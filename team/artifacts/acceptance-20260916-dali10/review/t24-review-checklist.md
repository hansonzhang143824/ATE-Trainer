# t24 审查清单（用户紧急评审裁定 · 逐项实测基线）

- 审查人：rule-reviewer · 日期：2026-09-16 · run `acceptance-20260916-dali10`
- **状态：t24（deps: t23）尚未 claim** —— t23 未完成，按协议不抢跑。本文是**预备清单 + 已实测基线**。
- **审查对象**：t23 强制修正令之后的 payload 修订版。**当前 payload `620d99ea…` 已被 Captain/用户标记未批准、不得落盘**；盘上现存为 `73995983…`（18:36:18）——两者**都不是**将被审查的最终版。
- 分权：**只出判定、不改被审产物**（以哈希前后一致证明）。

> ⚠️ **本文中所有对当前 payload 的引用 = `implementation-payload-TM600-TM601.cpp`
> 32969 B / python-plaintext sha256 `7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b` / mtime 18:36:18。**
> 审查前必重算哈希；若已变，本文的"已实测基线"段落即失效，须对**新版**重做。

---

## 0. 已独立核对的 locator（清单要求）

| 清单所引 | 实测结果 | 判定 |
|---|---|---|
| `source/Test_Method.h:32` = `ERROR_RES 9999` | **成立**：`Test_Method.h:32  #define ERROR_RES	9999`（另有 `:18` 变更记录 "Reset ERROR_RES to 9999"） | ✅ locator 正确 |
| 先例 `debug/source/test.cpp:8087-8090` | **成立**：`8087 if (im3[site] - im1[site] > 1e-6)` / `8088 gain = (vcs3-vcs1)/(im3-im1)*1e3;` / `8089 else` / `8090 gain[site] = ERROR_RES;` ⇒ **项目既有编码 = 无电流时写 `ERROR_RES`**，且该处**先** `FPVI0.Set(FI,0,…)` 再判定（`:8083`） | ✅ locator 正确 |

---

## 1. 逐项检查表（清单 1–7）与当前 payload 的实测状态

