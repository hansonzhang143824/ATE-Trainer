# 门禁调用方式核实 · 补遗 2（更正补遗 1 的 I-1：实测推翻「不在作用域」的推断）

> 时间：2026-09-16 23:2x +0800。本文件**更正** `gate-invocation-notes-addendum-1.md` 的 **I-1 推断**。层级：本文件 > 补遗 1 > 原始 `gate-invocation-notes.md`。
> 核实方式：**只读**源码 + **实跑**只读断言；未修改任何脚本、未运行完整 `run_gates.ps1`、未写目标树。

## 1. 撤回（RETRACTED）

| 我在补遗 1 里写的 | 状态 | 实测更正 |
| --- | --- | --- |
| **I-1**：「TM600/TM601 无 `rampi_capv(` ⇒ **不在 `bst-sw` 门的 targets 内** ⇒ 该门对它们既不报红也不构成通过证据」 | **撤回（被实跑推翻）** | 该门**另有独立的契约闭集通道**，且**默认作用域就写着这两个函数名**（见 §2）。实跑证明它对 TM600/TM601 **确实执行**并给出逐项 missing（§3） |
| 「t54 报 TM600 缺 `[48,76]` ⇒ NEW-RED 需要另行解释」 | 已解释 | 就是这条通道产生的，与 targets 无关；无需另找机制 |

**部分保留（仍是事实）**：`derive_targets()` 确实只选 `rampi_capv(` 函数（L100-L101），实测部署态 targets = `TM607_BUCK_LS_ZCD(LS)` / `TM608_BOOST_HS_ZCD(HS)` / `TM609_BOOST_HS_NEG(HS)` / `TM640_BOOST_HS_OCP(HS)`，**不含 TM600/TM601**；且 `if not targets: 空 PASS; return 0`（L497-L499）确实发生在契约闭集断言（L503）**之前** ⇒ 「targets 为空会让契约闭集断言被跳过」这一点仍成立（下文 §4 有实例）。

## 2. 实际机制（FACT，源码 + 实跑双证）

- `DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]`（`verify_bst_sw_sequence.py:259`），可由 `--tm-scope` 覆盖；`resolve_scope()` L402-L413。
- `check_contract_closures(..., scope)` L429-L467：`for tm in scope:` → 取该函数在 payload 里的 `cbite.SetOn` 数值集（`_numbers_from_payload` L296），与 `expected_for_tm()`（L380-L399）算出的 **契约期望集** 求差 → 缺失即 `errors.append(...)`（**致命通道**，与既有 FAIL 同一出口）。
- 期望集判据：`CONTRACT_RULE_NOTE`（L261-L263）= `aliasResolution[*].resolution.closedRelayNumbers`（按 `usedByTm` / `tmDeltas.<TM>.aliasesUsed` 索引）；`pinRouteTable` 与 `relaySet` **只作 locator**，不参与判定。
- 契约来源：`--contract` > `proj_config` 覆盖段 > `<workspace>/team/artifacts/<run>/setup-contract.json`（L277-L284）；读不到契约 ⇒ **追加 error（红）而不是静默跳过**（L505-L507）。
- 主流程顺序（L490-L523）：`targets` 计算 → `--list` 分支 → **`if not targets: 空 PASS return 0`** → 契约闭集断言 → 逐目标 HS/LS 序列检查。

## 3. 实跑判据（本轮只读执行，可复现）

命令 A（部署态树 + 冻结契约）：
```
python scripts\verify_bst_sw_sequence.py --src D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp \
  --contract D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm601r3-20260916\snapshot\setup_contract.json
```
输出（逐字）：
```
[t30] TM600_HS_RDSON: 契约声明必需 [48, 60, 61, 76, 83] vs payload SetOn 比对完成, 缺失=[48, 76] (缺失数 2)
[t30] TM601_LS_RDSON: 契约声明必需 [60, 61, 154, 155] vs payload SetOn 比对完成, 缺失=[] (缺失数 0)
[t30] 契约来源: setup_contract.json rev=36 | 判据: aliasResolution[*].resolution.closedRelayNumbers ...
[scan] targets=4 FAIL=2
*** FAIL (BST-SW GOLDEN SEQUENCE) ***
  - TM600_HS_RDSON: 契约声明必需的继电器 K48 未出现在 cbite.SetOn 中 (… payload locator: test.cpp:9081; 该函数实际闭合=['K126_V1P5_CAP','K13_VBAT_Cap','K57_CAP_BST_SW','K60_BUSL0_VCP','K61_ACM8_SW','K83_BUSH0_PMID','K85_CAP_PMID'])
  - TM600_HS_RDSON: 契约声明必需的继电器 K76 未出现在 cbite.SetOn 中 (同上)
exit=1
```
**由此确立的事实**：
1. 该门对 **TM600_HS_RDSON / TM601_LS_RDSON 都执行**契约闭集断言（无需任何 `--tm-*` 参数）。
2. 部署态（`15c7d2b8…`，未落盘）**TM600 缺 `[48,76]`，且实际闭合集里连 `K109/K110` 都没有**（=仅漏腿，与 t48 的记载一致）。
3. **TM601 在冻结契约下的期望集只有 `[60,61,154,155]`（PGND/SW 那条），missing=[] ⇒ 绿**。这从门禁侧独立印证：**冻结契约里 TM601 没有任何 BST 要求**；新 DFT 的 `vset[bst,5,…]` 与它不冲突但也未被覆盖 ⇒ 必须由 `t6` 补登记，否则「TM601 的 BST=5 V」在门禁层面永远无约束。

## 4. 新发现的可执行陷阱（FACT + 警告）

命令 B（冻结候选 payload 文件 + 冻结契约）：
```
python scripts\verify_bst_sw_sequence.py --src team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp --contract <同上>
→ [scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS     exit=0
```
- 原因：该 payload 文件**只含 TM600/TM601 增量**，不含 `rampi_capv` 家族函数 ⇒ `targets=[]` ⇒ **在契约闭集断言之前就 `return 0`** ⇒ **假绿**。
- **⇒ 对 `t9/t11` 的硬要求（新增）**：禁止把「候选 payload 文件」直接当 `--src` 运行本门并据此判定；`--src` 必须指向**等价全量源文件**（payload 映射进目标树后的完整 `test.cpp`），并且必须核对 `[scan] targets=N`（N>0）与 `[t30]` 两行都在场；任何「空 PASS」一律视为**未执行**而非通过。
- 同时印证 t54 已登记的缺口：`main()` 的早退使契约断言可被静默跳过（本处为 `targets` 为空这一具体触发条件，已实测复现）。

## 5. 边界

未修改 `scripts/verify_bst_sw_sequence.py`（24,964 B / `17092fea…1d54c78`）与 `scripts/run_gates.ps1`（9,763 B / `dd2a4337…ab310b9`）；**未运行完整 `run_gates.ps1`**（因其会写日志目录并可能触发编译，且当前无已落盘新树 —— 只跑了本门脚本的只读断言）；**未写目标树、未写 devel**；本轮结论为门禁/登记层面，**非电性结论、无机台验证**。
