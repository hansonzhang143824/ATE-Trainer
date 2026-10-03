# 任务 E：真实候选运行成为主流程，并一次修正 12 项系统问题

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录；插件目录简写为 `plugin/` = `plugins/dsh-ptc-control-plane/`）
- 编写：Claude Code（2026-10-03），方向经用户、Codex、Claude 三方确认。执行：Codex（`/goal`）。验收：Claude Code
- 本文件是本轮**唯一执行依据**。执行中忘了要做什么，回到第 1 节（目标）和附录 A（用户原话）。
- 问题编号（R01…）对应 `docs/tasks/ISSUE-REGISTER.md`。本任务完成后由 Claude Code 更新登记表状态。
- 本任务是 D 之后的新任务，**不回滚、不改写 D 的代码提交与历史数据**。
- 完成后在第 10 节填写完成报告。

---

## 1. 目标

### 1.1 用户原意（原话见附录 A，任何实现不得偏离）

- 系统本来不需要 SMOKE_ONLY 和 BUSINESS_ONLY。SMOKE_ONLY 是为了用最轻量的 Agent 验证系统本身（调度、交接、合同）；BUSINESS_ONLY 是为了验证「训练优化 Agent 之后再执行工作流」这条链路，用 597 排除真实业务中与系统无关的卡点。
- 这两者**只是验证工具**。真正的流程里，Agent 内部可以是空的，用户通过聊天式训练逐步优化；不需要「597 不能改」之类的约束，597 / 1+2 只在验证时用到。
- 当前实现把验证工具做成了主要（页面上唯一的）运行方式，偏离了原意。本任务把它纠正回来。
- 用户要求：**这一轮至少修正一半以上的已知问题，不要拆成很多个任务**。所以本任务同时修正与接入真实业务直接相关的系统问题（1.3）。

### 1.2 三方确认的边界（Codex 原文，写死）

> * `SMOKE_ONLY` 和 `BUSINESS_ONLY` 保留为独立验证工具，不参与正式冻结和发布。
> * 页面新增"真实候选运行"，并作为默认运行入口。
> * 真实候选运行必须先完成，才能冻结和发布。
> * 合成运行只能验证系统，不能作为发布依据。
> * `businessGatePassed` 保留用于旧记录兼容，但不再作为真实运行或发布条件。
> * `597`、`1+2` 只在验证时临时注入，不能进入 Agent 指令、schema 或正式运行。
> * 历史合成冻结/发布版本保持不可发布、不可激活，不改写旧数据。
> * `AGENTS.md` 重写为"真实候选运行是主流程，SMOKE/BUSINESS 是回归验证工具"，同时保留哈希、会话、bindings 和归档专家的安全边界。

> * 旧的 `FRAMEWORK_TRAINING` 版本不能仅凭模式名自动视为真实版本，必须能找到对应运行，并证明：未使用 SMOKE/BUSINESS、运行完成、步骤 schema 通过、目标与 revision/hash 一致；否则禁止新发布。
> * 新普通运行统一使用明确的 `CANDIDATE` 模式，并显式保存 `sourceBundle`。
> * `businessGatePassed` 仅为历史兼容字段，不再作为候选运行、冻结或发布条件。
> * 现有已激活 release 保持不变，不改写历史数据；页面只限制其再次发布。

Claude Code 定稿时的取舍（已告知用户）：
1. 发布模式（已发布版本）的普通运行记为 `RELEASE`，与训练模式的 `CANDIDATE` 区分。
2. SMOKE / BUSINESS 只能从页面发起；训练会话里的专家调用运行一律是 `CANDIDATE`。
3. 「历史合成版本不可激活」沿用 D 的规则（只针对**含合成指令**的发布版本）；以合成运行为验证依据、但内容真实的已有发布版本（如 `release-6aab1ccf…`）保持可切回，只禁止它们对应的冻结版本**再次发布**。

### 1.3 本轮修正的问题（共 12 项 + 1 项可行性验证）

| 编号 | 问题 | 本轮做法 | 规格 |
|---|---|---|---|
| R01 | 页面只能发起合成运行，没有真实候选运行入口 | 新增并设为默认 | 4.1、4.6 |
| R02 | 正式路径（训练会话、子 Agent、工作区说明）被写成「合成测试」 | 提示词矩阵 | 4.5 |
| R03 | 冻结依据不可证明（revision 可不传、依赖兼容回退、合成运行可冻结） | 冻结 9 条校验 | 4.3 |
| R04 | 以合成运行为依据的冻结版本仍可发布 | 发布资格判定 | 4.4 |
| R05 | `AGENTS.md` 把系统锁在合成冒烟范围 | 按附录 B 重写 | 4.7 |
| R06 | `businessGatePassed === false` 是发布条件 | 去掉该条件 | 4.4 |
| R07 | DSH 每次重启都改写**已结束**运行的 `dispatch.json`；9/22 的 3 条记录已被改写 | 修代码 + 从 Git 历史按字节恢复 3 条 | 4.8 |
| R08 | 步骤超时时运行立即标为 failed，子会话是否终止尚未确认 | 先进入 stopping，确认后再 failed；限时兜底 | 4.9 |
| R09 | 脚本工具单次最多 30 秒，真实材料解析不够用 | 上限提到 10 分钟，且不超过所在步骤超时 | 4.10 |
| R10 | 透明加密层下，DSH 启动的脚本读取材料文件得到明文还是密文，未验证 | 宿主探针，用真实材料实测并留证 | 4.12 EM |
| R12 | 页面初始运行状态显示「尚未运行 · idle」 | 修正显示 | 4.6 第 9 条 |
| R21 | D 的宿主验收主流程用接口代替页面，漏掉了「页面跑不了真实运行」 | 本轮主流程验收必须在页面点按钮 | 4.12 |
| R11（可行性） | 真实材料如何交给 Agent | 本轮只验证「运行输入带文件路径 + 脚本工具读取文件」这条路可行（EM）；正式方案留给 C2 | 4.12 EM |

### 1.4 不在本轮范围

R11 的正式方案（材料目录、路径白名单、大文件处理）；R15 旧 TM109 流水线代码清理；R16 9/23~9/29 未提交 DFT 改动的去留（需用户决定）；R17 D-5（待审核状态、版本说明、版本对比）；R18 停机期间删除的会话重启后复用旧壳（需另行调查）；R19 仓库卫生（用户已决定暂不处理）。删除或改写任何已有冻结、发布、revision、bindings、会话文件。

### 1.5 硬停止条件（`docs/tasks/00-PLAN.md` 2.4 节，原文）

> 1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
> 2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
> 3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
> 4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
> 5. 同一个问题尝试 3 种不同的解决办法后仍失败。

### 1.6 本轮明确授权

- 修改仓库根目录 `AGENTS.md`，内容**照抄附录 B**（不得自行增删）。
- 修改 `plugin/lib/trainer-schema.js` 中脚本工具 `timeoutMs` 的上限（4.10），不改其他白名单。
- `context` 返回的 `frozenVersions` 条目**新增字段**（4.4）；运行记录新增字段。不得删除或改名已有字段。
- 训练会话工作区说明文件 `Training_Materials/framework/control/sessions/<hash>/AGENTS.md`：**仅当文件内容与旧文本逐字节相同**时替换为新文本（4.5 第 3 条）；其他内容一律不动。
- 按 4.8 第 2 条，从提交 `5468af34` 按字节恢复以下 3 个文件，**只限这 3 个**：
  - `Training_Materials/runs/training-20260922t143354z-454b6e9a/dispatch.json`
  - `Training_Materials/runs/training-20260922t153154z-fa40e64f/dispatch.json`
  - `Training_Materials/runs/training-20260922t154456z-898b29e5/dispatch.json`
- 验收构造测试数据：EM 可临时修改 `agent-T3` 的候选内容（经 `apply-changes`），结束后恢复为原内容（新 revision、内容逐字节相同）。
- 修改已有测试：仅限因本任务规则而失效的断言（合成运行不能冻结、`businessGatePassed` 不再是发布条件、默认执行模式、超时状态时序、重启不再改写已关闭回执、脚本超时上限），在报告「偏离」中逐个列出测试名、原断言、新断言。
- 冻结、发布、激活只能经系统接口产生；不得手工改写 `publish/`、`versions/`、`revisions/`、`control/bindings/` 下的已有文件。

