# t30 — 门禁补盲：`bst-sw` 增加"SetOn 集合 vs 契约声明闭合集合"断言

- run-id：`acceptance-20260916-dali10`
- 执行者：compile-diagnostician（attempt 1，`attempt_id 0b304fc6-0dea-42d4-b745-ca4581cc3d24`）
- inScope：`scripts/verify_bst_sw_sequence.py`、`team/artifacts/acceptance-20260916-dali10/gate-logs-t30`
- 改动文件：**仅 1 个脚本**；`gate_baseline.json` / 契约 / meta / payload / 目标树 / `devel` **零写入**
- 取证纪律：受保护源一律 **python 明文**读写与哈希；**未编译**；**编译成功 ≠ 电性正确**（本报告无任何电性结论）

---

## 1. 盲区（实测根因）

`verify_bst_sw_sequence.py` 原先**完全不读契约**：`setup-contract` / `aliasResolution` / `needsClosed` /
`relaySet` / `K109` / `K110` 命中数**均为 0** ⇒ 它只校验"BST-SW 台阶序列 + K57 电容"，
**不比对"契约要求闭合的继电器"** ⇒ 裁定 (ii) 的 `[110,61]` 只落地一半（K110 从未闭合）却**12 门全绿**。

实测（python 明文，**两态分开**；Captain 令按 `t44` 实测更正）：
> **口径更正（t44 实测 / Captain 令）："现闭集"必须双列** —— 此前"TM600 现 SetOn 含 `K109/K110`、无 `48/76`"
> 的说法**只对 payload 成立**。两态实测：
>
> | 态 | 对象 | TM600 SetOn 数字集合 | 判定 |
> | --- | --- | --- | --- |
> | **payload（DELIVERED）** | `implementation-payload-TM600-TM601.cpp:219` | `[13,57,60,61,83,85,109,110,126]` | **闭错腿（109/110）+ 漏闭（48/76）** |
> | **部署态（DEPLOYED＝本门禁实际输入）** | `ForCodexDebug/source/test.cpp:9081` | `[13,57,60,61,83,85,126]` | **仅漏闭**（两腿皆不闭；只闭 `K57_CAP_BST_SW` 自举电容继电器） |
>
> ⇒ 本门禁的阳性对照描述**一律以部署态为准**（下表即部署态读数）。
契约 `aliasResolution[bst2sw].resolution.closedRelayNumbers = [110, 61]`，其 `usedByTm` 含 `TM600`。

## 2. 判据选择（四轮只读实测；**这一步是本任务的主要内容**）

| 候选判据源 | 实测结果 | 结论 |
| --- | --- | --- |
| `pinRouteTable[*][*].needsClosed` 并集 | TM600 missing **23** / TM601 missing **18** | **弃用**：它是"通往每个 PIN 的**全部可能路线**"枚举（`pinRouteTable[BST]` 列 7 条，含 CH0 High=`[46,48,76]`、QTMUe=`[141,46,48,76]`…），并入判定会把**未被选中的路线**当必需 |
| `tmDeltas.<TM>.relaySet` 整体 | TM600 missing **29** / TM601 missing **20** | **弃用**：它是**资源预算池**，含只被它提及、无任何路由依据的 K 号（实测 `K17/K18/K20/K86/K130/K142` "仅 relaySet 提及"） |
| 门禁内部 `targets`（ZCD 家族）作用域 | **FAIL=0 / exit 0**（断言失效！） | **弃用**：门禁 targets 由 meta `powered_pins` 拓扑指纹派生 = `TM607/608/609/640`，**TM600 根本不在其中** ⇒ 这正是它看不见 K110 的原因 |
| 契约 `usedByTm` **全量**作用域 | 11 条红（TM108/109/TM1205 也被判红） | **过度归因**：TM108/109 的 `pgnd2sw` 属 **ramp 段**；TM1205 闭的是**自己的 path 别名**（`K_FPVIH_TO_SW1_A=46`/`K_FPVIL_TO_BST1_A=41`） |
| **`aliasResolution[a].closedRelayNumbers` + 显式作用范围** | TM600 missing **`[110]`** / TM601 missing **`[]`** | **采用** |

## 3. 实现（可复用判据，零硬编码）

期望集合（**全部从冻结契约读取，不硬编码任何 K 号**）：

