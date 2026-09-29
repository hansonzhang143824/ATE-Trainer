# Agent Trainer 空白系统开发与验证计划

版本：2026-09-29
范围：空白 Agent Trainer 基础控制体系
验收入口：白色 Agent Trainer 页面
排除范围：真实业务流、半导体业务规则、八位历史专家的活动执行

## 1. 目标与范围

本轮目标是验证 Agent Trainer 能否作为一个通用的空白控制体系使用：用户可以从零创建 Agent，训练和优化 Agent，创建工作流，调整工作流顺序，冻结并发布版本，再在工程模式中调用已发布版本。

当前产品不预置 DFT、原理图、策略、方法、规则评审、ATE 实现、编译诊断和演进专家。八位专家的资料只作为隔离的历史参考资料保存，不进入当前 registry、运行、发布或工程模式。

白色 Agent Trainer 是唯一产品界面和唯一验收入口。PTC 控制面只保留后台 API、运行调度、版本冻结、发布隔离和 DSH 原生会话桥接能力；不再作为第二套用户操作面板。

## 2. 不变量

1. 活动 registry 初始为空，不包含历史专家和历史工作流。
2. 历史专家资料与活动 registry、候选版本、运行目录和发布包完全隔离。
3. 新建 Agent 的 ID、指令、输入输出 Schema、Skill、脚本、权限和交接规则由当前候选配置决定，不得固定调用历史 Agent。
4. Agent 优化必须产生新的 revision，旧 revision 保留且可追溯。
5. 优化会话必须使用 `agent-trainer` 预设和 Trainer 工具：`trainer_context`、`trainer_assets`、`trainer_apply_changes`、`trainer_validate`、`trainer_run` 等。
6. 优化会话不得使用 `bash`、PowerShell 或直接编辑工作区文件来代替 Trainer 候选修改。
7. 工作流运行必须记录 workflow ID、参与 Agent ID、每一步 revision、run ID、输入、实际 JSON 输出和最终状态。
8. 发布版本冻结后，工程模式只能读取发布快照；候选修改不得改变已发布运行结果。
9. 本计划不验证真实业务输出，也不恢复历史专家业务流程。

## 3. 开发计划

### D1. 历史资料隔离

1. 为八位历史专家建立只读历史资料目录。
2. 保存每位专家的职责、内部流程、记忆、Skill、脚本、输入输出 Schema、交接规则、版本和已有证据。
3. 从活动 registry、默认种子、白色页面初始状态、SMOKE_ONLY 活动路径和工程模式列表中移除八位专家。
4. 添加检查：活动 registry 不得引用历史专家 ID，运行和发布包不得读取历史目录。

交付物：历史资料索引、隔离目录、活动 registry 为空的证据。

### D2. 空白 registry 与白色入口

1. 白色 Agent Trainer 从空 registry 加载。
2. 左侧 Agent 和工作流列表允许为空。
3. 保留新建 Agent、新建工作流、训练模式、发布模式和工程模式交互。
4. PTC 深色面板只保留“打开 AT Trainer”入口和宿主能力。
5. 白色页面显示真实 API 返回的数据，不显示历史专家占位数据。

交付物：空 registry 页面截图、API 响应、电脑点击记录。

### D3. 新建 Agent 与配置持久化

1. 支持创建 Agent ID、显示名、职责、输入 Schema、输出 Schema、Skill、脚本、权限和交接规则。
2. 保存候选时以原子变更写入新的 candidate revision。
3. 运行时读取保存后的配置快照，不能只使用页面内存或一次会话回复。
4. 运行记录绑定 Agent ID、revision、run ID 和实际输出。

交付物：Agent manifest、instructions、输入输出 Schema、candidate revision、run evidence。

### D4. Agent Trainer 优化链路

