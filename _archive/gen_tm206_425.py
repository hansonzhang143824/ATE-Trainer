# -*- coding: utf-8 -*-
# 生成 TM206~425 (30函数) 追加到 DALI\AI.cpp (TM205 之后)
# 已手写: TM206/207/210/211/212/213 (见下方 blocks)
# 构建器: TM214/215/220/222/300/301/400-413/418-425
import io

AI = r'D:\Newtest\CLAUDE_PROCESS\Project\DALI\AI.cpp'
blocks = []

# =====================================================================
# 手写块 (TM206/207/210/211/212/213) 从已提交脚本内容保留
# =====================================================================

HAND = r'''
// =====================================================================
// TM206: IPD_VAC2 — VAC2 下拉电流 @VAC2=4V (期望 2mA)
// 依据: reg_config/tm206.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM206_IPD_VAC2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VAC2 = StsGetParam(funcindex, "IPD_VAC2");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ipd_vac2[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share)
    // ⚠MI 下拉电流测量: 不闭合 Cap2
    cbite.SetOn(K13_VBAT_Cap, K19_VAC2, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令 (reg_config/tm206.sv)

    // ====== Step 3: Register Config ======
    // ⚠DFT 用 wait_warmup[] 而非 en_tm[]: 0x08 为功能寄存器 (VAC2 下拉), 按 DFT 不调用 entertestmode
    I2CWriteSameData(DEV_ADDR, 0x08, 0x20);  // Write reg 0x08 = 32
    // field[(VAC2_PULLDOWN,1)] → 使能 VAC2 下拉

    // ====== Step 4: Measure (VAC2 1V→4V, MI) ======
    // vset[vac2,1,1e-3,0] → VAC2=1V 预置
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac2,4,1e-3,0] → VAC2=4V, 测 I(VAC2) = 下拉电流 (期望 2mA)
    VAC123_AMUX_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vac2[site] = VAC123_AMUX_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPD_VAC2->SetTestResult(site, 0, ipd_vac2[site]);
    }
    return 0;
}


// =====================================================================
// TM207: IPD_VAC3 — VAC3 下拉电流 @VAC3=4V (期望 2mA)
// 依据: reg_config/tm207.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM207_IPD_VAC3(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VAC3 = StsGetParam(funcindex, "IPD_VAC3");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ipd_vac3[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC3 → VAC123_AMUX_ACM (S5_0): K18_VAC3 (Share)
    // ⚠MI 下拉电流测量: 不闭合 Cap2
    cbite.SetOn(K13_VBAT_Cap, K18_VAC3, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令 (reg_config/tm207.sv)

    // ====== Step 3: Register Config ======
    // ⚠DFT 用 wait_warmup[] 而非 en_tm[]: 0x08 为功能寄存器 (VAC3 下拉), 按 DFT 不调用 entertestmode
    I2CWriteSameData(DEV_ADDR, 0x08, 0x10);  // Write reg 0x08 = 16
    // field[(VAC3_PULLDOWN,1)] → 使能 VAC3 下拉

    // ====== Step 4: Measure (VAC3 1V→4V, MI) ======
    // vset[vac3,1,1e-3,0] → VAC3=1V 预置
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac3,4,1e-3,0] → VAC3=4V, 测 I(VAC3) = 下拉电流 (期望 2mA)
    VAC123_AMUX_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vac3[site] = VAC123_AMUX_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPD_VAC3->SetTestResult(site, 0, ipd_vac3[site]);
    }
    return 0;
}


// =====================================================================
// TM210: VAC1_SNK_DET_VTH_RELMODE — VAC1 SNK 检测阈值, REL 模式 (Toggle)
// 依据: reg_config/tm210.sv (verbatim I2C/field 注释)
// ⚠RELMODE 为斜率检测: OVERVIEW 无 expect 值, 暂按 Toggle 3参数抓 DTEST0 翻转阈值
// =====================================================================
DUT_API int TM210_VAC1_SNK_DET_VTH_RELMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_SNK_DET_VTH_RELMODE_Rise = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Rise");
    CParam *VAC1_SNK_DET_VTH_RELMODE_Fall = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Fall");
    CParam *VAC1_SNK_DET_VTH_RELMODE_Hys  = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_RELMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x03);  // Write reg 0x07 = 3
    I2CWriteSameData(DEV_ADDR, 0x56, 0x02);  // Write reg 0x56 = 2
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(VAC1_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1),(DMUX_EN,1),(DMUX_SEL,2)] → VAC1 SNK_DET(REL) 路由到 DTEST0 (reg_config/tm210.sv)
    delay_ms(10);  // delay[10e-3]

    // ====== Step 4: Measure (VAC1 0→3→0V) ======
    // ⚠RELMODE 斜率检测: 两段斜坡 (0→3 上升/3→0 下降), DTEST0 翻转阈值 (expect 待 OVERVIEW 补全)
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC1_SNK_DET_VTH_RELMODE_Rise->SetTestResult(site, 0, rise[site]);
        VAC1_SNK_DET_VTH_RELMODE_Fall->SetTestResult(site, 0, fall[site]);
        VAC1_SNK_DET_VTH_RELMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM211: VAC2_SNK_DET_VTH_RELMODE — VAC2 SNK 检测阈值, REL 模式 (Toggle)
// 依据: reg_config/tm211.sv (verbatim I2C/field 注释)
// ⚠RELMODE 为斜率检测: OVERVIEW 无 expect 值, 暂按 Toggle 3参数抓 DTEST0 翻转阈值
// =====================================================================
DUT_API int TM211_VAC2_SNK_DET_VTH_RELMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_SNK_DET_VTH_RELMODE_Rise = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Rise");
    CParam *VAC2_SNK_DET_VTH_RELMODE_Fall = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Fall");
    CParam *VAC2_SNK_DET_VTH_RELMODE_Hys  = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_RELMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share, 斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K19_VAC2, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x05);  // Write reg 0x07 = 5
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2C);  // Write reg 0x56 = 44
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1),(DMUX_EN,1),(DMUX_SEL,44)] → VAC2 SNK_DET(REL) 路由到 DTEST0 (reg_config/tm211.sv)
    delay_ms(10);  // delay[10e-3]

    // ====== Step 4: Measure (VAC2 0→3→0V) ======
    // ⚠RELMODE 斜率检测: 两段斜坡 (0→3 上升/3→0 下降), DTEST0 翻转阈值 (expect 待 OVERVIEW 补全)
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC2_SNK_DET_VTH_RELMODE_Rise->SetTestResult(site, 0, rise[site]);
        VAC2_SNK_DET_VTH_RELMODE_Fall->SetTestResult(site, 0, fall[site]);
        VAC2_SNK_DET_VTH_RELMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM212: VAC1_SNK_DET_VTH_ABSMODE — VAC1 SNK 检测阈值, ABS 模式 (Toggle)
// 期望: rising 1.9V / falling 1.7V (OVERVIEW)
// 依据: reg_config/tm212.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM212_VAC1_SNK_DET_VTH_ABSMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Rise = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Rise");
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Fall = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Fall");
    CParam *VAC1_SNK_DET_VTH_ABSMODE_Hys  = StsGetParam(funcindex, "VAC1_SNK_DET_VTH_ABSMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x02);  // Write reg 0x07 = 2
    I2CWriteSameData(DEV_ADDR, 0x56, 0x02);  // Write reg 0x56 = 2
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(VAC1_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0),(DMUX_EN,1),(DMUX_SEL,2)] → VAC1 SNK_DET(ABS) 路由到 DTEST0 (reg_config/tm212.sv)
    delay_ms(10);  // delay[10e-3]

    // ====== Step 4: Measure (VAC1 0→3→0V) ======
    // ABS 模式: 绝对阈值, 期望 rising 1.9V / falling 1.7V
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC1_SNK_DET_VTH_ABSMODE_Rise->SetTestResult(site, 0, rise[site]);
        VAC1_SNK_DET_VTH_ABSMODE_Fall->SetTestResult(site, 0, fall[site]);
        VAC1_SNK_DET_VTH_ABSMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM213: VAC2_SNK_DET_VTH_ABSMODE — VAC2 SNK 检测阈值, ABS 模式 (Toggle)
// 期望: rising 1.9V / falling 1.7V (OVERVIEW)
// 依据: reg_config/tm213.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM213_VAC2_SNK_DET_VTH_ABSMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Rise = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Rise");
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Fall = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Fall");
    CParam *VAC2_SNK_DET_VTH_ABSMODE_Hys  = StsGetParam(funcindex, "VAC2_SNK_DET_VTH_ABSMODE_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share, 斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K19_VAC2, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x07, 0x04);  // Write reg 0x07 = 4
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2C);  // Write reg 0x56 = 44
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0),(DMUX_EN,1),(DMUX_SEL,44)] → VAC2 SNK_DET(ABS) 路由到 DTEST0 (reg_config/tm213.sv)
    delay_ms(10);  // delay[10e-3]

    // ====== Step 4: Measure (VAC2 0→3→0V) ======
    // ABS 模式: 绝对阈值, 期望 rising 1.9V / falling 1.7V
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC2_SNK_DET_VTH_ABSMODE_Rise->SetTestResult(site, 0, rise[site]);
        VAC2_SNK_DET_VTH_ABSMODE_Fall->SetTestResult(site, 0, fall[site]);
        VAC2_SNK_DET_VTH_ABSMODE_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
'''

