#!/usr/bin/env python3
"""Deterministic INPUT_SYNC for one TM."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import dft_source
from material_plaintext_hash import sha256_plaintext
from validate_schematic_outputs import validate as validate_schematic_outputs

ROOT = dft_source.ROOT
INTENT_RESOLUTIONS = ROOT / "project" / "DALI" / "meta" / "intent-resolutions.json"
SPECIAL_INFORMATION = dft_source.INPUT_ROOT / "DALI-special-information.json"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_hash_matches(path: Path, expected: str) -> bool:
    try:
        return path.is_file() and json.loads(path.read_bytes().decode("utf-8-sig")).get("sourceSha256") == expected
    except Exception:
        return False


def yaml_hash_matches(path: Path, expected: str) -> bool:
    try:
        return path.is_file() and any(line.startswith("sourceSha256:") and line.partition(":")[2].strip().strip('"\'') == expected for line in path.read_text(encoding="utf-8-sig").splitlines())
    except Exception:
        return False


def dft_coverage_matches(meta_path: Path, yaml_path: Path, row: dict, tm: str) -> bool:
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        expected = {key: value for key, value in row.items() if key}
        if meta.get("tm") != tm or meta.get("rawIntent") != expected:
            return False
        header, raw, in_raw = {}, {}, False
        for line in yaml_path.read_text(encoding="utf-8-sig").splitlines():
            if line == "rawIntent:":
                in_raw = True
                continue
            if in_raw and line and not line.startswith("  "):
                in_raw = False
            if ": " not in line:
                continue
            key, value = line.strip().split(": ", 1)
            if in_raw:
                if key in raw:
                    return False
                raw[key] = json.loads(value)
            elif not line.startswith("  "):
                header[key] = json.loads(value)
        expected_yaml = {str(key).replace(" ", "_").replace(chr(10), "_"): value for key, value in expected.items()}
        return header.get("tm") == tm and raw == expected_yaml
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


def declared_dft_pins(row: dict) -> list[str]:
    pins: list[str] = []
    for column in ("Code1", "Code2", "Code3", "Dynamic"):
        for value in re.findall(r"\bvset\[([^,\]]+)", str(row.get(column, "")), flags=re.I):
            value = value.strip().upper()
            if value and value not in pins:
                pins.append(value)
    for value in re.split(r"[\n,;]+", str(row.get("Power", ""))):
        value = value.strip().upper()
        if value and value not in pins:
            pins.append(value)
    return pins


def components_has_dut_pin(path: Path, pin: str) -> bool:
    try:
        return bool(re.search(r"(?<![A-Za-z0-9_])" + re.escape(pin) + r"(?![A-Za-z0-9_])", path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tm", required=True)
    parser.add_argument("--trial-dir", required=True)
    args = parser.parse_args()
    tm, trial = args.tm.upper(), Path(args.trial_dir).resolve()
    special_information = None
    special_hash = None
    if SPECIAL_INFORMATION.is_file():
        try:
            special_information = json.loads(SPECIAL_INFORMATION.read_text(encoding="utf-8-sig"))
            if not isinstance(special_information.get("mappings"), list):
                raise ValueError("mappings is not a list")
            special_hash = sha256_plaintext(SPECIAL_INFORMATION)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"BLOCKED: invalid DALI-special-information.json: {exc}")
            return 2
    resolutions = {}
    if INTENT_RESOLUTIONS.is_file():
        try:
            resolutions = json.loads(INTENT_RESOLUTIONS.read_text(encoding="utf-8")).get("resolutions", {})
        except Exception:
            pass
    trial.mkdir(parents=True, exist_ok=True)
    try:
        workbook, schematic_source = dft_source.discover_workbook(), dft_source.discover_schematic()
    except ValueError as exc:
        print(f"BLOCKED: {exc}")
        return 2
    workbook_hash, schematic_hash = sha256_plaintext(workbook), sha256_plaintext(schematic_source)
    resolution_hash = sha(INTENT_RESOLUTIONS) if INTENT_RESOLUTIONS.is_file() else None
    overview_rows = dft_source.rows_for(workbook, tm)
    dft_dir, schematic_dir = dft_source.dft_output_dir(tm), dft_source.schematic_output_dir()
    dft_files = [dft_dir / "dft-meta.json", dft_dir / "dft-conditions.yaml"]
    schematic_files = [schematic_dir / "SCH-Connect-Map.txt", schematic_dir / "SCH-Connect-Map.json", schematic_dir / "Component-Statistic.txt", schematic_dir / "Components-Statistic.json", schematic_dir / "Path-Proofs.txt", schematic_dir / "Path-Proofs.json", schematic_dir / "schematic-receipt.json"]
    dft_missing = [str(p) for p in dft_files if not (json_hash_matches(p, workbook_hash) if p.suffix == ".json" else yaml_hash_matches(p, workbook_hash))]
    if len(overview_rows) == 1 and not dft_missing and not dft_coverage_matches(dft_files[0], dft_files[1], overview_rows[0], tm):
        dft_missing = [str(p) + " has incomplete or mismatched OVERVIEW coverage" for p in dft_files]
    schematic_report = validate_schematic_outputs(schematic_source, dft_source.INPUT_ROOT / "sch_confirmed.json")
    schematic_missing = list(schematic_report["missingOrStaleOutputs"])
    entry = resolutions.get(tm)
    declared_monitor = entry.get("decision", {}).get("monitorDutPin") if isinstance(entry, dict) else None
    components = schematic_dir / "Component-Statistic.txt"
    if schematic_report["status"] == "ready" and isinstance(declared_monitor, str) and declared_monitor and not components_has_dut_pin(components, declared_monitor):
        schematic_missing.append(str(components) + " does not declare the declared monitor pin " + declared_monitor)
    declared_pins = declared_dft_pins(overview_rows[0]) if len(overview_rows) == 1 else []
    manifest = {"schemaVersion": 8, "stage": "INPUT_SYNC", "tm": tm,
        "materialRoots": {"input": str(dft_source.INPUT_ROOT), "output": str(dft_source.OUTPUT_ROOT), "errorLog": str(dft_source.ERROR_ROOT)},
        "canonicalInputs": {
            "dft": {"path": str(workbook), "sha256": workbook_hash, "sheet": dft_source.OVERVIEW_SHEET, "rowCount": len(overview_rows), "rawRows": overview_rows, "declaredPins": declared_pins, "checkLabel": str(overview_rows[0].get("Check", "")) if len(overview_rows) == 1 else "", "requiredOutputs": [str(p) for p in dft_files], "missingOrStaleOutputs": dft_missing, "status": "ready" if not dft_missing else "stale"},
            "schematic": {"path": str(schematic_source), "sha256": schematic_hash, "requiredOutputs": [str(p) for p in schematic_files], "missingOrStaleOutputs": schematic_missing, "status": "ready" if not schematic_missing else "stale"},
            "intentResolution": {"path": str(INTENT_RESOLUTIONS), "sha256": resolution_hash, "entry": entry, "status": "declared" if isinstance(entry, dict) else "not_declared", "gate": "informational only; this file never blocks a run"},
            "specialPinInformation": {"path": str(SPECIAL_INFORMATION), "sha256": special_hash, "document": special_information, "status": "declared" if special_information else "not_declared", "gate": "authoritative only for listed DALI logical-pin mappings"}},
        "dispatchableRoles": []}
    if len(overview_rows) != 1:
        manifest.update(status="blocked", blockReason=f"expected exactly one {dft_source.OVERVIEW_SHEET} row for {tm}; found {len(overview_rows)}")
    else:
        stale = [name for name in ("dft", "schematic") if manifest["canonicalInputs"][name]["status"] == "stale"]
        manifest.update(status="ready" if not stale else "needs-derived-artifacts", dispatchableRoles=[f"{name}-expert" for name in stale])
    out = trial / "input-manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{manifest['status'].upper()}: {out}")
    print("DISPATCH=" + ",".join(manifest["dispatchableRoles"]))
    return 0 if manifest["status"] in ("ready", "needs-derived-artifacts") else 2


if __name__ == "__main__":
    raise SystemExit(main())