---

## 2. 现状（Claude Code 已读代码确认，执行前请复核行号）

| 事实 | 位置 |
|---|---|
| `run`：`executionMode` 为 BUSINESS_ONLY / SMOKE_ONLY 时用 `syntheticBusinessBundle` / `syntheticSmokeBundle` 改写执行包，否则用 `baseBundle`；只有这两种模式才把 `sourceBundle: baseBundle` 传给运行器 | `plugin/lib/trainer-service.js` 约 499~509 行 |
| `execute(operation, args, binding)`：来自训练会话工具的请求 `binding` 非空（`authorize` 对 `principal.kind === 'tool'` 返回绑定），来自页面的请求无会话绑定 | `trainer-service.js` 约 189~202、407、566 行 |
| 运行器：`executionMode: input.executionMode ?? 'FRAMEWORK_TRAINING'`；`sourceBundleSha256: sourceBundle?.bundleSha256 ?? bundle.bundleSha256`；只在传入 `sourceBundle` 时写 `source-bundle.json` | `plugin/lib/framework-agent-run.js` 约 330~347 行 |
| `readRun`：没有 `source-bundle.json` 且两个 sha 相等时，把执行包本身当 `sourceBundle`（兼容回退） | `framework-agent-run.js` 约 104~115 行 |
| 每步输出按 `outputSchemaRef` 校验，结果存 `step.validation`；全部通过才 `run.status='completed'`、`run.validation={ok:true}` | `framework-agent-run.js` 约 259、281、285 行 |
| 超时：`onCancel` 的 timeout 分支直接 `run.status='failed'`、`completedAt`、`step.status='failed'`，此时 `childTerminationConfirmed=false`；而 `finishCancellation` 本来会在确认终止后按 `entry.timedOut` 置 failed | `framework-agent-run.js` 约 135~147、199~218 行 |
| `freeze`：要求 completed、`validation.ok`、目标一致；`bundle = run.sourceBundle`；`validation.executionMode` 兜底 `'FRAMEWORK_TRAINING'`；**`revisionId` 可不传** | `trainer-service.js` 约 525~540 行 |
| `freezeTarget`：只在传了 `revisionId` 时才校验 `bundle.revisionId` | `plugin/lib/trainer-bundle.js` `freezeTarget` |
| `evidenceCheck` 要求 `evidence.businessGatePassed === false` | `plugin/lib/trainer-release.js` 约 7~17 行 |
| 训练会话专家提示词：「All inputs and results here are synthetic. businessGatePassed is always false. Never read archived business profiles, private material…」 | `plugin/lib/trainer-preset.js` 约 16 行 |
| 训练会话工作区说明文件：`'# Synthetic Agent Trainer workspace\n…'`，只在文件不存在时写入 | `trainer-service.js` 约 266~270 行 |
| 子 Agent 身份说明「You execute a synthetic framework training step … This is not business certification.」；脚本工具描述「Run the declared synthetic JSON script …」；脚本超时报错「synthetic script timed out」 | `plugin/lib/framework-dsh-adapter.js` 约 23、82、156 行 |
| 脚本工具超时：schema `timeoutMs` 最大 30000；适配器再检查 `<= 30000` | `plugin/lib/trainer-schema.js` 约 50 行；`framework-dsh-adapter.js` 约 76 行 |
| 步骤子 Agent `toolFilter: { allow: [] }`，但登记的脚本工具与 `structured_output` 仍可见；脚本以普通 node / python 进程运行，参数经 stdin 传入 | `framework-dsh-adapter.js` 约 19~30、70~100、152~156 行 |
| 重启对账：`reconcileInterruptedTrainingRuns` 在判断运行是否仍在进行**之前**，就把所有带 `dispatch.json` 的运行回执改写为 `closeReason:'host_restart'`、`closedAt=重启时间`；9/22 的 3 条已关闭回执已于 2026-10-03 11:15 被改写（原值在提交 `5468af34`） | `plugin/lib/training-execution.js` 约 40~78 行 |
| 页面执行模式只有 `data-exec="smoke"` / `"business"`，默认 `state.exec:'smoke'`；运行时 `executionMode` 只会是 SMOKE_ONLY / BUSINESS_ONLY，输入写死 `{receivedValue:'1+2'}` / `{receivedValue:'23*24+45'}` | `docs/prototypes/agent-trainer-repair-prototype.html` 约 52、80、359~360 行 |
| 页面「冻结候选」`freezeCandidate()` 用 `state.liveRun.runId`，不传 `revisionId`；「发布此版本」用 `version.validation.runId` | 同上 约 369~376、379 行 |
| 页面初始 `lastRun:{id:'尚未运行',status:'idle'}`，`runStatusText` 没有 `idle` 映射 → 显示「尚未运行 · idle」；运行状态行显示 `businessGatePassed: false` | 同上 约 80、130 行及 `runStatusText` |
| 测试目标「新工作流 1」= `custom-workflow-1`：4 个 Agent 的输入 schema 均为空对象可通过（`additionalProperties: true`、无必填），空输入可以运行 | 当前候选 revision（`current.json`） |
| D 的宿主验收 DF 通过接口（`startApiRun`）发起合成验证运行再冻结，没有经过页面运行 | `docs/tasks/verify/verify-b-host.mjs` 约 686~760 行 |
| 历史运行中出现过的 `executionMode`：缺失、`FRAMEWORK_TRAINING`、`SMOKE_ONLY`、`BUSINESS_ONLY`、`SYNTHETIC_597` | `Training_Materials/runs/*/framework-run.json` |

---

## 3. 本轮要交付的行为（验收以此为准）

| 编号 | 行为 | 问题 | 验证 |
|---|---|---|---|
| E-1 | 页面默认执行模式为「真实候选运行」；有输入框（可空或 JSON 对象）；SMOKE / BUSINESS 移入「系统验证」分组，仍可使用；初始状态显示「尚未运行」 | R01、R12 | EC-1、EX-7、单测 |
| E-2 | 训练模式普通运行记 `CANDIDATE`，发布模式记 `RELEASE`；两者都显式保存 `source-bundle.json`（= 实际执行包）；执行的是真实指令 | R01、R03 | EC-2 ~ EC-4、EC-7、单测 |
| E-3 | 冻结只接受同一目标、同一 revision、已完成、每步 schema 通过的 `CANDIDATE` 运行；必须传 `revisionId`；其他情况用专用错误码拒绝 | R03 | EC-5、EX-1 ~ EX-4、单测 |
| E-4 | 发布资格可证明（4.4）；不可发布的冻结版本页面按钮禁用并标明原因；已有发布版本不改、可切回；`businessGatePassed` 不再是条件 | R04、R06 | EC-6、EX-6、EL-1 ~ EL-5、单测 |
| E-5 | 提示词矩阵：只有 SMOKE / BUSINESS 运行出现「合成」说明；普通运行、训练会话、会话工作区说明不出现 synthetic / 合成 / 597 / 1+2 | R02 | EP-1、EP-2、单测 |
| E-6 | `AGENTS.md` 按附录 B 重写 | R05 | Claude 复核 |
| E-7 | 重启不再改写已关闭的回执；3 条被改写的回执按字节恢复；重启前后所有已关闭回执不变 | R07 | ER-1 ~ ER-3、单测 |
| E-8 | 步骤超时：先 `stopping`（错误码 `STEP_TIMEOUT` 已可见），子会话终止确认后 `failed`；120 秒内未确认则 `failed` 并标记 `terminationUnconfirmed: true`，同目标新运行继续被阻止 | R08 | ET-1 ~ ET-3、H 回归、单测 |
| E-9 | 脚本工具 `timeoutMs` 上限 600000（10 分钟），且不得超过所在步骤的超时 | R09 | EM-1、单测 |
| E-10 | 真实材料读取探针：DSH 启动的脚本工具按路径读取 `Dali_testmode.xlsx`，结果与 Python 直接读取逐项比对，结论留证 | R10、R11 | EM-1 ~ EM-4 |
| E-11 | 回归：B（A 步骤）、C1（K、H 步骤）、D（DO、DP 步骤）、只读复核仍通过 | — | 步骤 4、5 |

