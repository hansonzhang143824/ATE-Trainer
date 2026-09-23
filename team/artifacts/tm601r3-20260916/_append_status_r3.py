# -*- coding: utf-8 -*-
"""Append the consolidated round-2/3 corrections to team/CURRENT_STATUS.md and
refresh the affected pins. Run: python .\\_append_status_r3.py"""
import hashlib
import json
import os
import time

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


entry = """

## 2026-09-16 23:2x +0800 两处自我更正 + 门禁实跑判据（覆盖本页此前的门禁口径）

**① 撤回「bst-sw 门靠 meta `capAuthority.powered_pins` 指纹」**：那是 `scripts/verify_bst_sw_sequence.py` docstring L5-L7/L81-L85 里**已被作者于 2026-09-13 重写掉的旧实现**。实际选靶判据在 `derive_targets()` L100-L101（函数体含 `rampi_capv(`），拓扑由 `SetOn` 内 `K_FPVIH_TO_PGND`→LS / `K_FPVIH_TO_PMID`→HS 判定，判不出则 WARN 跳过（L106-L112）。

**② 撤回「TM600/TM601 不在 bst-sw 门作用域」**（我 23:0x 的推断，已被实跑推翻）：门内另有一条**独立的契约闭集通道**，且**默认作用域就写着这两个函数**——`DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]`（L259）；`check_contract_closures()` L429-L467 对 scope 内每个函数做「契约期望集 − payload `cbite.SetOn` 集」的致命断言；判据 = `aliasResolution[*].resolution.closedRelayNumbers`（L261-L263）；`pinRouteTable`/`relaySet` 仅作 locator；读不到契约 = 红（L505-L507）。

**③ 实跑判据（只读，本轮执行）**
```
python scripts\\verify_bst_sw_sequence.py --src D:\\PROJECT6-DALI\\ForCodexDebug\\source\\test.cpp \\
  --contract team\\artifacts\\tm601r3-20260916\\snapshot\\setup_contract.json
→ [t30] TM600_HS_RDSON: 期望 [48,60,61,76,83] 缺失 [48,76]
→ [t30] TM601_LS_RDSON: 期望 [60,61,154,155] 缺失 []
→ [scan] targets=4 FAIL=2 ; exit=1
```
其中 `targets=4` = `TM607_BUCK_LS_ZCD / TM608_BOOST_HS_ZCD / TM609_BOOST_HS_NEG / TM640_BOOST_HS_OCP`（**不含** TM600/TM601，因它们无 `rampi_capv`）。附带确立：**部署态 TM600 的实际闭合集里连 `K109/K110` 都没有**，只有 `{13,57,60,61,83,85,126}` ⇒ 属**仅漏腿**（与 t48 记载一致）。

**④ 新事实（对契约修订重要）**：冻结契约下 **TM601 的期望集只有 `[60,61,154,155]`，无任何 BST 要求** ⇒「TM601 BST=5 V」在门禁层面**当前无约束**，必须由新 DAG 的 `t6` 登记，否则永远不被检查。

**⑤ 新陷阱（实测，必须写进 t9/t11 口径）**：把**只含增量的候选 payload 文件**当 `--src` 会得到 `targets=[]`，脚本在契约闭集断言**之前** `return 0` 并打印「空 PASS」（**实测 exit=0**）⇒ **假绿**。硬要求：`--src` 必须指向**等价全量源文件**，且必须同时在场 `[scan] targets=N (N>0)` 与两行 `[t30]`；**空 PASS 一律记为「未执行」，不得记为通过**。

**⑥ 另一 run 的活跃写入（本会话第三次实测）**：`acceptance-20260916-dali10/setup-contract.json` 377,128 B → **377,276 B**；其 `team.json` 亦反复漂移。⇒ 新 DAG 的输入只认冻结副本（`snapshot/setup_contract.json` = 376,308 B / `d9ecffb0…`）。

**⑦ 未做**：未运行完整 `run_gates.ps1`（无已落盘新树，产物会与最终树不对应）；未改任何门禁脚本；未落盘任何 payload；`devel` 零写入。裁 A1（TM600 PMID=5 V）因独立复核未回收，仍标 **provisional**。
"""

before = sig(STATUS)
with open(STATUS, "rb") as f:
    old = f.read()
with open(STATUS, "wb") as f:
    f.write(old + entry.encode("utf-8"))
after = sig(STATUS)

man = json.load(open(PIN, encoding="utf-8"))
man["files"]["current_status"] = {"path": STATUS, "size": after[0], "sha256": after[1],
                                 "note": "refreshed after this session's own appends"}
# refresh any other drifted live entries
for key in ("old_team_json", "setup_contract_old", "execution_plan", "team_json_new"):
    rec = man["files"].get(key)
    if not rec or not rec.get("path"):
        continue
    p = rec["path"]
    if os.path.exists(p):
        sz, h = sig(p)
        if h != rec["sha256"]:
            rec.update({"size": sz, "sha256": h, "note": "refreshed after observed drift"})
            print("refreshed", key, sz, h[:12])
json.dump(man, open(PIN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("CURRENT_STATUS.md:", before[0], "->", after[0], after[1])
print("pin:", sig(PIN))
