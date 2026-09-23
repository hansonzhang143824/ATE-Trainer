# Current Sense 电流检测（chip Block）

> 具体参数类型族 **CurrentSense**。四件套：`L1-chip/CurrentSense`(是什么) + `L3-method/CurrentSense`(怎么测) + `L4-Golden-code/CurrentSense`(长啥样) + `L5-debug/CurrentSense`(怎么排查，按需)。
> **下游关系**：Current Threshold（族5，ZCD/OCP/Peak 等）用本族的 Vcs 做阈值比较，见 `L1-chip/Current-Threshold.md`。

## 是什么

Current Sense（电流检测）是电源芯片**电流精度**的关键参数。核心精度管控 = 输出电压精度 + 输出电流精度，Current Sense 对应后者。

## 设计目的

| 用途 | 具体场景 |
|---|---|
| 过流保护 | OCP 检测、Peak 电流检测、ZCD 电流检测（都通过 current sense 实现），防短路/过载损坏 |
| 功率管理 | 结合电压检测实时监控功率（功率 = 电压 × 电流），优化能量管理效率 |
| 电池管理 | 监测充放电电流、计算剩余容量、防过充/过放 |
| 电流控制 | 恒流源控制、LED 驱动电流控制 |
| 计量计费 | 电能计量、按使用量计费 |

## 基本结构（电流镜式，内部 MOSFET）

- PowerFET 流过的电流 = IBAT，电流镜 FET 与 PowerFET 比例 **5K:1** → Imirror = IBAT/5K
- 镜像电流流过 **Rsns**（可 Trim 调 Gain），在 Rsns 上产生压降：**Vsns = Rsns × Imirror + Vos**，即常见的 Current Sense 电压 **Vcs**
- **核心参数两个**：① **Gain**（评价不同电流负载下表现一致性）② **Offset/Vos**（0 电流时的失调电压，Trim 指标，保证接近 0mV）

**示例**：Rsns 理想值 2K、镜比 5K:1、Vos=0mV → IBAT=1A 时 Imirror=0.2mA → Vcs=Imirror×Rsns=0.4V → **Gain = Vcs/IBAT = 400mohm**。Trim 时把 Vcs 经 AMUX 通路 MUX 到指定 Pin，把 Gain trim 到 400mohm（对应 Rsns trim 到 2K）。

**Vos 测试**：一般选 0 电流时 Trim，把 Gain error 影响降到最低。

## 第二种结构（电阻分压式，外部 Rpower）

- 用 **Rpower 取代功率 MOSFET**，差分电压采集电路类似，区别在于用**电阻比例**实现电流镜分流
- 内部 Rsns = Rpower × 5K：Rpower 上流 1A → Rsns 上 0.2mA → 理想 Vcs = Rsns×0.2mA + Vos(0mV) = Rpower×1A
- 核心 Gain 计算方法不变：**Gain = Vcs/Ipower**（例：VBUS、PMID）

## 内外置原则

| 功率 | Current Sense 位置 | 原因 |
|---|---|---|
| 大功率（>4~6A） | **外部** | 集成大功率 MOSFET 面积大、成本高；温升明显影响温度特性 |
| 小功率（<4~6A） | **内部** | 面积/成本可接受 |

外置例：IBUS_SNSP–IBUS_SNSN、IBAT_SNSP–IBAT_SNSN。

## 典型应用公共模式（Vcs + EA）

> 虚线框内 IBUS_FB 实际代表 Vcs；IBUS_REF 是设置的工作电流档位 reference；**EA = 比较器失调电压误差**（理想 0，为保证精度需 Trim 这个 EA）。

以下都是对外的**整体精度参数**，Current Sense 是其中一环，对整体精度影响非常大：

- Peak Current = Vcs + EA（峰值电流 EA 精度）
- OCP Current = Vcs + EA（OCP 电流 EA 精度）
- 环路 Current = Vcs + EA（环路电流 EA 精度）
- AMUX Current = Vcs + EA（AMUX 电流 EA 精度）
- ZCD Current = Vcs + EA（ZCD 电流 EA 精度）
- Trickle Current = Vcs + EA（Trickle 电流 EA 精度）

## Trim 建议

- 精度要求高的电路：**Gain 和 Offset 都 Trim**；不同模式（BUCK/BOOST）用不同套 current sense → 各自 Trim
- 其他 EA 也建议增加 Trim，最大化保证精度
- 任何一个环路出现精度问题，可结合 current sense 精度分析来源

## DFT 设计需明确（供 debug）

1. Current sense 测量方法 + 对应计算公式
2. 不同档位的寄存器配置方法
3. 有无不同工作模式（Buck/Boost/PFM/FPWM），不同模式 current sense 是否一致、是否每个测试方法都有
4. 测试 reference 怎么 mux 出来、mux 到哪个 Pin
5. 不同信号的驱动能力统计
