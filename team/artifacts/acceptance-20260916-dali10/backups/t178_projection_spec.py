# -*- coding: utf-8 -*-
"""Add a fully specified projection spec (exclusion AND serialization) to my anchors file so a third party can reproduce its body hash; log the peer comparison."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

SPEC = {
    "version": 1,
    "exclude": ["generatedAt"],
    "serialization": "json.dumps(body, ensure_ascii=False, sort_keys=True) with Python's DEFAULT separators (', ', ': ')",
    "encoding": "utf-8",
    "note": "the projection must state BOTH the exclusion list and the serialization, otherwise the same criterion reproduces as several different values (measured on the peer report: five plausible conventions gave five different hashes)",
}
body = {k: v for k, v in doc.items() if k not in SPEC["exclude"] and k != "projectionSpec" and k != "bodySha256"}
body_sha = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
doc["projectionSpec"] = SPEC
doc["bodySha256"] = body_sha
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()

# verify by recomputing from the written file
chk = json.load(open(ap, encoding="utf-8"))
chk_body = {k: v for k, v in chk.items() if k not in SPEC["exclude"] and k not in ("projectionSpec", "bodySha256")}
recomputed = hashlib.sha256(json.dumps(chk_body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
print("anchors file:", len(ab), "B / whole-file sha:", hashlib.sha256(ab).hexdigest())
print("bodySha256 recorded :", body_sha)
print("bodySha256 recomputed:", recomputed, "| reproducible by a third party:", recomputed == body_sha)
print("whole-file hash vs body hash differ (expected, file embeds generatedAt):", hashlib.sha256(ab).hexdigest() != body_sha)

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "peer's timestamp root cause confirmed; added a fully specified projection spec to my anchors file (exclusion + serialization) so its body hash is third-party reproducible",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "projectionSpecGap": {
             "peerSpecStates": "exclude=['generatedAt'], version 1, with the rule 'do not mix across versions; bump to v2 when the exclusion list changes'",
             "peerSpecDoesNotState": "the serialization convention (key ordering, separators, encoding) - so a third party cannot reproduce the body hash even on matching bytes",
             "measured": {"theirRecordedBodySha256": "52233dd1e54d9e046677eac11fb44d9c7b391d5d7d15a87f9d51ec251af7f74b",
                          "myFiveConventionsOnTodaysBytes": {"compact sorted": "ce4649e83d2745e4ad363298272758d5d8e75ce690e02c1240a1041be099edac",
                                                             "compact insertion": "3ec88e0fdfb420ccdd5302b9ea2ffa17be818b529a0c79c944eb08d419a3e0c0",
                                                             "default sorted": "65bcb65357ebf253860b1801cba293a2fb48b01b0f35872666db730ba48fc8f4",
                                                             "default insertion": "78d74274615b5518d1f29df751829d9dcda299984f8d038ac97894102ec98b23",
                                                             "all timestamp fields blanked, sorted": "61917c0d9a21032cbb469f508a311dedd2d33c8bf09bf8fbd64d8ca921644691"}},
             "whyNoMatchIsNotTheirError": "their own note says a projection hash must not be compared across versions, and the report has moved from 31,821 B (their message) to 33,808 B (now) - so comparing their value with today's bytes is a cross-version comparison and is invalid by their own rule",
             "requestToPeer": "state the serialization inside projectionSpec and re-issue the body hash on the current bytes; then one round closes it",
             "mySideFix": "my anchors file now carries projectionSpec {exclude, serialization, encoding, version} plus bodySha256, and I verified a third party can recompute it: %s" % body_sha},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "build-report.json": {"path": os.path.join(A, "build-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "build-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "build-report.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
