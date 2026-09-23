# -*- coding: utf-8 -*-
"""按 schematic-expert ② 的建议 (a)：把 `contract` 块拆成**单一基准**——
顶层只保留**门禁态**身份；**现盘态**三值只放 `currentOnDisk`。避免"rev32 紧挨 rev39 的哈希"。
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
MARK = "'baseline'"          # 新块的标志


def show_contract_block(tag):
    d = json.load(io.open(REPORT, encoding='utf-8-sig'))
    c = d['contract']
    print('  [%s] contract 顶层键 = %s' % (tag, list(c.keys())))
    print('        revision = %r ; size = %r ; mtime = %r'
          % (c.get('revision'), c.get('size'), c.get('mtime')))
    print('        currentOnDisk = %s' % json.dumps(c.get('currentOnDisk'), ensure_ascii=False))


print('=== 修复前 ===')
show_contract_block('before')

t = io.open(GEN, encoding='utf-8-sig').read()
OLD = re.search(r"    'contract': \{.*?\n    \},\n", t, re.S)
if not OLD:
    print('ERROR: 未找到 contract 块')
    raise SystemExit(1)
print('\n=== 生成器原块 ===')
print(OLD.group(0)[:900])

NEW = """    'contract': {
        # ⚠️ 单一基准原则（schematic-expert 指出"两态混放"）：本块**只**描述门禁态身份；
        #    现盘态三值一律只放 currentOnDisk，避免"rev32 紧邻 rev39 的哈希"被误读为同一版本。
        'baseline': 'gate-read (门禁日志自述)',
        'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
        'revision': gateRevFromLog,
        'revisionNote': ('本块所有字段均为**门禁态**（= 门禁那次运行实际读到的版本）；'
                         '现盘值见 currentOnDisk —— 两者基准不同，引用时必须分别声明。'),
        'currentOnDisk': {'baseline': 'on-disk (现盘)', 'revision': rev, 'size': c_size,
                          'sha256': c_sha, 'mtime': c_mt},
        'bst2sw_closedRelayNumbers': b2['resolution'].get('closedRelayNumbers'),
        'bst2sw_supersededRelaySet': b2['resolution'].get('supersededRelaySet'),
        'note': 't53 收尾（路径 1）已落地：权威期望由 ch18 的 [110,61] 切到 ch5 路线 [48,60,61,76]',
    },
"""
t = t.replace(OLD.group(0), NEW, 1)
io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('\n  生成器已改 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成:', (r.stdout or '').strip().replace('\n', ' | ')[:200] if r.stdout else r.stderr[:200])

print('\n=== 修复后 ===')
show_contract_block('after')
