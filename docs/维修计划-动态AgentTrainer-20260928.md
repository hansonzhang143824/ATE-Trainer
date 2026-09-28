# 动态 Agent Trainer 修复计划

日期：2026-09-28  
目标：把 DSH PTC 工作台恢复为“空项目可配置、同一工作流双模式、发布冻结、工程只读”的稳定架构，并用用户创建的原理图专家 + DFT 专家完成端到端验证。

## 1. 目标边界

正式项目首次打开时不预置 Agent，也不预置工作流。Agent、Skill、脚本、输入输出合同和工作流都由用户在训练模式中创建或导入。

`Synthetic Role 1~7` 与 `Synthetic Producer → Consumer` 只保留为隔离的自动化回归 fixture，不进入正式项目状态，不显示在用户的默认 Agent/工作流列表中。

同一份用户工作流定义保留两个执行适配器；适配器的证据边界不能互相冒充：

- `SMOKE_ONLY`：遵守 `AGENTS.md` 的 active smoke contract。框架验收仍按 registry 顺序派发八个新鲜、无工具、无私有材料的子任务，使用精确提示 `1+2等于几，把答案写在JSON里`，校验数字 `answer: 3`，并保持 `businessGatePassed: false`。用户工作流中的 Agent 选择和连线只作为框架编排映射与绑定校验展示，不把两专家烟测写成真实业务证明。
- `BUSINESS_ONLY`：加载当前 Agent 的真实指令、Skill、脚本和项目材料，产生业务产物并执行业务门禁。

模式切换只改变步骤执行适配器和 run kind；SMOKE_ONLY 只能写入 `Training_Materials/runs/<runId>/` 或 `publish/runs/<runId>/` 的 smoke 证据，BUSINESS_ONLY 只能写入 `Training_Materials/runs/<runId>/` 的业务证据。两者不复制工作流、不复用旧运行结果，也不让 smoke 按钮冒充真实业务。

## 2. 最终用户流程

```text
空项目
  → 新建原理图专家 / DFT 专家
  → 新建 Offline-Coding-Flow
  → 选择并排序：原理图专家 → DFT 专家
  → 从 Agent 或工作流入口打开 DSH 原生 Trainer 会话
  → 在会话中训练当前专家/工作流，诊断运行并发起修改后复测
  → SMOKE_ONLY 框架验收（八专家 contract，非半导体认证）
  → BUSINESS_ONLY 业务训练（原理图 → DFT）
  → 查看运行输入/输出与 Skill/脚本
  → （单独业务 release decision 前）冻结候选证据
  → 发布/工程模式回放 SMOKE_ONLY 版本
```

业务模式必须先执行 `project_config.json` 门禁；原理图专家完成机器产物、PinIndex 和 CBIT 冲突检查后，才允许启动 DFT 专家。Pin 无法确认、输入绑定缺失或 CBIT 冲突时，当前步骤停止并保留证据。BUSINESS_ONLY 的训练产物在单独的业务训练和 release decision 前不具备发布资格。

## 3. 分阶段实现

### P0：原型审阅门

- 交付：[agent-trainer-repair-prototype.html](prototypes/agent-trainer-repair-prototype.html)。
- 原型展示两种状态：用户创建的两个 Agent，以及可被清空的空项目概念；同时明确 active smoke 的八专家 contract 与两专家 BUSINESS_ONLY 图的边界。
- 原型必须能点击切换训练/发布/工程模式、SMOKE_ONLY/BUSINESS_ONLY、步骤、运行记录三页，并保留按 Agent、按工作流和按运行记录打开原生 Trainer 会话的入口。
- 本阶段不改生产运行逻辑；用户确认原型后才进入 P1。

### P1：项目和资产模型

动态 Agent manifest、复制边界、能力/执行适配器和 workflow step revision 的开发顺序记录在：[ATE Trainer 开发计划](agent-trainer-development-plan-20260928.md)。

- 新增项目 registry：`agents[]`、`workflows[]`、`skills[]`、`tools[]`、`revisions[]`。
- 正式 registry 初始为空；测试 fixture 通过显式 fixture loader 注入。
- Agent/工作流 ID、版本、输入输出 Schema、Skill/脚本声明全部配置化。
- 保留旧 smoke 和历史发布目录为只读兼容数据。

退出条件：新建第九个 Agent 不需要修改 JavaScript 白名单；空项目可正常打开；历史 smoke 记录不出现在正式项目列表中。

