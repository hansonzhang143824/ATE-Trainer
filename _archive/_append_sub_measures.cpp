// ===================================================================
// DALI: measure_bandgap — TM139 Trim_VBG 测量 (VDM MV, 返回 mV)
// treg: bandgap, 16步(Table 0-15, ASSY F0 bits 0-3)
// 测量: VDM_SDA_ACM MV (调用方已置 FI=0 高阻), MVRET × 1e3 → mV
// 寄存器由 test.cpp 已配置: 0x10=0x43, 0x57=0x02, 0x5E=0x0C (ATEST0_MUX=12 → VBG)
// ===================================================================
void measure_bandgap(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
		}

		// 写入 EFUSE trim 值 (bandgap 16步 → F0 bits 0-3)
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
		delay_ms(2);

		// VDM_SDA_ACM MV测量 (FI=0 高阻, 量程10UA)
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V → mV
		}
	}
}

// ===================================================================
// DALI: measure_bg_res_div — TM135 Trim_BG_RES_DIV 测量 (VDM MV, 返回 mV)
// treg: bg_res_div, 8步(Table 0-7, ASSY F1 bits 2-4)
// 测量: VDM_SDA_ACM MV (调用方已置 FI=0 高阻), MVRET × 1e3 → mV
// 寄存器由 test.cpp 已配置: 0x10=0x43, 0x57=0x02, 0x5E=0x0A (ATEST0_MUX=10 → BG_RES_DIV)
// ===================================================================
void measure_bg_res_div(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
		}

		// 写入 EFUSE trim 值 (bg_res_div 8步 → F1 bits 2-4)
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value1);
		delay_ms(2);

		// VDM_SDA_ACM MV测量 (FI=0 高阻, 量程10UA)
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V → mV
		}
	}
}

// ===================================================================
// DALI: measure_iztc_res — TM133 Trim_IZTC_RES 测量 (VDM MI, 返回 uA 带符号)
// treg: iztc_res, 64步(Table 0-63, ASSY F0 bits 4-7 + F1 bits 0-1)
// 测量: VDM_SDA_ACM MI (调用方已置 FV=1V), MIRET × 1e6 → uA (IZTC 负电流 × -1)
// 寄存器由 test.cpp 已配置: 0x10=0x43, 0x57=0x02, 0x5E=0x08 (ATEST0_MUX=8 → IZTC_RES)
// ===================================================================
void measure_iztc_res(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };
	DWORD working_value2[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
		}

		// 写入 EFUSE trim 值 (iztc_res 64步 → F0 bits 4-7 + F1 bits 0-1)
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value2);
		delay_ms(2);

		// VDM_SDA_ACM MI测量 (FV=1V, 量程10UA), 返回 uA
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = -1 * VDM_SDA_ACM.GetMeasResult(site, MIRET) * 1e6;  // A → uA (IZTC 电流方向取反)
		}
	}
}
