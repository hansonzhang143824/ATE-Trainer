# 任务 D：冻结与发布完整性（冻结真实内容、识别被污染版本、版本时间与排序、发布页版本列表）

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录；插件目录简写为 `plugin/` = `plugins/dsh-ptc-control-plane/`）
- 编写：Claude（2026-10-03）。执行：Codex（`/goal`）。验收：Claude
- 本文件是本轮**唯一执行依据**。执行中忘了要做什么，回到第 1 节（目标）和第 5 节（步骤）。
- 完成后在第 10 节填写完成报告。

---

## 1. 目标（用户原话整理，不得偏离）

1. 系统总目标（用户原话整理）：搭一套系统——**工作流可以随意调整、Agent 可以随意编辑；工作流不变，Agent 通过训练会话持续优化、能力越来越强；之后可以固定版本（冻结）并发布**。SMOKE_ONLY（1+2=3）用最轻量的任务验证流程本身；BUSINESS_ONLY 当前**有意**使用合成 597 业务流，排除真实业务搭建问题的干扰。系统确认完全没问题后，才转向真实 ATE 业务。本轮仍属系统开发。
2. D0 盘点（`docs/tasks/D0-release-audit.md`，提交 `ea1ea7c`）之后，Claude 复核发现一个**阻断问题**：
   - 页面「冻结候选」使用当前运行 `state.liveRun`，页面只能发起 SMOKE_ONLY / BUSINESS_ONLY；
   - 服务端 `freeze` 取 `run.bundle`（`plugin/lib/trainer-service.js` freeze 分支），而这两种运行的执行包已被 `syntheticSmokeBundle` / `syntheticBusinessBundle` 改写成合成指令；
   - 结果：**冻结版本里保存的是 `# Synthetic SMOKE_ONLY verification` 合成指令，不是用户的 Agent**，但 `version.json` 仍声称对应某个候选 revision。D0 新建的 `frozen-cfb09c03…`、`frozen-00f99692…` 及其发布版本 `release-53dc2488…`、`release-74077b90…` 均如此；较早的 `frozen-9319cc9c…` 等是真实指令（合成改写引入之前）。
   - 发布模式下 SMOKE/BUSINESS 运行会再次改写，输出照样是 3 / 597，所以一直没被发现。
3. 本轮只做 D-1 ~ D-4（用户已确认）：
   - **D-1（阻断）冻结与发布保存真实内容**：合成验证运行同时保存改写前的真实执行包；冻结、发布使用真实执行包；记录验证方式。
   - **D-2（阻断）识别被污染的存量版本**：不改写旧文件；读取时识别出合成指令，列表中标出，禁止拿它发布、禁止激活（切回）它，禁止工作流引用它。
   - **D-3（重要）版本时间与序号**：新冻结、新发布写入创建时间与序号，列表按序号从新到旧，旧版本「时间未知」排最后。
   - **D-4（重要）发布页版本列表**：发布审核模式下显示当前工作流的冻结与发布版本、时间、验证方式、当前激活标识，可「发布此版本」「切回此版本」。
4. **不在本轮范围**：待审核（staged/review）状态、版本说明、版本对比（D-5，可延后）；真实业务（C2/DFT）；改变 SMOKE/BUSINESS 的合成改写本身；删除或改写任何已有冻结 / 发布文件。

**硬停止条件**（`docs/tasks/00-PLAN.md` 2.4 节，原文）：

> 1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
> 2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
> 3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
> 4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
> 5. 同一个问题尝试 3 种不同的解决办法后仍失败。

本轮**明确授权**：给 `context` 返回中的 `frozenVersions` 条目、`releases` 返回中的条目**新增字段并改变排序**（见 4.3）；给运行记录新增字段与文件。不得删除或改名已有字段。冻结、发布、激活只能经系统接口产生；不得手工改写 `publish/`、`versions/`、`revisions/` 下的已有文件。

---

## 2. 现状（Claude 已读代码确认，执行前请复核行号）

