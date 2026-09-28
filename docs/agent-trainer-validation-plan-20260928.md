# ATE Trainer 系统验证方案（讨论议题合并总结，2026-09-28）

状态：待用户 review。本方案合并近期确定的四个验证维度：训练 → 发布 → 工程、单 Agent → 工作流、轻量化冒烟 → 真实业务，以及按 Agent 配置执行。本文只定义验证顺序、证据和通过条件；不改变已确认的原型交互。

## 1. 验证目标

验证 ATE Trainer 是否具备可复用模板能力，而不是一次性验证两个固定专家：

- 可以创建、训练、优化 Agent，并为每次优化形成独立版本。
- 可以把多个 Agent 编排成工作流，调整顺序、替换步骤并重新运行。
- 可以把经过验证的 Agent 和工作流冻结、发布，再由工程模式调用固定版本。
- 新建 Agent 与已有 Agent 使用同一套模型、会话、资产和版本机制；能力由配置和执行适配器决定，不能由固定 Agent ID 决定。

本轮采用“小范围、分层验证”：所有 Agent 先做最小冒烟；真实业务使用 TM109，覆盖当前已有业务材料的原理图专家和 DFT 专家；首个用户工作流额外加入一个由 Trainer 新建的 Agent，用于验证动态编排，但该新 Agent 在没有独立业务合同前只参加工作流 smoke，不虚构 TM109 业务产物。

## 2. 两条验证路径

### 2.1 生命周期路径：训练 → 发布 → 工程

1. 训练模式创建 Agent 和工作流，形成候选版本。
2. 对候选 Agent 和工作流完成规定的最小冒烟及必要的业务验证。
3. 发布模式冻结精确的 Agent revision、工作流 revision、资产和 SHA-256 证据。
4. 工程模式只能读取并调用已发布版本；未发布的 Agent 或工作流不可用。
5. 修改训练草稿后，旧发布版本继续使用原快照；新版本只有重新验证并发布后才可用。

本轮的发布/工程回放只验证轻量 `SMOKE_ONLY` 版本。`BUSINESS_ONLY` 真实业务结果留在训练证据中，除非另有明确的业务 release decision。

### 2.2 纵向能力路径：Agent → 工作流

#### 阶段 A：单 Agent 最小冒烟

每个参与验证的 Agent 独立运行：

- 新鲜 DSH child。
- 无工具、无私有项目材料。
- 精确提示：`1+2等于几，把答案写在JSON里`。
- 结构化结果必须是数字 `answer: 3`。

这一阶段只证明 Agent 可创建、可打开原生 Trainer 会话、可执行、可记录和可版本化，不证明业务能力。

#### 阶段 A1：Agent 优化候选验证

本轮将“训练”的最小可验证定义定为：通过 Trainer 修改 Agent 的可执行内容，保存为新的 candidate revision，重新运行该 revision，并用运行证据证明行为已经按新定义变化。单纯修改页面文字但没有保存、重新执行和新证据，不算训练完成。

优化必须形成一个新的 Agent candidate revision，而不是覆盖基线：

1. `Agent v1` 先按最小合约执行 `1+2`，结构化结果为数字 `3`，保存为 baseline evidence。
2. 在 Trainer 会话中修改候选的指令、Skill、脚本或输入输出合同，形成 `Agent v2 candidate`。验证样例可以改为 `2+3`，期望结构化结果为数字 `5`。
3. 以独立的 `agent-optimization` run 执行 v2，记录变更摘要、candidate revision、输入、期望结果、实际结果和 receipt。这个 run 不覆盖 v1，也不冒充 `SMOKE_ONLY`。
4. 如果 Agent 的职责仍然是通用算术能力，v2 还要回归原来的 `1+2 → 3`；如果职责有意改成新的专用合同，则必须同步更新合同、测试样例和能力说明，不能只改名称。
5. v2 通过后，才允许把它加入工作流候选；发布时冻结 v2 的完整配置和摘要。v1 的运行和已发布版本保持不变。

这里的 `2+3 → 5` 是验证 Agent 优化是否真正改变了可执行行为的示例。active `SMOKE_ONLY` 仍固定使用 `1+2 → 3`，因为它验证的是平台调用、阶段交接和发布回放，不随某个 Agent 的候选优化而改变。

#### 阶段 B：单 Agent 真实业务冒烟

原理图专家和 DFT 专家分别执行一个小而完整的真实业务样本，先隔离验证 Agent 自身：

