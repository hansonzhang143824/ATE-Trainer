#!/usr/bin/env python3
"""Internal ATE Captain entry for conversational DALI PTC deliveries.

A user opens ATE Captain and names TM items or one TM range. Captain calls
open_new_delivery() once, then advance_batch() after each role handoff. Users
do not run this module or provide batch identifiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Callable

import ate_ptc_batch_runner as batch
import project_info


# A TM mention may sit directly against CJK text ("写TM103的code"), so a
# Unicode  boundary is wrong here: CJK code points count as word characters.
# Use ASCII-only lookarounds instead, and accept the "TM103/106/425" shorthand.
_TM_TOKEN = r"TM\s*(\d+(?:\s*/\s*\d+)*)"
_RANGE = re.compile(
    r"(?<![A-Za-z0-9_])TM\s*(\d+)\s*(?:到|至|~|～|—|－|-)\s*(?:TM\s*)?(\d+)(?![0-9])",
    re.IGNORECASE,
)
_TM = re.compile(r"(?<![A-Za-z0-9_])" + _TM_TOKEN, re.IGNORECASE)


def parse_scope(text: str) -> dict:
    """Accept an explicit TM list or a single inclusive TM range."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("请说明测试项目，例如“跑 TM102、TM105”或“跑 TM106 到 TM110”。")
    text = unicodedata.normalize("NFKC", text)
    ranges = list(_RANGE.finditer(text))
    if len(ranges) > 1:
        raise ValueError("一次只说一个连续范围；例如“TM106 到 TM110”。")
    if ranges:
        match = ranges[0]
        low, high = int(match.group(1)), int(match.group(2))
        if low > high:
            raise ValueError("范围起点不能大于终点。")
        return {"kind": "range", "start": f"TM{low}", "end": f"TM{high}"}

    tms: list[str] = []
    for match in _TM.finditer(text):
        for number in re.split(r"\s*/\s*", match.group(1)):
            tm = f"TM{int(number)}"
            if tm not in tms:
                tms.append(tm)
    if not tms:
        raise ValueError("请说明测试项目，例如“跑 TM102、TM105”或“跑 TM106 到 TM110”。")
    return {"kind": "explicit", "tms": tms}


def _project_binding(info: dict) -> dict:
    raw = project_info.PROJECT_INFO.read_bytes()
    return {
        "project": info.get("project"),
        "projectDir": info.get("projectDir"),
        "inputRoot": (info.get("roots") or {}).get("input"),
        "inputsDigest": (info.get("approval") or {}).get("inputsDigest"),
        "projectInfoSha256": hashlib.sha256(raw).hexdigest(),
    }


def _new_batch_id(scope: dict, now: datetime | None = None) -> str:
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    suffix = (
        f"{scope['start'].lower()}-{scope['end'].lower()}"
        if scope["kind"] == "range"
        else "-".join(tm.lower() for tm in scope["tms"])
    )
    base = f"dali-{stamp}-{suffix}"
    candidate, number = base, 2
    while batch.batch_path(candidate).exists():
        candidate = f"{base}-{number}"
        number += 1
    return candidate


def _selection_args(scope: dict) -> tuple[list[str] | None, list[str] | None]:
    return (
        (None, [scope["start"], scope["end"]])
        if scope["kind"] == "range"
        else (list(scope["tms"]), None)
    )


def _load_approved_project() -> tuple[dict | None, dict | None]:
    info = project_info.load()
    problems = project_info.problems(info)
    if problems:
        return None, {
            "state": "PROJECT_INFO",
            "dispatch": None,
            "reason": "项目路径还没有确认。",
            "problems": problems,
            "action": "请在 Captain 的项目确认窗口中确认或修改项目路径。",
            "evidence": str(project_info.PROJECT_INFO),
        }
    return info, None


def _with_context(output: dict, definition: dict, *, command: str, prepared: list[dict] | None = None) -> dict:
    output.update({
        "batchId": definition["batchId"],
        "batchDefinition": str(batch.batch_path(definition["batchId"])),
        "selection": definition["selection"],
        "project": (definition.get("projectBinding") or {}).get("project"),
        "command": command,
    })
    if prepared is not None:
        output["prepareResults"] = prepared
    return output


