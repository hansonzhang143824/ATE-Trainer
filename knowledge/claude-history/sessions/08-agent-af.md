# 会话 #8 — 你是软件架构师，为 D:\\Newtest\\CLAUDE_PROCESS 项目设计一个"上电/下电代码生成脚本"的具体实现方案。项目是半导体芯片测试代码生成流水线

- 文件：`agent-afae67e4caa8212ca.jsonl`（项目 subagents）
- 时间：2026-08-09T10:45:10.473Z → 2026-08-09T10:50:49.797Z，大小 0.5 MB
- 用户消息 1 条 / 助手文本 24 段 / 工具调用标记 50 行

---

## 对话正文（工具输出已剥离）

### 2026-08-09 10:45:10 [user]

你是软件架构师，为 D:\Newtest\CLAUDE_PROCESS 项目设计一个"上电/下电代码生成脚本"的具体实现方案。项目是半导体芯片测试代码生成流水线（Nuvolta STS8300）。

## 背景

项目遵循架构原则"推理→agent，固定→脚本"。power-on-agent / power-off-agent 目前是 agent 文件，但逻辑全是固定模板，决定转成 python 脚本 `gen_power_sequence.py`。**核心验收约束（用户明确）**：脚本执行时，agent follow 的所有规则必须被涵盖，不能因脚本化丢规则；脚本输出要与 AI.cpp 现有正确人工代码对拍一致。

**用户已拍板**：
1. 输出方式 = **方案1 CLI**：读 TestItemMeta JSON + 资源分配表 → stdout 输出上电代码块 + PowerState JSON，主 Skill 拼装，不直接改 AI.cpp
2. 量程前缀判断 = **看对象名 extern 类型声明**：Pin_Channel_define.h 里 `extern FXVIe_PLUS SW1_SW2_FXVI;` → SW1_SW2_FXVI 是 FXVIe_PLUS 类型 → 量程前缀 `FXVIe_PLUS_`；`extern ACM200 LG1_LG2_ACM;` → ACM200 → `ACM200_`；FPVI 对象 → `FPVIe_`。脚本从 Pin_Channel_define.h 解析 extern 声明做权威判断
3. verify = **AI.cpp 真实函数对拍**：普通(3.7V)/多源/浮动大电流(TM600) 三类

**待解决的新问题（用户提出）**："如果没有资源分配表怎么办"——B 路径无资源分配表。我的思路：pin→源表映射作为脚本**输入参数**（JSON/dict），A 路径由调用方从资源分配表.csv 生成传入，B 路径由 relay-agent 从 SCH-Connect-Map 补齐传入；脚本本身不做 pin→源表查找，只读 Pin_Channel_define.h 判断类型。

## 已探索确认的关键事实（可直接采用）

### 规则清单（来源：power-on-agent.md / power-off-agent.md / memory 记忆 / knowledge）
- **上电 R-PON**：
  - 指令→模式：vset→FV，iset→FI，MV 无 FI→FI=0+最小量程10UA
  - 浮动源识别：hardwareInit[].pin 含"2"即跨 Pin（pmid2sw→PMID,SW）
  - 量程选择：≥2×设定值，选最接近的最小档；force/测量值≤量程90%
  - 普通上电：`<Res>.Set(FV, value, vRange, iRange, <TYPE>_RELAY_ON)` + delay_ms(1)
  - 浮动电压源三阶段：PinB 基准 → FPVI.Set(FV,0,FPVIe_1V,FPVIe_10A,FPVI_RELAY_ON)+delay_us(200) → PinA 台阶升，每步|ΔV|≤5V+delay_us(200)
  - 大电流（≥1A）：FPVI.Set(FV,0,...)→FPVI.Set(FI,0,...)→FPVI.SetClamp(25,25)→FPVI.Set(FI,target,...)
  - PowerState JSON 4 字段：sources[]/floatingPairs[]/upSequence[]/finalVoltages{}
- **下电 R-POFF**：
  - 类型判定：floatingPairs非空+type=vset→浮动下电；FI≥1A→大电流；其他→普通
  - 普通三步：全部源 Set(FV,0,原量程,RELAY_ON) → delay_ms(1) → 统一 10V/10MA RELAY_OFF
  - 浮动下电：反转 upSequence，PinA先降→PinB→其他→PinA归零，每步|ΔV|≤5V+delay_us(200)；FPVI永远最后一个RELAY_OFF
  - 大电流下电：FI=0→FV=0→RELAY_OFF
- **量程表**（sources/acm200.md, fovie.md, fpvie.md）：
  - ACM200: 电压 3p6V(≤1.8V)/10V(≤5V)/40V(≤20V)；电流 1UA(≤500nA)/10UA(≤5μA)/100UA(≤50μA)/1MA(≤500μA)/10MA(≤5mA)/100MA(≤50mA)/200MA(≤100mA)
  - FOVIe(=FXVIe_PLUS): 电压 1V(≤0.5V)/2V(≤1V)/5V(≤2.5V)/10V(≤5V)/20V(≤10V)/40V(≤20V)；电流 10UA/100UA/1MA/10MA/100MA/1A
  - FPVIe: 电压 100MV/1V/2V/5V/10V/20V/40V/100V；电流 10UA/100UA/1MA/10MA/100MA/1A/2A/10A
- **RELAY_OFF 统一量程**：ACM200_10V/10MA，FOVIe_10V/10MA（FXVIe_PLUS_10V/10MA），FPVIe_1V/10MA（已从 AI.cpp TM600 样例确认是 10MA 不是 10A）
- **大电流阈值双层**：≥200mA 必须 FPVIe；≥1A 触发三段式+BUS

### 数据格式
- **TestItemMeta JSON**（dual-parse-agent.md 定义）：functionName/testType/params[]/hardwareInit[]/softwareInit/pinsInvolved[]/resourcesInvolved[]/floatingPairs[]/activeFetPairs[]/voltageInference
  - hardwareInit[]: {cmd:vset|iset, pin:小写, value, time:"100e-6", ignore:0}
  - floatingPairs[]: {type:vset|iset, pinA, pinB, deltaV, fullNotation}