- 输入材料和依赖可加载。
- Skill、脚本和工具权限按 Agent 快照生效。
- 输出合同、业务门禁和错误停止行为正确。
- 运行证据包含 runId、Agent revision、输入/输出和哈希。

DFT 的业务样本使用现有 DFT 真实执行流程。DFT 所需的上游输入先使用已核验的固定样本，避免把原理图 Agent 的问题混入 DFT 单体验证。

#### 阶段 C：工作流轻量冒烟

创建首个三 Agent 候选工作流：

```text
原理图专家 → Trainer 新建 Agent（custom-agent-01）→ DFT 专家
```

三个 Agent 都使用自己的最小 `1+2` 流程，检查：

- 步骤顺序和重复步骤。
- Agent 之间的输入绑定和上游证据哈希。
- 任一步骤失败时停止后续步骤。
- 工作流 revision、运行记录和原生 Trainer 会话绑定正确。

该阶段属于用户工作流冒烟，不替代 `team/ptc/ptc_stage_registry.json` 规定的 active 八专家 smoke contract。完整 SMOKE_ONLY 发布回放仍必须满足八个 registry slots、reviewer 双 review、Evolution auxiliary 和 `businessGatePassed:false`。

#### 阶段 D：真实业务工作流

在原理图专家和 DFT 专家的 TM109 单体业务冒烟通过后，执行 TM109 真实业务工作流：

```text
原理图专家 → DFT 专家
```

此时 DFT 必须消费本次原理图专家实际生成的机器产物，并验证串行交接、输入合同、门禁和失败停止。这样可以把 Agent 自身问题与多 Agent 编排问题分开定位。

TM109 必须至少产出以下文件，并在训练运行证据中生成一份机器可读的哈希校验记录表 `evidence/tm109-output-hashes.json`：

- `project/DALI/Output_Global_Material/dft/TM109/dft-conditions.yaml`
- `project/DALI/Output_Global_Material/dft/TM109/dft-meta.json`
- `project/DALI/Output_Global_Material/dft/TM109/dft-semantic-review.json`

哈希记录表至少包含 TM 编号、文件角色、相对路径、字节数、SHA-256、生成 Agent revision、来源输入 SHA-256 和校验状态。YAML/JSON 文件缺失、解析失败、哈希不匹配或语义 review 不通过时，TM109 工作流必须阻断。

## 3. 新建 Agent 等价性验证

系统需要支持“复制为新 Agent”或使用完整配置创建新 Agent：

- 新 Agent 有独立的 `agentId`、revision、训练历史、session 和运行目录。
- 它可以复制 DFT 的职责、内部流程、Skill、脚本、输入输出合同、依赖、权限和 `ptc-dft` 执行适配器。
- 它与原 DFT Agent 的能力配置可以等价，但后续优化互不影响。
- 只读 capability bundle 可以复用，但训练草稿、revision、Skill/脚本覆盖、运行记录和发布快照必须深度隔离。
- 工作流可以用新 Agent 替换原 DFT 步骤，替换前检查输入输出合同、能力和依赖兼容性。
- 执行器按 Agent 快照中的 capability/adapter 加载流程，不能通过 `profileId === 'ptc-dft-expert'` 赋予能力。

验收用例：复制 DFT 为一个新 ID，用相同业务输入分别运行两个 Agent；确认进入同一 DFT 适配器、产出合同兼容，且两者的运行证据和后续版本完全独立。

当前生产代码仍有固定 `ptc-dft-expert` 判断，因此“新 Agent 可替换 DFT”是本轮实现必须完成并验收的重构项，不把原型中的静态演示视为已实现。

## 4. 发布与工程隔离验证

现有 SMOKE 发布路径已有冻结快照、发布 ID/摘要绑定、独立 `publish/runs/<runId>/` 和完整性校验。本轮不重复安排大规模隔离测试，只保留一项动态接入回归：

1. 发布 Agent/工作流 revision A。
2. 在训练模式修改为 revision B。
3. 工程模式继续运行 A，并确认发布包摘要、Agent 绑定和工作流顺序不变。
4. 只有重新验证并发布 B 后，工程模式才显示 B。
5. 工程模式不能写候选、重排步骤、替换 Agent 或修改发布快照。

如果发布包依赖的训练证据或文件发生变化，工程启动前必须阻断，而不能静默读取新内容。

