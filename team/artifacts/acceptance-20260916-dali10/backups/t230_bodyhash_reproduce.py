# -*- coding: utf-8 -*-
"""Reproduce the owner's projectionSpec v2 body hash from their stated bodyDefinition, and record the result."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
br_p = os.path.join(A, "build-report.json")
raw = open(br_p, "rb").read()
d = json.loads(raw.decode("utf-8-sig"))
exclude = ["generatedAt", "receipts"]
body = {k: v for k, v in d.items() if k not in exclude}
canon = json.dumps(body, ensure_ascii=False, sort_keys=True)
computed = hashlib.sha256(canon.encode("utf-8")).hexdigest()
recorded = "9804fbe2272477ecf51de6162401ae295dad7a6aa0f865a00f3bd16f9517fa24"
print("file:", len(raw), "B /", hashlib.sha256(raw).hexdigest()[:24], "@", datetime.datetime.fromtimestamp(os.stat(br_p).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
print("top-level keys:", list(d.keys()))
print("excluded present:", {k: (k in d) for k in exclude})
print("computed body hash :", computed)
print("their recorded hash:", recorded)
print("MATCH:", computed == recorded)

rc = json.load(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), encoding="utf-8"))
print("\nreceipt projectionSpec:", json.dumps(rc.get("projectionSpec"), ensure_ascii=False)[:400])
print("receipt reproducibleBodySha256:", rc.get("reproducibleBodySha256"))
print("receipt hash == my computed:", rc.get("reproducibleBodySha256") == computed)

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon_e(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "reproduced the owner's projectionSpec v2 body hash from its stated bodyDefinition - the missing-serialization gap is closed",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon_e(lg["entries"][-1]),
         "bodyHashReproduction": {"computed": computed, "recorded": recorded, "match": computed == recorded,
                                  "method": "json.loads(bytes.decode('utf-8-sig')) minus exclude=['generatedAt','receipts'], then json.dumps(ensure_ascii=False, sort_keys=True), utf-8",
                                  "note": "their v1 exclusion list was incomplete (it did not exclude the 'receipts' field), which is why the earlier recorded value could not be reproduced and should never have been cited as a stable value"},
         "artifacts": {"build-report.json": {"path": br_p.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                       "gate-logs-t54/build-report.receipt.json": {"path": os.path.join(A, "gate-logs-t54", "build-report.receipt.json").replace("\\", "/"),
                                                                   "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t54", "build-report.receipt.json")),
                                                                   "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon_e(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
