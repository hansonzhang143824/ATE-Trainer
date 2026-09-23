# RUN-LEDGER — acceptance-20260916-dali10

> Captain 台账（恢复锚点）。会话中断/压缩/重启后**先读本文件**，再读 `isolation-baseline.json`，然后 `agent_teams_status`。

- Team: `ate-dali-acceptance`，profile `ate-delivery`（7 成员 / 9 任务 / 10 依赖）
- run-id: `acceptance-20260916-dali10`
- 唯一写目标: `D:/PROJECT6-DALI/ForCodexDebug`
- 生产树（只读）: `D:/PROJECT6-DALI/devel` — 123 文件，aggregate `9daceeed3769fa8d4b45c0ca…`（见 `isolation-baseline.json`）
- debug 副本起点: `source` 111 文件，aggregate `ccd58311d00d2bdb40aa0c9c…`

## 运行起点冻结证据（captain 落盘，早于任何成员写入）

| 文件 | 明文 sha256（已与 baseline-20260916 交叉核对：MATCH） |
|---|---|
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` |
| `.../source/sub.cpp` | `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470` |
| `.../source/StdAfx.h` | `ba8ab3de1b0c35cb7e9a477bd0b385f80671dc51011a08c9a5220518aab6aee6` |

## DAG 与状态

| id | 环节 | 成员 | kind | 依赖 | 产物 |
|---|---|---|---|---|---|
| t1 | DFT 意图 | dft-expert | work | — | `dft-ir.json` |
| t2 | 原理图连通性 | schematic-expert | work | — | `schematic-ir.json` |
| t3 | 全局 Setup 契约 | setup-architect | requirements | t1,t2 | `setup-contract.json` |
| t4 | 逐 TM 测试计划 | test-strategy-architect | requirements | t3 | `test-plan.json` |
| t5 | 实现（TM600/601 真新增） | ate-implementer | implementation | t4 | `implementation-manifest.json`, `diffs/` |
| t6 | 独立规则审查 r1 | rule-reviewer | review(t5) | t5 | `review-findings.json` |
| t7 | 能力核验（并行于 t6） | dft-expert | verification | t5 | `verification-report.json` |
| t8 | 门禁 + Release 编译 | compile-diagnostician | verification | t6 | `build-report.json` |
| t9 | 集成 + 隔离审计 | setup-architect | integration | t6,t7,t8 | `acceptance-report.json` |

## 必须遵守的两条硬约束（已实测，非推断）

1. **TSZ/DLP 透明加密**：`test.cpp`/`sub.cpp`/`StdAfx.h`/`dali_tm_meta.json`/`test_conditions.yaml` 与多数 `scripts/*.py` 磁盘头为 `TSZ#`。
   - 授权进程（python / devenv）看到**明文**；PowerShell（`Get-Content`/`Select-String`/`Get-FileHash`/`.NET ReadAllBytes`）只得到**密文**。
   - **更正（13:55，新证据）**：本条原写"`grep`/`cat` 只得到密文"，**该措辞已撤回**。实测：本 DSH 会话的 `grep` 工具（ripgrep 由 node 进程托管）对 `project/DALI/input/DFT.csv` **读到的是明文**（首次定位 TM600/TM601 即由此得到），而同一文件的 PowerShell `.NET` 读取得到 `54 53 5A 23`（`TSZ#`）密文头。即：**读得到明文 ≠ 该文件未受保护**，且不同工具链读同一 TSZ 文件的结果不同。
   - 由此确定的可信规则：**哈希锚点与写入一律走 python**（记录 plaintext sha256）；grep 结果可作旁证，但**不得**作为哈希锚点或变更判定依据。
   - 相关事实：`project/DALI/input/DFT.csv` 亦为 TSZ 容器（.NET 读到 `TSZ#`，python 读到明文 CSV）。其明文锚点：**16862 B，sha256 `B92D203FA6F152120A316B9E32C037F7C1C978E96424EDF5A871F02E5CFE0FD4`**（首行 `Item,Function Name,ShortName,ExpectValue,Unit,...`）。故 TM600/TM601 的 10/8 mohm 与 Check/Dynamic 字段**可复验**（python 路径），不是"不可验证"。
   - 因此：一切源码读写走 python；写入前备份；写入后复读比对 sha256；禁止用 PowerShell 文本命令改写源码。
2. **限值冲突不得折中**：OVERVIEW 权威值 TM600 `HS_RDSON`=**11 mΩ**（`Special="Y / 2 FLOAT"`）、TM601 `LS_RDSON`=**7.5 mΩ**；而 `project/DALI/input/DFT.csv:90`=10 mohm、`:98`=8 mohm。必须作为 `blockingDecisions` 记录并由 Captain/用户裁定，禁止取平均或静默择一。

## 已知门禁基线

- green（11）: material-audit, material, material-status, awg, meta, smoke, input-sync, relay-trace, merge, bst-sw, path-def
- knownRed: `cbit`（存量，不阻塞；新增红才阻塞）
- 判据：`scripts/run_gates.ps1` 退出码 0 = 无新增红

## 当前状态（最后一次 captain 更新）

- t1、t2 `in_progress`（attempt 1）：dft-expert / schematic-expert — 两个上游分析并行进行中。
- t3–t9 全部 `pending`，被上游依赖阻塞（属预期，非故障）。
- rule-reviewer、compile-diagnostician 已正确拒绝启动被阻塞任务并待命（不违反纪律）。
- 未观察到任何 `needs_revision`；修复回路尚未触发。

## 修复回路约定

t6 返回 `needs_revision` 时由运行时自动生成 repair + 下一轮 review（新任务依赖**成功**的来源，不依赖失败任务）。
**若该机制未触发**：由 Captain 在观测到 needs_revision 的同一回合手工创建 repair 任务（`sourceTaskId=t5`，assignee `ate-implementer`），再建下一轮 review（`reviewedTaskId=t5`）。

## 已验证的跨阶段陷阱与路径纠正（Captain 实测，13:45）

### 1. TSZ 双哈希陷阱（会破坏 t9 的隔离/变更比对）

同一文件、同一字节数，**Python 得到明文哈希，PowerShell/`.NET` 得到密文哈希**：

| 文件 | Python（授权 → plaintext） | PowerShell `Get-FileHash`（→ ciphertext） | 字节数 |
|---|---|---|---|
| `project/DALI/meta/dali_tm_meta.json` | `1F5EEB5E33372E197DBCB5D0AC2739E3166729F7210A5F7CA46A423DFCD9F7F1` | `48B06343E7BF69D829EEAB627B65043F173AB04EBC8ED5521D90F0D14D832E77` | 143019 |
| `project/DALI/meta/test_conditions.yaml` | `0F4354ED5B3ECC0233FAE8689CE70F4E97942ED900D8D8DD7B34D9E4694F5C48` | `D501253AAFC274BA3D72EE8B03FF5CD1F7D40DBFBC3AE920E726F9223EA7A115` | 11363 |
| `.../source/test.cpp` | `5C9CB3F9339F6DB373AFCFF7504EF6B34924A4CA3042B5926CB612C819AC3317`（= baseline） | `6EFC38E628BD903507647E4D964AAA8A7929E2ECAC0108634A1EFC7E52156BFA` | 434629 |

**规则**：所有 before/after 哈希一律由 **Python** 生成并标注 `plaintext`；任何成员上报的哈希若与本表 Python 列不符，先判断是否用了 `Get-FileHash`，**不得直接判定"文件被改动"**。
（背景：t4 责任成员上报的 `48B06343…` / `D501253A…` 即密文哈希，不是错报，但不可用于变更判定。）

### 2. 角色手册路径缺陷（已就地修正）

- `golden-code/`、`project/DALI/golden-code`：**均不存在**（Test-Path=False）。
- 真实黄金案例库：`knowledge/references/L4-Golden-code/` — 36 项 / 18 个 `.md`；与本次十项相关：`tm600-normal-highcurrent.{cpp,md}`、`Rdson.{cpp,md}`、`toggle-template.{cpp,md}`、`TM1205_TRX_BST_UV_GD.{cpp,md}`、`TM130_Trim_VBG.{cpp,md}`、`sub-measure-template.{cpp,md}`。
- 已修正：`team/roles/test-strategy-architect.md`、`team/roles/ate-implementer.md`、`team/README.md`。

### 3. 恢复锚点

- `team/EXECUTION_PLAN.md`（host 侧持久记忆，自述为"唯一状态总览"，**新会话第一个读它**）已同步上述两条结论与变更日志。
- 该文件独立确认：staged plan 已批准启动，t1/t2 运行中，0/9 完成。

## 已裁定：TM600/TM601 symbol 命名与 meta 覆盖（Captain 实测推导）

**升级来源**：ate-implementer 在 t5 被阻塞期间的只读侦察（`implementer-recon.md`）提出两个 owner 决策。已用源码证据裁定，不需要等 t4 猜。

### 硬规则（源码证据，不可违反）

`scripts/gen_testitems_meta.py:86-94` 的 `load_testcpp_fns()`：

```python
m = re.match(r'DUT_API int ((?:TM\d+(?:_\d+)?_\w+|Trim_\w+))\(short funcindex', line)
tm = re.match(r'TM(\d+(?:_\d+)?)_', name)
```

`main():359-360` → `name = fns[item]`（**函数名取自 test.cpp**）、`row = ov.get('TM'+item)`（意图取自 OVERVIEW）。

结论：meta 的 `functionName` 是**从 test.cpp 抄录**的，不是从 DFT.csv/OVERVIEW 反推的。因此 TM600/TM601 函数名只受两条硬约束：

1. 必须声明为 `DUT_API int <NAME>(short funcindex ...)`（现有惯例）；
2. `<NAME>` 必须匹配 `TM\d+(?:_\d+)?_\w+`，即必须以 `TM600_` / `TM601_` 开头 —— 否则 Item 映射失败、meta 门失败。

### 裁定 A：符号名

- `acceptance/acceptance-plan.json` 的 `symbolHint` = `RDSON_TEST_HS` / `RDSON_TEST_LS` **不能直接用作函数名**（无 `TM600_`/`TM601_` 前缀 → 违反硬约束 2）。
- 与最接近的同族一致（TM607/608/609 的 DFT `ShortName` 为 `BUCK_LS_ZCD`/`BOOST_HS_ZCD`/`BOOST_HS_NEG`，真实符号即 `<Item>_<ShortName>`），故推荐：
  - **TM600 → `TM600_HS_RDSON`**
  - **TM601 → `TM601_LS_RDSON`**
- 注意：DFT.csv 的 `Function Name`/`ShortName` 与真实符号**并非机械对应**（反例：TM100 `INFRA_TEST`/`VS_PRE` → 真实 `TM100_HSKP_ATEST0`；TM130 `Trim_VBG`/`HP_VBG` → `TM130_VCC_VBAT_HT_3P7`）。故 `symbolHint` 只能当提示；精确名由 t4 在 `test-plan.json` 中**显式固定**，t5 严格照抄，t6 据此审查。

### 裁定 B：meta 覆盖（不再是 UNKNOWN）

一旦两个函数以上述名字存在，`gen_testitems_meta.py` 会**自动**把 TM600/TM601 纳入注册表（函数名来自 test.cpp，意图来自 OVERVIEW —— 已确认 OVERVIEW 有 TM600/TM601 两行），`check_testitems_meta.py --require-all` 即可通过。
- `project/DALI/reg_config/tm600.sv`、`tm601.sv` 已存在，供 `_extract_registers` 抽取寄存器证据。
- `dali_tm_meta.json`、`test_conditions.yaml` **已在 t5 的 inScope 内**，且"门禁无新增红"已是 t5 验收项 → **无需新增任务**。

### 可复现探针

`team/artifacts/acceptance-20260916-dali10/probe_meta_naming.py`（只读；python 读取 TSZ 明文；输出 meta 结构、test.cpp 符号集与生成器命名逻辑）。

### 本轮同步核实的成员事实（均 TRUE）

- `devel/source/test.cpp` 与 `ForCodexDebug/source/test.cpp` **字节完全相同**（`5c9cb3f9…`，434629 B，python 直接比对 `b1 == b2`）→ 运行起点隔离成立，此后的 debug 副本差异可完全归因于本 run。
- DFT.csv 中 TM600/TM601 记录（0-based index 18/19）：TM600 `FuncName=RDSON_TEST` `ShortName=HS_RDSON` `ExpectValue=10` `Unit=mohm` `Check=PMID-SW` `Dynamic=iset[pmid2sw,1,1e-3,0]` `Type=MV&MI`；TM601 `FuncName=(空)` `ShortName=LS_RDSON` `ExpectValue=8` `Unit=mohm` `Check=PGND-SW` `Dynamic=iset[sw2pgnd,1,1e-6,0]` `Type=MV&MI`。与成员上报一致。

## 已裁定：force/compliance 机制与 API 代际（Captain 实测，14:05）

**升级来源**：ate-implementer §8（`implementer-recon.md`）：RDSON 黄金案例属**另一个 API 代际**，不能照抄；并提出 3 个问题，其中 #1（`SetClamp` 缺失时如何限定 force 的 clamp/compliance）标为 UNKNOWN。

### 问题 #1 的答案（有证据，不再是 UNKNOWN）

本代 TM 级 force 的**范围/compliance 是 `Set(...)` 的第 3、4 个实参（量程枚举）**，不存在独立的 clamp 方法：

```
test.cpp:835  PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);
test.cpp:1396 VBAT_PD3_FXVI.MeasureVI(50, 5);
test.cpp:1399 iq_standby[site] = VBAT_PD3_FXVI.GetMeasResult(site, MIRET) * 1e6;  // A -> uA
```

- 签名形态：`Set(<source type>, <value>, <电压量程枚举>, <电流量程枚举>, <relay 模式>)`；`MeasureVI(a, b)` + `GetMeasResult(site, MVRET|MIRET)` 取回测量值。
- 黄金案例的 `FPVI.SetClamp(50,50)` 在本代**无对应物**（`SetClamp` 在全部 7 个源文件中命中数 = 0），其语义应由**选择合适的量程枚举**实现，而不是调用 clamp。
- **工程约束（Captain 指出）**：TM600/TM601 的 `Dynamic` 为 `iset[pmid2sw,1,1e-3,0]` / `iset[sw2pgnd,1,1e-6,0]`，即**force 1 A**。故电流量程必须 ≥1 A —— 现有示例里的 `FXVIe_PLUS_10MA` 明显**不够**；t4 必须在 StdAfx.h 的量程枚举中选型并写入计划（不得照抄示例值）。

### 我的错误撤回（Captain 自述）

我在本轮先判定"成员的 0 命中是假零"，**该判定错误，已撤回**。原因：我的探针把 7 个文件拼成一个 blob 统计，而成员限定在 `test.cpp`/`StdAfx.h`。逐文件归因后实测：

| 名字 | test.cpp | sub.cpp | StdAfx.h | Test_Method.cpp | Test_Method.h |
|---|---|---|---|---|---|
| `SetClamp` | 0 | 0 | 0 | 0 | 0 |
| `VBAT_ACM` | **0** | 5 | 0 | 0 | 0 |
| `FOVIe_40V` | **0** | 0 | 0 | 1 | 0 |
| `FOVIe_100MA` | **0** | 4 | 0 | 0 | 0 |
| `FOVIe_` | **0** | 21 | 0 | 187 | 75 |

→ 成员对其声明范围（test.cpp + StdAfx.h）的 0 命中**全部正确**；`SetClamp` 在**任何**文件都不存在。

**但要记录一个精化**：`FOVIe_*` / `VBAT_ACM` 并非全库不存在，而是存在于 **`sub.cpp` / `Test_Method`（方法库层）**，只是**不在 TM 级 `test.cpp`**。因此黄金案例的写法在语法层未必非法，但属于**跨代 TM 级用法**，仍不可照抄 —— 该精化支持而非推翻成员的结论。

### 问题 #2 裁定：拓扑冲突以 DFT 意图为准

`DFT.csv` 规定 `iset[pmid2sw,1,1e-3,0]` / `iset[sw2pgnd,1,1e-6,0]`，`Check=PMID-SW` / `PGND-SW`，`Type=MV&MI` → **外部强制电流 + 差分 Kelvin 感测**（RDSON = V_meas / I_force）。归档黄金案例改为从 FPVI 自身的 `MVRET/MIRET` 反推，**属不同拓扑**。
裁定：**以 DFT 意图层为准**（依据：acceptance-plan 要求计划 source-traceable 到 DFT；项目自述信息源层级"DFT 意图层 > 对象名反推"；角色手册禁止为便于编码而重新定义测试意图）。黄金案例只提供**本代 API 机制**（`Set`/`MeasureVI`/`GetMeasResult` 形态），**不得**改变测量拓扑。
注意量级：1 A 下 10 mΩ ≈ 10 mV 差分，`MeasureVI` 需选择能分辨 mV 的电压量程。

### 问题 #3（限值 11/7.5 vs 10/8 mohm）

仍待用户裁定，不折中、不静默择一（见上节）。

### 可复现探针

`probe_api_generation.py`（代际差异与 API 命中）、`probe_compliance.py`（force 调用形态）。

## TSZ 争议终裁（Captain 实测，14:20）——两份互相矛盾的报告，判定如下

**争议**：成员 A 说"test.cpp 是 TSZ 容器、pwsh 只见密文"；成员 B（rule-reviewer）说"实测前 16 字节 = `ef bb bf 2f 2a…`、NUL=0、python 全树 0 个 TSZ 容器 → 文件是明文、**不加密**，pwsh 报错是编码/行分割异常"。

**终裁证据（同一文件、同一字节数、两条读取路径对照）**：

| 文件 | python（授权进程） | pwsh `.NET ReadAllBytes`（未授权） |
|---|---|---|
| `source/test.cpp` | size 434629，**NULs = 0**，first16 = `ef bb bf 2f 2a 2a …`（BOM + `/**`） | size 434629，**NULs = 2055**，first16 = `54 53 5A 23 05 90 07 0E 7A 01 …`（**`TSZ#`**） |
| `source/sub.cpp` | size 121909，**NULs = 0**，first16 = `ef bb bf 23 69 6e 63 …`（BOM + `#inc`） | size 121909，**NULs = 731**，first16 = `54 53 5A 23 05 54 07 0E 29 01 …` |
| `scripts/run_gates.ps1`（**对照组：非保护文件**） | size 7660，NULs = 0，`ef bb bf 23 20 72 75 6e…` | size 7660，NULs = 0，`EF BB BF 23 20 72 75 6E…` → **两侧完全一致** |

**裁定**：
1. `test.cpp` / `sub.cpp` **确实受 DLP 透明加密**。授权进程（python）拿到明文，未授权进程（pwsh/.NET）拿到 `TSZ#` 密文。
2. 成员 A 的前提**成立**；成员 B 的"不加密"结论**错误，不予采纳**。
3. 成员 B 的推断错误根源：它**只在授权视角测量**（python），并用"python 看到明文"去证明"文件未加密"。这正是本台账此前已记录的陷阱 —— **能读到明文 ≠ 未受保护**；其"全树 0 个 TSZ 容器"是**按构造必然成立**（授权进程视角），不构成反证。
4. 成员 B 的"pwsh 是编码/行分割异常、机制 UNKNOWN"**被对照组否证**：同一 pwsh 调用读非保护的 `run_gates.ps1` 完全正常；对 `test.cpp` 拿到 2055 个 NUL 与 `TSZ#` 魔数 → 机制就是**读到密文**，不是编码问题。

**纪律不变（两条子规则各自独立，且都已实测）**：
- 存在性/内容断言：用 **grep 工具**或 **python**（Grep/python 互证 @6985 一致，二者皆明文可达）；**禁止**用 pwsh `Select-String`/`Get-Content`，0 命中**不得**当缺失证据。
- 哈希锚点：只用 **python 明文 sha256**（`Get-FileHash` 是密文哈希）。锚点：`test.cpp` `5c9cb3f9…ac3317`（434629 B）、`sub.cpp` `e86d49be…c391470`、`StdAfx.h` `ba8ab3de…aab6aee6`。

## 已裁定 BD-03：TM600/TM601 寄存器映射（Captain 独立复核，14:20）

t1 报告两套寄存器映射（`.sv` vs `DFT.csv`），并提示"写错会打开另一只 FET"。Captain 用**现行已出货代码**做裁判：

| TM（现行 test.cpp） | 0x10 | 0x59 | 0x5A | 0x61 | 侧别 |
|---|---|---|---|---|---|
| TM607_BUCK_LS_ZCD | 0x43 | 0x20 | **0x01** | 0x4B | LS |
| TM608_BOOST_HS_ZCD | 0x43 | 0x20 | **0x02** | 0x4B | HS |
| TM609_BOOST_HS_NEG | 0x43 | 0x20 | **0x02** | 0x4B | HS |
| TM640_BOOST_HS_OCP | 0x43 | 0x20 | 0x02（后 0x06） | 0x4B（后 0x4F） | HS |
| TM641_BST_UV | 0x43 | 0x20 | — | 0x4B | — |
| `reg_config/tm601.sv`（LS_RDSON） | 0x43 | 0x20 | **0x01** | 0x4B | LS |
| `reg_config/tm600.sv`（HS_RDSON） | 0x43 | 0x20 | **0x02** | 0x4B | HS |

**裁定：采用 per-TM `reg_config/tm600.sv` / `tm601.sv` 的寄存器映射**（`0x59=0x20`、`0x5A=0x02`(HS)/`0x01`(LS)、`0x61=0x4B`）。理由：它与**现行已出货代码的 HS/LS 位型完全一致**（TM608/609 HS→0x5A=0x02，TM607 LS→0x5A=0x01），而 `DFT.csv` 的 Software_initial（`0x58/0x59/0x61=0x0B`，且 TM600(HS) 行写 TM_LSON、TM601(LS) 行写 TM_HSON，**两侧互为镜像**）与现行代际不一致 —— 与 `PROGRESS.md` 记录的 LS/HS 位反转修复史相符。
**作用域限定**：本裁定只覆盖**寄存器映射**。force/Check 拓扑仍以 DFT 意图为准（已裁定）；**限值仍待用户裁定**（BD-01）；`.sv` 的激励值与 DFT.csv 不同（vbat 3.5 vs 4.2、pmid 5 vs 15、TM601 用 vbus 5 而非 pmid 9），属**仿真激励**域，不得直接覆盖 ATE 激励值。

## 已更正（Captain 自我撤回）：compliance/clamp 机制

我此前裁定"本代无独立 clamp 方法、compliance 只能靠 `Set()` 量程实参" —— **前半句错误，已撤回**。实测 SDK（`F12011.vcxproj` 的 AdditionalIncludeDirectories → `C:/AccoTEST/AccoTEST System/INCLude`，55 个头文件）：
- `FPVIe.h:101 int SetClamp(double percent_PFS, …)`、`FXVIe.h:117/458` → **`SetClamp` 确实存在**（黄金案例的 `FPVI.SetClamp(50,50)` 在本代合法）；它只是在**本项目自有代码**中 0 次使用。
- 量程枚举（实测）：`FPVIe_IRNG` = 10A, 2A, 1A, 100MA…；`FXVIe_IRNG` = 1A, 100MA…；`FXVIe_PLUS_IRNG` = 1A, 100MA…（**封顶 1 A**）；`FPVIe_VRNG` = 100V…100MV；`FXVIe_PLUS_VRNG` = 40V, 30V, 20V, 10V, 3p6V。
- **约束（成立且更精确）**：TM600/TM601 的 1 A 强制**只能由 `FPVIe` 家族承载**（`FXVIe_PLUS` 封顶 1 A），建议留余量取 `FPVIe_2A`/`FPVIe_10A`，**不可**用 `FXVIe_PLUS_10MA`；clamp 可用 `SetClamp`。
- 差分感测 API 存在：`FXVIe_PLUS_DIFF_VRNG` = DIFF_10V / DIFF_3p6V（`FXVIe.h:423`），但**项目内 0 次使用**；现行 TM 用两次单端读相减（TM702_1）。t4 必须**显式二选一**，不得静默。

## 待用户裁定（集中清单，BD-01/05/06/07 + 04）

| 编号 | 问题 | Captain 建议 | 依据 |
|---|---|---|---|
| ~~BD-01~~ | **✅ 已由用户裁定并关闭** | **采用 OVERVIEW：TM600 = 11 mΩ、TM601 = 7.5 mΩ 作为本次验收限值**；DFT.csv 的 10 / 8 mohm 作为**已登记冲突**原样保留、**不折中、不平均、不删除** | 用户裁定；OVERVIEW 为 DFT 意图层权威，且 DFT.csv 已被证明为旧代际（寄存器映射镜像） |
| BD-04 (high) | TM108/TM109 上升阈值 4.4 V(OVERVIEW) vs 4.15 V(DFT.csv)；TM109 行 ramp `vac3` 且 DMUX 抄成 TM108 的 22（行内自相矛盾） | 取 **OVERVIEW 4.4 V**，并把 TM109 行内矛盾登记为已知歧义 | 同上；DFT.csv 行内自相矛盾使其不可作权威 |
| BD-05 | TM600/TM601 1 A 浮动的 compliance/clamp **无任何来源**（黄金默认 0.5 V） | 由你指定，或接受"沿用黄金 0.5 V + 2 ms 脉冲"作为**有期限豁免**并记入 limitations | 无源可依，团队不得自造限值 |
| BD-06 | TM1205 所有 DFT 源 ExpectValue/容差全空 → 无 spec 无法判 pass/fail | 接受"仅结构闭环、不做 pass/fail 判定"并记入 limitations | 同上 |
| BD-07 | TM600 `Special='Y / 2 FLOAT'` 语义（两浮动节点 vs 2 A 浮动力） | 需 DFT 工程师澄清；暂按"两浮动节点"设计并在计划中标注为假设 | 语义歧义 |

> **BD-01 关闭后的执行口径（t3/t4/t5/t6/t8/t9 一律遵守）**：判定阈值取 **TM600 = 11 mΩ、TM601 = 7.5 mΩ**；在 plan / manifest / review / build-report 中**必须并列引用**两侧来源（`OVERVIEW!row 132/133` 与 `DFT.csv index 18/19`）并注明"以 OVERVIEW 为验收限值、CSV 值保留为已登记冲突"，使该决定**可追溯**且不掩盖分歧。`dft-ir.json` 的 `limitConflictPairs`/`PA-01/PA-02` 无需修改（其职责就是保真记录冲突）。

## 已裁定：TM600/TM601 force/sense 拓扑与 iset 字段语义（Captain 实测，14:35）

### 裁定 A：force/sense 引脚（关闭 BD-02 的默认解）

| TM | force 通路 | sense（Check） | 依据 |
|---|---|---|---|
| TM600 (HS_RDSON) | `iset[pmid2sw, …]` = PMID↔SW | `PMID-SW` | DFT.csv 行内**自洽**（强制与感测同一对节点 = 四线 Kelvin） |
| TM601 (LS_RDSON) | `iset[sw2pgnd, …]` = SW↔PGND | `PGND-SW` | 同上；且 LS FET 位于 SW↔PGND，强制 PMID↔SW 不会把 1 A 压到 LS 管上 |

`reg_config/tm601.sv` 的激励是 `isrcPMID_SW`（PMID↔SW），与其 `SW-PGND` 检查节点**互相矛盾** → 该 .sv 激励**不采纳**。
**作用域再次限定**：`.sv` 只在**寄存器映射**上权威（见 BD-03 裁定）；**force/sense 拓扑与激励值以 DFT 意图为准**（本裁定 + 此前拓扑裁定）。
若 t2 原理图给出相反证据（例如 `PMID_SW` 是模型内部节点名而非外部引脚对），需由 t2/t3 带证据上报，Captain 再复核；在此之前默认按上表执行。

### 裁定 B：`iset[...]` 字段语义 —— **不存在单位缺陷**

格式为 `iset[<pin 对>, <电流 A>, <ramp 时间 s>, <flag>]`。**决定性书面证据**（`reg_config/tm600.sv`）：

```
38: `NVT_STIM.en_isrc_sw = 1;
39: `NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3);
41: // pin SW current set to 1A
42: //		iset[sw,1,1e-3,0]
```

即 `ramp_isrc_val(1, 1e-3)`（值 1、ramp 1e-3）对应注释 **"1A"** 与 `iset[sw,1,1e-3,0]` → **第 2 字段是电流，第 3 字段是 ramp 时间**。
DFT.csv 全部 33 处 `iset` 用法一致（抽样）：`iset[vcc,0.03,1e-3,0]`、`iset[bst,0.1,1e-6,0]`、`iset[sw2pmid,2,1e-6,0]`、`iset[sw2pmid,3.2,1e-3,0]`、`iset[pgnd2sw,0.5,0,0]`。

→ **TM601 `iset[sw2pgnd,1,1e-6,0]` = 1 A、ramp 1 µs**（TM600 是 1 A、ramp 1 ms）。**没有 1 µA 缺陷**；t1 的 C-01 写 "1 A" **正确**，且不是从 `.sv` 继承来的结论。
（旁注：TM627/628 出现 5 字段的异常写法 `iset[pmid2sw,-0,9,0,0]`，属源数据瑕疵，与本裁定无关，登记备查。）

## 产物哈希登记（供 t9 集成比对；`dft-ir.json` 旧值已作废）

| 产物 | 大小 | python 明文 sha256 | 状态 |
|---|---|---|---|
| `dft-ir.json` | 99058 B | `85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e` | **live**（13:52 close-out 修订后） |
| `dft-ir.json`（旧） | 88101 B | `478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755` | **作废**（t1 交接信中引用的是此值 → 下游必须**重新哈希**，不得沿用手抄值） |

教训：交付信里手抄的哈希会因交付物被修订而失效；**以文件现算哈希为准**（t9 集成审计必须现算）。

## 已确认：DFT 路径别名缺解析表 → 已并入 t3 必交付（Captain 实测，14:50）

**成员发现（test-strategy-architect）+ Captain 复核结论：成立**，且是 t5 的阻塞性缺口。

| 事实 | 实测结果 |
|---|---|
| DFT 别名出现处 | `DFT.csv`：`pmid2sw` 10、`pgnd2sw` 9、`bst2sw` 9、`sw2pgnd` 4 |
| 在源码/通路文件中的出现 | `test.cpp` 仅 1 处 `pmid_sw`；`sub.cpp`/`StdAfx.h`/`SCH-Connect-Map.txt`/`CSV_CONNECTIVITY.NET` **0 命中** |
| `intermediates.paths_txt` | `project/DALI/paths.txt` **不存在**（其余 5 个中间产物均存在） |

→ **"别名 → (激励仪器, 继电器通路, K 号)" 无机读解析表**。

**但这不是"无解阻塞"**：工程自带生成器 `scripts/gen_paths.py`（自述：BFS 通路追踪 `trace_single`、稀缺源表识别、禁借道 BUS、G6K/MOS 通断模型、**FPVIe 域约束 FH/SH vs FL/SL**、**F/S 分类 Kelvin/PC 短接/单线**、relay 类型权威源 = CBIT Excel，支持 `--json` 结构化 `path_list`）。`paths.txt` 即其声明的产物。
**Captain 指令**：t3 用该脚本生成通路表，**输出到 run 目录**（`sch-paths.json`/`.txt`），**不写** `project/DALI/paths.txt`；并在 `setup-contract.json` 内用 `resources`+`tmDeltas` 给出别名解析表（带证据）。已发消息给 t3 责任人（t3 未交付，来得及）。

**可引用文字证据（Captain 已核对）**：`knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:16`（FPVI 唯一 → `iset[PMID2SW,1A]` 占 FPVI_BUS；BST−SW 降级双独立源）、`knowledge/hardware/voltage-inference.md:98/143`（`iset[PMID2SW,1A]` → PMID≈SW，压差 = I×RDSON < 100 mV）。注意其中 `K31`/`K17` 为**旧代际 K 名**（现行 0 命中），必须换算。

## 已确认：`.sv` 属旧代际仿真域（成员发现 + Captain 复核）

- `.sv` 文件头 `generate time: 2026-05-15 16:48:30`（Captain 实读 tm600.sv/tm601.sv 确认）。
- PROGRESS.md 记录的 LS/HS 位反转修复对应备份 `test.cpp.bak_tm607_609_20260819`、`test.cpp.bak_bst_sw_fix_20260826`（Captain 在源码目录列表中实见）→ **.sv 早于该修复**。
- `.sv` 的恒定电流路径与 DFT.csv **互换**：tm600.sv `isrcSW`→`iset[sw,…]`（单端）vs DFT TM600 `iset[pmid2sw,…]`；tm601.sv `isrcPMID_SW`→`iset[pmid_sw,…]` vs DFT TM601 `iset[sw2pgnd,…]`。成员判断与 Captain 归因**一致**。
- **作用域**：`.sv` 仅在**寄存器映射**上权威（BD-03，因其与现行出货代码位型一致）；**激励路径/引脚/ramp 一律以 DFT 意图为准**，`.sv` 激励不得照抄。

## 已裁定：TM600/TM601 实现形态（Captain 复核 + 标准铁律，15:05）

以下四条**全部由 Captain 独立实测/实读**，不依赖成员自述。

### A. 门禁陷阱（**会直接导致"新增门禁红"**）：TM600/TM601 禁止使用 `rampi_capv`

`scripts/verify_bst_sw_sequence.py:78-114` 的 `derive_targets()` **按行为自证取目标**：

```
函数体内含 `rampi_capv(` → 电流斜坡 → 本家族  （docstring 原话）
K_FPVIH_TO_PGND → 'LS'(BUCK, SW↔PGND); K_FPVIH_TO_PMID → 'HS'(BOOST, PMID↔SW)
```

且该脚本自陈"目标集合随 meta 漂移，**每加一个 TM 就可能多几条假 FAIL**"（TM641/643/1205 曾被误判）。
→ TM600/TM601 是 **MV&MI 静态强制**，不是电流阈值 ramp 家族；若用 `rampi_capv` 实现 1 A 强制，会被本门收为 ZCD/OCP 家族目标并按硬编码精确串逐条要求 → **几乎必然新增 FAIL**，直接违反验收标准 5（无新增门禁失败）。
**裁定：改用 `FPVIe::Set(FI, …, FPVIe_2A, FPVIE_RELAY_ON)` + `MeasureVI` + `GetMeasResult(MVRET/MIRET)`；禁止 `rampi_capv`/`rampv_capv`。**

### B. 量程：`FPVIe_2A`（不是 1A）

`knowledge/standards/units.md:3-5`："**量程选择：≥ 2× 设定值** — 选最接近设定值 2 倍的那一档量程"。1 A → 最小合规档 = **`FPVIe_2A`**。同族先例：TM607/608 用 `FPVIe_2A`，TM609/640（3 A）用 `FPVIe_10A`。（成员已自行撤回此前"用 FPVIe_1A"的说法。）

### C. force/sense 形态：FPVIe 浮动源，强制对 == 感测对（**标准强制**）

`knowledge/standards/rules-registry.md:44` **R-BST-SW** 原文："**HS=BOOST(PMID-SW) / LS=BUCK(SW-PGND)，均电流>200mA 用 FPVIe 浮动源**"。
→ ① 独立佐证了本台账此前的 force/sense 裁定（TM600 HS=PMID↔SW、TM601 LS=SW↔PGND）——这是**第三处独立来源**（DFT.csv 行内自洽 + 本标准）；② 1 A > 200 mA ⇒ **必须 FPVIe 浮动源**；③ `FXVIe_PLUS` 族封顶 1 A（`FXVIe.h:13-21`）且 `FXVIe_PLUS_DIFF_*` 项目内 0 次使用 ⇒ 不采用 DIFF API；④ 两次单端相减（TM702_1 写法）测的是 VDM−AMUX，**不等于** Check 要求的节点对 ⇒ 不采用。
**裁定：`FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON)` → `MeasureVI(...)` → `R[mΩ] = MVRET / MIRET × 1e3`**；电压量程用 `FPVIe_1V`（**不用** `FPVIe_100MV`：失败件 1 A×1 Ω 会顶量程），分辨率用 `MeasureVI(..., FPVIe_MV_X10, ...)`（`FPVIe.h:104-112`、增益枚举 `:37-51`）。

### D. 计算铁律 R-VIR

`rules-registry.md:40` + `units.md:64-66`："**电阻 = 实测电压 / 实测电流** … R = `GetMeasResult(MVRET)` / `GetMeasResult(MIRET)`（同一源表同一次 MeasureVI 后读取）。**禁止**用理论设定电流"。→ TM600/TM601 的 `calculation` 必须写成 `R = MVRET / MIRET`，并以 MIRET 回读实际电流。

### E. 高低电流上下电铁律（已在该标准登记，t3/t5 必须遵守）

- `rules-registry.md:32` **R-PON**：含"**大电流三段式（FV=0→FI=0→Clamp→FI）**"、浮动源三阶段 ≤5 V。
  → **BD-05 的机制有了标准依据**（Clamp 是官方上电步骤之一）；但**具体数值仍无来源**，仍属用户裁定项。
- `rules-registry.md:33` **R-POFF**：普通三步（归零→`delay_ms(1)`→`RELAY_OFF`）、浮动反转台阶、**FPVI 最后 RELAY_OFF**、大电流 `FI=0→FV=0→OFF`、`RELAY_OFF` 统一量程（**FPVI 用 1V/10MA 非 10A**）。

## 用户裁定 BD-01 原文与作用域（15:2x，用户下达）

> 本次 `acceptance-20260916-dali10` 采用 **OVERVIEW 的 TM600=11 mΩ、TM601=7.5 mΩ** 作为**代码与测试计划的验收限值**。证据理由：`project_config.json` 将 DFT xlsx 设为权威 DFT 输入，OVERVIEW 是当前意图层且有明确 sheet/row 定位；`DFT.csv` 的 10/8 mohm 作为**冲突的派生/旧值**保留在 IR 与最终报告，**禁止改写、平均或删除**。该裁定**仅适用于本次 debug 副本验收**；若后续发现更新版本/批准记录，**必须重开该决策**。

执行口径：plan / manifest / review-findings / build-report / acceptance-report **一律按 11 mΩ / 7.5 mΩ 判定**，并**并列引用**两侧来源（`OVERVIEW!row 132/133` 与 `DFT.csv` recordIndex0Based 18/19）＋上述理由、作用域、重开条件。`dft-ir.json` 的 `PA-01/PA-02` 由 t4 改标 `closed-by-user-adjudication`（两侧证据保留）。

## Captain 第三次自我更正：撤回"感测端用 FPVI 自身 MVRET"（15:2x）

**撤回内容**：我先前裁定"同一个 FPVI 浮动源承担强制与感测，`R = MVRET/MIRET`"中的**感测端部分**。
**撤回理由（证据）**：
- 我核实 `FPVIe.h:104-112`（`MeasureVI(…, FPVIe_MV_GAIN mvGain …)`）、`:45-51`（X1/X2/X5/X10）、`:114-117`（`GetMeasResult` 默认 `retType = MVRET`）→ **能力存在**；
- 但 live 代码 `test.cpp:8065-8071`（Captain 逐行读）为：`VDM_SDA_ACM.MeasureVI(50,5)`、`VAC123_AMUX_ACM.MeasureVI(50,5)`、`FPVI0.MeasureVI(50,5)`，随后 `MVRET_A − MVRET_B` 取 ΔV、**`FPVI0.GetMeasResult(MIRET)` 只用于电流** —— 全项目**无一处**把 FPVI 的 `MVRET` 当测量值；
- 计量上也必须如此：1 A × 10 mΩ ≈ **10 mV**，源端两线自读会把继电器/引线电阻算进去，必须用 DUT 引脚上的独立感测点。
**错误性质（自记）**：我把"**API 有能力**"当成了"**用法/计量上正确**" —— 与本轮我两次纠正成员的错误属同一类。这是本 run 我第三次自我更正（前两次：假零误判、clamp 不存在）。

**更正后的统一形态（t4 写计划 / t5 实现 / t6 审查的共同口径）**：
1. 强制：`FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON)`（>200 mA 用 FPVIe 浮动源：`rules-registry.md:44` R-BST-SW；量程 `units.md:3-5` "≥2×"）。
2. 感测：在 DFT `Check` 引脚对上**两点单端 `MVRET` 相减** —— TM600 = PMID↔SW，TM601 = SW↔PGND。
3. 电流：同一 FPVI 的 `fabs(GetMeasResult(site, MIRET))`；`R[mΩ] = |ΔV| / |I| × 1e3`（R-VIR；E027 会检"只读 MVRET 未读 MIRET"与"出现理论值字面量"）。
4. 禁用 `rampi_capv`/`rampv_capv`（门禁目标污染，见上节）。
5. **感测仪器指派**：由 t3 的"DFT 别名 → 仪器/继电器/K 号"表给出；缺则 t4 记 blocking decision，**不得猜仪器名**。
6. `MeasureVI(..., FPVIe_MV_X10, ...)`：**不再强制**（项目内 0 次使用、56 处均为两参形态）。仅在感测仪器确为 FPVIe 类且 plan 给出"10 mV 级 + 1 V 量程"论证时采用，并显式标注为**首次使用/有意偏离先例**。

## 产物哈希登记（更新）

| 产物 | 大小 | python 明文 sha256 | 状态 |
|---|---|---|---|
| `dft-ir.json` | 107133 B | `0a1c3b1e474c508c63d639d69e3b905ce94cb5b8085c98745c05a6625669597e` | **live（v3）**；t4 已独立比对与 `dft-raw/dft-ir-hashes.json` 一致 |
| `schematic-ir.json` | 447580 B | `3ed7a4d752ceb72c2ec7510988b93ab8474ef3459de85afe78d4254a8d5ef2c7` | **live**；Captain 实测 schema PASS；nets 41 / paths 182 / hazards 22 / openQuestions 13 / sources 19；scope 十项 TM |
| `dft-ir.json`（v1/v2） | 88101 / 99058 B | `f3faedc2…` / `478f88a4…` / `85db02e3…` | **全部作废**（交付信手抄哈希不可信，**下游一律现算**） |

**新增/更新仍开项**：`DD-01`（t1 把 `iset[sw2pgnd,1,1e-6,0]` 的"1 µA 字面解读"并列保存 —— **Captain 已裁定为 ramp 1 µs、电流 1 A**，依据 `tm600.sv:38-42` 三行互证 + 36 处 `iset` 用法中第 2 槽只出现电流值/第 3 槽只出现时间值；以 Captain 裁定为准）、`FS-01`（TM601 force/sense 不一致 —— **已由 Captain 裁定**：采 DFT.csv 自洽配对 SW↔PGND，不采用 `.sv` 的 `isrcPMID_SW`）。

## 里程碑：t2 完成并经 Captain 独立复验（15:4x）

| 项 | 实测 |
|---|---|
| 产物 | `team/artifacts/acceptance-20260916-dali10/schematic-ir.json` |
| 大小/哈希 | **450689 B**，sha256 `ed77ccae15f458535015994d9dbbc6cd4c95c34b0bc283fae9cab32bcd06e41d`（**注意**：早先我测到的 447580 B / `3ed7a4d7…` 是交付前的中间版本，**已作废**） |
| Schema | `python scripts/validate_team_artifact.py schematic-ir …` → **PASS** |
| 规模 | nets 41 / paths 182 / derivedPaths 3 / hazards 23 / relays 72 / dutPins 18 / components 29 / unresolvedTopology 8 / openQuestions 15 / sources 19 |
| 工具验证 | adapter 六门 PASS；`csv_pathproof_v2` PASS（112 sources / 669 accepted / 335 rejected / **219 Kelvin pairs** / 0 failures）；重生成 `CSV_CONNECTIVITY.NET`/`SCH-Connect-Map.txt`/`Component-Statistic.txt` 与运行前**逐字节相同**；debug 副本与 `devel` 哈希仍与 `isolation-baseline.json` 一致 |
| 团队状态 | t1 completed、t2 completed、**t3 in_progress**（setup-architect attempt 1） |

### 解决"感测形式之争"的关键事实（来自 t2，Captain 采纳）

t2 finding：`FPVIe0` 的 **PC 网络是板级 F↔S 短接**，且串有 `R1_CS 100 mΩ±1%` / `R2_CS 5 mΩ±1%` → 对 10 mΩ 目标**致命**（串联感测电阻会淹没被测值）。结论：10/8 mΩ 项**必须**走 **BUS Kelvin 路由 `K87/K88/K89`、`K131/K132/K133`**，**绝不可**用 `K90/K91 + K82`。
→ 这把"FPVIe 自读 vs 两点单端相减"之争**收敛为一个可查证的夹具问题**：**哪台仪器终止该 Kelvin 路由**。已要求 t3 在别名表中给出（若终止于独立电压表 → 采两点单端相减；若 FPVIe 感测端子确实终止该路由且与 `unresolvedTopology` 里的"10 kΩ Kelvin 串联行"兼容 → 采 FPVIe 四线 Kelvin）。**二者都不可达 → blocking decision 上报。**

### t2 报告的其他必须落进契约的项

1. **FPVIe BUS 每侧一根线**：`K83`(PMID) 与 `K154`(PGND) 同在 `FPVIe0_FH_BUS_S1`/`_SH_BUS_S1` → 同时闭合**把 PMID 短到 PGND**；不变量="每 BUS 侧只闭一个 pin"。
2. **`K141`/`K142` 必须打开**（桥接 FPVIe0↔FPVIe1，且默认 QTMU 路由依赖它们）——否则 TM600 的两个浮动回路**并成一个节点**。
3. **极性**：SW 在 FPVIe0 **LOW** bus，PMID/PGND 在 **HIGH** bus → 两回路方向相反（t2 登记 hazard `kind=polarity`）。Captain 裁定：**强制方向与引脚对仍以 DFT 意图为准**，t3 必须给出器件级实现与依据；**物理上无法实现则登记 blocking 上报，禁止静默反向/换对**。（R 用 `|ΔV|/|I|`，符号不影响 R 值，但方向决定**哪只管子导通**。）
4. **旧代际 K 号**：文档里的 `K31/K15/K17/K33` 属上一版板；本网表 `K83` / `K60+K61` / `K41` / `K154+K155`（t2 hazard `kind=legacy-numbering`）。
5. **硬件签核缺口（新增风险）**：t2 指出**继电器无电流额定值记录** → 1 A 强制在电性上**可行但未获硬件签核**，属**残余风险**，需写入最终报告的 limitations。

## Captain 第四次自我更正：裁定信中的编译级拼写错误（16:0x）

我在下达"统一实现形态"时写了 `FPVIE_RELAY_ON`（大写 E）—— **该标识符不存在**。实测：

| 拼写 | 命中 |
|---|---|
| `FPVIe_RELAY_ON`（正确） | test.cpp 54 / sub.cpp 96 / Test_Method.cpp 63 / BoardCheck.cpp 76 = **289** |
| `FPVIE_RELAY_ON`（我的错写） | **0** |

SDK `FPVIe.h` 的 `FPVIe_OUT_RELAY` 只声明 `FPVIe_RELAY_HOLD / FPVIe_RELAY_ON / FPVIe_RELAY_OFF / FPVIe_RELAY_SENSE_ON`。C++ 区分大小写 → 照抄我的错写会**编译失败**。
**由 ate-implementer 显式上报而非静默修改**（符合纪律），Captain 予以确认并更正：**一律用 `FPVIe_RELAY_ON`**。

## 新增教训：多轮撤回造成的"版本错位"风险（16:0x）

**事件**：ate-implementer 把我**早先已撤回**的版本（"无条件用 FPVI 自身 MVRET"）当作**生效裁定**，并在其 prep doc 里写成"锁定形态"。原因是我们双方消息交叉 —— 它的写入发生在我发出撤回/最终判据之前或同时。
**处置**：已发纠正信，明确"当前生效裁定＝按路径证据二选一"，并要求把**感测模式+感测仪器槽位**保持 **显式 PENDING**，不得在该槽位定稿前写成既定实现（骨架其余部分可锁定）。
**规则（写入本台账供后续遵守）**：
1. **撤回必须指名被撤回的那一条**（编号/原文片段 + 时间），不能只写"我撤回之前的说法" —— 本轮我已发生 4 次自我更正，若不指名，接收方极易沿用旧版。
2. **接收方在写入"锁定/生效"字样前，必须先确认自己引用的是最新一版**；有疑问先回报版本，不得静默择一。
3. **同一决策的最终形态必须落在本台账的单一小节**（本文件即唯一权威），成员 prep/plan 中的副本一律标注"以 RUN-LEDGER 为准"。

### 感测形态的最终状态（唯一权威）

- **强制端（已锁定）**：`FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON)` → `delay_ms(2)`；ramp 仅据 DFT（TM600 1 ms / TM601 1 µs）；量程依据 `units.md` "≥2×" + live 先例 `sub.cpp:3258`。
- **电流端（已锁定）**：同一 FPVI 的 `fabs(GetMeasResult(site, MIRET))`。
- **ΔV 端（PENDING，判据明确）**：t3 必须回答 (a) FPVI0 的 sense 是否经 `K88_FPVI0_Sense_FLOAT`/`K91_FPVI0_PC_Sense` 落到 PMID/SW 引脚（→ 真 Kelvin，则用 FPVIe 自身四线 + `MVRET`，并需远端感测闭合 `FPVIe_RELAY_SENSE_ON`）；(b) PMID/SW 各自的单端伏特表通路（→ 用两点单端 `MVRET` 相减）；(c) 各 `FPVIe_RELAY_*` 取值下内部继电器动作。**两者都不可达 → blocking 上报。**
- 关键警告：仅用 `RELAY_ON`（本地/仪器端感测）时 `MVRET` 很可能含引线+继电器压降，对 11/7.5 mΩ 目标是几十个百分点误差；旁证 `Test_Method.h:21` 注释显示本项目曾**有意**从 `RELAY_SENSE_ON` 改回 `RELAY_ON`。**故 `RELAY_ON`+`MVRET` 不得作为最终形态预先锁定。**
- 算式（已锁定，R-VIR）：`R[mΩ] = |ΔV| / |I| × 1e3`，两侧均为实测值（E027 检"只读 MVRET 未读 MIRET"与"理论值字面量"）。

## 感测形式的最终收敛（Captain 直查 t2 IR，16:1x）

Captain 用 python 直读 `schematic-ir.json` 的 `paths[]`（182 条）复核成员主张，**两种形式都已被布线**——这把"感测形式之争"从"布线未知"降级为"驱动层 + PC 排除"两件事：

| 形式 | 夹具证据（path / relays） | 状态 |
|---|---|---|
| (a) FPVIe 自身四线 Kelvin | `role=S S1_FPVIe_SH0 → PMID_S_S1`（**[83]**）、`→ PGND_S_S1`（[154,155]）、`S1_FPVIe_SL0 → SW_S_S1`（[60,61]） | 布线成立；**驱动层未证**（`FPVIe_RELAY_SENSE_ON` 是否为启用远端感测的开关） |
| (b) 独立仪器两点单端 | `S10_CH0_A → PMID_S_S1`（**[83,86,141]**）、`→ PGND_S_S1`（[86,141,154,155]）、`→ AMUX_S_S1`（[86,141,154]）；`S8_QVM_CH0+ → AMUX_F/PMID_F/PGND_F_S1` | 布线成立；**具名仪器候选 = `S10_CH0_A` / `S8_QVM_CH0+`** |

**硬排除（两方证据一致）**：ΔV **绝不走 PC 通路**（`K87/K88/K90/K91 + K82_R_CS`）——该通路串有板上检流电阻 **`R1_CS_S1 = 100 mΩ ±1%` / `R2_CS_S1 = 5 mΩ ±1%`**（net `FPVIe0_FL_PC_S1`），与 10/8 mΩ 限值**同量级**，会让读数被 shunt 主导。ΔV 必须取**感测侧 BUS 通路**（DUT 侧 Kelvin 线）。

**K 号口径裁定（依 `StdAfx.h:249-255` 命名，以成员划分为准，t2 摘要的"K87/K88/K89 = BUS Kelvin 路由"表述不精确）**：`K87_FPVI0_FH_SL_SHORT`/`K89_FPVI0_FL_SH_SHORT` = **本地二线交叉短接**；`K88_FPVI0_Sense_FLOAT` = **感测浮动**；`K90_FPVI0_PC_Force`/`K91_FPVI0_PC_Sense` = **PC 通路**（FPVI1 同构 `:303-309`）。

**决策规则（已下发 t3/t4）**：(b) 作**可交付基线**（live 先例 `test.cpp:8065-8071` + 已布线 + 具名仪器），(a) 作**带证据的增强项**（首次使用/有意偏离需标注并引用 path id）；前提是 t3 的驱动层答案到位，若判"不可判定"则 (a) 降级为待验证增强，**不阻塞整条链**。两候选都必须排除 PC 通路并给出依据。

### 同时并入契约的 t2 关键事实（Captain 采纳）

1. **FPVIe 通道预算**：每 site 仅 **2** 个 FPVIe 通道；TM600 单独即占满（`PMID↔SW 1 A → FPVIe0` + `BST↔SW 5 V → FPVIe1`）；IR 明言 **TM600 与 TM601 不能共用同一函数**（证据 `hardware-specs.md:17`）。与黄金案例"大电流优先占 FPVI_BUS、BST−SW 降级双独立源"一致。
2. **E006 反向偏置不变量**：`vset[bst2sw,5]` 与 `iset[pmid2sw,1]` 并存时，**BST 必须始终领先 PMID/SW ≥5 V**，否则 220 nF `Cap_SW_BST_S1` 反偏可能损伤芯片。
3. **供流能力**：`ACM200 ≤ ±200 mA`、`FXVIe_PLUS ≤ ±1 A（脉冲）`，**只有 FPVIe（±10 A）能供 1 A**；回路两端都必须经 BUS 继电器，否则引脚悬空。
4. **放电事实**：`Cap2_PMID_S1 4.7 µF`、门控 `K85_CAP_PMID_S1S2`、经 `R_PMID_S1 1 K` 泄放到 `AGND_F_S1`（**非直接跨电容**）；`R_PMID_KLV_S1 10 K` 仅串在 KLV 线。
5. **open items 带入契约**：**U1**（继电器触点 1 A 额定值**无数据表证据** → 与"1 A 未硬件签核"同源）、**U2**（10 kΩ KLV 串阻 vs FPVIe 感测输入）。

## 用户裁定：BD-05 关闭（provisional engineering default，16:3x）

> 仅用于 `acceptance-20260916-dali10` 的 **debug 代码与编译，不授权上机**：采用黄金案例的 **`FPVIe.SetClamp(50,50)`**，并在**每次 FV/FI 模式切换后重新设置**；1 A force 使用 **FPVIe 1V/2A 量程** ⇒ **电压 compliance = ±0.5 V**（远高于正常压降 ~11 mV / 7.5 mV，但可限制开路异常）。标记为 **provisional engineering default**；最终报告**保留 U1（继电器 1 A 额定值 / 真实上机前硬件签核风险）**；**不得据此执行硬件测试，不得改生产树**。

执行口径：
- `safetyInvariants` / `parameters` 写入"clamp = ±0.5 V（`SetClamp(50,50)` on `FPVIe_1V`，`percent_PFS/percent_NFS` 语义见 `FPVIe.h:101`），**每次 FV/FI 模式切换后必须重新下发**"（`knowledge/sources/fpvie.md:141-168` 实测切换清除箝位）。
- 一律标注 `provisional: true` + "**非 DUT 数据表值、非 pass/fail 判据，仅限制开路/误配**"。
- **U1**（继电器触点 1 A 额定值无数据表证据 = 上机前硬件签核风险）与 **U2**（10 kΩ KLV 串阻 vs FPVIe 感测输入）保留为 open items，写入最终报告 limitations。
- 边界重申：不得上机、不得改 `D:/PROJECT6-DALI/devel`。

## Captain 第五次自我更正：撤回 (b) 具名感测仪器候选（16:3x）

**撤回内容**：我在裁定点名的 (b) 候选 `S10_CH0_A` / `S8_QVM_CH0+` **作废**。
**错误性质**：我只查了 `paths[]` 的**可达性**，没查 `hazards[]` 的**计量有效性** —— 又一次把"可达/有能力"当成"可用"（与本轮前四次同源）。
**反证（由 test-strategy-architect 拦下，Captain 逐字复核 `hazards[]` 确认）**：
- `hazards[measurement-validity]`（high）原文：QTMU "low side is DGND and QTMU carries a single line … **no Kelvin split**"；PMID(`S10_CH0_A`, K83+K141) 与 SW(`S10_CH0_B`, K60/K61/K142) 的默认路由"are QTMU routes, which is fine for Iq/toggle DC work but **invalid for a mOhm-level force/sense measurement**"；`requiredMitigation`＝"**For TM600/TM601 use only FPVIe Kelvin routes; do not measure RDSON on the QTMU**"。
- `hazards[shared-resource]`（high）：`K141`/`K142` **桥接** `FPVIe0_FH_BUS↔FPVIe1_FH_BUS` 与 `FPVIe0_FL_BUS↔FPVIe1_FL_BUS`；QTMU 默认路由"require exactly the relays that **merge FPVIe0 and FPVIe1 into one node — which destroys TM600's two independent floating loops**"。
- QVM（`S8_QVM_CH0+`）不成 Kelvin 对：`CH0+ → PMID_F_S1`（role=F HIGH）而 `CH0- → SW_S_S1`（role=S LOW）；ACM200 只有到 SW 的通路（`S5_ACM200_SH8 → SW_S_S1`），**到不了 PMID**。

**生效结论（覆盖此前所有版本）**：**ΔV 主候选＝(a) FPVIe 自身 Kelvin 通路**（`S1_FPVIe_SH0→PMID_S_S1`[83]、`S1_FPVIe_SL0→SW_S_S1`[60,61]、`S1_FPVIe_SH0→PGND_S_S1`[154,155]；F/S 走独立 BUS 线）；**(b) 记为"除非 t3 另找出具备独立 Kelvin 分线的仪器表，否则本次不可交付"**，并**必须附 IR 反证**；**禁止** PC 通路（`K90/K91 + K82_R_CS`，串 `R1_CS_S1 100 mΩ±1%` / `R2_CS_S1 5 mΩ±1%`）。
**遗留未知（唯一）**：**驱动层** —— `FPVIe_RELAY_SENSE_ON`（或何种设置）才把 FPVIe 内部感测放大器接到 `SH_BUS`/`SL_BUS` 而非 PC 通路。该槽位在 plan 中保持**显式 PENDING**。

### `hazards[]` 中其余已确认的强约束（已随契约下发）

- `high-current`：只有 **FPVIe（±10 A）** 能供 1 A（ACM200 ≤±200 mA、FXVIe_PLUS ≤±1 A 脉冲）；**回路两端都必须经 BUS 继电器**，否则引脚留在默认源上并把两台仪器短接。要求的继电器：TM600 = `K83`(PMID) + `K60/K61`(SW)；TM601 = `K60/K61`(SW) + `K154/K155`(PGND)。
- `shared-resource`（每通道一根高/低 BUS 线）：**同一 BUS 线上只能闭一个引脚继电器**（同时闭 `K83` 与 `K154` 就把 PMID 短到 PGND）。
- `shared-resource`（SW/VCP 共用 BUSL_VCP）：`K61` 闭合期间 `K68/VCP` 支路必须**惰性**。
- `shared-resource`（FPVIe 通道预算）：**TM600 与 TM601 必须拆成独立函数**，不得合并（`bus-topology.md 八` 禁止 HS/LS 合并；`0x59=0x01` vs `0x02`、PMID 电压不同、热开关风险）。
- `shared-resource`（K93_AGND2PGND，medium）：**TM601 期间保持 OPEN**；若必须启用，需验证 1 A 回流在 `R_PGND_S1` 上的压降不会把 `AGND_F_S1` 抬出限值。
- `shared-resource`（AMUX/PGND 同属 `S3_3` 组）：**TM102/TM103（AMUX 电压）与 TM601（PGND 回流）不得同 site 并行**，需串行。
- `shared-resource`（VCC/ACDRV 共用 `BUSH_ACDRV`，medium）：`K25`+`K30` 视为**原子共享资源**（2026-08-26 曾有意未把 `K25` 定义为短接继电器，故已发布定义里没有警告）。
- `shared-resource`（FXVIe_PLUS 默认常通 `K84_HG2`→PMID，medium）：FPVIe BUS 接管 PMID 时必须显式决定 `K84` 状态，避免默认源与 FPVIe 互抢。
- 跨站共享：`K85_CAP_PMID_S1S2`、`K57_CAP_BST_SW_S1S2`、`K87/K89_KELVIN0_S1S2` 等**跨 S1/S2，两站不能独立开关** → 并行站点受限于此。

## 里程碑：t3 完成（verdict=pass），t4 解锁；ΔV 槽位**关闭** = (a)（16:5x）

| 项 | 实测 |
|---|---|
| t3 产物 | `setup-contract.json` **190,534 B**，`validate_team_artifact.py setup-contract` → **PASS**；配套 `setup-contract-build.py`、`sch-paths.json`（367 条）、`sch-paths.txt`、`setup-recon.md` |
| 契约规模 | 70 resources / 12 aliasResolution / 12 globalInitialization(R-PON) / 8 globalCleanup(R-POFF) / 10 tmDeltas / 19 safetyInvariants / 13 conflicts / 11 openItems |
| 别名表（必交付，已落实） | `pmid2sw → FPVIe0 CH0 High PMID(K83)+Low SW(K60,K61)`；`sw2pgnd → FPVIe0 CH0 High PGND(K154,K155)+Low SW(K60,K61)`；`bst2sw → FPVIe1 CH1 High BST+Low SW(K131,K132,K134,K135)`；第一来源＝DFT.csv 行内 sense-path 标签列，已与 `gen_paths.py` BFS 交叉校验；旧代际 K 名已换算 |
| 团队状态 | t1✅ t2✅ **t3✅** → **t4 解锁**；t5–t9 待命 |

### ΔV 感测槽位：关闭为 (a) FPVIe 浮动四线（有 3 条独立证据）

1. **夹具级**（Captain 实读 `schematic-ir-sensing.json` 现盘）：`dfdPairVerdicts` 对 PMID↔SW 与 SW↔PGND 均 `kelvinPairAvailable: true`、**`fourWireProper: true`**、`senseKind="genuine 4-wire (BUS route never enters the PC nets)"`；`requiredPairAssertions` 三条 `found: true`（含 ch1 BST↔SW）；`unreachableNodes = []`。
2. **排他性**：`nonKelvinInstruments` 明确否决全部四个独立仪表 —— `QTMUe`（低端 DGND/单线）`invalidFor: mOhm differential RDSON`；`QVMe`（一引线落 force 网，非 Kelvin 对）；`ACM200`（仅到 SW、±200 mA，不能供 1 A）；`FXVIe_PLUS`（低端回 AGND_F，**无法构成浮动对**）。→ **(b) "两点单端相减"在本次夹具上不可组装**，记为"本次不可实施"，不再作基线。
3. **本 TM 专属黄金先例**：`knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp:91` 原文 `hs_rdson[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1e3;//mohm` —— 归档实现正是 (a)。（符号/继电器号为旧代际，**只取结构不取符号**。）

### Captain 第六次自我更正：撤回"引线/继电器电阻"论据（结论不变）

我先前用"源端两线自读会把继电器/引线电阻算进去"论证必须用独立电压表 —— **该论据不成立**：`bus-topology.md:104` 要求 FH/SH 与 FL/SL 全程连通到 PAD，t2 的 `singleEndedEvidence` 亦显示 FPVIe 的 sense 端子（`SH0→PMID_S_S1`[83]、`SL0→SW_S_S1`[60,61]）与 force 并行到 DUT 引脚，**本就是真四线**；两线退化只发生在力/感短接桥 `K86`/`K130`（SD-2）。**正确理由是排他性**（第 2 条）：没有第二台仪器能在 Check 对两端都取到单端读数。由 ate-implementer 提出、Captain 复核后采纳。

### 继电器状态权威（裁定）

**以 `SCH-Connect-Map.txt` 的图例 + 逐行"需闭合:"列表为 SetOn 权威**；脚本级依据：`gen_path_defines.py` 自述"数据权威: SCH-Connect-Map.txt 的 group head `需闭合:` 列表 = 该通路全量 SetOn 集"。**禁止**从某个全局 NC/NO 极性规则反推继电器状态（IR 的 `gatingRelayDefaultState` 类表述只对具体继电器成立）。t3 登记的 5 处分歧按此逐条裁决并由 t4 写入计划；`relay-trace` 门为执行校验。**不为此新建修复任务**（避免为形式完整性消耗一轮真实工作；冲突已在 `setup-contract.conflicts` 与本节留痕）。

### 哈希时效（本 run 第 N 次踩到，务必现算）

| 产物 | 成员引用值 | **Captain 实测现盘值（权威）** |
|---|---|---|
| `schematic-ir-sensing.json` | 39593 B / `dc52dca4…` | **47156 B / `ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140`** |
| `schematic-ir.json` | 450689 B / `ed77ccae…` | 一致（450689 B / `ed77ccae15f45853…`）—— 该文件在 447580 B/`3ed7a4d7…` 之后又被推进一版，前者作废 |

**规则重申**：交付物可能在被引用后继续重生成 → **任何引用前必须现算哈希**。

## 资源仲裁裁定（Captain，16:5x）：采用夹具证据，黄金的双独立源方案列为待证备选

**争议**：黄金案例（`tm600-normal-highcurrent.cpp` L10-11/L37-49）用**两个独立接地参考源**（`BTST_ACM`+`SW_ACM`）实现 BST−SW=5 V，**不占 FPVIe 通道**（其口径只需 1 个 FPVI 通道）；而 t2 的 IR `resourceConflicts.fpvieChannelBudget` 称 TM600 需 FPVIe0（PMID↔SW 1 A）+ FPVIe1（BST↔SW 5 V），**两通道占满**。

**裁定**：
1. **采用夹具证据**：t3 的别名表（源自本夹具 BFS + DFT.csv 行内标签）给出 `bst2sw → FPVIe1 CH1 High→BST / Low→SW`，故本次按**两通道**方案实现，`SD-1`（TM600/TM601 必须拆成独立函数）保留生效。
2. **黄金的双独立源方案列为备选**，**须先取得夹具证据**（当前 t2 已证 `ACM200` 只能到 SW、`FXVIe_PLUS` 只能到 PMID/PGND 且无法构成浮动对 → **到 BST 的非 FPVIe 通路无证据**）才能采用；一旦取得，可释放 FPVIe1 并使 (c) 方案（ch1 作第二只浮动电压表）复活。
3. 黄金的其余可取之处按"**只取结构不取符号**"采纳：`FV=0 → FI=0 → SetClamp` 三段式、4 级 BST 台阶（BST 恒领先 5 V）、下电时 FET 全程导通 + 反向台阶、`RELAY_OFF` 统一量程 10V/10MA、**FPVI 最后断开** —— 正好是 E006 不变量的落地形态。**不得照抄**其旧代际寄存器（`0x58/0x10/0x59/0x61 = 0x00/0x43/0x01/0x0B`）与旧符号（`FPVI`/`FPVI_RELAY_ON`/K31/K17/K18/K32/K30/K28）。
4. 采样数按 TM600 专属黄金取 **`MeasureVI(200, 5)`**（live 先例为 `(50,5)`；条目内标注两处来源差异）。

## Captain 第七次自我更正 + 感测激活方式收口（17:0x）

**我的两处错（由 ate-implementer 抓出，Captain 逐条复核确认）**：
1. 我称"`FPVIe_MV*` 在项目内 0 次"——**不准确**。实测 `Test_Method.cpp` 的 `FPVIe_MV_X1`/`FPVIe_MI_X1` 各 **36 处**（如 `:288/:559/:704/:895` 的 `MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG)`），其余文件 0。正确表述：**增益实参在方法库层有先例，但只用 X1 默认；`FPVIe_MV_X10` 确为首次**。
2. 我在裁定中写过 `FPVIe.Set(...)`——**对类名用点号是无效 C++**。正确：全局对象 `FPVI0`/`FPVI1`（`extern FPVIe FPVI0;` 见 `Pin_Channel_define.h:120-121`），写法 `FPVI0.Set(...)`（或类限定 `FPVIe::Set(...)`）。

**同时确认的事实**（Captain 实测）：`FPVIe_RELAY_SENSE_ON` / `FPVIe_CONTACTMODE` / `FPVIe_HIGH_MV` / `FPVIe_LOW_MV` 在**全部项目源码命中 0**；`FPVIe_MV_X10` 命中 0；FPVIe 的 `GetMeasResult(MVRET)` 在 test.cpp/sub.cpp/Test_Method.cpp 命中 0（**但有本 TM 黄金先例**，见下）。

### 裁定：本 run 采用"最小首次使用面"

```
FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
FPVI0.SetClamp(50, 50);          // provisional；每次 FV/FI 切换后重发
delay_ms(2);
FPVI0.MeasureVI(200, 5, FPVIe_MV_X10);
R[mΩ] = FPVI0.GetMeasResult(site, MVRET) / FPVI0.GetMeasResult(site, MIRET) * 1e3;
FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
```

1. **本 run 不使用** `FPVIe_RELAY_SENSE_ON` / `CONTACTMODE` / `HIGH_MV` / `LOW_MV` —— 其必要性属**仪器配置事实**，本次**只做代码与编译、不授权上机**，无法取证。→ 写入 **U9（bench 验证项）**：若上机发现 `RELAY_ON` 下感测回路未激活，则 `SENSE_ON`+`CONTACTMODE`（配 `HIGH_MV`/`LOW_MV`）为**文档化备选**。
2. **首次使用面收敛为 1 项**：`FPVIe_MV_X10`（论证：10 mV 级差分需在 1 V 量程取增益；**拒绝** `FPVIe_100MV`，因失败件在 ±0.5 V clamp 下会先饱和）。FPVIe `MVRET` 读取标注为"**黄金支持、项目首次**"（`tm600-normal-highcurrent.cpp:91`）。其余形态全有先例（`FPVIe_RELAY_ON` 289 处、`Set`、`MeasureVI`、`MIRET`）。
3. **边界句写入计划与报告**：本次交付＝**代码与编译闭环**；**感测端子激活方式与 clamp 数值均为 provisional/工程默认，须上机验证**。limitations 含 U1、U2、U3–U8、U9。

## Captain 裁定 BD-04（17:1x）与 IR 冻结决定

**BD-04 裁定：TM108/TM109 上升阈值采用 OVERVIEW 的 4.4 V**；`DFT.csv` 的 4.15 V 作为**已登记冲突**逐字保留（禁改写/平均/删除）。
依据：① 与用户 BD-01 **同源判据**（同一对文档、同类限值分歧 ⇒ 同一权威规则：`project_config.json` 以 DFT xlsx 为权威输入、OVERVIEW 为当前意图层且有 sheet/row 定位）；② `DFT.csv` 的 TM109 行**自相矛盾**（ramp `vac3` 而该项语义为 VAC2_PRST、DMUX 抄成 TM108 的 22 —— 由 t1 与 t2 各自独立发现）；③ 本裁定系 Captain **依用户判据类推**，**可被用户裁定覆盖**（可逆性已声明）。
当前状态：**BD-04 关闭**；**BD-05 已由用户关闭**（clamp provisional ±0.5 V）；仅剩 **BD-07**（`Y / 2 FLOAT` 语义，按"两浮动节点"假设并标注）与 **BD-06**（TM1205 无数值限值 → 记入 limitations）——二者均以"标注假设/记入 limitations"处理，**不作为 open blocker** 阻塞定稿。

**IR 冻结决定**：`dft-ir.json` **不再增补第五版**。理由：避免继续制造哈希 churn（本 run 已因重生成造成至少 4 次"引用哈希失效"）。IR v4 中"BD-05 仍 open"属**滞后**（v4 构建于用户裁定之前），其最终状态由**两处权威**承载：t4 的 `test-plan.json`（以用户裁定为准）与**本台账**（裁定/作用域总账）；t9 集成按此对账。

### 产物哈希登记（更新）

| 产物 | 大小 | python 明文 sha256 | 状态 |
|---|---|---|---|
| `dft-ir.json` | **116140 B** | **`82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568`** | **live（v4）**，已应用 R-01～R-04；v1/v2/v3（`f3faedc2…`/`478f88a4…`/`85db02e3…`/`0a1c3b1e…`）**全部作废** |
| `schematic-ir.json` | 450689 B | `ed77ccae15f458535015994d9dbbc6cd4c95c34b0bc283fae9cab32bcd06e41d` | live |
| `schematic-ir-sensing.json` | **47156 B** | **`ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140`** | live（成员引用的 39593 B/`dc52dca4…` 已过期） |
| `setup-contract.json` | 190534 B | 见 t3 交付（schema PASS） | live |

**规则**：交付物会在被引用后继续重生成 ⇒ **任何引用前必须现算哈希**（t9 隔离/一致性审计按此执行）。

## 用户裁定（最终一批，17:3x）：BD-01/04/05/06/07 全部收口

> **适用范围（唯一）**：仅适用于 `acceptance-20260916-dali10` 的 **debug 代码生成与编译**；**不授权真实上机**。不得据此执行硬件测试；不得改 `D:/PROJECT6-DALI/devel`。

| 编号 | 裁定 | 保留的冲突/条件 |
|---|---|---|
| **BD-01** | TM600 = **11 mΩ**、TM601 = **7.5 mΩ**（OVERVIEW） | `DFT.csv` 的 10 / 8 mohm **逐字保留**为已登记冲突；仅适用本次 debug 验收，发现更新版本须重开 |
| **BD-04** | TM108/TM109 上升阈值 = **4.4 V**（OVERVIEW） | `DFT.csv` 的 **4.15 V** ＋ **TM109 行的 vac3/DMUX 行内矛盾**保留为冲突 |
| **BD-05** | 沿用黄金 **`FPVIe.SetClamp(50,50)`**（1 V 量程 ⇒ **±0.5 V**）；**每次 FV/FI 切换后重发**；**1 A 脉冲上限 2 ms** | 标 **provisional / bench-signoff-required**；数值非数据表值、**非 pass/fail 判据** |
| **BD-06** | TM1205 **只做结构闭环**，**不发明 pass/fail 数值** | 写入 **limitations** |
| **BD-07** | 本次按"**两浮动节点**"解释 | 标为**可重开假设** |

**执行要点**：
- **1 A 脉冲 ≤2 ms**：与黄金实现一致（`delay_us(2000)` → 立即 `Set(FI,0)` 关断）。t5 的 sequence 必须体现"强制→2 ms 内测量→关断"，不得长时间保持 1 A。
- clamp 在 **FV↔FI 每次切换后重设**（`knowledge/sources/fpvie.md:141-168` 实测切换清除箝位）；本项**严于黄金**（黄金只设一次），t6 不得误判为偏离。
- 全部五项在 plan/manifest/review/acceptance-report 中一律标 **closed-by-user-adjudication**，并**并列保留**冲突侧证据与 locator。

### 边界句（写入计划、manifest、build-report、acceptance-report）

> **本次交付＝debug 代码生成与编译闭环**；不授权真实上机；**BD-05 的 clamp/脉冲参数与感测端子激活方式均为 provisional / bench-signoff-required**；编译与门禁通过**不等于**电性/硬件正确（且 1 A 强制的继电器触点额定值**尚无数据表证据**，见 U1）。

## 新增纪律：**"校验 PASS" 必须与"产物哈希变化"配对检查**（setup-architect 实测发现，17:4x）

**事例**：t3 重建 `setup-contract.json` 时脚本因 `single_aliases` 定义顺序抛 `NameError`，**构建实际失败**；但**旧文件仍在**，校验器对**陈旧产物**照样报 **PASS**。作者靠"重建前后文件哈希比对"才发现，删旧重建后才真正通过。

**推论（已写入纪律，t5/t6/t8/t9 一律遵守）**：
1. 任何"校验/门禁 PASS"结论，**必须同时给出该产物当前的现算哈希**，并证明它与**本次修订前**的哈希**不同**（或说明为何应当相同）。
2. 对"重新生成的产物"尤其危险：旧文件存留会让失败的重建表现为成功。 → **重建失败时必须先删除/改名旧产物**，再重跑并复验。
3. 该纪律同时覆盖**门禁**：`run_gates.ps1` 的 PASS 必须与"被试产物为当前修订"的证据配对（t8 的 build-report 需含此项）。

## 里程碑：t4 完成（verdict=pass），t5 已解锁（17:4x）

| 项 | 实测 |
|---|---|
| t4 产物 | `test-plan.json` **98,641 B**，sha256 `19e6f2c389db69a7c944a41883dc9af7b2b1083bfc495c2b4d0ed901b8e13cfe`；`validate_team_artifact.py test-plan` → **PASS**；生成器 `test-plan-build.py`（可复现）；另做结构自检 + **泄露扫描**（19 个 API/C++ token 命中 0） |
| 十项分类 | TM000 normal+grouped；TM001 normal+grouped；TM102 normal(pad MV)；TM103 normal(pad MI)；TM108 toggle+awg+grouped；TM109 toggle+awg；TM135 trim；**TM600 normal+high-current+differential(floating)**；**TM601 normal+high-current+differential**；TM1205 toggle+differential+awg+grouped |
| t3 补强版 | `setup-contract.json` 更新为 **216,717 B**，sha256 `9402a3c0c33f740ca4951309b6ec21f4b57fc5d0178a11163b22b9ab11edbc05`（旧 205,372 B/`96c9c2b4…` 与更早 190,534 B 均**作废**）；新增 aliasFlatTable(16)/aliasNamingVariants/measurementPlan/BD-07 未决项，既有裁定未改；schema PASS |
| 团队状态 | t1✅ t2✅ t3✅ t4✅ → **t5 解锁（实现阶段，首次写源码）**；t6–t9 待命 |

## Captain 裁定 BD-08（17:4x）：ATE 激励用 DFT/OVERVIEW，不采用 `.sv` 仿真域电压

**争议**：t3 契约的 TM600/TM601 上电序列用了 **reg_config 仿真域电压**（VBAT 3.5 V、PMID 5 V、TM601 vbus 5 V），而 ATE 激励为 **vbat 4.2 / pmid 15（TM600）、9（TM601）**，与我此前"`.sv` 激励不得覆盖 ATE 激励值"的裁定冲突。

**裁定**：ATE 激励一律按 **DFT/OVERVIEW 意图层** ——
- **TM600**：`vbat 4.2` / `pmid 15` / `bst2sw 5` / `vdrv 5`
- **TM601**：`vbat 4.2` / `pmid 9` / `vdrv 5`
`.sv` 的仿真值（3.5 / 5 / vbus 5）**不采纳**，改记 `simulationDomainReference`（**保留不删**）。

**依据**：① 与此前 BD-03 作用域限定一致（`.sv` 只在**寄存器映射**上权威）；② 与用户 BD-01 同源判据（DFT 意图层权威）；③ `.sv` 文件头 `generate time: 2026-05-15`，早于 LS/HS 位修正，其电压并非按本板 ATE 条件设定。
**状态**：`closed-by-captain-ruling`（非用户裁定，注明**可被用户覆盖**）。已下发 t4（计划 stimulus 用 ATE 值）、t5（按计划实现，不一致先回报）、t3 责任人（修订 `tmDeltas` 并把仿真值改记为参考）。

## 其他裁定与记录（本轮）

- **ΔV 维持 (a) FPVIe 浮动四线**，**不因 t3 的 QVM 观察重开**：t3 报"QVM ch0 是唯一单仪器两线差分（CH0+→K137,K83→PMID / CH0-→K138,K60,K61→SW）"，但 t2 的 `nonKelvinInstruments` 对 `QVMe` 判定为 "one lead lands on a force net → mixed F/S pair，`invalidFor: the mOhm Kelvin sense of TM600/TM601`"，而 (a) 已有**夹具排他性 + 归档 TM600 黄金先例**双重支撑。QVM 路线记为**备选证据（含反证）**。
- **新增 divergence（t3）**：① `bst1_sw1`/`bst2_sw2`（TM1205）在 connect-map 中 SW1/SW2 走 HIGH、BST1/BST2 走 LOW，与 `bst2sw`（BST 高）**极性相反** ⇒ "BST 领先 SW"须靠**电压符号**而非端子指派；② `bst2sw` 的 `K134/K135` 同现于 CH1 High→BST 与 Low→SW 两条"需闭合"列表（明细显示 force 对 K131/K134 与 sense 对 K132/K135 为不同线，倾向 F/S 合并记法）。→ 保留登记，**以 `SCH-Connect-Map` 逐行"需闭合"为权威**，由 `relay-trace` 门与 t6 校验。
- **命名变体实测**：`sw2pmid` 7 次、`pmid_sw` 10 次（**勿与 `.sv` 旧代际 `isrcPMID_SW` 混淆**）⇒ 纪律重申：token 检索必须声明拼写集合（含箭头/连字符/下划线变体），0 命中不得当作"不存在"。

### 产物哈希登记（更新）

| 产物 | 大小 | python 明文 sha256 | 状态 |
|---|---|---|---|
| `test-plan.json` | 98641 B | `19e6f2c389db69a7c944a41883dc9af7b2b1083bfc495c2b4d0ed901b8e13cfe` | **live（t4 交付）** |
| `setup-contract.json` | **216717 B** | **`9402a3c0c33f740ca4951309b6ec21f4b57fc5d0178a11163b22b9ab11edbc05`** | **live**；190534 B 与 205372 B/`96c9c2b4…` 作废 |
| `dft-ir.json` | 116140 B | `82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568` | live（v4，**冻结不再增版**） |
| `schematic-ir.json` | 450689 B | `ed77ccae15f458535015994d9dbbc6cd4c95c34b0bc283fae9cab32bcd06e41d` | live |
| `schematic-ir-sensing.json` | 47156 B | `ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140` | live |

## Captain 第八次自我更正：`rampi_capv` 判据必须是"新增量"而非"全树 0 命中"（rule-reviewer 实测拦下，17:5x）

**我的错**：我把"禁用 `rampi_capv`/`rampv_capv`"写成近似"全树不得出现"的判据，并据此下达 t5/t6 检查项。**实测基线**（python 明文读 `ForCodexDebug/source/test.cpp`）：
- `rampv_capv` = **78 处**（首 1955、末 8843）
- `rampi_capv` = **4 处**（7034/7124/7210/7552，**全部落在 TM607/608/609 区段 6956–7552**）

即两 token 在**既有基线中已大量存在**。若按"全树 0 命中"判，会对既有 **82 处**误判 FAIL。

**更正后的判据（t5/t6 一律按此）**：只判**新增量** —— t5 只要**未在 TM600/TM601 及其新增代码**中引入 `rampi_capv`/`rampv_capv`，即 **PASS**；既有用法属基线既有状态，**不得**计为 t5 新增门禁红。理由不变：`verify_bst_sw_sequence.py:78-114` 按"函数体内含 `rampi_capv(`"**行为自证**收目标，新增函数一旦含它就会被该门按硬编码精确串判 → **新增红**。
同类提醒：`verify_awg_params.py` E005 的 `_Rise/_Fall/_Hys` **既有 pre-existing 红**（TM425/607/608/609）同样属基线，不得算作新增；`cbit` 亦为已登记 KNOWN-RED。

## 门禁红判定通则（写入纪律）

**任何门禁的 PASS/FAIL 只看"相对于基线的新增"**，并须：
1. 给出**退出码 + 日志路径 + 日志哈希**；
2. 显式区分 **KNOWN-RED（基线）** 与 **NEW-RED（本次引入）**；
3. 对"某 token/函数是否出现"这类判据，**必须限定范围与新增量**，并声明检索的拼写集合与工具（pwsh 不可用于源码断言）。

## 产物哈希登记（更新：`test-plan.json` v2 为准）

| 产物 | 大小 | python 明文 sha256 | 状态 |
|---|---|---|---|
| `test-plan.json` | **113773 B** | **`7f1bdf976c721596b00203c38eef29d559701a7bbdaa06a2d045855265a86463`** | **live（v2）** —— 含 BD-04/05/06/08 状态收口、四项反证、MV_X10 论证、继电器权威规则、K 号最小 `_A` 宏、U1–U9 limitations；schema PASS |
| `test-plan.v1.json` | 98641 B | `19e6f2c389db69a7c944a41883dc9af7b2b1083bfc495c2b4d0ed901b8e13cfe` | **历史副本**（t4 终态 output 中登记的是该值 —— **t4 为 terminal，不能改**；**下游以 v2 为准，且一律现算**） |
| `test-plan-tm600-tm601-measurement-excerpt.md` | 见 t10 交付 | 见 t10 交付（现算） | 补充交接件（承载逐字调用形式；`test-plan.json` 本身保持"无 API 名/C++"以符合 t4 验收标准） |
| `dft-ir.json` | **130724 B** | **`d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b`** | **live = v6（CURRENT）**；含 CR-01..CR-06、TM601 `forceAndSense.force.pins=[PGND (High), SW (Low)]`、`.sv` 记号 SUPERSEDED-BY-RULING（逐字保留）、`fixtureEvidence`（含两条不存在的反向配对）、`FS-01=resolved-with-fixture-evidence`、`DD-01=resolved`、`evidencePreservation` |
| `dft-ir.json`（v1–v5） | 88109 / 88101 / 99058 / 107133 / 116140 B | `f3faedc2…` / `478f88a4…` / `85db02e3…` / `0a1c3b1e…` / `82398d2f…` | **全部作废**（**注意：`82398d2f…`/116140 B 是 v5，不是 v4** —— 本台账早前标签有误，已更正；权威链见 `dft-raw/dft-ir-hashes.json` 的 `hashHistory`） |
| `schematic-ir.json` | 多次重建 | 引用时刻现算（已测到 450689 / 453464 / 455650 / 455676 B） | **以现算为准**；t1 的 `fixtureEvidence.sha256 = 9f5643d1…` 是一个已登记锚点（**该文件缺全库权威哈希 → t9 须现算并登记**） |

**⚠️ 记账规则**：**terminal 任务的 output 里登记的哈希不可修改**（t1/t2/t3/t4 的 output 均已过期）。因此 **run 内唯一权威哈希表＝本表**，且任何引用**必须现算**后再使用。

## 关键补充：`FPVIe_HIGH_MV`/`FPVIe_LOW_MV` **不可达**（setup-architect 实测，18:0x）

`ATDriverPackGlobal.h` 的 `enum MeasRet` **只有** `{MEASTYPERET, MVRET, MIRET}`，且 `FPVIe_RET_RESULT`（`FPVIe.h:60-66`）**没有任何公共方法接受** ⇒ 该枚举**"已声明但无签名路径"**。

**影响**：本 run **明确不规划** `HIGH_MV`/`LOW_MV` 路径 —— 这与我们"最小首次使用面"的裁定**同向且更强**（不只是"无先例"，而是**不可达**）。因此：
- ΔV 唯一可用的自测读数是 **`MVRET`**（通道自身 SH0−SL0 差分的通用返回），`MI` 用 `MIRET`；
- `U9` 的范围相应收窄为：**只在 `FPVIe_RELAY_ON` vs `FPVIe_RELAY_SENSE_ON` 这一个激活模式维度上验证**（不再涉及分侧返回）；
- `FPVIe_CONTACTMODE` 仅经 `ContactCheck()`（`FPVIe.h:167`）可达，但那是**接触检查**、不是测量路径选择 → 同样不用于测量。

## t3 契约"感测可达性"三问答复结论（Captain 采纳）

1. **可达（[Kelvin]）**：TM600 `SH0→K88(NC)→K83(ON)→K84(NC)→PMID_S`（L167）＋ `SL0→K88(NC)→K60(ON)→K61(ON)→SW_S`（L176）；TM601 `SH0→K88→K154/K155→PGND_S`（L158）＋ `SL0→SW_S`。→ **方式 A 夹具级成立**。
   - Caveat：**`K88_KELVIN0` 同时承载 SH0 与 SL0**（一个感测继电器服务通道 0 两极）→ 不得假设逐极握手；且**必须走 BUS 路线**（PC 路线 `K90/K91`+`R1_CS 100 mΩ`/`R2_CS 5 mΩ` 为板级短接，禁用）。
2. **单端替代（若需要）**：PMID = `FXVIe_PLUS PMID_HG2`（K84 默认导通）/ `QVM ch0+`（K137,K83）；SW = `ACM200 S5_FH8/SH8`（K61）/ `QVM ch0-`（K138,K60,K61）；PGND = `FXVIe_PLUS PGND`（K155）/ `QVM ch0+`（K137,K154,K155）。**ACM200 无 PMID/PGND 组**（实测）。
3. **F/S 分类 = [Kelvin]**（BUS 路线）⇒ ΔV 可作真四线差分；PC 路线为 **[PC短接]**；另有 [单线] 情形但不落在本三节点。附加约束：`R_PMID_KLV`/`R_SW1_KLV` 为 **10 kΩ 串在 Kelvin 感测行**（= U2）。

**产物哈希更新**：`setup-contract.json` = **229,695 B / `ab07d6f9f67ec24696187367dd7671ab317dc39777cd61fccfb16abd6195eee2`**（live；190,534 / 205,372 / 216,717 B 三版作废）。

**完整性事实（已写入契约 `integrityNotes`，Captain 采纳为全队纪律）**：
1. **run 目录内 TSZ 使哈希工具分叉**：PowerShell `Get-FileHash` 与 python 的 SHA256 在**字节数相同**时不同；对照 run 目录**外**的 `team/schemas/setup-contract.schema.json` 两工具**完全一致**（`C7A84550…`）⇒ 是**透明加密层**、不是篡改。→ **下游一律 pin python 明文哈希**。
2. **上游 IR 在 t1/t2 完成之后仍被修订**（`dft-ir.json` mtime 14:15:18 / 130,724 B；`schematic-ir.json` 14:15:05 / 455,676 B）→ 契约已按 14:15 版整份重跑，`inputs[]` 12 条哈希构建时逐条校验 **stale=0**；`SCH-Connect-Map.txt`（`cc8009fb`）与 `DFT.csv`（`b92d203f`）全程未动 ⇒ 别名表不受影响。**若 IR 再变，用 `setup-contract-build.py` 一键重放。**

## **run 内权威哈希表（Captain 现算，18:2x）** —— 所有下游引用以本表为基准，**并仍须引用时现算**

| 产物 | 大小 | sha256（python 明文） | mtime |
|---|---|---|---|
| `dft-ir.json` | **130724 B** | `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b` | 14:15:18 |
| `schematic-ir.json` | **457531 B** | **`9f4a7707fb0a1b31f4f884dcac617c5273506de6c2a088a3b9c3f1b20683f639`** | 14:17:29 |
| `test-plan.json` | **113773 B** | `7f1bdf976c721596b00203c38eef29d559701a7bbdaa06a2d045855265a86463` | 14:15:48 |
| `setup-contract.json` | **229695 B** | `ab07d6f9f67ec24696187367dd7671ab317dc39777cd61fccfb16abd6195eee2` | 14:16:01 |
| `schematic-ir-sensing.json` | **47446 B** | `43ad8c84ed21290efbb8a955568cab382fdaa5a766405e44bd2f337633a818f8` | 14:07:07 |
| `dft-raw/dft-ir-hashes.json` | 13041 B | `0b9d29faa77e24a21f01c3be40b9bc800c621db94988ef600e3a3da3886fb91d` | 14:16:46 |
| `isolation-baseline.json` | 44144 B | `6268e0df03290d6d40468942a28b0a13b1caf9433d705e6d946085bcf30d2e83` | 13:40:32 |

**说明**：
- 全部产物**最后一次写入集中在 14:07–14:17**，此后未再变动（本轮现算确认）→ **对账窗口已稳定**。
- `schematic-ir.json` 先前被多人测到 450689 / 453464 / 455650 / 455676 B 四个值，**现盘为 457531 B / `9f4a7707…`**（dft-expert 在其 IR 里登记的 `9f5643d1…` 是**更早一版**，不是现盘）→ 已按现算值登记，**t9 审计须以现算为准**。
- 早期 `82398d2f…`(116140 B) 是 `dft-ir.json` 的 **v5**（台账早前误标 v4，已更正）；完整六版链见 `dft-raw/dft-ir-hashes.json` 的 `hashHistory`。
- 本表的存在**不替代**"引用时现算"纪律：terminal 任务 output 里的哈希（t1–t4）**全部过期且不可修改**，唯一权威是**现算值 + 本表对照**。

## Captain 裁定：K87/K88/K89 = **保持默认（不得 SetOn）**（18:4x，关闭 t5 新开项 6.15）

**争议**：t2 的 `hazards[measurement-validity]`/`kelvin-integrity` 把 mitigation 写成 "use the FPVIe BUS Kelvin route (**K87/K88/K89** for channel 0)"，而现行 `StdAfx.h:251-253` 把这三个命名为 `K87_FPVI0_FH_SL_SHORT`、`K88_FPVI0_Sense_FLOAT`、`K89_FPVI0_FL_SH_SHORT` —— 按字面**激励**它们会把 force 与 sense 短接，与 t2 的本意相反。两种读法导出**相反的继电器状态**，错则 4 线退化 2 线（∓几十 %）或感测完全失效。

**裁定（依三条既有证据链）**
1. `SCH-Connect-Map.txt` **L4 图例**：`Relay-ON=需SetOn闭合, Relay-NC=默认导通`；**L9-12** 明确 `S1_FPVIe_FH0→K87(NC)→FPVIe0_FH_BUS_S1`、`SH0→K88(NC)→…SH_BUS`、`FL0→K89(NC)→…FL_BUS`，组头写 **"需闭合: 无(默认导通)"**。
2. `StdAfx.h:251-253` 的名字描述的是**被激励的那一侧**（`FH_SL_SHORT`/`FL_SH_SHORT` = SetOn 后才短接；`Sense_FLOAT` = SetOn 后才把感测切到浮动/本地）。
3. 既有裁定：继电器状态**以 `SCH-Connect-Map` 图例 + 逐行"需闭合"为 SetOn 权威**，禁止由名称反推。

**结论**：**K87/K88/K89 一律保持默认态（不 SetOn、不置 OFF）**；t2 的 "use K87/K88/K89 route" 应读作"**路由经过**这些继电器（默认态）"，**不是**"激励它们"。
路径上真正需要闭合的仅：TM600 = `K83` + `K60,K61`；TM601 = `K154,K155` + `K60,K61`。同时 `K141/K142` **OPEN**、`K86/K130` **OPEN**、TM601 期间 `K93` **OPEN**。
**实现要求**：在 setup 注释/计划引用中显式写明"K87/K88/K89 = 默认态、不得 SetOn"，并在 manifest 证据中引用本裁定（含 `SCH-Connect-Map` L4/L9-12 与 `StdAfx.h:251-253`），避免 t6 误判为"漏闭合 BUS 入口继电器"。

## 其他本轮确认（提升证据等级）

- **BD-05 的"切换后重发 clamp"由手册明文支撑**（不再只是 Captain 要求）：`knowledge/sources/fpvie.md:141-168` —— "Clamp settings are mode-dependent. Switching between FV/FI modes clears clamp settings back to **102%**. Within the same mode, clamp settings persist."，且手册示例本身在模式切换后重发 `SetClamp(25,25)`；`percent_PFS/percent_NFS` 为满量程百分比、有效范围 10–102%。→ 请在 manifest 引该出处。
- **两种来源的独立性再获佐证**：归档修订把 **11/7.5 mΩ 与 `pmid 5 V`** 配对、`DFT.csv` 把 **10/8 mohm 与 `pmid 15/9 V`** 配对 ⇒ 独立支持我们"两套来源并存、以 OVERVIEW 为验收限值、CSV 保留为冲突"的裁定。
- **t2 的 `limit-inconsistency` hazard 文本已过期**：仍把 `iset` 第三槽读作"1 mA/1 µA compliance"；**已被裁定取代**（第三槽 = ramp 时间：TM600 1 ms / TM601 1 µs）。已通知 t5 不沿用，并记为过期文本（IR v6 未增版，故不改写）。
- **t2 的 `schematic-ir.json` 定稿 = 457,531 B / `9f4a7707…`**（与我 18:2x 现算一致）；它新增了 `claimDigest` 内容锚定 + `expectations` 断言 + 负测试（B：无关字段 churn 不动摘要；C：反转 TM601 极性触发摘要变化与期望失败；D：改 TM600 iset 触发期望失败），并**自查出自身一处 bug**（期望断言未进证据记录 → 已修）。→ 这是本 run 证据锚定做法的**最佳实践**，值得 t9 引用其 `validation.evidenceStability`。

## 用户终裁（BD-04 + BD-08，19:0x）：ATE 激励唯一口径 + 两份产物同步修订

**BD-04**：TM108/TM109 = **OVERVIEW 4.4 V**；`DFT.csv` 4.15 V 与 TM109 行 vac3/DMUX 矛盾**保留** → `test-plan.json` 该项状态 `closed-for-this-run`。

**BD-08（唯一 ATE 激励口径）**：
- **TM600：PMID = 15 V**、**TM601：PMID = 9 V**、**standby/supply（VBAT）= 4.2 V**；
- `tm600.sv` / `tm601.sv` 的 **5 V / 3.5 V 属 simulation-domain stimulus，只可用于寄存器映射证据，不得覆盖 ATE 激励**；
- **禁止混合两个值**（不得以 5 V 作激励、不得 3.5 V 与 4.2 V 混用、不得并存于同一激励语句）。

**修订范围（用户明确要求"两份同步"）**：
1. `test-plan.json`（t10，进行中）→ 状态收口 + ATE 激励值 + `.sv` 值改记 `simulationDomainReference`；
2. `setup-contract.json` → `tmDeltas` 激励字段改为 ATE 值，`.sv` 仿真值改记 `simulationDomainReference`（注明"仅寄存器映射/仿真域参考"）；**两者都要重过 schema 并再公告新哈希**；
3. **下发 t5**：激励一律用 ATE 值；寄存器仍用 per-TM `.sv` 映射（`.sv` **唯一**被采纳的用途），在 manifest 中把"激励来源"与"寄存器来源"**分开标注**，避免被读成混用。

`.sv` 仅在被采纳的**寄存器映射**维度上权威；其激励值**永不**进入 ATE 序列。此口径已写入 t3/t4/t5 的指令。

## Captain 终裁：BST−SW 回路 = **FPVIe ch1**（黄金双独立源方案不采纳）（19:1x）

**分歧**：t4 主张按黄金用 `BTST_ACM + SW_ACM` **双接地参考源**实现 BST−SW=5 V 以**省下一个 FPVIe 通道**；而我的资源仲裁裁定与 t2 的 SD-1 都要求 TM600 用 `FPVIe0`(PMID↔SW 1 A) + **`FPVIe1`(BST↔SW 5 V)**。

**裁定：维持 FPVIe ch1，不采用黄金双源安排**。理由＝**缺夹具证据**（非偏好）：
- t2 实测：`ACM200` **只到 SW、到不了 BST**；`FXVIe_PLUS` **只能到 PMID/PGND 且低端回 `AGND_F`、无法构成浮动对** ⇒ 本夹具**无证据**表明存在可承担 BST−SW 的非 FPVIe 源对。
- 黄金用**旧代际**源名（`BTST_ACM`、`PMID_FOVI` 现行命中 **0**），照搬须先重新推导现行源。
- t2 的 `channelAllocationPerTm`：TM600 吃满 ch0+ch1（PMID↔SW 3 继电器、BST↔SW 5 继电器），TM601 只需 ch0 ⇒ **TM600 是约束方**，**SD-1 继续生效**。
→ 黄金方案记为 **`alternative-not-adopted`**，采用前提＝"夹具证据证明存在可达 BST 的非 FPVIe 源对"。

## 口径更正与加强（19:1x）

1. **采样数**：我此前"live 先例是 50"**过粗**。实测：`test.cpp` 全部 **56 处 `(50,5)`**、无 `(200,…)`；但 `sub.cpp` 有 **`(200,10)` ×4**、`BoardCheck.cpp` 亦有 `(200,10)`。→ 若采用 `(200,5)`，记为**"黄金取值；比任何 TM 级代码更平均；对正确性中性，只影响噪声与测试时间"**。
2. **clamp 触发＝失效特征**：黄金注释给出 "0.5 V compliance ⇒ 最大可测 RDSON = 500 mΩ" ⇒ **≥500 mΩ 时源被箝位、读数无效**；实现注释须写明，t6 按"保护而非限值"读（与 BD-05 一致）。
3. **(a) 的结论由"判据满足"升级为"归档原生实现且唯一可组装"**：`tm600-normal-highcurrent.cpp`（＝`Rdson.cpp`，6106 B，`8cdb0be1…`）原生即 `GetMeasResult(MVRET)/GetMeasResult(MIRET)*1e3`（L91）＋序列 `FV0(L79)→FI0(L80)→SetClamp(50,50)(L82)→FI=1(L85)→delay_us(2000)(L86)→MeasureVI(200,5)(L87)→立即 FI=0(L88)`；叠加 t2 对 `QVMe`（mixed F/S）、`QTMU`（DGND 单线）、`ACM200`（到不了 PMID）的三重否决 ⇒ **live 的 ACM 单端相减在本网表上无法组装**。
4. 黄金"结构可取、符号不取"的清单再确认：4 级 BST 台阶（BST 恒领先 5 V）、下电时 FET 全程导通、**FPVI 最后断开**（L131）＝E006 的落地形态；**不取**其旧寄存器（`0x58/0x10/0x59/0x61`）与旧符号（`FPVI`/`FPVI_RELAY_ON`/K31/K17/K18/K32/K30/K28）。注意 `RELAY_OFF` 量程按**我们的** `FPVIe_1V/FPVIe_10MA`（黄金用 10 V/10 MA）。

## 时序裁定：**两个版本角色**（19:3x）—— 冻结实现输入，审查输入后置

| 产物 | 实现依据（t5 期间冻结） | 审查/集成依据（后置） |
|---|---|---|
| `test-plan.json` | **v3 = 121694 B / `2e93a46c54c79b9028940840f6cf162d15304f89df3c3e88dd5fdea5f5061eda`** | **v4**（t11，待 t5 完成后收口：BD-04 用 `closed-for-this-run`、BD-06 改已关闭、BD-07 进 limitations 并标可重开、`bench-signoff` 关键词、用户边界句原样、新增 U10；**不得新增工程约束**） |
| `setup-contract.json` | **立即修订（t12）**：激励改 ATE 值 + `simulationDomainReference` 迁移 + U10 | 修订后版本为唯一依据 |

**裁定理由**：v4 的差异**只有 1 条与代码相关**（BD-05 的 **1 A 脉冲 ≤2 ms**），该条已由 t4 与我**点对点**下发给 t5 ⇒ 代码不会被带错；其余为状态名/边界句/limitations，属 t6/t9 的输入，**晚一轮不产生返工**，且能保持 t5 输入哈希稳定、便于"实现 vs 计划"一致性核对。
**例外**：`setup-contract.json` 的激励错误**与代码直接相关**（t5 要照契约写上电序列），故**不后置**，立即修订；t5 一律按 ATE 值实现（TM600 `VBAT 4.2/PMID 15/BST-SW 5/VDRV 5`；TM601 `VBAT 4.2/PMID 9/VDRV 5`），并在 manifest 注明该修订发生在实现期间。
**t9 对账**：按上表区分"实现依据 / 审查依据"两条哈希，二者差异已在此声明，不构成不一致。

**采纳 t4 的 `hashPolicy` 为全队做法**："inputArtifacts 哈希＝构建时快照；消费方**必须现算**；失配属**正常漂移**（本 run 已 7 次以上）；**实质事实一律用 key/locator 引用，不用哈希引用**。"

## 🔴 用户一致性门（19:4x）：**上游收口前禁止写入 debug 副本**

> **t5 可保持 claimed，但在 t11/t12 完成、且 `test-plan.json` / `setup-contract.json` 的最终 python 明文哈希 + 关键裁定摘要发给 ate-implementer 之前，不得写 `ForCodexDebug`。** 完成后让 t5 以"**内容键/locator + 最终快照哈希**"重新确认输入；**不要边改上游边写源码**。当前 `test.cpp` 仍是基线 `5c9cb3f9…3317`。

**门禁执行状态**
| 项 | 状态 |
|---|---|
| t5 | **claimed（attempt 1）**，已下 **HOLD 令**（可做 run 目录内的只读准备与 manifest 草稿，**禁止写 ForCodexDebug**） |
| t11（`test-plan.json` v4） | **立即执行**（原"v4 后置"方案**作废** —— 门禁要求两份先收口） |
| t12（`setup-contract.json`） | **立即执行**（激励改 ATE + `simulationDomainReference` 迁移 + U10 + QVM 措辞降级） |
| 基线未被触碰 | **已复核**：`test.cpp` `5c9cb3f9…3317`（434629 B，mtime 09-13 22:40）、`sub.cpp` `e86d49be…c391470`、`StdAfx.h` `ba8ab3de…aab6aee6` —— 与 `isolation-baseline.json` 一致 |

**放行条件（全部满足才发"输入确认"给 t5）**：① t11 完成且 schema PASS；② t12 完成且 schema PASS；③ 我**现算**两份产物的最终 python 明文哈希；④ 把**关键裁定摘要**（BD-01/04/05/06/07/08、U10 SIGN-CONVENTION、DV-01=(a)、K87/K88/K89 默认态、ATE 激励值、1 A ≤2 ms、clamp 每次 FV/FI 切换后重发、禁 ramp 家族**只看新增量**）与两哈希一并下发；⑤ t5 **回填输入确认**（内容键/locator + 快照哈希）后才开始写源码。

## 编号与措辞裁定（19:4x）

- **`U10` = SIGN-CONVENTION**（我方分配）；t3 新报的"QVM ch0 与 FPVIe0 同时强制同节点的并发性无文档" → 编为 **`U11`**。
- **DV-01 维持 (a) FPVIe 浮动四线**，**不改判 QVM**。依据：① 已裁定；② t2 `nonKelvinInstruments` 判 `QVMe` = "one lead lands on a force net → mixed F/S pair；invalidFor: the mOhm Kelvin sense of TM600/TM601"；③ (a) 有归档 TM600 原生实现（`MVRET/MIRET×1e3`，黄金 L91）＋端子排他性。
  → t3 契约 `measurementPlan` 的 `voltageDifferentialPreferred` 措辞**必须降级**为 **"candidate, disputed with t2"**（备选与反证并列）。

## 🛑 硬阻塞：t5 因**沙箱写权限**失败（环境阻塞，非设计阻塞）（20:0x）

**现象**：t5（实现）**failed**。根因：目标树 `D:/PROJECT6-DALI/ForCodexDebug` 在会话工作区（`D:/Newtest/DSH/ATE-Coding-Plat`）**之外**，沙箱以 `workspace-write` 拒绝写入（`file access denied under workspace-write mode`）；成员按升级规则**重试一次并申请 `danger-full-access`，被用户拒绝（final）**，随后未做任何绕行。

**目标树可证明未被触碰（Captain 现算复核）**：
| 文件 | 大小 | python 明文 sha256 | 起始 mtime |
|---|---|---|---|
| `source/test.cpp` | 434629 B | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca…3317` | 09-13 22:40:01 |
| `source/sub.cpp` | 121909 B | `e86d49bef7ae725106311d8205df6dbc11184c7a…c391470` | 08-30 23:34:00 |
| `source/StdAfx.h` | 56968 B | `ba8ab3de1b0c35cb7e9a477bd0b385f80671dc510…aab6aee6` | 08-30 11:20:05 |
→ 与 `isolation-baseline.json` 一致；`devel` 未动；未执行编译。

**已在工作区内完整交付（可随时应用）**：
1. `implementation-payload-TM600-TM601.cpp` — 13121 B / `2cd1ee725049d014…`：两个函数的**完整函数体**，供逐字追加到 `src/test.cpp`，带应用头（before-hash、字节模式要求、标识符出处、声明的首次使用）。
2. `backups/test.cpp.before_TM600_TM601.bak` — 434629 B / `5c9cb3f9…3317`，写前已验证与实盘逐字节相同。
3. 就绪插入脚本（备份 → 校验 → 字节模式追加 → 复验 → BOM/CRLF/行数检查）：`%TEMP%\insert_tm600_601.py`。**必须用 python**（编辑器/`Copy-Item` 会破坏 DLP 文件：文本模式把 CRLF 变 `\r\r\n`，PowerShell 复制得到空文件）。
4. 内容严格按已签收的 `test-plan.json` + `setup-contract.json` 构建（ATE 激励、per-TM `.sv` 寄存器、K83+K60,K61 / K154,K155+K60,K61、K93/K141/K142/K90/K91 不动、`FPVIe_2A`、`MeasureVI(200,5,FPVIe_MV_X10)`、R-VIR、禁 ramp 家族、`FPVIe_RELAY_ON` 小写 e）。

**下游影响**：**t6/t7/t8 在当前状态下无法出绿** —— 没有源码变更可审、没有可编译对象；若权限不解决，t6/t7/t8/t9 应报 **blocked**（而非按各自职责判失败）。

## 一致性门执行状态（20:0x）

| 项 | 我现算验收结果 |
|---|---|
| t11（`test-plan.json` v4） | ❌ **未落地**：`bench-signoff`=0、`closed-for-this-run`=0、BD-04 仍 `closed-by-captain-ruling (analogous)`、BD-06 仍 `OPEN (accepted…)`、BD-07 不在 limitations、无 U10（文件仍 = v3 `2e93a46c…`），已催 |
| t12（`setup-contract.json`） | ❌ **未落地**：`simulationDomainReference`=0、`U10`=0、`voltageDifferentialPreferred`=4、`disputed`=0，Step 2 仍为 `VBAT=3.5 V, PMID=5 V`（TM600）与 `VBAT=3.5 V, VBUS=5 V`（TM601），已催 |
| 放行 t5 写源码 | ⛔ **双重未满足**：① 上游未收口；② **沙箱权限**（决定性） |

**门禁不变**：上游收口 + 最终哈希与裁定摘要下发 + t5 回填输入确认 **之后**才允许写 `ForCodexDebug`。但因权限阻塞，**该门目前无法被满足** —— 需用户决策（见我给用户的选项）。

## U 编号统一表（Captain 定，20:1x）—— 跨产物唯一口径

| 编号 | 内容 | 承载产物 |
|---|---|---|
| U1 | 继电器 1 A 触点额定值无数据表证据（上机前硬件签核） | plan + contract + manifest |
| U2 / U2b | 10 kΩ KLV 串阻 vs FPVIe 感测输入（**U2b 给数值判据**：偏置电流 ≤ **11 nA**(TM600) / ≤ **7.5 nA**(TM601)；实测 `R_PMID_KLV_S1=10K` 接 PMID 轨 ↔ `NetK84_HG2_S1_7`，**SW 引脚本身无 Kelvin 串阻**） | 同上 |
| U3–U8 | t3 的既有 openItems | 同上 |
| U9 | `RELAY_ON` 是否足以激活感测回路（`HIGH_MV/LOW_MV` 经实测**不可达**，已排除） | 同上 |
| **U10** | **QVM ch0 与 FPVIe0 同节点并发性无文档**（计划已用此号） | plan（+ contract 引用） |
| **U11** | **SIGN-CONVENTION**：FPVIe ch0 端子指派由网表固定（PGND 仅 HIGH 侧、SW 仅 LOW 侧）⇒ `iset` 符号须按"别名方向 → 仪器端子 → 命令符号"三步推导；**按 DFT 字面方向实现、不得静默反号**；bring-up 判据三条；**不上报用户** | plan + contract |
| **SENSE-FORM** | 远端 Kelvin 驱动层动作 **NOT DETERMINABLE**（无手册镜像）；槽位 PENDING + 判据 | contract |
| BD-06 / BD-07 | TM1205 仅结构闭环（无数值判据）／`Y / 2 FLOAT` 两浮动节点（**可重开假设**） | plan + report |

**起因**：我先给 `U10=SIGN-CONVENTION`，而 t4 已用 `U10=QVM 并发性`。**以本表为准**（避免跨产物重复编号造成 t6/t9 对账错位）。

## 验收记录（20:1x）

| 产物 | 现算 | 验收 |
|---|---|---|
| `test-plan.json` | **v4 = 128624 B / `738998ca98414f326fb0fdde895f4bf8aa6bd921672480cbd215384f6087a72b`** | ✅ `bench-signoff`=1、limitations **17** 条（含 U10/BD-06/BD-07）、`simulationDomainReference`=2、pulseCap 2 ms、clamp"严于黄金非偏离"、用户边界句逐字；**仍缺 2 项**（BD-04 状态串应为 `closed-for-this-run`；补 **U11**）→ 已开出 v5 |
| `setup-contract.json` | **267330 B / `f17935d7b7800442…`** | ❌ **t12 五项仍未落地**（`simulationDomainReference`=0、Step 2 仍 `3.5 V/5 V`、`U10/U11`=0、`voltageDifferentialPreferred`=4）→ 已第三次下达，要求只做这 5 项 |

## Captain 独立核验：t5 payload（未应用）与哈希分歧裁决（20:2x）

**哈希分歧裁决**：ate-implementer 报 `schematic-ir-sensing.json` = 47446 B / `43ad8c84…`，与我**更早**报的 47156 B / `ad9859e9…` 冲突。Captain 现算：**47446 B / `43ad8c84ed21290efbb8a955568cab382fdaa5a766405e44bd2f337633a818f8`（mtime 14:07:07）** ⇒ **成员的值正确**；我那个是**被覆盖的上一版**。结论：**不是方法差异，是时间差**（本 run 反复出现的漂移）。成员"拒绝沿用他人哈希、改为带 path/size/mtime 的现算值"的做法**予以确认**。

**payload 核验（`implementation-payload-TM600-TM601.cpp` = 14077 B / `af521e72…`）** —— 以下各项 Captain 逐行确认合规：
强制 `FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON)` → `delay_ms(2)` → `MeasureVI(200,5,FPVIe_MV_X10)` → **立即** `Set(FI,0,…)`；clamp 在 **FV→FI 切换后、1 A 之前**下发（L106→L107→L111→L112）⇒**切换后重发成立**；算式 `hs_rdson = v_meas/i_meas*1e3`（`MVRET` / `fabs(MIRET)`）⇒ **R-VIR**；寄存器 `0x10=0x43 / 0x59=0x20 / 0x5A=0x02(HS) / 0x61=0x4B`；继电器 `K83 + K60_BUSL0_VCP + K61_ACM8_SW`（+K13/K85/K57/K126），**每 BUS 侧只闭一个 pin**，`K86/K87/K88/K89/K90/K91/K93/K141/K142` 未动作；激励 `VBAT 4.2 / PMID 15 / V1P5 5` + BST 台阶 5→20（恒领先 5 V）⇒ **E006 落地**；下电 FET 保持导通 + 反向台阶 + 统一 `RELAY_OFF` 量程（`FPVIe_1V/FPVIe_10MA`）+ **FPVIe 最后断开**；`FPVIe_RELAY_ON` 小写 e ×11、`FPVIE_RELAY_ON` 0、`rampi_capv`/`rampv_capv` 0。
**（自我更正）** 我先前用单行正则误判"缺 MVRET/MIRET 算式"—— 实际是分两行赋值；已更正，**算式合规**。

**⚠️ 一处已下发要求澄清（L70）**：上电首步 `FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON)` 在 **FV=0** 初值上用 **10 A 量程**，与 `units.md:3-5`"量程 ≥2×、取最小合规档"及**归档黄金同步用 `FPVIe_2A`** 不一致 → 要求成员**二选一并留证**（改最小合规档 / 保留 10 A 并写明理由），**不得静默保留**。这是 t6 极可能判 finding 的点，提前处置优于被审查抓出。

## 处置：t12 改派 + DV-01 误引纠正（20:3x）

**t12 连续四轮未落地**（契约已到 276231 B / `204e6976…`，但五项字段修订仍未进文件：`simulationDomainReference`=0、Step 2 仍 `VBAT=3.5 V, PMID=5 V`、`U10/U11`=0、`voltageDifferentialPreferred`=4、`disputed`=0）。因它是**用户门禁"放行 t5 写源码"的第二个硬条件**且属纯机械修订，**已改派 test-strategy-architect**（`agent_teams_reassign_task`，理由已记录）。原 owner 的其它高质量产出（`irPathCrossReference`、`relayNameMap`、`senseFormOptions`、E006 双措辞、U2b 数值判据、QTMU 反证）**全部保留并采纳**。

**DV-01 误引纠正**：契约中出现"按 Captain 裁定：**(b) 为可交付基线、(a) 为增强项**"—— **与裁定相反，已要求更正**。权威口径：
- **(a) FPVIe 浮动四线 = 实现形态**（已裁定、已入 `test-plan.json` v4、已被 t5 payload 实现）；依据＝端子排他性 + t2 `nonKelvinInstruments` 对 `QVMe` 的否决 + 归档 TM600 原生 `MVRET/MIRET×1e3`（黄金 L91）。
- **(b) = 备选**，须先解决 **t2-vs-t3 对 QVM 的对立判定**；**QTMU 变体对 TM600 已被 K141/K142 阻断**（K141 = `FPVIe0_FH_BUS_S1`+`FPVIe1_FH_BUS_S1`，TM600 独占两通道 ⇒ 闭 K141 会把 PMID 与 BST 短接）。
- 驱动层不可判定 ⇒ 槽位 **PENDING** + **U9** bring-up 判据；**首次使用面仅 `FPVIe_MV_X10`**。

**采纳的独立反证（setup-architect 实测，支持裁定）**：QTMU 候选（`S10_CH0_A/B`）对 **TM600 BLOCKED**（K141/K142 桥接）；**PC 通路按网表定案**——shunt 所在 net `FPVIe0_FL_PC_S1` 只出现在 `K90/K91(+K82)`，**不在 `K87/K88/K89`** ⇒ K87/K89 = BUS 侧力继电器兼二线短接钩、K88 = 感测浮动、只有 `K90/K91(+K82)` 是 PC（IR 括号措辞不精确已登记）。

**哈希审计**：ate-implementer 新增 `HASH-AUDIT.md`，记录**三个产物的引用值与现盘不符**（`dft-ir.json` 引用 116140/`82398d2f…` vs 现盘 130724/`d8f900a4…`；`schematic-ir-sensing.json` 引用 47156/`ad9859e9…` vs 现盘 47446/`43ad8c84…`；`test-plan.json` 引用 v3 vs 现盘 v4）。**纪律确认**：不得凭记忆或消息引用哈希；**引用前用 python 现算**，有 sidecar 的与 sidecar 交叉校验，**纯文本行数**（`test.cpp` = **8878**）作廉价稳定校验。此点对 **t6 审查、t8 门禁、t9 隔离审计**尤为关键。

**t5 payload 已对 v4 复验合规**（ate-implementer 复读计划而非假设）：TM600 forceLoop PMID→SW、TM601 SW↔PGND（PGND 高）、1.0 A、ramp 1 ms/1 µs、settle 2 ms、200 采样 ×5、clamp 每次模式切换后重发、2 ms 硬上限由 `delay_ms(2)` + 立即 `Set(FI,0,…)` 满足；U9 与最小首次使用面一致。

## Captain 裁定：1 A 脉冲算术 —— settle 由 2 ms 降为 **1 ms**（20:4x）

**争议（成员实测 SDK 语义后提出，Captain 采纳）**：`knowledge/sources/fpvie.md:174-209` —— `MeasureVI` 在 `MEAS_NORMAL` 下**在调用内完成**，且 `samplePeriod` 以 **µs** 计。故：
- `delay_ms(2)` = **2.000 ms**（settle）
- `MeasureVI(200, 5)` = 200 × 5 µs = **1.000 ms**（采集，且会**累加**到强制时长）
- ⇒ **有效 1 A 脉冲 ≈ 3 ms**，**超出用户"1 A 脉冲上限 2 ms"的硬上限**；而用户同时引用的黄金形式（`delay_us(2000)` → `MeasureVI(200,5)` → 立即 `Set(FI,0)`）**自身也是 ≈3 ms**。

**裁定：以用户明文硬上限为准 → settle 改为 `delay_ms(1)`，整段脉冲 ≈ 2 ms。**
判据：① 用户把 2 ms 表述为 **HARD CAP**，且该上限约束的是"**强制电流持续时间整体**"（目的是限制 DUT/继电器热与应力）；② **超出上限是危险方向、缩短 settle 是安全方向**，取舍以硬上限为准；③ 黄金只提供**结构**，**不覆盖明文硬约束**；④ 代价可接受（settle 2→1 ms，采样数与量程不变）。

**执行要求（已下发）**：
- payload：`Set(FI,1.0,…)` → **`delay_ms(1)`** → `MeasureVI(200,5,FPVIe_MV_X10)` → **立即** `Set(FI,0,…)`；头部注释写下结算式 `1 ms + 1 ms = 2 ms ≤ 2 ms HARD CAP`，并显式标注"**为满足硬上限而由黄金的 2 ms 降为 1 ms，属有意偏离**"。
- 计划 v5（t11）：settle 改 1 ms + 写入结算式；`pulseCap` 的**度量口径**明确为"整个强制电流持续时间（settle + acquisition）"；删去"等待 2 ms 就是上限"的旧表述；标注为有意偏离黄金。
- 契约 t12：激励字段修订与本次 settle 修正**互不冲突**。

**残留提示（t6 应核）**：0.5 V clamp 下的失效特征（≥500 mΩ 时读数无效）与 2 ms 硬上限共同构成"**短脉冲 + 钳位保护**"的安全包络；t6 需确认代码里**不存在任何长于 2 ms 的 1 A 保持**（成员已实测：0 处 `delay_ms(≥10)`）。

## 凭据漂移条例（dft-expert 发现，20:5x）—— 第 4 例且最严重

**发现**：`dft-ir.json` 正文内嵌的 `items.TM601.forceAndSense.fixtureEvidence.sha256` = `9f5643d136ea…`（构建 v6 时读到的 `schematic-ir.json` 453464 B 版本），而 live 已是 **457531 B / `9f4a7707…`**。⇒ **按 IR 内嵌哈希去校验 schematic IR 必然失败**。这是"产物在消息飞行中重生"的第 4 例，且**唯一一例产物内部嵌入了过期锚点**。

**处置（正确的做法，Captain 采纳为规则）**：**不解冻/不重建产物**，而是：
1. 对 **live** 文件复验四条夹具路径（`FH0→PGND_F_S1`[154,155]/HIGH、`FL0→SW_F_S1`[60,61]/LOW、`SH0→PGND_S_S1`、`SL0→SW_S_S1`）**全部仍成立**，两个反向配对**仍不存在** ⇒ **FS-01 与"TM601 极性 = PGND High / SW Low"结论不受影响**；
2. sidecar 增 `fixtureAnchor`（`drift=true` + 逐路径复验 + 结论不变），并把陈旧 `selfVerification`（"72/72"）更正为 **135/136**；
3. **保留那 1 个 FAIL 作为诚实信号**（"IR 内嵌锚点 == 磁盘哈希"确实不等），**不改成通过**；
4. 新增幂等脚本 `dft-ir-raw/scripts/dft_ir_reanchor_fixture.py`，作为 **t7/t9 断言夹具来源前的前置动作**（引 `liveAtReanchor.sha256`，并显式声明 drift）。

**规则（写入纪律）**：
- **凡"冻结的产物内嵌某文件哈希"，被嵌文件后续重生时 → 在 sidecar/台账登记 drift，不得解冻产物重建**（这是"避免哈希 churn"决定的直接推论）。
- **`schematic-ir.json` 在本 run 内已至少两次重生**（450689 → 453464 → 455676 → 457531 B）⇒ 引用**必须现算**；`HASH-AUDIT.md` 该行需加此注。

## 契约收敛：ΔV 仅两种形态（setup-architect，20:5x）

`setup-contract.json` = **279284 B / `018dcb0d…`**（schema PASS）。收敛结论（Captain 采纳）：
- **(a) FPVIe 感测对 SH0/SL0**：两端均 `role=S`、真 Kelvin，**受驱动层未取证门控**；
- **(b) 两点单端相减，且必须取 sense 脚**：`S3_FXVIe_PLUS_SH1→PMID_S_S1`（relays=[]，K84 默认导通）＋ `S5_ACM200_SH8→SW_S_S1`（[61]）；TM601 = `S3_FXVIe_PLUS_SH3→PGND_S_S1`（[155]）＋ 同 SW —— 均 `role=S`、`direct`、**不需 K141/K142、不碰 PC 通路**；
- **禁止**：PC 通路（`K90/K91+K82`，net `FPVIe0_FL_PC_S1` 串 `R1_CS 100 mΩ`/`R2_CS 5 mΩ`）、QTMU 桥接（`K141/K142`）、**任何 force 脚单端读（含 QVM 混合落点）**；
- **QTMU 对 TM600 = BLOCKED**（网表级证据：`K141` = `FPVIe0_FH_BUS_S1`+`FPVIe1_FH_BUS_S1` ⇒ **把 PMID 与 BST 短接于同一节点**；`K142` 同理接 FL 侧）；
- **QVM 自我撤回**（t3 撤回上一轮"QVM 可作 C 选项"）：IR paths 显示 `QVM_CH0+ → PMID_F_S1`(role=**F**)、`→ PGND_F_S1`(role=**F**)、`CH0- → SW_S_S1`(role=**S**) ⇒ **混合 F/S 落点、非 Kelvin 对**。
- **Captain 裁定维持不变**：**(a) 为实现形态**（已入计划 v4/v5、已被 payload 实现）；(b) 为**已登记且已布线的候选**（比此前"四仪表否决"更精确 —— (b) 用 sense 脚读，不是 force 脚）。

## 用户授权 Full access + 5 条执行纪律（21:0x）—— 本轮最高优先级约束

**授权**：用户明确回复"大胆干，没问题，100% 授权"，本次验收临时启用 **Full access**；运行时策略已切换为 **danger-full-access**。

**Captain 实测**：对 `D:/PROJECT6-DALI/ForCodexDebug` 写入探针 → **WRITE OK**（已清理临时文件）⇒ **写权限在本会话已真正生效**。（成员会话权限需各自探针确认；若仍被拒，**停在 payload 并如实上报，不得把权限失败写成实现失败或完成**。）

**纪律（用户原文，逐条生效）**
1. **任务状态对账**：文件更新 ≠ 任务闭合。**t11/t12 必须由对应成员正式 claim、按任务契约完成 schema/token/哈希验证并标为 completed**；**禁止只改文件不闭合任务状态**。
2. **t11/t12 completed 之前，不得写 `D:/PROJECT6-DALI/ForCodexDebug`。**
3. **t13**（t11/t12 完成后创建）：`sourceTaskId=t5`，**不覆盖已 failed 的 t5**。要求：现读最终 `test-plan`/`setup-contract` → **python 明文 SHA-256 固定输入** → 复核/重生成 payload → **只改 `ForCodexDebug`，严禁 `devel`** → 写前备份 `test.cpp` → 写后 **python 明文回读哈希** → 同步生成 meta/test_conditions → 跑 gates → 产出 **schema PASS 的 `implementation-manifest.json`** → **之后才解锁 t6/t7**。
4. 若 t13 开始时仍无外部写权限 → **停在 payload**，**不得伪装**。
5. **不授权真实机台/硬件电性验证**；**SIGN-CONVENTION 只能作为 bring-up limitation**；**编译闭环 ≠ 电性签收**。

**当前任务状态（我现算）**：`test-plan.json` = **v8 137290 B / `4294a043e674c68cdb42ca7e87d6d5a02709cac3a3bfd4c7ec002f4f64c2e304`**（schema PASS；v8 修掉 items[TM108/109] 中"BD-04 open"的最后残留 + 作者/版本字段）；`setup-contract.json` = **310089 B / `609fa38fc1c8fcf96996b4ad1e3e8f0ed1e9a3a23ff7150dd69572d32bcca3b7`**（BD-08 激励 + `simulationDomainReference` 已落地并验收）。**t11/t12 仍为 pending** → 已要求两位 owner 正式 claim 并闭合。

## Captain 裁定（21:0x）

**① BST−SW 回路：裁定 (ii) —— 不用 FPVIe1 CH1，维持接地参考 `SW12_U1REF_BST_ACM`。**
依据（implementer 实测 live `StdAfx.h:303-309`）：`K131_FPVI1_FH_SL_SHORT`/`K132_FPVI1_Sense_FLOAT`/`K134_FPVI1_PC_Force`/`K135_FPVI1_PC_Sense` 是 **ch1 的感测浮动/PC 通路继电器**，与 ch0 的 87/88/89/90/91 **同类** —— 正是 v5 负列表与 K87/K88/K89 裁定**禁止激励**的那一类；且 **ch1 无简单端点宏**（只有 composite `K_FPVIH_TO_BST_B=131,132,134,135`），test.cpp 中 FPVI1 仅用于零值初始化。
⇒ FPVIe1-CH1 记为 **`intended-but-unrealisable`**（前提：须先提供 ch1 最小端点继电器集与证据）。**SD-1 继续成立**，但绑定理由更正为"**0x59 的 HS/LS 位互斥 + PMID 电压不同（15 V vs 9 V）**"，**不再是通道预算**。契约侧 `resourceBudget`"FPVIe1 BST-SW 5 V" 与 `bst2sw` resources **必须更正**。

**② 脉冲：裁定 (b)** —— 交付 `pulse2ms-variant`（`delay_ms(1)`），`1 ms settle + 200×5 µs = 1 ms 采集 = 2 ms ≤ 2 ms HARD CAP`；注释写结算式 + **显式标注"为满足用户硬上限而有意偏离黄金的 2 ms"**；计划侧（t11）同步 settle=1 ms。

**③ 哈希"假清洁"危害（rule-reviewer 独立复核，Captain 采纳）**：**`Get-FileHash`/`.NET` 读取受保护树得到的是密文视图**，故任何基于它的比对都会**假失配**、任何 pwsh 正则扫描都会**假清洁**（payload/计划两侧均出现过）。**授权读者 = python 明文 + grep 工具**（rule-reviewer 用 grep 复核 `QVM` 4 处与 python 行号一致）。run 目录内**文本产物本身未受保护**（唯一含 NUL 的是 `__pycache__` 二进制）。⇒ **门禁通则**：哈希一律 python 明文 + 现算时刻；内容断言只许用 python/grep。

## ⚠️ Captain 自我更正（21:0x，post-change verification）：撤回"契约 BD-08 已落地并验收通过"

**被撤回的结论**：我在前一轮报告与台账中写过"`setup-contract.json`（310089 B / `609fa38f…`）：BD-08 激励 + `simulationDomainReference` **已落地并验收通过**"。

**为何撤回（本回合实测）**：在 310089 B 该版本上，我现算复核发现 **`powerSequenceDelta` Step 2 文本仍为仿真域值**（`VBAT=3.5 V, PMID=5 V …` / `VBAT=3.5 V, DVRV=5 V, VBUS=5 V`），`ateStimulus` 只是**并列新增**而未替换文本 ⇒ **同一文档存在两个激励源 = 用户明令禁止的"混合"**。故"验收通过"在当时**不成立**（我当时只核了 `simulationDomainReference` 出现次数，**未核 Step 2 文本本身** —— 这是本轮最实质的核查疏漏）。

**更正后的现况（我本回合现算，见下）**：`setup-contract.json` = **316529 B / `86d14a87ff3cea3d35806a83f9c1442853f68b8b1072a35240b406d3ee54486c`**：**Step 2 已改写为 ATE 值** —— 原文实读 `"Step 2 power on (ATE values, BD-08): VBAT=4.2 V, PMID=15 V, BST-SW=5 V, VDRV=5 V"`、TM601 `"…VBAT=4.2 V, PMID=9 V, VDRV=5 V. VBUS=5 V is a simulation-domain value and is NOT an ATE stimulus for this item"`；`simulationDomainReference` = 12 处；`stale=0`；schema PASS（成员报告，已由我现算哈希对齐）。⇒ **该缺陷现已修复**。

**仍未落地（我本回合现算）**：
| 产物 | 现算 | 缺失项 |
|---|---|---|
| `test-plan.json` | **142445 B / `19ff5e842d45168aae68b24b3eb2a0d41deaff72d9f28e4080577ab7a2a14842`** | `U11` = **0**；settle 仍非 1 ms（无 `delay_ms(1)`） |
| `setup-contract.json` | **316529 B / `86d14a87…`** | `U10`/`U11` = **0**；`voltageDifferentialPreferred` = **4**（未降级） |

**写权限（本回合第二次探针，post-authorization）**：`D:/PROJECT6-DALI/ForCodexDebug` → **WRITE OK**（已清理）。⇒ 本会话的 Full access **确实生效**；但**成员会话各自的权限仍需其自查**（成员报告仍为 denied）。

**任务账**：t11/t12 **仍未 claim**（attempt 0）→ 已按"retry 重新派发"再次下发，要求成员在任务上下文内 claim → 校验 → completed。

## 记账死锁已解开：t11/t12 由 Captain 代成员 **claim**（21:1x）

**问题**：用户纪律 1 要求"成员正式 claim → 校验 → 标 completed，**禁止只改文件不闭合任务状态**"，但 t11/t12 连续多轮停在 `pending attempt 0`：两位 owner 每轮都在继续改内容，**从不 claim**，门禁因此闭不上。

**处置**：使用平台能力 `agent_teams_claim_task(assignee=<member>)` **由 Captain 代成员认领**（内容仍由成员产出，我不代笔），结果：
| 任务 | 现状态 | attempt_id | 剩余项（我本回合现算确认） |
|---|---|---|---|
| **t11**（plan） | **claimed / attempt 1** | `78709517-7c39-44da-baf9-0a9a6299e864` | 现盘 **142445 B / `19ff5e84…`**：`U11`=0、无 `delay_ms(1)`（settle 未改 1 ms） |
| **t12**（contract） | **claimed / attempt 1** | `8df1b7d7-c088-4134-b618-36f81652f8ad` | 现盘 **316529 B / `86d14a87…`**：`U10`/`U11`=0、`voltageDifferentialPreferred`=4（未降级） |

**已下发给两位 owner 的收尾三步（缺一不算完成）**：① 改**生成器**并重跑（禁手改 JSON，保可复现性）→ ② `validate_team_artifact.py`（**仓库根运行**）要求 **exit 0** → ③ `agent_teams_update_task` 带 **attempt_id + commandsRun(exit code) + acceptanceResults(逐项证据) + 前后现算哈希**，`status=completed`。

**同时裁定的两问**：① **"standby/supply = 4.2 V" 字面限于 TM600/TM601**，但对 TM102/103/108/109 采用 4.2 V **与"ATE = DFT 声明值"同源 → 保留**（IR/.sv 的 4.0/3.0 V 继续作 `simulationDomainReference` + 分歧登记，**不回退**）；② **契约在 t12 completed 后冻结**，产物内加单调 `revision` + `generatedAt`，跨成员只引 revision + 现算哈希；**保留 2 处仪器前缀 path id**（path 可追溯性优先），在 `namingPolicy` 注明其为证据引用而非实现 API。

**闭环依赖链（未变）**：t11/t12 **completed** → 我创建 **t13**（`sourceTaskId=t5`，不覆盖 failed 的 t5）→ 现读最终两份产物并用 **python 明文 SHA-256 固定输入** → 写前备份 → 写后明文回读 → 生成 meta/test_conditions → 跑 gates → schema PASS 的 `implementation-manifest.json` → **才解锁 t6/t7**。

## 台账更正 + 冻结规则（21:2x）

**① 我记的 payload 哈希已过期，现更正（att-e-implementer 指出，我采纳）**：

| 产物 | 我此前记的（**过期**） | **现算（权威）** |
|---|---|---|
| `implementation-payload-TM600-TM601.cpp` | 14077 B / `af521e72…` | **23323 B / `82c5b5fbfa82d299f3e22885982d7acf3f88fd8ba58dca60885df46e8999ac42`**（BOM+CRLF、0 孤立 LF；可执行代码层面 0 个 `RELAY_SENSE_ON`/`CONTACTMODE`/`HIGH_MV`/`LOW_MV`/`rampi_capv`/`rampv_capv`；`SetClamp(50,50)` 恰 2 处） |
| `…pulse2ms-variant.cpp` | 21412 B / `e07ea2f5…` | **23825 B / `3e439b176896f0e275965a0bebb6cb918033e9f96cbac3afb97debd4e1c2a3e0`** |
| `backups/test.cpp.before_TM600_TM601.bak` | — | 434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`（未变，正确） |

**② `test-plan.json` 版本链（成员用保留副本 v1–v9 举证，我采纳其结论）**：
v1 98641（14:11:43）→ v2 113773 → v3 121694 → **v4 128624（14:25:51）** → v5 131707 → v6 134802 → v7 136263 → v8 137290 → v9 142445 → **live v10 = 144096 B / `f2237cc1d13e9174…`（14:50:31，"v10 stimulus-layer separation: per-entry provenance marks"）**。
⇒ **"v4 为最新"的说法作废**（v4 之后 25 分钟内又有 6 版）；**任何"被指派的基线版本"都不得作为 pin 目标**。

**③ 冻结规则（Captain 定，t11 收尾时必须满足）**：
1. **t11 的 completed 必须落在一个"冻结的 revision"上** —— 即 owner 标 completed 之后**不得再出新版**；若需再改，**另开任务**（不得在同一 task 内继续漂移）。
2. 冻结后 `test-plan.json` / `setup-contract.json` 只允许**引用**，不允许再生成；任何下游引用一律 **python 明文现算 + revision 字符串**。
3. **pin 约定（终稿）**：manifest 登记 **内容键 + locator + revision 字符串 + 引用时刻现算哈希**，历史版本列 history。**禁止 pin 任何"被某人指派的版本号"**（v4 之误的根因）。
4. 若 t11 完成后又一次出新版 → **t11 视为未完成**，退回重来（我会用 `probe_gate_check.py` 复核内容与哈希，不采信单方声明）。

**④ 一处成员读取已过期（我逐字复核更正）**：成员称"t12 的 Step 2 仍为仿真域激励（按其 310089 B 读取）"。**在现盘 316529 B / `86d14a87…` 上该缺陷已修复** —— 我逐字实读：TM600 `"Step 2 power on (ATE values, BD-08): VBAT=4.2 V, PMID=15 V, BST-SW=5 V, VDRV=5 V"`；TM601 `"…VBAT=4.2 V, PMID=9 V, VDRV=5 V. VBUS=5 V is a simulation-domain value and is NOT an ATE stimulus for this item"`。

## 台账刷新（21:3x）：payload 新哈希 + L70 修复复核 + 一处我方测量缺陷更正

**① payload 新哈希（我本回合现算，权威）**

| 产物 | 现算大小 | python 明文 sha256 | 备注 |
|---|---|---|---|
| `implementation-payload-TM600-TM601.cpp` | **23887 B** | **`5370fe4d01edbc376686c8ac29d66baf18b4c48a3e014932114e80a8df0e07b1`** | 含 `delay_ms(2)` settle（黄金形式） |
| `implementation-payload-TM600-TM601.pulse2ms-variant.cpp` | **24408 B** | **`2b48bc0e9f3097e191d4d3267dd4ebd3c974a9207f667c93c4ee9c97a5f97a31`** | **＝ t13 的交付件**（裁定 (b)：`delay_ms(1)`，`delay_ms(2)` 出现 0 次） |
| `backups/test.cpp.before_TM600_TM601.bak` | 434629 B | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` | 与实盘逐字节相同（其 3 个孤立 LF 是**原文件属性**，非缺陷） |

**② Captain 的 L70 finding 已由成员修复，我独立复核通过**
原缺陷：上电首步 `FPVI0.Set(FV, 0, FPVIe_1V, **FPVIe_10A**, …)` 在 0 V/0 A 初值上用 10 A 量程，违反 `units.md:3-5`（量程 ≥2×、取最小合规档）。成员采用我的选项 (i) 改为 **`FPVIe_10UA`**，并写明理由（0 无 2× 要求 ⇒ 最小档即合规档；且 `FPVIe_10UA` 正是 R-POFF-06 的统一关断电流档），**未**沿用黄金该步的 `FPVIe_2A`（理由：2 A 是 1 A 强制点的选择，用在零初始化上属同类错误再犯）。
**我的独立复核（代码层、排除注释）**：`FPVIe_10A` = **0**、`FPVIe_10UA` = **2**、`SetClamp(50,50)` = **2**、`MeasureVI(200, 5, …)` = **2**、`rampi_capv|rampv_capv` = **0**、`RELAY_SENSE_ON|CONTACTMODE` = **0** —— 全部符合。1 A 强制点仍为 `FPVIe_2A`、拆解仍为 `FPVIe_10MA`。

**③ 我方测量缺陷更正（撤回我上一回合的 CRLF 读数）**
我上一回合用"排除注释后重新拼接的字符串"去数行尾，重拼过程**已把行尾规范化**，因而得到 `CRLF=0 / loneLF=146` 的**假读数**，并据此质疑成员的"BOM+CRLF"声明。**该质疑撤回**。按**原始字节**重测：
- `implementation-payload-TM600-TM601.cpp`：BOM=True，**CRLF=359，孤立 LF=0** ✓
- `pulse2ms-variant.cpp`：BOM=True，**CRLF=363，孤立 LF=0** ✓
- `backups/….bak`：BOM=True，CRLF=8874，孤立 LF=3（= 原 `test.cpp` 自身属性）
**纪律补充**：**行尾/编码断言一律在原始字节上做**（`bytes.count(b'\r\n')`），**不得**在解码并重拼的字符串上做。（同族问题：`schematic-ir.json` 等哈希必须用**字节哈希**，解码后重编码会因 CRLF/LF 得出不同值 —— setup-architect 本轮独立实测同结论。）

**④ 纪律（成员第四次请求，采纳）**：**任何哈希引用前必须从该时刻的文件现算（python 字节口径）**；本 run 已发生 ≥5 次外部引用过期（我 2 次、成员 2 次、t4 计划版本 1 次），根因均为"发信期间产物被重生成"。

## 终局：实现门禁重建（22:xx）—— t14/t15 取消、t16/t17 冻结修复、U 编号终裁、BST (ii) 维持

### 1. 任务账（当前）
| 任务 | 状态 | 说明 |
|---|---|---|
| t11 | ✅ completed（by captain） | `test-plan.json` 已补 U11 + settle 1 ms |
| t12 / t13 | ✅ completed | t13 = 契约范围更正（BD-08 仅 TM600/TM601）+ U 编号首次统一 + DV-01 措辞降级 |
| **t14** | ❌ **cancelled** | 依赖缺 t13（用户指出的 DAG 结构缺陷） |
| **t15** | ❌ **cancelled** | 用户指令阻断：setup 交叉引用自相矛盾 + pin 的 setup 哈希过期时禁止进入实现 |
| **t16** | 🔄 pending（独立·可审计） | **setup 冻结修复**：统一 U10/U11 全部交叉引用 + 生成器幂等 + **连续两次生成字节哈希一致** + schema PASS + 更新 `setup-contract-pin.json`；单一写入者＝生成器 owner |
| **t17** | 🔄 pending（独立·可审计） | **计划冻结修复**：`items[].assumptions`/`globalRulesApplied` 中与裁定 (ii) 相反的 BST−SW 表述改掉 + 幂等 + 两次生成哈希一致 + schema PASS |
| 实现任务 | ⏸ **未创建** | **t16 与 t17 均 completed 后**才创建，**显式依赖两者**并固定新的 setup/test-plan 字节哈希 |

### 2. U 编号终裁（全产物统一，禁止再对调）
**U10 = QVM channel-0 concurrency**｜**U11 = FI SIGN-CONVENTION**。
我现算复核现盘 `setup-contract.json` = 326439 B / `25138683b28f5205a8331413cd067c0a24b350067d76f2934ad7e55c23adddeb`，`U10/U11` 交叉引用**逐字段 `problems: NONE`**（`polarityDecision.status/captainRuling/assumptionToVerify/escalation`、`conflicts[12]`、`tmDeltas.commandSign` 均为 U11；`openItems[11] = U10`）。**但"已消除"目前仅为单次读数** —— t16 的**两次连续生成字节一致**才是可审计证据。

### 3. BST−SW 裁定 (ii) 维持（A）
裁定：**基线＝接地参考 `SW12_U1REF_BST_ACM`**；**FPVIe1-CH1 = `intended-but-unrealisable`**。依据（implementer 独立复核）：① ch1 **无最小端点宏**（仅 composite `K_FPVIH_TO_BST_B=131,132,134,135` / `K_FPVIL_TO_SW_B=132,133,134,135`），ch0 有 `_A` 宏；② 该四只继电器是 **ch1 的感测浮动/PC 通路类**（`StdAfx.h:303-309`），属 v5 负列表同类；③ **live 无任何 TM 用 FPVIe1 驱动 BST**。
⇒ **payload 不变**（`bf7e58da…`，`SW12_U1REF_BST_ACM` ×13、0 个 K131–K135）；**计划文本由 t17 修正**。这是本 run 第 N 次"发现相反证据必须上报、不得自行择一"的正面案例。

### 4. 我方撤回（冻结声明作废）
- 撤回"`setup-contract.json` 已冻结 325885 B / `b98cd824…`" —— 期间被**两个写入者交替重生成**（`U10↔U11` 为**等长替换**，故出现"**大小相同、哈希不同**"：526cca29 → c36a9799 → 25138683）。
- 撤回"计划已冻结 v12 = 148150 B / `b3ea1714…`" —— 成员在无任务号下修为 v13（并修掉我 v12 手改遗漏的 `items[].sequence` "Wait 2 ms"，该遗漏**若照实现会得 3 ms 违反 2 ms 硬上限**，是我的错，已认）。

### 5. 写权限与边界（纪律 4/5）
- **成员会话连续 4 次写探针均被拒**（原始错误：`PermissionError [Errno 13]`；其权限在会话启动时固定、无法自内部提权，本会话审批已禁用）→ 已按纪律 4 处理：**停在 payload 并如实上报**，不伪装。
- **Captain 本会话写探针成功**（`danger-full-access`）⇒ 落盘将由具备权限的一方执行，报告须写明"**内容作者=ate-implementer、执行者=写入方**"，t6/t7 独立复核。
- **目标树至今未被触碰**：`source/test.cpp` = 434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`；`devel` 未动。
- **不授权机台/电性验证**；U10/U11 仅作 bring-up limitation；**编译闭环 ≠ 电性签核**。

**写前须完成的硬条件**：t16 + t17 completed（两次生成哈希一致、schema PASS、pin 更新）→ 我创建实现任务（显式依赖两者 + 固定双哈希）→ 下发"冻结哈希 + 裁定摘要" → 实现者先做 mismatch 复核 → 才允许写。

## 单一写入者裁定 + 最小 Setup 修复任务（t18）（22:2x）

**用户调度令**：立即广播"**停止无任务写入**"；`setup-architect` 只作 **t16** 单一 writer；`test-strategy-architect` 只作 **t17** 单一 writer；**t16/t17 未 completed 前不得继续裁定扩展、不得创建实现任务**；完成后由 **Captain 独立复验**（两次哈希、schema、U10/U11、BST−SW）后再建实现任务。
**已执行**：向三人分别下发（含停止编辑 setup/test-plan 与生成器的硬指令 + 各自 claim 要求）；`ate-implementer` 保持 idle。

**新增 `t18` = 最小 Setup 修复（kind=repair，`sourceTaskId=t12`，`sourceFindingIds=[BD08-SCOPE-01]`，依赖 t16）**
撤回 t12 对 **TM102/TM103/TM108/TM109** 的 BD-08 扩展：删除其 `ateStimulus`（含 source）与 `stimuli[0]`/`stimuliSourceNote` 的 supersede 改写 → **恢复各自 IR 派生原文与 DFT/OVERVIEW ATE 值**；并把 **DFT.csv 第 12/25/30 行声明 `vset[vbat,4.2,100e-6,0]` vs OVERVIEW/IR 4.0 V（TM108/109 3.0 V）** 的分歧**登记为保留两侧的冲突**（不得删除/平均）；`.sv` 值继续留 `simulationDomainReference`。**不动** TM600/TM601、U10/U11、路由、寄存器、safety invariants。与 t16 同源串行（同一生成器）。

**门禁序列（用户明令，未满足不得进入实现）**
`t16`（U 交叉引用统一 + 生成器幂等 + **两次生成字节一致** + schema PASS + pin 刷新）
→ `t18`（最小 Setup 修复 + 冲突登记 + schema PASS + 前后字节哈希）
→ `t17`（计划 BST−SW 文本对齐裁定 (ii) + 幂等 + 两次生成一致 + schema PASS）
→ **Captain 独立复验**（两次哈希、schema、U10/U11、BST−SW）
→ 才创建**实现任务**（显式依赖 t16/t17/t18 + t11，固定冻结字节哈希）→ 下发"冻结哈希 + 裁定摘要" → 实现者先做 mismatch 复核 → 方允许写。

## 本轮其它实测与更正（22:2x）

- **实现者按契约三条链修正 TM601 力符号**：`+1.0` → **`-1.0 A`**（HIGH=PGND ⇒ 命令符号取反；`MIRET` 用 `fabs()` 故记录幅值不变），并把三步推导链写入代码注释供 t6 复核；payload 现算 **27228 B / `889c8e77668c86350227035afcb436792358feb424ba1d9e62c2b5da356b207e`**（取代 `bf7e58da…`）。**我采纳**（该符号约定本身是 U11 的 bring-up 校验项；契约明文标注"正 FI = 电流自 HIGH 端流出"为**从黄金推断、无头文件/手册明文**）。
- **pin 与产物不同刻**：成员实测 `setup-contract-pin.json` 记 `321779 B / 93e417f6…`，而现盘已 ≥`327117 B` ⇒ 已要求 owner 在 t16/t18 完成时**最后刷新 pin** 并写明 `measuredAt` 与两次一致结论。
- **写权限再确认**：成员会话连续 4 次探针被拒（`PermissionError [Errno 13]`），Captain 会话可写 ⇒ 落盘由具备权限方执行并标注"内容作者/执行者"。
- **目标树仍未触碰**：`test.cpp` = 434629 B / `5c9cb3f9…3317`。

## DAG 冻结缺陷更正：**最终冻结门槛移到 t18**（22:3x，用户裁定）

**缺陷**：`t18` 依赖 `t16` 且会**再次修改同一** `setup-contract-build.py` / `setup-contract.json` ⇒ **t16 的"两次同哈希 + pin"在 t18 之后必然失效**（冻结声明会被随后重生成作废）。

**裁定（生效）**
1. **t16 = 中间步骤**：仍须完成 U 交叉引用统一（U10 = QVM channel-0 concurrency、U11 = FI SIGN-CONVENTION）+ 生成器幂等 + schema PASS；其两次一致性仅作**中间自检**，**不宣告最终冻结**。
2. **`t18` = 最终冻结门槛**：修复后**连续运行生成器两次** → **两次 Python 明文字节 SHA-256 完全相同** → **schema PASS (exit 0)** → **刷新最终 `setup-contract-pin.json`**（最终 size/sha256/mtime/`measuredAt`/"两次一致=True"/五项检查/哈希方法）→ **报告两次哈希**。
3. **t18 完成前：继续禁止 Full access 与任何外部（目标树）写入**。
4. **实现任务的依赖改为 `t17 + t18`**（不再只依赖 t16），并固定 **t18 之后的 setup 哈希** + **t17 之后的 test-plan 哈希**。

**已下发**：该追加裁定已发给 `setup-architect`（唯一写入者），并要求按 **t16 → t18** 顺序执行、t16 完成时**不得**宣告最终冻结。

## U 编号 canonical 终裁 + 过期脚本作废（23:xx）

**canonical（与用户指令逐字一致，全产物唯一映射）**：**U10 = QVM channel-0 concurrency**｜**U11 = FI SIGN-CONVENTION**。

**现况对照（我以成员回报 + 现算哈希核对）**
| 产物 | 编号现状 | 处置 |
|---|---|---|
| `setup-contract.json`（329806 B / `a5da890a…`，revision 15） | **已是 canonical ✓**（`U10: QVM ch0 concurrent use…`、`U11 bring-up verification…`） | 无需改动 |
| `test-plan.json`（v14 = 151276 B / `316ee352…`） | **相反**（U10 = SIGN-CONVENTION、U11 = QVM） | **t17 追加该项**：改回 canonical（含 limitations/items/引用处），并更正 `align_plan_u_labels.py` 头部注释 |

**过期脚本作废（已加显式警示，禁止执行）**：`fix_u_numbering.py`、`align_plan_u_labels2.py` —— 二者头部依据引用的是**已作废的旧状态**（v12 / 契约旧版），照其执行会把产物**推离 canonical**。已在两脚本首部加 `⛔ OBSOLETE / DO NOT RUN` 警示块（含 canonical 声明）。

**记账（按 t10 先例）**：计划侧 **v13/v14 由 Captain 指示、由计划 owner 在无任务号下完成**，作者链在此登记：v13 = 150245 B / `b8bae3c8c3adb8803d721372dad6d4b8c852074b8d1c3274e33fe1fcb6185171`（修掉我 v12 遗漏的 `items[].sequence` "Wait 2 ms"）；v14 = 151276 B / `316ee352f9621bea423b638cf952042295d6548af59bab4eda62cbcdb2f7c851`（BD-04 精确 `closed-for-this-run` + `statusNote`、`bench-signoff` 5 处、边界句原句、U 编号与 DV-01 维持 (a)）。**t11 的 claim 被拒原文**：`Error: task t11 is assigned to "captain", not you`（t11 归 captain 且已 completed，终态不可补记）。

**并发写入事件（实测）**：`test-plan.json` 在 15:13:07 被**非其 owner 的进程**重建过一次；`setup-contract.json` 在观测期内 325885 → 329806 B。⇒ **单一写入者已广播并生效**：计划 owner = test-strategy-architect（t17）、契约 owner = setup-architect（t16→t18），Captain 不再编辑这两份产物与其生成器。

## t18 权威范围追加（用户指令，23:xx）—— "最小 freeze repair" 的完整定义

**用户实测**：t13 报的冻结点 `325885 B / b98cd824…` 与随后现算 `326363 B / 30b96931…` 不一致；`probe_t13_state.py` 三项语义仍 PASS，但**其"生成器状态"计数与现盘不同** ⇒ **可复现性/冻结被并发写破坏**（生成器与 artifact 被不同写者交替编辑）。

**t18 必做（最终冻结门槛，除原范围外新增 4 项）**
1. **`setup-contract-build.py` 与现盘产物对齐**（消除"生成器计数 ≠ 现盘"的偏差）。
2. **连续两次运行生成器 → 两次 Python 明文字节 SHA-256 完全相同**；**schema PASS（exit 0）**。
3. **确认无并发写者**：两次运行前后记录 **mtime + size + 字节哈希**，并**显式声明期间无其他写入**；发现第三方变动即停手回报。**唯一写入者 = setup-architect**。
4. **更新两份记录**：① `setup-contract-pin.json`（最终 size/sha256/mtime/`measuredAt`/"两次一致=True"/五项检查/哈希方法/revision）；② **实现输入确认表**（内容键 + locator + revision 字符串 + **引用时刻现算哈希**），供后续实现任务直接 pin。

**硬约束（用户明令）**
- **禁止启用外部写权限、禁止任何写探针或写副本**（目标树保持**零写入**）。
- **实现重试必须 pin 新哈希**：**不得采用 `b98cd824…` 或 `30b96931…`**（未经本次重建确认的值）；只认 **t18 两次一致的那个字节哈希**。
- `t16` 为中间步骤，**完成时不得宣告最终冻结**。

**canonical 编号（全产物，不得对调）**：**U10 = QVM channel-0 concurrency**、**U11 = FI SIGN-CONVENTION**（契约现盘已符合；计划侧由 **t17** 改回）。

**已下发**：该追加已发给 setup-architect（唯一写入者），要求 claim t16 并按序执行到 t18 完成，回报两次哈希（应相同）+ schema exit code + pin 与输入确认更新证据。

## 审计基准纪律 + 记账（23:xx）

**Captain 自我更正**：我对计划侧"t11 未落地"的多次判定，**基准取自历史副本**（`test-plan.v3.json` = 121694 B / `2e93a46c…`，mtime 14:20:55）而**非现盘**。现盘 `test-plan.json` = **v14 = 151276 B / `316ee352f9621bea423b638cf952042295d6548af59bab4eda62cbcdb2f7c851`（mtime 15:18:50）**，t11 六项**均已成立**（我用自己脚本现刻复核：`bench-signoff`=5、`closed-for-this-run`=4、BD-06 带 ", no numeric criteria"、BD-07 在 limitations、limitations=18）。**该判定撤回。**
**纪律（采纳）**：① 结论前必须用**同一次读取**同时打印 **size + sha256 + mtime**，并在报告中带**时刻**；② **禁止把"先前记下的期望哈希"当比对锚点**；③ **禁止引用自己上一次打印的数字**（侧车 8 次哈希失配中 ≥2 次属此类）；④ 断言"字段已落盘"必须回读文件，不得采信写入器 stdout（含自己的）。
**假检查更正**：`probe_gate_check.py` 对 `delay_ms(1)/delay_ms(2)` 计数 **0/0 是预期**（t4 验收标准要求计划**不含 API 名与 C++ 代码**，settle 以语义表述）；正确检查项是其 `'1 ms' settle mentions`。

**记账（按 t10 先例）**：计划侧 **v13/v14 由 Captain 指示、由计划 owner 在无任务号下完成**，作者链登记：
- v13 = 150245 B / `b8bae3c8c3adb8803d721372dad6d4b8c852074b8d1c3274e33fe1fcb6185171`（修掉我 v12 遗漏的 `items[].sequence` "Wait 2 ms"）
- v14 = 151276 B / `316ee352f9621bea423b638cf952042295d6548af59bab4eda62cbcdb2f7c851`（BD-04 精确 `closed-for-this-run` + `statusNote`、`bench-signoff` 5 处、边界句原句、DV-01 维持 (a)）
**claim 被拒原文**：`Error: task t11 is assigned to "captain", not you`（t11 归 captain 且 completed，终态不可补记）。

## 实现者侧产物登记（23:xx，引用时刻现算）

| 产物 | 现算 | 说明 |
|---|---|---|
| `implementation-payload-TM600-TM601.cpp` | **27228 B / `889c8e77668c86350227035afcb436792358feb424ba1d9e62c2b5da356b207e`** | **单一路径**（同名副本已删除）；BOM+CRLF、0 孤立 LF；含按契约三步链把 **TM601 命令符号改为派生 `-1.0 A`**（TM600 保持 `+1.0 A`）＋三步推导链与 U11 bring-up 判据注释 |
| `implementation-payload-TM600-TM601.pulse2ms-variant.cpp` | **已删除** | 裁定 (b) 早已并入主件；副本只会造成双路径歧义 |
| `backups/test.cpp.before_TM600_TM601.bak` | 434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` | 与实盘逐字节相同 |
| `t5-input-confirmation.md` | 9652 B / `0ace2aee4c4dce43feaedaf39b1b34a54f5929f53f79038da99b3880d29216d9` | 新增 **§C2 已应用裁定表**（(b)、量程修复、拆解顺序修复、裁定 (A)、符号约定 + U11 状态）；**5 个 HASH 单元格保持留白**，待冻结哈希下发后填写并先做 mismatch 复核 |
| `APPLY-TM600-TM601.md` | 3730 B / `3f7ea26172920ff8e20627f4167a990fe0c939d9f080f1908485115f947f975e` | 落盘程序（备份→校验→python 字节模式追加→回读复验） |
| `HASH-AUDIT.md` | 8084 B | 含 sidecar 多写入器根因与三条纪律增补 |

**裁定 (A) 已双向确认**：实现者复核 payload —— BST 轨由接地参考 `SW12_U1REF_BST_ACM` 驱动（13 处调用），`FPVI1` 仅出现在拆解 `RELAY_OFF`，**`K131/K132/K134/K135` 在可执行代码中零出现** ⇒ **payload 即 (ii)/(A) 的实现形态**；manifest 将记录"计划文本已于 t17 修正以与实现一致"，并同时引用修正前后的两段文字。

## t16 / revision 18 —— Captain 独立复验通过（23:xx）

**现盘实测（我的工具，逐字段）**
| 项 | 实测 |
|---|---|
| `setup-contract.json` | **330667 B / `5dd21593ce3a11772f7dfe1a0a0a9e5ca487bfb090e8fde4a44c45c4115c5412`（revision 18）** |
| schema | `validate_team_artifact.py setup-contract` → **PASS exit 0** |
| openItems | **U10 = "QVM ch0 concurrency (verbatim captain text)"**、**U11 = "SIGN-CONVENTION (verbatim captain text)"** ⇒ **canonical ✓** |
| `polarityDecision.signConventionFinding` | **status / captainRuling / escalation 三处现均写 U11** ⇒ 用户所引 `30b96931` 版的内部矛盾**已消除** |
| 交叉引用一致性 | `probe_u_refs.py`（已修正为关键词匹配）→ **`problems: NONE`** |
| BST−SW (ii) | `SW12_U1REF_BST_ACM` ×9、`supersededRelaySet`、`bstRuling_ii`、`intended but currently unrealisable` ×2 |
| DV-01 | `voltageDifferentialPreferred` **0 次** |
| `setup-contract-pin.json` | 1548 B；`revision/sizeBytes/sha256` **与产物一致 ✓** |
| 幂等 | 成员实测**连续两次生成字节一致**；**关键构造：`generatedAt` 由 revision 派生而非墙钟**（否则幂等不可能）—— Captain 采纳为**最佳实践** |

**两处我方更正**
1. 我此前用 `probe_u_refs.py` 报的"2 处编号不符"是**探针期望串过期**（topic 现为 "QVM ch0 concurrency" 而非 "QVM channel 0 concurrency"）⇒ **假阳性，已撤回**，探针已改为关键词匹配并重跑 `problems: NONE`。
2. 成员指出我引的 `310,089 B / 609fa38f…` 是其 14:49 版快照 ⇒ **撤回该引用**。

**新增待办（已下发 t18）**：pin 的 `measuredAt`（15:26:48）**早于**派生 `generatedAt`（"15:34:00 (revision 18)"）⇒ 要求 t18 的最终 pin **把真实墙钟测量时刻与派生时间戳分成两个字段**并加说明，避免 t6/t9 误读。

**记账**：`t12`/`t16` 均已 completed（重复 claim 被平台拒绝是预期）；**不需要为形式另开闭合任务**。`t15` 早已取消（用户指令），最终冻结门槛为 **t18**；计划侧 canonical 修正由 **t17** 承接。

## ⛔ 阻断任务外写入 + 最终输入定义（用户紧急令，23:xx）

**漂移证据（用户实测）**：`t16` completed 输出 revision 16 / `9f6d6e07…`，但 **15:28:13 现盘已变为 revision 19 / 330656 B / `e2be6d63…`**，而 **`t18` 仍 pending**；计划侧亦在任务外推进至 **v15 = 156206 B / `b3af9c75…`**（`t17` 仍 pending）⇒ **存在任务外再生成**。

**已下发（两位唯一写入者）**
- **立即停止一切无任务号写入**（含措辞微调、交叉引用并入等非任务列明内容）；**只在各自任务内变更**。
- **setup-architect → claim `t18` 并在其内一次收口**（裁定 **(B)**：照原文**执行撤回** TM102/103/108/109 的 BD-08 扩展 + 冲突登记；我先前"保留 4.2 V"的裁定**已撤回**，因用户阻塞性指令覆盖之）。
- **test-strategy-architect → claim `t17`**：① U 编号改回 **canonical（U10 = QVM channel-0 concurrency、U11 = FI SIGN-CONVENTION）**；② BST−SW 对齐裁定 (ii)/(A)；③ 生成器幂等 + 两次同哈希 + schema PASS。

**最终输入定义（用户明令）**
1. **不得把 `t16` 的哈希当最终输入**；亦不得以任何历史哈希（`9f6d6e07…` / `5dd21593…` / `e2be6d63…` / `316ee352…` / `b3af9c75…`）作最终 pin。
2. **`t18` 与 `t17` 双 completed 后**，由 **Captain 独立现算**最终哈希 → **与 `setup-contract-pin.json` 对比** → 并做**短时稳定复读**（间隔复读确认哈希与 mtime 不再变化）→ **通过后才作为实现任务的输入 pin**。
3. **不开放 Full access**；**禁止写探针/写副本**；目标树保持**零写入**。

**其它本轮记录**
- 成员对**我的审计基准**的更正成立：我误引的 `121694 B / 2e93a46c…` 正是历史副本 `test-plan.v3.json`；现盘 v15 的五项放行条件全绿。该判定**已撤回**。
- 成员自我更正一条**真实错误**（"87/88/89 必须保持 OPEN" → 它们是 **Relay-NC 默认导通**）；正确表述改为**可检查口径**"87/88/89/90/91 不得进入 required-on(SetOn) 集合"。**采纳**，并新增"IR 动作列表 vs connect-map 默认导通触点 二者皆正确、不得互指矛盾"的规则（预计可挡掉一个 t6 假 finding）。
- `dft-raw/dft-ir-hashes.json` = 19733 B / `9ed89c11…`（六区块在位）；`dft-ir.json` 未改 = 130724 B / `d8f900a4…`；`20483 B / 4ebc1089…` 已 **VOID**。

## 15:36 峰时费用暂停（用户指令；恢复入口）

用户要求北京时间 18:00 后继续，避免 DeepSeek 峰时费用。已向 Captain 发送暂停指令并停止可见的运行回合；因排队旧消息可自动拉起成员，已停止本地 DSH Web 服务（`127.0.0.1:7799` 无监听）。暂停核对 `team.json`：t16 completed；t17/t18 为 claimed，**不代表完成**。目标 debug `source/test.cpp` 仍为 434629 B / Python 明文 sha256 `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`；未开启 Full access。15:34:31 Setup/Test Plan 现盘分别为 331223 B / `0fed1c181c6d584a9be6e3efbccb354c4e2f05d7437bc737f052b6cb4653a58a`、157175 B / `33a0a4e46a209f036bfd5c0fc0316ae51cc67ce64277d2be78173c0615498e6d`，均属**未冻结快照，不得作实现输入**。18:00 恢复时先读 `team/EXECUTION_PLAN.md`，重查服务/任务状态、现盘哈希与 pin、Schema、t17/t18 是否中断，再按最终冻结门槛继续；自动恢复提醒 `18-00-dsh` 完成后取消，避免次日重复。

## 18:0x 恢复：任务归属纠正 + 冻结证据（不沿用任何暂停前未冻结哈希作输入）

**恢复动作**（依据 `team/EXECUTION_PLAN.md` §7 第 1 项 + 用户恢复指令）
1. **任务归属核查（`agent_teams_status`）**：`t16` **completed** ✓；`t17` **claimed attempt 2 → test-strategy-architect** ✓（策略 owner 正确，保留）；`t18` **claimed attempt 3 → schematic-expert** ✗ **违反单一写入者家规**（t18 会改 `setup-contract.json` 与其生成器，唯一写入者必须是 Setup owner）。
2. **sanctioned 纠正（绝不手改 team.json）**：`agent_teams_reassign_task(t18 → setup-architect)` ⇒ **t18 = claimed, attempt 4, attempt_id `90223d2d-c897-4474-83ab-c66a88b55512`** ✓；被停下的原理图专家回合已终止。
3. 已下发执行令：**setup-architect 执行 t18 撤回**（Captain 先前"四项 4.2 V 保留"的裁定**已被用户阻塞性指令覆盖并撤回** ⇒ 按原文执行撤回，**不取消**）；**test-strategy-architect 收口 t17**。

**冻结证据（现盘现算；首次读取 18:06:02）**
| 产物 | 现算 | 备注 |
|---|---|---|
| `setup-contract.json` | **331223 B / `0fed1c181c6d584a9be6e3efbccb354c4e2f05d7437bc737f052b6cb4653a58a`** | revision **20**，mtime **15:31:10**，schema **PASS exit 0** |
| `test-plan.json` | **157175 B / `33a0a4e46a209f036bfd5c0fc0316ae51cc67ce64277d2be78173c0615498e6d`** | mtime **15:31:18**，schema **PASS exit 0** |
| `setup-contract-pin.json` | 1865 B / `60b8c3d4321d5da1a5ebd51e8961f732fdce9198c3b0fb6c7c1517d935447398` | `sha256` 与产物一致 ✓；**`frozen: True` 属提前宣告**（revision 20 将被 t18 覆盖） |

**短时稳定复读（间隔 6 秒）**：两份产物均 **STABLE** ⇒ 暂停期间无进一步写入。
**U 编号一致性**：`problems: NONE`（`U10 = QVM ch0 concurrency`、`U11 = SIGN-CONVENTION` = canonical）。成员另补 **U7**（committed intermediates 的 provenance 字符串，源自 IR `unresolvedTopology U7`）并给出 U1–U11 全编号断言 —— **采纳**（编号表要求 U1–U11 完整）。
**⚠ t18 尚未执行（门禁仍开）**：`BD08-SCOPE-01` **不存在**；TM102/TM103/108/109 仍 `ateStimulus=True`、`stimulusScopeNote=False` ⇒ 四项 BD-08 扩展**仍在**。

**门禁不变**：`t17` + `t18` 双 completed（两次生成字节一致 + schema PASS + 无并发写者确认 + 最终 pin + 输入确认）→ **Captain 独立复算两份现盘 Python 明文字节哈希、对比 pin、schema、U10/U11、BST−SW，并短时稳定复读** → 通过后才创建**实现任务（显式依赖 t17+t18）**。
**模式**：Workspace Write（**未开 Full access**）；`source/test.cpp` = 434629 B / `5c9cb3f9…3317`；`devel` 零写入。
**记账**：`t12`/`t16` 已 completed；重复 claim/update 被平台以"终态不可变"拒绝属**预期** ⇒ **不为形式另开任务**，本轮闭合记录由 **t18 的 output** 承载。

## t18 裁定时间线 + 两侧 locator（18:1x，唯一有效口径）

| # | 来源 | 内容 | 效力 |
|---|---|---|---|
| T1 | Captain（较早） | "四项 4.2 V 保留、归因各自 DFT 行" | ❌ **SUPERSEDED** |
| T2 | **用户（较晚，阻塞性指令）** | "请勿静默保留该扩展；**撤回** TM102/103/108/109 的 `ateStimulus.vbat=4.2` 与 supersede 表述，**恢复其各自 DFT/OVERVIEW ATE 值**；保留 .sv 值作 reference/冲突；不改 TM600/TM601、U10、路由、寄存器、safety invariants" | ✅ **有效** |
| T3 | **Captain（t18 / attempt 4，本条）** | 执行 T2；两侧证据并列登记；封口条件见下 | ✅ **当前有效** |

**两侧证据（Captain 独立实测；禁止改写成单侧、禁止平均）**
- **A 侧（DFT.csv）**：`project/DALI/input/DFT.csv` **L12 = TM103**、**L25 = TM108**、**L30 = TM109** 各自声明 `vset[vbat,4.2,100e-6,0]`（TM600/TM601 见 L90/L98）。
- **B 侧（IR/OVERVIEW Code1 + reg_config）**：`dft-ir.json` `items[TM102].stimuli[0].vbat = 4.0 V`、`items[TM103] = 4.0 V`、`items[TM108] = 3.0 V`、`items[TM109] = 3.0 V`（各 note 均写 "DFT.csv says 4.2 V — see conflicts"）。

**t18 验收要旨（修订版）**：① 删除四项 `ateStimulus`（含 source）与 `stimuli[0]`/`stimuliSourceNote` 的 supersede 改写 ⇒ 恢复原始 IR 派生文本（4.0/3.0 V）；② **登记冲突并保留两侧 locator**；③ `.sv` 值留 `simulationDomainReference`；④ **两次生成字节一致** + **schema exit 0**；⑤ **确认无并发写者**（两次运行前后 mtime+size+哈希）；⑥ **最终 pin**（`frozen` 由本次收尾写入；真实 `measuredAt` 与派生 `generatedAt` 分列）+ **输入确认**；⑦ 回报并标 completed。

**归属处理**：t18 因违反单一写入者家规从 schematic-expert 改派 **setup-architect（attempt 4 / `90223d2d-c897-4474-83ab-c66a88b55512`）** ✓。`t12`/`t13`/`t16` 均已 completed，**不为形式另开闭合任务**（本轮闭合记录由 t18 output 承载）。

**冻结证据（18:06 现算 + 6 秒稳定复读）**：`setup-contract.json` = 331223 B / `0fed1c18…`（rev 20，schema PASS，U canonical `problems: NONE`，pin.sha256 与产物一致但 `frozen:true` 属**提前宣告**）；`test-plan.json` = **160645 B / `29c0206ebaeb341dde9739709a91141dd75d0fbd47f2be2cfe6bc2a9e147b508`（v17，schema PASS）**；**两者均 STABLE**。**t18 尚未执行**：`BD08-SCOPE-01` 不存在、四项仍带 `ateStimulus` ⇒ 门禁仍开。

## t18 撤回已落地（Captain 逐项核验，18:1x）

**现盘**：`setup-contract.json` = **revision 21 / 328723 B / `7f505fdbbb60aa798fb79d16d431f095ff26693406633de9132b0e1cde7ee59f`**（mtime 18:09:30）；`setup-contract-pin.json` = 2101 B（`sha256` 与产物**一致** ✓，`revision=21`，**墙钟 `measuredAt=18:09:41`** 与**派生 `generatedAt="2026-09-16 16:02:00 (revision 21)"` 已分列**）；**6 秒稳定复读 STABLE**。任务态：**t18 = in_progress, attempt 4 → setup-architect** ✓（归属已纠正）。

**核验结果（我的脚本 `probe_t18_verify.py`）**
| 项 | 实测 |
|---|---|
| 四项 `ateStimulus` | **已删除**（TM102/103/108/109 均 `ateStimulus=False`；字段仅剩 `stimuli`） |
| 四项 `stimuli[0]` | **已恢复原始 IR 派生原文**：`OVERVIEW Code1 / reg_config/tm102.sv / DFT.csv Hardware_initial (4.2 V in DFT.csv — see conflicts)`；TM103/TM108/TM109 同构 |
| `simulationDomainReference` | 保留：TM102/103 = **4.0 V**、TM108/109 = **3.0 V**，状态 "retained as the simulation-domain reference … NOT an ATE stimulus in its own right" |
| **冲突登记** | `conflicts[1]` = "**TM102/TM103/TM108/TM109 VBAT divergence (registered, both sides retained, t18)**: DFT.csv lines **12 (TM103), 25 (TM108), 30 (TM109)** each declare `vset[vbat,4.2,100e-6,0]`, while the IR/OVERVIEW-derived stimulus and reg_config .sv carry **4.0 V for TM102/TM103 and 3.0 V for TM108/TM109**. Neither side is averaged or deleted…" ✓ |

**两处残留（不阻塞，但需记录/可一句话修正）**
1. 冲突文本续句写"**the ATE stimulus follows the item's OWN DFT.csv row (4.2 V)**" —— 若用户本意是"四项 ATE 值取 **OVERVIEW（4.0/3.0 V）**"，这是一行改动；若本意是"取各自 DFT.csv（4.2 V）、把 OVERVIEW 值留作参考"，则现盘即为正确。**已提请用户一句话确认**。
2. 我要求的溯源句 "captain's earlier keep-ruling was superseded by the user's blocking correction" **未出现**（`superseded by the user` = 0 命中）；属**文字项**，可在 t18 收尾时补一句。

**t18 仍欠（收口硬指标）**：① 连续两次生成**字节一致**；② schema **exit 0**；③ 无并发写者确认（两次运行前后 mtime+size+哈希）；④ **最终 pin**（`frozen` 由本次收尾写入）；⑤ **实现输入确认**；⑥ 回报并标 **completed**。
**t17 仍欠**：连续两次生成**字节一致** + BST−SW (ii) 状态确认 + 标 completed（现盘 plan = **161516 B / `0578bd5e…`（v18）**，schema PASS）。

## t18 completed（revision 21）+ Captain 独立冻结复算 + excerpt 关键更正（18:1x）

**t18 = completed**（setup-architect, attempt 4）：BEFORE `0fed1c18…`（331,223 B, rev 20）→ **AFTER `7f505fdbbb60aa798fb79d16d431f095ff26693406633de9132b0e1cde7ee59f`（328,723 B, rev 21）**；生成器**两次运行字节一致**；`validate_team_artifact.py setup-contract` **exit 0**；pin 同刻刷新（`measuredAt 18:10:38`，墙钟与派生 `generatedAt` 分列）。逐项 diff：四项 `ateStimulus` 删除、`stimuli[0]` 恢复 IR 原文、冲突登记（conflicts 21→22，两侧 locator 并列不删不平均）、`.sv` 值留 `simulationDomainReference`、未触碰 TM600/TM601/U10/U11/路由/寄存器/safety/上下电/别名表。

**Captain 独立复算（18:11，含 6 秒稳定复读）**
| 产物 | 现算 | 结论 |
|---|---|---|
| `setup-contract.json` | **328723 B / `7f505fdb…`**（rev 21, mtime 18:10:37） | schema **PASS exit 0**；U 一致性 `problems: NONE`；pin.sha256 **与产物一致** ✓；**STABLE** |
| `test-plan.json` | **161516 B / `0578bd5e5b17f7bee0feafb75641c22f4105eb0bcf410126def47bdd5920ea62`（v18）** | schema **PASS exit 0**；**STABLE** |
| `setup-contract-pin.json` | 2132 B / `f37b814c…` | revision 21 + 两次一致结论 + checks |

**⚠ 关键更正（影响 t5 落盘）**：t5 的**绑定输入** `test-plan-tm600-tm601-measurement-excerpt.md` 曾仍写 **`delay_ms(2)`**（计划侧自 v13 起即为 1 ms）⇒ 照旧值实现会得 **≈3 ms 脉冲、违反用户 2 ms 硬上限**。已由计划 owner 修正为 `delay_ms(1)` 并新增 **Amendment 1**（结算式 + SDK 依据 `fpvie.md:174-209` + "有意偏离黄金、不得判为无据偏离"）。现算：**8423 B / `9554d4d6f4fe878d05ba65fe5a79628192445f46ff74793e22d146f0e9ef89c8`**（旧 5911 B / `342651a7…` 作废）⇒ **必须纳入放行快照包**。

**哈希结算**：`schematic-ir-sensing.json` = **47446 B / `43ad8c84…`**（两次独立一致）⇒ 我早期的 `47156/ad9859e9…` **作废**（已撤回）。

**两处残留（非阻塞，待处置）**：① 契约冲突条目续句写 "the ATE stimulus follows the item's OWN DFT.csv row (4.2 V)"，与已恢复的 `stimuli[0]`（IR/OVERVIEW 4.0/3.0 V）**措辞上不一致**（前者是"ATE 权威"陈述、后者是"原文恢复"）；② 我要求的溯源句 "superseded by the user's blocking correction" **未出现**。二者均为文字项，可在后续小任务或 t9 报告中收口。

**t17 仍欠**：**两次生成字节一致** + BST−SW (ii) 状态回报 + 标 completed（现盘 plan v18、excerpt 已新哈希）。
**流程留档（t3 经验，可复用）**：**repair/quality 类任务的 `acceptanceResults` 必须与任务自身声明的 acceptance 条目一一对应、按原序提交**；自拟条目会被平台拒绝。

## pin 侧车缺陷（用户发现）+ 新建 t19 + 冻结态汇总（18:2x）

**缺陷（用户独立复核 + Captain 复核确认）**：`setup-contract-pin.json`（4313 B / `d0f46e28…`）内**旧 `checks` 区块与新 `fiveChecks`/`t18Checks` 并存**，其中旧块 **`u10 = false`**（`u11 = true`）；而产物 `openItems` 的 **U10 = "QVM ch0 concurrency (verbatim captain text)"** ⇒ **谓词假阴性**，非产物问题。`frozenAt`/`measuredAt` 现为 18:11:44（15:31:25 旧值已覆盖）。
⇒ **该 pin 在修正前不得作为"全绿冻结"使用**（已按用户要求如此对待）。

**新建 `t19`**（kind=repair，`sourceTaskId=t18`，`sourceFindingIds=[PIN-U10-01]`，inScope 仅 pin 文件，assignee=setup-architect）：
① 修正 `checks.u10` 谓词（断言 U10 条目 topic/detail 含 `QVM` 且含 `concurr`；U11 断言含 `SIGN-CONVENTION`）⇒ 冻结产物上必须 true，且 **u10 与 u11 同时 true**、旧新块不得并存矛盾；
② `frozenAt`/`measuredAt` 写为**本次修正的真实墙钟**；
③ **保留** `twoConsecutiveRunsIdentical` 与两项相同哈希；
④ **变更后回读**：pin 全项 true + `pin.sha256 == 产物现算字节哈希`（证据入 output）；
⑤ **不得改 `setup-contract.json` 本体**（保持 revision 21 / 328723 B / `7f505fdb…`）；⑥ 回报并标 completed。

**冻结态汇总（18:12 现算）**
| 产物 | 现算 | 状态 |
|---|---|---|
| `setup-contract.json` | **revision 21 / 328723 B / `7f505fdb…`**（mtime 18:11:43；18:12:55 复读未变） | schema **exit 0**；两次生成同哈希；U canonical ✓；**已冻结** |
| `test-plan.json` | **v18 / 161516 B / `0578bd5e…`** | schema **exit 0**；**t17 仍欠两次生成同哈希证明** |
| `test-plan-tm600-tm601-measurement-excerpt.md` | **8423 B / `9554d4d6…`** | 已由 `delay_ms(2)` 修正为 `delay_ms(1)` + Amendment 1；**t5 绑定输入** |
| `implementation-payload-TM600-TM601.cpp` | **27676 B / `ca61d5acb6a2aee7ea1dae06fba771bcdb46100acee52624526c0bd6b3baa0c9`** | 仅注释级更新（继电器措辞改为器件级"不得进入 required-on 集合"）；可执行差异无 |
| `schematic-ir-sensing.json` | 47446 B / `43ad8c84…`（三方独立一致） | 我早期 `47156/ad9859e9…` **已作废** |

**解锁顺序（用户裁定，不变）**：**t19 + t17 均 completed** → Captain 独立复验（两份现盘哈希、**pin 全项 true 且哈希一致**、schema、U10/U11 canonical、BST−SW、**短时稳定复读**）→ 才创建**实现任务（显式依赖 t17+t18[+t19]）**并固定冻结双哈希 + excerpt 哈希。**在此期间禁止目标树写入、禁止 Full access**；`devel` 与目标树至今零写入（`test.cpp` = `5c9cb3f9…3317`）。

## t17 completed（计划冻结修复，Captain 接管执行，18:4x）

**起因**：t17 声明内的必须项"BST−SW 对齐裁定 (ii)"连续多轮未落地（我实测 v19 中 `SW12_U1REF_BST_ACM` 与 `intended-but-unrealisable` 均 **0 命中**），而 owner 的回合被跨成员协调占用 ⇒ 按用户"达成即收口"要求，Captain 接管（reassign → attempt 3）并本轮完成。

**配对哈希**：BEFORE v19 = 164399 B / `d2aef4ad5f3e48f939256220bbcf4baa4a0693cfd1770d31c8868f9eb41719bb` → **AFTER v20 = 166099 B / `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016`**

**改动（均在生成器 `test-plan-build.py` 内，非手改 JSON ⇒ 可复现）**
1. **BST−SW 裁定 (ii) 落地**：`items[TM600].assumptions` 改为"**基线＝接地参考 ACM200 对 `SW12_U1REF_BST_ACM`（闭合集 `[110,61]` = K110_ACM18_BST / K61_ACM8_SW）**；**FPVIe1-CH1 = INTENDED BUT CURRENTLY UNREALISABLE**"，附**三条证据**（ch1 无最小端点宏、仅 composite `K_FPVIH_TO_BST_B=131,132,134,135`；该四只属 ch1 感测浮动/本地感测/PC 类，即负列表 87–91 禁激励的同类；live 无 TM 经 FPVIe1 驱动 BST）＋重启前提＋**更正后的拆函数绑定理由**（0x59/0x5A HS/LS 位互斥 + PMID 设定值 15 V vs 9 V，**不是**通道预算）。
2. **`globalRulesApplied` 的 R-BST-SW** 同步改为同口径。
3. **生成器幂等**：`generatedAt` 原为 `datetime.now(CST)` 墙钟 ⇒ 字节幂等**不可能**；已改为**由 revision 派生的常量**并加说明注释。
4. 版本串提升为 **v20**（保留 v19 说明作历史）。

**验证**：两次连续运行 `test-plan-build.py` → **字节与哈希完全相同**（166099 B / `1925250d…`）；`validate_team_artifact.py test-plan` → **exit 0**；`SW12_U1REF_BST_ACM`=3、`INTENDED BUT CURRENTLY UNREALISABLE`=1、`[110,61]`=3；U canonical（`U10 - QVM` / `U11 - SIGN-CONVENTION`）保持。

**剩余**：**仅 `t19`**（pin 的 `checks.u10=false` 假阴性修正；已代 claim，attempt_id `65752c32-bc57-4dad-91a4-fc5c91717732`，assignee=setup-architect）。**t19 completed 后** → Captain 独立复验（双 hash + **pin 全项 true** + schema + U10/U11 + BST−SW + 短时稳定复读）→ 才创建实现任务（依赖 **`[t17, t18, t19]`**）。

## 冻结门禁达成：Captain 独立复验 18/18 PASS → 创建实现任务 t20（18:2x）

**三项冻结任务全部 completed**：`t17`（计划冻结：BST−SW (ii) + 幂等；Captain 接管执行）、`t18`（setup 最终冻结 + 撤回 + 冲突登记）、`t19`（pin 谓词假阴性修正；Captain 接管执行）。

**Captain 独立复验（`verify_freeze_gate.py`，同一次读取 + 6 秒稳定复读）：`checks=18 PASS=18 FAIL=0`**
| 组 | 结果 |
|---|---|
| 现盘快照 | `setup-contract.json` **329115 B / `295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c`（rev 22）**；`test-plan.json` **166099 B / `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016`（v20）**；pin 6505 B / `0a0c1dc4…`；`implementation-input-pin.json` 3907 B / `a69d6b49…` |
| schema | setup-contract **exit 0**、test-plan **exit 0** |
| U canonical | 契约 U10 = "QVM ch0 concurrency (verbatim captain text)"、U11 = "SIGN-CONVENTION…"；计划 limitations `U10 - QVM` / `U11 - SIGN-CONVENTION` 各 1 |
| BST−SW (ii) | 计划 `SW12_U1REF_BST_ACM` ×3、`INTENDED BUT CURRENTLY UNREALISABLE` ×1；契约 ×9 |
| pin | **全部 checks = true**（含 `u10=true`）；`pin.sha256 == 产物现算` ✓；`twoRunsByteIdentical` ✓；`frozenAt` = 真实墙钟 18:19:30 + `frozenAtKind` |
| t18 撤回 | 四项 `ateStimulus` 已删除；冲突两侧 locator 并列（"Neither side is averaged or deleted"）；**撤回溯源句在位**（"SUPERSEDED, not pending"） |
| 稳定复读 | 两份产物 6 秒后**哈希不变** |

**实现任务 `t20` 已创建**（kind=implementation，`sourceTaskId=t5`，**依赖 `[t17, t18, t19]`**，assignee=ate-implementer）：固定冻结输入（setup rev22 `295d483a…`、plan v20 `1925250d…`、excerpt `9554d4d6…`、payload `7902f5d9…`、备份 `5c9cb3f9…`）；**禁用哈希清单**（`b98cd824…`/`30b96931…`/`7f505fdb…`/`9f6d6e07…`/`e2be6d63…`/`d2aef4ad…`）；开工前 mismatch 复核 → 备份 → 幂等写入 → 回读；12 项门禁 **delta vs baseline**（11 GREEN + `cbit` KNOWN-RED）；Release 编译；`implementation-manifest.json` schema PASS；署名"内容作者=ate-implementer / 执行者=写入方"；**无写权限则停在 payload，绝不伪装**。

**边界**：**Full access 仅在本任务即将写 `ForCodexDebug` 的同一回合启用**，完成后恢复 Workspace Write；**`devel` 严禁写**；不授权机台/电性验证；编译闭环 ≠ 电性签核。目标树至今零写入（`test.cpp` = 434629 B / `5c9cb3f9…3317`）。

## 🚀 实现已落盘（本轮首次写入目标树）+ 门禁 delta 结果（18:3x）

**写入授权**：Captain 会话在 `workspace-write` 下被拒 → 按 harness 规则**同回合升级一次**（`danger-full-access` + 理由）→ **用户批准**（探针 `WRITE OK`）⇒ 进入用户裁定的"**实现写入回合**"，由 **Captain 作为写入方**执行；**内容作者 = ate-implementer**。

**落盘（`apply_payload_to_target.py`，前置断言 + 写后回读）**
| 项 | 值 |
|---|---|
| BEFORE | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` = **434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`** |
| 备份校验 | `backups/test.cpp.before_TM600_TM601.bak` **逐字节等于** live（434629 B / 同哈希）|
| payload 校验 | 28222 B / `7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122` ✓（与冻结值一致）|
| **AFTER** | **462848 B / `3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479`**（+28219 B）|

**独立复核（`verify_applied_target.py`，6/6 PASS）**：① 原有部分孤立 LF 数保持不变（3→3）；② live == baseline + 归一化 payload **逐字节相同**；③ 追加区块 **0 孤立 LF**；④ `DUT_API` 定义 **`TM600_HS_RDSON`=1 / `TM601_LS_RDSON`=1**；⑤ 代码级（剥离注释）`delay_ms(1)=6 / delay_ms(2)=0`、`SetClamp(50,50)=2`、`MeasureVI(200,5=2`、`FPVIe_10A=0`、`FPVIe_10UA=2`、`rampi_capv=0 / rampv_capv=0`；⑥ **真实新增能力**：两个符号在 baseline 中不存在。
**★ 方法学更正（Captain 自纠）**：首次复核曾 FAIL，原因是我在**整块（含注释）**上计数 —— 注释里的"禁用清单"提到 `rampi_capv`/`rampv_capv` 等，导致 1/3 而非 0/2 的假失配；改为**剥离注释后的代码级计数**即全绿。**"delta-only"判据与此同理**。

**meta 再生（第 5 步，`scripts/gen_testitems_meta.py` + `gen_test_conditions.py`，exit 0/0）**
- `project/DALI/meta/dali_tm_meta.json` = **146180 B / `1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693`**（101 函数，含 `TM600_HS_RDSON`×1 / `TM601_LS_RDSON`×1）
- `project/DALI/meta/test_conditions.yaml` = **11627 B / `4dd0468efeb1708faa42ea8ae364791bd59b50dbf61a7691165d6e3bcdac1279`**

**门禁 delta（`scripts/run_gates.ps1`，baseline 仅 `{"cbit": true}`）＝ 10 GREEN + 2 NEW-RED（阻塞）**
| 门禁 | 状态 | exit | 日志 | 日志哈希 |
|---|---|---|---|---|
| material-audit / material / material-status / awg / meta / smoke / input-sync / merge / bst-sw / path-def | **GREEN** | 0 | 见 `gate-logs-t20/` | 已登记 |
| **relay-trace** | **NEW-RED** | 1 | `relay-trace.log`（1035 B） | `53c3c0cfcc8cd90463286134bd7fee9160e7e6753b29b808b6815cadc2151833` |
| **cbit** | **NEW-RED** | 1 | `cbit.log`（4782 B） | `2fb094e5b188af1b79ce0d5d33715b2cd5f8a75746ba493415cdf4de32cd3f38` |

- **`relay-trace`**：**`TM601_LS_RDSON` 静态供电 SW/VBUS 但未闭稳压电容 `K45_Cap_SW1_BST1`/`K44_Cap_SW2_BST2`/`K57_CAP_BST_SW`/`K5_VBUS_Cap`（FR-001 反向: 供电→闭; meta 权威）** ← **本次新增代码直接触发**；另有 `TM643_VBAT_LOOP_INDICTOR` 2 条（待定性是否存量）。
- **`cbit`**：`K168_R100M_VCP_F`/`K169_R100M_PB5_F`/`K170_R100M_VAC_F` = "目标有脚本无"（待定性）。

**任务态**：`t20` 已被实现者标 failed（其会话无写权限，如实上报"payload 就绪、权限未生效"）；写入实际由 Captain 在本回合完成 ⇒ 新建 **`t21`（repair，`sourceTaskId=t20`，**不依赖失败的 t20**，平台规则禁止依赖 failed）** 承接：闭合 2 个新增红 + 归属定性 → **delta 0 新增红** → Release 编译 → schema-PASS manifest。
**尚未做**：Release 编译（依赖门禁先归零）、`implementation-manifest.json` 定稿、t6/t7/t8/t9。

**边界**：`devel` **零写入**；不授权机台/电性验证；**编译闭环 ≠ 电性签核**。

## 🔎 独立规则审查项（用户提供证据 + Captain 现场核验）—— t21 的必做清单与 t6 的明确项

> 用户明确：**不要仅满足语法编译**；以下为独立规则审查的明确项。**t20 failed 保留记录，t21 完成后才放行 t6/t7。**

### F1【门禁harness 缺陷，已由 Captain 实测证明】`cbit` 的 NEW-RED 是**假阳性**
| 读取方 | 结果 |
|---|---|
| Python（授权读者，明文） | `scripts/gate_baseline.json` = **28 B**，UTF-8 BOM + `{"cbit": true}` ⇒ 解码成功 |
| PowerShell（`run_gates.ps1:65` 的 `Get-Content -Raw -Encoding UTF8`） | 读到 **8192 B 的 TSZ 密文**，首 60 字符 = `%TSD-Header-###%…` ⇒ **`ConvertFrom-Json` 抛错**（"Unexpected character encountered while parsing value: %"）⇒ `$baseline` 保持空 ⇒ **所有红灯一律判 NEW-RED** |
**结论**：`cbit` 本来就在基线里（KNOWN-RED），被误判为新增红。**处置：修 `run_gates.ps1` 的基线读取（改用 python 授权读者解析后回传），严禁改写 `gate_baseline.json` 掩盖。** 同步须复核 `relay-trace` 是否也被该缺陷误判 —— 见 F2（其发现本身**真实**，故该门仍为真红）。

### F2【真红】`TM601_LS_RDSON` 缺稳压电容闭合（与 TM600 不对称）
payload 两处 SetOn 列表对比（行号=payload 内）：
- TM600（L189）：`K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, **K57_CAP_BST_SW**, 126, -1`
- TM601（L320）：`K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, 126, -1` ← **缺 `K57_CAP_BST_SW`**，且两函数均缺 `K44_Cap_SW2_BST2` / `K45_Cap_SW1_BST1` / `K5_VBUS_Cap`
⇒ 门禁 `relay-trace` 对 TM601 的 4 条 FR-001 发现（静态供电 SW/VBUS ⇒ 须闭对应稳压电容）**成立、须修**。

### F3【命名】`126` 字面量应改用宏名
payload 用裸 `126`；目标树 `source/StdAfx.h`（57433 B）实测 `#define\tK126_V1P5_CAP\t126` ⇒ **宏存在、非虚构**，但应按宏名书写（避免数字漂移）。

### F4【量程规则冲突（两函数）】≥2× 且"最小合规档"
payload 全程使用 `FXVIe_PLUS_10V`，其中：
- `PMID_HG2_FXVI.Set(FV, **15**, FXVIe_PLUS_10V, …)` ← **15 V 在 10 V 档上，超出量程**
- `PMID_HG2_FXVI.Set(FV, **9**, FXVIe_PLUS_10V, …)` ← 违反 ≥2× 余量
- `VBAT_PD3_FXVI.Set(FV, 4.2, 10V…)`、`V1P5_U34PS_FXVI.Set(FV, 5, 10V…)` 亦须复核
**按用户只读确认的 SDK 事实**（来源=用户从本机 SDK 头只读确认，非 Captain 实测；Captain 的独立检索升级**已被用户拒绝**，故不另法绕取）：`FXVIe_PLUS_20V/30V/40V`、`ACM200_20V/40V` 均存在 ⇒ 逐档应为 **15 V→`FXVIe_PLUS_30V`、9 V→`FXVIe_PLUS_20V`、ACM 10 V→20 V、ACM 20 V→40 V**；**并须检查回落台阶（10/5/0）与关断态的档位**。

### F5【TM601 符号/除零风险】
`R[mΩ] = MVRET / fabs(MIRET) × 1e3`：TM601 用**派生 −1 A**，若 `MVRET` 取到负值将得**负 RDSON**；`MIRET ≈ 0` 时**除零**。须加保护与明确的符号前提说明。

### F6【脉冲余量】2 ms 为"理论零余量"
1 ms settle + **理论** 1 ms acquisition（200 × 5 µs）= **恰好 2 ms 硬上限**，**未计驱动/调用延时** ⇒ **上机前不得据此视作"实测脉冲合规"**。

### F7【产物落点】meta/test_conditions 落在 DSH 工作区
`gen_testitems_meta.py` / `gen_test_conditions.py` 实际输出到 **`D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\meta\`**（`dali_tm_meta.json` = 146180 B / `1c849664…`；`test_conditions.yaml` = 11627 B / `4dd0468e…`），**不是 VS debug 树** ⇒ 须在 manifest/验收中如实标注落点与用途。

**结论（门禁判定复核）**：`relay-trace` = **真红**（F2/F4 相关，且 F4 未被门禁覆盖，须独立审查）；`cbit` = **假阳性**（F1 harness 缺陷）。**t20 的"无新增门禁失败"仍不成立**（relay-trace 真红在），**t21 须完成 F1–F7 后重跑门禁并复算 delta**，之后才放行 t6/t7。

### F8【根因：门禁供电模型与 BD-08 裁定冲突 —— 用户提供 + Captain 现场核实】`K5/K44/K45` 不得盲闭
**现盘 meta 原文（我实测 `project/DALI/meta/dali_tm_meta.json`）**
```
TM601_LS_RDSON.hardwareInit : vset vbat 3.5 / vset vdrv 5.0 / vset vbus 5.0 / iset pmid_sw 1.0 (1e-3)
TM601_LS_RDSON.capAuthority.powered_pins = ["ISW","SW","VBAT","VBUS","VDRV"]
```
**冻结裁定（BD-08 + `test-plan.json` v20）**：TM601 的 ATE 激励 = **VBAT 4.2 V、PMID 9 V、VDRV 5 V**；**VBUS 5 V 仅 `simulationDomainReference`、非 ATE 激励**。
⇒ **门禁"静态供电 VBUS"的前提来自 meta，而 meta 取的是 OVERVIEW/`.sv` 层（3.5 V、vbus 5 V）** ⇒ 与本次冻结裁定冲突 ⇒ **`K5_VBUS_Cap` 缺失属模型假阳性**。

**逐条布线核查（`project/DALI/SCH-Connect-Map.txt`，只读）**
| 电容 | 图内定位 | 该节点到达路径 | 判定 |
|---|---|---|---|
| `Cap2_VBUS_S1 4.7uF`（**K5**） | L915 `VBUS 稳压 … 需闭合: K5` | VBUS ← `K3`（L213）/ CH1 `K138,K139,K145,K146,K3`（L421）；**`K154+K155` = `CH0 High -> PGND`（L156）** | **不闭**（VBUS 非本项 ATE 激励；实施者注释 "VBUS reachable via K154_BUSH0_AMUX" **事实错误**，须改） |
| `Cap_SW2_BST2_S1 220nF`（**K44**） | L906 `SW2 稳压 … 需闭合: K44` | SW2 ← `K46,K49`（L183），**与 SW 不同节点**，且**不在** meta `powered_pins` | **不闭**（门禁把 SW/SW1/SW2 当"电容家族" ⇒ 过度要求） |
| `Cap_SW1_BST1_S1 220nF`（**K45**） | L905 `SW1 稳压 … 需闭合: K45` | SW1 ← `K46`（L177），**不同节点**，不在 `powered_pins` | **不闭**（同上） |
| `Cap_SW_BST_S1 220nF`（**K57**） | L904 `SW 稳压 … 需闭合: K57` | SW ← `K60,K61`（L174）；**SW 确在 `powered_pins`** 且为本函数低侧力节点 | **待判**：须先读门禁规则自身例外句（"unless that PIN is the measured current path"），若覆盖 SW 则连 K57 也不该盲关 |

**修法（用户裁定：带反证修规则/例外，不得为门禁变绿盲闭继电器）**
- **(A) 修门禁输入/模型**：TM600/TM601 的 `hardwareInit`/`capAuthority.powered_pins` 以**冻结 ATE 激励**为准（VBAT 4.2 / PMID 9 / VDRV 5；**排除 VBUS 与一切 simulation-domain 轨**），SW1/SW2 与 SW 分节点判定；**倾向 run 作用域覆盖/例外，不改通用 `gen_testitems_meta.py`**；或
- **(B) 具名例外**：登记"TM601 不适用 VBUS/SW1/SW2 家族电容"的例外 + locator，并在 manifest `limitations` 如实记录。

**同时保留**：`K126_V1P5_CAP` 修正（有 `#define` 依据，非盲改）；`TM643` 作为**已记录存量偏离**（改动前副本跑门禁得逐字节相同告警），如修另开任务。
**Captain 流程缺陷（已认）**：上一条 handoff 只转述门禁**汇总**，**漏掉日志中的 `*** FAIL *** 虚构继电器名 126`** —— 该 error 才是阻塞项；**规则：门禁结论必须以日志原文为准**。

## 职责分离链（用户裁定）+ 旧 t6 悬空处置（2026-09-16 18:34 +08:00）

**备份与恢复（措辞纠正）**：目标树已有**逐字节备份** `backups/test.cpp.before_TM600_TM601.bak`（434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`）；**恢复须按校验流程执行**（先核对备份哈希与现盘哈希 → 以 python 明文·字节方式写回 → 回读复验），**尚无经演练的一键恢复脚本**（不得表述为"一键还原"）。

**用户要求**：meta/BD-08 冲突不得由 Captain 或实现者单独裁定；`rule-reviewer`（或独立 schema/规则修复任务）**只读**审查 FR-001 对 TM600/601 的适用边界并给出**带 locator** 的修正规则/例外建议；`ate-implementer` **只负责经批准的代码修复**；且**不得让旧 t6 因依赖 failed t5 永久悬空**。

**已建立的任务链**
| 任务 | 归属 | 依赖 | 内容 |
|---|---|---|---|
| **t22** | rule-reviewer（**只读**） | — | FR-001 适用边界审查（`verify_relay_trace.py:317-328` 原文 locator）→ 判定四条电容发现真红/假阳性 → 给出 **(A) 修门禁输入/模型（run 作用域，不动通用 `gen_testitems_meta.py`）** 或 **(B) 具名例外** 的带 locator 建议；明确 meta 供电模型与 BD-08 冲突的因果链；单独裁定 `K57` 是否被"measured current path"例外覆盖；**只读约束**（不得改 payload/契约/计划/生成器/目标树/devel） |
| **t23** | ate-implementer | **[t22]** | **经批准的代码修复**：只按 t22 判为必需者闭合电容、移除假阳性闭合（至少 `K5`）、保留 `K126_V1P5_CAP` 命名修正、改写"inert for the measurement"推断性注释、保持全部代码不变量与 scope 纪律 |
| **t24** | rule-reviewer（独立、只读） | **[t23]** | **独立实现审查**（`reviewedTaskId=t23`）：t22 裁定一致性、代码不变量、冻结口径、scope 纪律、推断性表述改写 → verdict `pass`/`needs_revision`（附结构化 findings） |

**旧 `t6` 悬空处置（平台限制，如实记录）**：`t6` 依赖 failed 的 `t5`，**永久不可认领**。Captain 尝试 `reassign_task(t6 → captain)` 以取消，**被平台拒绝**：`Error: task t6 is blocked by unfinished dependencies: t5 — complete them before captain takeover`。⇒ **无法取消/改派**；其职责已由 **`t24`**（对象改为 t23、依赖 t23）承接。恢复者须知：**t6 将永远停在 blocked，属平台结构限制，不是遗漏**。

**修订后的有效交付链**：`t1→t2→t3→t4`（已完成）→ `t11/t12/t13`（规划收口）→ `t16→t18` + `t17`（**输入冻结，已完成**）→ `t19`（pin 修正，已完成）→ `t20`（**落盘，已执行**）/`t21`（门禁修复，进行中）→ **`t22→t23→t24`** → 门禁 delta 归零 → Release 编译 → manifest → t7/t8/t9。

## 🔴 F9【紧急代码审查：F5 不可落盘，payload 标记"未批准"】（用户裁定 + Captain 实测确认，18:5x）

**用户裁定**：现盘 t21 payload（31,133 B / `620d99eaa87b6971cddb16a2dbb1f4af4c950f9fc0b0edcf9b266eb824b53ebf`）**F5 改法不可落盘**；**标记为未批准/待修，不执行目标树替换**。

**Captain 独立实测确认（locator = payload 行号）**
| # | 缺陷 | 证据 |
|---|---|---|
| 1 | **TM600 注释误贴** | L270–L272 在 `TM600_HS_RDSON` 段内写 "with the derived **−1 A** command on **TM601** … a negative RDSON is the expected magnitude"（TM601 情形贴到 TM600） |
| 2 | **符号错误：正电阻会输出为负** | L407–L409 `v_meas = MVRET`(SIGNED)、`ls_rdson = (i_meas>0.1) ? (v_meas/i_meas*1e3) : 0.0`；L401–L403 自述"期望差分为负" ⇒ 正阻值必然输出负值。TM600 同理（L278–L280） |
| 3 | **零流 fail-OPEN** | L280 / L409：`\|I\| ≤ 0.1 A` ⇒ 返回 **`0.0` mΩ** ⇒ **断路/未施流被误报为"超低阻合格"** |
| 4 | **量程违规** | L227（上台阶）/ L286（回落台阶）`PMID_HG2_FXVI.Set(FV, 10.0, FXVIe_PLUS_10V, …)` = **1×，违反 ≥2×** ⇒ 应 `FXVIe_PLUS_20V`（其余配对经逐条核验均满足：15 V→30 V、9 V→20 V、5 V→10 V、ACM 10 V→20 V） |

**用户提供的项目内 fail-closed 先例（采用；须由实现者独立复核 locator）**
- `source/Test_Method.h:32` 定义 **`ERROR_RES 9999`**；先例 `debug/source/test.cpp:8087-8090`：`im3-im1 <= 1e-6` 时写 `gain[site] = ERROR_RES`。
- ⇒ **先清零/下电，再按既有失败码记录**；**禁止自创 0 mΩ / inf / NaN**。
- **TM601 符号裁定**：负 FI 与负 MVRET **同号**时计算**正值** `MVRET/MIRET`（或 `fabs/fabs`）；**但必须单独诊断反向极性**；**不得以负数作为 "expected magnitude"**。

**已下发的具约束力要求（8 条，等同 t23 追加验收）**：正幅值阻值；同号判据 + 独立极性异常上报；`|I| ≤ 门限` 先清零再记 `ERROR_RES`；**cleanup 不跳过**（含 R-POFF：FPVI0 最后释放）；删除 TM600 误贴注释且各函数只描述本函数；10 V 台阶（上/回落）→ `FXVIe_PLUS_20V` 并给出完整配对表；保持代码不变量；范围纪律 + 修后重跑 `relay-trace`/`awg`/`bst-sw`。**同步扩展 `t24` 审查清单**（上述 7 项为必查）。

**平台限制（如实记录）**：尝试以新任务 t25 替换 t23 时被拒 —— `inScope overlaps t23 …`；随后尝试 `reassign_task(t23 → captain)` 亦被拒 —— `task t23 is blocked by unfinished dependencies: t22`。⇒ **t23 无法取消/替换**，故本修正令以**具约束力的 Captain 追加验收**形式附加于 t23（并已入台账与 EXECUTION_PLAN），**落盘仍由 Captain 在复核后执行**。

## F8 根因证成（meta 原文 + 生成器源码）+ **K57 判定被反转的缺口**（实现者提供，Captain 复核）

**根因证成（从 meta 与生成器自证，非推断）**
- `project/DALI/meta/dali_tm_meta.json` → `TM601_LS_RDSON`：`hardwareInit: vset vbat 3.5 / vdrv 5.0 / **vbus 5.0** / iset pmid_sw 1.0`；`capAuthority.powered_pins = ["ISW","SW","VBAT","VBUS","VDRV"]`，`mi_pins []`、`ramp_pins []`、`testpad_pins []`。
- **生成器自证**：`gen_testitems_meta.py:148-149` 的 `capAuthority` 取自 **OVERVIEW 行**（`powered_pins` = vset + Power 列 + Dynamic 裸 pin）⇒ **门禁"VBUS 静态供电"的前提生成自被 BD-08 取代的层** ⇒ **模型假阳性**（与 Captain 的 F8 判定一致）。**K5 不闭。**

**逐电容裁定（均带 locator，见 `t21-tm601-fr001-exception.md`）**：**K5 不闭**（VBUS 非本项 ATE 激励；到达需 `K3`，L213/L421；`K154+K155`=PGND，L156）；**K44 不闭**（SW2 ← `K46,K49`，L183，且不在 `powered_pins`）；**K45 不闭**（SW1 ← `K46`，L177，同）；**K57 暂闭**（依据见下，**待 t22 反转**）；`K126_V1P5_CAP` 保留。K44/K45 被点名仅因家族判定按**前缀**：`cap_pin()`（`verify_relay_trace.py:100-115`）产出 `SW1_BST1`，`fam_intersect()`（`:56-58`）以 `"SW1_BST1".startswith("SW")` 命中供电 pin `SW`；`gen_testitems_meta.py:394` 用同一家族逻辑生成其审计列。

**K57 的规则依据（逐字 + locator）**：`verify_relay_trace.py:325-326`
```python
if fam_intersect(mi, ptok) or fam_intersect(ramp, ptok):
    continue  # 该 PIN 被测电流 / 是 ramp 扫描源 (按 PIN 豁免, 非按函数)
```
⇒ **豁免按 PIN（`mi_pins`/`ramp_pins`）生效**，而本项 meta 两者**均为空** ⇒ 规则当前要求闭合该电容。

**⚠ 反转缺口（实现者主动披露，价值高）**：本项**确实测电流**（`iset pmid_sw 1.0` 在其 `hardwareInit` 内，回流路径经 SW），但生成的 `params`/`mi_pins` **为空** —— 因为 `gen_testitems_meta.py:191-197` 的推导**漏掉了该 pin**。⇒ **若按 (A) 正确填充 `mi_pins`，豁免即生效 ⇒ `K57` 也不应闭合 ⇒ 本项将"零电容闭合"。** ⇒ **K57 的闭合在模型修正后可能被推翻**，故**在 t22/(A) 定案前不得落盘**。

**后续修法（与用户偏好一致）**：**(A) run 作用域覆盖/例外**（不改共享 `gen_testitems_meta.py`、不动其它 run）：TM600/TM601 的 `hardwareInit`/`powered_pins` 对齐冻结 ATE 激励（VBAT 4.2 / PMID 9 / VDRV 5；排除 VBUS 与全部 simulation-domain 轨）、按真实测量 pin **填充 `mi_pins`**、并把 SW/SW1/SW2 视为**不同节点**。另：**`t25`** 已承担 harness 侧三处修复（基线 python 读取 + 前缀碰撞 + VBUS 可达性）。

**payload 现状（未批准，未落盘）**：32969 B / `7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b`；`K5/K44/K45` 进 executable code = **0**；`K57` ×2；`K126` ×2；`inert for the measurement` = 0；`SETTLING IS NOT ANALYSED` = 1。**F9（F5 正幅值/极性诊断/`ERROR_RES` fail-closed/cleanup/10 V 台阶→20 V/TM600 注释）四项仍全部未实现** —— 详见 F9 节。

## ✅ t22 独立只读裁定（verdict=pass）—— FR-001 适用边界定案 + 两条叙事纠正

**产物**：`review/t22-fr001-applicability-review.md`（27514 B / `29d1e070…`）、`review/t22-fr001-findings.json`（18946 B / `dcb9af2c…`）、只读证明三件套（BEFORE/AFTER/verify：11 个被检对象前后 python-plaintext sha256 全一致；`devel` 与目标树未动；review 目录外零写入）。

**四条判定（TM600_HS_RDSON = 0 条，无需处置）**
| 发现 | 判定 | 依据 |
|---|---|---|
| `K5_VBUS_Cap`（L915） | **假阳性** | 本 run 无 VBUS 电源；meta 的 VBUS 唯一源自 `vset vbus 5.0`（BD-08 定性 simulationDomainReference）；原理图上 VBUS 只是浮空通道到达点（L213 `K3` / L421） |
| `K45_Cap_SW1_BST1`（L905） | **假阳性** | 前缀折叠：`fam_intersect(powered,'SW1_BST1')={'SW'}`（`startswith`）；SW1/SW2 未供电且不在 `powered_pins` |
| `K44_Cap_SW2_BST2`（L906） | **假阳性** | 同上（`SW2_BST2`） |
| **`K57_CAP_BST_SW`（L904）** | **真红（针对被评估版）⇒ 应闭合** | 豁免**不覆盖**：`L325` 比对的是**电容自身令牌 `BST_SW`**，而 `BST_SW` 是**真实供电轨**（`bst_sw 5.0`，`powered_pins` 显式含）⇒ 豁免不触发 |

**★ 裁定效果（反转我先前的疑虑）**：`K57` **应保持闭合** —— payload 现版的 K57 闭合**正确**；实现者先前"若填充 `mi_pins` 会使豁免触发、K57 也应移除"的推论**被 t22 的更精确读法取代**（豁免按**电容令牌 `BST_SW`** 比对，而非 pin `SW`）。

**因果链（t22 给出）**：`gen_testitems_meta.py:148-180`（vset → `powered_pins`）→ meta 含 **VBUS** → `verify_relay_trace.py:313/318` 以 meta 为**唯一权威** → L323 未闭 → **L328 假阳性**。

**建议**：**(A) 推荐** —— run 级 meta：**移除 VBUS** + 补**精确** `mi_pins`/`ramp_pins` + **前缀匹配改令牌边界**；⚠️ **`fam_intersect`（L56-58）被 L318/321/325 与降级的 L394 共用 ⇒ 动共享脚本前必须沙箱对照**。**(B) 仅作临时具名例外**（B1/B2 不适用、B3 适用）。**禁止**改 `gate_baseline.json` 遮挡。
**"可否为让门禁变绿而关闭未供电节点的继电器" = 否**，并附**实证反例**：旧 payload 为过关加入 `K5_VBUS_Cap`，却**未闭真正到达 VBUS 的 `K3_BUSL0_VBUS`**。

**⚠ 两条叙事纠正（必须更新，防止恢复者误判）**
1. 那 **4 条是 WARNING**（`L328`）；**FAIL 实由另 2 条 `虚构继电器名 126` ERROR（L416-420）产生** —— 与 FR-001 **无关**。（我先前的 F2 汇总把它当作阻塞项，属措辞不精确。）
2. **门禁日志评估的是 18:23:31 的部署版**，**不是** 18:33:33 的 payload ⇒ **两者不可混引**。

**t22 交接的未闭合项（由 Captain 派活）**
① **payload 尚未写入目标树**：部署态 `test.cpp` = `3dbceb49…`，`TM601` 的 `SetOn@9197` 仍缺 4 个 Cap 且用裸 `126` ⇒ **这是 FAIL 的直接原因**。
② **run 级 meta 未移除 VBUS、前缀折叠未修** ⇒ **即使 payload 落地，门禁仍会继续报 3 条假阳性**（→ 由 **t26** 承接）。
③ **UNKNOWN**：重跑元数据生成器是否会**覆盖** run 级修正（只读约束下未执行，**需沙箱验证**）→ 由 t26 验证。
④ `K44/K45/K57/K5` 均属 **`_S1S2` 共享家族**（`Dali-SCH.csv:336/326/346/316`）⇒ 须按契约的**跨 site 规则**处置（→ 由 t26/t24 覆盖）。

**独立互证（并发事实）**：审查期间实现者把 payload 改为 32969 B / `73995983…`（18:36:18：移除 K5/K44/K45、**保留 K57**、裸 `126`→`K126_V1P5_CAP`），其注释**独立复述同一因果链** ⇒ 与 t22 裁定**独立互证**（非转述所致）。

## 🚀 里程碑与"发现 high 缺陷"锚点（Captain 实测，恢复时先读本节）

**已达成（我有实测证据，非成员转述）**
```
部署态 test.cpp   = 469,714 B / 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a   (mtime 18:53:33)
落盘复验          = t23-apply-verification.json → 10/10 PASS（区块 EOF 逐字节保真 / BOM 保留 / 孤立 LF 结构不变 / 两函数各 1 定义
                    / delta(live−baseline) == payload 全 token 相等）
门禁              = 12 门 = 10 GREEN + cbit KNOWN-RED + 0 NEW-RED → 结论"无新增红——收尾通过"（exit 0）
Release 编译      = MSBuild 12.0 / PlatformToolset v120 / Win32 Release → "Release PASSED (0 errors, 0 warnings)"（exit 0）
manifest          = implementation-manifest.json 33,773 B / 7c67aa74498c839d73ee391a1fae43ab39f0f42d4ceba0700ba2c0387192edfd → schema PASS / exit 0
```
**Captain 自陈**：首次落盘复验判 FAIL 属**我的谓词错误**（按整文件计数，判据实为 delta-only）；改用增量口径后 10/10 PASS。两次结果均留档，未删除。

**🔴 独立复核发现并由 Captain 自证成立的 high 缺陷（裁决 (ii) 闭合集合缺半）**
- 要求侧（契约 rev 24）：`tmDeltas.TM600.relaySet` 含 **110**；`aliasResolution[…]closedRelayNumbers` 含 110；`pinRouteTable` BST 路线 `needsClosed=[109,110]`；`L145 "BST": "S5_ACM200_FH18/SH18 (K110_BST)"`；`L1897 relayPath = K110_ACM18_BST -> K61_ACM8_SW`。
- 连接图（Captain 自读）：**L42** `CH0 Low -> BST [Kelvin] 需闭合: K109,K110,…`；**L43** `… K109(ON) -> K110(ON) -> BST_F`；**L109/L110** `… K109(ON) -> K110(Relay-NC) -> PB0_F/PB0_S`；**L724/L725** `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` / `SH18 -> … PB0_S`。
- 实现侧：落盘 TM600 SetOn = `K83,K60,K61,K13,K85,K57,K126` ⇒ **`K109`/`K110` = 0** ⇒ **裁定 (ii) 的 BST 激励路径在实现上不成立**。
- **门禁盲区**：`verify_bst_sw_sequence.py` 对 `K110`/`110`/`needsClosed`/`relaySet` 命中 **0** ⇒ 门禁结构上看不见该缺口 ⇒ **"门禁绿 ≠ 电性正确"的实测实例**（t9 必录）。
- 处置：**不采纳"改契约为 [61]"，除非契约 owner 出示夹具硬连物证**（连接图 K110 路径本身即反证）。

**本轮新建任务（DAG 尾部重建 —— 旧 t7/t8/t9 依赖 failed/终态 t5，永不解锁，故全部替代）**
| 任务 | owner | 内容 | 依赖 |
|---|---|---|---|
| **t27** | test-strategy-architect | 计划收口（补 v20 provenance + teardown 消歧 + 初始化量程 + 按侧车重钉） | — |
| **t28** | compile-diagnostician | RS-1..RS-4 断言 + **用探针制造回退并证明断言变红** + manifest 登记重放 | — |
| **t29** | ate-implementer | **补 TM600 `K109/K110`**（BST 激励路径）→ 新 payload + 独立复核 + Captain 落盘 | t24 |
| **t30** | compile-diagnostician | `bst-sw` 增加"SetOn vs 契约 needsClosed"断言（**阳性对照：当前缺 K110 必须报红**） | — |
| **t31** | setup-architect | 审计链改 append-only + 写明 "traceable 而非 independently verifiable" 定级 | — |
| **t32** | dft-expert | 独立核验真实新增能力 + 八项纪律 + 落盘复算（**取代悬空 t7**） | t24, t29 |
| **t33** | compile-diagnostician | 门禁全跑 + Release 真实编译 → `build-report.json`（**取代悬空 t8**） | t29, t30 |
| **t34** | setup-architect | 最终集成验收 + 隔离审计 + 未声明产物处置（**取代悬空 t9**） | t32, t33 |

**t28 红证通过（把"静默抹除"变成可检出失败）**
```
check_input_sync.py : 8727 B / d8722d91…  →  17,455 B / e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1（新增 RS 组）
RS-1 TM601 powered_pins ∌ VBUS ｜ RS-2 TM600 mi_pins ∋ SW、TM601 ∋ {PMID_SW,SW}
RS-3 hardwareInit vset 轨道集+数值 == 冻结 ATE 且无 vbus ｜ RS-4 yaml _sync.metaSha256 == sha256(meta)
RS-FAIL ⇒ 既有 bad 路径 ⇒ exit 1 ⇒ run_gates.ps1 自动计为 NEW-RED（非 warn）
红证：BEFORE（修复前）IN SYNC / exit 0 → 检不出；AFTER OUT OF SYNC / exit 1，RS-1/2/3 全红
      RS-4 在"戳同拍刷新"的忠实重生成场景仍 MATCH = 预期正确（故 RS-1..RS-3 才是检出主力）
(a) manifest 新增顶层 generationReplayRequirement（revision manifest-amendment-1，含 4 步重放顺序 + detector + redProofEvidence）
     33773 B → 36,733 B，schema PASS exit 0；gate_baseline.json 未改（021015da…）
```
**Captain 对 t28 三条自报项的裁定**：**R1 不改**（红态在汇总层以 input-sync=NEW-RED 已可见，明细在 `gate-logs-*/input-sync.log`；改 `run_gates.ps1` 会动到已复核的 t25 产物，收益仅文字可见性）；**R2 保持不动**（复核进行中，改动会使判据哈希失效）；**R3 采纳**（RS-3 用"轨道集合+数值"双重比较，**收紧非放宽**，符合 fail-closed 纪律）；**R4 登记为限制项**（本任务只让抹除**可检出**、不阻止其发生；预防＝生成器侧加固，留作后续）。
**t28 标 failed 的唯一原因＝独立复核未回收**（与 t25 同一标准，处置正确）；待复核方出意见后另派"复核回填"任务收口。
**t29 待裁定的实质分歧（交由 rule-reviewer 裁定，Captain 不单方裁定）**：TM600 是否**还需闭 K109**？
- 实现者（t29）：补 `K109_BUSL1_PB0` + `K110_ACM18_BST`（引 `pinRouteTable CH0 Low->BST needsClosed=[109,110,138,139,145,146]`）；
- 契约 owner（独立取证）：**只 K110 必需**，`K109` 属 FPVIe 路线（`SCH` L43/L44/L269/L270），契约权威为 `aliasResolution[3].closedRelayNumbers=[110,61]`；
- Captain 补充证据：两套集合属**两条不同路线**（后者含 FPVIe0 的 K138/K139/K145/K146，而 TM600 从未闭过它们）；ACM 源路径见 `SCH` **L723-725**；**无夹具硬连证据**。
⇒ 判定 (i) 非必需 ⇒ minimal-endpoint 违反（needs_revision）；(ii) 必需 ⇒ pass 且 `t35` 补 `[109,110,61]`；(iii) 二者皆可 ⇒ 须给判据。**`t30` 断言设计亦依赖此裁定**（若最小端点成立，断言须同查"不得多闭"）。

**19:35 外部恢复核对新增未决项（取自独立审查原文，非电学裁定）**：`review/t29-k110-implementation-review.md` §2 的 reviewer 明确指出 **TM601 也调用 `SW12_U1REF_BST_ACM.Set(FV, 5, …)`，但 TM601 `pinRouteTable` 无 BST 条目、`relaySet` 和当前 `SetOn` 均无 K109/K110**；要求契约 owner 说明 TM601 的 5 V 如何实际到达 BST，若无可达路径则需修订契约/计划/payload。进一步直读 `SCH-Connect-Map.txt:724-725`：**K110 未动作时该 ACM18 源经 NC 指向 PB0_F/PB0_S**，故若此 5 V 设置实际驱动该源，可能误驱动 PB0；这是连线+代码推论，尚非机台实测。t35 完成摘要只列三项归口，**未见对此第四项的明确答复**。在独立裁定前，不得把 t29 的 TM600 payload 审查 pass 外推为 TM601 电学闭环。另 `implementation-payload-TM600-TM601.cpp` 19:33 现盘已变 **38147 B / `272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0`**，t29 旧审查针对的 **36381 B / `73b511b7…`** 不覆盖新字节；落盘前须重新 pin + 独立复审。恢复入口见 `team/CURRENT_STATUS.md`。

**19:44 t30 新证据（不得漏十项之一 TM1205）**：`gate-logs-t30/bst-sw.log` 对旧部署树给出 TM600 缺 K110、`targets=4 FAIL=1`，门禁只把 `bst-sw` 转为 NEW-RED；这是有效阳性对照。t30 因独立复核未回收保守标 failed，旧 t33 依赖它不能自动解锁。另其 `bst-sw-extended-scope-tm1205.log` 显示 TM1205 在契约 `bst2sw.usedByTm` 中，扩展作用域报缺 `[61,110]`；目前**不能判定是契约登记/路径别名错位，还是实现缺失**，须单独由契约 owner + 独立规则审查裁定，不能因默认门禁仅针对 TM600/TM601 而将 TM1205 算通过。该发现属于本 run 十项范围，必须进入 t34 或其替代最终报告。

**冻结基准（以 Captain 现算为准）**：契约 **rev 24 / 328,805 B / `fd00a508…`**；计划 **live `test-plan.json` = v21 / 176,875 B / `f0f825dd302d4105676b113f2335bc1f6fe54c8bcd46a32d621c1026c111dc04`**（`revisionHistory` 21 条、v20+v21 在位；`inputPin` = rev 24 / `fd00a508…`；**Captain 独立复验：validator PASS exit 0**；歧义句 `floating channel last` = 0，残留 10 处 `floating instrument released last` **全部位于消歧句内部**、非活规范）；历史副本 `test-plan.v20final.json`（`fabdd24f…`）与 `test-plan.v20.json`（`1925250d…`）**保留**（修复"快照缺失致不可复现哈希"缺陷），**canonical 一律为 live `test-plan.json`**；`devel` 零写入；**未做任何电性/机台验证**；**编译闭环 ≠ 电性签核**。

**流程记录（如实，不回滚）**：setup-architect 在收到"仅改一个字段"的授权**之前**已把 `implementation-input-pin.json` 的 plan 侧更新到 v20，并**额外新增** `supersededValues`/`noteForDownstream`/`siblingExplanation` 三字段；其主动披露该偏差。裁定：**保留三字段**（纯增可审计性、不改 pin 语义），偏差记入台账；`status` 仍为 NOT FINAL。

## 🔴 用户阻断裁定已落地为两方独立判定（t39/t40）+ t38 反转结论（Captain，20:1x）

**裁定执行（用户 19:5x 下达的第四项，落盘前必须闭合）**
- **`t39`**（setup-architect，requirements）：契约 owner 侧**独立判定** TM601 的 `SW12_U1REF_BST_ACM.Set(FV,5)` **如何到达 BST** —— IR 路径表 + 权威网表 + 端子表触点语义 + payload 实际激励**四方并用** → 逐步路径 + 每跳 locator；两分支处置：**需 K110/其他继电器 ⇒ 契约/计划/payload 各侧最小修法**；**不需 ⇒ 具体替代路径 + locator**（并解释为何 `SCH:724/725` 不构成反证）；另必答**"悬空驱动应移除还是补齐通路"**。须经 rule-reviewer 独立复核。
- **`t40`**（rule-reviewer，review）：**并行且互不采信**的独立判定 + **PB0 误驱动风险分级**（FACT/INFERENCE/UNKNOWN）+ **对现盘 payload 重新 pin/review**（显式声明旧哈希 verdict 不覆盖新字节）。
- **绑定条款（已下发两方）**：**禁止以"契约未列 BST"代替可达性证明**（用户原话）；反向亦然 —— **契约列了某继电器 ≠ 可达**；可达性只能由**电路路径**证明；结论须标 FACT/INFERENCE/UNKNOWN 并声明**尚非机台实测**。
- **落盘冻结**：`t29_apply_replace.py` 常量虽已改为 `272667f3…`/38,147 B，**按裁定不执行**；**不借旧审批执行改过的脚本**；**两方闭环前不落盘**。

**⚠ t38 的反转结论（实现者已交，待两方独立确认或推翻）**
- 实现者据三方证据判定 **TM601 本不需要驱动 BST** ⇒ **移除**该悬空驱动（TM601 段 3 行可执行代码），**而非**补 `K109/K110`：**(a)** `DFT.csv` TM601 行（L98）不声明 `bst2sw`，其 delta 内 `SW12_U1REF_BST_ACM` **0 次**；**(b)** 契约 rev 24 `TM601.pinRouteTable` **无 BST 节点**、`relaySet` **无 109/110**、`bst2sw.usedByTm` 仅 `TM600/TM1205`；**(c)** 网表 + 端子图：到 BST 需 `K109(ON)+K110(ON)`，**无来源指派给 TM601**。
- **新 payload（引用一律现算 + 内容键）**：**39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`（mtime 19:55:59）**；证据 `t40-tm601-bst-evidence.md` = 8,229 B / `cb322c7ee446efe881ce5786f605be23559fe85a609d9837c16dc4f35ce8c877`；沙箱三门禁 PASSED、**新增红 0**；不变量全保持（TM600 `K109`×1/`K110`×1；TM601 ACM Sets=0）。
- **机制精化（待独立复核）**：`knowledge/hardware/relays.md` L3-31 记该器件为 **G6K-2G-Y DPDT 磁保持、NO 脚未通电即导通**（"默认 2-3 通、6-7 通"，自带"与直觉相反"警示）⇒ 连接图 **`K110(Relay-NC)`＝未动作路径**（未动作→PB0、动作→BST），**非"常闭触点"**；并解释 `K87/K88/K89` 未通电导通 ⇒ 负列表规则应为"**不得加入 required-on 集合**"而非"强制断开"。
- **实现者自陈**：TM601 注释曾写"本项从不驱动该轨"而同函数三行之下正在切换该源 —— **注释与代码自相矛盾**（与早前 "inert for the measurement" 同类），已改正并留痕。
- **纪律**：该结论**不得由实现者单方定案** ⇒ 必须由 `t39`/`t40` 独立确认或推翻后再动契约 rev 25 与落盘。
- **⚠ 时序交叉（实现者主动披露，非抗令）**：**`t38` 在暂缓令送达前已执行完毕**（三条依据已确立、3 行已删、不变量与三门禁已复跑）。实现者**未回溯**并保存**精确回退数据**（两条 `Set(FV,…)` 与一条 `RELAY_OFF`），现计数 **TM601 ACM Sets = 0 / TM600 = 10**（TM600 阶梯未动）。**Captain 裁定：批准、不回溯**（交叉非抗令；改动为精确 3 行删除、完全可逆；再回溯＝叠加一次未授权编辑）。交叉已记入其证据文档 `section 0`。
- **实现者已按 Captain 要求落实 FACT/INFERENCE/UNKNOWN 三分**，并**主动下调自身过度断言**：'源走 PB0 而非 BST' 标为 **INFERENCE（接线推论、非机台实测）**，风险写成**双向**（'BST 未被驱动' ∧ '**PB0 被驱动**'）；**UNKNOWN** = 'PB0 在 DUT 侧是否有电学后果（可能是空载监视点）' 与 '夹具是否硬连 ACM→BST'；其 §1 结论标为 **`PROPOSAL PENDING t39 AND t40`**（不抢答两方判定）。
- **冻结生效（实现者承诺）**：payload = 39,457 B / `2d0984d9…`；证据文档 = **11,691 B / `de6bb17f755e8046579cf6dc0efefd7ad332f2ecc96104b3b51e669d003d99a9`**（由 8,229 B/`cb322c7e…` 改写而来 —— **有归属、已披露、且为满足 Captain 要求的必改项**，不视为违规；此后冻结）；**目标树未动**（仍 t23 `15c7d2b8…`）；`devel` 零写入；**未落盘**。
- **两分支执行口径（已备好）**：**(A) 若两方判"需要驱动 BST"** ⇒ **先契约 rev 25**（`tmDeltas.TM601` 增 BST 节点/路线与 `needsClosed`；`relaySet`/`aliasesUsed`/`usedByTm` 登记）→ **再**恢复 3 行 + 补 `K109_BUSL1_PB0`/`K110_ACM18_BST`（`SCH:42/:43` 为唯一到 BST 的路线）→ 三门禁 → 独立复核 → Captain 落盘；**(B) 若判"不需要"** ⇒ 移除即最终态，`t40` 复核"替代路径陈述" → 一次 REPLACE `2d0984d9…`。**两方分歧时：实现者只报告分歧、不自行裁定**（已承诺）。

