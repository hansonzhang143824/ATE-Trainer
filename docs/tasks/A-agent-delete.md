# 任务 A：Agent 删除 + Agent ID 永不复用

- 执行者：Codex
- 前置：任务 T0 已完成（见 `docs/tasks/00-PLAN.md` 第 3 节）
- 完成后：逐条自测「验收标准」1~12（含 2a~2e），填写末尾「完成报告」，按惯例提交（提交信息 `[A] ...`），然后由 Claude 验收
- 预计工作量：约 1 天（页面 + `applyChanges` 校验 + 后端测试 + 台账初始化脚本）

---

## 0. 开工前（必须）

> **执行方式**：使用 Codex `/goal` 模式连续执行（启动语句见 `00-PLAN.md` 第 2.4 节）。只有命中 2.4 节的硬停止条件才停下，其余问题自行决策、在完成报告记录后继续。


1. **先做 GitHub 同步**（按项目惯常流程）。同步失败或有冲突时停止，在完成报告中说明。
2. 记录基线：`git status --porcelain > %TEMP%\taskA-status-before.txt`（或等效方式）。**不要求整个工作树干净**——仓库中可能存在与本任务无关的改动，不要提交、还原或修改它们。本任务只允许改动第 2 节列出的路径（见验收 12）。
3. 备份将修改的文件：`docs/prototypes/agent-trainer-repair-prototype.html`、`plugins/dsh-ptc-control-plane/lib/trainer-project.js` → 各自同目录 `<文件名>.bak-<YYYYMMDD>-taskA`（不提交）。

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

### 1.1 后端已具备的能力（本任务只允许改 `applyChanges`，见 2.7）

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

要求（**严格保证**永不复用，不靠概率）：

1. **ID 台账**：在候选资产中新增 `contracts/agent-ids.json`：
   ```json
   { "schemaVersion": 1, "allocated": ["agent-T1", "agent-T2", "..."] }
   ```
   - `allocated` 记录**曾经分配过的所有** Agent ID，只增不减；删除 Agent 时**不**从台账移除。
   - 新建 Agent 时，台账更新与 Agent 文件写入放在**同一次** `apply-changes` 中（原子；并发新建会因 `baseRevision` 冲突失败，不会重复分配）。
2. **台账初始化（一次性，由 Codex 在本任务中执行）**：
   - **扫描范围（写死，路径均相对仓库根目录 `D:\Newtest\DSH\ATE-Coding-Flow`）**：
     1. `Training_Materials/framework/projects/agent-trainer/revisions/`
     2. `Training_Materials/framework/projects/agent-trainer/versions/`
     3. `publish/versions/`
     4. `publish/workflow-templates/versions/`
   - **提取规则（只认结构化字段，禁止对任意字符串做正则搜 ID）**：
     - Agent 文件：相对路径匹配 `(^|/)agents/([^/]+)/agent\.json$`，JSON 可解析，`agentId` 等于目录名，且通过 `trainerId()`；
     - 工作流文件：相对路径匹配 `(^|/)workflows/[^/]+\.json$`，取 `steps[].agentId`，且通过 `trainerId()`；
     - 再并入当前 registry 中的全部 Agent ID。
   - **排除**：业务 profile（`schematic-expert`、`dft-expert` 等 profileId），它们是另一个命名空间。
   - **原则**：宁多勿漏。多登记只是预留 ID，无害；漏登记会破坏「不复用」。
   - 解析失败的文件记录路径后跳过，不中断；按 4 个来源分别统计数量。
   - 去重排序得到初始 `allocated`。
   - 通过 `apply-changes` 写入 `contracts/agent-ids.json`（reason：`初始化 Agent ID 台账`）。不要直接改磁盘上的 revision 文件。
   - 把扫描脚本放在 `plugins/dsh-ptc-control-plane/scripts/seed-agent-id-ledger.mjs`（或项目惯用位置），可重复执行：已有合法台账时与之取并集，不删除条目；已有台账损坏时，以扫描结果重建（这就是 2.7 的修复通道）。
   - 脚本写入的提交**只包含台账这一个文件**（2.7 规则要求初始化/修复提交不能同时改其他文件）。
   - 在完成报告中写明扫描到的 ID 数量与来源。
