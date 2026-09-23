# AgentTeams 职责与规则路由（长期入口）

本文件定义 DSH `ate-delivery` 团队的稳定分工。Captain 按产物依赖派任务和检查交接，不替专家作电气/测试方法决策；专家按本文件加载与自己有关的已有规则，不把旧流水线的 19 个 agent 原样搬进新团队。规则正文仍在原目录，本文件只建立所有权、读取指针和退回条件。

## 1. 决策权与交接

| 决策/产物 | 唯一责任角色 | 必须取得的证据 | 交给下游前必须说清楚 | 不得代替谁 |
| --- | --- | --- | --- | --- |
| DFT 测试意图 `dft-ir.json` | `dft-expert` | 原始 DFT、逐 TM `reg_config`、来源位置；meta 仅交叉核对 | 被测对象、激励/测量量、目标关系、数值/单位、显式时序、冲突和缺项 | 不选机台源表、继电器或黄金案例台阶 |
| 物理连接 `schematic-ir.json` | `schematic-expert` | SCH/CBIT、连接图、F/S 与默认态 | 源到 DUT 的候选通路、需动作继电器、共享/互斥、闭环及不通之处 | 不决定测试方法或用哪个候选通路 |
| 全局 Setup `setup-contract.json` | `setup-architect` | 两份 IR、源表/继电器定义、TReg、机台能力 | 可用资源目录、通路与通道归属、全局初始化、互斥/安全约束、可复用清理动作 | 不替逐 TM 策略作资源组合和完整测试步骤 |
| 逐 TM 测试计划 `test-plan.json` | `test-strategy-architect` | 上述三份产物、参数/功能类型索引、适用规则、已确认黄金案例 | 每端点资源选择、完整上电/测试/下电状态与顺序、专属寄存器依据、测量与计算、log、异常清理、未决项 | 不写 C++/机台 API；不把方法决策留给实现者 |
| ATE 代码与 manifest | `ate-implementer` | 已签收的计划与 Setup、机台手册、库函数 | 将指定资源/步骤映射成 API；记录范围、量程、备份和差异 | 不自行换源、改步骤、补寄存器意图或变更判限 |
| 独立规则审查 | `rule-reviewer` | 输入契约、代码 diff、active 规则和错误实例 | 可定位的 findings；阻断项退回其决策 owner 或实现者 | 不静默修改代码、不把案例惯例升为通用规则 |
| 门禁/编译 | `compile-diagnostician` | 审查通过的实现、构建环境与 gate 报告 | 真实构建结果、错误分类、剩余风险 | 只可独立修行为不变的机械错误 |

Captain 只协调依赖、固定输入哈希、记录裁定与阻断状态。涉及电气意图、资源选择、步骤、限值的争议退回对应 owner；无证据时不由 Captain 或下游猜测填空。用户的明确裁定记录为本次权威输入，但仍须标作用域、时间、来源并同步到下游产物。

## 2. 已有执行规则如何被新角色吸收

“吸收”是**按需读取、应用并引用现有权威文件**，不是复制一份容易漂移的规则，也不是让每个专家全量读取 `skills/nuvolta-codegen.md`。旧 `skills/AGENT_MAP.md` / `skills/nuvolta-codegen.md` 描述旧的单主代理流水线；在 AgentTeams 中仅作历史流程索引，任务 owner 以本文件和 `team/roles/*.md` 为准。

