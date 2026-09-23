# t26 复核 · 第四次（短复评，revision `t26-correction-3`）

- 复核人：rule-reviewer · 日期：2026-09-16 · 范围：**仅 K57 段 + R-3 / R-4 落实**（按请求）
- 对象：`team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json`
  **17,081 B / python-plaintext sha256 `d45194221c47545e4305cad78c7f0f283db8011e3d92ad59cb11dca5f01735b7`（`t26-correction-3`，mtime 19:02:21）** —— 与申报**逐位一致** ✅
- 只读声明：未修改任何被审文件（`meta`/`yaml` 现盘哈希与 t26 完成时一致，见下）。

## 结论：**ACCEPT — T26-F1 已闭合；R-3/R-4 已落实；边界② 关闭成立** ✅

---

## 1. ✅ T26-F1（我连提两次的 medium）—— **已修复并闭合**

**新文（per-function，已消除"TM600/TM601 一刀切"）**
- `L198 verdict`：*"**PER-FUNCTION**: TM600_HS_RDSON **MUST KEEP** `K57_CAP_BST_SW` closed (both the rule layer and the engineering layer require it). TM601_LS_RDSON **is exempted** at the rule layer and may run zero-Cap-c…"*
- `L200`：*"TM600: **REQUIRED** – its powered rail token is `BST_SW`, and the exemption set (`mi_pins`) contains only `SW`, so `fam_intersect({'SW'},'BST_SW')` is empty; deleting K57 would raise a new FR-001 warning."*
- `L201`：*"TM601: **NOT REQUIRED** – …"*
- `L208-210 withdrawals`：**逐条留痕**（撤回"两者都不应闭"、撤回"两者规则层都不要求"），并注明"corrected here after rule-reviewer's token-level analysis, **which I re-derived independently**"。
- `L212 ledgerRequirement`：改为"**TM600 required (rule + engineering), TM601 exempted at the rule layer but retained**" ⇒ **我上轮指出的"台账会错记"风险已消除**。
- `L268 k57TokenAnalysis` + `L313 maskingEffect` + `L287/L308 逐格矩阵` ⇒ 与我 t26 round 2/3 的 finding **逐格一致**。

**我独立复核（用门禁自己的 `fam_intersect`）**：我从 `scripts/verify_relay_trace.py` **原样抽取该函数**执行（非自行重写），结果与申报表格**逐格吻合**：
```
fam_intersect(['SW'],'BST_SW')             = []          ✅ 与申报一致（TM600 豁免不中）
fam_intersect(['SW'],'SW_BST')             = ['SW']      ✅
fam_intersect(['PMID_SW','SW'],'SW_BST')   = ['SW']      ✅
（旁证）fam_intersect(['SW1','SW1_BST1','SW2_BST2'],'SW') = []   ✅ t25 分节点成立
```
⇒ **TM600 规则层+工程层均要求保留 K57；TM601 规则层豁免、可零电容。** 与 t22 裁定与我 t24 payload 结论**完全一致**，**表面冲突已消除**。

## 2. ✅ R-3（重生成可检测性）—— 已落实

`reapplyAfterRegeneration = true`；`inputSyncDetectability` 诚实写明**现存 input-sync 检测不到 run 级覆盖被重生成抹掉**，并给出 token/locator 级断言建议、注明门禁脚本改动属 out of scope 且已上交 Captain。
**我的独立旁证（值得写入台账）**：最新 `input-sync.log` 末行为 **`INPUT SYNC: **IN SYNC**`** —— 恰好实证"**门禁此刻是绿的，但抹掉检测仍缺失**"：若重生成发生，戳会同步刷新，input-sync 仍报 IN SYNC。⇒ 该风险**已定位、尚未解除**，登记正确。

## 3. ✅ R-4（最小端点）—— 已登记
`minimalEndpointNote` 记 `K126_V1P5_CAP`（令牌 `V1P5`）在两函数 `powered_pins` 中都不存在 ⇒ 当前闭合属冗余（不报错），建议实现者复核必要性；locator 指向 `test.cpp L9081/L9255`。**低优先、非阻塞**，登记正确。

## 4. ✅ 门禁与边界（复核请求第 3/4 项）

| 项 | 实测 | 判定 |
|---|---|---|
| 日志时序（申报 19:02:01–19:02:04） | .log mtime **19:02:00–19:02:04**，**均晚于 payload 写入 18:53:33** | ✅ 早前 18:53:16 已被取代 |
| `relay-trace` | **`RELAY TRACE PASSED`**；仅 TM643 两条 WARN；TM600/TM601 干净 | ✅ |
| `input-sync` | **IN SYNC**（见 §2 说明） | ✅ |
| `cbit` | 仍为存量 KNOWN-RED（K168/K169/K170 等 CBIT 定义类） | ✅ 与申报一致 |
| meta 内容未再改 | `dali_tm_meta.json` 147,520 B / **`50efba4e…`** 一致 | ✅ |
| yaml 未再改 | `test_conditions.yaml` 11,628 B / **`c919b11d…`** 一致 | ✅ |
| 产物自洽 | 其中同时引用 `50efba4e…` 与 `c919b11d…`，与现盘一致 | ✅ |
| 边界② | `payloadFindingNotInScope` 改为 **CLOSED（非 payload 缺陷、非 blocker）** | ✅ 与我只是读模拟结论（491 defines 全解析、全树零虚构名）一致 |

## 5. 汇总

| 项 | 状态 |
|---|---|
| **T26-F1**（K57 措辞，medium，2 次提出） | ✅ **CLOSED**（per-function 更正 + 留痕 + 双别名 token 分析 + 台账要求已改） |
| **T26-F2 / R-3**（重生成静默抹除 + 守卫缺失） | ✅ 风险**已登记并建议**；**缓解未落地**（属 out of scope）⇒ 记为**已定位、待 Captain 决定是否另派** |
| **R-4**（K126 最小端点） | ✅ 已登记（low，非阻塞） |
| **边界②** | ✅ CLOSED |
| **meta/model 覆盖本体** | ✅ **ACCEPT（签收）** |

**无新增 finding**。**t26 的 meta/model 覆盖可以签收**；唯一仍在**树上**的未决风险是 §2 的"重生成会抹掉修正且门禁检不出"，其处置权在 Captain（生成器落改或加 run 级断言）。

**t24 payload 结论不变**：**TM601 可零电容；TM600 必须保留 `K57_CAP_BST_SW`**（规则层+工程层，与 t22 一致）。
