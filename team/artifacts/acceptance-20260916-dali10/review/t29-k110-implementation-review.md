# t29 独立实现审查（K110 修复落地前复核）

- 审查人：rule-reviewer（独立于实现者 ate-implementer）· 日期：2026-09-16
- **被审对象**：`team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp`
  **36,381 B / python-plaintext sha256 `73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e` / mtime 19:17:11** —— 与申报**逐位一致** ✅
- **只读声明**：未修改任何被审产物。

> **⚠️ 复核期间 `test-plan.json` 发生版本推进（已核实不影响本 verdict）**
> 我取证时（t29 复核开始）计划为 **v20 = 166,099 B / `fabdd24f…`**；**复核结束时已变为 v21 = 176,875 B / `f0f825dd302d4105676b113f2335bc1f6fe54c8bcd46a32d621c1026c111dc04` / mtime 19:24:17**（`revision` 自述为 **`v21 (t27 - authorised, freeze lifted inside this scope only)`**）。
> **v21 的三项变更**（依其自述 + 我关键词核验）＝① teardown 措辞消歧（双浮动通道下**测量通道最后释放**）；② 初始化量程入计划（1 V 量程 / 10 uA 电流档）；③ 采样说明精确化（COUNT 200 在方法库层为 10 µs 周期，PAIR (200,5) 属黄金专属）。**关键词扫描：`K57` 不在 revision 文本内、`K110` 不在、`BST` 仅作 teardown 语境出现。**
> **我逐项复核 v21 中本 verdict 所依赖的内容，全部未变**：`closed set [110,61]` 仍 **3 处**（`items[TM600].assumptions[0]`、`globalRulesApplied` 的 **R-BST-SW**、以及 boundary 表述），`SW12_U1REF_BST_ACM` **3** 次、`INTENDED BUT CURRENTLY UNREALISABLE` **1** 次、限值 `11/7.5/4.4/4.15` 计数不变；**`K109` 在计划中仍 0 次**（⇒ 计划只写 `[110,61]`，`K109` 的权威来源仍是契约 `relaySet`/`pinRouteTable` + `SCH`）。
> ⇒ **判据仍绑定**：(a) 的最小端点判据与 (b) 的 TM600 集合判据**不因 v21 而改变**。**本 verdict 针对 payload `73b511b7…`，与计划 v20/v21 的切换无关。**

## 结论：**verdict = pass**（四条预先承诺判据全部满足；(b) 另附一项须由 `t35` 归口的契约缺项，不阻塞本 payload 的「可落盘」结论）

---

## 1. 四条判据逐项

### (a) 只补契约权威集合所需继电器（最小端点）—— ✅ PASS

| 新闭继电器 | 权威依据（locator） | 判定 |
|---|---|---|
| `K110_ACM18_BST`（110） | 契约 `/tmDeltas/TM600/relaySet` **含 110 与 109**（我实测：`109 in relaySet: True`、`110 in relaySet: True`）；契约 `/aliasResolution[3].resolution.closedRelayNumbers[0]=110`；`SCH-Connect-Map.txt` L43 `… K109(ON) -> K110(ON) -> BST_F` | ✅ 属权威集合 |
| `K109_BUSL1_PB0`（109） | 契约 `/tmDeltas/TM600/pinRouteTable.BST/"CH0 Low" → needsClosed=[109,110,138,139,145,146]`（contract line 42）；`SCH` **L42** `CH0 Low -> BST [Kelvin] 需闭合: K109,K110,…`；`SCH` L43 的串行链含 `K109(ON)` | ✅ 属权威集合 |

**最小端点结论**：payload 新增**恰好两点**（`L219` 由 7 项 → 9 项：新增 `K109_BUSL1_PB0`、`K110_ACM18_BST`），**未新增任何其它继电器**；且 TM600 的其余既有项（`K83/K60/K61/K13/K85/K57/K126`）**一字未动**。**未越出契约权威集合** ✅

