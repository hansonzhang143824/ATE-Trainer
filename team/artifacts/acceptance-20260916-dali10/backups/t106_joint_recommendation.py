# -*- coding: utf-8 -*-
"""Verify typo status; log the joint recommendation (b now, (a) post-thaw) agreed with the reviewer."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

carrier = os.path.join(A, "acceptance-report.json")
t = open(carrier, encoding="utf-8").read()
print("typo status now: correct=%d misspelled=%d" % (t.count("TM643_VBAT_LOOP_INDICTOR"), t.count("TM643_VAT_LOOP_INDICTOR")))
print("carrier:", rec(carrier))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
JOINT = ("JOINT RECOMMENDATION ON GATE INTEGRITY (rule-reviewer has adopted my weighting and moved from (a) to (b)): implement (b) immediately - the orchestrator asserts that the bst-sw output contains 'targets=N' with N>0, else FAIL - "
         "and (c) is already landed as t34 L45; (a) (making a zero-target scan a hard error inside the gate script) is deferred to the post-thaw cleanup, where it can be bundled with other gate-domain improvements in a single re-review. "
         "Criteria: (b) does not touch scripts/ (honouring this batch's standing rule), is immediately effective and highly reversible; (a) is more thorough but touches the gate domain, requires a fresh verdict on new bytes and is unattractive while the contract is frozen. "
         "The reviewer notes their earlier preference for (a) failed to price in those costs. Doing nothing leaves a false-green channel with no log trace.")
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "joint gate-integrity recommendation (b now, (a) post-thaw) after the reviewer adopted my weighting; typo status re-confirmed",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "jointRecommendation": JOINT,
    "typoStatus": {"carrier": rec(carrier), "correct": t.count("TM643_VBAT_LOOP_INDICTOR"), "misspelled": t.count("TM643_VAT_LOOP_INDICTOR"),
                   "fixedAt": "2026-09-16 23:09:01", "note": "the reviewer's and schematic-expert's scans predate the fix"},
    "artifacts": {"acceptance-report.json": rec(carrier), "scripts/gate_baseline.json": rec("scripts/gate_baseline.json")},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
