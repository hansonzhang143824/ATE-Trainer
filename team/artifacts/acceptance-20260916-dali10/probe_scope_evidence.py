# probe_scope_evidence.py — 摆出"四项激励值"两侧证据（DFT.csv 行 vs IR/OVERVIEW）
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
W = "D:/Newtest/DSH/ATE-Coding-Plat/"
D = W + "team/artifacts/acceptance-20260916-dali10/"

print("=== A 侧：DFT.csv 行（ATE 权威，用户 BD-08 判据）===")
for i, line in enumerate(open(W + "project/DALI/input/DFT.csv", encoding="utf-8", errors="replace").read().splitlines(), 1):
    if any(t in line for t in ("TM102", "TM103", "TM108", "TM109")):
        print("  L%-4d %s" % (i, line[:170]))

print("\n=== B 侧：dft-ir.json 中各该 TM 的激励/IR 值 ===")
ir = json.load(open(D + "dft-ir.json", encoding="utf-8"))
raw_items = ir.get("items") or []
if isinstance(raw_items, dict):
    items = raw_items
else:
    items = {}
    for it in raw_items:
        if isinstance(it, dict):
            key = it.get("tm") or it.get("TM") or it.get("id")
            if key:
                items[key] = it
for tm in ("TM102", "TM103", "TM108", "TM109"):
    it = items.get(tm) or {}
    frags = []
    for key in ("stimulus", "stimuli", "supply", "vbat", "powerSequence", "conditions", "limits"):
        v = it.get(key)
        if v:
            frags.append("%s=%s" % (key, json.dumps(v, ensure_ascii=False)[:240]))
    print("  %-6s %s" % (tm, " | ".join(frags) if frags else "(no stimulus/supply key)"))
    if not frags:
        print("         top-level keys:", list(it.keys())[:14])

print("\n=== 现盘哈希 ===")
import hashlib
for f in ("setup-contract.json", "test-plan.json"):
    b = open(D + f, "rb").read()
    print("  %-22s %8d B  %s" % (f, len(b), hashlib.sha256(b).hexdigest()))
