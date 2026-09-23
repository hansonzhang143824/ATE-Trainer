# t26 · 现盘（`t26-correction-3`）复核确认书（含版本时序澄清）

- 复核人：rule-reviewer · 日期：2026-09-16
- 对象：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **17,081 B / python-plaintext sha256 `d45194221c47545e4305cad78c7f0f283db8011e3d92ad59cb11dca5f01735b7`（`t26-correction-3`，mtime 19:02:21）** ✅
- 只读：本复核未修改任何被审文件。

## 0. 先把时序说清（并未出现"复核旧版"）

我方意见文件的**实际落盘顺序**（磁盘 mtime 实测）：

| 我方文件 | mtime | 对应被审版本 |
|---|---|---|
| `review/t26-independent-review.md` | 18:57:27 | `correction-1`（11,511 B） |
| `review/t26-independent-review-2.md` | 18:59:45 | `correction-2`（14,246 B）—— **其中 T26-F1 为对该版所提** |
| `review/t26-independent-review-3.md` | 19:01:14 | `correction-2` 复评（再次提出 F1 + 新增 F2） |
| **`review/t26-independent-review-4.md`** | **19:03:03** | **`correction-3`（17,081 B）—— 已 ACCEPT** |

⇒ **`t26-correction-3` 我已复核并 PASS**，文件为 `t26-independent-review-4.md`（落盘于你发出本轮请求之后约 40 秒，双方消息交叠）。**并非复核了旧版**；我从未在 `correction-3` 上提出 F1。你本轮的三项检查我已重跑确认，结论一致，见下。

## 1. ✅ (i) K57 段满足 T26-F1（现盘行号锚点）

| 字段 | 现盘行 | 判定 |
|---|---|---|
| `k57Conclusion.verdict` | **L198** | ✅ *"PER-FUNCTION: TM600_HS_RDSON **MUST KEEP** `K57_CAP_BST_SW` closed (both the rule layer and the engineering layer require it). TM601_LS_RDSON **is exempted** at the rule layer and may run zero-Cap-closure… **Net instruction to the payload: change nothing**…"* |
| `ruleLayer.TM600` | **L199+** | ✅ *"**REQUIRED** – its powered rail token is `BST_SW`, and the exemption set (`mi_pins`) contains only `SW`, so `fam_intersect({'SW'},'BST_SW')` is empty; deleting K57 would raise a new FR-001 warning."* |
| `ruleLayer.TM601` | **L199+** | ✅ *"**NOT REQUIRED** – both its powered rail token (`SW`) and its `mi_pins` (`PMID_SW, SW`) meet the `SW_BST` alias…"* |
| `withdrawals` | **L208** | ✅ 两版错误结论逐条留痕（"for BOTH functions - WRONG for TM600" / "no longer requires K57 for TM600 as well - also WRONG"） |
| `ledgerRequirement` | **L212** | ✅ "TM600 required (rule + engineering), TM601 exempted at the rule layer but retained" —— **我指出的台账错记风险已消除** |
| `k57TokenAnalysis` | **L267** | ✅ 含 `whyItMatters`（**L268**：两别名在 `cap_defs` 中是 **SEPARATE entries**、**each evaluated independently**、同通道 57 同物理继电器 ⇒ **豁免按 token 生效、不按继电器**） |
| `maskingEffect` | **L313** | ✅ "…`L354` is evaluated **BEFORE** the exemption, so TM600's requirement is silently satisfied today. **Removing K57 from TM600 would un-mask it and add a NEW warning**." |

**我的独立复核（用门禁自己的函数）**：从 `scripts/verify_relay_trace.py` **原样抽取 `fam_intersect`** 执行，与 `k57TokenAnalysis` 逐格表**逐格吻合**：
```
fam_intersect(['SW'],'BST_SW')             = []        ✅
fam_intersect(['SW'],'SW_BST')             = ['SW']    ✅
fam_intersect(['PMID_SW','SW'],'SW_BST')   = ['SW']    ✅
（旁证）fam_intersect(['SW1','SW1_BST1','SW2_BST2'],'SW') = []   ✅ t25 分节点成立
```
⇒ **T26-F1 CLOSED**，且与 t22 / t24 的理由现已统一。

