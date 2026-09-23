---
name: nuvolta-codegen
description: Nuvolta STS8300 测试代码生成 — 工作流编排 + 内容索引。固定入口：入口解析→Step0 原理图(有货先验)→Step1 DFT+pin 三源三层校验→CBIT-Definition(有货先验门)→Step3 批次分类→Step4 共用生成循环→Step5 收尾双查。规则正文一律在 knowledge/standards/，每环就地按指针读取
---

# Nuvolta STS8300 测试代码生成（编排 + 索引）

> **本文件定位（2026-08-30 用户拍板）**：只放**指向各环节的指针**（规则 / 检查 / 脚本 / agent），**不含具体执行内容**。
> 每执行到哪一环，就在那一环按指针去 `knowledge/standards/<file>` 读规则、去 `.claude/agents/<file>` 读执行细节、去工程根调脚本。
> 规则正文**一律**在 `knowledge/standards/`（见 §4 索引）；改规则 → 改对应 standards 文件，本文件只维护指针。

---

## 1. 架构（固定解析链 + CBIT-Definition）

```
用户: "写 TM600"
        │
        ▼
  主 Skill 入口（解析指令 → 本批 TM 范围；唯一解析链）        [入口: project_config.json + OVERVIEW(Dali_testmode.xlsx)]
        │
   Step -1: 输入同步门（2026-09-13 新增 · 先于一切「是否要重生成」判定）
   [脚本] check_input_sync.py — 判「输入侧派生文件是否与源同版本」（版本一致性, 不看 mtime）
          DFT 组: xlsx → meta → yaml     (meta._syncStamp.dftSha256 / yaml._sync.metaSha256)
          SCH 组: csv → map + statistic   (validation_manifest.json.txt 的 input/artifacts 哈希)
          ┌ IN SYNC     → **什么都不用改**（跳过 Step0 重生成, 直接下行）
          └ OUT OF SYNC → 只重生成落后那一组（DFT: gen_testitems_meta → gen_test_conditions；
                          SCH: run_hardware_parse）→ 复跑本门至 IN SYNC
        │
   Step 0: 原理图解析（有货先验: 无 SCH-Connect-Map 才 sch-parse；有 → 沿用现网产物）
   [Skill] sch-parse → Component-Statistic + SCH-Connect-Map    [读: knowledge/hardware/schematic-parsing.md]
   [门]    check_library_files.py 工程完整性门（Step0 之前必跑, 0 缺失才进）[规则: none, 纯脚本]
        │
   Step 1: DFT 解析 + pin 交叉校验（2026-08-27 交换: 先原理图后 DFT）
   [文件]  Pin_Channel_define.h → 源表名映射 (FOVIe=FXVIe_PLUS)  [规则: site-num-rule.md]
   [Agent] dft-parse-agent（仅 DFT parse）                       [读: test-types.md]
   [脚本]  gen_testitems_meta.py + gen_test_conditions.py → meta + test_conditions.yaml
   [脚本]  check_dft_pins.py → 三源三层校验（L1 DUT pad / L2 测试pad / L3 组合节点）
          未命中 → 问用户；0 未命中才放行
        ▼
  CBIT-Definition（cbit-agent 执行 · 公共前置,每次进入必走）     [读: relay-checklist.md]
   有继电器定义文件?
     ├── 否 → 完整四阶段创建: P1 gen_cbit_defines.py --cbit → P2 gen_paths.py → P3 gen_path_defines.py(歧义组agent复核) → P4 gen_cbit_defines.py --verify <StdAfx.h> [--map <SCH-Connect-Map.txt>]
     └── 是 → 有货先验门: 工程 dll(F12011.dll) mtime 距今 >1 天 → 才 P4 check；≤1 天 → 跳过
        ▼
  Step 3: 材料门（**批次级前置** · 2026-09-13 挪位: 原在生成循环 ①）
  [脚本] gen_material_status.py --check（索引漂移）+ verify_material_receipt.py --no-read-proof
         —— **一次看全整批**: TM × 参数类型 × 材料可用性 × Test Type 框架可用性（**零内容载入**）
         ┌ 有案例 → 收据声明（param_type / branch / materials / tier1）
         └ 无案例 或 无框架 → **软门: 记录缺口 + 放行**（按 DFT + 上电/测量/机台手册/log/框架 规则写）
            收尾须**整批汇总上报**；同类积累后回收提炼成新 golden / 规则
  ⚠ 硬门（仍 FAIL）: 收据不实 —— 声明了不存在的材料 / 未声明登记的必读材料 /
                     branch·tier1 缺失或矛盾 / 读证不足（软硬分界 = 用户流程图的两条「否」分支）
        ▼
  共用生成循环（**按组**: 分组键 = (param_type, 测试条件指纹)）   [读: framework.md + units.md + toggle-awg-rules.md + register-config.md + context-management.md §6]
   ├── ① 取料 + 定框架（**逐项** · 2026-09-13 从原 Step3 降到这里；材料门已上移为批次前置）
   │      Tier1 通用方法(L1-chip + L3-method) → 判「够不够写」→ 不够才 Tier2(分支 .md) → 仍不够 Tier3(原文按需)
   │      + Test Type 判定(7 类) → 选模板 + 写**组级读证**(golden 哈希 + 四类结构)
   ├── ② relay-agent（先通路继电器 → 再角色继电器 → 统一 cbite.SetOn()）  [读: relay-checklist.md + path-principles.md]
   ├── ③ gen_power_sequence.py（一次输出 上电/PowerState/下电 三段）      [读: units.md R-PON-09 在 power-on-agent.md 规格]
   ├── ④ 模板填充 → entertestmode() + Software_initial                  [读: register-config.md + framework.md]
   ├── ⑤ measure-agent（MI/MV/Toggle/Trim/AMUX-NTC）                    [读: toggle-awg-rules.md + test-types.md + units.md]
   ├── ⑥ 模板填充 → LogData                                            [读: units.md R-LOG/R-HYS/R-VIR]
   ├── ⑦ verify_single_fn.py → 单函数冒烟（**每 TM 一次、秒级、不编译**；FAIL 停留当前 TM, 不得进下一个）
   │      ⚠ 编译节奏另算（`context-management.md §2.2`，阈值 5）: ≤5 个 TM → 写完编一次；>5 个 → 每 5 个编一次 + 末尾一次
   └── 最后一个测试项? 否→循环  │ 是
        ▼
  两段式写码收尾（`context-management.md §2`）
   ├── 阶段1: 新 TM 全部追加尾部后 → 增量编译 + 门禁
   └── 阶段2: 按 TM 编号**归位** → **移动后必须再编译一次**（查"组装"有没有出错）
               —— 起先代码是按"不考虑贴在程序哪里"写的、统一追加在尾部，最后才组装进程序
               零移动（本批已按 TM 递增）→ 阶段1/2 编译合一，收尾注明「本批零移动」
        ▼
  收尾双查（Step 5）   [读: error-checklist.md + check-agent.md + verification.md]
   ├── check-agent（60+ 项 P/E/R/H 检查）
   ├── gen_cbit_defines.py --verify <StdAfx.h> [--map <Map>]（继电器定义 V1~V8；⚠ --verify/--map 都需带参数，裸写=argparse 报错 exit 2）
   ├── verify_awg_params.py --src test.cpp（Toggle 3 参数门禁 E005）
   ├── check_testitems_meta.py --require-all --require-scope <本批>（meta 全覆盖门）
   └── verify_relay_trace.py --meta --warn-as-error（Cap 供电反向检查 E）
        │ FAIL → 修复 → 重新检查 → PASS ✓
```

