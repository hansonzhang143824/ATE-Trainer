# t25 门禁 harness/模型修复（F1 + F2 + F3 诊断）— 收口报告

- run-id：`acceptance-20260916-dali10`
- 执行者：compile-diagnostician（attempt 1，`attempt_id 64d90135-87f9-4440-9717-d2c35edc094c`）
- inScope：`scripts/run_gates.ps1`、`scripts/verify_relay_trace.py`、`team/artifacts/acceptance-20260916-dali10/gate-logs-t25`
- 取证纪律（本轮实测确认）：本工作区源受 DLP 透明加密，**pwsh 是盲的**。所有哈希/文本取证均
  由 **python 以 rb 读取**，并标注 `plaintext / binary-TSZ-container`；未对受保护源使用
  `Get-FileHash` / `Select-String` 做前后比对或内容判断。

> **⚠️ 附录更正（2026-09-16，独立复核后）**：`t25-reviewer-response.md` 是本报告的**权威附录**，
> 其中含两处**自我更正／撤回**：
> ① §3.4/§7 中"`K_SW_BST_Cap` 修复后不再被 `SW` 触发"**错误** —— 实测
>    `fam_intersect({'SW'},'SW_BST') = ['SW']` **仍命中**（token 边界 `_` 合法）；
>    F2 的准确收敛是"只消除 2 条（K44/K45）"，`SW_BST` 的匹配**未被改动**。
> ② §6 待裁项 1 的 **(A) 建议（扩 t25 权限让我落地 meta）已撤回** —— 实测 `t26`
>    （owner setup-architect）的 inScope **已包含** `project/DALI/meta/dali_tm_meta.json`，
>    为避免同一文件同一字段的并发写冲突，改推 **(B) 由 t26 单一 owner 落地**；
>    脚本侧 F1/F2 已生效，t26 的 verify 命令直接受益。

> **⚠️⚠️ 最终树复核（2026-09-16 更晚，权威结论）**：见 `gate-logs-t25-verify/t25-final-verification.md`。
> 其中三项覆盖本报告：
> 1. **本报告"payload 未落盘 / `test.cpp` 含 2 处裸 `126`（`3dbceb49…`）"已过期** —— 现为
>    `469714 B / 15c7d2b8…`（mtime 18:53:33，`K126_V1P5_CAP`，裸 126 = 0）。该表述在 t25 执行窗口内
>    **实测正确**，但已被后续 payload 落盘取代。
> 2. **门禁现状已被我本人复跑更新**：`FULL_EXIT = 0`；**12 门 = 11 GREEN + `cbit` KNOWN-RED**；
>    `relay-trace` **GREEN**（仅剩 2 条 TM643 存量 WARN，`RELAY TRACE PASSED`）；结论"无新增红 —— 收尾通过"。
> 3. **F2 的验收判据位置更正**：在当前（t26 落地后）输入上，把 `fam_intersect` 换回旧实现结果**完全相同**
>    ⇒ 验收条目"SW 不得匹配 SW1_BST1/SW2_BST2"的**可观测效果现由 t26 的 meta 覆盖达成**；
>    F2 仍**正确且无回归**（A/B 只消 2 条、新增 0；独立穷举证实 NEW 命中集恒为 OLD 子集），
>    但其作用是修复**匹配语义的复发路径**（meta 再变化时该缺陷会复发），
>    不应计入"消假阳性"的独立功劳。准确表述见 `t25-final-verification.md` §4。

---

## 1. 结论速览

| 缺陷 | 状态 | 处置 |
| --- | --- | --- |
| **F1 基线/配置经 pwsh 读被 DLP 加密而静默失效** | ✅ **已修 + 已验证** | `run_gates.ps1` 统一改经 **python 授权读者**解析 JSON；`cbit` 恢复 `KNOWN-RED`，且 **cbit 门从"从未执行"恢复为"执行"** |
| **F2 `fam_intersect` 前缀碰撞（SW ↛ SW1_BST1/SW2_BST2）** | ✅ **已修 + 已验证** | 改为**对称 token 边界**匹配；全树 A/B 对照：消除 2 条假阳性，**新增告警 0** |
| **F3 VBUS 可达性/供电建模** | ⚠️ **反证完成，修法需授权** | 已证明**不是匹配语义缺陷、代码侧无法修**；根因在 meta `powered_pins`；沙箱提案已验证（消除目标告警 1 条、新增 0 条）但**写盘路径 `project/DALI/meta/dali_tm_meta.json` 不在 inScope** → 见 §6 待裁 |

