// =====================================================================
// TM131: IRPPO_EA_FB — IRPPO EA 反馈电压 (MV, ATEST0)
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43 (WAKE_UP=1)
//      → 0x57=0x02, 0x5E=0x06 (ATEST0_MUX=6 → IRPPO_EA_FB)
//      → vset[vdm,1.2] 稳定 → vset_off[vdm] → MV, Check: ~0.8V
// =====================================================================
DUT_API int TM131_IRPPO_EA_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IRPPO_EA_FB = StsGetParam(funcindex, "IRPPO_EA_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double irppo_ea_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);

    // ====== Step 4: Measure ======
    // vset[vdm,1.2]: 先稳定外部 pin 上电
    VDM_SDA_ACM.Set(FV, 1.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // field[(EN_ATEST0,1),(ATEST0_MUX,6)] → IRPPO_EA_FB 通路
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x06);
    // vset_off[vdm]: 释放 VDM pin — FV=1.2V 切到高阻 FI=0, DUT ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        irppo_ea_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IRPPO_EA_FB->SetTestResult(site, 0, irppo_ea_fb[site]);
    }
    return 0;
}

// =====================================================================
// TM132: IHR_P_1UA — IHR_P 电流 1uA (MI, ATEST0, uA)
// DFT: vset[vbat,5] vset[amux,1] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x07 (ATEST0_MUX=7 → IHR_P_1UA)
//      → vset[vdm,1] → Check: I(VDM) (1uA)
// 注意: MI 测试不闭合 K13_VBAT_Cap (电容影响电流测量)
// =====================================================================
DUT_API int TM132_IHR_P_1UA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IHR_P_1UA = StsGetParam(funcindex, "IHR_P_1UA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ihr_p_1ua[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // AMUX -> VAC123_AMUX_ACM: K20_ACM0_AMUX (AMUX=1V 偏置)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // ⚠MI测试不闭合 K13_VBAT_Cap
    cbite.SetOn(K20_ACM0_AMUX, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    // vset[amux,1,100e-3,0] -> AMUX=1V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);

    // ====== Step 4: Measure ======
    // field[(EN_ATEST0,1),(ATEST0_MUX,7)] → IHR_P_1UA 通路
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x07);
    // vset[vdm,1]: VDM=1V FV, 测 I(VDM) (10UA最小电流档)
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ihr_p_1ua[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET) * 1e6;  // A → uA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IHR_P_1UA->SetTestResult(site, 0, ihr_p_1ua[site]);
    }
    return 0;
}

