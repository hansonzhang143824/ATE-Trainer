# CBIT 继电器映射表

三源交叉引用：CBIT表 ↔ HIB网表 ↔ StdAfx.h

## 命名约定

| 源 | 格式 | 示例 |
|----|------|------|
| **CBIT表** | `K<编号>[_后缀]` | `K1`, `K11_F`, `K93_GAIN1_SEL` |
| **HIB网表** | `K<编号>_<功能>_<站点/组>` | `K1_PGND2AGND_S1`, `K2_VBAT_Cap_G1` |
| **StdAfx.h** | `K_<功能>` | `K_PGND2AGND`, `K_VBAT_Cap` |

## 命名后缀规则

| 后缀 | 含义 | 示例 |
|------|------|------|
| `_F` / `_S` | G6K 双刀双掷的两个独立线圈（Coil1/Coil2） | `K11_F` / `K11_S` |
| `_G1` | 两个工位共用一个机械继电器 | `K2_VBAT_Cap_G1` |
| `_Sx` | 单工位独占双刀（x=工位号） | `K1_PGND2AGND_S1` |

## CBIT 驱动能力

| 继电器类型 | 1 CBIT 可驱动数量 |
|-----------|:---:|
| 机械 G6K | 8 个 |
| 光耦 TLP3412/G3VM | 16 个 |

## CBIT 表三种分布模式

| 模式 | 继电器 | 含义 |
|------|--------|------|
| Site1-8/Site9-16 分两组 | K1-K7, K15-K34, K39-K40, K43, K45-K46 | 机械继电器，1 CBIT 驱动 8 个 |
| 全 16 站点同一 CBIT | K8-K14, K38, K41, K47-K48, K51-K81, K90-K91, K95, K99 | 光耦继电器，1 CBIT 驱动 16 个 |
| 仅 Site1-8 | K2-K3, K35-K37, K42, K44 | G1 全局共享 |
| 仅 Site1 | K93, K94, K96 | 所有站点信号短接，一个机械继电器 |

## 功能名前缀含义

| 前缀/后缀 | 含义 |
|-----------|------|
| FOS | Force Short（force 端短接） |
| SNS | Sense（sense 端） |
| BUS | FPVI BUS 总线继电器 |
| Cap | 电容继电器 |
| CHG | Charge（充电） |
| DCHG | Discharge（放电） |
| LP | Loop（环路） |
| PC | Probe Card |
| PU | Pull-Up（上拉） |
| SEL | Select（选择） |

## 逐继电器理解清单

### K1 ~ K7
| CBIT | HIB | StdAfx | 类型 | 功能 |
|------|-----|--------|------|------|
| K1 | K1_PGND2AGND_S1 | K_PGND2AGND(0,1) | G6K | PGND↔AGND 连接 |
| K2 | K2_VBAT_Cap_G1 | K_VBAT_Cap(2) | G6K | VBAT Cap 电容 |
| K3 | K3_VBUS_Cap_G1 | K_VBUS_Cap(3) | G6K | VBUS Cap 电容 |
| K4 | K4_BUSL_VBAT_S1 | K_BUSL_VBAT(4,5) | G6K | VBAT BUS 低侧 |
| K5 | K5_BUSH_VBUS_S1 | K_BUSH_VBUS(6,7) | G6K | VBUS BUS 高侧 |
| K6 | K6_BUSL_BST1_S1 | K_BUSL_BST1(8,9) | G6K | BST1 BUS 低侧 |
| K7 | K7_BST_SHARE_S1 | K_BST2_ACM(10,11) | G6K | BST Share 切换 |