**违反门禁纪律的选项已被显式排除**：`scripts/gate_baseline.json` 内容**一字未改**（哈希前后一致，
§4），未放宽任何判据，未为绿灯盲闭任何继电器。

---

## 2. F1 修复：基线/配置读取改为「授权读者」

### 2.1 缺陷机制（实测）

| 证据 | pwsh 视角 | python 视角 |
| --- | --- | --- |
| `scripts/gate_baseline.json` | `Get-Item` = **8192 B**；`Get-Content -Raw -Encoding UTF8 \| ConvertFrom-Json` → **FAILED** `Unexpected character encountered while parsing value: %. Path '', line 0, position 0.` | **28 B** 明文 `b'\xef\xbb\xbf{\r\n    "cbit":  true\r\n}\r\n'`，解析 = `{"cbit": true}` |
| `project_config.json` | `ConvertFrom-Json` → **FAILED** `Unexpected character ... value: T.`（首字符 `T` = 密文头） | 2102 B 明文 JSON，解析 OK |
| raw bytes 检验 | `-AsByteStream` 首字节 = `25 54 53 44 2D 48 65 61 64 65 72 2D 23 23 23 25` = `%TSD-Header-###%` | `readsAs = plaintext` |

原始代码的两处后果（本次实测复现）：
1. `$baseline` 为空 ⇒ **`cbit` 的 1 个红灯被误判 `NEW-RED`**（实为存量 `KNOWN-RED`）；
2. `$cfg` 解析失败 ⇒ `$stdafx` 为空 ⇒ **`cbit` 门被整段跳过（从未执行）**，并打印
   `WARN: 读不到 project_config.json 的 inputs.relay_definitions → cbit 门将跳过`。

### 2.2 修法（只改读取方式）

新增 `Read-JsonViaPython`（`run_gates.ps1`）：

```powershell
$pyCode = 'import json,sys;sys.stdout.reconfigure(encoding="utf-8");print(json.dumps(json.load(open(sys.argv[1],encoding="utf-8-sig")),ensure_ascii=True,separators=(",",":")))'
$raw = & python -c $pyCode $Path
if (-not $raw -or $LASTEXITCODE -ne 0) { return $null }
return (($raw | Out-String).Trim() | ConvertFrom-Json)
```

- 基线：`$b = Read-JsonViaPython $baselinePath`（**只换读者，`gate_baseline.json` 未动**）；
  并新增一条显式告警：基线解析为空时打印 `WARN: 基线 ... 解析为空 → 存量红无法区分`（**失败不再静默**）。
- 配置：`$cfg = Read-JsonViaPython (Join-Path $root 'project_config.json')`（同一读者）。

**附带修正（本轮自测发现）**：首版曾把 `$root` 误写成 `$PSScriptRoot`。该脚本约定 `$root` = **workspace 根**
（再由 `$root + "scripts\..."` 拼路径），而 `$PSScriptRoot` 在本脚本以副本形式运行/沙箱/dot-source 时会指向
副本目录 ⇒ 基线与配置再次静默找不到。已改回**按本脚本文件真实路径上溯两级**（`$MyInvocation.MyCommand.Path`
→ `$PSCommandPath` → `Join-Path $PSScriptRoot 'run_gates.ps1'` 三级兜底）。
该缺陷以**副本运行**的方式被抓到（副本解析出 `$root = ...\gate-logs-t25`、`path.exists=False`），修后副本亦能正确定位。

### 2.3 验证（同一命令，前后对照）

```
pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t25
```

| | 修复前 | 修复后 |
| --- | --- | --- |
| 基线加载 | `WARN: 读不到 project_config.json ...`（无"已加载"行） | `基线(存量红) 已加载: cbit` |
| 门禁条目数 | **11**（`cbit` 缺席） | **12** |
| `cbit` 判定 | **未执行** | `KNOWN-RED`（exit 1） |
| 汇总尾部 | `存量红（已知, 不阻塞）:` 缺失 | `存量红（已知, 不阻塞）: cbit` |

`KNOWN-RED` 的正确性：`gate_baseline.json` 明文 = `{"cbit": true}` ⇒ `cbit` 是被**登记为存量红**的门，
判定与基线内容一致（**未改基线来制造这个结论**）。

