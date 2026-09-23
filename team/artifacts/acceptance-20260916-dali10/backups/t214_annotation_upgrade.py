# -*- coding: utf-8 -*-
"""Adopt schematic-expert's upgrade (a'): human-readable prefix PLUS a machine-consumable status field; extend the marker rule accordingly."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
raw = open(C, "rb").read()
d = json.loads(raw.decode("utf-8"))
blk = d["revision29Bindings"]["completenessUnderBothReadings"]
print("current keys:", list(blk.keys()))
print("disposition (head):", str(blk.get("disposition"))[:90])

UPGRADE = {
    "name": "annotation upgrade (a-prime) proposed by schematic-expert",
    "problem": "option (a) - a text prefix inside the value - is robust to key order, display order and deep-path reads, but a machine still has to parse prose to learn the state",
    "proposal": ("keep the human-readable prefix AND add a sibling machine-consumable key, e.g. "
                 "disposition = '[SUPERSEDED - history only] add K48/K76 and RETAIN K109/K110 this batch; ...' plus "
                 "dispositionStatus = {state: SUPERSEDED, operativeRule: 'REMOVE K109/K110 (t53)', note: 'retained as history only'}"),
    "benefits": ["a deep-path reader of the value carries the annotation with it",
                 "independent of key order and of sorted display",
                 "a program can consume the state without parsing prose",
                 "it only ADDS a key, so unlike renaming to disposition_superseded it breaks no existing deep-path reference"],
    "criterionExtended": "an annotation must be co-located with the content it constrains; state that must be machine-consumable must have its own field",
    "historyPreserved": "the original disposition wording is retained (with the prefix), so the R1 convention still holds",
    "reportedToCaptain": "the option set I already submitted listed (a)/(b)/(c)/status quo; this upgrade is offered as an amendment, since schematic-expert asked me to supplement rather than re-report",
}

PTR = os.path.join(A, "gate-logs-t28", "supersession-pointers.json")
doc = json.load(open(PTR, encoding="utf-8"))
doc["entries"].append({
    "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": "amendment to the remediation options: the (a) text prefix plus a machine-consumable status sibling key (schematic-expert's a-prime)",
    "pointers": [{
        "artifact": C.replace("\\", "/"),
        "artifactSha256AtRecording": hashlib.sha256(raw).hexdigest(),
        "artifactRevisionAtRecording": d.get("revision"),
        "supersededPaths": ["revision29Bindings.completenessUnderBothReadings.disposition",
                            "revision29Bindings.completenessUnderBothReadings.ruling",
                            "revision29Bindings.completenessUnderBothReadings.why_the_union_and_not_either_single_form.union_form"],
        "currentKeysOfTheBlock": list(blk.keys()),
        "remediationUpgrade": UPGRADE,
        "gateImpact": "none - the gate reads only aliasResolution[*].resolution.closedRelayNumbers = [48,60,61,76]",
    }],
})
json.dump(doc, open(PTR, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pb = open(PTR, "rb").read()
print("pointer file:", len(pb), "B /", hashlib.sha256(pb).hexdigest(), "| entries:", len(doc["entries"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
ad = json.load(open(ap, encoding="utf-8"))
mc = ad.get("markerCoLocationRule") or {}
mc["criterionExtended"] = UPGRADE["criterionExtended"]
mc["remediationUpgrade"] = "human-readable prefix inside the value + a sibling machine-consumable status key (a-prime); only adds a key, so no existing deep-path reference breaks"
ad["markerCoLocationRule"] = mc
sem = ad.get("staleTokenCriterion") or {}
sem["finerSubForm"] = ("token presence is not semantic reference: the same word can refer to a different object (in the instance, 'superseded' at character 224 of the disposition value refers to ANOTHER field being downgraded). "
                       "So the check must first classify WHOM the token refers to - same root as 'co-occurrence is not relationship' and 'the right domain is not the right formula'.")
ad["staleTokenCriterion"] = sem
ad["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(ad, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the annotation upgrade (a-prime) and recorded the finer sub-form of the stale-token criterion; amending the option set already submitted to the captain",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "annotationUpgrade": UPGRADE,
         "artifacts": {"gate-logs-t28/supersession-pointers.json": {"path": PTR.replace("\\", "/"), "sizeBytes": len(pb), "sha256": hashlib.sha256(pb).hexdigest()},
                       "gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "setup-contract.json": {"path": C.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
