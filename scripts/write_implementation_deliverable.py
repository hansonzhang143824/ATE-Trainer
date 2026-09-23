#!/usr/bin/env python3
"""Create ABI-correct IMPLEMENTATION handoffs only after the shared gate passes."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tm_for(trial: Path) -> str:
    return trial.name.replace("-ptc-v2", "").replace("-ptc", "").upper()


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def validate_manifest(trial: Path) -> tuple[dict, list[dict], str]:
    tm = tm_for(trial)
    manifest_path = trial / "implementation" / "implementation-manifest.json"
    method_path = trial / "method" / f"{tm.lower()}-test-method-contract.json"
    manifest = read_json(manifest_path)
    signed = manifest.get("signedInputs") or {}
    if signed.get("methodContractSha256") != sha256(method_path):
        raise ValueError(f"{trial.name}: manifest method-contract hash is stale")
    sources: list[dict] = []
    for change in manifest.get("changes") or []:
        source = Path(change.get("path", ""))
        expected = change.get("afterSha256")
        if not source.is_file() or not isinstance(expected, str) or sha256(source) != expected:
            raise ValueError(f"{trial.name}: manifest source hash is stale")
        sources.append({"path": str(source).replace("\\", "/"), "sha256": expected})
    if not sources:
        raise ValueError(f"{trial.name}: manifest needs at least one current source hash")
    return manifest, sources, str(manifest_path.relative_to(ROOT)).replace("\\", "/")


def write_ready(trial: Path, manifest: dict, sources: list[dict], artifact: str) -> Path:
    tm = tm_for(trial)
    handoff = {
        "schemaVersion": "PTC-HANDOFF-V1",
        "event": "deliverable_ready",
        "status": "success",
        "stage": "IMPLEMENTATION",
        "verdict": "deliverable_ready",
        "tm": tm,
        "nextRole": "rule-reviewer",
        "artifact": artifact,
        "sha256": sha256(trial / "implementation" / "implementation-manifest.json"),
        "source": sources[0]["path"],
        "sourceSha256": sources[0]["sha256"],
        "sources": sources,
        "signedInputs": manifest.get("signedInputs") or {},
    }
    path = trial / "implementation" / "deliverable-ready.json"
    path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trials", nargs="+", help="one or more tmNNN-ptc trial directories")
    args = parser.parse_args()
    trials = [Path(value).resolve() for value in args.trials]
    gate = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_implementation_batch.py"), *(str(x) for x in trials)],
        cwd=ROOT, text=True, capture_output=True, encoding="utf-8",
    )
    if gate.returncode:
        print(json.dumps({"status": "FAIL", "reason": "implementation gate failed", "gateOutput": gate.stdout + gate.stderr}, ensure_ascii=False, indent=2))
        return 1
    records = []
    for trial in trials:
        manifest, sources, artifact = validate_manifest(trial)
        handoff = write_ready(trial, manifest, sources, artifact)
        records.append({"tm": tm_for(trial), "handoff": str(handoff), "sourceHashes": sources})
    print(json.dumps({"status": "PASS", "handoffs": records}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
