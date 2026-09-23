// =====================================================================
// AI.cpp — DALI 测试代码生成 (TM000~425)
// 生成日期: 2026-08-05 (初版 TM100~112) / 2026-08-06 (扩展 TM000~113)
//           2026-08-08 (扩展 TM114~205 与 TM206~425)
// 输入依据:
//   - Pin_Channel_define.h       源表名映射 (Sx_y → 语义源表名)
//   - SCH-Connect-Map.txt        源表→PIN/BUS 连接图 (继电器通路)
//   - Dali_testmode.xlsx         测试定义 (OVERVIEW/TestIO/ATESTMAP/DTESTMAP)
//   - CBIT表-DALI.xlsx           继电器名称与通道号
//   - C:\AccoTEST\...\INCLUDE\FXVIe.h  FXVIe_PLUS 操作函数 (FXVIe_PLUS_* 常量)
// 2026-08-05 22:11 网表更新 (S3 端口 FOVIe→FXVIe_PLUS 更名) 后验证:
//   TM000~113 全部使用语义源表名 (VBAT_PD3_FXVI/VDM_SDA_ACM/VAC123_AMUX_ACM/
//   NQON_HG1_ACM/VBUS_DRVH1_ACM/ACDRV123_VCC_ACM/SCL_VACWL_ACM), 与网表端口更名无关
// 2026-08-05 修正 (用户确认): VAC1/2/3 源表由 PB5_PC4_ACM 改为 VAC123_AMUX_ACM (S5_0)
//   反短接铁律: 源表→目标PIN的通路禁止经过/连接其他 DUT PIN (非目标PIN禁驱动),
//   除非浮动源连接了这两个 PIN (等电位/电流闭环)。
//   K69/K70/K77/K78 (PB5/VAC Share) 不再闭合 — 同时闭合会把 PB5 与 VAC1 短接。
// 2026-08-06 Toggle 参数规则 (用户确认): ramp(AWG) 测试若 DFT 有两段(升+降) →
//   参数展开为 <Base>_Rise / <Base>_Fall / <Base>_Hys, Hys = Rise - Fall
// 2026-08-06 扩展 TM000~113 (用户确认): 新增 Top Iq (TM000/000_1/001/001_2/001_3)、
//   HSKP 子项 (TM108_1 VAC1_PRST_DMO_A、TM110_1 VAC_SAFT_PB、TM110_2 VAC_WL_PRST)、
//   TM113 VCC_UV (VBAT电流折返检测);
//   TM002~006 (SCAN&IDDQ / EFUSE×3 / ABS) 按用户要求不生成 (需专用流程/设备)。
//   Iq 测试 (MI) 严禁闭合 K13_VBAT_Cap (外挂Cap2会掩盖真实静态电流, 使测量偏大)。
// 2026-08-08 扩展 TM114~205 (用户请求: 继续写 TM113~TM205): 29 个新函数 —
//   VCC 通路精度/限流 (TM114~118), VAC_PATH_ON (TM121), VMCU 精度/限流 (TM122~126),
//   VBAT 路径切换/比较器 (TM127~130), BG ATEST0 内部信号+TSD (TM131~139),
//   IO 阈值/下拉电阻/下拉电流 (TM200~205)。
//   TM119 (VBAT_PATH_ON)→tm112 覆盖, TM120 (VBUS_PATH_ON)→tm107 覆盖, TM202 (R_INT)→tm400 合并, 跳过。
//   ⚠ Trim 项 (TM133/135/139) DALI 无 .treg, 暂按"测默认值"实现, Trim execute 待 treg 确认。
//   TM204/205 DFT 用 wait_warmup[] 而非 en_tm[] (0x08 功能寄存器), 按原始设计不调 entertestmode。
// 2026-08-08 扩展 TM206~425 (用户请求: 继续从 TM205 写到 TM425): 30 个新函数 —
//   IPD 下拉电流: TM206/207 IPD_VAC2/VAC3 (0x08 下拉, wait_warmup, 不调 entertestmode)
//   SNK 检测: TM210~213 VAC1/2 SNK_DET VTH REL/ABS 模式 (Toggle, 0x07+0x56/0x57)
//   PWM 阈值: TM214/215 PWM1/2_VTH (Toggle, +0x67/0x68 D2A_OVRD 强制 IO 使能)
//   下拉电阻: TM220/222 DMO/DMA_PD_R (0x71+0x56, FI=1mA → R=V/I, ⚠机制预估)
//   OSC 频率: TM300/301 OSC64K/4P5M (QTMU_GP 测频, K66_TMU_nQON, 新继电器)
//   MNT 比较器: TM400~403/409 VBUS_OVP×3/REVI/HT (Toggle, VBUS 斜坡)
//     TM406/408/410~413 VBAT_LOW/OVP/VTRIKLE×2/VRE_CHG×2 (Toggle, VBAT 斜坡, VAC1 供电)
//     TM403 REVI 触发极性倒置 (rise→TRIG_RISING, fall→TRIG_FALLING), 结果=翻转点−VBAT
//   FB 电压: TM418~422/424 VAC1/2/3/VBUS/VBAT_FB + VREF_TRIM (ATEST0, MV on VDM)
//     TM425 VREF_1P2V_BUF (ATEST1/AMUX pad, MV on AMUX_PGND_FXVI)
//   跳过: TM208/209(→212/213), TM216~219(→214/215), TM221(→220), TM223(→222),
//     TM414/415/416(No such case)。
//   ⚠ Trim 项 (TM300/301/422/424/425) DALI 无 .treg, 暂按"测默认值"实现, Trim execute 待 treg。
//   ⚠ TM220/222 R_pd 无 OVERVIEW expect, 测量机制为预估; TM412/413 VRE_CHG Hys 为负 (极性)。
//
// 文件结构:
//   第一部分: CBIT 继电器定义 (继电器名 → CBITe 通道号)
//   第二部分: 测试内容
//     TM000/000_1 Top Iq_Standby (MI)      TM001 Iin_Suspend (MI)
//     TM001_2/001_3 Iq_Shipmode/Operation (MI)
//     TM100/101 HSKP ATEST0 (MV)           TM102/103/104 HSKP LP (MV+MI)
//     TM105 VSPRE_MAX_CMP (Toggle)         TM106/107 VBUS_PRST (Toggle)
//     TM108/108_1 VAC1_PRST (Toggle, DMO/A) TM109/110 VAC2/3_PRST (Toggle)
//     TM110_1 VAC_SAFT_PB (Toggle)         TM110_2 VAC_WL_PRST (Toggle, +K33)
//     TM111/112 VBAT_UV/HT (Toggle)        TM113 VCC_UV (MI@VBAT折返, Toggle)
//     TM114~118 VCC 通路精度/限流 (MV+MI) TM121 VAC_PATH_ON (Toggle)
//     TM122~126 VMCU 精度/限流 (MV+MI)    TM127~130 VBAT 路径切换/比较器 (Toggle)
//     TM131~139 BG ATEST0 内部信号+TSD     TM200/201 VTH_SCL/SDA_IN (Toggle)
//     TM203 R_SDA (Ω)                      TM204/205 IPD_VBUS/VAC1 (MI)
//     TM206/207 IPD_VAC2/VAC3 (MI)         TM210~213 VAC1/2 SNK_DET (Toggle)
//     TM214/215 PWM1/2_VTH (Toggle)        TM220/222 DMO/DMA_PD_R (Ω, FI负载)
//     TM300/301 OSC64K/4P5M (QTMU测频)     TM400~403/409 VBUS_OVP/REVI/HT (Toggle)
//     TM406/408/410~413 VBAT 比较器 (Toggle) TM418~422/424 FB 电压 (ATEST0 MV)
//     TM425 VREF_1P2V_BUF (ATEST1 MV)
//
// ⚠ 待办:
//   - field[]→I2CWriteSameData: TM100~112 全部 + TM001_2/108_1/110_1/110_2 已从 reg_config/*.sv 提取
//     (0x56/0x57/0x5E/0x5B/0x61/0x58/0x10/0x29, 含尾注); TM000/000_1 (APORT_DET_ENABLE)、TM001
//     (WAKE_UP/AC1_GATE_ON) 无对应 reg_config 文件, 仍待寄存器地图确认
//   - K13_VBAT_Cap 在 COMPONENT-STATISTIC 标记"需人工确认" (Cap 候选)
//   - DTEST0 观测: 触发电平 1.65V 为预估 (TM105~112/108_1/110_1/110_2), 需按实际 nQON 电平确认
//   - nQON 通路标记"单线-仅S" (K64_HG1), 观测方式需确认
//   - TM113 已实现为 ramp 两段式 (VCC_UV_Rise/_Fall/_Hys); I-trig 电平 10mA 为预估,
//     需按实际 I(VBAT) 折返电流确认
//   - TM108_1 DFT 用 wait_warmup/key1_open 而非 en_tm[], 是否需 entertestmode() 待确认
//   - TM001_3 备注 "Covered by bench test", 生产程序可裁剪
//   - TM206~425 新增待办:
//   - QTMU (TM300/301) 触发电平 1.65V 沿用 DTEST0 观测约定, 需按实际 OSC 幅度确认;
//     K66_TMU_nQON 为新继电器, 需 CBIT 表核对 S34_CBIT66 实装
//   - TM214/215 PWM VTH 需 D2A_EN_PWM_IO 使能, 已用 0x67/0x68 D2A_OVRD 强制, 需实机确认
//   - TM220/222 DMO/DMA_PD_R 无 OVERVIEW expect, R=V/I 为机制预估, 需实际电平确认
//   - TM403 VBUS_REVI 极性倒置 (rise→RISING/fall→FALLING) 与 delta=翻转−VBAT 需实机确认
//   - TM412/413 VRE_CHG Hys=Rise−Fall 为负 (幅值≈0.05), 极性特殊需确认
//   - TM422 VBAT_FB 测点 (4V/5V) 待确认 (bench 记录 1.597V@3.998V)
// =====================================================================

// =====================================================================
// 第一部分: CBIT 继电器定义 (CBIT表-DALI.xlsx, S34_CBIT<n>)
// =====================================================================
#define K4_DRVH1         4   // VBUS/DRVH1 (VBUS_DRVH1_ACM S5_10, 默认NC直连)
#define K8_PD3           8   // VBAT (FXVIe_PLUS S3_5) 默认NC直连
#define K13_VBAT_Cap    13   // VBAT Cap2
#define K18_VAC3        18   // VAC3 Share (同VAC123_AMUX_ACM通道, 默认NC走VAC1, SetOn选VAC3)
#define K19_VAC2        19   // VAC2 Share (SetOn选VAC2)
#define K21_VAC_Cap     21   // VAC Cap2
#define K25_VCC_F       25   // VCC Connect (ACDRV123_VCC_ACM S5_1)
#define K31_VMCU        31   // VCC/VMCU Share (VCC_VMCU_FXVI S3_2, 默认NC=VCC, SetOn=ON=VMCU)
#define K33_VAC_WL      33   // VAC_WL (SCL_VACWL_ACM S5_2)
#define K59_SDA         59   // VDM/SDA Share (默认NC=VDM, SetOn切SDA)
#define K64_HG1         64   // nQON/HG1 (DTEST0观测, 默认NC)
#define K65_nQON_PU     65   // nQON 上拉 (DTEST0观测)
#define K66_TMU_nQON    66   // nQON/DTEST0 → QTMU (S10_CH0_A, S34_CBIT66, TM300/301 OSC 频率测量)


// Toggle/AWG 测试方法对象 — 全局定义一次, 所有 Toggle 函数共用
Test_Method test_method;//cannot delete


// =====================================================================
// 第二部分: 测试内容
// =====================================================================

