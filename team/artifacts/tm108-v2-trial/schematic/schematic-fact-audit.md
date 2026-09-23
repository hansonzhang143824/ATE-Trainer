# TM108 阶段1 — 原理图三件套与候选通路独立事实审计（仅 TM108）

- runId: `tm108-v2-trial`
- task: `t3`（verification，独立事实审计）
- auditor: schematic-expert
- 审计对象: `project/DALI/SCH-Connect-Map.txt`、`project/DALI/Component-Statistic.txt`、`project/DALI/schematic-ir.json`（+ 其引用的逐条证明文件 `project/DALI/path_proofs.json.txt`）
- 范围: **物理连接事实**（DUT PIN 端点、候选源端、闭合继电器全集、默认态、共享节点/BUS 共享/互斥）。**不选 TM108 通路、不选源表、不选继电器组、不选方法、不裁 DFT 阈值。**
- 结论一句话: 三件套在 **net 名 / 继电器实例名 / 通路继电器集合** 三个层面互不矛盾（99/99 relay 状态一致、逐端子通路 relay 行集是 IR 链的子集、无 `issues`）；发现的是 **1 处语义口径问题（`Relay-NC` 双义）** 与 §6 的 6 条登记冲突，**均为登记项而非改写项**；三件套**未做重解析、未被改动**（§7 前后哈希实证）。

---

## 1. Scope

**做**：三件套互检；对 TM108 相关的每个 DUT PIN（`VAC1`、`VBAT`、`nQON`、`AGND`，各 F/S 两侧）枚举候选源端与**完整闭合继电器集合**，给出默认 NC/NO 态、共享节点、BUS 共享、互斥关系，每条给 `文件:行号` 或 `artifact-key` 证据；未证实项登记为**未证实/定点补证**。

**不做**（全文遵守）：不选择 TM108 的通路/源表/继电器组/激励/上限；不评价 DFT 阈值（4.4 V vs 4.15 V 属 DFT 范围）；不涉及任何其它 TM 的通路选择；不写源码、不编译；不审计 meta 目录。

**边界合规**：`project/DALI/` 全程只读；`project/DALI/meta/` 未作为输入；`D:/PROJECT6-DALI/devel` 未访问（§7）。

---

## 2. Inputs + hashes

### 2.1 哈希口径（必须先读）

`schematic-ir.json` 是 **DLP/TSZ 透明加密文件**：PowerShell / .NET 读到**磁盘密文**（头 4 字节 `54 53 5a 23` = `TSZ#`），**只有 DLP 授权进程（python）**读到明文 JSON（`{\n "runId": "acce…`）。因此该文件有**两个合法哈希**，二者都登记、禁止混用。另两件为明文，两口径同值。

| artifact | bytes | sha256（PowerShell `Get-FileHash`，磁盘口径） | sha256（python 明文口径） | 口径一致? |
|---|---|---|---|---|
| `project/DALI/SCH-Connect-Map.txt` | 66403 | `cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427` | 同左 | 是（明文；CRLF 965） |
| `project/DALI/Component-Statistic.txt` | 29049 | `30a11536a3781bac58f10cc400cf9f9c9f0c4b32469c81cfc583eb7d475beb74` | 同左 | 是（明文；CRLF 495） |
| `project/DALI/schematic-ir.json` | 454933 | `7ef9d702892093a5de75031500f78a6d627e44d5130cc832be9292d2577d8bdc` | `35fdd1582958eb6e4fd63e29da59dec63dfe19e3fd6198d8cc8b8f727a5c7ff5` | **否**（磁盘密文 vs 明文） |
| `project/DALI/path_proofs.json.txt`（IR 引用的逐条证明源） | 2548310 | `eda90a922b2d9e68ed3ac3736986a64ba57ec4fe243701b0d7b2123796ba4863`（IR `evidence[].sha256` 引用值，本审计未重算；python 明文可读） | （未重算） | — |

- mtime：两件套 = 2026-09-16 22:30:44；`schematic-ir.json` = 2026-09-16 22:39:42。
- **路径大小写**：`project/DALI/…` 与 `Project/DALI/…` 在本机是**同一目录**（`os.path.samefile=True`，均解析为 `D:\Newtest\DSH\ATE-Coding-Plat\project\DALI`）→ 见 §6 C-4。
- IR 自校验（IR key `validation`）：`status=PASS`；10 项 `checks[]` 全 PASS（含 `cbit_traceability unmapped=0`、`accepted=669/rejected=335/pairs=219`、`determinism_vs_canonical` 两件套 `byteIdentical=true`）；`issues=[]`。
- IR 规模（python 实测）：`nets=123, paths=232, relays=101, pins=135, scope=10，pinsPerTm=UNKNOWN(UNSPECIFIED)`。
- 证明文件规模（`path_proofs.json.txt`）：`sources=112, raw_best_paths=1004, accepted_path_proofs=669, rejected_paths=335, kelvin_pairs=219, kelvin_pair_failures=0`，`status=PASS`，`issues=0`；每条 accepted proof 含 `source_port / source_meta / dut_pin / dut_net / path[]（逐继电器：relay / relay_instance / relay_number / state / from_pin / to_pin / from_net / to_net）/ required_on / cbit / validation`——**这是"闭合继电器全集"的原始权威记录**。
- DFT 侧（上游给定，未重跑）：`team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:148` = `params: [{"check": "MV", "checkPin": "DTEST0", "dftItem": "TM108"}]`；`:14`/`:146` = `TM108_HSKP_VAC1_PRST dftItem=TM108 testType=toggle projectType=一般测试项目(AWG) paramType=UVLO`。

### 2.2 本审计的可复现产物（全部在 `team/artifacts/tm108-v2-trial/schematic/`）

`tm108-sch-extract.py` → `tm108-extract.json/.txt`（取哈希、可读性判定、TM108 端子 IR 记录、关键词命中行）；
`tm108-consistency.py` → `tm108-consistency-check.json/.txt`（逐继电器状态矩阵、两件套/IR 对照）；
`tm108-perpath.py` → `tm108-perpath-compare.txt`（逐端子：map 行 vs IR 链集合差）；
`tm108-facts.py` → `tm108-facts.json/.txt`（器件端口→器件名、逐端子通路）；
`tm108-evidence.py` → `tm108-evidence-collect.txt`（定向证据行：端口映射、列头、P2P/上拉/稳压、DUT PIN→net 附注）；
`tm108-dump-map.py` → `tm108-connectmap-ranges.txt`；
`tm108-paths-proofs.py` → `tm108-paths-proofs.txt/.json`（**TM108 端子逐条 proof 的完整继电器链**）。
**全部脚本对 `project/DALI/` 只读。**

---

## 3. Artifact consistency（三件套互检）

### 3.1 三者各承载什么（先说清能力边界）

