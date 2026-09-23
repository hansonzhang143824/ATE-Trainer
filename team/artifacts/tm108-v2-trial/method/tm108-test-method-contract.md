# TM108 测试方法契约（VAC1_PRST · 阶段/实际节点/测量/下电/Log + 逐阶段 BST-SW 约束）

- runId: `tm108-v2-trial` · task: `t5` · owner: **test-method-expert**
- TM: **TM108** (`VAC1_PRST`, implemented symbol `TM108_HSKP_VAC1_PRST`)
- 写入范围（本任务唯一）：`team/artifacts/tm108-v2-trial/method/`
  `tm108-test-method-contract.md`、`tm108-test-method-contract.json`、`bst-sw-phase-check.md`、`_build_method_contract.py`、`_finalize_method_contract.mjs`
- 上游签名边界：`team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` / `.json`（t4，test-strategy-architect）
- 本契约**只**决定：方法证据与 Golden 适用性、阶段顺序、实际节点电位、测量与计算、下电、Log、逐阶段 BST-SW 约束评价。
  **不**决定：分类/源表/通路/继电器组/寄存器值（策略侧）、C++/SDK/量程枚举/cbite 调用形式（实现侧）、独立评审（评审侧）、编译（门禁侧）。
- **未写入任何项目文件**：`project/DALI/` 只读；`D:/PROJECT6-DALI/devel` 未访问。

---

## 0. 一句话结论

TM108 是**一般测试项目 + 阈值 AWG（toggle）+ grouped**，参数族 **UVLO/PRST**：
在签名边界内共 **9 个阶段**（P0 预状态 → P1 闭合 → P2 VBAT 上电 → P3 寄存器生效 → P4 升扫测量 → P5 折返保持 → P6 降扫测量 → P7 下电归零 → P8 释放与安全终态），
闭合集 **{13, 65}** + **K17 处于闭合态**，寄存器 delta **entertestmode + (DMUX_EN=1, DMUX_SEL=22)**，
测量用 **两段式 rampv_capv**（升扫捕下降沿 / 降扫捕上升沿）产出 **Rise / Fall / Hys(mV)** 三参数。
**观测端点身份未解决（OI-T4-01 → OI-T5-01）**：本契约**从不**把 `DTEST0` 当作 `nQON`，
所有依赖观测端点的决定一律标 **PENDING-OI-T4-01**；DFT 冲突 F1–F6 一律双侧保留、不取舍。
**BST/SW 约束（0 V ≤ BST_actual − SW_actual ≤ 5 V）逐阶段评价：9/9 阶段均标 定点补证（未证实）**，
原因是签名边界内既无 BST/SW 的源表分配、也无任一继电器在其上有必需状态，且 `SW_actual` **不按 0 V 默认**
（理由见 `bst-sw-phase-check.md`，待闭合项 `OI-T5-02` / 退回项 `RT-2`）。

---

## 0b. 修订台账（Rev 2 · task `t10` · `RF-01` / `RR-02` 处置）

> 本文件为**第 2 版（rev 2）**。Rev 1 是 `t8` 独立规则评审所审查的字节（基线哈希见下表），评审的唯一致命项
> `RF-01`（`blocker`，类别 `contract-vs-capability`，owner = **test-method-expert**）以及同一规则下的推论 `RR-02` 由本次修订处置。
> 评审意见：`review/t8-review-findings.md` / `.json`（sha256 `4700223A…` / `CC366492…`，完整值见 §8 evidence）。

| 项 | 内容 |
|---|---|
| 触发 | `RF-01`（阻断）：R3 §6 `logPlan` 列 **10** 个 logicalId，实现只能发出 **3** 个（三条 `SetTestResult`），另 7 条仅在注释里；同规则下的失败路径缺口见 `RR-02`（评审标为 **INFERENCE**，因 `rampv_capv` 的失败语义未登记） |
| 处置 | **disposition (b)** —— 把 raw-context/context 行**显式降级为源码注释文档**（并写明**它们不是工位日志记录**），同时补一条**不依赖任何本项目不存在的 API** 的失败路径规则 |
| 为什么不是 (a) | 见 §6.3 能力审计：本项目唯一可写入工位日志的机制是 `CParam::SetTestResult`，它只能写在**经 `StsGetParam(funcindex,"<名>")` 取得的 DFT 参数**上；本项的 DFT 参数恰好只有 3 个（`VAC1_PRST_Rise/_Fall/_Hys`），把 7 条上下文写成记录就等于**新增 DFT 参数**——那是 DFT/策略侧的改动，越出本契约边界（→ 新增 `OI-T5-06` / `RT-6`，不在此处私自发明） |
| 对评审措辞的一处细化 | 评审的结论“本文件没有可及的 in-TM 文本日志 API”在**实质上成立**，但措辞需细化：`TREG_ERROR::treg_error_log`（`treg.h:176`）**是可调用的**（`treg.h` 在 `test.cpp` 的传递包含闭包内，声明为 `public static`）；它的实现（`treg.cpp:227-251`）却是**开一个调试控制台窗口**（`FreeConsole/AllocConsole/SetConsoleTitleA("AccoTEST Debug Window")/freopen("conout$")`）后 `printf_s` 一段 “ERROR Information List”，**不是工位日志记录**。因此结论不变，但依据从“不可及”改为“可及但不是记录”（证据见 §6.3、§8） |
| 本版改动 | §4 失败路径规则、§6 `logPlan` 全文重发、§8 evidence 增补、§9 openItems 增补 `OI-T5-06`/`OI-T5-07`、§10 returns 增补 `RT-6`、§11 交接、§12 自检 |
| 本版未改 | **未改任何电气值、继电器、寄存器、量程、limit 或容差**；未改 C++ 代码；未访问 `D:\PROJECT6-DALI`（本次只读工作区内产物） |
| 未决项纪律 | `OI-T4-01`、`OI-T5-01`、`OI-T5-02`、`OI-T5-03`、`OI-T5-05`、`RT-1`…`RT-5`、`F1`–`F6` **一条都不解决、不改名、不站边**（新增 `OI-T5-06/07`、`RT-6` 是**新增**，不是对既有项的裁定） |

**哈希台账（Rev 1 基线 = 评审所审查的字节；本版哈希见同目录修订说明）**

| 产物 | Rev 1（基线）sha256（plaintext） | Rev 2 |
|---|---|---|
| `method/tm108-test-method-contract.md` | `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7`（90822 B） | 见 `method/tm108-test-method-contract-rev2-note.md`（一个文件无法包含自身哈希，故同目录落盘） |
| `method/tm108-test-method-contract.json` | `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21`（102544 B） | 同上 |

---

## 1. 上游边界与哈希台账

| 输入 | sha256 | 用途 |
|---|---|---|
| `strategy/tm108-resource-config-contract.md` | `6f6057721062e97ebda53531383aff22a91bd0aa8141aadc6bafc5ef448fe6e4` | 签名资源/配置边界（**唯一权威**） |
| `strategy/tm108-resource-config-contract.json` | `fba489b5d8ca06a12d74c187edbbfe1e2f3fc2d564b27dc6ab8b092f8bd3e4b9` | 机读边界（闭集/寄存器/openItems） |
| `dft/dft-fact-audit.md` | `aec7fd74a01314b856009104c721f93b11fe9490b27c0673dea6e3f385274029` | 当前项目 DFT 事实与 F1–F6 |
| `schematic/schematic-fact-audit.md` | `1f5996b21ae84e2e80688c88015cfea2dd9e35f1075858c72970711a35cef1b8` | 物理节点/继电器/互斥事实 |
| `schematic/tm108-paths-proofs.json` | `293fbbfa4225e08128325a250b8770d263cbac2c5b2d93374b77074e8c3be3bc` | 逐条 proof 的触点/net 原始记录 |

**边界使用（机读字段见 JSON `boundaryUsed`）**

- 源表：VAC123_AMUX_ACM (S5_0), VBAT_PD3_FXVI (S3_5), NQON_HG1_ACM (S5_9, CANDIDATE ONLY)（RA-5 为 `CANDIDATE ONLY`）
- 继电器组：G1, G2, G3, G4（G4 为备选，**本方法不使用**）
- 实际动作闭合集：[13, 65]；K17 只要求“处于闭合态”，其动作形式归 OI-T4-04 与实现侧
- 寄存器字段：entertestmode(), DMUX_EN=1, DMUX_SEL=22；**无**停用字段
- 被驱动/被观测节点：VAC1_F, VAC1_S, VBAT_F, VBAT_S, NetK64_HG1_S1_7 (observation candidate)

**继电器基础态（把签名契约的同一组事实按“每个阶段都能指名一个显式集合”的方式分区；每条都回指契约）**

- 动作闭合（须 SetOn）：`[13, 65]`（G3 功能性闭合；契约 md :224、:245）
- 须处于闭合态、但方法不声明其来源：`[17]`（契约 md :199、:245-246；OI-T4-04）
- 依赖默认导通（**不动作**）：`[8, 18, 19, 64, 88, 89]`（契约 md :247；`K8/K18/K19/K64` 的角色见契约 md :295-298）
- 必须保持未动（隔离/互斥）：`[14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142]`（契约 md :248）
- 板上有通路但**签名契约未赋予状态**：`[7, 61, 57, 48, 76, 110, 109, 41, 42, 43]`（见 `RT-1`/`RT-2`；其中 `K57` 是 BST-SW 耦合电容门）

> 口径：**本方法不新增任何继电器状态**。上表是对契约自身列表的分区；唯一需要策略侧裁决的读回差异（`K13`）见 `RT-1`。

---

## 2. methodEvidence[]（逐来源：适用性 direct / partial / unavailable + 判据）

判据维度（`team/TEAM_ARCHITECTURE_V2.md:203`、`:231-233`）：参数类型 / DUT 拓扑 / 关键相对电压 / DFT 操作点 / 源表工作模式 / 资源边界。

**E1. team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md / .json (signed t4 resource/config contract)**

- 定位：`contract md :27-30, :92-121, :181-252, :256-267, :403-420; contract json resourceAllocation[] / relayGroups[] / registerDelta[] / openItems[]`
- 适用性：**direct**
- 理由：This is the signed resource/configuration boundary for TM108 and the only authority for source tables, channels, closure sets, functional relays, isolation requirements and the register delta. Every phase below cites it; nothing outside it is added.
- 维度：参数类型=n/a (boundary source)；拓扑=n/a；关键相对电压=n/a；DFT 操作点=n/a；源表工作模式=n/a；资源边界=direct - the boundary itself

**E2. team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md (t2 DFT fact audit)**

- 定位：`:138-143 (parameters), :145-168 (Power/Dynamic), :170-179 (Check), :204-216 (Limits), :218-231 (register), :233-244 (timing), :262-276 (F1-F6), :318-337 (P1-P10)`
- 适用性：**direct**
- 理由：Current-project fact layer: it fixes what the DFT actually wrote (vset expressions, check pin name, limit text, register directive, delay) and keeps F1-F6 as registered conflicts. Used for the operating point and for the pending markers.
- 维度：参数类型=UVLO/PRST threshold, single observable；拓扑=single-ended input scan + digital observation；关键相对电压=limit text only (4.4 V / 4.15 V / hys 0.35 V), F1 open；DFT 操作点=direct；源表工作模式=n/a；资源边界=n/a

**E3. team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md + tm108-paths-proofs.txt/.json (t3 schematic fact audit)**

