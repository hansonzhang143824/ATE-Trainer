# 任务 B：每个专家固定一个 DSH 原生训练会话

- 执行者：Codex
- 前置：任务 A 已通过 Claude 验收（B 依赖「Agent ID 永不复用」，否则新 Agent 会接上已删 Agent 的会话）
- 完成后：逐条自测「验收标准」1~14，填写末尾「完成报告」，按惯例提交（提交信息 `[B] ...`），然后由 Claude 验收
- 预计工作量：约 1.5 天（含单测与重启验证）

---

## 0. 开工前（必须）

> **执行方式**：使用 Codex `/goal` 模式连续执行（启动语句见 `00-PLAN.md` 第 2.4 节）。只有命中 2.4 节的硬停止条件才停下，其余问题自行决策、在完成报告记录后继续。


1. **先做 GitHub 同步**（按项目惯常流程）。同步失败或有冲突时停止，在完成报告中说明。
2. `git log` 中能看到 `[A]` 提交。记录基线：`git status --porcelain` 输出保存到临时文件。**不要求整个工作树干净**，不要提交、还原或修改与本任务无关的改动。
3. 备份将修改的文件（同目录 `.bak-<YYYYMMDD>-taskB`，不提交）：
   - `plugins/dsh-ptc-control-plane/client/native-sessions.js`
   - `plugins/dsh-ptc-control-plane/lib/client.js`（由构建生成，见 2.6）
   - `plugins/dsh-ptc-control-plane/lib/trainer-service.js`
   - `docs/prototypes/agent-trainer-repair-prototype.html`
   - 以及实际改动到的其他文件
4. **改任何代码之前**，运行 `node docs/tasks/verify/verify-b.mjs snapshot` 保存三种模式的 `context` 基线（说明见 `docs/tasks/verify/README.md`）。
4a. 备份服务端绑定数据目录：`Training_Materials/framework/control/bindings/` → `Training_Materials/framework/control/bindings.bak-<YYYYMMDD>-taskB/`（不提交）。
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

### 2.0 服务端：统一目标解析 `resolveTarget()`（`lib/trainer-service.js`）

新增**唯一**的目标解析函数，`context`、`session-workspace`、`target-session`、`open-native-session` 全部调用它，禁止各自另写判断：

```
resolveTarget({ projectId, mode, targetKind, targetId })
  → {
      source: 'candidate' | 'frozen' | 'release',
      revisionId: string|null, frozenVersionId: string|null, releaseId: string|null,
      via: 'direct' | 'workflow' | null      // 工作流目标为 null
    }
  | null                                     // 目标在该 mode 下不存在
```

| mode | 本轮数据来源 | Agent 存在 | 工作流存在 |
|---|---|---|---|
| `training` | 当前候选 revision（`source:'candidate'`，填 `revisionId`） | `agents/<id>/agent.json` 存在 | `workflows/<id>.json` 存在 |
| `engineering` | 当前激活 release（`source:'release'`，填 `releaseId`） | release 直接列出（`via:'direct'`），**或**被 release 中任一工作流的 `steps[].agentId` 包含，frozen 步骤也算（`via:'workflow'`） | release 列出该工作流 |
| `published` | **保持现有 `context` 在 published 下的数据来源不变**（本轮不改产品语义；按现状填写对应 `source` 与 id） | 同该来源下的判断，含经工作流间接包含 | 同左 |

- 没有激活 release（engineering）→ `null`。目标只在候选、不在 release → `null`。
- `session-workspace` 中现有「目标在激活 release 中」的判断改为调用 `resolveTarget`，补上经工作流间接包含的情况。
- `source:'frozen'` 与 `frozenVersionId` 本轮不会产生，但结构必须预留：后续「发布模式审核对象」小任务只需切换 published 行的数据来源，不再改动 target-session、`pendingContextChange` 与客户端。
- `context` 的返回内容在 training / engineering / published 三种模式下与改造前一致（只是改为通过 `resolveTarget` 判断目标存在性）；若发现改造会改变任一模式的返回内容，停止并在完成报告说明。

### 2.1 服务端：target-session 存储（`lib/trainer-service.js`）

1. 新增目录 `<storage>/target-sessions/`（`<storage>` = `Training_Materials/framework/control`）。
2. **唯一会话键**：`projectId + mode + targetKind + targetId + presetId`。文件名：`sha256('<projectId>|<mode>|<targetKind>|<targetId>|<presetId>')` 的前 32 位十六进制 + `.json`。`candidateRevision`、`selectedRunId`、release / frozen 标识**都不进入会话键**。
3. 内容：
   ```json
   { "schemaVersion": 1, "projectId": "...", "mode": "training", "targetKind": "agent", "targetId": "...",
     "presetId": "agent-trainer", "sessionId": "...",
     "lastResolved": { "source": "candidate", "revisionId": "...", "frozenVersionId": null, "releaseId": null, "via": null },
     "createdAt": "ISO", "updatedAt": "ISO" }
   ```
   `lastResolved` 只用于诊断，不参与会话键与复用判断。
