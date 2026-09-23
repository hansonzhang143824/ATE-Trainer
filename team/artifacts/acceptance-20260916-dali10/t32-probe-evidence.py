# -*- coding: utf-8 -*-
"""t32 probe: locate every evidence file the verification contract requires, with plaintext hashes."""
import os, sys, json, hashlib, glob, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"
DEVEL = r"D:/PROJECT6-DALI/devel"

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

print('=== 1. candidate evidence files (linux-style search) ===')
pats = [
    os.path.join(ROOT, 'team', 'artifacts', RUN, '**', '*.bak'),
    os.path.join(ROOT, 'team', 'artifacts', RUN, '**', '*before*'),
    os.path.join(ROOT, 'backup', '**', '*'),
    os.path.join(ROOT, 'team', 'artifacts', RUN, '**', '*.md'),
]
seen = set()
for pat in pats:
    for p in glob.glob(pat, recursive=True):
        if os.path.isfile(p) and p not in seen:
            seen.add(p)
for p in sorted(seen):
    rel = os.path.relpath(p, ROOT)
    if any(k in rel.lower() for k in ('t24', 'review', 'before', 'bak', 'ledger', 'manifest', 'verification', 'accept')):
        print('  %9d  %s' % (os.path.getsize(p), rel))

print()
print('=== 2. tree files of interest ===')
for p in [os.path.join(TARGET, 'source', 'test.cpp'), os.path.join(DEVEL, 'source', 'test.cpp'),
          os.path.join(TARGET, 'source', 'StdAfx.h'), os.path.join(DEVEL, 'source', 'StdAfx.h'),
          os.path.join(TARGET, 'source', 'sub.cpp'), os.path.join(DEVEL, 'source', 'sub.cpp'),
          os.path.join(TARGET, 'source', 'Pin_Channel_define.h'), os.path.join(DEVEL, 'source', 'Pin_Channel_define.h')]:
    print('  %-58s exists=%-5s %s' % (p.replace(ROOT, '.'), os.path.exists(p), (sha(p) if os.path.exists(p) else '-')))

print()
print('=== 3. run dir top-level key artifacts ===')
for name in ['implementation-manifest.json', 'implementation-payload-TM600-TM601.cpp', 'review-findings.json',
             'test-plan.json', 'setup-contract.json', 'schematic-ir.json', 'dft-ir.json',
             'implementation-payload-TM600-TM601.cpp.before', 'APPLY-TM600-TM601.md']:
    p = os.path.join(ROOT, 'team', 'artifacts', RUN, name)
    print('  %-52s exists=%-5s %s' % (name, os.path.exists(p), (('%d %s' % (os.path.getsize(p), sha(p)[:16])) if os.path.exists(p) else '-')))

print()
print('=== 4. run ledger mentions of the baseline bak / t24 / t25 / t29 ===')
lp = os.path.join(ROOT, 'team', 'artifacts', RUN, 'RUN-LEDGER.md')
if os.path.exists(lp):
    txt = rt(lp)
    lines = txt.splitlines()
    print('  ledger lines:', len(lines), 'size', os.path.getsize(lp), sha(lp)[:16])
    for i, l in enumerate(lines, 1):
        if re.search(r'before_TM600|t24|t25|t29|verification-report|434[,.]?629|taskCont', l, re.I):
            print('   %5d %s' % (i, l.strip()[:190]))