```
期望 = ∪ aliasResolution[a].resolution.closedRelayNumbers
       a ∈ { 使 <TM> 以独立 token 出现在其 usedByTm 中的别名 }     ← 契约权威、无需 per-TM 登记
         ∪ { tmDeltas.<TM>.aliasesUsed 声明的别名 }
         ∪ { --tm-alias <TM>=<a>,... 外部声明 }                  ← 修补 aliasesUsed 漏登记（参数化）
比对 = 该函数块内**所有** cbite.SetOn(...) 的 K 号 / 裸数字（python 明文解析）
作用范围 = --tm-scope；默认 DEFAULT_TM_SCOPE = ["TM600_HS_RDSON","TM601_LS_RDSON"]（本 run 实现对象）
```

- **致命通道**：缺失项进 `errors[]` ⇒ `main()` 既有出口 `sys.exit(1)`（与原有 FAIL 同一出口）
  ⇒ `run_gates.ps1` 的 `exit!=0 ⇒ NEW-RED` **自动计入新增红**（**不是 warn**）。
- **`relaySet` / `pinRouteTable` 仅作 locator**：失败信息附 `pinRouteTable[BST][…] L42/L268; relaySet`，
  便于人工定位，但**不参与判定**。
- **`usedByTm` 优先于 `aliasesUsed`**：实测 `TM600.aliasesUsed = ["pmid2sw"]` 漏登记 `bst2sw`，
  而 `usedByTm` 明确列出 TM600 ⇒ 若只信 `aliasesUsed`，本缺陷**仍会被漏检**（这是本任务最关键的一处判断）。
- **`--check-extra`（默认关闭）**：SetOn 出现不在"别名闭合并集 ∪ relaySet ∪ 角色继电器"中的 K 号即红；
  供 K109 裁定（"不得多闭"）使用，**开关由契约/裁定控制，无需改代码**。

## 4. 验收证据

### 4.1 阳性对照（本任务最关键）——当前树必须红 ✅

```
python scripts/verify_bst_sw_sequence.py --list-scope
[t30] 生效作用范围 = ['TM600_HS_RDSON', 'TM601_LS_RDSON']
[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] vs payload SetOn 比对完成, 缺失=[110] (缺失数 1)
[t30] TM601_LS_RDSON: 契约声明必需 [60, 61, 154, 155] vs payload SetOn 比对完成, 缺失=[] (缺失数 0)
[scan] targets=4 FAIL=1
*** FAIL (BST-SW GOLDEN SEQUENCE) ***
  - TM600_HS_RDSON: 契约声明必需的继电器 K110 **未出现在 cbite.SetOn 中**
    (契约来源: aliasResolution[bst2sw].closedRelayNumbers (usedByTm lists TM600)
     | 契约侧 locator: pinRouteTable[BST][列2: FPVIe → PIN (BUS继电器) | CH0 Low] L42;
                       pinRouteTable[BST][列2 … CH1 Low] L268; relaySet
     | payload locator: test.cpp:9081; 该函数实际闭合=[K126_V1P5_CAP, K13_VBAT_Cap, K57_CAP_BST_SW,
                        K60_BUSL0_VCP, K61_ACM8_SW, K83_BUSH0_PMID, K85_CAP_PMID])
exit=1
```
日志：`gate-logs-t30/bst-sw-positive-control.log`

### 4.2 阴性对照 ✅
- **同一次运行内 `TM601_LS_RDSON` 缺失 = `[]`**（零误报）；
- **存量 TM643 两条仍为 WARN、未升级**：`relay-trace` = **GREEN**（`gate-logs-t30/relay-trace.log`
  与 t28 时**同哈希** `bf2e3da7183026e0…` ⇒ 逐字节未变）。

### 4.3 只增不改（等价性证明）✅
`python scripts/verify_bst_sw_sequence.py --skip-contract-closures` ⇒ `targets=4 FAIL=0` /
`BST-SW SEQUENCE PASSED` / **exit 0**，与**修复前脚本**输出一致 ⇒ 新增断言是**纯增量**，
关掉后行为完全回到原状（同时也证明既有序列判据与目标集**未被改动**：`--list` 仍为
`TM607/608/609/640`，与备份脚本一致）。

