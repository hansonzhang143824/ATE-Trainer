# t39 / 交付件 `t41-tm601-bst-path-determination.md` — TM601 的 `SW12_U1REF_BST_ACM` 5 V 如何到达 BST（四方证据判定）

> ## ⚠️ 现盘 payload 更正横幅（v1.25，事实性更正；单点插入、不改既有正文）
> **现盘交付件 = 43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24（566 行）**，TM600 SetOn = `[13,48,57,60,61,76,83,85,126]`（**含 `K48/K76`、可执行 `K109/K110` = 0**）；**canonical 已由 Captain 定格为该字节、写入已停**。
> 本文件内所有把 **`39,457 B / 2d0984d992d5d8cb…`**（或 `38,147/272667f3…`、`36,381/73b511b7…`、`35,014/444810dd…`）写作"**现盘**"的表述，**均指 2026-09-16 21:09:24 之前的时点、属历史**；同一路径在 20:45–21:09 被**就地覆盖四次**、**从未有副本**，故旧值全树 0 命中是**正确结果**。引用一律以**现算**为准。

- Author: **setup-architect**（契约 owner 侧）；Independent review: **rule-reviewer**（t40，作者不得自审）
- 判定对象：payload 中 **TM601_LS_RDSON** 曾执行的 `SW12_U1REF_BST_ACM.Set(FV, 5, …)`
- 依据四方：**契约 rev 24**（`fd00a508…`）+ **IR**（`schematic-ir.json` / `schematic-validation/path_proofs.json.txt`）+ **权威网表**（`project/DALI/Dali-SCH.csv`）+ **端子图**（`knowledge/hardware/relays.md:3-31`）
- 边界：本文件**只判定与出修法**；不改 `test.cpp`/payload/计划/门禁脚本；`devel` 零写入。

---

## 1. 结论（唯一，先答 acc1）

> **TM601 的 `SW12_U1REF_BST_ACM.Set(FV, 5, …)` 到达的不是 BST，而是 `PB0_F_S1` / `PB0_S_S1`（及同网的 `PWM1_F_S1`/`PWM1_S_S1`）。**
> 在 TM601 的契约闭合集合下**不存在**从 ACM200 S5 通道脚到 BST 的路径：该路径唯一的开关是 **`K110_BST_S1`**，而 **`K110` 不在 TM601 的任何授权集合内**（`relaySet` 无 110、`aliasesUsed=[sw2pgnd]`、`scopePins` 无 BST、`pinRouteTable` 无 BST 键）。
> ⇒ **该驱动属"悬空激励"**（有落点，但落在非目标节点上），**不构成 TM601 的 BST 5 V**。

## 2. 逐步路径（逐跳 locator）

### 2.1 实际路径（K110 未激磁 ⇒ 到 PB0）

| 跳 | 节点/元件 | 状态 | locator |
| --- | --- | --- | --- |
| 0 | `SW12_U1REF_BST_ACM`（ACM200，S5 通道，`S5_ACM200_FH18`/`SH18`）输出 5 V | 驱动 | `StdAfx.h:69`（`extern ACM200 SW12_U1REF_BST_ACM`）；`Pin_Channel_define.h:20`（`S5_5,S6_5,…`） |
| 1 | ACM 脚直接落在 **`K110` 的公共端**：`S5_ACM200_FH18` + `K110_BST_S1.6` + `K109_BUSL_PB0_S1.4` **同一 net** | — | 网表 `Dali-SCH.csv` net `NetK109_BUSL_PB0_S1_4`；IR `accepted_path_proofs[S5_ACM200_FH18->PB0_F_S1].path` |
| 2 | **端子图**：`6 = COM2`；**复位态 `6-7` 通**（磁保持继电器：标 NO 的脚在无电时闭合） | K110 **未 SetOn** | `knowledge/hardware/relays.md:25`、`:29`（"默认 2-3 通、6-7 通"）、`:31` |
| 3 | 经 K110 pin7 → net `NetK110_BST_S1_7` = **`PB0_F_S1`**、`PWM1_F_S1`、`S24_P10`、`K147_PB0_OSC.2`、`R_PB0.1` | 落点＝**PB0_F** | 网表 net `NetK110_BST_S1_7`；IR 同上 path 的 `to_net` |
| 4 | S 侧同理：`SH18` → pin3 → **复位态 `2-3`** ⇒ pin2 → net `NetK110_BST_S1_2` = **`PB0_S_S1`**、`PWM1_S_S1` | 落点＝**PB0_S** | 网表 net `NetK110_BST_S1_2`；IR `accepted_path_proofs[S5_ACM200_SH18->PB0_S_S1]` |
| 5 | `PB0_F_S1`/`PB0_S_S1` 在网表中是 **`[PORT]`（DUT 引脚）** | — | `Dali-SCH.csv` MemberType=PORT 行 |

### 2.2 若要到达 BST（需 K110 激磁 —— 而 TM601 不授权）

| 跳 | 路径 | locator |
| --- | --- | --- |
| A | `S5_ACM200_FH18 → K110(ON: 6→5) → NetK57_CAP_BST_SW_S1S2_3`（含 `BST_F_S1`、`K57.3`、`K76.5`、`K134.4`、`R_BST.1`） | 网表该 net；IR `accepted_path_proofs[S5_ACM200_FH18->BST_F_S1]` **`required_on=[110]`**、path 只有 `K110(110:ON, 6→5)` |
| B | `S5_ACM200_SH18 → K110(ON: 3→4) → NetK76_ACM_BST_S1_4`（含 `BST_S_S1`、`K76.4`、`K135.4`、`R_BST.2`） | 网表该 net；IR `[S5_ACM200_SH18->BST_S_S1]` **`required_on=[110]`** |
| C | 端子图：置位态 `3-4` 通、`6-5` 通 | `relays.md:23`、`:24`、`:29` |

## 3. 三方证据并用（acc2）

