# TM108 资源与配置契约（VAC1_PRST）

- runId: `tm108-v2-trial` · task: `t4` · owner: **test-strategy-architect**
- TM: **TM108** (`VAC1_PRST`, implemented symbol `TM108_HSKP_VAC1_PRST`)
- 产物（本任务唯一写入范围 `team/artifacts/tm108-v2-trial/strategy/`）：
  `tm108-resource-config-contract.md`、`tm108-resource-config-contract.json`、
  `tm108_relay_workflow.py`、`tm108-relay-workflow.txt`、`step-01..step-08-*.txt`
- 本契约**只**决定：分类 / 源表 / 通路 / 继电器组 / 寄存器 delta / 证据 / 定点补证。
  **不**决定上电、测量、下电、Log（`team/ROLE_ROUTING.md:9` 归 test-method-expert）。
- 输入（全部只读）：t2 DFT 事实审计、t3 原理图事实审计与逐条 proof、冻结 Setup 基线、
  源表定义头、active 规则与知识访问矩阵。
- **未写入任何项目文件**：`project/DALI/meta/`、`project/DALI/SCH-Connect-Map.txt`、
  `project/DALI/Component-Statistic.txt`、`project/DALI/schematic-ir.json` 全程只读；
  `D:/PROJECT6-DALI/devel` 未访问。

---

## 0. 判定摘要（一句话）

TM108 是**一般测试项目 + 阈值 AWG（toggle）+ grouped**，参数族 **UVLO**；
三个端点分别为 **VBAT**（静态供电）、**VAC1**（被扫描输入）、**DTEST0**（观测，端点身份**未证实**）；
选定资源为 **`VBAT_PD3_FXVI`(FXVIe_PLUS S3_5) + `VAC123_AMUX_ACM`(ACM200 S5_0) +
`NQON_HG1_ACM`(ACM200 S5_9，候选)**；闭合集最小到 **{K13, K65}** 功能性闭合 +
**K17 在 VAC1 支路处于闭合态**，其余通路触点全部走**默认导通**；
**不占用任何 FPVIe / QVMe / QTMUe 通道**。所有 DFT 冲突 F1–F6 与原理图 openItems 一律**登记，不裁决**。

---

## 1. projectType

| 项 | 值 | 证据 |
|---|---|---|
| 项目类型（规则判定） | **一般测试项目**（7 类判定表第 7 类） | `knowledge/standards/test-types.md:47-60`；`knowledge/references/func_type_index.md:20` |
| 证据层标注 | `projectType=一般测试项目(AWG)` | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:146`；`team/artifacts/acceptance-20260916-dali10/dft-raw/meta-refs-dump.txt:337-341` |
| 函数架构族 | **toggle（阈值 AWG）+ grouped** | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:146`；`team/artifacts/acceptance-20260916-dali10/setup-contract.json:5314-5318` |
| Trim 判定 | **否**（不触发 Trim 框架） | `project/DALI/meta/dali_tm_meta.json:1395`；`project/DALI/meta/test_conditions.yaml:268`；`team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:47` |
| 大电流判定 | **否** | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:151`（`mi_pins: []`）；`project/DALI/meta/dali_tm_meta.json:1494`（`currentStimuli: []`） |
| 差分判定 | **否**（单端数字观测） | `project/DALI/meta/dali_tm_meta.json:1402`；`project/DALI/meta/dali_tm_meta.json:1426-1428` |
| 其他类别（Contact/OTP/P2P/Leakage） | **否**（DFT 无相应字段） | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:147-168` |

判定依据链（命中即停）：无 “Trim” 字样、Trim 判定列非 Y、参数名不与 treg 同名 →
排除第 1 类；无 OS/Kelvin 指令 → 排除第 2 类；无 Pre/Post Readback → 排除第 3/4 类；
无 P2P/leakage → 排除第 5/6 类；落入第 7 类。规则出处 `knowledge/standards/test-types.md:47-60`。

---

## 2. parameterType

**参数族 = UVLO**（阈值参数族：ramp 电压 → 观测脚翻转）。

| 项 | 值 | 证据 |
|---|---|---|
| 证据层 `paramType` | `UVLO` | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:146` |
| 被测可观察量 | `VAC1_PRST`（rise / fall / hys 三段） | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:147`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:151` |
| 命名契约 | `<基名>_Rise / _Fall / _Hys`，`Hys = Rise − Fall` | `knowledge/standards/toggle-awg-rules.md:14-26` |
| ramp 调用数 | 2（升+降），故 3 参数规则**适用** | `project/DALI/meta/dali_tm_meta.json:1459-1471`；`project/DALI/reg_config/tm108.sv:17-26` |
| trigger 方向 | 升扫 → 观测下降沿（观测脚反相）；降扫 → 观测上升沿 | `knowledge/standards/toggle-awg-rules.md:28-30`；`knowledge/references/L3-method/voltage-threshold-ate.md:26-32` |
| 权威限值 | `rising vth 4.4V, hys 0.35V` / 单位 V | `project/DALI/meta/dali_tm_meta.json:1390`；`project/DALI/meta/test_conditions.yaml:263`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:152` |
| 容差 | **任何 DFT 源均未给出** | `project/DALI/input/DFT-full.json:5-18`（表头无容差列） |
| 参考四件套 | `L1-chip/UVLO.md` + `L3-method/UVLO.md` + `L4-Golden-code/UVLO.cpp`（PRST 阈值 AWG） | `knowledge/references/param_type_index.md:20`；`knowledge/references/L4-Golden-code/UVLO.md` |

> ⚠ 限值存在未决冲突 **F1**（CSV 层写 4.15 V）：见 §9 `OI-T4-09`，本契约不取舍。

---

## 3. functionArchitecture

```
TM108 (VAC1_PRST)
├─ 主函数：一个 VAC1 阈值项，单端数字观测，一次 DMUX 寄存器配置
├─ 子结构：
│   ① VBAT 静态供电（DFT Power 列指定）
│   ② VAC1 双向线性扫描（两段 = 两次 ramp 调用 = 3 个结果参数）
│   ③ 观测端点的数字翻转捕获（端点身份未证实 → 候选）
│   ④ 寄存器 delta：entertestmode + (DMUX_EN=1, DMUX_SEL=22)
└─ 不涉及：Trim / treg / OTP / 大电流 / 差分 / AWG 电流扫描
```