// =====================================================================
// Trim_IZTC_RES (TM133) — IZTC_RES 电阻 Trim (MI, uA)
// treg: iztc_res, 64步(ASSY F0 bits 4-7 + F1 bits 0-1), Target=220uA
// DFT: vset[vbat,5] vset[amux,1] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x08 (ATEST0_MUX=8 → IZTC_RES) → vset[vdm,1]
// 测量: measure_iztc_res (写 F0+F1, VDM MI, -1×MIRET×1e6 uA)
// 注意: MI 测试不闭合 K13_VBAT_Cap
// =====================================================================
DUT_API int Trim_IZTC_RES(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IZTC_RES_step0 = StsGetParam(funcindex, "IZTC_RES_step0");
    CParam *IZTC_RES_step1 = StsGetParam(funcindex, "IZTC_RES_step1");
    CParam *IZTC_RES_step2 = StsGetParam(funcindex, "IZTC_RES_step2");
    CParam *IZTC_RES_step3 = StsGetParam(funcindex, "IZTC_RES_step3");
    CParam *IZTC_RES_step4 = StsGetParam(funcindex, "IZTC_RES_step4");
    CParam *IZTC_RES_step5 = StsGetParam(funcindex, "IZTC_RES_step5");
    CParam *IZTC_RES_step6 = StsGetParam(funcindex, "IZTC_RES_step6");
    CParam *IZTC_RES_step7 = StsGetParam(funcindex, "IZTC_RES_step7");
    CParam *IZTC_RES_step8 = StsGetParam(funcindex, "IZTC_RES_step8");
    CParam *IZTC_RES_step9 = StsGetParam(funcindex, "IZTC_RES_step9");
    CParam *IZTC_RES_step10 = StsGetParam(funcindex, "IZTC_RES_step10");
    CParam *IZTC_RES_step11 = StsGetParam(funcindex, "IZTC_RES_step11");
    CParam *IZTC_RES_step12 = StsGetParam(funcindex, "IZTC_RES_step12");
    CParam *IZTC_RES_step13 = StsGetParam(funcindex, "IZTC_RES_step13");
    CParam *IZTC_RES_step14 = StsGetParam(funcindex, "IZTC_RES_step14");
    CParam *IZTC_RES_step15 = StsGetParam(funcindex, "IZTC_RES_step15");
    CParam *IZTC_RES_step16 = StsGetParam(funcindex, "IZTC_RES_step16");
    CParam *IZTC_RES_step17 = StsGetParam(funcindex, "IZTC_RES_step17");
    CParam *IZTC_RES_step18 = StsGetParam(funcindex, "IZTC_RES_step18");
    CParam *IZTC_RES_step19 = StsGetParam(funcindex, "IZTC_RES_step19");
    CParam *IZTC_RES_step20 = StsGetParam(funcindex, "IZTC_RES_step20");
    CParam *IZTC_RES_step21 = StsGetParam(funcindex, "IZTC_RES_step21");
    CParam *IZTC_RES_step22 = StsGetParam(funcindex, "IZTC_RES_step22");
    CParam *IZTC_RES_step23 = StsGetParam(funcindex, "IZTC_RES_step23");
    CParam *IZTC_RES_step24 = StsGetParam(funcindex, "IZTC_RES_step24");
    CParam *IZTC_RES_step25 = StsGetParam(funcindex, "IZTC_RES_step25");
    CParam *IZTC_RES_step26 = StsGetParam(funcindex, "IZTC_RES_step26");
    CParam *IZTC_RES_step27 = StsGetParam(funcindex, "IZTC_RES_step27");
    CParam *IZTC_RES_step28 = StsGetParam(funcindex, "IZTC_RES_step28");
    CParam *IZTC_RES_step29 = StsGetParam(funcindex, "IZTC_RES_step29");
    CParam *IZTC_RES_step30 = StsGetParam(funcindex, "IZTC_RES_step30");
    CParam *IZTC_RES_step31 = StsGetParam(funcindex, "IZTC_RES_step31");
    CParam *IZTC_RES_step32 = StsGetParam(funcindex, "IZTC_RES_step32");
    CParam *IZTC_RES_step33 = StsGetParam(funcindex, "IZTC_RES_step33");
    CParam *IZTC_RES_step34 = StsGetParam(funcindex, "IZTC_RES_step34");
    CParam *IZTC_RES_step35 = StsGetParam(funcindex, "IZTC_RES_step35");
    CParam *IZTC_RES_step36 = StsGetParam(funcindex, "IZTC_RES_step36");
    CParam *IZTC_RES_step37 = StsGetParam(funcindex, "IZTC_RES_step37");
    CParam *IZTC_RES_step38 = StsGetParam(funcindex, "IZTC_RES_step38");
    CParam *IZTC_RES_step39 = StsGetParam(funcindex, "IZTC_RES_step39");
    CParam *IZTC_RES_step40 = StsGetParam(funcindex, "IZTC_RES_step40");
    CParam *IZTC_RES_step41 = StsGetParam(funcindex, "IZTC_RES_step41");
    CParam *IZTC_RES_step42 = StsGetParam(funcindex, "IZTC_RES_step42");
    CParam *IZTC_RES_step43 = StsGetParam(funcindex, "IZTC_RES_step43");
    CParam *IZTC_RES_step44 = StsGetParam(funcindex, "IZTC_RES_step44");
    CParam *IZTC_RES_step45 = StsGetParam(funcindex, "IZTC_RES_step45");
    CParam *IZTC_RES_step46 = StsGetParam(funcindex, "IZTC_RES_step46");
    CParam *IZTC_RES_step47 = StsGetParam(funcindex, "IZTC_RES_step47");
    CParam *IZTC_RES_step48 = StsGetParam(funcindex, "IZTC_RES_step48");
    CParam *IZTC_RES_step49 = StsGetParam(funcindex, "IZTC_RES_step49");
    CParam *IZTC_RES_step50 = StsGetParam(funcindex, "IZTC_RES_step50");
    CParam *IZTC_RES_step51 = StsGetParam(funcindex, "IZTC_RES_step51");
    CParam *IZTC_RES_step52 = StsGetParam(funcindex, "IZTC_RES_step52");
    CParam *IZTC_RES_step53 = StsGetParam(funcindex, "IZTC_RES_step53");
    CParam *IZTC_RES_step54 = StsGetParam(funcindex, "IZTC_RES_step54");
    CParam *IZTC_RES_step55 = StsGetParam(funcindex, "IZTC_RES_step55");
    CParam *IZTC_RES_step56 = StsGetParam(funcindex, "IZTC_RES_step56");
    CParam *IZTC_RES_step57 = StsGetParam(funcindex, "IZTC_RES_step57");
    CParam *IZTC_RES_step58 = StsGetParam(funcindex, "IZTC_RES_step58");
    CParam *IZTC_RES_step59 = StsGetParam(funcindex, "IZTC_RES_step59");
    CParam *IZTC_RES_step60 = StsGetParam(funcindex, "IZTC_RES_step60");
    CParam *IZTC_RES_step61 = StsGetParam(funcindex, "IZTC_RES_step61");
    CParam *IZTC_RES_step62 = StsGetParam(funcindex, "IZTC_RES_step62");
    CParam *IZTC_RES_step63 = StsGetParam(funcindex, "IZTC_RES_step63");
    CParam *IZTC_RES_pre_value = StsGetParam(funcindex, "IZTC_RES_pre_value");
    CParam *IZTC_RES_pre_bit = StsGetParam(funcindex, "IZTC_RES_pre_bit");
    CParam *IZTC_RES_post_bit = StsGetParam(funcindex, "IZTC_RES_post_bit");
    CParam *IZTC_RES_updated = StsGetParam(funcindex, "IZTC_RES_updated");
    CParam *IZTC_RES_guessed = StsGetParam(funcindex, "IZTC_RES_guessed");
    CParam *IZTC_RES_target = StsGetParam(funcindex, "IZTC_RES_target");
    CParam *IZTC_RES_post_value = StsGetParam(funcindex, "IZTC_RES_post_value");
    CParam *IZTC_RES_post_rt = StsGetParam(funcindex, "IZTC_RES_post_rt");
    CParam *NTC_20uA = StsGetParam(funcindex, "NTC_20uA");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("iztc_res");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // AMUX -> VAC123_AMUX_ACM: K20_ACM0_AMUX (AMUX=1V 偏置)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // ⚠MI 测试不闭合 K13_VBAT_Cap
    cbite.SetOn(K20_ACM0_AMUX, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    // vset[amux,1,100e-3,0] -> AMUX=1V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(EN_ATEST0,1),(ATEST0_MUX,8)] -> IZTC_RES 通路
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x08);

    // ====== Step 4: Measure (VDM FV=1V, Trim execute 写 EFUSE + MI) ======
    // vset[vdm,1]: VDM=1V FV, 测 I(VDM)
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    PARAM_NODE.execute(measure_iztc_res, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    return 0;
}

// =====================================================================
// TM134: IPTAT_1UA — IPTAT 电流 1uA (MI, ATEST0, uA)
// DFT: vset[vbat,5] vset[amux,1] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x09 (ATEST0_MUX=9 → IPTAT_1UA) → vset[vdm,1]
// 注意: MI 测试不闭合 K13_VBAT_Cap
// =====================================================================
DUT_API int TM134_IPTAT_1UA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPTAT_1UA = StsGetParam(funcindex, "IPTAT_1UA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iptat_1ua[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // AMUX -> VAC123_AMUX_ACM: K20_ACM0_AMUX
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // ⚠MI测试不闭合 K13_VBAT_Cap
    cbite.SetOn(K20_ACM0_AMUX, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    // vset[amux,1,100e-3,0] -> AMUX=1V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);

    // ====== Step 4: Measure ======
    // field[(EN_ATEST0,1),(ATEST0_MUX,9)] → IPTAT_1UA 通路
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x09);
    // vset[vdm,1]: VDM=1V FV, 测 I(VDM)
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iptat_1ua[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET) * 1e6;  // A → uA
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPTAT_1UA->SetTestResult(site, 0, iptat_1ua[site]);
    }
    return 0;
}

