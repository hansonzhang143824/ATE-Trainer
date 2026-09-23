# -*- coding: utf-8 -*-
"""Add the diagnostician's two cross-references into t34 L45 (append-only wording), verify their build-report size, refresh anchors + ledger."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

br = os.path.join(A, "build-report.json")
br_rec = rec(br)
print("build-report.json (recomputed):", br_rec["sizeBytes"], "B /", br_rec["sha256"][:24], "@", br_rec["measuredAt"], "| they reported 28,909 B")

f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
XREF = (" CROSS-REFERENCE (added at compile-diagnostician's request, both sides now linked): the same gap is registered in its own report as build-report.emptyPassGuard.status = recorded but NOT ENFORCED, together with enforcementGap, residualRisk, fixOptions (i)/(ii) and the criterion "
        "'an unchecked run must not be mapped to PASS'; and as exitZeroSemantics, which separates the two kinds of exit 0 (assertion executed vs empty-PASS early return). Its own measurement agrees with mine: run_gates.ps1 has zero references to targets/scan/emptyPassGuard. "
        "If the captain authorises remedy (b), the re-run precondition can reuse the assertion sentence recorded in this entry.")
n = 0
for i, x in enumerate(d["limitations"]):
    if x.startswith("L45 ") and "CROSS-REFERENCE (added at compile-diagnostician" not in x:
        d["limitations"][i] = x + XREF
        n += 1
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("L45 cross-reference added:", n, "| t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(),
      "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = dict(rec(f34), writesStopped=False)
doc["anchors"]["peer/build-report.json"] = dict(br_rec, owner="compile-diagnostician", note="peer artifact; size/sha recomputed by me, content not reviewed")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "t34 L45 now cross-references compile-diagnostician's emptyPassGuard and exitZeroSemantics (their request); their peer rule (peer ledger must not be called a neutral baseline) confirmed; build-report recomputed",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "crossReference": "t34 L45 <-> build-report.emptyPassGuard/exitZeroSemantics; both record that run_gates.ps1 has zero references to targets/scan/emptyPassGuard, and both recommend remedy (b) with (c) already landed",
    "artifacts": {"acceptance-report.json": rec(f34), "build-report.json": br_rec, "scripts/gate_baseline.json": rec("scripts/gate_baseline.json")},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
