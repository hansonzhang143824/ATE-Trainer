# PTC 链路回归问题清单（系统 ready 之后）

> 来源：批次 `dali-20260921-080849`（TM106/TM108/TM425）真实回归观察 + 8 角色合同审查。
> 用户要求：只收录 **agent 执行流程问题** 与 **agent 间产物合同/schema 问题**；环境/平台问题（key、profile 挂载等）已解决，不在本清单。
> 时间线：08:08 建档 → 08:18/08:25 源专家完成 → 08:25–09:58 Captain 死等 → 09:58 唤醒 → 10:12 dft-refresh 返工 → 10:58 完成 → 11:03 STRATEGY → 11:25 METHOD 派发 → 此后转空壳模式推进 COMPILE。

## A 类：agent 执行流程问题

| # | 问题 | 证据 | 影响 | 建议 |
|---|------|------|------|------|
| A1 | **子代理完成后 Captain 不会被自动唤醒**。子代理结果 splice 进主会话 inbox，但 DSH 机制要求下一轮用户消息才触发消费，Captain 派发完就静默。 | 08:25 两位源专家完成 → 主会话停写 93 分钟，直到人工发消息；此后每个阶段转换同样需外部驱动 | 每阶段转换空转 3~93 分钟，是总时长一半以上的来源 | material-boundary 插件在子代理 `turn/end` 后自动注入推进消息（事件驱动），替代外部唤醒 |
| A2 | **批次启动无输入材料完备性预检**。dft 首跑完成后 Captain 才发现材料缺失，追加派发 dft-refresh-1，多花 45 分钟。 | 10:12 派发 `dft-expert-...-refresh-1.json` 回执；refresh 会话跑 refresh_dft_meta_from_source.py 到 10:58 | 一次可预见的返工；3 TM 批次放大为 45 分钟 | captain-entry 建档时先跑 input-manifest 完备性校验，缺料在首派发前补齐 |
| A3 | **trial 目录与 profile.writable 边界矛盾**。批次 trialDirs 指向 `team/artifacts/<batch>/<tm>`，但 dft profile.writable 只有 `Output_Global_Material/dft/<TM>`，专家写 trial 目录被 material boundary 拒，产物实际落在 Output_Global_Material；trial 目录里只有 input-manifest.json。 | dft 子代理回执自述"trial 目录被 host boundary 拒"；tm106/ 下仅 input-manifest.json | 下游按 trialDirs 找 dft 产物会落空；批次产物分散两处 | trialDirs 与 profile.writable 对齐，或合同 x-artifacts 明确两类落点及引用规则 |
| A4 | **批次状态可观测性差（多源拼图 + 滞后）**。判断真实进度需拼 batch json（initialSourceDispatchPending）、advance-handoff.json（state 滞后：receipts 已到 METHOD 时仍显示 INPUT_SYNC）、dispatch-receipts 计数、trial 目录内容四个源。 | 11:25 实测：handoff state=INPUT_SYNC 而 method-expert 回执已落盘 | 驱动方/监控无法从单一权威文件读出阶段 | 单一 authoritative 状态文件（state + 每 TM 子状态），带 schema |
| A5 | **handoff/batch JSON 带 UTF-8 BOM**。Node `fs.readFileSync` 不认 `utf-8-sig` 编码，消费方必须手动剥 BOM；本次 autopilot 因此状态读取失败静默降级为 `?`。 | autopilot 首版日志连续 `state=?`；`advance-handoff.json` 文件头 `EF BB BF` | 任何 Node 工具链消费批次状态都会踩坑 | 产出侧（Captain run_code 写 JSON 时）用 `json.dumps(..., ensure_ascii=False)` 无 BOM 写出 |
| A6 | **串行单链，无 TM 级并行**。8 阶段顺序执行、每阶段单专家实例串行处理全部 TM。 | strategy 16 步 25 分钟、refresh 45 分钟、全程 3 小时+ 才到 METHOD | 时长随 TM 数 × 阶段数线性放大 | 编排层支持 TM 级并行派发（同角色多实例）或按 TM 拆批次 |
| A7 | **模型单步推理慢**。glm-5.3-flash 每步 ~1.5 分钟（strategy 16 步 25 分钟，reasoning-chunks 3414）。 | 子代理会话日志统计 | IMPLEMENTATION 等重阶段会进一步放大 | 按 PTC 初衷（run_code 批处理减少轮次）收紧每阶段步数预算；或为重阶段配快模型 |
| A8 | **headless 单轮模式不能承载多阶段流程**。`dsh headless` 一问一答即退出，Captain 的"自动推进"话术落空（批次 002137 仅建档、无 trial 目录）。 | 批次 dali-20260921-002137 `initialSourceDispatchPending: true` 永久滞留 | 生产/回归驱动必须 web 会话 + 外部 API 驱动，该约束未写入任何文档 | 文档明确；或 ptcflow 提供 headless-loop 模式 |

