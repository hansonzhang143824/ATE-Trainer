// =============================================================================
// relay.h - DALI project CBIT relay definitions
// Source: CBIT表-DALI.xlsx + SCH-DALI.NET
// Mode: cbit-ctreate-step
// Date: 2026-07-28
// =============================================================================

#ifndef RELAY_H
#define RELAY_H

// =============================================================================
// 1. Single-Point Relay Definitions
//    Rule: strip _Sx/_SxSy suffix; merge F/S dual-coil (KELVIN keeps _FS)
//    S34_CBITn -> n (0~127), S36_CBITn -> n+128 (128~255)
// =============================================================================

// 1.1 MOS SPST (TLP3412, per-Site _S1~_S8)
#define K1_COMP_AMP                         1      // S34_CBIT1
#define K6_VBUS_LP                          6      // S34_CBIT6
#define K9_COMP_SVLP1                       9      // S34_CBIT9
#define K10_COMP_SVLP2                      10     // S34_CBIT10
#define K11_VBUS_SVLP                       11     // S34_CBIT11
#define K12_VBAT_SVLP                       12     // S34_CBIT12
#define K14_VAC1_P2P                        14     // S34_CBIT14
#define K15_VAC2_P2P                        15     // S34_CBIT15
#define K16_VAC3_P2P                        16     // S34_CBIT16
#define K22_ACDRV1                          22     // S34_CBIT22
#define K23_ACDRV2                          23     // S34_CBIT23
#define K24_ACDRV3                          24     // S34_CBIT24
#define K25_VCC                             25     // S34_CBIT25
#define K26_ACDRV1_P2P                      26     // S34_CBIT26
#define K27_ACDRV2_P2P                      27     // S34_CBIT27
#define K28_ACDRV3_P2P                      28     // S34_CBIT28
#define K34_SCL_PU                          34     // S34_CBIT34
#define K38_KLV1_2_short                    38     // S34_CBIT38
#define K39_KLV1_P2P                        39     // S34_CBIT39
#define K40_KLV2_P2P                        40     // S34_CBIT40
#define K41_BUS_BST                         41     // S34_CBIT41
#define K46_BUS_SW1                         46     // S34_CBIT46
#define K47_BUS_SW1                         47     // S34_CBIT47
#define K53_LG2_P2P                         53     // S34_CBIT53
#define K54_LG1_P2P                         54     // S34_CBIT54
#define K55_HG2_P2P                         55     // S34_CBIT55
#define K56_HG1_P2P                         56     // S34_CBIT56
#define K62_BUS_QON                         62     // S34_CBIT62
#define K63_SDA_PU                          63     // S34_CBIT63
#define K65_nQON_PU                         65     // S34_CBIT65
#define K66_TMU_nQON                        66     // S34_CBIT66
#define K68_VCP_F                           68     // S34_CBIT68
#define K69_PB5_F                           69     // S34_CBIT69
#define K70_VAC_F                           70     // S34_CBIT70
#define K71_KLV_F                           71     // S34_CBIT71
#define K72_PA5_F                           72     // S34_CBIT72
#define K73_VCN_F                           73     // S34_CBIT73
#define K77_VAC_S                           77     // S34_CBIT77
#define K78_PB5_S                           78     // S34_CBIT78
#define K79_KLV_S                           79     // S34_CBIT79
#define K80_PA5_S                           80     // S34_CBIT80
#define K81_AMPOUT_QVM                      81     // S34_CBIT81
#define K86_KELVIN0_FS                      86     // S34_CBIT86
#define K92_AGND_F2S                        92     // S34_CBIT92
#define K94_BUS_PC8                         94     // S34_CBIT94
#define K96_BUS_CC1                         96     // S34_CBIT96
#define K101_BUS_PA0                        101    // S34_CBIT101
#define K103_PA0_PU                         103    // S34_CBIT103
#define K104_BUS_PD5                        104    // S34_CBIT104
#define K106_BUS_PA1                        106    // S34_CBIT106
#define K108_PA1_PU                         108    // S34_CBIT108
#define K111_BUS_PA6                        111    // S34_CBIT111
#define K113_PA6_PU                         113    // S34_CBIT113
#define K116_BUS_PB7                        116    // S34_CBIT116
#define K118_BUS_PA4                        118    // S34_CBIT118
#define K120_BUS_PA7                        120    // S34_CBIT120
#define K122_PA7_PU                         122    // S34_CBIT122
#define K127_U2_PS                          127    // S34_CBIT127
#define K128_PU_PS                          128    // S36_CBIT0
#define K129_Backup                         129    // S36_CBIT1
#define K130_KELVIN1_FS                     130    // S36_CBIT2
#define K136_QVMH_BUS0                      136    // S36_CBIT8
#define K137_QVMH_BUS1                      137    // S36_CBIT9
#define K138_QVML_BUS0                      138    // S36_CBIT10
#define K139_QVML_BUS1                      139    // S36_CBIT11
#define K140_QVML_AGND                      140    // S36_CBIT12
#define K143_DCM_BUS0_H                     143    // S36_CBIT15
#define K144_DCM_BUS1_H                     144    // S36_CBIT16
#define K145_DCM_BUS0_L                     145    // S36_CBIT17
#define K146_DCM_BUS1_L                     146    // S36_CBIT18
#define K_PB0_PB1_OSC                       147    // S36_CBIT19
#define K148_PC4_PD                         148    // S36_CBIT20
#define K149_PA1_PD                         149    // S36_CBIT21
#define K150_PA4_PD                         150    // S36_CBIT22
#define K152_VDM_TMU                        152    // S36_CBIT24
#define K153_PA4                            153    // S36_CBIT25
#define K156_BUS_VCN                        156    // S36_CBIT28
#define K158_AMPOUT                         158    // S36_CBIT30
#define K168_VCP_F                          159    // S36_CBIT31
#define K169_PB5_F                          160    // S36_CBIT32
#define K170_VAC_F                          161    // S36_CBIT33

