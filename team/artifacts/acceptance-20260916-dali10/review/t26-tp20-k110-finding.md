# t26/t24 追加 finding + 复核基准更正（基于现盘 `test-plan.json` v20）

- 审查人：rule-reviewer · 日期：2026-09-16
- 触发：test-strategy-architect 指出我 §H.1 的行为"复核基准 v19"**不在盘上**；我独立复核**确认其成立**。
- 只读声明：未修改任何被审产物（仅写 `review/` 下文件）。

---

## A. 复核基准更正（我方缺陷，已更正）

### A-1 事实
- **我 §H.1 锁定的基准 `164399 B / d2aef4ad5f3e48f939256220bbcf4baa4a0693cfd1770d31c8868f9eb41719bb` 不在盘上任何文件中。**
- 盘上快照实测（glob 全工作区）：`v1..v10, v12..v18, v20` ⇒ **`test-plan.v11.json` 与 `test-plan.v19.json` 均 ABSENT**（我实测确认，与架构师所述一致）。
- **现盘 `test-plan.json` = 166099 B / `fabdd24f220d3b3e1eaf2bc782bf896adceb38074a72bffa7ba0d2d181ec8ed4` / mtime 19:04:49 / `revision: v20 (t17 closure - BST-SW ruling (ii) + idempotent generatedAt)`**。

### A-2 定性（我的责任，如实记录）
我的**哈希读数本身正确**（与 t17 交接公告 `d2aef4ad…` 一致），但**我在两次快照之间读取、且未保留副本**；作者习惯"重建前存当前版"，v19 落在 `v18`(18:09:28) 与 `v20`(19:04:49) 之间**从未落盘**。
⇒ 定性为**我方的可追溯性缺陷**（引用无法在盘上复现的哈希），**非读取错误、非作者记录问题**。t9 若据此追溯会指向盘上不存在的字节。
**已更正**：`review/t6-review-checklist.md` §H.1 加作废标注、新增 §I 以 v20 为现行基准。

### A-3 追加纪律（第 2 条）
> **凡引用产物哈希，必须同时确认该哈希对应盘上实际存在的文件**（`glob` + 现算比对自证）；仅记录哈希不足以支撑可追溯性。

### A-4 同类混淆：`1925250d…` 是快照副本、不是现盘
我此前**两处**把 `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016` 当作"现行 v20"。实测：
- **现盘 `test-plan.json`** = `fabdd24f…`
- **快照副本 `test-plan.v20.json`** = `1925250d…`（**同 size 166099，不同字节**）

⇒ 二者同属"v20 家族"但**不是同一份字节**；引用时必须标明"现盘 / 快照副本"。这是我**第二次**同类"同 size 不同哈希"混淆，已并入 A-3 纪律。

### A-5 架构师零成本复跑：我逐项复核全部吻合 ✅
```text
SW12_U1REF_BST_ACM                    = 3  (expected 3) ✅
INTENDED BUT CURRENTLY UNREALISABLE   = 1  (expected 1) ✅
ruling (ii)                           = 3  (expected 3) ✅
lowercase 'intended-but-unrealisable' = 0  (expected 0) ✅
```
其"按小写连字符形式检索会误得未落地"的告诫**成立**。
**幂等性我独立复核**：`test-plan-build.py` 中 `datetime.now` 命中数 = **0** ⇒ `generatedAt` 确为 revision 派生常量 ✅

---

## B. ⚠️ 新 finding（实质）：裁定 (ii) 的 `[110]` 未落地，且门禁看不见

