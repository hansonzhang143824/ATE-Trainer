# -*- coding: utf-8 -*-
"""Record the definition-versioning rule (the regress terminator) and verify the owner's meta definition file."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
meta_p = os.path.join(A, "gate-logs-t54", "build-report.receipts.meta.json")
meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
print("meta definition file present:", os.path.exists(meta_p))
print("   keys:", sorted(meta.keys()) if meta else "n/a")
print("   metaVersion:", meta.get("metaVersion"), "| metaIdentity present:", bool(meta.get("metaIdentity")))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
RULE = {
    "name": "definition versioning (the regress terminator; raised by schematic-expert, implemented by the owner)",
    "statement": ("If identity is judged by a projection, and the projection is defined by a definition file, then THAT definition can drift too. So the definition carries its own version (metaVersion) and its own identity (metaIdentity), and definitions are cited BY VERSION. "
                  "Version pinning is what terminates the regress: value -> projection -> projection definition -> definition version, where the chain stops."),
    "instance": "gate-logs-t54/build-report.receipts.meta.json carries metaVersion=1 plus metaIdentity; the receipt's projectionSpec is cited with its version",
    "whyItBelongsHere": "it is the outermost layer of the same family as snapshotValueKeyConvention (a recorded value must declare its moment) and citationStabilityLevels (L2 works only while the cited name is stable): each layer names the thing that could otherwise drift silently",
    "recursionTermination": "without a version on the definition, every layer can be redefined and no citation is ever pinned; with it, the chain has a fixed point",
}
doc["definitionVersioningRule"] = RULE
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "recorded the definition-versioning rule after the owner added a versioned definition file; verified its fields",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "definitionVersioningRule": RULE,
         "metaFileVerified": {"present": os.path.exists(meta_p), "keys": sorted(meta.keys()) if meta else [], "metaVersion": meta.get("metaVersion")},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "gate-logs-t54/build-report.receipts.meta.json": {"path": meta_p.replace("\\", "/"), "sizeBytes": os.path.getsize(meta_p),
                                                                         "sha256": hashlib.sha256(open(meta_p, "rb").read()).hexdigest()} if os.path.exists(meta_p) else None}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