---

## 2. 触发映射（任务进来先读哪一组）

| 触发 | 先读 |
|------|------|
| 写TM / codegen | §1 架构 + §3 流程 + `framework.md` + `units.md` + `error-checklist.md` |
| 继电器 / 通路 / CBIT / Share / Kelvin | `relay-checklist.md` + `path-principles.md` + `hardware/schematic-parsing.md` |
| 编译 / debug / deploy / 写测试方案 | compile-agent / deploy-agent / testplan-agent（旁路, 用户触发, 不进 codegen） |
| 源表 API（FPVI/ACM/FOVI/HVI/HPVI/QVM/FXVI） | `sources/index.md` 速查 → 对应 `sources/*.md` |
| 自进化（/evolve rules/exp/fn / daylog） | rules-agent / experience-agent / sub-function-agent |

---

## 3. 工作流程骨架（每步 = 目标 / 谁执行 / 读什么 / 产出）

### Step -1: 输入同步门（版本一致性 · 2026-09-13 新增）

- **目标**: 判「输入侧派生文件是否与源同版本」，决定**要不要重生成**——匹配就什么都不改。
- **执行**: `python check_input_sync.py`（退出码 0 = 全 MATCH = 无需修改；1 = 有落后项）。
- **两条版本链**:
  - **DFT 组**: `Dali_testmode.xlsx` → `dali_tm_meta.json`（`_syncStamp.dftSha256`）→ `test_conditions.yaml`（`_sync.metaSha256`）
  - **SCH 组**: `Dali-SCH.csv` → `SCH-Connect-Map.txt` + `Component-Statistic.txt`（`validation_manifest.json.txt` 的 `input.sha256` + `artifacts.*_sha256`）
