# TM108 — DFT 侧 DTEST0 观测端点证据：OI-T4-01 解析报告（仅 TM108）

- runId: `tm108-v2-trial` · task: `t6` · owner: **dft-expert** · date: 2026-09-17
- 产物（本任务唯一写入范围 `team/artifacts/tm108-v2-trial/dft/`）：
  `dtest0-oi-t4-01-resolution.md`
- 只读输入：t2 DFT 事实审计、当前 DFT 三件套、`project/DALI/input/` 与 `project/DALI/_archive/`
  的纯文本 DFT 证据、`project/DALI/reg_config/`、冻结 Setup 基线（只读）。
- **未改写任何项目产物**：`project/DALI/**` 全程只读；`D:/PROJECT6-DALI/devel` 未访问。
  本报告 §5 提出的任何改动都**只作提案**，留在授权之后。
- 范围：仅 TM108；不涉及任何其他 TM。

---

## Ruling

**结论一（DTEST0 语义，DFT 侧可确立）**：`DTEST0` 在 DFT 侧**不是外接 PAD 名**，而是**芯片内部数字
mux（DMUX / Reg_DTEST0）的总线名**——DFT 用它表示"把选中的内部数字信号经 DMUX 送到数字观测 PAD"。
证据：`DTEST0` 不出现在项目 PAD 清单 `project/DALI/input/PINLIST.txt:1-39`（39 行 PAD 名，含 `INT`），
而 DFT 自己的 pin-map sheet 把它登记为"Digital Test"列的值
（`project/DALI/_archive/_dump_TestIO.txt:1-2`）；DMUX 侧它对应寄存器 `Reg_DTEST0_general`
（`project/DALI/_archive/_dump_DTESTMAP.txt:1`）。DFT 三件套本身对 TM108 只记录
`check = V(DTEST0)`（`project/DALI/meta/dali_tm_meta.json:1402`、`project/DALI/meta/test_conditions.yaml:267`），
不含任何 PAD 绑定。

**结论二（DTEST0 → nQON 关系：可确立，但不是由当前三件套确立）**：DFT 工作簿自己的 pin-map sheet
`TestIO` 把 `DTEST0` 绑到物理 PAD `nQON`：
`project/DALI/_archive/_dump_TestIO.txt:2` = `nQON  <Analog空>  DTEST0  SCAN_OUT`；
`DTEST0` 不在 PAD 清单里（`project/DALI/input/PINLIST.txt:1-39`），而 `nQON` 是唯一的
"Digital Test = DTEST0" 载体。故 **`DTEST0`(内部数字 mux 总线) → `nQON`(PAD) 的关系成立**，
DD 的语义边界是"DUT 上可观测的物理端子 = `nQON`"。该项在冻结 Setup 基线与实现层同样成立：
`team/artifacts/acceptance-20260916-dali10/setup-contract.json:5666-5671`、
`team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt:395`。

**结论三（何处定义 check pin / test-bus mapping：已定位到确切来源）**：定义者是**当前 DFT 工作簿
`Dali_testmode.xlsx` 的两个 sheet**，而不是三件套：
- `TestIO`（PAD ↔ ATEST/DTEST/SCAN 绑定）—— **本次输入工作簿中该 sheet 存在且 7 行**
  （`project/DALI/meta/manifest.json:60`），与归档快照 `_dump_TestIO.txt` 的 7 行一致
  （`project/DALI/_archive/_dump_TestIO.txt:1-7`）。
- `DTESTMAP`（`Reg_DTEST0_general` 的 mux 索引 → A2D 信号，75 行）
  —— 本次工作簿中 **75 行**（`project/DALI/meta/manifest.json:63`），与
  `project/DALI/_archive/_dump_DTESTMAP.txt:1-75` 的 75 行一致。

**结论四（DTEST0 是否由 DFT 证据单独识别出可观测端子：是，但带一条限定）**：
DFT 源**能**识别出唯一可观测物理端子 `nQON`（结论二），该识别来自 DFT 自己的 TestIO 映射，
不是命名推测。**限定**：该映射在**当前三件套里不存在**，当前工作簿中 `TestIO` / `DTESTMAP`
的**单元格内容**没有任何产物携带；我是用同项目归档快照（`_dump_TestIO.txt` / `_dump_DTESTMAP.txt`，
2026-08-06 生成）确认的，其 sheet 行数与当前工作簿声明的行数**逐一对上**（7 行 / 75 行）。
因此：**`DTEST0 → nQON` 判定为已证实（DFT 源 + 行数一致的归档映射）**；
**`DTEST0_MUX` 字段的寄存器位定义**仍为未证实（见结论五）。