- **资源分配表.csv**（D:\Newtest\CLAUDE_PROCESS\资源分配表.csv）列：Pin Name/Resource Name/Connect Relay to Resource/Relay to FPVI_BUS/P2P Relay/Type/Cap1/Cap2/PULL_UP RESISTOR/Prority。Type 列取值：ACM200/FOVI/QVM/QTMU/FPVI/DCM
- **Pin_Channel_define.h**：`extern FXVIe_PLUS SW1_SW2_FXVI;` 形式（对象名+类型）

### 真实代码样例（AI.cpp / test.cpp，对拍基准）
- 普通：`VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON); delay_ms(1);` 下电 `Set(FV,0,FXVIe_PLUS_10V,FXVIe_PLUS_10MA,RELAY_ON); delay_ms(1); Set(FV,0,FXVIe_PLUS_10V,FXVIe_PLUS_10MA,RELAY_OFF);`
- 浮动大电流 TM600（test.cpp）：FPVI.Set(FV,0,FPVIe_1V,FPVIe_2A,FPVI_RELAY_ON)→delay_us(200)→台阶 ramp（BTST_ACM/PMID_FOVI 每步5V）→ 大电流 FPVI.Set(FV,0)→FPVI.Set(FI,0)→FPVI.SetClamp(25,25)→FPVI.Set(FI,1,...)→delay_us(2000)→MeasureVI→FPVI.Set(FI,0)
- **真实源表对象名**（AI.cpp 现行命名，比 pin-resource-map 旧速查表权威）：VBAT_PD3_FXVI、VAC123_AMUX_ACM、VCC_VMCU_FXVI、VBUS_DRVH1_ACM、AMUX_PGND_FXVI、NQON_HG1_ACM、QTMU_GP、FPVI

### 现有脚本模式（可复用）
- **gen_tm206_425.py**：`blocks=[]` + 模板字符串 + 构建器函数 `.replace('@XX@', val)` + 末尾追加。此模式只用于直接写文件，我们的新脚本是 CLI 输出，用 print 即可
- **verify_relay_trace.py** 关键可复用函数：
  - `read_enc(path)`：utf-8-sig→utf-8→gbk→latin-1 逐级回退解码（DLP 透明加密环境）
  - 错误累积 errors/warns + `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` + 成功 print 'XXX PASSED' exit 0 / FAIL exit 1
- **AI.cpp 源表 extern 声明在文件顶部**，`#define Kxx` 也在 AI.cpp 顶部

## 你的任务：设计具体实现方案

请设计并输出（中文，尽量具体到可执行）：

1. **gen_power_sequence.py 的完整模块结构**：函数清单（如 parse_hw_init / select_range / gen_power_on / gen_power_off / gen_power_state / build_code_block），每个函数的输入输出
2. **量程选择算法**：给定 源表类型(ACM200/FXVIe_PLUS/FPVIe) + 设定值 + 是force还是relay_off → 返回量程常量。写清楚查表逻辑（≥2× 且 ≤90% 边界怎么处理）
3. **Pin_Channel_define.h 解析**：如何从 extern 声明提取"对象名→类型"映射；对象名结尾(_ACM/_FXVI/FPVI)与类型的对应规则
4. **无资源分配表时（B 路径）**：pin→源表映射的输入接口设计——CLI 参数怎么传（如 --pin-map 指向一个 JSON 或直接靠 resourcesInvolved[] + Pin_Channel_define.h）；明确脚本在"无资源分配表但有 resourcesInvolved + Pin_Channel_define.h"时能否自行确定源表类型
5. **输出格式**：上电代码块/下电代码块/PowerState JSON 的精确文本格式（含注释 `// ====== Step 2: Power On ======` 等），与 AI.cpp 风格一致
6. **CLI 接口**：`python gen_power_sequence.py --meta meta.json [--pin-map map.json]` 的参数设计，--verify 对拍模式
7. **verify 对拍设计**：如何从 AI.cpp 提取现有函数的上电/下电段落与脚本输出 diff；diff 不一致时怎么报告（哪些差异可接受如注释格式、哪些必须一致如 Set 行）
8. **规则→函数覆盖映射表**：把 R-PON-01~08 / R-POFF-01~06 / R-FLT / R-RNG / R-SRC / R-ST 每条规则映射到脚本的具体函数名（这是"规则被涵盖"的核心交付物）
9. **仍需保留 agent 的部分**：明确哪些输入必须由 agent/用户提供（fetPairs、Sense 通路继电器等），脚本以什么形式接收

请阅读需要确认的文件（read-only）：power-on-agent.md、power-off-agent.md、sources/acm200.md、fovie.md、fpvie.md、Pin_Channel_define.h（如可读）、verify_relay_trace.py、资源分配表.csv。输出完整设计方案。

### 2026-08-09 10:45:13 [assistant]

我将先探索项目结构和关键文件，然后输出完整设计方案。让我先了解项目目录。
- [tool] Bash
- [tool] Glob

### 2026-08-09 10:45:19 [assistant]

我已了解项目结构。现在并行读取关键文件。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:45:21 [assistant]

现在查找并读取 Pin_Channel_define.h、verify_relay_trace.py、资源分配表.csv 和其他关键文件。
- [tool] Glob
- [tool] Read
- [tool] Read

### 2026-08-09 10:45:23 [assistant]

读取 Pin_Channel_define.h、gen_tm206_425.py、dual-parse-agent.md 和 pin-resource-map.md。
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:45:27 [assistant]

读取 gen_tm206_425.py 的脚本模式、relay.h、以及 AI.cpp 中的实际上电/下电代码用于对拍设计。
- [tool] Read
- [tool] Bash

### 2026-08-09 10:45:32 [assistant]

现在查看 AI.cpp 中的浮动源/大电流序列和 relay.h 的继电器常量定义。
- [tool] Grep
- [tool] Grep
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:45:38 [assistant]

查看 test.cpp 的 TM600 浮动大电流段详细代码和 RELAY 常量定义位置。
- [tool] Read
- [tool] Grep

