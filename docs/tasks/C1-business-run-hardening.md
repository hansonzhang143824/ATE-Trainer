# 任务 C1：业务运行加固

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录）
- 编写：Claude（2026-10-03）。执行：Codex（`/goal` 模式）。验收：Claude
- 本文件是本轮**唯一的执行依据**。执行中忘了要做什么，回到第 1 节（目标）和第 5 节（步骤）。
- 完成后在本文件末尾第 10 节填写完成报告。

---

## 1. 目标（用户原话整理，执行中不得偏离）

1. 用户的总策略：**先用合成题（BUSINESS_ONLY 的 23*24+45=597）把整套系统做完、确认没有问题，再停止系统开发，专注搭建真正的 ATE 业务线。** 本轮属于系统开发，不做任何真实业务内容。
2. 本轮只做 C1 的五项（用户已确认）：
   1. **断开旧 TM109 业务流水线的入口**（代码保留，不删除）；
   2. **单步超时可配置**：新步骤默认 5 分钟，上限 30 分钟；页面跟踪上限按工作流计算，最多 3 小时；超时提示写明是哪一步；
   3. **超时真正生效的验证**（用合成题 + 临时把某一步超时调到 1 秒触发，不做真实 DFT 业务；DFT 解析试点是后续的 C2，本轮不碰）；
   4. **业务运行进行中刷新页面能接回**；
   5. **DSH 重启时未结束的业务运行被标为「已中断」，页面不被挡住，可以重新发起**。
3. 不在本轮范围：DFT 解析试点（C2）、冻结版本排序与发布审核（D）、删除旧流水线代码、Agent 撤销删除、删除时连带移除步骤。

**硬停止条件**（`docs/tasks/00-PLAN.md` 2.4 节，原文）：

> 1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
> 2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
> 3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
> 4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
> 5. 同一个问题尝试 3 种不同的解决办法后仍失败。

本轮**允许**修改 `lib/trainer-schema.js`（上限与 businessPipeline 两处，见 4.2），这是本任务书明确授权的范围。

---

## 2. 现状（Claude 读代码确认，执行前请复核）

| 事实 | 位置 |
|---|---|
| 页面「运行」按钮：`runTrainer()` 中 `if(state.exec==='business'&&currentWorkflow()?.businessPipeline)return runBusinessPipeline();`，工作流带 `businessPipeline` 字段时分流到旧 TM109 流水线（`/api/ptc-control/training-runs` + `/state` 轮询，状态可能为 `unknown`） | `docs/prototypes/agent-trainer-repair-prototype.html` |
| 当前候选 6 个工作流都**没有** `businessPipeline` 字段，旧流水线实际不会被触发；但数据格式仍允许写入它 | `lib/trainer-schema.js` 的 `workflowDefinition` |
| 新框架 BUSINESS_ONLY：`trainer-service.js` 的 `run` 把执行包改写成 597 合成题（`syntheticBusinessBundle`），由 `framework-agent-run.js` 执行；状态只有 queued/preparing/running/pausing/paused/stopping/completed/failed/cancelled/interrupted | `lib/trainer-service.js`、`lib/framework-agent-run.js` |
| DSH 重启：`mountTrainerHost` 调 `runner.reconcileInterrupted()`，把非终态且不在内存中的运行标为 `interrupted`，`error.code = 'HOST_RESTARTED'` | `lib/trainer-host.js`、`lib/framework-agent-run.js` |
| 单步超时：运行器 `createTrainingLifecycle({ timeoutMs: definition.timeoutMs ?? 300000 })`；超时后错误信息为 `training execution exceeded N ms`，运行判 `failed` | `lib/framework-agent-run.js`、`lib/training-lifecycle.js` |
| 执行包里步骤未写超时时默认 `120000` | `lib/trainer-bundle.js`（`timeoutMs: step.timeoutMs ?? 120000`） |
| 数据格式：`timeoutMs` 最大 `480000`（8 分钟） | `lib/trainer-schema.js` |
| 页面保存工作流：`workflowDefinition(wf)` 每步写 `timeoutMs: prior.timeoutMs \|\| 120000`，按**位置**继承旧步骤属性（移动步骤时 stepId/timeoutMs 留在原位置，不跟着 Agent 走） | 页面 `workflowDefinition` |
| 页面跟踪运行：`refreshLiveRun` 固定最多 15 分钟（`LIVE_RUN_POLL_MAX_MS`）就停止刷新 | 页面 |
| 页面刷新后接回：`resumeActiveLiveRun` 接回最近一个非终态的 `framework-run`（冒烟与业务都适用；业务接回此前没有实测） | 页面 |