- **判定**: 全 MATCH → **无需修改**，跳过 Step0/SCH 重生成；DRIFT/NO-STAMP/MISSING → 只重生成落后那一组，**DFT 组顺序不可反**（先 meta 后 YAML，YAML 的 stamp 引用 meta 哈希），复跑本门至 IN SYNC。
- **与 Step2 dll mtime 门的区别**: 本门管**输入侧版本一致**（内容哈希，不看 mtime）；dll mtime 门管**产物侧新鲜度**（编译发布时效）。两者独立，本门在前。
- **读**: 无（纯脚本；`project_config.json` 为路径唯一入口）。

### Step 0: 原理图解析（有货先验）

- **工程完整性门（Step0 之前必跑）**: `python check_library_files.py` — 查 Library-Functions 16 文件 + `.treg` 在 vs_src_dir 齐全；缺任一 → **反馈「缺失 Library Function」**；0 缺失（退出码0）才进 Step0。换项目时工程文件与 .treg 由用户同步更换。
- **目标**: 无 SCH-Connect-Map 才 sch-parse 生成；有 → 沿用现网产物（不重解析）。
- **产出**: Component-Statistic + SCH-Connect-Map.txt（含列11 通路分类六类/多源/最短路径，归 sch-parse agent，不脚本化）。
- **读**: `knowledge/hardware/schematic-parsing.md`。

### Step 1: DFT 解析 + pin 交叉校验

- **目标**: 圈定本批 TM 清单（对照 OVERVIEW isCodeGen 过滤）→ DFT → meta + test_conditions.yaml → pin 三源三层校验。
- **执行**: 入口解析 → Pin_Channel_define.h 源表映射 → dft-parse-agent（仅 DFT）→ gen_testitems_meta.py + gen_test_conditions.py → check_dft_pins.py（L1/L2/L3，未命中→问用户，0 未命中才放行）。
- **testType 覆盖（权威）**: 两段斜坡(升+降) → YAML `testType` 强制 `toggle`（gen_test_conditions.py 判定，覆盖 DFT 声明）。
- **收尾: 材料状态扫描（2026-09-13 新增）**: `python gen_material_status.py` → 刷新 `references/material_status.json`（**只放状态+哈希+指针，不放内容**）。供 Step3 批次材料门「一次看全整批可用性 + 缺口 + 框架可用性」而**不必载入任何材料内容**；`--check` 复算哈希判**漂移**（材料被改/删/新增未登记）。
- **读**: `test-types.md`（分类 + 覆盖判定）、`site-num-rule.md`（STS_SITE_NUM→SITE_NUM 改写）。

