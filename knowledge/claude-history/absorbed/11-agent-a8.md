# 吸收记录 #11 — verify_relay_trace.py 结构化分析（338 行，检查 E 数据流）

- 源文件：`sessions/11-agent-a8.md` ← `~/.claude/projects/subagents/agent-a810acbdaa13ec287.jsonl`
- 时间：2026-08-10 07:04→07:05（0.1MB）；subagent 只读分析（为 Meta 化改造铺路）
- 主题：verify_relay_trace.py 全函数清单 + 五段检查 + 检查 E（FR-001 反向 Cap 检查）精确数据流

## 关键结构

- **输入层**：`read_enc`（L20-29，utf-8-sig→utf-8→gbk→latin-1 回退）、`parse_defines`（L32-37，`#define\s+(K\d+_\w+)\s+(\d+)`）、`parse_setons`（L40-46）、`parse_map_rels`（L49-55，**只解析 Relay-ON/NC**）、`fn_blocks`（L58-66，按 `DUT_API int TM\d+_\w+\(` 切函数）。
- **反推函数**：`obj_pins`（L116-122，对象名→驱动 PIN：取最后一个非类型/后缀 token，如 `VAC123_AMUX_ACM→VAC123`）、`mi_current_pins`（L90-102，MIRET 源→被测电流 PIN，跳过 NON_SUPPLY_TOKENS）、`fv_supply_objs`（L131-136，`pre_poweroff` 段内 `\w+\.Set\(FV,` → {obj:{pins}}）。
- **判定辅助**：`is_testpad_bias`（L170-178，对象名+闭合 Share 继电器名都含 AMUX/VDM/NTC/ATEST）、`cap_pin`（L76-79，`K\d+_(\w+)_Cap$`）、`is_pu`/`is_p2p`、`capi_monitor_sources`（ramp[vi]_capi 第 4 参）、`is_ramp_or_scan`（ramp 首参 / FV 值非字面量或 ≥2 不同值）、`observes_open_drain`（NQON_HG1_ACM/QTMU_GP/SDA_INT）、`pre_poweroff`（L125-128，**按 'Step 5' 字符串截断**下电段+去注释）。
- **五段检查**：S 结构规则（有 Step1 无 SetOn→error，须显式 `cbite.SetOn(-1)`）/ A 名真实性（继电器名 ∈ defines）/ B 功能规则（Cap：测该 PIN 电流却闭→error；PU：闭但未观测开漏→warn；P2P 占位）/ C 闭环规则（on_set 通过、nc_set 冗余 warn、都不在→虚构通路 error）/ D 反向检查（观测开漏无上拉→warn）/ **E 反向检查（静态供电未闭 Cap，FR-001）**。
- **检查 E 数据流**（L296-315）：`cap_defs`（PIN→Cap 继电器，`setdefault` 每 PIN 取第一个）→ 三向 PIN 匹配（==/startswith 双向）→ 豁免链：①已闭 Cap **或** `fam & mi_pins`（**按 PIN 豁免**）②capi 电流捕获源 ③ramp/扫描源 → 否则 WARN。
- **CLI**：`--warn-as-error`/`--src`/`--defines`（sys.argv 手动扫描）；退出码 1=FAIL、0=PASSED（仅 warns 仍 0）。
- **外部依赖**：test.cpp（--src 可覆盖）、StdAfx.h（--defines 可覆盖）、SCH-Connect-Map.txt（PROJ 固定）。
- **无 meta/JSON 读取逻辑**（零匹配）——Meta 化需从零新增。

## 交叉引用

- 检查 E 的"按 PIN 豁免"语义 = #9 FR-001 规则的落地实现；#10 的 E1/E2/E3 经验都来自该脚本的实现坑；后续会话会把它 Meta 化/拆分。