---

## 3. 本轮要交付的行为（验收以此为准）

| 编号 | 行为 | 由哪个检查验证 |
|---|---|---|
| C1-1 | 页面「运行」不再分流到旧流水线；保存带 `businessPipeline` 的工作流被服务端拒绝，错误信息含 `businessPipeline` | K-1、K-2 |
| C1-2a | 单步超时上限 30 分钟：`1800000` 可保存，`1800001` 被拒绝 | K-3、K-4 |
| C1-2b | 步骤卡片上有「超时（分钟）」输入框，可改、可保存，非法值被拒绝 | T-1 ~ T-3 |
| C1-2c | 超时真正生效；运行 `failed`，`error.code = 'STEP_TIMEOUT'`，信息写明第几步、stepId、agentId、时长；页面显示该信息，「运行」按钮恢复可用 | H-1 ~ H-4 |
| C1-2d | 页面跟踪上限按工作流计算（15 分钟 ~ 3 小时） | Claude 读代码复核（见 4.1 第 5 条） |
| C1-4 | 业务运行进行中刷新页面能接回，跟到结束 | I-1 ~ I-4 |
| C1-5 | 运行暂停（未结束）时重启 DSH → `interrupted` / `HOST_RESTARTED`；页面不接回它、「运行」可用；重新发起能完成 | J1-1、J2-1 ~ J2-3 |

---

## 4. 实现规格

### 4.1 页面 `docs/prototypes/agent-trainer-repair-prototype.html`

（页面每次请求都从磁盘读取，改页面本身不需要重启 DSH；但本轮还改了插件代码，所以仍要按第 5 节重启。）

1. **断开旧流水线入口**：删除 `runTrainer()` 里的这一行：
   `if(state.exec==='business'&&currentWorkflow()?.businessPipeline)return runBusinessPipeline();`
   `runBusinessPipeline` / `refreshBusinessRun` 等函数保留不动（只是不再被调用）。删除后页面源码中不能再出现字符串 `return runBusinessPipeline()`（K-1 检查）。
2. **步骤卡片超时输入框（接口写死，验收程序依赖它）**：
   - 当前工作流的每个步骤卡片上加一个输入框：`<input type="number" data-step-timeout="{步骤序号，从 0 开始}" min="1" max="30" step="1" value="{分钟}">`，前面有标签「超时（分钟）」。
   - 显示值 = `Math.round((step.timeoutMs ?? 120000) / 60000)`（未写超时的旧步骤显示 2，与执行包默认值一致）。
   - 只在训练模式可编辑；发布、工程模式 `disabled`。
   - 触发 `change` 事件时：值必须是 1~30 的整数，否则 toast 显示文字中包含「超时需为 1~30 分钟」，输入框恢复为原值，**不保存**；合法则把该步骤的 `timeoutMs` 设为 `分钟 × 60000`，通过现有的 `persistWorkflow` 保存（生成新 revision），toast 显示中包含「已保存」。
