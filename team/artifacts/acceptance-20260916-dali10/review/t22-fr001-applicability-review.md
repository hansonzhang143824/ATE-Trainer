# t22 — FR-001 适用边界只读审查：TM600_HS_RDSON / TM601_LS_RDSON

- 任务：t22（attempt 1，attempt_id `ced1b66b-1ac3-4de7-b971-cc183f375d25`）
- 审查人：rule-reviewer（独立于 Captain 与实现者）
- 日期：2026-09-16 · run: `acceptance-20260916-dali10`
- 约束遵守：**只读**。未修改任何代码、产物、计划、契约、生成器或目标树（前后哈希见 §9）。
- 取证纪律：内容断言一律 **python 明文**；哈希为 **python-plaintext sha256**；每条断言附 locator。

---

## 0. 摘要（结论先行）

| 门禁发现（`gate-logs-t20/relay-trace.log` L5–L8） | 独立判定 | 依据 |
|---|---|---|
| `TM601_LS_RDSON` 未闭 `K5_VBUS_Cap` | **假阳性** | VBUS 在本 run 无任何电源；meta 的 `vbus 5.0` 是仿真域值 |
| `TM601_LS_RDSON` 未闭 `K45_Cap_SW1_BST1` | **假阳性** | 令牌前缀碰撞：`SW` 前缀命中 `SW1_BST1`，而 SW1 未被供电 |
| `TM601_LS_RDSON` 未闭 `K44_Cap_SW2_BST2` | **假阳性** | 同上（`SW` → `SW2_BST2`） |
| `TM601_LS_RDSON` 未闭 `K57_CAP_BST_SW` | **真红（当前部署态）** | `BST_SW` 是真实供电轨（`hardwareInit` `bst_sw`=5.0）；但已存在于更新后的 payload 中，**待落地** |
| `TM600_HS_RDSON`（0 条） | **无需处置** | 其 `powered_pins` 不含 VBUS/SW，且已闭 `K57_CAP_BST_SW` |

**两条必须纠正的既存叙事（否则下游会误判）：**

1. **那 4 条是 WARNING，不是 ERROR。** `verify_relay_trace.py:412-420` 只在 `errors` 非空时 `sys.exit(1)`；`warns` 仅在 `--warn-as-error`（`T237`）时才致红。本次 FAIL 的真实原因是**另两条** `虚构继电器名 126 (无 #define)`（L10–L11）——**与 FR-001 无关**。
2. **门禁日志评估的是 18:23:31 的部署版本，不是 18:33:33 的最终 payload。** 因此"4 条电容发现"描述的是**旧**代码状态；最终 payload 已闭全部 4 个（`implementation-payload-TM600-TM601.cpp:345`），但**该写入从未落到 `ForCodexDebug`**。

---

## 1. FR-001 规则原文与适用边界（locator + 逐句引用）

**规则位置**：`scripts/verify_relay_trace.py:305-328`（注释 `L305-309`，实现 `L310-328`）

逐句引用（`L310-328`）：

```text
310  meta_fn = meta_by_name.get(name)
311  if meta_fn is not None:
312      ca = meta_fn.get('capAuthority') or {}
313      powered = {p.upper() for p in ca.get('powered_pins', [])}
314      mi = {p.upper() for p in ca.get('mi_pins', [])}
315      ramp = {p.upper() for p in ca.get('ramp_pins', [])}
316      testpad = {p.upper() for p in ca.get('testpad_pins', [])}
317      for ptok, cap_relay in sorted(cap_defs.items()):
318          fam_powered = fam_intersect(powered, ptok)
319          if not fam_powered:
320              continue
321          if fam_intersect(testpad, ptok):
322              continue  # 该家族只作测试垫偏置, 非供电轨
323          if cap_relay in relays:
324              continue  # 已闭其 Cap
325          if fam_intersect(mi, ptok) or fam_intersect(ramp, ptok):
326              continue  # 该 PIN 被测电流 / 是 ramp 扫描源 (按 PIN 豁免, 非按函数)
327          cap_rev_checked += 1
328          warns.append(f'{name}: 静态供电 {"/".join(sorted(fam_powered))} 但未闭稳压电容 {cap_relay} (FR-001 反向: 供电→闭; meta权威)')
```

**适用边界（逐条，含机制）**

