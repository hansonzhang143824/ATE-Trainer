# -*- coding: utf-8 -*-
"""t54 补充阳性/阴性对照（**沙箱内、不改脚本、不动基线、不落盘目标树**）。

Captain 要求三项并列，且均在同一契约版本下：
  阳性：沙箱副本 TM600 去掉 K48+K76（制造等价真缺口）⇒ 必须报红（红因＝缺 K48/76）
  阴性：沙箱副本＝终批 payload ⇒ PASS（missing=[]）
  部署态对照：D:/.../test.cpp:9081 ⇒ FAIL，红因＝缺 [48,76]

⚠️ 能力边界（必须声明）：
  `verify_bst_sw_sequence.py` 的 main() 在 `targets` 为空时**提前 return** ⇒ 无法用 `--src`
  对仅有 TM600/TM601 的副本跑端到端。因此本对照**复现其判据函数**
  （`expected_for_tm()` 的派生规则 + `missing = set(exp) - set(SetOn)`），
  **不是门禁进程的真实输出**；部署态一列则是**真实 run_gates 输出**（gate-logs-t54）。
"""
import hashlib
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))
import verify_relay_trace as V  # noqa: E402

PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
CONTRACT = os.path.join(RUN, 'setup-contract.json')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def setons_of(path):
    t = io.open(path, encoding='utf-8-sig', errors='replace').read()
    out = {}
    for fn, blk in V.fn_blocks(t):
        nums = set()
        for r in V.parse_setons(blk):
            m = re.match(r'K(\d+)_', r)
            if m:
                nums.add(int(m.group(1)))
            elif re.fullmatch(r'\d+', r):
                nums.add(int(r))
        out[fn] = nums
    return out


C = json.loads(io.open(CONTRACT, encoding='utf-8-sig').read())
rev = C.get('revision')
idx = {}
for e in (C.get('aliasResolution') or []):
    a = str(e.get('alias', ''))
    nums = set()
    for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []):
        if isinstance(x, int):
            nums.add(x)
        else:
            nums |= {int(y) for y in re.findall(r'\d+', str(x))}
    users = set()
    for x in (e.get('usedByTm') or []):
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    idx[a] = (nums, users)


def expected(base):
    d = C['tmDeltas'][base]
    exp = {}
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        for n in sorted(idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasesUsed:%s' % a)
    for a, (nums, users) in idx.items():
        if base in users:
            for n in sorted(nums):
                exp.setdefault(n, 'usedByTm:%s' % a)
    return exp


exp600 = expected('TM600')

print('=== 同一契约版本 ===')
print('  revision = %s ; size = %d B ; sha256 现算见下' % (rev, os.path.getsize(CONTRACT)))
print('  bst2sw.closedRelayNumbers =',
      [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]['resolution'].get('closedRelayNumbers'))
print('  期望集 TM600 = %s' % sorted(exp600))

# ---- 阳性：沙箱副本去掉 K48 + K76 ----
src = io.open(PAY, encoding='utf-8-sig', errors='replace').read()
line_cut = re.compile(r'^(.*cbite\.SetOn\()(.*?)(\);\s*)$', re.M)


def strip_two_named(text, names):
    """在**唯一** SetOn 行里去掉指定别名参数（只动沙箱副本的字符串）。"""
    def repl(m):
        args = [a.strip() for a in m.group(2).split(',')]
        kept = [a for a in args if a not in names]
        return m.group(1) + ', '.join(kept) + m.group(3)
    return line_cut.sub(repl, text)


POS = strip_two_named(src, {'K48_ACM5_AMP_REF', 'K76_ACM_BST'})
tmp = os.path.join(tempfile.gettempdir(), 't54_positive_control.cpp')
io.open(tmp, 'w', encoding='utf-8', newline='').write(POS)

rows = []
for label, path in (('阳性（沙箱副本，去 K48+K76）', tmp),
                    ('阴性（终批 payload 原样）', PAY),
                    ('部署态对照（真实门禁输入）', DEP)):
    data = setons_of(path)
    nums = data.get('TM600_HS_RDSON', set())
    missing = sorted(set(exp600) - nums)
    rows.append((label, os.path.basename(path), sorted(nums), missing))
    print('  %-26s TM600=%s' % (label, sorted(nums)))
    print('       missing=%s ⇒ %s' % (missing, '报红' if missing else 'PASS'))

print()
print('=== 阳性对照有效性 ===')
pos_missing = rows[0][3]
print('  阳性 missing = %s ⇒ %s' % (pos_missing, '✅ 真缺口被捕获（报红）' if pos_missing else '❌ 未捕获'))
print('  阴性 missing = %s ⇒ %s' % (rows[1][3], '✅ PASS' if not rows[1][3] else '❌ 意外红'))
print('  部署 missing = %s ⇒ %s' % (rows[2][3], '✅ FAIL（红因正确）' if rows[2][3] else '❌ 意外绿'))

out = {
    'contract': {'revision': rev, 'size': os.path.getsize(CONTRACT), 'sha256': sha(CONTRACT),
                 'bst2sw_closedRelayNumbers':
                     [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]['resolution'].get('closedRelayNumbers')},
    'expected_TM600': sorted(exp600),
    'controls': [{'label': l, 'file': f, 'tm600_seton': n, 'missing': m} for l, f, n, m in rows],
    'capabilityNote': ('本对照复现 `expected_for_tm()` 派生规则与 `missing = set(exp) - SetOn` 判据；'
                       '**不是** `verify_bst_sw_sequence.py` 进程输出 —— 该脚本 main() 在 targets 为空时提前 return，'
                       '故无法用 --src 对仅有 TM600/TM601 的副本端到端跑。部署态一列为真实 run_gates 输出。'),
    'discipline': '沙箱内完成；未改脚本、未动 gate_baseline.json、未启用 --check-extra、未写目标树。',
}
op = os.path.join(HERE, 't54-controls.json')
io.open(op, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=2))
print('\nWROTE %s (%d B)' % (op, os.path.getsize(op)))
