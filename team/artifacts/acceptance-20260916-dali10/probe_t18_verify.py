# probe_t18_verify.py — 核验 t18 撤回是否完整（四项激励原文 + 冲突登记 + 两侧 locator）
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
c = json.loads(open(D + "setup-contract.json", encoding="utf-8").read())
s = json.dumps(c, ensure_ascii=False)

print("revision:", c.get("revision"))
print("\n--- 四项：激励字段现状 ---")
for tm in ("TM102", "TM103", "TM108", "TM109"):
    d = (c.get("tmDeltas") or {}).get(tm) or {}
    st = d.get("stimuli")
    print("  %-6s keys=%s" % (tm, [k for k in d.keys() if "timul" in k or "ate" in k.lower()]))
    if isinstance(st, list) and st:
        print("         stimuli[0] = %s" % str(st[0])[:200])
    sr = d.get("simulationDomainReference")
    if sr:
        print("         simRef     = %s" % json.dumps(sr, ensure_ascii=False)[:150])

print("\n--- 冲突登记搜寻（关键词）---")
for kw in ("4.2", "4.0", "3.0", "DFT.csv", "OVERVIEW Code1", "see conflicts",
           "BD08", "BD-08", "superseded by the user", "not averaged", "retract"):
    print("  %-28s hits=%d" % (kw, s.count(kw)))

print("\n--- conflicts[] 中与四项相关的条目 ---")
for i, cf in enumerate(c.get("conflicts") or []):
    blob = json.dumps(cf, ensure_ascii=False)
    if any(t in blob for t in ("TM102", "TM103", "TM108", "TM109")):
        print("  [%d] %s" % (i, blob[:400]))
