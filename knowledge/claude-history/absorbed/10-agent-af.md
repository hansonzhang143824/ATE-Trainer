# 吸收记录 #10 — experience-agent：Cap 修复的 4 条实现经验提炼（relay-check.md / project-notes.md）

- 源文件：`sessions/10-agent-af.md` ← `~/.claude/projects/subagents/agent-aff1e05ab747020ab.jsonl`
- 时间：2026-08-10 06:39→06:40（0.1MB）；subagent 扮演 experience-agent
- 主题：FR-001 重构（#9）之外的**实现/调试经验**入库（经验≠规则）

## 提炼的 4 条经验（draft 状态，human-in-the-loop）

- **E1 对象名 token 消歧**：供电 token 排除集（NON_SUPPLY_TOKENS）必须覆盖驱动/通道变体（DRVx/HT…），否则供电轨对检查不可见——曾掩盖 TM114/124/127/128 四处 VBUS 漏检（未闭 K5）。
- **E2 测试垫偏置误报**：名字含 cap 家族 token（VAC）≠ 供电轨；**对象名和闭合 Share 继电器名都含**测试垫 token（AMUX/VDM/NTC/ATEST）才判测试垫偏置、不查 Cap（消除 TM132/134 的 K21_VAC_Cap 误报）。
- **E3 豁免粒度反模式**：函数级（"函数有 MIRET → 整函数不闭"）与集合级（`mi_pins` 非空即跳过）是同款反模式；豁免须落 **PIN 粒度**（`fam & mi_pins`）。
- **E4 工具链**：严格扫描 `verify_relay_trace.py --warn-as-error` + 秒级编译 `fast_rebuild.ps1 -Incremental`（需传 Path 参数，5.1s 0 errors/0 warnings）。

## 落地

- 新建 `.claude/knowledge/experience/relay-check.md`（E1/E2/E3）、`project-notes.md`（E4）；更新 `experience/index.md`。

## 交叉引用

- #9（FR-001 规则本体）→ 本会话（实现经验）是同一重构的两层沉淀；与 #11（verify_relay_trace.py 结构）直接相关。
