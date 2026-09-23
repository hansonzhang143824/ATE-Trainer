# -*- coding: utf-8 -*-
"""补一步：生成器在镜像时**显式移除旧键 `mirrorSize`**（它会被并集从历史层带过来 ⇒ 变成"记死的旧尺寸"）。
写前/写后双验（ast.parse），随后顺带写入一次并自证。
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('① 前置：生成器语法 OK（%d B）' % len(src.encode('utf-8')))

OLD = ("                    merged['setupArchitectFreezeAnchors']['mirrorAt'] = (\n"
       "                        __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'))")
NEW = OLD + ("\n                    # ⚠️ 移除**旧键** `mirrorSize`（会随并集从历史层带过来 ⇒ 成为\"记死的旧尺寸\"；活体漂移实例）\n"
             "                    merged['setupArchitectFreezeAnchors'].pop('mirrorSize', None)")

if "pop('mirrorSize'" in src:
    print('  已含移除语句（幂等）')
elif OLD in src:
    src2 = src.replace(OLD, NEW, 1)
    ast.parse(src2)                       # 写前言
    io.open(GEN, 'w', encoding='utf-8', newline='').write(src2)
    print('  已加入移除语句 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    sys.exit(1)

ast.parse(io.open(GEN, encoding='utf-8-sig').read())   # 写后验
print('② 后置：生成器语法 OK')

r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('③ 顺带写入 exit=%d ; %s' % (r.returncode, (r.stdout or '').strip().splitlines()[0][:70] if r.stdout else r.stderr[:120]))

B = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
saa = (B.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors') or {}
print('\n④ 自证')
print('  子键 =', list(saa.keys()))
print('  旧键 mirrorSize 已移除 =', 'mirrorSize' not in saa)
print('  mirrorSizeAtMirrorTime =', saa.get('mirrorSizeAtMirrorTime'), '｜ mirrorAt =', saa.get('mirrorAt'))
print('  失效声明在 =', 'value expires' in str(saa.get('mirrorSizeNote')))
print('  entries =', len(B['anchors']), '｜ 他方条数 =', len(saa.get('anchors') or {}), '｜ 文件 =', os.path.getsize(LIVE), 'B')

# 再跑一次确认幂等（连跑两次应一致，除时间戳/镜像尺寸行）
sig = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    b = open(LIVE, 'rb').read()
    J = json.loads(b.decode('utf-8-sig'))
    s = (J.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors') or {}
    sig.append((len(b), 'mirrorSize' in s, s.get('mirrorSizeAtMirrorTime')))
print('⑤ 连跑两次:', sig, '⇒ 旧键不再出现 =', all(not x[1] for x in sig))
