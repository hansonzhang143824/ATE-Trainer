# DSH 原生 PTC 训练与发布控制面实施计划

> 状态：实施中；阶段 1 原生控制面已安装到 DSH 3080，阶段 2～5 继续开发  
> 日期：2026-09-22  
> 工作区：`D:\Newtest\DSH\ATE-Coding-Flow`  
> 决策人：用户  
> 实施统筹：Codex

## 1. 已确认的核心决策

1. 放弃现有 4090 独立专家控制台，不迁移页面、不兼容旧 API、不做双轨运行。
2. 最终只运行 DSH；训练、评估、发布和正式运行控制全部成为 DSH 原生能力。
3. 不再运行 `tools/expert-console.mjs`，不再使用 4090 端口。
4. 不再通过 HTTP 桥接 DSH 3080，也不再轮询、解压 DSH 的 `.zstd` 会话日志。
5. 训练与正式交付不是一个可随时改变的全局开关，而是两种不同的运行身份。
6. 每次运行创建时固定其模式、Agent 版本、编排版本、输入输出目录和发布版本；运行中不得切换。
7. 发布对象不是单个 Agent，而是一套完整的 Release Bundle：Agent、编排、合同、边界、门禁与验证证据一起冻结。
8. 发布模式可以运行、暂停、停止、恢复、沟通和登记问题，但不能修改 Agent 或编排逻辑。

## 2. 目标与非目标

### 2.1 目标

- 在 DSH 内提供 `PTC Training` 和 `ATE PTC Runtime` 两种明确入口。
- 训练模式支持单 Agent 训练和完整流水线训练。
- 训练模式可以修改候选 Agent 草稿和候选编排，并在隔离目录中复测。
- 点击发布时执行完整评估，成功后生成不可修改的发布快照。
- 正式运行只使用已冻结的 Release Bundle。
- 主机层强制训练目录、交付目录和发布快照边界，不依赖 Agent 自觉。
- 正式运行中支持暂停、恢复、停止、查看状态和补充沟通。
- 发现的问题可以登记回训练待办，但不能在正式运行中现场修改规则。
- DSH 重启后可以恢复训练运行、正式运行和发布版本身份。

### 2.2 非目标

- 不复制 4090 的页面布局。
- 不迁移 4090 的五个页签。
- 不保留 `/api/trainer/send`、`/api/trainer/poll` 等兼容接口。
- 不继承旧 Trainer 会话。
- 不追求与旧控制台的视觉一致。
- 不在第一版实现复杂图表、历史数据分析和装饰性仪表盘。

## 3. 目标架构

```text
DSH
├─ dsh-ptc-control-plane
│  ├─ DSH 原生控制界面
│  ├─ 训练运行管理
│  ├─ 流程训练编排
│  ├─ 草稿评估
│  ├─ Release Bundle 发布
│  ├─ 暂停、恢复、停止和沟通
│  └─ 运行事件与状态恢复
│
├─ dsh-ptc-material-boundary
│  ├─ 训练态目录边界
│  ├─ 正式态目录边界
│  ├─ 发布态修改禁令
│  ├─ Agent 身份与回执验证
│  └─ 发布快照哈希验证
│
└─ DSH 原生服务
   ├─ sessions
   ├─ agents
   ├─ subagents
   ├─ events
   ├─ webServer
   └─ client slots
```

建议新建独立插件 `dsh-ptc-control-plane`，保留 `dsh-ptc-material-boundary` 作为独立安全边界。控制面故障不应削弱边界保护。

## 4. 两种运行身份

### 4.1 PTC Training

- 使用 Agent 草稿。
- 使用编排草稿。
- 输入和产物全部写入训练运行目录。
- 可以单独运行一个 Agent。
- 可以运行完整阶段链。
- 可以生成和采纳训练提案。
- 可以修改草稿并复测。
- 可以执行评估和发布。
- 禁止写正式项目与正式交付产物。
- 禁止直接改写已发布快照。

### 4.2 ATE PTC Runtime

- 使用创建批次时固定的 `releaseId`。
- 使用 Release Bundle 内冻结的 Agent 和编排。
- 只写正式项目与批次目录。
- 可以暂停、恢复、停止和向当前 Agent 追加运行消息。
- 可以登记训练问题。
- 禁止修改 Agent 草稿、发布版本、合同、案例、编排和插件规则。
- 新版本发布后，已经运行的批次继续使用原 release，不得中途漂移。

