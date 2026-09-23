# -*- coding: utf-8 -*-
"""t42 控制组复核 v2 —— 修正列口径（ACM200 pin 名在 `MemberName`，不在 `Designator`）。

v1 缺陷：我用 `Designator` 匹配 `S5_ACM200_FH<n>` ⇒ 0 命中（假阴性）。
本脚本按 `MemberName` 匹配，并复核 schematic-expert 的控制组主张：
  (i) 宏通道号 = ACM 别名号 = 网表脚后缀；
  (ii) site-5 ACM200 F 脚后缀集合 = 24 个（后缀即通道号）；
  (iii) **ch5 网不含 K110；ch18 网不含 K48/K76**（决定性分离）。
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
print('Dali-SCH.csv %d B / %s ; 行数 %d' % (os.path.getsize(CSV),
                                            hashlib.sha256(open(CSV, 'rb').read()).hexdigest(), len(rows)))


def members_of_net(net):
    """返回该 net 上的 (成员名, 所属器件) —— 只有 member 的情况器件为空。"""
    out = set()
    for r in rows:
        if str(r.get('NetName') or '') == net:
            out.add((str(r.get('MemberName') or ''), str(r.get('Designator') or '')))
    return sorted(out)


def net_of_member(member):
    for r in rows:
        if str(r.get('MemberName') or '') == member:
            return str(r.get('NetName') or '')
    return None


print('\n=== (ii) site-5 ACM200 F 脚后缀集合 ===')
suff = sorted({int(m.group(1)) for r in rows
               for m in [re.fullmatch(r'S5_ACM200_FH(\d+)', str(r.get('MemberName') or ''))] if m})
print('  S5_ACM200_FH<n> 的 n 集合 = %s' % suff)
print('  规模 = %d' % len(suff))

print('\n=== (i)+(iii) 控制组：每个 ACM 脚所在 net 与 K 继电器 peers ===')
for n in (4, 5, 7, 8, 18):
    net = net_of_member('S5_ACM200_FH%d' % n)
    peers = members_of_net(net) if net else []
    ks = sorted({m.split('.')[0] for m, _d in peers if m.startswith('K')})
    print('  FH%-3d net=%-32s K-peers=%s' % (n, net, ks))

print('\n=== ch5 网 与 ch18 网的完整成员（决定性分离）===')
for label, member in (('ch5  (FH5)', 'S5_ACM200_FH5'), ('ch5  (SH5)', 'S5_ACM200_SH5'),
                      ('ch18 (FH18)', 'S5_ACM200_FH18'), ('ch18 (SH18)', 'S5_ACM200_SH18')):
    net = net_of_member(member)
    print('  %-12s member=%-16s net=%s' % (label, member, net))
    if net:
        for m, d in members_of_net(net):
            print('       %-24s %s' % (m, d))

print('\n=== 判读 ===')
print('  若 FH5 所在网含 K48 而不含 K110，且 FH18 所在网含 K110 而不含 K48/K76：')
print('   ⇒ schematic-expert 的控制组成立：**后缀即通道号；ch5=K48、ch18=K110 是两个不同通道**')
print('   ⇒ 结合 StdAfx.h「唯一一条 ACM200[] -> BST 宏 = K_BST_ACM = 48,76」，')
print('     则 `SW12_U1REF_BST_ACM`（宏 = S5_5 等 8 个 site 的 channel 5）**走 [48,76]，不走 K110**')
