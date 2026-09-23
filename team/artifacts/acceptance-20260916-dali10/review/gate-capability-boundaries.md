# 门禁能力边界（gate capability boundaries）—— 只读复核产物

- 作者：rule-reviewer（独立复核方）· 日期：2026-09-16 · run `acceptance-20260916-dali10`
- 用途：供 **`t34`（最终集成验收，替代悬空旧 `t9`）直接引用**，作为"**门禁绿 ≠ 电性正确**"的必录限制项证据。
- 取证纪律：内容断言只用 **python / grep 工具**；所有哈希为 **python-plaintext sha256**；**未使用 pwsh 读取受保护源码做断言**（原因见 B-1）。
- 只读声明：本文件为新增评审产物，**未修改任何被审对象**。

## 0. 使用说明（给 t34）

本清单列出**五条已在本 run 中被实测证实的门禁能力边界**。每条给：
**(能证明什么 / 不能证明什么 / 需要什么额外断言)**，并附**可复现命令**与**locator**。
请勿把"门禁 exit 0"读作"电路实现正确"；下列每一条都对应一个**已被证实的假绿或假红**。

---

## B-1 DLP 读取不对称：命令壳的 .NET 路径读到**密文**，必然 0 命中（假阴性）

**能证明什么**：在**授权读取路径**上（python / node 托管检索工具），被保护文件的**明文内容**可被正确断言。
**不能证明什么**：**任何**用 pwsh `Select-String` / `Get-Content` / `Get-FileHash` / `.NET File.*` 对受保护文件做出的"不存在 / 无匹配 / 哈希为 X"结论 —— 这些读到的是**未授权视图**，**必然给出假阴性/假哈希**。

**实测证据（同一文件、同一时刻、两种读者）**：
| 对象 | python（授权） | pwsh `.NET`（未授权） |
|---|---|---|
| `ForCodexDebug/source/test.cpp` | 434,629 B，**NULs=0**，首16 = `ef bb bf 2f 2a 2a…` | 434,629 B，**NULs=2055**，首16 = `54 53 5a 23 05 90 07 0e…`（`TSZ#`） |
| `artifacts/.../test-plan.json` | 136,263 B，NULs=0，`{\n  "run` | 136,263 B，**NULs=648**，`TSZ#` |
| `project/DALI/input/DFT.csv` | 16,862 B，NULs=0，sha256 `b92d203f…` | 16,862 B，NULs=278，`Get-FileHash` = `c87e6015…`（**≠** python 值） |
| 非保护对照（`run_gates.ps1`） | 与 .NET 视图**一致** | 一致 ⇒ 差异**由文件是否受保护**引起，非 pwsh 本身 |

**授权读者判定（实测）**：`grep` 工具搜 `test-plan.json` 的 `QVM` = **4 处（行 27/2322/2542/2543）**，与 python 明文 **4 处、行号一致** ⇒ **grep 工具与 python 同为授权读者**；受保护树上**只有 pwsh 的 .NET 路径未授权**。
**零成本预筛**：python 读首 4KB，**NULs=0 ⇒ 该文件有明文视图**。⚠️ **但预筛干净不能证明"不存在保护层"**（保护**按读者**生效，不按文件）。

**需要的额外断言**：① 内容断言必须**标注取证工具**（python / grep）；② 哈希必须**python 现算 + mtime**，并**确认该哈希对应盘上实际存在的文件**；③ 禁止 pwsh 对受保护树做内容或哈希断言。

---

## B-2 `bst-sw` 门禁**不比对"闭合集合"**，因此看不见"该闭的继电器没闭"（假绿）

