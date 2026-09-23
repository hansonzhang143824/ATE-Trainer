# -*- coding: utf-8 -*-
"""
TM403-425 代码生成与插入 (15 测试函数 + 3 measure 函数)
- test.cpp: UTF-8-BOM + CRLF (DLP)
- sub.cpp:  GBK (DLP)
模板驱动, 全部函数遵循 nuvolta-codegen 规则.
"""
import io, sys, re

TEST_CPP = r'D:\PROJECT6-DALI\devel\source\test.cpp'
SUB_CPP  = r'D:\PROJECT6-DALI\devel\source\sub.cpp'

# =====================================================================
# Toggle 模板 (参考 TM111/TM112/TM400: rising→TRIG_FALLING, falling→TRIG_RISING)
# =====================================================================
TOGGLE_TPL = '''// =====================================================================
// __TM__: __NAME__ — __DESC__
// DFT: __DFT__
// 期望: __EXPECT__
// Loop: __LOOP__
// =====================================================================
DUT_API int __TMID__(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *__NAME___Rise = StsGetParam(funcindex, "__NAME___Rise");
    CParam *__NAME___Fall = StsGetParam(funcindex, "__NAME___Fall");
    CParam *__NAME___Hys = StsGetParam(funcindex, "__NAME___Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
__CONNECT_COMMENTS__
    cbite.SetOn(__CONNECT_RELAYS__);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // __SUPPLY_COMMENT__
    __SUPPLY_SET__
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // __REG_COMMENT__
    entertestmode();
__REG_WRITES__
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // nQON high-Z reads DTEST0 logic level; __RAMP_COMMENT__
    // __RAMP_RANGE_COMMENT__
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(__RAMP_SRC__, __RAMP_VRNG__, __RAMP_IRNG__,
                           NQON_HG1_ACM, __CAP_VRNG__, __CAP_IRNG__,
                           __LO__, __HI__, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(__RAMP_SRC__, __RAMP_VRNG__, __RAMP_IRNG__,
                           NQON_HG1_ACM, __CAP_VRNG__, __CAP_IRNG__,
                           __HI__, __LO__, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV)
    }

    // ====== Step 5: Power Off (三步下电) ======
__POFF1__
    delay_ms(1);
__POFF2__

    // ====== Step 6: LogData (测试结果) ======
    FOR_EACH_VALID_SITE(site)
    {
        __NAME___Rise->SetTestResult(site, 0, rise_result[site]);
        __NAME___Fall->SetTestResult(site, 0, fall_result[site]);
        __NAME___Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}'''

