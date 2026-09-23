# t26 复核 · 第二次（针对 revision `t26-correction-1`）

- 复核人：rule-reviewer（独立于修改者 setup-architect）· 日期：2026-09-16
- 复核对象：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **11,511 B / python-plaintext sha256 `238b2b6c43d535c815034cdf67ea459d01efcf94aa94bc58f2c2c03d79190b10`（`t26-correction-1`，mtime 18:58:31）** —— 与申报**逐位一致** ✅
- 只读声明：本复核未修改任何被审文件。

## 结论

| 项 | 判定 |
|---|---|
| revision 产物哈希 | ✅ 逐位一致 |
| 两处主动更正的**意图**（撤回"必须移除 K57"、撤回旧 payload 归因） | ✅ 接受，方向正确 |
| **门禁最新结论** | ✅ **独立复核成立**：11 门 GREEN + `cbit` KNOWN-RED；`relay-trace` = **PASSED**；meta 覆盖 101/101；FR-001 反向仅 2 处（**均为 TM643**）；**虚构继电器名 = 0**；TM600/TM601 已无任何 finding |
| **K57 两层表述** | ⚠️ **对 TM601 正确，对 TM600 仍不准确 —— 需第三次更正（不阻塞收口）** |

---

## 1. ✅ 已独立复核成立的部分

**1.1 最新门禁（`gate-logs-t26/`，全部 18:58:14–18:58:18，晚于树写入 18:53:33 ⇒ 证据对现树有效）**
- `relay-trace.log`：`99 个函数有继电器 (结构规则 0, 功能规则 182, FR-001 反向 **2**)` → `WARNINGS:` 仅 **TM643 两条** → **`RELAY TRACE PASSED`** ✅
- 其余：`AWG PARAMS PASSED` / `BST-SW SEQUENCE PASSED` / `CHECK-TESTITEMS-META PASSED`（101/101）/ `MERGE DISCIPLINE PASSED` / `SINGLE-FN SMOKE PASSED` / `AUDIT PASSED` / `VERIFY PASSED`（path-def 275/275）/ `input-sync` 通过 / `material` PASS → **11 GREEN** ✅
- 唯一存量红 = `cbit`（KNOWN-RED，`K169/K170` 等 CBIT 定义类）✅
- **`TM600/TM601: 虚构继电器名` 已归零** —— 与我上轮"全树虚构名令牌 = 0"的只读模拟一致 ✅

**1.2 归因更正成立**
你把旧的"唯一剩余红 = 虚构 126"更正为"已消失"，与我上轮实测一致；`K126_V1P5_CAP`（`StdAfx.h:299`）是正确修法。

**1.3 撤回"必须移除 K57"成立且重要**
原 `"K57 must NOT be closed / zero-Cap-closure / payload 应移除"` 已撤回、不再要求改 `test.cpp`。这与我上轮 finding（原文会为 TM600 引入新增红）方向一致 ✅

**1.4 input-sync 戳合规**（上轮已核，本轮维持）：yaml `_sync.metaSha256` == 现盘 meta 哈希（我现算，`MATCH: True`）。

---

## 2. ⚠️ 仍需更正：K57 两层表述中的**规则层**对 **TM600** 不成立

**更正版原文**（`L193`、`L196`）：
> *"(rule layer) the FR-001 reverse check **no longer REQUIRES `K57_CAP_BST_SW` for TM600/TM601**; … `SW` is now in `mi_pins` … so `verify_relay_trace.py` **L356 exempts the SW family by PIN**"*

**实测反驳（我按现盘规则逐 token 复算）**：L356 的豁免是 `fam_intersect(mi, ptok)`，其中 **`ptok` 是被遍历到的那个电容令牌**，不是函数声明：

| 函数 | `powered_pins` 中的令牌 | `ptok` | `mi_pins` | `fam_intersect(mi, ptok)` | **规则是否要求闭 K57** |
|---|---|---|---|---|---|
| **TM600_HS_RDSON** | 含 **`BST_SW`** | **`BST_SW`** | `["SW"]` | **`∅`**（`'BST_SW'` **不以** `'SW'` 开头；旧版双向 `startswith` 已由 t25 的 token 边界匹配收紧） | **是（REQUIRES）** |
| **TM601_LS_RDSON** | 只含 `SW` | `SW_BST` | `["PMID_SW","SW"]` | `{'SW'}`（`'SW_BST'` 以 `'SW'` 开头且 `'_'` 为合法边界） | 否（豁免成立） |

