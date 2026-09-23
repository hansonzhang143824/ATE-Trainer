# UVLO 要点总结（UVLO/PRST 阈值 AWG · 电压阈值 + 迟滞）

> 源文件：`L4-Golden-code/UVLO.cpp`（PRST_TEST，98 行）｜索引登记：PRST 阈值 AWG（一般测试项目）—— rampv_capv 双扫(TRIG_RISING/FALLING) + VAC1/2/3 三通道 + Hys=(rise−fall)×1e3。**注意：与 L4-Golden-code/toggle-template.cpp 内容相同（同源快照）——本 md 按"UVLO 族阈值方法论"写，toggle-template.md 按"模板复用"写**

## 1. 参数类型
- **UVLO/PRST 阈值 AWG**（欠压/present 电压阈值）：一般测试项目；同原理族 UVLO/OVP/PRST/VBAT_LOW/RECHG（见 L1-chip/UVLO.md、L3-method/UVLO.md）。
- 与 Current Threshold（ZCD）的关键区别：**UVLO 有上下两个阈值 + Hys；ZCD 单阈值、无迟滞**。

## 2. 角色抽象（精髓）
- **被测 rail ↔ 比较器通道角色**：VAC1/2/3（本例为 GD present 通道，每通道一次完整测量），由 0x56(DMUX_SEL) 选择：VAC1=0x24 / VAC2=0x23 / VAC3=0x22。
- **比较器输出监测脚 = NTC2_FOVI**（FOVIe_10V/100UA，FI=0）：指示 PIN 类观测；注意 Open-Drain 需上拉（FR-002）、Push-Pull 不用（L1-chip/UVLO.md）。
- 供电角色：VBAT_ACM=V_TYP + K_VCC_Cap/K_VBAT_Cap（不参与 ramp 的 rail 固定供电）。
- 下一项目：单通道 UVLO/OVP/VBAT_LOW = 只取一个通道块；多 rail 版 = 复制块、换 DMUX_SEL。

## 3. 关键结构/特殊点
- **rampv_capv 双扫 = 阈值 AWG 标准打法**：升扫（低→高，TRIG_RISING）→ 上阈值；降扫（高→低，TRIG_FALLING）→ 下阈值；**Hys=(rise−fall)×1e3（mV）**。
- 每通道独立块 + 通道间先关再开的干净切换（防上一通道残留影响）。
- I2C：entertestmode + wake_up(0x13=0x02) + EN_I2C(0x58=0x01) + DMUX_EN(0x55=0x01) + DMUX_SEL(0x56)。
- 参数命名规范：`ShortName_Rise / _Fall / _Hys`（Hys=Rise−Fall，L3-method/UVLO.md）。

## 4. 上电/下电时序
- 上电：SetOn(K_VCC_Cap, K_VBAT_Cap[, K_VACx_ACM]) → delay 3ms → VBAT=V_TYP（ACM 20V）→ VAC123_VBATD 预置 2.8V → I2C → 双扫。
- 通道切换：VAC123_VBATD 归 0、该通道 RELAY_OFF → 下一通道重新 SetOn。
- 整体下电：VAC123_VBATD→0、VBAT→0 → delay 200us → 统一 RELAY_OFF。

## 5. 测量与判定
- `rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 2.95, 3.45, 400/200, 10, 2.5, TRIG_RISING, vacx_rise)` + 降扫（3.25→2.75, TRIG_FALLING）。
- FOR_EACH_VALID_SITE 内算 `hys=(rise−fall)*1e3`（mV）；VACx_Rise/Fall/Hys SetTestResult；判定在 spec 层。

## 6. 一句话适用场景
UVLO/PRST/OVP/VBAT_LOW 类"供电电压阈值 + Hys"测试（含多 rail/多通道）：直接抄本文件的双扫 + DMUX 通道切换框架；写参数时确认 Hys 单位约定（本文件 mV，OVP.cpp 存 V）。
