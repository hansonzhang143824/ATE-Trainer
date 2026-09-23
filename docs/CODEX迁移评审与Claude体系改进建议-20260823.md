# CODEX 迁移评审与 Claude Code 体系改进建议

日期：2026-08-23  
工作目录：`D:\Newtest\CODEX\_PROCESS`  
接收方：Claude Code / DeepSeek ATE Offline Coding 工作流维护者  
范围：Agent、Skill、Action、知识库、硬件解析、中间产物、代码生成、验证与 VS 编译迁移  
限制：本轮未读取机台手册正文；机台规则继续使用已有摘要和已生效规则，只有出现 API/量程歧义时才按需检索原手册。

---

## 0. 执行结论

原体系的主要价值没有问题：ATE 领域知识丰富，DFT、原理图/CBIT、寄存器、黄金案例、测试方法、上下电经验和编译脚本都已经积累。迁移的核心不是重写这些知识，而是解决以下工程化问题：

1. Agent 数量过多，确定性任务也交给 Agent，造成重复读取、职责重叠和结论漂移。
2. 同一规则在 memory、knowledge、旧文档、Skill 和脚本中存在多个正文副本，容易出现“读取了错误版本”。
3. 工作流描述了应该读取黄金案例，但此前没有机器证据证明实际读取过，导致 TM607～609 编译通过却违反 BST–SW 压差规则。
4. 编译被错误地当成功能正确性的强证据；实际上编译只能证明语法、链接和工程集成。
5. 迁移验证最初复用了部分旧中间产物，不能证明新入口真正完成“从输入到代码”的闭环。
6. Action 清单与实际文件状态没有自动同步，清单中的“完成/待办”会逐渐失真。

目前已经完成架构收敛、硬件解析 V2 迁移、旧 Action 保留、两层检查、正式 VS 双配置编译和 ZCD 功能修正。当前可以继续使用，但仍建议完成第 4、5 节列出的 Action 后，再把该体系视为可稳定复制到新芯片/新项目的标准平台。

---

## 1. 发现的问题与改进决策

### 1.1 Agent 过多，职责按“代码步骤”切得过细

原体系把 relay、power-on、measure、power-off、check、compile、deploy、CBIT 各阶段进一步拆成约 18 个 Agent。问题是：这些角色会重复读取同一份 DFT、通路和规则，而且每个 Agent 都可能重新解释上下文，导致接口成本高于推理收益。

决定：

- 生产链路收敛为 4 个 Agent：Workflow Orchestrator、Hardware & Topology Reviewer、Test Design Reviewer、Verification & Build Reviewer。
- Knowledge Curator 作为用户触发的离线维护角色，不进入日常生产链路。
- CBIT 解析、通路查找、meta 生成、上下电序列、单函数检查等确定性工作改由脚本执行。
- 原 18 Agent / 2 Skill 不删除，迁移至 `legacy-agent-specs/`，只作为规则溯源，禁止作为生产入口。

效果：减少多 Agent 重复推理；把“是否执行过”从 Agent 自报转为脚本结果；保留历史规则来源，避免迁移时知识丢失。

### 1.2 输入路径和版本依赖聊天记忆

原流程存在从当前目录、历史会话或 Claude memory 推断项目输入的情况。遇到 DALI 原理图更新、加密 CSV、VS 工程切换时，容易复用旧输入或旧中间产物。

决定：

- 建立 `project_config.json` 作为项目输入唯一入口。
- 建立 `project_manifest.py`，冻结 project/chip/revision/site、DFT、Dali-SCH、CBIT、VS 工程、ChannelMap、TREG、资源/继电器定义及源码哈希。
- 任何输入哈希变化，旧 PathProof、TestItemPlan、代码和编译证据全部失效，必须回到 G0/G1。

效果：当前 manifest 验证状态为 PASS；正式 `test.cpp`、`StdAfx.h` 和专项校验器已被 manifest 记录。

### 1.3 原理图解析入口和中间产物权威不清晰