**新增两条止损规则（本 run 已四次"同文件不同哈希"）**
1. **内容键引用 + 现算哈希**：payload 按内容键引用，**且内容键必须限定"去注释后的可执行计数"**（缺陷已由实现者逮到并更正：`K109_BUSL1_PB0`/`K110_ACM18_BST` 的**全文本计数是 ×2**、第二次出现在 `PER-FUNCTION JUSTIFICATION` 注释内，**可执行各 ×1**；按全文本匹配会让"继电器列表已丢失、注释仍在"的文件**误通过**）。**修正后判据**：`t29 PER-FUNCTION JUSTIFICATION` ×1（注释，区分修订代际）+ **去注释后** `K109_BUSL1_PB0` ×1、`K110_ACM18_BST` ×1；t38 修订另须 **TM601 ACM Sets = 0 / TM600 ACM Sets = 10**；不变量按可执行口径。哈希每次现算并记 mtime；**②b 剥离方法与计数约定（实现者定稿，可复现）**：**按行剥离行内注释**（`re.sub(r"//.*$","",line,flags=re.M)`）后**去掉前导空白仍非空**方计为可执行 —— **仅剥离"以 `//` 开头的行"会漏掉行尾注释**（实测 `ERROR_RES` 会被算成 4 而非 2）；**`ACM Sets(<fn>)`**（**唯一合法定义**，Captain 裁定）＝ 该函数体内**经 ②b 剥离后仍非空且含 `.Set`** 的行数 —— **不是"仪器名出现次数"**（二者在现盘同为 10/0 属**巧合**：一旦注释在可执行区内提及仪器、或出现非 `.Set` 引用〔如仅 `ACM200_RELAY_OFF` 的调用〕即分歧 ⇒ **"通常相等"的定义＝潜伏的假通过**，与本 run 已修两次的"全文本 vs 可执行""naive vs proper 剥离"同类）；**交叉校验**＝未剥离计数 = 剥离后 + 注释提及数（现盘 TM600 为 11 = 10 + 1）。函数体范围＝从 `DUT_API int <NAME>(short funcindex, LPCTSTR funclabel)` 行到下一个同类行（实测 **TM600(L179-354)=10、TM601(L355-522)=0**，二者属**修订特定键**、须写明 "for the `2d0984d9…` revision"，**非永久不变量**）；**注意不对称**：`PER-FUNCTION JUSTIFICATION` 按**注释**计（全文本 1／可执行 0），继电器名必须按**可执行**计 —— 同一种读法会让"继电器列表被删"的文件通过；
2. **给出哈希即冻结（freeze-on-publication）**：复核期间写入方不得再改；若必须再改，须交回新哈希并由复核方**对新字节重出 verdict**。

