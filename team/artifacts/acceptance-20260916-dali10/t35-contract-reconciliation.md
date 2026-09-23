# t35 — 契约归口：t29 上报的三处不一致（带证 + 两路径对比 + 推荐）

> ## ⚠️ 现盘 payload 更正横幅（v1.25，事实性更正；单点插入、不改既有正文）
> **现盘交付件 = 43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24（566 行）**，TM600 SetOn = `[13,48,57,60,61,76,83,85,126]`（**含 `K48/K76`、可执行 `K109/K110` = 0**）；**canonical 已由 Captain 定格为该字节、写入已停**。
> 本文件内所有把 **`39,457 B / 2d0984d992d5d8cb…`**（或 `38,147/272667f3…`、`36,381/73b511b7…`、`35,014/444810dd…`）写作"**现盘**"的表述，**均指 2026-09-16 21:09:24 之前的时点、属历史**；同一路径在 20:45–21:09 被**就地覆盖四次**、**从未有副本**，故旧值全树 0 命中是**正确结果**。引用一律以**现算**为准。

- Author / contract owner: **setup-architect**（本任务 t35）
- Independent review: **rule-reviewer**（作者不得自审）
- Decision owner for path A/B: **Captain**
- Anchor of the artefact under discussion: `setup-contract.json` = **rev 24 / 328,805 B / `fd00a5082170293fcea29446c009fc432977d61a8f624ef17ac1c82f41515a18`**（冻结）
- Companion evidence: `t29-k110-evidence.md`（ate-implementer，10,062 B）+ 本文件第 0 节的复算 locator

---

## 0. Evidence base（全部只读复算，locator 逐条给出）

| # | 事实 | locator |
| --- | --- | --- |
| E1 | `aliasResolution[3]`（bst2sw）`resolution.relayChain` = `K110_ACM18_BST`（"SetOn (ACM200 S5_FH18 -> BST)"）+ `K61_ACM8_SW`；`closedRelayNumbers = [110, 61]` | 契约 rev 24 `/aliasResolution[3]/resolution` |
| E2 | `tmDeltas.TM600.relaySet` **含 109 与 110** | 同上 `/tmDeltas/TM600/relaySet` |
| E3 | `tmDeltas.TM600.pinRouteTable` BST 行 `…CH0 Low` 的 `needsClosed = [109,110,138,139,145,146]` | 同上 `/tmDeltas/TM600/pinRouteTable` |
| E4 | `terminalAssignment.high = "BST"`、`nodeOnHighTerminal = "BST"`、`nodeOnLowTerminal = "SW (SW12_U1REF_BST_ACM is ground-referenced…)"` | 同上 `/aliasResolution[3]/resolution/terminalAssignment` |
| E5 | `CH0 Low -> BST  [Kelvin]  需闭合: K109,K110,K138,K139,K145,K146`；`… K109(Relay-ON) -> K110(Relay-ON) -> BST_F` | `project/DALI/SCH-Connect-Map.txt:42-44` |
| E6 | `PB0_PWM1 [Kelvin] 需闭合: 无(默认导通)`；`F: S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`；`S: S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S` ⇒ **K110 双掷**：未激磁时 ACM18 落在 **PB0**，激磁后才到 BST | `SCH-Connect-Map.txt:723-725`（对照 `:109-110`） |
| E7 | `CH0 High -> BST  [Kelvin]  需闭合: K46,K48,K76`（另一条到 BST 的路线，本 run **未采用**） | `SCH-Connect-Map.txt:39-41` |
| E8 | `CH1 Low -> BST 需闭合: K109,K110`（FPVIe CH1 框架下的 BST 走法） | `SCH-Connect-Map.txt:268-270` |
| E9 | 部署态 `test.cpp`：`K109`/`K110` **全文件命中 0 次**（落盘前状态）。**payload 版本序列（全部实测）**：`35,014 B / 444810dd…` → `36,381 B / 73b511b7…`（t29）→ `38,147 B / 272667f3…`（t29 最终、含 K109/K110；**rule-reviewer 的 t29 verdict 针对此版**）→ **`39,457 B / 2d0984d992d5d8cb11868660b29cb…`（t38 移除 TM601 悬空 ACM 驱动，**现盘**）**。⇒ 前三者为**已取代的过渡态、无副本**；canonical 由 Captain 定性，等 Captain REPLACE（请以 **39,457** 版为交付件） | `t29-k110-evidence.md` + 本人只读复算 |
| E10 | `verify_bst_sw_sequence.py` 对 `K110`/`K109`/`needsClosed`/`relaySet` **命中 0** ⇒ 门禁盲区（t30 负责加断言） | `scripts/verify_bst_sw_sequence.py` |
| E11 | **未找到**"夹具已把 `SW12_U1REF_BST_ACM` 硬连到 BST"的证据；`_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,S6_5,S11_5,S12_5,S21_5,S22_5,S27_5,S28_5"` 是 **ACM 自身通道脚**、不是 BST 网 | `Pin_Channel_define.h:20`、`StdAfx.h:69` |

**定级纪律（必须照写，不得升级）**：E11 的结论是"**无证据支持夹具硬连**"，**不是**"已证伪夹具硬连"。任何报告不得写成"已排除"，只能写"未发现支持证据；若日后出现夹具侧证据，本归口需重开"。

---

## 1. 不一致 ①：`closedRelayNumbers` 与路线表口径不一致（漏 `K109`）

- **现象**：`aliasResolution[3].closedRelayNumbers = [110, 61]`（E1），但同一 TM 的 `relaySet` 含 109（E2）、`pinRouteTable` 的 `CH0 Low -> BST` 需要 `[109,110,138,139,145,146]`（E3），连接图 `:42-44` 亦如此（E5）。
- **性质判定（带证）**：这不是"数值冲突"，而是**未标注的窄化**：`[110,61]` 是**ACM200 通道脚路线**的闭合集（E6：ACM18 脚经 K110 到 BST、SW 经 K61），而 `[109,…]` 那一串属 **FPVIe CH0-Low 路线**（E5/E8）——两条路线共用 K110 这个双掷节点。
  ⚠️ **本行已被附录 E/F 取代（同文件内以此为准）**：**`K109` 不属 ACM 脚路线**（端子表 `relays.md:3-31` + IR `required_on=[110]`，见 E.1/F.1）；**契约字面仍要求 K109**（`relaySet∋109` 且 `pinRouteTable…CH0 Low.needsClosed∋109`）⇒ **t29 闭 `K109`+`K110` 属「依约保守」、合规**。（原表述「必要性未独立确立」作废。）另：**K110 是 ACM 路线的摆动器**；**K109 另有自己的两对极点**，两者**不是共用同一双掷**、只在同一 net 相接（E.2 更正）。
- **风险**：下游（含 t34 报告、t30 断言）会把 `[110,61]` 当"全部所需"，或把 `[109,…]` 当"ACM 路线所需"，两种读法都能被引到。
- **归口建议（最小、纯增量）**：保留现有 `closedRelayNumbers` 不动，**新增** `closedRelayNumbersByRoute`：
  `{"ACM200_SW12_U1REF_BST_ACM": [110, 61], "FPVIe_CH0_Low_to_BST": [109,110,138,139,145,146], "connectMap_L42_L43": [109,110,138,139,145,146]}`，并加一句 `k109RoleOnAcmRoute`：**"not independently established; the approved payload closes it conservatively"**。

## 2. 不一致 ②：端子归属未确立（FPVIe CH1 框架 vs ACM200 驱动）

- **现象**：`terminalAssignment.high = BST` / `nodeOnHighTerminal = BST`（E4）是 **FPVIe CH1** 的说法（`CH1 High -> BST`，E8），而裁定 (ii) 的 BST−SW 5 V 由 **ACM200 `SW12_U1REF_BST_ACM`**（接地参考 AC 源，E11）驱动。
- **性质判定**：**契约文本未确立 ACM 驱动下的端子/节点归属** ⇒ 后人可能据 `terminalAssignment` 误以为要用一对 FPVIe 通道（这正是 t29 的担忧）。
- **可确立的事实（带证）**：ACM200 的 S5 通道脚（`S5_ACM200_FH18/SH18`）**就是 K110 的公共端**（E6）；K110 未激磁→PB0，激磁→BST（E5/E6）；SW 侧由 `K61_ACM8_SW`（E1）落到 SW。⇒ **BST−SW 的差分 = ACM200 输出电平**，不是"一对力/感通道"的差。
- **归口建议（最小、纯增量）**：新增 `acmDriveFraming`：
  `{"instrument":"SW12_U1REF_BST_ACM (ACM200, ground-referenced)","channel":"S5_FH18/SH18","nodes":{"BST":"reached with K110 energised (ACM18 pin)","SW":"via K61_ACM8_SW"},"differential":"BST-SW equals the ACM output level; no FPVIe force/sense pair is in play for this rail","k109":"see closedRelayNumbersByRoute"}`
  并把 `terminalAssignment` 标注为 **legacy FPVIe framing, not applicable to the ruled ACM drive**（不删原文，避免抹掉溯源）。

## 3. 不一致 ③：未采用的 `CH0 High -> BST` 路线未标注

