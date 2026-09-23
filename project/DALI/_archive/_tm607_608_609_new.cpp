// =====================================================================
// TM607/608/609 — BUBO ZCD / HS_NEG 电流阈值测试 (rampi_capv)
// 生成依据:
//   寄存器: reg_config/tm607.sv / tm608.sv / tm609.sv (field[] -> I2C 权威)
//   源表:   Pin_Channel_define.h
//   通路:   StdAfx.h PATH_RELAY 宏 (K_FPVIH_TO_* / K_FPVIL_TO_*, gen_path_defines.py 权威)
//   方法:   references/method/Current-Threshold.md (rampi_capv, 无迟滞单阈值)
//   风格:   test.cpp TM406_VBAT_LOW_VTH (六步法 + ramp*_capv + 三步下电)
//
// 用户修正 (2026-08-19):
//   TM607 LS_ZCD 下管:  电流 ramp 在 SW↔PGND  之间 (原 DFT iset[pmid_sw] 错)
//   TM608 HS_ZCD 上管:  电流 ramp 在 PMID↔SW  之间 (原 DFT iset[sw]     错)
//   TM609 HS_NEG 上管:  电流 ramp 在 PMID↔SW  之间 (原 DFT iset[sw]     错)
//   DTEST0 = nQON PIN (NQON_HG1_ACM 高阻读, K65_nQON_PU 上拉)
//
// 用户确认 (2026-08-19):
//   [A] VDRV = V1P5 短接 → 源表 V1P5_U34PS_FXVI (DALI_Net.NET V1P5_F/S net 含 TP_VDRV_F/S)
//   [B] trig 方向 = TRIG_RISING
//   [C] TM609 ramp = 0 → -3A (FPVIe_10A, 负向限流)
//   [D] 参数名 LS_ZCD / HS_ZCD / HS_NEG (DFT OVERVIEW isCodeGen=Y, meta 已补录)
// =====================================================================

// ---------------------------------------------------------------------
// TM607 BUCK_LS_ZCD — 下管 Low-Side FET 过零电流 (SW↔PGND ramp)
// 期望: 0.1A (ZCD 单阈值, 无迟滞)
// 电流环: FPVI0 High→SW1 → DUT(LSFET) → PGND → FPVI0 Low
// 电压:   VBAT=3.5V, PMID=5V, VDRV=5V
// 寄存器: BUBO force LS on (TM_LSON), DTEST0 mux=6
// ---------------------------------------------------------------------
DUT_API int TM607_BUCK_LS_ZCD(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LS_ZCD = StsGetParam(funcindex, "LS_ZCD");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ls_zcd[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // 电流通路 (StdAfx.h PATH_RELAY 宏):
    //   SW1  → FPVI0 High: K_FPVIH_TO_SW1_A = K136,K137,K143,K144,K46
    //   PGND → FPVI0 Low : K_FPVIL_TO_PGND   = K138,K140,K51,K53,K93
    // 电压源默认 NC 直连 (VBAT K8 / PMID K83 / VDRV), 无需 SetOn
    // K13_VBAT_Cap: VBAT 静态供电稳定; K65_nQON_PU: nQON 上拉读 DTEST0
    cbite.SetOn(K_FPVIH_TO_SW1_A, K_FPVIL_TO_PGND, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,3.5] / vset[pmid,5] / vset[vdrv,5]
    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VDRV=V1P5 短接
    delay_ms(1);
    // FPVI0 浮动源初始化: FV=0 + FI=0 (为电流 ramp 做准备)
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    delay_us(200);
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config (寄存器配置) ======
    // field[(WAKE_UP,1)] -> field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]
    //   -> field[(D2A_BUBO_TM_DIS_CLK,1)] -> field[(DMUX_EN,1),(DMUX_SEL,37),(D2A_BUBO_DTEST0,6)]
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x5A, 0x01);  // D2A_BUBO_TM_LSON=1 (下管 LS FET 导通)
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // D2A_BUBO_EN_FORCE_ON=1, BUBO_MODE=0
    delay_us(10);                             // 1e-5s
    I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
    delay_ms(3);                              // 3e-3s
    I2CWriteSameData(DEV_ADDR, 0x56, 0x25);  // DMUX_SEL=37
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // DMUX_EN=1
    I2CWriteSameData(DEV_ADDR, 0x5F, 0x06);  // D2A_BUBO_DTEST0=6 (LS ZCD)
    delay_ms(5);                              // 5e-3s

    // ====== Step 4: Measure (rampi_capv 电流 ramp, 捕 DTEST0 翻转) ======
    // FPVI0 ramp 电流 -0.2A -> +0.2A; nQON(ACM200 10UA 高阻) 捕 DTEST0 翻转点
    // 翻转点电流 = ZCD 阈值 (期望 0.1A); trig_level=1.65V = nQON 逻辑中点
    test_method.rampi_capv(FPVI0, FPVIe_1V, FPVIe_2A,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           -0.2, 0.2, 200, 20, 1.65, TRIG_RISING, ls_zcd);

    // ====== Step 5: Power Off (三步下电) ======
    // 先关电流, 再关电压 (FPVI 先 FI=0 再 FV=0)
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);  // nQON cap 源下电
    delay_ms(1);
    FPVI0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        LS_ZCD->SetTestResult(site, 0, ls_zcd[site]);
    }
    return 0;
}

