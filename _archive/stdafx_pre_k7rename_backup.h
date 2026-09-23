// stdafx.h : include file for standard system include files,
//  or project specific include files that are used frequently, but
//      are changed infrequently
//

#if !defined(AFX_STDAFX_H__3811CD50_B7B0_42B9_9E73_805A91708537__INCLUDED_)
#define AFX_STDAFX_H__3811CD50_B7B0_42B9_9E73_805A91708537__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000


// Insert your headers here
#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers
#include <windows.h>

#include <assert.h>
#define DUT_API extern "C" __declspec(dllexport)
#include <string>
using namespace std;
#include "usertype.h"
#include "userres.h"
#include "spec.h"
#include "treg.h"
//#include"Shmoo.h"
#ifdef _DEBUG
#define DEBUG_MODE 0
#else
#define DEBUG_MODE 0
#endif
#define ACM_NUM 12
#define FOVI_NUM 4
#define FPVI_NUM_NO_SITE 16
#define FPVI_GP_NUM 2
#define MOS_OS_GP_NUM 2
#define QVM_GP_NUM 2
#define TMU_GP_NUM 2

#define QA 0
#define FT 1
#define CP 1
#define TempChar 2
#define QUAL 3
#define HTOL_Burn 4
#define HTOL_Read 5
#define DEV_ADDR 0xCC
//#define DEV_ADDR 0xD0
#define BURNNED 1
#define FRESH 0
#define TTR  true


extern FXVIe_PLUS SW1_SW2_FXVI;
extern FXVIe_PLUS PMID_HG2_FXVI;
extern FXVIe_PLUS VCC_VMCU_FXVI;
extern FXVIe_PLUS AMUX_PGND_FXVI;
extern FXVIe_PLUS NRST_PB5_FXVI;
extern FXVIe_PLUS VBAT_PD3_FXVI;
extern FXVIe_PLUS V1P5_U34PS_FXVI;
extern FXVIe_PLUS AMPOUT_U2PS_FXVI;
extern ACM200 VAC123_AMUX_ACM;
extern ACM200 ACDRV123_VCC_ACM;
extern ACM200 SCL_VACWL_ACM;
extern ACM200 KLV12_PGNDWL_ACM;
extern ACM200 BST12_U1PS_ACM;
extern ACM200 SW12_U1REF_BST_ACM;
extern ACM200 LG1_LG2_ACM;
extern ACM200 VDM_SDA_ACM;
extern ACM200 VCP_SW_ACM;
extern ACM200 NQON_HG1_ACM;
extern ACM200 VBUS_DRVH1_ACM;
extern ACM200 COMP_VCN_ACM;
extern ACM200 PC8_PC6_ACM;
extern ACM200 CC1_PB3_QPOINT_ACM;
extern ACM200 PB5_PC4_ACM;
extern ACM200 PA0_PC3_ACM;
extern ACM200 PD5_CC2_ACM;
extern ACM200 PA1_PB1_ACM;
extern ACM200 PB0_BST_ACM;
extern ACM200 PA6_PC5_ACM;
extern ACM200 PA5_PB2_ACM;
extern ACM200 PB7_PB6_ACM;
extern ACM200 PA4_PB4_ACM;
extern ACM200 PA7_PD2_ACM;
extern FPVIe FPVI0;
extern FPVIe FPVI1;
extern QVMe QVM_S1;
extern QVMe QVM_S2;
extern QVMe QVM_S3;
extern QVMe QVM_S4;
extern QVMe QVM_S5;
extern QVMe QVM_S6;
extern QVMe QVM_S7;
extern QVMe QVM_S8;
extern QTMUe QTMU_S1;
extern QTMUe QTMU_S2;
extern QTMUe QTMU_S3;
extern QTMUe QTMU_S4;
extern QTMUe QTMU_S5;
extern QTMUe QTMU_S6;
extern QTMUe QTMU_S7;
extern QTMUe QTMU_S8;
extern  ACM200 ACM_GRP;
extern  FXVIe_PLUS FXVI_GRP;
extern  QTMUe QTMU_GP;
extern  QVMe QVM_GP;
extern  FPVIe FPVI_GP;

extern int TEST_FLOW;
extern int USER_MODE ;


extern DCM dcm;
extern CBITe cbite;
extern TREG trim_reg;
extern SPEC spec;


//
extern int offfpvi;
extern int onfpvi;
extern int keepon_fpvi;
extern DWORD g_last_valid_fpvi;

// SERIAL for active site
extern int globalsite;
extern BYTE sitesta[SITE_NUM];
extern ULONG ulWriteData[SITE_NUM];
extern int nReadData[SITE_NUM];

inline int MSiteStat(int treg_site)
{
	BYTE treg_stat[SITE_NUM] = { 0 };
	int a;
	a = STSGetSiteStatus(treg_stat, SITE_NUM);
	return (int)treg_stat[treg_site];
}

#define FOR_EACH_VALID_SITE(site) for (int site = 0; site < SITE_NUM; site++) if (MSiteStat(site))
#define FOR_EACH_SITE(site) for (int site = 0; site < SITE_NUM; site++)
#define SITE globalsite
#define SERIAL \
	StsGetSiteStatus(sitesta, SITE_NUM);  for (globalsite = 0; globalsite < SITE_NUM; globalsite++)  if (sitesta[globalsite])

#define SERIAL_GP_FPVI StsGetSiteStatus(sitesta, SITE_NUM); for(globalsite=0;globalsite<SITE_NUM;globalsite++)  if(sitesta[globalsite]) if ((gp_no==0&&SITE==0) || (gp_no==0&&SITE==2) || (gp_no==0&&SITE==4) || (gp_no==0&&SITE==6) ||(gp_no==0&&SITE==8) || (gp_no==0&&SITE==10) || (gp_no==0&&SITE==12) || (gp_no==0&&SITE==14) ||(gp_no==1&&SITE==1) || (gp_no==1&&SITE==3) || (gp_no==1&&SITE==5) || (gp_no==1&&SITE==7)|| (gp_no==1&&SITE==9) || (gp_no==1&&SITE==11) || (gp_no==1&&SITE==13) || (gp_no==1&&SITE==15))
#define SERIAL_GP_FPVI_QVM StsGetSiteStatus(sitesta, SITE_NUM); for(globalsite=0;globalsite<SITE_NUM;globalsite++)  if(sitesta[globalsite]) if ((mos_os_gp_no==0&&SITE==0) || (mos_os_gp_no==0&&SITE==2) || (mos_os_gp_no==0&&SITE==4) || (mos_os_gp_no==0&&SITE==6) ||(mos_os_gp_no==0&&SITE==8) || (mos_os_gp_no==0&&SITE==10) || (mos_os_gp_no==0&&SITE==12) || (mos_os_gp_no==0&&SITE==14) ||(mos_os_gp_no==1&&SITE==1) || (mos_os_gp_no==1&&SITE==3) || (mos_os_gp_no==1&&SITE==5) || (mos_os_gp_no==1&&SITE==7)|| (mos_os_gp_no==1&&SITE==9) || (mos_os_gp_no==1&&SITE==11) || (mos_os_gp_no==1&&SITE==13) || (mos_os_gp_no==1&&SITE==15))
#define SERIAL_GP_QVM StsGetSiteStatus(sitesta, SITE_NUM); for(globalsite=0;globalsite<SITE_NUM;globalsite++)  if(sitesta[globalsite]) if ((gp_no==0&&SITE==0) || (gp_no==0&&SITE==2) || (gp_no==0&&SITE==4) || (gp_no==0&&SITE==6) ||(gp_no==0&&SITE==8) || (gp_no==0&&SITE==10) || (gp_no==0&&SITE==12) || (gp_no==0&&SITE==14) ||(gp_no==1&&SITE==1) || (gp_no==1&&SITE==3) || (gp_no==1&&SITE==5) || (gp_no==1&&SITE==7)|| (gp_no==1&&SITE==9) || (gp_no==1&&SITE==11) || (gp_no==1&&SITE==13) || (gp_no==1&&SITE==15))
#define SERIAL_GP_TMU StsGetSiteStatus(sitesta, SITE_NUM); for(globalsite=0;globalsite<SITE_NUM;globalsite++)  if(sitesta[globalsite]) if ((SITE == gp_no * 4) || (SITE == gp_no * 4 + 1) || (SITE == gp_no * 4 + 2) || (SITE == gp_no * 4 + 3) || (SITE == gp_no * 4 + 8) || (SITE == gp_no * 4 + 9) || (SITE == gp_no * 4 + 10) || (SITE == gp_no * 4 + 11))
//#define SERIAL for(globalsite=0;globalsite<SITE_NUM;globalsite++) 
#define SERIAL_ALL for(globalsite=0;globalsite<SITE_NUM;globalsite++) 