### 2026-08-09 10:45:42 [assistant]

查看规则注册表、命名规范、单位规范和 RELAY 常量的定义位置。
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:45:44 [assistant]

搜索 R-PON / R-POFF / R-FLT / R-RNG / R-SRC / R-ST 规则编号的定义位置，以及查看 knowledge 中相关规则的原始定义。
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:45:51 [assistant]

检查 PROGRESS.md 和 daylog 了解转换任务的最近上下文，并查看 references 目录中的参考样例。
- [tool] Bash
- [tool] Read

### 2026-08-09 10:45:57 [assistant]

查看 daylog、reference 样例、以及 RELAY 常量/量程常量的定义位置。
- [tool] Read
- [tool] Read

### 2026-08-09 10:46:04 [assistant]

检查 AI.cpp 中 TM600/浮动大电流样例是否存在，以及 RELAY/量程常量定义位置。
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:46:07 [assistant]

查找量程/RELAY 常量的宏定义位置。
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:46:12 [assistant]

查看普通 3.7V 上电样例在 AI.cpp 中的真实形态，以及 relay.h 内容。
- [tool] Grep
- [tool] Read

### 2026-08-09 10:46:42 [assistant]

查看 AI.cpp 前 300 行，理解普通上电中电流量程(10MA/100UA/100MA)的选用差异。
- [tool] Read

### 2026-08-09 10:47:48 [assistant]

检查 AI.cpp 中 FPVI 的使用情况（浮动/大电流是否存在），并确认 test.cpp 的 TM600 与参考样例的差异。
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:47:51 [assistant]

查看经验库中的 power-sequence 模式记录，以及 measure-agent 如何生成上电/下电（了解调用边界）。
- [tool] Read
- [tool] Grep

### 2026-08-09 10:47:54 [assistant]

阅读主 Skill 中上电/下电的调用上下文。
- [tool] Read

### 2026-08-09 10:47:56 [assistant]

阅读 CLAUDE.md 架构原则和 verify_tm206_425.py 的校验模式。
- [tool] Read
- [tool] Read

### 2026-08-09 10:47:59 [assistant]

查看源表规则.txt 确认量程边界处理的权威表述。
- [tool] Read

### 2026-08-09 10:48:14 [assistant]

查看 AI.cpp 中 iset（FI）模式的源表调用形态，确定 FI 模式的 vRange 选择。
- [tool] Grep

### 2026-08-09 10:49:17 [assistant]

确认 FPVI 对象名的定义方式（extern 声明中只有 FPVI0/FPVI1，代码却用 `FPVI`）。
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:49:20 [assistant]

查看 AI.cpp 头部与 Test_Method 头文件，确认 FPVI 对象与量程宏的来源。
- [tool] Read
- [tool] Grep

### 2026-08-09 10:50:49 [assistant]

我已收集齐所有关键事实。现在输出完整设计方案。

---

# gen_power_sequence.py 实现方案（上电/下电代码生成脚本）

## 0. 关键事实结论（基于实际读取确认）

- **AI.cpp 77 个函数全部是普通/多源（ACM200 + FXVIe_PLUS）**，无 FPVI/浮动/大电流用例；TM600 浮动大电流基准在 `test.cpp:940-1049` 与 `.claude/references/tm600-normal-highcurrent.cpp`。因此三类对拍中"浮动大电流(TM600)"必须以 test.cpp/reference 为基准（`--verify-src` 可指）。
- **对象名 ≠ 资源表名**：资源分配表 Resource Name 是逻辑名（`VBAT_ACM`/`PMID_FOVI`/`VAC123_ACM`），Pin_Channel_define.h 的 extern 对象名才是代码里真正用的（`VBAT_PD3_FXVI`/`PMID_HG2_FXVI`/`VAC123_AMUX_ACM`）。二者仅共享 **PIN 大写 token**。这是 pin→object 映射必须由调用方解析、脚本不做逻辑名→extern 推断的核心原因。
- **量程/RELAY 常量**（`FXVIe_PLUS_10V`、`ACM200_10MA`、`FPVIe_1V`、`FXVIe_PLUS_RELAY_ON`）来自 AccoTEST 框架头（`C:\AccoTEST\...\INCLUDE\FXVIe.h`），不在本仓库；脚本只负责按类型拼出**正确字面量**。
- **RELAY_OFF 统一量程**：ACM200→`10V/10MA`，FXVIe_PLUS→`10V/10MA`，FPVIe→`1V/10MA`（test.cpp:1042 实锤是 `FPVIe_10MA`，不是 10A）。
- **继电器前缀特例**：FPVI 量程前缀 `FPVIe_`，但继电器常量是 `FPVI_RELAY_ON/OFF`（无 `e`）；FXVIe_PLUS/ACM200 两者前缀一致。
- **FV 模式电流量程是判断输入，非确定推导**：AI.cpp 同一 VBAT=3.7V，iRange 有 `10MA`(TM000)、`100UA`(TM001_2/3)、`100MA`(TM001_4+) 三种，取决于该测试 DUT 预期电流。脚本必须接收 `currentLimit` 覆盖，否则默认 100MA 会与 Iq 类函数对拍失败。
- **浮动 ramp 终点来自 voltageInference**：`vset[bst2sw,5]` 的 hardwareInit 只给初值，最终 BST=20/PMID=15 来自电压推断——脚本必须接收 `rampProfile`（agent 提供），不能从 hardwareInit 推。
- **B 路径定论**：脚本**不需要**资源分配表.csv。只要拿到 `{pin: object}` 映射（A 由调用方从 CSV 翻译、B 由 relay-agent 从 SCH-Connect-Map 补齐），脚本就能从 Pin_Channel_define.h 自行解析类型。资源分配表只影响"pin→object 映射怎么来"，不影响脚本内部。

---

## 1. 模块结构（函数清单 + 输入/输出）