| 事实 | 位置 |
|---|---|
| `run`：`executionMode` 为 BUSINESS_ONLY / SMOKE_ONLY 时 `resolved = synthetic…Bundle(baseBundle)`，只把 `resolved` 交给 `runner.startRun` | `plugin/lib/trainer-service.js` 约 495~509 行 |
| 运行器只保存 `execution-bundle.json`（改写后的），记录 `bundleSha256` 与 `bundleArtifact`；`readRun` 校验后返回 `{...record, bundle}` | `plugin/lib/framework-agent-run.js` `startRun`（约 290 行起）、`readRun`（约 97 行） |
| `freeze`：要求完成的验证运行，`bundle = run.bundle` 后 `freezeTarget` | `trainer-service.js` 约 519~537 行 |
| `freezeTarget` 写 `versions/frozen-<uuid>/{bundle-manifest.json, version.json}`；`version.json` 字段：frozenVersionId、bundleSha256、revisionId、targetKind、targetId、workflowRevision、agentBindings | `plugin/lib/trainer-bundle.js` 约 199~210 行 |
| `listFrozenVersions` 按目录名 `sort()`（UUID 字符串序） | `trainer-bundle.js` 约 227~241 行 |
| 工作流步骤可引用冻结 Agent（`agentVersion.kind === 'frozen'`），解析时 `loadFrozenBundle` 取其文件 | `trainer-bundle.js` 约 80、91~93、127 行 |
| `stageRelease`：`evidenceCheck` 要求 `evidence.bundleSha256 === bundle.bundleSha256` 等；写 `publish/versions/release-<uuid>/{bundle-manifest.json, verification.json, release.json}` | `plugin/lib/trainer-release.js` 7~17、32~52 行 |
| `activateRelease` 写 `publish/active/<projectId>/<kind>/<targetId>.json`；`listReleases` 按目录名 `sort()` | `trainer-release.js` 54~61、73~85 行 |
| 页面「冻结候选」`freezeCandidate()` 用 `state.liveRun.runId`；「发布」`publishCandidate()` 用 `state.liveFrozen` + `state.liveRun`（刷新页面后无法发布之前的冻结版本） | `docs/prototypes/agent-trainer-repair-prototype.html` |
| 页面进入发布审核模式时 `loadLiveContext()` 以 `mode:'published'` 读取 context | 同上 |

---

## 3. 本轮要交付的行为（验收以此为准）

| 编号 | 行为 | 验证 |
|---|---|---|
| D-1a | SMOKE_ONLY / BUSINESS_ONLY 运行记录 `sourceBundleSha256`（改写前真实执行包），并保存真实执行包；`readRun` 返回 `sourceBundle` | DF-2、单测 |
| D-1b | 用合成验证运行冻结 → 冻结文件中的指令、工作流文件 = 该运行对应候选 revision 的真实内容；`version.json` 记录 createdAt、sequence、validation{runId, executionMode}；bundleSha256 = 运行的 sourceBundleSha256 | DF-3 ~ DF-5 |
| D-1c | 用该冻结版本 + 同一验证运行发布 → 发布文件为真实内容；`release.json` 记录 createdAt、sequence、validationMode；激活后发布模式 SMOKE 运行仍正常 | DF-6、DF-7 |
| D-1d | 用 D 之前的合成运行（没有真实执行包）冻结 → 拒绝 `validation_source_unavailable` | DS-5 |
| D-2 | 被污染（含合成指令）的冻结、发布版本在列表中 `contaminated: true`；用它发布 → `TRAINER_FROZEN_SYNTHETIC`；激活它 → `TRAINER_RELEASE_SYNTHETIC`；工作流引用被污染的冻结 Agent → `TRAINER_FROZEN_SYNTHETIC` | DS-1 ~ DS-4、单测 |
| D-3 | 冻结、发布列表按 sequence 从大到小，无 sequence 的旧版本排最后（旧版本之间按 ID），旧版本 createdAt 为 null | DO-1、DO-2 |
| D-4 | 发布审核页 `#version-list` 显示当前工作流的版本行、时间 / 时间未知、验证方式、当前激活、合成指令标识；「切回此版本」生效；被污染与当前激活的按钮禁用 | DP-1 ~ DP-5；「发布此版本」由 Claude 读代码复核 |