- **现象**：`:39-41` 存在 `CH0 High -> BST 需闭合: K46,K48,K76`（E7），契约内无任何"未采用"标注。
- **性质判定**：属裁定 (ii) 判定 **unrealisable** 的类（该路线依赖 FPVIe CH0-High 复合宏/桥接件，且 (ii) 已明确 `K_FPVIH_TO_BST_B` 那一类为 intended-but-unrealisable；K76/K46 亦不在本 run 采用集内）。
- **归口建议（最小、纯增量）**：新增 `unrealisableRoutes`：`[{"route":"FPVIe CH0 High -> BST","needsClosed":[46,48,76],"locator":"SCH-Connect-Map.txt:39-41","status":"NOT USED - unrealisable class per ruling (ii); annotated so no later reader re-implements it"}]`。

---

## 4. 两条路径：对比 + 推荐（用户纪律：给选择必须给对比与推荐）

| | **路径 A：改契约（rev 25，纯增量标注）** | **路径 B：登记性限制（不改契约）** |
| --- | --- | --- |
| 内容 | 生成器加 `closedRelayNumbersByRoute` / `acmDriveFraming` / `unrealisableRoutes` + 把 `terminalAssignment` 标为 legacy；重跑两次字节一致 → schema exit 0 → 刷 pin → 广播 **rev 25** | 不改契约；把三处写进本文件 + t34 的 `acceptance-report.json` 限制清单 |
| 优点 | 契约自洽：t34/t30 引用时无歧义；`terminalAssignment` 不再误导；③ 有显式"未采用"标注 | **零漂移**：保住 rev 24 锚定（t26 override、plan `inputArtifacts`、pin 全部不动）；无新一轮复核 |
| 缺点 | 新哈希 ⇒ pin 刷新、plan `inputArtifacts` 记录漂移（需按 `hashPolicy` 说明）、t26 override 引用的 rev 24 与 t34 引用的 rev 25 并存需写清；多一轮独立复核 | 契约内**留着**未标注的窄化与 FPVIe 框架端子表 —— 正是 t29 担心的"后人误用"路径；t30 的断言若按契约取集合，会持续面对歧义 |
| 成本 | 1 次生成器改动 + 2 次重跑 + schema + pin + 广播 + 1 轮复核 | 0 次写入；只写文档 |
| 可逆性 | 高（纯增量标注可再撤回，但会产生更多版本） | 高（随时可改走 A） |

**推荐：路径 A（纯增量标注），但执行前置＝rule-reviewer 复核 + Captain 一句 GO。**
判据：① 三处都属于"**契约文本内部不自洽/不自明**"，而 t34 必须以契约为权威引用；把歧义留给报告，等于把风险转嫁给验收；② 修法是**纯增量**（不改任何既有数值、不删原文），语义风险≈0；③ 与"不采纳把 [61] 改小"的裁定**不冲突**——A 保留 `[110,61]` 原值并只补路线标注。
**若 Captain 选择 B**：本文件即为其限制登记（三处 + locator + E11 定级），我会把它逐条抄进 t34 的 `acceptance-report.json`，并在报告中写明"契约存在未标注窄化与 legacy 端子框架"。

---

## 5. 本任务状态

- 三处不一致**已逐条带 locator 归口**（第 1/2/3 节），两路径**已对比并给出推荐**（第 4 节）。
- **路径 A 的契约改动尚未执行**：按 acc4/acc5，需 rule-reviewer 复核 + Captain 决策；执行时我会走完整流程（改生成器 → 两次字节一致 → `validate_team_artifact.py setup-contract` exit 0 → 刷 `setup-contract-pin.json` → 广播 rev 25）。
- **当前默认按路径 B 登记**（零漂移），直至收到 GO。
- 边界：本文件未改 `test.cpp`/payload/计划/门禁脚本；`devel` 零写入；`setup-contract.json` 仍为 rev 24 / `fd00a508…`（未动）。

---

## 附录 A（captain 裁定后追加，v1.1）— locator 分歧一次性解法 + 两条处置确认

### A.1 locator 不是"不同产物"，是**同一文件里的两条不同路线**（并列登记，不再查第二文件）

`project/DALI/SCH-Connect-Map.txt`（同一路径，全量扫描，四行同时存在）：

| locator | 路线 | 含义 |
| --- | --- | --- |
| **L42 / L43 / L44** | `CH0 Low -> BST [Kelvin] 需闭合: K109,K110,K138,K139,K145,K146`；`… K109(Relay-ON) -> K110(Relay-ON) -> BST_F/S` | **到 BST 的需闭合串**（K110 必须激磁） |
| **L724 / L725** | `F: S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`；`S: S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S` | **决定性 locator**：ACM200（`SW12_U1REF_BST_ACM`）仪器侧经 K110 的 NC 触点到 **PB0** —— 不闭 K110 时 AC 源**到不了 BST** |
| **L109 / L110** | `S1_FPVIe_FL0/SL0 -> … -> K109(Relay-ON) -> K110(Relay-NC) -> PB0_F/S` | **FPVIe0（CH0 FL0/SL0）** 侧经 `K109` 后由 K110 落 PB0（另一条路线，同为真） |

契约侧并列 locator（`setup-contract.json`，rev 24）：
- **L145** `"BST": "S5_ACM200_FH18/SH18 (K110_BST)"` —— **契约内已部分承载 ACM200 框架**（附录 A.3 据此降低了 ② 的改动量）
- **L1440** `"relay": "K110_ACM18_BST"`
- **L1897** `"relayPath": "K110_ACM18_BST -> K61_ACM8_SW"`
- `aliasResolution[3].resolution.closedRelayNumbers = [110, 61]`

⇒ 两组（L42/43 与 L724/725、L109/110）**同文件、都真、用途不同**：前者是"需闭合/到 BST"，后两者是"未激磁时落 PB0"的两个来源侧。本文件此前的 locator 歧义**至此关闭**。

### A.2 两条处置由 captain 裁定、照准执行（无需再请示）

1. **`correction-8` 产物不再改动**（low）：`independentReview.note` 的陈旧版本串**保持不动**，改在**审计链** `ledgerDeltaNotInArtifact` + `carriedFindings` 挂号（先落 `snapshot-2` 再改写链文件，遵守自保规则 (ii)）。**不需要额外授权**。
2. **K110 维持"实现缺闭合"**：已确认**未找到夹具硬连证据**，且查到的证据方向相反（ACM 仪器侧经 K110 NC 落 PB0）。**"无证据 ≠ 已证伪"不得被用作翻转依据** —— 若日后出现夹具侧证据，**本归口重开**，但在此之前结论不动。

### A.3 对 ② 的建议范围（据 A.1 的 L145 收窄）

契约 L145 已写 `"BST": "S5_ACM200_FH18/SH18 (K110_BST)"` ⇒ ② 所需的并非"从零确立"，而是**把 `terminalAssignment` 的 FPVIe 框架标注为 legacy + 补一句 ACM 差分语义**（"BST−SW equals the ACM output level"）。改动量因此更小，**路径 A 的成本相应下降**（仍建议等 rule-reviewer 复核 + captain GO 再执行）。

---

## 附录 B（rule-reviewer 复核后追加，v1.2）— 路线归属之争不改变 payload 正确性 + 归口新增两项

### B.1 K109/K110 的"路线归属"不影响结论（复核方结论，我复核接受）

- 若 **K109+K110 都属 CH0-Low 路线**（`SCH:43/44` 的串行链正是 `… K138/K139 … K109(ON) → K110(ON) → BST_F/S`）⇒ 要 BST 到位**两者都必须闭** ⇒ payload 闭两者**正确**；
- 若 **K109 属别的路线** ⇒ 契约 `pinRouteTable.BST["…CH0 Low"].needsClosed = [109,110,138,139,145,146]` **已把 K109 列为该路径必需** ⇒ payload **仍符合契约权威集合**。
⇒ ⚠️ **本节结论已被附录 F.2 取代（以此为准）**：**K110 必需且充分；`K109` 不是 ACM 基线路径所需**
> **⚠️ 追加 v1.21 限定**：该句的"必需且充分"**只对 ch18 腿成立**；**本仪器（`SW12_U1REF_BST_ACM`，ch5）→ BST 需 `[48,76]`**（见 §L / §L.3）。（IR `S5_ACM200_FH18/SH18 -> BST` 的 `required_on=[110]`；含 109 的 21 条 accepted path 全属 S10/FPVIe/QVM 路线）。**t29 仍合规、verdict 仍 pass**，但理由改为「**契约字面要求 K109 ⇒ 依约保守**」，**不是**「两种读法都应闭」。本节上述「两种读法」的论述**作废**，仅作历史留痕。

### B.2 归口新增（captain 指定并入本任务）