**结论五（OI-T4-10 寄存器 mux 冲突：两侧均保留，不平均，且不按位模式反推）**：
`DMUX_SEL` 与 `DTEST0_MUX` 是**两套不同的字段/寄存器**，不能互相当作对方的解码：
- `.sv` / meta / YAML 层：`DMUX_SEL = 22`（`project/DALI/reg_config/tm108.sv:14`、
  `project/DALI/meta/dali_tm_meta.json:1505`、`project/DALI/meta/test_conditions.yaml:261`）
- CSV 层：`field[(EN_DTEST0,1),(DTEST0_MUX,23)]` + `I2CWriteSameData(DEV_ADDR, 0x55, 0x97)`
  （`project/DALI/input/DFT.csv:26`、`team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:50`）
- **独立事实**：`Reg_DTEST0_general` 索引 22 = `a2d_vac1_prst`，索引 23 = `a2d_vbat_uv_ok`
  （`project/DALI/_archive/_dump_DTESTMAP.txt:24`、`:25`）。
- **可核对的规律（仅陈述，不作位模式反推）**：CSV 层 `DTEST0_MUX` 值等于对应
  `DMUX_SEL` 值**加一**——TM108 `23 = 22+1`（`DFT.csv:26`）、TM109 `22 = 21+1`（`DFT.csv:31`）、
  TM110 `21 = 20+1`（`DFT.csv:36`）。该一致偏移提示两字段的定义或编码域不同，
  但**当前可用证据中不存在 `DTEST0_MUX` / `Reg_DTEST0_general` 字段位定义的载体**，
  故 22/23 两侧**均保留、均不单独作为权威**（承 t4 `OI-T4-10`、t2 冲突 F2）。

**一句话总裁定**：`DTEST0` 的可观测物理端子已由 DFT 自己的 TestIO 映射证实为 `nQON`（资源对象
`NQON_HG1_ACM`），故 OI-T4-01 的"关系"部分**可关闭**；但"证据载体"部分**不能关闭**——当前三件套
不含该映射，且 `DTEST0_MUX` 字段定义无载体，故替换为 `OI-T6-02`（见 §6），
并**不**断言任何 PAD 名称是"DTEST0"或"INT"的等价物。

---

## Evidence