| artifact | 承载内容 | 实测规模 |
|---|---|---|
| `SCH-Connect-Map.txt` | **逐通路**：`列1..列11` 的"源端 → DUT PIN"链路，每行含继电器链与 `(Relay-ON/Relay-NC)` 令牌；`列11` 为 P2P/上拉/下拉/稳压/net 短接分类；末附 **DUT PIN → 信号 net 映射** | 966 行；带令牌行 1648 个令牌（ON 1049 / NC 599）；`需闭合` 组头覆盖 129 个 K 号 |
| `Component-Statistic.txt` | **清点与门控**：G1..G5/G1c/G1d 全 PASS；DUT PIN 69 个/136 端口；继电器 **182 只**（机械 G6K 80 + 光耦 MOS 102）按功能分类；元器件 272 个；net 295 个；**源表端口 → 器件名**映射；**源表清点（112 端口：ACM200 54 / DCM 15 / DIO 10 / FPVIe 8 / FXVIe_PLUS 20 / QTMUe 2 / QVMe 2 …）** | 495 行 |
| `schematic-ir.json` | **机读 IR**：`pins[]`（候选源端 + `requiredRelays` + 证明数）、`paths[]`（逐端子 `relayChainUnion`，带每继电器状态）、`relays[]`（101 条，含单值 `state`）、`nets[]`、`validation` | 454933 B（密文） |

**能力边界（重要，已实测）**：`Component-Statistic.txt` **不含任何"默认态"清单**（`默认ON/默认NC/默认导通` 三种字样全文 0 命中；只有功能分类与门控警告）。因此"默认 NC/NO"的权威来源只有两处：**通路行令牌** 与 **proof 的 `state`/`required_on`**。另：`IR relays[]` 只有 101 条且**全部带 `dutPins`**，**不是全板 182 只清单**（§6 C-5）。

### 3.2 互检结论（逐项）

| 检查 | 方法 | 结果 |
|---|---|---|
| net 名一致 | 通路行右端 vs IR `nets[]`/`pins[].nets` | **一致**（例：`VAC1_F_S1` ↔ `NetCap1_VAC1_S1_1`；`VAC1_S_S1` ↔ `NetK19_VAC2_S1_7`；`nQON_F_S1` ↔ `NetK64_HG1_S1_7`；`VBAT_S_S1` ↔ `NetK8_PD3_S1_2`） |
| 继电器实例名一致 | 通路行 K 号 vs IR `relays[].instance` vs 组件统计功能清单 | **一致**（抽样 K7/K8/K17/K18/K19/K20/K21/K62/K64/K65/K66/K70/K82/K86-K92/K130-K146/K154/K155 全部对齐；`Component-Statistic.txt:441/443/445/447/449/451/453/459` 给出同编号同后缀实例名） |
| 继电器状态 | IR 每条 `relays[].state` 是否出现在该 K 号通路令牌中 | **99/99 一致**：IR 单值 `state` 恒能在同 K 号令牌中找到；**同 K 号既有 ON 又有 NC 的共 41 只**（IR `state` 取 NC），这 41 只的路径级状态必须看行令牌或 proof（§5.1、§6 C-1） |
| 逐端子 relay 集合 | `paths[] PIN_<terminal>.relayChainUnion` vs 以该端子结尾的通路行 K 号 | **map 行集 ⊂ IR 链**（无行令牌被 IR 丢失）；IR 链额外含 BUS 层继电器（例 `PIN_VBAT_F_S1` 链多出 130/132/136/141；`PIN_VAC1_F_S1` 链多出 142）；IR `pins[].requiredRelays` 是**各 proof 的交集**（例 VAC1_F = [17,70,87,90,142,145,146]，**缺 82/18/19**）→ **不可当闭合全集使用** |
| 与 proof 权威记录一致 | proof `path[]` 的继电器实例/pin/net 与通路行 | **一致**：每条 proof 的链与 map 行同构，且额外给出**触点脚号与 net 到 net 跃迁**（§5.3） |
| 器件端口映射 | `S*_* -> 器件名` vs IR 候选源端 | **一致**：`S5_ACM200_FH0/SH0/SL(0-5)/FL(0-11) -> VAC123_AMUX_ACM`、`S5_ACM200_FH9/SH9 -> NQON_HG1_ACM`、`S3..S30_x5 -> VBAT_PD3_FXVI`、`S10_0/CH0_A/CH0_B -> QTMU_S1 (QTMUe)`（`Component-Statistic.txt:87/91/114/144/319/342/376/377/382/405/408/431`） |
| 门控 | 两件套门控行 vs IR `validation` | **一致**（`Component-Statistic.txt:7-57` 全 PASS；IR `status=PASS`, `issues=[]`） |

### 3.3 明确的一致项（确认）

1. 三件套**同源同构**：继电器 `K<编号>_<功能>` + 站点后缀（`_S1` / `_S1S2`）；"同一 K 号两个实例（F 侧/S 侧）"是设计事实而非矛盾（`Component-Statistic.txt:449` `K86_KELVIN0_F/K86_KELVIN0_S/K130_KELVIN1_F/K130_KELVIN1_S`）。
2. IR `relays[]` 的单值 `state` 与通路令牌**同源**（不是独立证据）；**proof 的 `state` 与 `required_on` 才是"是否必须闭合"的判据**。
3. `VAC1` 的**公共结构**三件套一致：`K17_BUSL_VAC_S1`（BUS）→ 分叉 `K18_VAC3_S1`/`K19_VAC2_S1`（串联两触点，同 net `NetK18_VAC3_S1_*`）→ 末端 `NetCap1_VAC1_S1_1`(F)/`NetK19_VAC2_S1_7`(S)。
4. `nQON` 与 `HG1` 共用 `K62_BUS_FH/SH_QON` 与 `K64_HG1`（`Component-Statistic.txt:441/457`）；`nQON` 与 `HG1` 同挂 ACM200 第 9 号端口组 `NQON_HG1_ACM`（`:114/138/204/228/256/280/342/366/405/431`）。三件套对此**无分歧**。
5. 拒绝的 proof 全是**角色不匹配**（Force 口不能终止在 Sense 端子），非拓扑缺失：VAC1_F 2 条、VAC1_S 1 条、VBAT_F 2 条、VBAT_S 3 条、nQON_F 2 条、nQON_S 3 条、AGND_S 2 条（`tm108-paths-proofs.json` `rejected`）。

### 3.4 认定的不一致

