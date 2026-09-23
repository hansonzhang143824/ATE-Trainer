# setup-recon — t3 前置侦察（setup-architect，只读，未认领 t3 时预置）

> 状态：t3 仍被 t2 阻塞时完成。本文件是**侦察笔记**，不是 t3 交付物；t3 交付物为
> `setup-contract.json`（schema：`team/schemas/setup-contract.schema.json`）。
> 所有结论均标注「实测」或「来源」，未实测项显式标 UNKNOWN。

## 1. DFT 路径别名（本次十项 TM 相关）

实测：`project/DALI/input/DFT.csv` 计数 `pmid2sw`=10、`pgnd2sw`=9、`bst2sw`=9、`sw2pgnd`=4；
`sw2bst`=0（`bst2sw` 才是既有写法）。

第一来源（DFT 行内 sense-path 标签列，机读，**优先于 BFS**）：

| 行号 | 向量 | sense-path 标签 | Check 类型 |
|---|---|---|---|
| DFT.csv:97 | `iset[pmid2sw,1,1e-3,0]` | `PMID-SW` | MV&MI |
| DFT.csv:104 | `iset[sw2pgnd,1,1e-6,0]` | `PGND-SW` | MV&MI |
| DFT.csv:92/125/137/150/164/175/213/251/285 | `vset[bst2sw,5,1e-3,0]` | `BST-SW`（vset，非大电流） | MV |
| DFT.csv:116 | `iset[sw2pgnd,0.5,1e-3,0]` | — | — |
| DFT.csv:121-122 | `iset[pgnd2sw,0.5,0,0]` / `iset[pgnd2sw,-0.1,1e-3,0]` | `INT` | Toggle, MI |
| DFT.csv:154/161/172 | `iset[pmid2sw,3,…]` / `iset[pgnd2sw,3,…]` / `iset[sw2pgnd,3,…]` | `AMUX-NTC` | MV |

→ 别名→节点对：`pmid2sw` = PMID↔SW；`sw2pgnd` = SW↔PGND；`pgnd2sw` = PGND↔SW（与 `sw2pgnd`
同名对反方向）；`bst2sw` = BST↔SW。**方向/极性不能由别名推断，必须与 sense-path 标签 +
Check 列共同判定。**

交叉来源：`knowledge/hardware/voltage-inference.md:98`（`iset[PMID2SW,1A] → PMID ≈ SW，压差 = I×RDSON，
通常 <100mV`）、`:143`；`knowledge/hardware/bus-topology.md:278`（`vset[bst2sw]` + `iset[pmid2sw]` 共存）；
`knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:16`（FPVI 唯一 → 大电流
`iset[PMID2SW,1A]` 占 FPVI_BUS；BST−SW 降级双独立源）。

旧代际 K 名换算（golden 内 `K31_VBUSL_PMID`、`K17_BUSH_SW`、`K18_BST_SW_Cap`、`K30_VBAT_Cap`、
`BTST_ACM`、`PMID_FOVI` 在 `test.cpp`/`StdAfx.h` **实测 0 命中**）→ 必须换算到现行 K 名，
换算表来源：`project/DALI/SCH-Connect-Map.txt`（组头「需闭合:」）+ `gen_paths.py --json`。

风险注记（历史错误，必须按 TM 与 sense-path 交叉校验）：`knowledge/claude-history/absorbed/34-b55b4f8d.md:58/83`
记录 TM607 的 meta/`IPMID2SW` 是 **DFT 错误**（真实路径 SW↔PGND，用户裁定"按照 SW 和 PGND"）；
另有 `pmid_sw` / `sw2pmid` 变体命名（见 `knowledge/claude-history/sessions/26-37eaa5d8.md:12/64`）。

## 2. 通路生成器（工程既有脚本，勿自造）

- `scripts/gen_paths.py`（实测：python 3.12.5，`--audit-rules` → P-P1..P-P11 ALL PASSED）。
- CLI：`--config`（默认工作区根 `project_config.json`）、`--netlist`（默认
  `project/DALI/CSV_CONNECTIVITY.NET`）、`--cbit`（默认 `project/DALI/CBIT表-DALI.xlsx`）、
  `--output <file>`、`--json`、`--max-depth`（默认 6）、`--audit-rules`。
- 输出语义（源码 `:812-826`）：人类可读文档 → stdout（给 `--output` 则落文件）；`--json` 把
  `path_list` JSON **追加到 stdout**，前置一行 `===== PATH_LIST JSON =====`。
  → 落两个文件：`sch-paths.txt`（`--output`）+ `sch-paths.json`（剥 marker 后的纯 JSON）。
- 结构化元素（`:291-292`）：`{dut_pin, source, side, via_relays[], intermediate_source}`，
  `via_relays` 元素 `{name, cbit, type, state, annotation}`（`:275`）。
