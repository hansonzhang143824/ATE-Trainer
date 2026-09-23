#!/usr/bin/env python3
"""Native CSV graph PathProof validator for ATE Hardware Parse V2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("csv_schematic_adapter_v2", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def relay_number(name: str) -> int | None:
    match = re.match(r"K(\d+)_", name)
    return int(match.group(1)) if match else None


def pin_role(port: str) -> tuple[str, str]:
    match = re.match(r"^(.+?)_(?:FORCE|SENSE)_S\d+$", port)
    if match:
        return match.group(1), "F" if "_FORCE_" in port else "S"
    match = re.match(r"^(.+?)_([FS])_S\d+$", port)
    if match:
        return match.group(1), match.group(2)
    match = re.match(r"^(.+?)_S\d+$", port)
    return (match.group(1), "") if match else (port, "")


def source_meta(port: str) -> dict:
    source_type = "UNKNOWN"
    for token in ("ACM200", "FXVIe_PLUS", "FXVIe", "FPVIe", "QTMU", "QVM"):
        if token in port:
            source_type = token
            break
    if re.match(r"^S(?:24|9)_P\d+$", port):
        source_type = "DCM"
    if re.match(r"^S10_CH\d+_[AB]$", port):
        source_type = "QTMU"
    role = ""
    side = ""
    channel = ""
    match = re.search(r"_(FH|SH|FL|SL)(\d+)", port)
    if match:
        side, channel = match.group(1), match.group(2)
        role = "F" if side in {"FH", "FL"} else "S"
    else:
        match = re.search(r"CH(\d+)([+-])$", port)
        if match:
            channel, side = match.group(1), match.group(2)
            role = "F" if side == "+" else "S"
        else:
            match = re.search(r"_P(\d+)$", port)
            if match:
                channel, role = match.group(1), "F"
    domain = "HIGH" if side in {"FH", "SH", "+"} else "LOW" if side in {"FL", "SL", "-"} else ""
    family = source_type
    family_match = re.match(r"^(S\d+_.+?)_(?:FH|SH|FL|SL)\d+", port)
    if family_match:
        family = family_match.group(1)
    else:
        family_match = re.match(r"^(S\d+_.+?)_CH\d+[+-]$", port)
        if family_match:
            family = family_match.group(1)
    pair_domain = "" if source_type == "QVM" else domain
    return {
        "type": source_type,
        "role": role,
        "side": side,
        "channel": channel,
        "domain": domain,
        "pair_key": f"{family}:{channel}:{pair_domain}",
    }


class NativeGraph:
    def __init__(self, graph: dict):
        self.graph = graph
        self.nets = graph["nets"]
        self.ports = graph["ports"]
        self.port_nets = graph["port_nets"]
        self.relays = {
            name for name in graph["instances"] if relay_number(name) is not None
        }
        self.g6k = {name for name in self.relays if graph["instances"][name] == "G6K"}
        self.mos = self.relays - self.g6k
        self.ipn: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
        for net, conns in self.nets.items():
            for inst, pin in conns:
                self.ipn[inst][pin].append(net)
        self.dut_by_net: dict[str, list[str]] = defaultdict(list)
        for port, direction in self.ports.items():
            if direction == "OUTPUT":
                for net in self.port_nets.get(port, []):
                    self.dut_by_net[net].append(port)
        # Rule A: 固定电压节点 = 地(AGND/DGND/JGND/AGND_*)+固定电源轨(J+5V/J+12V)。作中间节点非法(源表与之对拉)。
        self.fixed_voltage_nets = {
            n for n in self.nets
            if n in ("AGND", "DGND", "JGND") or n.startswith("AGND_") or n.startswith("S34_JGND")
            or "J+5V" in n or "J_5V" in n or "J+12V" in n or "J_12V" in n
        }

    def transitions(self, inst: str, pin: int):
        if inst in self.g6k:
            nc = {2: (3,), 3: (2,), 7: (6,), 6: (7,)}
            on = {3: (4,), 4: (3,), 6: (5,), 5: (6,)}
            for target in nc.get(pin, ()): yield target, "NC"
            for target in on.get(pin, ()): yield target, "ON"
        else:
            if pin == 1: yield 2, "ON"
            elif pin == 2: yield 1, "ON"

    @staticmethod
    def bus_domain(net: str) -> str:
        if any(x in net for x in ("FH_BUS", "SH_BUS", "FH_PC", "SH_PC")):
            return "HIGH"
        if any(x in net for x in ("FL_BUS", "SL_BUS", "FL_PC", "SL_PC")):
            return "LOW"
        return ""

    @staticmethod
    def scarce(source: str) -> bool:
        return any(x in source for x in ("FPVIe", "QTMU", "QVM", "CH0"))

    def trace(self, source: str, max_depth: int = 6) -> list[dict]:
        starts = self.port_nets.get(source, [])
        meta = source_meta(source)
        queue = deque((net, [], frozenset(), "") for net in starts)
        visited = {(net, frozenset(), "") for net in starts}
        best: dict[str, tuple[tuple[int, int], dict]] = {}
        while queue:
            net, path, used_numbers, active_bus_domain = queue.popleft()
            terminals = self.dut_by_net.get(net, [])
            if terminals:
                for dut in terminals:
                    key = (len(used_numbers), sum(step["state"] == "ON" for step in path))
                    proof = {
                        "source_port": source,
                        "source_meta": meta,
                        "dut_pin": dut,
                        "dut_net": net,
                        "path": path,
                        "required_on": sorted({step["relay_number"] for step in path if step["state"] == "ON"}),
                        "terminal_stop": True,
                    }
                    if dut not in best or key < best[dut][0]:
                        best[dut] = (key, proof)
                # PATH_CONTRACT: DUT PIN is a terminal; never expand beyond it.
                continue
            if len(used_numbers) >= max_depth:
                continue
            for inst, pin in self.nets.get(net, []):
                if inst not in self.relays:
                    continue
                number = relay_number(inst)
                if number is None or number in used_numbers:
                    continue
                for target_pin, state in self.transitions(inst, pin):
                    for next_net in self.ipn[inst].get(target_pin, []):
                        if next_net == net:
                            continue
                        if next_net in self.fixed_voltage_nets and next_net not in self.dut_by_net:
                            continue  # Rule A: 固定电压节点作中间节点非法(终点地脚由 terminal-stop 覆盖)
                        if not self.scarce(source) and self.bus_domain(next_net):
                            continue
                        next_domain = self.bus_domain(next_net)
                        if next_domain and meta["domain"] and next_domain != meta["domain"]:
                            continue
                        next_active = active_bus_domain
                        if state == "ON" and next_domain:
                            if next_active and next_active != next_domain:
                                continue
                            next_active = next_domain
                        step = {
                            "relay": re.sub(r"_S\d+(?:S\d+)?$", "", inst),
                            "relay_instance": inst,
                            "relay_number": number,
                            "state": state,
                            "from_net": net,
                            "from_pin": pin,
                            "to_pin": target_pin,
                            "to_net": next_net,
                        }
                        next_used = used_numbers | {number}
                        visit_key = (next_net, next_used, next_active)
                        if visit_key not in visited:
                            visited.add(visit_key)
                            queue.append((next_net, path + [step], next_used, next_active))
        return [item[1] for item in best.values()]


def load_cbit(workspace: Path, path: Path) -> tuple[dict[int, list[dict]], list[str]]:
    # gen_cbit_defines.py 与 adapter/pathproof 同属一个 workspace:
    # 旧布局在 <ws> 根; 迁移后(2026-09)在 <ws>/scripts → 两个候选都加 sys.path。
    for cand in (workspace, workspace / "scripts"):
        if str(cand) not in sys.path:
            sys.path.insert(0, str(cand))
    import gen_cbit_defines
    entries = gen_cbit_defines.read_excel_cbit(str(path))
    by_number: dict[int, list[dict]] = defaultdict(list)
    for group, name, raw in entries:
        match = re.match(r"K(\d+)", name)
        if not match:
            continue
        by_number[int(match.group(1))].append({
            "name": name,
            "group": group,
            "raw": raw,
            "value": gen_cbit_defines.cbit_val(raw),
        })
    issues = [f"K{number}: CBIT value conflict" for number, rows in by_number.items()
              if len({row["value"] for row in rows}) > 1]
    return dict(by_number), issues


def validate_and_pair(proofs: list[dict], cbit_by_number: dict[int, list[dict]]) -> tuple[list[dict], list[dict], list[str], list[dict]]:
    accepted: list[dict] = []
    rejected: list[dict] = []
    hard_issues: list[str] = []
    for proof in proofs:
        dut_base, dut_role = pin_role(proof["dut_pin"])
        source_role = proof["source_meta"]["role"]
        proof["dut_base"] = dut_base
        proof["dut_role"] = dut_role
        proof["cbit"] = {
            str(number): cbit_by_number.get(number, []) for number in proof["required_on"]
        }
        missing = [number for number in proof["required_on"] if number not in cbit_by_number]
        proof["validation"] = {
            "terminal_stop": proof["terminal_stop"],
            "role_match": not dut_role or not source_role or dut_role == source_role,
            "cbit_complete": not missing,
            "missing_cbit": missing,
        }
        if not proof["validation"]["role_match"]:
            proof["reject_reason"] = "KELVIN_ROLE_CROSS"
            rejected.append(proof)
        elif missing:
            proof["reject_reason"] = "MISSING_CBIT"
            rejected.append(proof)
            hard_issues.append(f"{proof['source_port']}->{proof['dut_pin']}: missing CBIT {missing}")
        else:
            accepted.append(proof)

    grouped: dict[tuple[str, str], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for proof in accepted:
        if proof["source_meta"]["type"] not in {"FPVIe", "ACM200", "FXVIe_PLUS", "FXVIe", "QVM"}:
            continue
        role = proof["source_meta"]["role"]
        if role not in {"F", "S"}:
            continue
        grouped[(proof["source_meta"]["pair_key"], proof["dut_base"])][role].append(proof)
    pairs: list[dict] = []
    for (source_key, dut_base), roles in sorted(grouped.items()):
        force = roles.get("F", [])
        sense = roles.get("S", [])
        if not force or not sense:
            continue
        f = min(force, key=lambda p: (len(p["path"]), len(p["required_on"])))
        s = min(sense, key=lambda p: (len(p["path"]), len(p["required_on"])))
        f_state = {step["relay_number"]: step["state"] for step in f["path"]}
        s_state = {step["relay_number"]: step["state"] for step in s["path"]}
        conflicts = sorted(number for number in set(f_state) & set(s_state) if f_state[number] != s_state[number])
        pair = {
            "source_pair": source_key,
            "dut_base": dut_base,
            "force_proof": {"source": f["source_port"], "dut": f["dut_pin"], "required_on": f["required_on"]},
            "sense_proof": {"source": s["source_port"], "dut": s["dut_pin"], "required_on": s["required_on"]},
            "relay_state_conflicts": conflicts,
            "status": "PASS" if not conflicts else "FAIL",
        }
        pairs.append(pair)
        if conflicts:
            hard_issues.append(f"{source_key}->{dut_base}: F/S relay-state conflict {conflicts}")
    return accepted, rejected, hard_issues + [
        f"{p['source_pair']}->{p['dut_base']}: pair conflict" for p in pairs if p["status"] == "FAIL"
    ], pairs


def _workspace_root(start) -> Path:
    """上溯找 project_config.json 所在目录 = workspace 根 (config 权威位置)。"""
    d = Path(start)
    while not (d / "project_config.json").is_file():
        d = d.parent
    return d


def main() -> int:
    package = Path(__file__).resolve().parents[1]
    workspace = _workspace_root(package)
    adapter = load_adapter(package / "scripts" / "csv_schematic_adapter_v2.py")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=adapter.find_schematic_csv(workspace / "Project" / "DALI"))
    parser.add_argument("--cbit", type=Path, default=adapter.find_cbit_form(workspace / "Project" / "DALI"))
    parser.add_argument("--out-dir", type=Path, default=workspace / "Project" / "DALI")
    args = parser.parse_args()

    rows, warnings = adapter.load_csv(args.input)
    graph_data = adapter.build_graph(rows)
    graph = NativeGraph(graph_data)
    cbit_by_number, cbit_issues = load_cbit(workspace, args.cbit)
    sources = sorted(port for port, direction in graph.ports.items() if direction == "INOUT")
    proofs = [proof for source in sources for proof in graph.trace(source)]
    accepted, rejected, issues, pairs = validate_and_pair(proofs, cbit_by_number)
    issues = cbit_issues + issues

    payload = {
        "schema_version": 1,
        "engine": "native_csv_graph_v2",
        "input": {"path": str(args.input.resolve()), "sha256": sha256(args.input)},
        "cbit": {"path": str(args.cbit.resolve()), "sha256": sha256(args.cbit)},
        "contracts": {
            "dut_pin_is_terminal": True,
            "kelvin_force_sense_no_cross": True,
            "shared_relay_state_must_match": True,
            "cbit_traceability_required": True,
        },
        "counts": {
            "sources": len(sources),
            "raw_best_paths": len(proofs),
            "accepted_path_proofs": len(accepted),
            "rejected_paths": len(rejected),
            "kelvin_pairs": len(pairs),
            "kelvin_pair_failures": sum(pair["status"] == "FAIL" for pair in pairs),
        },
        "warnings": warnings,
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
        "accepted_path_proofs": accepted,
        "rejected_paths": rejected,
        "kelvin_pairs": pairs,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "path_proofs.json.txt"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = args.out_dir / "PATHPROOF-VALIDATION.txt"
    summary.write_text(
        "\n".join([
            "ATE Hardware Parse — Native PathProof Validation",
            f"status={payload['status']}",
            *(f"{key}={value}" for key, value in payload["counts"].items()),
            f"issues={len(issues)}",
            *(f"- {issue}" for issue in issues[:200]),
            "",
        ]), encoding="utf-8"
    )
    print(f"PathProof: {out}")
    print(f"Summary: {summary}")
    print(json.dumps({"status": payload["status"], **payload["counts"], "issues": len(issues)}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
