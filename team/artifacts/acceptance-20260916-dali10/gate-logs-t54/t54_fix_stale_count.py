# -*- coding: utf-8 -*-
"""更正 t44-count-correction.md §3.3 的"11/20"数字（无范围标签且属**更早 payload 版本**）。幂等。

现盘 payload（TM600 body 内）实测：
  K109_BUSL1_PB0 / K110_ACM18_BST : 提及 3 / 注释 3 / SetOn 调用点 0 ；全文件提及 3（同）
  K48_ACM5_AMP_REF / K76_ACM_BST  : 提及 4 / 注释 3 / SetOn 调用点 1 ；全文件提及 4（同）
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CORR = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't44-count-correction.md'))
MARK = '计数口径须同时标**版本**与**范围**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(CORR, encoding='utf-8-sig').read()
if MARK in t:
    print('已更正（幂等）: %d B' % os.path.getsize(CORR))
    raise SystemExit(0)

OLD = ('**计数口径同样须标版本**：该 payload 的 `TM600` 体内 `K109`/`K110` 的文本提及（11/20 次）**全部是注释**')
NEW = ('''**''' + MARK + '''（本行取代此前无标签的"11/20"）**：
- 实测量级**随 payload 版本变化** —— `11/20` 属**更早一版**（注释更长）；**现盘版本**为
  `K109_BUSL1_PB0` 提及 **3**（注释 3、SetOn 调用点 0）、`K110_ACM18_BST` 提及 **3**（注释 3、SetOn 调用点 0）；
  `K48_ACM5_AMP_REF` / `K76_ACM_BST` 各提及 **4**（注释 3、**SetOn 调用点 1**）；
- 上述"提及"在**函数体内与全文件相同**（该两 token 仅出现在 TM600 段）；
- **该 payload 的 `TM600` 体内 `K109`/`K110` 的文本提及全部是注释**''')

if OLD not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)
t = t.replace(OLD, NEW, 1)
t = t.rstrip() + '''

> ⚠️ **范围与版本标签纪律（schematic-expert 提出，我采纳）**：凡报"提及/命中"数，**必须同时标注
> ① 范围（函数体内 / 全文件）② 版本（payload 的现算 sha256 或"引用前现算"）**。
> 否则两个都正确的数字会互相看起来像矛盾（本轮已发生：`11/20`＝旧版全文件、`3/3`＝现版函数体内）。
'''
io.open(CORR, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(CORR, encoding='utf-8-sig').read()
print('已更正: %d B / %s' % (os.path.getsize(CORR), sha(CORR)))
for k in (MARK, '实测量级**随 payload 版本变化**', '范围与版本标签纪律'):
    print('  含 %-26s %s' % (k[:24], k in t2))
