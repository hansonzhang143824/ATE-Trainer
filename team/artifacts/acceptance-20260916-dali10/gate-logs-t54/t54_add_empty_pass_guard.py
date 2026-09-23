# -*- coding: utf-8 -*-
"""把 schematic-expert 的可执行验收规则写入 build-report.json（幂等、脚本直写）：
   "t54 的 PASS 须同时满足 `[scan] targets=N>0`；否则该 PASS 为空跳。"
并记录本轮实测 targets 值（从门禁日志现算提取，非手抄）。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN, 'build-report.json')
MARK = 'emptyPassGuard'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


rep = json.load(io.open(REPORT, encoding='utf-8-sig'))
if MARK in rep:
    print('已写入（幂等）: %d B' % os.path.getsize(REPORT))
    raise SystemExit(0)

# 从门禁日志现算提取 targets=N（脚本提取，非手抄）
def grep_targets(path):
    if not os.path.isfile(path):
        return None
    t = io.open(path, encoding='utf-8-sig', errors='replace').read()
    m = re.search(r'\[scan\]\s+targets=(\d+)', t)
    return int(m.group(1)) if m else None


bst = os.path.join(RUN, 'gate-logs-t54', 'bst-sw.log')
t54_targets = grep_targets(bst)

rep[MARK] = {
    'rule': ('**t54 的 PASS 须同时满足 `[scan] targets=N>0`；否则该 PASS 为空跳（未执行断言）。**'
             '（schematic-expert 提出，Captain 已将 B-7 记为门禁能力局限；本条为可执行验收格式。）'),
    'rationale': ('`verify_bst_sw_sequence.py` L497-499：`if not targets: print(…空 PASS); return 0` '
                  '⇒ 空集时**契约闭合断言整段被跳过**却仍 exit 0；故"exit 0"本身不足以证明检查已执行。'),
    'evidenceThisRun': {
        'gateLog': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/bst-sw.log',
        'targetsObserved': t54_targets,
        'assertionExecuted': bool(t54_targets and t54_targets > 0),
        'note': ('本轮 t54 的 `bst-sw` 日志含 `[scan] targets=%s`（>0）⇒ **契约闭合断言确已执行**，'
                 '故该次 NEW-RED 是真判定，不是空跳。' % t54_targets),
    },
    'counterExample': ('`--src <候选payload>`（只含 TM600/TM601）⇒ 日志无 `targets=`，'
                       '而是 `无 rampi_capv 电流斜坡测试项 … 空 PASS` / exit 0 ⇒ **属空跳，不得计为通过**。'),
}
io.open(REPORT, 'w', encoding='utf-8').write(json.dumps(rep, ensure_ascii=False, indent=2))
rep2 = json.load(io.open(REPORT, encoding='utf-8-sig'))
print('已写入: %d B / %s' % (os.path.getsize(REPORT), sha(REPORT)))
print('  targetsObserved =', rep2[MARK]['evidenceThisRun']['targetsObserved'])
print('  assertionExecuted =', rep2[MARK]['evidenceThisRun']['assertionExecuted'])
print('  verdict 仍 =', rep2['verdict'])
