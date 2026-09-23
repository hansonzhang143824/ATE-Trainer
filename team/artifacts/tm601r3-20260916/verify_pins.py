# -*- coding: utf-8 -*-
"""Recompute every pin in team/artifacts/tm601r3-20260916/pin/snapshot-manifest.json
and report drift. Read-only: never writes. Usage:  python verify_pins.py"""
import hashlib
import json
import os
import sys

RUN = os.path.dirname(os.path.abspath(__file__))
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")


def sig(path):
    with open(path, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


def main():
    man = json.load(open(PIN, encoding="utf-8"))
    drift = []
    checked = 0
    for group in ("files", "captainPrecheck", "captainPrecheckAddendum1",
                  "subagentDiffReport", "decisionBoard"):
        block = man.get(group) or {}
        items = block.items() if group == "files" else [(group, block)]
        for name, rec in items:
            path = (rec or {}).get("path")
            if not path:
                continue
            if not os.path.exists(path):
                drift.append((group, name, "GONE", None, rec))
                continue
            size, sha = sig(path)
            checked += 1
            if size != rec.get("size") or sha != rec.get("sha256"):
                drift.append((group, name, "DRIFT", (size, sha), rec))
    print("pins checked:", checked)
    if not drift:
        print("RESULT: ALL PINS MATCH")
        return 0
    print("RESULT: %d DRIFT/GONE" % len(drift))
    for group, name, kind, cur, rec in drift:
        print("  %-8s %-26s %s" % (kind, name, group))
        print("      pinned: %s %s" % (rec.get("size"), (rec.get("sha256") or "")[:24]))
        if cur:
            print("      now   : %s %s" % (cur[0], cur[1][:24]))
    return 1


if __name__ == "__main__":
    sys.exit(main())
