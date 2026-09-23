# -*- coding: utf-8 -*-
"""按 schematic-expert ② 把闭世界断言**域化**（幂等）：
  · 断言**一律把"域 + 文件数"与结果一起打印**（否则"无变化"会被读成**绝对**）；
  · **★ 明确该断言的域不含目标树** ⇒ **它不能作为"落盘"的证据**（须与"四次沙箱 PASS 不是落盘"成对引用）。
"""
import collections
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
WS = os.path.abspath(os.path.join(RUN, '..', '..', '..'))
T28 = os.path.join(RUN, 'gate-logs-t28')
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

SCOPE = [(RUN, '本 run 产物域'), (os.path.join(WS, 'scripts'), 'scripts/')]


def tree_map():
    m = {}
    for root, label in SCOPE:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    b = open(p, 'rb').read()
                except Exception:
                    continue
                m[p] = (len(b), hashlib.sha256(b).hexdigest())
    return m


print('=== 域化执行（域 + 文件数 与结果一起打印）===')
before = tree_map()
DOMAIN = ' ∪ '.join('%s(%s)' % (os.path.relpath(r, WS).replace('\\', '/'), lb) for r, lb in SCOPE)
print('  **域 D = %s**' % DOMAIN)
print('  域内文件数 = **%d**（本次现算）' % len(before))

inp, outp = LIVE + '.cw2-in', LIVE + '.cw2-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
J = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
J.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {
    'anchors': {f'CW2-{i}.json': {'s': True} for i in (1, 2, 3)}}
open(inp, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2))
r = subprocess.run([sys.executable, GEN, '--in', inp, '--out', outp],
                   capture_output=True, text=True, encoding='utf-8')
K = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
n = len((K.get('preservedPeerNamespaces') or {}).get('qaProbeAnchors', {}).get('anchors') or {})
after = tree_map()
added = sorted(p for p in after if p not in before)
changed = sorted(p for p in after if p in before and before[p] != after[p])
removed = sorted(p for p in before if p not in after)
allowed = {inp, outp}
unexpected = [p for p in added + changed + removed if p not in allowed]

print('  探针实效（应 3）= %d ⇒ **仪器已抵达进程** = %s' % (n, n == 3))
print('  跑前 %d → 跑后 %d 文件' % (len(before), len(after)))
print('  diff：新增 %d ｜ 变化 %d ｜ 消失 %d' % (len(added), len(changed), len(removed)))
print('  允许集 = {--in 副本, --out 目标}')


class D(dict):
    pass


assertion = {
    'form': ('**在 域 D = {%s}，你扫时 %d 文件 内，除允许集 {--in 副本, --out 目标} 外，无文件发生 (path,size,sha256) 变化**'
             % (DOMAIN, len(before))),
    'method': '以补集替代枚举：**不需知道生成器还碰哪些通道**（env/cwd/临时/相对路径）',
    'domainFileCount': len(before),
    'result': {'passed': not unexpected, 'unexpectedChanges': [os.path.relpath(p, WS) for p in unexpected]},
    'mustNotBeCitedAs': {
        'landing-evidence': ('★ **本断言的域不含目标树** (D:/PROJECT6-DALI/…) ⇒ '
                             '**它不能作为"落盘"的证据**；须与"沙箱 PASS ≠ 落盘"成对引用。'),
        'absolute-no-change': ('"在域内无变化"**不等于**"全局无变化"⇒ 引用须连同**域与文件数**，'
                               '否则"无变化"会被读成**绝对**（即"0 命中必须带域"应用于本断言自身）。'),
    },
    'excludedFromDomain': {
        '.agent-teams/**': '团队协议状态与消息日志（约 10 文件）',
        'knowledge/**': '约 239 文件',
        'targetTree': 'D:/PROJECT6-DALI/**（**根本不在本会话工作区内**）',
    },
}
print('\n  **断言（域化形式）**：%s' % assertion['form'])
print('  域外（结构上无法覆盖）：.agent-teams/** ｜ knowledge/** ｜ **目标树**')

print('\n=== 写入纪律登记（域化要求）===')
MARK = '### 附十一·补｜闭世界断言必须**域化**：域 + 文件数须与结果一起打印'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

''' + MARK + '''

**来源**：schematic-expert 指出 —— **闭世界断言的强度完全来自它的域**。

**要求**
> **闭世界断言一律把"域 + 文件数"与结果一起打印** ——
> 否则"**无变化**"会被读成 **绝对**（这正是"**0 命中必须带域**"应用于该断言**自身**）。

**本 run 域化结果**
```
域 D = {本 run 产物域, scripts/}，扫时 **1,384** 文件（schematic-expert 其后现算 1,396 ⇒ 方向一致）
  跑前 1,384 → 跑后 1,386；diff：新增 = {--in 副本, --out 目标} ｜ 变化 = 无 ｜ 消失 = 无
  ⇒ **在域内**：除允许集外无变化 ✓
域外（结构上无法覆盖）：`.agent-teams/**`（约 10 文件）｜ `knowledge/**`（约 239 文件）
  ｜ **目标树 `D:/PROJECT6-DALI/…`（根本不在本会话工作区内）**
```

**★ 决策相关（必须成对引用）**
> **该断言的域不含目标树 ⇒ 它不能作为"落盘"的证据**；
> 须与"**四次沙箱 PASS 不是落盘**"**成对引用**（否则有人会用它替代落盘证据）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

for p in (inp, outp):
    if os.path.isfile(p):
        os.remove(p)
print('\n  清理后活档 sha =', hashlib.sha256(open(LIVE, 'rb').read()).hexdigest()[:24])
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