## 5. 原型交互冻结基线

验证实现不得大改当前原型的页面结构和入口。以下交互必须保留：

- 训练、发布、工程三种产品模式。
- `SMOKE_ONLY` / `BUSINESS_ONLY` 切换。
- Agent 和工作流列表、空项目状态、新建入口。
- 工作流步骤选择、排序、重复和删除。
- 运行记录的步骤状态、输入/输出、Skill + 脚本三个页签。
- 从当前 Agent、当前工作流和运行记录打开 Trainer 原生会话。
- 工程模式只显示已发布工作流及其绑定 Agent，没有发布内容时显示空状态。

视觉上继续使用当前已确认的轻量列表样式，不恢复灰色默认按钮框。

## 6. 证据与通过条件

每个验证阶段至少保存：

- `runId`、`agentId`、`agentRevision`、`workflowId`、`workflowRevision`。
- 执行模式、session 绑定、输入/输出合同和上游证据哈希。
- Agent/工作流配置快照和 SHA-256。
- 成功、阻断、停止和失败原因。
- 发布版本的 manifest、文件列表和 bundle digest。

通过条件是：单体 Agent 失败可以独立定位；工作流失败可以定位到交接或编排；发布后工程运行只消费固定快照；新建 Agent 能在不改执行器白名单的情况下复用 DFT 能力；所有 smoke 结果保持 `SMOKE_ONLY`、`answer:3` 和 `businessGatePassed:false`。

## 7. 本轮明确不做

- 不一次性训练所有 Agent 的真实业务流程。
- 不把单体 Agent 冒烟或两 Agent 工作流冒烟当成半导体业务认证。
- 不在 smoke 路径调用旧 DFT/Schematic gate、parser、业务脚本或归档流程。
- 不改变已确认原型的主要交互结构。
- 不在没有新业务 release decision 的情况下发布 `BUSINESS_ONLY` 版本。

## 8. Review 验收矩阵

| 对象 | 前置条件 | 模式 | 核心检查 | 预期结果 |
| --- | --- | --- | --- | --- |
| 基础 Agent | 已创建 Agent 候选 | `SMOKE_ONLY` | fresh child、无工具、`answer:3`、独立记录 | Agent 冒烟通过 |
| Agent 优化候选 | 已有 Agent v1 baseline | `agent-optimization` | v1 `1+2→3`、v2 `2+3→5`、变更摘要、回归和独立 receipt | v2 行为改变且 v1 不受影响 |
| 复制/自定义 Agent | 配置与 DFT 能力合同一致 | `SMOKE_ONLY` | 新 ID、同 adapter、独立 revision 和 run | 可独立运行，不改原 DFT |
| 多 Agent 工作流 | 至少两个已通过 smoke 的 Agent | `SMOKE_ONLY` | 顺序、交接哈希、失败停止 | 工作流冒烟通过 |
| 首个三 Agent 工作流 | 原理图、custom-agent-01、DFT 均已完成 smoke | `SMOKE_ONLY` | `原理图→custom-agent-01→DFT` 顺序、三份 child receipt、失败停止 | 动态新增 Agent 可编排 |
| 原理图单 Agent | 固定真实业务样本 | `BUSINESS_ONLY` | 输入、脚本、产物、门禁、证据 | 单体业务通过或明确阻断 |
| DFT 单 Agent | TM109 固定真实 DFT 样本 | `BUSINESS_ONLY` | 三个 DFT 输出、hash record、门禁、证据 | 单体业务通过或明确阻断 |
| 原理图 → DFT（TM109） | 两个单体业务均通过 | `BUSINESS_ONLY` | 消费本次上游产物、三个输出文件、哈希表、串行交接、失败停止 | 真实工作流通过或定位到编排问题 |
| DFT → 复制 Agent 替换 | 复制 Agent 已完成等价配置校验 | `BUSINESS_ONLY` | 工作流替换后必要 TM109 产物字段/文件角色/哈希记录结构一致，Agent ID 和 revision 独立 | 替换成功，原 DFT 不受影响 |
| 发布 → 工程 | smoke 工作流已冻结发布 | `SMOKE_ONLY` | releaseId/digest 固定、运行目录独立、草稿不泄漏 | 工程只调用发布快照 |

每一行都必须留下 `runId`、revision、模式、状态、失败原因和对应的输入/输出或发布摘要证据，才能在 review 中勾选通过。