| 新团队角色 | 启动时/命中任务时读取的既有材料 | 吸收的决策范围；工具与边界 |
| --- | --- | --- |
| `dft-expert` | `skills/agents/dft-parse-agent.md`、`knowledge/standards/merge_rules.md`、`knowledge/standards/test-types.md`（仅识别 DFT 声明）、`knowledge/standards/register-config.md`（仅来源解析） | 保留原文与冲突、零合并、单位/参数/显式时序。不得把 `hardwareInit` 直接解释为已验证的物理通路。 |
| `schematic-expert` | `skills/sch-parse.md`、`knowledge/hardware/schematic-parsing.md`、`knowledge/hardware/closed-loop-model.md`、`knowledge/hardware/bus-topology.md`、`knowledge/hardware/cbit-principles.md`、`skills/agents/cbit-path-finder.md` | 解析物理网络、F/S 路径和默认态；`scripts/gen_paths.py` 等脚本是验证/追踪工具，不取代 SCH-Connect-Map 的证据。 |
| `setup-architect` | `knowledge/hardware/pin-resource-map.md`、`knowledge/hardware/relays.md`、`knowledge/hardware/bus-topology.md`、`knowledge/standards/relay-checklist.md`、`knowledge/standards/site-num-rule.md`、`knowledge/standards/treg.md`、`skills/agents/cbit-agent.md` 及 CBIT 规格文档、`knowledge/sources/index.md` | 建立单一资源/继电器/TReg 目录与全局安全约束；已有 `scripts/gen_cbit_defines.py` / `scripts/gen_path_defines.py` 为定义和核对工具。逐 TM 选哪路源由策略专家定。 |
| `test-strategy-architect` | `knowledge/standards/test-types.md`、`knowledge/standards/toggle-awg-rules.md`、`knowledge/standards/units.md`、`knowledge/standards/register-config.md`；`knowledge/hardware/test-strategy.md`、`knowledge/hardware/voltage-inference.md`；`knowledge/references/func_type_index.md`、`knowledge/references/param_type_index.md` → 匹配的 L1/L3/L4；`skills/agents/power-on-agent.md`、`skills/agents/power-off-agent.md`、`skills/agents/measure-agent.md` | 分类与方法设计、机台资源**选择**、逐阶段电压推导、台阶上/下电、寄存器专属 delta、采样/公式/log。旧 power-on/off 文档和 `scripts/gen_power_sequence.py` 是候选模式/工具，特殊组合须逐阶段验证，不能直接替代计划。只加载当前测试类型匹配的材料。 |
| `ate-implementer` | `knowledge/sources/index.md` → 实际选定板卡文档及机台/SDK 手册；`knowledge/standards/framework.md`、`knowledge/standards/naming.md`、`knowledge/standards/functions-registry.md`、`knowledge/standards/context-management.md`；计划指定的 L4 代码案例 | 决定 API 调用、准确量程枚举、工程落点和可维护实现；旧 relay / power / measure agent 文档可作实现细节参考，不可重新裁定方法。 |
| `rule-reviewer` | `knowledge/standards/rules-registry.md` 的 **active** 区、`knowledge/standards/error-checklist.md`、`knowledge/standards/verification.md`、`knowledge/standards/relay-checklist.md`、`skills/agents/check-agent.md`、`skills/agents/cbit-check-agent.md`；匹配的 `knowledge/experience/` | 查契约一致性、资源/电气路径、代码规则和历史失败模式。draft/经验只作为调查线索，不自动成为阻断规则；新规则需证据、适用范围和审核发布。 |
| `compile-diagnostician` | `skills/agents/compile-agent.md`、`knowledge/standards/verification.md`、`knowledge/standards/context-management.md`、`scripts/run_gates.ps1` 及适用 verify 脚本 | 运行门禁与真实 VS 构建、定位并分类；不把“编译成功”当成电气验证通过。 |

跨角色读规则允许，但**决策 owner 不变**。例如 `units.md` 的 log 单位由策略计划确定、实现者落实、审查者验证；`relay-checklist.md` 的物理路径由 schematic/Setup 证明、策略选用、审查者复核。`rules-agent` / `experience-agent` / `sub-function-agent` 是旧流程的知识提炼机制，不是当前验收 DAG 的并行执行角色；候选规则遵循 `rules-registry.md` 的 draft → 人工审核 → active，不自动写入专家长期规范。

## 3. 测试策略交给实现者的最小契约

每个 TM 的 `test-plan.json` 至少能追溯以下内容；目前通用 JSON Schema 只检查部分字段，**Schema PASS 不等于本表通过**。缺一项应标为未决/阻断并退回，不准由实现者填空。