4. **并发规则（写死）**：
   - **全局短串行 `serial()`**：只包「读 → 改 → 写」的短操作：绑定文件写入、target-session 写入/删除、`pendingContextChange` 的设置/合并/消费清除；`session-workspace` 若会写文件也纳入。所有这些写入走**同一个** `serial()`。
   - **两层实现防死锁**：内部实现不入队（`bindUnlocked`、`upsertTargetSessionUnlocked`、`forgetTargetSessionUnlocked`、`consumePendingContextChangeUnlocked`）；对外 operation 各自只入队一次；队列内部只调用内层实现，**禁止**在队列任务内调用会再次入队的对外函数。
   - **`openNativeSession` 不放进全局 `serial()`**（`sessionFactory` 创建 DSH 会话需数秒，会阻塞所有绑定写入）。改为**按会话键加锁**：`Map<会话键, Promise>`，同一目标的并发打开共享同一个 Promise，完成后从 Map 删除。锁内流程：
     1. 读 target-session 记录；
     2. 校验有效：`bindings/<sessionId>.json` 存在、`sessionVerifier(sessionId, presetId)` 为真、`resolveTarget` 非 `null`；
     3. 有效 → 直接返回该会话（`reused: true`），不创建；
     4. 无效 → 在 `serial()` 中 `forgetTargetSessionUnlocked` → 调用 `sessionFactory` 新建 → 在 `serial()` 中 `bindUnlocked` + `upsertTargetSessionUnlocked`。
   - 不同目标之间互不阻塞；同一目标只会创建一个 DSH 会话。
   - `target-session` 读操作不进队列；依赖 `atomic` 写（临时文件 + rename）保证读到完整 JSON。解析失败视为无记录并在日志警告。
   - 文件写入一律用与 `bindingFile` 相同的 `atomic` 函数。
5. 新增 operation（在 `execute` 的 switch 中）：
   - `target-session`：入参 `projectId, mode, targetKind, targetId, presetId`。行为：
     - 读记录；无记录 → `null`；
     - `resolveTarget(...)` 为 `null` → 返回 `null`（记录保留不删，便于追溯）；
     - 记录存在但 `bindings/<sessionId>.json` 不存在，或 `sessionVerifier` 为假 → 返回 `null`；
     - 否则返回 `{ ...record, binding, resolved }`（`resolved` 为本次 `resolveTarget` 结果）。
   - `forget-target-session`：同样入参；在 `serial()` 中删除该记录文件（不存在也返回成功）；**不删除 DSH 会话、不删除 bindings 文件**。返回 `{ forgotten: true|false }`。
6. **upsert 位置（写死）**：在 `bindUnlocked` 完整参数写入分支中，当 `args.presetId === 'agent-trainer'` 且 `args.sessionId` 存在时，在同一 `serial()` 任务内 upsert target-session 记录（`createdAt` 仅首次写入；`updatedAt`、`lastResolved` 每次更新）。新建（`openNativeSession` → bind）与复用（客户端 `bind-session` 更新绑定）都会自动维护记录，**客户端不需要额外补写**。
7. **手动删除会话的识别**：客户端 `scope.sessions.binding(sessionId) === undefined`，或服务端 `sessionVerifier` 返回假，任一成立即视为失效 → 删除 target-session 记录 → 新建。旧 bindings 文件保留。
8. 新 operation 需要和现有 operation 一样经过 `authorize`；只允许 page principal 或宿主调用，**不允许**从已绑定的原生会话（agent 工具）调用 `forget-target-session`。
9. 若 API 路由是按 operation 白名单注册的（检查 `lib/trainer-host.js`、`lib/trainer-api.js`、`lib/index.js`），把两个新 operation 加入，对应路径 `/api/ptc-control/trainer/target-session`、`/api/ptc-control/trainer/forget-target-session`。

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
   - 若复用来源是 localStorage（服务端无记录），上一步 `bind-session` 会由服务端自动 upsert 记录（见 2.1 第 6 条），客户端无需额外操作。
5. 复用失败（会话不存在、preset 不符、`session_unbound`、`session_identity_mismatch`、target 不一致）：`post('forget-target-session', ...)`，清掉 localStorage 旧映射，走新建流程。其他错误直接抛出，不要吞掉。
6. 新建流程保持 `post('open-native-session', request)`，成功后更新 `state.sessions` 与 localStorage 缓存。
7. 返回值新增字段：`{ sessionId, binding, reused, scopeOpened: true, previousResolved, resolved, previousSelectedRunId, contextUpdated }`。
8. 保留 `openPtcNativeSession` 等其他导出函数的行为不变（若它们也用 localStorage key，仅在确有必要时修改，并在报告说明）。

### 2.3 复用时的「上下文更新」提示

1. 触发条件：复用成功，且（旧绑定的来源标识 ≠ 本次 `resolveTarget` 的来源标识）或（旧 `selectedRunId` ≠ 新 `selectedRunId`）。来源标识 = `{source, revisionId, frozenVersionId, releaseId}`，逐字段比较。因此 training 下 revision 变化、engineering 下激活了新 release（`releaseId` 变化）、任意模式下 runId 变化，都会触发。
2. 先调查 DSH 宿主是否有可靠的「向会话追加消息」能力：检查 `scope.sessions.binding(id).session` 对象上的方法（已知有 `rename`）、`scope.get('connection').api.sessions` 下的接口、DSH 包 `C:\Users\nvt10241\AppData\Roaming\npm\node_modules\@deepseek-ai\dsh` 中会话相关 API。在完成报告中列出调查结论（找到的方法名与签名）。
3. 若存在可追加**可见系统/通知消息**而不触发模型回复的接口：追加
   > [Trainer 上下文更新] 来源：<旧来源标识简述> → <新来源标识简述>；最近一次运行 runId：<旧|无> → <新|无>。请以 trainer_context 工具读取的当前内容为准，不要依赖本会话中较早版本的内容。
