# -*- coding: utf-8 -*-
"""Add the deployed-tree anchor (two-object comparison) to t34; refresh my anchors file and append a snapshot-log entry."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
DEP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"

db = open(DEP, "rb").read()
dsize, dsha = len(db), hashlib.sha256(db).hexdigest()
dmtime = datetime.datetime.fromtimestamp(os.stat(DEP).st_mtime).strftime("%Y-%m-%d %H:%M:%S")
print("deployed tree:", dsize, "B /", dsha, "@", dmtime)

f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
L42 = ("L42 (TWO-OBJECT COMPARISON, recomputed on my side for t54's re-run): object A = the DELIVERED payload (team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp) = 43,806 B / "
       "66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24 -> the gate's own assertion gives TM600 missing=[] and TM601 missing=[] (0 errors); object B = the DEPLOYED tree "
       "(D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp) = " + str(dsize) + " B / " + dsha + " @ " + dmtime + " -> the same assertion gives TM600 missing=[48,76] and TM601 missing=[], 2 errors. "
       "Therefore the pre-landing CLI exit=1 belongs to object B alone and is the expected pre-REPLACE state; after landing, object B must be re-measured and the CLI re-run once (the run must first check that [scan] targets = N > 0, "
       "because a source without the ZCD/OCP-family ramp items makes the script return early with an 'empty PASS' - see L34).")
if L42 not in d["limitations"]:
    d["limitations"].append(L42)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%H:%M:%S"), "| limitations:", len(d["limitations"]))

# my anchors file
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
doc["anchors"]["acceptance-report.json"] = rec(f34)
doc["anchors"]["DEPLOYED_tree/source/test.cpp"] = {"path": "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp", "sizeBytes": dsize, "sha256": dsha, "measuredAt": dmtime, "note": "read-only reference object for the two-object comparison"}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

# snapshot log entry
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))
lg["entries"].append({"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      "reason": "deployed-tree anchor re-measured for t54's re-run (two-object comparison) + t34 L42 recorded",
                      "deployedTree": {"path": "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp", "sizeBytes": dsize, "sha256": dsha, "measuredAt": dmtime},
                      "t34": {"sizeBytes": len(b34), "sha256": hashlib.sha256(b34).hexdigest()},
                      "anchorsFile": {"sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
lb = open(LOG, "rb").read()
print("snapshot log:", len(lg["entries"]), "entries |", len(lb), "B /", hashlib.sha256(lb).hexdigest())