---

## 4. 实现规格

### 4.1 执行模式（`plugin/lib/trainer-service.js` 的 `run`）

1. 常量（导出，供测试与其他模块使用）：
   ```js
   export const SYNTHETIC_EXECUTION_MODES = new Set(['SMOKE_ONLY', 'BUSINESS_ONLY', 'SYNTHETIC_597']);
   ```
2. 在解析执行包之前归一化 `executionMode`：
   - `mode === 'training'`：缺省 → `'CANDIDATE'`；允许 `CANDIDATE`、`SMOKE_ONLY`、`BUSINESS_ONLY`。
   - `mode === 'published'`：缺省 → `'RELEASE'`；允许 `RELEASE`、`SMOKE_ONLY`、`BUSINESS_ONLY`。
   - 其他值（含显式传 `'FRAMEWORK_TRAINING'`、`'SYNTHETIC_597'`）→ `fail('EXECUTION_MODE_INVALID', '不支持的执行模式')`，不创建运行。
   - `binding` 非空（请求来自训练会话工具）且归一化结果不是 `CANDIDATE` → `fail('EXECUTION_MODE_FORBIDDEN', '训练会话只能发起真实候选运行；SMOKE_ONLY / BUSINESS_ONLY 只能从页面发起')`。
3. 执行包：SMOKE / BUSINESS 照旧改写；`CANDIDATE` / `RELEASE` 用 `baseBundle`。
4. **所有模式**都向 `runner.startRun` 传 `sourceBundle: baseBundle` 和归一化后的 `executionMode`，使每个新运行都有 `source-bundle.json`。`CANDIDATE` / `RELEASE` 运行的 `bundleSha256` 必须等于 `sourceBundleSha256`（补单测）。
5. `readRun` 的兼容回退**保留不改**（旧记录仍可读），但冻结与发布资格判断**不得依赖**回退得到的 `sourceBundle`（见 4.3 第 8 行、4.4）。

### 4.2 运行器把执行模式交给适配器（`framework-agent-run.js` → `framework-dsh-adapter.js`）

1. 运行器调用适配器执行每一步时，在传给适配器的参数对象中新增字段 `executionMode`（值为 `run.executionMode`）。
2. 适配器据此选择 4.5 的提示词。缺省（旧调用方未传）按非合成处理。
3. 运行记录字段不删不改名；`businessGatePassed: false` 照写。

### 4.3 冻结（`trainer-service.js` 的 `freeze`）

按以下顺序校验，任何一条不满足即失败、不产生冻结版本：

| 顺序 | 条件 | 失败码 / 文案 |
|---|---|---|
| 1 | 传入 `revisionId` | `TRAINER_FREEZE_REVISION_REQUIRED`：冻结必须指定候选 revision |
| 2 | 传入 `runId`，运行存在且属于本项目 | 沿用 `validation_required` |
| 3 | `run.executionMode` 不在 `SYNTHETIC_EXECUTION_MODES` | `TRAINER_FREEZE_SYNTHETIC_RUN`：合成验证运行只能验证系统，不能作为冻结依据；请先完成真实候选运行 |
| 4 | `run.executionMode === 'CANDIDATE'` 且 `run.mode === 'training'` | `TRAINER_FREEZE_CANDIDATE_REQUIRED`：冻结需要一次真实候选运行（CANDIDATE） |
| 5 | `run.status === 'completed'`、`run.validation?.ok === true`、每一步 `status === 'completed'` 且 `step.validation?.ok === true`（`step.validation` 结构以 `framework-agent-run.js` 约 259 行为准） | 沿用 `validation_required` |
| 6 | `run.projectId / targetKind / targetId` 与请求一致 | 沿用 `validation_required` |
| 7 | `run.revisionId === args.revisionId` | `TRAINER_FREEZE_REVISION_MISMATCH`：运行的 revision 与要冻结的 revision 不一致 |
| 8 | 运行有 `sourceBundleArtifact`（读到的是 `source-bundle.json`，不是回退）；`sourceBundle.revisionId === args.revisionId`；`sourceBundle.bundleSha256 === run.sourceBundleSha256 === run.bundleSha256` | `validation_source_unavailable` |
| 9 | `syntheticInstructionRefs(sourceBundle)` 为空 | 沿用 `TRAINER_FROZEN_SYNTHETIC` |

通过后调用 `freezeTarget({..., revisionId: args.revisionId, bundle: sourceBundle, validation: { runId, executionMode: 'CANDIDATE', revisionId: args.revisionId } })`。`freezeTarget` 内部的 revision 校验改为**无条件**执行。

### 4.4 发布资格（`trainer-service.js`；`context.frozenVersions` 新字段）

1. 在 `trainer-service.js` 中新增并导出 `frozenPublishEligibility(projectId, version)`（可读取运行），返回 `{ publishable, code, reason }`，按顺序判定：

| 顺序 | 情况 | 结果 |
|---|---|---|
| 1 | 冻结内容含合成指令（D 的 `contaminated`） | `TRAINER_FROZEN_SYNTHETIC` / 合成指令，不可发布 |
| 2 | `version.validation` 为空或没有 `runId` | `TRAINER_FROZEN_NO_VALIDATION` / 无验证依据，不可发布 |
| 3 | `validation.executionMode` 在 `SYNTHETIC_EXECUTION_MODES` | `TRAINER_FROZEN_SYNTHETIC_VALIDATION` / 合成验证依据，不可发布 |
| 4 | `validation.executionMode` 不是 `CANDIDATE` 也不是 `FRAMEWORK_TRAINING` | `TRAINER_FROZEN_VALIDATION_UNPROVEN` / 验证依据无法证明，不可发布 |
| 5 | 读取 `validation.runId` 对应运行失败（不存在、完整性校验失败） | 同上 `UNPROVEN` |
| 6 | 运行记录中的原始 `executionMode`（缺失视为旧真实运行）在 `SYNTHETIC_EXECUTION_MODES` | 同上 `UNPROVEN` |
| 7 | 运行未完成、`validation.ok !== true`、任一步未完成或 `step.validation?.ok !== true` | 同上 `UNPROVEN` |
| 8 | 运行的 `projectId / targetKind / targetId / revisionId` 与冻结版本不一致；或 `(run.sourceBundleSha256 ?? run.bundleSha256) !== version.bundleSha256` | 同上 `UNPROVEN` |
| 9 | 以上都通过 | `publishable: true`，`code: null`，`reason: null` |

2. `context` 组装 `frozenVersions` 时，每个条目新增 `publishable`（布尔）、`publishBlockCode`（字符串或 null）、`publishBlockReason`（上表中文文案或 null）。不改原有字段与排序。
3. `stage-release`：
   - 先做上述判定，不可发布 → 以 `publishBlockCode` 为错误码、`publishBlockReason` 为文案失败，不写任何发布文件。
   - 请求的 `runId` 必须等于 `version.validation.runId`，否则 `TRAINER_RELEASE_RUN_MISMATCH`：发布必须使用冻结时记录的验证运行。
   - `trainer-release.js` 的 `evidenceCheck` 去掉 `evidence.businessGatePassed !== false` 条件，其余不变。
   - `release.json` 照写 `businessGatePassed: false`（兼容字段）；`validationMode` 写验证运行的 `executionMode`。
4. `activate-release`、`loadReleaseBundle`：不新增拦截（沿用 D：只拦截含合成指令的发布版本）。

### 4.5 提示词矩阵

| 位置 | CANDIDATE / RELEASE（及训练会话本身） | SMOKE_ONLY / BUSINESS_ONLY |
|---|---|---|
| 子 Agent 身份说明（`framework-dsh-adapter.js` 约 156 行） | `You execute one step of a workflow. Follow its selected instructions and Skill documents. Use only declared tools. Return your result through structured_output.` | 保持现有合成说明不变 |
| 脚本工具描述（约 82 行） | `Run the declared JSON script ${toolName}.` | 保持现有 |
| 脚本相关报错文案（`synthetic script timed out`、`synthetic script parameters failed validation`、`synthetic script changed after loading`） | 去掉 `synthetic ` 字样（所有模式统一） | 同左 |
| 训练会话专家提示词（`trainer-preset.js` 约 16 行整句替换） | `Runs you start execute the candidate's real instructions, Skills and schemas (executionMode CANDIDATE). SMOKE_ONLY and BUSINESS_ONLY are system checks started only from the workbench page. Do not read archived expert profiles, credentials or operating-system configuration.` | — |
| 训练会话工作区说明（`trainer-service.js` 约 269 行） | `# Agent Trainer workspace\nRuns execute the candidate Agent instructions and contracts. Use the registered framework tools and server binding. Do not load archived expert profiles, credentials or operating-system configuration.\n` | — |

