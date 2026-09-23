# t26 · `t26-correction-5` 最终复核结论（ACCEPT）

- 复核人：rule-reviewer（独立于修改者 setup-architect）· 日期：2026-09-16
- **被审对象（现盘）**：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **21,773 B / python-plaintext sha256 `38880b78f896f4d9c786d23c2cc96e477d96472ef6d6aa741a9e81d1990e705c`（`t26-correction-5`，mtime 19:05:54）** —— 与申报**逐位一致** ✅
- 只读：未修改任何被审文件；`meta`（`50efba4e…`）与 `yaml`（`c919b11d…`）**均未再改**（现算比对 `match=True`）✅

## 结论：**三项检查全部 PASS ⇒ ACCEPT**

| 检查 | 结果 |
|---|---|
| (i) K57 段是否满足 T26-F1 | ✅ PASS |
| (ii) R-3 / R-4 是否落实 | ✅ PASS（并新增 RS-1..RS-4 断言规格，规格本身正确可用） |
| (iii) 是否仍有"把 K57 当纯工程建议/可移除"的残留 | ✅ PASS（残留扫描命中 2 行，**全部无害**） |

---

## 1. ✅ (i) K57 段（现盘行号，逐项落位）

| 字段 | 行 | 内容/判定 |
|---|---|---|
| `verdict` | **L217** | PER-FUNCTION：TM600 **MUST KEEP**（规则层+工程层）/ TM601 规则层豁免可零电容；净指令"change nothing" ✅ |
| `ruleLayer.TM600` | **L219** | *"REQUIRED - … powered rail token is **BST_SW**, and the exemption set (mi_pins) contains only **SW**, so `fam_intersect({'SW'},'BST_SW')` is **empty**; deleting K57 would raise a new FR-001 warning."* ✅ |
| `ruleLayer.TM601` | **L220** | *"NOT REQUIRED - … its `mi_pins` (PMID_SW, SW) meet the **SW_BST** alias, so the exemption fires."* ✅ |
| `engineeringLayer` | **L222-226** | `statement`/`why`（DFT.csv L92 / OVERVIEW L984，引 t22 裁定）/`exemptionCaveat`（*"Gate silence is not evidence that a cap is unnecessary"*）✅ |
| `withdrawals` | **L227-230** | 两版错误结论逐条留痕（含"corrected here after rule-reviewer's token-level analysis, **which I re-derived independently**"）✅ |
| `ledgerRequirement` | **L231** | *"**TM600 required (rule + engineering), TM601 exempted at the rule layer but retained**"* ⇒ **我指出的"台账会顺传播错记"风险已消除** ✅ |
| `k57TokenAnalysis.whyItMatters` / `maskingEffect` | 另段 | 两别名在 `cap_defs` 中为 **SEPARATE entries, each evaluated independently**（同通道 57、同物理继电器）⇒ **豁免按令牌生效、不按继电器** ✅ |

**我的独立复核**：从 `scripts/verify_relay_trace.py` **原样抽取 `fam_intersect`** 执行（非自写）：`({'SW'},'BST_SW')=[]`、`({'SW'},'SW_BST')={'SW'}`、`({'PMID_SW','SW'},'SW_BST')={'SW'}` —— 与其表**逐格吻合**；旁证 `({'SW1','SW1_BST1','SW2_BST2'},'SW')=[]` 亦成立。**T26-F1 CLOSED**，t22 / t24 / t26 结论与理由现已统一。

## 2. ✅ (ii) R-3 / R-4 与 RS 断言规格

- `regenerationBehaviour.reapplyAfterRegeneration = true` ✅（登记"任一次生成器重跑会静默抹除三项修正"）
- `inputSyncDetectability` ✅（诚实说明现存 input-sync **检测不到**该抹除）
- `minimalEndpointNote` ✅（K126 冗余，low，非阻塞）
- **`recommendedGateAssertions`（L343-368）新增 RS-1..RS-4** —— 我核对**规格本身正确可用**：
  - **RS-1** `TM601 powered_pins ∌ VBUS` ✅ 正确（对应 t22-A2 的根因）
  - **RS-2** `TM600 mi_pins ∋ SW` 且 `TM601 mi_pins ∋ {PMID_SW, SW}` ✅ 正确（保住豁免前提）
  - **RS-3** 两函数 `hardwareInit` vset == 冻结 ATE（4.2/15/5/5 与 4.2/9/5）且无 vbus ✅ 正确
  - **RS-4** yaml `_sync.metaSha256 == sha256(meta)` ✅ 正确，且**明确标注"单独不足"**（因戳随生成刷新）—— 这一自我限定**准确**
  - 并注明落地位置 `scripts/check_input_sync.py`、**属 t26 out of scope、需 Captain 派任务** ✅ 分权处置正确
