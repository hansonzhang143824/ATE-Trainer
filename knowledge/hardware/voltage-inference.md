# 电压推断规则 — 四类推断方法

## 概述

测试代码中的 Pin 电压不仅由 DFT 指令决定，还受源表约束、FET 导通、FPVI 大电流等因素影响。本文档定义了四类电压推断方法，Agent 在生成代码时必须**逐阶段推算每个 Pin 的电压**。

---

## 四种推断类型

### 类型 A: 源表限定 (Source-Limited)

**规则:** Pin 电压 = 源表设定值

```
SW_ACM.Set(FV, 4) → SW = 4V
VBAT_ACM.Set(FV, 4.2) → VBAT = 4.2V
PMID_FOVI.Set(FV, 15) → PMID = 15V
```

**适用范围:** 非浮空源（ACM200, FOVI），单 Pin vset，无 FET 介入

**约束:** 源表输出阻抗低，Pin 电压被强制到设定值

---

### 类型 B: AB 浮动对 (Floating Pair, AB-Type)

**规则:** PinA - PinB = 源表设定值，前提是闭环完整

```
vset[BST2SW, 5V] + FPVI闭环 → BST - SW = 5V
```

**前提条件:**
1. 源表两端各自通过继电器连接到对应 Pin
2. 闭环完整: Source_H → [BUS] → PinA → [BUS] → Source_L
3. 没有其他源表强制驱动 PinA 或 PinB

**判断流程:**
```
1. 检查 DFT 是否有 vset/iset[AxB] 指令
2. 检查 BUS 继电器是否闭合（两端都要）
3. 如果闭环完整 → AB关系成立: PinA - PinB = 设定值
4. 如果闭环不完整 → 降级为两个独立Pin, 各自用类型A
```

**示例:**
```
vset[BST2SW, 5V]:
  BUS闭合 → BST-SW=5V (类型B)
  BUS未闭合, BTST_ACM=5V, SW_ACM=0V → BST=5V, SW=0V, BST-SW=5V (两个独立类型A, 等效)
```

---

### 类型 C: FET 导通 (Chip Type — 用户提供)

**规则:** FET 导通后, 两端 Pin 电压相等

```
HS FET (0x59 HSON=1) 导通 → PMID = SW
LS FET 导通 → SW = PGND
```

**NU1201 已知 FET 对（用户提供）:**

| 编号 | FET 对 | 类型 | 导通条件 | 导通后 |
|------|--------|------|----------|--------|
| C1 | PMID ↔ SW | 上管 (HS) | 0x59=0x01 (HSON=1) | PMID = SW |
| C2 | VBUS ↔ PMID | 上管 | — | VBUS = PMID |
| C3 | SW ↔ PGND | 下管 (LS) | — | SW = PGND |

**通用 FET 对模式:**

| 类型 | 典型对 | 导通后 |
|------|--------|--------|
| **上管 (High-Side)** | PMID-SW, VBUS-PMID, VIN-SW | D=S |
| **上管驱动** | BST-HG, BST-DRVH | BST ≈ DRVH (自举) |
| **下管 (Low-Side)** | SW-PGND, LG-PGND | S=GND |
| **下管驱动** | DVRL-PGND, DRVH-SW | — |

**推断规则:**
```
FET导通前: 两端电压独立, 各自用类型A/B推断
FET导通后: 两端电压相等, 取较高一侧 → 低侧跳变到高侧
```

> **重要:** FET 对由用户提供，Agent 不可自行推断。需在双表解析阶段收集。

---

### 类型 D: FPVI 大电流 (High Current Path)

**规则:** FPVI 施加 ≥ 200mA 电流时, 两端 Pin 电压非常接近

```
iset[PMID2SW, 1A] → PMID ≈ SW (压差 = I × RDSON, 通常 < 100mV)
```

**适用范围:**
- FPVI 通过 BUS 继电器连接两个 Pin
- FI ≥ 200mA
- 电流路径: FPVI → PinA → DUT → PinB → FPVI

**推断:**
```
PMID ≈ SW (压差仅 RDSON × 1A)
若 RDSON=50mΩ → 压差=50mV → 可近似 PMID=SW
```

---

## 电压推断工作流

对每个测试阶段，按优先级推断每个 Pin 的电压:

```
阶段: 上电后、FET导通前
  Pin电压 = 类型A (源表设定) 或 类型B (AB浮动对)
  示例: VBAT=4.2, VDRV=5, SW=0, PMID=15, BST=20

阶段: FET导通后、测量前
  1. 先按类型A/B计算
  2. 叠加类型C: FET对中低侧跳变到高侧
  3. 叠加类型D: FPVI大电流连接的两Pin近似相等
  示例: PMID=15 (A) → SW跳变=15 (C: PMID↔SW导通)
        BST=20 (A) → BST-SW=20-15=5V ✓

下电阶段:
  1. FET状态: 导通还是关断?
  2. 若导通 → SW跟随PMID (类型C)
  3. 按设定值更新Pin电压
```

---

## TM600 应用示例

### 已知条件
```
DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]
      iset[pmid2sw,1A] (dynamic)
FET对(C1): PMID ↔ SW, 导通条件 0x59=0x01
FPVI: K31_BUS_PMID + K17_BUSH_SW 闭合 → 类型D (大电流1A)
BST-SW: 无BUS → 类型A独立: BTST_ACM=20V, SW_ACM=0V
```

### 阶段电压追踪

| 阶段 | PMID | SW | BST | BST-SW | 推断依据 |
|------|------|-----|-----|:---:|------|
| 上电初态 | 0V | 0V | 0V | 0V | 类型A |
| 台阶1 | 0V | 0V | 5V | 5V | A: BTST=5, SW=0 |
| 台阶3 | 10V | 0V | 15V | 15V | A: BTST=15, SW=0 |
| 台阶4 | 15V | 0V | 20V | 20V | A: BTST=20, SW=0 |
| **FET导通** | 15V | **15V** | 20V | **5V** ✓ | C: PMID=SW |
| 测量(FPVI FI=1A) | ≈SW | ≈PMID | 20V | 5V | D: PMID≈SW |
| 下电台阶1 | 10V | 10V (C) | 15V | 5V | C: SW=PMID |
| 下电台阶3 | 0V | 0V (C) | 5V | 5V | C: SW=PMID |
| 下电完毕 | 0V | 0V | 0V | 0V | 类型A |

---

## 配置: FET 对定义 (用户输入区)

```json
{
  "chip": "NU1201",
  "fetPairs": [
    { "id": "C1", "pair": ["PMID", "SW"],   "type": "HS", "condition": "0x59_bit0=1" },
    { "id": "C2", "pair": ["VBUS", "PMID"], "type": "HS", "condition": "0x59_bit1=1" },
    { "id": "C3", "pair": ["SW", "PGND"],   "type": "LS", "condition": "0x59_bit2=1" }
  ]
}
```

> Agent 在解析 DFT 时加载此配置，生成代码时全程追踪电压。
