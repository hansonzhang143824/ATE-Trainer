# -*- coding: utf-8 -*-
"""Archive the four discipline items agreed with the reviewer, and confirm the prefix guard is already a mechanism (not a promise)."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
ARCHIVE = [
    "(a) a name is a recomputable fact, not a style choice: function/relay/pin names are always taken from the source, never retyped or relayed",
    "(b) a typo in a message and a defect in an artifact are two different things: correction requests apply to ARTIFACTS, and any citation must give path + recomputation",
    "(c) a misspelled name is a derived-text defect (search and cross-reference silently miss it) - the same family as the union residue and the omitted K60",
    "(d) a fix must cure the criterion: replacing a one-off correction with 'derive from the source' plus a post-fix sweep is the root cure (that was the point of the four reminders)",
]
gen = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
gt = open(gen, encoding="utf-8").read()
m = re.search(r"DO_NOT_TOUCH_PREFIXES\s*=\s*\(([^)]*)\)", gt)
prefixes = m.group(1).strip() if m else "not found"

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "archived the four discipline items agreed with the reviewer; confirmed the prefix guard is already a mechanism, and that the reviewer's figures were earlier time points",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "disciplineArchive": ARCHIVE,
         "prefixGuardIsMechanism": {"generator": gen.replace("\\", "/"), "generatorSizeBytes": os.path.getsize(gen),
                                    "generatorSha256": hashlib.sha256(open(gen, "rb").read()).hexdigest(),
                                    "DO_NOT_TOUCH_PREFIXES": prefixes,
                                    "note": "the reviewer supported adding t34-carrier/t34-CARRIER; that is already implemented by the owner, so the protection is a mechanism rather than a promise"},
         "valueUpdate": {"theirFiguresWereEarlier": {"carrier": "they measured 70,540 B / 05288c83... while I had moved on", "ledger": "they measured 100,219 B / 1c587cbb... (28 entries) while this entry brings the ledger past 43"},
                         "rule": "live files: recompute at citation time"},
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "gate-logs-t28/t28_make_anchors.py": {"path": gen.replace("\\", "/"), "sizeBytes": os.path.getsize(gen),
                                                             "sha256": hashlib.sha256(open(gen, "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["disciplineArchive"] = ARCHIVE
doc["prefixGuardIsMechanism"] = "owner's generator DO_NOT_TOUCH_PREFIXES = %s (already implemented, not a promise)" % prefixes
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("prefixes:", prefixes)
