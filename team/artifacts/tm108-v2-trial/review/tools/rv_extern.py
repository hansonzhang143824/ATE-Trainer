import os, re, io, json

ROOT = r'D:\PROJECT6-DALI\ForCodexDebug'
SRC = os.path.join(ROOT, 'source')
OUT = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\out'

def rb(p):
    with open(p, 'rb') as f:
        return f.read()

def txt(p):
    return rb(p).decode('utf-8-sig', errors='replace')

lines_out = []
def p(*a):
    lines_out.append(' '.join(str(x) for x in a))

BC = os.path.join(SRC, 'BoardCheck.h')
TG = os.path.join(SRC, 'treg.h')

p('=== FILES ===')
for f in (BC, TG):
    b = rb(f)
    p('  %s  bytes=%d sha256=%s bom=%s crlf=%d' % (
        f, len(b),
        __import__('hashlib').sha256(b).hexdigest(),
        b[:3] == b'\xef\xbb\xbf', b.count(b'\r\n')))

# ---- BoardCheck.h : CBC_log region ----
bl = txt(BC).split('\n')
bl = [x[:-1] if x.endswith('\r') else x for x in bl]
p('')
p('=== BoardCheck.h  class CBC_log and log()/test_log() declarations ===')
for i, l in enumerate(bl):
    if 'CBC_log' in l or re.search(r'\blog\s*\(|\btest_log\s*\(', l) or 'LogFile' in l or 'mslog' in l.lower():
        s = l.rstrip()
        p('  %5d| %s' % (i + 1, s))

p('')
p('=== BoardCheck.h : any global/singleton instance of CBC_log ===')
for i, l in enumerate(bl):
    if re.search(r'CBC_log', l):
        s = l.rstrip()
        p('  %5d| %s' % (i + 1, s))

# ---- treg.h : the named lines and context ----
tl = txt(TG).split('\n')
tl = [x[:-1] if x.endswith('\r') else x for x in tl]
p('')
p('=== treg.h : lines 100-200 (callbacks, log_data, treg_error_log) ===')
for n in range(100, min(201, len(tl) + 1)):
    p('  %5d| %s' % (n, tl[n - 1].rstrip()))

p('')
p('=== treg.h : every line mentioning log ===')
for i, l in enumerate(tl):
    if re.search(r'log', l, re.I):
        p('  %5d| %s' % (i + 1, l.rstrip()))

open(os.path.join(OUT, 'extern_c11.txt'), 'w', encoding='utf-8').write('\n'.join(lines_out))
print('\n'.join(x for x in lines_out if all(ord(c) < 128 for c in x)))
print('[non-ascii lines suppressed: %d of %d]' % (
    sum(1 for x in lines_out if any(ord(c) >= 128 for c in x)), len(lines_out)))
