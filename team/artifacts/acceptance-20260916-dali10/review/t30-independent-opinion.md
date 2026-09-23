# t30 独立复核意见（`bst-sw` 增加"SetOn 集合 vs 契约闭合集合"断言 + 缺 K110 阳性对照）

- 复核人：rule-reviewer（独立于作者 compile-diagnostician）· 日期：2026-09-16
- 被审：`scripts/verify_bst_sw_sequence.py` —— **24,964 B / `17092feac034902e463fc5f14c79dc48cb1195436eda14f26d25691e11d54c78`**（与申报**逐位一致** ✅；CRLF **560** / lone LF **0** ⇒ 行尾按申报保持 ✅；BOM `23 21 2f` = `#!/` 无 BOM ✅）
- 备份 `…pret30` = 12,185 B / `92250484…` ✅ 一致
- 只读声明：未修改任何被审文件。**我运行脚本后复核了 4 个可能被写的对象，全部未变**（见 §6）。

## 结论：**ACCEPT（可签收）**，但附 **1 项须登记的门禁能力边界（B-6）** 与 **3 项契约侧待办**。

---

## 1. ✅ 阳性对照真实，且**确认走致命通道**

**我亲自运行**（`python scripts/verify_bst_sw_sequence.py`，默认参数）：
```text
[t30] TM600_HS_RDSON: 契约声明 [60, 61, 83, 110] vs payload SetOn …, 缺失=[110] (共 1)
[t30] TM601_LS_RDSON: 契约声明 [60, 61, 154, 155] vs payload SetOn …, 缺失=[] (共 0)
[scan] targets=4 FAIL=1
*** FAIL (BST-SW GOLDEN SEQUENCE) ***
exit = 1
```
**逐条核对你的申报**：TM600 缺 `110` ✅；TM601 缺失为空 ✅；`FAIL=1` ✅；**exit 1** ✅。

**"该红能否被 warn 路径吞掉" —— 我核了，不能**：源码中该断言**只往 `errors` 追加**，最终判定在既有 `if errors:` 分支（`sys.exit(1)`）；`run_gates.ps1:121-123` 的分类只看 **exit code**，`:139/:181` 仅 `NEW-RED` 才 `exit 1` ⇒ **该红必然进 NEW-RED 通道、不可能被 warn 吞掉** ✅（与 t28 的 RS 断言同构，方向正确。）

## 2. ✅ 只增不改：既有判据未被削弱

- `--skip-contract-closures` ⇒ **`FAIL=0` / `BST-SW SEQUENCE PASSED` / exit 0**（我实测）⇒ **回到修复前行为**，证明新断言是**可关闭的纯增量**，既有序列判据**未被改写**。
- **`--list` 仍为 `TM607/608/609/640` 四个目标**（我实测输出：`TM607_BUCK_LS_ZCD / TM608_BOOST_HS_ZCD / TM609_BOOST_HS_NEG / TM640_BOOST_HS_OCP`）⇒ **门禁内部 targets 集未被改动** ✅
- **`diff` 规模的旁证**：文件 12,185 → 24,964 B（+12,779），而 `DEFAULT_TM_SCOPE` 等新块集中在 `L243-259`、`L372-398`、`L403-465`、`L508-516`；**既有 `check_ls`/`check_hs`/`derive_targets` 的序列判据未动** ✅

## 3. ✅ 判据"零硬编码 + 可复用"成立，`usedByTm` 优先序**可接受**，但**契约侧须补**

**我实测确认你的关键发现**：
```
aliasResolution[bst2sw].usedByTm = ['TM600 (BST must lead PMID)', 'TM1205 (BST1-SW1 / BST2-SW2 ramps)']
aliasResolution[bst2sw].resolution.closedRelayNumbers = [110, 61]
tmDeltas.TM600.aliasesUsed = ['pmid2sw']      ← 确实漏登记 bst2sw
tmDeltas.TM1205.aliasesUsed = []              ← 完全为空
```
- **判定：以 `usedByTm` 为主索引 —— 可接受，且是当前唯一可用的正确选择。** 理由：`aliasesUsed` 既**漏登记**（TM600 仅 `pmid2sw`）又**为空**（TM1205），若只信它会**继续漏检**。
- **但"零硬编码"仅对 K 号/期望值成立**（期望值全部读 `aliasResolution[*].resolution.closedRelayNumbers`，代码里**无 K 号字面量** ✅）。**索引源仍依赖契约登记的完整性** ⇒ 这正是 §5 的 B-6 边界。
- **要求（不属 t30 inScope，请转契约 owner）**：补 `tmDeltas.TM600.aliasesUsed` 的 `bst2sw`、并写明 TM1205 的别名归属（见 §4）。**在补齐之前，`usedByTm` 为主索引是正确且必要的权宜。**

