#!/usr/bin/env python3
"""CSV schematic validation entry.

This adapter reads Altium unified-circuit-connectivity CSV directly, validates
its schema, materializes an EDIF-compatible graph, and runs the existing proven
six-gate/path engine. It is the sole production pipeline: the synthetic EDIF is
passed as a positional NETLIST override into sch_parse.py driven by the
production project_config.json, so the canonical output names
(SCH-Connect-Map.txt / Component-Statistic.txt) are written unchanged.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_COLUMNS = (
    "SheetPath", "RecordType", "RecordKey", "NetName", "MemberType",
    "MemberName", "Designator", "ComponentUniqueID", "MemberUniqueID",
    "ComponentKind", "LibraryReference", "PartID", "PinNumber", "PinName",
    "Electrical", "Relation", "EndpointStatus", "ObservedNetCount",
    "ObservedNets", "EffectiveShortNetCount", "EffectiveShortNets",
    "DanglingEndpointCount", "DanglingNets", "Status", "RawID",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def q(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def infer_cell(designator: str, pins: set[int], pin_names: set[str]) -> str:
    """Infer only the categories needed by the legacy graph/check engine."""
    if re.match(r"^K\d+_", designator):
        if pins - {1, 2} or pin_names - {"COMMON", "NO"}:
            return "G6K"
        return "SW_SPST"
    prefix = re.match(r"^[A-Za-z]+", designator)
    prefix = prefix.group(0).upper() if prefix else "COMPONENT"
    return {
        "CAP": "Cap",
        "C": "Cap",
        "R": "Res2",
        "D": "D_Schottky",
        "TP": "TEST_POINT_SMALL",
    }.get(prefix, f"CSV_{prefix}")


def load_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    signature = path.read_bytes()[:16]
    if signature.startswith(b"%TSD-Header-###%") or signature.startswith(b"TSZ#"):
        raise ValueError(
            f"encrypted TSD/TSZ container is not a parseable CSV: {path}. "
            "Export or copy its unchanged plaintext CSV content to a .txt or plain .csv file."
        )
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        raw_rows = list(reader)
        if not raw_rows:
            raise ValueError("CSV contains no header")
        fields = tuple(raw_rows[0])
        missing = [name for name in REQUIRED_COLUMNS if name not in fields]
        extra = [name for name in fields if name not in REQUIRED_COLUMNS]
        if missing:
            raise ValueError(f"CSV schema missing columns: {missing}")
        rows: list[dict[str, str]] = []
        compact_count = 0
        for line_no, values in enumerate(raw_rows[1:], 2):
            if len(values) != len(fields):
                raise ValueError(
                    f"CSV line {line_no} has {len(values)} columns; expected {len(fields)}"
                )
            member_type = values[4].strip().upper()
            normalized = list(values)
            compact = False
            if member_type == "PIN" and not values[14].strip() and values[12].strip().upper() in {
                "PASSIVE", "INPUT", "OUTPUT", "I/O", "POWER"
            }:
                # Dali-SCH compact layout:
                # fixed[0:9], PartID, PinName, PinNumber, Electrical, RawID.
                compact = True
                normalized = [""] * len(fields)
                normalized[:9] = values[:9]
                normalized[11] = values[9]
                # Altium places PinNumber/PinName in either order depending on
                # whether the schematic pin designator is numeric or symbolic.
                if values[10].strip().isdigit():
                    normalized[12] = values[10]
                    normalized[13] = values[11]
                elif values[11].strip().isdigit():
                    normalized[12] = values[11]
                    normalized[13] = values[10]
                else:
                    raise ValueError(
                        f"compact PIN row has no numeric pin at line {line_no}: "
                        f"{values[6]} ({values[10]!r}, {values[11]!r})"
                    )
                normalized[14] = values[12]
                normalized[24] = values[13]
            elif member_type in {"PORT", "NET_LABEL", "POWER_PORT"} and not values[14].strip() and values[6].strip():
                # Compact non-pin layout:
                # fixed[0:6], Electrical, Status-or-RawID, RawID(optional).
                compact = True
                normalized = [""] * len(fields)
                normalized[:6] = values[:6]
                normalized[14] = values[6]
                if member_type == "PORT":
                    normalized[23] = values[7]
                    normalized[24] = values[8]
                else:
                    normalized[24] = values[7]
            if compact:
                compact_count += 1
            rows.append(dict(zip(fields, normalized)))
    if not rows:
        raise ValueError("CSV contains no data rows")
    warnings: list[str] = []
    if compact_count:
        warnings.append(
            f"normalized Dali-SCH compact field layout for {compact_count}/{len(rows)} rows"
        )
    if extra:
        warnings.append(f"extra columns retained but unused: {extra}")
    bad_type = sorted({
        r["RecordType"] for r in rows
        if r["RecordType"] not in {"NET_MEMBER", "NET_TIE_ENDPOINT", "NET_TIE_GROUP", "ELECTRICAL_SHORT_GROUP"}
    })
    if bad_type:
        raise ValueError(f"unsupported RecordType values: {bad_type}")
    return rows, warnings


def build_graph(rows: list[dict[str, str]]) -> dict:
    nets: dict[str, list[tuple[str, int]]] = defaultdict(list)
    ports: dict[str, str] = {}
    port_nets: dict[str, set[str]] = defaultdict(set)
    net_ports_ordered: dict[str, list[str]] = defaultdict(list)
    net_labels: dict[str, list[str]] = defaultdict(list)
    inst_pins: dict[str, set[int]] = defaultdict(set)
    inst_pin_names: dict[str, set[str]] = defaultdict(set)
    component_values: dict[str, str] = {}
    source_rows = 0
    dut_rows = 0
    ignored_ports: list[dict[str, str]] = []
    port_direction_conflicts: list[dict[str, str]] = []
    net_tie_groups: list[dict[str, object]] = []
    net_short_groups: list[dict[str, str]] = []
    semantic_port_aliases: list[dict[str, str]] = []
    electrical_role_corrections: list[dict[str, str]] = []

    for row in rows:
        record_type = row["RecordType"].strip().upper()
        if record_type == "NET_TIE_GROUP":
            short_nets = [n.strip() for n in row["EffectiveShortNets"].split("|") if n.strip()]
            expected = int(row["EffectiveShortNetCount"] or 0)
            if row["Status"].strip().upper() != "OK" or len(short_nets) != expected:
                raise ValueError(
                    f"invalid NET_TIE_GROUP {row.get('MemberName', '')}: "
                    f"status={row.get('Status', '')}, expected={expected}, actual={len(short_nets)}"
                )
            net_tie_groups.append({
                "name": row["MemberName"].strip(),
                "nets": short_nets,
                "dangling_endpoint_count": int(row["DanglingEndpointCount"] or 0),
            })
            continue
        if record_type == "NET_TIE_ENDPOINT":
            # Connectivity is applied from the validated group row below.
            continue
        if record_type == "ELECTRICAL_SHORT_GROUP":
            # Altium 编译电气节点: ShortNets 里所有 net 属于同一节点 (直接导线).
            # 记录短接事实(供 SCH-Connect-Map net短接 列), 不合并 net(保持各自 net 名,
            # 下游通路分析需知道"经过此节点即已短接"的事实).
            short_nets = [n.strip() for n in row["ShortNets"].split("|") if n.strip()]
            if not short_nets:
                short_nets = [n.strip() for n in row["EffectiveShortNets"].split("|") if n.strip()]
            net_short_groups.append({
                "kind": (row["ShortKind"].strip().upper() or "DIRECT_NET_ALIAS"),
                "object": (row["ShortObject"].strip().upper() or "DIRECT_WIRE"),
                "status": (row["ShortStatus"].strip().upper() or "CONFIRMED"),
                "canonical": row["NetName"].strip(),
                "nets": short_nets,
            })
            continue
        net = row["NetName"].strip()
        mtype = row["MemberType"].strip().upper()
        if not net:
            raise ValueError(f"row has empty NetName: {row.get('RecordKey', '')}")
        if mtype == "PIN":
            inst = row["Designator"].strip()
            pin_text = row["PinNumber"].strip()
            if not inst or not pin_text:
                raise ValueError(f"PIN row lacks designator/pin: {row.get('RecordKey', '')}")
            try:
                pin = int(pin_text)
            except ValueError as exc:
                # For IC symbols Altium may export the symbolic design pin in
                # PinNumber (GND/VOUT/RS+) and the physical package number in
                # PinName. The relay rows keep numeric PinNumber, so preferring
                # the numeric field is deterministic and preserves topology.
                display_pin = row["PinName"].strip()
                if display_pin.isdigit():
                    pin = int(display_pin)
                else:
                    raise ValueError(
                        f"PIN row has no numeric physical pin at {inst}: "
                        f"PinNumber={pin_text!r}, PinName={display_pin!r}"
                    ) from exc
            item = (inst, pin)
            if item not in nets[net]:
                nets[net].append(item)
            inst_pins[inst].add(pin)
            val = row.get("ComponentValue", "").strip()
            if val and inst not in component_values:
                component_values[inst] = val
            if row["PinName"].strip():
                inst_pin_names[inst].add(row["PinName"].strip().upper())
        elif mtype == "PORT":
            name = row["MemberName"].strip()
            electrical = row["Electrical"].strip().upper()
            if not name:
                # Altium emits two connected, unnamed ports on N00028. They
                # have no addressable semantic endpoint and no component pin;
                # legacy EDIF represents these as UNDEFINED and ignores them.
                ignored_ports.append(row)
                continue
            if name.startswith("S3_FOVIe_"):
                normalized = name.replace("S3_FOVIe_", "S3_FXVIe_PLUS_", 1)
                semantic_port_aliases.append({"csv": name, "normalized": normalized})
                name = normalized
            if electrical == "OUTPUT":
                direction = "OUTPUT"
                dut_rows += 1
            elif electrical == "I/O":
                # Some older Altium exports mark AGND_F/S DUT terminals as I/O.
                # A non-slot Kelvin-style terminal is a DUT endpoint, not an
                # instrument source. Slot sources always start with S<slot>_.
                if re.match(r"^.+_[FS]_S\d+$", name) and not re.match(r"^S\d+_", name):
                    direction = "OUTPUT"
                    dut_rows += 1
                    electrical_role_corrections.append({
                        "port": name, "csv": "I/O", "normalized": "OUTPUT"
                    })
                else:
                    direction = "INOUT"
                    source_rows += 1
            else:
                ignored_ports.append(row)
                continue
            old = ports.get(name)
            if old and old != direction:
                # Altium can export two overlapping sheet-port records with the
                # same identity but different electrical styles. OUTPUT is the
                # conservative DUT-terminal role: a source must never be
                # invented merely because one duplicate record says I/O.
                resolved = "OUTPUT" if "OUTPUT" in (old, direction) else old
                port_direction_conflicts.append({
                    "port": name,
                    "first": old,
                    "second": direction,
                    "resolved": resolved,
                    "net": net,
                })
                ports[name] = resolved
            else:
                ports[name] = direction
            port_nets[name].add(net)
            if name not in net_ports_ordered[net]:
                net_ports_ordered[net].append(name)
        elif mtype in {"NET_LABEL", "POWER_PORT"}:
            label = row["MemberName"].strip()
            if label and label not in net_labels[net]:
                net_labels[net].append(label)

    # A net-tie is an intentional zero-ohm relation. Preserve every original
    # net name, but give each member the union of all component connections.
    # This makes every alias electrically equivalent without inventing a relay.
    for group in net_tie_groups:
        names = group["nets"]
        merged: list[tuple[str, int]] = []
        for name in names:
            for item in nets.get(name, []):
                if item not in merged:
                    merged.append(item)
        for name in names:
            nets[name] = list(merged)
        # Net Tie 同样记录为 net 短接事实 (有意零欧短接, 供 net短接 列)
        net_short_groups.append({
            "kind": "NET_TIE",
            "object": "NET_TIE",
            "status": "CONFIRMED",
            "canonical": names[0] if names else group.get("name", ""),
            "nets": list(names),
        })

    # The CSV exporter retains a named net for a single dangling relay pin;
    # EDIF omits that net. G3 already checks the physical floating-pin rule and
    # permits one floating contact in a G6K part. Remove only this redundant
    # representation so G5 does not count the same condition as a hard failure.
    singleton_relay_nets: list[dict[str, object]] = []
    intentional_open_nets: list[dict[str, object]] = []
    nets_with_ports = {net for names in port_nets.values() for net in names}
    for name, conns in list(nets.items()):
        if name in nets_with_ports or len(conns) != 1:
            continue
        inst, pin = conns[0]
        if re.match(r"^K\d+_", inst):
            singleton_relay_nets.append({"net": name, "relay": inst, "pin": pin})
            del nets[name]
        elif inst.startswith("TP_") or re.search(r"(^|_)NC($|_)", name, re.IGNORECASE):
            intentional_open_nets.append({"net": name, "component": inst, "pin": pin})
            del nets[name]

    # --- PIN 短接自动登记 (PORT-only DUT 端口与另一 DUT 端口共 net → 合成 TP_<PORT> 测试点) ---
    # 真实 Altium EDIF 用 TP_<PORT> 测试点标记「端口接线点」; CSV 导出可能遗漏该点。按「共 net」关系
    # 合成, 使 PORT-only 短接端口成为 net 成员 (sch_parse 经 Step B1 TP_<PORT> 映射), 而非孤立 PORT。
    # 覆盖 VDRV↔V1P5 / PWM1↔PB0 这类「端口共 net 短路」; 已存在同名 TP 时不重复合成。
    synthesized_tps: list[dict[str, str]] = []
    dut_port_names = {name for name, direction in ports.items() if direction == "OUTPUT"}
    for p in sorted(dut_port_names):
        if p in inst_pins:
            continue  # 有物理 PIN 的端口无需合成
        for net in port_nets.get(p, ()):
            # 与另一个 DUT 端口共 net = 短路 (同一电气节点), 无论对方有无物理 PIN
            other_ports = [q for q in net_ports_ordered.get(net, []) if q in dut_port_names and q != p]
            if other_ports:
                tp = "TP_" + p
                if tp not in inst_pins:
                    inst_pins[tp] = {1}
                    inst_pin_names[tp].add("1")
                    if (tp, 1) not in nets[net]:
                        nets[net].append((tp, 1))
                    synthesized_tps.append({"port": p, "testpoint": tp, "net": net})

    if not ports:
        raise ValueError("no OUTPUT/I/O sheet ports found")
    if not nets:
        raise ValueError("no component PIN connectivity found")

    instances = {
        inst: infer_cell(inst, pins, inst_pin_names[inst])
        for inst, pins in inst_pins.items()
    }
    relay_count = sum(1 for name in instances if re.match(r"^K\d+_", name))
    return {
        "nets": dict(nets),
        "ports": ports,
        "port_nets": {k: sorted(v) for k, v in port_nets.items()},
        "net_ports": {net: list(net_ports_ordered.get(net, [])) for net in nets},
        "net_labels": {net: list(net_labels.get(net, [])) for net in nets},
        "instances": instances,
        "component_values": component_values,
        "inst_pins": {k: sorted(v) for k, v in inst_pins.items()},
        "relay_count": relay_count,
        "source_port_rows": source_rows,
        "dut_port_rows": dut_rows,
        "ignored_ports": ignored_ports,
        "port_direction_conflicts": port_direction_conflicts,
        "net_tie_groups": net_tie_groups,
        "net_short_groups": net_short_groups,
        "semantic_port_aliases": semantic_port_aliases,
        "electrical_role_corrections": electrical_role_corrections,
        "singleton_relay_nets": singleton_relay_nets,
        "intentional_open_nets": intentional_open_nets,
        "synthesized_tps": synthesized_tps,
    }


def safe_symbol(value: str, prefix: str, index: int) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return value
    return f"{prefix}_{index}"


def write_synthetic_edif(graph: dict, out_path: Path) -> dict:
    """Write a deterministic EDIF view without mutating the source graph.

    Every physical CSV net is emitted exactly once. If it has named sheet ports,
    one semantic port name becomes the canonical net name. OUTPUT (DUT) names
    take precedence over I/O source names; an existing raw-name match takes
    precedence over both. This mirrors Altium EDIF's single-name physical net.
    """
    lines = ["(edif CSV_V2", "  (library CSV_V2_LIB", "    (cell Sheet1_SchDoc", "      (interface"]
    for index, (name, direction) in enumerate(sorted(graph["ports"].items()), 1):
        sym = safe_symbol(name, "PORT", index)
        if sym == name:
            lines.append(f"        (port {name} (direction {direction}))")
        else:
            lines.append(f"        (port (rename {sym} {q(name)}) (direction {direction}))")
    lines.extend(["      )", "    )"])

    component_values = graph.get("component_values", {})
    for inst, cell in sorted(graph["instances"].items()):
        val = component_values.get(inst, "")
        if val:
            lines.append(
                f"    (Instance {inst} (viewRef NetlistView (cellRef {cell}))"
                f" (Property Value (String {q(val)})))"
            )
        else:
            lines.append(f"    (Instance {inst} (viewRef NetlistView (cellRef {cell})))")

    canonical_names: dict[str, str] = {}
    canonical_collisions: list[dict[str, str]] = []
    used_names: set[str] = set()
    renamed_count = 0
    net_index = 0
    for net, conns in sorted(graph["nets"].items()):
        net_index += 1
        candidates = graph["net_ports"].get(net, [])
        labels = graph["net_labels"].get(net, [])
        if labels:
            canonical = net if net in labels else labels[0]
        elif candidates:
            canonical = candidates[0]
        else:
            canonical = net
        if canonical in used_names and canonical != net:
            canonical_collisions.append({
                "physical_net": net,
                "requested_name": canonical,
                "resolved_name": net,
            })
            canonical = net
        used_names.add(canonical)
        canonical_names[net] = canonical
        if canonical != net:
            renamed_count += 1
        n_sym = safe_symbol(canonical, "NET", net_index)
        if n_sym == canonical:
            lines.append(f"    (Net {canonical}")
        else:
            lines.append(f"    (Net (rename {n_sym} {q(canonical)})")
        for inst, pin in conns:
            lines.append(f"      (PortRef &{pin} (InstanceRef {inst}))")
        lines.append("    )")

    # CSV net 短接事实 (ELECTRICAL_SHORT_GROUP / NET_TIE_GROUP) → 合成 EDIF comment,
    # 供 sch_parse.py 列11 输出 "net短接" 分类. 只记录事实, 不合并 net.
    for sg in graph.get("net_short_groups", []):
        nets_str = "|".join(sg["nets"])
        lines.append(
            f'  (comment "CSV_NET_SHORT:{sg["kind"]}:{sg["object"]}:{sg["status"]}:{sg["canonical"]}:{nets_str}")'
        )

    lines.extend(["  )", ")", ""])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "physical_nets": len(graph["nets"]),
        "renamed_nets": renamed_count,
        "terminals": 0,
        "canonical_net_names": canonical_names,
        "canonical_name_collisions": canonical_collisions,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _find_by_name(directory, word, extensions, label):
    """按「文件名含 word + 扩展名在 extensions」在 directory 下(不递归)找唯一文件。

    0 或 >1 个匹配都抛 FileNotFoundError(带清楚提示), 拒绝静默歧义。
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"目录不存在: {directory}")
    matches = sorted(
        p for p in directory.iterdir()
        if p.is_file()
        and word.upper() in p.name.upper()
        and p.suffix.lower() in extensions
    )
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(
            f"未找到{label}(文件名含 '{word}' 且扩展名 {extensions}): {directory}"
        )
    raise FileNotFoundError(
        f"发现多个{label}(文件名含 '{word}' 且扩展名 {extensions}): {[p.name for p in matches]}"
    )