| 判定 | 值 | 证据 |
|---|---|---|
| 是否需要 AWG | **需要** | `project/DALI/meta/dali_tm_meta.json:1459-1471`；`project/DALI/meta/dali_tm_meta.json:1496-1498`；`project/DALI/reg_config/tm108.sv:18`、`:23` |
| 是否需要差分 | 否 | `project/DALI/meta/dali_tm_meta.json:1426-1428`（`checkLines` 长度 1） |
| 是否需要大电流 | 否 | `project/DALI/meta/dali_tm_meta.json:1494` |
| 是否需要组合（composition） | 否（单端点扫描 + 单观测） | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:159-161` |
| 观测链路意图 | DFT Notes 明写 `mux A2D_VAC1_PRST to dtest0` | `project/DALI/meta/dali_tm_meta.json:1396` |

**能力边界（本契约不越界）**：只给出资源与继电器边界；上电/测量/下电/Log 由 test-method-expert
在 `team/ROLE_ROUTING.md:9` 与 `team/TEAM_ARCHITECTURE_V2.md:151` 的边界内决定。

---

## 4. endpointRequirements[]（端点需求清单 · 八步流程 ①）

| PIN | 角色 | 需求 | DFT 依据 | 证据（path:line） | 状态 |
|---|---|---|---|---|---|
| `VBAT` | power | 静态直流供电，仅 force，无 sense 需求，不测电流 | Power 列 = `VBAT` | `project/DALI/meta/dali_tm_meta.json:1400`；`project/DALI/meta/dali_tm_meta.json:1420-1422`；`project/DALI/meta/test_conditions.yaml:255`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:159` | 已定资源；设定值冲突 F4 另记 |
| `VAC1` | dynamic（被扫描） | 双向 force ramp；原理图侧该 PIN 的 proof 同时给出 force/sense 两端 | Dynamic 列 = `VAC1` | `project/DALI/meta/dali_tm_meta.json:1401`；`project/DALI/meta/dali_tm_meta.json:1423-1425`；`project/DALI/meta/test_conditions.yaml:259`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:160` | **已定资源** |
| `DTEST0` | check / 观测 | 数字翻转观测端点（DFT 写的是芯片内部节点名） | Check 列 = `V(DTEST0)` | `project/DALI/meta/dali_tm_meta.json:1402`；`project/DALI/meta/dali_tm_meta.json:1426-1428`；`project/DALI/meta/test_conditions.yaml:267`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:161`；`team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:148` | **未解决 → 定点补证 `OI-T4-01`** |
| `AGND` | 参考回流 | 板级参考；ACM200 / FXVIe_PLUS 的 Low 端分组接 AGND_F，单端 force 经此闭合 | DFT 无 AGND 列，仅拓扑事实 | `project/DALI/SCH-Connect-Map.txt:801`；`project/DALI/SCH-Connect-Map.txt:804`；`project/DALI/Component-Statistic.txt:453` | 仅参考，不分配资源；资格未证实 `OI-T4-08` |
| `KLV1` | 本项不需要 | 不分配资源 | DFT 行无 KLV1 列/无 ramp/无测量 | `team/artifacts/acceptance-20260916-dali10/setup-contract.json:5319-5325`；`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:147-168` | 候选通路存在但本项不用（`project/DALI/SCH-Connect-Map.txt:78-79`） |
| `KLV2` | 本项不需要 | 不分配资源 | 同上 | `team/artifacts/acceptance-20260916-dali10/setup-contract.json:5319-5325`；`project/DALI/SCH-Connect-Map.txt:84-85` | 同上 |

### 4.1 DTEST0 专项（必须登记，不得假设）

- **实测（本次重扫）**：`DTEST0` 在 `project/DALI/SCH-Connect-Map.txt`、
  `project/DALI/Component-Statistic.txt`、`project/DALI/schematic-ir.json`、`project/DALI/input/PINLIST.txt`
  的命中数**均为 0**（复现命令与输出见 `team/artifacts/tm108-v2-trial/strategy/step-08-closure_set.txt`）。
- **原理图侧唯一的可观测端点**是 `nQON`（`NQON_HG1_ACM` 端口组）：
  `project/DALI/Component-Statistic.txt:114`；`project/DALI/Component-Statistic.txt:405`；
  `team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:172`；`team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:270`。
- **本契约不假设 `DTEST0 == nQON`**：`resourceAllocation[RA-5]` 的 `status` 字段明写
  `CANDIDATE ONLY`，并要求该关系被闭合后才能被下游消费。
- 对照侧读法（CSV 层 `Check = INT`）同样只登记不取舍：`team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:52`；`team/artifacts/acceptance-20260916-dali10/dft-raw/DFT-full.json:136`。

### 4.2 force / sense / functional 需求归类

| 端点 | force | sense | monitor / functional |
|---|---|---|---|
| VBAT | `VBAT_PD3_FXVI` S3_5 | 同一对象的 SH5（同 net 回读） | **功能性继电器**：`K13_VBAT_Cap`（加电轨稳压电容门，`project/DALI/SCH-Connect-Map.txt:914`；`knowledge/standards/relay-checklist.md:31-38`） |
| VAC1 | `VAC123_AMUX_ACM` S5_0 FH0 | 同通道 SH0 | **不闭** `K21_VAC_Cap`（被扫描输入，`project/DALI/SCH-Connect-Map.txt:913`；`team/artifacts/acceptance-20260916-dali10/setup-contract.json:3955`） |
| 观测（候选 nQON） | — | 同通道 FH9 | **功能性继电器**：`K65_nQON_PU`（开漏观测的 5 V 上拉，`project/DALI/SCH-Connect-Map.txt:891`） |

---

## 5. resourceAllocation[]（八步流程 ②③④）

判定规则：**③ 分流**（`knowledge/references/L3-method/relay-design-flow.md:43-48`；
`knowledge/references/L3-method/path-principles.md:6`）——本项无差分对、无大电流、无 >200 mA 需求，
故走**非稀缺源表分支**（ACM200 / FXVIe_PLUS），稀缺源（FPVIe / QVMe）保留给差分与大电流项目。
**④ 最短通路**按 "需闭合继电器**并集数**升序"（`knowledge/references/L3-method/path-principles.md:8`；
`knowledge/references/L3-method/relay-design-flow.md:50-51`）。