- 定位：`schematic-fact-audit.md :98-203, :205-257, :261-274, :301-315; tm108-paths-proofs.txt per-terminal chains`
- 适用性：**partial**
- 理由：Supplies the physical node facts used by the actual-node and BST/SW derivations (net names, contact numbers, default-conducting tokens, mutual exclusions). Partial because it proves that DTEST0 has 0 hits (:94, :172, :270) - i.e. the observation endpoint of this method is NOT physically resolved there, so the audit can corroborate node potentials but cannot settle the endpoint.
- 维度：参数类型=n/a；拓扑=direct for the node facts；关键相对电压=n/a；DFT 操作点=n/a；源表工作模式=n/a；资源边界=partial: no DTEST0 evidence exists in the three-artifact set

**E4. knowledge/references/L3-method/UVLO.md**

- 定位：`:5-19`
- 适用性：**direct**
- 理由：Parameter-type method for a PRST/UVLO threshold: ramp the pin low->high for the rising threshold, high->low for the falling threshold, Hys = rise - fall in mV, open-drain indication needs a pull-up. Parameter type and topology match TM108 (PRST by name at :17).
- 维度：参数类型=direct (UVLO/PRST family)；拓扑=direct (supply/input ramp + monitor toggle)；关键相对电压=not stated by this source；DFT 操作点=direct；源表工作模式=not stated；资源边界=not stated

**E5. knowledge/references/L1-chip/UVLO.md**

- 定位：`:14-29`
- 适用性：**partial**
- 理由：Gives the mechanism (hysteresis, indicator pin is either POWER GOOD or a DTEST pin, open-drain needs a pull-up per FR-002) and lists PRST as an equivalent threshold class. Partial because it is generic chip knowledge: it does not fix this part's indicator pin identity, so it cannot close OI-T4-01.
- 维度：参数类型=partial (generic UVLO/PRST family)；拓扑=partial (indicator pin role only)；关键相对电压=general hysteresis rationale only；DFT 操作点=n/a；源表工作模式=n/a；资源边界=n/a

**E6. knowledge/references/L3-method/voltage-threshold-ate.md**

- 定位：`:1-34 (method A)`
- 适用性：**partial**
- 理由：Method A of this exact item family ('representative item VAC1_PRST' at :11) fixes the trigger-edge convention (rising ramp -> capture the falling edge; falling ramp -> capture the rising edge) and the Hys formula (:30). Partial because its own prerequisite line :5 states the observation-pin alias 'DTEST0->nQON', and the signed contract forbids treating that alias as fact (OI-T4-01); the alias is therefore carried as pending, not adopted.
- 维度：参数类型=direct (PRST)；拓扑=direct (single-ended input scan)；关键相对电压=trigger-edge convention only；DFT 操作点=direct；源表工作模式=not stated；资源边界=n/a

**E7. knowledge/standards/toggle-awg-rules.md**

- 定位：`:12-34`
- 适用性：**direct**
- 理由：Two-segment ramp => exactly three parameters <base>_Rise/_Fall/_Hys with Hys = Rise - Fall (:14), ramp-call counting rule (:18-26), trigger direction (:28-30), and the mandatory toggle observation relay requirement (:32-34). TM108's DFT has two vset steps, so the 3-parameter contract applies. The 'DTEST0/nQON inverted' wording at :30 is carried as pending (OI-T4-01).
- 维度：参数类型=direct (Toggle/AWG threshold)；拓扑=direct；关键相对电压=trigger level is method-side, not fixed here；DFT 操作点=direct；源表工作模式=direct (voltage ramp + capture)；资源边界=constrains relays (pull-up) but does not name them

**E8. knowledge/standards/functions-registry.md**

- 定位：`:23-31 (shared ramp semantics), :43 (rampv_capv)`
- 适用性：**direct**
- 理由：Fixes the semantics of the measurement primitive this method must use: step = sample count (not a voltage increment), interval >= 10, trig_level = trigger threshold, result = the ramp value at the trigger point. That is what makes the measurement plan executable and reviewable.
- 维度：参数类型=n/a；拓扑=n/a；关键相对电压=n/a；DFT 操作点=n/a；源表工作模式=direct (ramp + capture primitive)；资源边界=n/a

**E9. knowledge/standards/rules-registry.md**

- 定位：`:32 (R-PON), :33 (R-POFF), :37 (R-LOG), :38 (R-HYS), :39 (R-SETON), :44 (R-BST-SW)`
- 适用性：**partial**
- 理由：R-PON/R-POFF/R-HYS/R-LOG/R-SETON apply directly and are cited per phase and in the power-down/log plans. R-BST-SW (:44) is a specialized golden constraint scoped to the Current-Threshold/ZCD item class (its own enforcing script derives the target function from a topology fingerprint) - the TM108 item family is not that class, so the rule is used as the formulation of the 0 <= BST-SW <= 5 V constraint only, not as a topology mandate.
- 维度：参数类型=partial；拓扑=R-BST-SW is partial (different class)；关键相对电压=direct (formulation of the BST-SW window)；DFT 操作点=n/a；源表工作模式=partial；资源边界=n/a

**E10. knowledge/standards/relay-checklist.md**

- 定位：`:25-42 (Cap2 rule and its per-PIN exceptions), :71-75 (closure order and explicit SetOn(-1))`
- 适用性：**direct**
- 理由：Basis for two method decisions: the VBAT cap gate stays closed for a powered rail, and the scanned-input cap gate must be removed (per-PIN exception) - exactly the asymmetry between K13 and K21 that the signed contract requires.
- 维度：参数类型=n/a；拓扑=direct；关键相对电压=n/a；DFT 操作点=direct；源表工作模式=n/a；资源边界=direct (functional relay rule)

**E11. knowledge/references/L4-Golden-code/UVLO.cpp / UVLO.md / toggle-template.cpp (the param_type_index :42 four-pack case for PRST threshold AWG)**

- 定位：`knowledge/references/param_type_index.md:42 and :45 name the case; the code file itself is NOT present in this workspace checkout`
- 适用性：**unavailable**
- 理由：The PRST threshold-AWG golden code is the nearest same-parameter-type case, but its file is not present under knowledge/references/L4-Golden-code/ in this checkout (only UVLO.md is), so it was not read and cannot be graded. No conclusion in this contract depends on it.
- 维度：参数类型=would be direct；拓扑=unassessed；关键相对电压=unassessed；DFT 操作点=unassessed；源表工作模式=unassessed；资源边界=unassessed

**E12. team/artifacts/acceptance-20260916-dali10/setup-contract.json (frozen Setup baseline, read-only)**

- 定位：`:130-160 (ACM200 group and use), :5666-5671 (per-TM TM108 powerSequenceDelta), :5675-5682 (measurePlan), :5683-5719 (limits + BD-04 threshold ruling), :3905-3964 (globalInitialization), :8150-8179 (safetyInvariants, incl. :8156 PIN-attached relays, :8157 site-joint relays, :8161 E006 BST wording, :4162 unified RELAY_OFF ranges)`
- 适用性：**partial**
- 理由：Corroborates the method (per-TM power sequence, site delay, unified off-range table, ACM200 capability +-200 mA, the three-step power-down) and supplies the differential-window wording recorded for BST. Partial, not direct: Setup is frozen and does not decide this TM's method (ROLE_ROUTING :7), and its own open item exists for the TM108 delta (OI-T4-16). Where it and the signed contract differ on an explicit relay state (K13), the difference is returned to strategy as RT-1 instead of being decided here.
- 维度：参数类型=n/a；拓扑=n/a；关键相对电压=E006 wording is the only BST-SW statement in the baseline；DFT 操作点=n/a；源表工作模式=direct for ACM200/FXVIe_PLUS capability；资源边界=partial (read-only baseline)

**E13. team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt (existing implemented TM108 function, lines 390-468)**

- 定位：`:390-468`
- 适用性：**partial**
- 理由：The already-implemented function is the only place where this method's numeric parameters exist today (relay set, delays, 200/20 samples, 1.65 V capture level, ranges, three-step power-down). It is used as corroboration for numbers and as the evidence that these values are not invented - it is NOT an authority: the implemented function embeds the DTEST0==nQON assumption in its comment (:395) which this contract must not adopt, and it is not consistent with the signed contract on K13 (:414). Implementation is a downstream consumer of this contract, so where they differ this contract governs.
- 维度：参数类型=n/a；拓扑=partial (assumes the unresolved endpoint)；关键相对电压=partial (capture level 1.65 V only)；DFT 操作点=n/a；源表工作模式=direct (ramp + capture + ranges)；资源边界=partial: differs from the signed contract on K13

**Golden 结论**：本参数类型的最近同类 Golden（`L4-Golden-code/UVLO.cpp` 的 PRST 阈值 AWG）在本工作区**不可读（unavailable）**，
而知识层给出的观测脚别名（`voltage-threshold-ate.md:5`）与已实现函数注释（`testcpp-blocks.txt:395`）都**内含 `DTEST0`→`nQON` 这一未证实前提**，
因此该 Golden 即便可读也只能作为 **partial** 参考，不得直接采用；本契约的全部结论均不依赖它。

---

## 3. methodPhases[]（阶段状态表）

每阶段列出 prerequisite / relayGroup / resourceState / registerActivation / actualNodeVoltages / differentialChecks / setpoint / ramp / delay / exitCondition；
每个数值回指 DFT、签名契约、active 规则或既有实现（证明“非杜撰”）。

### P0 — Pre-state: no active closure, sources not yet enabled (connect / pre-flight)