## B 类：agent 间产物合同/schema 问题

| # | 问题 | 证据 | 影响 | 建议 |
|---|------|------|------|------|
| B1 | **合同强度不均：源头严、末端松**。dft 要求 testCondition 18 必填子字段，schematic 要求 6 产物名→sha256；而 implementer 的 `changes[]` 除 SHA 外无结构约束，compile 合同直接装原始 stdout 大字段。 | 各角色 output-contract.schema.json 对比 | 末端交接质量无机器约束，返工风险集中在下游 | 末端合同对齐源头强度（changes[] 每项必填字段集、compile 输出结构化） |
| B2 | **dft x-semantic-review 的 `verdict: "PASS"` 无验证力且无 FAIL/PENDING 表达**。该键位于 x- 扩展平级，是注解不是 JSON Schema 约束；且领域现实存在"语义预期值缺失"（TM106 首批遗留 PENDING_DOMAIN_INPUT），PASS-only 合同无法表达。 | dft schema 第 27–32 行；F051 遗留项 | 缺输入的 TM 无法按合同交接，只能走合同外通道 | verdict 进 properties + enum [PASS, FAIL, PENDING_INPUT]，并定义 PENDING 下游行为 |
| B3 | **rule-reviewer 一人双审**。RULE_REVIEW_METHOD 与 RULE_REVIEW_IMPLEMENTATION 同一角色同一 preset，等于自己定的规则自己审下游。 | rule-reviewer profile.yaml 注释自述双阶段路由 | 审查独立性缺失 | 拆两个 reviewer preset 或交叉审查 |
| B4 | **implementer 合同缺 trimCompliance 条件必填**。OUTPUT_CONTRACTS.md 描述 Trim 项必须含 trimCompliance（三个文件的 SHA + PASS 记录），但 implementer schema 的 required 无此字段（if-Trim-then-required 未落 schema）。 | OUTPUT_CONTRACTS.md Trim 段 vs implementer schema | 文档与 schema 漂移实例：gate 会对 Trim 拒收，但合同声明层看不出要求 | schema 补 if/then 条件必填 |
| B5 | **合同三源无一致性锁定**。OUTPUT_CONTRACTS.md（人读）+ output-contract.schema.json（机器）+ gate 脚本（实际执行）三源维护；dft/schematic schema 的 description 声称"mirrors validate 脚本"，但无自动测试锁定一致。 | dft/schematic schema description | 漂移必然发生（B4 已是实例） | 以 schema 为单一来源：CI 测试断言 gate 校验字段集 == schema required 集，文档从 schema 生成 |
| B6 | **schematic TM-less 与 dft per-TM 粒度不一致**。schematic 整批一套产物（无 per-TM 目录），dft 按 TM 分目录；下游按 TM 消费时两类来源引用方式不同。 | schematic profile.yaml 注释"TM-less on purpose" | 下游合同（strategy/method）需同时处理两种粒度，复杂度外泄 | 统一粒度，或下游合同显式定义两类来源的引用规则 |
| B7 | **编排层交接文件无 schema**。advance-handoff.json、批次 json、dispatch-receipt 均无合同定义；外部驱动方（本次回归的 autopilot）只能靠猜字段（state/dispatches/waitingTms）。 | autopilot 开发过程 | "Captain↔驱动方"这一层交接完全没有合同，正是用户要定义的交接文档盲区 | handoff/receipt 落 schema 纳入 team/ptc/ 合同体系 |
| B8 | **trial 目录 input-manifest.json 无合同**。批次在 trial 目录生成的 input-manifest.json 不在任何角色 output-contract 的 x-artifacts 列表里，字段结构未定义。 | tm106/ 下仅此文件 | 输入交接层（批次→专家）的产物无约束 | 归入编排层合同（与 B7 一并定义） |

## 已验证可用的部分（不构成问题）

- web API 驱动方案可行：`POST /api/session.create` / `session.prompt`（mode=queue）+ events.mux 事件流。
- pinned dispatch + 回执持久化真实工作（identity 来自回执而非显示名）。
- material boundary 读写拦截真实工作（dft 写 trial 目录被拒即为证据）。
- INPUT_SYNC→STRATEGY→METHOD 派发链真实走通（5 张回执）。

## 附：驱动侧事实（供复现）

- Captain 会话：`session-f7af44ee-5e8d-4743-be0d-2327fc4432d3`（web, agentPreset=ate-ptc）。
- 自动驾驶：scratchpad/autopilot.mjs（静默 60s 唤醒，COMPILE/COMPLETE 退出）。
- 会话日志：`~/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/<id>/session.jsonl.zstd`（多帧 zstd，用 decompress_arg.js 解）。
