# -*- coding: utf-8 -*-
"""Verify and fix the TM643 function-name typo (VAT vs VBAT) in my artifacts; sweep for other occurrences."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
DEP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
src = open(DEP, encoding="utf-8", errors="replace").read()
print("source: TM643_VBAT_LOOP_INDICTOR =", src.count("TM643_VBAT_LOOP_INDICTOR"), "| TM643_VAT_LOOP_INDICTOR =", src.count("TM643_VAT_LOOP_INDICTOR"))

BAD = "TM643_VAT_LOOP_INDICTOR"
GOOD = "TM643_VBAT_LOOP_INDICTOR"
targets = {
    "acceptance-report.json": os.path.join(A, "acceptance-report.json"),
    "setupArchitect-anchors.json": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"),
    "setupArchitect-freeze-snapshots.json": os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json"),
    "PATH-MAP.md": os.path.join(A, "PATH-MAP.md"),
    "t34-carrier-pointer.json": os.path.join(A, "t34-carrier-pointer.json"),
}
for name, p in targets.items():
    if not os.path.exists(p):
        continue
    b = open(p, encoding="utf-8").read()
    n = b.count(BAD)
    if n:
        b = b.replace(BAD, GOOD)
        open(p, "w", encoding="utf-8").write(b)
        bb = open(p, "rb").read()
        print("FIXED %-38s occurrences=%d -> %d B / %s @%s" % (name, n, len(bb), hashlib.sha256(bb).hexdigest(),
              datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")))
    else:
        print("clean  %-38s occurrences=0" % name)

# sweep
print("\npost-fix sweep:")
for name, p in targets.items():
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        print("  %-40s bad=%d good=%d" % (name, t.count(BAD), t.count(GOOD)))
