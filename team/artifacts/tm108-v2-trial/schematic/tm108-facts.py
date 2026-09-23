#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the TM108 fact tables for the audit report (t3).

Outputs tm108-facts.json / tm108-facts.txt with, per TM108-relevant DUT pin:
  - the SCH-Connect-Map.txt per-pin section lines (candidates + relay chain + tokens)
  - the "S<n>_<inst> -> <DEVICE>" channel map rows from Component-Statistic.txt
  - the schematic-ir.json pin record (sources / requiredRelays / relayChainUnion /
    path evidence) and the IR's per-source-end path records if present
  - relay default state (IR) + all map tokens for each relay number
Read-only on project/DALI.
"""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).parent
PROJ = pathlib.Path("project/DALI")


def read_lines(p):
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read().splitlines()


cm = read_lines(PROJ / "SCH-Connect-Map.txt")
cs = read_lines(PROJ / "Component-Statistic.txt")
ir = json.loads((PROJ / "schematic-ir.json").read_text(encoding="utf-8"))

# ---------- map: pin sections in 列7/8/9/10 style ("  <PIN>  [Kelvin]  需闭合: ...") ----------
map_sections = {}
sec_header_re = re.compile(r"^\s{2}([A-Za-z0-9_+()（）\u4e00-\u9fff]+)\s+(\[[^\]]*\])\s*需闭合:\s*(.*)$")
cur = None
for i, l in enumerate(cm, 1):
    m = sec_header_re.match(l)
    if m and not l.startswith("    "):
        cur = m.group(1)
        map_sections.setdefault(cur, {"header_lines": [], "rows": []})
        map_sections[cur]["header_lines"].append({"line": i, "text": l, "pairing": m.group(2), "needClose": m.group(3)})
        continue
    # rows belong to current pin when they look like "  F: ... -> nQON_F" or "    A -> ... -> nQON"
    mrow = re.match(r"^\s+(F|S):\s*(.+)$", l)
    if mrow and cur:
        map_sections[cur]["rows"].append({"line": i, "role": mrow.group(1), "text": mrow.group(2).strip()})
        continue
    mrow2 = re.match(r"^\s+(\S+)\s*->\s*.*->\s*([A-Za-z0-9_+]+)\s*$", l)
    if mrow2 and cur and "->" in l:
        map_sections[cur]["rows"].append({"line": i, "role": None, "text": l.strip()})

# also collect every line containing the pin name with "->" (covers 列2-6 style)
pin_lines = {}
for i, l in enumerate(cm, 1):
    if "->" in l:
        for m in re.finditer(r"->\s*([A-Za-z0-9_+]+)\s*$", l):
            pin_lines.setdefault(m.group(1), []).append({"line": i, "text": l.strip()})

# ---------- component statistic channel map ----------
chan_rows = []
for i, l in enumerate(cs, 1):
    m = re.match(r"^\s+(S\d+_[A-Za-z0-9_+()\-]+)\s*->\s*(.+?)\s*\((.+?)\)\s*$", l)
    if m:
        chan_rows.append({"line": i, "port": m.group(1), "deviceNet": m.group(2), "device": m.group(3)})

ir_by_pin = {p["pin"]: p for p in ir["pins"]}
ir_path_by_pin = {}
for p in ir["paths"]:
    if p["id"].startswith("PIN_"):
        ir_path_by_pin[p["id"][4:]] = p

TM_PINS = ["VBAT_F_S1", "VBAT_S_S1", "VAC1_F_S1", "VAC1_S_S1",
           "nQON_F_S1", "nQON_S_S1", "AGND_F_S1", "AGND_S_S1", "AMUX_F_S1", "AMUX_S_S1"]

facts = {"pins": {}, "channel_map": chan_rows, "relay_states_ir": {}, "map_tokens": {}}
for r in ir["relays"]:
    facts["relay_states_ir"][r["name"]] = r["state"]
for i, l in enumerate(cm, 1):
    for m in re.finditer(r"K(\d+)\(Relay-(ON|NC)\)", l):
        facts["map_tokens"].setdefault(m.group(1), []).append({"line": i, "state": m.group(2)})

for pid in TM_PINS:
    base = pid.rsplit("_", 2)[0]
    entry = {
        "pin": pid,
        "ir_pin": ir_by_pin.get(pid),
        "ir_path": ir_path_by_pin.get(pid),
        "map_pin_section": map_sections.get(base) or map_sections.get(pid),
        "map_tail_rows": pin_lines.get(pid, []),
        "map_base_rows": pin_lines.get(base, [])[:20],
    }
    facts["pins"][pid] = entry

(OUT / "tm108-facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")

txt = []
txt.append("### channel map (Component-Statistic.txt) rows whose port or device net relates to the TM108 path")
for c in chan_rows:
    if re.search(r"(VAC|NQON|VBAT|AGND|PD3|HG1|QON|DCM|QTMU|VAC123)", c["port"] + c["deviceNet"]):
        txt.append("%5d| %-34s -> %-40s (%s)" % (c["line"], c["port"], c["deviceNet"], c["device"]))

txt.append("")
txt.append("### map pin sections")
for pid, e in facts["pins"].items():
    txt.append("---- %s" % pid)
    sec = e["map_pin_section"]
    if sec:
        for h in sec["header_lines"]:
            txt.append("H %5d| %s" % (h["line"], h["text"]))
        for r in sec["rows"]:
            txt.append("R %5d| %s" % (r["line"], r["text"]))
    for r in e["map_tail_rows"]:
        txt.append("T %5d| %s" % (r["line"], r["text"]))
    for r in e["map_base_rows"]:
        txt.append("B %5d| %s" % (r["line"], r["text"]))
    p = e["ir_pin"]
    if p:
        txt.append("IR pin sources=%s reqRelays=%s nets=%s proofs=%s kelvin=%s"
                   % (p["sources"], p["requiredRelays"], p["nets"], p["proofCount"], p["kelvinPairs"]))
    pp = e["ir_path"]
    if pp:
        txt.append("IR path from=%s conf=%s" % (pp["from"], pp["confidence"]))
        for c in pp.get("relayChainUnion", []):
            txt.append("IR chain %-24s %s" % (c[0], c[1]))
    txt.append("")

txt.append("### relay default state (IR relays[].state) vs map tokens for relays on the TM108 pin paths")
for n in ["7", "8", "13", "17", "18", "19", "20", "21", "62", "64", "65", "66", "70", "82",
          "86", "87", "88", "89", "90", "92", "130", "136", "137", "138", "139", "140", "141",
          "142", "143", "144", "145", "146", "154", "155"]:
    nm = [k for k in facts["relay_states_ir"] if re.match(r"K%s\b" % n, k)]
    toks = facts["map_tokens"].get(n, [])
    states = sorted({t["state"] for t in toks})
    txt.append("K%-4s IR=%s tokens=%s n=%d lines=%s" % (
        n, [facts["relay_states_ir"][x] for x in nm], states, len(toks),
        [t["line"] for t in toks][:12]))

(OUT / "tm108-facts.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
print("WROTE tm108-facts.json / tm108-facts.txt")
print("channel rows:", len(chan_rows), "pin sections:", len(map_sections))