**能证明什么**：① **BST 源与台阶**：`SW12_U1REF_BST_ACM` 的 0 V 初始化、power-on 的 `0→5→10`、power-off 的 `10→5→0` 是否按次数出现（`verify_bst_sw_sequence.py:199-231`，`require_exact_count`）；② **BST 电容继电器仅在**：`if BST_SRC in block: … if seton is None or BST_CAP_RELAY not in seton.group(1): errors.append("missing BST-SW differential capacitor relay K57_CAP_BST_SW")`（`:270-276`）。
**不能证明什么**：**它不检查该函数是否闭齐了契约要求的继电器。** 实测该文件内 `K110`=**0**、`110`=**0**、`needsClosed`=**0**、`relaySet`=**0** 命中 ⇒ 它**从不读契约的 `needsClosed`/`relaySet`，也从不校验 `SetOn` 的内容集合**（只在 `:272` 取出 SetOn 后**仅**判断有无 `K57`）。

**由此产生的真实假绿（本 run 主证据）**：v20 与契约 rev24 均要求 TM600 的 BST−SW 闭合集合 **`[110, 61]`**（`items[TM600].assumptions[0]`、`R-BST-SW`；契约 `/aliasResolution[3].resolution.closedRelayNumbers[0]=110`、`bstRuling_ii`、`/tmDeltas/TM600/relaySet` 含 110、`pinRouteTable.BST CH1 Low needsClosed=[110]`），而现盘 `test.cpp`（469,714 B / `15c7d2b8…`）TM600 段内 **`K109`=0、`K110`=0**，只闭到 `K61_ACM8_SW` ⇒ **`[110]` 未落地**。`K110` 为**双掷**：不动作时按 `Relay-NC` 把 BST 接向 **`PB0`**（`SCH-Connect-Map.txt` L724/L725 `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`；L109/L110 同）⇒ **AC 源到不了 BST，裁定 (ii) 的接地参考激励不成立**。
**该门仍报 `BST-SW SEQUENCE PASSED`** —— 因为它只看"源与台阶"，不看"闭合集合"。

**需要的额外断言**：新增"**SetOn 集合 vs 契约 `needsClosed`**"断言：对每个被驱动 PIN，读契约 `pinRouteTable.<PIN>.*.needsClosed`（及 `aliasResolution[*].resolution.closedRelayNumbers`），要求**该函数 SetOn 集合 ⊇ 该路径 needsClosed**；**断言必须泛化**（不得硬编码 `[110,61]` 或 TM600 特例），**失败信息含 file:line**，并附**全树 A/B 证明无误报**。**验收必须含阳性对照**：修复落盘前对 TM600 缺 `K110` **报红**，落盘后转绿（**该阳性对照应由独立复核方在只读沙箱重放，不采信自述**）。

---

## B-3 `input-sync` 只比对**戳相等**，**检不出"修正被重生成抹掉"**（假绿）

**能证明什么**：**戳一致性** —— `check_input_sync.py:13-14` 定义两对：`meta._syncStamp.dftSha256 == sha256(DFT)` 与 `yaml._sync.metaSha256 == sha256(meta)`。即它证实"yaml 的戳与当前 meta 字节一致"。
**不能证明什么**：**"修正是否仍然生效"。** 实测：重跑 `gen_testitems_meta.py` 会**逐字节还原**改动前的 meta（探针 `t26-regen-probe/dali_tm_meta.regen.json` = 146,180 B / `1c849664…`，**与改动前逐字节相同**），**抹掉 TM600/TM601 的三项 run 级修正**（TM601 的 `vset vbus` 与 `powered_pins.VBUS` 全部回归、两项 `mi_pins` 回空）；而 **yaml 的 `_sync.metaSha256` 戳会随生成同步刷新** ⇒ **该门仍报 `INPUT SYNC: **IN SYNC**`**。⇒ **门禁全绿也无法发现"修正已被静默抹除"。**

