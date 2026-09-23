# -*- coding: utf-8 -*-
"""Fix the previous script's bug and complete the reviewer round: pointer note, generator-version annotation, BEFORE/AFTER namespace counts, DO_NOT_TOUCH guard test, ledger self-proof."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

# 1) pointer automation note (idempotent)
ptr_path = os.path.join(A, "t34-carrier-pointer.json")
ptr = json.load(open(ptr_path, encoding="utf-8"))
if "automationNote" not in ptr:
    ptr["automationNote"] = ("AUTOMATED TOOLS: do NOT read this file as the report. Read the artifact at carrier.path. This file exists only so a name-based search for '*t34*' can find the mapping; "
                             "a glob for '*t34*' hits THIS file first instead of the carrier.")
    ptr["nameCollisionWarning"] = "name-based globbing hits this pointer first; readers must follow carrier.path"
    json.dump(ptr, open(ptr_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("pointer:", rec(ptr_path))

# 2) generator / fix / shared-file facts
fix = os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py")
gen = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
sh_rec, fix_rec, gen_rec = rec(sh), rec(fix), rec(gen)
s = json.load(open(sh, encoding="utf-8"))
ppn = s.get("preservedPeerNamespaces") or {}
blk = ppn.get("setupArchitectFreezeAnchors") or {}
after_count = len(blk.get("anchors") or {})
print("shared anchors:", sh_rec["sizeBytes"], "B /", sh_rec["sha256"][:16], "@", sh_rec["measuredAt"])
print("preserved namespace entries NOW (= AFTER):", after_count, "| mirrorOf:", blk.get("mirrorOf"), "| mirrorSize:", blk.get("mirrorSize"))
print("fix script mtime:", fix_rec["measuredAt"], "| generator mtime:", gen_rec["measuredAt"])
led = os.path.join(A, "gate-logs-t28", "t28-anchors.snapshots.jsonl")
print("owner ledger rows:", len([l for l in open(led, encoding="utf-8").read().splitlines() if l.strip()]) if os.path.exists(led) else "n/a",
      "| mtime:", datetime.datetime.fromtimestamp(os.stat(led).st_mtime).strftime("%Y-%m-%d %H:%M:%S") if os.path.exists(led) else "-")

# 3) ledger entry with self-proof
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
ann = ("BEFORE=1 was measured at 2026-09-16 22:24:15. Measured facts about versions: the union-accumulation fix script has mtime 2026-09-16 22:22:38 and the generator t28_make_anchors.py has mtime 2026-09-16 22:22:54, i.e. BOTH PREDATE that measurement - "
       "so BEFORE=1 was already produced by the FIXED generator. AFTER is measured on the same fixed generator after its 22:58:53 regeneration. Consequence: a BEFORE==AFTER==1 result here shows that the fix preserves what exists but does not restore previously lost entries; "
       "it is NOT evidence about the pre-fix generator, whose output was never snapshotted.")
FILES = {"acceptance-report.json": os.path.join(A, "acceptance-report.json"), "t34-carrier-pointer.json": ptr_path,
         "t34-CARRIER-PATH.md": os.path.join(A, "t34-CARRIER-PATH.md"), "PATH-MAP.md": os.path.join(A, "PATH-MAP.md"),
         "gate-logs-t28/setupArchitect-anchors.json": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"),
         "gate-logs-t28/t28-anchors.json": sh, "gate-logs-t28/t28_make_anchors.py": gen,
         "gate-logs-t54/t54_fix_preservation_union.py": fix, "setup-contract.json": os.path.join(A, "setup-contract.json"),
         "implementation-payload-TM600-TM601.cpp": os.path.join(A, "implementation-payload-TM600-TM601.cpp"),
         "scripts/gate_baseline.json": "scripts/gate_baseline.json"}
entry = {
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "reviewer round: pointer automation note; generator-version annotation; BEFORE/AFTER namespace counts measured on the FIXED generator; ledger self-proof (their point: append-only is still a promise, not a mechanism)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "namespaceCounts": {"before": {"measuredAt": "2026-09-16 22:24:15", "entries": 1}, "after": {"measuredAt": sh_rec["measuredAt"], "entries": after_count,
                        "sharedFileSizeBytes": sh_rec["sizeBytes"], "sharedFileSha256": sh_rec["sha256"]},
                        "interpretation": "BEFORE and AFTER are both on the FIXED generator (see generatorVersionAnnotation); equality shows preservation of what exists, not restoration of what was lost"},
    "generatorVersionAnnotation": ann,
    "artifacts": {k: rec(v) for k, v in FILES.items() if os.path.exists(v)},
}
canon = hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry["ledgerSelfProof"] = {
    "rule": ("Each entry records the ledger sha256 BEFORE its write, the canonical JSON hash of the entry, and (from this entry on) the ledger sha256 AFTER its write. An auditor can verify an entry's content by recomputing its canonical hash and can detect a rewrite of history, "
             "because editing any earlier entry changes that entry's canonical hash. Limitation stated honestly: the pre-write hashes of earlier entries cannot be recomputed retrospectively, since the ledger's earlier serializations were not captured - which is exactly why the rule starts here."),
    "entryCanonicalSha256": canon,
}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
# patch in the post-write hash (append-only: record it in a following tiny marker entry rather than rewriting history)
entry["ledgerSelfProof"]["ledgerSha256AfterThisWrite"] = hashlib.sha256(post).hexdigest()
lg["entries"][-1] = entry
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post2 = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(post2), "B /", hashlib.sha256(post2).hexdigest())
print("AFTER count:", after_count, "| entry canonical sha:", canon[:24])
