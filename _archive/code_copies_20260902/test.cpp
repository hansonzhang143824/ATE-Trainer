// test.cpp — NU1201 测试函数 (TM000~TM623)
// 自动生成，基于 STS8300 编程手册 v2.1.15 和 DFT.csv
//
// 测试流程: Connect → PowerOn → RegisterConfig → Measure → PowerOff → Check
// 6步法骨架，每函数必须执行完整6步

#include "stdafx.h"

// ====== 源表声明 ======
// FOVIe (8ch/board)
FOVIe VBUS_FOVI("Sx_0");       // VBUS — FOVIe
FOVIe AMUX_FOVI("Sx_1");       // AMUX — FOVIe (电压测量)
FOVIe PMID_FOVI("Sx_2");       // PMID — FOVIe
FOVIe NTC_FOVI("Sx_3");        // NTC — FOVIe (差分参考)

// ACM200
ACM200 KLV12_ACM("Sx_4");      // KLV1/KLV2 — ACM200
ACM200 ACDRV123_ACM("Sx_5");   // ACDRV1/ACDRV2/ACDRV3 — ACM200
ACM200 SW_ACM("Sx_6");         // SW — ACM200
ACM200 VCC_ACM("Sx_7");        // VCC — ACM200
ACM200 VDRV_AMP_ACM("Sx_8");   // VDRV/AMP_OUT — ACM200
ACM200 VBAT_ACM("Sx_9");       // VBAT — ACM200
ACM200 VAC123_ACM("Sx_10");    // VAC1/VAC2/VAC3 — ACM200
ACM200 PGND_ACM("Sx_11");      // PGND — ACM200
ACM200 BTST_ACM("Sx_12");      // BST — ACM200
ACM200 VBATD_ACM("Sx_13");     // VBAT_DET — ACM200
ACM200 SCL_ACM("Sx_14");       // SCL — ACM200
ACM200 SDA_INT_ACM("Sx_15");   // SDA/INT — ACM200 (Toggle观测源)

// FPVIe (2ch/board, 大电流≥1A)
FPVIe FPVI("Sx_16");
FPVIe FPVI_PC("Sx_17");        // FPVI Kelvin/PC

// ====== 继电器定义 (来自资源分配表) ======
// --- Cap2 电容继电器 ---
#define K16_VBUS_Cap     16
#define K25_VCC_Cap      25
#define K28_VDRV_Cap     28
#define K30_VBAT_Cap     30
#define K32_PMID_Cap     32
#define K37_VAC_Cap      37
#define K66_VBATD_Cap    66

// --- Connect Relay to Resource ---
#define K15_BUSH_VBUS    15
#define K17_BUSH_SW      17
#define K19_BUSH_KLV     19
#define K21_BUSH_ACDRV   21
#define K26_BUSH_VDRV    26
#define K29_BUSL_VBAT    29
#define K31_VBUSL_PMID   31
#define K33_BUSL_PGND    33
#define K34_BUSL_VAC     34
#define K38_BUSL_BTST    38
#define K40_BUSH_AMUX    40
#define K41_BUSH_NTC     41
#define K42_BUSH_PGND    42
#define K43_SDA_INT      43
#define K44_SDA_INT2     44
#define K55_SCL          55

// --- P2P 继电器 ---
#define K18_BST_SW_Cap   18      // BST-SW P2P
#define K47_ACDRV1_P2P   47
#define K48_ACDRV2_P2P   48
#define K49_ACDRV3_P2P   49
#define K50_VAC1_P2P     50
#define K51_VAC2_P2P     51
#define K52_VAC3_P2P     52
#define K68_KLV1_P2P     68

// --- 上拉电阻 ---
#define K53_SCL_PU       53
#define K54_QP           54      // QPoint (特殊电路)
#define K56_NTC_PU       56
#define K57_SDA_PU       57
#define K58_INT_PU       58      // Toggle 必须

// --- 共享继电器 ---
#define K20_KLV_SHARE    20
#define K22_ACDRV_SHARE  22
#define K23_ACDRV_SHARE2 23
#define K27_VDRV_AMP     27
#define K35_VAC_SHARE    35      // VAC3→VAC123_ACM
#define K36_VAC_SHARE2   36      // VAC2→VAC123_ACM
#define K46_Short        46

// --- FPVI Kelvin ---
#define K9_KELVIN        9
#define K10_KELVIN       10
#define K11_KELVIN       11
#define K12_SHARE        12
#define K13_PC           13


// ===================================================================
// TM000: IQ_TEST — Standby 静态电流测量 (VBAT MI)
// ===================================================================
DUT_API int TM000_IQ_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IQ_Standby1_DSM = StsGetParam(funcindex, "IQ_Standby1_DSM");
    CParam *IQ_Standby2_DSM = StsGetParam(funcindex, "IQ_Standby2_DSM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iq_sby1[SITE_NUM] = { 0 };
    double iq_sby2[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT_ACM 直接 MI → Cap OFF; VDRV 仅供电 → Cap ON
    // 单Pin vset, 无跨Pin操作 → 不需要BUS继电器
    cbite.SetOn(K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (vset) ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (TM000) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x00);   // Standby1 mode

    // ====== Step 4: Measure IQ_Standby1_DSM (MI, uA级) ======
    // VBAT_ACM直接测电流, 量程 10UA ≥ 2×IQ(≈数μA)
    VBAT_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_sby1[site] = VBAT_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 3b: Register Config (TM000_1) ======
    // 注: TM000和TM000_1共享上电, 仅寄存器不同
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);   // WAKE_UP=1

    // ====== Step 4b: Measure IQ_Standby2_DSM (MI) ======
    delay_ms(1);
    VBAT_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_sby2[site] = VBAT_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        IQ_Standby1_DSM->SetTestResult(site, 0, iq_sby1[site]);
        IQ_Standby2_DSM->SetTestResult(site, 0, iq_sby2[site]);
    }

    return 0;
}


