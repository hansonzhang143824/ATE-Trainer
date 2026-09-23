# -*- coding: utf-8 -*-
# 从 test.cpp 提取新 TM300/301 (trim 框架) 同步到 gen_tm216_402.cpp
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

src = r'D:\PROJECT6-DALI\devel\source\test.cpp'
gen = r'D:\Newtest\CLAUDE_PROCESS\gen_tm216_402.cpp'

def read(p):
    with open(p, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk'):
        try:
            return raw.decode(enc), enc, raw[:3] == b'\xef\xbb\xbf'
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('gbk'), 'gbk', False

def extract_block(text, sig, anchor, stop):
    """提取 [sep前注释头..anchor所在函数] 完整块"""
    s = text.find(sig)
    start = text.rfind(sep, 0, s)
    stop_sig = text.find(stop, s)
    end = text.rfind(sep, 0, stop_sig)
    assert start >= 0 and end > start, f'locate fail sig={sig} stop={stop}'
    return start, end, text[start:end]

sep = '// ====================================================================='

# ---- 从 test.cpp 提取新块 ----
t_text, t_enc, _ = read(src)
_, _, tm300_new = extract_block(t_text, 'DUT_API int TM300_OSC_64K', sep, 'DUT_API int TM301_OSC_4P5M')
_, _, tm301_new = extract_block(t_text, 'DUT_API int TM301_OSC_4P5M', sep, 'DUT_API int TM400_VBUS_OVP_VTH1')
new_block = tm300_new + sep + '\r\n' + tm301_new
print('test.cpp 提取: TM300+TM301 块长度', len(new_block))

# ---- 替换 gen_tm216_402.cpp ----
g_text, g_enc, g_bom = read(gen)
old_start, old_end, old_block = extract_block(g_text, 'DUT_API int TM300_OSC_64K', sep, 'DUT_API int TM400_VBUS_OVP_VTH1')
print('gen 旧块:', old_start, old_end, len(old_block))

new_gen = g_text[:old_start] + new_block.replace('\r\n', '\n') + g_text[old_end:]
bom = '\ufeff' if g_bom else ''
with open(gen, 'wb') as f:
    f.write(bom.encode('utf-8') + new_gen.encode('utf-8'))
print(f'gen_tm216_402.cpp 更新完成: {len(g_text)} -> {len(new_gen)}')
print('校验 TM300 trim key:', 'trim("osc_64k")' in new_gen, '| TM301 trim key:', 'trim("osc_4p5m")' in new_gen)
print('校验无旧残留 0xF2=0x04:', 'I2CWriteSameData(DEV_ADDR, 0xF2, 0x04)' not in new_gen)
