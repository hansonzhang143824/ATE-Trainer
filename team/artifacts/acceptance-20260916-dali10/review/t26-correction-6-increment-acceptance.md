# t26 · `t26-correction-6` 增量确认（ACCEPT 覆盖该增量）

- 复核人：rule-reviewer · 日期：2026-09-16
- 对象：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **24,424 B / python-plaintext sha256 `1af63a29f1e45cb38535d4ecf558d3364f8994c931cc4739e9c0c2ecbee2ccb0`（`t26-correction-6`，mtime 19:06:48）** —— 与申报**逐位一致** ✅
- 只读：未修改任何被审文件。契约 rev24 `fd00a508…`、meta `50efba4e…`、yaml `c919b11d…` 均与我上轮快照一致（未再改）。

## 结论：**我上轮的 ACCEPT 覆盖 `correction-6` 的增量** ✅（7 项已 ACCEPT 的实质字符串逐字仍在）

---

## 1. 已 ACCEPT 的内容未被改动（逐字复核）

我用**解析后的 JSON 值**（非原始行，避免转义干扰）核对上轮 ACCEPT 的 7 处实质字符串：

| 字段 | 现盘值 | 判定 |
|---|---|---|
| `verdict` | *"PER-FUNCTION: TM600_HS_RDSON **MUST KEEP** `K57_CAP_BST_SW` closed (both the rule layer and the engineering layer require it). TM601_LS_RDSON **is exempted** at the rule layer and may run zero-Cap-closure… **Net instruction to the payload: change nothing**…"* | ✅ 逐字一致 |
| `ruleLayer.TM600` | *"**REQUIRED** - … token is `BST_SW`, and the exemption set (mi_pins) contains only `SW`, so `fam_intersect({'SW'},'BST_SW')` is **empty**; deleting K57 would raise a new FR-001 warning."* | ✅ |
| `ruleLayer.TM601` | *"**NOT REQUIRED** - … `mi_pins` (PMID_SW, SW) meet the `SW_BST` alias, so the exemption fires."* | ✅ |
| `engineeringLayer.exemptionCaveat` | *"Gate silence is not evidence that a cap is unnecessary."* | ✅ |
| `withdrawals` | 两条撤回记录逐字在位 | ✅ |
| `ledgerRequirement` | *"TM600 required (rule + engineering), TM601 exempted at the rule layer but retained."* | ✅ |
| `k57TokenAnalysis.whyItMatters` | *"…cap_defs keeps them as **SEPARATE** entries, each evaluated for exemption independently…"* | ✅ |
| `k57TokenAnalysis.maskingEffect` | *"…Removing K57 from TM600 would un-mask it and add a **NEW** warning **- the opposite of what an earlier revision of this artifact predicted**."* | ✅ 含原句，并**追加**一句自我更正说明（属增强，非改判） |

