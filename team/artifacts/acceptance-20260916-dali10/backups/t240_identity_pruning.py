# -*- coding: utf-8 -*-
"""Record the owner's mechanisation of identity-based appending, and the rule it establishes: identity de-duplication needs a stable identity projection."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

RULE = {
    "name": "identity-based pruning (established by the owner's receipt-history fix)",
    "statement": ("An append-only log that records an artefact's identity should append ONLY when the identity changes, and should say so in a reason field (identity-change versus routine-reverify, not appended). "
                  "Growth is then bounded by the number of distinct identities rather than by the number of checks."),
    "precondition": ("Identity de-duplication is possible ONLY when the identity projection is stable. The owner verified the body hash (projectionSpec v2, with serialization/encoding/bodyDefinition declared) is stable across seconds; without that, there would be no way to decide whether an identity had changed. "
                     "So a stable projection is a PRECONDITION for pruning, not an independent nicety."),
    "instance": {"before": "54 rows / 107,127 B with only 5 distinct body hashes - 49 rows recorded an UNCHANGED identity",
                 "fix": "(a) append only on identity change; (b) add a reason field distinguishing identity-change from routine-reverify",
                 "selfProof": "three consecutive runs across second boundaries gave 54 -> 54 -> 54 rows, all skipped",
                 "raisedBy": "my observation that the history grew on every verification run; the owner mechanised it rather than deferring it"},
    "family": "same economy as 'one fewer write is one fewer drift', applied to automated logging",
}
doc["identityBasedPruningRule"] = RULE
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# verify the owner's numbers from the live files
recs_p = os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl")
rows = [l for l in open(recs_p, encoding="utf-8").read().splitlines() if l.strip()]
bodies = set()
for l in rows:
    try:
        b = json.loads(l).get("reproducibleBodySha256")
        if b:
            bodies.add(b)
    except Exception:
        pass
print("receipts.jsonl rows:", len(rows), "| distinct body hashes:", len(bodies))

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "recorded the owner's mechanisation of identity-based appending and the precondition it rests on (a stable identity projection)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "identityBasedPruningRule": RULE,
         "mySideMeasurement": {"receiptsRows": len(rows), "distinctBodyHashes": len(bodies)},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "gate-logs-t54/build-report.receipts.jsonl": {"path": recs_p.replace("\\", "/"), "sizeBytes": os.path.getsize(recs_p),
                                                                     "sha256": hashlib.sha256(open(recs_p, "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
