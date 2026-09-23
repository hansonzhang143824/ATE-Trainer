# 吸收记录 #41 — Skill 与 codegen pipeline 结构盘点（执行频率/循环表述逐字摘录，供架构文档）

- 源文件：`sessions/41-agent-a1.md`（293 行，全文）← `~/.claude/projects/subagents/agent-a16ad084268ba0dc5.jsonl`
- 时间：2026-08-26 13:15 → 13:16（0.3MB）；用户 1 条（盘点任务）/ 助手 4 段 / 工具 12 次
- 主题：盘点 skill 文件 + nuvolta-codegen.md pipeline 结构，重点逐字摘录"执行频率与循环关系"表述

## 盘点结论

1. **Skill 全工作区仅 3 处**：`.claude/skills/nuvolta-codegen.md`（核心 42.6KB）、`.claude/skills/sch-parse.md`（薄指针 2KB→schematic_parse/）、`schematic_parse/SKILL.md`（解析流水线正文 4.4KB）。
2. **主 pipeline**：Step0 入口分流（有资源表→A/无→B）→ Step1A dual-parse--A / Step1B sch-parse→Pin_Channel_define→dual-parse--B → Step2 cbit 公共前置（无定义→创建 A 仅 P1+P4/B 四阶段；有→仅 check）→ Step3 按 testType 选模板（普通 6 段注释/Toggle Rise-Fall-Hys/Trim 9 后缀）→ Step4 共用生成循环（0 材料门→1 relay-agent→2 pin-map→3 gen_power_sequence 三段 SECTION→4 模板 entertestmode→5 measure-agent→6 LogData→7 单函数冒烟→8 最后一项?）→ Step5 收尾双查（check-agent + gen_cbit --verify + verify_awg_params E005 + meta 全覆盖门）。
3. ⭐ **循环/频率关键句逐字摘录**（供文档引用）：单函数冒烟"FAIL 停留当前 TM 修正, 不得进下一个 TM"；meta 全覆盖门"每批测试项目收尾必做, 机械强制不靠自觉"/正向"无记录→ERROR 禁止静默跳过"/反向"isCodeGen='Y' 必须已写入, 缺任一项→FAIL 列出 TM 编号+Name"；B-001 批量纪律三条；材料门"FAIL 禁止进入 relay-agent; Current Threshold/ZCD 必须同时声明 code/HS_ZCD.cpp + code/LS_ZCD.cpp"；上下文铁律 5 条（test.cpp 禁全读/两段式写码归位单 TM 单元/StdAfx.h 禁全读/golden 走索引/黄金案例=关键结构非 PIN 字典）；脚本改动后必跑 --audit-rules（13+11+13+19）；daylog 每次收尾必写。
4. **sch-parse 解析管线**：五脚本流水线（adapter→pathproof→gen_path_defines→gen_cbit_defines→gen_relay_role_defines）+ 六门控串行任一 FAIL 即停；产物统一落 Project/DALI/。
5. **panorama.md B 路径 14 步**（5 输入源 + 一次性 1-4 + 逐项循环 5-14 + 两级分类 + 两层检验）：每步落点表格。
6. **引用汇总**：脚本 14 个、agent 18 个、knowledge/ 与 references/ 与 daylog/库函数清单。

## 涉及文件

- 只读：nuvolta-codegen.md（全读，497+ 行）、sch-parse.md、schematic_parse/SKILL.md 及规则文档、panorama.md、references 索引。

## 交叉引用

- #40（agent 盘点）/ #42（脚本盘点）同刻并行；#39 同源步骤梳理；本报告与 #40/#42 共同构成 #43 全景架构文档的素材基础。

## 未决问题

- 无（盘点结论）。