### Step 2: CBIT-Definition（公共前置 · 每次进入必走）

- **有定义** → 有货先验门: 工程 dll mtime 距现在 **>1 天 → 才 P4 check**；**≤1 天 → 跳过**（刚随编译发布不重复验）。
- **无定义** → 完整四阶段创建:
  - P1 `gen_cbit_defines.py --cbit <CBIT表.xlsx> --stat <Component-Statistic.txt>` → 单点 #define + V1~V8
  - P2 `gen_paths.py --netlist --cbit --json`（优先读 SCH-Connect-Map，缺失时 BFS 兜底）
  - P3 `gen_path_defines.py` → 通路 #define 追加 StdAfx.h（命名歧义组 → cbit-path-namer 复核）
  - P4 `gen_cbit_defines.py --cbit --verify <StdAfx.h> [--map <SCH-Connect-Map.txt>]`
- **脚本改动后必跑** `--audit-rules`（gen_cbit_defines / gen_paths / gen_path_defines 各 12+ 规则自检）。
- **读**: `relay-checklist.md`；产出落点 StdAfx.h（单点块 / PATH_RELAY 段 / RELAY_ROLE 段）。

### Step 3: 材料门（**批次级前置** · 2026-09-13 挪位）

> 从生成循环 ① 上移为批次前置：**一次看全整批**（TM × 参数类型 × 材料可用性 × Test Type 框架可用性），**零内容载入**。
> 原「框架创建」下移为 Step4 ①（逐项）——testType 本就是逐 TM 的。

- **执行**: `gen_material_status.py --check`（索引漂移）+ `verify_material_receipt.py --no-read-proof`（批次前置阶段不要求读证，读证留到 ① 写码时）。
- **软门（材料缺口 → 记录 + 放行，不阻塞）**: ①参数类型未登记 ②无黄金案例 ③Test Type 无框架模板。
  三条都**记录缺口 + 按 DFT + 上电/测量/机台手册/log/框架 规则写码**；**收尾须整批汇总上报**；同类积累后回收提炼成新 golden/规则。
  黄金独有的四类结构**兜不住的那一项 → 向用户提问**（`context-management.md §5`）。
- **硬门（仍 FAIL · 收据不实）**: 声明了不存在的材料 / 未声明登记的必读材料 / `branch`·`tier1` 缺失或矛盾 / 读证不足。
  分界依据 = 用户流程图：两条「否」分支是**缺材料**（软）；「是」之后的检索失败是**收据不实**（硬）。
- **读**: `context-management.md` §6（三档 + 分组 + 隔离）。

### Step 4: 共用生成循环（**按组**: 分组键 = `(param_type, 测试条件指纹)`）

① **取料 + 定框架**（逐项）→ ② **relay-agent**（环节② 统一单元: 先通路→再角色→统一 cbite.SetOn；13 步详见 `agents/relay-agent.md`）→ ③ **gen_power_sequence.py**（--meta + --pin-map + --define → 上电/PowerState/下电三段；R-PON/R-POFF 规则清单在 power-on/power-off-agent.md 规格文档）→ ④ **模板填充**（entertestmode + Software_initial）→ ⑤ **measure-agent** → ⑥ **模板填充**（LogData）→ ⑦ **verify_single_fn.py 单函数冒烟**（FAIL 停留当前 TM, PASS 才进下一个）。

