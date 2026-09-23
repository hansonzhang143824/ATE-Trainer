# 闭环模型 + Kelvin/Non-Kelvin 理论

> 来源: `源表规则.txt`（正文已整合到本文档）。本文档是继电器配置和测量代码的理论基础。

---

## 一、物理链路模型

```
POGO(源表输出点) → 继电器 → Copper(原理图DUT PIN/铜皮) → 弹簧针 → 芯片PAD
```

- **POGO**: 所有源表 Force/Sense 线的出口，包括 FH/FL/SH/SL、AGND/DGND/JGND、CBIT、电源、QTMU、QVMe
- **Copper**: 原理图上的 DUT PIN 铜皮，简称 copper
- **弹簧针**: 连接 copper 和芯片 PAD，存在接触电阻

---

## 二、模拟源表统一特性

| 特性 | 说明 |
|------|------|
| **4线 Kelvin 结构** | 所有模拟源从 POGO 出来都是 FH/SH/FL/SL 四线分离（但 HIB 可通过继电器降级为 2 线） |
| **Force 端** | 输出电压/电流，**测量电流** |
| **Sense 端** | **测量电压**，相当于理想电压表（内阻 >100MΩ） |
| **Sense 阻抗** | 内阻 >100MΩ → 10K 串联电阻对测量影响 <1%，可忽略 |

### 模拟源表类型

ACM, ACM200, FXVIe, FXVIe_PLUS, FOVIe, FPVIe

### FPVIe 特殊

- 大电流、通道数少 → **采用浮动接法**
- 浮动定义: **FPVIe 的 Low 端不强制接 AGND**（与其他模拟源的核心区别）
- 其余模拟源: FL→AGND_F/GND_F, SL→AGND_S/GND_S（芯片放好后已短接到地）

---

## 三、闭环原则 = 两个条件缺一不可

### 条件①: Force-Sense 必须连接

FH/SH 之间必须有通路（继电器/电阻/芯片PAD短接），FL/SL 同理。

| 连接形式 | 判定 |
|---------|------|
| 直接导线短接 | ✅ 连通 |
| 继电器导通 | ✅ 连通 |
| 芯片放置后 PAD 处短接 | ✅ 连通 |
| <5K 电阻 | ✅ 视为短接 |
| >5K 电阻 | ❌ 视为开路（Board check 除外） |
| 10K 电阻 + 芯片放置 | ✅ 视为 Kelvin（芯片 PAD 短接 << 10K） |

> ⚠️ 板载 Kelvin 电阻（>5K 接在 Force-Sense 之间）仅用于 Board check 开路检测，正常测试时视为不存在。

### 条件②: High-Low 必须形成回路

FH/FL 之间电流必须能流通（不能断路）。

#### 四种闭环类型

| 类型 | High 端 | Low 端 | 典型场景 |
|:---:|---------|--------|---------|
| **A** | 到 DUT Pin | 到 DUT Pin | FPVI 跨 Pin: `iset[AxB]`, `vset[AxB]` |
| **B** | 到节点 | 到节点 | 测电阻/电容等器件两端 |
| **C** | 到 DUT Pin | 到节点（含 AGND） | 非浮空源单 Pin: `vset[Pin,V]`, `iset[Pin,I]` |
| **D** | — | — | Kelvin 电阻 >5K 视为开路（仅 Board check 用） |

#### 非浮空源的闭环（类型 C）

```
FH/SH → [继电器] → [电阻] → DUT Pin → DUT → AGND
FL/SL → [继电器] → AGND_F → AGND
```

- High 端只需满足条件①（Force-Sense 连接 + 到达 Copper/节点）
- Low 端芯片放好后 FL/SL 已短接到 AGND

#### FPVI 浮动源的闭环（类型 A）

```
FH/SH → [BUS继电器] → PinA → DUT → PinB → [BUS继电器] → FL/SL
```

- Low 端**不接 AGND**，两端都需要 BUS 继电器
- 浮动 = FH/FL/SH/SL 四线全部浮空，电流由 PinA→PinB 唯一路径决定

---

## 四、Kelvin vs Non-Kelvin 连接

### 定义

> ⚠️ 无论 Kelvin 还是 Non-Kelvin，Force 和 Sense **都必须连通**（闭环条件①）。区别仅在于汇合点的位置。

```
Kelvin:     FH → 继电器 → Copper_F → 弹簧针_F → PAD ┐
            SH → 继电器 → Copper_S → 弹簧针_S → PAD ┘ (在PAD处汇合)
            ↑ 走线全程分开，直到芯片PAD才短接 ↑

Non-Kelvin: FH → 继电器 → Copper → 弹簧针 → PAD
            SH → 继电器 → Copper (同上) ┘ (在Copper/继电器处已汇合)
            ↑ 在到达芯片PAD之前就已经短接 ↑
```

