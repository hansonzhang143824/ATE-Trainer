# t52 最终 verdict（绑定停写字节）：pass

- 出具人：rule-reviewer · 日期：2026-09-16 · 任务：`t52`（最终）
- **对象（Captain ① 正式定性的停写字节）**：
```
implementation-payload-TM600-TM601.cpp
  = 43,806 B
  = 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4
  @ 2026-09-16 21:09:24
```
- **只读**：本次仅写本文件；未改 payload / 契约 / 计划 / 门禁 / 两棵树。
- **边界**：**非电性结论**；**无机台实测**；**编译闭环 ≠ 电性签核**。

## 0. verdict
> ## **verdict = `pass`**
> **绑定上述 `43,806 / 66abc088…` 字节；不覆盖任何历史版本**（`2d0984d9…`/39,457、`6034af71…`/41,797、`c03632d9…`/42,998 均为历史）。
> **若该文件被再次写入，本 verdict 立即失效，须由我按新字节重出。**

## 1. 对象一致性（我现算，与 Captain 定性逐位一致）
```
size  = 43,806 B                ✓
sha256 = 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4   ✓
mtime  = 21:09:24               ✓（停写以来未变；连读两次一致）
```

## 2. 形态与文本规范（与 Captain ② 独立复算一致）
| 项 | 实测 | 判定 |
|---|---|---|
| BOM | 存在（`EF BB BF`） | ✅ |
| 行尾 | **CRLF 566 处、孤立 LF 0 处** | ✅ |
| `SUPERSEDED` 标记 | **2 处**（保留供溯源） | ✅ |

## 3. 内容键（去注释后可执行计数）
```
K48_ACM5_AMP_REF = 1 、K76_ACM_BST = 1
K109_BUSL1_PB0   = 0 、K110_ACM18_BST = 0
K46_BUS          = 0
TM600 SetOn(L264) = [13, 48, 57, 60, 61, 76, 83, 85, 126]     ← 含 K48/K76、无 K109/K110
TM601 SetOn(L471) = [13, 57, 60, 61, 85, 126, 154, 155]       ← 无 ch5 端点
**无任何 SetOn 同时含 K48 与 K109**（并集已不存在；`t38` 的 TM601 移除已生效）
```
⇒ **"闭错"（闭 `K109/K110`）已消除；"漏闭"仅存在于部署态** ✓ 与 Captain ② 一致。

## 4. 硬约束 / 不变量 / 负列表
`delay_ms(1)`=6、**`delay_ms(2)`=0（2 ms 脉冲硬上限满足）**、`delay_ms(3)`=2、`SetClamp(50,50)`=2、`ERROR_RES`=2、`K126_V1P5_CAP`=2、`K57_CAP_BST_SW`=2、`K5_VBUS_Cap`=0、`K44_Cap_SW2_BST2`=0、`K45_Cap_SW1_BST1`=0、`K46_BUS`=0 ✅
**负列表**（`87/88/89/90/91/131/132/134/135`）**可执行命中全 0** ✅（口径："不得加入 required-on、不得驱动其动作"）

## 5. 三项新增项（终判）
- **(a) 排他性前提已写入注释** ✅ 正确且**未混淆**：注释含 `cbite-qtmue` 引用与 `exclusive` / `All unspecified` 原文；**未把排他性当作"配对 `RELAY_OFF` 已满足"的证据**（`RELAY_OFF` 仍显式给出）。
- **(b) 并集安全性的承重前提** ✅：**`PB0_BST_ACM` 命中 0**；**`L378 FPVI1.Set(FV, 0, …, FPVIe_RELAY_OFF)` 显式释放 ch1**（注释 `channel 1 (BST-SW loop) releases first`）。
  ⇒ **判定（INFERENCE）**：本版安全性依赖**输出纪律**，**非继电器排他性所强制** ⇒ **须入 `t34` 限制清单**（若后续驱动 `PB0_BST_ACM` 或去掉 `L378`，安全性失效）。
- **(c) `t38` 移除已生效** ✅（TM601 `.Set`=0；payload 不含部署态字节引用，未混述）

