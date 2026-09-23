# t54 执行事实（决定性）：**未落盘 ⇒ 无法产出真正的 `bst-sw` GREEN**

- 触发：Captain 裁定"路径 1；t54 判据＝GREEN"，同时指出**目标树未落盘**（仍 `15c7d2b8…`）。
  二者**张力**：GREEN 需要"已落盘的候选 payload"，而落盘不在我的可写范围内。本文件给出**实测证据**。

## 1. 实测：`--src` 无法把门禁指向候选 payload

```
$ python scripts/verify_bst_sw_sequence.py --src team/artifacts/.../implementation-payload-TM600-TM601.cpp
[scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS
EXIT=0
$ python scripts/verify_bst_sw_sequence.py --src <同上> --tm-scope TM600_HS_RDSON,TM601_LS_RDSON
[scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS
EXIT=0
```
**根因（读源码）**：`main()` 中
```python
targets = derive_targets(iter_functions(text))
if not targets:
    print("[scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS")
    return 0                       # ← 在任何判定之前就返回
...
errors = []
# ---- t30: 契约闭合集合断言 ----  ← 只在 targets 非空时才到达
```
但**契约闭合断言本身不依赖 `targets`**（`check_contract_closures()` 自己按 `scope`/`payload` 取数）。
⇒ **"空 targets 早退"是一个真实缺口**：当源文件里没有 ZCD 家族函数时，**整段契约闭合断言被跳过**，
`--tm-scope` 也救不了（它只在到达断言后才生效）。

## 2. t54 在"未落盘"下**能**与**不能**产出什么

| 项 | 能否 | 依据 |
| --- | --- | --- |
| 目标树门禁全套（`run_gates.ps1`，我沙箱可跑） | **能** | 实测可跑；但输入是**部署态 `15c7d2b8…`** ⇒ 结果只能是该树的真实结论（`bst-sw` 红） |
| `bst-sw` 对**候选 payload** 的判定 | **不能**（用被审脚本） | ① 目标路径写死为 `cfg.derived.test_cpp`；② 即使 `--src` 也因"空 targets 早退"到不了断言 |
| 等价判定（复现断言逻辑于候选 payload） | 能（**非门禁产出**） | 我的探针：`exp=[48,60,61,76,83]` ⊆ 实际 `{13,48,57,60,61,76,83,85,126}` ⇒ `missing=[]` |

## 3. 因此 t54 的**如实**结论形态（三种，取决于落盘与否）

1. **目标树仍未落盘**（当前）：`run_gates.ps1` 如实报 `bst-sw` **NEW-RED**，但**红因是"部署态缺 `48/76`"**，
   且 `compiledRevision = 15c7d2b8…`（**不是**候选 payload）⇒ `build-report.json` 记 **blocked**，
   并**并列**候选 payload 的等价判定（§2 第 3 行）与"落盘后预期 GREEN"。
   **不得**把这一红记成回归/缺陷（契约 rev 29 下它正是"实现尚未落盘"的直接后果）。
2. **落盘后**（需 Captain 或可写会话执行）：我**重跑一次** `run_gates.ps1` ⇒ 期望 `bst-sw` **GREEN**；
   `compiledRevision` = 落盘后现算值；`build-report.json` → `pass`。
3. **落盘后仍红**：按 Captain 裁定，**只在 `t53` 未按路径 1 落地时适用** ⇒ 在报告中**并列两套期望**、
   归因记 **"契约权威值待消歧"**，**不得**记成缺陷/回归。

## 4. 顺带发现（建议登记为残余改进项）

`main()` 的"空 `targets` 早退"会让**契约闭合断言在非 ZCD 源文件上静默跳过**。
若将来希望"对任意源文件校验契约闭合"，需把该早退改为"早退仅跳过 ZCD 序列检查，**仍执行契约闭合断言**"。
**属 `scripts/` 变更 ⇒ 不在我 t54 的 inScope，需 Captain 另派任务**（且**不得**顺带改 `gate_baseline.json`）。

## 5. 边界
静态连通性/登记层面；**非电性结论**；**无机台实测**；**编译闭环 ≠ 电性签核**。
