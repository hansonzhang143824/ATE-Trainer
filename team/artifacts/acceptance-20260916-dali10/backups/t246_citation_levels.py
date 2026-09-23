# -*- coding: utf-8 -*-
"""Adopt the three-level citation-stability scheme, version the name table, and state the rename protocol it requires."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

LEVELS = {
    "name": "citation stability levels (named by schematic-expert; my practice was its L2)",
    "levels": {
        "L0": "write the value from memory or by relaying it - weakest; this run hit it repeatedly",
        "L1": "value PLUS its moment - resists drift, but still binds a number that will change (the (A)/(B) normative form)",
        "L2": "cite only the FIELD NAME or path; take the value at use time - strongest available, and what I adopted",
    },
    "precondition": ("L2 has a precondition: the field name itself must be stable. The rename mirrorSize -> mirrorSizeAtMirrorTime shows names do change, and at the moment of a rename an L2 citation degrades into a DANGLING LOCATOR "
                     "(the peer's citation of mirrorSize is that case)."),
    "enabler": "a maintained name table - my knownSpecsRegister - is what makes 'cite only the name' work at all",
    "requirements": ["the name table must itself carry a version",
                     "renames must be append-only: add the new name and annotate the old one (the same shape as the (a-prime) remediation)",
                     "a citing party must, in L2, also supply the table version or recomputed evidence that the field still exists - otherwise L2 fails silently"],
    "criterion": "citation stability cannot exceed the stability of the cited name - isomorphic to 'a proof inherits its inputs' provenance' and 'a rule inherits its examples' defects'",
    "implementedHere": {"knownSpecsRegister.version": "added", "renameProtocol": "stated", "recomputeEvidence": "this file is read by path and any field's presence can be recomputed"},
}
doc["citationStabilityLevels"] = LEVELS

reg = doc.get("knownSpecsRegister") or {}
reg["version"] = 1
reg["renameProtocol"] = ("Renaming a field is append-only: add the new name and annotate the old one (see fieldNameCanonicalisation for the worked case knownSpecsRegister/specRegister). "
                         "An L2 citation of a name is only as stable as this table's version, so a citing party should also recompute that the field exists.")
doc["knownSpecsRegister"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("knownSpecsRegister.version:", reg.get("version"))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the three-level citation-stability scheme (L0/L1/L2) with its precondition, and versioned the name table plus stated the rename protocol it requires",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "citationStabilityLevels": LEVELS,
         "nameTableVersioned": {"field": "knownSpecsRegister", "version": reg.get("version"), "renameProtocol": "append-only: add the new name, annotate the old"},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
