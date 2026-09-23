# t24 独立实现审查（替代永久悬空的旧 t6）

- 审查人：rule-reviewer（**独立于实现者，未自审**）· 日期：2026-09-16 · run `acceptance-20260916-dali10`
- 被审实现任务：**t23**（经批准的代码修复）
- 审查对象：`team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp`
  **35014 B / python-plaintext sha256 `444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c`**（UTF-8 BOM、CRLF=475、bare LF=0、NUL=0）
- 分权与只读：**只出判定、不改被审产物**（前后哈希一致，见 §6）。取证纪律：内容断言一律 **python 明文 / grep 工具**；哈希一律 **python-plaintext sha256 + 现算**。

## 结论：**verdict = pass** ✅

| 验收项 | 结果 | 关键证据（行号为被审 payload 行号） |
|---|---|---|
| t22 假阳性项确未闭合 | **PASS** | 可执行代码内 `K5_VBUS_Cap` = **0**、`K44_Cap_SW2_BST2` = **0**、`K45_Cap_SW1_BST1` = **0** |
| t22 必需项确已闭合 | **PASS** | `K57_CAP_BST_SW` = **2**（TM601 SetOn `L377`、TM600 SetOn `L203`） |
| `delay_ms(1)`×6 / `delay_ms(2)`×0 | **PASS** | 去注释后 `delay_ms(1)` = **6**（`L246/263/311/424/456/461`）；`delay_ms(2)` = **0** |
| `SetClamp(50,50)`×2 | **PASS** | `L256`（TM600）、`L414`（TM601）；去注释后恰 2 处 |
| `MeasureVI(200,5,FPVIe_MV_X10)`×2 | **PASS** | `L268`、`L429` |
| ramp 家族 0 / 裸 `126` 0 / `K126_V1P5_CAP` 就位 | **PASS** | `rampi_capv(`=**0**、`rampv_capv(`=**0**；裸 `126` = **0**；`K126_V1P5_CAP` 出现在两个 SetOn |
| 冻结口径（符号/PMID/VBAT/VBUS/2 ms） | **PASS** | 见 §3 |
| scope 纪律（TM643 零改动/不复制黄金/devel 零写入） | **PASS** | 见 §4 |
| 推断性表述已改 | **PASS** | `inert` = **0**；改为显式"settling 未分析、列 U11 上机项" |

---

## 1. t22 裁定的一致性（逐条）

| t22 判定 | 要求 | payload 实测 |
|---|---|---|
| T22-01 `K5_VBUS_Cap` **假阳性** | 不得闭合 | 可执行代码 **0** 次 ✅（仅出现在解释性文字） |
| T22-02 `K44_Cap_SW2_BST2`、`K45_Cap_SW1_BST1` **假阳性** | 不得闭合 | 均 **0** 次 ✅ |
| T22-03 `K57_CAP_BST_SW` **真红**（豁免不覆盖，BST_SW 真实供电） | 应闭合 | 已闭合 2 处 ✅ |

**TM601 SetOn（`L377`，8 项）**：`K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`
**TM600 SetOn（`L203`，7 项）**：`K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`
⇒ 与 t22 裁定**逐条一致**，且不再有"为过关而闭合未供电节点"的任何迹象。

## 2. 代码不变量（**去注释后**计数，这是关键口径）

| token | 全文出现 | **去注释后可执行** | 判定 |
|---|---|---|---|
| `delay_ms(1)` | 7（含 `L64` 注释） | **6** | ✅ 与申报 6 一致 |
| `delay_ms(2)` | 0 | **0** | ✅ |
| `SetClamp(50, 50)` | 3 | **2** | ✅ 与申报 2 一致 |
| `MeasureVI(200, 5, FPVIe_MV_X10)` | 2 | **2** | ✅ |
| `rampi_capv` / `rampv_capv` | 各 1（**均在 `L43` 注释**） | **0 / 0** | ✅ 申报 0 正确 |
| 裸 `126` | 0 | **0** | ✅ |
| `K126_V1P5_CAP` | 3 | 2 在 SetOn | ✅ 就位 |