---

## 4. 实现规格

### 4.1 合成标识（`plugin/lib/trainer-bundle.js`）

1. 新增并导出：
   ```js
   export const SYNTHETIC_INSTRUCTION_RE = /^# Synthetic (SMOKE_ONLY|BUSINESS_ONLY) verification/;
   export function syntheticInstructionRefs(bundle) // 返回 bundle.steps 中 instructionsRef 指向的文件内容匹配上式的 ref 列表（去重，按出现顺序）
   ```
2. `trainer-service.js` 中 `SYNTHETIC_SMOKE_INSTRUCTIONS` / `SYNTHETIC_BUSINESS_INSTRUCTIONS` 的第一行必须匹配该正则（新增单测断言：对 `syntheticSmokeBundle` / `syntheticBusinessBundle` 的结果调用 `syntheticInstructionRefs` 非空；如这两个函数未导出，导出它们或导出常量，二选一）。

### 4.2 运行记录保存真实执行包（D-1a）

1. `trainer-service.js` 的 `run`：当 `executionMode` 为 BUSINESS_ONLY 或 SMOKE_ONLY 时，调用 `runner.startRun({..., bundle: resolved, sourceBundle: baseBundle })`；其他情况不传 `sourceBundle`。
2. `framework-agent-run.js` `startRun`：
   - 传入 `sourceBundle` 时：深拷贝冻结；用与 `bundle` 相同的 `verifyBundle` 校验；要求与 `bundle` 的 `projectId`、`targetKind`、`targetId`、`revisionId`、`workflowRevision`、以及每一步的 `stepId`/`agentId`/`agentRevision` 完全一致，否则 `fail('SOURCE_BUNDLE_MISMATCH', …)`；用 `store.write(dir, 'source-bundle.json', sourceBundle, true)` 保存，记录 `run.sourceBundleArtifact`（与 `bundleArtifact` 同结构）和 `run.sourceBundleSha256 = sourceBundle.bundleSha256`。
   - 未传时：`run.sourceBundleSha256 = bundle.bundleSha256`，`run.sourceBundleArtifact = null`。
3. `readRun`：
   - 有 `sourceBundleArtifact`：读取 `source-bundle.json`，校验文件 sha 与 `sourceBundleArtifact.sha256`、内容 `bundleSha256 === record.sourceBundleSha256`，不符 `fail('RUN_BUNDLE_CHANGED', 'stored source bundle changed')`；返回 `sourceBundle`。
   - 无 artifact 且 `record.sourceBundleSha256 === record.bundleSha256`：`sourceBundle = bundle`。
   - 旧记录（没有 `sourceBundleSha256` 字段）：`executionMode` 为 SMOKE_ONLY / BUSINESS_ONLY 时 `sourceBundle = null`；否则 `sourceBundle = bundle`。

### 4.3 冻结与发布（D-1b ~ D-3）

1. `trainer-service.js` `freeze`：
   - 保留现有校验（completed、validation.ok、目标一致）；
   - `bundle = run.sourceBundle`；为 null 时 `fail('validation_source_unavailable', '该验证运行没有保存真实执行包（D 之前的合成运行），请重新运行一次验证后再冻结')`；
   - `syntheticInstructionRefs(bundle)` 非空时 `fail('TRAINER_FROZEN_SYNTHETIC', '执行包包含合成指令，不能冻结')`（防御）；
   - 调用 `freezeTarget({..., bundle, validation: { runId: run.runId, executionMode: run.executionMode ?? 'FRAMEWORK_TRAINING' } })`。