```text
gen_power_sequence.py
│
├── A. 输入层（读文件）
│   read_enc(path) -> str                       # utf-8-sig→utf-8→gbk→latin-1 回退（DLP 透明加密）
│   load_meta(path) -> dict                     # TestItemMeta JSON
│   load_pin_map(path) -> dict                  # --pin-map JSON（见 §4）
│   load_pin_channel_define(path) -> dict       # extern 解析（见 §3）
│
├── B. 解析/解析层
│   parse_extern_types(src) -> dict             # {objectName: typeName}（extern 权威）
│   resolve_source_type(pin_map, extern_map, builtin) -> dict  # 每 pin 的 {object,type,range_prefix,relay_prefix}
│   resolve_all_sources(meta, pin_map, extern_map) -> list     # 输出 Source 列表（去重、含 FPVI 附加）
│   parse_floating_pairs(meta) -> list          # 校验 floatingPairs[]（type/pinA/pinB/deltaV）
│
├── C. 量程/模式层
│   mode_for_cmd(cmd) -> "FV"|"FI"              # vset→FV, iset→FI（R-PON-01）
│   select_range(stype, kind, value) -> str     # 量程常量（R-RNG，见 §2）
│   relay_off_ranges(stype) -> (vRange,iRange)  # R-POFF-06 统一量程
│   relay_const(stype, on_off) -> str           # 继电器常量（含 FPVI 特例）
│   classify_power_off(power_state, meta) -> "normal"|"floating"|"high_current"  # R-POFF-01
│   is_high_current(pairs, meta) -> bool        # ≥1A 判定
│
├── D. 上电生成层
│   gen_simple_power_on(sources, meta) -> [str] # R-PON-06 普通
│   gen_floating_ramp(floating_pairs, ramp_profile, sources) -> [str]  # R-PON-07 + R-FLT 三阶段台阶
│   gen_high_current_init(fpvi_source, target) -> [str]  # R-PON-08 三段式（FV=0→FI=0→Clamp→FI=target）
│   gen_power_on(meta, sources) -> [str]         # 顶层：按 floatingPairs 有无/大电流分支组合
│
├── E. 下电生成层
│   gen_normal_power_off(sources) -> [str]       # R-POFF-02 三步
│   gen_floating_power_off(power_state, sources) -> [str]  # R-POFF-03 反转 ramp + R-POFF-04 FPVI最后
│   gen_high_current_off(fpvi_source) -> [str]   # R-POFF-05 FI=0→FV=0→OFF
│   gen_power_off(power_state, meta, sources) -> [str]  # 顶层：按 classify_power_off 分支
│
├── F. PowerState / 拼装层
│   build_power_state(meta, sources, up_seq) -> dict  # 4 字段：sources/floatingPairs/upSequence/finalVoltages
│   build_code_block(lines, header_comment) -> str     # 4 空格缩进 + `// ====== Step X: … ======` 注释
│   emit_sections(on_block, state_json, off_block) -> str  # stdout 带 `###SECTION:…###` 分隔符
│
├── G. verify 层（--verify）
│   extract_ai_cpp_power_sections(src, func_name) -> {on_lines, off_lines}   # 从 AI.cpp/test.cpp 抽取
│   normalize_set(line) -> dict                  # Set 行 → 字段 dict（去空白/注释）
│   compare_sets(generated, extracted, category_map) -> (errors, warns, infos)  # §7
│   run_verify(args) -> int                      # 退出码
│
├── H. 规则审计层
│   RULE_COVERAGE = { rule_id: [func_names], ... }   # §8 核心交付物
│   audit_rules() -> str                        # --audit-rules 打印映射表 + 断言可达
│
└── I. main / argparse
    main() -> int                               # --meta --pin-map --verify --verify-src --verify-func …
```

### 各函数 I/O 要点

- `resolve_source_type` 输出：`{ "VBAT": {"object":"VBAT_PD3_FXVI","type":"FXVIe_PLUS","range_prefix":"FXVIe_PLUS_","relay_prefix":"FXVIe_PLUS_"}, "PMID":{...,"type":"FXVIe_PLUS"}, "FPVI": {"object":"FPVI","type":"FPVIe","relay_prefix":"FPVI_"} }`
- `gen_simple_power_on` 输入 Source 结构：`{"pin":"VBAT","object":"VBAT_PD3_FXVI","type":"FXVIe_PLUS","cmd":"vset","mode":"FV","value":4.2,"vRange":"FXVIe_PLUS_10V","iRange":"FXVIe_PLUS_100MA","relay_on":"FXVIe_PLUS_RELAY_ON"}`；输出字符串行（含 DFT 指令注释）。
- `build_power_state` 的 `sources[]` 直接沿用上电 Source（去重），`upSequence[]` 记录上电实际发出的每一步（step/source/mode/value/note/delay），`finalVoltages{}` = 各 pin 最终电压（来自 rampProfile 或 hardwareInit value）。

---

## 2. 量程选择算法

```python
RANGE_TABLES = {
  "ACM200": {
    "V": [("ACM200_3p6V", 1.8), ("ACM200_10V", 5.0), ("ACM200_40V", 20.0)],
    "I": [("ACM200_1UA", 500e-9), ("ACM200_10UA", 5e-6), ("ACM200_100UA", 50e-6),
          ("ACM200_1MA", 500e-6), ("ACM200_10MA", 5e-3), ("ACM200_100MA", 50e-3),
          ("ACM200_200MA", 100e-3)],
  },
  "FXVIe_PLUS": {                      # 即 fovie.md 的 FOVIe 量程表，前缀用 extern 类型
    "V": [("FXVIe_PLUS_1V", 0.5), ("FXVIe_PLUS_2V", 1.0), ("FXVIe_PLUS_5V", 2.5),
          ("FXVIe_PLUS_10V", 5.0), ("FXVIe_PLUS_20V", 10.0), ("FXVIe_PLUS_40V", 20.0)],
    "I": [("FXVIe_PLUS_10UA", 5e-6), ("FXVIe_PLUS_100UA", 50e-6), ("FXVIe_PLUS_1MA", 500e-6),
          ("FXVIe_PLUS_10MA", 5e-3), ("FXVIe_PLUS_100MA", 50e-3), ("FXVIe_PLUS_1A", 500e-3)],
  },
  "FPVIe": {
    "V": [("FPVIe_100MV", 50e-3), ("FPVIe_1V", 0.5), ("FPVIe_2V", 1.0), ("FPVIe_5V", 2.5),
          ("FPVIe_10V", 5.0), ("FPVIe_20V", 10.0), ("FPVIe_40V", 20.0), ("FPVIe_100V", 50.0)],
    "I": [("FPVIe_10UA", 5e-6), ("FPVIe_100UA", 50e-6), ("FPVIe_1MA", 500e-6),
          ("FPVIe_10MA", 5e-3), ("FPVIe_100MA", 50e-3), ("FPVIe_1A", 500e-3),
          ("FPVIe_2A", 1.0), ("FPVIe_10A", 5.0)],
  },
}
RELAY_OFF_RANGES = { "ACM200": ("ACM200_10V","ACM200_10MA"),
                     "FXVIe_PLUS": ("FXVIe_PLUS_10V","FXVIe_PLUS_10MA"),
                     "FPVIe": ("FPVIe_1V","FPVIe_10MA") }   # R-POFF-06（FPVIe 10MA 已对拍确认）
