# Agent Trainer 原生会话替代验证报告

日期：2026-09-30  
范围：DSH 直接 ATE Trainer 入口、Agent Trainer 工作台、DSH 原生 Agent 会话、DSH 原生工作流会话、候选优化与运行复核。

## 续验审计更正（2026-09-30）

本报告是部分验证记录，不能作为 Gate 0–6 全部 PASS 的证明。上一轮宣告全部完成过早，当前继续验收。已定位的代码缺口包括：先打开原生窗口再绑定 Trainer、复用缓存未重新核对服务端绑定、消息响应未检查 nonce 和来源、多宿主广播可重复处理、缓存键缺少 project/mode。修复后必须重新进行点击验证。

待补证据：干净项目现场创建、工作流原生顺序修改、刷新/宿主重开/过期和错误绑定、八专家 smoke 冻结发布与工程回放、回滚演练。直接入口和 Agent 原生会话已有带时间、原生 AX 和 SHA-256 的新证据，但不能替代其余 Gate。

## 交付与回滚证据

- 回滚基线：`dea25de chore: checkpoint before native session replacement`
- 开发与验收计划：`8e4ff39 docs: define native session development and click acceptance`
- 原生会话实现：`3ff3dac feat: launch agent trainer in native DSH sessions`
- 生成 bundle 校正：`24ca2b5 chore: regenerate native session client bundle`
- 受影响的实现文件：
  - `docs/prototypes/agent-trainer-repair-prototype.html`
  - `plugins/dsh-ptc-control-plane/client/panel.js`
  - `plugins/dsh-ptc-control-plane/lib/client.js`

## 静态与构建验证

| 检查 | 结果 |
|---|---|
| `node --check plugins/dsh-ptc-control-plane/client/panel.js` | 通过 |
| `node --check plugins/dsh-ptc-control-plane/lib/client.js` | 通过 |
| `npm run build:client` | 通过；生成 bundle 与源码一致 |
| 原生会话 launcher 定向测试 | 11/11 通过（`--test-isolation=none`） |
| 空系统与直接 ATE Trainer 入口定向测试 | 4/4 通过（`--test-isolation=none`） |
| 根目录 A-G 证据测试 | 2/2 通过 |
| 白页残留 `session.prompt` / `session.history` / textarea | 未发现 |

上一轮插件完整测试集共 377 项，其中 317 项通过、60 项失败。输出包含 `spawnSync python EPERM`、stage registry 和发布 fixture 错误。尚未在相同环境对照基线重跑，不能把全部失败归为历史问题或断言与本次改动无关。本轮两个定向文件在 `--test-isolation=none` 下共 15/15 通过；普通隔离模式仍受当前 Windows `spawn EPERM` 限制，不能把它当作通过。定向测试也不能代替本计划的完整点击验收。

## 点击式正向验收

### 直接 ATE Trainer 入口（本轮新增）

DSH 宿主页面实际显示单层入口“打开 ATE Trainer”，链接指向带当前 `nativeHost` 的 `/agent-trainer` 工作台；入口旁标注“直接进入 Trainer；原生会话仍由 DSH 宿主承载”。没有先展开 PTC 面板的第二次点击。点击后白页显示候选 revision 和 Agent/工作流选择器，说明入口替换已经接入实际 DSH 插槽。

本轮实际点击 `agent-T1` →“打开当前专家原生会话”，白页回执为：

```text
已请求 DSH 宿主打开原生会话 · agent · agent-T1 · session session-ca6a57d2-5ee0-4ec8-a446-0580132c067f
训练入口已切换到 DSH 原生会话
preset: agent-trainer · target: agent/agent-T1
```

随后在真实 DSH 原生输入框中发送：

```text
请只读取 trainer_context，用一句人话告诉我当前绑定的是哪个 agent；不要修改候选，不要运行工作流。
```