**需要的额外断言**（规格已由 t26 写入 `recommendedGateAssertions`，`RS-1..RS-4`，可直接实现）：**RS-1** `TM601 powered_pins ∌ VBUS`；**RS-2** `TM600 mi_pins ∋ SW` 且 `TM601 mi_pins ∋ {PMID_SW, SW}`；**RS-3** 两函数 `hardwareInit` vset == 冻结 ATE（`4.2/15/5/5` 与 `4.2/9/5`）且无 `vbus`；**RS-4** `yaml._sync.metaSha256 == sha256(meta)`（**现已生效但单独不足** —— 因戳随生成刷新）。
**阳性对照要求**：用**探针**制造回退（探针文件落 run 目录、**不覆盖 live meta**），断言必须**变红**；否则该断言对"静默抹除"无效。

---

## B-4 `relay-trace` 的 FR-001 发现是 **WARNING**，不是 ERROR；**调用未启用 `--warn-as-error`**（分类易被误读）

**能证明什么**：FR-001 反向发现会**被报告**（`verify_relay_trace.py:359` 走 `warns.append`）；而"虚构继电器名 / 冗余 / 虚构通路 / 功能规则违反"等走 `errors.append`（`:331/:374/:384/:406`）⇒ 只有 **errors** 触发 `sys.exit(1)`（`:451`；另 `:454` 为 `--warn-as-error` 分支）。
**不能证明什么**：**"FR-001 干净"不等于"电容闭合集合正确"。** 实测 `run_gates.ps1:80` 的调用为 `verify_relay_trace.py --meta`，**未带 `--warn-as-error`** ⇒ **warns 不会使该门变红**。故本 run 中"relay-trace 的 4 条电容发现"**本身不是致红原因**；当初的 exit 1 由**另两条 `虚构继电器名 126`（errors）**产生。
**另需注意**：该门的通过条件里还有 `L354`「已闭其 Cap → continue」**先于** `L356` 豁免判定 ⇒ **TM600 的 K57 要求曾被"已闭合"掩盖**（t26 F1 的机制）。

**需要的额外断言**：① 台账须把 **WARNING / ERROR / 致命** 三类**分列**，不得把 warning 当作致红原因（或明确 `--warn-as-error` 是否启用）；② 若某类 warn 应具阻断力，必须在调用参数中显式启用并登记。

---

## B-5 `run_gates` 的红门分类**依赖一次基线读取**；读失败 ⇒ **一切红门被判 NEW-RED**

**能证明什么**：`run_gates.ps1:87-97` 经 `Read-JsonViaPython` 读 `scripts/gate_baseline.json`（明文 28 B `{"cbit": true}`），据此在 `:121-123` 判定 `KNOWN-RED` / `NEW-RED`；总体退出码在 `:139`/`:181`：**仅当存在 `NEW-RED`（或 build 失败）时 `exit 1`**。
**不能证明什么**：**"KNOWN-RED" 的正确性依赖该 28 B 基线被正确读出。** 若基线读失败（如历史上 pwsh 读到 8192 B 密文容器 `%TSD-Header-###%`），`:94-95` 只打印 WARN、`$baseline` 为空 ⇒ **所有红门被判 NEW-RED**，从而**虚增新增红**；同时 `$stdafx` 为空会**静默跳过 `cbit` 门**（`:69`，fail-open：门**消失**而**不变红**）。

**需要的额外断言**：① 基线读取失败应**显式失败**（而非仅 WARN + 全量 NEW-RED）；② `cbit` 等依赖外部输入的门应把"输入缺失"记为**失败**而非**跳过**；③ 日志须记录本次判定所依据的基线哈希。

---

## 附：本清单三条核心结论（供 t34 直接引用）

1. **门禁绿 ≠ 电性正确**：`bst-sw` 报 PASS 的同时，裁定 (ii) 要求的 `K109/K110` **在实现中完全缺失**（B-2）。
2. **门禁绿 ≠ 记录仍然有效**：重生成会逐字节抹掉 run 级 meta 修正，而 `input-sync` 仍报 IN SYNC（B-3）。
3. **"0 命中" ≠ "不存在"**：受保护树上 pwsh 的 .NET 路径**必然** 0 命中/假哈希（B-1）；同理 `bst-sw` 对 `K110` 的 0 命中**不是"K110 不被使用"的证据**，而是"该门不查它"的证据。

