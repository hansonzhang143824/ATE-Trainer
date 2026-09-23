# 会话 #30 — 背景：Nuvolta STS8300 ATE 离线代码生成体系。codex 迁移产物在 `D:\\Newtest\\CODEX\\_PROCESS`，它做了 5 个 

- 文件：`agent-a8d91b60c2e8db57d.jsonl`（项目 subagents）
- 时间：2026-08-23T15:14:44.857Z → 2026-08-23T15:16:09.068Z，大小 0.2 MB
- 用户消息 1 条 / 助手文本 6 段 / 工具调用标记 20 行

---

## 对话正文（工具输出已剥离）

### 2026-08-23 15:14:44 [user]

背景：Nuvolta STS8300 ATE 离线代码生成体系。codex 迁移产物在 `D:\Newtest\CODEX\_PROCESS`，它做了 5 个 reviewer agent + 一个 8 步 skill（材料门在 Step 3）+ V2 硬件解析入口。我要评估其中「reviewer 化」和「材料门」的实质，设计如何只吸收其思想（而非全套替换）。请精确读取以下文件，返回**精确内容**（关键条款原文、门禁表述、输入输出），不要泛泛总结：

1. `D:\Newtest\CODEX\_PROCESS\.claude\agents\hardware-topology-reviewer.md`
2. `D:\Newtest\CODEX\_PROCESS\.claude\agents\test-design-reviewer.md`
3. `D:\Newtest\CODEX\_PROCESS\.claude\agents\verification-build-reviewer.md`
4. `D:\Newtest\CODEX\_PROCESS\.claude\agents\knowledge-curator.md`
   - 对每个：返回其职责、输入、输出、门禁/判定标准、tools 字段。特别关注：这些 agent 是"执行生成"还是"审核把关"？它们是否承担 relay 闭合 / 测量代码的生成？

5. `D:\Newtest\CODEX\_PROCESS\.claude\skills\nuvolta-codegen.md`（skill 2.0，约40行）
   - 完整返回 8 步流程，特别精确抄录 Step 3「材料门」的原文表述（材料存在却未读取不得生成、param_type_index 判定、HS_ZCD/LSZCD 必须同时读等）。

6. `D:\Newtest\CODEX\_PROCESS\run_hardware_parse.py`
   - 返回：入口参数、`--engine v2` 与 `--engine legacy` 的切换机制、它调用哪些脚本、如何区分两种引擎的 config。

请分节返回，附文件路径。重点：明确指出「5 个 reviewer agent 是否包含 relay/measure 的生成执行角色」这个事实，以及「材料门」的确切可执行机制（是否有配套检查脚本，还是只写在 skill 文字里）。

### 2026-08-23 15:14:47 [assistant]

I'll read all the requested files in parallel, and also list the agents directory to account for all 5 reviewer agents.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Glob

### 2026-08-23 15:14:53 [assistant]

I have the 4 requested files plus the skill and the Python entry. The directory contains a 5th agent (`workflow-orchestrator.md`) that the skill references, and the user's question about "5 reviewer agents" and relay/measure generation requires it. I also need to check whether the material gate has any executable enforcement beyond the skill text.
- [tool] Read
- [tool] Glob
- [tool] Glob
- [tool] Grep

### 2026-08-23 15:14:59 [assistant]

Let me check the material-gate enforcement more precisely: where `param_type_index.md` actually lives, what the grep hit in the V2 adapter is, and which verification scripts exist.
- [tool] Glob
- [tool] Glob
- [tool] Grep
- [tool] Grep

### 2026-08-23 15:15:08 [assistant]

The material gate's exact executable mechanism is the key question. Let me verify whether any script enforces it, and read the `param_type_index.md` index that the skill references.
- [tool] Read
- [tool] Grep

### 2026-08-23 15:15:23 [assistant]

I have all the requested content. Let me quickly confirm the executable gate landscape (which scripts enforce what) to precisely answer the "material gate" mechanism question.
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-23 15:16:09 [assistant]

