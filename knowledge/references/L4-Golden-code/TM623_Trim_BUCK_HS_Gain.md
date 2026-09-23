# TM623_Trim_BUCK_HS_Gain 要点总结（Trim · BUCK HS Gain 复杂档主流程，32 steps）

> 源文件：`L4-Golden-code/TM623_Trim_BUCK_HS_Gain.cpp`（137 行）｜索引登记：**已确认** —— BUCK HS 增益 trim，32 steps，FPVI 3A + 浮动源 + BST 台阶上电 = 复杂 Trim 标准模板

## 1. 参数类型
- **Trim（BUCK HS Current Sense Gain，复杂档）**：FPVI 3A 大电流 + 浮动源 + BST 台阶；关联 Trim 规则、FPVIe、大电流规则。
- DFT 对齐：`vset[vbat,5] / vset[pmid,5] / vset[bst2sw,5] / vset[vdrv,5]` + `iset[pmid2sw,3A]`，Check: AMUX−NTC MV；treg: `"buck_hsfet_gain"`（5 位, step0~31，32 步）。

## 2. 角色抽象（精髓）
- **被测结构 = HS FET（C1, PMID↔SW）**：0x59 HSON 导通后 PMID=SW；同一对端点既走 FPVI 3A 电流闭环（K31+K17），又是 CS 增益的激励/感知对象 —— "管两端 = 电流闭环两端 = 激励角色"三合一。
- **差分观测角色**：CS 信号（ATEST1=9）→ AMUX，参考 → NTC；`results = AMUX − NTC`（sub 内完成）。
- **台阶配对 = BST−SW**：BTST_ACM 独立供 BST（台阶只到 BST10/PMID5，比 RDSON 的 20/15 低 —— trim 无需高压差），K18_BST_SW_Cap 稳压差。
- **Trim 值角色**：`trim_reg.trim("buck_hsfet_gain")` 跨 FA/FB 两 EFUSE 寄存器（2 封装 → working_value1+2）。
- 下一项目：大电流 CS Gain Trim 按同角色映射（管两端闭环 / 台阶对 / 差分观测端 / 多寄存器 trim 值）。

## 3. 关键结构/特殊点
- **复杂 Trim 标准模板** = TM130 简单档三段式（继电器/上电/execute）+ FPVI 大电流初始化 + BST 台阶 + 差分 sub —— 与 TM130_Trim_VBG.md 对照即知"复杂档加了什么"。
- 上电台阶 2 级即够：BST5/PMID0 → BST10/PMID5（导通后 SW=PMID=5V，BST−SW=5V ✓）。
- FPVI 三段式在 execute 前预置：FV0 → FI0 → **SetClamp(50,50)**（0.5V compliance）；execute 结束后收尾：FI0 → FV0 → **SetClamp(100,100)**（解除 compliance 限制，防残留）。
- 下电沿用 RDSON 母版纪律：FET 不关、BST 领先 PMID 台阶同步降。

## 4. 上电/下电时序
- SetOn：K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap。
- 上电：FPVI FV0 → VBAT5/VDRV5 → SW0 → PMID/BST 0 → BST5 → PMID5 → BST10(PMID5)；I2C：0x10=0x43、0x58=0x20、0x59=0x01（HS 导通）、0x61=0x0B。
- 下电：FPVI 收尾（含 SetClamp 复位）→ BST5/PMID0（VBAT 归 0）→ VDRV0、BST0、SW0 → 统一 RELAY_OFF（FPVI 最后断）。

## 5. 测量与判定
- `PARAM_NODE.execute(measure_BUCK_HS_CS_GAIN, spec, funcindex, funclabel, 1, 0, 0, 0)`：32 步扫描，每步 sub 写 FA/FB + FPVI 3A + AMUX−NTC 差分 MV。
- target/updated/guessed 由 Trim 框架按差分电压对 trim 步的单调性判定，主函数只管继电器/电源/execute。

## 6. 一句话适用场景
"大电流激励 + 浮动源 + BST 台阶 + 差分回读"的功率管 CS Gain trim —— 复杂档标准模板，直接套用。
