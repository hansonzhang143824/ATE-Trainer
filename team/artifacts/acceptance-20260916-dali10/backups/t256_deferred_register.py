# -*- coding: utf-8 -*-
"""Implement the reviewer's suggestion: register the items I have deferred, naming WHOSE carrier currently holds each one."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

REG = {
    "name": "deferred items register (raised by rule-reviewer: if a rule is temporarily carried elsewhere, say WHOSE carrier holds it)",
    "why": ("A deferral without a named carrier invites the failure where both sides assume the other has it. Naming the carrier makes the deferral auditable and is the same discipline as a citation carrying its provenance."),
    "items": [
        {"item": "wrongStringTaxonomy refinement - a classification claim must state the class scanned ('no runner executes it' is not 'no script mentions it')",
         "currentCarrier": "rule-reviewer's note", "foldIn": "beside wrongStringTaxonomy's decision rule at my next writes to this file"},
        {"item": "certaintyTieringPattern refinement - if a tier is empty, state explicitly that it is empty and why",
         "currentCarrier": "rule-reviewer's note", "foldIn": "beside the pattern's definition at my next write"},
        {"item": "snapshotValueKeyConvention worked pair - the same value unlabelled is a defect, labelled with a moment it is a record",
         "currentCarrier": "rule-reviewer's note", "foldIn": "beside snapshotValueKeyConvention at my next write"},
        {"item": "structuralVerificationRule instance - comparing two files by size can never conclude 'same', only 'looks the same' (equal-length edits are invisible)",
         "currentCarrier": "rule-reviewer's note", "foldIn": "beside identityAddendum at my next write"},
        {"item": "threeLayersAffectReading refinement - a structural read must also declare the LEVEL it read at",
         "currentCarrier": "test-strategy-architect's note", "foldIn": "beside threeLayersAffectReading at my next write"},
        {"item": "scopeRule instance pair - path-layer lapse (mine: a missing key returned a credible 0) and vocabulary-layer lapse (theirs: a keyword list lacking synonyms returned a credible False)",
         "currentCarrier": "rule-reviewer's note plus my reply", "foldIn": "into scopeRule.instances at my next write"},
        {"item": "generalisation that REQUESTS are also timing claims ('please update your registration' is a claim about the timing regime)",
         "currentCarrier": "test-strategy-architect's note", "foldIn": "beside citationFormRule at my next write"},
    ],
    "myRule": "no deferral without a named carrier; when folding an item in, state which carrier held it until then",
}
doc["deferredItemsRegister"] = REG
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest(), "| deferred items:", len(REG["items"]))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "implemented the reviewer's suggestion that a deferred rule names WHOSE carrier holds it; registered seven deferred items",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "deferredItemsRegister": REG,
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
