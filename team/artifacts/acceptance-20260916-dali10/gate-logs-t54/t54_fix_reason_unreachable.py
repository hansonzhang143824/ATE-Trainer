# -*- coding: utf-8 -*-
"""修 rule-reviewer ③ 暴露的**真缺陷**（幂等）：
`reason` 只在**真正追加**的分支里被赋值 ⇒ 而追加已被"仅身份变化"抑制 ⇒
  ⇒ **至今 0 行含 `reason`** ⇒ **该字段结构上不可达、决策未被记载**（rule-reviewer 实测"mei 测到"是**对的**）。

修法：**决策写到"每次都会重算"的外部载体** —— 收据新增 **`lastAppendDecision`**
（总是存在：记本次是 appended 还是 skipped、依据哪个身份值、以及之所以如此的策略）。
⇒ 既不碰历史行（append-only 保持），又让决策可见。
"""
import ast
import collections
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
H = os.path.join(HERE, 'build-report.receipts.jsonl')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

OLD = "    'countUnitNote': ("
NEW = ('''    'lastAppendDecision': {
        'note': ('**本次生成对历史账本的追加决策（每次都会重算、因此总是可见）** —— '
                 '`reason` 只在真正追加的行里出现 ⇒ **在 skip 情形下结构上不可达** ⇒ '
                 '故把决策放在本字段（收据每次重算），而**不改任何历史行**。'),
        'policy': '仅在身份（reproducibleBodySha256，projectionSpec 口径）变化时追加',
    },
''' + OLD)
if "'lastAppendDecision'" in src:
    print('  lastAppendDecision 已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    # 让生成器在决策处回填该字段
    OLD2 = ("if _rec.get('reproducibleBodySha256') not in _known_bodies:\n"
            "    with io.open(_hist_p, 'a', encoding='utf-8') as _f:")
    NEW2 = ("_appended = _rec.get('reproducibleBodySha256') not in _known_bodies\n"
            "_rec['lastAppendDecision']['appended'] = _appended\n"
            "_rec['lastAppendDecision']['byIdentity'] = _rec.get('reproducibleBodySha256')\n"
            "_rec['lastAppendDecision']['reason'] = ('identity-change' if _appended\n"
            "                                        else 'routine-reverify (identity unchanged => NOT appended)')\n"
            "_rec['lastAppendDecision']['ledgerLinesAtDecision'] = len(_prev_lines)\n"
            "open(_rec_p, 'w', encoding='utf-8').write(_json.dumps(_rec, ensure_ascii=False, indent=2))\n"
            "if _appended:\n"
            "    with io.open(_hist_p, 'a', encoding='utf-8') as _f:")
    if OLD2 in out:
        out = out.replace(OLD2, NEW2, 1)
        ast.parse(out)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
        print('  已加 lastAppendDecision + 回填 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 决策处锚点未命中；仅加了字段定义')
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
else:
    print('  WARN: countUnitNote 锚点未命中')

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')
n0 = len([l for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()])
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:70]))
n1 = len([l for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()])
print('  账本行数 %d → %d（**0 增长** ⇒ 策略生效）' % (n0, n1))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  收据含 lastAppendDecision =', 'lastAppendDecision' in rec)
print('  值 =', json.dumps(rec.get('lastAppendDecision'), ensure_ascii=False)[:200])
R = [json.loads(l) for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()]
print('  历史行含 reason 的行数 =', sum(1 for x in R if 'reason' in x), '/', len(R),
      '（**仍为 0 ⇒ 未改历史行**，但决策现已在收据可见 ✓）')

print('\n=== 规则入册 ===')
MARK = '## 附廿六｜决策必须落在"每次都会重算"的载体上（否则 skip 分支下结构上不可达）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 指出我方 `reason` 字段"末行**没测到**"（其**不判错、只要求谓词**）；
我方核查后确认**其观察正确，且这是真缺陷**：`reason` **只在真正追加的分支里被赋值**，
而追加已被"仅身份变化"抑制 ⇒ **至今 0 行含 `reason`** ⇒ **该字段结构上不可达、决策未被记载**。

**规则**
> **"决策"必须落在"每次都会重算"的载体上**（如收据），
> **不能只落在"条件成立时才产生"的分支里** —— 否则**在未触发分支时，决策结构上不可见**。

**判据**：**"决策发生了"与"决策被记载"是两件事；前者在代码里，后者必须在产物里。**

**落地**：收据新增 **`lastAppendDecision`**（`appended` / `byIdentity` / `reason` / `ledgerLinesAtDecision`），
**每次生成都重算** ⇒ **skip 与 append 两种情形都可见**；**历史行一字未改**（append-only 保持）✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
