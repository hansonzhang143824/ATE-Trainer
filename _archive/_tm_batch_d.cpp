// =====================================================================
// TM200: VTH_SCL_IN — SCL 输入阈值电压 (Toggle, SCL ramp)
// DFT: vset[vbat,5] → en_tm[] → 0x56=0x05, 0x57=0x08 → 扫 SCL 0→3→0, 捕 DTEST0
// 期望: rising<1.4V, falling>0.6V
// =====================================================================
DUT_API int TM200_VTH_SCL_IN(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTH_SCL_IN_Rise = StsGetParam(funcindex, "VTH_SCL_IN_Rise");
    CParam *VTH_SCL_IN_Fall = StsGetParam(funcindex, "VTH_SCL_IN_Fall");
    CParam *VTH_SCL_IN_Hys = StsGetParam(funcindex, "VTH_SCL_IN_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // SCL  -> SCL_VACWL_ACM: default NC (ACM2)
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(DMUX_EN,1),(DMUX_SEL,5)] -> 0x56=0x05, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 3.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
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
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VTH_SCL_IN_Rise->SetTestResult(site, 0, rise_result[site]);
        VTH_SCL_IN_Fall->SetTestResult(site, 0, fall_result[site]);
        VTH_SCL_IN_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM201: VTH_SDA_IN — SDA 输入阈值电压 (Toggle, SDA ramp)
// DFT: vset[vbat,5] → en_tm[] → 0x56=0x06, 0x57=0x08 → 扫 SDA 0→3→0, 捕 DTEST0
// 注意: SDA 经 K59_ACM7_SDA 切至 ACM7, 用 VDM_SDA_ACM 驱动 SDA
// =====================================================================
DUT_API int TM201_VTH_SDA_IN(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTH_SDA_IN_Rise = StsGetParam(funcindex, "VTH_SDA_IN_Rise");
    CParam *VTH_SDA_IN_Fall = StsGetParam(funcindex, "VTH_SDA_IN_Fall");
    CParam *VTH_SDA_IN_Hys = StsGetParam(funcindex, "VTH_SDA_IN_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // SDA  -> VDM_SDA_ACM: K59_ACM7_SDA (ACM7 切至 SDA)
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K59_ACM7_SDA, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(DMUX_EN,1),(DMUX_SEL,6)] -> 0x56=0x06, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VDM_SDA_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 3.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VDM_SDA_ACM, ACM200_10V, ACM200_100MA,
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
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VTH_SDA_IN_Rise->SetTestResult(site, 0, rise_result[site]);
        VTH_SDA_IN_Fall->SetTestResult(site, 0, fall_result[site]);
        VTH_SDA_IN_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM202: R_INT — INT 引脚上拉电阻 (MI, Ω)
// DFT: vset[vbat,4] → en_tm[] → 0x67=0x31, 0x68=0x30 → 灌 10uA 测 V → R=V/I
// 注意: INT 与 SDA 共享 ACM7 测试线, SetOn K59_ACM7_SDA
// =====================================================================
DUT_API int TM202_R_INT(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *R_INT = StsGetParam(funcindex, "R_INT");
    //}}AFX_STS_PARAM_PROTOTYPES

    double r_int[SITE_NUM] = { 0 };
    double v_measure[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // INT  -> VDM_SDA_ACM: K59_ACM7_SDA (SDA/INT 共享测试线)
    cbite.SetOn(K59_ACM7_SDA, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(PAD_SEL_INT,1),...] -> 0x67=0x31, 0x68=0x30
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x67, 0x31);
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
    delay_ms(1);

    // ====== Step 4: Measure ======
    // FI=10uA 灌入 INT 测试线, 测 V → R = V/10uA
    // 量程规则: 10uA×2=20uA → 100UA (DFT 写 10UA 满量程太近, 升一档)
    VDM_SDA_ACM.Set(FI, 0.00001, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        v_measure[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
        r_int[site] = v_measure[site] / 1e-5;  // R = V / 10uA (Ω)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        R_INT->SetTestResult(site, 0, r_int[site]);
    }
    return 0;
}

// =====================================================================
// TM203: R_SDA — SDA 引脚电阻 (MI, Ω)
// DFT: vset[vbat,4] → en_tm[] → 0x67=0x32, 0x68=0x30 → 灌 10uA 测 V → R=V/I
// =====================================================================
DUT_API int TM203_R_SDA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *R_SDA = StsGetParam(funcindex, "R_SDA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double r_sda[SITE_NUM] = { 0 };
    double v_measure[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // SDA  -> VDM_SDA_ACM: K59_ACM7_SDA
    cbite.SetOn(K59_ACM7_SDA, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(PAD_SEL_SDA,1),...] -> 0x67=0x32, 0x68=0x30
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x67, 0x32);
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
    delay_ms(1);

    // ====== Step 4: Measure ======
    // FI=10uA 灌入 SDA 测试线, 测 V → R = V/10uA
    VDM_SDA_ACM.Set(FI, 0.00001, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        v_measure[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
        r_sda[site] = v_measure[site] / 1e-5;  // R = V / 10uA (Ω)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        R_SDA->SetTestResult(site, 0, r_sda[site]);
    }
    return 0;
}

// =====================================================================
// TM204: IPD_VBUS — VBUS 放电电流 (MI, mA)
// DFT: vset[vbat,4] → delay 5ms → vset[vbus,5] → 0x08=0x08→delay→0x00→delay→0x08→delay
//      → Check: I(VBUS) (20mA)
// 注意: wait_warmup 不调用
// =====================================================================
DUT_API int TM204_IPD_VBUS(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VBUS = StsGetParam(funcindex, "IPD_VBUS");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ipd_vbus[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: K4 default NC
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; delay 5ms
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(5);
    // vset[vbus,5,100e-3,0] -> VBUS=5V FV (wait_warmup 不调用)
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // 0x08=0x08 → delay → 0x00 → delay → 0x08 → delay (IPD 使能切换)
    I2CWriteSameData(DEV_ADDR, 0x08, 0x08);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x08, 0x00);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x08, 0x08);
    delay_ms(1);

    // ====== Step 4: Measure ======
    // 测 I(VBUS) 放电电流 (100MA≥2×20mA)
    VBUS_DRVH1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vbus[site] = VBUS_DRVH1_ACM.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPD_VBUS->SetTestResult(site, 0, ipd_vbus[site]);
    }
    return 0;
}

// =====================================================================
// TM207: IPD_VAC3 — VAC3 放电电流 (MI, mA)
// DFT: vset[vbat,4] → en_tm[]? → 0x08=0x10 → vset[vac3,1] 测 I, vset[vac3,4] 测 I
// 注意: wait_warmup 不调用; 单参数组, 记录 4V 档结果
// =====================================================================
DUT_API int TM207_IPD_VAC3(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VAC3 = StsGetParam(funcindex, "IPD_VAC3");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ipd_vac3_1v[SITE_NUM] = { 0 };
    double ipd_vac3_4v[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC3 -> VAC123_AMUX_ACM: K18_ACM0_VAC3
    cbite.SetOn(K18_ACM0_VAC3, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV (wait_warmup 不调用)
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // 0x08=0x10 (VAC3 IPD 使能)
    I2CWriteSameData(DEV_ADDR, 0x08, 0x10);
    delay_ms(1);

    // ====== Step 4: Measure ======
    // vset[vac3,1]: VAC3=1V FV, 测 I(VAC3)
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vac3_1v[site] = VAC123_AMUX_ACM.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }
    // vset[vac3,4]: VAC3=4V FV, 测 I(VAC3)
    VAC123_AMUX_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vac3_4v[site] = VAC123_AMUX_ACM.GetMeasResult(site, MIRET) * 1e3;  // A → mA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData (单参数组, 记录 4V 档结果) ======
    FOR_EACH_VALID_SITE(site)
    {
        IPD_VAC3->SetTestResult(site, 0, ipd_vac3_4v[site]);
    }
    return 0;
}

// =====================================================================
// TM210: VAC1_SNK_DET_VTH_RELMODE — VAC1 吸收检测阈值, REL 模式 (Toggle)
// DFT: vset[vbat,4] → en_tm[] → 0x07=0x03 → 0x56=0x02, 0x57=0x08 → delay 10ms
//      → 扫 VAC1 0→5→0, 捕 DTEST0 (慢段前置检查 + 快段捕获)
// =====================================================================
DUT_API int TM210_VAC1_SNK_DET_VTH_RELMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_SNK_DET_VTH_RELMODE_Rise = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Rise");
    CParam *VAC1_SNK_DET_VTH_RELMODE_Fall = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Fall");
    CParam *VAC1_SNK_DET_VTH_RELMODE_Hys = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(SNK_DET_MODE,3)] -> 0x07=0x03 (REL 模式)
    // field[(DMUX_EN,1),(DMUX_SEL,2)] -> 0x56=0x02, 0x57=0x08; delay 10ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x03);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(10);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // DFT 含慢段(2e-3)前置检查 + 快段(0.1e-3)捕获; 前置检查由 ramp 前 settle 替代
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
        VAC1_SNK_DET_VTH_RELMODE_Rise->SetTestResult(site, 0, rise_result[site]);
        VAC1_SNK_DET_VTH_RELMODE_Fall->SetTestResult(site, 0, fall_result[site]);
        VAC1_SNK_DET_VTH_RELMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM211: VAC2_SNK_DET_VTH_RELMODE — VAC2 吸收检测阈值, REL 模式 (Toggle)
// DFT: vset[vbat,4] → en_tm[] → 0x07=0x05 → 0x56=0x2C, 0x57=0x08 → 扫 VAC2 0→5→0
// =====================================================================
DUT_API int TM211_VAC2_SNK_DET_VTH_RELMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_SNK_DET_VTH_RELMODE_Rise = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Rise");
    CParam *VAC2_SNK_DET_VTH_RELMODE_Fall = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Fall");
    CParam *VAC2_SNK_DET_VTH_RELMODE_Hys = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC2 -> VAC123_AMUX_ACM: K19_ACM0_VAC2
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K19_ACM0_VAC2, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(SNK_DET_MODE,5)] -> 0x07=0x05 (REL 模式)
    // field[(DMUX_EN,1),(DMUX_SEL,44)] -> 0x56=0x2C, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x05);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2C);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(10);

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
        VAC2_SNK_DET_VTH_RELMODE_Rise->SetTestResult(site, 0, rise_result[site]);
        VAC2_SNK_DET_VTH_RELMODE_Fall->SetTestResult(site, 0, fall_result[site]);
        VAC2_SNK_DET_VTH_RELMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM212: VAC1_SNK_DET_VTH_ABSMODE — VAC1 吸收检测阈值, ABS 模式 (Toggle)
// DFT: vset[vbat,4] → en_tm[] → 0x07=0x02 → 0x56=0x02, 0x57=0x08 → 扫 VAC1 0→5→0
// 期望: R:1.9V / F:1.7V
// =====================================================================
DUT_API int TM212_VAC1_SNK_DET_VTH_ABSMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Rise = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Rise");
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Fall = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Fall");
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Hys = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(SNK_DET_MODE,2)] -> 0x07=0x02 (ABS 模式)
    // field[(DMUX_EN,1),(DMUX_SEL,2)] -> 0x56=0x02, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(10);

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
        VAC1_SNK_DET_VTH_ABSMODE_Rise->SetTestResult(site, 0, rise_result[site]);
        VAC1_SNK_DET_VTH_ABSMODE_Fall->SetTestResult(site, 0, fall_result[site]);
        VAC1_SNK_DET_VTH_ABSMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM213: VAC2_SNK_DET_VTH_ABSMODE — VAC2 吸收检测阈值, ABS 模式 (Toggle)
