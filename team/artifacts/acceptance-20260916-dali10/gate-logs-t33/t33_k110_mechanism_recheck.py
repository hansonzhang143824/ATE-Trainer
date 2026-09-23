# -*- coding: utf-8 -*-
"""t33/K110 机制复核——按 setup-architect 给的新权威 locator（端子表 + 网表）实测。

目的：把机制表述从"同一文件不同路线"（我此前的中间结论）升级为**端子级**结论，并核对两句并列结论：
  (a) K109 不属 ACM 脚路线（同 net ≠ 串联）
  (b) 契约字面权威仍要求 K109 ⇒ t29 闭 K109+K110 属依约保守、合规
"""
import csv
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
CSV = os.path.join(WS, 'project', 'DALI', 'Dali-SCH.csv')


def h(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== 权威端子表 knowledge/hardware/relays.md ===')
p = os.path.join(WS, 'knowledge', 'hardware', 'relays.md')
print('  %d B / %s' % (os.path.getsize(p), h(p)))
print('  L29 口诀: 默认 2-3 通、6-7 通；通电 3-4 通、6-5 通')
print('  L31 注意: 磁保持继电器 —— 标注 NO 的脚默认闭合，NC 脚通电后才闭合（与普通继电器直觉相反）')

print('\n=== 网表 Dali-SCH.csv 端子级实测 ===')
print('  CSV %d B / %s' % (os.path.getsize(CSV), h(CSV)))
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8-sig', errors='replace')))
cols = list(rows[0].keys()) if rows else []
print('  列名:', cols[:14])


def find_desig(desig_pat, want_pins=None):
    out = []
    for r in rows:
        d = ''.join(str(v) for v in r.values() if v)
        des = str(r.get('Designator') or r.get('RefDes') or r.get('Name') or '')
        if re.fullmatch(desig_pat, des.strip()):
            out.append(r)
    return out


# 通用：打印 K109 / K110 的全部行（按 Designator 或任意字段含 K109/K110）
for label, pat in (('K109', r'K109'), ('K110', r'K110')):
    hits = [r for r in rows if any(pat in str(v) for v in r.values())]
    print('\n  --- %s 命中行数: %d ---' % (label, len(hits)))
    seen = set()
    for r in hits[:40]:
        pin = str(r.get('PinName') or r.get('Pin') or r.get('PIN') or '')
        net = str(r.get('NetName') or r.get('Net') or r.get('NET') or '')
        cv = str(r.get('ComponentValue') or r.get('Value') or '')
        des = str(r.get('Designator') or r.get('RefDes') or '')
        key = (des, pin, net)
        if key in seen:
            continue
        seen.add(key)
        print('    desig=%-8s pin=%-8s net=%-34s value=%s' % (des, pin, net, cv[:24]))

print('\n=== 判读 ===')
print('  若 K110 的 pin6(COM2) 与 S5_ACM200_FH18 同 net，且 pin5(NC)/pin7(NO) 分别落 BST_F/PB0_F：')
print('    ⇒ 通电 6-5 → BST_F；默认(复位) 6-7 → PB0_F ⇒ ACM 路线由 K110 单独完成（K110 必须 SetOn）')
print('  若 K109 的公共端(3/6)落在 FPVIe1_*_BUS_S1 而其在 BST 串中仅"同 net"：')
print('    ⇒ K109 不属 ACM 脚路线（同 net ≠ 串联），但契约 relaySet/needsClosed 仍字面要求 109')
