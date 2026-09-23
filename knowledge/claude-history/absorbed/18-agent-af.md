# 吸收记录 #18 — 现状知识盘点（subagent 只读扫描，知识分层方案 Q1 诊断落地）

- 源文件：`sessions/18-agent-af.md`（501 行，全文）← `~/.claude/projects/subagents/agent-af0624697cb9267c0.jsonl`
- 时间：2026-08-15 15:08 → 15:12（0.9MB 原始）；用户 1 条（盘点任务规格）/ 助手 11 段 / 工具 78 次（只读 Glob/Read/Grep）
- 主题：**STS8300 offline coding 项目现状知识盘点**——哪些文件存什么、哪些重复/散落、应收敛到哪（目标三注册表：rules-registry.md / references/index.md / functions-registry.md）

## 任务规格（用户原文要点）

- 严格只读；盘点 4 处：①项目知识库 `.claude\`（agents\ 18 个 / knowledge\ sources+hardware+standards+experience / skills\ / references\ / AGENT_MAP.md）②项目根目录散件（*.txt/*.md/*.py，重点列名+一句话作用）③auto-memory `memory\`（nuvola-*.md 与 STS8300-*.md 逐个列——重复重灾区）④外部库 D:\test_method\、D:\shared_functions\（仅目录结构）。
- 输出四段：A 文件清单 / B **重复清单**（六块重点：cbite/继电器闭合、上电、下电、测量/量程、命名、单位换算；≥3 处重复标 ⚠）/ C 散件清单（去向建议）/ D 收敛对照表。

## ⭐ 盘点结论（关键发现）

1. **最严重重复 = auto-memory 与 knowledge 双套副本**：`memory\nuvolta-*.md`（24 个）规则正文几乎全在 `knowledge\` 另有唯一家（rules-registry.md + hardware/relays.md + standards/units.md + standards/naming.md）；`STS8300-*.md`（10 个全章 API 提取）与 `knowledge/sources/*.md`（精简版）**成对重复**。
2. **根目录散件 = 历史主权威已大部迁移但被反向引用**：`继电器识别规范.txt`/`源表规则.txt`/`原理图解析基本规则.txt`/`常用测试要求和硬件选型-实践.txt`/`规则文件DEEPSEEK.md`（1366 行）正文已进 knowledge\，但 relays.md/schematic-parsing.md/cbit-principles.md **仍标注 txt 为权威** → 删前必须改引用。
3. **错误编号体系冲突**：根 `project_rules.md`/`Check-DEEPSEEK.md` 旧 E001~E017（2026-07-04）vs `nuvolta-common-errors.md` 新 E001~E012/E028/E029（**E008 两套含义不同**）→ 应废弃旧体系。
4. **三注册表缺两个**：rules-registry.md 已建（active/draft/retired + 强制层映射）；`references/index.md`、`functions-registry.md` **未创建**（references\ 只有 3 个裸 cpp）。
5. **收敛方向已在**（`讨论记录-知识分层方案.md`）：一条知识=一个 ID=一个正文位置，memory 只留指针，散件归档删除，脚本 RULE_COVERAGE 作机器强制层。

## 关键重复条目抽样（B 段，六块全 ⚠）

- **cbite.SetOn 排他/-1 结尾/SetOn(-1) 空操作**（E011/R-SETON/R004）：7 位置（STS8300-cbite-qtmue §2.3、relay-checklist 10/11 步、common-errors E011、framework、units.md、rules-registry R-SETON、project_rules.md）。
- **Cap2 默认闭+按 PIN 例外（FR-001/E012）**：7 位置（relay-checklist、common-errors E012、floating-source、relays.md、bus-topology §七、rules-registry FR-001、experience/relay-check.md）。
- **闭环两条件（Force-Sense+High-Low，E009）**：5 位置；**FV 上电/MV→FI=0+10UA**：6 位置；**量程≥2× 决策表**：4 位置；**AWG `_Rise/_Fall/_Hys` 命名**：6 位置；**R-LOG/R-HYS 单位换算**：各 4 位置。

## 涉及文件（盘点对象全集——本身就是一份索引）

- `.claude\agents\` 18 个（dual-parse/relay/measure/power-on/power-off/check/cbit/cbit-singlepoint/cbit-parse/cbit-check/cbit-path-finder/cbit-path-namer/compile/deploy/testplan/rules/experience/sub-function-agent）；
- `.claude\knowledge\` sources 6（acm200/fovie/fpvie/hvie/qvme/accotest-api）+ hardware 10（relays/closed-loop-model/bus-topology/schematic-parsing/test-strategy/pin-resource-map/voltage-inference/pogo/cbit-mapping/cbit-principles）+ standards 6（rules-registry/naming/units/framework/merge_rules/treg）+ experience 3（index/relay-check/project-notes）；
- 脚本族：管线 12（sch_parse.py/gen_cbit_defines.py/gen_paths.py/**gen_path_defines.py**/gen_power_sequence.py/gen_dali_meta.py/verify_relay_trace.py/verify_merge_rules.py/verify_awg_params.py/gen_ramp64.py/fast_rebuild.ps1/compile.ps1）+ 批次一次性 18（gen_tm206_425.py/gen_insert_tm403_425.py/extract_stdafx_from_transcript.py/restore_stdafx.py/DALI\gen_v8.py/phase2_singlepoint.py/gen_final.py 等）+ STS8300 UI 自动化 15（auto_sts8300.py/spy_*/click_vcproject.py 等）；
- auto-memory：nuvola-*.md 24 + STS8300-*.md 10 + 其他 5（MEMORY.md/cbit-shorted-pin-rule/sch-isolated-port-rule/self-evolving-agents/test-method-ramp-library/dali-netlist-encryption——列了 6 个）；
- 外部库：`D:\test_method\`（Test_Method.h/.cpp + gen_ramp64.py + AI.cpp + COMPONENT-STATISTIC/SCH-Connect-Map，DLP 头）；`D:\shared_functions\`（README + registry\index.md + changelog.md，**尚无 src/**——跨项目通用子函数库雏形）。

## 交叉引用

- 上游设计 = `讨论记录-知识分层方案.md`（5 问方案，本报告是其 Q1 诊断落地）；下游动作（若执行）= 建 references/index.md + functions-registry.md、memory 降级指针化、散件归档。
- 报告中的脚本族与 #15 会话产物互相印证：gen_path_defines.py（P3，13 规则）、gen_dali_meta.py（--require-all 门）都是 #15 刚建；_rename_trim_node.py/extract_stdafx_from_transcript.py/restore_stdafx.py 是 #15 事故产物。
- E008 新旧编号含义冲突点 = 归档清理时的高危陷阱（#19/#20 agent 会话可能涉及整理动作）。

## 未决问题

- 盘点后是否真的执行了收敛（references/index.md、functions-registry.md 是否已建、散件是否归档）→ 需在后续会话（尤其 #19/#20/#43）中查证；本会话只读未动任何文件。
- 报告 A1 agents\ 表与 AGENT_MAP.md 的 19 文件索引差异（报告列 18 个）——后续 agent 增删以 AGENT_MAP 为准。
