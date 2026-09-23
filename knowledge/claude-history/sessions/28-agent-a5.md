# 会话 #28 — 背景：Nuvolta STS8300 ATE 离线代码生成体系。现行权威在 `D:\\Newtest\\CLAUDE_PROCESS`，我准备设计一个优化方案，把 

- 文件：`agent-a5b868ea2c254bf63.jsonl`（项目 subagents）
- 时间：2026-08-23T15:14:38.140Z → 2026-08-23T15:15:45.738Z，大小 0.1 MB
- 用户消息 1 条 / 助手文本 2 段 / 工具调用标记 3 行

---

## 对话正文（工具输出已剥离）

### 2026-08-23 15:14:38 [user]

背景：Nuvolta STS8300 ATE 离线代码生成体系。现行权威在 `D:\Newtest\CLAUDE_PROCESS`，我准备设计一个优化方案，把 codex 迁移产出的「输入哈希冻结」和「材料门硬门禁」两个方法论吸收进现行体系。我需要精确了解现行体系这三个文件的内部结构，以便设计"接缝"（在哪里并入、改哪个函数）。

请精确读取以下文件（用 Read 工具，路径含中文需用绝对路径），返回**精确的结构化内容**（字段名、函数签名、key 名、错误码编号），不要泛泛总结：

1. `D:\Newtest\CLAUDE_PROCESS\proj_config.py`
   - 完整读取。返回：它加载哪些配置字段（inputs/derived/outputs/intermediates 等 key 的全名清单）、`config_from_argv` 和 `load` 的函数签名与返回值结构、路径解析逻辑（如何从 project_config.json 解析出各文件绝对路径）、`_root`/`_config` 等内部字段、是否已有任何哈希/校验逻辑。
   - 目的：我要设计如何把 SHA-256 输入哈希冻结（codex 的 project_manifest.py 功能）并入这里，需要知道现有结构。

2. `D:\Newtest\CLAUDE_PROCESS\.claude\agents\check-agent.md`
   - 返回：检查项总数、P/E/R/H 四层各有哪些检查项（列出错误码编号和一句话含义）、如何新增一个检查项、是否已有任何"材料/黄金代码/参考案例是否被读取"类的检查、是否有"门禁/证据"相关的机制。
   - 目的：我要设计「材料门硬门禁」（材料存在却未读取不得生成）怎么落到 check-agent 或新增脚本，需要知道现有检查体系。

3. `D:\Newtest\CLAUDE_PROCESS\.claude\AGENT_MAP.md`
   - 返回：完整 agent 清单（每个 agent 的名字、触发条件、依赖、产出、状态是否"已脚本化"），特别标注 relay-agent 和 measure-agent 的状态（是否已脚本化、还是仍活跃执行）。

请把三个文件的结论分节返回，附关键文件路径和行号。这些信息将直接用于设计实施计划，准确性优先。

### 2026-08-23 15:14:39 [assistant]

I'll read all three files in parallel to give you the precise structural content.
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-23 15:15:45 [assistant]

三个文件已精确读取完毕。以下为结构化结论（路径 + 行号精确，准确性优先）。

---

## 1. `D:\Newtest\CLAUDE_PROCESS\proj_config.py`（92 行）

### 职责（docstring L1–18）
- 唯一输入入口：读 `project_config.json` → 相对路径解析为绝对路径 + 从 `vs_src_dir` 派生源文件。
- DLP 透明加密兼容：`rb` 读 + utf-8-sig 回退解码（L18、L27–35）。

### 常量
- `_DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_config.json')`（L23–24）

### 内部函数
| 函数 | 行号 | 签名 / 逻辑 |
|---|---|---|
| `_read(path)` | L27–35 | `open(path,'rb')` → 依次尝试 `utf-8-sig` / `utf-8` / `gbk`，全失败则 `utf-8 errors='replace'` |
| `_resolve(root, p)` | L38–42 | `p=str(p)`；`os.path.isabs(p)` → `normpath(p)`；否则 `normpath(join(root, p))` |
| `_resolve_section(root, sec)` | L45–46 | `{k: _resolve(root, v) for k,v in (sec or {}).items()}` — 整段路径化 |

