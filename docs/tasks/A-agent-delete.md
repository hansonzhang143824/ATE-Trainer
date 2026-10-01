# 任务 A：Agent 删除 + Agent ID 永不复用

- 执行者：Codex
- 前置：任务 T0 已完成（见 `docs/tasks/00-PLAN.md` 第 3 节）
- 完成后：逐条自测「验收标准」1~12，填写末尾「完成报告」，按惯例提交（提交信息 `[A] ...`），然后由 Claude 验收
- 预计工作量：半天以内

---

## 0. 开工前（必须）

1. **先做 GitLab 同步**（按项目惯常流程）。同步失败或有冲突时停止，在完成报告中说明。
2. `git status` 确认工作区干净（T0 已提交）。
3. 备份将修改的文件：`docs/prototypes/agent-trainer-repair-prototype.html` → 同目录 `agent-trainer-repair-prototype.html.bak-<YYYYMMDD>-taskA`（不提交）。

---

## 1. 背景

Agent Trainer 白色工作台：`http://127.0.0.1:3080/agent-trainer`。

- 页面源码：`docs/prototypes/agent-trainer-repair-prototype.html`，单文件内联脚本。由插件 `plugins/dsh-ptc-control-plane/lib/trainer-host.js` 在每次请求时 `readFileSync` 返回，**改完刷新页面即生效，不需要重启 DSH**。
- 候选资产存储：`Training_Materials/framework/projects/agent-trainer/`
  - `current.json`：当前 candidate revision 指针；
  - `revisions/<revisionId>/`：不可变快照，`revision.json` 记录文件清单与 sha256；
  - `changes/<changeSetId>.json`：每次 `apply-changes` 的变更记录。
- 一个 Agent 由 `candidateAgentFiles(id, name)` 生成 4 个文件：
  - `agents/<id>/instructions.md`
  - `agents/<id>/agent.json`（`agentId, name, instructionsRef, skillRefs[], toolIds[], inputSchemaRef, outputSchemaRef`，可能还有 `processRef`、`scriptRefs[]`）
  - `contracts/<id>-input.schema.json`
  - `contracts/<id>-output.schema.json`

### 1.1 后端已具备的能力（本任务不改后端）

- `POST /api/ptc-control/trainer/apply-changes`，body `{projectId:'agent-trainer', requestId, baseRevision, reason, changes:[{path, content}]}`：
  - `content: null` = 删除该文件；
  - 一次提交原子生成新 revision；`baseRevision` 不是当前 revision 时返回 `TRAINER_REVISION_CONFLICT`。
  - 实现：`lib/trainer-project.js` → `applyChanges`。
- 提交前做完整性校验（`lib/trainer-schema.js` → `validateProjectFiles`），不通过返回 `TRAINER_PROJECT_INVALID`，整个提交被拒。会导致删除失败的引用：
  - 工作流步骤（`agentVersion.kind !== 'frozen'`）引用的 `agents/<agentId>/agent.json`；
  - 步骤 `outputSchemaRef` 引用的文件；
  - 其他 `agent.json` 的 `instructionsRef / inputSchemaRef / outputSchemaRef / processRef / scriptRefs`；
  - `skills/*/skill.json` 的 `entryRef / referenceRefs / scriptRefs`；
  - `tests/*.json` 指向的 `agents/<targetId>/agent.json`。
- 已发布 / 已激活版本使用冻结 bundle（`versions/`、releases），**不受候选中删除影响**。
- ID 校验：`trainerId()` 要求 `^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$`，且不能是 Windows 保留名。

### 1.2 页面中可复用的函数 / 状态

- `addAgent()`：当前新建逻辑（需修改）。
- `candidateAgentFiles(id, name)`：生成新 Agent 文件。
- `persistCandidateChanges(changes, reason)`：调用 `apply-changes`（带 `baseRevision`），成功后 `loadLiveContext()` 刷新。
- `loadLiveContext()`：从 `trainer/context` + `trainer/assets` 重建 `agents`、`workflows`、`state.liveAssets`（当前 revision 全部文件 `{path: content}`）。
- `isTraining()`：是否训练模式；`state.product` 取值 `training / release / engineering`。
- `hasActiveRun()`：是否有运行进行中。
- `showToast(text)`、`render()`、`esc(v)`（HTML 转义）。
- `workflows`：`{ <name>: { workflowId, name, steps: [agentId...], manifest } }`；`agents`：`{ <id>: { id, name, ... } }`。

---

## 2. 要做的事

### 2.1 Agent ID 永不复用（先做）

现状问题：`addAgent` 优先补 `agent-T1/T2/T3` 空缺，再用 `custom-agent-N`，`state.customAgentNo` 每次刷新从 1 开始。有删除后，新 Agent 会拿到已删 Agent 的 ID。