**✅ 两方独立判定已完成并一致（20:3x）**
- **`t39`（契约 owner，completed）**：TM601 的 ACM 5 V **到不了 BST**，落在 **DUT 引脚** `PB0_F_S1`/`PB0_S_S1`（同网 `PWM1_*`/`K147_PB0_OSC`/`S24_P10`/`R_PB0`/`TP_PB0_*`）⇒ 悬空激励 + **对 DUT 引脚的非预期 5 V 偏置风险**；契约四处（`aliasesUsed=["sw2pgnd"]`、`relaySet` 无 109/110、`scopePins` 无 BST、`pinRouteTable` 无 BST 键）**独立排除 BST**；**推荐移除**（`t38` 已执行）。交付件 `t41-tm601-bst-path-determination.md` = 11,032 B / `24ba7b9060dc80477f15ec0ab63127ba846b13fd47435b9fe6abd3a7fc49d1d1`。**FACT/INFERENCE/UNKNOWN 分离；UNKNOWN 未写"已排除"。**
- **`t40`（rule-reviewer，独立、未采信 t39，verdict=pass）**：**TM601 不需要 BST、不应到达 BST，移除是唯一同时满足用户要求与最小端点纪律的处置**；现盘 TM601 段该激励调用 **= 0** ⇒ 无落点激励已清零。**Q1 分级**：FACT＝本项不再产生 PB0 意外驱动；INFERENCE（反事实）＝若恢复驱动且不闭 K110，5 V 落 `PB0_F_S1`（与 IR 的 accepted PB0 路径一致）；UNKNOWN＝① PB0 网外部占用/冲突 ② `ACM200_RELAY_ON` 仪器内部继电器行为 ③ K110 机械保持语义（型号 `IM06DJR` **未从器件手册确认** ⇒ 该机械语义降级为 INFERENCE/UNKNOWN，"未动作落 PB0"另有网表/IR/派生表**三条独立来源**支撑）。报告 `review/t40-tm601-bst-determination.md` = 12,133 B / `dd54fad38087abddb192d4a8e9bcae5840ac750b032e72732e8091487347a900`。**对现盘 39,457 B 的四条判据全部 PASS**（TM600 `L219` 9 项含 `K109`+`K110`；TM601 `L426` 8 项；两函数负列表命中 0；机制/locator 注释齐备；不变量全一致；`PMID_HG2` 10 V → `FXVIe_PLUS_20V`）。
- **canonical 定性（Captain）**：**canonical = `implementation-payload-TM600-TM601.cpp` / 39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` / mtime 19:55:59（python 明文）**；`38,147 / `272667f3…``（复核方 t29 verdict 对象）、`36,381 / `73b511b7…``、`35,014 / `444810dd…`` 为**过渡态、盘上无副本** ⇒ **其既往 verdict 不覆盖现盘**；`t39` 的证据取自契约/IR/网表/端子表、**不依赖旧字节** ⇒ 两结论**可合并**。
- **剩余唯一门 = `t42`（schematic-expert，在跑）**：`SW12_U1REF_BST_ACM` 的 ACM200 引脚归属 —— **pin 5**（宏 `S5_5` 一类 ⇒ `S5_ACM200_FH5/SH5`，`SCH:673` 经 K48/K76 → BST_F ⇒ 需 **`[48,76]`**、K110 非本路线必需）vs **pin 18**（⇒ 需 **`[110,61]`**，契约 ACM200 侧条目为漏项）。**对"TM601 移除"无影响**（两读法下 TM601 都到不了 BST：`48/76` 与 `109/110` 皆未闭）；**但若判 pin 5 ⇒ TM600 侧应闭集合可能为 `[48,76]`，而 TM600 SetOn 两者皆无 ⇒ 可能是另一处真缺陷**（届时另派任务）。
- **`t30` 连带后果（已要求加注）**：其期望集合含 `[110]`、**固化了 pin-18 前提** ⇒ 须在 `t30-summary.md` 写明推导来源与"ACCEPT 只覆盖『盲区已关闭』、不覆盖前提正确性"；若 `t42` 判 pin 5 ⇒ **另派任务**按路线修正/拆分断言（不得动 `gate_baseline.json`）。

**🔴 `t42` 判定完成（verdict=pass）—— 会改变验收结论：ACM200 引脚归属 = ch5 ⇒ 到 BST 需 `[48,76]`，K110 非本路线必需（20:4x）**
- **结论**：`SW12_U1REF_BST_ACM` 驱动 **ACM200 channel 5**（`S5_5` 族），**不是 pin 18** ⇒ 到 BST 必需集合 = **`[48,76]`**、**`K110` 非必需**；`K110_BST`/`K110_ACM18_BST` 属**另一台仪器 `PB0_BST_ACM`（ch18）**；与 SW 端 `K61_ACM8_SW` 合并后 **BST–SW 闭集 = `[48,61,76]`**。产物 `t42-acm200-pin-attribution.md` = 19,351 B / `8883daad0d22e669eeb1dd8038a3ad72591078413aed097473d33949300f4cfb`。
- **三方互证（各带 locator）**：① **宏语义实读**（`Pin_Channel_define.h:20` = `S5_5`；`:62 _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE1_` = `S5_0..S5_23` 恰 24 token；`:57` 分组；`:15-:38` 24 宏按通道序；`hardware-specs.md` ACM200 = 24 通道 ⇒ **站点后 token 即通道索引**）；② **`StdAfx.h` 第二绑定**（extern 顺序 `:64-:87` 与宏表一一对应；别名自带通道号：`K48_ACM5_AMP_REF`、`K61_ACM8_SW`、`K59_ACM7_SDA`、`K102_ACM15_PC3`、`K110_ACM18_BST`）；③ **权威网表**（`NetK46_BUS_FH_SW1_S1_2 = {K46.2, K48.6, S5_ACM200_FH5}` ⇒ ch5 在 K48 输入端；`NetK109_BUSL_PB0_S1_4 = {K109.4, K110.6, S5_ACM200_FH18}`）。
- **在役代码自证**：`test.cpp:7000/7087/7170/7513` 闭 `K48_ACM5_AMP_REF`+`K76_ACM_BST`，`:7598/:7621` 注释逐字写明与 `ACM200_FH5(SW12_U1REF_BST_ACM)` 共用接入 BST ⇒ **代码内确认 ch5**。**陷阱**：`SW12_U1REF_BST_ACM`/`PB0_BST_ACM` 与 `K76_ACM_BST`/`K110_ACM18_BST` 都含 "BST" ⇒ **按字符串匹配必然配错对**。
- **契约三处错项（已指认，契约未动）**：`resources[2].channelsInScope.BST = "S5_ACM200_FH18/SH18 (K110_BST)"`、`aliasResolution[3].resolution.relayChain[0].relay = K110_ACM18_BST`、`aliasFlatTable[3].relayPath = K110_ACM18_BST -> K61_ACM8_SW`；**内部一致性判据**：同一 `channelsInScope` 对 SW=FH8/INT=FH15/VDM=FH7 均符合"通道=宏通道"（分别吻合 `K61_ACM8_SW`/`K102_ACM15_PC3`/`K59_ACM7_SDA`），**唯 BST 破例** ⇒ 该三处为错。`alternatives[0]`（FH18 fallback）是**唯一** `[110,61]` 正确处；`legacyKMap.mapping[2]` 应记**三条腿**（FPVIe0-CH0-high `[46,48,76]` / ACM200 ch5 `[48,76]` / FPVIe 低域&ACM200 ch18 `[109,110]`）。
- **⚠ 对 t29 的直接后果（前提被推翻）**：交付件 TM600 SetOn 闭 `K109`+`K110`、**`K48/K76` 零命中** ⇒ **用 ch18 腿驱动 ch5 对象**；且 `K109` pins 3/6 = `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`，**把 FPVIe1 低域总线拉上 BST 节点**（新风险）。⇒ **"K110 必需"前提不成立；真缺陷是缺 `[48,76]`**（TM600 对 48/76 有契约授权）。现盘 `test.cpp:9081/9255` **两腿皆未闭**（无 BST 源腿）。
- **⚠ 连带更正（PB0 论断失效）**：`t39`/`t40` 的"5 V 落 `PB0_F_S1`"建立于 **ch18** 前提；按 ch5 ⇒ 未动作时经 **`K48(NC) -> K49 -> SW1_F/SW2_F`** 改道（`SCH:775/778`），**不是 PB0**。⇒ `t43` 须修订（**不改变**各自处置结论：TM601 无 BST 授权 ⇒ 移除正确）。
- **门禁侧**：`t30` 期望集含 `[110]`、**固化 pin-18 前提** ⇒ 已按要求加注（推导来源逐条 locator / 明写 pin-18 前提 / 声明"ACCEPT 只覆盖『盲区已关闭』，不覆盖前提正确性"）；`t42` 判 ch5 ⇒ **期望集须随 rev 25 改为 `[48,76]` 口径或按路线拆分（另派任务、不得动 `gate_baseline.json`）**。**新增脆弱点（已收档）**：期望集第二源 `usedByTm` 系**从散文用正则抽 TM 号**（`\b(TM\d+)\b`）⇒ 描述被改写会**静默改变期望集**；根治＝契约加结构化"别名→TM 归属"字段（并入 rev 25）。
- **⚠ `t40` v2 与 `t42` 正面冲突（由 `t43` 裁定，含循环禁令）**：`t40` v2（`review/t40-tm601-bst-determination.md` = 17,654 B / `20c56b4ce677d030eea5f357db9a7e1f072150459e1d140a0c911aeaf8cd8b89`，verdict 维持 pass）已按用户条款①重做为**四方并用可达性证明**（`FH18` 与 `K110.COM2` 同 net → 端子表 `6=COM2`、默认 6-7 通/通电 6-5 通 → 未动作落 `PB0_F_S1`；**只有 `K110` 置位才到 BST**；IR `required_on=[110]`），**即沿 ch18 论证**；而 `t42` 判定仪器实为 **ch5**（`[48,76]`）。**两者互斥、不可合并** ⇒ `t43` 须先裁"**仪器驱动 ch5 还是 ch18**"，判据按证据等级（宏语义实读 → `StdAfx.h` 别名通道号 → 权威网表 net 成员 → 在役代码 4 处 + `:7598/:7621` 注释），并**禁止循环**：**不得**以契约 `channelsInScope.BST="…FH18/SH18 (K110_BST)"` 或 `aliasResolution[3].relayChain` 作权威（**正是 `t42` 指认的错项**）。
- **✅ 双方收敛项（可直接进 rev 25）**：ACM200→BST **确有两条、分属不同引脚**（`FH18=[110]`、`FH5=[48,76]`），而契约 `pinRouteTable["BST"][".6: ACM200…"] needsClosed=[48,76]`（line 672）**只反映 FH5、未按引脚分列** ⇒ **真实契约缺陷**，与 `bst2sw.usedByTm`(TM1205)、`TM600.aliasesUsed` 漏 `bst2sw` **同根因（B-6）**；修法＝**按引脚/路线分列**。
- **PB0 风险定级（t39，blocking）**：反事实落点 `PB0_F_S1`/`PB0_S_S1` 为 **DUT 引脚（`MemberType=PORT`）**，同网含 `PWM1_*`/`TP_PB0_*`/`K147_PB0_OSC`/`S24_P10`/`R_PB0` ⇒ 不止"BST 未驱动"；`t38` 移除该驱动后风险消除（**双方一致：不得回退 t38**）。
- **✅ `t44` 补遗完成（t42 加固，结论不变）**：`t44-t42-addendum.md` = 16,257 B / `30aa1be601c058152688aa6d3def9e53e159898c7dce3a2035f9c0230f687a79`（侧车 `t44-t42-addendum-pin.json` + 生成器 `t44-pin-addendum.py`）；**t42 原文未改写**（仍 19,351 B / `8883daad…`）—— **刻意另立补遗以避免再制造哈希漂移**。**证据强度分级（诚实标注）**：**(1) 行为层（最强，新收录）**：**已执行**的人工调用点 `test.cpp:7000/7087/7170/7513` 闭 `K48_ACM5_AMP_REF`+`K76_ACM_BST`，`:6997/:7598/:7621` 注释把 `SW12_U1REF_BST_ACM` 与 `ACM200_FH5` 写在**同一句** ⇒ **不依赖 `S5_5` 解读、不依赖 `FH<n>` 编号、不依赖任何未使用宏**；**(2) 穷举（新）**：**全部 15 条**源归属 BST 的复合宏中，ACM200 归属仅 `K_BST_ACM=48,76`(:620) 与 `K_BST2_ACM=43`(:619)，**无一条含 K110**；含 K110 者为 `FPVIe[L]`(:451/:452)/`QVM[L]`(:557)；**(3) 主动降级**：`K_BST_ACM` 实测 **1 定义 / 0 调用点** ⇒ 属**意图/文档证据、非行为证据**，行为权重归 (1)；**(4) 控制组 5/5** ✓。
- **⚠ 口径更正（须同步 t29/t30/t34 叙述）**："TM600 现闭集含 `K109/K110`、无 `48/76`" **只对 payload 成立**：**payload** `L219`（`2d0984d9…`）含 `K109_BUSL1_PB0`+`K110_ACM18_BST`、无 48/76 ⇒ **闭错腿 + 漏闭**；**现盘部署态** `test.cpp:9081`（`15c7d2b8…`）**两腿皆不闭**（只闭 `K57_CAP_BST_SW` 自举电容继电器）⇒ **仅漏闭**。⇒ **`t30` 阳性对照在期望集改为 `[48,61,76]` 后仍报红，但归因由"缺 K110"改为"缺 48/76"**，描述须随之改；`t38`/TM601 两处皆不闭，与其移除 TM601 ACM 驱动的处置一致。
- **两处 UNKNOWN 交 `t43` 一并裁定**：① **TM600/TM601 是否必须由 ACM200 驱动 BST**（裁决 (ii) 称 rail 保持 `SW12_U1REF_BST_ACM` 形式，但**现盘未闭任何 BST 源腿**）；② **是否允许改用 `PB0_BST_ACM`(ch18)+`[110]`**。二者直接决定 **t29 的 `K109/K110` 去留**与 **rev 25 写法**。

- **`t33` 转 pass 的有序清单（compile-diagnostician，三分支）**：`gate-logs-t33/t33-transition-plan.md`（A：判 ch18 ⇒ 我 REPLACE → 其复算 `compiledRevision`（**不再沿用 `15c7d2b8…`**）→ 重跑门禁（期望仅 `bst-sw` 转绿）→ 我交回 `build.log`+0/0+DLL 哈希 → 其只改 `build-report.json` + 复跑 schema；B：判 ch5 ⇒ 先 rev 25 → 断言随契约更新并按新期望集重跑阳性/阴性 + 全树 A/B（另派任务、**不动基线**）；C：两路线并存 ⇒ 按路线拆分期望集）。**其会话只读 ⇒ 编译证据须标注"来源＝可写会话（Captain）"**。

- **待办门 = `t43`（rule-reviewer 独立复核 t42 + 裁定）**：① TM600 是否**必须**由 ch5 驱动 BST；② t29 的 `K109/K110` **保留（标依约保守）还是移除**；③ 是否允许改用 ch18+`[110]`（物理可达但**改变声明仪器**）；④ 契约三处错项指认是否成立。**`t43` 回收后**：rev 25（三处更正 + `closedRelayNumbersByRoute` 分列 + 三条登记待办 + TM601 段"无 BST 节点/路线" + 结构化别名字段）→ 若需 `[48,76]` 则另派 payload 任务 → 三门禁 → 独立复核 → **Captain REPLACE**。

**Ⓘ 危险项登记（20:7x 精化）**：部署态 TM600 **在调 ch5 源（`.Set` 10 次、非零 FV 7 次、阶梯 `0→5→10→15→20→15→10→5→0`、量程最高 `ACM200_40V`、末次 `RELAY_OFF`）的同时，其函数体内 `K46/K48/K49/K76/K109/K110` 命中全为 0** ⇒ ① `SCH:672`（BST 组头）**需闭 `K48,K76`、无默认导通路线** ⇒ **意图的 BST 轨无源**（`K57_CAP_BST_SW` 是自举电容继电器、**非源**）；② `SCH:774/775` —— `SW1 需闭合: 无(默认导通)`、`F: S5_ACM200_FH5 -> K48(NC) -> K49(NC) -> SW1_F` ⇒ **该 0–20 V 阶梯落在 `SW1_F/SW1_S`**，而 **`SW1` 不在 TM600 的 `scopePins` 内** ⇒ **越界驱动相节点**。⇒ 与 `T32-F1`（BST 闭合失败）、"缺 `[48,76]`"**是同一缺陷的三种表述**；**`K48` 是改道开关** ⇒ `[48,76]` **不是叠加式多闭**。**澄清（`schematic-expert`）**：**`SW1` 不是 `SW` 的 Kelvin 抽头，而是另一开关相节点**（`BST1/SW1`、`BST2/SW2` 各有独立自举电容继电器 `K45_Cap_SW1_BST1`/`K44_Cap_SW2_BST2`；`K49` 别名 `K49_ACM5_SW2` 同 ch5）⇒ **不是"同节点两源对拉"，而是"把相节点当 BST 驱动"**。**电性后果（20 V 落 SW1 对 DUT 是否致命）＝ UNKNOWN，须 owner/机台判定**；FACT/INFERENCE/UNKNOWN 已分级。
**Ⓙ 教训登记（`schematic-expert` 自查）**：**尾部注释块会骗过任何"最近前置 `DUT_API`"式的机械归属法** —— `L7598` 属 **TM641** 的函数头注释块（`L7590` 结束 TM640、`L7593` 起 `TM641: BUBO BST UV` 注释块、`L7606` 定义）⇒ **须先读注释块自称的 TM 名再归属**；其已撤回"`L7598` 为 TM600 缓解先例"的表述并更正计数（**TM640**：SW12 提及 7／非零 3／`K48`·`K76` 各 3；**TM641**：2／非零 0）。

**Ⓘb 新增专项判定（20:8x，会决定合并批可行性）**：`schematic-expert` 指出 **`K48` 是改道开关**（闭它把 ch5 由 `SW1` 移到 `K76→BST` 并断开默认 SW1 通路），而 **TM1205 的 `bst1_sw1`/`bst2_sw2` 变体行（契约 `aliasFlatTable[14]` kNumbers `[46,41]`、`[15]` `[46,49,41,43]`）用的正是同一 ch5 端点**（`K46`、`K49`、`K41`、`K43`；`K49` 别名 `K49_ACM5_SW2` 亦 ch5）⇒ **若冲突，计划中的 payload 改动（TM600 补 `K48/K76`）必须附带显式状态纪律**；另登记其观察 **`K110.pin4` 与 `K48` 两条腿汇合于 `K76.4` 节点**（是否产生互动属电气判定）。⇒ 已派 **`t47`**（schematic-expert）判定，含"各 TM 的 `cbite.SetOn` 是否为完整显式闭集、未列出件是否保持前项状态"这一必须回答的子问题。

**Ⓘc ch5 源的三目的地分区（FACT，`ate-implementer` 追加）**：`S5_ACM200_FH5` 在网表中**恰好三个目的地、由继电器状态分区 ⇒ 同一时刻只能去一个**：`SCH:673 K48(ON)+K76(ON) → BST_F`／`SCH:775 K48(NC)+K49(NC) → SW1_F`／`SCH:778 K48(NC)+K49(ON) → SW2_F` ⇒ **为修 TM600 而闭 `K48/K76`，必然把 ch5 从 `SW1/SW2` 取走**（"改道 ≠ 叠加"由此结构性证实）。**同线竞争者（六个在役函数同时使用该仪器并闭 `K48/K76`）**：`TM607_BUCK_LS_ZCD`、`TM608_BOOST_HS_ZCD`、`TM609_BOOST_HS_NEG`、`TM616_VC_OFFSET`、`TM640_BOOST_HS_OCP`、`TM641_BST_UV`；另 `aliasFlatTable[14] bst1_sw1`/`[15] bst2_sw2`（kNumbers `[46,41]`/`[46,49,41,43]`）共享 ch5 端点。⇒ **`t47` 范围已据此扩大**（须逐项给各函数对 ch5 端点的闭合状态 + 各 TM 的 `cbite.SetOn` 是否完整显式闭集〔未列出件是否保持前项状态〕+ 是否有冲突/是否需按项状态纪律）。**记账更正**：实现者自纠"TM600 非零 FV 9 次"实为 **7** 次（10 次 `.Set`：值 `[0,5,10,15,20,15,10,5,0,0]`，9 `RELAY_ON`／1 `RELAY_OFF`）—— 结论（源已被驱动）不变。

**当前盘面（对照用）**：部署态 `test.cpp` 仍 **469,714 B / `15c7d2b8…`（t23，`K109`/`K110` 命中 0）** ⇒ `DELIVERED ≠ DEPLOYED`；`build-report.json` = 13,075 B / `808abcc1…` **verdict=blocked**；`verification-report.json` = 27,473 B / `daba0578…` **verdict=fail**（T32-F1 blocker + F2/F3 high）；`acceptance-report.json` 未产出（t34 未开始）。**Release 编译由 Captain 在落盘后执行**（成员会话对目标树只读，MSBuild `MSB3491`）。

## ✅ 裁定生效清单（Captain，20:5x —— 全体请照此停止"待 Captain"循环）

1. **canonical 名义定性**：`implementation-payload-TM600-TM601.cpp` = **39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` / mtime 19:55:59（python 明文）**；`38,147/`272667f3…``、`36,381/`73b511b7…``、`35,014/`444810dd…`` 为**过渡态、无副本**，其既往 verdict **不覆盖现盘**。**三序并存告警至此结案**；`t39`/`t40`/`t42`/`t44` 四份结论**均以该字节为引用对象**（`t39` 为路径判定、无需字节声明）。
2. **落盘门**：**只差 `t43`**（`t39` ✅／`t40` ✅ pass／`t42` ✅ pass）。`t43` 回收后由我一次性下发定案批并 **REPLACE**。
3. **`t34` 口径**：**先出 blocked/fail 如实版**（必录：`T32-F1` **扩为两处部署态差异** —— 缺 `K109/K110` ／**仍带 TM601 无落点激励**；`F2/F3`；`DELIVERED≠DEPLOYED`；门禁双成因；**B-6 与 B-2 并列**；meta 重生成风险；耦合三条并列；`MSB3491`；编译≠电性；无机台验证）；**终稿**待落盘 + 我代跑编译 + `t33` 转 pass。**`t29` 的 `pass` 须分列归属**：只覆盖 **TM600 侧**补闭合；TM601 侧由 `t40` 覆盖。
4. **`t35` 路径 A = GO**，**执行在 `t43` 之后**；范围＝路线语义分列（ACM200 行**按引脚分列** `acm_5→[48,76]`／`acm_18→[110]`）+ **三条登记待办**（`TM600.aliasesUsed += bst2sw`；TM1205 移出 `bst2sw.usedByTm` 并建 BST1/BST2 独立别名；补 `TM1205.aliasesUsed`）+ **TM601 段显式登记"无 BST 节点/路线、不采用 ACM200 BST 驱动"** + **结构化"别名→TM 归属"字段**（替代散文正则抽 TM 号）+ `relays.md` L29/L31 状态方向**更正或加注** + 术语统一 `un-actuated/actuated` + 负列表规则写成"**不得加入 required-on、不得驱动其动作**"。
5. **plan 侧 pin**：**已授权写入 v21 数值**（`implementation-input-pin.json` = 10,134 B / `a9cf8b3c…`）；**`status` 保持 `NOT FINAL`** —— **FINAL 只由我复验时现算**，此点不因任何主张而变。
6. **`R1`（`run_gates.ps1:119` 正则）**：**本轮不派任务**（改它会作废 `t25` 已复核产物哈希；明细日志已足以定位）⇒ 登记为**残余改进项**，待验收闭环后再议。
7. **`manifest` / `reviewStatus`**：**manifest 按 role/revision 引用、不引哈希、不冻结**（活档）；`reviewStatus` 中"`t24` verdict 被 PARTIALLY WITHDRAWN（K109/K110 不在其覆盖内）"**保留、不回滚**。
8. **引用纪律（四条，全部生效）**：① 单一真源 `gate-logs-t28/t28-anchors.json`（**稳定引用锚点 = 剔除 `anchorsObservedAt` 行后的主体哈希**；消息只给「路径 + size」；值一律 python(rb) 现算）；② 内容键 **必须限定"去注释后可执行计数"** + **写明剥离方法**（`re.sub(r"//.*$","")`，去前导空白仍非空方计；行首剥离会把 `ERROR_RES` 算成 4）；③ **冻结声明只写「文件名 + 现算哈希 + 现算时刻」，尺寸与哈希同一命令取得**，**转述记忆值一律视为未验证**；④ **给出哈希即冻结**，若再写须交回新哈希并由复核方**对新字节重出 verdict**。
9. **`t28`/`t30` 收口**：以两份独立 ACCEPT 意见在台账收口；**`t41`**＝复核回填任务（owner=rule-reviewer，只出 verdict + 现算哈希，不重跑不改被审文件）。
10. **编译**：**由我在落盘后执行**（成员会话对目标树只读、`MSB3491`）⇒ 交回 `build.log` + **0 error / 0 warning 逐字** + `F12011.dll` 的 size/sha256/mtime，并标注"**证据来源＝可写会话（Captain）**"。

