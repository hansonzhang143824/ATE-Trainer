# 任务 B：每个专家固定一个 DSH 原生训练会话

- 执行者：Codex
- 前置：任务 A 已通过 Claude 验收（B 依赖「Agent ID 永不复用」，否则新 Agent 会接上已删 Agent 的会话）
- 完成后：逐条自测「验收标准」1~14，填写末尾「完成报告」，按惯例提交（提交信息 `[B] ...`），然后由 Claude 验收
- 预计工作量：约 1 天（含单测与重启验证）

---

## 0. 开工前（必须）

1. **先做 GitLab 同步**（按项目惯常流程）。同步失败或有冲突时停止，在完成报告中说明。
2. `git status` 确认工作区干净，`git log` 中能看到 `[A]` 提交。
3. 备份将修改的文件（同目录 `.bak-<YYYYMMDD>-taskB`，不提交）：
   - `plugins/dsh-ptc-control-plane/client/native-sessions.js`
   - `plugins/dsh-ptc-control-plane/lib/trainer-service.js`
   - `docs/prototypes/agent-trainer-repair-prototype.html`
   - 以及实际改动到的其他文件
4. 备份服务端绑定数据目录：`Training_Materials/framework/control/bindings/` → `Training_Materials/framework/control/bindings.bak-<YYYYMMDD>-taskB/`（不提交）。
5. 运行一次插件现有测试，记录基线结果（通过数 / 失败数）。测试入口以 `plugins/dsh-ptc-control-plane/package.json` 的 scripts 为准。

---

## 1. 背景

### 1.1 现状

白色工作台点「打开 Trainer 原生会话」（训练当前选中 Agent）或「在 Trainer 中训练当前工作流」时：

1. 页面 `openNativeSession(kind)` → `nativeSessionRequest(kind)` 组装请求：
   `{targetKind, targetId, agentId|workflowId, projectId:'agent-trainer', mode, candidateRevision, selectedRunId, presetId:'agent-trainer'}`
2. `sendNativeBridge(request, title)` 通过 `postMessage` / BroadcastChannel / localStorage 发给 DSH 宿主窗口（消息类型 `dsh-agent-trainer-open-session`），等待 `dsh-agent-trainer-session-result`。
3. 宿主侧调用 `client/native-sessions.js` → `openTrainerNativeSession(scope, request, { post, title, hostId })`（调用方用 `grep -rn openTrainerNativeSession plugins/dsh-ptc-control-plane/client` 定位）。
4. `openTrainerNativeSession` 当前逻辑：
   - 复用 key = `ptcSessionKey(targetKind, JSON.stringify([projectId, mode, targetId, presetId, candidateRevision, selectedRunId]))`；
   - 先查进程内 `state.sessions`，再查宿主窗口 localStorage（`ptc-native-session:<key>`）；
   - 找到且 `matches(binding)` 通过 → 复用；`matches` 要求 `candidateRevision`（或 `currentCandidateRevision`）与 `selectedRunId` 都相同；
   - 否则 `post('open-native-session', request)` 新建。
5. 服务端 `lib/trainer-service.js`：
   - `storage = <workspaceRoot>/Training_Materials/framework/control`；
   - 绑定按 sessionId 存：`bindings/<sessionId>.json`，字段含 `projectId, mode, targetKind, targetId, presetId, candidateRevision, selectedRunId, sessionId, bindingRevision, effectiveTools, toolCatalogSha256` 等；
   - `bind(args)`：仅传 `sessionId` 时返回现有绑定 + `currentCandidateRevision`；传完整参数时校验并写入，`baseBindingRevision` 必须等于现有 `bindingRevision`（否则 `binding_conflict`），`bindingRevision` +1；
   - `openNativeSession(args)`：`sessionFactory` 创建真实 DSH 会话，然后 `bind`；
   - `apply-changes` 分支：若请求来自已绑定会话，会把该会话绑定的 `candidateRevision` 更新为新 revision；
   - 有串行队列 `serial(task)` 可用于写操作互斥。

### 1.2 问题

- 保存候选（revision 变）或运行一次（selectedRunId 变）后 key 改变 → 每轮迭代新开一个会话，DSH 会话列表里堆积同名会话，训练过程分散。
- key → sessionId 只在宿主窗口 localStorage，换窗口/清缓存后找不回。
- `matches()` 里 `currentCandidateRevision` 的容忍逻辑因 key 含 revision 而永远用不到。

### 1.3 目标

