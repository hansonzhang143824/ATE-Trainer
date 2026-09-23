# t6 审查清单（按用户最终裁定 · 只核对“是否符合裁定”，不重开裁定）

日期：2026-09-16 · run: acceptance-20260916-dali10 · 审查人: rule-reviewer
状态：t5 仍为 `pending`（未 claim），t6 被 t5 阻塞，**尚未开始审查**。本文件是预备清单 + 已实测基线。

适用范围（唯一）：仅本 run 的 **debug 代码生成与编译**；**不授权真实上机**；不改生产树。

---

## A. 五项已裁定项（`closed-by-user-adjudication`）—— 判分口径

**不得**列为 unresolved blocker；只核对“实现是否符合裁定”，不判裁定本身是否合理。若实现与裁定不符 → finding（针对实现），不是重开裁定。

| 编号 | 裁定（判分依据） | 核对点 |
|---|---|---|
| BD-01 | TM600 **11 mΩ** / TM601 **7.5 mΩ**（OVERVIEW） | 被改/新增函数的限值与判据是否用 11 / 7.5；`DFT.csv` 10/8 mohm **并列保留**且带 locator，无改写/平均/删除 |
| BD-04 | TM108/TM109 阈值 **4.4 V**（OVERVIEW） | 是否用 4.4 V；`DFT.csv` 4.15 V 与 TM109 行 vac3/DMUX 矛盾**并列保留**为冲突 |
| BD-05 | 黄金 **`SetClamp(50,50)`**（1 V ⇒ ±0.5 V）；**每次 FV/FI 切换后重发**；**1 A 脉冲 ≤2 ms**；标 **provisional / bench-signoff-required**；**非 pass/fail 判据** | 三项逐条核对；clamp 重发**严于黄金**（黄金只设一次）→ **不得判为偏离**；须标 provisional |
| BD-06 | TM1205 仅结构闭环，无数值判据 | 记入 limitations，不得凭空造数值判据 |
| BD-07 | TM600 `Y / 2 FLOAT` 按“两浮动节点”实现 | 是否按两浮动节点实现；标注为**可重开假设** |

## B. 逐条审查清单（用户指定，9 项）

1. **限值**：每个被改/新增函数用 11 / 7.5 mΩ，且**并列保留** `DFT.csv` 侧数值与 locator（无改写/平均/删除）。
2. **1 A 脉冲 ≤2 ms 且测量后立即关断**（对照黄金 `delay_us(2000)` → `Set(FI,0)`）。长时间保持 1 A = **finding**。
3. **clamp 在每次 FV/FI 切换后重设**。本项**严于黄金**（黄金只设一次），**不得判为偏离**。
4. **首次使用项须标“有意偏离 + 论证”**：
   - `FPVIe_MV_X10`：需 10 mV 级 + 1 V 量程论证，且须说明**为何不用** `FPVIe_100MV`（clamp 下先饱和）。
   - FPVIe `MVRET` 读取：标“黄金支持、项目首次”，引 `tm600-normal-highcurrent.cpp:91`。
5. **最小首次使用面**：`FPVIe_RELAY_SENSE_ON` / `CONTACTMODE` / `HIGH_MV` / `LOW_MV` **本 run 不应出现**；出现即判**超出裁定范围**，要求移除并改列 U9 bench 项。
6. **禁用 `rampi_capv`/`rampv_capv` —— 已按 F1 更正为「只判新增量」**（Captain 2026-09-16 确认其原指令有误）：
   - **判据**：t5 **未在 TM600/TM601 及其新增代码**中引入 `rampi_capv`/`rampv_capv` → **PASS**。
   - 既有 **82 处**（`rampv_capv` 78 + `rampi_capv` 4，见 §C.2）为**基线既有状态**，**不得**计为 t5 新增门禁红，**不得**据此判 FAIL。
   - 机制原因（Captain 提供）：`scripts/verify_bst_sw_sequence.py:78-114` 按「函数体内含 `rampi_capv(`」**行为自证**收目标 → 新增函数一旦含该串即被硬编码判红。
   - 同源纪律：`scripts/verify_awg_params.py` E005 对 `_Rise/_Fall/_Hys` 的**既有 pre-existing 红**（TM425/607/608/609）同属基线，**不得**算作新增红。
   - 取证口径：判「新增」须用 python 明文 diff（基线行号见 §C.2）与 t5 改动集比较，**不得**数全树 token。
