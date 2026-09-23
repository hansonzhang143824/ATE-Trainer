# -*- coding: utf-8 -*-
"""修正：`appendPolicy` 里的动态值（制度边界）**必须在有 `_prev_lines` 的收据段**写入，
报告段无该变量（我上一版因此 `NameError` ⇒ 生成器一度不可跑，已按"改后必须复验"抓出）。

正确结构：
  · 报告 `appendPolicy`：**只写策略语义**（无任何会漂的量）
  · 收据 `appendPolicyBoundary`：**事件表述的动态边界**（`runSeq` 起效点）+ 带限定的历史计数
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

# ① 把报告段 appendPolicy 里的动态表达式去掉（只留语义）
i = src.find("'appendPolicy'")
j = src.find("'countUnitNote'")
OLD = src[i:j]
NEW = ("    'appendPolicy': ('**本账本仅在身份（body 哈希，`projectionSpec` 口径）变化时追加**；'\n"
       "                     '**因此\"一段时间无增长\"不等于\"无运行\"** —— 新策略下**运行可以发生而有意不记**。'\n"
       "                     '**运行计数一律查 `runSeq`**（单调序号）。'\n"
       "                     '⚠️ **制度边界以事件表述、不锚行号**：本策略生效点与【预策略段】规模见收据的 '\n"
       "                     '`appendPolicyBoundary`（**该字段带限定名、且证明冻结**）。'),\n")
if '_prev_lines' not in OLD:
    print('  报告段已是纯语义（幂等）')
else:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已把报告段改为纯语义（去动态表达式）→ %d B' % os.path.getsize(GEN))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

# ② 收据段：加带限定的边界 + 一次性冻结
src2 = io.open(GEN, encoding='utf-8-sig').read()
if 'appendPolicyBoundary' in src2:
    print('  收据边界字段已含（幂等）')
else:
    OLDF = "    'prePolicyCountsAtPolicyWrite': {"
    if OLDF in src2:
        # 已有占位字段 ⇒ 补动态边界写入逻辑
        pass
    ANCH = "_ppc = _rec.get('prePolicyCountsAtPolicyWrite') or {}"
    NEW_ANCH = ("_rec['appendPolicyBoundary'] = {\n"
                "    'text': ('本策略自 **`runSeq = %d` 起生效**；此前 %d 行（即【预策略段】）为旧制度：每次运行都追加'\n"
                "             '⇒ 该段内行数 ≠ 运行次数。' % (len(_prev_lines) + 1, len(_prev_lines))),\n"
                "    'effectiveFromRunSeq': len(_prev_lines) + 1,\n"
                "    'note': ('**事件表述**（自哪个 runSeq 起生效）⇒ 作为历史事件永久稳定；'\n"
                "             '**不写『账本当前共多少行』**（那是当前测量、必然漂）。'),\n"
                "}\n"
                "if 'prePolicyCountsAtPolicyWrite' in _rec and (_rec['prePolicyCountsAtPolicyWrite'] or {}).get('lines') is None:\n"
                "    _ppc0 = _rec['prePolicyCountsAtPolicyWrite']\n"
                "    _ppc0['lines'] = len(_prev_lines)\n"
                "    _ppc0['distinctBodyIdentities'] = len(_known_bodies - {None})\n"
                "    _ppc0['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')\n"
                + ANCH)
    if ANCH in src2:
        out2 = src2.replace(ANCH, NEW_ANCH, 1)
        ast.parse(out2)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out2)
        print('  已加 appendPolicyBoundary + 一次性冻结 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 收据段锚点未命中')
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置2：语法 OK')

for i in (1, 2, 3):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    err = (r.stderr or '').strip().splitlines()
    print('  run%d: exit=%d %s' % (i, r.returncode, ' | '.join(tl)[:50] if tl else (err[-1][:80] if err else '')))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  收据含 appendPolicyBoundary =', 'appendPolicyBoundary' in rec)
print('  边界文本 =', (rec.get('appendPolicyBoundary') or {}).get('text', '')[:110])
print('  effectiveFromRunSeq =', (rec.get('appendPolicyBoundary') or {}).get('effectiveFromRunSeq'))
print('  prePolicyCounts =', json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False))
a1 = json.dumps(rec.get('appendPolicyBoundary'), ensure_ascii=False) + json.dumps(rec.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False)
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
b = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('  再跑两次后两者均不变 =',
      a1 == json.dumps(b.get('appendPolicyBoundary'), ensure_ascii=False) + json.dumps(b.get('prePolicyCountsAtPolicyWrite'), ensure_ascii=False),
      '⇒ **冻结、无漂移源** ✓')
