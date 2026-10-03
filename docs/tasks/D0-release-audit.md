# 任务 D0：冻结与发布现状盘点（只读盘点 + 真实宿主实测，不修改代码）

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录）
- 编写：Claude（2026-10-03）。执行：Codex（`/goal`）。评估：Claude
- 本文件是本轮唯一执行依据。执行中忘了要做什么，回到第 1 节。

---

## 1. 目标（用户原话整理，不得偏离）

1. 系统总目标：搭一套系统——**工作流可以随意调整、Agent 可以随意编辑；工作流不变，Agent 通过训练会话持续优化、能力越来越强；之后可以固定版本（冻结）并发布**。SMOKE_ONLY（1+2=3）用最轻量的任务验证流程本身；BUSINESS_ONLY 当前有意使用合成 597 业务流，排除真实业务搭建问题的干扰。系统确认完全没问题后，才转向真实 ATE 业务。
2. 用户说明：**冻结和发布之前已经由 Codex 完成**。Claude 不掌握具体完成情况。
3. 本轮目的：**把冻结与发布的真实现状整理清楚，并在真实宿主中实测一遍完整链路**，给 Claude 评估「还缺什么、下一轮（D）做什么」提供证据。
4. **本轮不修改任何产品代码**（`plugins/`、`docs/prototypes/` 一律不改）。发现缺陷只记录，不修复。

**硬停止条件**（`docs/tasks/00-PLAN.md` 2.4 节，原文）：

> 1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
> 2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
> 3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
> 4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
> 5. 同一个问题尝试 3 种不同的解决办法后仍失败。

补充：本轮**只允许通过系统自身的接口或页面**创建冻结版本、发布版本、切换激活版本（这是正常使用，不属于停止条件 4）；**不得手工创建、修改、删除** `publish/`、冻结版本目录、revision 目录下的任何文件。

---

## 2. 已知背景（供核对，不保证完整）

- Claude 的 Project 文档记录：`stageRelease()` 直接写 `publish/versions/release-*.json`；`listReleases()` 只返回 `releases` 与 `active`；没有可查询的「待审核（staged/current-review）」指针；冻结版本没有明确的冻结时间/序号字段，不得按 UUID 目录名或文件修改时间排序。以上是 10 月 1~2 日的记录，**以当前代码为准**，与代码不符的写明。
- 相关代码（至少）：`plugins/dsh-ptc-control-plane/lib/trainer-release.js`、`trainer-bundle.js`、`trainer-service.js`（`run` 中 `loadReleaseBundle`、`listReleases`、published/engineering 分支）、`trainer-routes*` / `trainer-tools.js`（对外 operation）、页面 `docs/prototypes/agent-trainer-repair-prototype.html`（发布、工程模式相关按钮）。
- 运行时：BUSINESS_ONLY 会把执行包替换为 597 合成题、SMOKE_ONLY 替换为 1+2=3（`trainer-service.js` 的 `syntheticBusinessBundle` / `syntheticSmokeBundle`），**published 模式同样如此**；不带 executionMode（FRAMEWORK_TRAINING，训练会话 `trainer_run`）执行真实指令。

---

## 3. 要交付的内容

在本文件第 8 节写盘点报告，必须包含以下 6 部分，每条结论都要有证据（文件:行号、接口请求与返回片段、运行 ID、磁盘路径）。

### 3.1 代码盘点
1. 冻结与发布相关的全部对外 operation / 接口：名称、参数、返回、调用方（页面按钮 / 训练会话工具 / 仅接口）。
2. 数据落盘结构：冻结版本、发布版本（release）、激活指针各自的目录、文件名规则、字段（贴一个真实样例，去掉无关大字段）。
3. 状态模型：一个版本从「候选 revision」到「冻结」到「发布/激活」到「被替换/回滚」的完整流转；每一步谁能触发、有什么校验（例如 `verifyBundle`、ID 台账、schema 校验）。
4. 三种模式（training / published / engineering）分别读哪个版本、怎么解析（`resolveTarget`、`context`、`run`）。
5. 冻结版本的排序依据（代码里实际用什么排序）；是否存在「待审核」概念。
6. 相关测试文件与覆盖点清单（测试名）。

