/////////////////////// Auto-generated AMS Test Code ////////////
/////////////////////// Test: IAC_VAC1_KLV1_ACC ////////////
// Test Item: TM801

`NVT_STIM.en_vsrc_vbat = 1;
`NVT_STIM.vsrcVBAT.ramp_vsrc_val(4.4, 100e-6);
#1000;
// pin VBAT set to 4.4V
//		vset[vbat,4.4,100e-6,0]
`NVT_STIM.vsrcVAC1.ramp_vsrc_val(5, 100e-6);
`NVT_STIM.en_vsrc_vac1 = 1;
#1000;
// pin VAC1 set to 5V
//		vset[vac1,5,100e-6,1]
`NVT_STIM.swKLV1_VAC1.set_ron_val(0.02);
`NVT_STIM.en_sw_klv1_vac1 = 1;
#1000000;
// pin KLV1_VAC1 resistor = 0.02��
//		res[klv1_vac1,0.02]

entertestmode();
//		en_tm[]
I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
I2CWriteSameData(DEV_ADDR, 0x11, 0x18);  // Write reg 0x11 = 24
I2CWriteSameData(DEV_ADDR, 0x30, 0x08);  // Write reg 0x30 = 8
I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,8),(EN_ATEST0,1),(ATEST0_MUX,31),(IAC_SEL,2)]
I2CWriteSameData(DEV_ADDR, 0x30, 0x0B);  // Write reg 0x30 = 11
//		field[(IAC_RATIO,3)]
#1000000;  // delay 1e-3s
//		delay[1e-3]
`NVT_STIM.en_isrc_klv1 = 1;
`NVT_STIM.isrcKLV1.ramp_isrc_val(0.3, 1e-3);
#1000;
// pin KLV1 current set to 0.3A
//		iset[klv1,0.3,1e-3,0]
#1000000;  // delay 1e-3s
//		delay[1e-3]
`NVT_STIM.en_isrc_klv1 = 1;
`NVT_STIM.isrcKLV1.ramp_isrc_val(0.5, 1e-3);
#1000;
// pin KLV1 current set to 0.5A
//		iset[klv1,0.5,1e-3,0]

#1000000;  // delay 1e-3s
//		delay[1e-3]
$finish;
//		finish[]

/////////////////////// End of Auto-generated Code ////////////