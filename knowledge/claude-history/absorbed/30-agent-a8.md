# 吸收记录 #30 — codex 5 reviewer agent + 材料门实质评估（subagent 只读）

- 源文件：`sessions/30-agent-a8.md`（282 行，全文）← `~/.claude/projects/subagents/agent-a8d91b60c2e8db57d.jsonl`
- 时间：2026-08-23 15:14 → 15:16（0.2MB）；用户 1 条 / 助手 6 段 / 工具 20 次
- 主题：评估 codex 迁移产物（D:\Newtest\CODEX\_PROCESS）中「reviewer 化」和「材料门」实质，为只吸收思想（非全套替换）提供精确依据

## ⭐ 核心事实 A：5 个 reviewer agent 都不承担 relay/measure 代码生成

- 目录实际 5 个 agent（用户列 4 个缺 **workflow-orchestrator.md**）：
  - hardware-topology-reviewer：审核/证明角色（PASS/AMBIGUOUS/FAIL 三值，输出 PathProof 含有序 net/relay edges、Kelvin、证据哈希；不改外部定义文件，差异报告交外部团队）；tools 仅 Read/Grep/Bash。
  - test-design-reviewer：设计/判定角色（输出 TestItemPlan：PowerPlan/RegisterPlan/MeasurementPlan/LogPlan/waiver；"确定性代码段由生成器生成，本角色不复制粘贴模板实现"；材料冲突→AMBIGUOUS 不静默降级）；tools 仅 Read/Grep/Bash。
  - verification-build-reviewer：独立审核 + 用户触发编译（10 条最低门禁：manifest 哈希不漂移/meta 双向对应/lifecycle 有序/PathProof relays 全在 Step1/无杂散驱动/TODO 不入生产/整批只验一次/发布哈希核对/编译证据）；tools 仅 Read/Grep/Bash。
  - knowledge-curator：离线知识维护（唯一有 Edit，限知识维护；draft→人工批准→active；"不参与生产代码生成"）。
  - workflow-orchestrator：编排者（9 条职责 + G0-G5 阶段门禁：G0 Manifest 哈希冻结 / G1 Hardware PathProof / G2 Design TestItemPlan / G3 Generate+L1 Smoke verify_single_fn / G4 Batch Verify / G5 Build 用户触发；"任一门禁没有证据即为 FAIL"）。
- **代码生成发生在 skill Step 3.2「用脚本/模板生成到 staging」**，不是 agent 手写；relay 正确性由脚本验证（verify_relay_trace.py / verify_bst_sw_sequence.py）。
- skill 2.0 8 步流程（manifest 冻结→硬件基线→逐 TM 材料门+生成+单函数冒烟→代表函数先冒烟→整批独立门禁→修复回炉→原子发布→用户触发编译）；强制策略含"旧 Agent/Skill 位于 knowledge/standards/legacy-agent-specs 禁止执行"。

## ⭐ 核心事实 B：材料门 = 只有 skill 文字 + 数据索引，无配套检查脚本

- `param_type_index.md`（CODEX 版）是数据索引（Current Threshold 登记 code/HS_ZCD + code/LSZCD，标注"两份必须同时读取"+约束 BST>=SW、0<=BST-SW<=5V、目标 5V）。
- 全仓库 grep HS_ZCD|LSZCD|param_type_index|references/... 命中仅两文件且都不是材料门检查器：verify_bst_sw_sequence.py（TARGETS=(TM607_BUCK_LS_ZCD, TM608_BOOST_HS_ZCD, TM609_BOOST_HS_NEG)，校验生成后源码的 BST-SW 时序 = 约束的下游产物校验）+ adapt_tm607_609_bst_sw.py（写黄金注释字符串）。
- **"材料存在却未读取不得生成"没有机器可执行检查**；流程唯一结构锚点 = orchestrator G2（TestItemPlan 须写实际读取路径）+ G4 check_testitems_meta（只证 TM↔meta↔DFT 双向对应，不证材料被读）。→ 若要硬门禁需在生成脚本/verify_single_fn/新校验器加"TestItemPlan 声明的材料路径必须实际存在且与索引一致"。
- 可执行门禁全景：project_manifest.py(G0)/run_hardware_parse.py(G1)/verify_single_fn.py(G3,7 项)/check_testitems_meta.py/verify_relay_trace.py/verify_awg_params.py/verify_bst_sw_sequence.py/gen_cbit_defines --verify/gen_path_defines --verify/verify_merge_rules.py/verify_library_status.py(G4)/编译(G5)——**材料门不在其中**。

## 关键结论

- "reviewer 化"实质 = 把生成与审核彻底分离（生成器/模板产码，reviewer 只证明与把关）+ G0-G5 证据门禁 + 原子发布 + 哈希绑定。
- "材料门"思想要吸收成可执行机制，必须新写检查器（后来在 CLAUDE_PROCESS 侧落地为 verify_material_receipt.py，见 #31/#34）。

## 涉及文件

- 只读 CODEX _PROCESS 5 agent + skill + run_hardware_parse.py + grep。零修改。

## 交叉引用

- #28/#29 同批并行调查；#34（codex 评审主会话）消化本结论；#31 显示材料门/哈希冻结已在 CLAUDE_PROCESS 落地（verify_material_receipt.py、project_manifest.py、verify_bst_sw_sequence.py 进入收尾序列）。

## 未决问题

- 无（评估性结论，决策在 #34）。