1. 从白色页面选择 Agent 后创建真实 `agent-trainer` 原生会话。
2. 会话绑定 project、target Agent、candidate revision 和运行上下文。
3. 会话启动时确认 Trainer 工具目录；缺少 `trainer_context` 时直接阻断。
4. 优化 Agent 先读取 `trainer_context` 和 `trainer_assets`，再根据用户请求调用 `trainer_apply_changes`。
5. 保存后生成新的 revision 和 change set。
6. 使用新的 revision 运行 Agent，旧 revision 仍可复现。
7. 会话复用必须校验预设；普通 DSH 会话不能被当作优化会话复用。

交付物：session binding、工具目录证据、change set、前后 revision、对比运行记录。

### D5. 工作流编排与交接

1. 支持创建空工作流和加入 Agent。
2. 支持设置执行顺序、输入映射和输出映射。
3. 每个步骤固定实际 Agent ID 和 revision。
4. 相邻步骤只通过声明的输入输出合同传递 JSON。
5. 运行记录显示参与 Agent、顺序、每步状态、输入、输出和合同校验结果。
6. 修改工作流时生成新的 workflow revision，旧 revision 不覆盖。

交付物：workflow manifest、步骤版本快照、映射记录、运行记录。

### D6. 发布与工程模式隔离

1. 只有完成验证的候选 Agent 和工作流才能冻结。
2. 发布时生成不可变发布包和完整哈希记录。
3. 工程模式只读取已激活发布版本。
4. 工程模式不能看到未发布 Agent 或工作流。
5. 发布后修改候选配置不得改变已发布包和工程模式运行结果。

交付物：冻结版本、发布包、哈希、工程模式读取和运行证据。

### D7. 验证与 Git checkpoint

每完成 D1–D6 一个阶段，必须执行对应定向测试、保存证据并建立 Git checkpoint。任何阶段失败时停止后续验收，修复后从失败阶段重新执行。不得用预先写入的 PASS 替代实际点击结果。

## 4. 基础功能验收：新 Agent 与工作流

本章由主会话按步骤实际执行。结果栏只能在点击验证并取得证据后填写，执行前保持空白或填写“未执行”。任一步失败，停止后续验收并先修复。

### A. 新建 Agent

操作：

1. 在白色 Agent Trainer 界面点击“新建 Agent”。
2. 创建 `agent-T1` 并保存候选版本。
3. 打开该 Agent 的原生 Trainer 会话。
4. 输入：`1+2等于几，把答案写在JSON里`。
5. 确认输出为 `{"answer":3}`。
6. 保存 Agent 版本。
7. 返回 Agent 页面运行 `agent-T1`。

通过条件：

- Agent 创建成功；
- 原生会话可执行；
- 输出为 `{"answer":3}`；
- 保存后运行结果仍为 `3`；
- 使用的是新建 Agent，不得固定调用 `ptc-dft-expert`。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Agent ID | |
| revision | |
| run ID | |
| 原生会话 ID | |
| 实际 JSON 输出 | |
| 最终状态 | 未执行 |

### B. 优化 Agent

操作：

1. 打开 `agent-T1` 的原生 Trainer 会话。
2. 输入：将执行内容改为 `2+3`，结果写入 JSON。
3. 确认使用 `trainer_context`、`trainer_assets`、`trainer_apply_changes` 完成修改。
4. 保存新的 Agent revision。
5. 运行最新 revision。

通过条件：

- 产生新的 Agent revision；
- 最新版本输出为 `{"answer":5}`；
- 原 revision 未被覆盖；
- 修改通过 Trainer 能力完成，不得使用 `bash` 直接编辑工作区。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Agent ID | |
| 原 revision | |
| 新 revision | |
| change set ID | |
| run ID | |
| 实际 JSON 输出 | |
| 工具调用证据 | |
| 最终状态 | 未执行 |

### C. 单 Agent 工作流

操作：

1. 创建 `workflow-T1`。
2. 加入 `agent-T1`。
3. 执行工作流并输入 `1+2`。

通过条件：

