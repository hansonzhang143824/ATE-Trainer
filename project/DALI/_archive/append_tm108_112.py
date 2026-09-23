# -*- coding: utf-8 -*-
# 追加 TM108-112 到 test.cpp (保留 UTF-8 BOM + CRLF)
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\PROJECT6-DALI\devel\source\test.cpp'

code = r'''
// =====================================================================
// TM108: HSKP VAC1_PRST - VAC1 PRST CMP threshold (digital V(DTEST0))
// DFT: vset[vbat,3] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,22)] -> a2d_vac1_prst
//      -> VAC1 0->10->0V scan, measure V(DTEST0)=nQON toggle (r 4.059 f 3.738)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST = StsGetParam(funcindex, "VAC1_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac1_prst[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC (VAC1 path)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // NOTE: VAC1 is scanned input, do NOT close K21_VAC_Cap
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,22)] -> a2d_vac1_prst (reg_config/tm108.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VAC1, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VAC1 0->10V (step 0.5V) ---
    for (double v = 0.0; v <= 10.001; v += 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] != 0 && prev_state[site] == 1 && state == 2 && !rising_done[site])
            {
                vth_r[site] = v;
                rising_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }

    // --- falling scan VAC1 10->0V (step 0.5V) ---
    for (double v = 10.0; v >= -0.001; v -= 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] == 2 && state == 1 && !falling_done[site])
            {
                vth_f[site] = v;
                falling_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }
    FOR_EACH_VALID_SITE(site)
    {
        vac1_prst[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC1_PRST->SetTestResult(site, 0, vac1_prst[site]);
    }
    return 0;
}


// =====================================================================
// TM109: HSKP VAC2_PRST - VAC2 PRST CMP threshold (digital V(DTEST0))
// DFT: vset[vbat,3] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,21)] -> a2d_vac2_prst
//      -> VAC2 0->10->0V scan, measure V(DTEST0)=nQON toggle (r 4.079 f 3.748)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM
// NOTE: VAC2 selected via K19_VAC2 (need to confirm routing to AMUX channel)
// =====================================================================
DUT_API int TM109_HSKP_VAC2_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_PRST = StsGetParam(funcindex, "VAC2_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac2_prst[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC2 -> VAC123_AMUX_ACM: close K19_ACM0_VAC2 to route VAC2 (待确认CBIT)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // NOTE: VAC2 is scanned input, do NOT close K21_VAC_Cap
    cbite.SetOn(K65_nQON_PU, -1);
    cbite.SetOn(K19_ACM0_VAC2, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,21)] -> a2d_vac2_prst (reg_config/tm109.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x15);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VAC2, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VAC2 0->10V (step 0.5V) ---
    for (double v = 0.0; v <= 10.001; v += 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] != 0 && prev_state[site] == 1 && state == 2 && !rising_done[site])
            {
                vth_r[site] = v;
                rising_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }

    // --- falling scan VAC2 10->0V (step 0.5V) ---
    for (double v = 10.0; v >= -0.001; v -= 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] == 2 && state == 1 && !falling_done[site])
            {
                vth_f[site] = v;
                falling_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }
    FOR_EACH_VALID_SITE(site)
    {
        vac2_prst[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC2_PRST->SetTestResult(site, 0, vac2_prst[site]);
    }
    return 0;
}


// =====================================================================
// TM110: HSKP VAC3_PRST - VAC3 PRST CMP threshold (digital V(DTEST0))
// DFT: vset[vbat,3] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,20)] -> a2d_vac3_prst
//      -> VAC3 0->10->0V scan, measure V(DTEST0)=nQON toggle (r 4.085 f 3.758)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM
// NOTE: VAC3 selected via K18_VAC3 (need to confirm routing to AMUX channel)
// =====================================================================
DUT_API int TM110_HSKP_VAC3_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC3_PRST = StsGetParam(funcindex, "VAC3_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac3_prst[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC3 -> VAC123_AMUX_ACM: close K18_ACM0_VAC3 to route VAC3 (待确认CBIT)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // NOTE: VAC3 is scanned input, do NOT close K21_VAC_Cap
    cbite.SetOn(K65_nQON_PU, -1);
    cbite.SetOn(K18_ACM0_VAC3, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,20)] -> a2d_vac3_prst (reg_config/tm110.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x14);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VAC3, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VAC3 0->10V (step 0.5V) ---
    for (double v = 0.0; v <= 10.001; v += 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] != 0 && prev_state[site] == 1 && state == 2 && !rising_done[site])
            {
                vth_r[site] = v;
                rising_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }

    // --- falling scan VAC3 10->0V (step 0.5V) ---
    for (double v = 10.0; v >= -0.001; v -= 0.5)
    {
        VAC123_AMUX_ACM.Set(FV, v, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] == 2 && state == 1 && !falling_done[site])
            {
                vth_f[site] = v;
                falling_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }
    FOR_EACH_VALID_SITE(site)
    {
        vac3_prst[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC3_PRST->SetTestResult(site, 0, vac3_prst[site]);
    }
    return 0;
}


// =====================================================================
// TM111: HSKP VBAT_UV - VBAT_UV CMP threshold (digital V(DTEST0))
// DFT: vset[vac1,5] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,23)] -> a2d_vbat_uv_ok
//      -> VBAT 5->0V scan, measure V(DTEST0)=nQON toggle (r 2.178 f 2.137)
// Loop: VAC123_AMUX_ACM + VBAT_PD3_FXVI + NQON_HG1_ACM
// =====================================================================
DUT_API int TM111_HSKP_VBAT_UV(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_UV = StsGetParam(funcindex, "VBAT_UV");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbat_uv[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测扫描输入)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K21_VAC_Cap, -1);
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,1e-3,0] -> VAC1=5V FV (10V range)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,23)] -> a2d_vbat_uv_ok (reg_config/tm111.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x17);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VBAT, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VBAT 0->5V (step 0.1V) ---
    for (double v = 0.0; v <= 5.001; v += 0.1)
    {
        VBAT_PD3_FXVI.Set(FV, v, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] != 0 && prev_state[site] == 1 && state == 2 && !rising_done[site])
            {
                vth_r[site] = v;
                rising_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }

    // --- falling scan VBAT 5->0V (step 0.1V) ---
    for (double v = 5.0; v >= -0.001; v -= 0.1)
    {
        VBAT_PD3_FXVI.Set(FV, v, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] == 2 && state == 1 && !falling_done[site])
            {
                vth_f[site] = v;
                falling_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }
    FOR_EACH_VALID_SITE(site)
    {
        vbat_uv[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_UV->SetTestResult(site, 0, vbat_uv[site]);
    }
    return 0;
}


// =====================================================================
// TM112: HSKP VBAT_HT_3P1V - VBAT_HT_3P1V CMP threshold (digital V(DTEST0))
// DFT: vset[vbat,2.5] + vset[vac1,5] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,40),(D2A_REGN_TM_EN,1)]
//      -> VBAT 4->0V scan, measure V(DTEST0)=nQON toggle (r 3.019 f 2.972)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM112_HSKP_VBAT_HT_3P1V(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_HT_3P1V = StsGetParam(funcindex, "VBAT_HT_3P1V");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbat_ht_3p1v[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K21_VAC_Cap, -1);
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,1e-3,0] -> VBAT=2.5V FV; vset[vac1,5,1e-3,0] -> VAC1=5V
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,40),(D2A_REGN_TM_EN,1)] -> a2d_vbat_path_on (reg_config/tm112.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x28);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);

    // ====== Step 4: Measure (scan VBAT, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VBAT 0->4V (step 0.1V) ---
    for (double v = 0.0; v <= 4.001; v += 0.1)
    {
        VBAT_PD3_FXVI.Set(FV, v, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] != 0 && prev_state[site] == 1 && state == 2 && !rising_done[site])
            {
                vth_r[site] = v;
                rising_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }

    // --- falling scan VBAT 4->0V (step 0.1V) ---
    for (double v = 4.0; v >= -0.001; v -= 0.1)
    {
        VBAT_PD3_FXVI.Set(FV, v, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
        delay_ms(1);
        NQON_HG1_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            double vnqon = NQON_HG1_ACM.GetMeasResult(site, MVRET);
            int state = (vnqon > 1.0) ? 2 : 1;
            if (prev_state[site] == 2 && state == 1 && !falling_done[site])
            {
                vth_f[site] = v;
                falling_done[site] = 1;
            }
            prev_state[site] = state;
        }
    }
    FOR_EACH_VALID_SITE(site)
    {
        vbat_ht_3p1v[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_HT_3P1V->SetTestResult(site, 0, vbat_ht_3p1v[site]);
    }
    return 0;
}
'''

with open(path, 'r', encoding='utf-8-sig') as f:
    data = f.read()
if not data.endswith('\n'):
    data += '\n'
data += code.lstrip('\n')
with open(path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write(data)
print('TM108-112 appended. Total lines:', data.count('\n'))
