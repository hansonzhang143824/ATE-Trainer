# -*- coding: utf-8 -*-
"""修：`countUnitNote` 应加入**收据 dict 本身**（这样收据与历史行都带上）。
现有写法只加在历史行，而历史行是 `_rec` 的副本 ⇒ 收据里没有 ⇒ 需改在 `_rec` 定义处。
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

# 1) 从历史行写法里移除 countUnitNote（避免重复）
OLD_HIST = ("_line['countUnitNote'] = ('计数单位：`lineCount` 是**行的条数**；'\n"
            "                          '**状态数须按 (size, sha256, bodySha, at) 去重后计**。'\n"
            "                          '同秒内两次运行 ⇒ 同 `at`（只到秒）⇒ **同 at 不构成同一性**"
            "（见纪律』同一性需证据』）。')")
if OLD_HIST in src:
    src = src.replace(OLD_HIST + '\n', '', 1)
    print('  已从历史行写法移除 countUnitNote')

# 2) 加入 _rec（收据本身）—— 放在 isFrozen 之前
ANCHOR = "    'isFrozen': False,"
NEW = ("    'isFrozen': False,\n"
       "    'countUnitNote': ('计数单位：`lineCount`（历史账本）是**行的条数**；'\n"
       "                      '**状态数须按 (size, sha256, reproducibleBodySha256, at) 去重后计**。'\n"
       "                      '⚠️ `at` 只到**秒** ⇒ 同秒两次运行得到**同 at 同 sha** 的两行 ⇒ '\n"
       "                      '**同 at 不构成同一性**（见纪律『同一性本身需要证据』）。'),")
if "'countUnitNote'" in src and 'countUnitNote' in src.split('isFrozen')[0]:
    print('  已含（幂等）')
elif ANCHOR in src:
    out = src.replace(ANCHOR, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已加入收据 countUnitNote → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    sys.exit(1)

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:70] if tl else (r.stderr or '')[:120]))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
hrow = json.loads(io.open(os.path.join(HERE, 'build-report.receipts.jsonl'), encoding='utf-8')
                  .read().strip().splitlines()[-1])
print('\n=== 自证 ===')
print('  收据含 countUnitNote =', 'countUnitNote' in rec)
print('  历史行含 countUnitNote =', 'countUnitNote' in hrow)
print('  收据键 =', list(rec.keys()))
