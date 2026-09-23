---
name: cbit-singlepoint-agent
description: CBIT Phase2 单点继电器#define — 已脚本化→gen_cbit_defines.py (本文件为规格文档, 规则溯源)
model: sonnet
tools: Read, Write
---

# CBIT Single-Point Agent — Phase 2（规格文档）

> **已脚本化 (2026-08-09)**: 本 agent 的确定性逻辑（动态读 CBIT 表 + F/S 合并 + BUS 方向合并 + 单点 #define 生成）已完整落地为 **`gen_cbit_defines.py`**（`merge_names()` + `gen_singlepoint_defines()`）。
> **主 Skill / cbit-agent 不再调用本 agent 执行**，直接调脚本。
> 本文件保留为**规格文档**：以下是脚本实现的规则源头（每条规则 ↔ 脚本函数见 `RULE_COVERAGE` C-P1/C-P1a/1b/1c/C-P2）。

## 输入

CBIT 表 Excel（脚本动态读，col0=原位号, col10=CBIT通道, 分组标题定位组别）:
```
cbit_value -> [{name, group, cbit_raw}, ...]
```

## 铁律

1. 单点定义 = 扣除 `_Sx`/`_SxSy` 后缀后保留完整名
2. 同一 CBIT 的 F/S 双线圈合并 (KELVIN 保留 `_FS`)
3. 单点定义不参考特殊说明 2/3/4
4. 去重后每个 CBIT 值只出现一次

## 合并规则（脚本 merge_names() 完整实现）

### 优先级 1 — 同 CBIT 双线圈合并（机械 G6K 双线圈共享同一 CBIT 通道）

```
单条目: 直接使用 name

KELVIN F/S 对 (如 K86_KELVIN0_F + K86_KELVIN0_S):
  → base_FS (如 K86_KELVIN0_FS)

非KELVIN F/S 对, 单字母后缀 (如 K22_ACDRV1_F + K22_ACDRV1_S):
  → 去掉 _F/_S 后缀 (如 K22_ACDRV1)

非KELVIN F/S 对, 全词后缀 (如 K_FPVIH_TO_KLV_FORCE_S1 + K_FPVIH_TO_KLV_SENSE_S1):
  → 合并为 _FOS_SNS 后缀 (如 K_FPVIH_TO_KLV_FOS_SNS)
  判断: 两个名称去除 _Sx 站点后缀后，仅在 _FORCE / _SENSE 部分不同 + 共享同一 CBIT

其它共享 CBIT 的名字 (如 K147_PB0_OSC + K147_PB1_OSC):
  → K_PB0_PB1_OSC (name1_name2)
```

### 优先级 2 — BUS 方向合并

```
BUS FH/SH 对 (如 K46_BUS_FH_SW1 + K46_BUS_SH_SW1):
  → K46_BUS_SW1 (去掉方向标记)
BUS FL/SL 对 (如 K47_BUS_FL_SW1 + K47_BUS_SL_SW1):
  → K47_BUS_SW1
```

### FORCE/SENSE 合并优先级（二选一，不可同时用）

- 如果名字仅以 `_F` / `_S` 结尾（单字母）→ 去掉后缀
- 如果名字以 `_FORCE_*` / `_SENSE_*` 结尾（全词）→ 合并为 `_FOS_SNS`
- 所有后缀合并后，再应用 BUS 方向合并

## 输出格式

按 group 分组输出（脚本 `gen_singlepoint_defines()`）:

```cpp
// 1.1 MOS SPST (TLP3412, per-Site _S1~_S8)
#define K1_COMP_AMP                         1      // S34_CBIT1
#define K6_VBUS_LP                          6      // S34_CBIT6
...

// 1.2 G6K Dedicated (per-Site _S1~_S8)
#define K3_BUSL_VBUS                        3      // S34_CBIT3
...

// 1.3 G6K Shared (2-Site _S1S2/_S3S4/_S5S6/_S7S8)
#define K0_VCC_Cap                          0      // S34_CBIT0
...
```

## 输出验证（脚本 V1~V8 强制）

- 每个 CBIT 值只出现一次 (V1)
- 无重复命名 (V1)
- 总数 = 去重后的 CBIT 数 (V5)
- F/S 成对已合并 (V6) / 位号范围 0~255 (V4) / 命名规范 (V3)

## 脚本验证状态（2026-08-09）

- `--audit-rules`: 规则覆盖自检 PASS
- 与 phase2_singlepoint_output.txt 对拍: **161 条逐字节一致**
- AI.cpp 13 个实际使用 define: 全覆盖 (1 个命名差异 WARN: K25_VCC_F vs 规范 K25_VCC, 同 CBIT 值)
- V1~V8 全 PASS
