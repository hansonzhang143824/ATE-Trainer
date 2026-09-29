# Agent Trainer 白色页面点击证据

页面：`http://127.0.0.1:3080/agent-trainer`

以下记录来自白色 Agent Trainer 页面实际按钮操作；每一步之后都以服务端 JSON 产物复核，没有用预写 PASS 替代点击结果。

| 步骤 | 页面操作 | 服务端证据 |
|---|---|---|
| A | 训练模式点击“新建 Agent”，创建 `agent-T1`；点击“新建工作流”创建 `workflow-T1`；运行当前单 Agent 工作流 | `Training_Materials/runs/framework-a988a655-21b4-4898-93a0-9a082198891d/framework-run.json`，`agent-T1` 输出 `{"answer":3}` |
| B | 选择 `agent-T1`，点击“打开当前专家原生会话”；发送 `2+3` 优化请求；会话面板显示 `trainer_context`、`trainer_assets`、`trainer_apply_changes`；再运行优化版本 | `Training_Materials/framework/control/requests/agent-trainer/native-session-evidence-20260929.json`；优化 run `framework-4daa41e0-09b0-42a9-9011-9d2eefaae7da` 输出 `{"answer":5}` |
| C | 将 `agent-T1` 加入 `workflow-T1` 并运行 | 同一单 Agent run，记录 workflow、step、revision 和合同校验 |
| D | 训练模式创建 `agent-T2`，点击“加入当前 Agent”，保持 `T1,T2` 并运行；服务端记录两个独立 framework step | `Training_Materials/runs/framework-282d0db2-de6a-43db-872f-833bb4ff0d78/framework-run.json`，输出 `3,5` |
| E | 再加入 `agent-T3`，运行三步工作流并检查每个实际 framework step 的完成状态和输出 | `Training_Materials/runs/framework-f75373f8-8022-4513-8cb8-0809bb593a08/framework-run.json`，输出 `3,5,7`，合同校验通过 |
| F | 点击工作流步骤的上移按钮，把顺序改成 `T3,T1,T2`，保存新候选并再次运行 | `Training_Materials/runs/framework-9ea1d10b-54e9-45d8-8425-537d4a4cefb9/framework-run.json`，新 workflow revision，输出 `7,3,5` |
| G | 点击“冻结候选”“发布 SMOKE 快照”；切换工程模式点击“运行已发布工作流”；回训练模式删除候选 `T2` 步骤；切回工程模式选中 `workflow-T1` 再次运行 | release `release-95a32837-bd2e-4929-9364-4d9c2165091d`；两次 `publish/runs/` 运行 `framework-7712...`、`framework-4ca...` 仍为 `T3,T1,T2` 和 `7,3,5` |

## 会话说明

当前 standalone localhost 页面没有 DSH 宿主注入的 `sessionServices`。因此 B 使用了明确命名空间 `white-native-*` 的离线宿主适配器，并仍通过服务端 `agent-trainer` binding、preset 校验和 Trainer tool API 完成同一授权链路；普通 DSH 会话不会被接受为优化会话。真实注入式 DSH 会话仍取决于运行页面的 DSH 宿主环境。
