# t25 独立复核意见（评审方无改动权 · 只出判定）

- 复核人：rule-reviewer · 日期：2026-09-16 · run `acceptance-20260916-dali10`
- 请求方：compile-diagnostician（t25）
- **只读声明**：本复核**未修改任何文件**（含被审脚本、日志、meta、证据产物）。所有结论来自 python 明文读取 + grep 工具。
- 取证纪律：哈希一律 **python-plaintext sha256**；内容断言只用 **python / grep 工具**；**未使用 pwsh 做任何源码文本判断**。

## 0. 被审对象哈希：全部与请求方申报值一致 ✅

| 文件 | size | python-plaintext sha256 | 判定 |
|---|---|---|---|
| `scripts/run_gates.ps1`（改后） | 9763 | `dd2a4337f22d339a4a0f866c43d1843413db8f1d9e726c07bf8fbcaa5ab310b9` | ✅ 一致 |
| `scripts/run_gates.ps1.pret25`（改前备份） | 7660 | `91b3fcfcd80273934dc48197c47fce491b755d4f01af5045488ded317b242043` | ✅ 一致 |
| `scripts/verify_relay_trace.py`（改后） | 21068 | `65e0c67f827bf4ff6e6d1b3a45bf3b76058815f8d4df501b19a3271f06410f9c` | ✅ 一致 |
| `verify_relay_trace.py.pret25` | 19507 | `18654b3ccddad9a929fa277a9ba9876091f5741126304c29df8bc1310be0061d` | ✅ 一致 |
| `gate_baseline.json`（**判据文件**） | 28 | `021015da84e6fd4c54a595796e1bad73e18c57db94f856871d5667044302cb1d` | ✅ **未改动**；与 `gate_baseline.json.pret25` **同哈希** |
| `dali_tm_meta.json.pret25` | 146180 | `1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693` | ✅ 与我 t22 取证时刻**同哈希** ⇒ meta 未被 t25 改动 |
| `run_gates.ps1` 完整性 | — | BOM `ef bb bf` 保持；**CRLF=0 / bare LF=181** ⇒ **LF 保持** | ✅ 与申报一致 |

---

## 1. F1（基线读取改经 python 授权读者）—— **ACCEPT** ✅

**独立核对结论：`cbit` 是正确的 `KNOWN-RED`，且结论并非靠"改判据"取得。**

1. **基线明文正确**：`gate_baseline.json` 实读 28 B，`021015da84e6fd4c…`，内容 `\xef\xbb\xbf{\r\n    "cbit":  true\r\n}\r\n` ⇒ `{"cbit": true}`。python 明文 **28 B** vs 申报的 pwsh 密文 **8192 B**，与 DLP 透明白名单现象吻合。
2. **判据文件内容未被改动**：`gate_baseline.json` 现盘哈希 == `.pret25` 备份哈希 == `021015da…`。**我未发现"改基线内容"的任何痕迹**。
3. **修法性质正确**：`run_gates.ps1:50-57` 新增 `Read-JsonViaPython`：`python -c 'json.load(open(p,encoding="utf-8-sig")) → json.dumps(ensure_ascii=True)'` → `ConvertFrom-Json`。**只替换读取通道，未改任何判定逻辑**（`L49` 注释亦如此声明）。同一函数还修好了 `project_config.json` 的读取（`L64-68`），这正是 `$stdafx` 为空、`cbit` 门被静默跳过的原因 ⇒ 12 门（修复前 11 门）与"cbit 门缺失"的叙事自洽。
4. **未发现放宽判据的旁路**：`L55` 在 `$LASTEXITCODE -ne 0` 或空输出时返回 `$null`（fail-closed 而非 fail-open）；`L69` 读不到时打印 WARN 并跳过该门——**注意这是"跳过"而非"变绿"**：门数从 11→12 说明 cbit 门这次**真的跑了**并报 KNOWN-RED，而非被跳过。方向正确。

**唯一提请留存的口径**：`L69` 的"读不到 → 跳过门"路径若在将来触发，会让门**消失**而不是**变红**。建议（非阻塞）把它升级为显式失败或至少计入 NEW-RED 分类器，避免"门静默消失"这一历史缺陷换形态复发。

---

## 2. F2（`fam_intersect` 改对称 token 边界）—— **ACCEPT**，并用**独立方式**复核了 A/B 可信度 ✅

**我未复用其矩阵脚本**，而是自行实现 OLD/NEW 两版语义做对照，结论与其申报一致且更强：

### 2.1 单调性（这是 A/B 可信度的关键前提）
对**全部 35 个 token** 穷举：**NEW 的命中集恒为 OLD 的子集**（`NEW not-subset-of-OLD: 0`），**新增命中 0**。
⇒ **新匹配器在数学上只能删除命中，永不可能新增**。故"新增告警 0"**不是经验巧合，而是结构保证**；其 5252 对矩阵中"不命中→命中 0 对"与我的结论一致，可信。

