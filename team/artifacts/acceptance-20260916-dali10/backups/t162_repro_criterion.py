# -*- coding: utf-8 -*-
"""Archive the reproducible-criterion convention (with its boundary caveat) and note its adoption by the plan side."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
CONV = {
    "name": "reproducible criterion (proposed by setup-architect, adopted by the plan side as its section 2.8)",
    "statement": "A criterion given as prose can only be BELIEVED; a criterion given as a command plus expected output can be CHECKED. Every gate or acceptance claim should carry the command that produced it and the output that proves it.",
    "instances": [
        "pin alignment: one command printing the byte-match flag, size, hash, mtime and plan status, with expected output '185689 True 185689 2026-09-16 21:54:50 v25 ... NOT FINAL' - both sides re-ran it independently",
        "the t34 locator command plus a direct call of the gate's own closure function, showing missing=[] errors=0 on the payload",
    ],
    "costOfNotDoingIt": "the review side can only trust narration, which produced this run's friction: 'a declaration goes stale as soon as it is made', the same-size/three-hash case, and coordinates that looked stale but had merely moved",
    "boundaryCaveat": ("reproducibility proves only that THE COMMAND YIELDS THAT OUTPUT FOR THAT INPUT. It is NOT an electrical or acceptance conclusion. This binds to the standing rule 'a gate PASS is not an electrical sign-off' so that reproducibility cannot be misread as evidence about the hardware.",
                       "proposed by the plan side; adopted here"),
    "status": "adopted by the plan side (their section 2.8, with both instances); being raised with the captain as a run convention",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "archived the reproducible-criterion convention (adopted by the plan side) with its boundary caveat; raising it with the captain",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "reproducibleCriterion": CONV,
         "peerNoteReconciliation": {"theirClaimedSameMomentReading": "66,305 B / 968def24... @23:04:01", "myRecomputation": "identical", "conclusion": "the earlier apparent discrepancy was a send-time versus measure-time difference, not a disagreement",
                                     "currentNote": "they now cite 79,136 B / 054dc9ab... @23:36:20 - the file keeps moving, so citations stay path + recomputation"},
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "review-handoff-note-plan-side.md": {"path": os.path.join(A, "review-handoff-note-plan-side.md").replace("\\", "/"),
                                                            "sizeBytes": os.path.getsize(os.path.join(A, "review-handoff-note-plan-side.md")),
                                                            "sha256": hashlib.sha256(open(os.path.join(A, "review-handoff-note-plan-side.md"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["reproducibleCriterion"] = CONV
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
