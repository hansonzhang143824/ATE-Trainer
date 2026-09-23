# -*- coding: utf-8 -*-
"""The reviewer's prompt exposed three stale claims inside my own carrier-path pointer file: fix them (snapshot line, limitations range, removed superseded-scratch path)."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
CAR = os.path.join(A, "acceptance-report.json")
car_b = open(CAR, "rb").read()
car = {"sizeBytes": len(car_b), "sha256": hashlib.sha256(car_b).hexdigest(),
       "measuredAt": datetime.datetime.fromtimestamp(os.stat(CAR).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
rep = json.loads(car_b.decode("utf-8"))
n_lim = len(rep["limitations"])
print("carrier now:", car, "| limitations:", n_lim)

# rebuild the markdown pointer with current facts (no stale snapshot, no removed path)
md = ("# t34 carrier path (unambiguous)\n\n"
      "`t34` is a TASK LABEL and appears in no filename.\n\n"
      "* carrier (absolute): `D:/Newtest/DSH/ATE-Coding-Plat/team/artifacts/acceptance-20260916-dali10/acceptance-report.json`\n"
      "* carrier (workspace-relative): `team/artifacts/acceptance-20260916-dali10/acceptance-report.json`\n"
      "* the carrier is a LIVE file: recompute before citing. Snapshot at the time this file was last rewritten: %d B / `%s` @ %s\n"
      "* the t34 entries are `limitations[]` in that JSON (currently L1..L%d)\n"
      "* other `*t34*` names in the tree (recursive, verified): the two pointer files themselves, `backups/t60_apply_captain_t34_t35_t41.py`, `backups/t82_t34_pointer.py`, and copies inside `backups/setuparch-20260916-230435/`\n"
      "* historical note: an earlier revision of this line cited `backups/superseded-scratch/...`; that sub-directory no longer exists (verified: exists() = False) and is NOT to be cited again\n\n"
      "**OWNERSHIP:** owner = setup-architect. Do not rewrite this file from another member's generator (suggested DO_NOT_TOUCH_PREFIXES additions: `t34-carrier`, `t34-CARRIER`).\n"
      ) % (car["sizeBytes"], car["sha256"], car["measuredAt"], n_lim)
mp = os.path.join(A, "t34-CARRIER-PATH.md")
open(mp, "w", encoding="utf-8").write(md)
mb = open(mp, "rb").read()
print("t34-CARRIER-PATH.md:", len(mb), "B /", hashlib.sha256(mb).hexdigest())

# check the JSON pointer for the removed path too
jp = os.path.join(A, "t34-carrier-pointer.json")
jd = json.load(open(jp, encoding="utf-8"))
jt = json.dumps(jd, ensure_ascii=False)
before_bad = jt.count("superseded-scratch")
if before_bad:
    jd["why"] = jd.get("why", "").replace("backups/superseded-scratch/t60_apply_captain_t34_t35_t41.py", "backups/t60_apply_captain_t34_t35_t41.py")
    jd["stalePathNote"] = "an earlier revision cited backups/superseded-scratch/... - that sub-directory no longer exists (verified) and must not be cited"
    json.dump(jd, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
jb = open(jp, "rb").read()
print("pointer json: removed-path occurrences before=%d after=%d | %d B / %s" % (
    before_bad, json.dumps(json.load(open(jp, encoding="utf-8")), ensure_ascii=False).count("superseded-scratch"), len(jb), hashlib.sha256(jb).hexdigest()))

# ledger
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "the reviewer's prompt to check the shrunken pointer file exposed THREE stale claims inside it (snapshot line, limitations range, removed superseded-scratch path); all fixed",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "pointerAudit": {"observation": "the reviewer compared 2,388 B with 824 B, but those are two DIFFERENT files: PATH-MAP.md (2,388 B, still present) and t34-CARRIER-PATH.md (824 B). No file lost content.",
                          "butTheirQuestionWasFruitful": "checking as asked exposed three stale claims inside t34-CARRIER-PATH.md: a snapshot size/hash from 22:43:13, the limitations range L1..L44, and a citation of the removed backups/superseded-scratch/ path",
                          "fixes": ["snapshot line now states the live-file rule and marks its values as a snapshot at the last rewrite",
                                    "limitations range updated to L1..L%d" % n_lim,
                                    "the removed path is replaced and flagged as never-to-be-cited again",
                                    "the JSON pointer had the same removed path and was corrected too"],
                          "discipline": "size change proves only that something changed, not what - the reviewer refused to infer, and that refusal is what made this checkable"},
         "artifacts": {"t34-CARRIER-PATH.md": {"path": mp.replace("\\", "/"), "sizeBytes": len(mb), "sha256": hashlib.sha256(mb).hexdigest()},
                       "t34-carrier-pointer.json": {"path": jp.replace("\\", "/"), "sizeBytes": len(jb), "sha256": hashlib.sha256(jb).hexdigest()},
                       "acceptance-report.json": dict(car, path=CAR.replace("\\", "/"))}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
