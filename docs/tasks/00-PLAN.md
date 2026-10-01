# Agent Trainer 迭代计划：Agent 删除 + 专家固定训练会话

- 项目根目录：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录）
- 编写：Claude（2026-10-01）
- 执行分工：**Codex 负责实现与自测（主力）**，**Claude 负责任务书、阶段验收与疑难诊断**
- 相关任务书：
  - 任务 T0（基线同步）：写在本文件第 3 节，无单独文件
  - `docs/tasks/A-agent-delete.md`
  - `docs/tasks/B-expert-fixed-session.md`

---

## 1. 背景

### 1.1 已完成（Claude，2026-10-01）

问题：工作流验证时 agent-T3 一直显示「运行中」不结束。

诊断结论：后端运行早已 `completed`（4 步全部完成，约 63 秒），是**前端轮询有次数上限**（`refreshLiveRun` 30 次 ≈ 30 秒）导致界面停在最后一次看到的状态。

已修改 `docs/prototypes/agent-trainer-repair-prototype.html`（**尚未提交到 Git**）：

1. `refreshLiveRun`（SMOKE / framework run）：改为按时间轮询，最长 15 分钟，间隔 1s→5s 递增，连续 5 次网络错误才放弃；新增 `pollLiveRun`，用 token 防止重复轮询链；页面加载后 `resumeActiveLiveRun` 自动接回进行中的 framework run。
2. `refreshBusinessRun`（BUSINESS_ONLY）：改为按时间轮询，最长 60 分钟，间隔 2s→10s 递增；运行 2 分钟内未出现在状态列表则停止；新增 `pollBusinessRun`。**未做**业务运行的刷新后自动接回（`/api/ptc-control/state` 的 `trainingRuns` 混有 framework run 且大量 `status: unknown`，不可靠）。
3. 已验证：SMOKE_ONLY 完整运行约 63 秒，页面跟到 4 步全部 completed。BUSINESS_ONLY 未实际运行验证。

同时产生的本地文件：
- `docs/prototypes/agent-trainer-repair-prototype.html.bak-20261001-poll`（修改前备份，**不要提交**）
- `docs/tasks/*.md`（本计划与任务书）

### 1.2 本轮要解决的问题

| 编号 | 问题 | 影响 |
|---|---|---|
| A | 只能新建 Agent，不能删除；且新建 ID 会复用（`agent-T1~T3` 补空缺、`custom-agent-N` 计数每次刷新从 1 开始） | 无法清理；一旦能删除，新 Agent 会继承已删 Agent 的运行记录、发布记录、会话绑定 |
| B | 训练专家时，复用会话的 key 包含 `candidateRevision` 与 `selectedRunId`，保存候选或跑一次运行后就新开 DSH 原生会话；映射只存在宿主窗口 localStorage | 训练过程散落在大量会话里，换窗口/清缓存后找不回 |

### 1.3 已确认的设计决策（用户已接受）

1. **Agent 删除**：被工作流引用时**阻止删除**（不做级联移除）；删除走现有 `apply-changes`（`content: null`），旧 revision 不可变保留，作为将来恢复的基础；本轮**不做**撤销/回收站。
2. **Agent ID 永不复用（严格保证）**：候选资产中维护 ID 台账 `contracts/agent-ids.json`（只增不减，由历史 revision 一次性初始化；`contracts/` 是当前后端允许的资产前缀），新建 Agent 用随机 ID `agent-xxxxxxxx` 且必须不在台账中，台账与 Agent 文件同一次 `apply-changes` 原子写入；显示名存于 `agent.json.name`；存量 ID 不迁移。**保证范围是所有经过 `apply-changes` 的写入**（页面、原生会话的 `trainer_apply_changes` 工具、直接 API 调用），由服务端在 `applyChanges` 中强校验；A 因此允许修改 `lib/trainer-project.js` 的 `applyChanges` 及对应测试（细则见 A 任务书 2.7）。base 没有台账时只允许单独的初始化/修复提交，同时新建 Agent 一律拒绝。
3. **专家固定会话**：同一 `projectId + mode + targetKind + targetId + presetId` 只对应一个长期 DSH 会话；对应关系存服务端；复用时把绑定更新到最新 revision / runId 并让会话知道上下文已变；提供「新开训练会话」按钮。会话键固定为 `projectId + mode + targetKind + targetId + presetId`；revision / runId / release 变化只更新绑定并产生 `pendingContextChange`。
4. **统一目标解析**：新增唯一函数 `resolveTarget()`，供 `context`、`session-workspace`、`target-session`、`open-native-session` 共用；training 查当前候选，engineering 查激活 release（含被工作流间接包含的 Agent），返回结构统一为 `{source, revisionId, frozenVersionId, releaseId, via}`，`lastResolved` 与 `pendingContextChange` 使用同一来源结构。
5. **发布模式延期**：当前代码没有可查询的「当前审核中的 staged release」（`stageRelease()` 直接写 `publish/versions/release-*.json`，`listReleases()` 只返回 `releases` 与 `active`）。本轮 B 中 published 的 resolver 与现有 `context` 保持一致，不改变产品语义；staged/current-review 指针单独立项（见第 9 节）。
6. **串行**：全局短 `serial()` 只包短的读改写；内部实现与对外 operation 分两层防死锁；`openNativeSession` 不进全局队列，改为按会话键加锁，同一目标只创建一个 DSH 会话。
7. **`pendingContextChange` 删除硬规则**：只有来源标识完全相同**且** `fromRunId === toRunId` 时才删除；来源相同但 runId 不同必须保留。