1. **IR（`schematic-validation/path_proofs.json.txt`，669 条 accepted path proofs）**
   - `S5_ACM200_FH18 -> BST_F_S1`：**`required_on=[110]`**、`path=[K110(ON, 6→5)]`、`defaultClosedRelays` 未列为非空 ⇒ **唯一必需件 = K110**；
   - `S5_ACM200_SH18 -> BST_S_S1`：**`required_on=[110]`**、`path=[K110(ON, 3→4)]`；
   - `S5_ACM200_FH18 -> PB0_F_S1` / `SH18 -> PB0_S_S1`：**`required_on=[]`**、`path=[K110(NC, 6→7 / 3→2)]` ⇒ **未激磁时的合法落点就是 PB0**；
   - 含 `109` 的 accepted path 共 **21 条**，**全部**属 `S10_CH0_B` / `S1_FPVIe_FL0,FL1,SL0,SL1` / `S8_QVM_CH0-` 路线，**无一条 `S5_ACM200_*`** ⇒ K109 与 ACM 路线无关（与 t35 附录 F 一致）。
2. **权威网表 `Dali-SCH.csv`（net 成员）**
   - `NetK109_BUSL_PB0_S1_4` = `S5_ACM200_FH18` + `K109.4` + `K110.6`（同 net ⇒ ACM 源即 K110 公共端，**中间无器件**）；
   - `NetK110_BST_S1_7` / `NetK110_BST_S1_2` = PB0/PWM1 侧；`NetK57_CAP_BST_SW_S1S2_3` / `NetK76_ACM_BST_S1_4` = BST 侧；
   - `K109` 的 COM1/COM2（pin3/pin6）在 `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`，其 NO 脚 pin2/pin7 为单成员（悬空）net ⇒ K109 与 ACM→BST 无关。
3. **端子图 `knowledge/hardware/relays.md:3-31`（G6K-2G-Y DPDT）**
   - `3=COM1、6=COM2、2/7=NO、4/5=NC`；**复位 `2-3 & 6-7`、置位 `3-4 & 6-5`**（L21-27/L29/L31 的"磁保持反直觉"提示）⇒ 与网表 net 成员**完全吻合**：K110 未激磁 ⇒ ACM 源 → PB0；激磁 ⇒ ACM 源 → BST。

## 4. 两种结论的分支处置（acc3）

### 分支 **(B)：TM601 不需要 BST 5 V —— **本判定采用此分支**

- **替代路径（TM601 的实际激励方式，带 locator）**：
  | 目的 | 路径 | IR `required_on` | locator |
  | --- | --- | --- | --- |
  | SW 强制 | `S1_FPVIe_FL0 → K89(NC) → K60(ON) → K61(ON) → SW_F_S1` | **`[60,61]`** | IR `accepted_path_proofs[S1_FPVIe_FL0->SW_F_S1]` |
  | SW 强制（S 侧） | `S1_FPVIe_SL0 → K88(NC) → K60(ON) → K61(ON) → SW_S_S1` | **`[60,61]`** | IR `[S1_FPVIe_SL0->SW_S_S1]` |
  | PGND | `S1_FPVIe_FH0 → K87? → … → K154/K155 → PGND_F_S1`；`SH0 → PGND_S_S1` | **`[154,155]`** | IR `[S1_FPVIe_FH0->PGND_F_S1]` / `[S1_FPVIe_SH0->PGND_S_S1]` |
  ⇒ 与契约 **`aliasResolution[sw2pgnd].closedRelayNumbers = [154,155,60,61]`** **逐项一致**；契约 `forceSenseTopology` = "force SW<->PGND (FPVIe0 CH0, PGND on the high terminal), sense SW-PGND Kelvin pair"，`measurePlan` = `MV SW-PGND` + `MI PMID_SW` ⇒ **全项无 BST 参照**。
- **契约侧一致性（三处独立指标都排除 BST）**：`tmDeltas.TM601.aliasesUsed=["sw2pgnd"]`（**无 bst2sw**）；`relaySet` **不含 109/110**；`scopePins=[SW,PGND,PMID,VBUS,VBAT,VDRV,V1P5,AGND]`（**无 BST**）；`pinRouteTable` **无 BST 键**（TM600 才有）。`aliasResolution[bst2sw].usedByTm = ["TM600 (BST must lead PMID)", "TM1205 …"]`（**无 TM601**）。
- **为何 `SCH-Connect-Map.txt:724/725`（`K110(Relay-NC) -> PB0`）不构成反证**：它**正是**本判定的机制图 —— 它描述的"未动作时 ACM 源落在 PB0"与端子图 L25/L29、网表 `NetK109_BUSL_PB0_S1_4` 的成员关系**三方一致**；把它当作"源能到 BST"的证据会与端子图/IR 的 `required_on=[110]` 相矛盾。

### 分支 **(A)（未被采用，列出以备考）**：若 Captain 改判 TM601 **需要** BST−SW 5 V

需同时改动（逐项 locator，缺一不可，否则又是"声明与实现不一致"）：
1. `tmDeltas.TM601.scopePins` 增 `BST`；`relaySet` 增 `109`、`110`（`tmDeltas.TM601`）；
2. `aliasResolution[bst2sw].usedByTm` 增 `TM601`（现仅 TM600/TM1205）或其 `resolution` 增 TM601 专用条目；
3. `tmDeltas.TM601.pinRouteTable` 增 `BST` 键并给出 `needsClosed`（ACM 路线 `[110]` + SW 侧 `[61]`，与 TM600 同源）；
4. `measurePlan` 需增 BST 参照的量测（现仅 `MV SW-PGND` / `MI PMID_SW`）；
5. **计划侧**同步（`test-plan.json` TM601 的 `stimulus`/`measure` 行）；
6. **payload 侧**：TM601 的 SetOn 增 `K110_ACM18_BST`（`K109` 非 ACM 路线必需，见 §3）。
**代价**：契约 → rev 25/26、计划 → v22、payload 再造一版 —— 而**当前四方证据无一支持该分支**，故不推荐。

## 5. 补充问（acc4）：悬空激励应"移除"还是"补齐通路"