**可复现命令（授权读者 = python / grep 工具）**：
```text
python -c "import pathlib;print(pathlib.Path(r'team/artifacts/acceptance-20260916-dali10/test-plan.json').read_text(encoding='utf-8').count('SW12_U1REF_BST_ACM'))"   # 期望 3
python -c "import pathlib,hashlib;p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp';b=pathlib.Path(p).read_bytes();print(len(b),hashlib.sha256(b).hexdigest())"
# grep 工具：在 test-plan.json 内检索 QVM -> 期望 4 处（行 27/2322/2542/2543）
```

**关联证据文件**：`review/t26-tp20-k110-finding.md`（B-2）、`review/t26-correction-5-acceptance.md` / `-6-increment-acceptance.md` / `-8-confirmation.md`（B-3、RS 规格）、`review/forensics-method.md`（B-1）、`review/t25-independent-opinion.md`（B-4/B-5 的门禁改动复核）、**`review/t30-independent-opinion.md`（B-6）**。

---

## B-6 由契约**派生**的断言：其覆盖上限＝**契约登记的完整性**（缺项即静默盲区；错项即误报）

- **来源**：t30 为 `bst-sw` 增加"`SetOn` 集合 vs 契约声明闭合集合"断言（`verify_bst_sw_sequence.py` 24,964 B / `17092fea…`），期望值全部读 `setup-contract.json` 的 `aliasResolution[*].resolution.closedRelayNumbers`。**该修法本身正确**（已由本复核 ACCEPT），但引入一条**新的能力边界**。
- **能证明什么**：**当契约把某函数的闭合集合登记正确时**，该断言能发现"**实现少闭了必需继电器**"（t30 的阳性对照正是此类：TM600 缺 `110` ⇒ `FAIL=1` ⇒ exit 1 ⇒ NEW-RED）。
- **不能证明什么**：**它无法发现"契约自身登记有误"的情况。** 两类实证：
  1. **登记漏项 → 静默盲区**：`tmDeltas.TM600.aliasesUsed = ['pmid2sw']` **漏登记 `bst2sw`**（实测）。若断言以 `aliasesUsed` 为索引，**TM600 的 K110 缺口依旧不可见** —— 与 B-2 的原始盲区同形。t30 改以 `aliasResolution[bst2sw].usedByTm` 为主索引**规避了**这一点（判定可接受），但**根因仍在契约里**。
  2. **登记错项 → 误报**：`bst2sw.usedByTm` 含 **`TM1205 (BST1-SW1 / BST2-SW2 ramps)`**，而 TM1205 实际闭的是**自己的 path 别名**（`K_FPVIH_TO_SW1_A=46` / `K_FPVIL_TO_BST1_A=41`）且 `aliasesUsed = []`（实测）⇒ 若把断言范围扩到全量，会**对 TM1205 报 `缺失=[61,110]`**，而这是**契约登记不对称**造成的，不是实现缺陷。
  3. 同类：`K109` 的"可能多闭"**无法由契约派生断言解决**，因为契约**本就把 `109` 写进了 `relaySet` 与 `pinRouteTable…CH0 Low.needsClosed`**（t35 归口项）。
- **需要的额外要求**：① 断言以**契约登记**为源时，必须同时输出**本次检查范围**（t30 已满足：源码 `L514` 打印作用范围）；② 契约侧须**消除登记不对称**（补 `aliasesUsed`、修正 `usedByTm`、为被判定的路线建立独立别名）—— **属契约任务，不属门禁任务**；③ `t34` 引用时应与 **B-2** 并列，并注明"**B-2 已由 t30 部分修复，但按 B-6 其覆盖仍受契约登记质量约束**"。

