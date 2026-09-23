

## 2026-09-16 22:0x +0800（RUN-LEDGER 条目） TM601 DFT 修改后的裁定与新 DAG（Captain，最新单一恢复入口）

**用户裁定（本次权威输入）**：用户已修改 `project/DALI/Dali_testmode.xlsx`，**修改后的 TM601 DFT 为唯一权威**；先前 TM601 DFT 有错误，忽略其引起的所有 TM601 报错，不作为阻断、修复或验收失败依据。旧 DFT 派生的 TM601 推断、计划、payload、审查**仅保留审计用途**。

**现盘事实（python read_bytes 现算）**
- 新版 DFT：`project/DALI/Dali_testmode.xlsx` = 12,210,680 B / SHA-256 `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` @ 2026-09-16 21:46:39（旧版 pin 为 `d9d721a3…`，已失效）。
- TM601（OVERVIEW row 133）：`vset[vbat,3.5,100e-6,0]` / `vset[vdrv,5,100e-6,0]` / `vset[vbus,5,100e-6,0]` / **`vset[bst,5,100e-6,0]`（BST=5 V，旧版没有）**；`field[WAKE_UP,1]` + `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]`；`delay[5e-3]` / **`iset[pmid_sw,1,1e-3,0]`** / `delay[2e-3]`；Power=VBAT,SW；`I(PMID_SW)`；SW-PGND；ExpectValue=7.5 mΩ。
- TM600（OVERVIEW row 132）未变：`vset[pmid,5,100e-6,0]`（**PMID=5 V**）、`vset[bst_sw,5,1e-3,0]`（**BST−SW=5 V**）、`iset[sw,1,1e-3,0]`、ExpectValue=11 mΩ、Special=`Y / 2 FLOAT`。
- 目标树 `ForCodexDebug/source/test.cpp` = 469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`（未落盘）；`devel/source/test.cpp` = 434629 B / `5c9cb3f9…`（只读）。
- 旧 run 现盘：`setup-contract.json` 376308 B / `d9ecffb0…`（rev 36）、`test-plan.json` 185689 B / `707ce845…`（v25）、旧候选 payload 43806 B / `66abc088…`；`t55_replace.py` 5573 B / `cc8711f9…`（**未执行**）。
- 旧 run `team.json` phase=`running`：t43/t52 pending、t54 failed；`schematic-expert`/`setup-architect`/`test-strategy-architect`/`rule-reviewer`/`compile-diagnostician` 仍为 working，可能继续改写**旧目录**产物。

**裁定**
1. **停止旧 `t55` REPLACE**：未经新策略与独立审查，**不得落盘任何旧候选 payload**。旧 `66abc088…` 与旧 `2d0984d9…` 一律视为 audit-only。
2. **忽略旧 DFT 引起的 TM601 报错**：旧 `bst-sw`/`relay-trace` 针对 TM601 的红灯、旧 `[110,61]`/`[48,60,61,76]` 之争、t38/t39/t40/t41/t42/t43/t44~t48/t52 的 TM601 结论**均不作为本轮阻断、修复或验收失败依据**（保留审计）。
3. **新职责链**：`dft-expert` 重提取新 DFT → `schematic`/`Setup` 核实物理通路/通道/共享与互斥 → `test-strategy-architect` 制定逐 TM 资源、阶段、寄存器、测量、下电、日志 → `rule-reviewer` 独立审查 → **之后** `ate-implementer` 才映射 API。**Captain 只协调依赖，不落盘、不裁定电气意图**。
4. **TM600 单独复审**（不予豁免）：ACM200 channel 5 → BST 的 `K48/K76`、BST-SW 闭集、多源互斥、以及 **PMID=5 V 与新证据对照旧黄金/`voltage-inference.md` 的 15 V**（并列登记，待裁定，不得静默采用）。
5. **输入冻结**：新 DAG 全部走 `team/artifacts/tm601r3-20260916/snapshot/` 冻结副本 + `pin/snapshot-manifest.json`，以免旧 run 的活跃写入污染新输入 pin。

**新 DAG（staged，等待用户 Approve & Run）**：团队 `ate-dali-tm601r3` / profile `ate-delivery` / 7 成员 / 9 任务 / 依赖 8。
```text
t1  requirements  dft-expert             重提取新 DFT（唯一权威）
 ├─ t2  verification  schematic-expert   JM601 SW—PGND + BST=5 V 可实施性；TM600 ch5→BST/K48/K76/多源互斥
 ├─ t6  implementation setup-architect   契约合并修订（ch5 分组 + 三目的地互斥 + TM601 BST 登记 + 旧条目 superseded）[deps t1,t2]
 │   └─ t7  requirements  test-strategy-architect  逐 TM 资源/阶段/寄存器/测量/下电/日志
 │        └─ t8  review  rule-reviewer   独立审查（verdict=pass 才放行）[deps t2,t6,t7]
 │             ├─ t9  implementation ate-implementer  payload 映射（不落盘）[dep t8]
 │             │   └─ t10 verification rule-reviewer  落盘前检查点 GO/NOGO [deps t8,t9]
 │             │        └─ t11 verification compile-diagnostician 门禁 + Release 编译 [dep t10]
 │             └─ t12 integration setup-architect 十项终稿与残余项 [deps t8,t9,t10,t11]
