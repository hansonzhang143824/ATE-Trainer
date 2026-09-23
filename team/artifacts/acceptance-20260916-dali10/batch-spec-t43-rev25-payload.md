# 定案批规格（等 `t43` 结案即执行）：契约 rev 25 + payload 同批落盘

> Captain 侧执行规格。**状态：待 `t43` 结案**（`t43` = rule-reviewer 对 ch5 判定的独立复核 + `K109/K110` 去留裁定）。
> **判据基础（六条独立证据同向）**：宏表 `Pin_Channel_define.h:20 = "S5_5,…"`（ch5）vs `:33 = "S5_18,…"`（ch18，另一台仪器 `PB0_BST_ACM`）；部署代码 `test.cpp:6997` 注释 + `L7000/L7085/L7087/L7170/L7513` 五处 `SetOn` 对本案仪器闭 `K60,K61,K48,K76`；`SCH-Connect-Map.txt:672-674`（ACM200 列组头 `需闭合: K48,K76`，源自 `S5_ACM200_FH5`）vs `SCH:42/L268`（含 `K109,K110` 的行起点均为 `S1_FPVIe_FL*`）；复合宏 `K_BST_ACM=48,76` / `K_SW_ACM=61` / `K_FPVIL_TO_BST_B=109,110` / `K_FPVIL_TO_SW_A=60,61`；控制组 5/5（宏通道 = 别名号 = 网表脚后缀）；契约 owner 已撤回其 `bst2sw` 映射为"取错通道"的自身错误。

---

## 零、`t43` 结案结论（本规格的裁定依据，20:9x）

- **`t43`（rule-reviewer）判定：ch5/ch18 归属 = UNKNOWN（可约束）**。它**接受并加强**第 1 步（`_GROUP_CHANNEL_DEFINE_ACM_GRP_`，`Pin_Channel_define.h:57`，192 token，第二 token 集恰为 `{0..23}` ⇒ `_n` 是**通道索引**）；**不背书**第 2 步（"故需 `[48,76]`"），理由：**(i)** 契约 `relayChain` 逐字写 `ACM200 S5_FH18 -> BST`，其**本意**无独立正面证据（作者虽自认取错通道）；**(ii)** 网表三条通道各走各的继电器（`FH5→K48→K76→BST`、`FH8→K60/K61→SW`、`FH18→K109/K110`）。
- **Captain 裁定的处置（做"两读法交集"、把分歧项推迟，不折中）**：
  1. **立即执行（两读法都安全）**：TM600 `SetOn` **追加 `K48_ACM5_AMP_REF` + `K76_ACM_BST`**（ch5 下必需；ch18 下只是并入既有并联支路——`K76.S1.5`/`K110.S1.5` 同 `BST_F_S1`、`K76.S1.4`/`K110.S1.4` 同 `BST_S_S1`）。
  2. **推迟（分歧处）**：**本轮 `K109/K110` 保留不删**（删除在 ch18 下不安全）——**其代价必须登记**：会把 **`FPVIe1_FL/SL_BUS` 耦合到 BST 节点**、并接上**未被驱动的 ch18 引脚**；**该项列为"须在电性签核前由 owner/机台裁定"的残余限制**。
  3. **`--check-extra`（"不得多闭"）在本修订不得启用**（并集多闭副作用）——写入 payload 注释与 `t34` 限制清单。
  4. **`t29` 定性更正**：改为"**`t42` 成立时属缺件／契约字面成立时属合规**"；**`t29` 的 `pass` 仍有效**（与 ch5/ch18 之争正交）。
  5. **收窄表述**：本案仪器是**"一个源、两端路径"** —— **源从 ch5（`S5_5`）进入 ⇒ `K48→K76→BST`**；**SW 端经 ch8 的 `K61_ACM8_SW` 引出**（部署代码对同一仪器同闭 `K48,K76` 与 `K60,K61`）。⇒ **不得表述为"整台仪器只占一个通道"**。
- **`K109/K110` 去留 = 另立一次裁定**（待 ch5/ch18 归属由 owner/机台结清）。⇒ **本批不做删除**。

---

## 一、权威口径（本批的事实与集合）

| 项 | 值 |
|---|---|
| 仪器 | `SW12_U1REF_BST_ACM` = **ACM200 channel 5**（跨域复合：BST 侧取 ACM200 族、SW 侧取 FPVIe[L] 族） |
| BST 侧闭集 | **`[48, 76]`**（`K48_ACM5_AMP_REF` + `K76_ACM_BST`） |
| SW 侧闭集 | **`[60, 61]`**（`K60_BUSL0_VCP` + `K61_ACM8_SW`） |
| 该对并集 | **`[48,60,61,76]`** |
| **`t30` 对 TM600 的期望（三源并集）** | **`{48,60,61,76,83}`**（`83` 来自 `pmid2sw`） |
| `K109/K110` 归属 | **FPVIe[L]（`K_FPVIL_TO_BST_B`）／`K110` 另属 ch18 的 `PB0_BST_ACM`** —— **非本仪器所需** |
| `PB0_BST_ACM`(ch18)+`[110]` | **不允许**改用（会**改变声明仪器**）；ch18 数据保留并单列供其自身用途 |
| TM600 | **必须**由 ACM200 驱动 BST（基线裁定 (ii) 声明该对，且 TM600 正是驱动它的函数）⇒ 闭 BST 侧 `[48,76]`、**移除 `K109/K110`** |
| TM601 | **无 BST 需求** ⇒ `t38` 的移除**成立**；**不得**为其补 `48/76` |
| TM1205 | 期望须取自 **`bst1_sw1`/`bst2_sw2` 变体行**（`[46,41]` / `[46,49,41,43]`），**非 `bst2sw`** |
| 门禁 | `bst-sw` 现红因"缺 `110`"是**按错误字段**；修正后红因"缺 `48/76`"；**本批后期望 GREEN**（脚本无该腿硬编码 K 号 ⇒ 随契约自动更新，**不派脚本任务**） |