迁移过程中先后出现 `schdoc.txt`、加密 CSV 明文副本、`unified_circuit_connectivity...csv`、Dali-SCH CSV 和旧 EDIF 网表等候选输入。如果不固定权威输入，会出现 SCH-Connect-Map 没有更新但下游继续执行的问题。

决定：

- 当前默认权威输入固定为 `ATE_Hardware_Parse_Skill_V2_Test_Package/Dali-SCH.csv`。
- 默认 Action 改为 `run_hardware_parse.py --engine v2`。
- 旧 EDIF 解析完整保留，通过 `--engine legacy` 显式执行，不删除、不覆盖旧黄金产物。
- V2 独立生成 `SCH-Connect-Map.v2.txt`、`COMPONENT-STATISTIC.v2.txt`、PathProof 和验证清单。
- 新旧原理图差异不再简单按“必须相同”处理，而是区分解析失败与批准的硬件版本差异，并绑定输入哈希。

效果：V2 解析门 8/8 PASS；648 条 PathProof、210 对 Kelvin、0 failure；321 条有效通路定义反向验证 PASS。用户确认的硬件改版差异被保留，没有通过修改算法强行抹平。

### 1.4 资源/继电器定义的所有权边界不清晰

资源和继电器定义需要结合硬件、CBIT、ChannelMap 和 VS 工程，但该部分由其他工程师负责。如果 Offline Coding 流程擅自重新生成并覆盖，可能破坏外部团队的交付边界。

决定：

- `project_config.json` 明确 `resource_and_relay_definition = external_team`。
- 本流程默认只消费和验证：文件存在、工程引用、CBIT 一致性、Source→DUT PIN 闭环。
- 只有用户明确要求接管定义生成时，才进入单独工作流。

效果：既能完成通路证明，又不会无授权覆盖外部团队资产。

### 1.5 迁移验证曾复用旧中间文件

用户指出，迁移专用验证必须重新生成 SCH-Connect-Map、COMPONENT-STATISTIC、meta 和代码，而不能沿用旧文件后只验证编译。

决定：

- 迁移验证采用“新输入 → 新解析产物 → 新 PathProof → 新定义检查 → 新 meta/代码 → 正式编译”的闭环。
- 旧产物仅用于差异比较和回退，不作为 V2 PASS 的输入。
- 迁移完成后的正常使用恢复标准工作流，不要求每次都做新旧 A/B 迁移比较。

效果：证明了新默认入口可以独立生成下游证据；同时识别出 TM607 对旧 `K_FPVIL_TO_PGND` 的依赖，避免保留不存在的硬件通路来骗过编译。

### 1.6 每个项目检查与整批检查曾容易混淆

原流程中存在“所有项目写完再统一检查”的表达，但用户实际要求是两层：每个项目写完先检查，整批写完再统一检查。

决定：

- L1：每个 TM 生成到 staging 后立即执行 `verify_single_fn.py --fn <当前TM>`；当前项未 PASS 不得开始下一项。
- L2：全部目标 TM 的 L1 都 PASS 后，执行一次跨项目统一门禁。
- 修复某项后，该项先重跑 L1，然后整批重跑 L2。
- G5 编译仅在用户明确要求时执行。

效果：局部错误可以在当前 TM 截止，跨项目覆盖、meta、通路、合并和函数库状态仍由整批门禁检查，二者不互相替代。

### 1.7 编译通过被误当成功能正确

TM607～609 是本次最重要的反例：前一版实际进入 VS 工程并完成 Release/Debug 编译，但没有落实黄金案例的 BST–SW 压差。

证据：

- `param_type_index.md` 原本已把 Current Threshold 指向 `code/HS_ZCD + code/LSZCD`。
- 前次生成没有真正读取两份黄金 code，只使用了 DFT、寄存器、硬件通路和编译证据。
- 修正前 TM607 没有建立 BST；TM608/609 把 PMID 与 BST 都设置为绝对 5V，实际 `BST-SW=0V`。

决定：