### 2.2 实际消去的家族（我实测）
| fam | 由 OLD 命中、NEW 不再命中 |
|---|---|
| `SW` | `SW1`、`SW1_BST1`、`SW2_BST2` |
| `VAC` | `VAC1`、`VAC2`、`VAC3` |
| `VAC1`/`VAC2`/`VAC3` | `VAC` |
（其余 `BST_SW`/`PMID`/`ISW`/`VBUS`/`VBAT` 等无变化）

### 2.3 对 TM601 的净效果（我实测，与门禁日志对齐）
`powered_pins = [ISW, SW, VBAT, VBUS, VDRV]`、`mi_pins=[]`、`ramp_pins=[]`：
- `SW1_BST1` → **要求消失**（`K45_Cap_SW1_BST1`）
- `SW2_BST2` → **要求消失**（`K44_Cap_SW2_BST2`）
- `SW_BST` → 仍命中（`K57_CAP_BST_SW`，因 `'SW_BST'` 含 token 边界）
- `VBAT` → 仍命中（`K13_VBAT_Cap`）；`VBUS` → 仍命中（`K5_VBUS_Cap`）
⇒ 恰为申报的"只消 2 条"。且 `gate-logs-t25/relay-trace-after-f2.log` 实测 **6 条告警**（TM643×2 + TM601×2 + 2 条 `虚构继电器名 126` ERROR）。**我独立预测的修复前告警数亦为 6**（按 L310-328 逐函数复算），**两处互证**。

### 2.4 `K57` 的语义在修复后不变（重要）
`K57_CAP_BST_SW` 的 token 是 `BST_SW`，它**从来不是**靠 `SW` 前缀命中的，而是靠 `'BST_SW'` 与家族 `SW` 的**尾部 token 边界**命中；修复后**仍然命中**。⇒ §H 的 F2 修复**没有**动摇"K57 应当闭合"这一 t22 裁定（与我在 t22 的判定一致）。请求方称"修复后不再被 `SW` 触发"——**措辞需更正**：它不再被 `SW` *前缀* 触发，但**仍被 `BST_SW` 命中而要求闭合**；`relay-trace-after-f2.log` 中 `TM601_LS_RDSON … K57_CAP_BST_SW` 告警仍在，正是证据。

---

## 3. 两条残留风险裁定

### R1（VAC 家族折叠、14/24 条 `K21_VAC_Cap` 需求消失）—— **ACCEPT，且我实测证据比申报更强** ✅

- **我独立复算**：`VAC` 家族消失的命中为 `VAC1/VAC2/VAC3`；反向（家族 `VAC1` 等命中 `VAC`）也消失。
- **申报称"14 条"**；我按 24 函数（24 个声明 VAC* 的函数中 `VAC` 家族与 `VAC1/2/3` 的产物）逐条核算得到的**候选面更大**：**共 28 条 (function, token) 变化行**，涉及 **`K21_VAC_Cap` 的 24 个函数** + `K45/K44` 各 2 个函数。
- **关键安全问题（"这些需求在修复前后是否真的都不出现"）我实测证实**：
  - 声明 `VAC` 于 `powered_pins` 的函数共 **30 个**：其中 **20 个已闭合 `K21_VAC_Cap`**，**10 个命中 mi/ramp 豁免**，**两者之外的 0 个** ⇒ **修复前也从未产生 VAC 告警**（我按 L310-328 顺序复算，修复前告警总数 6，其中 **VAC = 0**）。
  ⇒ **该折叠是"latent（从未点亮）"，不可能造成任何回归**。申报结论正确。
- **工程判断（我给的独立意见）**：**无法也不应要求"VAC 裸族电容"**——因为 `StdAfx.h` 里**根本不存在 token 为裸 `VAC` 的 Cap define**（只有 `K21_VAC_Cap`→`VAC`、`K_VAC1_Cap`→`VAC1` 等）。旧行为把 `VAC1` 折进 `VAC` 是**前缀伪影**，不是"要求 VAC 轨电容"的真实语义。
- **但 v22 式折叠也有代价（须登记的下限）**：`VAC`、`VAC1`、`VAC2`、`VAC3` 经 `cap_defs` **规范化到同一物理继电器 `K21_VAC_Cap`（#define = 21）**；我实测 **24 个函数**在"供电 VAC1/VAC2/VAC3 的同时闭合 `K21_VAC_Cap`**。⇒ 在**同一物理继电器**的意义上，三者的折叠是**正确**的。
- **我给出的边界建议**：折叠**仅**在"命名别名 → 同一物理继电器"成立时安全（本项成立：`K57_CAP_BST_SW` 与 `K_SW_BST_Cap` 皆 = 57；`K_VAC1_Cap` 与 `K21_VAC_Cap` 皆 = 21）。**将来若出现"同名前缀但不同物理继电器"的 PI N**（例如 `SW` 与 `SW1` 是不同节点），token 边界规则**天然正确**；若出现"不同名但同一继电器"，规则**仍靠 cap_defs 规范化兜底**（本次即如此）。⇒ **建议把"token 边界 + 别名规范化"两件事实一起写入规则注释**（该修复的 docstring 已部分做到），以免后人误以为修复"降低了要求"。

