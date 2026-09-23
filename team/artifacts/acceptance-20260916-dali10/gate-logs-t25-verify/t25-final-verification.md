# t25 门禁复核（在 t26 落地后，最终树）— 我本人独立执行，非采信二手

- 日期：2026-09-16
- 触发：setup-architect 告知"payload 已落盘 ⇒ relay-trace 已 GREEN、全套 exit 0"
- 处置：**不采信二手结论**，我用 python 明文复算哈希 + 本人复跑门禁 + 逐 token 复核
- 结论：**其 ③ 成立（并推翻我 t25 报告里的"未落盘"记录）**；同时暴露**我 F2 的验收判据在最终树上被元数据修复覆盖**，见 §4

---

## 1. 关键文件最终态（python 明文 sha256）

| 文件 | 我 t25 报告记录 | **现在（最终树）** | 变化方 |
| --- | --- | --- | --- |
| 目标树 `ForCodexDebug/source/test.cpp` | 462848 B `3dbceb49…`（含 2 处裸 `126`） | **469714 B `15c7d2b8…` mtime 18:53:33**（`bare-126` = 0，`K126_V1P5_CAP` ×3） | payload 落盘（非 t25） |
| `project/DALI/meta/dali_tm_meta.json` | 146180 B `1c849664…` | **147520 B `50efba4e…` mtime 18:52:27** | **t26**（非 t25） |
| 目标树 `StdAfx.h` | 56968 B `ba8ab3de…` | 56968 B `ba8ab3de…` | 未变 |
| `scripts/gate_baseline.json` | 28 B `021015da…` | 28 B `021015da…` | **未变（始终未被我改）** |
| `scripts/run_gates.ps1`（我修） | 9763 B `dd2a4337…` | 9763 B `dd2a4337…` | t25 |
| `scripts/verify_relay_trace.py`（我修） | 21068 B `65e0c67f…` | 21068 B `65e0c67f…` | t25 |
| `devel/source/test.cpp`（生产树只读） | `5c9cb3f9…` | `5c9cb3f9…` | **未变** |

⚠️ **我 t25 报告中的"payload 未落盘 / test.cpp 含 2 处裸 126"表述现已过期** —— 该表述在当时（我执行 t25 的窗口内）是**实测正确**的，但它已被后续落盘覆盖。**以本文件为准。**

## 2. 我本人复跑门禁（独立执行，命令与验收契约一致）

```
pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t25-verify
→ FULL_EXIT = 0
基线(存量红) 已加载: cbit                ← F1 生效
12 门 = 11 GREEN + cbit KNOWN-RED
relay-trace = GREEN exit 0
结论: 无新增红 —— 收尾通过（存量红 1 个）
```
`relay-trace` 明细：`99 个函数有继电器（结构规则 0，功能规则 182，FR-001 反向 2），meta 覆盖 101/101`；
**仅剩 2 条 WARN（均 TM643_VBAT_LOOP_INDICTOR：`K57_CAP_BST_SW`、`K5_VBUS_Cap`）**，`RELAY TRACE PASSED`。
⇒ 与验收契约中"预期仅剩 2 条存量 `TM643`"**完全吻合**。

**逐条归因**（我复算，不采信转述）：

| 变化 | 归因 | 证据 |
| --- | --- | --- |
| 2 处裸 `126` ERROR 消失 | **payload 落盘**（`K126_V1P5_CAP`） | 落地树正则 `bare-126` = 0；`K126_V1P5_CAP` ×3；TM601 SetOn 行含 `K57_CAP_BST_SW, K126_V1P5_CAP, -1` |
| TM601 `VBUS` 假阳性消失 | **t26** meta 覆盖 | 现 `TM601.powered_pins = ['ISW','SW','VBAT','VDRV']`（**不含 VBUS**）、`mi_pins = ['PMID_SW','SW']` |
| `cbit` KNOWN-RED 正确分类 | **t25 F1** | `gate_baseline.json` 仍 28 B `021015da…`；门禁 12 门（此前 11 门） |
| SW1/SW2 不再被点名 | 见 §4（**t26 已足够**；F2 亦正确但非必要） | 现 powered=不含 SW1/SW2；旧语义下 `fam_intersect` 亦为 `[]` |

## 3. K57：我按"两层写法"复核，结论与 t26 更新后的产物一致

