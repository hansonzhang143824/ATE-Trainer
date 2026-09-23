# TM108 逐阶段 BST-SW 约束检查（0 V ≤ BST_actual − SW_actual ≤ 5 V）

- runId: `tm108-v2-trial` · task: `t5` · owner: **test-method-expert** · 目标 TM: **TM108** 唯一
- 规则：`team/TEAM_ARCHITECTURE_V2.md:210-227`（含“不可违反的阶段约束”与“不设自动例外”）；`knowledge/standards/rules-registry.md:44`（R-BST-SW 的表述）
- 阶段集合来自 `tm108-test-method-contract.md` §3 的 P0–P8，与之一一对应，无阶段被跳过。

## 1. 结论（一句话）

**9/9 阶段均为 定点补证（未证实）**：在签名边界 `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` 内，
BST 与 SW **既不是 TM108 的端点**，**也没有任何源表分配**，**也没有任一继电器组在其上有必需状态**；
因此 `BST_actual` 与 `SW_actual` 都无法从“实际闭合继电器 + 短接 + 功能状态 + 已驱动节点”导出。
`SW_actual` **明确不取 0 V**（架构 :212-224 禁止该默认），因此不构成“BST−SW ≤ 5 V 成立”的结论。
待闭合项 **OI-T5-02**；需要边界补证的部分已作为 **RT-2** 退回 test-strategy-architect。

## 2. SW_actual 的推导链（逐条，非默认值）

| 步 | 事实 | 来源 | 对 SW_actual 的作用 |
|---|---|---|---|
| 1 | TM108 端点集合 = VAC1（被扫描）、VBAT（供电）、观测候选、AGND（仅板级参考）；**无 BST/SW** | 契约 md :94-101 | SW 不是本项的端点，方法不需要驱动它——但这也意味着方法**无法观测**它 |
| 2 | TM108 的 5 条资源分配只落在 `VAC123_AMUX_ACM S5_0`、`VBAT_PD3_FXVI S3_5`、`NQON_HG1_ACM S5_9` | 契约 md :133-139（RA-1..RA-5） | 没有任何源表接到 SW 节点 |
| 3 | 本项实际动作的闭合集 = `{13, 65}`（VBAT 稳压电容门 + 观测上拉），K17 另需处于闭合态 | 契约 md :192-252 | 这两个继电器都在 VBAT / 观测支路，与 SW 无触点关系（`project/DALI/SCH-Connect-Map.txt:891`、`:914`） |
| 4 | 依赖默认导通的触点 = `K8 / K18 / K19 / K64`；四者都不动作 | 契约 md :220-222、:247 | 其触点在 VBAT、VAC1、nQON 三条链上；SW 不在其中 |
| 5 | 观测器候选链 `S5_ACM200_FH9 → K64(pin6→7) → NetK64_HG1_S1_7`；而 HG1 侧需要 K64 动作 | tm108-paths-proofs.txt:170-173、:196；契约 md :298 | **K64 保持未动 ⇒ 高边栅极域（HG1）不被测试机接入**；这是本项唯一“可能接触高边域”的继电器，且被契约关闭 |
| 6 | SW 节点在板上有通路（ACM200 ch8 `S5_ACM200_FH8/SH8` 经 `K61_SW`；K61 在同一文件里是双态继电器，IR 单值取 NC） | `setup-contract.json:144`、`:371`；`tm108-consistency-check.txt:109`、`:173` | K61 不在本项闭集、也不在契约的 keep-open 列表 → 其状态**未由签名契约赋予**（`RT-2`），不能据此推断 SW 的电位 |
| 7 | BST 节点在板上有通路（baseline 形式 `S5_ACM200_FH5 → K48 → K76 → BST_F/S`；并存形式 `S5_ACM200_FH18 → K110 → BST`，以及 CH1 Low `K109+K110`），均需 K48/K76/K109/K110 等动作 | `tm108-connectmap-ranges.txt:16-21`、`:83-91`；`setup-contract.json:145`、`:149-153` | 这些继电器的状态同样未由签名契约赋予 → BST 电位不可导出 |
| 8 | BST↔SW 之间只有 **220 nF 自举电容门 `K57_CAP_BST_SW`**（`SW 稳压 Cap_SW_BST_S1 C=220nF 需闭合: K57`） | `project/DALI/SCH-Connect-Map.txt:904`；`setup-contract.json:3941`、`:8156`（K57 被列为“本项需要的稳压电容门”的**条件候选**，同时被明确归入“不出现在任何 `required_on`、必须按功能规则给状态”的 PIN 附着继电器） | **签名契约既未闭合 K57、也未把 K57 放进 keep-open 列表** → 这是本边界唯一可能触及 BST-SW 对却状态不明的元件（`RT-2`）；按“不在签名闭集内即不动作”，本方法**不闭 K57** |
| 9 | 芯片内部的开关级（低边/高边导通、SW=PGND 或 SW=PMID）由 DFT 意图、寄存器 delta 与闭集**都未承诺** | 契约 md :256-267（delta 只有 entertestmode + DMUX 两字段）；dft-fact-audit.md :227-231 | SW 的实际电位取决于该内部状态；**不可用“SW=0 V”替代**（架构 :222-224 明令禁止） |

