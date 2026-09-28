# ATE Trainer 原型交互验收记录（2026-09-28）

本记录对应已确认的 Agent Trainer 原型交互和验收顺序。页面通过本地预览服务打开：
`http://127.0.0.1:8123/agent-trainer-repair-prototype.html`。

这份记录只证明按钮、状态和只读边界按原型验收标准可操作；SMOKE_ONLY 的真实八专家执行和 BUSINESS_ONLY 的 TM109 业务证据仍以控制面测试与 Training_Materials 运行证据为准，静态原型不会冒充真实业务执行。

## computer use 点击结果

1. 在训练模式点击“新建 Agent”。左侧 Agent 数量由 2 变为 3，出现“新建 Agent 1”，详情显示 `custom-1`、`draft`、`1+2等于几，把答案写在JSON里` 和 `{"answer":3}`。
2. 点击“新建工作流”。左侧工作流数量由 1 变为 2，并选中“新工作流 1”；页面显示空步骤和“加入当前 Agent”入口。
3. 点击“加入当前 Agent”加入新建 Agent；再选择“DFT 专家”并加入；再选择“原理图专家”并加入。
4. 点击步骤上移按钮两次，页面顺序确认是：`原理图专家 → 新建 Agent 1 → DFT 专家`。
5. 点击“运行 SMOKE_ONLY”，等待完成后页面显示 `run-20260928-003`、`scope: framework-smoke · completed · businessGatePassed: false`；记录包含 8 个 registry slot 和 Evolution auxiliary，每个 fresh child 均为 `answer: 3`。
6. 点击“打开当前专家原生会话”，页面显示已绑定当前 DFT 专家、当前 runId 和 candidate revision，会话输入区可见。
7. 点击“BUSINESS_ONLY”，页面合同切换为 `project_config.json` 门禁、原理图机器交接包、DFT 串行消费和 Training_Materials 哈希证据；点击“运行 BUSINESS_ONLY”后显示 `run-20260928-004`、`scope: business-training · completed`，三步状态依次为原理图、新建 Agent、DFT。
8. 点击“SMOKE_ONLY”后点击“冻结候选”，状态栏显示“候选已冻结；切换发布模式审核 SHA-256 依赖”。
9. 点击“发布模式”，发布按钮解锁；点击“发布 SMOKE 快照”，页面自动进入工程模式，顶部显示“已发布 1 个工作流 / 3 个 Agent”。
10. 工程模式页面验证：只显示已发布工作流及其三个绑定 Agent；步骤排序、删除、加入、保存和冻结按钮均为禁用；点击“运行已发布版本”后显示 `run-20260928-005`、`scope: framework-smoke · completed · businessGatePassed: false`。
11. 在独立页面点击“查看空项目状态”，列表变为 0 Agent、0 工作流；再点击“工程模式”，页面显示“工程模式没有可用的已发布工作流”，运行记录区域显示没有已发布工作流或 Agent。

## 结论

- 原型交互验收：通过。
- 三 Agent 工作流顺序与 SMOKE_ONLY 页面状态：通过。
- 训练、发布、工程只读边界：通过。
- 空 registry 的工程不可用状态：通过。
- 本记录不把原型演示结果当作 TM109 真实业务通过证据；真实业务结果必须满足验证方案中的 YAML/JSON 产物、语义 review 和 SHA-256 校验表条件。


## 正式 DSH Agent Trainer computer-use 验收（3080）

正式服务重启后打开 `http://127.0.0.1:3080/`，先点击“创建并打开原生会话”，确认页面显示“已绑定 DSH 原生会话”。随后实际点击“+ 新建 Agent”，填写 `tm109-dft-copy / TM109 DFT Copy` 并点击“保存候选”；Agent 列表显示第三个 Agent。实际点击“+ 新建工作流”，填写 `tm109-replacement-flow / TM109 Copy Replacement Flow`，第 1 步选 TM109 DFT Copy，第 2 步选 Synthetic consumer，点击“保存候选”。

在“工作流配置 → 编辑步骤与输入映射”中确认 step-1 为 `tm109-dft-copy`，并将 step-2 替换为同一个独立 Agent。第一次 `tm109-dft-copy → lab-consumer` 运行 `framework-602dbdf7-3821-499c-9ee7-e9a685849861` 被输入合同正确阻断（缺少 `receivedValue`）；替换后再次点击“运行一次”，`framework-f4be7479-b94b-4df4-a715-3ba407f88159` 显示“框架验证通过”、2/2 步通过，两个步骤均为 `tm109-dft-copy`，产物为 `{}`，加载引用 SHA-256 与包 SHA-256 可见。

随后实际点击“冻结当前已保存候选”、选择同包成功运行、点击“生成自包含发布包”和“激活所选发布版本”：

- frozen version：`frozen-2a7e5645-06fd-4e88-a913-2684dc955f5d`
- release：`release-aea00034-4654-49cd-bb6c-5f376cab20e4`
- bundle SHA-256：`3eb3293caa44fc20da682288c8f319de1d553c9d3020f4fe33d5ff7b31a0d166`
- `businessGatePassed: false`，保持 SMOKE_ONLY 合同。

点击“工程模式”后页面显示“已激活版本 · 只读”，编辑和发布入口均不可修改；点击工程“运行一次”得到 `framework-3ff0355b-b03a-47c1-9718-7281de8875d2`，类型为 `FRAMEWORK_REPLAY`，终态“框架验证通过”、2/2 步通过，bundle SHA-256 与发布包一致。computer-use 截图显示正式工程模式及右侧“框架验证通过”。

结论：正式 Agent Trainer 的创建、原生会话绑定、工作流 Agent 替换、输入合同阻断、合成运行、冻结、发布和工程回放按钮验收通过；TM109 业务合同仍按 BUSINESS_ONLY 单独验收，不由本合成页面结果替代。
