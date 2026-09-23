# -*- coding: utf-8 -*-
"""Discipline-3 in practice: take a timestamped BYTE COPY of my own (and key peer) artifacts so a later auditor can verify the bytes of this round, not just the hashes. Then log it."""
import json, hashlib, os, shutil, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
dest = os.path.join(A, "backups", "setuparch-%s" % stamp)
os.makedirs(dest, exist_ok=True)

SRC = {
    "acceptance-report.json": os.path.join(A, "acceptance-report.json"),
    "setupArchitect-anchors.json": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"),
    "setupArchitect-freeze-snapshots.json": os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json"),
    "t34-carrier-pointer.json": os.path.join(A, "t34-carrier-pointer.json"),
    "t34-CARRIER-PATH.md": os.path.join(A, "t34-CARRIER-PATH.md"),
    "PATH-MAP.md": os.path.join(A, "PATH-MAP.md"),
    "setup-contract.json": os.path.join(A, "setup-contract.json"),
    "implementation-input-pin.json": os.path.join(A, "implementation-input-pin.json"),
    "t35-contract-reconciliation.md": os.path.join(A, "t35-contract-reconciliation.md"),
    "t41-tm601-bst-path-determination.md": os.path.join(A, "t41-tm601-bst-path-determination.md"),
    "implementation-payload-TM600-TM601.cpp": os.path.join(A, "implementation-payload-TM600-TM601.cpp"),
    "test-plan.json": os.path.join(A, "test-plan.json"),
    "build-report.json": os.path.join(A, "build-report.json"),
    "t28-anchors.json": os.path.join(A, "gate-logs-t28", "t28-anchors.json"),
}

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

manifest = {"copiedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "purpose": ("Byte copies of this round's artifacts. Rationale: 'hash pins but does not preserve' - a hash cannot be re-verified once the file is rewritten, and size is not a proxy (this run produced 3,579 B three times with three different hashes). "
                        "A copy makes the round independently checkable; the copies are READ-ONLY evidence and must never be edited."),
            "owner": "setup-architect", "files": {}}
for name, src in SRC.items():
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(dest, name))
        manifest["files"][name] = {"from": src.replace("\\", "/"), "copy": os.path.join(dest, name).replace("\\", "/"),
                                   "sizeBytes": os.path.getsize(src), "sha256": sha(src),
                                   "sourceMtime": datetime.datetime.fromtimestamp(os.stat(src).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
mpath = os.path.join(dest, "MANIFEST.json")
json.dump(manifest, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("byte-copy dir:", dest.replace("\\", "/"))
print("copied:", len(manifest["files"]), "files | manifest:", os.path.getsize(mpath), "B /", sha(mpath))

# log it (append-only)
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "discipline 3 in practice: took a timestamped BYTE COPY of this round's artifacts (a hash pins but does not preserve; size is not a proxy - 3,579 B appeared three times with three different hashes)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "byteCopySnapshot": {"dir": dest.replace("\\", "/"), "manifest": mpath.replace("\\", "/"), "manifestSha256": sha(mpath), "fileCount": len(manifest["files"]),
                         "note": "read-only evidence; never edit the copies"},
    "artifacts": {k: {"path": v["from"], "sizeBytes": v["sizeBytes"], "sha256": v["sha256"], "measuredAt": v["sourceMtime"]} for k, v in manifest["files"].items()},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(post), "B /", hashlib.sha256(post).hexdigest())
