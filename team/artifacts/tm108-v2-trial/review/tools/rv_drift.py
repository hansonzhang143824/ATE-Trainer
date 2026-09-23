# -*- coding: utf-8 -*-
import os, hashlib, difflib, time, json

LIVE = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
COPY = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\copy\test.cpp'
MAN = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\implementation-manifest.json'
BACK = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before'

def rb(p):
    return open(p, 'rb').read()

def L(p):
    t = rb(p).decode('utf-8-sig')
    x = t.split('\n')
    y = [z[:-1] if z.endswith('\r') else z for z in x]
    if y and y[-1] == '':
        y = y[:-1]
    return y

print('=== 1. identity and mtimes ===')
for p in (LIVE, COPY, MAN, BACK):
    b = rb(p)
    st = os.stat(p)
    print('  %-28s %8d  sha256=%s' % (os.path.basename(p), len(b), hashlib.sha256(b).hexdigest()))
    print('      mtime=%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)))
print()
print('=== 2. has the live file changed since my reviewed copy? ===')
print('  live == reviewed copy :', rb(LIVE) == rb(COPY))
print()
print('=== 3. manifest self-consistency now ===')
d = json.loads(rb(MAN).decode('utf-8'))
live_h = hashlib.sha256(rb(LIVE)).hexdigest()
print('  manifest changes[0].afterSha256 =', d['changes'][0].get('afterSha256'))
print('  live test.cpp sha256            =', live_h)
print('  BINDING HOLDS                   =', d['changes'][0].get('afterSha256') == live_h)
print('  manifest sizeAfter field        =', d['changes'][0].get('sizeAfter'), '| live size', len(rb(LIVE)))
print('  manifest deviations ids         =', [x.get('id') for x in d.get('deviations', [])])
print('  manifest openItems count        =', len(d.get('openItems', [])))
print('  has scopeCorrection-ish keys?   =', sorted(k for k in d.keys() if 'orrect' in k or 'evision' in k or 'mend' in k))
print()
print('=== 4. what changed in test.cpp (reviewed copy -> live), summary ===')
A = L(COPY)
B = L(LIVE)
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
print('  changed blocks: %d' % len(ops))
for t, i1, i2, j1, j2 in ops:
    print('   %-8s copy[%d:%d] -> live[%d:%d]' % (t, i1 + 1, i2, j1 + 1, j2))
print()
print('  --- added/changed live lines (first 60) ---')
n = 0
for t, i1, i2, j1, j2 in ops:
    for k in range(j1, j2):
        if n < 60:
            print('   live %5d| %s' % (k + 1, B[k].rstrip()[:150]))
            n += 1
print('  total changed live lines: %d' % sum(j2 - j1 for t, i1, i2, j1, j2 in ops))
print()
print('=== 5. does the live TM108 span still lack a Step 4 heading? ===')
sig = [i + 1 for i, l in enumerate(B) if 'DUT_API int TM108_HSKP_VAC1_PRST' in l]
print('  TM108 signature still unique at line(s):', sig)
if sig:
    lo, hi = sig[0] - 50, sig[0] + 140
    for k in range(lo, min(hi, len(B)) + 1):
        if 'Step 4' in B[k - 1] or 'Step 5' in B[k - 1] or 'P4 rising sweep' in B[k - 1]:
            print('   live %5d| %s' % (k, B[k - 1].rstrip()[:150]))
print()
print('=== 6. does the live file still contain the RF-01 logPlan comment claim? ===')
t = rb(LIVE).decode('utf-8-sig')
for probe in ('carried by the trace comments in this function',
              'No placeholder number is ever logged',
              'the cbite scope ends with the function',
              'released implicitly with the cbite scope'):
    print('  %-46s %d' % (probe[:46], t.count(probe)))
print()
print('=== 7. non-comment sequence: does the live file still match the pre-change backup? ===')
def noncomment(lines):
    out = []
    for l in lines:
        s = l.strip()
        if s == '' or s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
            continue
        out.append(l)
    return out
print('  live non-comment lines:', len(noncomment(B)), ' backup:', len(noncomment(L(BACK))),
      ' identical sequence:', noncomment(B) == noncomment(L(BACK)))