## 2. ✅ (ii) R-3 / R-4 已落实（现盘行号锚点）

| 项 | 现盘行 | 判定 |
|---|---|---|
| `regenerationBehaviour` | **L247** | ✅ 登记重生成行为 |
| `reapplyAfterRegeneration` | **L261** | ✅ `= true`（要求生成后重放） |
| `inputSyncDetectability` | **L262** | ✅ 诚实写明"现存 input-sync **检测不到** run 级覆盖被抹掉"，并给 token/locator 断言建议、注明门禁脚本改动属 out of scope 已上交 Captain |
| `minimalEndpointNote` | **L315** | ✅ `K126_V1P5_CAP`（令牌 `V1P5`）不在两函数 `powered_pins` 中 ⇒ 闭合属冗余（不报错），建议实现者按最小端点复核；locator `test.cpp` L9081/L9255 |
| `gates.evidenceTiming` | **L191** | ✅ 标注早前 18:53:16 日志已被取代 |
| `rootCause` | **L240** | ✅ VBUS 精确 token、非 `BUSH0_AMUX`（与我 t22/t25 实测一致） |

**门禁现盘（19:02:00–19:02:04，晚于 payload 写入 18:53:33）**：`RELAY TRACE PASSED`、仅 TM643 两条 WARN、FR-001 反向 2 处；其余 10 门 PASSED ⇒ **11 GREEN + `cbit` KNOWN-RED**；`TM600/TM601: 虚构继电器名` = 0 ✅

## 3. ✅ (iii) 无"把 K57 当纯工程建议/可移除"的残留表述

我对现盘做了**残留扫描**（凡含 `remove|must not|should not|zero-Cap|not be closed|advisory|optional|drop` 且同行的 K57 语句全部列出）。命中仅 **3 行**，**全部为无害**：

| 行 | 内容 | 为何无害 |
|---|---|---|
| **L198** | *"…TM600 **MUST KEEP**…；TM601 … may run zero-Cap-closure… **Net instruction to the payload: change nothing**…"* | 这是**更正后的正确指令本身**（明确要求删除 TM601 的 `zero-Cap` 措辞仅适用于 TM601，且净指令是"什么都不改"）；含 `zero-Cap` 字样属**描述 TM601**，非建议移除 TM600 |
| **L209** | *"an earlier revision said 'K57 must NOT be closed / zero-Cap-closure item' for BOTH functions - **WRONG for TM600, withdrawn**;"* | **撤回记录**（`withdrawals`），标明历史错误，非现行指令 |
| **L256** | *"the two reds it **removed** (TM601 SW->K57… and TM601 VBUS->K5…) **would come back**;"* | 描述**重生成会把红带回来**（风险警示），与"能否移除 K57"无关 |

⇒ **不存在**任何现行表述把 TM600 的 K57 当作"纯工程建议/可移除"；相反，L198 明确"change nothing"、L313 明确"删除 TM600 的 K57 会 un-mask 并新增告警"。**(iii) PASS。**

## 4. 结论

三项检查 **全部 PASS** ⇒ **ACCEPT**（与 `t26-independent-review-4.md` 一致，无新增 finding，无新 line 号需求）。

**唯一仍在树上的未决风险**（不属产物缺陷）：重生成会逐字节抹掉本次三项修正，而 `input-sync` 仍报 `IN SYNC`（戳随生成刷新）⇒ 门禁全绿也检不出；处置权在 Captain（生成器落改 / 加 run 级断言 / 明确接受）。

**t24 payload 结论不变**：**TM601 可零电容；TM600 必须保留 `K57_CAP_BST_SW`**（规则层 + 工程层）。