// DFT: vset[vbat,4] → en_tm[] → 0x07=0x04 → 0x56=0x2C, 0x57=0x08 → 扫 VAC2 0→5→0
// =====================================================================
DUT_API int TM213_VAC2_SNK_DET_VTH_ABSMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Rise = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Rise");
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Fall = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Fall");
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Hys = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC2 -> VAC123_AMUX_ACM: K19_ACM0_VAC2
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K19_ACM0_VAC2, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(SNK_DET_MODE,4)] -> 0x07=0x04 (ABS 模式)
    // field[(DMUX_EN,1),(DMUX_SEL,44)] -> 0x56=0x2C, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x04);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2C);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(10);

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
        VAC2_SNK_DET_VTH_ABSMODE_Rise->SetTestResult(site, 0, rise_result[site]);
        VAC2_SNK_DET_VTH_ABSMODE_Fall->SetTestResult(site, 0, fall_result[site]);
        VAC2_SNK_DET_VTH_ABSMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM214: PWM1_Vth — PWM1 输入阈值电压 (Toggle, PWM1 ramp)
// DFT: vset[vbat,4] → en_tm[] → 0x10=0x43 → 0x56=0x2E, 0x57=0x08
//      → 0x67=0x30, 0x68=0x30 → delay 2ms → 扫 PWM1 0→4→0, 捕 DTEST0
// 期望: R:1.4V / F:0.6V
// =====================================================================
DUT_API int TM214_PWM1_Vth(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM1_Vth_Rise = StsGetParam(funcindex, "PWM1_Vth_Rise");
    CParam *PWM1_Vth_Fall = StsGetParam(funcindex, "PWM1_Vth_Fall");
    CParam *PWM1_Vth_Hys = StsGetParam(funcindex, "PWM1_Vth_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // PWM1 -> PB0_BST_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,46)] -> 0x56=0x2E, 0x57=0x08
    // field[(PAD_SEL_PWM1,1),...] -> 0x67=0x30, 0x68=0x30; delay 2ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2E);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(PB0_BST_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 4.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(PB0_BST_ACM, ACM200_10V, ACM200_100MA,
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
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        PWM1_Vth_Rise->SetTestResult(site, 0, rise_result[site]);
        PWM1_Vth_Fall->SetTestResult(site, 0, fall_result[site]);
        PWM1_Vth_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM215: PWM2_Vth — PWM2 输入阈值电压 (Toggle, PWM2 ramp)
// DFT: vset[vbat,4] → en_tm[] → 0x10=0x43 → 0x56=0x2D, 0x57=0x08
//      → 0x67=0x30, 0x68=0x30 → delay 2ms → 扫 PWM2 0→4→0, 捕 DTEST0
// =====================================================================
DUT_API int TM215_PWM2_Vth(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM2_Vth_Rise = StsGetParam(funcindex, "PWM2_Vth_Rise");
    CParam *PWM2_Vth_Fall = StsGetParam(funcindex, "PWM2_Vth_Fall");
    CParam *PWM2_Vth_Hys = StsGetParam(funcindex, "PWM2_Vth_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // PWM2 -> PA6_PC5_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,45)] -> 0x56=0x2D, 0x57=0x08
    // field[(PAD_SEL_PWM2,1),...] -> 0x67=0x30, 0x68=0x30; delay 2ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2D);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(PA6_PC5_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, 4.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(PA6_PC5_ACM, ACM200_10V, ACM200_100MA,
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
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        PWM2_Vth_Rise->SetTestResult(site, 0, rise_result[site]);
        PWM2_Vth_Fall->SetTestResult(site, 0, fall_result[site]);
        PWM2_Vth_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
