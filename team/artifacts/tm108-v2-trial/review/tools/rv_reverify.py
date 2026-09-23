# -*- coding: utf-8 -*-
import os, re, hashlib, json, shutil, time

LIVE = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
R = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
OUT = os.path.join(R, 'tools', 'out')
MAN = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\implementation-manifest.json'
OLD = os.path.join(R, 'copy', 'test.cpp')            # reviewed revision b79b911a
NEW = os.path.join(R, 'copy', 'test.cpp.r2-live')    # newly observed live revision

raw = open(LIVE, 'rb').read()
h = hashlib.sha256(raw).hexdigest()
open(NEW, 'wb').write(raw)
print('LIVE test.cpp captured: bytes=%d sha256=%s' % (len(raw), h))
print('  mtime=%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(LIVE).st_mtime)))
print('  preserved reviewed revision still at copy/test.cpp:',
      hashlib.sha256(open(OLD, 'rb').read()).hexdigest()[:16])
print('  saved new revision to copy/test.cpp.r2-live')
print()

t = raw.decode('utf-8-sig')
lines = t.split('\n')
lines = [x[:-1] if x.endswith('\r') else x for x in lines]
if lines and lines[-1] == '':
    lines = lines[:-1]

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
            if c == '\\':
                i += 1
                if i < n: o.append(text[i])
            elif c == '"': st = 'code'
        elif st == 'chr':
            o.append(c)
            if c == '\\':
                i += 1
                if i < n: o.append(text[i])
            elif c == "'": st = 'code'
        elif st == 'line':
            if c == '\n': st = 'code'; o.append(c)
        elif st == 'block':
            if c == '*' and i + 1 < n and text[i + 1] == '/': st = 'code'; i += 1
        i += 1
    return ''.join(o)

code = strip_comments(t)
print('=== RF-01 RE-VERIFIED against the new live revision ===')
for name in ('SetTestResult', 'GetMeasResult', 'STSGetParam', 'StsGetParam'):
    pass
print('  SetTestResult   raw=%d  in-code calls=%d' % (len(re.findall(r'\bSetTestResult\b', t)),
                                                     len(re.findall(r'\bSetTestResult\s*\(', code))))
print('  GetMeasResult   raw=%d  in-code calls=%d' % (len(re.findall(r'\bGetMeasResult\b', t)),
                                                     len(re.findall(r'\bGetMeasResult\s*\(', code))))
print('  LogData         raw=%d  in-code calls=%d' % (len(re.findall(r'\bLogData\b', t)),
                                                     len(re.findall(r'\bLogData\s*\(', code))))
loglike = sorted(set(m for m in re.findall(r'\b([A-Za-z_]\w*(?:::\w+)?)\s*\(', code)
                     if re.search(r'(?i)log|trace|report|print|record', m)))
print('  log-like callables in CODE across the whole file:', loglike)
print('  SetTestResult sites inside the TM108 span:', len(re.findall(r'SetTestResult', '\n'.join(lines[2192:2315]))))
print()
print('  RF-01 unresolved markers still present in the new revision:')
for probe in ('carried by the trace comments in this function',
              'No placeholder number is ever logged',
              'failureContext',
              'bstSwStatus',
              'sweepGeometry'):
    print('    %-48s %d' % (probe[:48], t.count(probe)))
print()
print('=== RF-02 / RF-03 / RF-04 repairs verified present in the new revision ===')
print('  RF-02 "ASSUMED, NOT verified"                       :', t.count('ASSUMED, NOT verified'))
print('  RF-02 "That behaviour is ASSUMED here and NOT verified":', t.count('That behaviour is ASSUMED here and NOT verified'))
print('  RF-02 old assertion "released implicitly with the cbite scope":', t.count('released implicitly with the cbite scope'))
print('  RF-02 old assertion "the cbite scope ends with the function":', t.count('the cbite scope ends with the function'))
print('  RF-03 "Step 4: Measure" headings present            :', len(re.findall(r'Step 4: Measure', t)))
print('  RF-03 TM108 Step 4 heading                          :', t.count('Step 4: Measure (library AWG ramp, capture on the observation candidate)'))
print()
print('=== comment-only discipline preserved on the new revision ===')
def noncomment(ls):
    o = []
    for l in ls:
        s = l.strip()
        if s == '' or s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
            continue
        o.append(l)
    return o
BK = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before'
bb = open(BK, 'rb').read().decode('utf-8-sig')
bl = bb.split('\n'); bl = [x[:-1] if x.endswith('\r') else x for x in bl]
if bl and bl[-1] == '':
    bl = bl[:-1]
print('  non-comment lines: backup=%d live=%d identical=%s' % (len(noncomment(bl)), len(noncomment(lines)),
                                                              noncomment(bl) == noncomment(lines)))
print('  BOM=%s CRLF=%d bareLF=%d' % (raw[:3] == b'\xef\xbb\xbf', raw.count(b'\r\n'), raw.count(b'\n') - raw.count(b'\r\n')))
print()
print('=== manifest state at this instant ===')
mraw = open(MAN, 'rb').read()
d = json.loads(mraw.decode('utf-8'))
print('  bytes=%d sha256=%s' % (len(mraw), hashlib.sha256(mraw).hexdigest()))
print('  mtime=%s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(MAN).st_mtime)))
print('  changes[0].afterSha256=%s' % d['changes'][0].get('afterSha256'))
print('  binding to the captured live revision holds:', d['changes'][0].get('afterSha256') == h)
print('  deviations:', [x.get('id') for x in d.get('deviations', [])])
print('  openItems :', [x.get('id') for x in d.get('openItems', [])])
print('  selfChecks count:', len(d.get('selfChecks', [])))
