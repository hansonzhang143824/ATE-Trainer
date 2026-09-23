# -*- coding: utf-8 -*-
"""判定：我哪些产物里仍写着"ACM 脚路线由 K110 单独完成/必须 SetOn"（t42/t44 已推翻的表述）。

只读检索，列出文件 + 行 + 上下文，供精确更正（不整篇改写）。
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')

PATTERNS = [
    r'K110 单独完成',
    r'由 K110 单独',
    r'ACM 脚路线由 K110',
    r'ACM 到 BST 由 K110',
    r'必须 SetOn',
    r'K110 必须',
]
ROOTS = [os.path.join(RUN, 'gate-logs-t33'), os.path.join(RUN, 'gate-logs-t30'),
         os.path.join(RUN, 'gate-logs-t28')]

print('=== 检索我方产物 ===')
hits = 0
for root in ROOTS:
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        if not os.path.isfile(p) or not f.endswith(('.md', '.json', '.txt', '.log', '.py')):
            continue
        try:
            t = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            for pat in PATTERNS:
                if re.search(pat, line):
                    print('  %-34s L%-5d %s' % (f, i, line.strip()[:130]))
                    hits += 1
                    break
print('  命中 %d 行' % hits)

print('\n=== 对照：t42/t44 的判定（对方产物）===')
for f in ('t42-acm200-pin-attribution.md', 't44-t42-addendum.md'):
    p = os.path.join(RUN, f)
    if os.path.isfile(p):
        d = open(p, 'rb').read()
        import hashlib
        print('  %-34s %8d B / %s' % (f, len(d), hashlib.sha256(d).hexdigest()[:16]))
