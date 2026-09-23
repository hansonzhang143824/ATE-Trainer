#!/usr/bin/env python3
"""Batch-stage Captain gate for one user-requested set of PTC test modes.

``ate_ptc_runner.py`` remains the source of truth for a single TM's gates.
This module never dispatches agents.  It collects those per-TM verdicts and
issues exactly one next-stage handoff for the whole requested batch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
import re
from datetime import datetime, timezone

import ate_ptc_runner as single
import dft_source
import trial_directory


ROOT = Path(__file__).resolve().parents[1]
BATCH_ROOT = ROOT / "team" / "artifacts" / "ptc-batches"
BATCH_TRIAL_ROOT = ROOT / "team" / "artifacts"
FAST_DELIVERY_STATE = "FAST_DELIVERY_PENDING_AUDIT"
FAST_DELIVERY_SKIPPED_STAGES = ("RULE_REVIEW_IMPLEMENTATION",)
FAST_DELIVERY_GATE_FILES = (
    "team/ptc/ptc_stage_registry.json",
    "team/ptc/OUTPUT_CONTRACTS.md",
    "scripts/ate_ptc_runner.py",
    "scripts/ate_ptc_batch_runner.py",
    "scripts/verify_implementation_batch.py",
)

# Stage ranks are NOT restated here. `team/ptc/ptc_stage_registry.json` is the
# single state source; `single.stage_order()` derives the ranking (and folds the
# CORRECTION_STRATEGY alias onto STRATEGY) from that registry, so an edit to the
# registry can never leave a stale table behind in this module.


def normalized_tms(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        tm = value.upper()
        if not tm or tm in result:
            if not tm:
                raise ValueError("TM names must be non-empty")
            continue
        result.append(tm)
    if not result:
        raise ValueError("at least one TM is required")
    return result


def batch_path(batch_id: str) -> Path:
    if not batch_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for char in batch_id):
        raise ValueError("batch id may contain only letters, digits, _ and -")
    return BATCH_ROOT / f"{batch_id}.json"


def range_tms(start: str, end: str) -> list[str]:
    """Select DFT items that exist in the inclusive user-supplied range."""
    match_start = re.fullmatch(r"TM(\d+)", start.upper())
    match_end = re.fullmatch(r"TM(\d+)", end.upper())
    if not match_start or not match_end:
        raise ValueError("范围请写成 TM106 到 TM110。")
    low, high = int(match_start.group(1)), int(match_end.group(1))
    if low > high:
        raise ValueError("范围起点不能大于终点。")
    workbook = dft_source.discover_workbook()
    selected = []
    for name in dft_source.overview_rows(workbook):
        match = re.fullmatch(r"TM(\d+)", name.upper())
        if match and low <= int(match.group(1)) <= high:
            selected.append(name.upper())
    selected.sort(key=lambda name: int(name[2:]))
    if not selected:
        raise ValueError(f"范围 {start.upper()} 到 {end.upper()} 内没有 DFT 测试项目。")
    return selected


def explicit_tms(values: list[str]) -> list[str]:
    """An explicitly named missing TM is a short user-visible error."""
    tms = normalized_tms(values)
    workbook = dft_source.discover_workbook()
    missing = [tm for tm in tms if len(dft_source.rows_for(workbook, tm)) != 1]
    if missing:
        raise ValueError("你点名的 " + "、".join(missing) + " 在 DFT 中没有。")
    return tms

def load_or_create_batch_definition(batch_id: str, supplied_tms: list[str] | None, supplied_range: list[str] | None) -> dict:
    """Freeze one user batch. Fast delivery is stored only in this batch JSON."""
    path = batch_path(batch_id)
    if path.is_file():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            tms = normalized_tms(saved.get("tms", []))
        except (OSError, ValueError, json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"batch definition is invalid: {path}") from exc
        if not isinstance(saved, dict):
            raise ValueError(f"batch definition is invalid: {path}")
        requested = explicit_tms(supplied_tms) if supplied_tms is not None else (range_tms(*supplied_range) if supplied_range else None)
        if requested is not None and requested != tms:
            raise ValueError(f"batch {batch_id} already freezes a different TM list: {', '.join(tms)}")
        saved["tms"] = tms
        return saved
    if supplied_tms is None and supplied_range is None:
        raise ValueError(f"batch {batch_id} does not exist; provide --range or --tms when creating it")
    tms = explicit_tms(supplied_tms) if supplied_tms is not None else range_tms(*supplied_range)
    selection = {"kind": "explicit", "tms": tms} if supplied_tms is not None else {"kind": "range", "start": supplied_range[0].upper(), "end": supplied_range[1].upper()}
    definition = {
        "schemaVersion": 4, "batchId": batch_id, "tms": tms, "selection": selection,
        # New Captain batches never reuse a historical TM trial. Every TM gets
        # an isolated directory under the batch id, while shared global source
        # materials remain governed by INPUT_SYNC.
        "trialDirs": {tm: str((BATCH_TRIAL_ROOT / batch_id / tm.lower()).resolve()) for tm in tms},
    }
    write_batch_definition(definition)
    return definition


def load_or_create_batch(batch_id: str, supplied_tms: list[str] | None, supplied_range: list[str] | None) -> list[str]:
    """Compatibility helper for callers that need only the frozen TM list."""
    return load_or_create_batch_definition(batch_id, supplied_tms, supplied_range)["tms"]


def write_batch_definition(definition: dict) -> None:
    batch_id = definition.get("batchId")
    if not isinstance(batch_id, str):
        raise ValueError("batch definition has no batchId")
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)
    batch_path(batch_id).write_text(json.dumps(definition, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fast_gate_configuration() -> dict:
    """Record exact strict-gate bytes in force before the deferred audit."""
    files = []
    for relative in FAST_DELIVERY_GATE_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"fast delivery cannot start: required gate file is missing: {relative}")
        files.append({"path": relative, "sha256": sha256_bytes(path.read_bytes())})
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"sha256": sha256_bytes(encoded), "files": files}


def is_fast_delivery_active(definition: dict) -> bool:
    return (definition.get("fastDelivery") or {}).get("status") == FAST_DELIVERY_STATE


def fast_delivery_eligibility(items: list[dict]) -> str | None:
    """Nothing before implementation review can be skipped."""
    states = {item["result"].get("state") for item in items}
    if states != {"RULE_REVIEW_IMPLEMENTATION"}:
        return ("fast delivery may start only when every TM is at RULE_REVIEW_IMPLEMENTATION; "
                "it cannot skip input, strategy, method, method review, or implementation")
    return None


def run_minimum_implementation_gate(items: list[dict]) -> tuple[bool, dict]:
    """Run the mandatory signed-code gate for the entire frozen batch."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_implementation_batch.py"), *(item["trial"] for item in items)],
        cwd=ROOT, text=True, capture_output=True, encoding="utf-8",
    )
    raw = (result.stdout + result.stderr).strip()
    try:
        report = json.loads(result.stdout) if result.stdout.strip() else {"rawOutput": raw}
    except json.JSONDecodeError:
        report = {"rawOutput": raw}
    report["exitCode"] = result.returncode
    return result.returncode == 0 and report.get("status") == "PASS", report


