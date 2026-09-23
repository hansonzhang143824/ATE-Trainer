# -*- coding: utf-8 -*-
"""Append the 2026-09-16 TM601-DFT-change rulings to the three long-lived
tracking files, and freeze the tm601r3-20260916 run inputs.

Reads/writes with python byte mode (plaintext). Never touches
D:/PROJECT6-DALI/devel or the target VS tree.
"""
import hashlib
import json
import os
import shutil
import time

WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
RUN = os.path.join(WS, "team", "artifacts", "tm601r3-20260916")
STAMP = "2026-09-16 22:0x +0800"


def sha(p):
    b = open(p, "rb").read()
    return len(b), hashlib.sha256(b).hexdigest()


def append(path, text):
    with open(path, "rb") as f:
        old = f.read()
    new = old + text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(new)
    return len(old), len(new), hashlib.sha256(new).hexdigest()


SECTION = """

## {stamp} TM601 DFT 修改后的裁定与新 DAG（Captain，最新单一恢复入口）

**用户裁定（本次权威输入）**：用户已修改 `project/DALI/Dali_testmode.xlsx`，**修改后的 TM601 DFT 为唯一权威**；先前 TM601 DFT 有错误，忽略其引起的所有 TM601 报错，不作为阻断、修复或验收失败依据。旧 DFT 派生的 TM601 推断、计划、payload、审查**仅保留审计用途**。

**现盘事实（python read_bytes 现算）**
- 新版 DFT：`project/DALI/Dali_testmode.xlsx` = 12,210,680 B / SHA-256 `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` @ 2026-09-16 21:46:39（旧版 pin 为 `d9d721a3…`，已失效）。
- TM601（OVERVIEW row 133）：`vset[vbat,3.5,100e-6,0]` / `vset[vdrv,5,100e-6,0]` / `vset[vbus,5,100e-6,0]` / **`vset[bst,5,100e-6,0]`（BST=5 V，旧版没有）**；`field[WAKE_UP,1]` + `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]`；`delay[5e-3]` / **`iset[pmid_sw,1,1e-3,0]`** / `delay[2e-3]`；Power=VBAT,SW；`I(PMID_SW)`；SW-PGND；ExpectValue=7.5 mΩ。
- TM600（OVERVIEW row 132）未变：`vset[pmid,5,100e-6,0]`（**PMID=5 V**）、`vset[bst_sw,5,1e-3,0]`（**BST−SW=5 V**）、`iset[sw,1,1e-3,0]`、ExpectValue=11 mΩ、Special=`Y / 2 FLOAT`。
- 目标树 `ForCodexDebug/source/test.cpp` = 469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`（未落盘）；`devel/source/test.cpp` = 434629 B / `5c9cb3f9…`（只读）。
- 旧 run 现盘：`setup-contract.json` 376308 B / `d9ecffb0…`（rev 36）、`test-plan.json` 185689 B / `707ce845…`（v25）、旧候选 payload 43806 B / `66abc088…`；`t55_replace.py` 5573 B / `cc8711f9…`（**未执行**）。
- 旧 run `team.json` phase=`running`：t43/t52 pending、t54 failed；`schematic-expert`/`setup-architect`/`test-strategy-architect`/`rule-reviewer`/`compile-diagnostician` 仍为 working，可能继续改写**旧目录**产物。

**裁定**
1. **停止旧 `t55` REPLACE**：未经新策略与独立审查，**不得落盘任何旧候选 payload**。旧 `66abc088…` 与旧 `2d0984d9…` 一律视为 audit-only。
2. **忽略旧 DFT 引起的 TM601 报错**：旧 `bst-sw`/`relay-trace` 针对 TM601 的红灯、旧 `[110,61]`/`[48,60,61,76]` 之争、t38/t39/t40/t41/t42/t43/t44~t48/t52 的 TM601 结论**均不作为本轮阻断、修复或验收失败依据**（保留审计）。
3. **新职责链**：`dft-expert` 重提取新 DFT → `schematic`/`Setup` 核实物理通路/通道/共享与互斥 → `test-strategy-architect` 制定逐 TM 资源、阶段、寄存器、测量、下电、日志 → `rule-reviewer` 独立审查 → **之后** `ate-implementer` 才映射 API。**Captain 只协调依赖，不落盘、不裁定电气意图**。
4. **TM600 单独复审**（不予豁免）：ACM200 channel 5 → BST 的 `K48/K76`、BST-SW 闭集、多源互斥、以及 **PMID=5 V 与新证据对照旧黄金/`voltage-inference.md` 的 15 V**（并列登记，待裁定，不得静默采用）。
5. **输入冻结**：新 DAG 全部走 `team/artifacts/tm601r3-20260916/snapshot/` 冻结副本 + `pin/snapshot-manifest.json`，以免旧 run 的活跃写入污染新输入 pin。

**新 DAG（staged，等待用户 Approve & Run）**：团队 `ate-dali-tm601r3` / profile `ate-delivery` / 7 成员 / 12 任务 / 依赖 13。
```text
t1  requirements  dft-expert             重提取新 DFT（唯一权威）
 ├─ t2  verification  schematic-expert   JM601 SW—PGND + BST=5 V 可实施性；TM600 ch5→BST/K48/K76/多源互斥
 ├─ t6  implementation setup-architect   契约合并修订（ch5 分组 + 三目的地互斥 + TM601 BST 登记 + 旧条目 superseded）[deps t1,t2]
 │   └─ t7  requirements  test-strategy-architect  逐 TM 资源/阶段/寄存器/测量/下电/日志
 │        └─ t8  review  rule-reviewer   独立审查（verdict=pass 才放行）[deps t2,t6,t7]
 │             ├─ t9  implementation ate-implementer  payload 映射（不落盘）[dep t8]
 │             │   └─ t10 verification rule-reviewer  落盘前检查点 GO/NOGO [deps t8,t9]
 │             │        └─ t11 verification compile-diagnostician 门禁 + Release 编译 [dep t10]
 │             └─ t12 integration setup-architect 十项终稿与残余项 [deps t8,t9,t10,t11]
```

**阻断项（须用户裁定或前置条件满足才能继续）**
- **B1 t55 REPLACE 已停**：执行条件 = t8 `verdict=pass` + t10 检查点 GO + 用户对目标树写入的一次性授权。
- **B2 DFT 现盘已变**：旧 dft-ir 的 `d9d721a3…` pin 失效，21:46 后任何依赖旧读数的结论均须重算（新 DAG 已含此项）。
- **B3 待裁定（不阻断提取，但阻断任何依赖该值的实现）**：新 DFT `vset[pmid,5,…]` 与历史黄金/`knowledge/hardware/voltage-inference.md` 的 PMID=15 V 的差异（TM600）；需用户或授权 owner 给出作用域与重开条件。
- **B4 待核实**：TM601 `vset[bst,5,…]` 的物理含义（BST 单端轨相对 GND，还是 BST−SW 差分=5 V；新 DFT 未给 `bst_sw` 行）——由 schematic/Setup 给事实、strategy 给操作点，不得由实现者猜。
- **B5 旧 run 仍在跑**：旧团队可能继续改写旧目录产物；新 DAG 已用冻结副本隔离，但**旧 run 的 pending/failed 不会自动闭合**，需在终稿或用户裁定中正式登记。
- **B6 边界**：`devel` 零写入；**未做任何机台/电性验证**；**编译闭环 ≠ 电性签核**。
"""