**口径说明（我实测）**：申报的"`rampi_capv`/`rampv_capv` 0"指**可执行代码**，正确；全文计数为 1，唯一来源是 `L43` 的禁止性注释。我另行核对该项**不会破坏门禁**：`scripts/verify_bst_sw_sequence.py:100` 的收目标正则为 `\brampi_capv\s*\(`（**调用形式**），我的注释行**不匹配**该正则 ⇒ 不会被误收为 ZCD 家族目标。见 §5 的 T24-ADV-1（预防性建议）。

## 3. 与冻结口径的一致性

| 冻结要求 | 实测 locator | 判定 |
|---|---|---|
| TM600 **+1 A** | `L262 FPVI0.Set(FI, 1.0, …)  // +1 A (DFT literal)` | ✅ |
| TM601 **派生 −1 A** | `L423 FPVI0.Set(FI, -1.0, …)  // -1 A (derived)` | ✅ |
| TM600 PMID **15 V** | `L234 PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_30V, …)` | ✅ |
| TM601 PMID **9 V** | `L393 PMID_HG2_FXVI.Set(FV, 9, FXVIe_PLUS_20V, …)` | ✅ |
| **VBAT 4.2 V** | `L215`（TM600）、`L388`（TM601） | ✅ |
| **VBUS 非 ATE 激励** | `vset vbus` = **0**；`VBUS` 仅见于解释性文字 | ✅ |
| 量程 ≥2× 配对（含 10 V 台阶） | 15→`PLUS_30V`(L234)、**10→`PLUS_20V`**(L229 升 / L298 落)、5→`10V`、9→`20V`、4.2→`10V`、ACM 10→`ACM200_20V`(L227/L300)、ACM 15/20→`40V` | ✅ 全部满足 |
| **2 ms 硬上限（settle+acquisition）** | 施流 `L262`/`L423` → `delay_ms(1)` + `MeasureVI(200×5us=1ms)` → **立即** `Set(FI,0)`（`L269`/`L430`）；`delay_ms(2)` 不存在 | ✅ |

**符号与失败路径（本轮实质改进）**：全部阻值赋值只有两类 —— `fabs/fabs * 1e3`（`L289`、`L448`，注释 "positive magnitude"）或 `ERROR_RES`（`L291`、`L450`）。**不存在**产生负值、0 值或其它"看似合格"的赋值路径 ⇒ 同时满足"正幅值"与"无电流 fail-closed"。
**异号诊断**：`L288` / `L447` 以 `v_meas*i_meas > 0.0` 判同号；`L283-284` / `L441-444` 明确"异号 = polarity/fixture 故障，**永不**以负阻表达"，异号走 `ERROR_RES` 失败路径。**顺序正确**：先 `Set(FI,0)`（`L269`/`L430`）后判定与记录；与先例 `test.cpp:8087-8090` + `Test_Method.h:32 #define ERROR_RES 9999` 一致。

## 4. scope 纪律

- **TM643 等范围外代码**：payload 内 `TM643` 提及 = **0**；仅定义 `TM600_HS_RDSON`、`TM601_LS_RDSON` 两个函数 ✅
- **未复制只读黄金**：`knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp`（6106 B、`8cdb0be1…`）在 `ForCodexDebug` 与 `devel` 全树**无逐字节副本** ✅
- **`devel` 零写入**：`devel/source/test.cpp` = `5c9cb3f9…`、`StdAfx.h` = `ba8ab3de…`，与 run 基线一致 ✅
- **清理不跳过**：两函数各**仅一个 `return` 且在函数末尾**（`L325`、`L474`），无 `goto`、无中途 `break` ⇒ 无路径可跳过清理；RELAY_OFF 段先 VBAT/V1P5/PMID/SW12，再 FPVI1（TM600 `L317`），**FPVI0 最后释放**（TM600 `L318`、TM601 `L467`）✅

## 5. 非阻塞 advisory（不改变 pass）