| field | content |
|---|---|
| prerequisite | Task accepted; signed resource/config contract hash verified (this file's Boundary + Hash Ledger section). At entry the tester is in the project default relay state: no relay of this item is actuated. |
| relayGroup | none (G1-G4 not yet entered) |
| resourceState | {"closureSetActuated": [], "relaysInExplicitState": {"closed": [13, 65, 17], "notActuated": [8, 18, 19, 64, 88, 89], "keepOpen": [14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142], "notAssignedByContract": [7, 61, 57, 48, 76, 110, 109, 41, 42, 43]}, "sourcesEnabled": "none"} |
| registerActivation | none (no register write yet) |
| setpoint | none (no source is set in this phase); the DFT power intent that will be applied next is vset[vbat,3,100e-6,0] (dft-fact-audit.md :152) with the CSV counterpart vset[vbat,4.2,...] kept open as F4 (dft-fact-audit.md :271). |
| ramp | none |
| delay | none (R-SETON requires the Connect block to start with cbite.SetOn(...) + delay_ms(3) at the start of P1, rules-registry.md :39) |
| exitCondition | Every planned relay has an explicit state (closed / not-actuated / keep-open) and every keep-open relay is at its MOS-open default. Any deviation aborts the item before any source is enabled. |

**actualNodeVoltages**

  - VAC1_F: high-impedance / not driven (no source enabled; the path contact K18/K19 is default-conducting but its far end is the source, RA-1).
  - VBAT_F: not driven (VBAT_PD3_FXVI not enabled).
  - observation node: no pull-up yet (K65 open), so the candidate observation node is floating in this phase.
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Pre-flight differential check on the ramp pair: VAC1_F and VAC1_S are two nets of the same pin (schematic-fact-audit.md :127) - no differential stimulus is planned, so no differential envelope has to be held here.
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P1 — Closure of the signed functional relays (connect)

| field | content |
|---|---|
| prerequisite | P0 passed with every relay in an explicit state (setup-contract.json:3908). |
| relayGroup | G1+G2+G3 entered together; the contract states no relay has a direction- or phase-dependent required state (G2 note in contract json relayGroups[1]), so one closure set covers the whole item and no time-division is triggered (contract md :286). |
| resourceState | {"closureSetActuated": [13, 65], "functionalRelayRoles": {"13": "VBAT stabiliser cap gate for a powered rail (relay-checklist.md :27-37; project/DALI/SCH-Connect-Map.txt:914)", "65": "5 V pull-up for the open-drain observation node (project/DALI/SCH-Connect-Map.txt:891; parameter-type method UVLO.md :19-20)"}, "pathRelayState": "K17 is required to be in the closed state on the VAC1 branch (contract md :199, :245-246) WITHOUT this method claiming how it got there - OI-T4-04 is still open, so no actuation call for K17 is written by this contract (ate-implementer decides the call form under OI-T4-04).", "defaultConductingReliedUpon": [8, 18, 19, 64, 88, 89], "keepOpen": [14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142]} |
| registerActivation | none |
| setpoint | No source value is set in this phase; K13/K65 are functional closures whose only numeric content is the 5 V pull rail of the candidate observation node (project/DALI/SCH-Connect-Map.txt:891). |
| ramp | none |
| delay | contract md :225-226 and setup-contract.json:5667 fix the site delay after the closure: delay_ms(3) (the baseline states 'delay 3 ms'), applied before VBAT is enabled. |
| exitCondition | Closure set equals {13,65} with K17 in the closed state and every keep-open relay un-actuated; the site delay has elapsed. |

**actualNodeVoltages**

  - VAC1_F / VAC1_S: still undriven (source enabled in P2); K21_VAC_Cap stays open so no cap is across the scanned input (contract md :200; K21 source: project/DALI/SCH-Connect-Map.txt:913).
  - VBAT_F / VBAT_S: still undriven; K13 now closed, so the 4.7 uF VBAT stabiliser (project/DALI/SCH-Connect-Map.txt:914) is connected to a rail that will be powered in P2.
  - observation node (candidate nQON_F, net NetK64_HG1_S1_7): now pulled up through K65; the pull-up is fixed at 5 V (project/DALI/SCH-Connect-Map.txt:891) and the node is open-drain, so with the DUT's internal indicator off the node sits near 5 V - which is what makes the 1.65 V capture level (testcpp-blocks.txt:435) a valid mid-scale logic threshold.
  - K64 stays un-actuated, so HG1 is never connected to the tester (contract md :298; schematic-fact-audit.md :170).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Toggle observation relay requirement (toggle-awg-rules.md :32-34) is satisfied functionally: pull-up K65 + the default-conducting K64 observation contact; the pull-up is a functional relay taken from the signed contract, not added here.
  - Isolation check: K21 open (no cap on the scanned input), K14 open (no VAC1-to-AGND short), K70/K87/K90/K82 open (CH0 High branch not selected), K141/K142 open (no FPVIe BUS bridge), K86/K130 open (no force/sense bridge) - all of these are contract isolationRequirements (contract md :201, :222).
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P2 — VBAT static supply on (rest of the item is idle) (power-on)

| field | content |
|---|---|
| prerequisite | P1 closure set confirmed and the 3 ms site delay elapsed. |
| relayGroup | G3 (static supply half; the observation half of G3 is already active from P1 and stays active). |
| resourceState | {"closureSetActuated": [13, 65], "sources": {"VBAT": "VBAT_PD3_FXVI, channel S3_5, force FV=the DFT setpoint, range FXVIe_PLUS_10V, current limit FXVIe_PLUS_100MA (RA-3; the range and limit pair is the existing implemented call at testcpp-blocks.txt:419 and the RELAY_OFF-unified family at setup-contract.json:4162)"}} |
| registerActivation | none |
| setpoint | VBAT setpoint: 3 V (artifact layer) with the 4.2 V CSV counterpart registered, not averaged (dft-fact-audit.md :151-153, :271; contract json openItems OI-T4-12). Ramp time of the DFT expression: 100e-6 s (dft-fact-audit.md :152). |
| ramp | The DFT expression for the rail is a ramp-type command vset[vbat,3,100e-6,0]; the method implements it as the source's own ramp/set behaviour with the 100e-6 s ramp time from the DFT expression, and does not insert a second ramp. |
| delay | delay_ms(1) after the rail is enabled - the value used by the implemented function (testcpp-blocks.txt:420) and consistent with the baseline per-TM sequence (setup-contract.json:5668); it is a method-side hold time, not a DFT number. |
| exitCondition | Rail is at its setpoint and no register has been written yet. |

**actualNodeVoltages**

  - VBAT_F: driven to the DFT setpoint; the authoritative artifact-layer value is 3 V (dft-fact-audit.md :151, tm108.sv body at regconfig-scope.json:35) and the CSV layer states 4.2 V (dft-fact-audit.md :153) - F4 is carried, and the method applies the DFT-intent value 3 V as the single setpoint to code while recording that the conflict is unresolved.
  - VBAT_S: reads the K8 pin-2 node (schematic-fact-audit.md :151).
  - VAC1_F / VAC1_S: still 0 V intent - no stimulus is applied until P4; the ramp primitive starts from its own start point (functions-registry.md :31).
  - observation node: pulled up (P1) - the DUT's indicator state in this phase is exactly the quantity the test measures later, and its identity is unresolved (OI-T4-01).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Rail/return check: the FXVIe_PLUS and ACM200 low ends are grouped to AGND_F (project/DALI/SCH-Connect-Map.txt:801, :804), which is how the single-ended force closes its loop; AGND is a reference only and no source is allocated to it (contract md :99, :186).
  - No differential pair is energised in this phase.
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P3 — Register activation of the observation mux (staircase: testmode key then the delta) (register configuration)

| field | content |
|---|---|
| prerequisite | P2 complete: rail at setpoint, closure set unchanged. |
| relayGroup | G1+G2+G3 unchanged (no relay action in this phase). |
| resourceState | {"closureSetActuated": [13, 65], "note": "No relay changes in this phase; the closure set from P1 remains valid."} |
| registerActivation | Step 1: entertestmode() - mandatory precondition before any register write (contract md :260; register rule knowledge/standards/register-config.md:12-22; DFT provenance en_tm[] at dft-fact-audit.md :227). Step 2: the delta pair DMUX_EN=1 and DMUX_SEL=22 written together as one field directive (contract md :261-263; dft-fact-audit.md :222-224; .sv body regconfig-scope.json:35). Step 3: none. |
| setpoint | No new numeric setpoint: DMUX_EN=1 and DMUX_SEL=22 are the signed contract's values (contract md :261-262), and the contested alternatives (0x55=0x97 i.e. 23; the EN_DTEST0/DTEST0_MUX pair) are recorded, not used (dft-fact-audit.md :230). |
| ramp | none (register writes are discrete actions; no ramp) |
| delay | No dedicated delay is specified by the DFT for the register staircase (the DFT's only delay is delay[1e-3] applied at the end of the sequence, dft-fact-audit.md :237); the method therefore does not insert an invented register settle delay - if implementation-side settling is required it must come back as a need to this owner. |
| exitCondition | Testmode is entered and the one field directive has been issued; the observation-dependent decisions of this phase are still flagged pending. |

**actualNodeVoltages**

  - VAC1_F / VAC1_S: 0 V intent held (the mux writes do not touch the input pin).
  - VBAT_F: setpoint held.
  - observation node: the mux selection is what makes the DUT's indicator visible on this node AT ALL - and because DMUX_SEL's value is contested (22 vs 23, F2) and the observed endpoint's identity is unproven (OI-T4-01), the following decisions are marked PENDING-OI-T4-01, not assumed: (a) that writing DMUX_SEL=22 connects the VAC1 PRST indicator to the observed node, (b) that the mux output is inverted at that node, (c) the CSV-side register counterpart EN_DTEST0/DTEST0_MUX=1/23 which the contract explicitly does not apply (contract md :264).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Register staircase order is a hard rule: entertestmode precedes the writes (R-PON family; contract md :260); writing the two DMUX fields as one directive follows the DFT's own form field[(DMUX_EN,1),(DMUX_SEL,22)] (dft-fact-audit.md :223).
  - The observation-dependent decisions in this phase are pending OI-T4-01 and must not be treated as resolved by any downstream stage.
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P4 — Rising sweep of VAC1 with capture during the sweep (measure (rising segment))

| field | content |
|---|---|
| prerequisite | P3 complete (testmode + delta written); closure set from P1 intact. |
| relayGroup | G1 (contract json relayGroups[0]); G2 closes the same set (relayGroups[1]). |
| resourceState | {"closureSetActuated": ["none - G1/G2 actuate no relay (closureSetActuatedThisStage=[])"], "sources": {"VAC1": "VAC123_AMUX_ACM channel S5_0 as the ramp source; range ACM200_20V and limit ACM200_100MA (range derived from the DFT's 10 V scan end by the rule 'range >= 2x the setpoint, smallest satisfying step' (R-PON, rules-registry.md :32) - 20 V; the ACM200 family limit is +-200 mA (setup-contract.json:134) so 100 mA is within capability), and the observation source NQON_HG1_ACM channel S5_9 with range ACM200_10V and limit ACM200_10UA (RA-5, CANDIDATE ONLY)", "VBAT": "static supply held from P2"}} |
| registerActivation | active from P3 (DMUX_EN=1, DMUX_SEL=22) - the activation is what the phase depends on, and it is pending OI-T4-01. |
| setpoint | Ramp start/end: 0 V -> 10 V per the artifact layer (dft-fact-audit.md :163, :272) with the CSV layer's 3.8->4.4->4.1->3.5 V staircase and the Notes' 3~5 V at 1V/ms recorded as unresolved (F5/F6). Capture level 1.65 V (testcpp-blocks.txt:435). Range 20 V and limits 100 mA / 10 uA as above. |
| ramp | Ramp time: 1e-3 s for the DFT vset step (dft-fact-audit.md :241; regconfig-scope.json:35). Geometric ramp parameters for the primitive: 200 samples at 20 us per sample = 4 ms of sweep (functions-registry.md :27-28 for the semantics; the 200/20 values are the existing implemented call, testcpp-blocks.txt:435 - a method-side choice and not a DFT number). |
| delay | No separate delay inside the sweep; the hold before the sweep is the P3/P2 chain. Post-sweep the DFT's only delay is 1e-3 s at the end of the sequence (dft-fact-audit.md :237). |
| exitCondition | The trigger fired at a captured source voltage (a result exists for this segment) or the sweep reached its end point without a trigger - in the latter case the segment fails its own completeness condition and the failure-path rule of §4 applies (the affected parameter is **not published**; nothing is written in its place). |

**actualNodeVoltages**

  - VAC1_F: swept from the ramp start point to the ramp end point; the ramp geometry itself is a registered conflict (F5: 0->10->0 V vs 3~5 V at 1V/ms vs 3.8->4.4->4.1->3.5 V, contract json OI-T4-13) and is therefore marked PENDING; the single geometry written into this phase is the artifact/Code2 one (0 V -> 10 V) with the two competitors recorded verbatim.
  - VAC1_S: the source's own sense port on the same pin - the measurement reference is the source's reading on that node, not an independent Kelvin pair (contract json resourceAllocation RA-2 senseCharacter).
  - VBAT_F: setpoint held (the ramp source is a different instrument and a disjoint chain - contract md :300).
  - observation node: toggles when the VAC1 threshold is crossed; the tabulated thresholds in this method count on the indicator's polarity, which is pending (OI-T4-01) - see differentialChecks.
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Trigger polarity (pending OI-T4-01): the parameter-type method says the rising sweep must capture the FALLING edge of the indication (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30), i.e. TRIG_FALLING with a 1.65 V level (level and mode provenance: existing implemented call testcpp-blocks.txt:433-435; the level is a mid-scale logic threshold for the 5 V pull-up of project/DALI/SCH-Connect-Map.txt:891). This is only correct if the indicator presented on the observed node is inverted as the knowledge base states; that premise is DTEST0==nQON-dependent and is marked PENDING, so neither the polarity nor the level may be treated as settled.
  - Anti-short: the VAC1 chain contains no other DUT pin (every accepted VAC1 proof has terminal_stop=true, contract md :318; schematic-fact-audit.md :85).
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P5 — Hold at the sweep end before the falling segment (stimulus endpoint / turn-around)

| field | content |
|---|---|
| prerequisite | P4 exited with a captured rise value, or with a no-capture condition handled per the §4 failure-path rule (no value published for the affected parameter). |
| relayGroup | G2 entered; the closure set is unchanged from G1 (contract md :205-211). |
| resourceState | {"closureSetActuated": ["none - G2 is the same closure set as G1"], "sources": {"VAC1": "ramp source held at the 10 V end point (same range/limit as P4)", "VBAT": "held"}} |
| registerActivation | active (unchanged, pending OI-T4-01) |
| setpoint | Held value: the falling segment's start point, i.e. the rising segment's end point (10 V per the artifact layer; F5 open). |
| ramp | none in this phase (the ramp belongs to P4 and P6). |
| delay | Method-side settle before reversal: the DFT delay applied at the end of the sequence is 1e-3 s (dft-fact-audit.md :237); the method does not invent an additional turn-around delay but requires the reversal to be written as a consecutive call to the same primitive (P6) with no relay/range change between the two calls. |
| exitCondition | The observed value has been stable across the reversal boundary (or the instability is recorded as failure context). |

**actualNodeVoltages**

  - VAC1_F / VAC1_S: at the sweep end point (10 V nominal) - the only phase in which the scanned pin is held at an extreme before the reverse sweep, which is why the turn-around order is written explicitly: the falling segment must start from a settled value and must not include a relay action (K21 stays open throughout: project/DALI/SCH-Connect-Map.txt:913).
  - VBAT_F: setpoint held.
  - observation node: the indicator is in its post-threshold state; the state's identity is pending (OI-T4-01).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Turn-around differential rule: nothing in this method requires a differential pair; the two nets VAC1_F/VAC1_S belong to the same pin and are never driven as a differential stimulus (schematic-fact-audit.md :127).
  - Reversal ordering: the same source is used for both segments (RA-1/RA-2) so no source hand-off and no series-relay switch occurs at the turn-around - this is what keeps the closure set identical in G1 and G2.
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P6 — Falling sweep of VAC1 with capture during the sweep (measure (falling segment))

| field | content |
|---|---|
| prerequisite | P5 complete; closure set and register activation unchanged. |
| relayGroup | G2 (contract json relayGroups[1]). |
| resourceState | {"closureSetActuated": ["none - G2 actuates no relay"], "sources": {"VAC1": "ramp source from the end point back down (same range/limit as P4)", "VBAT": "held"}} |
| registerActivation | active (unchanged, pending OI-T4-01) |
| setpoint | Ramp start/end: 10 V -> 0 V per the artifact layer (dft-fact-audit.md :164) with the CSV layer's staircase recorded as unresolved (F5). Capture level 1.65 V (testcpp-blocks.txt:439). |
| ramp | Ramp time: 1e-3 s for the DFT vset step (dft-fact-audit.md :241); primitive geometry 200 samples x 20 us (testcpp-blocks.txt:439, semantics functions-registry.md :27-28). |
| delay | No in-sweep delay; the DFT's terminal delay 1e-3 s (dft-fact-audit.md :237) is applied after this phase as part of the completion of the measurement sequence (it is not part of the power-down, whose delay is R-POFF's delay_ms(1)). |
| exitCondition | Both segments have produced a captured value (or a no-capture condition handled per the §4 failure-path rule), and the pair is complete for the Hys computation. |

**actualNodeVoltages**

  - VAC1_F: swept downward; this segment is what produces the second of the two thresholds, so its geometry inherits the same unresolved F5 geometry and must be written consistently with P4 (a fall segment that does not mirror the rise segment would fabricate a hysteresis).
  - VAC1_S: as in P4.
  - VBAT_F: setpoint held.
  - observation node: toggles in the opposite direction; polarity pending (OI-T4-01).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Trigger polarity (pending OI-T4-01): the falling sweep must capture the RISING edge (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30), written as TRIG_RISING with the same 1.65 V level (testcpp-blocks.txt:437-439).
  - Both segments must be evaluated with the same capture level, otherwise Hys would carry a measurement artefact instead of a device hysteresis.
  - The result of this phase is the second of exactly three parameters (toggle-awg-rules.md :14) - a single-parameter method would violate the ramp-call-count rule (:18-26).
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224).
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P7 — Bounded settle window then de-energising the stimulus sources (power-down step 1 of 3)