blocks.append(HAND)

# =====================================================================
# 构建器: MNT_Toggle_VBAT (TM406/408/410/411/412/413) — VAC1 供电, VBAT 斜坡
# =====================================================================
MNT_VBAT = r'''
// =====================================================================
// @TM@: @NAME@ — @DESC@ (Toggle)
// 期望: @EXP@
// 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@_Rise = StsGetParam(funcindex, "@PNAME@_Rise");
    CParam *@PNAME@_Fall = StsGetParam(funcindex, "@PNAME@_Fall");
    CParam *@PNAME@_Hys  = StsGetParam(funcindex, "@PNAME@_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 供电: VAC123_AMUX_ACM (ACM200 S5_0); Cap2 K21_VAC_Cap
    // VBAT 为斜坡源(非供电) → 不加 K13_VBAT_Cap (避免拉偏ramp)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,1e-3,0] → VAC1=5V (DUT供电)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
@I2C@    // @FIELD@

    // ====== Step 4: Measure (VBAT 0→5→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@_Rise->SetTestResult(site, 0, rise[site]);
        @PNAME@_Fall->SetTestResult(site, 0, fall[site]);
        @PNAME@_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
'''

def mnt_vbat(tm, name, pname, desc, exp, i2c, field):
    return (MNT_VBAT
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@DESC@', desc).replace('@EXP@', exp)
            .replace('@I2C@', i2c).replace('@FIELD@', field))

