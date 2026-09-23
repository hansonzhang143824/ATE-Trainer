# -*- coding: utf-8 -*-
"""Correct the residue count to THREE children (ruling, disposition, union_form) in the pointer file, t34 L47 and the ledger."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
CONTRACT = os.path.join(A, "setup-contract.json")
raw = open(CONTRACT, "rb").read(); d = json.loads(raw.decode("utf-8"))
blk = d["revision29Bindings"]["completenessUnderBothReadings"]
CHILDREN = {
    "revision29Bindings.completenessUnderBothReadings.ruling": blk.get("ruling"),
    "revision29Bindings.completenessUnderBothReadings.disposition": blk.get("disposition"),
    "revision29Bindings.completenessUnderBothReadings.why_the_union_and_not_either_single_form.union_form": blk["why_the_union_and_not_either_single_form"]["union_form"],
}
print("residue children (all three):")
for k, v in CHILDREN.items():
    print("  -", k, "=>", str(v)[:120])

PTR = os.path.join(A, "gate-logs-t28", "supersession-pointers.json")
doc = json.load(open(PTR, encoding="utf-8"))
doc["entries"].append({
    "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": "correction: the residue inside the superseded parent block is THREE children, not two (the earlier entry named ruling and union_form; the recount also exposes disposition, which is the most consequential because it is imperative)",
    "pointers": [{
        "artifact": CONTRACT.replace("\\", "/"),
        "artifactSha256AtRecording": hashlib.sha256(raw).hexdigest(),
        "artifactRevisionAtRecording": d.get("revision"),
        "supersededPaths": list(CHILDREN.keys()),
        "values": CHILDREN,
        "coveredBy": "the parent block's SUPERSEDED key plus the captain's final disposition (add K48/K76, REMOVE K109/K110, single channel-5 route)",
        "note": ("'disposition' still reads 'add K48/K76 and RETAIN K109/K110 this batch; removal ... stays scheduled for the later minimal cleanup revision' - an imperative sentence that contradicts the final ruling. It is covered by the parent marker and read by no gate, "
                 "but a reader opening that field alone would be misled, so it is named here explicitly."),
        "gateImpact": "none - the gate reads only aliasResolution[*].resolution.closedRelayNumbers = [48,60,61,76]",
    }],
})
json.dump(doc, open(PTR, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pb = open(PTR, "rb").read()
print("\npointer file:", len(pb), "B /", hashlib.sha256(pb).hexdigest())

f = os.path.join(A, "acceptance-report.json")
rep = json.load(open(f, encoding="utf-8"))
for i, x in enumerate(rep["limitations"]):
    if x.startswith("L47 "):
        rep["limitations"][i] = x.replace(
            "TWO residue children inside the superseded parent block revision29Bindings.completenessUnderBothReadings: its 'ruling' field ('The batch keeps the UNION ...') and the nested why_the_union_and_not_either_single_form.union_form.",
            "THREE residue children inside the superseded parent block revision29Bindings.completenessUnderBothReadings: 'ruling' ('The batch keeps the UNION ...'), 'disposition' ('add K48/K76 and RETAIN K109/K110 this batch ...' - imperative and the most consequential), and the nested why_the_union_and_not_either_single_form.union_form."
        ).replace("TWO residue children", "THREE residue children")
json.dump(rep, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
print("L47 says THREE:", "THREE residue children" in json.dumps(rep, ensure_ascii=False))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
e = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
     "reason": "residue count corrected to THREE children (ruling, disposition, union_form); 'disposition' is imperative and contradicts the final ruling",
     "contractRevision": d.get("revision"),
     "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
     "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
     "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
     "residueFinal": {"parent": "revision29Bindings.completenessUnderBothReadings", "children": list(CHILDREN.keys()), "values": CHILDREN,
                      "classification": {"legitimateUnionUses": 8, "alreadyMarkedSuperseded": 2, "residue": 3, "total": 13},
                      "note": "the 8 legitimate uses are pair-level unionRelays keys/values, the three-source expectation (no 110) and two cross-check sentences; pure counting cannot separate these from residue - only enumerating and classifying each occurrence can"},
     "artifacts": {"setup-contract.json": {"path": CONTRACT.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                   "gate-logs-t28/supersession-pointers.json": {"path": PTR.replace("\\", "/"), "sizeBytes": len(pb), "sha256": hashlib.sha256(pb).hexdigest()},
                   "acceptance-report.json": {"path": f.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}}}
e["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(e)}
lg["entries"].append(e)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