#define	K0_VCC_Cap	0
#define	K1_COMP_AMP3	1
#define	K2_AMP_QVM	2
#define	K3_BUSL0_VBUS	3
#define	K4_ACM10_DRVH1	4
#define	K5_VBUS_Cap	5
#define	K6_VBUS_LP	6
#define	K7_BUSL0_VBAT	7
#define	K8_FOVI5_PD3	8
#define	K9_COMP_SVLP1	9
#define	K10_COMP_SVLP2	10
#define	K11_VBUS_SVLP	11
#define	K12_VBAT_SVLP	12
#define	K13_VBAT_Cap	13
#define	K14_VAC1_P2P	14
#define	K15_VAC2_P2P	15
#define	K16_VAC3_P2P	16
#define	K17_BUSL_VAC	17
#define	K18_ACM0_VAC3	18
#define	K19_ACM0_VAC2	19
#define	K20_ACM0_AMUX	20
#define	K21_VAC_Cap	21
#define	K22_ACM1_ACDRV1_F	22
#define	K22_ACM1_ACDRV1_S	22
#define	K23_ACM1_ACDRV2_F	23
#define	K23_ACM1_ACDRV2_S	23
#define	K24_ACM1_ACDRV3_F	24
#define	K24_ACM1_ACDRV3_S	24
#define	K25_ACM1_VCC_F	25
#define	K25_ACM1_VCC_S	25
#define	K26_ACDRV1_P2P	26
#define	K27_ACDRV2_P2P	27
#define	K28_ACDRV3_P2P	28
#define	K29_BUSL0_VCC	29
#define	K30_BUSH0_ACDRV	30
#define	K31_FOVI2_VMCU	31
#define	K32_BUSL0_SCL	32
#define	K33_ACM2_VAC_WL	33
#define	K34_SCL_PU	34
#define	K35_BUSH0_KLV	35
#define	K36_ACM3_PGND_WL	36
#define	K37_ACM3_KLV2	37
#define	K38_KLV1_2_short	38
#define	K39_KLV1_P2P	39
#define	K40_KLV2_P2P	40
#define	K41_BUS0_FL_BST	41
#define	K41_BUS0_SL_BST	41
#define	K42_ACM4_AMP_PS	42
#define	K43_ACM4_BST2	43
#define	K44_Cap_SW2_BST2	44
#define	K45_Cap_SW1_BST1	45
#define	K46_BUS0_FH_SW1	46
#define	K46_BUS0_SH_SW1	46
#define	K47_BUS0_FL_SW1	47
#define	K47_BUS0_SL_SW1	47
#define	K48_ACM5_AMP_REF	48
#define	K49_ACM5_SW2	49
#define	K50_FOVI0_SW2	50
#define	K51_BUSL0_LG	51
#define	K52_ACM6_LG2	52
#define	K53_LG2_P2P	53
#define	K54_LG1_P2P	54
#define	K55_HG2_P2P	55
#define	K56_HG1_P2P	56
#define	K57_CAP_BST_SW	57
#define	K58_BUSH0_VDM	58
#define	K59_ACM7_SDA	59
#define	K60_BUSL0_VCP	60
#define	K61_ACM8_SW	61
#define	K62_BUS0_FH_QON	62
#define	K62_BUS0_SH_QON	62
#define	K63_SDA_PU	63
#define	K64_ACM9_HG1	64
#define	K65_nQON_PU	65
#define	K66_TMU_nQON	66
#define	K68_R5M_VCP_F	68
#define	K69_R5M_PB5_F	69
#define	K70_R5M_VAC_F	70
#define	K71_CS_KLV_F	71
#define	K72_CS_PA5_F	72
#define	K73_CS_VCN_F	73
#define	K74_GAIN1_SEL	74
#define	K75_GAIN2_SEL	75
#define	K76_ACM_BST	76
#define	K77_VAC_S_AMP	77
#define	K78_PB5_S_AMP	78
#define	K79_KLV_S_AMP	79
#define	K80_PA5_S_AMP	80
#define	K81_AMP1OUT_QVM	81
#define	K82_SEL_R_CS	82
#define	K83_BUSH0_PMID	83
#define	K84_FOVI1_HG2	84
#define	K85_CAP_PMID	85
#define	K86_FPVI0_H_SHORT	86
#define	K86_FPVI0_L_SHORT	86
#define	K87_FPVI0_FH_SL_SHORT	87
#define	K88_FPVI0_Sense_FLOAT	88
#define	K89_FPVI0_FL_SH_SHORT	89
#define	K90_FPVI0_PC_Force	90
#define	K91_FPVI0_PC_Sense	91
#define	K92_AGND_F2S_SHORT	92
#define	K93_AGND2PGND_SHORT	93
#define	K94_BUS1_FL_PC8	94
#define	K94_BUS1_SL_PC8	94
#define	K95_ACM12_PC6	95
#define	K96_BUS1_FH_CC1	96
#define	K96_BUS1_SH_CC1	96
#define	K97_ACM13_Qpoint	97
#define	K98_ACM13_PB3	98
#define	K99_BUSL1_PB5	99
#define	K100_ACM14_PC4	100
#define	K101_BUS1_FH_PA0	101
#define	K101_BUS1_SH_PA0	101
#define	K102_ACM15_PC3	102
#define	K103_PA0_PU	103
#define	K104_BUS1_FL_PD5	104
#define	K104_BUS1_SL_PD5	104
#define	K105_ACM16_CC2	105
#define	K106_BUS1_FH_PA1	106
#define	K106_BUS1_SH_PA1	106
#define	K107_ACM17_PB1	107
#define	K108_PA1_PU	108
#define	K109_BUSL1_PB0	109
#define	K110_ACM18_BST	110
#define	K111_BUS1_FH_PA6	111
#define	K111_BUS1_SH_PA6	111
#define	K112_ACM19_PC5	112
#define	K113_PA6_PU	113
#define	K114_BUSL1_PA5	114
#define	K115_ACM20_PB2	115
#define	K116_BUS1_FH_PB7	116
#define	K116_BUS1_SH_PB7	116
#define	K117_ACM21_PB6	117
#define	K118_BUS1_FL_PA4	118
#define	K118_BUS1_SL_PA4	118
#define	K119_ACM22_PB4	119
#define	K120_BUS1_FH_PA7	120
#define	K120_BUS1_SH_PA7	120
#define	K121_ACM23_PD2	121
#define	K122_PA7_PU	122
#define	K123_BUSL1_PB5	123
#define	K124_FOVI4_nRST	124
#define	K125_FOVI6_U34_PS	125
#define	K126_V1P5_CAP	126
#define	K127_FOVI7_U2_PS	127
#define	K128_FOVI7_PU_PS	128
#define	K129_FOVI7_Backup	129
#define	K130_FPVI1_H_SHORT	130
#define	K130_FPVI1_L_SHORT	130
#define	K131_FPVI1_FH_SL_SHORT	131
#define	K132_FPVI1_Sense_FLOAT	132
#define	K133_FPVI1_FL_SH_SHORT	133
#define	K134_FPVI1_PC_Force	134
#define	K135_FPVI1_PC_Sense	135
#define	K136_QVMH_BUS0	136
#define	K137_QVMH_BUS1	137
#define	K138_QVML_BUS0	138
#define	K139_QVML_BUS1	139
#define	K140_QVML_AGND	140
#define	K141_QTMUA_BUS0H	141
#define	K142_QTMUB_BUS0L	142
#define	K143_DCM_BUS0_H	143
#define	K144_DCM_BUS1_H	144
#define	K145_DCM_BUS0_L	145
#define	K146_DCM_BUS1_L	146
#define	K147_PB0_OSC	147
#define	K147_PB1_OSC	147
#define	K148_PC4_PD	148
#define	K149_PA1_PD	149
#define	K150_PA4_PD	150
#define	K151_NC_GND	151
#define	K152_VDM_TMU	152
#define	K153_PA4_AMP3	153
#define	K154_BUSH0_AMUX	154
#define	K155_FOVI3_PGND	155
#define	K156_BUS0_FH_VCN	156
#define	K156_BUS0_SH_VCN	156
#define	K157_ACM11_COMP	157
#define	K158_FOVI7_AMPOUT	158
#define	K168_R100M_VCP_F	168
#define	K169_R100M_PB5_F	169
#define	K170_R100M_VAC_F	170









extern "C" int USERRES_API STSMaskTHBConfigCheck(bool maskFlag);///EEROM Ð´Èë³É¹¦ÐèÉ¾³ý


//8200 transefer to 8300
extern bool DO_TRIM;
extern bool QC;
extern int g_x_coords[SITE_NUM], g_y_coords[SITE_NUM];
extern char waferid[64];
#define GLOBAL
GLOBAL void G_GetXYCoordinate();

// TODO: reference additional headers your program requires here

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