def delivery_execution_scope(text: str) -> dict:
    text = unicodedata.normalize("NFKC", text)
    mentions_dft = bool(re.search(r"DFT\s*(?:expert|专家)?", text, re.IGNORECASE))
    dft_only = mentions_dft and bool(re.search(
        r"(?:只|仅)\s*(?:(?:执行|运行|跑|做)(?:到|性)?)?\s*DFT\s*(?:expert|专家)?|"
        r"(?:其余|其他).{0,12}不执行|"
        r"(?:only\s+(?:run\s+)?DFT|DFT\s+(?:expert\s+)?only)", text, re.IGNORECASE))
    return {"sourceRoles": ["dft-expert"] if dft_only else ["dft-expert", "schematic-expert"],
            "stopAfter": "INPUT_SYNC" if dft_only else None}


def _initial_source_dispatch(definition: dict) -> dict:
    trials = [str(batch.trial_for(definition, tm)) for tm in definition["tms"]]
    execution_scope = definition.get("executionScope") or delivery_execution_scope("")
    return {
        "state": "INPUT_SYNC", "dispatch": None,
        "dispatches": [
            {"role": role, "tms": list(definition["tms"]), "trialDirs": trials}
            for role in execution_scope["sourceRoles"]
        ],
        "targetTms": list(definition["tms"]),
        "trialDirs": trials,
        "executionScope": execution_scope,
        "reason": "new batch: verify the canonical DFT and schematic materials before later stages",
    }

def _aggregate_with_default_fast(definition: dict, items: list[dict]) -> dict:
    """Enable fast delivery only after its prerequisite strict stages pass.

    Every newly created Captain batch records this default. It cannot skip any
    earlier gate. Strict audit is never resumed by this entry point.
    """
    policy = definition.get("captainFastDeliveryPolicy") or {}
    if (
        policy.get("defaultEnabled") is True
        and not definition.get("fastDelivery")
        and batch.fast_delivery_eligibility(items) is None
    ):
        batch.activate_fast_delivery(definition, items, captain_authorized=True)
    return batch.aggregate_fast_delivery(definition, items) if batch.is_fast_delivery_active(definition) else batch.aggregate(items)


def advance_batch(
    batch_id: str,
    *,
    prepare: Callable[[list[str]], list[dict]] | None = None,
    stage_entry: Callable[[str], dict] | None = None,
) -> dict:
    """Captain-internal continuation after one role's terminal handoff."""
    info, problem = _load_approved_project()
    if problem:
        return problem
    try:
        definition = batch.load_or_create_batch_definition(batch_id, None, None)
        binding = definition.get("projectBinding") or {}
        if binding.get("projectInfoSha256") != _project_binding(info).get("projectInfoSha256"):
            raise ValueError("当前项目配置已变化。请先在 Captain 中确认项目，再开启新的批次。")
        if (definition.get("executionScope") or {}).get("stopAfter") == "INPUT_SYNC":
            return _with_context({"state": "INPUT_SYNC", "dispatch": None, "dispatches": [],
                                  "executionScope": definition["executionScope"],
                                  "reason": "用户限定只执行 DFT；禁止自动进入后续阶段。"},
                                 definition, command="captain-scope-stop")
        entries = stage_entry or batch.entry
        prepared = None
        if definition.pop("initialSourceDispatchPending", False):
            prepared = prepare(definition["tms"]) if prepare is not None else batch.prepare_definition(definition)
            batch.write_batch_definition(definition)
        items = ([entries(tm) for tm in definition["tms"]] if stage_entry is not None else batch.items_for(definition))
        output = _aggregate_with_default_fast(definition, items)

        # A source role has completed when INPUT_SYNC has no role to dispatch.
        # Captain refreshes every manifest once, then reads the next gate.
        if output.get("state") == "INPUT_SYNC" and not output.get("dispatches"):
            prepared = prepare(definition["tms"]) if prepare is not None else batch.prepare_definition(definition)
            items = ([entries(tm) for tm in definition["tms"]] if stage_entry is not None else batch.items_for(definition))
            output = _aggregate_with_default_fast(definition, items)
    except ValueError as exc:
        return {"state": "BLOCKED", "dispatch": None, "reason": str(exc)}
    return _with_context(output, definition, command="captain-advance-batch", prepared=prepared)


