import os, re, hashlib

ROOT = r'D:\PROJECT6-DALI\ForCodexDebug'
SRC = os.path.join(ROOT, 'source')
OUT = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\out'

def rb(p):
    with open(p, 'rb') as f:
        return f.read()

def L(p):
    t = rb(p).decode('utf-8-sig', errors='replace')
    x = t.split('\n')
    return [y[:-1] if y.endswith('\r') else y for y in x]

out = []
def p(*a):
    out.append(' '.join(str(x) for x in a))

# 1. the 4 BoardCheck mentions in test.cpp -- decisive for CBC_log reachability
p('=== 1. every "BoardCheck" occurrence in test.cpp ===')
tl = L(os.path.join(SRC, 'test.cpp'))
for i, l in enumerate(tl):
    if 'BoardCheck' in l:
        p('  %5d| %s' % (i + 1, l.rstrip()))
p('  (if these are not a type use, BoardCheck::log is not reachable)')

# 2. LogDataStruct.h -- name suggests a log data structure
p('')
p('=== 2. LogDataStruct.h (in the include closure) — full listing if small ===')
fp = os.path.join(SRC, 'LogDataStruct.h')
if os.path.exists(fp):
    b = rb(fp)
    ls = L(fp)
    p('  bytes=%d lines=%d sha256=%s' % (len(b), len(ls), hashlib.sha256(b).hexdigest()))
    for i, l in enumerate(ls):
        p('  %5d| %s' % (i + 1, l.rstrip()))
else:
    p('  NOT FOUND')

# 3. mylib.h -- in the closure
p('')
p('=== 3. mylib.h (in the include closure) — members matching log/print/record ===')
fp = os.path.join(SRC, 'mylib.h')
if os.path.exists(fp):
    ls = L(fp)
    p('  bytes=%d lines=%d sha256=%s' % (len(rb(fp)), len(ls), hashlib.sha256(rb(fp)).hexdigest()))
    hits = [(i + 1, l.rstrip()) for i, l in enumerate(ls) if re.search(r'(?i)log|print|record|trace|SetTestResult', l)]
    p('  hits=%d' % len(hits))
    for n, l in hits[:60]:
        p('  %5d| %s' % (n, l))
else:
    p('  NOT FOUND')

# 4. spec.h -- does it declare CParam or any result/log API?
p('')
p('=== 4. spec.h / sub.h / tempchar.h — SetTestResult or CParam declarations ===')
for f in ('spec.h', 'sub.h', 'tempchar.h', 'StdAfx.h', 'userres.h', 'usertype.h'):
    fp = os.path.join(SRC, f)
    if not os.path.exists(fp):
        p('  %-14s NOT FOUND' % f)
        continue
    ls = L(fp)
    t = '\n'.join(ls)
    p('  %-14s lines=%-5d CParam=%d SetTestResult=%d class-decl-%s'
      % (f, len(ls), len(re.findall(r'\bCParam\b', t)),
         len(re.findall(r'SetTestResult', t)),
         sorted(set(re.findall(r'class\s+(\w+)', t)))[:8]))

# 5. any declaration of SetTestResult anywhere in the tree (finds the CParam owner)
p('')
p('=== 5. any DECLARATION of SetTestResult (with a parameter list and semicolon) ===')
found = False
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.h', '.hpp', '.cpp')):
            continue
        fpp = os.path.join(dp, f)
        for i, l in enumerate(L(fpp)):
            if re.search(r'SetTestResult\s*\([^)]*\)\s*;', l):
                p('  %-28s %5d| %s' % (os.path.relpath(fpp, ROOT), i + 1, l.strip()[:150]))
                found = True
if not found:
    p('  NONE -> CParam/SetTestResult is declared outside this checkout')

# 6. whole-tree search for any other plausible log API name
p('')
p('=== 6. tree-wide search for other candidate log APIs ===')
names = ['WriteLog', 'AddLog', 'LogMessage', 'LogLine', 'LogText', 'LogString',
         'log_msg', 'log_text', 'add_log', 'write_log', 'PrintLog', 'SetLog',
         'LogData', 'msLogData', 'DataLog', 'datalog', 'TestLog', 'test_log']
for n in names:
    hits = []
    for dp, dn, fn in os.walk(SRC):
        for f in fn:
            if not f.lower().endswith(('.h', '.hpp', '.cpp')):
                continue
            fpp = os.path.join(dp, f)
            c = len(re.findall(r'\b' + re.escape(n) + r'\b', rb(fpp).decode('utf-8-sig', errors='replace')))
            if c:
                hits.append((os.path.relpath(fpp, ROOT), c))
    if hits:
        p('  %-12s %s' % (n, hits))

open(os.path.join(OUT, 'final_reach.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c) < 128 for c in x)))
print('[non-ascii suppressed: %d of %d]' % (
    sum(1 for x in out if any(ord(c) >= 128 for c in x)), len(out)))