接地树实测：TM601 `SetOn` **闭 K57**（`K57_CAP_BST_SW` 在列表内），**不闭 K44/K45/K5**。
- **规则层**：`SW` 进 `mi_pins` ⇒ `verify_relay_trace.py:325-326` 按 PIN 豁免 ⇒ **不要求**闭 K57；
- **工程层**：`BST_SW` 真被静态供电（`bst_sw`/`bst2sw` 5 V）⇒ **建议仍闭**，payload 闭着 = 正确。
两层写法已被 t26 采纳，**且已进一步细化为"逐函数"**（见 §3.1）。引用版本号以现盘 revision 为准。

### 3.1 逐函数复核（我独立复算，确认 setup-architect 的 per-function 细化成立）

> **版本引用更新（19:1x 实测）**：其产物 `meta-excitation-override.json` **现盘 = `t26-correction-6`，
> 24,424 B / `1af63a29f1e45cb38535d4ecf558d3364f8994c931cc4739e9c0c2ecbee2ccb0`**（mtime 19:06:48）。
> 本文曾依次引用过 `correction-1`（11,511 B / `238b2b6c…`）与 `correction-4`（19,157 B / `4b28d464…`），
> **均已过期；引用一律以现盘 revision 为准。**
> ⚠️ **溯源缺口（我在 artifacts 全树扫描实测）**：`correction-1..5` **没有任何历史副本留存**
> （就地覆盖）⇒ "被 rule-reviewer ACCEPT 的那一版（`correction-3`）"到现盘之间的**哈希链无法被第三方复核**。
> 已在给 Captain 与 setup-architect 的报告中建议：冻结 `meta-excitation-override.<revision>.json` +
> 维护 `revisionHistory[{revision,bytes,sha256,acceptedByReview}]`。
>
> **✅ 该建议已被 setup-architect 落地，我独立验证通过（19:13 实测）**：
> - 快照 `meta-excitation-override.t26-correction-8.json` = **26,999 B / `62f2da6f0996ee5a…380ae5ec`**，
>   与 live `meta-excitation-override.json`（同 size/hash）**逐字节一致** ⇒ "取快照未改产物"成立；
> - 审计链 `meta-excitation-override-revision-history.json` = **4,349 B / `535e4144aedb4385…79258c88`**，
>   8 条 revision（含 `correction-4`/`-7` 无复核文件、`correction-8` 待重新锚定的**如实披露**）。
> - **定级（我如实标注）**：`correction-1..7` 的 `sha256` **无法被第三方独立验证**（内容已不存在），
>   故该链为 **traceable（可追溯）而非 independently verifiable（可独立验证）**。
> - **⚠️ 我另发现的第二层同型风险（已报，未执行）**：该**审计链文件自身没有快照**（单一文件、就地覆盖）
>   ⇒ 它被改写时失败/覆盖会让整条链归零。建议改为 **append-only** 或对链文件本身也做快照。
>
> **K57 的权威表述以 t26 产物为准**（`k57Conclusion.ruleLayer` / `.engineeringLayer`、
> `k57TokenAnalysis.maskingEffect`、`.verdict`、`.ledgerRequirement`、`.withdrawals`）——
> 经我实测，上述三段已**实质覆盖**"规则层 / 实现层 / 工程层"，故本报告**不主张**再进行结构性追加。
>
> **门禁输入与声明载体的区分（重要，供 t9 引用）**：门禁读的是
> `project/DALI/meta/dali_tm_meta.json`（现 **147,520 B / `50efba4ec6c27192…`，mtime 18:52:27，未变**），
> **不是** `meta-excitation-override.json`（后者是**声明/审计载体**）。两者须靠
> `check_input_sync.py`（RS-1..RS-4）或 manifest 登记 + 重放绑定；实测
> `t26-regen-probe/dali_tm_meta.regen.json` = 146,180 B / `1c849664…` 与 **t25 前**的现盘 meta
> 逐字节同哈希 ⇒ **"重生成静默抹除修正"是可达路径**（当前无门禁会因此变红）。

其探针副本 `t26-regen-probe/verify_relay_trace.OLDfam.py` = 19542 B /
`183e33ebe0a4bf3e284606b4a96ac5e19a43292f786f71e87878705b01d425fb`（我复算一致）；
`t26-regen-probe/dali_tm_meta.regen.json` = 146180 B / `1c8496645492f7b7…` ⇒
**与 t25 前的现盘 meta 逐字节同哈希**（确认为未受 t25 污染的基线副本）。

逐 token 复算（现行 meta + 现行 `test.cpp`）：