要求：
1. 新建 Agent ID 格式：`agent-` + 8 位小写十六进制，来源 `crypto.randomUUID().replace(/-/g,'').slice(0,8)`。
2. 生成后检查：当前 `agents` 中不存在；`state.liveAssets` 中不存在以 `agents/<id>/` 开头的路径。冲突则重新生成，最多 5 次，仍冲突则 toast 报错并中止。
3. 不需要检查历史 revision 中的 ID（8 位十六进制随机空间约 43 亿，碰撞可忽略），不要为此新增后端接口。
4. 显示名：`新 Agent N`，N = 当前 Agent 数 + 1（仅显示用，允许重复）。写入 `agent.json.name` 与 `instructions.md` 首行。
5. 不迁移、不重命名任何已有 Agent（`agent-T1~T3`、`custom-agent-N`、`新建 Agent 1` 等保持原样）。
6. 侧边栏 Agent 列表、工作流步骤卡片、「步骤状态」面板、运行记录下拉框：**显示 `name`**；在 `title` 属性（hover）或副标题中显示 id。若某处当前显示 id，改为 `name` 后需保证布局不溢出（长名称用 CSS 省略号）。
7. `state.customAgentNo` 及其相关 `custom-agent-` 分配逻辑可删除；`agent-T1~T3` 的优先分配逻辑必须删除。

### 2.2 删除入口

1. 侧边栏每个 Agent 项右侧加删除按钮（文字「删除」或图标 `×`，`aria-label="删除 Agent <name>"`），仅在 `isTraining()` 为真时渲染。
2. 点击删除按钮不能触发「选中该 Agent」（`event.stopPropagation()`）。
3. 以下情况点击后不进入确认流程，只 toast 提示：
   - `hasActiveRun()` 为真：「当前有运行进行中，完成后再删除 Agent。」
   - `state.liveError` 非空（未接通 registry）：「Trainer registry 未加载，无法删除。」

### 2.3 引用检查（阻止删除）

1. 遍历 `workflows`，收集 `steps` 中包含该 agentId 的所有位置：`{workflowName, stepIndex(从 1 开始)}`。
2. 再遍历 `state.liveAssets` 中 `workflows/*.json` 原始 manifest 的 `steps[].agentId`（防止 `workflows` 对象因过滤丢失引用）。
3. 有任何引用：**不调用 `apply-changes`**，显示提示（toast 或确认层的只读模式）：
   > 无法删除「<name>」：它被以下工作流使用：『新工作流 1』第 3 步、…。请先在工作流中用 × 移除该步骤。

### 2.4 计算待删除文件（只基于 `state.liveAssets`）

1. 所有以 `agents/<id>/` 开头的路径。
2. 该 Agent `agent.json` 中的 `inputSchemaRef`、`outputSchemaRef`、`processRef`、`scriptRefs[]` 指向的文件，**仅当**：
   - 不位于 `skills/`、`tools/` 下；且
   - 没有任何其他文件引用它。「其他文件」包括：其他 Agent 的 `agent.json`（同上 4 类字段）、`skills/*/skill.json`（`entryRef / referenceRefs / scriptRefs`）、`tools/*.json`（`scriptRef`）、`workflows/*.json` 中 `steps[].outputSchemaRef`。
3. `tests/*.json` 中 `targetKind === 'agent' && targetId === <id>` 的文件。
4. 不删除 `skills/`、`tools/` 下任何文件。
5. 把计算逻辑写成独立纯函数 `agentDeletionPlan(agentId, files, workflowsList)`，返回 `{ blockedBy: [{workflowName, stepIndex}], deletePaths: [...], keptShared: [...] }`，便于测试。

### 2.5 确认层

1. 使用页面内自定义模态层（遮罩 + 卡片），**禁止使用 `window.confirm` / `alert` / `prompt`**。
2. 内容：
   - 标题：「删除 Agent『<name>』？」
   - ID：`<id>`
   - 将删除的文件列表（`deletePaths`），以及「保留（被其他资产共享）」列表（`keptShared`，为空则不显示）
   - 说明：「删除只影响训练候选；已发布版本不受影响。旧 revision 中仍保留该 Agent。」
   - 按钮：「取消」「确认删除」（危险色）。
3. Esc 键与点击遮罩等同「取消」。
4. 「确认删除」点击后禁用按钮防重复提交，显示「删除中…」。

### 2.6 提交与结果处理

1. 调用 `persistCandidateChanges(deletePaths.map(path => ({ path, content: null })), '用户通过白色 Agent Trainer 删除 Agent <id>（<name>）')`。
2. 成功：
   - 关闭确认层；
   - 若被删的是 `state.selected` / `state.recordAgent`，切到剩余第一个 Agent（无则 `null`）；
   - `render()`；toast：「已删除 <name>。旧 revision 中仍保留其历史。」
