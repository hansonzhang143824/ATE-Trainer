# t26 复核 · 第三次（revision `t26-correction-2`）

- 复核人：rule-reviewer（独立于修改者）· 日期：2026-09-16
- 对象：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **14,246 B / python-plaintext sha256 `b3dd2095e757dcd572db65e9bf706546adb484d6eab33c284ae2f73451435f46`（`t26-correction-2`，mtime 19:00:17）** —— 与申报**逐位一致** ✅
- 只读声明：未修改任何被审文件。

## 结论速览

| 新增项 | 判定 |
|---|---|
| ① `rootCause`（VBUS 精确 token，非 BUSH0_AMUX） | ✅ **ACCEPT**（与我 t22/t25 实测一致） |
| ② `regenerationBehaviour`（重跑生成器会覆盖本修正） | ✅ **ACCEPT —— 实证成立且重要**；但需登记缓解措施（见 T26-F2） |
| ③ `engineeringLayer.exemptionCaveat` | ✅ 方向正确（"gate silence ≠ 不需要"），**但**同段「规则层」措辞对 **TM600 仍不准确**（见 T26-F1，仍未修复） |
| 门禁现状（11 GREEN + cbit KNOWN-RED，relay-trace PASSED） | ✅ **ACCEPT**（我上轮已独立复核日志时序与内容） |
| meta 本体 / 边界声明 | ✅ ACCEPT |

---

## 1. ✅ ① 根因表述 —— 与我实测一致，ACCEPT

该表述（VBUS 假阳性源于 meta `powered_pins` 的**精确 token `VBUS`**，源自 `gen_testitems_meta.py:147-187` 的 OVERVIEW 派生层；**不是** `BUSH0_AMUX`）与我 t22/t25 的独立实测**逐条吻合**：
- 我实算 `fam_intersect(['K154_BUSH0_AMUX'],'VBUS') = ∅`（旧/新匹配语义皆然）；`powered_pins` 中含 `BUSH0` 的 token 数 = **0**。
- 规则只取 `capAuthority`（`verify_relay_trace.py` E1 段），不读 `#define`/不读 Cap 附件/不读 `SCH-Connect-Map`。

## 2. ✅ ② 重跑覆盖实验 —— 实证成立，且**这是我上轮标为 UNKNOWN 的问题的答案**

我独立复核探针文件 `t26-regen-probe/dali_tm_meta.regen.json`：
- **146,180 B / `1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693`** ⇒ **与"改动前"逐字节相同**（我核对：正是 t26 的 before 值）✅
- 内容回退确认：`TM600 hw pins = [vbat, pmid, bst_sw, vdrv, sw]`、`TM601 hw pins = [vbat, vdrv, vbus, pmid_sw]`（**`vset vbus` 回来了**）、两者 `mi_pins = []`、TM601 `powered_pins` 含 **`VBUS`** ⇒ **本 run 级三项修正全部会被重生成抹掉** ✅
- 同时证明**生成器是确定性的**（能逐字节复现改动前文件）✅

**意义**：这把我上轮明确标为 **UNKNOWN** 的问题"重生成是否覆盖 override"**转化为已实测的确定事实**。⇒ 该实验**必须**登记，并配缓解措施（T26-F2）。

## 3. ⚠️ ③ K57 措辞 —— `exemptionCaveat` 方向对，**但规则层表述对 TM600 仍错**（T26-F1 未修复）

`correction-2`（`L193`、`L196`、`L202`）仍写：
> *"(rule layer) the FR-001 reverse check **no longer REQUIRES K57_CAP_BST_SW for TM600/TM601**"* …
> *"the per-PIN exemption **silences the RULE for TM600/TM601**"*

**我按现盘规则 + 现盘 meta 做闭集模拟，量化了两者的差别**（判据为 `fam_intersect(mi, ptok)`，`ptok` 为**被遍历到的电容令牌**）：

| 函数 | `ptok` | `mi_pins` | 若**移除** K57 闭合 | ⇒ 规则行为 |
|---|---|---|---|---|
| **TM600_HS_RDSON** | **`BST_SW`** | `["SW"]` | **产生** `BST_SW → K57_CAP_BST_SW` 告警 | **规则要求（未豁免）** |
| **TM601_LS_RDSON** | `SW_BST` | `["PMID_SW","SW"]` | **无**告警 | **豁免成立** |

模拟实测输出：
```
TM600_HS_RDSON  if K57 closed -> NONE     if K57 removed -> [('BST_SW','K57_CAP_BST_SW')]
TM601_LS_RDSON  if K57 closed -> NONE     if K57 removed -> NONE
```
⇒ **"exempts the SW family by PIN for TM600" 不成立**：TM600 的令牌是 `BST_SW`，而 `mi_pins=["SW"]`；`'BST_SW'` **不以** `'SW'` 开头，t25 的 token 边界匹配后双向都不命中（旧版双向 `startswith` 才会命中）。
⇒ 现门禁为绿，是因为 payload **仍在闭** K57，规则在 **`L354`「已闭其 Cap → continue」先行跳过**，`L356` 根本没被求值 —— **绿是"被闭合掩盖"，不是"被豁免"**。

