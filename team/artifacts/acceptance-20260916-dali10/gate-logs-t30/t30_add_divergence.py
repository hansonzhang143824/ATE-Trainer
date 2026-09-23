# -*- coding: utf-8 -*-
"""在 t30-summary.md §6 的 TM1205 行补 `divergence` 极性分歧（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SUM = os.path.join(HERE, 't30-summary.md')
MARK = '`divergence` 极性分歧（须随 rev 25 第 4 条携带）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(SUM, encoding='utf-8-sig').read()
if MARK in t:
    print('已补注（幂等）: %d B' % os.path.getsize(SUM))
    raise SystemExit(0)

anchor = '| **TM1205** | 契约 `bst2sw.usedByTm` 含 TM1205；但其实际通路是**变体行**：'
if anchor not in t:
    print('ERROR: §6 TM1205 行锚点未命中')
    raise SystemExit(1)

add = ('''

> ⚠️ **`divergence` 极性分歧（须随 rev 25 第 4 条携带）**（schematic-expert 指出、我复核成立）：
> `aliasFlatTable[14]/[15]` 契约自述："**POLARITY: for bst1_sw1 the connect-map puts SW1 on the HIGH terminal
> and BST1 on the LOW terminal, i.e. the opposite of bst2sw (BST high / SW low).** The 'BST must lead SW'
> invariant therefore cannot be satisfied by terminal assignment alone - the sign of the applied voltage matters.
> **Registered, not averaged; must be settled by t4/relay-trace.**"
> - **FACT**：`K_FPVIH_TO_SW1_A = 46`（FPVIe[H]→SW1）、`K_FPVIL_TO_BST1_A = 41`（FPVIe[L]→BST1）⇒ SW1 在 HIGH 端、BST1 在 LOW 端，确为 `bst2sw` 的**镜像**；
> - **INFERENCE**：把 TM1205 移到变体行时，E006 族不变量（"BST 须领先 SW"）由"端子指派"变为"**施加电压的符号**"问题；
> - **UNKNOWN**：DUT 是否容许 BST 低于 SW 及后果 ⇒ **未判定、未实测**。
> ⇒ **rev 25 第 4 条必须把该 `divergence` 一并带入 TM1205 的条目/计划**，否则"错归属 → 继承未结算的反极性"，
> 等于用一个缺陷换另一个缺陷；并应标给 **E006/DFT 意图归口方**（契约原文即写"须由 t4/relay-trace"）。
> 另：我 `gate-logs-t30/t30-verify-tm1205.log` 的宏展开**不全**（`parse_defines` 截断多值宏）⇒
> 以 `gate-logs-t33/t33-correction-2-divergence-and-macro.md` §1 的正确展开为准。
''')

idx = t.index(anchor)
end = t.index('\n', t.index('|', t.index('|', idx) + 1) if False else idx)
# 找到该表格行的行尾
line_end = t.index('\n', t.index('**登记错项**', idx))
io.open(SUM, 'w', encoding='utf-8', newline='').write(t[:line_end] + add + t[line_end:])
t2 = io.open(SUM, encoding='utf-8-sig').read()
print('已补注: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
print('  含 divergence 段 =', MARK in t2)
print('  含镜像事实 =', '确为 `bst2sw` 的**镜像**' in t2)
