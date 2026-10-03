#!/usr/bin/env python3
"""Deterministic completeness check for a signed METHOD contract."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from ptc_contract_schema import validate_method_contract


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("--strategy-sha", required=True)
    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    errors = validate_method_contract(contract, args.strategy_sha)
    if errors:
        print("FAIL")
        print("\n".join(errors))
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