宿主实际产生 `trainer_context · {}` 工具调用，原生回复为“当前绑定的是 agent-T1 这个 agent（项目 agent-trainer，训练模式，候选版本 revision-c9f89fa5…）”，并显示 `用时 11 秒、首 token 4.9 秒、66 tok/s`。绑定文件为 `Training_Materials/framework/control/bindings/session-ca6a57d2-5ee0-4ec8-a446-0580132c067f.json`，包含 9 个 Trainer 工具和 `deepseek-official/deepseek-v4-flash` 的服务端模型选择。完整点击与输入记录见 `docs/agent-trainer-native-session-evidence-20260930.json`；该文件保存后计算小写 SHA-256。

同一原生窗口随后实际发送固定 smoke 输入 `1+2等于几，把答案写在JSON里`，收到合法 JSON `{ "answer" :  3 }`；原生界面显示本轮用时 6 秒、首 token 5.2 秒、64 tok/s。该结果只证明当前 Agent 的原生调用链可用，仍按 `SMOKE_ONLY` / `businessGatePassed:false` 解释，不代表业务能力或发布已通过。

### 工作流原生会话

通过 Trainer 页面实际点击工作流“新工作流 1”→“在 Trainer 中训练当前工作流”，DSH 打开工作区 `ATE Trainer · workflow:custom-workflow-1`，session 为 `session-7bda7999-35ca-49a5-b214-16ad2598b609`。原生输入先调用 `trainer_context`/`trainer_runs`，随后调用 `trainer_validate` 和 `trainer_run`；事件流显示 step-1 至 step-4 全部完成，`childTerminationConfirmed=true`。真实步骤输出为 `3 → 231 → 3 → 3`，最终 `{ "answer":3,"mode":"SMOKE_ONLY","businessGatePassed":false }`，run 为 `framework-9b806116-73cf-496a-a8e8-183bb6dff7e0`。

模型核对发现：绑定文件期望 `deepseek-official/deepseek-v4-flash`，但工作流原生窗口初始实际请求为 `zai-coding-cn/glm-5.3-flash`；在原生模型选择器实际点击 `DeepSeek-V4-Flash` 后，下一轮真实 ledger 变为 `deepseek-official/deepseek-v4-flash`，回复用时 1 秒、首 token 1.4 秒、429 tok/s。入口默认模型是否自动切换仍是未完成项，不能把“绑定期望”当成“默认实际”。

### Agent 原生会话

从 DSH 的“打开 ATE Trainer”直达入口进入白色 Agent Trainer，再点击“打开当前专家原生会话”。DSH 宿主显示真实窗口标题 `Agent Trainer · agent-T1`，preset 为 `agent-trainer`。在 DSH 原生输入框中发送上下文读取指令，真实事件包含 `trainer_context`，原生回复返回了当前 agent、candidate revision 和运行状态。

随后在同一个原生窗口输入优化指令，要求把 Agent 改成计算 `11*21`，并要求调用 `trainer_apply_changes`、`trainer_validate`。真实结果：

- 新 revision：`revision-3aadcf48-da49-45cd-b7b6-2f6e3ab84d92`
- changeSet：`change-34aa609b-86bb-4802-9b95-05fcd107bd20`
- `trainer_validate.ok=true`，无 errors
- 新运行：`framework-cb133349-894f-43e5-b46e-65e7819da2bf`
- 新运行 JSON：`{"answer":231}`

用原生会话指定旧 revision `revision-c8620b6f-c92f-46d6-9a63-1b156ed09d99` 重跑，得到旧运行 `framework-0b06781b-753c-4ae8-a225-2577fe6da99b`，JSON 为 `{"answer":5}`。`trainer_compare` 证明 before/after bundle 不同，且 changeSet 正确关联旧 revision 与新 revision。

### 工作流原生会话

点击“在 Trainer 中训练当前工作流”，DSH 宿主显示原生工作流会话，preset 为 `agent-trainer`。在原生输入框中要求读取工作流上下文并调用 `trainer_run`，真实运行：

