# 会话 #41 — 在工作区 `D:\\Newtest\\CLAUDE_PROCESS` 下盘点 skill 文件与 codegen pipeline 结构，用于写一份"ATE Off

- 文件：`agent-a16ad084268ba0dc5.jsonl`（项目 subagents）
- 时间：2026-08-26T13:15:38.408Z → 2026-08-26T13:16:56.818Z，大小 0.3 MB
- 用户消息 1 条 / 助手文本 4 段 / 工具调用标记 12 行

---

## 对话正文（工具输出已剥离）

### 2026-08-26 13:15:38 [user]

在工作区 `D:\Newtest\CLAUDE_PROCESS` 下盘点 skill 文件与 codegen pipeline 结构，用于写一份"ATE Offline Coding 工作流架构"文档。

请做：
1. 读 `.claude\skills\nuvolta-codegen.md`（这是核心 codegen skill，可能很长，可分段读）。提取：
   - 主 pipeline 的完整阶段结构（Step0~Step10 或类似），每阶段做什么、调用哪个 agent / 脚本 / 模板。
   - **所有关于"执行频率与循环关系"的表述**：例如逐 TM 循环、批量生成循环、单函数冒烟 FAIL 停留当前 TM、收尾双查、meta 门禁、上下文铁律、读文件纪律等。逐字摘录关键句子（这些是"循环/频率"章节的事实来源）。
   - 它引用/调用了哪些脚本、哪些 agent、哪些 knowledge 文档。
