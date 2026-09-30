# Agent Trainer 原生会话替代开发计划

版本：2026-09-30  
适用范围：Agent Trainer 的 Agent 训练、工作流训练、优化、运行、冻结与发布入口  
实施前 Git 回滚点：`dea25de chore: checkpoint before native session replacement`

## 1. 目标和完成定义

本版本把真实 DSH 原生会话设为唯一训练聊天入口。用户在白色 Agent Trainer 页面选择 Agent 或工作流后，点击“打开原生会话”，系统把用户带到 DSH 的原生会话窗口；用户在该原生窗口中输入训练指令，Trainer 通过真实工具读取上下文、修改候选、校验、运行并返回原生消息和工具事件。

追加需求（2026-09-30）：DSH 显示直接可点击的“打开 ATE Trainer”入口，替代原先需要先展开的 PTC 面板。用户点击一次即可进入 Trainer 工作台；选择 Agent 或工作流后，仍由对应按钮打开 DSH 原生训练会话。该入口调整加入本计划，原有开发目标和 Gate 0–6 验收要求保持不变。

白色页面保留目标选择、候选 revision、运行结果、冻结/发布和错误状态等工作台功能。它不再提供一个看起来像聊天窗口的替代输入框，也不直接调用 `session.prompt`、`session.history` 来模拟训练对话。白色页面只负责发送一次原生会话启动请求，并显示跳转状态和可核对的 ID。

“SMOKE_ONLY”与用户的业务优化训练必须分开：

- `SMOKE_ONLY` 继续遵守 `AGENTS.md` 的固定合同：每个新 child 收到 `1+2等于几，把答案写在JSON里`，结果为数字 `answer: 3`，`businessGatePassed: false`。它只证明模型调用、阶段交接和发布回放。
- 例如把 `agent-T2` 改为计算 `11*21` 并得到 `231`，属于单独的候选优化/训练运行，使用 `agent-optimization` 或等价明确模式，不能伪装成 smoke，也不能写入 smoke 发布证据。

完成条件是 Agent 和工作流两条路径都满足“按钮点击 → DSH 原生窗口 → 原生输入 → 原生工具事件/回复 → 服务端候选或运行证据”的闭环，并且刷新、重开、切换目标、宿主不可用和重复请求都有确定结果。

## 2. 现状基线和主要问题

实施前已创建回滚提交 `dea25de`。当前原型页仍有以下旧链路：

1. `docs/prototypes/agent-trainer-repair-prototype.html` 直接调用 `/api/ptc-control/trainer/open-native-session`，这只创建后端绑定，不能让 DSH 窗口可见地打开该会话。
2. 白色页面自身持有 textarea，并通过 `session.history`/`session.prompt` 轮询和拼接文本。这是页面内模拟聊天，不是原生 DSH 会话。
3. DSH 宿主已有可复用能力：`plugins/dsh-ptc-control-plane/lib/client.js` 和 `panel.js` 的桥接监听会调用 `openPtcNativeSession`，最终执行 `scope.sessions.open(sessionId)`；它还支持按目标和 preset 复用本地会话。
4. `trainer-service.js` 的 `openNativeSession` 只创建会话和绑定，不能代替宿主窗口切换。

因此本次改造的核心是恢复并收紧“白页请求 → DSH 宿主 → `scope.sessions.open` → 原生窗口”的链路，并删除白页聊天替代路径。

## 3. 目标架构和边界

### 3.1 组件职责

| 组件 | 职责 | 不允许承担的职责 |
|---|---|---|
| 白色 Agent Trainer 页 | 选择目标、显示候选/运行状态，发起带 nonce 的 native-session 请求 | 伪造聊天、直接轮询或提交原生消息 |
| DSH ATE Trainer 入口 `panel.js`/`client.js` | 直接打开工作台；校验来源和请求，创建或复用会话，绑定目标，调用 `scope.sessions.open`，回传结果 | 修改候选内容、替白页生成训练结论 |
| `openTrainerNativeSession` | 按 project、mode、target、revision、run、preset 复用或创建真实 DSH session，核对服务端绑定并打开窗口 | 通过白页 iframe 或离线适配器冒充原生窗口 |
| `trainer-service.js` | 创建绑定、提供 Trainer 工具、写入 revision/run 证据 | 负责可见窗口跳转 |
| DSH 原生会话 | 承载用户输入、模型流式回复、Trainer 工具调用及工具结果 | 使用白页摘要作为训练证据 |

### 3.2 请求/响应合同

白页发送 `dsh-agent-trainer-open-session`，至少包含：