### `load(config_path=None)`（L49–82）
- 默认 `_DEFAULT_CONFIG`；`abspath` 化；不存在则抛 `FileNotFoundError('project_config.json 不存在: '+path)`（L53–54）。
- `data = json.loads(_read(config_path))`；`root = os.path.dirname(config_path)`（L56–57）。

**派生逻辑（L59–68）**：
- `inputs = _resolve_section(root, data.get('inputs'))`
- `vs = inputs.get('vs_src_dir', '')` → 硬编码派生三项：
  - `test_cpp` = `vs/test.cpp`
  - `sub_cpp` = `vs/sub.cpp`
  - `stdafx_h` = `vs/StdAfx.h`
- 显式 `data.get('derived')` 段逐 key 覆盖派生值（L67–68）。

**返回 dict —— 9 个 key（L72–82）**：
```
project          ← data.get('project','')            字符串
project_dir      ← _resolve(root, data.get('project_dir'))（仅当有值）
inputs           ← _resolve_section 后的整段 dict（内含 vs_src_dir）
optional_inputs  ← _resolve_section(data.get('optional_inputs'))
intermediates    ← _resolve_section(data.get('intermediates'))
outputs          ← _resolve_section(data.get('outputs'))
derived          ← 派生+覆盖后的 dict
_root            ← root（= config_path 所在目录）
_config          ← config_path 的 abspath
```

### `config_from_argv(argv)`（L85–91）
- `'--config' in argv` → 取 `argv[index+1]`，否则返回 `None`。

### 从 project_config.json 读取的配置字段全名清单
- **标量**：`project`、`project_dir`
- **段（section，key 任意，按需读取）**：`inputs`（其中特例 key `vs_src_dir` 用于派生）、`optional_inputs`、`intermediates`、`outputs`、`derived`（覆盖段）
- docstring（L10–15）给出的**约定 key 示例**：`inputs['cbit']`、`derived['test_cpp']`、`intermediates['sch_connect_map']`、`outputs['meta']`

### 内部字段
- 仅 `_root` 与 `_config`（小写，均为返回 dict 的一部分）；无类，纯模块函数。

### 哈希 / 校验逻辑
- **完全没有**。全文无 hash / sha / md5 / checksum / 内容比对。唯一的校验是 L53 `os.path.exists(config_path)`（只查配置文件本身存在）。
- 这是你要并入「SHA-256 输入哈希冻结」的**净区**：可在 `load()` 返回 dict 时附加 `_hash` / `_inputs_digest`，或在 `load()` 内对 `data`（或各 section）做一次哈希并作为新 key 返回。

---

## 2. `D:\Newtest\CLAUDE_PROCESS\.claude\agents\check-agent.md`（248 行）

### 元信息（front-matter L1–6）
- `name: check-agent`；`description: 代码检查 — 质量门禁，60+ 项逐条检查，输出结构化 PASS/FAIL/WARN 报告`；`model: sonnet`；`tools: Read, Grep, Glob`。

### 输入表（L11–20，5 个输入）
`组装后的完整函数代码`（必）、`Pin Pair 约束条件`（必）、`DFT.csv 目标行`（选）、`资源分配表.csv`（选）、`TestItemMeta` JSON（选）、`PowerState` JSON（选）、`NU1201.treg`（Trim 时）。缺 DFT/资源表时切**轻量模式**（L22–28）。

### 检查项总数（实测，非 60+）
| 组 | 编号区间 | 主 ID 数 | 行号 |
|---|---|---|---|
| P | P001–P006 | 6 | L44–53 |
| E | E001–E027 | 27 | L55–100（E018 另有专项 L78–90） |
| T | T001–T005 | 5 | L102–110 |
| R | R001–R035 | 35 | L112–150 |
| V | V001–V007（含 V003a/b/c 子行） | 7 主 / 10 行 | L152–178 |
| M | M001–M004 | 4 | L180–189 |
| H | H001–H008 | 8 | L191–202 |
| **合计** | | **主 ID 92**（含子行 95） | |

front-matter 声称 "60+ 项" 是**过期数字**，实际已到 92 个主 ID。

