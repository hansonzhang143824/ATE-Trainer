#!/usr/bin/env python3
"""Validate the expert roster (handoff section 13.4).

Every non-captain stage owner in the PTC stage registry must be covered by a
PUBLISHED expert profile that can actually be dispatched (profile exists,
status.json points at an intact published version). A dangling mapping or an
unmapped owner is a FAILURE, not a warning: an owner without a dispatchable
profile would silently fall back to label dispatch with no boundary.

INPUT_SYNC is owned by `captain` in the registry; its two source roles
(dft-expert, schematic-expert) are validated explicitly instead.

Exit code 0 = roster complete; 2 = problems found.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "team" / "expert-profiles"
REGISTRY = ROOT / "team" / "ptc" / "ptc_stage_registry.json"

# registry owner (or INPUT_SYNC source role) -> profile id
OWNER_PROFILE = {
    "dft-expert": "ptc-dft-expert",
    "schematic-expert": "ptc-schematic-expert",
    "test-strategy-architect": "strategy-expert",
    "test-method-expert": "method-expert",
    "rule-reviewer": "rule-reviewer",
    "ate-implementer": "ate-implementer",
    "compile-diagnostician": "compile-diagnostician",
    "evolution-expert": "evolution-expert",
}

# Owners without profiles yet, reported as gaps rather than failing the whole
# check. Empty since the third batch landed.
EXPECTED_MISSING: set[str] = set()


def profile_state(profile_id: str) -> tuple[str, str]:
    directory = PROFILES / profile_id
    if not directory.is_dir():
        return "missing", f"no profile directory at {directory}"
    status_path = directory / "status.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return "missing", f"status.json unreadable: {error}"
    version = status.get("publishedVersion")
    if not isinstance(version, str) or not version.startswith("v"):
        return "unpublished", f"publishedVersion = {version!r}"
    manifest_path = directory / "versions" / version / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return "broken", f"{profile_id}@{version}: manifest unreadable: {error}"
    if manifest.get("digest") != status.get("manifestDigest"):
        return "broken", f"{profile_id}@{version}: status digest does not match the manifest"
    return "published", f"{profile_id}@{version}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-missing", nargs="*", default=[],
                        help="extra owners allowed to lack a profile in this run")
    args = parser.parse_args()

    allowed_missing = EXPECTED_MISSING | set(args.expect_missing)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    owners = sorted({stage.get("owner") for stage in (registry.get("stages") or {}).values()
                     if isinstance(stage, dict) and isinstance(stage.get("owner"), str)
                     and stage["owner"] != "captain"})
    owners = sorted(set(owners) | {"dft-expert", "schematic-expert", "evolution-expert"})

    problems: list[str] = []
    report: list[str] = []
    for owner in owners:
        profile_id = OWNER_PROFILE.get(owner)
        if profile_id is None:
            if owner in allowed_missing:
                report.append(f"OK (deferred): {owner} has no profile yet (third batch)")
            else:
                problems.append(f"{owner}: no profile mapping and not in the deferred list")
            continue
        state, detail = profile_state(profile_id)
        if state == "published":
            report.append(f"OK: {owner} -> {detail}")
        elif owner in allowed_missing:
            report.append(f"OK (deferred): {owner} -> {profile_id} is {state} ({detail})")
        else:
            problems.append(f"{owner} -> {profile_id}: {state} ({detail})")

    for profile_id in sorted(p.name for p in PROFILES.iterdir() if p.is_dir()):
        if profile_id not in OWNER_PROFILE.values():
            problems.append(f"{profile_id}: profile on disk is mapped to no registry owner")

    for line in report:
        print(line)
    if problems:
        for line in problems:
            print(f"PROBLEM: {line}")
        return 2
    print("roster complete: every covered owner dispatches through a published profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
