#!/usr/bin/env python3
"""Create a non-production VS copy for Hardware Parse V2 compile validation.

The production VS tree and production project_config.json are read-only inputs.
Generated definitions and compiler outputs are written only below the V2
validation directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


IGNORED_DIRS = {"Backup", "debug", "Debug", "Release", ".vs", "ipch"}
IGNORED_SUFFIXES = {".obj", ".pdb", ".ilk", ".pch", ".tlog"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def copy_filter(_directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in IGNORED_DIRS}
    ignored.update(name for name in names if Path(name).suffix.lower() in IGNORED_SUFFIXES)
    return ignored


def require_child(path: Path, parent: Path) -> None:
    try:
        path.relative_to(parent)
    except ValueError as exc:
        raise ValueError(f"sandbox must remain below {parent}: {path}") from exc


def main() -> int:
    workspace = Path(__file__).resolve().parents[2]
    v2_dir = workspace / "Project" / "DALI" / "hardware_parse_v2"
    parser = argparse.ArgumentParser(description="Prepare isolated V2 VS compile sandbox")
    parser.add_argument(
        "--config",
        type=Path,
        default=v2_dir / "project_config.v2.json.txt",
    )
    parser.add_argument(
        "--sandbox",
        type=Path,
        default=v2_dir / "vs_compile_sandbox",
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    sandbox = args.sandbox.resolve()
    require_child(sandbox, v2_dir.resolve())
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))

    source_dir = Path(config["inputs"]["vs_src_dir"]).resolve()
    source_project = Path(config["inputs"]["vs_project"]).resolve()
    source_treg = Path(config["inputs"]["treg"]).resolve()
    for required in (source_dir, source_project, source_treg):
        if not required.exists():
            raise FileNotFoundError(required)

    sandbox_devel = sandbox / "devel"
    sandbox_source = sandbox_devel / "source"
    shutil.copytree(
        source_dir,
        sandbox_source,
        dirs_exist_ok=True,
        copy_function=shutil.copy2,
        ignore=copy_filter,
    )
    sandbox_devel.mkdir(parents=True, exist_ok=True)
    sandbox_treg = sandbox_devel / source_treg.name
    shutil.copy2(source_treg, sandbox_treg)

    sandbox_config = json.loads(json.dumps(config))
    sandbox_config["revision"] = f"{config.get('revision', 'v2')}-compile-sandbox"
    sandbox_config["inputs"].update(
        {
            "vs_project": str(sandbox_source / source_project.name),
            "channelmap": str(sandbox_source / Path(config["inputs"]["channelmap"]).name),
            "vs_src_dir": str(sandbox_source),
            "treg": str(sandbox_treg),
            "resource_definitions": str(
                sandbox_source / Path(config["inputs"]["resource_definitions"]).name
            ),
            "relay_definitions": str(
                sandbox_source / Path(config["inputs"]["relay_definitions"]).name
            ),
        }
    )
    compile_config_path = v2_dir / "project_config.v2.compile.json.txt"
    compile_config_path.write_text(
        json.dumps(sandbox_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    source_stdafx = source_dir / "StdAfx.h"
    sandbox_stdafx = sandbox_source / "StdAfx.h"
    source_test = source_dir / "test.cpp"
    sandbox_test = sandbox_source / "test.cpp"
    manifest = {
        "schema_version": 1,
        "mode": "isolated_compile_validation",
        "production_vs_modified": False,
        "source_vs_dir": str(source_dir),
        "sandbox_vs_dir": str(sandbox_source),
        "compile_config": str(compile_config_path),
        "baseline_hashes": {
            "production_stdafx_sha256": sha256(source_stdafx),
            "sandbox_stdafx_sha256": sha256(sandbox_stdafx),
            "production_test_cpp_sha256": sha256(source_test),
            "sandbox_test_cpp_sha256": sha256(sandbox_test),
        },
    }
    manifest_path = v2_dir / "compile_sandbox_manifest.v2.json.txt"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"V2 compile sandbox: {sandbox_source}")
    print(f"V2 compile config: {compile_config_path}")
    print("Production VS modified: False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
