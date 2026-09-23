#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check for the TM109 test method contract (task TM109-METHOD-R1).

Read-only over the workspace except for writing its own report
self-check-tm109-method.json. Exit code 0 = every check PASS.

Hashing uses Path.read_bytes() (the DLP plaintext reader) on purpose; the native
Windows hashing path returns ciphertext for DLP-protected artifacts.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
METHOD = HERE.parent
TRIAL = METHOD.parent
ROOT = HERE.parents[4]

CONTRACT = METHOD / "tm109-test-method-contract.json"
MD = METHOD / "tm109-test-method-contract.md"
REPORT = METHOD / "self-check-tm109-method.json"
HANDOFF = METHOD / "deliverable-ready.json"
STRATEGY = TRIAL / "strategy" / "tm109-resource-config-contract.json"
STRATEGY_HANDOFF = TRIAL / "strategy" / "deliverable-ready.json"

RESULTS = []


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(cid, description, ok, evidence):
    RESULTS.append({
        "id": cid,
        "description": description,
        "status": "PASS" if ok else "FAIL",
        "evidence": evidence,
    })
    return ok


def pending(cid, description, evidence):
    RESULTS.append({
        "id": cid,
        "description": description,
        "status": "PENDING",
        "evidence": evidence,
    })
    return True