// =====================================================================
// TM000/000_1: Top Iq_Standby — 睡眠静态电流 (MI)
// TM000    Iq_Standby:     w/o VAC_PLUG 模块 (VAC1/2 APORT 检测关闭), 期望 ~22uA
// TM000_1  Iq_Standby_PLUG:w/i VAC_PLUG 模块 (VAC1/2 APORT 检测使能), 期望 ~31.5uA
// 闭环: VBAT_PD3_FXVI (FXVIe_PLUS S3_5) High→[K8 NC]→VBAT→DUT→AGND→Low
// ⚠Iq 测试严禁闭合 K13_VBAT_Cap (外挂Cap2会掩盖真实静态电流)
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
    // TODO: 解析为 I2CWriteSameData(DEV_ADDR, 0xXX, 0xXX)
    delay_ms(10);  // delay[10e-3] 稳定后测 I(VBAT)
    VBAT_PD3_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iq_standby[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET);
    }

    // --- TM000_1: Iq_Standby w/i VAC_PLUG (MI) ---
    // field[(VAC1_APORT_DET_ENABLE,1),(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]
    //   → VAC1/2 APORT 检测使能, VAC_PLUG 模块唤醒
    // TODO: 解析为 I2CWriteSameData(DEV_ADDR, 0xXX, 0xXX)
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
// 闭环: VBAT_PD3_FXVI (FXVIe_PLUS S3_5)
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
    // TODO: 解析为 I2CWriteSameData(DEV_ADDR, 0xXX, 0xXX)

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
// TM100/101: HSKP ATEST0测量 (MV) — 共享 VBAT + VDM 闭环
// TM100 VS_PRE: 0.5*VS_PRE 电压 (期望~2V, VBAT=4V, BUBO 使能)
// TM101 LP_VBG: 低压bandgap电压 (期望~1.27V, 先稳定VDM外部pin)
// 闭环:
//   VBAT_PD3_FXVI (FXVIe_PLUS S3_5) High→[K8 NC]→VBAT→DUT→AGND→Low
//   VDM_SDA_ACM   (ACM200 S5_7)     High→[K59 NC]→VDM(ATEST0)→DUT→AGND→Low
// ATEST0 mux 输出在 VDM pad (TestIO: VDM=ATEST0)
// =====================================================================
DUT_API int TM100_HSKP_ATEST0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VS_PRE = StsGetParam(funcindex, "VS_PRE");
    CParam *LP_VBG = StsGetParam(funcindex, "LP_VBG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vs_pre[SITE_NUM] = { 0 };
    double lp_vbg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI (FXVIe_PLUS S3_5): K8 默认NC直连, 无需SetOn
    // VDM  → VDM_SDA_ACM   (ACM200 S5_7):     K59 默认NC=VDM直连, 无需SetOn (SetOn才切到SDA)
    // ⚠Cap2: K13_VBAT_Cap 闭合 → VBAT供电稳定(MV测试), 但 COMPONENT-STATISTIC 标记"需人工确认", 请核实
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV模式; 10V量程(≥2×4V=8V), 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // en_tm[] → 进入测试模式
    entertestmode();

    // ====== Step 4: Measure (逐参数配置寄存器+测量) ======

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
    // 第1步: FV=0, 保持当前量程
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    // 第3步: 切小档(10V/10MA) + 关断继电器
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VS_PRE->SetTestResult(site, 0, vs_pre[site]);
        LP_VBG->SetTestResult(site, 0, lp_vbg[site]);
    }

    return 0;
}


// =====================================================================
// TM102/103/104: HSKP LP ATEST0 (MV+MI) — 共享 VBAT + VDM 闭环
// TM102 LP_VBG_BF:  低压bg缓冲电压  (MV, ATEST0_MUX=2, 期望~1.27V)
// TM103 LP_HR_0P5U:  IBP 0.5uA HR    (MI, ATEST0_MUX=4, 期望~0.5uA)
// TM104 LP_PTAT_0P5U:IBP 0.5uA PTAT  (MI, ATEST0_MUX=5, 期望~0.5uA)
// 闭环: 同 TM100/101 (VBAT_PD3_FXVI + VDM_SDA_ACM)
// =====================================================================
DUT_API int TM102_HSKP_LP_ATEST0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LP_VBG_BF   = StsGetParam(funcindex, "LP_VBG_BF");
    CParam *LP_HR_0P5U  = StsGetParam(funcindex, "LP_HR_0P5U");
    CParam *LP_PTAT_0P5U = StsGetParam(funcindex, "LP_PTAT_0P5U");
    //}}AFX_STS_PARAM_PROTOTYPES

    double lp_vbg_bf[SITE_NUM]   = { 0 };
    double lp_hr_05u[SITE_NUM]   = { 0 };
    double lp_ptat_05u[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连, 无需SetOn
    // VDM  → VDM_SDA_ACM:   K59 默认NC=VDM直连, 无需SetOn
    // ⚠K13_VBAT_Cap: MV+供电稳定 (Cap候选, 需人工确认)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV; 10V量程(≥2×4V), 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // en_tm[] → 进入测试模式
    entertestmode();

    // ====== Step 4: Measure (逐参数配置寄存器+测量) ======

    // --- TM102: LP_VBG_BF (MV) ---
    // vset[vdm,1.2,100e-6,0]: 先稳定外部pin上电
    VDM_SDA_ACM.Set(FV, 1.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x02);  // Write reg 0x5E = 2
    // field[(EN_ATEST0,1),(ATEST0_MUX,2)] → LP_VBG_BF 通路 (reg_config/tm102.sv)
    // vset_off[vdm]: 释放VDM → 高阻FI=0, DUT的ATEST0输出驱动VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_vbg_bf[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // --- TM103: LP_HR_0P5U (MI) ---
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x04);  // Write reg 0x5E = 4
    // field[(EN_ATEST0,1),(ATEST0_MUX,4)] → IBP 0.5uA HR 通路 (reg_config/tm103.sv)
    // vset[vdm,1,100e-6,0]: VDM=1V FV模式, 测I(ATEST0); 电流量程10UA(测uA级电流)
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_hr_05u[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET);
    }

    // --- TM104: LP_PTAT_0P5U (MI) ---
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x05);  // Write reg 0x5E = 5
    // field[(EN_ATEST0,1),(ATEST0_MUX,5)] → IBP 0.5uA PTAT 通路 (reg_config/tm104.sv)
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        lp_ptat_05u[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET);
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
        LP_HR_0P5U->SetTestResult(site, 0, lp_hr_05u[site]);
        LP_PTAT_0P5U->SetTestResult(site, 0, lp_ptat_05u[site]);
    }

    return 0;
}


// =====================================================================
// TM105: VSPRE_MAX_CMP — VSPRE MAX 比较器阈值 (Toggle)
// 闭环: VAC123_AMUX_ACM (ACM200 S5_0) High→[K18/K19默认NC]→VAC1→DUT→AGND→Low
// 观测: DTEST0 (nQON pad) ← NQON_HG1_ACM (ACM200 S5_9, K64 NC)
// 比较器: VS_MAX(=VAC-VDIO) vs VBAT; rising vth~0.3V, falling vth~0V @VBAT=4V
// 期望: VAC-VBAT≈1V → VAC1 上升阈值≈5V
// =====================================================================
DUT_API int TM105_VSPRE_MAX_CMP(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VSPRE_MAX_CMP_Rise = StsGetParam(funcindex, "VSPRE_MAX_CMP_Rise");
    CParam *VSPRE_MAX_CMP_Fall = StsGetParam(funcindex, "VSPRE_MAX_CMP_Fall");
    CParam *VSPRE_MAX_CMP_Hys  = StsGetParam(funcindex, "VSPRE_MAX_CMP_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT → VBAT_PD3_FXVI: K8 默认NC直连; Cap2 K13_VBAT_Cap 供电稳定
    // VAC1 → VAC123_AMUX_ACM (ACM200 S5_0): K18/K19 默认NC直连, 无需SetOn
    // Cap2: K21_VAC_Cap (VAC ramp 稳定)
    // DTEST0(nQON) → NQON_HG1_ACM: K64 NC 直连; ⚠nQON上拉 K65_nQON_PU (Toggle观测)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] → VBAT=4V FV; 10V量程, 100MA电流档
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,0)] → VSPRE_MAX_CMP 比较器输出路由到 DTEST0 (reg_config/tm105.sv)

    // ====== Step 4: Measure (Toggle: VAC1 0→10→0V) ======
    // Rise: VAC1 0→10V, DTEST0(nQON) 下降沿触发 → 抓上升阈值
    // Fall: VAC1 10→0V, DTEST0(nQON) 上升沿触发 → 抓下降阈值
    // ⚠trig=1.65V 为 DTEST0/nQON 逻辑电平预估, 需按实际nQON电平确认
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 10, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      10, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
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
        VSPRE_MAX_CMP_Rise->SetTestResult(site, 0, rise[site]);
        VSPRE_MAX_CMP_Fall->SetTestResult(site, 0, fall[site]);
        VSPRE_MAX_CMP_Hys->SetTestResult(site, 0, hys[site]);
    }

    return 0;
}

// =====================================================================
// TM106: VBUS_PRST — VBUS 上电复位比较器阈值 (Toggle)
// 闭环: VBAT_PD3_FXVI (FXVIe_PLUS S3_5) + VBUS_DRVH1_ACM (ACM200 S5_10)
// 观测: DTEST0 (nQON) ← NQON_HG1_ACM + K65_nQON_PU
// 期望: rising vth 3.9V, hys 0.2V @VBAT=3V
// =====================================================================
DUT_API int TM106_VBUS_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_PRST_Rise = StsGetParam(funcindex, "VBUS_PRST_Rise");
    CParam *VBUS_PRST_Fall = StsGetParam(funcindex, "VBUS_PRST_Fall");
    CParam *VBUS_PRST_Hys  = StsGetParam(funcindex, "VBUS_PRST_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBUS → VBUS_DRVH1_ACM: K4 默认NC直连, 无需SetOn
    // DTEST0(nQON): K64 NC + K65_nQON_PU 上拉
    // ⚠K13_VBAT_Cap (Cap候选需确认)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] → VBAT=3V (FXVIe_PLUS)
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x13);  // Write reg 0x56 = 19
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,19)] → A2D_VBUS_PRST 路由到 DTEST0 (reg_config/tm106.sv)

    // ====== Step 4: Measure (VBUS 3→5→3V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 3, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_PRST_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_PRST_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_PRST_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM107: VBUS_HT_VBAT — VBUS 与 VBAT 比较器阈值 (Toggle)
// 观测: DTEST0; 期望: rising vth 0.126V, hys 0.18V @VBAT=4V
// =====================================================================
DUT_API int TM107_VBUS_HT_VBAT(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_HT_VBAT_Rise = StsGetParam(funcindex, "VBUS_HT_VBAT_Rise");
    CParam *VBUS_HT_VBAT_Fall = StsGetParam(funcindex, "VBUS_HT_VBAT_Fall");
    CParam *VBUS_HT_VBAT_Hys  = StsGetParam(funcindex, "VBUS_HT_VBAT_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x29);  // Write reg 0x56 = 41
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,41)] → vbus_path_on 路由到 DTEST0 (reg_config/tm107.sv)

    // ====== Step 4: Measure (VBUS 2→5→2V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      2, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 2, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_HT_VBAT_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_HT_VBAT_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_HT_VBAT_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM108: VAC1_PRST — VAC1 上电复位比较器阈值 (Toggle)
// 闭环: VBAT_PD3_FXVI + VAC123_AMUX_ACM(S5_0, VAC1经K18/K19默认NC)
// 观测: DTEST0; 期望: rising vth 4.4V, hys 0.35V @VBAT=3V
// =====================================================================
DUT_API int TM108_VAC1_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST_Rise = StsGetParam(funcindex, "VAC1_PRST_Rise");
    CParam *VAC1_PRST_Fall = StsGetParam(funcindex, "VAC1_PRST_Fall");
    CParam *VAC1_PRST_Hys  = StsGetParam(funcindex, "VAC1_PRST_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1: VAC123_AMUX_ACM (ACM200 S5_0) 经 K18/K19 默认NC直连
    // Cap2: K21_VAC_Cap (VAC ramp 稳定)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] → VBAT=3V
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);  // Write reg 0x56 = 22
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,22)] → A2D_VAC1_PRST 路由到 DTEST0 (reg_config/tm108.sv)

    // ====== Step 4: Measure (VAC1 0→10→0V) ======
    // ACM200_20V 量程: 10V端点=50% (≤90%量程规则)
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 10, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      10, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
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
        VAC1_PRST_Rise->SetTestResult(site, 0, rise[site]);
        VAC1_PRST_Fall->SetTestResult(site, 0, fall[site]);
        VAC1_PRST_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM108_1: VAC1_PRST_DMO_A — VAC1 上电复位比较器阈值 (Toggle, DMO/A 输出)
// 同 TM108 但通过 DMO/A 数字输出观测 (DFT: Using DMO/A output)
// 闭环: VBAT_PD3_FXVI + VAC123_AMUX_ACM; 观测: DTEST0 (nQON)
// 期望: rising vth 4.4V, hys 0.35V @VBAT=3V
// =====================================================================
DUT_API int TM108_1_VAC1_PRST_DMO_A(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST_DMO_A_Rise = StsGetParam(funcindex, "VAC1_PRST_DMO_A_Rise");
    CParam *VAC1_PRST_DMO_A_Fall = StsGetParam(funcindex, "VAC1_PRST_DMO_A_Fall");
    CParam *VAC1_PRST_DMO_A_Hys  = StsGetParam(funcindex, "VAC1_PRST_DMO_A_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 → VAC123_AMUX_ACM: K18/K19 默认NC直连
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] → VBAT=3V
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // wait_warmup[] / key1_open[] (DFT 特有命令, 待解析为等效时序)
    // ⚠DFT 未用 en_tm[], 用 key1_open[] 进入 DMO 测试路径 — 是否需 entertestmode() 待确认
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);  // Write reg 0x56 = 22
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,22)] → A2D_VAC1_PRST 路由到 DTEST0 (reg_config/tm108_1.sv)
    I2CWriteSameData(DEV_ADDR, 0x71, 0x3B);  // Write reg 0x71 = 59
    // field[(D2A_DMO_CHANNEL_SEL,1),(D2A_DMA_CHANNEL_SEL,1),(DM_CHANNEL_SEL_OVER_WRITE,1),
    //        (D2A_DMA_EN,1),(D2A_DMO_EN,1)] → DMO/A 通道输出使能 (reg_config/tm108_1.sv)

    // ====== Step 4: Measure (VAC1 0→10→0V) ======
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 10, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      10, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC1_PRST_DMO_A_Rise->SetTestResult(site, 0, rise[site]);
        VAC1_PRST_DMO_A_Fall->SetTestResult(site, 0, fall[site]);
        VAC1_PRST_DMO_A_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM109: VAC2_PRST — VAC2 上电复位比较器阈值 (Toggle)