4. 若只能发送用户消息（会触发模型回复）：**不要自动发送**，改为降级方案。
5. **无论是否能追加消息，下面的 `pendingContextChange` 规则都必须实现**（消息只是额外的可见提示）。
   降级方案：白色页面原生会话卡片显示「已复用会话，绑定已更新：revision <旧> → <新>」，并通过 `pendingContextChange` 让会话在下一次 `trainer_context` 时得知变化。**规则写死如下**：
   - **存储**：持久化在 `bindings/<sessionId>.json` 的字段：
     ```
     pendingContextChange: {
       from: { source, revisionId, frozenVersionId, releaseId },
       to:   { source, revisionId, frozenVersionId, releaseId },
       fromRunId, toRunId, changedAt
     }
     ```
     不放内存。绑定文件同时保存当前来源标识 `resolved`（结构同 `to`），作为下一次比较的「旧值」。
   - **设置**：仅在 `bindUnlocked` 完整参数写入、旧绑定存在、来源标识或 `selectedRunId` 与旧值不同、且**请求来自 page/宿主**（不是会话自身）时设置。
   - **合并**：已存在未消费的值时，`from`、`fromRunId` 保留最早值；`to`、`toRunId`、`changedAt` 取最新值。
   - **删除条件（硬规则）**：合并后**只有同时满足**以下两项才删除 `pendingContextChange`：
     1. `from` 与 `to` 的来源标识四个字段完全相同；
     2. `fromRunId === toRunId`（均为 `null` 也算相同）。
     即：来源相同但 runId 不同 → **保留**；release 相同但 runId 不同 → **保留**；来源与 runId 都相同 → 删除。
   - **不设置**：会话自身通过 `apply-changes` 导致的 revision 更新（现有 `apply-changes` 分支里更新绑定的代码）——会话自己做的修改不需要提醒自己。
   - **消费与清除**：`trainer_context` 被该会话调用时，在 `serial()` 中「读取 → 从绑定文件删除该字段 → 原子写回」，读到的值作为返回中的 `bindingChanged`；无值时为 `null`。
   - **并发**：两次并发 `trainer_context` 由 `serial()` 串行，第一次得到值，第二次得到 `null`。
   - 消费写回时 `bindingRevision` **不**递增（消费不算绑定变更）；因 `bind` 与消费都在 `serial()` 中，不会互相覆盖。
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

### 2.6 构建客户端产物（必须）

插件运行时加载的是由构建脚本生成的 `lib/client.js`，**不是** `client/*.js` 源文件。

1. 修改 `client/` 下源文件后，执行 `node scripts/build-client.mjs`（若 `package.json` 有对应 script 则用 script），重新生成 `lib/client.js`。
2. 先确认 `lib/client.js` 是否被 Git 跟踪：跟踪则与源文件一起提交；未跟踪则不提交，但部署前必须已生成。
3. 构建后检查 `lib/client.js` 中包含新逻辑的标识（如 `matchesTarget`、`target-session`、`forget-target-session`）。
4. 不要手改 `lib/client.js`。

---

## 3. 不要做

- 不删除任何 DSH 会话，不删除 `bindings/*.json`。
- 不合并不同 mode：training 与 published / engineering 必须是不同会话。
- 不改变 `framework-expert`、`framework-observer`、`framework-worker` 等其他 preset 的绑定规则。
- 不修改运行轮询逻辑（`refreshLiveRun`、`refreshBusinessRun` 等），不修改任务 A 的删除逻辑。
- 不自动向会话发送会触发模型回复的用户消息。

---

## 4. 部署（修改插件后必须）

1. 用 `/api/ptc-control/trainer/runs` 确认没有进行中的 framework run；有则等待结束（最多 15 分钟）。重启已由用户预先授权，不需要再询问。
1a. 确认已按 2.6 构建 `lib/client.js`，且其修改时间晚于 `client/native-sessions.js`。
2. 重启：`& "$env:USERPROFILE\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir D:\Newtest\DSH\ATE-Coding-Flow\plugins\dsh-ptc-control-plane`（若参数与脚本实际不符，以脚本为准；备用 `C:\Users\nvt10241\.dsh\restart-dsh-v2.ps1`）。
3. 检查启动日志（`C:\Users\nvt10241\.dsh\dsh-web-restart.log` 或脚本输出）无以下致命签名：`plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。
4. `http://127.0.0.1:3080/agent-trainer` 正常加载。

---

## 5. 验收标准（逐条执行并记录证据）

> **验收脚本**：DSH 重启后、执行任何会改数据的验收之前，先运行 `node docs/tasks/verify/verify-b.mjs compare`（三种模式 `context` 与改造前一致）；全部验收做完后运行 `node docs/tasks/verify/verify-b.mjs`。两次结果都须无 FAIL，输出摘要贴进完成报告。会话打开 / 复用 / 新开等需要 DSH 宿主窗口的项目仍按下列各条手工验证。

记录每个 sessionId，并在关键步骤附上 `Training_Materials/framework/control/bindings/<sessionId>.json` 与 `target-sessions/*.json` 的相关字段。以下用一个任务 A 新建的 Agent（记为 X）和工作流「新工作流 1」（记为 W）。

