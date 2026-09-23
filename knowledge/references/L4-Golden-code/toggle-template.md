# toggle-template 要点总结（Toggle/AWG 迟滞模板 · 多通道逐块复制范式）

> 源文件：`L4-Golden-code/toggle-template.cpp`（PRST_TEST，98 行）｜索引登记：VAC1/2/3 GD present 检测 —— rampv_capv 双扫 + Hys + entertestmode + I2C 配置 + 三步下电；静态 FV-MV 类（如 VC_CLAMP_LOW）也可参考本文件的"无 ramp 框架"。**注意：与 L4-Golden-code/UVLO.cpp 内容相同（同源快照）——本 md 侧重"模板复用"，UVLO.md 侧重"阈值方法论"**

## 1. 参数类型
- Toggle/AWG（迟滞）：阈值翻转检测模板（GD present / PRST / UVLO 类比较器通用）；一般测试项目。
- 亦作为"静态 FV-MV（无 ramp）"项目的框架参考（索引 VC_CLAMP_LOW 行登记）。

## 2. 角色抽象（精髓）
- **被测通道角色**：VAC1/2/3 三路 GD present，每通道一次完整测量；通道由 0x56(DMUX_SEL) 选择：VAC1=0x24 / VAC2=0x23 / VAC3=0x22 —— 每通道 = "被测 rail + 内部比较器通道"组合。
- **ramp 源角色**：VAC123_VBATD_ACM（ACM200_10V/100mA）在阈值附近（~2.8V）ramp；**观测角色**：NTC2_FOVI（FOVIe_10V/100UA，FI=0，cap 抓翻转）。
- 供电角色：VBAT_ACM=V_TYP（ACM 20V）+ K_VCC_Cap/K_VBAT_Cap。
- 下一项目：N 路同构阈值 → 每路复制"继电器组 + DMUX 配置 + 双扫 + 关断"块，只换 DMUX_SEL 与继电器。

## 3. 关键结构/特殊点
- **多通道逐块复制范式**：每通道独立块 = SetOn(本通道继电器组，VAC2/3 各带 K_VACx_ACM) → 上电 + I2C → 升扫+降扫 → 先关本通道源/继电器 → 下一通道再 SetOn；通道间**先关再开的干净切换**防残留。
- 双扫窗口：升 TRIG_RISING(2.95→3.45)、降 TRIG_FALLING(3.25→2.75)；注意 VAC1/2 用 400、VAC3 用 200（扫描点数按通道可调）。
- **Hys=(rise−fall)×1e3 → mV**（R-HYS 规则）。
- I2C：entertestmode + wake_up(0x13=0x02) + EN_I2C(0x58=0x01) + DMUX_EN(0x55=0x01) + DMUX_SEL(0x56)。

## 4. 上电/下电时序
- 上电：SetOn(K_VCC_Cap, K_VBAT_Cap[, K_VACx_ACM]) → delay 3ms → VBAT=V_TYP(ACM 20V) → VAC123_VBATD 预置 → I2C → 双扫。
- 通道切换：VAC123_VBATD 归 0 → RELAY_OFF 本通道 → 下一通道 SetOn。
- 整体下电（三步）：VAC123_VBATD→0、VBAT→0 → delay 200us → VAC/VBAT/NTC2 统一 RELAY_OFF。

## 5. 测量与判定
- `rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 2.95, 3.45, 400/200, 10, 2.5, TRIG_RISING, …)` 与降扫各一次 → rise/fall。
- FOR_EACH_VALID_SITE 内算 `hys=(rise−fall)*1e3`（mV）；VACx_Rise/Fall/Hys 共 9 参数 SetTestResult；判定在 spec 层。

## 6. 一句话适用场景
N 路同构比较器/阈值检测（GD present、多通道 PRST）或静态 FV-MV 项目搭框架时：抄本文件的"逐块复制 + 通道干净切换 + 三步下电"骨架。