3. **新步骤默认 5 分钟**：`addStep` 新增的步骤写 `timeoutMs: 300000`。已有步骤保持原值不变（不得批量改写现有工作流）。
4. **步骤属性跟着步骤走**：重写 `workflowDefinition(wf)` 的继承方式，使移动、删除步骤时，每个步骤自己的 `stepId`、`timeoutMs`、`outputSchemaRef`、`outputBindings`、`agentVersion` 跟随该步骤移动，不再按位置继承；`inputBindings` 仍按新顺序重新生成（与现在相同）。新增步骤用新的唯一 `stepId`。
5. **页面跟踪上限按工作流计算**：替换 `refreshLiveRun` 中固定的 15 分钟上限：`上限 = clamp(Σ 该运行所属工作流各步 (timeoutMs ?? 120000) + 5 分钟, 最少 15 分钟, 最多 3 小时)`。所属工作流按 `run.targetId` 在页面已加载的工作流中查找；找不到就用 15 分钟。超时提示文字改为「运行 {runId} 超过 {N} 分钟仍未结束，已停止自动刷新；刷新页面可继续跟踪。」
6. **运行错误显示**：在 `#run-id` 旁新增元素 `<div id="run-error"></div>`，内容 = 当前跟踪的运行的 `error.message`（没有则为空）。`refreshLiveRun` 每次刷新都更新它。
7. 页面不得出现 `window.confirm`、`alert(`、`prompt(`；不得修改 B 任务相关的原生会话卡片逻辑。

### 4.2 服务端

1. `lib/trainer-schema.js`：
   - `workflowDefinition` 中步骤 `timeoutMs` 的 `maximum` 由 `480000` 改为 `1800000`；
   - 在 `validateProjectFiles` 校验 `workflows/*.json` 的分支里新增：工作流 JSON 含 `businessPipeline` 字段时报错，错误信息写为 `businessPipeline is archived (legacy TM109 pipeline); remove it`；
   - 同一分支里，对步骤 `timeoutMs` 的手工校验补上上限：不是 1~1800000 的安全整数就报 `invalid timeoutMs`。
   - `businessPipelineDefinition` 定义可以保留（旧代码引用），但新写入一律被上面的检查拒绝。
2. `lib/framework-agent-run.js`：单步超时时（`createTrainingLifecycle` 的 `onCancel` 中 `stopReason === 'timeout'`），把运行和该步骤的错误写为：
   - `code: 'STEP_TIMEOUT'`
   - `message: 第 {序号，从 1 开始} 步 {stepId}（{agentId}）超过 {时长}未完成，已判失败`，其中时长：能被 60000 整除写「{N} 分钟」，否则写「{秒数} 秒」（例如 1000 ms → 「1 秒」，300000 → 「5 分钟」）。
   - 运行最终状态仍为 `failed`（现有逻辑）。
3. 不修改 `lib/trainer-bundle.js` 的默认值（保持 `120000`），不修改 `syntheticBusinessBundle`，不修改 `reconcileInterrupted` 的行为（只在测试中覆盖它）。

### 4.3 测试（新增 `plugins/dsh-ptc-control-plane/test/c1-business-hardening.test.mjs`，并在 `test/all.test.mjs` 末尾 import）

1. `validateProjectFiles`：工作流含 `businessPipeline` → 有错误，信息含 `businessPipeline`；步骤 `timeoutMs` 为 `1800000` 通过，`1800001` 与 `0` 失败。
2. 运行器：用一个永不返回的假适配器、步骤 `timeoutMs: 50`，运行结束为 `failed`，`error.code === 'STEP_TIMEOUT'`，`message` 匹配 `/^第 1 步 \S+（\S+）超过 .+未完成，已判失败$/`；再测 `60000` 的格式化结果为「1 分钟」（可以把格式化函数导出单测）。
3. `reconcileInterrupted`：一个 `paused` 状态、不在内存中的运行，调用后为 `interrupted`、`error.code === 'HOST_RESTARTED'`（若已有等价测试，注明测试名即可）。
4. 测试桩必须模拟真实行为，不能把请求参数原样回传当结果。

---

## 5. 执行步骤