2. `trainer-bundle.js` `freezeTarget`：`version.json` 在现有字段之外新增 `createdAt`（ISO 字符串）、`sequence`（该项目冻结版本的递增整数，从现有最大 sequence + 1 开始，旧版本视为 0）、`validation`（上面的对象，未传则 null）。序号分配必须在 `trainerLock` 内完成（锁路径用项目的 `versions` 目录或同级专用锁目录），避免并发重复。`loadFrozenBundle` 的完整性校验不变（新字段不参与比较）。
3. `listFrozenVersions` 每个条目在现有字段之外新增：`createdAt`（无则 null）、`sequence`（无则 null）、`validation`（无则 null）、`contaminated`（布尔）、`contaminatedRefs`（数组）。排序：有 sequence 的按 sequence 从大到小，其后是无 sequence 的旧版本，按 frozenVersionId 字符串升序。
4. `trainer-release.js`：
   - `stageRelease`：加载冻结后**先**检查 `syntheticInstructionRefs`，非空 `trainerFail('TRAINER_FROZEN_SYNTHETIC', '该冻结版本包含合成指令，不能发布')`；`evidenceCheck` 中的 sha 比较改为 `(evidence.sourceBundleSha256 ?? evidence.bundleSha256) !== bundle.bundleSha256`，其余条件不变；`verification.json` 中 `bundleSha256` 写冻结版本的 sha，新增 `executionBundleSha256`（= `evidence.bundleSha256`）与 `executionMode`；`release.json` 新增 `createdAt`、`sequence`（发布版本的独立递增序号，规则同冻结，在锁内分配）、`validationMode`（= `evidence.executionMode ?? 'FRAMEWORK_TRAINING'`）。
   - `activateRelease`：读取发布后检查其 bundle 的 `syntheticInstructionRefs`，非空 `trainerFail('TRAINER_RELEASE_SYNTHETIC', '该发布版本包含合成指令，不能激活')`，不写指针。
   - `listReleases`：`releases` 每个条目 = 原 metadata + `createdAt`（无则 null）+ `sequence`（无则 null）+ `contaminated` + `contaminatedRefs`；排序规则同 4.3 第 3 条（旧版本按 releaseId 升序）。`active` 不变。
   - `loadReleaseBundle` **不**加拦截（不影响已激活版本的读取）。
5. 工作流引用冻结 Agent：`resolveBundle` 中通过 `loadFrozenBundle` 取冻结 Agent 时，若该冻结版本 `syntheticInstructionRefs` 非空，`trainerFail('TRAINER_FROZEN_SYNTHETIC', '工作流引用的冻结 Agent 包含合成指令')`。

### 4.4 页面 `docs/prototypes/agent-trainer-repair-prototype.html`（D-4，接口写死，验收程序依赖）

1. 在工作流区域 `#steps` 之后新增 `<section id="version-list"></section>`。**只在发布审核模式（`state.product==='release'`）显示内容**；其他模式清空并隐藏。
2. 数据：进入发布审核模式、切换工作流、发布或切回成功后刷新：`context`（mode:'published'）的 `frozenVersions` 与 `releases` 接口（mode:'published'）。只显示**当前工作流**（`targetKind==='workflow' && targetId===当前 workflowId`）的条目，顺序按接口返回。
3. 每个版本一行：
   - 冻结：`<div data-version-row data-kind="frozen" data-id="{frozenVersionId}" data-active="false" data-contaminated="{true|false}">`
   - 发布：`<div data-version-row data-kind="release" data-id="{releaseId}" data-active="{是否当前激活}" data-contaminated="{true|false}">`
   - 行内文字依次包含：「冻结」或「发布」；有 sequence 时 `#{sequence} · {YYYY-MM-DD HH:mm}`（本地时间），否则「时间未知」；`验证 {executionMode / validationMode}`（无则「验证 未知」）；ID 前 16 位；当前激活的发布行包含「当前激活」；被污染的行包含「合成指令，不可发布」（冻结）或「合成指令，不可激活」（发布）。
