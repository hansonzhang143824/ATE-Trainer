# Post-stop integrity check: did the forced interruption of t10/t11 damage anything?
import hashlib, json, os, re, difflib

A = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
TGT = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
BK = os.path.join(A, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')
ANCHOR = '15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== 1. target test.cpp ===')
raw = open(TGT, 'rb').read()
txt = raw.decode('utf-8-sig', errors='replace')
L = txt.split('\n')
print('sha256_pl :', hashlib.sha256(raw).hexdigest())
print('bytes     :', len(raw), '| BOM:', raw[:3] == b'\xef\xbb\xbf', '| CRLF:', txt.count('\r\n'),
      '| bare LF:', txt.count('\n') - txt.count('\r\n') - (1 if txt.endswith('\n') else 0))
print('lines     :', len(L))
print('DUT_API   :', len(re.findall(r'DUT_API int ', txt)))
sym = [i + 1 for i, l in enumerate(L) if 'DUT_API int TM108_HSKP_VAC1_PRST' in l]
print('TM108 sym :', sym, '| full signature count:',
      sum(1 for l in L if 'DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)' in l))
# truncation / half-write detection
last = [l for l in L if l.strip()]
print('last 3 non-empty lines:', [l[:60] for l in last[-3:]])
print('ends with closed brace at col 0:', any(l.rstrip('\r') == '}' for l in last[-3:]))

print()
print('=== 2. backup anchors ===')
for tag, p, exp in (('test.cpp.before', BK, ANCHOR),
                    ('sub.cpp.before', os.path.join(A, 'implementation', 'backup', 'tm108-v2-impl__sub.cpp.before'),
                     'e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470')):
    h = sha(p)
    print('%-16s %s intact=%s %d B' % (tag, h[:24], h == exp, os.path.getsize(p)))

print()
print('=== 3. comments-only invariant vs pre-change backup (RF-02/03 edits must keep it) ===')
B = open(BK, 'rb').read().decode('utf-8-sig', errors='replace').split('\n')
strip = lambda X: [x.rstrip('\r') for x in X if x.strip() and not x.strip().startswith('//')]
print('non-comment lines before/after:', len(strip(B)), len(strip(L)), '| identical:', strip(B) == strip(L))
sm = difflib.SequenceMatcher(None, B, L, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
print('changed opcodes:', len(ops), '| after-range:', min(o[3] for o in ops) + 1, '-', max(o[4] for o in ops))

print()
print('=== 4. JSON artifacts parse ===')
for rel in ('implementation/implementation-manifest.json',
            'method/tm108-test-method-contract.json',
            'review/t8-review-findings.json'):
    p = os.path.join(A, rel)
    try:
        d = json.load(open(p, encoding='utf-8'))
        print('OK    %-46s %s %8d B' % (rel.split('/')[-1], sha(p)[:16], os.path.getsize(p)))
    except Exception as e:
        print('FAIL  %-46s %s  (%s)' % (rel.split('/')[-1], sha(p)[:16], e))

print()
print('=== 5. hashes of the artifacts in play ===')
for rel in ('implementation/implementation-manifest.json', 'implementation/t7-selfcheck.md',
            'method/tm108-test-method-contract.md', 'review/t8-review-findings.json',
            'review/t8-review-findings.md'):
    p = os.path.join(A, rel)
    import datetime
    print('%-42s %s %8d B  %s' % (rel.split('/')[-1], sha(p)[:16], os.path.getsize(p),
                                  datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%H:%M:%S')))

print()
print('=== 6. is the manifest still bound to the live file? ===')
try:
    m = json.load(open(os.path.join(A, 'implementation', 'implementation-manifest.json'), encoding='utf-8'))
    after = m['changes'][0]['afterSha256']
    live = hashlib.sha256(raw).hexdigest()
    print('manifest afterSha256:', after[:24])
    print('live               :', live[:24])
    print('BOUND:', after == live)
except Exception as e:
    print('cannot check binding:', e)