1. `intent`: DFT 目标、操作点、限值和来源；冲突裁定的作用域。
2. `resourceAllocation`: 每个 force/sense/供电/观测端点选择哪类仪器、具体通道/对象和已验证路由；同时占用、短接与共享节点检查。
3. `powerAndTestPhases`: 各阶段的目标电压/电流、相对电压条件、动作先后、寄存器状态、等待/采样窗；包含正常与异常下电。具体 API/量程枚举可留给实现者。
4. `registerProgram`: 全局初始化引用与逐 TM 寄存器 delta 分开；每一项指向 DFT、`reg_config` 或已批准裁定，冲突不静默择一。
5. `measurementAndLog`: 激励极性、实测通道、同步性、公式（用实测值）、site 维度、log 名/单位/限值及失败处理。
6. `evidenceAndStatus`: 每个关键选择可回指源文件/产物；未决项、假设、禁止交接的条件具名。

策略计划应描述**可执行的电气状态和顺序**，但不需写 `Set(FV,...)` 等 SDK 调用。Setup 契约只证明候选资源和安全边界；策略计划要从中选择本 TM 的组合，不能把“去看 Setup”当作资源选择结论。

## 4. TM600 作为分工验收样例

- `dft-expert` 只交测试意图：PMID—SW 1 A、实测 PMID−SW 电压和电流求 HS RDSON、VBAT/PMID/VDRV 操作点、要求 BST−SW=5 V；不规定 BST/PMID 交替设值的代码。用户已确认这组意图**基本正确**。
- `schematic-expert` 给每个候选源到 PMID、SW、BST 的 F/S 路径、所需继电器和互斥事实；`setup-architect` 验证资源目录和安全约束。通道 5 / 通道 18 的物理差异必须由这些证据确定，不许从对象名猜。
- `test-strategy-architect` 根据 1 A 能力、Setup 通路和黄金案例，选定 PMID—SW 的电流源以及 BST/SW 的供电源，说明它们能否同时工作；列出 BST 与 PMID **逐级交替**上、下电的状态、顺序、寄存器、强制电流、采样、撤流、log 和异常清理。测量时满足 BST−SW 目标差；过渡阶段的约束另按适用规则验证，不能把目标差误写成每个中间动作后的恒等式。
- `ate-implementer` 仅把已签收步骤转换为机台 API；`rule-reviewer` 独立对照计划、连线、代码和适用规则。

**冲突隔离**：`knowledge/hardware/voltage-inference.md` 的 TM600 示例使用 PMID=15 V 和旧寄存器示例，`tm600-normal-highcurrent.cpp` 也是案例操作点；当前 `dft-ir.json` 提取的 TM600 操作点为 PMID=5 V。策略专家必须对账并记录裁定，不能因为文件标题写“规则”就用旧示例覆盖本次 DFT。`skills/agents/power-on-agent.md` / `power-off-agent.md` 的脚本规格也不得跳过这种逐 TM 对账。TM601 原 DFT 产物未列 BST，但用户已提出 BST 条件；“源文件未写”不等于“不需要”，应保留为具名冲突，不允许流到实现层变成默认省略。

## 5. 运行与进化纪律

1. Captain 先读本文件、`team/README.md`、`team/CURRENT_STATUS.md` 与当前验收范围；每位专家再读自己的 `team/roles/*.md` 和上表当前任务匹配的少量原规则。不要全量灌入所有材料。
2. 每次交接写产物路径、现算哈希、来源/裁定、阻断项和下一 owner；下游发现缺项，退回 owner，不通过聊天口头补丁继续写码。
3. 规则冲突先区分：原始数据、当前项目事实、active 规则、黄金案例、历史经验和 draft。保留两侧证据；用户或有授权的 owner 裁定后才更新计划。原始案例不因一次冲突而被静默改写。
4. 可复用的新结论进入对应 `knowledge/standards/` 或角色手册前，按 `rules-registry.md` 审核并说明适用范围；一次 TM 的电压/继电器实例先留在 run artifact。被推翻的结论要标 superseded/retired，不能两份并存都叫权威。
5. 本文件是路由规则，不表示当前运行中的 DSH 会话已自动重载提示词或旧计划已修正。新/重领任务必须显式复读；当前 TM600/601 计划仍需策略专家修订与独立复核，不能因这份文档存在就放行。