## 🔴 裁定更新（20:5x）：**合并为同一批落盘** + 部署态 TM600 **活危害**实测

**Ⓐ 落地时序裁定（选 (i)，取代"先落 `2d0984d9…` 再修"）**：**`t43` 回收后，把「契约 rev 25（ACM200 行按引脚分列 ⇒ 期望集合 `[48,61,76]`）+ payload 改动（TM600 闭 `K48`+`K76`(+`K61`)，并按 `t43` 裁定处置 `K109/K110`）」合并为**同一批**，然后**只重跑一次门禁**。**
- 判据：**(a)** 本 run 已反复因"证据与被审对象不属同一修订"付出代价（`T32-F2/F3`），带已知红落盘会重演；**(b)** TM600 的必需件本就是 `[48,76]`，payload 改动与契约 rev **本就同批**；**(c)** payload 只能有一套最终内容（`K109/K110` 去留待 `t43`）。
- **期望更新**：批处理完成后 **`bst-sw` 期望 GREEN**（修正期望集 `[48,61,76]` 将被满足）⇒ **不再存在"落盘后仍红"的例外路径**；其余 11 门不变；`cbit` 仍为基线豁免。
- **`compile-diagnostician` 的 ② 事实（确认）**：现行 TM600 SetOn 在**两套口径下都缺**（pin-18 缺 `[110]`、pin-5 缺 `[48,76]`）⇒ 单落 t29 只会把红从"缺 110"变成"缺 48/76"。
- **好消息**：`verify_bst_sw_sequence.py` **无任何具体 K 号字面量** ⇒ **契约 rev 后断言自动更新、脚本无需改动**（"契约驱动"设计价值已实测）。

