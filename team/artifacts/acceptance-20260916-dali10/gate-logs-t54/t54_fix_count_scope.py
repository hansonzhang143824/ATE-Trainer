# -*- coding: utf-8 -*-
"""补范围标签：K109/K110 的"提及"必须标范围（函数体内 vs 全文件），并给出四列口径。

对齐双方读数：其在 TM600 体内测得 3/3；我方文本提及曾报 11/20（疑为全文件）。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import verify_relay_trace as V  # noqa: E402

PAY = os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10',
                   'implementation-payload-TM600-TM601.cpp')
t = io.open(PAY, encoding='utf-8-sig', errors='replace').read()
blocks = dict(V.fn_blocks(t))
body = blocks.get('TM600_HS_RDSON', '')

print('文件 = %d B ; 行数 = %d（splitlines 计法，不含尾随空行差异）' % (os.path.getsize(PAY), len(t.splitlines())))

TOKENS = ['K109_BUSL1_PB0', 'K110_ACM18_BST', 'K48_ACM5_AMP_REF', 'K76_ACM_BST']
print('\n%-20s %-16s %-16s %-16s %s' % ('token', 'body提及', 'body注释行', 'body SetOn点', '全文件提及'))
rows = []
for tok in TOKENS:
    in_body = body.count(tok)
    body_comment = sum(1 for l in body.splitlines() if tok in l and l.strip().startswith('//'))
    body_calls = sum(1 for m in re.finditer(r'cbite\.SetOn\(([^;]*)\)', body) if tok in m.group(1))
    whole = t.count(tok)
    rows.append((tok, in_body, body_comment, body_calls, whole))
    print('%-20s %-16d %-16d %-16d %d' % (tok, in_body, body_comment, body_calls, whole))

print('\n=== 修正后的口径表述（补范围标签）===')
for tok, b, c, s, w in rows:
    print('  `%s`：**TM600 body 内 %d**（其中注释行 %d、SetOn 调用点 %d）／**全文件 %d**'
          % (tok, b, c, s, w))

print('\n=== 结论 ===')
print('  1) **闭集口径**（门禁判据）= SetOn 调用点：K48=1、K76=1、K109=0、K110=0')
print('  2) **提及口径**必须带范围：body 内 %d/%d ；全文件 %d/%d'
      % (rows[0][1], rows[1][1], rows[0][4], rows[1][4]))
print('  ⇒ 我方此前只写"11/20"**缺范围标签**，正确写法 = "全文件 11/20（其中 TM600 body 内 3/3）"')