---

## 1.4 最终执行顺序（写死）

1. Claude 输出 v3 最终任务书（本版）；
2. 用户只核对 v3 diff；
3. GitHub 同步（修复本地 Git 状态后完成）；
4. T0（Codex）；
5. A（Codex）；
6. Claude 验收 A；
7. B（Codex）；
8. Claude 验收 B。

前一步未完成或验收未通过，不进入下一步。

---

## 2. 角色与交接协议

### 2.1 Codex（实现）

- **每个任务开工前必须先做 GitHub 同步**（按项目惯常流程）。同步失败、有冲突或工作区状态与任务书描述不符时，**停止并在完成报告中说明**，不要自行强推或丢弃本地改动。
- 严格按任务书范围改动；需要偏离时，在完成报告「偏离」一栏写明原因。
- 每个任务完成后：
  1. 逐条执行验收标准并记录实际结果（通过 / 失败 + 证据：命令输出、接口返回片段、文件路径）；
  2. 填写任务书末尾「完成报告」；
  3. 按项目惯例提交，提交信息以任务编号开头（如 `[A] Agent 删除与 ID 不复用`）。
- 遇到问题时按第 2.4 节「连续执行规则」处理：只有命中硬停止条件才停下，其余情况自行决策、记录后继续。

### 2.2 Claude（验收与诊断）

- 不参与日常实现，只在以下时点介入：
  - **验收 A**：Codex 报告 A 完成后，读完成报告和改动 diff，在 Claude 内置浏览器中对 `http://127.0.0.1:3080/agent-trainer` 做端到端抽查（见第 5 节）。
  - **验收 B**：同上（见第 6 节）。
  - **疑难诊断**：Codex 阻塞且用户转来时。
- 为节省额度：Claude 验收以抽查关键路径为主，不重复执行 Codex 已有证据的全部单项；验收结论只给「通过」或「不通过 + 具体问题清单」，修复仍交回 Codex。

### 2.3 用户

- 在 Codex 中启动任务（工作目录 `D:\Newtest\DSH\ATE-Coding-Flow`），指令模板：
  > 先做 GitHub 同步。然后按 docs/tasks/<任务文件> 执行，完成后逐条自测验收标准，填写文件末尾的完成报告并提交。
- Codex 完成后告诉 Claude「<任务编号> 做完了」，Claude 开始验收。
- 用户已预先授权 Codex 在 A、B 中自行重启 DSH（按任务书的重启与检查步骤），不需要再逐次确认。


### 2.4 连续执行规则（Codex 使用 `/goal` 模式）

A、B 各需约 1~1.5 天，**必须用 Codex 的 `/goal` 模式连续执行**，不要每完成一小步就停下等确认。

**启动方式**（用户在 Codex 中输入，每个任务一个 goal）：

- T0 + A：
  > /goal 按 docs/tasks/00-PLAN.md 第 3 节完成 T0，然后按 docs/tasks/A-agent-delete.md 完成任务 A。只改两份文档列出的路径。完成条件：A 验收标准 1~12（含 2a~2e）全部通过并记录证据、插件测试全部通过、A 任务书末尾完成报告已填写、按限定路径提交。遇到 00-PLAN.md 第 2.4 节的硬停止条件时停止并在完成报告中说明，其余问题自行决策、记录后继续。