> 说明：我首轮脚本的"CHANGED"判定是**我方的检查假阳性**（原句在 JSON 中带 `\` 转义，而我的子串比对用的是未转义文本）。改用解析值复核后确认**一致**。特此记录，避免误读为产物被动过。

## 2. 增量两块的措辞（我逐条核实）

**(a) `inputSyncGreenWhileUndetectable`（L379-384）—— ACCEPT**
- `logLine` 引用的**日志原文我已独立核对**：`gate-logs-t26/input-sync.log` 末行确为 `INPUT SYNC: **IN SYNC** …`（该日志 mtime **19:02:02**，即最近一次门禁运行）✅
- 其含义表述**准确**：门禁此刻全绿，但"修正被抹掉"**仍不可检出**（重跑生成器时 yaml 戳会同拍刷新 ⇒ input-sync 仍报 IN SYNC，而三项修正按探针被逐字节还原）✅
- `status`（"risk located, not yet mitigated; mitigation is a gate-script change outside t26 scope → captain's disposition"）与 `mitigationSpecReady: RS-1..RS-4` ✅ **分权与定位都正确**。

**(b) `reviewRound4`（L386-399）—— ACCEPT**
- `artifactUnderReview` = **`t26-correction-3`（17,081 B / `d4519422…`）**、`verdict` = ACCEPT、`reviewArtifact` = `review/t26-independent-review-4.md` —— **与我方记录逐项吻合** ✅
- `reviewerCorroboration` 记录"rule-reviewer 从 `verify_relay_trace.py` 原样抽取 `fam_intersect` 并独立运行" —— **属实** ✅
- `confirmedByReviewer` 五项与 `remainingRisk` / `payloadConclusionUnchanged`（TM601 可零电容；TM600 必须保留）—— 与我的结论一致 ✅

## 3. ⚠️ 唯一仍需更正：`reviewLagNote`（L370-376）事实错误**未修**（我第二次提出）

现盘该块仍写：
- `round2`: *"reviewed **t26-correction-1 again** (t26-independent-review-2.md) → T26-F1 (= R-1, same finding)"*
- `round1`: *"reviewed t26-correction-1 (9937 B / 16614e98...)"* ← 其中 size 亦与 `correction-1` 不符（`correction-1` 为 **11,511 B / `238b2b6c…`**；9,937 B / `16614e98…` 是**更早的非 correction 版**）
- `current`: *"t26-correction-5 (this revision)"* ← 现盘已是 `correction-6`

**磁盘 mtime 实测（权威）**：

| 我方文件 | mtime | 实际被审版本 |
|---|---|---|
| `t26-independent-review.md` | 18:57:27 | `correction-1`（11,511 B / `238b2b6c…`） |
| `t26-independent-review-2.md` | **18:59:45** | **`correction-2`（14,246 B / `b3dd2095…`）** ← 非 correction-1 |
| `t26-independent-review-3.md` | 19:01:14 | `correction-2` 复评（F1 重申 + F2 新增） |
| `t26-independent-review-4.md` | 19:03:03 | `correction-3` → **ACCEPT** |
| `t26-correction-3-confirmation.md` | 19:04:28 | `correction-3` 逐项确认 |
| `t26-correction-5-acceptance.md` | 19:05+ | `correction-5` → **ACCEPT** |

⇒ **`correction-3` 与 `correction-5` 均已获 ACCEPT**，本轮确认覆盖 `correction-6`；我方**从未**在 `correction-3/5/6` 上提出 F1。
**这一处不影响任何技术结论**（不改变 K57 判定、门禁结论、风险定性），但会把"复核滞后 / 重复提同一 finding"写进台账并**低估已完成覆盖**。**请仅改 `reviewLagNote` 的 `round1..round3` 与 `current` 字段**（可径直采用本表），其余四块**无需再动** —— 这属于台账准确性维护，不是新一轮技术争议。

## 4. 交付

- **ACCEPT 覆盖 `correction-6` 增量**：两块新增均为**证据登记/自我更正**，无新主张，措辞与我的独立复核一致；已 ACCEPT 的 7 处实质字符串**逐字未变**。
- **待 Captain 派活（唯一未决风险，不阻塞签收）**：① 实现 RS-1..RS-4（`scripts/check_input_sync.py`，out of scope）；②（可选）生成器侧落改。二者合起来才把"重生成静默抹除"变成**可检出失败**。你在给 Captain 的定稿建议 **(a)+(c)** 我**支持**：`(a)` manifest 登记重放 + `(c)` input-sync 断言，覆盖了"记录"与"检测"两端，成本可控且可逆。
- **门禁**：日志 19:02:00–19:02:04（晚于 payload 写入 18:53:33）；`RELAY TRACE PASSED`、仅 TM643 两条 WARN；**11 GREEN + `cbit` KNOWN-RED**。
- **t24 结论不变**：**TM601 可零电容；TM600 必须保留 `K57_CAP_BST_SW`**（规则层 + 工程层）。
