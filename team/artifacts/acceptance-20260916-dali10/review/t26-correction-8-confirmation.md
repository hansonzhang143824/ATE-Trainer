# t26 · `t26-correction-8` 确认（台账更正生效；实质未变）

- 复核人：rule-reviewer · 日期：2026-09-16
- 对象（**现盘实测**）：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **26,999 B / python-plaintext sha256 `62f2da6f0996ee5afd4e828d59da5a80f7da8fe89e1302632f2e1411380ae5ec` / mtime 19:11:05 / `revision: t26-correction-8`**
- **与 setup-architect 公告不一致（须记录）**：其消息称现盘为 `t26-correction-7` = 27,517 B / `4de0ec9b0db2a1af21b834929b95aa0c2c0252fee24ab5571a4a7680e066c3de`；**实测不匹配**（当前为 26,999 B / `62f2da6f…` / revision 自称 **correction-8**）。⇒ 又一次"一版滞后"，但**结论不受影响**（本版自称仅做台账事实更正）。
- 只读：未修改任何被审产物。

## 结论：**台账更正生效且已核实 → ACCEPT（实质未变）**

---

## 1. ✅ `reviewLedger` 更正**准确** —— 我以磁盘 mtime 逐项比对，全部吻合

产物已**删除**错误的 `reviewLagNote`，改为 `reviewLedger`（含 `whyCorrected` + 逐条 `file/sizeBytes/sha256/mtime/reviewedRevision/outcome`）。**我独立比对磁盘实际 mtime**：

| 我方文件 | 磁盘实测 mtime | 产物记载 | 产物记载的 reviewedRevision | 判定 |
|---|---|---|---|---|
| `t26-independent-review.md` | 18:57:27 | 18:57:27 | `correction-1` | ✅ |
| `t26-independent-review-2.md` | 18:59:45 | 18:59:45 | **`correction-2`**（并注明"**T26-F1 raised (this is where F1 was first filed)**"） | ✅ **更正生效** |
| `t26-independent-review-3.md` | 19:01:14 | 19:01:14 | `correction-2` 复评（F1 repeated + F2 added） | ✅ |
| `t26-independent-review-4.md` | 19:03:03 | 19:03:03 | **`correction-3` → ACCEPT，F1 closed** | ✅ **漏记已补** |
| `t26-correction-3-confirmation.md` | 19:04:28 | 19:04:28 | `correction-3` 逐项确认 | ✅ |
| `t26-correction-5-acceptance.md` | 19:06:57 | 19:06:57 | `correction-5` ACCEPT | ✅ |
| `t26-correction-6-increment-acceptance.md` | 19:08:30 | 19:08:30 | `correction-6` 增量 ACCEPT | ✅ |

⇒ 我此前的两点指认（**round2 实审 `correction-2`**、**`correction-3` 已获 ACCEPT**）**均已被正确采纳**；产物并显式写明"F1 从未对 `correction-3`/`correction-5` 提出过；先前 note 错置轮次、低估已完成覆盖"。**台账缺陷 CLOSED** ✅

**⚠️ 台账现为 7 条，应再补 2 条**（我这两份文件**均晚于本版产物**，故其未记载属实、非其过错）：
- `review/t26-correction-6-increment-acceptance.md` 之后：**`review/t26-tp20-k110-finding.md`（19:13:44）** —— 含 **high** 级 finding（见 §3）
- 本文件（`t26-correction-8` 确认）落盘后亦应登记

## 2. ✅ 实质内容未变（我逐字复核已 ACCEPT 的字符串，全部在位）

`verdict`（`MUST KEEP K57_CAP_BST_SW closed`）✅｜`ruleLayer.TM600`（`fam_intersect({'SW'},'BST_SW') is empty`）✅｜`ledgerRequirement`（`TM600 required (rule + engineering)`）✅｜`RS-1`（`does NOT contain 'VBUS'`）✅｜`RS-3`（`vbat 4.2 / pmid 15 / bst_sw 5 / vdrv 5`）✅｜`maskingEffect`（`Removing K57 from TM600 would un-mask it and add a NEW warning`）✅
⇒ **K57 段 / RS 规格 / 边界② / 门禁证据一字未改**，与公告一致。

## 3. ⚠️ 唯一需更正的残留（非技术，low）+ 一件必须上桌的事（high）

**(a) `independentReview.note` 仍写 `t26-correction-7`**（`"review must use the current revision (t26-correction-7)"`），而现盘已是 **correction-8**。这与它刚刚修好的同类"版本指针陈旧"问题同源。

