# -*- coding: utf-8 -*-
"""Create/append the append-only freeze snapshot log (setup-architect's own), which records one entry per declared snapshot with path+size+sha256+time."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")

FILES = {
    "setup-contract.json": "team/artifacts/acceptance-20260916-dali10/setup-contract.json",
    "setup-contract-build.py": "team/artifacts/acceptance-20260916-dali10/setup-contract-build.py",
    "setup-contract-pin.json": "team/artifacts/acceptance-20260916-dali10/setup-contract-pin.json",
    "implementation-input-pin.json": "team/artifacts/acceptance-20260916-dali10/implementation-input-pin.json",
    "acceptance-report.json": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json",
    "t35-contract-reconciliation.md": "team/artifacts/acceptance-20260916-dali10/t35-contract-reconciliation.md",
    "t41-tm601-bst-path-determination.md": "team/artifacts/acceptance-20260916-dali10/t41-tm601-bst-path-determination.md",
    "implementation-payload-TM600-TM601.cpp": "team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp",
    "test-plan.json": "team/artifacts/acceptance-20260916-dali10/test-plan.json",
    "scripts/gate_baseline.json": "scripts/gate_baseline.json",
}

snap = {}
for name, rel in FILES.items():
    b = open(rel, "rb").read()
    snap[name] = {"sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                  "measuredAt": datetime.datetime.fromtimestamp(os.stat(rel).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

if os.path.exists(LOG):
    doc = json.load(open(LOG, encoding="utf-8"))
else:
    doc = {"purpose": ("APPEND-ONLY snapshot log maintained by setup-architect. Each entry records one point-in-time snapshot of my own artifacts and the shared inputs I cite, so that a citation can be checked "
                       "even after a live file is written again. Rule: filenames + recomputed sha256 + recomputed time; a remembered value is unverified; the log itself is the only thing I append to, never rewrite."),
           "owner": "setup-architect", "entries": []}

doc["entries"].append({
    "snapshotIndex": len(doc["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "reason": "post rev-39 freeze (contract) + t34 L19/L20/L40/L41 updates + pin plan row at live v25 (reviewer requested a per-round snapshot instead of repeated freeze restatements)",
    "contractRevision": 39,
    "payloadCanonical": {"path": "team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp",
                         "sizeBytes": 43806, "sha256": "66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4", "writesStopped": True},
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76],
                      "expectedForTM600": [48, 60, 61, 76, 83]},
    "artifacts": snap,
})
json.dump(doc, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(LOG, "rb").read()
print("snapshot log:", LOG)
print("entries:", len(doc["entries"]), "| file:", len(b), "B /", hashlib.sha256(b).hexdigest(),
      "@", datetime.datetime.fromtimestamp(os.stat(LOG).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
for k, v in snap.items():
    print("   %-42s %8d B  %s @%s" % (k, v["sizeBytes"], v["sha256"][:20], v["measuredAt"]))
