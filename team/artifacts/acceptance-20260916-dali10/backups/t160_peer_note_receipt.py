# -*- coding: utf-8 -*-
"""Recompute the plan-side note the reviewer-role peer cites, and record the receipt; log the byte-copy snapshot verification they performed."""
import json, hashlib, os, datetime, glob

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

note = rec(os.path.join(A, "review-handoff-note-plan-side.md"))
print("peer note (recomputed now):", note)
print("  they cited: 77,249 B / 2ffea93acda7ca1b... @23:32:06")

# re-verify my own byte-copy snapshot against its manifest (independent of their check)
snap = os.path.join(A, "backups", "setuparch-20260916-230435")
man = json.load(open(os.path.join(snap, "MANIFEST.json"), encoding="utf-8"))
ok = bad = 0
for name, meta in man["files"].items():
    p = os.path.join(snap, name)
    if os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == meta["sha256"]:
        ok += 1
    else:
        bad += 1
        print("  MISMATCH:", name)
print("byte-copy snapshot re-verified: %d matched / %d mismatched (of %d)" % (ok, bad, len(man["files"])))
print("manifest:", rec(os.path.join(snap, "MANIFEST.json")))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "peer verified my byte-copy snapshot 14/14; recorded their new note anchor and re-verified the snapshot myself",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "byteCopySnapshotReverified": {"dir": snap.replace("\\", "/"), "files": len(man["files"]), "matched": ok, "mismatched": bad,
                                        "peerCheck": "test-strategy-architect independently verified 14/14 against the manifest and recorded it as the run's first systematic byte-level fallback",
                                        "whyItMatters": "neither size nor hash can restore a state once a live file moves on; only a byte copy can - this closes the hole exposed by the same-size/three-hash case"},
         "peerReceipts": [dict(note, owner="test-strategy-architect", citation="recomputed by me (not relayed)",
                               note="their cited 77,249 B @23:32:06; my recomputation above is the current value")],
         "artifacts": {"review-handoff-note-plan-side.md": note,
                       "backups/setuparch-20260916-230435/MANIFEST.json": rec(os.path.join(snap, "MANIFEST.json")),
                       "acceptance-report.json": rec(os.path.join(A, "acceptance-report.json"))}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["byteCopySnapshot"] = {"dir": snap.replace("\\", "/"), "files": len(man["files"]), "peerVerified": ok,
                           "manifestSha256": hashlib.sha256(open(os.path.join(snap, "MANIFEST.json"), "rb").read()).hexdigest(),
                           "note": "read-only evidence; peer verified 14/14; re-verified by me after their check"}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
