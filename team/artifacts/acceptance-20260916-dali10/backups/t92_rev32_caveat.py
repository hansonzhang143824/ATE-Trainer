# -*- coding: utf-8 -*-
"""Add the rev-32 attribution caveat, the append-only ledger discipline line, and the recomputed build-report value to t34; refresh anchors + ledger."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

br = os.path.join(A, "build-report.json")
br_rec = rec(br) if os.path.exists(br) else None
print("build-report.json:", br_rec)

f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
L48 = ("L48 (two additions requested by compile-diagnostician, plus its recomputed value): "
       "(1) CAVEAT on the rev-32 attribution (must sit next to L42): the historical log's self-reported 'rev=32' plus the fact that the channel-5 expectation appears somewhere in the interval (rev 28 snapshot -> current disk) only supports "
       "'log self-report + interval compatibility'. The bytes of the rev-32 file no longer exist (no byte snapshot was taken), so it must NOT be claimed that the gate's input has been BYTE-PROVEN to be rev 32. "
       "(2) DISCIPLINE (implementation form of discipline 3 'copy the bytes, do not merely record hashes'): all parties now keep an append-only snapshot ledger - setup-architect: gate-logs-t28/setupArchitect-freeze-snapshots.json; "
       "compile-diagnostician: gate-logs-t28/t28-anchors.snapshots.jsonl - each entry appended, never overwriting history, carrying a timestamp, and (on my side) kind=full + contractRevision + artifacts + selfAnchor. "
       + ("(3) RECOMPUTED peer value: build-report.json = %d B / %s @ %s (the 21,300 B I quoted earlier was stale; I recompute rather than relay)." % (br_rec["sizeBytes"], br_rec["sha256"], br_rec["measuredAt"]) if br_rec else ""))
d["limitations"].append(L48)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = dict(rec(f34), writesStopped=False)
if br_rec:
    doc["anchors"]["peer/build-report.json"] = dict(br_rec, owner="compile-diagnostician", note="peer artifact, owner-reported + recomputed by me for size/sha; content not reviewed here")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
FILES = {"acceptance-report.json": f34, "gate-logs-t28/setupArchitect-anchors.json": ap,
         "build-report.json": br, "setup-contract.json": os.path.join(A, "setup-contract.json"),
         "implementation-payload-TM600-TM601.cpp": os.path.join(A, "implementation-payload-TM600-TM601.cpp"),
         "test-plan.json": os.path.join(A, "test-plan.json"), "scripts/gate_baseline.json": "scripts/gate_baseline.json"}
lg["entries"].append({"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
                      "reason": "t34 L48: rev-32 attribution caveat + append-only-ledger discipline line + recomputed build-report value (peer value re-measured instead of relayed)",
                      "contractRevision": 39,
                      "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
                      "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
                      "artifacts": {k: rec(v) for k, v in FILES.items() if os.path.exists(v)}})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(post), "B /", hashlib.sha256(post).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(LOG).st_mtime).strftime("%H:%M:%S"))
