# 会话 #40 — 在工作区 `D:\\Newtest\\CLAUDE_PROCESS` 下盘点所有 agent 定义文件，用于写一份"ATE Offline Coding 工作流架构

- 文件：`agent-acd0d3d75a06356c6.jsonl`（项目 subagents）
- 时间：2026-08-26T13:15:35.273Z → 2026-08-26T13:16:51.169Z，大小 0.3 MB
- 用户消息 1 条 / 助手文本 5 段 / 工具调用标记 24 行

---

## 对话正文（工具输出已剥离）

### 2026-08-26 13:15:35 [user]

在工作区 `D:\Newtest\CLAUDE_PROCESS` 下盘点所有 agent 定义文件，用于写一份"ATE Offline Coding 工作流架构"文档。

请做：
1. 列出 `.claude\agents\` 目录下的全部 .md 文件（应有：rules-agent、experience-agent、compile-agent、deploy-agent、testplan-agent、power-off-agent、cbit-singlepoint-agent、cbit-parse-agent、cbit-check-agent、dual-parse-agent、power-on-agent、relay-agent、measure-agent、check-agent、sub-function-agent 等）。
2. 对每个 agent，读文件提取：**名称、一句话职责、触发条件（用户说什么话/什么时机）、输入（依赖哪些文件/资料）、输出（产出的文件/产物）、它会调用哪些脚本或 skill、执行频率（每次生成TM / 每批 / 用户触发 / 收尾）**。
3. 读 `.claude\AGENT_MAP.md`，提取它对各 agent 的触发/依赖/产出概括，以及整个 agent 地图的组织方式。

输出为结构化清单（按 agent 分组，每项一行简短要点即可），中文回答。重点是准确提取"输入文件"和"输出文件/产物"以及"调用关系"，这些我要直接写进文档。不要遗漏任何 agent 文件。
- [tool] Glob
- [tool] Glob
- [tool] Bash

### 2026-08-26 13:15:42 [assistant]

There are 18 agent files (the user's expected list plus `cbit-agent.md`, `cbit-path-finder.md`, `cbit-path-namer.md`). Let me read them all plus the AGENT_MAP.md.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:15:45 [assistant]

Now let me read the remaining 12 agent files in parallel.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:15:48 [assistant]

Now let me read the remaining 7 agent files.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:15:54 [assistant]

All 18 agent files plus AGENT_MAP.md are read. Let me quickly check the skills directory (referenced by the agents as `nuvolta-codegen`, `sch-parse`) and confirm no other agent files exist.
- [tool] Glob
- [tool] Bash

### 2026-08-26 13:16:51 [assistant]

已完成全部盘点。工作区 `D:\Newtest\CLAUDE_PROCESS\.claude\agents\` 下共有 **18 个 agent 定义文件**（AGENT_MAP 头注"共 19 个"已过时；含用户预期列表之外的 `cbit-agent`、`cbit-path-finder`、`cbit-path-namer` 三个）。另有 `AGENT_MAP.md` 和 2 个 skill（`nuvolta-codegen` 主 Skill、`sch-parse`）。

按 AGENT_MAP 的组织方式，18 个 agent 分四组。以下为结构化清单。

---

## 一、代码生成 Pipeline（主 Skill 编排，双路径 A/B + cbit 公共前置）

### 1. dual-parse-agent（`dual-parse-agent.md`）
- **职责**：双表解析，DFT（+资源分配表）→ TestItemMeta JSON，A/B 双模式
- **触发**：主 Skill 每次进入，入口分流后按路径传 `--A` / `--B`
- **输入**：`--A` = DFT.csv + 资源分配表.csv + FET 对配置（knowledge/hardware/voltage-inference.md）；`--B` = DFT 段（TM 行，仅 DFT，无资源表）
- **输出**：**TestItemMeta JSON**（functionName/testType/params[]/hardwareInit/softwareInit/dynamic/pinsInvolved/resourcesInvolved/floatingPairs/activeFetPairs/voltageInference）
- **调用**：无脚本；引用 knowledge/hardware/pin-resource-map.md、naming.md、voltage-inference.md
- **频率**：每次生成 TM（每个测试项一个）
- **要点**：`--B` 的 resourcesInvolved 留空，源表映射由 relay-agent 从 SCH-Connect-Map 补齐

### 2. cbit-agent（`cbit-agent.md`）— 公共前置编排器
- **职责**：保证继电器定义文件（relay.h/StdAfx.h #define）存在且正确；有→仅 check，无→串行四阶段创建
- **触发**：主 Skill **每次进入都先走**（存在即冻结：只 check 不更新）
- **输入**：CBIT 表(.xlsx)、COMPONENT-STATISTIC、SCH-Connect-Map（B 路径）、netlist（B 路径兜底）、定义文件
- **输出**：**relay.h/StdAfx.h 单点+通路 #define 块** + **V1~V8 校验报告**
- **调用**：`gen_cbit_defines.py --cbit [--stat] [--verify]`（P1/P4）、`gen_paths.py --netlist --cbit [--json]`（P2 兜底）、`gen_path_defines.py`（P3）、子 agent `cbit-path-namer`（P3 仅 B）
- **频率**：每次进入主 Skill（A 路径只走 P1+P4；B 路径完整 P1→P2→P3→P4）
- **要点**：A 路径 relay.h 只含单点继电器（无 SCH-Connect-Map 不定义通路）；四阶段严格串行不可跳步

### 3. cbit-parse-agent（`cbit-parse-agent.md`）— 已脚本化，规格文档
- **职责**：CBIT 辅助解析（CBIT表→cbit_map；定义文件→existing_defines）
- **触发**：不再派发执行，逻辑并入 `gen_cbit_defines.py`
- **输入**：CBIT表(.xlsx)、StdAfx.h/relay.h、COMPONENT-STATISTIC
- **输出**：cbit_map（CBIT值→继电器名/分组） + existing_defines（脚本内中间产物，供单点 merge / V5/V6 / P4 对拍）
- **调用**：`gen_cbit_defines.py`（read_excel_cbit/build_cbit_map/load_existing_defines）
- **频率**：已脚本化

### 4. cbit-singlepoint-agent（`cbit-singlepoint-agent.md`）— 已脚本化，规格文档
- **职责**：CBIT Phase1 单点继电器 #define 生成（F/S 双线圈合并、BUS 方向合并、FORCE/SENSE 合并）
- **触发**：不再派发执行，逻辑并入 `gen_cbit_defines.py`
- **输入**：CBIT 表 Excel（col0=原位号, col10=CBIT通道, 分组标题）
- **输出**：按 group 分组的**单点 #define 块**（161 个唯一 CBIT 值）+ V1~V8 校验
- **调用**：`gen_cbit_defines.py`（merge_names + gen_singlepoint_defines）
- **频率**：已脚本化（A+B 都执行）

### 5. cbit-check-agent（`cbit-check-agent.md`）— 已脚本化，规格文档
- **职责**：CBIT Phase4 校验，V1~V8 八项校验定义正确性（只发现问题不修改）
- **触发**：不再派发执行，逻辑并入 `gen_cbit_defines.py --verify`；单独触发仍可用 "CBIT"/"继电器定义"
- **输入**：relay.h/StdAfx.h（--verify）、CBIT表（--cbit）、COMPONENT-STATISTIC（--stat, V8）、SCH-Connect-Map（--map, V2/V7）
- **输出**：**CBIT-CHECK RESULT**（V1~V8 + OVERALL PASS/FAIL + Issues）
- **调用**：`gen_cbit_defines.py`（check_v1~check_v8 + run_checks）
- **频率**：已脚本化（P4 每次 cbit 前置都跑）

### 6. cbit-path-finder（`cbit-path-finder.md`）— 已脚本化，规格文档
- **职责**：CBIT Phase2 通路查找，从 Netlist 追踪 DUT_PIN→稀缺源表（FPVIe/QTMU/QVM）通路
- **触发**：不再派发执行，脚本化 `gen_paths.py`（仅 B 路径；SCH-Connect-Map 存在时优先参考，缺失时兜底）
- **输入**：port_list、net_map、instance_map、cbit_map（Phase1 产出）或 netlist + CBIT表
- **输出**：**path_list JSON**（[{dut_pin, source, side, via_relays[], intermediate_source}]）
- **调用**：`gen_paths.py --netlist <file> --cbit <file> [--json]`
- **频率**：已脚本化（仅 B 路径）
- **要点**：FPVIe 域约束（FH配SH/FL配SL）、G6K/MOS 脚位通断、F/S 合并分类（Kelvin/PC短接/单线）

### 7. cbit-path-namer（`cbit-path-namer.md`）— 已脚本化 + 少量 agent 复核
- **职责**：CBIT Phase3 通路继电器 #define 命名（命名优先级 K_<源>H/L_TO_<PIN> / _<途经源> / _A/B/C）
- **触发**：已脚本化 `gen_path_defines.py`；仅 "`_B` 类 CH0/CH1 双通道取舍" 仍需本 agent 复核
- **输入**：path_list + single_point_defines（或 SCH-Connect-Map `需闭合:` 行）
- **输出**：**通路继电器 #define 块**（352 定义，追加到 **StdAfx.h** 2.x 段，include guard 内）
- **调用**：`gen_path_defines.py`（--no-write 预览 / --verify 一致性 / --check-relay 对拍 / --audit-rules）
- **频率**：已脚本化（仅 B 路径，一次性创建）
- **要点**：多源同 PIN 尾缀 `_A/_B/_C` 属正常命名全部发布；仅 ⚠非有效（F/S 未同时闭合）不发布

### 8. relay-agent（`relay-agent.md`）
- **职责**：继电器闭合决策 + 闭环验证，输出 cbite.SetOn() + delay_ms(3)
- **触发**：共用生成循环内（每个测试项）
- **输入**：TestItemMeta.pinsInvolved/floatingPairs/params[].check；**A 路径** = resourcesInvolved[] + 资源分配表.csv（relay.h 只含单点继电器）；**B 路径** = SCH-Connect-Map（源表映射补齐，可含通路继电器）
- **输出**：**cbite.SetOn(Kxx, Kyy, -1); delay_ms(3);** 代码块；无继电器 → `cbite.SetOn(-1);`
- **调用**：无脚本；由 `verify_relay_trace.py` 强制校验（B/D/E 方向 + src 结构规则）
- **频率**：每次生成 TM
- **要点**：机械 G6K 默认闭合/光耦默认断开；Connect=Default 不闭合；BUS/Cap2/P2P/PU 功能应用规则；反短接（Step12）；路径穷举法（Step13）

### 9. power-on-agent（`power-on-agent.md`）— 已脚本化，规格文档
- **职责**：上电配置 + 上电序列（已由 `gen_power_sequence.py` 取代，本文档为 R-PON 规则清单规格）
- **触发**：不再派发推理，主 Skill 直接调脚本生成 Step2 上电代码 + PowerState JSON
- **输入**：TestItemMeta.hardwareInit/floatingPairs/mvNoFipins（--meta）、--pin-map、--define Pin_Channel_define.h
- **输出**：**POWER_ON 代码块**（Step2 上电）+ **PowerState JSON**（sources/floatingPairs/upSequence/finalVoltages）
- **调用**：`python gen_power_sequence.py --meta <TestItemMeta.json> --pin-map <pinmap.json> --define Pin_Channel_define.h --mode power-on`
- **频率**：每次生成 TM（脚本化，上电下电同一次调用 `--mode both` 默认）
- **要点**：R-PON-01~09（vset→FV/iset→FI、量程≥2×、浮动源三阶段≤5V、大电流三段式、power/digital/ATEST PIN 两段式）

### 10. measure-agent（`measure-agent.md`）
- **职责**：测量代码生成，五模式（MI/MV/Toggle/Trim/AMUX-NTC）
- **触发**：共用生成循环内（每个测试项）
- **输入**：TestItemMeta.params[].check + checkPin、testType、resourcesInvolved[]、NU1201.treg（Trim 测试）
- **输出**：**Step4 测量代码段**（MeasureVI + GetMeasResult + SetTestResult；Toggle 用 rampv_capv；Trim 用 TRIM_NODE.execute + sub.cpp measure 函数）
- **调用**：无脚本；Toggle 用 test_method.rampv_capv（13 参数）；Trim 模板 references/sub-measure-template.cpp
- **频率**：每次生成 TM
- **要点**：MI→MIRET / MV→MVRET；LogData 单位 = spec 预期单位（uA→*1e6 等）；Toggle 参数固定 3 个 Rise/Fall/Hys；Trim 禁止在 test.cpp 写 MeasureVI

### 11. power-off-agent（`power-off-agent.md`）— 已脚本化，规格文档
- **职责**：下电序列（已由 `gen_power_sequence.py` 取代，本文档为 R-POFF 规则清单规格）
- **触发**：不再派发推理，主 Skill 调脚本（与上电同一次调用，内部复用 PowerState）
- **输入**：TestItemMeta（--meta，含 hardwareInit/floatingPairs/rampProfile）、--pin-map、PowerState（内部继承上电终点）
- **输出**：**POWER_OFF 代码块**（Step5 下电）
- **调用**：`python gen_power_sequence.py --meta ... --pin-map ... --define ... --mode power-off`（默认 both）
- **频率**：每次生成 TM（脚本化）
- **要点**：R-POFF-01~06（普通三步/浮动反转/大电流 FI=0→FV=0→OFF；RELAY_OFF 统一量程 10V/10MA，FPVI 用 1V/10MA；FPVI 永远最后断开；每步≤5V+delay_us(200)）

### 12. check-agent（`check-agent.md`）
- **职责**：代码检查质量门禁，60+ 项逐条检查（P/E/T/R/V/M/H 组），输出结构化 PASS/FAIL/WARN 报告
- **触发**：**收尾双查**（主 Skill 生成循环完成后，与 cbit-check 一起；FAIL→修复→重查→PASS）
- **输入**：组装后完整函数代码、Pin Pair 约束条件、DFT.csv(可选)、资源分配表.csv(可选)、TestItemMeta JSON(可选)、PowerState JSON(可选)、NU1201.treg(Trim时)
- **输出**：**JSON 报告** {verdict, summary, checks[]}
- **调用**（强制脚本）：`verify_awg_params.py --src`（E005）、`verify_relay_trace.py --src`（R004/R005）、`verify_material_receipt.py --receipt`（E030 生成前）、`verify_bst_sw_sequence.py --src`（E030 生成后）、`verify_merge_rules.py`（M组）
- **频率**：收尾双查（每 TM / 每批）
- **要点**：无 DFT/资源表自动切轻量模式（V 组强制 + E/R 代码结构项）；V 组电压过渡态 FAIL_CRITICAL（烧片）；反短接 P006

---

## 二、独立工作流 Agent（旁路 pipeline，用户触发，当前不执行）

### 13. compile-agent（`compile-agent.md`）
- **职责**：打开 VS 工程→写码→code check→编译→Debug 闭环
- **触发**：用户触发 "编译"/"debug"（不进 codegen pipeline）
- **输入**：工程路径（含 .sln/.vcxproj）、修改指令/代码（模式B必需）、配置（Release/Debug 可选）
- **输出**：修改摘要（文件+行号）、Rebuild 结果、自修复记录、Debug 启动状态
- **调用**：`D:\Newtest\CLAUDE_PROCESS\compile.ps1 -ProjectPath "<工程路径>" [-SkipDebug] [-Configuration Release]`
- **频率**：用户触发（codegen 可选收尾）
- **要点**：模式A纯编译 / 模式B写码+编译；打开工程先于写码；编译前 code check；自修复最多 10 次

### 14. deploy-agent（`deploy-agent.md`）
- **职责**：STS8300 自动开软件前置（打开 STS8300 软件 + VS），就绪后交给 compile-agent
- **触发**：用户触发 "deploy"/"打开STS8300"（compile-agent 的开软件前置，非废弃）
- **输入**：VS 状态检测（COM）；路径B需用户提供 PGS 路径 + PGS 文件名
- **输出**：软件就绪状态（路径A直接交 compile-agent；路径B调脚本自动打开）
- **调用**：`D:\Newtest\CLAUDE_PROCESS\auto_sts8300.py <PGS_PATH> <PGS_NAME>` + `input_guard.py`（键鼠屏蔽，ESC 中止）
- **频率**：用户触发（前置）
- **要点**：VS 已运行零确认；VS 未运行只问一次；依赖 control.exe、Python D:\SOFTWARE_INSTALL\python.exe

### 15. testplan-agent（`testplan-agent.md`）
- **职责**：测试方案生成 — 程序 + 硬件图 → 人类可读测试方案 Word 文档
- **触发**：用户触发 "写测试方案"/"翻译"（不进 pipeline）
- **输入**：工程路径（test.cpp/sub.cpp）、SCH-Connect-Map、COMPONENT-STATISTIC
- **输出**：**测试方案 Word 文档**（.docx，python-docx 生成，按 TM 编号排序含目录）
- **调用**：python-docx（无独立脚本）
- **频率**：用户触发
- **要点**：继电器功能/源表通路归类以 SCH-Connect-Map/COMPONENT-STATISTIC 为准（非代码注释）

---

## 三、自进化三 Agent（独立启用，共享 daylog 数据源）

### 16. rules-agent（`rules-agent.md`）
- **职责**：规则自进化，从 daylog 提炼候选规则，六类分类，写入待审核区，人工发布后同步 verify 脚本
- **触发**：手动 "提炼规则"/"跑 rules-agent"/"/evolve rules"
- **输入**：`daylog/*.md`、`merge_rules.md`、`verify_*.py`（现有强制脚本）
- **输出**：**`knowledge/standards/rules-registry.md` draft 区**（不直接发布）；发布后同步 verify 脚本
- **调用**：发布后更新 `verify_merge_rules.py` / `verify_relay_trace.py` / check-agent 错误码
- **频率**：用户触发（知识沉淀层独立运行）

### 17. experience-agent（`experience-agent.md`）
- **职责**：经验自进化，从 daylog 提炼项目级实现经验，写入经验库 + 记忆索引，人工审核发布
- **触发**：手动 "沉淀经验"/"跑 experience-agent"/"/evolve exp"
- **输入**：`daylog/*.md`、`PROGRESS.md`、auto-memory `nuvolta-*.md`（feedback 类）
- **输出**：**`knowledge/experience/` 经验条目**（index.md/power-sequence.md/measurement.md/debug-patterns.md/project-notes.md）+ 同步 `MEMORY.md` + 经验库 index.md
- **调用**：无脚本；global/specialized rule 转发 rules-agent、sub_function usage 转发 sub-function-agent
- **频率**：用户触发

### 18. sub-function-agent（`sub-function-agent.md`）
- **职责**：子函数自进化，从 daylog 代码 diff 提炼可复用 helper，写入共享子函数库 draft，人工发布
- **触发**：手动 "提炼子函数"/"跑 sub-function-agent"/"/evolve fn"
- **输入**：`daylog/*.md`（含代码 diff）、`库函数\test_method\`（现有专项库）、`references/`、当前项目 `*.cpp`
- **输出**：**`D:\Newtest\CLAUDE_PROCESS\库函数\shared_functions\draft\<函数名>.md`**；发布后迁入 `src\` + `registry/index.md` + `registry/changelog.md`
- **调用**：无脚本（与 test_method 专项库分工：通用→shared_functions，专项 ramp→test_method）
- **频率**：用户触发

---

## 四、AGENT_MAP.md 本身（`.claude\AGENT_MAP.md`）

**组织方式**：单一入口在根目录 `工作流全景.md`（流程地图+文件所有权+更新协议），本文件为 Agent 细节速查，四个 section：
1. **代码生成 Pipeline**：主 Skill 编排，双路径 + cbit 公共前置。入口 Step0 分流（有无资源分配表）→ A 路径走 dual-parse --A / B 路径走 sch-parse→dual-parse --B → cbit 公共前置 → 共用生成循环（框架→relay→power-on→[寄存器]→measure→power-off→[LogData]）→ 收尾双查（check-agent + cbit-check）
2. **独立工作流 Agent**：sch-parse(Skill)、compile、deploy、testplan —— 用户触发、当前不执行，不进 codegen pipeline
3. **自进化三 Agent**：rules / experience / sub-function，共享 daylog
4. **废弃 Agent**：A0 旧遗留已删除

**对各 agent 的触发/依赖/产出概括**（表格速查，关键几行）：
- **入口分流(0)**：每次进入，看有资源分配表? → 路径 A/B
- **dual-parse --A(1)**：DFT.csv + 资源分配表 → 完整 TestItemMeta；**--B(1')**：DFT 段 → 部分 TestItemMeta（无源表映射）
- **sch-parse Skill(1b)**：SCH-DALI.NET → COMPONENT-STATISTIC + SCH-Connect-Map
- **cbit-agent(2)**：CBIT表/Netlist/定义文件 → 有定义→check / 无→A 仅单点 P1+P4 / B 完整四阶段
- **relay-agent(3)**：TestItemMeta + (A:资源表 / B:SCH-Connect-Map) → cbite.SetOn() + 闭环验证
- **power-on(4)/power-off(7)**：已脚本化 gen_power_sequence.py（上电/下电），标注"推理→agent, 固定→脚本"
- **measure-agent(6)**：params[].check + testType → 测量代码
- **check-agent + cbit-check(9)**：收尾双查，完整代码+TestItemMeta+PowerState+定义文件 → PASS/FAIL/WARN 报告

---

## 补充说明（供文档引用）

- **脚本化架构原则**：AGENT_MAP 反复强调"推理→agent, 固定→脚本"。已脚本化的 agent：power-on/power-off（→ `gen_power_sequence.py`）、cbit-parse/singlepoint/check（→ `gen_cbit_defines.py`）、cbit-path-finder（→ `gen_paths.py`）、cbit-path-namer（→ `gen_path_defines.py`，仅 `_B` 双通道取舍保留 agent 复核）。这些 agent 的 .md 文件保留为**规格文档（规则溯源）**，不再被派发推理。
- **仍执行推理的 agent**（活跃）：dual-parse、relay、measure、check（收尾）、cbit-agent（编排器）+ cbit-path-namer（仅复核）；自进化三 agent 用户触发；compile/deploy/testplan 当前不执行。
- **文件路径绝对值**：所有脚本均在 `D:\Newtest\CLAUDE_PROCESS\` 下（compile.ps1、gen_power_sequence.py、gen_cbit_defines.py、gen_paths.py、gen_path_defines.py、auto_sts8300.py、input_guard.py、verify_*.py）；知识库在 `D:\Newtest\CLAUDE_PROCESS\knowledge\`；子函数库在 `D:\Newtest\CLAUDE_PROCESS\库函数\shared_functions\`。