- **I-1（medium，语义口径）**：`Relay-NC` 在通路图中表示"**默认导通，不需 SetOn 闭合**"（`SCH-Connect-Map.txt:4` 自述），**不是**"该继电器默认态为 NC"。IR `relays[].state` 用的是单值"默认/对比态"口径，两者**同名不同义**。证据：同一 `K8_PD3_S1` 在 VBAT 段写 `K8(Relay-NC)`（`:832-834`）、在 PD3 段写 `K8(Relay-ON)`（`:814-816`）；IR 只有一条 `state=NC`。**IR 单值态不能用于判定"某条通路是否需要闭合该继电器"**——必须用行令牌或 proof 的 `required_on`。
- **I-2（low，文件内自洽）**：`需闭合:` 组头 ≠ 该组行令牌并集：`:189` 组头缺 `K82`（该组行 `:190/:191` 含 `K82`）；`:200` 组头把 `K18` 计为需闭合（该组行 `:199/:200` 为 `K18(Relay-NC)`）。
- **I-3（low，命名）**：同一节点两种书写：`VAC1_F`(`:190`) / `VAC1`(`:631`)、`VBAT_F`(`:833`) / `VBAT`(`:514`)、`AMUX_F`(`:34`) / `AMUX`(`:460`)、`AGND_S`(`:32`) / `AGND`(`:854`)；`Component-Statistic.txt:486/491` 的 net 清单只登记基名，`:924-966` 另登记用户确认的短接/TP 映射。
- **I-4（low，说明性）**：IR `validation.adapterPathResolutionNote` 称 `Project/DALI` 与 `project/DALI` 为不同目录；实测为**同一目录**（`samefile=True`）。
- **I-5（low，计数口径）**：IR `relays[]`=101（全带 `dutPins`）≠ 全板 182 只（`Component-Statistic.txt:439`）。
- **I-6（medium，未证实）**：DFT 检查脚 `DTEST0` 在三件套中 **0 命中**（`SCH-Connect-Map.txt`、`Component-Statistic.txt` 全文检索；IR `pins[]` 135 与 `paths[]` 232 中亦无 `DTEST`）。

---

## 4. TM108 endpoint access（逐 DUT PIN 的候选源端与闭合继电器全集）

数据来源三层并行列证：**map 行**（`文件:行号`）、**IR**（`artifact-key`）、**proof**（`path_proofs.json.txt` 的 `dut_pin/required_on/path[]`）。括号内为该条通路的 `required_on`（需 SetOn 的继电器号）；`state=NC` 的触点为默认导通、不列入 `required_on`。

### 4.1 `VAC1`（被扫描输入）

**F 侧 = `VAC1_F_S1`（net `NetCap1_VAC1_S1_1`，5 条 accepted proof）**

| 候选源端 | 完整继电器链（触点脚 + 状态） | `required_on` | map 行 | 配对 |
|---|---|---|---|---|
| `S1_FPVIe_FH0`（CH0 Force-High） | `K87_KELVIN0`(ON,3→4) → `K90_PC0_Force`(ON,3→4) → `K82_R_CS`(**NC**,3→2) → `K70_VAC_F`(ON,1→2) → `K18_VAC3`(**NC**,3→2) → `K19_VAC2`(**NC**,3→2) | [70, 87, 90] | `SCH-Connect-Map.txt:190` | Kelvin F（与 `:191` 的 `S1_FPVIe_SH0` 成对） |
| `S1_FPVIe_FL0`（CH0 Force-Low） | `K89_KELVIN0`(NC,3→2) → `K17_BUSL_VAC`(ON,3→4) → `K18`(NC) → `K19`(NC) | [17] | `:193` | Kelvin F（与 `:194` 的 `S1_FPVIe_SL0` 成对） |
| `S1_FPVIe_FL1`（CH1 Force-Low） | `K133_KELVIN1`(NC,3→2) → `K146_DCM_BUS1_L`(ON,2→1) → `K145_DCM_BUS0_L`(ON,1→2) → `K17`(ON) → `K18`(NC) → `K19`(NC) | [17, 145, 146] | `:407` | Kelvin F（与 `:408` 的 `S1_FPVIe_SL1` 成对） |
| `S5_ACM200_FH0`（ACM200 CH0 F 侧；器件 net 名 `VAC123_AMUX_ACM`） | `K18`(NC) → `K19`(NC) | **[]（全默认导通，无需 SetOn）** | 无独立行（列6 未单列 VAC1） | 见下 `S5_ACM200_SH0` |
| `S10_CH0_B`（QTMUe；`Component-Statistic.txt:377` 记 `S10_CH0_B -> QTMU_S1`） | `K142_QTMU_BUSB`(ON,3→4) → `K17`(ON) → `K18`(NC) → `K19`(NC) | [17, 142] | 无独立行（列8 只列 VDM/nQON） | QTMU 不分 Kelvin（`:846`） |

- 被拒证明（角色不符）：`S1_FPVIe_SH0`、`S1_FPVIe_SL0`（`tm108-paths-proofs.json` → `rejected.VAC1_F_S1`）。
- **并联/分叉结构（同一族 relay 可被多源端共用）**：`S5_ACM200_FH0` 与 `S10_CH0_B` 都在 **`K18(3)`/`K18(2)`、`K19(3)`/`K19(2)` 触点**上汇入；`S1_FPVIe_FL0` 经 `K17(3→4)`、`S1_FPVIe_FL1` 经 `K17(3→4)`、`S10_CH0_B` 经 `K17(3→4)`，而 `S1_FPVIe_FH0` 经 `K70(1→2)`，**两族在 `VAC_FORCE_S1` net 汇合**——即 `VAC_FORCE_S1` 是共享节点。

**S 侧 = `VAC1_S_S1`（net `NetK19_VAC2_S1_7`，4 条 accepted proof）**

| 候选源端 | 完整继电器链（触点脚 + 状态） | `required_on` | map 行 |
|---|---|---|---|
| `S1_FPVIe_SL0` | `K88_KELVIN0`(NC,6→7) → `K17`(ON,6→5) → `K18`(NC,6→7) → `K19`(NC,6→7) | [17] | `:194` |
| `S1_FPVIe_SL1` | `K132_KELVIN1`(NC,6→7) → `K139_QVML_BUS1`(ON,2→1) → `K138_QVML_BUS0`(ON,1→2) → `K17`(ON,6→5) → `K18`(NC) → `K19`(NC) | [17, 138, 139] | `:408` |
| `S5_ACM200_SH0` | `K18`(NC,6→7) → `K19`(NC,6→7) | **[]** | 无独立行 |
| `S8_QVM_CH0-`（QVM 低端） | `K138_QVML_BUS0`(ON,1→2) → `K17`(ON,6→5) → `K18`(NC) → `K19`(NC) | [17, 138] | `:631`（写 `… -> VAC1`） |

- 被拒：`S1_FPVIe_FL0`（角色不符）。
- 方向要求：`S10_CH0_A -> K66(ON) -> nQON`（`:850`）与 `S10_CH0_A -> K141(NC) -> K7(ON) -> K8(NC) -> VBAT`（`:514`）证明 **QTMU 通道把自己作为低端/回程**；其另一路 `S10_CH0_B` 只出现在 VAC1 证明里。IR 把 VAC1_S 的 net 记为 `NetK19_VAC2_S1_7`（K19 的 **7 脚**），与 F 侧 `NetCap1_VAC1_S1_1` 是**两个不同 net**（同轴两端）。