| id | 端点 | 侧 | 源表对象（已定义） | 源表类型 | 端口 | 通道 | 选定通路 | 并集 | 排名 |
|---|---|---|---|---|---|---|---|---|---|
| RA-1 | VAC1 | force | `VAC123_AMUX_ACM` | ACM200 | `S5_ACM200_FH0` | `S5_0` | `S5_ACM200_FH0 → K18(NC) → K19(NC) → VAC1_F` | `[]`（0） | 1 |
| RA-2 | VAC1 | sense | `VAC123_AMUX_ACM` | ACM200 | `S5_ACM200_SH0` | `S5_0` | `S5_ACM200_SH0 → K18(NC) → K19(NC) → VAC1_S` | `[]`（0） | 1 |
| RA-3 | VBAT | force | `VBAT_PD3_FXVI` | FXVIe_PLUS | `S3_FXVIe_PLUS_FH5` | `S3_5` | `S3_FXVIe_PLUS_FH5 → K8(NC) → VBAT_F` | `[]`（0） | 1 |
| RA-4 | VBAT | sense | `VBAT_PD3_FXVI` | FXVIe_PLUS | `S3_FXVIe_PLUS_SH5` | `S3_5` | `S3_FXVIe_PLUS_SH5 → K8(NC) → VBAT_S` | `[]`（0） | 1 |
| RA-5 | 观测（候选） | observation | `NQON_HG1_ACM` | ACM200 | `S5_ACM200_FH9` | `S5_9` | `S5_ACM200_FH9 → K64(NC) → nQON_F` | `[]`（0） | 2（rank1 被排除） |

### 5.1 源表对象存在性（每个对象都能在**源表定义头**里精确指认）

| 源表对象 | 类型 | 通道宏定义（path:line） | 对象声明（path:line） | 端口→器件映射（path:line） |
|---|---|---|---|---|
| `VAC123_AMUX_ACM` | ACM200 | `project/DALI/Pin_Channel_define.h:15` (`_PIN_CHANNEL_DEFINE_VAC123_AMUX_ACM_ = "S5_0,S6_0,S11_0,S12_0,S21_0,S22_0,S27_0,S28_0"`) | `project/DALI/Pin_Channel_define.h:96` (`extern ACM200 VAC123_AMUX_ACM;`) | `project/DALI/Component-Statistic.txt:382`；`project/DALI/Component-Statistic.txt:319`；`project/DALI/Component-Statistic.txt:408` |
| `VBAT_PD3_FXVI` | FXVIe_PLUS | `project/DALI/Pin_Channel_define.h:12` (`_PIN_CHANNEL_DEFINE_VBAT_PD3_FXVI_ = "S3_5,S4_5,S13_5,S14_5,S19_5,S20_5,S29_5,S30_5"`) | `project/DALI/Pin_Channel_define.h:93` (`extern FXVIe_PLUS VBAT_PD3_FXVI;`) | `project/DALI/Component-Statistic.txt:308`；`project/DALI/Component-Statistic.txt:833-834` |
| `NQON_HG1_ACM` | ACM200 | `project/DALI/Pin_Channel_define.h:24` (`_PIN_CHANNEL_DEFINE_NQON_HG1_ACM_ = "S5_9,S6_9,S11_9,S12_9,S21_9,S22_9,S27_9,S28_9"`) | `project/DALI/Pin_Channel_define.h:105` (`extern ACM200 NQON_HG1_ACM;`) | `project/DALI/Component-Statistic.txt:405`；`project/DALI/Component-Statistic.txt:431`；`project/DALI/Component-Statistic.txt:114` |

> 备选（未选用）对象的定义同样精确可指认：
> `FPVI0` = `project/DALI/Pin_Channel_define.h:39` + `project/DALI/Pin_Channel_define.h:120`；
> `FPVI1` = `project/DALI/Pin_Channel_define.h:40` + `project/DALI/Pin_Channel_define.h:121`；
> `QVM_S1` = `project/DALI/Pin_Channel_define.h:41` + `project/DALI/Pin_Channel_define.h:122`；
> `QTMU_S1` = `project/DALI/Pin_Channel_define.h:49` + `project/DALI/Pin_Channel_define.h:130`。

### 5.2 每个端点的候选通路与排除理由（逐条 proof 派生）

**VAC1_F_S1（5 条 accepted proof）**

| 排名 | 源端 | 并集（required_on） | 完整继电器链 | 处置 |
|---|---|---|---|---|
| 1 | `S5_ACM200_FH0` | `[]` | `K18(NC) → K19(NC)` | **选用**（RA-1） |
| 2 | `S1_FPVIe_FL0` | `[17]` | `K89(NC) → K17(ON) → K18(NC) → K19(NC)` | 备选 G4（占用 FPVIe0） |
| 3 | `S10_CH0_B` | `[17,142]` | `K142(ON) → K17(ON) → K18(NC) → K19(NC)` | 排除：需 QTMU 桥 `K142`（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8158` 要求其在 FPVIe 占用时保持断开） |
| 4 | `S1_FPVIe_FH0` | `[70,87,90]` | `K87(ON) → K90(ON) → K82(NC) → K70(ON) → K18(NC) → K19(NC)` | 排除：并集最大且穿越 FPVIe0 PC 短路网（`project/DALI/SCH-Connect-Map.txt:190`；`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8154`） |
| 5 | `S1_FPVIe_FL1` | `[17,145,146]` | `K133(NC) → K146(ON) → K145(ON) → K17(ON) → K18(NC) → K19(NC)` | 排除：需 DCM 低端 BUS 继电器 |

**VAC1_S_S1（4 条）**：`S5_ACM200_SH0` `[]`（选用 RA-2）＞ `S1_FPVIe_SL0` `[17]` ＞ `S8_QVM_CH0-` `[17,138]` ＞ `S1_FPVIe_SL1` `[17,138,139]`。

**VBAT_F_S1（5 条）**：`S3_FXVIe_PLUS_FH5` `[]`（选用 RA-3）＞ `S10_CH0_A` `[7]` ＞ `S1_FPVIe_FH1` `[7]` ＞ `S1_FPVIe_FH0` `[7,143,144]` ＞ `S8_QVM_CH0+` `[7,130,136]`。
**VBAT_S_S1（4 条）**：`S3_FXVIe_PLUS_SH5` `[]`（选用 RA-4）＞ `S1_FPVIe_SH1` `[7]` ＞ `S10_CH0_A` `[7,130]` ＞ `S1_FPVIe_SH0` `[7,136,137]`。

**nQON_F_S1（6 条）**：`S24_P0` `[]` 但 **path=[]（0 步，无 net 跃迁）→ 不可用**；
`S5_ACM200_FH9` `[]`（**候选** RA-5）＞ `S10_CH0_A` `[66]` ＞ `S1_FPVIe_FH0` `[62]` ＞ `S1_FPVIe_FH1` `[66]` ＞ `S8_QVM_CH0+` `[66,130,136]`。

逐条链与 `required_on` 的原始记录：`team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.txt`、
`team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.json`，
其来源为 `project/DALI/path_proofs.json.txt`（accepted_path_proofs = 669，status PASS）。

---

## 6. relayGroups[]（八步流程 ⑤⑥⑦⑧）

**闭合集派生口径（硬约束）**：闭合集 = **per-path proof 的 `required_on` 并集 + 该 proof 的完整继电器链**；
**不**取 `schematic-ir.json` 的 `pins[].requiredRelays`（那是各 proof 的**交集**，会漏继电器——
`team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:74`）；
**不**取 `relays[].state`（单值默认/对比态，无法表达"该通路是否需闭合"——
`team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:89`、`:265`）。

**路径级触点状态语义**：`Relay-NC` = 默认导通、**不计入** `required_on`
（`project/DALI/SCH-Connect-Map.txt:4`；`project/DALI/SCH-Connect-Map.txt:8-19`）。

### G1 — VAC1 被扫描输入（升扫）

| 项 | 内容 |
|---|---|
| 通路 | `S5_ACM200_FH0 → K18(NC) → K19(NC) → VAC1_F` ／ `S5_ACM200_SH0 → K18(NC) → K19(NC) → VAC1_S` |
| force | `VAC123_AMUX_ACM`（`S5_ACM200_FH0`，通道 `S5_0`） |
| sense | `VAC123_AMUX_ACM`（`S5_ACM200_SH0`，通道 `S5_0`） |
| 通路继电器 | `K18_VAC3`（未动，默认导通，`pin3→pin2`）；`K19_VAC2`（未动，默认导通，`pin3→pin2`）；`K17_BUSL_VAC`（**须处于闭合态**，`pin3→pin4`/`pin6→pin5`） |
| 功能继电器 | 无 |
| 隔离/互斥要求 | `K21_VAC_Cap` 保持未动（`project/DALI/SCH-Connect-Map.txt:913`）；`K14_VAC1_P2P` 保持未动（`project/DALI/SCH-Connect-Map.txt:877`）；CH0 High 支路的 `K70/K87/K90/K82` 保持未动（`project/DALI/SCH-Connect-Map.txt:190`）；`K141/K142` 保持未动（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8158`） |
| 冲突状态 | **无冲突**（`K18/K19` 均处于默认态 → 以"不分叉"选中 VAC1） |
| 闭合集 | `[]`（仅需 `K17` 在闭合态） |