- `project_config.json` 位于**工作区根**（实测），非 `project/DALI/`。其
  `intermediates.paths_txt = "project/DALI/paths.txt"` **文件不存在**（实测），其余 5 个中间产物存在。

## 3. 仪器 API（权威来源：SDK 头文件，实测路径）

`F12011.vcxproj` 的 `AdditionalIncludeDirectories = C:\AccoTEST\AccoTEST System\INCLude`。
实测该目录含 `FPVIe.h / FXVIe.h / ACM200.h / FOVIe.h / UserRes.h`。

| 事实 | 证据（实测） |
|---|---|
| `SetClamp` 存在且可调用 | `FPVIe.h:101 int SetClamp(double percent_PFS, double percent_NFS);`；`FXVIe.h:117`（FXVIe）、`FXVIe.h:458`（FXVIe_PLUS） |
| `FPVIe_IRNG` 含 10 A / 2 A | `FPVIe.h:17 enum FPVIe_IRNG` → `:19 FPVIe_10A`、`:20 FPVIe_2A` |
| `FXVIe_PLUS_IRNG` 封顶 1 A | `FXVIe.h:348 enum FXVIe_PLUS_IRNG` → `:350 FXVIe_PLUS_1A`（无 2A/10A） |
| `Set` / `MeasureVI` / `GetMeasResult` | `FPVIe.h:89/:97`、`:104`、`:114` |

**更正（自我撤回）**：先前"`SetClamp` 在 `D:\PROJECT6-DALI` 全树 0 命中 ⇒ 本代无 clamp"
的说法**不成立**——该 0 命中是我把扫描根限制在项目树（`ForCodexDebug` / `devel`）造成的
**扫描范围限制**，不是"不存在"的证据。SDK 头在 `C:\AccoTEST\...`，项目树里自然没有。
正确表述：`SetClamp` 在 **SDK 中存在**，在**本项目自有源码**中 0 次使用。
同样注意 `team/EXECUTION_PLAN.md:81/129` 记载的"本代无 SetClamp（全文件命中 0）"属**范围误导**，
与 `RUN-LEDGER.md:220-222` 的正确版本冲突，应以本条为准。

`SetClamp` 语义（来源 `knowledge/sources/fpvie.md:141-168`，SDK 手册镜像）：参数为**满量程百分比**
（正/负），且**切换 FV/FI 模式会清除箝位并回到 100%/102%** → 每次模式切换后必须重新下发。
数值来源仍缺（BD-05），**不得自造限值**。

## 4. 限值口径（BD-01，用户裁定：以 OVERVIEW 为准）

| TM | OVERVIEW | DFT.csv | 裁定 |
|---|---|---|---|
| TM600 (HS_RDSON) | `11 mΩ` — `project/DALI/_archive/_dump_OVERVIEW.txt:981` | `10 mohm` — `DFT.csv:90` | **11 mΩ**（DFT 为已登记冲突） |
| TM601 (LS_RDSON) | `7.5 mΩ` — `_dump_OVERVIEW.txt:994` | `8 mohm` — `DFT.csv:98` | **7.5 mΩ**（DFT 为已登记冲突） |

附注（实测）：`_dump_OVERVIEW.txt:994` 的 TM601 公式写作 `Rds,on=(SW-PGND)/IPMID2SW`，
而同一行 alias 相关的 DFT 行是 `sw2pgnd`——与第 1 节的历史 `IPMID2SW` DFT 错误属同一类，
**须按 sense-path 标签（PGND-SW）为准并登记分歧**。

## 5. 上下电铁律（原文来源 `knowledge/standards/rules-registry.md`）

- `:32 R-PON`：vset→FV / iset→FI；MV 无 FI→FI=0+最小量程 10UA；浮动源三阶段 ≤5 V；
  **大电流三段式 FV=0→FI=0→Clamp→FI**；小电流两段式按 PIN 类型（power 100MA / digital 10MA /
  ATEST 直接测量量程）；量程 ≥2× 取最小档；FPVI 等电位。
- `:33 R-POFF`：类型判定；普通三步（归零→`delay_ms(1)`→`RELAY_OFF`）；浮动反转台阶；
  **FPVI 最后 RELAY_OFF**；大电流 `FI=0→FV=0→OFF`；`RELAY_OFF` 统一量程（**FPVI 用 1V/10MA 非 10A**）。

## 6. 未决项（写契约时显式保留，不自造）

- **BD-05**：clamp/compliance 数值无来源（机制见第 3 节）。
- 现行 K 名换算表：待 `gen_paths.py --json` 结果落到 `sch-paths.json` 后逐别名填实。
- `tmDeltas` 中每个别名的 (force 仪器, relay path 名, K 号集合, 方向/极性) 三元组将在 t3 完成。
