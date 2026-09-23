# -*- coding: utf-8 -*-
"""记录并机制化 schematic-expert ③ 的发现：**"隔离输入"≠"隔离输出"**。

事实（其逐字读到 + 我方日志实测）：
  设计声明（其档案文本）："take an OFFLINE copy … (never the live shared file)"
  执行实测（我方日志）：生成器**把输出写到了 canonical 活路径** ⇒ 实验期间活档被改写；
  活档无损靠**事后人工还原**（已字节级验证）。
⇒ 按证据分层（行为层 > 声明文本），留档须写成："该实验**写入了 canonical 活路径**；还原经字节级核对、结果无损；
   设计文本中 'never the live shared file' 属**当时意图**，不是**已实现的性质**。"

机制化（两半）：
  (a) **输出路径重定向** —— 沙箱实验必须改生成器的**输出**目标，而非只隔离输入；
  (b) **跑后断言** —— 实验收尾**先 assert 活档哈希 == 实验前哈希**，再写"无损"结论（固定动作）。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
GEN = os.path.join(HERE, 't54_make_report.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== ① 留档：行为层 vs 声明层（写入登记）===')
MARK = '### 附七·补｜"隔离输入" ≠ "隔离输出"（沙箱实验的输出路径问题）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

''' + MARK + '''

**来源**：schematic-expert 逐字读到设计声明、并在我方执行日志里找到**相反的行为事实**。
```
**设计文本声明**："take an OFFLINE copy of t28-anchors.json (**never the live shared file**)"
**执行日志实测**：`WROTE …\\t28-anchors.json (12204 B / 77842d64…)` ⇒ **生成器把输出写到了 canonical 活路径**
⇒ **实验期间活档被改写**；活档无损靠**事后人工还原**（经字节级核对：同 size 同 sha ✓）
```
**⇒ 正确留档（按证据分层：行为层 > 声明文本）**
> 该实验**写入了 canonical 活路径**；还原经字节级核对、**结果无损**；
> 设计文本中 "never the live shared file" 属**当时意图**，**不是已实现的性质**。

**判据（其给出，我方采纳）**
> **"我用了副本"是关于输入的主张；"我没改变活档"是关于输出的主张 —— 二者需要各自的证据。**

**机制化（两半，缺一即会重演）**
| # | 动作 | 本 run 落地 |
| --- | --- | --- |
| (a) | **输出路径重定向**：沙箱实验改生成器的**输出目标**，而非只隔离输入 | 见 `t54_experiment_sandboxed.py`：以 `--out` 指向沙箱副本；**不再写 canonical** |
| (b) | **跑后断言**：收尾**先 assert 活档哈希 == 实验前哈希**，再写"无损" | 已写成固定动作（脚本内 assert + 落盘） |

**属"静默类"**（还原若失败/不完整，被改的是一份**被引用的产物**且不易察觉）⇒ **按分诊须机制化** ✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== ② 给 build-report 的 mustNotBeCitedAs 增第二条禁止推论 ===')
src = io.open(GEN, encoding='utf-8-sig').read()
OLD = "'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'\n                             '属**原理上不可测**。'),"
NEW = ("'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'\n"
       "                             '属**原理上不可测**。'\n"
       "                             '⚠️ **亦不得**引作 **(iv) 历史 8→1 丢失之原因** 的证据 —— '\n"
       "                             '本实验测的是**当前生成器行为**，**不说明当年那次丢失由何导致**'\n"
       "                             '（与"当前行为不为历史修订作证"同一时域纪律）。'),")
if '亦不得**引作 **(iv)' in src:
    print('  已含（幂等）')
elif OLD in src:
    io.open(GEN, 'w', encoding='utf-8', newline='').write(src.replace(OLD, NEW, 1))
    print('  已增第二条禁止推论 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中（打印上下文）')
    i = src.find('mustNotBeCitedAs')
    print(repr(src[i:i + 200]) if i > 0 else '（未找到）')

import ast
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('  语法 OK')
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成末行:', (r.stdout or '').strip().splitlines()[-1][:70] if r.stdout else (r.stderr or '')[:120])