### 3.2 现有数据盘点（只读）
1. 当前项目里已有的冻结版本、发布版本数量；每个的 ID、对应目标（agent / workflow 与 ID）、创建时间来源、是否激活。
2. 这些数据是否都能被当前代码正常读取（用接口读取，不手工解析为准）。

### 3.3 真实宿主实测（端到端，必须在 `http://127.0.0.1:3080` 真实执行）
使用**测试目标**，不得使用或改动用户的业务 Agent：优先用 `custom-workflow-1`（「新工作流 1」）及其步骤中的测试 Agent；若需要单个 Agent，用 X=`agent-2abe705b`。按顺序执行并记录每一步的请求/返回或页面截图：

| 编号 | 动作 | 记录 |
|---|---|---|
| R-1 | 训练模式：对测试目标保存一次候选修改（如改一行说明文字），得到新 revision | revisionId |
| R-2 | 冻结该 revision（用系统提供的方式：页面按钮或接口，写明用的哪个） | frozenVersionId、落盘路径 |
| R-3 | 生成发布版本（stage release） | releaseId、落盘路径 |
| R-4 | 激活该发布版本（若系统中「生成」与「激活」是同一步，写明） | active 指针前后对比 |
| R-5 | published 模式运行该目标：SMOKE_ONLY 与 BUSINESS_ONLY 各一次 | runId、终态、`releaseId` 字段、加载的版本是否正确 |
| R-6 | engineering 模式查看/运行（按系统实际支持的能力） | 返回与预期 |
| R-7 | 再做一次 R-1~R-4，得到第二个发布版本；确认 active 切换到新版本 | 两个 releaseId 与时间 |
| R-8 | 切回（回滚到）第一个发布版本（若系统支持；不支持则写「不支持」及代码证据） | active 指针 |
| R-9 | 页面在发布模式、工程模式下的显示：版本列表顺序、当前激活版本的标识、能否区分新旧版本 | 截图路径 |
| R-10 | 训练会话（原生会话）中，专家工具是否能看到/操作冻结与发布（`trainer_context` 等返回中与发布相关的字段） | 返回片段 |

R-5 结束后，把测试目标的候选修改恢复（用 `apply-changes` 改回原内容）。实测产生的冻结版本、发布版本**保留，不删除**。最后若激活指针与开工前不同，且系统支持切回，切回开工前的激活版本，并写明。

### 3.4 回归
- 插件全量测试（`plugins/dsh-ptc-control-plane` 下 `node test/all.test.mjs`）：记录 passed / failed（基线 411 / 0）。
- `node docs/tasks/verify/verify-b.mjs`：记录结果。
- 本轮不改代码，**不需要重启 DSH**。

### 3.5 差距清单
对照第 1 节系统目标中「固定版本并发布」这一环，列出：
- 已经可用、且本轮实测通过的能力；
- 存在但有问题的能力（现象、复现步骤、证据）；
- 缺失的能力（例如：待审核指针、冻结排序、回滚、发布前检查、版本说明/备注、版本对比，以实际为准）。
每条注明严重程度：阻断（主线走不通）/ 重要 / 可延后。

### 3.6 不确定项
代码与运行结果不一致、或无法判断的地方单独列出，不要猜。

---

## 4. 执行步骤

1. `git fetch github --prune`；`HEAD`、`github/master`、`github/main` 三者一致（应为 `84e3e93` 或之后）。不一致 → 停止条件 1。记录 `git status --porcelain` 到 `.tmp-d0-baseline-status.txt`（不提交）。
2. 完成 3.1、3.2（只读）。
3. 确认没有进行中的 framework run（`/api/ptc-control/trainer/runs`），执行 3.3。
4. 执行 3.4。
5. 写第 8 节报告（用 Node 按 UTF-8 写入，不用 PowerShell 的 `Add-Content`/`Out-File`；写完确认 NUL 0、UTF-8 可解码）。
6. 提交：**只** `git add docs/tasks/D0-release-audit.md`；提交信息 `[D0] 冻结与发布现状盘点`；推送 `github master` 与 `github main`（不加 `--force`），三个 ref 一致且 `0	0`。
7. 确认 `git status --porcelain` 中除本轮之前已有的条目外，没有新增对 `plugins/`、`docs/prototypes/` 的修改。