blocks.append(mnt_vbat('TM406', 'VBAT_LOW_VTH', 'VBAT_LOW_VTH', 'VBAT 低压比较器 (boost)',
    'rising 2.7V / falling 2.5V, hys 0.2V',
    '''    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);  // Write reg 0x09 = 10
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);  // Write reg 0x56 = 26
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,26),(BUBO_MODE,1)] → A2D_VBAT_LOW(boost) 路由到 DTEST0'))

blocks.append(mnt_vbat('TM408', 'VBAT_OVP', 'VBAT_OVP', 'VBAT 过压比较器 (buck)',
    'rising 104%·VBAT_CV=4.368V / falling 102%·VBAT_CV=4.284V, hys 2% (VBAT_CV=4.2V)',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1C);  // Write reg 0x56 = 28
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,28),(VBAT_CV,9)] → A2D_VBAT_OVP(buck) 路由到 DTEST0'))

blocks.append(mnt_vbat('TM410', 'VTRIKLE_VTH1', 'VTRIKLE_VTH1', 'VBAT 涓流充电阈值1 (buck)',
    'rising 2.7V / falling 2.4V, hys 0.3V',
    '''    I2CWriteSameData(DEV_ADDR, 0x0A, 0x09);  // Write reg 0x0A = 9
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);  // Write reg 0x56 = 29
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VTRICKLE,0)(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] → A2D_VTRIKLE_VTH1(buck) 路由到 DTEST0'))

blocks.append(mnt_vbat('TM411', 'VTRIKLE_VTH2', 'VTRIKLE_VTH2', 'VBAT 涓流充电阈值2 (buck)',
    'rising 3.0V / falling 2.7V, hys 0.3V',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);  // Write reg 0x56 = 29
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VTRICKLE,1)(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] → A2D_VTRIKLE_VTH2(buck) 路由到 DTEST0'))

blocks.append(mnt_vbat('TM412', 'VRE_CHG_VTH1', 'VRE_CHG_VTH1', 'VBAT 再充电阈值1 (buck)',
    'rising VBAT_CV−0.1≈4.0V / falling 3.95V, hys 0.05V; ⚠极性: Hys=Rise−Fall 为负 (幅值≈0.05)',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);  // Write reg 0x56 = 27
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VRE_CHG,0)(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] → A2D_VRE_CHG_VTH1(buck) 路由到 DTEST0'))