**推导结论**：`SW_actual` 在本边界内**不可导出**；`BST_actual` 同理。因此“0 V ≤ BST_actual − SW_actual ≤ 5 V”**不能**被声明为满足，
按架构 :216-227 的处置：该阶段**登记为定点补证**（而不是继续排布该阶段的电气动作）。本契约对 P1–P8 的电气设计均**不依赖** BST/SW 的数值，
故列表自身仍可执行；但**该约束的证实责任不得被静默丢弃**，已作为 `OI-T5-02` 与 `RT-2` 挂账。

## 3. 逐阶段检查表

| 阶段 | 阶段名 | 该阶段实际闭合/状态 | BST_actual | SW_actual | 0 ≤ BST−SW ≤ 5 V | 结论 | 定点补证原因 |
|---|---|---|---|---|---|---|---|
| P0 | pre-state | 无（未进入任何组） | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | no source allocated to BST/SW; switching stage not committed by the DFT; SW deliberately not taken as 0 V |
| P1 | closure of the signed functional relays | {13, 65} + K17 闭合态 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | no allocated source; no required state for K48/K76/K61 in the signed closure set; K57_CAP_BST_SW state ambiguous (RT-2) |
| P2 | VBAT power-on | {13, 65} + VBAT 源使能 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | VBAT is a rail pin; the switching stage is not enabled by TM108's register delta (only DMUX_EN/DMUX_SEL), and no tester source drives BST/SW |
| P3 | register activation | {13, 65} + 寄存器 delta 生效 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | the delta contains no driver/switching enable; a BST/SW state still cannot be derived, and BST/SW remain unreachable by any closed relay |
| P4 | rising sweep (measure) | {13, 65} + VAC1 升扫 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | the swept chain (VAC123_AMUX_ACM -> K18 -> K19 -> VAC1_F) is disjoint from every BST/SW route; the internal high-side/low-side commitment is not part of the DFT intent, so neither node's potential is derivable |
| P5 | hold at the sweep end / turn-around | {13, 65} + VAC1 折返保持 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | same as P4; no relay action occurs at the turn-around, so no new BST/SW coupling appears |
| P6 | falling sweep (measure) | {13, 65} + VAC1 降扫 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | same as P4; a falling input sweep does not couple to the BST-SW pair through any closed contact of G1/G2 |
| P7 | power-down step 1 (zeroing) | {13, 65} + 三源归零 | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | the collapse ordering rule for BST-SW applies only to items that drive BST; here the rail collapse cannot be shown to keep any BST/SW relation, so the constraint stays unproven |
| P8 | power-down steps 2-3 (release + safe end state) | 释放（无闭合） | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | after release no node of this item is driven; BST/SW end state is again DUT-internal and unevidenced in this boundary |

## 4. 参考：板级 BST/SW 相关事实与本项的关系（只读证据）

| 事实 | 证据 | 与 TM108 的关系 |
|---|---|---|
| BST 通道族属于 ACM200 ch5（`SW12_U1REF_BST_ACM`），baseline 路线 `K48 + K76`；并存 `K110`（PB0_BST_ACM / ch18）与 `K109+K110`（CH1 Low）路线 | `setup-contract.json:145`、`:149-153`；`tm108-connectmap-ranges.txt:16-21`、`:83-91` | 均在签名闭集之外；本项不选、不闭 |
| SW 节点的测试机通路经 `K61_SW`（ACM200 ch8，`S5_ACM200_FH8/SH8`） | `setup-contract.json:144`；`tm108-consistency-check.txt:109`、`:173`（K61 双态，IR 单值 NC） | 未由签名契约赋状态（`RT-2`） |
| BST↔SW 自举电容 220 nF，门控继电器 `K57_CAP_BST_SW` | `project/DALI/SCH-Connect-Map.txt:904`；`setup-contract.json:3941`、`:8156`（PIN 附着继电器不出现在任何 `required_on`，必须按功能规则给状态） | 唯一可能触及 BST-SW 对的元件；状态不明 → `RT-2` |
| 平台级差分要求原文（E006：`BST must lead PMID/SW by >=5 V` / 自举电容不得反偏；两个措辞都被登记而非平均） | `setup-contract.json:8161`；`rules-registry.md:44`（0≤BST−SW≤5 V，目标 5 V） | 用于确认本约束的**表述**；该条目的作用域是 Current-Threshold/ZCD 类（带自身拓扑指纹与专用门禁脚本），**不**把 TM108 所属家族归入该类 |
| 低端/高端回路（FXVIe_PLUS 与 ACM200 的 Low 端）分组接 `AGND_F` | `project/DALI/SCH-Connect-Map.txt:801`、`:804` | 说明单端 force 的电流回路；与 BST/SW 无触点关系 |

## 5. 该结论的下游后果（明确写出，避免被误读）

- 对**实现者**：不得为了“让 BST−SW 检查通过”而新增任何继电器动作或源表设置；本项不存在该检查所需的资源（架构 :216-227 的例外只能由用户裁定）。
- 对**校验者**：审查时应核对每一阶段都带有本检查的结论（9/9），而不是核对一个数值；若下游要求 BST−SW 的**数值**，只能先闭合 `OI-T5-02` / `RT-2`。
- 对**策略侧**：若 TM108 必须给出 BST/SW 的实测证据，则需补：BST/SW 端点与源表分配、其继电器必需状态、以及 K57 的显式状态（`RT-2`）。
- 不得把本文件读成“TM108 无 BST/SW 风险所以无需检查”的结论——本文件的结论是**未证实**，不是“无风险”。

