# -*- coding: utf-8 -*-
"""并入 rule-reviewer ②③（幂等）：
  ② **字段定义说明**（关键）：`prevLineSha256` = 上一行**原始行字节**的 sha256；
     `ledger_self_sha256` = 本行**语义摘要**的 sha256 ⇒ **二者不是同一个东西**，
     不写明定义 ⇒ 每个新读者都会像其一样用错定义（属 R3"前提式域声明"：把定义写在使用处）。
  ③ 新增纪律：**自一致性**（凡对某类产物主张某性质，必须对同类产物一致适用）。
并当场按其正确定义**逐行复核链**（自证）。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
J = os.path.join(HERE, 'build-report.receipts.jsonl')
GEN = os.path.join(HERE, 't54_make_report.py')
META = os.path.join(HERE, 'build-report.receipts.meta.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== ① 按其**正确定义**逐行复核链（自证）===')
lines = [l for l in io.open(J, encoding='utf-8').read().splitlines() if l.strip()]
print('  行数 =', len(lines), '｜ 文件 =', os.path.getsize(J), 'B')
ok = 0
bad = []
for i in range(1, len(lines)):
    prev = hashlib.sha256(lines[i - 1].encode('utf-8')).hexdigest()
    got = json.loads(lines[i]).get('prevLineSha256')
    if got == prev:
        ok += 1
    else:
        bad.append(i + 1)
print('  链有效行数 = %d/%d ⇒ CHAIN VALID = %s' % (ok, len(lines) - 1, not bad))
if bad:
    print('  异常行 =', bad)
first = json.loads(lines[0])
print('  首行 prevLineSha256 = %r（应为 None）' % first.get('prevLineSha256'))

print('\n=== ② 字段定义：写入头文件 + 生成器注释 ===')
meta = {}
if os.path.isfile(META):
    try:
        meta = json.load(io.open(META, encoding='utf-8-sig'))
    except Exception:
        meta = {}
meta.setdefault('ledger', 'build-report.receipts.jsonl')
meta['fieldDefinitions'] = {
    'prevLineSha256': '上一行**原始行字节**（不含换行符）的 sha256 —— **链用的就是它**',
    'ledger_self_sha256': '本行**语义摘要**（`json.dumps(本行, 不含该字段)` 与之前全部行的拼接）的 sha256 —— **不是链用的那个**',
    'live_sha256': '当次生成时刻、报告文件的**整文件**字节哈希',
    'live_lf_sha256': '同上，但**行尾归一化**（LF）后',
    'reproducibleBodySha256': '剔除 `generatedAt` 后的 **body** 哈希（幂等/内容判定用）',
}
meta['warning'] = ('⚠️ `prevLineSha256`（链）与 `ledger_self_sha256`（语义摘要）**不是同一个东西**；'
                   '用错定义会得到"看起来可信的错结论"（本 run 实测：rule-reviewer 首次即用错定义）。')
meta['appendOnly'] = True
meta['updatedAt'] = __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds')
io.open(META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=2))
print('  已写 %s (%d B)' % (os.path.basename(META), os.path.getsize(META)))

src = io.open(GEN, encoding='utf-8-sig').read()
if 'ledger_self_sha256 的定义' in src:
    print('  生成器注释已含定义（幂等）')
else:
    OLD = "_line['prevLineSha256'] = (_hl.sha256(_prev_lines[-1].encode('utf-8')).hexdigest() if _prev_lines else None)"
    NEW = ("# 字段定义（务必区分）：\n"
           "#   prevLineSha256    = 上一行**原始行字节**的 sha256 —— **链用的就是它**\n"
           "#   ledger_self_sha256= 本行**语义摘要**的 sha256 —— **不是链用的那个**（用错会得错结论）\n"
           + OLD)
    if OLD in src:
        out = src.replace(OLD, NEW, 1)
        import ast
        ast.parse(out)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
        print('  已加生成器注释 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 生成器锚点未命中')

print('\n=== ③ 新增纪律：自一致性 ===')
MARK = '## 附八｜自一致性（凡对某类产物主张某性质，必须对同类产物一致适用）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 采纳我方"把收据历史账本从**可选**改判为**必做**"的理由（**自一致性**），并建议入册。

**规则**
> **凡你对某类产物主张某性质（只增不改／不标 FROZEN／身份用哈希），必须对同类产物一致适用；不一致即缺陷。**
> **判据**：**主张会不会被自己的另一个产物违反？**

**本 run 首例依据（我方自陈）**
```
对 `t28-anchors` 主张"**只增不改**"，却让 `build-report.receipt.json` **每次覆写**
  ⇒ 只保留"最近一版"身份 ⇒ **与自身主张不一致** ⇒ 故必须另设 `build-report.receipts.jsonl`（append-only）
⇒ 它同时解释了**为何 (c) 必须比 (b) 更强**："便利指针"天然不满足"只增不改"，故**必须**历史账本。
```
**同位实例（本 run）**：`livenessDeclaration` 主张"**活档不得标 FROZEN**" ⇒
若另有一份同类活档被标 FROZEN，即违反本条（故报告与收据都必须自陈 LIVE）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

# 重新生成（让生成器注释生效）并复核
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:60] if tl else (r.stderr or '')[:120]))
lines2 = [l for l in io.open(J, encoding='utf-8').read().splitlines() if l.strip()]
ok2 = sum(1 for i in range(1, len(lines2))
          if json.loads(lines2[i]).get('prevLineSha256') == hashlib.sha256(lines2[i - 1].encode('utf-8')).hexdigest())
print('\n再验：行数 = %d ｜ 链有效 = %d/%d' % (len(lines2), ok2, len(lines2) - 1))