- **①（增补）**：路径 A 应把 **K109 的附属关系**写进 `aliasResolution[3].resolution.relayChain`（或按 A.1 的 `closedRelayNumbersByRoute` 表达），使"契约文本"与 `pinRouteTable`/`relaySet` 同口径；路径 B 则须在限制清单写明"`relayChain` 未列 K109，权威集合以 `pinRouteTable.needsClosed` 为准"。
- **③（增补）TM601 无 BST 条目：确认为 by design（非缺失）**。TM601 的驱动对象是 **SW-PGND**（其 DFT 行为 `iset[sw2pgnd,…]`、sense SW-PGND），**不使用 BST−SW 5 V 差分**；契约内 TM601 无 `bst2sw` 类条目属**正确**，不需补。若后人误以为"两函数应有对称的 BST 条目"，以本条为准。
- **版本引用纪律（复核方实测提醒，我确认）**：引用审计链时**必须现算**——我此前公告的 9,855 B / `e92e1683…` 实为 `…snapshot-3.json` 的**内容**，链条当时即已推进；现盘链 = **12,997 B / `3e4cc4069a3086d190e20ca8c65dc18ae92c1dcfe957b2f2951cb913c84e7f55`**（且随后又追加过，见链内 `citationNote`）。**凡引用一律现算。**」

---

## 附录 C（rule-reviewer 复核后追加，v1.3）— 契约在 K109 上自相矛盾（本任务最实质一条）+ 链冻结

### C.1 新证据（我逐条复现）

| # | 证据 | 复现 |
| --- | --- | --- |
| C-E1 | `SCH-Connect-Map.txt` **L700-760（ACM200 S5 通道表邻域）**：`K109` 出现 **0 次**、`K110` **2 次**（L724/L725） | ✅ 我实测同值 |
| C-E2 | 全文件 `K109` 仅出现在 **L42/43/44、108/109/110、268/269/270、328/329/330、538/539、578/579**，**全部属 FPVIe / QVM 路线**，**无一条在 ACM 脚链上** | ✅ 我实测同清单 |
| C-E3 | `SCH` L723 `PB0_PWM1 … 需闭合: 无(默认导通)`；L724/725 `S5_ACM200_FH18/SH18 -> K110(Relay-NC) -> PB0_F/S` | ✅ |

⇒ **K109 不在 ACM 脚链上**；"ACM 脚路线只需 `K110`（+ SW 侧 `K61`）"成立。

### C.2 契约自相矛盾（本文件 ① 的升级定性）

| 字段 | 值 | 语汇 |
| --- | --- | --- |
| `aliasResolution[3].resolution.closedRelayNumbers` | **`[110, 61]`** | **ACM200** 口径（与 C-E1/C-E3 一致） |
| `aliasResolution[3].resolution.relayChain` | `K110_ACM18_BST`(SetOn, "ACM200 S5_FH18 -> BST") + `K61_ACM8_SW` | **ACM200** 口径 |
| `tmDeltas.TM600.pinRouteTable.BST["…CH0 Low"].needsClosed` | **`[109,110,138,139,145,146]`** | **FPVIe 实例**口径（与 `SCH` L43/L44 一致） |
| `tmDeltas.TM600.relaySet` | 含 `109`、`110` | 两套并集 |

⇒ **定性**：`[109,110,138,139,145,146]` 是 **FPVIe 实例路线**（`S1_FPVIe_FL0/SL0 → … → K109(ON) → K110(ON) → BST`）的闭合集合，**不是 ACM 脚路线的**；`pinRouteTable.BST` 的**命名/语义需消歧**，否则任何按它实现的 payload 都会**多闭 K109**。
**级别**：高于此前的"`closedRelayNumbers` 窄化未标注" —— 这不是措辞问题，而是**同一契约对同一问题给出相反答案**，会被 t30 的断言（契约集合 vs payload）与 t34 的报告同时引用。

### C.3 对 t29/复核结论的记账（不推翻 verdict）

- **t29 verdict 仍为 pass**：payload 满足契约**字面**权威集合（`K109`/`K110` 都在 `TM600.relaySet`，且 `pinRouteTable.BST CH0 Low needsClosed` 含二者）；
- **K109 的闭合理由现为"有争议、可能多余"**（按 C.1 证据，ACM 路线很可能只需 `K110`）；
- **处置建议（同意复核方）**：**现在不改 payload** —— 再动一次会**第四次移动哈希**并使刚落定的复核锚点失效，且 `K109` **不在任何负列表**、无副作用；**待 K109 归属在本文件裁定后，于下一次实质修订**把 K109 移出 TM600 的 SetOn（"最小端点"清理）**并同步更正 `pinRouteTable` 语义/命名**；
- **路径 A/B 因此更清晰**：**A（推荐）**= rev 25 纯增量：`closedRelayNumbersByRoute`（ACM `[110,61]` / FPVIe CH0-Low `[109,110,138,139,145,146]`）+ `acmDriveFraming` + `unrealisableRoutes` + **`pinRouteTable.BST` 消歧句**；**B** = 不改契约 ⇒ 必须把"`pinRouteTable.BST.needsClosed` 是 FPVIe 路线口径、ACM 路线只需 `[110,61]`"写进 t34 限制清单，并**提醒 t30 不要两套语汇混用**。

### C.4 审计链冻结（回应复核方"第三次同类漂移"）

- 复核方实测链 = **17,431 B / `f96ef93edcf9ba7bc0868158d9d804e4b1214cb6c19e817753cbd19c933096e2`**，与我现盘一致 ✅；其指出我早前公告的 `932f0613…`(11,785 B) **实为 `snapshot-4` 内容**（`snapshot-3` = 9,855 B / `e92e1683…` 与申报一致）——判断正确，映射已在链内 `citationNote`。
- **自本条起审计链冻结**：不再追加（除出现新事实，且必须先按自保规则 (ii) 落 `snapshot-<n>` 并在同一条消息给出**现算**哈希）。**引用一律现算**，不得引用历史公告值。
- 链内已含：`locatorAlignment`（双组 locator + 12 处完整性）、`fixtureHardwireAssumption`="无证据支持"、`gateGuardAssignment`=t30、以及"**不得把 K110 finding 误挂到契约或计划**"。


---

## 附录 D（网表级复核，v1.4）— **K109 与 K110 不在串联链上**；"ACM 路线必须双闭"不成立

**承上**：附录 C 引用的 `SCH-Connect-Map.txt` 是**派生表**（`project_config.json.intermediates.sch_connect_map`）；本节改以**权威网表** `project/DALI/Dali-SCH.csv`（307,157 B / `inputs.csv_schematic` "唯一权威 CSV 源"）逐行复核。**复核实测本文件全部 1,338 行。**

### D.1 网表原始行（`Dali-SCH.csv`，MemberName/NetName 原样）

| 继电器 | 引脚 | NetName | 同网其它成员 |
| --- | --- | --- | --- |
| K109 | 3 | `FPVIe1_FL_BUS_S1` | （FPVIe1 低总线侧） |
| K109 | 6 | `FPVIe1_SL_BUS_S1` | （FPVIe1 低总线侧） |
| K109 | **4** | `NetK109_BUSL_PB0_S1_4` | **K110.6**, **[PORT] S5_ACM200_FH18** |
| K109 | **5** | `NetK109_BUSL_PB0_S1_5` | **K110.3**, **[PORT] S5_ACM200_SH18** |
| K109 | 2 | `NetK109_BUSL_PB0_S1_2` | **仅 1 个成员（悬空）** |
| K109 | 7 | `NetK109_BUSL_PB0_S1_7` | **仅 1 个成员（悬空）** |
| K110 | **6 / 3** | 同上两个 net | 与 ACM 端口、K109.4/5 **同一个节点** |
| K110 | 5 | `NetK57_CAP_BST_SW_S1S2_3` | K57.3, K76.5, K134.4, R_BST.1, TP_BST_F, **BST_F_S1** |
| K110 | 4 | `NetK76_ACM_BST_S1_4` | K76.4, K135.4, R_BST.2, TP_BST_S, **BST_S_S1** |
| K110 | 2 | `NetK110_BST_S1_2` | PB0_S_S1, PWM1_S_S1, R_PB0.2, TP_PB0_S, TP_PWM1_S |
| K110 | 7 | `NetK110_BST_S1_7` | PB0_F_S1, PWM1_F_S1, S24_P10, K147.2, R_PB0.1, TP_PB0_F, TP_PWM1_F |

### D.2 逐条事实（FACT）

1. **`S5_ACM200_FH18/SH18`（ACM200 S5 通道脚）、`K109.4/.5`、`K110.6/.3` 同时出现在同一 net 上** ⇒ 它们是**同一个节点**，**ACM 源与 K110 的公共端之间没有任何继电器**。
2. **K110 才是 ACM↔BST 的开关**：激磁时经 pin5/pin4 接到 `BST_F_S1`/`BST_S_S1` 网；不激磁时经 pin2/pin7 接到 `PB0_F/S`、`PWM1_F/S` 网。
3. **K109 的另一侧去 `FPVIe1_FL_BUS_S1` / `FPVIe1_SL_BUS_S1`**（FPVIe1 低总线），其 pin2/pin7 在**单成员网**（本导出中悬空）。
4. 因此"`S5_ACM200_FH18 → K109 的掷 → K110 的 common → BST`"这种**串联读法与本网表的 net 成员关系不符**：三者同网 ⇒ **K109 不在 ACM→BST 的串联路径上**。

### D.3 推论与未知（INFERENCE / UNKNOWN，严格分列）

