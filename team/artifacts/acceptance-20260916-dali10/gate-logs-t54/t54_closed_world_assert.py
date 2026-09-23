# -*- coding: utf-8 -*-
"""按 schematic-expert ③④ 落地两条（我方自评：值得机制化）：
  ③ 规则：**"注入零实效"首先是对接线（仪器是否抵达进程）的证据，其次才是对假设的证据**
     —— 在解释 nul 结果之前，必须先验证仪器确实到位。
  ④ **闭世界断言**：沙箱运行前后，除沙箱目录与 `--out` 目标外，工作树内**不得有任何文件的
     (path, size, sha256) 发生变化** ⇒ **不枚举写通道也能覆盖"没想到的通道"**。
     判据（其给出）：**"我隔离了两条通道"是我所知通道的主张；"没有东西被我改动过"是补集的主张
     ⇒ 后者只能用闭世界断言**。
"""
import ast
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
T28 = os.path.join(RUN, 'gate-logs-t28')
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')

# 闭世界范围：工作树内**会被触碰到的可能区域**（本 run 的产物域 + 脚本域）
SCOPE = [RUN, os.path.join(WS, 'scripts')]


def tree_map():
    m = {}
    for root in SCOPE:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    b = open(p, 'rb').read()
                except Exception:
                    continue
                m[p] = (len(b), hashlib.sha256(b).hexdigest())
    return m


print('=== ① 记录规则（写入纪律登记）===')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '### 附十｜"注入零实效"是对接线的证据，其次才是对假设的证据'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已包含（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 由我方一次实测（**只做输出重定向后首跑 ⇒ 注入的 3 条探针 0 条生效**）提出问题。

**事实（我方）**
```
先只加 `--out`（输出重定向）→ 在离线副本注入 3 条第三方前缀条目 → 首跑
结果：`qaProbeAnchors.anchors = 0`、`setupArchitectFreezeAnchors 在 = False`
⇒ 若把它读成"并集路径不保留探针" ⇒ **就是一个假阴性**（本 run 反复出现的那一族）
⇒ 正确读法：**接线问题**（生成器仍读 canonical 活档 ⇒ 探针根本没进进程）
```
**规则（采纳其表述）**
> **"注入零实效"首先是对接线（仪器是否抵达进程）的证据，其次才是对假设的证据** ——
> **在解释 nul 结果之前，必须先验证"仪器确实抵达了进程"**（否则 nul 不可解释）。
**配套动作**：用一个**效果可观测的探针**（本例＝输出里可数的探针条数）区分"接线断"与"机制不保留"。
**同位关系**：与"**先打印容器与条数，再断言『不存在』**"是**一对** ——
那条防"假阴性来自观察者"，本条防"**假阴性来自仪器没接上**"。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== ② 闭世界断言（沙箱实验前后全树 (path,size,sha256) diff）===')
MARK2 = '### 附十一｜闭世界断言：不枚举写通道也能覆盖"没想到的通道"'
t2 = io.open(REG, encoding='utf-8-sig').read()
if MARK2 in t2:
    print('  登记已含（幂等）')
else:
    BLOCK2 = '''

---

''' + MARK2 + '''

**来源**：schematic-expert 指出我方 `--in` + `--out` 只覆盖**已知的两条通道**；
**是否还碰其他通道**（env／cwd／临时文件／相对路径配置）**双方都未验证** ⇒ 按分诊属**静默类**（部分生效的隔离会给出看似合理的结果）。

**断言（不必枚举）**
> **沙箱运行前后，除沙箱目录与 `--out` 目标之外，工作树内不得有任何文件的 `(path, size, sha256)` 发生变化。**

**实现**：跑前对工作树（本 run 产物域 + `scripts/`）做一次 `(path,size,sha256)` 清单，跑后再做一次，**diff 必须只有沙箱内新增/变化**。

**判据（其给出，我方采纳）**
> **"我隔离了两条通道"是关于我所知通道的主张；"没有东西被我改动过"是关于补集的主张 ——
> 后者只能用闭世界断言。**

**成本**：两次树扫描（本 run 已有同类扫描脚本）。
**落地**：见 `t54_closed_world_assert.py`（本轮实测执行）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t2.rstrip() + BLOCK2)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== ③ 执行闭世界实验（--in/--out 沙箱 + 前后 diff）===')
before = tree_map()
print('  跑前快照 = %d 文件' % len(before))

inp, outp = LIVE + '.cw-in', LIVE + '.cw-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
J = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
J.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {
    'anchors': {f'CW-{i}.json': {'s': True} for i in (1, 2, 3)}}
open(inp, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2))

r = subprocess.run([sys.executable, GEN, '--in', inp, '--out', outp],
                   capture_output=True, text=True, encoding='utf-8')
print('  生成器 exit=%d' % r.returncode)
K = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
n = len((K.get('preservedPeerNamespaces') or {}).get('qaProbeAnchors', {}).get('anchors') or {})
print('  探针实效（应 3）= %d ⇒ **仪器已抵达进程** = %s' % (n, n == 3))

after = tree_map()
print('  跑后快照 = %d 文件' % len(after))
changed, added, removed = [], [], []
for p in set(before) | set(after):
    if p not in before:
        added.append(p)
    elif p not in after:
        removed.append(p)
    elif before[p] != after[p]:
        changed.append(p)
allowed = {inp, outp}
print('\n  --- 闭世界 diff ---')
print('  新增 = %s' % [os.path.relpath(p, RUN) for p in sorted(added)])
print('  变化 = %s' % [os.path.relpath(p, RUN) for p in sorted(changed)])
print('  消失 = %s' % [os.path.relpath(p, RUN) for p in sorted(removed)])
unexpected = [p for p in set(added) | set(changed) | set(removed) if p not in allowed]
print('\n  **允许集 = {--in, --out} 两个沙箱路径**')
print('  **超出允许集的变化 = %s**' % ([os.path.relpath(p, RUN) for p in unexpected] if unexpected else '（无）'))
print('  ⇒ **闭世界断言 = %s**' % ('通过' if not unexpected else '**未通过**'))

for p in (inp, outp):
    if os.path.isfile(p):
        os.remove(p)
print('\n  已清理沙箱输入/输出；活档 sha =', hashlib.sha256(open(LIVE, 'rb').read()).hexdigest()[:24])
