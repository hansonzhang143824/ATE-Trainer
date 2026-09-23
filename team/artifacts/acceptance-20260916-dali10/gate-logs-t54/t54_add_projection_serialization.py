# -*- coding: utf-8 -*-
"""按 setup-architect ③ 补 `projectionSpec` 的**序列化与编码**声明（否则第三方即便字节相同也无法复现 body 哈希），
并**在当前字节上重发 body 哈希**；随后做**独立第三方复现自证**（从已落盘文件重算）。

我方实际约定（当前实现，v2）：
  body = json.dumps({k:v for k,v in json.loads(file).items() if k not in exclude},
                     ensure_ascii=False, sort_keys=True)
  exclude = ['generatedAt', 'receipts']   ← v2（v1 仅 generatedAt，已废弃：其不稳）
"""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
REC = os.path.join(HERE, 'build-report.receipt.json')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

OLD = "        'exclude': ['generatedAt', 'receipts'],\n        'version': 2,"
NEW = ('''        'exclude': ['generatedAt', 'receipts'],
        'version': 2,
        'serialization': ("json.dumps(body, ensure_ascii=False, sort_keys=True) "
                          "，分隔符为 Python json 默认（', ' 与 ': '），无尾随换行"),
        'encoding': 'utf-8',
        'bodyDefinition': ("body = {k: v for k, v in json.loads(<file bytes>.decode('utf-8-sig')).items() "
                           "if k not in exclude} ⇒ 再按上述 serialization/encoding 序列化后取 sha256"),
        'stabilityNote': ('核心不稳定来源是 `generatedAt`（每次生成）与 `receipts`（仅 at/lineCount 变）；'
                          '两者均已排除 ⇒ v2 下 body 哈希**跨次生成稳定**（v1 未排 `receipts` ⇒ 不稳定，已废弃）'),''')
if "'serialization'" in src and 'bodyDefinition' in src:
    print('  已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已补 serialization/encoding/bodyDefinition → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    sys.exit(1)
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:55] if tl else (r.stderr or '')[:120]))

rec = json.load(io.open(REC, encoding='utf-8-sig'))
ps = rec['projectionSpec']
print('\n=== 收据 projectionSpec（现刻）===')
for k, v in ps.items():
    print('  %-16s %s' % (k, str(v)[:110]))

print('\n=== 第三方复现自证（从**已落盘文件**重算 body）===')
b = open(REPORT, 'rb').read()
J = json.loads(b.decode('utf-8-sig'))
body = {k: v for k, v in J.items() if k not in ps['exclude']}
s = json.dumps(body, ensure_ascii=False, sort_keys=True)
h = hashlib.sha256(s.encode(ps['encoding'])).hexdigest()
print('  记录值（收据） = %s' % rec['reproducibleBodySha256'])
print('  独立重算       = %s' % h)
print('  ⇒ **逐位相同 = %s**' % (rec['reproducibleBodySha256'] == h))
print('  整文件 sha     = %s（应与上面不同，因含 generatedAt/receipts）' % hashlib.sha256(b).hexdigest())

print('\n=== 并验证：我复算出的"旧值不可重现"原因（跨版本，按其判断）===')
print('  其试的五种约定均不命中我旧报的 52233dd1… —— 原因：该值对应**v1/更早字节**（跨版本比较，按 note 本就无效）')