| field | content |
|---|---|
| prerequisite | P6 complete; both segment results recorded. |
| relayGroup | G1/G2/G3 closure set STILL ACTIVE in this step (the relays are not released until the last power-down step) - the contract's relay groups have no power-down variant, and R-POFF's three-step rule keeps the relay state through step 1 (rules-registry.md :33). |
| resourceState | {"closureSetActuated": [13, 65], "sources": {"VAC1": "FV=0, range/limit held as in P4, relay still ON", "VBAT": "FV=0, range/limit held, relay still ON", "observation": "FV=0, range ACM200_10V, limit ACM200_10UA, relay still ON"}} |
| registerActivation | still active from P3 (no register write is used to disable it; the contract delta has no disable field) |
| setpoint | All setpoints in this step are 0 V (the zeroing order of P7/P8 is the existing implemented sequence at testcpp-blocks.txt:452-454). |
| ramp | downward to 0 V; no ramp is applied in this step (the sweep already ended in P6). |
| delay | delay_ms(1) between zeroing and the relay release (R-POFF's step 2; rules-registry.md :33; existing implementation testcpp-blocks.txt:455). |
| exitCondition | Every source reads 0 V intent and the hold has elapsed. |

**actualNodeVoltages**

  - VAC1_F: driven to 0 V (source zeroing, source relay still ON).
  - VBAT_F: driven to 0 V while K13 is still closed, i.e. the 4.7 uF stabiliser remains across a collapsing rail - that is the intended discharge path of the rail before the cap gate is released (K13 1 kohm bleed note: setup-contract.json:3943).
  - observation node: the pull-up source is zeroed; the node's logic state after this step is no longer a defined quantity and is not used by anything downstream.
  - Chip internal state: the testmode/mux activation is NOT un-written in this step; the delta has no disable field and the contract provides none (returning that need is RT-3).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - De-energising order: the scan/supply stimulus is zeroed BEFORE any contact is opened, which is the anti-short-arcing requirement 'never hot-switch a BUS relay between unequal potentials' (setup-contract.json:8175) and R-POFF's step 1.
  - All three sources are returned to FV=0 while keeping their ranges, which is R-POFF's 'zero while holding range' step (rules-registry.md :33).
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224). Note that BST-SW collapse ordering (the R-BST-SW wording 'the FET must stay on while the rails collapse', setup-contract.json:8161) is about items that actually drive BST; it cannot be honoured or violated here because this item drives neither node.
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

### P8 — Release of the signed closure set and the safe end state (power-down steps 2-3 of 3)

| field | content |
|---|---|
| prerequisite | P7 completed: all sources zeroed, hold elapsed. |
| relayGroup | G3 release (functional relays), then G1/G2 are already in their un-actuated state; no relay is left actuated. |
| resourceState | {"closureSetActuated": [], "finalRelayState": {"13": "released (cap gate opened, which is the sanctioned discharge mechanism per setup-contract.json:3943)", "65": "released", "keepOpen": [14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142], "notActuated": [8, 18, 19, 64, 88, 89]}, "finalSourceState": "all three channels RELAY_OFF with the unified RELAY_OFF ranges (ACM200_10V/10MA, FXVIe_PLUS_10V/10MA - rules-registry.md :33 and setup-contract.json:4162)"} |
| registerActivation | none (nothing is written and nothing is un-written - the state of the delta fields after the item is out of scope; see RT-3) |
| setpoint | None (all setpoints 0 V and all channels off). |
| ramp | none |
| delay | The RELAY_OFF stage carries no additional delay beyond the hold already applied in P7. |
| exitCondition | All relays released, all sources off with unified ranges, no rail charged, no source energised. |

**actualNodeVoltages**

  - VAC1_F / VAC1_S: source relay open, no drive, no cap (K21 open) -> floating node.
  - VBAT_F / VBAT_S: source relay open; K13 released, so the rail has no charge path and the cap gate's 1 kohm bleed (setup-contract.json:3943) is the discharge mechanism.
  - observation node: pull-up released -> floating.
  - K8/K18/K19/K64 remain un-actuated (never touched by this item) - the same state they had at P0, so the item leaves no selector residue.
  - K17, if it was closed by the VAC1 branch entry, is left as the VAC1 branch entry state requires; releasing it would re-open the branch and is therefore NOT part of this method (the contract requires the closed state and does not assign the actuation - OI-T4-04).
  - BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
  - BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
  - K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
  - K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.