### P2：统一执行器和模式适配器

本阶段必须移除业务执行对 `ptc-dft-expert` 固定 ID 的依赖，改为按 Agent manifest 的 capability 和 `executionAdapter` 解析；工作流替换必须在输入输出合同、依赖和权限兼容检查通过后执行。

- 建立统一 framework runner，接收同一份 workflow revision。
- `SmokeAdapter` 按 active registry 派发八个 fresh `1+2` 子任务；`BusinessAdapter` 读取训练材料并执行真实脚本/门禁。两专家图只作为用户业务图，不能替换八专家 smoke contract。
- 真实交接使用静态 JSON Pointer input binding，保存实际 payload、来源产物和哈希。
- Agent、工作流和运行详情的训练入口必须调用同一个原生会话服务：服务端先创建/绑定 session，再由宿主打开可见的 DSH 原生会话；绑定至少包含 `projectId`、`targetKind`、`targetId`、`candidateRevision`、`runId`、`executionMode`、`scope` 和 `schemaVersion`。Trainer 会话使用显式 `agent-trainer` preset，不能静默回退到 `standard`/`code`；普通 framework child 使用 `framework-worker`，两者身份和工作目录分离。
- Trainer 会话支持“训练当前专家”“训练当前工作流”“先诊断，不修改”“修改并复测”“运行工作流”“暂停/继续/停止”等命令；每条请求带幂等 `requestId`，真实结果必须返回 `runId`、event 和 receipt。无法嵌入时要明确提示已在新的原生会话中打开，不能用页面内静态聊天或定时器冒充原生会话。
- 业务 `INPUT_SYNC` 改为严格串行：schematic 完成并通过门禁后再启动 DFT；smoke registry 的阶段顺序仍由 `team/ptc/ptc_stage_registry.json` 控制。
- `BusinessAdapter` 只能通过当前 `/api/ptc-control/business/*` 的显式 profile/allowlist 进入；必须拒绝直接导入或调用 `team/ptc/native-control-plane/archive/DFT-SCHEMATIC-LEGACY-20260923/` 中的历史 flow、gate、parser 和 check。
- 不允许旧 `/training-runs/execute`、旧 smoke release 或历史 receipt 替代新运行。

退出条件：同一 workflow revision 可分别创建两个 run，用户图显示相同的 schematic → DFT 连线；SMOKE run 记录八专家 contract 与 `businessGatePassed:false`，BUSINESS run 记录真实输入和产物，两个 run 的证据根目录和执行内容不同；缺字段、Schema 错误、超时和模型错误均明确阻断。

### P3：冻结、发布和工程只读

- 冻结包包含 Agent 指令、memory、Skill、脚本、合同、工具注册、工作流和全部依赖 SHA-256。
- 发布包可在没有训练目录的隔离目录中运行。
- 发布模式只审核和激活，不修改候选。
- 工程模式只能读取活动发布包；工作流选择范围只包含已发布工作流，选中工作流后只能看到并运行该发布版本绑定的 Agent、顺序和资产。没有已发布工作流时工程模式显示空状态；没有已发布 Agent 时不提供任何 Agent 入口。任何写入候选、Skill 或脚本的请求都拒绝并留下事件。

退出条件：修改训练草稿不会影响旧发布运行；激活新版本后才产生变化；篡改冻结文件或缺依赖会在工程启动前失败。

### P4：白色 Trainer 面板和运行记录

- 恢复 V1 白色信息架构：左侧先有 `Trainer` 项目入口，再分组显示当前项目实际登记的 Agent、工作流和运行记录；空项目显示空状态和新建按钮。
- 工作流编辑器支持选择、排序、重复步骤和模式切换。
- 运行详情增加三个页签：步骤状态、输入/输出、Skill + 脚本。
- Trainer 面板必须提供“打开原生会话”按钮；切换 Agent、工作流或历史运行时更新精确绑定，不猜测最新 run，不复用其他目标的 session。工程/发布会话只读，工程模式可观察和控制运行但不能 apply changes。
- 工程模式的工作流与 Agent 选择必须由活动发布清单驱动；不能从训练候选、未发布草稿或历史运行记录回填可用项。工作流与其 Agent 绑定在发布版本中固定，工程模式不允许重排、增删步骤或替换 Agent。
- 选择某个 Agent 时，所有绑定资产都显示；本次实际使用的条目标绿色，未使用条目使用中性颜色。
- 发布/工程模式隐藏编辑入口并显示只读原因。
- 模式和运行记录要明确显示 `framework-smoke`（八专家 contract）与 `workflow-business`（原理图 → DFT）scope，避免两专家业务图被误读为完整 active smoke。