blocks.append(mnt_vbat('TM413', 'VRE_CHG_VTH2', 'VRE_CHG_VTH2', 'VBAT 再充电阈值2 (buck)',
    'rising VBAT_CV−0.1≈3.9V / falling 3.85V, hys 0.05V; ⚠极性: Hys=Rise−Fall 为负 (幅值≈0.05)',
    '''    I2CWriteSameData(DEV_ADDR, 0x0A, 0x69);  // Write reg 0x0A = 105
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);  // Write reg 0x56 = 27
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VRE_CHG,1)(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] → A2D_VRE_CHG_VTH2(buck) 路由到 DTEST0'))

# =====================================================================
# 构建器: MNT_Toggle_VBUS (TM400/401/402/403/409) — VBAT 供电, VBUS 斜坡
# =====================================================================
MNT_VBUS = r'''
// =====================================================================
// @TM@: @NAME@ — @DESC@ (Toggle)
// 期望: @EXP@
// 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@_Rise = StsGetParam(funcindex, "@PNAME@_Rise");
    CParam *@PNAME@_Fall = StsGetParam(funcindex, "@PNAME@_Fall");
    CParam *@PNAME@_Hys  = StsGetParam(funcindex, "@PNAME@_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap (DUT供电)
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4_DRVH1 默认NC直连 (斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
@I2C@    // @FIELD@

    // ====== Step 4: Measure (VBUS @LO@→@HI@→@LO@V) ======
@MEAS_COMMENT@    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, @VRNG@, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      @LO@, @HI@, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, @VRNG@, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      @HI@, @LO@, 200, 50, 1.65, TRIG_RISING, fall);
    }
@DELTA@
    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, @VRNG@, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, @VRNG@, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@_Rise->SetTestResult(site, 0, rise[site]);
        @PNAME@_Fall->SetTestResult(site, 0, fall[site]);
        @PNAME@_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
'''

def mnt_vbus(tm, name, pname, desc, exp, i2c, field, lo, hi, vrng,
             meas_comment='', delta=''):
    return (MNT_VBUS
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@DESC@', desc).replace('@EXP@', exp)
            .replace('@I2C@', i2c).replace('@FIELD@', field)
            .replace('@LO@', lo).replace('@HI@', hi).replace('@VRNG@', vrng)
            .replace('@MEAS_COMMENT@', meas_comment).replace('@DELTA@', delta))

blocks.append(mnt_vbus('TM400', 'VBUS_OVP_VTH1', 'VBUS_OVP_VTH1', 'VBUS 过压阈值1',
    'rising 6.5V / falling 6.2V, hys 0.3V',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VBUS_OVP,0),(DMUX_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH1) 路由到 DTEST0',
    '4', '7', 'ACM200_20V'))

blocks.append(mnt_vbus('TM401', 'VBUS_OVP_VTH2', 'VBUS_OVP_VTH2', 'VBUS 过压阈值2',
    'rising 12.8V / falling 12.5V, hys 0.3V',
    '''    I2CWriteSameData(DEV_ADDR, 0x0C, 0x08);  // Write reg 0x0C = 8
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(VBUS_OVP,2),(DMUX_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH2) 路由到 DTEST0',
    '4', '15', 'ACM200_40V'))

blocks.append(mnt_vbus('TM402', 'VBUS_OVP_VTH3', 'VBUS_OVP_VTH3', 'VBUS 过压阈值3',
    'rising 18.8V / falling 18.5V, hys 0.3V',
    '''    I2CWriteSameData(DEV_ADDR, 0x0C, 0x14);  // Write reg 0x0C = 20
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    I2CWriteSameData(DEV_ADDR, 0xFF, 0x04);  // Write reg 0xFF = 4
''',
    'field[(WAKE_UP,1),(VBUS_OVP,5),(DMUX_EN,1),(MPP_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH3) 路由到 DTEST0',
    '4', '20', 'ACM200_40V'))

blocks.append(mnt_vbus('TM409', 'VBUS_HT_4P8V', 'VBUS_HT_4P8V', 'VBUS 高温路径4.8V (boost)',
    'rising 4.8V (bench 4.661V)',
    '''    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);  // Write reg 0x09 = 10
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1F);  // Write reg 0x56 = 31
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,31),(BUBO_MODE,1)] → A2D_VBUS_HT_4P8V(boost) 路由到 DTEST0',
    '4', '7', 'ACM200_20V'))

# TM403 特殊: VBUS_REVI, 结果 = VBUS翻转电压 − VBAT(4V)
blocks.append(mnt_vbus('TM403', 'VBUS_REVI_VTH', 'VBUS_REVI_VTH', 'VBUS 反向电流检测',
    'falling VBUS−VBAT≈−120mV / rising 0V (bench f−0.138/r−0.016)',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1E);  // Write reg 0x56 = 30
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
''',
    'field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] → A2D_VBUS_REVI 路由到 DTEST0',
    '3.7', '4.5', 'ACM200_10V',
    meas_comment='''    // ⚠REVI 极性: VBUS<VBAT 时故障(REVI 激活,nQON低); VBUS 上升段 REVI 解除 → nQON 上升沿 = TRIG_RISING
    // 下降段 REVI 激活 → nQON 下降沿 = TRIG_FALLING (与常规比较器相反)
''',
    delta='''    // 结果 = VBUS翻转点 − VBAT(4V): 期望 falling≈−0.12V / rising≈0V
    FOR_EACH_VALID_SITE(site)
    {
        rise[site] = rise[site] - 4.0;
        fall[site] = fall[site] - 4.0;
    }
'''))