```

**阻断项（须用户裁定或前置条件满足才能继续）**
- **B1 t55 REPLACE 已停**：执行条件 = t8 `verdict=pass` + t10 检查点 GO + 用户对目标树写入的一次性授权。
- **B2 DFT 现盘已变**：旧 dft-ir 的 `d9d721a3…` pin 失效，21:46 后任何依赖旧读数的结论均须重算（新 DAG 已含此项）。
- **B3 待裁定（不阻断提取，但阻断任何依赖该值的实现）**：新 DFT `vset[pmid,5,…]` 与历史黄金/`knowledge/hardware/voltage-inference.md` 的 PMID=15 V 的差异（TM600）；需用户或授权 owner 给出作用域与重开条件。
- **B4 待核实**：TM601 `vset[bst,5,…]` 的物理含义（BST 单端轨相对 GND，还是 BST−SW 差分=5 V；新 DFT 未给 `bst_sw` 行）——由 schematic/Setup 给事实、strategy 给操作点，不得由实现者猜。
- **B5 旧 run 仍在跑**：旧团队可能继续改写旧目录产物；新 DAG 已用冻结副本隔离，但**旧 run 的 pending/failed 不会自动闭合**，需在终稿或用户裁定中正式登记。
- **B6 边界**：`devel` 零写入；**未做任何机台/电性验证**；**编译闭环 ≠ 电性签核**。


## 2026-09-16 22:1x +0800 Captain 只读预检（第 1 轮 goal 推进）

- 新增 inputs/captain-precheck-new-dft.md = 6671 B / c2b859aa4d613a0f8f4be0aa79e04a73465d680591dbfdabc7c9dac7299ca3d0（现算 @ 2026-09-16 22:02:01）：新版 OVERVIEW row 132/133 逐字段、与旧 IR 的差异表、三处待裁定/待核实项（D1 PMID 5 V vs 15 V、D2 TM601 BST=5 V 语义、D3 源命名三方并存）、旧契约 TM601/TM600 的现盘登记。
- 关键事实：新版 row 133 **只给 set[bst,5,100e-6,0]，没有 st_sw 差分行**；旧 dft-ir.json 的 TM601 条目**没有任何 BST 激励登记**（旧 xlsx 字节不可得，「旧版是否已含 bst 而漏记」= UNKNOWN，不断言）。
- 旧目录继续漂移已在同轮实测（contract 376,308 → 377,128 B），冻结副本策略有效；新 DAG 输入不含任何旧目录现值。
- 本文件为 Captain 自查，**不是 t1 交付件**；t1 必须自行重提取取证。
- 边界：目标树 469,714 B / 15c7d2b8… 未落盘；devel 只读；无机电/电性验证。


## 2026-09-16 22:2x +0800 验证子代理回收 + 预检补遗

- 独立验证子代理 8da92d00-a049-43b6-87d0-d578b0238bbe 完成，产物 inputs/t1-input-diff-new-dft.md = 43172 B / 109f7f3f104c2c3f5aeda04851d3e9cbc60f8b5ae3e95bf36e98e898b01afb36（**子代理自报哈希，Captain 未逐行复核**）。其结论：相对旧版工作簿（见证 dft-raw/overview-dft.json 自记 overview.sha256=d9d721a3…），可比范围内 **TM600 row 132 逐字段相同**；**TM601 L133 的 Code1 由 3 行变 4 行，新增 set[bst,5,100e-6,0]**，该 token 亦不在 	m601.sv 中。
- 该代理另报一项**旧 IR 缺陷**：旧 dft-ir.json 曾断言 OVERVIEW rows 132/133「no force value」，而旧版见证文本当时已含 iset 行 ⇒ **属欠提取，非工作簿变化**。
- Captain 独立实测确认（FACT）：全工作簿 sw2pgnd 命中 **0**；set[bst, 命中 **1**（仅 OVERVIEW:133）；set[pmid, 39；st_sw 24（不含 133）；FPVI/ACM/FOVI/FXVIe 全 **0** ⇒ **DFT 层不给仪器族名**，「FPVI 供 SW—PGND」是下游推断而非 DFT 事实。
- 新增 inputs/captain-precheck-addendum-1.md = 4686 B / 3f2e77f3d64eb645b0793506894fad69e05c798dcb23e9ea2d4c6fbabf7590e8：折叠上述证据、更正预检两处措辞（旧 IR「无 force」为假；sw2pgnd 仅存于 DFT.csv）、列出 5 项仍待 owner 裁定/核实项。**预检本体不改写**（保持 c2b859aa…），避免哈希漂移。
- **DAG 不变**：9 任务 / 依赖 8；上述证据具名落入 t1/t2/t7/t8，无需新增任务。用户裁定项（TM600 PMID 5 V vs 15 V、TM601 bst 语义、旧 run 单方终态）仍待给出。
- 边界：目标树 469,714 B / 15c7d2b8… 未变；devel 零写入；无机台/电性验证。


## 2026-09-16 22:3x +0800 决策板落盘（Captain 证据汇编，等专家接管）

- 新增 decision-board-tm600-tm601.md = 9558 B / c53ea391cd159e9584bb0c2b5fe9afaf06a8b027980c987a8ff3b930444bdf33：① 新版 DFT 逐格地址提取表（TM600 row 132 / TM601 row 133，含 Special 空值、Power=VBAT、de test 非限值等）；② 与激励回路有关的既有事实（pmid2sw=[83,60,61] PMID/SW、sw2pgnd=[154,155,60,61] PGND/SW、st2sw=ACM200 SW12_U1REF_BST_ACM [48,60,61,76]、cm200_ch18_pb0_bst=[110]）；③ 四个待裁定项的并列证据+选项对比+推荐（A PMID 5 V vs 15 V、B set[bst,…] 语义、C TM601 BST 供电源在契约中缺失、D TM600/TM601 端点互斥）；④ 各专家接管所需最小输入。
- **本轮新增的可判定事实（Captain 实测）**：iset[pmid_sw,…] 在工作簿里是**通用回路名**（TM601/TM605/TM609 等行均用），Check 的 loating source：I(PMID_SW) 亦见于 TM605/608/609/627 ⇒ **PMID_SW 不等于端点对**；TM601 的端点对由 Check=SW-PGND 与 Notes=(SW-PGND)/IPMID2SW 表述，而冻结契约里 PGND/SW 那一对登记的别名是 **sw2pgnd**，且 sw2pgnd.closedRelayNumbers 在早期契约中曾为 null（本快照已是 [154,155,60,61]）。
- **新增缺口登记**：冻结契约 st2sw.usedByTm 只有 TM600 (BST must lead PMID)，**TM601 无任何 BST 供电源登记** ⇒ 由 	6 处置（并连带处置 BST 节点多源汇聚 K76.pin4/K110.pin4 同网与 ch5 三目的地互斥）。
- **DFT 容器/明文差异**：python 
ead_bytes = 12,210,680 B，而 PowerShell Get-Item 报 12,218,368 B —— 与既有 TSZ/DLP 记录一致，**引用一律用 python 明文值**。
- DAG 不变（9 任务 / 依赖 8）；本文件为 Captain 汇编，不替代 	1/t2/t6/t7/t8 任何产物，也不构成电气裁定。
- 边界：目标树未落盘（469,714 B / 15c7d2b8…）；devel 零写入；无机台/电性验证。


## 2026-09-16 22:4x +0800 pin 校验器落盘 + 漂移实测

- 新增 erify_pins.py（只读）：一次命令重算 pin 内全部对象并报漂移，当前输出 **pins checked: 19 → ALL PINS MATCH**。
- **本轮 pin 校验抓到 3 处真实漂移**（正是该 pin 存在的意义）：
  1. 	eam/artifacts/acceptance-20260916-dali10/team.json：字节数不变（664,820）但哈希由 5c1c8150… 变为 6e94ec8… ⇒ **旧 run 仍在被改写**（任务状态更新）。旧 run 现盘非终态任务 = t5/t20/t21/t25/t28/t30/t32/t33/t54 ailed、t6/t7/t8/t9/t43/t52 pending；成员中 setup-architect/	est-strategy-architect/te-implementer/
ule-reviewer/compile-diagnostician 仍 working。
  2. 	eam/CURRENT_STATUS.md、3. 	eam/EXECUTION_PLAN.md：因本轮我自己的裁定追加而变。
- 已刷新这三项的 pin 并注明刷新原因；pin 现盘 = 0 B / ，erifier 字段指向 erify_pins.py。
- **结论**：旧 run 的活跃写入与「共同工作区两个 run 并发改写同批产物」的风险已被实测坐实；新 DAG 全部输入走冻结副本的策略继续有效，**不建议**在新 DAG 运行期间沿用旧目录现值作为输入。
- 边界：目标树 469,714 B / 15c7d2b8… 未落盘；devel 零写入；无机台/电性验证。


## 2026-09-16 22:5x +0800 门禁调用方式核实（t11 起点）

- 新增 inputs/gate-invocation-notes.md = 3111 B / 1ab24ec665388a8c6762abc6c6b428bf7fd3ebb401d53c4e0f9297d8a8094ec9：核实 st-sw 门的真实调用方式与判据（
un_gates.ps1:82 调 erify_bst_sw_sequence.py，L5-L14 的目标函数由 meta 拓扑指纹派生、max|iset|>=1A → FPVIe_10A、LS → I2C 0x01、**无 BST-SW 目标时空 PASS**；:34-35 契约常量；
un_gates.ps1:22-25/37 的 -Only/-LogDir/-BuildPath 语义）。
- **可执行后果**：常规跑法**不给 --src** ⇒ 门校的是 meta 派生目标而非候选 payload；要证明候选闭集必须另用 --src <candidate>，并同时核对 targets 非空（t54 已登记：main() 在 targets 空时提前 return，会静默跳过契约闭集断言）。
- **A1.1 新缺口**：脚本把 LS 项归入 BST=5V (禁 10V) 分支靠的是 powered_pins 含 IPMID2SW/PMID-SW 指纹，而新版 DFT 对 TM601 的 BST=5 V 是**显式**给在 L133 的、Power 却只有 VBAT ⇒ 指纹若未命中，TM601 的 BST 约束会落进**空 PASS 而不报警**。归口：t1（IR 与 meta 派生可命中）/t7（计划写明 BST 目标与寄存器依据）/t11（--src+非空 targets 双向确认，禁止以空 PASS 记绿）。
- **未修改任何门禁脚本**（
un_gates.ps1、erify_bst_sw_sequence.py 字节未动）；**本轮未运行门禁**（避免产出与最终树不对应的证据）。
- 边界：目标树 469,714 B / 15c7d2b8… 未落盘；devel 零写入；无机台/电性验证。


## 2026-09-16 23:0x +0800 自我更正：撤回「meta 指纹」口径（门禁适用域）

- 新增 inputs/gate-invocation-notes-addendum-1.md = 4287 B / 8b7795b76b07b4bed3aa1f955c068697a88f6147d7cb5ea46291bee7df8f37fc（本条目**更正** gate-invocation-notes.md 的 A1.1，原文件不改写）。
- **撤回**：「st-sw 门靠 meta capAuthority.powered_pins 指纹归类 LS/HS」以及与它绑定的「meta 指纹未命中 ⇒ TM601 空 PASS」两句。前者只存在于脚本 **docstring L5-L7/L81-L85 的历史说明**，是**已被作者废弃的旧实现**（docstring 自述 2026-09-13 重写）。
- **实际代码**（scripts/verify_bst_sw_sequence.py = 24,964 B / 17092fea…1d54c78，只读核实）：选靶判据是 derive_targets() L100-L101 的 **
ampi_capv( 行为自证**；拓扑由 SetOn 内 K_FPVIH_TO_PGND(LS)/K_FPVIH_TO_PMID(HS) 判定，判不出则 WARN 跳过（L106-L112）；**targets 为空即空 PASS 提前 return**（L497-L499），此后的契约闭集断言（L503-L523）与 targets 同域。
- **新推论（INFERENCE）**：TM600/TM601 是 RDSON/iset 直流项、无 
ampi_capv( ⇒ **不在 targets 内** ⇒ 现行 st-sw 门对它们**既不报红也不构成通过证据**。这与「t54 报部署态 TM600 缺 [48,76] 为 NEW-RED」需要另行解释（改契约期望集后仍红）不矛盾，但**不能**把该门的红/绿直接当这两项的签署证据。
- **UNKNOWN 归口 t11**：check_contract_closures 的 
esolve_scope()/check_extra 是否会额外纳入 TM600/TM601（本次只读主流程，未读完 L248-L470）⇒ 跑门禁时必须核对 [scan] targets=N 与 [t30] 生效范围（--list-scope），**禁止把 targets=0 的空 PASS 记为绿**。
- 另：高影响建议「TM600 PMID=5 V（裁 A1）」的**独立对抗性复核**已派出（子代理 6fe11f3f-94c7-43f6-bb9b-f020acc73fa5），产物拟落 
eview/independent-review-pmid-ruling.md；在回收前该建议一律标 **provisional**。
- 边界：未改任何脚本、未运行门禁；devel 零写入；目标树 469,714 B / 15c7d2b8… 未落盘。


## 2026-09-16 23:2x +0800 自我更正 #2 + 门禁实跑判据（含假绿陷阱）

- 新增 `inputs/gate-invocation-notes-addendum-2.md` = 6015 B / `80b32b1d9d127b69cf5569c5f0c6249e9c40738ee761181670b97cc89f16a16b`。**撤回补遗 1 的 I-1**（「TM600/TM601 不在 bst-sw 门作用域」）——被实跑推翻。
- **实际机制**：`verify_bst_sw_sequence.py:259` `DEFAULT_TM_SCOPE=["TM600_HS_RDSON","TM601_LS_RDSON"]`；`check_contract_closures()` L429-L467 对 scope 内每个函数做「契约期望集 − payload SetOn 集」的闭集断言（**致命通道**），判据 = `aliasResolution[*].resolution.closedRelayNumbers`（L261-L263）；契约路径 `--contract`(L277-L284)；读不到契约 = 红(L505-L507)。该断言在 `targets` 之外独立执行。
- **实跑（只读；命令与逐字输出见补遗 2 §3）**：部署态 `15c7d2b8…` + 冻结契约 rev36 ⇒ `TM600_HS_RDSON` 期望 `[48,60,61,76,83]` 缺失 `[48,76]`；`TM601_LS_RDSON` 期望 `[60,61,154,155]` 缺失 `[]`；`targets=4 FAIL=2`；exit=1。附带确立：**部署态 TM600 的实际闭合集连 K109/K110 都没有**（仅漏腿，与 t48 记载一致）。
- **新事实（对 t6 重要）**：冻结契约下 **TM601 的期望集只有 `[60,61,154,155]`，无任何 BST 要求** ⇒ 门禁层面「TM601 BST=5 V」当前**无约束**；不经 `t6` 登记就永远不会被检查。
- **新陷阱（实测）**：拿**只含增量的候选 payload 文件**当 `--src` ⇒ `targets=[]` ⇒ 在契约闭集断言**之前** `return 0` ⇒ **假绿**（命令 B 输出「空 PASS」，exit=0）。⇒ `t9/t11` 硬要求：`--src` 必须是**等价全量源文件**，且必须同时在场 `[scan] targets=N (N>0)` 与两行 `[t30]`；**空 PASS 记为「未执行」，不得记为通过**。
- 独立复核子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5` 仍在跑（`review/independent-review-pmid-ruling.md` 尚未出现）⇒ 裁 A1 继续标 **provisional**。
- **另一 run 的活跃写入再次实测**：`acceptance-20260916-dali10/setup-contract.json` 由 377,128 B 变 377,276 B（本会话第三次观测到旧目录漂移）⇒ 冻结副本（376,308 B / `d9ecffb0…`）是本 run 唯一输入，继续有效。
- 边界：未改任何脚本；**未运行完整 `run_gates.ps1`**（只跑本门脚本的只读断言）；未写目标树/devel；**非电性结论**。