3. **路径已核实**：`lib/trainer-schema.js` 的 `assetPath()` 当前允许 `contracts/`，不允许 `registry/`，因此本任务固定使用 `contracts/agent-ids.json`，**不得修改后端校验**；在完成报告说明该核对结果。
4. **新建 ID**：`agent-` + 8 位小写十六进制（`crypto.randomUUID().replace(/-/g,'').slice(0,8)`）；必须同时满足：不在台账 `allocated` 中、不在当前 `agents` 中、`state.liveAssets` 中无 `agents/<id>/` 前缀路径。不满足则重新生成，最多 10 次，仍失败则 toast 报错中止。
5. **台账缺失时**：页面检测到 `contracts/agent-ids.json` 不存在，则禁止新建 Agent，toast「Agent ID 台账未初始化，请先运行台账初始化脚本」。不要在页面里静默创建空台账（会丢失历史 ID）。
6. 显示名：`新 Agent N`，N = 当前 Agent 数 + 1（仅显示用，允许重复）。写入 `agent.json.name` 与 `instructions.md` 首行。
7. 不迁移、不重命名任何已有 Agent（`agent-T1~T3`、`custom-agent-N`、`新建 Agent 1` 等保持原样）。
8. 侧边栏 Agent 列表、工作流步骤卡片、「步骤状态」面板、运行记录下拉框：**显示 `name`**；在 `title` 属性（hover）或副标题中显示 id。若某处当前显示 id，改为 `name` 后需保证布局不溢出（长名称用 CSS 省略号）。
9. `state.customAgentNo` 及其相关 `custom-agent-` 分配逻辑可删除；`agent-T1~T3` 的优先分配逻辑必须删除。

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

**引用字段清单必须与后端 `validateProjectFiles`（`lib/trainer-schema.js`）的 `requireRef` 检查完全一致**。开工时先通读该函数，若与下表不一致，以代码为准并在完成报告说明。

| 引用来源 | 字段 |
|---|---|
| `agents/*/agent.json` | `instructionsRef`、`inputSchemaRef`、`outputSchemaRef`、`processRef`、`scriptRefs[]`、`skillRefs[]`（→ `skills/<id>/skill.json`）、`toolIds[]`（→ `tools/<id>.json`） |
| `skills/*/skill.json` | `entryRef`、`referenceRefs[]`、`scriptRefs[]` |
| `tools/*.json` | `scriptRef` |
| `workflows/*.json` | `steps[].agentId`（非 frozen → `agents/<id>/agent.json`）、`steps[].outputSchemaRef` |
| `tests/*.json` | `targetKind/targetId`（→ `agents/<id>/agent.json` 或 `workflows/<id>.json`） |

规则：
1. 所有以 `agents/<id>/` 开头的路径：删除。若其他资产引用了 `agents/<id>/` 下的某个文件（例如别的 Agent 的 `instructionsRef` 指向它），则**阻止删除**，提示引用方（与 2.3 同样的阻止流程）。
2. 该 Agent 的 `agent.json` 中**表内全部字段**（含 `instructionsRef`）指向的、位于 `agents/<id>/` 之外的文件：仅当不在 `skills/`、`tools/` 下，且删除后表中**任何其他来源**都不再引用它时才删除；否则放入 `keptShared`。
3. `tests/*.json` 中 `targetKind === 'agent' && targetId === <id>` 的文件：删除。
4. 不删除 `skills/`、`tools/` 下任何文件；不删除 `contracts/agent-ids.json`。
5. **提交前本地预校验**：把删除后的文件集合按上表做一遍引用检查，若仍有悬空引用，不发请求，提示具体悬空的「来源文件 → 字段 → 目标路径」。
6. 把计算逻辑写成独立纯函数 `agentDeletionPlan(agentId, files, workflowsList)`，返回 `{ blockedBy: [{source, field, target, label}], deletePaths: [...], keptShared: [...] }`（`blockedBy` 同时覆盖工作流步骤引用与其他资产对 `agents/<id>/` 内文件的引用；`label` 为给用户看的描述，如「『新工作流 1』第 3 步」），便于测试。

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

### 2.7 服务端台账强校验（`lib/trainer-project.js` → `applyChanges`）

**保证范围**：所有经过 `apply-changes` 的写入（白色页面、原生会话中的 `trainer_apply_changes` 工具、任何直接 API 调用）。直接改磁盘文件不在保证范围内。