### R2（`K_SW_BST_Cap` 与 `K57_CAP_BST_SW` 是否同一物理继电器）—— **我独立实证：是同一继电器** ✅

只读取证（python 明文 `StdAfx.h` + 复现 gate 的 `cap_defs` 规范化 L273-286）：

| define 名 | 号 | `cap_pin()` token | 规范化后 `cap_defs[token]` |
|---|---|---|---|
| `K_SW_BST_Cap` | **57** | `SW_BST` | `K57_CAP_BST_SW`（经 `canon_by_ch`，通道 57） |
| `K57_CAP_BST_SW` | **57** | `BST_SW` | `K57_CAP_BST_SW` |

⇒ **同号 57、同一物理继电器、同一权威名** ⇒ **`K_SW_BST_Cap` 与 `K57_CAP_BST_SW` 是同一继电器**（"查证"完成，不再是 UNKNOWN）。
⇒ **含义**：修复后 `SW_BST` 不再被家族 `SW` 命中（`'SW_BST'.startswith('SW')` 后接 `_`，按**反向**边界本应命中——见下方发现 F-1），而 `BST_SW` 仍命中 ⇒ **净效果是"同一个继电器仍被要求闭合"**，只是命中的 token 从 `SW_BST` 变成 `BST_SW`。**功能上无损失**。

#### ⚠️ F-1（low–medium，非阻塞）：请求方一处**表述与实测不符**
新 `fam_intersect` 的两个分支（`L79-83` 正向 `p.startswith(fam)`、`L85-88` 反向 `fam.startswith(p)`）均为"token 边界"判定，**逻辑本身正确且对称**：
- `fam='SW'`、`p='SW_BST'`：正向分支命中——`p` 中 `fam` 之后是 `'_'`（非字母数字）= 合法边界 ⇒ **命中**。
- `fam='SW'`、`p='SW1_BST1'`：正向分支的下一字符是 `'1'`（字母数字）⇒ **不命中**；且因 `p` 不以 `'SW1_BST1'` 为 `fam` 前缀，反向分支也不触发。
我的穷举实测结论：`fam='SW'` 时**消失的仅为** `['SW1','SW1_BST1','SW2_BST2']`，**`SW_BST` 不在消失列表** ⇒ **`SW_BST` 仍被 `SW` 命中**。
⇒ 请求方"`K_SW_BST_Cap` 修复后不再被 `SW` 触发"**与实测不符**：它**仍被 `SW` 命中**，真正消失的是 `SW1_BST1`/`SW2_BST2` 一类。
**影响**：因两者已由 `cap_defs` 规范化为**同一继电器**（见 R2），该表述差异**不改变任何结论**；但**文档须更正**，否则后人可能据错误表述去"修"一个本已正确的分支。

---

## 4. F3（VBUS）反证 —— **ACCEPT：根因确为 meta `powered_pins` 的 `VBUS`；`BUSH0_AMUX` 不是根因**（我独立证实） ✅

1. **根因恒定**：`VBUS` 作为**单独 token 精确出现**在 `TM601_LS_RDSON.capAuthority.powered_pins`（verbatim: `["ISW","SW","VBAT","VBUS","VDRV"]`）。因 `p == fam` 在所有匹配语义（含我的 V3 精确语义）下**恒命中**，故 `K5_VBUS_Cap` 要求**在任何匹配语义下都必然产生** ⇒ **代码侧无法消除**。结论成立。
2. **`BUSH0_AMUX` 不是根因**（我独立复算）：
   - `old_fam(['K154_BUSH0_AMUX'],'VBUS') = []`、`new_fam(...) = []` ⇒ **与 VBUS 家族毫无交集**；
   - `powered_pins` 中**含 `BUSH0` 的 token 数 = 0**；
   - 规则不读 `#define`、不读 Cap 附件、不读 `SCH-Connect-Map`（`verify_relay_trace.py:313-316` 只取 `capAuthority`）。
   ⇒ 请求方对该任务书表述的更正**成立**。
