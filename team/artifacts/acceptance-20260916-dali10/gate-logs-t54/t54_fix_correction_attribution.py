# -*- coding: utf-8 -*-
"""更正 t33-k110-mechanism-correction.md §3 的归因：权威值已于 rev 33 消歧为 ch5（不再"未消歧"）。幂等。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't33-k110-mechanism-correction.md'))
MARK = '**归因更正（rev 33 之后）**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(P, encoding='utf-8-sig').read()
print('BEFORE: %d B' % os.path.getsize(P))
if MARK in t:
    print('已更正（幂等）: %d B' % os.path.getsize(P))
    raise SystemExit(0)

OLD = ('- 但**方向问题需与"归属未消歧"分开看**：rev 26 已把该字段标注为')
if OLD not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)

NEW = ('- ⚠️ ' + MARK + '：**rev 33 起该字段已消歧为 ch5**（`closedRelayNumbers = [48,60,61,76]`、'
       '`110` 移入 `closedRelayNumbersSuperseded`、`contestedAttribution.status = CLOSED (t53): … CHANNEL 5`）'
       '⇒ **"权威值仍是 `[110,61]`"及由此推出的"未消歧假红"均已不成立**；'
       '**落盘后 `bst-sw` 的预期＝GREEN**（路径 1 条件已满足，不需路径 2 的归因）。以下为**当时（rev 26 前）**的写法，'
       '保留作留痕：\n'
       '- 但**方向问题需与"归属未消歧"分开看**：rev 26 已把该字段标注为')

t = t.replace(OLD, NEW, 1)
# 把"路径 2"整段标注为历史
t = t.replace('⇒ **当前是"契约权威值未消歧"，不是断言写错**。',
              '⇒ **（当时）当前是"契约权威值未消歧"，不是断言写错**。', 1)
t = t.replace('- 路径 2（只增不翻）⇒ 落盘后仍红，而**红因是"缺 110"= 假红**，应按"待消歧"归因，**不得记为缺陷**。',
              '- ~~路径 2（只增不翻）⇒ 落盘后仍红，红因是"缺 110"= 假红~~ ⇒ **该路径已随 rev 33 消歧而取消**'
              '（历史留痕；现口径：权威值 = ch5，落盘后预期 GREEN）。', 1)
io.open(P, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(P, encoding='utf-8-sig').read()
print('AFTER : %d B / %s' % (os.path.getsize(P), sha(P)))
for k in (MARK, '已消歧为 ch5', '该路径已随 rev 33 消歧而取消'):
    print('  含 %-24s %s' % (k, k in t2))
