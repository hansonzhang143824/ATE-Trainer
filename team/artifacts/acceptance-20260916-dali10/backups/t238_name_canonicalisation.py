# -*- coding: utf-8 -*-
"""Fix a field-name inconsistency between my two carriers, exposed by the reviewer's field search."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

doc["fieldNameCanonicalisation"] = {
    "statement": ("One thing must have one name across my carriers. A field-name difference between carriers is the same hazard as two wordings of one rule: a reader searching one name concludes absence in the other carrier."),
    "mapping": {"knownSpecsRegister": "canonical name; used at the top level of this anchors file",
                "specRegister": "the SAME content under a different name inside the ledger entry entries[60] - a name mismatch on my side, recorded rather than rewritten (entries are immutable)"},
    "instance": ("rule-reviewer searched for `knownSpecsRegister` inside ledger entries and found nothing; a deep path search located the content at entries[60].specRegister. Their search domain was 'entry top-level keys', and they correctly declined to conclude absence - "
                 "the mismatch was mine, not a gap in their view."),
    "rule": "future writes use the canonical name; where an older entry carries the other name, the mapping is stated here instead of rewriting history",
    "alsoNoted": "structuralVerificationRule.identityAddendum exists only in this anchors file by design (it is a rule field), which matches the reviewer's reading",
}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "tick",
         "reason": "answers the reviewer's nested-path request and records a field-name mismatch between my own carriers (knownSpecsRegister vs specRegister)",
         "artifactsAbsent": True,
         "artifactsAbsentReason": "no artefact value set is recorded here; this entry maps two field names and answers a path query",
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "pathAnswers": {
             "anchorsFile": {"structuralVerificationRule.identityAddendum": True, "prohibitedInferenceConvention": True, "knownSpecsRegister": True},
             "ledger": {"entries[60].prohibitedInferenceConvention": True, "entries[60].specRegister": "same content as the anchors file's knownSpecsRegister"},
             "identityAddendumInLedger": False,
             "conclusion": "the reviewer's reading was right for identityAddendum (anchors-only); for knownSpecsRegister the content IS in the ledger, under the name specRegister - my naming mismatch, not a gap in their view",
         },
         "fieldNameRule": "one thing, one name across carriers; state a mapping where an immutable older entry uses another name",
         }
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
