# 吸收记录 #40 — Agent 定义盘点（18 个 agent 四分组结构化清单，供架构文档）

- 源文件：`sessions/40-agent-ac.md`（262 行，全文）← `~/.claude/projects/subagents/agent-acd0d3d75a06356c6.jsonl`
- 时间：2026-08-26 13:15 → 13:16（0.3MB）；用户 1 条（盘点任务）/ 助手 5 段 / 工具 24 次
- 主题：盘点 `.claude/agents/` 全部 agent 定义（名称/职责/触发/输入/输出/调用/频率）供"ATE Offline Coding 工作流架构"文档

## 盘点结论（18 个 agent，四分组）

1. **代码生成 Pipeline（主 Skill 编排）**：
   - dual-parse-agent（每次生成 TM，--A DFT+资源表/--B 仅 DFT → TestItemMeta JSON；--B resourcesInvolved 空由 relay-agent 补）
   - cbit-agent（编排器，每次进入；有定义→check 无→A 仅 P1+P4/B 完整四阶段）
   - cbit-parse/singlepoint/check/path-finder（已脚本化→gen_cbit_defines.py/gen_paths.py，规格文档）
   - cbit-path-namer（脚本化 gen_path_defines.py；仅 `_B` CH0/CH1 双通道取舍留 agent 复核；多源同 PIN 尾缀 _A/B/C 正常命名全发布）
   - relay-agent（活跃推理，每次生成 TM：cbite.SetOn + delay_ms(3)，无继电器 SetOn(-1)；A 查资源表/B 查 SCH-Connect-Map）
   - power-on/power-off-agent（已脚本化 gen_power_sequence.py，规格文档保留 R-PON/R-POFF 清单）
   - measure-agent（活跃推理，五模式 MI/MV/Toggle/Trim/AMUX-NTC → Step4 测量代码）
   - check-agent（收尾双查：P/E/T/R/V/M/H 组 60+ 项；强制脚本 verify_awg_params/verify_relay_trace/verify_material_receipt/verify_bst_sw_sequence/verify_merge_rules）
2. **独立工作流 Agent（用户触发不执行）**：compile-agent（compile.ps1，自修复≤10 次）、deploy-agent（auto_sts8300.py + input_guard.py）、testplan-agent（python-docx Word 方案）。
3. **自进化三 Agent（共享 daylog）**：rules-agent（/evolve rules→rules-registry draft）、experience-agent（/evolve exp→knowledge/experience/）、sub-function-agent（/evolve fn→库函数/shared_functions/draft）。
4. AGENT_MAP.md 组织：四 section（pipeline/独立/自进化/废弃），单一入口指向根目录工作流全景.md。

**脚本化原则**："推理→agent，固定→脚本"；仍活跃推理 = dual-parse/relay/measure/check/cbit-agent(+path-namer 复核)。

## 涉及文件

- 只读：.claude/agents/ 18 个 .md、AGENT_MAP.md、skills/（nuvolta-codegen/sch-parse）。

## 交叉引用

- #41/#42 同刻并行盘点（skills+脚本），三份合成为"工作流架构"文档素材（#43 全景会话承接）；与 #28/#39 的 AGENT_MAP 状态一致（19 文件头注已过时→实际 18）。

## 未决问题

- 无（盘点结论，供 #43 使用）。
