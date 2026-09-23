#!/usr/bin/env python3
"""Role-local gate for one DFT expert output set."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import dft_source
from material_plaintext_hash import sha256_plaintext
from ptc_contract_schema import validate_test_condition


def byte_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def yaml_hash_matches(path: Path, expected: str) -> bool:
    try:
        return any(line.startswith("sourceSha256:") and line.partition(":")[2].strip().strip("\"'") == expected
                   for line in path.read_text(encoding="utf-8-sig").splitlines())
    except OSError:
        return False


def _norm_text(value) -> str:
    """Newline-normalized string form for semantic comparison."""
    return value.replace("\r\n", "\n") if isinstance(value, str) else str(value)


def _cell_value_matches(expected_value, actual_value) -> bool:
    """Exact first, then newline-normalized string comparison."""
    if expected_value == actual_value:
        return True
    return _norm_text(expected_value) == _norm_text(actual_value)


def _loose_scalar(text: str):
    """Accept single-line JSON, quoted or bare scalars alike."""
    try:
        return json.loads(text)
    except ValueError:
        pass
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~", ""):
        return None
    for conv in (int, float):
        try:
            return conv(text)
        except ValueError:
            continue
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def yaml_semantic_condition(path: Path) -> dict | None:
    """Loosely extract ``testCondition`` from the human-readable YAML rendering.

    Accepts single-line JSON values as well as nested multi-line lists of
    mappings and bare scalars; alignment is semantic, not byte-level.
    """
    values: dict[str, object] = {}
    in_condition = False
    current_list_key = None
    current_item = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not in_condition:
            if line == "testCondition:":
                in_condition = True
            continue
        if line and not line[0].isspace():
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("- "):
            rest = stripped[2:].strip()
            if ": " in rest:
                k, v = rest.split(": ", 1)
                item = {k: _loose_scalar(v)}
            else:
                item = _loose_scalar(rest)
            values.setdefault(current_list_key, []).append(item)
            current_item = item if isinstance(item, dict) else None
            continue
        if ": " in stripped:
            key, value = stripped.split(": ", 1)
        elif stripped.endswith(":"):
            key, value = stripped[:-1], None
        else:
            continue
        if value is None and indent <= 2:
            values[key] = []
            current_list_key = key
            current_item = None
            continue
        if indent > 2 and isinstance(current_item, dict):
            current_item[key] = _loose_scalar(value)
            continue
        if indent <= 2:
            values[key] = _loose_scalar(value)
    return values if in_condition else None


def _condition_aligned(yaml_value, json_value) -> bool:
    """Semantic alignment between the YAML rendering and the JSON contract."""
    if yaml_value == json_value:
        return True
    if isinstance(json_value, dict) and isinstance(yaml_value, dict):
        if set(yaml_value) != set(json_value):
            return False
        return all(_condition_aligned(yaml_value[k], json_value[k]) for k in json_value)
    if isinstance(json_value, list) and isinstance(yaml_value, list):
        return len(yaml_value) == len(json_value) and all(
            _condition_aligned(a, e) for a, e in zip(yaml_value, json_value))
    return _cell_value_matches(json_value, yaml_value)




def coverage_matches(meta_path: Path, yaml_path: Path, row: dict, tm: str) -> bool:
    """The DFT role owns field-for-field coverage of its one OVERVIEW row."""
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        expected = {key: value for key, value in row.items() if key}
        condition = meta.get("testCondition", {})
        required_condition = {"identity", "isTrim", "powerSequence", "registerFieldIntent", "measurement", "involvedPins"}
        if meta.get("tm") != tm or not required_condition.issubset(condition):
            return False
        raw_intent = meta.get("rawIntent")
        if not isinstance(raw_intent, dict):
            return False
        normalized_raw = {_norm_text(key): value for key, value in raw_intent.items()}
        for key, cell_value in expected.items():
            if cell_value in (None, ""):
                continue  # empty cells carry no information; representation is free
            if not _cell_value_matches(cell_value, normalized_raw.get(_norm_text(key))):
                return False
        location = meta.get("sourceLocation")
        if (not isinstance(location, dict)
                or not isinstance(location.get("sheet"), str)
                or not location.get("sheet", "").strip()
                or not isinstance(location.get("row"), int)
                or isinstance(location.get("row"), bool)
                or location.get("row", 0) < 2):
            return False
        if meta.get("parseStatus") not in {"ok", "selfResolved", "pendingUser"}:
            return False
        open_items = meta.get("openItems")
        if not isinstance(open_items, list) or any(
            not isinstance(item, dict)
            or item.get("type") not in {"conflict", "missingField", "unparsable", "pinAlarm"}
            or not isinstance(item.get("description"), str)
            or not item.get("description", "").strip()
            for item in open_items
        ):
            return False
        if meta.get("parseStatus") == "ok" and open_items:
            return False
        if validate_test_condition(condition):
            return False
        yaml_condition = yaml_semantic_condition(yaml_path)
        if yaml_condition is None or not _condition_aligned(yaml_condition, condition):
            return False
        tm_ok = False
        source_ok = False
        meta_source = meta.get("sourceSha256")
        for line in yaml_path.read_text(encoding="utf-8-sig").splitlines():
            stripped = line.strip()
            if stripped.startswith("tm:") and stripped.partition(":")[2].strip().strip("\"'") == tm:
                tm_ok = True
            if stripped.startswith("sourceSha256:") and stripped.partition(":")[2].strip().strip("\"'") == meta_source:
                source_ok = True
        return tm_ok and source_ok
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


def semantic_review_matches(review_path: Path, tm: str, source_hash: str, meta: Path, conditions: Path) -> tuple[bool, str]:
    """Require a PASS review bound to the current source and both generated artifacts."""
    try:
        review = json.loads(review_path.read_text(encoding="utf-8-sig"))
        if review.get("tm") != tm or review.get("verdict") != "PASS":
            return False, "review verdict is not PASS"
        reads = review.get("readSources", [])
        if not any(item.get("sha256") == source_hash and item.get("withinInputRoot") is True for item in reads if isinstance(item, dict)):
            return False, "review is not bound to the canonical input plaintext hash inside Input_GlobalMaterial"
        reviewed_artifacts = review.get("reviewedArtifacts")
        reviewed = {}
        if isinstance(reviewed_artifacts, dict):
            reviewed = {Path(str(name)).name: digest for name, digest in reviewed_artifacts.items()}
        elif isinstance(reviewed_artifacts, list):
            reviewed = {Path(item.get("path", "")).name: item.get("sha256") for item in reviewed_artifacts if isinstance(item, dict)}
        for artifact in (meta, conditions):
            if reviewed.get(artifact.name) != byte_sha256(artifact):
                return False, f"review is not bound to current {artifact.name}"
        return True, ""
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False, "missing or invalid semantic review"


def validate(tm: str, workbook: Path | None = None) -> dict:
    tm = tm.upper()
    workbook = (workbook or dft_source.discover_workbook()).resolve()
    expected = sha256_plaintext(workbook)
    folder = dft_source.dft_output_dir(tm)
    meta, conditions, review = folder / "dft-meta.json", folder / "dft-conditions.yaml", folder / "dft-semantic-review.json"
    stale: list[str] = []
    try:
        meta_doc = json.loads(meta.read_text(encoding="utf-8-sig"))
        if meta_doc.get("sourceSha256") != expected:
            stale.append(f"{meta}: sourceSha256 differs from canonical workbook plaintext hash")
        if meta_doc.get("parseStatus") == "pendingUser":
            stale.append(f"{meta}: parseStatus=pendingUser - unresolved intent must not flow downstream (Action-01)")
        open_items = meta_doc.get("openItems")
        if isinstance(open_items, list) and open_items:
            stale.append(f"{meta}: openItems has {len(open_items)} unresolved item(s) - resolve before delivery (Action-01)")
    except (OSError, json.JSONDecodeError):
        stale.append(f"{meta}: missing or invalid JSON")
    if not yaml_hash_matches(conditions, expected):
        stale.append(f"{conditions}: missing or sourceSha256 differs from canonical workbook plaintext hash")
    rows = dft_source.rows_for(workbook, tm)
    if len(rows) != 1:
        stale.append(f"{workbook}: expected exactly one OVERVIEW row for {tm}; found {len(rows)}")
    elif not coverage_matches(meta, conditions, rows[0], tm):
        stale.append(f"{folder}: DFT JSON/YAML lacks the required source coverage or condition fields")
    review_ok, reason = semantic_review_matches(review, tm, expected, meta, conditions)
    if not review_ok:
        stale.append(f"{review}: {reason}")
    return {
        "role": "dft-expert", "gate": "DFT_OUTPUT", "status": "ready" if not stale else "stale",
        "canonicalInput": {"path": str(workbook), "sha256": expected, "sheet": dft_source.OVERVIEW_SHEET},
        "requiredOutputs": [str(meta), str(conditions), str(review)], "missingOrStaleOutputs": stale,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one DFT expert output set, including the bound LLM semantic review")
    parser.add_argument("--tm", required=True)
    parser.add_argument("--workbook", type=Path)
    args = parser.parse_args()
    report = validate(args.tm, args.workbook)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