RELAY_CONST = { ("ACM200",True):"ACM200_RELAY_ON", ("ACM200",False):"ACM200_RELAY_OFF",
                ("FXVIe_PLUS",True):"FXVIe_PLUS_RELAY_ON", ("FXVIe_PLUS",False):"FXVIe_PLUS_RELAY_OFF",
                ("FPVIe",True):"FPVI_RELAY_ON", ("FPVIe",False):"FPVI_RELAY_OFF" }  # FPVI 无 e
```

```python
def select_range(stype, kind, value):
    """kind: 'V'|'I'；value: V 或 A。返回量程常量名。
    stype ∈ {ACM200, FXVIe_PLUS, FPVIe}（来自 extern 权威类型）。"""
    table = RANGE_TABLES[stype][kind]
    for name, table_max in table:            # 表已按 table_max 升序
        if value <= table_max:               # 边界含等号：value==table_max 取本档
            return name
    raise RangeError(f"{stype} {kind}: 值 {value} 超最大量程")
```

**边界处理说明（"≥2× 且 ≤90%"）：**

1. 表项 `table_max` 在知识库里写的是"该档安全设定上限"，它恒等于**档位标称满量程的 50%**：`ACM200_3p6V`→1.8V、`ACM200_100MA`→50mA、`FPVIe_2A`→1A、`FPVIe_100MV`→50mV。因此"量程(满量程) ≥ 2×设定值" ⟺ "table_max ≥ 设定值"。**查表取第一个 table_max ≥ value 即同时满足 ≥2× 与 ≤90% 两条约束。**
2. **≤90% 约束自动满足**：value ≤ table_max = 0.5×满量程 < 0.9×满量程，无需额外判断。算法里保留一个防御性断言：若某档 `value > 0.9*满量程`（仅在表数据被改坏时触发）→ WARN。
3. **等号边界**：`value == table_max`（如 FI=50mA 与 100MA 档 table_max=50mA）取本档。这正好对上 AI.cpp `VCC_VMCU_FXVI.Set(FI, 0.05, …, FXVIe_PLUS_100MA, …)`（2×50mA=100mA=满量程，取 100MA）。
4. **已知手写代码违反 ≥2× 的案例**（AI.cpp:2917 `VDM_SDA_ACM.Set(FI,1e-5,…,ACM200_10UA)`：10μA 用 10UA 档，2×10μA>10μA）：脚本严格规则会输出 `ACM200_100UA`，对拍时**归类为 WARN**（手写码松弛，需人审，见 §7）。

**F 值 / 量程选取分工：**

| 模式 | 强制值量程（select_range，确定性，对拍必一致） | 合规量程（非强制那档） |
|---|---|---|
| FV（vset） | vRange = select_range(type,'V', value) | iRange = 由 `currentLimit` 经 select_range(type,'I', currentLimit) 选；未提供→默认 `100MA`（ACM/FXVIe_PLUS 主流量程，见 §1 关键事实） |
| FI（iset, 非FPVI） | iRange = select_range(type,'I', value) | vRange = 默认 `10V`（AI.cpp 全部 iset 用 ACM200_10V / FXVIe_PLUS_10V） |
| FPVI 大电流 | iRange = select_range('FPVIe','I', target)（1A→`FPVIe_2A`） | vRange = 固定 `FPVIe_1V`（大电流小压降） |
| FPVI 浮动等电位 | 固定 `FPVIe_1V, FPVIe_10A`（R-FLT，用户规则） | — |

> 决策依据：AI.cpp `Set(FI,…)` 的 vRange 恒为 10V、`Set(FV,…)` 的 iRange 大多是 100MA 但 Iq 类是 10MA/100UA——所以"强制值量程"是脚本确定推导、"合规量程"是 agent 判断输入（`currentLimit` 覆盖）。

---

## 3. Pin_Channel_define.h 解析

```python
EXTERN_RE = re.compile(r'extern\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*;')

def parse_extern_types(src):
    """src = read_enc(Pin_Channel_define.h)
    返回 { objectName: typeName }，仅收集 'extern <TYPE> <NAME>;' 形式（本文件 88~142 行）。
    示例: 'extern FXVIe_PLUS SW1_SW2_FXVI;' → {"SW1_SW2_FXVI":"FXVIe_PLUS", ...}"""
    return { m.group(2): m.group(1) for m in EXTERN_RE.finditer(src) }

