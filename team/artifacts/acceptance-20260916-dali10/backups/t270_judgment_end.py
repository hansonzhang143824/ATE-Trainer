# -*- coding: utf-8 -*-
"""Extend valueFrameCriterion with a third end: judgments expire with their premises (the reviewer's 15th self-correction)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

vf = doc.get("valueFrameCriterion") or {}
vf["judgmentEnd"] = {
    "addition": ("The criterion had a recording end and a comparison end. rule-reviewer's fifteenth self-correction adds a THIRD: a JUDGMENT must carry the state under which it was made. "
                 "A judgment such as 'this is not a current defect' or 'no hash is required' is only valid while its premise holds; once the state changes, the judgment expires and must be withdrawn or updated."),
    "instance": ("rule-reviewer had judged the mirror record's option (c-prime) 'not a current defect, only needs its purpose declared'. The owner then ADDED the content hash, so the premise ('no content hash exists') disappeared and the judgment expired - hence their withdrawal, logged as their fifteenth self-correction."),
    "criterion": "the validity period of 'X is not necessary' equals the validity period of the premise 'X has not been provided'",
    "sameRootAs": "a value must carry its moment - here a JUDGMENT must carry its premise's moment, otherwise the judgment silently outlives the state it was about",
    "whyItIsEasyToMiss": "a withdrawn value looks stale; a withdrawn JUDGMENT keeps reading as a present assessment, because nothing in its wording says when it was formed",
}
vf["threeEndsSummary"] = "recording end (declare a value's moment) | comparison end (prove both readings saw the same object) | judgment end (carry the state under which the judgment was made)"
doc["valueFrameCriterion"] = vf
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "extended the value-frame criterion with the judgment end, after the reviewer withdrew its 'not a current defect' judgment because the owner supplied the missing element",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "judgmentEnd": vf["judgmentEnd"],
         "threeEnds": vf["threeEndsSummary"],
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