- 同一 `(projectId, mode, targetKind, targetId, presetId)` 对应**一个**长期训练会话（DSH 会话不删就一直在）。
- 对应关系**存服务端**；localStorage 只作缓存。
- revision / runId 变化时**复用会话并更新绑定**，并让会话明确知道上下文已变化。
- 用户可「新开训练会话」，新会话成为该目标的默认会话；旧会话保留为历史。
- 已删除的 Agent / 工作流不再复用其会话。

---

## 2. 要做的事

### 2.1 服务端：target-session 存储（`lib/trainer-service.js`）

1. 新增目录 `<storage>/target-sessions/`。
2. 文件名：`sha256('<projectId>|<mode>|<targetKind>|<targetId>|<presetId>')` 的前 32 位十六进制 + `.json`。
3. 内容：
   ```json
   { "schemaVersion": 1, "projectId": "...", "mode": "training", "targetKind": "agent", "targetId": "...",
     "presetId": "agent-trainer", "sessionId": "...", "createdAt": "ISO", "updatedAt": "ISO" }
   ```
4. 写入使用与 `bindingFile` 相同的原子写函数（`atomic`），并放在 `serial()` 中执行。
5. 新增 operation（在 `execute` 的 switch 中）：
   - `target-session`：入参 `projectId, mode, targetKind, targetId, presetId`。行为：
     - 读记录；无记录 → 返回 `null`；
     - 用 `readProject` 检查 target 仍存在于当前 candidate（agent 查 `project.agents[].agentId`，workflow 查 `project.workflows[].workflowId`）；不存在 → 返回 `null`（记录保留不删，便于追溯）；
     - 有记录但 `bindings/<sessionId>.json` 不存在 → 返回 `null`；
     - 否则返回 `{ ...record, binding }`。
   - `forget-target-session`：同样入参；删除该记录文件（不存在也返回成功）；**不删除 DSH 会话、不删除 bindings 文件**。返回 `{ forgotten: true|false }`。
6. `openNativeSession(args)` 成功后写入/覆盖 target-session 记录。
7. 新 operation 需要和现有 operation 一样经过 `authorize`；只允许 page principal 或宿主调用，**不允许**从已绑定的原生会话（agent 工具）调用 `forget-target-session`。
8. 若 API 路由是按 operation 白名单注册的（检查 `lib/trainer-host.js`、`lib/trainer-api.js`、`lib/index.js`），把两个新 operation 加入，对应路径 `/api/ptc-control/trainer/target-session`、`/api/ptc-control/trainer/forget-target-session`。

### 2.2 客户端：复用规则（`client/native-sessions.js` → `openTrainerNativeSession`）

1. 去重 key（`state.pending`、`state.sessions`、localStorage key）改为：
   `ptcSessionKey(targetKind, JSON.stringify([projectId, mode, targetId, presetId]))`。
2. 查找顺序：
   1. `post('target-session', {projectId, mode, targetKind, targetId, presetId})`；
   2. 若服务端返回 `null`，再查进程内 `state.sessions` 与 localStorage（兼容旧数据）；用旧数据找到的 sessionId 也必须通过下面第 3 步的全部校验才可复用。
3. 复用条件（全部满足）：
   - `scope.sessions.binding(sessionId) !== undefined`（DSH 中会话仍存在）；
   - `sessionPreset(binding) === 'agent-trainer'`；
   - `post('bind-session', {projectId, mode, sessionId})` 成功，且返回绑定的 `projectId, mode, targetKind, targetId, presetId` 与请求一致（新 `matchesTarget()`，**不比较 revision 与 runId**）。
4. 复用时更新绑定：
   - `post('bind-session', {...request, sessionId, baseBindingRevision: previous.bindingRevision})`；
   - 遇到 `binding_conflict`：重新读一次绑定再重试 1 次，仍失败则抛错；
   - 校验返回绑定 `effectiveTools` 包含 `trainer_context`；
   - 若复用来源是 localStorage（服务端无记录），复用成功后补写服务端 target-session 记录（可在服务端 `bind` 成功后由客户端调用一个写入入口，或在服务端 `bind` 中对 `presetId==='agent-trainer'` 自动 upsert —— 二选一，在完成报告说明）。
5. 复用失败（会话不存在、preset 不符、`session_unbound`、`session_identity_mismatch`、target 不一致）：`post('forget-target-session', ...)`，清掉 localStorage 旧映射，走新建流程。其他错误直接抛出，不要吞掉。
6. 新建流程保持 `post('open-native-session', request)`，成功后更新 `state.sessions` 与 localStorage 缓存。
7. 返回值新增字段：`{ sessionId, binding, reused, scopeOpened: true, previousCandidateRevision, previousSelectedRunId, contextUpdated }`。
8. 保留 `openPtcNativeSession` 等其他导出函数的行为不变（若它们也用 localStorage key，仅在确有必要时修改，并在报告说明）。

