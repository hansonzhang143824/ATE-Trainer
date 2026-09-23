# DSH 启动按需 ATE 团队

## 前置条件

重启 DSH 一次，使它加载全局 web profile 中的 `ate-delivery-v2`。在 DSH 左侧选择工作区 `ATE-Coding-Plat`，点击“新会话”。

## 启动命令

将下面整段粘贴到新会话输入框并发送：

```text
/agent-teams --profile ate-delivery-v2 处理 project/DALI 的 TM108。你是唯一的 Commander/Captain。现在只创建并分派两个根任务：dft-expert 和 schematic-expert。两者必须先按 team/ptc/ATE_PTC_RUNTIME.md 的 G0/G1 输入输出复用检查执行；产物有效则回报 reuse，输入变化才解析变化范围。不得创建、启动或分派任何其他角色。两项成功或复用后，先向 Commander 写终态报告，等待 Commander 验证后再创建策略任务；失败则写错误日志并阻断下游。
```

DSH 会显示一个可审阅的团队计划。确认计划中仅有 `dft-expert` 与 `schematic-expert` 两项根任务后，点击 **Approve & Run**。

## 预期状态

- 计划审阅阶段：9 个角色只显示在 roster，不会创建成员模型会话。
- 点击 Approve & Run 后：仍然不会启动 9 个成员；仅两个已分派根任务的成员被 materialize。
- 其余 7 个角色显示 `unspawned`，直到 Commander 为其创建依赖满足的任务。
- 失败时：下游角色保持 `unspawned`，错误日志路径写入任务终态报告。