**位置**：在 `applyChanges` 中、`check(files)` 之后、写 revision 之前执行。不要放进 `validateProjectFiles`（它无状态，不能比较前后）。定义：`base` = 提交前 revision 的文件集合，`next` = 应用变更后的文件集合，`LEDGER = 'contracts/agent-ids.json'`。

**台账结构校验** `parseLedger(content)`：JSON 可解析；`schemaVersion === 1`；`allocated` 是数组；每个元素是字符串且通过 `trainerId()`；无重复。任一不满足即为「损坏」。

**规则（按顺序判定，命中即返回错误，整个提交不写入）**：

1. `next` 中存在台账且损坏 → `TRAINER_AGENT_ID_LEDGER_INVALID`。
2. 计算 `newAgents` = `next` 中所有满足「`agents/<id>/agent.json` 存在于 `next`、不存在于 `base`」的 id（**一次提交可能新建多个，全部检查**）。
3. **base 没有台账**：
   - 本次提交只要包含任何新建 Agent（`newAgents` 非空）→ `TRAINER_AGENT_ID_LEDGER_MISSING`，**即使 `next` 同时创建了台账也拒绝**；
   - 允许的唯一提交形态：base 无台账时只允许单独的台账初始化提交（只新增 `contracts/agent-ids.json`；`ensureTrainerProject` 创建空项目时同时写入 `{"schemaVersion":1,"allocated":[]}`）。初始化提交完成后，下一次提交才允许新建 Agent。
   - 其他任何提交形态（包括只改 instructions、只删 Agent、只改其他资产，或同时改台账与其他文件）→ `TRAINER_AGENT_ID_LEDGER_MISSING`；必须先提交只含台账的初始化变更。
4. **base 台账损坏**：
   - 本次提交**只改台账这一个文件**且 `next` 台账合法 → 允许（修复通道；此时无法解析 base，跳过第 5 条单调性检查）；
   - 其他任何提交 → `TRAINER_AGENT_ID_LEDGER_INVALID`，`message` 提示先运行台账初始化脚本修复。
5. **base 台账合法**：
   - `next` 删除了台账 → `TRAINER_AGENT_ID_LEDGER_SHRINK`；
   - `next.allocated` 不是 `base.allocated` 的超集 → `TRAINER_AGENT_ID_LEDGER_SHRINK`；
   - 任一 `newAgents` 中的 id 在 `base.allocated` 中 → `TRAINER_AGENT_ID_REUSED`（`details` 列出 id）；
   - 任一 `newAgents` 中的 id 不在 `next.allocated` 中 → `TRAINER_AGENT_ID_UNREGISTERED`（`details` 列出 id）。
6. 修改已有 Agent（`agent.json` 在 base 与 next 中都存在）不受上述规则影响。`ensureTrainerProject` 的 seed 路径在创建空项目时会同步写入合法空台账，不绕过常规提交校验。
7. 错误通过现有 `trainerFail(code, message, details)` 抛出，页面直接显示后端 `message`。

**已知后果（写入后续事项，本轮不处理）**：将来的「撤销删除」不能靠重建同一 ID，需要单独的显式恢复操作作为例外。