- Current Threshold/ZCD 生成前必须同时读取 HS_ZCD 与 LSZCD，并把读取路径和关键约束写入 TestItemPlan。
- 新增 active 规则 `R-BST-SW`。
- 新增 `verify_bst_sw_sequence.py`，校验 K45、FV→FI 交接、上电台阶和反向下电台阶。
- 编译结果降级为 G5 工程集成证据，不能替代功能规则校验。

效果：TM607、TM608、TM609 专项校验全部 PASS；L1 全 PASS；正式 VS Release/Debug 均 0 error、0 warning；没有使用 `#if 0`。

### 1.8 规则和知识正文重复，Action 状态会漂移

原体系中同一规则分散在 auto-memory、knowledge、旧 txt/md、Skill 和脚本。另一个问题是 `工作流Action清单.html` 仍将已经完成的 CLAUDE.md 更新标为待办，将已建立但未完全覆盖的 references 简化为“待建”。

决定：

- 建立三注册表：规则、材料、函数。
- active rule 必须记录来源、scope、强制层；memory 和历史会话只能产生 draft。
- 旧 Agent/Skill 和历史主文档降级为 specification-only。
- Action 状态以后应由文件/测试证据生成，不再人工维护静态 HTML 状态。

效果：权威入口已经明显收敛，但自动知识审计和 Action 报告生成器仍未完成，见后续 Action。

---

## 2. 已完成动作与效果

| 已完成动作 | 主要产物 | 效果/证据 |
|---|---|---|
| 工作目录迁移到新根目录 | `D:\Newtest\CODEX\_PROCESS` | 后续工作统一在新目录开展；旧体系内容保留用于回退/溯源 |
| Agent 架构收敛 | `.claude/AGENT_MAP.md`、4 个生产 Agent、1 个 Curator | 从约 18 个生产 Agent 收敛为 4+1；确定性步骤脚本化 |
| 唯一生产入口 | `.claude/skills/nuvolta-codegen.md`、`CLAUDE.md` | Claude 不再从多个 Skill/旧 Agent 任意选择生产路径 |
| 旧工作流保留 | `knowledge/standards/legacy-agent-specs/` | 原 Action/Agent 规格未删除，状态明确为 historical/specification-only |
| 项目输入冻结 | `project_config.json`、`project_manifest.py`、`Project/DALI/build_manifest.json` | 输入、源码和验证工具哈希可追溯；输入漂移会使旧证据失效 |
| 新硬件解析方案并行引入 | `run_hardware_parse.py --engine v2` | 新方案先并行验证，旧 `--engine legacy` 保留；验证通过后 V2 成为默认 |
| 重新生成 V2 中间产物 | `hardware_parse_v2/SCH-Connect-Map.v2.txt`、`COMPONENT-STATISTIC.v2.txt` | 不依赖旧中间文件完成解析闭环 |
| 新旧原理图版本比较 | `migration_comparison.v2.json.txt` | 887 条一致、113 条仅旧、49 条仅 V2；差异按用户确认的硬件改版批准并绑定哈希 |
| 原生 PathProof | `path_proofs.v2.json.txt`、`PATHPROOF-VALIDATION.v2.txt` | 648 条接受路径、210 Kelvin 对、0 failure；不穿越 DUT，不把 relay 并集当有序通路 |
| Path/CBIT 下游验证 | `gen_paths.py`、`gen_path_defines.py`、`gen_cbit_defines.py` | 321 路径定义反向 PASS；CBIT overall PASS；V7 明确 SKIP 而非假 PASS |
| 两层代码检查 | `verify_single_fn.py`、`verification.md` | 每 TM L1 + 全批 L2 的执行粒度已经写入 Skill 和 Orchestrator |
| 迁移样本与正式 VS 验证 | TM000、TM000_1、TM101、TM106、TM107～110、TM607～609 | 目标函数保持在正式 `test.cpp`；正式 Release/Debug 构建可通过 |
| TM607 硬件改版适配 | 正式 `test.cpp` | 不保留已不存在的 `K_FPVIL_TO_PGND`；改用 High→PGND、Low→SW1，并修正电流符号 |
| TM607～609 黄金规则修正 | `R-BST-SW`、`verify_bst_sw_sequence.py` | 全过程满足 `BST>=SW`、`0<=BST-SW<=5V`；3 项专项 PASS |
| 正式代码安全发布 | `Backup/test.cpp.before_bst_sw_fix_20260823_212404.bak` 等 | 生产修改前有备份；未用 `#if 0` 或删除函数绕过编译 |
| 迁移报告和机器记录 | `MIGRATION-VALIDATION-REPORT.md`、`downstream_compile_validation.v2.json.txt` | 人可读结论与机器可读状态同时保留 |