1. **仅对"有 meta 的函数"生效**（`L311`）。TM600/TM601 均在 meta 中（`project/DALI/meta/dali_tm_meta.json`，101 函数）。
2. **触发前提**：`fam_intersect(powered_pins, cap 的 PIN 令牌) ≠ ∅`（`L318-320`）。即**只看 meta 声称的静态供电轨**，不读原理图、不读本 run 裁定。
3. **四类跳过条件**（按 `L321/323/325` 顺序）：测试垫家族（`testpad`）、已闭该 Cap（`relays`）、该 PIN **被测电流**（`mi`）、该 PIN 是 **ramp 扫描源**（`ramp`）。
4. **匹配函数 `fam_intersect`（`L56-58`）是双向前缀匹配**：
   `return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}`
   → 只要 `fam` 是 `p` 的前缀即算命中。**这是 K44/K45 假阳性的机制**（见 §3.2）。
5. **豁免按 "PIN 令牌" 而非按函数**（`L326` 注释原文："按 PIN 豁免, 非按函数"）。
   ⚠️ **关键限定**：该豁免比对的是**电容自身的 PIN 令牌 `ptok`** —— `K57_CAP_BST_SW` 的 `ptok` 是 **`BST_SW`**，**不是 `SW`**（`cap_pin` 解析见 `L100-116`；实测见 §3.4）。
6. **`cap_defs` 的 PIN 令牌来源**（`L273-286`）：由 `StdAfx.h` 的 `#define K\d*_\w+` 表经 `cap_pin()` 解析，并按通道号归一化到权威名（`L268-272` 注释）。
7. **严重级别**：命中只 `warns.append`（`L328`）→ **WARNING**；只有 `errors`（`L375` 等）才 `sys.exit(1)`（`L416-420`）。`--warn-as-error` 会把 WARNING 升级为 FAIL（`L421-423`、`L237`）。

**对 TM600/TM601 的适用边界小结**：该规则**只**依据 meta 的 `powered_pins` 与 `cap_defs` 的令牌做静态推断，**既不读原理图连通性，也不读本 run 的 BD-08 裁定**。因此凡是"meta 供电模型 ≠ 本 run 真实激励"或"令牌前缀误撞"的地方，它都会产出**基于错误前提的发现**。

---

## 2. 输入事实（实测，全附 locator）

| 事实 | 值 | locator |
|---|---|---|
| TM600 `capAuthority.powered_pins` | `["BST-SW","BST_SW","ISW","PMID","VBAT","VDRV"]`，`mi_pins`/`ramp_pins`/`testpad_pins` 均空 | `dali_tm_meta.json` → `functions[TM600_HS_RDSON].capAuthority` |
| TM601 `capAuthority.powered_pins` | `["ISW","SW","VBAT","VBUS","VDRV"]`，三豁免集均空 | 同上 `TM601_LS_RDSON` |
| TM600 `hardwareInit` | `vbat 3.5 / pmid 5.0 / bst_sw 5.0 / vdrv 5.0 / iset sw 1.0` | 同上 |
| TM601 `hardwareInit` | `vbat 3.5 / vdrv 5.0 / **vbus 5.0** / iset pmid_sw 1.0` | 同上 |
| 继电器名定义 | `K5_VBUS_Cap`@`StdAfx.h:161`；`K44_Cap_SW2_BST2`@`206`；`K45_Cap_SW1_BST1`@`205`；`K57_CAP_BST_SW`@`220`；`K126_V1P5_CAP`@`299` | `ForCodexDebug/source/StdAfx.h`（python 明文） |
| 电容引脚映射 | `Cap_SW_BST_S1 =220nF 需闭合: K57`@`SCH-Connect-Map.txt:904`；`Cap_SW1_BST1_S1 =220nF: K45`@`905`；`Cap_SW2_BST2_S1 =220nF: K44`@`906`；`Cap2_VBUS_S1 =4.7uF: K5`@`915` | 同左 |
| **VBUS 的真实到达路径** | `CH0 Low -> VBUS [Kelvin] 需闭合: K3`@`SCH-Connect-Map.txt:213`；`CH1 Low -> VBUS [Kelvin] 需闭合: K138,K139,K145,K146,K3`@`421`；路径展开 `S1_FPVIe_FL0 -> K89(NC) -> K3(ON) -> K4(NC) -> VBUS_F`@`214` | 同左 |
| **PGND 高端的真实路径** | `CH0 High -> PGND [Kelvin] 需闭合: K154,K155`@`SCH-Connect-Map.txt:156`；展开 `S1_FPVIe_FH0 -> K87(NC) -> K154(ON) -> K155(ON) -> PGND_F`@`157` | 同左 |
| SW 低端路径 | `CH0 Low -> SW [Kelvin] 需闭合: K60,K61`@`174` | 同左 |
| SW1/SW2 高端路径 | `CH0 High -> SW1 需闭合: K46`@`177`；`CH0 High -> SW2 需闭合: K46,K49`@`183` | 同左 |
| VBUS 无源表对象 | `test.cpp` 中 `VBUS` 相关标识符仅出现于继电器名/其它 TM 名（如 `K5_VBUS_Cap`、`TM204_IPD_VBUS`），**无 VBUS 源表对象**；`sub.cpp` 仅有 `VBUS`/`VBUS_FOVI`/`V_TYP_VBUS` | python 全词扫描 `ForCodexDebug/source/{test.cpp,sub.cpp,*.h}` |
| `mi_pins`/`ramp_pins` 机制在别处确有使用 | `mi_pins` 非空 27/101 函数，`ramp_pins` 非空 41/101 函数；例：`TM641_BST_UV.ramp_pins=['SW']`、`TM1009_QDT_VPCHG_SHORT_CURRENT.mi_pins=['SW1']`、`TM106_HSKP_VBUS_PRST.ramp_pins=['VBUS']` | `dali_tm_meta.json` 统计 |

