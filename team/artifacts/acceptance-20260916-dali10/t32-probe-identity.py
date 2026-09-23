# -*- coding: utf-8 -*-
"""t32 probe 4: review-vs-deployed identity check, manifest claims vs disk, gate log attribution."""
import os, sys, json, re, hashlib
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RD = os.path.join(ROOT, 'team', 'artifacts', RUN)
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

print('=== A. chain of hashes: every claimed revision of the implementation ===')
claims = []
# t20 apply record
a = json.loads(rt(os.path.join(RD, 't20-apply-verification.json')))
claims.append(('t20-apply-verification.json before/after', a.get('before', {}).get('sha256'), a.get('after', {}).get('sha256')))
# t23
for n in ('t23-apply-result.json', 't23-apply-verification.json'):
    p = os.path.join(RD, n)
    if os.path.exists(p):
        j = json.loads(rt(p))
        s = json.dumps(j, ensure_ascii=False)
        hs = sorted(set(re.findall(r'\b[0-9a-f]{64}\b', s)))
        claims.append((n, hs, None))
# t29 documented
claims.append(('t29-k110-evidence.md documented payload hashes', ['73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e',
                                                                  '444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c'], None))
for c in claims:
    print('  %-52s %s' % (c[0], json.dumps(c[1:], ensure_ascii=False)[:220]))

live_payload = sha(os.path.join(RD, 'implementation-payload-TM600-TM601.cpp'))
live_target = sha(os.path.join(TARGET, 'source', 'test.cpp'))
print('  %-52s %s' % ('LIVE implementation-payload...cpp', live_payload))
print('  %-52s %s' % ('LIVE target test.cpp', live_target))

print()
print('=== B. manifest claims vs disk ===')
man = os.path.join(RD, 'implementation-manifest.json')
mj = json.loads(rt(man))
mtext = json.dumps(mj, ensure_ascii=False)
print('  manifest', os.path.getsize(man), sha(man)[:16])
for probe, label in [('15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a', 'deployed 15c7d2b8'),
                     ('73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e', 'payload t29 73b511b7'),
                     ('3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479', 't20-after 3dbceb49'),
                     ('5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317', 'baseline 5c9cb3f9')]:
    print('  manifest contains %-22s %s' % (label, probe in mtext))
for k in ('files', 'changedFiles', 'artifacts', 'hashes', 'target', 'writeTarget', 'evidence'):
    if k in mj:
        v = mj[k]
        print('  manifest.%s: %s' % (k, (json.dumps(v, ensure_ascii=False)[:200] if not isinstance(v, list) else 'list len %d' % len(v))))

print()
print('=== C. gate log attribution (which revision did the gates see?) ===')
gl = os.path.join(RD, 'gate-logs-t25')
for n in ('run-gates-stdout.log',):
    p = os.path.join(gl, n)
    if os.path.exists(p):
        t = rt(p)
        print('  ', n, os.path.getsize(p), sha(p)[:16])
        for l in t.splitlines()[:25]:
            if l.strip(): print('     ', l.strip()[:150])
rt_log = os.path.join(gl, 'relay-trace.log')
if os.path.exists(rt_log):
    t = rt(rt_log)
    print('  relay-trace.log', os.path.getsize(rt_log), sha(rt_log)[:16])
    for l in t.splitlines():
        if re.search(r'PASSED|FAIL|FR-001|逆|warn|TM601|TM600', l, re.I):
            print('     ', l.strip()[:160])

print()
print('=== D. does the review target identity match the deployed file? ===')
t24 = rt(os.path.join(RD, 'review', 't24-implementation-review.md'))
hash_in_review = sorted(set(re.findall(r'\b[0-9a-f]{64}\b', t24)))
print('  hashes cited in t24 review:', json.dumps(hash_in_review, ensure_ascii=False))
print('  deployed in review?', live_target in hash_in_review, '| payload in review?', live_payload in hash_in_review)
for l in t24.splitlines():
    if re.search(r'L20[0-9]|L37[0-9]|K57|K109|K110|payload|36381|签名|hash', l):
        print('     ', l.strip()[:150])
