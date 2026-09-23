// =====================================================================
// TM121: VAC_PATH_ON — VCC 切换至 VAC1 供电的切换阈值 (Toggle)
// DFT: vset[vbat,3] → en_tm[] → 0x56=0x2A, 0x57=0x08 → 扫 VAC1 0→5→0, 捕 DTEST0
// 期望: VAC1>4.4V 时 VCC 切换至 VAC1 (VAC_PATH_ON_Rise/_Fall/_Hys)
// =====================================================================
DUT_API int TM121_VAC_PATH_ON(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC_PATH_ON_Rise = StsGetParam(funcindex, "VAC_PATH_ON_Rise");
    CParam *VAC_PATH_ON_Fall = StsGetParam(funcindex, "VAC_PATH_ON_Fall");
    CParam *VAC_PATH_ON_Hys = StsGetParam(funcindex, "VAC_PATH_ON_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] -> VBAT=3V FV
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(DMUX_EN,1),(DMUX_SEL,42)] -> 0x56=0x2A, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2A);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 5.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           5.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f);
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
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC_PATH_ON_Rise->SetTestResult(site, 0, rise_result[site]);
        VAC_PATH_ON_Fall->SetTestResult(site, 0, fall_result[site]);
        VAC_PATH_ON_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM122: VMCU_VBAT_PATH_ACC1 — VMCU 由 VBAT 供电的稳压精度 (MV)
// DFT: vset[vbat,3.7] → en_tm[] → 0x10=0x43, 0x29=0x10 (VMCU_FAVOR_VBAT=1)
//      → iset[vmcu,0.05] → Check: V(VMCU) (3.2~3.7V)
// =====================================================================
DUT_API int TM122_VMCU_VBAT_PATH_ACC1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VBAT_PATH_ACC1 = StsGetParam(funcindex, "VMCU_VBAT_PATH_ACC1");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vbat_path_acc1[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU -> VCC_VMCU_FXVI: K31_FOVI2_VMCU (FOVI2 驱动 VMCU)
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    cbite.SetOn(K31_FOVI2_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x10
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);

    // ====== Step 4: Measure ======
    // iset[vmcu,0.05]: VMCU 灌 50mA, 测 V(VMCU) 稳压值
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vbat_path_acc1[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VBAT_PATH_ACC1->SetTestResult(site, 0, vmcu_vbat_path_acc1[site]);
    }
    return 0;
}

// =====================================================================
// TM123: VMCU_VBAT_PATH_ACC2 — VMCU 由 VBAT 供电的稳压精度 (MV)
// DFT: vset[vbat,3.7] → en_tm[] → 0x10=0x43, 0x29=0x18 (VMCU_FAVOR_VBAT=1 + VMCU_VOL_BAT_PATH=1)
//      → iset[vmcu,0.05] → Check: V(VMCU) (3.2~3.7V)
// =====================================================================
DUT_API int TM123_VMCU_VBAT_PATH_ACC2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VBAT_PATH_ACC2 = StsGetParam(funcindex, "VMCU_VBAT_PATH_ACC2");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vbat_path_acc2[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU -> VCC_VMCU_FXVI: K31_FOVI2_VMCU
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    cbite.SetOn(K31_FOVI2_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1),(VMCU_VOL_BAT_PATH,1)] -> 0x10=0x43, 0x29=0x18
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x18);

    // ====== Step 4: Measure ======
    // iset[vmcu,0.05]: VMCU 灌 50mA, 测 V(VMCU) 稳压值
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vbat_path_acc2[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VBAT_PATH_ACC2->SetTestResult(site, 0, vmcu_vbat_path_acc2[site]);
    }
    return 0;
}

// =====================================================================
// TM124: VMCU_VCC_PATH_ACC — VMCU 由 VCC/VBUS 供电的稳压精度 (MV)
// DFT: vset[vbat,3.7] vset[vbus,5] → en_tm[] (delay) → iset[vmcu,0.05]
//      → Check: V(VMCU) (3.8~4.5V)
// =====================================================================
DUT_API int TM124_VMCU_VCC_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VCC_PATH_ACC = StsGetParam(funcindex, "VMCU_VCC_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vcc_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU -> VCC_VMCU_FXVI: K31_FOVI2_VMCU
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    cbite.SetOn(K31_FOVI2_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] (DFT 仅 delay, 无寄存器写入)
    entertestmode();
    delay_ms(1);

    // ====== Step 4: Measure ======
    // iset[vmcu,0.05]: VMCU 灌 50mA, 测 V(VMCU) 稳压值
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vcc_path_acc[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VCC_PATH_ACC->SetTestResult(site, 0, vmcu_vcc_path_acc[site]);
    }
    return 0;
}