### G2 — VAC1 被扫描输入（降扫）

| 项 | 内容 |
|---|---|
| 通路/force/sense/继电器 | **与 G1 完全相同** |
| 冲突状态 | **无冲突**；无任何继电器的必需状态随扫描方向改变 → **不需要分时复用** |
| 说明 | 单独成组仅为让方法契约可对两段排序，闭合集与 G1 是**同一组** |

### G3 — 静态供电 + 观测通路（两次扫描前后均有效）

| 项 | 内容 |
|---|---|
| 通路 | `S3_FXVIe_PLUS_FH5 → K8(NC) → VBAT_F` ／ `S3_FXVIe_PLUS_SH5 → K8(NC) → VBAT_S` ／ `S5_ACM200_FH9 → K64(NC) → nQON_F` |
| force | `VBAT_PD3_FXVI`（`S3_FXVIe_PLUS_FH5`，通道 `S3_5`） |
| sense | `VBAT_PD3_FXVI`（`S3_FXVIe_PLUS_SH5`，通道 `S3_5`） |
| 通路继电器 | `K8_PD3`（未动，VBAT 侧，`pin6→pin7`）；`K64_HG1`（未动，nQON 侧，`pin6→pin7`） |
| 功能继电器 | `K13_VBAT_Cap`（VBAT 稳压电容门，`project/DALI/SCH-Connect-Map.txt:914`）；`K65_nQON_PU`（nQON 5 V 上拉，`project/DALI/SCH-Connect-Map.txt:891`） |
| 隔离/互斥要求 | `K8` 不得动作（否则切到 PD3）；`K64` 不得动作（否则切到 HG1）；`K141/K142` 未动；`K92_AGND_F2S` 未动；`K7_BUSH_VBAT` **本分配不使用** |
| 冲突状态 | **无冲突**（与 G1/G2 无共享继电器的状态冲突） |
| 闭合集 | **`{13, 65}`** |
| 冻结基线交叉核对 | `team/artifacts/acceptance-20260916-dali10/setup-contract.json:5666-5671`（`cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`，并明写 `K21_VAC_Cap must stay open`） |

### G4 — **备选分配**（不得与 G1–G3 同时启用）