# =====================================================================
# 构建器: PWM_VTH (TM214/215)
# =====================================================================
PWM_VTH = r'''
// =====================================================================
// @TM@: @NAME@ — @PWM@ 输入阈值 (Toggle)
// 期望: rising 1.4V / falling 0.6V, hys 0.8V (OVERVIEW)
// 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
// ⚠0x67/0x68 D2A_OVRD 强制 PWM IO 使能 (D2A_EN_PWM_IO), 阈值检测经 DTEST0
// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@_Rise = StsGetParam(funcindex, "@PNAME@_Rise");
    CParam *@PNAME@_Fall = StsGetParam(funcindex, "@PNAME@_Fall");
    CParam *@PNAME@_Hys  = StsGetParam(funcindex, "@PNAME@_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // @PWM@ → @SRC@ (@SRCNAME@, 直接连接, 斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm@NUM@.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, @DMRX@);  // Write reg 0x56 = @DMRD@
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,@DMS@)] → @PWM@ 阈值信号路由到 DTEST0
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);  // Write reg 0x67 = 48
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // Write reg 0x68 = 48
    // field[(D2A_OVRD_SEL,48),(ovrd_value,3)] → D2A 强制 @PWM@ IO 使能
    delay_ms(2);  // delay[2e-3]

    // ====== Step 4: Measure (@PWM@ 0→4→0V) ======
    {
        test_method.rampv_capv(@SRC@, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(@SRC@, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    @SRC@.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    @SRC@.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@_Rise->SetTestResult(site, 0, rise[site]);
        @PNAME@_Fall->SetTestResult(site, 0, fall[site]);
        @PNAME@_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
'''

def pwm_vth(tm, name, pname, pwm, src, srcname, dmrx, dmrd, dms):
    return (PWM_VTH
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@PWM@', pwm).replace('@SRC@', src).replace('@SRCNAME@', srcname)
            .replace('@DMRX@', dmrx).replace('@DMRD@', dmrd).replace('@DMS@', dms))

blocks.append(pwm_vth('TM214', 'PWM1_VTH', 'PWM1_VTH', 'PWM1', 'PB0_BST_ACM', 'S5_18', '0x2E', '46', '46'))
blocks.append(pwm_vth('TM215', 'PWM2_VTH', 'PWM2_VTH', 'PWM2', 'PA6_PC5_ACM', 'S5_19', '0x2D', '45', '45'))

# =====================================================================
# 构建器: R_PULL (TM220/222) — DMO/DMA 下拉电阻
# =====================================================================
R_PULL = r'''
// =====================================================================
// @TM@: @NAME@ — @PIN@ 下拉/推挽电阻测量 (FI 负载法)
// 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
// ⚠OVERVIEW expect 空: 测量机制为预估 (FI=1mA 灌入低态输出, R=V/I ≈ Rds_on)
// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@ = StsGetParam(funcindex, "@PNAME@");
    //}}AFX_STS_PARAM_PROTOTYPES

    double @VAR@[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // @PIN@ → @SRC@ (@SRCNAME@, 直接连接)
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (DMO 数字输入源)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x71, @REG71X@);  // Write reg 0x71 = @REG71D@
    // @FIELD71@
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);  // Write reg 0x56 = 22
    // field[(DMUX_SEL,22)] → @PIN@ 输出路由到 DTEST0 (reg_config/tm@NUM@.sv)

    // ====== Step 4: Measure (@PIN@ 低态下拉电阻) ======
    // vset[vac1,5,10e-3,0] → VAC1=5V: @PIN@ 缓冲输出 HIGH (功能确认)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac1,0,10e-3,0] → VAC1=0V: @PIN@ 缓冲输出 LOW
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(2);  // delay[2e-3]
    // FI=1mA 灌入 @PIN@, 测 V → R = V/I (⚠机制预估)
    @SRC@.Set(FI, 1e-3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    @SRC@.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        @VAR@[site] = @SRC@.GetMeasResult(site, MVRET) / 1e-3;  // Ω
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    @SRC@.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    @SRC@.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@->SetTestResult(site, 0, @VAR@[site]);
    }
    return 0;
}
'''

