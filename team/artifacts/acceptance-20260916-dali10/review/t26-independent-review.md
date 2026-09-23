# t26 独立复核意见（run 作用域 meta/model 覆盖）

- 复核人：rule-reviewer（**修改者为 setup-architect，非本人；本复核独立**）· 日期：2026-09-16
- 请求方：setup-architect（t26）
- **只读声明**：本复核未修改任何被审文件。取证：python 明文 / grep 工具；哈希 python-plaintext 现算。
- **结论：meta/model 覆盖本身 ACCEPT（干净、run 作用域、零新增红）；但 K57 结论有 1 处实质错误，边界② 已失效（非 blocker）。**

---

## 0. 哈希复核：三项申报值**逐位一致** ✅

| 文件 | 申报 | 我现算 | 判定 |
|---|---|---|---|
| `meta-excitation-override.json` | 9,937 B / `16614e98…c353ea` | 9,937 B / `16614e98c379124dd12d57fccd733921f3a11b4f792010530f28fb6316c353ea` | ✅ |
| `project/DALI/meta/dali_tm_meta.json` | 147,520 B / `50efba4e…4b1f42` | 147,520 B / `50efba4ec6c271923c5f956b9c2a9f2f19173f7c0900a24ce0ec2ac3704b1f42` | ✅（前值 `1c849664…` / 146,180 B 与申报的 before 一致） |
| `project/DALI/meta/test_conditions.yaml` | 11,628 B / `c919b11d…3e238c79` | 11,628 B / `c919b11ddb6d4df2093a9c0c63ca7fe782cfb01e15cb3b2996a3f58a3e238c79` | ✅ |

**run 作用域核实（我独立比对 `.pret25` 备份）**：101 → 101 函数，**逐函数比对仅 `TM600_HS_RDSON` 与 `TM601_LS_RDSON` 两个条目发生变化**，其余 99 个字节级不变 ✅ ⇒ "只动两条目、未动生成器、未动其它 run"**成立**。

**⚠️ 但请注意一个客观事实（影响边界②）**：`ForCodexDebug/source/test.cpp` **已在 t26 之后被写入**——现盘 **469,714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**（mtime **18:53:33**），而 t26 的门禁日志写于 **18:53:16**。即：**t26 的门禁证据评估的是写入前的旧树**，其 `relayTraceFindingsAfter` 中那两条 `虚构继电器名 126` 反映的是**旧树**状态。

---

## 1. 边界②（`K126_V1P5_CAP` 被判"虚构继电器名 126"）——**非 blocker；且现树已不再发生** ✅

**我不采信"payload 缺陷"这一归因，理由如下**：

1. **该继电器名在头文件中解析正常**：`StdAfx.h:299  #define\tK126_V1P5_CAP\t126`。我**用门禁自己的正则** `#define\s+(K\d*_\w+)\s+(\d+)` 在真实文件上解析，得到 `K126_V1P5_CAP → 126`，且 491 个 define 全部解析成功 ⇒ **不存在"门禁无法解析该名字"的机制**。
2. **我按门禁自身的 `fn_blocks` + `parse_setons` + 名字真实性规则，对现盘 test.cpp 做模拟**（未改动任何文件）：
   - `TM600_HS_RDSON` SetOn = `K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` → **全部在 defines 表中**
   - `TM601_LS_RDSON` SetOn = `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` → **全部在 defines 表中**
   - **全树虚构名令牌数 = 0**
3. **因此**：t26 日志里的那两条"虚构 126"是**旧树（裸 `126`）的历史残留**，不是 `K126_V1P5_CAP` 的问题。旧树确实用**裸数字 `126`**，而门禁按名字匹配 → 必然报"虚构继电器名 126"。写入后的命名是**正确修法**（裸数字永远无法匹配 defines 表）。
⇒ **判定：② 不是 blocker，且已被落地写入消除。**建议 Captain 以现盘树重跑门禁并记录新哈希，取代 18:53:16 的旧日志。

---

## 2. 边界① 与 **K57 结论**——**有一处实质错误，必须更正** ❌（但不阻塞 t26 的 meta 部分）