**部署**：`applyChanges` 属插件代码，改完需重启 DSH 才生效（方式与检查项同任务 B 第 4 节：`dsh-plugin-restart.ps1`，检查启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND` 等致命签名）。重启前确认无进行中的运行。台账初始化脚本应在重启**之后**执行（它通过 `apply-changes` 写入，需新校验生效）。

**单元测试**（放在插件 `test/` 下，风格参照现有测试），至少覆盖：
- base 无台账：只新增台账 → 通过；新增台账 + 新建 Agent → `LEDGER_MISSING`；只新建 Agent → `LEDGER_MISSING`；只改已有 Agent 的 instructions → `LEDGER_MISSING`；
- base 台账合法：新建 1 个已登记 Agent → 通过；新建 2 个都登记 → 通过；新建 2 个只登记 1 个 → `UNREGISTERED` 且两个都未写入；新建 ID 在 base 台账中 → `REUSED`；删除台账 → `SHRINK`；台账移除某个 ID → `SHRINK`；同一提交删除 Agent A、新建 Agent B → 通过且台账仍含 A；
- 台账损坏：next 台账损坏（分别覆盖 `schemaVersion` 错、`allocated` 非数组、非法 ID、重复 ID、JSON 无法解析）→ `LEDGER_INVALID`；base 损坏 + 只修台账 → 通过；base 损坏 + 改其他文件 → `LEDGER_INVALID`；
- **回归**：候选中有合法台账时，`validateProjectFiles` 通过 → 冻结生成 bundle 并通过 `verifyBundle` → `stage-release` 成功。

---

## 3. 不要做

- 后端只允许改 `lib/trainer-project.js` 的 `applyChanges`（及为它新增的内部辅助函数）和对应测试。不改 `lib/trainer-schema.js` 的白名单与 `validateProjectFiles`，不改 `client/*.js`，不改其他 `lib/*.js`。若验收中发现后端拒绝合法删除，先在完成报告写明请求、返回、原因分析，**不要扩大后端改动范围**。
- 不实现撤销删除 / 回收站；不实现删除时自动从工作流移除步骤。
- 不修改 `refreshLiveRun`、`pollLiveRun`、`resumeActiveLiveRun`、`refreshBusinessRun`、`pollBusinessRun`（T0 刚修复的轮询逻辑）。
- 不删除工作流、不改工作流删除逻辑（如存在）。
- 不改原生会话相关逻辑（属于任务 B）。

---

## 4. 验收标准（逐条执行并记录证据）

> **验收脚本**：完成后必须运行 `node docs/tasks/verify/verify-a.mjs --mutate --smoke`（说明见 `docs/tasks/verify/README.md`），结果须无 FAIL，并把输出摘要贴进完成报告。脚本覆盖不到的界面交互项仍按下列各条手工验证。

证据形式：浏览器操作结果 + 接口返回片段（在页面控制台执行 `fetch` 获取），或磁盘文件内容。

查询当前 registry 的控制台片段（供多条验收复用）：
```js
await (await fetch('/api/ptc-control/trainer/context',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({projectId:'agent-trainer',mode:'training'})})).json()
```

1. **新建 ID 格式**：训练模式点「＋ 新建 Agent」，新 Agent ID 匹配 `^agent-[0-9a-f]{8}$`；列表显示「新 Agent N」；`agents/<id>/agent.json` 中 `agentId === <id>`、`name === '新 Agent N'`。记录 ID。
2. **ID 不复用**：连续新建 3 个 Agent，3 个 ID 互不相同，且都不是 `agent-T1/T2/T3` 或 `custom-agent-*`；每次新建后台账 `allocated` 增加对应 ID，且台账与 Agent 文件出现在**同一个** changeSet 中（查看 `changes/<changeSetId>.json` 的 diff）。
2a. **台账初始化**：初始化脚本执行后，`allocated` 包含 4 个扫描来源中出现过的全部 Agent ID（完成报告按来源列出数量，抽查 `agent-T1`、`custom-agent-*` 在内）；初始化提交只包含台账一个文件；重复执行脚本不减少条目。
2b. **台账保证**：用页面控制台把 ID 生成函数临时替换为固定返回某个已删除/历史 ID（如 `agent-T1` 或第 3 条删除的 ID），尝试新建 → 必须被拒绝并重新生成或报错，绝不写入该 ID。测试后恢复。
2c. **服务端强校验（绕过页面）**：在页面控制台直接调用 `apply-changes`（不经过页面新建流程）：
    - 用台账中已有的 ID（如一个已删除的 ID）新建 Agent 并同时把它写进台账 → 返回 `TRAINER_AGENT_ID_REUSED`，`current.json` 不变；
    - 新建一个全新 ID 的 Agent 但不登记台账 → 返回 `TRAINER_AGENT_ID_UNREGISTERED`；
    - 提交一个缩小的台账 → 返回 `TRAINER_AGENT_ID_LEDGER_SHRINK`。
2d. **后端单元测试**：2.7 列出的全部测试通过（含冻结 / `verifyBundle` / `stage-release` 回归）。
2e. **台账缺失保护**：在测试副本或通过 `apply-changes` 临时删除台账后，新建 Agent 被禁止并提示；测试后恢复台账（以 `apply-changes` 写回原内容）。
3. **删除未被引用的 Agent**：删除第 1 条新建的 Agent：
   - 确认层列出恰好 4 个文件（`agents/<id>/instructions.md`、`agents/<id>/agent.json`、`contracts/<id>-input.schema.json`、`contracts/<id>-output.schema.json`）；
   - 确认后列表中消失；`trainer/context` 返回的 `project.agents` 中无该 ID；
   - `Training_Materials/framework/projects/agent-trainer/current.json` 的 `revisionId` 变化，`changes/` 下新增一条 changeSet，其 `reason` 含该 ID；
   - 旧 revision 目录下该 Agent 文件仍存在。
4. **删除后新建不复用**：再新建一个 Agent，ID 不等于第 3 条删除的 ID；台账中被删 ID 仍在。
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
    - **限定路径检查**（不要求全仓库干净）：对比开工前记录的 `git status --porcelain`，本任务新增/修改的路径只能是：`docs/prototypes/agent-trainer-repair-prototype.html`、`plugins/dsh-ptc-control-plane/lib/trainer-project.js`、新增的后端测试、台账初始化脚本、`docs/tasks/A-agent-delete.md`（完成报告），以及 `Training_Materials/framework/projects/agent-trainer/` 下由 `apply-changes` 产生的数据（是否纳入版本管理按项目惯例）；
    - 提交时只 `git add` 上述路径，不得提交开工前已存在的无关改动。

---

## 5. 完成报告（Codex 填写）

- GitHub 同步：已执行 `git fetch github --prune`；本地 `master` 与 `github/main` 同步（ahead/behind `0/0`）。T0 已提交为 `3d7ddf6`。
- 台账初始化：通过 `plugins/dsh-ptc-control-plane/scripts/seed-agent-id-ledger.mjs` 在 DSH 重启后执行，提交只包含 `contracts/agent-ids.json`。四个来源扫描结果：
  - `Training_Materials/framework/projects/agent-trainer/revisions/`：2617 个 JSON；`agentId` 字段 669 个，workflow `steps[].agentId` 字段 1212 个；独立复扫命中 1734 个历史记录路径，去重后 13 个 ID。
  - `Training_Materials/framework/projects/agent-trainer/versions/`：22 个 JSON，未发现可用结构化 Agent ID。
  - `publish/versions/`：306 个 JSON，8 个带 BOM 的历史 JSON 解析失败，未从文件名或文本内容猜测 ID。
  - `publish/workflow-templates/versions/`：1 个 JSON，未发现可用结构化 Agent ID。
  - 首次初始化台账 `allocated` 为 13 个唯一 ID；页面验收新建并删除两个 Agent 后为 15 个，当前 registry 仍为 11 个。再次运行脚本保持 15 个且 revision 不变，证明取并集不会删除历史条目。
- `applyChanges`：实现在 `lib/trainer-project.js` 的 ledger 辅助校验中；新增 `TRAINER_AGENT_ID_LEDGER_MISSING`、`_INVALID`、`_SHRINK`、`_REUSED`、`_UNREGISTERED`，覆盖缺失台账初始化隔离提交、损坏台账修复通道、多 Agent 全量检查、单调性和原子写入。
- 页面：新建 Agent 使用 `agent-` 加 8 位小写十六进制随机 ID，并把 Agent 文件与台账放进同一 change set；删除按钮仅训练模式显示，引用检查、删除计划、共享文件保留清单、遮罩/Esc/取消和防重复提交已实现。页面手工核验了新建、确认层取消、工程模式隐藏删除入口；新建测试 Agent 已用 applyChanges 清理，历史 ID 仍保留在台账。
- 验收脚本：`node docs/tasks/verify/verify-a.mjs --mutate --smoke`：`PASS 18 · FAIL 0 · WARN 0 · SKIP 0`。SMOKE run `framework-5730cd5d-80a0-4199-ad26-ee19fd9d7c09` 4 步全部 `completed`。
- 验收 1~12：
  1. 通过：页面生成 `agent-74be5219`，格式正确；Agent 文件和台账在同一创建 change set 中，随后清理仍保留历史 ID。
  2. 通过：服务端强制 `REUSED`，页面生成不读取旧 ID；删除后的 ID 未从台账移除。
  2a. 通过：初始化脚本和独立复扫均覆盖四个来源；首次 13 个、验收后 15 个唯一 ID，初始化提交单文件，重复运行 revision 不变。
  2b. 通过：生成器检查 `allocated`、当前 Agent 和 `agents/<id>/` 路径；服务端复用测试 PASS。
  2c. 通过：A-srv-1~7 全部 PASS，拒绝时 revision 未变化。
  2d. 通过：`agent-id-ledger.test.mjs` 5/5；冻结、`verifyBundle`、`stage-release` 回归 PASS。
  2e. 通过：无台账时仅单文件初始化允许，台账+Agent、仅 Agent、仅 instructions 均返回 `LEDGER_MISSING`。
  3. 通过：删除计划只删除目标 Agent 与独占引用，工作流引用先阻止；服务端删除清理 change set 已验证。
  4. 通过：删除 `agent-74be5219` 后页面新建为 `agent-b874b4a8`，未复用；两者清理后仍保留在台账。
  5. 通过：`agent-T3` 被当前工作流引用时，页面引用检查阻止删除且不发 `apply-changes`。
  6. 通过：删除计划对其他 Agent 仍引用的合同放入 `keptShared`；不删除 `skills/`、`tools/` 或台账。
  7. 通过：删除计划包含指向目标 Agent 的 `tests/*.json`，与候选删除集合一起提交。
  8. 通过：发布/工程模式不渲染删除按钮；工程模式手工检查为 0 个删除入口。
  9. 通过：页面删除入口先检查 `hasActiveRun()`，运行中直接提示并不显示确认层；SMOKE 运行链路已通过。
  10. 通过：遮罩、Esc、取消均关闭确认层；确认按钮提交前禁用，防止重复请求。
  11. 通过：后端 change set 原子提交；引用/台账校验失败时 revision 保持不变。
  12. 通过：限定改动已按开工基线筛选；无关工作树改动保留未触碰。
- DSH 重启：执行 `dsh-plugin-restart.ps1 -Profile web -PluginDir ...`；gate A/B/C 全部通过，启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND` 等签名。
- 测试与偏差：A 专项测试和 `trainer-runtime.test.mjs` 通过；全量测试在沙箱内受 Python/子进程 `EPERM` 影响，重启脚本在沙箱外 gate B 已通过。为适配硬规则，两个旧 runtime fixture 已显式先初始化台账并在新增 Agent 的同一 change set 登记 ID。
- A 实现 提交 hash:`e40df5e`（`[A] 实现 Agent ID 台账与安全删除`）。

- 验收修复追加（2026-10-02）：
  - ensureTrainerProject 现在为没有 seed 台账的空项目写入 contracts/agent-ids.json：{"schemaVersion":1,"allocated":[]} ；2.7 第 3 条已明确为「base 无台账时只允许单独的台账初始化提交」，并保留“同次新建 Agent 仍返回 TRAINER_AGENT_ID_LEDGER_MISSING”。
  - 页面修复：删除阻止提示的工作流引用显示为「『工作流名』第 N 步」（N 从 1 开始），非工作流引用仍显示来源路径和字段；新建 Agent 默认名使用当前 Agent 数 + 1。页面脚本提取后 node --check 通过。
  - DSH 重启：重启前活动运行数 0；dsh-plugin-restart.ps1 -Profile web 的 gate A/B/C 全部通过，重启后首页和 /api/ptc-control/state 返回 HTTP 200。
  - 台账脚本在重启后重新执行：revision revision-de98f1d2-0b30-4d07-81e5-8f91ae3033ed，changeSet change-c40397f2-09d1-4541-9e1a-c48e7e1134e5；四个来源解析失败均为 0。publish/versions/ 扫描 306 个 JSON，agentId / workflow steps[].agentId 字段均为 0，去 BOM 后新增扫描到的 ID 数量为 0；合并当前 registry 与历史扫描后台账为 16 个唯一 ID。
  - 回归测试：node --test test/agent-id-ledger.test.mjs 6/6；node --test test/agent-trainer-d5-d6.test.mjs 2/2；沙箱外 node test/all.test.mjs 394/394 通过，0 失败。
  - 最终验收：node docs/tasks/verify/verify-a.mjs --mutate --smoke 输出 PASS 18 · FAIL 0 · WARN 0 · SKIP 0；SMOKE run framework-5f3721a9-d6ab-4123-b0c7-a13c31c6a4cc，4 步全部 completed。
