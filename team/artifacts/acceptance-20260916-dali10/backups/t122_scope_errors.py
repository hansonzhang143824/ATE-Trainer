# -*- coding: utf-8 -*-
"""Correct two scope errors of my own: the removed superseded-scratch path, and the top-level-only 'no blocked filename' claim. Record the scope rule."""
import json, hashlib, os, datetime, re, glob

A = r"team/artifacts/acceptance-20260916-dali10"
f = os.path.join(A, "acceptance-report.json")
d = json.load(open(f, encoding="utf-8"))

# gather the true facts, scope-qualified
blocked = []
for root, dirs, files in os.walk(A):
    for x in files:
        if "blocked" in x.lower():
            blocked.append(os.path.join(root, x).replace("\\", "/"))
t34files = sorted(p.replace("\\", "/") for p in glob.glob("**/*t34*", recursive=True))
print("blocked-named files (recursive):", blocked)
print("t34-named paths (recursive):", t34files)
print("superseded-scratch exists:", os.path.exists(os.path.join(A, "backups", "superseded-scratch")))

CORR = (("CORRECTED (my own scope error, reported by test-strategy-architect): an earlier statement of mine said no file in the run directory has 'blocked' in its name. That check had only listed the TOP LEVEL of the run directory. "
         "A recursive walk finds TWO: gate-logs-t33/t33-blocked-before-anchors.json and gate-logs-t33/t33-blocked-after-anchors.json. "
         "Rule adopted: any 'whole tree' or 'does not exist' assertion must state its scan scope explicitly, including subdirectories - a top-level listing is not a tree scan."),)

pathfix_old = "backups/superseded-scratch/t60_apply_captain_t34_t35_t41.py"
pathfix_new = "backups/t60_apply_captain_t34_t35_t41.py (the superseded-scratch sub-directory no longer exists - verified: os.path.exists(...)=False; the script now sits directly under backups/)"

changed = []
def fix_strings(node, path):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            fix_strings(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            fix_strings(v, path + ["[%d]" % i])
    elif isinstance(node, str):
        new = node
        if pathfix_old in new:
            new = new.replace(pathfix_old, pathfix_new)
        if "文件里面" in new:
            pass
        if re.search(r"no file (?:name|with) .{0,30}blocked", new, re.I) or ("blocked" in new.lower() and "不存在" in new and "文件" in new):
            new = new + " " + CORR[0]
        if new != node:
            parent = d
            for part in path[:-1]:
                parent = parent[int(part[1:-1])] if part.startswith("[") else parent[part]
            last = path[-1]
            if last.startswith("[") and last.endswith("]"):
                parent[int(last[1:-1])] = new
            else:
                parent[last] = new
            changed.append(".".join(path))
fix_strings(d, [])

# also append a summary entry so the correction is explicit
d["limitations"].append(
    "L50 (TWO SCOPE ERRORS OF MINE, corrected after test-strategy-architect's re-measurement): "
    "(1) I wrote that 'the run directory contains no file with blocked in its name'; that check listed only the top level - a recursive walk finds two files: " + ", ".join(blocked) + ". "
    "(2) I cited the script path backups/superseded-scratch/t60_apply_captain_t34_t35_t41.py; that sub-directory no longer exists (measured: exists() = False) and the script now sits at backups/t60_apply_captain_t34_t35_t41.py. "
    "Both are the same failure mode as the basename misses elsewhere in this run: an assertion about 'the whole tree' or 'does not exist' made from a partial scan. "
    "Rule adopted for my own artefacts: state the scan scope with every existence/absence assertion, and never generalise a top-level listing to a tree. Current t34-named paths (recursive): " + "; ".join(t34files) + ".")

json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("\nchanged fields:", changed)
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

# anchors: record the scope rule
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["scopeRule"] = ("Any assertion of the form 'the whole tree', 'no such file' or 'does not exist' must state the scan scope explicitly, including sub-directories. A top-level listing is not a tree scan. "
                    "Two instances in this run came from my own partial scans (a basename-only search, and a top-level-only 'no blocked filename' claim); the counterparty had the mirrored instance.")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())

# ledger
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "corrected two scope errors of mine (top-level-only 'no blocked filename' claim; removed superseded-scratch path) and adopted the scope rule",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "scopeErrorsCorrected": {"blockedNamedFiles": blocked, "supersededScratchExists": os.path.exists(os.path.join(A, "backups", "superseded-scratch")),
                                   "t34NamedPaths": t34files, "scopeRule": doc["scopeRule"]},
         "artifacts": {"acceptance-report.json": {"path": f.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                                                   "measuredAt": datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
