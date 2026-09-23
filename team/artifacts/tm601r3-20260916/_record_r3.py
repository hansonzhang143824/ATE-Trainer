# -*- coding: utf-8 -*-
"""Append the round-3 gate finding to the run ledger, refresh pins, run verify.

Run:  python .\_record_r3.py
"""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


NOTE = os.path.join(RUN, "inputs", "gate-invocation-notes-addendum-2.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")

entry = """

## 2026-09-16 23:2x +0800 自我更正 #2 + 门禁实跑判据（含假绿陷阱）

- 新增 `inputs/gate-invocation-notes-addendum-2.md` = __NOTE_SIZE__ B / `__NOTE_SHA__`。**撤回补遗 1 的 I-1**（「TM600/TM601 不在 bst-sw 门作用域」）——被实跑推翻。
- **实际机制**：`verify_bst_sw_sequence.py:259` `DEFAULT_TM_SCOPE=["TM600_HS_RDSON","TM601_LS_RDSON"]`；`check_contract_closures()` L429-L467 对 scope 内每个函数做「契约期望集 − payload SetOn 集」的闭集断言（**致命通道**），判据 = `aliasResolution[*].resolution.closedRelayNumbers`（L261-L263）；契约路径 `--contract`(L277-L284)；读不到契约 = 红(L505-L507)。该断言在 `targets` 之外独立执行。
- **实跑（只读；命令与逐字输出见补遗 2 §3）**：部署态 `15c7d2b8…` + 冻结契约 rev36 ⇒ `TM600_HS_RDSON` 期望 `[48,60,61,76,83]` 缺失 `[48,76]`；`TM601_LS_RDSON` 期望 `[60,61,154,155]` 缺失 `[]`；`targets=4 FAIL=2`；exit=1。附带确立：**部署态 TM600 的实际闭合集连 K109/K110 都没有**（仅漏腿，与 t48 记载一致）。
- **新事实（对 t6 重要）**：冻结契约下 **TM601 的期望集只有 `[60,61,154,155]`，无任何 BST 要求** ⇒ 门禁层面「TM601 BST=5 V」当前**无约束**；不经 `t6` 登记就永远不会被检查。
- **新陷阱（实测）**：拿**只含增量的候选 payload 文件**当 `--src` ⇒ `targets=[]` ⇒ 在契约闭集断言**之前** `return 0` ⇒ **假绿**（命令 B 输出「空 PASS」，exit=0）。⇒ `t9/t11` 硬要求：`--src` 必须是**等价全量源文件**，且必须同时在场 `[scan] targets=N (N>0)` 与两行 `[t30]`；**空 PASS 记为「未执行」，不得记为通过**。
- 独立复核子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5` 仍在跑（`review/independent-review-pmid-ruling.md` 尚未出现）⇒ 裁 A1 继续标 **provisional**。
- **另一 run 的活跃写入再次实测**：`acceptance-20260916-dali10/setup-contract.json` 由 377,128 B 变 377,276 B（本会话第三次观测到旧目录漂移）⇒ 冻结副本（376,308 B / `d9ecffb0…`）是本 run 唯一输入，继续有效。
- 边界：未改任何脚本；**未运行完整 `run_gates.ps1`**（只跑本门脚本的只读断言）；未写目标树/devel；**非电性结论**。
"""

size, sha = sig(NOTE)
with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + entry.replace("__NOTE_SIZE__", str(size)).replace("__NOTE_SHA__", sha).encode("utf-8"))

man = json.load(open(PIN, encoding="utf-8"))
man["gateInvocationNotesAddendum2"] = {"path": NOTE, "size": size, "sha256": sha}
lsize, lsha = sig(LEDGER)
man["files"]["run_ledger"] = {"path": LEDGER, "size": lsize, "sha256": lsha}
for key in ("old_team_json", "setup_contract_old"):
    p = man["files"][key]["path"]
    if os.path.exists(p):
        sz, h = sig(p)
        if h != man["files"][key]["sha256"]:
            man["files"][key].update({"size": sz, "sha256": h,
                                      "note": "live artifact of the OTHER run; refreshed after observed drift"})
            print("refreshed", key, sz, h[:12])
json.dump(man, open(PIN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
psize, psha = sig(PIN)
print("gate-addendum-2:", size, sha)
print("ledger:", lsize, lsha)
print("pin:", psize, psha)