### 2.1 当前最终构建证据

- 正式源文件：`D:\PROJECT6-DALI\devel\source\test.cpp`
- Python 明文 SHA-256：`8B2848785940134DE51E9B29951EA9A40F9C37F749E5B1D417EFD7B7DA309218`
- Debug 最终 DLL：`D:\PROJECT6-DALI\devel\F12011.dll`
- DLL SHA-256：`27F805E2A97539CFDC4FA01AFACAC730AF959D9555530061AC9F58012F212672`
- Release / Win32：PASS，0 error、0 warning
- Debug / Win32：PASS，0 error、0 warning
- `#if 0`：0
- DLL 修改时间晚于正式源文件，证明当前源码实际参与构建。

---

## 3. 原 A01～A14 Action 的当前复核状态

以下状态以 2026-08-23 的实际文件为准，不直接沿用旧 HTML 中的标签。

| Action | 当前状态 | 复核结论 | 后续动作 |
|---|---|---|---|
| A01 测试结构类型判定 | 已完成 | `test-types.md` 已有 7 类判定和 Trim 铁律 | 仅需纳入知识审计 |
| A02 寄存器配置位置与读取 | 部分完成 | `register-config.md` 只有 24 行骨架；不足以覆盖 test.cpp/sub.cpp、SV/treg 冲突和脚本读取证据 | P0：补完整规则和 TestItemPlan 字段 |
| A03 测量经验 | 未完成 | `measurement.md` 仅 16 行，仍是空壳；采样点、间隔、量程切换、Clamp、恢复 0 等未系统化 | P1：从黄金案例和已验证 TM 回填，active 铁律进 registry/validator |
| A04 上下电经验 | 未完成 | `power-sequence.md` 仅 17 行；R-PON/R-POFF 虽在注册表和脚本中，但经验层缺少典型波形、绕法和失败案例 | P0：优先补齐，特别是浮动源/BST/大电流 |
| A05 继电器检查清单 | 部分完成 | `relay-check.md` 已有 163 行，但偏向 `verify_relay_trace.py` 实现陷阱，不完全等同于 11 步工程检查清单 | P1：增加面向测试设计的 11 步清单，保留脚本实现章节 |
| A06 references 四件套 | 部分完成 | 已建立 code/chip/method/debug/circuit；当前约 code 12、chip 4、method 4、debug 1、circuit 0 | P1：按参数覆盖率补齐，不以“目录存在”判完成 |
| A07 参数类型索引 | 部分完成 | `param_type_index.md` 已建立并已用于 ZCD，但仍有 `_待归档_` 和材料覆盖缺口 | P0：增加 machine-readable material receipt 和覆盖率检查 |
| A08 函数注册表 | 部分完成 | `functions-registry.md` 已建立，但多项调用点仍为“待补”，64 ramp 当前只按家族登记 | P1：补签名、调用点、状态、最小测试证据和适用机台版本 |
| A09 知识完整性审计 | 未开始 | `gen_knowledge_audit.py` 不存在 | P1：建议提前，不必等所有内容补完；先审计重复正文、断链、空壳和过期状态 |
| A10 规则/Action 导出 | 未开始 | `gen_rules_report.py` 不存在 | P2：生成 Markdown/HTML/CSV，状态从证据计算 |
| A11 auto-memory 降级为指针 | 未确认完成 | 新工作根目录中无足够证据证明 Claude Code auto-memory 已全部降级；此动作需要在 Claude 的 memory 目录侧完成 | P1：列出 memory 文件和目标权威链接，禁止保留规则正文副本 |
| A12 更新 CLAUDE.md | 已完成 | 已改为入口+指针，指向 AGENT_MAP 和唯一 Skill | 更新旧 Action HTML 状态即可 |
| A13 资源/继电器定义 | 外部持续项 | 当前 VS 定义已纳入 manifest 并被验证；定义生成仍由外部团队负责 | P0 外部：建立交付合同、版本号和差异报告格式 |
| A14 TREG 定义 | 外部持续项 | `standards/treg.md` 内容较完整，当前 NU1201.treg 已被 manifest 发现；具体 Trim 定义仍依赖项目交付 | P0 外部：把 treg 完整性、参数同名和 VS 工程引用加入门禁 |

