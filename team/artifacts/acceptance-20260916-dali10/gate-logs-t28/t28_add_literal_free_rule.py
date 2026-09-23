# -*- coding: utf-8 -*-
"""把 rule-reviewer 的"免字面量核验法"并入 t28-freeze-correction.md 的纪律清单（幂等）。

新规则（第 6 条）：核验脚本中**禁止出现任何手写哈希字面量**；要构造变体一律由 ACTUAL 切片生成；
优先用「现算 == 现算」比较；差异定位用 zip 逐位比较而非人工逐位相减。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(HERE, 't28-freeze-correction.md')
MARK = '### 5.2 免字面量核验法（rule-reviewer 提议，2026-09-16）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(FC, encoding='utf-8-sig').read()
print('BEFORE: %d B' % os.path.getsize(FC))
if MARK in t:
    print('已写入（幂等）: %d B' % os.path.getsize(FC))
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**动因**：我方在核对 `t28-red-proof.json` 的哈希时，把两个"候选串"分两行写进同一表达式 ⇒
**Python 隐式拼接相邻字符串字面量**，两个候选实际变成同一个值 ⇒ 得出**"两个都错"的无效结论**。
⇒ 这不是"写得不够小心"的问题，而是**引入了字面量**的问题。

**规则（六条合一的第 6 条）**
> **核验脚本中禁止出现任何手写哈希字面量**（包括"两个候选分两行写进同一表达式"）：
> 1. 优先 **`hashlib.sha256(open(p,"rb").read()).hexdigest()` == 同法现值** ——「现算对现算」，天然免疫隐式拼接；
> 2. 需要构造**变体**（如"把第 42 位置为另一个字符"）时，**一律由 ACTUAL 切片生成**
>    （`actual[:41] + 'c' + actual[42:]`），**不得书写整串**；
> 3. 需要**定位差异**时用 `[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]`，
>    **不做人工逐位相减**（人工相减同样要求先把串抄进来）；
> 4. 需要**全串校验**时，用脚本内的**路径拼接**（`os.path.join` / `Path`），**不用字面量拼串**。

**附（独立坑）**：同一表达式里多个字符串字面量**只做比较**时不会被拼接，
但**一旦参与拼接/格式化就会被拼接** ⇒ **根本做法是不引入字面量**，而不是"小心地写"。

**本 run 五条既有纪律（第 1–5 条，与前文一致）**
1. 消息内不手抄长哈希（只给「路径 + size + 现算命令」）；
2. 一切读取/哈希用 python `rb`（DLW 保护下 pwsh 文本路径读到密文 ⇒ 假哈希/假 0 命中）；
3. **写文档脚本必须证明幂等**（同输入 N 次 ⇒ 同 `sha256`；否则改为"先剥离历史段再追加"）；
4. **单一真源必须由工具生成**（不得手写）；且**真源自身也须现算**（它也会被再次写入）；
5. **不得因自己探针报 `False` 就改认他方值** —— 应从文件现算 + 逐字符 diff 后再判。
'''
io.open(FC, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(FC, encoding='utf-8-sig').read()
print('AFTER : %d B / %s' % (os.path.getsize(FC), sha(FC)))
for k in (MARK, '禁止出现任何手写哈希字面量', '现算对现算', '不做人工逐位相减'):
    print('  含 %-26s %s' % (k, k in t2))
