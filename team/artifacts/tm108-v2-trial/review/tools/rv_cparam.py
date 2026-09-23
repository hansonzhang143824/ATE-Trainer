import os, re

ROOT = r'D:\PROJECT6-DALI\ForCodexDebug'
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

# 1. every file under the whole target root mentioning CParam, and any class-decl pattern
p('=== 1. search whole ForCodexDebug tree for a CParam declaration ===')
pats = [r'class\s+\w*\s*CParam', r'class\s+CParam', r'typedef.*CParam', r'struct\s+CParam']
cand = []
for dp, dn, fn in os.walk(ROOT):
    if '.git' in dp or 'ipch' in dp.lower():
        continue
    for f in fn:
        if not f.lower().endswith(('.h', '.hpp', '.cpp', '.cxx', '.inl')):
            continue
        fp = os.path.join(dp, f)
        try:
            t = rb(fp).decode('utf-8-sig', errors='replace')
        except Exception:
            continue
        if 'CParam' in t:
            rel = os.path.relpath(fp, ROOT)
            decl = [q for q in pats if re.search(q, t)]
            n = len(re.findall(r'\bCParam\b', t))
            cand.append((n, rel, decl))
for n, rel, decl in sorted(cand, key=lambda x: -x[0]):
    p('  %-52s CParam=%-5d decl=%s' % (rel, n, decl if decl else '-'))

# 2. the class that owns SetTestResult (wherever it lives)
p('')
p('=== 2. contexts around the first "SetTestResult" declaration seen anywhere ===')
seen = set()
for n, rel, _ in sorted(cand, key=lambda x: -x[0])[:6]:
    fp = os.path.join(ROOT, rel)
    lines = L(fp)
    for i, l in enumerate(lines):
        if re.search(r'SetTestResult', l) and '(' in l and ';' in l:
            key = (rel, i)
            if key in seen:
                continue
            seen.add(key)
            lo = max(1, i - 12)
            hi = min(len(lines), i + 8)
            p('  --- %s around line %d ---' % (rel, i + 1))
            for k in range(lo, hi + 1):
                p('  %5d| %s' % (k, lines[k - 1].rstrip()))
            p('')
            break

# 3. Test_Method.h : the test_method object surface (does it expose a logger?)
p('=== 3. Test_Method.h : members whose name matches log/print/record/label ===')
tm = None
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.lower() == 'test_method.h':
            tm = os.path.join(dp, f)
            break
    if tm:
        break
p('  file: %s' % (tm or 'NOT FOUND'))
if tm:
    tml = L(tm)
    p('  bytes=%d lines=%d sha256=%s' % (len(rb(tm)), len(tml),
      __import__('hashlib').sha256(rb(tm)).hexdigest()))
    for i, l in enumerate(tml):
        if re.search(r'(?i)log|label|print|record|trace|SetTestResult|cmpname', l):
            p('  %5d| %s' % (i + 1, l.rstrip()))

# 4. sub.h : anything loggable
p('')
p('=== 4. sub.h : members matching log/print/record ===')
sh = None
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.lower() == 'sub.h':
            sh = os.path.join(dp, f)
            break
    if sh:
        break
p('  file: %s' % (sh or 'NOT FOUND'))
if sh:
    shl = L(sh)
    hits = [(i + 1, l.rstrip()) for i, l in enumerate(shl) if re.search(r'(?i)log|print|record', l)]
    p('  lines=%d  hits=%d' % (len(shl), len(hits)))
    for n, l in hits[:40]:
        p('  %5d| %s' % (n, l))

open(os.path.join(OUT, 'cparam.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c) < 128 for c in x)))
print('[non-ascii suppressed: %d of %d]' % (
    sum(1 for x in out if any(ord(c) >= 128 for c in x)), len(out)))
