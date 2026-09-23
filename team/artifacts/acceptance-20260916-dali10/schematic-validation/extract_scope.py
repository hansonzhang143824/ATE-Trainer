#!/usr/bin/env python3
"""Extract scope-relevant schematic evidence for the DALI 10-TM acceptance run.

Reads the freshly regenerated PathProof output (native_csv_graph_v2) and the
synthetic-EDIF connect map, and writes two compact evidence files next to it:
  scope-paths.json        accepted paths / kelvin pairs for the ten TM scopes
  resource-conflicts.json relay reuse across scope pins + shared-resource flags
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent

# DUT pins / rails named by the ten in-scope TMs (foundation, toggle-trim,
# power-special groups of team/acceptance/acceptance-plan.json).
SCOPE = {
    "TM000": ["VBAT", "VCC", "AGND", "VAC1", "VAC2"],
    "TM001": ["VBAT", "VCC", "AGND", "VAC1"],
    "TM102": ["VAC1", "AGND", "AMUX", "VCC"],
    "TM103": ["VAC1", "VAC2", "AGND", "VCC"],
    "TM108": ["VAC1", "KLV1", "KLV2"],
    "TM109": ["VAC2", "KLV1", "KLV2"],
    "TM135": ["VDM", "SDA", "SCL", "VCC"],
    "TM600": ["PMID", "SW", "BST", "VBAT", "VDRV", "V1P5", "AMUX", "AGND", "PGND"],
    "TM601": ["SW", "PGND", "PMID", "VBUS", "VBAT", "VDRV", "V1P5", "AGND"],
    "TM1205": ["BST", "SW", "VBUS", "PMID"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    proofs_path = HERE / "path_proofs.json.txt"
    data = json.loads(proofs_path.read_text(encoding="utf-8"))
    acc = data["accepted_path_proofs"]
    kelvin = data["kelvin_pairs"]
    rej = data["rejected_paths"]

    wanted = sorted({p for pins in SCOPE.values() for p in pins})

    by_pin: dict[str, list] = collections.defaultdict(list)
    for p in acc:
        if p["dut_base"] in wanted:
            by_pin[p["dut_base"]].append(p)

    scope_paths = {
        "generatedFrom": {
            "path_proofs": {"path": "team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt",
                            "sha256": sha256(proofs_path)},
            "engine": data["engine"],
            "status": data["status"],
            "counts": data["counts"],
            "input_csv": data["input"],
            "cbit": data["cbit"],
        },
        "scope": SCOPE,
        "pinPathCounts": {k: len(v) for k, v in sorted(by_pin.items())},
        "paths": {
            k: [
                {
                    "source_port": p["source_port"],
                    "source_type": p["source_meta"]["type"],
                    "source_role": p["source_meta"]["role"],
                    "source_domain": p["source_meta"]["domain"],
                    "dut_pin": p["dut_pin"],
                    "dut_net": p["dut_net"],
                    "required_on": p["required_on"],
                    "relays": [r["relay_instance"] for r in p["path"]],
                    "states": [f'{r["relay_number"]}:{r["state"]}' for r in p["path"]],
                    "terminal_stop": p["terminal_stop"],
                    "validation": p["validation"],
                }
                for p in sorted(by_pin[k], key=lambda x: x["source_port"])
            ]
            for k in sorted(by_pin)
        },
        "kelvinPairs": [
            k for k in kelvin
            if k["dut_base"] in wanted
        ],
        "rejectedForScopePins": [
            {"source_port": r["source_port"], "dut_pin": r["dut_pin"],
             "required_on": r["required_on"], "reject_reason": r.get("reject_reason")}
            for r in rej if r["dut_base"] in wanted
        ],
    }
    (HERE / "scope-paths.json").write_text(
        json.dumps(scope_paths, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- resource conflict analysis -------------------------------------
    relay_users: dict[int, set] = collections.defaultdict(set)
    relay_names: dict[int, set] = collections.defaultdict(set)
    for pin in wanted:
        for p in by_pin.get(pin, []):
            for r in p["path"]:
                relay_users[r["relay_number"]].add(pin)
                relay_names[r["relay_number"]].add(r["relay"])
    shared = {n: sorted(v) for n, v in relay_users.items() if len(v) > 1}

    scope_relays: dict[str, set] = {}
    for tm, pins in SCOPE.items():
        s = set()
        for pin in pins:
            for p in by_pin.get(pin, []):
                s |= set(p["required_on"])
        scope_relays[tm] = s
    overlap = []
    tms = sorted(scope_relays)
    for i, a in enumerate(tms):
        for b in tms[i + 1:]:
            common = sorted(scope_relays[a] & scope_relays[b])
            if common:
                overlap.append({"a": a, "b": b, "sharedRelays": common})

    # ---- relay_role / stabiliser entries from the connect map -----------
    map_path = Path("project/DALI/SCH-Connect-Map.txt")
    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    stab = [l.strip() for l in map_text.splitlines()
            if "稳压" in l and re.search(r"\b(PMID|SW|SW1|SW2|VBUS|VBAT|V1P5_VDRV|VCC)\b", l)]
    p2p = [l.strip() for l in map_text.splitlines() if "↔" in l and "需闭合" in l]
    net_short = [l.strip() for l in map_text.splitlines() if "DIRECT_NET_ALIAS" in l]

    # ---- isolation: did the regenerated map match the committed one? ----
    committed = Path("project/DALI/SCH-Connect-Map.txt")
    regen_same = None
    if committed.is_file():
        regen_same = sha256(committed) == sha256(map_path)

    conflicts = {
        "relaySharedAcrossScopePins": {str(k): v for k, v in sorted(shared.items())},
        "scopeRelaySets": {k: sorted(v) for k, v in scope_relays.items()},
        "scopePairOverlaps": overlap,
        "stabiliserRelaysOnScopeRails": stab,
        "pinToPinShortPaths": p2p,
        "netShortGroups": net_short,
        "regeneratedMapMatchesCommitted": regen_same,
    }
    (HERE / "resource-conflicts.json").write_text(
        json.dumps(conflicts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "scopePinsWithPaths": sorted(by_pin),
        "scopePinsWithoutAnyPath": [p for p in wanted if p not in by_pin],
        "relaysSharedAcrossScopePins": len(shared),
        "regeneratedMapMatchesCommitted": regen_same,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