> **⚠️ Captain 裁定（2026-09-16，已生效）：保持不动，不要求修改该产物。** 理由：改这一行会产生新哈希，使刚锚定的 `correction-8`（`62f2da6f…`）ACCEPT 再次失效，而收益仅为指针文字。
> **据此以书面记录本项不一致，并声明权威口径**：
> - **`independentReview.note` 内的 `t26-correction-7` 是陈旧指针**；本产物**权威版本标识以 `revision` 字段为准 = `t26-correction-8`**，并以**本文件所记载的哈希**为唯一判据锚：`62f2da6f0996ee5afd4e828d59da5a80f7da8fe89e1302632f2e1411380ae5ec`。
> - **本项为 low、仅台账文字层，不影响任何技术结论**（K57 段 / RS 规格 / 边界② / 门禁证据均已逐字核验未变）。
> - 复核者在此明确：**该不一致已登记、已裁决、不再产生新版本**。
> **不阻塞签收。**

**(b) 我的 `K110` finding（high）在本产物中 0 命中**：实测产物内 `K110`=0、`[110,61]`=0、`t26-tp20-k110-finding`=0。
**说明**：该 finding 落盘于 19:13:44，**晚于**本产物 19:11:05 ⇒ 未收录**属实、非本产物之过**。但**它是当前最重的未决项**，摘要如下（详见 `review/t26-tp20-k110-finding.md`）：
- v20 `items[TM600].assumptions[0]` 与 `R-BST-SW`、以及 `setup-contract.json` rev24（`/aliasResolution[3].resolution.closedRelayNumbers[0]=110`、`bstRuling_ii`、`/tmDeltas/TM600/relaySet` 含 110、`pinRouteTable.BST CH1 Low needsClosed=[110]`）**均要求 BST−SW 闭合集合 `[110, 61]`**；
- **现盘 `test.cpp`（`15c7d2b8…`）TM600 段内 `K109`=0、`K110`=0**，只闭到 `K61_ACM8_SW` ⇒ **`[110]` 未落地**；**我 t24 判 ACCEPT 的 payload（`444810dd…` L203）同样无 `K110`**；
- `K110` 为**双掷**继电器，未 SetOn 时按 **Relay-NC** 把 BST 接向 **`PB0`**（`SCH` L724/L725）⇒ 不闭 `K110` 时 AC 源到不了 BST，裁定 (ii) 的接地参考驱动**不成立**；
- **门禁看不见**：`verify_bst_sw_sequence.py` 中 `K110`/`110`/`needsClosed`/`relaySet` 命中数**均为 0** ⇒ 不读契约闭合集合、不比对 SetOn。
- **处置权在 Captain**（三选一：补 `K109`/`K110`；或更正契约/v20 的 `[110]`；或加"SetOn vs needsClosed"断言）—— 与你我均无权单方改门禁脚本/契约。

## 4. 交付

- **`t26-correction-8`：ACCEPT（台账更正生效、实质未变）**；§3(a) 的版本指针不一致已按 **Captain 裁定**以书面登记、**不再产生新版本**（权威以 `revision` 字段为准）。
- **台账请补登** `t26-tp20-k110-finding.md`（19:13:44）与本文件。
- **t24 结论（已按 Captain 裁定扩展）**：TM601 可零电容；**TM600 必须保留 `K57_CAP_BST_SW`，并须补 `K109`/`K110`**（K110 finding 已采纳，派 `t29` 修复 + `t30` 门禁断言）。
- **本条 finding 的处置已定（不必再等）**：Captain 采纳 **①+③**、**不采纳 ②**（除非契约 owner 出示"夹具已硬连 ACM20→BST"物证；`SCH` L42/L43/L724 的 K110 路径本身即反证）。
  - `t29`（ate-implementer，repair，`sourceTaskId=t24`）：按冻结契约权威集合补 `K109`/`K110`，**须经本复核者独立复核**，落盘由 Captain 执行（REPLACE 语义）。
  - `t30`（compile-diagnostician）：`bst-sw` 门禁加"**SetOn 集合 vs 契约 `needsClosed`**"断言；**阳性对照＝t29 落盘前必须对 TM600 缺 `K110` 报红**，落盘后转绿，且**不得硬编码本 run 特例号**。
  - 我的复核判据已预先承诺（见 `review/t26-tp20-k110-finding.md` 与本文件）：只补权威集合所需项、TM601 是否需同补须给判据、机制/locator 写入注释、不得动负列表与 `_S1S2` 共享家族；门禁断言须**独立在只读沙箱重放阳性对照**、须泛化读契约、须给全树 A/B 证明无误报、失败信息含 locator。
- **仍未决**：RS-1..RS-4 落地（已派 `t28`）+ 生成器侧落改（消除"重生成静默抹除"）；审计链第二层风险（已派 `t31`）。
- **纪律已锁定**：**门禁绿 ≠ 电性正确**（K110 即新证据）。