> **推荐：移除**（t38 已按此执行；**现盘 payload = 39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` @19:55:59，TM601 块内已无 `SW12_U1REF_BST_ACM` 驱动**）。

**判据（四条，按强度排序）**
1. **契约权威**：TM601 的 `aliasesUsed`/`scopePins`/`relaySet`/`pinRouteTable` **四处都不含 BST 或 K110** ⇒ 补齐通路＝**超出该条目的契约授权**，属"多闭/多驱动"，需要先改契约（分支 A，无证据支持）。
2. **IR 权威**：TM601 关心的两条路径 `S1_FPVIe_FL0/SL0 -> SW`（`[60,61]`）与 `-> PGND`（`[154,155]`）**都不经过 ACM200，也不经过 BST**。
3. **风险面（本条最重）**：K110 未激磁时 ACM 的 5 V 落在 **`PB0_F_S1`/`PB0_S_S1`** 上，而这两个 net 在网表中是 **`[PORT]`（DUT 引脚）**，且同网还挂着 `K147_PB0_OSC`、`S24_P10`、`R_PB0`、`TP_PB0_*`、`PWM1_*` ⇒ **该驱动会在 TM601 测试期间把 5 V 施加到 DUT 的 PB0/PWM1 节点**（非预期偏置），属**功能性风险**，不是"冗余"。
4. **最小端点纪律**：t38 的判定与执行与契约 "minimal-endpoint" 原则一致（不闭/不驱动契约未授权件）。

**反方（若你要保留驱动）唯一可能理由**：TM601 需要 BST 参照的量测 —— 但契约 `measurePlan` 与 IR 都不支持，且 DFT/OVERVIEW 的 TM601 判据是 **SW−PGND 的 R_DSON 7.5 mΩ**（`limits.authoritative = "ExpectValue=7.5 (OVERVIEW…)"`）。⇒ **不成立**。

## 6. UNKNOWN（acc5，如实登记，不得写成"已排除"）

| # | UNKNOWN | 需要什么证据才能闭合 |
| --- | --- | --- |
| U1 | 夹具侧是否存在"硬连 ACM→BST"（绕过 K110） | 夹具手册/接线表（本工作区未提供）；**当前无证据支持**，且与端子图/网表不一致，故不采信 |
| U2 | `PB0_F_S1`/`PB0_S_S1`/`PWM1_*` 在 TM601 期间是否被其它源驱动或悬空 | 机台/夹具侧驱动状态（导出不可判定）；本判定只断言"ACM 5 V 会到达该 net"，不断言该 net 的对外影响程度 |
| U3 | DFT 是否对 PB0/PWM1 施加跨条目约束 | `DFT.csv`（357 行）以**精确 token `PB0`** 检索**无命中**（已实测）；**这不能证明 PB0 无约束**，仅说明该 CSV 未用该 token 记录 |
| U4 | K109 的 NO 脚（pin2/pin7）单成员 net 是"未使用触点"还是导出范围限制 | 原理图原件/网表导出范围说明；不影响本判定（结论只依赖 K110 的公共端与两掷） |

## 7. 引用与复算

- 契约：`setup-contract.json` rev 24 = 328,805 B / `fd00a5082170293fcea29446c009fc432977d61a8f624ef17ac1c82f41515a18`（**本任务未改动**）
- IR：`schematic-ir.json`（457,531 B / `9f4a7707fb0a1b31f4f884dcac617c5273506de6c2a088a3b9c3f1b20683f639`）+ `schematic-validation/path_proofs.json.txt`（2,548,322 B，669 条 accepted path proofs）
- 网表：`project/DALI/Dali-SCH.csv`（307,157 B，1,338 行）
- 端子图：`knowledge/hardware/relays.md`（13,624 B / `8029ee13690ca2158e48ea002bad69f2d943d76126bb133b4e54b8401934fcdb`，L3-31）
- payload：现盘 39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` @19:55:59（TM601 块已无 ACM 驱动）；上一版 38,147 B / `272667f3…` 含该驱动


---

## 附录 G（captain 新增判据并入，v1.1）

### G.1 两句并列口径（**必须并列，防后人误判**）

> **(a)** **`K110` 必需**：ACM200 S5 通道脚与 `K110` 公共端同 net（网表 `NetK109_BUSL_PB0_S1_4`/`_5`），**通电 6-5/3-4 → BST，默认 6-7/2-3 → PB0**（端子表 `relays.md` L22-31）⇒ **ACM↔BST 由 `K110` 单独完成**。
> **(b)** **`K109` 不属 ACM 路线，但契约字面仍要求它**（`tmDeltas.TM600.relaySet` 含 109 且 `pinRouteTable.BST["CH0 Low"].needsClosed` 含 109）⇒ **t29 同闭 `K109`+`K110` 属"依约保守"、合规**；**后人不得以"K109 本非 ACM 所需"为由把它当"多闭"删除**（契约文本若要消除该歧义，只能走"按路线分列"，见 `t35` 路径 A）。

### G.2 PB0 意外驱动风险（按 FACT / INFERENCE / UNKNOWN 分开写；**尚无机台实测**）

- **FACT（网表/派生表可核）**：`SCH-Connect-Map.txt:724/725` = `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`、`S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S`；`SCH:723` 记 `PB0_PWM1 … 需闭合: 无(默认导通)`；网表中 `K110.7 (NO) → NetK110_BST_S1_7`（含 **`PB0_F_S1`（`[PORT]`）**、`PWM1_F_S1`、`S24_P10`、`K147_PB0_OSC_S1.2`、`R_PB0_S1.1`、`TP_PB0_F_S1.1`）、`K110.2 (NO) → NetK110_BST_S1_2`（含 **`PB0_S_S1`（`[PORT]`）**、`PWM1_S_S1`、`TP_PB0_S_S1.1`）。（我实测复算一致。）
- **INFERENCE（由 FACT 推出，非实测）**：若 TM601 在 `K110` 未激磁时驱动 `SW12_U1REF_BST_ACM` 输出 5 V，则**该 5 V 会出现在上述 `PB0_F_S1`/`PB0_S_S1`（DUT 引脚）及其同网节点上** ⇒ 风险**不止"BST 未被驱动"**，而是**对 DUT 的 PB0/PWM1 侧施加非预期偏置**（并可能经 `K147_PB0_OSC`/`S24_P10`/`R_PB0`/测试点影响到其它测量或 OSC 路径）。
- **UNKNOWN（须机台/夹具侧证据）**：① 两 net 在 TM601 期间**是否另有源驱动或处于悬空/高阻**；② PB0/PWM1 在正常流程中是否本就被偏置（及 DFT 是否对其有跨条目约束）；③ 非预期偏置在任何测量回路上的**实际后果**。⇒ **未做任何机台验证**，本项**只作事实与风险登记，不作电性判定**。
- **处置**：**移除该悬空驱动**（t38 已执行）—— 亦是本风险的**最小消除手段**（保留＝持续存在该偏置）。