def activate_fast_delivery(definition: dict, items: list[dict], captain_authorized: bool) -> None:
    """Persist a Captain-authorized exception only after the code contract passes."""
    if not captain_authorized:
        raise ValueError("fast delivery requires Captain's explicit --captain-authorized flag")
    if is_fast_delivery_active(definition):
        return
    if definition.get("fastDelivery"):
        raise ValueError("fast delivery was already used for this batch; use --resume-audit instead of enabling it again")
    ineligible = fast_delivery_eligibility(items)
    if ineligible:
        raise ValueError(ineligible)
    gate_ok, gate_report = run_minimum_implementation_gate(items)
    if not gate_ok:
        raise ValueError("fast delivery cannot start because the mandatory implementation check failed: " + json.dumps(gate_report, ensure_ascii=False))
    definition["fastDelivery"] = {
        "status": FAST_DELIVERY_STATE,
        "enabledBy": "captain",
        "enabledAt": datetime.now(timezone.utc).isoformat(),
        "preEnableGateConfiguration": fast_gate_configuration(),
        "skippedStages": list(FAST_DELIVERY_SKIPPED_STAGES),
        "minimumImplementationGate": gate_report,
    }
    write_batch_definition(definition)


def compile_is_ready(item: dict) -> bool:
    trial = Path(item["trial"])
    return (single.is_ready(trial / "compile" / "deliverable-ready.json", "COMPILE")
            and single.compile_is_current(trial / "compile" / "build-report.json"))