### P 组（6 项，L46–53）
- P001 DFT至上（条件满足DFT不自行创造）
- P002 继电器名来自资源分配表
- P003 testType 与代码模式匹配
- P004 不确定参数未猜测已标⚠️
- P005 混合信号处理正确
- P006 反短接铁律（源表→目标PIN通路不得经过/连接其他DUT PIN）

### E 组（27 项，L59–100）
E001 Trim参数完整性 / E002 Trim不用MeasureVI / E003 VAC Share继电器映射 / E004 AFX注释成对 / E005 AWG两段式3参数（强制跑 `verify_awg_params.py`）/ E006 源表名真实性 / E007 浮动源台阶上电200us / E008 BUS继电器冲突 / E009 FPVI等电位 / E010 上电顺序PinA领先 / E011 BUS路径BST-PMID不短接 / E012 FPVI未设FV=0 / E013 台阶不完整ΔV≤5V+200us / E014 电压计算PinA=PinB+deltaV / E015 PMID电压严格按DFT / E016 压差超限≤5V / E017 台阶等待Set后跟delay / E018 FET耦合反偏（FAIL_CRITICAL 烧片，专项 L78–90）/ E019 BUS优先级 / E020 Cap继电器名来自资源表Cap2列 / E021 下电保持FET / E022 BUS意外短接 / E023 继电器热切 / E024 HS/LS禁止合并 / E025 LogData单位=spec预期 / E026 Ramp Hys单位（mV/mA *1e3）/ E027 电阻=实测V/实测I（禁理论值）。

### T 组（5 项，L106–110）
T001 EFUSE寄存器正确 / T002 封装数量=EFUSE寄存器数 / T003 sim_step存在 / T004 全flag处理 / T005 寄存器分开放置。

### R 组（35 项，L116–150）—— 一句话含义
- **结构类**：R001 参数数组命名小写 / R002 cbite.SetOn逗号分隔-1结尾 / R003 SetOn后delay_ms(3) / R004 无继电器=SetOn(-1)（强制跑 `verify_relay_trace.py`）/ R005 Cap2默认闭+按PIN例外 / R006 Toggle强制K43+K58 / R007 AMUX/NTC隔离K40/K41 / R008 Connect Relay逐个核查
- **量程/模式类**：R009 量程≥2× / R010 FV/FI模式映射 / R011 FPVI大电流初始化顺序 / R012 ≥1A用FPVI / R013 未用源表不出现 / R014 MI→MIRET MV→MVRET / R015 Toggle mon_src=SDA_INT_ACM / R016 测量资源来自resourcesInvolved / R017 Toggle ramp 13参数 / R018 电阻单位>100mA→mΩ / R019 大电流关断 / R020 AMUX-NTC FI=0+10UA+差分
- **下电类**：R021 下电序列反转 / R022 浮动源台阶下电 / R023 RELAY_OFF统一10V/10MA / R024 FPVI最后断开 / R025 所有源下电 / R026 大电流下电顺序
- **注释/签名类**：R027 函数签名DUT_API int TMxxx / R028 DFT注释在开头 / R029 继电器注释 / R030 浮动源电压标注 / R031 台阶标注 / R032 大电流路径注释 / R033 Software_initial完整性
- **特殊**：R034 entertestmode 先于I2CWriteSameData / R035 LogData FOR_EACH_VALID_SITE+SetTestResult

### V 组（L152–178，轻量强制）
V001 Pin Pair约束提取 / V002 电压序列追踪 / V003 过渡态压差+极性（x>2.9V须A≥B）+ V003a 极性 / V003b 浮空Pin=0V / V003c Ramp领导权 / V004 台阶完整性 / V005 台阶延迟 / V006 FET导通时刻 / V007 下电过渡态。

### M 组（L180–189）
M001 零合并铁律违反（merge_log.md 有任意合并行→FAIL）/ M002 合并缺日志 / M003 规则引用错误 / M004 合并残留。由 `verify_merge_rules.py` 强制执行。

### H 组（8 项，L195–202）
H001 AWG必须rampv_capv/rampi_capv / H002 Trim measure在sub.cpp / H003 CSpec不在test.cpp / H004 程序单位V/A / H005 Toggle mon_src≠NTC_FOVI/AMUX_FOVI / H006 同Function Name内参数可合并 / H007 单Pin vset不需FPVI_BUS / H008 缺vset[AxB] BST=SW, VDRV=LG。