- **INFERENCE-1**：对 **ACM200 驱动**而言，**只闭 K110 即可到 BST**（K109 是否闭合不改变 ACM→BST 的通断）。
- **INFERENCE-2**：`pinRouteTable.BST["CH0 Low"].needsClosed = [109,110,138,139,145,146]` 是 **FPVIe CH0-Low 实例路线**的集合（FPVIe1 低总线 → 经 K109 → 同节点 → 经 K110 → BST）；该路线**确实需要 K109+K110**（与派生表 L43/L44 一致）。两套语汇的差异是**路线不同**，不是网表与派生表冲突。
- **UNKNOWN-1（重要，需电气判定）**：在 TM600 的 BST−SW 场景下**闭 K109 会把该节点与 `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1` 相连** —— 若这两条 FPVIe1 低总线在本项未被驱动/悬空，则无副作用；若被驱动或被其它项占用，则可能出现**非预期耦合**。**本导出不能判定其驱动状态**。
- **UNKNOWN-2**：K109 的 pin2/pin7 为单成员网，可能是"未使用触点"或导出范围限制；不影响 D.2 的结论（该结论只依赖 pin4/5 与 ACM/K110 同网）。

### D.4 对三项待办的修正结论

1. **契约 `closedRelayNumbers` 不应改为 `[109,110,61]`**：`[110,61]`（ACM200 路线）**与网表一致**；`109` 属 FPVIe 路线。若要表达完备，应走附录 B/A 的 **`closedRelayNumbersByRoute`**（按路线分列），**而不是**把两条路线的集合合并成一个"权威集合"。
2. **派生表 `SCH-Connect-Map.txt` L724/L725 不是"结构性遗漏"**：它画的是 **ACM 脚 → K110 → PB0/BST** 这一层，与网表同网关系一致（三层同网，链上只需 K110）。**但该表未画出 K109 的去向（FPVIe1 低总线）** ⇒ 建议在该表旁注明"K109 的另侧去 FPVIe1 低总线"，避免后人误判"K109 悬空/多余"。
3. **t29 payload 闭 K109 的记账**：按 D.3-INFERENCE-1，**K109 不是 ACM 路线所必需**；按 UNKNOWN-1，闭合它**可能**引入与 FPVIe1 低总线的耦合。**是否保留由 Captain/实现者按电气判定**（我不改 payload；`K109` 不在任何负列表，现无功能性副作用被证实）。
4. **对 `t30` 的提醒**：若按"网表 net 成员推导串联集"，**必须按"网络连通性"而非"继电器名字顺序"推导** —— 按名字顺序会得出"K109 与 K110 串联"的错误串联集，从而把 FPVIe 路线的要求强加到 ACM 路线上。**阳性对照仍成立**：当前树缺 K110 ⇒ 对 TM600 报红（K110 是 ACM 路线唯一必需件）。

### D.5 我方更正（如实）

- 附录 C 的**方向结论**（"K109 不在 ACM 脚链上"）**经网表复核成立**；
- 但附录 C 里"`[109,110,138,139,145,146]` 属 FPVIe 路线"的**判定同时被网表证实**（D.3-INFERENCE-2），因此**"契约自相矛盾"的定性应弱化为"两套路线语汇未标注"**（见 D.4-1 的 `closedRelayNumbersByRoute` 方案）；
- **我未据任何未验证前提改动契约**：`setup-contract.json` 仍为 **rev 24 / 328,805 B / `fd00a5082170293fcea29446c009fc432977d61a8f624ef17ac1c82f41515a18`**。


---

## 附录 E（端子图复核后定稿，v1.5）— 端子级机理、两处措辞更正、A 方案落笔清单

### E.0 权威端子图（我独立复核；此前我未检索到，属检索遗漏）

`knowledge/hardware/relays.md` = **13,624 B / `8029ee13690ca2158e48ea002bad69f2d943d76126bb133b4e54b8401934fcdb` / 246 行**，其中 **L3-31** 给出 **G6K-2G-Y（DPDT，磁保持）** 端子表：**3 = COM1、6 = COM2、2/7 = NO、4/5 = NC**；口诀 **"默认 2-3 通、6-7 通；通电 3-4 通、6-5 通"**。

### E.1 套用端子图后的机理（FACT，两个独立来源互相印证）

| 事实 | 依据 |
| --- | --- |
| **ACM 源落在 K110 的公共端**：`K110.S1.6 = COM2` 与 `S5_ACM200_FH18` 同在 `NetK109_BUSL_PB0_S1_4` | 端子表 L25 + 网表 net 成员 |
| **K110 单独完成 ACM 路线**：置位 6-5 → `NetK57_CAP_BST_SW_S1S2_3`（`BST_F_S1`）；复位 6-7 → `NetK110_BST_S1_7`（`PB0_F_S1`/`PWM1_F_S1`） | 端子表 L29 + 网表 |
| **K109 的公共端是 FPVIe1 低总线**：`K109.S1.3 = COM1` → `FPVIe1_FL_BUS_S1`；`K109.S1.6 = COM2` → `FPVIe1_SL_BUS_S1` | 端子表 L22/L25 + 网表 |
| **K109.S1.4/.5 = NC 只是"接在同一 net 上"**（同 net ≠ 串联）；K109 的 NO 脚 2/7 为单成员（悬空）net | 端子表 L23/L24 + 网表 |
| ⇒ **K109 不属 ACM 脚路线**；ACM→BST 由 K110 单独完成 | E.1 前四行 |

### E.2 两处措辞更正（接受复核方意见，按"旧→新"留痕）

| 旧表述（附录 C/D） | 更正为 |
| --- | --- |
| "K109 在 ACM 脚路线上的必要性**未独立确立**" | **"K109 不属 ACM 脚路线"**（已由端子图否定其必要性；"未确立"太弱） |
| "**两条路线共用双掷 K110**" | **"K110 是 ACM 路线的 BST↔PB0 摆动器；K109 另有自己的两对极点（COM1/COM2 + NO/NC），两者不是共用同一双掷，只是**在同一 net 上相接**"** |

### E.3 必须并列写清的两句（否则后人会误判 t29）

> **(a)** **K109 不属 ACM 脚路线**（E.1；ACM→BST 只需 K110）。
> **(b)** **但契约字面权威仍要求 K109**：`tmDeltas.TM600.relaySet` 含 `109`，且 `pinRouteTable.BST["CH0 Low"].needsClosed` 含 `109` ⇒ **t29 闭 `K109`+`K110` 属"依约保守"，合规、无需修订**；复核方 `verdict=pass` 维持（仅**理由**按 E.1 更正）。
> **(b-0) 限定（v1.20 就地补入）**：本句的"依约保守"**仅在 rev 24 的 `bst2sw` 映射下成立**；rev 25/33 起该映射已按 ch5 收窄（`closedRelayNumbers=[48,60,61,76]`）⇒ 本句**作为历史陈述**保留，不再是现行依据（现行依据见 §L.3）。
> **(b-1) 防误用条款（v1.20 更正；与 §L.3 的落批口径并存、不冲突）**：**复核方原意（保留）**：**(a) 不得单独用于判定 `38,147 B / 272667f3…` 版**的 t29 违规 —— 该版依 **rev 24 契约字面**闭合，**其 `verdict=pass` 不被 ch5 结论推翻**。**更正**：`K109/K110` 的**移除**决定于 **§L.3 的完整 ch5 证据链**（在役生产代码 4 处 `K48+K76`、复合宏 `K_BST_ACM`、控制组、ch18/ch5 网表分离、IR `required_on=[48,76]`）+ **Captain 落批**，**不是**由 §F.6 或 §H.2 的可达性证明**反推**而来 ⇒ **二者不冲突**（本 run 的最终处置确为"移除"，见 §L.3 与 §I.2，并已由现盘 payload 执行：`K109`/`K110` 可执行计数 = 0）。但**任何人不得仅凭"`K109` 不属 ACM 路线"这一句就删除它** —— 须同时具备**完整 ch5 证据链 + Captain 落批**。
> **(c) 附带 UNKNOWN（未验证，需电气判定）**：TM600 场景闭 K109 会把该节点接到 `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`；两条总线在本项的驱动/悬空状态**本导出不可判定** ⇒ 若有占用则可能非预期耦合。**建议 payload 不动，写入 t34 限制清单。**

### E.4 路径 A 的落笔清单（复核方与我的意见一致；**待 Captain GO**）

1. `closedRelayNumbersByRoute`：`acm = [110, 61]`（**首要 locator = `relays.md` L3-31 端子表**；`SCH:723-725` 作佐证）、`fpvieCh0Low = [109,110,138,139,145,146]`（标 **legacy / 未采用**）；
2. `acmDriveFrame`：`K110.COM2 = S5_ACM200_FH18/SH18`；置位 → `BST_F/BST_S`；复位 → `PB0_F/PB0_S`；SW 经 `K61_ACM8_SW`；**差分 = ACM 输出电平**；
3. `unrealisableRoutes`：`CH0 High -> BST [46,48,76]`（`SCH` L46-50 显示其经 `K41/K42/K43` 到 **BST1/BST2**，非本项 BST）、`CH1 -> BST [109,110]`；
4. `terminalAssignment` / `nodeOnHighTerminal` 标 `legacy:true` + `supersededBy:acmDriveFrame`（**不删原文**）；
5. **rev24/rev25 引用规则**：下游一律引 rev25；并广播新 revision + 现算哈希。
**执行前置**：Captain GO + （复核方已表示对 A 无保留意见）；**未获 GO 前按 B（登记限制）**。

