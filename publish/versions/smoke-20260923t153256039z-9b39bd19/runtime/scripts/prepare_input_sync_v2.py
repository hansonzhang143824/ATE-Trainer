#!/usr/bin/env python3
"""Per-role INPUT_SYNC aggregation.

The legacy collector still prepares the manifest's source row details.  This
entrypoint replaces its aggregate artifact verdict with two role-local gate
reports.  It never declares a TM COMPLETE.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import validate_dft_outputs
import validate_schematic_outputs
from material_plaintext_hash import sha256_plaintext

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tm", required=True)
    parser.add_argument("--trial-dir", required=True)
    args = parser.parse_args()
    trial = Path(args.trial_dir).resolve()
    legacy = ROOT / "scripts" / "prepare_input_sync.py"
    completed = subprocess.run([sys.executable, str(legacy), "--tm", args.tm, "--trial-dir", str(trial)], cwd=ROOT)
    manifest_path = trial / "input-manifest.json"
    if not manifest_path.is_file():
        return completed.returncode or 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") == "blocked":
        return completed.returncode or 2

    dft_gate = validate_dft_outputs.validate(args.tm)
    schematic_gate = validate_schematic_outputs.validate()
    confirmed = ROOT / "project" / "DALI" / "Input_GlobalMaterial" / "sch_confirmed.json"
    schematic_gate["regenerationCommand"] = (
        "python scripts/generate_schematic_txt.py --source "
        "project/DALI/Input_GlobalMaterial/Dali-SCH.csv --confirmed "
        "project/DALI/Input_GlobalMaterial/sch_confirmed.json --cbit project/DALI/Input_GlobalMaterial/CBIT表-DALI.xlsx --out-dir "
        "project/DALI/Output_Global_Material/schematic --expected-source-sha "
        + schematic_gate["canonicalInput"]["sha256"]
        + " --expected-confirmed-sha " + sha256_plaintext(confirmed) + " --expected-cbit-sha " + sha256_plaintext(ROOT / "project" / "DALI" / "Input_GlobalMaterial" / "CBIT表-DALI.xlsx")
    )
    for key, gate in (("dft", dft_gate), ("schematic", schematic_gate)):
        item = manifest["canonicalInputs"][key]
        item.update({
            "path": gate["canonicalInput"]["path"], "sha256": gate["canonicalInput"]["sha256"],
            "requiredOutputs": gate["requiredOutputs"], "missingOrStaleOutputs": gate["missingOrStaleOutputs"],
            "status": gate["status"],
        })
    stale = [role for role, gate in (("dft", dft_gate), ("schematic", schematic_gate)) if gate["status"] != "ready"]
    manifest["schemaVersion"] = 8
    manifest["roleGates"] = {"dft-expert": dft_gate, "schematic-expert": schematic_gate}
    manifest["globalGate"] = {
        "name": "INPUT_SYNC_AGGREGATE", "status": "ready" if not stale else "pending",
        "meaning": "Aggregates source-role gates only. Task COMPLETE is decided solely by the final PTC gate.",
    }
    manifest["status"] = "ready" if not stale else "needs-derived-artifacts"
    manifest["dispatchableRoles"] = [f"{role}-expert" for role in stale]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{manifest['status'].upper()}: {manifest_path}")
    print("DISPATCH=" + ",".join(manifest["dispatchableRoles"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