---

## 3. F2 修复：`fam_intersect` 前缀碰撞

### 3.1 缺陷机制（实测复现）

`cap_pin()` 把电容名折算成 PIN token：`K45_Cap_SW1_BST1 → 'SW1_BST1'`、`K44_Cap_SW2_BST2 → 'SW2_BST2'`；
旧 `fam_intersect` 用纯字符串前缀 `p == fam or p.startswith(fam) or fam.startswith(p)`，
在 `fam_intersect(powered={'ISW','SW','VBAT','VBUS','VDRV'}, 'SW1_BST1')` 处因 `'SW1_BST1'.startswith('SW')`
返回 `{'SW'}` ⇒ 对**未供电**的 SW1/SW2 轨提出稳压电容闭合要求。

节点判据（只读，`project/DALI/SCH-Connect-Map.txt`，python 读取）：

| locator | 原文 | 含义 |
| --- | --- | --- |
| `L174` | `CH0 Low -> SW  [Kelvin]  需闭合: K60,K61` | 本项被测的 SW 节点 |
| `L177` | `CH0 High -> SW1  [Kelvin]  需闭合: K46` | **不同节点** |
| `L183` | `CH0 High -> SW2  [Kelvin]  需闭合: K46,K49` | **不同节点** |
| `L156` | `CH0 High -> PGND  [Kelvin]  需闭合: K154,K155` | 本项高端到达点 |

### 3.2 修法

改为**对称 token 边界**匹配（家族相等，或前缀后紧跟非字母数字边界）：

```python
if p == fam: hit.add(p); continue
if p.startswith(fam) and p[len(fam):len(fam)+1] and not p[len(fam)].isalnum(): hit.add(p); continue
if fam.startswith(p) and fam[len(p):len(p)+1] and not fam[len(p)].isalnum(): hit.add(p)
```

- 保留同族：`ISW↔ISW`、`SW↔SW`、`V1P5↔V1P5_VDRV`、`SW_BST` 等 token 内下划线组合；
- 消除异族：`SW ↛ SW1_BST1/SW2_BST2`（数字后缀不是 token 边界）、`VAC ↛ VAC1/VAC2/VAC3`（同类折叠）。

### 3.3 验证 A —— 全树 A/B 对照（旧实现 vs 新实现，同输入同规则）

在只读 `scripts/` 之外的沙箱里以 `proj_config` + 同一条规则跑两遍（`t25-proofs.py` P7）：

| | 修复前 | 修复后 |
| --- | --- | --- |
| 规则自述 | 功能规则 179 处，**FR-001 反向 6 处** | 功能规则 179 处，**FR-001 反向 4 处** |
| exit | 1 | 1 |
| **旧有新无** | — | **2 条**：`TM601_LS_RDSON` 的 `K44_Cap_SW2_BST2`、`K45_Cap_SW1_BST1` |
| **新有旧无（必须为 0）** | — | **0 条** |

⇒ 精确命中"只删 SW1/SW2 假阳性、其余 101 函数判定不变"，**没有新增告警、没有新增红**。

### 3.4 验证 B —— 全量穷举回归矩阵

真实 cap token（`StdAfx.h` 经 `cap_pin()`，13 个）× 101 函数 × 4 权威集（powered/mi/ramp/testpad）
= **5252 对**，逐对比较新旧命中集：变化 52 对，其中
**"命中→不命中" 40 对、"不命中→命中" 0 对**，受影响函数 31 个。
40 对里对**最终规则输出**（是否要求闭某电容）产生实际差异的仅 16 条（`t25-variant-matrix.json`）：
`K45/K44`（正点命中，F2 修复目标）+ 14 条 `K21_VAC_Cap`（同类折叠，见 §5 残留风险）。

---

## 4. F3：VBUS —— 反证 + 沙箱提案（未落地）

### 4.1 反证一：code-only 修不掉（`t25-f3-sandbox.py`）

在**同一规则位点**比较三种匹配语义下 `TM601_LS_RDSON -> K5_VBUS_Cap` 是否仍被要求闭合：

| 语义 | 该需求是否存在 |
| --- | --- |
| V1 修复前（`startswith` 双向） | **True** |
| V2 t25 已落地（对称 token 边界） | **True** |
| V3 reviewer 建议（只约束正方向 `fam + '_'`） | **True** |

