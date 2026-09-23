// =====================================================================
// TM1205: TRX_BST_UV_GD — BST1-SW1 / BST2-SW2 两组 BST UVLO 阈值 (Toggle)
// DFT OVERVIEW (Dali_testmode.xlsx): Test BST1-SW1, BST2-SW2 的 UVLO 值
//   流程: vbat=4V → en_tm → D2A_OVRD_SEL 47/45/48=3 + BOOTGD_DEG_BYPASS
//         → DMUX_SEL=57(路1 BST1-SW1) 双扫 → DMUX_SEL=58(路2 BST2-SW2) 双扫
// 驱动: BST1/BST2 为自举高侧、SW1/SW2 为开关低侧 → V(BST) > V(SW)
//   FPVI0 浮动差分跨对: High→SW(K46/K49), Low→BST(K41/K43)
//   FPVI0 输出 = V(SW)-V(BST) = -(BST-SW 压差) ∈ [-4,0]V
//   ramp 0→-4V ⟺ BST-SW 0→4V (上扫, 释放) / -4→0V ⟺ 4→0V (下扫, UVLO 触发)
// 观测: nQON(DTEST0) 翻转 (TM641/643 同模式), 继电器 K65_nQON_PU 上拉
// 两路串行: FPVI0 单通道, 先 DMUX 57 测 BST1-SW1, 再切 K43/K49 + DMUX 58 测 BST2-SW2
// =====================================================================
DUT_API int TM1205_TRX_BST_UV_GD(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *BST1_UV_Rise = StsGetParam(funcindex, "BST1_UV_Rise");
    CParam *BST1_UV_Fall = StsGetParam(funcindex, "BST1_UV_Fall");
    CParam *BST1_UV_Hys = StsGetParam(funcindex, "BST1_UV_Hys");
    CParam *BST2_UV_Rise = StsGetParam(funcindex, "BST2_UV_Rise");
    CParam *BST2_UV_Fall = StsGetParam(funcindex, "BST2_UV_Fall");
    CParam *BST2_UV_Hys = StsGetParam(funcindex, "BST2_UV_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double bst1_rise[SITE_NUM] = { 0 };
    double bst1_fall[SITE_NUM] = { 0 };
    double bst1_hys[SITE_NUM] = { 0 };
    double bst2_rise[SITE_NUM] = { 0 };
    double bst2_fall[SITE_NUM] = { 0 };
    double bst2_hys[SITE_NUM] = { 0 };
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // 路1 BST1-SW1: FPVI0 High→SW1 (K_FPVIH_TO_SW1_A=K46) + FPVI0 Low→BST1 (K_FPVIL_TO_BST1_A=K41)
    //   K46/K41 均为 Relay-ON 需闭合; BST1/SW1 Kelvin 对
    // VBAT 静态供电: K13_VBAT_Cap; nQON 观测: K65_nQON_PU 上拉
    // ⚠ Cap 纪律 (FR-001): BST-SW 是差分 ramp 源 → 不闭 BST Cap (K45_Cap_SW1_BST1/K44_Cap_SW2_BST2 拖慢 ramp)
    cbite.SetOn(K_FPVIH_TO_SW1_A, K_FPVIL_TO_BST1_A, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (VBAT 台阶, DFT: vbat=4V) ======
    // FPVI0 先 0 差分 (SW1=BST1), VBAT 上电后 FPVI0 输出负域 ramp
    FPVI0.Set(FV, 0, FPVIe_5V, FPVIe_100MA, FPVIe_RELAY_ON);  // 差分 0: BST1-SW1=0V
    delay_us(200);
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VBAT=4V
    delay_ms(1);

    // ====== Step 3: Register Config (tm1205.sv 权威序列) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x67, 0x2F);  I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // D2A_OVRD_SEL=47, ovrd=3
    I2CWriteSameData(DEV_ADDR, 0x67, 0x2D);  I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // D2A_OVRD_SEL=45, ovrd=3
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);  I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // D2A_OVRD_SEL=48, ovrd=3
    I2CWriteSameData(DEV_ADDR, 0x5C, 0x02);  // D2A_TRX_TM_BOOTGD_DEG_BYPASS=1
    delay_ms(1);                             // delay[1e-3]

    // ====== Step 4: Measure (两路串行, 各 Toggle 双扫捕 nQON 翻转) ======
    // 路1: BST1-SW1 (DMUX_SEL=57)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x39);  // DMUX_SEL=57
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // DMUX_EN=1
    delay_us(100);
    // FPVI0 输出 0→-4V = BST1-SW1 0→4V 上扫: 释放阈值 (nQON 与 ramp 反向, TRIG_FALLING 捕 rise)
    test_method.rampv_capv(FPVI0, FPVIe_10V, FPVIe_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0, -4, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // FPVI0 输出 -4→0V = BST1-SW1 4→0V 下扫: UVLO 触发阈值 (TRIG_RISING 捕 fall)
    test_method.rampv_capv(FPVI0, FPVIe_10V, FPVIe_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           -4, 0, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        bst1_rise[site] = fabs(vth_r[site]);   // |FPVIe 触发点| = BST1-SW1 压差
        bst1_fall[site] = fabs(vth_f[site]);
    }
    FOR_EACH_VALID_SITE(site)
    {
        bst1_hys[site] = (bst1_rise[site] - bst1_fall[site]) * 1e3;  // V→mV (R-HYS)
    }
    delay_ms(1);

    // 路2: BST2-SW2 (重新 SetOn 切路: K_FPVIH_TO_SW2_A=46,49 + K_FPVIL_TO_BST2_A=41,43; DMUX_SEL=58)
    cbite.SetOn(K_FPVIH_TO_SW2_A, K_FPVIL_TO_BST2_A, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x3A);  // DMUX_SEL=58
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // DMUX_EN=1
    delay_us(100);
    test_method.rampv_capv(FPVI0, FPVIe_10V, FPVIe_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           0, -4, 200, 20, 1.65, TRIG_FALLING, vth_r);
    test_method.rampv_capv(FPVI0, FPVIe_10V, FPVIe_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           -4, 0, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        bst2_rise[site] = fabs(vth_r[site]);
        bst2_fall[site] = fabs(vth_f[site]);
    }
    FOR_EACH_VALID_SITE(site)
    {
        bst2_hys[site] = (bst2_rise[site] - bst2_fall[site]) * 1e3;
    }
    delay_ms(1);

    // ====== Step 5: Power Off ======
    FPVI0.Set(FV, 0, FPVIe_5V, FPVIe_100MA, FPVIe_RELAY_ON);   // 差分回 0
    delay_us(200);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    FPVI0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        BST1_UV_Rise->SetTestResult(site, 0, bst1_rise[site]);
        BST1_UV_Fall->SetTestResult(site, 0, bst1_fall[site]);
        BST1_UV_Hys->SetTestResult(site, 0, bst1_hys[site]);
        BST2_UV_Rise->SetTestResult(site, 0, bst2_rise[site]);
        BST2_UV_Fall->SetTestResult(site, 0, bst2_fall[site]);
        BST2_UV_Hys->SetTestResult(site, 0, bst2_hys[site]);
    }
    return 0;
}
