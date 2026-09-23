# -*- coding: utf-8 -*-
"""首次域化执行**未通过**（变化 1 / 超出允许集 1）—— 查明：那是**本脚本自己**在跑断言前写入了
`t54-discipline-register.md`（把规则入册）⇒ **域内含有"断言自身正在写的产物"** ⇒ **自指污染**。

修法（机制化）：**闭世界断言必须把"断言自身会写的路径"计入允许集，或在断言窗口内不写任何东西**
⇒ 本脚本：**先入册（已完成）→ 再在"零写入窗口"内单跑断言**，并打印每个 diff 项（不聚合）。
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
ENUM = {'roots': [os.path.relpath(r, WS).replace('\\', '/') for r in ROOTS],
        'hiddenEntries': False, 'followSymlinks': False, 'maxDepth': 'unbounded'}


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
                    m[p] = (len(open(p, 'rb').read()), hashlib.sha256(open(p, 'rb').read()).hexdigest())
                except Exception:
                    continue
    return m


print('=== 零写入窗口内的域化断言（枚举规则与结果同印）===')
print('  枚举规则：根集 = %s ｜ 过滤器 = %s' % (ENUM['roots'], {k: ENUM[k] for k in ('hiddenEntries', 'followSymlinks', 'maxDepth')}))
before = tree_map()
print('  域内文件数 = %d' % len(before))

inp, outp = LIVE + '.g-in', LIVE + '.g-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
J = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
J.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {'anchors': {f'G-{i}.json': {'s': True} for i in (1, 2, 3)}}
open(inp, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2))
# 注：inp/outp 位于域内 ⇒ 必须计入允许集
r = subprocess.run([sys.executable, GEN, '--in', inp, '--out', outp], capture_output=True, text=True, encoding='utf-8')
K = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
n = len((K.get('preservedPeerNamespaces') or {}).get('qaProbeAnchors', {}).get('anchors') or {})
after = tree_map()

added = sorted(p for p in after if p not in before)
changed = sorted(p for p in after if p in before and before[p] != after[p])
removed = sorted(p for p in before if p not in after)
allowed = {inp, outp}
print('  探针实效 = %d/3 ｜ 跑前 %d → 跑后 %d' % (n, len(before), len(after)))
print('  --- 逐项 diff（不聚合）---')
for tag, items in (('新增', added), ('变化', changed), ('消失', removed)):
    for p in items:
        rel = os.path.relpath(p, RUN).replace('\\', '/')
        print('    %s: %s ｜ 是否在允许集 = %s' % (tag, rel, p in allowed))
unexpected = [p for p in (set(added) | set(changed) | set(removed)) if p not in allowed]
print('  **超出允许集 = %d** ⇒ **闭世界断言 = %s**' % (len(unexpected), '通过' if not unexpected else '未通过'))

for p in (inp, outp):
    if os.path.isfile(p):
        os.remove(p)

print('\n=== 入册：自指污染修法 ===')
MARK = '### 附廿五·补｜闭世界断言的"自指污染"：域内含有断言自身正在写的产物'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

''' + MARK + '''

**事实（我方首次域化执行未通过）**
```
跑前 1,478 → 跑后 1,480：新增 2 ｜ **变化 1** ｜ 消失 0 ⇒ **超出允许集 = 1**
查明：那 1 处变化是**本脚本自己在断言前写入了 `t54-discipline-register.md`**（把规则入册）
  ⇒ **域内含有"断言自身正在写的产物"** ⇒ **自指污染**（**不是被测工具的行为**）
```
**修法（机制化）**
> **闭世界断言必须把"断言自身会写的路径"计入允许集，或在断言窗口内不写任何东西**；
> 且**逐项打印 diff**（不聚合）⇒ 否则"自指污染"与"真实越界"在输出里长得一样。

**同族**：这与"自指字段只能指向过去或被版本钉住"（§附廿三）同根 ——
**断言与它的域若共享可写状态，就会污染自身观测** ✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
