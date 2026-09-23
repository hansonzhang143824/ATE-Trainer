import os, re, hashlib

ROOT = r'D:\PROJECT6-DALI\ForCodexDebug'
SRC = os.path.join(ROOT, 'source')
OUT = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\out'

def rb(p):
    with open(p, 'rb') as f:
        return f.read()

def txt(p):
    return rb(p).decode('utf-8-sig', errors='replace')

out = []
def p(*a):
    out.append(' '.join(str(x) for x in a))

# --- duplicate copies
p('=== 1. are the duplicate sources identical? (plaintext sha256 + size) ===')
for a, b in (('treg.h', os.path.join('src', 'treg.h')),
             ('treg.cpp', os.path.join('src', 'treg.cpp'))):
    fa, fb = os.path.join(SRC, a), os.path.join(SRC, b)
    ha = hashlib.sha256(rb(fa)).hexdigest() if os.path.exists(fa) else None
    hb = hashlib.sha256(rb(fb)).hexdigest() if os.path.exists(fb) else None
    p('  %-10s %s %d' % (a, ha, len(rb(fa)) if ha else -1))
    p('  %-10s %s %d  IDENTICAL=%s' % (b, hb, len(rb(fb)) if hb else -1, ha == hb))

# --- is TREG_LOG::log_data private in the src/ copy too?
for a in ('treg.h', os.path.join('src', 'treg.h')):
    fa = os.path.join(SRC, a)
    if not os.path.exists(fa):
        continue
    t = txt(fa)
    i = t.find('class TREG_LOG')
    seg = t[i:i + 900] if i >= 0 else ''
    p('  %-14s class TREG_LOG segment contains "private:"=%s  log_data decl=%s'
      % (a, 'private:' in seg, bool(re.search(r'log_data\s*\(', seg))))

# --- transitive include closure from test.cpp
p('')
p('=== 2. transitive include closure from test.cpp (local headers, resolved in source/) ===')
inc_re = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]', re.M)
seen = set()
order = []

def resolve(name):
    base = os.path.basename(name)
    for cand in (os.path.join(SRC, name), os.path.join(SRC, base),
                 os.path.join(SRC, 'src', base)):
        if os.path.exists(cand):
            return cand
    return None

stack = [os.path.join(SRC, 'test.cpp'), os.path.join(SRC, 'sub.cpp')]
while stack:
    fp = stack.pop()
    rp = os.path.relpath(fp, ROOT)
    if rp in seen:
        continue
    seen.add(rp)
    order.append(rp)
    try:
        t = txt(fp)
    except Exception:
        continue
    for m in inc_re.finditer(t):
        n = m.group(1)
        c = resolve(n)
        if c:
            stack.append(c)

p('  closure size: %d local headers/sources' % len(order))
for r in sorted(order):
    p('    %s' % r)
bc_in = any(r.lower().endswith('boardcheck.h') for r in seen)
tg_in = any(r.lower().endswith('treg.h') for r in seen)
p('  --> BoardCheck.h IN CLOSURE: %s' % bc_in)
p('  --> treg.h        IN CLOSURE: %s' % tg_in)

# --- any global / extern BoardCheck instance a TM could reach?
p('')
p('=== 3. BoardCheck instances and externs anywhere in the tree ===')
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.cpp', '.h', '.hpp')):
            continue
        fp = os.path.join(dp, f)
        t = txt(fp)
        rel = os.path.relpath(fp, ROOT)
        for i, l in enumerate(t.split('\n')):
            if re.search(r'\bBoardCheck\b', l) and re.search(r'\bextern\b|^\s*BoardCheck\s+\w+\s*;|\bnew\s+BoardCheck\b|\bBoardCheck\s+\w+\s*\(', l):
                p('  %-26s %5d| %s' % (rel, i + 1, l.strip()[:120]))
        if 'BoardCheck' in t:
            n = len(re.findall(r'\bBoardCheck\b', t))
            if n and rel not in ('source\\BoardCheck.h', 'source\\BoardCheck.cpp'):
                p('  (mentions) %-26s %d' % (rel, n))

# --- does anything outside BoardCheck.* mention CBC_log / bc_log / test_log ?
p('')
p('=== 4. users of CBC_log / bc_log / test_log outside BoardCheck.* ===')
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.cpp', '.h', '.hpp')):
            continue
        fp = os.path.join(dp, f)
        rel = os.path.relpath(fp, ROOT)
        if rel.lower().endswith(('boardcheck.h', 'boardcheck.cpp')):
            continue
        t = txt(fp)
        for k in ('CBC_log', 'bc_log', 'test_log'):
            if re.search(r'\b' + k + r'\b', t):
                p('  %s uses %s' % (rel, k))
p('  (no lines above = no user outside BoardCheck.*)')

open(os.path.join(OUT, 'reach.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c) < 128 for c in x)))
print('[non-ascii suppressed: %d of %d]' % (
    sum(1 for x in out if any(ord(c) >= 128 for c in x)), len(out)))
