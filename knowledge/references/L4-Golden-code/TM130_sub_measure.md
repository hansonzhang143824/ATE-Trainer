# TM130_sub_measure 要点总结（Trim sub · VBG 简单档落地实例）

> 源文件：`L4-Golden-code/TM130_sub_measure.cpp`（34 行）｜索引登记：Trim（VBG·简单）配套 sub —— measure_HP_VBG（AMUX MV）

## 1. 参数类型
- Trim sub 落地实例（VBG 电压基准 trim，简单档）：即 sub-measure-template **模式 A（普通 MV 单源表直测）** 的现实代码。
- 与 TM623_sub_measure.cpp（模式 B 实例）对照：同签名同节奏，差异仅在 VBG 无需大电流/差分 → 简单档 sub 的完整增量视图。

## 2. 角色抽象（精髓）
- **Trim 值角色**：`trim_reg.trim("bandgap")` + `assy("EFUSE_REG_F0")`（4 位，step0~15，**单封装** → 只用 working_value1）。
- **被测电压观测角色**：Bandgap 输出经内部 mux（ATEST0）到 **AMUX_FOVI**，FI=0 下 MV 读取 = "内部基准电压引出观测"的标准映射；下一项目若被测信号也 mux 到 AMUX/DTEST，直接按此角色替换。
- 寄存器配置由 test.cpp 预配（0x56=0x62, 0x67=0x0A, 0x68=0x30），sub 层不再重复配置。
- 简单档 = 仅 AMUX 一路观测；若被测信号需差分回读（如 CS Gain），参考 TM623 的 AMUX−NTC 双路 sub。

## 3. 关键结构/特殊点
- 签名 `(TRIM_NODE*, TREG_MEASURE_FLAG, double *results)` 与模板模式 A 逐字一致 → 模板的直接实例，可当"模式 A 如何填真实寄存器/源表"的样例。
- 每步节奏：读 working（PRE/POST + BURNNED 先 copy_read_to_work）→ `dcm.I2CWriteData(0xF0)` → delay 2ms → `AMUX_FOVI.MeasureVI(50, 5)` → 取 MVRET。
- 无 FPVI / 无浮动源 / 无 BST → 简单档特征：1 个源表 + 1 个 EFUSE 寄存器即完成测量。
- 采样参数 `MeasureVI(50, 5)` 与模板模式 A 完全一致；无大电流场景，故不需要 FPVI/SetClamp。

## 4. 上电/下电时序
- sub 不含上下电；由 `TM130_Trim_VBG` 主函数在 execute 前后负责（K30_VBAT_Cap + VBAT 4.2V，见 TM130_Trim_VBG.md）。

## 5. 测量与判定
- `AMUX_FOVI.MeasureVI(50, 5)` → `GetMeasResult(site, MVRET)` 填入 results[site]（VBG 电压，mV 量级）。
- 步进扫描与 target 判定交给 execute 框架。
- 单步开销极小（一次 MV、无 ramp/无大电流稳定等待），适合 16 步 × 多 site 的快速逐点扫描。

## 6. 一句话适用场景
"单源表 + 单 EFUSE 寄存器"类电压 Trim（VBG/基准电压）的 measure 函数直接照抄本文件。
