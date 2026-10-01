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
2. **Agent ID 永不复用**：新建 Agent 用随机 ID（`agent-xxxxxx`），显示名存于 `agent.json.name`；存量 ID 不迁移。
3. **专家固定会话**：同一 `projectId + mode + targetKind + targetId + presetId` 只对应一个长期 DSH 会话；对应关系存服务端；复用时把绑定更新到最新 revision / runId 并让会话知道上下文已变；提供「新开训练会话」按钮。
4. 顺序：**T0 → A → 验收 A → B → 验收 B**。B 依赖 A 的「ID 永不复用」。

---

## 2. 角色与交接协议

### 2.1 Codex（实现）

- **每个任务开工前必须先做 GitLab 同步**（按项目惯常流程）。同步失败、有冲突或工作区状态与任务书描述不符时，**停止并在完成报告中说明**，不要自行强推或丢弃本地改动。
- 严格按任务书范围改动；需要偏离时，在完成报告「偏离」一栏写明原因。
- 每个任务完成后：
  1. 逐条执行验收标准并记录实际结果（通过 / 失败 + 证据：命令输出、接口返回片段、文件路径）；
  2. 填写任务书末尾「完成报告」；
  3. 按项目惯例提交，提交信息以任务编号开头（如 `[A] Agent 删除与 ID 不复用`）。
- 遇到阻塞（同一问题 30 分钟无进展）：停止，在完成报告写清楚现象、已尝试的办法、证据路径和**一个**具体问题，交给用户转 Claude。

### 2.2 Claude（验收与诊断）

- 不参与日常实现，只在以下时点介入：
  - **验收 A**：Codex 报告 A 完成后，读完成报告和改动 diff，在 Claude 内置浏览器中对 `http://127.0.0.1:3080/agent-trainer` 做端到端抽查（见第 5 节）。
  - **验收 B**：同上（见第 6 节）。
  - **疑难诊断**：Codex 阻塞且用户转来时。
- 为节省额度：Claude 验收以抽查关键路径为主，不重复执行 Codex 已有证据的全部单项；验收结论只给「通过」或「不通过 + 具体问题清单」，修复仍交回 Codex。

### 2.3 用户

- 在 Codex 中启动任务（工作目录 `D:\Newtest\DSH\ATE-Coding-Flow`），指令模板：
  > 先做 GitLab 同步。然后按 docs/tasks/<任务文件> 执行，完成后逐条自测验收标准，填写文件末尾的完成报告并提交。
- Codex 完成后告诉 Claude「<任务编号> 做完了」，Claude 开始验收。
- 需要重启 DSH 时（任务 B），确认 DSH 当前没有正在进行的重要会话/运行。

---

## 3. 任务 T0：基线同步（Codex，约 10 分钟）

目的：把 Claude 已做的轮询修复和任务书纳入版本管理，确保 A/B 在干净基线上开工。

步骤：
1. 执行 GitLab 同步前，先 `git status` 记录本地改动。预期至少包含：
   - 修改：`docs/prototypes/agent-trainer-repair-prototype.html`（轮询修复）
   - 新增：`docs/tasks/00-PLAN.md`、`docs/tasks/A-agent-delete.md`、`docs/tasks/B-expert-fixed-session.md`
   - 新增：`docs/prototypes/agent-trainer-repair-prototype.html.bak-20261001-poll`
2. 按惯常流程完成 GitLab 同步，**保留**上述本地改动（若远端同一文件也有改动，以合并方式解决，不得丢弃轮询修复；冲突无法自动判断时停止报告）。
3. 提交轮询修复与任务书：提交信息 `[T0] 修复 Trainer 运行状态轮询上限；新增迭代计划与任务书`。`.bak-*` 文件不提交（如项目无相应 ignore 规则，可在 `.gitignore` 中加入 `*.bak-*`，或保持未跟踪）。
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
| 主要改动 | `docs/prototypes/agent-trainer-repair-prototype.html` | `plugins/dsh-ptc-control-plane/client/native-sessions.js`、`lib/trainer-service.js`、页面原生会话卡片、`test/` |
| 后端改动 | 原则上无 | 有（新增 target-session 存储与 2 个 operation） |
| 是否需重启 DSH | 否（页面每次请求现读） | 是（插件代码） |
| 预计 Codex 工作量 | 半天以内 | 约 1 天（含单测与重启验证） |
| 任务书 | `docs/tasks/A-agent-delete.md` | `docs/tasks/B-expert-fixed-session.md` |

---

## 5. Claude 验收 A（检查清单）

前提：Codex 完成报告已填写，验收 1~12 自测通过，且已提交。

1. 读完成报告与 `git show` 的改动，确认：未改 `lib/`；未改 `refreshLiveRun` / `refreshBusinessRun`；无 `window.confirm` / `alert`。
2. 浏览器打开工作台，确认训练模式下 Agent 列表有删除入口，切到发布/工程模式后消失。
3. 新建一个 Agent → 检查 ID 格式与显示名 → 删除 → 用 `/api/ptc-control/trainer/context` 确认已从 registry 消失、revision 已变化。
4. 尝试删除被「新工作流 1」引用的 Agent → 应被阻止，且网络请求中无 `apply-changes`。
5. 运行一次「新工作流 1」SMOKE_ONLY → 4 步 completed。
6. 结论：通过 → 通知用户启动 B；不通过 → 给出问题清单（编号、现象、复现步骤、期望），交回 Codex。

## 6. Claude 验收 B（检查清单）

前提：Codex 完成报告已填写，验收 1~14 自测通过，DSH 已重启且启动日志无致命错误。

1. 读完成报告与改动 diff，重点核对：`matches()` 不再比较 revision/runId；target-session 记录存服务端；复用路径会更新绑定；`[Trainer 上下文更新]` 的实现方式（或降级方案）。
2. 同一 Agent：打开会话 → 跑一次 SMOKE → 保存一次候选 → 再打开，三次应为同一 sessionId；核对 `Training_Materials/framework/control/bindings/<sessionId>.json` 中 `candidateRevision`、`selectedRunId`、`bindingRevision` 的变化。
3. 「新开训练会话」得到新 sessionId，旧会话仍在 DSH 会话列表中。
4. 删除一个有过会话的 Agent 后新建 Agent，确认新 Agent 得到全新会话。
5. 结论同验收 A。

---

## 7. 风险与应对

| 风险 | 应对 |
|---|---|
| GitLab 同步时远端也改了 `agent-trainer-repair-prototype.html` | T0 中合并处理；无法判断时停止并报告，由用户/Claude 决定 |
| DSH 宿主没有可靠的「向会话追加消息」接口 | B 第 3 节已规定降级方案：不伪造，只在页面卡片提示 |
| 修改插件后 DSH 启动失败 | 使用 `C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1`（失败自动回滚）；检查启动日志致命签名 |
| 删除 Agent 误删共享 contracts | A 第 4 节规定引用计数后才删；A 验收 7 用 SMOKE 运行兜底验证 |
| 业务运行返回 `status: unknown` 时页面视为进行中，最长 60 分钟阻挡新运行 | 本轮不处理；建议后端在运行结束时写明确终态（列入后续） |

## 8. 后续（本轮不做）

- Agent 撤销删除 / 「最近删除」列表（基于旧 revision 恢复）。
- 删除 Agent 时可选的「从工作流中连带移除步骤」。
- BUSINESS_ONLY 运行在页面刷新后的可靠接回（需要后端提供按 purpose / 活跃状态过滤的接口）。
- 后端为业务运行写入明确终态，消除 `unknown`。
