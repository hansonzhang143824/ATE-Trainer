#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TM108 cross-artifact check helper (t3). Read-only on project/DALI.

Writes tm108-crosscheck-raw.txt next to itself with the raw evidence lines used
by the audit report.
"""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).parent
ir = json.loads(pathlib.Path("project/DALI/schematic-ir.json").read_text(encoding="utf-8"))
def read_lines(p):
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read().splitlines()


cm = read_lines("project/DALI/SCH-Connect-Map.txt")
cs = read_lines("project/DALI/Component-Statistic.txt")

out = []
w = out.append

w("### IR: paths whose relayChainUnion contains a given K number")
for n in [19, 18, 20, 13, 64, 66, 62, 70, 17, 8, 7, 90, 87, 89, 92, 140, 21, 65, 137, 136, 138, 139]:
    pat = "K%d_" % n
    hits = []
    for p in ir["paths"]:
        names = [c[0] for c in p.get("relayChainUnion", [])]
        if any(x.startswith(pat) for x in names):
            states = sorted({c[1] for c in p["relayChainUnion"] if c[0].startswith(pat)})
            hits.append((p["id"], states))
    w("K%-4d paths=%d %s" % (n, len(hits), hits[:8]))

w("")
w("### IR relays detail (name-prefix match)")
for r in ir["relays"]:
    if re.match(r"K(19|18|20|13|64|66|62|70|92|140|21|65|137)\b", r.get("name", "")):
        w(json.dumps({k: r[k] for k in r if k != "evidence"}, ensure_ascii=False))
        for e in r.get("evidence", [])[:3]:
            w("     ev: %s | %s" % (e.get("path"), e.get("locator")))

w("")
w("### IR: VAC1 / nQON / VBAT path records (full)")
for pid in ["PIN_VAC1_F_S1", "PIN_VAC1_S_S1", "PIN_nQON_F_S1", "PIN_nQON_S_S1",
            "PIN_VBAT_F_S1", "PIN_VBAT_S_S1", "PIN_AGND_F_S1", "PIN_AGND_S_S1"]:
    for p in ir["paths"]:
        if p["id"] == pid:
            w(json.dumps(p, ensure_ascii=False, indent=1))

w("")
w("### IR: nets whose name matches VAC/K64/K19/K17/K13/Cap")
for n in ir["nets"]:
    if re.search(r"(VAC|K64|K19|K17|K13|Cap2_VBAT|Cap1_VBAT)", n["name"]):
        w(json.dumps(n, ensure_ascii=False))

w("")
w("### IR: openQuestions + hazards")
w(json.dumps(ir.get("openQuestions"), ensure_ascii=False, indent=1))
w(json.dumps(ir.get("hazards"), ensure_ascii=False, indent=1))

w("")
w("### IR: validation block")
w(json.dumps(ir.get("validation"), ensure_ascii=False, indent=1)[:6000])

w("")
w("### Component-Statistic.txt lines 1-60")
for i in range(1, 61):
    w("%5d| %s" % (i, cs[i - 1]))

w("")
w("### Component-Statistic.txt lines 415-495")
for i in range(415, len(cs) + 1):
    w("%5d| %s" % (i, cs[i - 1]))

w("")
w("### SCH-Connect-Map.txt lines 1-40")
for i in range(1, 41):
    w("%5d| %s" % (i, cm[i - 1]))

w("")
w("### SCH-Connect-Map.txt lines 659-690 (ACM section head)")
for i in range(659, 691):
    w("%5d| %s" % (i, cm[i - 1]))

w("")
w("### SCH-Connect-Map.txt lines 920-966")
for i in range(920, len(cm) + 1):
    w("%5d| %s" % (i, cm[i - 1]))

w("")
w("### grep: lines mentioning K19 / K17 / K13 / K64 / K66 / K65 / K21 / K92 / K140 / K7 / K8 anywhere")
pat = re.compile(r"\bK(19|17|13|64|66|65|21|92|140|7|8)\b")
for label, lines in (("SCH-Connect-Map.txt", cm), ("Component-Statistic.txt", cs)):
    w("--- %s ---" % label)
    for i, l in enumerate(lines, 1):
        if pat.search(l):
            w("%5d| %s" % (i, l))

(OUT / "tm108-crosscheck-raw.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("WROTE", OUT / "tm108-crosscheck-raw.txt", len(out), "lines")