// ===================================================================
// TM100/101/103: INFRA_TEST — AMUX测量 (MV+MI), 共享VBAT+AMUX闭环
// 闭环: AMUX_FOVI High→[Default]→AMUX→DUT→AGND→AMUX_FOVI Low
// ===================================================================
DUT_API int TM100_INFRA_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VS_PRE     = StsGetParam(funcindex, "VS_PRE");
    CParam *LP_VBG     = StsGetParam(funcindex, "LP_VBG");
    CParam *LP_HR_0P5U = StsGetParam(funcindex, "LP_HR_0P5U");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vs_pre[SITE_NUM]    = { 0 };
    double lp_vbg[SITE_NUM]    = { 0 };
    double lp_hr_05u[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT供电+AMUX测量 — 单Pin操作, 不需要BUS
    // Cap2: K30(VBAT供电, MV加Cap)
    // AMUX: Default直连, 无Cap2
    cbite.SetOn(K30_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();

    // ====== Step 4: Measure (逐参数配置寄存器+测量) ======

    // --- TM100: VS_PRE (MV) ---
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);  // EN_ATEST0=1, ATEST0_MUX=3 → VS_PRE
    AMUX_FOVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vs_pre[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
    }

    // --- TM101: LP_VBG (MV) ---
    I2CWriteSameData(DEV_ADDR, 0x56, 0x12);  // EN_ATEST0=1, ATEST0_MUX=2 → LP_BG_BUF
    AMUX_FOVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_vbg[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
    }

    // --- TM103: LP_HR_0P5U (MI) ---
    // AMUX_FOVI切换到FV模式测电流
    I2CWriteSameData(DEV_ADDR, 0x56, 0x22);  // EN_ATEST0=1, ATEST0_MUX=4 → LP_HR_0P5U
    AMUX_FOVI.Set(FV, 1, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
    delay_ms(1);
    AMUX_FOVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_hr_05u[site] = AMUX_FOVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VS_PRE->SetTestResult(site, 0, vs_pre[site]);
        LP_VBG->SetTestResult(site, 0, lp_vbg[site]);
        LP_HR_0P5U->SetTestResult(site, 0, lp_hr_05u[site]);
    }

    return 0;
}


// ===================================================================
// TM105: VSPRE_MAX_CMP — VSPRE MAX Comparator (Toggle MV)
// 闭环: VAC123_ACM High→[Default]→VAC1→DUT→AGND→VAC123_ACM Low
// 观测: SDA_INT_ACM←[K43]←INT
// ===================================================================
DUT_API int TM105_VSPRE_MAX_CMP(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VSPRE_MAX_CMP = StsGetParam(funcindex, "VSPRE_MAX_CMP");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC1闭环: Default直连 → 不需要额外Connect Relay
    // Cap2: K30(VBAT供电), K37(VAC ramp)
    // Toggle: K43(INT→SDA_INT_ACM)+K58(INT上拉)
    cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 5.35, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);  // EN_ATEST0=1, ATEST0_MUX=3

    // ====== Step 4: Measure (Toggle: VAC1 4.05→5.35→4.05) ======
    // Rise: 4.05→5.35, TRIG_RISING @ 4.75V → 抓上升阈值
    // Fall: 5.35→4.05, TRIG_FALLING @ 4.55V → 抓下降阈值
    {
        ToggleTest tt;
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      4.05, 5.35, 200, 50, 4.75, TRIG_RISING, rise);
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      5.35, 4.05, 200, 50, 4.55, TRIG_FALLING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VSPRE_MAX_CMP->SetTestResult(site, 0, rise[site]);
    }

    return 0;
}


// ===================================================================
// TM106: VBUS_PRST — VBUS 上电复位检测 (Toggle MV)
// Check=INT, rising vth 3.91V, hys 0.2V
// ===================================================================
DUT_API int TM106_VBUS_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_PRST = StsGetParam(funcindex, "VBUS_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]   = { 0 };

    // ====== Step 1: Connect ======
    // VBAT: K29_BUSL_VBAT + K30_VBAT_Cap (供电)
    // VBAT供电, VBUS ramp — 单Pin操作, 无跨Pin → 不需要BUS(K29/K15)
    // Cap2: K30(VBAT), K16(VBUS ramp)
    // Toggle: K43+K58
    cbite.SetOn(K30_VBAT_Cap, K16_VBUS_Cap, K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_FOVI.Set(FV, 3.3, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON); // 起始电压
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x55, 0x94);   // EN_DTEST0=1, DTEST0_MUX=20

    // ====== Step 4: Measure (Toggle: rampv_capv, VBUS 3.3→4.5→3.3) ======
    // Rise: 3.3→4.5, 抓TRIG_RISING → VBUS升到3.91V时VBUS_PRST=1
    // Fall: 4.5→3.3, 抓TRIG_FALLING → VBUS降到3.71V时VBUS_PRST=0
    // Hys = Rise - Fall ≈ 0.2V
    {
        ToggleTest tt;
        tt.rampv_capv(VBUS_FOVI, FOVIe_10V, FOVIe_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      3.3, 4.5, 200, 50,
                      3.91, TRIG_RISING, rise);
        tt.rampv_capv(VBUS_FOVI, FOVIe_10V, FOVIe_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 3.3, 200, 50,
                      3.71, TRIG_FALLING, fall);
    }
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_PRST->SetTestResult(site, 0, rise[site]);
        // Note: hys available for additional validation
    }

    return 0;
}


// ===================================================================
// TM108: VAC1_PRST — VAC1 上电复位检测 (Toggle MV)
// 闭环: VAC123_ACM High→[Default]→VAC1→DUT→AGND→VAC123_ACM Low
// ===================================================================
DUT_API int TM108_VAC1_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST = StsGetParam(funcindex, "VAC1_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC1闭环: Default直连 → 不需要Connect Relay
    // Cap2: K30(VBAT供电), K37(VAC ramp)
    // Toggle: K43(INT→SDA_INT_ACM)+K58(INT上拉)
    cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 3.3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x55, 0x97);  // EN_DTEST0=1, DTEST0_MUX=23

    // ====== Step 4: Measure (Toggle: VAC1 3.3→4.5→3.3) ======
    {
        ToggleTest tt;
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      3.3, 4.5, 200, 50, 3.91, TRIG_RISING, rise);
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 3.3, 200, 50, 3.71, TRIG_FALLING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC1_PRST->SetTestResult(site, 0, rise[site]);
    }

    return 0;
}


// ===================================================================
// TM109: VAC2_PRST — VAC2 上电复位检测 (Toggle MV)
// 闭环: VAC123_ACM High→[K36]→VAC2→DUT→AGND→VAC123_ACM Low
// ===================================================================
DUT_API int TM109_VAC2_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_PRST = StsGetParam(funcindex, "VAC2_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC2闭环: 需要K36_VAC_SHARE2连接VAC2→VAC123_ACM
    // Cap2: K30(VBAT供电), K37(VAC shared)
    // Toggle: K43+K58
    cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K36_VAC_SHARE2,
                K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 3.3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x55, 0x96);  // EN_DTEST0=1, DTEST0_MUX=22

    // ====== Step 4: Measure (Toggle: VAC2 3.3→4.5→3.3) ======
    {
        ToggleTest tt;
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      3.3, 4.5, 200, 50, 3.91, TRIG_RISING, rise);
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 3.3, 200, 50, 3.71, TRIG_FALLING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC2_PRST->SetTestResult(site, 0, rise[site]);
    }

    return 0;
}


