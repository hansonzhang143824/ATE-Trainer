"""Validate that PTC role prompts expose the gate-owned output ABI before dispatch."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "team/ptc/OUTPUT_CONTRACTS.md": (
        "strategy/<tm-lower>-resource-config-contract.json",
        "stage = STRATEGY",
        "stage = METHOD",
        "stage = RULE_REVIEW_METHOD",
        "stage = IMPLEMENTATION",
        "stage = RULE_REVIEW_IMPLEMENTATION",
        "stage = COMPILE",
        "FAST_DELIVERY_PENDING_AUDIT",
        "--resume-audit --batch <id>",
    ),
    "team/roles/test-strategy-architect.md": (
        "team/ptc/OUTPUT_CONTRACTS.md",
        "strategy/<tm-lower>-resource-config-contract.json",
        "validate_strategy_contract.py",
        "nextRole=test-method-expert",
    ),
    "team/roles/test-method-expert.md": (
        "team/ptc/OUTPUT_CONTRACTS.md",
        "method/<tm-lower>-test-method-contract.json",
        "stage=METHOD",
    ),
    "team/roles/rule-reviewer.md": ("team/ptc/OUTPUT_CONTRACTS.md", "Deferred implementation audit"),
    "team/roles/ate-implementer.md": ("team/ptc/OUTPUT_CONTRACTS.md",),
    "team/roles/compile-diagnostician.md": ("team/ptc/OUTPUT_CONTRACTS.md", "Per-batch fast delivery compile"),
}

def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative, markers in REQUIRED.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing required ABI marker: {marker}")
    return errors

def main() -> int:
    errors = validate()
    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