### 4.4 门禁级（契约 verify 命令）✅
```
pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t30
→ FULL_EXIT = 1
12 门 = 10 GREEN + bst-sw NEW-RED + cbit KNOWN-RED
*** 新增红 1 个（阻塞）***  [bst-sw] BST-SW 黄金约束 exit=1
    - TM600_HS_RDSON: 契约声明必需的继电器 K110 **未出现在 cbite.SetOn 中** …
存量红（已知, 不阻塞）: cbit
```
⇒ **只有 `bst-sw` 由 GREEN 变 NEW-RED，其余 11 门逐字不变**（`relay-trace` GREEN、
`input-sync` GREEN、`cbit` KNOWN-RED）⇒ 精确、无误伤、走 NEW-RED 分类器。

### 4.5 转绿条件（留给 t29 落盘后复核）
**转绿条件取决于契约口径 —— 三情形并列（Captain 定的最终口径）**：

| 情形 | 契约期望（TM600） | 落盘后判定 |
| --- | --- | --- |
| **rev 24（现状）+ 落 t29 payload** | `[60,61,83,110]` | t29 补 `110` 后 `缺失=[]` ⇒ **GREEN**（原预期成立；但该契约字段跨族无效） |
| **rev 25（BST 侧 `[48,76]`）而 payload 未同批改** | `[48,60,61,76]` | TM600 仍缺 `[48,76]` ⇒ **仍 NEW-RED = 第二处真缺陷（非回归、非 t29 之错）** |
| **rev 25 + payload 同批（Captain 裁定 (i)，本 run 实际分支）** | `[48,60,61,76]` | payload 同批补 `K48/K76` ⇒ **期望 GREEN**；**不存在"落盘后仍红"的例外路径** |

**闭集更正（Captain 2026-09-16）**：BST–SW 闭集应为 **`[48,60,61,76]`**（我先前给的是 `[48,61,76]`，已更正）——
**BST 侧 ∈ ACM200 族 `[48,76]`、SW 侧 ∈ FPVIe[L] 族 `[60,61]`**；这台仪器是**跨域复合**设计。
⇒ "ch5 `[48,76]`" 指 **BST 侧**（正确）；但**门禁期望应为两侧并集 `[48,60,61,76]`**。
⇒ TM600 现盘已闭 `{60,61}`、**缺 `{48,76}`** ⇒ **红色叙事的目标 = "缺 `48/76`"，不得写成"缺 K110"**。
（现算核对：`gate-logs-t30/t30_check_closureset.py` → `t30-check-closureset.log`；部署态已闭 `{60,61,83,13,57,85,126}`，相对该并集缺 `{48,76}`。）

| 契约口径 | 期望集合 | t29 落盘后部署态 | 判定 |
| --- | --- | --- | --- |
| **rev 24（现状，pin-18 口径）** | `[60,61,83,110]` | 缺 `110` 被补上 ⇒ `缺失=[]` | ⇒ **`FAIL=0`，门禁转 GREEN**（原预期成立） |
| **rev 25（`t42`/`t44` 判 ch5 后，`[48,76]` 口径）** | 仅 **TM600**：BST `[48,76]` + SW `[61]` | TM600 部署态**仍缺 `48/76`**（payload 亦缺）；**TM601 不受此期望约束**（其别名是 `sw2pgnd=[154,155,60,61]`，部署态**已满足**） | ⇒ **仅 TM600 仍 NEW-RED**，属**第二处真缺陷**（TM600 未闭 `[48,76]`），**不是回归、也不是 t29 的错** |
| 备注 | TM1205 | 契约 `bst2sw.usedByTm` 含 TM1205，但 TM1205 不属本门禁默认作用范围（`--tm-scope`），且其变体通路在契约中**无 `aliasFlatTable` 经查为空** ⇒ 期望不可从契约派生 | 见 §6 超范围发现 |

- 本断言**只要求契约声明必需者**，故 `t29` 只补 `K109+K110` 在 rev 24 口径下即可转绿；
- `K109` 若日后裁定非必需，只需**改契约**（或加 `--tm-alias`/`--check-extra` 参数），**断言代码无需改动**；
- **ch5 口径的断言修订须由 Captain 另派任务**（范围仅 `scripts/verify_bst_sw_sequence.py` + 日志），
  **不得改动 `gate_baseline.json`**；且届时须给**阳性对照**（当前树缺 `[48,76]` ⇒ 必须报红）。
