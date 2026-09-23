# -*- coding: utf-8 -*-
"""Record the shared closure of the namespace dispute and adopt the peer's 'authoritative != independent != neutral' triad; recompute the peer report."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

br = rec(os.path.join(A, "build-report.json"))
rc = rec(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"))
print("peer build-report:", br)
print("peer receipt     :", rc)
if rc and br:
    rd = json.load(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), encoding="utf-8"))
    print("receipt matches current bytes:", rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"])

TRIAD = ("BASELINE TRIAD (adopted from compile-diagnostician's baselineTriad): a source can be AUTHORITATIVE (the gate consumes it - the contract's closedRelayNumbers), INDEPENDENT (maintained by a party other than the one being reviewed), and NEUTRAL (owned by no party in the exchange) - "
         "the three are different properties. In this run: the contract is authoritative and neutral, the peer's report is independent of me but its own product, and my anchors file is neither independent nor neutral for a reviewer - which is exactly why rule-reviewer declined to use it as a baseline.")

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "namespace dispute closed on all three sides with the two-part statement; adopted the authoritative/independent/neutral triad and recomputed the peer report",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "baselineTriad": TRIAD,
         "disputeClosureThreeSides": {
             "statement": "(1) the top-level key IS preserved; (2) the preserved content is 1 entry and the earlier eight have no copy anywhere",
             "myScan": "397 files at my time point; 6 files contain the key string - 3 of my own scripts (code references) and 3 inside my 23:04 byte-copy snapshot, all carrying the CURRENT single-entry state",
             "theirScan": "411 files at their time point; same 6 files, same classification; the file they still label 371 items counted top-level entries including directories",
             "agreedKeyPoint": "copies that preserve the OLD eight entries = 0, so 'no copy retains the old content' holds; the earlier wording 'zero hits for the key string' was imprecise on their side and is corrected",
             "lossAttribution": "the owner's own account (its fix script records the earlier 6~8 -> 1 collapse); not my inference and not the reviewer's",
         },
         "artifacts": {"build-report.json": dict(br, owner="compile-diagnostician", note="peer artifact; size/sha recomputed by me, content not reviewed") if br else None,
                       "gate-logs-t54/build-report.receipt.json": rc,
                       "acceptance-report.json": rec(os.path.join(A, "acceptance-report.json"))}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["baselineTriad"] = TRIAD
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