### K8 ~ K14 (光耦，全 16 站点同一 CBIT)
| CBIT | HIB | StdAfx | 功能 |
|------|-----|--------|------|
| K8 | K8_VBAT_ST_S1 | K_VBAT_ST(12) | VBAT ST |
| K9 | K9_VBUS_ST_S1 | K_VBUS_ST(13) | VBUS ST |
| K10 | K10_VDRV_Cap_G1 | K_VDRV_Cap(16) | VDRV Cap |
| K11_F | K11_BUS_FL_S1 | — | BUS FL (G6K Coil1) |
| K11_S | K11_BUS_SL_S1 | — | BUS SL (G6K Coil2) |
| K12_F | K12_KLV1_F_S1 | — | KLV1 Coil1 |
| K12_S | K12_KLV1_S_S1 | — | KLV1 Coil2 |
| K13_F | K13_KLV2_F_S1 | — | KLV2 Coil1 |
| K13_S | K13_KLV2_S_S1 | — | KLV2 Coil2 |
| K14_F | K14_KLV3_F_S1 | — | KLV3 Coil1 |
| K14_S | K14_KLV3_S_S1 | — | KLV3 Coil2 |

### K15 ~ K34
| CBIT | HIB | StdAfx | 类型 | 功能 |
|------|-----|--------|------|------|
| K15 | K15_BUSL_VAC_S1 | — | G6K | VAC BUS 低侧 |
| K16 | K16_VAC3_S1 | K_VAC3_ACM(27,28) | G6K | VAC3↔ACM |
| K17 | K17_VAC2_S1 | K_VAC2_ACM(29,30) | G6K | VAC2↔ACM |
| K18 | K18_VBATD_S1 | — | G6K | VBATD |
| K19_F | K19_BUS_FH_S1 | K19_BUSL_PGND(33,34) | G6K | BUS FH (Coil1), CBIT33 |
| K19_S | K19_BUS_SH_S1 | K19_BUSL_PGND(33,34) | G6K | BUS SH (Coil2), CBIT34 |
| K20_F | K20_NTC1_F_S1 | — | G6K | NTC1 Coil1 |
| K20_S | K20_NTC1_S_S1 | — | G6K | NTC1 Coil2 |
| K21_F | K21_VCOMP_F_S1 | K_VCOMP_ACM(37,38) | G6K | VCOMP↔ACM Coil1 |
| K21_S | K21_VCOMP_S_S1 | K_VCOMP_ACM(37,38) | G6K | VCOMP↔ACM Coil2 |
| K22_F | K22_PGND_F_S1 | — | G3VM | PGND Coil1 (光耦) |
| K22_S | K22_PGND_S_S1 | — | G3VM | PGND Coil2 (光耦) |
| K23 | K23_BUSH_IBUSP_S1 | — | G6K | IBUSP BUS 高侧 |
| K24 | K24_HG1_S1 | — | G6K | HG1 |
| K25 | K25_IBATP_S1 / K25_IBUSP_S1 | — | G6K | IBATP/IBUSP |
| K26 | K26_HG2_S1 | — | G6K | HG2 |
| K27 | K27_BUSL_IBUSN_S1 | — | G6K | IBUSN BUS 低侧 |
| K28 | K28_IBUSN_S1 / K28_LG1_S1 | — | G6K | IBUSN/LG1 |
| K29 | K29_IBATN_S1 | — | G6K | IBATN |
| K30 | K30_LG2_S1 | — | G6K | LG2 |
| K31 | K31_BUSL_SW_S1 | — | G6K | SW BUS 低侧 |
| K32 | K32_BUSH_SW_S1 | — | G6K | SW BUS 高侧 |
| K33 | K33_PGND_S1 | K33_PGND(61,62) | G6K | PGND |
| K34 | K34_SW2_S1 / K34_SW_S1 | K_SW2_FOVI(63,64) | G6K | SW2↔FOVI |