// 闭环: 同 TM108, VAC2 经 +K19_VAC2 (VAC123_AMUX_ACM 通道)
// =====================================================================
DUT_API int TM109_VAC2_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_PRST_Rise = StsGetParam(funcindex, "VAC2_PRST_Rise");
    CParam *VAC2_PRST_Fall = StsGetParam(funcindex, "VAC2_PRST_Fall");
    CParam *VAC2_PRST_Hys  = StsGetParam(funcindex, "VAC2_PRST_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC2: +K19_VAC2 选通 (K18_VAC3 保持NC)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, K19_VAC2, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x15);  // Write reg 0x56 = 21
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,21)] → A2D_VAC2_PRST 路由到 DTEST0 (reg_config/tm109.sv)

    // ====== Step 4: Measure (VAC2 0→10→0V) ======
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 10, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      10, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
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
        VAC2_PRST_Rise->SetTestResult(site, 0, rise[site]);
        VAC2_PRST_Fall->SetTestResult(site, 0, fall[site]);
        VAC2_PRST_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM110: VAC3_PRST — VAC3 上电复位比较器阈值 (Toggle)
// 闭环: 同 TM108, VAC3 经 +K18_VAC3 (VAC123_AMUX_ACM 通道)
// =====================================================================
DUT_API int TM110_VAC3_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC3_PRST_Rise = StsGetParam(funcindex, "VAC3_PRST_Rise");
    CParam *VAC3_PRST_Fall = StsGetParam(funcindex, "VAC3_PRST_Fall");
    CParam *VAC3_PRST_Hys  = StsGetParam(funcindex, "VAC3_PRST_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC3: +K18_VAC3 选通 (K19_VAC2 保持NC)
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, K18_VAC3, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x14);  // Write reg 0x56 = 20
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,20)] → A2D_VAC3_PRST 路由到 DTEST0 (reg_config/tm110.sv)

    // ====== Step 4: Measure (VAC3 0→10→0V) ======
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 10, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      10, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
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
        VAC3_PRST_Rise->SetTestResult(site, 0, rise[site]);
        VAC3_PRST_Fall->SetTestResult(site, 0, fall[site]);
        VAC3_PRST_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM110_1: VAC_SAFT_PB — VAC 移动电源安全检测比较器阈值 (Toggle)
// 观测: DTEST0 (DMUX_SEL=65); 期望: rising vth<2.8V, hys 0.24V
// 闭环: VBAT_PD3_FXVI + VAC123_AMUX_ACM (K18/K19默认NC→VAC1)
// =====================================================================
DUT_API int TM110_1_VAC_SAFT_PB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC_SAFT_PB_Rise = StsGetParam(funcindex, "VAC_SAFT_PB_Rise");
    CParam *VAC_SAFT_PB_Fall = StsGetParam(funcindex, "VAC_SAFT_PB_Fall");
    CParam *VAC_SAFT_PB_Hys  = StsGetParam(funcindex, "VAC_SAFT_PB_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x41);  // Write reg 0x56 = 65
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,65)] → A2D_VACDIO_PB_SAFETY_DET 路由到 DTEST0 (reg_config/tm110_1.sv)

    // ====== Step 4: Measure (VAC1 0→5→0V) ======
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC_SAFT_PB_Rise->SetTestResult(site, 0, rise[site]);
        VAC_SAFT_PB_Fall->SetTestResult(site, 0, fall[site]);
        VAC_SAFT_PB_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM110_2: VAC_WL_PRST — VAC_WL 上电复位比较器阈值 (Toggle)
// 斜坡源: SCL_VACWL_ACM (ACM200 S5_2) +K33_VAC_WL → VAC_WL
// 观测: DTEST0 (DMUX_SEL=64); 期望: rising vth>4.5V, hys 0.4V
// =====================================================================
DUT_API int TM110_2_VAC_WL_PRST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC_WL_PRST_Rise = StsGetParam(funcindex, "VAC_WL_PRST_Rise");
    CParam *VAC_WL_PRST_Fall = StsGetParam(funcindex, "VAC_WL_PRST_Fall");
    CParam *VAC_WL_PRST_Hys  = StsGetParam(funcindex, "VAC_WL_PRST_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC_WL → SCL_VACWL_ACM: +K33_VAC_WL 选通 (默认NC走SCL)
    // ⚠本测试 VAC_WL 独立于 VAC1/2/3 母线, 不闭合 K21_VAC_Cap
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K33_VAC_WL, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(wake_up,1)] → 唤醒 (reg_config/tm110_2.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x40);  // Write reg 0x56 = 64
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,64)] → A2D_VAC_WL_PRST 路由到 DTEST0 (reg_config/tm110_2.sv)

    // ====== Step 4: Measure (VAC_WL 0→5→0V) ======
    {
        test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VAC_WL_PRST_Rise->SetTestResult(site, 0, rise[site]);
        VAC_WL_PRST_Fall->SetTestResult(site, 0, fall[site]);
        VAC_WL_PRST_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM111: VBAT_UV — VBAT 欠压比较器阈值 (Toggle)
// 供电: VAC1=5V (VAC123_AMUX_ACM); 斜坡源: VBAT_PD3_FXVI
// 观测: DTEST0; 期望: rising vth 2.2V, hys 0.1V
// =====================================================================
DUT_API int TM111_VBAT_UV(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_UV_Rise = StsGetParam(funcindex, "VBAT_UV_Rise");
    CParam *VBAT_UV_Fall = StsGetParam(funcindex, "VBAT_UV_Fall");
    CParam *VBAT_UV_Hys  = StsGetParam(funcindex, "VBAT_UV_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 供电: VAC123_AMUX_ACM (ACM200 S5_0); Cap2 K21_VAC_Cap
    // VBAT 为斜坡源(非供电) → 不加 K13_VBAT_Cap (避免拉偏ramp)
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,1e-3,0] → VAC1=5V (DUT供电)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x17);  // Write reg 0x56 = 23
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,23)] → A2D_VBAT_UV 路由到 DTEST0 (reg_config/tm111.sv)

    // ====== Step 4: Measure (VBAT 0→5→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
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
        VBAT_UV_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_UV_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_UV_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM112: VBAT_HT_3P1V — VBAT 高温3.1V路径导通比较器 (Toggle)
// 供电: VAC1=5V + VBAT=2.5V初始; 斜坡源: VBAT_PD3_FXVI
// 期望: rising vth 3.1V, hys 0.1V
// =====================================================================
DUT_API int TM112_VBAT_HT_3P1V(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_HT_3P1V_Rise = StsGetParam(funcindex, "VBAT_HT_3P1V_Rise");
    CParam *VBAT_HT_3P1V_Fall = StsGetParam(funcindex, "VBAT_HT_3P1V_Fall");
    CParam *VBAT_HT_3P1V_Hys  = StsGetParam(funcindex, "VBAT_HT_3P1V_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,1e-3,0]: VBAT初始2.5V
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5,1e-3,0]: VAC1=5V (DUT供电)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x28);  // Write reg 0x56 = 40
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    I2CWriteSameData(DEV_ADDR, 0x58, 0x20);  // Write reg 0x58 = 32
    // field[(DMUX_EN,1),(DMUX_SEL,40),(D2A_REGN_TM_EN,1)] → vbat_path_on 路由到 DTEST0 (reg_config/tm112.sv)

    // ====== Step 4: Measure (VBAT 0→4→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
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
        VBAT_HT_3P1V_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_HT_3P1V_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_HT_3P1V_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}

// =====================================================================
// TM113: VCC_UV — VCC 欠压比较器阈值 (Toggle, 电流折返检测)
// VBAT=3V 供电, ramp VCC 0→5→0, 观测 I(VBAT) 折返 (VCC_UV 触发一级电流折返)
// 期望: rising vth 2.1V, hys 0.1V (bench: r 2.08 / f 1.96)
// 实现: rampv_capi — ramp源=VCC_VMCU_FXVI (S3_2, K31 NC=VCC), cap源=VBAT_PD3_FXVI
//        (S3_5) FV=3V + ITrig; 抓到折返点的 VCC 电压即 VCC_UV 阈值
// =====================================================================
DUT_API int TM113_VCC_UV(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_UV_Rise = StsGetParam(funcindex, "VCC_UV_Rise");
    CParam *VCC_UV_Fall = StsGetParam(funcindex, "VCC_UV_Fall");
    CParam *VCC_UV_Hys  = StsGetParam(funcindex, "VCC_UV_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC; +K13_VBAT_Cap 供电稳定
    // VCC  → VCC_VMCU_FXVI (S3_2): K31 默认NC=VCC 直连, 无需 SetOn
    // ⚠本测试观测 I(VBAT), 不用 DTEST0 → 不闭合 K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,1e-3,0] → VBAT=3V (cap源: FV=3V, ITrig 测 I(VBAT))
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — VCC_UV 为实时保护比较器, 正常工作模式即生效)
    // ⚠I-trig 电平 10mA 为预估, 需按实际 I(VBAT) 折返电流确认 (见头部待办)

    // ====== Step 4: Measure (VCC 0→5→0V, 抓 I(VBAT) 折返点) ======
    {
        test_method.rampv_capi(VCC_VMCU_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, 3,
                      0, 5, 200, 50, 0.01, TRIG_FALLING, rise);
        test_method.rampv_capi(VCC_VMCU_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, 3,
                      5, 0, 200, 50, 0.01, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VCC_UV_Rise->SetTestResult(site, 0, rise[site]);
        VCC_UV_Fall->SetTestResult(site, 0, fall[site]);
        VCC_UV_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}



// =====================================================================
// TM114~205: VCC 通路精度/限流 + VMCU 精度/限流 + BG ATEST0 + IO 阈值/下拉
// 2026-08-08 追加 (用户请求: 继续写 TM113~TM205; TM113 已存在, 此处为 TM114~205)
// 依据: Dali_testmode.xlsx OVERVIEW + reg_config/tm*.sv + CBIT表 + SCH-Connect-Map
// 源表映射: VCC=VCC_VMCU_FXVI(S3_2,K31 NC=VCC), VMCU=VCC_VMCU_FXVI+K31 ON,
//   VBAT=VBAT_PD3_FXVI(S3_5), VBUS=VBUS_DRVH1_ACM(S5_10), VAC1=VAC123_AMUX_ACM(S5_0),
//   AMUX=AMUX_PGND_FXVI(S3_3,K155 NC), VDM/ATEST0=VDM_SDA_ACM(S5_7,K59 NC=VDM),
//   DTEST0观测=NQON_HG1_ACM(S5_9,K64 NC)+K65_nQON_PU, SCL=SCL_VACWL_ACM(S5_2,K33 NC),
//   SDA=VDM_SDA_ACM+K59 ON
// ⚠ 待办: TM133/135/139 为 Trim 项(TRIM_ZTC_RES/TRIM_BG_RES_DIV/TRIM_BG), DALI 无 .treg,
//   暂按"测量默认值"实现, Trim execute 流程待 treg 确认后补
// =====================================================================

// =====================================================================
// TM114~118: VCC 通路精度/限流 (闭环: VBAT/VBUS/VAC1 供电 + VCC 源带载)
// TM114 VCC_VBUS_PATH_ACC:   VBUS=5V+VBAT=3.7V+VAC1=5.2V, VCC 带载50mA → V(VCC) 期望 4.2~4.5V
// TM115 VCC_VAC_PATH_ACC:    VBAT=2.5V+VAC1=5V, VCC 带载30mA → V(VCC) 期望 3.3~3.7V
// TM116 VCC_VBAT_PATH_ACC:   VBAT=3.7V, VCC 带载50mA → V(VCC) 期望 3.4~3.7V
// TM117 VCC_CUR_LIMIT_VBAT:  VBAT=4V, VCC 拉1V → I(VCC) 期望 20~70mA (bench 25mA)
// TM118 VCC_CUR_LIMIT_VBUS:  VBAT=3V+VBUS=5V, VCC 拉1V → I(VCC) 期望 30~70mA (bench 14mA)
// 注: TM115/116/117/118 DFT 无 en_tm[] (纯精度/限流测量) → 不进入测试模式
// =====================================================================
DUT_API int TM114_VCC_VBUS_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBUS_PATH_ACC = StsGetParam(funcindex, "VCC_VBUS_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vbus_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC  → VCC_VMCU_FXVI (S3_2): K31 默认NC=VCC 直连, 无需 SetOn
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap 供电稳定(MV)
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbus,5,100e-6,0] → VBUS=5V FV (10V量程≥2×5V)
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V FV
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5.2,100e-6,0] → VAC1=5.2V FV
    VAC123_AMUX_ACM.Set(FV, 5.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式 (写密钥解锁测试寄存器), 再写寄存器
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1),(REGN_VOL_SET,0)]  → 唤醒 + VCC 输出电压调节=0 (reg_config/tm114.sv)

    // ====== Step 4: Measure (VCC 带载 50mA, MV) ======
    // iset[vcc,0.05,1e-3,0] → VCC 源 FI=50mA 拉载, 测 V(VCC)
    // ⚠FI 方向: DFT 为 +0.05; 若 VCC 为 DUT 输出需"sink"加载, 可能需负号, 待确认
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vbus_path_acc[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VBUS_PATH_ACC->SetTestResult(site, 0, vcc_vbus_path_acc[site]);
    }
    return 0;
}