2. 读 `.claude\skills\sch-parse.md` 和 `schematic_parse\SKILL.md`，提取原理图解析 pipeline 的阶段（如 CSV adapter → sch_parse → pathproof → verify → 发布），每阶段输入输出与脚本。
3. 读 `.claude\knowledge\panorama.md`（B 路径 14 步全景），提取 14 步名称与每步的落点（脚本/文档）。
4. 搜索工作区内是否还有其他 skill 文件（如 `schematic_parse\` 或 `.claude\skills\` 下的 .md），一并概括。

输出为结构化清单，中文回答。**特别注意：任何描述循环、迭代、冒烟、门禁、批量、停留、重跑的句子都要原样摘录**，我要据此写"执行频率与循环关系"章节。
- [tool] Bash
- [tool] Glob

### 2026-08-26 13:15:43 [assistant]

Now let me read the core skill files in parallel.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:15:46 [assistant]

Let me check for any other skill files and examine the schematic_parse structure further.
- [tool] Glob
- [tool] Glob
- [tool] Bash

### 2026-08-26 13:15:53 [assistant]

Let me read the remaining pipeline-defining files to round out the sch-parse stages.
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:56 [assistant]

我已读完全部核心文件并盘点完 skill 文件。以下为结构化清单。

---

# ATE Offline Coding 工作流架构 — 盘点清单

## 一、Skill 文件盘点（全工作区仅 3 处）

| 文件 | 类型 | 职责 |
|---|---|---|
| `D:\Newtest\CLAUDE_PROCESS\.claude\skills\nuvolta-codegen.md` | 核心 codegen Skill（42.6KB） | 双路径 codegen 主流程，生成 test.cpp/sub.cpp |
| `D:\Newtest\CLAUDE_PROCESS\.claude\skills\sch-parse.md` | 薄指针 Skill（2KB） | 原理图 Netlist 解析，指向 `schematic_parse/` |
| `D:\Newtest\CLAUDE_PROCESS\schematic_parse\SKILL.md` | 解析流水线正文（4.4KB） | CSV 唯一生产管线，四/五脚本流水线 |

搜索确认：`**/SKILL.md` 全工作区仅匹配 `schematic_parse/SKILL.md` 一处；`**/skills/**/*.md` 仅 `.claude/skills/` 下两个文件。**无其他 skill 文件**。相关支撑材料分布在 `.claude/agents/`（18 个 agent 规格文档）、`.claude/knowledge/`（sources/standards/experience/hardware）、`schematic_parse/`（规则与脚本）、`.claude/references/`（chip/method/code/debug 黄金材料 + 索引）。

---

## 二、`nuvolta-codegen.md` 主 pipeline 阶段结构

### Step 0 — 入口分流
判断有无 `资源分配表.csv`：有 → **流程 A**；无（仅 .net 文件）→ **流程 B**。

### Step 1A — 流程 A 准备（`dual-parse-agent --A`）
输入 DFT 行 + 资源分配表.csv + FET 配置 → 输出 **TestItemMeta JSON 完整版**（functionName, testType, params, hardwareInit, softwareInit, pinsInvolved, resourcesInvolved, floatingPairs, voltageInference）。A 路径不需要 sch-parse。

### Step 1B — 流程 B 准备（sch-parse → Pin_Channel_define → dual-parse --B）
1. `[Skill] sch-parse`：SCH-DALI.NET → COMPONENT-STATISTIC + SCH-Connect-Map
2. `[文件] Pin_Channel_define.h` → 源表名映射（多工位共享源表名，FOVIe=FXVIe_PLUS）
3. `[Agent] dual-parse-agent (--B)`：仅 DFT parse → **TestItemMeta JSON 部分版**（resourcesInvolved 为空 → 源表映射由 relay-agent 从 SCH-Connect-Map 补齐）

### Step 2 — cbit 公共前置（每次进入必走）
判断有无继电器定义文件（relay.h / #define）：
- **无** → 创建：A 路径仅 P1 单点+P4 check（无 SCH-Connect-Map）；B 路径完整四阶段（singlepoint → path-finder → path-namer → check，含通路）
  - P1（A+B）：`gen_cbit_defines.py --cbit ... --stat ...` → 单点 #define + V1~V8（OVERALL PASS 才可用）
  - P2（仅B）：优先参考 SCH-Connect-Map；缺失时 `gen_paths.py --netlist ... --cbit ... --json` → 通路文档 + PATH_LIST JSON
  - P3（仅B）：`gen_path_defines.py` → 通路 #define 追加 StdAfx.h 2.x 段（DLP 字节模式）；命名歧义组交 cbit-path-namer 复核
  - P4（A+B）：`gen_cbit_defines.py --verify`（B 路径加 `--map` 跑 V2/V7）
- **有** → 仅 check（P4 脚本 --verify）验证，不更新

> 脚本化原则：**推理→agent，固定→脚本**。cbit-parse/singlepoint/check/path-finder/path-namer 五 agent 已降为规格文档；power-on/power-off 已脚本化。

### Step 3 — 共用生成循环（按 testType 选框架模板）
三类模板：**普通测试**（6 段注释：Step1 Connect/Step2 上电/Step3 寄存器/Step4 测量/Step5 下电/Step6 LogData）、**Toggle 测试**（Rise/Fall/Hys 3 参数）、**Trim 测试**（9 固定后缀 + step0~N，走 sub.cpp）。

### Step 4 — 共用生成循环（每测试项顺序调用）
```
0. 材料门（生成前拦截）→ verify_material_receipt.py，FAIL 禁止进入 relay-agent
1. relay-agent → 继电器闭合代码（A: 查资源分配表 / B: 查 SCH-Connect-Map）
2. 生成 pin-map JSON（A/B 同 schema，脚本不做 pin→源表查找，映射由调用方生成）
3. gen_power_sequence.py → 一次调用输出三段 SECTION（POWER_ON / POWER_STATE / POWER_OFF）
4. 模板填充 → entertestmode(); + DFT Software_initial 原样复制
5. measure-agent → 测量代码
6. 模板填充 → LogData
7. 单函数冒烟 → verify_single_fn.py（FAIL 停留当前 TM，PASS 才进下一个）
8. 最后一个测试项? 否 → 循环 / 是 → Step 5
```

### Step 5 — 收尾双查
`check-agent`（60+ 项 P/E/R/H）+ `gen_cbit_defines.py --verify` + `verify_awg_params.py --src test.cpp`（Toggle 3 参数门禁 E005，必跑）+ **meta 全覆盖门** `check_testitems_meta.py --require-all --require-scope <本批范围>`。有 FAIL → 修复 → 重新检查 → 直到 PASS。

---

## 三、【重点】执行频率与循环关系 — 逐字摘录

以下句子全部原样摘录自 `nuvolta-codegen.md`，供撰写"循环/频率"章节作事实来源。

### 1. 逐 TM 生成循环 / 批量生成循环
- （架构图 line 41-42）`├── [脚本] verify_single_fn.py → 单函数冒烟（--fn <当前TM>, FAIL 停留当前 TM）` / `└── 最后一个测试项? 否→循环`
- （Step 4 循环，line 269）`对每个测试项执行（A/B 共用同一条流水线，差异只在 relay-agent 查表来源与 pin-map 生成）:`
- （line 281）`8. 最后一个测试项? 否 → 回到本循环下一个 / 是 → Step 5`
- （批量生成 line 344）`4. 循环: 每个独立 Function (MR-000 零合并) → Step 3~4 共用生成循环`

### 2. 单函数冒烟（FAIL 停留当前 TM）
- （line 280）`**单函数冒烟（B-001 脚本强制, 2026-08-23）** → 组装完当前 TM 函数后立即 python verify_single_fn.py --src <test.cpp> --fn <当前TM>（7 项: 占位符/分号/花括号/CRLF/模板残留/lifecycle 六阶段行为证据/寄存器解锁顺序）→ **FAIL 停留当前 TM 修正, 不得进下一个 TM**; PASS 才进下一个`

### 3. 收尾双查 / 重跑
- （line 50）`FAIL → 修复 → 重新检查 → PASS ✓`
- （line 322）`输出结构化检查报告。有 FAIL → 修复 → 重新检查 → 直到 PASS。`

### 4. meta 全覆盖门（每批收尾必做）
- （line 324）`**⚠️ meta 全覆盖门（每批测试项目收尾必做，2026-08-10 用户要求，机械强制不靠自觉）**`
- （line 325）`**每个测试项目必须有 meta 文件** —— 运行 check_testitems_meta.py --require-all --require-scope <本批范围>，**双向强制**`
- （line 326，正向）`test.cpp 每函数必须有 OVERVIEW 记录，无记录 → ERROR 退出（**禁止静默跳过**），需先补 Dali_testmode.xlsx /OVERVIEW 该行；覆盖率 = test.cpp 函数数，<100% → FAIL`
- （line 327，反向）`本批范围内 OVERVIEW isCodeGen='Y' 的每项必须已在 test.cpp 有 DUT_API 函数，缺任一项 → **FAIL 并列出具体 TM 编号+Name**（如 TM403-425 未写时列出全部 15 项）。**范围 = 用户指令的 TM 批次**，如 --require-scope 403-425`
- （line 329）`顺序：写完代码 → python check_testitems_meta.py --require-all --require-scope <本批范围> → 再 verify_relay_trace.py --meta <新meta> --warn-as-error`
- （line 330）`**铁律**：本批范围内 isCodeGen='Y' 项必须全部写入 test.cpp，漏项即 FAIL——禁止把 OVERVIEW 有记录但没写进 test.cpp 的项目静默留到下批（TM403-425 正是此漏点，2026-08-10 堵住）`
- （批量 line 346）`6. **meta 全覆盖门**: python check_testitems_meta.py --require-all --require-scope <本批范围> → 每个测试项目都有 meta (无 OVERVIEW 记录→ERROR) + 本批 isCodeGen=Y 项全写入 (缺项→FAIL) → 覆盖率 100% PASS`

### 5. 批量生成纪律 B-001
- （line 350）`1. **先单函数冒烟**: 模板/数据 dict 有 bug = 整批一起错。先插入 **1 个代表函数** → 编译 + check_testitems_meta.py --require-all + verify_relay_trace.py --meta --warn-as-error 全绿 → 再批量放量`
- （line 351）`2. **占位符按长度降序替换**: 模板占位符可能有前缀关系 (...) → sorted(mapping, key=len, reverse=True); 替换后**断言无残留 __X__**（有→FAIL, 不静默生成坏代码）`
- （line 352）`3. **生成后自检**: 分号在尾随注释前（* 1e3; // comment, 否则 C2143 missing ';'）、花括号配平、CRLF 字节干净 (DLP 源文件必须字节模式 open('wb'), 禁止文本模式 \r\r\n)`

