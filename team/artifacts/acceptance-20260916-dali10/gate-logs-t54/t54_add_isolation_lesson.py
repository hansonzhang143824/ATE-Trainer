# -*- coding: utf-8 -*-
"""补：把"隔离输入 != 隔离输出"这一课并入登记（幂等）。内部引号一律用『』避免嵌套。"""
import io
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '### 附七·补｜『隔离输入』 ≠ 『隔离输出』（沙箱实验的输出路径问题）'

t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 逐字读到设计声明、并在我方执行日志里找到**相反的行为事实**。
```
设计文本声明：take an OFFLINE copy of t28-anchors.json (never the live shared file)
执行日志实测：WROTE …/t28-anchors.json (12204 B / 77842d64…) ⇒ 生成器把输出写到了 canonical 活路径
⇒ 实验期间活档被改写；活档无损靠事后人工还原（经字节级核对：同 size 同 sha ✓）
```
**正确留档（证据分层：行为层 > 声明文本）**
> 该实验**写入了 canonical 活路径**；还原经字节级核对、**结果无损**；
> 设计文本中 never the live shared file 属**当时意图**，**不是已实现的性质**。

**判据（其给出，我方采纳）**
> **『我用了副本』是关于输入的主张；『我没改变活档』是关于输出的主张 —— 二者需要各自的证据。**

**机制化（两半，缺一即会重演）**
| # | 动作 | 落地 |
| --- | --- | --- |
| (a) | **输出路径重定向**：沙箱实验改生成器的**输出目标**，而非只隔离输入 | 见 `t54_experiment_sandboxed.py`（`--out` 指向沙箱副本；**不写 canonical**） |
| (b) | **跑后断言**：收尾**先 assert 活档哈希 == 实验前哈希**，再写『无损』 | 已写成固定动作（脚本内 assert + 落盘） |

**属静默类**（还原若失败/不完整，被改的是一份**被引用的产物**且不易察觉）⇒ **按分诊须机制化** ✓
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B' % os.path.getsize(REG))
for k in (MARK, '输出路径重定向', '跑后断言', '二者需要各自的证据'):
    print('  含 %-20s %s' % (k, k in t2))
