# -*- coding: utf-8 -*-
"""Apply fieldAddressingRule to MY OWN scripts: find position-based addressing of contract fields or ledger entries, and classify each hit."""
import os, re, glob, json

RUN = r"team/artifacts/acceptance-20260916-dali10"
patterns = {
    "contract-position": re.compile(r"aliasResolution\s*\[\s*\d+\s*\]"),
    "ledger-position": re.compile(r"entries\s*\[\s*\d+\s*\]"),
    "list-position-generic": re.compile(r"(resolutions|anchors|limitations|aliases)\s*\[\s*\d+\s*\]"),
}
hits = {k: [] for k in patterns}
scanned = 0
for root, dirs, files in os.walk("."):
    if any(x in root for x in (".git", "node_modules")):
        continue
    for f in files:
        if not f.endswith(".py"):
            continue
        p = os.path.join(root, f)
        scanned += 1
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for name, rx in patterns.items():
            for m in rx.finditer(t):
                line = t[:m.start()].count("\n") + 1
                hits[name].append((p.replace("\\", "/"), line, m.group(0)))
print("python files scanned:", scanned)
for name, lst in hits.items():
    print("\n%s -> %d hit(s)" % (name, len(lst)))
    for p, line, frag in lst:
        print("   %s:%d  %s" % (p, line, frag))
