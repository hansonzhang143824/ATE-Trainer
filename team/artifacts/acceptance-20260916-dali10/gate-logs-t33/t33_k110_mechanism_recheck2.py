# -*- coding: utf-8 -*-
"""t33/K110 机制复核 v2 —— 端子级结论（按 setup-architect 的新权威 locator）。

v1 缺陷: 用 `PinName` 取引脚名，而该 CSV 的引脚列实际是 `MemberName` ⇒ 打印为空、判读依据不足。
v2 修正并给出**每个 net 的完整成员**，据此给出可复核的三句话结论。

权威端子表: knowledge/hardware/relays.md L18-31 —— G6K-2G-Y DPDT 磁保持:
  引脚 2=NO(默认↔COM1/3)、3=COM1、4=NC(通电↔COM1)、5=NC(通电↔COM2)、6=COM2、7=NO(默认↔COM2)
  ⚠️ 磁保持: **NO 脚默认闭合、NC 脚通电后才闭合**（与普通继电器直觉相反）
  ⇒ 口诀: 默认 2-3 通、6-7 通；通电 3-4 通、6-5 通
"""
import csv
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
CSV = os.path.join(WS, 'project', 'DALI', 'Dali-SCH.csv')
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8-sig', errors='replace')))
print('Dali-SCH.csv %d B / %s' % (os.path.getsize(CSV),
                                  hashlib.sha256(open(CSV, 'rb').read()).hexdigest()))
print('引脚列 = MemberName（v1 误用 PinName 导致空列）\n')


def members(desig_re, pin=None):
    out = []
    for r in rows:
        des = str(r.get('Designator') or '')
        if re.fullmatch(desig_re, des):
            m = str(r.get('MemberName') or '')
            if pin is None or m == str(pin):
                out.append((des, m, str(r.get('NetName') or '')))
    return sorted(set(out))


def net_members(net):
    out = []
    for r in rows:
        if str(r.get('NetName') or '') == net:
            out.append((str(r.get('Designator') or '<net>'), str(r.get('MemberName') or '')))
    return sorted(set(out))


print('=== K110_BST_S1 的端子归属 ===')
for des, m, net in members(r'K110_BST_S1'):
    print('  pin %-8s → %s' % (m, net))

print('\n=== K109_BUSL_PB0_S1 的端子归属 ===')
for des, m, net in members(r'K109_BUSL_PB0_S1'):
    print('  pin %-8s → %s' % (m, net))

print('\n=== 关键 net 的完整成员 ===')
for net in ('NetK76_ACM_BST_S1_4', 'NetK110_BST_S1_7', 'NetK109_BUSL_PB0_S1_4',
            'NetK109_BUSL_PB0_S1_5', 'FPVIe1_FL_BUS_S1', 'FPVIe1_SL_BUS_S1'):
    print('  [%s]' % net)
    for des, m in net_members(net):
        print('      %-24s %s' % (des, m))

print('\n=== 结论（三句，均可由上表复核） ===')
print('  1) K110 pin3=COM1、pin6=COM2；pin4=NC(通电↔COM1) 落 NetK76_ACM_BST_S1_4')
print('     （该 net 同时含 R_BST_S1 pin2 / TP_BST_S_S1 / K76_ACM_BST_S1 pin4 ⇒ 即 BST 侧）')
print('     pin7=NO(默认↔COM2) 落 NetK110_BST_S1_7（含 TP_PB0_F_S1 / K147_PB0_OSC_S1 ⇒ 即 PB0 侧）')
print('     ⇒ 通电 6-5 / 3-4 → BST 侧；默认(复位) 6-7 → PB0 侧')
print('  2) ACM 源（S5_ACM200_FH18，SCH:724）接 K110 公共端一侧 ⇒ **ACM 到 BST 由 K110 单独完成，必须 SetOn**')
print('  3) K109 公共端 pin3/pin6 落 FPVIe1_FL_BUS_S1 / FPVIe1_SL_BUS_S1（FPVIe1 侧）')
print('     其 NC/NO 与 K110 公共端**同 net 相连** ⇒ 属另一条路线/耦合，**同 net ≠ 串联**')
print('     ⇒ (a) K109 不属 ACM 脚路线；(b) 契约字面权威仍要求 K109（relaySet 含 109、pinRouteTable CH0 Low needsClosed 含 109）')
print('        ⇒ t29 闭 K109+K110 = 依约保守且合规')
