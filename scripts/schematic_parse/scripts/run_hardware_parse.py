#!/usr/bin/env python3
"""ATE hardware parse action.

CSV schematic parsing is the sole production pipeline: the adapter materializes
a synthetic EDIF from the Altium CSV and runs the six-gate/path engine, then the
downstream CBIT/path definitions are regenerated from the canonical outputs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("\n>>> " + " ".join(command))
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def _workspace_root(start: Path) -> Path:
    """上溯找 project_config.json 所在目录 = workspace 根 (config 权威位置)。"""
    d = start
    while not (d / "project_config.json").is_file():
        d = d.parent
    return d


def main() -> int:
    package = Path(__file__).resolve().parents[1]     # <workspace>/scripts/schematic_parse
    scripts_root = package.parent                     # <workspace>/scripts (gen_*.py 所在)
    workspace = _workspace_root(scripts_root)
    parser = argparse.ArgumentParser(description="ATE schematic hardware parse action")
    parser.add_argument("--publish-definitions", action="store_true")
    args = parser.parse_args()

    config = workspace / "project_config.json"
    active = json.loads(config.read_text(encoding="utf-8-sig"))
    map_path = (workspace / active["intermediates"]["sch_connect_map"]).resolve()
    stat_path = (workspace / active["intermediates"]["component_statistic"]).resolve()
    run([sys.executable, str(package / "scripts" / "csv_schematic_adapter_v2.py")], workspace)
    run([sys.executable, str(package / "scripts" / "csv_pathproof_v2.py")], workspace)
    path_command = [
        sys.executable, str(scripts_root / "gen_path_defines.py"),
        "--config", str(config), "--map", str(map_path),
    ]
    if not args.publish_definitions:
        path_command.append("--no-write")
    else:
        active = json.loads((workspace / "project_config.json").read_text(encoding="utf-8-sig"))
        stdafx = Path(active["inputs"]["relay_definitions"]).resolve()
        backup_dir = stdafx.parent / "Backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = backup_dir / f"StdAfx.h.before_hardware_parse_{stamp}.bak"
        shutil.copy2(stdafx, backup)
        print(f"Production definition backup: {backup}")
    run(path_command, workspace)
    run(
        [
            sys.executable, str(scripts_root / "gen_cbit_defines.py"),
            "--config", str(config), "--stat", str(stat_path), "--map", str(map_path),
        ],
        workspace,
    )
    print("HARDWARE PARSE: PASS")
    print(f"PathProof: {map_path.parent / 'path_proofs.json.txt'}")
    print("Definitions published: " + str(args.publish_definitions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
