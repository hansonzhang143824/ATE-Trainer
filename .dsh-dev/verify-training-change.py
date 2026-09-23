#!/usr/bin/env python3
"""Post-change verification for the round-5 training change.

Checks the things that were claimed but not directly inspected before: that the
rule text and the executable case gate are present in BOTH the draft and the
PUBLISHED snapshot of each master, that the case files are still valid JSON, and
that re-applying the training script is a no-op.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "team" / "expert-profiles"
problems: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{'' if ok else ' — ' + detail}")
    if not ok:
        problems.append(label)


for profile_id in ("ptc-dft-expert", "ptc-schematic-expert"):
    directory = PROFILES / profile_id
    status = json.loads((directory / "status.json").read_text(encoding="utf-8"))
    version = status["publishedVersion"]

    # 1. draft: the case declares an executable gate
    case = json.loads((directory / "cases" / "TM106" / "expected.json").read_text(encoding="utf-8"))
    verification = case.get("verification") or {}
    check(f"{profile_id} draft case declares an executable gate",
          isinstance(verification.get("command"), str) and verification.get("expectExit") == 0,
          json.dumps(verification)[:120])
    check(f"{profile_id} draft instructions carry the training rule",
          "training round 1" in (directory / "instructions.md").read_text(encoding="utf-8").lower())
    check(f"{profile_id} draft changelog records the training round",
          "training round 1" in (directory / "changelog.md").read_text(encoding="utf-8").lower())

    # 2. the PUBLISHED snapshot carries the same rule — the thing that actually runs
    snapshot = directory / "versions" / version
    published_case = json.loads((snapshot / "cases" / "TM106" / "expected.json").read_text(encoding="utf-8"))
    published_verification = published_case.get("verification") or {}
    check(f"{profile_id}@{version} published snapshot carries the gate",
          published_verification.get("command") == verification.get("command"),
          f"draft {verification.get('command')!r} vs published {published_verification.get('command')!r}")
    check(f"{profile_id}@{version} published instructions carry the rule",
          "training round 1" in (snapshot / "instructions.md").read_text(encoding="utf-8").lower())
    check(f"{profile_id}@{version} published changelog carries the rule",
          "training round 1" in (snapshot / "CHANGELOG.md").read_text(encoding="utf-8").lower())
    check(f"{profile_id}@{version} snapshot file count matches its manifest",
          len([p for p in snapshot.rglob("*") if p.is_file()]) == len(json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))["files"]) + 1,
          "manifest.json itself is not listed")

# 3. re-applying the training script must change nothing (node runs the .mjs)
before = {str(p.relative_to(ROOT)): p.read_bytes() for p in PROFILES.rglob("*") if p.is_file() and "versions" not in p.parts}
completed = subprocess.run(["node", str(ROOT / ".dsh-dev" / "train-draft-rules.mjs")],
                           cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
output = (completed.stdout or "").strip()
print("--- re-run of train-draft-rules.mjs ---")
print(output)
check("training script exits 0 on a second run", completed.returncode == 0, (completed.stderr or "")[:200])
check("training script reports every file already up to date",
      output.count("already up to date") == 6, output.replace("\n", " | ")[:300])
after = {str(p.relative_to(ROOT)): p.read_bytes() for p in PROFILES.rglob("*") if p.is_file() and "versions" not in p.parts}
check("a second run changes no draft file", before == after,
      f"{sorted(set(before) ^ set(after))}")

print()
if problems:
    print(f"{len(problems)} PROBLEM(S): {problems}")
    raise SystemExit(1)
print("ALL TRAINING-CHANGE CHECKS PASS")