4. 按钮：
   - 冻结行：`<button data-frozen-publish="{frozenVersionId}">发布此版本</button>`；被污染、或 `validation?.runId` 缺失时禁用。点击：`stage-release`（mode:'published'，frozenVersionId，runId = `validation.runId`）→ `activate-release` → toast「已激活发布版本：{releaseId}」→ 刷新列表；失败 toast「发布失败：{message}」。
   - 发布行：`<button data-release-activate="{releaseId}">切回此版本</button>`；被污染、或已是当前激活时禁用。点击：`activate-release` → toast「已切回发布版本：{releaseId}」→ 刷新列表与 `loadLiveContext()`；失败 toast「切回失败：{message}」。
   - 不使用 `window.confirm` / `alert` / `prompt`。
5. 现有 `freezeCandidate` / `publishCandidate` 保留；它们走同样的服务端校验。不修改 C1 的超时输入、`#run-error`、运行接回逻辑，不修改 B 的原生会话卡片。

### 4.5 测试（新增 `plugin/test/d-release-integrity.test.mjs`，并在 `test/all.test.mjs` 末尾 import）

至少覆盖（测试桩必须模拟真实行为，不得把参数原样回传当结果）：
1. SMOKE_ONLY 合成运行 → `readRun` 有 `sourceBundle`，`sourceBundleSha256 ≠ bundleSha256` → `freeze` 得到的冻结 manifest 中每一步指令 = 候选 revision 文件；`version.json` 有 createdAt / sequence=1 / validation.executionMode='SMOKE_ONLY'。
2. BUSINESS_ONLY 同上（sequence 递增）。
3. 用 1 的冻结版本与运行 `stage-release` 成功；`release.json` 的 validationMode、sequence、createdAt；`verification.json` 的 bundleSha256 = 冻结 sha、executionBundleSha256 = 运行的 bundleSha256。
4. 旧格式合成运行记录（无 sourceBundleSha256、executionMode='SMOKE_ONLY'）→ `freeze` 失败 `validation_source_unavailable`。
5. 被污染的冻结版本（测试中用 `freezeTarget` 直接冻结一个合成执行包制造）→ `listFrozenVersions` 中 `contaminated:true`；`stageRelease` → `TRAINER_FROZEN_SYNTHETIC`；工作流引用它 → `TRAINER_FROZEN_SYNTHETIC`。
6. 被污染的发布版本（测试临时目录中构造）→ `listReleases` 中 `contaminated:true`；`activateRelease` → `TRAINER_RELEASE_SYNTHETIC`，指针不变。
7. 排序：3 个新冻结 + 1 个无 sequence 的旧冻结 → 顺序为 3、2、1、旧；发布同理。
8. `startRun` 传入目标不一致的 `sourceBundle` → `SOURCE_BUNDLE_MISMATCH`；篡改 `source-bundle.json` 后 `readRun` → `RUN_BUNDLE_CHANGED`。
9. 4.1 第 2 条的合成常量断言。

已有测试若仅因**新增字段或排序**而失败，可以修改断言（在报告「偏离」中逐个列出测试名与原因）；因其他原因失败视为缺陷，按第 7 节修复。

---

## 5. 执行步骤

所有命令在仓库根目录执行；默认沙箱报 `EPERM`（含 `spawnSync python EPERM`）时用提升权限环境重跑同一命令。

### 步骤 0：准备
1. `git fetch github --prune`；`HEAD`、`github/master`、`github/main` 三者相同（应为 `ea1ea7c` 或之后）。不一致 → 硬停止条件 1。
2. `git status --porcelain > .tmp-d-baseline-status.txt`（不提交）。确认 Claude 已放入、未提交的文件存在：`docs/tasks/D-release-integrity.md`（本文件）、`docs/tasks/verify/verify-b-host.mjs`（新增步骤 DF/DS/DO/DP）、`docs/tasks/verify/README.md`。
3. 备份将修改的文件为同目录 `.bak-20261003-taskD`（不提交）：页面、`trainer-bundle.js`、`trainer-release.js`、`trainer-service.js`、`framework-agent-run.js`。
4. 记录开工时 `custom-workflow-1` 的激活发布版本（`releases` 接口 `active`，应为 `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58`）。

