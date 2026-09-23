# -*- coding: utf-8 -*-
"""（避免引号嵌套：内部引号一律用『』）给 mustNotBeCitedAs 增第二条禁止推论。
"""
import ast
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：生成器语法 OK（%d B）' % len(src.encode('utf-8')))

OLD = "'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'\n                             '属**原理上不可测**。'),"
NEW = (
    "'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'\n"
    "                             '属**原理上不可测**。'\n"
    "                             '⚠️ **亦不得**引作 **(iv) 历史 8→1 丢失之原因** 的证据 —— '\n"
    "                             '本实验测的是**当前生成器行为**，**不说明当年那次丢失由何导致**'\n"
    "                             '（与『当前行为不为历史修订作证』同一时域纪律）。'),"
)
if '亦不得**引作 **(iv)' in src:
    print('  已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已增第二条禁止推论 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    i = src.find('mustNotBeCitedAs')
    print(repr(src[i:i + 240]) if i > 0 else '（未找到）')
    sys.exit(1)

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('重生成末行:', (r.stdout or '').strip().splitlines()[-1][:70] if r.stdout else (r.stderr or '')[:120])