### 6. 材料门（生成前拦截）
- （line 270）`0. **材料门（生成前拦截, 2026-08-23）** → 按 param_type_index.md 判定参数类型 → 加载 chip/ + method/ + **全部** code/ 黄金材料 → 写入 receipt（Project/DALI/material_receipts.json: {TM: {param_type, materials}}，路径相对 references 根）→ python verify_material_receipt.py --receipt <receipt> --tm <当前TM> → **FAIL 禁止进入 relay-agent**。材料存在却未读取不得生成; Current Threshold/ZCD 必须同时声明 code/HS_ZCD.cpp + code/LS_ZCD.cpp，只读其一 → FAIL（正是 TM607-609 根因）`

### 7. 脚本规则自检（audit-rules 重跑纪律）
- （line 217）`**脚本改动后必跑 python gen_cbit_defines.py --audit-rules + python gen_paths.py --audit-rules + python gen_path_defines.py --audit-rules**（13 + 11 + 13 规则覆盖自检）确认规则未丢。`
- （line 283）`> 上电/下电已脚本化（架构原则: 推理→agent, 固定→脚本）。... **每次脚本改动后必须跑 python gen_power_sequence.py --audit-rules**（19 规则覆盖自检）确认未丢规则。`

### 8. cbit 公共前置频率（每次进入必走）
- （line 190）`### Step 2: cbit 公共前置（每次进入必走）`
- （line 213）`└── 是 → 仅 check (P4 脚本 --verify) 验证定义正确，不更新（除非用户要求更新）`