def main() -> int:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    s = json.loads(STRATEGY.read_text(encoding="utf-8"))
    sh = json.loads(STRATEGY_HANDOFF.read_text(encoding="utf-8"))

    strategy_sha = sha256(STRATEGY)
    contract_sha = sha256(CONTRACT)
    md_sha = sha256(MD)

    # SC-01  artifacts parse
    check("SC-01", "method contract, signed strategy contract and strategy handoff all parse as JSON",
          isinstance(c, dict) and isinstance(s, dict) and isinstance(sh, dict),
          {"contractSections": len(c), "strategySections": len(s)})

    # SC-02  the DLP hash gate: the plaintext digest of the signed input equals the signed digest
    check("SC-02", "signed strategy contract sha256 equals the digest recorded in the strategy handoff",
          strategy_sha == sh.get("sha256"),
          {"recomputedPlaintext": strategy_sha, "handoffDeclared": sh.get("sha256"),
           "reader": "Path.read_bytes via hashlib.sha256"})

    # SC-03  the digest this contract recorded for its input is the same digest
    recorded = [x.get("verifiedSha256") for x in c.get("signedInputs", [])]
    check("SC-03", "the sha256 this contract records for its signed input equals the recomputed plaintext digest",
          strategy_sha in recorded,
          {"recorded": recorded, "recomputed": strategy_sha})

    # SC-04  the handoff gate that authorises this stage
    check("SC-04", "strategy handoff is a deliverable_ready event routed to test-method-expert",
          sh.get("event") == "deliverable_ready" and sh.get("nextRole") == "test-method-expert",
          {"event": sh.get("event"), "fromRole": sh.get("fromRole"), "nextRole": sh.get("nextRole"),
           "taskId": sh.get("taskId")})

    # SC-05  contract verdict and the mandated section set
    required_sections = ["methodEvidence", "methodPhases", "measurementPlan", "powerDownPlan",
                         "logPlan", "evidence", "openItems", "strategyBoundaryCarriedVerbatim",
                         "goldenApplicability", "bstSwApplicability", "limitPlan",
                         "routedFindings", "inputVerification", "charterBoundary", "handoff"]
    missing = [k for k in required_sections if k not in c]
    check("SC-05", "contract verdict is deliverable_ready and every mandated section is present",
          c.get("verdict") == "deliverable_ready" and not missing,
          {"verdict": c.get("verdict"), "missingSections": missing})

    phases = c.get("methodPhases", [])
    phase_fields = ["phaseId", "name", "category", "purpose", "prerequisite", "relayGroup",
                    "resourceState", "registerActivation", "actualNodeVoltages",
                    "differentialChecks", "bstSwCheck", "setpoint", "ramp", "delay", "sample",
                    "exitCondition", "onFailure", "evidence"]
    bad = []
    for p in phases:
        for f in phase_fields:
            if f not in p or p[f] in (None, "", [], {}):
                bad.append("%s.%s" % (p.get("phaseId"), f))
    check("SC-06", "every planned phase carries all mandated fields with non-empty values",
          not bad, {"phaseCount": len(phases), "violations": bad})

    # SC-07  BST/SW per-phase constraint recorded for every phase
    constraint = "0 V <= BST_actual - SW_actual <= 5 V"
    bst_bad = []
    for p in phases:
        b = p.get("bstSwCheck") or {}
        if b.get("constraint") != constraint:
            bst_bad.append("%s: constraint missing or altered" % p.get("phaseId"))
        if b.get("applicable") is False and not (b.get("proofBasis") and b.get("wouldBecomeApplicableIf")):
            bst_bad.append("%s: NOT_APPLICABLE without a derivation or falsification trigger" % p.get("phaseId"))
    check("SC-07", "every phase evaluates 0 V <= BST_actual - SW_actual <= 5 V, with a derivation and a falsification trigger where it is not applicable",
          not bst_bad, {"violations": bst_bad, "resultPerPhase": {p["phaseId"]: p["bstSwCheck"]["result"] for p in phases},
                        "gateEvidence": c.get("bstSwApplicability", {}).get("gateEvidence")})

    # SC-08  strategy-owned values are copied, not changed
    carry = {e["endpointId"]: e for e in c.get("strategyBoundaryCarriedVerbatim", {}).get("endpointMap", [])}
    strategy_ra = {e["endpointId"]: e for e in s.get("resourceAllocation", [])}
    mism = []
    for eid, ref in strategy_ra.items():
        mine = carry.get(eid)
        if not mine:
            mism.append(eid + ": missing from the carried boundary")
            continue
        for key in ("sourceTable", "slot", "channel", "selectedPath"):
            if mine.get(key) != ref.get(key):
                mism.append("%s.%s: %r != %r" % (eid, key, mine.get(key), ref.get(key)))
        if sorted(mine.get("closureSet") or []) != sorted(ref.get("requiredActuations") or []):
            mism.append("%s.closureSet: %r != %r" % (eid, mine.get("closureSet"), ref.get("requiredActuations")))
    s_reg = [(x.get("order"), x.get("call"), x.get("reg"), x.get("data")) for x in s.get("registerDelta", []) if x.get("call")]
    c_reg = [(x.get("order"), x.get("call"), x.get("reg"), x.get("data")) for x in c["strategyBoundaryCarriedVerbatim"]["registerDelta"]]
    if s_reg != c_reg:
        mism.append("registerDelta: %r != %r" % (c_reg, s_reg))
    check("SC-08", "every strategy-owned source, route, slot, channel, closure set and register value is carried verbatim (nothing changed or added)",
          not mism, {"violations": mism, "endpointsChecked": sorted(strategy_ra.keys()),
                     "registerDelta": c_reg})

    # SC-09  measurement plan completeness
    mp = c.get("measurementPlan", {})
    mp_keys = ["forceMeasureEndpoints", "range", "sweepOrStep", "sample", "calculation", "limit", "siteHandling"]
    check("SC-09", "measurement plan defines endpoints, range, sweep or step, sampling, calculation, limit and site handling",
          all(k in mp and mp[k] for k in mp_keys),
          {"missing": [k for k in mp_keys if not mp.get(k)]})

    # SC-10  limit provenance
    lp = {x["name"]: x for x in c.get("limitPlan", {}).get("parameters", [])}
    ok10 = (lp.get("VAC2_PRST_Rise", {}).get("nominal") == 4.15
            and lp.get("VAC2_PRST_Hys", {}).get("nominal") == 350
            and "DERIVED" in (lp.get("VAC2_PRST_Fall", {}).get("class") or "")
            and "UNRESOLVED" in (lp.get("VAC2_PRST_Rise", {}).get("toleranceStatus") or "")
            and "PENDING_LIMIT_RULING" in (lp.get("VAC2_PRST_Rise", {}).get("judgement") or ""))
    check("SC-10", "limits keep their DFT provenance, the falling value is marked DERIVED, and the missing tolerance keeps the judgement pending",
          ok10, {k: {kk: lp[k].get(kk) for kk in ("nominal", "unit", "class", "judgement", "toleranceStatus")} for k in lp})

    # SC-11  power-down and cleanup
    pd = c.get("powerDownPlan", {})
    order = [a.get("order") for a in pd.get("actions", [])]
    check("SC-11", "power-down is ordered (sources to zero before the path relays open), has a safe end state and forbids invented register writes",
          pd.get("ordered") is True and order == sorted(order) and len(order) >= 5
          and bool(pd.get("safeEndState")) and "no register write" in (pd.get("registerPolicy") or ""),
          {"order": order, "safeEndState": pd.get("safeEndState"), "registerPolicy": pd.get("registerPolicy")})

    # SC-12  log plan
    log = c.get("logPlan", {})
    log_keys = ["rawValues", "calculatedValues", "judgement", "unit", "precision", "context"]
    check("SC-12", "log plan defines raw values, calculated values, judgement, unit, precision and context",
          all(k in log and log[k] for k in log_keys), {"missing": [k for k in log_keys if not log.get(k)]})

    # SC-13  golden applicability
    ga = c.get("goldenApplicability", {})
    dims = ga.get("dimensionComparison", [])
    verdicts = {g.get("verdict", "") for g in ga.get("candidates", [])}
    check("SC-13", "Golden applicability is judged per dimension against parameter type, topology, relative voltages, DFT operation point, source mode and resource boundary",
          len(dims) >= 6 and bool(ga.get("conclusion")) and any("differs" in (d.get("verdict") or "") for d in dims)
          and all(any(v.startswith(x) for x in ("direct", "partial", "unavailable")) for v in verdicts),
          {"dimensions": [d["dimension"] for d in dims], "conclusionStartsWith": (ga.get("conclusion") or "")[:7]})

    # SC-14  method evidence applicability labels
    ev = c.get("methodEvidence", [])
    bad_ev = [e.get("id") for e in ev
              if e.get("applicability", "").split()[0] not in ("direct", "partial", "unavailable")
              or not e.get("reason") or not e.get("source") or not e.get("locator")]
    check("SC-14", "every method evidence entry states a source, a locator, an applicability of direct/partial/unavailable and a reason",
          not bad_ev, {"violations": bad_ev, "count": len(ev)})

    # SC-15  routed findings are actionable and no strategy edit is claimed
    rf = c.get("routedFindings", [])
    bad_rf = [f.get("id") for f in rf if not f.get("routedTo") or not f.get("closingSource") or not f.get("fact")]
    check("SC-15", "every routed finding names an owner, a closing source and the fact that raised it; the contract claims no strategy edit",
          not bad_rf and bool(c.get("charterBoundary", {}).get("strategyArtifactsUnmodified")),
          {"violations": bad_rf, "findings": [f.get("id") for f in rf],
           "strategyArtifactsUnmodified": c.get("charterBoundary", {}).get("strategyArtifactsUnmodified")})

    # SC-16  output scope
    allowed = {"tm109-test-method-contract.json", "tm109-test-method-contract.md",
               "self-check-tm109-method.py", "self-check-tm109-method.json", "deliverable-ready.json"}
    present = sorted(p.name for p in METHOD.iterdir() if p.is_file())
    check("SC-16", "the method output directory contains only this task's declared artifacts",
          set(present) <= allowed, {"present": present, "allowed": sorted(allowed)})

    # SC-17  phase identity and node coverage
    ids = [p.get("phaseId") for p in phases]
    nodes_ok = all(all(n in p["actualNodeVoltages"] for n in ("VBAT", "VAC2", "INT", "BST", "SW")) for p in phases)
    check("SC-17", "phase ids are unique and every phase states the actual node voltages for VBAT, VAC2, INT, BST and SW",
          len(ids) == len(set(ids)) and nodes_ok and ids[0] == "MP-1",
          {"phaseIds": ids, "nodeKeysPresent": nodes_ok})

    # SC-18  handoff binding (final gate)
    if HANDOFF.is_file():
        h = json.loads(HANDOFF.read_text(encoding="utf-8"))
        check("SC-18", "deliverable-ready.json is a deliverable_ready event bound to this contract by sha256",
              h.get("event") == "deliverable_ready" and h.get("sha256") == contract_sha
              and h.get("nextRole") == "ate-implementer" and h.get("taskId") == "TM109-METHOD-R1",
              {"event": h.get("event"), "declared": h.get("sha256"), "recomputed": contract_sha,
               "nextRole": h.get("nextRole"), "blockingItems": h.get("blockingItems")})
    else:
        pending("SC-18", "deliverable-ready.json is a deliverable_ready event bound to this contract by sha256",
                {"note": "handoff not written yet in this pass (written after the first self-check run)"})

    failed = [r for r in RESULTS if r["status"] == "FAIL"]
    report = {
        "checkId": "tm109-method-self-check",
        "taskId": "TM109-METHOD-R1",
        "role": "test-method-expert",
        "projectId": c.get("projectId"),
        "tm": c.get("tm"),
        "generatedAt": c.get("generatedAt"),
        "hashReader": "python hashlib over Path.read_bytes() (DLP plaintext); the native Windows hashing path returns ciphertext for these files",
        "artifactHashes": {
            "tm109-test-method-contract.json": contract_sha,
            "tm109-test-method-contract.md": md_sha,
            "self-check-tm109-method.py": sha256(HERE),
            "signed-strategy-contract.json": strategy_sha,
            "signed-strategy-deliverable-ready.json": sha256(STRATEGY_HANDOFF),
        },
        "results": RESULTS,
        "counts": {
            "pass": len([r for r in RESULTS if r["status"] == "PASS"]),
            "fail": len(failed),
            "pending": len([r for r in RESULTS if r["status"] == "PENDING"]),
        },
        "overall": "FAIL" if failed else "PASS",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("self-check %s: pass=%d fail=%d pending=%d" % (report["overall"], report["counts"]["pass"],
                                                         report["counts"]["fail"], report["counts"]["pending"]))
    for r in RESULTS:
        if r["status"] != "PASS":
            print("  %s %s %s" % (r["status"], r["id"], json.dumps(r["evidence"], ensure_ascii=False)))
    print("contract sha256 = " + contract_sha)
    print("md sha256       = " + md_sha)
    print("script sha256   = " + sha256(HERE))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
