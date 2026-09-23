# t28 独立复核意见（input-sync RS-1..RS-4 + 探测式回退证明 + manifest 重放登记）

- 复核人：rule-reviewer（独立于作者 compile-diagnostician）· 日期：2026-09-16
- **只读声明**：未修改任何被审文件。取证：python 明文 / grep 工具；哈希 python-plaintext 现算。
- **结论：六项复核要点全部 ACCEPT —— 无 blocker、无越界；另附 3 条非阻塞建议。**

## 0. 哈希复核

| 对象 | 申报 | 我现算 | 判定 |
|---|---|---|---|
| `scripts/check_input_sync.py`（改后） | 17,455 B / `e804c459…d784d1` | 17,455 B / `e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1` | ✅ 一致 |
| `…pret28` 备份 | 8,727 B / `d8722d91…` | 同 | ✅ |
| `implementation-manifest.json`（改后） | 36,733 B / `53ae63ab…` | **39,167 B / `216a2e376322d5f315e11524308d5a15cf4d02a5f16f881a3a2a5727ddc601d9`** | ⚠️ **不一致（第三次漂移）** |
| `…pret28` 备份 | 33,773 B / `7c67aa74…` | 同 | ✅ |
| `gate_baseline.json` | 28 B / `021015da…` | 28 B / `021015da84e6fd4c54a595796e1bad73e18c57db94f856871d5667044302cb1d` | ✅ **未改** |
| `project/DALI/meta/dali_tm_meta.json` | `50efba4e…` | 同 | ✅ 未写 |
| 目标树 `test.cpp` | `15c7d2b8…` | 同 | ✅ 未写 |
| `devel` 两文件 | `5c9cb3f9…` / `ba8ab3de…` | 同 | ✅ 未写 |

> **manifest 连续三次漂移**：33,773 → 36,733（申报）→ **39,167（我实测）**。**不影响功能判定**（其 `generationReplayRequirement` 内容在现盘完整存在），但**任何引用都须现算**。

---

## 1. ✅ 规格实现忠实（RS-1..RS-4 逐条对照）

规格来源 = `meta-excitation-override.json:recommendedGateAssertions`；实现位于 `check_input_sync.py:241-330`（`check_meta_override_rs`）。

| 断言 | 规格要求 | 实现实测（`L…`） | 判定 |
|---|---|---|---|
| **RS-1** | TM601 `powered_pins` 不含 `VBUS` | `L265-270`：`'MATCH' if 'VBUS' not in pp else RS_STATUS` | ✅ 忠实 |
| **RS-2** | TM600 `mi_pins` ∋ `SW`；TM601 ∋ `{PMID_SW, SW}` | `L274-285`：`miss = sorted(want - mi)`，任一缺失即 `RS_STATUS` | ✅ 忠实 |
| **RS-3** | vset == 冻结 ATE（TM600 `4.2/15/5/5`、TM601 `4.2/9/5`）且不含 `vbus` | `L235-238` 常量表；`L303-304` 单独检 `vbus`；`L305-311` 比对**轨道集合**（报"多余/缺失"）；`L313-315` 比对**数值** | ✅ 忠实 |
| **RS-4** | yaml `_sync.metaSha256` == `sha256(meta)` | `L322-328`：`_cmp(y_meta_sha, meta_sha)` | ✅ 忠实 |

### "RS-3 轨道集合 + 数值双重比较"是否越界 —— **判定：属收紧，非越界** ✅
规格原文要求 vset **等于**冻结 ATE 且**不含 `vbus`**。**"相等"在集合语义上本就意味着"多一条轨道即不符"**；实现把"多余/缺失"显式列进 detail，属于**把规格的完整含义显式化**，并未引入规格之外的新阈值或新判据。**更没有放宽任何既有判据**（见 §4）。⇒ **我接受其"收紧"自述**，且认为它正是规格所要求的行为。

## 2. ✅ RS-FAIL 必计入 NEW-RED（我独立验证该链，无豁免）

**独立运行**（非复用其脚本）：`python scripts/check_input_sync.py` → **exit 0**，4 条 RS 项均 `[OK]`。
**链核验**：
- `L344 bad = [i for i in items if i['status'] != 'MATCH']` —— **唯一**的"良性"判定；`L345 in_sync = not bad`；`L349`（json 模式）与 `L400`（文本模式）**均 `return 1`** ⇒ 非零。
- **穷举检查"是否有既有判据豁免 RS-FAIL"**：`status' == 'MATCH'` = **0 处**、`in ('DRIFT'` = **0 处**、`exempt` = **0 处**、`ignore` = **0 处**；`!= 'MATCH'` 仅 **1 处**（即 `L344`）。⇒ **RS-FAIL 没有任何豁免路径** ✅
- **未新增独立 exit 路径**这一做法**正确**：复用 `bad` 使 RS-FAIL 与既有 DRIFT/MISSING **同权**，从而自动落入 `run_gates.ps1:139/:181` 的 `NEW-RED ⇒ exit 1` 分类器。**我不要求新增独立路径**（那反而会有"绕开分类器"的风险）。
- **附带**：`MISSING`（meta 缺失/无法解析、TM601 条目缺失）同样落到 `bad` ⇒ **fail-closed**，不会静默通过 ✅