### E.5 对 t30 的最终口径（复核方与我就此一致）

断言须以 **端子图（`relays.md` L3-31）+ netlist net 成员**推导串联集，**不得以 `sch_connect_map` 派生表为源**（否则漏 K109）；并应检测**派生表 vs 网表不一致**；其失败须落 **NEW-RED / exit 1** 通道（不得只 warn）。**夹具硬连仍为"未发现证据"、非"已排除"**；出现新证据则本归口重开。


### E.6 门禁盲区成因（t30 实测补录，2026-09-16）

- **成因（t30 执行者实测）**：`verify_bst_sw_sequence.py` 在 t30 之前**完全不读契约**（`setup-contract`/`aliasResolution`/`needsClosed`/`relaySet`/`K109`/`K110` 命中数全 0），且其**目标集是 ZCD 家族（TM607/608/609/640）**，**TM600 根本不在其中** ⇒ 这就是"12 门全绿却漏掉契约要求闭合的 K110"的直接原因。**我复核**：该脚本现 = **24,964 B / `17092feac034902e…`**，已含 `setup-contract`/`needsClosed`/`relaySet`/`TM600` 命中 ⇒ 盲区已被 t30 关闭。
- **t30 阳性对照实测**：`TM600_HS_RDSON 契约声明必需 [60,61,83,110] 缺失=[110]`；TM601 缺失 `[]`；门禁级 **FULL_EXIT=1，仅 `bst-sw` 变 NEW-RED、其余 11 门逐字不变**；`gate_baseline.json` 未改（28 B / `021015da…`）；`--skip-contract-closures` 证明纯增量。
- **断言语义（与我 E.5 口径一致）**：按"**契约声明必需**"判定（缺失即 RED），**不是**把该闭的判成不该闭 ⇒ **t29 只补 K110 也能转绿**；补 K109 亦不引入"多闭"红（除非另启用 `--check-extra`）。
- **证据文件**：`gate-logs-t30/bst-sw-positive-control.log`、`bst-sw.log`、`t30-k110-cross-check.py`/`t30-k110-cross-check.log`（含 L42/43/44/109/110/724/725 逐行读数与契约三方对照）。
- **落盘哈希（供 t33/t34 引用）**：`check_input_sync.py` = 17,455 B / `e804c459b2d3088e…`；`verify_bst_sw_sequence.py` = 24,964 B / `17092feac034902e…`；`run_gates.ps1` = 9,763 B / `dd2a4337f22d339a…`；`gate_baseline.json` = 28 B / `021015da84e6fd4c…`（未改）。


### E.7 payload 来源结案 + DELIVERED／DEPLOYED 两栏约定（供 t33/t34 统一引用）

- **来源已结案**：`38,147 B / `272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0` @19:30:55` 经 **payload owner（ate-implementer）声明为 t29 final**（**该版现为过渡态**：其后 t38 的阻断修复产出 **`39,457 B / 2d0984d992d5d8cb11868660b29cb…`** 为**现盘**）、并由 test-strategy-architect 与本人各自只读实测确认（`K109_BUSL1_PB0 ×2`、`K110_ACM18_BST ×2`、`K126_V1P5_CAP ×3`、`delay_ms(2) ×0`、`SetClamp(50,50) ×2`）⇒ **含 t29 修复、非回退**。链条：`bf7e58da…(26011) → 889c8e77…(27228) → 73995983…(32969) → 444810dd…(35014) → 73b511b7…(36381) → 272667f3…(38147, t29 final) → 2d0984d9…(39457, **current**, t38 移除 TM601 ACM 驱动)`。
  **canonical 的"名义确认"仍归 Captain**（owner 声明≠终裁）；但**"来源不明"这一疑点已消除**，不再阻塞任何 pin 的表述。
- **两栏约定（我此后一律如此写；建议 t33/t34 同样）**：
```
DELIVERED（交付件，未落盘） = implementation-payload-TM600-TM601.cpp
                              38,147 B / 272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0 @19:30:55
DEPLOYED （目标树实际内容） = ForCodexDebug/source/test.cpp
                              469,714 B / 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a @18:53:33
                              K109_BUSL1_PB0 = 0 / K110_ACM18_BST = 0  ⇒ 缺 t29 修复（待 Captain REPLACE）
```
  规则：**描述"交付件/继电器集合/契约符合性"引 DELIVERED；描述"当前盘上实际行为/门禁实测"引 DEPLOYED**；二者之差＝**待 Captain 执行的 REPLACE**。**据此，任何"12 门全绿"的陈述必须注明是 DEPLOYED(t23) 状态**——那正是 K110 缺失仍被漏过的现场。
- **本人的 pin 说明**：`implementation-input-pin.json` **按设计不含 payload 行**（其字段范围由 Captain 逐次授权），因此上述两栏只在**本文件与报告**中出现；若 Captain 授权，我可再加一行以固化。


---

## 附录 F（IR 级复核，v1.6，**本附录取代附录 B.1 的那句定性**）— K110 必需且充分；K109 不属 ACM 基线路径

> **⚠️ 标题级更正（v1.21，Captain 授权的事实性更正）**：本标题的两句**只对 ch18 腿成立** —— **ch18（`S5_ACM200_FH18/SH18`）→ BST 需 `[110]`；ch5（`S5_ACM200_FH5/SH5`，本仪器 `SW12_U1REF_BST_ACM`）→ BST 需 `[48,76]`**；`K110` 属 `PB0_BST_ACM`（ch18）。本附录正文其余内容保留为历史；现行依据见 §L（ch5 收窄）与 §L.3。

### F.1 权威 IR 证据（我独立复算 `schematic-validation/path_proofs.json.txt`，669 条 accepted path proofs）

| 源端口 → 端点 | `required_on` | path（继电器级） |
| --- | --- | --- |
| **`S5_ACM200_FH18 -> BST_F_S1`** | **[110]** | `K110`（ON, pin6→5），**单继电器** |
| **`S5_ACM200_SH18 -> BST_S_S1`** | **[110]** | `K110`（ON, pin3→4），**单继电器** |
| `S10_CH0_B -> BST_F_S1` / `-> BST_S_S1` | `[109,110]` / `[109,110,130]` | 含 K109 |
| `S1_FPVIe_FL0 -> BST_F_S1` / `S1_FPVIe_SL0 -> BST_S_S1` / `FL1`/`SL1` | `[109,110,145,146]` / `[109,110,138,139]` / `[109,110]` | 含 K109 |
| `S8_QVM_CH0- -> BST_S_S1` | `[109,110,139]` | 含 K109 |
| **全部含 109 的 accepted path** | **21 条，全部为 S10 / S1_FPVIe_* / S8_QVM 路线** | **无一条是 `S5_ACM200_*`** |

⇒ **FACT（v1.16 事实性更正，Captain 授权一次；记录级 IR 证据推翻原句的"整体结论"）**：**`S5_ACM200_*→BST` 有两族并列，原句"ACM200 S5 通道到 BST 只需 `K110`（必需且充分）"**只对 ch18 成立、整体结论作废**：
> - **ch18（`S5_ACM200_FH18/SH18`）→ `BST_F/S_S1`：`required_on=[110]`**（path `K110(ON,6→5)` / `K110(ON,3→4)`）；
> - **ch5（`S5_ACM200_FH5/SH5`）→ `BST_F/S_S1`：`required_on=[48,76]`**（path `K48(ON,6→5)→K76(ON,6→5)` / `K48(ON,3→4)→K76(ON,3→4)`）—— **与 `K110` 无关**；
> - **本基线用哪一族，取决于 `SW12_U1REF_BST_ACM` 的通道归属**：`t42` 主张 **ch5**、`t43` 判 **UNKNOWN（可约束）**；
> - **逻辑缺口（如实记录）**：本行上方"含 109 的 21 条 accepted path 无一条是 `S5_ACM200_*`"**陈述本身正确**，但**只排除了 `K109`，不足以推出"ACM200 S5 只需 `K110`"** —— 该推理漏掉了 **ch5 的 `[48,76]` 族**（`rule-reviewer` 记录级解析 669 条 `accepted_path_proofs` 所得，见 `schematic-validation/path_proofs.json.txt`）。
> - **保留**：**后人不得据"`K109` 本非 ACM 所需"判 `t29` 多闭**（该禁令见 §E.3 (b-1) 与 §F.6）。
（旁证：`S5_ACM200_FH18 -> PB0_F_S1` 亦为 accepted path，`required_on=[]`、path=`K110(NC)` ⇒ 未激磁落 PB0，与端子表/网表一致。）

### F.2 取代 B.1 的定性（**B.1 那句"两种读法下都应闭"作废**）