7. **格式与符号**：全局对象 `FPVI0.Set(...)`（**`FPVIe` 是类名，不得用点号**）；枚举 `FPVIe_RELAY_ON`（小写 e）。
8. **取证纪律**：只用 grep 工具/python；禁用 pwsh 读取源码做存在性/缺失断言；哈希一律 python 明文并标 `plaintext`；**引用任何交付物前现算哈希**。
9. **limitations 必含**：U1/U2/U3–U8/U9/BD-06/BD-07，以及边界句“编译与门禁通过不等于电性/硬件正确”。

边界：我**只出 findings、不改实现**；`reviewedArtifact` 记录被审实现哈希；评审前后用 python 哈希自证未改动被评产物。

---

## C. 已实测基线（python 明文取证）

### C.1 源码锚点（2026-09-16）

| 文件 | size | sha256 (plaintext) |
|---|---|---|
| `ForCodexDebug/source/test.cpp` | 434629 | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` |
| `ForCodexDebug/source/sub.cpp` | 121909 | `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470` |
| `ForCodexDebug/source/StdAfx.h` | 56968 | `ba8ab3de1b0c35cb7e9a477bd0b385f80671dc51011a08c9a5220518aab6aee6` |

### C.2 ⚠️ 清单第 6 项必须按“新增量”判，不能按“全树 0 命中”判

实测（python 明文，`ForCodexDebug/source/test.cpp`）：

- `rampv_capv` — **78 个调用点**（首 1955，末 8843）
- `rampi_capv` — **4 个调用点**（7034 / 7124 / 7210 / 7552）

⇒ 两项**在既有基线代码中已大量存在**，其中 `rampi_capv` 4 处**全部**落在 TM607/608/609 区段（6956–7552）。
⇒ **正确判分口径**：核对 t5 **是否在 TM600/TM601 及其新增代码中引入 `rampi_capv`/`rampv_capv`**；若 t5 未引入，则清单第 6 项 **PASS**。既有代码的既有用法属**基线既有状态**，不得算作 t5 新增门禁红。
⇒ 反面警示：若按“全树不得出现该 token”判分，会因既有 78+4 处而**误判 FAIL**。

### C.3 清单第 4/5 项基线状态（t5 前）

`test.cpp` 中实测出现次数（python 明文）：`SetClamp`=0、`FPVIe_MV_X10`=0、`FPVIe_100MV`=0、`FPVIe_RELAY_SENSE_ON`=0、`CONTACTMODE`=0、`HIGH_MV`=0、`LOW_MV`=0、`7.5`=0、`MVRET`=36。
⇒ 若 t5 后这些由 0 变为 >0，即为**新增首次使用**，逐条按第 4/5 项判定（`MVRET` 需按“黄金支持、项目首次”论证）。

### C.4 现有 TM 定义位置（t5 前）

`TM108_HSKP_VAC1_PRST`@2155、`TM109_HSKP_VAC2_PRST`@2233、`TM1205_TRX_BST_UV_GD`@8766。
**TM600 / TM601 在 `test.cpp` 中无定义** → 与“真实新增能力”一致；t5 落地后需核对新增定义位置与实现。

### C.5 隔离基线（可直接用于 t9）

python 逐文件哈希：`ForCodexDebug/source` 与 `devel/source` 各 111 文件，**全部源码/头文件逐字节相同**；唯一差异为 `source/Release/` 编译产物（obj/lib/pdb/exp/tlog）。
⇒ Release 产物差异**不得**作为“源码被污染”证据（假阳性）。

---

## D. ⚠️ 交付物哈希陈旧（“引用哈希前现算”已生效）

Captain 报的哈希与我此刻现算的**不一致**（本 run 已 4 次出现引用哈希失效）：

| 交付物 | 报告中 size / sha256 | 我现算 size / sha256 | 判定 |
|---|---|---|---|
| `dft-ir.json` | 88101 B / `478f88a4…`（t1 报） | **116140 B** / `82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568` | **已失效** |
| `schematic-ir.json` | 450689 B / `ffc82b0b…`（t2 报） | **455650 B** / `ffc82b0b0692963e2c6bbbb45edd49bb29c890ca1fd5116a2736e78d65238aec` | **size 与报值不符**（哈希符） |
| `setup-contract.json` | 190534 B / `9402a3c0…`（t3 报） | **216717 B** / `9402a3c0c33f740ca4951309b6ec21f4b57fc5d0178a11163b22b9ab11edbc05` | **size 与报值不符**（哈希符） |
| `test-plan.json` | 98641 B / `19e6f2c3…`（t4 报） | **98641 B** / `19e6f2c389db69a7c944a41883dc9af7b2b1083bfc495c2b4d0ed901b8e13cfe` | **一致（有效）** |
| `isolation-baseline.json` | — | 44144 B / `6268e0df03290d6d40468942a28b0a13b1caf9433d705e6d946085bcf30d2e83` | 现算值 |

事实：这些文件的关键写入时间为 **09-16 14:11–14:12**（`dft-raw/scripts/dft_ir_patch_captain4_rulings.py` 亦在 14:11:41 写入），即**在 t1/t2/t3 报告之后又被重新生成**。
⇒ 我**不**声称这是缺陷（可能是合法的裁定补丁重生成）；我声称的是：**报告中引用的 size/hash 对 3 个交付物已陈旧**，t6 的 `reviewedArtifact` 与 t9 的证据包必须**以现算值**为准，不得沿用报告值。
⇒ **给 t5/t8/t9 的可执行要求**：任何 finding / 报告里引用 dft-ir.json、schematic-ir.json、setup-contract.json 时，附**该引用时刻 python 明文的 size+sha256**。

## E. 待 t5 落地后执行的取证（预备命令形态）

- 新增代码定位：python 明文 diff `test.cpp` 与 `devel` 基线哈希 → 得改动集。
- 逐项核对 A/B 清单，evidence 字段写 **工具 + 文件 + 行号**（grep 工具或 python）。
- 全程只读；结束前后各算一次被评产物 python 明文 sha256 自证未改动。

---

## F. F1–F5 回执后的增补（2026-09-16，Captain 确认）

### F.1 新增审查项：**是否把只读知识树文件复制进 debug 树**
黄金 `tm600-normal-highcurrent.cpp` 位于**只读知识树** `knowledge/references/L4-Golden-code/`，**不在** `D:\PROJECT6-DALI` 下。
⇒ **审查项**：t5 **不得**把该文件（或其它 `knowledge/references/**` 文件）复制进 `ForCodexDebug` 当作"新增产物"；出现即 finding。判定用 python：新增文件中若与黄金逐字节相同 → 命中该 finding。

### F.2 黄金引用实测更正
实测 `knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp` = **6106 B**（Captain 回信写 6109 B）、139 行、CRLF=0、NUL=0、sha256 `8cdb0be1dd8381008a6a6ca84743170d6e1cf6f5c84f21a1e2e947a0187b72ce`。
**哈希与 Captain 一致，size 差 3 B（3 位数字转写误差）**；并行检出 `ATE-Coding-Platform\...` 的同名文件**逐字节相同**（同一哈希）。

### F.3 哈希再次漂移（第 5/6 次）——以现算为准
Captain 报 `schematic-ir.json` 450689 B/`ed77ccae…`；我上轮现算 455650 B/`ffc82b0b…`；**本轮现算又变**。全部以**引用时刻现算值**为准：

| 交付物（2026-09-16 t10 修订后现算） | size | sha256 (plaintext) |
|---|---|---|
| `test-plan.json`（**t10 修订版**） | 113773 | `7f1bdf976c721596b00203c38eef29d559701a7bbdaa06a2d045855265a86463` |
| `test-plan.v1.json`（t4 原版留档） | 98641 | （内容即我上轮实测算得的 `19e6f2c3…` 版） |
| `dft-ir.json` | 130724 | `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b` |
| `schematic-ir.json` | 455882 | `6d61cf78575ddfafab417c3e065f8404ecc26873775bbd4b5b357f22beaec671` |
| `setup-contract.json` | 229695 | `ab07d6f9f67ec24696187367dd7671ab317dc39777cd61fccfb16abd6195eee2` |
| `isolation-baseline.json` | 44144 | `6268e0df03290d6d40468942a28b0a13b1caf9433d705e6d946085bcf30d2e83` |

### F.4 t10 修订版实测状态（**t6 的审查基准**，`generatedAt 2026-09-16T14:15:48+08:00`）

**已落地（PASS 项）**
- `limitations` 由 7 条 → **14 条**，已补齐 **U3 / U4 / U5 / U6 / U8 / U9**（含 U7 占位）与边界句（"Build/compile success is not electrical validation…"）。
- 资源仲裁前提已写入 items[7].assumptions（两浮动通道 vs 归档黄金单浮动通道，以合约为准）。
- 计划仍自标为 t4 attempt 1，**未标注 t10 修订轮次**。

**未落地（需 t10 补齐，否则按缺失判 finding）**
- **BD-04 / BD-05 / BD-06 / BD-08 状态仍为 OPEN**（`blockingDecisions` 实测：BD-04 `OPEN`/high/null；BD-05 `OPEN (mechanism fixed, value provisional)`；BD-06 `OPEN (accepted as structural closure)`；BD-08 `OPEN (needs adjudication)`/high/null）。
  ⇒ Captain 已裁定关闭这四项，但**文档未改**；items[4]/[5] 的 `unresolved` 仍写 "BD-04 … open"。
- **`limitations` 无 BD-07 条目**：实测 limitations 14 条内**无任何** BD-07 行（BD-07 仅在 `blockingDecisions[6]` 标 `ASSUMPTION (recorded)`）。按清单第 9 项 → **missing**。
- **`bench-signoff` = 0 次**、**`simulationDomainReference` = 0 次**（BD-05 需标 `provisional / bench-signoff-required`；BD-08 裁定要求 `.sv` 仿真值改记 `simulationDomainReference` 保留）。
- `U7` 为"未提出、占位"条目；`U9` 已列为 limitation（与清单第 5 项"U9 bench 项"衔接）。

**判分口径**：t6 以 **t10 之后**的 `test-plan.json` 为准；上述未落地项若在 t5/t10 收尾后仍缺失 → 按缺失判 finding（不重开裁定本身）。
**⚠️ 本段已过期 —— 现行基准是 v19，见 §H**；F2/F5 已结案。

---

## H. 计划 v19 = 现行审查基准（复核对象哈希，2026-09-16）

### H.1 基准锁定（python 现算，复述前必重算）

> **⚠️ 本节已被 §I 更正（2026-09-16 19:0x）。** 以下 164399 B / `d2aef4ad…` 的版本**不在盘上任何文件**（无 `test-plan.v19.json`，实测 ABSENT）⇒ **不得再作为复核基准引用**。**现行复核基准见 §I：现盘 `test-plan.json` = 166099 B / `fabdd24f…`（v20）。** 本条保留作为错误与更正记录。

`team/artifacts/acceptance-20260916-dali10/test-plan.json`
- ~~size 164399 B · python-plaintext sha256 `d2aef4ad5f3e48f939256220bbcf4baa4a0693cfd1770d31c8868f9eb41719bb` · mtime 18:14:22~~（**已作废：盘上无此字节**）
- 我当时的哈希读数正确（t17 交接公告值 `d2aef4ad…`），但**该版在两个快照之间被覆盖**，且我未保留副本 ⇒ 现在无法在任何盘上文件中复现该哈希。
- 全链快照（现盘）：`v1..v10, v12..v18, v20`；**缺 `v11`、缺 `v19`**（我已实测确认 ABSENT）。
- 注：`limitations` 实测 **19 条**（architect 公告 v6/v7 时为 17 条，是版本差非分歧）。

### H.2 F2/F5 结案与**记录内不一致**的裁定（我接受并据实更正）
architect 用**盘上历史副本**实测 settle，我独立复核后确认：

| 版本 | size | sha256 | limitations | 已标号项（occ） |
|---|---|---|---|---|
| v1 | 98641 | `19e6f2c3…` | **7** | 仅 `U1`（U1=6,U2=5,U3=1,U4=0,U5=1,U6=0,U7=0,U8=0,U9=0） |
| **v2** | **113773** | `7f1bdf97…` | **14** | `U1,U3–U9`（U3=2,U4=1,U5=2,U6=1,U7=1,U8=1,U9=4） |

⇒ **我的 F2 记录里 size（113773 = v2）与 content 形状（7 条 / U4=U6=U7=U8=U9=0 = v1）来自两次不同测量，被并列写进同一条 finding** —— architect 的指认**成立**，我接受该裁定及其定性（记为"记录内两个数字不一致"，不记为陈旧读取）。
⇒ 成因已查清：我 F5 的**独立测量**（同一时刻）实测 **limitations=14 且 U3–U9 在位**，与 v2 吻合；F2 中引的 7 条来自**更早的 t10 前测量**。**实质结论未被污染**（F2 的要点 —— `blockingDecisions` 标 OPEN —— 对 v1/v2 均成立），但**引用纪律违规**：不同时刻的读数不得混入同一条 finding。
⇒ **追加纪律**：每条 finding 只能使用**同一时刻、同一哈希**的一组读数；跨时刻数据必须分列并各标哈希+mtime。

### H.3 v19 逐项复核（我实测，python 明文）
- **BD 状态全部就位**：BD-01 `closed-by-user-adjudication`｜BD-04 `closed-for-this-run`｜BD-05 `closed-by-user-adjudication`｜BD-06 `closed-by-user-adjudication (structural closure only)`｜BD-07 `ASSUMPTION (recorded)`｜BD-08 `closed-by-captain-ruling (reversible by the user)`｜DV-01 `ruled`。
- **namingPolicy（§G.4 的 low finding）已改**：明确"contains no C++ syntax and prescribes no new API"并列出**三类既有标识符** ⇒ **finding 关闭**。
- **BD-01 判据**：TM600 `11 mOhm` + `registeredConflict{10, DFT.csv}`；TM601 `7.5 mOhm` + `registeredConflict{8}` ⇒ **并列保留成立**。
- **BD-04 判据**：TM108/TM109 主值 `4.4 V`，TM109 明列 `VAC2_PRST rising (registered conflict) 4.15 V` ⇒ **并列保留成立**。
- **清单 B 第 4 项**：`measurement.gainFirstUse` 在位，标 `FIRST USE - intentional deviation from precedent`，含 1 V 量程 / 10 mV 级论证。
- **清单 B 第 6 项**：v19 内 `rampi_capv`=0、`rampv_capv`=0 ⇒ 计划侧无新增（**实现侧仍须逐函数核对**）。
- **清单 B 第 5 项**：`FPVIe_RELAY_SENSE_ON`/`CONTACTMODE`/`HIGH_MV`/`LOW_MV` v19 内均 **0 次** ⇒ 计划未越界。

### H.4 ✅ 我**撤销**一条自拟的 TM601 疑似 pre-finding（自查后排除）
v7→v19 结构 diff 中**唯一两项删除**是 `items/TM600|TM601/measurement/samples/note`（含"必须落在 2 ms 脉冲上限内"字样）。我一度怀疑 TM601 因此丢失"测量后立即关断"约束，遂逐条读 v19 序列 —— **不成立，撤销**：
- v19 新增 `measurement.pulseCap`（TM600、TM601 **均有**）：`value 2 ms`、`metric` = settle+acquisition 全程、`rule` = *"HARD CAP on the 1 A pulse: apply the force, complete the capture inside 2 ms, **then remove the current immediately**"*，并附黄金 `precedent` 路径 ⇒ **约束未丢，改为更强的结构化字段**。
- 序列内 TM600 `[8] Immediately remove the forced current (1 A pulse must be short).`、TM601 `[8] Remove the forced current immediately.` **均在位**（各 11 步、2 处含关断）。
- 结论：两处 note 删除属**去冗余**，**非约束丢失**，不构成 finding。

### H.5 v7→v19 结构 diff（我自算，落盘）
`review/test-plan-diff-v7-v19.md`（我生成；覆盖 items 的 limits/unresolved/calculation/parameters/datalog/measurement/cleanup/methodFamily/exceptionalRequirements/assumptions/implementationEvidence/sequence + limitations + BD 状态）：
**added=28，removed=2，changed=49** ⇒ **无需 architect 另出 diff 表**，其 `revisionHistory` 可与我的口径对账。

---

## G. test-strategy-architect 工具层通报的独立复核（2026-09-16，全部实测）

### G.1 ✅ 受保护范围**包含 artifacts 本身**（比 Captain 首轮广播更广）——我实测确认
同一文件两种读者：

| 文件 | python 明文视图 | pwsh `[System.IO.File]::ReadAllBytes` |
|---|---|---|
| `artifacts/.../test-plan.json` | 136263 B, **NULs=0**, first16 `7b 0a 20 20 22 72 75 6e …`（`{\n  "run`） | 136263 B, **NULs=648**, first16 `54 53 5a 23 05 17 07 0e b0 00 …`（`TSZ#`） |
| `project/DALI/input/DFT.csv` | 16862 B, **NULs=0**, sha256 `b92d203fa6f15212…` | 16862 B, **NULs=278**, first8 `54 53 5a 23 05 35 07 0e` |
| `Get-FileHash DFT.csv` | — | `c87e601534d5d4ca…`（≠ python 明文 `b92d203f…`） |
| `Get-FileHash test-plan.json` | — | `c3465ddf1bb38aa7…`（≠ python 明文 `e1dd24de…`） |

⇒ 与 architect 的 fixture **逐字节吻合**（`c87e6015…` / `b92d203f…`）。
⇒ **新增纪律（零成本预筛）**：python 读首 4KB，**NULs=0 ⇒ 该文件有明文视图**；NULs>0 者（如 `.pyc`）属二进制、需另行判断。
⇒ 全 artifacts 扫描（python，首 4KB）：**唯一**含 NUL 的是 `dft-raw/scripts/__pycache__/dft_ir_items_part1.cpython-312.pyc` → **我们的文本产物均未受保护**；其 pwsh 视图（`TSZ#`）是**读取器过滤视图**所致，**不得**据此判“产物被加密/被改”。

### G.2 ✅✅ 关键澄清：**grep 工具是授权读取器**（architect 未言明，我实测确认）
对 `test-plan.json` 搜 `QVM`：**grep 工具 = 命中 4 处**（行 27 / 2322 / 2542 / 2543），与 python 明文 `QVM`×4 **完全一致**；同一文件 pwsh 读到密文。
⇒ **grep 工具与 python 同为授权读者、二者逐字互证**；受保护树上**只有 pwsh 的 .NET 路径未授权**。
⇒ 断言口径：grep 工具**可用于**内容断言（须写明工具+行号）；`pwsh Select-String/Get-Content/Get-FileHash/ReadAllBytes` **一律禁止**。

### G.3 ✅ 版本冲突已消解——**双方读数都真实，是同一文件的不同版本**
`test-plan.json` 快照序列（python 现算，实测）：

| 快照 | size | sha256(前16) | mtime |
|---|---|---|---|
| `test-plan.v1.json` | 98641 | `19e6f2c389db69a7` | 14:11:43 |
| **`test-plan.v2.json`** | **113773** | **`7f1bdf976c721596`** | **14:15:48** ← 我 F2 读的正是这一版 |
| `test-plan.v3.json` | 121694 | `2e93a46c54c79b90` | 14:20:55 |
| `test-plan.v4.json` | 128624 | `738998ca98414f32` | 14:25:51 |
| `test-plan.v5.json` | 131707 | `18cf4d7ff9844c4a` | 14:30:12 |
| **`test-plan.v6.json`** | **134802** | **`d84035516c04795c`** | **14:33:04** ← architect 读的这一版 |
| `test-plan.json`（现行，= v7） | **136263** | **`e1dd24defaed603b`** | **14:37:12** |

⇒ 我读的是**当时现算**的 v2（113773 B 与我 F2 报的 size 逐位吻合），architect 读的是 v6 ⇒ **双方均非陈旧读取**；F2 对 v2 的结论正确。
⇒ **v7 已修掉 F2/F5 各项**：BD-01 `closed-by-user-adjudication`；BD-04 `closed-for-this-run (user-confirmed…)`；BD-05 `closed-by-user-adjudication`；BD-06 `closed-by-user-adjudication (structural closure only)`；BD-07 `ASSUMPTION (recorded)`；BD-08 `closed-by-captain-ruling (reversible by the user)`；DV-01 `ruled`。
⇒ limitations **17 条**，含 `[13] U9`、`[14] U10`、`[15] BD-06`、`[16] BD-07`；边界句 "Build/compile success is not electrical validation" **逐字存在**（True）。**F2/F5 结案。**
⇒ **新纪律（防再度误判）**：本 run 计划文件以每几分钟一版推进 ⇒ 我的 finding 必须**逐条附“被检文件 python 现算 sha256 + mtime”**，复述前重算；版本号本身即审计线索。

### G.4 ⚠️ namingPolicy 自述与自含内容不符（low，需归档、不阻塞）
`namingPolicy` 声称 *"prescribes no test-function name … contains no test-function identifier"*。
实测 `items[*].symbol` **逐条含测试函数标识符**：`TM000_IQ_STANDBY`、`TM001_IIN_SUSPEND`、`TM102_HSKP_LP_ATEST0`、`TM103_HSKP_LP_HR_0P5U`、`TM108_HSKP_VAC1_PRST`、`TM109_HSKP_VAC2_PRST`、`Trim_BG_RES_DIV`、**`TM600_HS_RDSON`**、**`TM601_LS_RDSON`**、`TM1205_TRX_BST_UV_GD`（occ：`TM600_HS_RDSON`=1、`TM601_LS_RDSON`=1、`TM108_HSKP_VAC1_PRST`=2、`TM1205_TRX_BST_UV_GD`=4）。
- 术语上可自辩：symbol 是**被引用标识符**而非“规定的实现 API”；且 C++ 语法实测确为 0（`DUT_API`=0、`Set(FV`=0、`#include`=0、`;` 行尾=0）⇒ **“不含 C++ 片段”成立**。
- 但自述句 "contains no test-function identifier" **字面为假**，且 `TM600_HS_RDSON`/`TM601_LS_RDSON` 正是本 run **新增能力**之名 ⇒ 有被误读为“计划已固定实现名/API”的风险。
- **处置**：不阻塞；建议改写为 *"contains no C++ syntax and prescribes no new API; it quotes existing test-function identifiers in the `symbol` field for traceability only"*。t6 记 **low finding**（文档自述与内容不符），**不判为架构缺陷**。

### G.5 ✅ DFT.csv 实际位置（供 t6/t8/t9 引用）
`DFT.csv` **不在** `D:\PROJECT6-DALI` 下（该树无 DFT.csv）；实测位于
`D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\input\DFT.csv`（16862 B，python 明文 sha256 `b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4`）；另有 `DFT_restored.csv`（16824 B，`0e0c31106586eacc…`）。引用时写全路径 + 现算哈希。

---

## I. ⚠️ 复核基准更正：v19 不在盘上 ⇒ 现行为 **v20**（2026-09-16，test-strategy-architect 指出、我独立复核确认）

### I.1 更正（我方的可追溯性缺陷）
**§H.1 曾把复核基准锁在 `164399 B / d2aef4ad…`（"v19"）。该字节不在盘上任何文件中。**

**盘上快照实测**（glob 全工作区）：`test-plan.v1/v2/v3/v4/v5/v6/v7/v8/v9/v10/v12/v13/v14/v15/v16/v17/v18/v20.json`
⇒ **`test-plan.v11.json` 与 `test-plan.v19.json` 均 ABSENT（我实测确认）**。

**根因与我的责任**：我记录的哈希读数本身**是对的**（与 t17 交接公告的 `d2aef4ad…` 一致），但**我在两次快照之间读取、且未保留副本**；作者的习惯是"重建前存当前版"，故 v19 恰好落在 `v18`（18:09:28）与 `v20`（19:04:49）两次保存之间而**从未落盘**。
**定性**：这是我的**可追溯性缺陷**（引用了一个无法在盘上复现的哈希），**不是**读取错误，也不是作者的记录问题。**t9 若据此追溯，会指向盘上不存在的字节** —— 已按架构师要求更正。
**新增纪律（第 2 条）**：凡引用产物哈希，必须**同时确认该哈希对应某个盘上存在的文件**（可用 `glob` + 现算比对自证）；仅记录哈希不足以支撑可追溯性。

### I.2 现行为复核基准（我独立现算）
| 项 | 值 |
|---|---|
| `test-plan.json`（**现行基准**） | **166099 B / python-plaintext sha256 `fabdd24f220d3b3e1eaf2bc782bf896adceb38074a72bffa7ba0d2d181ec8ed4` / mtime 19:04:49** |
| `revision` 字段 | `v20 (t17 closure - BST-SW ruling (ii) + idempotent generatedAt)` |
| 快照副本 `test-plan.v20.json` | **166099 B / `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016`** |
| `generatedAt` | 现为 **revision 派生常量**（非墙钟），见下 |

**⚠️ 我此前在两处把 `1925250d…` 当作"现行 v20"** —— 实测该哈希属于**快照副本 `test-plan.v20.json`**，而**现盘 `test-plan.json` 是 `fabdd24f…`**（同 size，不同字节）。二者都是"v20 家族"，但**不是同一份字节**；引用时必须区分是"现盘"还是"快照副本"。**这是我第二次同类的"同 size 不同哈希"混淆**，已并入 I.1 的纪律。

### I.3 架构师的零成本复跑验证（我逐项复核，全部吻合）
```text
SW12_U1REF_BST_ACM                     = 3   (expected 3)  ✅
INTENDED BUT CURRENTLY UNREALISABLE    = 1   (expected 1)  ✅
ruling (ii)                            = 3   (expected 3)  ✅
lowercase 'intended-but-unrealisable'  = 0   (expected 0)  ✅
```
⇒ 其"按小写连字符形式检索会误得未落地"的告诫**成立**。

**幂等性（我独立复核）**：`test-plan-build.py` 中 `datetime.now` 命中数 = **0** ⇒ `generatedAt` 确为 revision 派生常量，两次生成可字节一致 ✅

### I.4 v19→v20 的实质变更对我 checklist 的影响（按架构师要求复查）
**变更 = BST−SW 仲裁改为裁定 (ii)**：基线＝**接地参考 `SW12_U1REF_BST_ACM`**，`closedRelayNumbers = [110, 61]`（`K110_ACM18_BST` / `K61_ACM8_SW`）；`FPVIe1-CH1 = INTENDED BUT CURRENTLY UNREALISABLE`（三条证据：ch1 无最小端点宏、四只属 ch1 感测浮动/PC 类同负列表 87–91 禁动类、live 无 TM 用 FPVIe1 驱动 BST）；黄金双独立源 `ALTERNATIVE-NOT-ADOPTED`。契约同侧：`/aliasResolution[3].resolution.closedRelayNumbers[0]=110`、`bstRuling_ii`、`/tmDeltas/TM600/relaySet` 含 **110**、`pinRouteTable.BST."CH1 Low".needsClosed=[110]`（另有 CH0 Low 路径 `[109,110,138,139,145,146]`）。

**⇒ 对我 checklist 条目的影响（重要）**：B 清单第 6 项（继电器/资源仲裁）应补充判据：**TM600 的 BST−SW 基线路径必须按裁定 (ii) 闭合 `[110, 61]`**（而不只是"不得用 ramp 家族"）。
**⚠️ 该判据暴露了一个真问题**（见 `review/t26-tp20-k110-finding.md`）：**现盘 `test.cpp` 的 TM600 段中 `K109`/`K110` 出现次数均为 0**（`K61_ACM8_SW` 已闭），即**裁定 (ii) 的 `[110]` 未落地**；现行 `bst-sw` 门禁**不读 relaySet/needsClosed/SetOn**（`K110`/`110`/`needsClosed`/`relaySet` 命中数均为 0），故**看不见这个缺口**。已在给 Captain 的报告中提请派任务核处。
