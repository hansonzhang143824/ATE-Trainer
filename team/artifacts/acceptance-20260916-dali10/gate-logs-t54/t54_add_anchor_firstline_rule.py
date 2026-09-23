# -*- coding: utf-8 -*-
"""并入 schematic-expert ① 的落实细节：**版本锚必须置于消息首行**（写文末＝等于没写），
理由与"读数规则的有效性＝它的可发现性"同源。幂等。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '**锚必须置于消息首行（否则约定退化为形式）**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已含该细节 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

OLD = '**配套**：更正他方结论前，**先读其消息的版本锚**；若其锚 ≠ 你手上的现值 ⇒ **先声明差值，再判对错**。'
NEW = ('**配套**：更正他方结论前，**先读其消息的版本锚**；若其锚 ≠ 你手上的现值 ⇒ **先声明差值，再判对错**。\n\n'
       + MARK + '：**锚写在文末等于没写** —— '
       '该约定的有效性取决于它的**可发现性**（与"读数规则的有效性＝可发现性"同源）。\n'
       '⇒ 因此**首行即锚**，且**锚只用你亲自现算过的值**；引用他方读数时**标明"我未独立现算、按其自述采信"**，'
       '**不代他人背书**。\n')
if OLD not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)
t = t.replace(OLD, NEW, 1)
io.open(REG, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '首行即锚', '不代他人背书'):
    print('  含 %-18s %s' % (k, k in t2))