## 6. ⚠️ 契约侧：Captain ④ 引的 **rev 27 已被 rev 36 取代**，且**要求的那一项已完成**
我实测**现盘** `setup-contract.json` = **376,308 B / `d9ecffb0f81994be13c5ef83f8312b20d0fc57295b6ac10195d60f6e7d47ce59` / `revision: 36`**：
```
aliasResolution[bst2sw].resolution.closedRelayNumbers = [48, 60, 61, 76]      ← **已改为生效值**（Captain ④ 的核心要求已达成）
relayChain[0] = {"relay":"K48_ACM5_AMP_REF","state":"SetOn (ACM200 S5_FH5 -> BST leg; paired with K76_ACM_BST)"}  ← 归属已更正
channelsInScope.BST ← 请 owner 复核是否仍为 "S5_ACM200_FH18/SH18 (K110_BST)"
新增：closedRelayNumbersSuperseded=[110,61] / relayChainSuperseded / evidenceCh5 / evidenceSupersededChannel1 / consistencyAudit
```
**⇒ 门禁读取路径已验证**：`scripts/verify_bst_sw_sequence.py` **`L372`** 逐字读 `aliasResolution[*].resolution.closedRelayNumbers` ⇒ **现盘取到 `[48,60,61,76]`** ⇒ **`110` 已不在期望集，不会产生 `missing=[110]`** ⇒ **`t53` 的"修正未落进门禁所读字段"这一时效点已消除**。
**⇒ 期望集**：`t30` 对 TM600 = **`{48,60,61,76,83}`**（契约条目值 `{48,60,61,76}` ∪ `pmid2sw` 的 `{83}`；两者为**不同层次**，非互斥数字）。
**⇒ 仍请 owner 复核**：`channelsInScope.BST` 的归属是否已改（这是 Captain ④ 清单里我唯一无法确认已落的一项）。

## 7. 不覆盖 / UNKNOWN
- **不覆盖**：所有历史 payload 版本；`t40`/`t42`/`t43` 的字节级结论适用于其各自登记的字节。
- **UNKNOWN（不声称）**：机台层电气行为；`SW1_F/SW2_F` 本工况占用状态；`K110` 机械保持语义（`IM06DJR` 未核手册）。
- **闭集 `{48,60,61,76}` 属"由生产行为/契约推出的 INFERENCE"**，**非机台签核**。

## 8. 🔴 验证局限（本 verdict 的适用边界，必须一并引用）
**新发现并经我独立复现**：`scripts/verify_relay_trace.py` 的 `parse_defines()` **静默截断多值宏**。
```
L39-44  def parse_defines(src):
L42         for m in re.finditer(r'#define\s+(K\d*_\w+)\s+(\d+)', src):
L43             d[m.group(1)] = int(m.group(2))          ← 正则只吃**第一段数字**
```
**我实测**：`StdAfx.h` 中**多值宏 209 条，209 条全部被截断为第一个数字（100%）**：
```
K_FPVIH_TO_BST_A   真值 46,48,76                    → defines 记 46
K_FPVIL_TO_SW_A    真值 60,61                       → defines 记 60
K_BST_ACM          真值 48,76                       → defines 记 48
K_FPVIH_TO_ACDRV1_B 真值 136,137,143,144,22,30       → defines 记 136
```
**影响面（我逐脚本核实）**：
```
verify_relay_trace.py     parse_defines 使用 1 处、defines[...] 使用 2 处     ⇒ **受本缺陷影响**
verify_bst_sw_sequence.py parse_defines 使用 0 处、defines[...] 0 处、import 0 ⇒ **不受影响**
```
⇒ **结论（三条，务必与 verdict 同时引用）**：
1. **`bst-sw` 的期望集与判定不受本缺陷影响**（该脚本零引用）⇒ **本 verdict 的 `pass` 不因本项而动摇**；
2. **`relay-trace` 的 PASS 不构成对"多值宏路线"的证据** —— 凡以 `defines[name]` 作为"该名字闭合哪些继电器"判据处，宏路线被**少算** ⇒ 偏向**误报缺失**，**不会产生假通过**（保守方向）；
3. **`relay-trace` 是否把截断值用作判据，仍属 UNKNOWN**（`compile-diagnostician` 已追踪加载点与消费点，未穷尽全部检查路径）⇒ **我按 UNKNOWN 登记，不声称已排除**。
## 9. 窄口径字节级复核（Captain ② 四类判据）—— 逐项结果
**对象**：43,806 B / `66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4` @21:09:24（566 行）
**窄口径判定：`pass`（1 条非阻断 finding，见 §9.5）**