**Ⓑ Captain 独立实测（部署态，python 明文；推翻全队共同假设）**：`ForCodexDebug/source/test.cpp` = **469,714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**；**TM600 段(8880-9215)：`SW12_U1REF_BST_ACM` 引用 11 / `.Set` 调用 10（含 `FV 0/5/10/15/20` 与回落 `15/10/5`，全部 `ACM200_RELAY_ON`），而该段 `K48`/`K76`/`K109`/`K110` 命中均为 0**；**TM601 段(9217-9399)：`.Set` 调用 3（`9269 FV5 RELAY_ON`／`9338` 归零／`9344 RELAY_OFF`），四继电器命中均 0**。
- ⇒ **部署态 TM600 在"驱动 ch5 源"的同时 `K48` 未闭** ⇒ 按 `t44` 的改道机制（`L774/L775` `SW1 需闭合: 无(默认导通)`；`K48` 默认 `NO(2/7)` 去 `SW1/SW2`）**源被送到 `SW1_F/SW2_F`**（**非 BST、也非 PB0**）⇒ **不是"少一个闭合"，而是**活危害（源被改道）**。**`K48` 是改道开关 ⇒ `[48,76]` 不是叠加式多闭。**
- ⇒ 此前 `t39`/`t40` 的"未动作 ⇒ 源落 `PB0`"**只对 ch18 腿成立**；部署态 TM600 的实际落点是 **`SW1/SW2`**。**`schematic-expert` 的 UNKNOWN ①（部署态 TM600 是否启用该源输出）就此解决：已启用 ⇒ 活危害**。
- **由此进一步支持 ch5**：部署态在役代码对**同一仪器**跑 10 次 ch5 阶梯（与 `t44` 行为层一致）；**ch18 腿无一处被 TM600 使用**。