1. 上表左列文字照抄。普通运行与训练会话中，任何由系统发给模型的文本都不得包含 `synthetic`、`Synthetic`、`合成`、`597`、`1+2`、`23*24+45`（候选 Agent 自己的指令内容不在此限）。
2. `trainer-preset.js` 其余句子不改。
3. 工作区说明文件迁移：打开 / 解析训练会话（写工作区说明的同一处）时，若 `sessions/<hash>/AGENTS.md` 内容与旧文本 `'# Synthetic Agent Trainer workspace\nOnly synthetic framework assets and runs. Do not load archived business profiles or private inputs. Use the registered framework tools and server binding. businessGatePassed remains false.\n'` **逐字节相同**，替换为新文本；不同则不动；不存在则写新文本。

### 4.6 页面 `docs/prototypes/agent-trainer-repair-prototype.html`（接口写死，验收程序依赖）

1. 执行模式区域：
   - 新增第一个按钮 `<button data-exec="candidate">真实候选运行</button>`，默认 `state.exec:'candidate'`。
   - 现有两个按钮保留原 `data-exec` 值和文字，放进一个带文字标签「系统验证（结果不能用于冻结 / 发布）」的分组。
   - 只在训练模式可切换（沿用现有限制）。
2. 输入框：新增 `<textarea id="run-input" placeholder="运行输入：JSON 对象，可留空"></textarea>`，在训练模式选中 `candidate` 时、以及工程模式（运行已发布工作流）时显示；SMOKE / BUSINESS 时隐藏。
   - 内容去掉首尾空白后为空 → 输入 `{}`。
   - 否则 `JSON.parse`，结果必须是非 null、非数组的对象；否则 toast「运行输入必须是 JSON 对象」，**不发请求**。
3. 运行请求（`runTrainerCore`）：
   - 训练模式：`candidate` → `executionMode:'CANDIDATE'`，输入取输入框；`smoke` / `business` → 照旧（固定输入）。
   - 工程模式：`executionMode:'RELEASE'`，输入取输入框。
   - `#run` 文字：训练模式 `candidate` 时为「▶ 运行（真实候选）」；其他沿用现有文字。
4. 文案：`candidate` / `RELEASE` 时，`#mode-help` 为「真实候选运行：使用当前候选 Agent 的指令、Skill 与输入输出合同；完成后可用于冻结。」，`#contract` 为「按候选 Agent 注册的输入 / 输出合同执行。」；检查面板、步骤描述、运行状态行不得出现 597、1+2、合成、`businessGatePassed` 字样。SMOKE / BUSINESS 时文案保持现状。
5. 接回运行时 `state.exec` 映射：`CANDIDATE` → `candidate`，`SMOKE_ONLY` → `smoke`，`BUSINESS_ONLY` → `business`，其他不改 `state.exec`。
6. 「冻结候选」`freezeCandidate()`：
   - 当前运行 `executionMode` 在合成集合中 → toast「合成验证运行不能用于冻结，请先完成真实候选运行。」，不发请求；
   - 请求增加 `revisionId: state.liveRun.revisionId`；
   - 服务端失败照旧 toast「冻结失败：{message}」。
7. 发布审核页版本列表（D 的 `#version-list`）冻结行：增加属性 `data-publishable="{true|false}"`；`publishable === false` 时「发布此版本」禁用，行内显示 `publishBlockReason`；D 的其他属性、文字、发布行按钮行为不变。
8. 超时显示（配合 4.9）：运行处于 `stopping` 且 `error.code === 'STEP_TIMEOUT'` 时，`#run-error` 显示超时文案（沿用 C1 的 `formatStepTimeoutMessage` 内容）并追加「，正在停止子会话」；最终 `failed` 且 `terminationUnconfirmed === true` 时追加「；子会话终止未确认，同一目标的新运行将被阻止，直至确认或重启 DSH」。
9. 初始状态（R12）：`runStatusText` 增加 `idle:'未运行'`、`stopping:'正在停止'`；没有任何运行时 `#run-id` 只显示「尚未运行」（不带「 · 」后缀）。
10. 不使用 `window.confirm` / `alert` / `prompt`；不修改 B 的原生会话卡片、C1 的超时输入、运行接回逻辑。

### 4.7 `AGENTS.md`

用附录 B 的全文替换仓库根目录 `AGENTS.md`。以 UTF-8（无 BOM）、LF 写入，写完确认 NUL 为 0。

### 4.8 重启对账不再改写已结束运行（R07）

1. `plugin/lib/training-execution.js` 的 `reconcileInterruptedTrainingRuns`：
   - 先读 `state.json`；`state.status` 不在 `['checking', 'dispatching', 'running']` → `continue`，**不碰** `dispatch.json`。
   - 对仍在进行的运行：若有 `dispatch.json` 且其 `executionStatus !== 'closed'`，才改写为 `closed` / `host_restart`（签名逻辑不变）；已是 `closed` 的回执不改。
   - 然后照旧把 `state.json` 改为 `interrupted`。
   - 检查同目录其他会写 `host_restart` 的位置（`pipeline-guard.js` 约 56 行用 `flag:'wx'` 只新建不覆盖，`pipeline-execution.js` 约 70 行）：如存在覆盖已关闭记录的同类问题，按同一原则修正并在报告中列出；不存在则写明已检查。
2. 恢复被改写的 3 条回执（只限 1.6 所列 3 个路径）：
   - 用 Node 或 Python 读取 `git show 5468af34:<path>` 的**原始字节**写回（不得经 PowerShell 或 shell 重定向写文件）；
   - 写回后 `sha256(文件) === sha256(git cat-file blob 5468af34:<path>)`，并用 `verifyTrainingReceipt` 验证签名有效；
   - 扫描所有 `Training_Materials/runs/*/dispatch.json`，统计 `closeReason === 'host_restart'` 的数量与路径，写进报告（其余被改写的回执在 Git 中没有原值，无法恢复，只记录）。
3. 恢复完成后、步骤 3 重启**之前**，快照所有 `Training_Materials/runs/*/dispatch.json` 的 sha256 到 `docs/tasks/verify/results/e-receipts-before-restart.json`（ER 使用）。

### 4.9 步骤超时的状态时序（R08，`framework-agent-run.js`）

1. `onCancel` 的 timeout 分支：设置 `entry.timedOut = true`、`run.cancellationRequested = true`、`run.childTerminationConfirmed = false`、`run.status = 'stopping'`，写入 `run.error` / `step.error`（`STEP_TIMEOUT`，文案与 details 不变），**不再**在此处设置 `run.status = 'failed'`、`run.completedAt`、`step.status`、`step.completedAt`。
2. 子会话终止确认后，由现有 `finishCancellation` 按 `entry.timedOut` 把运行与当前步骤置为 `failed`（保持现有逻辑）。
3. 兜底：进入 timeout 的 `stopping` 后 120 秒仍未确认终止 → 运行置为 `failed`、`completedAt`，当前步骤 `failed`，`run.terminationUnconfirmed = true`，记录事件 `termination-unconfirmed`。现有「同一目标存在未确认终止的运行时拒绝新运行」的保护保持不变；之后若迟到的确认到达，照旧记录 `late-settlement` 并把 `childTerminationConfirmed` 置 true，不改 `failed`。
4. 手动停止（非超时）的时序不变。

### 4.10 脚本工具超时上限（R09）

1. `plugin/lib/trainer-schema.js` 脚本工具定义：`timeoutMs` 的 `maximum` 由 30000 改为 600000。
2. `framework-dsh-adapter.js`：
   - 检查改为 `definition.timeoutMs > 0 && definition.timeoutMs <= 600000`，报错文案「script timeout must be within 600 seconds」；
   - 步骤开始前，若某个登记脚本工具的 `timeoutMs` 大于该步骤的超时（`definition.timeoutMs ?? 300000`，与 4.9 同一来源），该步骤失败，错误码 `TOOL_TIMEOUT_EXCEEDS_STEP`，文案写明工具名与两个时长。

