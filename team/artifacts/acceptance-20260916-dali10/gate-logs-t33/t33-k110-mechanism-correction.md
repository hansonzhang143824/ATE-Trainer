# t33/K110 机制：**更正挂条**（t42/t44 已推翻本文主语）

> **本文件是 `t33-k110-mechanism.md` 的更正挂条，不替代它。**
> 被更正的三处**保留原样**（作为"我曾如此断定"的留痕），以下为**以 t42/t44 为准**的现行结论。

## 1. 被推翻的表述（我方产物中现存的确切位置）

| 文件 | 行 | 原文（节选） | 状态 |
| --- | --- | --- | --- |
| `gate-logs-t33/t33-k110-mechanism.md` | L39 | "**K110 必须 SetOn —— 实现缺闭合是真缺陷**" | ❌ **作废** |
| `gate-logs-t33/t33-k110-mechanism.md` | L53 | "ACM 源在 K110 公共端；通电到 BST、默认到 PB0 ⇒ K110 必须 SetON" | ❌ **作废** |
| `gate-logs-t33/t33-k110-mechanism.md` | L57 | "t30 的契约断言方向正确" | ⚠️ **有条件成立**（见 §3） |
| `gate-logs-t33/t33-k110-mechanism-recheck2.log` | L72 | "ACM 到 BST 由 K110 单独完成，必须 SetOn" | ❌ **作废**（日志作为过程记录保留，不追改） |
| `gate-logs-t33/t33-k110-mechanism-recheck.log` | L41 | 同上 | ❌ **作废**（同上） |
| `gate-logs-t30/t30-k110-cross-check.log` | L30 | "断言要求契约必需 K110 …… 与 SCH L42/43/L724 方向一致" | ⚠️ **有条件成立**（见 §3） |

## 2. 现行结论（依 `t42` = requirements/verdict=pass 与 `t44` 补遗）

1. **`SW12_U1REF_BST_ACM` 是 ACM200 的 channel 5**（`Pin_Channel_define.h`：宏值 `S5_5,S6_5,…`）⇒ **到 BST 需 `K48 + K76`**；
   **`K110`（`K110_ACM18_BST`）属另一台仪器 `PB0_BST_ACM`（ch18）**。
2. 因此我原第 1 句"**ACM 脚路线由 K110 单独完成、必须 SetOn**"**只对 ch18 成立，对本案仪器（ch5）不成立** ⇒ **作废**。
3. 我原第 2 句"K109 不属 ACM 脚路线"方向仍成立，但**应精确化**为：
   **`K109`/`K110` 属 ch18 路线，不是本案仪器（ch5）的路线**。
4. 我原第 3 句"契约字面仍要求 K109"**成立**（`relaySet` 与 `pinRouteTable…CH0 Low` 均含 109）。
5. **BST–SW 闭集（ch5 口径）= `[48,61,76]`**（SW 侧经 `K61_ACM8_SW`）。Captain 另更正为两侧并集 **`[48,60,61,76]`**（BST 侧 ∈ ACM200 族 `[48,76]`、SW 侧 ∈ FPVIe[L] 族 `[60,61]`）——**以 Captain 的表述为准**。

## 3. 对 t30 断言的影响（关键：我的期望集来源是**被标为错项的那个映射**）

- 我的 `check_contract_closures()` 期望集**全读** `aliasResolution[*].resolution.closedRelayNumbers`，
  **无任何 K 号字面量** ⇒ 该字段错，断言就跟着错。setup-architect 已就此自认（其映射做错），
  并指出：**现在的断言"要求一个非必需的 110，且看不见真正的缺口 `K48/K76`"**。
- ⚠️ **归因更正（rev 33 之后）**：**rev 33 起该字段已消歧为 ch5**（`closedRelayNumbers = [48,60,61,76]`、`110` 移入 `closedRelayNumbersSuperseded`、`contestedAttribution.status = CLOSED (t53): … CHANNEL 5`）⇒ **"权威值仍是 `[110,61]`"及由此推出的"未消歧假红"均已不成立**；**落盘后 `bst-sw` 的预期＝GREEN**（路径 1 条件已满足，不需路径 2 的归因）。以下为**当时（rev 26 前）**的写法，保留作留痕：
- 但**方向问题需与"归属未消歧"分开看**：rev 26 已把该字段标注为
  `contestedAttribution: CONTESTED - preserved (add-only) pending owner ruling` ⇒
  **当前是"契约权威值未消歧"，不是断言写错**。我 t54 的预备实测据此给出两条路径：
  - 路径 1（`t53` 把权威值切到 ch5）⇒ 期望随契约更新 ⇒ 落盘后 `bst-sw` 期望 GREEN；
  - ~~路径 2（只增不翻）⇒ 落盘后仍红，红因是"缺 110"= 假红~~ ⇒ **该路径已随 rev 33 消歧而取消**（历史留痕；现口径：权威值 = ch5，落盘后预期 GREEN）。
- **阳性对照必须重建**：若权威值切 ch5，阳性对照应为"**TM600 缺 `K48/K76` ⇒ 红**"，
  而非现行的"缺 `[110]`"。**重建须在新期望集合下重跑阳性/阴性 + 全树 A/B，且不得改动 `gate_baseline.json`**（待 Captain 派单口径）。

## 4. 边界
静态连通性/登记层面；**非电性结论**；**无机台实测**；**编译闭环 ≠ 电性签核**。
（预期：`t43` 为独立复核方；若其反转 ch5 判定，本挂条须随之再更正。）