**Ⓒ 已派 `t45`**（schematic-expert）：把 **`L672` 的章节归属**（落在 **`L662: ## 列6: ACM200 → PIN (Share继电器)`** 节内 ⇒ **ACM200 列自己的组头**即写 `需闭合: K48,K76`、无 `K109/K110`，强于 `L673/L674` 与 `K_BST_ACM` 复合宏）+ 三项新旁证（`L461/462`、`L536/537`、**`L538/539` 证明 `K109/K110` 腿服务 FPVIe[L]/QVM[L]**）+ **`K48` 改道机制逐脚闭环** + **Ⓑ 实测**，落成产物供 `t43` 引用。

**Ⓓ `t43` 现在须一并处理（我已在裁定要求中下发）**：① ch5 vs ch18；② `K109/K110` 去留（若 `B=remove ∧ A=ch18` ⇒ 须配"停 ACM 驱动"或"契约声明非必需"，否则重造 `t38` 型"有激励无落点"缺陷）；③ 是否允许改用 ch18+`[110]`；④ 确认 `rev 25` 先于 payload；**并须解释**：若判 ch18，则部署态 TM600 的 10 次 ch5 驱动与 `K110` 腿**互不匹配**（源在 ch5、闭的是 ch18 腿）这一矛盾。

## ✅ 定案（20:6x）：**ch5 成立 ⇒ TM600 须闭 `[48,76]`、移除 `K109/K110`**；少数派立场赖以为据的映射**已被其作者撤回**

