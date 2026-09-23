# -*- coding: utf-8 -*-
"""Sharpen citationFormRule: the rule constrains what travels AS IDENTITY, not what is read as content."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

cf = doc.get("citationFormRule") or {}
cf["identifierVsReadingClause"] = {
    "correction": ("The rule does NOT mean 'never cite numbers'. It means: a CONTAINER's measurements (size, entry count, hash) must not travel as an IDENTITY, because they expire by construction; whereas the CONTENT of a carrier may still be stated by value, "
                   "because that is exactly what a reader opens the file to see."),
    "whatItConstrains": "what is used as an identifier",
    "whatItDoesNotConstrain": "what is used as reading material",
    "reconciles": "this is why the 'measured now' reading in my t34 L55 stays (it is labelled as a reading for that moment) while container sizes never travel inside a citation",
    "criterionWhenInDoubt": "ask whether the value is standing in for the object (then it must not be carried) or being shown as content (then it may be stated, with its moment)",
    "raisedBy": "test-strategy-architect as an operational completion of the rule",
}
cf["cleanestMeasurementOnTheTimingTopic"] = {
    "series": ["46 entries / 159,366 B", "56 / 192,597", "69 / 234,150", "72 / 244,558 (measured by the peer)"],
    "reading": "four readings of one container, each true at its own moment, of a container that is SUPPOSED to grow - so the evening's apparent disagreements were never about facts, only about moments",
    "note": "my own later measurement of the same file is a fifth point, which is the same statement again",
}
doc["citationFormRule"] = cf
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "sharpened citationFormRule with the identifier-versus-reading clause and recorded the four-point timing series as the topic's cleanest measurement",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "citationFormSharpened": cf["identifierVsReadingClause"],
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