def aggregate_fast_delivery(definition: dict, items: list[dict]) -> dict:
    """Allow only compile, then hold a clearly marked deferred-audit state."""
    fast = definition["fastDelivery"]
    ineligible = fast_delivery_eligibility(items)
    if ineligible:
        return {"state": "BLOCKED", "dispatch": None, "reason": "fast delivery no longer has a current implementation: " + ineligible,
                "tmStates": [compact(item) for item in items]}
    current_config = fast_gate_configuration()
    if current_config["sha256"] != (fast.get("preEnableGateConfiguration") or {}).get("sha256"):
        return {"state": "BLOCKED", "dispatch": None,
                "reason": "strict gate configuration changed after fast delivery was enabled; resume audit cannot prove the original boundary",
                "tmStates": [compact(item) for item in items]}
    gate_ok, gate_report = run_minimum_implementation_gate(items)
    if not gate_ok:
        return {"state": "BLOCKED", "dispatch": None,
                "reason": "mandatory implementation check failed after fast delivery was enabled",
                "minimumImplementationGate": gate_report,
                "tmStates": [compact(item) for item in items]}
    if all(compile_is_ready(item) for item in items):
        return {"state": FAST_DELIVERY_STATE, "dispatch": None,
                "reason": "compile passed; independent implementation review is pending",
                "skippedStages": list(FAST_DELIVERY_SKIPPED_STAGES),
                "nextAction": "run --resume-audit --batch <id>",
                "minimumImplementationGate": gate_report,
                "tmStates": [compact(item) for item in items]}
    registry, error = single.load_stage_registry()
    if error or registry is None:
        return {"state": "BLOCKED", "dispatch": None, "reason": error or "stage registry unavailable"}
    compile_config = registry["stages"]["COMPILE"]
    return {"state": FAST_DELIVERY_STATE, "dispatch": compile_config["owner"], "nextRequiredStage": "COMPILE",
            "registeredStage": "COMPILE", "registeredOwner": compile_config["owner"], "registeredGate": compile_config["gate"],
            "targetTms": [item["tm"] for item in items], "trialDirs": [item["trial"] for item in items],
            "reason": "mandatory implementation check passed; compile is required before deferred audit",
            "skippedStages": list(FAST_DELIVERY_SKIPPED_STAGES), "minimumImplementationGate": gate_report,
            "tmStates": [compact(item) for item in items]}


def resume_audit(definition: dict) -> None:
    """Restore strict mode at exactly the independent implementation review."""
    fast = definition.get("fastDelivery") or {}
    if fast.get("status") != FAST_DELIVERY_STATE:
        raise ValueError("batch is not in FAST_DELIVERY_PENDING_AUDIT")
    if fast_gate_configuration()["sha256"] != (fast.get("preEnableGateConfiguration") or {}).get("sha256"):
        raise ValueError("strict gate configuration changed since fast delivery was enabled; do not resume against different gates")
    fast["status"] = "AUDIT_RESUMED"
    fast["resumedAt"] = datetime.now(timezone.utc).isoformat()
    fast["resumeStage"] = "RULE_REVIEW_IMPLEMENTATION"
    definition["fastDelivery"] = fast
    write_batch_definition(definition)

def trial_for(definition: dict, tm: str) -> Path:
    """Resolve the frozen per-batch trial directory without history lookup."""
    registered = (definition.get("trialDirs") or {}).get(tm)
    if isinstance(registered, str) and registered:
        return trial_directory.resolve(tm, registered)
    # Compatibility only for pre-schema-4 batches created before isolation.
    return trial_directory.resolve(tm)

def entry(tm: str, trial: Path | None = None) -> dict:
    trial = trial or trial_directory.resolve(tm)
    return {"tm": tm, "trial": str(trial), "result": single.stage(trial, tm)}