TOGGLES = [
    dict(tm='TM403', name='VBUS_REVI_VTH',
         desc='VBUS-VBAT 反向比较阈值 (Toggle, VBUS ramp)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] '
             '-> 0x10=0x43, 0x56=0x1E, 0x57=0x08 -> VBUS 3.7->4.5->3.7 ramp, 捕 DTEST0 翻转',
         expect='falling -0.120V / rising 0V (r -0.016 / f -0.138)',
         loop='VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC (VBUS 为被测 ramp 源, 不闭 K5_VBUS_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vbat,4,100e-6,0] -> VBAT=4V FV',
         supply_set='VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
         reg_comment='field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] -> 0x10=0x43, 0x56=0x1E, 0x57=0x08',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1E);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBUS 3.7->4.5->3.7 ramp',
         ramp_range_comment='VBUS 量程: 4.5V×2=9 <= 10V 档 table_max 5.0 -> ACM200_10V (R-RNG)',
         ramp_src='VBUS_DRVH1_ACM', ramp_vrng='ACM200_10V', ramp_irng='ACM200_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='3.7', hi='4.5',
         poff1='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM406', name='VBAT_LOW_VTH',
         desc='boost mode VBAT 低压阈值 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(BUBO_MODE,1),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,26)] '
             '-> 0x09=0x0A, 0x10=0x43, 0x56=0x1A, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='rising 2.7V / falling 2.5V (r 2.686 / f 2.491)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(BUBO_MODE,1)] -> 0x09=0x0A; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,26)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM408', name='VBAT_OVP',
         desc='buck mode VBAT OVP 阈值 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,28),(VBAT_CV,9)] '
             '-> 0x10=0x43, 0x56=0x1C, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='rising 104%*VBAT_CV / hys 2% (r 4.231 / f 4.158, VBAT_CV=4.2)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,28),(VBAT_CV,9)] -> 0x10=0x43, 0x56=0x1C, 0x57=0x08',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1C);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM409', name='VBUS_HT_4P8V',
         desc='boost mode VBUS 4.8V 比较阈值 (Toggle, VBUS ramp)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> field[(BUBO_MODE,1),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,31)] '
             '-> 0x09=0x0A, 0x10=0x43, 0x56=0x1F, 0x57=0x08 -> VBUS 4->7->4 ramp, 捕 DTEST0 翻转',
         expect='rising 4.8V (r 4.661 / f 4.562)',
         loop='VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC (VBUS 为被测 ramp 源, 不闭 K5_VBUS_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vbat,4,100e-6,0] -> VBAT=4V FV',
         supply_set='VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
         reg_comment='field[(BUBO_MODE,1)] -> 0x09=0x0A; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,31)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x09, 0x0A);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1F);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBUS 4->7->4 ramp',
         ramp_range_comment='VBUS 量程: 7V×2=14 > 10V 档 table_max 5.0 -> ACM200_40V (R-RNG)',
         ramp_src='VBUS_DRVH1_ACM', ramp_vrng='ACM200_40V', ramp_irng='ACM200_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='4.0', hi='7.0',
         poff1='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM410', name='VTRIKLE_VTH1',
         desc='buck mode VBAT 涓流充电阈值 1 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(VTRICKLE,0),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] '
             '-> 0x0A=0x09, 0x10=0x43, 0x56=0x1D, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='rising 2.7 / hys 0.3 (r 2.687 / f 2.393)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(VTRICKLE,0)] -> 0x0A=0x09; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,29)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x0A, 0x09);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM411', name='VTRIKLE_VTH2',
         desc='buck mode VBAT 涓流充电阈值 2 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(VTRICKLE,1),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,29),(BUBO_MODE,0)] '
             '-> 0x10=0x43, 0x56=0x1D, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='rising 3 / hys 0.3 (r 2.983 / f 2.690)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(VTRICKLE,1)] 默认值不写 0x0A; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,29)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1D);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM412', name='VRE_CHG_VTH1',
         desc='buck mode VBAT 再充电阈值 1 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(VRE_CHG,0),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] '
             '-> 0x10=0x43, 0x56=0x1B, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='VBAT_CV-0.1 / hys 0.05 (r 3.979 / f 4.030, VBAT_CV=4.1)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(VRE_CHG,0)] 默认值不写 0x0A; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,27)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM413', name='VRE_CHG_VTH2',
         desc='buck mode VBAT 再充电阈值 2 (Toggle, VBAT ramp)',
         dft='vset[vac1,5,100e-6,0] -> en_tm[] -> field[(VRE_CHG,1),(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,27),(BUBO_MODE,0)] '
             '-> 0x0A=0x69, 0x10=0x43, 0x56=0x1B, 0x57=0x08 -> VBAT 0->5->0 ramp, 捕 DTEST0 翻转',
         expect='VBAT_CV-0.2 / hys 0.05 (r 3.882 / f 3.929, VBAT_CV=4.1)',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + NQON_HG1_ACM',
         connect_comments='''    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC + K21_VAC_Cap 供电稳定
    // VBAT -> VBAT_PD3_FXVI: K8 default NC (VBAT 为被测 ramp 源, 不闭 K13_VBAT_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up''',
         connect_relays='K21_VAC_Cap, K65_nQON_PU, -1',
         supply_comment='vset[vac1,5,100e-6,0] -> VAC1=5V FV',
         supply_set='VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
         reg_comment='field[(VRE_CHG,1)] -> 0x0A=0x69; field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,27)] -> 0x10, 0x56, 0x57',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x0A, 0x69);
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1B);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);''',
         ramp_comment='VBAT 0->5->0 ramp (双向)',
         ramp_range_comment='VBAT 量程: 5V×2=10 -> FXVIe_PLUS_10V (R-RNG)',
         ramp_src='VBAT_PD3_FXVI', ramp_vrng='FXVIe_PLUS_10V', ramp_irng='FXVIe_PLUS_100MA',
         cap_vrng='ACM200_10V', cap_irng='ACM200_10UA',
         lo='0.0', hi='5.0',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),
]


# =====================================================================
# FB 模板 (参考 TM100 VDM MV + TM124 多源供电)
# =====================================================================
FB_TPL = '''// =====================================================================
// __TM__: __NAME__ — __DESC__
// DFT: __DFT__
// 期望: __EXPECT__
// Loop: __LOOP__
// =====================================================================
DUT_API int __TMID__(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *__NAME__ = StsGetParam(funcindex, "__NAME__");
    //}}AFX_STS_PARAM_PROTOTYPES

    double __VARNAME__[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
__CONNECT_COMMENTS__
    cbite.SetOn(__CONNECT_RELAYS__);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
__SUPPLY_SETS__
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // __REG_COMMENT__
    entertestmode();
__REG_WRITES__
    delay_ms(2);

    // ====== Step 4: Measure (VDM 高阻 MV 测 ATEST0 = channel voutp) ======
    // VDM_SDA_ACM.Set(FI, 0, 10V, 10UA) 高阻: DUT ATEST0 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VDM_SDA_ACM.MeasureVI(50, 5);
    FOR_EACH_VALID_SITE(site)
    {
        __VARNAME__[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET);
    }

    // ====== Step 5: Power Off (三步下电) ======
__POFF1__
    delay_ms(1);
__POFF2__

    // ====== Step 6: LogData (测试结果) ======
    FOR_EACH_VALID_SITE(site)
    {
        __NAME__->SetTestResult(site, 0, __VARNAME__[site]);
    }
    return 0;
}'''

FBS = [
    dict(tm='TM418', name='VAC1_FB', var='vac1_fb',
         desc='VAC1 反馈电压 (FB, ATEST0 MV via VDM)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x11=0x11, 0x57=0x02, 0x5E=0x1F '
             '(ATEST0_MUX=31=channel voutp) -> vset[vac1,5,1e-3,0], 测 V(ATEST0)=VAC1/10',
         expect='VAC1/10 = 0.5V',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + VDM_SDA_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC1 -> VAC123_AMUX_ACM: K18/K19 default NC (VAC1 通路)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap + K21_VAC_Cap: VBAT/VAC1 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K21_VAC_Cap, -1',
         supply_sets='''    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; vset[vac1,5,1e-3,0] -> VAC1=5V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);''',
         reg_comment='0x10=0x43(WAKE_UP); 0x11=0x11(AMUX 通道=VAC1); 0x57=0x02(EN_ATEST0); 0x5E=0x1F(ATEST0_MUX=31=channel voutp)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x11, 0x11);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);''',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM419', name='VAC2_FB', var='vac2_fb',
         desc='VAC2 反馈电压 (FB, ATEST0 MV via VDM)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x11=0x12, 0x57=0x02, 0x5E=0x1F '
             '(ATEST0_MUX=31=channel voutp) -> vset[vac2,10,1e-3,0], 测 V(ATEST0)=VAC2/10',
         expect='VAC2/10 = 1.0V',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + VDM_SDA_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC2 -> VAC123_AMUX_ACM: K19_ACM0_VAC2 (VAC2 通路继电器)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap + K21_VAC_Cap: VBAT/VAC2 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K21_VAC_Cap, K19_ACM0_VAC2, -1',
         supply_sets='''    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; vset[vac2,10,1e-3,0] -> VAC2=10V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);''',
         reg_comment='0x10=0x43(WAKE_UP); 0x11=0x12(AMUX 通道=VAC2); 0x57=0x02(EN_ATEST0); 0x5E=0x1F(ATEST0_MUX=31=channel voutp)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x11, 0x12);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);''',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM420', name='VAC3_FB', var='vac3_fb',
         desc='VAC3 反馈电压 (FB, ATEST0 MV via VDM)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x11=0x13, 0x57=0x02, 0x5E=0x1F '
             '(ATEST0_MUX=31=channel voutp) -> vset[vac3,15,1e-3,0], 测 V(ATEST0)=VAC3/10',
         expect='VAC3/10 = 1.5V',
         loop='VBAT_PD3_FXVI + VAC123_AMUX_ACM + VDM_SDA_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VAC3 -> VAC123_AMUX_ACM: K18_ACM0_VAC3 (VAC3 通路继电器)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap + K21_VAC_Cap: VBAT/VAC3 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K21_VAC_Cap, K18_ACM0_VAC3, -1',
         supply_sets='''    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; vset[vac3,15,1e-3,0] -> VAC3=15V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);''',
         reg_comment='0x10=0x43(WAKE_UP); 0x11=0x13(AMUX 通道=VAC3); 0x57=0x02(EN_ATEST0); 0x5E=0x1F(ATEST0_MUX=31=channel voutp)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x11, 0x13);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);''',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM421', name='VBUS_FB', var='vbus_fb',
         desc='VBUS 反馈电压 (FB, ATEST0 MV via VDM)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x11=0x14, 0x57=0x02, 0x5E=0x1F '
             '(ATEST0_MUX=31=channel voutp) -> vset[vbus,4,1e-3,1] -> vset[vbus,10,1e-3,1], 测 V(ATEST0)=VBUS/10',
         expect='VBUS/10 = 1.0V',
         loop='VBAT_PD3_FXVI + VBUS_DRVH1_ACM + VDM_SDA_ACM',
         connect_comments='''    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC (VBUS 静态供电, 测 ATEST0 不流经其 Cap)
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap + K5_VBUS_Cap: VBAT/VBUS 静态供电稳定 (FR-001: 供电→闭)''',
         connect_relays='K13_VBAT_Cap, K5_VBUS_Cap, -1',
         supply_sets='''    // vset[vbat,4,100e-6,0] -> VBAT=4V FV; vset[vbus,4,1e-3,1] -> vset[vbus,10,1e-3,1] -> VBUS=10V
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VBUS_DRVH1_ACM.Set(FV, 4, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);''',
         reg_comment='0x10=0x43(WAKE_UP); 0x11=0x14(AMUX 通道=VBUS); 0x57=0x02(EN_ATEST0); 0x5E=0x1F(ATEST0_MUX=31=channel voutp)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x11, 0x14);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x1F);''',
         poff1='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),
]


