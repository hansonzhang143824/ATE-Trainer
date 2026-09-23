# TM600/TM601 决策板（Captain 证据汇编，等专家接管）

> 时间：2026-09-16 22:3x +0800 ｜ 性质：**证据与来源汇编 + 待裁定项，不含电气裁定**。
> 来源分层：`[C]` = Captain 本会话直接实测；`[S]` = 独立子代理报告（同模型路由，未逐行复核）；`[F]` = 冻结件现值（`snapshot/`）。
> 用途：给 `t1/t2/t6/t7` 一个现成的事实基线，并给用户四个待裁定项一个可比较的形式。**本文件不替代任何专家产物，也不构成机电/电性结论。**

## 1. 新版 DFT 逐字段提取表 `[C]`

工作簿：`project/DALI/Dali_testmode.xlsx` = 12,210,680 B / `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` @21:46:39（sheet `OVERVIEW`，header row 1）。

### TM600（row 132，逐格地址）

| 地址 | 列 | 值 |
| --- | --- | --- |
| A132/B132/C132 | Item/Level/Name | `TM600` / `BUBO` / `HS_RDSON` |
| D132 | Description | `high side powerfet rdson` |
| E132/F132/G132 | ExpectValue/Unit/Test | `11` / `mΩ` / `direct` |
| H132 | Special | `Y\n2 FLOAT` |
| I132 | Purpose | `SCM` |
| K132 | Notes | `Rds,on=(PMID-SW)/ISW` |
| L132 | Code1 | `vset[vbat,3.5,100e-6,0]` ⏎ `vset[pmid,5,100e-6,0]` ⏎ `vset[bst_sw,5,1e-3,0]` ⏎ `vset[vdrv,5,100e-6,0]` |
| M132 | Code2 | `en_tm[]` ⏎ `field[(WAKE_UP,1)]` ⏎ `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]` |
| N132 | Code3 | `delay[1e-3]` ⏎ `iset[sw,1,1e-3,0]` ⏎ `delay[2e-3]` ⏎ `finish[]` |
| O132 | Power | `VBAT\nBST-SW` |
| P132 | Dynamic | `ISW` |
| Q132 | Check | `PMID-SW\nfloating source：V(BST_SW)` |
| R132 / U132 / AJ132 | isCodeGen / AMS / is test | `Y` / `Done` / `checked` |
| AH132 | de test | `I=0.2A\npmid-sw=46mV`（**DE 调试列，非限值**） |

### TM601（row 133，逐格地址）

| 地址 | 列 | 值 |
| --- | --- | --- |
| A133/B133/C133 | Item/Level/Name | `TM601` / `BUBO` / `LS_RDSON` |
| D133 | Description | `low side powerfet  rdson`（原文双空格） |
| E133/F133/G133 | ExpectValue/Unit/Test | `7.5` / `mΩ` / `direct` |
| **H133** | **Special** | **空**（TM600 有 `Y\n2 FLOAT`，TM601 无） |
| I133 | Purpose | `SCM` |
| K133 | Notes | `Rds,on=(SW-PGND)/IPMID2SW` |
| L133 | Code1 | `vset[vbat,3.5,100e-6,0]` ⏎ `vset[vdrv,5,100e-6,0]` ⏎ `vset[vbus,5,100e-6,0]` ⏎ **`vset[bst,5,100e-6,0]`** |
| M133 | Code2 | `en_tm[]` ⏎ `field[(WAKE_UP,1)]` ⏎ `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]` |
| N133 | Code3 | `delay[5e-3]` ⏎ `iset[pmid_sw,1,1e-3,0]` ⏎ `delay[2e-3]` ⏎ `finish[]` |
| O133 | Power | `VBAT`（**不含 BST / BST-SW**） |
| P133 | Dynamic | `SW\nISW` |
| Q133 | Check | `SW-PGND\nfloating source：I(PMID_SW)` |
| R133 / U133 / AJ133 | isCodeGen / AMS / is test | `Y` / `Done` / `checked` |
| AH133 | de test | `I=1A\nSW-PGND=0.3`（**无单位**，非限值） |

