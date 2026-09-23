DUT_API int PRST_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST_Rise = StsGetParam(funcindex, "VAC1_PRST_Rise");
    CParam *VAC1_PRST_Fall = StsGetParam(funcindex, "VAC1_PRST_Fall");
    CParam *VAC1_PRST_Hys = StsGetParam(funcindex, "VAC1_PRST_Hys");
    CParam *VAC2_PRST_Rise = StsGetParam(funcindex, "VAC2_PRST_Rise");
    CParam *VAC2_PRST_Fall = StsGetParam(funcindex, "VAC2_PRST_Fall");
    CParam *VAC2_PRST_Hys = StsGetParam(funcindex, "VAC2_PRST_Hys");
    CParam *VAC3_PRST_Rise = StsGetParam(funcindex, "VAC3_PRST_Rise");
    CParam *VAC3_PRST_Fall = StsGetParam(funcindex, "VAC3_PRST_Fall");
    CParam *VAC3_PRST_Hys = StsGetParam(funcindex, "VAC3_PRST_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double vac1_prst_rise[SITE_NUM] = { 0 };
	double vac1_prst_fall[SITE_NUM] = { 0 };
	double vac1_prst_hys[SITE_NUM] = { 0 };
	double vac2_prst_rise[SITE_NUM] = { 0 };
	double vac2_prst_fall[SITE_NUM] = { 0 };
	double vac2_prst_hys[SITE_NUM] = { 0 };
	double vac3_prst_rise[SITE_NUM] = { 0 };
	double vac3_prst_fall[SITE_NUM] = { 0 };
	double vac3_prst_hys[SITE_NUM] = { 0 };

	//--------VAC1 GD PRESTENT
	cbite.SetOn(K_VCC_Cap, K_VBAT_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 2.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NTC2_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_OFF);
	entertestmode();
	I2CWriteSameData(DEV_ADDRESS, 0x13, 0x02);//wake_up = 1
	I2CWriteSameData(DEV_ADDRESS, 0x58, 0x01);//EN_I2C = 1
	I2CWriteSameData(DEV_ADDRESS, 0x56, 0x24);// DMUX_SEL [36] = 1,VAC1_GD_PRESENT
	I2CWriteSameData(DEV_ADDRESS, 0x55, 0x01);//DMUX_EN = 1 
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 2.95, 3.45, 400, 10, 2.5, TRIG_RISING, vac1_prst_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 3.25, 2.75, 400, 10, 2.5, TRIG_FALLING, vac1_prst_fall);

	VAC123_VBATD_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	//-------VAC2 GD PRESTENT
	cbite.SetOn(K_VCC_Cap, K_VBAT_Cap, K_VAC2_ACM,  -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDRESS, 0x13, 0x02);//wake_up = 1
	I2CWriteSameData(DEV_ADDRESS, 0x58, 0x01);//EN_I2C = 1
	I2CWriteSameData(DEV_ADDRESS, 0x55, 0x01);//DMUX_EN = 1 
	I2CWriteSameData(DEV_ADDRESS, 0x56, 0x23);// DMUX_SEL [35] = 1,VAC2_GD_PRESENT
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 2.95, 3.45, 400, 10, 2.5, TRIG_RISING, vac2_prst_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 3.25, 2.75, 400, 10, 2.5, TRIG_FALLING, vac2_prst_fall);

	VAC123_VBATD_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	//-------VAC3 GD PRESTENT
	cbite.SetOn(K_VCC_Cap, K_VBAT_Cap, K_VAC3_ACM,  -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDRESS, 0x13, 0x02);//wake_up = 1
	I2CWriteSameData(DEV_ADDRESS, 0x58, 0x01);//EN_I2C = 1
	I2CWriteSameData(DEV_ADDRESS, 0x55, 0x01);//DMUX_EN = 1 
	I2CWriteSameData(DEV_ADDRESS, 0x56, 0x22);// DMUX_SEL [35] = 1,VAC3_GD_PRESENT
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 2.95, 3.45, 200, 10, 2.5, TRIG_RISING, vac3_prst_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 3.25, 2.75, 200, 10, 2.5, TRIG_FALLING, vac3_prst_fall);

	VAC123_VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_us(200);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	NTC2_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		vac1_prst_hys[site] = (vac1_prst_rise[site] - vac1_prst_fall[site])*1e3;//mV
		vac2_prst_hys[site] = (vac2_prst_rise[site] - vac2_prst_fall[site])*1e3;//mV
		vac3_prst_hys[site] = (vac3_prst_rise[site] - vac3_prst_fall[site])*1e3;//mV

		VAC1_PRST_Rise->SetTestResult(site, 0, vac1_prst_rise[site]);
		VAC1_PRST_Fall->SetTestResult(site, 0, vac1_prst_fall[site]);
		VAC1_PRST_Hys->SetTestResult(site, 0, vac1_prst_hys[site]);//mV
		VAC2_PRST_Rise->SetTestResult(site, 0, vac2_prst_rise[site]);
		VAC2_PRST_Fall->SetTestResult(site, 0, vac2_prst_fall[site]);
		VAC2_PRST_Hys->SetTestResult(site, 0, vac2_prst_hys[site]);//mV
		VAC3_PRST_Rise->SetTestResult(site, 0, vac3_prst_rise[site]);
		VAC3_PRST_Fall->SetTestResult(site, 0, vac3_prst_fall[site]);
		VAC3_PRST_Hys->SetTestResult(site, 0, vac3_prst_hys[site] );//mV
	}

	return 0;
}
