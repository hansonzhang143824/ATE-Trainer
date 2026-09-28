# ATE Trainer 开发计划（动态 Agent 能力与工作流替换，2026-09-28）

状态：D1/D2/D4/D6 已实现，D5/D7 待业务合同与工程回放验收。本计划对应[系统验证方案](agent-trainer-validation-plan-20260928.md)，保持已确认的原型页面结构和交互入口，不先重做 UI。每个阶段都有独立验证和 Git checkpoint；未通过当前阶段不得进入下一阶段。

## 1. 开发目标

把当前固定专家执行器改成按 Agent 配置执行，使以下行为成立：

- 新建 Agent 与已有 Agent 是同一种实体，有独立 ID、revision、session、运行证据和发布快照。
- Agent 的职责、内部流程、Skill、脚本、输入输出合同、依赖、权限和执行适配器由配置决定。
- 复制 DFT Agent 可以生成独立的新 Agent；新 Agent 可以替换工作流中的 DFT 步骤。
- DFT 业务执行不再通过 `profileId === 'ptc-dft-expert'` 放行，而是通过声明的 capability/executionAdapter 执行。
- 首个三 Agent smoke 工作流验证动态新增 Agent；TM109 真实业务工作流验证原理图 → DFT 的实际交接和产物。

## 2. 不变的边界

- 当前原型的产品模式、主导航、Agent/工作流列表、运行记录页签、原生会话入口和工程只读行为保持不变。
- active `SMOKE_ONLY` 仍严格使用八专家 registry 顺序、精确 `1+2等于几，把答案写在JSON里`、fresh child、无工具/私有材料、数字 `answer:3` 和 `businessGatePassed:false`。
- 新增 Agent 的动态替换能力主要用于用户候选工作流和 `BUSINESS_ONLY`，不改写 active 八阶段 registry。
- TM109 真实业务证据写入 `Training_Materials/runs/<runId>/`；SMOKE 发布和工程回放继续写 `publish/versions/<releaseId>/`、`publish/runs/<runId>/`。
- 不恢复 legacy archive 中的旧 smoke gate、parser、business gate 或 compile 业务路径。

## 3. 分阶段开发与 checkpoint

### D0：基线与契约冻结

**变更**：保存当前原型、计划、registry、现有 Agent profile 和发布边界的摘要；定义 Agent manifest、workflow step、revision 和 run evidence 的字段。

**验收**：原型关键入口不变；现有 SMOKE_ONLY 规则仍能被静态检查发现；新字段有 schema 和兼容策略。

**Git checkpoint**：只提交计划、schema 和基线清单，提交信息 `docs: freeze agent trainer validation baseline`。

### D1：配置驱动的 Agent 模型

**变更**：新增统一 Agent manifest，至少包含 `agentId`、`revision`、`capabilities`、`executionAdapter`、指令引用、Skill/脚本引用、输入输出合同、依赖和权限。执行器、Trainer session 和运行证据都读取 manifest。

**验收**：原理图、DFT 和 `custom-agent-01` 都能通过同一套 profile resolver 创建 run；resolver 不使用固定 Agent ID 白名单决定能力；旧八专家 smoke 的 registry 映射保持不变。

**Git checkpoint**：只提交 manifest/schema/resolver 和测试，提交信息 `feat: make agent execution configuration driven`。

### D2：Agent 优化候选闭环

**变更**：通过现有 Trainer 原生会话入口保存 candidate revision，增加 `agent-optimization` run kind 和变更摘要；不新增顶层页面。

**验收**：v1 用 `1+2 → 3`；v2 修改可执行内容后用 `2+3 → 5`；v2 证据独立，v1 不变；声明通用算术能力时追加 `1+2 → 3` 回归。

**Git checkpoint**：提交 candidate revision、run evidence 和回归测试，提交信息 `feat: add agent optimization candidate runs`。

### D3：去除 DFT 固定 ID 判断

**变更**：重构 `training-execution.js`、business handler 和相关 dispatcher：从 run 绑定的 Agent snapshot 读取 `executionAdapter: 'ptc-dft'` 和能力合同；只有 manifest 能力、输入合同、依赖和权限满足时才允许 DFT 执行。

**验收**：原 `ptc-dft-expert` 和复制出的新 Agent 都能进入同一 DFT adapter；未知 adapter、缺失能力、合同不兼容或越权依赖明确阻断；代码中不再以 `ptc-dft-expert` 作为唯一业务执行资格。

**Git checkpoint**：提交执行器重构、兼容测试和固定 ID 删除记录，提交信息 `refactor: resolve business execution by agent capability`。

### D4：复制 Agent 与工作流替换

**变更**：增加“复制为新 Agent”的后端能力，复制完整 DFT 配置但保留独立 ID、revision、训练草稿、运行目录和发布快照；工作流 step 改为绑定 `agentId + agentRevision`，替换前执行合同/能力/依赖兼容检查。

**验收**：复制 DFT 为 `custom-dft-agent`；两者使用同一 DFT adapter 和相同能力配置；把工作流 DFT step 替换为 `custom-dft-agent` 后可以运行；修改复制 Agent 不改变原 DFT。

**Git checkpoint**：提交 clone、replacement、深度隔离和兼容校验测试，提交信息 `feat: support independent agent clone and workflow replacement`。

### D5：TM109 业务产物合同

**变更**：为 TM109 的 BUSINESS_ONLY 运行固定输入、上游交接和输出合同；保存：