### K35 ~ K45
| CBIT | HIB | StdAfx | 功能 |
|------|-----|--------|------|
| K35 | K35_SW1_BST1_G1 | K_BST1_SW1_Cap(65) | SW1/BST1 Cap (G1) |
| K36 | K36_SW2_BST2_G1 | K_BST2_SW2_Cap(66) | SW2/BST2 Cap (G1) |
| K37 | K37_VCC_Cap_G1 | K_VCC_Cap(67) | VCC Cap (G1) |
| K38 | K38_VAC_Cap_G1 | K_VAC_Cap(68) | VAC Cap |
| K39 | K39_AMON_BUF_S1 | K39_AMON_BUF(69,70) | AMON Buffer (BUS) |
| K40 | K40_NTC1_BUF_S1 | K40_NTC_BUF(71,72) | NTC1 Buffer (BUS) |
| K41_F | K41_KELVIN_F_S1 | K41_KLV_FS(74,75) | Kelvin Coil1 (BUS) |
| K41_S | K41_KELVIN_S_S1 | K41_KLV_FS(74,75) | Kelvin Coil2 (BUS) |
| K42 | K42_KELVIN_G1 | K42_KLVIN(76) | Kelvin (G1) |
| K43 | K43_KELVIN_S1 | K43_KLVIN(77,78) | Kelvin |
| K44 | K44_KELVIN_G1 | K44_KLVIN(79) | Kelvin (G1) |
| K45 | K45_SHARE_S1 | K45_SHARE(80,81) | Share 切换 |

### K46 ~ K58
| CBIT | HIB | StdAfx | 功能 |
|------|-----|--------|------|
| K46_PC | K46_PC_S1 | K46_PC(82,83) | Probe Card 通路切换 |
| K47_F | K47_VBUSD_F_S1 | — | VBUSD Coil1 |
| K47_S | K47_VBUSD_S_S1 | — | VBUSD Coil2 |
| K48_F | K48_SDA_F_S1 | K_SDA_ACM(121,122) | SDA↔ACM Coil1 |
| K48_S | K48_SDA_S_S1 | K_SDA_ACM(121,122) | SDA↔ACM Coil2 |
| K51 | K51_ACDRV1_S1 | K_ACDRV1_ACM(89) | ACDRV1↔ACM |
| K52 | K52_ACDRV2_S1 | K_ACDRV2_ACM(90) | ACDRV2↔ACM |
| K53 | K53_ACDRV3_S1 | K_ACDRV3_ACM(91) | ACDRV3↔ACM |
| K54 | K54_SCL_S1 | K_SCL_ACM(92) | SCL↔ACM |
| K55 | K55_BU_PS_S1 | K55_BU_PS(93) | BU Power Supply |
| K56 | K56_BO_PS_S1 | K56_BO_PS(94) | BO Power Supply |
| K57 | K57_AMPOUT_S1 | K57_AMP_QVM(95,96) | AMP 输出↔QVM 测量 |
| K58 | K58_SDA_PU_S1 | K_SDA_PU(97) | SDA Pull-Up 上拉 |

### K90 ~ K91 (PGND 光耦选择)
| CBIT | HIB | StdAfx | 类型 | 功能 |
|------|-----|--------|------|------|
| K90 | K90_S1 | K_PGND1_SNS(124) | TLP3412 | PGND 公共端↔PGND1（光耦） |
| K91 | K91_S1 | K_PGND2_SNS(125) | TLP3412 | PGND 公共端↔PGND2（光耦） |

K65(PGND_SNS) = PGND1 和 PGND2 的公共节点，K90/K91 分别选通到具体 PGNDx。

### PGND 命名规则
**未写编号的 PGND = PGND1。** 即：
- `K_PGND_FOS` = PGND1 Force Short
- `K_PGND1_SNS` = PGND1 Sense
- `K33_PGND` = PGND1 通道
- `K_AGND_FS` = AGND↔PGND1 连接

