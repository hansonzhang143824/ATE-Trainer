# -*- coding: utf-8 -*-
"""独立复核 schematic-expert 的"意外收获"：唯一幸存的字节快照能否把 rev 28 判定升级为第三方可复核。

只读该快照，核对 size / sha256 / revision / closedRelayNumbers 与其申报值。
"""
import hashlib
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
SNAP = os.path.join(RUN, 'backups', 't53-20260916-211719', 'setup-contract.json')

print('=== 快照目录内容 ===')
d0 = os.path.dirname(SNAP)
for f in sorted(os.listdir(d0)):
    p = os.path.join(d0, f)
    if os.path.isfile(p):
        print('  %-40s %8d B' % (f, os.path.getsize(p)))

d = open(SNAP, 'rb').read()
print('\n=== 独立现算（不采信任何字面）===')
print('  路径   = team/artifacts/acceptance-20260916-dali10/backups/t53-20260916-211719/setup-contract.json')
print('  size   = %d B' % len(d))
print('  sha256 = %s' % hashlib.sha256(d).hexdigest())
j = json.loads(d.decode('utf-8-sig'))
print('  revision = %s' % j.get('revision'))
b = [x for x in j['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
print('  aliasResolution[bst2sw].resolution.closedRelayNumbers = %s'
      % (b.get('resolution') or {}).get('closedRelayNumbers'))

print('\n=== 与其申报值比对 ===')
claim_size = 354106
claim_sha_prefix = '78cfc954b73a007e8cc2'
claim_closed = [110, 61]
actual_closed = (b.get('resolution') or {}).get('closedRelayNumbers')
print('  size 一致          =', len(d) == claim_size)
print('  sha 前缀一致       =', hashlib.sha256(d).hexdigest().startswith(claim_sha_prefix))
print('  closed 一致        =', actual_closed == claim_closed)
print('  revision==28       =', str(j.get('revision')) == '28')

print('\n=== 结论 ===')
ok = (len(d) == claim_size and hashlib.sha256(d).hexdigest().startswith(claim_sha_prefix)
      and actual_closed == claim_closed)
print('  独立复核通过 =', ok)
if ok:
    print('  ⇒ 其 rev 28 的两项判定（"门禁当时读到的字段仍是 [110,61]"、"修订当时只加未撤"）')
    print('     **有字节级证据、可第三方复核**，不再依赖其字面。')
    print('  ⇒ 同时为纪律 #3 提供**唯一反例式证明**：五个中间态中仅此一个可复核，')
    print('     原因正是"覆写前先复制了字节"。')
