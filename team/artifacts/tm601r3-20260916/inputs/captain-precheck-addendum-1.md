# Captain 预检补遗 1：折叠验证子代理的差异证据，并更正预检的两处措辞

> 时间：2026-09-16 22:2x +0800。本文件**不改写**已冻结的 `captain-precheck-new-dft.md`（6,671 B / `c2b859aa…ca3d0`），只作补遗，避免再次哈希漂移。
> 来源分层：**Captain 实测**（本文标注者）＝本会话直接跑 Python 得到；**子代理报告**＝独立子代理 `8da92d00…`（同一模型路由 deepseek-v4-flash）产出，路径 `inputs/t1-input-diff-new-dft.md` = 43,172 B / `109f7f3f104c2c3f5aeda04851d3e9cbc60f8b5ae3e95bf36e98e898b01afb36`（其自报值，未由我方逐行复核）。

## 1. Captain 独立实测的确认项（FACT）

对新版工作簿 `f4bbb856…9564` 全 sheet 逐格扫描：

| token | 命中数 | 命中位置 |
| --- | --- | --- |
| `sw2pgnd` | **0** | 全工作簿无 |
| `pmid_sw` / `PMID_SW` | 6 / 5 | `OVERVIEW:133,137,140,141,149` |
| `bst_sw` | 24 | `OVERVIEW:132`（**不含 133**）等 |
| `BST-SW` | 15 | `OVERVIEW:132` 等、`InitialDFT_Check:8` |
| `vset[bst,` | **1** | **仅 `OVERVIEW:133`** |
| `vset[pmid,` | 39 | `OVERVIEW:132,134,135,136,138,139…` |
| `FPVI` / `ACM` / `FOVI` / `FXVIe` | 0 / 0 / 0 / 0 | 全工作簿无仪器族名 |

**结论**：① `iset[sw2pgnd,…]` 只存在于 `input/DFT.csv`，**新版工作簿完全不用该 token**；② `vset[bst,5,…]` 是全工作簿唯一一条，且只出现在 TM601 行；③ DFT 层**不给任何仪器族名**，「FPVI 供 SW—PGND」属下游由物理通路推出的选择，不是 DFT 事实。

另：旧提取见证 `acceptance-20260916-dali10/dft-raw/overview-dft.json` 自记 `overview.sha256 = d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e`（**Captain 实测**），与旧 `dft-ir.json` 记录的 xlsx 哈希一致 ⇒ 该文件确实保存着**旧版**工作簿的 OVERVIEW 文本，可作为「旧版是否已含 bst」的判定见证。

## 2. 更正预检的两处措辞

| 位置 | 预检原文 | 更正 |
| --- | --- | --- |
| 预检 §3 表格「是否含『无 BST』字样」行 | 含糊（只说旧推断在下游） | **旧 `dft-ir.json` 自身还断言过 OVERVIEW rows 132/133「no force value / no force at all」**（子代理定位：`conflicts[0].forceMagnitudeDisambiguation`、`items[8].forceAndSense.force.authorityChain.overview`）。据旧版见证文本，该断言**对旧版即已为假**（iset 行当时已存在）⇒ 属**旧 IR 的欠提取缺陷**，不是工作簿变化 |
| 预检 §4 D3 表 | 把三方并存写成「待 t1 归口」 | 其中**新版工作簿一侧是确定的**：只用 `pmid_sw`，不用 `sw2pgnd`；`sw2pgnd` 与 `iset[sw2pgnd,1,1e-6,0]` 只存在于 `DFT.csv`（旧派生输入） |

**不变的部分**：`OVERVIEW!L133` 的 `vset[bst,5,100e-6,0]` 是**真实新增**（旧版见证中该行 Code1 为 3 行，新版 4 行；且 `tm601.sv` 全文无 `bst` token）。TM600 row 132 在可比字段上**逐字段相同**。

## 3. 仍需 owner 裁定/核实（不因补遗而减少）

1. **TM601 激励对与极性**：工作簿写 `SW-PGND` + `I(PMID_SW)`，**不给极性**；旧 `CR-03` 曾把 `.sv` 的 `PMID_SW` 记法判为 superseded，而新 DFT 又把该记法写回来 ⇒ 由 schematic（物理极性事实）+ strategy（操作点）收口。
2. **`vset[bst,…]` 语义**：BST 对 GND 还是 BST 对 SW（工作簿无 `bst_sw` 行、100 µs ramp 亦与 TM600 的 1 ms 不同）。
3. **三套轨值不一致**：工作簿（TM601 `3.5/5/5/5`；TM600 `3.5/5/5/5`）vs `knowledge/hardware/voltage-inference.md:142-143`（TM600 `vbat 4.2, pmid 15, bst2sw 5`，BST=20 V）vs `DFT.csv`（`4.2/15`；`4.2/9`）。**`voltage-inference.md` 没有 TM601 章节** ⇒ TM601 无法从知识侧获得裁定，只能由物理事实 + 用户裁定。
4. **1 A 的 compliance/clamp**：三处输入均未给值，仍为 UNKNOWN。
5. **范围限制**：新版工作簿 250 行中仅 14 行可与旧版逐格比较，其余行的差异状态 = UNKNOWN（不主张「只有一格变了」超出该 14 行范围）。

## 4. 对 DAG 的影响

**任务数与依赖不变**（9 任务 / 依赖 8），但本轮证据已具名落入 `t1`（重提取并登记欠提取缺陷）、`t2`（极性/物理通路/共享互斥）、`t7`（BST 语义与三套轨值的对账）、`t8`（独立审查时禁止沿用旧 IR 的「无 force」断言）。**无需新增任务**：上述第 3 项中的用户裁定项，若你给出裁定即在 `t6/t7` 内落为登记条目。

## 5. 边界

`devel` 零写入；目标树 `ForCodexDebug/source/test.cpp` = 469,714 B / `15c7d2b8…36c01a` 未变；**无机台/电性验证**；本补遗不构成电气裁定。