> **限定（v1.20 就地补入）**：本节及 §B.1/§F.1 的"两种读法/依约保守"论述**仅在 rev 24 的 `bst2sw` 映射下成立**；rev 25/33 收窄为 ch5 后，**现行依据是 §L.3 的完整 ch5 证据链 + Captain 落批**（现盘 payload 已按此执行：`K109/K110` 可执行计数 = 0）。单独引用本节时请连读本限定。

> **正确表述（v1.21 更正）**：**ch18（`FH18/SH18`）→ BST 需 `[110]`**；**ch5（`FH5/SH5`，本仪器）→ BST 需 `[48,76]`**；**`K109` 不出现在任何 `S5_ACM200_*→BST` 路径上**。原句"K110 必需且充分"的整体结论**只对 ch18 成立**；本仪器按 ch5 ⇒ `[48,76]`（见 §L）。
> **t29 payload 仍合规、verdict 仍 `pass`** —— 因为**契约字面**仍要求 K109（`relaySet∋109` **且** `pinRouteTable…CH0 Low.needsClosed∋109`）；**K109 的闭合应记为"依约保守、超出 IR/端子图所需"**，**不是**"两种读法都必需"。
> **后人注意**：据 IR/端子图，ACM 路线只需 K110；据 `pinRouteTable.needsClosed` 会继续多闭 K109 —— 这正是路径 A（按路线分列）要消除的歧义。

### F.3 归口 2 的 locator 更正（首要 locator = 端子图）

- **首要 locator：`knowledge/hardware/relays.md` L3-31**（G6K-2G-Y DPDT：**3=COM1、6=COM2、2/7=NO、4/5=NC**；"默认 2-3 通、6-7 通；通电 3-4 通、6-5 通"）—— 这是"ACM 脚即 K110 公共端"的**唯一建立者**；
- **佐证**：`SCH-Connect-Map.txt:723-725`（仅显示 `FH18 -> K110(NC) -> PB0`，不显示公共端）、附录 F.1 的 IR `required_on=[110]`。

### F.4 冻结与引用纪律（因两份文件曾被继续追加）

- **自本附录起，`t35-contract-reconciliation.md` 与 `meta-excitation-override-revision-history.json` 双双冻结**（除非出现新事实且经 Captain 指示）；引用**一律现算**，本文件内历史公告值一律作废。
- 现刻现算（本附录写完后即为冻结值）：**t35 = 见本任务报告**；链 = **17,431 B / `f96ef93edcf9ba7bc0868158d9d804e4b1214cb6c19e817753cbd19c933096e2`**。

### F.5 payload 记账（供 Captain 定性）

- 工作区现盘 = **39,457 B / `2d0984d992d5d8cb11868660b29cb…` @19:55:59**（t38 阻断修复后，TM601 块内 ACM 驱动命中 0）；**`38,147 B / 272667f3…` @19:30:55 为 t29 final、且是 rule-reviewer 的 t29 `verdict=pass` 所针对的那一版**（其报告标注"待落盘字节 = 现盘 38,147 B"属**实测陈述**，非定性）；
- `36,381 B / 73b511b7…` 与 `35,014 B / 444810dd…` **均已被取代且无副本**；
- **落盘/前置断言请按"现盘 = `2d0984d9…`（39,457 B）"处理**；若 Captain 选择以 `272667f3…`（38,147 B）落盘，则须同时说明"该版含 TM601 悬空 ACM 驱动"这一已知缺陷，否则实际字节与判据不一致。


### F.6 限制项口径（复核方精确化，**必须同句出现**）

> **闭合 `K109` 的现状与风险（三条必须并列陈述，不得单独引用任一半句）**：
> **(i)** 现盘 TM600 的 SetOn **已含 `K109_BUSL1_PB0`** ⇒ 该耦合**不是潜在风险，而是当前闭集下已经发生**：`K109.COM1/COM2` 分别接 `FPVIe1_FL_BUS_S1` / `FPVIe1_SL_BUS_S1`（端子表 L22/L25 + 网表）；
> **(ii)** 同时，`K109` **不在任何负列表**、且**目前没有被证实的功能性副作用**；
> **(iii)** **两总线在本项的驱动/悬空状态本导出不可判定** ⇒ **是否需要避免该耦合属电气判定，不属本任务（契约归口）裁定**。
> ⇒ **t34 的必录限制清单必须同时含 (i)(ii)(iii)**（与 B-1..B-5 并列），并注明「导出不可判定驱动状态」。**任何只写 (ii) 的表述都会被读成「无副作用」，属误导。**

### F.7 复核依据措辞（复核方折中，我采纳）

> *「**复核所依据的字节 = 现盘 `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`（39,457 B @19:55:59，实测）**；`38,147 B / 272667f3…`、`36,381 B / 73b511b7…`、`35,014 B / 444810dd…` 均为**已被取代的中间态（无副本）**；`canonical` 由 Captain 定性。」*

> **定点更正说明（v1.13，2026-09-16，Captain 授权一处）**：本节原措辞把复核依据指向 `38,147 B / 272667f3…`（当时为现盘）；现盘已前进为 **`39,457 B / 2d0984d9…`**（t38 删除 TM601 悬空 ACM 驱动）⇒ 依授权**仅更正本句**，其余段落一字未动。**归属分列（同 Captain 裁定）**：**t29 的 `pass` 覆盖 TM600 侧补闭合**（`L219` 在两版逐字相同）；**TM601 侧的移除由 `t40` 覆盖**；不得把整版现盘交付件记作 t29 的成果。
> 两者不冲突：**verdict 必须指向一组具体字节**（审阅的定义），**canonical 是 captain 的定性**（运行纪律）。落盘字节 ≠ 复核字节的风险由此消除。

**本次更正说明（v1.7）**：应复核方要求修正**三处同文件内不一致**（E9 失效哈希、正文①/B.1 旧推理、UNKNOWN-1 的并列要求）；改后**本文件再次冻结**。


### F.8 复核方 B-6 与 `bst2sw.usedByTm` 的 TM1205 登记（并入路径 A 的第 ⑥ 项）

- **B-6（门禁能力边界）**："契约派生断言的覆盖上限 = 契约登记完整性" —— 我接受该定级，并据此**扩张 A 的清单**：
- **`aliasResolution[bst2sw].usedByTm` 现为 `["TM600 (BST must lead PMID)", "TM1205 (BST1-SW1 / BST2-SW2 ramps)"]`，其中 **TM1205 的登记与 IR 不符**（IR 实测，669 条 accepted path）：
  - **16 条以 `BST1_*`/`BST2_*` 为端点的 accepted path，无一条 `required_on` 含 `110`**：`S1_FPVIe_FL0 -> BST1_F_S1 = [41]`、`-> BST2_F_S1 = [41,43]`、`S10_CH0_B -> BST1_F_S1 = [41,142]`、`-> BST2_F_S1 = [41,43,142]`、**`S5_ACM200_FH4 -> BST1_F_S1 = []`（默认导通）**、`S5_ACM200_FH4 -> BST2_F_S1 = [43]` 等；
  - ⇒ **TM1205 的 BST1/BST2 路线不需要 `K110`**，把 TM1205 挂在 `bst2sw`（其 `closedRelayNumbers=[110,61]`、`relayChain=[K110…, K61…]`）名下**会误导下游**（例如 t30 的断言若按 `usedByTm` 索引，会把 TM1205 也纳入 K110 的必需范围）。
  - **路径 A 的第 ⑥ 项**：在 rev 25 中把 `bst2sw.usedByTm` 收窄为 **`["TM600 (BST must lead PMID)"]`**，并为 TM1205 增列独立路线条目（`BST1/BST2` 各自 `needsClosed`，按上表 locator），或在 `usedByTm` 条目上加 `doesNotRequire: [110]` 的显式说明。**依据 locator**：IR `accepted_path_proofs[S1_FPVIe_FL0->BST1_F_S1]` 等 16 条 + `SCH-Connect-Map.txt:45-50`（`CH0 Low -> BST1 需闭合: K41`；`-> BST2 需闭合: K41,K43`）。
- **冻结说明（v1.8）**：本次更正为"（a）两处取代标记已就位、（b）payload 引用统一到现盘 + 过渡态标注、（c）并入 B-6 与 TM1205 项"；改后本文件**再次冻结**（新哈希见任务报告）。


### F.9 门禁盲区成因（**两个**，t30/t33 实测补录，更正 E.6 的单一成因表述）

E.6 只写了"`bst-sw` 不读契约"——**执行方指出这不是全部**，我据其实测与我的复核并录如下**两条成因**：

1. **不读契约**：t30 之前 `verify_bst_sw_sequence.py` 对 `setup-contract`/`aliasResolution`/`needsClosed`/`relaySet`/`K109`/`K110` **命中数全 0**；
2. **作用域不含 TM600**：该门禁的目标集是 **ZCD 家族 `TM607/608/609/640`**（由 meta `powered_pins` 指纹派生），**TM600/TM601 根本不在其中** ⇒ **即使加了契约读取，若作用域仍取门禁内部 targets，阳性对照依旧 `FAIL=0`**（执行方实测，见 `t30-summary.md` §2 第 3 行）。
   ⇒ 最终修法：作用域改为**显式可参数化** `--tm-scope`（默认 `TM600_HS_RDSON,TM601_LS_RDSON`）。