## 5. 异常处理

| 现象 | 处理 |
|---|---|
| 某一步系统不支持（例如没有回滚） | 记为「不支持」并附代码证据，继续后面的步骤，不要自己实现 |
| 某一步报错 | 记录完整请求/返回，按系统提示的正确用法最多再试 2 种方式；仍失败记为「存在但有问题」，继续 |
| 需要改代码才能继续 | 不改；记录到差距清单，跳过该步 |
| 实测弄乱了测试目标的候选内容 | 用 `apply-changes` 恢复，不要手工改 revision 文件 |
| 全量测试或 verify-b 失败 | 本轮未改代码，属于环境或既有问题，记录现象与输出，不修复 |

## 6. 不在本轮范围

修复任何缺陷、实现待审核指针或冻结排序、真实业务（DFT）相关内容、删除任何数据。

## 7. Claude 评估方式

读第 8 节报告与证据，抽查落盘文件与 Git ref，然后给出 D 的范围、任务书和时间估算。

---

## 8. 盘点报告（Codex 填写）

- 基线：执行 `git fetch github --prune` 成功；HEAD / github/master / github/main = `84e3e932ea51839f7928be165462180fe3b91365`（含 C1）；开工 `git status --porcelain` 原样保存至 `.tmp-d0-baseline-status.txt`（123173 字符）。本轮未修改或提交基线中既有条目。

### 3.1 代码盘点

