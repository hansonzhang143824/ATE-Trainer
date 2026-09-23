# -*- coding: utf-8 -*-
"""The recount found a SECOND residue child (the parent block's 'ruling' field). Record both in the pointer file and correct t34 L47."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
CONTRACT = os.path.join(A, "setup-contract.json")
raw = open(CONTRACT, "rb").read(); d = json.loads(raw.decode("utf-8"))
blk = d["revision29Bindings"]["completenessUnderBothReadings"]
print("parent keys:", list(blk.keys()))
print("ruling:", str(blk.get("ruling"))[:180])
print("disposition:", str(blk.get("disposition"))[:180])
print("SUPERSEDED:", str(blk.get("SUPERSEDED"))[:160])

# append a second pointer entry covering both residue children
PTR = os.path.join(A, "gate-logs-t28", "supersession-pointers.json")
doc = json.load(open(PTR, encoding="utf-8"))
doc["entries"].append({
    "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": "second residue child found by the recount (enumerate-then-classify); record it so a reader opening either child alone is warned",
    "pointers": [{
        "artifact": CONTRACT.replace("\\", "/"),
        "artifactSha256AtRecording": hashlib.sha256(raw).hexdigest(),
        "artifactRevisionAtRecording": d.get("revision"),
        "supersededPaths": [
            "revision29Bindings.completenessUnderBothReadings.ruling",
            "revision29Bindings.completenessUnderBothReadings.why_the_union_and_not_either_single_form.union_form",
        ],
        "values": {"ruling": blk.get("ruling"), "union_form": blk["why_the_union_and_not_either_single_form"]["union_form"]},
        "coveredBy": "the parent block's SUPERSEDED key and the captain's disposition (add K48/K76, remove K109/K110, single channel-5 route)",
        "correctionOfMyOwnCount": "my earlier report said the contract had 12 'union' occurrences; a raw-text recount gives 13, and classifying all 13 showed that TWO children of this block still assert the union form - the 'union_form' sub-key I had named, and the block's own 'ruling' field.",
        "gateImpact": "none - the gate reads only aliasResolution[*].resolution.closedRelayNumbers = [48,60,61,76]",
    }],
})
json.dump(doc, open(PTR, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pb = open(PTR, "rb").read()
print("\npointer file:", len(pb), "B /", hashlib.sha256(pb).hexdigest())

# correct L47 in the carrier
f = os.path.join(A, "acceptance-report.json")
rep = json.load(open(f, encoding="utf-8"))
corr = (" CORRECTION AND EXTENSION (enumerate-then-classify, after test-strategy-architect challenged my count): my earlier figure of 12 'union' occurrences was WRONG - a raw-text recount gives 13; classifying all 13 gives "
        "8 legitimate uses (the pair-level unionRelays keys and values, the three-source expectation _t30ExpectationNote.expectedUnion/derivation which contains no 110, and two cross-check sentences), 2 already-marked-superseded strings, and TWO residue children inside the superseded parent block "
        "revision29Bindings.completenessUnderBothReadings: its 'ruling' field ('The batch keeps the UNION ...') and the nested why_the_union_and_not_either_single_form.union_form. Both are now named in the append-only record gate-logs-t28/supersession-pointers.json, "
        "which changes no contract byte and therefore invalidates no hash. Pure counting would have missed this second child; only enumerating and classifying each occurrence found it.")
for i, x in enumerate(rep["limitations"]):
    if x.startswith("L47 ") and "CORRECTION AND EXTENSION" not in x:
        rep["limitations"][i] = x + corr
json.dump(rep, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(rep["limitations"]))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
e = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
     "reason": "recount (13, not 12) found a SECOND residue child; recorded both in the supersession pointer file and corrected t34 L47",
     "contractRevision": d.get("revision"),
     "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
     "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
     "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
     "residue": {"parent": "revision29Bindings.completenessUnderBothReadings", "parentHasSupersededKey": "SUPERSEDED" in blk,
                 "residueChildren": ["ruling", "why_the_union_and_not_either_single_form.union_form"],
                 "countCorrection": {"myEarlierFigure": 12, "recountRawText": 13, "legitimateUses": 8, "alreadyMarkedSuperseded": 2, "residue": 2}},
     "artifacts": {"setup-contract.json": {"path": CONTRACT.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                   "gate-logs-t28/supersession-pointers.json": {"path": PTR.replace("\\", "/"), "sizeBytes": len(pb), "sha256": hashlib.sha256(pb).hexdigest()},
                   "acceptance-report.json": {"path": f.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}}}
e["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(e)}
lg["entries"].append(e)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