**differentialChecks**

  - Safe end state check: no source is left energised, no cap gate for a powered rail is left closed, every keep-open relay is at its MOS-open default, and no relay of this item remains actuated.
  - Abnormal exit runs this same two-step sequence (zero -> hold -> release) from the finally path - an aborted item may not leave a charged rail or an energised source (setup-contract.json:8179).
  - BST/SW: 定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints (contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore DUT-internal states of a switching stage that the DFT does not commit and that the register delta does not enable; SW must NOT be defaulted to 0 V (architecture :212-224). Closing evidence for the whole item: see OI-T5-02.
  - BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

---

## 4. measurementPlan（force/measure、量程、扫描、采样窗口、计算、limit、site）

- 参数集：`VAC1_PRST_Rise, VAC1_PRST_Fall, VAC1_PRST_Hys` — Two ramp segments (rise + fall) => exactly three parameters <base>_Rise/_Fall/_Hys with Hys = Rise - Fall; a single-parameter plan is forbidden (toggle-awg-rules.md :14, :18-26). The three names already exist in the current implementation, which is corroboration only (dft-fact-audit.md via contract json parameterType.awgParameterContract).
- 原语：`test_method.rampv_capv` — ramp a voltage source and capture the ramp value at the trigger point; step = sample count, interval >= 10, trig_level = trigger threshold, result = ramp voltage at the trigger sample (functions-registry.md :25-31, :43)
- 合法性：rampv_capv is the volume-ramp/capture member of test_method, which is what an AWG item must use (toggle-awg-rules.md :8-11; test-types.md :71)

### 段：rise（阶段 P4）

- force 端点：VAC1；通道 VAC123_AMUX_ACM S5_0 (force port S5_ACM200_FH0)；模式 FV ramp
  量程 ACM200_20V / ACM200_100MA；量程依据：R-PON range rule: >= 2x the setpoint, smallest satisfying step; the scanned end is 10 V (dft-fact-audit.md :163), so 20 V. The ACM200 family limit is +-200 mA (setup-contract.json:134)
- measure 端点：observation candidate (NQON_HG1_ACM S5_9, CANDIDATE ONLY)；量程 ACM200_10V / ACM200_10UA；**PENDING-OI-T4-01 - the endpoint's identity is unproven; consuming this allocation requires the DTEST0->nQON relation or the nQON side to be established**
- sweep：0 V → 10 V（依据 artifact layer / Code2 (dft-fact-audit.md :163); F5 keeps 3~5 V at 1V/ms (Notes) and 3.8->4.4->4.1->3.5 V (CSV) registered and unresolved - PENDING）
- step：200 samples (sample count, not a voltage increment - functions-registry.md :27)；采样窗口：interval 20 us per sample => 4 ms of sweep for the segment; the primitive's own requirement is interval >= 10 (functions-registry.md :28)
- trig：1.65 V (mid-scale logic threshold for the 5 V pull-up of project/DALI/SCH-Connect-Map.txt:891; existing implemented level testcpp-blocks.txt:435) / TRIG_FALLING（依据 rising input sweep captures the falling edge of the indication (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30) - PENDING because it assumes the indicator's polarity on the observed node）
- result：the ramp source voltage at the trigger point = rising threshold candidate

### 段：fall（阶段 P6）

- force 端点：VAC1；通道 VAC123_AMUX_ACM S5_0 (same channel, same source as the rise segment)；模式 FV ramp
  量程 ACM200_20V / ACM200_100MA；量程依据：same as the rise segment: 20 V for a 10 V scan end (R-PON range rule, rules-registry.md :32)
- measure 端点：observation candidate (same as rise)；量程 ACM200_10V / ACM200_10UA；**PENDING-OI-T4-01**
- sweep：10 V → 0 V（依据 artifact layer / Code2 (dft-fact-audit.md :164); mirrored to the rise segment so that Hys cannot be fabricated by a geometry mismatch - PENDING with F5）
- step：200 samples；采样窗口：interval 20 us per sample => 4 ms of sweep for the segment
- trig：1.65 V (identical to the rise segment) / TRIG_RISING（依据 falling input sweep captures the rising edge of the indication (voltage-threshold-ate.md :26-32) - PENDING as above）
- result：the ramp source voltage at the trigger point = falling threshold candidate

### 计算与判定

- VAC1_PRST_Rise = captured ramp voltage of the rise segment (unit V, DFT unit: dft-fact-audit.md :209)
- VAC1_PRST_Fall = captured ramp voltage of the fall segment (unit V)
- VAC1_PRST_Hys = (Rise - Fall) * 1e3 -> unit mV, per R-HYS (rules-registry.md :38) and voltage-threshold-ate.md :30; the x1e3 is applied at the assignment and commented, never applied to the logged identity of Rise/Fall
- Each site is measured and judged independently; results are per-site arrays and Hys is computed per site from that site's own Rise and Fall. No cross-site averaging, interpolation or sharing of captured values is permitted.

### limits

- 权威文本：`rising vth 4.4 V, hys 0.35 V; unit V (dft-fact-audit.md :208-209)`（依据：artifact/OVERVIEW layer; the frozen baseline's BD-04 threshold ruling accepts the same side (setup-contract.json:5695-5700; ruling scope: that debug-copy acceptance only)）
- 已登记冲突：the DFT CSV layer states 4.15 V for the same rising threshold (dft-fact-audit.md :214, :268); it is registered as OI-T4-09 and is NOT averaged, rewritten or dropped
- 容差：NOT PUBLISHED in any DFT source (dft-fact-audit.md :215) and the frozen baseline records the same (setup-contract.json:5687)
- 使用方式：This contract therefore states which threshold text is authoritative and that the tolerance does not exist; the pass/fail application (including how a missing tolerance is handled) is a spec-side decision, returned as RT-4 rather than invented here. F1 remains an open ruling item (OI-T4-09) and must not be treated as settled by the implementation or by review.
- Hys 定义：Hys = Rise - Fall (a device property); the DFT limit 'hys 0.35 V' is compared against the computed mV value after the R-HYS conversion.

### 失败路径规则（no-trigger / boundary-trigger / negative-Hys）· Rev 2 重发

> Rev 1 的这里要求“记录 log plan 的失败上下文”。Rev 2 保留它的**三个触发情形**与“**不得写入被替代的数**”这一禁止，
> 但把“记录”换成**本项目真实存在的两种载体**（源码注释文档 + “不发布结果”本身），因此**不依赖任何本项目不存在的 API**。
> 三个情形**逐 site**判定；判定只用本项自己写进调用和读回的端点值，**不引入任何新的电压、电流、阈值、limit 或容差**。

1. **没有触发（no trigger）**：该段没有产生捕获。该 site 的 `<base>_Rise` / `<base>_Fall` **不得发布数值**——
   包括数组的**初值/默认值**在内，任何非捕获的数字都不得送进工位日志写入机制；`Hys` 也不得由缺捕获的段计算。
   *能力状态*：原语是否上报“没有触发”本身**未登记**（`functions-registry.md:43` 只登记了 *result = 触发点处的 ramp 电压*，没有失败信号），
   因此本契约**不指定**任何检测原语，只规定义务，并把该缺口登记为 **`OI-T5-07`**。在该项闭合前，
   “无捕获”必须按**未闭合的失败路径**对待，**不得**当作已合规（这正是不把它写成代码缺陷的原因，与评审 `RR-02` 的定性一致）。
2. **边界触发（boundary trigger）**：捕获值等于该段**自己声明的两个端点值之一**（即触发发生在扫描边界上，不是区间内的阈值）。
   发布层面按第 1 条处理，并在该 site 的失败记录中写明命中的是哪一个端点。判据只用该段自己的起止值，**不新增阈值**。
3. **负 Hys（negative Hys）**：该 site `Rise < Fall`。这是一个**计算量**，不是缺捕获的替代数，因此**按计算值发布**，
   不得钳位、不得改符号、不得跨 site 平均；同时该 site 必须**另行标注为失败路径情形**。负 Hys 是否判失败属于 spec 侧问题
   （本项**没有发布容差**：`RT-4`），**不在此处裁定**。

**记录载体（与本项目真实能力一致）**：失败上下文（阶段 id、段、原因、触发模式、捕获电平、实际使用的起止/步数/间隔，以及当时生效的未决项）
以**源码注释文档**的形式落在本项自己的区段内——即 §6.2 给 raw-context 行的同一状态，**不声称为工位日志记录**
（边界内没有承载自由文本上下文的工位日志机制：见 §6.3 与 `OI-T5-06`）。
在工位日志一侧**真实可用且必须兑现**的，是该参数**结果的缺失**：**不发布数值本身就是记录**。

### 越界需求（不在边界内，须退回或登记）

- The observation endpoint identity and its polarity: returned to strategy/DFT via OI-T4-01; the measurement cannot be finalised until it is closed.
- The scan geometry: returned via F5 (OI-T4-13). The resource allocation itself is range-agnostic (contract json OI-T4-13), so only the method's geometry is pending.
- A per-segment settle/sampling requirement beyond the DFT's single 1e-3 s delay: would be a method need not derivable from the DFT - returned as RT-5 if a reviewer or implementer requires a number.

---

## 5. powerDownPlan（下电动作、节点电位、差分检查、安全终态）

- 类型：normal de-energisation (no floating-source pair and no high-current loop is used by this item, so R-POFF's floating and high-current branches do not apply - rules-registry.md :33)

| # | 动作 | 阶段 |
|---|---|---|
| 1 | Zero the scan source: VAC1 FV=0 while holding its range and leaving its relay ON. | P7 |
| 2 | Zero the supply: VBAT FV=0 while holding its range and leaving its relay ON (K13 still closed, so the 4.7 uF stabiliser discharges through the rail's bleed). | P7 |
| 3 | Zero the observation capture source: FI/FV=0 with range ACM200_10V / ACM200_10UA, relay still ON. | P7 |
| 4 | Hold delay_ms(1). | P7 |
| 5 | Release all three channels with the unified RELAY_OFF ranges (ACM200_10V/10MA, FXVIe_PLUS_10V/10MA). | P8 |
| 6 | Release the functional closures K13 then K65 (cap gate opening is the sanctioned rail discharge), leaving every keep-open relay un-actuated. | P8 |

**规则依据**

- R-POFF normal three-step (zero while holding range -> delay_ms(1) -> RELAY_OFF with unified ranges) - rules-registry.md :33
- unified RELAY_OFF range table - setup-contract.json:4162
- every energised rail needs a discharge plan (cap gate opened + bleed) - setup-contract.json:3943, :8177
- abnormal exit runs the same sequence - setup-contract.json:8179

**actualNodeVoltages（下电）**

- after step 4: all three driven nodes are at 0 V intent, VBAT_F is a collapsing rail with K13 still closed
- after step 6: no node of this item is driven; VBAT_F/VBAT_S/VAC1_F/VAC1_S/observation node are floating with all caps released

**differentialChecks（下电）**

- no differential pair is energised during the power-down
- the only differential check that applies is the BST/SW constraint, which is NOT PROVEN for both power-down phases (see bst-sw-phase-check.md; closing evidence OI-T5-02)

**安全终态**：no source energised; no cap gate of a powered rail left closed; every keep-open relay at its MOS-open default; K8/K18/K19/K64 never actuated, so no selector residue; nothing written to the DUT after the power-down (no register de-activation exists in the signed delta).

---

## 6. logPlan（原始量 / 计算量 / 判定量 / 单位 / 精度 / 上下文）· **Rev 2 重发**

> **本节按 `RF-01` 重新签发（disposition (b)）。** Rev 1 把 10 个 logicalId 一律称作 “log”，其中 7 条在签名边界内**没有可用的记录机制**。
> Rev 2 明确分成两类：**§6.1 = 工位日志记录（3 条 calculated，机制与字段映射逐条给出）**；
> **§6.2 = 原始量/上下文行 = 源码注释文档（7 条，明文声明它们不是工位日志记录）**。
> 能力审计与逐候选依据见 §6.3；失败路径规则见 §4「失败路径规则」。

- site 模型：All logged quantities are per-site; each site is judged with its own values (no shared or averaged quantities).

### 6.1 工位日志记录（本项目唯一可及的日志写入机制）

**机制**：`CParam::SetTestResult(<site>, <limit>, <value>)`，在由 `StsGetParam(funcindex, "<parameter name>")` 取得的**DFT 参数对象**上调用。
参数名必须来自本项的 DFT 参数表，而本项恰好只有 3 个参数；因此**能被记录的量的上限就是这 3 条**。
依据：活动标准 `R-LOG`（`rules-registry.md:37`）本身就用 `SetTestResult` 表述 Log 规则；本项目内不存在第二个工位日志写入机制（§6.3 逐候选审计）。

**字段映射（参数位置 = 字段）**

| 位置 | 字段 | 本项取值来源 |
|---|---|---|
| 1 | site | 逐 site 循环的 site 索引（site 模型见上），**逐 site 独立** |
| 2 | limit | **本项不使用**：本项没有发布任何容差（`RT-4`）。此位不承载测量值，也**不得**被当作上下文的记录载体 |
| 3 | value | 下表 `source` 列的量 |

| logicalId | kind | unit | precision | source（→ 位置 3 的 value） | notes |
|---|---|---|---|---|---|
| `VAC1_PRST_Rise` | calculated | V | as specified for the parameter | captured ramp voltage of the rise segment | unit must match the DFT unit column (V) - R-LOG (rules-registry.md :37) |
| `VAC1_PRST_Fall` | calculated | V | as specified for the parameter | captured ramp voltage of the fall segment | same unit rule |
| `VAC1_PRST_Hys` | calculated | mV | as specified for the parameter | (Rise - Fall) * 1e3 | R-HYS: the conversion is applied at the Hys assignment with a comment and is never applied to the Rise/Fall identity (rules-registry.md :38) |

这三条是**本项唯一的工位日志记录**。除此之外没有第四条：要让任何其他量成为记录，必须先在该 DFT 项的**参数表**里存在同名参数，
而这属于 DFT/策略侧的改动（→ 新增 `OI-T5-06` / `RT-6`）。**本契约不发明参数名。**

### 6.2 原始量 / 上下文行 —— 源码注释文档（**不是工位日志记录**）

> **明文声明**：以下 7 行**不是工位日志记录，也不会被任何调用发出**。它们是**源码注释文档**——读者在**源码**里读到它们，
> 不会在**工位日志**里读到它们。本契约**不声称**这些量被记录、也**不声称**存在承载它们的机制。这就是本版的方法侧立场（disposition (b)，`RF-01` 的处置内容）。
> 任何把这些注释当作“已记录的上下文字段”的说法，都超出本契约允许的范围（§6.4）。

| logicalId（文档标识，非日志字段） | 文档应载明 | 落点 | 为什么只能停在注释 |
|---|---|---|---|
| `triggerModeRise` / `triggerModeFall` | 每段**实际使用**的触发模式 | 该项 P4/P6 区段注释 | 极性未决（`OI-T4-01`）；注释与调用同址，改代码即改注释 |
| `captureLevel` | 两段**实际使用**的（同一个）捕获电平 | 同上 | 用于向复核者证明两段同电平（否则 Hys 会带上测量伪影） |
| `sweepGeometry` | **实际使用**的起止、步数、间隔 | 同上 | `F5`/`OI-T4-13` 未决；注释与调用同址 |
| `registerActivationTrace` | testmode 进入与那条字段指令（`DMUX_EN`/`DMUX_SEL`）**实际写入**的值 | 该项 P3 区段注释 | `F2` 未决：需记录**实际写入**值而非争议值 |
| `relayActuationTrace` | **实际应用**的闭合集与每个 keep-open 继电器的状态 | 该项 P1 区段注释 | 通路检查覆盖不到 PIN 附着功能继电器（`setup-contract.json:8156`） |
| `failureContext` | 阶段、段、原因（no trigger / boundary trigger / negative Hys）与当时生效的未决项 | 该项测量区段注释 + §4 失败路径规则 | 边界内无自由文本日志机制（§6.3、`OI-T5-06`）；未捕获时**不发布数值本身就是记录** |
| `bstSwStatus` | 逐阶段 BST/SW 判定（9/9 定点补证，pending `OI-T5-02`） | 该项 banner 注释 + `bst-sw-phase-check.md` | 让下游看到该约束**被评估过且未证实**，而不是被静默省略 |

### 6.3 能力审计：这 7 行为什么不能成为记录（逐候选 · 含包含闭包与可及性）

> 方法：以 `test.cpp` 的**传递包含闭包**与**声明可及性**为准，而不是以名字搜索为准（本项目存在两份不同字节的 `treg.h`/`treg.cpp`，名字搜索会误判）。

| 候选机制 | 声明位置 | 是否在 `test.cpp` 闭包内 / 可调用 | 结论 | 本次复核所用的证据 |
|---|---|---|---|---|
| `CParam::SetTestResult(<site>,<limit>,<value>)`（经 `StsGetParam(funcindex,"<名>")`） | `CParam` 本身是 SDK/框架类型，**不在本项目源码树内**（评审全树搜索 `decl=-`） | **是**，本项唯一可用的日志写入路径 | **唯一可用的记录机制**；但受“DFT 参数名”约束 → 只能承载 §6.1 的三条 | 评审 `logging.txt` §C（代码内 **187** 处调用）、§G（`test.cpp` 内**没有**任何以字符串/格式串为参数的函数**定义**）；本次复核 `review/copy/test.cpp` 中 `SetTestResult(` 共 **188** 次文本出现，其中 1 次在注释内（`:1159`）→ 187 处代码调用，与评审一致 |
| `TREG_ERROR::treg_error_log(const char* format, ...)` | `treg.h:176`（`public static` 于 `class TREG_ERROR`） | **是**（`StdAfx.h:27` → `treg.h`，即 `test.cpp` 的传递闭包内），**可调用** | **可及，但不是工位日志机制**：实现会 `FreeConsole()`/`AllocConsole()`/`SetConsoleTitleA("AccoTEST Debug Window")`/`freopen("conout$","w+t",stdout)`，然后 `printf_s(" ERROR  Information List..............\n")`、`printf_s(" %d. ", error_count)`、`printf_s(buffer)` —— 写的是**调试控制台窗口**，无 site 维度、不落入工位数据日志。**不采用**（另：把良性的方法上下文当“错误”打进错误列表本身就不成立） | 本次复核 `Library-Functions/treg/treg.cpp`（与项目 `source/treg.cpp` 同字节，sha256 `AE86D1A1CDBD3EE1BAED85D3435A46CB19D5803AE97C0FAF0373E1CA91512489`）`:191-192`、`:227-251`；评审 `errlog.txt`。**这是对评审措辞的唯一细化**：结论不变，依据由“不可及”改为“可及但不是记录” |
| `TREG_LOG::log_data(...)` | `treg.h:195`（于 `class TREG_LOG` 的 **`private:`** 段；`friend` 仅 `TREG` / `TRIM_NODE` / `TRIM_GRP_NODE`） | 闭包内但**私有 → TM 函数不可调用** | **不可及** | 评审 `reach.txt`（`treg.h` IN CLOSURE: True；`class TREG_LOG` 段含 `private:`=True）；本次复核 `Library-Functions/treg/treg.h:186-199` |
| `CBC_log::log` / `CBC_log::test_log` | `BoardCheck.h:759-760`（`board_check`/`bc_log` 成员在 `:778`） | **不在闭包内**；`CBC_log`/`bc_log`/`test_log` 在 `BoardCheck.*` 之外**无使用者** | **不可及** | 评审 `reach.txt`（BoardCheck.h IN CLOSURE: **False**；无外部使用者）、`extern_c11b.txt`；本次复核工作区同字节副本 `Library-Functions/BoardCheck/BoardCheck.h`（sha256 `AD562C1C14929BBF71F5549269CE6C44C16352EB4D4299A130952F714D5D83EA`，与项目 `source/BoardCheck.h` 同字节）在 `test.cpp` 中零使用 |
| `msLogData(...)` + `SetTestNumber(...)` | 仅见于 `treg.cpp:348`，位于 **`#ifdef TREG_ETS364`** 平台分支内；声明在**本工作区不存在的测试机框架头**（该处注释指向 `uicclib.h`） | **可及性与语义 UNKNOWN**（本任务无法证明声明、实现与调用语义） | **不采用**：评审侧 charter 的“库函数”铁律要求每次调用回指**登记、声明、真实实现与调用语义**，在无声明的情况下调用它，正是本交付被扣分的同一类缺陷（参见 `RF-02` 的违规依据）；且它按 test number 记录、面向 trim 步骤值，本项没有对应登记 | 本次复核 `Library-Functions/treg/treg.cpp:287`（`#ifdef TREG_ETS364` 开）、`:302`、`:346-348`；评审 `reach.txt`/`final_reach.txt`。→ 登记为 `OI-T5-06`（记录能力）与 `RT-6`（需要框架侧确认） |
| `LogData`（`test.cpp` 内 91 处） | —— | 全部是 `// ====== Step 6: LogData ======` 注释头，**从不是调用** | **非机制** | 评审 `logging.txt` §A/§B；本次复核计数一致（91 处注释头） |
| `printf` / `cout` | `test.cpp:390`、`:564-569` | 仅热键/UI 代码（其中 564/565 已注释、569 为注释文字） | **非工位日志机制** | 评审 `logging.txt` §D；本次复核一致 |
| `stslogdata(...)` | `source/src/treg.cpp`（**重复副本**，非 `source/treg.h`） | 未在本工作区任何头中看见声明 | **不采用**；且**即便可用也不新增能力**：其自身实现仍走 `StsGetParam(funcindex,"Func_Label")->SetTestResult(...)`，同样受 DFT 参数名约束 | 评审 `cparam.txt` §2（`source\src\treg.cpp:62-75`） |

**审计结论**：`test.cpp` 内**唯一**的工位日志写入机制是 `CParam::SetTestResult`，它只能写在经 `StsGetParam` 取得的 DFT 参数上；
本项目不存在第二个能把**自由文本上下文**写进工位日志的机制（`treg_error_log` 只写调试控制台；`log_data` 私有；`CBC_log` 不可及；`msLogData` 未证实）。
因此 §6.2 的 7 行走不了记录路线——**这不是实现缺陷，而是平台与被签边界的事实**，`RF-01` 的处置正是据此选择 (b)。

### 6.4 禁止

- logging a source-table raw value in the wrong unit (R-LOG)
- logging Hys in V (R-HYS)
- logging a placeholder or defaulted SW/BST value
- **把 §6.2 的注释当作工位日志记录来引用或声称**（Rev 2 新增；这是 `RF-01` 的直接禁令）
- **以初值/默认值顶替缺失的捕获**（Rev 2 新增；与 §4 失败路径规则第 1 条一致）

---

## 7. 逐阶段 BST-SW 约束（0 V ≤ BST_actual − SW_actual ≤ 5 V）

> 规则：`team/TEAM_ARCHITECTURE_V2.md:210-227`；`knowledge/standards/rules-registry.md:44`。
> 结论摘要：**9/9 阶段为 定点补证（未证实）**，逐阶段推导与 `SW_actual` 推导见 `bst-sw-phase-check.md`。

| 阶段 | BST_actual | SW_actual | 差值与判定 | 依据 |
|---|---|---|---|---|
| P0 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | no source allocated to BST/SW; switching stage not committed by the DFT; SW deliberately not taken as 0 V |
| P1 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | no allocated source; no required state for K48/K76/K61 in the signed closure set; K57_CAP_BST_SW state ambiguous (RT-2) |
| P2 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | VBAT is a rail pin; the switching stage is not enabled by TM108's register delta (only DMUX_EN/DMUX_SEL), and no tester source drives BST/SW |
| P3 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | the delta contains no driver/switching enable; a BST/SW state still cannot be derived, and BST/SW remain unreachable by any closed relay |
| P4 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | the swept chain (VAC123_AMUX_ACM -> K18 -> K19 -> VAC1_F) is disjoint from every BST/SW route; the internal high-side/low-side commitment is not part of the DFT intent, so neither node's potential is derivable |
| P5 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | same as P4; no relay action occurs at the turn-around, so no new BST/SW coupling appears |
| P6 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | same as P4; a falling input sweep does not couple to the BST-SW pair through any closed contact of G1/G2 |
| P7 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | the collapse ordering rule for BST-SW applies only to items that drive BST; here the rail collapse cannot be shown to keep any BST/SW relation, so the constraint stays unproven |
| P8 | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | after release no node of this item is driven; BST/SW end state is again DUT-internal and unevidenced in this boundary |

**为何不能给出数值（要点，详证见 `bst-sw-phase-check.md`）**

- BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).
- BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).
- K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.
- K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.
- BST_actual: not derivable - no allocated source, no driven node, no closed contact. SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require).

