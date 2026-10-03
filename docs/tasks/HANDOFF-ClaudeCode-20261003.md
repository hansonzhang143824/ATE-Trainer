# 交接说明：Agent Trainer 系统开发的计划与验收工作（Cowork Claude → Claude Code，2026-10-03）

> 读者：在用户电脑上以 **Local** 模式运行的 Claude Code（工作目录 `D:\Newtest\DSH\ATE-Coding-Flow`）。
> 你接替的是「写计划 / 任务书 + 验收」这一角色。你能直接在本机执行命令，这一点比之前的 Cowork 会话强：测试、重启 DSH、宿主验收、git 都可以自己跑。

---

## 1. 用户目标（原话整理，任何时候不得偏离）

1. **先把系统做完，再做真实业务**：「当前 BUSINESS_ONLY 其实也是先按照假的 597 来跑，因为我要的是建立一套系统，等确认这套系统完全没问题了，我才会停止系统开发，然后专注于搭建一套真正的 ATE 业务线。」
2. **系统是什么**：工作流可以随意调整、Agent 可以随意编辑；工作流不变，Agent 通过**训练会话**持续优化、能力越来越强；之后**冻结版本并发布**。
3. **两种验证**：SMOKE_ONLY（1+2=3）用最轻量的任务验证流程本身；BUSINESS_ONLY 本意是真实业务，但为了排除「业务流搭建不合理、schema 不好、Agent 间合同没约好」这类与系统无关的干扰，**有意**先用合成 597。真实业务时再切回。
4. 用户是测试工程师（STS364 / STS8300 模拟芯片测试），真实业务线是 ATE（第一个试点计划用 DFT 解析）。

## 2. 用户的工作规则（必须遵守）

- 结论必须仔细验证，**对照真实文件**，不能凭汇总下结论。用户原话：「我不接受你简单分析就给一堆方案和计划，导致 codex 连续做了几轮都始终没有完成。」
- 验收结论只有两种：**「通过」** 或 **「不通过 + 问题清单」**。
- 计划要细致、可执行、先验证可行；任务书里**附上目标原文**，防止执行者跑偏。
- 如果仍把实现交给 Codex：指令以 `/goal` 开头，写全文档路径和停止规则，放在代码块里给用户转贴。
- 回答用中文，简洁。

## 3. 环境与常用命令

| 用途 | 命令 / 位置 |
|---|---|
| 插件目录 | `plugins/dsh-ptc-control-plane`（下称 plugin） |
| 全量测试 | 在 plugin 下 `node test/all.test.mjs`（约 4 分钟；受限沙箱会出现 44 个 `spawnSync python EPERM`，需在允许 Python 子进程的环境运行） |
| 客户端构建（改了 `client/*.js` 才需要） | `node plugins/dsh-ptc-control-plane/scripts/build-client.mjs` → `lib/client.js` |
| 重启 DSH（改了 plugin/lib 才需要） | 先确认 `/api/ptc-control/trainer/runs` 无进行中运行，再 `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`；要求 Gate A/B/C 全部 0、3080 返回 200、启动日志无 `plugin tree failed to load` / `ERR_MODULE_NOT_FOUND` / `ERR_PACKAGE_PATH_NOT_EXPORTED` / `input hint must not be empty` |
| 页面 | `docs/prototypes/agent-trainer-repair-prototype.html`，每次请求从磁盘读取，改页面不用重启；访问 `http://127.0.0.1:3080/agent-trainer?nativeHost=<宿主ID>` |
| 接口 | `POST http://127.0.0.1:3080/api/ptc-control/trainer/<operation>`，白名单见 `plugin/lib/trainer-api.js` |
| 只读复核 | `node docs/tasks/verify/verify-b.mjs`（应 PASS 10） |
| 宿主自动验收 | `node docs/tasks/verify/verify-b-host.mjs --steps <X>`，一次一步；步骤见 `docs/tasks/verify/README.md`：A~G（任务 B）、K/T/H/I/J1/J2（C1）、DF/DS/DO/DP（D）。它会开一个独立 Chrome（临时 profile、调试端口 9333） |
| 远端 | `github`，分支 `master` 与 `main` 同步推送，不强推 |