```json
{
  "bridgeId": "uuid",
  "nonce": "uuid",
  "projectId": "agent-trainer",
  "targetKind": "agent|workflow",
  "targetId": "agent-T2",
  "candidateRevision": "revision-...",
  "selectedRunId": null,
  "presetId": "agent-trainer",
  "mode": "training|published|engineering",
  "source": "agent-trainer-white-shell"
}
```

这里的 mode 表示工作台和会话权限模式；算术 smoke 与候选优化的执行范围另行记录，不通过混用会话 mode 伪装 smoke。

宿主先通过 `session-workspace` 核对 revision。新会话由 `open-native-session` 在服务端创建、挂入 DSH 工作区并完成 Trainer 绑定，客户端刷新会话列表；复用会话先读取服务端绑定，再以当前 bindingRevision 重新核对绑定。两条路径都在真实 `scope.sessions.open` 选中目标会话后返回 `dsh-agent-trainer-session-result`，包含 `bridgeId`、`nonce`、`sessionId`、`targetKind`、`targetId`、`candidateRevision`、`presetId`、`openedAt` 和 `reused`。失败返回稳定错误码，例如 `HOST_UNAVAILABLE`、`ORIGIN_REJECTED`、`TARGET_MISMATCH`、`STALE_SESSION`、`OPEN_FAILED`。

重复 nonce 必须幂等；同一目标、revision、preset 可以复用同一 session；目标、revision 或 preset 不匹配时必须拒绝旧 session 并重新创建或要求用户重新打开。

### 3.3 通讯顺序

1. 用户在 DSH 直接点击“打开 ATE Trainer”进入工作台，保留 opener、BroadcastChannel、宿主标识和允许的 host origin；无需展开 PTC 面板。
2. 用户点击 Agent 或工作流的“打开原生会话”。白页生成 nonce，仅发送 bridge 请求并显示“正在打开 DSH 原生会话”。
3. 宿主校验 origin、project、target、revision 和 preset，调用 `openTrainerNativeSession`，确保真实会话已挂入 DSH 工作区、Trainer 绑定完成且客户端能查到会话。
4. 宿主完成真实 `scope.sessions.open(sessionId)`，再通过桥接返回 session ID 和绑定信息。
5. DSH 原生会话显示标题、模型和 Trainer 工具。用户在这里输入训练指令；工具事件和 assistant 流式消息成为聊天证据。
6. 白页在用户返回后读取服务端的 revision/run/publish 证据，供复核和发布按钮使用。

## 4. 分阶段实施计划

### D0：基线、合同和回滚

- 保留回滚提交 `dea25de`，记录当前 HEAD、原型文件、宿主桥接文件和运行环境。
- 新增本计划和点击式验收计划；计划文档先于代码修改提交。
- 冻结错误码、请求字段、允许 origin、目标绑定规则和 smoke/optimization 模式边界。
- 退出条件：文档提交成功，`git show dea25de` 可读，工作区中与本次无关的生成物未被加入提交。

### D1：恢复并加固宿主桥接

- 将 DSH 的 PTC 展开面板替换为“打开 ATE Trainer”直达入口；保留宿主处理原生会话启动请求的能力。
- 复用 `client.js`/`panel.js` 的 `postMessage`、BroadcastChannel、localStorage fallback 监听。
- 将 `openPtcNativeSession` 的结果包装成稳定响应，加入 nonce 幂等、origin allowlist、目标/preset/revision 校验。
- 确认调用顺序严格为：核对 workspace/revision → 创建并挂入工作区/复用 → 服务端绑定 → 刷新客户端会话列表 → 等待本地 binding → `scope.sessions.open` → result。
- 明确 fallback 只用于消息传输容错，不能把白页 session 当成原生窗口。
- 退出条件：宿主日志能看到 bridge request、`scope.sessions.open` 和 result，重复请求不会创建重复会话。

### D2：白页改为 launcher/status shell

- 删除或禁用白页训练 textarea、发送按钮、`session.prompt`、`session.history` 轮询和本地 transcript 合成。
- Agent 和 workflow 两个按钮使用同一 bridge contract，但 targetKind/targetId 不同。
- 成功后显示“已打开 DSH 原生会话”和 session ID；失败显示错误码、人工处理提示和重试按钮。
- 保留候选、运行、冻结、发布等页面操作；页面显示的 assistant 摘要只能来自已落盘原生事件或运行证据。
- 退出条件：直接访问 standalone localhost 且没有 DSH host 时明确阻断，不回退为 white-native 离线聊天。

### D3：生命周期、恢复和目标切换

- 以 `projectId + targetKind + targetId + presetId` 维护 session key，记录 session ID、candidate revision 和最近 bridge nonce。
- 白页刷新、DSH 页面重开或宿主重启后，先校验 session binding 和 revision，再复用或创建。
- 从 Agent 切到 workflow、从旧 revision 切到新 revision 时拒绝旧绑定，防止串聊。
- session 失效、preset 不符或绑定不存在时给出确定错误，不把旧消息显示给新目标。
- 退出条件：刷新/重开/切换/过期四类测试均能得到可解释的 session 结果。

