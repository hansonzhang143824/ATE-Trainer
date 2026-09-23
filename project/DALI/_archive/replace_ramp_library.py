# -*- coding: utf-8 -*-
# 将 TM105-112 的手动 for 循环 ramp 扫描替换为 test_method.rampv_capv 库函数调用
# 保留 UTF-8 BOM + CRLF。扫描源表、继电器设置、功率段均不改动。
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\PROJECT6-DALI\devel\source\test.cpp'

# (func子串, 扫描源, ramp_vrng, ramp_irng, start, stop, samples, 结果变量)
TMS = [
    ('TM105_HSKP_VSPRE_MAX_CMP', 'VAC123_AMUX_ACM', 'ACM200_20V', 'ACM200_100MA', '0.0', '10.0', '21', 'vspre_max_cmp'),
    ('TM106_HSKP_VBUS_PRST',     'VBUS_DRVH1_ACM',  'ACM200_10V', 'ACM200_100MA', '3.0', '5.0', '21', 'vbus_prst'),
    ('TM107_HSKP_VBUS_HT_VBAT',  'VBUS_DRVH1_ACM',  'ACM200_10V', 'ACM200_100MA', '2.0', '5.0', '31', 'vbus_ht_vbat'),
    ('TM108_HSKP_VAC1_PRST',     'VAC123_AMUX_ACM', 'ACM200_20V', 'ACM200_100MA', '0.0', '10.0', '21', 'vac1_prst'),
    ('TM109_HSKP_VAC2_PRST',     'VAC123_AMUX_ACM', 'ACM200_20V', 'ACM200_100MA', '0.0', '10.0', '21', 'vac2_prst'),
    ('TM110_HSKP_VAC3_PRST',     'VAC123_AMUX_ACM', 'ACM200_20V', 'ACM200_100MA', '0.0', '10.0', '21', 'vac3_prst'),
    ('TM111_HSKP_VBAT_UV',       'VBAT_PD3_FXVI',   'FXVIe_PLUS_10V', 'FXVIe_PLUS_100MA', '0.0', '5.0', '51', 'vbat_uv'),
    ('TM112_HSKP_VBAT_HT_3P1V',  'VBAT_PD3_FXVI',   'FXVIe_PLUS_10V', 'FXVIe_PLUS_100MA', '0.0', '4.0', '41', 'vbat_ht_3p1v'),
]


def new_measure(src, vrng, irng, start, stop, samples, var):
    return (
        '    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======\n'
        '    // nQON high-Z reads DTEST0 logic level; ramp the scan source linearly and\n'
        '    // capture the source voltage at the instant V(nQON) crosses the 1.0V threshold\n'
        '    double vth_r[SITE_NUM] = { 0 };    // rising toggle threshold\n'
        '    double vth_f[SITE_NUM] = { 0 };    // falling toggle threshold\n'
        '    // rising ramp: trigger cap V rising through 1.0V -> toggle on rising edge\n'
        '    test_method.rampv_capv(' + src + ', ' + vrng + ', ' + irng + ',\n'
        '                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,\n'
        '                           ' + start + ', ' + stop + ', ' + samples + ', 100, 1.0, TRIG_RISING, vth_r);\n'
        '    // falling ramp: trigger cap V falling through 1.0V -> toggle on falling edge\n'
        '    test_method.rampv_capv(' + src + ', ' + vrng + ', ' + irng + ',\n'
        '                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,\n'
        '                           ' + stop + ', ' + start + ', ' + samples + ', 100, 1.0, TRIG_FALLING, vth_f);\n'
        '    FOR_EACH_VALID_SITE(site)\n'
        '    {\n'
        '        ' + var + '[site] = vth_r[site];\n'
        '    }\n'
    )


with open(path, 'r', encoding='utf-8-sig') as f:
    data = f.read()

total = 0
for func, src, vrng, irng, start, stop, samples, var in TMS:
    # 定位函数块: 从 DUT_API int TMxxx( 到下一个 DUT_API int 或文件末尾
    sig = 'DUT_API int %s(' % func
    f_start = data.find(sig)
    if f_start < 0:
        print('!! NOT FOUND: %s' % func)
        continue
    f_end = data.find('DUT_API int ', f_start + len(sig))
    if f_end < 0:
        f_end = len(data)
    block = data[f_start:f_end]

    # 块内找 Step 4 / Step 5 标记
    s4 = block.find('// ====== Step 4: Measure')
    s5 = block.find('// ====== Step 5: Power Off')
    if s4 < 0 or s5 < 0 or s5 <= s4:
        print('!! Step4/Step5 markers not found in %s (s4=%d s5=%d)' % (func, s4, s5))
        continue

    old = block[s4:s5]
    new = new_measure(src, vrng, irng, start, stop, samples, var)
    if 'for (double v' not in old:
        print('!! Step4 section has no manual ramp loop in %s — skipping' % func)
        continue
    data = data[:f_start + s4] + new + data[f_start + s5:]
    total += 1
    print('OK  %s : replaced Step4 (manual loop -> rampv_capv, %s %s->%s %spts)' % (func, src, start, stop, samples))

if total == len(TMS):
    with open(path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(data)
    print('\nAll %d functions replaced. Total lines: %d' % (total, data.count('\n')))
else:
    print('\n!! %d/%d replaced — NOT writing to disk' % (total, len(TMS)))