t26 结论：*"TM600/TM601 不应闭合 `K57_CAP_BST_SW` …… 本项为零电容闭合"*，并要求实现者移除 payload 中的 K57。

**我按门禁规则（t25 后的实际行号）逐 token 复算，发现该结论对 TM601 成立、对 TM600 不成立**：

| 函数 | `powered_pins` | K57 的 `cap_pin` 令牌 | `mi_pins` | 该令牌是否被 `L356` 豁免（token 边界匹配） | 若**删掉 K57 闭合**会怎样 |
|---|---|---|---|---|---|
| `TM600_HS_RDSON` | `[BST-SW, BST_SW, ISW, PMID, VBAT, VDRV]` | **`BST_SW`** | `["SW"]` | **否**：`fam_intersect({'SW'}, 'BST_SW') = ∅`（`'BST_SW'` **不以** `'SW'` 开头，也不以 `'SW'` 为前缀） | **会产生新告警**：`TM600_HS_RDSON: 静态供电 BST_SW 但未闭稳压电容 K57_CAP_BST_SW` ⇒ **新增红 1** |
| `TM601_LS_RDSON` | `[ISW, SW, VBAT, VDRV]` | **`SW_BST`** | `["PMID_SW","SW"]` | **是**：`fam_intersect({'PMID_SW','SW'}, 'SW_BST') = {'SW'}`（`'SW_BST'` 以 `'SW'` 开头、后接 `'_'` 非字母数字=合法边界） | 无新告警 ⇒ **可以移除** |

**根因（t26 的推理把两个不同令牌当成同一个）**：K57 有**两个别名**——`K57_CAP_BST_SW`（token `BST_SW`）与 `K_SW_BST_Cap`（token `SW_BST`），二者 `#define` 同为 **57**、经 `cap_defs` 规范化到同一物理继电器（我在 t25 复核中已实证）。**但门禁的 `cap_pin()` 是按"被遍历到的那个 define 名"取令牌的**，而 `cap_defs` 中 **`SW_BST` 与 `BST_SW` 是两个不同的 token 条目**，分别做豁免判定。
- TM600 的 `powered_pins` 显式含 **`BST_SW`** ⇒ 走 `BST_SW` 条目 ⇒ 豁免集合 `mi_pins=["SW"]` **命不中** ⇒ **规则要求闭合 K57**。
- TM601 的 `powered_pins` 只含 **`SW`** ⇒ 走 `SW_BST` 条目 ⇒ `mi_pins` 含 `SW` **命中** ⇒ **豁免成立**。
⇒ t26 引用的 `verify_relay_trace.py L356`（=t25 后行号，即其旧编号 `:325`）**确实存在且正确**，但它**按 PIN 令牌生效**，TM600 的令牌是 `BST_SW`，**不在** `mi_pins` 中，故豁免**不适用于 TM600**。

**为什么 t26 的门禁日志没有暴露这一点**：现树 payload 的 TM600 SetOn（`test.cpp:9081`）**仍然闭着 K57**，因此 `L354` 的"已闭其 Cap → continue"先行跳过，**告警被"已闭合"掩盖**。一旦按 t26 的建议删除，掩盖解除，新红出现。

### 对 K57 的**独立裁定**
1. **TM600_HS_RDSON：K57 必须保持闭合。** 依据：(a) `BST_SW` 是显式供电轨（`hardwareInit bst_sw 5 V`；`powered_pins` 含 `BST_SW`）；(b) 规则未豁免（上表实算）；(c) 与我 **t22 裁定一致**（t22 时 `powered_pins` 亦含 `BST_SW`，结论即"应闭合"）。t26 称"TM600 不需要 K57"**与门禁实算矛盾**。
2. **TM601_LS_RDSON：K57 可以移除**（规则豁免成立）。**但这不是"必需移除"**——移除后无告警，保留亦无告警（`L354` 先跳过）。若按 t26 的"零电容闭合"目标移除，**门禁仍为绿**。
3. ⇒ **更正建议**：把"本项为零电容闭合"改为 **"TM601 可零电容闭合；TM600 必须保留 K57_CAP_BST_SW"**。若实现者按原文同时删除两处，**会为 TM600 引入 1 条新增告警**，与 t26 自己申报的"新增 0"冲突。

