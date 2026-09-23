#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump SCH-Connect-Map line ranges for TM108 audit evidence (t3, read-only)."""
import pathlib
import sys

OUT = pathlib.Path(__file__).parent
p = pathlib.Path("project/DALI/SCH-Connect-Map.txt")
with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
    lines = fh.read().splitlines()

ranges = [(25, 90), (659, 700), (795, 860), (860, 930)]
buf = []
for a, b in ranges:
    buf.append("===== SCH-Connect-Map.txt lines %d-%d =====" % (a, b))
    for i in range(a, min(b, len(lines)) + 1):
        buf.append("%5d| %s" % (i, lines[i - 1]))
    buf.append("")

# every line mentioning K18 / K19 / K17 / K20 / K13 / K21 / K64 / K65 / K66 / K92 / K140 / K7 / K8
import re
pat = re.compile(r"\bK(7|8|13|17|18|19|20|21|64|65|66|92|140)\b")
buf.append("===== all lines matching K7/K8/K13/K17/K18/K19/K20/K21/K64/K65/K66/K92/K140 =====")
for i, l in enumerate(lines, 1):
    if pat.search(l):
        buf.append("%5d| %s" % (i, l))

(OUT / "tm108-connectmap-ranges.txt").write_text("\n".join(buf) + "\n", encoding="utf-8")
print("WROTE", OUT / "tm108-connectmap-ranges.txt", len(buf), "lines")
print("total map lines", len(lines))
