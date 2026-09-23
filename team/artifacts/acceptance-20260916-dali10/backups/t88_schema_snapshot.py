# -*- coding: utf-8 -*-
"""Classify snapshot-log entries 2-5 (they lack contractRevision/artifacts), declare the required schema for future entries, and append a complete entry."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))

print("--- current entries ---")
for e in lg["entries"]:
    print("idx=%s takenAt=%s keys=%s artifacts=%s rev=%s" % (
        e.get("snapshotIndex"), e.get("takenAt"), ",".join(sorted(e.keys())),
        len(e.get("artifacts") or {}), e.get("contractRevision")))

# classification of the hollow entries, based on what they actually contain
classes = {
    2: ("tick+cross-check", "recorded the reviewer's K60 self-correction artifacts; carried peerArtifacts (recomputed) and a t34Carrier mapping, but no per-artifact value set and no contract revision"),
    3: ("tick+anchor", "recorded the deployed-tree anchor (recomputed) for the two-object comparison and t34's hash at that moment; no contract revision, no full artifacts map"),
    4: ("tick+measurement", "recorded the BEFORE measurement of the shared anchors namespace (preservedNamespaceEntries_before=1) plus the owner's admission; no artifact value set"),
    5: ("tick+withdrawal", "recorded the withdrawal of my 'shared file drops my keys' claim with the ledger evidence and the residual UNKNOWN; no artifact value set"),
}

# complete entry with the full required schema
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

FILES = {
    "setup-contract.json": os.path.join(A, "setup-contract.json"),
    "setup-contract-build.py": os.path.join(A, "setup-contract-build.py"),
    "setup-contract-pin.json": os.path.join(A, "setup-contract-pin.json"),
    "implementation-input-pin.json": os.path.join(A, "implementation-input-pin.json"),
    "acceptance-report.json": os.path.join(A, "acceptance-report.json"),
    "t34-carrier-pointer.json": os.path.join(A, "t34-carrier-pointer.json"),
    "t34-CARRIER-PATH.md": os.path.join(A, "t34-CARRIER-PATH.md"),
    "t35-contract-reconciliation.md": os.path.join(A, "t35-contract-reconciliation.md"),
    "t41-tm601-bst-path-determination.md": os.path.join(A, "t41-tm601-bst-path-determination.md"),
    "implementation-payload-TM600-TM601.cpp": os.path.join(A, "implementation-payload-TM600-TM601.cpp"),
    "test-plan.json": os.path.join(A, "test-plan.json"),
    "gate-logs-t54/bst-sw.log": os.path.join(A, "gate-logs-t54", "bst-sw.log"),
    "scripts/gate_baseline.json": "scripts/gate_baseline.json",
}

lg["schema"] = {
    "requiredPerEntry": ["snapshotIndex", "takenAt", "kind", "reason", "contractRevision", "artifacts"],
    "kindEnum": ["full", "tick"],
    "rule": ("An entry whose value set was not recorded must say so: kind='tick' and artifactsAbsentReason. 'A record that carries no values' and 'no record' must remain distinguishable after the fact. "
             "Entries 2-5 were written before this schema was declared and are classified in the appended entry below; their bytes cannot be back-filled, which is exactly why the schema is now explicit."),
}
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "schema declaration + retrospective classification of entries 2-5 + full value set (reviewer point 3: entries 2-5 carried no contractRevision/artifacts)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "classificationOfEarlierEntries": [{"snapshotIndex": k, "kind": v[0], "artifactsAbsent": True, "artifactsAbsentReason": v[1]} for k, v in sorted(classes.items())],
    "note": "back-filling entries 2-5 is impossible (their per-artifact bytes were never captured) - recorded here rather than silently rewritten, because this file is append-only.",
    "artifacts": {k: rec(v) for k, v in FILES.items()},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(LOG, "rb").read()
print("\nsnapshot log: %d entries | %d B / %s @%s" % (len(lg["entries"]), len(b), hashlib.sha256(b).hexdigest(),
      datetime.datetime.fromtimestamp(os.stat(LOG).st_mtime).strftime("%Y-%m-%d %H:%M:%S")))
print("new entry artifacts:", len(lg["entries"][-1]["artifacts"]))
