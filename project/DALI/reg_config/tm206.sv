/////////////////////// Auto-generated AMS Test Code ////////////
/////////////////////// Test: IPD_VAC2 ////////////
// Test Item: TM206

`NVT_STIM.en_vsrc_vbat = 1;
`NVT_STIM.vsrcVBAT.ramp_vsrc_val(4, 100e-6);
#1000;
// pin VBAT set to 4V
//		vset[vbat,4,100e-6,0]

wait_warmup();
//		wait_warmup[]
I2CWriteSameData(DEV_ADDR, 0x08, 0x20);  // Write reg 0x8 = 32
//		field[(VAC2_PULLDOWN,1)]

`NVT_STIM.en_vsrc_vac2 = 1;
`NVT_STIM.vsrcVAC2.ramp_vsrc_val(1, 1e-3);
#1000;
// pin VAC2 set to 1V
//		vset[vac2,1,1e-3,0]
#1000000;  // delay 1e-3s
//		delay[1e-3]
`NVT_STIM.en_vsrc_vac2 = 1;
`NVT_STIM.vsrcVAC2.ramp_vsrc_val(4, 1e-3);
#1000;
// pin VAC2 set to 4V
//		vset[vac2,4,1e-3,0]
#1000000;  // delay 1e-3s
//		delay[1e-3]
$finish;
//		finish[]

/////////////////////// End of Auto-generated Code ////////////