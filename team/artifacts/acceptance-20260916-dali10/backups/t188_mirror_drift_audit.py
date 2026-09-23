# -*- coding: utf-8 -*-
"""Verify the mirrorSize drift and audit my own artifacts: every record of ANOTHER party's file size must carry a timestamp."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
MINE = {"team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-freeze-snapshots.json",
        "team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-anchors.json",
        "team/artifacts/acceptance-20260916-dali10/acceptance-report.json"}

# 1) verify the drift
sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
s = json.load(open(sh, encoding="utf-8"))
blk = (s.get("preservedPeerNamespaces") or {}).get("setupArchitectFreezeAnchors") or {}
mirror_size = blk.get("mirrorSize")
mirror_of = blk.get("mirrorOf")
led = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
led_now = os.path.getsize(led)
print("owner's mirrorSize field :", mirror_size)
print("its mirrorOf target      :", mirror_of)
print("my ledger now            :", led_now, "B  => gap:", (led_now - mirror_size) if isinstance(mirror_size, int) else "n/a")
print("owner shared file        :", os.path.getsize(sh), "B /", hashlib.sha256(open(sh, "rb").read()).hexdigest()[:24])

# 2) audit: records of OTHER parties' files inside my artifacts, and whether each carries a timestamp
def has_time(d):
    return any(k for k in d if re.search(r"(at|At)$", str(k)) or "time" in str(k).lower())

print("\n--- audit of peer-file records in MY artifacts ---")
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
gaps = []
def walk(node, path):
    if isinstance(node, dict):
        p = node.get("path")
        if isinstance(p, str) and node.get("sizeBytes") is not None:
            peer = p.replace("\\", "/") not in MINE and not p.replace("\\", "/").endswith(("acceptance-report.json", "setupArchitect-anchors.json", "setupArchitect-freeze-snapshots.json"))
            if peer and not (node.get("measuredAt") or node.get("sourceMtime") or node.get("at")):
                gaps.append((".".join(path), p))
        for k, v in node.items():
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
walk(doc, [])
print("anchors: peer-file records lacking a timestamp:", len(gaps))
for g in gaps[:10]:
    print("   ", g)

# ledger entries carry takenAt at entry level; verify that pattern holds for peer artifacts
lg = json.load(open(led, encoding="utf-8"))
missing_entry_time = [e.get("snapshotIndex") for e in lg["entries"] if not e.get("takenAt")]
print("ledger entries: total =", len(lg["entries"]), "| lacking entry-level takenAt =", missing_entry_time or "none")
peer_in_ledger = 0
for e in lg["entries"]:
    for k, v in (e.get("artifacts") or {}).items():
        if isinstance(v, dict) and v.get("sizeBytes") is not None and "peer" not in str(k) and k not in ("acceptance-report.json", "gate-logs-t28/setupArchitect-anchors.json", "gate-logs-t28/setupArchitect-freeze-snapshots.json", "scripts/gate_baseline.json"):
            peer_in_ledger += 1
print("ledger artifacts referencing other parties' files:", peer_in_ledger, "(each inherits the entry's takenAt)")
