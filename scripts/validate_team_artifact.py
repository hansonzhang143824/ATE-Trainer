#!/usr/bin/env python3
"""Validate one AgentTeams handoff artifact against a project schema."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"only local schema refs are supported: {ref}")
    node: Any = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        node = node[token]
    if not isinstance(node, dict):
        raise ValueError(f"schema ref does not resolve to an object: {ref}")
    return node


def _validate(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str, errors: list[str]) -> None:
    if "$ref" in schema:
        _validate(value, _resolve_ref(root, schema["$ref"]), root, path, errors)
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']!r}")

    expected = schema.get("type")
    if isinstance(expected, str) and not _type_matches(value, expected):
        errors.append(f"{path}: expected {expected}, got {type(value).__name__}")
        return

    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}: missing required property {name!r}")
        properties = schema.get("properties", {})
        for name, child in value.items():
            child_path = f"{path}/{name}"
            if name in properties:
                _validate(child, properties[name], root, child_path, errors)
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    errors.append(f"{child_path}: additional property is not allowed")
                elif isinstance(additional, dict):
                    _validate(child, additional, root, child_path, errors)

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: expected at least {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, child in enumerate(value):
                _validate(child, item_schema, root, f"{path}/{index}", errors)

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"{path}: {value!r} does not match {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", help="Schema name (for example dft-ir) or schema path")
    parser.add_argument("artifact", help="Artifact JSON path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    schema_arg = Path(args.schema)
    if schema_arg.suffix.lower() != ".json":
        schema_arg = root / "team" / "schemas" / f"{args.schema}.schema.json"
    elif not schema_arg.is_absolute():
        schema_arg = root / schema_arg

    artifact = Path(args.artifact)
    if not artifact.is_absolute():
        artifact = root / artifact

    schema = json.loads(schema_arg.read_text(encoding="utf-8-sig"))
    instance = json.loads(artifact.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    _validate(instance, schema, schema, "<root>", errors)
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"PASS {artifact} conforms to {schema_arg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
