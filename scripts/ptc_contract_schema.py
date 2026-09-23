"""Shared, contract-driven validation primitives for DALI PTC artifacts.

The module validates declared test families and publisher forms. It never assumes
a voltage, sweep direction, trigger, API call, or result count beyond the
contract's own declaration.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ptc_trim_validation import validate_trim_execution_declaration

METHOD_FAMILIES = frozenset({"direct_measurement", "scan", "trim"})
PUBLISHER_KINDS = frozenset({"set_test_result", "trim_node_execute"})
DECLARATION_STATES = frozenset({"DECLARED", "NOT_DECLARED", "NOT_APPLICABLE", "AMBIGUOUS"})
RESOLVED_SCAN_STATES = frozenset({"DECLARED", "DFT_HELPER_DECLARED", "USER_DECIDED", "RESOLVED"})
# Project rule approved by the user: trigger labels follow physical sweep direction.
USER_SCAN_DIRECTION_RESULTS = {"RISING": "FALLING", "FALLING": "RISING"}


def _mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _error(errors: list[str], path: str, detail: str) -> None:
    errors.append(f"{path} {detail}")


def _require_mapping(value: Any, path: str, errors: list[str]) -> Mapping[str, Any] | None:
    if not _mapping(value):
        _error(errors, path, "must be an object")
        return None
    return value


def _require_state(value: Any, path: str, errors: list[str], *, allowed: frozenset[str] = DECLARATION_STATES) -> str | None:
    body = _require_mapping(value, path, errors)
    if body is None:
        return None
    state = body.get("state")
    if state not in allowed:
        _error(errors, f"{path}.state", f"must be one of {', '.join(sorted(allowed))}")
        return None
    return state


def classify_test_condition(condition: Mapping[str, Any]) -> str | None:
    """Return the family implied by a DFT semantic handoff.

    A trim is first because it may contain a direct voltage measurement. A ramp
    makes the remaining family a scan.
    """
    if condition.get("isTrim") is True:
        return "trim"
    if condition.get("hasRamp") is True:
        return "scan"
    if condition.get("hasRamp") is False:
        return "direct_measurement"
    return None


def validate_test_condition(condition: Any) -> list[str]:
    """Validate the DFT semantic handoff against the 6-field contract.

    Mirrors team/expert-profiles/ptc-dft-expert/output-contract.schema.json
    (x-gate-sync items 05-09): identity/isTrim/powerSequence/registerFieldIntent/
    measurement/involvedPins are required; the remaining fields are optional and
    are recorded verbatim in rawIntent instead of failing validation.
    """
    errors: list[str] = []
    body = _require_mapping(condition, "testCondition", errors)
    if body is None:
        return errors

    if not _nonempty_string(body.get("identity")):
        _error(errors, "testCondition.identity", "must be a non-empty string (Name)")
    if not isinstance(body.get("isTrim"), bool):
        _error(errors, "testCondition.isTrim", "must be a boolean")

    power = body.get("powerSequence")
    if not isinstance(power, list) or not power:
        _error(errors, "testCondition.powerSequence", "must be a non-empty array of vset/iset stages")
    else:
        for index, stage in enumerate(power):
            label = f"testCondition.powerSequence[{index}]"
            if not isinstance(stage, dict):
                _error(errors, label, "must be a mapping")
                continue
            if stage.get("cmd") not in {"vset", "iset"}:
                _error(errors, f"{label}.cmd", "must be vset or iset")
            if not _nonempty_string(stage.get("pin")):
                _error(errors, f"{label}.pin", "must be a non-empty string")
            value = stage.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                _error(errors, f"{label}.value", "must be a number")
            if not _nonempty_string(stage.get("pluseTime")):
                _error(errors, f"{label}.pluseTime", "must be a non-empty string")
            status = stage.get("status")
            if isinstance(status, bool) or not isinstance(status, int) or status < 0:
                _error(errors, f"{label}.status", "must be an integer >= 0")
            ramp = stage.get("rampFrom")
            if ramp is not None and (isinstance(ramp, bool) or not isinstance(ramp, (int, float))):
                _error(errors, f"{label}.rampFrom", "must be a number or null")

    fields = body.get("registerFieldIntent")
    if not isinstance(fields, list):
        _error(errors, "testCondition.registerFieldIntent", "must be an array (may be empty)")
    else:
        for index, entry in enumerate(fields):
            label = f"testCondition.registerFieldIntent[{index}]"
            if not isinstance(entry, dict):
                _error(errors, label, "must be a mapping")
                continue
            if entry.get("kind") not in {"field", "en_tm"}:
                _error(errors, f"{label}.kind", "must be field or en_tm")
            if not _nonempty_string(entry.get("raw")):
                _error(errors, f"{label}.raw", "must be a non-empty string")

    if not _nonempty_string(body.get("measurement")):
        _error(errors, "testCondition.measurement", "must be a non-empty string (V/I/R/Toggle syntax per rules file)")

    pins = body.get("involvedPins")
    if not isinstance(pins, list) or not pins or not all(_nonempty_string(pin) for pin in pins):
        _error(errors, "testCondition.involvedPins", "must be a non-empty list of pin names")
    return errors

def validate_method_contract(contract: Any, strategy_sha: str | None = None) -> list[str]:
    """Validate a METHOD contract from its declared family and publisher form."""
    errors: list[str] = []
    body = _require_mapping(contract, "contract", errors)
    if body is None:
        return errors
    if body.get("stage") != "METHOD":
        _error(errors, "stage", "must be METHOD")
    if body.get("verdict") != "deliverable_ready":
        _error(errors, "verdict", "must be deliverable_ready")
    if not _nonempty_string(body.get("tm")):
        _error(errors, "tm", "is missing")
    if strategy_sha is not None and (body.get("signedInputs") or {}).get("strategyContractSha256") != strategy_sha:
        _error(errors, "signedInputs.strategyContractSha256", "is missing or stale")

    family = body.get("methodFamily")
    if family not in METHOD_FAMILIES:
        _error(errors, "methodFamily", f"must be one of {', '.join(sorted(METHOD_FAMILIES))}")
    boundary = _require_mapping(body.get("resourceBoundary"), "resourceBoundary", errors)
    if boundary is not None and not isinstance(boundary.get("allocations"), list):
        _error(errors, "resourceBoundary.allocations", "must be a list")
    phases = body.get("methodPhases")
    if not isinstance(phases, list) or not phases:
        _error(errors, "methodPhases", "must be a non-empty list")
    plan = _require_mapping(body.get("measurementPlan"), "measurementPlan", errors)
    down = _require_mapping(body.get("powerDownPlan"), "powerDownPlan", errors)
    if down is not None:
        if not isinstance(down.get("actions"), list) or not down["actions"]:
            _error(errors, "powerDownPlan.actions", "must be a non-empty list")
        if not _nonempty_string(down.get("safeEndState")):
            _error(errors, "powerDownPlan.safeEndState", "must be a non-empty string")
    if plan is None:
        return errors

    publisher = _require_mapping(plan.get("resultPublisher"), "measurementPlan.resultPublisher", errors)
    publisher_kind: str | None = None
    if publisher is not None:
        publisher_kind = publisher.get("kind")
        if publisher_kind not in PUBLISHER_KINDS:
            _error(errors, "measurementPlan.resultPublisher.kind", f"must be one of {', '.join(sorted(PUBLISHER_KINDS))}")
        count = publisher.get("minimumCount")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            _error(errors, "measurementPlan.resultPublisher.minimumCount", "must be an integer of at least 1")
        names = publisher.get("resultNames")
        if not isinstance(names, list) or not all(_nonempty_string(name) for name in names):
            _error(errors, "measurementPlan.resultPublisher.resultNames", "must be a list of non-empty names")
        elif isinstance(count, int) and not isinstance(count, bool) and len(names) < count:
            _error(errors, "measurementPlan.resultPublisher.resultNames", "must contain at least minimumCount names")

    trim_execution = plan.get("trimExecution")
    if publisher_kind == "trim_node_execute":
        trim = _require_mapping(trim_execution, "measurementPlan.trimExecution", errors)
        if trim is not None:
            validate_trim_execution_declaration(trim, errors)
    elif family == "trim":
        _error(errors, "measurementPlan.resultPublisher.kind", "must be trim_node_execute for methodFamily trim")
    elif trim_execution is not None:
        _error(errors, "measurementPlan.trimExecution", "is only valid with trim_node_execute")

    log_plan = _require_mapping(body.get("logPlan"), "logPlan", errors)
    required_results: list[str] = []
    if log_plan is not None:
        raw_results = log_plan.get("requiredResults")
        if not isinstance(raw_results, list) or not raw_results or not all(_nonempty_string(item) for item in raw_results):
            _error(errors, "logPlan.requiredResults", "must be a non-empty list of result names")
        else:
            required_results = list(raw_results)
    if publisher is not None and required_results and publisher.get("resultNames") != required_results:
        _error(errors, "logPlan.requiredResults", "must match measurementPlan.resultPublisher.resultNames in order")

    scan = plan.get("scanRangeResolution")
    if family == "scan":
        scan_body = _require_mapping(scan, "measurementPlan.scanRangeResolution", errors)
        if scan_body is not None and scan_body.get("state") not in RESOLVED_SCAN_STATES:
            _error(errors, "measurementPlan.scanRangeResolution.state", "must declare a resolved scan range")
        sweeps = plan.get("sweeps")
        if not isinstance(sweeps, list) or not sweeps:
            _error(errors, "measurementPlan.sweeps", "must declare at least one sweep")
        elif publisher is not None:
            declared_results = set(publisher.get("resultNames") or [])
            for index, sweep in enumerate(sweeps):
                if not _mapping(sweep):
                    _error(errors, f"measurementPlan.sweeps[{index}]", "must be an object")
                    continue
                for key in ("direction", "result"):
                    if not _nonempty_string(sweep.get(key)):
                        _error(errors, f"measurementPlan.sweeps[{index}].{key}", "must be a non-empty string")
                for key in ("fromV", "toV"):
                    if not isinstance(sweep.get(key), (int, float)) or isinstance(sweep.get(key), bool):
                        _error(errors, f"measurementPlan.sweeps[{index}].{key}", "must be numeric")
                if sweep.get("result") not in declared_results:
                    _error(errors, f"measurementPlan.sweeps[{index}].result", "must be declared by resultPublisher")
    elif scan is not None:
        scan_body = _require_mapping(scan, "measurementPlan.scanRangeResolution", errors)
        if scan_body is not None and scan_body.get("state") in RESOLVED_SCAN_STATES:
            _error(errors, "measurementPlan.scanRangeResolution", "declares a scan while methodFamily is not scan")
    return errors


def method_execution_profile(contract: Any) -> tuple[dict[str, Any] | None, list[str]]:
    """Return the executable shape declared by a valid method contract.

    Consumers use this instead of maintaining their own method-family, publisher,
    and scan branching.  The profile contains only contract declarations; it never
    supplies test-specific defaults.
    """
    errors = validate_method_contract(contract)
    if errors or not _mapping(contract):
        return None, errors
    plan = contract["measurementPlan"]
    publisher = plan["resultPublisher"]
    return {
        "family": contract["methodFamily"],
        "publisher": {
            "kind": publisher["kind"],
            "minimumCount": publisher["minimumCount"],
            "resultNames": list(publisher["resultNames"]),
            "executeCallPrefix": (plan.get("trimExecution") or {}).get("executeCallPrefix"),
        },
        "sweeps": list(plan.get("sweeps") or []),
        "measurementPin": plan.get("measurementPin"),
        "quantity": plan.get("quantity"),
    }, []


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_method_dft_alignment(contract: Any, condition: Any, *, profile: Mapping[str, Any] | None = None) -> list[str]:
    """Validate METHOD against its signed DFT semantic handoff.

    Values, result names, directions and result counts come from the signed
    contract.  This function only checks that the method did not contradict the
    DFT handoff or its own declared execution profile.
    """
    errors = validate_test_condition(condition)
    if profile is None:
        profile, method_errors = method_execution_profile(contract)
        errors.extend(method_errors)
    if profile is None or not _mapping(condition):
        return errors

    implied = classify_test_condition(condition)
    if implied is None:
        _error(errors, "testCondition", "does not declare a method family")
    elif profile["family"] != implied:
        _error(errors, "methodFamily", f"{profile['family']!r} conflicts with DFT-implied {implied!r}")

    measurement = condition.get("measurement") or {}
    if profile.get("measurementPin") != measurement.get("check"):
        _error(errors, "measurementPlan.measurementPin", "differs from testCondition.measurement.check")
    if profile.get("quantity") != measurement.get("quantity"):
        _error(errors, "measurementPlan.quantity", "differs from testCondition.measurement.quantity")

    if profile["family"] == "scan":
        ramps = [entry for entry in ((condition.get("scanIntent") or {}).get("entries") or [])
                 if isinstance(entry, Mapping) and entry.get("kind") == "ramp"]
        if not ramps:
            _error(errors, "testCondition.scanIntent.entries", "must declare at least one ramp for a scan method")
        allowed_ranges = {
            (start, end)
            for entry in ramps
            for start, end in [(_as_number(entry.get("from")), _as_number(entry.get("to")))]
            if start is not None and end is not None
        }
        for index, sweep in enumerate(profile["sweeps"]):
            start, end = _as_number(sweep.get("fromV")), _as_number(sweep.get("toV"))
            if allowed_ranges and start is not None and end is not None and (start, end) not in allowed_ranges and (end, start) not in allowed_ranges:
                _error(errors, f"measurementPlan.sweeps[{index}]", "is outside the DFT-declared ramp range")
        resolution = (contract.get("measurementPlan") or {}).get("scanRangeResolution") or {}
        direction_results = {
            "RISING": resolution.get("risingResult"),
            "FALLING": resolution.get("fallingResult"),
        }
        for direction, required_result in USER_SCAN_DIRECTION_RESULTS.items():
            declared = direction_results.get(direction)
            if declared is not None and declared != required_result:
                _error(errors, "measurementPlan.scanRangeResolution", f"{direction} mapping conflicts with project scan rule ({required_result})")
        for index, sweep in enumerate(profile["sweeps"]):
            direction = str(sweep.get("direction", "")).upper()
            expected = USER_SCAN_DIRECTION_RESULTS.get(direction, direction_results.get(direction))
            if expected is not None and sweep.get("result") != expected:
                _error(errors, f"measurementPlan.sweeps[{index}].result", "does not follow the declared project/contract direction mapping")
    elif condition.get("hasRamp") is True:
        _error(errors, "testCondition.hasRamp", "declares a ramp but methodFamily is not scan")
    return errors
