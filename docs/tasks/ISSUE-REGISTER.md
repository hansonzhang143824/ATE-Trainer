# 问题登记表（Agent Trainer 系统开发）

- 建立：Claude Code，2026-10-03。每轮验收后由验收方更新「状态」与「证据」。
- 状态取值：`待修` / `本轮修正中（任务 X）` / `已修正（任务 X，提交）` / `已验证事实` / `延后` / `需用户决定` / `非缺陷`。
- 「证据」写代码位置、提交或结果文件路径，不写汇总性描述。

## 1. 统计（2026-10-03）

| 类别 | 数量 | 编号 |
|---|---|---|
| 需要修正的问题 | 18 | R01–R12、R15–R19、R21 |
| 其中纳入任务 E | 12（67%） | R01–R10、R12、R21；另 R11 做可行性验证 |
| 非缺陷（设计如此） | 2 | R13、R14 |

## 2. 问题表

| 编号 | 问题 | 发现 / 证据 | 状态 |
|---|---|---|---|
| R01 | 页面只能发起 SMOKE_ONLY / BUSINESS_ONLY，没有真实候选运行入口 | 页面 `runTrainerCore` 只发这两种 `executionMode` | 本轮修正中（任务 E） |
| R02 | 训练会话专家提示词、会话工作区说明、步骤子 Agent 身份说明都写成「合成测试」 | `trainer-preset.js` 约 16 行；`trainer-service.js` 约 269 行；`framework-dsh-adapter.js` 约 156 行 | 本轮修正中（任务 E） |
| R03 | 冻结依据不可证明：`revisionId` 可不传、依赖 `readRun` 兼容回退、合成运行可作冻结依据 | `trainer-service.js` freeze；`trainer-bundle.js` freezeTarget；`framework-agent-run.js` 104~115 行 | 本轮修正中（任务 E） |
| R04 | 以合成运行为验证依据的冻结版本仍可发布（如 `frozen-c2f9fe08…`） | D 的 DF 验收即如此冻结、发布 | 本轮修正中（任务 E） |
| R05 | `AGENTS.md` 把系统锁在合成冒烟范围，后续 Agent 会按它把系统往合成方向推 | 仓库根 `AGENTS.md` | 本轮修正中（任务 E） |
| R06 | `businessGatePassed === false` 被当作发布条件 | `trainer-release.js` `evidenceCheck` | 本轮修正中（任务 E） |
| R07 | DSH 每次重启都把**已结束**运行的 `dispatch.json` 改写为 `host_restart`；9/22 的 3 条已于 2026-10-03 11:15 被改写 | `training-execution.js` `reconcileInterruptedTrainingRuns`；原值在提交 `5468af34` | 本轮修正中（任务 E） |
| R08 | 步骤超时时运行立即标 `failed`，子会话终止尚未确认 | `framework-agent-run.js` `onCancel` timeout 分支 | 本轮修正中（任务 E） |
| R09 | 脚本工具单次最多 30 秒 | `trainer-schema.js` 约 50 行；`framework-dsh-adapter.js` 约 76 行 | 本轮修正中（任务 E） |
| R10 | 透明加密层下，DSH 启动的脚本读取材料文件是明文还是密文，未验证（本机 Git Bash 读部分文件为 `TSZ` 头密文，Python 为明文） | 2026-10-03 本机检查；`docs/CLAUDE.md`（旧项目说明）记载本机有 DLP 透明加密，要求 `.cpp/.h` 一律用 Python 按字节读写 | 本轮修正中（任务 E，探针 EM） |
| R11 | 真实材料（DFT 文件等）如何交给 Agent：运行输入只是 JSON，资源文件只收文本且限定目录，步骤子 Agent 只有登记的脚本工具 | `trainer-schema.js` 7 行 `assetPath`；`framework-dsh-adapter.js` | E 验证「输入带路径 + 脚本读取」可行性；正式方案延后到 C2 |
| R12 | 页面初始运行状态显示「尚未运行 · idle」 | 页面 `lastRun` 初值与 `runStatusText` | 本轮修正中（任务 E） |
| R13 | 删除仍被工作流引用的 Agent | 提交前校验拒绝（`TRAINER_PROJECT_INVALID`），任务 A 规格如此 | 非缺陷 |
| R14 | 删除 Agent 不能撤销 | 任务 A：Agent ID 不复用 | 非缺陷 |
| R15 | 旧 TM109 业务流水线代码与路由仍在（页面入口已在 C1 断开） | 页面 `runBusinessPipeline`；`/api/ptc-control/business/*` | 延后（系统稳定后清理） |
| R16 | 9/23~9/29 的 DFT 业务模式改动一直未提交（`scripts/training_*.py`、`skills/agents/dft-parse-agent.md`、`team/expert-profiles/ptc-dft-expert/*`，以及未跟踪的 `training_dft_review_input.py`、`write_dft_semantic_review.py` 等） | `git status` | 需用户决定（建议原样归档提交，不启用） |
| R17 | D-5：待审核（staged / review）状态、版本说明、版本对比 | D 任务书 1 节第 4 条 | 延后 |
| R18 | DSH 停机期间删除的会话，重启后首次打开可能复用旧壳 | 任务 B 遗留 | 延后（需另行调查） |
| R19 | 仓库卫生：约 65 个未跟踪条目；约 100 个已跟踪的 `.pyc` 与旧业务日志；`.tmp-dsh-home-validation` 内有指向 DSH 安装目录的目录联接 | 2026-10-03 盘点，`docs/tasks/cleanup-step3-candidates-20261003.md` | 需用户决定（用户 2026-10-03 决定暂不处理） |
| R20 | （已处理）Git 中两份文档被 NUL 损坏 | `WORKBOARD.md`、`agent-trainer-business-evidence-20260929.md` | 已修正（`ece9a47`） |
| R21 | D 的宿主验收主流程用接口代替页面，漏掉「页面跑不了真实运行」 | `verify-b-host.mjs` `startApiRun` | 本轮修正中（任务 E：主流程验收必须在页面点按钮） |

## 3. 2026-10-03 已完成的维护（不计入上表）

| 内容 | 提交 |
|---|---|
| 补交 D 的验收程序说明，D 判「通过」 | `7333917` |
| 修复两份 NUL 损坏文档（R20） | `ece9a47` |
| 补交 `verify-a.mjs`、`verify-b.mjs` 与两份交接说明 | `a2270b8` |
| 新增 `.gitignore`，验证数据移出 Git（本机保留） | `09e4686` |
| 提交运行必需数据作为备份；两个数据目录按原始字节保存（`-text`） | `ba9c71c` |
| 删除验收截图与临时文件（本机，82 项） | 不涉及 Git，记录见 `docs/tasks/cleanup-step3-candidates-20261003.md` |
