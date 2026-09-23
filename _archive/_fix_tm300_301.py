# -*- coding: utf-8 -*-
# 重写 TM300/301 为 trim 框架 (test.cpp 字节模式, DLP BOM+CRLF 保留)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

tm300 = r"""// =====================================================================
// TM300: OSC_64K — OSC64K 输出频率 Trim (Trim, QTMU 测频, KHz)
// DFT: vset[vbat,4] → en_tm[] → 0x56=0x0C, 0x57=0x08 (DMUX_EN=1, DMUX_SEL=12)
//      Trim='Y', field[(D2A_TRIM_OSC_64K,2)] → 无条件走 trim 框架
// treg key: osc_64k (8步, D2A_OSC_64K_TRIM 3bit/TRIM1)
// ⚠ 数据缺口 (已报告): ① treg 无 [osc_64k] 段 ② reg_config 写 0xF2=0x04
//   但 TRIM_REG byte map 0xF2 = Trim_OSC_4P5M[3:3](bit0)+Trim_IBUS_SNS_EA_OS[0:3](bits7-4),
//   bit2 无字段定义 → 写入对不上 ③ D2A_TRIM_OSC_64K(reg_config) vs D2A_OSC_64K_TRIM(TRIM_REG) 命名不一致
//   暂按 reg_config 0xF2 实现 (待用户确认)
// =====================================================================
DUT_API int TM300_OSC_64K(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_64K_step0 = StsGetParam(funcindex, "OSC_64K_step0");
    CParam *OSC_64K_step1 = StsGetParam(funcindex, "OSC_64K_step1");
    CParam *OSC_64K_step2 = StsGetParam(funcindex, "OSC_64K_step2");
    CParam *OSC_64K_step3 = StsGetParam(funcindex, "OSC_64K_step3");
    CParam *OSC_64K_step4 = StsGetParam(funcindex, "OSC_64K_step4");
    CParam *OSC_64K_step5 = StsGetParam(funcindex, "OSC_64K_step5");
    CParam *OSC_64K_step6 = StsGetParam(funcindex, "OSC_64K_step6");
    CParam *OSC_64K_step7 = StsGetParam(funcindex, "OSC_64K_step7");
    CParam *OSC_64K_pre_value = StsGetParam(funcindex, "OSC_64K_pre_value");
    CParam *OSC_64K_pre_bit = StsGetParam(funcindex, "OSC_64K_pre_bit");
    CParam *OSC_64K_post_bit = StsGetParam(funcindex, "OSC_64K_post_bit");
    CParam *OSC_64K_updated = StsGetParam(funcindex, "OSC_64K_updated");
    CParam *OSC_64K_guessed = StsGetParam(funcindex, "OSC_64K_guessed");
    CParam *OSC_64K_target = StsGetParam(funcindex, "OSC_64K_target");
    CParam *OSC_64K_post_value = StsGetParam(funcindex, "OSC_64K_post_value");
    CParam *OSC_64K_post_rt = StsGetParam(funcindex, "OSC_64K_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &OSC_64K = trim_reg.trim("osc_64k");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> QTMU S10_CH0: K66_TMU_nQON (QTMU_GP.Connect 连接输入继电器)
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    // K65_nQON_PU: nQON high-Z 时上拉, QTMU 需完整数字摆幅
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (不含 CSpec) ======
    // field[(DMUX_EN,1),(DMUX_SEL,12)] -> 0x56=0x0C, 0x57=0x08; delay 1ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x56, 0x0C);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);

    // ====== Step 4: Trim execute (measure_osc_64k 写 0xF2 + QTMU 测频) ======
    // ⚠ treg 无 [osc_64k] 段, trim 参数/写入地址待用户确认
    OSC_64K.execute(measure_osc_64k, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    return 0;
}

// =====================================================================
// TM301: OSC_4P5M — OSC4P5M 输出频率 Trim (Trim, QTMU 测频, 重构 MHz)
// DFT: vset[vbat,5] → en_tm[] → 0x10=0x43 → 0x56=0x33, 0x57=0x08
//      (DMUX_EN=1, DMUX_SEL=51 路由 OSC4P5M/128 foldback) → 测 nQON 频率
//      Trim='Y', Notes=TRIM_OSC_4P5M → treg key "osc_4p5m" (DFT Notes 列权威)
// treg: osc_4p5m, 16步(Target=4.5MHz, Table 0-15, 0xF1 bits 7-5 + 0xF2 bit0)
// 测量: measure_osc_4p5m (写 F1/F2 → QTMU 测 foldback ~35KHz → ×0.128 重构 MHz)
// Loop: VBAT_PD3_FXVI + QTMU_GP (nQON 经 K66)
// =====================================================================
DUT_API int TM301_OSC_4P5M(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_4P5M_step0 = StsGetParam(funcindex, "OSC_4P5M_step0");
    CParam *OSC_4P5M_step1 = StsGetParam(funcindex, "OSC_4P5M_step1");
    CParam *OSC_4P5M_step2 = StsGetParam(funcindex, "OSC_4P5M_step2");
    CParam *OSC_4P5M_step3 = StsGetParam(funcindex, "OSC_4P5M_step3");
    CParam *OSC_4P5M_step4 = StsGetParam(funcindex, "OSC_4P5M_step4");
    CParam *OSC_4P5M_step5 = StsGetParam(funcindex, "OSC_4P5M_step5");
    CParam *OSC_4P5M_step6 = StsGetParam(funcindex, "OSC_4P5M_step6");
    CParam *OSC_4P5M_step7 = StsGetParam(funcindex, "OSC_4P5M_step7");
    CParam *OSC_4P5M_step8 = StsGetParam(funcindex, "OSC_4P5M_step8");
    CParam *OSC_4P5M_step9 = StsGetParam(funcindex, "OSC_4P5M_step9");
    CParam *OSC_4P5M_step10 = StsGetParam(funcindex, "OSC_4P5M_step10");
    CParam *OSC_4P5M_step11 = StsGetParam(funcindex, "OSC_4P5M_step11");
    CParam *OSC_4P5M_step12 = StsGetParam(funcindex, "OSC_4P5M_step12");
    CParam *OSC_4P5M_step13 = StsGetParam(funcindex, "OSC_4P5M_step13");
    CParam *OSC_4P5M_step14 = StsGetParam(funcindex, "OSC_4P5M_step14");
    CParam *OSC_4P5M_step15 = StsGetParam(funcindex, "OSC_4P5M_step15");
    CParam *OSC_4P5M_pre_value = StsGetParam(funcindex, "OSC_4P5M_pre_value");
    CParam *OSC_4P5M_pre_bit = StsGetParam(funcindex, "OSC_4P5M_pre_bit");
    CParam *OSC_4P5M_post_bit = StsGetParam(funcindex, "OSC_4P5M_post_bit");
    CParam *OSC_4P5M_updated = StsGetParam(funcindex, "OSC_4P5M_updated");
    CParam *OSC_4P5M_guessed = StsGetParam(funcindex, "OSC_4P5M_guessed");
    CParam *OSC_4P5M_target = StsGetParam(funcindex, "OSC_4P5M_target");
    CParam *OSC_4P5M_post_value = StsGetParam(funcindex, "OSC_4P5M_post_value");
    CParam *OSC_4P5M_post_rt = StsGetParam(funcindex, "OSC_4P5M_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &OSC_4P5M = trim_reg.trim("osc_4p5m");

    // ====== Step 1: Connect ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // nQON -> QTMU S10_CH0: K66_TMU_nQON (QTMU_GP.Connect 连接输入继电器)
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    // K65_nQON_PU: nQON high-Z 时上拉, QTMU 需完整数字摆幅
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K66_TMU_nQON, -1);
    delay_ms(3);

    // ====== Step 2: Power On ======
    // vset[vbat,5,100e-6,0] -> VBAT=5V FV
    VBAT_PD3_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (不含 CSpec) ======
    // field[(WAKE_UP,1)] -> 0x10=0x43
    // field[(DMUX_EN,1),(DMUX_SEL,51)] -> 0x56=0x33, 0x57=0x08; delay 1ms
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x33);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(1);

    // ====== Step 4: Trim execute (measure_osc_4p5m 写 F1/F2 + QTMU 测频) ======
    OSC_4P5M.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 0, 0);

    // ====== Step 5: Power Off (三步下电) ======
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);

    return 0;
}"""

