// ===================================================================
// TM600: HS_RDSON — 上管RDSON (PMID↔SW, 1A)
// ===================================================================
// DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]
//      iset[pmid2sw,1A], Check: PMID-SW MV&MI
// FET: C1(PMID↔SW), 0x59=0x01 HS导通
// 闭环: FPVI → K31 → PMID → HS FET → SW → K17 → FPVI
// BST: BTST_ACM独立供20V(台阶ramp), 不用FPVI_BUS
// ===================================================================
DUT_API int TM600_HS_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 ======
    // FPVI_BUS: K31(PMID→BUS) + K17(SW→BUS) → PMID↔SW闭环
    // BST-SW: K18 P2P电容, BTST_ACM独立供BST
    // Cap2: K32_PMID_Cap(FPVI浮动MI), K30_VBAT_Cap(供电), K28_VDRV_Cap(供电)
    cbite.SetOn(K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 (BST领先PMID 5V台阶ramp) ======
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);

    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5V, PMID=0V
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V, PMID=5V
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=15V, PMID=10V
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=20V, PMID=15V → FET导通后 SW→15V, BST-SW=5V ✓
    BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HS FET导通 → PMID=SW
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);

    // ====== Step 4: 测量 (RDSON = V/I × 1000 mΩ) ======
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

    // ====== Step 5: 下电 (BST和PMID同步台阶下降) ======
    // FET导通, SW=PMID, BST领先PMID 5V保证BST-SW≥0
    // 台阶1: BST=15V, PMID=10V (BST-SW=15-10=5V)
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V, PMID=5V (BST-SW=10-5=5V)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=5V, PMID=0V (BST-SW=5-0=5V)
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=0V, VDRV归零, SW归零
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // RELAY_OFF (统一量程 10V/10MA)
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
    }

    return 0;
}
