# -*- coding: utf-8 -*-
"""Adopt the joint rule 'attribute by measurement, not memory or inference' with both instances (theirs and mine)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
RULE = {
    "name": "attribute by measurement, not by memory or inference (joint rule, one instance from each side)",
    "statement": "Attribution and values alike must be MEASURED. The outgoing message log is part of the evidence base, not memory.",
    "instanceCounterparty": ("the plan side asserted three times that it had never claimed a particular expectation value; the setup side produced the original sentence from its own outgoing log, and the plan side withdrew - it had defended a position from memory."),
    "instanceMine": ("I attributed a diagnostician reading to a stale rev-28 copy BY INFERENCE without measuring it, and withdrew it after the owner supplied the evidence anchor (the log's self-reported rev=32)."),
    "sharedFailureMode": "treating a remembered or inferred attribution as a measurement",
    "whyItMatters": "recorded with one instance from each side so the rule reads as a structural risk of multi-agent collaboration rather than one member's slip",
    "recordedBy": "the plan side as its section 2.5b, using the joint-two-instances form; archived here for citation",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the joint attribution rule with both instances; the plan side recorded it as its section 2.5b, the reproducible-criterion proposal as its section 2.8, and the reviewer's pre-change citation count as its section 2.9",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "attributionRule": RULE,
         "independentConvergence": "the plan side's 23:17:53 reading of my ledger (21 entries / 75,150 B / 7eef4f1f...) matched my own measurement at that time - two parties, same live file, same reading",
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["attributionRule"] = RULE
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