## 5. 目录与产物模型

### 5.1 Agent 资产

```text
team/expert-profiles/<profileId>/
├─ instructions.md                 # 草稿
├─ profile.yaml                    # 草稿
├─ output-contract.schema.json     # 草稿
├─ cases/                          # 草稿案例
├─ evaluation/                     # 草稿评估
├─ status.json
└─ versions/vN/                    # 已发布、不可修改快照
```

### 5.2 训练运行产物

现有平铺训练目录保留作兼容参考；新的训练执行全部使用独立运行目录：

```text
Training_Materials/runs/<trainingRunId>/
├─ run.json
├─ input/
├─ input-sync/
├─ strategy/
├─ method/
├─ review/
├─ implementation/
├─ compile/
├─ verification/
├─ receipts/
└─ ErrorLog/
```

这样可以并行训练、重复复测和保留失败证据，不会互相覆盖。

### 5.3 正式交付产物

```text
project/<ProjectName>/Input_GlobalMaterial/
project/<ProjectName>/Output_Global_Material/
project/<ProjectName>/ErrorLog/

team/artifacts/<batchId>/<tm>/
├─ input-manifest.json
├─ strategy/
├─ method/
├─ review/
├─ implementation/
└─ compile/
```

### 5.4 发布包

```text
team/ptc/releases/
├─ active-release.json
└─ ptc-release-vN/
   ├─ release-manifest.json
   ├─ profiles/
   ├─ orchestration/
   ├─ contracts/
   ├─ policies/
   └─ verification/
```

`active-release.json` 只保存当前活动版本指针。发布先在临时目录完整生成并验证，最后原子切换指针，禁止半发布。

## 6. Release Bundle 必须固定的内容

- 每个 Agent 的 profileId、版本和文件哈希。
- Agent 指令、边界、输出合同和案例版本。
- `ptc_stage_registry` 编排快照。
- Captain 入口与阶段推进规则。
- 派发器身份和关键策略哈希。
- 上下游交接合同。
- 关键门禁与校验脚本哈希。
- 单 Agent 评估结果。
- 完整流程回归结果。
- 发布者、发布时间、上一版本和回退指针。

正式派发前必须复核 Release Bundle 自身哈希。任何快照漂移都必须拒绝运行。

## 7. 分阶段实施计划

### 阶段 0：冻结当前基线

工作：

- 记录现有专家已发布版本和哈希。
- 记录当前阶段注册表、派发器和边界插件状态。
- 保存 4090 功能清单作为历史参考。
- 建立回退点。
- 清理插件源码中旧工作区硬编码，改成安装配置注入。

产物：

```text
team/ptc/migration/baseline-manifest.json
team/ptc/migration/4090-feature-reference.json
team/ptc/migration/rollback-plan.md
```

预计 Codex 主动时间：1～1.5 小时。

### 阶段 1：DSH 原生控制面骨架

工作：

- 新建 `plugins/dsh-ptc-control-plane/`。
- 注册 DSH 服务端插件和客户端面板。
- 接入 sessions、agents、subagents、events 和 webServer。
- 显示当前训练运行、正式批次、草稿状态和活动 release。
- 不再依赖 4090。

验收：

- DSH 启动后自动出现 PTC 控制入口。
- 4090 不运行时状态读取正常。
- 插件重启门禁全部通过。

预计 Codex 主动时间：2～3 小时。

### 阶段 2：运行身份与硬目录隔离

工作：

- 建立不可变的 run context。
- 增加 `PTC Training` 与 `ATE PTC Runtime` 两个身份入口。
- 控制 API、工具守卫和路径守卫同时检查运行身份。
- 去除全局 `activeMode` 对运行行为的控制权。

验收：

- 训练态写 `project/DALI` 被主机拒绝。
- 正式态写 Agent 草稿或编排草稿被主机拒绝。
- 训练态直接改 `versions/vN` 被主机拒绝。
- 运行中的任务不受页面模式切换影响。

预计 Codex 主动时间：3～4 小时。

### 阶段 3：单 Agent 训练

工作：

