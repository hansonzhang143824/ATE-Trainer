#!/usr/bin/env python3
"""Publish one expert master profile version (handoff section 6.2).

Order is fixed and non-negotiable:
  1. evaluate the DRAFT — a failed draft is refused, and nothing is written;
  2. refuse to overwrite an existing ``versions/<vN>/`` (snapshots are immutable);
  3. copy the draft assets into ``versions/<vN>/``;
  4. write a hash manifest over exactly those files;
  5. record the version, its digest and the previous version in ``status.json``.

The previous published version is never deleted, so a rollback is a pointer move
in ``status.json`` rather than a rebuild.

    python scripts/publish_expert_profile.py --profile ptc-dft-expert --version v1

Exit codes: 0 = published, 2 = refused (with the reason), 1 = usage error.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import expert_profile as ep  # noqa: E402
from evaluate_expert_profile import evaluate  # noqa: E402


def _refuse(reason: str, **extra) -> dict:
    return {"schemaVersion": 1, "published": False, "reason": reason, **extra}


def publish(profile_id: str, version: str, *, skip_regression: bool = False, skip_case_gates: bool = False, now: datetime | None = None) -> dict:
    if not ep.VERSION_PATTERN.match(version):
        return _refuse(f"version must look like v<n>, received {version!r}")
    directory = ep.profile_dir(profile_id)
    if not directory.is_dir():
        return _refuse(f"unknown expert profile {profile_id!r}")

    report = evaluate(profile_id, skip_regression=skip_regression, skip_case_gates=skip_case_gates)
    if report["verdict"] != "pass":
        # Refusal is a hard stop: no snapshot directory is created.
        return _refuse("the draft evaluation failed, so nothing was published",
                       failedChecks=report["failed"], evaluation=report)

    target = directory / "versions" / version
    if target.exists():
        return _refuse(f"{target} already exists; a published version is immutable — choose another version")

    inventory = ep.asset_inventory(profile_id)
    for relative in sorted(inventory):
        source = directory / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    published_inventory = ep.asset_inventory(profile_id)
    published_files = {relative: digest for relative, digest in published_inventory.items() if not relative.startswith("versions/")}
    snapshot_files = {}
    for relative in sorted(inventory):
        snapshot_files[relative] = ep.sha256_file(target / relative)
    manifest = {
        "schemaVersion": 1,
        "profileId": profile_id,
        "version": version,
        "publishedAt": (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z"),
        "executionClass": (ep.load_profile(profile_id)[0] or {}).get("executionClass"),
        "evaluation": {"verdict": report["verdict"], "failed": report["failed"], "caseCount": report["caseCount"], "checks": report["checks"]},
        "files": snapshot_files,
        "digest": ep.snapshot_digest(snapshot_files),
    }
    ep.write_json(target / "manifest.json", manifest)

    status_path = directory / "status.json"
    status = ep.read_json(status_path)
    status = status if isinstance(status, dict) else {"schemaVersion": 1, "profileId": profile_id}
    previous = status.get("publishedVersion")
    history = status.get("history") if isinstance(status.get("history"), list) else []
    history.append({"version": version, "publishedAt": manifest["publishedAt"], "digest": manifest["digest"], "previousVersion": previous})
    status.update({
        "schemaVersion": 1,
        "profileId": profile_id,
        "draftEvaluation": {"verdict": report["verdict"], "failed": report["failed"], "caseCount": report["caseCount"], "assetDigest": report["assetDigest"]},
        "publishedVersion": version,
        "previousVersion": previous,
        "publishedAt": manifest["publishedAt"],
        "manifestDigest": manifest["digest"],
        "history": history,
    })
    ep.write_json(status_path, status)

    return {
        "schemaVersion": 1,
        "published": True,
        "profileId": profile_id,
        "version": version,
        "previousVersion": previous,
        "manifest": str(target / "manifest.json"),
        "manifestDigest": manifest["digest"],
        "fileCount": len(snapshot_files),
        "draftFileCount": len(published_files),
        "status": str(status_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish an evaluated expert master profile version")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--skip-regression", action="store_true")
    args = parser.parse_args()
    result = publish(args.profile, args.version, skip_regression=args.skip_regression)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("published") else 2


if __name__ == "__main__":
    raise SystemExit(main())