- B（Claude 验收 A 通过后）：
  > /goal 按 docs/tasks/B-expert-fixed-session.md 完成任务 B。只改任务书列出的路径。完成条件：B 验收标准 1~14 全部通过并记录证据、插件测试全部通过、`lib/client.js` 已重新构建、DSH 重启后启动日志无致命签名、B 任务书末尾完成报告已填写、按限定路径提交。遇到 00-PLAN.md 第 2.4 节的硬停止条件时停止并在完成报告中说明，其余问题自行决策、记录后继续。

**建议**：启动前把 Codex 的审批策略设为不需要逐条命令确认（在 Codex 中选择自动执行/full-auto 一类的模式，以 Codex 实际提供的选项为准），否则 `/goal` 仍会在每个命令处停下等批准。

**硬停止条件（只有这些情况才停下）**：
1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
5. 同一个问题尝试 3 种不同的解决办法后仍失败。

**不属于停止条件、应自行处理的情况**：
- 任务书与代码实际情况有细节出入：选择最符合任务书意图的做法，在完成报告「偏离」一栏记录原因后继续。
- 测试失败：定位并修复后重跑，直到通过。
- 重启 DSH：已预先授权。重启前用 `/api/ptc-control/trainer/runs` 确认没有进行中的 framework run；有则等待其结束（最多 15 分钟）后再重启。
- 验收需要构造测试数据：自行构造，用完清理，并在完成报告记录。
- 需要选择实现细节（命名、函数拆分、测试组织）：自行决定。

---

## 3. 任务 T0：基线同步（Codex，约 10 分钟）

目的：把 Claude 已做的轮询修复和任务书纳入版本管理，确保 A/B 在记录过基线的工作树上开工。

步骤：
1. 执行 GitHub 同步前，先 `git status --porcelain` 记录本地改动（仓库中可能还有与本计划无关的改动，**不要提交、还原或修改它们**）。与本计划相关的预期改动：
   - 修改：`docs/prototypes/agent-trainer-repair-prototype.html`（轮询修复）
   - 新增：`docs/tasks/00-PLAN.md`、`docs/tasks/A-agent-delete.md`、`docs/tasks/B-expert-fixed-session.md`
   - 新增：`docs/prototypes/agent-trainer-repair-prototype.html.bak-20261001-poll`
2. 按惯常流程完成 GitHub 同步，**保留**上述本地改动（若远端同一文件也有改动，以合并方式解决，不得丢弃轮询修复；冲突无法自动判断时停止报告）。
3. 只 `git add` 上述相关路径，提交轮询修复与任务书：提交信息 `[T0] 修复 Trainer 运行状态轮询上限；新增迭代计划与任务书`。`.bak-*` 文件不提交（如项目无相应 ignore 规则，可在 `.gitignore` 中加入 `*.bak-*`，或保持未跟踪）。
4. 验收：
   - `git log -1` 显示 T0 提交；
   - 提交后的 `agent-trainer-repair-prototype.html` 中能搜到 `LIVE_RUN_POLL_MAX_MS`、`BUSINESS_RUN_POLL_MAX_MS`、`pollLiveRun(`、`pollBusinessRun(`，搜不到 `attempt<30`、`attempt<90`；
   - 页面脚本语法检查通过（提取 `<script>` 内容后 `node --check`）；
   - 刷新 `http://127.0.0.1:3080/agent-trainer` 能正常加载 Agent 列表与工作流。

T0 不需要 Claude 验收，完成后直接进入 A。

---

## 4. 任务 A / B 概要

| | 任务 A：Agent 删除 + ID 不复用 | 任务 B：专家固定训练会话 |
|---|---|---|
| 主要改动 | `docs/prototypes/agent-trainer-repair-prototype.html`、`lib/trainer-project.js`（`applyChanges`）、台账初始化脚本、后端测试 | `plugins/dsh-ptc-control-plane/client/native-sessions.js`、`lib/trainer-service.js`、页面原生会话卡片、`test/` |
| 后端改动 | 有，仅 `applyChanges` 台账强校验 | 有（`resolveTarget`、target-session 存储、2 个 operation、按目标加锁） |
| 是否需重启 DSH | 是（`applyChanges` 属插件代码；页面部分无需重启） | 是（插件代码） |
| 预计 Codex 工作量 | 约 1 天 | 约 1.5 天（含单测与重启验证） |
| 任务书 | `docs/tasks/A-agent-delete.md` | `docs/tasks/B-expert-fixed-session.md` |