### 4.11 测试（新增 `plugin/test/e-real-candidate-run.test.mjs`，并在 `test/all.test.mjs` 末尾 import）

测试桩必须模拟真实行为，不得把参数原样回传当结果。至少覆盖：

1. 训练模式不传 `executionMode` → 运行记录 `CANDIDATE`，有 `source-bundle.json`，`sourceBundleSha256 === bundleSha256`，执行包指令 = 候选 revision 文件。
2. 发布模式不传 → `RELEASE`，同样保存 `source-bundle.json`。
3. 显式 `FRAMEWORK_TRAINING` / `SYNTHETIC_597` / 未知值 → `EXECUTION_MODE_INVALID`；有会话绑定时发起 SMOKE / BUSINESS → `EXECUTION_MODE_FORBIDDEN`。
4. 冻结 4.3 表每一行各一个失败用例（共 9 个，失败码逐一断言），以及一个成功用例（`version.json` 的 `validation = {runId, executionMode:'CANDIDATE', revisionId}`）。
5. 4.4 表每一行各一个用例（`publishable` / `publishBlockCode` 逐一断言）；`stage-release` 对不可发布版本失败且不写文件；`runId` 不一致 → `TRAINER_RELEASE_RUN_MISMATCH`；验证运行的 `businessGatePassed` 不参与判断。
6. 提示词矩阵：用桩捕获 `ctx.subagents.start` 的参数与脚本工具描述，断言 CANDIDATE / RELEASE 不含 4.5 第 1 条列出的字样、SMOKE / BUSINESS 仍含合成说明；`TRAINER_INSTRUCTIONS` 不含这些字样。
7. 工作区说明迁移：旧文本 → 被替换；其他内容 → 不动；不存在 → 写新文本。
8. 重启对账：已关闭回执（含 `closeReason` 为超时的）字节不变；`running` 状态的运行回执被关闭、状态变 `interrupted`；`completed` 状态的运行 `state.json` 与回执都不变。
9. 超时时序：超时后立即读取 → `stopping` + `STEP_TIMEOUT`；确认终止后 → `failed`；120 秒兜底（测试中可注入较短时长）→ `failed` + `terminationUnconfirmed: true`；兜底后同目标新运行被拒；手动停止时序不变。
10. 脚本超时：600000 通过 schema、600001 被拒；工具超时大于步骤超时 → `TOOL_TIMEOUT_EXCEEDS_STEP`。

`plugin/test/d-release-integrity.test.mjs` 中「用 SMOKE / BUSINESS 运行冻结、发布成功」的用例，按本任务规则改为断言 `TRAINER_FREEZE_SYNTHETIC_RUN`，冻结 / 发布成功部分改用 CANDIDATE 运行；其他因 1.6 所列原因失效的测试同样处理并记录。

### 4.12 宿主验收程序（Codex 在 `docs/tasks/verify/verify-b-host.mjs` 中新增 EC / EX / EL / EP / ER / ET / EM 七个步骤）

判定条件以本节为准，**只允许选择器、等待时间、路径等机械性调整**，调整写进报告。复用现有工具函数（`expect`、`note`、`waitRun`、`releasesState`、`activeReleaseFor`、`frozenList`、`contentCheck`、`versionRows`、`writeWorkflow`、`restoreWorkflow` 等）。EC 写 `docs/tasks/verify/results/e-state.json`，其他步骤读取。测试目标：工作流「新工作流 1」= `custom-workflow-1`。**EC、EX-1、EX-7、EL-3、EL-4 必须在页面上点按钮完成**；接口只用于构造异常、读取结果和恢复。

**EC 主流程（页面）**
- EC-0 预检（沿用 P-0、P-1），记录开工激活版本 `origActive`。
- EC-1 训练模式下：`button[data-exec="candidate"]` 处于激活状态；`#run` 文字含「真实候选」；`#run-input` 可见；「系统验证」分组内仍有 `data-exec="smoke"` / `"business"` 两个按钮；没有运行时 `#run-id` 文字为「尚未运行」且不含 `idle`。
- EC-2 `#run-input` 留空，点 `#run` → 出现新运行；接口读取：`executionMode === 'CANDIDATE'`、`mode === 'training'`、`targetId === 'custom-workflow-1'`；等待 `completed`。
- EC-3 该运行目录有 `source-bundle.json`；`sourceBundleSha256 === bundleSha256`；`revisionId` 等于当前候选 revision；每一步指令与候选 revision 文件内容逐字节相同，不含合成指令。
- EC-4 每一步 `validation.ok === true`；没有一步输出等于 `{answer:3}` 或 `{answer:597}`；若某步指令含 `answer equal to N`，则该步输出 `answer === N`。
- EC-5 页面点「冻结候选」→ toast 含「候选已冻结」；新冻结版本 `validation = {runId: EC-2 运行, executionMode: 'CANDIDATE', revisionId: EC-2 的 revision}`，`bundleSha256 === 运行的 sourceBundleSha256`，冻结文件内容 = 候选 revision。
- EC-6 切到发布审核页：新冻结行 `data-publishable="true"`、按钮可用；点「发布此版本」→ toast 含「已激活发布版本」；新 release 的 `frozenVersionId`、`verifiedRunId`、`validationMode === 'CANDIDATE'` 正确；激活指针 = 新 release。
- EC-7 工程模式点运行（`#run-input` 留空）→ 新运行 `executionMode === 'RELEASE'`、`releaseId` = 新 release、`completed`、有 `source-bundle.json`、输出不是 3 / 597。
- EC-8 发布审核页对 `origActive` 行点「切回此版本」→ 激活指针恢复为 `origActive`。

**EX 拒绝路径**
- EX-1 页面选 `smoke` 并运行至完成，点「冻结候选」→ toast 含「合成验证运行不能用于冻结」，冻结版本数不变；用接口以该运行 + 正确 `revisionId` 冻结 → `TRAINER_FREEZE_SYNTHETIC_RUN`。
- EX-2 页面选 `business` 运行至完成（可复用 `startBusinessFromPage`），接口冻结 → `TRAINER_FREEZE_SYNTHETIC_RUN`。
- EX-3 接口用 EC-2 运行冻结但不传 `revisionId` → `TRAINER_FREEZE_REVISION_REQUIRED`；传别的 revision → `TRAINER_FREEZE_REVISION_MISMATCH`。
- EX-4 接口用一个历史 `FRAMEWORK_TRAINING`（或缺失 executionMode）的已完成运行冻结 → `TRAINER_FREEZE_CANDIDATE_REQUIRED`。
- EX-5 接口发起 `executionMode:'FRAMEWORK_TRAINING'` 的运行 → `EXECUTION_MODE_INVALID`，没有新运行。
- EX-6 接口用 EC-5 冻结版本 + 另一个运行 ID 发布 → `TRAINER_RELEASE_RUN_MISMATCH`，没有新 release。
- EX-7 页面 `#run-input` 输入 `[1,2` 点运行、再输入 `[1,2]` 点运行 → 两次都 toast「运行输入必须是 JSON 对象」，运行数不变。

**EL 历史版本**
- EL-1 `context.frozenVersions`：`frozen-c2f9fe08-feb4-4dc1-a3b2-a672be7342c6`、`frozen-f48fab80-f02d-4863-9df9-c228b8fd3daa` 为 `publishable:false` / `TRAINER_FROZEN_SYNTHETIC_VALIDATION`；`frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312`、`frozen-00f99692-c936-453e-91e5-c0e2c6acb423` 为 `TRAINER_FROZEN_SYNTHETIC`；EC-5 的冻结版本为 `publishable:true`。
- EL-2 接口用 `frozen-c2f9fe08…` + 其验证运行发布 → `TRAINER_FROZEN_SYNTHETIC_VALIDATION`，没有新 release。
- EL-3 发布审核页：EL-1 中不可发布的行「发布此版本」禁用并显示对应原因；EC-5 的行可用。
- EL-4 页面对 `release-6aab1ccf-efee-4985-a591-dd2d7f36d1e7` 点「切回此版本」成功，再切回 `origActive`（已有发布版本不受影响）。
- EL-5 驱动程序**独立**读取磁盘上每个冻结版本的 `version.json` 和对应运行文件，按 4.4 表自行计算 `publishable` / `publishBlockCode`，与接口返回逐个比对，全部一致（报告中列出每个版本的结果）。驱动不得调用服务端的判定函数。

