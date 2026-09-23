# probe_meta_naming.py — Captain 只读探针：推导 meta 注册表的函数命名规则
# 用途：回答 t5 升级的问题 A（TM600/TM601 的精确 symbol 名从哪来）
# 运行：python team/artifacts/acceptance-20260916-dali10/probe_meta_naming.py
# 说明：TSZ/DLP 透明加密文件必须用 python 读取，PowerShell/grep 只得密文。
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = "D:/Newtest/DSH/ATE-Coding-Plat"

# 1) meta 注册表的 key 形态
meta = json.loads(open(f"{ROOT}/project/DALI/meta/dali_tm_meta.json", encoding="utf-8").read())
fns = meta.get("functions", [])
print("meta functions: type=%s len=%s" % (type(fns).__name__, len(fns)))
if isinstance(fns, list) and fns:
    print("first entry keys:", list(fns[0].keys()))
    print("first entry:", json.dumps(fns[0], ensure_ascii=False)[:300])
# 找出承载函数名的字段
namefield = None
if isinstance(fns, list) and fns:
    for cand in ("name", "func", "function", "symbol", "item", "Item"):
        if cand in fns[0]:
            namefield = cand
            break
print("name field guess:", namefield)
keys = [str(e.get(namefield)) for e in fns] if namefield else []
print("sample keys:", keys[:6])
print("keys starting TM103/TM108/TM607/TM608:",
      [k for k in keys if k.startswith(("TM103", "TM108", "TM607", "TM608"))][:10])
print("do keys equal test.cpp symbols? (spot check)")
src = open("D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp", encoding="utf-8-sig", errors="replace").read()
syms = set(re.findall(r"\b(TM\d{3,4}_[A-Za-z0-9_]+)\s*\(", src))
print("  meta keys that are also test.cpp symbols:", len([k for k in keys if k in syms]), "/", len(keys))
print("  meta keys NOT found in test.cpp:", [k for k in keys if k not in syms][:8])

# 2) 生成器如何构造函数名 / 如何与 test.cpp 对齐
lines = open(f"{ROOT}/scripts/gen_testitems_meta.py", encoding="utf-8", errors="replace").read().splitlines()
needles = ["f\"TM", "'TM'", '"TM"', "re.compile", "def ", "fname", "func_name", "match(", "name =", "Item", "Level"]
print("\n--- gen_testitems_meta.py name-derivation lines ---")
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith("#") or not s:
        continue
    if any(n in l for n in needles):
        print("%4d: %s" % (i, l[:160]))
