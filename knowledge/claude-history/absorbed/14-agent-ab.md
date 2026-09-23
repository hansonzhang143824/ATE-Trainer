# 吸收记录 #14 — 继电器命名体系调查（relay.h vs StdAfx.h + test.cpp 用法 + path-namer 规则）

- 源文件：`sessions/14-agent-ab.md` ← `~/.claude/projects/subagents/agent-abded62abf8b55d60.jsonl`
- 时间：2026-08-10 11:55→12:00（0.4MB）；subagent 只读调查
- 主题：两套继电器命名体系差异 + test.cpp 实际用法 + cbit-path-namer 命名规则

## 环境关键发现

- **test.cpp 是带二进制头（`TSZ#`）的编码文件**：Bash/grep 沙箱看到 1283 行混淆视图（grep 全空），PowerShell/Read 解码出真实内容 **6962 行**。DLP 加密环境分析必须用 PowerShell/Read。

## SCH-Connect-Map 通路格式（818 条）

- 通路中继用**裸位号** `K30(Relay-ON)`，不带名字；group 头行 `CH0 High -> ACDRV1 [Kelvin] 需闭合: K22,K30`。
- 源表 6 类：FPVIe(491+8)/QTMUe(70+2)/QVMe(76+16)/ACM200(108)/FXVIe_PLUS(45)/DCM(2)。

## test.cpp 继电器用法

- **一律物理名**（StdAfx.h），**0 处**语义通路别名（K_FPVI*/K_*_TO_*/K_*_ACM）；仅 `#include "stdafx.h"`（不包含 relay.h，语义别名编译不过）。
- 唯一方法 `cbite.SetOn(...)`（无 SetOff），以 `-1` 结尾；无继电器显式 `cbite.SetOn(-1)`。
- 实际用到的 11 个宏（全部在 StdAfx.h 有定义）：K13_VBAT_Cap(61次)、K65_nQON_PU(36)、K21_VAC_Cap(20)、K5_VBUS_Cap(7)、K25_ACM1_VCC_F(6)、K31_FOVI2_VMCU(5)、K19_ACM0_VAC2(4)、K18_ACM0_VAC3(3)、K20_ACM0_AMUX(3)、K59_ACM7_SDA(3)、K66_TMU_nQON(2)。
- 裸 K 号（K4/K8/K59/K61/K64/K66/K67/K95）只在注释里；K67 未在 StdAfx.h 定义（位号空洞）。

## relay.h vs StdAfx.h 命名体系

- **relay.h**（规范化）：单点去工位后缀+F/S 合并（K25_VCC、K41_BUS_BST）+ 2.x 通路别名（K_FPVIH_TO_SW1 等，2.1~2.8 段）。CBIT 值：S34_CBITn→0~127、S36_CBITn→n+128。
- **StdAfx.h**（物理名，编译器实际使用）：K0~K170 平铺，保留原始名（K25_ACM1_VCC_F、K88_FPVI0_Sense_FLOAT），F/S 双别名同值。
- gen_cbit_defines --verify 只校验 `K\d+` + 单个整数值（位号值层），物理名可过（同值异名 WARN）、通路别名不校验。

## cbit-path-namer 命名规则（relay.h 2.x 依据）

- 类型2（稀缺源→DUT_PIN）：`K_<源>_TO_<PIN>`；类型1（稀缺源→公共节点）：`K_<源>_TO_<Net>`；类型3（其他源→DUT_PIN）：`K_<PIN>_<源>`。
- 多路径优先级：0=FOS_SNS 对（`K_FPVIH_TO_KLV_FOS_SNS`）→ 1=H/L 分端（`K_FPVIH_TO_SW2`）→ 2=途经源不同（`K_FPVI_TO_SW2_ACM`）→ 3=A/B/C 后缀。铁律：优先级不可跳过；#define 值=via_relays CBIT 逗号分隔；via_relays 空→不定义。

## 交叉引用

- 与 #13（gen_cbit_defines/gen_paths）同一调查批；两套命名体系是 verify/生成脚本的"权威分层"（值层 vs 名层 vs 通路层）；test.cpp 用物理名 = #11 verify_relay_trace 用 StdAfx.h 物理名做权威的原因。