**踩过的坑**
1. PowerShell `Add-Content` / `Out-File` 会往 Markdown 写入 0x00。写文件一律用 node / python 按 UTF-8；交付后检查 NUL = 0。
2. PowerShell 读本机部分文件可能拿到密文（透明加密层），判断文件内容用 node / python。
3. 接口的 `requestId` 不能含点号（`invalid_identity`），不能复用（`request_conflict`）；不要显式传 `purpose:'FRAMEWORK_TRAINING'`（`PURPOSE_INVALID`）。
4. Codex 常见问题：把没做的项标成通过；把自己的宿主验收推给「待用户执行」；漏提交。验收要逐条看证据文件，不看汇总。
5. 硬停止条件见 `docs/tasks/00-PLAN.md` 2.4 节（删会话 / 删 bindings / 手改 revision、冻结、release 文件 / 强推都属于禁止项）。

## 4. 进度（截至 2026-10-03）

| 任务 | 结论 | 提交 | 任务书 |
|---|---|---|---|
| A Agent 删除与 ID 不复用 | 通过 | — | `docs/tasks/A-agent-delete.md` |
| B 专家固定会话（14 条） | 通过 | `77a7655` | `docs/tasks/B-expert-fixed-session.md`、B5、B6 |
| C1 业务运行加固（断开旧 TM109 入口、单步超时 1~30 分钟、刷新接回、重启标记中断） | 通过 | `84e3e93` | `docs/tasks/C1-business-run-hardening.md` |
| D0 冻结与发布盘点 | 数据属实；漏掉了阻断问题（见下） | `ea1ea7c` | `docs/tasks/D0-release-audit.md` |
| D 冻结与发布完整性 | **功能全部通过；1 项未完成（见 4.1）** | `3c23333`…`06807ca` | `docs/tasks/D-release-integrity.md` |

### 4.1 D 的验收结论（Cowork Claude 已复核）：不通过，问题清单 1 项（非功能）

- **问题 1**：`docs/tasks/verify/README.md` 中「任务 D 的附加步骤」一节没有提交。证据：磁盘上 README 为 9587 字节、mtime 1791021044805（含 D 一节），而 `.git/index` 中该文件 mtime 仍为 1791002646（C1 时）。任务书第 5 节步骤 7 要求提交它。
- **修复**：`git add docs/tasks/verify/README.md`，提交信息 `[D] 补交验收程序说明`，推送 master 与 main，确认 0/0。补完即可判「通过」。

已核对并确认无误的部分（不必重做）：
- 三个 ref = `06807ca`；`.git/index` 中本轮变动路径只有任务书列出的 9 个（缺上面的 README），未改已有测试。
- `verify-b-host-{DF,DS,DO,DP,A,K}.json` 全部 PASS（DF 10、DS 7、DO 4、DP 7、A 10、K 7）；verify-b PASS 10；custom-workflow-1 激活指针 = `release-ad91f02f…`（开工值）。
- **直接打开**新冻结 `frozen-c2f9fe08…` 与新发布 `release-6aab1ccf…` 的 `bundle-manifest.json`：4 个 Agent 的 instructions.md 都是真实指令（"You are agent-T2. Solve exactly 11*21…" 等），不再是合成指令；`version.json` 有 createdAt / sequence 3 / validation{SMOKE_ONLY}；`release.json` 有 createdAt / sequence 2 / validationMode SMOKE_ONLY。
- 代码：`framework-agent-run.js` 保存并校验 `source-bundle.json`，readRun 回退规则符合任务书 4.2；`trainer-service.js` freeze 改用 `run.sourceBundle`；冻结与发布序号都在 `trainerLock` 内分配；stage 先查合成再查证据，sha 比较用 `sourceBundleSha256 ?? bundleSha256`；activate 拦截合成版本；工作流引用合成冻结 Agent 被拦截；页面「发布此版本」用 `version.validation.runId` 先 stage 再 activate，失败有 toast。
- Codex 的偏离（已在报告写明，判定可接受）：验收程序 `restoreWorkflow` 改为按原始 path 恢复（工作流改名后按名称找不到）；DP 等待具体发布行。早期失败的 DF 尝试额外留下 frozen #1/#2、release #1（真实内容，保留即可）。

## 5. 关键事实与测试数据

