# Agent Trainer 原生会话点击式验收计划

版本：2026-09-30  
对应开发计划：`docs/agent-trainer-native-session-development-plan-20260930.md`  
验收原则：像用户一样点击实际按钮，并在 DSH 原生会话输入内容；API、脚本和文件读取只能用于验收后的证据核对，不能代替点击或原生聊天。

## 1. 验收范围和硬门槛

本计划验收 Agent、工作流、原生跳转、训练优化、恢复、错误处理、smoke、冻结、发布和工程回放。白色页面是选择/复核工作台，DSH 原生会话是唯一训练聊天窗口。

追加入口验收（2026-09-30）：DSH 直接显示“打开 ATE Trainer”，不再要求展开 PTC 面板。点击一次进入 Trainer 工作台，并继续验证 Agent 与工作流的原生会话按钮；原 Gate 0–6 保持为整体通过条件。

以下任一项失败即阻断发布：

- 点击按钮后没有进入真实 DSH 原生会话，或只在白页显示模拟 transcript。
- 原生会话的 target、preset、candidate revision 与用户选择不一致。
- 原生输入没有产生用户消息、assistant/stream 事件或 Trainer 工具事件。
- 优化只改变了页面文字，没有新 revision/changeSet/run，或旧 revision 无法对照。
- 工作流没有真实 native workflow session，步骤顺序和 handoff 无证据。
- smoke 使用了 `11*21`、历史业务 gate 或非 fresh child，或结果没有 `SMOKE_ONLY`/`businessGatePassed:false`。
- 刷新、重开、目标切换或宿主不可用时串用了旧会话或静默回退。

严重级别：P0=原生链路/目标错绑/数据污染，P1=恢复、工具证据、发布隔离，P2=文字、样式、提示语。P0/P1 全通过才算 PASS。

## 2. 测试前置和证据规则

### 2.1 前置条件

1. 使用当前 DSH 宿主，确认“打开 ATE Trainer”直达入口可见，且没有必须先展开的 PTC 控制面板；不要把独立 localhost 页面作为 native 能力证明。
2. 在 DSH 点击“打开 ATE Trainer”进入工作台，确认 opener、host origin、nativeHost 和启动消息 channel 存在。
3. 准备一个干净的候选项目；每次创建、保存、打开、加入、排序、冻结和发布都必须现场点击，不能把已有状态当作创建证据。
4. 记录测试时间、浏览器 tab、DSH host、目标 ID、candidate revision 和当前模式。

### 2.2 每条用例必须保存的证据

- CUA 点击序列：按钮文字、selector/坐标、点击时间、截图或 AX 树。
- bridge trace：`bridgeId`、`nonce`、channel、hostOrigin、request/response 时间、错误码。
- native session：session ID、窗口标题、preset、targetKind、targetId、candidate revision、`scope.sessions.open` 成功证据。
- native transcript：用户原文、assistant 首 chunk/终态、tool/call、tool/result、turn/end。
- 候选和运行：旧/新 revision、changeSet、run ID、stepId、agentId、输入、输出、validation、终态。
- 发布：releaseId、snapshot hash、published runId、工程模式读取的 release。

证据落盘位置：

```text
Training_Materials/framework/control/bindings/<sessionId>.json
Training_Materials/framework/control/requests/agent-trainer/<request>.json
Training_Materials/runs/<runId>/framework-run.json
publish/versions/<releaseId>/
publish/runs/<runId>/framework-run.json
```

截图/AX/bridge transcript 放入本次验收批次目录，并为每个文件计算小写 SHA-256。预写 PASS、只读后端 binding、白页摘要都不能单独作为通过证据。

## 3. Gate 0：入口和当前版本

**步骤**

1. 在 DSH 直接点击“打开 ATE Trainer”，不得先展开 PTC 面板或点击第二层 Trainer 链接。
2. 在白页确认项目为 `agent-trainer`，模式切换可见，当前候选 revision 可见。
3. 记录白页地址、host origin、bridge channel 和截图。

**预期**

- 页面由 DSH 宿主打开，能收到 bridge 请求；直接从 standalone localhost 打开时若无宿主，页面显示 `HOST_UNAVAILABLE`，不出现可训练的模拟聊天。
- 宿主显示 ATE Trainer 直接入口，点击一次进入工作台；Agent 与工作流两个训练入口仍能打开真实原生会话。
- 当前版本与回滚点对应的变更记录可查；本次实现前基线为 `dea25de`。