// ---------------------------------------------------------------------
// TM608 BOOST_HS_ZCD — 上管 High-Side FET 过零电流 (PMID↔SW ramp)
// 期望: 0.1A (ZCD 单阈值, 无迟滞)
// 电流环: FPVI0 High→PMID → DUT(HSFET) → SW1 → FPVI0 Low
// 电压:   VBAT=3.5V, PMID=5V, BST_SW=5V
// 寄存器: BUBO force HS on (TM_HSON), DTEST0 mux=5
// ---------------------------------------------------------------------
DUT_API int TM608_BOOST_HS_ZCD(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_ZCD = StsGetParam(funcindex, "HS_ZCD");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_zcd[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // 电流通路 (StdAfx.h PATH_RELAY 宏):
    //   PMID → FPVI0 High: K_FPVIH_TO_PMID_A = K83
    //   SW1  → FPVI0 Low : K_FPVIL_TO_SW1_A = K47
    // K13_VBAT_Cap: VBAT 供电稳定; K65_nQON_PU: nQON 上拉读 DTEST0
    cbite.SetOn(K_FPVIH_TO_PMID_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,3.5] / vset[pmid,5] / vset[bst_sw,5]
    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    BST12_U1PS_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // BST_SW
    delay_ms(1);
    // FPVI0 浮动源初始化: FV=0 + FI=0
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    delay_us(200);
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config (寄存器配置) ======
    // field[(WAKE_UP,1)] -> field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_HSON,1),(BUBO_MODE,1)]
    //   -> field[(D2A_BUBO_TM_DIS_CLK,1)] -> field[(DMUX_EN,1),(DMUX_SEL,37),(D2A_BUBO_DTEST0,5)]
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);  // BUBO_MODE=1
    I2CWriteSameData(DEV_ADDR, 0x5A, 0x02);  // D2A_BUBO_TM_HSON=1 (上管 HS FET 导通)
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // D2A_BUBO_EN_FORCE_ON=1
    delay_us(10);                             // 1e-5s
    I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
    delay_ms(3);                              // 3e-3s
    I2CWriteSameData(DEV_ADDR, 0x56, 0x25);  // DMUX_SEL=37
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // DMUX_EN=1
    I2CWriteSameData(DEV_ADDR, 0x5F, 0x05);  // D2A_BUBO_DTEST0=5 (HS ZCD)
    delay_ms(5);                              // 5e-3s

    // ====== Step 4: Measure (rampi_capv 电流 ramp, 捕 DTEST0 翻转) ======
    // FPVI0 ramp 电流 -0.2A -> +0.2A; nQON 捕 DTEST0 翻转点 = ZCD 阈值 (期望 0.1A)
    test_method.rampi_capv(FPVI0, FPVIe_1V, FPVIe_2A,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           -0.2, 0.2, 200, 20, 1.65, TRIG_RISING, hs_zcd);

    // ====== Step 5: Power Off (三步下电) ======
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);  // nQON cap 源下电
    delay_ms(1);
    FPVI0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        HS_ZCD->SetTestResult(site, 0, hs_zcd[site]);
    }
    return 0;
}