# =====================================================================
# Trim 模板 (参考 TM301/Trim_VBG: VDM 高阻 → execute)
# =====================================================================
def gen_trim_step_params(prefix, nsteps):
    lines = []
    for i in range(nsteps):
        lines.append('    CParam *%s_step%d = StsGetParam(funcindex, "%s_step%d");' % (prefix, i, prefix, i))
    for suf in ['pre_value', 'pre_bit', 'post_bit', 'updated', 'guessed', 'target', 'post_value', 'post_rt']:
        lines.append('    CParam *%s_%s = StsGetParam(funcindex, "%s_%s");' % (prefix, suf, prefix, suf))
    return '\n'.join(lines)

TRIM_TPL = '''// =====================================================================
// __TM__: __NAME__ — __DESC__
// DFT: __DFT__
// 期望: __EXPECT__
// Loop: __LOOP__
// =====================================================================
DUT_API int __TMID__(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
__STEP_PARAMS__
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &__KEY__ = trim_reg.trim("__KEYL__");

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VDM  -> VDM_SDA_ACM: K59 default NC=VDM
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // __PON1_COMMENT__
    __PON1_SET__
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // __REG_COMMENT__
    entertestmode();
__REG_WRITES__
    delay_ms(2);

    // ====== Step 4: Trim execute (measure 写 EFUSE + VDM MV) ======
__PON2_BLOCK__
    // VDM_SDA_ACM.Set(FI, 0, 10V, 10UA) 高阻: DUT ATEST 输出驱动 VDM pad
    VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    __KEY__.execute(__MEASURE__, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    __POFF1__
    delay_ms(1);
    __POFF2__

    return 0;
}'''

