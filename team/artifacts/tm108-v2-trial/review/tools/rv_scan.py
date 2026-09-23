import os, re, json, hashlib

BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
OUT = os.path.join(BASE, 'review', 'tools', 'out')
os.makedirs(OUT, exist_ok=True)
AFTER = os.path.join(BASE, 'review', 'copy', 'test.cpp')
BEFORE = os.path.join(BASE, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')


def load(p):
    with open(p, 'rb') as f:
        b = f.read()
    t = b.decode('utf-8-sig')
    r = t.split('\n')
    L = [x[:-1] if x.endswith('\r') else x for x in r]
    if L and L[-1] == '':
        L = L[:-1]
    return b, t, L


ba, ta, A = load(AFTER)
bb, tb, B = load(BEFORE)
rep = []


def p(*a):
    rep.append(' '.join(str(x) for x in a))


p('=== 1. TM108 body extraction ===')
sigA = [i for i, l in enumerate(A) if 'DUT_API int TM108_HSKP_VAC1_PRST' in l][0] + 1
bodyA = A[sigA - 1:2309]           # 2193..2309
bannerA = A[2148:2192]             # 2149..2192
bodyB = B[2154:2225]               # 2155..2225
bannerB = B[2148:2154]             # 2149..2154
p('after  sig line', sigA, 'body lines', len(bodyA), 'banner lines', len(bannerA))
p('before sig line 2155 body lines', len(bodyB), 'banner lines', len(bannerB))
p('')
p('=== 2. "Step N" headings present in the CHANGED region (before vs after) ===')
for name, lines, lo in (('BEFORE', B, 2149), ('AFTER', A, 2149)):
    for i, l in enumerate(lines):
        if re.search(r'Step\s*\d', l):
            p('  %s line %d: %s' % (name, i + 1, l.strip()))
    p('  --')
p('')
p('=== 3. logging / output primitives in the WHOLE after-file ===')
pats = {
    'SetTestResult': r'SetTestResult',
    'LogData': r'LogData',
    'printf/TRACE/OutputDebugString': r'\b(printf|TRACE|OutputDebugString|cout|fprintf|sprintf)\b',
    'Log/WriteLog/AddLog/LogMessage': r'\b\w*Log\w*\s*\(',
    'CParam decl/usage': r'\bCParam\b',
    'StsGetParam': r'StsGetParam',
}
countsA = {k: len(re.findall(v, ta)) for k, v in pats.items()}
countsB = {k: len(re.findall(v, tb)) for k, v in pats.items()}
for k in pats:
    p('  %-34s before=%-6d after=%-6d' % (k, countsB[k], countsA[k]))
# every distinct call name that looks like a logger, whole file
calls = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_:]*)\s*\(', ta))
loggish = sorted(c for c in calls if re.search(r'(?i)log|trace|report|print|record|output', c))
p('')
p('  distinct callable names matching log|trace|report|print|record|output (whole file):')
p('   ', loggish)
p('  -- occurrences WITH word boundary, whole file:')
for c in loggish:
    p('     %-40s %d' % (c, len(re.findall(r'\b' + re.escape(c) + r'\s*\(', ta))))
p('')
p('=== 4. in-TM logging calls actually present in the TM108 body (after) ===')
p('   SetTestResult occurrences in TM108 body:', len(re.findall(r'SetTestResult', '\n'.join(bodyA))))
for i, l in enumerate(bodyA):
    if re.search(r'SetTestResult|\b\w*Log\w*\(', l):
        p('     %d: %s' % (2193 + i, l.strip()))
p('')
p('=== 5. cbite / relay actuation inventory, WHOLE file ===')
for name, txt in (('before', tb), ('after', ta)):
    p('  %s: SetOn=%d  SetOff=%d  RelayOff=%d  Reset=%d  \\.Off\\(=%d  DelayOff=%d  SetOffAll=%d'
      % (name, len(re.findall(r'SetOn', txt)), len(re.findall(r'SetOff', txt)),
         len(re.findall(r'RelayOff', txt)), len(re.findall(r'\bReset\b', txt)),
         len(re.findall(r'\.Off\s*\(', txt)), len(re.findall(r'DelayOff', txt)),
         len(re.findall(r'SetOffAll', txt))))
p('  cbite token count before=%d after=%d' % (tb.count('cbite'), ta.count('cbite')))
p('')
p('=== 6. K17_BUSL_VAC occurrences, WHOLE file ===')
for name, lines in (('BEFORE', B), ('AFTER', A)):
    hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if 'K17' in l]
    p('  %s: %d hit(s)' % (name, len(hits)))
    for ln, l in hits:
        p('     %d: %s' % (ln, l))
p('')
p('=== 7. relay macro tokens inside TM108 body (after) ===')
toks = re.findall(r'\bK\d+_[A-Za-z0-9_]+', '\n'.join(bodyA))
p('  tokens:', sorted(set(toks)), 'counts:', {t: toks.count(t) for t in sorted(set(toks))})
excl = ['K47', 'K48', 'K57', 'K61', 'K76', 'K109', 'K110', 'K141', 'K142', 'K86', 'K130']
for e in excl:
    p('   %-6s present in body: %s' % (e, bool(re.search(r'\b' + e + r'\b', '\n'.join(bodyA)))))
p('')
p('=== 8. numeric relay literals in TM108 body ===')
for i, l in enumerate(bodyA):
    if re.search(r'SetOn\(|\bK\d+\b', l):
        p('     %d: %s' % (2193 + i, l.strip()))
p('')
p('=== 9. count of DUT_API TM symbols ===')
p('  DUT_API ... ( occurrences:', len(re.findall(r'DUT_API\s+int\s+TM\d+', ta)))
p('  TM108 signature occurrences:', len(re.findall(r'DUT_API int TM108_HSKP_VAC1_PRST', ta)))
p('')
p('=== 10. manifest/selfcheck numeric claims re-checked ===')
def noncomment(lines):
    out = []
    for l in lines:
        s = l.strip()
        if s == '' or s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
            continue
        out.append(l)
    return out
p('  non-comment lines before=%d after=%d (manifest/t7-selfcheck claim 5625/5625)' % (len(noncomment(B)), len(noncomment(A))))
p('  manifest sourceLocationBefore=2154  actual=2155')
p('  manifest sourceLocationAfter =2192  actual=%d' % sigA)
p('')
p('=== 11. K13 / keep-open cross-check against R1 ===')
for name, lines in (('AFTER', A),):
    for i, l in enumerate(lines):
        if 2149 <= i + 1 <= 2309 and re.search(r'K13|K65|K21|K17', l):
            p('     %d: %s' % (i + 1, l.strip()))
p('')
p('=== 12. all distinct numeric literals in TM108 body (contract-traceability input) ===')
nums = set()
for l in bodyA:
    code = re.sub(r'//.*$', '', l)
    for m in re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', code):
        nums.add(m)
p('  ', sorted(nums, key=lambda x: (len(x), x)))
p('')
p('=== 13. 1.65 occurrences whole file ===')
p('  before=%d after=%d' % (tb.count('1.65'), ta.count('1.65')))
for i, l in enumerate(A):
    if '1.65' in l:
        p('     %d: %s' % (i + 1, l.strip()))

open(os.path.join(OUT, 'scan.txt'), 'w', encoding='utf-8').write('\n'.join(rep))
print('\n'.join(rep))
