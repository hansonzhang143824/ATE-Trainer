// =====================================================================
// TM216: PWM1_Current — PWM1 漏电流 (MI, uA)
// DFT: vset[vbat,4] → en_tm[] → 0x10=0x43 → 0x56=0x2E, 0x57=0x08
//      → 0x67=0x30, 0x68=0x30 → delay 2ms → PWM1 FV=0 测 I(PWM1) (10uA)
// Loop: VBAT_PD3_FXVI + PB0_BST_ACM
// 测量: PWM1 FV=0V, MI 量程 100UA (R-PON-09 digital 两段式)
// =====================================================================
DUT_API int TM216_PWM1_Current(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM1_Current = StsGetParam(funcindex, "PWM1_Current");
    //}}AFX_STS_PARAM_PROTOTYPES

    double pwm1_curr[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // PWM1 -> PB0_BST_ACM: default NC
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
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

    // ====== Step 4: Measure ======
    // vset[pwm1,0]: PWM1 FV=0V, 测 I(PWM1) 漏电流 (Expect 10uA)
    // R-PON-09 digital 两段式: 10MA→500us→测量量程 100UA (table_max 50uA ≥ 2×10uA)
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_us(500);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    PB0_BST_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        pwm1_curr[site] = PB0_BST_ACM.GetMeasResult(site, MIRET) * 1e6;  // A -> uA (R-LOG)
    }

    // ====== Step 5: Power Off (三步下电) ======
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        PWM1_Current->SetTestResult(site, 0, pwm1_curr[site]);
    }
    return 0;
}

// =====================================================================
// TM217: PWM2_Current — PWM2 漏电流 (MI, uA)
// DFT: vset[vbat,4] → en_tm[] → 0x10=0x43 → 0x56=0x2D, 0x57=0x08
//      → 0x67=0x30, 0x68=0x30 → delay 2ms → PWM2 FV=0 测 I(PWM2) (10uA)
// Loop: VBAT_PD3_FXVI + PA6_PC5_ACM
// 测量: PWM2 FV=0V, MI 量程 100UA (R-PON-09 digital 两段式)
// =====================================================================
DUT_API int TM217_PWM2_Current(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM2_Current = StsGetParam(funcindex, "PWM2_Current");
    //}}AFX_STS_PARAM_PROTOTYPES

    double pwm2_curr[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // PWM2 -> PA6_PC5_ACM: default NC
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
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

    // ====== Step 4: Measure ======
    // vset[pwm2,0]: PWM2 FV=0V, 测 I(PWM2) 漏电流 (Expect 10uA)
    // R-PON-09 digital 两段式: 10MA→500us→测量量程 100UA (table_max 50uA ≥ 2×10uA)
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_us(500);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    PA6_PC5_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        pwm2_curr[site] = PA6_PC5_ACM.GetMeasResult(site, MIRET) * 1e6;  // A -> uA (R-LOG)
    }

    // ====== Step 5: Power Off (三步下电) ======
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        PWM2_Current->SetTestResult(site, 0, pwm2_curr[site]);
    }
    return 0;
}

// =====================================================================
// TM220: DMO_PD_R — DMO pulldown 导通电阻 (Ohm)
// DFT: vset[vbat,4] → en_tm[] → 0x71=0x2A → 0x56=0x16 → vset[vac1,0]
//      → delay 2ms → Measure Ron(DMO, AGND)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + PC8_PC6_ACM
// 测量: VAC1=0V 使 DMO 输出低, DMO FI=1mA, R = 实测MVRET/实测MIRET (R-VIR)
// =====================================================================
DUT_API int TM220_DMO_PD_R(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *DMO_PD_R = StsGetParam(funcindex, "DMO_PD_R");
    //}}AFX_STS_PARAM_PROTOTYPES

    double dmo_ron[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    // DMO -> PC8_PC6_ACM: K95 default NC
    // K13_VBAT_Cap + K21_VAC_Cap: VBAT/VAC1 供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMO_EN,1),(D2A_DMO_CHANNEL_SEL,1)] -> 0x71=0x2A
    // field[(DMUX_SEL,22)] -> 0x56=0x16
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x71, 0x2A);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);

    // ====== Step 4: Measure ======
    // vset[vac1,0]: VAC1=0V → DMO 数字输入低 → 输出拉低, 测 DMO→AGND 导通电阻
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    // DMO FI=1mA 灌电流 (量程 10MA, table_max 5m ≥ 2×1mA)
    PC8_PC6_ACM.Set(FI, 0.001, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    PC8_PC6_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        double v_meas = PC8_PC6_ACM.GetMeasResult(site, MVRET);
        double i_meas = PC8_PC6_ACM.GetMeasResult(site, MIRET);
        dmo_ron[site] = v_meas / i_meas;  // R = 实测V/实测I (R-VIR)
    }

    // ====== Step 5: Power Off (三步下电) ======
    PC8_PC6_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    PC8_PC6_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        DMO_PD_R->SetTestResult(site, 0, dmo_ron[site]);
    }
    return 0;
}

