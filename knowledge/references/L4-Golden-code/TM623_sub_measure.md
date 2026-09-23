# TM623_sub_measure 要点总结（Trim sub · BUCK HS CS Gain 复杂档落地实例）

> 源文件：`L4-Golden-code/TM623_sub_measure.cpp`（60 行）｜索引登记：Trim（BUCK 高边增益·复杂）配套 sub —— measure_BUCK_HS_CS_GAIN（大电流 + AMUX−NTC 差分 MV）

## 1. 参数类型
- Trim sub 落地实例（BUCK HS Current Sense Gain，复杂档）：即 sub-measure-template **模式 B（大电流 + AMUX−NTC 差分）** 的现实代码。

## 2. 角色抽象（精髓）
- **Trim 值角色（2 封装）**：`trim_reg.trim("buck_hsfet_gain")`（5 位, step0~31）**跨 2 个 EFUSE 寄存器**：bit0~1 在 EFUSE_REG_FA、bit2~4 在 EFUSE_REG_FB → working_value1 + working_value2 都要读/写。
- **差分观测角色对**：AMUX_FOVI（CS 信号端）+ NTC_FOVI（参考端），两路 MV 相减 = 差分电压；下一项目换被测信号端/参考端两个角色即可。
- 被测结构（HS FET 闭环 + 3A 激励）由主函数 TM623_Trim_BUCK_HS_Gain 搭建，sub 只做每步"写 trim + 差分测量"。
- 与 TM130_sub_measure.cpp（模式 A 实例）对照：sub 层增量 = 第二个 EFUSE 寄存器 + FPVI 3A 激励 + AMUX/NTC 双路差分。

## 3. 关键结构/特殊点
- 每步节奏：读 FA/FB working（PRE/POST + BURNNED 先 copy_read_to_work）→ `dcm.I2CWriteData(0xFA)` + `(0xFB)` 两寄存器 → delay 2ms。
- 寄存器配置：0x56=0x04（EN_ATEST1）、0x5A=0x50（ATEST1=9，把 CS 信号引到 AMUX）、0x65=0x04（DIS_NTC_DETECTION_ANALOG=1，关掉 NTC 检测模拟避免干扰）。
- 大电流测量节奏：`FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A)`（10A 量程 ≥ 2×3A）→ delay 2ms 稳定 → `FPVI.MeasureVI(200, 5)` → **立即 FI=0 关断**。
- 差分：`AMUX_FOVI.MeasureVI(200, 5)` + `NTC_FOVI.MeasureVI(200, 5)` → MVRET 相减填 results。
- 差分消共模：两路 MVRET 相减抵消 Sense 路径/引脚共模偏移；两路使用相同 MeasureVI 参数（200,5）保证口径一致。

## 4. 上电/下电时序
- sub 不含上下电；由主函数 execute 前后负责（台阶上电与 FPVI 预置见 TM623_Trim_BUCK_HS_Gain.md）。

## 5. 测量与判定
- 测量值 = AMUX MVRET − NTC MVRET（差分电压，反映 Vcs/Gain 变化）→ results[site]。
- 步进扫描、spec 比较与 target 判定交给 execute 框架（依差分电压对 trim 值的单调性定步）。
- results 直接存差分电压，不做换算；Gain 计算与判定由 Trim 框架按 spec 完成。

## 6. 一句话适用场景
需要"3A 级大电流激励 + 双端差分回读"的 CS Gain / 大电流 Trim 的 measure 函数直接照抄本文件。