- `dft-conditions.yaml`
- `dft-meta.json`
- `dft-semantic-review.json`
- `evidence/tm109-output-hashes.json`

哈希表记录每个文件的 role、path、bytes、SHA-256、来源输入 hash、Agent revision 和验证状态。生产执行器按 Agent adapter 读取合同，不按固定 DFT ID 分支。

**验收**：原理图单体和 DFT 单体分别可通过或明确阻断；TM109 工作流消费本次原理图产物；缺文件、解析失败、hash 不匹配、semantic review 非 PASS 时停止。

**Git checkpoint**：提交 TM109 contract/schema、receipt/hash record 和测试，提交信息 `feat: add TM109 business output contract`。

### D6：三 Agent smoke 工作流

**变更**：使用现有原型的 Agent/工作流入口创建 `custom-agent-01`，编排 `原理图 → custom-agent-01 → DFT`；不新增复杂页面。

**验收**：三个 Agent 各自 fresh child、无工具、精确 1+2 JSON；顺序、三份 receipt、上游 hash 和失败停止均正确；该 smoke 不生成 TM109 业务产物。

**Git checkpoint**：提交动态工作流编排与 smoke tests，提交信息 `feat: validate dynamic three-agent workflow smoke`。

### D7：发布、工程回放与最终回归

**变更**：把通过的轻量 smoke workflow 冻结到 `publish/versions/<releaseId>/`，工程运行写 `publish/runs/<runId>/`；保留旧发布版本并接入草稿变更回归。

**验收**：工程只能读取已发布 workflow/Agent；训练草稿变化不改变旧 release digest、绑定和顺序；篡改快照或证据时启动前阻断；SMOKE_ONLY 不被 BUSINESS_ONLY 产物替代。

**Git checkpoint**：提交发布/工程回归测试和最终验收报告，提交信息 `test: verify agent trainer release and engineering replay`。

## 4. 每个阶段的回滚规则

- 每个 checkpoint 只包含该阶段的代码、schema、测试、计划和必要的证据索引；禁止提交现有无关训练运行、业务材料和临时文件。
- 阶段失败时回滚到最近一个通过 checkpoint；不在失败状态继续叠加下一阶段。
- 原型文件只有在确实需要增加状态提示时才修改，且必须先保存视觉基线和交互入口清单。
- 任何生产按钮接线必须同时提供对应测试和 run evidence；静态原型可点击不能替代后端验收。

## 5. 当前 Git 交付状态

本计划要求每个阶段提交并推送 Git。当前仓库分支为 `master`，remote 已配置为公司 GitLab：`https://gitlab.nuvoltatech.com.cn/NVT10241/ate-trainer.git`。普通执行环境对 `.git` 有显式拒绝写入的 ACL，提升后的受控执行可以完成选择性暂存和本地提交；工作区其他修改仍未纳入 checkpoint。按 D0–D7 顺序逐阶段提交，不能一次性混合提交。

## 6. Git 记录操作

恢复 Git 权限和 remote 后，后续每个阶段按同一流程执行：

```text
1. 确认当前分支和上一个 checkpoint commit。
2. 只把本阶段列出的文件加入暂存区；禁止 git add -A。
3. 运行针对本阶段的测试、静态检查和 git diff --cached --check。
4. 提交一个独立 commit，记录阶段编号和目的。
5. 记录 commit SHA、测试命令和结果到本计划或阶段报告。
6. push 到指定 remote；push 成功后记录远程分支和 commit SHA。
```

建议使用分支 `codex/agent-trainer-dynamic`，阶段提交信息固定为 D0–D7 对应的 checkpoint message。每个提交都必须能单独回滚和重放；不得把训练运行目录、业务材料、临时预览文件或其他已有脏修改混入提交。

如果任一步骤因权限、remote、测试或审查失败：保留前一个已通过 checkpoint，记录 `blocked` 原因和失败命令，不进入下一阶段，也不报告“已上传”。

### 当前 D0 checkpoint 状态

2026-09-28 已只提交三份计划文档，缓存区空白检查通过：

```text
1b82a08 docs: record Agent Trainer validation and development plans
```

此前的 `329d2d6 test: verify GitLab upload` 只是上传链路探针，只包含
`GIT_UPLOAD_TEST_20260928.txt`，远端分支为 `codex/git-upload-test`，不能视为 D0。
当前 D0 已有本地 SHA，但尚未声称已上传：无凭据的 `git push --dry-run` 返回
`could not read Username`；普通环境的代理 `127.0.0.1:9` 也会阻断 HTTPS。
实际上传需要在网络可达的环境中使用新的 GitLab `write_repository` PAT，上传后再把
远程分支和 SHA 补记到本节。工作区其余修改和未跟踪文件仍保持原状。

### 已完成实现 checkpoint

- `b813127 feat: add dynamic Agent profile runtime`：实现配置驱动 profile resolver、独立 clone、revision manifest/pointer、动态 profile 的训练材料与 DFT capability 绑定、SMOKE API 和训练边界校验。
- `0ef2f15 feat: support dynamic Agent workflow replacement`：实现候选工作流替换、Agent revision/content/manifest 摘要绑定、发布阶段复核和工程回放固定版本；没有 active 发布版本时工程回放在派发前拒绝。
- 相关定向回归：Agent runtime、训练 guard/dispatch、workflow replacement 共 63 项通过；JavaScript `node --check` 通过。最终完整回归 `npm test`：357/357 通过。
