# -*- coding: utf-8 -*-
"""按 rule-reviewer ① 处置我方生成器输出里的 `mirrorSize` 活体漂移（采纳其建议 (c)）：
  · 改名 `mirrorSizeAtMirrorTime` + 同址加 `mirrorSizeNote: value expires; recompute`
  · **顺带**在本次（已因其它原因进行的）写入中处理；**不另触发额外写入**
  · **处置前不动它、也不据此改任何结论**：本脚本先记录漂移证据，再改生成器，再验证
"""
import ast
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')

print('=== ① 漂移证据（处置前，先取证）===')
A = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
saa = (A.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors') or {}
mir = os.path.join(T28, 'setupArchitect-freeze-snapshots.json')
cur = os.path.getsize(mir) if os.path.isfile(mir) else None
print('  mirrorOf    =', saa.get('mirrorOf'))
print('  mirrorSize  =', saa.get('mirrorSize'), '（记死值）')
print('  镜像现盘 size =', cur)
print('  ⇒ 漂移 =', (cur - saa['mirrorSize']) if (saa.get('mirrorSize') and cur) else 'n/a', 'B')

print('\n=== ② 改生成器（建议 (c)：改名 + 失效声明）===')
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
OLD_A = "                    merged['setupArchitectFreezeAnchors']['mirrorSize'] = os.path.getsize(os.path.join(HERE, f))"
NEW_A = ("                    merged['setupArchitectFreezeAnchors']['mirrorSizeAtMirrorTime'] = os.path.getsize(os.path.join(HERE, f))\n"
         "                    merged['setupArchitectFreezeAnchors']['mirrorSizeNote'] = (\n"
         "                        'value expires; recompute —— 该值是**镜像时刻**的 size，不构成该文件的现身份；'\n"
         "                        '引用请以 全路径 + 当次现算 sha256 为准')\n"
         "                    merged['setupArchitectFreezeAnchors']['mirrorAt'] = (\n"
         "                        __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'))")
if 'mirrorSizeAtMirrorTime' in src:
    print('  生成器已含（幂等）')
elif OLD_A in src:
    src2 = src.replace(OLD_A, NEW_A, 1)
    ast.parse(src2)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(src2)
    print('  已改 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中，打印上下文：')
    i = src.find('mirrorSize')
    print(repr(src[i - 200:i + 120]) if i > 0 else '（未找到 mirrorSize）')

print('\n=== ③ 顺带写入一次（本次写入同时消化其它内容；不额外再写）===')
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  exit=%d ; %s' % (r.returncode, (r.stdout or '').strip().splitlines()[0][:80] if r.stdout else r.stderr[:120]))

B = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
saa2 = (B.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors') or {}
print('\n=== ④ 处置后自证 ===')
print('  子键 =', list(saa2.keys()))
print('  mirrorSizeAtMirrorTime =', saa2.get('mirrorSizeAtMirrorTime'))
print('  mirrorAt               =', saa2.get('mirrorAt'))
print('  mirrorSizeNote 含失效声明 =', 'value expires' in str(saa2.get('mirrorSizeNote')))
print('  旧键 mirrorSize 是否已移除 =', 'mirrorSize' not in saa2)
print('  entries =', len(B['anchors']), '｜ 他方条数 =', len((saa2.get('anchors') or {})))
print('  文件 = %d B' % os.path.getsize(LIVE))