---

## 4. 迁移后新增的必要 Action

### M01：建立 TestItemPlan 的机器可读 Schema 和“材料读取回执”——P0

当前 Skill 已要求读取 `param_type_index.md`，但仍主要靠 Agent 遵守。应增加每个 TM 的 JSON/YAML TestItemPlan，至少包含：

- `tm_id`、parameter type、structure type；
- DFT 行/参数引用；
- PathProof ID；
- 实际读取的 chip/method/code/debug 文件及 SHA-256；
- 从黄金材料提取的 invariant；
- PowerPlan/RegisterPlan/MeasurementPlan/LogPlan；
- waiver 和人工批准。

L2 必须验证：索引要求的材料集合等于读取回执集合。这样可以从机制上阻止再次遗漏 HS_ZCD/LSZCD。

### M02：把 `R-BST-SW` 从固定 TM 专项脚本升级为通用 Power Invariant 验证器——P0

当前 `verify_bst_sw_sequence.py` 已可靠覆盖 TM607～609，但函数名和资源名仍是项目专用。建议升级为：

- 从 TestItemPlan 获取浮动节点、绝对电源和差分限制；
- 抽取代码中每一步 Set 状态；
- 构建离散电源状态时间线；
- 验证任意 `A-B` 压差上下限、先后次序和反向下电；
- 支持 BST–SW、BST–PMID、浮动 FPVI、高边 RDSON/Trim 等场景。

固定 TM 脚本可保留为回归测试，不应成为唯一实现。

### M03：修正 AWG 严格校验器的类型误报——P0

`verify_awg_params.py --strict-params` 当前对 TM425、TM607、TM608、TM609 存在既有误报：把单阈值 ZCD/Trim 套用为 Rise/Fall/Hys 迟滞规则。

建议：

- 校验器先消费 parameter type / structure type，而不是仅按函数中出现 ramp 推断；
- Single-threshold、Hysteresis、Trim 分开规则；
- 修正后用真实正例、反例建立回归测试；
- 未修正前不得把 4 个误报永久当“可忽略基线”。

### M04：建立统一 Pipeline Runner 和阶段证据账本——P0

目前唯一 Skill 已经描述 G0～G5，但仍需 Claude 逐条调用脚本。建议建立一个非 Agent 的 runner：

```text
run_pipeline.py --scope TM607,TM608,TM609 --through G4
run_pipeline.py --scope ... --build Both --user-approved
```

runner 只负责顺序、输入哈希、退出码、产物路径和状态，不负责工程判断。输出 `pipeline_run.json`，记录每个 TM 的 G2/G3/L1 和整批 G4/G5 证据。它可以防止漏跑 L1、漏跑专项验证或在输入漂移后继续使用旧 PASS。

### M05：把 Action 清单改为证据驱动——P1

旧 HTML 的 A06/A07/A12 状态已经与当前文件不一致。建议 A09/A10 合并实现：

- 检查目标文件存在、非空壳、TODO 数、引用完整性和对应验证器；
- 区分 `DONE / PARTIAL / EXTERNAL / BLOCKED / RETIRED`；
- 输出 Markdown + HTML + JSON；
- 每条状态附证据文件和最后验证时间。

### M06：清理并正式登记已知基线债务——P1

当前仍有以下已知项：

