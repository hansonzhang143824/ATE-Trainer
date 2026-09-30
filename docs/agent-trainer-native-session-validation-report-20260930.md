# Agent Trainer 原生会话替代验证报告

日期：2026-09-30  
范围：Agent Trainer 白页入口、DSH 原生 Agent 会话、DSH 原生工作流会话、候选优化与运行复核。

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
| 原生会话、bundle、客户端状态、空系统定向测试 | 28/28 通过 |
| 根目录 A-G 证据测试 | 2/2 通过 |
| 白页残留 `session.prompt` / `session.history` / textarea | 未发现 |

插件完整测试集共 377 项，其中 317 项通过、60 项失败。失败项集中在本机既有环境和历史业务 fixture：`spawnSync python EPERM`、缺失的 stage registry fixture、业务源/发布 fixture 不完整等；与本次三个原生会话文件无关。原生会话相关定向测试和浏览器点击验收均通过。

## 点击式正向验收

### Agent 原生会话

从 DSH PTC 面板点击打开白色 Agent Trainer，再点击“打开当前专家原生会话”。DSH 宿主显示真实窗口标题 `Agent Trainer · agent-T2 — DeepSeek Harness`，preset 为 `agent-trainer`。在 DSH 原生输入框中发送上下文读取指令，真实事件包含 `trainer_context` 和 `trainer_assets`，DeepSeek 返回了当前 agent、candidate revision 和运行状态。

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

> DSH 宿主未在 15 秒内确认原生窗口，请从 DSH PTC 面板重新打开。

页面没有白页输入框、没有本地 transcript，也没有静默伪造成功。

## 边界说明

- 八专家 smoke 结果仍按项目约束标记 `SMOKE_ONLY` / `businessGatePassed:false`；本次变更没有重新激活历史 DFT、schematic 或业务 gate。本文记录的 Agent 优化和 workflow training 运行属于训练范围，均保留 `businessGatePassed:false`，不产生发布 release。
- Agent-T2 的 `11*21=231` 是候选优化验证，不替换八专家 smoke 固定题 `1+2=3`。
- 当前会话 `freeze:false`，因此本次没有执行冻结和发布；发布仍需按独立发布决策完成 smoke 全链证据后进行。