⇒ **恒定存在**。原因：命中来自 `powered_pins` 里 **精确存在大写 `VBUS`**（`p == fam`），
与 `SW1/SW2` 那类前缀折叠无关 ⇒ **F3 不能靠改 `fam_intersect` 或规则侧判据解决**。

### 4.2 反证二：`BUSH0_AMUX` 不是根因（任务书表述更正）

任务书 F3 描述为"模型把 `BUSH0_AMUX` 当作 VBUS 供电"。**实测不成立**：

- `verify_relay_trace.py` 的规则输入**只有** meta `capAuthority`（`:311-328`）；
  **不读 `#define` 名、不读 Cap 附件继电器、不读 SCH-Connect-Map** ⇒ `K154_BUSH0_AMUX/K155` 无法进入 VBUS 判定；
- `fam_intersect(任何含 BUSH0_AMUX 的串, 'VBUS') = []`；`BUSH0_AMUX` 相关 token 在 `powered_pins` 中出现 **0 次**；
- 实际触发值：`TM601_LS_RDSON.capAuthority.powered_pins = ['ISW','SW','VBAT','VBUS','VDRV']`，
  其中 `VBUS` 由 `gen_testitems_meta.py:147-187` 从 **OVERVIEW 行**派生（`code` 内 `vset[vbus,...]`）。

`BUSH0_AMUX` 的说法源头是实现者注释（"VBUS reachable via K154_BUSH0_AMUX"），
**该理由本身是错的**（`K154+K155` = `CH0 High -> PGND`，`L156`；VBUS 需 `K3`，`L213/L421`），
但它不是门禁输出的成因。

### 4.3 真根因与冻结裁定的冲突（引用，不重裁）

- 冻结裁定 BD-08：TM601 的 ATE 激励 = **VBAT 4.2 / PMID 9 / VDRV 5**；
  **VBUS 5 V 仅 `simulationDomainReference`，非 ATE 激励**
  （`team/artifacts/.../setup-contract.json` `tmDeltas.TM601.simulationDomainReference`；
  `RUN-LEDGER.md:1397`）。DFT.csv 的 TM601 行**不含 vbus token**（`setup-contract-build.py:1445`）。
- 门禁输入 meta 的 `powered_pins` 却含 `VBUS`（OVERVIEW 派生层，已被 BD-08 取代）⇒ **假阳性**。
- 因此修法只能是**改输入/模型**（run 作用域），且**必须由 Captain 授权**：
  `project/DALI/meta/dali_tm_meta.json` **不在本任务 inScope**。本任务**未改该文件**
  （哈希前后一致：`1c8496645492f7b7…`，§5）。

### 4.4 沙箱提案验证（只写 artifacts 副本，未动生产文件）

副本：`gate-logs-t25/sandbox-f3/dali_tm_meta.t25proposal.json`（仅改一处：
`TM601_LS_RDSON.capAuthority.powered_pins` 去掉 `VBUS`，并加 `_t25ProposalNote` 记录依据）。

A/B 全树对照（`t25-f3-sandbox.py`）：

| | 线上 meta | 提案 meta |
| --- | --- | --- |
| FR-001 反向处数 | 4 | **3** |
| exit | 1 | 1 |
| 消除告警 | — | **1 条**：`TM601_LS_RDSON: 静态供电 VBUS 但未闭稳压电容 K5_VBUS_Cap` |
| **新增告警** | — | **0 条** |

⇒ 提案**精确命中 F3 目标、零副作用**，可直接落地（需授权）。

---

## 5. 改动清单与哈希（python / DLP 授权读者计算）

| 文件 | 前 | 后 | BOM | 行尾 |
| --- | --- | --- | --- | --- |
| `scripts/run_gates.ps1` | 7660 B `91b3fcfcd8027393…` | **9763 B `dd2a4337f22d339a…`** | 保持 UTF-8 BOM | 保持 LF |
| `scripts/verify_relay_trace.py` | 19507 B `18654b3ccddad9a9…` | **21068 B `65e0c67f827bf4ff…`** | 无 BOM（原样） | 保持 LF |

**明令禁止改 / 本任务未改（哈希前后一致）**：

