# -*- coding: utf-8 -*-
"""Update my peer identitySource to the current receipt plus the new append-only receipts ledger, per the owner's request."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

br = rec(os.path.join(A, "build-report.json"))
rc = rec(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"))
jl_p = os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl")
jl = rec(jl_p)
rows = [l for l in open(jl_p, encoding="utf-8").read().splitlines() if l.strip()]
print("build-report      :", br["sizeBytes"], "B /", br["sha256"][:24], "@", br["measuredAt"])
print("receipt           :", rc["sizeBytes"], "B /", rc["sha256"][:24], "@", rc["measuredAt"])
print("receipts.jsonl    :", jl["sizeBytes"], "B /", jl["sha256"][:24], "| rows:", len(rows))
rd = json.load(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), encoding="utf-8"))
print("receipt fields    :", sorted(rd.keys()))
print("receipt consistent:", rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"])
first = json.loads(rows[0]) if rows else {}
last = json.loads(rows[-1]) if rows else {}
print("jsonl row0 keys   :", sorted(first.keys()))
print("jsonl last row at :", last.get("at"), "| chain fields present:", any(k for k in last if "prev" in k.lower() or "self" in k.lower()))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["peer/build-report.json"] = dict(
    br, owner="compile-diagnostician",
    note="peer artifact; size/sha recomputed by me, content not reviewed",
    liveness="THE PEER REPORT IS A LIVE FILE: it must not be labelled FROZEN and its in-report self-computed hashes must not be cited. To pin the identity of a particular version, read the receipt and recompute it.",
    identitySource=("gate-logs-t54/build-report.receipt.json (current: %d B / %s @ %s; the receipt is REGENERATED on every run, so its own size and time must be recomputed too) "
                    "plus the append-only history gate-logs-t54/build-report.receipts.jsonl (current: %d B / %s; %d rows)" % (
                        rc["sizeBytes"], rc["sha256"], rc["measuredAt"], jl["sizeBytes"], jl["sha256"], len(rows))),
    identitySourceNote="the receipt and its history ledger are themselves live files - cite them by path and recompute; same rule as 'a pointer must not hard-code a size'",
)
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("\nanchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "updated my peer identitySource to the current receipt plus the owner's new append-only receipt history, at the owner's request",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "peerIdentitySource": {"receipt": rc, "receiptHistory": dict(jl, rows=len(rows)), "report": br,
                                "receiptConsistentWithLiveBytes": rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"],
                                "receiptFields": sorted(rd.keys()),
                                "note": "the receipt carries 'size' (not sizeBytes) - the field name was itself the source of an earlier false negative on my side; and the receipt is regenerated per run, so its own size/time must be recomputed like any live value"},
         "artifacts": {"build-report.json": br, "gate-logs-t54/build-report.receipt.json": rc, "gate-logs-t54/build-report.receipts.jsonl": jl}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