### G.3 payload 版本更正（captain 消息引 38,147；**现盘已前进一版**）

```
现盘  implementation-payload-TM600-TM601.cpp = 39,457 B / 2d0984d992d5d8cb11868660b29cb…  @19:55:59   ← t38 已移除 TM601 的 SW12_U1REF_BST_ACM 驱动（TM601 块内命中 0）
38,147 B / 272667f3… @19:30:55 = **含该悬空驱动**的版本（rule-reviewer 的 t29 verdict 针对此版）
36,381 B / 73b511b7… @（t29 首次修复）= 已取代的中间态；35,014 B / 444810dd… 同（均无副本）
```
⇒ **t40 的"重新 pin/review"请以 `39,457 B / 2d0984d9…` 为目标**（该版已无悬空驱动）；若务必以 38,147 为审查对象，则须在审查结论中同时记录"该版含 G.2 所述 PB0 偏置风险"。


---

## 附录 H（captain 绑定条款 ①–⑥ 逐条并入，v1.2）— **可达性证明优先，契约登记不得替代**

### H.1 性质与证法（条款 ①）

**本项＝落盘前的独立"可达性路径裁定"**：只回答"**从 ACM200 S5 源（`S5_ACM200_FH18`/`SH18`）出发，经哪些继电器/触点状态、经哪些 net，能否到达 `BST_F`/`BST_S`**"，每跳给 locator。
**四方并用**（缺一不可）：**① 原理图 IR 路径表**（`schematic-validation/path_proofs.json.txt` 的 `accepted_path_proofs`）**② 权威网表 net 成员**（`project/DALI/Dali-SCH.csv`）**③ 端子表触点语义**（`knowledge/hardware/relays.md` L18-31）**④ payload 实际激励指令**（现盘 payload 的 SetOn 集合与 ACM 指令）。
🔴 **纪律（照抄用户条款）**：**禁止以"契约未列 BST"代替可达性证明**；**反向同样成立 —— 契约列了某继电器也不等于可达性成立**；可达性**只能由电路路径证明**，不能被登记表替代。故本附录**不引契约作为证明**（契约只作旁证，见 H.4）。

### H.2 可达性证明（逐跳；起点＝ACM200 S5 源）

| 跳 | 元件/触点 | 状态依据 | 结果 | locator |
| --- | --- | --- | --- | --- |
| 0 | `SW12_U1REF_BST_ACM`（ACM200 S5 通道，脚 `S5_ACM200_FH18`/`SH18`） | 源 | 5 V 出现在 S5 通道脚 | `StdAfx.h:69`；`Pin_Channel_define.h:20` |
| 1 | 源脚与 **`K110_BST_S1.6`（COM2）/`.3`（COM1）**、`K109_BUSL_PB0_S1.4`/`.5` **同一 net** | 网表 net 成员 | 源**直接落在 `K110` 公共端**（中间无器件） | `Dali-SCH.csv` nets `NetK109_BUSL_PB0_S1_4` / `_5`；IR `accepted_path_proofs[S5_ACM200_FH18->PB0_F_S1].path[0].from_net` |
| 2 | `K110` 是否动作 | **payload 的实际指令**：TM601 的 SetOn **不含 `K110`**（不含 `K109`）⇒ `K110` 停在**复位态** | 复位态触点：**`6-7` 通、`2-3` 通**（`4-5`/`3-4` 断） | 端子表 `relays.md:25`（`6=COM2`）、`:29`（"默认 2-3 通、6-7 通"）、`:31`（磁保持：NO 脚默认闭合）；payload 现盘 **39,457 B / `2d0984d9…` @19:55:59**，TM601 块（L355+）内 `SW12_U1REF_BST_ACM` **命中 0** |
| 3 | `K110` pin7（NO）与 pin2（NO）所接 net | 网表 net 成员 | `NetK110_BST_S1_7` = **`PB0_F_S1`**、`PWM1_F_S1`、`S24_P10`、`K147_PB0_OSC_S1.2`、`R_PB0_S1.1`、`TP_PB0_F_S1.1`；`NetK110_BST_S1_2` = **`PB0_S_S1`**、`PWM1_S_S1`、`TP_PB0_S_S1.1` | `Dali-SCH.csv` 上述两 net；IR 同上 path 的 `to_net` |
| 4 | **BST 侧需要什么** | 网表 + 端子表 | `BST_F_S1` 在 `NetK57_CAP_BST_SW_S1S2_3`（与 `K110.5`/`NC` 同 net）；`BST_S_S1` 在 `NetK76_ACM_BST_S1_4`（与 `K110.4`/`NC` 同 net）⇒ **只有 `K110` 处于置位态（`6-5`/`3-4` 通）时，源才到 BST** | `Dali-SCH.csv` 两 net；`relays.md:23/24/29` |
| 5 | IR 的独立复算 | IR 路径表 | `S5_ACM200_FH18 -> BST_F_S1` **`required_on=[110]`**、path 仅 `K110(ON,6→5)`；`S5_ACM200_SH18 -> BST_S_S1` **`required_on=[110]`**；而 `S5_ACM200_FH18 -> PB0_F_S1` **`required_on=[]`**、path `K110(NC,6→7)` | `path_proofs.json.txt` 对应条目 |

> **可达性结论（唯一、由电路路径得出，不依赖任何登记表）**：
> **在 TM601 的闭合集合下（不闭 `K110`）不存在 `S5_ACM200_*` → `BST_F`/`BST_S` 的电气路径；该源经 `K110` 的复位触点到达 `PB0_F_S1`/`PB0_S_S1`（及 `PWM1_*`）。**
> 若要到达 BST，**唯一充分必要条件是 `K110` 置位**（`6-5`/`3-4` 通）；**`K109` 无论开闭都不改变 ACM 源→BST 的可达性**（它不在该 net 链上：其公共端在 `FPVIe1_FL/SL_BUS_S1`，见网表 `K109.3/.6`）。

### H.3 PB0 误驱动：**首要独立风险项**（条款 ②，并分级）