// =====================================================================
// Trim_BG_RES_DIV (TM135) — BG 电阻分压 Trim (MV, mV)
// treg: bg_res_div, 8步(ASSY F1 bits 2-4), Target=1000mV
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x0A (ATEST0_MUX=10 → BG_RES_DIV) → vset_off[vdm]
// 测量: measure_bg_res_div (写 F1, VDM MV, MVRET×1e3 mV)
// =====================================================================
DUT_API int Trim_BG_RES_DIV(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *BG_RES_DIV_step0 = StsGetParam(funcindex, "BG_RES_DIV_step0");
    CParam *BG_RES_DIV_step1 = StsGetParam(funcindex, "BG_RES_DIV_step1");
    CParam *BG_RES_DIV_step2 = StsGetParam(funcindex, "BG_RES_DIV_step2");
    CParam *BG_RES_DIV_step3 = StsGetParam(funcindex, "BG_RES_DIV_step3");
    CParam *BG_RES_DIV_step4 = StsGetParam(funcindex, "BG_RES_DIV_step4");
    CParam *BG_RES_DIV_step5 = StsGetParam(funcindex, "BG_RES_DIV_step5");
    CParam *BG_RES_DIV_step6 = StsGetParam(funcindex, "BG_RES_DIV_step6");
    CParam *BG_RES_DIV_step7 = StsGetParam(funcindex, "BG_RES_DIV_step7");
    CParam *BG_RES_DIV_pre_value = StsGetParam(funcindex, "BG_RES_DIV_pre_value");
    CParam *BG_RES_DIV_pre_bit = StsGetParam(funcindex, "BG_RES_DIV_pre_bit");
    CParam *BG_RES_DIV_post_bit = StsGetParam(funcindex, "BG_RES_DIV_post_bit");
    CParam *BG_RES_DIV_updated = StsGetParam(funcindex, "BG_RES_DIV_updated");
    CParam *BG_RES_DIV_guessed = StsGetParam(funcindex, "BG_RES_DIV_guessed");
    CParam *BG_RES_DIV_target = StsGetParam(funcindex, "BG_RES_DIV_target");
    CParam *BG_RES_DIV_post_value = StsGetParam(funcindex, "BG_RES_DIV_post_value");
    CParam *BG_RES_DIV_post_rt = StsGetParam(funcindex, "BG_RES_DIV_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("bg_res_div");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(EN_ATEST0,1),(ATEST0_MUX,10)] -> BG_RES_DIV 通路
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0A);

    // ====== Step 4: Measure (VDM high-Z, Trim execute 写 EFUSE + MV) ======
    // vset_off[vdm]: 释放 VDM pin — DUT ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    PARAM_NODE.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    return 0;
}

