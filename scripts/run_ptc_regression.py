#!/usr/bin/env python3
"""Run the supported, read-only DALI PTC regression suite.

The runner writes only its report below the repository's fixed regression root;
it never creates a system temporary directory and it never changes a trial,
contract, source file, or build output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_TEST_ROOT = ROOT / "team" / "artifacts" / "_ptc-regression"
DEFAULT_REPORT = "last-run.json"

# These tests do not write source or production artifacts.  They either test a
# pure contract/registry module, or write only controlled fixtures below PTC_REGRESSION_ROOT.
SUPPORTED_TESTS = (
    "test_ptc_contract_schema.py",
    "test_ptc_trim_validation.py",
    "test_ptc_stage_registry.py",
    "test_check_functional_relays.py",
    "test_check_path_conflicts.py",
    "test_search_strategy_routes.py",
    "test_verify_source_table_mapping.py",
)

# These historical tests use tempfile.TemporaryDirectory().  On Windows CPython's
# `mkdtemp` creates the directory with mode 0o700, which it implements as an explicit,
# PROTECTED (SE_DACL_PROTECTED) owner-only DACL. A protected DACL blocks inheritance,
# so the directory never receives the workspace's inheritable sandbox write grant and
# the confined regression run cannot write or remove it. That — not DLP — is the
# measured cause (85 byte-identical temp objects on this host were created months ago
# by unsandboxed pip, i.e. plain `mkdtemp`); the schematic generator hit the same bug
# and was fixed by creating its staging directory with the default mode and a guard
# test in test_staging_directory.py. These five stay reported as skipped until
# migrated to an explicit PTC regression fixture root, which will need the same fix.
LEGACY_TEMP_TESTS = {
    "test_ate_ptc_batch_runner.py": "uses tempfile.TemporaryDirectory()",
    "test_ate_ptc_correction.py": "uses tempfile.TemporaryDirectory()",
    "test_ate_ptc_runner.py": "uses tempfile.TemporaryDirectory()",
    "test_ptc_output_contracts.py": "uses tempfile.TemporaryDirectory()",
    "test_trial_directory.py": "uses tempfile.TemporaryDirectory()",
}

INTEGRATION_TMS = ("TM102", "TM105", "TM425")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_output(text: str, limit: int = 6000) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def safe_test_root(value: str | None) -> Path:
    root = (Path(value).resolve() if value else DEFAULT_TEST_ROOT.resolve())
    artifact_root = (ROOT / "team" / "artifacts").resolve()
    if root != artifact_root and artifact_root not in root.parents:
        raise ValueError(f"test root must be inside {artifact_root}")
    return root


def test_environment(test_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    # The values are supplied for migrated tests.  This runner does not execute
    # legacy tempfile tests until they stop creating implicit system-temp files.
    for name in ("PTC_REGRESSION_ROOT", "TMP", "TEMP", "TMPDIR"):
        env[name] = str(test_root)
    path_parts = [str(ROOT), str(SCRIPTS), env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(part for part in path_parts if part)
    return env


def run_unit_test(name: str, test_root: Path) -> dict[str, Any]:
    path = SCRIPTS / name
    started = time.perf_counter()
    process = subprocess.run(
        [sys.executable, str(path)], cwd=ROOT, text=True, capture_output=True,
        env=test_environment(test_root), encoding="utf-8", errors="replace",
    )
    elapsed = round(time.perf_counter() - started, 3)
    return {
        "name": name,
        "status": "PASS" if process.returncode == 0 else "FAIL",
        "elapsedSeconds": elapsed,
        "exitCode": process.returncode,
        "output": clean_output(process.stdout + process.stderr),
    }


def integration_check() -> list[dict[str, Any]]:
    """Validate registry and signed method contracts without writing files."""
    sys.path.insert(0, str(SCRIPTS))
    import ate_ptc_runner  # imported only after the repository path is fixed

    registry, error = ate_ptc_runner.load_stage_registry()
    if error or registry is None:
        return [{"tm": tm, "status": "FAIL", "reason": error or "registry missing"} for tm in INTEGRATION_TMS]

    records: list[dict[str, Any]] = []
    for tm in INTEGRATION_TMS:
        trial = ROOT / "team" / "artifacts" / f"{tm.lower()}-ptc"
        strategy = trial / "strategy" / f"{tm.lower()}-resource-config-contract.json"
        method = trial / "method" / f"{tm.lower()}-test-method-contract.json"
        if not strategy.is_file() or not method.is_file():
            records.append({
                "tm": tm, "status": "FAIL", "reason": "strategy or method contract is missing",
                "strategy": str(strategy), "method": str(method),
            })
            continue
        try:
            strategy_hash = sha256(strategy)
            passed = ate_ptc_runner.validate_method_contract(method, strategy_hash)
        except (OSError, ValueError) as exc:
            records.append({"tm": tm, "status": "FAIL", "reason": str(exc)})
            continue
        records.append({
            "tm": tm,
            "status": "PASS" if passed else "FAIL",
            "registryStage": registry["stages"]["METHOD"]["gate"],
            "strategySha256": strategy_hash,
            "method": str(method),
            "reason": "registry loaded and method contract validates against its signed strategy" if passed else "method contract did not validate against its signed strategy",
        })
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Run supported read-only PTC regressions.")
    parser.add_argument("--test-root", help="fixed writable directory under team/artifacts")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="report name below --test-root")
    args = parser.parse_args()
    test_root = safe_test_root(args.test_root)
    report_path = (test_root / args.report).resolve()
    if report_path.parent != test_root and test_root not in report_path.parents:
        raise SystemExit("report must remain below the fixed test root")
    if report_path.suffix.lower() != ".json":
        raise SystemExit("report must be a JSON file")

    test_root.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    unit = [run_unit_test(name, test_root) for name in SUPPORTED_TESTS]
    integration = integration_check()
    failures = [item for item in unit if item["status"] != "PASS"]
    integration_failures = [item for item in integration if item["status"] != "PASS"]
    payload = {
        "schemaVersion": 1,
        "suite": "dali-ptc-supported-regression",
        "startedAtUtc": datetime.now(timezone.utc).isoformat(),
        "testRoot": str(test_root),
        "readOnlyScope": ["PTC registry", "method contracts for TM102/TM105/TM425"],
        "unitTests": unit,
        "skippedLegacyTests": [
            {"name": name, "reason": reason, "migration": "replace implicit tempfile use with PTC_REGRESSION_ROOT fixture"}
            for name, reason in LEGACY_TEMP_TESTS.items()
        ],
        "integration": integration,
        "summary": {
            "passed": len(unit) - len(failures) + len(integration) - len(integration_failures),
            "failed": len(failures) + len(integration_failures),
            "skipped": len(LEGACY_TEMP_TESTS),
            "elapsedSeconds": round(time.perf_counter() - started, 3),
        },
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"report: {report_path}")
    return 1 if payload["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
