# -*- coding: utf-8 -*-
"""Adopt and evidence t4's tightening: identify tick entries by kind AND by the explicit absence declaration."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")

pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
s = lg.setdefault("schema", {})
note = s.setdefault("countAmplificationNote", {})
note["tickIdentificationRule"] = {
    "rule": "an entry is a tick if and only if BOTH (a) its top-level `kind` is exactly 'tick' AND (b) it carries the explicit absence declaration `artifactsAbsent`",
    "raisedBy": "test-strategy-architect observed that the difference between full and tick is not 'fewer fields' but an EXPLICIT DECLARATION of absence",
    "generalForm": "an explicit declaration beats an inferred absence - the same family as a declared decision rule, a declared moment, and an explicitly named token",
    "measuredCrossTab": {"tickWithArtifactsAbsent": "5 / 5", "fullWithArtifactsAbsent": "0 / 83", "missingKindWithArtifactsAbsent": "0 / 6",
                         "otherKindValues": "none - the distribution is closed",
                         "table": "{(None, False): 6, (full, False): 83, (tick, True): 5}"},
    "limitingObservation": ("On all 94 entries observed the two conditions COINCIDE exactly, so they corroborate each other; but no entry has yet been seen with one condition holding and not the other, so their mutual independence has not been stressed. "
                            "A future disagreement would be a defect signal rather than a definitional puzzle."),
    "whyTighten": "identifying by shape means a reader does not depend on one label being right; two independent indicators must agree",
}
note["selfDemonstration"] = ("The rule demonstrates itself: after the write that recorded it, the tick count rose again (3 -> 4 -> 5) because correction-type entries are themselves ticks. "
                             "This is not a constructed example but the archive's ordinary operation - noted by test-strategy-architect as the cleanest confirmation of the self-referential mechanism.")
lg["schema"] = s

def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "tick",
         "reason": "adopted the two-condition tick identification rule and evidenced it with a measured cross-tab",
         "artifactsAbsent": True,
         "artifactsAbsentReason": "no artefact value set is recorded here; this entry tightens a schema-level counting definition and reports a cross-tabulation",
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "tickIdentificationRule": note["tickIdentificationRule"],
         "note": "this entry is itself a tick with the absence declaration, so it satisfies both conditions it defines"}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()

# record the same rule in the anchors file for by-name citation
ad = json.load(open(ap, encoding="utf-8"))
ad["tickIdentificationRule"] = note["tickIdentificationRule"]
ad["tickIdentificationRule"]["selfDemonstration"] = note["selfDemonstration"]
ad["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(ad, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
