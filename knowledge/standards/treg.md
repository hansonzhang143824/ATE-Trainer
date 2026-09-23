# TREG — Trim Register 系统知识库

## 概述

TREG (Test REGister) 是 STS8300 平台的 **Trim 参数管理类**，负责:
- 管理 Trim 参数的 bit 值
- 将多个参数的 bit 值拼装为硬件寄存器（Word Assembly）
- 执行 Trim 流程：CHAR → PRE → 计算最优 step → POST → 写入
- 自适应学习（Adaptive Trim Learning）

## 架构

```
TREG (根类)
├── trim      → TRIM      → TRIM_NODE[]     ← 单个 Trim 参数 (如 bandgap)
├── trim_grp  → TRIM_GRP  → TRIM_GRP_NODE[] ← Trim 参数组
├── sel       → SEL       → SEL_NODE[]      ← 选择位 (如 Thermal Shutdown)
├── assy      → ASSY      → ASSY_NODE[]     ← 寄存器拼装 (如 EFUSE_REG_F0)
└── assy_grp  → ASSY_GRP  → ASSY_GRP_NODE[] ← 寄存器组 (多寄存器设备)
```

**信息流向:**
```
TRIM/SEL 各自存储 bit 值
       ↓
ASSY 将多个参数拼装为完整寄存器值
       ↓
ASSY_GRP 组织多寄存器为逻辑组
       ↓
通过 DCM I2C 写入芯片
```

---

## 数据存储 (STORAGE)

每个 TRIM 参数和 SEL 位有 4 个存储区（per site）:

| 存储 | 含义 | 用途 |
|------|------|------|
| **start** | sot() 后的初始值 | 基线值，不修改 |
| **working** | 当前工作值 | ⭐最重要: trim 操作修改此值 |
| **programmed** | 已烧录值 | trim 被禁用时，从此拷贝到 working |
| **read_back** | 从芯片读回的值 | 已烧录设备的值 |
| **saved** | 临时保存 | save_working() / restore_working() |

**关键操作:**
```cpp
trim_node->get_working(site)       // 读取 working 值
trim_node->set_working(value)      // 设置 working 值
trim_node->copy_read_to_work(site) // 已烧录: 读回值 → working
trim_node->save_working()          // working → saved
trim_node->restore_working()       // saved → working
```

---

## 初始化和全局配置

```cpp
TREG trim_reg;

// 初始化: 加载 .treg 文件
trim_reg.init("NU1201.treg", NUM_SITES, QC_flag, DO_TRIM);

// SOT: 将所有 start 拷入 working
trim_reg.sot();

// 控制 trim 模式
trim_reg.trim.set_trim_allowed(TRIM_MODE);      // 允许/禁止 trim
trim_reg.force_table_char_active(CHAR_MODE);     // 强制建表模式

// EOT: 自适应学习数据处理
trim_reg.eot();
```

---

## ASSY — 寄存器拼装

**作用:** 将分散在多个 TRIM 参数中的 bit 值拼装为完整 8-bit 寄存器值。

```
[_EFUSE_REG_F0]              ← treg 中的定义
0: bandgap = 0               ← bit 0 来自 bandgap 参数
1: bandgap = 1               ← bit 1 来自 bandgap 参数
2: bandgap = 2               ← bit 2 来自 bandgap 参数
3: bandgap = 3               ← bit 3 来自 bandgap 参数
4: iztc_res = 0              ← bit 4 来自 iztc_res 参数
5: iztc_res = 1              ← bit 5 来自 iztc_res 参数
6: iztc_res = 2              ← bit 6 来自 iztc_res 参数
7: iztc_res = 3              ← bit 7 来自 iztc_res 参数

trim_reg.assy("EFUSE_REG_F0").get_working(site)
  → 将 bandgap 4bit + iztc_res 4bit 拼装为 1 字节
```

**常用 ASSY 操作:**
```cpp
INT64 val = trim_reg.assy("EFUSE_REG_F0").get_working(site);  // 读拼装值
trim_reg.assy("EFUSE_REG_F0").set_working(val, site);         // 写拼装值(会反拼装到各参数)
bool ok = trim_reg.assy("EFUSE_REG_F0").comp_read_to_start(site); // 对比验证
```

---

## TRIM_NODE — 单个 Trim 参数

### 获取参数引用