---

## 3. 逐条独立判定

### 3.1 `K5_VBUS_Cap`（L915）— **假阳性**

- 门禁理由（`relay-trace.log:8`）：`静态供电 VBUS 但未闭稳压电容 K5_VBUS_Cap`。
- **前提错误**：`powered_pins` 含 `VBUS` 的**唯一来源**是 `hardwareInit` 的 `vset vbus 5.0`，而 BD-08 已把该值定性为 **`simulationDomainReference`**，且明确本 run 的 TM601 ATE 激励为 **VBAT 4.2 / PMID 9 / VDRV 5**（`implementation-payload-TM600-TM601.cpp:356,357,359,361`）。
- **旁证**：VBUS 在原理图上**不是电源节点**，而是浮空通道的到达点（`SCH-Connect-Map.txt:213/214/421`）；且 `test.cpp` 中**没有任何 VBUS 源表对象**。
- **判定**：VBUS 在本 run **未被供电** ⇒ "静态供电 VBUS" 不成立 ⇒ **该发现为假阳性**。

### 3.2 `K45_Cap_SW1_BST1`（L905）与 3.3 `K44_Cap_SW2_BST2`（L906）— **均为假阳性**

- 门禁理由（`relay-trace.log:5,6`）：两条都写 `静态供电 SW …` —— **注意它报的供电轨是 `SW`，不是 `SW1`/`SW2`**。
- **机制（实测复现 gate 自身逻辑）**：`cap_pin("K45_Cap_SW1_BST1")="SW1_BST1"`、`cap_pin("K44_Cap_SW2_BST2")="SW2_BST2"`；
  `fam_intersect({'ISW','SW','VBAT','VBUS','VDRV','BST_SW'}, 'SW1_BST1') = {'SW'}`（因 `'SW1_BST1'.startswith('SW')`）。
  ⇒ **`SW` 令牌把 `SW1_BST1`/`SW2_BST2` 前缀误认为同一家族。这就是 L5/L6 报 "静态供电 SW" 的原因。**
- **为何是假阳性**：先看事实。`hardwareInit` 只设 `bst_sw 5.0`（一条 5 V 浮空轨），**未给 SW1/SW2 供电**；SW1/SW2 在原理图上是被通道经 `K46`/`K49` 驱动的**高端到达点**（`SCH-Connect-Map.txt:177/183`），本 run 的 TM601 测量路径是 **SW→PGND**（低端 `K60,K61`@`174`，高端 `K154,K155`@`156`），不经 SW1/SW2。
  再看规则：`SW1_BST1`/`SW2_BST2` **本不在** `powered_pins` 内，纯粹由 §1.4 的前缀碰撞触发。