TRIMS = [
    dict(tm='TM422', name='VBAT_FB', key='MNT_VBAT_RSNS_LOOP', keyl='mnt_vbat_rsns_loop',
         desc='VBAT 反馈电压 trim (Trim, mnt_vbat_rsns_loop)',
         dft='vset[vbat,4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x57=0x02, 0x5E=0x17 (ATEST0_MUX=23=FB_VBAT) '
             '-> vset[vbat,5,100e-6,0]; mnt_vbat_rsns_loop 16步(EFUSE F7 bits1-4), target=0 (FB 偏差)',
         expect='V(FB_VBAT)=VBAT*2/5=2V, trim 使偏差→0',
         loop='VBAT_PD3_FXVI + VDM_SDA_ACM',
         nsteps=16, measure='measure_mnt_vbat_rsns_loop',
         pon1_comment='vset[vbat,4,100e-6,0] -> VBAT=4V FV (配置寄存器前)',
         pon1_set='VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
         reg_comment='0x10=0x43(WAKE_UP); 0x57=0x02(EN_ATEST0); 0x5E=0x17(ATEST0_MUX=23=FB_VBAT)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x17);''',
         pon2_block='''    // vset[vbat,5,100e-6,0] -> VBAT=5V (测量条件)
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);''',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM424', name='VREF_TRIM', key='MNT_DAC_BUF_OS', keyl='mnt_dac_buf_os',
         desc='LDO 参考电压 trim (Trim, mnt_dac_buf_os)',
         dft='vset[vbat,4.4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x57=0x02, 0x5E=0x13 (ATEST0_MUX=19=VREF_1P68V) '
             '-> mnt_dac_buf_os 32步(EFUSE F7 bits5-7+F8 bits0-1), target=1680mV',
         expect='V(VREF_1P68V) trim 到 1.68V',
         loop='VBAT_PD3_FXVI + VDM_SDA_ACM',
         nsteps=32, measure='measure_mnt_dac_buf_os',
         pon1_comment='vset[vbat,4.4,100e-6,0] -> VBAT=4.4V FV',
         pon1_set='VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
         reg_comment='0x10=0x43(WAKE_UP); 0x57=0x02(EN_ATEST0); 0x5E=0x13(ATEST0_MUX=19=VREF_1P68V)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
    I2CWriteSameData(DEV_ADDR, 0x5E, 0x13);''',
         pon2_block='',   # VBAT 已在最终 4.4V, 无二次设置
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),

    dict(tm='TM425', name='VREF_1P2V_BUF', key='MNT_V1P2_BUF', keyl='mnt_v1p2_buf',
         desc='内部 1.2V 参考电压 trim (Trim, mnt_v1p2_buf)',
         dft='vset[vbat,4.4,100e-6,0] -> en_tm[] -> 0x10=0x43, 0x57=0x04(EN_ATEST1), 0x58=0x02(ATEST1_MUX=2=VREF_1P2V_BUF) '
             '-> mnt_v1p2_buf 16步(EFUSE F6 bits5-7+F7 bit0), target=1200mV',
         expect='V(VREF_1P2V_BUF) trim 到 1.2V',
         loop='VBAT_PD3_FXVI + VDM_SDA_ACM',
         nsteps=16, measure='measure_mnt_v1p2_buf',
         pon1_comment='vset[vbat,4.4,100e-6,0] -> VBAT=4.4V FV',
         pon1_set='VBAT_PD3_FXVI.Set(FV, 4.4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
         reg_comment='0x10=0x43(WAKE_UP); 0x57=0x04(EN_ATEST1); 0x58=0x02(ATEST1_MUX=2=VREF_1P2V_BUF)',
         reg_writes='''    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x04);
    I2CWriteSameData(DEV_ADDR, 0x58, 0x02);''',
         pon2_block='',
         poff1='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);''',
         poff2='''    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'''),
]