## 4. Gate 1：Agent 原生会话和基础 smoke

**步骤**

1. 点击“新建 Agent”，填写 `agent-T1`，点击“保存 Agent”。分别记录两个点击和生成的 agent ID。
2. 在 Agent 列表选择 `agent-T1`，点击“打开当前专家原生会话”。
3. 在跳转后的 DSH 原生输入框中输入并发送：

   `请读取当前绑定 agent 名称，只回复 agent-T1。`

4. 再输入并发送：

   `1+2等于几，把答案写在JSON里`

5. 观察原生窗口中的用户消息、assistant 首 chunk、终态和 Trainer 工具事件。

**预期**

- 真实 DSH 原生窗口被打开，标题/preset 为 `agent-trainer`，绑定为 `targetKind=agent,targetId=agent-T1`。
- 原生回复包含 `agent-T1`，算术结果为合法 JSON `{"answer":3}`。
- 产生 fresh child 和 `SMOKE_ONLY` 证据；结果含 `businessGatePassed:false`。白页没有生成第二份训练 transcript。

## 5. Gate 2：Agent 原生优化和新旧版本对照

**步骤**

1. 在 Gate 1 的原生窗口输入并发送：

   `请先读取真实 trainer_context 和 trainer_assets。把当前 Agent 的执行任务改为：计算 11*21。请调用 trainer_apply_changes 保存候选，再调用 trainer_validate 校验。不要只口头说明。`

2. 等待并记录原生工具调用、工具结果、assistant 终态、new revision 和 changeSet。
3. 返回白页，点击“运行当前 Agent”，记录新 runId 和 JSON 输出。
4. 选择旧 revision，点击“运行当前 Agent”，记录旧 runId 和 JSON 输出。

**预期**

- 新 revision 与 changeSet 真实写入 `Training_Materials/runs/<runId>/`；新 revision 的 output 为 `{"answer":231}` 或契约等价的数字 231。
- 旧 revision 仍保持原 smoke 行为 `{"answer":3}`，证明训练前后行为发生了可复现变化。
- 优化运行标记为 `agent-optimization` 或明确的训练模式，不能标为 `SMOKE_ONLY`。

## 6. Gate 3：工作流原生会话、排序和 handoff

**步骤**

1. 点击“新建工作流”，命名 `workflow-native-1`，点击保存。
2. 点击“加入 Agent”，先加入 `agent-T1`，再加入 `agent-T2`；每次点击都记录。
3. 点击“在 Trainer 中训练当前工作流”。确认跳转到 DSH 原生窗口，绑定为 `targetKind=workflow,targetId=workflow-native-1`。
4. 在原生窗口输入：

   `请读取当前工作流的步骤和绑定 revision，只用列表告诉我顺序；不要修改。`

5. 在原生窗口输入：

   `把工作流顺序改为 agent-T2 → agent-T1。请读取真实上下文，调用 trainer_apply_changes 保存并调用 trainer_validate 校验，然后运行一次。`

6. 返回白页，点击“运行当前工作流”，核对每个 step 的 agentId、revision、input、output 和 handoff。

**预期**

- 原生窗口显示 workflow 绑定、用户消息、工具事件和终态；白页没有 workflow 模拟聊天。
- 新 workflow revision 的顺序为 T2→T1，运行证据按该顺序生成；没有步骤时不能用上一步输出冒充本步输入。
- 每个 child 都是 fresh DSH model child，缺失、畸形或非预期结果会使运行失败并停止。

## 7. Gate 4：恢复、切换、重复和错误

### 4.1 刷新与重开

1. 在已有 native session 时刷新白页，再点击同一目标的“打开原生会话”。
2. 关闭并重新打开 DSH 宿主页，从“打开 ATE Trainer”直达入口进入，重复打开同一目标。

预期：复用仍有效且绑定正确的 session，或创建清晰标记的新 session；不出现重复窗口、空 transcript 或错误目标。

### 4.2 目标和 revision 切换

1. 从 agent-T1 切到 agent-T2，再切到 workflow-native-1。
2. 选旧 revision 后切回新 revision，再点击打开。

预期：旧 session 被拒绝复用或明确创建新 session；每个 native 窗口显示正确 target/revision/preset。

### 4.3 无宿主和桥接故障