- **判定**：两条均为**假阳性**。根因是模型缺陷（前缀碰撞），**不是**"SW1/SW2 其实被供电"。
- **补充**：即便 SW1/SW2 真的由某源驱动，也说明 `powered_pins` 漏声明了它们（`powered_pins` 里没有 `SW1`/`SW2`），届时应由**显式声明**而非前缀碰撞来触发。

### 3.4 `K57_CAP_BST_SW`（L904）— **真红（针对当前部署态）；非"SW 豁免"适用**

- 门禁理由（`relay-trace.log:7`）：`静态供电 SW 但未闭稳压电容 K57_CAP_BST_SW`。
  - 该消息里的 "SW" 同样是前缀碰撞的产物；真正命中该 Cap 的令牌是 **`BST_SW`**（`cap_pin("K57_CAP_BST_SW")="BST_SW"`）。
- **关于 `BST_SW` 的供电事实**：`hardwareInit` 实测含 `{"cmd":"vset","pin":"bst_sw","value":5.0}`（TM600 与 TM601 **都有**），且 `powered_pins` **显式**含 `BST_SW`（另有拼写变体 `BST-SW`，含连字符，**永不匹配**任何 `cap_pin` 令牌 → 死条目）。⇒ **BST_SW 确实是本 run 的静态供电轨** ⇒ 门禁要求闭 `K57` 的**前提成立**。
- **"measured current path / ramp source" 豁免是否覆盖 SW？—— 明确不覆盖**：
  1. `L325` 比对的是 **`ptok` = `BST_SW`**，而 `mi_pins`/`ramp_pins` **均为空**（§2 实测）⇒ 豁免不成立。
  2. 退一步，即便按 PIN 语义看：本 run 的 TM601 是 `iset pmid_sw 1.0` 的**强制电流**路径（`hardwareInit`），而电流由浮空源自身的 `MIRET` 读出、电压由 Kelvin 对读出（payload `:413` 一带），SW 并未被声明为 `mi_pins`/`ramp_pins`。meta 在别处**确有**声明此类豁免的先例（`TM641_BST_UV.ramp_pins=['SW']`、`TM1009…mi_pins=['SW1']`）⇒ **该字段可用而本项未填**，属**输入模型缺失**，不是规则不适用。
  3. 物理上：`K57` 的 `ptok` 是 BST_SW，是**被供电轨**；其另一端接 SW（测量节点）。强制电流走 SW→PGND 的 FET 环路，电容支路在稳态不取直流电流，故**不足以构成"测量后必须断开"的理由**。
- **判定**：**真红**（在门禁评估的那一版代码上确实未闭）。**但**：最终 payload 已把它列入 SetOn（`implementation-payload-TM600-TM601.cpp:345`），只是**未落地**。
  ⇒ **"连 K57 也不应盲关"成立，但理由不是"SW 豁免"，而是"它本身有真实供电前提"**；反之亦不可为过关而**删**它。
- 风险提示（供修复窗口）：`K57` 位于**每 site 共享**的 `_S1S2` 家族（`Dali-SCH.csv:346` `K57_CAP_BST_SW_S1S2`），跨 site 闭合需按契约的共享继电器规则处置。

---

## 4. 门禁输入（meta）与本 run 冻结裁定的冲突 —— 因果链

**冲突事实**：

| 来源 | TM601 的供电/激励 |
|---|---|
| `dali_tm_meta.json` → `TM601_LS_RDSON.hardwareInit` | `vbat 3.5 / vdrv 5.0 / **vbus 5.0** / iset pmid_sw 1.0` |
| `dali_tm_meta.json` → `TM601_LS_RDSON.capAuthority.powered_pins` | `["ISW","SW","VBAT","**VBUS**","VDRV"]` |
| 冻结 BD-08 + `test-plan.json`（v19+） | ATE 激励 = **VBAT 4.2 / PMID 9 / VDRV 5**；**VBUS 5 V 仅 `simulationDomainReference`，非 ATE 激励** |
| payload 实际实现 | `VBAT_PD3_FXVI.Set(FV,4.2,…)`@`356`；`V1P5_U34PS_FXVI.Set(FV,5,…)`@`357`；`SW12_U1REF_BST_ACM.Set(FV,5,…)`@`359`；`PMID_HG2_FXVI.Set(FV,9,…)`@`361` —— **无 VBUS 源** |

**因果链（污染路径）**

