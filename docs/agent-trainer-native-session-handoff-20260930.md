# Agent Trainer 原生会话续验交接文档

日期：2026-09-30  
用途：交给新的 Codex 会话继续执行同一个 Goal。本文不是完成声明；只要下列门槛还有一项未验证，Goal 必须保持 active。

## 1. 必须继承的 Goal

继续完成原生 DSH 会话替代桥接的开发与全部验收：保留现有 Git 回滚点，逐项核对已提交计划，修复原生跳转、绑定和恢复缺口，通过实际点击和原生输入验证 Agent、工作流、smoke/发布隔离并保存可追溯证据；未验证项不得宣告完成。

新会话必须使用 Goal 模式持续推进，不能把本交接文档、已有部分证据或一次成功的 Agent 会话当成整体完成。只有开发计划和验收计划的所有门槛都逐项通过、证据写盘并复核后，才可以结束 Goal。

## 2. 新会话启动顺序

先阅读并遵守仓库根目录 `AGENTS.md`，然后按顺序阅读：

1. `docs/agent-trainer-native-session-development-plan-20260930.md`
2. `docs/agent-trainer-native-session-validation-plan-20260930.md`
3. `docs/agent-trainer-native-session-validation-report-20260930.md`
4. `docs/agent-trainer-native-session-evidence-20260930.json`
5. 本交接文档

所有验收继续使用真实 DSH 界面操作：点击实际按钮、在 DSH 原生输入框发送消息、观察原生工具事件和终态。服务端/API/文件读取只能用于对照证据，不能替代点击和原生输入。每次补测都追加新的时间戳 evidence，不覆盖旧证据。

## 3. Git 和工作树

- 回滚基线：`dea25de chore: checkpoint before native session replacement`。
- 本轮原生实现的最近聚焦提交：`5ed59fc fix: expose direct ATE Trainer native entry`。
- 本交接文档及其前后的计划、报告、evidence 应在新会话开始前由当前会话单独提交；新会话先确认 `git log` 和 `git status`，只提交本任务相关路径，绝不能 `git add .`。
- 工作树有大量历史运行产物、临时文件和其他未跟踪内容；不要清理、覆盖或纳入本任务提交。
- 当前仓库存在失效的远程 ref，提交时可能出现 geometric repack/bad object 警告；只要目标提交成功，记录警告并继续，不要因此重写或删除工作树。

## 4. 已实现和已有实证

实现已包括：DSH 宿主直接显示“打开 ATE Trainer”，不再需要先点 PTC 面板；Trainer 请求由宿主创建真实 workspace/session；native session 复用前重新校验服务端绑定、target、revision、preset；宿主打开后回读并确认当前 native selection；绑定文件和运行产物留在既定 Training/Publish 边界内。

已完成的真实点击证据：

- DSH 宿主实际显示“打开 ATE Trainer”，链接带 `nativeHost` 直接进入 `/agent-trainer`。
- 点击 `agent-T1` 和“打开当前专家原生会话”，宿主创建 `session-ca6a57d2-5ee0-4ec8-a446-0580132c067f`，标题为 `ATE Trainer · agent:agent-T1`。
- 在真实原生输入框发送 `trainer_context` 指令，实际产生 `trainer_context` 工具调用并返回 agent-T1；随后发送固定 smoke 输入 `1+2等于几，把答案写在JSON里`，原生返回 JSON `answer: 3`。
- 点击工作流“新工作流 1”→“在 Trainer 中训练当前工作流”，宿主创建 `session-7bda7999-35ca-49a5-b214-16ad2598b609`；原生输入触发 `trainer_context`、`trainer_runs`、`trainer_validate`、`trainer_run`、`trainer_events`，真实 run `framework-9b806116-73cf-496a-a8e8-183bb6dff7e0` 完成，四个步骤均 completed，最终 `SMOKE_ONLY` 且 `businessGatePassed:false`。
- 当前 evidence：`docs/agent-trainer-native-session-evidence-20260930.json`，对应 SHA-256 sidecar 为 `8aa77931a920dab65c3e915bc5b02c6b064b9f86cb57143932414eb5e1210352`（新会话开始时重新核对文件和 sidecar）。
- 定向测试在 Windows `--test-isolation=none` 下为 15/15；`npm run build:client` 通过；普通隔离模式受当前 `spawn EPERM` 限制，不能声称通过。