**与本轮改动的对照 `[C][S]`**：以旧版见证 `dft-raw/overview-dft.json`（自记 `sha256=d9d721a3…`）为准，**TM600 row 132 逐字段未变**；**TM601 `L133` 由 3 行变 4 行，新增 `vset[bst,5,100e-6,0]`**。全工作簿 `vset[bst,` 仅 1 处、`sw2pgnd` 0 处、`FPVI/ACM/FOVI/FXVIe` 各 0 处 `[C]`。

## 2. 与激励回路有关的既有事实（只引证据，不重推）

### 2.1 DFT 侧的回路命名 `[C]`
- `iset[pmid_sw,…]` 在本工作簿是**通用回路名**，出现在 TM601、TM605、TM609（`iset[pmid_sw,-2,1e-3,0]`）等行；`Check` 里的 `floating source：I(PMID_SW)` 亦见于 TM605/TM608/TM609/TM627。
- 因此 **`PMID_SW` 是回路/仪器通道名，不等于回路端点对**。TM601 的端点对由 `Check=SW-PGND` 与 `Notes=(SW-PGND)/IPMID2SW` 表述。

### 2.2 冻结契约里的三条路线 `[F]`（`snapshot/setup_contract.json`，revision 36）

| 路线 | 仪器 | 高端节点 | 低端节点 | 需闭合 | 引用者 |
| --- | --- | --- | --- | --- | --- |
| `pmid2sw` | FPVIe0 (S1_0)，FH0/SH0 / FL0/SL0 | **PMID** | **SW** | `[83, 60, 61]` | TM600 |
| `sw2pgnd` | FPVIe0 (S1_0)，FH0/SH0 / FL0/SL0 | **PGND** | **SW** | `[154, 155, 60, 61]` | TM601 |
| `bst2sw` | `SW12_U1REF_BST_ACM`（ACM200，宏 `S5_5…`，`Pin_Channel_define.h:20`） | BST | SW | `[48, 60, 61, 76]` | `TM600 (BST must lead PMID)` |

- `closedRelayNumbersByRoute` 按通道分列：`acm200_ch5_bst=[48,76]`、`acm200_ch5_sw=[60,61]`、`acm200_ch5_bst_sw_closure=[48,60,61,76]`、**`acm200_ch18_pb0_bst=[110]`**（含 locator `SCH-Connect-Map.txt:672-674`、`IR accepted_path_proofs[S5_ACM200_FH5/SH5 → BST_F/S].required_on=[48,76]`、行为层 `test.cpp:6997/7000/7085/7087/7170/7513`）。
- **TM601 在冻结契约中没有任何 BST 供电源登记**：`bst2sw.usedByTm` 只写 TM600；`tmDeltas.TM601.scopePins` 无 BST、`relaySet` 不含 `48/76/110`。

## 3. 四个待裁定项（并列证据 + 选项对比 + 推荐）

### A. TM600 操作点：`PMID=5 V` 还是 `15 V`

| 侧 | 原文与出处 |
| --- | --- |
| 新版 DFT | `vset[pmid,5,100e-6,0]` + `vset[bst_sw,5,1e-3,0]`（`L132`）`[C]` |
| 规则/黄金 | `voltage-inference.md:18 PMID_FOVI.Set(FV, 15) → PMID = 15V`；`:142 DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]`；`:151-160` 台阶表以 PMID=15 / BST=20 推演 `[C]` |
| DFT.csv | `vset[vbat,4.2]` + `pmid=15` 系（与 `.sv` 的 `3.5` 亦冲突）`[S]` |

| 选项 | 优 | 缺 | 成本 | 可逆性 |
| --- | --- | --- | --- | --- |
| **A1（推荐）以新版 DFT `PMID=5 V` 为准**，`voltage-inference.md` 标注「历史示例/适用域：另一代际或另一操作点」 | 与「修改后 DFT 唯一权威」一致；`Check=V(BST_SW)` 在该组合下自洽（BST−SW=5 V 由 ACM 地参考通道直接设定） | 与知识库正式示例冲突，须显式写适用域，否则后续会再犯 | 低（改计划内登记） | 高（仅标注，不改字节） |
| A2 以 15 V 为准 | 与知识库示例一致 | **与用户裁定的唯一权威直接冲突**；须用户另出裁定 | 低 | 高 |
| A3 并列登记不裁定 | 不担责 | 阻断实现（`t7` 无法选额定值/量程） | 中（延后） | — |

### B. TM601 的 `vset[bst,5,…]` 语义：BST 对 GND，还是 BST−SW=5 V