DUT_API int TM115_VCC_VAC_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VAC_PATH_ACC = StsGetParam(funcindex, "VCC_VAC_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vac_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC → VCC_VMCU_FXVI (K31 NC=VCC 直连); VBAT (K8 NC); VAC1 (K18/K19 NC)
    cbite.SetOn(K13_VBAT_Cap, -1);  // VBAT 供电稳定 (MV)
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,100e-6,0] → VBAT=2.5V (低压, 不主导 VCC)
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5,100e-6,0] → VAC1=5V (VCC 主供电通路)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — 纯精度测量, 不进测试模式)

    // ====== Step 4: Measure (VCC 带载 30mA, MV) ======
    // iset[vcc,0.03,1e-3,0] → VCC 源 FI=30mA 拉载, 测 V(VCC)
    // ⚠FI 方向: DFT 为 +0.03, sink 方向待确认
    VCC_VMCU_FXVI.Set(FI, 0.03, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vac_path_acc[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VAC_PATH_ACC->SetTestResult(site, 0, vcc_vac_path_acc[site]);
    }
    return 0;
}


DUT_API int TM116_VCC_VBAT_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_PATH_ACC = StsGetParam(funcindex, "VCC_VBAT_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_vbat_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC → VCC_VMCU_FXVI (K31 NC=VCC 直连); VBAT (K8 NC)
    cbite.SetOn(K13_VBAT_Cap, -1);  // VBAT 供电稳定 (MV)
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,1e-3,0] → VBAT=3.7V (VCC 唯一供电)
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令 (VBAT 稳定后等待预热), 等效延迟已含在 delay_ms 中

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — 纯精度测量, 不进测试模式)

    // ====== Step 4: Measure (VCC 带载 50mA, MV) ======
    // iset[vcc,0.05,1e-3,0] → VCC 源 FI=50mA 拉载, 测 V(VCC)
    // ⚠FI 方向: DFT 为 +0.05, sink 方向待确认
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_vbat_path_acc[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_VBAT_PATH_ACC->SetTestResult(site, 0, vcc_vbat_path_acc[site]);
    }
    return 0;
}


DUT_API int TM117_VCC_CUR_LIMIT_VBAT_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_CUR_LIMIT_VBAT_PATH = StsGetParam(funcindex, "VCC_CUR_LIMIT_VBAT_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_cur_limit_vbat_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC → VCC_VMCU_FXVI (K31 NC=VCC 直连); VBAT (K8 NC)
    // ⚠MI 限流测量: 不闭合 K13_VBAT_Cap (避免外挂Cap2分流掩盖真实限流电流)
    cbite.SetOn(-1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — 纯限流测量, 不进测试模式)

    // ====== Step 4: Measure (VCC 拉 1V, MI) ======
    // vset[vcc,1,1e-3,1] → VCC 源 FV=1V (1e-3 为初始设置), 测 I(VCC) = DUT 限流值
    // 量程: 100MA ≥ 2×70mA(限流上限), 确保能吸收 DUT 限流电流
    VCC_VMCU_FXVI.Set(FV, 1, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_cur_limit_vbat_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_CUR_LIMIT_VBAT_PATH->SetTestResult(site, 0, vcc_cur_limit_vbat_path[site]);
    }
    return 0;
}


DUT_API int TM118_VCC_CUR_LIMIT_VBUS_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_CUR_LIMIT_VBUS_PATH = StsGetParam(funcindex, "VCC_CUR_LIMIT_VBUS_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vcc_cur_limit_vbus_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VCC → VCC_VMCU_FXVI (K31 NC=VCC 直连); VBAT (K8 NC); VBUS (K4 NC)
    // ⚠MI 限流测量: 不闭合 Cap2
    cbite.SetOn(-1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] → VBAT=3V
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vbus,5,100e-6,0] → VBUS=5V
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — 纯限流测量, 不进测试模式)

    // ====== Step 4: Measure (VCC 拉 1V, MI) ======
    // vset[vcc,1,1e-3,1] → VCC 源 FV=1V, 测 I(VCC) = DUT 限流值
    VCC_VMCU_FXVI.Set(FV, 1, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vcc_cur_limit_vbus_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VCC_CUR_LIMIT_VBUS_PATH->SetTestResult(site, 0, vcc_cur_limit_vbus_path[site]);
    }
    return 0;
}


// =====================================================================
// TM119 (VBAT_PATH_ON) 由 tm112 覆盖 / TM120 (VBUS_PATH_ON) 由 tm107 覆盖 → 跳过
// =====================================================================


// =====================================================================
// TM121: VAC_PATH_ON — VAC1 供电路径导通 (Toggle)
// VBAT=3V 供电, ramp VAC1 0→5→0V, 观测 DTEST0 (A2D_VAC_PATH_ON)
// 期望: VAC1>4.4V 时 VCC 切换至 VAC1 供电 (VBAT<3.1V 前提)
// =====================================================================
DUT_API int TM121_VAC_PATH_ON(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC_PATH_ON_Rise = StsGetParam(funcindex, "VAC_PATH_ON_Rise");
    CParam *VAC_PATH_ON_Fall = StsGetParam(funcindex, "VAC_PATH_ON_Fall");
    CParam *VAC_PATH_ON_Hys  = StsGetParam(funcindex, "VAC_PATH_ON_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap 供电稳定
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (斜坡源, 不加Cap)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU (K64 NC)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3,100e-6,0] → VBAT=3V
    VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2A);  // Write reg 0x56 = 42
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,42)] → A2D_VAC_PATH_ON 路由到 DTEST0 (reg_config/tm121.sv)

    // ====== Step 4: Measure (VAC1 0→5→0V) ======
    {
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VAC123_AMUX_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      5, 0, 200, 50, 1.65, TRIG_RISING, fall);
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
        VAC_PATH_ON_Rise->SetTestResult(site, 0, rise[site]);
        VAC_PATH_ON_Fall->SetTestResult(site, 0, fall[site]);
        VAC_PATH_ON_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM122~126: VMCU 精度/限流 (VMCU 源 = VCC_VMCU_FXVI + K31 ON)
// TM122 VMCU_VBAT_PATH_ACC1 (LDO): VBAT=3.7V, 带载50mA → V(VMCU) 期望 3.2~3.7V
// TM123 VMCU_VBAT_PATH_ACC2 (LDR): 同 122, LDR 模式 → 期望 3.2~3.7V
// TM124 VMCU_VCC_PATH_ACC:   VBAT=3.7V+VBUS=5V, 带载50mA → V(VMCU) 期望 3.8~4.5V
// TM125 VMCU_CUR_LIMIT_VBAT: VBAT=3.7V, VMCU拉0.5V → I(VMCU) 期望 10~40mA
// TM126 VMCU_CUR_LIMIT_VCC:  VBAT=3.7V+VBUS=5V, VMCU拉0.5V → I(VMCU) 期望 20~70mA
// =====================================================================
DUT_API int TM122_VMCU_VBAT_PATH_ACC1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VBAT_PATH_ACC1 = StsGetParam(funcindex, "VMCU_VBAT_PATH_ACC1");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vbat_path_acc1[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU → VCC_VMCU_FXVI (S3_2): K31 ON=VMCU (SetOn 切换)
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap 供电稳定(MV)
    cbite.SetOn(K31_VMCU, K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);  // Write reg 0x29 = 16
    // field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] → 唤醒 + VMCU 由 VBAT 供电 (LDO) (reg_config/tm122.sv)

    // ====== Step 4: Measure (VMCU 带载 50mA, MV) ======
    // iset[vmcu,0.05,1e-3,0] → VMCU 源 FI=50mA 拉载, 测 V(VMCU)
    // ⚠FI 方向: DFT 为 +0.05, sink 方向待确认
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vbat_path_acc1[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VBAT_PATH_ACC1->SetTestResult(site, 0, vmcu_vbat_path_acc1[site]);
    }
    return 0;
}


DUT_API int TM123_VMCU_VBAT_PATH_ACC2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VBAT_PATH_ACC2 = StsGetParam(funcindex, "VMCU_VBAT_PATH_ACC2");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vbat_path_acc2[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU → VCC_VMCU_FXVI (K31 ON); VBAT (K8 NC); +K13_VBAT_Cap (MV)
    cbite.SetOn(K31_VMCU, K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x18);  // Write reg 0x29 = 24
    // field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1),(VMCU_VOL_BAT_PATH,1)] → VMCU 由 VBAT 供电 (LDR) (reg_config/tm123.sv)

    // ====== Step 4: Measure (VMCU 带载 50mA, MV) ======
    // iset[vmcu,0.05,1e-3,0] → VMCU 源 FI=50mA 拉载, 测 V(VMCU)
    // ⚠FI 方向: DFT 为 +0.05, sink 方向待确认
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vbat_path_acc2[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VBAT_PATH_ACC2->SetTestResult(site, 0, vmcu_vbat_path_acc2[site]);
    }
    return 0;
}


DUT_API int TM124_VMCU_VCC_PATH_ACC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_VCC_PATH_ACC = StsGetParam(funcindex, "VMCU_VCC_PATH_ACC");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_vcc_path_acc[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU → VCC_VMCU_FXVI (K31 ON); VBAT (K8 NC); VBUS (K4 NC); +K13_VBAT_Cap (MV)
    cbite.SetOn(K31_VMCU, K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vbus,5,100e-6,0] → VBUS=5V (VMCU 由 VCC/VBUS 通路供电, DFT 注"不需要VCC供电")
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    // en_tm[] → 进入测试模式 (DFT 仅 en_tm[], 无 field 寄存器写, reg_config/tm124.sv)
    entertestmode();

    // ====== Step 4: Measure (VMCU 带载 50mA, MV) ======
    // iset[vmcu,0.05,1e-3,0] → VMCU 源 FI=50mA 拉载, 测 V(VMCU)
    // ⚠FI 方向: DFT 为 +0.05, sink 方向待确认
    VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_vcc_path_acc[site] = VCC_VMCU_FXVI.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_VCC_PATH_ACC->SetTestResult(site, 0, vmcu_vcc_path_acc[site]);
    }
    return 0;
}


DUT_API int TM125_VMCU_CUR_LIMIT_VBAT_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_CUR_LIMIT_VBAT_PATH = StsGetParam(funcindex, "VMCU_CUR_LIMIT_VBAT_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_cur_limit_vbat_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU → VCC_VMCU_FXVI (K31 ON); VBAT (K8 NC)
    // ⚠MI 限流测量: 不闭合 Cap2
    cbite.SetOn(K31_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);  // Write reg 0x29 = 16
    // field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] → VMCU 由 VBAT 供电 (reg_config/tm125.sv)

    // ====== Step 4: Measure (VMCU 拉 0.5V, MI) ======
    // vset[vmcu,0.5,1e-3,0] → VMCU 源 FV=0.5V, 测 I(VMCU) = DUT 限流值
    VCC_VMCU_FXVI.Set(FV, 0.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_cur_limit_vbat_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_CUR_LIMIT_VBAT_PATH->SetTestResult(site, 0, vmcu_cur_limit_vbat_path[site]);
    }
    return 0;
}


DUT_API int TM126_VMCU_CUR_LIMIT_VCC_PATH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VMCU_CUR_LIMIT_VCC_PATH = StsGetParam(funcindex, "VMCU_CUR_LIMIT_VCC_PATH");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vmcu_cur_limit_vcc_path[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VMCU → VCC_VMCU_FXVI (K31 ON); VBAT (K8 NC); VBUS (K4 NC)
    // ⚠MI 限流测量: 不闭合 Cap2
    cbite.SetOn(K31_VMCU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.7,100e-6,0] → VBAT=3.7V
    VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vbus,5,100e-6,0] → VBUS=5V
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令, 等效延迟已含在 delay_ms 中

    // ====== Step 3: Register Config ======
    // (DFT 无 en_tm[] — 纯限流测量, 不进测试模式; reg_config/tm126.sv 仅 wait_warmup)

    // ====== Step 4: Measure (VMCU 拉 0.5V, MI) ======
    // vset[vmcu,0.5,1e-3,0] → VMCU 源 FV=0.5V, 测 I(VMCU) = DUT 限流值
    VCC_VMCU_FXVI.Set(FV, 0.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vmcu_cur_limit_vcc_path[site] = VCC_VMCU_FXVI.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VMCU_CUR_LIMIT_VCC_PATH->SetTestResult(site, 0, vmcu_cur_limit_vcc_path[site]);
    }
    return 0;
}


