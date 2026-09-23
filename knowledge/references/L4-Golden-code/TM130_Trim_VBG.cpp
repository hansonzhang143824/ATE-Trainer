// ===================================================================
// TM130: Trim_VBG — Bandgap 电压 Trim (AMUX MV, 16 steps)
// ===================================================================
// DFT: vset[vbat,4.2], Check: AMUX MV
// treg: "bandgap" (4位, step0~step15)
// 简单Trim: 无FPVI, 无浮动源, 无BST
// ===================================================================
DUT_API int TM130_Trim_VBG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PARAM_step0  = StsGetParam(funcindex, "PARAM_step0");
    CParam *PARAM_step1  = StsGetParam(funcindex, "PARAM_step1");
    CParam *PARAM_step2  = StsGetParam(funcindex, "PARAM_step2");
    CParam *PARAM_step3  = StsGetParam(funcindex, "PARAM_step3");
    CParam *PARAM_step4  = StsGetParam(funcindex, "PARAM_step4");
    CParam *PARAM_step5  = StsGetParam(funcindex, "PARAM_step5");
    CParam *PARAM_step6  = StsGetParam(funcindex, "PARAM_step6");
    CParam *PARAM_step7  = StsGetParam(funcindex, "PARAM_step7");
    CParam *PARAM_step8  = StsGetParam(funcindex, "PARAM_step8");
    CParam *PARAM_step9  = StsGetParam(funcindex, "PARAM_step9");
    CParam *PARAM_step10 = StsGetParam(funcindex, "PARAM_step10");
    CParam *PARAM_step11 = StsGetParam(funcindex, "PARAM_step11");
    CParam *PARAM_step12 = StsGetParam(funcindex, "PARAM_step12");
    CParam *PARAM_step13 = StsGetParam(funcindex, "PARAM_step13");
    CParam *PARAM_step14 = StsGetParam(funcindex, "PARAM_step14");
    CParam *PARAM_step15 = StsGetParam(funcindex, "PARAM_step15");
    CParam *PARAM_pre_value  = StsGetParam(funcindex, "PARAM_pre_value");
    CParam *PARAM_pre_bit    = StsGetParam(funcindex, "PARAM_pre_bit");
    CParam *PARAM_post_bit   = StsGetParam(funcindex, "PARAM_post_bit");
    CParam *PARAM_updated    = StsGetParam(funcindex, "PARAM_updated");
    CParam *PARAM_guessed    = StsGetParam(funcindex, "PARAM_guessed");
    CParam *PARAM_target     = StsGetParam(funcindex, "PARAM_target");
    CParam *PARAM_post_value = StsGetParam(funcindex, "PARAM_post_value");
    CParam *PARAM_post_rt    = StsGetParam(funcindex, "PARAM_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("bandgap");

    // ====== Step 1: 继电器闭合 ======
    // K30_VBAT_Cap: VBAT Cap2 (供电, MV模式→ON)
    // AMUX_FOVI: Default直连, 无需额外继电器
    cbite.SetOn(K30_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 ======
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 ======
    entertestmode();
    // Bandgap: EN_ATEST0=1, ATEST0_MUX=12, D2A_OVRD_SEL=10, OVRD_VALUE=3
    I2CWriteSameData(DEV_ADDR, 0x56, 0x62);
    I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
    delay_ms(2);  // Bandgap 稳定时间

    // ====== Step 4: Trim execute ======
    PARAM_NODE.execute(measure_HP_VBG, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: 下电 ======
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    return 0;
}
