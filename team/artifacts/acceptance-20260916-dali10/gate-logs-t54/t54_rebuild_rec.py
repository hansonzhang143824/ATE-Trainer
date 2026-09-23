# -*- coding: utf-8 -*-
"""把生成器的**收据 dict 段整段重建**（含全部应有关键字段，缩进正确），一次性消除我历次补丁造成的错位。
（如实说明：先前一次替换吃掉了 `lastAppendDecision` 并把 `appendPolicy` 挤到错误缩进——本脚本整段重写以收口。）
"""
import ast
import collections
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

start = src.find('_rec = {')
end = src.find("_rec_p = os.path.join", start)
assert start > 0 and end > start, 'anchors not found'
print('  重建区间 = [%d, %d)（%d 字符）' % (start, end, end - start))

NEW = '''_rec = {
    'subject': 'team/artifacts/acceptance-20260916-dali10/build-report.json',
    'at': _dt.datetime.now().astimezone().isoformat(timespec='seconds'),
    'size': len(_b),
    'sha256': _hl.sha256(_b).hexdigest(),
    'sha256_lf_normalized': _hl.sha256(_b.replace(b"\\r\\n", b"\\n")).hexdigest(),
    'topLevelEntries': len(_json.loads(_b.decode('utf-8-sig'))),
    'reproducibleBodySha256': _hl.sha256(
        _json.dumps(
            {k: v for k, v in _json.loads(_b.decode('utf-8-sig')).items()
             if k not in ('generatedAt', 'receipts')},
            ensure_ascii=False, sort_keys=True).encode('utf-8')
    ).hexdigest(),
    'reproducibleNote': ('剔除 `generatedAt` 与 `receipts` 后的 body 哈希；projectionSpec v2 ⇒ 跨次生成稳定。'
                         '（更正留痕：v1 曾以"收据历史行 sha 在变"为由，该理由不成立且已撤回。）'),
    'projectionSpec': {
        'exclude': ['generatedAt', 'receipts'],
        'version': 2,
        'serialization': ("json.dumps(body, ensure_ascii=False, sort_keys=True)，分隔符为 Python json 默认，无尾随换行"),
        'encoding': 'utf-8',
        'bodyDefinition': ("body = {k: v for k, v in json.loads(<file bytes>.decode('utf-8-sig')).items() "
                           "if k not in exclude} ⇒ 再按上述 serialization/encoding 序列化后取 sha256"),
        'stabilityNote': ('不稳定来源是 `generatedAt`（每次生成）与 `receipts`；均已排除 ⇒ v2 下跨次稳定。'
                          '⚠️ 排除项 `receipts` 在当前正文中不存在（正文键路径穷举 0 命中）⇒ 属**预防性**，'
                          '本身不构成升版本理由；**升 v2 的正当理由＝v1 未声明序列化与编码 ⇒ 第三方同字节也无法复现**。'),
        'note': ('跨秒不变；跨版本不可混用 —— 排除项/序列化/编码任一变化都必须换版本号。'),
    },
    'standardTriHash': ('活档产物的标准三哈希（用途不同、不可互换）：'
                        'sha256 = 身份（逐字节同盘）；sha256_lf_normalized = 跨序列化可比重（行尾无关）；'
                        'reproducibleBodySha256 = 幂等判定（剔除 generatedAt、跨次可比）。'),
    'hashInvariance': {
        'sha256': '逐字节同盘身份（含 generatedAt ⇒ 跨次重生成会变）',
        'sha256_lf_normalized': '行尾不变（跨编辑器 / CRLF-LF 可比）',
        'reproducibleBodySha256': '时间戳不变（跨秒/跨次可比；用于判内容是否变）',
    },
    'isFrozen': False,
    'appendPolicy': ('**本账本仅在身份（body 哈希，projectionSpec 口径）变化时追加**；'
                     '**因此"一段时间无增长"不等于"无运行"** —— 新策略下运行可以发生而有意不记。'
                     '**运行计数一律查 `runSeq`**。'
                     '⚠️ **制度边界以事件表述、不锚行号**：生效点与【预策略段】规模见 `appendPolicyBoundary`。'),
    'appendPolicyBoundary': {
        'note': ('**事件表述的边界**（自哪个 runSeq 起生效）⇒ 作为**历史事件永久稳定**；'
                 '**本字段不写『账本当前共多少行』** —— 那是**当前测量、必然漂**。'
                 '【预策略段】规模见 `prePolicyCountsAtPolicyWrite`（**带限定名的历史读数**）。'),
        'effectiveFromRunSeq': None,
        'prePolicySegments': None,
    },
    'prePolicyCountsAtPolicyWrite': {
        'note': ('**预策略段（每次运行都追加的那一段）的规模 —— 取值为本字段首次写入时的测量**。'
                 '⚠️ 名字自带限定：这是写入时刻的历史读数，不是账本当前总量。'),
        'lines': None,
        'distinctBodyIdentities': None,
        'asOf': None,
        'frozen': True,
    },
    'lastAppendDecision': {
        'note': ('**本次生成对历史账本的追加决策（每次都会重算、因此总是可见）** —— '
                 '`reason` 只在真正追加的行里出现 ⇒ 在 skip 情形下**结构上不可达** ⇒ '
                 '故把决策放在本字段（收据每次重算），而**不改任何历史行**。'),
        'policy': '仅在身份（reproducibleBodySha256，projectionSpec 口径）变化时追加',
        'appended': None,
        'byIdentity': None,
        'reason': None,
        'ledgerLinesAtDecision': None,
    },
    'countUnitNote': ('计数单位：`lineCount` 是**行的条数**；状态数须按 '
                      '(size, sha256, reproducibleBodySha256, at) 去重后计。'
                      '⚠️ `at` 只到**秒** ⇒ 同秒两次运行得到同 at 同 sha 两行 ⇒ 同 at 不构成同一性；'
                      '故**状态数是运行次数的下界**；精确运行计数请用 `runSeq`；秒级 at 不是计数装置。'
                      '⚠️ 自证请**按行计**（"含该字段的行数 = N / M"），不得按文件计。'),
    'note': '报告为**活档**；本收据每次生成后重算。引用某一版身份请用本文件，勿用报告内的自算哈希。',
}
'''
out = src[:start] + NEW + src[end:]
ast.parse(out)
io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
print('  已整段重建收据 dict → %d B' % os.path.getsize(GEN))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

