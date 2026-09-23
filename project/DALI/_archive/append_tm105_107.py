# -*- coding: utf-8 -*-
# 追加 TM105-107 到 test.cpp (保留 UTF-8 BOM + CRLF)
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\PROJECT6-DALI\devel\source\test.cpp'

code = r'''
// =====================================================================
// TM105: HSKP VSPRE_MAX_CMP - VSPRE power rail max comparator (digital V(DTEST0))
// DFT: vset[vbat,4] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,0)] -> a2d_vspre_max_cmp
//      -> VAC1 0->10->0V scan, measure V(DTEST0)=nQON toggle (rising vth ~0.3V, falling 0V @VBAT=4V)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM105_HSKP_VSPRE_MAX_CMP(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VSPRE_MAX_CMP = StsGetParam(funcindex, "VSPRE_MAX_CMP");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vspre_max_cmp[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up (DTEST0 logic read)
    // NOTE: VAC1 is scanned input, do NOT close K21_VAC_Cap (cap slows scan)
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; 10V range (>=2*4V)
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,0)] -> a2d_vspre_max_cmp (reg_config/tm105.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VAC1, find DTEST0 toggle) ======
    // nQON high-Z read DTEST0 logic level (FI=0)
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };    // rising toggle threshold (VAC1)
    double vth_f[SITE_NUM] = { 0 };    // falling toggle threshold (VAC1)
    int prev_state[SITE_NUM] = { 0 };  // 0=init, 1=low, 2=high
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
            int state = (vnqon > 1.0) ? 2 : 1;   // logic-high criterion 1.0V
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
        vspre_max_cmp[site] = vth_r[site];   // record rising toggle threshold
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
        VSPRE_MAX_CMP->SetTestResult(site, 0, vspre_max_cmp[site]);
    }
    return 0;
}


// =====================================================================
// TM106: HSKP VBUS_PRST - VBUS PRST COMP threshold (digital V(DTEST0))
// DFT: vset[vbat,3] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,19)] -> a2d_vbus_prst
//      -> VBUS 3->5->3V scan, measure V(DTEST0)=nQON toggle (r 3.798 f 3.613)
// Loop: VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM106_HSKP_VBUS_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_PRST = StsGetParam(funcindex, "VBUS_PRST");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbus_prst[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,19)] -> a2d_vbus_prst (reg_config/tm106.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x13);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VBUS, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VBUS 3->5V (step 0.1V) ---
    for (double v = 3.0; v <= 5.001; v += 0.1)
    {
        VBUS_DRVH1_ACM.Set(FV, v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
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

    // --- falling scan VBUS 5->3V (step 0.1V) ---
    for (double v = 5.0; v >= 2.999; v -= 0.1)
    {
        VBUS_DRVH1_ACM.Set(FV, v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
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
        vbus_prst[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_PRST->SetTestResult(site, 0, vbus_prst[site]);
    }
    return 0;
}


// =====================================================================
// TM107: HSKP VBUS_HT_VBAT - VBUS HT_VBAT CMP threshold (digital V(DTEST0))
// DFT: vset[vbat,4] -> en_tm[] -> field[(DMUX_EN,1),(DMUX_SEL,41)] -> a2d_vbus_path_on
//      -> VBUS 2->5->2V scan, measure V(DTEST0)=nQON toggle (rising vth 0.126V @VBAT=4V)
// Loop: VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM107_HSKP_VBUS_HT_VBAT(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_HT_VBAT = StsGetParam(funcindex, "VBUS_HT_VBAT");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbus_ht_vbat[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    // field[(DMUX_EN,1),(DMUX_SEL,41)] -> a2d_vbus_path_on (reg_config/tm107.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x29);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (scan VBUS, find DTEST0 toggle) ======
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);

    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    int prev_state[SITE_NUM] = { 0 };
    int rising_done[SITE_NUM] = { 0 };
    int falling_done[SITE_NUM] = { 0 };

    // --- rising scan VBUS 2->5V (step 0.1V) ---
    for (double v = 2.0; v <= 5.001; v += 0.1)
    {
        VBUS_DRVH1_ACM.Set(FV, v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
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

    // --- falling scan VBUS 5->2V (step 0.1V) ---
    for (double v = 5.0; v >= 1.999; v -= 0.1)
    {
        VBUS_DRVH1_ACM.Set(FV, v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
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
        vbus_ht_vbat[site] = vth_r[site];
    }

    // ====== Step 5: Power Off (three-step) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_HT_VBAT->SetTestResult(site, 0, vbus_ht_vbat[site]);
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
print('TM105-107 appended. Total lines:', data.count('\n'))