---

## 3. 其余复核（我独立确认）

| 项 | 实测 | 判定 |
|---|---|---|
| 激励对齐冻结 ATE（TM600 vbat 4.2/pmid 15；TM601 vbat 4.2/pmid 9/vdrv 5） | 与 `setup-contract.json` rev24（现算 `fd00a508…`）及我 t24 复核的 payload 施值一致 | ✅ |
| 删除 `vset vbus 5.0`、`powered_pins` 去 `VBUS` | 与我 t22 裁定 A2 完全一致（VBUS 非 ATE 激励；到达需 K3，本项不闭） | ✅ |
| `SW/SW1/SW2` 分节点 | t25 已把 `fam_intersect` 改为 token 边界；t26 的 meta 侧保持令牌精确（只写 `SW`）⇒ 不会被 meta 侧的前缀碰撞推翻 | ✅ |
| `input-sync` 戳刷新 | yaml `_sync.metaSha256` = `50efba4e…` **等于**现盘 meta 哈希（我现算比对 `MATCH: True`）⇒ **是"内容变更后同步戳"，不是"改门禁来遮蔽漂移"** | ✅ 合规 |
| 其它 99 函数不动 / 生成器不动 | 逐函数比对仅 2 项变化；`gen_testitems_meta.py` 未在 changedFiles 中，且我未发现其被改 | ✅ |
| `K126_V1P5_CAP` 是否会被规则要求闭合 | `cap_pin('K126_V1P5_CAP')='V1P5'`；TM600/TM601 的 `powered_pins` **均不含 `V1P5`** ⇒ 规则**不要求** K126；它当前被闭合属**冗余**（不报错，因闭环规则按 connect-map 判定）。**非 blocker**，但建议按最小端点纪律复核其必要性 | ⚠️ 低优先 |

---

## 4. 交付与风险

**ACCEPT**：t26 的 meta/model 覆盖**可以签收**——哈希可核、run 作用域干净、激励与 BD-08/rev24 对齐、`VBUS` 移除正确、input-sync 戳刷新合规、其它 99 函数零改动、生成器未动、零新增红（前提是 TM600 保留 K57）。

**必须更正项（不阻塞 t26 收口，但阻塞"按原建议删除 K57"这一动作）**
- **R-1（medium）**：K57 结论须改为"TM600 保留 / TM601 可选移除"；若按原文删除 TM600 的 K57，将新增 1 条 FR-001 告警，违反"新增 0"。
- **R-2（medium，流程）**：t26 的门禁证据（18:53:16）早于树写入（18:53:33），其 `relayTraceFindingsAfter` 与"仅剩红=虚构 126"的表述**对现树已失效**。请以现盘 `test.cpp 15c7d2b8…` 重跑门禁并归档，作为 t8 的前置证据。
- **R-3（low）**：`meta_excitation` 覆盖是**手改 run 级 meta**（非生成器产出）。已可见风险：下次重跑 `gen_testitems_meta.py` 会**覆盖**本次覆盖。建议在 override 中明确"重生成后须重新施加"，并在 input-sync 处保留可检测性（现仅 `metaSha256`，不含"覆盖是否仍生效"的语义）。
- **R-4（low，归属）**：边界①（payload 仍闭 K57/K126）与②（裸 126 历史）**均属实现者/Captain 的写入范围**，t26 未越权，处置正确。

**明确非 blocker**：**边界②不是 blocker**（我按门禁规则在现树上模拟：TM600/TM601 SetOn 全名可解析，全树虚构名令牌 = 0）。**边界①中"移除 K57"对 TM600 应取消**（见 R-1）。

**未验证/UNKNOWN**：我未执行 `gen_testitems_meta.py`，故"重生成是否覆盖本次覆盖"为**未验证**（R-3 所述），未声称已实测。