**执行方的机制更正留痕（三轮，第三轮为准）**：① 第一轮把 `SCH L109/L110` 读成"K110 经 NC 到 PB0 ⇒ 质疑必要性"（漏读 `L43/L44` 的 `K110(Relay-ON)->BST_F`）⇒ **已撤回**；② 第二轮"同一文件里的不同路线"（≈本文件附录 A/B 口径）⇒ **已被端子级证据取代**；③ **第三轮（权威）**：端子表 + 网表 ⇒ **ACM 源在 K110 公共端，通电到 BST、默认到 PB0** ⇒ 以其为准（落盘 `gate-logs-t33/t33-k110-mechanism.md`，v1 探针保留不作废，作为更正留痕）。**首 locator 亦已按其更正为端子表 `relays.md:18-31`，`SCH:723-725` 作佐证。**

**旁证（我复核其只读脚本的读数，与本节一致）**：`K110.3 (COM1) → NetK109_BUSL_PB0_S1_5`（＝`S5_ACM200_SH18`，同 net 含 `K109.5`）；`K110.6 (COM2) → NetK109_BUSL_PB0_S1_4`（＝`S5_ACM200_FH18`，同 net 含 `K109.4`）；`K110.4 (NC) → NetK76_ACM_BST_S1_4`（＝`BST_S_S1`）；`K110.7 (NO) → NetK110_BST_S1_7`（＝`PB0_F_S1/PWM1_F_S1/S24_P10`）；`K109.3/6 → FPVIe1_FL/SL_BUS_S1`。

**冻结说明（v1.9）**：本次仅补录成因第二条与执行方的更正留痕；改后本文件**再次冻结**（新哈希见任务报告）。


### F.10 精确化定性（复核方 §③，采用）与 A/B 语义重述（复核方 §④）+ 其 IR 全景证据（§②）

**① 定性升级（取代"两套语汇未标注"的说法）**：
> **不是两个字段互相矛盾，而是"一个字段承载了两条路线的并集而未分列"**：
> `tmDeltas.TM600.pinRouteTable.BST["CH0 Low"].needsClosed = [109,110,138,139,145,146]` **同时**含
> **ACM 路线所需（`110`）** 与 **FPVIe 路线所需（`109,138,139,145,146`）**，**未按路线分列**
> ⇒ **按其实现的 payload 会多闭 `K109`**。
> **为什么采用这个说法**：它直接给出**可执行修法（分列）**；"语汇未标注"只描述症状。

**② A/B 语义重述（按复核方要求，二者互斥且可裁决）**：
- **A（推荐，我无保留支持）= 分列**：`closedRelayNumbersByRoute` = `{acm:[110,61]}` / `{fpvieCh0Low:[109,110,138,139,145,146]}` / `{s10Ch0B:[109,110]}` + `pinRouteTable.BST` **消歧句** + `acmDriveFraming` + `unrealisableRoutes`（+ F.8 的第 ⑥ 项 TM1205 登记更正）；
- **B（不推荐）= 把 `K109` 写进 ACM 路线集合**（即让 ACM 路线也"需要" K109）⇒ 与端子图/网表/IR **三源相反**，会把错误的路线归属固化成权威。
  （此前把 B 写成"并入 `[109,110,61]`"——**语义已按本条更正为"写进 ACM 路线集合"**，以免与"两路线分列"混淆。）

**③ 复核方提供的 IR 路径全景（独立于网表的第二来源；我已复算一致）**：
```
S5_ACM200_FH18->BST_F_S1  requiredOnRelays=[110]           chain=[K110_BST_S1 "110:ON"]
S5_ACM200_SH18->BST_S_S1  requiredOnRelays=[110]           chain=[K110_BST_S1 "110:ON"]
S1_FPVIe_FL0->BST_F_S1    requiredOnRelays=[109,110,145,146]
S1_FPVIe_SL0->BST_S_S1    requiredOnRelays=[109,110,138,139]
S1_FPVIe_FL1->BST_F_S1    requiredOnRelays=[109,110]
S1_FPVIe_SL1->BST_S_S1    requiredOnRelays=[109,110]
S10_CH0_B->BST_F_S1       requiredOnRelays=[109,110]
S10_CH0_B->BST_S_S1       requiredOnRelays=[109,110,130]
S8_QVM_CH0->BST_S_S1      requiredOnRelays=[109,110,139]
```
⇒ **凡"ACM200 通道 → BST"只需 `[110]`；凡"FPVIe/QVM 低总线 → BST"都需 `[109,110,…]`** ⇒ K109 属 FPVIe/QVM 一侧。
⇒ 并解释 F.10-① 的并集来源：`pinRouteTable.BST["CH0 Low"]` 的 `[109,110,138,139,145,146]` **恰为** IR 中 `S1_FPVIe_FL0->BST_F_S1`（`109,110,145,146`）与 `S1_FPVIe_SL0->BST_S_S1`（`109,110,138,139`）两条路径的**并集**。

**④ 复核方 §⑤ 的确认（我不再重复举证）**：`verify_bst_sw_sequence.py` 对 `needsClosed`/`relaySet` 命中 **0** ⇒ **该门从未导入路线表**，故**它不是 K109 多闭的来源**；来源是**契约数组**（`relaySet` 含 109 且 `pinRouteTable…CH0 Low` 含 109）⇒ **t29 依约保守**成立。

**⑤ 复核方 §⑦ 的成对措辞要求**：已由 **F.6** 落实（三条并列：(i) 耦合**已经发生**／(ii) 不在负列表且**目前无可证实副作用**／(iii) **两总线驱动状态不可判定**），并已列入 **t34 必录限制清单**；**禁止只写 (ii)**。

**冻结说明（v1.10）**：本次为定性精确化 + A/B 语义重述 + 证据并入；改后本文件**再次冻结**（新哈希见任务报告）。


---

## 附录 I（v1.11）— t34 前置与必录清单（契约 owner 侧登记，供 myself 与复核方对照）

### I.1 t34 的两条**前置依赖**（缺一不可）

1. **落盘（REPLACE）发生**：`DELIVERED` 与 `DEPLOYED` 必须收敛。**t34 中的 DELIVERED 必须写成"落盘时刻现算"的 size/sha256/mtime + 内容键**（`t29 PER-FUNCTION JUSTIFICATION` / `K109_BUSL1_PB0` / `K110_ACM18_BST`），**不得沿用任何先前公告值**（本 run 已出现四次"同一文件不同哈希"：35,014→36,381→38,147→39,457）。
2. **一次"可写会话"的 Release 构建**：本会话对 `D:/PROJECT6-DALI/ForCodexDebug` **只读**，MSBuild 实测 `error MSB3491`（写 `source\Release\F12011.tlog\F12011.lastbuildstate` 被拒）⇒ **Release 编译只能由 Captain 的可写会话完成**（或换含目标树工作区的会话）。**t33 的 `build-report.json` 现为 `verdict=blocked`（落盘前状态记录），不是最终证据**。

### I.2 门禁证据的**归属规则**（t33 执行方落实，我确认采用）

- `compiledRevision = 15c7d2b8…`（t23，缺 K109/K110）—— **一切门禁/编译证据的归属对象**；
- `expectedAfterReplace` = 落盘时刻现算的 payload sha256（当前候选 `2d0984d9…`）；
- **红/绿归属跟随 `compiledRevision`** ⇒ `bst-sw = NEW-RED`（K110 缺失）属于**部署修订**，既不属于构建过程、也不属于未部署的 t29 payload；
- `cbit` = **基线豁免**（`gate_baseline.json` 未改：28 B / `021015da…`）；`relay-trace`/`input-sync` GREEN ⇒ t25/t28 断言在位且通过；
- `postReplaceExpectation`（**两口径并列，v1.14 事实性更正**；单写"转 GREEN"已被 `t42` 否证）：
  - **若契约仍为 rev 24（ch18/pin-18 口径，期望 `[60,61,83,110]`）** ⇒ t29 payload 落盘后 `bst-sw` **应转 GREEN**，其余 11 门不变；
  - **若契约已 rev 25（ch5 口径，期望 `[48,60,61,76]`）而 payload 未补 `K48/K76`** ⇒ `bst-sw` **仍为 NEW-RED（缺件）** —— 属**第二处真缺陷**，不是回归、也不是 t29 的错；
  - **🔴 现状（按 `t50` 现值实测，v1.17 事实性更正）**：payload = **43,806 B / `66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4`@21:09:24**，**TM600 的 SetOn（L264）= `{83,60,61,48,76,13,85,57,126}`** ⇒ **已闭 `K48/K76`（ch5 腿）且已不再闭 `K109/K110`（可执行计数 K48×1、K76×1、K109×0、K110×0）**；TM601 未闭 `48/76`、亦无 `109/110`（其轨道由 `sw2pgnd` 承担）。
  - **按路线分列口径（rev 26/27 `closedRelayNumbersByRoute`，期望 `{48,60,61,76,83}`）⇒ 满足 ⇒ `bst-sw` 期望 GREEN**；
  - **⚠️ 但按**现盘契约的遗留字段**（`aliasResolution[bst2sw].closedRelayNumbers=[110,61]`，rev 25 只增不翻未改它）⇒ 门禁仍会索要 `110` ⇒ **`bst-sw` 会报 NEW-RED，且该红是"期望字段未随路线分列切换"所致，不是 payload 缺陷** ⇒ 须由"门禁改读按路线分列字段"的任务收口（同批不得把此红记为回归）。
  - 说明：先前"仍红＝第二处真缺陷（缺 `48/76`）"的表述**只对 `t50` 之前的 payload 成立**，现已被本次更正取代（`t50` 已补 `K48/K76`）。
  - 实测依据（我复核）：部署态 **TM600（`test.cpp:9081`）** SetOn = `[83,60,61,13,85,57,126]`、**TM601（:9255）** = `[154,155,60,61,13,85,57,126]` ⇒ 两口径下 **TM600 都缺件**（ch5 缺 `48,76`；ch18 缺 `110`）；t29 payload 的 TM600 SetOn 已含 `110` ⇒ **只满足 ch18 口径**；
  - **旁证（强化 ch5）**：同一棵部署树的历史生产函数（`test.cpp:7000/7087/7170/7513`）明确闭合 **`K48_ACM5_AMP_REF + K76_ACM_BST`**，注释即 "BST ← SW12_U1REF_BST_ACM: …(FH5→BST)"。
