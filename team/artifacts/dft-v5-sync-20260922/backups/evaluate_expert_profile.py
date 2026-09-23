#!/usr/bin/env python3
"""Evaluate one expert master profile's draft (handoff section 6.1).

Every check below is machine-checkable and reports its own verdict, so a failing
evaluation names the exact reason instead of returning a bare "failed".

    python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version draft

Exit codes: 0 = pass, 2 = fail (a fail is never reported as a pass), 1 = usage.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import expert_profile as ep  # noqa: E402  (path is fixed above, by design)

REGRESSION_COMMAND = ("node", "--test", "all.test.mjs", "--test-reporter=tap")


class Checks:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def record(self, check_id: str, ok: bool, detail: str) -> None:
        self.entries.append({"id": check_id, "ok": bool(ok), "detail": detail})

    @property
    def failed(self) -> list[dict]:
        return [entry for entry in self.entries if not entry["ok"]]


def _check_assets(profile_id: str, checks: Checks) -> None:
    directory = ep.profile_dir(profile_id)
    missing = [name for name in ep.REQUIRED_ASSETS if not (directory / name).is_file()]
    checks.record("assets", not missing, "all required assets present" if not missing else f"missing: {', '.join(missing)}")


def _check_metadata(profile_id: str, checks: Checks) -> dict | None:
    profile, errors = ep.load_profile(profile_id)
    checks.record("profile_metadata", not errors, "profile.yaml parsed and identified" if not errors else "; ".join(errors))
    if profile is None:
        return None
    classes, mapping, registry_errors = ep.registry_classes()
    if registry_errors:
        checks.record("execution_class_source", False, "; ".join(registry_errors))
        return profile
    declared = profile.get("executionClass")
    checks.record(
        "execution_class_registered",
        declared in classes,
        f"executionClass {declared!r} is registered in the plugin policy registry" if declared in classes
        else f"executionClass {declared!r} is not one of {sorted(classes)}",
    )
    checks.record(
        "execution_class_matches_profile_map",
        mapping.get(profile_id) == declared,
        f"plugin maps {profile_id} to {mapping.get(profile_id)!r}",
    )
    for key in ("readable", "writable", "requiredGates"):
        values = profile.get(key)
        checks.record(f"declared_{key}", isinstance(values, list) and len(values) > 0, f"{key}: {values!r}")
    # An input specialist must not declare a retired artifact as readable — the
    # boundary is only as strong as the path list it is built from.
    readable = profile.get("readable") if isinstance(profile.get("readable"), list) else []
    tainted = [str(entry) for entry in readable if any(name in str(entry).lower() for name in ep.FORBIDDEN_INPUT_NAMES)]
    checks.record("readable_has_no_retired_artifact", not tainted,
                  "readable declares no retired artifact" if not tainted else f"readable names a retired artifact: {tainted}")
    return profile


def _check_output_contract(profile_id: str, checks: Checks) -> None:
    path = ep.profile_dir(profile_id) / "output-contract.schema.json"
    schema = ep.read_json(path)
    if not isinstance(schema, dict):
        checks.record("output_contract", False, "output-contract.schema.json is not a JSON object")
        return
    required = schema.get("required")
    ok = schema.get("type") == "object" and isinstance(required, list) and len(required) > 0
    checks.record("output_contract", ok, f"object schema with required={required!r}" if ok else "schema must be an object with a non-empty required list")


def _check_cases(profile_id: str, profile: dict, checks: Checks) -> list[dict]:
    directory = ep.profile_dir(profile_id)
    cases_root = directory / "cases"
    index = ep.read_json(directory / "evaluation" / "expected-results.json")
    if not isinstance(index, dict) or not isinstance(index.get("cases"), list):
        checks.record("case_index", False, "evaluation/expected-results.json has no cases list")
        return []
    indexed = [entry.get("caseId") for entry in index["cases"] if isinstance(entry, dict)]
    on_disk = sorted(path.name for path in cases_root.iterdir() if path.is_dir()) if cases_root.is_dir() else []
    checks.record("case_index_matches_disk", sorted(indexed) == on_disk,
                  f"index {sorted(indexed)} vs cases/ {on_disk}")
    execution_class = str((profile or {}).get("executionClass") or "")
    input_class = execution_class in ("input-dft", "input-schematic")
    readable = [str(r) for r in ((profile or {}).get("readable") or []) if isinstance(r, str)]

    def inside_read_roots(case_id: str, text: str) -> bool:
        if input_class:
            return "Input_GlobalMaterial" in text
        for root in readable:
            bound = root.replace("<TM>", str(case_id))
            if text == bound or text.startswith(bound.rstrip("/") + "/"):
                return True
        return False

    cases: list[dict] = []
    for case_id in indexed:
        path = cases_root / str(case_id) / "expected.json"
        case = ep.read_json(path)
        if not isinstance(case, dict):
            checks.record(f"case_{case_id}", False, f"{path} is missing or invalid JSON")
            continue
        problems = []
        canonical = case.get("canonicalInput")
        if not isinstance(canonical, str) or not inside_read_roots(case_id, canonical):
            scope = "the canonical input root (Input_GlobalMaterial)" if input_class else \
                f"the profile's declared readable roots {readable}"
            problems.append(f"canonicalInput must name a file inside {scope}")
        reads = case.get("expectedReadSources")
        if not isinstance(reads, list) or not reads:
            problems.append("expectedReadSources must be a non-empty list")
        else:
            for entry in reads:
                text = str(entry)
                if not inside_read_roots(case_id, text):
                    scope = "the canonical input root (Input_GlobalMaterial)" if input_class else \
                        f"the profile's declared readable roots {readable}"
                    problems.append(f"expectedReadSources entry is outside {scope}: {text}")
                if any(forbidden in text.lower() for forbidden in ep.FORBIDDEN_INPUT_NAMES):
                    problems.append(f"expectedReadSources names a forbidden old artifact: {text}")
        outputs = case.get("expectedOutputs")
        if not isinstance(outputs, list) or not outputs:
            problems.append("expectedOutputs must be a non-empty list")
        # A case may name the retired artifacts it must NOT read. Each entry must
        # be OUTSIDE the allowed read scope (that is what makes it retired) and
        # must not also appear as an expected read source.
        forbidden = case.get("forbiddenInputs")
        if forbidden is not None:
            if not isinstance(forbidden, list) or not forbidden:
                problems.append("forbiddenInputs, when present, must be a non-empty list")
            else:
                for entry in forbidden:
                    text = str(entry)
                    if inside_read_roots(case_id, text):
                        problems.append(f"forbiddenInputs entry is inside the allowed read scope, so it is not a retired artifact: {text}")
                    if isinstance(reads, list) and text in [str(item) for item in reads]:
                        problems.append(f"forbiddenInputs entry is also listed as an expected read source: {text}")
        if case.get("semanticTruthStatus") == "PENDING_DOMAIN_INPUT" and not case.get("semanticTruthNote"):
            problems.append("a case that defers semantic truth must say so in semanticTruthNote")
        checks.record(f"case_{case_id}", not problems, "; ".join(problems) if problems else "case is complete and inside the allowed read scope")
        cases.append(case)
    return cases

def _check_preset(profile: dict | None, checks: Checks) -> None:
    """Agreement with the DSH preset the user actually selects. Absent is not a failure."""
    preset_id = (profile or {}).get("presetId")
    if not isinstance(preset_id, str):
        return
    metadata = ep.PRESET_ROOT / preset_id / "preset.yml"
    if not metadata.is_file():
        checks.record("preset_agreement", True, f"UNKNOWN: preset {preset_id} is not installed on this machine, so its display name could not be compared")
        return
    text = metadata.read_text(encoding="utf-8-sig", errors="replace")
    expected = (profile or {}).get("displayName")
    ok = any(line.strip() == f"name: {expected}" for line in text.splitlines())
    checks.record("preset_agreement", ok, f"preset.yml name matches displayName {expected!r}" if ok else f"preset.yml does not declare 'name: {expected}'")


def _check_regression(checks: Checks, skip: bool) -> None:
    if skip:
        checks.record("boundary_regression", True, "SKIPPED by --skip-regression: the plugin boundary suite was not run in this evaluation")
        return
    plugin = ep.ROOT / "plugins" / "dsh-ptc-material-boundary" / "test"
    try:
        completed = subprocess.run(
            REGRESSION_COMMAND, cwd=plugin, capture_output=True,
            # The suite prints UTF-8; decoding with the locale codec (GBK on this
            # machine) raised inside the reader thread and would have hidden real
            # output behind a UnicodeDecodeError.
            encoding="utf-8", errors="replace", timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        checks.record("boundary_regression", False, f"could not run the boundary suite: {error}")
        return
    ok = completed.returncode == 0
    checks.record("boundary_regression", ok, "plugin boundary suite passed" if ok else f"plugin boundary suite exited {completed.returncode}")


def _check_case_verification(cases: list[dict], checks: Checks, skip: bool) -> None:
    """Run a golden case's declared verification, if it declares one.

    A case that only *says* what the gate should print is a claim; a case that
    declares the command and exit code its gate must produce can be re-run by
    anyone. The first-batch loop showed why this matters: the DFT artifacts were
    only provably correct once the review was re-bound to them and the gate was
    re-run, so a case that cannot be re-verified is worth little.

    Cases without a `verification` block are untouched, which keeps the
    evaluation usable in a checkout that has no project material.
    """
    declared = [case for case in cases if isinstance(case.get("verification"), dict)]
    if not declared:
        return
    if skip:
        checks.record("case_verification", True, "SKIPPED by --skip-case-gates: no case gate was executed in this evaluation")
        return
    for case in declared:
        case_id = case.get("caseId")
        verification = case["verification"]
        command = verification.get("command")
        expected_exit = verification.get("expectExit")
        expected_text = verification.get("expectContains")
        if not isinstance(command, str) or not command.strip():
            checks.record(f"case_gate_{case_id}", False, "verification.command must be a non-empty string")
            continue
        if not isinstance(expected_exit, int):
            checks.record(f"case_gate_{case_id}", False, "verification.expectExit must be an integer")
            continue
        try:
            completed = subprocess.run(
                command, cwd=str(ep.ROOT), shell=True, capture_output=True,
                encoding="utf-8", errors="replace", timeout=600,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            checks.record(f"case_gate_{case_id}", False, f"could not run {command!r}: {error}")
            continue
        problems = []
        if completed.returncode != expected_exit:
            problems.append(f"exit {completed.returncode}, expected {expected_exit}")
        if isinstance(expected_text, str) and expected_text not in (completed.stdout or ""):
            problems.append(f"stdout does not contain {expected_text!r}")
        checks.record(f"case_gate_{case_id}", not problems, f"{command} produced exit {completed.returncode}" if not problems else "; ".join(problems))


def evaluate(profile_id: str, *, skip_regression: bool = False, skip_case_gates: bool = False) -> dict:
    checks = Checks()
    _check_assets(profile_id, checks)
    profile = _check_metadata(profile_id, checks)
    _check_output_contract(profile_id, checks)
    cases = _check_cases(profile_id, profile, checks)
    _check_preset(profile, checks)
    _check_regression(checks, skip_regression)
    _check_case_verification(cases, checks, skip_case_gates)
    return {
        "schemaVersion": 1,
        "profileId": profile_id,
        "version": "draft",
        "verdict": "pass" if not checks.failed else "fail",
        "checks": checks.entries,
        "failed": [entry["id"] for entry in checks.failed],
        "caseCount": len(cases),
        "assetDigest": ep.snapshot_digest(ep.asset_inventory(profile_id)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate one expert master profile's draft assets")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--version", default="draft")
    parser.add_argument("--skip-regression", action="store_true", help="skip the plugin boundary suite (fast, less evidence)")
    parser.add_argument("--skip-case-gates", action="store_true", help="skip the golden cases' declared gate commands")
    args = parser.parse_args()
    if args.version != "draft":
        print(json.dumps({"verdict": "fail", "reason": "only the draft is evaluated; publish promotes a passed draft"}, ensure_ascii=False))
        return 2
    report = evaluate(args.profile, skip_regression=args.skip_regression, skip_case_gates=args.skip_case_gates)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