// =====================================================================
// TM125: VMCU_CUR_LIMIT_VBAT_PATH — VMCU 由 VBAT 供电的电流限制 (MI, mA)
// DFT: vset[vbat,3.7] → en_tm[] → 0x10=0x43, 0x29=0x10 → vset[vmcu,0.5]
//      → Check: I(VMCU) (10~40mA)
// =====================================================================
DUT_API int TM125_VMCU_CUR_LIMIT_VBAT_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_CUR_LIMIT_VBAT_PATH = StsGetParam(funcindex, "VMCU_CUR_LIMIT_VBAT_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_cur_limit_vbat_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU -> VCC_VMCU_FXVI: K31_FOVI2_VMCU
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    cbite.SetOn(K31_FOVI2_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x10
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);

    // ====== Step 4: Measure ======
    // vset[vmcu,0.5]: VMCU=0.5V FV, 测 I(VMCU) 电流限制 (100MA≥2×40mA)
    VCC_VMCU_FXVI.Set(FV, 0.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_cur_limit_vbat_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_CUR_LIMIT_VBAT_PATH->SetTestResult(site, 0, vmcu_cur_limit_vbat_path[site]);
    }
    return 0;
}

// =====================================================================
// TM126: VMCU_CUR_LIMIT_VCC_PATH — VMCU 由 VCC/VBUS 供电的电流限制 (MI, mA)
// DFT: vset[vbat,3.7] vset[vbus,5] → vset[vmcu,0.5] → Check: I(VMCU) (20~70mA)
// 注意: 无 en_tm[], wait_warmup 不调用
// =====================================================================
DUT_API int TM126_VMCU_CUR_LIMIT_VCC_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_CUR_LIMIT_VCC_PATH = StsGetParam(funcindex, "VMCU_CUR_LIMIT_VCC_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_cur_limit_vcc_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU -> VCC_VMCU_FXVI: K31_FOVI2_VMCU
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    cbite.SetOn(K31_FOVI2_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] -> VBAT=3.7V FV
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // DFT 无 en_tm[], wait_warmup 不调用 (纯测量)

    // ====== Step 4: Measure ======
    // vset[vmcu,0.5]: VMCU=0.5V FV, 测 I(VMCU) 电流限制
    VCC_VMCU_FXVI.Set(FV, 0.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_cur_limit_vcc_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_CUR_LIMIT_VCC_PATH->SetTestResult(site, 0, vmcu_cur_limit_vcc_path[site]);
    }
    return 0;
}

// =====================================================================
// TM127: VBAT_PATH_ON_VMCU — VBAT 供电 VMCU 的切换阈值 (Toggle, VBAT ramp)
// DFT: vset[vbat,2.5] vset[vbus,5] → en_tm[] → 0x10=0x43, 0x29=0x10
//      delay 3ms → 0x56=0x35, 0x57=0x08 → 扫 VBAT 0→4→0, 捕 DTEST0
// =====================================================================
DUT_API int TM127_VBAT_PATH_ON_VMCU(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_PATH_ON_VMCU_Rise = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Rise");
    CParam *VBAT_PATH_ON_VMCU_Fall = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Fall");
    CParam *VBAT_PATH_ON_VMCU_Hys = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,100e-6,0] -> VBAT=2.5V FV
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x10
    // delay 3ms → field[(DMUX_EN,1),(DMUX_SEL,53)] -> 0x56=0x35, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);
    delay_ms(3);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x35);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 4.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f);
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
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_PATH_ON_VMCU_Rise->SetTestResult(site, 0, rise_result[site]);
        VBAT_PATH_ON_VMCU_Fall->SetTestResult(site, 0, fall_result[site]);
        VBAT_PATH_ON_VMCU_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM128: VBAT_PATH_ON_VCC — VBAT 供电 VCC 的切换阈值 (Toggle, VBAT ramp)