### 如何新增一个检查项
文件本身是 **agent 规格 prompt（非可执行代码）**，新增方式为：
1. 选组，在对应表格加一行，ID 续该组编号（如 R036 / H009）。
2. 定义「判定」列（检查方法/触发条件）。
3. 若 DFT 依赖或模式相关，同步更新：输入表（L11–20）、轻量模式清单（L24–28）、工作流 Step 5 模式选择（L224–228）。
4. 若需脚本强制，加 `verify_*.py` 引用（如 E005→`verify_awg_params.py`，R004→`verify_relay_trace.py`，M→`verify_merge_rules.py`）。
5. 输出 JSON 的 `checks[].id` 随之出现。

### 是否已有"材料/黄金代码/参考案例是否被读取"类检查
**没有。** 现体系只有：
- 输入表声明「必需/可选」输入（L11–20）；
- 检查项**引用**外部文件做比对（P002/E005/E006/E020 引用资源表、E001/T 组引用 treg），但**没有任何一项验证"材料文件是否真的被读取/加载/存在"**。
- 铁律「所有资源名以参考文件为准」（L245）是判定准则，不是存在性门禁。
→ 你的「材料门硬门禁」在此是**空白区**，可新增独立检查（如 `M005`/`H009` 或独立脚本）。

### 门禁 / 证据机制（已有的）
- 输出 JSON 结构 `{verdict, summary, checks[]}`（L32–40）。
- 汇总规则 Step 7（L230）：任一 FAIL→FAIL；仅 WARN→WARN；全 PASS→PASS。
- 判定标准 PASS/FAIL/WARN/SKIP（L234–238）。
- 铁律区（L240–247）：FAIL 必须引用规则编号；V 组/反短接 → FAIL_CRITICAL。
- M 组以 `merge_log.md` 为**证据文件**（M001–M004）。
- **注意**：现有门禁全部 keyed 到**代码内容正确性**，不 keyed 到「材料是否被读取」。你的硬门禁需要新增独立判定维度。

---

## 3. `D:\Newtest\CLAUDE_PROCESS\.claude\AGENT_MAP.md`（97 行）

版本日期 `2026-08-09`；目录 `.claude/agents/*.md` 共 19 个文件（2026-08-10 删 2 个 A0 旧遗留，L5）。

### 一、代码生成 Pipeline（L9–58）

| # | Agent | 触发 | 依赖 | 产出 | 状态 |
|---|---|---|---|---|---|
| 0 | 入口分流（非 agent） | 每次进入 | 有资源分配表? | 路径判定 A/B | — |
| 1 | dual-parse-agent --A | 流程A准备 | DFT.csv+资源分配表 | 完整 TestItemMeta | 活跃 |
| 1' | dual-parse-agent --B | 流程B准备 | DFT 段 | 部分 TestItemMeta | 活跃 |
| 1b | sch-parse（Skill） | 流程B前置 | SCH-DALI.NET | COMPONENT-STATISTIC + SCH-Connect-Map | 活跃 |
| 2 | **cbit-agent**（公共前置） | 每次进入主Skill | CBIT表/Netlist/定义文件 | 有定义→check / 无→A仅P1+P4 / B四阶段 | **部分脚本化**：P1/P2/P4 脚本化，P3 命名仍 agent（path-namer 复核） |
| 3 | **relay-agent** | 共用循环内 | TestItemMeta + (A资源表/B SCH-Connect-Map) | cbite.SetOn() + 闭环验证 (Step0~12) | **活跃执行，未脚本化** |
| 4 | ~~power-on-agent~~ → **gen_power_sequence.py** | 共用循环内 | --meta+--pin-map+--define | Step2 上电代码 + PowerState JSON | **已脚本化 2026-08-09** |
| 5 | （模板） | — | Software_initial + entertestmode铁律 | 寄存器配置代码 | 模板 |
| 6 | **measure-agent** | 共用循环内 | params[].check + testType | MI/MV/Toggle/Trim/AMUX-NTC 测量代码 | **活跃执行，未脚本化** |
| 7 | ~~power-off-agent~~ → **gen_power_sequence.py** | 共用循环内 | --meta+--pin-map | Step5 下电代码 | **已脚本化 2026-08-09** |
| 8 | （模板） | — | params | LogData SetTestResult | 模板 |
| 9 | check-agent + cbit-check | 收尾双查 | 完整代码+TestItemMeta+PowerState+定义文件 | PASS/FAIL/WARN 报告 | 活跃 |