RUNLEDGER = SECTION.format(stamp="2026-09-16 22:0x +0800（RUN-LEDGER 条目）")
STATUS = SECTION.format(stamp="2026-09-16 22:0x +0800（CURRENT_STATUS 条目）")
PLAN = SECTION.format(stamp="2026-09-16 22:0x +0800（EXECUTION_PLAN 条目）")

targets = [
    (os.path.join(RUN, "RUN-LEDGER.md"), RUNLEDGER),
    (os.path.join(WS, "team", "CURRENT_STATUS.md"), STATUS),
    (os.path.join(WS, "team", "EXECUTION_PLAN.md"), PLAN),
]

report = {}
for path, text in targets:
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(text.encode("utf-8"))
        report[os.path.basename(path)] = {"created": True, "size": os.path.getsize(path)}
        continue
    before = sha(path)
    old_len, new_len, new_sha = append(path, text)
    report[os.path.basename(path)] = {
        "before_size": before[0], "before_sha256": before[1],
        "after_size": new_len, "after_sha256": new_sha,
    }

# refresh the frozen snapshot of the run inputs
os.makedirs(os.path.join(RUN, "snapshot"), exist_ok=True)
os.makedirs(os.path.join(RUN, "pin"), exist_ok=True)
pin_path = os.path.join(RUN, "pin", "snapshot-manifest.json")
man = json.load(open(pin_path, encoding="utf-8"))
watch = {
    "dft_xlsx": r"D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\Dali_testmode.xlsx",
    "dft_csv": r"D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\input\DFT.csv",
    "dft_restored_csv": r"D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\input\DFT_restored.csv",
    "setup_contract_old": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\setup-contract.json",
    "test_plan_old": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json",
    "dft_ir_old": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\dft-ir.json",
    "schematic_ir": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\schematic-ir.json",
    "target_test_cpp": r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp",
    "devel_test_cpp": r"D:\PROJECT6-DALI\devel\source\test.cpp",
    "old_payload": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp",
    "t55_replace_script": r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\t55_replace.py",
    "old_team_json": r"D:\Newtest\DSH\ATE-Coding-Plat\.agent-teams\ate-dali-acceptance\team.json",
    "current_status": os.path.join(WS, "team", "CURRENT_STATUS.md"),
    "execution_plan": os.path.join(WS, "team", "EXECUTION_PLAN.md"),
}
man["capturedAt"] = time.strftime("%Y-%m-%d %H:%M:%S +0800")
man["files"] = {}
for k, p in watch.items():
    if os.path.exists(p):
        size, h = sha(p)
        man["files"][k] = {
            "path": p, "size": size, "sha256": h,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
        }
    else:
        man["files"][k] = {"path": p, "missing": True}

for key in ("setup_contract_old", "test_plan_old", "dft_ir_old", "schematic_ir", "old_payload"):
    src = man["files"][key]["path"]
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(RUN, "snapshot", key + os.path.splitext(src)[1]))

with open(pin_path, "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=2)

report["pin/snapshot-manifest.json"] = {
    "size": os.path.getsize(pin_path),
    "sha256": sha(pin_path)[1],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
