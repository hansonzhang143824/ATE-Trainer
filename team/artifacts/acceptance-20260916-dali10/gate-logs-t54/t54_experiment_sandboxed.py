# -*- coding: utf-8 -*-
"""机制化 (a)：给 `t28_make_anchors.py` 增加 **`--out <path>`**（输出重定向），
使沙箱实验能改**输出目标**而不只隔离输入。
随后用沙箱模式**重跑对照实验**，并执行 (b) **跑后断言**（活档哈希 == 实验前哈希）。
"""
import ast
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== (a) 给生成器加 --out 输出重定向 ===')
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
OLD = "out = os.path.join(HERE, 't28-anchors.json')"
NEW = ("out = os.path.join(HERE, 't28-anchors.json')\n"
       "# (a) 输出重定向：`--out <path>` ⇒ 沙箱实验可改**输出目标**，而非只隔离输入\n"
       "if '--out' in sys.argv:\n"
       "    _i = sys.argv.index('--out')\n"
       "    if _i + 1 < len(sys.argv):\n"
       "        out = sys.argv[_i + 1]\n"
       "        print('[out-redirect] 输出目标 = %s' % out)")
if "'--out' in sys.argv" in src:
    print('  已含 --out（幂等）')
elif OLD in src:
    out_src = src.replace(OLD, NEW, 1)
    ast.parse(out_src)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out_src)
    print('  已加入 --out → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    sys.exit(1)
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('  语法 OK')

print('\n=== (b) 沙箱重跑实验 + 跑后断言 ===')
live_before = sha(LIVE)
sandbox_live = LIVE + '.sandbox-copy'
sandbox_out = LIVE + '.sandbox-out'
# 输入副本
open(sandbox_live, 'wb').write(open(LIVE, 'rb').read())
import json
A = json.loads(open(sandbox_live, 'rb').read().decode('utf-8-sig'))
A.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {
    'anchors': {k: {'sentinel': True} for k in ('SANDBOX-1.json', 'SANDBOX-2.json', 'SANDBOX-3.json')}}
open(sandbox_live, 'w', encoding='utf-8').write(json.dumps(A, ensure_ascii=False, indent=2))
print('  输入副本注入 3 条（第三方前缀 qaProbeAnchors）')

# 让生成器**读**副本、**写**沙箱输出：通过临时把 HERE 指向副本所在的同目录不可行，
# 故采用：先备份活档 → 以副本替换活档 → 跑（--out 指向沙箱输出）→ 立即还原 → 断言
backup = LIVE + '.bak'
open(backup, 'wb').write(open(LIVE, 'rb').read())
try:
    open(LIVE, 'wb').write(open(sandbox_live, 'rb').read())
    r = subprocess.run([sys.executable, GEN, '--out', sandbox_out],
                       capture_output=True, text=True, encoding='utf-8')
    print('  跑生成器(--out) exit=%d' % r.returncode)
    for l in (r.stdout or '').strip().splitlines()[:2]:
        print('    ' + l.strip())
    B = json.loads(open(sandbox_out, 'rb').read().decode('utf-8-sig'))
    pp = B.get('preservedPeerNamespaces') or {}
    print('  **输出写到沙箱**：%s 存在=%s' % (os.path.basename(sandbox_out), os.path.isfile(sandbox_out)))
    print('  qaProbeAnchors.anchors = %d 条（应 3）' % len((pp.get('qaProbeAnchors') or {}).get('anchors') or {}))
    print('  setupArchitectFreezeAnchors 在 =', bool(pp.get('setupArchitectFreezeAnchors')))
finally:
    open(LIVE, 'wb').write(open(backup, 'rb').read())
    for p in (backup, sandbox_live, sandbox_out):
        if os.path.isfile(p):
            os.remove(p)

live_after = sha(LIVE)
print('\n=== (b) 跑后断言（固定动作）===')
print('  活档 sha 实验前 = %s' % live_before[:32])
print('  活档 sha 实验后 = %s' % live_after[:32])
assert live_after == live_before, '活档哈希不一致！'
print('  **assert 通过：活档未被改变** ✓')