3. 失败（含 `TRAINER_REVISION_CONFLICT`、`TRAINER_PROJECT_INVALID`）：
   - 确认层保留并显示错误信息（后端 `error.message` 原文）；
   - 冲突类错误额外提示「候选已被其他操作更新，请关闭后重试」并调用 `loadLiveContext()`；
   - 不修改本地 `agents` / `workflows`。

---

## 3. 不要做

- 不改 `plugins/dsh-ptc-control-plane/lib/*.js`、`client/*.js`。若验收中发现后端拒绝合法删除，先在完成报告写明请求、返回、原因分析，**不要自行改后端**。
- 不实现撤销删除 / 回收站；不实现删除时自动从工作流移除步骤。
- 不修改 `refreshLiveRun`、`pollLiveRun`、`resumeActiveLiveRun`、`refreshBusinessRun`、`pollBusinessRun`（T0 刚修复的轮询逻辑）。
- 不删除工作流、不改工作流删除逻辑（如存在）。
- 不改原生会话相关逻辑（属于任务 B）。

---

## 4. 验收标准（逐条执行并记录证据）

证据形式：浏览器操作结果 + 接口返回片段（在页面控制台执行 `fetch` 获取），或磁盘文件内容。

查询当前 registry 的控制台片段（供多条验收复用）：
```js
await (await fetch('/api/ptc-control/trainer/context',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({projectId:'agent-trainer',mode:'training'})})).json()
```

1. **新建 ID 格式**：训练模式点「＋ 新建 Agent」，新 Agent ID 匹配 `^agent-[0-9a-f]{8}$`；列表显示「新 Agent N」；`agents/<id>/agent.json` 中 `agentId === <id>`、`name === '新 Agent N'`。记录 ID。
2. **ID 不复用**：连续新建 3 个 Agent，3 个 ID 互不相同，且都不是 `agent-T1/T2/T3` 或 `custom-agent-*`。
3. **删除未被引用的 Agent**：删除第 1 条新建的 Agent：
   - 确认层列出恰好 4 个文件（`agents/<id>/instructions.md`、`agents/<id>/agent.json`、`contracts/<id>-input.schema.json`、`contracts/<id>-output.schema.json`）；
   - 确认后列表中消失；`trainer/context` 返回的 `project.agents` 中无该 ID；
   - `Training_Materials/framework/projects/agent-trainer/current.json` 的 `revisionId` 变化，`changes/` 下新增一条 changeSet，其 `reason` 含该 ID；
   - 旧 revision 目录下该 Agent 文件仍存在。
4. **删除后新建不复用**：再新建一个 Agent，ID 不等于第 3 条删除的 ID。
5. **被引用时阻止**：尝试删除 `agent-T3`（被「新工作流 1」第 3 步使用）：
   - 出现提示，内容含「新工作流 1」与「第 3 步」；
   - 浏览器网络请求中**没有**发出 `apply-changes`；
   - `current.json` 未变化。
6. **共享文件保留**：构造一个共享场景（手动或通过 `apply-changes` 让一个新 Agent 的 `agent.json.inputSchemaRef` 指向另一个 Agent 的 input contract），删除其中一个 Agent：确认层「保留」列表中出现该共享 contract，删除后该文件仍在 `trainer/assets` 中，另一 Agent 正常。测试完成后清理构造的数据（删除测试 Agent）。
7. **tests 联动**：若当前候选存在 `tests/*.json` 指向某个可删除 Agent，删除后该 test 文件一并删除；若当前无此类文件，构造一个后验证，再清理。
8. **只读模式无入口**：切换到发布模式、工程模式，Agent 列表中没有删除按钮。
9. **运行中禁止**：点「▶ 运行 SMOKE_ONLY」后立即点某个未被引用 Agent 的删除，出现「当前有运行进行中」提示且无确认层。
10. **确认层交互**：Esc、点遮罩、点「取消」均关闭且不提交；连续快速点两次「确认删除」只发出 1 次 `apply-changes`。
11. **回归**：完成上述操作后，运行「新工作流 1」SMOKE_ONLY，4 步全部 completed，页面「运行记录」显示 completed（不卡「运行中」）。
12. **代码质量**：
    - 提取页面 `<script>` 内容后 `node --check` 通过；
    - 页面刷新后浏览器控制台无新增 error；
    - 代码中无 `window.confirm`、`alert(`、`prompt(`；
    - `git diff --stat` 只包含 `docs/prototypes/agent-trainer-repair-prototype.html`（及本任务书的完成报告）。

---

## 5. 完成报告（Codex 填写）

- GitLab 同步结果：
- 改动摘要（函数级）：
- 新增函数列表：
- 验收 1~12 结果（每条：通过/失败 + 证据）：
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
- 测试中构造并已清理的数据：
- 偏离本任务书之处及原因：
- 遗留问题：
- 提交 hash：
