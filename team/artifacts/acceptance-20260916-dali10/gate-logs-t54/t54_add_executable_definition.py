# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 落地：把 `prevLineSha256` 的定义从**描述式**改成**可执行式**，
并核实"我方生成器实际用的是哪种口径"（该文件是 CRLF）。

其四种候选实测：原样(保留 \r) ⇒ 53/53 不符；**去尾部 \r** ⇒ 0/53 通过；加 \n / 加 \r\n ⇒ 不符。
⇒ 唯一口径 = **上一行去掉行终止符（CRLF）后的字节哈希**。
"""
import collections
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
H = os.path.join(HERE, 'build-report.receipts.jsonl')
META = os.path.join(HERE, 'build-report.receipts.meta.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
GEN = os.path.join(HERE, 't54_make_report.py')

raw = open(H, 'rb').read()
print('=== ① 文件真实行尾 ===')
print('  CRLF 次数 = %d ｜ 孤立 LF = %d' % (raw.count(b'\r\n'), raw.count(b'\n') - raw.count(b'\r\n')))

print('\n=== ② 四种口径实测（复现其过程）===')
lines = raw.split(b'\n')
lines = [l for l in lines if l.strip()]
rows = [json.loads(l.decode('utf-8')) for l in lines]


def mism(transform):
    bad = 0
    for i in range(1, len(lines)):
        prev = transform(lines[i - 1])
        if hashlib.sha256(prev).hexdigest() != rows[i].get('prevLineSha256'):
            bad += 1
    return bad


cands = {
    'split 原样（保留 \\r）': lambda b: b,
    '去掉尾部 \\r': lambda b: b.rstrip(b'\r'),
    '去掉尾部 \\r\\n': lambda b: b.rstrip(b'\r\n'),
    '行尾加 \\n': lambda b: b + b'\n',
    '行尾加 \\r\\n': lambda b: b + b'\r\n',
}
for name, tr in cands.items():
    print('  %-24s ⇒ 不匹配 = %d / %d' % (name, mism(tr), len(lines) - 1))

print('\n=== ③ 我方生成器实际写的口径 ===')
src = io.open(GEN, encoding='utf-8-sig').read()
i = src.find('prevLineSha256')
print('  生成器代码：', repr(src[i - 40:i + 130]))

print('\n=== ④ 把定义改成**可执行式**（meta + 生成器注释）===')
m = json.load(io.open(META, encoding='utf-8-sig'))
m.setdefault('fieldDefinitions', {})
m['fieldDefinitions']['prevLineSha256'] = (
    "sha256( 上一行的字节，**去掉其行终止符** ) —— 本文件为 CRLF ⇒ `\\r` 一并去掉；"
    "**等价实现**：`hashlib.sha256(prev_line_bytes.rstrip(b'\\r\\n'))`")
m['fieldDefinitions']['ledger_self_sha256'] = (
    "sha256( 之前全部行（**原样，含行尾**）与**本行语义摘要**的拼接 ) —— **不是链用的那个**")
m['executableDefinitionRule'] = (
    "定义必须写成**可执行形式**（procedure），不是**可解释描述**（description）——"
    "描述会被二次解释，而二次解释在执行前不会被发现。"
    "（本 run 实测：schematic-expert 读过本档警告后，仍按『只去 \\n』实现 ⇒ 得到 53/53 假 mismatch）")
m['warning'] = (m.get('warning', '') + ' ｜ 另：本文件为 CRLF ⇒ 『不含换行符』须明确为**去掉 CRLF**。')
io.open(META, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2))
print('  meta 已改 → %d B' % os.path.getsize(META))

if 'CRLF ⇒ rstrip' in src:
    print('  生成器已含（幂等）')
else:
    OLD = "    _prev_lines = [l for l in io.open(_hist_p, encoding='utf-8').read().splitlines() if l.strip()]"
    NEW = ("    # 读**字节**并去掉行终止符（本文件为 CRLF ⇒ \\r 一并去掉）；与 meta 的可执行定义一致\n"
           "    _raw = open(_hist_p, 'rb').read()\n"
           "    _prev_lines = [l for l in _raw.split(b'\\n') if l.strip()]")
    if OLD in src:
        src = src.replace(OLD, NEW, 1)
        # prevLineSha256 改为对字节算
        src = src.replace(
            "_line['prevLineSha256'] = (_hl.sha256(_prev_lines[-1].encode('utf-8')).hexdigest() if _prev_lines else None)",
            "_line['prevLineSha256'] = (_hl.sha256(_prev_lines[-1].rstrip(b'\\r\\n')).hexdigest() if _prev_lines else None)  # CRLF ⇒ rstrip",
            1)
        src = src.replace(
            "('\n'.join(_prev_lines) + '\n' + _json.dumps(_line, ensure_ascii=False)).encode('utf-8')",
            "(b'\\n'.join(_prev_lines) + b'\\n' + _json.dumps(_line, ensure_ascii=False).encode('utf-8'))",
            1)
        import ast
        ast.parse(src)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(src)
        print('  生成器已改 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 生成器锚点未命中')

print('\n=== ⑤ 规则入册 ===')
MARK = '## 附十九｜定义必须写成**可执行形式**（procedure），不是可解释描述'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 在**读过并引用过我方 `receipts.meta.json` 的警告之后**，仍按
"只去掉 `\\n`"实现校验 ⇒ 得到 **53/53 mismatch** 的**假结论"链已断"**；其用**四种候选口径**实测才定位到真定义。

**判据（其给出，我方采纳）**
> **"写在文档里的定义，如果读两遍能得到两种实现，那它还没被定义完。"**
> ⇒ **定义必须是"可执行的形式"（procedure），不是"可解释的描述"（description）** ——
> **因为描述会被二次解释，而二次解释在执行前不会被发现。**

**本 run 实证（歧义来源＝CRLF）**
```
本文件为 **CRLF**（实测 CRLF=54 / 孤立 LF=0）
· "split 原样（保留 \\r）" ⇒ 53/53 不符   · **"去掉尾部 \\r" ⇒ 0/53 通过** ★
· "行尾加 \\n" ⇒ 不符                    · "行尾加 \\r\\n" ⇒ 不符
⇒ 唯一口径 = **上一行去掉行终止符（CRLF）后的字节哈希**；
  我方旧描述"不含换行符"**在 CRLF 上有歧义**（可读成"只去 \\n"），两种读法给出**相反结论** ✓
```
**落地**：`fieldDefinitions.prevLineSha256` 改为可执行式
（`sha256(prev_line_bytes.rstrip(b'\\r\\n'))`），生成器改为**读字节 + rstrip**，并加 `executableDefinitionRule`。

**附带（其正面结论，我方采纳）**：**警告不能防止错误，但能让错误在二次校验中被识别** ——
该警告本身值得写下来（其"恰好被击中也说明它有必要"）✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

import subprocess
import sys
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:70]))

raw2 = open(H, 'rb').read()
L2 = [l for l in raw2.split(b'\n') if l.strip()]
R2 = [json.loads(l.decode('utf-8')) for l in L2]
bad = sum(1 for i in range(1, len(L2))
          if hashlib.sha256(L2[i - 1].rstrip(b'\r\n')).hexdigest()
          != R2[i].get('prevLineSha256'))
print('\n改后链校验（去 CRLF 口径）：不匹配 = %d / %d' % (bad, len(L2) - 1))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