def r_pull(tm, name, pname, pin, src, srcname, reg71x, reg71d, field71):
    return (R_PULL
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@PIN@', pin).replace('@SRC@', src).replace('@SRCNAME@', srcname)
            .replace('@VAR@', pname.lower())
            .replace('@REG71X@', reg71x).replace('@REG71D@', reg71d)
            .replace('@FIELD71@', field71))

blocks.append(r_pull('TM220', 'DMO_PD_R', 'DMO_PD_R', 'DMO', 'PC8_PC6_ACM', 'S5_12',
                     '0x2A', '42', 'field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMO_EN,1),(D2A_DMO_CHANNEL_SEL,1)] → DMO 作为 D2A 数字输出'))
blocks.append(r_pull('TM222', 'DMA_PD_R', 'DMA_PD_R', 'DMA', 'PA7_PD2_ACM', 'S5_23',
                     '0x31', '49', 'field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMA_EN,1),(D2A_DMA_CHANNEL_SEL,1)] → DMA 作为 D2A 数字输出'))

# =====================================================================
# 构建器: QTMU_FREQ (TM300/301) — DTEST0 频率测量 (OSC)
# =====================================================================
QTMU_FREQ = r'''
// =====================================================================
// @TM@: @NAME@ — @OSC@ 频率测量 (QTMU, DTEST0/nQON)
// 期望: @EXP@; 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
// ⚠Trim=Y: D2A_TRIM_OSC 修调项 DALI 无 .treg, 暂测默认频率, Trim execute 待 treg
// ⚠QTMU 触发电平 1.65V 沿用 DTEST0 观测约定, 需按实际 OSC 幅度确认
// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@ = StsGetParam(funcindex, "@PNAME@");
    //}}AFX_STS_PARAM_PROTOTYPES

    double @VAR@[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DTEST0(OSC) → QTMU (S10 CH0_A): K66_TMU_nQON; +K65_nQON_PU 上拉
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,@VBATV@,100e-6,0] → VBAT=@VBATV@V
    VBAT_PD3_FXVI.Set(FV, @VBATV@, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
@I2C@
    // ====== Step 4: Measure (QTMU 频率, KHz) ======
    // nQON/DTEST0 → QTMU S10 CHA (K66), 频率测量 (结果 KHz)
    QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
    QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
    QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 1.65, QTMUe_FILTER_PASS);
    QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS);
    FOR_EACH_VALID_SITE(site)
    {
        @VAR@[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
    }
    QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@->SetTestResult(site, 0, @VAR@[site]);
    }
    return 0;
}
'''

def qtnu_freq(tm, name, pname, osc, exp, vbatv, i2c):
    return (QTMU_FREQ
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@OSC@', osc).replace('@EXP@', exp).replace('@VBATV@', vbatv)
            .replace('@VAR@', pname.lower()).replace('@I2C@', i2c))

blocks.append(qtnu_freq('TM300', 'OSC64K', 'OSC64K', 'OSC64K',
    '64kHz (bench 72.67kHz trim前)',
    '4',
    '''    I2CWriteSameData(DEV_ADDR, 0x56, 0x0C);  // Write reg 0x56 = 12
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,12)] → OSC64K 路由到 DTEST0
    delay_ms(1);  // delay[1e-3]
    I2CWriteSameData(DEV_ADDR, 0xF2, 0x04);  // Write reg 0xF2 = 4
    // field[(D2A_TRIM_OSC_64K,2)] → OSC64K 修调 DAC (Trim)
    delay_ms(1);  // delay[1e-3]
'''))

blocks.append(qtnu_freq('TM301', 'OSC4P5M', 'OSC4P5M', 'OSC4P5M',
    '35kHz (分频折返)',
    '5',
    '''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm301.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x33);  // Write reg 0x56 = 51
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,51)] → OSC4P5M 路由到 DTEST0
    delay_ms(1);  // delay[1e-3]
'''))