- **① 取料 + 定框架（2026-09-13 从原 Step3 降到这里）**:
  - **testType 来源（Plan A）**: 读 `test_conditions.yaml` 的 `testType`（Step1 生成的 DFT 解读层权威源），不再从 DFT 重判，以覆盖后值为准。
  - **Test Type（7 类）判定 + 选模板**: 普通 / Toggle-AWG / Trim / OTP·MTP 五段式 → `framework.md` + `test-types.md`；三类无框架（Contact/P2P/Leakage）→ 软门缺口。
  - **材料三档（`context-management.md` §6）**: Tier1 通用方法**必做第一步** → 判够不够写 → 不够才 Tier2（按 `branch`）→ 仍不够 Tier3 原文（按需，只读分支匹配的 1 份）；**读完即弃**。
  - **写组级读证**: `goldenSha256` + 四类关键特殊结构（每组一次，不随 TM 数膨胀）。
  - **单位铁律**: R-LOG / R-HYS / R-VIR → `units.md`。

- **pin-map 生成（B 路径）**: 脚本不做 pin→源表查找，由 relay-agent 从 SCH-Connect-Map 补齐每个 PIN 的源表对象名 + 类型生成 pinMap（`{pinMap, currentLimit, rampProfile, mvNoFipins}`）。缺失 → ERROR 立即修，不静默跳过。
- **observe 语义**: 只写 PIN 不写源表对象；trigger 由 ramp 方向推（升→RISING / 降→FALLING），见 `toggle-awg-rules.md`。
- **读**: `framework.md` + `units.md` + `toggle-awg-rules.md` + `register-config.md` + `relay-checklist.md` + `path-principles.md` + `context-management.md`（读文件纪律: test.cpp/StdAfx.h 禁全读、golden 走索引、两段式写码）。

### Step 5: 收尾双查（代码检查）

- **执行**: check-agent（60+ 项 P/E/R/H）+ gen_cbit_defines.py --verify <StdAfx.h> [--map <Map>] + verify_awg_params.py + **meta 全覆盖门**（`check_testitems_meta.py --require-all --require-scope <本批>`，正向: test.cpp 每函数必须有 meta；反向: 本批 isCodeGen=Y 每项必须已写入 test.cpp）+ verify_relay_trace.py --meta。
- **FAIL → 修复 → 重新检查 → 直到 PASS**。
- **缺口回收（2026-09-13 新增）**: 若 Step3 落过 `material_gaps.json`，收尾须**整批汇总上报用户** + 按 §6.1 做**回收提炼**（缺口 → 新 golden / 新 Tier1 方法 / 新规则）→ 否则同类 TM 下次仍裸写。
- **读**: `error-checklist.md`（错误码速查）+ `verification.md`（两层检验门禁）+ `check-agent.md`（完整清单）。
- **批量纪律 B-001**: 先单函数冒烟 → 占位符降序替换 → 生成后自检（`rules-registry.md` 登记 + `verification.md`）。

---

## 4. 规则文件索引（knowledge/standards/，规则正文在这里）

> 本文件只留指针。规则/检查/脚本的全量定义在下列文件；每环执行时按 §3 就地读取。

