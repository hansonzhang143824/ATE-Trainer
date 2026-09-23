import os, re

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

# ---- where is CParam defined?
p('=== 1. files defining / declaring class CParam ===')
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.h', '.hpp')):
            continue
        fp = os.path.join(dp, f)
        t = rb(fp).decode('utf-8-sig', errors='replace')
        if re.search(r'\bclass\s+CParam\b', t):
            p('  %s : %d hits of "class CParam"' % (os.path.relpath(fp, ROOT),
                                                    len(re.findall(r'\bclass\s+CParam\b', t))))

# ---- CParam public methods (find the class body)
p('')
p('=== 2. CParam class body — every member declaration containing log/result/set ===')
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.h', '.hpp')):
            continue
        fp = os.path.join(dp, f)
        lines = L(fp)
        for i, l in enumerate(lines):
            if re.search(r'\bclass\s+CParam\b', l):
                p('  --- %s : %d ---' % (os.path.relpath(fp, ROOT), i + 1))
                for n in range(i + 1, min(i + 90, len(lines) + 1)):
                    s = lines[n - 1].rstrip()
                    if re.search(r'(?i)log|SetTestResult|GetMeasResult|public|private|protected|^\};', s):
                        p('  %5d| %s' % (n, s))
                break

# ---- treg_error_log definition & semantics
p('')
p('=== 3. treg.cpp : TREG_ERROR::treg_error_log and error() definitions ===')
tgc = os.path.join(SRC, 'treg.cpp')
tcl = L(tgc)
for i, l in enumerate(tcl):
    if re.search(r'treg_error_log|TREG_ERROR::error|::vprintf_s', l):
        lo = max(1, i - 2)
        hi = min(len(tcl), i + 22)
        p('  --- hit at line %d ---' % (i + 1))
        for n in range(lo, hi + 1):
            p('  %5d| %s' % (n, tcl[n - 1].rstrip()))
        p('')

# ---- any public logging API on TREG / TREG_LOG reachable from a TM?
p('=== 4. TREG class: members whose name contains log (to find a public wrapper) ===')
tl = L(os.path.join(SRC, 'treg.h'))
for i, l in enumerate(tl):
    if re.search(r'(?i)\blog', l):
        p('  %5d| %s' % (i + 1, l.rstrip()))

p('')
p('=== 5. TREG_LOG::log_data definition (who is allowed to write datalog) ===')
for i, l in enumerate(tcl):
    if re.search(r'void\s+TREG_LOG::log_data', l):
        for n in range(i + 1, min(len(tcl) + 1, i + 60)):
            p('  %5d| %s' % (n, tcl[n - 1].rstrip()))
        break

p('')
p('=== 6. tree-wide token counts (to reconcile the captain figures 200 / 422) ===')
tot = {}
per = {}
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.cpp', '.h', '.hpp')):
            continue
        fp = os.path.join(dp, f)
        t = rb(fp).decode('utf-8-sig', errors='replace')
        rel = os.path.relpath(fp, ROOT)
        for k in ('SetTestResult', 'GetMeasResult', 'CParam'):
            c = len(re.findall(r'\b' + k + r'\b', t))
            if c:
                tot[k] = tot.get(k, 0) + c
                per.setdefault(k, []).append((rel, c))
for k in ('SetTestResult', 'GetMeasResult', 'CParam'):
    p('  %-15s tree total=%d' % (k, tot.get(k, 0)))
    for rel, c in sorted(per.get(k, []), key=lambda x: -x[1])[:8]:
        p('        %-40s %d' % (rel, c))

p('')
p('=== 7. what StsGetParam returns / CParam result API actually used in test.cpp ===')
tj = rb(os.path.join(SRC, 'test.cpp')).decode('utf-8-sig', errors='replace')
calls = {}
for m in re.finditer(r'->\s*([A-Za-z_]\w*)\s*\(', tj):
    calls[m.group(1)] = calls.get(m.group(1), 0) + 1
p('  every "->method(" name used in test.cpp:')
for k, v in sorted(calls.items(), key=lambda x: -x[1]):
    p('        %-30s %d' % (k, v))

open(os.path.join(OUT, 'extern_c11c.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c) < 128 for c in x)))
print('[non-ascii lines suppressed: %d of %d]' % (
    sum(1 for x in out if any(ord(c) >= 128 for c in x)), len(out)))