- 对外入口统一为 `POST /api/ptc-control/trainer/<operation>`（`trainer-api.js:17-27`）。白名单完整列在 `trainer-api.js:27`：`context`, `assets`, `apply-changes`, `validate`, `run`, `runs`, `events`, `control`, `compare`, `changes`, `freeze`, `stage-release`, `activate-release`, `releases`, `bind-session`, `open-native-session`, `session-workspace`, `session-tool`, `target-session`, `forget-target-session`。冻结、stage、activate、原生会话和 target-session 均是页面专用操作（`trainer-service.js:7-9,196`）；普通 Trainer 会话只得到 `trainer-tools.js:2-6` 的 context/assets/runs/events/apply-changes/validate/run/control/compare，`trainer-service.js:551-560` 明确拒绝 freeze/stage/activate。
- 冻结调用需要候选目标、`runId`；服务端只接受 exact target 的 completed validation（`trainer-service.js:519-536`），返回 `frozenVersionId,bundleSha256,revisionId,targetKind,targetId,workflowRevision,agentBindings`。页面冻结按钮位于 `agent-trainer-repair-prototype.html:54,361-364`。
- 发布调用 `stage-release` 需要 `frozenVersionId` 与已拥有的验证证据，返回 release metadata；`activate-release` 需要 `projectId,releaseId`，返回并写入 active pointer；代码见 `trainer-service.js:538-540`、`trainer-release.js:32-61`。页面发布按钮顺序为 stage 后 activate（`agent-trainer-repair-prototype.html:367-368`）。
- 落盘结构：冻结在 `Training_Materials/framework/projects/<projectId>/versions/frozen-<uuid>/{bundle-manifest.json,version.json}`（`trainer-bundle.js:199-209`）；发布在 `publish/versions/release-<uuid>/{bundle-manifest.json,verification.json,release.json}`，`release.json` 最后写入（`trainer-release.js:32-52`）；激活指针在 `publish/active/<projectId>/<targetKind>/<targetId>.json`（`trainer-release.js:54-60`）。真实样例：`frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312` 对应 revision `revision-7f5aaee3-ddd5-4f2d-8296-f03d53d9ebb1`、bundle SHA256 `5a4471840cb463ac6deab2cbd21b038cd30cdf8805ea0f30a3cc760436060da1`；`release-53dc2488-a38b-40e8-887b-fc646ea1730e` 绑定该 frozen、verifiedRun `framework-8a51d10e-199e-4c5e-b76b-bccf5559ed3d`、`businessGatePassed:false`；其 active pointer 同 release/bundle SHA。
- 状态流转为 candidate revision → completed exact-target validation → frozen bundle（`freezeTarget` 校验 bundle identity、完整性与 bindings，`trainer-bundle.js:211-224`）→ stage release（`evidenceCheck` 校验 completed/validation/businessGate/每个 step，`trainer-release.js:7-17,32-52`）→ activate pointer → published/engineering 读取 release。后续候选修改不改已冻结/发布 bytes；切回旧版本通过再次调用 `activate-release`，本轮 R-8 验证成功。
- 模式解析：`resolveTarget` 在 training/published（非 engineering）读 candidate revision，在 engineering 只从 active release 读 direct target 或 workflow 中的 Agent（`trainer-service.js:136-156`）；context 枚举 frozen/release 与能力（`trainer-service.js:423-448`）；run 在 published/engineering 加载 release bundle，在 SMOKE/BUSINESS 下替换合成 bundle（`trainer-service.js:487-497`）。
- 冻结排序实际是 `fs.readdirSync(...).filter(...).sort()` 的 frozen UUID 字符串顺序（`trainer-bundle.js:227-241`）；发布列表同样按 release UUID 字符串排序（`trainer-release.js:73-85`）。没有 createdAt/序号，也没有 staged/current-review 指针；`stageRelease` 直接完成 release marker。
- 相关覆盖：`framework-release.test.mjs`（exact bytes、验证证据、发布完整性）、`release-publisher.test.mjs`（失败证据、并发、rollback）、`framework-published-run.test.mjs`（固定 release replay）、`training-release.test.mjs`（SMOKE 发布/旧 release pinning/发布运行）、`agent-trainer-d5-d6.test.mjs:71`（冻结并由 engineering 读取）、`agent-trainer-session-tool.test.mjs:13`（会话工具白名单）、`target-session.test.mjs:14` 与 `trainer-native-launch.test.mjs:287`（固定会话/新开会话）。

### 3.2 现有数据盘点

- 开工接口读取（`context` 与 `releases` 均 HTTP 200，证据保存在 `.tmp-d0-release-audit-evidence.json`）得到 11 个 frozen、7 个 release、3 个 active pointer；所有记录均能由当前代码 `loadFrozenBundle/readRelease/loadReleaseBundle` 校验读取。当前最终接口读取为 13 个 frozen、9 个 release、3 个 active pointer。
- 开工 frozen（创建时间：当前 schema 无时间字段；不能从 UUID 或 mtime 推断）如下：
  - `frozen-126ded85-3e9c-4dad-989e-8845c70ae827` → workflow/custom-workflow-1 / `revision-d482f922-beac-4893-99e7-b37fffea7e02`
  - `frozen-2a4223e1-c65c-4670-a2e0-b848b3b51d6d` → workflow/workflow-T1 / `revision-f54820f5-9e63-4d63-8810-207a5842eead`
  - `frozen-2b72695b-d19c-417c-b485-b3f4a7a3fc7d` → workflow/custom-workflow-1 / `revision-8c543ff6-116a-4e83-9b2f-1805a8fea0ca`
  - `frozen-50741742-82e3-4a79-bb0a-149129b3eb7d` → workflow/workflow-T5 / `revision-51d96e23-8933-4d12-a428-b2a3cb6bf850`
  - `frozen-632c9f82-f522-4bc7-b5a8-d1b684a752e3`, `frozen-7ac96b58-1e92-443f-85c9-3d07674e0c05`, `frozen-ffe81780-bd56-462a-8760-a04b9827ecf4` → workflow/workflow-T1 / `revision-e29dcfcb-6541-4892-8657-8fb4122ff07a`
  - `frozen-85e70b63-d20a-4570-bbe5-68c90deea6f3` → workflow/workflow-T5 / `revision-b1562c9c-9813-47fd-9664-57c8ffaeef5a`
  - `frozen-9319cc9c-ad9f-46e0-b97b-497bb41dfa66` → workflow/custom-workflow-1 / `revision-06421406-94f5-4253-af76-5fa611d340c7`
  - `frozen-bed69174-cca1-4a0c-8ef0-838494a91487` → workflow/workflow-T1 / `revision-766d9e15-e653-45fa-a15f-71d5c53a02ad`
  - `frozen-ea6313ce-57c6-40ea-9b38-15a21e7ae99f` → workflow/workflow-T1 / `revision-a966831b-2c78-4f18-a32c-e43a219de84b`
  - 开工 active：custom-workflow-1 → `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58`；workflow-T1 → `release-ba5188a5-15fa-4872-8ec1-93203ffdb779`；workflow-T5 → `release-80b3d739-627b-4b27-b643-828d2066e7ea`。其余开工 release 不激活。