TYPE_PREFIX = {          # extern 类型 → 量程前缀 / 继电器前缀
  "ACM200":     ("ACM200_",      "ACM200_"),
  "FXVIe_PLUS": ("FXVIe_PLUS_",  "FXVIe_PLUS_"),
  "FPVIe":      ("FPVIe_",       "FPVI_"),     # 继电器前缀特例无 'e'
  # QVMe/QTMUe: 非电源源表，若出现在 power-on 输入则报错（不参与上电）
}
```

**对象名结尾后缀与类型的对应：** extern 类型本身已权威（`ACM200`/`FXVIe_PLUS`/`FPVIe`），**不依赖对象名 `_ACM/_FXVI/FPVI` 后缀猜测**。后缀仅在"用资源表逻辑名兜底匹配 extern"时作为校验线索（见 §4）。

**FPVI 特例处理：** Pin_Channel_define.h 只有 `FPVI0/FPVI1/FPVI_GP`，代码用对象名 `FPVI`（框架全局，未在本仓库 extern）。脚本内置 `BUILTIN_TYPES = {"FPVI": "FPVIe", "QVM_GP": "QVMe", "QTMU_GP": "QTMUe"}`，解析顺序：**pin-map 显式 `type` > extern 表 > builtin 表**；仍未命中 → 该 pin 报错列出（见 §4 错误策略）。

---

## 4. 无资源分配表时（B 路径）的输入接口

### 结论
- **脚本不需要资源分配表.csv**。它只消费 `--pin-map` 的 `{pin: object}`（+可选 `type`/`currentLimit`/`rampProfile`）+ Pin_Channel_define.h。
- **A 路径**：调用方（主 Skill 内 dual-parse/relay 组合）从 资源分配表.csv 的 `Pin Name` + `Resource Name` 列，结合 Pin_Channel_define.h extern，把逻辑名翻译成 extern 对象名后生成 `--pin-map`。
- **B 路径**：relay-agent 从 SCH-Connect-Map 查通路后直接输出 extern 对象名（resourcesInvolved 由它补齐），生成同样的 `--pin-map`。**两路径产出同一 schema，脚本不分 A/B。**

### `--pin-map` JSON schema
```json
{
  "comment": "A路径: dual-parse/relay从资源分配表.csv翻译; B路径: relay-agent从SCH-Connect-Map补齐",
  "pinMap": {
    "VBAT": { "object": "VBAT_PD3_FXVI" },
    "VAC1": { "object": "VAC123_AMUX_ACM" },
    "SW":   { "object": "SW1_SW2_FXVI" },
    "FPVI": { "object": "FPVI", "type": "FPVIe" }
  },
  "currentLimit": { "VBAT": 0.05 },
  "rampProfile": [
    { "pin": "VBAT", "targetV": 4.2 },
    { "pin": "SW",   "targetV": 0 },
    { "pin": "BST",  "targetV": 20 },
    { "pin": "PMID", "targetV": 15 }
  ],
  "stepV": 5.0
}
```

### "无资源分配表但有 resourcesInvolved + Pin_Channel_define.h" 能否自行确定类型？
- **能（部分）**：只要给出 extern 对象名，脚本就能从 Pin_Channel_define.h 确定类型。B 路径 relay-agent 补的 resourcesInvolved 若已是 extern 对象名（`VBAT_PD3_FXVI`），脚本可直接解析。
- **不能（逻辑名）**：若 resourcesInvolved 仍是资源表逻辑名（`VBAT_ACM`/`PMID_FOVI`），它们与 extern 名不同，脚本**不做**逻辑名→extern 的静默推断（脆弱）。提供 `--resolve-from-resources` 兜底：按命名规范拆 `PIN1_PIN2_…_<类型>`，用 PIN token 在 extern 表里做包含匹配 + 类型族校验（ACM200↔ACM、FOVI/FXVI↔FXVIe_PLUS、FPVI↔FPVIe），命中唯一才采纳，否则 **ERROR 列出未解析 pin**；该模式默认关闭、建议始终走 pin-map。
- **FPVI 判定**：resourcesInvolved 含 `"FPVI"`（或 floatingPairs 存在）即视为 FPVIe 附加源（R-SRC + R-FLT）。资源表 Type 列 `FOVI`/`ACM200` 不参与脚本判定，仅 A 路径调用方翻译时用。

### 缺失策略（清晰报错，不静默）
- 某 hardwareInit pin 不在 pinMap → ERROR `未解析源表: pin=<PIN>`（提示 A 查资源表 / B 查 SCH-Connect-Map）。
- hardwareInit pin 在 pinMap 但 object 在 extern 与 builtin 均未命中 → ERROR `未知源表对象: <object>`。
- 跨 pin（含 `2`）但 floatingPairs 缺失 → WARN（R-FLT 要求 pair 定义）。

---

## 5. 输出格式（精确文本）

stdout 三段式（主 Skill 按 `###SECTION:…###` 拆包拼装进模板 Step2/Step5 占位）：

```text
###SECTION:POWER_ON###
    // ====== Step 2: 上电 ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // vset[vac1,5,100e-6,0] → VAC1=5V
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
###SECTION:POWER_STATE###
{
  "sources": [
    { "name": "VBAT_PD3_FXVI", "mode": "FV", "finalValue": 3.7, "vRange": "FXVIe_PLUS_10V", "iRange": "FXVIe_PLUS_100MA" },
    { "name": "VAC123_AMUX_ACM", "mode": "FV", "finalValue": 5.0, "vRange": "ACM200_10V", "iRange": "ACM200_100MA" }
  ],
  "floatingPairs": [],
  "upSequence": [
    { "step": 1, "source": "VBAT_PD3_FXVI", "mode": "FV", "value": 3.7, "note": "vset[vbat,3.7]", "delay": "1ms" },
    { "step": 2, "source": "VAC123_AMUX_ACM", "mode": "FV", "value": 5.0, "note": "vset[vac1,5]", "delay": "1ms" }
  ],
  "finalVoltages": { "VBAT": 3.7, "VAC1": 5.0 }
}
###SECTION:POWER_OFF###
    // ====== Step 5: 下电 ======
    // 步骤1: 所有源归零(RELAY_ON保持量程)
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // 步骤2: RELAY_OFF(统一10V/10MA)
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
```

**浮动/大电流样式**（与 test.cpp TM600 对拍一致）：

```text
    // ====== Step 2: 上电 (台阶式 ramp, BST始终领先PMID≈5V) ======
    // FPVI初始化: FV=0 等电位 (PMID2SW 大电流预备)
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);
    // 非浮动源直接上电
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    // 台阶1: BST=5, PMID=0 (每步≤5V)
    BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    ...
    // ====== Step 5: 下电 (台阶式) ======
    ...
    // FPVI最后断开
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);
```