---

## 5. Claude 验收 A（检查清单）

> 自动化部分见 `docs/tasks/verify/`（`verify-a.mjs`、`verify-b.mjs`、`README.md`）。Codex 自测与 Claude 验收共用同一套脚本；Claude 验收时先看 Codex 贴的脚本结果，再在浏览器中做 README「手工清单」中的界面项。

前提：Codex 完成报告已填写，验收 1~12 自测通过，且已提交。

1. 读完成报告与 `git show` 的改动，确认：`lib/` 只改 `trainer-project.js` 的 `applyChanges` 及其对应测试；未改 `refreshLiveRun` / `refreshBusinessRun`；无 `window.confirm` / `alert`。
2. 浏览器打开工作台，确认训练模式下 Agent 列表有删除入口，切到发布/工程模式后消失。
3. 新建一个 Agent → 检查 ID 格式、显示名、ID 台账同一 changeSet 更新 → 删除 → 用 `/api/ptc-control/trainer/context` 确认已从 registry 消失、revision 已变化、台账中仍保留该 ID。
3b. 绕过页面直接调用 `apply-changes`：用已登记 ID 新建 → `TRAINER_AGENT_ID_REUSED`；不登记台账新建 → `TRAINER_AGENT_ID_UNREGISTERED`。
3a. 核对台账初始化结果：`allocated` 覆盖历史 revision 中的 Agent ID（抽查 `agent-T1`、`custom-agent-*`）。
4. 尝试删除被「新工作流 1」引用的 Agent → 应被阻止，且网络请求中无 `apply-changes`。
5. 运行一次「新工作流 1」SMOKE_ONLY → 4 步 completed。
6. 结论：通过 → 通知用户启动 B；不通过 → 给出问题清单（编号、现象、复现步骤、期望），交回 Codex。

## 6. Claude 验收 B（检查清单）

前提：Codex 完成报告已填写，验收 1~14 自测通过，DSH 已重启且启动日志无致命错误。

1. 读完成报告与改动 diff，重点核对：`matches()` 不再比较 revision/runId；target-session 记录存服务端、写入在 `serial()` 中、upsert 位于 `bind`；`lib/client.js` 已重新构建；published/engineering 按激活 release 判断；`pendingContextChange` 的设置/合并/消费符合任务书。
1a. 抽查 `context` 在 training / engineering / published 三种模式下的返回与改造前一致；engineering 下经工作流间接包含的 Agent 能被 `resolveTarget` 识别。
2. 同一 Agent：打开会话 → 跑一次 SMOKE → 保存一次候选 → 再打开，三次应为同一 sessionId；核对 `Training_Materials/framework/control/bindings/<sessionId>.json` 中 `candidateRevision`、`selectedRunId`、`bindingRevision` 的变化。
3. 「新开训练会话」得到新 sessionId，旧会话仍在 DSH 会话列表中。
4. 删除一个有过会话的 Agent 后新建 Agent，确认新 Agent 得到全新会话。
5. 结论同验收 A。

---

## 7. 风险与应对

| 风险 | 应对 |
|---|---|
| GitHub 同步时远端也改了 `agent-trainer-repair-prototype.html` | T0 中合并处理；无法判断时停止并报告，由用户/Claude 决定 |
| `resolveTarget` 改造意外改变 `context` 返回内容 | B 2.0 要求三种模式返回与改造前一致，验收 10 附前后对比；发现变化即停止报告 |
| 台账损坏导致项目无法写入 | A 2.7 保留「只改台账」的修复通道，用初始化脚本按扫描结果重建 |
| DSH 宿主没有可靠的「向会话追加消息」接口 | B 第 3 节已规定降级方案：不伪造，只在页面卡片提示 |
| 修改插件后 DSH 启动失败 | 使用 `C:\Users
vt10241\.dsh\rules\dsh-plugin-restart.ps1`（失败自动回滚）；检查启动日志致命签名 |
| 删除 Agent 误删共享 contracts | A 第 4 节规定引用计数后才删；A 验收 7 用 SMOKE 运行兜底验证 |
| 业务运行返回 `status: unknown` 时页面视为进行中，最长 60 分钟阻挡新运行 | 本轮不处理；建议后端在运行结束时写明确终态（列入后续） |