| | Kelvin | Non-Kelvin |
|------|:---:|:---:|
| Force/Sense 短接点 | 芯片 **PAD** | **Copper**（或更早） |
| HIB 上 Force-Sense 走线 | **分开走线**，不直接在板上短接，通过芯片 PAD 处汇合 | **已在板上短接**（继电器/导线） |
| 接触电阻影响 | ❌ 无（Sense 直接测 PAD） | ✅ 有（Copper→PAD 的接触电阻含在测量中） |

### Non-Kelvin 的 IR Drop 误差

```
Vsense = I × R_path + V_expect

R_path = R_导线(~1Ω) + R_继电器(几十mΩ~几十Ω) + R_接触(几Ω~几百Ω)
```

大电流场景下 IR drop 显著，必须用 Kelvin 连接保证精度。

### 接触电阻

弹簧针与 Copper/PAD 接触必然产生接触电阻：**几 Ω ~ 几百 Ω**。

- Kelvin 连接: Sense 线直接测 PAD 电压，接触电阻在电压表高阻回路中可忽略
- Non-Kelvin 连接: Force 电流流经接触电阻产生压降，Sense 在 Copper 处测量包含了这个压降

### 常规做法

Force 和 Sense 一般希望连接到**相同位置**（同节点/同 Copper/同 PAD），特殊情况由用户说明。

---

## 五、POGO 完整列表

| 类别 | POGO 标识 | Low 端 |
|------|----------|--------|
| **模拟源 FH/SH/FL/SL** | S28_ACM200_FH0~11, S30_FOVIe_FH0~1, S32_FPVIe_FH0 等 | 各自 FL/SL |
| **地** | AGND_F, AGND_S, DGND, JGND | — |
| **CBIT** | S34_CBIT0~127, S36_CBIT0~127 | JGND |
| **电源** | S36_+15V, S36_-15V, S36_+12V, S36_+5V | JGND |
| **电源** | S34_+15V, S34_-15V, S34_+12V, S34_+5V | JGND |
| **QTMU** | QTMU_A/B High 端 | DGND |
| **QVMe** | QVMe High/Low | 自身闭环 |
| **DCM** | S24_P0~63, S9_P0~63 | DGND |

### 地之间的短接关系（设计规范，100%强制）

```
AGND_F ←→ AGND ←→ DGND ←→ JGND
```

**原理图上三者强制短接（99% 项目如此标注）。**

| 地 | 用途 |
|----|------|
| AGND_F, AGND_S | 模拟地（Force/Sense），与 AGND 短接 |
| DGND | 数字地 — **DCM、QTMU 的 Low 端 100% 强制接 DGND** |
| JGND | CBIT/电源地 — **CBIT、电源的 Low 端 100% 强制接 JGND** |

因为三地互通，不同源表的 Low 端实际等电位，但设计上各源表的 Low 端参考地是指定的不可混用。

---

## 六、数字源表

### 数字源包括

**CBIT、电源、DCM、QTMU**

### 共同特性

| 特性 | 说明 |
|------|------|
| **不分 Kelvin** | 从 POGO 出来就是 **Non-Kelvin** 结构（FH/SH 已短接），只有 2 线 |
| **Low 端统一** | 全部短接 **DGND**，DGND 也通过 POGO 输出 |
| **闭环简化** | **只需 High 端形成闭环**，Low 端自动经 DGND 回流 |

### 各数字源 POGO

| 数字源 | High 端 POGO | Low 端 |
|--------|-------------|--------|
| DCM | S24_P0~P63, S9_P0~P63 | DGND |
| QTMU | QTMU_A/B High 端 | DGND |
| CBIT | S34_CBIT0~127, S36_CBIT0~127 | JGND（JGND↔DGND 互通） |
| 电源 | S36_±15V/±12V/+5V, S34_±15V/±12V/+5V | JGND（JGND↔DGND 互通） |

### 闭环判定（简化版）

```
数字源闭环 = High 端到达 Pin/节点 → 闭环 ✓
（Low 端已固定接 DGND，无需额外继电器）
```

### 特殊源表 QVMe

- 独立电压表，**只有 Sense 线（SH/SL），无 Force 线**
- 闭环原则与模拟源一致（条件① SH-SL 连通 + 条件② 回路）
- 不输出电流，仅测量电压

### CBIT 驱动能力

| 继电器类型 | 1个 CBIT 最大驱动数量 |
|-----------|:---:|
| 机械继电器 (G6K/AGQ) | **8 个** |
| 光耦继电器 (TLP3412/G3VM) | **32 个** |

> CBIT 识别文档后续更新。

---

## 七、应用于继电器分析

### 判断闭环是否满足

1. 画出 Force 电流路径（必须闭环）
2. 画出 Sense 电压测量路径（两端必须到达目标测量点）
3. 确认 Force 和 Sense 在目标点处等价（Kelvin）或短接（Non-Kelvin）
4. 确认 High-Low 形成完整回路

### 常见违反场景

| 违反 | 现象 |
|------|------|
| Sense 断路 | 电压读数漂移/噪声极大 |
| Force 断路 | 电流无法输出，源表报错 |
| Non-Kelvin + 大电流 | 测量电压 = DUT电压 + IR drop，精度差 |
| Force-Sense 未连接 | 源表无法正常工作 |