# CODEX 迁移产物精确内容报告

所有文件均位于 `D:\Newtest\CODEX\_PROCESS\`。目录实际包含 **5 个 agent**（你列了 4 个，缺 `workflow-orchestrator.md`，它是唯一的编排角色，且 skill 多次引用它，故一并纳入）。

---

## 1. `.claude\agents\hardware-topology-reviewer.md`

**tools 字段：** `Read, Grep, Bash`（无 Edit/Write）

**职责（description 原文）：** "审查网表、CBIT、ChannelMap、VS资源/继电器定义，证明 Source 到 DUT PIN 的通路并处理硬件歧义"

**输入（原文）：**
- 当前 build manifest
- DALI 网表、CBIT 表
- VS 工程及其 ChannelMap、资源定义、继电器定义
- 自动解析得到的 topology graph / candidate paths
- TestItemPlan 的 pins、floating pairs 和测量目标

**输出：PathProof（原文，每条证明至少包含）：**
- source object/type/channel
- DUT pin 与回流端
- 有序 net/relay edges（不能只给 relay 并集）
- required relay 及默认/通电状态
- Kelvin Force/Sense、BUS/Share/Cap/P2P 影响
- 非目标 pin 是否被连接或驱动
- 证据文件、行/节点标识和输入哈希
- `PASS / AMBIGUOUS / FAIL`

**所有权边界（原文）：** "资源和继电器定义由外部团队生成。本角色默认不改这些文件；发现错误时输出结构化差异报告，供外部团队修正。只有用户明确要求接管生成时，才进入单独工作流。"

**禁止（原文）：** "按源表对象名猜类型、把全局 relay 并集当当前通路、用最短路径代替电气可用性、忽略机械继电器默认态。"

**角色定性：审核/证明角色，非生成。** 判定标准 = PASS/AMBIGUOUS/FAIL 三值；skill 限定"仅歧义项调用"此角色。

---

## 2. `.claude\agents\test-design-reviewer.md`

**tools 字段：** `Read, Grep, Bash`

**职责（description 原文）：** "将 DFT 与硬件证据转换为测试结构和参数方法计划，处理寄存器、量程、时序、测量、日志及例外"

**"只做需要工程判断的部分"（原文）：**
- 选择结构类别：trim、contact、OTP/MTP read/burn、P2P leakage、leakage、general 等。
- 选择参数方法：RDSON、current sense、ADC、UVLO、current threshold、frequency、AMUX、closed-loop、OS、leakage、OTP、Kelvin 等。
- 明确 force/measure、range、clamp、delay、register sequence、公式、单位和日志映射。
- 对材料冲突或缺失输出 `AMBIGUOUS`，不得静默降级。

**输出：TestItemPlan（原文）：** "一个 TM 一份计划，包含硬件 PathProof 引用、PowerPlan、RegisterPlan、MeasurementPlan、LogPlan 和 exception/waiver。"

**合并规则（原文）：** "默认一个 TM 一个函数。若确需合并，必须存在 item-level waiver：列出 TM、共同硬件状态、共同流程、批准者、日期和理由。没有 waiver 时禁止合并。"

**关键句（原文）：** "确定性代码段由生成器生成，本角色不复制粘贴模板实现。"

**角色定性：设计/判定角色，非代码生成。** skill 限定"仅策略/例外调用"。测量/relay 代码明确由"生成器"产出，本角色不写。

---

## 3. `.claude\agents\verification-build-reviewer.md`

**tools 字段：** `Read, Grep, Bash`

**职责（description 原文）：** "独立验证生成代码、硬件闭环、测试生命周期、meta映射和编译证据；用户触发时执行构建"

**独立验证原则（原文）：** "生成器的 `--audit-rules` 只能证明结构覆盖，不能作为最终正确性证明。本角色必须从 manifest、IR/plan 和最终源码反向验证。" 以及："本角色负责第二层"跨项目统一门禁"，只在全部目标 TM 已分别通过 `verify_single_fn.py --fn <当前TM>` 后介入。第一层单函数冒烟由 `workflow-orchestrator` 在逐 TM 生成循环中立即调度；单函数冒烟 PASS 不能代替本角色的整批独立验证。"

**进入条件（原文，3 条）：**
1. 本批目标 TM/scope 已冻结。
2. 每个目标 TM 都有独立的单函数冒烟 PASS 证据。
3. 本批最终候选源码、meta、PathProof 和 manifest 哈希已冻结。
- "缺少任一条件即拒绝给出整批 PASS。"

**最低门禁（原文，10 条）：**
1. manifest 文件哈希和项目身份没有漂移。
2. 使用 `check_testitems_meta.py --require-all --require-scope <本批范围>` 证明每个 TM 的函数、meta 和 DFT 双向一一对应；默认不合并。
3. Step 1~6 生命周期有序且同一函数内闭合。
4. 每个 source→DUT pin PathProof 的全部 required relays 在该函数 Step 1 出现。
5. 无非目标 pin 驱动、无 Share 两侧误闭、浮动源有回流端。
6. 上电、寄存器、测量、下电、单位和 LogData 与计划一致。
7. TODO/stub helper 不得进入生产调用链。
8. 整批门禁只对全部目标 TM 的最终候选执行一次；任一项修复后，必须确认该项重新通过单函数冒烟，再重跑整批门禁。
9. 整批门禁 PASS 后核对发布后正式源码哈希与候选一致。
10. 编译只在用户触发后执行，记录命令、退出码、日志、源码和 DLL 哈希，并确认目标源码实际参与编译。

**失败报告要求（原文）：** "失败必须列出 TM、证据、期望和实际值；禁止只有笼统 PASS/FAIL。"

**角色定性：独立审核 + 用户触发编译。非生成。** 第 4 条是 relay 闭合的整批门禁，由脚本 `verify_relay_trace.py` 落地（见下）。

---

## 4. `.claude\agents\knowledge-curator.md`

**tools 字段：** `Read, Grep, Edit`（唯一有 Edit 的 agent，但被限定在知识维护）

**职责（description 原文）：** "用户触发的离线知识维护角色；将历史、daylog、案例和共享函数候选整理为 draft 并提交人工批准"

**原文关键条款：**
- "不参与生产代码生成。仅在用户明确要求"提炼规则/经验/函数"时运行。"
- "每条候选知识必须标注：`rule_id`、scope、status、source、effective_from、implemented_by、verified_by、exceptions。Claude 记忆和历史会话只能产生 draft，不能直接覆盖 active rule。"
- "冲突排序：项目/item scope > 明确人工批准 > 生效日期 > 证据等级。历史文件只用于追溯，不参与默认检索。"
- "共享函数必须经过：draft → 最小测试 → 至少两个确认案例 → 人工批准 → active。含 TODO 或恒定成功返回的实现不得发布。"

**角色定性：离线知识维护（draft 整理），明确"不参与生产代码生成"。**

---

## 5. `.claude\agents\workflow-orchestrator.md`（第 5 个 agent，必读）

**tools 字段：** `Read, Grep, Bash`

**职责（原文 9 条）：**
1. 首先运行 `project_manifest.py --write`；FAIL 时停止，禁止凭记忆补路径。
2. 确认 `project/chip/revision/site` 及网表、CBIT、VS 工程、ChannelMap、定义文件、TREG 哈希。
3. 只把硬件歧义交给 `hardware-topology-reviewer`。
4. 只把测试策略与例外交给 `test-design-reviewer`。
5. 按目标 TM 逐项执行"TestItemPlan → 生成到 staging → `verify_single_fn.py --fn <当前TM>`"；当前 TM 冒烟 PASS 前禁止开始下一个 TM。
6. 新模板/生成器批量放量前先跑 1 个代表函数；代表函数未通过不得批量展开。
7. 全部目标 TM 单函数冒烟 PASS 后，才把整批最终候选交给 `verification-build-reviewer` 做一次跨项目统一门禁；失败必须回到责任阶段，修复项重跑单函数冒烟后再重跑整批门禁。
8. 整批门禁 PASS 后才原子发布，并核对正式源码与候选源码哈希一致。
9. 编译和部署必须由用户触发，并绑定本次 manifest。

**阶段门禁（原文 G0–G5）：**
- G0 Manifest：输入齐全、哈希冻结、项目无混用。
- G1 Hardware：每个目标 pin 有有序 PathProof；外部定义只消费和校验。
- G2 Design：当前 TM 有 TestItemPlan；默认不合并。
- G3 Generate + L1 Smoke：当前 TM 生成到 staging 后立即执行 `verify_single_fn.py --fn <当前TM>`；PASS 才允许进入下一个 TM。
- G4 Batch Verify：全部目标 TM 冒烟 PASS 后统一执行一次；结构、通路、生命周期、meta↔code、API/单位全部通过。
- G5 Build：编译命令、退出码、日志、DLL 哈希可追溯。
- "任一门禁没有证据即为 FAIL，不允许写"根据经验应该正确"。"

**角色定性：编排者。** 第 5 条里"生成到 staging"的动作是**调用生成脚本/模板**，不是 agent 手写代码；relay/measure 代码的实体产出在 skill Step 3.2。

---

## 6. `.claude\skills\nuvolta-codegen.md`（skill 2.0，40 行）

**frontmatter description 原文：** "ATE offline coding 唯一生产入口；manifest冻结→硬件审查→逐TM设计/生成/冒烟→整批独立门禁→用户触发编译"

**8 步流程（原文，逐条照抄）：**

1. "每个执行批次先运行 `python project_manifest.py --write`；FAIL 立即停止。读取 manifest 后，不再从聊天记忆或目录中猜当前项目输入。"

2. "每个 manifest/硬件版本建立一次硬件基线：执行 `python run_hardware_parse.py --engine v2`，从 Dali-SCH CSV、CBIT 和 VS 工程定义生成连接图与原生 PathProof；仅歧义项调用 `hardware-topology-reviewer`。同一 manifest 下的 TM 复用已放行的 topology/PathProof；出现新 pin、新路径或输入哈希变化时重跑 G1，输入变化必须回到 G0。旧 EDIF Action 只允许通过 `--engine legacy` 显式回归/回退。"

3. "对目标 TM **逐项循环**，禁止先整批生成再统一冒烟："
   1. **材料门原文（逐字）：** "先按 `references/param_type_index.md` 判定参数类型并加载索引列出的 `chip/`、`method/` 和**全部** `code/` 黄金材料，把实际读取路径及关键约束写入 TestItemPlan；材料存在却未读取不得生成。Current Threshold / ZCD 必须同时读取 `code/HS_ZCD` 与 `code/LSZCD`，并写入 `BST>=SW`、`0<=BST-SW<=5V`、目标 `BST-SW=5V`。仅策略/例外调用 `test-design-reviewer`。"
   2. "用脚本/模板把当前 TM 的 relay、power-on、register、measure、power-off、log 生成到 staging。"
   3. "立即运行 `python verify_single_fn.py --src <staging源码> --fn <当前TM函数>`。"
   4. "冒烟 FAIL 时停留当前 TM，按证据回到设计或生成步骤；不得开始下一个 TM。"
   5. "冒烟 PASS 后才把当前 TM 加入本批最终候选，并进入下一个 TM。"

4. "使用新模板、修改后的模板或新生成器批量放量前，先选择 1 个代表函数完成"设计→生成→单函数冒烟"；代表函数未通过不得批量放量。编译仍遵守用户触发规则。"

5. "全部目标 TM 冒烟 PASS 后，才调用 `verification-build-reviewer` 对整批最终候选做一次独立反向门禁："
   - `check_testitems_meta.py --require-all --require-scope <本批范围>`；
   - `verify_relay_trace.py --meta <meta> --require-path-proof --warn-as-error`；
   - 按适用范围运行 `verify_awg_params.py --strict-params`、`verify_bst_sw_sequence.py --src <候选源码>`、`gen_cbit_defines.py --verify ...`、`gen_path_defines.py --verify`、`verify_merge_rules.py`、`verify_library_status.py`。

6. "整批门禁 FAIL 时必须列出 TM、证据、期望、实际和责任阶段；修复受影响项后，重新运行该项单函数冒烟，再重跑整批门禁。"

7. "整批门禁 PASS 后，才允许原子发布本批正式源码。发布后核对正式源码哈希与已验证候选一致。"

8. "只有用户明确说"编译/部署"才进入 G5，执行构建或 UI 自动化，并把命令、退出码、日志、源码/DLL 哈希绑定本次 manifest。"

**"当前输入与未来兼容"（原文）：** "当前原理图权威输入为 `ATE_Hardware_Parse_Skill_V2_Test_Package/Dali-SCH.csv`，硬件基线为 Dali-SCH CSV + CBIT + VS 工程；TREG 从 VS 工程项目项或工程目录发现。V2 输出位于 `Project/DALI/hardware_parse_v2/`。旧 EDIF 输入和原产物保留但不作为默认消费对象。资源/继电器定义是外部团队产物，本流程默认只消费和验证。"

**强制策略（原文，节选关键）：** "默认一个 TM 一个函数；显式 item waiver 才能合并。""生成器自审不能代替独立验证。""第一层是每个 TM 生成后立即执行的单函数冒烟；第二层是所有目标 TM 完成后的跨项目统一门禁，二者不可互相替代。""任何正式文件先在 staging 生成；单函数冒烟和整批门禁均通过后才原子替换。""所有产物绑定 manifest 哈希；输入漂移后必须重新开始。""编译只证明语法、链接和工程集成，不能替代黄金案例的功能约束；Current Threshold / ZCD 未通过 R-BST-SW 专项校验时，即使 Release/Debug 编译通过也不得发布。""旧 Agent/Skill 位于 `knowledge/standards/legacy-agent-specs`，禁止执行。"

---

## 7. `run_hardware_parse.py`

**入口参数（原文）：**
- `--engine`：`choices=("v2", "legacy")`，`default="v2"`。V2 是生产默认，legacy 仅作显式回归/回退。
- `--publish-definitions`：`action="store_true"`，控制是否真正写 `StdAfx.h` 继电器定义（默认只 `--no-write` 校验）。

**引擎切换机制（原文代码逻辑）：**
- `if args.engine == "legacy":` → 调用 `Project/DALI/sch_parse.py --config Project/DALI/hardware_parse_legacy/project_config.legacy.json.txt`，打印 `"LEGACY HARDWARE PARSE: PASS (explicit fallback; production default unchanged)"`，`return 0`。
- 否则走 V2 路径：`csv_schematic_adapter_v2.py` → `csv_pathproof_v2.py` → `gen_path_defines.py` → `gen_cbit_defines.py`，打印 `"V2 HARDWARE PARSE: PASS"` + PathProof 路径。

**V2 分支调用的脚本（原文顺序）：**
1. `ATE_Hardware_Parse_Skill_V2_Test_Package/scripts/csv_schematic_adapter_v2.py`（cwd=workspace）
2. `ATE_Hardware_Parse_Skill_V2_Test_Package/scripts/csv_pathproof_v2.py`
3. `gen_path_defines.py --config <v2 config> --map <SCH-Connect-Map.v2.txt>`（无 `--publish-definitions` 时追加 `--no-write`）
4. `gen_cbit_defines.py --config <v2 config> --stat <COMPONENT-STATISTIC.v2.txt> --map <SCH-Connect-Map.v2.txt>`

**两引擎的 config 区分（原文路径）：**
- legacy：`Project/DALI/hardware_parse_legacy/project_config.legacy.json.txt`
- v2：`Project/DALI/hardware_parse_v2/project_config.v2.json.txt`；配套产物 `SCH-Connect-Map.v2.txt`、`COMPONENT-STATISTIC.v2.txt`、`path_proofs.v2.json.txt`
- 发布定义时读取活动 `project_config.json` 的 `inputs.relay_definitions`，备份 `StdAfx.h` 到 `Backup/StdAfx.h.before_hardware_parse_v2_<时间戳>.bak`。

---

## 两个核心事实的结论

**事实 A：5 个 reviewer agent 是否包含 relay/measure 的生成执行角色？—— 不包含。**

全部 5 个 agent 的 tools 都只有 `Read, Grep, Bash`（`knowledge-curator` 例外有 `Edit`，但明确"不参与生产代码生成"）。没有任何 agent 承担 relay 闭合或测量代码的实体生成：
- relay、power-on、register、measure、power-off、log 的代码生成发生在 **skill Step 3.2「用脚本/模板……生成到 staging」**，由 `workflow-orchestrator` 在第 5 条职责里调度生成脚本，不是 agent 手写。
- `test-design-reviewer` 明言"确定性代码段由生成器生成，本角色不复制粘贴模板实现"。
- relay 闭合的正确性由**脚本**验证（`verify_relay_trace.py` 的闭环规则、`verify_bst_sw_sequence.py` 的 BST-SW 序列），而非由 agent 生成。

**事实 B：材料门的确切可执行机制 —— 只有 skill 文字 + 数据索引，没有配套检查脚本。**

- `param_type_index.md` 位于 `D:\Newtest\CODEX\_PROCESS\.claude\references\param_type_index.md`，是**数据索引**（"参数 → 文件路径"对照表），供 LLM 定位材料，本身不是检查器。它明确登记 Current Threshold 案例为 `code/HS_ZCD` + `code/LSZCD`，标注"两份案例必须同时读取"、约束 `BST>=SW`、`0<=BST-SW<=5V`。
- 全仓库 grep 所有 `*.py` 中 `HS_ZCD|LSZCD|param_type_index|references/(code|method|chip)`，命中只有两个文件，且都不是材料门检查器：
  - `verify_bst_sw_sequence.py`（`TARGETS = ("TM607_BUCK_LS_ZCD", "TM608_BOOST_HS_ZCD", "TM609_BOOST_HS_NEG")`）——校验**生成后源码**里的 BST-SW 时序，是材料门约束的下游产物校验，不是"材料是否被读取"的检查。
  - `ATE_Hardware_Parse_Skill_V2_Test_Package/scripts/adapt_tm607_609_bst_sw.py`——往适配代码里写黄金注释字符串。
- 因此"材料存在却未读取不得生成"**没有机器可执行的检查脚本**，只存在于 skill Step 3.1 的文字约束中，靠 LLM 遵循执行。它在流程里唯一的"结构锚点"是 `workflow-orchestrator` 的 G2 门禁"当前 TM 有 TestItemPlan"（Step 3.1 要求把"实际读取路径及关键约束"写入 TestItemPlan），以及 G4 的 `check_testitems_meta.py`（但那只证明 TM↔meta↔DFT 双向对应，**不**证明材料被读取）。若要吸收该思想并做成可强制执行的机制，需要在生成脚本或 `verify_single_fn.py`/新校验器里加"TestItemPlan 声明的材料路径必须实际存在且与索引一致"的检查。

**可执行门禁脚本全景（供对照）：** `project_manifest.py`（G0）、`run_hardware_parse.py`（G1）、`verify_single_fn.py`（G3/L1 冒烟，检查 placeholder/花括号/lifecycle 等 7 项）、`check_testitems_meta.py`、`verify_relay_trace.py`、`verify_awg_params.py`、`verify_bst_sw_sequence.py`、`gen_cbit_defines.py --verify`、`gen_path_defines.py --verify`、`verify_merge_rules.py`、`verify_library_status.py`（G4），用户触发的编译（G5）。**材料门不在其中。**
