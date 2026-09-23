# -*- coding: utf-8 -*-
"""R1 correction: my recorded rationale for the projectionSpec v2 bump was wrong; the owner's correction is now the three-party position."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")

CORRECTION = {
    "whatIRecorded": ("In my ledger entry about reproducing the body hash, and in the earlier notes on that thread, I recorded the reason for the projectionSpec bump as: 'their v1 exclusion list was incomplete (it did not exclude the receipts field), "
                      "which is why the earlier recorded value could not be reproduced'."),
    "whatIsCorrect": ("The owner corrected this: `receipts` is a field of the RECEIPT-HISTORY file, not of the report body, so excluding it is PREVENTIVE and a no-op today; and v1 was measured stable across seconds, so the 'unstable exclusion list' rationale fails. "
                      "The REAL reason for v2 is that v1 declared only its exclusions and never its serialization or encoding, so a third party could not reproduce the value even from identical bytes."),
    "whyMyVersionWasWrong": "I inferred a cause from the fact that my own five-convention attempt failed - but the failure was caused by the undeclared serialization, which is exactly the v2 fix; the exclusion list was a separate, innocent detail.",
    "whowithdrew": "the owner withdrew its own earlier trigger rationale and registered it as §廿一; rule-reviewer independently measured that the report body has no `receipts` key and demanded the predicate and its nature be declared",
    "threePartyPosition": "the `receipts` exclusion is defensive and pre-justified, currently a no-op; the genuine reason for the v2 bump is 'adding serialization/encoding/definition'",
    "nature": "this is a correction of a RATIONALE, not of a value: the body hash 9804fbe2... and its reproduction are unaffected",
}
doc = json.load(open(ap, encoding="utf-8"))
doc["projectionSpecRationaleCorrection"] = CORRECTION
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "tick",
         "reason": "R1 correction of a rationale I had recorded about the projectionSpec v2 bump, after the owner's correction and the reviewer's independent measurement",
         "artifactsAbsent": True,
         "artifactsAbsentReason": "no artefact value set is recorded here; this entry corrects a stated RATIONALE - the body hash and its reproduction are unaffected",
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "rationaleCorrection": CORRECTION,
         "note": "a value can be right while the story told about it is wrong - this entry repairs the story, and it is itself a tick because it carries no value set",
         }
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