**T26-F1（medium，仍未修复 —— 第二次提出）**
| 字段 | 内容 |
|---|---|
| id | T26-F1 |
| severity | medium |
| file | `team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json` |
| line | **193 / 196 / 202**（`k57Conclusion.verdict` / `why[0]` / `exemptionCaveat`） |
| problem | 「规则层」把 TM600 也写成"已豁免"；实测 TM600 的 `ptok=BST_SW` 不在其 `mi_pins=["SW"]` 中，`fam_intersect` 为空 ⇒ **规则仍要求闭 K57**。门禁为绿仅因 payload 已闭合而被 L354 跳过。 |
| requiredFix | 改为：**"规则层：**TM601** 的 `SW_BST` 令牌被 `mi_pins=['PMID_SW','SW']` 豁免 ⇒ 规则不再要求；**TM600** 的 `BST_SW` 令牌**不被**豁免 ⇒ **规则仍要求**闭合 `K57_CAP_BST_SW`（现 payload 已闭合，正确）。故 K57 对 TM600 是**规则要求**、对 TM601 才是**工程建议**。"** 并补"豁免按**令牌**生效、不按继电器"。 |
| 关联风险 | `L206 ledgerRequirement` 要求 manifest 记"both layers (exempted at the rule layer…)"。若照此登记，**会把 TM600 的规则要求错记为豁免**，污染实现台账。该条须同步更正。 |

**`L204 relayNormalisation` 仍需补正**：`SW_BST`/`BST_SW` 经 `canon_by_ch[57]` 归一到**同一继电器**（正确），但它们在 `cap_defs` 中是**两个 token 条目、各自独立判豁免** ⇒ **豁免按 token，不按继电器**；不能由"同一继电器"推出"豁免等价"。

**为何必须改**：不改则 **t22 与 t26 理由互斥**（结论同、理由反），且 t26 自身已把这个理由写进 `ledgerRequirement` ⇒ 错误会**顺着台账传播到实现与后续修订**。一次措辞更正即可消除。

## 4. ✅ 其余复核（维持前两轮结论）

- **门禁**：`gate-logs-t26/` 全部 **18:58:14–18:58:18**，晚于树写入 18:53:33 ⇒ 证据有效；`relay-trace` = FR-001 反向 2、仅 TM643 两条、**PASSED**；其余 10 门 PASSED；**11 GREEN + `cbit` KNOWN-RED**；`TM600/TM601: 虚构继电器名` = **0** ✅
- **meta**：现盘仍 **147,520 B / `50efba4e…`**（与 correction-1 相同，未被本轮再改）✅
- **input-sync 戳**：合规（戳值 == 现盘 meta 哈希）✅
- **run 作用域**：仅 TM600/TM601 两项变化，生成器未动 ✅

## 5. 新增 finding：T26-F2（medium）—— 重生成会静默抹掉本修正，须登记缓解

| 字段 | 内容 |
|---|---|
| id | T26-F2 |
| severity | medium |
| file | `team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`（记录）/ `project/DALI/meta/dali_tm_meta.json`（受影响对象） |
| problem | 已实测：重跑 `gen_testitems_meta.py` 会逐字节还原"改动前"meta（`1c849664…`），**抹掉** TM600/TM601 的 `hardwareInit`/`powered_pins`/`mi_pins` 三项修正 ⇒ `K5_VBUS_Cap` 假阳性与 `K57` 相关行为**会随之下次重生成而复发**，且**当前 input-sync 无法检出"修正是否仍生效"**（只比对 `metaSha256`，修订被生成器还原后戳也会被同步刷新，仍报 PASS）。 |
| requiredFix | 在 override 与 manifest 中登记**"生成后重放（replay-after-generate）"**步骤，并加一条**可检测的守卫**：例如把"修正条目必须存在"（`TM601 powered_pins ∌ VBUS`、`TM600 mi_pins ∋ SW`）做成 input-sync 的断言项，使"被生成器抹掉"变为**可检出的失败**而非静默。生成器侧改动（把修正落进 `gen_testitems_meta.py`）属 out of scope，由 Captain 决定是否另派。 |

## 6. 交付

- **原始 meta 输出本体：ACCEPT（可签收）**。
- **两项待改**：**T26-F1**（K57 措辞对 TM600，medium，第二次提出）/ **T26-F2**（重生成抹除风险 + 守卫缺失，medium）。二者**均不阻塞 t26 门禁结论与 meta 签收**，但 **F1 阻塞**任何"K57 仅为工程建议"的后续动作，**F2 阻塞**"把本修正当作长期有效"的任何假设。
- **t24 payload 结论不变**：**TM601 可零电容；TM600 必须保留 `K57_CAP_BST_SW`**（与 t22 一致）。
- **UNKNOWN 已消除**：上轮的"重生成是否覆盖"已由本实验转为**实测事实**（是，会覆盖）。
