# -*- coding: utf-8 -*-
"""精确落地：**仅当"身份"（body 哈希）变化时追加历史行** + `reason` 字段。
（前一次尝试的插入锚点未命中；本次按实际代码行替换，并在写前/写后做 ast.parse。）
"""
import ast
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
H = os.path.join(HERE, 'build-report.receipts.jsonl')


def rows():
    return [json.loads(l) for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()]


src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

OLD1 = "_prev_lines = []\nif os.path.isfile(_hist_p):"
NEW1 = ("_prev_lines = []\n"
        "_known_bodies = set()\n"
        "if os.path.isfile(_hist_p):")
if '_known_bodies' in src:
    print('  _known_bodies 已含（幂等）')
elif OLD1 in src:
    src = src.replace(OLD1, NEW1, 1)
    print('  已插入 _known_bodies 声明')
else:
    print('  WARN: 声明锚点未命中')

OLD2 = ("    _prev_lines = [l for l in io.open(_hist_p, encoding='utf-8').read().splitlines() if l.strip()]\n"
        "_line = dict(_rec)")
NEW2 = ("    _prev_lines = [l for l in io.open(_hist_p, encoding='utf-8').read().splitlines() if l.strip()]\n"
        "    for _l in _prev_lines:                       # 收集既有\"身份\"（body 哈希）\n"
        "        try:\n"
        "            _known_bodies.add(_json.loads(_l).get('reproducibleBodySha256'))\n"
        "        except Exception:\n"
        "            pass\n"
        "_line = dict(_rec)")
if '_known_bodies.add' in src:
    print('  收集逻辑已含（幂等）')
elif OLD2 in src:
    src = src.replace(OLD2, NEW2, 1)
    print('  已插入身份收集')
else:
    print('  WARN: 收集锚点未命中')

OLD3 = ("with io.open(_hist_p, 'a', encoding='utf-8') as _f:\n"
        "    _f.write(_json.dumps(_line, ensure_ascii=False) + '\\n')\n"
        "print('RECEIPT-HISTORY %s (%d 行)' % (_hist_p, len(_prev_lines) + 1))")
NEW3 = ("_line['reason'] = ('identity-change' if _rec.get('reproducibleBodySha256') not in _known_bodies\n"
        "                          else 'routine-reverify (identity unchanged => NOT appended)')\n"
        "if _rec.get('reproducibleBodySha256') not in _known_bodies:\n"
        "    with io.open(_hist_p, 'a', encoding='utf-8') as _f:\n"
        "        _f.write(_json.dumps(_line, ensure_ascii=False) + '\\n')\n"
        "    print('RECEIPT-HISTORY appended lineCount=%d reason=identity-change' % _line['lineCount'])\n"
        "else:\n"
        "    print('RECEIPT-HISTORY skipped (routine re-verify; identity unchanged)')\n"
        "    _ = _line['reason']")
if 'routine-reverify' in src:
    print('  条件追加已含（幂等）')
elif OLD3 in src:
    src = src.replace(OLD3, NEW3, 1)
    print('  已改为条件追加 + reason')
else:
    print('  WARN: 追加锚点未命中')

try:
    ast.parse(src)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(src)
    print('  已写入 → %d B' % os.path.getsize(GEN))
except SyntaxError as e:
    print('  **改动引入语法错误，已放弃写入** → %s' % e)
    sys.exit(1)
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

print('\n=== 自证：连跑三次，行数应不再随每次运行膨胀 ===')
for i in (1, 2, 3):
    n0 = len(rows())
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [l for l in (r.stdout or '').strip().splitlines() if 'RECEIPT-HISTORY' in l]
    print('  run%d: %d → %d 行 ｜ %s' % (i, n0, len(rows()), tl[-1][:70] if tl else ''))
    time.sleep(1.1)
R = rows()
print('\n  行数 = %d ｜ 不同 body 哈希 = %d' % (len(R), len({x.get('reproducibleBodySha256') for x in R})))
print('  末行 reason =', R[-1].get('reason'))