// =====================================================================
// TM222: DMA_PD_R — DMA pulldown 导通电阻 (Ohm)
// DFT: vset[vbat,4] → en_tm[] → 0x71=0x31 → 0x56=0x16 → vset[vac1,0]
//      → delay 2ms → Measure Ron(DMA, AGND)
// Loop: VBAT_PD3_FXVI + VAC123_AMUX_ACM + PA7_PD2_ACM
// 测量: VAC1=0V 使 DMA 输出低, DMA FI=1mA, R = 实测MVRET/实测MIRET (R-VIR)
// =====================================================================
DUT_API int TM222_DMA_PD_R(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *DMA_PD_R = StsGetParam(funcindex, "DMA_PD_R");
    //}}AFX_STS_PARAM_PROTOTYPES

    double dma_ron[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: default NC
    // DMA -> PA7_PD2_ACM: default NC
    // K13_VBAT_Cap + K21_VAC_Cap: VBAT/VAC1 供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMA_EN,1),(D2A_DMA_CHANNEL_SEL,1)] -> 0x71=0x31
    // field[(DMUX_SEL,22)] -> 0x56=0x16
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x71, 0x31);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);

    // ====== Step 4: Measure ======
    // vset[vac1,0]: VAC1=0V → DMA 数字输入低 → 输出拉低, 测 DMA→AGND 导通电阻
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    // DMA FI=1mA 灌电流 (量程 10MA, table_max 5m ≥ 2×1mA)
    PA7_PD2_ACM.Set(FI, 0.001, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    PA7_PD2_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        double v_meas = PA7_PD2_ACM.GetMeasResult(site, MVRET);
        double i_meas = PA7_PD2_ACM.GetMeasResult(site, MIRET);
        dma_ron[site] = v_meas / i_meas;  // R = 实测V/实测I (R-VIR)
    }

    // ====== Step 5: Power Off (三步下电) ======
    PA7_PD2_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    PA7_PD2_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        DMA_PD_R->SetTestResult(site, 0, dma_ron[site]);
    }
    return 0;
}

