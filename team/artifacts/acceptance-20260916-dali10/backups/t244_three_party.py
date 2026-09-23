# -*- coding: utf-8 -*-
"""Extend the independent-convergence register with the three-party instance on naming (the moment in the name)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

reg = doc.get("independentConvergenceRegister") or {}
reg["instances"] = (reg.get("instances") or []) + [
    "THREE-PARTY instance (naming): put the moment in the NAME - I phrased it as 'a deliberate record must name its moment', the owner implemented it as `mirrorSizeAtMirrorTime` (the identifier itself carries the time), and the plan side recorded the same conclusion independently; three parties arrived at the same fix by different routes.",
]
reg["threePartNote"] = ("This is the register's first three-party instance: convergence between two parties can still be coincidence or imitation, but three independent arrivals - in a naming decision that each could have made differently - is stronger evidence still. "
                        "Practical effect: a reader of the field knows which moment the value belongs to WITHOUT reading a note.")
doc["independentConvergenceRegister"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("register instances now:", len(reg["instances"]))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "extended the independent-convergence register with the three-party instance on naming; no change to the carrier was needed (the peer answered both of my questions with 'no change')",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "threePartyConvergence": reg["instances"][-1],
         "noChangeDecisions": {
             "measuredNow": "retained - it already carries a time and a label; removing it would remove the reader's knowledge of which moment the value belongs to",
             "externalAnchor": "retained as the live contract field the gate actually reads; if the summary table and the contract field ever diverge, the contract field governs",
         },
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