def items_for(definition: dict) -> list[dict]:
    return [entry(tm, trial_for(definition, tm)) for tm in definition["tms"]]


def registry_metadata(result: dict) -> dict:
    """Keep the single-TM registry binding visible in batch handoffs."""
    return {
        key: result[key]
        for key in ("registeredStage", "registeredOwner", "registeredGate")
        if key in result
    }


def compact(item: dict) -> dict:
    result = item["result"]
    return {
        "tm": item["tm"],
        "trial": item["trial"],
        "state": result.get("state"),
        "dispatch": result.get("dispatch"),
        "reason": result.get("reason"),
        **registry_metadata(result),
    }


def aggregate(items: list[dict]) -> dict:
    """Return a single batch handoff without selecting or dispatching agents."""
    blocked = [compact(item) for item in items if item["result"].get("state") in {"BLOCKED", "PROJECT_INFO"}]
    if blocked:
        return {"state": "BLOCKED", "dispatch": None,
                "reason": "有测试项目未通过当前门禁。",
                "blockedTms": blocked, "tmStates": [compact(item) for item in items]}

    registry, registry_error = single.load_stage_registry()
    if registry is None:
        return {"state": "BLOCKED", "dispatch": None,
                "reason": registry_error or "PTC stage registry is unavailable",
                "tmStates": [compact(item) for item in items], "inputs": [str(single.STAGE_REGISTRY_PATH)]}
    order = single.stage_order(registry)

    unknown = [compact(item) for item in items if item["result"].get("state") not in order]
    if unknown:
        return {"state": "BLOCKED", "dispatch": None,
                "reason": "检测到不支持的阶段状态。",
                "blockedTms": unknown, "tmStates": [compact(item) for item in items]}

    incomplete = [item for item in items if item["result"].get("state") != "COMPLETE"]
    if not incomplete:
        return {"state": "COMPLETE", "dispatch": None,
                "reason": "本批次全部编译通过。",
                "tmStates": [compact(item) for item in items]}

    current_rank = min(order[item["result"]["state"]] for item in incomplete)
    current = [item for item in incomplete if order[item["result"]["state"]] == current_rank]
    waiting = [compact(item) for item in incomplete if item not in current]

    # INPUT_SYNC may name DFT and schematic together.  Collapse all TM needs
    # into one role handoff per source role, with schematic generated once.
    if current_rank == order["INPUT_SYNC"]:
        needs: dict[str, list[dict]] = defaultdict(list)
        manual_prepare: list[dict] = []
        for item in current:
            roles = single.dispatch_roles(item["result"])
            if roles:
                for role in roles:
                    needs[role].append(item)
            else:
                manual_prepare.append(item)
        if manual_prepare:
            return {"state": "INPUT_SYNC", "dispatch": None,
                    "action": "先准备这些 TM 的输入，再继续。",
                    "targetTms": [item["tm"] for item in current],
                    "waitingTms": waiting, "tmStates": [compact(item) for item in items], **registry_metadata(current[0]["result"])}
        dispatches = [{"role": role, "tms": [item["tm"] for item in role_items],
                       "trialDirs": [item["trial"] for item in role_items]}
                      for role, role_items in sorted(needs.items())]
        return {"state": "INPUT_SYNC", "dispatch": None,
                "dispatches": dispatches,
                "reason": "先完成本批次缺失的输入材料。",
                "waitingTms": waiting, "tmStates": [compact(item) for item in items], **registry_metadata(current[0]["result"])}

    # Every stage reads the plural role list, so a per-TM result that names work
    # only through `dispatchableRoles` can no longer end its stage early.
    needs = defaultdict(list)
    for entry in current:
        for role in single.dispatch_roles(entry["result"]):
            needs[role].append(entry)
    if not needs:
        return {"state": "BLOCKED", "dispatch": None,
                "reason": "当前阶段无法确定唯一的处理角色。",
                "blockedTms": [compact(item) for item in current],
                "tmStates": [compact(item) for item in items]}
    roles = sorted(needs)
    # The same pending work as a per-role dispatch list, so the Captain entry
    # hook can start each role through its pinned expert profile (receipt,
    # persona, boundary) exactly like INPUT_SYNC; roles without a pinned
    # profile keep the historical label dispatch and stay visible in
    # `unpinnedRoles`.
    dispatches = [
        {"role": role,
         "tms": [entry["tm"] for entry in needs[role]],
         "trialDirs": [entry["trial"] for entry in needs[role]],
         "stage": current[0]["result"]["state"]}
        for role in roles
    ]
    return {"state": current[0]["result"]["state"],
            # The singular field stays empty when more than one role is pending,
            # so no caller can mistake one of them for the whole stage's owner.
            "dispatch": roles[0] if len(roles) == 1 else None,
            "dispatchableRoles": roles,
            "dispatches": dispatches,
            "targetTms": [item["tm"] for item in current],
            "trialDirs": [item["trial"] for item in current],
            "reason": "处理本阶段尚未完成的测试项目。",
            "waitingTms": waiting, "tmStates": [compact(item) for item in items], **registry_metadata(current[0]["result"])}


