#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Targeted evidence collection for the TM108 audit (t3, read-only).

1. Component-Statistic.txt: lines for each instrument-port -> device-name mapping
   connected to the TM108-relevant device nets.
2. SCH-Connect-Map.txt: the S10 / QTMUe / DCM column rows, the P2P and pull-up
   rows, and the per-pin rows for VBAT / VAC1 / nQON / AGND.
Writes tm108-evidence-collect.txt.
"""
import pathlib
import re

OUT = pathlib.Path(__file__).parent
PROJ = pathlib.Path("project/DALI")


def read_lines(p):
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read().splitlines()


cm = read_lines(PROJ / "SCH-Connect-Map.txt")
cs = read_lines(PROJ / "Component-Statistic.txt")

buf = []
w = buf.append

w("#### Component-Statistic.txt: port -> device rows for the TM108 device nets")
want_dev = ("VAC123_AMUX_ACM", "NQON_HG1_ACM", "VBAT_PD3_FXVI", "QTMU_S1")
for i, l in enumerate(cs, 1):
    if any(d in l for d in want_dev):
        w("%5d| %s" % (i, l.rstrip()))

w("")
w("#### Component-Statistic.txt: DUT PIN / TP / net inventory lines relevant to TM108")
for i, l in enumerate(cs, 1):
    if re.search(r"(DUT PIN|TP_VAC1|TP_VBAT|TP_nQON|AGND_F_S1|AGND_S_S1|NetCap1_VAC1|NetCap1_VBAT|NetK64|NetK18|NetK19|NetK17|NetK13|NetK92)", l):
        w("%5d| %s" % (i, l.rstrip()[:400]))

w("")
w("#### SCH-Connect-Map.txt: rows containing QTMU / DCM / S10")
for i, l in enumerate(cm, 1):
    if re.search(r"(QTMU|DCM|S10_CH0)", l):
        w("%5d| %s" % (i, l.rstrip()))

w("")
w("#### SCH-Connect-Map.txt: section header lines (all)")
for i, l in enumerate(cm, 1):
    if l.startswith("## ") or l.startswith("### ") or l.startswith("  ##"):
        w("%5d| %s" % (i, l.rstrip()))

w("")
w("#### SCH-Connect-Map.txt: lines 860-925 (P2P / pull-up / cap rows)")
for i in range(860, 926):
    if i <= len(cm):
        w("%5d| %s" % (i, cm[i - 1].rstrip()))

w("")
w("#### SCH-Connect-Map.txt: lines 924-966 (DUT PIN -> net mapping)")
for i in range(924, len(cm) + 1):
    w("%5d| %s" % (i, cm[i - 1].rstrip()))

w("")
w("#### SCH-Connect-Map.txt: rows for VBAT / VAC1 / VAC_WL / nQON / AGND / HG1 (any column)")
pat = re.compile(r"(VBAT|VAC1|VAC_WL|nQON|AGND|HG1)")
for i, l in enumerate(cm, 1):
    if "->" in l and pat.search(l):
        w("%5d| %s" % (i, l.rstrip()))

(OUT / "tm108-evidence-collect.txt").write_text("\n".join(buf) + "\n", encoding="utf-8")
print("WROTE", OUT / "tm108-evidence-collect.txt", len(buf), "lines")