- **未落地项（不属本产物缺陷）**：RS-1..RS-4 的**实现**与生成器侧落改仍待 Captain 派任务；本产物只提供规格，处理得当。

## 3. ✅ (iii) 残留扫描（现盘）

凡含 `remove|must not|should not|not be closed|advisory|optional` 且同行的 K57 语句，命中 **2 行**，**均无害**：
- **L228** = `withdrawals` **撤回记录**（标 "for BOTH functions - WRONG for TM600, **withdrawn**"）
- **L275** = 描述**重生成会把红带回来**（*"the two reds it **removed** … **would come back**"*，风险警示）

⇒ **不存在**把 TM600 的 K57 当"纯工程建议/可移除"的**现行**表述；`verdict`（L217）已是"MUST KEEP + change nothing"，`maskingEffect` 更明确"删除 TM600 的 K57 会 un-mask 并**新增**告警"。**(iii) PASS。**

---

## 4. ⚠️ 必须更正的事实性错误：`reviewLagNote`（L370-376）对我方复核轮次的记载

产物写道：
> `round1`: reviewed **t26-correction-1** …｜`round2`: reviewed **t26-correction-1 again** (t26-independent-review-2.md) ｜`round3`: reviewed **t26-correction-2**

**这与磁盘事实不符**。我方意见文件的实际 mtime 与被审版本对应关系如下（可复核）：

| 我方文件 | mtime | 实际被审版本 |
|---|---|---|
| `review/t26-independent-review.md` | **18:57:27** | `correction-1`（11,511 B / `238b2b6c…`） |
| `review/t26-independent-review-2.md` | **18:59:45** | **`correction-2`（14,246 B / `b3dd2095…`）** ← 非 correction-1 |
| `review/t26-independent-review-3.md` | **19:01:14** | `correction-2` 复评（F1 重申 + F2 新增） |
| `review/t26-independent-review-4.md` | **19:03:03** | **`correction-3`（17,081 B / `d4519422…`）→ 已 ACCEPT** |
| `review/t26-correction-3-confirmation.md` | **19:04:28** | `correction-3` 逐项确认（三项 PASS） |

⇒ **round2 打的是 `correction-2` 而非"correction-1 again"**；且 **`correction-3` 已获 ACCEPT**（`-4` 与 confirmation 两份文件）。我**从未在 `correction-3`/`correction-5` 上提出 F1**。
**影响**：该记载会把"我方复核滞后"和"重复提同一 finding"写进台账，进而**低估已完成的复核覆盖**并误导后续轮次。**请更正 `reviewLagNote`**（或直接以本文件 §4 表格替换其 `round1..round3` 字段）；`L246` 的 `review must use revision t26-correction-4` 亦与现盘（`correction-5`）不一致，请一并更新为现盘哈希。

---

## 5. 最终交付

- **t26 的 meta/model 覆盖：ACCEPT（签收）** —— 无新增 finding。`t26-correction-5`（`38880b78…`）三项检查全过。
- **待 Captain 派活（不阻塞本产物签收）**：① 实现 RS-1..RS-4（`scripts/check_input_sync.py`，out of t26 scope）；② 生成器侧落改（可选）。二者合起来才能消除"重生成静默抹除"风险。
- **仍在树上的唯一未决风险**：重生成会逐字节还原改动前 meta（探针 `1c849664…`，146,180 B），而 `input-sync` 仍报 `IN SYNC` ⇒ **门禁全绿也检不出**。建议 t9 在验收证据中把本次 meta 修正标注为处在该风险下并写明缓解。
- **门禁现盘**：日志 19:02:00–19:02:04（晚于 payload 写入 18:53:33）；`relay-trace` = **`RELAY TRACE PASSED`**、仅 TM643 两条 WARN；其余 10 门 PASSED ⇒ **11 GREEN + `cbit` KNOWN-RED**。
- **t24 payload 结论不变**：**TM601 可零电容；TM600 必须保留 `K57_CAP_BST_SW`**（规则层 + 工程层）。