def prepare(tms: list[str]) -> list[dict]:
    """Legacy compatibility: resolve history only for pre-isolation callers."""
    return prepare_definition({"tms": tms})

def prepare_definition(definition: dict) -> list[dict]:
    prepared = []
    for tm in definition["tms"]:
        trial = trial_for(definition, tm)
        command = [sys.executable, str(ROOT / "scripts" / "prepare_input_sync_v2.py"),
                   "--tm", tm, "--trial-dir", str(trial)]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        prepared.append({"tm": tm, "trial": str(trial), "exitCode": result.returncode,
                         "output": (result.stdout + result.stderr).strip()})
    return prepared


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", "--batch", dest="batch_id", required=True, help="persistent identifier for this user-requested TM batch")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--tms", nargs="+", help="explicitly named TMs; an absent TM is an error")
    selector.add_argument("--range", nargs=2, metavar=("START", "END"), help="inclusive TM range; absent numbers are skipped")
    parser.add_argument("--command", choices=("next", "prepare-input"), default="next")
    parser.add_argument("--enable-fast-delivery", action="store_true", help="Captain: defer only implementation review for this existing batch")
    parser.add_argument("--captain-authorized", action="store_true", help="records Captain's explicit per-batch authorization")
    parser.add_argument("--resume-audit", action="store_true", help="restore strict mode at the deferred implementation review")
    parser.add_argument("--details", action="store_true", help="include per-TM diagnostic detail")
    args = parser.parse_args()
    try:
        if args.enable_fast_delivery and args.resume_audit:
            raise ValueError("choose either --enable-fast-delivery or --resume-audit")
        if args.captain_authorized and not args.enable_fast_delivery:
            raise ValueError("--captain-authorized is valid only with --enable-fast-delivery")
        batch = load_or_create_batch_definition(args.batch_id, args.tms, args.range)
        tms = batch["tms"]
        definition_path = str(batch_path(args.batch_id))
        items = items_for(batch)
        if args.enable_fast_delivery:
            activate_fast_delivery(batch, items, args.captain_authorized)
        if args.resume_audit:
            resume_audit(batch)
        prepared = prepare_definition(batch) if args.command == "prepare-input" else []
        output = aggregate_fast_delivery(batch, items) if is_fast_delivery_active(batch) else aggregate(items)
    except ValueError as exc:
        output = {"state": "BLOCKED", "dispatch": None, "reason": str(exc)}
        prepared = []
        definition_path = None
    if prepared:
        output["command"] = "prepare-input"
        output["prepareResults"] = prepared
    if not args.details:
        output.pop("tmStates", None)
        if isinstance(output.get("waitingTms"), list):
            output["waitingTms"] = [item["tm"] if isinstance(item, dict) else item for item in output["waitingTms"]]
        if isinstance(output.get("blockedTms"), list):
            output["blockedTms"] = [item["tm"] if isinstance(item, dict) else item for item in output["blockedTms"]]
    output["batchId"] = args.batch_id
    if definition_path is not None and args.details:
        output["batchDefinition"] = definition_path
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 2 if output.get("state") == "BLOCKED" else 0