3. **沙箱提案证据充分性（我独立核对）**：`sandbox-f3/dali_tm_meta.t25proposal.json` 与现盘 meta 逐函数比对：**仅 1 处差异**（`TM601_LS_RDSON.capAuthority.powered_pins` 去掉 `VBUS`），**函数数 101 == 101**，无 `hardwareInit` 改动。其 A/B 结果为"消除 1 条（TM601 的 `K5_VBUS_Cap`）/新增 0 条"，与"差异仅此一处 + 其余函数输入不变"**逻辑自洽** ⇒ **证据充分**。
4. **是否越权**：**不越权**。提案是 (a) **沙箱副本**、(b) **未落地**、(c) 明确需 Captain 授权，且 `project/DALI/meta/` 不在 t25 inScope。**这是正确的分权处置**。
   - **但请注意**：该提案**与 t26（我已提交的 t22 建议 A2）重复**。t26 是"run 作用域 meta/model 覆盖：…修正 mi_pins + SW/SW1/SW2 分节点 + 明确 K57 结论"。**建议由 Captain 合并为单一 meta 覆盖动作**，避免两个任务同时改同一文件造成冲突（见 §6 风险 R-1）。
   - ⚠️ **另请注意**：即使落地本提案，`TM601_LS_RDSON` 仍会保留 **`K57_CAP_BST_SW`** 告警（因 `BST_SW` 真实供电 + 该函数未闭 K57）。这不是缺陷，而是**正确的真红**（与我在 t22 的裁定一致）：应由实现侧（t23 payload 落盘）闭合 K57 解决。

---

## 5. 门禁现状复核 —— **与申报一致** ✅

`run-gates-stdout.log` 实测：**12 门**（修复前 11 门）；`relay-trace` = **NEW-RED**（exit=1）、`cbit` = **KNOWN-RED**；其余 10 门 GREEN；总计 **exit=1**。
`relay-trace.log` 实测 **6 条**：TM643 的 2 条（`K57`/`K5_VBUS_Cap`）+ TM601 的 2 条（`K57`/`K5_VBUS_Cap`）+ **2 条 `虚构继电器名 126` ERROR**。
- **2 条裸 `126` 属修复前既存红**：部署态 `test.cpp` = 462848 B / `3dbceb49…`，其 `TM600_HS_RDSON`/`TM601_LS_RDSON` 的 `cbite.SetOn` 仍含裸 `126`（t23 payload 修订版已改 `K126_V1P5_CAP`，但**尚未落盘**）⇒ 该 2 条 ERROR **是当前 FAIL 的直接原因**，与 F1/F2 修复无关。✅ 归属正确。

---

## 6. 结论与残留风险

| 复核项 | 判定 |
|---|---|
| F1 基线读取经 python + 基线与判据未改 | **ACCEPT** ✅ |
| F2 token 边界 + A/B"消 2 条、增 0 条" | **ACCEPT** ✅（且我用**单调性证明**独立证实"增 0"是结构保证） |
| R1 VAC 折叠 | **ACCEPT** ✅（实测：30 个 VAC 函数中 20 已闭 + 10 豁免，**0 个会告警**；建议补齐注释而非改规则） |
| R2 `K_SW_BST_Cap` ≡ `K57_CAP_BST_SW` | **实证同一继电器（#define 均 57）** ✅；但请更正"不再被 SW 触发"的表述（见 F-1） |
| F3 根因 = meta 的 VBUS；沙箱提案 | **ACCEPT** ✅；提案证据充分、不越权，但**与 t26 重复，请合并** |
| 门禁 12 门 / NEW-RED / KNOWN-RED | **与实测一致** ✅ |

**非阻塞 finding（建议登记，不阻塞 t25 收口）**
- **F-1（low–medium）**：`verify_relay_trace.py` 新 docstring/结论中"`K_SW_BST_Cap` 修复后不再被 `SW` 触发"与实测不符（`SW_BST` 仍被 `SW` 命中；消失的是 `SW1`/`SW1_BST1`/`SW2_BST2`）。结论不受影响（同一继电器），但**文档须更正**，否则后人可能据此误改规则。
- **F-2（low）**：`run_gates.ps1:69` 的"读不到配置 → 跳过 cbit 门"属 **fail-open**（门会**消失**而非**变红**）。建议纳入 NEW-RED 分类器或改为显式失败，防止"门静默消失"以新形态复发。
- **F-3（流程，medium）**：F3 沙箱提案与 **t26** 触及同一文件/同一字段，**存在并发写冲突与结论不一致风险**。建议 Captain 指定**单一 owner** 执行 meta 覆盖，另一任务改为消费其结果。

**我不 reject 该沙箱提案**：其证据充分、作用面恰为 1 条告警、0 新增、不越权；**唯一要求是与 t26 合并后再落地**。

**只读证明**：本复核对上述 7 个被审对象**未做任何写入**；其哈希见 §0 与请求方申报一致（我复算所得的 `verify_relay_trace.py`、`run_gates.ps1`、`gate_baseline.json` 值即为现盘实读值，若后续被改动即与我申报值不符，可据此追责）。