# -*- coding: utf-8 -*-
"""Adopt test-strategy-architect's suggestion: make the 'peer-reported' annotation self-citing (a citation rule in the ledger schema)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

lg["schema"]["peerReceiptCiteRule"] = ("Any citation of a peerReceipts entry must carry that entry's 'citation' field verbatim (e.g. 'recomputed by me (not relayed)' versus 'peer-reported, not recomputed by me'). "
                                       "Reason (raised by test-strategy-architect): the qualification decays over time - a value once flagged 'peer-reported' will later be read as 'verified' unless the flag travels with the citation. "
                                       "Equivalently: never cite a peer value without its provenance flag, just as one never cites a hash without recomputing it.")

entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "adopted the peer-receipt citation rule (qualification must travel with the citation); symmetric-staleness observation recorded",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "observation": ("symmetric staleness: within the same hour both sides lag on different files - my quoted values lagged on acceptance-report.json and on this ledger, while theirs lagged on my anchors file and on their own note. "
                    "The workspace is concurrently edited, so the rule is invariant: recompute at citation time, never carry a transcribed value, and state the scan scope for any whole-tree/non-existence claim."),
    "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest(),
                                             "measuredAt": datetime.datetime.fromtimestamp(os.stat(os.path.join(A, "acceptance-report.json")).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
print("peerReceiptCiteRule added:", "peerReceiptCiteRule" in lg["schema"])
c = os.path.join(A, "acceptance-report.json")
print("current t34:", os.path.getsize(c), "B /", hashlib.sha256(open(c, "rb").read()).hexdigest()[:32])