### (b) 两函数判据显式 —— ✅ PASS（附一项契约缺项，见 §2）
- **TM600 = 需要**：如上表，`K109`/`K110` **明确在** `relaySet` 与 `pinRouteTable` 权威集合内。
- **TM601 = 未补，且已给理由**：payload `L355-393` 的 TM601 段只闭 `K154,K155,K60,K61,K13,K85,K57,K126`。**其判据来自契约侧**：我实测 **TM601 的 `pinRouteTable` 根本没有 `BST` 条目**（仅 `SW`/`PGND`），且 `TM601.relaySet` **不含 109/110** ⇒ 按契约口径 TM601 **无** BST−SW 闭合要求。**⇒ "只改一处"有可核依据，非默默漏改** ✅
- ⚠️ **但这暴露一个契约侧空缺**（不是 payload 缺陷）：TM601 **也**驱动 `SW12_U1REF_BST_ACM`（`L407` `Set(FV, 5, …)`；`L476/L482` 归零/下电），而**没有 K109/K110 时该 5 V 到不了 BST 节点**（同 TM600 的机制）—— 即"**驱动了源但无对应闭合集合**"。**该矛盾属契约口径，已由 Captain 派 `t35` 归口**；详见 §2。**不影响本 payload 的判定**（payload 既满足 TM600 的权威集合，又未越出 TM601 的契约集合）。

### (c) 机制/证据 locator 已写入注释 —— ✅ PASS
payload `L205-217` 逐条写入，**且我逐条核对无误**：
- `L205-208`：*"`K110_ACM18_BST` is a **DOUBLE-THROW** relay and its name alone does NOT route the source to BST"* + `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F (SCH:724)` / `SH18 -> … (SCH:725)` ⇒ 与 `SCH` 实测一致 ✅
- `L210-211`：`… K109(ON) -> K110(ON) -> BST_F (:43)`／`… K110(Relay-NC) -> PB0_F (:109)` ⇒ 与 `SCH` 实测一致 ✅
- `L212-213`：*"`K109_BUSL1_PB0` selects the branch. Route requirement: CH0 Low -> BST needsClosed K109,K110,… (:42; contract pinRouteTable BST/CH0 Low = [109,110,138,139,145,146])"* ⇒ 与契约/`SCH` 一致 ✅
- `L217`：*"K109/K110 are NOT part of the forbidden 87/88/89/90/91 class"* ⇒ 见 (d) ✅

### (d) 未误伤负列表（`K87/K88/K89`、`K131/K132/K133`）与 `_S1S2` —— ✅ PASS
我按 SetOn 的**继电器号**逐项比对：

| 函数 | SetOn 继电器号 | 负列表命中（87,88,89,90,91,131,132,133,134,135） |
|---|---|---|
| `TM600_HS_RDSON`（L219） | `[13, 57, 60, 61, 83, 85, 109, 110, 126]` | **0** ✅ |
| `TM601_LS_RDSON`（L393） | `[13, 57, 60, 61, 85, 126, 154, 155]` | **0** ✅ |

- `K88/K89` 在 `SCH` L43/L44 为 **`Relay-NC`（默认导通）**，payload **未 SetOn 它们**（正确：不得为通 BST 而动作负列表类继电器）✅
- `K131/K132/K133/K134/K135`（裁定 (ii) 定为 unrealisable 的 ch1 复合类）**均未出现** ✅
- **`_S1S2` 共享家族**：`K57_CAP_BST_SW`／`K13_VBAT_Cap`／`K85_CAP_PMID`／`K126_V1P5_CAP` 等在两函数中均被闭合，与既有共享闭合做法一致（`SCH`/`Dali-SCH.csv` 标注 `_S1S2`），**未新增跨 site 冲突**；新增的 `K109/K110` 为**逐 site 路径继电器**，不引入新的共享面 ✅

### 另核：`PMID_HG2` 10 V 台阶 —— ✅ PASS
`L245`（升）与 `L314`（回落）**均为 `FXVIe_PLUS_20V`**，满足 ≥2×（10 V→20 V）；其余配对复核无变化：5 V→`10V`（L240/L318）、15 V→`30V`（L250）、TM601 9 V→`20V`（L409）。

---

## 2. ⚠️ 需 `t35` 归口的契约缺项（**不影响本 payload 判定**，但请写入其验收）

我在核 (b) 时发现**契约侧的三处不一致确认存在**（实现者所报属实），其中**第 2 条最具实质影响**：