// =====================================================================
// TM127~130: VBAT 路径切换/比较器 (Toggle, VBAT 斜坡 → DTEST0 观测)
// TM127 VBAT_PATH_ON_VMCU: VBAT>2.8V VMCU 切 VBAT 通路 (DMUX_SEL=53)
// TM128 VBAT_PATH_ON_VCC:  VBAT>3.7V VCC 切 VBAT 通路 (DMUX_SEL=40)
// TM129 VCC_VBAT_HT_2P8:   VBAT_HT 比较器 rising vth 2.8V, hys 0.2V (DMUX_SEL=62)
// TM130 VCC_VBAT_HT_3P7:   VBAT_HT 比较器 rising vth 3.7V, hys 0.2V (DMUX_SEL=63)
// =====================================================================
DUT_API int TM127_VBAT_PATH_ON_VMCU(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_PATH_ON_VMCU_Rise = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Rise");
    CParam *VBAT_PATH_ON_VMCU_Fall = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Fall");
    CParam *VBAT_PATH_ON_VMCU_Hys  = StsGetParam(funcindex, "VBAT_PATH_ON_VMCU_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连 (供电)
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连 (斜坡源, 不加Cap)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU (K64 NC)
    cbite.SetOn(K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,2.5,100e-6,0] → VBAT 初始 2.5V (低于切换阈值 2.8V)
    VBAT_PD3_FXVI.Set(FV, 2.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vbus,5,100e-6,0] → VBUS=5V (VMCU 由 VBUS 供电)
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);  // Write reg 0x29 = 16
    // field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] → VMCU_FAVOR_VBAT!=0 (reg_config/tm127.sv)
    delay_ms(3);  // delay[3e-3] — 通路切换稳定等待
    I2CWriteSameData(DEV_ADDR, 0x56, 0x35);  // Write reg 0x56 = 53
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,53)] → VMCU VBAT_PATH_ON 路由到 DTEST0

    // ====== Step 4: Measure (VBAT 2.5→4→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      2.5, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_PATH_ON_VMCU_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_PATH_ON_VMCU_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_PATH_ON_VMCU_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


DUT_API int TM128_VBAT_PATH_ON_VCC(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_PATH_ON_VCC_Rise = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Rise");
    CParam *VBAT_PATH_ON_VCC_Fall = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Fall");
    CParam *VBAT_PATH_ON_VCC_Hys  = StsGetParam(funcindex, "VBAT_PATH_ON_VCC_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (供电); +K21_VAC_Cap
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连 (供电)
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连 (斜坡源, 不加Cap)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,3.4,100e-6,0] → VBAT 初始 3.4V (低于切换阈值 3.7V)
    VBAT_PD3_FXVI.Set(FV, 3.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[vac1,5,100e-6,0] → VAC1=5V
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    // vset[vbus,5,100e-6,0] → VBUS=5V (VCC 原由 VBUS 供电)
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x20);  // Write reg 0x29 = 32
    // field[(WAKE_UP,1),(VCC_FAVOR_VBAT,1)] → VCC_FAVOR_VBAT!=0 (reg_config/tm128.sv)
    delay_ms(3);  // delay[3e-3]
    I2CWriteSameData(DEV_ADDR, 0x56, 0x28);  // Write reg 0x56 = 40
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,40)] → VCC VBAT_PATH_ON 路由到 DTEST0

    // ====== Step 4: Measure (VBAT 3.4→4→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3.4, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBAT_PATH_ON_VCC_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_PATH_ON_VCC_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_PATH_ON_VCC_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


DUT_API int TM129_VCC_VBAT_HT_2P8(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_HT_2P8_Rise = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Rise");
    CParam *VCC_VBAT_HT_2P8_Fall = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Fall");
    CParam *VCC_VBAT_HT_2P8_Hys  = StsGetParam(funcindex, "VCC_VBAT_HT_2P8_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (供电); +K21_VAC_Cap
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连 (斜坡源, 不加Cap)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,1e-3,0] → VAC1=5V
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x10);  // Write reg 0x29 = 16
    // field[(WAKE_UP,1),(VMCU_FAVOR_VBAT,1)] (reg_config/tm129.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x3E);  // Write reg 0x56 = 62
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,62)] → VBAT_HT_2P8 路由到 DTEST0

    // ====== Step 4: Measure (VBAT 0→3→0V) ======
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
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
        VCC_VBAT_HT_2P8_Rise->SetTestResult(site, 0, rise[site]);
        VCC_VBAT_HT_2P8_Fall->SetTestResult(site, 0, fall[site]);
        VCC_VBAT_HT_2P8_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


DUT_API int TM130_VCC_VBAT_HT_3P7(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_VBAT_HT_3P7_Rise = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Rise");
    CParam *VCC_VBAT_HT_3P7_Fall = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Fall");
    CParam *VCC_VBAT_HT_3P7_Hys  = StsGetParam(funcindex, "VCC_VBAT_HT_3P7_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (供电); +K21_VAC_Cap
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连 (斜坡源, 不加Cap)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K21_VAC_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vac1,5,1e-3,0] → VAC1=5V
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x29, 0x20);  // Write reg 0x29 = 32
    // field[(WAKE_UP,1),(VCC_FAVOR_VBAT,1)] → VCC_FAVOR_VBAT=1 (reg_config/tm130.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x3F);  // Write reg 0x56 = 63
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,63)] → VBAT_HT_3P7 路由到 DTEST0

    // ====== Step 4: Measure (VBAT 0→4.5→0V) ======
    // ⚠reg_config/tm130.sv 中 DFT 迭代 3 组 VCC_FAVOR_VBAT (1/2/3 → 0x29=0x20/0x40/0x60),
    //   对应 rising vth 3.7/3.9/4.1V; 此处按 favor=1 (vth 3.7V) 实现 3 参数 Toggle,
    //   favor=2/3 是否需合并输出待 bench 确认
    {
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 4.5, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBAT_PD3_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 0, 200, 50, 1.65, TRIG_RISING, fall);
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
        VCC_VBAT_HT_3P7_Rise->SetTestResult(site, 0, rise[site]);
        VCC_VBAT_HT_3P7_Fall->SetTestResult(site, 0, fall[site]);
        VCC_VBAT_HT_3P7_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM131~139: BG 内部信号 (ATEST0 观测, ATEST0 pad = VDM pad, K59 NC=VDM)
// TM131 IRPPO_EA_FB: ATEST0_MUX=6, V(ATEST0) 期望 0.8V   (MV)
// TM132 IHR_P_1UA:   ATEST0_MUX=7, I(ATEST0) 期望 1uA    (MI, AMUX=1V+VDM=1V)
// TM133 IZTC_1UA:    ATEST0_MUX=8, I(ATEST0) 期望 1uA    (MI, Trim TRIM_ZTC_RES ⚠)
// TM134 IPTAT_1UA:   ATEST0_MUX=9, I(ATEST0) 期望 1uA    (MI)
// TM135 VREF_1P0:    ATEST0_MUX=10, V(ATEST0) 期望 1V    (MV, Trim TRIM_BG_RES_DIV ⚠)
// TM136 AVSS_BG:     ATEST0_MUX=11, V(ATEST0) 期望 0V    (MV)
// TM137 TSD_TM:      DMUX_SEL=18 + D2A_BG_TM_TSD=1, V(DTEST0) function check
// TM138 TDIE_WARM_TM:DMUX_SEL=17 + D2A_BG_TM_TSD=1, V(DTEST0) function check
// TM139 HP_VBG:      ATEST0_MUX=12, V(ATEST0) 期望 1.275V (MV, Trim TRIM_BG ⚠)
// =====================================================================
DUT_API int TM131_IRPPO_EA_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IRPPO_EA_FB = StsGetParam(funcindex, "IRPPO_EA_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double irppo_ea_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap 供电稳定(MV)
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm131.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x06);  // Write reg 0x5E = 6
    // field[(EN_ATEST0,1),(ATEST0_MUX,6)] → IRPPO_EA_FB 路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        irppo_ea_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        IRPPO_EA_FB->SetTestResult(site, 0, irppo_ea_fb[site]);
    }
    return 0;
}


DUT_API int TM132_IHR_P_1UA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IHR_P_1UA = StsGetParam(funcindex, "IHR_P_1UA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ihr_p_1ua[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // AMUX → AMUX_PGND_FXVI (S3_3): K155 默认NC直连
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[amux,1,100e-6,0] → AMUX=1V (限流100uA, 参考偏置)
    AMUX_PGND_FXVI.Set(FV, 1, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm132.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x07);  // Write reg 0x5E = 7
    // field[(EN_ATEST0,1),(ATEST0_MUX,7)] → IHR_P_1UA 路由到 ATEST0

    // ====== Step 4: Measure (I(ATEST0), MI) ======
    // vset[vdm,1,100e-6,0] → VDM/ATEST0 = 1V, 测 I(ATEST0) = 电流源电流
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ihr_p_1ua[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IHR_P_1UA->SetTestResult(site, 0, ihr_p_1ua[site]);
    }
    return 0;
}


DUT_API int TM133_IZTC_1UA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IZTC_1UA = StsGetParam(funcindex, "IZTC_1UA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iztc_1ua[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); AMUX (K155 NC); VDM/ATEST0 (K59 NC=VDM); +K13_VBAT_Cap
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[amux,1,100e-6,0] → AMUX=1V
    AMUX_PGND_FXVI.Set(FV, 1, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm133.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x08);  // Write reg 0x5E = 8
    // field[(EN_ATEST0,1),(ATEST0_MUX,8)] → IZTC_1UA 路由到 ATEST0

    // ====== Step 4: Measure (I(ATEST0), MI) ======
    // ⚠Trim 项 (TRIM_ZTC_RES): DALI 无 .treg, 暂测默认值; Trim execute 流程待 treg 确认
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iztc_1ua[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IZTC_1UA->SetTestResult(site, 0, iztc_1ua[site]);
    }
    return 0;
}


DUT_API int TM134_IPTAT_1UA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPTAT_1UA = StsGetParam(funcindex, "IPTAT_1UA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iptat_1ua[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); AMUX (K155 NC); VDM/ATEST0 (K59 NC=VDM); +K13_VBAT_Cap
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    // vset[amux,1,100e-6,0] → AMUX=1V
    AMUX_PGND_FXVI.Set(FV, 1, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm134.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x09);  // Write reg 0x5E = 9
    // field[(EN_ATEST0,1),(ATEST0_MUX,9)] → IPTAT_1UA 路由到 ATEST0

    // ====== Step 4: Measure (I(ATEST0), MI) ======
    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        iptat_1ua[site] = VDM_SDA_ACM.GetMeasResult(site, MIRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    AMUX_PGND_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPTAT_1UA->SetTestResult(site, 0, iptat_1ua[site]);
    }
    return 0;
}


DUT_API int TM135_VREF_1P0(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VREF_1P0 = StsGetParam(funcindex, "VREF_1P0");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vref_1p0[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); VDM/ATEST0 (K59 NC=VDM); +K13_VBAT_Cap
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm135.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0A);  // Write reg 0x5E = 10
    // field[(EN_ATEST0,1),(ATEST0_MUX,10)] → VREF_1P0 路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // ⚠Trim 项 (TRIM_BG_RES_DIV): DALI 无 .treg, 暂测默认值; Trim execute 流程待 treg 确认
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vref_1p0[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        VREF_1P0->SetTestResult(site, 0, vref_1p0[site]);
    }
    return 0;
}


DUT_API int TM136_AVSS_BG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *AVSS_BG = StsGetParam(funcindex, "AVSS_BG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double avss_bg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); VDM/ATEST0 (K59 NC=VDM); +K13_VBAT_Cap
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm136.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0B);  // Write reg 0x5E = 11
    // field[(EN_ATEST0,1),(ATEST0_MUX,11)] → AVSS_BG 路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        avss_bg[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        AVSS_BG->SetTestResult(site, 0, avss_bg[site]);
    }
    return 0;
}