```
meta 生成器 gen_testitems_meta.py:148-180 （powered_pins = vset + Power列 + Dynamic裸PIN）
        └─ 把 DFT/OVERVIEW 意图层的 `vset vbus 5.0` 直接算作"本函数被 FV 供电的供电轨"（:6, :149）
              └─ dali_tm_meta.json: TM601_LS_RDSON.capAuthority.powered_pins 含 "VBUS"
                    └─ verify_relay_trace.py:313/318 —— FR-001 以 powered_pins 为唯一权威
                          └─ :323 未闭 K5_VBUS_Cap ⇒ :328 产出"静态供电 VBUS 但未闭…"
                                └─ 结论：门禁把"仿真域默认值"误当作"本 run ATE 激励" ⇒ 假阳性
```

**为什么这是"输入模型"问题而非"代码"问题**：门禁**没有**任何读取 `test-plan.json` / BD-08 裁定的通道（`L313-316` 只取 meta）；而 meta 由 DFT 意图层派生（`gen_testitems_meta.py:2,5-8,148-149`），**无从感知 run 级裁定**。⇒ 只要 meta 的供电模型不动，门禁就会持续按旧模型判分。

**同类冲突的第二个面（前缀碰撞）**：`fam_intersect`（`L56-58`）的 `startswith` 使 `SW` 同时代表 `SW`/`SW1`/`SW2`，与 "SW1/SW2 未被供电" 的事实冲突 ⇒ §3.2/§3.3 的假阳性。此缺陷与 BD-08 **无关**，是独立模型缺陷。

---

## 5. 修正建议（可执行，均不越权写目标树）

### 方案 A（**推荐**）—— 在 run 作用域修正门禁输入模型，**不动通用生成器**

**A1. 补齐电流/扫描豁免声明（消除 §3.4 的"按 PIN 豁免未填"缺口）**
- 改法：在**本 run 的 meta 副本**中，为 `TM601_LS_RDSON` 增加 `capAuthority.mi_pins`/`ramp_pins` 声明（该函数为强制电流 `iset pmid_sw 1.0` ⇒ 声明其强制电流路径的 PIN 令牌），或等价地在 run 级 meta 补 `{"name":"TM601_LS_RDSON","capAuthority":{"ramp_pins":["PMID_SW","SW"]}}` 之类**显式**声明。
- locator：`dali_tm_meta.json` → `functions[TM601_LS_RDSON].capAuthority`；规则侧 `verify_relay_trace.py:325`。
- 依据：该字段语义即"被测电流 / ramp 源"（`gen_testitems_meta.py:7-8`）；别处已有 `TM641_BST_UV.ramp_pins=['SW']` 先例。
- ⚠️ **注意**：`PMID_SW` 与 `PMID`/`SW` 的家族关系**同样受前缀碰撞影响** —— 若声明 `PMID_SW`，会因 `'PMID_SW'.startswith('PMID')` 而**连带豁免 PMID 家族**（如 `K85_CAP_PMID`）。故应声明**最小且精确**的令牌集合，并逐一核对。

**A2. 修正 VBUS 供电模型（消除 §3.1）**
- 改法：把 `vset vbus 5.0` 标注为 `simulationDomainReference` 并从 `powered_pins` 中**移除 `VBUS`**（run 作用域 meta 副本 + run 级生成器覆盖）。**同时**：`payload:345` 中为满足门禁而加入的 **`K5_VBUS_Cap` 应移除**。
- locator：`dali_tm_meta.json` `TM601_LS_RDSON.capAuthority.powered_pins`；`implementation-payload-TM600-TM601.cpp:345`。
- 依据：BD-08 裁定；VBUS 在原理图上只是浮空通道到达点（`SCH-Connect-Map.txt:213/214/421`），`test.cpp` 内无 VBUS 源表对象。

**A3. 修正前缀碰撞（消除 §3.2/§3.3）**
- 改法（**run 作用域**，不改通用脚本行为）：把 `fam_intersect` 的前缀匹配改为**令牌边界匹配**（例如要求 `p == fam` 或 `p.startswith(fam + '_')`），因为 `SW1_BST1` 与 `SW` 是**不同家族**而非父子关系；或在 meta 侧撤销对 `SW1_BST1`/`SW2_BST2` 的家族归属。
- locator：`verify_relay_trace.py:56-58`（匹配函数）、`:318`（调用点）。
- ⚠️ **影响面（必须实测）**：该函数在 `L318/321/325` 共 3 处被调用，收紧匹配会**改动全库判分**（`L402`/`L394` 的降级分支亦同）。**不得盲改**：应先以 `--src` 指向**沙箱副本**跑改动前/后对照（本任务为只读，未执行）。