- 选择 Agent、案例或 TM。
- 创建隔离训练运行。
- 使用草稿 Agent 执行。
- 展示输入、输出、门禁、耗时和失败原因。
- 支持问题材料转提案、写草稿和同案例复测。
- 支持失败案例进入回归案例库。

首个验收案例：TM109 的 DFT Expert。

验收：

- 哈希一致时快速 `UNCHANGED`。
- 合同错误能稳定复现。
- 修改草稿后可以复测。
- 正式项目目录零变化。

预计 Codex 主动时间：3～4 小时。

### 阶段 4：完整流程训练

工作：

- 使用候选 Agent 集合和候选编排运行完整阶段链。
- 支持选择阶段范围。
- 每阶段生成身份回执与交接证据。
- 支持暂停、恢复和单阶段重跑。
- 检查错派、重复派发、错误推进、漏停和合同不一致。

阶段链：

```text
INPUT_SYNC
→ STRATEGY
→ METHOD
→ RULE_REVIEW_METHOD
→ IMPLEMENTATION
→ RULE_REVIEW_IMPLEMENTATION
→ COMPILE
```

验收：

- 完整训练 TM 跑通。
- 每阶段注入失败时停在正确位置。
- 训练运行不创建正式批次。
- 所有产物只进入对应训练运行目录。

预计 Codex 主动时间：4～6 小时。

### 阶段 5：原子发布

发布流程：

1. 锁定草稿集合和编排草稿。
2. 评估所有变更 Agent。
3. 校验合同和上下游兼容性。
4. 运行完整流程回归。
5. 生成专家和编排快照。
6. 生成 Release Bundle manifest。
7. 复算全部哈希。
8. 原子更新活动 release 指针。
9. 写发布记录和回退点。

验收：

- 任一步失败都不改变活动 release。
- 发布后修改草稿不影响正式版本。
- 修改发布快照任意字节都会被正式派发拒绝。
- 可以回退到上一 release。

预计 Codex 主动时间：3～4 小时。

### 阶段 6：正式运行锁定与控制

允许：

- 新建正式批次。
- 查看状态、产物和回执。
- 暂停自动推进。
- 停止和恢复。
- 向当前 Agent 追加运行消息。
- 将问题登记为训练待办。

禁止：

- 修改 Agent 指令、边界、合同和案例。
- 修改阶段注册表和派发逻辑。
- 覆盖发布快照。
- 让运行中的批次切换 release。

预计 Codex 主动时间：2～3 小时。

### 阶段 7：全量回归与切换

必须验证：

1. 单 Agent 训练。
2. 完整流程训练。
3. 训练目录越界拒绝。
4. 正式目录越界拒绝。
5. 发布失败回滚。
6. 发布快照篡改拒绝。
7. DSH 重启恢复。
8. 训练和正式交付同时运行。
9. 新 release 不影响旧批次。
10. 暂停后不再派发。
11. 沟通只影响当前任务，不改变合同。
12. TM109 DFT 快速复用。
13. DFT-only 请求不得派发 Schematic Expert。
14. 4090 完全不运行时所有功能正常。

完成后：

- 从启动说明中移除 4090。
- `tools/expert-console.mjs` 与旧 HTML 只归档，不参与运行。
- 更新操作说明和故障恢复文档。

预计 Codex 主动时间：3～4 小时；测试、重启与观察 4～7 小时。

## 8. 时间预算

| 阶段 | Codex 主动时间 |
|---|---:|
| 基线冻结 | 1～1.5 小时 |
| 原生控制面骨架 | 2～3 小时 |
| 模式与目录硬隔离 | 3～4 小时 |
| 单 Agent 训练 | 3～4 小时 |
| 完整流程训练 | 4～6 小时 |
| 原子发布 | 3～4 小时 |
| 正式运行控制 | 2～3 小时 |
| 全量回归与切换 | 3～4 小时 |
| **完整生产版合计** | **20～28 小时** |

另需测试运行、重启与观察时间 4～7 小时。连续推进预计 2～3 个工作日。

第一阶段可用版本包括：DSH 双身份入口、目录硬隔离、单 Agent 训练、发布态禁止修改，预计 6～8 小时。

## 9. 回退原则

