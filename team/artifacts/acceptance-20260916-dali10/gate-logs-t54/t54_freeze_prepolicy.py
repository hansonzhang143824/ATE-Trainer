# -*- coding: utf-8 -*-
"""修最后一步：`prePolicyCountsAtPolicyWrite` 的重建让 `lines` 每次都从 `None` 开始 ⇒ 每次都"首次写入"⇒
`asOf` 反复刷新（**冻结不彻底**）。改为：**从已落盘的 meta 档读回冻结值**，仅当确无时才首次回填。
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

OLD = ("if (_rec.get('prePolicyCountsAtPolicyWrite') or {}).get('lines') is None:\n"
       "    _ppc = _rec['prePolicyCountsAtPolicyWrite']\n"
       "    _ppc['lines'] = len(_prev_lines)\n"
       "    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
       "    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')")
NEW = ("# 冻结：优先从**已落盘的 meta 档**读回（否则每次重建都会『首次写入』⇒ asOf 反复刷新）\n"
       "_ppc_prev = {}\n"
       "try:\n"
       "    _mp = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')\n"
       "    if os.path.isfile(_mp):\n"
       "        _ppc_prev = (_json.loads(io.open(_mp, encoding='utf-8-sig').read())\n"
       "                     .get('prePolicyCountsAtPolicyWrite') or {})\n"
       "except Exception:\n"
       "    _ppc_prev = {}\n"
       "if _ppc_prev.get('lines') is not None:\n"
       "    _rec['prePolicyCountsAtPolicyWrite'] = _ppc_prev          # 已冻结 ⇒ 原样保留\n"
       "else:\n"
       "    _ppc = _rec['prePolicyCountsAtPolicyWrite']\n"
       "    _ppc['lines'] = len(_prev_lines)\n"
       "    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
       "    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')\n"
       "    # 落盘到 meta 档，作为**冻结的历史读数**（下一次生成即可读回）\n"
       "    try:\n"
       "        _mp = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')\n"
       "        _mj = (_json.loads(io.open(_mp, encoding='utf-8-sig').read())\n"
       "               if os.path.isfile(_mp) else {})\n"
       "        _mj['prePolicyCountsAtPolicyWrite'] = _ppc\n"
       "        open(_mp, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))\n"
       "    except Exception:\n"
       "        pass")
if "_ppc_prev" in src:
    print('  冻结读回已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已加冻结读回 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    i = src.find('prePolicyCountsAtPolicyWrite')
    print(repr(src[i - 60:i + 260]))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

import time


def snap():
    r = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
    return (r['appendPolicyBoundary']['effectiveFromRunSeq'],
            r['prePolicyCountsAtPolicyWrite']['lines'],
            r['prePolicyCountsAtPolicyWrite']['asOf'])


for i in (1, 2, 3):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    err = (r.stderr or '').strip().splitlines()
    print('  run%d: exit=%d %s' % (i, r.returncode, err[-1][:90] if err else 'OK'))
    time.sleep(1.1)
a = snap()
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    time.sleep(1.1)
b = snap()
print('\n  前置 =', a)
print('  两跑后 =', b)
print('  ⇒ **冻结（asOf 不再刷新）= %s**' % (a == b))
m = json.load(io.open(os.path.join(HERE, 'build-report.receipts.meta.json'), encoding='utf-8-sig'))
print('  meta 内已存冻结值 =', json.dumps(m.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False)[:180])