- 开工 7 个 release（均创建时间不可由当前 schema 得到，均 `businessGatePassed:false`）：
  - `release-2115e901-9b91-4c56-bff0-444b8c1b3fb8` → workflow-T5 / frozen-50741742 / revision-51d96e23
  - `release-80b3d739-627b-4b27-b643-828d2066e7ea` → workflow-T5 / frozen-85e70b63 / revision-b1562c9c
  - `release-869229d1-d18e-4a58-bac0-99a7ea18cbb8` → custom-workflow-1 / frozen-126ded85 / revision-d482f922
  - `release-9403c386-05d9-49bb-a562-2a920efb28cc` → workflow-T1 / frozen-2a4223e1 / revision-f54820f5
  - `release-95a32837-bd2e-4929-9364-4d9c2165091d` → workflow-T1 / frozen-bed69174 / revision-766d9e15
  - `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58` → custom-workflow-1 / frozen-9319cc9c / revision-06421406
  - `release-ba5188a5-15fa-4872-8ec1-93203ffdb779` → workflow-T1 / frozen-ea6313ce / revision-a966831b
- 本轮新增且保留：
  - `frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312` → custom-workflow-1 / `revision-7f5aaee3-ddd5-4f2d-8296-f03d53d9ebb1`；
  - `frozen-00f99692-c936-453e-91e5-c0e2c6acb423` → custom-workflow-1 / `revision-7a584fe8-a29c-4886-b206-ed01bed17481`；
  - `release-53dc2488-a38b-40e8-887b-fc646ea1730e` → frozen-cfb09c03；
  - `release-74077b90-d598-4431-a444-b04ff932147c` → frozen-00f99692；两者均为 inactive，因最终已恢复开工 active。

### 3.3 真实宿主实测（http://127.0.0.1:3080）

测试目标始终为 `agent-trainer/custom-workflow-1`，未使用业务 Agent；所有冻结、发布、激活、候选恢复均通过系统 API，未手工改写受保护文件。