- `K168_R100M_VCP_F`、`K169_R100M_PB5_F`、`K170_R100M_VAC_F` 三个 StdAfx 历史命名/CBIT 对拍缺口；
- CBIT V7 当前 `SKIP_BY_DESIGN`，需要明确由哪个独立验证器提供同等证据；
- AWG 四项误报；
- 函数注册表多个调用点待补；
- shared_functions 当前无 active 实现。

每项需要 owner、scope、原因、临时处置、到期日和关闭证据。禁止仅以“发布前后都存在”长期豁免。

### M07：建立黄金案例回归套件——P1

黄金 code 不应只供 Agent阅读，还应转换为可执行或可解析的合同测试：

- RDSON：浮动源台阶、Clamp、大电流回零、实测 V/I；
- ZCD：BST–SW、电流方向、单阈值；
- UVLO/OVP：Rise/Fall/Hys 和单位；
- Trim：判型、step、后缀、sub.cpp ACTIVE measure；
- Contact/Leakage/OTP：相应结构合同。

每次修改 Skill、模板或验证器时，先跑黄金回归，再允许批量生成。

### M08：完成 Knowledge Coverage Matrix——P1

按 parameter type 建矩阵，列出 chip/method/code/debug、规则、函数、验证器、正例、反例。目录存在不等于覆盖完成。建议至少标记：

- `COMPLETE`：四件套和验证器完整；
- `USABLE_WITH_GAPS`：能生成但缺 debug/反例；
- `REFERENCE_ONLY`：只有概念或案例，不允许自动生成；
- `BLOCKED`：材料冲突或缺失。

### M09：明确 DLP 文件的统一读写 API——P1

当前规则要求 `.cpp/.h/.NET` 走 Python 字节模式，但仍有 PowerShell 脚本可能用 `Get-Content/Set-Content` 修改 VS 文件。建议封装统一 `dlp_io.py`：

- 自动检测编码/BOM/CRLF；
- 先完整编码成功再原子替换；
- 自动备份、计算 Python 明文哈希；
- 禁止目标路径写入失败时截断；
- 所有生成/发布脚本复用同一实现。

### M10：更新工作流架构图和 Action HTML——P2

架构图应明确：

- G0/G1 对同一 manifest 通常一次执行；
- G2→G3→L1 是逐 TM 重复循环；
- G4 是全部 TM 完成后统一执行；
- G5 仅用户触发；
- 迁移专用 A/B 验证不是日常项目生成流程。

同时将 A01～A14 状态更新为本报告第 3 节的复核结果。

---

## 5. 给 Claude Code 的体系级建议

### 5.1 不要继续增加按步骤拆分的 Agent

只有以下情况值得调用 Reviewer Agent：

- 硬件图存在多个电气可行路径或短接风险；
- 测试策略、测量方法、寄存器含冲突/例外；
- 最终整批需要独立反向审查。

CSV 解析、BFS、代码拼接、单位检查、生命周期、编译和报告生成都应优先脚本化。不要重新启用 legacy relay-agent、power-on-agent、measure-agent 等生产角色。

### 5.2 每个阶段必须交付“产物 + 验证证据”，不能只返回自然语言 PASS

建议统一状态合同：

```text
PASS       = 产物存在、输入哈希匹配、独立验证器退出码 0
AMBIGUOUS  = 存在多个合理解释，需要工程师决定
FAIL       = 已证明违反规则或材料缺失
SKIP       = 明确不适用，并记录替代验证证据；不能当 PASS
```

### 5.3 黄金案例读取必须可审计

Claude 每次开始生成单个 TM 时，应先输出并保存：

```text
PARAM_TYPE: Current Threshold
INDEX_ENTRY: references/param_type_index.md#Current-Threshold
MATERIALS_READ:
  - chip/Current-Threshold.md <hash>
  - method/Current-Threshold.md <hash>
  - code/HS_ZCD <hash>
  - code/LSZCD <hash>
INVARIANTS:
  - BST>=SW
  - 0<=BST-SW<=5V
  - single threshold, no Hys
```

没有该回执不得进入代码生成。

### 5.4 “编译通过”必须放在验证矩阵的最后一列

