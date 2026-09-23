# -*- coding: utf-8 -*-
"""Test t4's proposed tightening: is artifactsAbsent present exactly on tick entries and absent on full ones?"""
import json, os, hashlib, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
p = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(p, encoding="utf-8"))
rows = []
for e in lg["entries"]:
    if not isinstance(e, dict):
        rows.append((None, None, None))
        continue
    rows.append((e.get("snapshotIndex"), e.get("kind"), "artifactsAbsent" in e))

tick = [r for r in rows if r[1] == "tick"]
full = [r for r in rows if r[1] == "full"]
none = [r for r in rows if r[1] is None]
print("entries:", len(lg["entries"]))
print("tick entries:", [(r[0], r[2]) for r in tick])
print("tick WITH artifactsAbsent:", sum(1 for r in tick if r[2]), "/", len(tick))
print("full WITH artifactsAbsent:", sum(1 for r in full if r[2]), "/", len(full))
print("missing-kind WITH artifactsAbsent:", sum(1 for r in none if r[2]), "/", len(none))
print("kind values other than full/tick/None:", sorted({r[1] for r in rows if r[1] not in ("full", "tick", None)}))
# cross-tab
tab = {}
for sn, k, aa in rows:
    tab.setdefault((k, aa), 0)
    tab[(k, aa)] += 1
print("cross-tab (kind, artifactsAbsent) -> count:", tab)
print("@", datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