| 主题 | 文件 | 关键内容 | 强制层/相关脚本 |
|------|------|---------|----------------|
| 找通路三原则 | `path-principles.md` | 精度门/最短通路/Pin2Pin/并行效率 + 冲突降级原则 + gen_source_path.py | gen_source_path.py --demo |
| 继电器清单 | `relay-checklist.md` | 闭环回路 / BUS 决策表 / Cap2 / 反短接 / 列11 六类 / 11 步清单 | verify_relay_trace.py、check-agent P006/R004/E011 |
| 寄存器配置 | `register-config.md` | 重新上电必须 entertestmode() 铁律 | check-agent R034 |
| 单位量程 | `units.md` | 量程≥2× / 单位判断 / R-LOG / R-HYS / R-VIR / SetOn / 台阶 | check-agent E025/E026/E027 |
| 框架模板 | `framework.md` | 普通 / Toggle / Trim 三模板 + 注释强制 + Trim 判定铁律 | — |
| Toggle/AWG | `toggle-awg-rules.md` | R-AWG 增项判定 / 3 参数 / 段数推导 / trigger | verify_awg_params.py、check-agent E005/H010 |
| 错误码速查 | `error-checklist.md` | P/E/R/H 四层 + 常用错误码明细表 | check-agent + 各 verify 脚本 |
| 测试类型 | `test-types.md` | 7 类项目结构 + 11 类参数族 + 测量方法 + testType 覆盖 | gen_test_conditions.py |
| 合并规则 | `merge_rules.md` | MR-000 零合并铁律 + 未来 MR-0xx 登记 + M 组错误码 | verify_merge_rules.py |
| SITE_NUM | `site-num-rule.md` | STS_SITE_NUM→SITE_NUM；唯一权威=工程 StdAfx.h L23；库头文件注释态勿解注 | — |
| 上下文管理 | `context-management.md` | test.cpp/StdAfx.h 禁全读 / 两段式写码 / golden 走索引 / 黄金案例角色提取 | — |
| 校验门禁 | `verification.md` | 单函数冒烟 5 项 + 跨项目统一门禁 + 与 B-001 关系 | verify_single_fn.py + 各门禁脚本 |
| 寄存器读法 | `treg.md` | TREG 系统: execute / ASSY / measure 模板 / 常见错误 | Trim 类 |
| 规则注册表 | `rules-registry.md` | 全局/专项规则生命周期（R-xxx 登记, draft→active→retired） | verify 脚本同步 |
| 命名 | `naming.md` | 函数/参数/源表/继电器/treg 命名 | check-agent |
| 子函数库 | `functions-registry.md` | 跨项目共享子函数索引 | sub-function-agent |

---

## 5. 内容索引（知识库 / Agent / Skill / 参考案例 / 项目文件）

### 知识库 `knowledge/`
| 文件 | 内容 |
|------|------|
| `sources/index.md` + `sources/*.md` | 源表 API 速查（ACM200/FPVIe/FOVIe/HVIe/QVMe/FXVIe…）+ 系统函数 + 硬件规格 |
| `hardware/relays.md` | G6K/TLP3412 规格, BUS/Share/Cap/P2P 分类 |
| `hardware/schematic-parsing.md` | **原理图解析**: 六任务门控 + 功能分类 + 通路有效性(Rule A/B) + 列11 六类 + 分时复用 |
| `hardware/closed-loop-model.md` | 闭环两条件 + Kelvin/Non-Kelvin + 接触电阻 |
| `hardware/test-strategy.md` | **源表选型(≥200mA→FPVIe) + 小电压生成 + 资源冲突** |
| `hardware/pin-resource-map.md` | Pin→源表→继电器 映射 + 继电器速查 |
| `hardware/bus-topology.md` | FPVI_BUS 拓扑 + 闭环模型 + BUS/Cap2 决策表 |
| `hardware/cbit-principles.md` / `hardware/cbit-mapping.md` | CBIT 通用原理 / 项目映射 |
| `experience/index.md` | 项目级经验库（experience-agent 维护） |
| `standards/` | **规则正文**（见 §4 索引，本文件不重复） |

### Agent `agents/`（规格/执行细节在各自文件）
| 文件 | 职责 |
|------|------|
| `dft-parse-agent.md` | DFT → TestItemMeta（仅 DFT parse, 源表映射留给 relay） |
| `relay-agent.md` | **环节② 统一单元**（先通路→后角色→统一 cbite.SetOn，13 步 + pin-map） |
| `measure-agent.md` | MI/MV/Toggle/Trim/AMUX-NTC |
| `power-on-agent.md` / `power-off-agent.md` | **已脚本化** → gen_power_sequence.py（规格文档, R-PON/R-POFF 清单） |
| `check-agent.md` | 60+ 项 P/E/R/H 四层检查（完整清单） |
| `cbit-agent.md` | CBIT-Definition 公共前置（有→dll 时效门 check / 无→四阶段） |
| `cbit-singlepoint/parse/check/path-finder/path-namer` | **已脚本化** → gen_cbit_defines.py / gen_paths.py / gen_path_defines.py（规格文档） |
| `compile-agent.md` / `deploy-agent.md` / `testplan-agent.md` | 编译+Debug / 开软件前置 / 测试方案（旁路, 用户触发） |
| `rules/experience/sub-function-agent.md` | 自进化（独立工作流, 见 §6） |