# =====================================================================
# 构建器: ATEST0_MV (TM418/419/420/421/422/424) — 反馈电压 MV on VDM
# =====================================================================
ATEST0_MV = r'''
// =====================================================================
// @TM@: @NAME@ — @DESC@ (MV @EXP@)
// 依据: reg_config/tm@NUM@.sv (verbatim I2C/field 注释)
@NOTE@// =====================================================================
DUT_API int @FUNC@(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *@PNAME@ = StsGetParam(funcindex, "@PNAME@");
    //}}AFX_STS_PARAM_PROTOTYPES

    double @VAR@[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
@CONN2@    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, @KREL@-1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    @I2C2@    // field[(@FIELDMERGED@)] → @FIELDTAIL@

    // ====== Step 4: Measure (V(ATEST0), MV) ======
@SRCSET@    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        @VAR@[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
@PWOFF2@    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
@PWOFF3@    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        @PNAME@->SetTestResult(site, 0, @VAR@[site]);
    }
    return 0;
}
'''

def atest0_mv(tm, name, pname, desc, exp, i2c2, fieldmerged, fieldtail,
              srcset='', conn2='', krel='', pwoff2='', pwoff3='', note=''):
    return (ATEST0_MV
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@DESC@', desc).replace('@EXP@', exp)
            .replace('@I2C2@', i2c2).replace('@FIELDMERGED@', fieldmerged)
            .replace('@FIELDTAIL@', fieldtail).replace('@SRCSET@', srcset)
            .replace('@CONN2@', conn2).replace('@KREL@', krel)
            .replace('@PWOFF2@', pwoff2).replace('@PWOFF3@', pwoff3)
            .replace('@NOTE@', note).replace('@VAR@', pname.lower()))

# TM418 VAC1_FB
blocks.append(atest0_mv('TM418', 'VAC1_FB', 'VAC1_FB', 'VAC1 反馈电压 (÷10)',
    'VAC1=5V → ATEST0≈0.5V',
    '''    I2CWriteSameData(DEV_ADDR, 0x11, 0x11);  // Write reg 0x11 = 17
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
''',
    'WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,1),(EN_ATEST0,1),(ATEST0_MUX,31',
    'VAC1/10 反馈路由到 ATEST0',
    srcset='''    // vset[vac1,5,1e-3,0] → VAC1=5V (量程 10V ≥ 2×5V)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
'''))

# TM419 VAC2_FB
blocks.append(atest0_mv('TM419', 'VAC2_FB', 'VAC2_FB', 'VAC2 反馈电压 (÷10)',
    'VAC2=10V → ATEST0≈1.0V',
    '''    I2CWriteSameData(DEV_ADDR, 0x11, 0x12);  // Write reg 0x11 = 18
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
''',
    'WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,2),(EN_ATEST0,1),(ATEST0_MUX,31',
    'VAC2/10 反馈路由到 ATEST0',
    srcset='''    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share)
    // vset[vac2,10,1e-3,0] → VAC2=10V (量程 20V ≥ 2×10V)
    VAC123_AMUX_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
''',
    conn2='''    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share)
''',
    krel='K19_VAC2, ',
    pwoff2='''    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
''',
    pwoff3='''    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
'''))

# TM420 VAC3_FB
blocks.append(atest0_mv('TM420', 'VAC3_FB', 'VAC3_FB', 'VAC3 反馈电压 (÷10)',
    'VAC3=15V → ATEST0≈1.5V',
    '''    I2CWriteSameData(DEV_ADDR, 0x11, 0x13);  // Write reg 0x11 = 19
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
''',
    'WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,3),(EN_ATEST0,1),(ATEST0_MUX,31',
    'VAC3/10 反馈路由到 ATEST0',
    srcset='''    // VAC3 → VAC123_AMUX_ACM (S5_0): K18_VAC3 (Share)
    // vset[vac3,15,1e-3,0] → VAC3=15V (量程 40V ≥ 2×15V)
    VAC123_AMUX_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
''',
    conn2='''    // VAC3 → VAC123_AMUX_ACM (S5_0): K18_VAC3 (Share)
''',
    krel='K18_VAC3, ',
    pwoff2='''    VAC123_AMUX_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
''',
    pwoff3='''    VAC123_AMUX_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);
'''))