// 1.2 G6K Dedicated (per-Site _S1~_S8)
#define K3_BUSL_VBUS                        3      // S34_CBIT3
#define K4_DRVH1                            4      // S34_CBIT4
#define K7_BUSH_VBAT                        7      // S34_CBIT7 (2026-08-10 复核修正: K7 实为 High 侧, 原理图改名 BUSH)
#define K8_PD3                              8      // S34_CBIT8
#define K17_BUSL_VAC                        17     // S34_CBIT17
#define K18_VAC3                            18     // S34_CBIT18
#define K19_VAC2                            19     // S34_CBIT19
#define K20_AMUX                            20     // S34_CBIT20
#define K29_BUSL_VCC                        29     // S34_CBIT29
#define K30_BUSH_ACDRV                      30     // S34_CBIT30
#define K31_VMCU                            31     // S34_CBIT31
#define K32_BUSL_SCL                        32     // S34_CBIT32
#define K33_VAC_WL                          33     // S34_CBIT33
#define K35_BUSH_KLV                        35     // S34_CBIT35
#define K36_PGND_WL                         36     // S34_CBIT36
#define K37_KLV2                            37     // S34_CBIT37
#define K42_AMP_PS                          42     // S34_CBIT42
#define K43_BST2                            43     // S34_CBIT43
#define K48_AMP_REF                         48     // S34_CBIT48
#define K49_ACM_SW2                         49     // S34_CBIT49
#define K50_FOVI_SW2                        50     // S34_CBIT50
#define K51_BUSL_LG                         51     // S34_CBIT51
#define K52_LG2                             52     // S34_CBIT52
#define K58_BUSH_VDM                        58     // S34_CBIT58
#define K59_SDA                             59     // S34_CBIT59
#define K60_BUSL_VCP                        60     // S34_CBIT60
#define K61_SW                              61     // S34_CBIT61
#define K64_HG1                             64     // S34_CBIT64
#define K76_ACM_BST                         76     // S34_CBIT76
#define K83_BUSH_PMID                       83     // S34_CBIT83
#define K84_HG2                             84     // S34_CBIT84
#define K88_KELVIN0                         88     // S34_CBIT88
#define K90_PC0_Force                       90     // S34_CBIT90
#define K91_PC0_Sense                       91     // S34_CBIT91
#define K93_AGND2PGND                       93     // S34_CBIT93
#define K95_PC6                             95     // S34_CBIT95
#define K97_Qpoint                          97     // S34_CBIT97
#define K98_PB3                             98     // S34_CBIT98
#define K99_BUSL_PB5                        99     // S34_CBIT99
#define K100_PC4                            100    // S34_CBIT100
#define K102_PC3                            102    // S34_CBIT102
#define K105_CC2                            105    // S34_CBIT105
#define K107_PB1                            107    // S34_CBIT107
#define K109_BUSL_PB0                       109    // S34_CBIT109
#define K110_BST                            110    // S34_CBIT110
#define K112_PC5                            112    // S34_CBIT112
#define K114_BUSL_PA5                       114    // S34_CBIT114
#define K115_PB2                            115    // S34_CBIT115
#define K117_PB6                            117    // S34_CBIT117
#define K119_PB4                            119    // S34_CBIT119
#define K121_PD2                            121    // S34_CBIT121
#define K123_BUSL_PB5                       123    // S34_CBIT123
#define K124_nRST                           124    // S34_CBIT124
#define K125_U34_PS                         125    // S34_CBIT125
#define K126_V1P5_CAP                       126    // S34_CBIT126
#define K132_KELVIN1                        132    // S36_CBIT4
#define K134_PC1_Force                      134    // S36_CBIT6
#define K135_PC1_Sense                      135    // S36_CBIT7
#define K154_BUSH_AMUX                      154    // S36_CBIT26
#define K155_FOVI_PGND                      155    // S36_CBIT27
#define K157_COMP                           157    // S36_CBIT29

