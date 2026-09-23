# TM130_Trim_VBG 要点总结（Trim · VBG 简单档主流程，16 steps）

> 源文件：`L4-Golden-code/TM130_Trim_VBG.cpp`（66 行）｜索引登记：**已确认** —— 电压基准 VBG trim，16 steps，无 FPVI/无浮动源/无 BST = 简单 Trim 标准模板

## 1. 参数类型
- **Trim（VBG 电压基准，简单档）**：无 FPVI、无浮动源、无 BST；关联 Trim 规则。
- DFT 对齐：`vset[vbat,4.2]`，Check: AMUX MV；treg: `"bandgap"`（4 位，step0~step15，16 步）。

## 2. 角色抽象（精髓）
- **被测结构角色**：Bandgap 输出经 ATEST0（mux=12）+ D2A_OVRD（OVRD_VALUE=3）内部送到 **AMUX_FOVI** 观测；无外部功率管/无台阶结构需要搭。
- **供电角色**：仅 K30_VBAT_Cap（VBAT Cap2，MV 模式直接 ON）；AMUX_FOVI Default 直连、无需额外继电器 —— 继电器最少化的基线案例。
- **Trim 值角色**：`trim_reg.trim("bandgap")` → execute() 每步回调 `measure_HP_VBG` 逐 site 写 EFUSE_REG_F0。
- 下一项目：被测电压同样经 AMUX/DTEST 观测的 Trim（基准/分压点），把 bandgap 映射为新信号、F0 映射为新 EFUSE 寄存器即可。

## 3. 关键结构/特殊点
- **简单 Trim 标准模板特征**（与 TM623 复杂档对照的基线）：继电器仅 K30_VBAT_Cap 1 个、电源仅 VBAT 4.2V 1 路、无台阶/BST/FPVI —— "复杂档 = 本模板 + FPVI 大电流 + BST 台阶 + 差分观测"。
- 参数族完整规范：PARAM_step0~15（每步一个参数）+ PARAM_pre_value/pre_bit/post_bit/updated/guessed/target/post_value/post_rt（Trim 通用参数命名，写新 Trim 项目直接复用这套名字）。
- Bandgap 稳定：delay 2ms；0x56/0x67/0x68 配 EN_ATEST0=1、ATEST0_MUX=12、D2A_OVRD_SEL=10、OVRD_VALUE=3。
- 步数由位宽决定：treg 4 位 → step0~15 共 16 步（=2^4）；写参数个数前先按 2^位宽核对（对照 TM623 5 位 → 32 步）。

## 4. 上电/下电时序
- 上电：SetOn(K30_VBAT_Cap) → delay 3ms → VBAT_ACM FV=4.2V（ACM200_10V/100mA）→ delay 200us。
- 下电：execute 结束后 VBAT 归 0 → delay 1ms → RELAY_OFF（10V/10MA）。

## 5. 测量与判定
- `PARAM_NODE.execute(measure_HP_VBG, spec, funcindex, funclabel, 1, 0, 0, 0)`：框架自动扫 16 步（每步 sub 写 trim + AMUX MV），按 spec 定 target、产出 updated/guessed 等结果参数。
- 判定与 trim 计算全部由 Trim 框架完成，主函数只负责继电器/电源/execute 三件事。

## 6. 一句话适用场景
需要"多步 trim + pre/post 验证"且**无大电流/浮动源要求**的电压基准类 Trim 项 —— 直接作标准模板套用。
