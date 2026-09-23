# Agent 全景地图 (2026-08-09)

> **单一入口见根目录 `工作流全景.md`**（流程地图 + 文件所有权 + 更新协议）；本文件为 Agent 细节速查。
> 所有 Agent + 关系 + 触发条件速查。更新: 每新增/废弃 Agent 同步此表。
> 目录: `.claude/agents/*.md` (共 19 个文件; 2026-08-10 删除 2 个 A0 旧遗留, 内容已迁移)
> **规则正文（2026-08-30 起）**: 一律在 `knowledge/standards/`（索引见 `skills/nuvolta-codegen.md` §4）；本文件与 nuvolta-codegen.md 都只放指针。

---

## 一、代码生成 Pipeline（主 Skill 编排, CBIT-Definition）

用户: "写 TMxxx" / "生成代码" → `nuvolta-codegen` Skill

```
入口: 解析用户指令 → 本批 TM 清单
        ▼
  sch-parse → Pin_Channel_define → dft-parse (仅 DFT, 源表映射留给 relay)
        ▼
  CBIT-Definition: 有继电器定义文件? 否→四阶段串行创建 / 是→仅check不更新
        ▼
  共用生成循环 (每个测试项): 框架 → relay → power-on → [寄存器] → measure → power-off → [LogData]
        ▼
  收尾双查: check-agent + cbit-check (FAIL→修复→重查→PASS)
```

| 序号 | Agent | 触发 | 依赖 | 产出 |
|:---:|-------|------|------|------|
| 1 | dft-parse-agent | DFT 解析 | DFT 段 (仅DFT) | TestItemMeta (无源表映射, relay 补) |
| 1b | *(sch-parse Skill)* | 前置 | SCH-DALI.NET | Component-Statistic + SCH-Connect-Map |
| 2 | **cbit-agent (CBIT-Definition)** | 每次进入主Skill | CBIT表/Netlist/定义文件 | 有定义→check / 无→完整四阶段含通路 (P1/P2/P4脚本化, P3命名仍agent) |
| 3 | relay-agent | 共用循环内 | TestItemMeta + SCH-Connect-Map | cbite.SetOn() + 闭环验证 (Step0~12) |
| 4 | ~~power-on-agent~~ → **gen_power_sequence.py** | 共用循环内 | --meta + --pin-map + --define | **Step2 上电代码 + PowerState JSON**（脚本化 2026-08-09） |
| 5 | *(模板)* | — | Software_initial + entertestmode铁律 | 寄存器配置代码 |
| 6 | measure-agent | 共用循环内 | params[].check + testType | MI/MV/Toggle/Trim/AMUX-NTC 测量代码 |
| 7 | ~~power-off-agent~~ → **gen_power_sequence.py** | 共用循环内 | --meta + --pin-map（PowerState 内部复用） | **Step5 下电代码**（脚本化 2026-08-09） |
| 8 | *(模板)* | — | params | LogData SetTestResult |
| 9 | check-agent + cbit-check | 收尾双查 | 完整代码 + TestItemMeta + PowerState + 定义文件 | PASS/FAIL/WARN 报告 |

> **脚本化 (2026-08-09)**：上电/下电为固定模板，power-on-agent / power-off-agent 已脚本化为 `gen_power_sequence.py`（架构原则: 推理→agent, 固定→脚本）。两 agent 文档保留为**规格文档**（R-PON/R-POFF 规则清单）。主 Skill 每次调脚本后跑 `--audit-rules` 确认规则覆盖未丢。

### CBIT-Definition — 创建继电器定义 (仅无定义文件时)

**完整四阶段（有 SCH-Connect-Map）**: 可含通路继电器

> **脚本化 (2026-08-09)**: P1 单点生成 + P4 校验 (V1~V8) 已脚本化为 **`gen_cbit_defines.py`**；P2 通路查找已脚本化为 **`gen_paths.py`**（架构原则: 推理→agent, 固定→脚本）。
> cbit-parse/singlepoint/check/path-finder 四 agent 保留为**规格文档**（规则溯源），不再执行。P3 通路命名（path-namer）**已脚本化 (2026-08-10)** 为 **`gen_path_defines.py`**（cbit-path-namer 规则实现为代码），命名歧义组（同源同 pin 多通路 → _A/_B/_C）仍交 path-namer agent 复核。
> **边界 (用户确认)**: SCH-Connect-Map.txt 完整生成（10 列/多源/最短路径+F/S 同时连通）归 **sch-parse agent（任务六）**，不脚本化；`gen_paths.py` 是通路追踪工具（BFS→path_list，覆盖 FPVIe/ACM200/FOVIe），SCH-Connect-Map 缺失时兜底，不宣称生成 SCH-Connect-Map。
> **通路定义脚本化 (2026-08-10)**: 通路继电器 #define 由 **`gen_path_defines.py`** 从 SCH-Connect-Map `需闭合:` 全量 SetOn 生成（352 定义），追加到编译头 **StdAfx.h**（include guard 内、DLP 字节模式先编码后写）；`--verify`(SCH-Connect-Map 一致性) /  / `--audit-rules`(P-DEF 12 规则自检) 机器自检。