```cpp
TRIM_NODE &node = trim_reg.trim("bandgap");  // 按名称获取
// 或
TRIM_NODE &node = trim_reg.trim[0];          // 按索引获取
```

### execute() — 核心 Trim 流程

```cpp
// 新版本 (Shuai): 使用 SPEC 参数自动 datalog —— ⭐写码唯一权威签名（2026-08-29 拍板）
// 文档(treg-docs-index.md)中的 TI 原版 execute(measure_func, tnum_prod, tnum_char, ...) 仅作机制原理参考
PARAM_NODE.execute(
    measure_func,      // 测量回调函数
    spec,              // SPEC 对象 (用于获取 limits)
    funcindex,         // 函数索引 (用于 StsGetParam)
    funclabel,         // 函数标签
    1,                 // unit_scale (单位缩放)
    0,                 // log_level (TREG_LOG_STD)
    0,                 // max_retry_cnt (重试次数)
    1                  // GRP (分组编号, 默认1)
);
```

**execute() 内部流程:**

```
table_char_active() = true (建表模式):
  save_working()
  for step 0..N-1:
    set_working(step)                                  // 设当前 step
    measure_func(this, TREG_MEASURE_CHAR, results)     // 测量
    table_char(results, step)                          // 记录到学习表
    StsGetParam(PARAM_step{step})->SetTestResult(...)   // datalog
  restore_working()

table_char_active() = false (量产模式):
  // 1. 已烧录设备恢复
  if (!trim_is_active[site]):
    copy_read_to_work(site)

  // 2. PRE 测量
  measure_func(this, TREG_MEASURE_PRE, results)
  StsGetParam(PARAM_pre_value)->SetTestResult(...)

  // 3. 计算最优 step
  pre(results, true)  // 搜索最优 step, 更新 working

  // 4. POST 测量 (如果 trim 改变了 working)
  if (DO_TRIM && updated_by_trim()):
    measure_func(this, TREG_MEASURE_POST, results)

  // 5. RETRY 循环
  for i in 0..max_retry_cnt:
    check_need_retry(limits, results)
    pre(results)
    if updated: measure_func(this, TREG_MEASURE_RETRY, results)
    else: break

  // 6. 记录 POST 结果
  post(results)
  StsGetParam(PARAM_post_value)->SetTestResult(...)
```

### 其他关键方法

```cpp
node.get_working(site)          // 当前 trim step 值 (0, 1, 2...)
node.get_steps()                // trim step 总数 (如 16)
node.get_target(site)           // trim 目标值
node.get_table_value(step)      // trim table 中 step 对应的值
node.get_pre_reading(site)      // PRE 测量值
node.get_post_reading(site)     // POST 测量值
node.get_guessed_final(site)    // 预测最终值
node.updated_by_trim(site)      // trim 是否改变了 working
```

---

## TREG_MEASURE_FLAG — 测量标志

```cpp
enum TREG_MEASURE_FLAG {
    TREG_MEASURE_NONE  = -1,  // 未使用
    TREG_MEASURE_CHAR,        // 建表测量 (每个 step 一次)
    TREG_MEASURE_PRE,         // 预测量 (找最优 step 前)
    TREG_MEASURE_POST,        // 后测量 (trim 完成后验证)
    TREG_MEASURE_RETRY        // 重试测量 (首次未达标)
};
```

---

## measure 函数模板

```cpp
void measure_XXX(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    // ====== 确定需要几个 EFUSE 寄存器 ======
    // 查 .treg 文件: 参数跨了几个 [_EFUSE_REG_Fx]
    // 1 个寄存器 → working_value1
    // 2 个寄存器 → working_value1 + working_value2

    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };  // 如有第 2 个

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == WS)
    {
        // ====== 读取 working 值 + 处理已烧录 ======
        FOR_EACH_SITE(site)
        {
            // PRE/POST 时: 已烧录设备恢复烧录值
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);

            // 从 ASSY 读取拼装后的寄存器值
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_Fx").get_working(site);
            // working_value2[site] = ...  // 如果跨多个寄存器

            // 记录 working 值 (用于 offline 验证)
            sim_step[site] = trim_node->get_working(site);
        }

        // ====== 写入 EFUSE 到芯片 (I2C, 8-bit) ======
        dcm.I2CWriteData(DEV_ADDR, 0xFx, 1, working_value1);
        // dcm.I2CWriteData(DEV_ADDR, 0xFy, 1, working_value2);
        delay_us(2000);

        // ====== 配置芯片测试寄存器 ======
        // [每个 step 变化的部分 — 放这里]
        I2CWriteSameData(DEV_ADDR, 0xXX, 0xXX);
        // ...

        // ====== 执行测量 ======
        // 注意: CHAR/PRE/POST/RETRY 全都需要测量!
        <ResourceName>.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = <ResourceName>.GetMeasResult(site, MVRET);
        }
    }
}
```

