---
name: cbit-parse-agent
description: CBIT辅助解析 — 已脚本化→gen_cbit_defines.py (本文件为规格文档, 规则溯源)
model: sonnet
tools: Read, Grep, Glob, Bash
---

# CBIT Parse Agent — 辅助解析（规格文档）

> **已脚本化 (2026-08-09)**: 本 agent 的确定性逻辑（CBIT表→cbit_map / 定义文件→existing_defines）已完整落地为 **`gen_cbit_defines.py`**（`read_excel_cbit()` + `build_cbit_map()` + `load_existing_defines()`）。
> **主 Skill / cbit-agent 不再调用本 agent 执行**，直接调脚本。
> 本文件保留为**规格文档**：以下是脚本实现的规则源头（`RULE_COVERAGE` C-P1 / C-CK-V1~V8）。

> **架构定位回顾**: 在 CBIT-Definition（cbit-agent 执行）内作辅助——P1 单点用其 cbit_map（CBIT表→继电器序号）；P4 check 用其 existing_defines（已有定义文件提取）。
> **Netlist 解析 + G1~G5 功能分类已由 sch-parse 产出 Component-Statistic + SCH-Connect-Map 取代，本 agent 不再重做原理图解析。**

## 输入

| 文件 | 用途 |
|------|:---:|
| CBIT表 (.xlsx) | → cbit_map (P1 单点序号, 脚本 read_excel_cbit) |
| StdAfx.h | → existing_defines (P4 check, 脚本 load_existing_defines) |
| Component-Statistic | 单点继电器清单（sch-parse 产出, 直接取用, 脚本 V8 交叉校验） |

## 输出 (结构化) — 脚本内中间产物

```
=== CBIT_MAP ===
  cbit_value -> {name, group(MOS/G6K_DEDICATED/G6K_SHARED), cbit_raw}
  ← 供单点 merge / V5/V6 用

=== EXISTING_DEFINES ===
  existing_defines = {name: [values]}
  ← 供 P4 check 对拍用 (--verify)
```

## 解析规则（脚本实现）

### Step 1: 解析 CBIT 表 → cbit_map（脚本 read_excel_cbit + build_cbit_map）

```
1.1 读取 Excel 所有行 (跳过标题行, 分组标题 '光耦'/'机械独享'/'机械共享' 定位组别)
1.2 对每行:
    name = col0 (Netlist继电器名)
    cbit_str = col10 (S34_CBITn / S36_CBITn)
    val = n (S34) 或 n+128 (S36)   ← cbit_val()
    group = 根据表内分组标题判断 (MOS / G6K_DEDICATED / G6K_SHARED)
1.3 → cbit_map = {val: [{name, group, cbit_raw}, ...]}
    注意: 同一 val 可能有多个 name (F/S双线圈共享CBIT)
```

### Step 2: 解析定义文件 → existing_defines（脚本 load_existing_defines）

```
2.1 正则提取所有 #define Kxx value (允许行尾 // 注释)
2.2 筛选 value 在 0~255 范围的 → 继电器定义
2.3 → existing_defines = [(name, value)]
```

> **不做**: Netlist 解析 / G1~G5 门控 / Component-Statistic 生成 — 已由 sch-parse（Skill）前置产出。需要时直接读取 sch-parse 的输出文件，不重复解析。

## 验证状态（2026-08-09）

- CBIT 表 182 继电器全解析（MOS 102 / G6K_DEDICATED 61 / G6K_SHARED 19），与 phase2 硬编码逐项一致
- S36 通道 37 个 → 位号 128~255 (V4 校验通过)
- Component-Statistic 任务三 182 条分类全解析 (V8 交叉校验 PASS)