---

## 二、契约 rev 25 改动清单（`setup-architect` 执行；`rev 24 / fd00a508…` → rev 25）

**A. 五处实测存在的错项/增项**
1. `resources[2].channelsInScope.BST = "S5_ACM200_FH18/SH18 (K110_BST)"` → 改为 **ch5 口径**（`S5_ACM200_FH5/SH5`；`K110_BST` 归 **ch18 `PB0_BST_ACM`**）。
2. `aliasResolution[3].resolution.relayChain[0].relay = "K110_ACM18_BST"`（`state` 串仍写 `SetOn (ACM200 S5_FH18 -> BST)`）→ 改为 **`K48_AMP_REF` + `K76_ACM_BST`**，`state` 串改为 ch5 表述。
3. `aliasFlatTable[3].relayPath = "K110_ACM18_BST -> K61_ACM8_SW"`（`kNumbers=[110,61]`）→ 同理更正（BST 侧 `[48,76]`；SW 侧 `[60,61]`）。
4. `aliasResolution[3].alternatives[0]`（原文 `…ACM200 FH18 -> BST via K110_BST, ACM200 FH8 -> SW via K61_SW`）—— **保留为唯一 `[110,61]` 正确处**，但须**加 `PB0_BST_ACm`/ch18 标注消歧**。
5. `legacyKMap.mapping[2]` 现只记**两条腿** → **补第三条腿：ACM200 ch5 = `[48,76]`**（原有：FPVIe0 CH0 high `K46,K48,K76`／FPVIe1 CH1 low `K109,K110`）。
6. **`bst2sw` 的 `relayChainHigh`/`relayChainLow` 均为 `null`（无推导）** → **补齐推导**或**显式标注"无推导（源自裁定文字）"**。

**B. 路线语义分列**
7. `closedRelayNumbersByRoute` **分两侧**：BST 侧 `[48,76]`（∈ ACM200）／SW 侧 `[60,61]`（∈ FPVIe[L]）。
8. **ACM200 行按通道分列**：`acm5 → [48,76]`、`acm18(PB0_BST) → [110]`（或至少在 `detail` 写明通道索引）。

**C. 三条登记待办**
9. `tmDeltas.TM600.aliasesUsed += "bst2sw"`（现仅 `["pmid2sw"]`；与其 DFT 含 `vset[bst2sw,5]` 及 `bst2sw.usedByTm` 列 TM600 不一致）。
10. **TM1205 移出 `bst2sw.usedByTm`**，为其建独立条目并绑 **`bst1_sw1`/`bst2_sw2` 变体行**。
11. **补齐 `tmDeltas.TM1205.aliasesUsed`**（现为空）。

**D. TM601 显式登记**
12. **"TM601 无 BST 节点/路线、不采用 ACM200 BST 驱动"**（保留 `sw2pgnd` 口径），防止后人再引入悬空驱动。

**E. 其他已确认项**
13. `terminalAssignment` 标 `legacy:true`（**不删原文**）+ `acmDriveFraming`。
14. `unrealisableRoutes`（`CH0 High -> BST [46,48,76]`、`CH1 -> BST [109,110]`）。
15. **结构化"别名→TM 归属"字段**（替代从 `usedByTm` 散文正则抽 TM 号；现为静默脆弱点）。
16. `relays.md` L21-27 与 L29/L31 状态指向**互相矛盾** → 契约内**更正或加注**（操作结论不变：未动作→PB0 只对 ch18；ch5 未动作经 `K48(NC)→K49→SW1/SW2`）；术语统一 **`un-actuated/actuated`**；负列表规则写成"**不得加入 required-on、不得驱动其动作**"。

**契约执行要求**：**不删原文**（保留并标 superseded）；双次生成**逐字节一致**；`validate` exit 0；**广播"文件名 + 现算哈希 + 现算时刻"**（尺寸与哈希同一命令取得）。

---

## 三、payload 改动清单（`ate-implementer` 执行；同批）

