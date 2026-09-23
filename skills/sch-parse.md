---
name: sch-parse
description: 原理图 Netlist 解析 — 六任务门控流程，输出 Component-Statistic 与 SCH-Connect-Map.txt（通用，任何项目可用）
---

# 原理图解析 Skill（薄指针）

> 本 skill 的正文已收敛到通用「原理图解析」环节文件夹，任何项目共用、不随项目变化。
> 触发：用户提供 .NET Netlist / Dali-SCH.csv，要求「解析原理图」「提取 PIN 继电器」「生成连接图」。

## 权威正文

| 文件 | 内容 |
|------|------|
| `schematic_parse/SKILL.md` | 运行入口（四脚本流水线）、状态机、输入输出 |
| `schematic_parse/VALIDATION_RULES.md` | 25 列契约、DLP 拒收、图构建规则、六门控 |
| `schematic_parse/NET_SHORT_RULES.md` | net 短接判定（ELECTRICAL_SHORT_GROUP/NetTie/0Ω/Jumper/Relay 优先级 + 输出格式） |
| `schematic_parse/KELVIN_RULES.md` / `OUTPUT_RULES.md` / `PATH_CONTRACT.md` / `RELAY_CONTROL_RULES.md` / `SOURCE_POLICY.yaml` | 具体规则 |
| `knowledge/hardware/schematic-parsing.md` | 深知识（功能分类、通路、11 列结构、Rule A/B） |

## 位置约定（2026-08-25 重组）

- **脚本**（通用，任何项目共用）：`schematic_parse/scripts/` — `csv_schematic_adapter_v2.py`、`csv_pathproof_v2.py`、`sch_parse.py`、`run_hardware_parse.py`
- **项目数据**（每项目不同，留项目目录）：`Project/DALI/` — `Dali-SCH.csv`、`sch_confirmed.json`、`CSV_CONNECTIVITY.NET`、`SCH-Connect-Map.txt`、`Component-Statistic.txt`
- **入口**：`python schematic_parse/scripts/run_hardware_parse.py [--publish-definitions]`

## 铁律（摘要，全文见 schematic_parse/SKILL.md 与 knowledge/hardware/schematic-parsing.md）

1. 六任务门控串行，任一 FAIL 即停，禁止带病继续。
2. 功能分类用三层动态判断，禁止编号硬编码 BUS/Share。
3. 孤立 PORT / TP 短接必报，不猜不假设；短接关系从 net 文件自动推导，例外登记项目 `sch_confirmed.json`。
4. 项目短接关系禁止硬编码进解析脚本（脚本是通用的）。
