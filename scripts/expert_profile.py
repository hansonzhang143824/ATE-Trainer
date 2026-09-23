#!/usr/bin/env python3
"""Shared expert-master helpers: strict profile metadata, asset inventory, manifests.

Deliberately dependency-free: the repository has no YAML library (see the note in
``validate_dft_outputs.py``), so ``profile.yaml`` is a STRICT subset — top-level
``key: value`` scalars plus ``key:`` followed by ``  - item`` lists. Anything else
is rejected loudly rather than silently misread.

``team/expert-profiles/<profile-id>/`` holds the master assets:

    profile.yaml                  metadata (this module's parser owns its shape)
    instructions.md               the expert's task statement
    output-contract.schema.json   required artifact fields
    cases/<TM>/expected.json      golden case expectations
    evaluation/expected-results.json   the case index and its expected verdicts
    CHANGELOG.md
    status.json                   draft verdict, published version, history
    versions/<vN>/                immutable published snapshots (written by publish)
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERT_ROOT = ROOT / "team" / "expert-profiles"
PLUGIN_REGISTRY = ROOT / "plugins" / "dsh-ptc-material-boundary" / "lib" / "expert-policy-registry.js"
PRESET_ROOT = Path.home() / ".dsh" / ".agent-presets"

REQUIRED_PROFILE_KEYS = (
    "schemaVersion", "id", "displayName", "presetId", "executionClass", "stage", "ownerRole",
)
REQUIRED_ASSETS = (
    "profile.yaml",
    "instructions.md",
    "output-contract.schema.json",
    "CHANGELOG.md",
    "status.json",
    "evaluation/expected-results.json",
)
# The single source for executionClass names is the plugin registry in JavaScript;
# this pattern reads it rather than restating it, and fails loudly if it changes.
CLASS_PATTERN = re.compile(r"^  '([a-z][a-z0-9-]*)': Object\.freeze\(\{", re.M)
PROFILE_CLASS_PATTERN = re.compile(r"^  '([a-z][a-z0-9-]*)': '([a-z][a-z0-9-]*)',$", re.M)
FORBIDDEN_INPUT_NAMES = ("schematic-ir.json", "old", "retired-context")
VERSION_PATTERN = re.compile(r"^v[0-9]+$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def profile_dir(profile_id: str) -> Path:
    return EXPERT_ROOT / profile_id


def parse_profile_yaml(text: str) -> tuple[dict, list[str]]:
    """Parse the strict profile subset. Returns (values, errors)."""
    values: dict[str, object] = {}
    errors: list[str] = []
    current_list: str | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_list is None:
                errors.append(f"line {number}: list item without a preceding key")
                continue
            values[current_list].append(line[4:].strip().strip('"').strip("'"))
            continue
        if line.startswith(" "):
            errors.append(f"line {number}: unsupported indentation (only two-space list items are allowed)")
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip():
            errors.append(f"line {number}: expected 'key: value'")
            continue
        key, value = key.strip(), value.strip()
        if value == "":
            values[key] = []
            current_list = key
            continue
        current_list = None
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if re.fullmatch(r"-?[0-9]+", value):
            values[key] = int(value)
        elif value in {"true", "false"}:
            values[key] = value == "true"
        else:
            values[key] = value
    return values, errors


def load_profile(profile_id: str) -> tuple[dict | None, list[str]]:
    """Read one profile's metadata, validating shape and identity."""
    directory = profile_dir(profile_id)
    path = directory / "profile.yaml"
    if not path.is_file():
        return None, [f"missing {path}"]
    values, errors = parse_profile_yaml(path.read_text(encoding="utf-8-sig"))
    for key in REQUIRED_PROFILE_KEYS:
        if key not in values:
            errors.append(f"profile.yaml is missing required key {key}")
    if values.get("id") != profile_id:
        errors.append(f"profile.yaml id {values.get('id')!r} does not match its directory {profile_id!r}")
    return (values if not errors else None), errors


def registry_classes() -> tuple[list[str], dict[str, str], list[str]]:
    """Read the executionClass names and the profile→class map from the plugin."""
    if not PLUGIN_REGISTRY.is_file():
        return [], {}, [f"plugin policy registry not found: {PLUGIN_REGISTRY}"]
    text = PLUGIN_REGISTRY.read_text(encoding="utf-8-sig")
    classes = CLASS_PATTERN.findall(text)
    mapping = dict(PROFILE_CLASS_PATTERN.findall(text))
    errors = []
    if len(classes) < 4:
        errors.append("could not read executionClass names from the plugin registry (shape changed?)")
    if not mapping:
        errors.append("could not read the profile→executionClass map from the plugin registry")
    return classes, mapping, errors


def asset_inventory(profile_id: str) -> dict[str, str]:
    """Every master asset except the published snapshots, as {relative path: sha256}."""
    directory = profile_dir(profile_id)
    files: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(directory).as_posix()
        if relative.startswith("versions/"):
            continue
        files[relative] = sha256_file(path)
    return files


def snapshot_digest(files: dict[str, str]) -> str:
    """One digest over the whole file map, stable regardless of insertion order."""
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(canonical)


def read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