- 会话：`session-5093a986-96ef-47f7-ac3d-8f706f42f2e9`
- 运行：`framework-209de487-5cde-4025-a1f5-62badc3c54c9`
- 状态：`completed`，`childTerminationConfirmed=true`
- step-1 `custom-agent-1` 输出 `{"answer":3}`
- step-2 `agent-T2` 接收 `{"answer":3}`，输出 `{"answer":231}`
- step-3 `agent-T3` 接收 `{"answer":231}`，输出 `{"answer":7}`
- 工作流最终输出 `{"answer":7}`，workflow validation `ok=true`

最终输出为 7 是当前 workflow-T2 固定 Agent 指令的既有行为；它证明了原生窗口、真实工具调用、fresh child 和 handoff 均已生效，不代表工作流已经被改造成通用乘法器。

### 重复打开与恢复

对同一 workflow/target/revision 连续点击入口，首次会话为 `session-47e4cfab-c7af-43e7-9d8b-c560926a4ffe`，第二次点击返回相同 session ID，并在白页显示“已复用有效会话”。宿主缓存使用 target、candidate revision、selected run 和 preset 组成复用键，避免重复窗口和错误绑定。

### 宿主不可用负向验收

在没有 DSH opener 的独立白页中，实际点击“打开当前专家原生会话”，等待 15 秒后显示：

> DSH 宿主未在 15 秒内确认原生窗口，请从 DSH“打开 ATE Trainer”入口重新打开。

页面没有白页输入框、没有本地 transcript，也没有静默伪造成功。

## 边界说明

- 八专家 smoke 结果仍按项目约束标记 `SMOKE_ONLY` / `businessGatePassed:false`；本次变更没有重新激活历史 DFT、schematic 或业务 gate。本文记录的 Agent 优化和 workflow training 运行属于训练范围，均保留 `businessGatePassed:false`，不产生发布 release。
- Agent-T2 的 `11*21=231` 是候选优化验证，不替换八专家 smoke 固定题 `1+2=3`。
- 上一轮没有执行冻结和发布。`freeze:false` 是原生工具权限边界；本计划要求通过页面按钮验证 smoke 冻结/发布，仍需补做。BUSINESS_ONLY 业务发布继续要求独立决策。


## 2026-09-30 continuation: synthetic BUSINESS_ONLY proof

A fresh Trainer page visibly exposed and accepted the renamed synthetic BUSINESS_ONLY control (23*24+45=597). The authoritative UI run was framework-5fd337b7-8548-4874-b1a2-cfedabff337c: input 23*24+45, output {"answer":597}, businessGatePassed:false, childTerminationConfirmed:true, model deepseek-official/deepseek-v4-flash. The native workflow proof remains framework-58cbd823-0b20-4b8e-93a9-702e2d25fa2b with one saved step custom-agent-7 and final answer 597. This is synthetic wiring evidence only; it does not certify semiconductor work or a real business gate.

The five dispatched eight-expert smoke receipts remain archive-only under team/ptc/native-control-plane/archive/SMOKE-EIGHT-20260930/manifest.json. Implementer, compile, and evolution were not dispatched. The active registry is empty. The sanctioned restart reached gate A but gate B remains blocked by the existing workspaceRegistry assertion; the server was not stopped.

### Current scope correction

The active user scope has eight-expert dispatch disabled. The current direct acceptance set is 63/63 passed: native session binding/selection, session recovery, Agent Trainer runtime/API, workflow editing and execution, and the synthetic `BUSINESS_ONLY` expression `23*24+45=597`. The full legacy `all.test.mjs` Gate B is not a valid completion signal for this scope because it still asserts archived eight-expert and real business-release behavior; it reports 325 passed and 63 failed in the current sandbox. No server restart is claimed from that result.
\n### Sanctioned restart gates (2026-09-30T14:25:39Z)\n\nThe sanctioned dsh-plugin-restart.ps1 -Profile web -Port 3080 -GatesOnly -WaitSeconds 0 completed with Gate A exit 0, Gate B exit 0, and Gate C exit 0. The server was untouched. Evidence: C:/Users/nvt10241/AppData/Local/Temp/dsh-plugin-restart-20260930-221743. The default sandbox had previously returned spawnSync python EPERM; the same release tests passed 10/10 and the sanctioned gates passed when child processes were permitted.\n