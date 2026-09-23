# -*- coding: utf-8 -*-
"""按 rule-reviewer ① 的建议，在 §附五 处加**层级说明**（幂等）：
**同一性是粒度比较的前提** ⇒ 读序应为 附五·补 → 附五 → 时序/状态断言。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '**读序提示（层级）**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

### 附五·层级说明（rule-reviewer 指出，供排序）— 读序：**附五·补 → 附五 → 时序/状态断言**

```
附五·补（本文件下方） ：**时序比较**必须先有**同一性证据**
                       （要断言"A 变成 B" ⇒ 先证"两次看的是同一个 A"）
附五（主条）           ：**记录粒度**必须覆盖**断言粒度**
                       （要断言"条目" ⇒ 需**条目级记录**）
⇒ 逻辑顺序：**先认同一对象 → 再要求同粒度证据 → 才能做时序/状态断言**
⇒ 故**同一性是粒度比较的前提** ⇒ 阅读/引用时按此顺序理解。
```
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '同一性是粒度比较的前提', '先认同一对象'):
    print('  含 %-22s %s' % (k, k in t2))