### D4：原生 Agent 训练闭环

- 训练模式打开 Agent 原生会话；原生工具可读取 `trainer_context`、`trainer_assets`、`trainer_runs`。
- 优化指令必须在原生窗口输入，工具调用必须产生候选 revision/changeSet，校验后才允许 run。
- 训练结果必须有 session ID、target ID、旧/新 revision、changeSet、run ID 和 JSON output。
- 退出条件：旧 revision 和新 revision 可分别运行，优化行为变化可被证明。

### D5：原生工作流训练闭环

- 白页创建/选择工作流、添加和排序 Agent；“在 Trainer 中训练当前工作流”发送 workflow bridge 请求。
- 原生窗口中可读取 workflow context，修改顺序或步骤映射，调用 apply/validate/run 工具。
- 运行证据必须逐步记录 stepId、agentId、revision、输入、输出和 handoff；所有 child 都是 fresh DSH model child。
- 退出条件：Agent 与 workflow 两个 native session 均可用，顺序变更在新 revision/run 中可见。

### D6：smoke、发布和工程隔离

- 运行现有八专家 `SMOKE_ONLY` 合同，固定输入和 `answer:3`；不调用历史 DFT gate、schematic parser 或业务 gate。
- 冻结八个 profile snapshot 和完整 orchestration evidence 到 `publish/versions/<releaseId>/`。
- 发布回放写入新的 `publish/runs/<runId>/`，仍派发 fresh arithmetic children。
- 优化运行和业务模式证据继续写入 `Training_Materials/runs/<runId>/`，不能污染 smoke release。
- 退出条件：未发布候选不会影响工程回放；每个结果带 `SMOKE_ONLY` 和 `businessGatePassed:false`。

### D7：可观测性、测试和回滚演练

- 为每次 bridge 写入 `bridgeId/nonce/requestAt/responseAt/channel/hostOrigin/sessionId/scope.sessions.open` 证据。
- 增加重复 nonce、origin 错误、无宿主、过期 session、wrong target、wrong preset、重复点击和宿主断开测试。
- 运行现有自动测试作为后端回归，但最终门槛必须由 CUA 实际点击和原生输入完成。
- 在临时分支执行一次回滚到 `dea25de` 的演练，确认可恢复旧白页和宿主代码。
- 退出条件：所有 P0/P1 项通过，失败项有可复现日志和修复提交。

### D8：原生模型路由闭环（追加）

- 原生会话创建时写入期望 `nativeModelSelection`，并在真实 DSH 输入后从 runtime ledger 核对实际 provider/model。
- 如果 DSH 宿主当前模型覆盖了绑定要求，入口必须提供明确的模型切换路径；在实际原生输入复验前不得声称 DeepSeek 已生效。
- 退出条件：Agent、工作流和发布回放至少各有一条原生请求显示实际 `deepseek-official/deepseek-v4-flash`，或者文档明确记录用户选择模型的必要步骤和原因。

## 5. 风险和处置

| 风险 | 处理 |
|---|---|
| standalone 页面没有 `sessionServices` | 显示 `HOST_UNAVAILABLE`，要求从 DSH“打开 ATE Trainer”入口打开，不使用离线聊天替代 |
| 只创建后端 session 未切换 UI | 把 `scope.sessions.open(sessionId)` 作为成功必要条件，缺失即失败 |
| DeepSeek 回复慢或无流式事件 | 在原生窗口记录首个 chunk、turn/end 和宿主日志，超时给出 OPEN/STREAM_TIMEOUT，不在白页伪造结果 |
| 旧 session 绑定到新目标 | 每次恢复校验 target/revision/preset，错误则拒绝复用 |
| smoke 与优化结果混写 | 由 mode、写入根目录和 JSON 合同三重校验隔离 |
| 工作区生成物污染提交 | 所有提交使用显式路径，禁止 `git add .` |

## 6. 开发退出标准

只有同时满足以下条件才算开发完成：

1. Agent 和 workflow 按钮都能打开真实 DSH 原生会话并显示正确绑定。
2. 白页没有可提交训练消息的模拟聊天入口。
3. 原生聊天产生真实用户消息、assistant 流式消息和 Trainer 工具事件。
4. Agent 优化和 workflow 修改能产生新 revision/changeSet/run，并保留旧 revision 对照。
5. smoke、发布、工程回放遵守 `AGENTS.md` 的固定合同和写入边界。
6. 验收计划中的点击门槛、恢复、错误和隔离用例全部有证据。