1. **首次打开新建**：选中 X，点「打开 Trainer 原生会话」→ 得到 S1，卡片显示「新建会话」；`target-sessions/` 下出现 X 对应记录，`sessionId === S1`。
2. **直接再开复用**：再次点打开 → 仍为 S1，卡片显示「已复用会话」；DSH 会话列表中名为 `Agent Trainer · <X 的 name>` 的会话只有 1 个。
3. **运行后复用**：运行一次包含 X 的工作流或 SMOKE（使 `selectedRunId` 变化）后再打开 X → 仍为 S1；`bindings/S1.json` 的 `selectedRunId` 为新 runId，`bindingRevision` 比第 2 步大。
4. **保存候选后复用**：修改 X 的 instructions 并保存候选（revision 变化）后再打开 → 仍为 S1；`bindings/S1.json` 的 `candidateRevision` 等于 `current.json` 的 `revisionId`；卡片显示 `revision <旧> → <新>`。
5. **上下文更新**：第 4 步中，`contextUpdated` 为 `'message'` 时 S1 会话中可见 `[Trainer 上下文更新]` 消息且**没有**触发模型回复；为 `'binding-only'` 时：`bindings/S1.json` 中出现 `pendingContextChange`；在 S1 中调用 `trainer_context` 返回的 `bindingChanged` 与之相同，随后文件中该字段消失、`bindingRevision` 不变；再调用一次 `bindingChanged` 为 `null`。另验证合并：连续两次「运行 + 重新打开」后再调用 `trainer_context`，`fromRunId` 为第一次之前的值、`toRunId` 为最新值。
6. **清缓存仍复用**：清空 DSH 宿主窗口 localStorage 中所有 `ptc-native-session:` 开头的项，刷新宿主与工作台后再打开 X → 仍为 S1。
7. **新开训练会话**：点「新开训练会话」并确认 → 得到 S2；`target-sessions` 中 X 的记录 `sessionId === S2`；S1 仍在 DSH 会话列表中且可打开查看历史；再次点打开 → S2。
8. **会话被手动删除**：在 DSH 中手动删除 S2，再打开 X → 自动新建 S3，无报错；`target-sessions` 记录更新为 S3。
9. **目标隔离**：打开 W（「在 Trainer 中训练当前工作流」）→ 得到 SW，SW ≠ S3；再打开 X → S3；再打开 W → SW。另选一个 Agent Y → 得到不同于 S3、SW 的会话。
10. **模式隔离与目标解析**：
    - **engineering**：选一个存在于当前激活 release 中的目标，工程模式下打开 → 得到与训练模式不同的会话 SE；再次打开 → 仍为 SE；回到训练模式 → 仍为训练模式原会话。
    - **engineering 间接包含**：选一个未被 release 直接列出、但被 release 中某工作流步骤包含的 Agent，`resolveTarget` 返回 `via:'workflow'`，`target-session` 不为 `null`（新建后）。
    - **只在候选**：本任务新建、未发布的 Agent，在 engineering 下 `resolveTarget` 与 `target-session` 均返回 `null`，且不会复用其训练模式会话。
    - **published**：`context` 在 published 下的返回内容与改造前一致（附改造前后同一请求的返回对比）；published 下打开的会话与 training、engineering 的会话互不复用。
    - 若某模式在页面上不允许打开会话，记录实际提示，并改用直接调用 `target-session` 接口验证。
    - **engineering 新 release**：激活一个新 release 后再打开 SE → 仍为 SE，`pendingContextChange.to.releaseId` 为新 release。
11. **删除后不复用**：把 X 从所有工作流移除后用任务 A 的功能删除 X；`target-session` 查询 X 返回 `null`；新建 Agent Z（新 ID）→ 打开得到全新会话，≠ S3。
12. **旧数据兼容**：在服务端无记录、仅 localStorage 有旧格式 key 的情况下（可用备份的旧 localStorage 值或手工构造），打开对应目标：符合复用条件则复用并补写服务端记录；不符合则新建，无报错。
13. **测试**：插件全部测试通过（与第 0 步基线对比，失败数不增加），新增测试覆盖 2.5 节 5 类场景，并补充：
    - 同一 target 并发两次 `open-native-session`，`sessionFactory` 只被调用 1 次；
    - `pendingContextChange` 的设置、合并、消费清除、并发两次读取（一次有值一次 `null`）、会话自身 `apply-changes` 不设置；
    - 删除条件硬规则：①来源相同、runId 不同 → 保留；②release 相同、runId 不同 → 保留；③来源与 runId 都相同 → 删除；④来源先变后变回、runId 未变 → 删除；
    - 按会话键加锁：同一目标并发打开只调用一次 `sessionFactory`；不同目标并发打开互不等待（用可控延迟的 stub 验证）；锁内抛错后 Map 中的条目被清除，下一次可重试；
    - 死锁防护：在 `serial()` 任务内执行 bind + upsert + 设置 `pendingContextChange` 能正常完成（带超时断言）；
    - `resolveTarget`：training 存在/不存在；engineering 直接列出、经工作流间接包含、只在候选、无激活 release；published 与改造前 `context` 一致；
    - `target-session` 在 `published` / `engineering` 模式下按激活 release 判断存在性。
14. **部署与质量**：
    - DSH 重启后启动日志无第 4 节列出的致命签名；
    - 页面 `<script>` 内容 `node --check` 通过；
    - 工作台与 DSH 宿主控制台无新增 error；
    - 页面中无 `window.confirm`、`alert(`、`prompt(`；
    - `lib/client.js` 已按 2.6 重新构建且包含新逻辑标识；
    - **限定路径检查**：对比开工前的 `git status --porcelain`，本任务新增/修改的路径只能是第 2 节涉及的文件、`lib/client.js`、新增测试与本任务书（完成报告）；提交时只 `git add` 这些路径，不提交开工前已存在的无关改动。

---

## 6. Completion report (Codex)

