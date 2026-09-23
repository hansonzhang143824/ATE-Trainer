# -*- coding: utf-8 -*-
"""按 rule-reviewer ⑤ 建议，把两条纪律判据写入 t28-freeze-correction.md §5（幂等）。

两条新增：
  (i)  幂等判据一句话化：同一脚本对同一输入运行 N 次，sha256 必须完全相同；
       若不同 ⇒ 脚本必须改为"先剥离历史段再追加"。
  (ii) 单一真源文件自身亦须现算：引用格式恒为「路径 + size + 现算命令」。
并把"只比较两次现算结果（sha256(a)==sha256(b)）"收紧为 §5 的核验口径。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(HERE, 't28-freeze-correction.md')
MARK = '### 5.1 幂等判据与核验口径（rule-reviewer 建议，2026-09-16）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(FC, encoding='utf-8-sig').read()
print('BEFORE: %d B' % os.path.getsize(FC))
if MARK in t:
    print('已写入（幂等）: %d B' % os.path.getsize(FC))
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**① 幂等判据（一句话，便于后来者复现）**
> 同一脚本对同一输入运行 N 次（N≥2，建议 3），产物 `sha256` **必须完全相同**；
> 若不同 ⇒ 该脚本必须改为"**先剥离历史段，再追加**"，并**给出 N 次的哈希作为验证**。

**② 核验口径（收紧"不手拼 expected"）**
> **只比较两次"现算结果"：`sha256(a) == sha256(b)`，或与产物内的冻结字段直接相等比较。**
> **禁止构造 expected 值、禁止手打哈希、禁止位级人工推理。**

理由：位级比较也要求人把某个字符串**先抄进核验链** —— 抄进来的那一刻就引入了新错误
（我方"把正确的 `c` 改成 `b`"正是这样发生的）。**现算对现算**则无需任何字面进入链中。

**③ 单一真源自身亦须现算**
> 单一真源文件（如 `gate-logs-t28/t28-anchors.json`）**也会被再次写入** ⇒ 其引用格式
> 恒为「**路径 + size + 现算命令**」，**不引用真源文件里的字面值**。

实证：该文件自身历经 5,794 B / 16 条 → 9,857 B / 29 条 → 10,255 B / 30 条 → **11,142 B / 32 条**（现盘）；
`t28-summary.md`、`t28-citation-notice.txt` 同样被多次写入。⇒ **"路径 + size + 现算命令"比任何字面值都稳。**

**④ 我方两次非幂等的完整留痕（供后来者对照）**
- 第 1 次：`t28-freeze-correction.md` 追加脚本未剥离历史段 ⇒ 3,594 → 6,001 → 8,408 B（同一脚本两次运行两个哈希）；
- 第 2 次：`t33-transition-plan.md` 同类问题 ⇒ 5,483 B（段落被追加两遍）；
- 两次均以"先剥离再追加 + 连跑验证"修复，且**旧哈希一律作废、引用现算**。
'''

io.open(FC, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(FC, encoding='utf-8-sig').read()
print('AFTER : %d B / %s' % (os.path.getsize(FC), sha(FC)))
for k in ('幂等判据（一句话', '只比较两次"现算结果"', '单一真源自身亦须现算', '两次非幂等的完整留痕'):
    print('  含 %-22s %s' % (k, k in t2))

# 幂等自证：再跑一次不应改变
