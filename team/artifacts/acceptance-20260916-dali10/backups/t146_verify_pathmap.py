# -*- coding: utf-8 -*-
"""Verify that every path referenced in PATH-MAP.md resolves, resolving each against the repository root and the run directory."""
import os, re

RUN = "team/artifacts/acceptance-20260916-dali10/"
p = RUN + "PATH-MAP.md"
t = open(p, encoding="utf-8").read()
refs = sorted(set(re.findall(r"`([A-Za-z0-9_./-]+\.(?:json|jsonl|md|py|cpp))`", t)))
ok, bad = [], []
for r in refs:
    if os.path.exists(r) or os.path.exists(RUN + r):
        ok.append(r)
    else:
        bad.append(r)
print("PATH-MAP.md =", os.path.getsize(p), "B")
print("referenced paths:", len(refs), "| resolvable:", len(ok), "| unresolved:", len(bad))
for b in bad:
    print("   UNRESOLVED:", b)
print()
print("intentional historical mentions of the removed filename:")
for m in re.finditer(r"[^.]*t28-anchors\.snapshots\.json(?!l| )", t):
    print("   ", m.group(0).strip()[:160])
print()
print("real snapshot files:", [x.replace("\\", "/") for x in sorted(os.listdir(RUN + "gate-logs-t28")) if "snapshots" in x])