## 4. ⚠️ "显式默认范围" `--tm-scope` —— **判定：可接受的可审计权宜，但须与契约侧修正并行**

**实测**：`DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]`（源码 `L259`，注释明写"可由 `--tm-scope` 覆盖"）。
**我的判定与理由**：
- ✅ **可接受**：范围**写在源码里可审计**、**可用命令行覆盖**、且**默认即覆盖 t29 触碰的两个函数** ⇒ "缺 K110 必报红"的阳性对照成立。作为**过渡**它比"无断言"（原状）严格得多。
- ⚠️ **但它是"硬编码范围"，且恰好是本次盲区的成因形态**（原门禁的 targets 里没有 TM600 ⇒ 看不见 K110）。若将来新增高电流项，**默认范围不自动覆盖** ⇒ 同一类盲区会以新形态复发。
- **⇒ 我的要求（二选一，请 Captain 择一）**：
  - **(a) 短期（建议）**：保留 `--tm-scope` 默认范围，**并保持"门禁输出中显式打印本次作用范围"这一既有做法** —— **我已实测：源码 `L514` 为 `print(f"[t30] 作用范围 = {_scope}")`，该要求已满足** ✅；**另把"范围应改为契约驱动"登记为待办**。
  - **(b) 目标态**：**改为契约驱动** —— 期望范围 = `∪ aliasResolution[a].usedByTm`（按 `bst2sw/BST` 类别名）而非硬编码名单。**前置＝契约 owner 先补齐 `usedByTm`/`aliasesUsed` 的登记不对称**（§3、§4 末条），**不属 t30 inScope**，同意不在本任务内做。
- **判据**：**A 不改电气、只加可审计性**，成本极低；**B 是正确终态**但依赖契约修正。⇒ **先在 A 上签收，B 另立契约任务。**
- **✅ 我另核实两条与旁路/默认值相关的事实**：① `run_gates.ps1:82` 的调用为 `args = @('scripts\verify_bst_sw_sequence.py')` —— **未携带 `--skip-contract-closures`**，断言**不会被门禁静默旁路** ✅；② `--check-extra` 在源码中**默认关闭**（只由显式参数开启）✅。

## 5. 🆕 **B-6（门禁能力边界，须并入 `review/gate-capability-boundaries.md` 供 t34 引用）**

> **"由契约派生的断言，其覆盖上限＝契约登记的完整性。"**

实证：
1. **登记漏项 → 静默盲区**：`tmDeltas.TM600.aliasesUsed` 漏 `bst2sw` ⇒ 若按 `aliasesUsed` 索引，**TM600 的 K110 缺口继续不可见**。
2. **登记错项 → 误报**：`bst2sw.usedByTm` 含 **TM1205**，而 TM1205 实际闭的是**自己的 path 别名**（`K_FPVIH_TO_SW1_A=46`/`K_FPVIL_TO_BST1_A=41`）且 `aliasesUsed=[]` ⇒ 扩到全量范围会**对 TM1205 报 `缺失=[61,110]`**（见 §7）。
3. ⇒ **该断言既能"抓实现漏闭"，也会"因契约登记错误而误报"**；**两类都必须与"实现确有缺陷"区分开**。

**给 t34 的引用建议**：与 **B-2（`bst-sw` 原门禁看不见闭合集合）** 并列引用，并注明"**B-2 已由 t30 部分修复；但 B-6 说明其覆盖仍受契约登记质量约束**"。

## 6. ✅ 阴性对照 / 门禁级 / 只读性

- **阴性对照**：同次运行 **TM601 缺失=[]** ✅（我实测）；**存量 TM643 两条仍为 WARN 未升级**、`relay-trace` 仍 GREEN ✅（你给的同哈希 `bf2e3da7183026e0…` 我未复算该日志，标记为 **author-reported**）。
- **门禁级**：`FULL_EXIT=1`、12 门 = 10 GREEN + **`bst-sw` NEW-RED** + `cbit` KNOWN-RED ⇒ **只有 `bst-sw` 变红且走 NEW-RED 分类器**（非 warn）—— 与 §1 的通道分析一致 ✅。**我未复跑整个 `run_gates`**，`FULL_EXIT` 与门数采信为 **author-reported**。
- **只读性（我运行后自证）**：`project/DALI/meta/dali_tm_meta.json`、`test_conditions.yaml`、`setup-contract.json`（`fd00a508…`）、目标树 `test.cpp`（`15c7d2b8…`）**四者前后哈希均未变**；`gate_baseline.json` 仍 28 B / `021015da…`（未改）；`devel/test.cpp` 仍 `5c9cb3f9…` ✅