**EP 提示词**
- EP-1 页面打开 Agent X（`agent-2abe705b`）的训练会话后，其工作区 `Training_Materials/framework/control/sessions/<hash>/AGENTS.md` 不含 `Synthetic` / `synthetic`；统计所有工作区说明文件：旧文本数量为 0，非旧文本文件的内容与步骤 0 快照相同。
- EP-2 读取 `plugin/lib/trainer-preset.js` 中 `TRAINER_INSTRUCTIONS` 与 `framework-dsh-adapter.js` 的普通运行身份说明，不含 4.5 第 1 条列出的字样；SMOKE / BUSINESS 的合成说明仍存在。

**ER 重启不改写已结束记录**（步骤 3 的部署重启即为被测重启，不额外重启）
- ER-1 1.6 所列 3 个 `dispatch.json` 的 sha256 等于 `git cat-file blob 5468af34:<path>` 的 sha256。
- ER-2 所有 `Training_Materials/runs/*/dispatch.json` 中，`e-receipts-before-restart.json` 里已是 `closed` 的回执，重启后 sha256 全部不变。
- ER-3 统计并列出当前 `closeReason === 'host_restart'` 的回执数量与路径（只记录，不判失败）。

**ET 超时时序**（沿用 C1 步骤 H 制造超时的方法：把某一步超时设为 1 分钟，运行一个确实超过 1 分钟的步骤；结束后恢复工作流）
- ET-1 超时发生后 10 秒内读取运行：`status === 'stopping'`，`error.code === 'STEP_TIMEOUT'`，文案写明第几步；页面 `#run-error` 含「正在停止子会话」。
- ET-2 最终状态 `failed`，且满足其一：`childTerminationConfirmed === true`；或 `terminationUnconfirmed === true` 且从超时到 `completedAt` 不少于 120 秒。事件序列中 `cancellation-requested` 在终态之前。
- ET-3 若 ET-2 走的是未确认分支：立即对同一目标发起新运行被拒绝（沿用现有错误码）。若走的是已确认分支：此项记为 PASS 并注明「未触发」。

**EM 真实材料读取探针**（经接口构造测试数据，结束后恢复）
- EM-0 记录 `agent-T3` 当前候选文件（`agents/agent-T3/*`、它引用的 schema）的原内容。
- EM-1 经 `apply-changes` 新增 `tools/material-probe.json`（`adapter` 用现有 python 脚本适配器，`timeoutMs: 60000`，参数 `{"path": string}`）与 `tools/material-probe.py`（读取 `path` 指向文件的全部字节，向 stdout 输出 JSON：`{"size": 字节数, "sha256": 小写十六进制, "head": 前 4 字节十六进制}`）；把该工具加入 `agent-T3`，并把其指令临时改为「调用 material_probe，参数 path 取输入中的 materialPath，原样返回工具结果 JSON」，输出 schema 临时改为要求 `size`(整数)、`sha256`(字符串)、`head`(字符串)。提交被接受（同时证明 60000 毫秒的工具超时可以保存）。
- EM-2 以 `targetKind:'agent'`、`targetId:'agent-T3'`、`executionMode:'CANDIDATE'` 运行，输入 `{"materialPath": "<仓库绝对路径>\\Training_Materials\\Input_GlobalMaterial\\Dali_testmode.xlsx"}`；运行 `completed`，事件中出现该工具的 `tool-started` 与 `tool-completed`。
- EM-3 驱动用 **Python 子进程**直接读取同一文件，计算 `size` / `sha256` / `head`；与 EM-2 的输出逐项比较，把两组值和结论写进证据：三项相同且 `head === '504b0304'` → 结论「DSH 脚本进程读取材料为明文」；否则 → 结论「DSH 脚本进程读到的内容与 Python 不同（可能为密文）」。**两种结论都判 PASS**（本项要的是事实证据），结论原样写进报告。
- EM-4 恢复：`agent-T3` 候选文件恢复为 EM-0 的原内容、删除临时工具文件；恢复后当前候选中这些文件逐字节等于 EM-0；`custom-workflow-1` 仍可解析。

同时在 `docs/tasks/verify/README.md` 新增「任务 E 的附加步骤」一节（表格格式同 D 节），并注明：**DF、DS 从本任务起退出回归**（它们按 D 的规则用合成运行冻结，与 E 的规则相反），由 EC / EX / EL 取代。

---

## 5. 执行步骤

所有命令在仓库根目录执行；默认沙箱报 `EPERM`（含 `spawnSync python EPERM`）时用提升权限环境重跑同一命令。

### 步骤 0：准备
1. `git fetch github --prune`；`HEAD`、`github/master`、`github/main` 三者相同（应为本任务书所在提交或之后）。不一致 → 硬停止条件 1。
2. `git status --porcelain > .tmp-e-baseline-status.txt`（不提交）。
3. 备份将修改的文件为同目录 `.bak-20261004-taskE`（不提交，`.gitignore` 已忽略）。
4. 记录开工时 `custom-workflow-1` 的激活发布版本（应为 `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58`）。
5. 快照所有 `Training_Materials/framework/control/sessions/*/AGENTS.md` 的 sha256 到 `docs/tasks/verify/results/e-sessions-before.json`（EP-1 用）。

### 步骤 1：实现
按第 4 节修改（含 4.8 第 2、3 条的恢复与快照）。完成后：
```
node --check docs/tasks/verify/verify-b-host.mjs
node -e "const s=require('fs').readFileSync('docs/prototypes/agent-trainer-repair-prototype.html','utf8');const m=s.match(/<script>([\s\S]*)<\/script>/);require('fs').writeFileSync('.tmp-e-page.js',m[1])" && node --check .tmp-e-page.js
git grep -n -i -E "synthetic|合成|597|23\*24|1\+2" -- plugins/dsh-ptc-control-plane/lib/trainer-preset.js plugins/dsh-ptc-control-plane/lib/framework-dsh-adapter.js plugins/dsh-ptc-control-plane/lib/trainer-service.js
```
**通过标准**：前两条无输出；第三条的每一处命中都只出现在 SMOKE / BUSINESS 分支、合成常量定义或与模型无关的内部判断中（报告中逐条说明）。

### 步骤 2：测试
在 `plugins/dsh-ptc-control-plane` 下：
```
node --test test/e-real-candidate-run.test.mjs
node test/all.test.mjs
```
**通过标准**：新测试全部通过；全量 0 failed，passed ≥ 421 + 新增用例数。

### 步骤 3：部署（同时是 ER 的被测重启）
确认没有进行中的 framework run，且 `e-receipts-before-restart.json` 已生成 → `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`。
**通过标准**：Gate A/B/C 全部 exit 0；3080 返回 200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。本轮不改 `client/`，不重建 `lib/client.js`。
若之后因修复需要再次重启：重启前重新生成 `e-receipts-before-restart.json`，重启后重跑 ER。

### 步骤 4：宿主验收（按顺序，一次一步）
```
node docs/tasks/verify/verify-b-host.mjs --steps ER
node docs/tasks/verify/verify-b-host.mjs --steps EC
node docs/tasks/verify/verify-b-host.mjs --steps EX
node docs/tasks/verify/verify-b-host.mjs --steps EL
node docs/tasks/verify/verify-b-host.mjs --steps EP
node docs/tasks/verify/verify-b-host.mjs --steps ET
node docs/tasks/verify/verify-b-host.mjs --steps EM
node docs/tasks/verify/verify-b-host.mjs --steps DO
node docs/tasks/verify/verify-b-host.mjs --steps DP
node docs/tasks/verify/verify-b-host.mjs --steps A
node docs/tasks/verify/verify-b-host.mjs --steps K
node docs/tasks/verify/verify-b-host.mjs --steps H
```
**通过标准**：每条命令末行 `FAIL 0`；ER-1~ER-3、EC-1~EC-8、EX-1~EX-7、EL-1~EL-5、EP-1~EP-2、ET-1~ET-3、EM-1~EM-4 全部 PASS；DO、DP、A（A-7 允许 WARN）、K、H 全部 PASS。
DP、H 若有断言与本任务规则直接冲突（例如要求 `frozen-c2f9fe08…` 的「发布此版本」可用，或要求超时后立即为 `failed`），只允许把该断言改为符合 4.4 / 4.9 的预期，并在报告中写明原断言、新断言与原因；其他失败按缺陷处理。