| id | 级别 | 内容 | locator |
|---|---|---|---|
| **T24-ADV-1** | low（预防性） | 禁止项的**裸词**仍出现在 `L43` 注释（`test_method.rampi_capv / rampv_capv`）。可执行计数确为 0，且当前门禁正则 `\brampi_capv\s*\(` 不匹配裸词 ⇒ 不破坏门禁；但若将来有扫描器按**裸 token** 匹配，会误收目标。建议改写措辞（如"rampi/rampv_capv 家族"） | payload `L43`；`verify_bst_sw_sequence.py:100` |
| **T24-ADV-2** | low | **任务书引用的 `setup-contract.json` 哈希已陈旧**：任务写 rev22 = `295d483a…`，我现算为 **`fd00a5082170293f…`（328805 B）**。以现算为准 | `setup-contract.json` |
| **T24-ADV-3** | low | 同号判据以乘法表达（`v*i > 0.0`）：行为正确且此量级不会溢出，但安全相关的极性判据写成显式同号表达式更清晰；另建议比较链写为 `fabs(i_meas) > 0.1 && v*i > 0.0`（现写法用**带符号** `i_meas` 与它刚参与符号判定的同一表达式作比较，是易读性上的隐患，非缺陷） | `L288`、`L447` |
| **T24-ADV-4** | medium（交接） | **manifest 哈希在交接与审查期间持续漂移**：t23 交接写 `21117 B / 5b6b3a01…`；我审查中途现算 `22910 B / 4182452a44878c44…`；**审查结束时再次现算为 25449 B / `dce54185d89382bf…`** ⇒ 该文件在审查期间又被写入。下游引用时**必须现算**，不得沿用任一旧值 | `implementation-manifest.json` |

## 6. 本 verdict 未覆盖的未决项（明确划界，避免误读为"已闭环"）

1. **payload 尚未落盘**：`ForCodexDebug/source/test.cpp` 仍为 462848 B / `3dbceb49…`（18:23:31），两函数 SetOn 仍含裸 `126` ⇒ **这才是门禁 exit 1 的直接原因**。本 pass 只判"payload 本身"。
2. **门禁侧仍会报的项**：`verify_relay_trace.py` 在 t25 F2 修复后仍报 `TM601_LS_RDSON: K57_CAP_BST_SW`；payload 落盘后该函数已闭 K57，预期随之消除。
3. **meta `powered_pins` 仍含 `VBUS`** ⇒ `K5_VBUS_Cap` 假阳性会持续到 t26 / t25 提案的 meta 修正落地（t22 裁定 A2）。
4. **settling/R-C 影响**：闭合的 220 nF K57 支路对被测轨的建立影响**payload 明确不作断言**，在 2 ms 零纸上余量下列为 **U11 上机项**。
5. **部署 ≠ 电性验证**：本审查只覆盖代码/口径一致性，**不构成任何电性或硬件结论**。

## 7. 只读证明

`review/t24-readonly-verify.json`：审查开始与结束两次重算被审 payload 及全部被检对象的 python-plaintext sha256，**被审 payload 前后一致 = `444810dd…`**；`devel` 未动；目标树未动；我仅在 `review/` 下新增 3 个文件。

---

## 8. 追认（Captain 唤醒后的终态确认与两项裁定）

**终态确认**：Captain 所指"最终 payload = 35014 B / `444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c`"**与我 t24 已审对象逐字节相同**（我复核 `MATCH: True`，mtime 18:42:34 未变）⇒ **本 verdict（pass）即针对该最终 payload**，无需重审。我预验证所用的 `73995983…`（31,133 B）早已被取代，§1–§7 全部读数**均取自 35,014 B 版**，非旧版。

### 8.1 T24-C（失败上报通道）——**语义可接受 ✅**

实测：`L323 HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);`、`L472 LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);`；失败值经结果对象上报，函数仍 `return 0;`（`L325`/`L474`）。
**依据（项目既有惯例，非我推断）**：`test.cpp` 全篇 **188 处** `->SetTestResult(site, 0, …)`，且**用点号的形式 0 处**；`return 0;` 是 `DUT_API int` 测试函数的统一返回值，**结果与失败以结果值表达**。故"函数返回 0"**不构成**缺失失败通道；`ERROR_RES`（9999）经 `SetTestResult` 进入结果对象，与先例 `L8090 gain[site] = ERROR_RES;` 及 `L7059 if (ls_zcd[site] != ERROR_RES)`（项目自己用"结果值 == ERROR_RES"判别失败）完全一致。
⇒ **T24-C 判为已满足；`return 0` 语义可接受。**

