# -*- coding: utf-8 -*-
"""收尾：修正 transition-plan 中"payload 将闭 K48+K76(+K61)"的过度断言（幂等）。
按现算：TM600 现盘已闭 {60,61}；批处理需补的是 {48,76}（60/61 已在）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TP = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't33-transition-plan.md'))
OLD = '（修正后契约期望集 `[48,60,61,76]`，payload 的 TM600 将闭 `K48`+`K76`(+`K61`)）⇒'
NEW = ('（修正后期望集 `[48,60,61,76]`；TM600 已闭 `{60,61}`，**批处理需补的是 `K48`+`K76`**）⇒')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(TP, encoding='utf-8-sig').read()
if NEW in t:
    print('已修正（幂等）: %d B / %s' % (os.path.getsize(TP), sha(TP)[:16]))
elif OLD in t:
    io.open(TP, 'w', encoding='utf-8', newline='').write(t.replace(OLD, NEW, 1))
    print('已修正: %d B / %s' % (os.path.getsize(TP), sha(TP)[:16]))
else:
    print('ERROR: 未找到待修断言')