仅明确写 PGND2 的才是 PGND2：`K_PGND2_SNS` / `K_PGND2AGND`。
| CBIT | HIB | StdAfx | 功能 |
|------|-----|--------|------|
| K59 | K59_PGND_FOS_S1 | K_PGND_FOS(98) | PGND Force Short |
| K60 | K60_VAC_FOS_S1 | K_VAC1_FOS(99) | VAC Force Short |
| K61 | K61_ISNSN_FOS_S1 | K_ISNSN_FOS_RCS(100) | ISNSN Force Short |
| K62 | K62_ISNSP_FOS_S1 | K_ISNSP_FOS_RCS(101) | ISNSP Force Short |
| K63 | K63_KLV_FOS_S1 | K_KLV_FOS(102) | KLV Force Short |
| K64 | K64_SW_FOS_S1 | K_SW1_FOS(103) | SW Force Short |
| K65 | K65_PGND_SNS_S1 | K_PGND1_SNS(124) | PGND Sense |
| K66 | K66_VAC_SNS_S1 | K_VAC_SNS(105) | VAC Sense |
| K67 | K67_IBUSN_SNS_S1 | K_IBUSN_SNS(106) | IBUSN Sense |
| K68 | K68_IBATN_SNS_S1 | K_IBATN_SNS(107) | IBATN Sense |
| K69 | K69_IBATP_SNS_S1 | K_IBATP_SNS(108) | IBATP Sense |
| K70 | K70_IBUSP_SNS_S1 | K_IBUSP_SNS(109) | IBUSP Sense |
| K71 | K71_KLV_SNS_S1 | K_KLV_SNS(110) | KLV Sense |
| K72 | K72_SW1_SNS_S1 | K_SW1_SNS(111) | SW1 Sense |
| K73 | K73_VCOMP_S1 | K_VCOMP_U2(112) | VCOMP↔U2 运放输入 |
| K74 | K74_ISNSP_S1 | K_ISNSP_FOS_LP(113) | ISNSP Loop |
| K75 | K75_ISNSN_S1 | K_ISNSN_FOS_LP(114) | ISNSN Loop |
| K76 | K76_VBUS_LP_S1 | K_VBUSD_DCHG(115) | VBUS 放电 |
| K77 | K77_VBAT_LP_S1 | K_VBATD_LP(116) | VBAT Loop 环路 |
| K78 | K78_VCOMP_S1 | K_VCOMP_U3(117) | VCOMP↔U3 运放输入 |
| K79 | K79_VBUS_LP_S1 | K_VBUSD_CHG(118) | VBUS 充电 |
| K80 | K80_AGND_FS_S1 | K_AGND_FS(119) | AGND Force Short |
| K81 | K81_RPN_S1 | K_RSNS_2OHM(120) | 2Ω 采样电阻 (R-P-N) |

### GAIN 和 其他
| CBIT | HIB | StdAfx | 功能 |
|------|-----|--------|------|
| K93 | K93_GAIN1_SEL | K_GAIN_20(85) / K_GAIN_100(85,86) | 运放增益档位选择 1 |
| K94 | K94_GAIN2_SEL | K_GAIN_50(86) / K_GAIN_100(85,86) | 运放增益档位选择 2 |
| K95 | K95_INT_S1 | K_INT_ACM(87) | INT↔ACM |
| K96 | K96_U1_PS | K_U1_PS(88) | U1 Power Supply |
| K99 | K99_1K_S1 | K_QP_1K(123) | QP 点接入 1kΩ 电阻 |

### GAIN 档位组合
| 档位 | K93(GAIN1) | K94(GAIN2) | StdAfx define |
|------|:---:|:---:|------|
| 10x | OFF | OFF | K_GAIN_10(126) |
| 20x | ON | OFF | K_GAIN_20(85) |
| 50x | OFF | ON | K_GAIN_50(86) |
| 100x | ON | ON | K_GAIN_100(85,86) |

### 组合别名
| StdAfx define | 实际对应 |
|---------------|---------|
| K_VBATD_ACM(27,28,31,32) | K16_VAC3(27,28) + K18_VBATD(31,32) |
| K_HG1_ACM(43,44) | K24_HG1 |
| K_HG2_ACM(43,44,47,48) | K24_HG1 + K26_HG2 |
| K_LG1_ACM(51,52) | K28_LG1 |
| K_LG2_ACM(51,52,55,56) | K28_LG1 + K30_LG2 |
| K_GAIN_100(85,86) | K93 + K94 |
| K_GAIN_20(85) | K93 |
| K_GAIN_50(86) | K94 |
