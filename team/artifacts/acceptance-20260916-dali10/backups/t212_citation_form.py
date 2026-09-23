# -*- coding: utf-8 -*-
"""Adopt t4's generalisation: cite the FIELD NAME (the invariant), never a live container's measurement."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

RULE = {
    "name": "cite the field name, not the container's measurement (proposed by test-strategy-architect from the live-file experience)",
    "statement": ("Once a rule or artefact has a stable name, cite it BY NAME or recompute it; never cite a live container's size, entry count or hash as part of the citation. "
                  "The field name survives every write; a measurement is stale by construction."),
    "consequenceForWayfinding": "wayfinding information is precisely the naming of invariant things - field name, owner, path. Measurements belong to the READER's recomputation, not to the citation.",
    "tiesTo": ["scopeRule", "snapshotValueKeyConvention", "structuralVerificationRule"],
    "evidenceFromThisRun": "two citations of my ledger and anchors file were overtaken within minutes (the ledger gained ten entries and ~33 KB in about two minutes; an earlier case gained sixteen entries across three messages)",
    "practice": "in messages: cite rule fields by name (e.g. 'the ledger's schema.peerReceiptCiteRule'), and when a value is needed, label it as recomputed now with its time rather than carrying it forward",
}
doc["citationFormRule"] = RULE

reg = doc.get("evidenceStrengthRegister") or {}
members = reg.get("members") or []
if not any(isinstance(m, dict) and m.get("rule") == "citationFormRule" for m in members):
    members.append({"rule": "citationFormRule", "oneLiner": "cite the stable field name (or recompute); never carry a live container's measurement", "locator": "this file: citationFormRule"})
reg["members"] = members
reg["reviewerAdoptedAddition"] = "membership extended with citationFormRule, proposed by test-strategy-architect"
doc["evidenceStrengthRegister"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("register members:", [m.get("rule") for m in members])

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the citation-form rule (cite the field name, not a live container's measurement) and added it to the evidence-strength register",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "citationFormRule": RULE,
         "namedFieldsVerifiedByPeer": "test-strategy-architect verified that my named fields exist and are citable: reproducibleCriterion (ledger + anchors), schema.peerReceiptCiteRule, byteCopySnapshot, scopeRule",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
