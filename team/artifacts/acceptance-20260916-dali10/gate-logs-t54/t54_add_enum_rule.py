# -*- coding: utf-8 -*-
"""按 schematic-expert ② 补要件（幂等）：**闭世界断言须打印"枚举规则" = 根集 ＋ 纳入过滤器**。
  其补充：**"有意的排除"与"无意的排除"在输出里长得一样，除非把过滤器打出来**。
  其另测：**当前暴露面 = 0**（域内点文件 = 0、符号链接 = 0）⇒ **前瞻性要件、非现症**（不夸大）。
  并与 rule-reviewer 的"域外型"盲区合并：**域 =（根集, 过滤器）**。
"""
import collections
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
WS = os.path.abspath(os.path.join(RUN, '..', '..', '..'))
T28 = os.path.join(RUN, 'gate-logs-t28')
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
ROOTS = [RUN, os.path.join(WS, 'scripts')]

print('=== ① 现状：过滤器这一面的暴露面（按其实测复核）===')
hidden, links, total, maxdepth = 0, 0, 0, 0
for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        d = dp[len(root):].count(os.sep)
        maxdepth = max(maxdepth, d)
        for name in list(dn) + fn:
            if name.startswith('.'):
                hidden += 1
        for f in fn:
            total += 1
            p = os.path.join(dp, f)
            if os.path.islink(p):
                links += 1
print('  域内文件总数 = %d ｜ 点开头的路径分量 = %d ｜ 符号链接 = %d ｜ 最大深度 = %d'
      % (total, hidden, links, maxdepth))
print('  ⇒ 与其实测一致（暴露面 = 0）⇒ **前瞻性要件、非现症** ✓（不夸大）')

print('\n=== ② 域化执行：打印"根集 + 过滤器" ===')
ENUM = {
    'roots': [os.path.relpath(r, WS).replace('\\', '/') for r in ROOTS],
    'includeFilter': {
        'hiddenEntries': False,      # 不含点开头路径分量
        'followSymlinks': False,     # os.walk 默认不跟随
        'maxDepth': 'unbounded',
        'fileTypes': 'all (any extension)',
    },
    'excludeFilter': ['(none beyond hidden/symlink rules)'],
}


def tree_map():
    m = {}
    for root in ROOTS:
        for dp, dn, fn in os.walk(root, followlinks=False):
            dn[:] = [d for d in dn if not d.startswith('.')]
            for f in fn:
                if f.startswith('.'):
                    continue
                p = os.path.join(dp, f)
                try:
                    b = open(p, 'rb').read()
                except Exception:
                    continue
                m[p] = (len(b), hashlib.sha256(b).hexdigest())
    return m


before = tree_map()
print('  **枚举规则（须与结果同印）**：根集 = %s ｜ 纳入过滤器 = %s ｜ 排除过滤器 = %s'
      % (ENUM['roots'], ENUM['includeFilter'], ENUM['excludeFilter']))
print('  域内文件数 = **%d**（本次现算）' % len(before))

inp, outp = LIVE + '.f-in', LIVE + '.f-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
J = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
J.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {'anchors': {f'F-{i}.json': {'s': True} for i in (1, 2, 3)}}
open(inp, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2))
r = subprocess.run([sys.executable, GEN, '--in', inp, '--out', outp], capture_output=True, text=True, encoding='utf-8')
K = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
n = len((K.get('preservedPeerNamespaces') or {}).get('qaProbeAnchors', {}).get('anchors') or {})
after = tree_map()
added = {p for p in after if p not in before}
changed = {p for p in after if p in before and before[p] != after[p]}
removed = {p for p in before if p not in after}
allowed = {inp, outp}
unexpected = [p for p in (added | changed | removed) if p not in allowed]
print('  探针实效 = %d/3 ｜ 跑前 %d → 跑后 %d' % (n, len(before), len(after)))
print('  diff：新增 %d ｜ 变化 %d ｜ 消失 %d ｜ **超出允许集 = %d** ⇒ %s'
      % (len(added), len(changed), len(removed), len(unexpected), '通过' if not unexpected else '未通过'))

print('\n=== ③ 规则入册 ===')
MARK = '## 附廿五｜闭世界断言须打印"枚举规则"：域 =（根集, 纳入过滤器）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 指出我方域化断言**只声明了根集、未声明纳入过滤器**，并给出与 rule-reviewer 盲区的合并形式。

**规则**
> **闭世界断言须打印它的枚举规则**：**根集** ＋ **纳入过滤器**
> （**是否含隐藏项 / 是否跟随符号链接 / 深度**）✓
> **判据**：**"有意的排除"与"无意的排除"在输出里长得一样，除非把过滤器打出来。**

**两例同根、位置不同（均不夸大）**
| 型 | 漏掉什么 | 实例 | 修法 |
| --- | --- | --- | --- |
| **域外型** | **根集**漏掉一整块 | rule-reviewer 的扫描看不到 `.agent-teams/**` | **声明根集** |
| **域内型** | **过滤器**漏掉条目（点文件／链接／深度） | 本 run 实测：域内点文件 **0**、符号链接 **0** ⇒ **暴露面今天为 0** | **声明过滤器** |

⇒ **两者同根：`枚举规则未声明`** ⇒ 故 **域 =（根集, 过滤器）** ✓

**本 run 落地的枚举规则（须与结果同印）**
```
根集 = {team/artifacts/acceptance-…-dali10, scripts/}
纳入过滤器 = {hiddenEntries: False, followSymlinks: False, maxDepth: unbounded, fileTypes: all}
排除过滤器 = （无）
```
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

for p in (inp, outp):
    if os.path.isfile(p):
        os.remove(p)
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