| 项 | 内容 |
|---|---|
| 触发条件 | 仅当 ACM200 的 `VAC123_AMUX_ACM` 通道不可用时改选 |
| 通路 | `S1_FPVIe_FL0 → K89(NC) → K17(ON) → K18(NC) → K19(NC) → VAC1_F` ／ `S1_FPVIe_SL0 → K88(NC) → K17(ON) → K18(NC) → K19(NC) → VAC1_S` |
| force / sense | `FPVI0`（`S1_FPVIe_FL0` / `S1_FPVIe_SL0`，通道 `S1_0` Low） |
| 通路继电器 | `K89_KELVIN0`（未动）、`K88_KELVIN0`（未动）、`K17_BUSL_VAC`（闭合） |
| 功能继电器 | `K13_VBAT_Cap`、`K65_nQON_PU` |
| 隔离要求 | `K21`、`K70/K87/K90/K82`、`K141/K142`、`K86_KELVIN0_F`、`K130_KELVIN1_F` 全部保持未动 |
| 冲突状态 | **无冲突**：`FL0` 与 `SL0` 落在 `K17` 的两组不同触点（`pin3→pin4` = `VAC_FORCE_S1`；`pin6→pin5` = `VAC_SENSE_S1`），一次动作覆盖两侧 |
| 闭合集 | **`{17}`** |
| 代价 | 占用 **FPVIe 通道 0**（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8165`：每 site 仅 2 个 FPVIe 通道，均被差分/大电流项目占用）→ 故不作为默认 |

### 6.1 本项继电器汇总

| 类别 | 号码 | 说明 |
|---|---|---|
| **动作（必须闭）** | `13`, `65` | 功能性闭合（Cap 门 + 上拉） |
| **须处于闭合态** | `17` | VAC 低域 BUS 入口（与 VAC 支路同源，非本项新增动作） |
| **依赖默认导通** | `8`, `18`, `19`, `64`, `88`, `89` | 通路触点默认导通，不计入 `required_on` |
| **必须保持未动（隔离/互斥）** | `14`, `15`, `16`, `21`, `38`, `39`, `40`, `70`, `82`, `86`, `87`, `90`, `92`, `130`, `141`, `142` | 反短接、Cap、FPVIe PC 短路网、QTMU 桥、力感桥 |
| 冻结基线候选池（仅作参考，**未被继承**） | `17,35,37,70,73,87,89,90,136,137,138,139,141,142,143,144,145,146` | `team/artifacts/acceptance-20260916-dali10/setup-contract.json:5326-5345`；其中 `35/37/73` 属 KLV1/KLV2（本项不用） |

**通道占用**：`S5_0`（ACM200/`VAC123_AMUX_ACM`）、`S5_9`（ACM200/`NQON_HG1_ACM`，候选）、`S3_5`（FXVIe_PLUS/`VBAT_PD3_FXVI`）。
**未占用**：FPVIe（`FPVI0`/`FPVI1`）、QVMe（`QVM_S1`）、QTMUe（`QTMU_S1`）、DCM（`S24_P0` 因 proof 为空路径被排除）。

---

## 7. registerDelta[]（逐 TM 寄存器配置清单）

| 字段 | 值 | 来源 | 作用域 | 证据 |
|---|---|---|---|---|
| `entertestmode()`（前置，非字段） | 配寄存器前调用 | DFT `.sv` + DFT `en_tm[]` | 本项 delta | `project/DALI/reg_config/tm108.sv:12`；`project/DALI/meta/dali_tm_meta.json:1441-1443`；规则 `knowledge/standards/register-config.md:12-22`；`project/DALI/meta/test_conditions.yaml:269`（`enTm: true`）；`project/DALI/meta/dali_tm_meta.json:1509`（`hasEnTm: true`） |
| `DMUX_SEL` | `22` | 器件层 + `.sv`（`I2CWriteSameData(DEV_ADDR, 0x56, 0x16)`） | 本项 delta | `project/DALI/meta/dali_tm_meta.json:1505-1507`；`project/DALI/meta/test_conditions.yaml:261`；`project/DALI/reg_config/tm108.sv:14`；字段清单 `project/DALI/meta/manifest.json:86` |
| `DMUX_EN` | `1` | 器件层 + `.sv`（`I2CWriteSameData(DEV_ADDR, 0x57, 0x08)`） | 本项 delta | `project/DALI/meta/dali_tm_meta.json:1500-1503`；`project/DALI/meta/test_conditions.yaml:261`；`project/DALI/reg_config/tm108.sv:15`；字段清单 `project/DALI/meta/manifest.json:85` |
| 一次 `field[(DMUX_EN,1),(DMUX_SEL,22)]` 指令 | 两字段同写 | DFT `Software_initial` 原样复制 | 本项 delta | `project/DALI/meta/dali_tm_meta.json:1444-1457`；规则 `knowledge/standards/register-config.md:8-11` |
| `EN_DTEST0` / `DTEST0_MUX` | `1` / `23`（**仅 CSV 层**） | CSV 层 `I2CWriteSameData(DEV_ADDR, 0x55, 0x97)` | **登记冲突，不采用** | `team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:50` |

- **全局 vs 逐 TM 边界**：全局初始化归 Setup（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:3905-3960`）；本表只写 TM108 的 delta，且**不向 Setup 回派任何逐 TM 源表决策**。
- **冲突**：`DMUX_SEL` 的 22/23 分歧即 DFT 冲突 **F2**（`OI-T4-10`），两侧证据均保留，未做平均。

---

## 8. 强制八步继电器流程执行日志（relay-design-flow.md）

流程权威：`knowledge/references/L3-method/relay-design-flow.md:39-75`。
逐步输出（可复现）：`team/artifacts/tm108-v2-trial/strategy/step-01-find_pin.txt` …
`step-08-closure_set.txt`，合并版 `team/artifacts/tm108-v2-trial/strategy/tm108-relay-workflow.txt`；
生成器 `team/artifacts/tm108-v2-trial/strategy/tm108_relay_workflow.py`（只读项目，只写本目录）。

| 步 | 动作 | 本项执行结果 | 输出文件 |
|---|---|---|---|
| ① 找 PIN | 从 DFT 提取 Power/Dynamic/Check/force/sense/功能 PIN | VBAT、VAC1、DTEST0（观测，身份未证实）；AGND 仅板级参考；KLV1/KLV2 不需要 | `step-01-find_pin.txt` |
| ② 找通路 | 在原理图三件套中列每端点到候选源表的所有可达路径 | VAC1_F 5 / VAC1_S 4 / VBAT_F 5 / VBAT_S 4 / nQON_F 6 / nQON_S 4 / AGND_F 4 / AGND_S 10 条 accepted proof，逐条含完整继电器链 | `step-02-find_path.txt` |
| ③ 分流选源 | 差分或大电流 → FPVI/QVM；否则非稀缺源 | **无差分、无大电流 → 非稀缺分支**（ACM200/FXVIe_PLUS）；FPVIe/QVMe 保留 | `step-03-source_split.txt` |
| ④ 最短通路选择 | 按需闭合继电器**并集数**升序；组合 PIN 检查源表两端 | RA-1..RA-5 全部 rank1 = 并集 0；`S24_P0` 因空路径被剔除 | `step-04-shortest_path.txt` |
| ⑤ 局部冲突处理 | 分时复用 → 第二短通路 → 保电流弃差分 → 定点补证 | 6 条局部分析（LC-1..LC-6）全部"无冲突"；**未触发任何降级分支** | `step-05-local_conflict.txt` |
| ⑥ 全局冲突检查 | 多源/共享 BUS/非目标 PIN/回灌/功能继电器/资源占用 | 8 条全局检查（GC-1..GC-8）全部通过；`K17/K62` 的 BUS 共享、`K141/K142` 桥、无 FPVIe 占用均成立 | `step-06-global_conflict.txt` |
| ⑦ 闭合分组 | 有冲突才按阶段拆多组；否则一组 | 无继电器必需状态随阶段改变 → **闭合集只有一个**；记录 G1/G2/G3（+备选 G4）供方法侧排序 | `step-07-closure_grouping.txt` |
| ⑧ 输出闭合集 | 每组列完整闭合集、断开要求与用途 | 最终闭合集写入本契约 §6 与 JSON `relayGroups[]`；`cbite.SetOn` 调用形式属实现侧（`relay-design-flow.md:115`：分时场景禁止把两组并进一次 SetOn） | `step-08-closure_set.txt` |

**局部冲突处理明细（⑤）**

- **LC-1** VAC1 的 F/S 同一分支：`S1_FPVIe_FL0` 与 `S1_FPVIe_SL0` 经 `K17` 分别落到 `VAC1_F`/`VAC1_S`
  （`project/DALI/SCH-Connect-Map.txt:193-194`）→ 一次动作覆盖两侧，无冲突。
- **LC-2** CH0 High 与 CH0 Low 分支：High 需 `K70/K87/K90`（`project/DALI/SCH-Connect-Map.txt:190`），
  Low 仅需 `K17`（`project/DALI/SCH-Connect-Map.txt:193`）→ **丢弃** High 分支（不是合并）。