// =====================================================================
// TM300: OSC_64K — OSC64K 输出频率 (QTMU 测频, KHz)
// DFT: vset[vbat,4] → en_tm[] → 0x56=0x0C, 0x57=0x08 → delay 1ms
//      → 0xF2=0x04 (D2A_TRIM_OSC_64K=2) → delay 1ms → 测 DTEST0 频率
// Trim=Y 但无 .treg, 固定 trim 值暂测 (暂测默认值)
// Loop: VBAT_PD3_FXVI + QTMU_GP (nQON 经 K66)
// 测量: QTMU FREQ, nQON 观察 DTEST0 (DMUX_SEL=12 路由 OSC64K)
// =====================================================================
DUT_API int TM300_OSC_64K(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_64K_step0 = StsGetParam(funcindex, "OSC_64K_step0");
    CParam *OSC_64K_step1 = StsGetParam(funcindex, "OSC_64K_step1");
    CParam *OSC_64K_step2 = StsGetParam(funcindex, "OSC_64K_step2");
    CParam *OSC_64K_step3 = StsGetParam(funcindex, "OSC_64K_step3");
    CParam *OSC_64K_step4 = StsGetParam(funcindex, "OSC_64K_step4");
    CParam *OSC_64K_step5 = StsGetParam(funcindex, "OSC_64K_step5");
    CParam *OSC_64K_step6 = StsGetParam(funcindex, "OSC_64K_step6");
    CParam *OSC_64K_step7 = StsGetParam(funcindex, "OSC_64K_step7");
    CParam *OSC_64K_pre_value = StsGetParam(funcindex, "OSC_64K_pre_value");
    CParam *OSC_64K_pre_bit = StsGetParam(funcindex, "OSC_64K_pre_bit");
    CParam *OSC_64K_post_bit = StsGetParam(funcindex, "OSC_64K_post_bit");
    CParam *OSC_64K_updated = StsGetParam(funcindex, "OSC_64K_updated");
    CParam *OSC_64K_guessed = StsGetParam(funcindex, "OSC_64K_guessed");
    CParam *OSC_64K_target = StsGetParam(funcindex, "OSC_64K_target");
    CParam *OSC_64K_post_value = StsGetParam(funcindex, "OSC_64K_post_value");
    CParam *OSC_64K_post_rt = StsGetParam(funcindex, "OSC_64K_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &OSC_64K = trim_reg.trim("osc_64k");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> QTMU S10_CH0: K66_TMU_nQON (QTMU_GP.Connect 连接输入继电器)
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    // K65_nQON_PU: nQON high-Z 时上拉, QTMU 需完整数字摆幅
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (不含 CSpec) ======
    // field[(DMUX_EN,1),(DMUX_SEL,12)] -> 0x56=0x0C, 0x57=0x08; delay 1ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x0C);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);

    // ====== Step 4: Trim execute (measure_osc_64k 写 0xF2 + QTMU 测频) ======
    // ⚠ treg 无 [osc_64k] 段, trim 参数/写入地址待用户确认
    OSC_64K.execute(measure_osc_64k, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    return 0;
}

// =====================================================================
// TM301: OSC_4P5M — OSC4P5M 输出频率 Trim (Trim, QTMU 测频, 重构 MHz)
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43 → 0x56=0x33, 0x57=0x08
//      (DMUX_EN=1, DMUX_SEL=51 路由 OSC4P5M/128 foldback) → 测 nQON 频率
//      Trim='Y', Notes=TRIM_OSC_4P5M → treg key "osc_4p5m" (DFT Notes 列权威)
// treg: osc_4p5m, 16步(Target=4.5MHz, Table 0-15, 0xF1 bits 7-5 + 0xF2 bit0)
// 测量: measure_osc_4p5m (写 F1/F2 → QTMU 测 foldback ~35KHz → ×0.128 重构 MHz)
// Loop: VBAT_PD3_FXVI + QTMU_GP (nQON 经 K66)
// =====================================================================
// =====================================================================
DUT_API int TM301_OSC_4P5M(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_4P5M_step0 = StsGetParam(funcindex, "OSC_4P5M_step0");
    CParam *OSC_4P5M_step1 = StsGetParam(funcindex, "OSC_4P5M_step1");
    CParam *OSC_4P5M_step2 = StsGetParam(funcindex, "OSC_4P5M_step2");
    CParam *OSC_4P5M_step3 = StsGetParam(funcindex, "OSC_4P5M_step3");
    CParam *OSC_4P5M_step4 = StsGetParam(funcindex, "OSC_4P5M_step4");
    CParam *OSC_4P5M_step5 = StsGetParam(funcindex, "OSC_4P5M_step5");
    CParam *OSC_4P5M_step6 = StsGetParam(funcindex, "OSC_4P5M_step6");
    CParam *OSC_4P5M_step7 = StsGetParam(funcindex, "OSC_4P5M_step7");
    CParam *OSC_4P5M_step8 = StsGetParam(funcindex, "OSC_4P5M_step8");
    CParam *OSC_4P5M_step9 = StsGetParam(funcindex, "OSC_4P5M_step9");
    CParam *OSC_4P5M_step10 = StsGetParam(funcindex, "OSC_4P5M_step10");
    CParam *OSC_4P5M_step11 = StsGetParam(funcindex, "OSC_4P5M_step11");
    CParam *OSC_4P5M_step12 = StsGetParam(funcindex, "OSC_4P5M_step12");
    CParam *OSC_4P5M_step13 = StsGetParam(funcindex, "OSC_4P5M_step13");
    CParam *OSC_4P5M_step14 = StsGetParam(funcindex, "OSC_4P5M_step14");
    CParam *OSC_4P5M_step15 = StsGetParam(funcindex, "OSC_4P5M_step15");
    CParam *OSC_4P5M_pre_value = StsGetParam(funcindex, "OSC_4P5M_pre_value");
    CParam *OSC_4P5M_pre_bit = StsGetParam(funcindex, "OSC_4P5M_pre_bit");
    CParam *OSC_4P5M_post_bit = StsGetParam(funcindex, "OSC_4P5M_post_bit");
    CParam *OSC_4P5M_updated = StsGetParam(funcindex, "OSC_4P5M_updated");
    CParam *OSC_4P5M_guessed = StsGetParam(funcindex, "OSC_4P5M_guessed");
    CParam *OSC_4P5M_target = StsGetParam(funcindex, "OSC_4P5M_target");
    CParam *OSC_4P5M_post_value = StsGetParam(funcindex, "OSC_4P5M_post_value");
    CParam *OSC_4P5M_post_rt = StsGetParam(funcindex, "OSC_4P5M_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &OSC_4P5M = trim_reg.trim("osc_4p5m");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> QTMU S10_CH0: K66_TMU_nQON (QTMU_GP.Connect 连接输入继电器)
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    // K65_nQON_PU: nQON high-Z 时上拉, QTMU 需完整数字摆幅
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (不含 CSpec) ======
    // field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,51)] -> 0x56=0x33, 0x57=0x08; delay 1ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x33);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);

    // ====== Step 4: Trim execute (measure_osc_4p5m 写 F1/F2 + QTMU 测频) ======
    OSC_4P5M.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    return 0;
}// =====================================================================
DUT_API int TM400_VBUS_OVP_VTH1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH1_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH1_Rise");
    CParam *VBUS_OVP_VTH1_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH1_Fall");
    CParam *VBUS_OVP_VTH1_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH1_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // field[(WAKE_UP,1),(VBUS_OVP,0),(DMUX_EN,1),(DMUX_SEL,32)] -> 0x10=0x43, 0x56=0x20, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // nQON high-Z reads DTEST0 logic level; VBUS 4→7→4 ramp
    // VBUS 量程: 7V×2=14 > 10V档 table_max 5.0 → ACM200_40V (R-RNG)
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.0, 7.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           7.0, 4.0, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV, 电流→mA)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH1_Rise->SetTestResult(site, 0, rise_result[site]);
        VBUS_OVP_VTH1_Fall->SetTestResult(site, 0, fall_result[site]);
        VBUS_OVP_VTH1_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM401: VBUS_OVP_VTH2 — VBUS OVP 阈值 2 (Toggle, VBUS ramp)
// DFT: vset[vbat,4] → en_tm[] → 0x0C=0x08 → 0x10=0x43 → 0x56=0x20, 0x57=0x08
//      (VBUS_OVP=2) → VBUS 4→15→4 ramp, 捕 DTEST0 翻转
// 期望: rising 12.8V / hys 0.3V
// Loop: VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM401_VBUS_OVP_VTH2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH2_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH2_Rise");
    CParam *VBUS_OVP_VTH2_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH2_Fall");
    CParam *VBUS_OVP_VTH2_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH2_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // field[(VBUS_OVP,2)] -> 0x0C=0x08
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,32)] -> 0x10=0x43, 0x56=0x20, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x0C, 0x08);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // nQON high-Z reads DTEST0 logic level; VBUS 4→15→4 ramp
    // VBUS 量程: 15V×2=30 > 10V档 table_max 5.0 → ACM200_40V (R-RNG)
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.0, 15.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           15.0, 4.0, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV, 电流→mA)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH2_Rise->SetTestResult(site, 0, rise_result[site]);
        VBUS_OVP_VTH2_Fall->SetTestResult(site, 0, fall_result[site]);
        VBUS_OVP_VTH2_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM402: VBUS_OVP_VTH3 — VBUS OVP 阈值 3 (Toggle, VBUS ramp)
