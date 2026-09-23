# ATE AgentTeams（项目本地层）

本目录不是另一个插件，而是已安装的 `@nanmicoder/dsh-agent-teams` 的项目本地团队配置、角色知识、交付契约和验收资产。DSH 仍把工作区设为 `D:\Newtest\DSH\ATE-Coding-Plat`；团队状态由插件写入工作区 `.agent-teams\`，可随工作区继续使用。

**稳定分工与原有规则的归属入口：[`team/ROLE_ROUTING.md`](ROLE_ROUTING.md)。** Captain 和各专家须先按此文件确认当前决策 owner、只读取该角色匹配的旧规则，再读自己的角色手册。旧 `skills/AGENT_MAP.md` / `skills/nuvolta-codegen.md` 仅作为旧流水线索引，不取代本团队的任务分工。

长期目标、实施阶段、当前状态、证据和恢复入口统一记录在 `team/EXECUTION_PLAN.md`。Captain 与所有专家在每次新任务、上下文压缩或冷启动后必须先读该文件；每个可验证里程碑完成后必须更新其状态表和变更日志。

## 隔离边界

- ATE 工作区：`D:\Newtest\DSH\ATE-Coding-Plat`
- 唯一允许修改和编译的 VS 副本：`D:\PROJECT6-DALI\ForCodexDebug`
- 原工程 `D:\PROJECT6-DALI\devel`：只读，不允许发布或覆盖
- 受 TSZ/DLP 保护的源码必须通过当前已有的 Python 明文字节读写链路处理；写入前备份并在写入后复读校验。

## 启动

```powershell
cd D:\Newtest\DSH\ATE-Coding-Plat
powershell -ExecutionPolicy Bypass -File .\team\start-ate-dsh.ps1
```

启动后发送：

```text
/agent-teams --profile ate-delivery 按 team/acceptance/acceptance-plan.json 跑通 DALI 真实生产闭环；所有代码只写 D:/PROJECT6-DALI/ForCodexDebug。
```

`dsh-agent-teams 0.1.14` 会先生成可编辑的成员阵容和任务 DAG。检查路径、成员和依赖后，再点击“确认并启动团队”。同一工作区不要同时启动两个会修改同一个 `.agent-teams` 状态目录的 DSH 进程。

## Captain 必须使用的 DAG 规则

1. `dft-expert` 与 `schematic-expert` 并行，分别产出 DFT IR 和原理图 IR。
2. `setup-architect` 可读取两份 IR，产出全局 Setup 契约；不得写测试函数。
3. `test-strategy-architect` 读取 IR、Setup 契约、meta 与匹配的黄金案例，确定逐 TM 的仪器资源分配、参数架构、明确的上电/测量/下电步骤、寄存器依据与日志字段；不写具体机台 API。TM600 的 BST/PMID 阶梯由此角色结合黄金案例规划，DFT 只给测试意图，Setup 给可用通路与安全约束。完整交接检查见 `ROLE_ROUTING.md` §3。
4. `ate-implementer` 只依据已签收计划、机台手册和库函数修改 debug 工程；资源或步骤不明确时退回策略/Setup，不在代码中临时决定测试方法。
5. `rule-reviewer` 独立审查并给出可定位、可验证的 findings；不得自己悄悄改代码。
6. 有阻塞 findings 时退回 `ate-implementer` 修复，再复审；通过后交给 `compile-diagnostician`。
7. `compile-diagnostician` 运行门禁和编译；语法修复可直接完成，涉及测试意图的修改必须退回实现者。

每个任务的完整产物写入 `team/artifacts/<run-id>/`，任务消息只返回不超过 2,000 字的摘要、产物路径、哈希、阻塞项和下一任接收者。不要把大段分析仅留在聊天上下文里。

对测试策略产物，**Schema PASS 只是结构检查**；资源选择、逐阶段电气状态、寄存器来源、测量与 log、异常清理任一缺失，都不得交给实现者猜测。现有运行中的成员若已缓存旧提示词，须在新/重领任务时显式复读 `ROLE_ROUTING.md` 与对应角色手册；文档更新不自动改写已生成的计划。

## 验收

验收清单见 `acceptance/acceptance-plan.json`，分三组执行：

- 基础/低功耗：TM000、TM001、TM102、TM103
- Toggle/Trim：TM108、TM109、TM135
- 大电流/差分：TM600、TM601、TM1205

一个真实 TM 从输入解析、计划、实现、审查到编译通过，就是一条真实生产闭环；全部十项用于验证架构的泛化和稳定性，而不是重新定义“闭环”。

## 知识进化

稳定知识进入 `roles/*.md`、`standards/`、`knowledge/references/L4-Golden-code/`（实测真实黄金案例库：18 .md + 13 .cpp/.txt，原 `golden-code/` 路径不存在）或结构化案例索引；单次运行证据进入 `artifacts/<run-id>/`。只有经过编译或门禁验证、并能追溯到来源的结论，才能晋升为角色长期规则。Agent 的会话记忆是辅助，版本化知识库才是可审计的长期记忆。
