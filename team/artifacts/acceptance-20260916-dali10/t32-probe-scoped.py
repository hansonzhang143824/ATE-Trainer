# -*- coding: utf-8 -*-
"""t32 probe 2: scoped invariants, K109/K110 presence across baselines/payload/target, t29 deploy check."""
import os, sys, json, re, hashlib
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RD = os.path.join(ROOT, 'team', 'artifacts', RUN)
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"

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

def strip_comments(src):
    out = []; i, n = 0, len(src); in_line = in_block = in_str = None
    while i < n:
        c = src[i]; nxt = src[i + 1] if i + 1 < n else ''
        if in_line:
            if c == '\n': in_line = False; out.append(c)
            i += 1; continue
        if in_block:
            if c == '*' and nxt == '/': in_block = False; i += 2; continue
            if c == '\n': out.append(c)
            i += 1; continue
        if in_str:
            out.append(c)
            if c == '\\': out.append(nxt); i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c == '/' and nxt == '/': in_line = True; i += 2; continue
        if c == '/' and nxt == '*': in_block = True; i += 2; continue
        if c in ('"', "'"): in_str = c; out.append(c); i += 1; continue
        out.append(c); i += 1
    return ''.join(out)

def func_block(text, name):
    m = re.search(r'DUT_API\s+int\s+' + re.escape(name) + r'\s*\(', text)
    if not m: return None, None, None
    brace = text.find('{', m.end()); depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == '{': depth += 1
        elif text[pos] == '}':
            depth -= 1
            if depth == 0:
                return text[m.start():pos + 1], text.count('\n', 0, m.start()) + 1, text.count('\n', 0, pos) + 1
    return text[m.start():], text.count('\n', 0, m.start()) + 1, None

print('=== A. per-function scoped invariants (comments stripped) ===')
files = {
 'target/test.cpp': os.path.join(TARGET, 'source', 'test.cpp'),
 'payload': os.path.join(RD, 'implementation-payload-TM600-TM601.cpp'),
 'baseline_bak': os.path.join(RD, 'backups', 'test.cpp.before_TM600_TM601.bak'),
}
SCOPE = [('delay_ms(1)', r'delay_ms\(1\)'), ('delay_ms(2)', r'delay_ms\(2\)'),
         ('SetClamp(50,50)', r'SetClamp\(\s*50\s*,\s*50\s*\)'),
         ('MeasureVI(200,5,FPVIe_MV_X10)', r'MeasureVI\(\s*200\s*,\s*5\s*,\s*FPVIe_MV_X10\s*\)'),
         ('bare 126', r'(?<![0-9A-Za-z_])126(?![0-9A-Za-z_])'), ('K126_V1P5_CAP', r'K126_V1P5_CAP'),
         ('ERROR_RES', r'ERROR_RES'), ('K109_BUSL1_PB0', r'K109_BUSL1_PB0'), ('K110_ACM18_BST', r'K110_ACM18_BST'),
         ('K109(any)', r'K109'), ('K110(any)', r'K110')]
scoped = {}
for label, p in files.items():
    txt = rt(p); st = strip_comments(txt)
    scoped[label] = {'size': os.path.getsize(p), 'sha256': sha(p),
                     'fileCounts': {k: len(re.findall(pat, st)) for k, pat in SCOPE},
                     'functions': {}}
    for fn in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
        blk, s, e = func_block(txt, fn)
        if blk is None:
            scoped[label]['functions'][fn] = {'found': False}
            continue
        bs = strip_comments(blk)
        scoped[label]['functions'][fn] = {'found': True, 'lines': [s, e], 'blockChars': len(blk),
                                          'counts': {k: len(re.findall(pat, bs)) for k, pat in SCOPE},
                                          'setOn': [ [t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1']
                                                     for so in re.findall(r'cbite\.SetOn\((.*?)\)\s*;', blk, re.DOTALL)]}
    print('--- %s (%d B, %s)' % (label, scoped[label]['size'], scoped[label]['sha256'][:12]))
    print('    file-level:', json.dumps(scoped[label]['fileCounts']))
    for fn, d in scoped[label]['functions'].items():
        if d['found']:
            print('    %-16s lines %s counts %s' % (fn, d['lines'], json.dumps(d['counts'])))
            print('                     SetOn: %s' % json.dumps(d['setOn'], ensure_ascii=False))
        else:
            print('    %-16s NOT FOUND' % fn)

print()
print('=== B. contract requirement for TM600 BST closure ===')
cp = os.path.join(RD, 'setup-contract.json')
c = json.loads(rt(cp))
print('  contract', os.path.getsize(cp), sha(cp)[:16])
csc = json.dumps(c, ensure_ascii=False)
hits = sorted(set(re.findall(r'[^\s,"\[\]]*(?:K?10[0-9]|K?11[0-9]|BUSL1_PB0|ACM18_BST)[^\s,"\[\]]*', csc)))[:40]
print('  K10x/K11x-ish tokens in contract:', hits[:40])
for key in ('pinRouteTable', 'aliasResolution', 'aliasFlatTable', 'relaySet'):
    if key in csc:
        print('  contract contains key section:', key)

print()
print('=== C. was t29 deployed? (t29 says payload 36381 B / 73b511b7) ===')
for p in [os.path.join(RD, 'implementation-payload-TM600-TM601.cpp'), os.path.join(TARGET, 'source', 'test.cpp')]:
    t = rt(p); st = strip_comments(t)
    print('  %-52s K109=%d K110=%d' % (os.path.relpath(p, ROOT).replace('\\', '/'), len(re.findall(r'K109', st)), len(re.findall(r'K110', st))))

out = os.path.join(RD, 't32-scoped-evidence.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(scoped, f, ensure_ascii=False, indent=1)
print('\nwrote', out)