**格式约定**：统一 4 空格缩进；每条 Set 前有 `// <DFT指令> → <解读>` 注释（agent 风格）；延迟常量 `delay_ms(1)`（普通）、`delay_us(200)`（台阶/等电位）、`delay_us(2000)`（大电流稳定）作为模块级常量可配。

---

## 6. CLI 接口

```text
python gen_power_sequence.py --meta <TestItemMeta.json>
                            [--pin-map <pin_map.json>]          # 推荐；缺失则用 --resolve-from-resources 兜底
                            [--define <Pin_Channel_define.h>]   # 默认 DALI/Pin_Channel_define.h
                            [--resolve-from-resources]          # 允许从 resourcesInvolved 逻辑名兜底(默认关闭)
                            [--current-limit <json>]            # 覆盖 pin-map.currentLimit
                            [--ramp-profile <json>]             # 覆盖 pin-map.rampProfile
                            [--mode power-on|power-off|both]    # 默认 both
                            [--no-state]                        # 不输出 POWER_STATE 段
                            [--verify <src.cpp>]                # 对拍模式：src 默认 DALI/AI.cpp
                            [--verify-func <TMxxx>]             # 指定对拍函数；缺省自动扫所有函数
                            [--verify-src test.cpp]             # 浮动大电流类指 test.cpp/reference
                            [--warn-as-error]                   # WARN 视为 FAIL
                            [--audit-rules]                     # 打印 R-PON/R-POFF/…→函数覆盖表并自检
```

- 无 `--verify`：生成并打印三段（或按 `--mode` 截断），exit 0。
- `--audit-rules`：打印 §8 映射表 + 断言 `RULE_COVERAGE` 每个 rule_id 的 function 在 `dir()` 中存在、且被 `gen_power_on`/`gen_power_off` 调用链可达 → 不满足 FAIL（这是"规则被涵盖"的机器自检）。
- 参数校验：`--meta` 必填；pin-map 缺失且未开兜底 → 对每个未解析 pin 报 ERROR 并 exit 1。

---

## 7. verify 对拍设计

### 抽取
- 复用 `verify_relay_trace.py` 的 `read_enc`/`fn_blocks`（`DUT_API int (TM\d+_\w+)\(short funcindex` 切函数边界）。
- 在目标函数内，按 `// ====== Step 2:` 与 `// ====== Step 3:` 切"上电段"、`// ====== Step 5:` 与 `// ====== Step 6:` 切"下电段"。
- 抽取所有 `\w+\.Set\((FV|FI), …\)` 行 → 解析为字段 dict：`{object, mode, value, vRange, iRange, relay}`（归一化：去空白、小写化不必要、数值 `4.2` vs `4.2` 精确比较、`1` vs `1.0` 归一）。

### 对比与归类
对每个 Set 行做字段级 diff，三类差异：

| 类别 | 范围 | 处理 |
|---|---|---|
| **ERROR（必须一致）** | object 名、mode(FV/FI)、强制值、RELAY_ON/OFF、**强制值量程**（FV 的 vRange / FI 的 iRange） | 任何不一致 → FAIL，并注明"脚本规则 R-RNG 预期 X，AI.cpp 是 Y" |
| **WARN（可接受/需人审）** | 合规量程（FV 的 iRange / FI 的 vRange）；AI.cpp 违反 ≥2× 的强制量程（如 10μA 用 10UA）；FPVI 等电位 iRange 10A vs 2A 版本差异；浮动 ramp 中 Set 的先后次序（只要最终态一致） | 列 WARN，`--warn-as-error` 才 FAIL |
| **INFO（忽略）** | 注释、delay 位置与分组（`delay_ms(1)` 每条 vs 合并）、SetClamp/MeasureVI/GetMeasResult 等非上电下电行 | 仅 INFO 列表 |

- 汇总后 `print('POWER SEQUENCE PASSED')` exit 0；有 ERROR → `print('*** FAIL ***')` + 逐条 diff + exit 1（沿用 verify_relay_trace.py 惯例）。
- 三类基准：
  1. **普通 3.7V**：AI.cpp TM000 系（`VBAT_PD3_FXVI.Set(FV,3.7, FXVIe_PLUS_10V, FXVIe_PLUS_10MA/100MA, …)`）。
  2. **多源**：AI.cpp TM206/TM001_2（VBAT + VAC123，三步下电）。
  3. **浮动大电流 TM600**：`--verify-src test.cpp` 或 `.claude/references/tm600-normal-highcurrent.cpp`（AI.cpp 无此例）。参考样例与 test.cpp 在 FPVI 初始化 iRange（10A vs 2A）有出入 → 该字段归 WARN。

---

## 8. 规则 → 函数覆盖映射表（核心交付物）

脚本内置 `RULE_COVERAGE`，`--audit-rules` 输出并自检：

