# -*- coding: utf-8 -*-
"""Extract in-scope meta entries + reg_config .sv contents + test.cpp/sub.cpp/stdfx references."""
import os, json, re, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
OUT = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")
os.makedirs(OUT, exist_ok=True)
DBG = r"D:/PROJECT6-DALI/ForCodexDebug/source"
DEV = r"D:/PROJECT6-DALI/devel/source"

def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for c in iter(lambda: f.read(1 << 20), b''):
                h.update(c)
    except Exception as e:
        return 'ERROR:' + str(e)
    return h.hexdigest()

def decode(raw):
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc), enc
        except Exception: pass
    return raw.decode('utf-8', errors='replace'), 'replace'

def rtext(p):
    return decode(open(p, 'rb').read())

SCOPE = ['TM000', 'TM001', 'TM102', 'TM103', 'TM108', 'TM109', 'TM135', 'TM600', 'TM601', 'TM1205']

# --- meta ---
mp = os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json')
meta = json.loads(rtext(mp)[0])
print('meta sha256', sha256_file(mp), 'funcs', len(meta['functions']))
print('#### meta: names containing scope bases / keywords ####')
keyre = re.compile(r'(000|001_|102_|103_|108_|109_|135|600|601|1205|RDSON|BG_RES_DIV|VAC1_PRST|VAC2_PRST|BST_UV)', re.I)
mhits = []
for f in meta['functions']:
    fn = f.get('functionName', '')
    di = f.get('dftItem', '')
    if keyre.search(str(fn)) or str(di) in SCOPE:
        mhits.append(f)
        print('=' * 100)
        print(json.dumps(f, ensure_ascii=False, indent=1))
print('meta hits', len(mhits))
with open(os.path.join(OUT, 'meta-scope.json'), 'w', encoding='utf-8') as fh:
    json.dump({'file': 'project/DALI/meta/dali_tm_meta.json', 'sha256': sha256_file(mp), 'hits': mhits}, fh, ensure_ascii=False, indent=2)

# --- reg_config ---
print('\n#### reg_config .sv ####')
regs = {}
svnames = ['tm600.sv', 'tm601.sv', 'rx_600.sv', 'rx_601.sv', 'tm102.sv', 'tm103.sv', 'tm108.sv', 'tm108_1.sv',
           'tm109.sv', 'tm135.sv', 'tm1205.sv', 'tm001_2.sv', 'tm100.sv', 'tm101.sv', 'tm602.sv']
for n in svnames:
    p = os.path.join(ROOT, 'project', 'DALI', 'reg_config', n)
    if not os.path.exists(p):
        print('MISSING', n); continue
    t, enc = rtext(p)
    regs[n] = {'sha256': sha256_file(p), 'encoding': enc, 'text': t}
    print('=' * 100)
    print('###', n, sha256_file(p), enc)
    print(t)
with open(os.path.join(OUT, 'regconfig-scope.json'), 'w', encoding='utf-8') as fh:
    json.dump(regs, fh, ensure_ascii=False, indent=2)

# --- source references in debug copy ---
print('\n#### source references (debug copy) ####')
sref = {}
for base, label in ((DBG, 'ForCodexDebug'), (DEV, 'devel(readonly)')):
    for fn in ('test.cpp', 'sub.cpp', 'StdAfx.h', 'sub.h', 'spec.cpp'):
        p = os.path.join(base, fn)
        if not os.path.exists(p):
            print('missing', p); continue
        t, enc = rtext(p)
        hits = []
        for pat in ('RDSON', 'TM600', 'TM601', 'TM1205', 'VAC1_PRST', 'VAC2_PRST', 'LP_HR_0P5U', 'LP_VBG_BF',
                    'VREF_1P0', 'BG_RES_DIV', 'IQ_STANDBY', 'IIN_SUSPEND', 'BST_UV'):
            for m in re.finditer(pat, t):
                ln = t.count('\n', 0, m.start()) + 1
                line = t.splitlines()[ln - 1] if ln - 1 < len(t.splitlines()) else ''
                hits.append({'pattern': pat, 'line': ln, 'text': line.strip()[:200]})
        sref[f'{label}/{fn}'] = {'sha256': sha256_file(p), 'encoding': enc, 'lineCount': t.count('\n') + 1, 'hits': hits}
        print(label, fn, 'lines', t.count('\n') + 1, 'sha256', sha256_file(p), 'hits', len(hits))
        for h in hits[:60]:
            print('   ', h['line'], h['pattern'], '|', h['text'])
with open(os.path.join(OUT, 'source-refs.json'), 'w', encoding='utf-8') as fh:
    json.dump(sref, fh, ensure_ascii=False, indent=2)
print('\nDONE')
