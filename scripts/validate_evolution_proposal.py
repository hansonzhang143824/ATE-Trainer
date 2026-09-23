#!/usr/bin/env python3
"""Validate an evolution-expert rule-improvement proposal (third batch).

A proposal is only valid if it binds to a real closed run (its evidence batch
directory exists on disk) and satisfies the output contract schema. The
evolution expert never publishes active rules itself; this gate only checks
that what it produced is auditable.

Exit code 0 = proposal valid; 2 = invalid.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_ENUM = {"PROPOSED", "ACCEPTED", "REJECTED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proposal", type=Path, help="path to the proposal JSON")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        proposal = json.loads(args.proposal.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "errors": [f"proposal unreadable: {error}"]}, ensure_ascii=False, indent=2))
        return 2

    for key in ("proposalId", "evidenceBatch", "evidenceArtifacts", "ruleChange", "rationale", "status"):
        if key not in proposal:
            errors.append(f"missing required field {key}")
    if not errors:
        if not isinstance(proposal.get("proposalId"), str) or len(proposal["proposalId"]) < 3:
            errors.append("proposalId must be a string of at least 3 characters")
        batch = proposal.get("evidenceBatch")
        if not isinstance(batch, str) or not (ROOT / "team" / "artifacts" / batch).is_dir():
            errors.append(f"evidenceBatch {batch!r} is not a closed batch under team/artifacts")
        artifacts = proposal.get("evidenceArtifacts")
        if not isinstance(artifacts, list) or len(artifacts) < 1 or not all(isinstance(a, str) for a in artifacts):
            errors.append("evidenceArtifacts must be a non-empty array of strings")
        if not isinstance(proposal.get("ruleChange"), dict):
            errors.append("ruleChange must be an object")
        rationale = proposal.get("rationale")
        if not isinstance(rationale, str) or len(rationale) < 20:
            errors.append("rationale must be a string of at least 20 characters")
        if proposal.get("status") not in STATUS_ENUM:
            errors.append(f"status must be one of {sorted(STATUS_ENUM)}")

    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps({"status": "PASS", "proposalId": proposal["proposalId"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