### 4.2 `VBAT`（静态供电）

**F 侧 = `VBAT_F_S1`（net `NetCap1_VBAT_S1_1`，5 条 proof）**

| 候选源端 | 完整继电器链 | `required_on` | map 行 |
|---|---|---|---|
| `S3_FXVIe_PLUS_FH5`（FXVIe_PLUS；`VBAT_PD3_FXVI`） | `K8_PD3`(**NC**,6→7) `NetK7_BUSH_VBAT_S1_4 -> NetCap1_VBAT_S1_1` | **[]** | `:833`（组头 `:832` 记 `需闭合: 无(默认导通)`） |
| `S1_FPVIe_FH1`（CH1 高端） | `K131_KELVIN1`(NC,3→2) → `K7_BUSH_VBAT`(ON,3→4) → `K8`(NC) | [7] | `:419` |
| `S1_FPVIe_FH0`（CH0 高端） | `K87_KELVIN0`(NC,3→2) → `K143_DCM_BUS0_H`(ON,2→1) → `K144_DCM_BUS1_H`(ON,1→2) → `K7`(ON) → `K8`(NC) | [7, 143, 144] | `:211` |
| `S10_CH0_A`（QTMUe） | `K141_QTMU_BUSA`(**NC**,3→2) → `K7`(ON,3→4) → `K8`(NC) | [7] | `:514` |
| `S8_QVM_CH0+`（QVM 高端） | `K136_QVMH_BUS0`(ON,1→2) → `K132_KELVIN1`(**NC**,2→3) → `K130_KELVIN1_F`(ON,1→2) → `K131_KELVIN1`(NC,3→2) → `K7`(ON) → `K8`(NC) | [7, 130, 136] | `:639` |

**S 侧 = `VBAT_S_S1`（net `NetK8_PD3_S1_2`，4 条 proof）**

| 候选源端 | 完整继电器链 | `required_on` | map 行 |
|---|---|---|---|
| `S3_FXVIe_PLUS_SH5` | `K8_PD3`(NC,6→7) | **[]** | `:834` |
| `S1_FPVIe_SH1` | `K132_KELVIN1`(NC,6→7) → `K7`(ON,3→4) → `K8`(NC) | [7] | `:420` |
| `S1_FPVIe_SH0` | `K88_KELVIN0`(NC,6→7) → `K137_QVMH_BUS1`(ON) → `K136_QVMH_BUS0`(ON) → `K7`(ON) → `K8`(NC) | [7, 136, 137] | `:212` |
| `S10_CH0_A` | `K141_QTMU_BUSA` → `K130_KELVIN1_F`(ON) → …（该条 proof 步数 6，逐条见 `tm108-paths-proofs.txt`） | [7, 130] | `:514` |

- 被拒：F 侧 `S1_FPVIe_SH0/SH1`；S 侧 `S1_FPVIe_FH0/FH1`、`S8_QVM_CH0+`（角色不符）。
- **关键物理事实**：`VBAT_S_S1` 的 net 是 **`NetK8_PD3_S1_2`**，即 `K8_PD3_S1` 的 **2 脚**——与 PD3 的 Sense 节点同 net（`K8` 另一侧 `NetK7_BUSH_VBAT_S1_4`，1 脚即 F 侧 `NetCap1_VBAT_S1_1`）→ **VBAT 与 PD3 在 K8 上互斥**（`:814-816` vs `:832-834`）。
- 稳压支路：`VBAT 稳压 Cap2_VBAT_S1 C=4.7uF 需闭合: K13`（`:914`）——`K13` **不出现在任何 proof/map 通路链中**（§8 OI-7）。

### 4.3 `nQON`（观测端子；DFT 检查脚 `DTEST0` 的候选承载端）

**F 侧 = `nQON_F_S1`（net `NetK64_HG1_S1_7`，6 条 proof）**

| 候选源端 | 完整继电器链 | `required_on` | map 行 |
|---|---|---|---|
| `S5_ACM200_FH9`（`NQON_HG1_ACM`） | `K64_HG1`(**NC**,6→7) `NetK62_BUS_FH_QON_S1_2 -> NetK64_HG1_S1_7` | **[]** | `:799`（组头 `:798` `需闭合: 无(默认导通)`） |
| `S10_CH0_A`（QTMUe） | `K66_TMU_nQON`(ON,2→1) `NetK66_TMU_nQON_S1_2 -> NetK64_HG1_S1_7` | [66] | `:850` |
| `S1_FPVIe_FH1`（CH1） | `K131_KELVIN1`(NC,3→2) → `K141_QTMU_BUSA`(**NC**,2→3) → `K66`(ON,2→1) | [66] | `:445`（组头 `:444`） |
| `S1_FPVIe_FH0`（CH0） | `K87_KELVIN0`(NC,3→2) → `K62_BUS_FH_QON`(ON,1→2) → `K64`(NC,6→7) | [62] | `:243`（组头 `:242`） |
| `S8_QVM_CH0+`（QVM 高端） | `K137_QVMH_BUS1`(ON) → `K136_QVMH_BUS0`(ON) → `K62_BUS_FH_QON`(ON) → `K64`(NC)（6 步，逐条见文件） | [66, 130, 136] | `:655` |
| `S24_P0`（DCM 源表端口，`Component-Statistic.txt:69` 列为 `DCM (15)` 之一） | **`path=[]`（0 步）**，`required_on=[]`，`cbit={}` | [] | **无对应行**（列8/列10 无此链） |

**S 侧 = `nQON_S_S1`（net `NetK64_HG1_S1_2`，4 条 proof）**：`S5_ACM200_SH9`（`K64` NC,6→7，`required_on=[]`；`:800`）、`S1_FPVIe_SH0`（`K88`(NC) → `K62_BUS_SH_QON`(ON) → `K64`(NC)，[62]；`:244`）、`S1_FPVIe_SH1`（`K132`(NC,6→7) → `K136`(ON) → `K137`(ON) → `K62_BUS_SH_QON`(ON) → `K64`(NC)，[62,136,137]；`:446`）、`S10_CH0_A`（`K66` → `K131` → `K130` 六步，[62,86,141]；`:850` 对应列8 行）。