| 读法 | 支持证据 | 反对/缺口 |
| --- | --- | --- |
| **B1「BST 单端轨 = 5 V（对 GND）」** | DFT 写的是单引脚 `vset[bst,…]`（TM600 差分写法是 `vset[bst_sw,…]`）；row 133 `Power=VBAT`，未把 BST-SW 列为供电/监测对；`Check` 只监测 `I(PMID_SW)`，**不监测 `V(BST_SW)`** `[C]` | LS 导通时 SW≈0.3 V（`AH133`）⇒ BST−SW≈4.7 V，**不是 5 V**；而 Notes 要测的是 SW—PGND，与 BST 无直接关系 |
| **B2「实际要求 BST−SW=5 V」** | 用户口述的 TM601 要求即写「BST−SW=5 V、BST=5 V」；FET 导通需要自举电压 | 工作簿**没有** `bst_sw` 行、`Power` 不含 BST-SW、`Check` 不含 `V(BST_SW)` ⇒ 工作簿**未把它写成差分对** `[C]` |

**共同事实**：`tm601.sv` 全文无 `bst` token `[S]`；`voltage-inference.md` **没有 TM601 章节** `[S]` ⇒ TM601 无法从知识侧获得裁定。**需 owner**：schematic 给物理事实（BST 节点能否被地参考源驱动、与 SW 的关系），strategy 给操作点。

### C. TM601 的 BST 供电源在契约中缺失（`t6` 必办）

- 冻结契约 `bst2sw.usedByTm` 只有 TM600；TM601 无 BST 资源登记 `[F]`。
- 若 B 结论需要 BST=5 V 或 BST−SW=5 V，则 `t6` 必须新增 TM601 的 BST 供电源（含通道/闭集/locator 与互斥），否则 `t7` 会退回。
- 同时 `t6` 必须处置 **BST 节点多源**：`K76.pin4` 与 `K110.pin4` 同网（多路源汇入 BST），`ch5` 三目的地互斥 —— 这是用户点名要单独复审的部分。

### D. TM600 与 TM601 能否共享同一批 PHP/SW/BST 端点

- 同族证据：`sw2pgnd` 与 `pmid2sw` **共用 FPVIe0 S1_0 的同一对低端腿** `[60,61]`，高端分别为 `[154,155]`（PGND）与 `[83]`（PMID）`[F]` ⇒ 两条回路**不能在同一个 site 同时成立**（一次只能选一条高端腿）。先后执行可行，需 `t2/t6` 明确互斥与释放顺序。
- 已部署先例：`cbite.SetOn` 是**排他**操作（每次调用只闭合括号内继电器）⇒ 逐函数完整闭集可避免跨项泄漏；但「显式 `RELAY_OFF` 共驱仪器」在 `TM641` 有先例（`test.cpp:7598` 注释）`[F, 出处见冻结契约 locator]`。

## 4. 专家接管时各自需要的最小输入

| 任务 | owner | 需要的最小输入 |
| --- | --- | --- |
| `t1` 重提取 | dft-expert | 本表 §1 + `inputs/t1-input-diff-new-dft.md`；须自行复算哈希并登记旧 IR 的「无 force」欠提取缺陷 |
| `t2` 物理核实 | schematic-expert | 本表 §2 + 冻结 `schematic-ir.json`(9f4a7707…) + `SCH-Connect-Map.txt`；须回答：BST 可被哪些源驱动、SW 到底是「回路端点」还是「仪器通道名」、`sw2pgnd` 与 `pmid_sw` 的节点差、ch5 三目的地互斥、多源汇聚的释放配对 |
| `t6` 契约修订 | setup-architect | §2 + `t2` 结论；须按通道分组、新增/更正 TM601 BST 资源、登记待裁定项 |
| `t7` 策略 | test-strategy-architect | 上述全部 + 裁定结果；须逐阶段给出资源/寄存器/测量/下电/日志 |
| `t8` 独立审查 | rule-reviewer | 被审字节 pin；须独立重推 ch5 位置与闭集，禁止沿用旧 IR 断言 |

## 5. 边界

`devel` 零写入；目标树 `ForCodexDebug/source/test.cpp` = 469,714 B / `15c7d2b8…36c01a` 未落盘；**未做任何机台/电性验证**；本文件不含电气裁定，也不替代 `t8` 独立审查。