- **R-1**：training context 初始 candidate revision 为 `revision-fffc63f5-a40d-4cf0-9687-f520a980538c`（失败尝试恢复后的等价候选）；���过 `apply-changes` 仅修改 `workflows/custom-workflow-1.json` 的 name 为“新工作流 1 · D0-R1”，得到 `revision-7f5aaee3-ddd5-4f2d-8296-f03d53d9ebb1`，HTTP 200。
- **R-2**：POST `freeze`（依赖 validation）使用验证运行 `framework-8a51d10e-199e-4c5e-b76b-bccf5559ed3d`，返回 `frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312`，路径 `Training_Materials/framework/projects/agent-trainer/versions/frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312`，HTTP 200。
- **R-3**：POST `stage-release` 返回 `release-53dc2488-a38b-40e8-887b-fc646ea1730e`，路径 `publish/versions/release-53dc2488-a38b-40e8-887b-fc646ea1730e`，HTTP 200。
- **R-4**：POST `activate-release` 后 custom-workflow-1 active 从 `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58` 切到 `release-53dc2488-a38b-40e8-887b-fc646ea1730e`（pointer bundle SHA `189a8960…` → `5a447184…`），HTTP 200。
- **R-5**：published SMOKE_ONLY 运行 `framework-fd8bfd8e-355f-4751-9cdc-f8c4313f8236` completed，`releaseId=release-53dc2488-a38b-40e8-887b-fc646ea1730e`，output `{answer:3}`；published BUSINESS_ONLY 运行 `framework-aab12e10-6780-428d-b42a-91a8bc36c3ea` completed，同 releaseId，output `{answer:597}`；均 `error:null`、`businessGatePassed:false`。
- **R-6**：engineering context HTTP 200，仅返回 active 发布绑定；engineering run `framework-9144d667-cf7b-4912-ae0c-556ac8765650` completed，`releaseId=release-53dc2488-a38b-40e8-887b-fc646ea1730e`，output `{answer:3}`，`error:null`。页面随后显示“工程模式 · 已发布 3 个工作流 / 4 个 Agent”。
- **R-7**：先用 `apply-changes` 恢复 R-1 name，再改为“新工作流 1 · D0-R7”，得到 `revision-7a584fe8-a29c-4886-b206-ed01bed17481`；validation `framework-49958265-0483-49fc-ac97-46fac00623ea`；freeze 得到 `frozen-00f99692-c936-453e-91e5-c0e2c6acb423`，stage 得到 `release-74077b90-d598-4431-a444-b04ff932147c`；activate 后 active 切到该第二 release，HTTP 均 200。
- **R-8**：系统没有单独 rollback operation；按代码证据（`activateRelease` 可再次写 pointer，`trainer-release.js:54-61`）用 `activate-release` 指回第一个 release，active 恢复 `release-53dc2488-a38b-40e8-887b-fc646ea1730e`；最后再次 activate 开工 release `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58`，其他两个 active pointer 也与开工一致。
- **R-9**：使用 computer-use 的 in-app browser CUA tab 28，URL `http://127.0.0.1:3080/agent-trainer`。发布审核截图/DOM 显示“发布审核 · 候选只读”、13 Agents、6 workflows、编辑控件 disabled；工程截图/DOM 在异步数据加载后显示“工程模式 · 已发布 3 个工作流 / 4 个 Agent”、3 个 workflows（新工作流 1、workflow-T1、workflow-T5）、4 个 Agents，选中 workflow 显示 release-ad91… 且只读。截图已在任务 UI 中 inline 捕获；CUA API 未返回可写入磁盘的路径，故此处记录 tab/URL/DOM，不虚构截图路径。
- **R-10**：POST `open-native-session` training workflow/custom-workflow-1 复用 `session-f9ecedff-217a-4231-a048-d48e6c225134`（HTTP 200、`reused:true`）；随后 `session-tool` context HTTP 200。binding 的 effectiveTools 为 `trainer_apply_changes,trainer_assets,trainer_compare,trainer_context,trainer_control,trainer_events,trainer_run,trainer_runs,trainer_validate`，无 freeze/stage/activate；context 返回 `frozenVersions` 与 `capabilities:{edit:true,freeze:false}`。
- R-5 后已通过 `apply-changes` 恢复候选原始 bytes，最终 `candidateRestoredExactly:true`，revision `revision-297a4c23-e14d-4e3d-afb9-19a4bf5bdca0`；保留本轮 2 个 frozen 与 2 个 release；最终无 active framework run。

### 3.4 回归

- `node test/all.test.mjs`（在允许 Python 子进程的环境重跑）：**411 passed / 0 failed / 0 cancelled / 0 skipped**，退出码 0，耗时约 234 秒。受限沙箱的第一次尝试为 367/44，44 项统一为 `spawnSync python EPERM`；未作为最终结果。
- `node docs/tasks/verify/verify-b.mjs`：**PASS 10 / FAIL 0 / WARN 0 / SKIP 0**，退出码 0；结果写入 `docs/tasks/verify/results/verify-b.json`。
- 本轮未改产品代码、未重启 DSH；最终查询 `/api/ptc-control/trainer/runs` active 为空。