# =====================================================================
# measure 函数模板 (sub.cpp, DALI 风格参照 measure_bandgap)
# =====================================================================
MEASURE_TPL = '''// ===================================================================
// DALI: __NAME__ — __TM__ __TITLE__ 测量 (VDM MV, 返回 mV)
// treg: __KEYL__, __STEPS__步(Table 0-__LAST__)
// 测量: VDM_SDA_ACM MV (调用方已置 FI=0 高阻), __RETCOMMENT__
// 寄存器由 test.cpp 已配置: __REG__
// ===================================================================
void __NAME__(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
__DECL__
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
__WORKVALS__
        }

        // 写入 EFUSE trim 值
__I2CWRITES__
        delay_ms(2);

        // VDM_SDA_ACM MV测量 (FI=0 高阻, 量程10UA)
        VDM_SDA_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = __RESULT__;
        }
    }
}'''

MEASURES = [
    dict(name='measure_mnt_vbat_rsns_loop', tm='TM422', title='VBAT_FB',
         keyl='mnt_vbat_rsns_loop', steps='16', last='15',
         retcomment='(V(FB_VBAT)-2.0)*1e3 mV 偏差 (VBAT=5V, FB=VBAT*2/5=2V, target=0)',
         reg='0x10=0x43, 0x57=0x02, 0x5E=0x17 (ATEST0_MUX=23=FB_VBAT)',
         decl='''    DWORD working_value1[SITE_NUM] = { 0 };''',
         workvals='''            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);''',
         i2cwrites='''        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);''',
         result='(VDM_SDA_ACM.GetMeasResult(site, MVRET) - 2.0) * 1e3;  // V → mV (FB_VBAT 偏差)'),

    dict(name='measure_mnt_dac_buf_os', tm='TM424', title='VREF_TRIM',
         keyl='mnt_dac_buf_os', steps='32', last='31',
         retcomment='MVRET*1e3 mV (target=1680mV)',
         reg='0x10=0x43, 0x57=0x02, 0x5E=0x13 (ATEST0_MUX=19=VREF_1P68V)',
         decl='''    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };''',
         workvals='''            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);''',
         i2cwrites='''        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, working_value2);''',
         result='VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V → mV'),

    dict(name='measure_mnt_v1p2_buf', tm='TM425', title='VREF_1P2V_BUF',
         keyl='mnt_v1p2_buf', steps='16', last='15',
         retcomment='MVRET*1e3 mV (target=1200mV)',
         reg='0x10=0x43, 0x57=0x04, 0x58=0x02 (ATEST1_MUX=2=VREF_1P2V_BUF)',
         decl='''    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };''',
         workvals='''            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F6").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);''',
         i2cwrites='''        dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value2);''',
         result='VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V → mV'),
]


