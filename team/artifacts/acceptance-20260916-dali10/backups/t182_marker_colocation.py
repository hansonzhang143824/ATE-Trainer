# -*- coding: utf-8 -*-
"""Verify schematic-expert's refinement: the marker is present twice, and the residual risk is co-location/visibility.
Adopt the marker-co-location rule and refine my supersession pointer file."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
raw = open(C, "rb").read()
d = json.loads(raw.decode("utf-8"))

blk = d["revision29Bindings"]["completenessUnderBothReadings"]
print("insertion order of keys in completenessUnderBothReadings:")
for i, k in enumerate(blk.keys()):
    print("   %d. %s" % (i + 1, k))
print("\nsorted order (what a sorting tool shows):")
for i, k in enumerate(sorted(blk.keys())):
    print("   %d. %s" % (i + 1, k))
print("\nmarkers present:")
print("   parent revision29Bindings.SUPERSEDED:", str(d["revision29Bindings"].get("SUPERSEDED"))[:120])
print("   same-object SUPERSEDED             :", str(blk.get("SUPERSEDED"))[:120])
print("   disposition (imperative)           :", str(blk.get("disposition"))[:120])

# does a deep-path citation see any marker? emulate: fetch the child only
child = blk["disposition"]
print("\ndeep-path fetch of the child returns a marker?:", ("SUPERSEDED" in child.upper() or "WITHDRAWN" in child.upper()))

RULE = {
    "name": "marker co-location rule (root B's precise mechanism; refinement raised by schematic-expert)",
    "statement": "A supersession marker operates only at the level it occupies; it does NOT propagate downward to child keys. Therefore an annotation must be co-located with the content it constrains, or written INSIDE that content.",
    "whyParentMarkersFail": ["in insertion order the reader reaches the imperative (disposition) before the sibling marker (SUPERSEDED), which sits near the end of the same object",
                             "a tool that sorts keys shows SUPERSEDED (uppercase) first, so the risk depends on display order",
                             "a deep-path citation of the child alone (revision29Bindings.completenessUnderBothReadings.disposition) sees no parent marker at all"],
    "measured": {"insertionOrder": list(blk.keys()), "sortedOrder": sorted(blk.keys()),
                 "markersPresent": {"parent_revision29Bindings.SUPERSEDED": bool(d["revision29Bindings"].get("SUPERSEDED")),
                                    "sameObject_SUPERSEDED": bool(blk.get("SUPERSEDED"))},
                 "childUnderDeepPathCarriesMarker": ("SUPERSEDED" in child.upper())},
    "correctionOfMyEarlierCharacterisation": ("I had described this as an 'imperative residue' without noting that the block ALREADY carries two explicit SUPERSEDED markers. The accurate description is: it is labelled (twice), but the label is NOT co-located with the imperative, "
                                              "so it fails under insertion-order reading and under deep-path citation. Root B's mechanism is therefore co-location/visibility, not absence of labelling."),
    "minimalRemedies": ["(a) prefix the imperative itself: '[SUPERSEDED - history only] add K48/K76 and RETAIN K109/K110 this batch; ...'",
                        "(b) rename the key to disposition_superseded",
                        "(c) state both in one value: 'RETIRED: RETAIN K109/K110 (old) / OPERATIVE: REMOVE K109/K110 (t53)'"],
    "criterion": "the marker must sit with what it constrains, or inside it; at the parent alone, or at the end of the same object, it fails under some reading",
    "note": "these remedies do NOT delete history - the R1 convention (never delete the original) still applies",
    "owner": "the contract is the captain's, so the choice belongs to the captain; my side records the criterion and the options",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted schematic-expert's refinement of root B (marker co-location) and corrected my own earlier characterisation of the residue",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "markerCoLocationRule": RULE,
         "artifacts": {"setup-contract.json": {"path": C.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

# refine my supersession pointer file: a parent marker does not protect a child key
PTR = os.path.join(A, "gate-logs-t28", "supersession-pointers.json")
doc = json.load(open(PTR, encoding="utf-8"))
doc["entries"].append({
    "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": "refinement: a parent-level SUPERSEDED marker does NOT protect a child key from a deep-path reader",
    "pointers": [{
        "artifact": C.replace("\\", "/"),
        "artifactSha256AtRecording": hashlib.sha256(raw).hexdigest(),
        "artifactRevisionAtRecording": d.get("revision"),
        "paths": ["revision29Bindings.completenessUnderBothReadings.disposition",
                  "revision29Bindings.completenessUnderBothReadings.ruling",
                  "revision29Bindings.completenessUnderBothReadings.why_the_union_and_not_either_single_form.union_form"],
        "measuredFacts": {"markersPresent": "the block carries two explicit SUPERSEDED markers (parent revision29Bindings.SUPERSEDED and the sibling completenessUnderBothReadings.SUPERSEDED)",
                          "insertionOrder": list(blk.keys()),
                          "risk": "the imperative (disposition) is reached BEFORE the sibling marker in insertion order; a sorting tool shows SUPERSEDED first; and a deep-path citation of the child alone sees no marker at all",
                          "childCarriesMarker": ("SUPERSEDED" in child.upper())},
        "criterion": "an annotation must be co-located with the content it constrains, or written inside it - a marker at the parent does not travel to the child",
        "optionsForTheOwner": RULE["minimalRemedies"],
        "gateImpact": "none - the gate reads only aliasResolution[*].resolution.closedRelayNumbers = [48,60,61,76]",
    }],
})
json.dump(doc, open(PTR, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pb = open(PTR, "rb").read()
print("pointer file:", len(pb), "B /", hashlib.sha256(pb).hexdigest())
