// sub.cpp — NU1201 Trim 测量函数
// Trim 测量函数规则: 只含寄存器配置 + 测量，不含上电/下电/继电器
// 大电流 Trim: 测量后必须立即 FI=0 关断

#include "stdafx.h"

// ===================================================================
// measure_IZTC_1UA — TM125 IZTC 1μA电流源 Trim (MI, AMUX)
// ===================================================================
void measure_IZTC_1UA(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
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

        // 配置寄存器: EN_ATEST0=1, ATEST0_MUX=4 (LP_HR_0P5U 通路)
        I2CWriteSameData(DEV_ADDR, 0x56, 0x22);   // EN_ATEST0=1, ATEST0_MUX=4

        // AMUX_FOVI MI测量: FV=1 强制1V, 量程100UA
        AMUX_FOVI.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = AMUX_FOVI.GetMeasResult(site, MIRET);
        }
    }
}


// ===================================================================
// measure_HP_VBG — TM130 Bandgap 电压 Trim (MV, AMUX)
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
        dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
        delay_us(2000);

        // 配置 Bandgap: EN_ATEST0=1, ATEST0_MUX=12
        // D2A_OVRD_SEL=10, OVRD_VALUE=3
        I2CWriteSameData(DEV_ADDR, 0x56, 0x62);   // EN_ATEST0=1, ATEST0_MUX=12
        I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);   // D2A_OVRD_SEL=10
        I2CWriteSameData(DEV_ADDR, 0x68, 0x30);   // OVRD_VALUE=3
        delay_ms(2);  // Bandgap 稳定时间

        // AMUX_FOVI MV测量: FI=0, 量程10UA
        AMUX_FOVI.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
        }
    }
}


// ===================================================================
// measure_CV_BUF_TRIM — TM439_1 VBAT CV Buffer Trim (MV, VBAT)
// ===================================================================
void measure_CV_BUF_TRIM(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
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
        dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
        delay_us(2000);

        // DFT Software_initial 中的 I2C 配置
        // WAKE_UP=1, VBAT_CV=1, IBAT_LIMIT=7, IBUS_SET=127, VBUS_LOOP_DISABLE=1,
        // EN_ATEST1=1, D2A_BUBO_ATEST1=5, DIS_NTC_DETECTION_ANALOG=1
        I2CWriteSameData(DEV_ADDR, 0x0A, 0x11);
        I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
        I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
        I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
        I2CWriteSameData(DEV_ADDR, 0x56, 0x04);  // EN_ATEST1=1
        I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);  // D2A_BUBO_ATEST1=5
        I2CWriteSameData(DEV_ADDR, 0x61, 0x13);  // VBAT_CV=1
        I2CWriteSameData(DEV_ADDR, 0x65, 0x04);  // DIS_NTC_DETECTION_ANALOG=1
        delay_ms(1);

        I2CWriteSameData(DEV_ADDR, 0x58, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
        I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);  // D2A_BUBO_EN_FORCE_ON=1
        delay_ms(1);

        I2CWriteSameData(DEV_ADDR, 0x67, 0x03);  // D2A_OVRD_SEL=3
        I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // OVRD_VALUE=3 (overwrite vbat > trickle)
        Inherit_register();
        delay_ms(2);

        // VBAT_ACM MV测量
        VBAT_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = VBAT_ACM.GetMeasResult(site, MVRET);
        }
    }
}


// ===================================================================
// measure_BUCK_HS_CS_GAIN — TM623 Buck HS Current Sense Gain Trim
// AMUX-NTC 差分测量 (MV)
// 大电流3A通过FPVI加载, 测量时FI=0保护
// ===================================================================
void measure_BUCK_HS_CS_GAIN(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    double amux_val[SITE_NUM] = { 0 };
    double ntc_val[SITE_NUM]  = { 0 };

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
        dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
        delay_us(2000);

        // DFT en_tm[] 配置:
        // TM_HSON=1, EN_FORCE_ON=1, TM_DIS_CLK=1, BUBO_MODE=0,
        // TM_FORCE_EN_CS=1, EN_ATEST0=1, EN_ATEST1=1,
        // D2A_BUBO_ATEST0=13, D2A_BUBO_ATEST1=9, DIS_NTC_DETECTION_ANALOG=1
        // (具体寄存器映射见DFT的Software_initial, 此处保留框架)
        I2CWriteSameData(DEV_ADDR, 0x59, 0x01);  // TM_HSON=1
        I2CWriteSameData(DEV_ADDR, 0x58, 0x20);  // TM_DIS_CLK=1
        I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);  // EN_FORCE_ON=1
        I2CWriteSameData(DEV_ADDR, 0x65, 0x04);  // DIS_NTC_DETECTION_ANALOG=1
        delay_ms(1);

        // 大电流加载: iset[pmid2sw,3A]
        // FPVI FI=3A, 量程 10A ≥ 2×3A=6A
        // 大电流规则: FI=3A→delay(2ms)→Measure→立即FI=0
        FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
        delay_us(2000);
        FPVI.MeasureVI(200, 5);
        FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 立即关断!

        // AMUX-NTC 差分测量 (AMUX-NTC大电流Trim专用)
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