# =====================================================================
# 生成
# =====================================================================
def fill(tpl, data):
    """按占位符长度降序替换, 避免前缀碰撞 (如 __CONNECT_COMMENTS__ vs __CONNECT__)."""
    mapping = dict(('__%s__' % k.upper(), str(v)) for k, v in data.items())
    for key in sorted(mapping, key=len, reverse=True):
        tpl = tpl.replace(key, mapping[key])
    return tpl

def gen_toggle(t):
    d = dict(t)
    d['TMID'] = t['tm'] + '_' + t['name']
    return fill(TOGGLE_TPL, d)

def gen_fb(t):
    d = dict(t)
    d['TMID'] = t['tm'] + '_' + t['name']
    d['VARNAME'] = t['var']
    return fill(FB_TPL, d)

def gen_trim(t):
    d = dict(t)
    d['TMID'] = t['tm'] + '_' + t['name']
    d['STEP_PARAMS'] = gen_trim_step_params(t['key'], t['nsteps'])
    return fill(TRIM_TPL, d)

def gen_measure(m):
    return fill(MEASURE_TPL, m)

def build_test_funcs():
    parts = []
    for t in TOGGLES:
        parts.append(gen_toggle(t))
    for t in FBS:
        parts.append(gen_fb(t))
    for t in TRIMS:
        parts.append(gen_trim(t))
    return '\n\n'.join(parts)

def build_sub_funcs():
    parts = []
    for m in MEASURES:
        parts.append(gen_measure(m))
    return '\n\n'.join(parts)


# =====================================================================
# 插入 (保持编码)
# =====================================================================
def read_text(path, enc):
    raw = open(path, 'rb').read()
    return raw.decode(enc, errors='replace')

def write_text(path, text, enc, add_bom_utf8=False):
    data = text.encode(enc)
    if add_bom_utf8:
        if not data.startswith(b'\xef\xbb\xbf'):
            data = b'\xef\xbb\xbf' + data
    open(path, 'wb').write(data)

def norm_crlf(text):
    # 统一 \r\n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.replace('\n', '\r\n')

def main():
    # ---- test.cpp: UTF-8-BOM + CRLF ----
    t = read_text(TEST_CPP, 'utf-8-sig')
    t = norm_crlf(t)
    new_t = norm_crlf(build_test_funcs())
    # 追加到文件末尾 (TM402 后)
    t = t.rstrip() + '\r\n' + new_t + '\r\n'
    write_text(TEST_CPP, t, 'utf-8', add_bom_utf8=True)
    print('test.cpp: +15 函数, %d 字节' % len(t.encode('utf-8')))

    # ---- sub.cpp: GBK ----
    s = read_text(SUB_CPP, 'gbk')
    s = norm_crlf(s)
    new_s = norm_crlf(build_sub_funcs())
    # 在 measure_osc_64k 函数之后插入
    start = s.find('void measure_osc_64k')
    assert start >= 0, 'measure_osc_64k 未找到'
    m = re.search(r'\r\n\}(?:\r\n|\Z)', s[start:])
    assert m, 'measure_osc_64k 结束未找到'
    insert_at = start + m.end()
    s = s[:insert_at] + new_s + '\r\n' + s[insert_at:]
    write_text(SUB_CPP, s, 'gbk')
    print('sub.cpp: +3 measure 函数, %d 字节' % len(s.encode('gbk')))

if __name__ == '__main__':
    main()