DUT_API int TM137_TSD_TM(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *TSD_TM = StsGetParam(funcindex, "TSD_TM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double tsd_tm[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DTEST0 观测 → NQON_HG1_ACM (S5_9): K64 NC + K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm137.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x12);  // Write reg 0x56 = 18
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,18)] → TSD 比较器输出路由到 DTEST0
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x40);  // Write reg 0x58 = 64
    // field[(D2A_BG_TM_TSD,1)] → 进入 TSD 测试模式 (阈值折返, 量产无法改变温度)

    // ====== Step 4: Measure (V(DTEST0), function check) ======
    // ⚠量产无法改变温度: 仅测当前 DTEST0 电平验证比较器翻转功能
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    NQON_HG1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        tsd_tm[site] = NQON_HG1_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        TSD_TM->SetTestResult(site, 0, tsd_tm[site]);
    }
    return 0;
}


DUT_API int TM138_TDIE_WARM_TM(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *TDIE_WARM_TM = StsGetParam(funcindex, "TDIE_WARM_TM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double tdie_warm_tm[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); +K13_VBAT_Cap; DTEST0 (K64 NC + K65_nQON_PU)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm138.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x11);  // Write reg 0x56 = 17
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,17)] → TDIE_WARM 比较器输出路由到 DTEST0
    delay_ms(1);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x40);  // Write reg 0x58 = 64
    // field[(D2A_BG_TM_TSD,1)] → 进入 TSD 测试模式

    // ====== Step 4: Measure (V(DTEST0), function check) ======
    // ⚠量产无法改变温度: 仅测当前 DTEST0 电平
    NQON_HG1_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    NQON_HG1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        tdie_warm_tm[site] = NQON_HG1_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        TDIE_WARM_TM->SetTestResult(site, 0, tdie_warm_tm[site]);
    }
    return 0;
}


DUT_API int TM139_HP_VBG(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HP_VBG = StsGetParam(funcindex, "HP_VBG");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hp_vbg[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT (K8 NC); VDM/ATEST0 (K59 NC=VDM); +K13_VBAT_Cap
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm139.sv)
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x0C);  // Write reg 0x5E = 12
    // field[(EN_ATEST0,1),(ATEST0_MUX,12)] → HP_VBG 路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // ⚠Trim 项 (TRIM_BG): DALI 无 .treg, 暂测默认值; Trim execute 流程待 treg 确认
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        hp_vbg[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        HP_VBG->SetTestResult(site, 0, hp_vbg[site]);
    }
    return 0;
}


// =====================================================================
// TM200~205: IO 阈值/下拉电阻/下拉电流
// TM200 VTH_SCL_IN:  ramp SCL 0→3→0, 观测 DTEST0, rising 期望 <1.4V (DMUX_SEL=5)
// TM201 VTH_SDA_IN:  ramp SDA 0→3→0, 观测 DTEST0, rising 期望 <1.4V (DMUX_SEL=6)
// TM202 R_INT:       由 TM400 合并覆盖 (VBUS>VBUS_OVP 时测 INT 电阻) → 跳过
// TM203 R_SDA:       SDA 下拉电阻: force 10uA, R=V/I (Ω)
// TM204 IPD_VBUS:    VBUS 下拉电流, IPD = I_on − I_off (期望 20mA)
// TM205 IPD_VAC1:    VAC1 下拉电流 @VAC1=4V (期望 2mA)
// =====================================================================
DUT_API int TM200_VTH_SCL_IN(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTH_SCL_IN_Rise = StsGetParam(funcindex, "VTH_SCL_IN_Rise");
    CParam *VTH_SCL_IN_Fall = StsGetParam(funcindex, "VTH_SCL_IN_Fall");
    CParam *VTH_SCL_IN_Hys  = StsGetParam(funcindex, "VTH_SCL_IN_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // SCL  → SCL_VACWL_ACM (S5_2): K33 默认NC走SCL (斜坡源)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x05);  // Write reg 0x56 = 5
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,5)] → VTH_SCL_IN 阈值信号路由到 DTEST0 (reg_config/tm200.sv)

    // ====== Step 4: Measure (SCL 0→3→0V) ======
    {
        test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(SCL_VACWL_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    SCL_VACWL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VTH_SCL_IN_Rise->SetTestResult(site, 0, rise[site]);
        VTH_SCL_IN_Fall->SetTestResult(site, 0, fall[site]);
        VTH_SCL_IN_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


DUT_API int TM201_VTH_SDA_IN(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTH_SDA_IN_Rise = StsGetParam(funcindex, "VTH_SDA_IN_Rise");
    CParam *VTH_SDA_IN_Fall = StsGetParam(funcindex, "VTH_SDA_IN_Fall");
    CParam *VTH_SDA_IN_Hys  = StsGetParam(funcindex, "VTH_SDA_IN_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // SDA  → VDM_SDA_ACM (S5_7): K59 SetOn 切到 SDA (默认NC=VDM)
    // DTEST0 观测 → NQON_HG1_ACM: K65_nQON_PU
    cbite.SetOn(K59_SDA, K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x06);  // Write reg 0x56 = 6
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,6)] → VTH_SDA_IN 阈值信号路由到 DTEST0 (reg_config/tm201.sv)

    // ====== Step 4: Measure (SDA 0→3→0V) ======
    {
        test_method.rampv_capv(VDM_SDA_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 3, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VDM_SDA_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VTH_SDA_IN_Rise->SetTestResult(site, 0, rise[site]);
        VTH_SDA_IN_Fall->SetTestResult(site, 0, fall[site]);
        VTH_SDA_IN_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM202 R_INT: 由 TM400 合并覆盖 (merge into TM400) → 跳过, 此处仅占位
// =====================================================================


DUT_API int TM203_R_SDA(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *R_SDA = StsGetParam(funcindex, "R_SDA");
    //}}AFX_STS_PARAM_PROTOTYPES

    double r_sda[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // SDA  → VDM_SDA_ACM (S5_7): K59 SetOn 切到 SDA
    cbite.SetOn(K59_SDA, K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x67, 0x32);  // Write reg 0x67 = 50
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // Write reg 0x68 = 48
    // field[(D2A_OVRD_SEL,50),(OVRD_VALUE,3)] → d2a_sda_out 强制输出, 使 SDA 下拉电阻可测
    //   (reg_config/tm203.sv; DFT 注 "Waiting for OVRD(d2a_sda_out)")

    // ====== Step 4: Measure (R_SDA, force 10uA → V) ======
    // SDA 源 FI=10uA, 测 V(SDA) → R = V/I (Ω, R018: ≤100mA 用 Ω)
    VDM_SDA_ACM.Set(FI, 1e-5, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        r_sda[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) / 1e-5;
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
        R_SDA->SetTestResult(site, 0, r_sda[site]);
    }
    return 0;
}


DUT_API int TM204_IPD_VBUS(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VBUS = StsGetParam(funcindex, "IPD_VBUS");
    //}}AFX_STS_PARAM_PROTOTYPES

    double i_on[SITE_NUM]  = { 0 };
    double i_off[SITE_NUM] = { 0 };
    double ipd_vbus[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连
    // ⚠MI 下拉电流测量: 不闭合 Cap2 (避免掩盖下拉电流)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(5);  // delay[5e-3]
    // vset[vbus,5,100e-6,1] → VBUS=5V
    VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令, 等效延迟已含在 delay_ms 中

    // ====== Step 3: Register Config ======
    // ⚠DFT 用 wait_warmup[] 而非 en_tm[] (reg_config/tm204.sv): 0x08 为功能寄存器
    //   (VBUS 下拉), 是否需 entertestmode() 待确认 — 此处按 DFT 原始设计不调用
    I2CWriteSameData(DEV_ADDR, 0x08, 0x08);  // Write reg 0x08 = 8
    // field[(VBUS_PULLDOWN,1)] → 使能 VBUS 下拉
    delay_ms(1);
    VBUS_DRVH1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        i_on[site] = VBUS_DRVH1_ACM.GetMeasResult(site, MIRET);
    }

    I2CWriteSameData(DEV_ADDR, 0x08, 0x00);  // Write reg 0x08 = 0
    // field[(VBUS_PULLDOWN,0)] → 关闭 VBUS 下拉
    delay_ms(1);
    VBUS_DRVH1_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        i_off[site] = VBUS_DRVH1_ACM.GetMeasResult(site, MIRET);
    }

    I2CWriteSameData(DEV_ADDR, 0x08, 0x08);  // Write reg 0x08 = 8
    // field[(VBUS_PULLDOWN,1)] → 重新使能 (DFT 三次切换, 取 on/off 差分)

    // ====== Step 4: Compute IPD = I_on − I_off ======
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vbus[site] = i_on[site] - i_off[site];
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        IPD_VBUS->SetTestResult(site, 0, ipd_vbus[site]);
    }
    return 0;
}


DUT_API int TM205_IPD_VAC1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VAC1 = StsGetParam(funcindex, "IPD_VAC1");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ipd_vac1[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1
    // ⚠MI 下拉电流测量: 不闭合 Cap2
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // wait_warmup[] → DFT 特有命令 (reg_config/tm205.sv)

    // ====== Step 3: Register Config ======
    // ⚠DFT 用 wait_warmup[] 而非 en_tm[]: 0x08 为功能寄存器 (VAC1 下拉), 按 DFT 不调用 entertestmode
    I2CWriteSameData(DEV_ADDR, 0x08, 0x40);  // Write reg 0x08 = 64
    // field[(VAC1_PULLDOWN,1)] → 使能 VAC1 下拉

    // ====== Step 4: Measure (VAC1 1V→4V, MI) ======
    // vset[vac1,1,1e-3,0] → VAC1=1V 预置
    VAC123_AMUX_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac1,4,1e-3,0] → VAC1=4V, 测 I(VAC1) = 下拉电流 (期望 2mA)
    VAC123_AMUX_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VAC123_AMUX_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        ipd_vac1[site] = VAC123_AMUX_ACM.GetMeasResult(site, MIRET);
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
        IPD_VAC1->SetTestResult(site, 0, ipd_vac1[site]);
    }
    return 0;
}

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


// =====================================================================
// TM406: VBAT_LOW_VTH — VBAT 低压比较器 (boost) (Toggle)
// 期望: rising 2.7V / falling 2.5V, hys 0.2V
// 依据: reg_config/tm406.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM406_VBAT_LOW_VTH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_LOW_VTH_Rise = StsGetParam(funcindex, "VBAT_LOW_VTH_Rise");
    CParam *VBAT_LOW_VTH_Fall = StsGetParam(funcindex, "VBAT_LOW_VTH_Fall");
    CParam *VBAT_LOW_VTH_Hys  = StsGetParam(funcindex, "VBAT_LOW_VTH_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);  // Write reg 0x09 = 10
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);  // Write reg 0x56 = 26
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,26),(BUBO_MODE,1)] → A2D_VBAT_LOW(boost) 路由到 DTEST0

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
        VBAT_LOW_VTH_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_LOW_VTH_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_LOW_VTH_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM408: VBAT_OVP — VBAT 过压比较器 (buck) (Toggle)
// 期望: rising 104%·VBAT_CV=4.368V / falling 102%·VBAT_CV=4.284V, hys 2% (VBAT_CV=4.2V)
// 依据: reg_config/tm408.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM408_VBAT_OVP(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_OVP_Rise = StsGetParam(funcindex, "VBAT_OVP_Rise");
    CParam *VBAT_OVP_Fall = StsGetParam(funcindex, "VBAT_OVP_Fall");
    CParam *VBAT_OVP_Hys  = StsGetParam(funcindex, "VBAT_OVP_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1C);  // Write reg 0x56 = 28
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,28),(VBAT_CV,9)] → A2D_VBAT_OVP(buck) 路由到 DTEST0

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
        VBAT_OVP_Rise->SetTestResult(site, 0, rise[site]);
        VBAT_OVP_Fall->SetTestResult(site, 0, fall[site]);
        VBAT_OVP_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM410: VTRIKLE_VTH1 — VBAT 涓流充电阈值1 (buck) (Toggle)
// 期望: rising 2.7V / falling 2.4V, hys 0.3V
// 依据: reg_config/tm410.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM410_VTRIKLE_VTH1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTRIKLE_VTH1_Rise = StsGetParam(funcindex, "VTRIKLE_VTH1_Rise");
    CParam *VTRIKLE_VTH1_Fall = StsGetParam(funcindex, "VTRIKLE_VTH1_Fall");
    CParam *VTRIKLE_VTH1_Hys  = StsGetParam(funcindex, "VTRIKLE_VTH1_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x0A, 0x09);  // Write reg 0x0A = 9
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);  // Write reg 0x56 = 29
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VTRICKLE,0)(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] → A2D_VTRIKLE_VTH1(buck) 路由到 DTEST0

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
        VTRIKLE_VTH1_Rise->SetTestResult(site, 0, rise[site]);
        VTRIKLE_VTH1_Fall->SetTestResult(site, 0, fall[site]);
        VTRIKLE_VTH1_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM411: VTRIKLE_VTH2 — VBAT 涓流充电阈值2 (buck) (Toggle)