// DFT: vset[vbat,4] → en_tm[] → 0x0C=0x14 → 0x10=0x43 → 0x56=0x20, 0x57=0x08
//      → 0xFF=0x04 (VBUS_OVP=5, MPP_EN=1) → VBUS 4→20→4 ramp, 捕 DTEST0 翻转
// 期望: rising 18.8V / hys 0.3V
// Loop: VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM402_VBUS_OVP_VTH3(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH3_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH3_Rise");
    CParam *VBUS_OVP_VTH3_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH3_Fall");
    CParam *VBUS_OVP_VTH3_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH3_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // field[(VBUS_OVP,5),(MPP_EN,1)] -> 0x0C=0x14
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,32)] -> 0x10=0x43, 0x56=0x20, 0x57=0x08
    // field[(...)] -> 0xFF=0x04
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x0C, 0x14);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    I2CWriteSameData(DEV_ADDR, 0xFF, 0x04);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // nQON high-Z reads DTEST0 logic level; VBUS 4→20→4 ramp
    // VBUS 量程: 20V×2=40 > 10V档 table_max 5.0 → ACM200_40V (R-RNG)
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.0, 20.0, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           20.0, 4.0, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV, 电流→mA)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH3_Rise->SetTestResult(site, 0, rise_result[site]);
        VBUS_OVP_VTH3_Fall->SetTestResult(site, 0, fall_result[site]);
        VBUS_OVP_VTH3_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
