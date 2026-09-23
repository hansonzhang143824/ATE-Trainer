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

BC = os.path.join(SRC, 'BoardCheck.h')
TG = os.path.join(SRC, 'treg.h')
bl = L(BC)
tl = L(TG)

p('=== 1. BoardCheck.h 205-235 (CBC_log class head + access specifiers) ===')
for n in range(205, 236):
    p('  %5d| %s' % (n, bl[n - 1].rstrip()))

p('')
p('=== 2. BoardCheck.h 745-790 (log declarations, access specifier, enclosing class) ===')
for n in range(745, min(791, len(bl) + 1)):
    p('  %5d| %s' % (n, bl[n - 1].rstrip()))

p('')
p('=== 3. enclosing class of line 778 (walk back for class/struct and access specifiers) ===')
depth = 0
for n in range(778, 0, -1):
    s = bl[n - 1]
    depth += s.count('}')
    depth -= s.count('{')
    if re.match(r'\s*(class|struct)\s+[A-Za-z_]\w*', s) and depth <= 0:
        p('  enclosing type at line %d: %s' % (n, s.rstrip()))
        break
p('  access specifiers between the enclosing type and line 778:')
inside = False
for n in range(778, 0, -1):
    s = bl[n - 1].strip()
    if re.match(r'^(class|struct)\s+[A-Za-z_]\w*', s):
        inside = True
    if inside and re.match(r'^(public|private|protected)\s*:', s):
        p('     line %d: %s' % (n, s))
        break

p('')
p('=== 4. access specifier governing the CBC_log::log / test_log declarations (before line 759) ===')
for n in range(758, 200, -1):
    s = bl[n - 1].strip()
    if re.match(r'^(public|private|protected)\s*:', s):
        p('     nearest specifier BEFORE (or at) line 759: line %d: %s' % (n, s))
        break
for n in range(759, 790):
    s = bl[n - 1].strip()
    if re.match(r'^(public|private|protected)\s*:', s):
        p('     nearest specifier AFTER line 759:      line %d: %s' % (n, s))
        break

p('')
p('=== 5. tree scan: who USES these primitives anywhere under ForCodexDebug ===')
pats = ['CBC_log', 'bc_log', 'test_log', 'treg_error_log', 'log_data', 'TREG_LOG', 'TREG_ERROR', 'datalog_func']
hits = {k: [] for k in pats}
nfiles = 0
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.cpp', '.h', '.hpp', '.c', '.cxx')):
            continue
        fp = os.path.join(dp, f)
        try:
            t = rb(fp).decode('utf-8-sig', errors='replace')
        except Exception as e:
            p('  [unreadable] %s (%s)' % (fp, e))
            continue
        nfiles += 1
        for k in pats:
            c = len(re.findall(r'\b' + re.escape(k) + r'\b', t))
            if c:
                hits[k].append((os.path.relpath(fp, ROOT), c))
p('  source files scanned: %d' % nfiles)
for k in pats:
    p('  %-16s : %s' % (k, hits[k] if hits[k] else 'NONE ANYWHERE'))

p('')
p('=== 6. includes in test.cpp / sub.cpp / StdAfx.h ===')
for f in ('test.cpp', 'sub.cpp', 'StdAfx.h', 'BoardCheck.h'):
    fp = os.path.join(SRC, f)
    if not os.path.exists(fp):
        p('  %s : MISSING' % f)
        continue
    t = rb(fp).decode('utf-8-sig', errors='replace')
    incs = re.findall(r'^\s*#\s*include\s*[<"]([^">]+)[">]', t, re.M)
    p('  %s (%d bytes) includes: %s' % (f, len(rb(fp)), incs))
    for key in ('BoardCheck', 'treg', 'StdAfx'):
        if any(key.lower() in i.lower() for i in incs):
            p('      -> includes %s' % key)

p('')
p('=== 7. result-primitive recount in test.cpp (raw tokens vs comment-stripped code) ===')
tj = rb(os.path.join(SRC, 'test.cpp')).decode('utf-8-sig', errors='replace')

def strip_comments(text):
    o = []; i = 0; n = len(text); st = 'code'
    while i < n:
        c = text[i]
        if st == 'code':
            if c == '"': st = 'str'; o.append(c)
            elif c == "'": st = 'chr'; o.append(c)
            elif c == '/' and i + 1 < n and text[i + 1] == '/': st = 'line'; i += 1
            elif c == '/' and i + 1 < n and text[i + 1] == '*': st = 'block'; i += 1
            else: o.append(c)
        elif st == 'str':
            o.append(c)
            if c == '\\': i += 1; o.append(text[i]) if i < n else None
            elif c == '"': st = 'code'
        elif st == 'chr':
            o.append(c)
            if c == '\\': i += 1; o.append(text[i]) if i < n else None
            elif c == "'": st = 'code'
        elif st == 'line':
            if c == '\n': st = 'code'; o.append(c)
        elif st == 'block':
            if c == '*' and i + 1 < n and text[i + 1] == '/': st = 'code'; i += 1
        i += 1
    return ''.join(o)

code = strip_comments(tj)
for name in ('SetTestResult', 'GetMeasResult', 'StsGetParam', 'rampv_capv', 'LogData'):
    raw = len(re.findall(r'\b' + name + r'\b', tj))
    rawcall = len(re.findall(r'\b' + name + r'\s*\(', tj))
    codecall = len(re.findall(r'\b' + name + r'\s*\(', code))
    p('  %-16s raw token=%-5d raw call=%-5d comment-stripped call=%-5d' % (name, raw, rawcall, codecall))
p('  in-code log-like callables in test.cpp:',
  sorted(set(re.findall(r'\b([A-Za-z_]\w*(?:::\w+)?)\s*\(', code)) & set(
      m for m in re.findall(r'\b([A-Za-z_]\w*(?:::\w+)?)\s*\(', code)
      if re.search(r'(?i)log|trace|report|print|record', m))))

open(os.path.join(OUT, 'extern_c11b.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c) < 128 for c in x)))
print('[non-ascii lines suppressed: %d of %d]' % (
    sum(1 for x in out if any(ord(c) >= 128 for c in x)), len(out)))