### 步骤 1：实现
按第 4 节修改。完成后：
```
node --check docs/tasks/verify/verify-b-host.mjs
node -e "const s=require('fs').readFileSync('docs/prototypes/agent-trainer-repair-prototype.html','utf8');const m=s.match(/<script>([\s\S]*)<\/script>/);require('fs').writeFileSync('.tmp-d-page.js',m[1])" && node --check .tmp-d-page.js
```
**通过标准**：两条都无输出。

### 步骤 2：测试
在 `plugins/dsh-ptc-control-plane` 下：
```
node --test test/d-release-integrity.test.mjs
node test/all.test.mjs
```
**通过标准**：新测试全部通过；全量 ≥ 420 passed（原 411 + 新增至少 9）、0 failed。

### 步骤 3：部署
确认没有进行中的 framework run → `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`。
**通过标准**：Gate A/B/C 全部 exit 0；3080 返回 200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。本轮不改 `client/`，不重建 `lib/client.js`。

### 步骤 4：宿主验收（按顺序，一次一步）
```
node docs/tasks/verify/verify-b-host.mjs --steps DF
node docs/tasks/verify/verify-b-host.mjs --steps DS
node docs/tasks/verify/verify-b-host.mjs --steps DO
node docs/tasks/verify/verify-b-host.mjs --steps DP
node docs/tasks/verify/verify-b-host.mjs --steps A
node docs/tasks/verify/verify-b-host.mjs --steps K
```
**通过标准**：每条命令末行 `FAIL 0`；DF-1~DF-8、DS-1~DS-5、DO-1~DO-2、DP-1~DP-5 全部 PASS；A-1~A-8（A-7 允许 WARN）、K-1~K-5 PASS（回归 B 与 C1）。
说明：DF 会临时修改「新工作流 1」、新建 2 个冻结版本与 1 个发布版本、临时激活后切回，结束时自动恢复并写 `docs/tasks/verify/results/d-state.json`；DS/DO/DP 读取该文件。DS 默认使用 D0 盘点中的版本与运行 ID（见驱动 `--contaminated-frozen` 等参数），如 ID 不存在按 6.4 处理。

### 步骤 5：只读复核
`node docs/tasks/verify/verify-b.mjs` → PASS 10 / FAIL 0。

### 步骤 6：写报告
用 Node 以 UTF-8 在第 10 节填写完成报告（不用 PowerShell 的 `Add-Content`/`Out-File`），写完确认 NUL 0、UTF-8 可解码。

### 步骤 7：提交与推送
1. 只 `git add`（写完整路径，不要用 `plugin/` 简写）：`docs/tasks/D-release-integrity.md`、`docs/tasks/verify/verify-b-host.mjs`、`docs/tasks/verify/README.md`、`docs/prototypes/agent-trainer-repair-prototype.html`、`plugins/dsh-ptc-control-plane/lib/trainer-bundle.js`、`plugins/dsh-ptc-control-plane/lib/trainer-release.js`、`plugins/dsh-ptc-control-plane/lib/trainer-service.js`、`plugins/dsh-ptc-control-plane/lib/framework-agent-run.js`、`plugins/dsh-ptc-control-plane/test/d-release-integrity.test.mjs`、`plugins/dsh-ptc-control-plane/test/all.test.mjs`，以及按 4.5 末段修改的已有测试文件（报告中逐个列出）。不要 add `docs/tasks/verify/results/`、`Training_Materials/`、`publish/`、`.bak-*`、`.tmp-*`。
2. 提交信息：`[D] 冻结与发布完整性：冻结真实内容、识别合成污染版本、版本时间排序与发布页版本列表`
3. 推送 `github master` 与 `github main`，不加 `--force`；三个 ref 一致且 `0	0`。

