# -*- coding: utf-8 -*-
"""把 schematic-expert 的"修展开器必须连带修消费者"告诫并入纪律登记（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附二｜修改展开器时必须连带修消费者（解析器-消费者耦合）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B' % os.path.getsize(REG))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**触发**：schematic-expert 同时读了两侧代码后提出（我**最小复现验证**成立）。主题：**只改正则就提交 = 会崩或会静默漏报**。

**耦合事实（逐行 locator，已复核）**
```
parse_defines()   L42  r'#define\\s+(K\\d*_\\w+)\\s+(\\d+)'   ← 只捕获一段数字
                  L43  d[m.group(1)] = int(m.group(2))        ← **标量 int**
消费者            L376 n = defines[r]                          ← **假设 n 是标量**
                  L401 if n in on_set:                         ← on_set 是 **int 集合**（L103-106 `add(int(...))`）
                  L403 if n in nc_set:
                  L406 f'… {r}(K{n}) …'                        ← 字符串格式化也假设标量
```

**若只把展开器改成"返回多值"，消费者会当场出事（我实测最小复现）**
| 新返回类型 | `in` 判定结果 | 后果 |
| --- | --- | --- |
| 标量 `int 154`（现状） | `True` | 正常 |
| **`list [154,155]`** | **抛 `TypeError: unhashable type: 'list'`** | **门禁崩溃**（非静默） |
| **`tuple (154,155)`** | **恒 `False`** | **静默漏报**（更糟：看起来仍 PASS） |
| 正确修法 | —— | 把 **L401/L403/L406 改为逐值循环** |

**⇒ 归档结论（供下一位 owner）**
> `parse_defines()` 的**首值截断**与其消费者（L401/L403/L406）的**标量签名是耦合**的
> ⇒ **修该展开器必须同步改那三处**（标量→逐值循环），否则 = **崩（list）** 或 **静默漏报（tuple）**。
> 该项归 **scripts owner**，**本批不授权**（Captain 裁定），且**不得借机改 `gate_baseline.json`**（28 B / `021015da…02cb1d`）。
留证：`gate-logs-t54/t54_verify_expander_coupling.py` / `t54-expander-coupling.log`。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, 'unhashable type', '静默漏报', '逐值循环'):
    print('  含 %-34s %s' % (k, k in t2))