- **LC-3** `K8` 的 VBAT/PD3 二选一：VBAT 侧默认导通（`project/DALI/SCH-Connect-Map.txt:832-834`），
  PD3 侧需 ON（`project/DALI/SCH-Connect-Map.txt:814-816`）→ 本项只用 VBAT。
- **LC-4** `K64` 的 nQON/HG1 二选一：nQON 侧默认导通（`project/DALI/SCH-Connect-Map.txt:242-244`），
  HG1 侧需 ON（`project/DALI/SCH-Connect-Map.txt:469-470`）→ 本项观测 nQON，`K64` 不得动作。
- **LC-5** 观测 F/S 两侧不可同时使用（DFT 只给一个单端检查）→ 登记 `OI-T4-02`。
- **LC-6** VAC1（扫描）与 VBAT（静态）链**不相交** → 不需分时复用，一组闭合集覆盖全程。

**全局冲突检查明细（⑥）**

- **GC-1** `K17_BUSL_VAC_S1` 为 `[BUS]`（`project/DALI/Component-Statistic.txt:441`），被 VAC1/VAC2/VAC3、
  AMUX、VAC_WL 共用（`project/DALI/SCH-Connect-Map.txt:192`、`:198`、`:204`、`:36`）→ 同时排除其它 VAC 功能，
  本项只选一路且 `K18/K19` 未动。
- **GC-2** `K62_BUS_FH_QON_S1`/`K62_BUS_SH_QON_S1` 为 `[BUS]` 且与 HG1 共用
  （`project/DALI/Component-Statistic.txt:441`、`:457`；`project/DALI/SCH-Connect-Map.txt:469-470`）→ 由 LC-4 消解。
- **GC-3** `K141/K142` 桥接两片 FPVIe BUS，冻结基线要求在 FPVIe 占用时保持断开
  （`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8158`）→ 本分配不使用，要求满足；
  同时使 QTMU 备选不可接受。
- **GC-4** `K21_VAC_Cap` 必须保持未动（`project/DALI/SCH-Connect-Map.txt:913`；
  `team/artifacts/acceptance-20260916-dali10/setup-contract.json:3955`），`K13_VBAT_Cap` 必须闭合
  （`project/DALI/SCH-Connect-Map.txt:914`；`knowledge/standards/relay-checklist.md:31-38`）→ 不同 PIN，无冲突。
- **GC-5** 反短接：`K14`（`project/DALI/SCH-Connect-Map.txt:877`）、`K38`（`:882`）、`K39/K40`（`:872-873`）、
  `K92`（`project/DALI/Component-Statistic.txt:453`）保持未动
  （`team/artifacts/acceptance-20260916-dali10/setup-contract.json:3920-3937`）。
- **GC-6** 无非目标 PIN 连入：本项所用每条 proof 的 `validation` 均为 `terminal_stop=true` + `role_match=true`；
  被拒 proof 全部是角色不匹配（Force 口落在 Sense 端），非拓扑缺失
  （`team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:85`）。
- **GC-7** `K13`/`K21` 为 `_S1S2` site 共同继电器（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8167`）→ 调度约束。
- **GC-8** 资源预算：本项**占用 0 个 FPVIe 通道**（`team/artifacts/acceptance-20260916-dali10/setup-contract.json:8165`），不与 mOhm 项目争用。

---

## 9. evidence[]（每项结论的 path:line / artifact:key 定位）

| # | 文件 | 定位 | 类别 |
|---|---|---|---|
| E1 | `project/DALI/meta/dali_tm_meta.json` | `:1382-1510`（TM108 对象全量） | READ-VISIBLE（磁盘为 `TSZ#` 包装，逻辑文本经读取工具可见） |
| E2 | `project/DALI/meta/test_conditions.yaml` | `:251-276` | READ-VISIBLE |
| E3 | `project/DALI/meta/manifest.json` | `:74-93`（rail/register 字段清单）、`:119-172`（noTest/notRun/noStimulusAndNoRamp） | READ-VISIBLE |
| E4 | `project/DALI/reg_config/tm108.sv` | `:6-31`（VBAT 3 V、entertestmode、DMUX 写、VAC1 10/0 V、delay） | FACT |
| E5 | `project/DALI/reg_config/tm108.sv` | sha256 `4d0ea5c30fe5369e98a6d81215bbfb5b5f41bf44ea1c5dbc8df94af75bb92dc1`（键 `regconfig-scope.json:33`） | FACT |
| E6 | `project/DALI/SCH-Connect-Map.txt` | `:4` 图例；`:8-19` FPVIe BUS；`:78-89` KLV；`:189-206` VAC1/2/3；`:210-212` VBAT；`:242-244` nQON；`:31`、`:257` AGND 自标非有效通路；`:406-408` CH1 Low→VAC1；`:418-420` CH1→VBAT；`:444-446` CH1→nQON；`:513-514`；`:630-631`；`:638-639`；`:654-655`；`:798-800`；`:801`；`:804`；`:814-816`；`:832-834`；`:849-850`；`:866-882`；`:891`；`:913`；`:914` | FACT |
| E7 | `project/DALI/SCH-Connect-Map.txt` | sha256 `cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427` | FACT |
| E8 | `project/DALI/Component-Statistic.txt` | `:69`；`:87`；`:114`；`:138`；`:204`；`:228`；`:256`；`:280`；`:308`；`:319`；`:342`；`:366`；`:371`；`:376-382`；`:405`；`:408`；`:431`；`:436-437`；`:439-459`（182 只继电器分类） | FACT |
| E9 | `project/DALI/Component-Statistic.txt` | sha256 `30a11536a3781bac58f10cc400cf9f9c9f0c4b32469c81cfc583eb7d475beb74` | FACT |
| E10 | `project/DALI/schematic-ir.json` | 454933 B；磁盘/密文 sha256 `7ef9d702892093a5de75031500f78a6d627e44d5130cc832be9292d2577d8bdc`；python/明文 sha256 `35fdd1582958eb6e4fd63e29da59dec63dfe19e3fd6198d8cc8b8f727a5c7ff5` | FACT（同一文件两个合法摘要，禁止混用） |
| E11 | `project/DALI/path_proofs.json.txt` | `accepted_path_proofs = 669`；本项 8 个端点的 accepted 数 5/4/5/4/6/4/4/10 | FACT |
| E12 | `project/DALI/Pin_Channel_define.h` | `:12`；`:15`；`:24`；`:39-41`；`:49`；`:93`；`:96`；`:105`；`:120-122`；`:130` | FACT |
| E13 | `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md` | `:110-260` 字段表；`:262-280` 冲突 F1–F9；`:318-337` openItems P1–P10 | 上游 t2 交付 |
| E14 | `team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md` | `:74`；`:85`；`:89`；`:94`；`:98-203`；`:205-257`；`:261-274`；`:301-315` | 上游 t3 交付 |
| E15 | `team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.txt` / `.json` | 逐端点 proof 链与 `required_on`（本契约全部闭合集的唯一来源） | 上游 t3 交付 |
| E16 | `team/artifacts/acceptance-20260916-dali10/setup-contract.json` | `:5313-5725`（tmDeltas.TM108）；`:3905-3960`（globalInitialization）；`:8150-8179`（safetyInvariants）；`:8181-8204`（conflicts）；`:8205+`（openItems） | READ-VISIBLE（冻结基线，只读） |
| E17 | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt` | `:146-151` | FACT |
| E18 | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt` | `:147-168`（TM108 行）；`:170-184`（TM108_1 变体） | FACT |
| E19 | `team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt` | `:40-54`（冲突层） | FACT |
| E20 | `team/artifacts/acceptance-20260916-dali10/dft-raw/regconfig-scope.json` | `:32-41` | FACT |
| E21 | `knowledge/references/L3-method/relay-design-flow.md` | `:39-75`；`:80-87`；`:115` | active 规则 |
| E22 | `knowledge/references/L3-method/path-principles.md` | `:6`；`:8`；`:12-15`；`:19-24`；`:28` | active 规则 |
| E23 | `knowledge/standards/relay-checklist.md` | `:8-15`；`:17-23`；`:26-40`；`:44-50`；`:52-69` | active 规则 |
| E24 | `knowledge/standards/test-types.md` | `:47-60`；`:76-86` | active 规则 |
| E25 | `knowledge/standards/toggle-awg-rules.md` | `:12-26`；`:28-34` | active 规则 |
| E26 | `knowledge/standards/register-config.md` | `:12-22` | active 规则 |
| E27 | `knowledge/references/L3-method/voltage-threshold-ate.md` | `:9-30` | active 方法 |
| E28 | `team/ROLE_ROUTING.md` | `:4-15` | 团队契约 |
| E29 | `team/TEAM_ARCHITECTURE_V2.md` | `:100-138`（继电器铁律、契约字段、交接内容） | 团队契约 |
| E30 | `team/artifacts/tm108-v2-trial/strategy/tm108-relay-workflow.txt` 及 `step-01..step-08-*.txt` | 八步流程逐步输出 | 本任务产物 |

