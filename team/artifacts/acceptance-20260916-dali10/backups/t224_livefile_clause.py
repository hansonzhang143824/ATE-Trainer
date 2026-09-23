# -*- coding: utf-8 -*-
"""Extend fieldAddressingRule with the live-file clause (search by field, never read by index on append-only files) and re-verify the chain by FIELD lookup."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

fa = doc.get("fieldAddressingRule") or {}
if isinstance(fa, str):
    fa = {"statement": fa}
fa["liveFileClause"] = ("On an append-only LIVE file, always locate records BY FIELD/KEY, never read them by index. 'The record I want' must be expressed as 'the record that contains field X', not as 'record N'. "
                        "Reason: an index is a POSITION and positions shift as entries are appended; a field is CONTENT and content does not shift. Reading by index on a live file means reading with an unstable predicate.")
fa["mechanisation"] = ("Because rule-reviewer hit this twice (entries[26]/entries[25] first, then entries[30]), and because it is silent and has an impact surface, it is mechanised rather than merely remembered: my verification scripts locate records by field or by the stored snapshotIndex, "
                       "never by array position.")
fa["peerEncounter"] = ("rule-reviewer's third instance: reading entries[30] returned False twice, nearly producing the false report 'premiseWithdrawn is not on file'; a field search located it at 0-based idx 29 / snapshotIndex 30. Two causes compounded: the off-by-one between 0-based index and 1-based snapshotIndex, and the ledger being appended between the two probes. "
                       "They logged it as their tenth self-correction.")
fa["samePrescription"] = "replace a position with a content identifier - the same fix as the numbering-system clause, the domain/unit rule and the 'do not cite line numbers as identity' rule"
doc["fieldAddressingRule"] = fa
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

# field-based re-verification of the chain (no index reads)
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

by_snapshot = {e.get("snapshotIndex"): e for e in lg["entries"] if isinstance(e, dict)}
manifest_holder = next((e for e in lg["entries"] if isinstance(e, dict) and isinstance(e.get("chainManifest"), dict)), None)
mismatch = []
if manifest_holder:
    for m in manifest_holder["chainManifest"]["entries"]:
        target = by_snapshot.get(m["snapshotIndex"])
        if target is None or canon(target) != m["entryCanonicalSha256"]:
            mismatch.append(m["snapshotIndex"])
print("field-based chain check: entries =", len(lg["entries"]),
      "| manifest holder snapshotIndex =", manifest_holder.get("snapshotIndex") if manifest_holder else None,
      "| frozen =", len(manifest_holder["chainManifest"]["entries"]) if manifest_holder else 0,
      "| mismatches =", mismatch or 0)

premise = next((e.get("snapshotIndex") for e in lg["entries"] if isinstance(e, dict) and e.get("premiseWithdrawn")), None)
print("field search for premiseWithdrawn -> snapshotIndex:", premise)
print("entry[5] (by field, snapshotIndex 5) carries premiseWithdrawn:", bool((by_snapshot.get(5) or {}).get("premiseWithdrawn")))

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "extended fieldAddressingRule with the live-file clause (search by field, never read by index on append-only files) at rule-reviewer's request, and re-verified the chain by field lookup",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(open(LOG, "rb").read()), "ledgerSha256BeforeThisWrite": hashlib.sha256(open(LOG, "rb").read()).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "liveFileClause": fa["liveFileClause"],
         "fieldBasedVerification": {"chainMismatches": mismatch or 0, "premiseWithdrawnAtSnapshotIndex": premise,
                                    "entry5Unchanged": not bool((by_snapshot.get(5) or {}).get("premiseWithdrawn")),
                                    "method": "records located by their snapshotIndex field, not by array position"},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