### 2.3 复用时的「上下文更新」提示

1. 触发条件：复用成功，且（旧绑定 `candidateRevision` ≠ 新 `candidateRevision`）或（旧 `selectedRunId` ≠ 新 `selectedRunId`）。
2. 先调查 DSH 宿主是否有可靠的「向会话追加消息」能力：检查 `scope.sessions.binding(id).session` 对象上的方法（已知有 `rename`）、`scope.get('connection').api.sessions` 下的接口、DSH 包 `C:\Users\nvt10241\AppData\Roaming\npm\node_modules\@deepseek-ai\dsh` 中会话相关 API。在完成报告中列出调查结论（找到的方法名与签名）。
3. 若存在可追加**可见系统/通知消息**而不触发模型回复的接口：追加
   > [Trainer 上下文更新] 候选 revision：<旧> → <新>；最近一次运行 runId：<旧|无> → <新|无>。请以 trainer_context 工具读取的当前内容为准，不要依赖本会话中较早 revision 的内容。
4. 若只能发送用户消息（会触发模型回复）：**不要自动发送**，改为降级方案。
5. 降级方案：只在白色页面原生会话卡片中显示「已复用会话，绑定已更新：revision <旧> → <新>」，并在服务端绑定中保留 `previousCandidateRevision`、`previousSelectedRunId` 字段供 `trainer_context` 工具读取；在 `trainer_context` 返回中加入 `bindingChanged: {fromRevision, toRevision, fromRunId, toRunId}`（仅当绑定更新后首次读取时为非空，读取后清除）。
6. 返回值 `contextUpdated` 取值：`'message'`（追加了消息）、`'binding-only'`（降级）、`false`（无变化）。

### 2.4 页面：原生会话卡片（`docs/prototypes/agent-trainer-repair-prototype.html`）

1. 卡片在 `status === 'opened'` 时显示：
   - `sessionId`；
   - 「新建会话」或「已复用会话」；
   - 当前绑定 revision；如有变化显示 `revision <旧> → <新>`；
   - 按钮「新开训练会话」。
2. 「新开训练会话」：
   - 点击后弹出页面内确认层（禁止 `window.confirm`）：「为『<name>』新开一个训练会话？当前会话会保留在 DSH 会话列表中作为历史，之后默认使用新会话。」
   - 确认后：`POST /api/ptc-control/trainer/forget-target-session`（mode、targetKind、targetId、presetId 与当前请求一致）→ 再调用 `openNativeSession(kind)`。
3. `nativeSessionRequest` 不需要改字段（revision 与 runId 仍需传给宿主用于更新绑定）。

### 2.5 测试（`plugins/dsh-ptc-control-plane/test/`）

为以下新增单测（风格参照现有测试）：
1. `target-session`：无记录返回 `null`；写入后可读；target 被删后返回 `null`；bindings 文件缺失时返回 `null`。
2. `forget-target-session`：删除记录；重复调用不报错；不删除 bindings 文件。
3. `openNativeSession` 成功后写入 target-session 记录（`sessionFactory` 用 stub）。
4. 客户端 `matchesTarget()`：revision / runId 不同仍匹配；targetId / mode / presetId 不同不匹配。
5. 客户端复用流程（mock `scope.sessions` 与 `post`）：
   - 服务端有记录 → 复用并以 `baseBindingRevision` 调用 `bind-session`；
   - 会话已从 DSH 删除 → 调用 `forget-target-session` 后新建；
   - `binding_conflict` 重试一次。

---

## 3. 不要做

- 不删除任何 DSH 会话，不删除 `bindings/*.json`。
- 不合并不同 mode：training 与 published / engineering 必须是不同会话。
- 不改变 `framework-expert`、`framework-observer`、`framework-worker` 等其他 preset 的绑定规则。
- 不修改运行轮询逻辑（`refreshLiveRun`、`refreshBusinessRun` 等），不修改任务 A 的删除逻辑。
- 不自动向会话发送会触发模型回复的用户消息。

---

## 4. 部署（修改插件后必须）

1. 确认 DSH 当前没有正在进行的运行或重要会话（向用户确认）。
2. 重启：`& "$env:USERPROFILE\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir D:\Newtest\DSH\ATE-Coding-Flow\plugins\dsh-ptc-control-plane`（若参数与脚本实际不符，以脚本为准；备用 `C:\Users\nvt10241\.dsh\restart-dsh-v2.ps1`）。
3. 检查启动日志（`C:\Users\nvt10241\.dsh\dsh-web-restart.log` 或脚本输出）无以下致命签名：`plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。
4. `http://127.0.0.1:3080/agent-trainer` 正常加载。

