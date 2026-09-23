# -*- coding: utf-8 -*-
"""按 schematic-expert ② 的建议，为该工具补**价值说明**（幂等）：把"双哈希"的理由写进工具自身。
并补 ③ 的状态措辞确认、④ 其自曝探针错误的现场违例记录。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 't54_snapshot_gate_inputs.py')
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = 'TOOL_RATIONALE_V1'

t = io.open(TOOL, encoding='utf-8-sig').read()
print('工具 %d B ; 已含价值说明 = %s' % (os.path.getsize(TOOL), MARK in t))
if MARK not in t:
    RATIONALE = '''# ==== ''' + MARK + '''：本工具的价值说明 ====
# 1) **归属从"自述"升级为"字节可证"**：把该次门禁运行的输入（契约 / 候选 payload / 基线）
#    复制成字节快照并与门禁日志同放 ⇒ 将来若被质疑"那次到底读的是哪一版"，有字节可证；
#    对应 `build-report.contract.gateExpectationSet.residualCaveat` 里那句
#    "不能声称已用字节证明读的是 rev 32" —— 本工具把它变成"**下一次运行可字节证明**"。
# 2) **双哈希（`sha256` + `sha256_lf_normalized`）—— 关掉我们踩过的真坑**
#    （schematic-expert 指出，我方采纳并记此价值说明）：
#    我们查 `t28-anchors.json` 漂移时，一度靠 `11,609 + 245 = 11,854` 才发现
#    "size 差来自 CRLF vs LF" ⇒ **size 与普通 sha 都会把"行尾变化"误报成"内容变化"**。
#    同时记 **原始 sha + LF 归一化 sha** ⇒ 后来者可区分
#    **"内容变了"** 与 **"只是行尾变了"** ⇒ **快照对照不再被编辑器行尾设置污染**。
# 3) **不改任何脚本、不改门禁、不动基线**（纯 copy）⇒ 与 Captain "不改门禁脚本"的裁定相容。
# ==========================================================================
'''
    lines = t.splitlines(keepends=True)
    ins = 0
    for i, l in enumerate(lines):
        if l.startswith('"""') and i > 0:
            ins = i + 1
            break
    lines.insert(ins, '\n' + RATIONALE + '\n')
    io.open(TOOL, 'w', encoding='utf-8', newline='').write(''.join(lines))
    print('  已插入价值说明 → %d B' % os.path.getsize(TOOL))

# 语法冒烟（改完必须能跑）
import subprocess
import sys
r = subprocess.run([sys.executable, TOOL, 't54-syntaxsmoke', '--dry-run'],
                   capture_output=True, text=True, encoding='utf-8')
print('  语法冒烟 exit=%d : %s' % (r.returncode, (r.stdout or r.stderr or '').strip().splitlines()[0][:80]))

# 纪律登记：并入其自曝探针错误的现场违例
t2 = io.open(REG, encoding='utf-8-sig').read()
M2 = '### 现场违例记录（规则的作者也会违反规则）'
if M2 in t2:
    print('  登记已含现场违例（幂等）')
else:
    BLOCK = '''

''' + M2 + '''

**来源**：schematic-expert 如实报备其本轮一处探针错误 —— 读 `manifest.items` 时**假设它是数组**、
直接按 list 迭代 ⇒ 取到空路径 ⇒ 把**目录**当文件读 ⇒ 被沙箱拒（`Permission denied`）。
**它违反的正是自己那条纪律**："**先打印容器与条数，再断言存在/形状**"。
```
正确做法：先 print 整个 items 结构 → 再按结构逐项比对（其修正方式）
⇒ 教训：**规则的作者也会违反规则，所以它才要写成机制，而不是写成提醒**
   （与我用**哨兵常量**替掉字符串包含、与"账本链式自证"替掉"只增承诺"同源）
```
**推论（纳入本 run 的元教训）**：
> **凡"靠自觉"的纪律都会被违反** —— 要么**机制化**（哨兵/链式自证/断言），
> 要么**接受它会被违反**并**在下游做检查**（如 `t54_postchange_verification.py` 的 25 项）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t2.rstrip() + BLOCK)
    print('  已并入现场违例 → 登记 %d B' % os.path.getsize(REG))