- 工作流创建成功；
- 实际调用 `agent-T1`；
- 输出为 `3`；
- 运行记录包含 workflow ID、Agent ID 和 revision。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Workflow ID | |
| Agent ID | |
| Workflow revision | |
| run ID | |
| 实际 JSON 输出 | |
| 最终状态 | 未执行 |

### D. 双 Agent 工作流

操作：

1. 创建 `agent-T2`，配置为执行 `2+3`。
2. 将 `agent-T2` 加入 `workflow-T1`。
3. 执行工作流。

预期结果：

```json
{
  "agent-T1": {"answer": 3},
  "agent-T2": {"answer": 5}
}
```

通过条件：

- 两个 Agent 都被实际调用；
- 输出按 Agent ID 正确对应；
- 无串结果、旧结果复用或固定 Agent 替代。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Workflow ID | |
| Workflow revision | |
| Agent 顺序 | |
| Agent revision 列表 | |
| run ID | |
| 实际 JSON 输出 | |
| 最终状态 | 未执行 |

### E. 三 Agent 工作流

操作：

1. 创建 `agent-T3`，配置为执行 `3+4`。
2. 加入 `workflow-T1`。
3. 执行工作流。

通过条件：

- 三个 Agent 都执行成功；
- 结果分别为 `3、5、7`；
- 运行记录包含三个独立 Agent。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Workflow ID | |
| Workflow revision | |
| Agent 顺序 | |
| Agent revision 列表 | |
| run ID | |
| 实际 JSON 输出 | |
| 最终状态 | 未执行 |

### F. 交换 Agent 顺序

操作：

1. 将顺序从 `T1 → T2 → T3` 改为 `T3 → T1 → T2`。
2. 保存新的工作流 revision。
3. 再次执行。

通过条件：

- 执行顺序变为 `T3、T1、T2`；
- 结果仍正确对应：
  - `T3 = 7`
  - `T1 = 3`
  - `T2 = 5`
- 旧工作流 revision 可追溯且未被覆盖。

结果记录：

| 项目 | 实际结果 |
|---|---|
| 原 Workflow revision | |
| 新 Workflow revision | |
| 实际执行顺序 | |
| Agent revision 列表 | |
| run ID | |
| 实际 JSON 输出 | |
| 最终状态 | 未执行 |

### G. 发布与工程模式

操作：

1. 冻结通过验收的工作流 revision。
2. 发布该版本。
3. 进入 DSH 工程模式。
4. 确认能看到已发布工作流和对应 Agent。
5. 执行一次工程模式运行。
6. 修改候选工作流但不重新发布，再次检查工程模式。

通过条件：

- 工程模式只能看到已发布版本；
- 发布版本运行结果仍为 `3、5、7`；
- 未发布修改不会影响已发布版本。

结果记录：

| 项目 | 实际结果 |
|---|---|
| Frozen version | |
| Release ID | |
| Published workflow ID | |
| Published Agent ID 列表 | |
| Engineering run ID | |
| 发布版本实际 JSON 输出 | |
| 未发布修改后的工程结果 | |
| 最终状态 | 未执行 |

## 5. 统一证据要求

每个步骤必须记录：

- Agent ID；
- 工作流 ID；
- Agent revision；
- Workflow revision；
- 原生会话 ID（涉及 Trainer 时）；
- change set ID（涉及修改时）；
- run ID；
- 实际 JSON 输出；
- 输入合同和输出合同校验结果；
- 最终状态；
- 白色界面 computer-use 操作证据。

不得使用以下内容作为通过证据：

- 预先写入的 completed 或 PASS；
- 原生会话中一次正确回复但未保存候选；
- 页面内存状态但没有服务端 revision；
- 固定历史 Agent 的模拟输出；
- 只显示工作流名称但没有实际 Agent 步骤记录。

## 6. 计划评审状态

本文件是待 review 的开发与验证计划。A–G 结果在实际执行前保持“未执行”，不得提前填写通过。
