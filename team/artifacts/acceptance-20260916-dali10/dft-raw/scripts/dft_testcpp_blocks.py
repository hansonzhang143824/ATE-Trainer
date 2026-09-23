# -*- coding: utf-8 -*-
"""Extract per-TM source blocks from debug test.cpp (and sub.cpp helpers) as evidence for dft-ir.json."""
import os, re, json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
OUT = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")
DBG = r"D:/PROJECT6-DALI/ForCodexDebug/source"

def decode(raw):
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc), enc
        except Exception: pass
    return raw.decode('utf-8', errors='replace'), 'replace'

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

tcpp = os.path.join(DBG, 'test.cpp')
t, enc = decode(open(tcpp, 'rb').read())
lines = t.split('\n')
print('test.cpp', sha256_file(tcpp), enc, 'lines', len(lines))

NAMES = ['TM000_IQ_STANDBY', 'TM001_IIN_SUSPEND', 'TM001_2_IQ_SHIPMODE', 'TM001_3_IQ_OPERATION',
         'TM102_HSKP_LP_ATEST0', 'TM103_HSKP_LP_HR_0P5U', 'TM108_HSKP_VAC1_PRST', 'TM109_HSKP_VAC2_PRST',
         'Trim_BG_RES_DIV', 'TM1205_TRX_BST_UV_GD', 'TM600', 'TM601', 'RDSON',
         'TM105_HSKP_VSPRE_MAX_CMP', 'TM106_HSKP_VBUS_PRST', 'TM107_HSKP_VBUS_HT_VBAT',
         'TM110_HSKP_VAC3_PRST', 'TM111_HSKP_VBAT_UV', 'TM112_HSKP_VBAT_HT_3P1V']

# index of all DUT_API function definitions
deffn = {}
for m in re.finditer(r'(?m)^DUT_API\s+int\s+(\w+)\s*\(', t):
    deffn[m.group(1)] = m.start()
print('\n#### all DUT_API functions in test.cpp (%d) ####' % len(deffn))
for k in deffn: print('  ', k)

blocks = {}
for name in NAMES:
    if name in deffn:
        start = deffn[name]
        # find preceding comment block start
        pre = t.rfind('\n//', 0, start)
        # walk back over contiguous comment lines
        s = start
        while True:
            ls = t.rfind('\n', 0, s)
            line = t[ls + 1:s] if ls >= 0 else t[:s]
            if line.strip().startswith('//') or line.strip() == '':
                s = ls if ls >= 0 else 0
                if ls < 0: break
            else:
                break
        # find closing brace of function at column 0
        m2 = re.compile(r'(?m)^\}').search(t, start)
        end = m2.end() if m2 else min(len(t), start + 8000)
        blocks[name] = {'file': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
                        'startLine': t.count('\n', 0, s) + 1,
                        'endLine': t.count('\n', 0, end) + 1,
                        'text': t[s:end]}
    else:
        blocks[name] = None
        print('\n!! NOT FOUND in test.cpp:', name)

with open(os.path.join(OUT, 'testcpp-blocks.json'), 'w', encoding='utf-8') as f:
    json.dump({'sha256': sha256_file(tcpp), 'encoding': enc, 'blocks': blocks}, f, ensure_ascii=False, indent=2)

# write readable per-TM file
with open(os.path.join(OUT, 'testcpp-blocks.txt'), 'w', encoding='utf-8') as f:
    f.write('test.cpp sha256=%s encoding=%s lines=%d\n' % (sha256_file(tcpp), enc, len(lines)))
    for name, b in blocks.items():
        f.write('\n' + '=' * 110 + '\n')
        if b is None:
            f.write('### %s : NOT FOUND IN TEST.CPP (baseline missing)\n' % name)
        else:
            f.write('### %s : lines %d-%d\n' % (name, b['startLine'], b['endLine']))
            f.write(b['text'] + '\n')
print('\nwrote', os.path.join(OUT, 'testcpp-blocks.txt'))