### 8.2 T24-A（"异号 vs 无电流必须可区分"）——**可接受，无需 revision ✅**

**要求的前提被实测证伪**：清单第 2 项要求"异号必须走**独立**的极性/夹具异常上报"。我实测项目**只有一个失败码**：
- `Test_Method.h` 中 `ERROR_*` 令牌全集 = **`['ERROR_RES']`**（唯一）；
- `test.cpp` 中 `ERROR_*` 令牌全集 = **`['ERROR_RES']`**；`sub.cpp` = **0 个**；
- 未发现任何 polarity / fixture / reverse 类错误码令牌。

⇒ 若为了"区分"而自创第二个失败码，**恰恰违反用户裁定**（"须来自项目既有语义，不得自创"）。故实现者"两者都记 `ERROR_RES`"**不是缺陷，而是唯一合规做法**。

**"可区分"要求应以两类证据分别满足，均成立**：
1. **静态可区分（go/no-go）**：两个条件在**独立分支**中给出同一失败结果，且注释逐条写明（`L285-287`、`L445-446`、`L291`/`L450` 行尾并列"no current (|I| ≤ 0.1 A), or an MVRET/MIRET sign mismatch"）⇒ 结果**恒为失败**，不存在"异号却被当合格"或"无电流却被当低阻合格"的路径（§3 已证）。
2. **部署后可区分（诊断归因）**：两者**不是同一故障**——无电流是**力/通路**故障（在 0.1 A 门限下），异号是**极性/夹具**故障（|I| 正常）。两者由`v_meas`、`i_meas` 的实际读数天然区分，且 `i_meas`/`v_meas` 已作为**带符号量**保留（`L281-282`、`L439-440`），可直接入 datalog 复判，无信息丢失。

**理由（为什么不需要"第二条上报通道"）**：结果的 go/no-go 判定**不依赖**"区分"；而"独立上报"在本项目里的等价物是**结果值 + 行内说明 + 原始测量量**，三者均已具备。
**建议（非阻塞，供后续加固；不改变本 verdict）**：若将来要更硬的诊断分离，正确做法是**增加可区分的失败值标记**（例如以 `SetTestResult` 的第 2 个参数或 datalog 中的状态字段表达"极性故障"），而**不是**新增错误码；且必须由 Captain 先裁定，属**跨 TM 的通用惯例变更**，不应在 t23/t24 内私自引入。
⇒ **T24-A 判为可接受；不给 `needs_revision`，不附 blocker finding。**

### 8.3 顺带复核（Captain 的其它引用）

| 引用 | 实测 | 判定 |
|---|---|---|
| `implementation-manifest.json` = 25,449 B / `dce54185d89382bfdd1a58196eb7b410ca88646aa82d38a3dd9820d3f868e18f` | **逐位一致**；`status: PENDING-WRITE …` | ✅ 我 §5 的 ADV-4 漂移告警**就地解除**（该值现为现算值） |
| 预验证 ❌ 项 1/2/3/5/6 在 35,014 B 版转 ✅ | 已实测：正幅值 `fabs/fabs`（`L289`/`L448`）、同号判据 `v*i>0`（`L288`/`L447`）、失败分支 `ERROR_RES`（`L291`/`L450`）、TM600 段内**无** TM601 的 −1 A 表述、**两处** `PMID_HG2` 10 V 台阶 = `FXVIe_PLUS_20V`（`L229` 升、`L298` 落） | ✅ 全部转 ✅，**我确认**（读数取自 35,014 B 版） |

**TM600 段边界说明**：TM600 函数体为 `L179-338`。段内 `L329` 出现的"TM601: LS_RDSON …"是**下一个函数的分隔注释**（紧随 `TM600` 函数体之后的行），不属 TM600 的符号前提；TM600 自身的符号叙述在 `L273-274`（正号取向），**不含** −1 A/negative 表述 ⇒ 第 6 项满足。