// =====================================================================
// TM136: AVSS_BG — AVSS 衬底电压 (MV, ATEST0, 期望 0V)
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x0B (ATEST0_MUX=11 → AVSS_BG)
// =====================================================================
DUT_API int TM136_AVSS_BG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *AVSS_BG = StsGetParam(funcindex, "AVSS_BG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double avss_bg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);

    // ====== Step 4: Measure ======
    // field[(EN_ATEST0,1),(ATEST0_MUX,11)] → AVSS_BG 通路 (期望 ~0V)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0B);
    // vset_off[vdm]: 释放 VDM pin — DUT ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        avss_bg[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        AVSS_BG->SetTestResult(site, 0, avss_bg[site]);
    }
    return 0;
}

// =====================================================================
// TM137: TSD_TM — 过温关断比较器 (MV, DTEST0, 期望 V(DTEST0))
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43
//      → 0x56=0x12, 0x57=0x08 (TSD 比较器→DTEST0), delay 1ms → 0x58=0x40
// 测量: nQON high-Z 读 V(DTEST0) 逻辑电平
// =====================================================================
DUT_API int TM137_TSD_TM(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *TSD_TM = StsGetParam(funcindex, "TSD_TM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double tsd_tm[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,18)] -> 0x56=0x12, 0x57=0x08, delay 1ms
    // field[(D2A_BG_TM_TSD,1)] -> 0x58=0x40
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x12);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x40);

    // ====== Step 4: Measure ======
    // nQON high-Z 读 V(DTEST0) 逻辑电平
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    NQON_HG1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        tsd_tm[site] = NQON_HG1_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        TSD_TM->SetTestResult(site, 0, tsd_tm[site]);
    }
    return 0;
}