- 被拒：F 侧 `S1_FPVIe_SH0/SH1`；S 侧 `S1_FPVIe_FH0/FH1`、`S8_QVM_CH0+`。
- **与 HG1 的互斥（可证）**：`K64_HG1_S1` 的 **7 脚** = nQON net，**2 脚** = `NetK62_BUS_FH_QON_S1_2`；HG1 通路要求 `K64(Relay-ON)`（`:70/:71/:296/:297/:470/:557/:700/:701`，proof `PIN_HG1_*` 链中 `state=ON`），nQON 通路要求 `K64` 保持默认导通（NC）→ **nQON 与 HG1 在 K64 上互斥**；两者又共用 `K62_BUS_FH/SH_QON` 与 ACM200 第 9 号端口组。
- 上拉支路：`nQON 上拉-固定5V R_nQON_PU_S1 需闭合: K65`（`:891`）；`K65` 在通路链与 IR `relays[]` 中 **0 出现**（§8 OI-7）。
- **`DTEST0` 可达性**：`DTEST0` 为器件内部数字节点（NMOS 开漏 nQON 观测），三件套无该名；原理图层面唯一对应可测端子是 `nQON`（`Component-Statistic.txt:114/138/204/228/256/280/342/366/405/431`）。**"DTEST0 经 nQON 观测"属 DFT 侧事实，本审计不假设**（§8 OI-6）。

### 4.4 `AGND`（参考/回流）

**`AGND_F_S1`（4 条 proof，全部 `path=[]`）**：`S3_FXVIe_PLUS_FL(0-3)`、`S3_FXVIe_PLUS_FL(4-7)`、`S5_ACM200_FL(0-11)`、`S5_ACM200_FL(12-23)` → `required_on=[]`，`dut_net = AGND_F_S1`（端口组名本身即 net 名，**0 步 = 无需任何继电器**）。
**`AGND_S_S1`（10 条 proof）**：

| 候选源端 | 完整继电器链 | `required_on` | map 行 |
|---|---|---|---|
| `S1_FPVIe_SL0` | `K88`(NC,6→7) → `K138_QVML_BUS0`(ON,1→2) → `K140_QVML_AGND`(ON) | [138, 140] | `:32`（组头 `:31` 自标 `[单线-仅SL] ⚠F/S未同时连通,非有效通路`） |
| `S1_FPVIe_SL1` | `K132`(NC,6→7) → `K139`(ON) → `K140`(ON) | [139, 140] | `:258`（组头 `:257` 同注） |
| `S3_FXVIe_PLUS_SL(0-3)`、`SL(4-7)`、`S5_ACM200_SL(0-5)`、`SL(6-11)`、`SL(12-17)`、`SL(18-23)`（6 个端口组） | **`path=[]`（0 步）** | [] | 无独立行 |
| `S8_QVM_CH0-` | `K140_QVML_AGND`(ON) | [140] | `:854`（DUT 端写 `AGND`） |
| `S10_CH0_B` | 六步（含 `K130_KELVIN1_F`(ON) 等，逐条见 `tm108-paths-proofs.txt`） | [130, 139, 140] | 无独立行 |

- 被拒：`S1_FPVIe_FL0`、`S1_FPVIe_FL1`（角色不符）。
- **`AGND_F` ↔ `AGND_S`**：由 `K92_AGND_F2S`（`Component-Statistic.txt:453` `[P2P(到地)]`）相连；IR net 记录为 `NetK92_AGND_F2S_S1_2`；`K92` 在通路链中 0 出现。
- **低速端分组**：ACM200 与 FXVIe_PLUS 的 Low 端 FL/SL **分组接 AGND_F**，闭环经 AGND 回流（`:801`、`:804`）。
- **F/S 关系**：`AGND_F` 侧 4 条 proof 全 0 步，`AGND_S` 侧才有经 K138/K139/K140 的链，且 `:31`/`:257` 自标"非有效通路"→ **AGND 方向不存在有效 Force/Sense 双线对**（§8 OI-10）。

### 4.5 共享节点 / BUS 共享 / 互斥（TM108 相关，汇总）

| 关系 | 事实 | 证据 |
|---|---|---|
| 共享 net（同一电气节点） | `VAC_FORCE_S1`（K17-4 脚 / K70-2 脚）、`VAC_SENSE_S1`（K17-5 脚）、`NetK18_VAC3_S1_2`（K18-2 / K19-3）、`NetK7_BUSH_VBAT_S1_4`（K7-4 / K8-6）、`NetK130_KELVIN1_F_S1_2`（K130-2 / K131-3）、`NetK62_BUS_FH_QON_S1_2`（K62-2 / K64-2）、`NetK138_QVML_BUS0_S1_1`（K138-1 / K139-2） | proof `path[]` 的 `from_net/to_net`（`tm108-paths-proofs.txt`） |
| BUS 共享 | `K17/K62/K136/K137/K138/K139/K141/K142/K143/K144/K145/K146/K154` 均属 `[BUS]`（`Component-Statistic.txt:441`），被大量非 TM108 端子共用；占用即与该 BUS 上其它端子互斥 | `Component-Statistic.txt:441`、`tm108-perpath-compare.txt` |
| 互斥（同 K 不同状态） | `K8`（VBAT↔PD3）、`K18/K19/K20`（VAC1/VAC2/VAC3/AMUX 四选）、`K17`（VAC123↔AMUX↔VAC_WL）、`K64`（nQON↔HG1）、`K131/K132/K133`（CH1 Kelvin 组）、`K141/K142`（QTMU A/B 两路） | `:190/:196/:202/:631/:633/:635`、`:70/:243`、`:407/:419`、`:514/:850` |
| 同脚复用（决定性互斥证据） | `K141_QTMU_BUSA_S1S2`：**3 脚**同时出现在 `S10_CH0_A→VBAT`(proof) 与 `S1_FPVIe_FH1→nQON`(proof)；`K62_BUS_SH_QON_S1` 的 **2 脚**同时出现在 `nQON_S`(S10_CH0_A 证明) 与 `HG1_S` 通路 → **同一时刻只能选其一** | `tm108-paths-proofs.txt`；`SCH-Connect-Map.txt:470/:557/:850` |
| 四选结构 | VAC1=`K18(NC)+K19(NC)`、VAC2=`K18(NC)+K19(ON)`、VAC3=`K18(ON)+K20(NC)`、AMUX=`K18(ON)+K20(ON)`（AMUX 另有 K154/K155 路径） | `:190/:196/:202/:37`、`:631/:633/:635/:535` |
| 到地与稳压旁路 | `VAC1↔AGND 需闭合: K14`（`:877`）、`VAC1 稳压 Cap2_VAC_S1 4.7µF 需闭合: K21`（`:913`） | 同上；K14/K21 不在任何 proof 链中 |

---

## 5. Relay facts（继电器物理事实）

### 5.1 命名与状态语义