// 1.3 G6K Shared (2-Site _S1S2/_S3S4/_S5S6/_S7S8)
#define K0_VCC_Cap                          0      // S34_CBIT0
#define K2_BUF                              2      // S34_CBIT2
#define K5_VBUS_Cap                         5      // S34_CBIT5
#define K13_VBAT_Cap                        13     // S34_CBIT13
#define K21_VAC_Cap                         21     // S34_CBIT21
#define K44_Cap_SW2_BST2                    44     // S34_CBIT44
#define K45_Cap_SW1_BST1                    45     // S34_CBIT45
#define K57_CAP_BST_SW                      57     // S34_CBIT57
#define K74_GAIN1_SEL                       74     // S34_CBIT74
#define K75_GAIN2_SEL                       75     // S34_CBIT75
#define K82_R_CS                            82     // S34_CBIT82
#define K85_CAP_PMID                        85     // S34_CBIT85
#define K87_KELVIN0                         87     // S34_CBIT87
#define K89_KELVIN0                         89     // S34_CBIT89
#define K131_KELVIN1                        131    // S36_CBIT3
#define K133_KELVIN1                        133    // S36_CBIT5
#define K141_QTMU_BUSA                      141    // S36_CBIT13
#define K142_QTMU_BUSB                      142    // S36_CBIT14
#define K151_NC_GND                         151    // S36_CBIT23

// =============================================================================
// 2. Path Relay Definitions
//    Rule1: FPVI/QTMU/QVM -> public node (>3 devices): K_SOURCE_TO_Net
//    Rule2: FPVI/QTMU/QVM -> DUT Pin (port INOUT/OUTPUT): K_SOURCE_TO_PIN
//    Rule3: Other source -> Pin: K_PIN_SOURCE
//    Rule4: Cap/resistor: K_Node_Cap
// =============================================================================

// 2.1 FPVIe -> SPST BUS -> DUT Pin (Rule2, H=High/FH+SH, L=Low/FL+SL)
// BST (FL+SL only): FPVIe_FL_BUS -> K41_BUS_BST -> BST
#define K_FPVIL_TO_BST              41       // = K41_BUS_BST
// SW1 H: FPVIe_FH/SH_BUS -> K46_BUS_SW1 -> SW1
#define K_FPVIH_TO_SW1              46       // = K46_BUS_SW1
// SW1 L: FPVIe_FL/SL_BUS -> K47_BUS_SW1 -> SW1
#define K_FPVIL_TO_SW1              47       // = K47_BUS_SW1
// SW2 H: FPVIe_FH/SH_BUS -> K46 -> K48(默认) -> K49(SetOn) -> SW2
#define K_FPVIH_TO_SW2              46,49    // K46_BUS_SW1 + K49_ACM_SW2
// SW2 L: FPVIe_FL/SL_BUS -> K47 -> K50(SetOn) -> SW2
#define K_FPVIL_TO_SW2              47,50    // K47_BUS_SW1 + K50_FOVI_SW2
// nQON (FH+SH only): FPVIe_FH/SH_BUS -> K62_BUS_QON -> nQON
#define K_FPVIH_TO_QON              62       // = K62_BUS_QON
// PC8 (FL+SL only): FPVIe_FL/SL_BUS -> K94_BUS_PC8 -> PC8
#define K_FPVIL_TO_PC8              94       // = K94_BUS_PC8
// CC1 (FH+SH only): FPVIe_FH/SH_BUS -> K96_BUS_CC1 -> CC1
#define K_FPVIH_TO_CC1              96       // = K96_BUS_CC1
// PA0 (FH+SH only): FPVIe_FH/SH_BUS -> K101_BUS_PA0 -> PA0
#define K_FPVIH_TO_PA0              101      // = K101_BUS_PA0
// PD5 (FL+SL only): FPVIe_FL/SL_BUS -> K104_BUS_PD5 -> PD5
#define K_FPVIL_TO_PD5              104      // = K104_BUS_PD5
// PA1 (FH+SH only): FPVIe_FH/SH_BUS -> K106_BUS_PA1 -> PA1
#define K_FPVIH_TO_PA1              106      // = K106_BUS_PA1
// PA6 (FH+SH only): FPVIe_FH/SH_BUS -> K111_BUS_PA6 -> PA6
#define K_FPVIH_TO_PA6              111      // = K111_BUS_PA6
// PB7 (FH+SH only): FPVIe_FH/SH_BUS -> K116_BUS_PB7 -> PB7
#define K_FPVIH_TO_PB7              116      // = K116_BUS_PB7
// PA4 (FL+SL only): FPVIe_FL/SL_BUS -> K118_BUS_PA4 -> PA4
#define K_FPVIL_TO_PA4              118      // = K118_BUS_PA4
// PA7 (FH+SH only): FPVIe_FH/SH_BUS -> K120_BUS_PA7 -> PA7
#define K_FPVIH_TO_PA7              120      // = K120_BUS_PA7
// VCN (FH+SH only): FPVIe_FH/SH_BUS -> K156_BUS_VCN -> VCN
#define K_FPVIH_TO_VCN              156      // = K156_BUS_VCN