## 8. 任务书修订记录

- 2026-10-01 v2（根据 Codex 评审修正 6 点）：
  1. A：ID 不复用改为台账严格保证（不再依赖随机概率）；
  2. A：删除引用检查与后端 `validateProjectFiles` 对齐，补 `instructionsRef` 等全部字段，并加提交前本地预校验；
  3. A/B/T0：不再要求整个工作树干净，改为记录基线 + 限定路径检查与限定路径提交；
  4. B：明确 `client/` 源文件需经 `scripts/build-client.mjs` 生成 `lib/client.js`；
  5. B：target-session 存在性按 mode 判断，published/engineering 以激活 release 为准；
  6. B：写死并发规则（写入全部进 `serial()`、`openNativeSession` 整体入队去重、upsert 位于 `bind`）与 `pendingContextChange` 的持久化、合并、消费清除规则。

- 2026-10-02 v3（根据后端核对与用户最新约定）：
  1. ID 台账路径固定为后端白名单允许的 `contracts/agent-ids.json`，不修改后端校验。
  2. T0、A、B 的同步目标统一为 GitHub，不再执行其他远端同步。
  3. A：台账由服务端在 `applyChanges` 强校验，保证范围为所有 `apply-changes` 写入；新增错误码 `TRAINER_AGENT_ID_LEDGER_MISSING / _INVALID / _SHRINK`、`TRAINER_AGENT_ID_REUSED / _UNREGISTERED`；base 无台账时只允许单独初始化提交（同时新建 Agent 拒绝）；台账损坏时只允许「只改台账」的修复提交；一次提交新建多个 Agent 全部检查。
  4. A：台账初始化扫描范围写死为仓库根目录下 4 个目录，只从结构化字段提取 ID，排除业务 profile。
  5. A：新增台账回归测试（校验 → 冻结 → `verifyBundle` → `stage-release`）。
  6. B：新增统一 `resolveTarget()`；engineering 含经工作流间接包含；published 本轮保持现状并延期。
  7. B：来源标识统一结构 `{source, revisionId, frozenVersionId, releaseId, via}`，用于 `lastResolved` 与 `pendingContextChange`；engineering 激活新 release 也触发上下文变化。
  8. B：串行改为「全局短 `serial()` + 两层实现 + 按会话键加锁」，替代 v2 中「`openNativeSession` 整体入全局队列」。
  9. B：`pendingContextChange` 删除硬规则——来源标识相同且 runId 相同才删除。
  10. 计划新增 1.4「最终执行顺序」。
  11. 计划新增 2.4「连续执行规则」：A、B 使用 Codex `/goal` 模式连续执行，写明启动语句、5 条硬停止条件与自行处理的情况；预先授权 Codex 自行重启 DSH。
  12. 新增验收脚本 `docs/tasks/verify/`：A、B 的自动化检查（含台账独立复扫、服务端强校验绕过测试、context 改造前后对比、target-session 与绑定文件不变量）；A、B 任务书的验收章节与完成报告已引用。

## 9. 后续（本轮不做）

- **发布模式审核对象**：新增可查询的 staged/current-review 指针，published 只显示待审核的冻结版本（无则为空）；完成后 published 的 `resolveTarget`、`context`、`session-workspace`、target-session 一起切换到 `source:'frozen'`。
- **冻结版本排序**：在 `version.json` 中增加明确的冻结时间或冻结序号；不得按 UUID 目录名或文件修改时间排序；存量冻结版本的迁移方式由该任务决定。
- Agent 撤销删除 / 「最近删除」列表（基于旧 revision 恢复）。注意：A 的台账强校验会拒绝重建同一 ID，恢复需设计显式例外操作。
- 删除 Agent 时可选的「从工作流中连带移除步骤」。
- BUSINESS_ONLY 运行在页面刷新后的可靠接回（需要后端提供按 purpose / 活跃状态过滤的接口）。
- 后端为业务运行写入明确终态，消除 `unknown`。
