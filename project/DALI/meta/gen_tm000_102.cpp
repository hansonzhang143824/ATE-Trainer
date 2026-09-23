// =====================================================================
// TM000: Top Iq_Standby (MI) — 待机模式静态电流
// 合并: TM000 (w/o VAC_PLUG, ~22uA) + TM000_1 (w/i VAC_PLUG, ~31.5uA)
// 流程: VBAT=4.4V 上电 → field APORT 开关 → 测 I(VBAT)
// 闭环: VBAT_PD3_FXVI (FXVIe_PLUS S3_5, K8 默认NC直连)
// =====================================================================
DUT_API int TM000_IQ_STANDBY(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Iq_Standby      = StsGetParam(funcindex, "Iq_Standby");
    CParam *Iq_Standby_PLUG = StsGetParam(funcindex, "Iq_Standby_PLUG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iq_standby[SITE_NUM]      = { 0 };
    double iq_standby_plug[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连, 无需闭合继电器
    // SetOn(-1): 仅关闭列表中的继电器(此处为空) → 全部释放, 干净起点
    cbite.SetOn(-1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4.4,100e-6,0] → VBAT=4.4V FV
    // 电压量程 10V (≥2×4.4=8.8V), 电流量程 100UA (≥2×31.5uA)
    VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // (DFT 无 en_tm[] — DUT 默认处于 sleep 模式, 无需进入测试模式)

    // ====== Step 4: Measure (逐参数配置寄存器 + 测量) ======

    // --- TM000: Iq_Standby w/o VAC_PLUG (MI) ---
    // field[(VAC1_APORT_DET_ENABLE,0),(VAC2_APORT_DET_ENABLE,0),(VAC_SNK_DET_SEL,0)]
    //   → VAC1/2 APORT 检测关闭, VAC_PLUG 模块不唤醒
    // 0x07: bit1=VAC1_APORT_DET_ENABLE, bit2=VAC2_APORT_DET_ENABLE, bit0=VAC_SNK_DET_SEL
    // (位映射推导自 TM210~213 reg_config, 待寄存器地图复核)
    I2CWriteSameData(DEV_ADDR, 0x07, 0x00);  // Write reg 0x07 = 0 (APORT 全关)
    delay_ms(10);  // delay[10e-3] 稳定后测 I(VBAT)
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_standby[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // --- TM000_1: Iq_Standby w/i VAC_PLUG (MI) ---
    // field[(VAC1_APORT_DET_ENABLE,1),(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]
    //   → VAC1/2 APORT 检测使能, VAC_PLUG 模块唤醒
    I2CWriteSameData(DEV_ADDR, 0x07, 0x06);  // Write reg 0x07 = 6 (bit1|bit2 使能)
    delay_ms(10);
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_standby_plug[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        Iq_Standby->SetTestResult(site, 0, iq_standby[site]);
        Iq_Standby_PLUG->SetTestResult(site, 0, iq_standby_plug[site]);
    }
    return 0;
}

// =====================================================================
// TM001: Top Iin_Suspend — 挂起模式静态电流 (MI)
// 期望: ~1.118mA (WAKE_UP=1 + AC1_GATE_ON=1)
// 闭环: VBAT_PD3_FXVI (FXVIe_PLUS S3_5, K8 默认NC直连)
// =====================================================================
DUT_API int TM001_IIN_SUSPEND(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Iin_Suspend = StsGetParam(funcindex, "Iin_Suspend");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iin_suspend[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连; 无需其他继电器
    cbite.SetOn(-1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V FV
    // 电压量程 10V (≥2×3.7=7.4V), 电流量程 10MA (≥2×1.118mA)
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式
    entertestmode();
    // field[(WAKE_UP,1),(AC1_GATE_ON,1)] → 唤醒 + AC1 gate 打开
    // WAKE_UP=1 → 0x10 bit0 (AI.cpp 全部唤醒函数统一写 0x10=0x43)
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67 (WAKE_UP=1)
    // TODO: AC1_GATE_ON 位未知 (AI.cpp 无 reg_config, 待寄存器地图确认)

    // ====== Step 4: Measure (MI) ======
    delay_ms(10);  // delay[10e-3] 稳定后测 I(VBAT)
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iin_suspend[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        Iin_Suspend->SetTestResult(site, 0, iin_suspend[site]);
    }
    return 0;
}

// =====================================================================
// TM001_2: Top Iq_Shipmode — 船运模式静态电流 (MI)
// 流程: VBAT=3.7V + VAC1=5V 上电 → en_tm + SHIPMODE_EN=1 → VAC1=0 → 等60ms → 测 I(VBAT)
// 闭环: VBAT_PD3_FXVI (S3_5) + VAC123_AMUX_ACM (S5_0, K18/K19默认NC→VAC1)
// =====================================================================
DUT_API int TM001_2_IQ_SHIPMODE(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Iq_Shipmode = StsGetParam(funcindex, "Iq_Shipmode");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iq_shipmode[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC; VAC1 → VAC123_AMUX_ACM: K18/K19默认NC
    // +K21_VAC_Cap → VAC1 供电稳定; ⚠K13_VBAT_Cap 严禁闭合(Iq测量)
    cbite.SetOn(K21_VAC_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5,100e-6,0] → VAC1=5V (量程 10V ≥2×5)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x29, 0x01);  // Write reg 0x29 = 1
    // field[(SHIPMODE_EN,1)] → 进入 shipmode (reg_config/tm001_2.sv)

    // ====== Step 4: Measure (MI) ======
    // vset[vac1,0,100e-6,0] → VAC1 掉电
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(60);  // delay[60e-3] 等 shipmode 稳定后测 I(VBAT)
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_shipmode[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        Iq_Shipmode->SetTestResult(site, 0, iq_shipmode[site]);
    }
    return 0;
}

// =====================================================================
// TM001_3: Top Iq_Operation — 工作模式 VBAT 静态电流 (MI)
// DFT 备注: Covered by bench test (信息项, 生产可裁剪)
// 闭环: VBAT_PD3_FXVI + VAC123_AMUX_ACM
// =====================================================================
DUT_API int TM001_3_IQ_OPERATION(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Iq_Operation = StsGetParam(funcindex, "Iq_Operation");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iq_operation[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    cbite.SetOn(K21_VAC_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5,100e-6,0] → VAC1=5V
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[], 无 field[] 寄存器配置)

    // ====== Step 4: Measure (MI) ======
    delay_ms(10);
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_operation[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        Iq_Operation->SetTestResult(site, 0, iq_operation[site]);
    }
    return 0;
}

// =====================================================================
// TM100: HSKP ATEST0 — VS_PRE 电压测量 (MV)
// 期望: 0.5*VS_PRE ≈ 2V (VBAT=4V, BUBO 使能)
// 闭环:
//   VBAT_PD3_FXVI (FXVIe_PLUS S3_5) High→[K8 NC]→VBAT→DUT→AGND→Low
//   VDM_SDA_ACM   (ACM200 S5_7)     High→[K59 NC]→VDM(ATEST0)→DUT→AGND→Low
// ATEST0 mux 输出在 VDM pad (TestIO: VDM=ATEST0)
// =====================================================================
DUT_API int TM100_HSKP_ATEST0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VS_PRE = StsGetParam(funcindex, "VS_PRE");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vs_pre[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI (FXVIe_PLUS S3_5): K8 默认NC直连, 无需SetOn
    // VDM  → VDM_SDA_ACM   (ACM200 S5_7):     K59 默认NC=VDM直连, 无需SetOn (SetOn才切到SDA)
    // ⚠K13_VBAT_Cap: MV 测试 VBAT 供电稳定 (Cap 继电器, Component-Statistic 候选)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV模式; 10V量程(≥2×4V=8V), 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // en_tm[] → 进入测试模式
    entertestmode();

    // ====== Step 4: Measure (配置寄存器+测量) ======

    // --- TM100: VS_PRE (MV) ---
    // [DFT Software_initial] 寄存器配置 (reg_config/tm100.sv):
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x03);  // Write reg 0x5E = 3
    //   field[(EN_ATEST0,1),(ATEST0_MUX,3)]           → ATEST0_MUX=3 → VS_PRE 通路
    I2CWriteSameData(DEV_ADDR, 0x57, 0x06);  // Write reg 0x57 = 6
    I2CWriteSameData(DEV_ADDR, 0x5B, 0x50);  // Write reg 0x5B = 80
    //   field[(EN_ATEST1,1),(D2A_BUBO_ATEST1_MUX,5)]  → ATEST1 使能 + BUBO mux=5
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // Write reg 0x61 = 75
    //   field[(D2A_BUBO_EN_FORCE_ON,1),(BUBO_MODE,0)] → BUBO 强制导通, mode=0
    // VDM 高阻 FI=0 测量 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vs_pre[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VS_PRE->SetTestResult(site, 0, vs_pre[site]);
    }
    return 0;
}

// =====================================================================
// TM101: HSKP ATEST0 — LP_VBG 电压测量 (MV)
// 期望: ~1.27V (低压 bandgap 电压, ATEST0_MUX=1)
// 流程: VDM 先 FV=1.2V 稳定外部 pin → 配寄存器 → vset_off(高阻 FI=0) → 测 V(ATEST0)
// 闭环: VBAT_PD3_FXVI + VDM_SDA_ACM (同 TM100)
// =====================================================================
DUT_API int TM101_HSKP_LP_ATEST0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LP_VBG = StsGetParam(funcindex, "LP_VBG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double lp_vbg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连, 无需SetOn
    // VDM  → VDM_SDA_ACM:   K59 默认NC=VDM直连, 无需SetOn
    // ⚠K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV; 10V量程(≥2×4V), 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // en_tm[] → 进入测试模式
    entertestmode();

    // ====== Step 4: Measure (配置寄存器+测量) ======

    // --- TM101: LP_VBG (MV) ---
    // vset[vdm,1.2,100e-6,0]: 先稳定外部 pin 上电 (DFT备注: 需要先稳定外部pin上电)
    VDM_SDA_ACM.Set(FV, 1.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x01);  // Write reg 0x5E = 1
    //   field[(EN_ATEST0,1),(ATEST0_MUX,1)]           → ATEST0_MUX=1 → LP_VBG 通路 (reg_config/tm101.sv)
    // vset_off[vdm]: 释放 VDM pin — 由 FV=1.2V 切到高阻 FI=0, DUT 的 ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_vbg[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        LP_VBG->SetTestResult(site, 0, lp_vbg[site]);
    }
    return 0;
}

// =====================================================================
// TM102: HSKP ATEST0 — LP_VBG_BF 电压测量 (MV)
// 期望: ~1.27V (低压 bg 缓冲电压, ATEST0_MUX=2)
// 流程: 同 TM101 (VDM 先 FV=1.2V → 配寄存器 → vset_off → 测 V(ATEST0))
// 闭环: VBAT_PD3_FXVI + VDM_SDA_ACM (同 TM100)
// =====================================================================
DUT_API int TM102_HSKP_LP_ATEST0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LP_VBG_BF = StsGetParam(funcindex, "LP_VBG_BF");
    //}}AFX_STS_PARAM_PROTOTYPES

    double lp_vbg_bf[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连, 无需SetOn
    // VDM  → VDM_SDA_ACM:   K59 默认NC=VDM直连, 无需SetOn
    // ⚠K13_VBAT_Cap: MV 测试 VBAT 供电稳定
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV; 10V量程(≥2×4V), 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // en_tm[] → 进入测试模式
    entertestmode();

    // ====== Step 4: Measure (配置寄存器+测量) ======

    // --- TM102: LP_VBG_BF (MV) ---
    // vset[vdm,1.2,100e-6,0]: 先稳定外部 pin 上电
    VDM_SDA_ACM.Set(FV, 1.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x02);  // Write reg 0x5E = 2
    //   field[(EN_ATEST0,1),(ATEST0_MUX,2)] → LP_VBG_BF 通路 (reg_config/tm102.sv)
    // vset_off[vdm]: 释放VDM → 高阻FI=0, DUT的ATEST0输出驱动VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_vbg_bf[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        LP_VBG_BF->SetTestResult(site, 0, lp_vbg_bf[site]);
    }
    return 0;
}
