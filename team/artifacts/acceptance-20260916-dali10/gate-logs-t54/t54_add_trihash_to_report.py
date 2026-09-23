# -*- coding: utf-8 -*-
"""补：`standardTriHash` 现只在**收据**内出现；按 rule-reviewer ③ 的本意应**报告侧**也有
（读者从报告即可知"三哈希各自用途"）。本脚本在报告的 `livenessDeclaration` 旁并列加入。
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：生成器语法 OK（%d B）' % len(src.encode('utf-8')))

ANCHOR = "    'livenessDeclaration': {"
NEW = ('''    'standardTriHash': ('**活档产物的标准三哈希**（用途不同、不可互换）：'
                        '① `sha256` = **身份**（逐字节同盘）；'
                        '② `sha256_lf_normalized` = **跨序列化可比重**（行尾无关）；'
                        '③ `reproducibleBodySha256` = **幂等判定**（剔除 `generatedAt`、跨次可比）。'
                        '⇒ **判『内容是否变』必须用 ③**，不得拿 ① 直接比。'),
''' + ANCHOR)
# 只改**报告**侧：锚点首次出现处即在报告 dict（livenessDeclaration 仅报告有）
if "    'livenessDeclaration': {" in src and src.count("'standardTriHash'") == 1:
    out = src.replace(ANCHOR, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已在报告侧加入 standardTriHash → %d B' % os.path.getsize(GEN))
else:
    print('  无需改（报告侧已有，或锚点异常）: count=%d' % src.count("'standardTriHash'"))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:60] if tl else (r.stderr or '')[:120]))

A = json.load(io.open(REPORT, encoding='utf-8-sig'))
rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  报告含 standardTriHash =', 'standardTriHash' in A)
print('  收据含 standardTriHash =', 'standardTriHash' in rec)
print('  报告 %d B ; 收据 %d B' % (os.path.getsize(REPORT), os.path.getsize(os.path.join(HERE, 'build-report.receipt.json'))))
