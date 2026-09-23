# -*- coding: utf-8 -*-
"""Independently verify the owner's control experiment and prefix guard."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

gen = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
src = open(gen, encoding="utf-8").read() if os.path.exists(gen) else ""
m = re.search(r"DO_NOT_TOUCH_PREFIXES\s*=\s*\(([^)]*)\)", src)
print("generator:", rec(gen))
print("DO_NOT_TOUCH_PREFIXES =", m.group(1).strip() if m else "NOT FOUND")

for f in ("gate-logs-t54/t54_prefix_and_union_experiment.py", "gate-logs-t54/t54-prefix-union-experiment.log"):
    print("  evidence:", f, rec(os.path.join(A, f)))

sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
s = json.load(open(sh, encoding="utf-8"))
ppn = s.get("preservedPeerNamespaces") or {}
blk = ppn.get("setupArchitectFreezeAnchors") or {}
raw = open(sh, "rb").read()
print("\nlive shared file:", len(raw), "B /", hashlib.sha256(raw).hexdigest()[:24])
print("  foreign (setupArchitect) entries:", len(blk.get("anchors") or {}))
print("  TESTSENTINEL present:", "TESTSENTINEL" in raw.decode("utf-8", "replace"))
print("  top-level keys:", list(s.keys())[:12])
print("  preservedPeerNamespaces keys:", list(ppn.keys()))

# experiment log content
lg = os.path.join(A, "gate-logs-t54", "t54-prefix-union-experiment.log")
if os.path.exists(lg):
    print("\n--- experiment log (tail) ---")
    lines = open(lg, encoding="utf-8", errors="replace").read().splitlines()
    for l in lines[-18:]:
        print("   ", l[:150])

br = rec(os.path.join(A, "build-report.json"))
rc = rec(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"))
print("\npeer build-report:", br)
print("peer receipt     :", rc)
if br and rc:
    rd = json.load(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), encoding="utf-8"))
    print("  receipt consistent with live report:", rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"])
