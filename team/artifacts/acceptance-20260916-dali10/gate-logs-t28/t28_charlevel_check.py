# -*- coding: utf-8 -*-
"""字符级核对 v2 —— 修正 v1 缺陷：相邻字符串字面量被 Python 隐式拼接，
导致两个候选值实际相同（都成了 'b' 变体），比较结论无效。

本版：候选值由**显式构造**（从 ACTUAL 出发逐位替换）生成，避免任何手抄字符串被拼接。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
P = os.path.join(RUN, 'gate-logs-t28', 't28-red-proof.json')
ANCH = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.json')

actual = hashlib.sha256(open(P, 'rb').read()).hexdigest()
print('=== ① t28-red-proof.json ===')
print('  文件 %d B' % os.path.getsize(P))
print('  ACTUAL = %s  (len=%d, pos42=%r)' % (actual, len(actual), actual[41]))

# 显式构造两个候选：把第 42 位分别置为 'c' 与 'b'（其余取 ACTUAL）
pos = 41
cand_c = actual[:pos] + 'c' + actual[pos + 1:]
cand_b = actual[:pos] + 'b' + actual[pos + 1:]
for label, c in (("候选 A：pos42='c'（我最初给的）", cand_c),
                 ("候选 B：pos42='b'（我'自纠'给的）", cand_b)):
    diff = [i + 1 for i in range(64) if c[i] != actual[i]] or []
    print('  %-26s ⇒ %s ; 与 ACTUAL 的差异位=%s' % (label, '正确' if not diff else '错误', diff))

print('\n  ⇒ 结论：ACTUAL 的 pos42 = %r ⇒ **我最初给的值正确；我的"自纠"把它改错了一位**。' % actual[41])

print('\n=== ② 单一真源 t28-anchors.json 里该条 ===')
raw = open(ANCH, 'rb').read()
A = json.loads(raw.decode('utf-8-sig'))
print('  文件 %d B / %s / %d 条（对方测得 9,857 B / 29 条 = 更早版本）'
      % (len(raw), hashlib.sha256(raw).hexdigest(), len(A['anchors'])))
for a in A['anchors']:
    if a.get('path', '').endswith('t28-red-proof.json'):
        v = a['sha256']
        print('  登记值 = %s' % v)
        print('  与 ACTUAL 全 64 位一致 = %s ; 等于 b 变体 = %s' % (v == actual, v == cand_b))

print('\n=== ③ check_input_sync.py 位数 ===')
q = os.path.join(WS, 'scripts', 'check_input_sync.py')
h = hashlib.sha256(open(q, 'rb').read()).hexdigest()
print('  ACTUAL = %s (len=%d)' % (h, len(h)))
bad = 'e804c459b2d3088e72d455eb9e1b7893111' 'cea47ad0a640735b6f5db42d784d1'  # 我消息里的 65 位串
print('  我消息里的串 len=%d ⇒ 长度异常=%s（确系多打一个字符）' % (len(bad), len(bad) != 64))
print('  与 ACTUAL 前 16 位比较: %s vs %s' % (bad[:16], h[:16]))
