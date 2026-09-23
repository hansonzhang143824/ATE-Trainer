/////////////////////// Auto-generated AMS Test Code ////////////
/////////////////////// Test: VAC1_PLUG_IN_OUT_DEADBAT ////////////
// Test Item: USB_103, generate time: 2026-04-21 20:48:45 //

`NVT_STIM.en_vac1_cable_insert = 1;  // plugin vac1
//		plugin[vac1]
`NVT_STIM.en_vsrc_vac1 = 1;
`NVT_STIM.vsrcVAC1.ramp_vsrc_val(5, 100e-6);
#1000;
// pin VAC1 set to 5V
//		vset[vac1,5,100e-6,0]
wait_warmup();
//		wait_warmup[]
`NVT_STIM.reg_en_mcu_load = 1;  // en_reg mcu_load, 1
//		en_reg[mcu_load,1]
`NVT_UVM_TOP.i_iic.write_byte(`DEV_ADDR, 8'h8, 8'h8);  // Write reg 0x8 = 8
//		field[(VBUS_PULLDOWN,1)]
`NVT_UVM_TOP.i_iic.write_byte(`DEV_ADDR, 8'h8, 8'h18);  // Write reg 0x8 = 24
//		field[(VAC3_PULLDOWN,1)]
#10000000;  // delay 10e-3s
//		delay[10e-3]
`NVT_STIM.en_vsrc_vac1 = 1;
`NVT_STIM.vsrcVAC1.ramp_vsrc_val(12, 1e-6);
#1000;
// pin VAC1 set to 12V
//		vset[vac1,12,1e-6,0]
#10000000;  // delay 10e-3s
//		delay[10e-3]
`NVT_STIM.en_vac1_cable_insert = 0;  // plugout vac1
//		plugout[vac1]
#10000000;  // delay 10e-3s
//		delay[10e-3]

// Error: √¸¡Ó∏Ò Ω¥ÌŒÛ: nan
//		nan

$finish;
//		finish[]

/////////////////////// End of Auto-generated Code ////////////