### 9. 上下文铁律 / 读文件纪律（2026-08-26 用户拍板）
- （line 358）`> 目的: 单任务上下文从 ~400-600K token 降到 ~10-20K。**禁止把大文件全量塞进上下文**——大文件一旦被读进来就常驻上下文, 之后每轮推理都重新处理它, 任务越往后越慢的根源。`
- （line 360-361）`1. **test.cpp 禁止全读 (348KB/6.7K 行 ≈ 116K token/次)** — 只需定位插入锚点: Grep test.cpp 找最后一个函数签名/尾部结构 → Read 只开尾部 50~100 行窗口拿锚点 (~2-3K token), 不全文。新增 TM 一律**追加到文件尾** (不改中间, 避免全文读+全文写)。`
- （line 363-366）`2. **两段式写码 (写完→编译→归位→再编译)**: 阶段 1 (正确性): 新 TM 全部追加尾部 → fast_rebuild -Incremental 编译过 + 门禁过。阶段 2 (归位): 按 TM 编号顺序把每个 TM 函数块移动到规范位置。**最小移动单位 = 单个 TM 单元**（一个 TM 的完整函数体, 含其 AFX 注释块）, 不拆行/不半截移动。移动用脚本定位+字节模式替换 (DLP), 之后**再增量编译一次**确认。函数定义顺序不影响链接, 归位是纯工程性重排, 安全; 先正确后归位, 两段互相解耦。`
- （line 367-368）`3. **StdAfx.h 禁止全读 (51KB/603 行 ≈ 17K token/次)** — 继电器用检索确认: 写具体 TM 时只 Grep StdAfx.h 确认**需要的几个 Kxx_ 宏**存在 (每次几百 token), 不全文。通路→继电器名优先从 SCH-Connect-Map + gen_path_defines.py 产物拿, 不靠读头文件全量。`
- （line 370-372）`4. **golden 一律走索引, 禁止从 test.cpp 现翻参考**: 先经 param_type_index.md / func_type_index.md 判定参数类型 → 只读**匹配的独立 golden 文件** (references/code/*.cpp, 1.3~6.9KB ≈ 500~2300 token/个), 不打开 test.cpp 找旧函数当模板。索引未登记的参数 → 归类到现有类型 (阈值 AWG→UVLO/toggle-template; 电流阈值→HS_ZCD/LS_ZCD), 补索引行即可, 不新建大文件。`
- （line 373-374）`5. **黄金案例 = 关键特殊结构参考, 非继电器/PIN 字典 (2026-08-26 用户拍板)**: 用 golden 前先提取它的**关键特殊结构** (抓关键点推断, 不机械模仿)`
- （line 381）`**不知道提取什么作为关键信息 → 向用户提问**, 不要机械套用。详情见 memory [[nuvolta-golden-case-usage]]。`

### 10. Trim 判定（禁止静默降级，也是门禁性表述）
- （line 265）`... **执行中发现材料缺失或错误（treg 无对应段、measure 函数注释、寄存器字段矛盾）→ 向用户报告错误**（列出具体不匹配点），**禁止静默降级**为"暂测默认值/普通测试直接测量"。`

### 11. 自动同步规则（每次修正后必做）
- （line 521-524）`**每次修正代码或规则错误后，必须同步更新:** 1. 对应的 knowledge/ 文件（如果知识变了） 2. check-agent.md 检查清单（如果有新的错误模式） 3. 写 daylog/ 当日条目`

