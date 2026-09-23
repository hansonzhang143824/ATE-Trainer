// ===================================================================
// TM601: LS_RDSON — 下管RDSON (SW↔PGND, 1A)
// ===================================================================
// DFT: vset[vbat,4.2], vset[pmid,9], vset[vdrv,5]
//      iset[sw2pgnd,1A], Check: PGND-SW MV&MI
// FET: C3(SW↔PGND), 0x59=0x02 LS导通
// 闭环: FPVI → K17 → SW → LS FET → PGND → K33 → FPVI
// 无BST ramp: LS FET无自举电容, BST-SW无约束
// ===================================================================
DUT_API int TM601_LS_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LS_RDSON = StsGetParam(funcindex, "LS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ls_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 ======
    // FPVI_BUS: K17(SW→BUS) + K33(PGND→BUS) → SW↔PGND闭环
    // Cap2: K32_PMID_Cap(PMID=9V供电, MV模式→Cap ON), K30_VBAT_Cap, K28_VDRV_Cap
    // 无BST ramp → K18_BST_SW_Cap不需要
    // 无HS FET → K31_VBUSL_PMID不需要
    cbite.SetOn(K17_BUSH_SW, K33_BUSL_PGND, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 ======
    // 无浮动源, 全部直接上电
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);

    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    PMID_FOVI.Set(FV, 9, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);  // 2×9=18≤20
    delay_us(200);

    // SW独立供电0V (ACM200 10V)
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);  // TM_DIS_CLK=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x02);  // LS FET导通 → SW=PGND≈0V
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
    // [电压推断] C3(SW↔PGND)导通 → SW=PGND≈0V, PMID=9V, BST=0V

    // ====== Step 4: 测量 (RDSON = V/I × 1000 mΩ) ======
    // 电流路径: FPVI → K17 → SW → LS FET → PGND → K33 → FPVI
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(50, 50);

    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);

    FOR_EACH_VALID_SITE(site) {
        ls_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // ====== Step 5: 下电 ======
    // 无BST/浮动源, 普通三步下电
    // 步骤1: 所有源归零(RELAY_ON, 保持量程)
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_ms(1);

    // 步骤2: RELAY_OFF (统一量程 10V/10MA)
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);
    }

    return 0;
}