### 其他 Skill `skills/`
| 文件 | 职责 |
|------|------|
| `sch-parse.md` | **原理图 Netlist 解析**（独立工作流）: 六任务门控 → Component-Statistic + SCH-Connect-Map.txt |

### 参考案例 `references/`（**两层索引 + L 层材料**）
| 文件 | 内容 |
|------|------|
| `param_type_index.md` | **参数类型索引层**（人读）：参数 → L1-chip / L3-method / L4-Golden-code / L5-debug 四件套（同名联动）+ 项目结构类型列 |
| `func_type_index.md` | **功能类型索引层**（人读）：7 类项目结构类型 → 判据 / **代码框架** / 测量方法 / 示例参数。**Step3 的 Test Type 检查按此判「框架是否已有」**（判据权威在 `standards/test-types.md`） |
| `material_status.json` | **材料状态**（机读，`gen_material_status.py` 生成）：状态 + 哈希 + 指针（不放内容）+ 缺口；含 `testTypes` 框架可用性段 |
| `00-index.md` | 参考层总入口（四件套 + 两层索引 + 变更纪律） |
| `L0-ate-primer.md` / `L1-chip/` | ATE 入门 / 芯片 Block 介绍（是什么）——**Tier1 通用方法的 chip 半边** |
| `L3-method/` | 典型参数测试方法（怎么测）——**Tier1 通用方法的 method 半边** |
| `L4-Golden-code/` | 优秀案例 `.cpp/.txt` + **同名 `.md` 要点总结**（长啥样）——Tier2 注解 / Tier3 原文 |
| `L5-debug/` | 调试/排查方法论（**按需**，非必须） |
| `L2-test-items/` | 测试项全景（04-uvlo / 05-ocp / 06-ovp / 07-current-sense / 08-nfault 等） |

### 项目文件（工程根）
| 文件 | 用途 |
|------|------|
| `project_config.json` | 项目输入清单唯一入口（+ proj_config.py 共享 loader） |
| `Dali_testmode.xlsx /OVERVIEW` | TM 定义 + isCodeGen 过滤（入口圈批 + meta 反向覆盖权威） |
| `gen_source_path.py` | **找通路规划门**（需求 DSL → 源表+通道+继电器+最短/第二短+跨需求重叠检测+冲突降级） |
| `gen_power_sequence.py` | 上电/下电代码生成器（--audit-rules 规则自检） |
| `gen_cbit_defines.py` / `gen_paths.py` / `gen_path_defines.py` | CBIT 定义 / 通路查找 / 通路命名（P1~P4 + --verify + --audit-rules） |
| `gen_testitems_meta.py` / `gen_test_conditions.py` | TestItemMeta / test_conditions.yaml 生成（各自 emit `_syncStamp` / `_sync` 版本戳） |
| `check_input_sync.py` | **输入同步门**（Step -1）：DFT↔meta↔YAML + csv↔map↔statistic 版本一致性；IN SYNC → 什么都不用改 |
| `gen_material_status.py` | **材料状态索引**（Step1 收尾生成）：`references/material_status.json` = 状态+哈希+指针（不放内容）+ 缺口；`--check` 判漂移 |
| `check_dft_pins.py` | **pin 三源三层交叉校验**（0 未命中才放行） |
| `check_library_files.py` | 工程完整性门（Step0 前, 0 缺失才进） |
| `verify_material_receipt.py` | **材料门**（Step3 批次前置）：**软门** 缺口（无类型/无案例/无框架）→ 记录+放行（`--strict` 可恢复 FAIL）；**硬门** 收据不实（声明不实/未声明必读/branch·tier1 矛盾/读证不足）→ FAIL；`--no-read-proof` 用于批次前置，`--audit-rules` 自检 |
| `verify_single_fn.py` | 单函数冒烟（B-001 脚本化, FAIL 停留当前 TM） |
| `verify_awg_params.py` / `verify_relay_trace.py` / `verify_merge_rules.py` / `check_testitems_meta.py` | 收尾门禁（E005 / Cap 反向 E / M 组 / meta 全覆盖） |
| `merge_log.md` | 批次级合并日志（M002 检查） |
| `NU1201.treg` | Trim 参数定义（权威源） |
| `daylog/` | 每日档案（自进化三 Agent 共享数据源） |
| `Library-Functions/shared_functions/` | 跨项目共享子函数库（sub-function-agent 维护） |

