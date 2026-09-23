# -*- coding: utf-8 -*-
"""并入 schematic-expert ②④ 的两条（幂等）：
  ② **引用"比较结论"时必须同时给出"哪一版投影"** —— 否则同一对比在不同投影下含义不同。
  ④ **"值"（身份主张）不得内引自证；"方法说明"（如何比较）不属身份主张** ——
     免得字面读法禁止在报告里记录哈希方案。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附十五｜比较结论必须标注"哪一版投影"；且"值"与"方法说明"须区分'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 由我方一处发现（`projectionSpec v1` 不完整 ⇒ 已升 v2）**反向更正其自己的旧结论**，并给出两条可推广规则。

**规则一｜比较结论须标注投影版本**
> **引用一组"比较结论"时，必须同时给出"哪一版投影"** ——
> **否则同一对比在不同投影下含义不同。**

**本 run 实例（其自陈更正）**
```
其旧论证（"body 恰好随真实编辑而变"）是在 **v1** 下测的：v1 只排除 `generatedAt`
  ⇒ **`receipts` 段的变动也会推动 body 值** ⇒ 该论证**混入了收据链 churn** ⇒ **不能严格成立**
更正后的干净形式（v2 口径）：**纯重生成 ⇒ body 恒定；仅真实编辑 ⇒ body 变化**
⇒ 故其那组数字应标注为"**测于 `projectionSpec v1`**"。
```
⇒ **判定上的意义**：**同一对比在不同投影下含义不同** ⇒ 与"哈希须连同比对口径引用"同源。

**规则二｜"值"与"方法说明"须区分**
> **"值"（身份主张）不得内引自证；"方法说明"（如何比较哈希）不属身份主张。**

**本 run 实例**：`standardTriHash` 同时留在**报告**与**收据** ——
**这不违反**"不得引用本文件内的任何自算哈希"，因为它是**如何比较哈希的用法说明**，不是**身份主张的值**。
**⇒ 若不写这一区分，字面读法会禁止在报告里记录哈希方案**（过度禁止）。

**附带（其自省，我方采纳）**：**未验证的机制应"先测再提"**；
其把候选解释标为 **UNKNOWN** 的做法**使该问题可被 settle、而不会变成假断言** ✓
—— **这正是"标注未验证"的价值**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
for k in (MARK, '哪一版投影', '方法说明', '先测再提'):
    print('  含 %-16s %s' % (k, k in t2))