// 2.2 FPVIe -> G6K BUSH/BUSL -> DUT Pin (Rule2, H=BUSH, L=BUSL)
// VBUS (BUSL): FPVIe_FL/SL_BUS -> K3_BUSL_VBUS -> VBUS
#define K_FPVIL_TO_VBUS              3        // = K3_BUSL_VBUS
// VBAT (BUSH): FPVIe_FH/SH_BUS -> K7_BUSH_VBAT -> VBAT  (2026-08-10 复核修正: 原 K_FPVIL_TO_VBAT 极性别名错误, K7 实为 High 侧)
#define K_FPVIH_TO_VBAT              7        // = K7_BUSH_VBAT
// VAC (BUSL): FPVIe_FL/SL_BUS -> K17_BUSL_VAC -> VAC
#define K_FPVIL_TO_VAC               17       // = K17_BUSL_VAC
// VCC (BUSL): FPVIe_FL/SL_BUS -> K29_BUSL_VCC -> VCC
#define K_FPVIL_TO_VCC               29       // = K29_BUSL_VCC
// ACDRV (BUSH): FPVIe_FH/SH_BUS -> K30_BUSH_ACDRV -> ACDRV
#define K_FPVIH_TO_ACDRV             30       // = K30_BUSH_ACDRV
// SCL (BUSL): FPVIe_FL/SL_BUS -> K32_BUSL_SCL -> SCL
#define K_FPVIL_TO_SCL               32       // = K32_BUSL_SCL
// KLV (BUSH): FPVIe_FH/SH_BUS -> K35_BUSH_KLV -> KLV
#define K_FPVIH_TO_KLV               35       // = K35_BUSH_KLV
// LG (BUSL): FPVIe_FL/SL_BUS -> K51_BUSL_LG -> LG
#define K_FPVIL_TO_LG                51       // = K51_BUSL_LG
// LG1 (BUSL): FPVIe_FL/SL_BUS -> K52_LG2(SetOn) -> LG1 (K52 NC 默认连通 LG2, 与 LG1 分时)
#define K_FPVIL_TO_LG1               52       // = K52_LG2
// VDM (BUSH): FPVIe_FH/SH_BUS -> K58_BUSH_VDM -> VDM
#define K_FPVIH_TO_VDM               58       // = K58_BUSH_VDM
// VCP (BUSL): FPVIe_FL/SL_BUS -> K60_BUSL_VCP -> VCP
#define K_FPVIL_TO_VCP               60       // = K60_BUSL_VCP
// PMID (BUSH): FPVIe_FH/SH_BUS -> K83_BUSH_PMID -> PMID
#define K_FPVIH_TO_PMID              83       // = K83_BUSH_PMID
// PB5 path1 (BUSL): FPVIe_FL/SL_BUS -> K99_BUSL_PB5 -> PB5
#define K_FPVIL_TO_PB5_A             99       // = K99_BUSL_PB5
// PB0 (BUSL): FPVIe_FL/SL_BUS -> K109_BUSL_PB0 -> PB0
#define K_FPVIL_TO_PB0               109      // = K109_BUSL_PB0
// PA5 (BUSL): FPVIe_FL/SL_BUS -> K114_BUSL_PA5 -> PA5
#define K_FPVIL_TO_PA5               114      // = K114_BUSL_PA5
// PB5 path2/CH1 (BUSL): FPVIe_FL/SL_BUS (CH1 简化) -> K99_BUSL_PB5 -> PB5  (原 123 错: K123 是 FPVIH High 侧, 2026-08-10 复核修正)
#define K_FPVIL_TO_PB5_B             99       // = K99_BUSL_PB5
// AMUX (BUSH): FPVIe_FH/SH_BUS -> K154_BUSH_AMUX -> AMUX
#define K_FPVIH_TO_AMUX              154      // = K154_BUSH_AMUX

