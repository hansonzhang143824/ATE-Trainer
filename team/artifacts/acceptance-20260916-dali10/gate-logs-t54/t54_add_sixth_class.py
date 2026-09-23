# -*- coding: utf-8 -*-
"""① 确认两处歧义在现盘的实际状态（他们称"仍待处置"）；② 并入第六类"局部修复不安全"。"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN, 'build-report.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== ① 两处歧义的现盘状态（现算）===')
d = json.load(io.open(REPORT, encoding='utf-8-sig'))
c = d['contract']
print('  build-report.json = %d B / %s' % (os.path.getsize(REPORT), sha(REPORT)))
print('  contract 顶层键 =', list(c.keys()))
print('  顶层残留 size/sha256/mtime =', [k for k in ('size', 'sha256', 'mtime') if k in c], '（应为 []）')
print('  currentOnDisk =', json.dumps(c.get('currentOnDisk'), ensure_ascii=False)[:150])
if 'bst2sw_closedRelayNumbersSuperseded' in c:
    print('  closedRelayNumbersSuperseded =', c['bst2sw_closedRelayNumbersSuperseded']['value'], '（旧闭集）')
if 'bst2sw_supersededCh1VariantRelaySet' in c:
    print('  supersededCh1VariantRelaySet =', c['bst2sw_supersededCh1VariantRelaySet']['value'], '（CH1 变体）')
print('  旧名别名的 warning 在 =', 'warning' in (c.get('bst2sw_supersededRelaySet') or {}))

print('\n=== ② 并入第六类"局部修复不安全" ===')
MARK = '## 附三｜第六类：局部修复不安全（repair-local-but-unsafe）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）; 登记 %d B' % os.path.getsize(REG))
else:
    BLOCK = '''

---

''' + MARK + '''

**与前五类的区别**：前五类（模式≠形式／模式≠宏间接／范围≠归属／范围≠字段位置／工具≠语义）
都发生在**"找数/计数"**层面；本类讲的是**"修复"**层面：
> **一个看起来局部的缺陷（如一行正则），其正确修复可能要求连带改动它的消费者**；
> 改一半 ⇒ **崩**（显式，尚可发现）或**静默漏报**（隐性，最危险）。

**本 run 实例（已最小复现）**：`parse_defines()` 的 `(\\d+)` 只捕获首值；
其三个消费者 `L401 if n in on_set` / `L403 if n in nc_set` / `L406 f'… (K{n}) …'` **都假设标量**：
| 若只改展开器返回 | 结果 |
| --- | --- |
| `list` | `TypeError: unhashable type: 'list'` ⇒ **崩** |
| `tuple` | `in` 恒 `False` ⇒ **静默漏报**（看起来仍 PASS） |
| 正确 | **L401/L403/L406 改逐值循环** |

**配套动作**：**修任何 helper 前，先枚举它的消费者与其签名假设**（先查后改）。
⇒ 与纪律 4（工具≠语义 / **先测展开器再信展开**）成对：**前者管"用前先验"，本类管"改前先查"**。

**归属**：`scripts/` owner；**本批不授权改**（Captain 裁定）；且**不得借机改 `gate_baseline.json`**。
留证：`gate-logs-t54/t54_verify_expander_coupling.py` / `t54-expander-coupling.log`、本文件 §附二。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    t2 = io.open(REG, encoding='utf-8-sig').read()
    print('  已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
    for k in (MARK, '改前先查', 'unhashable type', '静默漏报'):
        print('    含 %-22s %s' % (k, k in t2))
