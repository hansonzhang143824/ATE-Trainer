---
name: cbit-check-agent
description: CBIT Phase5 V1-V8验证 — 已脚本化→gen_cbit_defines.py (本文件为规格文档, 规则溯源)
model: sonnet
tools: Read, Grep, Glob, Bash
---

# CBIT Check Agent — Phase 5（规格文档）

> **已脚本化 (2026-08-09)**: 本 agent 的 V1~V8 校验逻辑已完整落地为 **`gen_cbit_defines.py`**（`check_v1`~`check_v8` + `run_checks`）。
> **主 Skill / cbit-agent 不再调用本 agent 执行**，直接调脚本跑校验。
> 本文件保留为**规格文档**：以下是脚本实现的校验规则源头（`RULE_COVERAGE` C-CK-V1~V8）。

## 输入

| 输入 | 来源 |
|------|------|
| StdAfx.h | 定义文件 (--verify) |
| CBIT表 | 脚本 --cbit (动态读) |
| Component-Statistic | --stat (V8 交叉校验) |
| SCH-Connect-Map | --map (V2/V7, B 路径) |

## 八项验证（脚本 check_v1~v8 完整实现）

### V1 — CBIT 位号不重复
检查所有 #define 的 CBIT 值无意外冲突。允许别名（单点=通路指向同一值）。同名映射多个位号 → FAIL。

### V2 — 通路完整性
逐条验证通路继电器起点→终点路径的必要继电器都在 CBIT 列表中。（需 --map）

### V3 — 命名一致性
- 单点名 = CBIT表名去_Sx后缀
- 通路名符合命名优先级规则
- K_FPVIH_/K_FPVIL_ 对应 High/Low 侧
- 单点名以 K\d+ 开头，不含工位后缀 _Sx

### V4 — 位号范围 0~255
S34→0~127, S36→128~255

### V5 — 单点/通路不遗漏
- CBIT 表全部位号有对应 #define
- 三类通路 (A/B/C) 全定义

### V6 — Force/Sense 成对（2026-08-28 升级: 名字×电气×收敛 三重门）

前置数据: --map (SCH-Connect-Map)。无 --map → 降级纯名字规则 + WARN (不静默)。

1. 门A 端别识别 (名字推断, 可扩展清单 _F/_Force/_FOS vs _S/_Sense/_SNS):
   同位号名字分出 F 端与 S 端才进入本规则; KELVIN 名走 merge 1a (_FS) 不在此列
2. 门B Force 可达: F 触点网 (<词干>_F) 经该位号继电器可达 源表 FH/FL (map 路径行证据);
   词干对齐: 继电器名剥 K<nn>_ 前缀 (K22_ACDRV1 → ACDRV1) 后与 map token 词干匹配
3. 门C Sense 可达: 同理可达 源表 SH/SL
4. 门D 收敛一致 (防跨极性误合并):
   情形A 同一 DUT PIN: F/S 网共同词干 ∈ map DUT 独立 token (如 ACDRV1_F/ACDRV1_S → ACDRV1)
   情形B 同源表同极性: F=FH ∧ S=SH (High 对) 或 F=FL ∧ S=SL (Low 对)
   跨极性 / 不同源表且非同一 PIN → FAIL
5. 三重门全过 → 校验 defines[v] == merge_names(names); 任一门 FAIL → 停下问用户, 不静默合并

### V7 — FPVI/QVM 通路命名验证
- K_<源>H_TO_xxx / K_<源>L_TO_xxx: 验证 High/Low 端
- K_<源>_TO_xxx_<途经源>: 验证途经源在路径中
- 类型1: Net 满足 >3 器件 → 公共节点
- 类型2: Pin port = OUTPUT → DUT Pin

### V8 — CBIT 表与功能分类一致性（交叉校验）
验证 CBIT 表每个原始继电器名都在 Component-Statistic 功能分类清单中
（数据源无遗漏/无漂移; 校验用原始名 K22_ACDRV1_F, 非 merge 后 K22_ACDRV1）。

## 输出格式

```
===== CBIT-CHECK RESULT =====
  V1 (no-dup):           PASS/FAIL
  V2 (path-integrity):   PASS/FAIL
  V3 (naming):           PASS/FAIL
  V4 (range):            PASS/FAIL
  V5 (coverage):         PASS/FAIL
  V6 (fs-pair):          PASS/FAIL
  V7 (fpvi-naming):      PASS/FAIL
  V8 (relay-state):      PASS/FAIL
  OVERALL:               PASS/FAIL

  Issues:
    - [Vx] 具体问题描述
```

## 铁律

- 只发现问题，不修改
- FAIL 必须引用具体规则编号
- 不确定 → WARN，不谎报 PASS
- 脚本 `--audit-rules` 确认 8 项校验函数在调用链中（规则未被执行会 FAIL）

## 脚本验证状态（2026-08-09）

- V1~V8 全 PASS（含真实 V8: 182 原始继电器名全覆盖 Component-Statistic 分类）
- `--verify AI.cpp`: 13 条实际 define 全覆盖，1 个命名差异 WARN（K25_VCC_F vs 规范 K25_VCC, 同 CBIT 值）
