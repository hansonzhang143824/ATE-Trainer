# -*- coding: utf-8 -*-
"""Enshrine the two-ended 'value frame' criterion (recording end + comparison end), promoted by rule-reviewer from my observation."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

CRIT = {
    "name": "value-frame criterion (my observation that the two disciplines are one coin; promoted to a named criterion by rule-reviewer)",
    "statement": ("Any reasoning that involves a value changing over time must declare BOTH ends: "
                  "(A) the RECORDING end - when recording another party's or a volatile value, declare that the value is a snapshot of a moment (timestamp + expiry declaration); "
                  "(B) the COMPARISON end - when comparing two readings, first establish that both saw the SAME OBJECT (identity evidence)."),
    "criterion": ("Missing (A) and the record is misread once it expires; missing (B) and two readings are mistaken for 'the evolution of one object'. Both are instances of a value lacking its frame, but in opposite directions: production side versus consumption side."),
    "why": "it joins the two disciplines already on file into one statement: snapshotValueKeyConvention (A) and structuralVerificationRule.identityAddendum (B)",
    "instances": {
        "peerOnA": "rule-reviewer cited the mirrorSize delta without declaring the moment (I had recorded the timestamp; the citation dropped it)",
        "peerOnB": "rule-reviewer treated 824 B and 2,388 B as one file's evolution; they are two different files at three time points",
        "mineOnB": "I compared two readings of the shared file and inferred a rev-28 attribution without identity evidence, and withdrew it after the owner's anchor",
        "note": "the same family has one lapse on each side of the coin, which is why the two-ended form is worth enshrining",
    },
    "reviewerProposal": "to be enlisted alongside R2",
}
doc["valueFrameCriterion"] = CRIT
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "enshrined the two-ended value-frame criterion (recording end + comparison end) at rule-reviewer's promotion request",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "valueFrameCriterion": CRIT,
         "namedFieldVerifiedByPeer": "snapshotValueKeyConvention was confirmed in place by rule-reviewer using a field search (idx 57 / snapshotIndex 58) with both instances present",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
