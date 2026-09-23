# -*- coding: utf-8 -*-
"""修正版：`NEW` 必须**以换行结尾**，否则 `'isFrozen'` 会被粘到 `}` 之后 ⇒ 语法错误。
（这正是"改后先 ast.parse"该拦下的那类；本脚本写入前验、写入后再验。幂等。）
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
ast.parse(src)
print('① 前置检查：生成器语法 OK（%d B）' % len(src.encode('utf-8')))

t = src
if 'projectionSpec' in t:
    print('  已含 projectionSpec（幂等）')
else:
    OLD = "    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据',\n"
    NEW = (
        "    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据',\n"
        "    # 投影必须带版本：否则「同名同形 != 同定义」，跨版本比对会静默混用（schematic-expert 指出）\n"
        "    'projectionSpec': {\n"
        "        'exclude': ['generatedAt'],\n"
        "        'version': 1,\n"
        "        'note': '跨秒不变；跨版本不可混用 —— 排除表一变就必须换版本号（v2），不得沿用同名键',\n"
        "    },\n"
        "    'hashInvariance': {\n"
        "        'sha256': '逐字节同盘身份（含 generatedAt ⇒ 跨次重生成会变）',\n"
        "        'sha256_lf_normalized': '行尾不变（跨编辑器 / CRLF-LF 可比）',\n"
        "        'reproducibleBodySha256': '时间戳不变（跨秒/跨次可比；用于判内容是否变）',\n"
        "    },\n"
    )
    if OLD not in t:
        print('  WARN: 锚点未命中')
        sys.exit(1)
    t2 = t.replace(OLD, NEW, 1)
    try:
        ast.parse(t2)                     # 写入**前**验
        io.open(GEN, 'w', encoding='utf-8', newline='').write(t2)
        print('  已写入 → %d B' % os.path.getsize(GEN))
    except SyntaxError as e:
        print('  **改动引入语法错误，已放弃写入** → line %s: %s' % (e.lineno, e.msg))
        sys.exit(1)

ast.parse(io.open(GEN, encoding='utf-8-sig').read())   # 写入**后**验
print('② 后置检查：生成器语法 OK')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tail[-1][:80] if tail else (r.stderr or '')[:130]))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 收据核对 ===')
print('  键 =', list(rec.keys()))
print('  projectionSpec =', json.dumps(rec.get('projectionSpec'), ensure_ascii=False))
print('  hashInvariance =', json.dumps(rec.get('hashInvariance'), ensure_ascii=False)[:150])
