// ===================================================================
// sub.cpp: measure_HP_VBG — TM130 Bandgap 电压 Trim 测量 (AMUX MV)
// ===================================================================
// treg: bandgap, 4位, EFUSE_REG_F0
// 测量: AMUX_FOVI MV, FI=0
// ===================================================================
void measure_HP_VBG(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == WS)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
            sim_step[site] = trim_node->get_working(site);
        }

        // 写入 EFUSE trim 值
        dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
        delay_us(2000);

        // 寄存器由 test.cpp 已配置: 0x56=0x62, 0x67=0x0A, 0x68=0x30
        // AMUX_FOVI MV测量 (FI=0, 量程10UA)
        AMUX_FOVI.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
        }
    }
}
