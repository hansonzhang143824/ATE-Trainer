# -*- coding: utf-8 -*-
"""Fold in the owner's new appendPolicy observation: a deliberately non-growing log must declare its policy, or silence is ambiguous."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

rule = doc.get("identityBasedPruningRule") or {}
rule["declareThePolicyClause"] = {
    "observation": ("A log that deliberately does not grow is AMBIGUOUS unless the policy is written into the artefact: 'no new rows' can mean 'nothing ran' just as easily as 'nothing changed'. "
                    "The owner therefore added an `appendPolicy` field to the receipt declaring 'append only on identity change', after schematic-expert observed the policy had never been written down."),
    "instance": "gate-logs-t54/build-report.receipt.json carries appendPolicy; the receipts ledger showed zero growth in that round, which is now interpretable rather than suspicious",
    "asymmetryWorthNoting": ("This is the mirror image of the over-reporting counts this run fixed earlier: there, a growing count looked like more activity; here, a static count can look like inactivity. Both are cured the same way - by declaring the rule that governs the number, next to the number."),
    "criterion": "any log whose growth is conditional must declare the condition in the artefact itself, so that its silence is decidable",
    "raisedBy": "schematic-expert observed the missing declaration; the owner implemented it",
}
doc["identityBasedPruningRule"] = rule
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "folded the declare-the-policy clause into identityBasedPruningRule after the owner added appendPolicy to the receipt",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "declareThePolicyClause": rule["declareThePolicyClause"],
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
