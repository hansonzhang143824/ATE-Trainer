#!/usr/bin/env python3
"""One-pass implementation gate driven by each signed method contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from ptc_contract_schema import method_execution_profile
from ptc_trim_validation import validate_trim_project_evidence


TRIM_STANDARD_PATHS = (
    "knowledge/standards/treg.md",
    "knowledge/references/L4-Golden-code/TM130_Trim_VBG.md",
    "knowledge/references/L4-Golden-code/sub-measure-template.md",
)
TRIM_VALIDATOR_PATH = "scripts/ptc_trim_validation.py"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_trim_compliance() -> dict:
    refs = []
    for relative in TRIM_STANDARD_PATHS:
        source = PROJECT_ROOT / relative
        refs.append({"path": relative, "sha256": sha(source)})
    validator = PROJECT_ROOT / TRIM_VALIDATOR_PATH
    return {
        "standardReferences": refs,
        "validator": {
            "path": TRIM_VALIDATOR_PATH,
            "sha256": sha(validator),
            "status": "PASS",
            "errors": [],
        },
    }


def validate_trim_compliance_evidence(manifest: dict, prefix: str) -> list[str]:
    """Require recorded standard versions and the deterministic Trim validation result."""
    errors: list[str] = []
    actual = manifest.get("trimCompliance")
    if not isinstance(actual, dict):
        return [prefix + "trim compliance evidence is missing"]
    expected = expected_trim_compliance()
    if actual.get("standardReferences") != expected["standardReferences"]:
        errors.append(prefix + "Trim standard references or hashes do not match the active project rules")
    if actual.get("validator") != expected["validator"]:
        errors.append(prefix + "Trim validator record is missing, stale, or not PASS")
    return errors


def function_body(source: str, symbol: str) -> tuple[str | None, int]:
    pattern = r"\bDUT_API\s+int\s+" + re.escape(symbol) + r"\s*\([^)]*\)\s*\{"
    match = re.search(pattern, source)
    if not match:
        return None, 0
    count = len(re.findall(pattern, source))
    index, depth = match.end(), 1
    while index < len(source) and depth:
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
        index += 1
    return source[match.start():index], count


def callback_body(source: str, symbol: str) -> tuple[str | None, int]:
    pattern = r"\bvoid\s+" + re.escape(symbol) + r"\s*\([^)]*TRIM_NODE[^)]*TREG_MEASURE_FLAG[^)]*double\s*\*[^)]*\)\s*\{"
    match = re.search(pattern, source)
    if not match:
        return None, 0
    count = len(re.findall(pattern, source))
    index, depth = match.end(), 1
    while index < len(source) and depth:
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
        index += 1
    return source[match.start():index], count


def validate_trim_callback(body: str, prefix: str, method: dict) -> list[str]:
    trim = ((method.get("measurementPlan") or {}).get("trimExecution") or {})
    callback = trim.get("callback") or {}
    treg = trim.get("treg") or {}
    errors: list[str] = []
    assembly = treg.get("assembly")
    address = treg.get("i2cAddress")
    source_table = callback.get("measurementSourceTable")
    if not isinstance(assembly, str) or assembly not in body:
        errors.append(prefix + "signed TREG assembly missing from trim callback")
    if isinstance(address, str) and address.lower() not in body.lower():
        errors.append(prefix + "signed TREG I2C address missing from trim callback")
    if not isinstance(source_table, str) or source_table + ".MeasureVI" not in body or source_table + ".GetMeasResult" not in body:
        errors.append(prefix + "signed measurement source is missing from trim callback")
    return errors


def number_pattern(value: object) -> str:
    text = str(value)
    if re.fullmatch(r"[+-]?\d+", text):
        return re.escape(text) + r"(?:\.0+)?"
    return re.escape(text)


def trial_tm(trial: Path) -> str:
    return trial.name.replace("-ptc-v2", "").replace("-ptc", "").upper()


def method_contract(trial: Path, tm: str) -> dict:
    path = trial / "method" / f"{tm.lower()}-test-method-contract.json"
    return json.loads(path.read_text(encoding="utf-8"))


def signed_source_tables(method: dict) -> list[str]:
    boundary = method.get("resourceBoundary") or {}
    by_endpoint = boundary.get("sourceTablesByEndpoint") or {}
    if isinstance(by_endpoint, dict):
        return [value for value in by_endpoint.values() if isinstance(value, str) and value]
    return [row.get("sourceTable") for row in (boundary.get("allocations") or [])
            if row.get("selectionState") == "SELECTED" and isinstance(row.get("sourceTable"), str) and row.get("sourceTable")]


def validate_relay_settle(body: str, prefix: str) -> list[str]:
    """Every actual relay closure has an immediate three millisecond settle."""
    errors: list[str] = []
    for match in re.finditer(r"cbite\s*\.\s*SetOn\s*\(([^;]*)\)\s*;", body, re.S):
        arguments = match.group(1)
        if not re.search(r"\bK\d+(?!\d)", arguments):
            continue  # SetOn(-1) is release, not a functional relay closure.
        following = body[match.end():].lstrip()
        # Comments may appear between the closure and mandatory settle, but no code.
        following = re.sub(r"^(?://[^\n]*\n|/\*.*?\*/\s*)", "", following, flags=re.S).lstrip()
        if not re.match(r"(?:Sleep|delay_ms)\s*\(\s*3\s*\)\s*;", following):
            errors.append(prefix + "functional relay closure must be followed immediately by a 3 ms wait")
    return errors


def validate_zero_before_off(body: str, prefix: str, source_tables: list[str]) -> list[str]:
    """Each signed source table must explicitly reach FV=0 while still ON before its OFF call."""
    errors: list[str] = []
    for table in source_tables:
        call = re.escape(table) + r"\s*\.\s*Set\s*\(\s*FV\s*,\s*0(?:\.0+)?\s*,[^;]*?(ACM200|FXVIe_PLUS|FPVIe)_RELAY_(ON|OFF)\s*\)\s*;"
        events = [(m.start(), m.group(2)) for m in re.finditer(call, body, re.S)]
        off_positions = [position for position, state in events if state == "OFF"]
        if not off_positions:
            errors.append(prefix + f"signed source table {table} is not shut down with FV=0 then relay off")
            continue
        for off in off_positions:
            if not any(position < off and state == "ON" for position, state in events):
                errors.append(prefix + f"signed source table {table} must set FV=0 with relay ON before relay OFF")
                break
    return errors


def validate_body(body: str, prefix: str, strategy: dict, evidence: dict, method: dict) -> list[str]:
    errors: list[str] = []
    required_relays = ["K" + str(number) for number in (strategy.get("setOnClosure") or {}).get("relays") or []]
    source_tables = signed_source_tables(method)
    for table in source_tables:
        if table not in body:
            errors.append(prefix + f"signed source table missing: {table}")
    errors.extend(validate_relay_settle(body, prefix))
    errors.extend(validate_zero_before_off(body, prefix, source_tables))
    for row in (evidence.get("orderedWrites") or []):
        if row.get("sourceText") not in body:
            errors.append(prefix + "register line differs from signed source")
    active = re.search(r"cbite\.SetOn\((?!-1)([^;]+)\);", body)
    if not active or not all(token in active.group(1) for token in required_relays):
        errors.append(prefix + "signed relay closure missing")
    profile, profile_errors = method_execution_profile(method)
    if profile_errors:
        return errors + [prefix + "invalid signed method contract: " + item for item in profile_errors]
    publisher = profile["publisher"]
    if publisher["kind"] == "set_test_result":
        actual = len(re.findall(r"SetTestResult\s*\(", body))
        if actual < publisher["minimumCount"]:
            errors.append(prefix + f"signed SetTestResult count missing: need {publisher['minimumCount']}, found {actual}")
    else:
        execute_prefix = publisher.get("executeCallPrefix")
        if not isinstance(execute_prefix, str) or not execute_prefix or execute_prefix not in body:
            errors.append(prefix + "signed trim execution API missing")
        trim = (method.get("measurementPlan") or {}).get("trimExecution")
        errors.extend(prefix + "trim: " + item for item in validate_trim_project_evidence(trim, source_body=body))
    for sweep in profile["sweeps"]:
        trigger = "TRIG_" + str(sweep.get("result", "")).upper()
        pattern = number_pattern(sweep.get("fromV")) + r"\s*,\s*" + number_pattern(sweep.get("toV")) + r".*?" + re.escape(trigger)
        if not re.search(pattern, body, re.S):
            errors.append(prefix + f"signed {sweep.get('fromV')}->{sweep.get('toV')} sweep with {trigger} missing")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate implementation against its own signed method contract")
    parser.add_argument("trials", nargs="+")
    args = parser.parse_args()
    errors: list[str] = []
    reports: list[dict] = []
    for raw_trial in args.trials:
        trial = Path(raw_trial)
        tm = trial_tm(trial)
        strategy_path = trial / "strategy" / f"{tm.lower()}-resource-config-contract.json"
        manifest_path = trial / "implementation" / "implementation-manifest.json"
        evidence_path = trial / "strategy" / "register-config-evidence.json"
        try:
            strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            method = method_contract(trial, tm)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{trial.name}: cannot read signed implementation inputs: {exc}")
            continue
        if ((manifest.get("signedInputs") or {}).get("methodContractSha256")
                != sha(trial / "method" / f"{tm.lower()}-test-method-contract.json")):
            errors.append(trial.name + ": implementation manifest is not bound to current method contract")
            continue
        if method.get("methodFamily") == "trim":
            errors.extend(validate_trim_compliance_evidence(manifest, trial.name + ": "))
        for change in manifest.get("changes") or []:
            source = Path(change.get("path", ""))
            expected = change.get("afterSha256")
            symbols = change.get("symbols") or []
            if not source.is_file() or sha(source) != expected:
                errors.append(trial.name + ": source hash mismatch")
                continue
            text = source.read_text(encoding="utf-8", errors="replace")
            for symbol in symbols:
                prefix = f"{trial.name}: {symbol}: "
                if change.get("kind") == "trim_measure_callback":
                    body, count = callback_body(text, symbol)
                    if count != 1 or body is None:
                        errors.append(prefix + f"trim callback definition count={count}")
                        continue
                    errors.extend(validate_trim_callback(body, prefix, method))
                    reports.append({"trial": trial.name, "tm": tm, "symbol": symbol, "kind": "trim_measure_callback", "sourceSha256": expected, "status": "PASS"})
                    continue
                body, count = function_body(text, symbol)
                if count != 1 or body is None:
                    errors.append(prefix + f"DUT_API declaration count={count}")
                    continue
                errors.extend(validate_body(body, prefix, strategy, evidence, method))
                reports.append({"trial": trial.name, "tm": tm, "symbol": symbol, "methodFamily": method.get("methodFamily"), "sourceSha256": expected, "status": "PASS"})
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "PASS", "checks": reports}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