1. 在没有 DSH host 的 standalone 页面点击打开。
2. 关闭 BroadcastChannel 或模拟 host origin 不在 allowlist。
3. 重复点击按钮和重复发送同一 nonce。

预期：分别得到 `HOST_UNAVAILABLE`、`ORIGIN_REJECTED`、幂等成功或明确失败；不得回退到白页 `session.prompt`，不得静默成功。

## 8. Gate 5：smoke、冻结、发布和工程回放

**步骤**

1. 点击 smoke 训练入口，逐个确认八个专家新 run 和 fresh child。
2. 在原生会话或页面提供的发布按钮中点击“冻结”，再点击“发布”。每个动作分别截图。
3. 点击“工程模式运行”，读取发布 release；之后在训练模式创建一个未发布候选，再次点击工程模式运行。

**预期**

- 八个专家均收到精确 smoke 输入并返回 `answer:3`；结果均 `SMOKE_ONLY`、`businessGatePassed:false`。
- `publish/versions/<releaseId>/` 含八个冻结 snapshot 和完整 orchestration evidence；`publish/runs/<runId>/` 使用 pinned snapshot 并创建新 run。
- 未发布候选不会改变工程模式结果；工程模式不调用训练中的白页聊天或旧业务 gate。

## 9. Gate 6：DeepSeek 响应和可观测性

在 Gate 1 至 Gate 3 中至少各保存一条：prompt 发出时间、首个 assistant/chunk 时间、tool call/result 时间、turn/end 时间。首 chunk 应早于终态；在当前环境记录实际耗时，超过项目阈值时标记 `STREAM_TIMEOUT` 并保留日志。不能用白页轮询延迟来代替原生流式事件。

## 10. 失败处理、重测和最终判定

- P0 失败：停止后续发布验收，修复并从失败 Gate 重新执行。
- P1 失败：可以继续收集不依赖该功能的证据，但不能宣布整体通过。
- P2 失败：记录界面问题，修复后补做对应截图。
- 每次重测必须生成新的时间戳和 evidence batch，旧批次保留，不覆盖。
- 最终 PASS 需要 Gate 0–6 全部通过、每个点击动作都有证据、native transcript 与服务端 run/revision 能互相对应，并由 Git 提交记录实现和验证结果。

## 11. 原生模型选择核对（追加）

绑定文件中的 `nativeModelSelection` 只是 Trainer 服务要求的模型快照；DSH 原生窗口还必须以实际请求 ledger 和窗口模型选择器核对最终路由。若窗口初始模型与绑定快照不同，必须在原生窗口实际点击模型选择器切换到 `DeepSeek-V4-Flash`，再发送一条消息并检查 ledger 的 `provider/model/modelSource`，否则模型 Gate 不通过。当前一次工作流验证已证明：初始宿主实际为 `zai-coding-cn/glm-5.3-flash`，点击选择 `DeepSeek-V4-Flash` 后实际 ledger 变为 `deepseek-official/deepseek-v4-flash`；该差异仍需决定是否在入口代码中自动消除，不能用绑定文件的期望值代替实际请求证据。



## Addendum 2026-09-30

The acceptance matrix now has direct evidence for the renamed synthetic BUSINESS_ONLY control and a completed fresh-child run for 23*24+45=597. Evidence is recorded in docs/agent-trainer-native-session-evidence-20260930.json and its SHA-256 sidecar. The active registry remains empty and the eight-expert receipts remain archive-only. Full restart gate B is outside the current scope because it invokes retired eight-expert/business-release tests; the direct scoped acceptance set is 63/63 passed.

### Current user-scope override

Eight-expert smoke, real semiconductor business execution, freeze/publish replay, and the legacy full-suite restart Gate B are outside the current requested scope. Their materials remain archive-only. Acceptance for this scope is the 63/63 direct test set plus actual page clicks and native input producing `23*24+45=597` with `businessGatePassed:false`.

### Gate closure evidence (2026-09-30T14:25:39Z)

Gate A, Gate B, and Gate C all passed in the sanctioned GatesOnly run. The earlier default-sandbox python EPERM was an execution permission artifact; release acceptance independently passed 10/10 with child-process permissions.


### Final audit result (2026-09-30)

Gate 0-6 closure evidence is recorded and hashed. The current scope is native DSH session replacement and smoke/publish isolation; it does not certify semiconductor business gates.
