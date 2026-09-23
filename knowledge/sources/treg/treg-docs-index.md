# TREG 官方解释文档索引（机台手册同级）

> 本目录是 TREG（Trim Register）类的**官方解释文档**原始 PDF 存放处，与 STS8300 源表手册同级。
> API 正文骨架在 `knowledge/standards/treg.md`；本表只做文档定位与要点索引。
> 来源：TI 内部培训资料（Analog / LP DCDC Converters），Eagle(ETS) 平台时代编写，类本体沿用至今（treg.h/treg.cpp）。

## 文档清单

| 文档 | 页数 | 日期/作者 | 内容定位 |
|------|:---:|-----------|---------|
| `TREG_presentation.pdf` | 36 | 2009-03-16, Anton Winkler | **基础教程**：Trimming 流程、基本概念、TRIM/SEL/ASSY/ASSY_GRP 四段 setup 文件语法、类初始化、手写 pre()/post() 用法、Debug 工具、自适应学习原理 |
| `TREG_execute()_&_trim_groups.pdf` | 32 | Helmut Osterloher | **进阶**：execute() 函数机制、datalogging 方案（标准/替代 msLogData）、TRIM_GRP 三种分组（measure/dependent/in-dependent）、最二乘选步算法、代码示例 |

## setup 文件语法速索引（两文档中最为权威的部分）

> ⚠️ 两份文档成文时该文件叫 `*.ini`；**现行已改用 `.treg` 扩展名**（更有识别性，2026-08-29 用户确认）。语法不变，仅扩展名与解析环境变化（Eagle → STS8300）。treg.h 中 `init()` 注释已写 "loads *.treg file"。

- **TRIM 段** `[参数名]`（大小写敏感）：`Target`（带单位，可带 M/k 等倍率）/ `Table`（逗号分隔；`*` 标记 sot() 后的默认 step；`(step)` 括号包裹=**禁用该 step**） / `Trim_type` = min|nom|max / `Trim_start_learn` / `Trim_step_learn` / `Trim_step_char`。
- **SEL 段** `[*段名]`（`*` 表示后续按 SEL bit 解析）：值可写二进制 `b101`、无符号、HEX `0x00`（≤32bit）；未分配 bit 必须用 dummy SEL（如 `fill_0x01`）补齐。
- **ASSY 段** `[_寄存器名]`（`_` 前缀解析时忽略）：行号 = Assy bit 位置；右侧为 TRIM/SEL 名 + 该参数的 bit 序号；`!` 前缀 = 该 bit 取反。
- **ASSY_GRP 段** `[#组名]`（`#` 前缀忽略）：行号 = 组内位置；右侧 ASSY 名 + 寄存器地址 + 可选 vector label 字符串。
- **TRIM_GRP 段**：`&组名`=measure group（多参数独立 trim、同时测量）、`%组名`=dependent group（一个 trim 影响多参数，一次选最优）、`$组名`=in-dependent group（多 trim 多参数，遍历 step 组合最小二乘）；成员行 `参数名 = #prod_tnum, #char_tnum`；`Target = #tnum` 可直接引用 testlist 限号。
- **[DEFAULT] 段**：全局设置，如 `use_mslogdata = true`（替代 datalogging 方案，省 test#）。

## 关键机制要点（文档原文）

- **信息只存 TRIM/SEL**；ASSY/ASSY_GRP 仅存链接，取值时 just-in-time 拼装、写入时反拼装。
- **五存储区**（per site）：working（最核心，trim 改这里）/ programmed（trim 禁用时拷入 working；用户须保证与 EEPROM 一致）/ start（默认值，start-learn 会改）/ read_back、saved（TREG 不主动用，用户经 save/restore 系列操作）。
- **`pre()` 改变 working 内容**（presentation p24 红字强调）；手写流程 = 写 working→测→`pre()`→再写→再测→`post()`。
- **execute()**：封装正确调用序列（pre/post/table_char + datalog），跳过不必要的 post 测量省时；测量回调原型 `void f(TRIM_NODE*, TREG_MEASURE_FLAG, double* results)`；CHAR/PRE/POST/RETRY 全部要在回调里写寄存器+测量。
  ⚠️ **签名拍板（2026-08-29 用户确认）**：写码一律以 **Shuai 版** `execute(measure_func, SPEC&, funcindex, funclabel, unit_scale, log_level, max_retry_cnt, GRP)` 为准（现行 treg.h 最新重载）；文档中的 TI 原版 `execute(measure_func, tnum_prod, tnum_char, log_level, ...)` 仅作机制原理参考，不用于写码。
- **datalog 命名**（标准方案）：`<NAME>_pre_bit/_pre/_pos_bit/_updated/_theory_/_target_/_pos_/_abs_err/_rel_err`；char 为 `<NAME>_char_*step_N`；`TREG_LOG_TABLE` 加 log trim table、`TREG_LOG_DELTA` 加 delta、`TREG_LOG_DEBUG` 屏幕 print char table。
- **组选步算法**：遍历所有 step 组合，对到 spec 限的 delta 取最小二乘和，可经 `TrimGrpErrorFunc` 用户自定义（加权）。
- **跳过 post 测量铁律**（presentation p35）：省时跳过第二次测量的前提是 trim 参数**必须仍对 spec 限判定**，第二个 TEST 语句不可省。
- **Trim parameter folding / predictability**：建表（table char）先于 trim 执行可避免首件预测误差（±½LSB 折叠现象）。

## Debug 工具（presentation p25-28）

- init 时屏幕输出 TREG initialization 摘要（Trim/SEL/ASSY/GRP 数量）。
- 五类定义错误弹窗：TRIM/BIT_FIELD/REGISTER/GROUP 定义重复或找不到引用，均指向 ini(→treg) 文件与名字。
- `dut.assy.print(site)` → 输出 register.txt（所有 ASSY 当前状态）。
- `TREG_LOG_DEBUG` → ETS Shell 屏 print char table（step/result/table/delta）。

## 本地代码对照

- 类实现：`Library-Functions/treg/treg.h`、`treg.cpp`（现行 STS8300 版，含 Shuai 版 execute 重载与 TRIM_GRP/ASSY_GRP 全量 API）。
- 项目实例：`Project/DALI/input/NU6801QDNB.treg`（setup 文件，`.treg` 扩展名）。
- 使用规则/常见错误（STS8300 视角）：`knowledge/standards/treg.md`。