### 12. daylog 收尾步骤（每次工作结束）
- （line 494）`**每次 codegen/debug/规则修正后, 在主 Skill 收尾时追加一条到 daylog/<当天日期>.md**`
- （line 504-506）`- 即使只改了某 stage 结果、只对某报错提了修正意见, 也写一条 → 后续提炼时被识别` / `- **即使暂时不跑三个 agent, 也要写 daylog** — 档案是以后提炼的原料, 不依赖完整 pipeline`

---

## 四、sch-parse 原理图解析 pipeline

### 引用关系
`sch-parse.md`（薄指针）→ 权威正文在 `schematic_parse/SKILL.md` + `VALIDATION_RULES.md` + `NET_SHORT_RULES.md` + `KELVIN_RULES.md` + `OUTPUT_RULES.md` + `PATH_CONTRACT.md` + `RELAY_CONTROL_RULES.md` + `SOURCE_POLICY.yaml`；深知识在 `knowledge/hardware/schematic-parsing.md`。

### 入口与位置约定
- 脚本（通用、任何项目共用）：`schematic_parse/scripts/` — `csv_schematic_adapter_v2.py`、`csv_pathproof_v2.py`、`sch_parse.py`（六门控引擎，53.9KB）、`run_hardware_parse.py`（编排入口）
- 项目数据（每项目不同）：`Project/DALI/` — `Dali-SCH.csv`、`sch_confirmed.json`、`CSV_CONNECTIVITY.NET`、`SCH-Connect-Map.txt`、`COMPONENT-STATISTIC.txt`
- 入口命令：
  - `run_hardware_parse.py`（校验 + 生成，--no-write 不写 StdAfx.h）
  - `run_hardware_parse.py --publish-definitions`（校验 + 发布 StdAfx.h 2.x 段，先自动备份到 Backup/）

### 五脚本流水线（SKILL.md 表 + run_hardware_parse.py 实际调用序）

| 顺序 | 脚本 | 输入 → 输出 |
|---|---|---|
| 1 | `csv_schematic_adapter_v2.py` | CSV → 合成 EDIF `CSV_CONNECTIVITY.NET` → `sch_parse.py` 六门控 → `SCH-Connect-Map.txt` + `COMPONENT-STATISTIC.txt` + `validation_manifest.json.txt` |
| 2 | `csv_pathproof_v2.py` | CSV + CBIT → 原生 BFS PathProof → `path_proofs.json.txt` + `PATHPROOF-VALIDATION.txt` |
| 3 | `gen_path_defines.py --config project_config.json --map <SCH-Connect-Map.txt> [--no-write]` | 通路定义 2.x 段 → StdAfx.h |
| 4 | `gen_cbit_defines.py --config ... --stat <COMPONENT-STATISTIC.txt> --map <SCH-Connect-Map.txt>` | CBIT 单点 + V1–V8 校验 |
| 5 | `gen_relay_role_defines.py --map <SCH-Connect-Map.txt> [--no-write]` | 列11 角色继电器定义 → StdAfx.h RELAY_ROLE 段（稳压/P2P/短路/上拉/下拉） |

（SKILL.md 称"四脚本流水线"，因脚本 3/4/5 复用 workspace 根目录生成器，`schematic_parse/scripts/` 内自身四文件为 adapter/pathproof/sch_parse/run_hardware_parse。）

### 六门控（sch_parse.py 引擎，串行门控）
G1c（孤立 PORT）、G1d（TP 短接确认）、G2（功能分类）、G3（浮空引脚/物理规则）、G4（器件参数）、G5（net 完整性）。任一 FAIL → `PARSER_FAIL`（退出码非 0）。状态机：`PASS`（六门控 PASS，列11 通路分类 + Rule A/B 已应用，退出码 0）/ `PARSER_FAIL`。

### 上游校验（VALIDATION_RULES.md）
25 列契约（REQUIRED_COLUMNS，缺一报错）、DLP 密文容器拒收（`%TSD-Header-###%` / `TSZ#`）、compact 布局归一化、图构建规则（PIN/PORT 判定、`S3_FOVIe_*`→`S3_FXVIe_PLUS_*` 别名归一、NET_TIE_GROUP、infer_cell、TP 合成）、下游 CBIT 校验 V1~V8（V1 无重复/V2 通路完整性/V3 命名/V4 量程/V5 覆盖/V6 F-S 配对/V7 FPVI 命名/V8 继电器状态）。