// ===================================================================
// TM110: VAC3_PRST — VAC3 上电复位检测 (Toggle MV)
// 闭环: VAC123_ACM High→[K35]→VAC3→DUT→AGND→VAC123_ACM Low
// ===================================================================
DUT_API int TM110_VAC3_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC3_PRST = StsGetParam(funcindex, "VAC3_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC3闭环: 需要K35_VAC_SHARE连接VAC3→VAC123_ACM
    // Cap2: K30(VBAT供电), K37(VAC shared)
    // Toggle: K43+K58
    cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K35_VAC_SHARE,
                K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 3.3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x55, 0x95);  // EN_DTEST0=1, DTEST0_MUX=21

    // ====== Step 4: Measure (Toggle: VAC3 3.3→4.5→3.3) ======
    {
        ToggleTest tt;
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      3.3, 4.5, 200, 50, 3.91, TRIG_RISING, rise);
        tt.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 3.3, 200, 50, 3.71, TRIG_FALLING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC3_PRST->SetTestResult(site, 0, rise[site]);
    }

    return 0;
}

// ===================================================================
// TM114/116/117/118: VCC_Function — VCC LDO 功能测试 (MV + MI)
// ===================================================================
DUT_API int TM114_VCC_Function(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_Acc1    = StsGetParam(funcindex, "VCC_Acc1");
    CParam *VCC_Acc3    = StsGetParam(funcindex, "VCC_Acc3");
    CParam *VCC_Cap2    = StsGetParam(funcindex, "VCC_Cap2");
    CParam *VCC_SHORT1  = StsGetParam(funcindex, "VCC_SHORT1");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_acc1[SITE_NUM]   = { 0 };
    double vcc_acc3[SITE_NUM]   = { 0 };
    double vcc_cap2[SITE_NUM]   = { 0 };
    double vcc_short1[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBUS: K15_BUSH_VBUS + K16_VBUS_Cap (5.2V供电)
    // VBAT: K29_BUSL_VBAT + K30_VBAT_Cap (3.7V供电)
    // VAC1: K34_BUSL_VAC + K37_VAC_Cap (5.2V供电)
    // VCC: K25_VCC_Cap (测量Pin)
    // VBUS/VBAT/VAC1供电, VCC测量 — 单Pin操作, 无跨Pin → 不需要BUS(K15/K29/K34)
    // Cap2: K16(VBUS), K30(VBAT), K37(VAC)
    // VCC: 3/4参数MV → 不加K25(避免干扰TM118 MI)
    cbite.SetOn(K16_VBUS_Cap, K30_VBAT_Cap, K37_VAC_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBUS_FOVI.Set(FV, 5.2, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VBAT_ACM.Set(FV, 3.7, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 5.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // VCC: MV时FI=0(最小档), iset[vcc,0.03/0.01/0.02]为后续MI做准备
    VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3 + 4: Register Config + Measure (逐个参数) ======

    // --- TM114: VCC_Acc1 (MV) ---
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);   // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x63, 0x01);   // REGN_VOL_SET=1
    // iset[vcc,0.03,1e-3,0] → VCC_ACM FI=30mA 加载(但不测量, 仅建立工作条件)
    VCC_ACM.Set(FI, 0.03, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_acc1[site] = VCC_ACM.GetMeasResult(site, MVRET);
    }

    // --- TM116: VCC_Acc3 (MV) ---
    // Hardware_initial: vset[vac1,4.5], iset[vcc,0.01]
    VAC123_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VCC_ACM.Set(FI, 0.01, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_acc3[site] = VCC_ACM.GetMeasResult(site, MVRET);
    }
    VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

    // --- TM117: VCC_Cap2 (MV) ---
    // Hardware_initial: vset[vbat,2.8], iset[vcc,0.02]
    VBAT_ACM.Set(FV, 2.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VCC_ACM.Set(FI, 0.02, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_cap2[site] = VCC_ACM.GetMeasResult(site, MVRET);
    }
    VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

    // --- TM118: VCC_SHORT1 (MI) ---
    // Hardware_initial: vset[vbat,4], Dynamic: vset[vcc,1] → VCC_ACM FV=1, 测电流
    // 直接MI → 临时去掉Cap2会影响精度, 但Cap已闭合在前面的MV测量
    // 妥协方案: 使用较大的电流量程规避Cap干扰
    VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VCC_ACM.Set(FV, 1, ACM200_5V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_short1[site] = VCC_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_Acc1->SetTestResult(site, 0, vcc_acc1[site]);
        VCC_Acc3->SetTestResult(site, 0, vcc_acc3[site]);
        VCC_Cap2->SetTestResult(site, 0, vcc_cap2[site]);
        VCC_SHORT1->SetTestResult(site, 0, vcc_short1[site]);
    }

    return 0;
}


// ===================================================================
// TM125: Trim_IZTC_RES — IZTC 1μA 电流源 Trim (MI, Trim=Y)
// ===================================================================
DUT_API int TM125_Trim_IZTC_RES(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IZTC_1UA_step0 = StsGetParam(funcindex, "IZTC_1UA_step0");
    CParam *IZTC_1UA_step1 = StsGetParam(funcindex, "IZTC_1UA_step1");
    CParam *IZTC_1UA_step2 = StsGetParam(funcindex, "IZTC_1UA_step2");
    CParam *IZTC_1UA_step3 = StsGetParam(funcindex, "IZTC_1UA_step3");
    CParam *IZTC_1UA_step4 = StsGetParam(funcindex, "IZTC_1UA_step4");
    CParam *IZTC_1UA_step5 = StsGetParam(funcindex, "IZTC_1UA_step5");
    CParam *IZTC_1UA_step6 = StsGetParam(funcindex, "IZTC_1UA_step6");
    CParam *IZTC_1UA_step7 = StsGetParam(funcindex, "IZTC_1UA_step7");
    CParam *IZTC_1UA_step8 = StsGetParam(funcindex, "IZTC_1UA_step8");
    CParam *IZTC_1UA_step9 = StsGetParam(funcindex, "IZTC_1UA_step9");
    CParam *IZTC_1UA_step10 = StsGetParam(funcindex, "IZTC_1UA_step10");
    CParam *IZTC_1UA_step11 = StsGetParam(funcindex, "IZTC_1UA_step11");
    CParam *IZTC_1UA_step12 = StsGetParam(funcindex, "IZTC_1UA_step12");
    CParam *IZTC_1UA_step13 = StsGetParam(funcindex, "IZTC_1UA_step13");
    CParam *IZTC_1UA_step14 = StsGetParam(funcindex, "IZTC_1UA_step14");
    CParam *IZTC_1UA_step15 = StsGetParam(funcindex, "IZTC_1UA_step15");
    CParam *IZTC_1UA_step16 = StsGetParam(funcindex, "IZTC_1UA_step16");
    CParam *IZTC_1UA_step17 = StsGetParam(funcindex, "IZTC_1UA_step17");
    CParam *IZTC_1UA_step18 = StsGetParam(funcindex, "IZTC_1UA_step18");
    CParam *IZTC_1UA_step19 = StsGetParam(funcindex, "IZTC_1UA_step19");
    CParam *IZTC_1UA_step20 = StsGetParam(funcindex, "IZTC_1UA_step20");
    CParam *IZTC_1UA_step21 = StsGetParam(funcindex, "IZTC_1UA_step21");
    CParam *IZTC_1UA_step22 = StsGetParam(funcindex, "IZTC_1UA_step22");
    CParam *IZTC_1UA_step23 = StsGetParam(funcindex, "IZTC_1UA_step23");
    CParam *IZTC_1UA_step24 = StsGetParam(funcindex, "IZTC_1UA_step24");
    CParam *IZTC_1UA_step25 = StsGetParam(funcindex, "IZTC_1UA_step25");
    CParam *IZTC_1UA_step26 = StsGetParam(funcindex, "IZTC_1UA_step26");
    CParam *IZTC_1UA_step27 = StsGetParam(funcindex, "IZTC_1UA_step27");
    CParam *IZTC_1UA_step28 = StsGetParam(funcindex, "IZTC_1UA_step28");
    CParam *IZTC_1UA_step29 = StsGetParam(funcindex, "IZTC_1UA_step29");
    CParam *IZTC_1UA_step30 = StsGetParam(funcindex, "IZTC_1UA_step30");
    CParam *IZTC_1UA_step31 = StsGetParam(funcindex, "IZTC_1UA_step31");
    CParam *IZTC_1UA_step32 = StsGetParam(funcindex, "IZTC_1UA_step32");
    CParam *IZTC_1UA_step33 = StsGetParam(funcindex, "IZTC_1UA_step33");
    CParam *IZTC_1UA_step34 = StsGetParam(funcindex, "IZTC_1UA_step34");
    CParam *IZTC_1UA_step35 = StsGetParam(funcindex, "IZTC_1UA_step35");
    CParam *IZTC_1UA_step36 = StsGetParam(funcindex, "IZTC_1UA_step36");
    CParam *IZTC_1UA_step37 = StsGetParam(funcindex, "IZTC_1UA_step37");
    CParam *IZTC_1UA_step38 = StsGetParam(funcindex, "IZTC_1UA_step38");
    CParam *IZTC_1UA_step39 = StsGetParam(funcindex, "IZTC_1UA_step39");
    CParam *IZTC_1UA_step40 = StsGetParam(funcindex, "IZTC_1UA_step40");
    CParam *IZTC_1UA_step41 = StsGetParam(funcindex, "IZTC_1UA_step41");
    CParam *IZTC_1UA_step42 = StsGetParam(funcindex, "IZTC_1UA_step42");
    CParam *IZTC_1UA_step43 = StsGetParam(funcindex, "IZTC_1UA_step43");
    CParam *IZTC_1UA_step44 = StsGetParam(funcindex, "IZTC_1UA_step44");
    CParam *IZTC_1UA_step45 = StsGetParam(funcindex, "IZTC_1UA_step45");
    CParam *IZTC_1UA_step46 = StsGetParam(funcindex, "IZTC_1UA_step46");
    CParam *IZTC_1UA_step47 = StsGetParam(funcindex, "IZTC_1UA_step47");
    CParam *IZTC_1UA_step48 = StsGetParam(funcindex, "IZTC_1UA_step48");
    CParam *IZTC_1UA_step49 = StsGetParam(funcindex, "IZTC_1UA_step49");
    CParam *IZTC_1UA_step50 = StsGetParam(funcindex, "IZTC_1UA_step50");
    CParam *IZTC_1UA_step51 = StsGetParam(funcindex, "IZTC_1UA_step51");
    CParam *IZTC_1UA_step52 = StsGetParam(funcindex, "IZTC_1UA_step52");
    CParam *IZTC_1UA_step53 = StsGetParam(funcindex, "IZTC_1UA_step53");
    CParam *IZTC_1UA_step54 = StsGetParam(funcindex, "IZTC_1UA_step54");
    CParam *IZTC_1UA_step55 = StsGetParam(funcindex, "IZTC_1UA_step55");
    CParam *IZTC_1UA_step56 = StsGetParam(funcindex, "IZTC_1UA_step56");
    CParam *IZTC_1UA_step57 = StsGetParam(funcindex, "IZTC_1UA_step57");
    CParam *IZTC_1UA_step58 = StsGetParam(funcindex, "IZTC_1UA_step58");
    CParam *IZTC_1UA_step59 = StsGetParam(funcindex, "IZTC_1UA_step59");
    CParam *IZTC_1UA_step60 = StsGetParam(funcindex, "IZTC_1UA_step60");
    CParam *IZTC_1UA_step61 = StsGetParam(funcindex, "IZTC_1UA_step61");
    CParam *IZTC_1UA_step62 = StsGetParam(funcindex, "IZTC_1UA_step62");
    CParam *IZTC_1UA_step63 = StsGetParam(funcindex, "IZTC_1UA_step63");
    CParam *IZTC_1UA_pre_value = StsGetParam(funcindex, "IZTC_1UA_pre_value");
    CParam *IZTC_1UA_pre_bit = StsGetParam(funcindex, "IZTC_1UA_pre_bit");
    CParam *IZTC_1UA_post_bit = StsGetParam(funcindex, "IZTC_1UA_post_bit");
    CParam *IZTC_1UA_updated = StsGetParam(funcindex, "IZTC_1UA_updated");
    CParam *IZTC_1UA_guessed = StsGetParam(funcindex, "IZTC_1UA_guessed");
    CParam *IZTC_1UA_target = StsGetParam(funcindex, "IZTC_1UA_target");
    CParam *IZTC_1UA_post_value = StsGetParam(funcindex, "IZTC_1UA_post_value");
    CParam *IZTC_1UA_post_rt = StsGetParam(funcindex, "IZTC_1UA_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    // ====== Step 1: Connect ======
    // VBAT供电, AMUX MI — 单Pin无跨Pin, 不需要BUS
    cbite.SetOn(K30_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // AMUX_FOVI: MI测量, FV=1(force 1V), 量程 100UA ≥ 2×1μA
    AMUX_FOVI.Set(FV, 1, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);   // WAKE_UP=1

    // ====== Step 4: Trim Execute ======
    TRIM_NODE &IZTC_NODE = trim_reg.trim("iztc_res");
    IZTC_NODE.execute(measure_IZTC_1UA, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    return 0;
}


// ===================================================================
// TM130: Trim_VBG — Bandgap 电压 Trim (MV, Trim=Y)
// ===================================================================
DUT_API int TM130_Trim_VBG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HP_VBG_step0 = StsGetParam(funcindex, "HP_VBG_step0");
    CParam *HP_VBG_step1 = StsGetParam(funcindex, "HP_VBG_step1");
    CParam *HP_VBG_step2 = StsGetParam(funcindex, "HP_VBG_step2");
    CParam *HP_VBG_step3 = StsGetParam(funcindex, "HP_VBG_step3");
    CParam *HP_VBG_step4 = StsGetParam(funcindex, "HP_VBG_step4");
    CParam *HP_VBG_step5 = StsGetParam(funcindex, "HP_VBG_step5");
    CParam *HP_VBG_step6 = StsGetParam(funcindex, "HP_VBG_step6");
    CParam *HP_VBG_step7 = StsGetParam(funcindex, "HP_VBG_step7");
    CParam *HP_VBG_step8 = StsGetParam(funcindex, "HP_VBG_step8");
    CParam *HP_VBG_step9 = StsGetParam(funcindex, "HP_VBG_step9");
    CParam *HP_VBG_step10 = StsGetParam(funcindex, "HP_VBG_step10");
    CParam *HP_VBG_step11 = StsGetParam(funcindex, "HP_VBG_step11");
    CParam *HP_VBG_step12 = StsGetParam(funcindex, "HP_VBG_step12");
    CParam *HP_VBG_step13 = StsGetParam(funcindex, "HP_VBG_step13");
    CParam *HP_VBG_step14 = StsGetParam(funcindex, "HP_VBG_step14");
    CParam *HP_VBG_step15 = StsGetParam(funcindex, "HP_VBG_step15");
    CParam *HP_VBG_pre_value = StsGetParam(funcindex, "HP_VBG_pre_value");
    CParam *HP_VBG_pre_bit = StsGetParam(funcindex, "HP_VBG_pre_bit");
    CParam *HP_VBG_post_bit = StsGetParam(funcindex, "HP_VBG_post_bit");
    CParam *HP_VBG_updated = StsGetParam(funcindex, "HP_VBG_updated");
    CParam *HP_VBG_guessed = StsGetParam(funcindex, "HP_VBG_guessed");
    CParam *HP_VBG_target = StsGetParam(funcindex, "HP_VBG_target");
    CParam *HP_VBG_post_value = StsGetParam(funcindex, "HP_VBG_post_value");
    CParam *HP_VBG_post_rt = StsGetParam(funcindex, "HP_VBG_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    // ====== Step 1: Connect ======
    // VBAT供电, AMUX MV — 单Pin无跨Pin, 不需要BUS
    cbite.SetOn(K30_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // AMUX MV测量: FI=0, 最小电流档10UA
    AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (I2C在measure_HP_VBG中) ======
    entertestmode();

    // ====== Step 4: Trim Execute ======
    TRIM_NODE &VBG_NODE = trim_reg.trim("bandgap");
    VBG_NODE.execute(measure_HP_VBG, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    return 0;
}


// ===================================================================
// TM439_1: Trim_VBAT_CV_BUF — VBAT CV Buffer Trim (MV, Trim=Y)
// ===================================================================
DUT_API int TM439_1_Trim_VBAT_CV_BUF(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *CV_BUF_TRIM_step0 = StsGetParam(funcindex, "CV_BUF_TRIM_step0");
    CParam *CV_BUF_TRIM_step1 = StsGetParam(funcindex, "CV_BUF_TRIM_step1");
    CParam *CV_BUF_TRIM_step2 = StsGetParam(funcindex, "CV_BUF_TRIM_step2");
    CParam *CV_BUF_TRIM_step3 = StsGetParam(funcindex, "CV_BUF_TRIM_step3");
    CParam *CV_BUF_TRIM_step4 = StsGetParam(funcindex, "CV_BUF_TRIM_step4");
    CParam *CV_BUF_TRIM_step5 = StsGetParam(funcindex, "CV_BUF_TRIM_step5");
    CParam *CV_BUF_TRIM_step6 = StsGetParam(funcindex, "CV_BUF_TRIM_step6");
    CParam *CV_BUF_TRIM_step7 = StsGetParam(funcindex, "CV_BUF_TRIM_step7");
    CParam *CV_BUF_TRIM_step8 = StsGetParam(funcindex, "CV_BUF_TRIM_step8");
    CParam *CV_BUF_TRIM_step9 = StsGetParam(funcindex, "CV_BUF_TRIM_step9");
    CParam *CV_BUF_TRIM_step10 = StsGetParam(funcindex, "CV_BUF_TRIM_step10");
    CParam *CV_BUF_TRIM_step11 = StsGetParam(funcindex, "CV_BUF_TRIM_step11");
    CParam *CV_BUF_TRIM_step12 = StsGetParam(funcindex, "CV_BUF_TRIM_step12");
    CParam *CV_BUF_TRIM_step13 = StsGetParam(funcindex, "CV_BUF_TRIM_step13");
    CParam *CV_BUF_TRIM_step14 = StsGetParam(funcindex, "CV_BUF_TRIM_step14");
    CParam *CV_BUF_TRIM_step15 = StsGetParam(funcindex, "CV_BUF_TRIM_step15");
    CParam *CV_BUF_TRIM_step16 = StsGetParam(funcindex, "CV_BUF_TRIM_step16");
    CParam *CV_BUF_TRIM_step17 = StsGetParam(funcindex, "CV_BUF_TRIM_step17");
    CParam *CV_BUF_TRIM_step18 = StsGetParam(funcindex, "CV_BUF_TRIM_step18");
    CParam *CV_BUF_TRIM_step19 = StsGetParam(funcindex, "CV_BUF_TRIM_step19");
    CParam *CV_BUF_TRIM_step20 = StsGetParam(funcindex, "CV_BUF_TRIM_step20");
    CParam *CV_BUF_TRIM_step21 = StsGetParam(funcindex, "CV_BUF_TRIM_step21");
    CParam *CV_BUF_TRIM_step22 = StsGetParam(funcindex, "CV_BUF_TRIM_step22");
    CParam *CV_BUF_TRIM_step23 = StsGetParam(funcindex, "CV_BUF_TRIM_step23");
    CParam *CV_BUF_TRIM_step24 = StsGetParam(funcindex, "CV_BUF_TRIM_step24");
    CParam *CV_BUF_TRIM_step25 = StsGetParam(funcindex, "CV_BUF_TRIM_step25");
    CParam *CV_BUF_TRIM_step26 = StsGetParam(funcindex, "CV_BUF_TRIM_step26");
    CParam *CV_BUF_TRIM_step27 = StsGetParam(funcindex, "CV_BUF_TRIM_step27");
    CParam *CV_BUF_TRIM_step28 = StsGetParam(funcindex, "CV_BUF_TRIM_step28");
    CParam *CV_BUF_TRIM_step29 = StsGetParam(funcindex, "CV_BUF_TRIM_step29");
    CParam *CV_BUF_TRIM_step30 = StsGetParam(funcindex, "CV_BUF_TRIM_step30");
    CParam *CV_BUF_TRIM_step31 = StsGetParam(funcindex, "CV_BUF_TRIM_step31");
    CParam *CV_BUF_TRIM_step32 = StsGetParam(funcindex, "CV_BUF_TRIM_step32");
    CParam *CV_BUF_TRIM_step33 = StsGetParam(funcindex, "CV_BUF_TRIM_step33");
    CParam *CV_BUF_TRIM_step34 = StsGetParam(funcindex, "CV_BUF_TRIM_step34");
    CParam *CV_BUF_TRIM_step35 = StsGetParam(funcindex, "CV_BUF_TRIM_step35");
    CParam *CV_BUF_TRIM_step36 = StsGetParam(funcindex, "CV_BUF_TRIM_step36");
    CParam *CV_BUF_TRIM_step37 = StsGetParam(funcindex, "CV_BUF_TRIM_step37");
    CParam *CV_BUF_TRIM_step38 = StsGetParam(funcindex, "CV_BUF_TRIM_step38");
    CParam *CV_BUF_TRIM_step39 = StsGetParam(funcindex, "CV_BUF_TRIM_step39");
    CParam *CV_BUF_TRIM_step40 = StsGetParam(funcindex, "CV_BUF_TRIM_step40");
    CParam *CV_BUF_TRIM_step41 = StsGetParam(funcindex, "CV_BUF_TRIM_step41");
    CParam *CV_BUF_TRIM_step42 = StsGetParam(funcindex, "CV_BUF_TRIM_step42");
    CParam *CV_BUF_TRIM_step43 = StsGetParam(funcindex, "CV_BUF_TRIM_step43");
    CParam *CV_BUF_TRIM_step44 = StsGetParam(funcindex, "CV_BUF_TRIM_step44");
    CParam *CV_BUF_TRIM_step45 = StsGetParam(funcindex, "CV_BUF_TRIM_step45");
    CParam *CV_BUF_TRIM_step46 = StsGetParam(funcindex, "CV_BUF_TRIM_step46");
    CParam *CV_BUF_TRIM_step47 = StsGetParam(funcindex, "CV_BUF_TRIM_step47");
    CParam *CV_BUF_TRIM_step48 = StsGetParam(funcindex, "CV_BUF_TRIM_step48");
    CParam *CV_BUF_TRIM_step49 = StsGetParam(funcindex, "CV_BUF_TRIM_step49");
    CParam *CV_BUF_TRIM_step50 = StsGetParam(funcindex, "CV_BUF_TRIM_step50");
    CParam *CV_BUF_TRIM_step51 = StsGetParam(funcindex, "CV_BUF_TRIM_step51");
    CParam *CV_BUF_TRIM_step52 = StsGetParam(funcindex, "CV_BUF_TRIM_step52");
    CParam *CV_BUF_TRIM_step53 = StsGetParam(funcindex, "CV_BUF_TRIM_step53");
    CParam *CV_BUF_TRIM_step54 = StsGetParam(funcindex, "CV_BUF_TRIM_step54");
    CParam *CV_BUF_TRIM_step55 = StsGetParam(funcindex, "CV_BUF_TRIM_step55");
    CParam *CV_BUF_TRIM_step56 = StsGetParam(funcindex, "CV_BUF_TRIM_step56");
    CParam *CV_BUF_TRIM_step57 = StsGetParam(funcindex, "CV_BUF_TRIM_step57");
    CParam *CV_BUF_TRIM_step58 = StsGetParam(funcindex, "CV_BUF_TRIM_step58");
    CParam *CV_BUF_TRIM_step59 = StsGetParam(funcindex, "CV_BUF_TRIM_step59");
    CParam *CV_BUF_TRIM_step60 = StsGetParam(funcindex, "CV_BUF_TRIM_step60");
    CParam *CV_BUF_TRIM_step61 = StsGetParam(funcindex, "CV_BUF_TRIM_step61");
    CParam *CV_BUF_TRIM_step62 = StsGetParam(funcindex, "CV_BUF_TRIM_step62");
    CParam *CV_BUF_TRIM_step63 = StsGetParam(funcindex, "CV_BUF_TRIM_step63");
    CParam *CV_BUF_TRIM_pre_value = StsGetParam(funcindex, "CV_BUF_TRIM_pre_value");
    CParam *CV_BUF_TRIM_pre_bit = StsGetParam(funcindex, "CV_BUF_TRIM_pre_bit");
    CParam *CV_BUF_TRIM_post_bit = StsGetParam(funcindex, "CV_BUF_TRIM_post_bit");
    CParam *CV_BUF_TRIM_updated = StsGetParam(funcindex, "CV_BUF_TRIM_updated");
    CParam *CV_BUF_TRIM_guessed = StsGetParam(funcindex, "CV_BUF_TRIM_guessed");
    CParam *CV_BUF_TRIM_target = StsGetParam(funcindex, "CV_BUF_TRIM_target");
    CParam *CV_BUF_TRIM_post_value = StsGetParam(funcindex, "CV_BUF_TRIM_post_value");
    CParam *CV_BUF_TRIM_post_rt = StsGetParam(funcindex, "CV_BUF_TRIM_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    // ====== Step 1: Connect ======
    // VAC1供电, VBAT MV — 单Pin无跨Pin, 不需要BUS
    cbite.SetOn(K37_VAC_Cap, K30_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();

    // ====== Step 4: Trim Execute ======
    TRIM_NODE &CVBUF_NODE = trim_reg.trim("mnt_vbat_cv_buf");
    CVBUF_NODE.execute(measure_CV_BUF_TRIM, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off ======
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    return 0;
}


// ===================================================================
// TM600: RDSON_TEST — HS_RDSON (MV&MI, FPVI浮动源1A大电流)
// vset[bst2sw,5] + iset[pmid2sw,1A] + HS FET导通, 台阶式ramp
// ===================================================================
DUT_API int TM600_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // iset[pmid2sw,1A]: FPVI浮动源, PMID(High)→SW(Low), 电流走FPVI_BUS不经过PMID_FOVI
    //   K31_VBUSL_PMID: PMID→FPVI_BUS (High端)
    //   K17_BUSH_SW: SW→FPVI_BUS (Low端)
    //   K32_PMID_Cap: PMID电容 (FPVI浮动源测电流, 不影响PMID_FOVI, Cap可加)
    // vset[bst2sw,5V]: BST浮动电压源, 台阶式ramp保证BST始终领先SW
    //   K18_BST_SW_Cap: BST-SW电容/P2P
    // vset[vbat,4.2]: K30_VBAT_Cap (VBAT仅供电, 非测量源)
    // vset[vdrv,5]: K28_VDRV_Cap (VDRV仅供电, 非测量源)
    cbite.SetOn(K30_VBAT_Cap, K31_VBUSL_PMID, K32_PMID_Cap, K28_VDRV_Cap,
                K17_BUSH_SW, K18_BST_SW_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (台阶式 ramp) ======
    // VBAT和VDRV直接上电(非浮动源, 无ramp需求)
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

    // FPVI FV=0先稳住SW=0V, 确保ramp期间SW电位确定
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(200);

    // PMID和BST台阶式ramp: BST始终领先PMID约5V
    // 保证HS FET导通瞬间(SW→PMID) BST已处于SW+5V
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5, PMID=0, SW=0 (BST-SW=5V)
    BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10, PMID=5, SW=0 (BST-SW=10V)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=15, PMID=10, SW=0
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 15, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=20, PMID=15, SW=0 → 准备导通
    // 导通瞬间: SW→PMID=15V, BST=20V, BST-SW=5V ✓
    BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);  // DIS_CLK=0
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HSON=1, HS FET导通 → SW≈PMID≈15V
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);  // EN_FORCE_ON=1, TM_LSON=1, BUBO_MODE=0
    // 导通瞬间: SW=0→15V, BST=20V, BST-SW=20-15=5V ✓

    // ====== Step 4: Measure (RDSON = V/I × 1000 mΩ) ======
    // iset[pmid2sw,1A]: 量程2A ≥ 1A×2=2A ✓, 电压量程1V(大电流小压降)
    // FPVI从FV模式切换到FI模式, 大电流规则: FV=0→FI=0→SetClamp→FI=目标值
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(25, 25);

    // 加载1A, 路径: PMID → HS FET → SW → FPVI
    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);  // 2ms稳定
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);  // 立即关断!

    FOR_EACH_VALID_SITE(site)
    {
        hs_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // ====== Step 5: Power Off (台阶式下电) ======
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 10, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // RELAY_OFF: 统一量程 10V/10MA
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
    }

    return 0;
}


// ===================================================================
// TM601: RDSON_TEST — LS_RDSON + BOOT_VOLTAGE_DROP
// TM601=LS_RDSON(MV&MI, FPVI浮动源1A), TM606=BOOT_VOLTAGE_DROP(MV)
// ===================================================================
DUT_API int TM601_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LS_RDSON           = StsGetParam(funcindex, "LS_RDSON");
    CParam *BOOT_VOLTAGE_DROP  = StsGetParam(funcindex, "BOOT_VOLTAGE_DROP");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ls_rdson[SITE_NUM]   = { 0 };
    double boot_drop[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // iset[sw2pgnd,1A] → BUS: K17(SW→FPVI_BUS)+K33+K42(PGND→FPVI_BUS)
    // Cap2: K30(VBAT), K32(PMID), K28(VDRV) — FPVI浮动源/供电加Cap
    // iset[bst,0.1]为单Pin操作 → 不需要BUS(K38), BTST_ACM直连
    // 单Pin vset → 不需要BUS(K29/K26/K31)
    cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap,
                K17_BUSH_SW, K33_BUSL_PGND, K42_BUSH_PGND, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 9, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // FPVI: 大电流初始化 FV=0→FI=0→SetClamp (14项检查清单)
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(25, 25);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);   // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);   // TM_DIS_CLK=1
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);   // EN_FORCE_ON=1

    // --- TM601: LS_RDSON (MV&MI) ---
    // iset[sw2pgnd,1A] → FPVI, SW(High)→PGND(Low)
    // 0x59=0x02 → LS FET导通
    I2CWriteSameData(DEV_ADDR, 0x59, 0x02);   // TM_LSON=1
    // 大电流加载: FI=1A, 量程2A ≥ 2×1A
    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);  // 2ms稳定
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);  // 立即关断!
    FOR_EACH_VALID_SITE(site)
    {
        ls_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // --- TM606: BOOT_VOLTAGE_DROP (MV) ---
    // iset[bst,0.1,1e-6,0] → BST_ACM FI=0.1A, 测VDRV-BST电压
    // Check=VDRV-BST → MV测BST端电压
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);   // TM_HSON=1 (恢复)
    BST_ACM.Set(FI, 0.1, ACM200_10V, ACM200_200MA, ACM200_RELAY_ON);
    delay_ms(1);
    BST_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        boot_drop[site] = BST_ACM.GetMeasResult(site, MVRET);
    }
    BST_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);
    BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);
        BOOT_VOLTAGE_DROP->SetTestResult(site, 0, boot_drop[site]);
    }

    return 0;
}