**A 的影响面与可逆性**
- 影响面：仅限**本 run 的 meta 副本**与该副本驱动的门禁；**不改** `gen_testitems_meta.py` 的通用逻辑，**不改**目标树，**不改** `gate_baseline.json`（`t21-new-red-analysis.md:24-26` 已明确禁止以此为遮挡手段）。
- 可逆性：**高**（新增/覆盖的 meta 副本与 payload 均可回退；无编译产物变更）。
- 风险：A3 若真改通用脚本，会影响其它 TM 与其它 run；**故建议先只在本 run 收窄/例外，不动共享脚本**。

### 方案 B —— 具名例外（不改模型，只登记适用范围）

一份**具名例外清单**，逐条给出"规则不适用"的范围与依据：

| # | 例外对象 | 适用范围 | 依据（locator） |
|---|---|---|---|
| B1 | FR-001 对 `K5_VBUS_Cap`（TM601） | 本 run 的 TM601_LS_RDSON | VBUS 非 ATE 激励（BD-08；`SCH-Connect-Map.txt:213/214/421`；`test.cpp` 无 VBUS 源表对象） |
| B2 | FR-001 对 `K44_Cap_SW2_BST2` / `K45_Cap_SW1_BST1`（TM601） | 同上 | 令牌前缀碰撞（`verify_relay_trace.py:56-58`）；SW1/SW2 未供电、且不在 `powered_pins`（`dali_tm_meta.json`） |
| B3 | **不**对本项设例外：`K57_CAP_BST_SW` | — | BST_SW 真实供电（`hardwareInit bst_sw=5.0`；`powered_pins` 显式含 `BST_SW`）⇒ 应闭合，且已定稿于 `payload:345` |

- **B 的前提**：例外必须**具名到"规则 + 函数 + 继电器"**，并以**书面偏离**入卷；同时保留门禁原发现（不得改基线遮挡）。
- 影响面：**零代码改动**；但门禁会**持续报同样 4 条**（除非以 `--warn-as-error` 之外的既有机制登记豁免），需要人在每次跑门禁时人工核对白名单。
- 可逆性：**最高**（纯文档）。
- 缺点：B 掩盖了 §5-A2/A3 两个**真实模型缺陷**，未来同样会误伤别的 TM。

### 方案选择建议（供 Captain 裁定）
**先做 A2 + A1（run 级 meta，最小面、可逆、直击根因），把 A3 作为独立任务并强制"沙箱对照"后再考虑**；B 仅作为 A 落地前的**临时登记**，不作为终态。

---

## 6. 明确回答："可否为了门禁变绿而关闭未供电节点的继电器？"

**结论：否。**

**反证（实证）**：
1. 规则本身把"静态供电"当作闭合的**唯一前提**（`verify_relay_trace.py:318-320`）。对 VBUS，该前提**在事实层面为假**（§3.1：无 VBUS 源、原理图上 VBUS 只是浮空通道到达点）。
2. **最新的 payload 已经这么做了，并因此引入新问题**：`implementation-payload-TM600-TM601.cpp:345` 为满足门禁把 **`K5_VBUS_Cap` 加入 SetOn**，而 `K3`（VBUS 的真实到达继电器，`SCH-Connect-Map.txt:213`）**并未闭合** —— 即出现"**为过门禁而闭合一个不属于任何通路的电容**"：既不构成 VBUS 通路，也不服务任何电源。这正是"为门禁变绿而闭未供电节点"的实例。
3. 规则设计者的原意与"盲目闭合"相反：`L321`（测试垫家族跳过）、`L325`（豁免被测/扫描 PIN）都是**抑制**无谓闭合的闸门；`L305-309` 的注释强调"**即使不需要闭合也要显式 SetOn(-1)**"。⇒ 门禁要的是**正确**，不是**闭合数量**。
4. 工程后果：闭合未供电节点的电容不产生功能收益，却**增加继电器动作次数/接触电阻路径**并可能与共享 `_S1S2` 家族的其它 site 状态冲突（`Dali-SCH.csv:346`）。同时它会**污染测量**：`K5` 的 4.7 µF 若与浮空通道到达点相连（`L214/215` 的 VBUS_F/VBUS_S），在强制电流期间会成为附加负载。

