# -*- coding: utf-8 -*-
"""Precision fix requested by the reviewer: separate PROVEN (a collapse occurred) from APPROXIMATE (how many entries were lost). Also confirm the generator-version annotation location."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# find where the generator-version annotation lives
gen_entries = [e["snapshotIndex"] for e in lg["entries"] if "generatorVersionAnnotation" in e]
print("entries carrying generatorVersionAnnotation:", gen_entries)

PRECISION = {
    "proven": "a collapse occurred: the owner's own fix script (gate-logs-t54/t54_fix_preservation_union.py, 4,012 B / 915f989e8a3ca2998b27...) states in writing that preservedPeerNamespaces previously collapsed entries into one - this is a product-level admission, stronger than a message-level one",
    "approximate": "how many entries were lost: the owner wrote '6~8', an interval, because the exact count was never captured. So the MAGNITUDE is approximate and must not be quoted as exactly 8",
    "measured": "what the preserved namespace contains NOW: exactly 1 entry (sub-key 'acceptance-report.json'), measured independently by both sides on the shared file",
    "correctWording": "the owner's fix script reports that 6~8 entries were collapsed into 1; the exact count is not recoverable (never captured); the current content is 1 entry",
    "family": "same discipline as the rev-32 attribution caveat: an interval-compatible statement must not be presented as byte-level proof; keep the two levels separate",
}

entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "precision fix requested by the reviewer: separate 'a collapse happened (proven)' from 'how many were lost (approximate 6~8)'",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "namespaceLossPrecision": PRECISION,
    "generatorVersionAnnotationLocation": {"entries": gen_entries,
        "content": "BEFORE=1 was measured at 22:24:15; the union-accumulation fix script has mtime 22:22:38 and the generator 22:22:54, both predating that measurement, so BEFORE and AFTER were both taken on the FIXED generator - equality shows preservation of what exists, not restoration of what was lost"},
    "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

# anchors: make the two-level statement citable
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["namespaceLossPrecision"] = PRECISION["correctWording"]
doc["generatorVersionOfBeforeAfter"] = "measured on the FIXED generator: fix script mtime 22:22:38 and generator mtime 22:22:54 both predate the BEFORE measurement at 22:24:15"
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())
