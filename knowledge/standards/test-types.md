# 测试类型识别（项目结构类型）

> **无歧义分类**：DFT 项 / 测试意图 → **项目结构类型**（7 类，按测试机制）→ **具体参数类型**（被测参数名）。
> - 项目结构类型决定**测什么**（测试机制）与**代码框架**；
> - 具体参数类型决定**参照材料**（`references/L4-Golden-code|L1-chip|L3-method|L5-L5-debug/<参数>`，同名联动，debug 按需）与**测量方法**（见 §测量方法）。
> - 判定按下列顺序**命中即停**，无模糊地带。

---

## 两级分类模型

```
DFT 项 / 测试意图 ──识别(无歧义)──▶ 项目结构类型 (7类, 决定机制+框架)
                                        │
                                        ▼
                                  具体参数类型 (被测参数名, 决定参照+测量方法)
                                        │
                                        ▼
                      references 四件套 (同名联动): L1-chip/<参数>(是什么) + L3-method/<参数>(怎么测) + L4-Golden-code/<参数>(长啥样) + L5-debug/<参数>(怎么排查, 按需)
```

**示例（ZCD）**：ZCD 测「ramp 电流 → 阈值翻转」→ 项目结构类型 = **一般测试项目**（AWG 翻转）→ 测量方法 = **test_method**（`rampi_capv`）→ 具体参数 **ZCD** → 参照 `chip/ZCD` + `L3-method/ZCD` + `code/ZCD`。

---

## 具体参数类型（11 类，决定参照材料）

> 具体参数类型 = 被测参数的**族**，决定参照材料四件套（`L1-chip/<族>` + `L3-method/<族>` + `L4-Golden-code/<族>` + `L5-debug/<族>` 同名联动，debug 按需）。
> 11 类清单（2026-08-16 用户提供），16 项归并为 11 类：Leakage 3 子类（P2P/ABS/Operation）、OTP/MTP 3 子类（Pre_Read/Burn/Post_Read）、OS+Kelvin 合 1 类，其余各 1 类。

| # | 具体参数类型（族） | 典型具体参数 | 机制一句话 | 详解 |
|---|---|---|---|---|
| 1 | RDSON | RDSON | 导通电阻 | `references/L1-chip/RDSON.md` + `L3-method/RDSON.md` |
| 2 | CurrentSense | Gain / Vos (Offset) | 电流采样/检测（核心参数 Gain + Offset/Vos，Vcs = Rsns×Imirror + Vos） | `references/L1-chip/CurrentSense.md` + `L3-method/CurrentSense.md` |
| 3 | ADC | ADC | 模数转换 | — |
| 4 | UVLO | UVLO / OVP / PRST / VBAT_LOW / RECHG | 欠压/过压锁定阈值（ramp 电压 → monitor 翻转） | `references/L1-chip/UVLO.md` + `L3-method/UVLO.md` |
| 5 | Current Threshold | ZCD / IPeak | 电流阈值（ramp 电流 → monitor 翻转） | `references/L1-chip/Current-Threshold.md` + `L3-method/Current-Threshold.md` |
| 6 | Freq Related | OSC | 频率相关 | — |
| 7 | AMUX | AMUX | 模拟多路复用 | — |
| 8 | close-loop | — | 闭环 | — |
| 9 | 接触 OS / Kelvin | OS / Kelvin_Test | 开短路/接触（ATE 自供方法） | — |
| 10 | Leakage | P2P leakage / ABS leakage / Operation leakage | 漏电流 | — |
| 11 | OTP/MTP | Pre_Read / Burn / Post_Read | 熔丝烧录 + 回读 | — |

---

## 项目结构类型判定表（7 类，按序命中即停）

> 判定来源分两类：**DFT 字段**（可脚本化，如 Trim）· **测试意图/用户指令**（解析 DFT Notes 或对话，如 Contact/OTP/Leakage）。
> 命中即停：从第 1 行往下，第一个满足判定条件的类即归属。

| # | 项目结构类型 | 判定条件 | 框架 | 典型参数/示例 |
|---|---|---|---|---|
| 1 | **Trim 参数** | ① DFT 含 "Trim" 字样（不区分大小写）② Trim 判定列 = Y ③ 参数名与 treg 文档 trim 参数同名 —— 三者**任一命中** | Trim | VBG、BUCK HS Gain |
| 2 | **接触项目 Contact** | 用户提到 OS 测试（或二极管测试）→ **OS 测试**；用户提到 Kelvin 测试 → **Kelvin 测试**（一般不在 DFT 写出，由 ATE 自供测试方法） | 待确认 | OS、Kelvin |
| 3 | **OTP/MTP Pre/Post Readback** | 用户提到 Pre/Post + Readback；**代码级：I2C 读 NVM → `set_read_back` → `comp_read(0)` → FRESH/BURNNED → `get_read_back` 出码值，无模拟量测量**（2026-09-07 案例确认） | **Readback 五段式**（`func_type_index.md` #3 + `L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5`） | OTP_PRE_READ、OTP_Read_Pre、MTP_PRE_READ、MTP_TRIM_READBACK |
| 4 | **OTP/MTP Burn** | 用户提到 OTP/MTP Burn；**代码级：working→变量→上电配置→数据写+密钥写（逐工位 FRESH 真/BURNNED 假，禁止重烧）→下电→`copy_work_to_prog`**（2026-09-07 案例确认） | **Burn 五段式**（同 Readback；`func_type_index.md` #4） | OTP_BURN、MTP_TRIM_BURN |
| 5 | **P2P Leakage** | 用户提到 P2P | 待确认 | — |
| 6 | **Leakage** | 用户提到 leakage 且**非** P2P；分 ABS leakage / Operation leakage | 待确认 | ABS leakage、Operation leakage |
| 7 | **一般测试项目** | 其余（FV-MV / FI-MV / FV-MI / FI-MI / AWG 翻转等） | 普通 | RDSON、ZCD、UVLO |