**FACT**（IR/网表/端子表/派生表原文）：`SCH-Connect-Map.txt:724/725` = `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` / `SH18 -> … -> PB0_S`；`SCH:723` = `PB0_PWM1 [Kelvin] 需闭合: 无(默认导通)`；网表 `NetK110_BST_S1_7`/`_2` 的成员含 **`PB0_F_S1`/`PB0_S_S1`（`MemberType = PORT`，即 DUT 引脚）**、`PWM1_F_S1`/`PWM1_S_S1`（同 PORT）、`S24_P10`、`K147_PB0_OSC_S1.2`、`R_PB0_S1.1/.2`、`TP_PB0_F/S_S1.1`、`TP_PWM1_F/S_S1.1`；`PB0` 在 `PB0_PWM1` net 上**默认导通**（无需闭合任何继电器）。
**INFERENCE**（由 FACT 推出）：**若**该 `Set(FV, 5, …)` 真驱动 ACM18 源且 `K110` 未动作，**该 5 V 将出现在 DUT 引脚 `PB0_F_S1`/`PB0_S_S1` 及其同网节点（`PWM1_*`、`K147_PB0_OSC`、`S24_P10`、`R_PB0`、测试点）上** ⇒ 后果**不止"BST 未被驱动"**，而是**对 DUT 的 PB0/PWM1 侧施加非预期偏置**，并可能经 `K147_PB0_OSC`（OSC 路径）与测试点影响**其它测量或条目**。
**分级（我的建议，供 Captain 裁定）**：**阻塞级（blocking）** —— 理由：受影响的 net 含 **DUT 引脚（PORT）** 与 **OSC 相关元件**，且**当前无法由导出判定**该 5 V 是否被其它源主导/是否处于悬空（见 UNKNOWN）；在判定闭合前**不得**把含该驱动的 payload 视为电学正确而落盘（与用户裁定一致）。
**UNKNOWN**（须机台/夹具证据，**不得写成已成事实的电性结论**）：① 两 net 在 TM601 期间**是否另有源驱动或处于悬空/高阻**；② PB0/PWM1 在正常流程中是否本就被偏置（及 DFT 是否对其有跨条目约束）；③ 该偏置在**实际测量回路**上的后果与量级；④ **本 run 未做任何机台/硬件实测**。

### H.4 契约登记只作旁证（明确其地位，回应条款 ①）

`tmDeltas.TM601` 的 `aliasesUsed=["sw2pgnd"]`、`relaySet` 无 109/110、`scopePins` 无 BST、`pinRouteTable` 无 BST 键 —— 这些**与 H.2 的可达性结论一致**，但**在本项中仅作旁证，不作为证明**；反之，契约**若**将来登记 BST/K110，也**必须重新做 H.2 的可达性复算**才成立。

### H.5 两分支的可执行处置（条款 ④）

- **(B)（本判定采用）不需 `K109`/`K110` 或其它继电器**：
  - **替代路径（把 TM601 的激励送到目标节点）**：`S1_FPVIe_FL0 → K89(NC) → K60(ON) → K61(ON) → SW_F_S1`（IR `required_on=[60,61]`）；`S1_FPVIe_SL0 → … → SW_S_S1`（`[60,61]`）；PGND 经 `S1_FPVIe_FH0/SH0 → … → [154,155] → PGND_F/S_S1`。与 payload 现盘 TM601 的 SetOn（`K154,K155,K60,K61,K13,K85,K57,K126`）**逐项吻合**。
  - **为何 `:724/725` 不构成反证**：该两行**描述的是同一只继电器的复位触点去向**（`K110` 停在复位 ⇒ 源→PB0），**与 H.2 的结论同向**；把它们读成"源能到 BST"会同时与端子表触点语义（`:25/:29`）和 IR `required_on=[110]` 相矛盾。
- **(A) 若 Captain 改判需要（备而不采）**：契约侧（`tmDeltas.TM601` 增 BST 节点/路线与 `needsClosed`、`aliasesUsed`/`usedByTm` 登记 + 分列字段）＋计划侧（TM601 stimulus/measure 行）＋payload 侧（TM601 SetOn 增 `K110_ACM18_BST`；`K109` 按其路线归属决定）**三侧最小修法**，并**须重审**：t40（可达性）、t30（门禁断言集合）、t24/t32/t33（实现与门禁/编译证据）**全部按新字节重跑**。
- **悬空驱动应"移除"还是"补齐通路"**：
  - **推荐＝移除**。**判据**：① 目标节点（BST）**在 TM601 下无任何测量引用**（`measurePlan` = `MV SW-PGND` / `MI PMID_SW`；DFT/OVERVIEW 判据为 SW−PGND 的 7.5 mΩ）；② 保留即**持续存在 H.3 的 PB0 偏置风险**（移除是**最小且唯一**的消除手段）；③ 补齐通路（加 `K110`）会**新引入**一条与 TM601 无关的 BST 激励，须连带改契约/计划并重审三处，收益为零。
  - **补齐通路仅在一种情形成立**：若 Captain 判定该 5 V 是 TM601 的**必需**激励（例如用于 BST 参照的差分/漏电判据）—— 而**现有四方证据与 DFT/OVERVIEW 均不支持**。

### H.6 payload 引用纪律（条款 ⑥）

