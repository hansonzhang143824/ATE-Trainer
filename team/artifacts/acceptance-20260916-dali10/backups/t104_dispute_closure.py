# -*- coding: utf-8 -*-
"""Log the closure of the message-quote dispute, with a recomputed peer receipt."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"

def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

note = os.path.join(A, "review-handoff-note-plan-side.md")
nr = rec(note)
print("peer note (recomputed):", nr["sizeBytes"], "B /", nr["sha256"], "@", nr["measuredAt"])
print("matches their reported 65,653 B:", nr["sizeBytes"] == 65653)

CLOSURE = (
    "CLOSURE OF THE MESSAGE-QUOTE DISPUTE (both sides now agree): test-strategy-architect withdrew their 'I never said it' assertion and named the lesson - check the outgoing message log with the same rigour as the artefacts, "
    "and do not defend a position on memory when the counterparty holds the quotation. Symmetry recorded honestly: I made an analogous lapse earlier in this run when I attributed a diagnostician reading to a rev-28 copy without measuring it, "
    "and withdrew it after their evidence anchor. Both are the same failure mode: treating a remembered or inferred attribution as a measurement. Confirmed current facts: the gate expectation is {48,60,61,76,83} on both sides; the old [48,61,76] survives only in annotated/historical contexts in both parties' artefacts; "
    "and the two 'v26' questions are DISTINCT - (a) annotating the plan's four [48,61,76] occurrences is closed (no new revision needed), (b) annotating the withdrawn B-argument inside v25's history remains pending with the captain and does not change the operative value."
)

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))

receipt = dict(nr)
receipt["owner"] = "test-strategy-architect"
receipt["citation"] = "recomputed by me (not relayed)"
receipt["note"] = ("their reported 65,653 B matched my recomputation" if nr["sizeBytes"] == 65653
                   else "their reported 65,653 B differs from my recomputation - the value moved again")

lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "message-quote dispute closed on both sides; recorded the mutual lesson and the distinctness of the two v26 questions",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "closure": CLOSURE,
    "peerReceipts": [receipt],
    "artifacts": {
        "acceptance-report.json": rec(os.path.join(A, "acceptance-report.json")),
        "implementation-input-pin.json": rec(os.path.join(A, "implementation-input-pin.json")),
        "setup-contract.json": rec(os.path.join(A, "setup-contract.json")),
        "test-plan.json": rec(os.path.join(A, "test-plan.json")),
    },
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