// DFT: vset[vbat,3.4] vset[vac1,5] vset[vbus,5] → en_tm[] → 0x10=0x43, 0x29=0x20
//      delay 3ms → 0x56=0x28, 0x57=0x08 → 扫 VBAT 0→4→0, 捕 DTEST0
// =====================================================================
DUT_API int TM128_VBAT_PATH_ON_VCC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_PATH_ON_VCC_Rise = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Rise");
    CParam *VBAT_PATH_ON_VCC_Fall = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Fall");
    CParam *VBAT_PATH_ON_VCC_Hys = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.4,100e-6,0] -> VBAT=3.4V FV
    // vset[vac1,5,100e-3,0] -> VAC1=5V FV
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV
    VBAT_PD3_FXVI.Set(FV, 3.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VCC_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x20
    // delay 3ms → field[(DMUX_EN,1),(DMUX_SEL,40)] -> 0x56=0x28, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x20);
    delay_ms(3);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x28);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 4.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f);
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
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_PATH_ON_VCC_Rise->SetTestResult(site, 0, rise_result[site]);
        VBAT_PATH_ON_VCC_Fall->SetTestResult(site, 0, fall_result[site]);
        VBAT_PATH_ON_VCC_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM129: VCC_VBAT_HT_2P8 — VBAT 高压阈值 2.8V (Toggle, VBAT ramp)
// DFT: vset[vac1,5] → en_tm[] → 0x10=0x43, 0x29=0x10 → 0x56=0x3E, 0x57=0x08
//      → 扫 VBAT 0→3→0, 捕 DTEST0 (期望 r2.8 hys0.2)
// =====================================================================
DUT_API int TM129_VCC_VBAT_HT_2P8(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_HT_2P8_Rise = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Rise");
    CParam *VCC_VBAT_HT_2P8_Fall = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Fall");
    CParam *VCC_VBAT_HT_2P8_Hys = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 -> VAC123_AMUX_ACM: default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (ramp 源)
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,100e-3,0] -> VAC1=5V FV; VBAT 接 0V (ramp 源, 继电器 ON)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x10
    // field[(DMUX_EN,1),(DMUX_SEL,62)] -> 0x56=0x3E, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x3E);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 3.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           3.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f);
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
        VCC_VBAT_HT_2P8_Rise->SetTestResult(site, 0, rise_result[site]);
        VCC_VBAT_HT_2P8_Fall->SetTestResult(site, 0, fall_result[site]);
        VCC_VBAT_HT_2P8_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM130: VCC_VBAT_HT_3P7 — VBAT 高压阈值 3.7V (Toggle, VBAT ramp)
// DFT: vset[vac1,5] → en_tm[] → 0x10=0x43, 0x29=0x20 → 0x56=0x3F, 0x57=0x08
//      → 扫 VBAT 0→4.5→0, 捕 DTEST0 (期望 r3.7 hys0.2)
// 注: DFT 含 3 迭代 (VCC_FAVOR_VBAT=1/2/3 → 3.7/3.9/4.1V), testplan 仅单参数组,
//     本实现执行名义迭代 (VCC_FAVOR_VBAT=1 → 3.7V), 其余需 testplan 参数扩展
// =====================================================================
DUT_API int TM130_VCC_VBAT_HT_3P7(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_HT_3P7_Rise = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Rise");
    CParam *VCC_VBAT_HT_3P7_Fall = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Fall");
    CParam *VCC_VBAT_HT_3P7_Hys = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 -> VAC123_AMUX_ACM: default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (ramp 源)
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,100e-3,0] -> VAC1=5V FV; VBAT 接 0V (ramp 源, 继电器 ON)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1),(VCC_FAVOR_VBAT,1)] -> 0x10=0x43, 0x29=0x20
    // field[(DMUX_EN,1),(DMUX_SEL,63)] -> 0x56=0x3F, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x29, 0x20);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x3F);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 4.5, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.5, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f);
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
        VCC_VBAT_HT_3P7_Rise->SetTestResult(site, 0, rise_result[site]);
        VCC_VBAT_HT_3P7_Fall->SetTestResult(site, 0, fall_result[site]);
        VCC_VBAT_HT_3P7_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