现盘 `implementation-payload-TM600-TM601.cpp` = **39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` @19:55:59**；**内容键实测**（本附录落笔时复算）：`t29 PER-FUNCTION JUSTIFICATION` ×1（L393）、`K109_BUSL1_PB0` ×2、`K110_ACM18_BST` ×2、`SW12_U1REF_BST_ACM` ×12、`TM600_HS_RDSON` ×2、`TM601_LS_RDSON` ×2，且 **TM601 块（L355+）内 `SW12_U1REF_BST_ACM` 命中 0**。
⇒ **引用一律"现算哈希 + 内容键"**，不得用单一旧哈希（38,147/`272667f3…` 为已取代的过渡态，且**正是含该悬空驱动的那一版**）。


---

## 附录 J（captain 三问逐条收敛，v1.3）— **独立判定**（不采信 t38 结论，仅以四方证据为准）

### J.1 三问之一：是否有任何来源**要求** TM601 驱动 BST？（四方逐一表态）

| 来源 | 读数（locator） | 表态 |
| --- | --- | --- |
| **DFT 意图** | `DFT.csv` 的 **TM601 行（csv row 20 / 文件 L98 起）**：stimuli = `vset[vbat,4.2,100e-6,0]` + `vset[pmid,9,100e-6,0]` + `vset[vdrv,5,100e-6,0]`；current = `iset[sw2pgnd,1,1e-6,0]`；measure = `PGND-SW` ⇒ **该行内 `bst2sw` 0 次**（对照：**TM600 行 csv row 19** 明确含 **`vset[bst2sw,5,1e-3,0]`** + `iset[pmid2sw,1,1e-3,0]`、measure `PMID-SW`） | **不要求** |
| **契约 rev 24** | `tmDeltas.TM601.aliasesUsed=["sw2pgnd"]`；`scopePins` 无 BST；`pinRouteTable` 无 BST 键；`relaySet` 无 109/110；`aliasResolution[bst2sw].usedByTm=["TM600 …","TM1205 …"]`（**不含 TM601**） | **不要求** |
| **IR 路径表** | IR 为**路线级**（非 TM 级）：`S5_ACM200_FH18/SH18 -> BST_F/S` = **`required_on=[110]`**；`S1_FPVIe_FL0/SL0 -> SW` = `[60,61]`、`-> PGND` = `[154,155]`。**IR 中不存在任何"TM601 → BST"的登记** | **未登记**（且无 TM601 专属 BST 路径） |
| **网表 + 端子表** | ACM200 S5 脚与 `K110.COM2/COM1` 同 net；`BST_F/BST_S` 接 `K110.5/.4`（NC 侧）⇒ **只有 `K110` 置位才可达 BST**；`K109` 公共端在 `FPVIe1_FL/SL_BUS_S1`，与该链无关 | **不要求**（且在该闭合集合下**不可达**） |

⇒ **四方一致：无任何来源要求 TM601 驱动 BST**；该驱动是**未登记的悬空激励**（并造成 J.3 的风险）。

### J.2 三问之二：**移除驱动是否正确**？

**我的独立结论：正确 —— "本不该驱动"**。判据（按强度）：
1. **DFT 意图层**：TM601 的判据是 **PGND–SW** 的 R_DSON（`iset[sw2pgnd]`、measure `PGND-SW`、limits 7.5 mΩ），**BST 不参与**；
2. **可达性层**：不闭 `K110` ⇒ 源落到 `PB0_F_S1`/`PB0_S_S1`（DUT 引脚），**不可能到 BST**（附录 H.2 逐跳证明）；
3. **风险层**：该驱动会**持续**对 DUT 的 PB0/PWM1 侧施加 5 V（附录 H.3，分级 blocking）；
4. **纪律层**：`t29`/`t23` 的 "minimal-endpoint" 原则 —— **不得驱动/闭合契约未授权件**。
⇒ **若保留**，唯一成立的路径是"DFT/契约新声明 TM601 需要 BST 参照"——**四方证据均不支持**；故**不保留**。**移除不改变 TM601 的任何测量能力**（其 SW 强制与 PGND 回路完整：附录 H.5-(B)）。

### J.3 三问之三：**契约 rev 25 是否仍有事项**？（三条登记待办逐条核）

| # | 待办 | 我实测的现盘状态 | 结论 |
| --- | --- | --- | --- |
| a | `TM600.aliasesUsed += bst2sw` | **`tmDeltas.TM600.aliasesUsed = ["pmid2sw"]`** —— **未含 `bst2sw`**，而 TM600 的 DFT 行明确 `vset[bst2sw,5,1e-3,0]`，且 `aliasResolution[bst2sw].usedByTm` 已列 TM600 ⇒ **两处登记不一致** | **成立，需在 rev 25 补** |
| b | TM1205 是否应从 `bst2sw.usedByTm` 移出并为 BST1-SW1/BST2-SW2 建独立别名 | **`tmDeltas.TM1205.aliasesUsed = []`（空）** 而 `bst2sw.usedByTm` 仍列 TM1205；且 IR 中 **16 条以 `BST1_*`/`BST2_*` 为端点的 accepted path，无一条 `required_on` 含 `110`**（`S1_FPVIe_FL0->BST1_F_S1=[41]`、`->BST2_F_S1=[41,43]`、**`S5_ACM200_FH4->BST1_F_S1=[]`**、`->BST2_F_S1=[43]` 等） | **成立**：应移出 `bst2sw`，并为 BST1/BST2 建独立别名/路线条目（否则 t30 按 `usedByTm` 索引会误纳 TM1205） |
| c | `aliasesUsed` 补齐（完整性） | 实测：`TM600=["pmid2sw"]`（缺 bst2sw）、**`TM1205=[]`**、`TM601=["sw2pgnd"]`（与实际使用一致）、`sw2pgnd.usedByTm=["TM601"]`（一致）；其余 TM 的别名仅 `vbat/pmid/vdrv/vbus/vac*/vdm` 一类"电压域"条目（无闭合集） | **成立**：rev 25 应做一次 `aliasesUsed ↔ usedByTm` **双向一致性核对并补齐** |
| d | **TM601 是否需要增 BST 需求** | —— | **不需要**（J.1）：rev 25 应**显式登记"TM601 无 BST 节点/路线；不采用 ACM200 BST 驱动"**，以免后人再引入悬空驱动 |

### J.4 对实现者"机制精化"的独立判定与**我方措辞**（captain ③）

**端子表原文**（`knowledge/hardware/relays.md`）：L21 `| 2 | NO | **↔ COM1(3)** | 断开 |`；L26 `| 7 | NO | **↔ COM2(6)** | 断开 |`；L23/L24 `| 4/5 | NC | 断开 | **↔ COM1(3)/COM2(6)** |`；L29 口诀 **"默认 2-3 通、6-7 通；通电 3-4 通、6-5 通"**；L31 ⚠️ **"磁保持继电器：标注 NO 的脚在默认无电时闭合，NC 脚在通电后才闭合。与普通弹簧继电器直觉相反！"**

**我方措辞（与实现者一致，并明确否定"常闭触点"读法）**：
> 派生连接图里的 **`K110(Relay-NC)` 表示"该继电器未动作（未通电）时的路径"**，**不是"常闭触点"**：G6K-2G-Y 是**磁保持 DPDT**，**未通电时导通的是标 `NO` 的脚（`2-3`、`6-7`）**，通电后导通的是标 `NC` 的脚（`3-4`、`6-5`）。故 `K110(Relay-NC) -> PB0` 的正确读法是"**K110 未动作 ⇒ 源落 PB0**"；`:43/:44` 的 `K110(Relay-ON) -> BST` 是"**K110 动作 ⇒ 源到 BST**"。**术语层面建议**：把连接图/契约中此类写法统一为 **`K110(un-actuated)` / `K110(actuated)`**，避免"NC/NO"被误读为触点类型。

**负列表（`K87/K88/K89` 等默认导通件）的规则措辞（我方）**：
> **应为"不得加入 required-on（需闭合/SetOn）集合、且不得驱动其动作"**，**而不是"强制断开"** —— 因为这类脚在**未通电时本就导通**，"断开"不是可通过 SetOn 列表达成的状态；把它们列入 required-on 只会**误增大电流/误接通路**。⇒ 规则：**默认导通件一律不进 required-on；若某路线必须断开它们，须显式记录其"动作"状态并单独论证。**


---

## 附录 K（**勘误**，v1.4）— `SW12_U1REF_BST_ACM` 的通道归属已由 `t42`/`t44` 独立判定为 **channel 5** ⇒ 本文件 §1/H.2 中"ACM↔BST 由 K110 完成"的前提**作废**

### K.1 独立判定结果（第三方任务，非本文件作者）

- **`t42`（schematic-expert，requirements，verdict=pass）** 唯一结论：**`SW12_U1REF_BST_ACM` 驱动 ACM200 `channel 5`（宏 `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,…"`），不是 `channel 18`**；到 BST 的必需继电器集合 = **`[48,76]`**；**`K110` 非必需**（`K110_ACM18_BST` 属 **`PB0_BST_ACM` = ch18**，是**另一个仪器对象**）。**修复后 BST–SW 闭集 = `[48,60,61,76]`**（SW 端 `S5_ACM200_FH8/SH8 -> K61_ACM8_SW`）。
- **`t44` 补遗**（`t44-t42-addendum.md` = 16,257 B / `30aa1be601c058152688aa6d3def9e53e159898c7dce3a2035f9c0230f687a79`）：`K_BST_ACM = 48,76` 是**唯一** ACM200→BST 复合宏；含 5/5 控制组与 ch5/ch18 决定性分离。

