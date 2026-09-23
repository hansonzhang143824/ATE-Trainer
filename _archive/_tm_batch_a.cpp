// =====================================================================
// TM113: VCC UV — VCC 欠压锁存 (UVLO) 阈值 (Toggle 电流触发, rampv_capi)
// DFT: vset[vbat,3] → vset[vcc,2.5] → vset[vcc,0] → 扫 VCC 0→2.5→0, 捕 I(VBAT)
// 期望: UVLO 阈值 (VCC_UV_Rise/_Fall/_Hys)
// 测量: VCC ramp (ACDRV123_VCC_ACM), VBAT cap_fv=3V 捕 I(VBAT) 触发点
// =====================================================================
DUT_API int TM113_VCC_UV(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_UV_Rise = StsGetParam(funcindex, "VCC_UV_Rise");
    CParam *VCC_UV_Fall = StsGetParam(funcindex, "VCC_UV_Fall");
    CParam *VCC_UV_Hys = StsGetParam(funcindex, "VCC_UV_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F (ACM1 驱动 VCC)
    // VBAT -> VBAT_PD3_FXVI: K8 default NC 直连
    // ⚠TM113 测 I(VBAT), 不闭合 K65_nQON_PU
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV (cap_fv_value=3, 保持 VBAT 电平)
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[] (SCM 直接扫 VCC, 依赖 VBAT 上电)

    // ====== Step 4: Measure (rampv_capi: VCC ramp, 捕 I(VBAT) 触发点) ======
    // VCC 0→2.5V: VBAT→VCC 通路随 VCC 越过 UVLO 关闭, I(VBAT) 下降沿穿过 10mA
    //             捕获上升段 UVLO 阈值 (TRIG_FALLING, 同 DTEST0 反相惯例)
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    test_method.rampv_capi(ACDRV123_VCC_ACM, ACM200_10V, ACM200_100MA,
                           VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           3.0, 0.0, 2.5, 200, 20, 0.01, TRIG_FALLING, vth_r);
    // VCC 2.5→0V: VBAT 通路随 VCC 低于 UVLO 重新导通, I(VBAT) 上升沿穿过 10mA
    //             捕获下降段 UVLO 阈值 (TRIG_RISING)
    test_method.rampv_capi(ACDRV123_VCC_ACM, ACM200_10V, ACM200_100MA,
                           VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           3.0, 2.5, 0.0, 200, 20, 0.01, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise_result[site] - fall_result[site];
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_UV_Rise->SetTestResult(site, 0, rise_result[site]);
        VCC_UV_Fall->SetTestResult(site, 0, fall_result[site]);
        VCC_UV_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM114: VCC_VBUS_PATH_ACC — VCC 由 VBUS 供电的稳压精度 (MV)
// DFT: vset[vbus,5] vset[vbat,3.7] vset[vac1,5.2] → en_tm[] → 0x10=0x43
//      → iset[vcc,0.05] → Check: V(VCC) (4.2~4.5V)
// =====================================================================
DUT_API int TM114_VCC_VBUS_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBUS_PATH_ACC = StsGetParam(funcindex, "VCC_VBUS_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vbus_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F (ACM1 驱动 VCC)
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    // vset[vac1,5.2,100e-3,0] -> VAC1=5.2V FV
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 5.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(REGN_VOL_SET,0)] -> 0x10=0x43
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);

    // ====== Step 4: Measure ======
    // iset[vcc,0.05]: VCC 灌 50mA, 测 V(VCC) 稳压值 (10V量程≥2×, 100MA≥2×50mA)
    ACDRV123_VCC_ACM.Set(FI, 0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vbus_path_acc[site] = ACDRV123_VCC_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VBUS_PATH_ACC->SetTestResult(site, 0, vcc_vbus_path_acc[site]);
    }
    return 0;
}

// =====================================================================
// TM115: VCC_VAC_PATH_ACC — VCC 由 VAC1 供电的稳压精度 (MV)
// DFT: vset[vbat,2.5] vset[vac1,5] → iset[vcc,0.03] → Check: V(VCC) (3.3~3.7V)
// 注意: 无 en_tm[], 无寄存器写入 (纯测量)
// =====================================================================
DUT_API int TM115_VCC_VAC_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VAC_PATH_ACC = StsGetParam(funcindex, "VCC_VAC_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vac_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,100e-6,0] -> VBAT=2.5V FV
    // vset[vac1,5,100e-3,0] -> VAC1=5V FV
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[], 无寄存器写入

    // ====== Step 4: Measure ======
    // iset[vcc,0.03]: VCC 灌 30mA, 测 V(VCC) 稳压值
    ACDRV123_VCC_ACM.Set(FI, 0.03, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vac_path_acc[site] = ACDRV123_VCC_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VAC_PATH_ACC->SetTestResult(site, 0, vcc_vac_path_acc[site]);
    }
    return 0;
}

// =====================================================================
// TM116: VCC_VBAT_PATH_ACC — VCC 由 VBAT 供电的稳压精度 (MV)
// DFT: vset[vbat,3.7] → iset[vcc,0.05] → Check: V(VCC) (3.4~3.7V)
// 注意: 无 en_tm[], wait_warmup 不调用
// =====================================================================
DUT_API int TM116_VCC_VBAT_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_PATH_ACC = StsGetParam(funcindex, "VCC_VBAT_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vbat_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[], wait_warmup 不调用 (纯测量)

    // ====== Step 4: Measure ======
    // iset[vcc,0.05]: VCC 灌 50mA, 测 V(VCC) 稳压值
    ACDRV123_VCC_ACM.Set(FI, 0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vbat_path_acc[site] = ACDRV123_VCC_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VBAT_PATH_ACC->SetTestResult(site, 0, vcc_vbat_path_acc[site]);
    }
    return 0;
}

// =====================================================================
// TM117: VCC_CUR_LIMIT_VBAT_PATH — VCC 由 VBAT 供电的电流限制 (MI, mA)
// DFT: vset[vbat,4] → vset[vcc,1] → Check: I(VCC) (20~70mA)
// 注意: 无 en_tm[]
// =====================================================================
DUT_API int TM117_VCC_CUR_LIMIT_VBAT_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_CUR_LIMIT_VBAT_PATH = StsGetParam(funcindex, "VCC_CUR_LIMIT_VBAT_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_cur_limit_vbat_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[]

    // ====== Step 4: Measure ======
    // vset[vcc,1]: VCC=1V FV, 测 I(VCC) 电流限制 (100MA≥2×70mA)
    ACDRV123_VCC_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_cur_limit_vbat_path[site] = ACDRV123_VCC_ACM.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_CUR_LIMIT_VBAT_PATH->SetTestResult(site, 0, vcc_cur_limit_vbat_path[site]);
    }
    return 0;
}

// =====================================================================
// TM118: VCC_CUR_LIMIT_VBUS_PATH — VCC 由 VBUS 供电的电流限制 (MI, mA)
// DFT: vset[vbat,3] vset[vbus,5] → vset[vcc,1] → Check: I(VCC) (30~70mA)
// 注意: 无 en_tm[]
// =====================================================================
DUT_API int TM118_VCC_CUR_LIMIT_VBUS_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_CUR_LIMIT_VBUS_PATH = StsGetParam(funcindex, "VCC_CUR_LIMIT_VBUS_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_cur_limit_vbus_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  -> ACDRV123_VCC_ACM: K25_ACM1_VCC_F
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    cbite.SetOn(K25_ACM1_VCC_F, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[]

    // ====== Step 4: Measure ======
    // vset[vcc,1]: VCC=1V FV, 测 I(VCC) 电流限制
    ACDRV123_VCC_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_cur_limit_vbus_path[site] = ACDRV123_VCC_ACM.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    ACDRV123_VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_CUR_LIMIT_VBUS_PATH->SetTestResult(site, 0, vcc_cur_limit_vbus_path[site]);
    }
    return 0;
}