- 命名：`K<编号>_<功能名>`（全板 182 只功能名见 `Component-Statistic.txt:439-459`），实例名加站点后缀（`_S1` / `_S1S2`）。"同一 K 号 F 侧/S 侧两个实例"是设计事实。
- **行令牌**（`SCH-Connect-Map.txt:4`）：`Relay-ON` = 需 SetOn 闭合；`Relay-NC` = 默认导通（无需闭合）。全文 1648 令牌：ON 1049 / NC 599。
- **proof 记录**（权威）：每步给 `state`(ON/NC) 与触点脚；`required_on` 只列**必须额外 SetOn 的继电器号**。因此"**闭合全集 = proof 步序列（含 NC 步，NC 步指该触点默认导通）+ required_on**"。
- **41 只"双态"继电器**（同一 K 号在通路中既有 ON 又有 NC，IR 单值 `state` 取 NC）：K4/K8/K18/K19/K20/K31/K33/K36/K37/K43/K48/K49/K50/K52/K59/K61/K64/K84/K87/K88/K89/K95/K98/K100/K102/K105/K107/K110/K112/K115/K117/K119/K121/K124/K131/K132/K133/K141/K142/K155/K157（`tm108-consistency-check.json` → `disagreements_map_vs_ir`）。

### 5.2 TM108 相关继电器逐项事实

| K | 实例（例） | 类别 | 默认态（由令牌/proof 判定） | TM108 相关角色 | 证据 |
|---|---|---|---|---|---|
| 7 | `K7_BUSH_VBAT_S1` | `[BUS]` | ON（VBAT/PD3 均为 ON） | VBAT BUS 挂接 | `:211/:212/:419/:420/:514/:639`；`:441` |
| 8 | `K8_PD3_S1` | `[Share]` | NC（VBAT=NC、PD3=ON） | VBAT ↔ PD3 二选一 | `:832-834` vs `:814-816`；`:457` |
| 13 | `K13_VBAT_Cap_S1S2` | `[Connect(Cap)]` | **无通路令牌** | VBAT 4.7 µF 稳压支路 | `:914`；`:447` |
| 14/15/16 | `K14_VAC1_P2P` 等 | `[P2P]` | **无通路令牌** | VAC1/2/3 ↔ AGND | `:877-879`；`:451` |
| 17 | `K17_BUSL_VAC_S1` | `[BUS]` | ON（20 处全 ON） | VAC123/AMUX/VAC_WL 公共入口（3↔4 为 F，6↔5 为 S） | `:190/:193/:196/:199/:202/:205/:407-414/:631/:637` |
| 18 | `K18_VAC3_S1` | `[通用]` | NC（VAC1/2 段 NC；VAC3/AMUX 段 ON） | VAC3 选择（3↔2 为 F，6↔7 为 S） | `:190/:196/:202/:631/:633/:635`；`:459` |
| 19 | `K19_VAC2_S1` | `[Connect]` | NC（VAC1 段 NC；VAC2 段 ON） | VAC2 选择（3↔2 / 6↔7） | `:190/:193/:199/:410/:631/:633`；`:445` |
| 20 | `K20_AMUX_S1` | `[Connect]` | NC（VAC3/AMUX 段 ON） | AMUX 选择 | `:37/:202/:205/:535`；`:445` |
| 21 | `K21_VAC_Cap_S1S2` | `[Cap]` | **无通路令牌** | VAC1 4.7 µF 稳压支路 | `:913`；`:443` |
| 62 | `K62_BUS_FH_QON_S1` / `K62_BUS_SH_QON_S1` | `[BUS]` | ON（nQON/HG1 全 ON） | nQON 与 HG1 公共 BUS | `:243/:244/:445/:446/:470/:557/:655`；`:441` |
| 64 | `K64_HG1_S1` | `[Share]` | NC（nQON=NC、HG1=ON） | nQON ↔ HG1 二选一（6↔7 = nQON net） | `:70/:71/:243/:244/:296/:297/:470/:557/:655/:700/:701/:799/:800`；`:457` |
| 65 | `K65_nQON_PU_S1S2` | `[Connect]` | **无通路令牌** | nQON 5 V 上拉 | `:891`；`:445` |
| 66 | `K66_TMU_nQON_S1` | `[Connect]` | ON（2 处全 ON） | QTMU / FPVIe1-F 侧入 nQON（2→1） | `:445/:850`；`:445` |
| 70 | `K70_VAC_F_S1` | `[通用]` | ON（6 处全 ON） | VAC1/2/3 公共后段（1→2） | `:190/:196/:202`；`:459` |
| 82 | `K82_R_CS_S1S2` | `[BUS]` | NC（8 处全 NC） | R_CS 采样电阻支路（3→2） | `:190/:191/:196/:197/:202/:203/:229/:230`；`:441` |
| 86/87/88/89 | `K86_KELVIN0_F_S1`…`K89_KELVIN0_S1S2` | `[BUS]`/`[Kelvin]` | 混合（41/77/36 处令牌） | CH0 Kelvin-0 F/S 走线 | `:9-13/:190-194/:243-244`；`:441/:449` |
| 90/91 | `K90_PC0_Force_S1` / `K91_PC0_Sense_S1` | `[BUS]` | K90 ON（8 处全 ON） | PC0 Force/Sense 走线 | `:82/:88/:163/:190/:196/:202/:226/:229`；`:441` |
| 92 | `K92_AGND_F2S_S1S2` | `[P2P(到地)]` | **无通路令牌** | AGND_F ↔ AGND_S | `Component-Statistic.txt:453`；IR `pins[AGND_S_S1].nets` |
| 130-133 | `K130_KELVIN1_F_S1`…`K133_KELVIN1_S1S2` | `[BUS]`/`[Kelvin]` | 混合 | CH1 Kelvin-1 F/S 走线 | `:407/:408/:419/:420`；`:441/:449` |
| 136/137 | `K136_QVMH_BUS0_S1` / `K137_QVMH_BUS1_S1` | `[BUS]` | ON（51/55 处） | QVMe 高端 BUS0/1 | `:211/:212/:446/:639/:655`；`:441` |
| 138/139 | `K138_QVML_BUS0_S1` / `K139_QVML_BUS1_S1` | `[BUS]` | ON（48/42 处） | QVMe 低端 BUS0/1 | `:32/:258/:408/:631/:637`；`:441` |
| 140 | `K140_QVML_AGND_S1` | `[P2P(到地)]` | ON（3 处） | QVM 低端 → AGND | `:32/:258/:854`；`:453` |
| 141/142 | `K141_QTMU_BUSA_S1S2` / `K142_QTMU_BUSB_S1S2` | `[BUS]` | NC（36 / 2 处） | QTMUe A/B 两路 BUS 入口 | `:445/:454/:514/:847/:238/:440`；`:441` |
| 143/144 | `K143_DCM_BUS0_H_S1` / `K144_DCM_BUS1_H_S1` | `[BUS]` | ON | DCM 高端 BUS0/1 | `:52/:211/:260/:296`；`:441` |
| 145/146 | `K145_DCM_BUS0_L_S1` / `K146_DCM_BUS1_L_S1` | `[BUS]` | ON | DCM 低端 BUS0/1 | `:43/:55/:407/:416`；`:441` |
| 154/155 | `K154_BUSH_AMUX_S1` / `K155_FOVI_PGND_S1` | `[BUS]`/`[Share]` | K154 ON；K155 NC/含 ON | AMUX / PGND 共享 | `:34/:35/:260/:261/:460/:502/:806/:807`；`:441/:457` |