# TM421 VBUS_FB
blocks.append(atest0_mv('TM421', 'VBUS_FB', 'VBUS_FB', 'VBUS 反馈电压 (÷10)',
    'VBUS=10V → ATEST0≈1.0V',
    '''    I2CWriteSameData(DEV_ADDR, 0x11, 0x14);  // Write reg 0x11 = 20
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
''',
    'WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,4),(EN_ATEST0,1),(ATEST0_MUX,31',
    'VBUS/10 反馈路由到 ATEST0',
    srcset='''    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连
    // vset[vbus,4,1e-3,1] → VBUS=4V 预置 (量程 20V)
    VBUS_DRVH1_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vbus,10,1e-3,1] → VBUS=10V, 测 V(ATEST0) = VBUS/10 ≈ 1.0V
    VBUS_DRVH1_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
''',
    pwoff2='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
''',
    pwoff3='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
'''))

# TM422 VBAT_FB
blocks.append(atest0_mv('TM422', 'VBAT_FB', 'VBAT_FB', 'VBAT 反馈电压 (×2/5)',
    'VBAT=5V → ATEST0=5×(2/5)=2.0V; ⚠bench 1.597V@4V, 测点(4V/5V)待确认',
    '''    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x17);  // Write reg 0x5E = 23
''',
    'WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,23',
    'VBAT×2/5 反馈路由到 ATEST0 (Trim TRIM_MNT_VBAT_RSNS_LOOP ⚠)',
    srcset='''    // vset[vbat,5,100e-6,0] → VBAT=5V, 测 V(ATEST0) = VBAT×2/5 ≈ 2.0V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);  // delay[1e-3]
''',
    note='''// ⚠Trim=Y (TRIM_MNT_VBAT_RSNS_LOOP): DALI 无 .treg, 暂测默认值, Trim execute 待 treg
// ⚠.sv 末尾 vbat 4→5V 后测量; bench 记录 1.597V@VBAT3.998V (测点在 4V), 需确认
'''))

# TM424 VREF_TRIM
blocks.append(atest0_mv('TM424', 'VREF_TRIM', 'VREF_TRIM', '内部基准电压 (VREF)',
    'VREF≈1.68V (bench 1.669V)',
    '''    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x13);  // Write reg 0x5E = 19
''',
    'WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,19',
    'VREF_TRIM 路由到 ATEST0 (Trim ⚠)',
    srcset='''    // vset[vbat,4.4,100e-6,0] → VBAT=4.4V (VREF 测量供电)
    VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(2);  // delay[2e-3]
''',
    note='''// ⚠Trim=Y (TRIM_BG): DALI 无 .treg, 暂测默认值, Trim execute 待 treg
'''))

# TM425 VREF_1P2V_BUF — ATEST1 (AMUX pad) 测量, 特殊
ATEST1_MV = r'''
// =====================================================================
// TM425: VREF_1P2V_BUF — 1.2V 基准缓冲输出 (MV @ATEST1/AMUX pad)
// 期望: 1.2V (bench 1.197V); 依据: reg_config/tm425.sv (verbatim I2C/field 注释)
// ⚠Trim=Y: DALI 无 .treg, 暂测默认值, Trim execute 待 treg
// =====================================================================
DUT_API int TM425_VREF_1P2V_BUF(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VREF_1P2V_BUF = StsGetParam(funcindex, "VREF_1P2V_BUF");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vref_1p2v_buf[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // ATEST1/AMUX pad → AMUX_PGND_FXVI (S3_3): 直接连接 (K155 默认NC=AMUX)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4.4,100e-6,0] → VBAT=4.4V (1.2V 基准测量供电)
    VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm425.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x04);  // Write reg 0x57 = 4
    I2CWriteSameData(DEV_ADDR, 0x58, 0x02);  // Write reg 0x58 = 2
    // field[(WAKE_UP,1),(EN_ATEST1,1),(ATEST1_MUX,2),(DIS_NTC_DETECTION_ANALOG,1)] → VREF_1P2V_BUF 路由到 ATEST1
    delay_ms(2);  // delay[2e-3]

    // ====== Step 4: Measure (V(ATEST1/AMUX), MV) ======
    // AMUX 高阻 FI=0 测 ATEST1 电压 (FXVIe_PLUS 10V量程, 10UA最小电流档)
    AMUX_PGND_FXVI.Set(FI, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    AMUX_PGND_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vref_1p2v_buf[site] = AMUX_PGND_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VREF_1P2V_BUF->SetTestResult(site, 0, vref_1p2v_buf[site]);
    }
    return 0;
}
'''
blocks.append(ATEST1_MV)

with io.open(AI, 'r', encoding='utf-8') as f:
    orig = f.read()

new_section = '\n'.join(blocks)
with io.open(AI, 'w', encoding='utf-8', newline='') as f:
    f.write(orig + new_section)

print(f'Appended {len(blocks)} func blocks. Total new chars: {len(new_section)}')