def find_schematic_csv(directory):
    """按文件名发现原理图 CSV: 文件名含 'SCH' 且扩展名 .csv。"""
    return _find_by_name(directory, "SCH", (".csv",), "原理图 CSV")


def find_cbit_form(directory):
    """按文件名发现 CBIT 表单: 文件名含 'CBIT' 且扩展名 .csv/.xlsx/.xls。"""
    return _find_by_name(directory, "CBIT", (".csv", ".xlsx", ".xls"), "CBIT 表单")


def _workspace_root(start: Path) -> Path:
    """上溯找 project_config.json 所在目录 = workspace 根 (config 权威位置)。"""
    d = start
    while not (d / "project_config.json").is_file():
        d = d.parent
    return d


def main() -> int:
    package_dir = Path(__file__).resolve().parents[1]
    workspace = _workspace_root(package_dir)
    default_input = find_schematic_csv(workspace / "Project" / "DALI")
    parser = argparse.ArgumentParser(description="CSV schematic validation entry")
    parser.add_argument("--input", type=Path, default=default_input)
    parser.add_argument("--workspace", type=Path, default=workspace)
    parser.add_argument("--project-config", type=Path, default=workspace / "project_config.json")
    parser.add_argument("--out-dir", type=Path, default=workspace / "Project" / "DALI")
    args = parser.parse_args()

    input_path = args.input.resolve()
    workspace = args.workspace.resolve()
    out_dir = args.out_dir.resolve()
    project_config = args.project_config.resolve()
    legacy_parser = package_dir / "scripts" / "sch_parse.py"
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if not legacy_parser.is_file():
        raise FileNotFoundError(legacy_parser)

    rows, warnings = load_csv(input_path)
    graph = build_graph(rows)
    # Keep the synthetic input beside the project's sch_confirmed.json so the
    # same reviewed per-project exceptions apply. The production config's
    # intermediates already name the canonical output files.
    synthetic_path = workspace / "Project" / "DALI" / "CSV_CONNECTIVITY.NET"
    edif_stats = write_synthetic_edif(graph, synthetic_path)

    base_config = json.loads(project_config.read_text(encoding="utf-8-sig"))
    config_dir = project_config.parent
    outputs = {
        key: (config_dir / Path(base_config["intermediates"][key + "_text"])).resolve()
        for key in ("component_statistic", "sch_connect_map")
    }

    manifest = {
        "schema_version": 1,
        "input": {
            "path": str(input_path),
            "sha256": sha256(input_path),
            "format": "Altium unified circuit connectivity CSV v3",
            "rows": len(rows),
            "sheet_paths": sorted({r["SheetPath"] for r in rows}),
        },
        "graph": {
            "ports": len(graph["ports"]),
            "dut_ports": sum(1 for d in graph["ports"].values() if d == "OUTPUT"),
            "source_ports": sum(1 for d in graph["ports"].values() if d == "INOUT"),
            "instances": len(graph["instances"]),
            "component_values": len(graph["component_values"]),
            "relays": graph["relay_count"],
            "net_tie_groups": len(graph["net_tie_groups"]),
            "net_short_groups": len(graph["net_short_groups"]),
            "normalized_singleton_relay_nets": len(graph["singleton_relay_nets"]),
            "normalized_intentional_open_nets": len(graph["intentional_open_nets"]),
            **edif_stats,
        },
        "warnings": warnings,
        "artifacts": {
            "synthetic_edif": str(synthetic_path),
            "component_statistic": str(outputs["component_statistic"]),
            "sch_connect_map": str(outputs["sch_connect_map"]),
        },
    }
    if graph["port_direction_conflicts"]:
        manifest["warnings"].append(
            "duplicate PORT direction conflicts resolved conservatively as OUTPUT: "
            + ", ".join(item["port"] for item in graph["port_direction_conflicts"])
        )
        manifest["port_direction_conflicts"] = graph["port_direction_conflicts"]
    if graph["ignored_ports"]:
        manifest["warnings"].append(
            f"ignored {len(graph['ignored_ports'])} unnamed/unsupported PORT rows with no addressable endpoint"
        )
        manifest["ignored_ports"] = [
            {
                "record_key": row.get("RecordKey", ""),
                "net": row.get("NetName", ""),
                "electrical": row.get("Electrical", ""),
            }
            for row in graph["ignored_ports"]
        ]
    if graph["net_tie_groups"]:
        manifest["net_tie_groups"] = graph["net_tie_groups"]
    if graph["net_short_groups"]:
        manifest["net_short_groups"] = graph["net_short_groups"]
    if graph["semantic_port_aliases"]:
        manifest["semantic_port_aliases"] = graph["semantic_port_aliases"]
    if graph["electrical_role_corrections"]:
        manifest["electrical_role_corrections"] = graph["electrical_role_corrections"]
    if graph["singleton_relay_nets"]:
        manifest["singleton_relay_nets"] = graph["singleton_relay_nets"]
    if graph["intentional_open_nets"]:
        manifest["warnings"].append(
            f"normalized {len(graph['intentional_open_nets'])} explicit TP/NC open nets as design intent"
        )
        manifest["intentional_open_nets"] = graph["intentional_open_nets"]
    if graph["synthesized_tps"]:
        manifest["synthesized_tps"] = graph["synthesized_tps"]
        manifest["graph"]["synthesized_tps"] = len(graph["synthesized_tps"])
    manifest_path = out_dir / "validation_manifest.json.txt"
    write_json(manifest_path, manifest)

    cmd = [
        sys.executable,
        str(legacy_parser),
        "--config",
        str(project_config),
        str(synthetic_path),
    ]
    completed = subprocess.run(
        cmd, cwd=workspace, text=True, encoding="utf-8", errors="replace",
        capture_output=True,
    )
    run_log = out_dir / "strict_gate_run.log"
    run_log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    manifest["artifacts"]["strict_gate_log"] = str(run_log)
    manifest["gate_exit_code"] = completed.returncode
    manifest["parser_gate_status"] = "PASS" if completed.returncode == 0 else "FAIL"
    for key, artifact in outputs.items():
        if artifact.is_file():
            manifest["artifacts"][key + "_sha256"] = sha256(artifact)
    if manifest["parser_gate_status"] == "PASS":
        manifest["status"] = "PASS"
        final_exit = 0
    else:
        manifest["status"] = "PARSER_FAIL"
        final_exit = completed.returncode or 1
    write_json(manifest_path, manifest)
    print(f"manifest: {manifest_path}")
    print(f"parser gate: {manifest['parser_gate_status']} (exit={completed.returncode})")
    print(f"overall status: {manifest['status']} (exit={final_exit})")
    return final_exit


if __name__ == "__main__":
    raise SystemExit(main())