⇒ **"no longer REQUIRES K57 **for TM600/TM601**" 对 TM600 是错的**；正确表述是 **"TM601 豁免；TM600 仍被规则要求"**。

**为什么门禁没暴露**：现盘 `test.cpp:9081` 的 TM600 SetOn **仍然包含 `K57_CAP_BST_SW`** ⇒ 规则在 `L354`("已闭其 Cap → continue") **先行跳过**，`L356` 根本不会被求值。**门禁绿是"被已闭合掩盖"，不是"被豁免"。** 我用只读模拟确认：若删除该闭合项且其它不变，TM600 将产生 `静态供电 BST_SW 但未闭稳压电容 K57_CAP_BST_SW`。

**`L203` 的归一化表述具有误导性（需补正）**：`'SW_BST'` 与 `'BST_SW'` 经 `canon_by_ch[57]` 归一为**同一继电器**——此点正确；但它们**在 `cap_defs` 中是两个不同 token 条目，各自独立做豁免判定**，因此"门禁上一直是同一条 finding"只说对了一半，且**不能**据此推出"两个令牌的豁免等价"。**豁免是按 token，不是按继电器。**

**影响（为什么值得改）**：该表述会制造 **t22 与 t26 的表面冲突**——t22 裁定 K57"**规则要求闭合**"，而更正版称"规则层不再要求、仅为工程建议"。二者**结论相同（都保留 K57）但理由相反**。若后人按"仅为工程建议"做最小端点清理删除 K57，**会给 TM600 引入 1 条新增红**。文档理由必须正确，否则结论会在下一次修订中被推翻。

**要求更正（结构化 finding）**
| 字段 | 内容 |
|---|---|
| id | T26-F1 |
| severity | medium |
| file | `team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json` |
| line | 193（`k57Conclusion.verdict`）与 196（`why[0]`）、203（`relayNormalisation`） |
| problem | 规则层声称"no longer REQUIRES K57 **for TM600/TM601**"，实测对 TM600 不成立：TM600 的 `ptok` 是 `BST_SW`，不在其 `mi_pins=["SW"]` 中，`fam_intersect` 返回空 ⇒ 规则仍要求闭 K57；门禁为绿仅因 payload 已闭合该继电器而被 L354 跳过。另 `relayNormalisation` 把"同一继电器"误推为"同一豁免"。 |
| requiredFix | 改为：**"规则层：TM601 的 `SW_BST` 令牌被 `mi_pins=['PMID_SW','SW']` 豁免 ⇒ 不再要求；TM600 的 `BST_SW` 令牌**不被**豁免 ⇒ 规则**仍要求**闭合 `K57_CAP_BST_SW`（现 payload 已闭合，正确）。因此 K57 对 TM600 是规则要求、对 TM601 才是工程建议。"** 并补一句"豁免按 token 生效，不按继电器；`SW_BST`/`BST_SW` 虽同归一为 K57，但豁免判定各自独立"。 |

---

## 3. 交付

- **meta/model 覆盖本体：ACCEPT（可签收）** —— 哈希可核、run 作用域干净（仅两项变化）、激励对齐 rev24/BD-08、`VBUS` 移除正确、input-sync 戳合规、生成器未动、**门禁 11 GREEN + cbit KNOWN-RED、TM600/TM601 零 finding**。
- **T26-F1（medium）**：K57 规则层表述对 TM600 需更正。**不阻塞 t26 收口与门禁结论**，但**阻塞**"把 K57 当纯工程建议/可移除"的任何后续动作。
- **t24 的 payload 结论不变**：TM601 可零电容；**TM600 必须保留 `K57_CAP_BST_SW`**（与我 t22 裁定一致）。

**UNKNOWN（未测，不声称）**：我未执行 `gen_testitems_meta.py`，"重生成是否覆盖本次 override"仍未验证（上轮 R-3）。
