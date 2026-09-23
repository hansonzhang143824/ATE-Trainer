# 一般电流阈值测试 ATE 通用方法（current-threshold-ate）

- 来源：用户 2026-09-02 提供。
- **L3 通用方法**：应用于一般电流阈值测试项（ZCD / Ipeak / Iocp / Itrickle / Ireg·Ilfc·Icc / Iterm 等）。
- 前置：观测脚代称见 `ATE-primer.md`（DTEST0→nQON）；电流检测方式见 L2 `07-current-sense.md`。

## 第一部分：参数介绍

**VBAT 充电相关**：
| 参数 | 典型值 | 测试方式 |
|---|---|---|
| **Itrickle** 预充电电流 | 100mA~500mA | 电流阈值 |
| **Ireg/Ilfc** 线性快充电流 | 500mA~2A | ⚠️ 不确定：电流阈值 **或 DC 电流测试**（若 DC 测试参考一般 DC 方法） |
| **Icc** 恒流充电电流 | 1A 以上 | ⚠️ 同上，电流阈值 或 DC |
| **Iterm** 充电截至电流 | 100mA~500mA | 电流阈值 |

**效率相关**：
| 参数 | 典型值 | 测试方式 |
|---|---|---|
| **ZCD** 过零检测电流 | ±1A 以内 | 电流阈值 |

**保护相关**：
| 参数 | 典型值 | 测试方式 |
|---|---|---|
| **Ipeak** 峰值电流 | 1A~几十A | 电流阈值 |
| **Iocp** 过流保护电流 | 1A~几十A | 电流阈值 |

> 除 Ireg/Ilfc/Icc 可能走 DC 测试外，其余均为**电流阈值测试**——通过 **ramp 电流** 或 **差分电压** 方式测量阈值电流点。

## 第二部分：执行流程（区分电流检测方式）

### 关键：先区分"芯片内置电流检测" vs "芯片外置电流检测"
> 具体区分方法参考《电流检测通用方法》（L2 `07-current-sense.md`）。

### 方式 A：电流检测**内置**的芯片

1. 用 **FPVI 连接芯片两个 Pin** → Ramp 电流，同时观测 **DTEST toggle**
   - 结构：`Param_Rise/Fall/Hys`（如 `VBAT_IPEAK_2A_Rise/Fall/Hys`）
2. FPVI 上**小→大** Ramp 电流 → DTEST 高→低 → **TRIG Falling edge** → `Param_Rising`
3. FPVI 上**大→小** Ramp 电流 → DTEST 低→高 → **TRIG Rising edge** → `Param_Falling`
4. 迟滞：`Param_Hys = (Rise − Falling) × 1e3`（mA，乘 1000）

### 方式 B：电流检测**外置**芯片，且 `电流×Rsns < 10mV`（外置电阻 Rsns）

> 在检测 Pin 之间外接电阻上 ramp 电流。

1. FPVI 链接电阻两端（电阻两端连两个 Sense Pin）→ Ramp 电流，观测 DTEST toggle
2. `Param_Rising = 捕获值 × Rsns / Rvs`
3. `Param_Falling = 捕获值 × Rsns / Rvs`
4. `Param_Hys = (Rise − Falling) × 1e3`（mA）
> ⚠️ 此方式 Rising/Falling 需**乘 Rsns/Rvs** 换算（把电压/电阻比转成电流）。

### 方式 C：电流检测**外置**芯片，`电流×Rsns > 10mV` 且 `外置电阻 < 50mΩ`

> 在检测 Pin 之间外接电阻上 ramp 电流。公式同 B。
1. FPVI 链接电阻两端 → Ramp 电流 → 观测 DTEST toggle
2. `Param_Rising = 捕获值 × Rsns / Rvs`
3. `Param_Falling = 捕获值 × Rsns / Rvs`
4. `Param_Hys = (Rise − Falling) × 1e3`（mA）

### 方式 D：电流检测**外置**芯片，`电流×Rsns > 10mV`，只需在检测 Pin 之间 **ramp 电压**

> ⚠️ 与 B/C 不同：此方式直接 ramp **电压**（非电流），按芯片内置电阻 `Rvcs` 换算回电流。
1. FPVI 连接两个 Sense Pin → Ramp **电压**，观测 DTEST toggle
2. `Param_Rising = 捕获值 / Rvcs`（芯片内置电阻）
3. `Param_Falling = 捕获值 / Rvcs`
4. `Param_Hys = (Rise − Falling) × 1e3`（mA）

### 各方式公式对比一览

| 方式 | Ramp 对象 | Rising/Falling 换算 | Hys |
|---|---|---|---|
| A 内置 | 电流 | 直接（=捕获电流） | `(Rise−Fall)×1e3` |
| B 外置 小mV | 电流 | `× Rsns/Rvs` | `(Rise−Fall)×1e3` |
| C 外置 大mV 小R | 电流 | `× Rsns/Rvs` | `(Rise−Fall)×1e3` |
| D 外置 大mV | **电压** | `/ Rvcs` | `(Rise−Fall)×1e3` |

## 第三部分：执行条件（管子导通前提）

1. 电流相关测试**有条件**：须有**寄存器配置 + 管子导通**必备条件
2. **充电相关**（Itrickle/Ireg/Ilfc/Icc/Iterm）：一般要求 **Battery FET 开启**；若无 Battery FET，需 **HSFET 或 LSFET 开启**——具体看 DFT ramp 电流在哪两个 Pin 之间
3. **Ipeak/OCP/ZCD**：一般要求 **HSFET 或 LSFET 开启**——需满足管子开启条件才能执行

## 关联

- 观测脚 = DTEST0(nQON)；驱动源 = FPVI（浮动差分源）接两 Pin/Sense
- 电流检测方式：L2 `07-current-sense.md`
- 管子开启：L1 `03-mosfet-drive.md`（HS 需自举 BST−SW；LS 直驱）
- L4 黄金案例：ZCD→`HS_ZCD.cpp`/`LS_ZCD.cpp`