**关键规则:**
- ALL flags (CHAR/PRE/POST/RETRY) 都需要写 EFUSE + 测量
- `sim_step` 用于 offline 验证 trim 逻辑
- EFUSE 寄存器必须查 .treg 确认，不可照抄
- 封装数 = 参数跨的 EFUSE 寄存器数
- I2C 通信协议是 8-bit → EFUSE 按 8 位组织

---

## test.cpp 中的 Trim 函数模板

```cpp
DUT_API int TMxxx_Trim_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PARAM_step0 ... PARAM_stepN = ...;
    CParam *PARAM_pre_value   = StsGetParam(funcindex, "PARAM_pre_value");
    CParam *PARAM_pre_bit     = StsGetParam(funcindex, "PARAM_pre_bit");
    CParam *PARAM_post_bit    = StsGetParam(funcindex, "PARAM_post_bit");
    CParam *PARAM_updated     = StsGetParam(funcindex, "PARAM_updated");
    CParam *PARAM_guessed     = StsGetParam(funcindex, "PARAM_guessed");
    CParam *PARAM_target      = StsGetParam(funcindex, "PARAM_target");
    CParam *PARAM_post_value  = StsGetParam(funcindex, "PARAM_post_value");
    CParam *PARAM_post_rt     = StsGetParam(funcindex, "PARAM_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("<treg参数名>");

    // Step 1: 继电器
    // Step 2: 上电
    // Step 3: 静态寄存器配置 (entertestmode + 不变的寄存器)
    // Step 4: FPVI 大电流初始化 (如有, FV=0→FI=0→Clamp)
    // Step 5: execute
    PARAM_NODE.execute(measure_XXX, spec, funcindex, funclabel, 1, 0, 0, 0);
    // Step 6: FPVI 关闭 (如有)
    // Step 7: 下电

    return 0;
}
```

**寄存器配置放置原则:**
| 放 test.cpp | 放 sub.cpp measure 函数 |
|------------|------------------------|
| 不变的静态配置 (entertestmode, 工作模式) | 每次 step 可能不同的配置 |
| 供电相关寄存器 | Trim 相关的寄存器 |

---

## treg 文件结构

```ini
[bandgap]                    ← TRIM 参数名
Target     = 1.223           ← 目标值
Table      = ...             ← step 对应值 (CHAR 模式或 simulate)
Trim_type  = nom             ← min / nom / max

[_EFUSE_REG_F0]              ← ASSY 寄存器
0: bandgap = 0               ← bit 0 来自 bandgap 参数
1: bandgap = 1
...
7: iztc_res = 3

[_EFUSE_REG_FA]              ← 一个参数可跨多个寄存器
6: buck_hsfet_gain = 0
7: buck_hsfet_gain = 1
```

---

## 自适应 Trim 学习

| 参数 | 含义 | 默认值 |
|------|------|:---:|
| `Trim_start_learn` | 延迟次数后开始调整默认 step | 20 |
| `Trim_step_learn` | 运行平均的样本数 (调整 step 值) | 50 |
| `Trim_step_char` | 每 N 次做一次完整建表 | 30 |

---

## 常见错误

| 错误 | 正确 |
|------|------|
| 只处理 PRE/POST flag | CHAR/PRE/POST/RETRY 全部处理 |
| 照抄 `EFUSE_REG_F0` | 查 treg 确认参数实际在哪个寄存器 |
| 以为 execute 只调一次 measure | PRE + 每个 step + POST + RETRY 多次调用 |
| EFUSE 写一次即可 | 每次 measure 调用都要写 (step 不同) |
| 寄存器全放 test.cpp | step 变化的放 sub.cpp, 静态的放 test.cpp |
| sim_step 可有可无 | offline 验证关键数据 |
| 只用一个 working_value | 跨 N 个 EFUSE 寄存器需要 N 个 working_value |