---

## 6. 自进化沉淀（知识沉淀层, 独立启用, 不替代主流程）

| Agent | 维护对象 | 触发 | 发布 |
|-------|---------|------|------|
| `rules-agent` | `standards/rules-registry.md` | `/evolve rules` | draft→人工确认→active→同步 verify 脚本 |
| `experience-agent` | `knowledge/experience/` | `/evolve exp` | draft→人工确认→active |
| `sub-function-agent` | `Library-Functions/shared_functions/` | `/evolve fn` | draft→人工确认→发布 |

### 6.1 缺口回收提炼（2026-09-13 新增 · 让缺口下次不再是缺口）

> **凡走软门（无黄金/无框架）写成的 TM，收尾必须回收提炼** —— 否则同类 TM 永远裸写，且裸写风险（TM607-609 类）无法随批次收敛。

1. **从哪来**: Step3 批次前置跑 `verify_material_receipt.py --gap-out <project_dir>/material_gaps.json` → 缺口清单落盘（含 TM + 缺什么）。
2. **提炼成什么**（按 `context-management.md §6` 三档定位）：
   - 有完整可参照函数 → **新 golden**：`L4-Golden-code/<函数名>.cpp`（工程源 Copy，保持原名）+ **同名 `.md` 要点总结**（角色抽象 + 四类关键特殊结构 + 上下电时序 + 测量判定 + 适用范围）
   - 只有方法论 → **新 L3-method**（`L3-method/<参数>.md`）或 **新 L1-chip** —— 即补 **Tier1 通用方法**（这是降上下文的根本）
   - 是通用约束 → **新 specialized rule**（`rules-registry.md`，并同步 verify 脚本）
3. **登记**: `param_type_index.md`（同名联动索引 + 代码案例表）**必须同步**；新增参数类型还要同步 `MATERIAL_REQUIREMENTS` + 跑 `gen_material_status.py` + `--audit-rules`。
4. **用户 review 门（不可省）**: 新增/修订的**总结文档**（`.md` 要点总结、L3-method、L1-chip）**必须由用户 review 确认**才算落地 —— 目前**全部 L4 总结文档尚待用户全量 review**（见 ▶ 待办）。**自审不算过门。**

**每次工作结束必须写 daylog**（`daylog/<当天日期>.md`，六类标记，模板见 `daylog/_template.md`）——即使不跑三 agent 也写，是以后提炼的原料。

---

## 7. 自动同步规则

**每次修正代码或规则错误后，必须同步更新:**
1. 对应的 `knowledge/standards/<file>`（§4 索引里的规则正文，规则改了正文在此，本文件不改）
2. 本文件只在**流程/指针变化**时改（环节增删、脚本换名、规则文件移动）
3. `check-agent.md` 检查清单（如有新的错误模式）
4. 写 `daylog/` 当日条目

> 反例会重复犯错。同步检查点见 §4 索引 + `check-agent.md`。