### 深知识六任务（schematic-parsing.md）
任务一 解析 DUT PIN → 任务二 解析源表（含任务二b 读 Pin_Channel_define.h 源表名映射）→ 任务三 解析继电器（BUS/Share/Connect/Cap 三层动态分类）→ 任务四 元器件 → 任务五 net → 任务六 生成 SCH-Connect-Map.txt（11 列，含列11 通路分类六类：P2P-到地/P2P-互短/上拉-固定5V/上拉-源表/下拉/稳压/net短接）。
通路有效性规则：最短路径原则、双线铁律（F/S 务必同时连通）、F/S 状态一致性铁律、反短接铁律、Rule A 固定电压节点铁律。

### 门控/循环表述（逐字摘录）
- （sch-parse.md line 29）`1. 六任务门控串行，任一 FAIL 即停，禁止带病继续。`
- （schematic-parsing.md）`**门控铁律：** 六个任务严格串行，每个任务的检查 Step 全部判定正常后，才允许进入下一任务。任何一步报错 → 停止，向用户报告，不继续。`
- （任务一 Step6c）`→ 必须向用户反馈异常，原理图确认` / `→ 未确认前不得继续，禁止当成"不存在"静默跳过`
- （任务一 Step6a）`TP短接先问` → `必须向用户询问确认`
- 脚本 1/2 复用一个 `sch_parse.py`（六门控引擎）不重造；产物统一落 `Project/DALI/`。

---

## 五、`panorama.md` — B 路径 14 步全景

### 五大输入源
DFT（test-Condition，→ dual-parse-agent）、原理图（SCH-Connect-Map 通路，→ schematic-parsing.md + sch_parse.py）、ChannelMap（源表通道↔工位+继电器 CBIT，→ Pin_Channel_define.h + Hardware-Config.h，他人负责，定义完成则跳过）、机台手册（STS8300 API，→ knowledge/sources/）、工程师经验（→ standards/ + experience/ + 库函数/）。

### 路径选择
- **B 路径（默认）**：`sch-parse` → ChannelMap（Pin_Channel_define）→ `dual-parse--B`（仅 DFT）
- **A 路径**：仅用户提到「资源分配表」时执行 → `dual-parse--A`

### 一次性搭建（步骤 1-4）

| 步骤 | 内容 | 落点 |
|---|---|---|
| 1 | 原理图解析：Component-Map + 通路梳理（最短路径优先 + 第二短备用） | `schematic-parsing.md` + `sch_parse.py` |
| 2 | DFT 解析：test-Condition | `dual-parse-agent` + `gen_testitems_meta.py`（机械派生 meta） |
| 3 | 源表+继电器定义：与 DFT 独立、同等级、次序无关 | `cbit-mapping.md` + `gen_cbit_defines.py` + `gen_paths.py` + `gen_path_defines.py` |
| 4 | Treg 定义：Trim 库函数 | `standards/treg.md` + `库函数/treg/` |

### 逐项循环（步骤 5-14）

| 步骤 | 内容 | 落点 |
|---|---|---|
| 5 | 分类：两级（项目结构类型 7 类 → 具体参数类型） | `standards/test-types.md` + `references/code·chip·method/` |
| 6 | 框架创建：选模板（普通/Toggle-AWG/Trim） | `standards/framework.md` |
| 7 | 变量定义：CParam + 结果数组 + Trim 节点 | `standards/framework.md` + `naming.md` |
| 8 | 继电器闭合：闭环原则 + 工程应用 | `hardware/relays.md` + `experience/relay-check.md` |
| 9 | 上电：量程/不过冲/clamp/大电流 | `experience/power-sequence.md` §上电 + R-PON |
| 10 | 寄存器配置：registermap 读取 | `standards/register-config.md` |
| 11 | 测量：采样/间隔/切量程/恢复 | `experience/measurement.md` + `standards/units.md` |
| 12 | 下电：下电次序/量程统一 | `experience/power-sequence.md` §下电 + R-POFF |
| 13 | log：单位规则 | `standards/units.md`（R-LOG） |
| 14 | 检验：两层 | `standards/verification.md` |

### 两级分类模型（步骤 5 核心）
`DFT 项 → 项目结构类型(7类, 决定框架) → 具体参数类型(被测参数名, 决定参照) → references 四件套(同名联动): chip/<参数> + method/<参数> + code/<参数> + debug/<参数>(按需)`。判定顺序**命中即停**。