**唯一正确方向**：修正**模型**（§5-A）或在卷面**具名例外**（§5-B），而**不是**补一个电气上无依据的 `SetOn`。

---

## 7. 采纳性检查（对既有叙事的更正）

| 既有说法 | 我的裁定 |
|---|---|
| "门禁对 TM601 报 4 条 FR-001 发现" | **成立**，但须补两点：这 4 条是 **WARNING**（非 ERROR）；评估对象是 **18:23:31 的部署版**，非 18:33:33 的 payload |
| "`TM601…hardwareInit` = vbat 3.5 / vdrv 5.0 / vbus 5.0 / iset pmid_sw 1.0" | **逐字成立**（实测一致） |
| "`capAuthority.powered_pins` = [ISW,SW,VBAT,VBUS,VDRV]" | **成立**（另有 `BST-SW` 只存在于 TM600，且为**永不匹配的死条目**） |
| "冻结 BD-08：TM601 激励 VBAT 4.2 / PMID 9 / VDRV 5，VBUS 仅 simulationDomainReference" | 与 payload 实测一致（`:356,357,359,361`）⇒ **一致** |
| `t21-new-red-analysis.md` F2 称"四条 FR-001 全消失（沙箱 464659 B / `7d97590d…`）" | **无法在当前树复核**：该沙箱副本 `7d97590d…` 不在本 run 目录内；且**最终 payload 未被写入** `ForCodexDebug`（部署态 `3dbceb49…` 仍是旧体）。**该结论目前不成立/未落地** |

---

## 8. 未决与风险（next owner 需知）

1. **写入未落地**：`ForCodexDebug/source/test.cpp` = 462848 B / `3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479`（mtime 18:23:31），其 `TM601_LS_RDSON` 的 `cbite.SetOn`（`test.cpp:9197`）为
   `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, 126`
   —— **缺 4 个 Cap 且用裸 `126`**（对应 `relay-trace.log:10-11` 的 2 条 ERROR）。**这才是本次 FAIL 的直接原因。**
2. **两组问题必须分开记账**：(a) FR-001 的 4 条 WARNING（其中 3 条假阳性 + 1 条真红）；(b) 2 条 `虚构继电器名 126` ERROR（致 FAIL，payload 已修为 `K126_V1P5_CAP`@`StdAfx.h:299`）。
3. **共享继电器风险**：`K44/K45/K57/K5` 均属 `_S1S2` 共享家族（`Dali-SCH.csv:336/326/346/316`），闭合需按契约的跨 site 规则处置。
4. **`PMID_SW` 前缀连带风险**：若按 §5-A1 声明豁免，务必核对 `PMID_SW` 前缀是否连带豁免 `PMID` 家族（如 `K85_CAP_PMID`）。
5. **未验证项（UNKNOWN）**：`gen_testitems_meta.py` 的重跑链路是否会把 run 级修正覆盖 —— **我未执行生成器**（只读约束），故"A 的落地方式"需由后续获批任务以**沙箱**验证。

---

## 9. 只读证明（前后哈希）

`review/t22-readonly-snapshot-BEFORE.json` 记录被检对象在本审查**开始时**的 python-plaintext sha256 与 mtime；审查结束时以同一脚本重算并比对，**全部一致**（见 `review/t22-readonly-snapshot-AFTER.json` 与 `t22-readonly-verify.json`）。

关键锚点（BEFORE = AFTER）：

