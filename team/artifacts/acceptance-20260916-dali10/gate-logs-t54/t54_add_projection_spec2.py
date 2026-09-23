# -*- coding: utf-8 -*-
"""按 schematic-expert ② 实现（幂等、且**用三引号避免引号嵌套陷阱**）：
  (a) 收据新增结构化 `projectionSpec = {exclude, version, note}` —— 投影必须**带版本**；
  (b) 收据并列**三哈希 + 各自的不变性**；
  (c) 其"1 行前置动作"：改完先 `ast.parse`（本脚本自身即示范）。
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')

src = io.open(GEN, encoding='utf-8-sig').read()
try:
    ast.parse(src)
    print('① ast.parse 前置检查：生成器语法 OK')
except SyntaxError as e:
    print('① ast.parse 前置检查：**语法错误** → %s' % e)
    sys.exit(1)

t = src
print('生成器 %d B ; 已含 projectionSpec = %s' % (os.path.getsize(GEN), 'projectionSpec' in t))

if 'projectionSpec' in t:
    print('  已含（幂等）')
else:
    OLD = "    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据'"
    NEW = '''    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据',
    # ⚠️ 投影必须带版本：否则「同名同形 != 同定义」，跨版本比对会静默混用（schematic-expert 指出）
    'projectionSpec': {
        'exclude': ['generatedAt'],
        'version': 1,
        'note': '跨秒不变；跨版本不可混用 —— 排除表一变就必须换版本号（v2），不得沿用同名键',
    },
    # 三哈希一表 + 各自抽象掉了什么（读者据此选对比较口径）
    'hashInvariance': {
        'sha256': '逐字节同盘身份（含 generatedAt ⇒ 跨次重生成会变）',
        'sha256_lf_normalized': '行尾不变（跨编辑器 / CRLF-LF 可比）',
        'reproducibleBodySha256': '时间戳不变（跨秒/跨次可比；用于判内容是否变）',
    },'''
    if OLD not in t:
        print('  WARN: 锚点未命中')
    else:
        t = t.replace(OLD, NEW, 1)
        try:
            ast.parse(t)                    # (c) 改完立即炸，而不是跑到一半
            io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
            print('  已加入 projectionSpec + hashInvariance → %d B' % os.path.getsize(GEN))
        except SyntaxError as e:
            print('  **改动引入语法错误，已放弃写入** → %s' % e)
            sys.exit(1)

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tail[-1][:80] if tail else (r.stderr or '')[:130]))

REC = os.path.join(HERE, 'build-report.receipt.json')
rec = json.load(io.open(REC, encoding='utf-8-sig'))
print('\n=== 收据核对 ===')
print('  键 =', list(rec.keys()))
print('  projectionSpec =', rec.get('projectionSpec'))
print('  hashInvariance 键 =', list((rec.get('hashInvariance') or {}).keys()))