### 3.5 差距清单

**已可用（本轮通过，无阻断）**

- 训练候选可通过 apply-changes 形成新 revision；必须先完成 exact-target validation 才能 freeze；冻结 bundle、bindings、SHA256 可由接口读取并经完整性校验（证据：R-1/R-2、`trainer-service.js:519-536`、`trainer-bundle.js:211-224`）。
- stage release 与 activate 分离，active pointer 可查询；published SMOKE_ONLY 与 BUSINESS_ONLY 都从指定 release replay，并写入对应 releaseId；engineering 只显示/运行 active release（R-3~R-6）。
- 旧 release 可通过再次 activate 回滚，候选恢复后原始 bytes 与开工一致；无会话/bindings 删除（R-8、最终 `candidateRestoredExactly:true`）。
- release 目录与验证证据有 exact-byte digest、target/bundle/step identity 校验，插件回归覆盖完整（411/0）。

**存在但有问题（重要）**

- frozen/release 没有创建时间、序号或备注字段，列表按 UUID 字符串排序，不能可靠回答“最新/上一版本”（`trainer-bundle.js:233`、`trainer-release.js:75`；3.2 真实记录）。
- 发布页没有版本列表、当前 active 标识或新旧对比；只能看到候选只读与发布按钮，版本实际列表只能通过 `releases` API 取得（R-9、`agent-trainer-repair-prototype.html:84`）。
- 没有独立 rollback API、回滚原因/审计事件；当前可用 activate-release 重新指向旧 release（R-8、`trainer-release.js:54-61`）。

**缺失（可延后，主线不阻断）**

- staged/current-review 指针与发布前 review 状态缺失：stage 直接写完整 release marker，没有中间状态（`trainer-release.js:47-52`）。
- 版本说明、差异/比较视图、发布历史与操作人信息缺失。工程页只呈现 active 绑定，训练会话工具也没有 freeze/release 操作（R-9/R-10、`trainer-tools.js:2-6`）。

### 3.6 不确定项

- 当前 metadata 没有 createdAt；本报告没有使用 UUID 或文件 mtime 推断创建顺序，因此“每个版本的创建时间”无法判定。
- CUA screenshot 返回 inline image bytes 但没有本地路径；报告使用 tab 28、URL 和 DOM 摘要作为证据，未伪造截图文件。
- 开工前已有 target-session binding 的旧 resolved revision 为 `revision-94c5bf70-6b0c-4c4d-8d74-c0e54c477ee6`；R-10 复用时产生 binding-only pendingContextChange 到最终 `revision-297a4c23-e14d-4e3d-afb9-19a4bf5bdca0`，没有删除会话或 bindings。
- 实测脚本早期两次请求分别因 requestId 含点号（`invalid_identity`）、复用 requestId（`request_conflict`）和显式 `purpose:FRAMEWORK_TRAINING`（`PURPOSE_INVALID`）失败；均通过系统 API 恢复候选后才进行成功链路，未产生额外 frozen/release。成功链路的全部请求/返回、最终恢复证据在 `.tmp-d0-release-audit-evidence.json`。
- 工程模式切换后首个 DOM 快照处于异步加载中的 0 项，约 1200 ms 后稳定为 3 workflows/4 Agents；R-6/R-9 采用稳定快照。

- 数据变化：新增冻结版本 `frozen-cfb09c03-ecc0-4469-a00b-abdde09aa312`, `frozen-00f99692-c936-453e-91e5-c0e2c6acb423`；新增发布版本 `release-53dc2488-a38b-40e8-887b-fc646ea1730e`, `release-74077b90-d598-4431-a444-b04ff932147c`；激活指针 custom-workflow-1 开工 `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58` → 中途切换两次 → 结束恢复同一 `release-ad91f02f-27cc-4e5f-b7e3-9f1ea8408a58`，workflow-T1/T5 始终不变。
- 提交 / 推送：待本轮报告提交后填写。