## 3. ✅ 回退可检出证明 —— **我独立重放，BEFORE/AFTER 均复现**

**我亲自运行** `gate-logs-t28/t28_red_proof.py`（未复用其结论），结果：
```text
BEFORE_fix  exit=0  verdict=IN SYNC   (script=check_input_sync.py.pret28)
AFTER_fix   exit=1  verdict=OUT OF SYNC
   [RS-FAIL] RS-1 VBUS 移除 / RS-2 mi_pins 修正 / RS-3 ATE 激励对齐
   *** NEW-RED: meta 的 run 作用域修正已被抹除 (3 项) ***
RED-PROOF PASSED = True
```
⇒ **"修复前检不出、修复后可检出"这一验收唯一要点成立** ✅

**(a) harness 是否真的只读现盘 meta、未写 `project/DALI/meta`？—— 我**前后哈希实测**，确认为只读** ✅
| 监测对象 | 运行前 | 运行后 | 判定 |
|---|---|---|---|
| `project/DALI/meta/dali_tm_meta.json` | `50efba4e…` | `50efba4e…` | **未变** |
| `project/DALI/meta/test_conditions.yaml` | `c919b11d…` | `c919b11d…` | **未变** |
| `project_config.json`（live） | `3c2c29ce…` | `3c2c29ce…` | **未变** |
| `scripts/gate_baseline.json` | `021015da…` | `021015da…` | **未变** |
其写入目标**仅**为自身目录 `gate-logs-t28/`（`redproof-test_conditions.regen.yaml`、`redproof-config.probe-meta.json`、两个 `.log`、`t28-red-proof.json`）。

**(b) 为何忠实模拟下 RS-4 仍 MATCH？—— 其解释正确，且**不是**回避** ✅
harness 刻意把副本 yaml 的 `_sync.metaSha256` **与探针 meta 同拍刷新**（`L42-63` 明确构造），这正是 `gen_test_conditions.py` 的真实行为 ⇒ **RS-4 看到的是"戳与当前 meta 一致"，理应 MATCH**。
⇒ 结论：**RS-4 天生看不见语义回退**（因为戳随生成刷新），**RS-1..RS-3 才是检测器** —— 这与我在 `review/gate-capability-boundaries.md` B-3 的判定一致，也与 `recommendedGateAssertions` 里 RS-4 被标注"**单独不足**"一致。**harness 没有回避，而是忠实复现了缺陷的形状。**

## 4. ✅ 未改基线、未放宽既有判据

- `gate_baseline.json` = **28 B / `021015da…`** ⇒ **未改** ✅
- **函数级比对**（我按 `def` 切块哈希）：`_cmp`/`_read_json`/`_read_yaml_sync`/`_sha`/`check_dft_group` **全部 identical**；`_caps_upper`/`_num`/`_read_json_rb`/`_vset_map`/`check_meta_override_rs` 为**新增**。
- `check_sch_group` 被我的粗测标为 CHANGED，**逐一 diff 后确认：其函数体一字未改，差异仅为紧随其后的新增注释块**（我的切块把相邻注释并入该函数所致）。⇒ **既有 6 条判定（DFT 组①②③ / SCH 组③a/b/c）逻辑与阈值未动** ✅
- 整文件 diff：**新增 172 行、删除仅 2 行**，且这 2 行是"必须改"的整合点（`items = check_dft_group + check_sch_group` 改为追加 RS 组；`mark` 字典增加 `RS_STATUS` 显示名）。**无既有判据被删改** ✅

## 5. ✅ manifest 的 `generationReplayRequirement` 登记充分

现盘实测该顶层键存在（`top-level keys = 30`），含：`statement`（**MANDATORY**：任何重生成后必须重放 + 复跑 input-sync）、`why`（**引用实测证据**：探针 `1c849664…` 逐字节等于覆盖前 meta，并列出被抹除的三项修正）、`replayOrder`（4 步，含"重放 run 作用域覆盖"与"以 RS-1..RS-4 验收"）、`detector`（RS-FAIL ⇒ NEW-RED ⇒ exit 1）。
⇒ **足以满足"生成后必须重放"的可追溯要求**：它同时给出**强制语句、实测依据、可执行顺序、自动检测器**四要素。**与 manifest 既有内容无冲突**（纯新增顶层键，`schema` 我另行未复跑，但作者报 PASS，我采信为 author-reported）。

## 6. 两条自报限制的裁定