---

## 5. 验收标准（逐条执行并记录证据）

记录每个 sessionId，并在关键步骤附上 `Training_Materials/framework/control/bindings/<sessionId>.json` 与 `target-sessions/*.json` 的相关字段。以下用一个任务 A 新建的 Agent（记为 X）和工作流「新工作流 1」（记为 W）。

1. **首次打开新建**：选中 X，点「打开 Trainer 原生会话」→ 得到 S1，卡片显示「新建会话」；`target-sessions/` 下出现 X 对应记录，`sessionId === S1`。
2. **直接再开复用**：再次点打开 → 仍为 S1，卡片显示「已复用会话」；DSH 会话列表中名为 `Agent Trainer · <X 的 name>` 的会话只有 1 个。
3. **运行后复用**：运行一次包含 X 的工作流或 SMOKE（使 `selectedRunId` 变化）后再打开 X → 仍为 S1；`bindings/S1.json` 的 `selectedRunId` 为新 runId，`bindingRevision` 比第 2 步大。
4. **保存候选后复用**：修改 X 的 instructions 并保存候选（revision 变化）后再打开 → 仍为 S1；`bindings/S1.json` 的 `candidateRevision` 等于 `current.json` 的 `revisionId`；卡片显示 `revision <旧> → <新>`。
5. **上下文更新**：第 4 步中，`contextUpdated` 为 `'message'` 时 S1 会话中可见 `[Trainer 上下文更新]` 消息且**没有**触发模型回复；为 `'binding-only'` 时，在 S1 中调用 `trainer_context` 工具返回 `bindingChanged` 非空，再调用一次为空。
6. **清缓存仍复用**：清空 DSH 宿主窗口 localStorage 中所有 `ptc-native-session:` 开头的项，刷新宿主与工作台后再打开 X → 仍为 S1。
7. **新开训练会话**：点「新开训练会话」并确认 → 得到 S2；`target-sessions` 中 X 的记录 `sessionId === S2`；S1 仍在 DSH 会话列表中且可打开查看历史；再次点打开 → S2。
8. **会话被手动删除**：在 DSH 中手动删除 S2，再打开 X → 自动新建 S3，无报错；`target-sessions` 记录更新为 S3。
9. **目标隔离**：打开 W（「在 Trainer 中训练当前工作流」）→ 得到 SW，SW ≠ S3；再打开 X → S3；再打开 W → SW。另选一个 Agent Y → 得到不同于 S3、SW 的会话。
10. **模式隔离**：切换到发布 / 工程模式后打开同一目标（若该模式允许打开）→ 得到与训练模式不同的会话；回到训练模式 → 仍为原会话。若该模式不允许打开，记录实际提示。
11. **删除后不复用**：把 X 从所有工作流移除后用任务 A 的功能删除 X；`target-session` 查询 X 返回 `null`；新建 Agent Z（新 ID）→ 打开得到全新会话，≠ S3。
12. **旧数据兼容**：在服务端无记录、仅 localStorage 有旧格式 key 的情况下（可用备份的旧 localStorage 值或手工构造），打开对应目标：符合复用条件则复用并补写服务端记录；不符合则新建，无报错。
13. **测试**：插件全部测试通过（与第 0 步基线对比，失败数不增加），新增测试覆盖 2.5 节 5 类场景。
14. **部署与质量**：
    - DSH 重启后启动日志无第 4 节列出的致命签名；
    - 页面 `<script>` 内容 `node --check` 通过；
    - 工作台与 DSH 宿主控制台无新增 error；
    - 页面中无 `window.confirm`、`alert(`、`prompt(`；
    - `git diff --stat` 只包含本任务书第 2 节列出的文件、新增测试与本任务书的完成报告。

---

## 6. 完成报告（Codex 填写）

- GitLab 同步结果：
- 测试基线（开工前）：
- 改动摘要（文件 + 函数）：
- 新增 operation 与路由注册位置：
- 2.2 第 4 条「补写服务端记录」采用的方案：
- 2.3 追加消息能力调查结论（方法名、签名、是否触发模型回复）：
- `contextUpdated` 最终实现：`message` / `binding-only`：
- DSH 重启方式与启动日志检查结果：
- 验收 1~14 结果（每条：通过/失败 + 证据）：
  1.
  2.
  3.
  4.
  5.
  6.
  7.
  8.
  9.
  10.
  11.
  12.
  13.
  14.
- 测试中构造并已清理的数据：
- 偏离本任务书之处及原因：
- 遗留问题：
- 提交 hash：