// ==== PATH_RELAY_START (gen_path_defines.py) ====
// Path Relay Definitions - Í¨Â·¼ÌµçÆ÷ÓïÒå±ðÃû (SetOn only)
//   Êý¾ÝÈ¨Íþ: DALI/SCH-Connect-Map.txt `Ðè±ÕºÏ:` È«Á¿ SetOn ¼¯
//   ÃüÃû¹æÔò: cbit-path-namer.md (FPVIe->K_FPVIH/L_TO_PIN; ÆäËû->K_PIN_SRC; ¶àÂ·¾¶->A/B/C)
//   Éú³É: gen_path_defines.py | 352 defines | !Ìø¹ý 38 | NC-only 31
// ------------------------------------------------------------------------------
// --- FPVIe -> DUT Pin ---
#define K_FPVIH_TO_ACDRV1_A                        22,30                        // FPVIe[H] -> ACDRV1: K22_ACM1_ACDRV1_F + K30_BUSH0_ACDRV
#define K_FPVIH_TO_ACDRV1_B                        143,144,22,26,30,56,62,64    // FPVIe[H] -> ACDRV1: K143_DCM_BUS0_H + K144_DCM_BUS1_H + K22_ACM1_ACDRV1_F + K26_ACDRV1_P2P + K30_BUSH0_ACDRV + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_ACDRV2_A                        23,30                        // FPVIe[H] -> ACDRV2: K23_ACM1_ACDRV2_F + K30_BUSH0_ACDRV
#define K_FPVIH_TO_ACDRV2_B                        143,144,23,27,30,56,62,64    // FPVIe[H] -> ACDRV2: K143_DCM_BUS0_H + K144_DCM_BUS1_H + K23_ACM1_ACDRV2_F + K27_ACDRV2_P2P + K30_BUSH0_ACDRV + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_ACDRV3_A                        24,30                        // FPVIe[H] -> ACDRV3: K24_ACM1_ACDRV3_F + K30_BUSH0_ACDRV
#define K_FPVIH_TO_ACDRV3_B                        143,144,24,28,30,56,62,64    // FPVIe[H] -> ACDRV3: K143_DCM_BUS0_H + K144_DCM_BUS1_H + K24_ACM1_ACDRV3_F + K28_ACDRV3_P2P + K30_BUSH0_ACDRV + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_AGND_A                          136,137,22,26,30,56,62,64    // FPVIe[H] -> AGND: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K22_ACM1_ACDRV1_F + K26_ACDRV1_P2P + K30_BUSH0_ACDRV + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_AGND_B                          154,155,56,62,64,93          // FPVIe[H] -> AGND: K154_BUSH0_AMUX + K155_FOVI3_PGND + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_AMUX_A                          136,137,143,144,154          // FPVIe[H] -> AMUX: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K154_BUSH0_AMUX
#define K_FPVIH_TO_AMUX_B                          154                          // FPVIe[H] -> AMUX: K154_BUSH0_AMUX
#define K_FPVIH_TO_CC1_A                           136,137,143,144,96           // FPVIe[H] -> CC1: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K96_BUS1_FH_CC1
#define K_FPVIH_TO_CC1_B                           96                           // FPVIe[H] -> CC1: K96_BUS1_FH_CC1
#define K_FPVIH_TO_COMP_A                          136,137,143,144,156,157      // FPVIe[H] -> COMP: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K156_BUS0_FH_VCN + K157_ACM11_COMP
#define K_FPVIH_TO_COMP_B                          156,157                      // FPVIe[H] -> COMP: K156_BUS0_FH_VCN + K157_ACM11_COMP
#define K_FPVIH_TO_DMA_PA7_A                       120,136,137,143,144          // FPVIe[H] -> DMA_PA7: K120_BUS1_FH_PA7 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_DMA_PA7_B                       120                          // FPVIe[H] -> DMA_PA7: K120_BUS1_FH_PA7
#define K_FPVIH_TO_HG1_A                           136,137,22,26,30,56,62,64    // FPVIe[H] -> HG1: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K22_ACM1_ACDRV1_F + K26_ACDRV1_P2P + K30_BUSH0_ACDRV + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_HG1_B                           62,64                        // FPVIe[H] -> HG1: K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_FPVIH_TO_HG2_A                           83,84                        // FPVIe[H] -> HG2: K83_BUSH0_PMID + K84_FOVI1_HG2
#define K_FPVIH_TO_HG2_B                           143,144,55,56,62,64,83,84    // FPVIe[H] -> HG2: K143_DCM_BUS0_H + K144_DCM_BUS1_H + K55_HG2_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K83_BUSH0_PMID + K84_FOVI1_HG2
#define K_FPVIH_TO_INT_PA0_A                       101,136,137,143,144          // FPVIe[H] -> INT_PA0: K101_BUS1_FH_PA0 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_INT_PA0_B                       101                          // FPVIe[H] -> INT_PA0: K101_BUS1_FH_PA0
#define K_FPVIH_TO_KLV1_A                          35,38                        // FPVIe[H] -> KLV1: K35_BUSH0_KLV + K38_KLV1_2_short
#define K_FPVIH_TO_KLV1_B                          136,137,154,155,35,39,93     // FPVIe[H] -> KLV1: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K154_BUSH0_AMUX + K155_FOVI3_PGND + K35_BUSH0_KLV + K39_KLV1_P2P + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_KLV2_A                          35,37                        // FPVIe[H] -> KLV2: K35_BUSH0_KLV + K37_ACM3_KLV2
#define K_FPVIH_TO_KLV2_B                          154,155,40,56,62,64,93       // FPVIe[H] -> KLV2: K154_BUSH0_AMUX + K155_FOVI3_PGND + K40_KLV2_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_LG1                             154,155,54,56,62,64,93       // FPVIe[H] -> LG1: K154_BUSH0_AMUX + K155_FOVI3_PGND + K54_LG1_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_LG2                             154,155,53,56,62,64,93       // FPVIe[H] -> LG2: K154_BUSH0_AMUX + K155_FOVI3_PGND + K53_LG2_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_NC                              154,155,56,62,64,93          // FPVIe[H] -> NC: K154_BUSH0_AMUX + K155_FOVI3_PGND + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_PA1_A                           106,136,137,143,144          // FPVIe[H] -> PA1: K106_BUS1_FH_PA1 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PA1_B                           106                          // FPVIe[H] -> PA1: K106_BUS1_FH_PA1
#define K_FPVIH_TO_PA6_PWM2_A                      111,136,137,143,144          // FPVIe[H] -> PA6_PWM2: K111_BUS1_FH_PA6 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PA6_PWM2_B                      111                          // FPVIe[H] -> PA6_PWM2: K111_BUS1_FH_PA6
#define K_FPVIH_TO_PB1_A                           106,107,136,137,143,144      // FPVIe[H] -> PB1: K106_BUS1_FH_PA1 + K107_ACM17_PB1 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PB1_B                           106,107                      // FPVIe[H] -> PB1: K106_BUS1_FH_PA1 + K107_ACM17_PB1
#define K_FPVIH_TO_PB3_A                           136,137,143,144,96,98        // FPVIe[H] -> PB3: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K96_BUS1_FH_CC1 + K98_ACM13_PB3
#define K_FPVIH_TO_PB3_B                           96,98                        // FPVIe[H] -> PB3: K96_BUS1_FH_CC1 + K98_ACM13_PB3
#define K_FPVIH_TO_PB5_A                           123,136,137,143,144          // FPVIe[H] -> PB5: K123_BUSL1_PB5 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PB5_B                           123                          // FPVIe[H] -> PB5: K123_BUSL1_PB5
#define K_FPVIH_TO_PB6_A                           116,117,136,137,143,144      // FPVIe[H] -> PB6: K116_BUS1_FH_PB7 + K117_ACM21_PB6 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PB6_B                           116,117                      // FPVIe[H] -> PB6: K116_BUS1_FH_PB7 + K117_ACM21_PB6
#define K_FPVIH_TO_PB7_A                           116,136,137,143,144          // FPVIe[H] -> PB7: K116_BUS1_FH_PB7 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PB7_B                           116                          // FPVIe[H] -> PB7: K116_BUS1_FH_PB7
#define K_FPVIH_TO_PC3_A                           101,102,136,137,143,144      // FPVIe[H] -> PC3: K101_BUS1_FH_PA0 + K102_ACM15_PC3 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PC3_B                           101,102                      // FPVIe[H] -> PC3: K101_BUS1_FH_PA0 + K102_ACM15_PC3
#define K_FPVIH_TO_PC5_A                           111,112,136,137,143,144      // FPVIe[H] -> PC5: K111_BUS1_FH_PA6 + K112_ACM19_PC5 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PC5_B                           111,112                      // FPVIe[H] -> PC5: K111_BUS1_FH_PA6 + K112_ACM19_PC5
#define K_FPVIH_TO_PD2_A                           120,121,136,137,143,144      // FPVIe[H] -> PD2: K120_BUS1_FH_PA7 + K121_ACM23_PD2 + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_PD2_B                           120,121                      // FPVIe[H] -> PD2: K120_BUS1_FH_PA7 + K121_ACM23_PD2
#define K_FPVIH_TO_PD3_A                           136,137,143,144,7,8          // FPVIe[H] -> PD3: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K7_BUSL0_VBAT + K8_FOVI5_PD3
#define K_FPVIH_TO_PD3_B                           7,8                          // FPVIe[H] -> PD3: K7_BUSL0_VBAT + K8_FOVI5_PD3
#define K_FPVIH_TO_PGND_A                          136,137,154,155,22,26,30,93  // FPVIe[H] -> PGND: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K154_BUSH0_AMUX + K155_FOVI3_PGND + K22_ACM1_ACDRV1_F + K26_ACDRV1_P2P + K30_BUSH0_ACDRV + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_PGND_B                          154,155                      // FPVIe[H] -> PGND: K154_BUSH0_AMUX + K155_FOVI3_PGND
#define K_FPVIH_TO_PGND_WL_A                       35,36                        // FPVIe[H] -> PGND_WL: K35_BUSH0_KLV + K36_ACM3_PGND_WL
#define K_FPVIH_TO_PGND_WL_B                       136,137,143,144,35,36        // FPVIe[H] -> PGND_WL: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K35_BUSH0_KLV + K36_ACM3_PGND_WL
#define K_FPVIH_TO_PMID_A                          83                           // FPVIe[H] -> PMID: K83_BUSH0_PMID
#define K_FPVIH_TO_PMID_B                          136,137,143,144,83           // FPVIe[H] -> PMID: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K83_BUSH0_PMID
#define K_FPVIH_TO_SDA_A                           136,137,143,144,58,59        // FPVIe[H] -> SDA: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K58_BUSH0_VDM + K59_ACM7_SDA
#define K_FPVIH_TO_SDA_B                           58,59                        // FPVIe[H] -> SDA: K58_BUSH0_VDM + K59_ACM7_SDA
#define K_FPVIH_TO_SW1_A                           136,137,143,144,46           // FPVIe[H] -> SW1: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K46_BUS0_FH_SW1
#define K_FPVIH_TO_SW1_B                           46                           // FPVIe[H] -> SW1: K46_BUS0_FH_SW1
#define K_FPVIH_TO_SW2_A                           136,137,143,144,46,49        // FPVIe[H] -> SW2: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K46_BUS0_FH_SW1 + K49_ACM5_SW2
#define K_FPVIH_TO_SW2_B                           46,49                        // FPVIe[H] -> SW2: K46_BUS0_FH_SW1 + K49_ACM5_SW2
#define K_FPVIH_TO_VAC1                            14,154,155,56,62,64,93       // FPVIe[H] -> VAC1: K14_VAC1_P2P + K154_BUSH0_AMUX + K155_FOVI3_PGND + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_VAC2                            15,154,155,56,62,64,93       // FPVIe[H] -> VAC2: K15_VAC2_P2P + K154_BUSH0_AMUX + K155_FOVI3_PGND + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_VAC3                            154,155,16,56,62,64,93       // FPVIe[H] -> VAC3: K154_BUSH0_AMUX + K155_FOVI3_PGND + K16_VAC3_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1 + K93_AGND2PGND_SHORT
#define K_FPVIH_TO_VBAT_A                          136,137,143,144,7            // FPVIe[H] -> VBAT: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K7_BUSL0_VBAT
#define K_FPVIH_TO_VBAT_B                          7                            // FPVIe[H] -> VBAT: K7_BUSL0_VBAT
#define K_FPVIH_TO_VCC_A                           25,30                        // FPVIe[H] -> VCC: K25_ACM1_VCC_F + K30_BUSH0_ACDRV
#define K_FPVIH_TO_VCC_B                           136,137,143,144,25,30        // FPVIe[H] -> VCC: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K25_ACM1_VCC_F + K30_BUSH0_ACDRV
#define K_FPVIH_TO_VCN_A                           136,137,143,144,156          // FPVIe[H] -> VCN: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K156_BUS0_FH_VCN
#define K_FPVIH_TO_VCN_B                           156                          // FPVIe[H] -> VCN: K156_BUS0_FH_VCN
#define K_FPVIH_TO_VDM_A                           136,137,143,144,58           // FPVIe[H] -> VDM: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H + K58_BUSH0_VDM
#define K_FPVIH_TO_VDM_B                           58                           // FPVIe[H] -> VDM: K58_BUSH0_VDM
#define K_FPVIH_TO_nQON_A                          136,137,141,62,66            // FPVIe[H] -> nQON: K136_QVMH_BUS0 + K137_QVMH_BUS1 + K141_QTMUA_BUS0H + K62_BUS0_FH_QON + K66_TMU_nQON
#define K_FPVIH_TO_nQON_B                          62                           // FPVIe[H] -> nQON: K62_BUS0_FH_QON
#define K_FPVIH_TO_nRST_A                          123,124,136,137,143,144      // FPVIe[H] -> nRST: K123_BUSL1_PB5 + K124_FOVI4_nRST + K136_QVMH_BUS0 + K137_QVMH_BUS1 + K143_DCM_BUS0_H + K144_DCM_BUS1_H
#define K_FPVIH_TO_nRST_B                          123,124                      // FPVIe[H] -> nRST: K123_BUSL1_PB5 + K124_FOVI4_nRST
#define K_FPVIL_TO_ACDRV1                          22,25,29                     // FPVIe[L] -> ACDRV1: K22_ACM1_ACDRV1_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_FPVIL_TO_ACDRV2                          23,25,29                     // FPVIe[L] -> ACDRV2: K23_ACM1_ACDRV2_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_FPVIL_TO_ACDRV3                          24,25,29                     // FPVIe[L] -> ACDRV3: K24_ACM1_ACDRV3_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_FPVIL_TO_AGND_A                          138,140,51,53                // FPVIe[L] -> AGND: K138_QVML_BUS0 + K140_QVML_AGND + K51_BUSL0_LG + K53_LG2_P2P
#define K_FPVIL_TO_AGND_B                          139,140,145,146,51,53        // FPVIe[L] -> AGND: K139_QVML_BUS1 + K140_QVML_AGND + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K51_BUSL0_LG + K53_LG2_P2P
#define K_FPVIL_TO_AMUX_A                          17,18,20                     // FPVIe[L] -> AMUX: K17_BUSL_VAC + K18_ACM0_VAC3 + K20_ACM0_AMUX
#define K_FPVIL_TO_AMUX_B                          138,139,145,146,17,18,20     // FPVIe[L] -> AMUX: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K17_BUSL_VAC + K18_ACM0_VAC3 + K20_ACM0_AMUX
#define K_FPVIL_TO_BST1_A                          41                           // FPVIe[L] -> BST1: K41_BUS0_FL_BST
#define K_FPVIL_TO_BST1_B                          138,139,145,146,41           // FPVIe[L] -> BST1: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K41_BUS0_FL_BST
#define K_FPVIL_TO_BST2_A                          41,43                        // FPVIe[L] -> BST2: K41_BUS0_FL_BST + K43_ACM4_BST2
#define K_FPVIL_TO_BST2_B                          138,139,145,146,41,43        // FPVIe[L] -> BST2: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K41_BUS0_FL_BST + K43_ACM4_BST2
#define K_FPVIL_TO_BST_SW_A                        109,110,138,139,60,61        // FPVIe[L] -> BST_SW: K109_BUSL1_PB0 + K110_ACM18_BST + K138_QVML_BUS0 + K139_QVML_BUS1 + K60_BUSL0_VCP + K61_ACM8_SW
#define K_FPVIL_TO_BST_SW_B                        109,110,133,134              // FPVIe[L] -> BST_SW: K109_BUSL1_PB0 + K110_ACM18_BST + K133_FPVI1_FL_SH_SHORT + K134_FPVI1_PC_Force
#define K_FPVIL_TO_CC2_A                           104,105,138,139,145,146      // FPVIe[L] -> CC2: K104_BUS1_FL_PD5 + K105_ACM16_CC2 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_CC2_B                           104,105                      // FPVIe[L] -> CC2: K104_BUS1_FL_PD5 + K105_ACM16_CC2
#define K_FPVIL_TO_DMO_PC6_A                       138,139,145,146,94,95        // FPVIe[L] -> DMO_PC6: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K94_BUS1_FL_PC8 + K95_ACM12_PC6
#define K_FPVIL_TO_DMO_PC6_B                       94,95                        // FPVIe[L] -> DMO_PC6: K94_BUS1_FL_PC8 + K95_ACM12_PC6
#define K_FPVIL_TO_DRVH1_A                         3,4                          // FPVIe[L] -> DRVH1: K3_BUSL0_VBUS + K4_ACM10_DRVH1
#define K_FPVIL_TO_DRVH1_B                         138,139,145,146,3,4          // FPVIe[L] -> DRVH1: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K3_BUSL0_VBUS + K4_ACM10_DRVH1
#define K_FPVIL_TO_HG1                             138,140,51,53,56,92          // FPVIe[L] -> HG1: K138_QVML_BUS0 + K140_QVML_AGND + K51_BUSL0_LG + K53_LG2_P2P + K56_HG1_P2P + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_HG2                             138,140,51,53,55,92          // FPVIe[L] -> HG2: K138_QVML_BUS0 + K140_QVML_AGND + K51_BUSL0_LG + K53_LG2_P2P + K55_HG2_P2P + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_KLV1                            138,140,39,51,53,92          // FPVIe[L] -> KLV1: K138_QVML_BUS0 + K140_QVML_AGND + K39_KLV1_P2P + K51_BUSL0_LG + K53_LG2_P2P + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_KLV2                            138,140,40,51,53,92          // FPVIe[L] -> KLV2: K138_QVML_BUS0 + K140_QVML_AGND + K40_KLV2_P2P + K51_BUSL0_LG + K53_LG2_P2P + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_LG1_A                           51,52                        // FPVIe[L] -> LG1: K51_BUSL0_LG + K52_ACM6_LG2
#define K_FPVIL_TO_LG1_B                           138,139,145,146,51,52        // FPVIe[L] -> LG1: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K51_BUSL0_LG + K52_ACM6_LG2
#define K_FPVIL_TO_LG2_A                           51                           // FPVIe[L] -> LG2: K51_BUSL0_LG
#define K_FPVIL_TO_LG2_B                           138,139,145,146,51           // FPVIe[L] -> LG2: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K51_BUSL0_LG
#define K_FPVIL_TO_NC                              138,140,51,53,92             // FPVIe[L] -> NC: K138_QVML_BUS0 + K140_QVML_AGND + K51_BUSL0_LG + K53_LG2_P2P + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_PA4_A                           118,138,139,145,146          // FPVIe[L] -> PA4: K118_BUS1_FL_PA4 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PA4_B                           118                          // FPVIe[L] -> PA4: K118_BUS1_FL_PA4
#define K_FPVIL_TO_PA5_A                           114,138,139,145,146          // FPVIe[L] -> PA5: K114_BUSL1_PA5 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PA5_B                           114                          // FPVIe[L] -> PA5: K114_BUSL1_PA5
#define K_FPVIL_TO_PB0_PWM1_A                      109,138,139,145,146          // FPVIe[L] -> PB0_PWM1: K109_BUSL1_PB0 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PB0_PWM1_B                      109                          // FPVIe[L] -> PB0_PWM1: K109_BUSL1_PB0
#define K_FPVIL_TO_PB2_A                           114,115,138,139,145,146      // FPVIe[L] -> PB2: K114_BUSL1_PA5 + K115_ACM20_PB2 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PB2_B                           114,115                      // FPVIe[L] -> PB2: K114_BUSL1_PA5 + K115_ACM20_PB2
#define K_FPVIL_TO_PB4_A                           118,119,138,139,145,146      // FPVIe[L] -> PB4: K118_BUS1_FL_PA4 + K119_ACM22_PB4 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PB4_B                           118,119                      // FPVIe[L] -> PB4: K118_BUS1_FL_PA4 + K119_ACM22_PB4
#define K_FPVIL_TO_PB5_A                           138,139,145,146,99           // FPVIe[L] -> PB5: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K99_BUSL1_PB5
#define K_FPVIL_TO_PB5_B                           99                           // FPVIe[L] -> PB5: K99_BUSL1_PB5
#define K_FPVIL_TO_PC4_A                           100,138,139,145,146,99       // FPVIe[L] -> PC4: K100_ACM14_PC4 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K99_BUSL1_PB5
#define K_FPVIL_TO_PC4_B                           100,99                       // FPVIe[L] -> PC4: K100_ACM14_PC4 + K99_BUSL1_PB5
#define K_FPVIL_TO_PC8_A                           138,139,145,146,94           // FPVIe[L] -> PC8: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K94_BUS1_FL_PC8
#define K_FPVIL_TO_PC8_B                           94                           // FPVIe[L] -> PC8: K94_BUS1_FL_PC8
#define K_FPVIL_TO_PD5_A                           104,138,139,145,146          // FPVIe[L] -> PD5: K104_BUS1_FL_PD5 + K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L
#define K_FPVIL_TO_PD5_B                           104                          // FPVIe[L] -> PD5: K104_BUS1_FL_PD5
#define K_FPVIL_TO_PGND                            138,140,51,53,93             // FPVIe[L] -> PGND: K138_QVML_BUS0 + K140_QVML_AGND + K51_BUSL0_LG + K53_LG2_P2P + K93_AGND2PGND_SHORT
#define K_FPVIL_TO_SCL_A                           32                           // FPVIe[L] -> SCL: K32_BUSL0_SCL
#define K_FPVIL_TO_SCL_B                           138,139,145,146,32           // FPVIe[L] -> SCL: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K32_BUSL0_SCL
#define K_FPVIL_TO_SW1_A                           47                           // FPVIe[L] -> SW1: K47_BUS0_FL_SW1
#define K_FPVIL_TO_SW1_B                           138,139,145,146,47           // FPVIe[L] -> SW1: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K47_BUS0_FL_SW1
#define K_FPVIL_TO_SW2_A                           47,50                        // FPVIe[L] -> SW2: K47_BUS0_FL_SW1 + K50_FOVI0_SW2
#define K_FPVIL_TO_SW2_B                           138,139,145,146,47,50        // FPVIe[L] -> SW2: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K47_BUS0_FL_SW1 + K50_FOVI0_SW2
#define K_FPVIL_TO_VAC1_A                          17                           // FPVIe[L] -> VAC1: K17_BUSL_VAC
#define K_FPVIL_TO_VAC1_B                          138,139,145,146,17           // FPVIe[L] -> VAC1: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K17_BUSL_VAC
#define K_FPVIL_TO_VAC2_A                          17,19                        // FPVIe[L] -> VAC2: K17_BUSL_VAC + K19_ACM0_VAC2
#define K_FPVIL_TO_VAC2_B                          139,140,145,146,15,17,19,92  // FPVIe[L] -> VAC2: K139_QVML_BUS1 + K140_QVML_AGND + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K15_VAC2_P2P + K17_BUSL_VAC + K19_ACM0_VAC2 + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_VAC3_A                          17,18                        // FPVIe[L] -> VAC3: K17_BUSL_VAC + K18_ACM0_VAC3
#define K_FPVIL_TO_VAC3_B                          139,140,145,146,16,17,18,92  // FPVIe[L] -> VAC3: K139_QVML_BUS1 + K140_QVML_AGND + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K16_VAC3_P2P + K17_BUSL_VAC + K18_ACM0_VAC3 + K92_AGND_F2S_SHORT
#define K_FPVIL_TO_VAC_WL_A                        32,33                        // FPVIe[L] -> VAC_WL: K32_BUSL0_SCL + K33_ACM2_VAC_WL
#define K_FPVIL_TO_VAC_WL_B                        138,139,145,146,32,33        // FPVIe[L] -> VAC_WL: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K32_BUSL0_SCL + K33_ACM2_VAC_WL
#define K_FPVIL_TO_VBUS_A                          3                            // FPVIe[L] -> VBUS: K3_BUSL0_VBUS
#define K_FPVIL_TO_VBUS_B                          138,139,145,146,3            // FPVIe[L] -> VBUS: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K3_BUSL0_VBUS
#define K_FPVIL_TO_VCC_A                           29                           // FPVIe[L] -> VCC: K29_BUSL0_VCC
#define K_FPVIL_TO_VCC_B                           138,139,145,146,29           // FPVIe[L] -> VCC: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K29_BUSL0_VCC
#define K_FPVIL_TO_VCP_A                           60                           // FPVIe[L] -> VCP: K60_BUSL0_VCP
#define K_FPVIL_TO_VCP_B                           138,139,145,146,60           // FPVIe[L] -> VCP: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K60_BUSL0_VCP
#define K_FPVIL_TO_VMCU_A                          29,31                        // FPVIe[L] -> VMCU: K29_BUSL0_VCC + K31_FOVI2_VMCU
#define K_FPVIL_TO_VMCU_B                          138,139,145,146,29,31        // FPVIe[L] -> VMCU: K138_QVML_BUS0 + K139_QVML_BUS1 + K145_DCM_BUS0_L + K146_DCM_BUS1_L + K29_BUSL0_VCC + K31_FOVI2_VMCU
// --- QTMUe -> DUT Pin ---
#define K_ACDRV1_QTMU                              141,22,30                    // QTMU[S10_CH0_A] -> ACDRV1: K141_QTMUA_BUS0H + K22_ACM1_ACDRV1_F + K30_BUSH0_ACDRV
#define K_ACDRV2_QTMU                              141,23,30                    // QTMU[S10_CH0_A] -> ACDRV2: K141_QTMUA_BUS0H + K23_ACM1_ACDRV2_F + K30_BUSH0_ACDRV
#define K_ACDRV3_QTMU                              141,24,30                    // QTMU[S10_CH0_A] -> ACDRV3: K141_QTMUA_BUS0H + K24_ACM1_ACDRV3_F + K30_BUSH0_ACDRV
#define K_AGND_QTMU_A                              154,155,93                   // QTMU[S10_CH0_A] -> AGND: K154_BUSH0_AMUX + K155_FOVI3_PGND + K93_AGND2PGND_SHORT
#define K_AGND_QTMU_B                              152,154,155,58,93            // QTMU[S10_CH0_B] -> AGND: K152_VDM_TMU + K154_BUSH0_AMUX + K155_FOVI3_PGND + K58_BUSH0_VDM + K93_AGND2PGND_SHORT
#define K_AMUX_QTMU_A                              154                          // QTMU[S10_CH0_A] -> AMUX: K154_BUSH0_AMUX
#define K_AMUX_QTMU_B                              152,154,58                   // QTMU[S10_CH0_B] -> AMUX: K152_VDM_TMU + K154_BUSH0_AMUX + K58_BUSH0_VDM
#define K_BST_QTMU_A                               46,48,76                     // QTMU[S10_CH0_A] -> BST: K46_BUS0_FH_SW1 + K48_ACM5_AMP_REF + K76_ACM_BST
#define K_BST_QTMU_B                               152,46,48,58,76              // QTMU[S10_CH0_B] -> BST: K152_VDM_TMU + K46_BUS0_FH_SW1 + K48_ACM5_AMP_REF + K58_BUSH0_VDM + K76_ACM_BST
#define K_CC1_QTMU_A                               96                           // QTMU[S10_CH0_A] -> CC1: K96_BUS1_FH_CC1
#define K_CC1_QTMU_B                               152,58,96                    // QTMU[S10_CH0_B] -> CC1: K152_VDM_TMU + K58_BUSH0_VDM + K96_BUS1_FH_CC1
#define K_COMP_QTMU_A                              156,157                      // QTMU[S10_CH0_A] -> COMP: K156_BUS0_FH_VCN + K157_ACM11_COMP
#define K_COMP_QTMU_B                              152,156,157,58               // QTMU[S10_CH0_B] -> COMP: K152_VDM_TMU + K156_BUS0_FH_VCN + K157_ACM11_COMP + K58_BUSH0_VDM
#define K_DMA_PA7_QTMU_A                           120                          // QTMU[S10_CH0_A] -> DMA_PA7: K120_BUS1_FH_PA7
#define K_DMA_PA7_QTMU_B                           120,152,58                   // QTMU[S10_CH0_B] -> DMA_PA7: K120_BUS1_FH_PA7 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_HG1_QTMU_A                               62,64                        // QTMU[S10_CH0_A] -> HG1: K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_HG1_QTMU_B                               152,58,62,64                 // QTMU[S10_CH0_B] -> HG1: K152_VDM_TMU + K58_BUSH0_VDM + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_HG2_QTMU                                 141,83,84                    // QTMU[S10_CH0_A] -> HG2: K141_QTMUA_BUS0H + K83_BUSH0_PMID + K84_FOVI1_HG2
#define K_INT_PA0_QTMU_A                           101                          // QTMU[S10_CH0_A] -> INT_PA0: K101_BUS1_FH_PA0
#define K_INT_PA0_QTMU_B                           101,152,58                   // QTMU[S10_CH0_B] -> INT_PA0: K101_BUS1_FH_PA0 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_KLV1_QTMU                                141,35,38                    // QTMU[S10_CH0_A] -> KLV1: K141_QTMUA_BUS0H + K35_BUSH0_KLV + K38_KLV1_2_short
#define K_KLV2_QTMU                                141,35,37                    // QTMU[S10_CH0_A] -> KLV2: K141_QTMUA_BUS0H + K35_BUSH0_KLV + K37_ACM3_KLV2
#define K_LG1_QTMU                                 154,155,54,93                // QTMU[S10_CH0_A] -> LG1: K154_BUSH0_AMUX + K155_FOVI3_PGND + K54_LG1_P2P + K93_AGND2PGND_SHORT
#define K_LG2_QTMU                                 154,155,53,93                // QTMU[S10_CH0_A] -> LG2: K154_BUSH0_AMUX + K155_FOVI3_PGND + K53_LG2_P2P + K93_AGND2PGND_SHORT
#define K_NC_QTMU                                  154,155,93                   // QTMU[S10_CH0_A] -> NC: K154_BUSH0_AMUX + K155_FOVI3_PGND + K93_AGND2PGND_SHORT
#define K_PA1_QTMU_A                               106                          // QTMU[S10_CH0_A] -> PA1: K106_BUS1_FH_PA1
#define K_PA1_QTMU_B                               106,152,58                   // QTMU[S10_CH0_B] -> PA1: K106_BUS1_FH_PA1 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PA4_QTMU                                 1,153,156,157                // QTMU[S10_CH0_A] -> PA4: K1_COMP_AMP3 + K153_PA4_AMP3 + K156_BUS0_FH_VCN + K157_ACM11_COMP
#define K_PA6_PWM2_QTMU_A                          111                          // QTMU[S10_CH0_A] -> PA6_PWM2: K111_BUS1_FH_PA6
#define K_PA6_PWM2_QTMU_B                          111,152,58                   // QTMU[S10_CH0_B] -> PA6_PWM2: K111_BUS1_FH_PA6 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PB1_QTMU_A                               106,107                      // QTMU[S10_CH0_A] -> PB1: K106_BUS1_FH_PA1 + K107_ACM17_PB1
#define K_PB1_QTMU_B                               106,107,152,58               // QTMU[S10_CH0_B] -> PB1: K106_BUS1_FH_PA1 + K107_ACM17_PB1 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PB3_QTMU_A                               96,98                        // QTMU[S10_CH0_A] -> PB3: K96_BUS1_FH_CC1 + K98_ACM13_PB3
#define K_PB3_QTMU_B                               152,58,96,98                 // QTMU[S10_CH0_B] -> PB3: K152_VDM_TMU + K58_BUSH0_VDM + K96_BUS1_FH_CC1 + K98_ACM13_PB3
#define K_PB5_QTMU_A                               123                          // QTMU[S10_CH0_A] -> PB5: K123_BUSL1_PB5
#define K_PB5_QTMU_B                               123,152,58                   // QTMU[S10_CH0_B] -> PB5: K123_BUSL1_PB5 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PB6_QTMU_A                               116,117                      // QTMU[S10_CH0_A] -> PB6: K116_BUS1_FH_PB7 + K117_ACM21_PB6
#define K_PB6_QTMU_B                               116,117,152,58               // QTMU[S10_CH0_B] -> PB6: K116_BUS1_FH_PB7 + K117_ACM21_PB6 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PB7_QTMU_A                               116                          // QTMU[S10_CH0_A] -> PB7: K116_BUS1_FH_PB7
#define K_PB7_QTMU_B                               116,152,58                   // QTMU[S10_CH0_B] -> PB7: K116_BUS1_FH_PB7 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PC3_QTMU_A                               101,102                      // QTMU[S10_CH0_A] -> PC3: K101_BUS1_FH_PA0 + K102_ACM15_PC3
#define K_PC3_QTMU_B                               101,102,152,58               // QTMU[S10_CH0_B] -> PC3: K101_BUS1_FH_PA0 + K102_ACM15_PC3 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PC5_QTMU_A                               111,112                      // QTMU[S10_CH0_A] -> PC5: K111_BUS1_FH_PA6 + K112_ACM19_PC5
#define K_PC5_QTMU_B                               111,112,152,58               // QTMU[S10_CH0_B] -> PC5: K111_BUS1_FH_PA6 + K112_ACM19_PC5 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PD2_QTMU_A                               120,121                      // QTMU[S10_CH0_A] -> PD2: K120_BUS1_FH_PA7 + K121_ACM23_PD2
#define K_PD2_QTMU_B                               120,121,152,58               // QTMU[S10_CH0_B] -> PD2: K120_BUS1_FH_PA7 + K121_ACM23_PD2 + K152_VDM_TMU + K58_BUSH0_VDM
#define K_PD3_QTMU_A                               7,8                          // QTMU[S10_CH0_A] -> PD3: K7_BUSL0_VBAT + K8_FOVI5_PD3
#define K_PD3_QTMU_B                               152,58,7,8                   // QTMU[S10_CH0_B] -> PD3: K152_VDM_TMU + K58_BUSH0_VDM + K7_BUSL0_VBAT + K8_FOVI5_PD3
#define K_PGND_QTMU_A                              154,155                      // QTMU[S10_CH0_A] -> PGND: K154_BUSH0_AMUX + K155_FOVI3_PGND
#define K_PGND_QTMU_B                              152,154,155,58               // QTMU[S10_CH0_B] -> PGND: K152_VDM_TMU + K154_BUSH0_AMUX + K155_FOVI3_PGND + K58_BUSH0_VDM
#define K_PGND_WL_QTMU                             141,35,36                    // QTMU[S10_CH0_A] -> PGND_WL: K141_QTMUA_BUS0H + K35_BUSH0_KLV + K36_ACM3_PGND_WL
#define K_PMID_QTMU                                141,83                       // QTMU[S10_CH0_A] -> PMID: K141_QTMUA_BUS0H + K83_BUSH0_PMID
#define K_SDA_QTMU                                 58,59                        // QTMU[S10_CH0_A] -> SDA: K58_BUSH0_VDM + K59_ACM7_SDA
#define K_SW1_QTMU_A                               46                           // QTMU[S10_CH0_A] -> SW1: K46_BUS0_FH_SW1
#define K_SW1_QTMU_B                               152,46,58                    // QTMU[S10_CH0_B] -> SW1: K152_VDM_TMU + K46_BUS0_FH_SW1 + K58_BUSH0_VDM
#define K_SW2_QTMU_A                               46,49                        // QTMU[S10_CH0_A] -> SW2: K46_BUS0_FH_SW1 + K49_ACM5_SW2
#define K_SW2_QTMU_B                               152,46,49,58                 // QTMU[S10_CH0_B] -> SW2: K152_VDM_TMU + K46_BUS0_FH_SW1 + K49_ACM5_SW2 + K58_BUSH0_VDM
#define K_VAC1_QTMU                                14,154,155,93                // QTMU[S10_CH0_A] -> VAC1: K14_VAC1_P2P + K154_BUSH0_AMUX + K155_FOVI3_PGND + K93_AGND2PGND_SHORT
#define K_VAC2_QTMU                                15,154,155,93                // QTMU[S10_CH0_A] -> VAC2: K15_VAC2_P2P + K154_BUSH0_AMUX + K155_FOVI3_PGND + K93_AGND2PGND_SHORT
#define K_VAC3_QTMU                                154,155,16,93                // QTMU[S10_CH0_A] -> VAC3: K154_BUSH0_AMUX + K155_FOVI3_PGND + K16_VAC3_P2P + K93_AGND2PGND_SHORT
#define K_VBAT_QTMU_A                              7                            // QTMU[S10_CH0_A] -> VBAT: K7_BUSL0_VBAT
#define K_VBAT_QTMU_B                              152,58,7                     // QTMU[S10_CH0_B] -> VBAT: K152_VDM_TMU + K58_BUSH0_VDM + K7_BUSL0_VBAT
#define K_VBUS_QTMU                                11,12,7                      // QTMU[S10_CH0_A] -> VBUS: K11_VBUS_SVLP + K12_VBAT_SVLP + K7_BUSL0_VBAT
#define K_VCC_QTMU                                 141,25,30                    // QTMU[S10_CH0_A] -> VCC: K141_QTMUA_BUS0H + K25_ACM1_VCC_F + K30_BUSH0_ACDRV
#define K_VCN_QTMU_A                               156                          // QTMU[S10_CH0_A] -> VCN: K156_BUS0_FH_VCN
#define K_VCN_QTMU_B                               152,156,58                   // QTMU[S10_CH0_B] -> VCN: K152_VDM_TMU + K156_BUS0_FH_VCN + K58_BUSH0_VDM
#define K_VDM_QTMU_A                               58                           // QTMU[S10_CH0_A] -> VDM: K58_BUSH0_VDM
#define K_VDM_QTMU_B                               152                          // QTMU[S10_CH0_B] -> VDM: K152_VDM_TMU
#define K_nQON_QTMU_A                              152,58,62                    // QTMU[S10_CH0_B] -> nQON: K152_VDM_TMU + K58_BUSH0_VDM + K62_BUS0_FH_QON
#define K_nQON_QTMU_B                              66                           // QTMU[S10_CH0_A] -> nQON: K66_TMU_nQON
#define K_nRST_QTMU_A                              123,124                      // QTMU[S10_CH0_A] -> nRST: K123_BUSL1_PB5 + K124_FOVI4_nRST
#define K_nRST_QTMU_B                              123,124,152,58               // QTMU[S10_CH0_B] -> nRST: K123_BUSL1_PB5 + K124_FOVI4_nRST + K152_VDM_TMU + K58_BUSH0_VDM
// --- QVMe -> DUT Pin ---
#define K_ACDRV1_QVMH                              137,22,30                    // QVM[¸ß¶Ë] -> ACDRV1: K137_QVMH_BUS1 + K22_ACM1_ACDRV1_F + K30_BUSH0_ACDRV
#define K_ACDRV1_QVML_A                            138,22,25,29                 // QVM[µÍ¶Ë] -> ACDRV1: K138_QVML_BUS0 + K22_ACM1_ACDRV1_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_ACDRV1_QVML_B                            140,26,92                    // QVM[µÍ¶Ë] -> ACDRV1: K140_QVML_AGND + K26_ACDRV1_P2P + K92_AGND_F2S_SHORT
#define K_ACDRV2_QVMH                              137,23,30                    // QVM[¸ß¶Ë] -> ACDRV2: K137_QVMH_BUS1 + K23_ACM1_ACDRV2_F + K30_BUSH0_ACDRV
#define K_ACDRV2_QVML_A                            138,23,25,29                 // QVM[µÍ¶Ë] -> ACDRV2: K138_QVML_BUS0 + K23_ACM1_ACDRV2_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_ACDRV2_QVML_B                            140,27,92                    // QVM[µÍ¶Ë] -> ACDRV2: K140_QVML_AGND + K27_ACDRV2_P2P + K92_AGND_F2S_SHORT
#define K_ACDRV3_QVMH                              137,24,30                    // QVM[¸ß¶Ë] -> ACDRV3: K137_QVMH_BUS1 + K24_ACM1_ACDRV3_F + K30_BUSH0_ACDRV
#define K_ACDRV3_QVML_A                            138,24,25,29                 // QVM[µÍ¶Ë] -> ACDRV3: K138_QVML_BUS0 + K24_ACM1_ACDRV3_F + K25_ACM1_VCC_F + K29_BUSL0_VCC
#define K_ACDRV3_QVML_B                            140,28,92                    // QVM[µÍ¶Ë] -> ACDRV3: K140_QVML_AGND + K28_ACDRV3_P2P + K92_AGND_F2S_SHORT
#define K_AGND_QVMH                                136,56,62,64                 // QVM[¸ß¶Ë] -> AGND: K136_QVMH_BUS0 + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_AGND_QVML                                140                          // QVM[µÍ¶Ë] -> AGND: K140_QVML_AGND
#define K_AMUX_QVMH                                136,154                      // QVM[¸ß¶Ë] -> AMUX: K136_QVMH_BUS0 + K154_BUSH0_AMUX
#define K_AMUX_QVML                                138,17,18,20                 // QVM[µÍ¶Ë] -> AMUX: K138_QVML_BUS0 + K17_BUSL_VAC + K18_ACM0_VAC3 + K20_ACM0_AMUX
#define K_BST1_QVML                                138,41                       // QVM[µÍ¶Ë] -> BST1: K138_QVML_BUS0 + K41_BUS0_FL_BST
#define K_BST2_QVML                                138,41,43                    // QVM[µÍ¶Ë] -> BST2: K138_QVML_BUS0 + K41_BUS0_FL_BST + K43_ACM4_BST2
#define K_BST_SW_QVML                              109,110,139                  // QVM[µÍ¶Ë] -> BST_SW: K109_BUSL1_PB0 + K110_ACM18_BST + K139_QVML_BUS1
#define K_CC1_QVMH                                 136,96                       // QVM[¸ß¶Ë] -> CC1: K136_QVMH_BUS0 + K96_BUS1_FH_CC1
#define K_CC2_QVML                                 104,105,139                  // QVM[µÍ¶Ë] -> CC2: K104_BUS1_FL_PD5 + K105_ACM16_CC2 + K139_QVML_BUS1
#define K_COMP_QVMH                                136,156,157                  // QVM[¸ß¶Ë] -> COMP: K136_QVMH_BUS0 + K156_BUS0_FH_VCN + K157_ACM11_COMP
#define K_COMP_QVML                                1,118,139,153                // QVM[µÍ¶Ë] -> COMP: K1_COMP_AMP3 + K118_BUS1_FL_PA4 + K139_QVML_BUS1 + K153_PA4_AMP3
#define K_DMA_PA7_QVMH                             120,136                      // QVM[¸ß¶Ë] -> DMA_PA7: K120_BUS1_FH_PA7 + K136_QVMH_BUS0
#define K_DMO_PC6_QVML                             139,94,95                    // QVM[µÍ¶Ë] -> DMO_PC6: K139_QVML_BUS1 + K94_BUS1_FL_PC8 + K95_ACM12_PC6
#define K_DRVH1_QVML                               138,3,4                      // QVM[µÍ¶Ë] -> DRVH1: K138_QVML_BUS0 + K3_BUSL0_VBUS + K4_ACM10_DRVH1
#define K_HG1_QVMH                                 136,62,64                    // QVM[¸ß¶Ë] -> HG1: K136_QVMH_BUS0 + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_HG1_QVML                                 140,56,92                    // QVM[µÍ¶Ë] -> HG1: K140_QVML_AGND + K56_HG1_P2P + K92_AGND_F2S_SHORT
#define K_HG2_QVMH                                 137,83,84                    // QVM[¸ß¶Ë] -> HG2: K137_QVMH_BUS1 + K83_BUSH0_PMID + K84_FOVI1_HG2
#define K_HG2_QVML                                 140,55,92                    // QVM[µÍ¶Ë] -> HG2: K140_QVML_AGND + K55_HG2_P2P + K92_AGND_F2S_SHORT
#define K_INT_PA0_QVMH                             101,136                      // QVM[¸ß¶Ë] -> INT_PA0: K101_BUS1_FH_PA0 + K136_QVMH_BUS0
#define K_KLV1_QVMH                                137,35                       // QVM[¸ß¶Ë] -> KLV1: K137_QVMH_BUS1 + K35_BUSH0_KLV
#define K_KLV1_QVML                                140,39,92                    // QVM[µÍ¶Ë] -> KLV1: K140_QVML_AGND + K39_KLV1_P2P + K92_AGND_F2S_SHORT
#define K_KLV2_QVMH                                137,35,37                    // QVM[¸ß¶Ë] -> KLV2: K137_QVMH_BUS1 + K35_BUSH0_KLV + K37_ACM3_KLV2
#define K_KLV2_QVML                                140,40,92                    // QVM[µÍ¶Ë] -> KLV2: K140_QVML_AGND + K40_KLV2_P2P + K92_AGND_F2S_SHORT
#define K_LG1_QVMH                                 136,54,56,62,64              // QVM[¸ß¶Ë] -> LG1: K136_QVMH_BUS0 + K54_LG1_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_LG1_QVML_A                               138,51,52                    // QVM[µÍ¶Ë] -> LG1: K138_QVML_BUS0 + K51_BUSL0_LG + K52_ACM6_LG2
#define K_LG1_QVML_B                               140,54,92                    // QVM[µÍ¶Ë] -> LG1: K140_QVML_AGND + K54_LG1_P2P + K92_AGND_F2S_SHORT
#define K_LG2_QVMH                                 136,53,56,62,64              // QVM[¸ß¶Ë] -> LG2: K136_QVMH_BUS0 + K53_LG2_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_LG2_QVML_A                               138,51                       // QVM[µÍ¶Ë] -> LG2: K138_QVML_BUS0 + K51_BUSL0_LG
#define K_LG2_QVML_B                               140,53,92                    // QVM[µÍ¶Ë] -> LG2: K140_QVML_AGND + K53_LG2_P2P + K92_AGND_F2S_SHORT
#define K_NC_QVMH                                  136,56,62,64                 // QVM[¸ß¶Ë] -> NC: K136_QVMH_BUS0 + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_NC_QVML                                  140,92                       // QVM[µÍ¶Ë] -> NC: K140_QVML_AGND + K92_AGND_F2S_SHORT
#define K_PA1_QVMH                                 106,136                      // QVM[¸ß¶Ë] -> PA1: K106_BUS1_FH_PA1 + K136_QVMH_BUS0
#define K_PA4_QVML                                 118,139                      // QVM[µÍ¶Ë] -> PA4: K118_BUS1_FL_PA4 + K139_QVML_BUS1
#define K_PA5_QVML                                 114,139                      // QVM[µÍ¶Ë] -> PA5: K114_BUSL1_PA5 + K139_QVML_BUS1
#define K_PA6_PWM2_QVMH                            111,136                      // QVM[¸ß¶Ë] -> PA6_PWM2: K111_BUS1_FH_PA6 + K136_QVMH_BUS0
#define K_PB0_PWM1_QVML                            109,139                      // QVM[µÍ¶Ë] -> PB0_PWM1: K109_BUSL1_PB0 + K139_QVML_BUS1
#define K_PB1_QVMH                                 106,107,136                  // QVM[¸ß¶Ë] -> PB1: K106_BUS1_FH_PA1 + K107_ACM17_PB1 + K136_QVMH_BUS0
#define K_PB2_QVML                                 114,115,139                  // QVM[µÍ¶Ë] -> PB2: K114_BUSL1_PA5 + K115_ACM20_PB2 + K139_QVML_BUS1
#define K_PB3_QVMH                                 136,96,98                    // QVM[¸ß¶Ë] -> PB3: K136_QVMH_BUS0 + K96_BUS1_FH_CC1 + K98_ACM13_PB3
#define K_PB4_QVML                                 118,119,139                  // QVM[µÍ¶Ë] -> PB4: K118_BUS1_FL_PA4 + K119_ACM22_PB4 + K139_QVML_BUS1
#define K_PB5_QVMH                                 123,136                      // QVM[¸ß¶Ë] -> PB5: K123_BUSL1_PB5 + K136_QVMH_BUS0
#define K_PB5_QVML                                 139,99                       // QVM[µÍ¶Ë] -> PB5: K139_QVML_BUS1 + K99_BUSL1_PB5
#define K_PB6_QVMH                                 116,117,136                  // QVM[¸ß¶Ë] -> PB6: K116_BUS1_FH_PB7 + K117_ACM21_PB6 + K136_QVMH_BUS0
#define K_PB7_QVMH                                 116,136                      // QVM[¸ß¶Ë] -> PB7: K116_BUS1_FH_PB7 + K136_QVMH_BUS0
#define K_PC3_QVMH                                 101,102,136                  // QVM[¸ß¶Ë] -> PC3: K101_BUS1_FH_PA0 + K102_ACM15_PC3 + K136_QVMH_BUS0
#define K_PC4_QVML                                 100,139,99                   // QVM[µÍ¶Ë] -> PC4: K100_ACM14_PC4 + K139_QVML_BUS1 + K99_BUSL1_PB5
#define K_PC5_QVMH                                 111,112,136                  // QVM[¸ß¶Ë] -> PC5: K111_BUS1_FH_PA6 + K112_ACM19_PC5 + K136_QVMH_BUS0
#define K_PC8_QVML                                 139,94                       // QVM[µÍ¶Ë] -> PC8: K139_QVML_BUS1 + K94_BUS1_FL_PC8
#define K_PD2_QVMH                                 120,121,136                  // QVM[¸ß¶Ë] -> PD2: K120_BUS1_FH_PA7 + K121_ACM23_PD2 + K136_QVMH_BUS0
#define K_PD3_QVMH                                 136,7,8                      // QVM[¸ß¶Ë] -> PD3: K136_QVMH_BUS0 + K7_BUSL0_VBAT + K8_FOVI5_PD3
#define K_PD5_QVML                                 104,139                      // QVM[µÍ¶Ë] -> PD5: K104_BUS1_FL_PD5 + K139_QVML_BUS1
#define K_PGND_QVMH                                136,154,155                  // QVM[¸ß¶Ë] -> PGND: K136_QVMH_BUS0 + K154_BUSH0_AMUX + K155_FOVI3_PGND
#define K_PGND_QVML                                140,93                       // QVM[µÍ¶Ë] -> PGND: K140_QVML_AGND + K93_AGND2PGND_SHORT
#define K_PGND_WL_QVMH                             137,35,36                    // QVM[¸ß¶Ë] -> PGND_WL: K137_QVMH_BUS1 + K35_BUSH0_KLV + K36_ACM3_PGND_WL
#define K_PMID_QVMH                                137,83                       // QVM[¸ß¶Ë] -> PMID: K137_QVMH_BUS1 + K83_BUSH0_PMID
#define K_SCL_QVML                                 138,32                       // QVM[µÍ¶Ë] -> SCL: K138_QVML_BUS0 + K32_BUSL0_SCL
#define K_SDA_QVMH                                 136,58,59                    // QVM[¸ß¶Ë] -> SDA: K136_QVMH_BUS0 + K58_BUSH0_VDM + K59_ACM7_SDA
#define K_SW1_QVMH                                 136,46                       // QVM[¸ß¶Ë] -> SW1: K136_QVMH_BUS0 + K46_BUS0_FH_SW1
#define K_SW1_QVML                                 138,47                       // QVM[µÍ¶Ë] -> SW1: K138_QVML_BUS0 + K47_BUS0_FL_SW1
#define K_SW2_QVMH                                 136,46,49                    // QVM[¸ß¶Ë] -> SW2: K136_QVMH_BUS0 + K46_BUS0_FH_SW1 + K49_ACM5_SW2
#define K_SW2_QVML                                 138,47,50                    // QVM[µÍ¶Ë] -> SW2: K138_QVML_BUS0 + K47_BUS0_FL_SW1 + K50_FOVI0_SW2
#define K_SW_QVML                                  138,60,61                    // QVM[µÍ¶Ë] -> SW: K138_QVML_BUS0 + K60_BUSL0_VCP + K61_ACM8_SW
#define K_VAC1_QVMH                                136,14,56,62,64              // QVM[¸ß¶Ë] -> VAC1: K136_QVMH_BUS0 + K14_VAC1_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_VAC1_QVML_A                              138,17                       // QVM[µÍ¶Ë] -> VAC1: K138_QVML_BUS0 + K17_BUSL_VAC
#define K_VAC1_QVML_B                              14,140,92                    // QVM[µÍ¶Ë] -> VAC1: K14_VAC1_P2P + K140_QVML_AGND + K92_AGND_F2S_SHORT
#define K_VAC2_QVMH                                136,15,56,62,64              // QVM[¸ß¶Ë] -> VAC2: K136_QVMH_BUS0 + K15_VAC2_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_VAC2_QVML_A                              138,17,19                    // QVM[µÍ¶Ë] -> VAC2: K138_QVML_BUS0 + K17_BUSL_VAC + K19_ACM0_VAC2
#define K_VAC2_QVML_B                              140,15,92                    // QVM[µÍ¶Ë] -> VAC2: K140_QVML_AGND + K15_VAC2_P2P + K92_AGND_F2S_SHORT
#define K_VAC3_QVMH                                136,16,56,62,64              // QVM[¸ß¶Ë] -> VAC3: K136_QVMH_BUS0 + K16_VAC3_P2P + K56_HG1_P2P + K62_BUS0_FH_QON + K64_ACM9_HG1
#define K_VAC3_QVML_A                              138,17,18                    // QVM[µÍ¶Ë] -> VAC3: K138_QVML_BUS0 + K17_BUSL_VAC + K18_ACM0_VAC3
#define K_VAC3_QVML_B                              140,16,92                    // QVM[µÍ¶Ë] -> VAC3: K140_QVML_AGND + K16_VAC3_P2P + K92_AGND_F2S_SHORT
#define K_VAC_WL_QVML                              138,32,33                    // QVM[µÍ¶Ë] -> VAC_WL: K138_QVML_BUS0 + K32_BUSL0_SCL + K33_ACM2_VAC_WL
#define K_VBAT_QVMH                                136,7                        // QVM[¸ß¶Ë] -> VBAT: K136_QVMH_BUS0 + K7_BUSL0_VBAT
#define K_VBUS_QVML                                138,3                        // QVM[µÍ¶Ë] -> VBUS: K138_QVML_BUS0 + K3_BUSL0_VBUS
#define K_VCC_QVMH                                 137,25,30                    // QVM[¸ß¶Ë] -> VCC: K137_QVMH_BUS1 + K25_ACM1_VCC_F + K30_BUSH0_ACDRV
#define K_VCC_QVML_A                               138,29                       // QVM[µÍ¶Ë] -> VCC: K138_QVML_BUS0 + K29_BUSL0_VCC
#define K_VCC_QVML_B                               140,22,25,26,92              // QVM[µÍ¶Ë] -> VCC: K140_QVML_AGND + K22_ACM1_ACDRV1_F + K25_ACM1_VCC_F + K26_ACDRV1_P2P + K92_AGND_F2S_SHORT
#define K_VCN_QVMH                                 136,156                      // QVM[¸ß¶Ë] -> VCN: K136_QVMH_BUS0 + K156_BUS0_FH_VCN
#define K_VCP_QVML                                 138,60                       // QVM[µÍ¶Ë] -> VCP: K138_QVML_BUS0 + K60_BUSL0_VCP
#define K_VDM_QVMH                                 136,58                       // QVM[¸ß¶Ë] -> VDM: K136_QVMH_BUS0 + K58_BUSH0_VDM
#define K_VMCU_QVML                                138,29,31                    // QVM[µÍ¶Ë] -> VMCU: K138_QVML_BUS0 + K29_BUSL0_VCC + K31_FOVI2_VMCU
#define K_nQON_QVMH                                136,62                       // QVM[¸ß¶Ë] -> nQON: K136_QVMH_BUS0 + K62_BUS0_FH_QON
#define K_nRST_QVMH                                123,124,136                  // QVM[¸ß¶Ë] -> nRST: K123_BUSL1_PB5 + K124_FOVI4_nRST + K136_QVMH_BUS0
// --- ACM200 -> DUT Pin ---
#define K_ACDRV1_ACM                               22                           // ACM200[] -> ACDRV1: K22_ACM1_ACDRV1_F
#define K_ACDRV2_ACM                               23                           // ACM200[] -> ACDRV2: K23_ACM1_ACDRV2_F
#define K_ACDRV3_ACM                               24                           // ACM200[] -> ACDRV3: K24_ACM1_ACDRV3_F
#define K_AGND_ACM                                 14,92                        // ACM200[] -> AGND: K14_VAC1_P2P + K92_AGND_F2S_SHORT
#define K_AMUX_ACM                                 18,20                        // ACM200[] -> AMUX: K18_ACM0_VAC3 + K20_ACM0_AMUX
#define K_BST2_ACM                                 43                           // ACM200[] -> BST2: K43_ACM4_BST2
#define K_CC2_ACM                                  105                          // ACM200[] -> CC2: K105_ACM16_CC2
#define K_COMP_ACM                                 157                          // ACM200[] -> COMP: K157_ACM11_COMP
#define K_DMO_PC6_ACM                              95                           // ACM200[] -> DMO_PC6: K95_ACM12_PC6
#define K_DRVH1_ACM                                4                            // ACM200[] -> DRVH1: K4_ACM10_DRVH1
#define K_KLV1_ACM                                 38                           // ACM200[] -> KLV1: K38_KLV1_2_short
#define K_KLV2_ACM                                 37                           // ACM200[] -> KLV2: K37_ACM3_KLV2
#define K_LG1_ACM                                  52                           // ACM200[] -> LG1: K52_ACM6_LG2
#define K_PB1_ACM                                  107                          // ACM200[] -> PB1: K107_ACM17_PB1
#define K_PB2_ACM                                  115                          // ACM200[] -> PB2: K115_ACM20_PB2
#define K_PB3_ACM                                  98                           // ACM200[] -> PB3: K98_ACM13_PB3
#define K_PB4_ACM                                  119                          // ACM200[] -> PB4: K119_ACM22_PB4
#define K_PB6_ACM                                  117                          // ACM200[] -> PB6: K117_ACM21_PB6
#define K_PC3_ACM                                  102                          // ACM200[] -> PC3: K102_ACM15_PC3
#define K_PC4_ACM                                  100                          // ACM200[] -> PC4: K100_ACM14_PC4
#define K_PC5_ACM                                  112                          // ACM200[] -> PC5: K112_ACM19_PC5
#define K_PD2_ACM                                  121                          // ACM200[] -> PD2: K121_ACM23_PD2
#define K_PGND_ACM                                 14,92,93                     // ACM200[] -> PGND: K14_VAC1_P2P + K92_AGND_F2S_SHORT + K93_AGND2PGND_SHORT
#define K_PGND_WL_ACM                              36                           // ACM200[] -> PGND_WL: K36_ACM3_PGND_WL
#define K_SDA_ACM                                  59                           // ACM200[] -> SDA: K59_ACM7_SDA
#define K_SW2_ACM                                  49                           // ACM200[] -> SW2: K49_ACM5_SW2
#define K_VAC2_ACM                                 19                           // ACM200[] -> VAC2: K19_ACM0_VAC2
#define K_VAC3_ACM                                 18                           // ACM200[] -> VAC3: K18_ACM0_VAC3
#define K_VAC_WL_ACM                               33                           // ACM200[] -> VAC_WL: K33_ACM2_VAC_WL
#define K_VCC_ACM                                  25                           // ACM200[] -> VCC: K25_ACM1_VCC_F
// --- FXVIe_PLUS -> DUT Pin ---
#define K_ACDRV1_FXVI                              22,25                        // FXVIe_PLUS[] -> ACDRV1: K22_ACM1_ACDRV1_F + K25_ACM1_VCC_F
#define K_ACDRV2_FXVI                              23,25                        // FXVIe_PLUS[] -> ACDRV2: K23_ACM1_ACDRV2_F + K25_ACM1_VCC_F
#define K_ACDRV3_FXVI                              24,25                        // FXVIe_PLUS[] -> ACDRV3: K24_ACM1_ACDRV3_F + K25_ACM1_VCC_F
#define K_AGND_FXVI                                55,84,92                     // FXVIe_PLUS[] -> AGND: K55_HG2_P2P + K84_FOVI1_HG2 + K92_AGND_F2S_SHORT
#define K_HG2_FXVI                                 84                           // FXVIe_PLUS[] -> HG2: K84_FOVI1_HG2
#define K_NC_FXVI                                  155,92,93                    // FXVIe_PLUS[] -> NC: K155_FOVI3_PGND + K92_AGND_F2S_SHORT + K93_AGND2PGND_SHORT
#define K_PD3_FXVI                                 8                            // FXVIe_PLUS[] -> PD3: K8_FOVI5_PD3
#define K_PGND_FXVI                                55,84,92,93                  // FXVIe_PLUS[] -> PGND: K55_HG2_P2P + K84_FOVI1_HG2 + K92_AGND_F2S_SHORT + K93_AGND2PGND_SHORT
#define K_SW2_FXVI                                 50                           // FXVIe_PLUS[] -> SW2: K50_FOVI0_SW2
#define K_VMCU_FXVI                                31                           // FXVIe_PLUS[] -> VMCU: K31_FOVI2_VMCU
#define K_nRST_FXVI                                124                          // FXVIe_PLUS[] -> nRST: K124_FOVI4_nRST
// ==== PATH_RELAY_END ====
#endif // !defined(AFX_STDAFX_H__3811CD50_B7B0_42B9_9E73_805A91708537__INCLUDED_)
