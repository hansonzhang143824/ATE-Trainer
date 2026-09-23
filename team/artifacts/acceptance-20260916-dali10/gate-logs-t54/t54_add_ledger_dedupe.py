# -*- coding: utf-8 -*-
"""回应 setup-architect ② 的观察（账本会随每次复验膨胀，3,338→55,652 B）：
**先判定"是否每次运行 body 哈希都变"** —— 若 body 稳定（projectionSpec v2），
则可**按"身份（body 哈希）变化"才追加**，例行复验不追加 ⇒ 消除膨胀且不丢身份。
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
H = os.path.join(HERE, 'build-report.receipts.jsonl')
REC = os.path.join(HERE, 'build-report.receipt.json')


def rows():
    return [json.loads(l) for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()]


print('=== ① 跨秒跑两次：body 哈希是否稳定？（决定能否按身份去重）===')
sigs = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    r = json.load(io.open(REC, encoding='utf-8-sig'))
    sigs.append((r['reproducibleBodySha256'], r['sha256'], r['size']))
    time.sleep(1.3)
print('  run1 body=%s file=%s size=%s' % (sigs[0][0][:16], sigs[0][1][:16], sigs[0][2]))
print('  run2 body=%s file=%s size=%s' % (sigs[1][0][:16], sigs[1][1][:16], sigs[1][2]))
stable = sigs[0][0] == sigs[1][0]
print('  ⇒ **body 哈希稳定 = %s** ⇒ %s' % (stable,
      '可按"身份变化才追加"去重 ✓' if stable else '仍需每次追加（body 不稳）'))

print('\n=== ② 统计当前膨胀情况 ===')
R = rows()
print('  行数 = %d ｜ 文件 = %d B' % (len(R), os.path.getsize(H)))
bodies = [x.get('reproducibleBodySha256') for x in R if x.get('reproducibleBodySha256')]
print('  不同 body 哈希数 = %d ⇒ **其中 (行数 − 该数) = %d 行为"例行复验"（身份未变）**'
      % (len(set(bodies)), len(R) - len(set(bodies))))

print('\n=== ③ 落地：仅在 body 哈希变化时追加（并加 reason 字段）===')
src = io.open(GEN, encoding='utf-8-sig').read()
import ast
ast.parse(src)
OLD = "_hist_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.jsonl')"
NEW = ("_hist_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.jsonl')\n"
       "# 去重：**仅当身份（body 哈希，projectionSpec v2）变化时追加**，避免例行复验导致膨胀\n"
       "#   （setup-architect 观察：3,338 → 55,652 B；其建议按身份变化才追加，或加 reason 区分）\n"
       "_known_bodies = set()\n"
       "if os.path.isfile(_hist_p):\n"
       "    for _l in io.open(_hist_p, encoding='utf-8').read().splitlines():\n"
       "        if _l.strip():\n"
       "            try:\n"
       "                _known_bodies.add(json.loads(_l).get('reproducibleBodySha256'))\n"
       "            except Exception:\n"
       "                pass")
if '_known_bodies' in src:
    print('  已含去重逻辑（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    # 在追加处包一层判断 + reason
    OLD2 = "with io.open(_hist_p, 'a', encoding='utf-8') as _f:\n    _f.write(json.dumps(_line, ensure_ascii=False) + '\\n')"
    NEW2 = ("_line['reason'] = ('identity-change' if _rec.get('reproducibleBodySha256') not in _known_bodies\n"
            "                          else 'routine-reverify (identity unchanged ⇒ NOT appended)')\n"
            "if _rec.get('reproducibleBodySha256') not in _known_bodies:\n"
            "    with io.open(_hist_p, 'a', encoding='utf-8') as _f:\n"
            "        _f.write(json.dumps(_line, ensure_ascii=False) + '\\n')\n"
            "    print('RECEIPT-HISTORY appended (identity-change)')\n"
            "else:\n"
            "    print('RECEIPT-HISTORY skipped (routine re-verify; identity unchanged)')")
    if OLD2 in out:
        out = out.replace(OLD2, NEW2, 1)
        ast.parse(out)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
        print('  已加入"仅身份变化才追加" + reason 字段 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 追加处锚点未命中')
else:
    print('  WARN: 账本路径锚点未命中')
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('  语法 OK')

print('\n=== ④ 自证：连跑三次，行数应只 +0/+1（不随每次运行膨胀）===')
for i in (1, 2, 3):
    n0 = len(rows())
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [l for l in (r.stdout or '').strip().splitlines() if 'RECEIPT-HISTORY' in l]
    print('  run%d: %d → %d 行 ｜ %s' % (i, n0, len(rows()), tl[-1][:60] if tl else ''))
    time.sleep(1.1)
