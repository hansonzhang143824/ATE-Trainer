# 更正记录二：宏展开截断 + `aliasFlatTable` 的 `divergence` 字段

- 触发：schematic-expert 两处指出（① 我的 `K_FPVIL_TO_BST2_A` 展开不全；② `aliasFlatTable[14]/[15]` 自带
  `divergence` 极性分歧字段，须随 rev 25 第 4 条一并携带）。
- 我方复核：**两处均成立**（本记录给出实测与影响范围）。

## 1. ⚠️ 根因：`verify_relay_trace.parse_defines()` **把多值宏截断为首个数字**

实测（`gate-logs-t33/t33_verify_divergence.py` → `t33-divergence-verify.log`）：
```
StdAfx.h 原文:
  #define K_FPVIH_TO_SW2_A 46,49 // FPVIe[H] -> SW2: K46_BUS0_FH_SW1 + K49_ACM5_SW2
  #define K_FPVIL_TO_BST2_A 41,43 // FPVIe[L] -> BST2: K41_BUS0_FL_BST + K43_ACM4_BST2
parse_defines() 返回:
  K_FPVIH_TO_SW2_A → 46      （漏 49）
  K_FPVIL_TO_BST2_A → 41     （漏 43）
  K_FPVIH_TO_BST_A → 46      （漏 48,76！）
```
⇒ **`parse_defines` 只返回首个数字**，属**多值宏的静默截断**。我 `t30_verify_tm1205.py` 用它做展开，
于是 `t30-verify-tm1205.log` L7 写成 `K_FPVIL_TO_BST2_A=41`（正确为 `41,43`）——**该行为不全，已作废**。

**正确展开（本次实测）**：
```
L8791 SetOn(K_FPVIH_TO_SW1_A, K_FPVIL_TO_BST1_A, K13, K65) → {13,41,46,65}          ⊇ aliasFlatTable[14].kNumbers {46,41}
L8835 SetOn(K_FPVIH_TO_SW2_A, K_FPVIL_TO_BST2_A, K13, K65) → {13,41,43,46,49,65}    ⊇ aliasFlatTable[15].kNumbers {46,49,41,43}
```
⇒ **与变体行恰好是超集关系**（多出 13/65 = 轨电容与 nQON 上拉），比我先前的表述更严丝合缝。

**影响范围（重要）**：
- **不影响我的门禁判据**：`scripts/verify_bst_sw_sequence.py` **不引用 `parse_defines`**（其源码不含 `aliasFlatTable`、
  不含宏展开），期望集只读 `aliasResolution[*].resolution.closedRelayNumbers`；
- **可能影响其它读者的推理**：凡用 `parse_defines()` 展开复合宏的地方（包括我自己的探针、也可能包括他人的分析），
  都可能**少算继电器**。⇒ **建议**：凡要判定"某宏闭了哪些 K"，**一律以 `StdAfx.h` 原文逐字展开**，
  或改用能返回全量的解析；**不要用 `parse_defines()` 做多值宏展开**。

## 2. `aliasFlatTable[14]/[15]` 的 `divergence` 字段（契约自述，逐字）

```
[14] bst1_sw1 : "POLARITY: for bst1_sw1 the connect-map puts SW1 on the HIGH terminal and BST1 on the LOW
                 terminal, i.e. the opposite of bst2sw (BST high / SW low). The 'BST must lead SW' invariant
                 therefore cannot be satisfied by terminal assignment alone - the sign of the applied voltage
                 matters. Registered, not averaged; must be settled by t4/relay-trace."
[15] bst2_sw2 : "same polarity divergence as bst1_sw1 (SW on the HIGH terminal)."
```

**FACT（连通性依据，可由 `StdAfx.h` 复核）**：`K_FPVIH_TO_SW1_A = 46`（「FPVIe[H] -> SW1」）、
`K_FPVIL_TO_BST1_A = 41`（「FPVIe[L] -> BST1」）⇒ **SW1 挂 HIGH 端、BST1 挂 LOW 端**，
与 `[14].relayPath`（`CH0 High -> SW1 需闭合 K46 ; CH0 Low -> BST1 需闭合 K41`）一致，**确为 `bst2sw` 的镜像**。

**INFERENCE（供裁量，非本记录裁定）**：`bst2sw` 的不变量是"BST 须领先 SW"（E006 族）；
在极性反转变体上它由"端子指派问题"变为"**施加电压的符号问题**"（契约原话即此）。

**UNKNOWN（电性）**：DUT 是否容许 BST 低于 SW 及其后果 ⇒ **未判定、未实测**。

**⇒ 对 rev 25 第 4 条的要求（采纳 schematic-expert 的意见）**：
把 TM1205 从 `bst2sw.usedByTm` 移到 `bst1_sw1`/`bst2_sw2` 时，**必须把该 `divergence` 一并带入** TM1205 的条目/计划，
并**标给 E006/DFT 意图的归口方**（契约原文写"须由 t4/relay-trace 结算"）。
否则等于"用一个缺陷换另一个缺陷"：**错归属 → 继承未结算的反极性**。

## 3. 我方两处产物需随本记录理解

| 产物 | 状态 |
| --- | --- |
| `gate-logs-t30/t30-verify-tm1205.log` | **L6/L7 的展开不全**（`K_FPVIL_TO_BST2_A=41` 应为 `41,43`、`K_FPVIH_TO_SW2_A=46` 应为 `46,49`）⇒ **以本记录 §1 的正确展开为准** |
| `gate-logs-t30/t30-summary.md` §6（TM1205 行） | 归属结论**成立**（`aliasFlatTable[14]/[15]` 可复核）；**但须补 `divergence` 极性分歧**（本轮已补注） |

## 4. 边界
静态连通性/头文件/宏展开层面；**FACT 均附实测**；**非电性结论**；**无机台实测**；**编译闭环 ≠ 电性签核**。