---

## 8. evidence[]（本契约每条结论的定位）

| # | 文件 | 定位 | 类别 |
|---|---|---|---|
| E1 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` | 6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4 (sha256); sections :92-121 (endpoints), :125-179 (allocation), :181-252 (relay groups), :256-267 (register delta), :370-420 (open items + handoff) | dependency artifact (signed upstream contract, t4) |
| E2 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.json` | FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9 (sha256); keys resourceAllocation / relayGroups / registerDelta / resourceSummary / openItems | dependency artifact (signed upstream contract, t4) |
| E3 | `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md` | AEC7FD74A01314B856009104C721F93B11FE9490B27C0673DEA6E3F385274029 (sha256); :138-260 field table, :262-276 F1-F6, :318-337 P1-P10 | dependency artifact (t2) |
| E4 | `team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md` | 1F5996B21AE84E2E80688C88015CFEA2DD9E35F1075858C72970711A35CEF1B8 (sha256); :98-203 candidates, :205-257 relay facts, :261-274 conflicts, :301-315 open items | dependency artifact (t3) |
| E5 | `team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.json / .txt` | 6AE38A3678BA05CAA0A0840C6E274E341770FFDC5CA0E3AA4C1474B72095D821 (sha256, .json); per-terminal proof chains with contact pins, nets, state and required_on | dependency artifact (t3) |
| E6 | `project/DALI/meta/dali_tm_meta.json` | :1382-1510 (TM108 object) - READ-VISIBLE via the DFT audit, not re-read here | project fact (through t2) |
| E7 | `project/DALI/reg_config/tm108.sv` | sha256 4d0ea5c30fe5369e98a6d81215bbfb5b5f41bf44ea1c5dbc8df94af75bb92dc1; body regconfig-scope.json:35 | project fact (through t2) |
| E8 | `project/DALI/SCH-Connect-Map.txt` | :891 (nQON pull-up), :904 (SW stabiliser cap gate K57), :913 (VAC1 cap gate K21), :914 (VBAT cap gate K13), :801/:804 (low ends to AGND_F), sha256 cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427 | project fact |
| E9 | `team/artifacts/acceptance-20260916-dali10/setup-contract.json` | :130-160 (ACM200 capability +-200 mA), :3905-3964 (globalInitialization incl. cap gates and the K21 exception), :4162 (unified RELAY_OFF ranges), :5666-5671 (TM108 powerSequenceDelta), :5683-5719 (limits + BD-04), :8150-8179 (safety invariants incl. :8156, :8157, :8161, :8169, :8175, :8179) | READ-VISIBLE frozen baseline (read-only) |
| E10 | `team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt` | :390-468 (existing implemented TM108 function - corroboration for the method-side numbers only) | FACT (existing implementation, not an authority) |
| E11 | `team/artifacts/tm108-v2-trial/schematic/tm108-connectmap-ranges.txt` | :16-27, :83-91, :226-228 (BST/BST1/BST2 routes and the SW cap gate) | dependency artifact (t3, range dump) |
| E12 | `team/artifacts/tm108-v2-trial/schematic/tm108-consistency-check.txt` | :109, :173 (K61_SW dual-state record: map tokens [NC,ON], IR single value NC) | dependency artifact (t3, per-relay state matrix) |
| E13 | `knowledge/references/L3-method/UVLO.md` | :5-19 | active method knowledge |
| E14 | `knowledge/references/L1-chip/UVLO.md` | :14-29 | chip knowledge |
| E15 | `knowledge/references/L3-method/voltage-threshold-ate.md` | :5, :9-34 | active method knowledge |
| E16 | `knowledge/standards/toggle-awg-rules.md` | :12-34 | active rule |
| E17 | `knowledge/standards/functions-registry.md` | :23-31, :43 | active rule (primitive semantics) |
| E18 | `knowledge/standards/rules-registry.md` | :32-39, :44 | active rule |
| E19 | `knowledge/standards/relay-checklist.md` | :25-42, :71-75 | active rule |
| E20 | `team/ROLE_ROUTING.md` | :4-15 | team contract |
| E21 | `team/TEAM_ARCHITECTURE_V2.md` | :151-227 (method role, forced flow, BST-SW hard constraint), :268-292 (output fields and handoff) | team contract |
| E22 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.md` | this artifact — Rev 1 baseline hash in §0b; Rev 2 hash in `method/tm108-test-method-contract-rev2-note.md` (a file cannot contain its own hash) | this task's output |
| E23 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.json` | this artifact — Rev 1 baseline hash in §0b; Rev 2 hash in `method/tm108-test-method-contract-rev2-note.md` | this task's output |
| E24 | `team/artifacts/tm108-v2-trial/method/bst-sw-phase-check.md` | this task's output | this task's output |
| E25 | `team/artifacts/tm108-v2-trial/method/_build_method_contract.py` | this task's generator (reproduced Rev 1 of all three artifacts and verified the upstream hashes). **Rev 2 note: this generator was NOT modified by the `t10` repair** — it lives inside the workspace's `TSZ#` transparent-encryption container, so the Rev 2 text was applied to the published plaintext artifacts (`_finalize_method_contract.mjs`'s outputs) and Rev 2 is therefore **not** reproducible from this generator as it stands; recorded so the next re-issue does not silently assume otherwise | this task's output |
| E26 | `team/artifacts/tm108-v2-trial/method/_finalize_method_contract.mjs` | this task's publisher (writes the three artifacts as plaintext UTF-8 and verifies the round-trip; needed because interpreter-written files in this workspace are stored inside a TSZ# transparent-encryption container that plain readers cannot parse) | this task's output |
| E27 | `team/artifacts/tm108-v2-trial/review/t8-review-findings.md` / `.json` | sha256 `4700223A2A257D144B355A3FD2E8BD60B7186C6C44B996BBD7FAD67A0BF47A25` / `CC3664921CF70F74B696EC13D17157E1321401EEC1D450702841FF67A266E649`; `findings[RF-01]` (blocker, category `contract-vs-capability`, owner `test-method-expert`, repair condition (a)/(b)) and `residualRisks[RR-02]` (marked INFERENCE) | the independent review this revision answers |
| E28 | `team/artifacts/tm108-v2-trial/review/tools/out/logging.txt` / `reach.txt` / `errlog.txt` / `cparam.txt` | sha256 `F50719EBB45771A74EAD9F704D819A7810B44B1A7E89A3888B58966520CE616E` / `A63F092DBB343DEBB2E8059CA40C61ADFFB501731CCA710C088F5C3D88B46755` / `63EEAAF3ED98992BEF36D161DD8D800ADE63A4F17D9A2A300FCE9863B3C5D989` / `05115FF9B68C344D1029DF0E8A8BA0B94645698AF92E1EE653AF8E9FE9E08F19` - the reviewer's reproducible callable inventory, include-closure analysis, `TREG_ERROR` extraction and `SetTestResult` context | capability audit, §6.3 (review side) |
| E29 | `team/artifacts/tm108-v2-trial/review/copy/test.cpp` | sha256 `B79B911A65A33ABD62697F8576BD04B5022194751C9BFC5B174ECDAB96D05D5A` (477123 B), the review's byte-identical copy of the live implementation file (review gates G-01/G-02); TM108 body `:2193-2309`; `SetTestResult` 188 text hits of which 1 is inside a comment (`:1159`) | the code revision this revision was written against - **read-only; this task wrote no C++ file and did not open `D:\PROJECT6-DALI`** |
| E30 | `Library-Functions/treg/treg.h` / `Library-Functions/treg/treg.cpp` | sha256 `E10C2AC7E2B53B043467ED1579E76DE9C41BDE2B6E7D5B787A3E0D8CCC262BBC` / `AE86D1A1CDBD3EE1BAED85D3435A46CB19D5803AE97C0FAF0373E1CA91512489`, **byte-identical to the project's `source/treg.h` / `source/treg.cpp`** (hashes reproduce `reach.txt`); `treg.h:176` `treg_error_log`, `:186-199` `class TREG_LOG` with `log_data` under `private:`; `treg.cpp:191-192`, `:227-251` (console implementation), `:287/302/346-348` (`msLogData` under `#ifdef TREG_ETS364`) | capability audit, §6.3 - this task's own verification, on byte-identical copies |
| E31 | `Library-Functions/BoardCheck/BoardCheck.h` | sha256 `AD562C1C14929BBF71F5549269CE6C44C16352EB4D4299A130952F714D5D83EA`, byte-identical to the project's `source/BoardCheck.h`; `:214 class CBC_log`, `:759 log(...)`, `:760 test_log(...)`, `:778 CBC_log bc_log;` | capability audit, §6.3 |
| E32 | `team/artifacts/tm108-v2-trial/review/repair-routing-plan.md` | `:26` the routing condition for `C11`/`RF-01`: "state whether each of `CBC_log::log` / `CBC_log::test_log`, `log_data`, `treg_error_log` is reachable from a TM function; either re-issue the `logPlan` within the real capability or accept the trace-comment form explicitly" | the repair condition this revision answers |
| E33 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract-rev2-note.md` | this revision's note - Rev 1 baseline hashes and Rev 2 hashes for both artifacts, the disposition record and the capability-audit summary | this task's output |

---

## 9. openItems[]（定点补证）

| id | 级别 | 内容 | 不做什么 | 闭合所需来源 | 归属 |
|---|---|---|---|---|---|
| `OI-T5-01` | blocker-for-observation-decisions | observation endpoint identity (carried from OI-T4-01) | this contract never equates DTEST0 with nQON and does not adopt the alias that appears in the knowledge base (voltage-threshold-ate.md :5) or in the existing implementation (testcpp-blocks.txt:395) | the DFT-side device relation DTEST0 -> nQON (A2D_VAC1_PRST mux) plus the register map for DMUX_SEL=22 (contract md :374) | dft-expert (relation) + test-strategy-architect (re-allocation) + test-method-expert (method re-issue) |
| `OI-T5-02` | high | BST/SW differential constraint cannot be proven for any phase of this item | no value is guessed and no phase is silently omitted; every phase carries the derivation and the verdict | either (a) a DFT-side statement that TM108 leaves the switching stage inactive plus the resulting evidencable node potentials, or (b) the BST/SW endpoint allocation (source table, channel, observation) and its relay state, which the strategy contract must add - see RT-2 | dft-expert + test-strategy-architect + test-method-expert |
| `OI-T5-03` | medium | the method-side numeric positions in the measurement plan that are not DFT numbers | the contract states each value's provenance and the plan they live in; none is presented as a DFT fact | a DFT/method ruling on the capture level and sweep resolution, or acceptance of the recorded positions as the method's own (review can verify the provenance, not the physical optimum) | test-method-expert (with test-strategy-architect for the range/limit pair if the allocation must change) |
| `OI-T5-04` | medium | carried DFT conflicts that govern the applied numbers | nothing is silently resolved to one side; each phase names the conflict it depends on | the closings recorded in contract md :370-390 (workbook re-dump or a captain/user ruling per conflict) | dft-expert + captain (F1/F3/F4/F5/F6); dft-expert + test-strategy-architect (F2) |
| `OI-T5-05` | low | no register de-activation of the delta exists | no write is invented; the omission is recorded | a strategy/DFT statement of the intended post-item register state, or acceptance of the global cleanup contract as sufficient | test-strategy-architect + setup-architect |
| `OI-T5-06`（**Rev 2 新增**） | medium | **no station-log record mechanism exists for the 7 raw-context/context rows** - the capability gap that `RF-01` identified | the rows are **not** presented as records (they are downgraded to source-comment documentation, §6.2); no DFT parameter name is invented; no call is made to an unregistered API; the disposition is recorded rather than hidden | one of: (a) the DFT item gains the parameter(s) under which the context would be logged (a DFT/strategy-side change, and then this contract re-issues §6.1 accordingly), or (b) the framework side confirms a station-log call for free-form context with a registered declaration and semantics (the `msLogData`/`TREG_ETS364` path is the only candidate seen and is **UNKNOWN** to this task), or (c) explicit acceptance of the comment-documentation status as the sanctioned form for this project | test-strategy-architect + dft-expert (parameter path) / compile-diagnostician (framework declaration of any candidate) + test-method-expert (re-issue §6 if a mechanism is confirmed) |
| `OI-T5-07`（**Rev 2 新增**） | medium | **`rampv_capv` 的“无触发”失败语义未登记** - so the §4 failure-path rule cannot be *detected* yet | the contract states the obligation (no defaulted number may be published) and does **not** name a detection primitive, does **not** assert that the current implementation violates it, and does **not** invent a return-value convention | the primitive's registered declaration, real implementation and call semantics (declaration + `Test_Method.cpp` body), or a bench observation of a no-trigger segment. Until then `RR-02` stays an INFERENCE and this item stays open | compile-diagnostician (framework/primitive evidence) + test-method-expert (re-issue the detection wording); any resulting code change is `ate-implementer`'s once this item closes |

**承载自上游的未决项（本契约逐条带入，不取舍）**

- DFT 冲突 **F1→OI-T4-09**、**F2→OI-T4-10**、**F3→OI-T4-11**、**F4→OI-T4-12**、**F5→OI-T4-13**、**F6→OI-T4-14**：全部双侧保留；本契约在执行侧采用 DFT 意图/artifact 侧数值，并**逐阶段标注该冲突**，不做平均、不裁剪。
- **OI-T4-01/02**：观测端点身份与观测侧选择 → 本契约以 `OI-T5-01` 承载，所有依赖决定标 PENDING。
- **OI-T4-03**（通道并发）、**OI-T4-04**（K17 动作形式）、**OI-T4-05/07**（PIN 附着功能继电器覆盖）、**OI-T4-08**（AGND 资格）、**OI-T4-16/17**（基线/口径）作为约束带入，未被本契约当作已裁定。

---

## 10. 退回项（越出签名边界的需要 → 命名 owner）

| id | 退回给 | 内容 | 需要什么 |
|---|---|---|---|
| `RT-1` | **test-strategy-architect** | explicit relay state of K13 (VBAT cap gate) differs between the frozen baseline and the signed contract：The signed contract's relayGroups[G3] states that K13_VBAT_Cap must be closed (backed by relay-checklist.md :27-37 for a powered rail) while the same contract's resourceSummary.keepOpenRelayNumbers also lists 13 in the keep-open set (contract md :248, :574; contract json resourceSummary). The frozen baseline closes it (setup-contract.json:5667). This method closes it at P1 and releases it at P8, on the explicit closure-set statement and the Cap2 rule, and reports the inconsistency rather than ignoring it. | one authoritative statement of K13's state in the signed contract (or removal from the keep-open set). |
| `RT-2` | **test-strategy-architect** | K57_CAP_BST_SW state is not in the signed boundary, and no BST/SW endpoint state exists：K57 is the 220 nF BST-SW coupling cap gate (project/DALI/SCH-Connect-Map.txt:904) and appears in the baseline's global init list of cap gates (setup-contract.json:3941), but the signed contract neither closes it nor puts it in the keep-open set - so its state is not expressible from this boundary, and the contract's own rule that every scope-path relay needs an explicit state (setup-contract.json:8169) is unmet for it. This is also what makes the BST/SW constraint unevaluable (OI-T5-02). | either an explicit K57 state in the contract (closed / not-actuated / not-an-item-relay) plus the BST/SW endpoint and relay state if the differential constraint must be evaluated, or a written statement that TM108 has no BST/SW relation for this method to evaluate. |
| `RT-3` | **test-strategy-architect** | no register field exists to undo the mux activation：The delta is entertestmode + (DMUX_EN=1, DMUX_SEL=22). The method writes nothing at the end (OI-T5-05). If the item is required to leave the mux disabled, the delta needs the corresponding field and value. | a delta field for de-activation, or explicit acceptance that no de-activation is required. |
| `RT-4` | **test-strategy-architect / captain** | no tolerance is published for the threshold limits：The DFT publishes 'rising vth 4.4 V, hys 0.35 V' with no tolerance column, and the baseline records the same (setup-contract.json:5687). A pass/fail application therefore cannot be written from the method contract alone, and this contract does not invent one. | a tolerance (or a written rule for a missing tolerance) from the spec/DFT side. |
| `RT-5` | **test-strategy-architect / setup-architect** | site-level concurrency of the shared ACM200 object：VAC123_AMUX_ACM serves VAC1/VAC2/VAC3/AMUX (contract json OI-T4-03); the method assumes serial use of the site and does not add a scheduling rule. | confirmation of the implied serial schedule or a concurrency table entry. |
| `RT-6`（**Rev 2 新增**） | **test-strategy-architect**（+ dft-expert，+ compile-diagnostician 若走框架声明） | **工位日志的记录能力不足**：`RF-01` 表明本项 7 条 raw-context/context 行在签名边界内无记录机制——唯一可用的写入路径 `CParam::SetTestResult` 只能写在经 `StsGetParam(funcindex,"<名>")` 取得的 **DFT 参数**上，而本项参数只有 3 个。Rev 2 已把该 7 行降级为注释文档（§6.2）并登记 `OI-T5-06`；本条是通往边界的正式请求，**不是**要求为了让评审通过而追加电气内容。 | 二选一：(a) 该 DFT 项新增承载上下文的参数（参数名与单位由 DFT/spec 侧给出，本契约随后重发 §6.1）；或 (b) 框架侧给出一个**已登记声明与语义**的自由文本工位日志调用（候选见 §6.3 的 `msLogData`/`TREG_ETS364`，本任务无法证实）；或 (c) 明确接受“注释文档”为本项目的合规定位，并据此收掉 `OI-T5-06`。 |

> 说明：本契约**没有**为了实现方便而改动任何源表、通路、继电器、寄存器值、功能继电器或隔离条件；
> 上表是唯一通向边界的请求。

---

## 11. 交接（给实现者与校验者）

- 已定：the phase order and each phase's prerequisite / relay group / register activation / actual node table / differential checks / setpoint / ramp / delay / exit condition
- 已定：the closure set to apply ({13,65}) and the keep-open list
- 已定：the register staircase (testmode then DMUX_EN/DMUX_SEL=22 as one directive) and the deliberate absence of any de-activation write
- 已定：the two-segment measurement with the three parameters, the calculation and the units (R-HYS/R-LOG)
- 已定：the three-step power-down and the safe end state
- 已定（**Rev 2**）：`logPlan` 分两类——**3 条 calculated = 工位日志记录**，机制与字段映射见 §6.1；**7 条 raw-context/context = 源码注释文档，明文不是工位日志记录**（§6.2）
- 已定（**Rev 2**）：失败路径规则（no-trigger / boundary-trigger / negative-Hys，逐 site；不发布被替代的数；见 §4）

**未决、不得当作已定**

- OI-T5-01 / OI-T4-01 (observation endpoint identity, trigger polarity, capture level validity, DMUX_SEL=22 sufficiency)
- OI-T5-02 / RT-2 (K57 与 BST/SW 约束 - 每阶段都是定点补证)
- OI-T5-03 (方法侧数值定位) 与 OI-T5-05 / RT-3 (寄存器无反激活)
- OI-T5-06 / RT-6 (7 条上下文行没有记录机制；本版只降级为注释文档，**不等于**该缺口已闭合)
- OI-T5-07 (`rampv_capv` 的“无触发”语义未登记；§4 失败路径规则第 1 条因此**尚不可检测**，`RR-02` 仍是 INFERENCE)
- OI-T5-04 (F1-F6, all carried)
- RT-1 (K13 state statement)
- RT-4 (missing tolerance)

> Review against the signed strategy contract and this contract only; the implemented function is not an authority. Any electrical or method change must be returned to the owner of this contract, not fixed in code.
>
> **Rev 2 给复核者的口径**：`logPlan` 的一致性判据是“**3 条 calculated 必须经 §6.1 的机制发出**，且 **7 条 raw-context/context 必须是注释文档、不得被任何人声称为工位日志记录**”。
> 复核不应因为“7 条没进工位日志”而把 `RF-01` 重新判为代码缺陷——那是平台与被签边界的事实，已由 §6.3 逐候选证明并登记为 `OI-T5-06` / `RT-6`。

---

## 12. 自检

| 检查 | 结果 |
|---|---|
| 方法契约 md/json 均存在且含 methodEvidence / methodPhases / measurementPlan / powerDownPlan / logPlan / evidence / openItems | 通过（本文件与同名 JSON） |
| 每个阶段十项字段齐备（prerequisite / relayGroup / resourceState / registerActivation / actualNodeVoltages / differentialChecks / setpoint / ramp / delay / exitCondition） | 通过（§3，9 个阶段） |
| 每个数值有引用、无杜撰 | 通过（§3 逐条引用；方法侧数值经 `OI-T5-03` 登记其来源与性质） |
| 逐阶段 BST-SW 显式评价（不默认 SW=0 V） | 通过（§7 + `bst-sw-phase-check.md`，9/9 为定点补证并给出原因） |
| 观测端点未被当作已解决（`DTEST0` ≠ `nQON`） | 通过（§0、§3 P3-P6、`OI-T5-01`） |
| F1–F6 未被静默解到单侧 | 通过（§9；各阶段标注适用冲突） |
| 未新增超出签名边界的源表/通路/继电器/寄存器/功能继电器/隔离条件 | 通过（§1 边界使用 + §10 退回项） |
| 无其他 TM 内容 | 通过（全文只出现 TM108；承接项用编号引用） |
| **Rev 2**：`logPlan` 已按 `RF-01` 重发，10 条 logicalId 全部有明确归属（§6.1 记录 3 条 / §6.2 注释文档 7 条） | 通过（§6 全节重发；7 条明文声明**不是**工位日志记录） |
| **Rev 2**：能力审计逐候选给出，并对评审措辞做了一处细化（`treg_error_log` 可及但只写调试控制台） | 通过（§6.3；证据 E27–E31） |
| **Rev 2**：失败路径规则不依赖任何本项目不存在的 API（三情形 + 记录载体） | 通过（§4；缺口登记为 `OI-T5-07`，`RR-02` 保持 INFERENCE） |
| **Rev 2**：既有未决项一条未解决/未改名/未站边 | 通过（`OI-T4-01`、`OI-T5-01/02/03/05`、`RT-1`…`RT-5`、`F1`–`F6`；新增 `OI-T5-06/07`、`RT-6` 为**新增**项） |
| **Rev 2**：未引入任何电气值、继电器、寄存器、量程、limit 或容差；未写/未改任何 C++ 文件；未访问 `D:\PROJECT6-DALI` | 通过（§0b；全部证据来自工作区内字节一致副本与评审产物） |

**未做（越界声明）**：不写 C++/SDK/API/量程枚举/cbite 调用形式（ate-implementer）；不做独立评审（rule-reviewer）；不编译、不建门禁（compile-diagnostician）；不部署、不宣称硬件通过。