## 2026-09-16 23:4x +0800 BST 节点源表（物理事实）+ B 项降级修正

- 新增 `bst-node-source-table.md` = 7538 B / `0b17bc652745802d77f806e21ea4169b20e0ac65b69405b599cea0c2f19e2a26`。来源 pin：`project/DALI/SCH-Connect-Map.txt` = 66,403 B / `cc8009fb…83cb427`（966 行）；`knowledge/hardware/relays.md` = 13,624 B / `8029ee13…1934fcdb`（246 行）。
- **BST 节点 8 条来路（逐行 locator）**：① ACM200 ch5 `K48,K76`（SCH:672-674）② FPVIe CH0-High `K46,K48,K76`（39-41）③ FPVIe CH0-Low `K109,K110,K138,K139,K145,K146`（42-44）④ S10_CH0_A `K141,K46,K48,K76`（461）⑤ QVM 高端 `K137,K46,K48,K76`（536）⑥ QVM 低端 `K109,K110,K139`（538）⑦ FPVIe CH1-High `K131,K132,K134,K135`（265-267）⑧ FPVIe CH1-Low `K109,K110`（268-270）。
- **多源互斥的具体形态**：ACM200 在 BST 上有两个可达通道 —— ch5 经 `K48/K76`、ch18 经 `K110` ⇒ 同一时刻只能选一路。连同「漏闭 K48 ⇒ 改道到 SW1/SW2 而非开路」（t47 结论），ch5 的三目的地天然互斥。
- **继电器语义（FACT, relays.md）**：`K46~K59` 列为 **MOS P2P，默认断开**（`relays.md:99`）；Share 继电器释放=通默认通道（`:96`）；BUS 释放=不通（`:95`）。⇒ **来路②④⑤要经 K46（默认断开=开路）**，来路①不经 K46（释放即改道）。**t48「显式 RELAY_OFF 配对非承重」的作用域应限定为来路①**。
- **B 项降级修正（对我上一轮措辞的实质更正）**：先前景象「BST=5 V」与「BST−SW=5 V」被我当作互相矛盾；实算后：LS 导通加 1 A 时 `V(SW)≈7.5 mV`，故 **BST=5 V（单端）⇒ BST−SW≈4.99 V**，两种读法在数值上几乎等价。⇒ 二者应视为**同一物理意图的两种说法**，真正待定的是「BST 由哪一路源驱动」与是否需要 `bst_sw` 差分行。工作簿 `AH133` 的 `SW-PGND=0.3`（无单位）**不足以定标**（与 7.5 mΩ 限值算术不自洽，子代理亦判其非限值列）。
- **待复核张力**：`relays.md:99` 把 K48/K49 列为 P2P(MOS)，但别处按 Share/BUS 使用（`:96/:95/:105-108`）⇒ 该归类由 `t2` 用端子图/网表定案，本汇编只按字面转述。
- 独立复核子代理 `6fe11f3f-…` 仍在跑 ⇒ 裁 A1 维持 **provisional**。
- 边界：未改脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 469,714 B / `15c7d2b8…` 未变；非电性结论。


