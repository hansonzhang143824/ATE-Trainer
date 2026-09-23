# -*- coding: utf-8 -*-
"""One write, two pending items: (1) fold the reviewer's 'identity is settled by reading the object' into structuralVerificationRule;
(2) enshrine the 'prohibited inference' convention (every result carries what it must NOT be cited as)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

# (1) fold the pending refinement in
svr = doc.get("structuralVerificationRule") or {}
svr["identityAddendum"] = ("Identity claims are settled by READING THE OBJECT, not by comparing metadata about it. Two readings of a size are not evidence that they describe the same object; reading the content is itself the mechanised form of the discipline "
                           "'do not assert identity without proof' (raised by rule-reviewer after committing that error twice in this run: 874/11854 and 824/2388, both later withdrawn).")
doc["structuralVerificationRule"] = svr

# (2) prohibited-inference convention
PI = {
    "name": "prohibited-inference convention (every result carries what it must NOT be cited as)",
    "statement": "Any experimental result or measurement conclusion states, in the artefact itself, which inferences it does NOT support. Evidence is granted; over-reach is forbidden in writing.",
    "why": "readers of a later round see only the conclusion, so the boundary must travel with it - the same reason a citation carries its provenance flag",
    "instances": [
        {"where": "my controlExperimentSpec.prohibitedInference",
         "text": "the union probe evidences category (ii) 'no loss of current content' only; it must never be cited as evidence of category (iii) recovery, because the earlier eight entries have no byte copy"},
        {"where": "rule-reviewer's review-side field mustNotBeCitedAs", "text": "the same shape on the review side - the two forms have converged"},
        {"where": "t34 L48 rev-32 caveat", "text": "log self-report plus interval compatibility; it must not be claimed that the gate's input was byte-proven to be rev 32"},
        {"where": "the three-way classification", "text": "'after == before' must not be read as 'still dropping' - the accurate reading is 'no longer losing, but not restoring'"},
    ],
    "unifiedForm": "result + what it evidences + what it must not be cited as",
    "reviewerNote": "raised for enshrinement by rule-reviewer; the review side already uses the same form under a different field name",
}
doc["prohibitedInferenceConvention"] = PI
doc["knownSpecsRegister"] = {
    "name": "numbered spec register (raised by rule-reviewer)",
    "statement": "Designs, experiments and specs are stored with an identifier so that later parties can cite 'spec item N' instead of restating the design; knowledge moves out of messages into citable artefacts.",
    "instances": ["controlExperimentSpec (my ledger entry[42] + this file)", "reproducibleCriterion", "snapshotValueKeyConvention", "certaintyTieringPattern"],
}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "one write covering two pending items: the identity addendum folded into structuralVerificationRule, and the prohibited-inference convention enshrined",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "prohibitedInferenceConvention": PI,
         "specRegister": doc["knownSpecsRegister"],
         "pendingItemClosed": "the refinement promised for structuralVerificationRule ('identity claims are settled by reading the object, not by comparing metadata about it') is now on file - it was folded into this write rather than triggering one of its own",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
