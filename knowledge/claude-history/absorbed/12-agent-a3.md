# 吸收记录 #12 — DALI TestItemMeta 探索（meta 覆盖范围 + SCH-Connect-Map 结构）

- 源文件：`sessions/12-agent-a3.md` ← `~/.claude/projects/subagents/agent-a3a2d76c0efc74dde.jsonl`
- 时间：2026-08-10 07:04→07:08（0.2MB）；subagent 只读探索
- 主题：TestItemMeta 数据现状 + SCH-Connect-Map 结构（为 verify_relay_trace Meta 化铺路）

## meta 现状

- `DALI\meta\` 下只有 **1 个 TestItemMeta JSON**：`tm000_102.json`（7367 字节，142 行，7 个函数：TM000/001/001_2/001_3/100/101/102）。`merged` 数组（第 4 行）把 TM000+TM000_1 合并为 `TM000_IQ_STANDBY`（1 函数 2 参数，用户 2026-08-09 拍板）；`functions[]` 数组 functionName 用全名。
- **覆盖缺口**：test.cpp 有 51 个 TM 函数，44 个无 meta；重点核对的 14 个函数（103/104/114/117/118/124/125/126/127/128/132/134/204/207）**全部无 meta**。meta 只含 MI/MV 类型，无 Trim/浮动/FOVI。
- 附带文件：`gen_tm000_102.cpp`（生成的 7 函数源码）、`check_tm.py`/`append_tm.py`（追加进 test.cpp，UTF-8 BOM+CRLF）、`find_fpvi*.py`、DTE 构建 ps1 脚本。

## meta 字段观察

- `hardwareInit[]` pin 只有 vbat/vac1/vdm 三种；`params[].check`=MI/MV、checkPin MI→VBAT、MV→ATEST0。
- `sources`：{PIN: {object, type, connect}}——**每个上电 PIN 都有对应条目**（vdm 键写 `"VDM/ATEST0"`）。
- `relaySetOn`：字符串，`"-1"`（全释放）或 Cap 继电器名（K21_VAC_Cap / K13_VBAT_Cap）。
- `powerOn`：{pin: {mode, value, iRange, vRange}}。
- **重要**：relaySetOn 引用的 Cap 继电器（K13/K21）在 SCH-Connect-Map.txt 中不存在（map 只覆盖信号通路继电器）；Cap 只在 meta 与 `sch_confirmed.json` 的 `relay_class` 出现。

## SCH-Connect-Map.txt 结构（1149 行，818 条通路）

- 10 列（FPVIe BUS 节点/FPVIe→PIN/QTMUe→PIN/QVMe→PIN/ACM→PIN(空)/ACM200→PIN/FXVIe_PLUS→PIN/QTMUe→PIN/QVMe→PIN/DCM→PIN）+ 附注（DUT PIN→信号 net，Unicode 箭头）。
- 行格式：`<源节点> -> Kxx(Relay-NC|Relay-ON) -> ... -> 末端PIN`；group 头行 `CH0 High -> ACDRV1 [Kelvin] 需闭合: K22,K30`。
- 纯 Relay-NC 默认导通通路存在（8 行 BUS 节点 + AMUX 单跳）。Relay-NC 750 次 / Relay-ON 1463 次。
- 环境发现：`tm000_102.json` 曾被 Git Bash hexdump 误判为二进制（管道伪影），PowerShell 确认真实 UTF-8——**Windows 管道工具不可信，用 PowerShell/Read 权威核实**。

## 交叉引用

- #11（verify_relay_trace.py）的 Meta 化改造输入；sch_confirmed.json 的 relay_class 机制与 #1（K57 覆盖）相关；meta 缺口（14 个重点函数）是后续会话的扩展方向。