// ===================================================================
// TM607/608/609: ZCD_NOC_Test — 零电流/负电流检测 (Toggle MI)
// BUCK_LS_ZCD + BOOST_HS_ZCD + BOOST_HS_NEG
// ===================================================================
DUT_API int TM607_ZCD_NOC_Test(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_LS_ZCD    = StsGetParam(funcindex, "BUCK_LS_ZCD");
    CParam *BOOST_HS_ZCD   = StsGetParam(funcindex, "BOOST_HS_ZCD");
    CParam *BOOST_HS_NEG   = StsGetParam(funcindex, "BOOST_HS_NEG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double buck_zcd[SITE_NUM]   = { 0 };
    double boost_zcd[SITE_NUM]  = { 0 };
    double boost_neg[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // iset[pgnd2sw]+iset[sw2pmid] → BUS: K17(SW), K31(PMID), K33+K42(PGND)
    // BST单Pin → 不需要BUS(K38); VBAT/VDRV单Pin → 不需要BUS(K29/K26)
    // Cap2: K30(VBAT), K32(PMID), K28(VDRV)
    // P2P: K18(BST-SW), Toggle: K43+K58
    cbite.SetOn(K30_VBAT_Cap, K31_VBUSL_PMID, K32_PMID_Cap, K28_VDRV_Cap,
                K17_BUSH_SW, K18_BST_SW_Cap, K33_BUSL_PGND, K42_BUSH_PGND,
                K43_SDA_INT, K58_INT_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // FPVI 大电流初始化
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(25, 25);
    delay_ms(1);

    // ====== Step 3: Register Config (共用) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);   // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);   // EN_FORCE_ON=1

    // --- TM607: BUCK_LS_ZCD (Toggle MI) ---
    // iset[pgnd2sw,0.5→-0.1A] ramp, 0x59=0x01(TM_LSON), 0x55=0xB0(DTEST0_MUX=48)
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);   // TM_LSON=1, BUBO_MODE=0
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);   // TM_DIS_CLK=1
    I2CWriteSameData(DEV_ADDR, 0x55, 0xB0);   // EN_DTEST0=1, DTEST0_MUX=48
    {
        ToggleTest tt;
        tt.rampi_capv(FPVI, FPVIe_1V, FPVIe_2A,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      0.5, -0.1, 100, 20,
                      0, TRIG_FALLING, buck_zcd);
    }
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);

    // --- TM608: BOOST_HS_ZCD (Toggle MI) ---
    // iset[sw2pmid,2→0.9A] ramp, 0x59=0x02(TM_HSON), 0x55=0xB1(DTEST0_MUX=49)
    // BUBO_MODE=1 (Boost mode)
    PMID_FOVI.Set(FV, 9, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
    I2CWriteSameData(DEV_ADDR, 0x59, 0x02);   // TM_HSON=1
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);   // TM_DIS_CLK=0
    I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);   // EN_DTEST0=1, DTEST0_MUX=49
    {
        ToggleTest tt;
        tt.rampi_capv(FPVI, FPVIe_1V, FPVIe_2A,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      2, 0.9, 100, 20,
                      0, TRIG_FALLING, boost_zcd);
    }
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);

    // --- TM609: BOOST_HS_NEG (Toggle MI, ≥1A大电流) ---
    // iset[sw2pmid,2→3.2A] ramp, 3.2A ≥ 1A → FPVIe_10A量程
    // 0x59=0x02, BUBO_MODE=1, FPWM_EN=1
    VBAT_ACM.Set(FV, 3.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    I2CWriteSameData(DEV_ADDR, 0x09, 0x19);   // FPWM_EN=1
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
    I2CWriteSameData(DEV_ADDR, 0x59, 0x02);   // TM_HSON=1
    I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);   // EN_DTEST0=1, DTEST0_MUX=49
    {
        ToggleTest tt;
        tt.rampi_capv(FPVI, FPVIe_1V, FPVIe_10A,
                      SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                      2, 3.2, 100, 20,
                      0, TRIG_RISING, boost_neg);
    }
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);

    // ====== Step 5: Power Off ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        BUCK_LS_ZCD->SetTestResult(site, 0, buck_zcd[site]);
        BOOST_HS_ZCD->SetTestResult(site, 0, boost_zcd[site]);
        BOOST_HS_NEG->SetTestResult(site, 0, boost_neg[site]);
    }

    return 0;
}