- **更正（schematic-expert 指出、我重算确认）：TM601 行已撤销****：我方先前的 `t33_postreplace_expectation.log` 把 bst2sw 的期望套到了 TM601 上（"TM601 pin-5 缺 [48,76]"）——**该行作废**。按现盘契约重算（`gate-logs-t30/t30-rederive-expectation.log`）：
  · `bst2sw.usedByTm = [TM600, TM1205]`、`sw2pgnd.usedByTm = [TM601]`；`TM601.aliasesUsed=['sw2pgnd']` ⇒ **TM601 现行契约下 `缺失=[]`（绿）**；
  · 故 rev 25 后**只有 TM600 需要闭 `[48,76]`**；若把 TM601 也纳入 bst2sw，会产生**假红**，并可能把实现推向 **t38 已明确移除**的"TM601 ACM 驱动"方向（t38 结论：TM601 的 ACM 驱动**无需**到达 BST）。
  · **给 rev 25 的护栏**：修订时**不得**把 TM601 加入 `bst2sw.usedByTm`（其 ACM 变体属别的别名）。
- 取证：`gate-logs-t33/t33_postreplace_expectation.log`（脚本 `t33_postreplace_expectation.py`，已登记进 `t28-anchors.json`）。

## 5. 改动清单与哈希（python 明文）

