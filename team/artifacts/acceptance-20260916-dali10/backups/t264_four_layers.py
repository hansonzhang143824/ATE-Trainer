# -*- coding: utf-8 -*-
"""Fold in the reviewer's four-layer synthesis, and resolve a labelling inconsistency in my own rule (three layers named, four covered)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

fa = doc.get("fieldAddressingRule") or {}
fa["fourLayerSummary"] = {
    "layers": {
        "1_fieldName": "which NAME - chainManifest versus ledgerSelfProof.entryCanonicalSha256",
        "2_nestingLevel": "from which LAYER - the same field at top level or nested is a different read",
        "3_numberingSystem": "under which NUMBERING - 0-based array index versus 1-based ordinal/snapshotIndex",
        "4_carrierStability": "which LOCATING PREDICATE - on a live append-only file locate by field, on a static file positional reads are admissible",
    },
    "whyItIsNowComplete": "any one of the four missing can produce a SILENT misread, so 'address by name' alone is not enough",
    "criterion": "a record's identity must be expressed as a CONTENT PREDICATE (which field/key, under which numbering, at which level), never as a position",
    "raisedBy": "rule-reviewer, who counted the layers and observed that my rule covers four while only three are named in threeLayersAffectReading",
    "labellingCorrection": ("My own file named the triple `threeLayersAffectReading` (name, level, numbering) while the rule as a whole covers FOUR layers, since carrier stability lives in `liveFileClause`. "
                            "The label is a count without its domain - the very family this run keeps repairing - so the four-layer statement is recorded here and the triple keeps its original name to avoid rewriting history."),
}
doc["fieldAddressingRule"] = fa
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "folded in the reviewer's four-layer synthesis and recorded a labelling correction in my own rule (three named, four covered)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "fourLayerSummary": fa["fourLayerSummary"],
         "myLabellingCorrection": "threeLayersAffectReading names three of the four layers, because carrier stability lives in liveFileClause; the label is a count without its domain",
         "peerReproducedMyTrap": "entries[30].snapshotIndex = 31 - reading by position 30 returns a different entry, so the reviewer reproduced the trap independently",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
