# -*- coding: utf-8 -*-
"""按行范围去重 t33-transition-plan.md 中重复的"闭集更正 + 三情形"块（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TP = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't33-transition-plan.md'))
START = '**闭集更正（Captain 2026-09-16）**'
END = '（本分支）。'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


lines = io.open(TP, encoding='utf-8-sig').read().splitlines(keepends=True)
starts = [i for i, l in enumerate(lines) if START in l]
print('诊断: %d 行 ; 块起始行 = %s' % (len(lines), starts))
if len(starts) <= 1:
    print('无需去重（幂等）: %d B / %s' % (os.path.getsize(TP), sha(TP)[:16]))
    raise SystemExit(0)

# 删掉第 2 个块（从第 2 次 START 到其后首个含 END 的行，含尾随空行）
s2 = starts[1]
e2 = None
for i in range(s2, min(s2 + 12, len(lines))):
    if END in lines[i]:
        e2 = i
        break
if e2 is None:
    print('ERROR: 未找到第 2 块的结束行')
    raise SystemExit(1)
# 连同其后的空行一起删
while e2 + 1 < len(lines) and lines[e2 + 1].strip() == '':
    e2 += 1
print('  删除第 %d–%d 行（1-based）' % (s2 + 1, e2 + 1))
del lines[s2:e2 + 1]
io.open(TP, 'w', encoding='utf-8', newline='').write(''.join(lines))
t = io.open(TP, encoding='utf-8-sig').read()
print('完成: %d B / %s ; 剩余块数 = %d' % (len(t.encode()), sha(TP)[:16], t.count(START)))
