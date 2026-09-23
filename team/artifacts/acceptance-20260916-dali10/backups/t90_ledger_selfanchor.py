# -*- coding: utf-8 -*-
"""Close the reviewer's ledger finding: classify entry 6, add per-entry self-anchoring (ledger's own size/sha before the write), and append a full entry."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")

pre = open(LOG, "rb").read()
pre_size, pre_sha = len(pre), hashlib.sha256(pre).hexdigest()
lg = json.loads(pre.decode("utf-8"))
print("ledger BEFORE this write: %d B / %s | entries=%d" % (pre_size, pre_sha, len(lg["entries"])))

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

lg["schema"]["selfRecord"] = "each entry records the ledger's OWN sizeBytes/sha256 as measured immediately before that write, so 'when was the ledger appended to' is itself recomputable"
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "close the reviewer's finding: classify the remaining hollow entry (idx6) + add self-anchoring to every future entry + full value set",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": pre_size, "ledgerSha256BeforeThisWrite": pre_sha, "entriesBeforeThisWrite": len(lg["entries"])},
    "classificationOfEarlierEntries": [{"snapshotIndex": 6, "kind": "tick", "artifactsAbsent": True,
                                        "artifactsAbsentReason": "recorded the peer note value and my anchors-file hash and the endorsement of section 2.3 - a tick, not a full value-set snapshot"}],
    "note": "entries 2-6 remain hollow by construction (their per-artifact bytes were never captured); they are classified, not back-filled. From this entry onward every entry is kind=full and carries contractRevision + artifacts + selfAnchor.",
    "artifacts": {k: rec(v) for k, v in FILES.items()},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
print("ledger AFTER : %d B / %s | entries=%d" % (len(post), hashlib.sha256(post).hexdigest(), len(lg["entries"])))
print("kinds:", [e.get("kind") for e in lg["entries"]])
print("entries with artifacts:", [e.get("snapshotIndex") for e in lg["entries"] if e.get("artifacts")])
print("current t34:", rec(FILES["acceptance-report.json"]))
