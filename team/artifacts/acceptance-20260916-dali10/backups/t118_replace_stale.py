# -*- coding: utf-8 -*-
"""Replace (not just annotate) the stale current-state claims about the payload revision, and label per-entry artifact hashes as historical."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
f = os.path.join(A, "acceptance-report.json")
d = json.load(open(f, encoding="utf-8"))
OLD_SHA = "2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9"
POLICY = os.path.join(A, "implementation-payload-TM600-TM601.cpp")
pb = open(POLICY, "rb").read()
NEW = {"path": "team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp",
       "sizeBytes": len(pb), "sha256": hashlib.sha256(pb).hexdigest(),
       "measuredAt": datetime.datetime.fromtimestamp(os.stat(POLICY).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
print("current canonical payload:", NEW["sizeBytes"], "B /", NEW["sha256"][:24])

STALE_PHRASES = [
    ("current 39,457 B / 2d0984d9...", "an older revision (39,457 B; superseded - see currentCanonicalArtifact)"),
    ("content keys verified: K109 x1 / K110 x1 executable, ACM Sets TM600=10 / TM601=0, SetOn TM600=1 / TM601=1",
     "content keys of THAT older revision were K109 x1 / K110 x1 executable, ACM Sets TM600=10 / TM601=0, SetOn TM600=1 / TM601=1; the CURRENT canonical payload instead closes K48/K76 with executable K109/K110 = 0"),
]

changed = []
def walk(node, path):
    if isinstance(node, dict):
        if node.get("artifactSha256") == OLD_SHA and "artifactSha256IsHistorical" not in node:
            node["artifactSha256IsHistorical"] = ("true - this hash records the payload revision that was reviewed at the time; it is not the current canonical payload")
            node["currentCanonicalArtifact"] = NEW
            changed.append(".".join(path) + ".artifactSha256")
        for k, v in list(node.items()):
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
    elif isinstance(node, str):
        new = node
        for a, b in STALE_PHRASES:
            if a in new:
                new = new.replace(a, b)
        if new != node:
            changed.append(".".join(path) + " (evidence text)")
            # write back via parent
            parent = d
            for part in path[:-1]:
                parent = parent[int(part[1:-1])] if part.startswith("[") else parent[part]
            last = path[-1]
            if last.startswith("[") and last.endswith("]"):
                parent[int(last[1:-1])] = new
            else:
                parent[last] = new
walk(d, [])
print("changed fields:", changed)
json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

t = b.decode("utf-8")
print("\ncontext-aware re-sweep:")
for m in re.finditer(r"K109 x1 / K110 x1 executable", t):
    ctx = t[max(0, m.start() - 220):m.end() + 100].replace("\n", " ")
    kind = "WITHDRAWAL/QUOTE" if re.search(r"withdrawn|earlier statement|previously asserted|older revision|CORRECTED", ctx, re.I) else "*** ASSERTION ***"
    print("  [%s] %s" % (kind, ctx[-140:]))
labeled = 0
for m in re.finditer(OLD_SHA, t):
    ctx = t[max(0, m.start() - 120):m.end() + 200].replace("\n", " ")
    if "IsHistorical" in ctx or "older revision" in ctx or "not the current canonical" in ctx:
        labeled += 1
    else:
        print("  *** unlabeled old-hash site ***: %s" % ctx[-120:])
print("old-hash sites labelled historical:", labeled)
