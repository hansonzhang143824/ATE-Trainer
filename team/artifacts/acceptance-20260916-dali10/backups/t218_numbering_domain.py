# -*- coding: utf-8 -*-
"""One write: extend fieldAddressingRule with the numbering-domain clause, and sharpen reproducibleCriterion with the two-part test."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

fa = doc.get("fieldAddressingRule") or ""
if isinstance(fa, str):
    fa = {"statement": fa}
fa["statement"] = fanew = ("Address fields BY NAME (alias name, key name), never by list position: a position is an assumption about ordering, not an identity. "
                           "Instance: I read aliasResolution[1] expecting bst2sw and got sw2pgnd; the correct by-name value is [48,60,61,76].")
fa["numberingDomainClause"] = ("When a sequence must be addressed positionally, declare WHICH numbering system is in use. An artefact can carry both a 0-based array index and a 1-based business ordinal (or a stored snapshotIndex), and both are commonly written 'entry[N]'. "
                               "Instance: my ledger's entries[25] has snapshotIndex 26, so 'entry[26]' denotes different objects under the two systems - rule-reviewer read the entry with snapshotIndex 27 when using index 26. "
                               "Criterion (raised by rule-reviewer): 'entry[N]' without a declared numbering is an undeclared unit/domain, the same family as a count without its domain.")
fa["threeLayersAffectReading"] = ["field name (chainManifest sits at entry level while entryCanonicalSha256 sits under ledgerSelfProof)",
                                  "nesting level (the same field at a different depth is a different read)",
                                  "numbering system (0-based index versus 1-based ordinal/snapshotIndex)"]
fa["peerSelfCorrection"] = "rule-reviewer logged this as its ninth self-correction (it also read entryCanonicalSha256 at the top level, a nesting-level slip)"
doc["fieldAddressingRule"] = fa

rc = doc.get("reproducibleCriterion") or {}
rc["twoPartTest"] = ("'Reproducible' means BOTH (a) independent of the working directory, and (b) the expected output asserts only invariants - snapshot values may be printed but must be labelled as recomputed, not as assertions. "
                     "Missing (a), the command fails elsewhere; missing (b), it misreports as soon as a snapshot value expires. Raised by rule-reviewer, who re-ran my corrected command successfully from a temporary directory.")
doc["reproducibleCriterion"] = rc
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "extended fieldAddressingRule with the numbering-domain clause and sharpened reproducibleCriterion with the two-part test (both raised by rule-reviewer)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "numberingDomainClause": fa["numberingDomainClause"],
         "reproducibleTwoPartTest": rc["twoPartTest"],
         "artifactReadPathVerifiedByPeer": "entries[25].chainManifest (25 frozen entries) with entries[25].snapshotIndex = 26 and entryCanonicalSha256 under entries[25].ledgerSelfProof",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
