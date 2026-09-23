---
name: power-off-agent
description: 下电序列 — 已脚本化 → gen_power_sequence.py（推理→agent, 固定→脚本）。本文档为脚本规格文档，保留 R-POFF 规则清单供脚本覆盖验证，不直接运行推理
model: sonnet
tools: Read, Grep, Bash
---

# 下电 Agent — 反转上电序列

> ⚠️ **已脚本化 (2026-08-09)**：下电逻辑为固定模板（三步下电/浮动反转台阶/大电流顺序/RELAY_OFF 统一量程），已由 `gen_power_sequence.py` 取代。本文档保留为**脚本规格文档**：列出 R-POFF 铁律清单 + 脚本输入接口。主 Skill 调用脚本消费 PowerState 生成 Step 5 下电代码，不再派发本 agent 推理。

## 脚本调用方式（主 Skill 用）

```bash
python gen_power_sequence.py \
  --meta <TestItemMeta.json> \
  --pin-map <pinmap.json> \
  --define Pin_Channel_define.h \
  --mode power-off
```

脚本内部复用上电阶段算出的 PowerState（sources/floatingPairs/upSequence），stdout 输出 `###SECTION:POWER_OFF###` 代码块，填入 `<%POWER_OFF_CODE%>`。上电段与下电段**同一次调用**（`--mode both` 默认）保证 PowerState 一致，主 Skill 分别取两个 SECTION。

## 核心原则: 下电起点 = 上电终点，必须读取 PowerState！

脚本内部从上电阶段继承 PowerState（不重新计算），保证下电反转的是真实上电终点。

## 输入

- `TestItemMeta`（--meta，含 hardwareInit/floatingPairs/rampProfile）
- `--pin-map`（pin→object，与上电段同一映射）
- `TestItemMeta.testType`
- `TestItemMeta.params[].check`

## 输出: 下电代码块（POWER_OFF SECTION）

## 决策流程（脚本内部实现，本文档仅存档原理）

### Step 1: 判断下电类型
| 条件 | 类型 |
|------|:---:|
| `floatingPairs` 非空 + type="vset" | 浮动电压源下电 |
| FI ≥ 1A | 大电流下电 |
| 其他 | 普通下电 |

### Step 2a: 普通下电
```
1. 对 PowerState.sources[] 每个源: .Set(FV, 0, 原vRange, 原iRange, RELAY_ON)
2. delay_ms(1)
3. 对每个源: .Set(FV, 0, 10V档, 10MA档, RELAY_OFF)
```

```cpp
// ====== Step 5: 下电 ======
// 步骤1: 所有源归零(RELAY_ON保持量程)
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_ms(1);
// 步骤2: RELAY_OFF(统一10V/10MA)
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
```

### Step 2b: 浮动电压源下电
**核心约束: 反转 upSequence, PinA 先降到与 PinB 齐平, 每步 ≤5V, 每步 200μs**

算法:
```
1. PinA 降到与 PinB 齐平 (压差→0)
2. PinB 归零 (或下一步目标)
3. 其他源归零
4. PinA 归零
5. delay_ms(1) → 所有源 RELAY_OFF (统一10V/10MA)
6. FPVI 最后 RELAY_OFF
```

```cpp
// ====== Step 5: 下电（台阶式） ======
// 基于PowerState: BST=10V, SW=5V
// 步骤1: PinA降到与PinB齐平
BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
// 步骤2: PinB归零
SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
// 步骤3: 其他源归零
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
// 步骤4: PinA归零
BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
// 步骤5: 所有源 RELAY_OFF
delay_ms(1);
BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
// FPVI最后断开
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_OFF);
```

### Step 2c: 大电流下电
```cpp
// 1. FI=0
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
// 2. FV=0
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
// 3. RELAY_OFF
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_OFF);
```

## 量程规则（R-POFF-06）
| 状态 | 电压量程 | 电流量程 |
|------|---------|---------|
| RELAY_ON (归零中) | 保持原量程 | 保持原量程 |
| RELAY_OFF (断开) ACM200/FXVIe_PLUS | 统一 `10V` | 统一 `10MA` |
| RELAY_OFF (断开) FPVIe | `FPVIe_1V` | `FPVIe_10MA` |

> ⚠️ 注意：FPVI RELAY_OFF 电流量程为 `10MA`（非 10A），已对拍 AI.cpp/reference 确认。

## R-POFF 规则清单（脚本必须覆盖）

| 规则ID | 内容 | 脚本函数 | 状态 |
|--------|------|---------|:---:|
| R-POFF-01 | 下电类型判定（普通/浮动/大电流） | classify_power_off() | 已覆盖 |
| R-POFF-02 | 普通三步（归零→delay_ms(1)→RELAY_OFF） | gen_normal_power_off() | 已覆盖 |
| R-POFF-03 | 浮动反转 upSequence（PinA先降→PinB→其他→PinA） | gen_floating_power_off() | 已覆盖 |
| R-POFF-04 | FPVI 永远最后一个 RELAY_OFF | gen_floating_power_off() | 已覆盖 |
| R-POFF-05 | 大电流 FI=0→FV=0→OFF | gen_high_current_off() | 已覆盖 |
| R-POFF-06 | RELAY_OFF 统一量程（FPVI 用 1V/10MA） | relay_off_ranges() | 已覆盖 |
| R-FLT | 下电台阶 ≤5V + delay_us(200) | gen_floating_power_off() | 已覆盖 |
| R-ST | 台阶延迟 | gen_floating_power_off() | 已覆盖 |

## 知识库引用
- 源表量程: `knowledge/sources/acm200.md`, `fovie.md`, `fpvie.md`
- 台阶规则: `knowledge/standards/units.md`
- FPVI 大电流: `knowledge/sources/fpvie.md`

## 铁律
- 必须从 PowerState 读取最终状态
- PinA 先降 → PinB 再降 → 其他 → PinA 归零
- 每步 |PinA-PinB| ≤ 5V + delay_us(200)
- FPVI 永远最后一个 RELAY_OFF
- 大电流: FI=0 → FV=0 → OFF