---

## 6. 异常处理

总原则：同一问题最多换 3 种办法；不得修改验收程序的判定条件（只允许选择器、超时、路径等机械性修正，diff 写进报告）；不得手工改写冻结、发布、revision、bindings 文件。

| 编号 | 现象 | 处理 |
|---|---|---|
| 6.1 | 浏览器启动、宿主入口问题 | 按 `docs/tasks/B5-host-acceptance.md` 6.1、6.2 |
| 6.2 | DF-2 没有 `sourceBundleSha256` | 核对 4.2 是否生效、插件是否已重启；`runs` 接口返回的是 `readRun` 结果 |
| 6.3 | DF-3/DF-5 报「是合成指令」或「与候选 revision 内容不同」 | 看证据 `byStep.DF` 的 `DF.freeze1.content.bad`；确认 `freeze` 用的是 `run.sourceBundle` 而不是 `run.bundle`；确认运行的 revisionId 与 DF-1 的 revision 相同 |
| 6.4 | DS 的默认 ID 在本机不存在（DS-1/DS-2 显示「缺失」） | 用 `releases` 接口与 `context.frozenVersions` 找出 D0 新建的两个冻结、两个发布版本与 D0 的验证运行，经驱动参数传入（`--contaminated-frozen a,b --contaminated-release c,d --legacy-run r`），在报告中写明 |
| 6.5 | DS-5 返回的不是 `validation_source_unavailable` | 若为 `validation_required`：该运行目标或状态不符，换 D0 中 custom-workflow-1 的另一个已完成 SMOKE 运行；仍不符按缺陷处理 |
| 6.6 | DP 找不到 `#version-list` 行 | 核对 4.4 的元素与属性名、发布审核模式切换后是否刷新列表；不要改验收程序 |
| 6.7 | DF-8 / DP-5 恢复失败 | 不要手改指针文件；用 `activate-release` 把 `custom-workflow-1` 指回步骤 0 第 4 条记录的版本，用 `apply-changes` 恢复工作流原内容（证据 `DF.restore`） |
| 6.8 | 全量测试失败 | 与基线 411 对比；仅因新字段 / 排序的按 4.5 末段处理，其余按第 7 节 |

## 7. 修复流程

定位 → 只改第 4 节涉及的文件 → 补能复现问题的测试 → 全量测试 0 失败 → 重启 Gate 通过 → 重跑失败步骤及其后的所有步骤（DF 失败则 DF 起全部重跑）。同一缺陷 3 次仍失败 → 硬停止条件 5。

## 8. 数据说明

- DF 每次运行新增 2 个冻结版本、1 个发布版本和 3 个合成运行，激活指针最终恢复；这些新版本是真实内容，保留。
- D0 产生的被污染版本保留不动（本轮只识别与拦截）。
- 不删除任何会话、bindings、运行、冻结或发布记录。

## 9. Claude 复核方式

读第 10 节、`results/verify-b-host-{DF,DS,DO,DP,A,K}.json` 与 `verify-b-host.json` 的证据；打开 DF 新建的冻结与发布文件确认指令是真实内容；审 diff（重点 4.2 的 readRun 回退规则、4.3 的锁内序号与 sha 比较、4.4 的「发布此版本」按钮）；核对 Git ref 与 `.git/index` 中的提交范围。

---

## 10. 完成报告（Codex 填写）