所有命令在仓库根目录执行；默认沙箱报 `EPERM` 时用提升权限环境重跑同一命令。

### 步骤 0：准备
1. `git fetch github --prune`；`HEAD`、`github/master`、`github/main` 三者相同（应为 `77a7655` 或之后）。不一致 → 硬停止条件 1。
2. `git status --porcelain > .tmp-c1-baseline-status.txt`（不提交）。确认 Claude 已放入的文件存在且为未提交改动：`docs/tasks/C1-business-run-hardening.md`（本文件）、`docs/tasks/verify/verify-b-host.mjs`（新增步骤 K/T/H/I/J1/J2）、`docs/tasks/verify/README.md`。
3. 备份将修改的文件为同目录 `.bak-20261003-taskC1`（不提交）：页面、`trainer-schema.js`、`framework-agent-run.js`。

### 步骤 1：实现
按第 4 节修改。完成后：
```
node --check docs/tasks/verify/verify-b-host.mjs
node -e "const s=require('fs').readFileSync('docs/prototypes/agent-trainer-repair-prototype.html','utf8');const m=s.match(/<script>([\s\S]*)<\/script>/);require('fs').writeFileSync('.tmp-c1-page.js',m[1])" && node --check .tmp-c1-page.js
```
**通过标准**：两条 `node --check` 都无输出；`grep -c "return runBusinessPipeline()" docs/prototypes/agent-trainer-repair-prototype.html` 为 0。

### 步骤 2：测试
在 `plugins/dsh-ptc-control-plane` 下：
```
node --test test/c1-business-hardening.test.mjs
node test/all.test.mjs
```
**通过标准**：新测试全部通过；全量 ≥ 410 passed（原 407 + 新增至少 3）、0 failed。

### 步骤 3：部署
确认没有进行中的 framework run（`/api/ptc-control/trainer/runs`）→ `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`。
**通过标准**：Gate A/B/C 全部 exit 0；3080 返回 200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。本轮不改客户端，不需要重建 `lib/client.js`；不运行 `verify-b.mjs compare`。

### 步骤 4：宿主验收（按顺序，一次一步）
```
node docs/tasks/verify/verify-b-host.mjs --steps K
node docs/tasks/verify/verify-b-host.mjs --steps T
node docs/tasks/verify/verify-b-host.mjs --steps H
node docs/tasks/verify/verify-b-host.mjs --steps I
node docs/tasks/verify/verify-b-host.mjs --steps J1
```
然后**立即**按步骤 3 的命令重启 DSH（J1 留下一个暂停的运行，重启前不要停止它；重启脚本若因「有进行中的运行」拒绝执行，按 6.5 处理），重启通过后：
```
node docs/tasks/verify/verify-b-host.mjs --steps J2
node docs/tasks/verify/verify-b-host.mjs --steps A
```
**通过标准**：每条命令输出末行 `FAIL 0`；检查 K-1~K-5、T-1~T-4、H-1~H-5、I-1~I-4、J1-1、J2-1~J2-3、A-1~A-8 全部 PASS（A-7 允许 WARN）。步骤 A 用来确认本轮没有破坏 B 的固定会话。
说明：K、T、H 会临时修改「新工作流 1」并在结束时自动恢复；恢复检查（K-5、T-4、H-5）失败时按 6.6 处理。

### 步骤 5：只读复核
`node docs/tasks/verify/verify-b.mjs` → PASS 10 / FAIL 0。

### 步骤 6：写报告
用 Node 以 UTF-8 在本文件第 10 节填写完成报告（不要用 PowerShell 的 `Add-Content` / `Out-File`），写完确认本文件 `NUL 0`、UTF-8 可解码。

