DUT_API int TM600_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // iset[pmid2sw,1A]: FPVI浮动源, PMID(High)→SW(Low), 电流走FPVI_BUS不经过PMID_FOVI
    //   K31_VBUSL_PMID: PMID→FPVI_BUS (High端)
    //   K17_BUSH_SW: SW→FPVI_BUS (Low端)
    //   K32_PMID_Cap: PMID电容(FPVI浮动源测电流, 不影响PMID_FOVI, Cap可加)
    // vset[bst2sw,5V]: BST浮动电压源, 台阶式ramp保证BST始终领先SW
    //   K18_BST_SW_Cap: BST-SW电容/P2P
    // vset[vbat,4.2]: K30_VBAT_Cap (VBAT仅供电, 非测量源)
    // vset[vdrv,5]: K28_VDRV_Cap (VDRV仅供电, 非测量源)
    cbite.SetOn(K30_VBAT_Cap, K31_VBUSL_PMID, K32_PMID_Cap, K28_VDRV_Cap, K17_BUSH_SW, K18_BST_SW_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (台阶式 ramp) ======
    // VBAT和VDRV直接上电(非浮动源, 无ramp需求)
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

    // FPVI FV=0先稳住SW=0V, 确保ramp期间SW电位确定
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(200);

    // PMID和BST台阶式ramp: BST始终领先PMID约5V
    // 保证HS FET导通瞬间(SW→PMID) BST已处于SW+5V
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5, PMID=0, SW=0 (BST-SW=5V)
    BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10, PMID=5, SW=0 (BST-SW=10V)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=15, PMID=10, SW=0
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 15, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=20, PMID=15, SW=0 → 准备导通
    // 导通瞬间: SW→PMID=15V, BST=20V, BST-SW=5V ✓
    BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);  // DIS_CLK=0
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HSON=1, HS FET导通 → SW≈PMID≈15V
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);  // EN_FORCE_ON=1, TM_LSON=1, BUBO_MODE=0
    // 导通瞬间: SW=0→15V, BST=20V, BST-SW=20-15=5V ✓

    // ====== Step 4: Measure (RDSON = V/I × 1000 mΩ) ======
    // iset[pmid2sw,1A]: 量程2A ≥ 1A×2=2A ✓, 电压量程1V(大电流小压降)
    // FPVI从FV模式切换到FI模式, 大电流规则: FV=0→FI=0→SetClamp→FI=目标值
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.SetClamp(25, 25);

    // 加载1A, 路径: PMID → HS FET → SW → FPVI
    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);  // 2ms稳定
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);  // 立即关断!

    FOR_EACH_VALID_SITE(site)
    {
        hs_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // ====== Step 5: Power Off (台阶式下电) ======
    // BST先降到与SW齐平(20V→15V), 再与PMID同步归零
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 10, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // RELAY_OFF: 统一量程 10V/10MA
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: Check Code ======
    FOR_EACH_VALID_SITE(site)
    {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
    }

    return 0;
}