- 基线：HEAD / github/master / github/main = ea1ea7c2b2c4c1a11e43c6687a060064acf1c5a6；开工 custom-workflow-1 激活版本 = release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58。
- 改动摘要：trainer-bundle 保存真实 source bundle、识别合成指令、冻结序号/时间/验证信息并排序；framework-agent-run 保存并校验 source-bundle.json；trainer-service 冻结真实包并阻断历史合成运行；trainer-release 阻断污染版本发布/激活并记录发布序号/验证方式；Agent Trainer 页面加入发布审核版本列表、污染标识、发布/切回按钮，并防止异步模式响应覆盖；验收脚本修正工作流按 ID 恢复和等待具体 DF 发布行；新增 D 完整性专项测试并接入全量测试。
- 测试：d-release-integrity 10/10；全量 421 passed / 0 failed / 0 cancelled。未修改既有业务测试；新增 plugins/dsh-ptc-control-plane/test/d-release-integrity.test.mjs 并由 test/all.test.mjs 引入。
- 部署：最近一次重启产物 C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261003-191028；Gate A=0、Gate B=0、Gate C=0；3080=200；启动日志无 plugin tree failed to load、ERR_MODULE_NOT_FOUND、ERR_PACKAGE_PATH_NOT_EXPORTED、input hint must not be empty。
- 宿主验收：
  - DF：PASS DF-1、DF-2、DF-3、DF-4、DF-5、DF-6、DF-7、DF-8；结果 PASS 10 / FAIL 0 / WARN 0。
  - DS：PASS DS-1、DS-2、DS-3、DS-4、DS-5；结果 PASS 7 / FAIL 0 / WARN 0。
  - DO：PASS DO-1、DO-2；结果 PASS 4 / FAIL 0 / WARN 0。
  - DP：PASS DP-1、DP-2、DP-3、DP-4、DP-5；结果 PASS 7 / FAIL 0 / WARN 0。
  - A：PASS A-1、A-2、A-3、A-4、A-5、A-6、A-7、A-8；结果 PASS 10 / FAIL 0 / WARN 0。
  - K：PASS K-1、K-2、K-3、K-4、K-5；结果 PASS 7 / FAIL 0 / WARN 0。
- 关键值：DF 新冻结 frozen-c2f9fe08-feb4-4dc1-a3b2-a672be7342c6 / frozen-f48fab80-f02d-4863-9df9-c228b8fd3daa；发布 release-6aab1ccf-efee-4985-a591-dd2d7f36d1e7；验证运行 framework-478f206b-05ca-43e7-9bd8-b9b9ff4811e5（SMOKE_ONLY）、framework-d5b0e800-d2ef-4ade-9299-5a31ff092bbe（BUSINESS_ONLY）、framework-7e334925-9455-4ac8-9627-830420e1c8cf（published smoke）；结束时激活版本 release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58。
- verify-b.mjs：最终检查 PASS 10 / FAIL 0；snapshot 初始 PASS 3 / FAIL 0；compare 在任何 DF 数据变更前运行，因 D 计划允许新增版本字段/排序显示 21 处预期漂移，结果 PASS 0 / FAIL 3，已如实记录；DF/DS/DO/DP/A/K 之后再次 compare 的 revision/新增数据漂移同样不作为最终检查。
- 偏离：首次 DF 因验收脚本在改名后按旧工作流名称恢复，出现 DF-X“候选中没有 workflows/null.json”；未改写版本/发布文件，已通过正式 apply-changes 恢复候选并修正验收脚本 restoreWorkflow 按原始 path/ID 读取。首次 DP 因脚本只等待任意冻结行而早于异步发布列表读取，出现 3 个机械性误报；已改为等待具体 DF release 行后重跑，DP 7/7。compare 的字段/排序漂移是 D 规格明确授权的 context 新字段，未删除或改名原有字段。构造并清理：DF 生成的验证运行/冻结/发布证据按验收脚本保留；临时备份与 .tmp-d-page.js 已清理；未删除任何 DSH 会话或 bindings。
- 提交 / 推送：主实现提交 3c233335c08171ffa5f5083202334d29d6aa1a6b；本报告补充提交待生成；当前 github/master=3c233335c08171ffa5f5083202334d29d6aa1a6b、github/main=3c233335c08171ffa5f5083202334d29d6aa1a6b，本地与 github/main rev-list 0/0。
