# 功能类型索引（Func Type Index）

> **两层索引之一**：本文件 = 功能类型索引层（功能类型 = test-types.md 的「项目结构类型」7 类 → 判据/框架/方法/示例参数）。
> 另一层 = [`param_type_index.md`](param_type_index.md) = 参数类型索引层（具体参数 → L1-chip/L3-method/L4-Golden-code/L5-debug 四件套）。
> **两层互不干涉**：功能类型决定「测什么 + 代码框架」，参数类型决定「参照材料」；每类功能类型对应至少一个参数，参数经 param_type_index.md 关联四件套。
> 判据/测量方法权威源 = `standards/test-types.md`（L1 规则层），本表为索引快照，不重复正文。

---

## 7 类功能类型（判定顺序命中即停）

| # | 功能类型 | 判据（判定条件） | 框架 | 测量方法 | 示例参数 |
|---|---|---|---|---|---|
| 1 | Trim 参数 | ① DFT 含 "Trim" ② Trim 判定列=Y ③ 参数名与 treg 同名（任一命中） | Trim | Trim（sub.cpp measure） | VBG、BUCK HS Gain |
| 2 | Contact | 用户提 OS / Kelvin 测试 | 待确认 | OS/Kelvin（ATE 自供） | OS、Kelvin |
| 3 | OTP/MTP Readback | 用户提 Pre/Post + Readback；**代码级：I2C 读NVM→set_read_back→comp_read(0)→FRESH/BURNNED→get_read_back 出码值，无模拟量测量**（2026-09-07 案例确认） | Readback（三件套五段式） | I2C 回读（OTP 直读窗口 / MTP 控制器+数据端口，MTP 加 CRC） | OTP_PRE_READ、OTP_Read_Pre、MTP_PRE_READ、MTP_TRIM_READBACK |
| 4 | OTP/MTP Burn | **代码级：working→变量→上电配置→数据写+密钥写（逐工位 FRESH真/BURNNED假，禁止重烧）→下电→copy_work_to_prog**（2026-09-07 案例确认） | Burn（与 Readback 同五段式） | 通信协议烧写（地址/键值/假键值=项目协议，勿硬编码） | OTP_BURN、MTP_TRIM_BURN |
| 5 | P2P Leakage | 用户提 P2P | 待确认 | — | — |
| 6 | Leakage | 用户提 leakage 且非 P2P | 待确认 | — | — |
| 7 | 一般测试项目 | 其余（FV-MV / FI-MV / FV-MI / FI-MI / AWG 翻转等） | 普通 | 普通 MeasureVI / AWG | RDSON、UVLO、ZCD |

## 代码框架（结构，2 种 + 待补）

| 框架 | 适用类型 | 结构要点 | 落点 |
|---|---|---|---|
| 普通 | 一般测试项目（#7） | AFX 注释 + CParam + MeasureVI 单函数 | `standards/framework.md` |
| Trim | Trim 参数（#1） | test.cpp（trim_reg + PARAM_NODE + step0~N）+ sub.cpp（measure） | `standards/framework.md` + `treg.md` |
| Readback/Burn | OTP/MTP Readback（#3）+ Burn（#4） | 三件套五段式（AFX参数块→变量声明→供电+通信读/写段→set_read_back/comp 段→get_read_back+SetTestResult 段）；PRE 判 fresh（comp_read(0)→全局 BURN_FLAG）、BURN 密钥闸门、POST 验证 comp_prog_to_read（MTP 加 CRC）；详见 `L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5.md` | `L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5` |
| 待确认 | Contact / P2P / Leakage（#2、#5、#6） | 现无模板 | 待你提供案例后补 |

## 测量方法（怎么测，3 种）

| 测量方法 | 触发条件 | 实现 |
|---|---|---|
| 普通 MeasureVI | 一般测试项目默认 | MeasureVI / Set + Measure |
| AWG | 阈值翻转（Check=Toggle / 需 ramp） | `test_method` 成员函数（rampv_capv / rampi_capv） |
| Trim | Trim 参数 | sub.cpp 的 measure 函数（treg） |

> AWG 与 Trim 是**测量方法**差异，不单独立「功能类型」（与 test-types.md 一致）。

---

## 待补

- [x] OTP Readback / OTP Burn 的**代码框架模板** + 黄金案例（2026-09-07 用户提供 5 案例 → `L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5`，L1/L3 文档同步建立）
- [ ] Contact / P2P / Leakage 三类的**代码框架模板**（现无，标「待确认」）
- [ ] 每类类型「结构」「方法」的详细资料（现指向 framework.md / test-types.md，待其补全后索引丰满）