| 阶段 | 执行方式 | 数据来源 | 产出 |
|:---:|---------|---------|------|
| P1 | **gen_cbit_defines.py --cbit [--stat]** | CBIT表 + Component-Statistic | 单点继电器 #define + V1~V8 |
| P2 | **gen_paths.py --netlist --cbit [--json]** 优先读 SCH-Connect-Map | SCH-Connect-Map (sch-parse产出) 优先 / netlist | DUT_PIN→稀缺源表通路 path_list |
| P3 | **gen_path_defines.py** (命名歧义组→cbit-path-namer 复核) | SCH-Connect-Map `需闭合:` + StdAfx.h 单点物理名 | 通路继电器 #define (2.x 通路段追加 StdAfx.h) |
| P4 | **gen_cbit_defines.py --cbit --verify [--stat] [--map]** | StdAfx.h + CBIT表 | V1~V8 校验报告 |

---

## 二、独立工作流 Agent (旁路 pipeline, 用户触发, 当前不执行)

> **共用原则 (2026-08-09 用户澄清)**: 以下三个 agent 都**由用户触发**、当前不执行。compile/deploy/testplan 不进 codegen pipeline。

| Agent | 触发条件 (用户说什么) | 依赖 | 产出 |
|-------|----------------------|------|------|
| sch-parse (Skill) | "原理图"/"sch-parse" | SCH-DALI.NET | Component-Statistic + SCH-Connect-Map |
| compile-agent | "编译"/"debug" (用户触发) | 工程路径 + 修改指令/codegen代码 + compile.ps1 | **打开工程→写码→code check→编译→Debug** 闭环 |
| deploy-agent | "deploy"/"打开STS8300" (用户触发) | auto_sts8300.py | **自动打开STS8300软件+VS** (前置; 后续编译/Debug复用compile-agent) |
| testplan-agent | "写测试方案"/"翻译" (用户触发) | test.cpp/sub.cpp + SCH-Connect-Map + Component-Statistic | 测试方案 **Word 文档** (人类可读语言) |

> cbit-agent 及四个子阶段已移至 **§一 CBIT-Definition**（不再独立工作流）。sch-parse 作为前置 Skill 被主 Skill 调用。单独触发 cbit-check 仍可用 "CBIT"/"继电器定义"。
> deploy-agent 不是废弃: 是 compile-agent 的**开软件前置**（解决用户手动开 STS8300/VS）, 后续内容与 compile 一致。

---

## 三、自进化三 Agent (2026-08-09 新增, 独立启用, 共享 daylog)

> 详情见 `knowledge/standards/rules-registry.md` + `knowledge/experience/` + `D:\Newtest\CLAUDE_PROCESS\Library-Functions\shared_functions\`

| Agent | 触发命令 | 维护对象 | 发布流程 |
|-------|---------|---------|---------|
| rules-agent | `/evolve rules` / "提炼规则" | rules-registry.md (规则生命周期) | draft→人工确认→active→同步verify |
| experience-agent | `/evolve exp` / "提炼经验" | knowledge/experience/ (项目经验) | draft→人工确认→active |
| sub-function-agent | `/evolve fn` / "提炼子函数" | D:\Newtest\CLAUDE_PROCESS\Library-Functions\shared_functions\ (跨项目子函数) | draft→人工确认→发布src/ |

数据源: `daylog/` 每日档案 (主 Skill 收尾必写一条, 六类标记)

---

## 四、废弃 Agent (待清理)

| Agent | 状态 | 取代者 |
|-------|------|--------|
| A0-原理图Agent.md | ✅ 已删除（2026-08-10 内容迁移完毕） | sch-parse + relay-agent (Step13 路径穷举法) |
| A0-知识库.md | ✅ 已删除（2026-08-10 内容迁移完毕） | relays.md + naming.md + sources/* + schematic-parsing.md |