- 参考产物：`gate-logs-t33/t33-revision-attribution.md`。

### I.3 t34 必录限制/未知清单（逐条，不得省略、不得美化）

1. **T32-F1（blocker）**：部署态 TM600 缺 `K109`/`K110`（成因＝ REPLACE 未发生，**与 t29 payload 合规不矛盾**）；
2. **T32-F2/F3（high）**：t24 所审对象（`444810dd…`/35,014）与部署对象（`15c7d2b8…`）不同；流通的 GREEN 门禁证据不属于部署修订；
3. **DELIVERED ≠ DEPLOYED**（附两栏与落盘时刻现算值）；
4. **门禁盲区（双成因）**：① 不读契约；② 目标集为 ZCD 家族 `TM607/608/609/640`、TM600 不在其中 ⇒ 仅加契约读取不改作用域仍 `FAIL=0`；最终以 `--tm-scope` 显式参数化（见 F.9）；
5. **meta 修正可能被下一次重生成静默抹除**（物证 `t26-regen-probe/dali_tm_meta.regen.json` = 146,180 B / `1c849664…`；缓解＝ t28 的 RS-1..RS-4 + manifest 登记，其回退红证用**真实**重生成产物验证）；
6. **`K109` 与 `FPVIe1_FL/SL_BUS_S1` 的耦合**（三条**必须并列**：已经发生／不在负列表且目前无可证实副作用／驱动状态本导出不可判定）—— 见 F.6；
7. **TM601 悬空 ACM 驱动**：判定不达 BST、落到 DUT 引脚 PB0/PWM1 侧 ⇒ 分级 **blocking**、处置移除（t38 已执行）—— 见 `t41` 附录 G/H；
8. **Release 编译在本会话不可达（MSB3491）**；若由 Captain 完成，证据须含其 `build.log` + DLL 哈希，并标注"证据来源＝Captain 会话"；
9. **编译闭环 ≠ 电性签核**；**未做任何机台/硬件电性验证**；
10. **契约仍 rev 24**（路径 A/rev 25 待 t40 回收 + Captain 裁定后执行）；**审计链 `verifiabilityGrade` = traceable, not independently verifiable（corrections 1..7）**。


---

## 附录 L（Captain 授权的**定点更正**，v1.15）— ch5 口径定案；D/E/F 的"K110 必需"前提作废

> **K110 结论更正声明（v1.23，复核方要求明写）**：**`t39` 与 `t35` 附录 D/E/F 的“到 BST 必须 `K110` 置位 / K110 必需且充分”结论予以更正** —— 该结论**只对通道 18（`PB0_BST_ACM`）成立**；**本案仪器 `SW12_U1REF_BST_ACM` = 通道 5 ⇒ BST 腿 = `K48_ACM5_AMP_REF` + `K76_ACM_BST`（`required_on=[48,76]`）**。四方独立证据（驱动宏通道索引／派生表 `SCH:662+672-674`／IR `[48,76]`／在役生产代码 `:6997/:7085` 注释与 `:7000/7087/7170/7513` SetOn）**经复核方逐条独立复核通过**。**跨域闭集 = BST `[48,76]` + SW `[60,61]` = `[48,60,61,76]`**（**SW 侧须写全 `K60`+`K61`**：同族 `pmid2sw=[83,60,61]`、`sw2pgnd=[154,155,60,61]` 与部署四处均如此；`[48,60,61,76]` **不完整**）。

> **结论行（v1.22，Captain 采信 addendum 后定点更新）**：`t43` **终局判定 = (a) ch5**（原 UNKNOWN 与并集建议已由其作者撤回；依据在役生产代码 `:7000/7087/7170/7513` 闭 `K48+K76`、`:6997/7598/7621` 同句写仪器与引脚、全文件 `K110_ACM18_BST`=0／`K109_BUSL1_PB0`=0；`t42` 独立 pass）。⇒ **本仪器 `SW12_U1REF_BST_ACM` 的 BST 腿 = `[48,76]`、SW 侧 `[60,61]`、闭集 `[48,60,61,76]`**；`K110` 属 `PB0_BST_ACM`（ch18），**本项不闭**。契约 `pendingOwnerRuling` 已更新为“t43 终局：判 (a) ch5（已生效）”（只增不翻、原文保留）。

### L.1 作废与更正（逐条指向本文件**既有段落**，不再改动其正文）

| 既有位置 | 原表述 | 处置 |
| --- | --- | --- |
| 附录 D.1/D.3、附录 E.1、附录 F.1/F.2 | 以 `K110` 为 ACM→BST 的唯一开关（"K110 必需且充分"） | **作废**（该结论只对 **ch18** 成立，不是本案仪器） |
| 附录 F.3、`aliasResolution[bst2sw]` 相关叙述 | `closedRelayNumbers=[110,61]`、`relayChain=K110_ACM18_BST→K61_ACM8_SW` | **更正为 ch5 口径**：**BST 侧 `[48,76]`（`K48_ACM5_AMP_REF` + `K76_ACM_BST`）**；SW 侧按四方证据重推（既有实现为 `K60+K61`）⇒ **BST–SW 闭集 = `[48,60,61,76]`** |
| 附录 B.1 / E.3 / F.2 中的"依约保守"半句 | "契约字面要求 `K109`（`relaySet∋109` 且 `pinRouteTable…CH0 Low.needsClosed∋109`）⇒ t29 同闭合规" | **保留为历史记录，并加限定**：*"**仅在 rev 24 的 `bst2sw` 映射下成立；rev 25 更正该映射后不再适用**"* |

### L.2 更正后的权威映射（六条独立证据）

**本案仪器 = `SW12_U1REF_BST_ACM` = ACM200 `channel 5`**（`Pin_Channel_define.h:20` `"S5_5,…"`；对照 `:33 PB0_BST_ACM = "S5_18,…"` ⇒ **两台不同仪器**）⇒ **到 BST 需 `K48+K76`**：`SCH:672-674`（列6 需闭合 `K48,K76`；`F: S5_ACM200_FH5 -> K48(ON) -> K76(ON) -> BST_F`）；IR `S5_ACM200_FH5/SH5 -> BST_F/S` **required_on=[48,76]**；**目标树生产代码**（`:6997/:7085` 注释 + `:7000/:7087/:7170/:7513` 闭 `K48_ACM5_AMP_REF`+`K76_ACM_BST`）；`t42`/`t44`（行为层 4 处调用点 + 15 条复合宏穷举 + 控制组 5/5 + ch5/ch18 网分离）；`compile-diagnostician` 独立控制组 5/5；`schematic-expert` 独立核验。**ch18（`PB0_BST_ACM`/`K110_ACM18_BST`）单列**，供其自身用途。

### L.3 落盘批（Captain ④/⑤）与 I.2 的三口径

本 run 采用 **rev 25 + payload 修正同批**（payload：TM600 补 `K48_ACM5_AMP_REF`+`K76_ACM_BST`；`K109/K110` **按 `t43` 的并集策略本轮应【保留】**、删除推迟另行裁定 —— ；`K109/K110` 的**最终处置 = 移除**（`t43` 的并集/UNKNOWN 已被其作者撤回并改判 **ch5**，契约 rev 33 已按 ch5 收窄：`closedRelayNumbers=[48,60,61,76]`、原文入 `superseded`）⇒ 现盘交付件（闭 `K48/K76`、无 `K109/K110`）**即为合规版**；此前的"本轮应保留"表述**作废**）⇒ **`bst-sw` 期望 = GREEN**。I.2 已同步改为**三口径并列**（rev 24 单改契约 ⇒ 绿；rev 25 单改契约而不补 payload ⇒ 红〔第二处真缺陷〕；**rev 25+payload 同批 ⇒ 绿〕**），并保留旁证与实测依据。**更正后本文件再次冻结**（台账记录该"事实性错误"例外）。