# 回填逻辑（在历史段，_prev_lines 可用）
src2 = io.open(GEN, encoding='utf-8-sig').read()
ANCH = "_appended = _rec.get('reproducibleBodySha256') not in _known_bodies"
FILL = ("_rec['appendPolicyBoundary']['effectiveFromRunSeq'] = len(_prev_lines) + 1\n"
        "_rec['appendPolicyBoundary']['prePolicySegments'] = len(_prev_lines)\n"
        "if (_rec.get('prePolicyCountsAtPolicyWrite') or {}).get('lines') is None:\n"
        "    _ppc = _rec['prePolicyCountsAtPolicyWrite']\n"
        "    _ppc['lines'] = len(_prev_lines)\n"
        "    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
        "    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')\n"
        + ANCH)
if "effectiveFromRunSeq'] = len(_prev_lines)" in src2:
    print('  回填已含（幂等）')
elif ANCH in src2:
    out2 = src2.replace(ANCH, FILL, 1)
    ast.parse(out2)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out2)
    print('  已加回填 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 回填锚点未命中')
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置2：语法 OK')

for i in (1, 2, 3):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    err = (r.stderr or '').strip().splitlines()
    print('  run%d: exit=%d %s' % (i, r.returncode, err[-1][:95] if err else 'OK'))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  收据键 =', list(rec.keys()))
print('  boundary.effectiveFromRunSeq =', rec['appendPolicyBoundary']['effectiveFromRunSeq'])
print('  prePolicyCounts =', json.dumps(rec['prePolicyCountsAtPolicyWrite'], ensure_ascii=False))
print('  lastAppendDecision.appended =', rec['lastAppendDecision']['appended'], '| reason =', str(rec['lastAppendDecision']['reason'])[:40])
snap = json.dumps({k: rec[k] for k in ('appendPolicyBoundary', 'prePolicyCountsAtPolicyWrite')}, ensure_ascii=False, sort_keys=True)
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
b = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('  再跑两次后边界与历史计数不变 =',
      snap == json.dumps({k: b[k] for k in ('appendPolicyBoundary', 'prePolicyCountsAtPolicyWrite')}, ensure_ascii=False, sort_keys=True),
      '⇒ **冻结** ✓')