### 步骤 7：提交与推送
1. 只 `git add`：`docs/tasks/C1-business-run-hardening.md`、`docs/tasks/verify/verify-b-host.mjs`、`docs/tasks/verify/README.md`、`docs/prototypes/agent-trainer-repair-prototype.html`、`plugins/dsh-ptc-control-plane/lib/trainer-schema.js`、`plugins/dsh-ptc-control-plane/lib/framework-agent-run.js`、`plugins/dsh-ptc-control-plane/test/c1-business-hardening.test.mjs`、`plugins/dsh-ptc-control-plane/test/all.test.mjs`（以及第 7 节修复流程中实际改动的文件）。不要 add `docs/tasks/verify/results/`、`.bak-*`、`.tmp-*`。
2. 提交信息：`[C1] 业务运行加固：断开旧流水线入口、单步超时可配置、刷新接回与重启中断验证`
3. 推送 `github master` 与 `github main`，不加 `--force`；三个 ref 一致且 `0	0`。

---

## 6. 异常处理

总原则：同一问题最多换 3 种办法；不得修改验收程序的判定条件（只允许选择器、超时、路径等机械性修正，diff 写进报告）；不得手工改写 revision / bindings 等数据文件。

| 编号 | 现象 | 处理 |
|---|---|---|
| 6.1 | 浏览器启动、宿主入口等问题 | 按 `docs/tasks/B5-host-acceptance.md` 6.1、6.2 处理 |
| 6.2 | K-2/K-3 失败（服务端没拒绝） | 核对 4.2 第 1 条是否生效（插件是否重启加载了新代码）；若已保存了带 `businessPipeline` 或超限的工作流，脚本会自动恢复，确认 K-5 PASS |
| 6.3 | T-1 找不到输入框或值不对 | 核对 4.1 第 2 条的属性名 `data-step-timeout`、`min`/`max`、显示值公式；不要改验收程序 |
| 6.4 | H-1/H-2 失败 | 先看证据 `byStep.H` 的 `H.run.error`：若仍是 `training execution exceeded`，说明 4.2 第 2 条未生效或未部署；格式不符就对照 4.2 第 2 条修正 |
| 6.5 | J1 后重启脚本拒绝执行（检测到进行中的运行） | 这是重启脚本的保护。本轮授权：对 J1 记录的那一个运行（`docs/tasks/verify/results/c1-restart-state.json`）**不要取消**，改用重启脚本支持的强制参数（以脚本实际参数为准）；若脚本没有强制参数，停止 DSH 进程后用同一脚本启动。仍无法重启 → 停止并报告 |
| 6.6 | K-5 / T-4 / H-5 恢复失败 | 不要手改 revision 文件。用 `apply-changes` 把 `workflows/custom-workflow-1.json` 改回证据中记录的原内容（`byStep.*` 的 `*.restore`），再确认 `assets` 返回内容与原内容一致 |
| 6.7 | I-2 未接回 | 核对 `resumeActiveLiveRun` 是否还能接回 `executionMode: BUSINESS_ONLY` 的运行、本轮改动是否影响它；属于代码缺陷 → 第 7 节 |
| 6.8 | J2-1 不是 `interrupted` | 看证据 `J2.run`：若为 `completed`，说明重启前运行已结束（J1 后没有立即重启或暂停未生效），重跑 J1 后立即重启；若仍为 `paused`，说明 `reconcileInterrupted` 未执行 → 代码缺陷 |
| 6.9 | 全量测试有失败 | 与基线 407 passed 对比，确认是否本轮引入；本轮引入的按第 7 节修复 |

## 7. 修复流程

定位 → 只改第 4 节涉及的文件 → 补能复现问题的测试 → 全量测试 0 失败 → 重启 Gate 通过 → 重跑失败的步骤，以及其后的所有步骤（J1/J2 成对重跑）。同一缺陷 3 次仍失败 → 硬停止条件 5。

## 8. 数据说明

- K、T、H 临时修改「新工作流 1」（`custom-workflow-1`）后自动恢复，会产生若干新的候选 revision，这是正常的。
- H、I、J1、J2 会产生若干 BUSINESS_ONLY 合成运行（597），J1 的那个运行最终为 `interrupted`，保留。
- 不删除任何会话、bindings、运行记录。

