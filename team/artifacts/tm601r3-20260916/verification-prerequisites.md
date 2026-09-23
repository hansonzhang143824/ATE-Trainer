# 验证前置：复核拦截清单 + 解锁后第一批可执行校验

> 时间：2026-09-17 00:2x +0800 ｜ 用途：给 `t2/t6/t7/t8/t11` 一份**直接可执行**的检查清单，避免解锁后再花时间摸索；同时把本轮所有可疑点具名拦截，防止它们流进实现层。
> 本文只读汇编；不含电气裁定；不影响任何 pin（`snapshot/` 冻结件仍为唯一输入）。

## 1. 已由本轮实测确立、可被直接引用的判据

| 判据 | 命令/位置 | 期望/已观测 |
| --- | --- | --- |
| 门禁契约闭集通道 | `python scripts\verify_bst_sw_sequence.py --src <全量源> --contract <契约>` | 必须出现 `[t30] TM600_HS_RDSON …` 与 `[t30] TM601_LS_RDSON …` 两行；`[scan] targets=N`（N>0） |
| 假绿陷阱 | 同上，`--src` 指向**只含增量**的文件 | 输出「空 PASS」exit 0 ⇒ **记为未执行** |
| 部署态缺腿 | 同命令（`--src D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp`，契约 = `snapshot/setup_contract.json`） | 已观测：TM600 期望 `[48,60,61,76,83]` 缺 `[48,76]`；TM601 期望 `[60,61,154,155]` 缺 `[]`；exit 1 |
| 期望集来源 | `verify_bst_sw_sequence.py:261-263` `CONTRACT_RULE_NOTE` | 只认 `aliasResolution[*].resolution.closedRelayNumbers`（按 `usedByTm` / `tmDeltas.<TM>.aliasesUsed` 索引）；`pinRouteTable`/`relaySet` 仅 locator |
| 作用域 | 同文件 `:259 DEFAULT_TM_SCOPE` | `["TM600_HS_RDSON","TM601_LS_RDSON"]`，可被 `--tm-scope` 覆盖 |
| R-BST-SW 上限 | 门禁 stdout `[contract] BST>=SW and 0<=BST-SW<=5V`（`:545`） | 任何阶段 BST−SW > 5 V 即违规 |
| 继电器语义 | `knowledge/hardware/relays.md:95-99` | BUS 释放=不通；Share 释放=通默认通道；**K46~K59 列为 MOS P2P 默认断开**（与 `:96/:105-108` 的 Share/BUS 归类有张力 ⇒ 交 `t2`） |
| ch5 输出节点 | `SCH-Connect-Map.txt:672-674` | `S5_ACM200_FH5/SH5 → K48 → K76 → BST_F/S`（需闭合**恰为** K48,K76） |
| 多源释放先例 | `test.cpp:7598 / 7621 / 7714` 注释 | 「K48/K76 把 ch5 输出接 BST ⇒ 该源全程 RELAY_OFF 不驱动」 |

## 2. 必须在实现前被 owner 明确回答的问题（拦截清单）

| # | 问题 | owner | 为什么必须回答 |
| --- | --- | --- | --- |
| Q1 | TM601 的 `vset[bst,5,…]` 是否**必须**驱动 BST（LS 导通不依赖 BST）？若是，由哪一路源驱动（来路①ch5 / ②④⑤ FPVIe-CH0-High 族 / ⑦CH1-High / ch18）？ | `t2` 事实 + `t7` 选择 | 决定 `t6` 要登记哪些腿；决定实现是否只是「保留现状」 |
| Q2 | TM600 在 PMID=5 V 工况下 BST 是否仍须两步（BST=5 → PMID=5 → BST=10，TM640 形状）？还是单值 `BST=5`（此时 BST−SW≈4.99 V，因 SW 压降极小）？ | `t7` | 两者都满足 ≤5 V 规则，但阶段数与寄存器/延时不同，实现必须唯一确定 |
| Q3 | `relays.md:99` 把 K48/K49 归 MOS P2P 与 `:96` 的 Share 归类冲突，**以哪个为准**？（影响「释放=开路」还是「释放=改道」的判定） | `t2` | 决定「多源互斥」是靠显式 RELAY_OFF 还是靠默认开路 |
| Q4 | TM601 的 SW—PGND 1 A 回路与 BST 供给共用 `K60/K61`（SW 低端腿）时，是否存在耦合/互斥后果？ | `t2` | 用户点名要核实「共享与互斥」 |
| Q5 | 1 A 强制电流的 compliance/clamp 数值 | `t7`（数值）+ 用户/硬件签核 | 三处输入（DFT/`.sv`/CSV）均未给值 |
| Q6 | `expected_for_tm` 对 TM600 的期望集是否应**去掉** FPVIe-CH1/其它来路并入的腿（当前 `[48,60,61,76,83]` 由 pmid2sw+bst2sw 两支合并）？ | `t6` + `t8` | 期望集直接决定门禁红绿，不能含「契约提及但实现不该闭」的腿 |

## 3. 解锁后第一批可执行校验（按顺序，均为只读或沙箱内操作）

1. `t1`：对**新版工作簿**重提取 → `dft-ir.json`，并在产物内登记「旧 IR 曾断言 rows 132/133 无 force 值」为**欠提取缺陷**（见证 `dft-raw/overview-dft.json` 自记 `overview.sha256=d9d721a3…`）。
2. `t2`：给出 BST 来路可达性表（本节表格已有骨架），并回答 Q1/Q3/Q4。
3. `t6`：契约修订后，用同一门禁命令核对「TM600 期望集是否 = `[48,60,61,76,83]`」与「TM601 期望集是否显式包含其 BST 腿」。
4. `t7`：逐阶段表必须写明**每一步** BST 与 PMID/SW 的目标值，并当场验证每一步 `0 ≤ BST−SW ≤ 5 V`。
5. `t8`：独立复核时**不得**沿用「TM601 无 BST」旧推断，也不得沿用旧 IR 的「无 force 值」断言。
6. `t11`：跑门禁必须同时在场 `[scan] targets=N` 与两行 `[t30]`；`--src` 用**等价全量源**；空 PASS 记未执行。

## 4. 边界

只读汇编；未改任何脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 469,714 B / `15c7d2b8…` 未变；**无机台/电性验证**。