### R1（`run_gates.ps1` 汇总层不再打印 `RS-FAIL` 字样）—— **接受（low），根因已定位；并经作者独立复现后**更正我方一处过度概括****
**根因**：`run_gates.ps1:119` 为 `$errLines = @($out | Where-Object { "$_" -match '^\s*[-*]\s+\S' } | Select-Object -First 6)` —— 只抓"**单**连字符或 **单**星号 + 空白 + 非空白"开头的行。

> **⚠️ 我方更正（2026-09-16，据 compile-diagnostician 独立复现 + 我本人复核）**
> 我原写"根因信号行 `*** NEW-RED: …` 不匹配该正则 ⇒ 被过滤"——**此点正确**；但我据此暗示"**看不到是 RS 触发的**"，**该推断过度**。
> **实测 `gate-logs-t28/redproof-after-fix.log`（47 行）**：匹配该正则的行**恰好 6 条，其中前 3 条就是 `- [RS-FAIL] …`**（后 3 条为 `- [RS-1/2/3 …]`）⇒ **`RS-FAIL` 明细会被汇总层捕获、未被挤出**；`*** NEW-RED: …` 一行**确不匹配**，但**文件内存在**。
> ⇒ **真实形态**：**根因标题行不显示，但 `- [RS-FAIL]` 明细会显示**；**真正的挤占风险是 `-First 6`**（`MISSING` 项很多时才可能挤出 RS-FAIL）。
> **⇒ 我撤回"看不到是 RS 触发"的措辞**；该更正**降低**本项严重度判断（仍为 low）。感谢作者以实测更正。

**影响面（我判定）**：**不阻断** —— ① 汇总层仍打印 `[input-sync] exit=1`，`NEW-RED` 分类与 `exit 1` 传播不受影响；② 若单独跑 `check_input_sync.py`，**stdout 明确打印 `*** NEW-RED` 与 `[RS-FAIL]`**（我实测）；③ 根因固定写在 `gate-logs-*/input-sync.log`。
**建议（非阻塞，**不要求**本任务改）**：`run_gates.ps1` 属 out of scope，**同意不在 t28 内改**；两条候选：**(i)** 给信号行加 `- ` 前缀；**(ii)** 把正则放宽为 `^\s*[-*]{1,3}\s+\S`。**作者与我认为 (ii) 更省事且不改信号行样式。** **记为 low 待办**。
**⚠️ 范围归属（作者实测补充）**：`run_gates.ps1` **不在 `t33` 的 inScope 内**（t33 仅列 `build-report.json` 与 `gate-logs-t33`）⇒ 若要做，须**由 Captain 另开一条小任务**或在并入 t33 时**显式扩范围**。**我不要求现在做。**

### R2（遗留未使用的 `import re`）—— **接受，明确不要求现在清理**
我实测：`'import re' present: True | 're.' usages: 0` ⇒ **确为死导入**。
**但我不要求现在改**，理由是本 run 已反复出现"**一改哈希、先前 verdict 即失效**"：为一个无功能影响的死导入再动一次、并使 t28 的复核锚点失效与 `gate_baseline` 无谓漂移，**代价大于收益**。**建议与其它实质修订合并**（如 R1 若将来落地）时一并清理。**我把它登记为 low 待办，不构成 needs_revision。**

## 7. 回归证据（我独立复现的部分）

- `python scripts/check_input_sync.py` → **exit 0 / IN SYNC**，RS 组 4 条 `[OK]` ✅（我亲自跑）
- `gate_baseline.json` 未改 ✅；`meta`（`50efba4e…`）/ 目标树（`15c7d2b8…`）/ `devel`（`5c9cb3f9…`、`ba8ab3de…`）**均未写** ✅
- **未独立复现**（采信为 author-reported）：`run_gates.ps1` 的 `FULL_EXIT = 0`、12 门 = 11 GREEN + `cbit` KNOWN-RED、`validate_team_artifact.py` 的 schema PASS、以及"未编译"。

## 8. 结论与建议

| 复核要点 | 判定 |
|---|---|
| 1 规格实现忠实（含 RS-3 收紧） | ✅ ACCEPT（收紧合理，非越界） |
| 2 RS-FAIL 计入 NEW-RED、无豁免 | ✅ ACCEPT（我穷举验证无豁免路径） |
| 3 回退可检出证明 | ✅ ACCEPT（**我独立重放**；harness 只读性由前后哈希证实） |
| 4 未改基线 / 未放宽既有判据 | ✅ ACCEPT（函数级 + diff 级双重核验） |
| 5 manifest 重放登记 | ✅ ACCEPT（四要素齐备） |
| 6 R1 / R2 | ✅ 两条**均接受**（R1 根因已定位，R2 不值得单独再改） |

**非阻塞待办（3 条）**：① R1 的汇总层 `RS-FAIL` 显示（改 `run_gates.ps1:119` 正则或信号行前缀）；② R2 死导入清理；③ **manifest 哈希连续漂移**（33,773→36,733→39,167 B）—— 请**冻结并在引用时现算**。

**总评：t28 的改动可以签收**；取证与证明链条（规格→实现→红态证明→只读性）完整且可复现。
