# 吸收记录 #42 — 脚本全景盘点（按工作流环节分组：输入→输出 + 门禁/生成/编排分类）

- 源文件：`sessions/42-agent-a5.md`（291 行，全文）← `~/.claude/projects/subagents/agent-a5d7ebe517ed12cef.jsonl`
- 时间：2026-08-26 13:15 → 13:17（0.4MB）；用户 1 条（盘点任务）/ 助手 12 段 / 工具 70 次
- 主题：盘点 CLAUDE_PROCESS 全部脚本（输入→输出、归属环节、门禁/生成/编排分类）供架构文档

## 盘点结论（按环节分组）

- **公共基础**：proj_config.py（config 读取器，唯一入口 project_config.json）、project_config.json。
- **原理图解析**：csv_schematic_adapter_v2.py（CSV→合成 EDIF，唯一生产管线）、sch_parse.py（六任务门控，生成+门禁）、csv_pathproof_v2.py（PathProof 门禁）、run_hardware_parse.py（流程编排，链式 adapter→pathproof→gen_path_defines→gen_cbit_defines，--publish-definitions 发布）。
- **meta**：gen_testitems_meta.py（纯 DFT 派生 capAuthority 四集）、check_testitems_meta.py（--require-all/--require-scope 门禁）；Project/DALI/meta/ append_tm.py、check_tm.py、find_fpvi*.py（历史/工具）。
- **cbit**：gen_cbit_defines.py（P1 单点生成 + P4 V1~V8 校验）。
- **通路**：gen_paths.py（BFS path-finder 脚本化）、gen_path_defines.py（2.x 通路段 → StdAfx.h）、gen_relay_role_defines.py（列11 角色段 RELAY_ROLE）、verify_relay_trace.py（继电器轨迹核对门禁，E 权威源=meta capAuthority）。
- **上电下电**：gen_power_sequence.py（R-PON/R-POFF → POWER_ON/STATE/OFF 三段）。
- **codegen 门禁**：verify_single_fn.py（7 项冒烟）、verify_awg_params.py（E005 Toggle 3 参数）、verify_bst_sw_sequence.py（R-BST-SW 黄金约束，meta 拓扑指纹派生）、verify_material_receipt.py（材料声明门生成前拦截）、verify_merge_rules.py（M001-M004）、verify_library_status.py（TODO/桩进生产 FAIL）；verify_i2c_sv.py/verify_tm206_425.py 指向已弃用 AI.cpp。
- **编译部署**：compile.ps1、fast_rebuild.ps1、meta\dte_rebuild.ps1/dte_buildcheck.ps1/dte_read_buildlog.ps1、auto_sts8300.py/start/run/diag/click/spy_*/record/replay/input_guard.py。
- **自进化/知识审计**：**gen_knowledge_audit.py = ⏳ 待建**（仅文档提及：工作流全景.md/工作流Action清单.html/CODEX评审，A09 P2 执行顺序第 5 步，无实体文件）；库函数\test_method\gen_ramp64.py（64 ramp 函数生成）。
- **归档**：根 _archive/、Project\DALI\_archive/、schematic_parse\_archive/（历史一次性脚本）。
- 环节调用链速览：原理图解析/ meta/ cbit/ 通路/ 上电下电/ codegen门禁/ 编译部署/ 知识审计。

## 涉及文件

- 只读：全部根目录 .py/.ps1、schematic_parse/scripts/、Project\DALI 脚本、库函数\test_method\gen_ramp64.py、project_config.json。

## 交叉引用

- #40（agent）/ #41（skill）同刻并行盘点；本报告脚本清单与 #42 前后各会话产物一致（gen_relay_role_defines.py 为 #36 新建）；gen_knowledge_audit 待建贯穿 #19/#20 待办。

## 未决问题

- gen_knowledge_audit.py 仍待建（审计脚本）；verify_i2c_sv/verify_tm206_425 指向弃用 AI.cpp（可能需迁移到 test.cpp 或归档）。
