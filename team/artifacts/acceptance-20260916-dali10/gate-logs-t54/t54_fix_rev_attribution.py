# -*- coding: utf-8 -*-
"""修正 build-report.json 的契约归属：从**门禁日志**提取门禁实际读取的 rev，而非引用现盘 rev。

发现：`gate-logs-t54/bst-sw.log` 自述 `rev=32`；而报告 `contract.revision` 记的是**现盘** rev（已到 39）
⇒ 属"引用与证据不属同一版"的同类问题（t32-F3 类别）。本脚本把生成器改为：
  · `contract.revision` ← **日志里门禁实际使用的 rev**（证据锚）
  · 新增 `contract.currentOnDisk` ← 现盘 rev/size/mtime（供读者对照）
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
RUN = os.path.abspath(os.path.join(HERE, '..'))

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B' % os.path.getsize(GEN))

# 1) 在生成器里加入"从日志提取 rev"的逻辑
ANCHOR = "report = {"
if 'gateRevFromLog' in t:
    print('  已含 gateRevFromLog（幂等）')
else:
    INS = '''# ⚠️ 门禁实际读取的契约 rev 来自**门禁日志自述**（证据锚），不是现盘 rev
_bst_log_txt = io.open(bst_log, encoding='utf-8-sig', errors='replace').read() if os.path.isfile(bst_log) else ''
_m = re.search(r'rev=(\\d+)', _bst_log_txt)
gateRevFromLog = _m.group(1) if _m else None
print('  [归属] 门禁日志自述 rev = %s ; 现盘 rev = %s' % (gateRevFromLog, C.get('revision')))

'''
    if ANCHOR not in t:
        print('  ERROR: 未找到 report = { 锚点')
        raise SystemExit(1)
    t = t.replace(ANCHOR, INS + ANCHOR, 1)

# 2) contract 段改用 gateRevFromLog，并另记现盘
OLD = ("    'contract': {\n"
       "        'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',\n"
       "        'revision': rev,")
NEW = ("    'contract': {\n"
       "        'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',\n"
       "        'revision': gateRevFromLog,          # ← 门禁**实际读取**的 rev（证据锚，取自 bst-sw.log 自述）\n"
       "        'revisionNote': ('本字段 = 门禁日志自述的 rev（与门禁证据同版）；'\n"
       "                         '现盘 rev 见 currentOnDisk —— 二者可能不同，引用时须区分'),\n"
       "        'currentOnDisk': {'revision': rev, 'size': c_size, 'mtime': c_mt},")
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    print('  已改 contract 段（rev → gateRevFromLog + currentOnDisk）')
elif 'gateRevFromLog' in t and 'currentOnDisk' in t:
    print('  contract 段已是新写法（幂等）')
else:
    print('  WARN: contract 段锚点未命中，请人工检查')

io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('  → 生成器现 %d B' % os.path.getsize(GEN))

# 复查
t2 = io.open(GEN, encoding='utf-8-sig').read()
for k in ('gateRevFromLog', "'currentOnDisk'", 'revisionNote'):
    print('    %-20s 生成器含 = %s' % (k, k in t2))
