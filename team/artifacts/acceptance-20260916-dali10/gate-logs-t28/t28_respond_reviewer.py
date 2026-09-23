# -*- coding: utf-8 -*-
"""回应 rule-reviewer：现算其 ①③ 引用的各文件，并按其建议改用
"路径 + size + 现算命令"格式（**不再输出哈希字面**）。

检查项：
  1) t28-citation-notice.txt 内是否含正确值（含错值？）
  2) t28-anchors.json 内 check_input_sync.py 条是否 64 位、是否正确
  3) verify_relay_trace.py / setup-contract.json / build-report.json / 部署态 test.cpp
  4) devel/source/test.cpp 的**完整哈希**（我此前只给了前缀）
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def size(p):
    return os.path.getsize(p)


print('=== ① t28-citation-notice.txt ===')
cn = os.path.join(RUN, 'gate-logs-t28', 't28-citation-notice.txt')
t = io.open(cn, encoding='utf-8-sig').read()
h_cis = sha(os.path.join(WS, 'scripts', 'check_input_sync.py'))
print('  路径: team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-citation-notice.txt')
print('  size = %d B' % size(cn))
print('  文件内是否含现算正确值 =', h_cis in t)
print('  文件内是否含 65 位错值（…31111cea…） =', ('31111cea' in t))

print('\n=== ② t28-anchors.json 内 check_input_sync.py 条 ===')
an = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.json')
A = json.load(io.open(an, encoding='utf-8-sig'))
print('  路径: team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json')
print('  size = %d B ; 条目 = %d' % (size(an), len(A['anchors'])))
for a in A['anchors']:
    if a.get('path') == 'scripts/check_input_sync.py':
        v = a['sha256']
        print('  该条 len = %d ; 与现算一致 = %s' % (len(v), v == h_cis))

print('\n=== ③ 其余各文件（只给路径+size，按新格式）===')
for rel in ('scripts/verify_relay_trace.py',
            'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
            'team/artifacts/acceptance-20260916-dali10/build-report.json'):
    print('  %-58s %d B' % (rel, size(os.path.join(WS, rel))))

print('\n=== ④ devel/source/test.cpp 完整值（补全，不再只给前缀）===')
dv = 'D:/PROJECT6-DALI/devel/source/test.cpp'
print('  路径: D:/PROJECT6-DALI/devel/source/test.cpp')
print('  size = %d B' % size(dv))
print('  完整哈希 = %s' % sha(dv))   # 由本脚本打印，非手抄
print('  （本轮我从未写入 devel；已由我方多轮 before/after 现算佐证）')

print('\n=== ⑤ 我此后消息格式（采纳其建议）===')
print('  格式：<路径> · <size> B · 现算：python -c "...sha256..."')
print('  **不再在消息里输出任何哈希字面** —— 从机制上消除"复制粘贴引入错误"这一通道。')
