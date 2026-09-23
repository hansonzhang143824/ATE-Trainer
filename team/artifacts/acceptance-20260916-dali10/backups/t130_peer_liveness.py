# -*- coding: utf-8 -*-
"""Recompute the peer report and its receipt, and record in my anchors entry that the peer report is a live file whose identity comes from the receipt."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"

def rec(p):
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "sha256_lf_normalized": hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

report = rec(os.path.join(A, "build-report.json"))
receipt_path = os.path.join(A, "gate-logs-t54", "build-report.receipt.json")
receipt = rec(receipt_path)
print("peer build-report (recomputed):", report)
print("peer receipt (recomputed)     :", receipt)
if receipt:
    rd = json.load(open(receipt_path, encoding="utf-8"))
    print("receipt fields:", sorted(rd.keys()))
    print("receipt isFrozen:", rd.get("isFrozen"))
    print("receipt sha matches current report bytes:", rd.get("sha256") == report["sha256"] if report else "n/a")
    print("receipt size matches:", rd.get("sizeBytes") == report["sizeBytes"] if report else "n/a")

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["peer/build-report.json"] = dict(
    report, owner="compile-diagnostician",
    note="peer artifact, owner-reported + recomputed by me for size/sha; content not reviewed by me",
    liveness="THE PEER REPORT IS A LIVE FILE: it must not be labelled FROZEN and its in-report self-computed hashes must not be cited. To pin the identity of a particular version, read the receipt below and recompute it.",
    identitySource=("gate-logs-t54/build-report.receipt.json - " + ("%d B / %s @ %s (isFrozen=%s, sha256_lf_normalized=%s)" % (
        receipt["sizeBytes"], receipt["sha256"], receipt["measuredAt"],
        json.load(open(receipt_path, encoding="utf-8")).get("isFrozen"),
        receipt["sha256_lf_normalized"]) if receipt else "not found")))
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("\nanchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "peer report is a live file - its identity is taken from the owner's receipt (compile-diagnostician's livenessDeclaration); values recomputed by me",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "peerReportLiveness": {"report": report, "identitySource": receipt,
                                 "rule": "the peer report must not be labelled FROZEN and its in-report hashes must not be cited; a specific version is pinned via the receipt file and recomputed"},
         "artifacts": {"acceptance-report.json": rec(os.path.join(A, "acceptance-report.json")),
                       "gate-logs-t28/setupArchitect-anchors.json": rec(ap),
                       "gate-logs-t54/build-report.receipt.json": receipt}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
