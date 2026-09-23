# -*- coding: utf-8 -*-
"""Maintain the peer rule registry: add rules newly named by the plan side (names only, no paraphrase)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

reg = doc.get("peerRuleRegistry") or {}
added = [
    "the two-registers division: prose carries the reasoning, named fields carry citable identity",
    "a change in citation form is the only evidence that a rule is in effect",
    "a suggestion superseded by a stronger implementation should be withdrawn, not defended",
]
for n in added:
    if n not in reg.get("names", []):
        reg.setdefault("names", []).append(n)
reg["maintenanceNote"] = ("Newly named peer rules are appended here BY NAME ONLY, so this pointer does not silently go stale. A stale pointer is a defect of exactly the kind this run keeps repairing; no paraphrase is ever stored, because the carrier remains the peer's note.")
reg["withdrawnSuggestion"] = ("The peer withdrew its suggestion that I also hold the two-registers rule, on the ground that requesting the copy is itself what produces the drift the principle guards against. Recorded so the decision is not re-litigated.")
doc["peerRuleRegistry"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("peer rule names now:", len(reg["names"]))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "maintained the peer rule registry with three newly named peer rules (names only) and recorded the peer's withdrawn suggestion",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "peerRuleRegistryMaintenance": {"addedNames": added, "totalNames": len(reg["names"]),
                                         "whyMaintained": "a stale pointer is a defect of the same kind this run repairs; the carrier stays the peer's note, so only names are stored"},
         "peerWithdrewSuggestion": "the peer withdrew its suggestion that I hold the two-registers rule as well",
         "peerVerificationOfMyRegister": "the peer verified 16 named fields by name, and noted that the reasoning lives inside the fields - so 'names carry identity, prose carries reasoning' is my existing structure, not a proposal",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