| # | 事实 | 证据（path:line） | 类别 |
|---|---|---|---|
| E-1 | TM108 的 DFT check 字段是 `V(DTEST0)` | `project/DALI/meta/dali_tm_meta.json:1402`、`project/DALI/meta/dali_tm_meta.json:1426-1428`、`project/DALI/meta/test_conditions.yaml:267`、`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:161` | 当前三件套 + 证据层 |
| E-2 | DFT Notes 明确"mux A2D_VAC1_PRST to dtest0" | `project/DALI/meta/dali_tm_meta.json:1396`、`project/DALI/meta/test_conditions.yaml:270`、`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:155` | 当前三件套 + 证据层 |
| E-3 | `TestIO` sheet：`nQON` 的 Digital Test = `DTEST0`，SCAN Function = `SCAN_OUT` | `project/DALI/_archive/_dump_TestIO.txt:1-2`（该 sheet 当前存在、7 行：`project/DALI/meta/manifest.json:60`） | 归档 DFT sheet 快照 + 当前行数 |
| E-4 | `DTEST0` 不是 PAD 名；PAD 清单里没有 `DTEST0`，但有 `INT` | `project/DALI/input/PINLIST.txt:1-39`（`:10` = `INT`） | DFT 侧 PAD 清单 |
| E-5 | `Reg_DTEST0_general` 索引 22 = `a2d_vac1_prst` | `project/DALI/_archive/_dump_DTESTMAP.txt:24`（sheet 当前 75 行：`project/DALI/meta/manifest.json:63`） | 归档 DFT sheet 快照 + 当前行数 |
| E-6 | 索引 23 = `a2d_vbat_uv_ok`（不是 VAC1 相关信号） | `project/DALI/_archive/_dump_DTESTMAP.txt:25` | 归档 DFT sheet 快照 |
| E-7 | `.sv` 写 `0x56 = 0x16`（22 / DMUX_SEL）与 `0x57 = 0x08`（DMUX_EN） | `project/DALI/reg_config/tm108.sv:14`、`team/artifacts/acceptance-20260916-dali10/dft-raw/regconfig-scope.json:32-36`、`team/artifacts/acceptance-20260916-dali10/dft-raw/meta-refs-dump.txt:1426-1430` | DFT 生成物 + 证据层 |
| E-8 | meta/YAML 层 `DMUX_EN=1, DMUX_SEL=22` | `project/DALI/meta/dali_tm_meta.json:1499-1508`、`project/DALI/meta/test_conditions.yaml:261` | 当前三件套 |
| E-9 | CSV 层写 `0x55 = 0x97`、`DTEST0_MUX = 23`，`Check = INT` | `project/DALI/input/DFT.csv:25-26`、`:29`、`team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:50`、`:52` | DFT 侧 CSV |
| E-10 | CSV 层同一致偏移：TM108 23/22+1、TM109 22/21+1、TM110 21/20+1 | `project/DALI/input/DFT.csv:26`、`:31`、`:36` | DFT 侧 CSV |
| E-11 | t2 审计已把 22/23 登记为 F2，且未取舍 | `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md:269` | 本 run 前序产物 |
| E-12 | t4 契约把 DTEEST0 端点标为"候选/未证实"，并禁止假定其等于 nQON | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md:98`、`:103`、`:105`、`:111`、`:374` | 本 run 前序产物 |
| E-13 | 实现层把"DTEST0 观测"落到 `nQON`：`NQON_HG1_ACM` + `K65_nQON_PU`，注释写 `measure V(DTEST0)=nQON toggle` | `team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt:395`、`:413-414`、`:429`、`:433-439` | 证据层（应用代码） |
| E-14 | 冻结 Setup 基线同结论：`cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`，并写明 `K21_VAC_Cap must stay open` | `team/artifacts/acceptance-20260916-dali10/setup-contract.json:5666-5671` | 冻结基线（只读） |
| E-15 | 实现侧触发电平 1.65 V 是"nQON 逻辑电平预估"，**DFT 层无该数值** | `team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt:432`、`:436`（DFT 侧仅给出 `deTest r 4.059 / f 3.738`：`project/DALI/meta/dali_tm_meta.json:1417`） | 证据层 + 当前三件套 |
| E-16 | 知识层把 `DTEST0` 记为 nQON 代称、开漏需上拉 | `knowledge/references/L0-ate-primer.md:13`、`knowledge/hardware/relays.md:142`、`:150` | 知识层（非 DFT 工件） |
| E-17 | 输入谱系：当前工作簿 `Dali_testmode.xlsx` sha256 `0b0480a2…abbd` / 10677032 B；归档映射快照系另一代（证据侧 `d9d721a3…788e` / 12210607 B） | `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md:46`、`:67-69`、`:296` | 本 run 前序产物 |
| E-18 | `INT` 在 DFT 侧的存在形式：PAD 清单成员 + Pin2Pin 表条目（与 AGND 同组，注释"能测到寄生 esd 的二极管"） | `project/DALI/input/PINLIST.txt:10`、`project/DALI/_archive/_dump_Pin2Pin.txt:12` | DFT 侧 PAD/连接清单 |

**关键限制（FACT）**：`TestIO` 与 `DTESTMAP` 的**单元格内容**不在当前 DFT 三件套中
（三件套只携带 row/col 与条目字段：`project/DALI/meta/manifest.json:11-24` 声明的输出只有
meta 与 YAML；`project/DALI/meta/manifest.json:60`、`:63` 只给出行数），且该工作簿不是 UTF-8 文本、
本次工具链无法读取其单元格（`team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md:72-97`）。
因此 E-3 / E-5 / E-6 的**内容**来源是同项目归档快照，其权威性由"与当前工作簿行数逐一对上"支撑，
不由内容哈希支撑（快照哈希：`_dump_TestIO.txt` = `7fd842e6…2972`，174 B；
`_dump_DTESTMAP.txt` = `9edd814e…9e98`，1930 B）。

---

## Method

1. **确认 DFT 侧对该端点写了什么**：从当前三件套取 `check` / `checkLines` / `log` / `notes`
   （E-1、E-2），再从证据层 `overview-dump.txt`、`csv-full-dump.txt` 交叉核对同一字段。
2. **定位定义者**：枚举 DFT 层可能定义"check pin / test-bus mapping"的载体——
   ① 当前三件套（条目级）；② DFT 工作簿 sheet 清单与行数（meta / manifest）；
   ③ DFT 侧 PAD 清单 `PINLIST.txt`；④ 工作簿 pin-map sheet 的纯文本快照（`_archive/_dump_*.txt`）；
   ⑤ `.sv` 生成物；⑥ PAD 级 Pin/Connect 清单。逐一对 `DTEST0` 做检索，记录命中与 0 命中。
3. **判定"可观测端子是否被 DFT 证据识别"**：只认**名称绑定证据**，不认"类似命名"推断。
   判据：`DTEST0` 是否为 PAD 名 → 否（E-4）；是否存在 sheet 级绑定 → 是（E-3）；
   绑定目标是否为物理 PAD → 是（`nQON`，且 `nQON` 出现在 PAD 清单 `project/DALI/input/PINLIST.txt:1-39`
   之外的接线事实中，见冻结基线与实现层 E-14、E-13）。
4. **不相干项排除**：把 `Check = INT` 与 `V(DTEST0)` 作**两条不同观测路径**分别登记（E-9、E-18），
   不合并、不互相替代。
5. **寄存器冲突核对**：把 `DMUX_SEL`（22）与 `DTEST0_MUX`（23）分别对 `Reg_DTEST0_general`
   索引 22/23 作名称核对（E-5、E-6），并对 TM108/TM109/TM110 三行检查是否存在系统偏移（E-10）。
6. **只写本任务范围内的报告文件**；对项目产物的任何修改只作提案（§5）。

---

## Counter-check

| 反向检验 | 目的 | 结果 |
|---|---|---|
| `DTEST0` 是否为 PAD 名？（若在 `PINLIST.txt` 命中，则"内部总线名"结论不成立） | 推翻结论一 | **未命中**：`project/DALI/input/PINLIST.txt:1-39` 无 `DTEST0`，其中 `:10` 为 `INT` → 结论一成立（E-4） |
| `DTEST0 → nQON` 是否只存在于实现代码（即"命名推测"）？ | 削弱结论二 | 否。绑定来自 DFT 自己的 TestIO sheet 快照（`project/DALI/_archive/_dump_TestIO.txt:2`），且该 sheet 当前 7 行与快照 7 行一致（`project/DALI/meta/manifest.json:60`）→ 结论二有 DFT 侧映射支撑（E-3） |
| 归档快照是否可能已过期（与当前工作簿不同代）？ | 削弱证据强度 | **部分成立**：输入谱系确有换代（`dft-fact-audit.md:46`、`:67-69`）；但两个 sheet 的**行数**在当前工作簿中被声明为 7 / 75，与快照行数一致（`manifest.json:60`、`:63`）→ 内容仍为 UNKNOWN，已登记为 `OI-T6-02`，未据此断言位定义 |
| 是否存在别的 sheet 定义 mux 字段（如 `SETTING_MAP` 733 行）？ | 寻找 `DTEST0_MUX` 定义载体 | 该 sheet 在当前三件套中只有行数（`project/DALI/meta/dali_tm_meta.json:200-202`），内容不在三件套内且本次无法读取 → `DTEST0_MUX` 位定义仍为 UNKNOWN（结论五） |
| `Check = INT` 是否可用"INT 就是 nQON 的别名"解释掉？ | 防止把 F3 静默消解 | **不可**：`INT` 是 PAD 清单独立成员（`project/DALI/input/PINLIST.txt:10`），且有独立 Pin2Pin 条目（`project/DALI/_archive/_dump_Pin2Pin.txt:12`）；TestIO 未把 `INT` 与 `DTEST0` 关联（`project/DALI/_archive/_dump_TestIO.txt:1-7`）→ 保持两侧登记，不动 |
| 按"位模式"把 23 反推为索引 23，是否可关闭 F2？ | 防止用未经证实的解码假说消解冲突 | **不可**：`DTEST0_MUX` 的位定义无载体；两种读法（十进制 23 / 7 位模式 `10111`）都指向 `a2d_vbat_uv_ok`（`_dump_DTESTMAP.txt:25`），与"VAC1 阈值"语义不符，属**需要裁定**而非可自证 → F2 保持两侧保留 |
| 三件套里是否已有任何 PAD 级绑定（若已有，则本任务的"缺载体"结论不成立）？ | 检验结论四的限定 | 三件套仅 `V(DTEST0)` 名称（`dali_tm_meta.json:1402`、`test_conditions.yaml:267`）；无 PAD 字段 → 限定成立 |

---

## Downstream impact

1. **OI-T4-01 的"关系"部分可以关闭，实体部分不能关闭。**
   - 可关闭：`DTEST0` 的可观测物理端子 = `nQON`，资源对象 `NQON_HG1_ACM`
     （t4 已给出对象、通道与通路：`tm108-resource-config-contract.md:139`、`:217-221`）。
   - 不能关闭：该映射的**当前工作簿载体**（TestIO/DTESTMAP 单元格）与 `DTEST0_MUX` 字段定义 →
     替换为 `OI-T6-02`（§6）。t4 的 `RA-5 = CANDIDATE ONLY` 不应仅凭本报告直接升级为"已定"；
     若队长裁定按 E-3 升级，则证据依据须写成"DFT TestIO 映射快照 + 当前行数一致"，
     而不是"三件套内含该映射"。
2. **观测端点的电气性质**：`nQON` 在 DFT/实现/知识三层一致表现为**开漏数字观测**，
   需要上拉（`K65_nQON_PU`；E-13、E-14、E-16）。这是**资源/继电器层**已由 t4 决定的内容，
   本报告不改动它。
3. **触发/判别电平没有 DFT 证据**：1.65 V 出自实现层注释"预估"（E-15），
   DFT 层只有 `deTest r 4.059 / f 3.738`（`project/DALI/meta/dali_tm_meta.json:1417`）。
   方法契约**不得**把 1.65 V 当成 DFT 事实；应作为"实现层预估值"登记，或列为定点补证（§6 `OI-T6-03`）。
4. **`Check = INT` vs `V(DTEST0)` 仍是开放冲突**（OI-T4-11 / F3）：本报告只证明
   "`DTEST0` 的可观测端子是 `nQON`"，**不**证明 `INT` 与 `nQON` 的关系，因此
   观测路径二选一（或分时）仍需队长裁定。方法契约不得以任一侧为前提推进测量判定。
5. **mux 值：下游只能按"名称一致"这一条可核对事实走**：`.sv` (22) 与 DFT Notes
   "A2D_VAC1_PRST → dtest0" 在语义上一致（E-5、E-7、E-2）；CSV 侧 23 = `a2d_vbat_uv_ok`
   与 VAC1 阈值语义不符（E-6）。但**本报告不裁定**，OI-T4-10 继续开放，
   两侧值都必须在契约中保留（与 t4 当前做法一致）。
6. **对 t5 方法契约的直接影响**：所有依赖"观测端点身份/触发电平"的阶段与测量判定应继续
   标 pending 并引用 `OI-T4-01`（关系已可引用本报告）与 `OI-T6-02`、`OI-T6-03`（新登记）；
   已可安全引用的部分是"nQON 开漏 + K65 上拉"这一资源事实（t4 已签）。

---

## Open items

| id | 状态 | 内容 | 闭合所需的**确切**来源 | owner |
|---|---|---|---|---|
| `OI-T4-01` | **部分关闭**：关系（`DTEST0` → `nQON`）已由 DFT TestIO 映射证据确立（E-3）；"当前工作簿载体"与 mux 位定义**未闭合**，拆分为 `OI-T6-02`、`OI-T6-03` | 观测端点身份 | 见 `OI-T6-02` | dft-expert（已交付） |
| `OI-T6-02` | 新登记（承接 OI-T4-01 的实体部分） | 当前工作簿 `Dali_testmode.xlsx` 的 `TestIO`（7 行）与 `DTESTMAP`（75 行）**单元格内容**在本 run 的任何产物中都不存在；现有结论依赖 2026-08-06 归档快照 `_dump_TestIO.txt` / `_dump_DTESTMAP.txt`，只有行数可与当前工作簿对上 | 当前工作簿 `TestIO` 与 `DTESTMAP` 两个 sheet 的纯文本转储（含 `update` 日期行），或接受归档快照并记录该接受决定 | captain（授权转储）+ dft-expert |
| `OI-T6-03` | 新登记 | 观测判别的触发电平 1.65 V 无 DFT 证据，仅为实现层"预估"（E-15） | DFT 层若存在 nQON 逻辑电平规格（芯片/工作簿规格页）则给出；否则由方法契约按"实现层预估值"登记并经队长裁定 | dft-expert + test-method-expert |
| `OI-T4-10` | **保持开放**（F2） | `DMUX_SEL = 22`（`.sv`/meta/YAML）vs `DTEST0_MUX = 23`（CSV）；本报告补充：索引 22 = `a2d_vac1_prst`、索引 23 = `a2d_vbat_uv_ok`，且 CSV 层存在 +1 一致偏移（TM108/109/110） | 当前工作簿 `SETTING_MAP`（733 行）中 `DTEST0_MUX` / `Reg_DTEST0_general` 的字段位定义，或 `.sv` 生成器所用的寄存器映射 | dft-expert + test-strategy-architect |
| `OI-T4-11` | **保持开放**（F3） | 观测脚身份 `V(DTEST0)` vs `Check = INT`；本报告仅证明 `DTEST0 → nQON`，未证明 `INT` 与 `nQON` 的任何关系 | 当前工作簿 `TestIO` / `Pin2Pin` 中 `INT` 的功能定义，或队长裁定观测路径 | dft-expert + captain |
| `OI-T6-04` | 新登记（低） | `INT` 在 DFT 侧的用途现有证据只有 PAD 清单成员（`PINLIST.txt:10`）与 Pin2Pin 条目（`_dump_Pin2Pin.txt:12`，与 AGND 同组、注释"能测到寄生 esd 的二极管"），**未**出现任何 `INT` 作观测端的 DFT 用例 | 当前工作簿 `TestIO` / `Pin2Pin` 全表，或 DFT.csv 中 `Check=INT` 其他行的对照说明 | dft-expert |

### 本次提交的项目产物修改提案（**未执行**，等授权）

| 提案 | 文件 | 拟改内容 | 理由 | 需要谁授权 |
|---|---|---|---|---|
| PR-1 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md`（**非本任务 in-scope**，仅提案；该行内容本 turn 未逐行复核，只按 t6 任务书给出的文件名与 RA-5 / OI-T4-01 标识引用） | 把 `RA-5` 的 `status` 从 `CANDIDATE ONLY` 改为"DFT TestIO 映射已证实（关系层面），mux 字段与当前工作簿载体仍待补证"，证据栏改用 E-3 / E-5 | 本报告结论四；避免以"三件套内含映射"表述 | captain + test-strategy-architect |
| PR-2 | `project/DALI/meta/manifest.json`（**out of scope，仅提案**） | 在 `gaps`/`notDone` 或新增 `unparsedSheets` 中显式登记 `TestIO`、`DTESTMAP` 的单元格内容未导出（只有行数） | 让"三件套不含 PAD 绑定"成为显式缺口，而不是下游隐性假设 | dft-expert 执行前需 captain 授权（`project/DALI/meta/` 非本任务 in-scope） |
| PR-3 | 当前工作簿 `Dali_testmode.xlsx` 的 `TestIO` / `DTESTMAP` 纯文本转储（新增产物，非改写） | 生成 `team/artifacts/tm108-v2-trial/dft/` 下的 sheet 转储 | 关闭 `OI-T6-02`，且不触碰任何项目文件 | captain 授权（需读取工作簿 sheet 的能力，本次工具链不具备） |

**声明**：以上三项**均未执行**。本任务只写入了
`team/artifacts/tm108-v2-trial/dft/dtest0-oi-t4-01-resolution.md`；
`project/DALI/**`、`D:/PROJECT6-DALI/devel`、`team/artifacts/tm108-v2-trial/strategy/` 全程只读。