| 文件 | 前 | 后 |
| --- | --- | --- |
| `scripts/verify_bst_sw_sequence.py` | 12185 B / `92250484d0dde498af620ff8847b79e352fd69c822b888188dc14414752e148c` | **24964 B / `17092feac034902e463fc5f14c79dc48cb1195436eda14f26d25691e11d54c78`**（行尾保持 **CRLF**：534 行；无 BOM 保持） |
| `scripts/gate_baseline.json`（**明令未改**） | — | `021015da84e6fd4c…02cb1d`（28 B，未变） |
| `setup-contract.json`（只读权威） | — | `fd00a5082170293fcea29446c009fc432977d61a8f624ef17ac1c82f41515a18`（328805 B，rev 24，未改） |
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`（未改） | — | `15c7d2b8d37b1564…`（469714 B） |
| `D:/PROJECT6-DALI/devel/source/test.cpp`（生产树只读） | — | `5c9cb3f9339f6db3…`（434629 B，未变） |

备份：`gate-logs-t30/backups/verify_bst_sw_sequence.py.pret30`（`92250484…`）。
补丁器（逐版可复现）：`t30_apply.py`(v1) → `t30_apply_v2.py` → `v3` → `v4` → `v5` → `v6` → `v7`（最终）。

### 5.1 规则原文前后 diff 与 locator（`scripts/verify_bst_sw_sequence.py`，改后）

| 位置 | 变化 |
| --- | --- |
| 常量区（`BST_CAP_RELAY` 之后） | 新增 `DEFAULT_TM_SCOPE = ["TM600_HS_RDSON","TM601_LS_RDSON"]` 与 `CONTRACT_RULE_NOTE` |
| `main()` 之前（新增 ~190 行） | `_load_contract` / `resolve_contract_path` / `resolve_scope` / `parse_alias_overrides` / `_numbers_from_payload` / `_nums_of_relay_entry` / `_base_of` / `_locators_for` / `_alias_index` / `expected_for_tm` / `check_contract_closures` |
| `main()` 的 `errors: list[str] = []` 之后 | 新增契约断言接线：解析契约路径（`--contract` > proj_config > `<ws>/team/artifacts/<run>/setup-contract.json`）→ 读契约（失败即红，**不静默跳过**）→ 解析 `--tm-scope`/`--tm-alias`/`--check-extra` → 结果并入 `errors` |
| `main()` 末尾既有出口 | **未改**：`if errors: ... return 1`（新增断言复用该致命出口） |
| **未改** | 既有序列判据（`check_ls`/`check_hs`/`require_exact_count`）、目标派生 `derive_targets`、`BST_SRC`/`BST_CAP_RELAY`、入口参数语义 |

## 6. 我主动报出的超范围发现（**未纳入默认判定**，请 Captain/复核裁定）

| 对象 | 实测事实 | 我的判断 |
| --- | --- | --- |
| `TM1205_TRX_BST_UV_GD` | 契约 `bst2sw.usedByTm` 含 TM1205，其 `relaySet` 含 61/110；而 payload 闭的是**自己的 path 别名**（`K_FPVIH_TO_SW1_A=46`/`K_FPVIL_TO_BST1_A=41`）⇒ 扩展范围后会 `缺失=[61,110]` | 与 K110 同源的**契约登记不对称**；`t29` 只处理 TM600/601 ⇒ **若纳入默认判定，t29 落盘后门禁仍红**。故**默认不纳入**，另作裁定项（证据：`bst-sw-extended-scope-tm1205.log`） |
| `TM108/TM109` | 契约 `pgnd2sw.usedByTm` 含二者，但该别名属 **ramp 段**，Step 1 不闭合 | 属"作用域语义"问题，非本缺陷；纳入即误报 |
| **TM1205** | 契约 `bst2sw.usedByTm` 含 TM1205；但其实际通路是**变体行**：`aliasFlatTable[14] bst1_sw1`、`[15] bst2_sw2`（契约**顶层**字段，共 16 条） | **登记错项**（BST1/BST2 ≠ BST）⇒ 把 `[110,61]` 套给它亦会假红；**且 TM1205 不在本门禁默认作用范围** ⇒ 当前不产生假红。**建议并入 rev 25 消歧**（Captain 已升为第 4 条待办） |

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

| **更正（我方自查）：`aliasFlatTable` 是契约顶层字段**：`aliasFlatTable` 是契约**顶层**字段（本契约共 16 条），不是 `tmDeltas.<TM>` 的子字段 —— 我先前只查了 `tmDeltas.TM1205.aliasFlatTable`（0 条）并**误报"不可复核"**，**该误报作废**。实测 `aliasFlatTable[14]` = `bst1_sw1`（`variantOf=bst2sw`，`relayPath="CH0 High -> SW1 需闭合 K46 ; CH0 Low -> BST1 需闭合 K41"`）、`[15]` = `bst2_sw2`，与部署态 `test.cpp:8791`（`K_FPVIH_TO_SW1_A=46` + `K_FPVIL_TO_BST1_A=41`）完全对齐 ⇒ **对方向我指出的 locator 是正确的**。 |

## 7. 限制与残留风险（不隐藏）

1. **作用范围是显式默认值**（`TM600_HS_RDSON,TM601_LS_RDSON`），由 `--tm-scope` 覆盖。理由已实测：
   取门禁内部 targets ⇒ 失效（v3）；取 `usedByTm` 全量 ⇒ 误报（v4）。**若裁定要求覆盖 TM1205，改参数即可，判据不动。**
2. **`usedByTm` 语义假设**：本判据假设 `usedByTm` 列出的别名，其 `closedRelayNumbers` 对该 TM 是
   **Step 1 必须闭合**。TM108/109/TM1205 的反例说明该假设**不总成立** ⇒ 这正是需要显式范围的原因；
   若要根治，应由契约 owner 在 `tmDeltas` 增加"逐函数 needsClosed"字段（**不在本任务 inScope**）。
3. **`--check-extra` 的允许集**含 `relaySet ∪ 角色继电器(K*_Cap 等)` 白名单以抑制误报；K109 若被判
   "非必需"，只需不改契约（或在契约中登记），断言代码无需变动；但白名单本身是**启发式**，需复核确认。
4. **本任务只让"漏闭"可检出**，不修复 `test.cpp`（属 t29）；**未编译**。
5. **边界声明**：无任何电性/硬件结论；**编译成功 ≠ 电性正确**。
6. **v1–v4 全部被我自己推翻并记录**（判据选择过程见 §2 与 `t30-criteria-probe.txt`），
   最终文件只含 v7 形态；每版补丁器与前后哈希均留档，便于复核追溯。

---

## 9. 加注：期望集合的前提依赖（Captain 裁定 2026-09-16）

### 9.1 (a) 期望集合的推导来源（逐条 locator）

| 步骤 | locator | 内容 |
| --- | --- | --- |
| 1 | 契约 `aliasResolution[bst2sw].usedByTm` | 字面串 `"TM600 (BST must lead PMID)"` ⇒ 经 `\b(TM\d+)\b` 抽出 base=`TM600` |
| 2 | 契约 `aliasResolution[bst2sw].resolution.closedRelayNumbers` | `[110, 61]` ⇒ 本函数期望集合 {60,61,83,110}（另含 `pmid2sw` 的 83/60/61） |
| 3 | 契约 `aliasResolution[bst2sw].resolution.relayChain` | `[{K110_ACM18_BST, 'SetOn (ACM200 S5_FH18 -> BST)'}, {K61_ACM8_SW, 'SetOn (ACM200 S5_FH8 -> SW)'}]` |
| 4 | 契约 `tmDeltas.TM600.aliasesUsed` | `['pmid2sw']` —— **漏登记 `bst2sw`**，故本断言改以 `usedByTm` 为主索引 |
| 5 | 被审脚本 | `expected_for_tm()` 的两处 `setdefault` 即上述两源；作用范围 `DEFAULT_TM_SCOPE` / `--tm-scope` |
| 6 | 阳性对照 | 部署态 TM600 SetOn 无 110 ⇒ `缺失=[110]` ⇒ `FAIL=1` ⇒ `bst-sw` NEW-RED |

**⚠️ 我方如实登记的附加风险**：第 1 步是**从 `usedByTm` 的散文描述里用正则抽 TM 号** ——
即期望集合**部分依赖人类可读文本**；若该描述被改写（如写成 `TM600x`），期望集合会**静默变化**。
根治应把"别名→TM 归属"改为**结构化字段**（属契约侧，非 t30 inScope）。

### 9.2 (b) 前提依赖：本期望集合**以 pin-18 为前提**

- 宏 `Pin_Channel_define.h`: `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,S6_5,…"` ⇒ **通道 `_5`**；
- 而契约 ACM200 侧条目 `tmDeltas.TM600.pinRouteTable.BST["列6: ACM200 → PIN (Share继电器)"]`
  的 `needsClosed = [48, 76]`；`StdAfx.h` 亦分列两条通路：`K_BST_ACM = 48,76`（ACM200[] → BST）
  与 `K_FPVIL_TO_BST_B = 109,110`（**FPVIe[L]** → BST）。