// ---------------------------------------------------------------------
// TM609 BOOST_HS_NEG — 上管 High-Side 负向电流限 (PMID↔SW ramp)
// 期望: -3A (负向限流, 0→-3A ramp)
// 电流环: FPVI0 High→PMID → DUT(HSFET) → SW1 → FPVI0 Low
// 电压:   VBAT=3.5V, PMID=5V, BST_SW=5V, VDRV=5V
// 寄存器: BUBO force HS on + FPWM + ATEST0 mux=6, DTEST0 mux=5
// ---------------------------------------------------------------------
DUT_API int TM609_BOOST_HS_NEG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_NEG = StsGetParam(funcindex, "HS_NEG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_neg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // 电流通路: PMID→FPVI0 High (K_FPVIH_TO_PMID_A=K83); SW1→FPVI0 Low (K_FPVIL_TO_SW1_A=K47)
    cbite.SetOn(K_FPVIH_TO_PMID_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,3.5] / vset[pmid,5] / vset[bst_sw,5] / vset[vdrv,5]
    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    BST12_U1PS_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // BST_SW
    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VDRV=V1P5 短接
    delay_ms(1);
    // FPVI0 浮动源初始化: FV=0 + FI=0 (2A 用 FPVIe_10A 量程)
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
    delay_us(200);
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config (寄存器配置) ======
    // field[(WAKE_UP,1)] -> field[(D2A_BUBO_EN_FORCE_ON,1),(BUBO_MODE,1),(FPWM_EN,1)]
    //   -> field[(DMUX_EN,1),(DMUX_SEL,37),(D2A_BUBO_DTEST0,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0_MUX,6)]
    //   -> field[(D2A_BUBO_TM_DIS_CLK,1)] -> field[(D2A_BUBO_TM_HSON,1)]
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x09, 0x1A);  // D2A_BUBO_EN_FORCE_ON=1, BUBO_MODE=1, FPWM_EN=1
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // D2A_BUBO_EN_FORCE_ON=1
    I2CWriteSameData(DEV_ADDR, 0x56, 0x25);  // DMUX_SEL=37
    I2CWriteSameData(DEV_ADDR, 0x57, 0x0A);  // DMUX_EN=1, EN_ATEST0=1
    I2CWriteSameData(DEV_ADDR, 0x5B, 0x06);  // D2A_BUBO_ATEST0_MUX=6
    I2CWriteSameData(DEV_ADDR, 0x5F, 0x05);  // D2A_BUBO_DTEST0=5 (HS)
    delay_us(10);                             // 1e-5s
    I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
    delay_ms(3);                              // 3e-3s
    I2CWriteSameData(DEV_ADDR, 0x5A, 0x02);  // D2A_BUBO_TM_HSON=1 (上管 HS FET 导通)
    delay_ms(5);                              // 5e-3s

    // ====== Step 4: Measure (rampi_capv 电流 ramp, 捕 DTEST0 翻转) ======
    // FPVI0 ramp 电流 0 -> -3A (FPVIe_10A); nQON 捕 DTEST0 翻转点 = 负向限流阈值
    test_method.rampi_capv(FPVI0, FPVIe_1V, FPVIe_10A,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0.0, -3.0, 200, 20, 1.65, TRIG_RISING, hs_neg);  // [B] rising / [C] 0->-3A

    // ====== Step 5: Power Off (三步下电) ======
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);  // nQON cap 源下电
    delay_ms(1);
    FPVI0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        HS_NEG->SetTestResult(site, 0, hs_neg[site]);
    }
    return 0;
}