### 两层检验（步骤 14）
- 单项目冒烟自检：一个函数生成后秒级自检（5 项）→ `verify_single_fn.py` ✅ 已实现
- 跨项目统一门禁：`check_testitems_meta.py --require-all/--require-scope` + `verify_relay_trace.py --meta` + `verify_awg_params.py` + `gen_cbit_defines.py` + `gen_path_defines.py` + `fast_rebuild.ps1`
- 逐字摘录（line 71）：`流程：冒烟脚本 → 编译 → 跨项目门禁 → 批量放量（对应 B-001）。`

---

## 六、被引用/调用的脚本、Agent、知识文档汇总（nuvolta-codegen.md）

### 脚本（workspace 根）
`gen_cbit_defines.py`、`gen_paths.py`、`gen_path_defines.py`、`gen_power_sequence.py`、`gen_testitems_meta.py`、`check_testitems_meta.py`、`verify_material_receipt.py`、`verify_single_fn.py`、`verify_relay_trace.py`、`verify_awg_params.py`、`verify_merge_rules.py`、`gen_relay_role_defines.py`、`fast_rebuild.ps1`、`_archive/gen_insert_tm403_425.py`（批量插入参考）。

### Agent（`.claude/agents/`，18 个）
- 执行链：`dual-parse-agent`（A/B 双模式）、`relay-agent`（10 步清单→cbite.SetOn）、`measure-agent`、`check-agent`（60+ 项 P/E/R/H）、`cbit-agent`（公共前置）
- 已脚本化降为规格文档：`power-on-agent`、`power-off-agent`、`cbit-singlepoint-agent`、`cbit-path-finder`、`cbit-path-namer`、`cbit-parse-agent`、`cbit-check-agent`
- 自进化（独立工作流）：`rules-agent`（/evolve rules）、`experience-agent`（/evolve exp）、`sub-function-agent`（/evolve fn）
- 其他：`compile-agent`（编译+Debug，自修复≤10次）、`deploy-agent`、`testplan-agent`

### knowledge/ 引用
`sources/`（acm200/fovie/fpvie/hvie/qvme 量程）、`hardware/`（relays、schematic-parsing、closed-loop-model、test-strategy、pin-resource-map、bus-topology、cbit-principles、cbit-mapping）、`standards/`（naming、framework、units、treg、merge_rules、rules-registry、register-config、verification、test-types、functions-registry）、`experience/`（index、power-sequence、measurement、relay-check、project-notes）。

### references/ 黄金材料
`chip/`、`method/`、`code/`、`debug/`（四件套同名联动）+ `param_type_index.md`（10.2KB，材料门判定依据）+ `func_type_index.md`。案例模板：`references/tm600-normal-highcurrent.cpp`、`sub-measure-template.cpp`、`toggle-template.cpp`。

### 其他
`daylog/`（每日档案，六类标记）、`库函数/shared_functions/`（跨项目子函数库，registry/index.md）、`Project/DALI/`（Dali-SCH.csv、material_receipts.json、NU1201.treg）、`merge_log.md`。

---

## 七、关键架构原则（写作要点）

1. **架构原则**：推理→agent，固定→脚本。agent 规格文档保留规则溯源，实际执行脚本化。
2. **双路径**：A（有资源分配表）/ B（无，走 sch-parse），共用 Step 3~4 生成循环，差异仅在 relay-agent 查表来源与 pin-map 生成。
3. **循环频率模型**：逐 TM 循环（材料门 → relay → pin-map → 上电 → 寄存器 → measure → 下电 → LogData → 单函数冒烟），**单函数冒烟 FAIL 停留当前 TM 不前进**；收尾 meta 全覆盖门（双向强制）堵漏项洞；批量先 1 个代表函数冒烟再放量。
4. **上下文优化**：大文件（test.cpp/StdAfx.h）禁全读，追加写尾 + 两段式（先正确后归位）写码，golden 走索引按"角色"参考。
5. **门禁矩阵**：材料门（verify_material_receipt）、六门控（sch_parse）、单函数冒烟（verify_single_fn）、Toggle 3 参数门禁（verify_awg_params E005）、继电器轨迹核对（verify_relay_trace）、meta 全覆盖门（check_testitems_meta）、脚本规则自检（--audit-rules 13/11/13/19 条）、编译门禁（fast_rebuild）。
6. **自进化层**：三个独立 agent 以 daylog 为原料，每次工作收尾必须写 daylog，不依赖完整 pipeline。
