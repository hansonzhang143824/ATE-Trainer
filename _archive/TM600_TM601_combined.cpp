DUT_API int TM600_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    CParam *LS_RDSON = StsGetParam(funcindex, "LS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };
    double ls_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 (HS路径) ======
    // HS路径: FPVI → K31_VBUSL_PMID → PMID → HS FET → SW → K17_BUSH_SW → FPVI
    // BST-SW: K18_BST_SW_Cap P2P电容, BTST_ACM独立供BST(不走FPVI_BUS)
    // Cap2: K32_PMID_Cap(FPVI浮动MI), K30_VBAT_Cap(供电), K28_VDRV_Cap(供电)
    // ⚠️ K33不闭合! K31+K17+K33同时闭合→PMID/SW/PGND全线短接!
    cbite.SetOn(K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 (BST领先PMID 5V台阶ramp) ======
    // 电压推断:
    //   VBAT=4.2(A)  VDRV=5(A)  SW=0(A, SW_ACM独立供0V)
    //   PMID=15(A, FOVI)  BST=20(A, BTST_ACM独立, 台阶ramp)
    //   BST-SW=20-0=20V(ramp中), FET导通后BST-SW=20-15=5V ✓

    // FPVI初始化: FV=0+FI=0, 为测量阶段大电流做准备
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);

    // 非浮动源直接上电
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // SW独立供电0V (ACM200 10V)
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // PMID和BST从0起步, BST始终领先PMID 5V
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5V, PMID=0V (BST-SW=5V)
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V, PMID=5V (BST-PMID=5V)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=15V, PMID=10V (BST-PMID=5V)
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=20V, PMID=15V (BST-PMID=5V)
    BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 (HS_RDSON) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);  // DIS_CLK=0
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HSON=1, LS OFF → HS FET导通
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);  // EN_FORCE_ON=1, TM_LSON=1
    // [电压推断] FET导通(C1:PMID↔SW) → SW跳变0→15V, BST=20V, BST-SW=5V ✓

    // ====== Step 4a: HS_RDSON 测量 (PMID-SW, 1A大电流) ======
    // 电流路径: FPVI → PMID → HS FET → SW → FPVI
    // 电压推断(D): iset[PMID2SW,1A]≥200mA → PMID≈SW, 压差=RDSON×1A
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(50, 50);

    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);

    FOR_EACH_VALID_SITE(site) {
        hs_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // ====== 继电器切换: HS→LS (防热切) ======
    // [热切规则] 切换前PMID必须降到0V, 避免PMID=15V→PGND=0V热切
    // PMID_FOVI FV=0 → PMID=0V, 继电器两端等电位 → 安全切换

    // Step 1: FPVI已FI=0关断, PMID降到0V
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);  // PMID=15→0V
    delay_us(200);

    // Step 2: 切换BUS继电器 (PMID和PGND都已0V, 无热切)
    // 断开K31(PMID→BUS), 闭合K33(PGND→BUS)
    cbite.SetOn(K17_BUSH_SW, K33_BUSL_PGND, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // Step 3: PMID恢复到9V (TM601 LS_RDSON需要)
    PMID_FOVI.Set(FV, 9, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // ====== Step 4b: LS_RDSON 测量 (PGND-SW, 1A大电流) ======
    // 切换寄存器: 关HS FET, 开LS FET
    I2CWriteSameData(DEV_ADDR, 0x59, 0x02);  // HSON=0, LSON=1 → LS FET导通
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);  // TM_DIS_CLK=1
    // [电压推断] FET导通(C3:SW↔PGND) → SW=PGND≈0V, BST=20V, BST-SW=20V(LS无自举,安全)
    delay_ms(1);

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
    // 当前状态: LS FET导通, SW≈PGND≈0V, BST=20V, PMID=9V
    // 关LS FET → BST和PMID独立台阶下电 (均无FET耦合)
    I2CWriteSameData(DEV_ADDR, 0x59, 0x00);  // LS OFF
    delay_us(200);

    // BST台阶下电: 20→15→10→5→0 (每步≤5V)
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // PMID台阶下电: 9→5→0 (每步≤5V)
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 其他源归零
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // RELAY_OFF (统一量程 10V/10MA)
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    // FPVI最后断开
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
        LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);
    }

    return 0;
}
