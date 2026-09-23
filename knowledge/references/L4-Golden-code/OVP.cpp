DUT_API int VBAT_Protection(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_OVP_2CELL_4V_Rise = StsGetParam(funcindex, "VBAT_OVP_2CELL_4V_Rise");
    CParam *VBAT_OVP_2CELL_4V_Fall = StsGetParam(funcindex, "VBAT_OVP_2CELL_4V_Fall");
    CParam *VBAT_OVP_2CELL_4V_Hys = StsGetParam(funcindex, "VBAT_OVP_2CELL_4V_Hys");
    CParam *VBAT_OVP_2CELL_4P4V_Rise = StsGetParam(funcindex, "VBAT_OVP_2CELL_4P4V_Rise");
    CParam *VBAT_OVP_2CELL_4P4V_Fall = StsGetParam(funcindex, "VBAT_OVP_2CELL_4P4V_Fall");
    CParam *VBAT_OVP_2CELL_4P4V_Hys = StsGetParam(funcindex, "VBAT_OVP_2CELL_4P4V_Hys");
    CParam *VBAT_OVP_4CELL_4V_Rise = StsGetParam(funcindex, "VBAT_OVP_4CELL_4V_Rise");
    CParam *VBAT_OVP_4CELL_4V_Fall = StsGetParam(funcindex, "VBAT_OVP_4CELL_4V_Fall");
    CParam *VBAT_OVP_4CELL_4V_Hys = StsGetParam(funcindex, "VBAT_OVP_4CELL_4V_Hys");
    CParam *VBAT_OVP_4CELL_4P4V_Rise = StsGetParam(funcindex, "VBAT_OVP_4CELL_4P4V_Rise");
    CParam *VBAT_OVP_4CELL_4P4V_Fall = StsGetParam(funcindex, "VBAT_OVP_4CELL_4P4V_Fall");
    CParam *VBAT_OVP_4CELL_4P4V_Hys = StsGetParam(funcindex, "VBAT_OVP_4CELL_4P4V_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here



	double vbat_ovp_2cell_4p1v_rise[SITE_NUM] = { 0 };
	double vbat_ovp_2cell_4p1v_fall[SITE_NUM] = { 0 };
	double vbat_ovp_2cell_4p1v_hys[SITE_NUM] = { 0 };
	double vbat_ovp_2cell_4p4_rise[SITE_NUM] = { 0 };
	double vbat_ovp_2cell_4p4_fall[SITE_NUM] = { 0 };
	double vbat_ovp_2cell_4p4_hys[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p1v_rise[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p1v_fall[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p1v_hys[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p4_rise[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p4_fall[SITE_NUM] = { 0 };
	double vbat_ovp_4cell_4p4_hys[SITE_NUM] = { 0 };

	cbite.SetOn(K_VBUS_Cap, K_VCC_Cap, K_VBATD_ACM,  -1);
	delay_ms(3);
	VBUS_ACM.Set(FV, V_TYP_VBUS, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_VBATD_ACM.Set(FV, 8, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	NTC2_FOVI.Set(FI, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDRESS, 0x13, 0x02);//wake_up = 1
	I2CWriteSameData(DEV_ADDRESS, 0x09, 0x00);//CHG_MODE = 0 
	I2CWriteSameData(DEV_ADDRESS, 0x55, 0x01);//DMUX_EN = 1
	I2CWriteSameData(DEV_ADDRESS, 0x56, 0x2B);// DMUX_SEL [43] = 1.
	//I2C_READ_BYTE(DEV_ADDR, 0x56, data_read);
	I2CWriteSameData(DEV_ADDRESS, 0x65, 0x00);
	I2CWriteSameData(DEV_ADDRESS, 0x66, 0x30);
	delay_ms(1);
	
	I2CWriteSameData(DEV_ADDRESS, 0x0B, 0x54);//N_CELL = 2 and VBAT_CV = 4V
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_RL_4P1")*8.4, spec[DEVICE_SEL]("VBAT_OVP_RH_4P1")*8.4, 400, 10, 2.5, TRIG_RISING, vbat_ovp_2cell_4p1v_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_FH_4P1")*8.4, spec[DEVICE_SEL]("VBAT_OVP_FL_4P1")*8.4, 400, 10, 2.5, TRIG_FALLING, vbat_ovp_2cell_4p1v_fall);

	I2CWriteSameData(DEV_ADDRESS, 0x0B, 1, 0x68);//N_CELL = 2 and VBAT_CV = 4.4V
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_RL_4P4")*8.8, spec[DEVICE_SEL]("VBAT_OVP_RH_4P4")*8.8, 400, 10, 2.5, TRIG_RISING, vbat_ovp_2cell_4p4_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_FH_4P4")*8.8, spec[DEVICE_SEL]("VBAT_OVP_FL_4P4")*8.8, 400, 10, 2.5, TRIG_FALLING, vbat_ovp_2cell_4p4_fall);


	I2CWriteSameData(DEV_ADDRESS, 0x0B, 1, 0xD4);//N_CELL = 4 and VBAT_CV = 4.0V
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_RL_4P1")*16.8, spec[DEVICE_SEL]("VBAT_OVP_RH_4P1")*16.8, 400, 10, 2.5, TRIG_RISING, vbat_ovp_4cell_4p1v_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_FH_4P1")*16.8, spec[DEVICE_SEL]("VBAT_OVP_FL_4P1")*16.8, 400, 10, 2.5, TRIG_FALLING, vbat_ovp_4cell_4p1v_fall);

	I2CWriteSameData(DEV_ADDRESS, 0x0B, 1, 0xE8);//N_CELL = 4 and VBAT_CV = 4.4V
	delay_ms(1);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_RL_4P4")*17.6, spec[DEVICE_SEL]("VBAT_OVP_RH_4P4")*17.6, 400, 10, 2.5, TRIG_RISING, vbat_ovp_4cell_4p4_rise);
	test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, spec[DEVICE_SEL]("VBAT_OVP_FH_4P4")*17.6, spec[DEVICE_SEL]("VBAT_OVP_FL_4P4")*17.6, 400, 10, 2.5, TRIG_FALLING, vbat_ovp_4cell_4p4_fall);

	
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
	NTC2_FOVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
	delay_ms(3);
	VAC123_VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBUS_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	NTC2_FOVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
	
	FOR_EACH_VALID_SITE(site)
	{
		vbat_ovp_2cell_4p1v_hys[site] = vbat_ovp_2cell_4p1v_rise[site] - vbat_ovp_2cell_4p1v_fall[site];
		vbat_ovp_2cell_4p4_hys[site] = vbat_ovp_2cell_4p4_rise[site] - vbat_ovp_2cell_4p4_fall[site];
		vbat_ovp_4cell_4p1v_hys[site] = vbat_ovp_4cell_4p1v_rise[site] - vbat_ovp_4cell_4p1v_fall[site];
		vbat_ovp_4cell_4p4_hys[site] = vbat_ovp_4cell_4p4_rise[site] - vbat_ovp_4cell_4p4_fall[site];

		VBAT_OVP_2CELL_4V_Rise->SetTestResult(site, 0, vbat_ovp_2cell_4p1v_rise[site]);
		VBAT_OVP_2CELL_4V_Fall->SetTestResult(site, 0, vbat_ovp_2cell_4p1v_fall[site]);
		VBAT_OVP_2CELL_4V_Hys->SetTestResult(site, 0, vbat_ovp_2cell_4p1v_hys[site]);
		VBAT_OVP_2CELL_4P4V_Rise->SetTestResult(site, 0, vbat_ovp_2cell_4p4_rise[site]);
		VBAT_OVP_2CELL_4P4V_Fall->SetTestResult(site, 0, vbat_ovp_2cell_4p4_fall[site]);
		VBAT_OVP_2CELL_4P4V_Hys->SetTestResult(site, 0, vbat_ovp_2cell_4p4_hys[site]);
		VBAT_OVP_4CELL_4V_Rise->SetTestResult(site, 0, vbat_ovp_4cell_4p1v_rise[site]);
		VBAT_OVP_4CELL_4V_Fall->SetTestResult(site, 0, vbat_ovp_4cell_4p1v_fall[site]);
		VBAT_OVP_4CELL_4V_Hys->SetTestResult(site, 0, vbat_ovp_4cell_4p1v_hys[site]);
		VBAT_OVP_4CELL_4P4V_Rise->SetTestResult(site, 0, vbat_ovp_4cell_4p4_rise[site]);
		VBAT_OVP_4CELL_4P4V_Fall->SetTestResult(site, 0, vbat_ovp_4cell_4p4_fall[site]);
		VBAT_OVP_4CELL_4P4V_Hys->SetTestResult(site, 0, vbat_ovp_4cell_4p4_hys[site]);
	}

	return 0;
}