| 文件 | sha256（python 明文） | 说明 |
| --- | --- | --- |
| `scripts/gate_baseline.json` | `021015da84e6fd4c…`（28 B，`{"cbit": true}`） | **内容一字未改**（备份 `backups/gate_baseline.json.pret25` 同哈希） |
| `project/DALI/meta/dali_tm_meta.json` | `1c8496645492f7b7…` | F3 目标，未授权未改 |
| `implementation-payload-TM600-TM601.cpp` | `444810dde99f79ed…` | 未触碰 |
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | `3dbceb496d79d7d0…`（462848 B） | 目标树未改（**仍含 2 处裸 `126` 错误**，见 §6） |
| `D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h` | `ba8ab3de1b0c35cb…` | 目标树未改 |
| `D:/PROJECT6-DALI/devel/source/test.cpp` | `5c9cb3f9339f6db3…` | **生产树只读，与 run 基线一致** |
| `D:/PROJECT6-DALI/devel/source/StdAfx.h` | `ba8ab3de1b0c35cb…` | **生产树只读，与 run 基线一致** |

**备份**：`gate-logs-t25/backups/{run_gates.ps1,verify_relay_trace.py,gate_baseline.json,dali_tm_meta.json}.pret25`
（改动前快照，哈希见 `t25-hashes.json`）。

**本轮未编译**：未执行 `fast_rebuild.ps1` / MSBuild —— t25 的 verify 命令只要求跑门禁；
目标树 `test.cpp` 仍含 2 处 `虚构继电器名 126`，此时编译无验收意义（t8 职责）。

---

## 6. 待裁 / 残留风险（不隐藏）

1. **【阻塞 F3 闭合 · 需授权】** 修 F3 必须改 `project/DALI/meta/dali_tm_meta.json`
   （**不在 inScope**）。已备好零副作用提案（§4.4）。**请裁定**：扩大 inScope 由我落地，
   或另开任务给有该路径权限的成员。在裁定前**我不动该文件**。
2. **残留风险 R1**：本轮 F2 修复在 16 条规则需求上与旧实现不同（除 K44/K45 外另有 14 条
   `K21_VAC_Cap`，来自 `VAC ↛ VAC1/VAC2/VAC3` 的同类折叠）。**这 14 条在修复前与修复后都不出现在
   任何门禁输出里**（受 meta 的 mi/ramp/testpad 豁免或已被闭合），故对"无新增红/绿"**零影响**；
   但 `VAC1_FB` 等函数是否需要 `K21_VAC_Cap`（VAC 裸族电容）属工程问题，需独立复核确认
   （我倾向：VAC1 节点的稳压电容是 `K_VAC1_Cap`，裸 `VAC` 家族电容不适用，但仍应留痕）。
3. **残留风险 R2**：`K_SW_BST_Cap`（token `SW_BST`）在修复后不再被 `SW` 触发闭合要求；
   它与 `K57_CAP_BST_SW`（token `BST_SW`）是否指同一物理节点，本轮**未实证**
   （`cap_defs` 的通道归并只在同通道号内生效）。留作独立复核项。
4. **目标树仍红（非本任务范围）**：`TM600_HS_RDSON`/`TM601_LS_RDSON` 各有 1 处
   `虚构继电器名 126 (无 #define)`（`test.cpp` 未落地 payload 修复）⇒ relay-trace 仍 `NEW-RED`。
   这是**修复前就存在的红**，t25 未新增任何红。
5. **未跑编译 ⇒ 无编译结论**。另：**编译成功 ≠ 电性/硬件正确**（本报告不含任何电性结论）。

---

## 7. 证据文件

| 文件 | 内容 |
| --- | --- |
| `gate-logs-t25/t25-proofs.json` | P1–P7 反证与全树 A/B 对照 |
| `gate-logs-t25/t25-variant-matrix.json` | 三种匹配语义的需求矩阵（152/136/135 条） |
| `gate-logs-t25/t25-f3-sandbox.json` | F3 code-only 反证 + 提案 A/B |
| `gate-logs-t25/t25-hashes.json` | 全部目标/日志/证据的 sha256 + plaintext 判定 |
| `gate-logs-t25/t25_apply.py` / `t25_apply2.py` | 逐字节保留 BOM/LF 的补丁器（含前后哈希） |
| `gate-logs-t25/{各门禁}.log` / `run-gates-stdout.log` | 门禁原始日志 |
| `gate-logs-t25/backups/*.pret25` | 改动前备份 |