### 步骤 5：只读复核
`node docs/tasks/verify/verify-b.mjs` → PASS 10 / FAIL 0。

### 步骤 6：写报告
用 Node 以 UTF-8 在第 10 节填写完成报告（不用 PowerShell 的 `Add-Content` / `Out-File`），写完确认 NUL 0、UTF-8 可解码。

### 步骤 7：提交与推送
1. 只 `git add`（写完整路径）：`AGENTS.md`、`docs/tasks/E-real-candidate-run.md`、`docs/tasks/verify/verify-b-host.mjs`、`docs/tasks/verify/README.md`、`docs/prototypes/agent-trainer-repair-prototype.html`、本任务改动的 `plugins/dsh-ptc-control-plane/lib/*.js`（报告中逐个列出）、`plugins/dsh-ptc-control-plane/test/e-real-candidate-run.test.mjs`、`plugins/dsh-ptc-control-plane/test/all.test.mjs`、按 1.6 修改的已有测试。不要 add `docs/tasks/verify/results/`、`Training_Materials/`、`publish/`、`.bak-*`、`.tmp-*`（恢复的 3 个回执在本机生效即可，`Training_Materials/runs/` 不进 Git）。
2. 提交信息：`[E] 真实候选运行成为主流程，并修正重启改写记录、超时状态、脚本超时上限等系统问题`
3. 推送 `github master` 与 `github main`，不加 `--force`；三个 ref 一致且 `0	0`。

---

## 6. 异常处理

总原则：同一问题最多换 3 种办法；不得放宽第 3 节与 4.12 的判定条件；不得手工改写冻结、发布、revision、bindings 文件。

| 编号 | 现象 | 处理 |
|---|---|---|
| 6.1 | 浏览器启动、宿主入口问题 | 按 `docs/tasks/B5-host-acceptance.md` 6.1、6.2 |
| 6.2 | EC-2 运行失败（某步输出不符合 schema） | 先看该步 `step-N.output.json` 与 `validation.errors`。这是候选 Agent 的真实内容问题，不是系统缺陷：**不得改写候选 Agent 指令或 schema 来迁就验收**；在报告中写明，并换用 4 个 Agent 的指令都完整的工作流目标重试（写明目标 ID）。仍无可用目标 → 硬停止条件 2，报告用户 |
| 6.3 | EC-3 没有 `source-bundle.json` | 核对 4.1 第 4 条是否生效、插件是否已重启 |
| 6.4 | EC-5 冻结被拒 | 按返回的失败码对照 4.3 表逐行排查；确认页面请求带了 `revisionId` |
| 6.5 | EL-5 有不一致 | 以 4.4 表为准修正服务端判定；不得修改驱动的独立计算逻辑 |
| 6.6 | EP-1 发现工作区说明文件仍是旧文本 | 确认迁移逻辑在打开 / 解析会话时执行；只替换逐字节相同的旧文本 |
| 6.7 | ER-1 不一致 | 确认用的是原始字节写回（Node / Python），不是经 shell 重定向；`git cat-file blob` 与写回文件逐字节比较 |
| 6.8 | ET-1 读不到 `stopping`（已经是 `failed`） | 核对 4.9 第 1 条是否删除了 timeout 分支里的 `failed` 赋值；若子会话确认极快（10 秒内已确认终止并置 failed），把 ET-1 的读取间隔缩短到超时后立即轮询（每 500 毫秒），并在报告中记录实际时序 |
| 6.9 | EM-2 子 Agent 没有调用工具 | 检查工具是否出现在该步骤的可用工具中（事件 `effectiveTools`）；指令写清工具名与参数；最多换 3 种指令写法，仍不调用 → 记录事件证据，EM-2 判 FAIL 并按第 7 节处理 |
| 6.10 | EM-4 恢复失败 | 不要手改 revision 文件；用 `apply-changes` 以 EM-0 记录的原内容重新提交 |
| 6.11 | 结束时激活指针未恢复 | 不要手改指针文件；用 `activate-release` 把 `custom-workflow-1` 指回步骤 0 第 4 条记录的版本 |
| 6.12 | 全量测试失败 | 与基线 421 对比；仅因 1.6 所列原因失败的按 4.11 末段处理，其余按第 7 节 |

## 7. 修复流程

定位 → 只改第 4 节涉及的文件 → 补能复现问题的测试 → 全量测试 0 失败 → 重启 Gate 通过（重启前按步骤 3 重新快照回执）→ 重跑失败步骤及其后的所有步骤（ER 与 EC 失败则从 ER 起全部重跑）。同一缺陷 3 次仍失败 → 硬停止条件 5。

## 8. 数据说明

- EC 每次新增 1 个真实候选运行、1 个冻结版本、1 个发布版本、1 个发布模式运行；EX、ET、EM 新增若干运行与 revision；激活指针最终恢复为开工值；`custom-workflow-1` 与 `agent-T3` 的候选内容最终与开工时逐字节相同（revision 编号会变）。这些数据保留，运行数据不进 Git。
- 3 个 9/22 回执恢复为原始字节；其他被改写且无原值的回执只记录，不改。
- 已有冻结、发布版本一律不改，只新增判定字段。
- 不删除任何会话、bindings、运行、冻结或发布记录。

## 9. Claude Code 复核方式

1. Git：三个 ref 一致；`git show --stat` 核对提交范围只含第 5 节步骤 7 列出的文件。
2. 逐条读 `docs/tasks/verify/results/verify-b-host-{ER,EC,EX,EL,EP,ET,EM,DO,DP,A,K,H}.json`，不看汇总。
3. **打开实际产出**：EC 的运行目录（`framework-run.json`、`source-bundle.json`、每步 output）、新冻结版本的 `version.json` 与 `bundle-manifest.json`、新 release 的 `release.json`；3 个恢复的回执与 `5468af34` 逐字节比较；EM 的运行输出与材料文件的 Python 读取结果。
4. 读 `AGENTS.md`，与附录 B 逐字比对。
5. 审 diff 中验收程序覆盖不到的部分：4.1 的模式归一化与会话限制、4.3 的校验顺序、4.4 的判定实现、4.5 的提示词分支、4.8 的对账顺序、4.9 的兜底计时、验收驱动中 EL-5 是否真的独立计算。
6. 在 Claude 内置浏览器中亲自做一次「真实候选运行 → 冻结 → 发布 → 切回」页面抽查。
7. 验收通过后更新 `docs/tasks/ISSUE-REGISTER.md` 与交接说明。

---

## 10. 完成报告（Codex 填写）

- 基线：HEAD / github/master / github/main = ；开工 custom-workflow-1 激活版本 = 。
- 改动摘要（逐个文件）：
- 提示词自查（步骤 1 第三条命令的每处命中及说明）：
- R07：恢复的 3 个回执 sha256 与 `5468af34` 对比；当前 `host_restart` 回执数量与路径；其他写 `host_restart` 位置的检查结论：
- 测试：e-real-candidate-run __/__；全量 __ passed / __ failed；修改的已有测试（测试名、原断言、新断言、原因）：
- 部署：重启产物路径；Gate A / B / C；3080；启动日志检查：
- 宿主验收：ER / EC / EX / EL / EP / ET / EM / DO / DP / A / K / H 各自的 PASS 项与统计：
- 关键值：EC 运行 ID、冻结版本 ID、发布版本 ID、发布模式运行 ID；EL-5 每个冻结版本的判定结果；ET 走的分支与实际时序；EM 两组读取值与结论；结束时激活版本：
- verify-b.mjs：
- 偏离：
- 提交 / 推送：

---