退出条件：Computer Use 能真实点击创建、编排、切换模式、运行、查看两页详情、冻结、发布和工程复跑。

### P5：验证和交付

本阶段的分层验证顺序、TM109 输出合同、Agent 可替换性、发布隔离回归和原型交互冻结基线记录在：[ATE Trainer 验证方案](agent-trainer-validation-plan-20260928.md)；分阶段开发与 Git checkpoint 记录在：[ATE Trainer 开发计划](agent-trainer-development-plan-20260928.md)。先完成单 Agent 最小冒烟，再完成原理图/DFT 单体业务冒烟，最后执行真实工作流；不把单体结果与工作流编排问题耦合。

- 自动测试：空项目、动态新增 Agent、任意顺序、重复 Agent、两种模式、输入绑定失败、Skill/脚本版本变化、冻结完整性、工程只读、重启和历史记录；还要覆盖 Agent/Trainer/工作流原生会话创建与恢复、显式 preset、绑定字段、旧 session 拒绝、会话切换不串线、真实发送/运行事件和 exact runId 诊断，以及工程模式只显示已发布工作流和其固定 Agent、未发布时为空、不能改编排。
- 真实 UI：只使用用户创建的原理图专家 + DFT 专家和 Offline-Coding-Flow；先完成八专家 SMOKE_ONLY 框架验收，再完成两专家 BUSINESS_ONLY 训练和证据检查。默认发布/工程回放只验收 SMOKE_ONLY；BUSINESS_ONLY 只有在另行明确业务 release decision 后才进入发布流程。
- 每个阶段单独 Git checkpoint；只提交本任务文件，保留用户已有未提交修改。

## 4. 并行会话分工

新会话统一读取本计划和交接文档，并使用 `gpt-6-astra`、`ultra`（不支持时才用 `xhigh`）。并行工作边界如下：

| 轨道 | 负责范围 | 不可修改 |
| --- | --- | --- |
| A | 项目 registry、空状态、Agent/工作流资产模型 | UI bundle、真实业务脚本 |
| B | 统一 runner、SMOKE/BUSINESS adapter、schematic→DFT 串行交接 | 页面布局 |
| C | 冻结包、发布激活、工程只读和完整性检查 | 训练执行器核心 |
| D | 白色 Trainer UI、运行详情三页、Computer Use 验收 | 后端资产格式 |

主会话负责接口契约、合并、受控重启和最终端到端验收。任何轨道完成后先写测试和报告，再合并；不直接覆盖其他轨道的文件。

## 5. Git 和回滚纪律

每个阶段开始前创建 checkpoint，每个阶段结束后提交独立 commit。禁止把用户已有的业务材料、训练运行和无关未跟踪文件混入提交。生产 bundle、计划、原型和交接文档必须能通过 Git 回滚。

## 6. 验收口径

只有以下证据同时存在才算交付：

1. 空项目可以由用户创建 Agent 和工作流。
2. active `SMOKE_ONLY` 满足八专家 contract：fresh child、无工具/私有材料、精确提示、`answer:3`、reviewer 双 review、evolution 辅助任务、`businessGatePassed:false`，并写入规定目录。
3. 同一用户工作流可创建 `BUSINESS_ONLY` run，原理图专家先于 DFT 专家，真实交接包含机器产物和哈希。
4. 运行记录可按 Agent 查看输入/输出和全部 Skill/脚本，本次使用项明确标绿色。
5. SMOKE 发布包自包含且工程模式不能修改它；BUSINESS_ONLY 在单独 release decision 前不得冒充已发布业务版本。
6. 真实 Computer Use 点击完成空项目配置、两专家 BUSINESS_ONLY 训练、SMOKE 发布和 SMOKE 工程回放。

单独的 `answer=3`、后台 API 返回 200、或静态原型可点击，都不能替代上述验收。

## 7. 当前明确不做的事

- 不把 Synthetic fixture 重新作为正式默认 Agent。
- 不删除历史 smoke、业务运行或归档材料。
- 不在 smoke 路径调用真实 DFT/原理图脚本。
- 不把一次业务 run 的产物当成已完成的 UI、发布和工程只读验收。
- 不在用户确认原型前接线生产按钮。