- **TM600（`TM600_HS_RDSON`）**：
  - **加** `K48_ACM5_AMP_REF`、`K76_ACM_BST`（BST 侧）；SW 侧 `K60`/`K61` **已在**。
  - **移除** `K109_BUSL1_PB0`、`K110_ACM18_BST`（BST 半边跨族；且会把 `FPVIe1_FL/SL_BUS` 耦合到 BST）。
  - 目标 SetOn ≈ `K83,K60,K61,K48,K76,K13,K85,K57,K126`（顺序以实现者为准，**须与既有范式一致**）。
  - **`L416-420` 的机制表述改为只陈述操作事实**（**不引 `relays.md` L31 口诀**）：如"未激磁时源经 `K48(NC)→K49` 落 `SW1/SW2`；激磁后经 `K48→K76` 到 BST"。
- **TM601（`TM601_LS_RDSON`）**：**不动**（`t38` 的移除为终态；**不得**补 `48/76`）。
- **照 `TM643` 的正确范式**（闭该腿而**把 ACM 源保持 `RELAY_OFF`**）——若 TM600 需要同时避免同节点多源驱动，须按 **BST 节点汇聚不变式**处理（`t48` 判定）。
- **内容键（修订特有）**：`t29 PER-FUNCTION JUSTIFICATION` ×1（注释）＋ 去注释后可执行 `K109_BUSL1_PB0` **×0**、`K110_ACM18_BST` **×0**、`K48_ACM5_AMP_REF` **×1**、`K76_ACM_BST` **×1**；`ACM Sets` 定义＝"剥离后仍非空且含 `.Set` 的行数"；交叉校验＝未剥离 = 剥离后 + 注释提及。
- **不变量（可执行口径）**：`delay_ms(1)`=6、`delay_ms(2)`=0、`SetClamp(50,50)`=2、`MeasureVI(200,5,FPVIe_MV_X10)`=2、裸 `126`=0、`K126_V1P5_CAP`=2、`ERROR_RES`=2、`K5+K44+K45`=0、`K57_CAP_BST_SW`=2；`PMID_HG2` 10 V 台阶 = `FXVIe_PLUS_20V`；BOM+CRLF、0 lone LF。
- **三门禁（沙箱副本）**：`relay-trace`（期望 `FR-001` 反向 2、仅 TM643 两条 WARN）、`bst-sw`（期望 **PASSED**）、`awg`；**新增红 0**。
- **产出**：新 payload + 证据文档；**须经 rule-reviewer 独立复核**（作者不自审）；**落盘由 Captain 执行**。

---

## 四、计划 v22（`test-strategy-architect` 执行；与 rev 25 同批）

- `items[TM600].assumptions` 等处 **`[110,61]` → `[48,60,61,76]`**，并**分两侧标注**：BST `[48,76]` ∈ ACM200／SW `[60,61]` ∈ FPVIe[L]。
- **不删原文**；增 `revisionHistory` v22 条目并写明理由（跨族 + `StdAfx.h` 四行 + 部署代码五处 + 契约该对无推导）；双次生成逐字节一致 + `validate` exit 0 + **广播新哈希**。
- 随后 `setup-architect` **刷新 `implementation-input-pin.json` 的 plan 行**（`status` 仍 `NOT FINAL`）。

---

## 五、落盘与验证（Captain 执行）

1. 以**备份 + 精确 REPLACE** 写入 `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`（写前备份、写后重读、逐字节/哈希验证；**失败自动回滚**）。
2. 落盘后**通报**新 `size/sha256/mtime` + `K109_BUSL1_PB0`/`K110_ACM18_BST`/`K48_ACM5_AMP_REF`/`K76_ACM_BST` 命中数。
3. **门禁快照**：落盘**前**（预期 `bst-sw` NEW-RED，缺 `48/76`）与落盘**后**（预期 **GREEN**、其余 11 门不变、`cbit` 仍基线豁免）各留一份 —— 即 `t30` 阳性对照的验收凭证。
4. **Release|Win32 编译由 Captain 在可写会话执行**（成员会话只读、`MSB3491`）⇒ 交回 `build.log` + **0 error / 0 warning 逐字输出** + `F12011.dll` 的 size/sha256/mtime，并标注"**证据来源＝可写会话（Captain）**"。
5. `compile-diagnostician` 据此把 `build-report.json` 由 `blocked` 转 `pass`（附 delta 归因 `bst-sw: NEW-RED → GREEN`，其余 11 门不变）并复跑 schema。
6. `setup-architect` 更新 `acceptance-report.json`（`verdict`/AC3/AC5 重评，**不新增文件**）。

---

## 六、边界与禁止项

- **`D:/PROJECT6-DALI/devel` 零写入**；目标树**只允许** `ForCodexDebug`。
- **不得**以"编译通过/门禁绿"替代电性结论；**本轮未做任何机台/电性验证** ⇒ 终稿必录 `electricalDisclaimer` 与相关 limitations。
- **不得**在 `t43` 结案前落盘；**不得**为 TM601 补 BST 侧闭合；**不得**删除 `K110` 的能力/数据（其属 ch18 自身用途）。
- 引用一律：**内容键 + 现算 python 明文哈希 + mtime**；manifest 按 **role/revision**；**冻结声明只写文件名 + 现算哈希 + 现算时刻**。

---

*本规格为 Captain 侧执行文件；随 `t43` 结案更新一次（记录结案结论），结案后即冻结。*