| 规则ID | 内容 | 函数 | 覆盖点 |
|---|---|---|---|
| R-PON-01 | vset→FV / iset→FI | `mode_for_cmd()` | 分支 cmd |
| R-PON-02 | MV 无 FI→FI=0 + 最小量程10UA | `apply_mv_no_fi()`（在 `gen_simple_power_on` 内调用） | `params[].check=MV` 且该 pin 无 iset 时，补 `Set(FI,0,…,<TYPE>_10UA,…)` |
| R-PON-03 | 浮动源识别（pin 含 `2`→跨Pin） | `parse_floating_pairs()` + `resolve_all_sources()` | 校验/补 FPVI 附加源 |
| R-PON-04 | 量程 ≥2× 取最小档 | `select_range()` | 强制值量程 |
| R-PON-05 | force/测量值 ≤ 量程90% | `select_range()` 内防御断言 | 表坏才触发 |
| R-PON-06 | 普通上电模板 + delay_ms(1) | `gen_simple_power_on()` | 逐条 Set |
| R-PON-07 | 浮动三阶段（PinB基准→FPVI FV=0→PinA台阶≤5V, delay_us(200)） | `gen_floating_ramp()` | 三阶段次序 |
| R-PON-08 | 大电流三段式（FV=0→FI=0→SetClamp(25,25)→FI=target） | `gen_high_current_init()` | 四行固定序 |
| R-POFF-01 | 下电类型判定 | `classify_power_off()` | floatingPairs+type=vset / FI≥1A / 普通 |
| R-POFF-02 | 普通三步（归零→delay_ms(1)→统一10V/10MA OFF） | `gen_normal_power_off()` | 三步序 |
| R-POFF-03 | 浮动下电反转 upSequence（PinA先降→PinB→其他→PinA归零, ≤5V, delay_us(200)） | `gen_floating_power_off()` | 反转 + 台阶 |
| R-POFF-04 | FPVI 永远最后 RELAY_OFF | `gen_floating_power_off()` 尾部 + `relay_const()` | 排序 |
| R-POFF-05 | 大电流下电 FI=0→FV=0→OFF | `gen_high_current_off()` | 三行序 |
| R-POFF-06 | RELAY_OFF 统一量程（ACM200_10V/10MA、FXVIe_PLUS_10V/10MA、FPVIe_1V/10MA） | `relay_off_ranges()` | 常量表 |
| R-FLT | 浮动等电位不可省、PinA=PinB+ΔV、每步≤5V | `gen_floating_ramp()` + `gen_floating_power_off()` | ΔV/等电位行 |
| R-RNG | 量程≥2×、≤90% | `select_range()` | 查表 |
| R-SRC | 源类型以 extern 声明为权威 | `parse_extern_types()` + `resolve_source_type()` | extern 解析 |
| R-ST | 台阶每步≤5V + delay_us(200)；普通 delay_ms(1)；大电流稳定 delay_us(2000) | `gen_floating_ramp()`/`gen_floating_power_off()`/`gen_high_current_init()` | 步长与延迟常量 |

> 交付动作：转换落地时把上表 R-PON-01~08 / R-POFF-01~06 / R-FLT / R-RNG / R-SRC / R-ST 登记进 `.claude/knowledge/standards/rules-registry.md` 的 active 区（当前注册表只有 MR-000/FR-001~003，尚无 power 规则编号）。

---

## 9. 仍需保留 agent 的部分（脚本的输入边界）

脚本是**确定性发射器**，以下"判断"必须由 agent/用户提供，脚本以 JSON 字段接收：

1. **pin→源表对象映射**（`--pin-map`）：A 由 dual-parse/relay 从资源分配表.csv 翻译 extern 名；B 由 relay-agent 从 SCH-Connect-Map 补齐。**脚本不查资源表、不做逻辑名→extern 静默推断**。
2. **FV 源合规电流量程**（`currentLimit`，每 pin 最大预期电流 A）：Iq 类 100UA/10MA、电源类 100MA 的判断在 agent（依据 params/测试规格）；脚本默认 100MA + 覆盖。
3. **浮动 ramp 终点与顺序**（`rampProfile`）：BST=20/PMID=15 等终值来自 `voltageInference`/`activeFetPairs`，脚本只把"目标序列"切确定性台阶（stepV=5、delay_us(200)）。无 rampProfile 时脚本退化为"按 hardwareInit value 单步"，并对浮动 pair 缺失终值给 WARN。
4. **≥200mA→FPVIe / ≥1A→三段式+BUS 的资源选型**：由 relay-agent 决定"哪个源挂在 FPVI、BUS 继电器闭哪些"；脚本只消费 `floatingPairs`+pin-map 里的 FPVI 对象，不判资源竞争。
5. **Sense 通路 / Cap / PU / P2P 继电器**：`cbite.SetOn(...)` 与 Cap/PU/P2P 功能规则完全归 relay-agent 与 verify_relay_trace.py，**脚本不生成任何继电器代码**。
6. **MV 无 FI 的意图**：某源是"测量源(FI=0)"还是"电源源"由 dual-parse/params[].check 定；脚本在 meta 带 `mvNoFiPins: [...]` 时执行 R-PON-02，否则默认按电源源处理。
7. **testType 框架**：Toggle/Trim 的 Step3~6（寄存器/测量/LogData）不在脚本范围。

---

## 实施顺序建议

1. 落地 `gen_power_sequence.py` 骨架 + 常量表（RANGE_TABLES/RELAY_OFF_RANGES/RELAY_CONST）+ `read_enc`/`parse_extern_types`/`select_range`（§1 A/B/C + §2/§3）。
2. 实现普通上电/下电（`gen_simple_power_on`/`gen_normal_power_off`）+ PowerState + 三段输出（§5）→ 对拍 AI.cpp 普通与多源类，先全绿。
3. 实现浮动与高电流（`gen_floating_ramp`/`gen_floating_power_off`/`gen_high_current_init`/`gen_high_current_off`）→ 对拍 TM600。
4. 实现 `--verify` 抽取/对比/分类（§7）与 `--audit-rules`（§8）。
5. 主 Skill `nuvolta-codegen.md` 接入：Step4 第 2/5 步改为调用脚本并把三段拼进模板；A/B 两路径生成 `--pin-map`。
6. 将 R-PON/R-POFF 等规则登记进 rules-registry.md。

---

### Critical Files for Implementation
- D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-on-agent.md
- D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-off-agent.md
- D:\Newtest\CLAUDE_PROCESS\.claude\agents\dual-parse-agent.md
- D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\sources\fpvie.md（及 acm200.md / fovie.md）
- D:\Newtest\CLAUDE_PROCESS\DALI\Pin_Channel_define.h
- D:\Newtest\CLAUDE_PROCESS\verify_relay_trace.py（read_enc/fn_blocks/错误累积模式复用）
- D:\Newtest\CLAUDE_PROCESS\test.cpp（TM600 浮动大电流对拍基准，行 940-1049）
- D:\Newtest\CLAUDE_PROCESS\.claude\references\tm600-normal-highcurrent.cpp（同基准权威版）
