# -*- coding: utf-8 -*-
"""更正我方一处"不可复核"误判：`aliasFlatTable` 是契约**顶层**字段（16 条），
`aliasFlatTable[14]/[15]` 确实存在（bst1_sw1 / bst2_sw2 变体行）。幂等写入 t30-summary.md §6。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SUM = os.path.join(HERE, 't30-summary.md')
C = json.loads(open(os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                                 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))
MARK = '**更正（我方自查）：`aliasFlatTable` 是契约顶层字段'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


aft = C.get('aliasFlatTable') or []
rows = {14: aft[14] if len(aft) > 14 else {}, 15: aft[15] if len(aft) > 15 else {}}

t = io.open(SUM, encoding='utf-8-sig').read()
if MARK in t:
    print('已更正过（幂等）: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
    raise SystemExit(0)

anchor = '| `TM108/TM109` | 契约 `pgnd2sw.usedByTm` 含二者，但该别名属 **ramp 段**，Step 1 不闭合 | 属"作用域语义"问题，非本缺陷；纳入即误报 |'
note = (anchor + '\n'
        '| **TM1205** | 契约 `bst2sw.usedByTm` 含 TM1205；但其实际通路是**变体行**：'
        '`aliasFlatTable[14] bst1_sw1`、`[15] bst2_sw2`（契约**顶层**字段，共 16 条） | '
        '**登记错项**（BST1/BST2 ≠ BST）⇒ 把 `[110,61]` 套给它亦会假红；**且 TM1205 不在本门禁默认作用范围** '
        '⇒ 当前不产生假红。**建议并入 rev 25 消歧**（Captain 已升为第 4 条待办） |\n'
        '| ' + MARK + '**：`aliasFlatTable` 是契约**顶层**字段（本契约共 16 条），'
        '不是 `tmDeltas.<TM>` 的子字段 —— 我先前只查了 `tmDeltas.TM1205.aliasFlatTable`（0 条）并**误报"不可复核"**，'
        '**该误报作废**。实测 `aliasFlatTable[14]` = `bst1_sw1`（`variantOf=bst2sw`，'
        '`relayPath="CH0 High -> SW1 需闭合 K46 ; CH0 Low -> BST1 需闭合 K41"`）、`[15]` = `bst2_sw2`，'
        '与部署态 `test.cpp:8791`（`K_FPVIH_TO_SW1_A=46` + `K_FPVIL_TO_BST1_A=41`）完全对齐 ⇒ **对方向我指出的 locator 是正确的**。 |')
if anchor not in t:
    print('ERROR: §6 锚点未命中')
    raise SystemExit(1)
t = t.replace(anchor, note, 1)
io.open(SUM, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(SUM, encoding='utf-8-sig').read()
print('已更正: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
for k in ('aliasFlatTable` 是契约顶层字段', '该误报作废', 'bst1_sw1'):
    print('  含 %-30s %s' % (k, k in t2))
print()
print('  契约 aliasFlatTable 顶层条目数 =', len(aft))
for i in (14, 15):
    if len(aft) > i:
        r = aft[i]
        print('  [%d] alias=%-10s variantOf=%-8s relayPath=%s'
              % (i, r.get('alias'), r.get('variantOf'), str(r.get('relayPath'))[:70]))