// ===================================================================
// TM623: Trim_BUCK_HS_Gain — Buck HS Current Sense Gain Trim (MV, Trim=Y)
// AMUX-NTC差分测量, FPVI大电流3A台阶ramp
// ===================================================================
DUT_API int TM623_Trim_BUCK_HS_Gain(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_HS_CS_GAIN_step0 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step0");
    CParam *BUCK_HS_CS_GAIN_step1 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step1");
    CParam *BUCK_HS_CS_GAIN_step2 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step2");
    CParam *BUCK_HS_CS_GAIN_step3 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step3");
    CParam *BUCK_HS_CS_GAIN_step4 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step4");
    CParam *BUCK_HS_CS_GAIN_step5 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step5");
    CParam *BUCK_HS_CS_GAIN_step6 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step6");
    CParam *BUCK_HS_CS_GAIN_step7 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step7");
    CParam *BUCK_HS_CS_GAIN_step8 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step8");
    CParam *BUCK_HS_CS_GAIN_step9 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step9");
    CParam *BUCK_HS_CS_GAIN_step10 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step10");
    CParam *BUCK_HS_CS_GAIN_step11 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step11");
    CParam *BUCK_HS_CS_GAIN_step12 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step12");
    CParam *BUCK_HS_CS_GAIN_step13 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step13");
    CParam *BUCK_HS_CS_GAIN_step14 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step14");
    CParam *BUCK_HS_CS_GAIN_step15 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step15");
    CParam *BUCK_HS_CS_GAIN_step16 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step16");
    CParam *BUCK_HS_CS_GAIN_step17 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step17");
    CParam *BUCK_HS_CS_GAIN_step18 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step18");
    CParam *BUCK_HS_CS_GAIN_step19 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step19");
    CParam *BUCK_HS_CS_GAIN_step20 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step20");
    CParam *BUCK_HS_CS_GAIN_step21 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step21");
    CParam *BUCK_HS_CS_GAIN_step22 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step22");
    CParam *BUCK_HS_CS_GAIN_step23 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step23");
    CParam *BUCK_HS_CS_GAIN_step24 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step24");
    CParam *BUCK_HS_CS_GAIN_step25 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step25");
    CParam *BUCK_HS_CS_GAIN_step26 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step26");
    CParam *BUCK_HS_CS_GAIN_step27 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step27");
    CParam *BUCK_HS_CS_GAIN_step28 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step28");
    CParam *BUCK_HS_CS_GAIN_step29 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step29");
    CParam *BUCK_HS_CS_GAIN_step30 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step30");
    CParam *BUCK_HS_CS_GAIN_step31 = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_step31");
    CParam *BUCK_HS_CS_GAIN_pre_value = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_pre_value");
    CParam *BUCK_HS_CS_GAIN_pre_bit = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_pre_bit");
    CParam *BUCK_HS_CS_GAIN_post_bit = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_post_bit");
    CParam *BUCK_HS_CS_GAIN_updated = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_updated");
    CParam *BUCK_HS_CS_GAIN_guessed = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_guessed");
    CParam *BUCK_HS_CS_GAIN_target = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_target");
    CParam *BUCK_HS_CS_GAIN_post_value = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_post_value");
    CParam *BUCK_HS_CS_GAIN_post_rt = StsGetParam(funcindex, "BUCK_HS_CS_GAIN_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    // ====== Step 1: Connect ======
    // iset[pmid2sw,3A] → BUS: K31(PMID)+K17(SW)
    // vset[bst2sw,5V] → 台阶ramp, BTST_ACM直连BST
    // VBAT/VDRV单Pin → 不需要BUS
    // Cap2: K30(VBAT), K32(PMID), K28(VDRV), P2P: K18(BST-SW)
    cbite.SetOn(K30_VBAT_Cap, K31_VBUSL_PMID, K32_PMID_Cap, K28_VDRV_Cap,
                K17_BUSH_SW, K18_BST_SW_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (台阶式ramp: BST领先PMID 5V) ======
    VBAT_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

    // FPVI FV=0稳住SW=0V
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.SetClamp(25, 25);
    delay_us(200);

    // 台阶ramp: BST始终领先PMID 5V
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 最终BST=10V, PMID=5V, SW=0 → BST-SW=10V
    // FET导通后SW→5V → BST-SW=5V ✓
    BTST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // AMUX-NTC差分: 都FI=0, 10V/10UA
    AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
    NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();

    // ====== Step 4: Trim Execute ======
    TRIM_NODE &BHSG_NODE = trim_reg.trim("buck_hsfet_gain");
    BHSG_NODE.execute(measure_BUCK_HS_CS_GAIN, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (台阶式下电) ======
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);
    AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    return 0;
}
