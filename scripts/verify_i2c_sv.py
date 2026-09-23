# -*- coding: utf-8 -*-
# 核对 AI.cpp 新批次 I2CWriteSameData 与 reg_config/tm*.sv verbatim 一致性
import io, re, os

AI = r'D:\Newtest\CLAUDE_PROCESS\Project\DALI\AI.cpp'
SV_DIR = r'D:\Newtest\CLAUDE_PROCESS\Project\DALI\reg_config'

def read_enc(path):
    """DLP 透明加密文件: utf-8-sig→utf-8→gbk→latin-1 回退"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')

def parse_i2c(text):
    """提取所有 I2CWriteSameData 行, 返回 (reg, val) 列表"""
    return re.findall(r'I2CWriteSameData\(\s*DEV_ADDR\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)', text)

with io.open(AI, 'r', encoding='utf-8') as f:
    src = f.read()

# 新批次函数 (按名精确提取)
tms = [206,207,210,211,212,213,214,215,220,222,300,301,
       400,401,402,403,406,408,409,410,411,412,413,418,419,420,421,422,424,425]

ok = True
checked = 0
for tm in tms:
    num = str(tm).zfill(3)
    # AI.cpp 函数块
    m = re.search(rf'DUT_API int (TM{num}\w*)\(short funcindex', src)
    if not m:
        print(f'TM{num}: FUNCTION NOT FOUND in AI.cpp'); ok = False; continue
    start = m.start()
    end = src.find('DUT_API int TM', start + 1)
    if end == -1: end = len(src)
    fn = src[start:end]
    ai_i2c = parse_i2c(fn)

    # .sv 文件
    sv_path = os.path.join(SV_DIR, f'tm{num}.sv')
    if not os.path.exists(sv_path):
        print(f'TM{num}: .sv NOT FOUND'); continue
    sv = read_enc(sv_path)
    sv_i2c = parse_i2c(sv)

    # 对齐 (AI 可能无 0x57 等; .sv 是源)
    ai_idx = 0
    mismatches = []
    for sv_reg, sv_val in sv_i2c:
        found = False
        for i in range(ai_idx, len(ai_i2c)):
            a_reg, a_val = ai_i2c[i]
            if a_reg == sv_reg:
                if a_val == sv_val:
                    found = True; ai_idx = i + 1
                else:
                    mismatches.append(f'reg {a_reg}: AI=0x{a_val} vs sv=0x{sv_val}')
                break
        if not found and not mismatches:
            # 无匹配 reg 或值不同
            pass
    # 重新做完整比对 (简单: AI 中每行 .sv 都必须存在)
    ai_set = set(ai_i2c)
    for sv_reg, sv_val in sv_i2c:
        if (sv_reg, sv_val) not in ai_set:
            mismatches.append(f'reg {sv_reg}: .sv=0x{sv_val} NOT in AI')
    checked += 1
    status = 'OK' if not mismatches else 'MISMATCH'
    if mismatches:
        ok = False
        print(f'TM{num}: {status} — {mismatches}')
    else:
        print(f'TM{num}: {status} ({len(ai_i2c)} writes)')

print(f'\nChecked {checked} tests. ', 'ALL I2C VALUES MATCH .sv' if ok else '*** MISMATCHES FOUND ***')