**Ⓔ 判据：六条独立证据同向 + 少数派唯一权威被作者撤回**
1. **宏表原文**（Captain 实测）：`Pin_Channel_define.h:20 _PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,…"`（ch5）与 `:33 _PIN_CHANNEL_DEFINE_PB0_BST_ACM_ = "S5_18,…"`（ch18）**是两台不同仪器**；`StdAfx.h`：`K48_ACM5_AMP_REF=48`、`K49_ACM5_SW2=49`（ch5）、`K110_ACM18_BST=110`（ch18）。
2. **代码调用实测**：`test.cpp` 全树 `SW12_U1REF_BST_ACM` 47 次、`PB0_BST_ACM` 21 次（两台都在）；**TM600 段(8880-9215) 只调 `SW12_U1REF_BST_ACM`（10 次 `.Set`，全 `RELAY_ON`），不调 `PB0_BST_ACM`**。
3. **行为层**（`t42`/`t44`）：部署态 `test.cpp:7000/7087/7170/7513` 对本仪器闭 **`K48_ACM5_AMP_REF`+`K76_ACM_BST`**，`:6997/:7598/:7621` 注释写 `(FH5→BST)`。
4. **复合宏穷举**（`t44`）：唯一 `ACM200[] -> BST` = `K_BST_ACM = 48,76`（`:620`），15 条中**无一条含 K110**。
5. **控制组 5/5 + 决定性分离**：`t42`、`compile-diagnostician`（独立，自纠列名后一致）；ch5 网 `{K46.2,K48.6,S5_ACM200_FH5}` 不含 K110、ch18 网 `{K109.4,K110.6,S5_ACM200_FH18}` 不含 K48/K76。
6. **契约 owner 自撤回**：`setup-architect` 撤回"K110 必需"，声明 **`aliasResolution[bst2sw]=[110,61]`／`relayChain=[K110_ACM18_BST,…]` 是它自己取用通道 18 派生表行造成的映射错误** ⇒ **少数派（ch18）唯一权威已被其作者撤回**；其"宏索引≠引脚号"的反驳被 `Pin_Channel_define.h` 原文排除（两台仪器各占一个通道）。

**Ⓕ Captain 据此裁定（三项）**
- **(i) 采信 ch5**；
- **(ii) payload 合并批**：TM600 的 SetOn **补 `K48_ACM5_AMP_REF`+`K76_ACM_BST`**（SW 侧核 `K60/K61` 是否足够），并**移除 `K109/K110`** —— 判据：rev 25 更正映射后"依约保守"的**字节基础消失**，且保留会把 **`FPVIe1_FL/SL_BUS_S1` 低域总线**与 **ch18 源脚**耦合到 BST（`t42`/`schematic-expert` 论证；实现者已让步接受）；
- **(iii) rev 25 增补**：`bst2sw` 映射更正（BST 侧 `[48,76]`）＋ **通道 18 路线单列**（`PB0_BST_ACM`/`K110_ACM18_BST`）＋ **`aliasResolution` 的 ACM200 行按通道分列** ＋ **`t30` 期望依据更正为 `[48,61,76]`** ＋ **TM1205 移出 `bst2sw.usedByTm`、落到 `bst1_sw1`/`bst2_sw2` 变体条目**（其部署态走 `K_FPVIH_TO_SW1_A`+`K_FPVIL_TO_BST1_A` 等变体行，不含 `K110/K61`）。
- **执行序**：**rev 25 先于 payload，同批落盘，只重跑一次门禁** ⇒ 期望 **`bst-sw` = GREEN**（因 payload 同批补 `K48/K76`）；**不存在"落盘后仍红"的例外路径**；`t34` 不得建立在"t29 落盘即绿"之上。
- **`t35` I.2 须更正**：原"落盘后 `bst-sw` 转绿"**只在 rev 24 口径成立** ⇒ 须写明**两口径各自的预期**（`compile-diagnostician` 已否证原始写法）。

**Ⓖ `t43` 待输出（我已给二选一，不得两者皆无）**：**(甲)** 结案并采纳 ch5 + **逐条 accept/reject `t42` 四层证据**；**(乙)** 坚持 ch18 并给出**新的独立依据**（不得再用已被作者撤回的映射），并**明确写出两方分歧与各自 locator、声明"分歧未解、不建议按任一方单独施工"**（**我折中**，届时据并列结论上报用户裁定）。

**Ⓗ 本轮另立两个补遗**：`t45`＝`L672` 属 **`L662: ## 列6: ACM200 → PIN (Share继电器)` 组头自证** + `K48` 改道机制 + Captain 部署态实测；`t46`＝期望集合与时序三口径（**TM600 仍缺 `[48,76]`**；**TM601 不受 `bst2sw` 约束**〔否则假红且与 `t38` 移除方向相反〕；**TM1205 期望取变体行**）+ 断言并集设计说明。
**Ⓘ 危险项登记**：部署态 TM600 **在调 ch5 源（10 次 `RELAY_ON`）的同时 `K48/K76/K109/K110` 全为 0 命中** ⇒ 源经 `K48` 默认路径改道至 **`SW1/SW2`**（非 BST、也非 PB0）⇒ **活危害（源被改道）**；`K48` 是**改道开关** ⇒ `[48,76]` **不是叠加式多闭**。

## 🔴 计数陷阱（20:9x，第 5 条引用纪律；由 `schematic-expert` 发现，Captain 已复算自纠）

**Ⓐ 陷阱本体**：**`\bK48\b` 匹配不到 `K48_ACM5_AMP_REF`** —— `_` 是 word 字符 ⇒ `48` 与 `_` 之间**无词边界** ⇒ **凡以别名形式出现的继电器在 word-boundary 检索下被系统性漏计**（只剩注释里的斜杠形式）。同理适用于 `K110_ACM18_BST`、`K76_ACM_BST`、`K61_ACM8_SW` 等**全部带后缀的别名**。**镜像情形（`ate-implementer` 自查）**：**按 `K48`/`K76` 做文本扫描，看不到复合宏形式** —— `TM641@L7623` 与 `TM643@L7734` 是经 **`K_FPVIH_TO_BST_A`（=46,48,76）** 闭腿的，**用 `K48` 搜根本不会命中** ⇒ 它据此误报"碰撞集 6 个（含 `TM616`）"。**通用形式＝"文本扫描不是归属判据；正则可能漏掉该量实际出现的形式"**（两侧各踩一次：`\bK48\b` 漏别名；`K48` 文本漏复合宏）。⇒ **`t47`/`t48` 须按此写规矩**：**brace-depth 定界 + 计数须覆盖别名与复合宏形式 + 每次标注范围（函数体 vs 文件级）**。
**Ⓑ 因此每条计数必须写明三件事**：**(a)** 检索方式（**substring** 还是 **word-boundary 正则**；**推荐 substring 或显式别名清单**）；**(b)** **范围**（全文件／函数体，且**必须写明定界方法**）；**(c)** **剥离方法**（见 ②b）。**"通常相等"或"未写明范围"的计数一律不得作为判据**（本 run 已多次因此产生假值/假通过）。
**Ⓒ 归属定界方法（已三次被证伪，禁止使用）**：**"最近前置 `DUT_API`"不可用于函数体归属** —— 本文件已三次踩坑（`L7598`→TM641、`L7500`→TM640、`L7503-7606` 范围污染）。**正确方法＝brace-depth**：函数体 = `DUT_API` 行 → 之后**首个列 0 的 `}`**；**紧邻声明前的注释块归下一个函数**（须先读注释块自称的 TM 名）。
**Ⓓ Captain 复算（纠正方法后，结论不变）**：部署态 `test.cpp`（469,714 B / `15c7d2b8…`）——
- **TM600 段 L9057-9216**：`K48`/`K76`/`K109`/`K110`/`K46`/`K49` **substring 与 word-boundary 均为 0**；`SW12_U1REF_BST_ACM` = **10**；**`SetOn`（L9081）= `K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`** ⇒ **无任何形式的 `K48/K76`（亦无 `K109/K110`）** ⇒ 先前结论**成立**。
- **TM601 段 L9217-9353（brace-depth）**：`K48`/`K76`/`K109`/`K110` = **0**（`K46`/`K49` 各 1，均在注释）；`SW12_U1REF_BST_ACM` = **3**（`L9269` 非零 `FV 5`、`L9338` 归零、`L9344` `RELAY_OFF`）；**`SetOn`（L9255）= `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`** ⇒ **驱动了源却无一条路由继电器** ⇒ **独立交叉佐证 `t33` 阻塞项**（"`t29`/`t38` 产物未应用于目标树"）；**边界**：只说明部署树滞后于 payload，**不反推 `t38` 失败**。
**Ⓔ 碰撞集更正（`schematic-expert` brace-depth 定界）**：**驱动该仪器且闭 `K48/K76` 腿的函数 = 5**：`TM607`/`TM608`/`TM609`/`TM640`/`TM641`（**`TM616` 应剔除** —— 其真体 L7411-7488 内命中 0；诱人的 `L7500` 属 **TM640** 头注释块）；**闭腿者共 6**（`TM607/608/609/640` 显式别名 + `TM641/643` 经 `K_FPVIH_TO_BST_A`）；**`TM643` 闭腿但不驱动仪器 = 正确形态**（ACM 源应保持 OFF）。文件级含 `K48_ACM5_AMP_REF` 的 `SetOn` 行 = **4**（L7000/L7087/L7170/L7513；TM640 内为 **1**）⇒ **两个数字各属不同范围，引用须带范围前缀**。

## 🟥🟢 定案依据之三（20:9x，迄今最硬）：**`[110,61]` 是"跨族混合对"，在任何读法下都不成立**

**Ⓐ 宏分族证据（`StdAfx.h`，`test-strategy-architect` 独立核出；Captain 确认可复算）**
```
L620 K_BST_ACM        = 48,76    // ACM200[] -> BST : K48_ACM5_AMP_REF + K76_ACM_BST
L638 K_SW_ACM         = 61       // ACM200[] -> SW  : K61_ACM8_SW
L452 K_FPVIL_TO_BST_B = 109,110  // FPVIe[L] -> BST : K109_BUSL1_PB0 + K110_ACM18_BST
L490 K_FPVIL_TO_SW_A  = 60,61    // FPVIe[L] -> SW  : K60_BUSL0_VCP + K61_ACM8_SW
（对照：L377 K_FPVIH_TO_BST_A 46,48,76；L514 K_BST_QTMU 141,46,48,76；L451 K_FPVIL_TO_BST_A 109,110,138,139,145,146）
```
⇒ **自洽解只有两个**：**(a) ACM200 族 = BST `{48,76}` + SW `{61}` ⇒ `[48,61,76]`**（与 `t42`、仪器宏 `S5_5`〔通道 5〕、继电器命名 `K48_ACM5`〔通道 5〕、**已部署实现**四者一致）；**(b) FPVIe[L] 族 = BST `{109,110}` + SW `{60,61}`**。**`[110,61]` = `110`（FPVIe[L]→BST 族）+ `61`（ACM200→SW 族）＝ 跨族混合，不属于任何自洽解** ⇒ **该结论独立于引脚之争**。
**Ⓑ 契约侧的额外薄弱点**：`aliasResolution[bst2sw].resolution` 的 **`relayChainHigh`/`relayChainLow` 均为 `null`** ⇒ **该对没有继电器链推导**（同文件 `pmid2sw` 有链），其来源是**裁定 (ii) 的文字**而非电路推导 ⇒ 进一步削弱"以该字段为 BST 侧依据"的论证（该字段作者已撤回其为"取错通道"，且该对本身**无推导**）。

