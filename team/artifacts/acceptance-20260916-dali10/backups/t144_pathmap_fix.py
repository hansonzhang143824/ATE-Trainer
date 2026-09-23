# -*- coding: utf-8 -*-
"""Fix the wrong filename in PATH-MAP.md and the anchors pathMap (t28-anchors.snapshots.json does not exist; the real files are .meta.json and .jsonl), and state the path BASE explicitly."""
import json, hashlib, os, datetime, glob

A = r"team/artifacts/acceptance-20260916-dali10"
RUN = "team/artifacts/acceptance-20260916-dali10"
real = [p.replace("\\", "/") for p in glob.glob(A + "gate-logs-t28/t28-anchors.snapshots*")]
print("real snapshot files:", real)

md = """# Run path map (who carries which task's artifact)

**PATH BASE (added after test-strategy-architect's verification): every path below is relative to the REPOSITORY ROOT `D:/Newtest/DSH/ATE-Coding-Plat`. A path that lives inside the run directory therefore starts with `%s/`; `scripts/...` is at the repository root, NOT inside the run directory.`

Written by `setup-architect` because this run produced several false MISSING cases from name/path ambiguity (basename-only searches, and one base-directory mismatch). **Rule: cite by full path + recomputed sha256 at citation time; never cite a remembered hash; state the base of any path list.**

| task / role | artifact (relative to the repository root) |
|---|---|
| `t34` (acceptance report; verdict `blocked`) | `%s/acceptance-report.json` — **there is NO file named `t34*`; `t34` is a task label.** Its entries live in that JSON's `limitations[]`. Pointer files: `t34-carrier-pointer.json`, `t34-CARRIER-PATH.md` |
| `t35` | `%s/t35-contract-reconciliation.md` |
| `t41` | `%s/t41-tm601-bst-path-determination.md` |
| `t49` / `t53` (contract work) | `%s/setup-contract-build.py` (generator) |
| contract | `%s/setup-contract.json` (+ `setup-contract-pin.json`) |
| plan side | `%s/test-plan.json` (owner: test-strategy-architect) + `%s/implementation-input-pin.json` (owner: setup-architect) |
| payload (canonical, writes stopped) | `%s/implementation-payload-TM600-TM601.cpp` |
| anchors | `%s/gate-logs-t28/setupArchitect-anchors.json` (owner: setup-architect) / `%s/gate-logs-t28/t28-anchors.json` (owner: compile-diagnostician) |
| snapshot ledgers | `%s/gate-logs-t28/setupArchitect-freeze-snapshots.json` (owner: setup-architect, append-only) / `%s/gate-logs-t28/t28-anchors.snapshots.jsonl` (owner: compile-diagnostician) |
| peer ledger metadata | `%s/gate-logs-t28/t28-anchors.snapshots.meta.json` (CORRECTED: an earlier revision of this table said `t28-anchors.snapshots.json`, which does not exist) |
| gate script / baseline | `scripts/verify_bst_sw_sequence.py` (**repository root**) / `scripts/gate_baseline.json` (28 B, untouched) |

**Gate-read field** (the only contract field the bst-sw gate consumes):
`%s/setup-contract.json` → `aliasResolution[bst2sw].resolution.closedRelayNumbers` = `[48, 60, 61, 76]`,
which yields the TM600 expectation `[48, 60, 61, 76, 83]`.

**Frozen vs live (as declared by the owning side):** FROZEN = `setup-contract.json`, `setup-contract-build.py`, `setup-contract-pin.json`, and the canonical payload. Everything else (reports, `t35`, `t41`, pins, anchors, ledgers, the plan) is a **live file** — cite with a timestamp, never with a bare hash.
""" % tuple([RUN] * 15)
p = os.path.join(A, "PATH-MAP.md")
open(p, "w", encoding="utf-8").write(md)
b = open(p, "rb").read()
print("PATH-MAP.md:", len(b), "B /", hashlib.sha256(b).hexdigest())
t = b.decode("utf-8")
print("  wrong name still present:", "t28-anchors.snapshots.json" in t.replace("t28-anchors.snapshots.jsonl", "").replace("t28-anchors.snapshots.meta.json", ""))
print("  base line present:", "PATH BASE" in t)

# fix the anchors pathMap
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
pm = doc.get("pathMap", {})
fixed = {}
for k, v in pm.items():
    if isinstance(v, str) and "t28-anchors.snapshots.json" in v and "meta" not in v:
        v = v.replace("t28-anchors.snapshots.json", "t28-anchors.snapshots.meta.json (+ t28-anchors.snapshots.jsonl)")
    fixed[k] = v
doc["pathMap"] = fixed
doc["pathBase"] = "all paths in this file are relative to the repository root D:/Newtest/DSH/ATE-Coding-Plat unless stated otherwise; run-directory artifacts carry the team/artifacts/acceptance-20260916-dali10/ prefix"
doc["pathMapCorrection"] = "an earlier revision named gate-logs-t28/t28-anchors.snapshots.json, which does not exist; the real files are t28-anchors.snapshots.meta.json and t28-anchors.snapshots.jsonl (raised by test-strategy-architect)"
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("  pathMap clean:", "snapshots.json'" not in json.dumps(doc["pathMap"], ensure_ascii=False))

# ledger
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "fixed the one genuine error in my path table (a filename that does not exist) and stated the path BASE explicitly, per test-strategy-architect's verification",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "pathMapAudit": {"theirResult": "19 references: 17 resolved, 1 was their base-directory artefact (the gate script lives at the repository root), 1 was a genuine error of mine",
                          "error": "gate-logs-t28/t28-anchors.snapshots.json does not exist; the real files are t28-anchors.snapshots.meta.json and t28-anchors.snapshots.jsonl",
                          "fixedIn": ["PATH-MAP.md (rewritten with a PATH BASE header and corrected rows)", "setupArchitect-anchors.json pathMap + new pathBase/pathMapCorrection fields"],
                          "ruleAdded": "a path list must state the directory its paths are relative to; otherwise a correct list still yields false MISSING results (three such cases in this run so far)"},
         "artifacts": {"PATH-MAP.md": {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest()},
                       "gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
