# -*- coding: utf-8 -*-
"""① 按 setup-architect ③ 的请求，把 `t34-carrier` / `t34-CARRIER` 纳入我方生成器的
   `DO_NOT_TOUCH_PREFIXES`（尊重其归属声明；不靠改名）。
② 对照实验（验证并集累积**保住当前内容**）：在**离线副本**上人为放入 3 条他方条目 → 重跑生成器
   → 验证：3 条**仍在**、(i) 不丢当前内容。**明确不涉及"恢复历史"**（原理上不可测）。
"""
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28DIR = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
T28GEN = os.path.join(T28DIR, 't28_make_anchors.py')
LIVE = os.path.join(T28DIR, 't28-anchors.json')

print('=== ① 前缀纳入 ===')
src = io.open(T28GEN, encoding='utf-8-sig').read()
OLD = "DO_NOT_TOUCH_PREFIXES = ('setupArchitect-',)"
NEW = ("DO_NOT_TOUCH_PREFIXES = ('setupArchitect-', 't34-carrier', 't34-CARRIER')"
       "  # setup-architect ③：其指针文件一并受保护（不改名、只拦写入）")
if 't34-carrier' in src:
    print('  已含（幂等）')
elif OLD in src:
    io.open(T28GEN, 'w', encoding='utf-8', newline='').write(src.replace(OLD, NEW, 1))
    print('  已纳入 → %s (%d B)' % (os.path.basename(T28GEN), os.path.getsize(T28GEN)))
else:
    print('  WARN: 锚点未命中')
src2 = io.open(T28GEN, encoding='utf-8-sig').read()
for k in ('setupArchitect-', 't34-carrier', 't34-CARRIER'):
    print('    含 %-18s %s' % (k, k in src2))

print('\n=== ② 对照实验（离线副本，验证"不丢当前内容"）===')
# 备份原活档
bak = LIVE + '.pretest-bak'
shutil.copy2(LIVE, bak)
try:
    A = json.load(io.open(LIVE, encoding='utf-8-sig'))
    pp = A.setdefault('preservedPeerNamespaces', {})
    ns = pp.setdefault('setupArchitectFreezeAnchors', {'anchors': {}})
    ns.setdefault('anchors', {})
    injected = ['TESTSENTINEL-1.json', 'TESTSENTINEL-2.json', 'TESTSENTINEL-3.json']
    for k in injected:
        ns['anchors'][k] = {'sentinel': True}
    io.open(LIVE, 'w', encoding='utf-8').write(json.dumps(A, ensure_ascii=False, indent=2))
    before_n = len(json.load(io.open(LIVE, encoding='utf-8-sig'))['preservedPeerNamespaces']
                     ['setupArchitectFreezeAnchors']['anchors'])
    print('  注入后条数 =', before_n, '（原 1 + 注入 3）')

    r = subprocess.run([sys.executable, T28GEN], capture_output=True, text=True, encoding='utf-8')
    print('  重跑生成器:', (r.stdout or '').strip().splitlines()[0] if r.stdout else r.stderr[:120])

    B = json.load(io.open(LIVE, encoding='utf-8-sig'))
    after = B['preservedPeerNamespaces']['setupArchitectFreezeAnchors']['anchors']
    print('  重跑后条数 =', len(after))
    kept = [k for k in injected if k in after]
    print('  注入的 3 条仍在 =', kept)
    print('\n  ⇒ (ii) 不丢当前内容：', '**成立**' if len(kept) == 3 else '**不成立**')
    print('  ⇒ 本实验**只能**证明 (ii)；**不得**引作"恢复历史"（(iii) 原理上不可测）—— 与 rule-reviewer 的判据限定一致。')
finally:
    shutil.copy2(bak, LIVE)
    os.remove(bak)
    print('\n  已还原活档（对照实验不改变我方真源）')
