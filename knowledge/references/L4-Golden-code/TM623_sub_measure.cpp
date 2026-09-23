// ===================================================================
// sub.cpp: measure_BUCK_HS_CS_GAIN — TM623 Buck HS Current Sense Gain Trim
// ===================================================================
// 模式: 大电流 + AMUX-NTC 差分测量 (MV)
// treg: buck_hsfet_gain, 5位, EFUSE_REG_F0
// FPVI: FI=3A → delay2ms → MeasureVI → FI=0关断
// 测量: AMUX_FOVI.MeasureVI - NTC_FOVI.MeasureVI (差分)
// ===================================================================
void measure_BUCK_HS_CS_GAIN(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    // buck_hsfet_gain 跨 EFUSE_REG_FA(bits 6-7) + EFUSE_REG_FB(bits 0-2) → 2个封装
    DWORD working_value1[SITE_NUM] = { 0 };  // EFUSE_REG_FA
    DWORD working_value2[SITE_NUM] = { 0 };  // EFUSE_REG_FB
    double amux_val[SITE_NUM] = { 0 };
    double ntc_val[SITE_NUM]  = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == WS)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            // buck_hsfet_gain bit0~1 在 FA, bit2~4 在 FB
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FA").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FB").get_working(site);
            sim_step[site] = trim_node->get_working(site);
        }

        // 写入两个 EFUSE 寄存器
        dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xFB, 1, working_value2);
        delay_us(2000);

        // 寄存器配置: register from DFT en_tm[]
        // ATEST0=13, ATEST1=9, TM_FORCE_EN_CS=1, DIS_NTC_DETECTION_ANALOG=1
        I2CWriteSameData(DEV_ADDR, 0x56, 0x04);  // EN_ATEST1=1
        I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);  // D2A_BUBO_ATEST1=9
        I2CWriteSameData(DEV_ADDR, 0x65, 0x04);  // DIS_NTC_DETECTION_ANALOG=1
        delay_ms(1);

        // ====== 大电流加载: FPVI FI=3A ======
        // 电流路径: FPVI→K31→PMID→HS FET→SW→K17→FPVI
        // 量程: FPVIe_10A (≥2×3A=6A)
        FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
        delay_us(2000);  // 2ms 稳定
        FPVI.MeasureVI(200, 5);
        FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 立即关断!

        // ====== AMUX-NTC 差分测量 ======
        AMUX_FOVI.MeasureVI(200, 5);
        NTC_FOVI.MeasureVI(200, 5);
        FOR_EACH_VALID_SITE(site)
        {
            amux_val[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
            ntc_val[site]  = NTC_FOVI.GetMeasResult(site, MVRET);
            results[site]  = amux_val[site] - ntc_val[site];
        }
    }
}