- 不删除现有专家版本。
- 不覆盖现有发布快照。
- 新插件首次启用时只读现有状态。
- 活动 release 指针始终保留上一版本。
- 插件安装和重启必须经过 DSH 插件安全闸门。
- 新控制面故障时，可以停用控制面插件；材料边界插件继续保护正式运行。
- 旧 4090 文件保留作历史参考，但不作为运行回退方案；回退目标是上一 DSH 原生 release。

## 10. Codex 与 CodeM 协作草案

### 10.1 推荐分工

Codex 负责架构与最终集成：

- 运行身份模型。
- 训练/正式边界。
- Release Bundle。
- 正式派发锁定。
- 与现有 Captain 和 material-boundary 插件集成。
- 插件重启、全量回归和最终验收。

CodeM 负责边界清楚、可以独立验收的实现包：

- DSH 客户端最小控制界面。
- 训练运行目录和状态展示组件。
- 测试夹具、失败注入案例和回归测试。
- 控制面文档与操作说明。
- 对 Codex 核心实现进行只读复核并提出补丁建议。

### 10.2 文件所有权原则

- 同一时间一个文件只能有一个实施者。
- CodeM 不修改 Codex 正在编辑的核心文件。
- Codex 不直接覆盖 CodeM 尚未交付的文件。
- 共享接口先写 schema 和测试，再分别实现。
- CodeM 不直接发布、不重启 DSH、不修改活动 release 指针。

建议所有协作任务登记到：

```text
team/ptc/native-control-plane/WORKBOARD.md
```

每项任务记录：

- taskId
- owner
- 状态
- 输入文件
- 允许修改文件
- 禁止修改文件
- 验收命令
- 结果路径
- 是否已被 Codex 集成

### 10.3 第一批适合交给 CodeM 的任务

1. `CM-001`：调查 DSH client slot 最小插件结构，输出不改代码的实现说明。
2. `CM-002`：建立控制面客户端骨架，只实现只读状态卡片。
3. `CM-003`：为训练/正式目录边界编写测试矩阵和失败用例。
4. `CM-004`：为 Release Bundle manifest 编写 JSON Schema 和验证测试。

Codex 同期完成运行身份、服务端状态模型和边界守卫。双方通过已冻结的 schema 对接，减少同文件冲突。

### 10.4 协作验收规则

- CodeM 每个任务只交付指定文件和一份结果报告。
- Codex 独立运行验收命令，不直接相信“已完成”描述。
- CodeM 产物未通过验收时不进入 DSH 启动配置。
- 所有 DSH 插件重启由 Codex 统一执行正式安全闸门。
- 发布按钮和活动 release 指针只由最终集成后的控制面管理。

### 10.5 CodeM CLI 调度协议

本机已确认安装 CodeM CLI，支持：

- `-p/--prompt` 非交互执行任务。
- `--session <id>` 为每项任务建立稳定会话。
- `--resume <id>` 或重复使用同一 `--session` 继续原任务。
- `--sandbox workspace-write` 限制写入工作区。
- `--approval-policy never` 避免后台任务等待交互确认；超出允许范围的动作直接拒绝。
- `--intelligence xhigh` 是本项目所有 CodeM 开发任务的固定智能强度。
- `codem sessions` 查询工作区会话。
- `codem bg` 查询 CodeM 后台任务。

标准调用模板：

```powershell
codem -p "<任务书>" `
  --session ptc-<taskId> `
  --sandbox workspace-write `
  --approval-policy never `
  --no-memory-update `
  --verbose
```

不使用 `--yolo`。每份任务书必须明确：

- 任务目标。
- 只允许读取的上下文。
- 允许修改的文件或目录。
- 明确禁止修改的文件。
- 必须执行的测试。
- 结果报告路径。
- 遇到不确定项时停止并在报告中提问，不自行扩大范围。

Codex 的并行工作流程：

1. Codex 先冻结接口、文件所有权和验收命令。
2. 启动 CodeM 非交互任务并取得终端作业指针与 CodeM session id。
3. CodeM 在限定目录工作时，Codex 同时实现不重叠的核心模块。
4. Codex 非阻塞读取 CodeM 日志和结果报告，不等待它完成才处理用户消息。
5. CodeM 完成后，Codex检查实际文件差异并独立重跑测试。
6. 只有通过复核的产物才进入集成和 DSH 重启流程。

首轮只并行运行一个 CodeM 写任务；确认文件所有权和回收机制稳定后，最多同时运行两个互不重叠的 CodeM 任务。
