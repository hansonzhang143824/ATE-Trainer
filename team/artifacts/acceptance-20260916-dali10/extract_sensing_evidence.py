#!/usr/bin/env python3
"""Extract the instrument-assignment / sensing evidence for PMID, SW and PGND.

Answers, from netlist evidence only:
  * which instrument (or which relay route) can reach each node;
  * whether that route is a four-wire Kelvin pair, a PC-shorted pair or a single line;
  * whether a usable Kelvin sense pair exists on PMID<->SW (TM600) and SW<->PGND (TM601).

Writes team/artifacts/acceptance-20260916-dali10/schematic-validation/sensing-evidence.json
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "team/artifacts/acceptance-20260916-dali10"
VAL = OUT / "schematic-validation"
MAP = ROOT / "project/DALI/SCH-Connect-Map.txt"
PROOFS = VAL / "path_proofs.json.txt"
COMPSTAT = ROOT / "project/DALI/Component-Statistic.txt"
SPECS = ROOT / "knowledge/sources/hardware-specs.md"
PINCH = Path("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h")

NODES = ("PMID", "SW", "PGND")
SHORT_GROUP_MEMBERS = {"FPVIe0_SH_PC_S1", "FPVIe0_SL_PC_S1"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- connect map
map_lines = MAP.read_text(encoding="utf-8", errors="replace").splitlines()

routes = defaultdict(list)  # node -> list of connect-map route records
section = ""
for i, line in enumerate(map_lines, 1):
    if line.startswith("## "):
        section = line[3:].strip()
        continue
    m = re.match(r"\s*(?:\S+\s*->\s*)?(PMID|SW|PGND)\s*(?:←.*?)?\s*\[(Kelvin|PC短接|单线[^\]]*)\]\s*(?:⚠[^需]*)?需闭合:\s*(.+?)\s*$", line)
    if m:
        routes[m.group(1)].append({
            "section": section, "line": i, "annotation": m.group(2),
            "requiredOn": m.group(3),
            "raw": line.strip(),
        })
        continue
    m2 = re.match(r"\s*(PMID|SW|PGND)\s*←\s*(.+?)\s*\[通路\]\s*需闭合:\s*(.+?)\s*$", line)
    if m2:
        routes[m2.group(1)].append({
            "section": section, "line": i, "annotation": "通路 (single line, no F/S split stated)",
            "requiredOn": m2.group(3), "raw": line.strip(),
        })

# chains that immediately follow each route header (indented continuation lines)
chains = defaultdict(list)
current = None
for i, line in enumerate(map_lines, 1):
    if re.match(r"\s*(?:\S+\s*->\s*)?(PMID|SW|PGND)\s*(?:←.*?)?\s*\[", line) or \
       re.match(r"\s*(PMID|SW|PGND)\s*←.*\[通路\]", line):
        current = None
        for n in NODES:
            if re.search(rf"\b{n}\b", line):
                current = n
                current_raw = line.strip()
                break
        continue
    if current and re.match(r"\s+\S.*->", line):
        chains[current].append({"line": i, "raw": line.strip()})

# ---------------------------------------------------------------- source-name map
chan_semantics = {}
for line in COMPSTAT.read_text(encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"\s+(S\d+_\d+)\s+->\s+(\S+)\s+\((\w+)\)", line)
    if m:
        chan_semantics[m.group(1)] = {"name": m.group(2), "type": m.group(3)}

# ---------------------------------------------------------------- path proofs
proofs = json.loads(PROOFS.read_text(encoding="utf-8"))
by_node = defaultdict(list)
for p in proofs["accepted_path_proofs"]:
    if p["dut_base"] in NODES:
        by_node[p["dut_base"]].append(p)

# ---------------------------------------------------------------- instrument capability
spec_text = SPECS.read_text(encoding="utf-8", errors="replace")
cap = {}
for mod in ("FOVIe", "FXVIe", "FXVIe_PLUS", "ACM", "ACM200", "FPVIe", "QVMe", "QTMUe"):
    m = re.search(rf"^\|\s*\*\*{re.escape(mod)}\*\*\s*\|(.*)$", spec_text, re.M)
    if m:
        cap[mod] = [c.strip() for c in m.group(1).split("|")]

# ---------------------------------------------------------------- verdicts
def classify(node: str) -> dict:
    rows = []
    for p in sorted(by_node[node], key=lambda x: (x["source_meta"]["type"], x["source_port"])):
        meta = p["source_meta"]
        role = p["dut_role"]
        chain = [{"relay": r["relay"], "state": r["state"]} for r in p["path"]]
        pc = any("_PC_" in r["relay"] or r["relay"].startswith(("K90", "K91")) for r in p["path"])
        rows.append({
            "sourcePort": p["source_port"], "instrument": meta["type"], "role": role,
            "dutPin": p["dut_pin"], "net": p["dut_net"], "requiredOn": p["required_on"],
            "chain": chain,
            "kelvin": bool(role in ("F", "S")),
            "touchesPcNets": pc,
            "confidence": "direct",
        })
    return {"node": node, "acceptedRoutes": rows,
            "instruments": sorted({r["instrument"] for r in rows}),
            "hasForceAndSenseOnSameInstrument": sorted(
                t for t in {r["instrument"] for r in rows}
                if {r["role"] for r in rows if r["instrument"] == t} >= {"F", "S"}),
            }

verdicts = {n: classify(n) for n in NODES}

# ---------------------------------------------------------------- pair analysis
def pair(a: str, b: str) -> dict:
    ra, rb = by_node[a], by_node[b]
    out = {"pair": f"{a}<->{b}", "singleInstrumentKelvinPairs": []}
    for inst in sorted({p["source_meta"]["type"] for p in ra} & {p["source_meta"]["type"] for p in rb}):
        for a_p in ra:
            if a_p["source_meta"]["type"] != inst or a_p["dut_role"] != "F":
                continue
            for b_p in rb:
                if b_p["source_meta"]["type"] != inst or b_p["dut_role"] != "F":
                    continue
                key_a = a_p["source_meta"]["pair_key"]
                key_b = b_p["source_meta"]["pair_key"]
                if key_a != key_b:
                    continue
                rel = sorted(set(a_p["required_on"]) | set(b_p["required_on"]))
                pc = any("_PC_" in r["relay"] for r in a_p["path"] + b_p["path"])
                out["singleInstrumentKelvinPairs"].append({
                    "instrument": inst,
                    "highTerminal": {"pin": a, "port": a_p["source_port"], "requiredOn": a_p["required_on"]},
                    "lowTerminal": {"pin": b, "port": b_p["source_port"], "requiredOn": b_p["required_on"]},
                    "unionRelays": rel,
                    "sharedRelays": sorted(set(a_p["required_on"]) & set(b_p["required_on"])),
                    "fourWireKelvinPreserved": not pc,
                    "touchesPcNets": pc,
                    "note": "high/low terminals of one instrument channel pair_key=%s" % key_a,
                })
    out["pairCount"] = len(out["singleInstrumentKelvinPairs"])
    return out


pairs = {
    "PMID_SW": pair("PMID", "SW"),
    "SW_PGND": pair("SW", "PGND"),
    "PGND_PMID": pair("PGND", "PMID"),
}

result = {
    "generatedFor": "TM600/TM601 differential Kelvin sense instrument assignment (t3/t4 input)",
    "runId": "acceptance-20260916-dali10",
    "sources": [
        {"path": "project/DALI/SCH-Connect-Map.txt", "locator": "columns 2-10 route headers + 需闭合 groups", "sha256": sha(MAP)},
        {"path": "team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt", "locator": "accepted_path_proofs for dut_base in PMID/SW/PGND", "sha256": sha(PROOFS)},
        {"path": "project/DALI/Component-Statistic.txt", "locator": "任务二b 源表名映射", "sha256": sha(COMPSTAT)},
        {"path": "knowledge/sources/hardware-specs.md", "locator": "module table lines 9-32", "sha256": sha(SPECS)},
        {"path": "D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h", "locator": "_PIN_CHANNEL_DEFINE_* macros", "sha256": sha(PINCH)},
    ],
    "connectMapRouteHeaders": {n: routes[n] for n in NODES},
    "connectMapChains": {n: chains[n] for n in NODES},
    "channelSemantics": {k: v for k, v in chan_semantics.items() if k.split("_")[0] in ("S3", "S5", "S8", "S10")},
    "instrumentCapabilityRows": cap,
    "nodeVerdicts": verdicts,
    "pairAnalysis": pairs,
    "netShortGroups": [l.strip() for l in map_lines if "DIRECT_NET_ALIAS" in l],
}
(VAL / "sensing-evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("wrote", VAL / "sensing-evidence.json")
for n in NODES:
    v = verdicts[n]
    print(f"\n== {n}: instruments={v['instruments']}")
    print("   F+S on same instrument:", v["hasForceAndSenseOnSameInstrument"])
    for r in v["acceptedRoutes"]:
        print(f"   {r['sourcePort']:22s} {r['instrument']:11s} role={r['role'] or '-':2s} req={r['requiredOn']} pc={r['touchesPcNets']}")
for k, v in pairs.items():
    print(f"\n== pair {k}: {v['pairCount']} single-instrument Kelvin pair(s)")
    for e in v["singleInstrumentKelvinPairs"]:
        print("   ", e["instrument"], e["highTerminal"]["port"], "->", e["lowTerminal"]["port"],
              "shared", e["sharedRelays"], "4wire", e["fourWireKelvinPreserved"], "pc", e["touchesPcNets"])
