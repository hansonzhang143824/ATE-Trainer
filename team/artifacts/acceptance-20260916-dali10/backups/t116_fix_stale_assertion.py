# -*- coding: utf-8 -*-
"""Fix the genuine stale assertion found by the audit (an entry asserting 'current 39,457 B / 2d0984d9... / K109 x1 / K110 x1 executable'), and refine the audit to judge context."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
f = os.path.join(A, "acceptance-report.json")
d = json.load(open(f, encoding="utf-8"))

# locate the stale statement
target = "content keys verified: K109 x1 / K110 x1 executable"
paths = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
    elif isinstance(node, str) and target in node:
        paths.append(".".join(path))
walk(d, [])
print("paths containing the stale statement:", paths)

def get(doc, path):
    cur = doc
    for part in path.split("."):
        if part.startswith("[") and part.endswith("]"):
            cur = cur[int(part[1:-1])]
        else:
            cur = cur[part]
    return cur

def setv(doc, path, value):
    parts = path.split(".")
    cur = doc
    for part in parts[:-1]:
        if part.startswith("[") and part.endswith("]"):
            cur = cur[int(part[1:-1])]
        else:
            cur = cur[part]
    last = parts[-1]
    if last.startswith("[") and last.endswith("]"):
        cur[int(last[1:-1])] = value
    else:
        cur[last] = value

FIX = (" CORRECTED (this sentence previously asserted the payload revision as '39,457 B / 2d0984d9...' with 'content keys verified: K109 x1 / K110 x1 executable', and it also carried the stale artifactSha256 2d0984d9...; both described an OLDER revision and were withdrawn elsewhere in this report): "
       "the live payload is 43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24; its TM600 SetOn is [13,48,57,60,61,76,83,85,126] - K48/K76 present, executable K109/K110 counts ZERO; "
       "ACM Set calls TM600=10 / TM601=0; SetOn TM600=1 / TM601=1. The older value is retained above only so the correction is legible.")

for p in paths:
    cur = get(d, p)
    if "CORRECTED (this sentence previously asserted" in cur:
        print("already corrected:", p)
        continue
    setv(d, p, cur + FIX)
    print("corrected:", p)

json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("\nt34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# refined audit: judge each occurrence's context instead of counting
t = b.decode("utf-8")
print("\nrefined sweep (context-aware):")
for m in re.finditer(r"K109 x1 / K110 x1 executable", t):
    ctx = t[max(0, m.start() - 200):m.end() + 120].replace("\n", " ")
    kind = "WITHDRAWAL/QUOTE" if re.search(r"withdrawn|earlier statement|previously asserted|CORRECTED", ctx, re.I) else "*** ASSERTION ***"
    print("  [%s] %s" % (kind, ctx[-150:]))
for m in re.finditer(r"2d0984d992d5d8cb", t):
    ctx = t[max(0, m.start() - 160):m.end() + 120].replace("\n", " ")
    kind = "HISTORY" if re.search(r"older|earlier|withdrawn|previously|superseded|CORRECTED", ctx, re.I) else "*** CURRENT-LOOKING ***"
    print("  [%s] %s" % (kind, ctx[-140:]))