每个 TM 至少需要区分：

| 证据 | 证明什么 | 不证明什么 |
|---|---|---|
| DFT/meta | 参数、范围、单位、scope | 硬件通路和上电正确 |
| PathProof | Source→Relay→DUT PIN 可达 | 测试方法和寄存器正确 |
| 黄金案例/方法规则 | 测试架构和功能 invariant | 当前代码已经实现 |
| L1/L2 | 代码结构、映射和专项合同 | VS 工程能链接 |
| VS Build | 语法、链接、工程集成 | 芯片工作点和测试功能正确 |

### 5.5 不要从 memory 直接发布 active 规则

Claude memory 只保存索引、用户偏好和当前项目指针。长期规则正文必须进入 rules registry、reference 或 functions registry；Knowledge Curator 先写 draft，人工确认后才 active，并同步验证器。

### 5.6 发现新问题时同时修代码和修流程

TM607～609 的教训不是只改三段代码。正确闭环是：

1. 修正式代码；
2. 增加专项验证器和反例；
3. 更新方法文档与 active rule；
4. 更新主 Skill 的材料门；
5. 把验证器加入 manifest；
6. 更新迁移报告和 Action；
7. 重新执行 L1、专项校验和正式构建。

以后所有用户纠正都建议按此模式处理。

---

## 6. 建议执行顺序

### 第一阶段：先堵住会生成错误代码的缺口

1. M01 TestItemPlan Schema + 材料读取回执。
2. M03 修复 AWG 类型误报。
3. A02 补完整寄存器配置规则。
4. A04 补完整上下电经验，结合 M02 通用 Power Invariant。
5. A13/A14 建外部交付合同和门禁。

### 第二阶段：把执行过程变成可重复流水线

1. M04 Pipeline Runner + `pipeline_run.json`。
2. M07 黄金案例回归套件。
3. M09 DLP 统一读写 API。
4. M06 基线债务登记和关闭。

### 第三阶段：完善知识覆盖与可视化

1. A03、A05、A06、A07、A08 补内容。
2. M08 Knowledge Coverage Matrix。
3. A09/A10 + M05 证据驱动 Action/规则报告。
4. A11 清理 Claude memory 正文副本。
5. M10 更新 HTML 和流程图。

---

## 7. Claude Code 接手时的必读顺序

不要先读机台手册。先按以下顺序读取：

1. `CLAUDE.md`
2. `.claude/AGENT_MAP.md`
3. `.claude/skills/nuvolta-codegen.md`
4. `project_config.json`
5. `Project/DALI/build_manifest.json`
6. `.claude/knowledge/standards/rules-registry.md`
7. `.claude/references/param_type_index.md`
8. `.claude/knowledge/standards/functions-registry.md`
9. `.claude/knowledge/standards/verification.md`
10. `Project/DALI/hardware_parse_v2/MIGRATION-VALIDATION-REPORT.md`
11. 本报告第 3～6 节的剩余 Action。

只有遇到 source API、量程边界或机台行为在摘要中没有答案时，才按引用定位读取对应手册章节，不要整本加载。

---

## 8. Claude Code 的接手验收条件

在宣布“体系改进完成”前，至少需要满足：

- A02/A04、M01/M02/M03/M04 已完成；
- 任意一个新 TM 可以从 manifest 独立执行 G0→G4；
- 每个 TM 都产生材料读取回执、TestItemPlan、L1 证据；
- 整批产生 L2 报告，任何 SKIP 都有替代证据；
- 修改输入后旧证据自动失效；
- 黄金回归套件能捕获一次故意注入的 BST–SW、Hys 参数、relay 缺失和单位错误；
- 用户触发时，当前正式源码真实参与 Release/Debug 构建；
- 不使用 `#if 0`、删除目标函数、伪造中间产物或复用旧 PASS 绕过验证；
- Action 报告状态与实际文件/测试结果一致。

满足以上条件后，整套体系才从“依赖资深工程师持续盯流程”提升为“可审计、可回归、可复制的 ATE Offline Coding 平台”。