## 5. 已发现但尚未闭环的模型问题

绑定文件配置的是 `deepseek-official/deepseek-v4-flash`，但原生宿主初始实际 ledger 曾是 `zai-coding-cn/glm-5.3-flash`。在 DSH 原生模型选择器中实际点击 `DeepSeek-V4-Flash` 后，再发消息并核对 ledger，实际变为 `deepseek-official/deepseek-v4-flash`，响应约 1 秒、首 token 约 1.4 秒。这个事实证明手动原生选择有效，但没有证明入口默认会自动切到 DeepSeek；不能只看绑定文件的期望值。必须继续决定并实现自动路由或把手动选择作为明确验收步骤，然后用真实 UI 和 ledger 验证。

## 6. 尚未通过的验收门槛

以下任一项未完成，Goal 不得结束：

1. **Gate 0：入口和版本**。从干净/新开的 DSH 宿主点击直接入口，确认加载的是当前提交的 ATE Trainer 版本。
2. **Gate 1：干净项目 Agent**。在实际页面创建一个干净 Agent，打开原生会话，输入固定 smoke，确认 fresh child、工具/终态和证据。
3. **Gate 2：Agent 优化回归**。在原生会话中把 Agent 改成计算 `11*21`，实际调用 apply/validate，比较新旧 revision 和运行结果；旧 revision 必须仍可追溯。
4. **Gate 3：工作流编辑和 handoff**。实际创建或编辑工作流，点击添加、排序并保存至少 T2→T1 顺序，再从原生会话运行，确认每个 fresh child、输入输出和顺序证据；不能只复用现有“新工作流 1”。
5. **Gate 4：恢复和错误**。实际刷新 Trainer、重开 DSH 宿主、重复打开、切换 target/revision，并验证过期绑定、无宿主、错误 origin、重复 nonce 的明确结果；不得回退到白页桥接 transcript。
6. **Gate 5：八专家 smoke、冻结、发布和工程回放**。按 `AGENTS.md` 的八专家 smoke 合同点击实际入口，确认精确输入、fresh child、`answer:3`、`SMOKE_ONLY`、`businessGatePassed:false`；再点击冻结/发布/工程运行，确认 pinned snapshot、publish run 和训练候选隔离。不得恢复历史 DFT/schematic/business gate。
7. **Gate 6：流式、时序、哈希和模型**。保存 prompt、首 token、工具事件、终态时间；核对小写 64 位 SHA-256；核对最终实际 provider/model；完成回滚演练并记录结果。

## 7. 新会话工作规则

- 每修复一个缺口，先写/更新开发计划、验收计划、报告和 evidence，再运行相关测试。
- 采用实际点击验证，不用脚本直接调用接口冒充用户操作；必要时用 CUA 的 accessibility tree、截图和原生输入作为证据。
- 原生窗口必须显示真实 DSH workspace、用户消息、工具事件和 assistant 终态；白页只负责入口、绑定状态和回执。
- 所有 smoke 结果保持 `SMOKE_ONLY` / `businessGatePassed:false`。业务模式 `BUSINESS_ONLY` 不自动进入发布。
- 不要把 agent-T1 的已有成功、工作流已有成功、或模型手动切换成功扩大解释为全部通过。
- 只有当 Gate 0–6 和模型路由项均有可追溯证据、测试结果和 Git 提交时，才更新 Goal 为 complete；否则保持 active，继续修复/重测。



## Continuation update 2026-09-30

A fresh Trainer page visibly exposed and accepted the renamed synthetic BUSINESS_ONLY control (23*24+45=597). The page run completed as framework-5fd337b7-8548-4874-b1a2-cfedabff337c with answer 597 and businessGatePassed:false. The underlying framework purpose is FRAMEWORK_TRAINING because the runtime rejects arbitrary run purposes; the UI label and evidence explicitly classify this as synthetic BUSINESS_ONLY and no real business gate was executed. Use DeepSeek-V4-Flash / High in the native model selector. Do not claim full completion until remaining release/rollback and restart gates are independently verified.
