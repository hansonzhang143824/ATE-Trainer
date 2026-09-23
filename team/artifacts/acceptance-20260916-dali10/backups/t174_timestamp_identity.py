# -*- coding: utf-8 -*-
"""Verify the peer's timestamp root cause and reproduce their body-hash criterion; apply the same criterion to my own timestamp-bearing files."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

br_p = os.path.join(A, "build-report.json")
rc_p = os.path.join(A, "gate-logs-t54", "build-report.receipt.json")
br, rc = rec(br_p), rec(rc_p)
print("peer build-report (now):", br)
print("peer receipt (now)     :", rc)

# reproduce their body-hash criterion: strip the timestamp field, then hash a canonical serialisation
d = json.loads(open(br_p, encoding="utf-8").read())
ts_fields = [k for k in d if isinstance(d[k], str) and ("generatedAt" in k or "at" == k.lower())]
print("timestamp-ish top-level fields in peer report:", ts_fields)
body = {k: v for k, v in d.items() if k != "generatedAt"}
body_canon = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
print("my reproduction of their body hash (sorted-keys canonical):", body_canon)
rd = json.loads(open(rc_p, encoding="utf-8").read())
print("their recorded reproducibleBodySha256:", rd.get("reproducibleBodySha256"))
print("receipt file hash matches live report:", rd.get("sha256") == br["sha256"], "| size matches:", rd.get("size") == br["sizeBytes"])
print("byte-level body with the generatedAt line removed:")
import re
raw = open(br_p, "rb").read().decode("utf-8")
raw_nostamp = re.sub(r'"generatedAt"\s*:\s*"[^"]*"\s*,?', "", raw)
print("   sha256 of that byte-level body:", hashlib.sha256(raw_nostamp.encode("utf-8")).hexdigest())

# apply the same criterion to my own timestamp-bearing artifacts
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
ad = json.loads(open(ap, encoding="utf-8").read())
abody = {k: v for k, v in ad.items() if k != "generatedAt"}
print("\nmy anchors file:", rec(ap)["sizeBytes"], "B /", rec(ap)["sha256"][:24])
print("   my body hash excluding generatedAt:", hashlib.sha256(json.dumps(abody, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "peer located the root cause of our sha discrepancy (an embedded second-level timestamp) and switched to a body hash; I reproduced the criterion and applied it to my own files",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "timestampIdentity": {
             "rootCause": "the peer report embeds generatedAt at second granularity, so the whole-file hash changes on every regeneration while the size stays the same - 'same size, different sha' is EXPECTED for such a file, not a defect",
             "criterionFix": "the reproducible criterion is the BODY hash with the timestamp field removed; the peer added reproducibleBodySha256 to its receipt and forced a 1.2s gap self-test (same size, same body hash, different file hash)",
             "myReproduction": {"theirRecorded": rd.get("reproducibleBodySha256"), "myCanonicalBodyHash": body_canon,
                                "byteLevelBodyHash": hashlib.sha256(raw_nostamp.encode("utf-8")).hexdigest(),
                                "note": "two body-hash conventions differ (canonical JSON vs byte-level with the line removed), so a body hash must state its convention - otherwise the same criterion reproduces as two different values"},
             "appliedToMyOwnFiles": {"file": ap.replace("\\", "/"), "wholeFileSha256": rec(ap)["sha256"],
                                     "bodySha256ExcludingGeneratedAt": hashlib.sha256(json.dumps(abody, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()},
             "newInstance": "this extends the same-size/different-identity family: a file that embeds its own generation time cannot be identified by its whole-file hash across seconds",
         },
         "peerSelfReportedSlip": "the peer reports an intermediate missing comma in its receipt writer that briefly broke the generator (SyntaxError), fixed immediately and re-verified - another live instance of 'verify after every change'",
         "artifacts": {"build-report.json": br, "gate-logs-t54/build-report.receipt.json": rc,
                       "gate-logs-t28/setupArchitect-anchors.json": rec(ap)}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