| 对象 | size | sha256 (plaintext) |
|---|---|---|
| `scripts/verify_relay_trace.py` | 18654 | `18654b3ccddad9a9…`（见 snapshot 全文） |
| `project/DALI/meta/dali_tm_meta.json` | 146180 | `1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693` |
| `project/DALI/SCH-Connect-Map.txt` | 66403 | `cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427` |
| `artifacts/.../implementation-payload-TM600-TM601.cpp` | 31133 | `620d99eaa87b6971cddb16a2dbb1f4af4c950f9fc0b0edcf9b266eb824b53ebf` |
| `artifacts/.../test-plan.json` | 1925250df53f8b52… | （见 snapshot 全文） |
| `ForCodexDebug/source/test.cpp` | 462848 | `3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479` |
| `devel/source/test.cpp` | 434629 | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`（**未改动**） |

---

## 10. 结论

1. FR-001（`verify_relay_trace.py:317-328`）对 **TM600_HS_RDSON 不产生任何发现**，无需处置；对 **TM601_LS_RDSON** 产生 **4 条 WARNING**，其适用前提是 **meta 的 `powered_pins`**，而不读取本 run 裁定或原理图。
2. 4 条中：**`K5_VBUS_Cap` 假阳性**（VBUS 未供电）、**`K44`/`K45` 假阳性**（`SW` 令牌前缀碰撞，SW1/SW2 未供电）、**`K57_CAP_BST_SW` 真红**（BST_SW 真实供电；已定稿于 payload `:345`，待落地）。
3. 冲突因果链：`gen_testitems_meta.py` 把 DFT 意图层的 `vset vbus 5.0` 当作供电轨 → meta `powered_pins` 含 `VBUS` → FR-001 以 meta 为唯一权威 → 假阳性（§4）。
4. 修正：**推荐方案 A**（run 作用域 meta：移除 `VBUS`、补精确豁免声明、收窄前缀碰撞），并以 **B 具名例外**作临时登记；**不得**改 `gate_baseline.json` 遮挡。
5. **不得为门禁变绿而关闭未供电节点的继电器** —— 最新 payload 为满足门禁加入 `K5_VBUS_Cap` 即为反例，应移除（§6）。
6. 本任务是**只读审查**，全程未修改任何被检对象（§9）。

---

## 11. 审查期间发生的并发变更（如实记录，非我方所为）

审查进行中，`implementation-payload-TM600-TM601.cpp` 被**另一名成员**（实现者）修订：

| | size | sha256 (plaintext) | mtime |
|---|---|---|---|
| BEFORE（我取证时） | 31133 | `620d99eaa87b6971cddb16a2dbb1f4af4c950f9fc0b0edcf9b266eb824b53ebf` | 18:33:33 |
| AFTER（并发写入后） | 32969 | `7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b` | 18:36:18 |

**该写入由对方完成，不是我方所为**（我方在 `team/artifacts/.../review/` 之外无任何写入；见 §9）。

**新版本的 SetOn（`payload:201` TM600 / `payload:365` TM601）**：
- `TM600_HS_RDSON`：`K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1`
- `TM601_LS_RDSON`：`K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1`

⇒ 新版本**已移除 `K5_VBUS_Cap`、`K44_Cap_SW2_BST2`、`K45_Cap_SW1_BST1`**，保留 `K57`，并把裸 `126` 改为 `K126_V1P5_CAP`。

**结论一致性**：这与本报告 §3.1、§3.2/§3.3、§3.4 与 §6 的裁定**完全一致**；其注释（`payload:348-360`）独立复述了同一因果链 —— `K5` 不应闭合（VBUS 未经由 `K3` 闭合、非本函数供电）、`K44/K45` 仅因**前缀折叠**被报（原话：*"the gate folds the family by PREFIX"*）。**该实现者修订是独立发生的，非源自本报告的传递**，故可视为对本裁定的**独立互证**。

**仍未解决（不因 payload 修订而消失）**：
1. 该 payload **仍未写入目标树**；部署态 `test.cpp` 依旧是 `3dbceb49…`（含裸 `126` 与缺 4 个 Cap）——见 T22-05。
2. 门禁的**假阳性前提仍未修正**：`dali_tm_meta.json` 的 `TM601_LS_RDSON.capAuthority.powered_pins` 依旧含 `VBUS`，`fam_intersect` 的前缀折叠依旧存在。⇒ 即使 payload 落地，门禁仍会**继续报这 3 条假阳性**（除非按 §5 修正模型或登记具名例外）。
3. `payload:361-364` 已自行声明：`K57` 对被测轨的 RC 建立影响**不在此处论证**，列为 bring-up 项（U11）——与本报告 §3.4 的风险提示一致。

**对修复任务的直接指令（不变）**：payload 保持当前形态（不含 `K5/K44/K45`），并按 §5-A2/A1 修正 run 级 meta；**不得**改 `gate_baseline.json` 遮挡，**不得**为过关而回加 `K5_VBUS_Cap`。