### K.2 本文件中**作废**的内容（逐条）

| 位置 | 原表述 | 状态 |
| --- | --- | --- |
| §1 结论 | "到 BST 必须 `K110` 置位"、"该路径唯一的开关是 `K110_BST_S1`" | **作废**（那是 ch18 路线）；正确：本案仪器 **ch5 ⇒ `[48,76]`** |
| §2 逐步路径 | ACM S5 脚同 net 即 `K110.COM2` ⇒ 结论"未激磁落 PB0" | **对 ch18 成立**；对 **ch5** 需重走：`S5_ACM200_FH5 -> K48(ON) -> K76(ON) -> BST_F`（`SCH:672-674`；IR `required_on=[48,76]`） |
| §H.2 可达性证明 | 同上（以 `K110` 为唯一开关） | **作废**，改以 ch5 逐跳重证（并列 §K.3） |
| §1 分支 (B) "不需 K110" | 结论方向**仍然正确**（TM601 不需要该驱动） | **保留**，但理由改为：**TM601 的闭合集合既不含 ch5 的 `K48/K76`，也不含 ch18 的 `K110`** ⇒ 两条路线都到不了 BST |
| §5 / H.3 PB0 风险 | "5 V 落到 PB0/PWM1（DUT 引脚）" | **保留但限定**：该风险属**驱动 ch18 时**的行为（`:724/725` 是 ch18 表）；**TM601 当时驱动的仪器实例是哪个通道，须由 `t42` 口径复核** ⇒ 列为 UNKNOWN-K1（见 K.5） |

### K.3 以 ch5 口径重证的逐步路径（替代 §H.2）

| 跳 | 依据 |
| --- | --- |
| 0 | `SW12_U1REF_BST_ACM` = ACM200 **ch5**（`Pin_Channel_define.h:20`：`S5_5,…,S28_5`） |
| 1 | `S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F`；`SH5 -> … -> BST_S`（`SCH-Connect-Map.txt:673-674`，列组头 `:672` 需闭合 `K48,K76`） |
| 2 | IR：`S5_ACM200_FH5 -> BST_F_S1` **required_on=[48,76]**；`SH5 -> BST_S_S1` **[48,76]** |
| 3 | 目标树既有生产代码自证：`test.cpp` L6997/L7085 注释 **"BST ← SW12_U1REF_BST_ACM: K48_ACM5_AMP_REF + K76_ACM_BST (FH5→BST)"**，L7000/L7087 的 `SetOn(…, K48_ACM5_AMP_REF, K76_ACM_BST, …)` 与其一致 |
| 4 | 旁证：`SCH:775-779`（同 ch5 经 `K48(Relay-NC)` 到 SW1/SW2）⇒ ch5 是共享通道，K48 动作选 BST、复位选 SW1/SW2 |
⇒ **修正结论**：**AC 源要到达 BST，必须闭 `K48 + K76`**（SW 侧按既有实现为 `K61`）⇒ **BST–SW 闭集 = `[48,60,61,76]`**（v1.24 更正：此前写作 `[48,61,76]` **漏了 SW 侧 `K60`**）；**`K110` 属通道 18（`PB0_BST_ACM`）**、**`K109` 属 FPVIe[L]/QVM[L] 低域路线**（二者皆非本仪器 ch5 路线）。

### K.4 对 TM600/TM601 的连带影响（**待 `t43` 独立复核后再定稿**）

- **TM600**：payload（`2d0984d9…`）与部署态（`15c7d2b8…`）的 TM600 SetOn **均不含 `K48/K76`** ⇒ **裁定 (ii) 的 BST−SW 5 V 未接通**（blocker，待修）；`t29` 所补的 `K109/K110` 按 ch5 口径**接不通本案仪器**；**去留裁定（最终）**：`t43` 的并集/UNKNOWN 已被其作者撤回并**改判 ch5**，契约 rev 33 已收窄 ⇒ **`K109/K110` 移除**；现盘交付件（闭 `K48/K76`、无 `K109/K110`）**即合规版**；此前"保留"表述**作废**。
- **TM601**：本文件"移除驱动"的**结论不变**（两案皆到不了 BST），但**理由按 K.3 重写**；`t38` 的移除动作仍然正确。
- **契约**：`aliasResolution[bst2sw] = [110,61]`（我取的 ch18 行）**须按 ch5 口径更正**（rev 25 范围，含"按路线分组"与三条登记待办）；**契约现仍 rev 24 / `fd00a508…`，本附录不改契约。**

