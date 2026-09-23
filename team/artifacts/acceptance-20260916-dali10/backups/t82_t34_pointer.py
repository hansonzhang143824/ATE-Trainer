# -*- coding: utf-8 -*-
"""Create the t34 carrier pointer file (so a filename-based scan can find it), and append the namespace-count 'before' measurement to my snapshot log."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"

def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

carrier = os.path.join(A, "acceptance-report.json")
ptr = {
    "purpose": ("POINTER FILE, not a duplicate. The task known as 't34' has NO artifact file of its own; its carrier is the path below. This file exists so that a filename-based search for '*t34*' can locate the mapping. "
                "Do not treat this file as the report; review the carrier."),
    "task": "t34",
    "carrier": rec(carrier),
    "carrierBasename": "acceptance-report.json",
    "why": "'t34' is a task label; the run's naming convention puts the artifact under its content name (acceptance-report.json), and the only other '*t34*' hit in the tree is a script (backups/superseded-scratch/t60_apply_captain_t34_t35_t41.py).",
    "whereItsEntriesLive": "acceptance-report.json -> limitations[] (the t34 entries are L1..L42, including the T32-F1 live-hazard rewrite, the two-object comparison, and the settled-wording entry)",
    "writtenBy": "setup-architect",
    "writtenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
out = os.path.join(A, "t34-carrier-pointer.json")
json.dump(ptr, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(out, "rb").read()
print("pointer:", out)
print("  ", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(out).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
print("  carrier:", ptr["carrier"]["sizeBytes"], "B /", ptr["carrier"]["sha256"], "@", ptr["carrier"]["measuredAt"])

# namespace-count 'before' measurement
sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
s = json.load(open(sh, encoding="utf-8"))
blk = ((s.get("preservedPeerNamespaces") or {}).get("setupArchitectFreezeAnchors") or {})
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "reason": "reviewer's demand for an empirical before/after count on the shared anchors file; this is the BEFORE measurement (to be paired with an AFTER taken after the next regeneration by its owner)",
    "sharedAnchorsFile": rec(sh),
    "preservedNamespaceEntries_before": len(blk.get("anchors") or {}),
    "peerNamespaceKeys": list((s.get("preservedPeerNamespaces") or {}).keys()),
    "ownerAdmissionOnRecord": "compile-diagnostician stated in writing that an early version of its generator collapsed multi-keys into one and that the 8 lost entries cannot be restored; it has since switched to union accumulation + mirroring + DO_NOT_TOUCH_PREFIXES=('setupArchitect-',)",
    "reviewerRulingAccepted": "rule-reviewer declined to use my self-maintained anchors file as its basis (independence + it also changes + the shared-file loss is unresolved); the practical rule both sides follow is: each side recomputes on citation.",
    "t34CarrierPointer": rec(out),
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
lb = open(LOG, "rb").read()
print("snapshot log:", len(lg["entries"]), "entries |", len(lb), "B /", hashlib.sha256(lb).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(LOG).st_mtime).strftime("%H:%M:%S"))
print("preserved namespace entries (BEFORE):", lg["entries"][-1]["preservedNamespaceEntries_before"])