**证据优先级**（`team/TEAM_ARCHITECTURE_V2.md:42-49`）：用户裁定 → 当前项目 DFT/原理图/Setup 事实 →
active 标准 → 已核对 Golden → 芯片知识 → 经验/归档。本契约全部结论落在前三级之内。

**0 命中不等于不存在**：`team/artifacts/acceptance-20260916-dali10/setup-contract.json:15` 明示
token 搜索必须声明拼写集合；本契约对 `DTEST0` 的 0 命中结论**已同时检索 `DTEST`/`dtest`**
（见 `step-08-closure_set.txt`），并仍按"未证实"登记而非断言不存在。

---

## 10. openItems[]（定点补证）

| id | 级别 | 内容 | 不做什么 | 闭合所需的确切来源 | 归属 |
|---|---|---|---|---|---|
| `OI-T4-01` | blocker（观测端点） | `DTEST0` 在三件套 + PINLIST 命中 0，`DTEST0 → nQON` 关系**无原理图证据** | **不假设** `DTEST0 == nQON`；`RA-5` 标 `CANDIDATE ONLY` | DFT 侧器件 `DTEST0`→`nQON`（A2D_VAC1_PRST）证据 + `DMUX_SEL=22` 的寄存器映射 | dft-expert（关系）+ 本角色（复分配） |
| `OI-T4-02` | medium | 观测用 nQON 的哪一侧（F 侧 `K62_BUS_FH_QON` / S 侧 `K62_BUS_SH_QON`）未定 | 不同时闭两侧 | 同 `OI-T4-01`，或队长裁定 | 本角色 |
| `OI-T4-03` | medium | `VAC123_AMUX_ACM` 同时服务 VAC1/2/3 与 AMUX，同 site 并发不可判 | 不做并发假设（隐含串行） | 冻结基线的通道并发表或裁定 | setup-architect + captain |
| `OI-T4-04` | medium | `K17` 在 VAC 支路被印为"Relay-ON"，是否需显式动作不可判（同一发布还把 `K82` 漏列入组头、把 `K18` 多算——`schematic-fact-audit.md:266`） | 只要求"处于闭合态"，不裁决来源 | `CSV_CONNECTIVITY.NET` net 级复核或修正后的生成器 | schematic-expert + ate-implementer |
| `OI-T4-05` | low | `K65_nQON_PU` 的默认态未在图内印出 | 只按功能需求要求闭合，不断言默认态 | `R_nQON_PU_S1` 的 net 复核 | schematic-expert |
| `OI-T4-06` | medium | `S24_P0 → nQON_F_S1` 的 proof 为 `path=[]`（0 步），且 `S24_Pn` 双身份 | 该端口被排除 | `CSV_CONNECTIVITY.NET` / `Dali-SCH.csv` net 复核 | schematic-expert |
| `OI-T4-07` | medium | `K13`/`K65` 属"PIN 附着继电器"——**不出现在任何 `required_on`**，通路检查覆盖不到（`setup-contract.json:8156`） | 不以 proof 充当其证据；改用功能规则 + 基线 `powerSequenceDelta` | 覆盖 PIN 附着继电器的 relay-trace 门禁 | 本角色 + compile-diagnostician |
| `OI-T4-08` | low | `AGND` 端点资格（封装脚 vs 板级参考）未证实；`AGND_S` 自标"非有效通路" | 不向 AGND 分配源表、不为它闭任何继电器 | 器件引脚表 + 封装图核对 | schematic-expert + setup-architect |
| `OI-T4-09` | **high（DFT 冲突 F1）** | 上升阈值 `4.4 V` vs `4.15 V` | **不取舍、不平均** | 用户/队长裁定，或当前工作簿 OVERVIEW 第 15 行与对应 CSV 行的重导出 | dft-expert + captain |
| `OI-T4-10` | medium（F2） | `DMUX_SEL`/`DTEST0_MUX` = `22` vs `23` | 两侧均登记，均不单独作为权威 | 工作簿 `SETTING_MAP`/`DTESTMAP` 或 `.sv` 生成器用的寄存器映射 | dft-expert + 本角色 |
| `OI-T4-11` | **high（F3）** | 观测脚身份 `V(DTEST0)` vs `Check = INT` | 两侧均登记；分配保持"候选" | 工作簿 `DTESTMAP` 与当前 DFT CSV 的 `Check` 列 | dft-expert + captain |
| `OI-T4-12` | medium（F4） | VBAT 设定值 `3 V` vs `4.2 V`（冻结基线亦登记同一分歧） | 不平均；契约保留两侧 | 队长/用户裁定（与基线同一处置） | captain + dft-expert |
| `OI-T4-13` | **high（F5）** | VAC1 动态范围三方分歧：`0→10→0 V` vs `3~5 V @1 V/ms` vs `3.8→4.4→4.1→3.5 V` | 本契约的资源分配对量程不敏感（ACM200 通道族覆盖），故分配在任一裁定下均成立；**ramp 本身不由本契约决定** | 队长裁定（Code 列 vs Notes 句） | captain + dft-expert |
| `OI-T4-14` | medium（F6） | DFT 内部时序自相矛盾：Notes `3~5 V @1 V/ms` vs `Code2` 10 V/1e-3 s | 逐字记录，不做调和 | 工作簿 ramp 意图或裁定 | dft-expert + captain |
| `OI-T4-15` | low | `TM108_1`（`VAC1_PRST_DMO_A`）变体是否在范围内（其 `.sv` 另有 `0x71=0x3B` 写） | 本契约只覆盖 TM108，不合并变体内容 | 队长裁定 | captain + dft-expert |
| `OI-T4-16` | low | 冻结基线 `tmDeltas.TM108` 的 `scopePins` 含 KLV1/KLV2、`relaySet` 含 KLV/FPVIe/DCM 继电器，与本契约逐端点复推导结果不完全一致 | **不写 Setup、不回派逐 TM 决策**；仅登记供基线 owner 对账 | setup-architect 的基线重整任务 | setup-architect + captain |
| `OI-T4-17` | low | 继电器状态发布双口径（图内 `Relay-NC` vs IR 单值 `state`，41 只双态） | 本契约自定口径：闭合集取自 proof，每个继电器给显式状态；**不读** `pins[].requiredRelays`、**不读** `relays[].state` | 本契约给出策略侧口径；IR 侧改为引用 proof | 本角色 + schematic-expert |