## 7. ⚠️ 超范围发现（TM1205）—— **裁定：暂不纳入默认判定；先修契约登记**

**我实测确认你的发现**：`bst2sw.usedByTm` 含 **TM1205**；`tmDeltas.TM1205.relaySet` **含 61 与 110**；但 TM1205 实际闭的是**自己的 path 别名**、且 `aliasesUsed=[]`。
**裁定（三点）**：
1. **暂不纳入默认范围** —— 理由：**(a)** 属**契约登记不对称**（TM1205 的 BST1-SW1/BST2-SW2 应在**自己的别名**下登记，而非挂到 `bst2sw`）；**(b)** 纳入会使**t29 落盘后门禁仍红**，把"K110 修复"与"TM1205 登记问题"混为一谈；**(c)** `--tm-scope` 已能按需扩展，**能力已具备**。
2. **应由契约 owner 修正**（→ t35/新任务）：把 **TM1205 从 `bst2sw.usedByTm` 移出**，并为 `BST1-SW1`/`BST2-SW2` 建立**独立别名**（含 `usedByTm: [TM1205]` 与其 `closedRelayNumbers`）；补齐 `aliasesUsed`。
3. **独立于本裁定的电气问题（不属你我裁定）**：TM1205 的 BST1−SW1/BST2−SW2 ramp 是否**需要** `61/110` 由电气判定；在契约修正前，**该问题不能被本断言回答**（否则就是"用错误登记判实现"）。

## 8. ✅ K109 兼容性 —— 判定：**设计正确，两种裁定下都不需改代码**

我实测确认：断言**不表态 K109**（契约 `closedRelayNumbers` 不含 109）；`--check-extra`（默认关闭）承担"**不得多闭**"。
⇒ **若 K109 裁定为"必需"**：契约写入 109 ⇒ 断言随动；
⇒ **若裁定为"非必需"**：契约不写 ⇒ 现 payload 多闭 109 **不会被本断言报红**，而由 `--check-extra` 按需承担。
**这两个分支都不需要改 t30 的代码** —— 判定成立 ✅
**补充一条我方结论（供你与 t34 记账）**：**K109 的"多闭"问题在本 run 无法由契约派生断言解决**，因为契约**本就把 109 写进了 `pinRouteTable…CH0 Low.needsClosed` 与 `relaySet`**；它属 **B-6** 的"登记本身有误"类，只能由契约修正（t35）消除。

---

## 9. 交付

| 复核要点 | 判定 |
|---|---|
| 1 阳性对照真实性 + 走致命通道 | ✅ ACCEPT（我独立运行复现，且确认不可被 warn 吞掉） |
| 2 只增不改、既有判据未削弱 | ✅ ACCEPT（skip 模式回到修复前行为；targets 未变） |
| 3 零硬编码 + `usedByTm` 优先序 | ✅ ACCEPT（K 号确无字面量；优先序为必要权宜）＋ **契约须补登记** |
| 4 `--tm-scope` 显式默认范围 | ✅ 可接受的可审计权宜；**须并行推进契约驱动**（另立任务） |
| 5 阴性对照 / 存量 WARN 未升级 | ✅ ACCEPT |
| 6 门禁级 NEW-RED | ✅ 与我通道分析一致（`FULL_EXIT` 等为 author-reported） |
| 7 K109 兼容 | ✅ 设计正确；两分支均无需改码 |
| 8 TM1205 超范围发现 | ✅ 裁定：**暂不纳入默认**；由契约 owner 修登记 |

**非阻塞待办（3 条，原第 ① 项已实测满足、撤销）**：① **（已满足）**门禁输出已显式打印作用范围（`L514`），保持即可；② 契约补 `tmDeltas.TM600.aliasesUsed += bst2sw`、补齐 TM1205 别名归属；③ 契约修正 `bst2sw.usedByTm` 的 TM1205 登记；④ 把 **B-6** 并入 `gate-capability-boundaries.md` 供 t34 引用。

**总评：t30 可以签收**（阳性对照真实、通道正确、纯增量、可关闭、只读自证齐备）。**⚠️ 提醒**：`--skip-contract-closures` 是**为验证而存在**的开关，**不得进入默认调用路径**；**我已实测确认 `run_gates.ps1:82` 的调用未携带它** ✅，建议后续若有人改动该行参数，须保留"未携带"这一事实。