| # | 要求 | 当前 payload 实测 | 预判 |
|---|---|---|---|
| 1 | 阻值必须**正幅值**；**不得把正电阻输出为负**；不得以负数作 "expected magnitude" | `L278 v_meas = GetMeasResult(MVRET)` 保持**带符号**；`L280 hs_rdson = (i>0.1)? (v_meas/i_meas*1e3) : 0.0`；`L429` 同理（TM601）。注释 `L270-272`/`L421-423` 明写 "**negative RDSON is the expected magnitude**" | ❌ **将违反** |
| 2 | 同号 ⇒ `MVRET/MIRET`（或 `fabs/fabs`）；**异号必须走独立极性/夹具异常上报** | 仅有**注释**暗示（`L272`/`L423` "a POSITIVE one is the polarity/fixture diagnostic"），**代码中无任何** MVRET/MIRET 同号判定、无独立异常上报分支、无失败码通道 | ❌ **未实现**（缺功能） |
| 3 | `\|I\| ≤ 门限` 必须 **fail-closed**：**先清零/下电再记失败码**，用 **`ERROR_RES`**；不得返回 `0.0 mΩ` | `L280`/`L429` 在 `i_meas ≤ 0.1` 时返回 **`0.0`** ⇒ 与"超低阻合格"不可区分；`ERROR_RES` 在 payload 中出现 **0 次**。注：清零**顺序**本身是正确的（TM600 `L267 Set(FI,0)` → `L278-280` 判定；TM601 `L418` → `L427-429`） | ❌ **将违反**（清单所指 L280/L409 位置对应现版 L280/L429） |
| 4 | cleanup 不跳过；R-POFF 顺序（**FPVI0 最后释放**） | **当前版本通过**：TM600（L177-326）与 TM601（L327-453）各自**仅一处 `return`，均在函数末尾**（`L313`/`L452` `return 0;`），无 `goto`、无中途 `break` 跳出；清理段 TM600 `L301-306`、TM601 `L441-445` 均为 `..._RELAY_OFF` 且 **FPVI0 最后**（TM600 `L306`、TM601 `L445`）。**函数级失败返回本身不存在**（两项都恒 `return 0`）→ 若改 fail-closed 需同时引入失败码返回，须重新枚举路径 | ✅ 现值通过（**改动后须重查**） |
| 5 | 量程 ≥2×：完整配对表（15→30、**10→20**、9→20、5→10、4.2→10、ACM 10→20）；0 V 不受约束 | 实测：15→`FXVIe_PLUS_30V`(L232)✅；9→`FXVIe_PLUS_20V`(L381)✅；5→`10V`(L222/290)✅；4.2→`10V`✅；ACM 5→`ACM200_10V`(L220/292/379)、ACM 10→`ACM200_20V`(L225/**L288**)✅；0 V→最小档✅。**但 `PMID_HG2_FXVI` 10 V 台阶（上 `L227`、回落 `L286`）仍为 `FXVIe_PLUS_10V`** ⇒ 不满足 ≥2× | ❌ **将违反**（两处） |
| 6 | `TM600_HS_RDSON` 段内不得出现 TM601 的 −1 A/negative 表述 | TM600 段 = `L177-326`。其中 `L270-272` 含 **"with the derived -1 A command on TM601 … expected differential is negative"** ⇒ TM600 段内**仍在讲 TM601 的 −1 A** | ❌ **将违反** |
| 7 | F2 电容按 **t22 裁定**：t22 判不适用者必须**未**闭合；另核对 K126 命名与 F3–F7 | 当前 payload TM601 SetOn `L365` = `K154,K155,K60,K61,K13,K85,K57,K126_V1P5_CAP` ⇒ **K5/K44/K45 未闭合（符合 t22 裁定）**；K126 用 `K126_V1P5_CAP`（非裸 126）✅。TM600 SetOn `L201` 含 `K57_CAP_BST_SW` ✅ | ✅ 现值通过（**待 t23 后复算**） |

**清单第 3 项措辞与实测的对应**：清单称"此前 draft 在 L280/L409 正是如此"——现版 docket 中返回 `0.0` 的确切位置为 **`L280`（TM600）与 `L429`（TM601）**；`L409` 现为注释行（"if the driven device is wrong, flip the sign FOR THIS ITEM ONLY"），**清单的 L409 在现版已漂移**，应从 `hs_rdson/ls_rdson` 赋值行定位。

---

## 2. 我方独立补充的发现（清单未列，但同属签署前提）

- **T24-A（缺功能，与第 2 项同源）**：TM601 强制 **−1 A**（`L411`），MVRET 保持带符号（`L427`）⇒ 期望 $v\_meas$ 为负、`v_meas/i_meas` 为负。代码不仅把它当"expected magnitude"，**也没有任何**异号检测与独立上报；同一 `0.0` 兜底还会把"夹具反向"与"无电流"**混成同一结果**。修法必须让两者可区分：无电流→`ERROR_RES`；异号→**独立极性/夹具异常上报**（清单第 2 项）。
- **T24-B（顺序/语义）**：清单第 3 项要求"**先清零/下电再记失败码**"。现版顺序已满足（`L267`/`L418` 先 `Set(FI,0)`，随后判定）；**修改时必须保持**，不得把判定挪到 FI=0 之前。
- **T24-C（函数返回通道）**：两函数当前恒 `return 0`（`L313`/`L452`），**不存在失败返回通道**。清单要求 fail-closed ⇒ 需明确"失败码如何经由返回值/结果数组上报"，并据此**重新枚举清理路径**（第 4 项）。**此点请实现者在 t23 明确说明机制**，否则我无法判定 fail-closed 是否真正生效。

---

## 3. t24 执行时的取证纪律（沿用并强化）

1. 内容/存在性一律 **grep 工具或 python 明文**；禁止 pwsh 读取源码断言。
2. 每条 finding 附 **工具 + 文件 + 行号**；哈希为 **python-plaintext sha256 + mtime**。
3. **只读**：审查前后对被审 payload 与全部被检对象算哈希并比对（BEFORE/AFTER 快照）。
4. 对**最终 payload**（非本文的 `73995983…`）重做 §1 与 §2 的逐条实测；本文仅作**同构模板**，不得直接当结论。
5. verdict 为 `needs_revision` 时附结构化 findings（id/severity/problem/requiredFix/file/line）。