// 2.3 Other Sources -> DUT Pin (Rule3: K_PIN_SOURCE)
// ACM200 -> ACDRV1
#define K_ACDRV1_ACM                 22       // = K22_ACDRV1
// ACM200 -> ACDRV2
#define K_ACDRV2_ACM                 23       // = K23_ACDRV2
// ACM200 -> ACDRV3
#define K_ACDRV3_ACM                 24       // = K24_ACDRV3
// ACM200 -> SW2
#define K_SW2_ACM                    49       // = K49_ACM_SW2
// ACM200 -> BST
#define K_BST_ACM                    76       // = K76_ACM_BST
// ACM200 -> SCL
#define K_SCL_ACM                    32       // = K32_BUSL_SCL
// ACM200 -> SDA
#define K_SDA_ACM                    59       // = K59_SDA
// FOVIe -> SW2
#define K_SW2_FOVI                   50       // = K50_FOVI_SW2
// FOVIe -> PGND
#define K_PGND_FOVI                  155      // = K155_FOVI_PGND
// FOVIe -> VCC
#define K_VCC_FOVI                   25       // = K25_VCC
// QVM -> AMPOUT
#define K_AMP_QVM                    81       // = K81_AMPOUT_QVM
// QTMU -> nQON
#define K_nQON_QTMU                  66       // = K66_TMU_nQON
// TMU -> VDM
#define K_VDM_TMU                    152      // = K152_VDM_TMU

// 2.4 Capacitor/Resistor Paths (Rule4: K_Node_Cap)
// VCC -> Cap2
#define K_VCC_Cap                    0        // = K0_VCC_Cap
// VBUS -> Cap2
#define K_VBUS_Cap                   5        // = K5_VBUS_Cap
// VBAT -> Cap2
#define K_VBAT_Cap                   13       // = K13_VBAT_Cap
// VAC -> Cap2
#define K_VAC_Cap                    21       // = K21_VAC_Cap
// SW2-BST2 cap
#define K_SW2_BST2_Cap               44       // = K44_Cap_SW2_BST2
// SW1-BST1 cap
#define K_SW1_BST1_Cap               45       // = K45_Cap_SW1_BST1
// BST-SW cap
#define K_BST_SW_Cap                 57       // = K57_CAP_BST_SW
// PMID -> Cap2
#define K_PMID_Cap                   85       // = K85_CAP_PMID
// V1P5 -> Cap
#define K_V1P5_Cap                   126      // = K126_V1P5_CAP

// 2.5 Pull-Up Paths
// SCL pull-up
#define K_SCL_PU                     34       // = K34_SCL_PU
// SDA pull-up
#define K_SDA_PU                     63       // = K63_SDA_PU
// nQON pull-up
#define K_nQON_PU                    65       // = K65_nQON_PU
// PA0 pull-up
#define K_PA0_PU                     103      // = K103_PA0_PU
// PA1 pull-up
#define K_PA1_PU                     108      // = K108_PA1_PU
// PA6 pull-up
#define K_PA6_PU                     113      // = K113_PA6_PU
// PA7 pull-up
#define K_PA7_PU                     122      // = K122_PA7_PU

// 2.6 GAIN Select Combinations
#define K_GAIN_20           74     // = K74_GAIN1_SEL
#define K_GAIN_50           75     // = K75_GAIN2_SEL
#define K_GAIN_100          74,75  // K74_GAIN1_SEL + K75_GAIN2_SEL

// 2.7 Kelvin Combinations
#define K_KELVIN0_FS        86     // = K86_KELVIN0_FS (F+S dual-coil)
#define K_KELVIN1_FS        130    // = K130_KELVIN1_FS (F+S dual-coil)

// 2.8 Special: K_PB0_PB1_OSC (K147_PB0_OSC+K147_PB1_OSC, see 1.1)

#endif // RELAY_H