p = r'D:\PROJECT6-DALI\devel\source\test.cpp'
with open(p, 'rb') as f:
    raw = f.read()
text = raw.decode('utf-8-sig')

sep = '// ====================================================================='
sig300 = text.find('DUT_API int TM300_OSC_64K')
start = text.rfind(sep, 0, sig300)
sig400 = text.find('DUT_API int TM400_VBUS_OVP_VTH1')
end = text.rfind(sep, 0, sig400)
if start < 0 or end < 0 or end <= start:
    print(f'ERROR locate: sig300={sig300} sig400={sig400} start={start} end={end}')
    sys.exit(1)

new_block = sep + '\r\n' + tm300.replace('\n', '\r\n')
new_text = text[:start] + new_block + text[end:]
with open(p, 'wb') as f:
    f.write('\ufeff'.encode('utf-8') + new_text.encode('utf-8'))
print(f'替换成功: 旧块 [{start},{end}) → 新块 [{start},{start+len(new_block)})')
with open(p, 'rb') as f:
    chk = f.read()
print('新文件大小:', len(raw), '->', len(chk))
print('BOM:', chk[:3] == b'\xef\xbb\xbf', '| CRLF:', chk.count(b'\r\n'),
      '| lone_CR:', chk.count(b'\r') - chk.count(b'\r\n'))