### 5.3 由 proof 得到的"触点脚 ↔ net"事实（下游闭集/互斥判断的依据）

- `K7_BUSH_VBAT`: 3 脚 = `FPVIe1_FH_BUS_S1`，4 脚 = `NetK7_BUSH_VBAT_S1_4`。
- `K8_PD3`: 6 脚 = `NetK7_BUSH_VBAT_S1_4`，7 脚 = `NetCap1_VBAT_S1_1`（F）/ `NetK8_PD3_S1_2`（S）。
- `K17_BUSL_VAC`: 3 脚 = `FPVIe0_FL_BUS_S1`，4 脚 = `VAC_FORCE_S1`；6 脚 = `FPVIe0_SL_BUS_S1`，5 脚 = `VAC_SENSE_S1`。
- `K18_VAC3`: 3 脚 = `VAC_FORCE_S1`(F) / `VAC_SENSE_S1`(S)，2 脚 = `NetK18_VAC3_S1_2`(F) / `_7`(S)。
- `K19_VAC2`: 3 脚 = `NetK18_VAC3_S1_2`(F) / `_7`(S)，2 脚 = `NetCap1_VAC1_S1_1`(F) / 7 脚 = `NetK19_VAC2_S1_7`(S) → 说明 S 侧走 **6↔7** 触对。
- `K64_HG1`: 6 脚 = `NetK62_BUS_FH_QON_S1_2`，7 脚 = `NetK64_HG1_S1_7`（= nQON F net）。
- `K62_BUS_FH_QON`: 1 脚 = `FPVIe0_FH_BUS_S1`，2 脚 = `NetK62_BUS_FH_QON_S1_2`。
- `K66_TMU_nQON`: 2 脚 = `NetK66_TMU_nQON_S1_2`，1 脚 = `NetK64_HG1_S1_7`。
- `K141_QTMU_BUSA`: 2 脚 = `FPVIe1_FH_BUS_S1`，3 脚 = `NetK66_TMU_nQON_S1_2`。`S10_CH0_A` 的两个证明分别以 `(3脚→2脚=FPVIe1_FH_BUS_S1)`（→VBAT 证明）与 `(3脚→…→K66→NetK64_HG1_S1_7)`（→nQON_F_S1 证明）起步，**共用同一对触点（2/3 脚）与同一端 net `NetK66_TMU_nQON_S1_2`** → **VBAT 与 nQON 不能同时经 QTMU/A 路取用**（该对触点只能处于一种状态；`K141` 默认 NC，而 VBAT 证明要求其闭合）。
- `K138_QVML_BUS0`: 1 脚 = `NetK138_QVML_BUS0_S1_1`，2 脚 = `FPVIe0_SL_BUS_S1`；`K139_QVML_BUS1`: 2 脚 = `FPVIe1_SL_BUS_S1`，1 脚 = `NetK138_QVML_BUS0_S1_1`。
- `K130_KELVIN1_F`: 1 脚 = `NetK130_KELVIN1_F_S1_1`，2 脚 = `NetK130_KELVIN1_F_S1_2`；`K131_KELVIN1`: 3 脚 = `NetK130_KELVIN1_F_S1_2`，2 脚 = `FPVIe1_FH_BUS_S1`。

---

## 6. Conflicts（登记项；含严重度与两侧证据）

| id | 级别 | 冲突 | 两侧证据 | 处置 |
|---|---|---|---|---|
| C-1 | **medium** | 状态语义：行令牌 `Relay-NC`（=默认导通/不需闭合，`:4` 定义） vs IR `relays[].state=NC`（单值默认/对比态）。IR 单值态**无法表达**"某通路需闭合该继电器" | `:4`；`:814-816`(K8 ON) vs `:832-834`(K8 NC)；IR `relays[K8_PD3_S1].state=NC`（`tm108-consistency-check.txt`） | 登记 OI-1；下游一律以 **proof `required_on` + 行令牌** 为准，语义口径归策略侧 |
| C-2 | low | `需闭合` 组头 ≠ 组内行令牌并集：`:189` 缺 `K82`；`:200` 多算 `K18` | `:189` vs `:190/:191`；`:200` vs `:199/:200` | OI-2；**不改文件**（§7） |
| C-3 | low | 同节点两种书写名（`VAC1_F`/`VAC1`、`VBAT_F`/`VBAT`、`AMUX_F`/`AMUX`、`AGND_S`/`AGND`） | `:190` vs `:631`；`:833` vs `:514`；`:34` vs `:460`；`:32` vs `:854`；`Component-Statistic.txt:486/491` | OI-3 |
| C-4 | low | IR `validation.adapterPathResolutionNote` 与实测矛盾（两路径实为同一目录） | `os.path.samefile=True`（本审计实测） vs IR key `validation.adapterPathResolutionNote` | OI-4 |
| C-5 | low | IR `relays[]`=101（全带 `dutPins`） vs 全板 182 只 | IR key `relays`；`Component-Statistic.txt:439` | OI-5 |
| C-6 | **medium** | DFT 检查脚 `DTEST0` 在三件套中 0 命中；其可测承载端 `nQON` 有 6 条 proof，但"DTEST0↔nQON"无原理图证据 | `compact-dump.txt:148`；IR `pins[nQON_F_S1]`；`Component-Statistic.txt:114/405` | **未证实/定点补证** → OI-6 |
| C-7 | low | 通路图不覆盖 `K13/K14/K15/K16/K21/K65/K92` 等稳压/上拉/P2P 支路的闭合后果（这些 K 号只在 `列11` 出现，任何 proof 链中 0 出现） | `:877-879/:891/:913/:914`；`Component-Statistic.txt:443/447/451/453`；`tm108-consistency-check.json`（K13/K21/K65/K92 tokens=0） | OI-7；是否使用属方法/策略侧 |
| C-8 | low | `S24_P0…S24_P15` 在同一文件内出现两种身份：`Component-Statistic.txt:69` 列为 DCM 源表端口，而同 `S24_Pn` 亦被用作 DCM 内部节点名；proof 对 `S24_P0→nQON_F_S1` 给出 **`path=[]`（0 步）** 的"直接连通"结论 | `Component-Statistic.txt:69`；proof `source_port=S24_P0, dut_pin=nQON_F_S1, path=[]` | **未证实** → OI-9；不假设该口可达 nQON |

**明确无分歧项**：IR `validation.issues=[]`；`path_proofs.json.txt` `status=PASS, issues=0, kelvin_pair_failures=0`；两件套 `determinismVsCanonical` 全 `byteIdentical=true`；门控 G1..G5/G1c/G1d 全 PASS；`cbit_traceability unmapped=0`；TM108 端子的被拒 proof 全部是角色不匹配（非拓扑缺失）。

