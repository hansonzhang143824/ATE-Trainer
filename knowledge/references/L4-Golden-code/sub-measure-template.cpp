// ===================================================================
// 参考案例: Trim sub.cpp measure 函数模板
// 所有 Trim 测量函数都放在 sub.cpp 中，不在 test.cpp 直接写 MeasureVI
// ===================================================================

// ===================================================================
// 模式A: 普通 MV/MI Trim (单源表直测)
// ===================================================================
void measure_XXX(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    // DWORD working_value2[SITE_NUM] = { 0 };  // 如果2个封装

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == WS)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_Fx").get_working(site);
            sim_step[site] = trim_node->get_working(site);
        }

        // 写入 EFUSE trim 值
        dcm.I2CWriteData(DEV_ADDR, 0xFx, 1, working_value1);
        delay_us(2000);

        // 寄存器配置(原样从 DFT Software_initial 复制)
        I2CWriteSameData(DEV_ADDR, 0xXX, 0xXX);
        // ...

        // 测量
        <ResourceName>.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = <ResourceName>.GetMeasResult(site, MVRET);  // MV用MVRET
            // results[site] = <ResourceName>.GetMeasResult(site, MIRET); // MI用MIRET
        }
    }
}

// ===================================================================
// 模式B: 大电流 + AMUX-NTC 差分测量 Trim
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

        // 寄存器配置
        // ...

        // 大电流加载: FI=目标 → delay(2ms) → 测量 → FI=0关断
        FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
        delay_us(2000);
        FPVI.MeasureVI(200, 5);
        FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 立即关断!

        // AMUX-NTC 差分测量
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

// ===================================================================
// 封装数量确定
// 在 treg 文件中查找 [_EFUSE_REG_Fx]，统计该参数涉及的封装数
// 1个封装 → working_value1; 2个封装 → working_value1 + working_value2
// ===================================================================