// =====================================================================
// TM138: TDIE_WARM_TM — 芯片温度偏置比较器 (MV, DTEST0, 期望 V(DTEST0))
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43
//      → 0x56=0x11, 0x57=0x08 (TDIE 比较器→DTEST0), delay 1ms → 0x58=0x40
// =====================================================================
DUT_API int TM138_TDIE_WARM_TM(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *TDIE_WARM_TM = StsGetParam(funcindex, "TDIE_WARM_TM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double tdie_warm_tm[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> NQON_HG1_ACM: K64 direct + K65_nQON_PU pull-up
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,17)] -> 0x56=0x11, 0x57=0x08, delay 1ms
    // field[(D2A_BG_TM_TSD,1)] -> 0x58=0x40
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x11);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x40);

    // ====== Step 4: Measure ======
    // nQON high-Z 读 V(DTEST0) 逻辑电平
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    NQON_HG1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        tdie_warm_tm[site] = NQON_HG1_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        TDIE_WARM_TM->SetTestResult(site, 0, tdie_warm_tm[site]);
    }
    return 0;
}

// =====================================================================
// Trim_VBG (TM139) — Bandgap 电压 Trim (MV, mV)
// treg: bandgap, 16步(ASSY F0 bits 0-3), Target=1220mV
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43
//      → 0x57=0x02, 0x5E=0x0C (ATEST0_MUX=12 → VBG) → vset_off[vdm]
// 测量: measure_bandgap (写 F0, VDM MV, MVRET×1e3 mV)
// =====================================================================
DUT_API int Trim_VBG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *BG_AVSS = StsGetParam(funcindex, "BG_AVSS");
    CParam *VBG_step0 = StsGetParam(funcindex, "VBG_step0");
    CParam *VBG_step1 = StsGetParam(funcindex, "VBG_step1");
    CParam *VBG_step2 = StsGetParam(funcindex, "VBG_step2");
    CParam *VBG_step3 = StsGetParam(funcindex, "VBG_step3");
    CParam *VBG_step4 = StsGetParam(funcindex, "VBG_step4");
    CParam *VBG_step5 = StsGetParam(funcindex, "VBG_step5");
    CParam *VBG_step6 = StsGetParam(funcindex, "VBG_step6");
    CParam *VBG_step7 = StsGetParam(funcindex, "VBG_step7");
    CParam *VBG_step8 = StsGetParam(funcindex, "VBG_step8");
    CParam *VBG_step9 = StsGetParam(funcindex, "VBG_step9");
    CParam *VBG_step10 = StsGetParam(funcindex, "VBG_step10");
    CParam *VBG_step11 = StsGetParam(funcindex, "VBG_step11");
    CParam *VBG_step12 = StsGetParam(funcindex, "VBG_step12");
    CParam *VBG_step13 = StsGetParam(funcindex, "VBG_step13");
    CParam *VBG_step14 = StsGetParam(funcindex, "VBG_step14");
    CParam *VBG_step15 = StsGetParam(funcindex, "VBG_step15");
    CParam *VBG_pre_value = StsGetParam(funcindex, "VBG_pre_value");
    CParam *VBG_pre_bit = StsGetParam(funcindex, "VBG_pre_bit");
    CParam *VBG_post_bit = StsGetParam(funcindex, "VBG_post_bit");
    CParam *VBG_updated = StsGetParam(funcindex, "VBG_updated");
    CParam *VBG_guessed = StsGetParam(funcindex, "VBG_guessed");
    CParam *VBG_target = StsGetParam(funcindex, "VBG_target");
    CParam *VBG_post_value = StsGetParam(funcindex, "VBG_post_value");
    CParam *VBG_post_rt = StsGetParam(funcindex, "VBG_post_rt");
    CParam *VBG_Filter = StsGetParam(funcindex, "VBG_Filter");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("bandgap");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] + field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(EN_ATEST0,1),(ATEST0_MUX,12)] -> VBG 通路
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0C);

    // ====== Step 4: Measure (VDM high-Z, Trim execute 写 EFUSE + MV) ======
    // vset_off[vdm]: 释放 VDM pin — DUT ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    PARAM_NODE.execute(measure_bandgap, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    return 0;
}