- 测试目标：工作流「新工作流 1」= `custom-workflow-1`（步骤：agent-T2、custom-agent-7、agent-T3、custom-agent-5）；Agent X = `agent-2abe705b`（固定会话 S2 `session-e4ab77e8…`，前一个 S1 `session-ad0b3230…`）；Z = `agent-70e75253`。
- 运行模式：页面 SMOKE / BUSINESS 会把执行包换成 1+2 / 597（`trainer-service.js` 的 `syntheticSmokeBundle` / `syntheticBusinessBundle`）；**训练会话里专家调用 `trainer_run` 时不带 executionMode，执行真实指令**。D 之后，合成运行同时保存真实执行包，冻结 / 发布用的是真实内容。
- 被污染（合成指令）的存量版本：`frozen-cfb09c03…`、`frozen-00f99692…`、`release-53dc2488…`、`release-74077b90…`。已被识别并禁止发布 / 激活，文件保留不动。
- 冻结与发布数据：冻结在 `Training_Materials/framework/projects/agent-trainer/versions/frozen-*/`；发布在 `publish/versions/release-*/`；激活指针在 `publish/active/agent-trainer/<kind>/<id>.json`。
- 训练会话专家工具：context / assets / runs / events / apply_changes / validate / run / control / compare；**没有** freeze / stage / activate（这些只在页面）。
- 脚本工具单次最多 30 秒（`trainer-schema.js`、`framework-dsh-adapter.js`）；单步超时 1~30 分钟。

## 6. 遗留问题（不阻塞，可排期）

1. C1 观察：步骤超时时 `onCancel` 立即把运行置为 failed，子会话终止尚未确认（同目标新运行仍受 `TERMINATION_UNCONFIRMED` 保护）。
2. 页面初始 `#run-id` 显示「尚未运行 · 运行中」（lastRun 默认无 status）。
3. B 遗留：DSH 停机期间删掉的会话，重启后首次打开可能复用旧壳。
4. 删除 Agent 不能撤销；删除 Agent 时不连带移除工作流步骤。
5. D-5 未做：待审核（staged/review）状态、版本说明、版本对比。
6. 旧 TM109 流水线代码与路由仍在（入口已断开），系统稳定后清理。

## 7. 下一步建议（由用户决定顺序）

1. 补交 D 的 README（4.1），D 判通过。
2. 用户原则是「系统完全没问题再做业务」。系统主线（编辑 → 训练会话优化 → 验证 → 冻结 → 发布 → 切回）现在已经打通并验证。可以和用户确认：系统开发是否到此为止，还是先处理第 6 节里的某些项。
3. 转向真实业务（C2，DFT 解析试点）前需要设计：
   - 一个开关：BUSINESS_ONLY 不再替换为 597，而是执行真实指令（`trainer-service.js` 中的判断），何时切换由用户决定；
   - 真实材料（DFT 文件）如何作为运行输入交给 Agent（现在输入只能是调用时传的 JSON）；
   - 脚本工具 30 秒上限是否需要放宽；
   - 先读旧 DFT 材料：`_archive`、`Training_Materials` 中 TM109、9/29 的证据。
4. 冻结真实 Agent 前，先用一次合成验证运行（D 之后的），再冻结，不要用 D 之前的运行。

## 8. 验收方法建议

- 你既能写计划也能执行。若自己实现，**开发与验收分两个会话**：验收会话只读任务书和验收程序，按任务书第 3 节与「复核方式」判定。
- 每个任务书沿用现有格式（参照 `docs/tasks/C1-business-run-hardening.md`、`D-release-integrity.md`）：目标原文与硬停止条件 → 现状（代码位置）→ 要交付的行为表 → 实现规格（接口写死）→ 步骤（含通过标准）→ 异常处理表 → 修复流程 → 数据说明 → 复核方式 → 完成报告模板。
- 验收时至少做：Git ref 三方一致 + `.git/index`（或 `git show --stat`）核对提交范围；逐条读 `docs/tasks/verify/results/*.json`；**打开实际产出的数据文件**（冻结 / 发布 / bindings）确认内容；审 diff 中验收程序覆盖不到的部分。
- 交接文档在 claude.ai Project「ATE-Agent-RunTime」也有副本（`claude/HANDOFF-*`），但 Claude Code 看不到 Project，以仓库里这份为准。