### K.5 新增 UNKNOWN（如实登记，不得写成已知）

- **UNKNOWN-K1**：TM601 当时驱动的那一次 `SW12_U1REF_BST_ACM.Set(FV,5,…)` 在**物理上**作用于哪个通道（ch5 是仪器对象定义；若该调用实例化的是 ch5，则其 PB0 风险与 §H.3 不同——ch5 未动作时经 `K48(NC)` 去 **SW1/SW2**，而非 PB0）。**需 `t43`/机台证据闭合。**
- **UNKNOWN-K2**：`K48/K76` 未闭合时 ch5 的实际落点（`SCH:672` 只给"需闭合"集合；未动作时去向须按 ch5 触点逐一核）。
- 本文件 §6（U1–U4）其余 UNKNOWN **继续有效**。


### G.3 机制更正（**待 `t43` 修订**）— ch5 未动作时改道 SW1/SW2，不是 PB0

> **本节为 captain 授权的一次定点更正（2026-09-16）：不修改上述任何既有段落；其内容与附录 K（勘误）一致，K 为详版，本节为可检索的定点标记。**

1. **更正**：本文件 §H.3 与 §5 中"未动作时 5 V 落在 **PB0/PWM1**（DUT 引脚）"的表述，**只对 `K110`/channel-18（`PB0_BST_ACM`）成立**。按 `t42`/`t44` 判定，`SW12_U1REF_BST_ACM` 实为 **ACM200 channel 5**；**其未动作时的去向是经 `K48(Relay-NC) -> K49 -> SW1_F/SW2_F`（`SCH-Connect-Map.txt:775/778`）**，**不是 PB0**。
2. **保留的部分**：`PB0` 路的物理事实（`:724/725`、网表 `NetK110_BST_S1_7`/`_2` 含 `PB0_F_S1`/`PB0_S_S1`＝DUT 引脚、`K147_PB0_OSC`、`S24_P10` 等）**仍然成立**，但**其主体是 ch18 的 `PB0_BST_ACM`**，与本案仪器的 ch5 无关。
3. **待裁定（不由你我单方定案）**：本机制更正与"TM601 当时那次 `Set` 物理上作用于哪个通道"（附录 K 的 UNKNOWN-K1）**一并交 `t43`（rule-reviewer 独立复核）裁定**；在 `t43` 出结论前，本节与 §H.2/§H.3/§5 的机制叙述**以"待 t43 修订"状态引用**。
4. **不受影响**：`t39` 的**处置结论**（TM601 无 BST 授权 ⇒ 移除悬空驱动；`t38` 已执行）**成立且已关闭**；`K48+K76`（ch5 ⇒ BST）与 `BST–SW 闭集 [48,60,61,76]` 的临时结论**待 `t43`**。


---

## 附录 L2（Captain 授权的**定点更正**，v1.6）— ch5 定案对 §1/§H.2/附录 J 的结论更正

> **K110 结论更正声明（v1.9）**：**`t39` 的“到 BST 必须 `K110` 置位”予以更正** —— 只对**通道 18（`PB0_BST_ACM`）**成立；**本案仪器（通道 5）⇒ BST `[48,76]`**，跨域闭集 **`[48,60,61,76]`**（SW 侧写全 `K60`+`K61`）。**TM601 侧结论不变**：其 `SetOn` 中 `K48/K76` 与 `K109/K110` 四者皆无 ⇒ **两读法下都到不了 BST ⇒ 移除正确**。

> **结论行（v1.8，Captain 采信 addendum 后定点更新）**：`t43` **终局 = ch5**（并集撤回）⇒ 本附录的“ch5 路径”表述为现行口径；**`K109/K110` 归 ch18、本项不闭**；TM601 侧结论不变（其 `SetOn` 中 `K48/K76` 与 `109/110` 四者皆无 ⇒ **两读法下都到不了 BST ⇒ 移除正确**，不依赖引脚归属裁定）。

**更正（指向既有段落正文，不再改动其内容）**：
1. **§1 结论** 中"到 BST 必须 `K110` 置位"**作废** ⇒ 本案仪器（ch5）**到 BST 需 `K48+K76`**（`SCH:672-674`；IR `required_on=[48,76]`；目标树生产代码 `:7000/:7087/:7170/:7513` 自证）；`K110` 属 **ch18/`PB0_BST_ACM`**。
2. **§H.2 达性证明** 的"唯一开关＝`K110`"**作废**；ch5 口径下的逐步路径见 **附录 K.3**（`S5_ACM200_FH5 -> K48(ON) -> K76(ON) -> BST_F/S`）。
3. **附录 J.1 的四方表态表**：DFT 行（TM601 无 `bst2sw`）、契约（TM601 无 BST 节点/`relaySet` 无 109/110）、IR（无 TM601→BST 登记）**三行结论不变**；**"网表+端子表"那一行须更正为**：*"本案仪器走 ch5 ⇒ 到 BST 需 `[48,76]`；`K109/K110` 属 ch18 ⇒ 两路线下 TM601 都到不了 BST"* ⇒ **J.2 的处置结论（移除悬空驱动）不变**。
4. **附录 J.3 的 (b) 句（契约字面要求 K109 ⇒ 依约保守）**：**保留为历史记录并加限定** —— *"仅在 rev 24 的 `bst2sw` 映射下成立；rev 25 更正后不再适用"*。
5. **附录 G.3/附录 K 的机制更正**（ch5 未动作 ⇒ 经 `K48(NC)->K49->SW1/SW2`，非 PB0）**维持**，并与 `t42`/`t44` **一致**；`UNKNOWN-K1`（TM601 那次 `Set` 实际作用于哪个通道）**由 `t43` 裁定**。
**更正后本文件再次冻结**（台账记录该"事实性错误"例外）。