### 9.1 内容键（去注释后可执行）
```
K48_ACM5_AMP_REF=1 ✓  K76_ACM_BST=1 ✓  K109_BUSL1_PB0=0 ✓  K110_ACM18_BST=0 ✓  K46=0 ✓
TM600 体内 SetOn 恰好 1 次 = L264（9 项）= [13,48,57,60,61,76,83,85,126] ✓
TM601 段 SetOn = L471；可执行 ACM200=0、SW12_U1REF_BST_ACM=0 ✓（L448/449 的 ACM200 提及为**注释**，非可执行）
```

### 9.2 不变量 / 文本
`delay_ms(1)`=6 ✓／`delay_ms(2)`=0 ✓／`SetClamp(50,50)`=2 ✓／`MeasureVI(200, 5, FPVIe_MV_X10)`=2 ✓／裸 `126` 在 SetOn 内 = 0 ✓／`K126_V1P5_CAP`=2 ✓／`ERROR_RES`=2 ✓／`K57_CAP_BST_SW`=2 ✓／`K5`+`K44`+`K45` 可执行 = 0/0/0 ✓；**BOM 存在 ✓、CRLF 566 ✓、孤立 LF 0 ✓**

### 9.3 注释合规
- `--check-extra` 那句为 **"NO --check-extra DISABLE is needed any more"**（＝不再需要禁用）✓（`L261`）
- 两段旧注释已标 `SUPERSEDED … retained as history, NOT the operative rule` **且保留而非删除** ✓（`L203` t29、`L230` t43；`SUPERSEDED` 共 2 处）
- 两案操作事实在位 ✓（`L240-245`：未激磁 `K48(NC)→K49` → `SW1_F/SW2_S`（或 `K49(ON)`→`SW2`）；激磁 `K48(ON)→K76(ON)` → BST）
- **`relays.md L31 口诀未被引用** ✓：`L238-239` 明写 "no mnemonic cited - knowledge/hardware/relays.md L31 is referenced 0 times here"；`L461-465` 引的是 `L3-31` 的**警示段**（且 `L462` 只以省略号示意口诀，未逐字引）

### 9.4 口径一致性
**ch5／移除 `K109/K110`／闭集 `[48,60,61,76]`** 与 `t43` 终局一致 ✓；契约现盘 = **rev 38**（`closedRelayNumbers=[48,60,61,76]`、`channelsInScope.BST` 已是 ch5 口径）⇒ **同向、无冲突** ✓

### 9.5 ⚠️ finding（非阻断，medium）：TM601 段落内仍有一处**未标 superseded 的旧落点论断**
- **file**：`team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp`
- **line**：**L448-453**（关键句 `L449`、`L453`）
- **problem**：该段写 *"the ACM200 bootstrap source **is only steered to BST when K110 is closed** … it was a DANGLING drive … **but, with K110 un-actuated, it landed on PB0** and never reached BST"*。**落在 `PB0` 只在 ch18 腿成立**；按在案 ch5 判定，**TM600/TM601 所驱动的 ch5 源未激磁时经 `K48(NC)→K49` 落 `SW1_F/SW2_F`，与 `PB0` 无关**。同一文件 `L230`/`L203` 已把同类旧论断标为 `SUPERSEDED`，**此段未标** ⇒ 与同文件既有的取代标注**不一致**（且本 payload 别处已按 ch5 更正）。
- **影响**：**不影响可执行语义与窄口径 pass**（纯注释）；但它是**唯一未标取代的 ch5/ch18 敏感论断**，会与 `L230` 之后的 ch5 口径并列出现，后续读者可能据其误判落点归属。**TM601 的处置结论（移除正确）不依赖落点归属** —— 该结论由"TM601 无 BST 授权 + `K48/K76/109/110` 四者皆不闭"双向成立，与本 finding 无关。
- **requiredFix**：把 `L448-453` 按同文件既有格式加一行前缀标注，例如
  `// [SUPERSEDED BY t50/t53 - ch18-leg landing point; retained as history, NOT the operative rule]`，
  并（可选）在其后补一句 ch5 口径的落点：`un-actuated -> K48(NC)->K49 -> SW1_F/SW2_F`。**不要求删除原文**（保留留痕符合本 run 惯例）。


