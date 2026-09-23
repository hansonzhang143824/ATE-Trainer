# -*- coding: utf-8 -*-
"""Compact extraction: meta scope records, reg_config bodies, PROGRESS/test_conditions mentions of the scope."""
import os, json, re, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
OUT = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")

def decode(raw):
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc), enc
        except Exception: pass
    return raw.decode('utf-8', errors='replace'), 'replace'

def rt(p): return decode(open(p, 'rb').read())
def sh(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

SCOPE = {'TM000', 'TM001', 'TM001_2', 'TM001_3', 'TM102', 'TM103', 'TM108', 'TM108_1', 'TM109', 'TM135', 'TM600', 'TM601', 'TM1205'}

mp = os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json')
meta = json.loads(rt(mp)[0])
print('#### ALL meta functionNames ####')
for f in meta['functions']:
    print('  %-32s dftItem=%-10s testType=%-8s projectType=%s paramType=%s' %
          (f.get('functionName'), f.get('dftItem'), f.get('testType'), f.get('projectType'), f.get('paramType')))
print()
print('#### compact meta for scope ####')
for f in meta['functions']:
    if str(f.get('dftItem')) in SCOPE or str(f.get('functionName')) in SCOPE:
        ov = f.get('overview', {})
        print('=' * 90)
        print('%-32s dftItem=%-9s testType=%-8s paramType=%-6s projectType=%s' %
              (f.get('functionName'), f.get('dftItem'), f.get('testType'), f.get('paramType'), f.get('projectType')))
        print('  overview: level=%s name=%s exp=%r unit=%s test=%r helper=%r' %
              (ov.get('level'), ov.get('name'), ov.get('expectValue'), ov.get('unit'), ov.get('test'), ov.get('helper')))
        print('  params:', json.dumps(f.get('params'), ensure_ascii=False))
        hw = []
        for h in f.get('hardwareInit', []):
            if h.get('cmd') == 'vset':
                hw.append('vset[%s,%s,%s,%s]' % (h.get('pin'), h.get('value'), h.get('time'), h.get('ignore')))
            else:
                hw.append(str(h.get('cmd')))
        print('  hardwareInit:', ' | '.join(hw))
        print('  registers:', json.dumps(f.get('registers'), ensure_ascii=False))
        print('  capAuthority:', json.dumps(f.get('capAuthority'), ensure_ascii=False))
        for k, v in f.items():
            if k not in ('functionName', 'dftItem', 'testType', 'paramType', 'projectType', 'overview', 'params', 'hardwareInit', 'registers', 'capAuthority'):
                print('  %s: %s' % (k, json.dumps(v, ensure_ascii=False)))

# reg_config needed
print('\n#### reg_config bodies (tm102/103/108/109/135/1205) ####')
for n in ('tm102.sv', 'tm103.sv', 'tm108.sv', 'tm109.sv', 'tm135.sv', 'tm1205.sv'):
    p = os.path.join(ROOT, 'project', 'DALI', 'reg_config', n)
    t, enc = rt(p)
    print('=' * 90)
    print('###', n, sh(p))
    # only the I2C / vset / iset lines
    for line in t.splitlines():
        s = line.strip()
        if not s: continue
        if s.startswith('//') or s.startswith('`') or s.startswith('#'):
            print('   ', s[:160]); continue
        print('   ', s[:160])

# PROGRESS.md / test_conditions mentions
print('\n#### PROGRESS.md + test_conditions mentions ####')
for rel in ('docs/PROGRESS.md', 'project/DALI/meta/test_conditions.yaml'):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print('missing', rel); continue
    t, enc = rt(p)
    print('=' * 90)
    print('###', rel, sh(p), enc, 'lines', t.count('\n') + 1)
    lines = t.splitlines()
    for i, line in enumerate(lines, 1):
        if re.search(r'(TM600|TM601|RDSON|HS_RDSON|LS_RDSON|11 m|7\.5|BST-SW|2 FLOAT|FLOAT)', line, re.I):
            print('   %5d %s' % (i, line.strip()[:220]))
print('DONE')
