DUT_API int TM600_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 ======
    // BUS优先级: FPVI只有一个, iset[PMID2SW,1A]必须用FPVI(大电流)→ K31+K17占用
    // BST-SW=5V可用BTST_ACM+SW_ACM独立供电, 不通过FPVI_BUS → K38不闭合
    // K31_VBUSL_PMID: PMID→FPVI_BUS (High端), FPVI大电流通道
    // K17_BUSH_SW: SW→FPVI_BUS (Low端), FPVI大电流回路
    // K18_BST_SW_Cap: BST-SW P2P电容, 稳定BST-SW压差
    // K32_PMID_Cap: PMID Cap2 (FPVI浮动MI, 电流走FPVI_BUS, Cap不干扰测量)
    // K30_VBAT_Cap: VBAT Cap2 (仅供电)
    // K28_VDRV_Cap: VDRV Cap2 (仅供电)
    // 闭环: FPVI→K31→PMID→DUT(HSFET)→SW→K17→FPVI (电流路径)
    // BST-SW压差: BTST_ACM独立供电BST, SW_ACM独立供电SW, 差值=5V
    cbite.SetOn(K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap, -1);
    delay_ms(3);

    // ====== Step 2: 上电 (台阶式ramp, BST始终领先PMID≈5V) ======
    // BST-SW压差: BTST_ACM独立供BST, SW_ACM独立供SW=0V, 不经过FPVI_BUS
    // FPVI仅供iset[PMID2SW]大电流, 上电阶段FV=0+FI=0初始化
    // 台阶策略: BST领先PMID 5V同步ramp, FET导通后SW→PMID, BST-SW=5V

    // FPVI初始化: FV=0+FI=0, 为测量阶段大电流做准备
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
    delay_us(200);

    // 非浮动源直接上电: VBAT=4.2V, VDRV=5V
    VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // SW独立供电0V, ACM200 10V量程
    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // PMID和BST从0起步
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // 台阶1: BST=5V(ACM200_10V), PMID=0V (BST-SW=5V ✓)
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V(ACM200_40V), PMID=5V (BST-SW=10V, BST-PMID=5V ✓)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=15V(ACM200_40V), PMID=10V (BST-PMID=5V ✓)
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: BST=20V(ACM200_40V), PMID=15V (BST-PMID=5V ✓)
    // FET导通后SW→PMID≈15V, BST-SW=20-15=5V ✓
    BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: 寄存器配置 ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x58, 0x00);  // DIS_CLK=0
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // HSON=1, HS FET导通
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);  // EN_FORCE_ON=1, TM_LSON=1
    // 导通瞬间: SW=0→15V, BST=20V, BST-SW=20-15=5V ✓

    // ====== Step 4: 测量 (大电流 RDSON = V/I × 1000 mΩ) ======
    // FPVI三段式: FV=0 → FI=0 → SetClamp
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    // [H4修复] SetClamp(50,50): 50%×1V=0.5V compliance → 最大可测RDSON=500mΩ
    FPVI.SetClamp(50, 50);

    // 加载1A, 路径: PMID → HS FET → SW → FPVI
    FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
    delay_us(2000);  // 2ms稳定
    FPVI.MeasureVI(200, 5);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);  // 立即关断!

    FOR_EACH_VALID_SITE(site) {
        hs_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000;
    }

    // ====== Step 5: 下电 (保持FET导通, BST领先PMID 5V同步ramp下降) ======
    // [修复] FET不关! 保持导通SW跟随PMID, BST始终领先5V保证BST-SW≥0
    // 当前状态: BST=20V, PMID=15V, FET导通SW≈15V, BST-SW=20-15=5V ✓

    // 台阶1: BST=15V(ACM200_40V), PMID=10V (SW≈10V, BST-SW=5V ✓)
    BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶2: BST=10V(ACM200_40V), PMID=5V (SW≈5V, BST-SW=5V ✓)
    BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶3: BST=5V(ACM200_10V), PMID=0V (SW≈0V, BST-SW=5V ✓)
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_us(200);

    // 台阶4: VDRV归零, BST=0V, SW=0V (BST-SW=0 ✓)
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

    // FPVI最后断开
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
    }

    return 0;
}
