# -*- coding: utf-8 -*-
"""两处动作：
  ① 记录"用门禁自身函数复算"的结果（比我的等价复现更硬）→ 写入门禁函数复算日志（已由命令产生）
  ② 修 `t28_make_anchors.py`：
     (a) `preservedPeerNamespaces` 改为**并集累积**（不丢子键）——此前把 6~8 条压成 1 条；
     (b) **尊重他方自有文件**：跳过 `setupArchitect-*`（其已把锚点迁到自有文件）。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
GEN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'gate-logs-t28', 't28_make_anchors.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B' % os.path.getsize(GEN))

# ---- (a) 并集累积：改为合并现盘 + 历史两层，且不清空 ----
OLD_MERGE = """        merged = dict(prev.get('preservedPeerNamespaces') or {})
        for k, v in prev.items():
            if k not in OWN_KEYS and k != 'preservedPeerNamespaces':
                merged[k] = v
        merged.pop('preservedPeerNamespaces', None)   # 剔除历史嵌套，避免复跑逐层加深"""
NEW_MERGE = """        merged = {}
        # 1) 先收历史层里**每个子键**（并集累积，避免把多键压成 1 键）
        for k, v in (prev.get('preservedPeerNamespaces') or {}).items():
            if k in ('preservedPeerNamespaces',):
                continue
            merged[k] = v
        # 2) 再收现盘顶层里的他方键（同样逐键并集）
        for k, v in prev.items():
            if k not in OWN_KEYS and k != 'preservedPeerNamespaces':
                merged[k] = v
        # 3) 与他方**自有文件**并集：若他方已迁出，仍保留到此命名空间（只读其文件）
        for f in os.listdir(HERE):
            if f.startswith('setupArchitect-') and f.endswith('.json'):
                try:
                    other = json.loads(io.open(os.path.join(HERE, f), encoding='utf-8-sig').read())
                    merged.setdefault('setupArchitectFreezeAnchors', {})
                    merged['setupArchitectFreezeAnchors']['mirrorOf'] = f
                    merged['setupArchitectFreezeAnchors']['mirrorSize'] = os.path.getsize(os.path.join(HERE, f))
                except Exception:
                    pass"""

if '先收历史层里' in t:
    print('  (a) 已是并集累积（幂等）')
elif OLD_MERGE in t:
    t = t.replace(OLD_MERGE, NEW_MERGE, 1)
    print('  (a) 已改并集累积')
else:
    print('  WARN: (a) 锚点未命中')

# ---- (b) 尊重他方自有文件：生成器不写 setupArchitect-* ----
if 'DO_NOT_TOUCH_PREFIXES' not in t:
    t = t.replace("out = os.path.join(HERE, 't28-anchors.json')",
                  "# 他方自有文件：本生成器**不写入**这些前缀的文件\n"
                  "DO_NOT_TOUCH_PREFIXES = ('setupArchitect-',)\n"
                  "out = os.path.join(HERE, 't28-anchors.json')", 1)
    print('  (b) 已加 DO_NOT_TOUCH_PREFIXES')

io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('  → 生成器现 %d B' % os.path.getsize(GEN))

# ---- 跑两次验证幂等且保住他方键 ----
import subprocess
import sys
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    print('  run%d: %s' % (i, (r.stdout or '').strip().splitlines()[0] if r.stdout else r.stderr[:120]))

A = json.load(io.open(os.path.join(HERE, 't28-anchors.json'), encoding='utf-8-sig'))
pp = A.get('preservedPeerNamespaces') or {}
saa = pp.get('setupArchitectFreezeAnchors') or {}
print('  他方命名空间键 =', list(pp.keys()))
print('  setupArchitectFreezeAnchors 子键 =', list(saa.keys()))
print('  其 anchors 条数 =', len(saa.get('anchors') or {}))
print('  mirrorOf =', saa.get('mirrorOf'), '| mirrorSize =', saa.get('mirrorSize'))
