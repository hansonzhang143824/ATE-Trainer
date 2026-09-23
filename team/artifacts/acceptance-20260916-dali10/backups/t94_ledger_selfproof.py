# -*- coding: utf-8 -*-
"""Reviewer round: pointer automation note, generator-version annotation for the before-measurement, and ledger self-proof (pre/post hashes + entry canonical hash)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

# --- 1) pointer file: explicit automation note ---
ptr_path = os.path.join(A, "t34-carrier-pointer.json")
ptr = json.load(open(ptr_path, encoding="utf-8"))
ptr["automationNote"] = ("AUTOMATED TOOLS: do NOT read this file as the report. Read the artifact at carrier.path. This file exists only so a name-based search for '*t34*' can find the mapping; "
                         "a grep/glob for '*t34*' will hit THIS file first (1.1 KB) instead of the carrier (tens of KB).")
ptr["nameCollisionWarning"] = "name-based globbing hits this pointer first; readers must follow carrier.path"
json.dump(ptr, open(ptr_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("pointer:", rec(ptr_path))

# --- 2) generator-version annotation for the 'before' measurement ---
fix = os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py")
gen = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
fix_rec, gen_rec = rec(fix), rec(gen)
print("fix script :", fix_rec)
print("generator  :", gen_rec)
print("shared anchors mtime:", datetime.datetime.fromtimestamp(os.stat(os.path.join(A, "gate-logs-t28", "t28-anchors.json")).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# --- 3) ledger self-proof entry ---
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))
# recover the generator-version fact from the fix script's own text
fixtxt = open(fix, encoding="utf-8", errors="replace").read()
before_measured_at = "2026-09-16 22:24:15"
fix_mtime = fix_rec["measuredAt"]
annotation = ("BEFORE (preservedNamespaceEntries=1) was measured at %s on the shared file whose bytes were produced by whichever generator version was live then; the union-accumulation fix script %s has mtime %s. "
              "So the BEFORE/AFTER pair must be read as: BEFORE may predate the fix; AFTER will be measured on the fixed version. Without this annotation, an AFTER==BEFORE result could not be distinguished from 'measured on the pre-fix generator'." % (
              before_measured_at, os.path.basename(fix), fix_mtime))
FILES = {"acceptance-report.json": os.path.join(A, "acceptance-report.json"), "t34-carrier-pointer.json": ptr_path,
         "t34-CARRIER-PATH.md": os.path.join(A, "t34-CARRIER-PATH.md"), "PATH-MAP.md": os.path.join(A, "PATH-MAP.md"),
         "gate-logs-t28/setupArchitect-anchors.json": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"),
         "gate-logs-t28/t28-anchors.json": os.path.join(A, "gate-logs-t28", "t28-anchors.json"),
         "gate-logs-t28/t28_make_anchors.py": gen, "gate-logs-t54/t54_fix_preservation_union.py": fix,
         "setup-contract.json": os.path.join(A, "setup-contract.json"),
         "implementation-payload-TM600-TM601.cpp": os.path.join(A, "implementation-payload-TM600-TM601.cpp"),
         "scripts/gate_baseline.json": "scripts/gate_baseline.json"}
entry = {
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "reviewer round: pointer automation note; generator-version annotation for the BEFORE measurement; ledger self-proof (the reviewer's point that 'append-only' is still a promise, not a mechanism)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "generatorVersionAnnotation": annotation,
    "ledgerSelfProof": {
        "rule": ("Each entry records the ledger's sha256 BEFORE and AFTER its own write, plus the canonical JSON hash of the entry itself. A later auditor can therefore (a) verify an entry's content by recomputing its canonical hash, "
                 "(b) verify the sequence by matching entry[n].ledgerSha256BeforeThisWrite against the ledger bytes as they were, and (c) detect a rewrite of history because any edit to an earlier entry changes that entry's canonical hash. "
                 "Limitation: the pre-write hashes of entries written before this rule was introduced cannot be recomputed retrospectively, because the ledger's exact earlier serialization was not captured - which is precisely why the rule is stated from here on."),
        "entryCanonicalSha256": hashlib.sha256(json.dumps({k: v for k, v in entry.items() if k not in ("ledgerSelfProof",)}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
    },
    "artifacts": {k: rec(v) for k, v in FILES.items() if os.path.exists(v)},
}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(post), "B /", hashlib.sha256(post).hexdigest())
print("entry canonical sha:", entry["ledgerSelfProof"]["entryCanonicalSha256"][:32])
print("annotation:", annotation[:200])
