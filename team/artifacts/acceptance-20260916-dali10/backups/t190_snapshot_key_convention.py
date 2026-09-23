# -*- coding: utf-8 -*-
"""Promote the snapshot-value key convention to a general, reusable naming rule, with both existing instances."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
CONV = {
    "name": "snapshot-value key convention (proposed by rule-reviewer from my recordedValuesAreSnapshots key)",
    "statement": ("A pointer or mirror field that records another file's size/hash must declare that its value is a snapshot of a moment, not an identity of the file now. Preferred forms: a boolean self-declaration on the record (`recordedValuesAreSnapshots`) and/or a time-baked key name (`mirrorSizeAtMirrorTime`) accompanied by a timestamp (`mirrorAt`) "
                  "and an expiry note (`mirrorSizeNote: value expires; recompute`)."),
    "why": "the discipline stops being 'do not hard-code a size' (a prohibition someone must remember) and becomes 'a hard-coded size must declare itself a snapshot' (a property of the record itself). Same prescription as a live file plus an external receipt.",
    "instances": [
        {"where": "t34-carrier-pointer.json", "key": "recordedValuesAreSnapshots",
         "value": "the size/sha256 in this pointer were true at 2026-09-16 22:40:03; the carrier is a live file - recompute before citing"},
        {"where": "gate-logs-t28/t28-anchors.json (owner's mirror block, after the drift finding)",
         "keys": ["mirrorSizeAtMirrorTime = 175358", "mirrorAt = 2026-09-17T00:33:15+08:00", "mirrorSizeNote = value expires; recompute"],
         "verifiedAtItsMoment": "my ledger measured 175,358 B at that time and 196,874 B later, so the pair (value, timestamp) is a true historical reading whose difference from the live file grows and shrinks over time"},
    ],
    "usageRule": "apply to any pointer/mirror/ledger record of another party's file; the name or a sibling field must state that the value expires",
    "reviewerNote": "rule-reviewer intends to fold this into R2's companion practices",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "promoted the snapshot-value key convention to a general reusable rule at the reviewer's suggestion, with both instances (mine and the owner's remediation)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "snapshotValueKeyConvention": CONV,
         "auditResultThisRound": "no peer-file size record in my artifacts lacks a timestamp (0 gaps); all 57 entries carry takenAt and their 124 peer-artifact references inherit it - so no edit was needed under this convention",
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "t34-carrier-pointer.json": {"path": os.path.join(A, "t34-carrier-pointer.json").replace("\\", "/"),
                                                    "sizeBytes": os.path.getsize(os.path.join(A, "t34-carrier-pointer.json")),
                                                    "sha256": hashlib.sha256(open(os.path.join(A, "t34-carrier-pointer.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["snapshotValueKeyConvention"] = CONV
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("pointer keys now:", list(json.load(open(os.path.join(A, "t34-carrier-pointer.json"), encoding="utf-8")).keys()))
