"""Correct TM109 strategy contract where its owned INT route was left unresolved."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "team" / "artifacts" / "tm109-direct-trial"
CONTRACT = TRIAL / "strategy" / "tm109-resource-config-contract.json"
BACKUP = TRIAL / "strategy" / "backup" / "tm109-resource-config-contract.before-int-allocation.json"
RECORD = TRIAL / "strategy" / "strategy-int-allocation-correction.json"
HANDOFF = TRIAL / "strategy" / "deliverable-ready.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(items, key, value):
    return next(x for x in items if x[key] == value)


def main():
    before = sha256(CONTRACT)
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    if not BACKUP.exists():
        shutil.copy2(CONTRACT, BACKUP)
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    allocation = one(data["resourceAllocation"], "allocationId", "RA-3")
    allocation.update({
        "sourceTable": "ACM200",
        "slot": "S5",
        "channel": "15",
        "ports": ["S5_ACM200_FH15 (force)", "S5_ACM200_SH15 (sense)"],
        "selectionState": "SELECTED",
        "selectedPath": "S5_ACM200_FH15 -> K102_PC3_S1 (un-actuated/default conducting) -> INT_F_S1; S5_ACM200_SH15 -> K102_PC3_S1 (un-actuated/default conducting) -> INT_S_S1",
        "requiredActuations": [],
        "requiredActuationsCount": 0,
        "requiredActuationsByLeg": {"forceLeg": [], "senseLeg": [], "unionCount": 0},
        "selectionBasis": "knowledge/hardware/pin-resource-map.md assigns INT / SDA to SDA_INT_ACM (ACM200); the frozen source-centric records directly reach both INT_F_S1 and INT_S_S1 from ACM200 ch15. The test-method stage still owns the observation mode, sampling and limits.",
        "confidence": "direct rule-layer assignment plus frozen source-centric reachability; K102 state is chain-context inference",
        "class": "SELECTED route; measurement mode intentionally deferred to test-method-expert",
    })
    allocation.pop("whyUnresolved", None)
    allocation.pop("candidateSet", None)

    rg = one(data["relayGroups"], "groupId", "RG-3")
    rg.update({
        "stage": "standing resource state (no phase ordering asserted by this contract)",
        "purpose": "connect ACM200 ch15 to the INT check endpoint; test-method-expert selects monitor/measurement configuration",
        "pathRelays": [],
        "relayStates": [{"relay": "K102_PC3", "number": 102, "instance": "K102_PC3_S1", "state": "un-actuated (default conducting path in this chain)", "recordedToken": "NC", "source": "SCH-Connect-Map.json candidatePaths.pinCentric PIN_INT_F_S1 / PIN_INT_S_S1 relayChainUnion"}],
        "forceSenseRelays": {"forceLeg": [], "senseLeg": [], "note": "ACM200 ch15 reaches the selected INT force/sense legs through the default-conducting K102 chain."},
        "conflictStatus": "no shared actuated relay with RG-1 or RG-2; K102 must remain un-actuated",
    })

    summary = data["resourceSummary"]
    summary["sourceTablesSelected"].append({"table": "ACM200", "slot": "S5", "channel": "15", "endpoint": "INT"})
    summary["sourceTablesUnresolved"] = []

    data["evidence"].append({
        "file": "knowledge/hardware/pin-resource-map.md",
        "locator": "INT / SDA -> SDA_INT_ACM -> ACM200; relay notes K43_SDA_INT and K58_INT_PU",
        "class": "active project hardware mapping rule used to choose the INT source table; it does not decide measurement mode or pull-up state",
    })
    data["charterBoundary"]["notDecided"] = [x for x in data["charterBoundary"]["notDecided"] if "observing instrument" not in x]
    data["handoff"]["usableBoundaries"] = [x for x in data["handoff"]["usableBoundaries"] if not x.startswith("INT:")]
    data["handoff"]["usableBoundaries"].append("INT: ACM200 S5 ch15 (FH15 force + SH15 sense), closure set empty; K102_PC3 remains un-actuated. Observation mode, sampling and limits are test-method decisions.")
    data["handoff"]["nonBlockingItems"] = [x for x in data["handoff"]["nonBlockingItems"] if x != "OI-S-03"]
    data["handoff"]["returnRule"] = "Return to test-strategy-architect only if a method needs a route, relay state or register configuration absent from this contract. Measurement mode, timing, sampling, limits and logs are owned by test-method-expert."
    data["verdict"] = "deliverable_ready"
    data["revision"] = {"number": 2, "reason": "Captain correction: INT source-table and route selection is strategy ownership under ROLE_ROUTING.md:8; the original contract incorrectly deferred it.", "previousSha256": before}

    encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    CONTRACT.write_text(encoded, encoding="utf-8")
    after = sha256(CONTRACT)
    record = {
        "artifact": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "beforeSha256": before,
        "afterSha256": after,
        "backup": str(BACKUP.relative_to(ROOT)).replace("\\", "/"),
        "change": "RA-3 and RG-3 now select ACM200 S5 ch15 for INT; K102 stays un-actuated. Method details remain deferred.",
        "evidence": ["team/ROLE_ROUTING.md:8", "knowledge/hardware/pin-resource-map.md INT / SDA -> SDA_INT_ACM -> ACM200", "SCH-Connect-Map.json source-centric ACM200 ch15 reaches INT_F_S1 and INT_S_S1"],
        "timestampUtc": datetime.now(timezone.utc).isoformat(),
    }
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    HANDOFF.write_text(json.dumps({
        "event": "deliverable_ready",
        "fromRole": "test-strategy-architect",
        "nextRole": "test-method-expert",
        "taskId": data["taskId"],
        "tm": "TM109",
        "projectId": "DALI",
        "artifact": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "sha256": after,
        "verdict": "deliverable_ready",
        "permittedNextAction": "Create the method contract using this resource/configuration contract. Do not alter source allocation, relay groups or register delta without returning a routed finding.",
        "blockingItems": [],
        "nonBlockingItems": data["handoff"]["nonBlockingItems"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS", after)

if __name__ == "__main__":
    main()
