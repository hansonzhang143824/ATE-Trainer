# -*- coding: utf-8 -*-
"""核实 rule-reviewer ③④：我的 postReplace 日志是否用旧 payload；现盘两态是否都符合预期。"""
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))
import verify_relay_trace as V  # noqa: E402

PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
CON = os.path.join(RUN, 'setup-contract.json')
LOG = os.path.join(RUN, 'gate-logs-t33', 't33-postreplace-expectation.log')

print('=== ① 我的 postReplace 日志用的是哪版 payload ===')
t = io.open(LOG, encoding='utf-8-sig', errors='replace').read()
for l in t.splitlines()[:8]:
    print('  ', l.strip()[:130])

print('\n=== ② 现盘两态 ===')
for l, p in (('payload', PAY), ('部署态', DEP)):
    d = open(p, 'rb').read()
    print('  %-6s %8d B  %s' % (l, len(d), hashlib.sha256(d).hexdigest()[:24]))

print('\n=== ③ 契约现盘 ===')
cd = open(CON, 'rb').read()
C = json.loads(cd.decode('utf-8-sig')) if False else __import__('json').loads(cd.decode('utf-8-sig'))
print('  revision = %s ; size = %d B' % (C.get('revision'), len(cd)))
b = [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
print('  bst2sw.closedRelayNumbers =', (b.get('resolution') or {}).get('closedRelayNumbers'))

print('\n=== ④ 两态对期望的满足度（现算）===')


def seton_nums(path):
    x = io.open(path, encoding='utf-8-sig', errors='replace').read()
    out = {}
    for fn, blk in V.fn_blocks(x):
        s = set()
        for r in V.parse_setons(blk):
            m = re.match(r'K(\d+)_', r)
            if m:
                s.add(int(m.group(1)))
            elif re.fullmatch(r'\d+', r):
                s.add(int(r))
        out[fn] = s
    return out


idx = {}
for e in (C.get('aliasResolution') or []):
    a = str(e.get('alias', ''))
    n = set()
    for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []):
        n.add(x) if isinstance(x, int) else n.update(int(y) for y in re.findall(r'\d+', str(x)))
    u = set()
    for x in (e.get('usedByTm') or []):
        u |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    idx[a] = (n, u)


def exp(base):
    d = C['tmDeltas'][base]
    o = set()
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        o |= idx.get(a, (set(), set()))[0]
    for a, (n, u) in idx.items():
        if base in u:
            o |= n
    return o


dep, pay = seton_nums(DEP), seton_nums(PAY)
for tm, base in (('TM600_HS_RDSON', 'TM600'), ('TM601_LS_RDSON', 'TM601')):
    e = exp(base)
    print('  %-16s exp=%-24s 部署态 missing=%-12s payload missing=%s'
          % (tm, sorted(e), sorted(e - dep.get(tm, set())), sorted(e - pay.get(tm, set()))))
