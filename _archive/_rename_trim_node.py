# -*- coding: utf-8 -*-
# 全局规则: TRIM_NODE 变量名 = trim 参数名大写 (PARAM_NODE -> OSC_64K/OSC_4P5M/IZTC_RES/BG_RES_DIV/BANDGAP)
# 字节模式 open('wb') 保留 BOM+CRLF (DLP 铁律)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\PROJECT6-DALI\devel\source\test.cpp'
with open(p, 'rb') as f:
    raw = f.read()
bom = raw[:3] == b'\xef\xbb\xbf'
text = raw.decode('utf-8-sig')

pairs = [
    ('TRIM_NODE &PARAM_NODE = trim_reg.trim("iztc_res");',
     'TRIM_NODE &IZTC_RES = trim_reg.trim("iztc_res");'),
    ('PARAM_NODE.execute(measure_iztc_res, spec, funcindex, funclabel, 1, 0, 0, 0);',
     'IZTC_RES.execute(measure_iztc_res, spec, funcindex, funclabel, 1, 0, 0, 0);'),
    ('TRIM_NODE &PARAM_NODE = trim_reg.trim("bg_res_div");',
     'TRIM_NODE &BG_RES_DIV = trim_reg.trim("bg_res_div");'),
    ('PARAM_NODE.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 0, 0);',
     'BG_RES_DIV.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 0, 0);'),
    ('TRIM_NODE &PARAM_NODE = trim_reg.trim("bandgap");',
     'TRIM_NODE &BANDGAP = trim_reg.trim("bandgap");'),
    ('PARAM_NODE.execute(measure_bandgap, spec, funcindex, funclabel, 1, 0, 0, 0);',
     'BANDGAP.execute(measure_bandgap, spec, funcindex, funclabel, 1, 0, 0, 0);'),
    ('TRIM_NODE &PARAM_NODE = trim_reg.trim("osc_64k");',
     'TRIM_NODE &OSC_64K = trim_reg.trim("osc_64k");'),
    ('PARAM_NODE.execute(measure_osc_64k, spec, funcindex, funclabel, 1, 0, 0, 0);',
     'OSC_64K.execute(measure_osc_64k, spec, funcindex, funclabel, 1, 0, 0, 0);'),
    ('TRIM_NODE &PARAM_NODE = trim_reg.trim("osc_4p5m");',
     'TRIM_NODE &OSC_4P5M = trim_reg.trim("osc_4p5m");'),
    ('PARAM_NODE.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 0, 0);',
     'OSC_4P5M.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 0, 0);'),
]

for old, new in pairs:
    c = text.count(old)
    assert c == 1, f'count={c}: {old}'
    text = text.replace(old, new)

with open(p, 'wb') as f:
    f.write('\ufeff'.encode('utf-8') + text.encode('utf-8'))
print('test.cpp 重命名完成: 10 处 PARAM_NODE -> 大写 trim 名')
print('残留 PARAM_NODE 检查:', text.count('PARAM_NODE'))
print('新变量确认: OSC_64K.execute =', 'OSC_64K.execute(' in text,
      '| OSC_4P5M.execute =', 'OSC_4P5M.execute(' in text,
      '| IZTC_RES =', 'TRIM_NODE &IZTC_RES' in text,
      '| BG_RES_DIV =', 'TRIM_NODE &BG_RES_DIV' in text,
      '| BANDGAP =', 'TRIM_NODE &BANDGAP' in text)