// 期望: rising 3.0V / falling 2.7V, hys 0.3V
// 依据: reg_config/tm411.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM411_VTRIKLE_VTH2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTRIKLE_VTH2_Rise = StsGetParam(funcindex, "VTRIKLE_VTH2_Rise");
    CParam *VTRIKLE_VTH2_Fall = StsGetParam(funcindex, "VTRIKLE_VTH2_Fall");
    CParam *VTRIKLE_VTH2_Hys  = StsGetParam(funcindex, "VTRIKLE_VTH2_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);  // Write reg 0x56 = 29
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VTRICKLE,1)(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] → A2D_VTRIKLE_VTH2(buck) 路由到 DTEST0

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
        VTRIKLE_VTH2_Rise->SetTestResult(site, 0, rise[site]);
        VTRIKLE_VTH2_Fall->SetTestResult(site, 0, fall[site]);
        VTRIKLE_VTH2_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM412: VRE_CHG_VTH1 — VBAT 再充电阈值1 (buck) (Toggle)
// 期望: rising VBAT_CV−0.1≈4.0V / falling 3.95V, hys 0.05V; ⚠极性: Hys=Rise−Fall 为负 (幅值≈0.05)
// 依据: reg_config/tm412.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM412_VRE_CHG_VTH1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VRE_CHG_VTH1_Rise = StsGetParam(funcindex, "VRE_CHG_VTH1_Rise");
    CParam *VRE_CHG_VTH1_Fall = StsGetParam(funcindex, "VRE_CHG_VTH1_Fall");
    CParam *VRE_CHG_VTH1_Hys  = StsGetParam(funcindex, "VRE_CHG_VTH1_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);  // Write reg 0x56 = 27
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VRE_CHG,0)(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] → A2D_VRE_CHG_VTH1(buck) 路由到 DTEST0

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
        VRE_CHG_VTH1_Rise->SetTestResult(site, 0, rise[site]);
        VRE_CHG_VTH1_Fall->SetTestResult(site, 0, fall[site]);
        VRE_CHG_VTH1_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM413: VRE_CHG_VTH2 — VBAT 再充电阈值2 (buck) (Toggle)
// 期望: rising VBAT_CV−0.1≈3.9V / falling 3.85V, hys 0.05V; ⚠极性: Hys=Rise−Fall 为负 (幅值≈0.05)
// 依据: reg_config/tm413.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM413_VRE_CHG_VTH2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VRE_CHG_VTH2_Rise = StsGetParam(funcindex, "VRE_CHG_VTH2_Rise");
    CParam *VRE_CHG_VTH2_Fall = StsGetParam(funcindex, "VRE_CHG_VTH2_Fall");
    CParam *VRE_CHG_VTH2_Hys  = StsGetParam(funcindex, "VRE_CHG_VTH2_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x0A, 0x69);  // Write reg 0x0A = 105
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);  // Write reg 0x56 = 27
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VRE_CHG,1)(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] → A2D_VRE_CHG_VTH2(buck) 路由到 DTEST0

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
        VRE_CHG_VTH2_Rise->SetTestResult(site, 0, rise[site]);
        VRE_CHG_VTH2_Fall->SetTestResult(site, 0, fall[site]);
        VRE_CHG_VTH2_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM400: VBUS_OVP_VTH1 — VBUS 过压阈值1 (Toggle)
// 期望: rising 6.5V / falling 6.2V, hys 0.3V
// 依据: reg_config/tm400.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM400_VBUS_OVP_VTH1(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH1_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH1_Rise");
    CParam *VBUS_OVP_VTH1_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH1_Fall");
    CParam *VBUS_OVP_VTH1_Hys  = StsGetParam(funcindex, "VBUS_OVP_VTH1_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VBUS_OVP,0),(DMUX_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH1) 路由到 DTEST0

    // ====== Step 4: Measure (VBUS 4→7→4V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 7, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      7, 4, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH1_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_OVP_VTH1_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_OVP_VTH1_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM401: VBUS_OVP_VTH2 — VBUS 过压阈值2 (Toggle)
// 期望: rising 12.8V / falling 12.5V, hys 0.3V
// 依据: reg_config/tm401.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM401_VBUS_OVP_VTH2(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH2_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH2_Rise");
    CParam *VBUS_OVP_VTH2_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH2_Fall");
    CParam *VBUS_OVP_VTH2_Hys  = StsGetParam(funcindex, "VBUS_OVP_VTH2_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x0C, 0x08);  // Write reg 0x0C = 8
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(VBUS_OVP,2),(DMUX_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH2) 路由到 DTEST0

    // ====== Step 4: Measure (VBUS 4→15→4V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 15, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      15, 4, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH2_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_OVP_VTH2_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_OVP_VTH2_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM402: VBUS_OVP_VTH3 — VBUS 过压阈值3 (Toggle)
// 期望: rising 18.8V / falling 18.5V, hys 0.3V
// 依据: reg_config/tm402.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM402_VBUS_OVP_VTH3(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH3_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH3_Rise");
    CParam *VBUS_OVP_VTH3_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH3_Fall");
    CParam *VBUS_OVP_VTH3_Hys  = StsGetParam(funcindex, "VBUS_OVP_VTH3_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x0C, 0x14);  // Write reg 0x0C = 20
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x20);  // Write reg 0x56 = 32
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    I2CWriteSameData(DEV_ADDR, 0xFF, 0x04);  // Write reg 0xFF = 4
    // field[(WAKE_UP,1),(VBUS_OVP,5),(DMUX_EN,1),(MPP_EN,1),(DMUX_SEL,32)] → A2D_VBUS_OVP(VTH3) 路由到 DTEST0

    // ====== Step 4: Measure (VBUS 4→20→4V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 20, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_40V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      20, 4, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_OVP_VTH3_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_OVP_VTH3_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_OVP_VTH3_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM409: VBUS_HT_4P8V — VBUS 高温路径4.8V (boost) (Toggle)
// 期望: rising 4.8V (bench 4.661V)
// 依据: reg_config/tm409.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM409_VBUS_HT_4P8V(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_HT_4P8V_Rise = StsGetParam(funcindex, "VBUS_HT_4P8V_Rise");
    CParam *VBUS_HT_4P8V_Fall = StsGetParam(funcindex, "VBUS_HT_4P8V_Fall");
    CParam *VBUS_HT_4P8V_Hys  = StsGetParam(funcindex, "VBUS_HT_4P8V_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);  // Write reg 0x09 = 10
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1F);  // Write reg 0x56 = 31
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,31),(BUBO_MODE,1)] → A2D_VBUS_HT_4P8V(boost) 路由到 DTEST0

    // ====== Step 4: Measure (VBUS 4→7→4V) ======
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 7, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_20V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      7, 4, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_HT_4P8V_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_HT_4P8V_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_HT_4P8V_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM403: VBUS_REVI_VTH — VBUS 反向电流检测 (Toggle)
// 期望: falling VBUS−VBAT≈−120mV / rising 0V (bench f−0.138/r−0.016)
// 依据: reg_config/tm403.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM403_VBUS_REVI_VTH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_REVI_VTH_Rise = StsGetParam(funcindex, "VBUS_REVI_VTH_Rise");
    CParam *VBUS_REVI_VTH_Fall = StsGetParam(funcindex, "VBUS_REVI_VTH_Fall");
    CParam *VBUS_REVI_VTH_Hys  = StsGetParam(funcindex, "VBUS_REVI_VTH_Hys");
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
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1E);  // Write reg 0x56 = 30
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] → A2D_VBUS_REVI 路由到 DTEST0

    // ====== Step 4: Measure (VBUS 3.7→4.5→3.7V) ======
    // ⚠REVI 极性: VBUS<VBAT 时故障(REVI 激活,nQON低); VBUS 上升段 REVI 解除 → nQON 上升沿 = TRIG_RISING
    // 下降段 REVI 激活 → nQON 下降沿 = TRIG_FALLING (与常规比较器相反)
    {
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      3.7, 4.5, 200, 50, 1.65, TRIG_RISING, rise);
        test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4.5, 3.7, 200, 50, 1.65, TRIG_FALLING, fall);
    }
    // 结果 = VBUS翻转点 − VBAT(4V): 期望 falling≈−0.12V / rising≈0V
    FOR_EACH_VALID_SITE(site)
    {
        rise[site] = rise[site] - 4.0;
        fall[site] = fall[site] - 4.0;
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_REVI_VTH_Rise->SetTestResult(site, 0, rise[site]);
        VBUS_REVI_VTH_Fall->SetTestResult(site, 0, fall[site]);
        VBUS_REVI_VTH_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM214: PWM1_VTH — PWM1 输入阈值 (Toggle)
// 期望: rising 1.4V / falling 0.6V, hys 0.8V (OVERVIEW)
// 依据: reg_config/tm214.sv (verbatim I2C/field 注释)
// ⚠0x67/0x68 D2A_OVRD 强制 PWM IO 使能 (D2A_EN_PWM_IO), 阈值检测经 DTEST0
// =====================================================================
DUT_API int TM214_PWM1_VTH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM1_VTH_Rise = StsGetParam(funcindex, "PWM1_VTH_Rise");
    CParam *PWM1_VTH_Fall = StsGetParam(funcindex, "PWM1_VTH_Fall");
    CParam *PWM1_VTH_Hys  = StsGetParam(funcindex, "PWM1_VTH_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // PWM1 → PB0_BST_ACM (S5_18, 直接连接, 斜坡源)
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
    // field[(WAKE_UP,1)] (reg_config/tm214.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2E);  // Write reg 0x56 = 46
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,46)] → PWM1 阈值信号路由到 DTEST0
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);  // Write reg 0x67 = 48
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // Write reg 0x68 = 48
    // field[(D2A_OVRD_SEL,48),(ovrd_value,3)] → D2A 强制 PWM1 IO 使能
    delay_ms(2);  // delay[2e-3]

    // ====== Step 4: Measure (PWM1 0→4→0V) ======
    {
        test_method.rampv_capv(PB0_BST_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(PB0_BST_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PB0_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        PWM1_VTH_Rise->SetTestResult(site, 0, rise[site]);
        PWM1_VTH_Fall->SetTestResult(site, 0, fall[site]);
        PWM1_VTH_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM215: PWM2_VTH — PWM2 输入阈值 (Toggle)
// 期望: rising 1.4V / falling 0.6V, hys 0.8V (OVERVIEW)
// 依据: reg_config/tm215.sv (verbatim I2C/field 注释)
// ⚠0x67/0x68 D2A_OVRD 强制 PWM IO 使能 (D2A_EN_PWM_IO), 阈值检测经 DTEST0
// =====================================================================
DUT_API int TM215_PWM2_VTH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PWM2_VTH_Rise = StsGetParam(funcindex, "PWM2_VTH_Rise");
    CParam *PWM2_VTH_Fall = StsGetParam(funcindex, "PWM2_VTH_Fall");
    CParam *PWM2_VTH_Hys  = StsGetParam(funcindex, "PWM2_VTH_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise[SITE_NUM] = { 0 };
    double fall[SITE_NUM] = { 0 };
    double hys[SITE_NUM]  = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // PWM2 → PA6_PC5_ACM (S5_19, 直接连接, 斜坡源)
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
    // field[(WAKE_UP,1)] (reg_config/tm215.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x2D);  // Write reg 0x56 = 45
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,45)] → PWM2 阈值信号路由到 DTEST0
    I2CWriteSameData(DEV_ADDR, 0x67, 0x30);  // Write reg 0x67 = 48
    I2CWriteSameData(DEV_ADDR, 0x68, 0x30);  // Write reg 0x68 = 48
    // field[(D2A_OVRD_SEL,48),(ovrd_value,3)] → D2A 强制 PWM2 IO 使能
    delay_ms(2);  // delay[2e-3]

    // ====== Step 4: Measure (PWM2 0→4→0V) ======
    {
        test_method.rampv_capv(PA6_PC5_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      0, 4, 200, 50, 1.65, TRIG_FALLING, rise);
        test_method.rampv_capv(PA6_PC5_ACM, ACM200_10V, ACM200_100MA,
                      NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                      4, 0, 200, 50, 1.65, TRIG_RISING, fall);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PA6_PC5_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = rise[site] - fall[site];
    }
    FOR_EACH_VALID_SITE(site)
    {
        PWM2_VTH_Rise->SetTestResult(site, 0, rise[site]);
        PWM2_VTH_Fall->SetTestResult(site, 0, fall[site]);
        PWM2_VTH_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}


// =====================================================================
// TM220: DMO_PD_R — DMO 下拉/推挽电阻测量 (FI 负载法)
// 依据: reg_config/tm220.sv (verbatim I2C/field 注释)
// ⚠OVERVIEW expect 空: 测量机制为预估 (FI=1mA 灌入低态输出, R=V/I ≈ Rds_on)
// =====================================================================
DUT_API int TM220_DMO_PD_R(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *DMO_PD_R = StsGetParam(funcindex, "DMO_PD_R");
    //}}AFX_STS_PARAM_PROTOTYPES

    double dmo_pd_r[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DMO → PC8_PC6_ACM (S5_12, 直接连接)
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (DMO 数字输入源)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x71, 0x2A);  // Write reg 0x71 = 42
    // field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMO_EN,1),(D2A_DMO_CHANNEL_SEL,1)] → DMO 作为 D2A 数字输出
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);  // Write reg 0x56 = 22
    // field[(DMUX_SEL,22)] → DMO 输出路由到 DTEST0 (reg_config/tm220.sv)

    // ====== Step 4: Measure (DMO 低态下拉电阻) ======
    // vset[vac1,5,10e-3,0] → VAC1=5V: DMO 缓冲输出 HIGH (功能确认)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac1,0,10e-3,0] → VAC1=0V: DMO 缓冲输出 LOW
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(2);  // delay[2e-3]
    // FI=1mA 灌入 DMO, 测 V → R = V/I (⚠机制预估)
    PC8_PC6_ACM.Set(FI, 1e-3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    PC8_PC6_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        dmo_pd_r[site] = PC8_PC6_ACM.GetMeasResult(site, MVRET) / 1e-3;  // Ω
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PC8_PC6_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PC8_PC6_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        DMO_PD_R->SetTestResult(site, 0, dmo_pd_r[site]);
    }
    return 0;
}


// =====================================================================
// TM222: DMA_PD_R — DMA 下拉/推挽电阻测量 (FI 负载法)
// 依据: reg_config/tm222.sv (verbatim I2C/field 注释)
// ⚠OVERVIEW expect 空: 测量机制为预估 (FI=1mA 灌入低态输出, R=V/I ≈ Rds_on)
// =====================================================================
DUT_API int TM222_DMA_PD_R(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *DMA_PD_R = StsGetParam(funcindex, "DMA_PD_R");
    //}}AFX_STS_PARAM_PROTOTYPES

    double dma_pd_r[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DMA → PA7_PD2_ACM (S5_23, 直接连接)
    // VAC1 → VAC123_AMUX_ACM (S5_0): K18/K19 默认NC走VAC1 (DMO 数字输入源)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x71, 0x31);  // Write reg 0x71 = 49
    // field[(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMA_EN,1),(D2A_DMA_CHANNEL_SEL,1)] → DMA 作为 D2A 数字输出
    I2CWriteSameData(DEV_ADDR, 0x56, 0x16);  // Write reg 0x56 = 22
    // field[(DMUX_SEL,22)] → DMA 输出路由到 DTEST0 (reg_config/tm222.sv)

    // ====== Step 4: Measure (DMA 低态下拉电阻) ======
    // vset[vac1,5,10e-3,0] → VAC1=5V: DMA 缓冲输出 HIGH (功能确认)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vac1,0,10e-3,0] → VAC1=0V: DMA 缓冲输出 LOW
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(2);  // delay[2e-3]
    // FI=1mA 灌入 DMA, 测 V → R = V/I (⚠机制预估)
    PA7_PD2_ACM.Set(FI, 1e-3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    delay_ms(1);
    PA7_PD2_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        dma_pd_r[site] = PA7_PD2_ACM.GetMeasResult(site, MVRET) / 1e-3;  // Ω
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PA7_PD2_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PA7_PD2_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        DMA_PD_R->SetTestResult(site, 0, dma_pd_r[site]);
    }
    return 0;
}


// =====================================================================
// TM300: OSC64K — OSC64K 频率测量 (QTMU, DTEST0/nQON)
// 期望: 64kHz (bench 72.67kHz trim前); 依据: reg_config/tm300.sv (verbatim I2C/field 注释)
// ⚠Trim=Y: D2A_TRIM_OSC 修调项 DALI 无 .treg, 暂测默认频率, Trim execute 待 treg
// ⚠QTMU 触发电平 1.65V 沿用 DTEST0 观测约定, 需按实际 OSC 幅度确认
// =====================================================================
DUT_API int TM300_OSC64K(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC64K = StsGetParam(funcindex, "OSC64K");
    //}}AFX_STS_PARAM_PROTOTYPES

    double osc64k[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DTEST0(OSC) → QTMU (S10 CH0_A): K66_TMU_nQON; +K65_nQON_PU 上拉
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x0C);  // Write reg 0x56 = 12
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,12)] → OSC64K 路由到 DTEST0
    delay_ms(1);  // delay[1e-3]
    I2CWriteSameData(DEV_ADDR, 0xF2, 0x04);  // Write reg 0xF2 = 4
    // field[(D2A_TRIM_OSC_64K,2)] → OSC64K 修调 DAC (Trim)
    delay_ms(1);  // delay[1e-3]

    // ====== Step 4: Measure (QTMU 频率, KHz) ======
    // nQON/DTEST0 → QTMU S10 CHA (K66), 频率测量 (结果 KHz)
    QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
    QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
    QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 1.65, QTMUe_FILTER_PASS);
    QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS);
    FOR_EACH_VALID_SITE(site)
    {
        osc64k[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
    }
    QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        OSC64K->SetTestResult(site, 0, osc64k[site]);
    }
    return 0;
}


