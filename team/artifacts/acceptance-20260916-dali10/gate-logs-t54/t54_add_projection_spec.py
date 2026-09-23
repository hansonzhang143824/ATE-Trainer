# -*- coding: utf-8 -*-
"""按 schematic-expert ② 实现（幂等）：
  (a) 收据新增**结构化** `projectionSpec = {exclude, version, note}` —— 投影必须**带版本**，
      否则"同名同形 ≠ 同定义"，跨版本比对会**静默混用**；
  (b) 收据并列**三哈希 + 各自的不变性**（sha256=逐字节 / lf_normalized=行尾不变 / body=时间戳不变）；
  (c) 其"1 行前置动作"：改完先 `ast.parse` 再跑 ⇒ 把"跑到一半才炸"变成"改完就炸"（压缩不可跑窗口）。
"""
import ast
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')

# (c) 先做语法前置检查（对本脚本自身即将修改的目标）
src = io.open(GEN, encoding='utf-8-sig').read()
try:
    ast.parse(src)
    print('① ast.parse 前置检查：生成器语法 OK')
except SyntaxError as e:
    print('① ast.parse 前置检查：**语法错误** → %s' % e)
    sys.exit(1)

t = src
print('生成器 %d B ; 已含 projectionSpec = %s' % (os.path.getsize(GEN), 'projectionSpec' in t))

if 'projectionSpec' not in t:
    OLD = "    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据'"
    NEW = ("    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据',\n"
           "    # ⚠️ 投影必须**带版本**：否则『同名同形 ≠ 同定义』，跨版本比对会**静默混用**（schematic-expert 指出）\n"
           "    'projectionSpec': {\n"
           "        'exclude': ['generatedAt'],\n"
           "        'version': 1,\n"
           "        'note': '跨秒不变；**跨版本不可混用** —— 排除表一变就必须换版本号（v2），不得沿用同名键',\n"
           "    },\n"
           "    # 三哈希一表 + 各自抽象掉了什么（读者据此选对比较口径）\n"
           "    'hashInvariance': {\n"
           "        'sha256': '**逐字节**同盘身份（含 generatedAt ⇒ **跨次重生成会变**）',\n"
           "        'sha256_lf_normalized': '**行尾不变**（跨编辑器 / CRLF↔LF 可比）',\n"
           "        'reproducibleBodySha256': '**时间戳不变**（跨秒/跨次可比；用于判"内容是否变"）',\n"
           "    },")
    if OLD in t:
        tar = ast.parse(t)
        t = t.replace(OLD, NEW, 1)
        try:
            ast.parse(t)                       # (c) 再验一次，改完立即炸而不是跑到一半
            io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
            print('  已加入 projectionSpec + hashInvariance → %d B' % os.path.getsize(GEN))
        except SyntaxError as e:
            print('  **改动引入语法错误，已放弃写入** → %s' % e)
            sys.exit(1)
    else:
        print('  WARN: 锚点未命中')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tail[-1][:80] if tail else (r.stderr or '')[:130]))

import json
REC = os.path.join(HERE, 'build-report.receipt.json')
rec = json.load(io.open(REC, encoding='utf-8-sig'))
print('\n=== 收据核对 ===')
print('  键 =', list(rec.keys()))
print('  projectionSpec =', rec.get('projectionSpec'))
print('  hashInvariance 键 =', list((rec.get('hashInvariance') or {}).keys()))