**Ⓒ 由此产生的三处口径更正（Captain 裁定）**
1. **`t29` 的 `pass` 需加范围限定**：**只对 rev 24 那个（已被证明跨族混合的）字面集合成立**；**它既闭了跨族对、又漏闭 `[48,76]`** ⇒ 统一表述为"**依（待更正的）契约字面合规，但该字面本身跨族无效；且漏闭 ACM200 族必需件**"；**`K109/K110` 仍判移除**（"依约保守"的字节基础随 rev 25 消失）。
2. **`t30` 期望集**：现期望里的 `110` **全部来自错误字段** ⇒ 随 **rev 25** 改为 **TM600 闭 `[48,76]`（+SW `[61]`）⇒ 期望 `[48,61,76]`**；其"阳性对照"是"按**错误集合**报红"。
3. **计划 `v22` 已授权**（`test-strategy-architect`）：**唯一变更**＝把继承自裁定 (ii) 文字的 **`[110,61]` 更正为 `[48,61,76]`**；**不删原文**（标 superseded）、增 `revisionHistory` v22 条目并写明理由（跨族混合 + `StdAfx.h` 四行为据 + 契约该对 `relayChainHigh/Low = null` 无推导）、双次生成逐字节一致 + `validate` exit 0 + **广播新 revision 与现算哈希**；随后由 `setup-architect` 同步刷新 `implementation-input-pin.json` 的 plan 行（`status` 仍 `NOT FINAL`）。
**Ⓓ `t43` 须据此结案**：**(甲)** 采纳 ACM200 族 `[48,61,76]` ＋逐条 accept/reject `t42` 四层证据；**(乙)** 坚持 `[110,61]` ⇒ 须正面回答 (i) 如何解释它是跨族混合而非任一自洽解、(ii) 为何在 `relayChainHigh/Low` 双 `null` 下仍以该字段为准、(iii) 为何网表 `S5_ACM200_FH5` 恰落在 `K48`（ACM5）网上。**仍坚持则并列分歧与 locator ⇒ 上报用户裁定（不折中）。** rev 25 另须**补齐或标注"无推导"**。

## 🟢 定案依据之四（20:9x）：**跨域复合** ⇒ 闭集 = **`[48,60,61,76]`**；**TM600 的缺口只有 BST 侧 `[48,76]`**

**Ⓐ 仪器是跨域复合（`test-strategy-architect` 提出，Captain 采纳并更正自身表述）**：`SW12_U1REF_BST_ACM` 这一对是**跨域复合**——**BST 侧取 ACM200 族 `{48,76}`**（`StdAfx.h:620 K_BST_ACM`）、**SW 侧取 FPVIe[L] 族 `{60,61}`**（`:490 K_FPVIL_TO_SW_A`；仪器名自身即表达此意）⇒ **权威闭集 = `[48,60,61,76]`**（**Captain 先前给的 `[48,61,76]` 漏了 SW 侧 `K60`，此处更正**）。
**Ⓑ 最强判据（可执行既成事实）**：部署态 `test.cpp` **`L6997` 注释 + `L7000/L7085/L7087/L7170/L7513`** 的五处 `SetOn` 对本案仪器闭的正是 **`K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST`**；配套 `SCH:672-674`（ACM200 列组头 `需闭合: K48,K76`、源 `S5_ACM200_FH5`）vs `SCH:42/L268`（含 `K109/K110` 的两行**起点均为 `S1_FPVIE_FL*`**）⇒ **`K109/K110` 的行属 FPVIe，不属 ACM200**。
**Ⓒ `T32-F1` / `t34` 缺陷表述更正（避免验收报告写错缺陷名）**：**不得**以"缺 `K109/K110`"作为 TM600 的缺陷；**正确表述**＝"**部署态 TM600 的 `SetOn`（`L9081` = `K83,K60,K61,K13,K85,K57,K126`）未闭 BST 侧 `K48/K76`，而其又驱动 ch5 源（10 次 `.Set`、非零 **7**）⇒ 激励未接 BST、**改道至 `SW1_F/SW1_S`**（`SW1` 不在 `scopePins` 内）**"。**按函数区分**：`TM607/608/609/640` 已闭 `K48/K76`，**仅 `TM600`/`TM601` 未闭** ⇒ **不得写成"部署版已满足 `[48,76]`"**。
**Ⓓ `t29` 的口径**：其 `pass` **仅对 rev 24 那个跨族无效的字面集合成立**；**它闭错 BST 侧族（`109/110`）且漏闭 `[48,76]`** ⇒ 表述＝"依（待更正的）契约字面合规，但该字面 BST 半边错误、且漏闭 BST 侧必需件"。**`K109/K110` 判移除**不变。
**Ⓔ 计划 `v22` 目标更正**：由 `[110,61]` 改为 **`[48,60,61,76]`**，并**分两侧写明**（BST `[48,76]` ∈ ACM200／SW `[60,61]` ∈ FPVIe[L]）；理由引 `StdAfx.h` `L620/L638/L452/L490` + 部署代码五处 + `SCH:672-674` vs `SCH:42/L268`。
**Ⓕ `t30` 期望集三种情形（最终口径）**：**rev 24 + 落 t29** ⇒ GREEN（原预期；但该字段跨族无效）；**rev 25 而 payload 未同批** ⇒ 仍 NEW-RED（第二处真缺陷）；**rev 25 + payload 同批（本 run 实际分支）** ⇒ **期望 GREEN**，**不存在"落盘后仍红"的例外路径**。

## 🔎 路线精度更正（20:9x，`ate-implementer` 复核 `test-strategy-architect` 的 locator）

**Ⓐ `[109,110]` 的路由有**三条不同**行，不可混引**：
```
L43    完整 CH0 链：S1_FPVIe_FL0 -> K89 -> K145 -> K146 -> K109 -> K110 -> BST_F   ← 若当作"canonical [109,110] 语句"，会连带要求 K145/K146
L268-269 最短 CH1 链：CH1 Low -> BST 需闭合 K109,K110；S1_FPVIe_FL1 -> K133(NC) -> K109(ON) -> K110(ON) -> BST_F   ← 体现最小对
L672-674 ACM200 路线：BST [Kelvin] 需闭合 K48,K76；F: S5_ACM200_FH5 -> K48(ON) -> K76(ON) -> BST_F（S 侧同）
```
⇒ **所有 `[109,110]` 路线的起点均为 `S1_FPVIe_FL*` 引脚，无一条起于 `S5_ACM200_*`** ⇒ 与契约 `aliasResolution[3]` 把 `[110,61]` 标为"ACM200 S5_FH18 → BST"的说法**相矛盾**（**每一个列出它的网表行**都反证该标注）。
**Ⓑ 另**：`K48/K76` 的**在役可用范式**已存在 —— **`TM643` 闭 `48/76` 而不驱动仪器**、**`TM641` 闭该腿且零次提及仪器** ⇒ 树内已有"**用该腿但把 ACM 源保持 OFF**"的**正确范例**（`TM600` 的修法应照此模仿，而非仅仅"补两个继电器"）。

## 📌 `t45`/`t46` 完成与数字定案（20:9x，`schematic-expert`；含更正 Captain）

- **交付件**：`t45-l672-section-evidence.md` = **14,784 B / `4d8940341f3cb1d28e9d6c03468edd084acdca58127e2817a489062d5f14630b`**；`t45-t42-timing-addendum.md` = **8,978 B / `5e5bde376e3634e6cb0567832765508277a8c83e0f7f4869e2e94a6a3c92e27a`**。
- **`t45` 核心**：`L672` 落在 **`L662: ## 列6: ACM200 → PIN (Share继电器)`** 节内（下节 `L803`）⇒ **ACM200 列自己的组头**即写 `需闭合: K48,K76`、源 `S5_ACM200_FH5`、**无 `K109/K110`**；**`L675 BST1 需闭合: 无(默认导通)`** 反证 **BST 无默认导通路线**；`L538/539` 证明 `K109/K110` 腿服务 **FPVIe[L]/QVM[L]**；`K48` 改道逐脚闭环（`K48` pin4/5 = `K76` COM pin3/6；`K76` pin4/5 = BST 节点/自举电容节点；`K49` pin7=SW1、pin5=SW2）。
- **数字定案（含更正 Captain 与实现者）**：**碰撞集 = 4**（`TM607`/`TM608`/`TM609`/`TM640`）；**`TM641`/`TM643` 各 0 次 `.Set`** ⇒ "**闭腿但不驱动**"＝**正确形态**；**`TM616` 剔除**（真体 `L7411-7488` 命中 0，诱因 `L7500` 属 `TM640` 头注释块）；**TM600** `.Set` 10 = 9 `RELAY_ON` + 1 `RELAY_OFF`（末次 `L9194`）、非零 **7**；**TM640**（体 `L7503-7590`）提及 **6**、非零 **3**、`K48`/`K76` token **各 2**、闭腿 `SetOn` **1**；**TM641** 提及 **1**（`L7621` 注释、`.Set` 0）。
- **`t46` 三口径表（`t33`/`t34` 排时序依据）**：
  | TM | rev24 期望 | rev25 修正后 | 部署态实际 | 今日 | 修正后 | 应做动作 |
  |---|---|---|---|---|---|---|
  | **TM600** | `{60,61,83,110}` | **`{48,60,61,76,83}`** | `{13,57,60,61,83,85,126}` | 红（缺 110） | **仍红（缺 `48,76`）** | **真修＝闭 `[48,76]`，非 `K109/K110`** |
  | **TM601** | `{154,155,60,61}` | 不变 | `{13,57,60,61,85,126,154,155}` | **绿** | **绿** | **无——不得补 `48/76`** |
  | **TM1205** | `{110,61}`（误用） | 变体 `[46,41]`+`[46,49,41,43]` | `{13,65,46,41,49,43}` | 红（**假红**） | 变体口径下**绿** | 契约须把 TM1205 绑到变体行 |
  ⇒ **`t30` 对 TM600 的期望值 = `{48,60,61,76,83}`**（三源并集：`pmid2sw` 给 `83/60/61`、修正后的 `bst2sw` 给 `48/76`）——**Captain 先前给的 `[48,60,61,76]` 是 BST–SW 对的并集，此处补全 `83`**。
  ⇒ **`verify_bst_sw_sequence.py` 三源并集设计正确且必要**（仅用 `aliasesUsed` 会跳过 TM600 的 BST 腿）；**两处假红源于契约数据、非脚本设计**；**脚本无该腿硬编码 K 号 ⇒ rev 25 后自动更新，不必改脚本**（**不派门禁脚本任务**）。
- **答 `t45`/`t46` 提出三问（Captain 裁定）**：**①** TM600 **必须**由 ACM200 驱动 BST（基线声明 + TM600 驱动 ch5 仪器）⇒ 闭 BST 侧 `[48,76]`、移除 `K109/K110`；**TM601 否**（`t38` 移除成立、**不得**补 `48/76`）。**②** **不允许**改用 `PB0_BST_ACM`(ch18)+`[110]`（会**改变声明仪器**）；ch18 数据保留并单列。**③** rev 25 三处归口 + **TM1205 绑变体行** + `alternatives[0]` 保留为唯一 `[110,61]` 正确处但须加 `PB0_BST_ACM` 消歧 + `legacyKMap.mapping[2]` **补第三条腿（ACM200 ch5 `[48,76]`）**。
- **`t41` 现冻结值**：**34,850 B / `b0ff71b752e5997a8a16829cde2cbbdb774eab1feeff3d6ddc4467841b9100b7`**（新增 **G.3 机制更正（待 t43）**：ch5 未动作时经 `K48(NC)→K49→SW1_F/SW2_F`，**不是 PB0**；§H.2/§H.3/§5 机制叙述**以"待 t43 修订"状态引用**；`t39` 处置结论已关闭不受影响）。
- **rev 25 五处实测确认存在**（`setup-architect` 逐条）：`channelsInScope.BST="S5_ACM200_FH18/SH18 (K110_BST)"`／`aliasResolution[3].relayChain[0].relay="K110_ACM18_BST"`／`aliasFlatTable[3].relayPath="K110_ACM18_BST -> K61_ACM8_SW"`／`alternatives[0]`（唯一 `[110,61]` 正确处）／`legacyKMap.mapping[2]` **只记两条腿、缺 ACM200 ch5 这第三条腿**（新增项）。

## ✅ 门已关闭（20:5x）：`t43` 完成 ⇒ 批处理执行中（`t49`/`t50`/`t51`）

**Ⓐ 门序（权威口径，终结所有分歧）**：`t39` ✅ → `t40` ✅（终稿 `37430005…`）→ `t42` ✅（pass）→ `t44` ✅（补遗）→ **`t43` ✅ 完成**（`review/t43-t42-review-and-unknown-ruling.md` = 7,439 B / `d4c3835437a41c9f1bee7b15c2d381da69c99ceacd0503f5f6dbb0f1023e90a7`，判 **ch5/ch18 = UNKNOWN（可约束）**）⇒ **"待门"状态结束**；任何仍写 `BLOCKED pending t40+t42` 的产物（如 `review-handoff-note-plan-side.md`）**视为已取代**，**不得用作调度依据**（已两次下达定点更正令；台账级以此为准）。
**Ⓑ `t47` 完成（决定性）**：**`cbite.SetOn` 是排他操作**（`knowledge/sources/cbite-qtmue.md:92-96`，用户 2026-08-09 纠正；`:87-89`、`:93`）⇒ **每个函数的 SetOn 即该项完整显式闭集**，**跨项状态泄漏不存在** ⇒ **"同线竞争者"不构成冲突**、**TM600 的 `K48/K76` 闭包可孤立实施**、**无需任何新的逐项状态机制**。产物 `t47-ch5-endpoint-sharing.md` = 14,019 B / `81f14d0a82c2543982d407e56634fe71652ef3019309ab21abca15c4def28b96`。
**Ⓒ payload 改动三条硬约束（已下发 `t50`）**：**(1)** **必须在 `L9081` 的同一次 `SetOn` 内追加** `K48_ACM5_AMP_REF`+`K76_ACM_BST` —— **不得另起第二次 `SetOn`**（`:92-93` 拆分陷阱）；**(2)** **不得追加 `K46`**（挂在 ch5 节点 `NetK46_BUS_FH_SW1_S1_2`，会把 FPVIe0 高侧 BUS 接上 BST 节点；那是 TM641/643 的形态，**TM600 不要**）；**(3)** **`K49`/`K110` 无需显式约束**（排他性释放 + pin 级已证 `K49` 无法影响 ch5 目的地）。**本轮保留 `K109/K110`**（删除在 ch18 下不安全 ⇒ 推迟另行裁定），登记其耦合代价；**`--check-extra` 不得启用**；`L416-420` 改为操作事实。
**Ⓓ 名单与计数最终版（作废此前所有 circulated 值）**：**既驱动又闭腿 = 4**（`TM607/608/609/640`）；**`TM641`/`TM643` 闭腿但 `.Set` 0 次**（"关源闭腿"的正确形态之一）；**`TM616` 两集合皆不属**；**`K41`/`K43` 非 ch5 端点**（属 FPVIe[L]→BST1/BST2；变体行与 ch5 真正共享的只有 `K46`、`K49`）；**TM640** body `L7503-7590`：提及 6／非零 3／token 各 2／闭腿 SetOn 1；**TM600** `.Set` **10 = 9 `RELAY_ON` + 1 `RELAY_OFF`（`L9194`）、非零 7**；**计数正则须别名包含式** `K48(?![0-9])`（`\bK48\b` 漏 `K48_ACM5_AMP_REF`）。
**Ⓔ 三条执行任务**：`t49`（契约 rev 25，**只增不翻**：新增 ch5 路线 `[48,76]`+`[60,61]`、ch18 单列 `PB0_BST_ACM`、按通道分列、既有 `[110,61]` 标 `contested` 并说明"无推导"、三条登记待办、TM601"无 BST 轨道"、结构化别名归属、`relays.md` **术语消歧**〔不宣称其自相矛盾——`setup-architect` 实测表/口诀/警示三者一致〕）／`t50`（payload 交集修正）／`t51`（计划 v22，**只增不翻**）。**其后**：payload 独立复核 → **Captain REPLACE** → 门禁前后快照 → **Captain 代跑 Release 编译** → `t33` 转 pass → `t34` 终稿。

## 🚀 `t50` 完成：payload 已按交集修正（21:0x）—— 待独立复核 `t52` 后由 Captain REPLACE

**Ⓐ payload 现值**：`implementation-payload-TM600-TM601.cpp` = **40,658 B / `5a668fe69929014f1dc5137be7fcabd4b898c862610b89f0183c73c7aff2a0f8`**（由 `39,457 B / `2d0984d9…`` 推进；`2d0984d9…` 自此为**历史值**）。
**Ⓑ TM600 的 SetOn（同一次调用，已核实体内 SetOn 恰好 1 次）**：`K83, K60, K61, K48_ACM5_AMP_REF, K76_ACM_BST, K109, K110, K13, K85, K57, K126` ⇒ **三条硬约束全部满足**：**(1)** `K48`/`K76` 在**同一次**调用内追加（**无第二次调用** ⇒ 未触发 `cbite-qtmue.md:92-93` 释放陷阱）；**(2)** **`K46` 可执行命中 = 0**（理由已写入注释：K46 属 FPVIe0 高侧 BUS 路径＝TM641/TM643 形态，非 ACM200 ch5 源路径）；**(3)** `K49`/`K110` 未显式约束（K49 默认投在 K48 动作后断开、K110 由排他性释放）。
**Ⓒ 不变量（剥离后可执行）**：`delay_ms(1)`6／`delay_ms(2)`0／`SetClamp(50,50)`2／`MeasureVI(200,5,FPVIe_MV_X10)`2／裸 `126`0／`K126_V1P5_CAP`2／`ERROR_RES`2／`K57_CAP_BST_SW`2／`K109`1／`K110`1／**`K48`1／`K76`1／`K46`0**；BOM+CRLF、0 lone LF。
**Ⓓ 门禁（沙箱副本 475,281 B / `178e4044d6d691a99420bd10202ab9c9a0e618042c29e2557a25a5f7db5742d1`，目标树未动）**：**`relay-trace` PASSED exit 0**（`FR-001` 反向 2；完整告警**仅 TM643 两条**；**无 TM600/TM601 finding**）；**`bst-sw` PASSED exit 0**（`targets=4 FAIL=0`）；**`awg` PASSED exit 0**（`FAIL=0 WARN=0`）⇒ **新增红 0**。
**Ⓔ `cbite.SetOn` 排他性逐字确认（`knowledge/sources/cbite-qtmue.md`）**：**`:80-81`** "Specified pins without site binding keep previous state. **All unspecified pins are set OFF.**"；`:87-89` `SetOn(K1,K2,-1)`／`SetOn(-1)` 例；**`:92-93`** "`SetOn` 是**排他（exclusive）操作**——每次调用只闭合括号内列出的继电器，**未列出的全部释放（OFF）**"（并点名**两次调用会释放前一次**的陷阱）；`:94` 正确写法；`:96` DALI 先例（TM109/110 合并为一次调用）。⇒ **缺陷性质正式定性**："**该项完整显式闭集里漏列** `K48/K76` ⇒ **主动把它们置于 OFF**"（**非**"疏忽漏了一个"、**非**跨项干扰）。
**Ⓕ 新增 FACT 级语义（`t48`）**：**"释放 ≠ 不导通"，语义按继电器类别而异**（`relays.md:29/95/96` + Component-Statistic 分类 + CSV part）：**`K46`/`K41` = BUS + TLP3412(MOS) ⇒ 释放＝开路**；**`K48`/`K49`/`K76`/`K110`/`K43` = Share + IM06DJR(G6K 转换型) ⇒ 释放＝导通其默认通道**；`K109` = BUS + G6K。⇒ **TM600 漏列 `K48` 不会断开 ch5，而是留在 `K48` 默认目的地 → `K49` → `SW1`**（"改道"而非"开路"的机理）；`K46` 为 MOS（漏列即开路）⇒ FPVIe0 高侧 BUS **不接入**；`K110` 默认投去 PB0 侧 ⇒ **ch18 不在 BST 节点上**。⇒ **推论：对 TM600，"闭 `48/76` 须配对显式 `RELAY_OFF`"**不是承重义务****（其它共用源的继电器自身已被释放）⇒ **"补 `[48,76]`"＋（后续）"移除 `K109/K110`"两步足够**；**不得**把"成对 RELAY_OFF"升格为通用契约不变量（更宽的决定，另议）。
**Ⓖ 落盘前独立复核 = `t52`（rule-reviewer）**：核对三条硬约束／内容键与不变量／门禁证据可复现，并确认 ① `ch5/ch18` 仍为 **UNKNOWN**（不得据本任务改判）、② 本轮保留 `K109/K110` 及其耦合代价已登记、③ `--check-extra` 保持禁用、④ `L416-420` 已改为仅陈述操作事实。**通过后由 Captain 执行 REPLACE**。

## 🧭 台账级兜底与两处收口（20:5x）

**Ⓐ 台账级兜底（生效）**：`review-handoff-note-plan-side.md`（`test-strategy-architect`）**正文仍有 3 处旧门表述**（`ate-implementer` 给出 file+line：**L206 / L242 / L252** 仍写 `t40 + t42` 为裁定对；**L9 / L135 已改为 `BLOCKED pending t43`**；**L11 的 `t35` 前置已改为 `t43`**）⇒ **"摘要已改、正文未改"的内部不一致**。我已两次下达定点更正令、作者未改 ⇒ **按我预告的备选路径收口**：
> **以本台账为准**：**门已关闭**（`t39`/`t40`/`t42`/`t43`/`t44` 全部完成）；**落盘由批处理 `t49`+`t50`+`t51` 及其独立复核支配**；**`t35` 路径 A 的开工条件以 Captain 的定案批为准，不以该注记正文为准**；该注记正文的 `t40 + t42` 表述（L206/L242/L252）**视为已取代**。
**Ⓑ canonical 重新定性 + 写入方冻结令（生效）**：**canonical = `implementation-payload-TM600-TM601.cpp` / 41,797 B / `6034af710a348e578099886737cc7cc086c8297808189cfa283ad8ce4ec7c4fa` @20:48:18`**（Captain 独立现算，543 行）；**payload 冻结**（未经 Captain 书面授权不得再写；若必须改 ⇒ 记旧哈希 → 报文新哈希 → 复核方**对新字节重出 verdict**）。TM600 `SetOn`（`L241`，**单次调用 11 项**）= `K83, K60, K61, K48_ACM5_AMP_REF, K76_ACM_BST, K109, K110, K13, K85, K57, K126`；**`K46` 可执行 = 0**；`check-extra` 注释 1 处；TM601 段（`L448`）无 ch5 端点、ACM 驱动 0。**"定性即冻结"成为硬约束**（本 run 已 13 次审核对象被改写）。
**Ⓒ `t48` §8.6 新事实 + **Captain 自我更正****：本版 TM600 **同时闭 `K48/K76` 与 `K110`**，且 `K109` 把 FPVIe1 的 `FL/SL BUS` 绑到 `K110` 的 COM 节点 ⇒ **三个潜在源同接 BST 节点**（`t48` §2.2 警告的汇聚**在继电器层已成真**）。**但 payload 用**仪器输出纪律**摁住它**：TM600 体内 **`PB0_BST_ACM` = 0 次**（ch18 从不驱动）、**`FPVI1.Set(FV,0,…,FPVIe_RELAY_OFF)` 于 `L355` 显式释放 ch1**。
⇒ **INFERENCE（要点）**：**"闭 `48/76` ⇒ 其它共用节点仪器输出 OFF"在本版是**承重前提****（**不被 `cbite.SetOn` 排他性强制**，而靠仪器输出纪律实现）；在**部署态**（两腿皆未闭）它只是潜在的。
⇒ **Captain 撤回此前说法**：`t48` 前一轮的"对 TM600 该配对**非承重**"**不再成立**（其基于"其它源继电器已被释放"的早期判断）；**`t34` 须改为**"**本批 payload 的并集安全性依赖仪器输出纪律……不得断言'配对要求已被继电器排他性满足'**"。
⇒ **另**：`t38` 的移除**在 payload 中已生效**（TM601 段无 ch5 端点）；`t48` §8.4 的"TM601 仍在驱动"**只适用于部署态** `15c7d2b8…`。
**Ⓓ 文档值（现算，引用一律现算）**：`t35` = `3dab888504e82fb090499685916ab7df6512b71caf7788a5d170bce6769be511`@20:49:14（v1.15）；`t41` = `509f4a3952e77b24c2880569212824a19abaef8033e77adefdb417415cd0fe93`@20:49:14（v1.6）；`t48` = **23,197 B / `ed905bfc8397319f28a2ed75163bfbeb28f7193cacf3b986efb110c3a41aa44a`**（§8 追加；原 `ae135c06…` 作废）；`acceptance-report.json` = `d61d8c93f7410854904d5f67e2126c9add445218acdc0d911a7d5a39b78a27ab`（27,186 B）；`review/t43-…md` = 7,439 B / `d4c38354…`；`review/t40-…md` = **27,250 B / `67fb79e1acd9adb69368ab81c391318da61eee88040a5dfdb2a436e0db85aea1`**（**Captain 早前引的 `37430005…` 是旧代，此处更正**）。

## ✅ 归属争议已闭（20:5x）：**ch5 在案**；仅"机台确认"仍缺

**Ⓐ 结论与依据（不是我单方裁的）**：**`SW12_U1REF_BST_ACM`（`Pin_Channel_define.h:20`，通道 5）与 `PB0_BST_ACM`（`:33`，通道 18）是两台不同仪器** ⇒ **本案仪器的 BST 腿 = `K48`+`K76`（ch5）**；`K110_ACM18_BST`/`K109_BUSL1_PB0` 属 **ch18 与 FPVIe[L]**，**不属本案仪器**。
依据链：**(1) 生产树行为（最硬）**：`test.cpp:7000/7087/7170/7513` 对**本仪器**闭 `K60,K61,K48,K76`，注释逐字 `(FH5→BST)`；**全文件 `K110_ACM18_BST`=0、`K109_BUSL1_PB0`=0**；**(2)** `t42` 独立复核 **pass**（10/10 零改动现算）；**(3)** `t43` 的裁定方**撤回其 UNKNOWN** 并**认账**"把契约派生文本当同级证据"的次序错误，给出**证据强度排序**：**行为/生产实现 > 权威网表 > IR/派生表 > 契约派生字段**；**(4)** **契约 owner 撤回**其 `bst2sw` 映射错误；**(5)** 族结构：**`[110,61]` 在任一读法下都不完整**（ACM200 读法缺 `48/76`；FPVIe[L] 读法**缺 `K109`**，而 `K109` 才是把 `FPVIe1_FL/SL_BUS_S1` 低域 BUS 带入该节点的**选择继电器**）。
**Ⓑ 因此终批改为"收窄 + 移除"**（取代我此前"维持并集"的裁定）：**rev 25 收窄式**（`bst2sw` → ch5 路线 `[48,76]`＋SW `[60,61]`；原文标 `superseded`；**ch18 路线单列**；按通道分列；`relayChainHigh/Low` 写成 **`absent`（非 `null`）**）＋ **payload 补 `K48/K76`、移除 `K109/K110`** ＋ **计划 v22 收窄式**（`[110,61]` → **`[48,60,61,76]`** 分两侧）。⇒ **消除耦合**（不再把 FPVIe1 低域总线与未驱动 ch18 引脚接到 BST 节点）且 **`--check-extra` 不再需要禁用**。
**Ⓒ 真正剩余的 UNKNOWN（只有这一条，且不阻塞落盘）**：**归属的"机台确认"仍缺** —— 本判定**全部为代码行为/文档推断（INFERENCE），无电性实测**；`relays.md:31` 的机械语义亦为 INFERENCE/UNKNOWN（`K110` 型号 `IM06DJR` 未核手册），但**不影响本裁定**（本裁定依行为，不依机械语义）。**残余耦合与"若归属判错"的风险一律写入 `t34` limitations。**
**Ⓓ 口径（引用一律现算）**：闭集 **`[48,60,61,76]`**（BST `[48,76]` ∈ ACM200／SW `[60,61]` ∈ FPVIe[L]）；`t30` 对 TM600 期望（三源并集）**`{48,60,61,76,83}`**；**`T32-F1`** = "**本项 `SetOn` 未含 `K48/K76`**"（**不是**"缺 `K109/K110`"）；**计数口径**（`schematic-expert`/`compile-diagnostician` 双向更正后）：`K48_ACM5_AMP_REF` **SetOn 操作数 4**／注释 4／**总提及 8**；`K76_ACM_BST` 同；`K_FPVIH_TO_BST_A` **2**／注释 4／总提及 6；`K_BST_ACM` 等族宏 **全 0 总提及**；**"驱动且闭腿"＝4（drive-strict）／5（comment-inclusive）** —— **两数均须带定义**。

## 🚀 终批 payload 已落盘（21:0x）—— 待实现者报"最终已写完"后定性冻结

**Ⓐ 授权改动已执行（Captain 现算）**：`implementation-payload-TM600-TM601.cpp` = **42,998 B / `c03632d93e0d4cc594ed4045bf6d52e6d3f897e61ed183e0475d556c45db26e0` @20:59:12`**（复核方在其前一瞬测得 `42,440 B / `72d7bc3a…`` ⇒ **存在两次写入**，**最终态以实现者书面报告为准**）。
**TM600 `SetOn`（`L256`，9 项）**：`K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` ⇒ **可执行 `K109`=0、`K110`=0、`K48`=1、`K76`=1、`K46`=0**；`SetOn` 调用 2 次（TM600 `L256`／TM601 `L463`）。**即：补 `K48/K76`、移除 `K109/K110`（收窄式终批）已完成**。
**Ⓑ 定序（照冻结令）**：**实现者报"最终已写完 + `size/sha256/mtime` + 9 项 SetOn 原文 + 内容键/不变量自检"** → **Captain 重新定性 canonical 并冻结** → **复核方对该字节出 verdict**（`t52` 旧 verdict 作废重做）→ **Captain REPLACE** → 门禁前后快照 → **Captain 代跑 Release 编译** → `t33`/`t34`。
**Ⓒ 新增事实（子集语义，`schematic-expert`）**：`verify_bst_sw_sequence.py` **`L448 missing = sorted(set(exp) - data['nums'])`** ⇒ **断言是子集语义**（期望须被实际闭集包含；**多闭仅在 `--check-extra` 下才报**）⇒ **默认语义下"保留 `K109/K110` 也不会使 `bst-sw` 变红"** ⇒ **移除 `K109/K110` 属契约/耦合层动作，不是"转绿前置"**（与 Captain 裁定理由一致，不冲突）。⇒ **`t30` 转绿条件**：TM600 闭 **`{48,60,61,76,83}`**（BST `{48,76}` + SW `{60,61}` + `pmid2sw` 的 `83`）。
**Ⓓ 口径（两个层次，勿混）**：**契约条目值**（`bst2sw.closedRelayNumbers`）＝该对两侧并集 **`{48,60,61,76}`**；**`t30` 对 TM600 期望**＝三源并集 **`{48,60,61,76,83}`**。
**Ⓔ 归因更正（`schematic-expert`/`test-strategy-architect` 自查）**：**部署态 TM600 自身两腿皆未闭**（`L9057-9217` 内 `K48/K76/K109/K110` 命中 **0**，而 `SW12_U1REF_BST_ACM`=**10**）⇒ **"高侧敞口在部署侧"**；此前把 `L6997/L7000` 当作"部署态 TM600 在闭 `K48/K76`"属**归属错误** —— 那些行属 `TM607_BUCK_LS_ZCD(L6985)`／`TM608_BOOST_HS_ZCD(L7073)`／`TM609_BOOST_HS_NEG(L7160)`／`TM640_BOOST_HS_OCP(L7503)`（另 `L7619`→`TM641_BST_UV`、`L7730`→`TM643_VBAT_LOOP_INDICTOR`）⇒ 它们仍是"**在役路线＝ch5 `[48,76]`**"的有力证据，**但不得用来断言 TM600 自身行为**。

## ✅ 一处 Captain 前裁的更正确认（21:1x）："配对 `RELAY_OFF`"的承重性随版本翻转

**Ⓐ 事实**：**中间版本 `6034af71…`（41,797 B）同时闭 `[48,76]` 与 `[109,110]`** ⇒ BST 节点有**三个潜在源**（ch5 经 `K48/K76`、ch18 的脚经 `K110`、FPVIe1 低域 BUS 经 `K109`）⇒ **该版下"配对 `RELAY_OFF`"是承重的**（靠仪器输出纪律：`PB0_BST_ACM` 0 次、`FPVI1` 于 `L355` 显式 `RELAY_OFF`）。
**现盘冻结版 `c03632d9…`（42,998 B）已移除 `K109/K110`** ⇒ **BST 节点只剩 ch5 一源** ⇒ **"配对 `RELAY_OFF`"退回**潜在**（`PB0_BST_ACM` 不驱动、`FPVI1` `RELAY_OFF` 由"必需"降为"双保险"）**。
⇒ **Captain 先前"对 TM600 该配对非承重"的说法，在**中间版**下不成立（已撤回），在**现冻结版**下**重新成立**；`t34` 的表述请写成 **"在中间版（并集）下承重；在现冻结版（单路线）下潜在"**，并注明版本。
**Ⓑ 不变项**：`K110.pin4 ≡ K76.pin4`（`NetK76_ACM_BST_S1_4`）、`pin5 ≡ pin5`（`NetK57_CAP_BST_SW_S1S2_3`）**仍成立**（FACT）；`TM641`/`TM643` 的"闭腿不驱动"先例亦成立 —— 且**源码内自带宏展开证据**：`L7619/L7730` 写 `K_FPVIH_TO_BST_A = K46_BUS0_FH_SW1 + K48_ACM5_AMP_REF + K76_ACM_BST`、`L7597/L7713` 写 `… ACM200_FH8→SW（共用 K61）` ⇒ **FPVIe0→BST 腿包含 ch5 的 `K48/K76`**，这正是 `TM641/TM643` 必须把该 ACM 源 `RELAY_OFF` 的原因（**命名层证据，强于只引裸宏**）。
**Ⓒ 计数（三列口径，已三方现算一致）**：`K48_ACM5_AMP_REF`／`K76_ACM_BST` = **调用点 4** + **注释 4** = 总计 8；`K_FPVIH_TO_BST_A` = **调用点 2**（`L7623`/`L7734`）+ **注释 4**（`L7597`/`L7619`/`L7713`/`L7730`）= 总计 6；`K_BST_ACM`／`K_FPVIL_TO_BST_B`／`K110_ACM18_BST`／`K109_BUSL1_PB0` = **0/0/0**。⇒ **凡引用必须带"调用点/注释/总计"标签**。

## ⚠️ 裁定效力限定（21:1x，`schematic-expert` 提出，Captain 采纳并**须写入 `t34` 与终批说明**）

> **方案 B（移除 `K109/K110`、只闭 ACM200 族 `{48,76}` + SW 侧 `{60,61}`）由**工程判断与契约一致性**保证，门禁不具备反证能力。**
> **理由**：未启用 `--check-extra` ⇒ `bst-sw` 为**子集判定**（`missing = exp − actual`）⇒ **多余的闭合不可见** ⇒ **若将来有人把 `K109/K110` 加回 payload，期望集仍被满足 ⇒ `bst-sw` 依旧 GREEN**。
> ⇒ **B 的守卫在代码评审与契约一致性，不在门禁**；欲使其受门禁保护，须**另立明确决定**启用 `--check-extra`（并定义 budget 池），**不得顺手打开**。

**Ⓐ `t53` 的一处时效性要求（避免新引入门禁查不出的契约内部不一致）**：`bst2sw` 的 `closedRelayNumbers` 应写 **`{48,60,61,76}`**（或显式拆成 BST 端 `{48,76}` / SW 端 `{60,61}`）—— 因为 **`pmid2sw={60,61,83}` 已含 `60,61`** ⇒ 写 `{48,76}` 与写 `{48,60,61,76}` **得到相同的 TM600 期望 `{48,60,61,76,83}`**（**门禁分辨不了**），但**同族差分别名 `pmid2sw`/`sw2pgnd` 都把 SW 端写作 `{60,61}`**、且**部署态四个 BST–SW 项都同时闭 `K60`+`K61`** ⇒ 只写 `{48,76}` 会**新引入一处契约内部不一致**，而该不一致**门禁结构上查不出**（子集判定）。
**Ⓑ `t54` 的可核对预期（两种写法下都成立）**：
```
payload (c03632d9…, {13,48,57,60,61,76,83,85,126})  ⇒ missing = []        ⇒ bst-sw PASS
部署态  (test.cpp:9081, {13,57,60,61,83,85,126})    ⇒ missing = [48, 76]   ⇒ FAIL（**红因正确**，不再是缺 110）
```
⇒ **若出现别的组合 ⇒ `t53` 改动超出预期范围，须回退核对**（不得按红/绿二分草率下结论）。

## 📏 第 6 条引用纪律（21:2x，`compile-diagnostician` 提出、Captain 采纳为 run 规则）：**消息中不输出哈希字面**

**Ⓐ 规则**：**消息/通报里只给「路径 + size + 现算命令」，不输出任何 64 位哈希字面**；需要的值由接收方**现算**或读**单一真源** `gate-logs-t28/t28-anchors.json`。核对结果**落盘为可复读日志**（现算写入），供对方逐条现算比对，**不必采信任何人的字面**。
**Ⓑ 依据（本 run 的实测教训）**：`t28-citation-notice.txt` 与 `t28-anchors.json` **盘上均正确**（真源 `check_input_sync.py` 条目 len=64 与现算一致），**错的只有"把脚本输出重打成消息"这一步** —— 即 **"脚本渲染 ≠ 不经人手"**：复制粘贴这一步会把错误重新引入。⇒ 后续应**从机制上消除该通道**，而非逐次纠正字面。
**Ⓒ 配套（已采纳）**：① 核对他人哈希**必须现算并逐字符 diff**，**不得因自己探针报 False 就改认他方值**（本 run 两个方向各犯一次：照录他方错值 / 把正确的 `c` 改成 `b`）；② 比较**两个现算结果**（`sha256(a) == sha256(b)` 或与产物内冻结字段比对），**不构造 expected 值、不手打、不做逐位人工推理**；③ 报告类文档（`t28-summary.md` 19,301 B、`t30-summary.md` 20,633 B 等）**尺寸一律现算**；④ `devel/source/test.cpp` 补全为 **434,629 B**（此前只给前缀）⇒ 可作 `t34` 的"生产树未被改动"并列证据。

## 剩余未知（UNKNOWN，不得当作已验证）

1. 运行时对 `needs_revision` 是否真会自动生成 repair —— 本会话尚未观测。
2. `tm600.sv`/`tm601.sv` 是否已完整描述所需寄存器写入（t4/t5 需判定）。
3. VS `devenv` 在本次会话能否真实完成 Release 编译（baseline 当时 VS 未运行，用的是磁盘源码）。
4. 验收标准 6「编译成功 ≠ 电性正确」：本轮**不含**任何硬件/电性实测。