⇒ **"到 BST 需 `[110]`"只成立于 pin-18 前提**（即 `SW12_U1REF_BST_ACM` 这台实例落在 ACM200 的
FH18/SH18 脚）。**该前提由 `t42`（schematic-expert）独立裁定。**

> **前提已判（`t42` + `t44`）：走 `ch5` ⇒ 到 BST 需 `[48,76]`。** 其最强证据为**行为层**：
> `test.cpp:7000/7087/7170/7513` 这些**已执行**调用点闭 `K48_ACM5_AMP_REF` + `K76_ACM_BST`，
> 且 `:6997/:7598/:7621` 注释把 `SW12_U1REF_BST_ACM` 与 `ACM200_FH5` 写在同一句；
> `K_BST_ACM` 复合宏被**主动降级**为意图/文档证据（**1 定义 / 0 调用点**）。
> ⇒ **本门禁的 ch5 口径修正待 Captain 派单**（见 §4.5 两口径表）；在那之前，本文件一律按**契约 rev 24** 判定。
⇒ **若 `t42` 判 pin 5**：期望集合应改为 `[48,76]`，或**按路线拆分**（ACM 侧按 pin 5 口径、FPVIe 侧保持）
——Captain 已声明届时另派任务，**且届时不得改动 `gate_baseline.json`**。

### 9.3 (c) ACCEPT 的覆盖边界（不得过度解读）

> **本门禁的 ACCEPT 只覆盖"盲区已关闭"（即：契约声明必需的闭合集不再被门禁无视、
> 缺失必走致命通道、阳性对照成立、只增不改），不覆盖"pin 归属前提"的正确性。**
> 前提正确性属 `t42` 的裁定范围；**不得把本 ACCEPT 读作"前提已裁定"**。
> 这与 **B-6**（"由契约派生的断言，其覆盖上限＝契约登记的完整性"）互为镜像：
> 断言既不能覆盖**错登记**，也不能把**未消歧登记**固化为既成事实。

### 9.4 加注：`t30` 前门禁的**两个**盲区成因（入档）

1. **不读契约**：`verify_bst_sw_sequence.py` 原先 `setup-contract` / `aliasResolution` /
   `needsClosed` / `relaySet` / `K109` / `K110` 命中数**均为 0**；
2. **目标集不含 TM600**：其 `targets` 由 meta `powered_pins` 拓扑指纹派生 =
   `TM607/608/609/640`（ZCD 家族）⇒ **TM600 不在其中**；
   ⇒ **只加"读契约"而不改作用域，阳性对照仍是 `FAIL=0`**（我方实测，见 §2 第 3 行）。
   最终以 **`--tm-scope` 显式参数化**（默认 `TM600_HS_RDSON,TM601_LS_RDSON`）。

**边界**：以上均为静态连通性/登记层面的结论；**无机台实测**；**编译闭环 ≠ 电性签核**。
