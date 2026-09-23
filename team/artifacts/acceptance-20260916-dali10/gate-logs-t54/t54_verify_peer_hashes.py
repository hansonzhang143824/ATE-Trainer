# -*- coding: utf-8 -*-
"""独立现算 schematic-expert 六项产物，比对"其申报值"（我方只报 路径+size+是否一致）。"""
import hashlib
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
# 其申报：(文件, 申报 size, 申报 sha256)
CLAIM = [
    ('t42-acm200-pin-attribution.md', 19351, '8883daad0d22e669eeb1dd8038a3ad72591078413aed097473d33949300f4cfb'),
    ('t44-t42-addendum.md', 16257, '30aa1be601c058152688aa6d3def9e53e159898c7dce3a2035f9c0230f687a79'),
    ('t45-l672-section-evidence.md', 14784, '4d8940341f3cb1d28e9d6c03468edd084acdca58127e2817a489062d5f14630b'),
    ('t45-t42-timing-addendum.md', 8978, '5e5bde376e3634e6cb0567832765508277a8c83e0f7f4869e2e94a6a3c92e27a'),
    ('t47-ch5-endpoint-sharing.md', 14019, '81f14d0a82c2543982d407e56634fe71652ef3019309ab21abca15c4def28b96'),
    ('t48-node-convergence-and-precedent.md', 23197, 'ed905bfc8397319f28a2ed75163bfbeb28f7193cacf3b986efb110c3a41aa44a'),
]
print('=== 独立现算 vs 其申报 ===')
allok = True
for name, csize, csha in CLAIM:
    p = os.path.join(RUN, name)
    if not os.path.isfile(p):
        print('  %-42s 文件不存在' % name)
        allok = False
        continue
    d = open(p, 'rb').read()
    h = hashlib.sha256(d).hexdigest()
    ok = (len(d) == csize and h == csha)
    allok &= ok
    print('  %-42s %7d B  与申报一致 = %s' % (name, len(d), '✓' if ok else '✗'))
    if not ok:
        print('        申报 size=%d sha=%s' % (csize, csha[:20]))
        print('        现值  size=%d sha=%s' % (len(d), h[:20]))
print('\n  全部一致 =', allok)
print('  （我方仍不在消息里贴哈希字面；需要值请现算）')