### B-1 事实链（全部实测）
| 来源 | 要求 |
|---|---|
| `test-plan.json` v20 `items[TM600].assumptions[0]` | *"…bootstrap-to-switched rail is driven by the GROUND-REFERENCED ACM200 pair `SW12_U1REF_BST_ACM` (**closed set [110, 61]** = `K110_ACM18_BST` / `K61_ACM8_SW`)"* |
| v20 `globalRulesApplied` → **R-BST-SW** | *"…driven by the GROUND-REFERENCED `SW12_U1REF_BST_ACM` pair (ruling (ii); **closed set [110,61]**)"* |
| `setup-contract.json` rev24 `/aliasResolution[3].resolution` | `relayChain[0].relay = K110_ACM18_BST`、`number = 110`、**`closedRelayNumbers[0] = 110`**；`bstRuling_ii` 同义 |
| contract `/tmDeltas/TM600/relaySet` | 含 **110** |
| contract `/tmDeltas/TM600/pinRouteTable.BST` | CH1 Low → `needsClosed = [110]`；CH0 Low → `needsClosed = [109, 110, 138, 139, 145, 146]` |
| `SCH-Connect-Map.txt` | L269 `S1_FPVIe_FL1 -> K133(NC) -> **K109(ON) -> K110(ON)** -> BST_F`；L270 同（`_SL1`）；L43/L44（ch0 路径）同样串 `K109 -> K110` |

**实现侧实测（现盘 `ForCodexDebug/source/test.cpp` = 469,714 B / `15c7d2b8…`）**：
- `TM600_HS_RDSON` 段内 **`K109` = 0 次、`K110` = 0 次**；
- 其唯一 SetOn = `K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`
  ⇒ **`K61` 已闭（[61] 落地），但 `K110` 缺失 ⇒ 裁定 (ii) 的 `[110, 61]` 只落地一半**；
- 同一缺口存在于**我 t24 判 ACCEPT 的 payload**（`444810dd…` `L203`）：其中同样**无 `K110`**。

### B-2 为什么这是真问题（而非"路径由其它继电器代偿"）
`K110_ACM18_BST` 是**双掷**继电器：S5_ACM200_FH18/SH18（ACM18）与 `PB0` 分别经 **`Relay-NC`** 接出（`SCH-Connect-Map.txt` L724/L725）。即在**未 SetOn（NC 默认导通）**状态下，`K110` 把 BST 节点接向 **`PB0`**，**不是** ACM18。⇒ 若不显式闭合 `K110`，AC 源**到不了 BST 节点**，裁定 (ii) 所指的"接地参考 `SW12_U1REF_BST_ACM` 驱动 BST−SW"**无法成立**；`[110,61]` 这一"封闭集合"的一半缺失。

### B-3 为什么此前没被发现（门禁盲区）
现行 `scripts/verify_bst_sw_sequence.py` 中：**`K110`=0、`110`=0、`needsClosed`=0、`relaySet`=0**（命中数实测）。该门**不读契约的 relaySet/needsClosed，也不比对 SetOn 的闭合集合**，只按 meta 拓扑指纹收目标并检查 BST≥SW 的大小关系 ⇒ **结构上不可能发现"该闭的继电器没闭"**。

### B-4 判定与建议
- **severity: high**（若不闭合，被测轨激励缺失 ⇒ 该项在硬件上不成立；且我的 t24 ACCEPT 未覆盖此判据，需补）。
- **不确定性声明（如实）**：我无法排除"夹具层面 `SW12_U1REF_BST_ACM` 已硬连到 BST、故 `K110` 不必要"这一可能。但**冻结契约与计划均以 `[110,61]` 为权威闭合集合**，`SCH` 图上 `K110` 是唯一可达 BST 的 ON 触点路径 ⇒ **两种解释必有一错**：要么实现缺闭合，要么契约/计划的 `[110]` 是错的。**须由 Captain/setup-architect 以夹具证据裁定**，不由我单方断言。
- **建议动作（我最初提出）**：① 实现侧补 `K109`/`K110`；或 ② 若夹具已硬连，则**更正契约与 v20 的 `[110,61]` → `[61]`** 并登记理由；③ `verify_bst_sw_sequence.py` 应加"闭合集合 vs 契约 needsClosed"的断言。
- **对我 t24 结论的修正**：t24 的 ACCEPT **仅限于"代码不变量 / t22 电容裁定 / 冻结口径 / scope"**，**未覆盖 BST−SW 闭合集合**；本 finding 补上该缺口后，**payload 的 BST 路径闭合集合不具备 ACCEPT 结论**。

---

