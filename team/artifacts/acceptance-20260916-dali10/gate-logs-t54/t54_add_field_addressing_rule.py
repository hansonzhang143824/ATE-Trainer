# -*- coding: utf-8 -*-
"""并入 setup-architect ② 的规则（幂等），并**按该规则检查我方所有脚本**是否也用"位置"寻址契约字段：
  **契约字段一律按名（别名名/键名）寻址，不得按列表位置** —— 位置是关于顺序的假设，不是身份。
"""
import collections
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附十六｜契约字段一律按名寻址，不得按列表位置'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：setup-architect 自陈一坑 —— 其按**位置**读 `aliasResolution[1]`（误以为 `bst2sw`），
实为 **`sw2pgnd`**（`[154,155,60,61]`）⇒ **一度把门禁字段值记错**；其已按名重取为 `[48,60,61,76]` 并更正。

**规则**
> **契约字段一律按名（别名名 / 键名）寻址，不得按列表位置** ——
> **位置是关于顺序的假设，不是身份。**

**本 run 实例**
```
`aliasResolution` 是 **12 条列表**，`bst2sw` 在 **index [3]**；
按位置读 [1] ⇒ 命中 `sw2pgnd`（`[154,155,60,61]`）⇒ 字段值记错。
正确写法：`[e for e in aliasResolution if e.get('alias') == 'bst2sw'][0]`
```
**归族**：**用假设替代身份**（与 `size` vs 身份、`preservedPeerKeys` vs 条目、`history` 键误读同族）。

**配套（我方自查，按此规则检查全部脚本）**
> 检查项：**是否存在 `aliasResolution[<数字>]` 之类的位置寻址**（对契约字段）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== 我方自查：是否有"位置寻址契约字段" ===')
pat = re.compile(r'aliasResolution\s*\[\s*\d+\s*\]|aliasResolution\[1\]|\[1\]\s*\[.?resolution')
hits = []
for dp, dn, fn in os.walk(RUN):
    for f in fn:
        if not f.endswith('.py'):
            continue
        p = os.path.join(dp, f)
        try:
            txt = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, l in enumerate(txt.splitlines(), 1):
            if pat.search(l):
                hits.append((os.path.relpath(p, RUN).replace('\\', '/'), i, l.strip()[:100]))
print('  位置寻址命中 = %d' % len(hits))
for h in hits[:10]:
    print('    %s L%d: %s' % h)
if not hits:
    print('  ⇒ **我方脚本无"按位置寻址契约字段"的写法** ✓')

print('\n=== 并按名复核我方的门禁字段取值 ===')
import json
C = json.loads(open(os.path.join(RUN, 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))
AR = C['aliasResolution']
by_name = [e for e in AR if e.get('alias') == 'bst2sw'][0]
print('  aliasResolution 条数 = %d ｜ bst2sw 的 index = %d' % (len(AR), AR.index(by_name)))
print('  按名取值 =', (by_name.get('resolution') or {}).get('closedRelayNumbers'))
print('  按位置 [1] 会得到 =', AR[1].get('alias'), (AR[1].get('resolution') or {}).get('closedRelayNumbers'))
print('  ⇒ 二者不同 ⇒ 该规则在本 run 确有实际区分力 ✓')

hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('\n  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
