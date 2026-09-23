import os, re

BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
AFTER = os.path.join(BASE, 'review', 'copy', 'test.cpp')
b = open(AFTER, 'rb').read()
t = b.decode('utf-8-sig')
L = t.split('\n')
L = [x[:-1] if x.endswith('\r') else x for x in L]
if L and L[-1] == '':
    L = L[:-1]

out = []
def p(*a):
    out.append(' '.join(str(x) for x in a))

p('=== A. every line containing "LogData" WITH a following paren ===')
for i, l in enumerate(L):
    if re.search(r'LogData\s*\(', l):
        p('  %d: %s' % (i + 1, l.rstrip()))
p('')
p('=== B. every line containing "LogData" (any form), first 20 ===')
hits = [(i + 1, l.rstrip()) for i, l in enumerate(L) if 'LogData' in l]
p('  total LogData token lines:', len(hits))
for ln, l in hits[:20]:
    p('  %d: %s' % (ln, l))
p('')
p('=== C. real call statements (code, not comment) anywhere in test.cpp ===')
# strip comments properly per line for the call inventory
import re as _re
def code_of(lines):
    res = []
    inblock = False
    for idx, l in enumerate(lines):
        s = ''
        i = 0
        while i < len(l):
            if inblock:
                j = l.find('*/', i)
                if j == -1:
                    i = len(l)
                else:
                    inblock = False
                    i = j + 2
            else:
                j2 = l.find('//', i)
                k2 = l.find('/*', i)
                if j2 != -1 and (k2 == -1 or j2 < k2):
                    s += l[i:j2]
                    i = len(l)
                elif k2 != -1:
                    s += l[i:k2]
                    inblock = True
                    i = k2 + 2
                else:
                    s += l[i:]
                    i = len(l)
        res.append(s)
    return res
code = code_of(L)
calls = {}
for idx, l in enumerate(code):
    for m in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)?)\s*\(', l):
        calls.setdefault(m, []).append(idx + 1)
loggish = {k: v for k, v in calls.items() if re.search(r'(?i)log|trace|report|print|record|output|result', k)}
p('  callables in CODE (real statements) matching log|trace|report|print|record|output|result:')
for k in sorted(loggish):
    p('    %-34s n=%-5d first lines %s' % (k, len(loggish[k]), loggish[k][:6]))
p('')
p('  ALL distinct callables used in CODE in the TM108 body (2193-2309):')
body = code[2192:2309]
bc = {}
for idx, l in enumerate(body):
    for m in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', l):
        bc.setdefault(m, []).append(2193 + idx)
for k in sorted(bc):
    p('    %-28s %s' % (k, bc[k]))
p('')
p('=== D. printf/TRACE/OutputDebugString lines ===')
for i, l in enumerate(L):
    if re.search(r'\b(printf|TRACE|OutputDebugString|cout|fprintf|sprintf)\b', l):
        p('  %d: %s' % (i + 1, l.rstrip()))
p('')
p('=== E. cbite.SetOn exact count ===')
p('  cbite.SetOn occurrences:', len(re.findall(r'cbite\.SetOn', t)))
p('')
p('=== F. lines 2246-2276 of the after-file (the P4-P6 region, step heading check) ===')
for n in range(2236, 2280):
    p('  %d: %s' % (n, L[n - 1].rstrip()))
p('')
p('=== G. any function DEFINITION in test.cpp that takes a string/format (possible logger) ===')
for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_:<>]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^;{}]*)\)\s*$', t, re.M):
    args = m.group(3)
    if re.search(r'char\s*\*|LPCTSTR|LPTSTR|string|const\s+char', args) and re.search(r'(?i)log|trace|print|msg|message|text|report', m.group(2)):
        p('  %s' % m.group(0)[:150])

open(os.path.join(BASE, 'review', 'tools', 'out', 'logging.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