## B-5 ✅ Captain 裁定（2026-09-16，已生效；本节取代 B-4 的"建议动作"）

**采纳路线 ① + ③；不采纳 ②**（除非契约 owner 出示"夹具已硬连 ACM20→BST"物证 —— **`SCH` L42/L43/L724 的 K110 路径本身即反证**）。

**Captain 独立复核的 locator（我逐条实测，9/9 全对，且比我原引更完整）**：
- `SCH-Connect-Map.txt`：**L42** `CH0 Low -> BST [Kelvin] … K109,K110,K138,K139,K145,K146`；**L43** `… K109(ON) -> K110(ON) -> BST_F`；**L109** `… K109(ON) -> K110(NC) -> PB0_F`；**L110** `… K110(NC) -> PB0_S`；**L724/L725** `S5_ACM200_FH18 -> K110(NC) -> PB0_F` / `SH18 -> … PB0_S`。
- `setup-contract.json`：**L145** `"BST": "S5_ACM200_FH18/SH18 (K110_BST)"`；**L1440** `"relay": "K110_ACM18_BST"`；**L1897** `"relayPath": "K110_ACM18_BST -> K61_ACM8_SW"`。
- **⚠️ 我方更正**：我 B-1 表内引 CH1→BST 为 `SCH` **L269/L270**；Captain 补的 **L42/L43 是 CH0 路径**。**TM600 SetOn 走 CH0（K83/K60/K61）⇒ L42/L43 才是本案主路径 locator**，L109/L110 是 K110 的两掷对照。二者都真，**主引应以 CH0 为准**。

**已派任务**：
- **`t29`**（ate-implementer，repair，`sourceTaskId=t24`，finding id `T26-TP20-K110`）：按冻结契约权威集合补 TM600 的 `K109`/`K110`，机制与 locator 写入 payload 注释；**须经本复核者独立复核**；落盘由 Captain 执行（REPLACE 语义）。
- **`t30`**（compile-diagnostician）：`bst-sw` 门禁增加"**SetOn 集合 vs 契约 `needsClosed`**"断言；**验收要点＝阳性对照**：t29 落盘前该断言必须对 TM600 缺 `K110` **报红**（证明真能抓缺陷），落盘后转绿；**不得硬编码本 run 特例号**。

**本复核者的预先承诺判据（供 t29/t30 直接对齐，避免返工）**：
- **t29**：(a) 只补契约权威集合所需项、**不引入**未在 `needsClosed`/负列表内的继电器（最小端点纪律）；(b) **`K109`/`K110` 是否同样补进 TM601 —— 须给判据**（若不需要，写明"为何 TM601 不同"，**不得默默只改一处**）；(c) 机制/证据 locator 写入 payload 注释；(d) **不得**触碰 K87/K88/K89 负列表继电器与 `_S1S2` 共享家族来达成闭合。
- **t30**：(a) **阳性对照须由我在只读沙箱独立重放**（落盘前→红 / 落盘后→绿），**不采信自述**；(b) 断言须**泛化**（读契约 `needsClosed`/`relaySet`，不硬编码 `[110,61]`、不硬编码 TM600 特例）；(c) 须给**全树 A/B**并证明**无误报**（或逐条解释）；(d) 失败信息须含 **file:line** locator。

---

## C. 对既有结论的影响汇总
| 结论 | 是否受影响 |
|---|---|
| t22 的 4 条电容判定（K5/K44/K45 假阳性、K57 真红） | **不受影响**（K57 判定与 BST 路径闭合集合是两件事；K57 仍是电容继电器） |
| t24 的 payload ACCEPT | **部分收回**：不变量/冻结口径/scope 仍然成立；**BST 路径闭合集合（`[110,61]`）不在其覆盖内**，见 B。 |
| t26 的 meta ACCEPT | **不受影响**（meta 侧；且 `powered_pins` 含 `BST_SW` 恰与 B 相符） |
| 门禁"11 GREEN + cbit KNOWN-RED" | **不受影响**，但**其绿不能证明 BST 路径闭合**（B-3 盲区）—— 这正是"编译/门禁通过 ≠ 电性正确"的又一实例 |
