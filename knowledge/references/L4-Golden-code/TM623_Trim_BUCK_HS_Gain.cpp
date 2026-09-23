// ===================================================================
// TM623: Trim_BUCK_HS_Gain — Buck HS Current Sense Gain Trim
// ===================================================================
// DFT: vset[vbat,5], vset[pmid,5], vset[bst2sw,5], vset[vdrv,5]
//      iset[pmid2sw,3A], Check: AMUX-NTC MV
// treg: "buck_hsfet_gain" (5位, step0~step31)
// FET: C1(PMID↔SW), 0x59 HS导通
// 闭环: FPVI→K31→PMID→HS FET→SW→K17→FPVI (3A大电流)
// BST: BTST_ACM独立, ramp至10V保证BST-SW=5V
// ===================================================================
DUT_API int TM623_Trim_BUCK_HS_Gain(short funcindex, LPCTSTR funclabel)
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
    CParam *PARAM_step16 = StsGetParam(funcindex, "PARAM_step16");
    CParam *PARAM_step17 = StsGetParam(funcindex, "PARAM_step17");
    CParam *PARAM_step18 = StsGetParam(funcindex, "PARAM_step18");
    CParam *PARAM_step19 = StsGetParam(funcindex, "PARAM_step19");
    CParam *PARAM_step20 = StsGetParam(funcindex, "PARAM_step20");
    CParam *PARAM_step21 = StsGetParam(funcindex, "PARAM_step21");
    CParam *PARAM_step22 = StsGetParam(funcindex, "PARAM_step22");
    CParam *PARAM_step23 = StsGetParam(funcindex, "PARAM_step23");
    CParam *PARAM_step24 = StsGetParam(funcindex, "PARAM_step24");
    CParam *PARAM_step25 = StsGetParam(funcindex, "PARAM_step25");
    CParam *PARAM_step26 = StsGetParam(funcindex, "PARAM_step26");
    CParam *PARAM_step27 = StsGetParam(funcindex, "PARAM_step27");
    CParam *PARAM_step28 = StsGetParam(funcindex, "PARAM_step28");
    CParam *PARAM_step29 = StsGetParam(funcindex, "PARAM_step29");
    CParam *PARAM_step30 = StsGetParam(funcindex, "PARAM_step30");
    CParam *PARAM_step31 = StsGetParam(funcindex, "PARAM_step31");
    CParam *PARAM_pre_value  = StsGetParam(funcindex, "PARAM_pre_value");
    CParam *PARAM_pre_bit    = StsGetParam(funcindex, "PARAM_pre_bit");
    CParam *PARAM_post_bit   = StsGetParam(funcindex, "PARAM_post_bit");
    CParam *PARAM_updated    = StsGetParam(funcindex, "PARAM_updated");
    CParam *PARAM_guessed    = StsGetParam(funcindex, "PARAM_guessed");
    CParam *PARAM_target     = StsGetParam(funcindex, "PARAM_target");
    CParam *PARAM_post_value = StsGetParam(funcindex, "PARAM_post_value");
    CParam *PARAM_post_rt    = StsGetParam(funcindex, "PARAM_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("buck_hsfet_gain");

    // ====== Step 1: 继电器闭合 ======
    // FPVI_BUS: K31(PMID→BUS) + K17(SW→BUS) → PMID↔SW 3A大电流闭环
    // BST-SW: K18_BST_SW_Cap P2P电容, BTST_ACM独立供BST
    // Cap2: K32_PMID_Cap(FPVI浮动MI), K30_VBAT_Cap(供电), K28_VDRV_Cap(供电)
    // AMUX/NTC: FOVI Default直连, 不参与BUS
    cbite.SetOn(K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 (BST领先PMID 5V台阶ramp) ======
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);

    VBAT_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5V(ACM200_10V), PMID=0V
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V(ACM200_40V), PMID=5V → FET导通后 SW→5V, BST-SW=5V ✓
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 ======
    entertestmode();
    // WAKE_UP=1, TM_HSON=1, EN_FORCE_ON=1, TM_DIS_CLK=1
    // EN_ATEST0=1, EN_ATEST1=1
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HS FET导通 → PMID=SW
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
    // [电压推断] FET导通C1 → SW=PMID=5V, BST=10V, BST-SW=5V ✓

    // ====== Step 4: FPVI 大电流初始化 ======
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.SetClamp(50, 50);

    // ====== Step 5: Trim execute ======
    PARAM_NODE.execute(measure_BUCK_HS_CS_GAIN, spec, funcindex, funclabel, 1, 0, 0, 0);
   
    // ====== Step 6: FPVI 关闭 ======
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    FPVI.SetClamp(100, 100);
    // ====== Step 7: 下电 (保持FET导通, BST领先5V同步下降) ======
    // 台阶1: BST=5V, PMID=0V (SW=0V, BST-SW=5V)
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: VDRV归零, BST=0V, SW=0V
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // RELAY_OFF
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    return 0;
}