---

## 测量方法（具体参数类型层，非项目结构类型）

> 项目结构类型定「测什么」，测量方法定「怎么测」。**AWG 与 Trim 是测量方法差异，不再单独立类。**

| 测量方法 | 触发条件 | 实现 |
|---|---|---|
| 普通测量（四种基本 IV） | 无 AWG 时按 FV-MV / FI-MV / FV-MI / FI-MI 之一 | `MeasureVI` / Set + Measure |
| AWG 测量（增项） | Check=Toggle / 需 ramp 翻转 | **`test_method` 成员函数**（`rampv_capv` / `rampi_capv`） |
| Trim 测量 | Trim 参数 | 在 **sub.cpp 的 measure 函数**中实现（见 `treg.md` + Trim 规则） |

> **AWG 是增项，不是替代（R-AWG，2026-08-27 用户拍板）**：AWG（ramp + toggle capture）是相对于四种基本 IV 测量（FV-MV/FI-MV/FV-MI/FI-MI）的**增项**。判定先问「有没有 AWG」：**无 AWG → 按四种基本 IV 之一写，禁止按 AWG 写**；**有 AWG → 按 AWG 写，可与基本 IV 同时存在（同测例既有静态 IV 又有 ramp 捕获），也可只有 AWG**（如 TM616：ramp AMUX → capture I(ATEST0)，observei 即测量，无独立 measure）。对应 YAML：`measure`（基本 IV，0..N）与 `observe`（AWG 捕获，0..N）相互独立、可共存可单有。

### 阈值测试 = AWG（判定方法）

> **凡是阈值测试都是 AWG**：在 PIN 上或 PIN 之间 ramp 电压/电流 → monitor 其他 PIN 的 Toggle 翻转。

判定方法（可结合，命中即 AWG）：
1. **参数名特征**：DFT 参数名含 UVLO / OVP / PRST / ZCD / IPeak / VBAT_LOW / RECHG 等
2. **根本方法**：看 ramp 条件 —— 时长 `1e-3` 表示 ramp，或 DFT 描述写了 ramp
3. 两者结合，有 ramp 条件即 AWG
4. **testType 覆盖（2026-08-27 拍板，权威）**：`gen_test_conditions.py` 检测到 power 同 pin 首尾相等两段斜坡(升+降) → test_conditions.yaml 的 `testType` 强制 `toggle`，覆盖 DFT 声明（TM210/211、TM615/616 命中）；Step3 框架分类**以 YAML 覆盖后值为准**（DFT OVERVIEW 的 testType 可能声明 normal/trim 但实际是 Toggle）
5. **ATEST 静态测量守卫（2026-08-30，gen_testitems_meta.py is_toggle）**：Check 只含 `V(ATESTx)`/`I(ATESTx)`（无 DTEST）、Dynamic 空、vset 无同 pin 多值 → **不算 toggle**（纯 ATEST mux 静态测量）——参数名含 `_VTH`/`_CMP` 也不触发名字启发式（TM1008 VREF_VTH_CMP 误判修正、TM100 顺带修正）
6. **Trim 列空白守卫（2026-08-30）**：OVERVIEW Trim 判定须 `strip()` 后判空 —— **Trim 列为空格 `' '` 是 DFT 单元格格式噪声，非真 Trim 标记**（TM1100 + TM212-217 空格 truthy 误判 trim 修正）；真 Trim 判定仍按上表 #1 三条件任一命中

---

## 待确认

- [x] ~~Contact / OTP Readback / OTP Burn / P2P / Leakage 五类~~ → **修正（2026-09-13）**：OTP Readback / OTP Burn 已于 **2026-09-07** 建立代码框架（五段式）+ 5 个黄金案例（`L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5`），`func_type_index.md` 标 `[x]`；本文件此条**曾经过期**。**现真正无框架的只有 3 类**：
  - [ ] **Contact（#2）** / **P2P Leakage（#5）** / **Leakage（#6）** 的**代码框架**（现无模板）
  - 机制：无框架走**软门**——记录缺口 + 按 DFT + 规则写码（`nuvolta-codegen.md` Step3）
- [ ] Leakage 内部 ABS vs Operation 的**细分判定条件**（当前仅靠参数名/Notes 区分）
- [ ] 判定脚本化落地：DFT 字段类（Trim）可机械判定；测试意图类（Contact/OTP/Leakage）需解析 Notes，待定落地形式

> 机器可读副本：`knowledge/references/material_status.json` 的 `testTypes` 段（由 `gen_material_status.py` 生成，含 `available` 标志）。改本表须同步该表的 `TEST_TYPE_FRAMEWORKS` + 跑 `--check`。