## 9. Claude 复核方式

读本文件第 10 节、`docs/tasks/verify/results/verify-b-host.json`（`byStep.K/T/H/I/J1/J2/A`）、提交 diff（重点核对 4.1 第 4、5 条和 4.2 第 2 条），以及 Git ref 与 `.git/index` 中的提交范围。

---

## 10. 完成报告（Codex 填写）

- 基线：HEAD / github/master / github/main = 77a7655d613a88f88ea225646d38d6fabe7b8bc2；开工状态原样保存于 `.tmp-c1-baseline-status.txt`。
- 改动摘要：页面移除 `runTrainer()` 到旧 `runBusinessPipeline()` 的入口；步骤卡片新增训练模式可编辑、发布/工程模式禁用的 1~30 分钟单步超时输入，步骤属性按步骤移动/删除时保持，运行跟踪上限按所属工作流超时总和计算，并显示运行错误；`trainer-schema.js` 拒绝旧 `businessPipeline`、将 `timeoutMs` 上限扩至 30 分钟；`framework-agent-run.js` 持久化 `STEP_TIMEOUT` 及步骤错误并按超时步骤定位；新增 C1 专项测试并接入全量测试。
- 测试：`c1-business-hardening.test.mjs` 4/4 通过；全量插件测试 411 passed / 0 failed / 0 cancelled / 0 skipped。
- 部署：最终重启产物 `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20261003-133254`；Gate A/B/C = 0；3080 = 200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty` 等致命签名。
- 宿主验收：K：K-1 PASS，K-2 PASS，K-3 PASS，K-4 PASS，K-5 PASS，FAIL 0；T：T-1 PASS，T-2 PASS，T-3 PASS，T-4 PASS，FAIL 0；H：H-1 PASS，H-2 PASS，H-3 PASS，H-4 PASS，H-5 PASS，FAIL 0；I：I-1 PASS，I-2 PASS，I-3 PASS，I-4 PASS，FAIL 0；J1：J1-1 PASS，FAIL 0；J2：J2-1 PASS，J2-2 PASS，J2-3 PASS，FAIL 0；A：A-1 至 A-8 PASS，FAIL 0。
- 关键值：H 超时运行 `framework-a71a2cb3-4d83-454d-b4db-0e0173fd8711`，错误为「第 1 步 step-1（agent-T2）超过 1 秒未完成，已判失败」；I 运行 `framework-844d5efd-3bd5-4073-b3c5-8cac046cfad2`，刷新后重新接回并完成；J1 暂停运行 `framework-95f93f96-8c8c-4c7e-9634-a8cfe7ce8cfa`，重启后为 `interrupted` / `HOST_RESTARTED`；J2 重新发起运行 `framework-f43b9ca3-8046-4aaa-950b-ec7617e42754` 并完成。
- verify-b.mjs：PASS 10 / FAIL 0 / WARN 0 / SKIP 0。
- 偏离：验收程序 `docs/tasks/verify/verify-b-host.mjs` 的 J1 暂停请求原缺少服务端必需的 `requestId`，首次返回 `invalid_identity`；仅作机械性修正，在 `api('control', { mode: MODE, runId, action: 'pause' })` 中加入 `requestId: requestId('J1-pause')`，未改变判定条件。I 首次预检因已有手工诊断运行占用而未完成，该运行结束后已按既有重试规则重跑并通过；无产品缺陷。C1 按任务书不执行客户端重建与 compare。
- 数据：K/T/H 临时工作流修改均自动恢复；未删除会话、bindings 或运行记录；J1 的中断运行保留；旧 TM109 代码保留。
- 提交 / 推送：本报告随本轮 C1 提交；最终 commit hash、github/master、github/main 与 0/0 同步状态以最终 Git ref 核对及交付消息为准。