def update_delivery_scope(batch_id: str, user_text: str) -> dict:
    """Narrow an unadvanced batch after a same-session user correction."""
    info, problem = _load_approved_project()
    if problem:
        return problem
    try:
        definition = batch.load_or_create_batch_definition(batch_id, None, None)
        binding = definition.get("projectBinding") or {}
        if binding.get("projectInfoSha256") != _project_binding(info).get("projectInfoSha256"):
            raise ValueError("当前项目配置已变化。请先确认项目配置。")
        requested = delivery_execution_scope(user_text)
        if requested.get("stopAfter") != "INPUT_SYNC":
            raise ValueError("本次修正没有明确限定只执行 DFT expert。")
        if definition.get("initialSourceDispatchPending") is not True:
            raise ValueError("当前批次已离开初始 INPUT_SYNC，不能在原批次缩小范围。")
        definition["executionScope"] = requested
        definition["captainEntry"]["scopeCorrectedAt"] = datetime.now().isoformat(timespec="seconds")
        batch.write_batch_definition(definition)
        output = {
            "state": "INPUT_SYNC", "dispatch": None, "dispatches": [],
            "targetTms": list(definition["tms"]), "executionScope": requested,
            "reason": "用户已将当前批次收窄为只执行 DFT expert。",
        }
    except ValueError as exc:
        return {"state": "BLOCKED", "dispatch": None, "reason": str(exc)}
    return _with_context(output, definition, command="captain-update-scope")


def open_new_delivery(
    user_text: str,
    *,
    now: datetime | None = None,
    prepare: Callable[[list[str]], list[dict]] | None = None,
    stage_entry: Callable[[str], dict] | None = None,
) -> dict:
    """Create a unique current-project batch and run its first INPUT_SYNC."""
    info, problem = _load_approved_project()
    if problem:
        return problem
    try:
        scope = parse_scope(user_text)
        tms_arg, range_arg = _selection_args(scope)
        batch_id = _new_batch_id(scope, now)
        definition = batch.load_or_create_batch_definition(batch_id, tms_arg, range_arg)
        definition["projectBinding"] = _project_binding(info)
        definition["executionScope"] = delivery_execution_scope(user_text)
        definition["captainEntry"] = {
            "kind": "conversation",
            "openedAt": (now or datetime.now()).isoformat(timespec="seconds"),
            "scope": scope,
        }
        # Fast delivery is the default for new Captain batches, but activation
        # waits for RULE_REVIEW_IMPLEMENTATION. Strict audit is never resumed
        # here; later resume needs a fresh user instruction to Captain.
        definition["captainFastDeliveryPolicy"] = {
            "defaultEnabled": True,
            "strictAuditResume": "user_explicit_instruction_required",
        }
        definition["initialSourceDispatchPending"] = True
        batch.write_batch_definition(definition)

        # A new batch always starts with source specialists. It never derives its
        # first state from an old TM trial or from CURRENT_STATUS.
        prepared = []
        output = _initial_source_dispatch(definition)
    except ValueError as exc:
        return {"state": "BLOCKED", "dispatch": None, "reason": str(exc)}
    return _with_context(output, definition, command="captain-open-delivery", prepared=prepared)


def main() -> int:
    parser = argparse.ArgumentParser(description="Internal ATE Captain conversational entry")
    parser.add_argument("--request", help="original user delivery request")
    parser.add_argument("--continue-batch", help="internal Captain continuation")
    parser.add_argument("--scope-update-batch", help="existing batch narrowed by a same-session correction")
    parser.add_argument("--scope-text", help="the correcting user text")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.request, args.continue_batch, args.scope_update_batch)) != 1:
        parser.error("provide exactly one internal action")
    if args.scope_update_batch and not args.scope_text:
        parser.error("--scope-update-batch requires --scope-text")
    result = (open_new_delivery(args.request) if args.request else
              advance_batch(args.continue_batch) if args.continue_batch else
              update_delivery_scope(args.scope_update_batch, args.scope_text))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("state") in {"BLOCKED", "PROJECT_INFO"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