## 附录 A：用户原话（2026-10-03，语音输入；语音转写把整段重复了一遍，第二遍只保留第一遍没有的结尾，以「……」标出）

> 这里我还是想说清楚，本来我是不需要 smoke only 和 business only 的。为什么做了这些东西？那当时做 smoke only 的原因是，如果接入真实的业务流，然后来去看这套系统的话，实际上在执行的过程中会因为真实业务的流流流程有问题，或者是两个 agent 的呃交接的 schema 或者是合同有问题，导致。 无法顺利的运行，所以我才想做一套 smoke only 的验证。那这样的话，用最轻量化的 agent 执行流程来去验证我的系统是否有问题。那为什么做 business only 呢？原因是在于，呃，这套 smoke only 验证了我的系统有没有问题，但是无法验证我训练 agent 之后去优化 agent 的流程。那优化之后 agent 的执行。 这套工作流的时候会不会有问题？所以就增加了这个 business only 的。那实际上 business only 的话，其实它就是接入我真实的业务。那但是这里又存在一个问题，就是还是接入真实业务之后，可能会因为跟这个系统无关的卡点会影响到整个流程的验证。所以当时我给 business only 了一个假的。 呃，业务那就是换成五九七的合成指令来去执行，来通过这个来确认说，哎，我整个这一套的系统，那本身可以做 smoke only 的验证，同时呢，也可以通过 business only 来确认我的优化流程也是没有问题的。那后面其实只要这套流程经过了验证之后，实际上这些 agent 内部的。 呃，业务其实都应该是空的。之后，那最多来说就是 smoke only 这时候可以是保留，那 business only 这里的话，那我我实际上就是说，我最多只是需要去验证一下，它确实能跑通。那如果说本身你们开发之后已经保证了这个流程被通过 computer use 的功能点那些按钮，确认是没有问题了，那实际上我实际上就根本就不需要这些。 business only 的时候 ，agent 内部的工作流啊，或者说它执行的东西是有数据的，它是空的就可以了。因为接下来我就直接去通过聊天室训练，来去优化这些最终的执行流程就可以了，完全不需要，呃，说呃中间的这个597不能改啊，或者是什么……因为这个只是用验证的时候才会用到的东西而真实的流程里面完全不需要这些东西的，理解我，告诉我是不是做偏了

同日补充：「我希望这次执行，至少把问题修正50%以上，不要分成EFGHI等多个步骤才能完成。」

---

## 附录 B：新的 `AGENTS.md` 全文（照抄）

````markdown
# ATE PTC Direct Runtime — Agent Trainer main flow

`team/ptc/ptc_stage_registry.json` remains the authority for stage order and
owner. The former DFT and schematic execution flows, rules, gates, and checks
are preserved under
`team/ptc/native-control-plane/archive/DFT-SCHEMATIC-LEGACY-20260923/`.
They are historical references and are not part of the active Agent Trainer
flow.

## Main flow (from 2026-10-04)

Agent Trainer is the active system. Workflows and Agents are editable; Agents
are improved through chat-based training sessions; a validated candidate is
frozen and published.

1. Ordinary runs execute the candidate's real instructions, Skills and
   input/output schemas. Training-mode runs record `executionMode: CANDIDATE`;
   published-mode runs record `executionMode: RELEASE`. Both persist their
   exact execution bundle as `source-bundle.json`.
2. Agents may start empty (no business material, Skill or script) and are
   filled in through training. No fixed answer, expression or synthetic
   contract may be written into Agent instructions, Skills or schemas.
3. Freeze requires a completed `CANDIDATE` run of the exact target and
   revision in which every step completed and passed its output schema.
   Publishing requires a frozen version whose validation run can be proven to
   be such a run.
4. There is no business correctness gate in this flow. `businessGatePassed` is
   kept only so older records stay readable; it is not a run, freeze or
   publish condition.

## System verification tools (never a release basis)

- `SMOKE_ONLY` (input `1+2`, answer `3`) checks dispatch, sessions, contracts
  and handoff with the lightest possible Agents.
- `BUSINESS_ONLY` (input `23*24+45`, answer `597`) checks that a workflow still
  orchestrates correctly after training changes, without real business
  blockers.
- Both rewrite only the transient execution bundle at run time. Their
  instructions, inputs and expected answers never enter candidate files,
  schemas or ordinary runs. Their runs cannot be used to freeze or publish.
  They are started only from the workbench page, not from training sessions.
- Historical frozen or published versions that contain synthetic
  instructions, or whose validation basis is synthetic or cannot be proven,
  stay on disk unchanged and cannot be newly published. Existing activation
  pointers are not changed.

## Hash and write boundaries

- Use SHA-256 lowercase 64-character hexadecimal digests only. Generated
  evidence is hashed over exact on-disk bytes. Protected canonical material,
  if used in a future explicitly restored business path, is hashed only with
  Python's plaintext view via `scripts/hash_ate_plaintext.py`.
- Training runs write under `Training_Materials/runs/<runId>/`; published
  runs write under `publish/runs/<runId>/`. Historical business outputs and
  the legacy archive are not overwritten by any run or host restart.
- Run and verification data (`Training_Materials/runs/`, `publish/runs/`,
  request journals, `docs/tasks/verify/results/`) is not committed to Git.

## Sessions and data safety

- Never delete DSH sessions or files under
  `Training_Materials/framework/control/bindings/`.
- Never hand-edit revision, frozen-version or release files on disk; they are
  produced only through the trainer API.
- Never force-push or rewrite Git history.

## Archived experts and legacy business paths

- The eight expert profiles (DFT, schematic, strategy, method, reviewer,
  implementer, compile, evolution) and their receipts are archive-only and
  must not be dispatched. The PTC stage registry is intentionally empty.
- Do not reactivate the archived DFT/schematic workflow, business gates,
  schematic parser, Component-Statistic producer, SCH-Connect-Map generator or
  compile without a separate explicit request, training and release decision.
- The sections below are kept verbatim for history. They describe the scope
  before 2026-10-04 and are not the active flow.

### [History] Current user scope (2026-09-30)

The eight expert profiles and their receipts are archive-only for the current
release and must not be dispatched. The active registry is intentionally empty.
Use the synthetic expression `23*24+45` (answer `597`) only to verify the
Agent Trainer Agent/workflow plumbing, including editing, saving and running;
this path remains synthetic and must record `businessGatePassed: false`.

### [History] Eight-expert smoke contract

1. DFT, schematic, strategy, method, reviewer, implementer, compile, and
   evolution experts all receive exactly: `1+2等于几，把答案写在JSON里`.
2. Each expert is trained independently in a new run with a fresh DSH model
   child. The child has no tools and receives no private project material or
   archived expert instructions. It must return JSON with numeric `answer: 3`.
3. The whole-chain training run dispatches fresh children in registry stage
   order. DFT and schematic occupy the two `INPUT_SYNC` slots; the reviewer
   is dispatched at both review stages. Evolution is a final auxiliary smoke
   task, not an invented registry stage. Captain/host independently checks
   each new child result and stops on a missing, malformed, or non-3 answer.
4. Do not call the former DFT gate, schematic parser, Component-Statistic
   producer, SCH-Connect-Map generator, business gates, or compile in this
   smoke path. No previous specialist output can substitute for a fresh
   arithmetic response.
5. Freeze the eight trained profile snapshots and the completed orchestration
   evidence to `publish/versions/<releaseId>/`. Published mode uses the
   pinned snapshot and writes a new run under `publish/runs/<runId>/`, again
   dispatching fresh arithmetic children for every slot.
6. Every smoke result says `SMOKE_ONLY` and `businessGatePassed: false`. A
   passing arithmetic chain proves model invocation, stage handoff, and
   release replay only. It never certifies semiconductor work.

### [History] Explicit business-training mode

The user has explicitly requested a separate business execution mode for the
DFT and schematic INPUT_SYNC agents. It is opt-in through
`/api/ptc-control/business/*` and is labeled `BUSINESS_ONLY`; it keeps all
frozen materials, parser products, semantic-review evidence, and receipts under
`Training_Materials/runs/<runId>/`. It never reuses SMOKE_ONLY buttons or
published smoke releases. The smoke contract above remains unchanged, and the
business mode is not release-eligible until a separate business training and
release decision is made.
````
