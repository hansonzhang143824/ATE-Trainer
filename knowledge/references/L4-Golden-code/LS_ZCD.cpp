DUT_API int LSZCD_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *LS_ZCD = StsGetParam(funcindex, "LS_ZCD");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

    //整个过程始终满足BST>=SW 同时BST-SW<=5V
    //----下管两端PMID和SW,测试项目是下管的ZCD测试，用到BST和SW，需要满足台阶上电原则，VBAT=VDRV=PMID=BST=5V,测试SW和PGND之间的电流阈值达到多大时候，会触发翻转， toggle PIN是INT
    因为电流大于200mA，用浮动源
    double ls_zcd[SITE_NUM] = { 0 };
    //---------------BUCK_LS_ZCD ： K33_BUSL_PGND, K17_BUSH_SW means SW-FPVI-PGND connect
    cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K33_BUSL_PGND, K17_BUSH_SW, K28_VDRV_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);//connect SW and PGND by FPVI
    delay_ms(3);
    VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(5);
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x59, 0x01);
    I2CWriteSameData(DEV_ADDR, 0x61, 0x0D);//		(D2A_BUBO_TM_LSON,1) 此时下管导通，SW=PGND
    I2CWriteSameData(DEV_ADDR, 0x55, 0xB0);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,48)]
    delay_ms(2);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
    FPVI.Set(FI, 0.26, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
    delay_ms(1);
    test_method.rampi_capv(FPVI, FPVIe_1V, FPVIe_1A, SDA_INT_ACM, ACM200_10V, ACM200_100UA, 0.25, -0.5, 200, 20, 2.5, TRIG_RISING, ls_zcd);
    FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
    FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
    
    VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
    BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
    BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    FOR_EACH_VALID_SITE(site)
    {
        LS_ZCD->SetTestResult(site, 0, ls_zcd[site]);
    }

	return 0;
}