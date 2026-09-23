# 吸收记录 #9 — Cap 稳压电容全局规则重构（FR-001：Cap 默认闭 + 按 PIN 例外）

- 源文件：`sessions/09-agent-ae.md` ← `~/.claude/projects/subagents/agent-aefb9a28762a4beec.jsonl`
- 时间：2026-08-10 06:35→06:36（0.1MB）；subagent 扮演 rules-agent
- 主题：规则重构沉淀——Cap 稳压电容从"MI 惯例不闭"（错误框架）改为"**Cap 默认闭 + 按 PIN 例外**"

## ⭐ 通用原则（FR-001，所有 STS8300 项目适用，2026-08-10 用户纠正）

**Cap 稳压电容默认闭**：PIN 加电就需要其 Cap 稳压。仅两种情况**按 PIN** 移除该 PIN 的 Cap：
① 该 PIN **被测电流**（电流流经 Cap 会被吃掉/掩盖真实 Iq）
② 该 PIN 是 **ramp/扫描电压源**（Cap 拖慢/扭曲 ramp）

⚠ **禁止按函数豁免**（"函数里有 MIRET → 整函数不闭"是反模式，曾致 10 函数漏闭）。
**反向检查**：PIN 被 FV 静态供电（非测该 PIN 电流/非 ramp/非下电段）未闭其 Cap → 缺陷(WARN)。
测试垫偏置（AMUX/VDM/NTC）非供电轨 → 不查 Cap（防误报）。
实例（仅 DALI，佐证）：14 处修复补 K13_VBAT_Cap / K5_VBUS_Cap。

## 落地动作

- rules-registry.md FR-001 行微调 1 处：反向检查子句补排除条件（"非测该 PIN 电流/非 ramp 扫描源/非下电段"），其余已达标未改（通用原则、不绑 DALI 继电器名、适用范围所有项目、生效 2026-08-10、来源"用户纠正"）。
- daylog 2026-08-10.md 无需修改（六类提炼已标 global rule + DALI 14 处为实例）。

## 交叉引用

- 与 #2/#5 的 K13_VBAT_Cap 待确认项相关（本规则重构解决了该分类语义）；与 verify_relay_trace.py 的 Cap 检查（FR-001）联动。
- "按函数豁免是反模式"的经验教训对后续所有 Cap 判定代码生效。