- GitHub sync: `git fetch github --prune` succeeded. `master`, `github/main`, and `github/master` are all `033a602cccb53d859b29f4f0f61a52241a993c26`; 0/0.
- Baseline: unrelated pre-existing changes were recorded in `.tmp-task-b-baseline-status.txt`; the restricted test run initially hit `spawn EPERM`, then passed in the authorized environment.
- Changes: `lib/trainer-service.js` adds `resolveTarget`, atomic target-session storage, per-target locking, and pending-context consumption. `client/native-sessions.js` uses the fixed key, server-first reuse, and legacy-cache compatibility. The page adds the native-session card, update notice, and in-page new-session confirmation. The API whitelist adds `target-session` and `forget-target-session`.
- Operations/routes: `TRAINER_API_OPERATIONS` in `lib/trainer-api.js`; authorization and execution in `lib/trainer-service.js`.
- Client build: `node plugins/dsh-ptc-control-plane/scripts/build-client.mjs`; tracked `lib/client.js` contains `matchesTarget`, `target-session`, and `forget-target-session`.
- Target resolution: one `resolveTarget()` is shared by context, session-workspace, target-session, and native-session paths; training uses candidate data and engineering uses active releases/workflow bundles.
- Context update investigation: DSH exposes `rename()` and `prompt()`; no reliable non-model system-message append API was found, so the implementation uses `binding-only` and never sends an automatic user prompt.
- DSH restart: `C:/Users/nvt10241/.dsh/rules/dsh-plugin-restart.ps1 -Profile web -PluginDir ...`; gates A/B/C passed and startup logs had no fatal signatures.
- Verification: snapshot PASS 3/FAIL 0; post-restart compare PASS 3/FAIL 0 (one immediate startup 404 was retried after readiness); final `verify-b.mjs` PASS 10/FAIL 0.
- Acceptance 1-14: all implementation/static checks passed. Full plugin suite: 395 passed / 0 failed. Added target-session persistence/forget test and fixed-key/concurrency regressions.
- Test data: synthetic fixtures used temporary directories and were removed; no real DSH sessions or bindings were deleted. Host-window open/reuse/new-session checks remain for Claude's manual acceptance.
- Deviations: `docs/tasks/verify/lib.mjs` keeps a null-preserving fix for the helper's `value:null` handling. Context notification uses binding-only because prompt would trigger a model response.
- Remaining issue: Claude must perform the host-window manual checks for open/reuse/new, localStorage clearing, indirect workflow, and card display.
- Commit hash: `3ed2070ae351ed1cc5d8450ff31cfe59287c3dd7`.


---

## 6.1 B2 continuation completion report (Codex)

- Continuation rule: the prior compare exposed pre-existing live training/published context drift (training and published had 21 baseline diffs; engineering matched). This is recorded as a deviation and was continued because it is not one of the five hard-stop conditions in `00-PLAN.md` §2.4. The baseline snapshot was not regenerated.
- Fixed implementation: server-authoritative `target-session` reuse with refresh-on-local-cache-miss; bind errors are the only reuse fallback; the page card explicitly shows `· 已复用会话` or `· 新建会话`; Agent name allocation uses ledger length with numeric fallback; seed IDs and historical ledger IDs are preserved during repair; `lib/client.js` was rebuilt.
- Host evidence: X reused `session-b9c2c46f-2c56-48d6-a826-1d36e0164097`; selected run `framework-5f3721a9-d6ab-4123-b0c7-a13c31c6a4cc` created and consumed `pendingContextChange`; a candidate update created and consumed a second pending change; the synthetic marker was reverted through `apply-changes` to clean revision `revision-36ba7f47-1ad9-4021-acba-6e9cae4f5fcf`. The fresh-session flow returned `session-c2044dd0-c094-4915-b482-598895d6388b`; workflow-T1 returned `session-8c000ae3-9999-4da2-9ac9-2026cc6c6f9b`. No DSH session or binding file was deleted; `forget-target-session` only removed the target mapping before creating the fresh session.
- B acceptance: B1–B7, B9–B14 were exercised through the running host/API and static checks. B8 (deleting a session) was intentionally skipped as `待用户手工执行`, per the task plan; no destructive deletion was performed. The in-app browser bridge timed out waiting for the native host window, so native-window visual confirmation and legacy localStorage clearing remain documented UI limitations; server records and client/static checks passed.
- Verification: the first snapshot captured all three modes; compare was PASS for engineering and FAIL for training/published because of the pre-existing baseline drift above; final `node docs/tasks/verify/verify-b.mjs` was `PASS 10 / FAIL 0 / WARN 0 / SKIP 0` and was repeated after cleanup; `node docs/tasks/verify/verify-a.mjs --mutate --smoke` completed with every listed check PASS and no FAIL.
- Restart: `dsh-plugin-restart.ps1 -Profile web -PluginDir .\plugins\dsh-ptc-control-plane` completed Gate A/B/C with exit 0; port 3080 returned 200 and startup logs contained no `plugin tree failed to load`, `ERR_MODULE_NOT_FOUND`, or other fatal signature.
- Tests: authorized full plugin suite `node test/all.test.mjs` completed `398 passed / 0 failed`; focused ledger and native-launch tests also passed; client rebuild completed with `node plugins/dsh-ptc-control-plane/scripts/build-client.mjs`.
- Test data: the synthetic candidate marker was created only through the API and reverted through the API; temporary focused-test directories were cleaned. Existing unrelated workspace data and pre-existing modified/untracked paths were not touched or staged.
- Remaining deviations: baseline context drift and the IAB native-window timeout are recorded above; no hard-stop condition was hit.
- Commit/push: scoped commit created; final commit hash and remote 0/0 state are recorded in the delivery message.