**架构原则（L40）**：「推理→agent，固定→脚本」。已脚本化清单（L40–50）：
- `gen_power_sequence.py`（上电/下电）
- `gen_cbit_defines.py`（P1 单点生成 + P4 V1~V8 校验）
- `gen_paths.py`（P2 通路追踪 BFS）
- `gen_path_defines.py`（P3 通路 #define，352 定义追加 StdAfx.h；命名歧义组仍交 path-namer 复核）

### 特别标注：relay-agent 与 measure-agent
- **relay-agent（L32）**：**仍活跃执行**，未脚本化。产出 `cbite.SetOn() + 闭环验证 (Step0~12)`。它在 cbit 公共前置（通路 #define 已脚本化）之后消费 `TestItemMeta + (A资源表 / B SCH-Connect-Map)`。
- **measure-agent（L35）**：**仍活跃执行**，未脚本化。依赖 `params[].check + testType`，产出各类测量代码。文档无任何「脚本化」标注。
- 两者是当前 pipeline 中**尚未脚本化的核心推理 agent**（与 power-on/off、cbit 各阶段已脚本化形成对比）。

### 二、独立工作流 Agent（L61–73，用户触发，当前不执行）
| Agent | 触发 | 依赖 | 产出 | 状态 |
|---|---|---|---|---|
| sch-parse（Skill） | "原理图"/"sch-parse" | SCH-DALI.NET | COMPONENT-STATISTIC + SCH-Connect-Map | 活跃（被主Skill调用） |
| compile-agent | "编译"/"debug" | 工程路径+compile.ps1 | 打开工程→写码→code check→编译→Debug | 用户触发，当前不执行 |
| deploy-agent | "deploy"/"打开STS8300" | auto_sts8300.py | 打开STS8300软件+VS | 用户触发，前置 |
| testplan-agent | "写测试方案"/"翻译" | test.cpp/sub.cpp+SCH-Connect-Map+COMPONENT-STATISTIC | Word 测试方案 | 用户触发，当前不执行 |

### 三、自进化三 Agent（L77–87）
| Agent | 触发命令 | 维护对象 |
|---|---|---|
| rules-agent | `/evolve rules` | rules-registry.md |
| experience-agent | `/evolve exp` | knowledge/experience/ |
| sub-function-agent | `/evolve fn` | 库函数/shared_functions/ |

### 四、废弃 Agent（L91–97）
- A0-原理图Agent.md（✅ 已删除 2026-08-10，内容迁移至 sch-parse + relay-agent）
- A0-知识库.md（✅ 已删除 2026-08-10，内容迁移至 relays.md + naming.md + sources/* + schematic-parsing.md）

---

## 对接缝设计有用的关键结论

1. **proj_config.py 是纯读取器、零哈希** —— 哈希冻结的最佳并入点是 `load()` 返回 dict（L72–82），加一个 `_input_hash` / `_manifest` key；或在 `_read()`（L27–35）拿到原始 bytes 时直接做 SHA-256（此时是 DLP 解码前的原始字节，哈希最稳定）。`config_from_argv`（L85–91）是 CLI 覆盖入口，哈希冻结的 `--config` 切换天然兼容。
2. **check-agent.md 无「材料被读取」检查、无材料存在性门禁** —— 需要新增独立检查项/脚本；现成可挂靠的证据机制是 JSON 报告的 `verdict` + `checks[]`，以及铁律区的 FAIL_CRITICAL 语义。
3. **relay-agent 与 measure-agent 均为活跃执行 agent** —— 若「材料门硬门禁」要拦在生成前，接缝应在主 Skill 生成循环（AGENT_MAP.md L18–23 的共用生成循环）之前，即 cbit 公共前置之后、relay-agent（#3）之前，而不是挂在 check-agent（收尾）上——除非你设计的门禁是「生成后材料未读则报告 FAIL」。

（说明：本报告为纯只读检索结论，未创建或修改任何文件。）