---

## 7. Re-parse decision

**结论：未执行三件套的 scoped re-parse；未改动 `project/DALI/` 任何文件。**

理由：
1. **无需写权**：本任务只需事实审计，`project/DALI/` 全只读即可满足全部验收；写回仅在"证实真实不一致且必须改写"时成立，本次**未证实**该类不一致（C-1 是语义口径未定；C-2/C-3/C-4/C-5/C-8 是表述/口径/说明瑕疵，**均非物理连通错误**，无需改字节）。
2. **已有可复现的重生成证据**：IR `validation.determinismVsCanonical` 记录了对 `CSV_CONNECTIVITY.NET`、`SCH-Connect-Map.txt`、`Component-Statistic.txt` 的**字节级重生成对比：三者 `byteIdentical=true`**（重生成哈希 = 现盘哈希）；并说明重生成写到 `<workspace>/Project/DALI`（大写 P）。本审计实测二者为**同一目录**（C-4），故**重解析不会改变现盘字节** → 无需再跑。
3. **本审计做的是"独立再取数"**：未调用 IR 生成器；用自写只读脚本（§2.2）从三件套 + proof 文件**独立提取**事实并互检，这是对 IR 结论的独立验证路径。
4. 若将来证实必须改写：按契约须给改写**前/后哈希**并单独报告——本次**未发生**。

**审计前 / 审计后哈希（现算对比）**

| artifact | 审计前 / 审计后（`Get-FileHash`，磁盘口径） | 是否变化 |
|---|---|---|
| `project/DALI/SCH-Connect-Map.txt` | `cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427` | 未变 |
| `project/DALI/Component-Statistic.txt` | `30a11536a3781bac58f10cc400cf9f9c9f0c4b32469c81cfc583eb7d475beb74` | 未变 |
| `project/DALI/schematic-ir.json` | `7ef9d702892093a5de75031500f78a6d627e44d5130cc832be9292d2577d8bdc`（python 明文口径 `35fdd1582958eb6e4fd63e29da59dec63dfe19e3fd6198d8cc8b8f727a5c7ff5`） | 未变 |
| `project/DALI/path_proofs.json.txt` | 本审计仅读；未重算（IR 引用哈希 `eda90a922b2d9e68ed3ac3736986a64ba57ec4fe243701b0d7b2123796ba4863`） | 未变（未写） |

**未访问 `D:/PROJECT6-DALI/devel`**：本次全部命令仅作用于 `D:\Newtest\DSH\ATE-Coding-Plat` 下路径；未对该目录发起任何读写。

---

## 8. Open items（未证实 / 定点补证）

| id | 内容 | 定点补证动作 | 归属 |
|---|---|---|---|
| OI-1 | `Relay-NC/ON`（通路）与 IR `state`（单值）双口径并存，41 只"双态"继电器易被误用 | 策略侧给出并用口径；IR 若需表达"路径级状态"，应改为引用 proof 而非单值 `state`（重生成 + 前后哈希） | test-strategy-architect |
| OI-2 | `需闭合` 组头缺 `K82`（`:189`）、多算 `K18`（`:200`）是否为解析器缺陷 | 用 `CSV_CONNECTIVITY.NET` 原始 net 复核 K82/K18 归属；确为缺陷则修生成器并重生成（**本审计不改文件**） | schematic-expert（后续任务） |
| OI-3 | 基名与 `_F/_S` 端子的同节点关系无可机读表达 | 在 IR `nets[]` 建立 `VAC1 ↔ VAC1_F/VAC1_S` 等别名 | schematic-expert（后续任务） |
| OI-4 | IR `adapterPathResolutionNote` 结论与实测矛盾 | 修正该说明文本 | schematic-expert（后续任务） |
| OI-5 | IR `relays[]` 收录口径（101/带 `dutPins`）未声明 | 在交接说明中显式声明 | schematic-expert（后续任务） |
| OI-6 | `DTEST0` 在三件套 0 命中；`DTEST0 ↔ nQON` 映射无原理图证据 | DFT 侧给出器件内 DTEST0→nQON 证据（DFT 源 `compact-dump.txt:148`；寄存器 `tm108.sv` DMUX_SEL） | dft-expert |
| OI-7 | `K13`(VBAT 稳压)、`K21`(VAC1 稳压)、`K14/K15/K16`(VAC1/2/3 到地)、`K65`(nQON 上拉)、`K92`(AGND_F↔AGND_S) 在 TM108 通路中是否必须闭合 | 属方法/策略选择；原理图仅提供"支路存在 + 默认态"事实 | test-strategy-architect / test-method-expert |
| OI-8 | map 的 pin 段落未单列 `S5_ACM200_FH0/SH0`、`S10_CH0_B` 等"端口组/器件级"源端的通路行（它们以 0 步或短链 proof 存在） | 若下游需要 map 级可读通路，建议在生成器里把端口组源端也落成行（重生成 + 前后哈希） | schematic-expert（后续任务） |
| OI-9 | `S24_P0 → nQON_F_S1` 的 proof 为 **0 步**（无任何继电器与 net 跃迁证据），且 `S24_P0…P15` 在同文件内似有 POGO 口/DCM 节点两种身份 | 用 `CSV_CONNECTIVITY.NET` 与 `Dali-SCH.csv` 复核该端口的 net 归属；未证实前不得视为可用观测源端 | schematic-expert |
| OI-10 | `AGND_F_S1`/`AGND_S_S1` 是否对应器件封装引脚；`AGND` 作为"有效通路端点"的资格（`:31`/`:257` 自标"单线-仅SL，非有效通路"）；F 侧 4 条 proof 全 0 步 | 用器件引脚表（`Pin_Channel_define.h`）与封装图核对，确认 AGND 是板级参考还是封装引脚 | schematic-expert + setup-architect |
| OI-11 | 原理图层面**无法判定** TM108 的 VAC1 扫描应使用哪一路（FPVIe CH0/CH1、QVM 低端、ACM200、QTMU）——本审计按契约**只枚举候选，不做选择** | 归策略/方法选择 | test-strategy-architect |

---

### 附：本审计的独立方法（可复核）

1. 逐件取哈希与可读性判定（§2.1），确认 `schematic-ir.json` 为 DLP 加密件并给出双口径哈希；
2. 独立提取三层证据：**map 全部 11 列的逐行链**、**IR 的 `pins[]/paths[]/relays[]`**、**proof 的逐条 `path[]/required_on`**，并叠加 `Component-Statistic.txt` 的端口→器件映射、功能分类与门控；
3. 互检：per-relay 状态矩阵（99/99）、per-terminal 集合差（map 行 ⊆ IR 链）、net/实例名一致性、门控与 proof 状态；
4. 冲突只登记、不擅自统一；未证实项一律标 **未证实/定点补证**；
5. 全程未改动 `project/DALI/`（§7 前后哈希实证）。