// =====================================================================
// TM301: OSC4P5M — OSC4P5M 频率测量 (QTMU, DTEST0/nQON)
// 期望: 35kHz (分频折返); 依据: reg_config/tm301.sv (verbatim I2C/field 注释)
// ⚠Trim=Y: D2A_TRIM_OSC 修调项 DALI 无 .treg, 暂测默认频率, Trim execute 待 treg
// ⚠QTMU 触发电平 1.65V 沿用 DTEST0 观测约定, 需按实际 OSC 幅度确认
// =====================================================================
DUT_API int TM301_OSC4P5M(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC4P5M = StsGetParam(funcindex, "OSC4P5M");
    //}}AFX_STS_PARAM_PROTOTYPES

    double osc4p5m[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // DTEST0(OSC) → QTMU (S10 CH0_A): K66_TMU_nQON; +K65_nQON_PU 上拉
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] → VBAT=5V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
    // field[(WAKE_UP,1)] (reg_config/tm301.sv)
    I2CWriteSameData(DEV_ADDR, 0x56, 0x33);  // Write reg 0x56 = 51
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);  // Write reg 0x57 = 8
    // field[(DMUX_EN,1),(DMUX_SEL,51)] → OSC4P5M 路由到 DTEST0
    delay_ms(1);  // delay[1e-3]

    // ====== Step 4: Measure (QTMU 频率, KHz) ======
    // nQON/DTEST0 → QTMU S10 CHA (K66), 频率测量 (结果 KHz)
    QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
    QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
    QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 1.65, QTMUe_FILTER_PASS);
    QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS);
    FOR_EACH_VALID_SITE(site)
    {
        osc4p5m[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
    }
    QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        OSC4P5M->SetTestResult(site, 0, osc4p5m[site]);
    }
    return 0;
}


// =====================================================================
// TM418: VAC1_FB — VAC1 反馈电压 (÷10) (MV VAC1=5V → ATEST0≈0.5V)
// 依据: reg_config/tm418.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM418_VAC1_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_FB = StsGetParam(funcindex, "VAC1_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac1_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x11, 0x11);  // Write reg 0x11 = 17
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
    // field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,1),(EN_ATEST0,1),(ATEST0_MUX,31)] → VAC1/10 反馈路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // vset[vac1,5,1e-3,0] → VAC1=5V (量程 10V ≥ 2×5V)
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vac1_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        VAC1_FB->SetTestResult(site, 0, vac1_fb[site]);
    }
    return 0;
}


// =====================================================================
// TM419: VAC2_FB — VAC2 反馈电压 (÷10) (MV VAC2=10V → ATEST0≈1.0V)
// 依据: reg_config/tm419.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM419_VAC2_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC2_FB = StsGetParam(funcindex, "VAC2_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac2_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share)
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, K19_VAC2, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x11, 0x12);  // Write reg 0x11 = 18
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
    // field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,2),(EN_ATEST0,1),(ATEST0_MUX,31)] → VAC2/10 反馈路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // VAC2 → VAC123_AMUX_ACM (S5_0): K19_VAC2 (Share)
    // vset[vac2,10,1e-3,0] → VAC2=10V (量程 20V ≥ 2×10V)
    VAC123_AMUX_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vac2_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC2_FB->SetTestResult(site, 0, vac2_fb[site]);
    }
    return 0;
}


// =====================================================================
// TM420: VAC3_FB — VAC3 反馈电压 (÷10) (MV VAC3=15V → ATEST0≈1.5V)
// 依据: reg_config/tm420.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM420_VAC3_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC3_FB = StsGetParam(funcindex, "VAC3_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vac3_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VAC3 → VAC123_AMUX_ACM (S5_0): K18_VAC3 (Share)
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, K18_VAC3, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x11, 0x13);  // Write reg 0x11 = 19
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
    // field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,3),(EN_ATEST0,1),(ATEST0_MUX,31)] → VAC3/10 反馈路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // VAC3 → VAC123_AMUX_ACM (S5_0): K18_VAC3 (Share)
    // vset[vac3,15,1e-3,0] → VAC3=15V (量程 40V ≥ 2×15V)
    VAC123_AMUX_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vac3_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VAC3_FB->SetTestResult(site, 0, vac3_fb[site]);
    }
    return 0;
}


// =====================================================================
// TM421: VBUS_FB — VBUS 反馈电压 (÷10) (MV VBUS=10V → ATEST0≈1.0V)
// 依据: reg_config/tm421.sv (verbatim I2C/field 注释)
// =====================================================================
DUT_API int TM421_VBUS_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_FB = StsGetParam(funcindex, "VBUS_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbus_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x11, 0x14);  // Write reg 0x11 = 20
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);  // Write reg 0x5E = 31
    // field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,4),(EN_ATEST0,1),(ATEST0_MUX,31)] → VBUS/10 反馈路由到 ATEST0

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // VBUS → VBUS_DRVH1_ACM (S5_10): K4 默认NC直连
    // vset[vbus,4,1e-3,1] → VBUS=4V 预置 (量程 20V)
    VBUS_DRVH1_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // vset[vbus,10,1e-3,1] → VBUS=10V, 测 V(ATEST0) = VBUS/10 ≈ 1.0V
    VBUS_DRVH1_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vbus_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_FB->SetTestResult(site, 0, vbus_fb[site]);
    }
    return 0;
}


// =====================================================================
// TM422: VBAT_FB — VBAT 反馈电压 (×2/5) (MV VBAT=5V → ATEST0=5×(2/5)=2.0V; ⚠bench 1.597V@4V, 测点(4V/5V)待确认)
// 依据: reg_config/tm422.sv (verbatim I2C/field 注释)
// ⚠Trim=Y (TRIM_MNT_VBAT_RSNS_LOOP): DALI 无 .treg, 暂测默认值, Trim execute 待 treg
// ⚠.sv 末尾 vbat 4→5V 后测量; bench 记录 1.597V@VBAT3.998V (测点在 4V), 需确认
// =====================================================================
DUT_API int TM422_VBAT_FB(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_FB = StsGetParam(funcindex, "VBAT_FB");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vbat_fb[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x17);  // Write reg 0x5E = 23
    // field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,23)] → VBAT×2/5 反馈路由到 ATEST0 (Trim TRIM_MNT_VBAT_RSNS_LOOP ⚠)

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // vset[vbat,5,100e-6,0] → VBAT=5V, 测 V(ATEST0) = VBAT×2/5 ≈ 2.0V
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);  // delay[1e-3]
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vbat_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        VBAT_FB->SetTestResult(site, 0, vbat_fb[site]);
    }
    return 0;
}


// =====================================================================
// TM424: VREF_TRIM — 内部基准电压 (VREF) (MV VREF≈1.68V (bench 1.669V))
// 依据: reg_config/tm424.sv (verbatim I2C/field 注释)
// ⚠Trim=Y (TRIM_BG): DALI 无 .treg, 暂测默认值, Trim execute 待 treg
// =====================================================================
DUT_API int TM424_VREF_TRIM(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VREF_TRIM = StsGetParam(funcindex, "VREF_TRIM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double vref_trim[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // VBAT → VBAT_PD3_FXVI (S3_5): K8 默认NC直连; +K13_VBAT_Cap
    // VDM/ATEST0 → VDM_SDA_ACM (S5_7): K59 默认NC=VDM直连 (ATEST0 pad 复用 VDM)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] → VBAT=4V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
        I2CWriteSameData(DEV_ADDR, 0x57, 0x02);  // Write reg 0x57 = 2
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x13);  // Write reg 0x5E = 19
    // field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,19)] → VREF_TRIM 路由到 ATEST0 (Trim ⚠)

    // ====== Step 4: Measure (V(ATEST0), MV) ======
    // vset[vbat,4.4,100e-6,0] → VBAT=4.4V (VREF 测量供电)
    VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(2);  // delay[2e-3]
    // VDM 高阻 FI=0 测 ATEST0 电压 (10V量程, 10UA最小电流档)
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        vref_trim[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
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
        VREF_TRIM->SetTestResult(site, 0, vref_trim[site]);
    }
    return 0;
}


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