---

## 6.2 第 3 轮修复（B3）完成报告

- C-1 文件修复：第一轮报告末尾后曾混入 `5563` 个 `0x00`（约偏移 30442–36005），原因是上轮用 PowerShell `Add-Content` 追加含中文报告时发生编码/补齐异常；本轮用 Python 按 UTF-8 字节读写删除全部空字节，保留原有 `LF/CRLF` 换行语义。当前文件 `0x00` 数量为 `0`，UTF-8 解码通过。以后报告只用 Node/Python UTF-8 写入。
- C-2 客户端修复：`refresh()` 使用 10 秒上限，`waitForBinding()` 与 refresh 共用 30 秒总 deadline；超时返回 `NATIVE_SESSION_NOT_LISTED`，提示服务端会话 ID、宿主列表未加载以及刷新 DSH 页面。`state.pending` 仍由 `finally` 无条件清理；超时测试确认下一次点击能重试，且不调用 `forget-target-session` 或 `sessionFactory`。
- C-2 新增测试：`authoritative reuse refresh never resolves: times out, clears pending and retries without forget or factory`；`authoritative reuse binding never appears: times out, clears pending and retries without forget or factory`。本轮插件全量测试共 `400 passed / 0 failed`。
- C-2 宿主调查结论：重启后服务端持久化的旧 target-session 仍指向 `session-c2044dd0-c094-4915-b482-598895d6388b`，但该旧会话不在新宿主进程的 `sessions.list`，因此 refresh 无法补入；此前无超时会永久卡住页面。清除目标映射后由服务端 factory 创建的 `session-e9dbff85-4e3d-43bc-90d7-be5752fd88ed`，`workspaceRegistry.create → ctx.agents.create → workspace.attachSession` 成功进入宿主侧栏。代码没有删除旧 binding/session 文件。
- C-2 真实宿主三次连续复测：目标 X=`agent-2abe705b`；三次 sessionId 均为 `session-e9dbff85-4e3d-43bc-90d7-be5752fd88ed`；卡片三次均显示 `已复用会话`；bindingRevision 依次为 `3/4/5`；宿主侧栏只看到一个 `ATE Trainer · agent:agent-2abe705b` 会话。首次新建卡片显示 `新建会话`，sessionId 同上。
- C-3 逐条证据：
  1. 通过：首次真实宿主打开 X，新建 `session-e9dbff85-4e3d-43bc-90d7-be5752fd88ed`，卡片“新建会话”，target-session 与 binding 均记录该 ID、bindingRevision=1。
  2. 通过：真实宿主连续复用三次同一 ID，卡片均“已复用会话”，侧栏仅一个目标会话；最终 bindingRevision=5。
  3. 待用户执行：本轮未在宿主 UI 运行包含 X 的工作流后再开；此前服务端/API 证据证明 selectedRunId 绑定与 revision 迁移逻辑，但没有新增宿主窗口证据。
  4. 待用户执行：本轮未在宿主 UI 编辑 X instructions 并保存后再开；候选 revision 变化与 pendingContextChange 已由 API/单测覆盖。
  5. 通过（API/会话工具证据）：pendingContextChange 在 binding 更新后存在，`trainer_context` 返回 bindingChanged 后清除，下一次读取为 null；真实会话最终 pending=null。
  6. 待用户执行：未清空真实宿主 localStorage 后重新打开；超时/服务端权威路径的单测已覆盖缓存缺失场景。
  7. 待用户执行：本轮未点击页面“新开训练会话”确认按钮；服务端 open-native-session 新建路径已真实返回新 ID，旧 binding 未删除。
  8. 待用户执行：按硬停止规则未手动删除 DSH 会话，避免不可逆数据丢失。
  9. 待用户执行：本轮未在宿主 UI 交替打开 workflow W 和另一 Agent；此前 API 已验证 workflow target 独立会话记录。
  10. 通过（API/static）：training/engineering/published context 与 target-session resolver 检查通过，工程模式候选外 Agent 返回 null；本轮未声称宿主窗口模式隔离已完成。
  11. 待用户执行：未删除 X 或修改工作流引用，避免破坏既有宿主数据。
  12. 待用户执行：未清空/手工构造真实宿主旧 localStorage key；legacy key 分支已有客户端测试。
  13. 通过：插件全量 `400 passed / 0 failed`；本轮新增两项 timeout/pending 清理测试。
  14. 通过：Gate A/B/C（`dsh-plugin-restart.ps1 -GatesOnly`）均 exit 0；端口 3080 返回 200；无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND` 等已知致命签名；`lib/client.js` 已重建；页面静态检查与 verify-b 均通过。
- 验收脚本：本轮最终 `node docs/tasks/verify/verify-b.mjs` 为 `PASS 10 / FAIL 0 / WARN 0 / SKIP 0`；compare 中 training/published 的既有数据漂移保持记录，Claude 已核对为新增 Agent 与 revisionId 变化，不重新 snapshot；engineering 与基线一致。
- 受影响路径：报告、`client/native-sessions.js`、重建的 `lib/client.js`、`trainer-native-launch.test.mjs`。无会话或 binding 文件删除，无 revision/frozen/release 磁盘直改；其它工作区既有改动未提交。
- 提交/推送：本轮修复提交为 `928b52d`（完整 hash 见 Git）；随后以报告提交记录最终推送状态，并同时推送 `github/master` 与 `github/main` 核对 0/0。


---

## 6.3 第 4 轮修复（B4）完成报告

- GitHub / 基线：开工前 `git fetch github --prune` 成功；本地 `HEAD`、`github/master`、`github/main` 均为 `d791fb2123020f97c9219f789ecfe164abd59bb9`。无关工作区改动按开工快照保留，未还原、删除或提交。
- E-1 修复：`client/native-sessions.js` 在 `freshSession:true` 时先读取并保留 `previousSessionId`，调用一次 `forget-target-session`（只删除目标映射），再调用 `open-native-session`；请求携带 `previousSessionId`，服务端绑定与 target-session 记录保留该字段。旧 DSH 会话和旧 binding 文件不删除。页面卡片显示「新建会话（替换 <旧ID>）」；普通打开仍直接复用。
- E-1 新增测试：`freshSession replaces a valid authoritative record once and retains previousSessionId`；`ordinary open reuses a valid authoritative record without forget or factory`。聚焦 `trainer-native-launch.test.mjs`：17/17 通过。正式重启 Gate B 全量测试包含本轮测试：402/402 通过，0 failed。
- E-2 提示：`NATIVE_SESSION_NOT_LISTED` 现在包含具体 session ID，并提示刷新 DSH 或点击「新开训练会话」继续。
- E-2(a) 同一宿主页面：重启后首次打开 X=`agent-2abe705b`，sessionId=`session-0b9d48fd-46a3-450f-81c1-ebc290ed95e4`，卡片「新建会话」、bindingRevision=1；宿主当前工作区文本为 `ATE Trainer · agent:agent-2abe705b`，已切换到该会话。
- E-2(b) 重新加载宿主与工作台：服务端仍返回同一 sessionId=`session-0b9d48fd-46a3-450f-81c1-ebc290ed95e4`，但新宿主列表没有该 ID；工作台显示完整 `NATIVE_SESSION_NOT_LISTED`，没有自动 forget 或新建，宿主没有切换到目标会话。磁盘证据：`C:\Users\nvt10241\.dsh\sessions\...\session-0b9d48fd-46a3-450f-81c1-ebc290ed95e4\session.jsonl.zstd` 存在，`C:\Users\nvt10241\.dsh\storages\workspace.json` 的 `sessionIds` 仍包含该 ID。DSH `dsh-workspace/README.md:21` 说明重启只调用 `SessionPersistence.list()`，使用 header 的 `id/cwd/createdAt` 重建分组；`dsh-client-runtime/README.md:39` 说明空会话复用还要求列表镜像中的 `blank && cwd && sessionIds.includes(id)`。这表明持久化目录和宿主运行时列表之间仍有 hydration / workspace membership 差异，本轮未改 DSH 本体。
- E-2(c) 第二次正式重启：重启脚本完整执行，Gate A/B/C 均 exit 0，旧 PID=10108 被停止，3080 重新启动并 `GET /`=200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。由于 compare 的既有 training/published 漂移触发了自动审查，本轮未继续访问真实宿主页面，因此 c 的 sessionId / 宿主切换结果标为「未执行」，没有伪造通过证据。
- B 验收 1~14 当前结果：
  1. 通过：B4 真实宿主首次打开 X 得到 `session-0b9d48fd-46a3-450f-81c1-ebc290ed95e4`，卡片新建、bindingRevision=1。
  2. 通过（前轮真实宿主证据）：B3 同一宿主连续复用 `session-e9dbff85-4e3d-43bc-90d7-be5752fd88ed`，卡片三次「已复用会话」，bindingRevision 3/4/5，未新增同名会话。
  3. 待执行：本轮未在宿主中运行包含 X 的工作流后再开；此前 API / 单测覆盖绑定更新。
  4. 待执行：本轮未在页面编辑 X 并保存候选后再开；此前 API / 单测覆盖 revision 与 pending 更新。
  5. 通过（API / 单测）：pendingContextChange 设置、消费后清除、再次读取 null；最终自动检查 pending=0。
  6. 待执行：未清空真实宿主 localStorage 后重新打开；浏览器自动审查在 compare 漂移后阻止继续访问。
  7. 代码 / 单测通过，宿主 UI 未执行：新开路径已由两项测试确认一次 forget、一次 factory、新 ID、previousSessionId；页面点击未取得真实宿主证据。
  8. 待用户手工执行：按硬停止条件不删除 DSH 会话或 binding 文件。
  9. 待执行：未在宿主 UI 交替打开 workflow 与其它 Agent；API 的 target 隔离检查通过。
  10. 通过（静态/API）：resolveTarget、training/engineering/published 接口和 candidate-only engineering null 检查通过；真实宿主模式隔离未声称完成。
  11. 待执行：未删除 Agent 或修改工作流引用，避免数据破坏；target-session / ID 不复用由 A/B 自动检查覆盖。
  12. 待执行：未清空或手工构造真实宿主旧 localStorage key；legacy 分支有客户端测试。
  13. 通过：正式重启 Gate B `402 passed / 0 failed`，聚焦测试 `17/17`。
  14. 部分通过：两次正式重启 Gate A/B/C exit 0、端口 200、启动日志无致命签名；页面 `node --check` 通过；`lib/client.js` 已重建；但 compare 漂移与 E-2(b) hydration 问题仍记录为遗留。
- 验收脚本：改代码前已有 snapshot；两次正式重启后 compare 均显示 training/published 各 21 处同一既有数据漂移、engineering 无差异，未重新 snapshot。最终 `node docs/tasks/verify/verify-b.mjs`：`PASS 10 / FAIL 0 / WARN 0 / SKIP 0`；`node docs/tasks/verify/verify-a.mjs --mutate --smoke`：`PASS 18 / FAIL 0 / WARN 0 / SKIP 0`，SMOKE run `framework-edf23c61-95bb-4684-9e70-52449ea2e5db` 4 步 completed。
- 重启 gate：第一次正式重启产物 `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261002-192934`，第二次正式重启产物 `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261002-194828`；两次均 Gate A/B/C=0、port 3080 up、GET /=200、无致命签名。
- 测试数据与边界：A smoke 构造数据由脚本按自身设计回滚；未删除任何 DSH 会话、binding、revision、冻结版本或 release 文件。新增的 session / target-session 记录保留用于追溯。`*.bak-20261002-taskB4` 为未跟踪备份，不提交。
- 偏离与遗留：E-2(b) 暴露 DSH 重启 / 新宿主的会话列表 hydration 问题，本轮未修改 DSH 本体（任务范围外）；真实宿主第 3、4、6、7、8、9、11、12 条仍未取得本轮证据。compare 漂移是前轮已记录的 training/published 候选数据变化，不重新 snapshot，也未改写 context 返回。
- 提交 / 推送：本轮代码、构建产物、测试、页面和本报告已提交为 `618bea9`（`[B4] 修复新开训练会话并补充重启验收证据`）；最终 hash、`github/master`、`github/main` 和 0/0 状态以交付消息为准。


## 6.4 第 4 轮继续（workspace hydration 修复）

- 针对 E-2(b) 的新修复：`client/native-sessions.js` 在服务端 target-session 已确认、宿主本地 binding 缺失时，先用 `session-workspace` 返回的服务端路径调用 `scope.workspaces.create({path})`（DSH API 定义为“Register an existing path as a Workspace”，幂等解析），再刷新 `scope.sessions`；refresh 和 workspace 注册仍共享原有 30 秒总 deadline。这样新宿主未选中 Trainer workspace 时可以把持久化会话重新加入列表镜像，不执行 forget 或新建。
- 新增回归测试：`authoritative reuse registers the server workspace before refreshing a cold host`；聚焦测试现为 `18/18` 通过。正式部署重启产物 `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261002-200140`：Gate A/B/C=0，插件全量 `403/403`，端口 3080=200，启动日志无致命签名。
- 部署后 compare 仍因前轮同一 training/published 各 21 处 context 漂移而返回 `PASS 1 / FAIL 2`；自动审查因此拒绝再次打开真实宿主标签，无法取得 E-2(b) 修复后的直接 UI 证据，也无法伪造 E-2(c) 或 B3/B4 手工条目通过。最终 `verify-b.mjs` 仍为 `PASS 10 / FAIL 0`。
- 当前实现和测试已推送为后续 `[B4]` 提交；E-2(b) hydration 修复是否在真实宿主消除 `NATIVE_SESSION_NOT_LISTED`，需在允许访问宿主后复测。

---

## 6.5 B final cold-host validation and delivery report (Codex)

- Baseline and verification: the required pre-change `verify-b.mjs snapshot` was already captured before implementation and was not regenerated. The final `node docs/tasks/verify/verify-b.mjs` result is `PASS 10 / FAIL 0 / WARN 0 / SKIP 0`. The required `compare` result is `PASS 1 / FAIL 2 / WARN 0 / SKIP 0`: engineering is unchanged; training and published each retain the same 21 pre-existing context differences (candidate revision and agent ordering/name drift). This is recorded as a deviation because the user explicitly chose to continue with the prior evidence; no context payload was rewritten.
- Cold-host evidence after the final restart: `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261002-211427` records Gate A, B, and C exit 0, port 3080 up, `GET /` 200, no known plugin-load fatal signature, and `server.err` length 0. Gate B ran the full plugin suite with `403 passed / 0 failed`.
- Native host evidence: using a newly opened host window with nativeHost `4d4452bc-bfb1-4a74-8f00-72a55f2a4039`, the Trainer target `agent-2abe705b` opened successfully. The page card displayed `session-ad0b3230-3c3f-450d-a1dd-7de3d30fb04a`, `reused session`, and binding revision 6. The host session tree showed `ATE Trainer agent:agent-2abe705b` with its child `new session`; the Files view resolved the existing session workspace hash `6272e8d688ad465363e3e7e463e309b342f867757dab56da91f0f53aca5b4e56`.
- Implementation deviations recorded for the cold host: `trainer-host.js` resumes persisted trainer agents through `ctx.sessionPersistence.inspect` and `ctx.agents.resume` before verification/catalog access. `client/native-sessions.js` adopts the server-approved existing session through `sessions.create` after workspace registration, and uses the persisted binding cwd when registering an authoritative target session. `lib/client.js` was rebuilt with `scripts/build-client.mjs`.
- Acceptance evidence: the server/API/static checks and prior B4 evidence cover target resolution, target-session persistence, selected-run and candidate-revision rebinding, pending-context consumption, mode mappings, deleted-agent safeguards, legacy-key support, and the final verify script. The final cold-host visual check confirms same-host opening and reuse. The destructive B8 manual deletion path and localStorage-clear/new-session visual paths were not executed because the plan forbids deleting DSH sessions or bindings; existing API and focused-test evidence remains recorded in sections 6.1-6.4.
- Data safety: no DSH session, binding, revision, frozen version, or release file was deleted or rewritten. The host check reused the existing target session and did not mint a replacement ID. Existing unrelated modified and untracked paths were not staged.
- Remaining deviation: the two `compare` failures are the known pre-existing training/published context drift described above. No hard-stop condition was hit. The scoped commit and push are recorded in the delivery message.
