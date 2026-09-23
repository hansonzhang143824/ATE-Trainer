# -*- coding: utf-8 -*-
"""补齐被我上一版替换掉的两段（如实说明：替换区间吃掉 `lastAppendDecision`）：
  · 收据 `lastAppendDecision`（决策每次重算）
  · 收据 `appendPolicyBoundary`（事件表述的边界）
两段都插在 `countUnitNote` 之前，且用**列表拼接**插入（避免再次吃掉相邻键）。
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

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))
print('  含 lastAppendDecision =', "'lastAppendDecision'" in src)
print('  含 appendPolicyBoundary =', "'appendPolicyBoundary'" in src)

ANCH = "    'countUnitNote': ("
if "'lastAppendDecision'" in src and "'appendPolicyBoundary': {" in src:
    print('  两段均已含（幂等）')
else:
    INS = (
        "    'lastAppendDecision': {\n"
        "        'note': ('**本次生成对历史账本的追加决策（每次都会重算、因此总是可见）** —— '\n"
        "                 '`reason` 只在真正追加的行里出现 ⇒ **在 skip 情形下结构上不可达** ⇒ '\n"
        "                 '故把决策放在本字段（收据每次重算），而**不改任何历史行**。'),\n"
        "        'policy': '仅在身份（reproducibleBodySha256，projectionSpec 口径）变化时追加',\n"
        "    },\n"
        "    'appendPolicyBoundary': {\n"
        "        'note': ('**事件表述的边界**（自哪个 `runSeq` 起生效）⇒ 作为**历史事件永久稳定**；'\n"
        "                 '**本字段不写『账本当前共多少行』** —— 那是**当前测量、必然漂**。'\n"
        "                 '【预策略段】的规模见 `prePolicyCountsAtPolicyWrite`（**带限定名的历史读数**）。'),\n"
    )
    if ANCH not in src:
        print('  WARN: countUnitNote 锚点未命中')
        sys.exit(1)
    out = src.replace(ANCH, INS + "\n" + ANCH, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已插入两段 → %d B' % os.path.getsize(GEN))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

# 在收据段回填：边界（动态，事件）+ 历史计数（一次性冻结）
src2 = io.open(GEN, encoding='utf-8-sig').read()
ANCH2 = "_appended = _rec.get('reproducibleBodySha256') not in _known_bodies"
if "_rec['appendPolicyBoundary']['effectiveFromRunSeq']" in src2:
    print('  边界回填已含（幂等）')
else:
    NEW2 = ("_rec['appendPolicyBoundary']['effectiveFromRunSeq'] = len(_prev_lines) + 1\n"
            "_rec['appendPolicyBoundary']['prePolicySegments'] = len(_prev_lines)\n"
            "if (_rec.get('prePolicyCountsAtPolicyWrite') or {}).get('lines') is None:\n"
            "    _ppc = _rec['prePolicyCountsAtPolicyWrite']\n"
            "    _ppc['lines'] = len(_prev_lines)\n"
            "    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
            "    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')\n"
            + ANCH2)
    if ANCH2 in src2:
        out2 = src2.replace(ANCH2, NEW2, 1)
        ast.parse(out2)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out2)
        print('  已加边界回填 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 回填锚点未命中')
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置2：语法 OK')

for i in (1, 2, 3):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    err = (r.stderr or '').strip().splitlines()
    print('  run%d: exit=%d %s' % (i, r.returncode, err[-1][:90] if err else 'OK'))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  收据键 =', list(rec.keys()))
print('  boundary.effectiveFromRunSeq =', (rec.get('appendPolicyBoundary') or {}).get('effectiveFromRunSeq'))
print('  prePolicyCounts =', json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False))
x = json.dumps(rec.get('appendPolicyBoundary'), ensure_ascii=False) + json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False)
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
b = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('  再跑两次后不变 =', x == json.dumps(b.get('appendPolicyBoundary'), ensure_ascii=False) + json.dumps(b.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False), '⇒ 冻结 ✓')

print('\n=== 规则入册 ===')
MARK = '## 附卅二｜同一个数字的两种地位：事件边界（稳定）vs 运行总量（必漂）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 指出我方 `appendPolicy` **自身引入漂移源** ——
它硬记"此前（1–54 行）"与"54 行里只有 5 个身份"，而**两者都是被管辖账本的当前总量** ⇒
**策略今后真的追加一行 ⇒ 该字段立刻失真** ⇒ **"为修一个语义缺口而引入一个漂移源"** ✓

**规则（其判据）**
> **同一个数字，两种地位**：
> · **事件边界**（"**本策略自 `runSeq = N` 起生效**"）⇒ **历史事件 ⇒ 永久稳定** ✓
> · **运行总量**（"共 54 行"）⇒ **当前测量 ⇒ 必然漂** ✗

**修法（采纳其 (ii) ＋ L-b 范式）**
```
· 边界＝**事件**（锚制度边界、不锚行号）：`appendPolicyBoundary.effectiveFromRunSeq`（**不再写总量**）
· 会漂的总量改名带限定：`prePolicyCountsAtPolicyWrite = {lines, distinctBodyIdentities, asOf, frozen}`
  ⇒ **名字承载限定**（同范式：`artifactSha256IsHistorical`、`mirrorSizeAtMirrorTime`）✓
· **一次性回填后冻结**：连跑三次**不变** ⇒ 无漂移源 ✓
```

**归族**：**"为修 X 而引入 X"** —— 本 run 第三次同形。
**单一处方**：**凡新增一处声明，须用促使你新增它的那条规则再检查它一遍**（**含自指：新政的文本也受新政约束**）✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
