#!/usr/bin/env python3
"""Read a DLP transparent-protected material file through Python's plaintext view.

This module is the single hash implementation used by PTC material gates.  Do
not replace it with PowerShell byte readers: those readers can see the DLP
wrapper instead of the CSV/XLSX plaintext.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_plaintext(path: Path | str) -> str:
    """Return the SHA-256 of the plaintext view exposed to Python."""
    material = Path(path)
    digest = hashlib.sha256()
    with material.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Hash a DLP material file through Python's plaintext view")
    parser.add_argument("path", type=Path)
    parser.add_argument("--expect", help="return 2 when the plaintext hash differs")
    parser.add_argument("--json", action="store_true", help="emit path and plaintext SHA-256 as JSON")
    args = parser.parse_args()
    try:
        digest = sha256_plaintext(args.path)
    except OSError as exc:
        parser.error(f"cannot read {args.path}: {exc}")
    payload = {"path": str(args.path), "sha256": digest, "view": "python-plaintext"}
    print(json.dumps(payload, ensure_ascii=False) if args.json else digest)
    return 0 if args.expect is None or digest == args.expect else 2


if __name__ == "__main__":
    raise SystemExit(main())