| 函数 | powered | mi | token | `fam_intersect(powered,token)` | mi/ramp 豁免 | 已闭合 | 规则要求闭合 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TM600_HS_RDSON | `BST-SW,BST_SW,ISW,PMID,VBAT,VDRV` | `SW` | `BST_SW` | `['BST_SW']` | **False** | True | False（**仅因已闭**） |
| TM600_HS_RDSON | 同上 | `SW` | `SW_BST` | `[]` | True | True | False |
| TM601_LS_RDSON | `ISW,SW,VBAT,VDRV` | `PMID_SW,SW` | `BST_SW` | `[]` | False | True | False |
| TM601_LS_RDSON | 同上 | `PMID_SW,SW` | `SW_BST` | `['SW']` | **True** | True | False |

⇒ **其 T26-F1 细化成立**：**TM601 是"豁免中"**（`SW` 在 `mi_pins`），**TM600 不是**（其令牌 `BST_SW` 不在
`mi_pins=['SW']` 里，`fam.startswith(p)` 亦为空 ⇒ 新旧语义都不豁免），TM600 的 K57 之所以不出告警是
**payload 已闭合被 `L354` 的"已闭 ⇒ continue"掩盖** ⇒ 若日后移除该闭合，TM600 会重新出现真实告警
（`bst_sw`/`bst2sw` 5 V 真供电）。**这是数据层与规则层之外的正确第三层事实，我方原表述未区分，予以补充。
当前 `relay-trace` 明细亦与此一致：TM600/TM601 均**零告警**（K57 已闭）。

## 4. ⚠️ 我主动更正一条**验收判据**：F2 的许可判据在最终树上被元数据修复覆盖

**事实（我复算）**：在**当前**（t26 落地后）的输入上，把 `fam_intersect` 换回**我修复前的旧实现**，
结果与现在**完全相同** —— 因为 `powered_pins` 已不含 `SW1_BST1/SW2_BST2` 家族成员，
旧语义下 `fam_intersect(powered, 'SW1_BST1') = []` 亦不产生告警。

⇒ **验收条目"SCH-Connect-Map 判据下 SW 不得匹配 SW1_BST1/SW2_BST2"所要求的可观测效果，
现由 t26 的 meta 覆盖达成；我 t25 的 F2 修复对最终树的这一条不再产生可观测贡献。**

**这不是把 F2 说成无用**，而是把它放回正确的位置：
1. **F2 修复本身正确且已过独立复核**：A/B 全树（在我执行时的树态上）**只消除 2 条、新增 0**；
   穷举 5252 对"不命中→命中" **0**；评审方独立穷举 35 token 证实 **NEW 命中集恒为 OLD 子集
   ⇒ 结构性不会新增要求**。结论：**F2 不可能引入回归**。
2. **F2 消除的是"匹配语义缺陷（latent）"**：只要 powered 含 `SW` 且某电容家族 token 以数字后缀
   （`SW1_BST1`/`SW2_BST2`）或多个节点名被折进 `VAC` 家族，旧实现就会点名**未供电节点**。
   当前恰由 t26 的 `powered_pins` 收窄掩盖了它 ⇒ **若 meta 再次变化（换项目/换 run），
   该缺陷会原样复发**。F2 修的是那条**复发路径**。
3. **准确表述（供 Captain 与 downstream 引用）**：
   > t25 的 F1 是达成当前绿色门禁的**必要**修复（否则基线解析失败、`cbit` 门静默消失、exit 非 0 原因被误报）；
   > t25 的 F2 是**正确且无回归**的匹配语义修复，其可观测效果在最终树上**已被 t26 的 meta 覆盖取代**；
   > 因此"SW1/SW2 消假阳性"这一条**不应**作为 t25 的独立功劳计入验收，且**不得**据此认为
   > "t26 覆盖脚本侧修复"——两者是不同层的修复（数据层 vs 规则层）。

## 5. 纪律与边界（最终核验）

- **`gate_baseline.json` 始终未被改动**：`021015da84e6fd4c…`（28 B），与 `backups/gate_baseline.json.pret25` 同哈希。
- **`devel` 生产树未被触碰**：`test.cpp 5c9cb3f9…`、`StdAfx.h ba8ab3de…`，与 run 基线一致。
- **t25 从未编译、从未写目标树**（t25 期间 `test.cpp` 为 `3dbceb49…`；现 `15c7d2b8…` 的改动来自 payload 落盘）。
- **t25 未新增任何红**：修复前/后同一命令 exit 均 1（当时），现为 0。
- **边界声明**：本文件**无任何电性/硬件结论**。**编译成功 ≠ 电性/硬件正确**；本轮**未做 Release 编译**（归 t8）。
- 我**未**创建第二个门禁结果目录之外的产物；复核日志：`gate-logs-t25-verify/`（含 `run-gates-stdout.log` 与 12 个门禁 `.log`）。
