# 吸收记录 #8 — gen_power_sequence.py 架构设计（软件架构师方案）

- 源文件：`sessions/08-agent-af.md` ← `~/.claude/projects/subagents/agent-afae67e4caa8212ca.jsonl`
- 时间：2026-08-09 10:45→10:50（0.5MB）；subagent 设计任务（后续落地为真实 gen_power_sequence.py）
- 主题：上电/下电代码生成脚本完整实现方案（用户验收：agent 规则全部涵盖 + 与 AI.cpp 人工代码对拍一致）

## 用户已拍板（关键约束）

1. 输出 = **CLI**（stdout 输出三段 + PowerState JSON，主 Skill 拼装，不直接改 AI.cpp）
2. 量程前缀 = **看 extern 类型声明**（Pin_Channel_define.h `extern FXVIe_PLUS SW1_SW2_FXVI;` 权威）
3. verify = **AI.cpp 真实函数对拍**（普通/多源/浮动大电流 TM600 三类）

## 关键事实结论（脚本设计的基石）

- AI.cpp 77 个函数全为普通/多源（ACM200+FXVIe_PLUS），无 FPVI 用例；TM600 浮动大电流基准在 test.cpp:940-1049 与 `.claude/references/tm600-normal-highcurrent.cpp`（`--verify-src` 可指）。
- **对象名 ≠ 资源表逻辑名**：extern 名（VBAT_PD3_FXVI）才是代码对象；pin→object 映射必须由调用方解析。
- **RELAY_OFF 统一量程实锤**：ACM200_10V/10MA、FXVIe_PLUS_10V/10MA、**FPVIe_1V/10MA**（test.cpp:1042 是 10MA 非 10A）。
- **FPVI 继电器前缀特例**：量程 `FPVIe_` 但继电器 `FPVI_RELAY_ON`（无 e）。
- **FV 模式 iRange 是输入非推导**：同一 VBAT=3.7V 有三种 iRange（10MA/100UA/100MA 按 DUT 预期电流）→ 脚本必须收 `currentLimit` 覆盖，默认 100MA。
- **浮动 ramp 终点来自 voltageInference/rampProfile**（agent 提供），脚本不能从 hardwareInit 推（vset[bst2sw,5] 只给初值）。
- **B 路径定论**：脚本不需要资源分配表.csv；只要 `{pin:object}` 映射（A 调用方从 CSV 翻译 / B relay-agent 从 SCH-Connect-Map 补齐），脚本从 extern 自行解析类型。

## 核心算法（select_range 量程选择）

- 查表取**第一个 table_max ≥ value**；table_max 恒等于档位满量程 50%（ACM200_3p6V→1.8V），因此"满量程≥2×设定值" ⟺ "table_max≥设定值"，≤90% 自动满足；等号边界取本档（FI=50mA→100MA 档，对上 AI.cpp 对拍）。
- 已知手写违反 ≥2× 案例：AI.cpp:2917 `VDM_SDA_ACM.Set(FI,1e-5,…,ACM200_10UA)`（10μA 用 10UA）→ 对拍归 WARN。
- FV 强制值 vRange=select_range；iRange=currentLimit 经表选；FI 强制 iRange=表选、vRange 默认 10V；FPVI 大电流 vRange 固定 FPVIe_1V。

## verify 对拍三分类

- **ERROR（必一致）**：object/mode/强制值/RELAY_ON/OFF/强制值量程
- **WARN**：合规量程、手写违反 ≥2×、FPVI 等电位 10A vs 2A、浮动 ramp Set 次序
- **INFO**：注释/delay 分组/非上下电行
- `--audit-rules`：RULE_COVERAGE 机器自检（每条 R-PON/R-POFF/R-FLT/R-RNG/R-SRC/R-ST → 函数存在且可达）

## 模块结构（落地参考）

输入层（read_enc/load_meta/load_pin_map/load_pin_channel_define）→ 解析层（parse_extern_types/resolve_source_type/resolve_all_sources/parse_floating_pairs）→ 量程层（mode_for_cmd/select_range/relay_off_ranges/relay_const/classify_power_off/is_high_current）→ 上电层（gen_simple_power_on/gen_floating_ramp/gen_high_current_init/gen_power_on）→ 下电层（gen_normal_power_off/gen_floating_power_off/gen_high_current_off/gen_power_off）→ PowerState/拼装（build_power_state/build_code_block/emit_sections）→ verify 层 → 规则审计层 → main/argparse。

## CLI

`python gen_power_sequence.py --meta <json> [--pin-map] [--define] [--resolve-from-resources] [--current-limit] [--ramp-profile] [--mode] [--verify <src.cpp>] [--verify-func] [--verify-src] [--warn-as-error] [--audit-rules]`

## 仍需 agent 提供（脚本输入边界）

pin→object 映射、currentLimit、rampProfile（终值）、≥200mA/≥1A 资源选型、Sense/Cap/PU/P2P 继电器（脚本不生成继电器代码）、MV 无 FI 意图、testType 框架。

## 交叉引用

- 建立在 #6（规则表）+ #7（脚本模式/数据格式）之上；其设计在后续会话中落地为真实 `gen_power_sequence.py`（在 CLAUDE_PROCESS 根目录）。
- 规则编号需登记进 rules-registry.md（当前只有 MR-000/FR-001~003）。
