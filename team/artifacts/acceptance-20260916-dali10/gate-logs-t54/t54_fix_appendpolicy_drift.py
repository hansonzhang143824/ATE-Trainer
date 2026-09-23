# -*- coding: utf-8 -*-
"""按 schematic-expert ② 修我方 `appendPolicy` 自身引入的漂移源（幂等）：
  它硬记了"此前（1–54 行）"与"54 行里只有 5 个身份" ⇒ **被管辖账本的当前总量** ⇒
  **一旦策略今后真的追加一行 ⇒ 该字段自身失真**（＝"为修一个语义缺口而引入一个漂移源"）。
修法（采纳其 (ii) 与 L-b 范式）：
  · 边界写成**事件**（锚在制度边界，不锚在行号）：**本策略自 `runSeq = N` 起生效，此前的记录属"预策略段"**
  · 会漂的总量**改名带限定**：`prePolicyCountsAtPolicyWrite = {lines, distinctBodyIdentities, asOf}`
  ⇒ **名字承载限定**（与 `art/../artifactSha256IsHistorical`、`mirrorSizeAtMirrorTime` 同范式）
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

OLD = ('''    'appendPolicy': ('**本账本仅在身份（body 哈希，`projectionSpec` 口径）变化时追加**；'
                     '**因此"一段时间无增长"不等于"无运行"** —— 新策略下**运行可以发生而有意不记**。'
                     '**运行计数一律查 `runSeq`**（单调序号）。'
                     '⚠️ 本策略于本轮启用；此前（1–54 行）为**旧制度：每次运行都追加** ⇒ '
                     '故 **54 行里只有 5 个身份**，且**行数 ≠ 运行次数**（新旧两段口径不同）。'),''')
NEW = ('''    'appendPolicy': ('**本账本仅在身份（body 哈希，`projectionSpec` 口径）变化时追加**；'
                     '**因此"一段时间无增长"不等于"无运行"** —— 新策略下**运行可以发生而有意不记**。'
                     '**运行计数一律查 `runSeq`**（单调序号）。'
                     '⚠️ **制度边界（以事件表述、不锚行号）**：本策略自 "
                     "'**`runSeq = %d` 起生效**' % (len(_prev_lines) + 1) + "
                     '"，**此前的记录属【预策略段】：每次运行都追加** ⇒ '
                     '**预策略段内"行数 ≠ 运行次数"**（该段行数见 `prePolicyCountsAtPolicyWrite`）。'),''')
if 'prePolicyCountsAtPolicyWrite' in src:
    print('  appendPolicy 已改（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已改 appendPolicy（事件表述）→ %d B' % os.path.getsize(GEN))
else:
    print('  WARN: appendPolicy 锚点未命中')
    i = src.find('appendPolicy')
    print(repr(src[i:i + 300]) if i > 0 else '（未找到）')

# 加"带限定的历史计数"字段（名字承载限定）
src2 = io.open(GEN, encoding='utf-8-sig').read()
ANCHOR = "    'lastAppendDecision': {"
NEWF = ('''    'prePolicyCountsAtPolicyWrite': {
        'note': ('**预策略段（每次运行都追加的那一段）的行数与身份数 —— 取值为【本字段首次写入时】的测量**。'
                 '⚠️ 名字自带限定：**这是写入时刻的历史读数，不是账本当前总量**；'
                 '账本当前总量请现算（行数 / `runSeq` / 不同 `reproducibleBodySha256`）。'
                 '（采纳 schematic-expert 的 L-b 范式：**限定写在字段名里**。）'),
        'lines': None,          # 首次写入时回填
        'distinctBodyIdentities': None,
        'asOf': None,
        'frozen': True,
    },
''' + ANCHOR)
if 'prePolicyCountsAtPolicyWrite' in src2 and "'lines': None" in src2:
    print('  历史计数字段已含（幂等）')
elif ANCHOR in src2:
    out2 = src2.replace(ANCHOR, NEWF, 1)
    # 回填：仅当尚未回填（frozen 且 lines 为 None）
    OLD3 = "_appended = _rec.get('reproducibleBodySha256') not in _known_bodies"
    NEW3 = ("_ppc = _rec.get('prePolicyCountsAtPolicyWrite') or {}\n"
            "if _ppc.get('lines') is None:\n"
            "    _ppc['lines'] = len(_prev_lines)\n"
            "    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
            "    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')\n"
            "    _rec['prePolicyCountsAtPolicyWrite'] = _ppc\n"
            + OLD3)
    if OLD3 in out2:
        out2 = out2.replace(OLD3, NEW3, 1)
        ast.parse(out2)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out2)
        print('  已加历史计数字段 + 一次性回填 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 回填锚点未命中')
else:
    print('  WARN: lastAppendDecision 锚点未命中')

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')
for i in (1, 2, 3):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:66]))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  appendPolicy =', rec['appendPolicy'][:150], '…')
print('  prePolicyCountsAtPolicyWrite =', json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False))

print('\n=== 关键自证：策略若真追加一行，该字段**不变**（无漂移源）===')
a = json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False)
for i in (1, 2, 3):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
b = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('  连跑三次后 prePolicyCounts = ', json.dumps(b.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False))
print('  三次前后相同 =', a == json.dumps(b.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False), '⇒ **冻结、不再漂** ✓')

print('\n=== 规则入册 ===')
MARK = '## 附卅二｜同一个数字的两种地位：事件边界（稳定）vs 运行总量（必漂）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 指出我方 `appendPolicy` **自身引入了一个漂移源** ——
它硬记了"此前（1–54 行）"与"54 行里只有 5 个身份"，而**这两个数都是被管辖账本的当前总量** ⇒
**策略今后真的追加一行 ⇒ 该字段立刻失真** ⇒ **"为修一个语义缺口而引入一个漂移源"** ✓

**规则（其判据）**
> **同一个数字，两种地位**：
> · **事件边界**（如"**本策略自 `runSeq = N` 起生效**"）⇒ **是历史事件 ⇒ 永久稳定** ✓
> · **运行总量**（如"**共 54 行**"）⇒ **是当前测量 ⇒ 必然漂** ✗

**修法（采纳其 (ii) ＋ L-b 范式）**
```
· 边界写成**事件**（锚在制度边界，不锚行号）："本策略自 `runSeq = N` 起生效，此前的记录属【预策略段】"
· 会漂的总量**改名带限定**：`prePolicyCountsAtPolicyWrite = {lines, distinctBodyIdentities, asOf, frozen}`
  ⇒ **名字承载限定**（同范式：`artifactSha256IsHistorical`、`mirrorSizeAtMirrorTime`）✓
· **一次性回填后冻结**：连跑三次该字段**不变** ⇒ 无漂移源 ✓
```

**归族**：**"为修 X 而引入 X"** —— 本 run 第三次同形。
**单一处方**：
> **凡新增一处声明，须用促使你新增它的那条规则再检查它一遍**（**含自指：新政的文本也受新政约束**）✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
