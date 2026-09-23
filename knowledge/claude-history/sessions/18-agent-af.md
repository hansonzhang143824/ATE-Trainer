# 会话 #18 — 你要对一个半导体测试代码生成项目做「现状知识盘点」，产出一份结构化报告。**严格只读：不要修改、创建、删除任何文件。** ## 项目背景 这是基于 STS830

- 文件：`agent-af0624697cb9267c0.jsonl`（项目 subagents）
- 时间：2026-08-15T15:08:28.129Z → 2026-08-15T15:12:47.505Z，大小 0.9 MB
- 用户消息 1 条 / 助手文本 11 段 / 工具调用标记 78 行

---

## 对话正文（工具输出已剥离）

### 2026-08-15 15:08:28 [user]

你要对一个半导体测试代码生成项目做「现状知识盘点」，产出一份结构化报告。**严格只读：不要修改、创建、删除任何文件。**

## 项目背景
这是基于 STS8300 测试机台的 offline coding 项目，知识（规则/经验/案例/函数）散落在多个位置，需要盘点"有哪些文件、各自存了什么、哪些内容重复/散落、应收敛到哪"。未来要收敛到三个注册表：`rules-registry.md`（规则）、`references/index.md`（参考材料）、`functions-registry.md`（函数）。

## 需要盘点的位置（全部只读扫描）
1. **项目知识库** `D:\Newtest\CLAUDE_PROCESS\.claude\`：`agents\`(约18个 .md)、`knowledge\`(sources\ hardware\ standards\ experience\ 四个子目录)、`skills\`、`references\`、`AGENT_MAP.md`
2. **项目根目录散件** `D:\Newtest\CLAUDE_PROCESS\` 下的 *.txt / *.md / *.py（重点：继电器识别规范.txt、源表规则.txt、原理图解析基本规则.txt、常用测试要求和硬件选型-实践.txt、规则文件DEEPSEEK.md、project_rules.md、paths_txt_生成规范_平台无关版.md、使用说明.md、启动.txt、以及所有 gen_*.py / verify_*.py / sch_parse.py / fast_rebuild.ps1 / compile.ps1）
3. **auto-memory** `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\`：MEMORY.md + 所有 nuvola-*.md + 所有 STS8300-*.md + 其他 *.md
4. **外部库**（只需列目录结构+一句话，不必深读每个函数）：`D:\test_method\`、`D:\shared_functions\`（如果存在）

## 脚本只需列名+一句话作用
gen_*.py / verify_*.py / sch_parse.py 等脚本不需要深读代码，只要从文件名/头部注释判断"它是干什么的、对应哪个环节、内置哪些规则"即可。

## 输出格式（结构化 markdown，重结论不重过程，别贴大段原文）
### A. 文件清单
按「位置」归类，每个文件一行：`文件名 — 一句话说明存什么`（memory 里的 nuvola-*.md 和 STS8300-*.md 要逐个列，因为它们是重复重灾区）

### B. 重复清单（最关键）
找出「同一规则/经验/知识出现在多个文件」的情况，重点看这六块：**cbite/继电器闭合、上电、下电、测量/量程、命名、单位换算**。每条格式：
`内容简述 → 出现在哪些文件（列路径）`。如果某块规则在 3 个以上位置重复出现，单独标 ⚠。

### C. 散件清单
项目根目录散落的 txt/md，哪些内容其实已迁移到 `.claude/knowledge\` 或应该归档删除（列出"根目录文件 → 内容 → 建议去向"）。

### D. 收敛对照表
对每个重复/散落的内容，给一行「应收敛到哪个文件」（三注册表之一，或 knowledge\ 下某文件）。

## 约束
- 只读，绝不写文件
- 报告控制在合理长度，用表格和短句，不要贴大段原文
- 直接返回报告文本作为你的最终输出（不要写文件）

### 2026-08-15 15:08:34 [assistant]

I'll start by scanning the directory structures in parallel.
- [tool] Glob
- [tool] Glob
- [tool] Glob
- [tool] Glob
- [tool] Glob

### 2026-08-15 15:08:45 [assistant]

I have the full file inventory. Now I'll read the content strategically, starting with the memory files (duplicate-prone) and knowledge files in parallel batches.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:09:00 [assistant]

Good progress. Now let me read the knowledge files (the convergence targets) and remaining memory rule files in parallel.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:09:12 [assistant]

Let me read the remaining memory rule files and key root scattered files.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:09:23 [assistant]

Let me read the remaining meta memory files and the key root scattered files.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:09:38 [assistant]

Now let me read the AGENT_MAP, remaining knowledge/hardware and sources files, and experience files.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:09:50 [assistant]

Let me check the external libraries and read the root scattered files.
- [tool] Glob
- [tool] Glob
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:10:04 [assistant]

Let me confirm the memory-vs-knowledge source duplication and read the remaining root files.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:10:22 [assistant]

Let me get script headers for accurate one-liners and read the last root files.
- [tool] Grep
- [tool] Read
- [tool] Read

### 2026-08-15 15:10:40 [assistant]

Let me quickly read the remaining knowledge/hardware file headers to finalize one-line descriptions.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-15 15:12:47 [assistant]

I've completed the read-only scan. Here is the structured knowledge inventory report.

---

# 现状知识盘点报告（只读扫描）

## A. 文件清单

### A1. 项目知识库 `D:\Newtest\CLAUDE_PROCESS\.claude\`

**agents\（18 个）**
| 文件 | 存什么 |
|---|---|
| `dual-parse-agent.md` | DFT+资源分配表解析 → TestItemMeta（路径 A/B） |
| `relay-agent.md` | 继电器闭合 + 闭环验证（Step0~12） |
| `measure-agent.md` | MI/MV/Toggle/Trim 测量代码生成 |
| `power-on-agent.md` | 上电规格文档（R-PON 规则清单，已脚本化后留作溯源） |
| `power-off-agent.md` | 下电规格文档（R-POFF 规则清单，同上） |
| `check-agent.md` | 收尾 60+ 项检查（错误码 R/P/E 组） |
| `cbit-agent.md` | CBIT 定义四模式管理（review/create-step/create-auto/check） |
| `cbit-singlepoint-agent.md` | P1 单点继电器定义规格（C-P1/C-P2 规则） |
| `cbit-parse-agent.md` | 原理图/netlist 解析规格 |
| `cbit-check-agent.md` | P4 校验 V1~V8 规格 |
| `cbit-path-finder.md` | P2 通路追踪规格（P-P1~P11） |
| `cbit-path-namer.md` | P3 通路命名规格（歧义组复核） |
| `compile-agent.md` | 编译+Debug 闭环（调 compile.ps1） |
| `deploy-agent.md` | 自动开 STS8300 软件+VS（前置） |
| `testplan-agent.md` | 测试方案 Word 文档生成 |
| `rules-agent.md` | 自进化规则 Agent（/evolve rules） |
| `experience-agent.md` | 自进化经验 Agent（/evolve exp） |
| `sub-function-agent.md` | 自进化子函数 Agent（/evolve fn） |

**knowledge\sources\（6 个，L0 机台规范层）**
| 文件 | 存什么 |
|---|---|
| `acm200.md` | ACM200 源表量程/模式精简参考 |
| `fovie.md` | FOVIe 源表精简参考 |
| `fpvie.md` | FPVIe 大电流浮空源精简参考 |
| `hvie.md` | HVIe 高压源精简参考（未用，预留） |
| `qvme.md` | QVMe 快速电压表精简参考（未用，预留） |
| `accotest-api.md` | AccoTEST 自动化接口（Control/TestUI/LOT 生命周期） |

**knowledge\hardware\（10 个）**
| 文件 | 存什么 |
|---|---|
| `relays.md` | 继电器硬件规格 + 功能分类 + Cap/PU/P2P 应用规则（FR-001~003） |
| `closed-loop-model.md` | 闭环模型 + Kelvin/Non-Kelvin 理论 |
| `bus-topology.md` | BUS 拓扑 + 闭环 + Cap2 + E006 反偏 |
| `schematic-parsing.md` | 六任务解析工作流 + 功能分类 + 通路有效性 + 常见错误 |
| `test-strategy.md` | 大电流/差分电压/运放选型指南 |
| `pin-resource-map.md` | Pin→源表→继电器映射 |
| `voltage-inference.md` | 电压四类推断方法 |
| `pogo.md` | POGO 点位命名/引出 |
| `cbit-mapping.md` | CBIT 三源交叉引用命名约定 |
| `cbit-principles.md` | CBIT 常量体系通用原理 |

**knowledge\standards\（6 个）**
| 文件 | 存什么 |
|---|---|
| `rules-registry.md` | **规则注册表（已存在）**，active/draft/retired 生命周期 |
| `naming.md` | 函数/参数/源表/继电器/treg 命名 |
| `units.md` | 量程≥2× + 单位换算 + cbite.SetOn 格式 + 台阶式 |
| `framework.md` | 三套函数框架模板 + 占位符说明 |
| `merge_rules.md` | 合并规则（MR-000 零合并铁律） |
| `treg.md` | TREG Trim 系统知识库 |

**knowledge\experience\（3 个）**
| 文件 | 存什么 |
|---|---|
| `index.md` | 经验库索引 |
| `relay-check.md` | verify_relay_trace 实现陷阱经验 |
| `project-notes.md` | 项目专属决策/工具记录 |

**skills\（2 个）**
| 文件 | 存什么 |
|---|---|
| `nuvolta-codegen.md` | 主 Skill（codegen pipeline 编排，规则正文的二次副本） |
| `sch-parse.md` | 原理图解析 Skill |

**references\（3 个 cpp，无 index.md）**
| 文件 | 存什么 |
|---|---|
| `tm600-normal-highcurrent.cpp` | 最复杂案例（Normal+大电流+浮动源） |
| `sub-measure-template.cpp` | Trim sub.cpp 模板 |
| `toggle-template.cpp` | Toggle/AWG 代码片段 |

**`AGENT_MAP.md`** — Agent 全景地图（19 文件索引 + pipeline 关系）

### A2. 项目根目录散件 `D:\Newtest\CLAUDE_PROCESS\`

**txt（根）**
| 文件 | 存什么 |
|---|---|
| `继电器识别规范.txt` | cbit-agent 四模式 + 通路继电器创建/命名规范（旧权威源） |
| `源表规则.txt` | 闭环原则/模拟数字源分类原文（旧权威源） |
| `原理图解析基本规则.txt` | 六任务解析规则原文（旧权威源） |
| `常用测试要求和硬件选型-实践.txt` | 大电流/差分电压/运放选型原文（旧权威源） |
| `启动.txt` | 仅一句话"切换到 D:\Newtest\CLAUDE_PROCESS" |
| `使用说明.txt`→`使用说明.md` | 旧版三份资料说明（DFT/资源表/规则md） |
| `PINLIST.txt` / `accotest_manual.txt` / `UI界面.txt` | 旧参考资料转储 |
| `tmp_acm.txt` `tmp_hvie.txt` `tmp_hpvie.txt` `tmp_qvme.txt` `tmp_fxvie.txt` | 源表 API 临时转储 |
| `recover_stdafx.h.txt` | StdAfx.h 事故恢复副本 |
| `_tm113_215_overview.txt` `_regconfig_113_215.txt` | 临时解析转储 |
| `Offline Coding 全景工作流.txt` | 用户梳理的 offline coding 全景流程 |

**md（根）**
| 文件 | 存什么 |
|---|---|
| `规则文件DEEPSEEK.md` | 1366 行完整规则集（历史主权威，已过时） |
| `project_rules.md` | 项目规则+错误跟踪（E001~E017 **旧编号体系**） |
| `Check-DEEPSEEK.md` | 与 project_rules.md 近乎重复的错误跟踪副本 |
| `try_resource.md` | 资源分配表 Sheet20 转储（试验性） |
| `paths_txt_生成规范_平台无关版.md` | paths.txt 生成规范（平台无关版） |
| `使用说明.md` | 旧版资料说明 |
| `CLAUDE.md` | 项目概述+架构（2026-07-18 版，已过时） |
| `PROGRESS.md` | 进度日志（活跃） |
| `讨论记录-知识分层方案.md` | 知识分层 5 问方案（本任务上游设计） |
| `daylog\_template.md` `2026-08-09.md` `2026-08-10.md` | 每日档案（自进化数据源） |

**py/ps1（脚本，见 §A5）**

### A3. auto-memory `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\`

**nuvola-*.md（24 个规则/经验文件）**
| 文件 | 存什么 |
|---|---|
| `nuvolta-relay-checklist.md` | 11 步继电器检查清单 + BUS/Cap2/闭环规则 |
| `nuvolta-common-errors.md` | 常见错误 E001~E012/E028/E029 |
| `nuvolta-test-flow.md` | 测试流程 6 步法 + 合并优化 |
| `nuvolta-power-rules.md` | 上电/下电规则（R-PON-09 两段式 + 三步下电） |
| `nuvolta-measurement.md` | MI/MV/Trim 测量模板 + R-LOG/R-VIR |
| `nuvolta-range-rules.md` | 量程≥2× 决策表 + 量程列表 + 电阻单位 |
| `nuvolta-toggle-rules.md` | Toggle 测试规则（3 参数/SDA_INT/K43+K58/R-HYS） |
| `nuvolta-trim-rules.md` | Trim 测试规则（8 后缀/TRIM_NODE 大写/treg 查找） |
| `nuvolta-test-types.md` | 测试类型识别（Trim/AWG/Normal） |
| `nuvolta-high-current.md` | 大电流规则（FPVIe 14 项清单） |
| `nuvolta-floating-source.md` | 浮动源规则（iset/vset[AxB] 解析 + E006） |
| `nuvolta-anti-short-rule.md` | 反短接铁律 |
| `nuvolta-bus-vs-share.md` | BUS vs Share 三层分类 |
| `nuvolta-kelvin-contact.md` | Kelvin 接法/接触电阻/KELVIN 矩阵 |
| `nuvolta-framework.md` | 函数框架规则（AFX 注释/文件分工） |
| `nuvolta-source-name-mapping.md` | Pin_Channel_define.h 源表名映射 + FXVIe_PLUS |
| `nuvolta-testmode-before-register.md` | entertestmode 铁律 |
| `nuvolta-reference.md` | 项目文件位置指针 + 寄存器表 |
| `nuvolta-working-dir.md` | 默认工作目录偏好 |
| `nuvolta-compile-deploy.md` | 编译必须走 compile-agent/fast_rebuild |
| `nuvolta-context-management.md` | 上下文管理（代码存文件） |
| `nuvolta-skill-autosync.md` | 规则修正后同步 skill |
| `nuvolta-auto-progress.md` | 自动更新 PROGRESS.md |
| `nuvolta-codegen-progress.md` | codegen 进度详情（长文，含历次教训） |

**STS8300-*.md（10 个 API 参考，与 sources\ 大量重叠）**
| 文件 | 存什么 |
|---|---|
| `STS8300-system-functions.md` | 框架/全局/参数函数 API 参考 |
| `STS8300-acm200.md` | ACM200 完整 API 提取（含错误码，全章） |
| `STS8300-fpvie.md` | FPVIe 大电流 API 参考 |
| `STS8300-fovie.md` | FOVIe API 参考 |
| `STS8300-acm.md` | ACM 交流源 API 参考 |
| `STS8300-hvie.md` | HVIe 高压源 API 参考 |
| `STS8300-hpvie.md` | HPVIe 大功率源 API 参考 |
| `STS8300-qvme.md` | QVMe API 参考（FFT） |
| `STS8300-fxvie.md` | FXVIe API 参考（Gang/TMU/差分） |
| `STS8300-cbite-qtmue.md` | CBITe 继电器控制 + QTMUe 时间测量 API 全章 |

**其他 md（5 个）**
| 文件 | 存什么 |
|---|---|
| `MEMORY.md` | 记忆索引（任务触发映射） |
| `cbit-shorted-pin-rule.md` | DUT Pin 短路识别 |
| `sch-isolated-port-rule.md` | 孤立 PORT 检测 + TP 短接确认 |
| `self-evolving-agents.md` | 自进化三 Agent 设计 |
| `test-method-ramp-library.md` | ramp 64 函数库 + rampv/rampi 语义 |
| `dali-netlist-encryption.md` | DALI 网表 DLP 加密 + 字节模式写铁律 |

### A4. 外部库（仅目录结构）
| 路径 | 结构 | 一句话 |
|---|---|---|
| `D:\test_method\` | Test_Method.h/.cpp + gen_ramp64.py + AI.cpp + COMPONENT-STATISTIC/SCH-Connect-Map(.txt + .bak) | 专项 ramp 捕获库（64 函数 4 类型×4 ramp 源×4 cap 源），DLP 加密头 |
| `D:\shared_functions\` | README.md + registry\index.md + registry\changelog.md | 跨项目通用子函数库（上电/测量/寄存器/下电/常量），尚无 src/ |

### A5. 脚本（列名 + 一句话作用）
**管线脚本（活跃）**
| 脚本 | 作用 |
|---|---|
| `sch_parse.py`（DALI\） | 原理图解析六任务门控 → COMPONENT-STATISTIC + SCH-Connect-Map |
| `gen_cbit_defines.py` | P1 单点继电器定义 + P4 V1~V8 校验（内置 C-CBIT 13 规则） |
| `gen_paths.py` | P2 通路追踪 BFS（内置 P-FINDER 11 规则） |
| `gen_path_defines.py` | P3 通路继电器定义生成 → StdAfx.h（内置 P-DEF 13 规则） |
| `gen_power_sequence.py` | 上电/下电脚本化（内置 R-PON/R-POFF 19 规则） |
| `gen_dali_meta.py` | TestItemMeta/capAuthority 四集生成（含 --require-all 全覆盖门） |
| `verify_relay_trace.py` | 继电器/FR-001 反向检查 E（Cap 默认闭） |
| `verify_merge_rules.py` | 合并规则 M001~M004 强制 |
| `verify_awg_params.py` | AWG 三参数门禁 |
| `gen_ramp64.py`（test_method） | 64 ramp 函数生成器 |
| `fast_rebuild.ps1` | 秒级快速构建验证（含 DTE 保存前置） |
| `compile.ps1` | 完整编译+Debug+testui |

**批次/一次性脚本（历史产物，非管线）**
`gen_tm206_425.py`、`verify_tm206_425.py`、`gen_insert_tm403_425.py`、`verify_i2c_sv.py`、`_add_measure_osc.py`、`_sync_tm300_301_gen.py`、`_rename_trim_node.py`、`_fix_tm300_301.py`、`extract_stdafx_from_transcript.py`、`restore_stdafx.py`、DALI 下 `gen_v8.py`/`phase2_singlepoint.py`/`gen_final.py`/`debug_trace.py`/`append_tm105_107.py`/`append_tm108_112.py`/`replace_ramp_library.py`/`meta\*.py` — 各批次 TM 生成/修复/验证的一次性工具。

**STS8300 UI 自动化（compile/deploy 用）**
`auto_sts8300.py`、`start_sts8300.py`、`run_sts8300.py`、`diag_sts8300.py`、`spy_*.py`（login/vcproject/click/popup/vs_status）、`click_vcproject.py`、`record_actions.py`、`replay_actions.py`、`input_guard.py`、`patch.py` — STS8300 软件+VS 窗口自动化。

---

## B. 重复清单（最关键）

> ⚠ = 3 个以上位置重复。每个「内容」列出出现路径。

### B1. cbite / 继电器闭合 ⚠
| 内容 | 出现位置 |
|---|---|
| **cbite.SetOn 排他语义 + `-1` 结尾 + 空操作 `SetOn(-1)`（E011/R-SETON/R004）** | `memory\STS8300-cbite-qtmue.md`（§2.3 排他陷阱）、`memory\nuvolta-relay-checklist.md`（第10/11步）、`memory\nuvolta-common-errors.md`（E011）、`memory\nuvolta-framework.md`、`knowledge\standards\units.md`（SetOn 格式段）、`knowledge\standards\rules-registry.md`（R-SETON）、`根目录 project_rules.md` |
| **机械 vs 光耦继电器默认状态（E008）** | `memory\nuvolta-relay-checklist.md`、`memory\nuvolta-common-errors.md`（E008）、`knowledge\hardware\relays.md`（G6K/MOS 规格）、`memory\nuvolta-bus-vs-share.md`（导通规则） |
| **闭环两条件（Force-Sense + High-Low）（E009）** | `memory\nuvolta-relay-checklist.md`、`knowledge\hardware\closed-loop-model.md`、`knowledge\hardware\bus-topology.md`、`根目录 源表规则.txt`（原文）、`memory\nuvolta-common-errors.md`（E009） |
| **BUS vs Share 继电器三层分类（E007）** | `memory\nuvolta-bus-vs-share.md`、`memory\nuvolta-relay-checklist.md`、`knowledge\hardware\relays.md`（动态分类）、`knowledge\hardware\schematic-parsing.md`（功能分类）、`knowledge\hardware\bus-topology.md`、`memory\nuvolta-common-errors.md`（E007） |
| **Cap2 默认闭 + 按 PIN 例外（FR-001/E012）** | `memory\nuvolta-relay-checklist.md`、`memory\nuvolta-common-errors.md`（E012）、`memory\nuvolta-floating-source.md`、`knowledge\hardware\relays.md`、`knowledge\hardware\bus-topology.md`（§七）、`knowledge\standards\rules-registry.md`（FR-001）、`knowledge\experience\relay-check.md` |

### B2. 上电 ⚠
| 内容 | 出现位置 |
|---|---|
| **FV 上电 / MV 无 FI→FI=0+最小量程 10UA** | `memory\nuvolta-power-rules.md`、`memory\nuvolta-measurement.md`（§5）、`memory\nuvolta-range-rules.md`（决策表）、`knowledge\standards\units.md`（FV/FI 判断）、`knowledge\standards\rules-registry.md`（R-PON）、`gen_power_sequence.py` |
| **R-PON-09 小电流两段式上电（按 PIN 类型）** | `memory\nuvolta-power-rules.md`、`knowledge\standards\rules-registry.md`（R-PON+注释）、`gen_power_sequence.py` |
| **大电流三段式（FV=0→FI=0→Clamp）** | `memory\nuvolta-high-current.md`、`memory\nuvolta-floating-source.md`、`knowledge\standards\framework.md`（FPVI_INIT）、`根目录 project_rules.md`、`gen_power_sequence.py` |
| **浮动源台阶式上电（E006 反偏）** | `memory\nuvolta-floating-source.md`、`memory\nuvolta-power-rules.md`、`memory\nuvolta-high-current.md`、`根目录 project_rules.md`、`knowledge\hardware\bus-topology.md`（§九）、`knowledge\standards\units.md` |

### B3. 下电 ⚠
| 内容 | 出现位置 |
|---|---|
| **三步下电（归零→delay→RELAY_OFF）+ RELAY_OFF 统一量程表** | `memory\nuvolta-power-rules.md`、`knowledge\standards\units.md`（台阶下电）、`knowledge\standards\rules-registry.md`（R-POFF）、`根目录 project_rules.md`（10V/10MA）、`gen_power_sequence.py` |
| **FPVI OFF 量程 = 1V/10MA** | `memory\nuvolta-power-rules.md`、`memory\nuvolta-high-current.md`（14项第14）、`knowledge\standards\rules-registry.md`（R-POFF） |

### B4. 测量 / 量程 ⚠
| 内容 | 出现位置 |
|---|---|
| **MI/MV 模板（MeasureVI/GetMeasResult MIRET/MVRET）** | `memory\nuvolta-measurement.md`、`memory\nuvolta-trim-rules.md`、`knowledge\standards\treg.md`（measure 模板）、`knowledge\standards\framework.md`、`memory\STS8300-acm200.md`（API） |
| **量程≥2× 决策表 + 量程列表** | `memory\nuvolta-range-rules.md`（最全）、`knowledge\standards\units.md`、`根目录 project_rules.md`、`gen_power_sequence.py`（R-RNG） |
| **电阻单位（>100mA→mΩ，≤100mA→Ω）** | `memory\nuvolta-range-rules.md`、`knowledge\standards\units.md`、`根目录 project_rules.md` |
| **R-VIR 电阻=实测V/实测I** | `memory\nuvolta-measurement.md`（§2b）、`knowledge\standards\rules-registry.md`（R-VIR） |
| **测量前等待 1ms/2ms** | `memory\nuvolta-measurement.md`、`memory\nuvolta-high-current.md` |

### B5. 命名 ⚠
| 内容 | 出现位置 |
|---|---|
| **函数/参数命名（TMxxx/TMxxx_Trim）** | `knowledge\standards\naming.md`、`knowledge\standards\framework.md`、`memory\nuvolta-framework.md` |
| **AWG 三参数 `_Rise/_Fall/_Hys` 命名** | `knowledge\standards\naming.md`、`memory\nuvolta-toggle-rules.md`、`memory\nuvolta-test-types.md`、`knowledge\standards\framework.md`（Toggle 模板）、`根目录 project_rules.md`、`根目录 规则文件DEEPSEEK.md` |
| **Trim step0~N + 8 后缀命名（E001）** | `memory\nuvolta-trim-rules.md`、`memory\nuvolta-common-errors.md`（E001）、`knowledge\standards\naming.md`、`knowledge\standards\framework.md`、`knowledge\standards\treg.md` |
| **TRIM_NODE 变量名=大写（E028）** | `memory\nuvolta-trim-rules.md`、`memory\nuvolta-common-errors.md`（E028）、`knowledge\standards\framework.md` |
| **继电器命名（去 _Sx / Cap2 取中间字段）** | `knowledge\standards\naming.md`、`knowledge\hardware\relays.md`（命名模式）、`knowledge\hardware\cbit-mapping.md` |
| **源表命名（PIN_类型 / extern 权威）** | `knowledge\standards\naming.md`、`memory\nuvolta-source-name-mapping.md` |

### B6. 单位换算 ⚠
| 内容 | 出现位置 |
|---|---|
| **LogData 单位=spec（R-LOG：uA×1e6/mA×1e3/nA×1e9/mV×1e3）** | `memory\nuvolta-measurement.md`（§2a）、`knowledge\standards\units.md`、`knowledge\standards\rules-registry.md`（R-LOG） |
| **Hys 单位（R-HYS：电压→mV/电流→mA ×1e3）** | `memory\nuvolta-toggle-rules.md`、`memory\nuvolta-measurement.md`（§2a 特例）、`knowledge\standards\units.md`、`knowledge\standards\rules-registry.md`（R-HYS） |
| **程序电压 V / 电流 A** | `knowledge\standards\units.md`、`根目录 project_rules.md` |
| **电阻单位公式 V/A×1000** | `memory\nuvolta-range-rules.md`、`knowledge\standards\units.md`、`根目录 project_rules.md` |

### 其他高重复（跨块）
| 内容 | 出现位置 |
|---|---|
| **Trim 判定铁律（DFT Trim=Y 无条件走框架，禁静默降级）** | `memory\nuvolta-trim-rules.md`、`memory\nuvolta-test-types.md`（整段复制）、`knowledge\standards\treg.md`、`knowledge\standards\framework.md` |
| **测试类型识别（Trim/AWG/Normal）** | `memory\nuvolta-test-types.md`、`根目录 规则文件DEEPSEEK.md`、`根目录 project_rules.md` |
| **entertestmode 铁律** | `memory\nuvolta-testmode-before-register.md`、`knowledge\standards\framework.md`（模板注释）、`skills\nuvolta-codegen.md` |
| **反短接铁律** | `memory\nuvolta-anti-short-rule.md`、`knowledge\hardware\schematic-parsing.md`（§四）、`knowledge\hardware\relays.md` |
| **源表 API（ACM200/FOVIe/FPVIe/HVIe/QVMe）** | `memory\STS8300-*.md`（全章提取）↔ `knowledge\sources\*.md`（精简版）**成对重复** |

---

## C. 散件清单（根目录 → 内容 → 建议去向）

| 根目录文件 | 内容 | 建议去向 |
|---|---|---|
| `源表规则.txt` | 闭环/源表分类原文 | **已迁移**到 `closed-loop-model.md`，归档/删 |
| `继电器识别规范.txt` | cbit 四模式+通路继电器命名 | **已迁移**到 `relays.md`+`cbit-principles.md`+`schematic-parsing.md`，归档/删（多处仍引用它为"权威"，删前须改引用） |
| `原理图解析基本规则.txt` | 六任务解析原文 | **已迁移**到 `schematic-parsing.md`，归档/删（同上引用） |
| `常用测试要求和硬件选型-实践.txt` | 大电流/差分电压/运放 | **已迁移**到 `test-strategy.md`，归档/删 |
| `规则文件DEEPSEEK.md` | 1366 行完整规则集（历史主权威） | **已迁移**到 knowledge\，归档 |
| `project_rules.md` | 项目规则+错误跟踪（旧 E001~E017 编号，与 nuvolta-common-errors E001~E012 **编号冲突**） | 归档/删，错误码收敛到 rules-registry |
| `Check-DEEPSEEK.md` | 与 project_rules.md 近乎重复 | 归档/删 |
| `try_resource.md` | 资源分配表 Sheet20 转储 | 已迁移到 `pin-resource-map.md`，删 |
| `paths_txt_生成规范_平台无关版.md` | paths.txt 规范 | 与 `gen_paths.py`/`schematic-parsing.md` 重叠，归档进 references 或删 |
| `使用说明.md` / `启动.txt` | 旧资料说明/一句 cd | 已被 `nuvolta-working-dir.md` 取代，删 |
| `PINLIST.txt` `accotest_manual.txt` `UI界面.txt` | 旧参考转储 | 归档/删 |
| `tmp_*.txt`（5 个） | 源表 API 临时转储 | 删 |
| `recover_stdafx.h.txt` | StdAfx.h 恢复副本 | 事故产物，归档 |
| `_tm113_215_overview.txt` `_regconfig_113_215.txt` | 临时转储 | 删 |
| `Offline Coding 全景工作流.txt` | 用户梳理流程 | 已并入 `讨论记录-知识分层方案.md`，归档 |
| `CLAUDE.md` | 项目概述（架构 2026-07-18 版已过时） | 保留但需更新为 AGENT_MAP.md 当前状态 |
| `PROGRESS.md` / `daylog\*` | 进度/每日档案 | 保留（活跃数据源） |
| `讨论记录-知识分层方案.md` | 知识分层方案设计 | **保留**（本任务的上游方案） |
| `DALI\_dump_*.txt` `phase1_*.txt` `phase2_singlepoint_output.txt` | 解析中间转储 | 可删（产物已合并为 COMPONENT-STATISTIC/SCH-Connect-Map） |

---

## D. 收敛对照表

> 目标三注册表：`rules-registry.md`（已存在）、`references/index.md`（**缺失**）、`functions-registry.md`（**缺失**）。

| 内容 | 应收敛到 |
|---|---|
| cbite.SetOn 排他/格式/空操作 | `rules-registry.md`（R-SETON，已收）→ 其余位置改引用 ID |
| 机械/光耦默认状态 | `rules-registry.md`（新增 ID）正文在 `knowledge/hardware/relays.md` |
| 闭环两条件 | `knowledge/hardware/closed-loop-model.md`（L0/L1 正文）→ memory 只留指针 |
| BUS vs Share 三层分类 | `knowledge/hardware/relays.md`（正文）+ `rules-registry.md`（E007 引用） |
| Cap2 默认闭（FR-001） | `rules-registry.md`（FR-001，已收） |
| 上电/下电序列（R-PON/R-POFF） | `rules-registry.md`（已收，正文指向 gen_power_sequence.py 内置 RULE_COVERAGE） |
| 量程≥2× / 量程列表 / 电阻单位 | `knowledge/standards/units.md`（L1 正文）+ `rules-registry.md`（R-RNG 引用） |
| R-LOG / R-HYS / R-VIR 单位换算 | `rules-registry.md`（已收三条） |
| 命名规则（函数/参数/AWG/Trim/继电器/源表） | `knowledge/standards/naming.md`（正文）+ `rules-registry.md`（E001/E028/E005 引用） |
| Trim 判定 + 8 后缀 + TRIM_NODE | `knowledge/standards/treg.md` + `framework.md`（正文）+ `rules-registry.md`（引用） |
| entertestmode 铁律 | `rules-registry.md`（新增 ID） |
| 反短接铁律 | `knowledge/hardware/schematic-parsing.md` §四（正文）+ `rules-registry.md`（P006 引用） |
| 机台 API（ACM200/FOVIe/FPVIe/HVIe/QVMe/CBITe/QTMUe） | `knowledge/sources/*.md`（L0 唯一家）；memory `STS8300-*.md` 降级为"去 sources 查"指针 |
| 源表名映射 / FXVIe_PLUS | `knowledge/sources/`（新增 fxvie_plus.md）+ `naming.md` |
| 代码案例（tm600/sub/toggle cpp） | `references/index.md`（**待建**，按测试类型索引） |
| ramp 库 / shared_functions 函数签名语义 | `functions-registry.md`（**待建**） |
| 经验类（relay-check/project-notes/编译陷阱） | `knowledge/experience/`（已就位）+ index.md 补条目 |
| 散件 txt/md 规则原文 | 删除或归档，正文只留 knowledge\ 一份 |
| auto-memory 全部 nuvola-*.md | 降级为"进度指针/非显而易见上下文"，规则正文移入 knowledge\，不复制正文 |

---

## 关键结论

1. **最严重的重复在 auto-memory 与 knowledge 之间**：`nuvola-*.md` 的规则正文几乎全部在 `knowledge/`（尤其 `rules-registry.md` + `hardware/relays.md` + `standards/units.md` + `standards/naming.md`）已有或应有唯一家，构成"规则正文两套副本"。`STS8300-*.md`（10 个全章 API 提取）与 `knowledge/sources/*.md`（精简版）是**成对重复**。

2. **根目录散件是历史主权威，已大部迁移但仍被反向引用**：`源表规则.txt`/`继电器识别规范.txt`/`原理图解析基本规则.txt`/`常用测试要求和硬件选型-实践.txt`/`规则文件DEEPSEEK.md` 的正文已进 `knowledge/`，但 `relays.md`/`schematic-parsing.md`/`cbit-principles.md` 仍标注这些 txt 为"权威规范"，删前必须改引用。

3. **错误编号体系冲突**：根目录 `project_rules.md`/`Check-DEEPSEEK.md` 用旧 E001~E017（2026-07-04），而 `nuvolta-common-errors.md` 用新 E001~E012/E028/E029（E008 在两套里含义不同），这是隐患，应废弃旧体系。

4. **三注册表缺两个**：`rules-registry.md` 已建立且结构良好（active/draft/retired + 强制层映射），但 `references/index.md` 和 `functions-registry.md` 尚未创建，`references/` 目前只有 3 个裸 cpp 无索引。

5. **收敛方向已明确**（`讨论记录-知识分层方案.md` 已定）：一条知识=一个 ID=一个正文位置（knowledge\ 权威），auto-memory 只留指针，根目录散件归档删除，脚本内置 RULE_COVERAGE 作为机器强制层。本报告即该方案 Q1 诊断所预言的"现状盘点"落地。