## 2026-09-16 23:5x +0800 A 项证据：已部署实现反证「15 V 台阶在 PMID=5 V 下成立」

- 新增 `pmid-operating-point-evidence.md` = 6454 B / `632ea15462e232cfaaf4455d7ffd03ae161d7c4846ca8ddb39621de0ead66844`（证据源 = 部署态 `test.cpp` 469,714 B / `15c7d2b8…`，只读；函数体按 `DUT_API int <Name>(short funcindex` 定界，未用「最近前置 DUT_API」错法）。
- **FACT（TM600 L9057-9216）**：`:9086` 注释写 `PMID 15 V, VBAT 4.2 V`；`:9097-9115` 是 `SW12_U1REF_BST_ACM`（0→5→10→15→20 V）与 `PMID_HG2_FXVI`（0→5→10→15 V）**交替**的 BST−SW=5 V 台阶；`:9114` 终态 = PMID 15 V / BST 20 V。`:9081` 的 SetOn 只有 7 个继电器（无 K48/K76），与门禁实跑「缺失 [48,76]」一致。
- **FACT（TM640 L7503-7605）**：`:7492` 的 DFT 行 `vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5]` **与新版 TM600 DFT 逐字相同**；`:7521/:7526` 用 ACM200 10 V/100 MA 两步（`Set(FV,5)` 当 SW=0、`Set(FV,10)` 当 SW=5）实现 BST−SW=5 V；`:7513` 闭集含 `K48_ACM5_AMP_REF, K76_ACM_BST`。⇒ **本板既有「PMID=5 V + BST−SW=5 V」的已部署先例**。
- **FACT（TM601 L9217-9353）**：`:9269` `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON)` ⇒ **部署态 TM601 本来就在驱动 BST=5 V**。**更正旧 run 叙事**：「TM601 无 BST / 已移除 ACM 激励」与部署态代码不符；其 SetOn 只是未闭 K48/K76。
- **INFERENCE（裁 A 判定，强证据但未独立复核）**：A2（15 V）在算术上自我矛盾——把 15 V 台阶（PMID 5→10→15 与 BST 10→15→20）套到 PMID=5 V 的操作点会得到 **20 V BST** 且台阶注释自身要求 step4=PMID 15 V；A1（PMID=5 V + BST−SW=5 V）与 `TM640` 先例一致。⇒ 建议裁定：以新版 DFT 的 5 V 操作点为准，`voltage-inference.md` 的 15 V 台阶标注为**已部署的另一种工况**并保留；**不许拼用**。
- **证据强度声明**：TM640/TM600 的代码事实=强；「串台阶产生 20 V」=由注释推得（中，未实测）。
- **独立复核状态**：子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5` 仍在运行；其任务书只给了 A1 的原始理由，**未包含本条的代码级反证** ⇒ 结论标「强证据、未独立复核」，终判由 `t8` + 用户收口。
- 边界：只读；未改任何文件；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；非电性结论。


## 2026-09-17 00:0x +0800 BST 供给资源事实 + TM601 通路缺失的代码级证据

- 新增 `bst-supply-resource-notes.md` = 5981 B / `3f1aae0588b973832101b322f535177381dc2544d729fa425c2883e90bf7b52e`。
- **FACT（TM601）**：部署态唯一 `cbite.SetOn` 在 `test.cpp:9255`，逐字为 `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` ⇒ **不含 K48/K76/K46/K49/K109/K110**；而 `:9269` 却把 ch5 `Set(FV,5,ACM200_10V,100MA,RELAY_ON)` ⇒ **源设了 5 V 但没有闭合到 BST 的通路**，BST=5 V 到不了 BST 节点。`:9246` 既有注释亦写明 SW1 需 K46、SW2 需 K46+K49，与 SW 是不同节点。
- **FACT（TM600 栅格）**：`:9081` 闭集 = K83(PMID) + K60/K61(SW) + K13/K85/K57/K126(cap)，**缺 K48/K76** ⇒ 与门禁实跑「缺失 [48,76]」一致。
- **FACT（ch5 归属）**：驱动性 `.Set` 见 TM607(:7008)/TM608(:7096,7100)/TM609(:7179,7184)/TM640(:7521,7526)/TM600(:9097-9115)/TM601(:9269)；`TM641/643` 注释 `:7598/:7621/:7714` 逐字写「K48/K76 把 ch5 输出接 BST ⇒ 该源全程 RELAY_OFF 不驱动」，即**多源互斥与显式释放的既有先例**。
- **FACT（ch18）**：`PB0_BST_ACM` 的实际用途是 **PWM1/PB0 引脚测量**（`:5003/5022/5026/5041/5045`、`:5185-5199` 含 `MeasureVI(50,5)`+`MIRET`；`:4994/5160` 注释 `default NC`）⇒ ch18 当 BST 供电源需另证（交 `t2`）。
- **INFERENCE**：新版 TM600 的 5 V 工况形状由部署态 TM640 给出（`:7521` BST=5、SW=0 → `:7524` PMID=5 → `:7526` BST=10、BST-SW=5），且 `:7513` 同时闭 `K48,K76`；沿用 15 V 台阶在 5 V 工况下会得 BST-SW=15 V，与门禁自身规则 `0<=BST-SW<=5V`（`:545`）冲突 ⇒ 支持 A1。
- **自我更正（第 5 次）**：我曾据被 `Select-Object -First` 截断的输出推测「部署态 TM600 不含 `PMID_HG2_FXVI.Set`」——**撤回**；普查为 59 处、`.Set` 51 处，TM600 体内确有（`:9102/9107/9112` 等）。
- 未改任何文件；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；非电性结论。


## 2026-09-17 00:2x +0800 验证前置（复核拦截清单）

- 新增 `verification-prerequisites.md` = 4849 B / `8db21b4c10a6099c520f6ec2ffa32166d09171f0e59af162e84e94ad7eb119b3`：把本轮确立的可执行判据、6 个必须由 owner 回答的拦截问题（Q1-Q6）、以及解锁后按序可跑的只读校验整理成清单。
- 关键拦截项：**Q3** `relays.md:99`（K46~K59 归 MOS P2P）与 `:96/:105-108`（Share/BUS 归类）**存在张力**，决定「释放=开路」还是「释放=改道」；**Q6** 门禁对 TM600 的期望集 `[48,60,61,76,83]` 是 pmid2sw+bst2sw 两支合并的结果，须由 `t6/t8` 确认是否含「契约提及但实现不该闭」的腿。
- 新增独立对抗性复核子代理 `e1aec5f2-6281-41ae-a132-0c3497358439`（同模型路由），任务书**带上本轮全部代码级事实**并要求逐条 CONFIRMED/PARTLY/REFUTED + 找反证；产物拟落 `review/independent-review-r7-findings.md`。前一个复核 `6fe11f3f-…` 仍在跑。
- 边界：只读；未改脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；非电性结论。


## 2026-09-17 00:4x +0800 独立复核回收（DISAGREE）+ 三项被迫撤回

- 复核件 `review/independent-review-pmid-ruling.md` = 28221 B / `533e71b99f74a7249c3d193b1a1eca7232861b3fd2cfee3ec3007671035978c8`（子代理 `6fe11f3f-…`，deepseek-v4-flash 路由，独立执行）。Captain 回执 = `review/captain-recovery-r8-independent-review.md` = 6223 B / `b2e6507547d91427faa6b2ea78c5b23f11c04145f00eba190771468079c1bd45`。
- **裁定：DISAGREE with Ruling A1 as written** —— 方向（5 V）大概对，但**论证是 non-sequitur**、权威面不完整、**字面执行最危险**。
- **撤回 1**：「沿用 15 V 台阶会得 BST−SW=15 V ⇒ 支持 A1」。根因：部署态 TM600 `:9081` **从未闭 K48/K76** ⇒ 20 V 台阶**未被证明到达 BST**，故该论证前提不成立；且不能用 TM640 反推 TM600 形状，因为同文件 `:9027-9028` 又声称「ACM200 reaches SW only and cannot reach BST」，**与 `SCH-Connect-Map.txt:672-674` 直接矛盾**（四方不一致：契约/门禁/已部署代码/注释）。
- **撤回 2（降级）**：「把 `voltage-inference.md` 的 15 V 台阶标为另一工况即可」不充分 —— 复核实测该文档 `:142-143` 是**逐字转录 DFT.csv**，而 DFT.csv（`b92d203f…`，现盘未变）是**契约明确引用的权威输入**（bst2sw:92 / pmid2sw:97）⇒ 改标记退役不了 15 V；差异是**四个耦合字段**（PMID 5/15、VBAT 3.5/4.2、iset[sw] vs iset[pmid2sw]、限值 11/10 mΩ），不能只挑一个。
- **撤回 3（限定作用域）**：「BST=5 V 与 BST−SW=5 V 数值等价」**只在 TM601（SW≈0）成立**；对 TM600（SW 跟随 PMID 到 5 V），BST−SW=5 V 要求 **BST 绝对值=10 V**（部署态 TM640 `:7521/:7526/:7566` 即此形状）；字面「BST=5 V」⇒ BST−SW=0 ⇒ FET 不导通 + 0.5 V clamp ⇒ **100% 假失败**。
- **抽查确认的复核引用（我实测）**：见证件 `overview-dft.json`（自记 xlsx `d9d721a3…`）**改动前 TM600 已是 `vset[pmid,5]` + ExpectValue 11** ⇒ 21:46 那次改动的可见 delta **只在 TM601 行新增 `vset[bst,5,…]`**；`test.cpp:9027-9028` 与 `:9011-9016`（clamp=保护、0.5 V↔500 mΩ）逐字确认。
- **复核新增（我未逐一复核）**：工作簿自相矛盾 —— `AH132` 的 `I=0.2A/pmid-sw=46mV` ⇒ 230 mΩ ≈ 21× 同行 `E132=11 mΩ`；全 VS 树 0 处运行期 `vset()` 调用（235 处皆注释）；BST−SW 上限引 ABS M29/M30/M44/M50 与 `docs/BST-SW通用知识介绍.txt`。
- **阻断 UNKNOWN（U-A…U-F）**：`vset` 语义（无 DFT 工具手册）、K48/K76 默认态、DUT Rds,on vs PMID（无 datasheet）、21:46 改动完整范围、PMID 上 FV+FI 共存性、BST−SW 绝对上限。
- **修正后的建议**：本议题**不是 PMID 二选一**，而是**四字段耦合工况对账**；**更优先的问题是「BST 到底通不通」**（`test.cpp:9027-9028` vs `SCH:672-674` 不能同时为真），它决定既有 20 V 台阶是否真到过 BST；A1 仅保留为**工作假设**，正式结论等第二个复核 `e1aec5f2-…` 回收。
- 边界：只读；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；无硬件验证。


## 2026-09-17 01:0x +0800 四方矛盾消解（R9）：ch5 可达 BST 有四份行为证据

- 新增 `bst-path-resolution-r9.md` = 6053 B / `4f29d428a1226ce0cef822615f0d04ec855c4e5766a08595acb4b4172b6b3971`。
- **事实 A（我实测，逐函数定界）**：闭 K48/K76 **且**驱动 ch5（`Set(FV,>0)`）的函数 = `TM607(6985-7072) / TM608(7073-7159) / TM609(7160-7249) / TM640(7503-7605)`，四个**全部 True**；而 `TM600(9057-9216)` 与 `TM601(9217-9353)` 驱动 ch5 却**都不闭 K48/K76**。⇒ 「本板 ACM200 到不了 BST」**不成立**；TM600/TM601 是**漏闭**。
- **事实 B（消解）**：`test.cpp:9024-9033` 那段「ACM200 reaches SW only and cannot reach BST」**上下文是「黄金案例用两个独立地参考源 BTST_ACM + SW_ACM 拼 BST−SW」的那套安排**，作者在论证「它无法构成一对」；该句是该安排下的陈述，**不是本板硬件限制**。⇒ 我 R8 回执里称「注释与端子图直接矛盾」**属越出上下文的引用，现更正**：两者不矛盾，是那段注释的局部论证被字面扩张。
- **事实 C（对 R8「四字段耦合」的更正）**：`test.cpp:9035-9037` 逐字写明 `「the archived revision pairs 11 / 7.5 mohm with pmid 5 V, while DFT.csv pairs 10 / 8 mohm with pmid 15 / 9 V」` ⇒ 部署态实现者已认定 **11/7.5 mΩ 与 PMID=5 V 是同一套来源**、DFT.csv 的 10/8 与 15/9 V 是另一套。⇒ A 项不是「四个零散冲突字段」，而是**选哪一套来源**；工作簿那套（5 V + 11/7.5）自洽，且与门禁期望集（pmid2sw+bst2sw 并集）取向一致。
- **可执行结论**：① TM600 在 `:9081` 那一次 SetOn 内补 `K48_ACM5_AMP_REF + K76_ACM_BST`（= TM640:7513 形状，正好补齐门禁 missing=[48,76]）；② TM601 要给 BST 腿登记 K48/K76，否则 `:9269` 的 5 V 永远到不了 BST；③ TM600 需 `BST_abs=10 V` 才有 BST−SW=5 V（SW 跟随到 5 V），TM601 单值 5 V 即 BST−SW≈4.99 V；④ 多源互斥须显式释放（TM641/643 先例 `:7598/:7621/:7714`）。
- **仍未证实**：K48/K76 的实际物理贯通（需台架/端子测量）、`vset` 权威语义、PMID 上 FV+FI 共存性、部署态 20 V 台阶是否真的到过 BST（未闭腿 ⇒ 大概率未到达，但属 INFERENCE）；第二个复核 `e1aec5f2-…` 尚未回收。
- 边界：只读；未改脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；无机台验证。


## 2026-09-17 01:2x +0800 沙箱实证：TM600 补 K48/K76 使门禁契约断言由红转绿

- 新增 `sandbox-fix-verification.md` = 3418 B / `af16a10bcaa00ba40cc26c637d3daddaf668a8dad91fb72230dc76c303ef808c`；脚本 `sandbox_fix_test.py`；结果 `sandbox/fix-test-result.json` = 1986 B / `5e633bf59e3e3b71cbcbca9539adf97909b7896c4739775e09e4517402b3cb33`。
- **方法**：逐字节复制目标树到 `sandbox/test.cpp.copy`（= 原件 `15c7d2b8…`），仅在 TM600 那一次 SetOn 内追加 `K48_ACM5_AMP_REF, K76_ACM_BST`（锚点唯一，脚本内 assert n==1），产出 `sandbox/test.cpp.k48k76` = 469745 B / `fab6262b32013154ad84dbf381b62936706c7c6804dd11fd5bedf8c9b5d703dd`（+31 B）。
- **结果（逐字）**：用例 A（未编辑）`TM600 缺失=[48,76]`、`targets=4 FAIL=2`、exit **1**；用例 B（加两腿）`TM600 缺失=[]`、`FAIL=0`、输出 `BST-SW SEQUENCE PASSED`、exit **0**。
- **结论 1**：该修法**在沙箱内被实证**可使契约闭集断言转绿（非预测）。
- **结论 2（重要限制）**：该门**只校验闭集、不校验阶梯** —— BST 源设 5 V / 10 V / 20 V 都不影响本门红绿 ⇒ **门禁绿 ≠ 操作点正确**，V 值与阶梯必须由 `t7` 计划 + `t8` 独立审查 + 台架签核保证。
- **结论 3**：本门只做文本集合比对，**不证明 K48/K76 的实际物理贯通**；TM601 因其契约闭集不含 BST 腿，该门对 TM601 的 BST 供给**仍无约束**，须经 `t6` 修订后才有效。
- **边界**：目标树 `15c7d2b8…` 与 `devel `5c9cb3f9…` 前后哈希不变（实测）；沙箱副本仅存在于本 run 目录；未改门禁脚本/契约/计划；无机台验证。
