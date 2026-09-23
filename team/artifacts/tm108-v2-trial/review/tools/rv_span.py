import hashlib, os, json, difflib

BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
OUT = os.path.join(BASE, 'review', 'tools', 'out')
os.makedirs(OUT, exist_ok=True)

AFTER = os.path.join(BASE, 'review', 'copy', 'test.cpp')
BEFORE = os.path.join(BASE, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')


def load(p):
    with open(p, 'rb') as f:
        b = f.read()
    txt = b.decode('utf-8-sig')
    # split on LF, strip trailing CR -> line list; keep trailing empty removed if file ends with newline
    raw = txt.split('\n')
    lines = [l[:-1] if l.endswith('\r') else l for l in raw]
    if lines and lines[-1] == '':
        lines = lines[:-1]
    return b, lines


ba, A = load(AFTER)
bb, B = load(BEFORE)
print('after  sha256', hashlib.sha256(ba).hexdigest(), 'lines', len(A))
print('before sha256', hashlib.sha256(bb).hexdigest(), 'lines', len(B))

# locate the TM108 signature in after
sig = 'DUT_API int TM108_HSKP_VAC1_PRST'
siglines = [i + 1 for i, l in enumerate(A) if sig in l]
print('sig lines (after, 1-based):', siglines)
sig2 = [i + 1 for i, l in enumerate(B) if sig in l]
print('sig lines (before, 1-based):', sig2)

# find the function end: matching closing brace from the signature line
def func_span(lines, start):
    depth = 0
    started = False
    for i in range(start - 1, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started and depth == 0:
            return start, i + 1
    return start, None

if siglines:
    s, e = func_span(A, siglines[0])
    print('AFTER function span (1-based incl):', s, e)
if sig2:
    s2, e2 = func_span(B, sig2[0])
    print('BEFORE function span (1-based incl):', s2, e2)

def dump(lines, lo, hi, path):
    with open(path, 'w', encoding='utf-8') as f:
        for n in range(lo, hi + 1):
            if 1 <= n <= len(lines):
                f.write('%5d|%s\n' % (n, lines[n - 1]))

# generous window around the span
if siglines:
    dump(A, max(1, siglines[0] - 60), min(len(A), siglines[0] + 140), os.path.join(OUT, 'after_span.txt'))
if sig2:
    dump(B, max(1, sig2[0] - 60), min(len(B), sig2[0] + 140), os.path.join(OUT, 'before_span.txt'))
print('dumped span files to', OUT)