**DFT 冲突 F1–F6 逐条承载**：F1→`OI-T4-09`、F2→`OI-T4-10`、F3→`OI-T4-11`、F4→`OI-T4-12`、
F5→`OI-T4-13`、F6→`OI-T4-14`。**没有任何一条被静默解到单侧**（对照
`team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md:262-276`）。

**原理图 openItems 承载**：`OI-1`→`OI-T4-17`、`OI-6`→`OI-T4-01`、`OI-7`→`OI-T4-05`/`OI-T4-07`、
`OI-9`→`OI-T4-06`、`OI-10`→`OI-T4-08`、`OI-11`→§5 的选路理由；
其余（`OI-2`/`OI-3`/`OI-4`/`OI-5`/`OI-8`）为原理图侧发布口径问题，未被本契约当作事实使用
（对照 `team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md:301-315`）。

---

## 11. 交接给 test-method-expert

**已定（可直接消费）**

1. 分类：`projectType` = 一般测试项目；`parameterType` = UVLO；`functionArchitecture` = toggle AWG + grouped。
2. 端点与唯一源表/通道/通路：VBAT → `VBAT_PD3_FXVI` `S3_5`；VAC1 → `VAC123_AMUX_ACM` `S5_0`；
   观测（候选）→ `NQON_HG1_ACM` `S5_9`。
3. 闭合集：G1/G2 = `{}`（`K17` 在闭合态）；G3 = `{13, 65}`；备选 G4 = `{17}`（占用 FPVIe0）。
4. 功能继电器与隔离要求：§6 汇总表。
5. 寄存器 delta 与来源：§7。
6. 冲突、资源限制与定点补证：§10。

**作为约束带入（不得当作已裁决）**：`OI-T4-01`/`02`（观测端点：**不得**直接假定 `DTEST0 == nQON`）、
`OI-T4-03`（隐含串行调度）、`OI-T4-04`（继电器显式状态）、`OI-T4-05`/`07`（功能继电器覆盖）、
`OI-T4-08`（AGND 不作端点）、`OI-T4-09`…`OI-T4-14`（F1–F6，两侧均保留）。

**必须退回策略侧的情形**：需要 G1–G4 之外的继电器状态 / 需要更换源表或通道 /
需要 delta 之外的寄存器字段 / 需要以 `DTEST0 == nQON` 为真为前提。

---

## 12. 本任务自检

| 检查 | 结果 |
|---|---|
| 契约 md/json 均存在且含 9 个必需字段 | 通过（见文件与 §1–§10） |
| 每个 `resourceAllocation` 条目指向**源表定义头中已定义且可精确指认**的对象 | 通过（§5.1：宏定义 `Pin_Channel_define.h:12/15/24` + extern 声明 `:93/96/105`） |
| 无"无引用的范围/对象/寄存器断言" | 通过（§9 E1–E30 覆盖全部结论） |
| 闭集由 proof（`required_on` + 完整链）派生，非 `pins[].requiredRelays`、非 `relays[].state` | 通过（§6 口径声明 + 生成器 `tm108_relay_workflow.py`） |
| 每个继电器组分别列 path / force-sense / functional / isolation 并附证据 | 通过（§6 G1–G4） |
| 八步流程逐步输出齐备（含局部冲突、全局冲突、闭合分组） | 通过（§8 + `step-01..step-08`） |
| TM108 用到的全部端点 PIN 已解决或登记为定点补证（含 `DTEST0` 与 supply/force/sense） | 通过（§4；`DTEST0` → `OI-T4-01`） |
| `DTEST0` 0 命中与 `DTEST0→nQON` 未证实均已**登记而非假设** | 通过（§4.1、`OI-T4-01`） |
| 冻结 Setup 仅作只读输入；未写任何 Setup 文件；未向 Setup 回派逐 TM 决策 | 通过（`resourceSummary.setupBaselineUsage`；§7 边界声明） |
| DFT 冲突 F1–F6 全部作为 openItems 承载，未静默解到单侧 | 通过（§10 承载表） |
| 无其他 TM 内容 | 通过（正文只出现 TM108；`TM108_1` 仅作为 `OI-T4-15` 的范围问题被登记，未被分配） |

**未做（越界声明）**：本契约不决定上电顺序、测量方案、下电顺序、Log 字段——归 test-method-expert；
不写 C++/SDK 名称——归 ate-implementer；不做独立评审——归 rule-reviewer。