| # | 契约不一致 | 我的独立核验 | 对本 payload 的影响 |
|---|---|---|---|
| ① | `aliasResolution[3].resolution.closedRelayNumbers = [110,61]` **漏 `K109`** | 实测该数组确为 `[110,61]`；而 `pinRouteTable.BST "CH0 Low"` = `[109,110,138,139,145,146]`、`SCH` L42/L43 串行链含 `K109(ON)` ⇒ **两处口径不一致** | **无**（payload 已按更完整的 `needsClosed` 补 `K109`，且 `K109` 在 `relaySet` 内 ⇒ 不越界） |
| ② | 该条 `terminalAssignment.high = "BST"` 建立在 **FPVIe CH1** 框架上，而裁定 (ii) 的 BST 由 **ACM200 `SW12_U1REF_BST_ACM`** 驱动 ⇒ **契约未确立该驱动下"哪个端子承载 BST"** | 实测 `terminalAssignment` 文本确为 CH1 框架；`bstRuling_ii` 同时声明 CH1 不可实现 ⇒ **自相矛盾** | **无**（TM600 的 BST 闭合依据来自 `relaySet` + `pinRouteTable CH0 Low`，不依赖该 `terminalAssignment`） |
| ③ | `pinRouteTable.TM600.BST` 仍有 `"CH0 High" -> needsClosed=[46,48,76]`（contract line 39），属裁定 (ii) 判定 unrealisable 的类 | 实测存在 | **无**（payload 未闭合 `46/48/76`；且该条目与"CH0 Low"路径并存，未被 (ii) 废除） |

**⚠️ 我另行发现、建议一并给 t35 的第 4 条（比①②③更实质）**：
**TM601 驱动了 BST 源却无 BST 闭合集合。** payload `L407`（及 `L476/L482`）对 TM601 施 `SW12_U1REF_BST_ACM.Set(FV, 5, …)`，**但 TM601 的 `pinRouteTable` 无 `BST` 条目、`relaySet` 不含 109/110** ⇒ 按现契约，**该 5 V 到不了 BST 节点**（机制同 TM600）。
**请 t35 明确**：TM601 是否**也应**闭合 `K109/K110`（若"应"，则现 payload 在 TM601 侧存在**同类缺失**，须另派修复；若"不应"，须说明 TM601 的 BST 由何路径建立 —— 否则 TM601 的 `SW12_U1REF_BST_ACM` 驱动是**无落点的悬空激励**）。
**本 verdict 不因此改判**：因为我判的是"payload 是否符合**契约权威集合**"，而现契约对 TM601 的 BST 要求**未表达**；**要求一旦由 t35 确立，请按新口径另派 patch 并再次交我复核**。

---

## 3. 其余复核（实现者自报项，我独立复现）

**代码不变量（去注释后可执行计数）**：`delay_ms(1)`=**6** ✅、`delay_ms(2)`=**0** ✅、`SetClamp(50, 50)`=**2** ✅、`MeasureVI(200, 5, FPVIe_MV_X10)`=**2** ✅、裸 `126`=**0** ✅、`K126_V1P5_CAP`=**2** ✅、`ERROR_RES`=**2** ✅。
**t22 电容裁定保持**：`K5_VBUS_Cap`=**0**、`K44_Cap_SW2_BST2`=**0**、`K45_Cap_SW1_BST1`=**0**、`K57_CAP_BST_SW`=**2** ✅ ⇒ 与我 t24 结论**完全一致**。

**⚠️ 门禁自报项我**未**独立复现**（其数字我采信为 **implementer-reported**）：`relay-trace PASSED`（FR-001 反向 3→2）、`bst-sw PASSED targets=4 FAIL=0`、`awg PASSED FAIL=0 WARN=0`、新增红 0。**理由**：这些需在沙箱重跑门禁，属落盘后复核环节；**我未运行**，故不冒称已复核。**建议由 `t30` 的门禁断言（含阳性对照）在落盘后承担该验证。**

**⚠️ 配套证据哈希漂移（记录，非判据）**：Captain 公告 `t29-k110-evidence.md` = 8,537 B / `660014a2…`，**我实测为 10,062 B / `1069e025bf0dc449474d4dbc7d732308474aeb5ab22425e7c648ad00296f5250`**（mtime 19:21:40）⇒ 该证据文件在公告后被再次写入。**不影响 payload 判定**（payload 哈希逐位一致），但引用时请以现算为准。

---

## 4. 交付与后续

- **`verdict = pass`（针对 `73b511b7…`）**：四条判据全过；**本 payload 可进入 REPLACE 落盘**（落盘由 Captain 执行）。
- **落盘后须补的三项独立验证**（均**不属**本 verdict 覆盖）：① `t30` 的"SetOn vs 契约 `needsClosed`"断言须在**落盘前对缺 K110 报红、落盘后转绿**（**阳性对照由我在只读沙箱重放**）；② `relay-trace`/`bst-sw`/`awg` 的 exit code 与 NEW-RED 分类（须以**现盘树**重跑并附现算哈希）；③ `t35` 归口后若确立 TM601 的 BST 要求，须**另派 patch 并二次复核**。
- **仍未决**：`t35` 契约四项归口；`t28` 的 RS-1..RS-4 落地（消除"重生成静默抹除"）；`t31` 审计链。
