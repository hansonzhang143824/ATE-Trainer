# NuvoltaAI 测试代码生成规则（完整版本）

## ⚠️ 强制性起飞前仪式（写代码前必须执行）

**在编写任何测试代码之前，你必须：**
1. ✅ 阅读并理解本文件的全部内容
2. ✅ 阅读 project_memory.md 的 Lessons Learned 部分
3. ✅ 阅读本文件顶部的「常见错误/反模式」列表
4. ✅ 对于每个测试项，逐条检查「CHECK:」规则并打印确认

---

## 🔴 常见错误/反模式（每次犯错后立即添加）

| 错误编号 | 错误描述 | 正确模式 | 首次发现 |
|----------|----------|----------|----------|
| E001 | Trim参数只定义了单个参数指针，缺少step0~stepN和固定后缀参数 | 根据treg位数定义所有step参数 + 8个固定后缀参数 | TM125/TM130 |
| E002 | Trim测试直接调用MeasureVI() | Trim测试必须使用TRIM_NODE.execute()模式 | TM125/TM130 |
| E003 | VAC2/VAC3测试缺少继电器连接 | VAC2需要K36_VAC_SHARE2，VAC3需要K35_VAC_SHARE | TM109/TM110 |
| E004 | 测试函数参数定义不在AFX注释之间 | 所有CParam定义必须放在//{{AFX_STS_PARAM_PROTOTYPES和//}}AFX_STS_PARAM_PROTOTYPES之间 | 通用 |
| E005 | AW测试只定义了单个参数 | AW测试固定包含3个参数：Parm_Rise、Parm_Fall、Parm_Hys，必须全部定义 | TM105/TM106/TM108/TM109/TM110 |

---

## 🟡 测试类型识别规则（CHECK: 每个测试项必须确定类型）

### 如何识别AWG/Toggle测试？
**CHECK: DFT.csv中Type列包含"Toggle"的测试项都是AWG测试**

| 识别条件 | 测试类型 | 参数数量 | 测量方式 |
|----------|----------|----------|----------|
| Trim=Y | Trim测试 | step0~stepN + 8个固定后缀参数 | TRIM_NODE.execute() |
| Type包含"Toggle" | AWG/Toggle测试 | 3个参数：Parm_Rise、Parm_Fall、Parm_Hys | test_method.rampv_capv/rampi_capv |
| 其他情况（MI/MV/MV&MI） | 普通测试 | 根据DFT.csv中ShortName定义 | 直接MeasureVI或set+measure |

### AWG测试参数命名规则
- 参数1：`ShortName_Rise` → 上升沿阈值（ramp从低到高，TRIG_FALLING触发）
- 参数2：`ShortName_Fall` → 下降沿阈值（ramp从高到低，TRIG_RISING触发）
- 参数3：`ShortName_Hys` → 迟滞 = Rise - Fall（自动计算）

---

## 0. 测试流程总则

**CHECK: 是否已阅读DFT.csv、资源分配表.csv和treg文件？**
1. 首先需要理解三张表：DFT.csv、资源分配表.csv 和 *.treg 文件（trim参数使用）
2. 创建测试函数时候，首先需要去查找DFT.csv 这张表，根据表中的内容，判断测试函数有多少个参数需要被生成，生成函数的框架参考：NU函数框架。
3. 接下来需要查找资源分配表.csv来确认有哪些继电器需要操作。
4. 对于Trim类型的测试项，需要读取*.treg文件来确定trim参数所在的EFUSE_REG封装。
5. 针对每个参数，都执行完整的测试流程，每个参数是独立的完整的执行完成测试流程，需要参考： NU参数测试流程
6. 最后参考：NU检查规则来修改错误， 每条规则打印后都打印一下****规则已经完成

## 1. 文件组织规则

### 1.1 文件分工
- **test.cpp**：存放所有测试函数（TMxxx），包括Trim测试的入口函数
- **sub.cpp**：存放所有Trim测量函数（measure_xxx）

### 1.2 Trim测量函数命名规则
- 函数名格式：`measure_` + 参数名（ShortName）
- 例如：参数名为`HP_VBG`，测量函数名为`measure_HP_VBG`
- 测量函数签名：`void measure_xxx(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)`

### 1.3 treg文件解析规则（Trim参数专用）

treg（Trim Register）是芯片Trim参数的定义文件，包含三类核心内容：**Trim参数定义**、**Selection Bit定义**和**封装（assy）定义**。

#### 1.3.1 Trim参数定义

**格式：** 以`[参数名]`开头，包含以下字段：

| 字段 | 含义 | 说明 |
|------|------|------|
| `[参数名]` | 参数名称 | 放在`[]`内，如`[bandgap]`、`[iztc_res]` |
| `Target` | 目标值 | Trim希望达到的目标值，如`Target = 1220`（1220mV） |
| `Trim_type` | Trim类型 | 一般为`nom`（标称值），其他如`abs`、`rel`等不用关心 |
| `Table` | 初始化表 | 元素数量与step数量相同，一般不用管 |
| `Trim_start_learn` | 二次加速累计次数 | trim加速相关，暂时忽略 |
| `Trim_step_learn` | trim平均值基数 | 最近多少个芯片的值做平均，暂时忽略 |
| `Trim_step_char` | 加速数量 | 多少颗好品后会加速，暂时忽略 |

**位数计算：**
- 从step数量计算：2^n = step数 → n = 位数
- 例如：step范围0~15（16个step）→ 4位（2^4=16）
- 例如：step范围0~63（64个step）→ 6位（2^6=64）

**示例：**
```
[bandgap]
Target = 1220
Trim_type = nom
;               	  0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
Table = *0,0.001,0.002,...,0,-0.001,...,-0.007
Trim_start_learn = 50
Trim_step_learn = 50
Trim_step_char = 96
```

#### 1.3.2 Selection Bit定义

**格式：** 以`[*SELECTIONS]`为开始标志

| 项目 | 说明 |
|------|------|
| 开始标志 | `[*SELECTIONS]` |
| 格式 | `参数名 =bxx` |
| 位数 | `b`后面有几位数字就是几位 |
| 默认值 | `b`后面的数字就是默认状态 |

**示例：**
```
[*SELECTIONS]
ibus_off_term_flt =b0     ; 1位，默认0（终端滤波器禁用）
addr_trim =b0             ; 1位，默认0
part_id_trim =b0          ; 1位，默认0
```

**Trim vs Selection Bit核心区别：**

| 特性 | Trim（微调参数） | Selection Bit（选择位） |
|------|-----------------|----------------------|
| 目的 | 微调校准到目标值 | 选择固定配置 |
| 过程 | 每个芯片单独trim，找到最佳step | 所有芯片设置相同值 |
| 结果 | 每个芯片的step可能不同 | 所有芯片的状态相同 |
| 示例 | bandgap、iztc_res | ibus_off_term_flt、addr_trim |

#### 1.3.3 封装（assy）定义

**目的：** 将Trim参数和Selection Bit按物理寄存器的8位进行打包，方便一次性写入芯片

**格式：** 以`[_EFUSE_REG_Fx]`为标志（[]内全大写，起始位是`_`）

| 项目 | 说明 |
|------|------|
| 标志格式 | `[_EFUSE_REG_Fx]` |
| 物理地址 | `_EFUSE_REG_F0` → I2C地址 `0xF0` |
| 行格式 | `assy位位置: 参数名 = 参数内部位` |

**封装行格式解析：**
```
开头数字:  参数名  = 结尾数字
  ↑          ↑        ↑
  │          │        └── 参数内部的位位置（从LSB到MSB）
  │          └── 参数名称
  └── assy封装内的物理位位置（0~7）
```

**示例：**
```
[_EFUSE_REG_F0]
0:  bandgap = 0    ; bandgap的bit0放在封装的bit0
1:  bandgap = 1    ; bandgap的bit1放在封装的bit1
2:  bandgap = 2    ; bandgap的bit2放在封装的bit2
3:  bandgap = 3    ; bandgap的bit3放在封装的bit3
4:  iztc_res = 0   ; iztc_res的bit0放在封装的bit4
5:  iztc_res = 1   ; iztc_res的bit1放在封装的bit5
6:  iztc_res = 2   ; iztc_res的bit2放在封装的bit6
7:  iztc_res = 3   ; iztc_res的bit3放在封装的bit7
```

**工作流程：**
1. Trim找到最佳step → 假设bandgap最佳step=8（二进制1000）
2. 根据封装定义计算值：bit[3]=1, bit[0-2]=0 → 0x08
3. 向物理寄存器0xF0写入0x08 → 芯片进入最佳状态

#### 1.3.4 合并封装

**格式：** `[_EFUSE_REG_REGISTER]`

**作用：** 将所有独立的assy（`_EFUSE_REG_F0`~`_EFUSE_REG_FF`）合并成一个完整的寄存器空间

**优势：**
- **统一访问**：可以直接访问合并后的assy，一次性查看所有参数状态
- **单独访问**：也可以单独访问某个独立assy（如`_EFUSE_REG_F0`）
- **数据共享**：两者数据是同步的，修改任意一个都会反映到另一个

**映射关系：**
- `[_EFUSE_REG_REGISTER]` 的bit 0~7 → `[_EFUSE_REG_F0]` 的bit 0~7
- `[_EFUSE_REG_REGISTER]` 的bit 8~15 → `[_EFUSE_REG_F1]` 的bit 0~7
- 以此类推...

#### 1.3.5 working_value数量确定

根据参数分布的封装数量确定`working_value`的数量：
- 1个封装：只需要`working_value1`
- 2个封装：需要`working_value1`和`working_value2`
- 3个封装：需要`working_value1`、`working_value2`和`working_value3`

#### 1.3.6 三个核心寄存器

treg系统中有三个核心寄存器，用于管理Trim参数的生命周期：

| 寄存器 | 作用 | 说明 |
|--------|------|------|
| **working** | 当前寄存器的值（动态） | Trim参数测完后，working中存的就是最佳step，会不断变化 |
| **programmed** | 编程后的值（固化） | 所有Trim做完后，把working转到programmed，作为最终编程值 |
| **read_back** | 回读值 | 用来存从芯片物理地址中读取的值，用于验证编程是否成功 |

**工作流程：**
1. **测量阶段**：working存储当前的trim step（不断变化）
2. **烧录阶段**：只有实际烧录芯片时才执行working → programmed（固化），测试阶段不执行此步骤
3. **验证阶段**：烧录后从芯片物理地址读取值到read_back，比较programmed和read_back的值是否相同，确认烧录内容与实际烧录一致

### 1.4 Trim测量函数模板（sub.cpp）

```cpp
void measure_xxx(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
{
    double qvm_results[SITE_NUM] = { 0 };
    INT64 sim_step[SITE_NUM] = { 0 };
    DWORD working_value1[SITE_NUM] = { 0 };
    // 如果有多个封装，添加working_value2、working_value3...
    
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == TempChar || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
            {
                if (BURN_FLAG[site] == BURNNED)
                {
                    trim_node->copy_read_to_work(site);
                }
            }
            // 根据封装数量读取working_value
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
            // working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
            sim_step[site] = trim_node->get_working(site);
        }

        // 根据封装数量写入I2C寄存器
        dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
        // dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value2);
        delay_us(2000);
        
        // 测量 - 根据Check类型选择MV或MI
        /* 资源 */.MeasureVI(200, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = (/* 资源 */.GetMeasResult(site, /* MVRET或MIRET */));
        }
    }
}
```

## 2. NU双表解析原则（核心）

生成函数时，必须 **同时完整不遗漏的读取并解析**以下两张表：

### 2.1 DFT.csv 表的使用方法：
第一行是表头，从第二行到最后一行就是各个测试项目的信息， 其中：
    * Function Name就是测试项的名称，补全测试项目时候，需要保证该名称唯一，并且与DFT.csv中的Function Name相同。
    * ShortName 是参数名，生成 `CParam*`， 每个参数都需要生成一个 `CParam*` 变量。
    * ExpectValue、Unit（用于单位换算），暂时忽略。
    * Hardware_initial 是上电的动作，参考：NU上电规则
    * Software_initial（I²C 或软件初始化脚本）：直接copy内容粘贴到程序中，放在Hardware_initial 之后
*Dynamic:这个是对于测试源的补充上电，参考：NU补充上电规则
    * Check（定义测量对象：电压、电流、阻抗等），参考：NU测量规则
    * Trim：如果为Y，则该参数为trim参数，参考：NU Trim规则

### 2.2 补全测试项目时候，需要按照参数名字，一个一个的补全，按照NU参数测试流程，生成代码，不同参数之间不需要用{}分隔，按照顺序依次填写就可以了。

### 2.3 资源分配表.csv使用方法
首先如果需要对于一个Pin 进行Poweron, Measure, Poweroff操作，首选需要将Pin Name 和源表进行绑定：例如VBAT的源表是VBAT_ACM，那么在资源分配表中就需要将VBAT_ACM和VBAT进行绑定。
第二，如果需要测量多个Pin，那么就需要在资源分配表中将多个Pin进行绑定，例如测量VBAT和VIN，那么就需要在资源分配表中将VBAT和VIN进行绑定。
第三，如果需要测量多个Pin的多个资源，那么就需要在资源分配表中将多个资源进行绑定，例如测量VBAT和VIN的两个资源，那么就需要在资源分配表中将VBAT_ACM和VIN_ACM进行绑定。
绑定方法参考：NU源表绑定规则。

## 3. NU参数测试流程

每次执行这个流程，6个部分均需要执行
1. **Connect**：测试前首先闭合所有满足要求的继电器，执行NU继电器闭合规则。
2. **Power On**：对于所有参与的PIN强制电压/电流， 参考：NU上电规则。
3. **Register Config**：通过 I²C 等方式配置 DUT，方法是直接copy Software_initial的内容放到power on之后。注意：Software_initial中的所有内容（包括//后面的注释）都必须完整保留，不能删除或修改I2CWriteSameData行后面的注释。
4. **Measure**：采集电压/电流/波形等，参考：NU测量规则。如果是trim参数，调用sub.cpp中的测量函数。
5. **Power Off**：所有参与的PIN对应的源表下电关闭，继电器不做改动参考：NU下电规则。
6. **check code**：代码生成完毕后，根据 NU检查规则 检查并修改。

### 3.1 连续测试参数合并优化规则（新增）

**核心原则：同一个测试函数内的多个参数，如果上电配置相同，可以合并上电和下电流程，提高测试效率。**

**适用条件：**
1. 多个参数在同一个测试函数内（同一个Function Name）
2. 上电配置（vset/iset指令）完全相同
3. 继电器配置相同
4. 测量对象相同或可以共享

**优化策略：**
1. **合并上电**：只执行一次上电流程，所有参数共用
2. **合并下电**：所有参数测试完成后一起下电
3. **entertestmode优化**：上电后只调用一次entertestmode()，后续参数直接配置寄存器（芯片在上电状态下测试模式保持有效）
4. **寄存器配置**：每个参数的寄存器配置独立执行

**优化前（低效）：**
```cpp
// 参数1：上电 → entertestmode → 配置寄存器 → 测量 → 下电
// 参数2：上电 → entertestmode → 配置寄存器 → 测量 → 下电
```

**优化后（高效）：**
```cpp
// 公共部分：上电（只执行一次）→ entertestmode（只执行一次）
// 参数1：配置寄存器 → 测量
// 参数2：配置寄存器 → 测量
// 公共部分：下电（只执行一次）
```

**验证规则：**
- 芯片上电后进入测试模式，只要不下电，测试模式保持有效
- 下电后寄存器清空，芯片回到初始状态
- 寄存器配置可以在测试模式下重复修改，无需重新进入测试模式

**注意事项：**
1. 如果参数之间需要不同的继电器配置或上电配置，则不能合并
2. 合并后需要确保参数之间没有相互干扰
3. 测量结果需要分别保存到各自的参数变量中

## 4. NU资源绑定规则

1. 每个参数测试时，都需要将所有参与测试的Pin与源表进行绑定，都需要在资源分配表中进行绑定，绑定方法如下：
在资源分配表.csv中查找Pin Name，然后在Resource Name中找到源表的名字，同时在Type中获取资源类型。

## 5. NU继电器闭合规则

### 核心原则（根本原因）

继电器配置的根本原因是**引脚与源表的绑定关系**。当多个引脚共用同一个源表（Resource Name）时，只有一个引脚是"默认连接"（Connect Relay to Resource=Default），其他引脚需要额外的继电器来切换连接。这就是为什么VAC2需要K36_VAC_SHARE2、VAC3需要K35_VAC_SHARE的根本原因。

### 具体规则

1. 继电器闭合，必须采用cbite.SetOn()指令，不能使用其他方式。要求是括号内所有变量统一放在括号内，用逗号分隔，最后结尾处是-1。举例：cbite.SetOn(K30_VBAT_Cap, -1); 之后等待3ms，delay_ms(3);
2. 如果有多个继电器，则需要统一放置在同一个括号内，用逗号分隔，最后结尾处是-1。举例：cbite.SetOn( K30_VBAT_Cap, K30_VBAT_PullUp, -1); 之后等待3ms，delay_ms(3);
3. **如果不需要闭合任何继电器**，必须使用 `cbite.SetOn(-1);`，不能省略不写。之后等待3ms，delay_ms(3);
4. cbite.SetOn内的继电器输入需要排查以下各项规则要求，
   1. **Connect Relay to Resource（资源继电器）**：这是引脚绑定到源表的核心继电器。在资源分配表.csv中查找Pin Name，在本行中找到Connect Relay to Resource列。如果值为"Default"，说明该引脚是源表的默认连接，不需要额外继电器；如果有K字开头的继电器，说明该引脚需要通过这个继电器才能连接到源表，必须闭合。**注意**：多个Pin即使共用同一个源表（Resource Name相同），每个Pin也必须单独查找自己那一行的Connect Relay to Resource，不能因为共用源表就认为继电器相同。例如VAC1、VAC2、VAC3共用VAC123_ACM，但它们的Connect Relay to Resource分别是Default、K36_VAC_SHARE2、K35_VAC_SHARE，必须逐个核对。
   2. 在资源分配表.csv中查找Pin Name，在本行中找到Connect Relay to FPVI_BUS，如果是空的就不需要做任何处理，如果有K字开头的继电器，说明有总线继电器，就去检查NU浮动源规则，如果满足浮动源规则，把浮动源继电器连接进来闭合。
   3. 在资源分配表.csv中查找Pin Name，在本行中找到P2P Relay，如果是default就不需要做任何处理，如果有K字开头的继电器，说明有P2P继电器，如果测试项目说明是P2P测试项目，就需要执行NU继电器闭合规则，把P2P继电器连接进来闭合，否则无需闭合。
   4. 在资源分配表.csv中查找Pin Name，在本行中找到Cap2 Relay，如果是default就不需要做任何处理，如果有K字开头的继电器，说明有电容继电器。注意：如果该Pin是测量电流（MI）的对象，则电容继电器不能闭合（电容会影响电流测量的精度和稳定性）；只有测量电压（MV）时才闭合电容继电器。
   5. 在资源分配表.csv中查找Pin Name，在本行中找到PULL_UP RESISTOR，如果是default就不需要做任何处理，如果有K字开头的继电器，同时在DFT.csv中找到该参数的Check，如果是toggle,就需要执行NU继电器闭合规则连接进来闭合。

### 5.1 继电器配置检查清单（新增）

**必须严格按照以下步骤检查继电器配置，避免遗漏或错误：**

| 序号 | 检查步骤 | 检查内容 | 常见错误 |
|------|---------|---------|----------|
| 1 | 列出所有参与测试的Pin | 根据DFT的vset/iset指令确定 | 遗漏某个Pin的继电器 |
| 2 | 逐个检查每个Pin的Connect Relay to Resource | 是否需要闭合资源继电器 | 多个Pin共用源表时漏查个别Pin |
| 3 | 检查浮动源规则 | 是否需要闭合FPVI_BUS继电器 | 非浮动源测试错误闭合FPVI_BUS继电器 |
| 4 | 检查P2P Relay | 是否需要闭合P2P继电器 | BST-SW测试漏闭合K18_BST_SW_Cap |
| 5 | 检查电容继电器 | 测量电压时闭合，测量电流时不闭合 | 测量电流时错误闭合电容继电器 |
| 6 | 检查Toggle测试上拉电阻 | Check=Toggle时必须闭合K58_INT_PU | Toggle测试漏闭合上拉电阻 |
| 7 | 检查INT引脚资源继电器 | Toggle测试必须闭合K43_SDA_INT | Toggle测试漏闭合INT资源继电器 |
| 8 | 检查继电器名称正确性 | 使用资源分配表中的准确名称 | 自定义错误的继电器名称（如K18_BST_SW_Cap_BTST） |
| 9 | 检查是否闭合了不应闭合的继电器 | AMUX/NTC的FPVI_BUS继电器绝对不能闭合 | 闭合K40_BUSH_AMUX或K41_BUSH_NTC |
| 10 | 确认cbite.SetOn格式正确 | 以-1结尾，逗号分隔 | 缺少-1或格式错误 |

**示例：TM608_BOOST_HS_ZCD继电器配置分析**

DFT配置：`vset[vbat,4.2]`, `vset[pmid,9]`, `vset[bst2sw,5]`, `iset[sw2pmid,0]`, Check=Toggle

| Pin | 继电器 | 规则来源 |
|-----|--------|---------|
| VBAT | K30_VBAT_Cap | Cap2规则 |
| PMID | K32_PMID_Cap | Cap2规则 |
| VDRV | K28_VDRV_Cap | Cap2规则 |
| PMID | K31_VBUSL_PMID | 浮动源规则（iset[sw2pmid]） |
| SW | K17_BUSH_SW | 浮动源规则（iset[sw2pmid]） |
| BST/SW | K18_BST_SW_Cap | P2P Relay规则 |
| INT | K43_SDA_INT | Connect Relay to Resource |
| INT | K58_INT_PU | Toggle测试，PULL_UP RESISTOR规则 |

正确配置：
```cpp
cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap, K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K43_SDA_INT, K58_INT_PU, -1);
```

## 6. NU浮动源规则

1. 在DFT.csv中Hardware_initial列中，如果出现iset[PinName2PinName],例如iset[pmid2sw,1,1e-3,0],就是满足浮动源规则，总线继电器连接进来闭合。主要是[]里有2，才是满足浮动源规则的。
2. 在DFT.csv中Hardware_initial列中，如果出现vset[PinName2PinName],例如vset[pmid2sw,1,1e-3,0],就是满足浮动源规则，总线继电器连接进来闭合。
3. 如果没有出现vset[PinName2PinName]，或者iset[PinName2PinName],就是不满足浮动源规则，总线继电器不能连接进来闭合。
4. 在DFT.csv中Hardware_initial列中，如果出现vset[PinName],例如vset[pmid,1,1e-3,0],就是不满足浮动源规则，总线继电器不能连接进来闭合。
5. 在DFT.csv中Hardware_initial列中，如果出现iset[PinName],例如iset[pmid,1,1e-3,0],就是不满足浮动源规则，总线继电器不能连接进来闭合。
6. 这里的值，如果是电压，则表示单位是V, 如果是电流，则表示单位是A。
7. 浮动源量程选择，参考：NU量程规则。

## 6.1 iset/vset指令完整解析规则（核心强化）

### 6.1.1 指令格式与参数含义

**iset指令格式：** `iset[PinName2PinName, 电流值, 模式, 忽略]`

**vset指令格式：** `vset[PinName, 电压值, 模式, 忽略]` 或 `vset[PinA2PinB, 电压值, 模式, 忽略]`

| 参数位置 | 含义 | 示例 | 说明 |
|---------|------|------|------|
| PinName2PinName | 浮动源表示，电流在两个Pin之间流动 | sw2pmid | 电流从SW流入，PMID流出；需用FPVI |
| PinName | 单Pin电压设置 | vbat | 使用ACM200/FOVI源表 |
| **PinA2PinB** | **浮动电压源，表示两个Pin之间的电压差** | **bst2sw, vdrv2lg** | **PinA为驱动引脚，PinB为跟随引脚；必须遵循台阶式上电/下电规则** |
| 值（第2个参数） | 电流值（A）或电压值（V） | 2, 0.9, 1, 0.5 | 根据指令类型确定单位 |
| 模式（第3个参数） | 0或1e-6=上电；1e-3=AWG | 1e-3, 1e-6, 0 | **模式是否生效取决于测试类型！** |
| 最后一个参数 | 忽略 | 0 | 始终忽略 |

**vset[PinA2PinB,...]格式的特殊规则：**

当DFT中出现`vset[PinA2PinB,电压,时间,0或1]`格式时（如bst2sw、vdrv2lg等），表示两个Pin之间的浮动电压源，必须遵循以下规则：

| 规则 | 说明 |
|------|------|
| **PinA-PinB电压关系** | PinA电压必须≥PinB电压，且电压差≤5V |
| **上电顺序** | 台阶式上电，PinA领先于或同步于PinB上升 |
| **下电顺序** | 台阶式下电，PinA先降到与PinB齐平，再继续降低 |
| **每个台阶后等待** | 每个电压变化台阶后必须等待200us |
| **详细规则参考** | 详见8.2.6节「浮动电压源台阶式上电/下电规则」 |

**常见PinA-PinB组合：**

| PinA（驱动引脚） | PinB（跟随引脚） | vset格式示例 | 电压关系 |
|----------------|-----------------|-------------|---------|
| BST | SW | vset[bst2sw,5,1e-3,0] | BST=SW+5V |
| VDRV | LG | vset[vdrv2lg,5,1e-3,0] | VDRV=LG+5V |

**关键规则：没有vset[PinA2PinB,...]配置时的处理**

当DFT中**没有**出现`vset[bst2sw,...]`或`vset[vdrv2lg,...]`等浮动电压源配置时：
- **BST电压必须等于SW电压**（或只设置BST=5V，不做升压）
- **VDRV电压必须等于LG电压**
- **禁止**单独设置BST=10V而SW≈0V，这会导致BST-SW电压差过大（>6V）损伤芯片

### 6.1.2 模式参数核心规则（避免反复犯错的关键）

**模式参数(1e-3/AWG)是否需要实现为ramp，取决于测试类型（Check列）：**

| 测试类型（Check列） | 模式参数为1e-3时的处理方式 | 代码实现 |
|-------------------|--------------------------|---------|
| **Toggle**（如ZCD检测） | **必须实现为AWG ramp**，从上一设置值扫描到当前值 | 使用`test_method.rampi_capv()` |
| **MI/MV/MV&MI**（如RDSON、静态测量） | **不做ramp**，仅作为静态FI/FV设置 | 使用`FPVI.Set(FI, 值)`或源表.Set() |
| **Trim**（如BOOST_HS_CS_GAIN） | **不做ramp**，仅作为静态FI设置 | 在measure函数中`FPVI.Set(FI, 值)` |

**判断流程：**
```
读取DFT.csv的Check列 → 判断测试类型
    ├─ 如果是Toggle → 使用rampi_capv/rampv_capv
    └─ 如果是MI/MV/MV&MI/Trim → 使用静态FI/FV设置
```

### 6.1.3 典型示例对比

**错误示例（RDSON误用AWG）：**
```cpp
// ❌ 错误！TM600_RDSON是MV&MI类型，不需要ramp
test_method.rampi_capv(FPVI, FPVIe_1V, FPVIe_10A, 
                       FPVI, FPVIe_1V, FPVIe_10A, 
                       0, 1, 200, 10, 2.5, TRIG_FALLING, 
                       hs_rdson_result);
```

**正确示例（RDSON静态FI测量）：**
```cpp
// ✅ 正确！RDSON是MV&MI类型，直接静态设置FI=1A
FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
delay_us(2000);
FPVI.MeasureVI(200, 5);
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
```

**正确示例（Toggle测试使用AWG）：**
```cpp
// ✅ 正确！TM608_ZCD是Toggle类型，使用rampi_capv
test_method.rampi_capv(FPVI, FPVIe_1V, FPVIe_10A, 
                       SDA_INT_ACM, ACM200_10V, ACM200_10UA, 
                       2, 0.9, 400, 10, 2.5, TRIG_FALLING, 
                       BOOST_HS_ZCD);
```

### 6.1.4 易错点总结

| 错误类型 | 错误描述 | 正确做法 |
|---------|---------|---------|
| RDSON误用AWG | 将RDSON测试（MV&MI类型）错误实现为rampi_capv | 静态FI测量：Set(FI,值)→delay→MeasureVI→Set(FI,0) |
| 忽略测试类型 | 只看模式参数1e-3就实现ramp，不判断Check列类型 | 先判断Check列类型，只有Toggle才用ramp |
| 模式参数误判 | 认为模式参数1e-3一定表示AWG | 模式参数只是指示配置方式，是否ramp由测试类型决定 |

## 7. NU测量规则

1. 测量之前首先需要等待1ms,采用函数delay_ms(1)
2. 首先是DFT.csv中的check，可以确定测量的对象是哪个Pin， 可以找到Pin Name，同时在Type可以找到时测量电压MV还是测量电流MI
例如：Check 列的Pin Name 是VBAT， Type 列是MI， 表示测量VBAT上的电流，测试方法是：
如果测量电流按下面执行：
 /* 资源1 */.MeasureVI(50,5);
     FOR_EACH_VALID_SITE(site)
    {
        变量[site]= /* 资源1 */.GetMeasResult(site, MIRET)
    }
如果测量电压按照下面执行：
 /* 资源1 */.MeasureVI(50,5);
     FOR_EACH_VALID_SITE(site)
    {
        变量[site]= /* 资源1 */.GetMeasResult(site, MVRET)
    }
3. 如果测试项中有trim字符，无论大小写，都认定为trim参数，测量按照：NU Trim 规则来编写。

### 7.1 NU Toggle测试规则（强制）

Toggle测试是一种特殊的测量方式，用于检测信号跳变。**以下规则必须严格遵守，否则测试将无法正常工作！**

**核心规则（强制执行）：**
1. **观测源固定为SDA_INT_ACM**：toggle信号必须由SDA_INT_ACM观测，不能使用NTC_FOVI或AMUX_FOVI
2. **必须闭合上拉电阻继电器**：在资源分配表.csv中查找INT引脚所在行的PULL_UP RESISTOR列，如果有K字开头的继电器，必须闭合
3. **必须闭合INT引脚的资源继电器**：在资源分配表.csv中查找INT引脚所在行的Connect Relay to Resource列，如果有K字开头的继电器，必须闭合 ← **最容易遗漏！**
4. **rampv_capv/rampi_capv的mon_src必须是SDA_INT_ACM**：观测toggle信号的源表必须是SDA_INT_ACM

**DFT识别规则：**
- Check列为"Toggle"或包含"toggle"关键字的测试项为Toggle测试
- 例如：`INT,"Toggle, MI"`、`INT Toggle`、`Toggle, MI`

**强制检查清单（编写代码前必须核对）：**

| 序号 | 检查项 | 必须包含 | 常见错误 |
|------|--------|---------|----------|
| 1 | 资源分配表中INT引脚的Connect Relay to Resource列是否有继电器 | ✅ 如果有，必须闭合 | ❌ 遗漏（最常见） |
| 2 | 资源分配表中INT引脚的PULL_UP RESISTOR列是否有继电器 | ✅ 如果有，必须闭合 | ❌ 遗漏 |
| 3 | ramp函数的mon_src是否为SDA_INT_ACM | ✅ 必须是 | ❌ 使用NTC_FOVI/AMUX_FOVI |
| 4 | 是否使用了正确的源表观测 | ✅ SDA_INT_ACM | ❌ 使用其他源表 |

**通用查找方法：**

在资源分配表.csv中查找INT引脚所在行：
1. **Connect Relay to Resource列**：如果有值（如K43_SDA_INT），必须闭合该继电器（引脚绑定源表的继电器）
2. **PULL_UP RESISTOR列**：如果有值（如K58_INT_PU），必须闭合该继电器（上拉电阻继电器）

**当前项目示例（NU1201）：**
| 继电器类型 | 当前项目继电器名称 | 用途 |
|-----------|------------------|------|
| Connect Relay to Resource | K43_SDA_INT | INT引脚连接到SDA_INT_ACM源表 |
| PULL_UP RESISTOR | K58_INT_PU | Toggle测试上拉电阻 |

**错误示例（必须避免）：**
```cpp
// 错误1：遗漏Connect Relay to Resource继电器（最常见错误！）
cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K58_INT_PU, -1);  // ❌ 缺少Connect Relay to Resource继电器

// 错误2：使用NTC_FOVI观测toggle信号
test_method.rampv_capv(..., NTC_FOVI, ...);  // ❌ 错误！

// 错误3：使用AMUX_FOVI观测toggle信号  
test_method.rampv_capv(..., AMUX_FOVI, ...);  // ❌ 错误！
```

**正确示例：**
```cpp
// 正确1：同时包含Connect Relay to Resource和PULL_UP RESISTOR继电器
cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K43_SDA_INT, K58_INT_PU, -1);  // ✅ 正确！

// 正确2：使用SDA_INT_ACM观测toggle信号
test_method.rampv_capv(FPVI, ..., SDA_INT_ACM, ...);  // ✅ 正确！
```

**记忆口诀：** Toggle测试，INT引脚两个类型的继电器必须都闭合 —— Connect Relay to Resource（引脚绑定源表的继电器）+ PULL_UP RESISTOR（上拉电阻继电器），一个都不能少！

### 7.2 NU 源表使用检查规则（新增）

**核心原则：只使用实际需要的源表，不要包含未使用的源表。**

检查步骤：
1. 根据DFT配置确定测试需要的Pin和源表
2. 检查上电、测量、下电部分是否包含了未使用的源表
3. 如果测试没有用到AMUX/NTC，下电部分不应该包含AMUX_FOVI/NTC_FOVI的设置
4. 如果测试没有用到SDA_INT_ACM，下电部分不应该包含SDA_INT_ACM的设置

**错误示例（必须避免）：**
```cpp
// TM608没有用到AMUX和NTC，但下电部分包含了它们
AMUX_FOVI.Set(FI, 0, ...);  // ❌ 错误！TM608没有用到AMUX
NTC_FOVI.Set(FI, 0, ...);   // ❌ 错误！TM608没有用到NTC
```

**正确示例：**
```cpp
// TM608用到的源表：VBAT_ACM, VDRV_AMP_ACM, PMID_FOVI, BTST_ACM, FPVI, SDA_INT_ACM
// 下电部分只包含这些源表
VBAT_ACM.Set(FV, 0, ...);
VDRV_AMP_ACM.Set(FV, 0, ...);
PMID_FOVI.Set(FV, 0, ...);
BTST_ACM.Set(FV, 0, ...);
SDA_INT_ACM.Set(FI, 0, ...);
FPVI.Set(FV, 0, ...);
```

## 8. NU检查规则

1. 首先检查所有继电器是否符合 NU浮动源规则，如果不符合就在cbite.Set()中移除。
2. 核对每个参与测试的Pin的Connect Relay to Resource是否与资源分配表中该Pin所在行一致。多个Pin共用同一个源表时，必须逐个核对每个Pin各自的资源继电器，不能因为共用源表就直接复制其他Pin的继电器配置。例如VAC1、VAC2、VAC3共用VAC123_ACM，但Connect Relay to Resource各不相同，需逐个检查。
3. 核对每个测量对象（Check列的Pin）的电容继电器（Cap2 Relay）是否正确：如果测量类型是电流（MI），则该Pin的电容继电器不能闭合（需从cbite.SetOn中移除）；只有测量电压（MV）时才闭合电容继电器。例如TM103测量LP_HR_0P5U的电流（MI），则LP_HR_0P5U对应的电容继电器不应闭合。
4. 核对I2CWriteSameData行后面的注释是否完整保留：Software_initial中//后面的注释内容必须原样出现在生成的代码中，不能遗漏或删除。
5. 核对电流量程是否正确：
   - 测量电压且FI=0时，电流量程必须选最小档位（10UA），不能用默认的100MA。
   - 对于有设定电流值的情况，量程必须大于等于设定值的2倍。例如FI=0.03A=30mA，2倍=60mA，应该选100MA档而不是10MA档（10MA=10mA<60mA不够）。
6. 核对测量模式是否正确：
   - FV（Force Voltage）：强制输出电压，用于测量电流
   - FI（Force Current）：强制输出电流，用于测量电压
   - 测量电压时必须使用FI模式（FI=0），不能使用FV模式

## 8.1 NU AMUX-NTC测量规则

AMUX-NTC表示AMUX和NTC两个引脚之间的差分测量：
1. **测量含义**：测量结果 = AMUX测量值 - NTC测量值
2. **继电器配置**：必须闭合K40_BUSH_AMUX和K41_BUSH_NTC两个继电器
3. **源表设置**：
   - AMUX_FOVI和NTC_FOVI都设置为FI模式（Force Current=0），用于测量电压
   - 电流量程选最小档位（FOVIe_10UA），因为FI=0只是补偿电流
   - 电压量程根据测量范围选择（通常FOVIe_10V）
4. **测量代码**：
   ```cpp
   AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
   NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
   // ... 寄存器配置 ...
   AMUX_FOVI.MeasureVI(200, 5);
   NTC_FOVI.MeasureVI(200, 5);
   FOR_EACH_VALID_SITE(site)
   {
       results[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
   }
   ```
5. **下电处理**：测量完成后必须对AMUX_FOVI和NTC_FOVI进行下电操作，RELAY_OFF状态时量程统一为10V/10MA

## 8.2 NU 大电流测试规则（新增）

### 8.2.1 大电流定义
- 电流值 ≥ 1A 定义为大电流
- 超过200mA的电流必须使用FPVI（ACM200最大只有200MA）

### 8.2.2 iset指令含义
- `iset[pmid2sw,3,1e-3,0]`：电流从PMID流入芯片，从SW流出芯片，FPVI连接PMID和SW
- `iset[pgnd2sw,3,1e-3,0]`：电流从PGND流入芯片，从SW流出芯片，FPVI连接PGND和SW
- 格式：`iset[流入引脚2流出引脚,电流值,稳定时间,忽略]`

### 8.2.3 FPVI_BUS继电器连接规则

**核心概念：FPVI_BUS是一个公共总线，闭合多个继电器会导致对应的引脚短接在一起！**

资源分配表中有两种继电器列，含义完全不同：

| 列名 | 含义 | 用途 |
|------|------|------|
| **Connect Relay to Resource** | Pin连接到自己源表的继电器 | 当值为Default时，不需要闭合额外继电器 |
| **Relay to FPVI_BUS** | Pin连接到FPVI_BUS的继电器 | **只有iset指令涉及的引脚才需要闭合** |

所有Pin连接FPVI都是通过**FPVI_BUS**继电器实现的，必须从资源分配表的**Relay to FPVI_BUS**列查找对应继电器：

| Pin | Relay to FPVI_BUS | 说明 |
|-----|-------------------|------|
| PMID | K31_VBUSL_PMID | PMID连接到FPVI_BUS |
| SW | K17_BUSH_SW | SW连接到FPVI_BUS |
| PGND | K33_BUSL_PGND | PGND连接到FPVI_BUS |
| VBAT | K29_BUSL_VBAT | VBAT连接到FPVI_BUS |
| AMUX | K40_BUSH_AMUX | AMUX连接到FPVI_BUS（**绝对不能闭合**） |
| NTC | K41_BUSH_NTC | NTC连接到FPVI_BUS（**绝对不能闭合**） |

**短路风险示例：**

错误配置（同时闭合K17和K40）：
```
FPVI High端 ──→ FPVI_BUS ──→ K31_VBUSL_PMID ──→ PMID
                       └──→ K40_BUSH_AMUX ──→ AMUX  ←── SW ──→ K17_BUSH_SW ──→ FPVI_BUS
```
→ SW和AMUX通过FPVI_BUS短接，电流无法正确通过DUT

正确配置（只闭合iset涉及的引脚）：
```
FPVI High端 ──→ FPVI_BUS ──→ K31_VBUSL_PMID ──→ PMID ──→ DUT ──→ SW ──→ K17_BUSH_SW ──→ FPVI_BUS ──→ FPVI Low端
```
→ 电流正确从PMID流入、SW流出

**关键注意事项：**
- AMUX和NTC使用各自的FOVI源表（AMUX_FOVI/NTC_FOVI）测量电压，Connect Relay to Resource=Default，**不需要闭合任何继电器**
- K40_BUSH_AMUX和K41_BUSH_NTC是连接到FPVI_BUS的继电器，不是连接到FOVI的继电器
- **只有iset指令涉及的引脚才需要闭合对应的FPVI_BUS继电器**
- 闭合多个FPVI_BUS继电器会导致对应引脚短路，**必须严格控制**
- 电流流入端和流出端的FPVI_BUS继电器都需要闭合

### 8.2.4 FPVI电压量程选择
大电流测试时，FPVI两端的电压降很小，因此**电压量程选1V档位**即可，不需要用10V档位。
- 示例：`FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);`

### 8.2.5 大电流测试流程（Trim函数）

由于trim的measure函数会被execute反复调用，因此大电流初始化和关闭应在test.cpp中完成，measure函数只负责改变电流值。

**test.cpp流程：**
```cpp
// execute之前 - 初始化FPVI（只执行一次）
FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10A, FPVI_RELAY_ON);   // 1. FV=0
FPVI.Set(FI, 0, FPVIe_10V, FPVIe_10A, FPVI_RELAY_ON);   // 2. FI=0
FPVI.SetClamp(25, 25);                                  // 3. 设置clamp（FI模式后设置才有效）

// execute - 调用measure函数（可能重复调用）
TRIM_NODE.execute(measure_func, ...);

// execute之后 - 关闭FPVI（只执行一次）
FPVI.Set(FI, 0, FPVIe_10V, FPVIe_10A, FPVI_RELAY_ON);   // 1. FI=0
FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10A, FPVI_RELAY_ON);   // 2. FV=0
FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10A, FPVI_RELAY_OFF);  // 3. OFF
```

**measure函数流程：**
```cpp
// 1. 修改寄存器值（I2C写入）
dcm.I2CWriteData(DEV_ADDR, reg_addr, 1, working_value);

// 2. 加载大电流（同时改变）
FPVI.Set(FI, 电流值, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);

// 3. 统一等待2ms（寄存器生效 + 电流稳定）
delay_us(2000);

// 4. 测量
// ... 测量代码 ...

// 5. 测量后立刻设置0电流
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
```

### 8.2.6 浮动电压源台阶式上电/下电规则（vset[A2B,...]模式）

当DFT中出现 `vset[A2B,电压,时间,0或1]` 格式时（A2B表示两个Pin之间的浮动电压源，如bst2sw、vdrv2lg等），需要遵循台阶式上电和下电规则：

**通用概念定义：**
- **PinA（驱动引脚）**：提供电压的引脚（如BST、VDRV），电压值较大
- **PinB（跟随引脚）**：被驱动的引脚（如SW、LG），电压值较小或跟随其他电压
- **电压关系**：PinA电压必须 ≥ PinB电压，**正常工作电压差≈5V，最大不超过6V**
- **台阶压差规则**：上电和下电的每个台阶，PinA与PinB的电压变化差值必须≤5V，避免过充产生spike

**上电顺序（台阶式上电，每个台阶压差≤5V）：**
```cpp
// 步骤1：先设置PinB基准电压，PinA初始电压与PinB相同，FPVI=FV=0（使PinB跟随）
PinB_SOURCE.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
PinA_SOURCE.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // PinB跟随基准电压，PinA-PinB=0V ✓
delay_us(200);

// 步骤2：PinA升至最终值（PinA=PinB+目标压差）
// 例如目标压差=5V，则PinA=5+5=10V，PinA-PinB=5V ✓
PinA_SOURCE.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
```

**核心原则：**
1. 始终先连接FPVI（FV=0），使PinB跟随基准电压
2. PinA上升必须领先于或同步于PinB上升，确保PinA≥PinB
3. **每个台阶的电压变化差值≤5V**，避免电压过冲（spike）
4. 如果PinB目标值>5V，需分步上升：PinA先升→PinB再升→PinA再升
5. 每个台阶步骤后必须等待200us，确保电压稳定
6. FPVI OFF时，电压量程=1V，电流量程=10MA

**下电顺序（PinA电压不能低于PinB，需逐步降低，且FPVI保持FV=0使PinB跟随）：**
```cpp
// 上电后：PinA=10V, PinB基准=9V, PinB≈9V (FPVI的FV=0使PinB跟随)

// 步骤1：PinA从10V降到9V（PinB基准=9V，PinB=9V，PinA-PinB=0V ✓）
PinA_SOURCE.Set(FV, 9, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);

// 步骤2：PinB基准从9V降到5V（PinB跟随变为5V，PinA=9V，PinA-PinB=4V ✓）
PinB_SOURCE.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_us(200);

// 步骤3：PinA从9V降到5V（PinB=5V，PinA-PinB=0V ✓）
PinA_SOURCE.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);

// 步骤4：PinB基准从5V降到0V（PinB跟随变为0V，PinA=5V，PinA-PinB=5V ✓）
PinB_SOURCE.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_us(200);

// 步骤5：其他电源降到0V
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);

// 步骤6：PinA最后降到0V（PinB=0V，PinA-PinB=0V ✓）
PinA_SOURCE.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

// 步骤7：断开所有继电器（OFF状态统一10V/10MA）
// FPVI OFF时必须使用：FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);
PinA_SOURCE.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
PinB_SOURCE.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
// ... 其他电源 ...

// 步骤8：最后断开FPVI继电器
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_OFF);
```

**关键逻辑：**
1. 大电流加载时，FPVI连接PinB和基准引脚，优先满足电流要求
2. FPVI在FV=0模式下，PinB和基准引脚没有电压差，因此PinB≈基准电压
3. PinA需要比PinB高5V
4. 不需要单独设置PinB电压，通过FPVI=0V自动让PinB跟随基准电压
5. **下电时PinA必须逐步降低**，始终保持PinA≥PinB，电压差≤5V

**常见PinA-PinB组合示例：**

| PinA（驱动引脚） | PinB（跟随引脚） | vset格式示例 | 电压关系 |
|----------------|-----------------|-------------|---------|
| BST | SW | vset[bst2sw,5,1e-3,0] | BST=SW+5V |
| VDRV | LG | vset[vdrv2lg,5,1e-3,0] | VDRV=LG+5V |
| 其他驱动引脚 | 其他跟随引脚 | vset[x2y,5,1e-3,0] | x=y+5V |

### 8.2.7 关键注意事项
1. **量程选择**：FPVI电流量程必须大于等于电流值的2倍（如3A电流→2×3=6A→选FPVIe_10A；1A电流→2×1=2A→选FPVIe_2A）。详见第14节NU量程规则。
2. **clamp设置**：clamp值必须在FI模式切换后设置，模式切换后clamp会失效
3. **时间要求**：加载大电流后必须等待稳定时间（1ms~5ms，推荐2ms），然后再测量；测量和施加电流之间最多不超过5ms
4. **快速关断**：测量完成后必须立刻设置FI=0，避免大电流持续通过DUT
5. **资源保护**：大电流测试有风险，必须严格按照流程操作
6. **浮动电压源下电规则**：当DFT中存在`vset[A2B,...]`格式时（如bst2sw、vdrv2lg），PinA必须先降到与PinB齐平，再下电其他电源，最后PinA才降到0V，始终保持PinA≥PinB且PinA-PinB≤5V

#### 大电流测试检查清单（必须严格遵守，避免重复出错）

| 序号 | 检查项 | 要求 | 常见错误 |
|------|--------|------|----------|
| 1 | 大电流定义 | 电流≥1A必须使用FPVI | 使用ACM200（最大200MA） |
| 2 | 量程选择 | 量程≥电流值的2倍 | FI=1A用FPVIe_10A（应为FPVIe_2A） |
| 3 | 初始化顺序 | FV=0 → FI=0 → SetClamp | 直接加载大电流，跳过初始化 |
| 4 | clamp时机 | FI模式切换后设置clamp | 在FV模式下设置clamp（无效） |
| 5 | 稳定时间 | 加载大电流后等待1ms~5ms | delay_us(100)（太短） |
| 6 | 测量后关断 | MeasureVI后立即FI=0 | 读取数据后再FI=0（大电流持续时间过长） |
| 7 | 数据读取时机 | FI=0之后读取数据 | MeasureVI之后直接读取，FI=0在读取之后 |
| 8 | 浮动电压源上电（vset[A2B,...]） | 台阶式上电，PinA领先PinB上升 | 直接设置PinA=14V，PinB还没跟随 |
| 9 | 浮动电压源下电（vset[A2B,...]） | 台阶式下电，PinA先降到与PinB齐平 | PinA直接降到0V，导致PinA<PinB |
| 10 | PinA-PinB电压差 | 始终≤5V且≥0V | PinA与PinB电压差超过5V |
| 11 | 台阶等待时间 | 每个台阶步骤后等待200us | 无等待或等待时间不足 |
| 12 | test.cpp中CSpec | **不允许出现**CSpec代码 | 在test.cpp中添加CSpec.SetPara |

**大电流测试标准代码模板（test.cpp中）：**
```cpp
// ========== 大电流初始化（execute之前）==========
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);      // 步骤1：FV=0
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);      // 步骤2：FI=0
FPVI.SetClamp(25, 25);                                   // 步骤3：SetClamp（FI模式后设置才有效）

// ========== 大电流测量流程 ==========
FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);      // 步骤4：加载大电流（量程≥2×电流值）
delay_us(2000);                                          // 步骤5：等待稳定（1ms~5ms，推荐2ms）
FPVI.MeasureVI(200, 5);                                  // 步骤6：测量
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);      // 步骤7：立即关断电流（必须在读取数据之前）
FOR_EACH_VALID_SITE(site)                                // 步骤8：读取测量结果
{
    xxx->SetMeasResult(site, FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET) * 1000); // V/A = Ω → ×1000 = mΩ
}
```

**大电流测量函数模板（sub.cpp中measure函数）：**
```cpp
// FPVI已在test.cpp中初始化（FV=0 → FI=0 → SetClamp）
FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);     // 加载大电流（量程≥2×电流值）
delay_us(2000);                                          // 等待稳定（1ms~5ms，推荐2ms）
AMUX_FOVI.MeasureVI(200, 5);                             // 测量
NTC_FOVI.MeasureVI(200, 5);
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);     // 立即关断电流（必须在读取数据之前）
FOR_EACH_VALID_SITE(site)                                // 读取测量结果
{
    amux_results[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
    ntc_results[site] = NTC_FOVI.GetMeasResult(site, MVRET);
    results[site] = amux_results[site] - ntc_results[site];
}
```

### 8.2.8 大电流测试易错点总结（避免反复犯错）

| 错误类型 | 错误描述 | 正确做法 |
|---------|---------|---------|
| RDSON误用AWG | 将RDSON测试（MV&MI类型）错误实现为rampi_capv | 静态FI测量：Set(FI,值)→delay→MeasureVI→Set(FI,0) |
| 量程选择过大 | FI=0.5A选FPVIe_2A，FI=1A选FPVIe_10A | 参考14.1节决策表：0.5A选1A，1A选2A |
| PinA电压量程错误（vset[A2B,...]） | PinA=10V时使用ACM200_10V量程 | 2×10=20V，需选ACM200_40V量程 |
| 初始化顺序错误 | 直接加载大电流，跳过FV=0→FI=0→SetClamp | 严格按照FV=0→FI=0→SetClamp→加载电流的顺序 |
| clamp时机错误 | 在FV模式下设置clamp | 必须在FI模式切换后设置clamp |
| 稳定时间不足 | delay_us(100)或无等待 | 加载大电流后必须等待2ms（delay_us(2000)） |
| 电流关断时机错误 | 读取数据后再FI=0 | MeasureVI后立即FI=0，然后读取数据 |
| 浮动电压源上电顺序错误（vset[A2B,...]） | 直接设置PinA=10V，PinB还没跟随 | 台阶式上电，每个台阶后等待200us |
| 浮动电压源下电顺序错误（vset[A2B,...]） | PinA直接降到0V，导致PinA<PinB | 台阶式下电，始终保持PinA≥PinB |
| 继电器配置错误 | 闭合了AMUX/NTC的FPVI_BUS继电器 | 只闭合iset涉及的引脚的FPVI_BUS继电器 |
| test.cpp中使用CSpec | 在test.cpp中添加CSpec.SetPara | CSpec代码只能出现在sub.cpp的measure函数中 |

## 9. NU上电规则

举例：vset[vbat,4.2,100e-6,0]
vset表示设置电压模式，对应实例中FV（Force Voltage，强制输出电压）：
 源表1 .Set(FV, 电压值, 电压量程 , 电流量程 , ACM200_RELAY_ON);
 源表1 .Set(FV, 电压值 , 电压量程 , 电流量程, FOVIe_RELAY_ON);

vbat 是 Pin Name，4.2是设置电压为4.2V，100e-6是上电时间，如果是100e-6表示正常上电模式，如果是1e-3表示AWG上电模式， 0忽略。
这里的Pin Name后续会用于资源分配表的映射。需要通道Pin Name找到Resource Name（源表名称）以及相关的继电器。
资源映射表中Type列是资源类型，比如：ACM200，FOVIe等。
这里电压值、电流值不可以超过量程，最好是量程的一半，以免出现测量不准，具体参考NU量程规则。
 ACM200电压量程:ACM200_10V,ACM200_10V,ACM200_40V
 FOVIe电压量程:FOVIe_10V,FOVIe_40V
 ACM200电流量程:ACM200_1MA,ACM200_10MA,ACM200_100MA
 FOVIe电流量程:FOVIe_1MA,FOVIe_10MA,FOVIe_100MA
如果power on需要有多个pin 参与，那么每个pin都需要独立上电。
如果测量所在Pin并没有上电的信息，就按照：如果测量电流，就设置测量pin电压是0V（FV模式）， 如果测试的是电压，就设置测量pin上电0mA（FI模式）。
测量电压时，如果DFT中没有给测量pin的上电条件（FI=0），电流量程默认选择最小档位（最接近10UA的档位，如FOVIe_10UA或ACM200_10UA），而不是默认的100MA。因为FI=0时只是作为电压测量的补偿电流，不需要大量程，用小量程可以提高精度。

**FV与FI模式区分规则：**
- **FV（Force Voltage）**：强制输出电压，源表主动输出设定的电压值，用于测量电流（MI）
- **FI（Force Current）**：强制输出电流，源表主动输出设定的电流值，用于测量电压（MV）
- 上电时（vset）：使用FV模式，给DUT提供电源
- 测量电压时（MV）：使用FI模式（FI=0），源表不输出电流，只测量电压
- 测量电流时（MI）：使用FV模式（FV=0或设定电压），源表输出电压，测量电流

## 10. NU下电规则

执行完成下列所有动作后，DUT 进入安全关断状态，可以进行下一次测试。

### 10.1 下电流程
举例：vset[vbat,4.2,100e-6,0]
vset表示设置电压模式，对应实例中FV：
 /* 资源1 */.Set(FV, 0, /* 电压量程 */, /* 电流量程 */, ACM200_RELAY_ON);
 /* 资源1 */.Set(FV, 0, /* 电压量程 */, /* 电流量程 */, FOVIe_RELAY_ON);
delay_ms(1);
 /* 资源1 */.Set(FV, 0, /* 电压量程 */, /* 电流量程 */, ACM200_RELAY_OFF);
 /* 资源1 */.Set(FV, 0, /* 电压量程 */, /* 电流量程 */, FOVIe_RELAY_OFF);

### 10.2 下电量程统一规则（新增）
- **RELAY_ON状态**：保持上电时的量程设置
- **RELAY_OFF状态**：电压量程统一改为10V，电流量程统一改为10MA
  - ACM200：`ACM200_10V`，`ACM200_10MA`
  - FOVIe：`FOVIe_10V`，`FOVIe_10MA`

## 11. NU补充上电规则

补充上电规则有10类，这里先列举其中两类：
第一类：举例，
"vset[vbus,3.5,100e-6,1]
vset[vbus,4.5,1e-3,1]
vset[vbus,4.3,100e-6,1]
vset[vbus,3.3,1e-3,1]"
vset表示设置电压模式，对应实例中FV：
 源表1 .Set(FV, 电压值, 电压量程 , 电流量程 , ACM200_RELAY_ON);
 源表1 .Set(FV, 电压值 , 电压量程 , 电流量程, FOVIe_RELAY_ON);
vbat 是 Pin Name，4.2是设置电压为4.2V，100e-6是上电时间，如果是100e-6表示正常上电模式，如果是1e-3表示AWG上电模式， 0忽略。
这里的Pin Name后续会用于资源分配表的映射。需要通道Pin Name找到Resource Name（源表名称）以及相关的继电器。
对于AWG参考4级规则： NU-AWG规则。

## 12. NU-AWG规则

采用 `test_method.rampv_capv()` 库函数，一行代码完成ramp+measure+trigger全部操作，代码更简洁。

**函数原型：**
```cpp
test_method.rampv_capv(ramp_src, ramp_v_range, ramp_i_range, mon_src, mon_v_range, mon_i_range, start_volt, end_volt, sample_num, interval_us, trig_volt, trig_edge, result_var);
```

**参数说明（共13个参数）：**

| 序号 | 参数 | 含义 | 示例 |
|------|------|------|------|
| 1 | ramp_src | RAMP源（输出电压斜坡的源表） | VAC123_VBATD_ACM |
| 2 | ramp_v_range | RAMP源电压量程 | ACM200_10V |
| 3 | ramp_i_range | RAMP源电流量程 | ACM200_100MA |
| 4 | mon_src | Monitor源（观测trigger信号的源表） | NTC2_FOVI |
| 5 | mon_v_range | Monitor源电压量程 | FOVIe_10V |
| 6 | mon_i_range | Monitor源电流量程 | FOVIe_100UA |
| 7 | start_volt | Ramp起始电压（V） | 4.35 |
| 8 | end_volt | Ramp结束电压（V） | 4.85 |
| 9 | sample_num | 采样点数 | 400 |
| 10 | interval_us | 采样间隔（us） | 10 |
| 11 | trig_volt | Trigger判断阈值电压（V） | 2.5 |
| 12 | trig_edge | Trigger触发沿 | TRIG_RISING / TRIG_FALLING |
| 13 | result_var | 测量结果保存变量名 | vbat_low_2cell_2p3_rise |

**使用示例：**

```cpp
// rise部分：电压从4.35V上升到4.85V，抓上升沿
test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, 
                       NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 
                       4.35, 4.85, 400, 10, 2.5, TRIG_RISING, 
                       vbat_low_2cell_2p3_rise); 

// fall部分：电压从4.65V下降到3.15V，抓下降沿
test_method.rampv_capv(VAC123_VBATD_ACM, ACM200_10V, ACM200_100MA, 
                       NTC2_FOVI, FOVIe_10V, FOVIe_100UA, 
                       4.65, 3.15, 400, 10, 2.5, TRIG_FALLING, 
                       vbat_low_2cell_2p3_fall);
```

**注意事项：**
- 变量定义：只需定义 `result_var` 相关变量（如 `xxx_rise`, `xxx_fall`, `xxx_hys`），无需额外定义 `sam`, `interval`, `Trig`, `Trig_Point` 等变量
- 迟滞计算：`hys = (rise - fall) * 1e3`

**电流Ramp函数 - test_method.rampi_capv()：**

用于电流斜坡测试，如ZCD（零电流检测）测试，电流从高值降到低值，观测toggle信号触发。

**函数原型：**
```cpp
test_method.rampi_capv(ramp_src, ramp_v_range, ramp_i_range, mon_src, mon_v_range, mon_i_range, start_curr, end_curr, sample_num, interval_us, trig_volt, trig_edge, result_var);
```

**参数说明（共13个参数，与rampv_capv相同，仅start_curr/end_curr为电流值）：**

| 序号 | 参数 | 含义 | 示例 |
|------|------|------|------|
| 1 | ramp_src | RAMP源（输出电流斜坡的源表） | FPVI |
| 2 | ramp_v_range | RAMP源电压量程 | FPVIe_1V |
| 3 | ramp_i_range | RAMP源电流量程 | FPVIe_10A |
| 4 | mon_src | Monitor源（观测trigger信号的源表） | NTC_FOVI |
| 5 | mon_v_range | Monitor源电压量程 | FOVIe_10V |
| 6 | mon_i_range | Monitor源电流量程 | FOVIe_10UA |
| 7 | start_curr | Ramp起始电流（A） | 2 |
| 8 | end_curr | Ramp结束电流（A） | 0.9 |
| 9 | sample_num | 采样点数 | 400 |
| 10 | interval_us | 采样间隔（us） | 10 |
| 11 | trig_volt | Trigger判断阈值电压（V） | 2.5 |
| 12 | trig_edge | Trigger触发沿 | TRIG_RISING / TRIG_FALLING |
| 13 | result_var | 测量结果保存变量名 | BOOST_HS_ZCD |

**使用示例（ZCD测试）：**
```cpp
// ZCD测试：电流从2A降到0.9A，观测toggle信号下降沿触发
// 注意：toggle信号观测源必须是SDA_INT_ACM，不是NTC_FOVI
test_method.rampi_capv(FPVI, FPVIe_1V, FPVIe_10A, 
                       SDA_INT_ACM, ACM200_10V, ACM200_10UA, 
                       2, 0.9, 400, 10, 2.5, TRIG_FALLING, 
                       BOOST_HS_ZCD);
```

## 13. NU函数框架

### 13.1 测试函数参数定义规则（强制执行）

**核心规则：所有测试函数的参数定义必须放在 `//{{AFX_STS_PARAM_PROTOTYPES` 和 `//}}AFX_STS_PARAM_PROTOTYPES` 之间！**

这是STS测试框架的强制性要求，缺少这对注释会导致框架无法识别测试参数，进而引发编译或运行时错误。

**标准格式：**
```cpp
DUT_API int TMxxx_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES    ← 必须有！
    CParam *Param1 = StsGetParam(funcindex, "Param1");
    CParam *Param2 = StsGetParam(funcindex, "Param2");
    // ... 所有参数定义都必须放在这里 ...
    //}}AFX_STS_PARAM_PROTOTYPES    ← 必须有！

    double param1[SITE_NUM] = { 0 };
    double param2[SITE_NUM] = { 0 };
    // ... 参数测试流程 ...
}
```

**详细说明：**
1. **注释必须成对出现**：`//{{AFX_STS_PARAM_PROTOTYPES` 和 `//}}AFX_STS_PARAM_PROTOTYPES` 必须同时存在，缺一不可
2. **所有参数定义必须放在中间**：无论有多少个参数（1个或多个），所有 `CParam *xxx = StsGetParam(funcindex, "xxx");` 语句都必须放在这对注释之间
3. **Trim测试函数同样适用**：Trim测试函数的step0~stepN、pre_value、post_rt等所有参数也必须放在这对注释之间
4. **参数数组定义在注释外**：`double param1[SITE_NUM] = { 0 };` 等数组定义必须放在注释对之后

**错误示例（必须避免）：**
```cpp
// ❌ 错误！缺少AFX_STS_PARAM_PROTOTYPES注释
DUT_API int TM600_RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");  // ← 错误位置！
    // ...
}

// ❌ 错误！只写了开头注释，缺少结尾注释
DUT_API int TMxxx_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Param1 = StsGetParam(funcindex, "Param1");
    // ... 缺少 //}}AFX_STS_PARAM_PROTOTYPES！
}
```

**正确示例：**
```cpp
// ✅ 正确！
DUT_API int TM000_IQ_TEST(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *IQ_Standby1_DSM = StsGetParam(funcindex, "IQ_Standby1_DSM");
    CParam *IQ_Standby2_DSM = StsGetParam(funcindex, "IQ_Standby2_DSM");
    //}}AFX_STS_PARAM_PROTOTYPES

    double iq_standby1_dsm[SITE_NUM] = { 0 };
    double iq_standby2_dsm[SITE_NUM] = { 0 };
    // ...
}
```

### 13.2 函数框架结构

DFT.csv中，从第二行开始，B列是测试项名字，C列是参数名字，补全测试项内容时候需要：

**参数数组命名规则：** `double param1[SITE_NUM] = { 0 };` 中param1是Param1的小写。

**多参数处理：** 如果不止一个参数，需要将所有参数都按照上述方式生成。

**结果输出格式：**
```cpp
FOR_EACH_VALID_SITE(site)
{
    Param1->SetTestResult(site, 0, param1[site]);
    Param2->SetTestResult(site, 0, param2[site]);
}
```

下面时打印参数测量结果的过程，需要打印所有参数的测量结果，参考下面案例：
    FOR_EACH_VALID_SITE(site)
    {
        Param1->SetTestResult(site, 0, param1[site]);
    }

    return 0;
}

## 14. NU量程规则

**核心原则：量程必须大于等于设定值的2倍（即"最接近设定值两倍"的量程档位）**

1. ACM200 电压量程有：ACM200_40V,ACM200_10V,ACM200_3p6V，电流量程有：ACM200_200MA ，ACM200_100MA,ACM200_10MA,ACM200_1MA,ACM200_100UA,ACM200_10UA,ACM200_1UA。
2. FOVI 电压量程有：FOVIe_40V,FOVIe_20V,FOVIe_10V,FOVIe_5V,FOVIe_2V,FOVIe_1V，电流量程有：FOVIe_1A,FOVIe_100MA,FOVIe_10MA,FOVIe_1MA,FOVIe_100UA,FOVIe_10UA。
3. FPVI 电压量程有：FPVIe_100V,FPVIe_40V,FPVIe_20V,FPVIe_10V,FPVIe_5V,FPVIe_2V,FPVIe_1V,FPVIe_100MV，电流量程有：FPVIe_10A,FPVIe_2A,FPVIe_1A,FPVIe_100MA,FPVIe_10MA,FPVIe_1MA,FPVIe_100UA,FPVIe_10UA。
4. **FV模式（Force Voltage）**：
   - 电压量程：选择大于等于设定电压值2倍的最小量程档位
   - 电流量程：默认100MA（除非源表本身需要测量电流，此时电流量程选择大于等于被测量电流值2倍的最小档位）
5. **FI模式（Force Current）**：
   - 电流量程：选择大于等于设定电流值2倍的最小量程档位
   - 电压量程：默认最小档位（除非源表本身需要测量电压，此时电压量程选择大于等于被测量电压值2倍的最小档位）
6. **量程选择示例**：
   - FI=1A → 2倍=2A → 选择大于等于2A的最小档位 → **FPVIe_2A**（不是10A）
   - FI=3A → 2倍=6A → 选择大于等于6A的最小档位 → **FPVIe_10A**（最接近6A）
   - FI=0.03A=30mA → 2倍=60mA → 选择大于等于60mA的最小档位 → **100MA**
   - FI=1mA → 2倍=2mA → 选择大于等于2mA的最小档位 → **10MA**
   - FV=5V → 2倍=10V → 选择大于等于10V的最小档位 → **ACM200_10V**或**FOVIe_10V**
   - FV=9V → 2倍=18V → 选择大于等于18V的最小档位 → **FOVIe_20V**或**ACM200_40V**
7. **特别注意**：
   - 大电流（≥1A）必须使用FPVI，ACM200/FOVI最大只能到1A
   - FI=0恢复电流时，量程应与之前force电流时保持一致
   - 量程选择错误会导致测量不准确或源表保护触发

### 14.2 电阻单位选择规则（RDSON等电阻测量）

**核心规则：根据测量电流大小决定电阻输出单位**

| 测量电流 | 输出单位 | 计算公式（V/A = Ω） |
|---------|---------|-------------------|
| **> 100mA** | **mΩ（毫欧姆）** | `GetMeasResult(site, MVRET) / GetMeasResult(site, MIRET) * 1000` |
| **≤ 100mA** | **Ω（欧姆）** | `GetMeasResult(site, MVRET) / GetMeasResult(site, MIRET) * 1` |

**代码示例：**
```cpp
FOR_EACH_VALID_SITE(site)
{
    double current = FPVI.GetMeasResult(site, MIRET);  // 单位：A
    double voltage = FPVI.GetMeasResult(site, MVRET);  // 单位：V
    
    if (current > 0.1)  // 电流 > 100mA
    {
        xxx->SetMeasResult(site, voltage / current * 1000);  // 输出 mΩ
    }
    else
    {
        xxx->SetMeasResult(site, voltage / current);         // 输出 Ω
    }
}
```

**说明：**
- 程序中所有源表（FPVI、ACM200、FOVI）返回的电压单位都是 **V（伏特）**，电流单位都是 **A（安培）**
- RDSON测试通常使用大电流（如1A），所以输出mΩ
- 小电流测量电阻（如Trim测试中的CS_GAIN）通常使用10μA~100μA，所以输出Ω

## 15. NU Trim 规则

### 15.1 Trim参数定义规则

Trim参数的参数定义与非Trim参数不同，需要根据treg文件中该参数的Table元素数量来确定step数量：

**位数计算**：Table元素数量 = 2^n，其中n为位数
- Table有8个元素 → 3位 → step0~step7
- Table有16个元素 → 4位 → step0~step15
- Table有32个元素 → 5位 → step0~step31
- Table有64个元素 → 6位 → step0~step63

**参数定义格式**：

```cpp
//{{AFX_STS_PARAM_PROTOTYPES
CParam *PARAM_NAME_step0 = StsGetParam(funcindex, "PARAM_NAME_step0");
CParam *PARAM_NAME_step1 = StsGetParam(funcindex, "PARAM_NAME_step1");
...
CParam *PARAM_NAME_stepN = StsGetParam(funcindex, "PARAM_NAME_stepN");
CParam *PARAM_NAME_pre_value = StsGetParam(funcindex, "PARAM_NAME_pre_value");
CParam *PARAM_NAME_pre_bit = StsGetParam(funcindex, "PARAM_NAME_pre_bit");
CParam *PARAM_NAME_post_bit = StsGetParam(funcindex, "PARAM_NAME_post_bit");
CParam *PARAM_NAME_updated = StsGetParam(funcindex, "PARAM_NAME_updated");
CParam *PARAM_NAME_guessed = StsGetParam(funcindex, "PARAM_NAME_guessed");
CParam *PARAM_NAME_target = StsGetParam(funcindex, "PARAM_NAME_target");
CParam *PARAM_NAME_post_value = StsGetParam(funcindex, "PARAM_NAME_post_value");
CParam *PARAM_NAME_post_rt = StsGetParam(funcindex, "PARAM_NAME_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
```

**示例**（假设PARAM_NAME有4位，16个step）：

```cpp
//{{AFX_STS_PARAM_PROTOTYPES
CParam *PARAM_NAME_step0 = StsGetParam(funcindex, "PARAM_NAME_step0");
CParam *PARAM_NAME_step1 = StsGetParam(funcindex, "PARAM_NAME_step1");
CParam *PARAM_NAME_step2 = StsGetParam(funcindex, "PARAM_NAME_step2");
CParam *PARAM_NAME_step3 = StsGetParam(funcindex, "PARAM_NAME_step3");
CParam *PARAM_NAME_step4 = StsGetParam(funcindex, "PARAM_NAME_step4");
CParam *PARAM_NAME_step5 = StsGetParam(funcindex, "PARAM_NAME_step5");
CParam *PARAM_NAME_step6 = StsGetParam(funcindex, "PARAM_NAME_step6");
CParam *PARAM_NAME_step7 = StsGetParam(funcindex, "PARAM_NAME_step7");
CParam *PARAM_NAME_step8 = StsGetParam(funcindex, "PARAM_NAME_step8");
CParam *PARAM_NAME_step9 = StsGetParam(funcindex, "PARAM_NAME_step9");
CParam *PARAM_NAME_step10 = StsGetParam(funcindex, "PARAM_NAME_step10");
CParam *PARAM_NAME_step11 = StsGetParam(funcindex, "PARAM_NAME_step11");
CParam *PARAM_NAME_step12 = StsGetParam(funcindex, "PARAM_NAME_step12");
CParam *PARAM_NAME_step13 = StsGetParam(funcindex, "PARAM_NAME_step13");
CParam *PARAM_NAME_step14 = StsGetParam(funcindex, "PARAM_NAME_step14");
CParam *PARAM_NAME_step15 = StsGetParam(funcindex, "PARAM_NAME_step15");
CParam *PARAM_NAME_pre_value = StsGetParam(funcindex, "PARAM_NAME_pre_value");
CParam *PARAM_NAME_pre_bit = StsGetParam(funcindex, "PARAM_NAME_pre_bit");
CParam *PARAM_NAME_post_bit = StsGetParam(funcindex, "PARAM_NAME_post_bit");
CParam *PARAM_NAME_updated = StsGetParam(funcindex, "PARAM_NAME_updated");
CParam *PARAM_NAME_guessed = StsGetParam(funcindex, "PARAM_NAME_guessed");
CParam *PARAM_NAME_target = StsGetParam(funcindex, "PARAM_NAME_target");
CParam *PARAM_NAME_post_value = StsGetParam(funcindex, "PARAM_NAME_post_value");
CParam *PARAM_NAME_post_rt = StsGetParam(funcindex, "PARAM_NAME_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
```

**固定后缀参数**（所有Trim参数都需要）：
- `_pre_value` - trim前的值
- `_pre_bit` - trim前的bit值
- `_post_bit` - trim后的bit值
- `_updated` - 是否更新
- `_guessed` - 是否猜测
- `_target` - 目标值
- `_post_value` - trim后的值
- `_post_rt` - trim后的结果

### 15.2 Trim测试入口函数（test.cpp）
```cpp
DUT_API int TMxxx_Trim_xxx(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    // 根据15.1节规则定义参数
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &PARAM_NODE = trim_reg.trim("PARAM_NAME");

    // 1. Connect - 继电器闭合
    cbite.SetOn(...);
    delay_ms(3);

    // 2. Power On - 上电
    // 根据DFT.CSV的Hardware_initial

    // 3. Register Config - 寄存器配置
    // 根据DFT.CSV的Software_initial

    // 4. Trim 实现 - 调用sub.cpp中的测量函数
    PARAM_NODE.execute(measure_PARAM_NAME, spec, funcindex, funclabel, 1, 0, 0, 0);

    // 5. Power Off - 下电（遵循NU下电规则，RELAY_OFF时统一10V/10MA）

    return 0;
}
```

### 15.3 Trim测量函数（sub.cpp）
参考第1.4节的模板

### 15.4 注意事项
1. TRIM_NODE 是一种类型， trim_reg.trim() 是class里面的一个成员函数，trim_reg 是TRIM_NODE的一个实例化的对象，trIm_reg.trim是调用trim这个成员函数，函数里的值就是参数名。
2. MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf, spec, funcindex, funclabel, 1, 0, 0,0); 这里面的execute也是一个成员函数，里面的参数：measure_mnt_v1p2_buf这个是一个函数，组成规则是：measure_+“参数名字“，spec是固定的内容，其实也是一个对象。
3. execute 中已经包含了测量部分，因此，trim参数只需要包含：继电器闭合，上电，寄存器配置，trim 实现和下电几个步骤。
4. 根据treg文件确定EFUSE_REG封装数量和I2C地址。

## 16. NU treg参数查找规则

### 16.1 查找流程

当处理Trim测试项时，需要根据DFT.CSV中的参数名到treg文件中查找对应的配置信息：

```
1. 精确匹配：使用DFT参数名直接查找treg中的[参数名]
2. 如果精确匹配失败，进行模糊匹配
3. 如果模糊匹配也找不到，提示用户并列出treg中所有可用的参数名
```

### 16.2 精确匹配规则

**直接匹配**：DFT参数名 = treg参数名
- DFT: `HP_VBG` → treg: `[bandgap]` ❌ (不匹配)
- DFT: `IZTC_1UA` → treg: `[iztc_res]` ❌ (不匹配)
- DFT: `CV_BUF_TRIM` → treg: `[mnt_vbat_cv_buf]` ❌ (不匹配)

> 注意：DFT中的参数名和treg中的参数名可能不一致，需要进行映射或模糊匹配。

### 16.3 模糊匹配规则

当精确匹配失败时，按照以下优先级进行模糊匹配：

**匹配优先级：**
1. **子串匹配**：DFT参数名包含treg参数名，或treg参数名包含DFT参数名
   - DFT: `HP_VBG` → treg: `[bandgap]` → 匹配 "BG" 子串
   - DFT: `IZTC_1UA` → treg: `[iztc_res]` → 匹配 "IZTC" 子串
   - DFT: `CV_BUF_TRIM` → treg: `[mnt_vbat_cv_buf]` → 匹配 "CV_BUF" 子串

2. **关键词匹配**：提取DFT参数名中的关键词，在treg参数名中搜索
   - DFT: `IBAT_CHG_GAIN` → 提取关键词: `IBAT`, `CHG`, `GAIN`
   - 在treg中搜索包含 `ibat` 或 `gain` 的参数名

3. **大小写不敏感匹配**：忽略大小写进行匹配
   - DFT: `HP_VBG` → treg: `[BandGap]` → 忽略大小写匹配

**匹配策略：**
- 只返回最匹配的1个结果（匹配度最高）
- 如果有多个结果匹配度相同，列出所有候选供用户选择

### 16.4 匹配度计算

| 匹配类型 | 匹配度分数 |
|---------|-----------|
| 精确匹配 | 100 |
| 子串完全包含（DFT包含treg） | 80 |
| 子串完全包含（treg包含DFT） | 70 |
| 关键词部分匹配 | 50 |
| 大小写不敏感匹配 | 30 |

### 16.5 查找失败处理

当精确匹配和模糊匹配都找不到时：

1. **提示用户**：明确告知找不到对应的treg参数
2. **列出treg中所有参数名**：方便用户确认正确的参数名
3. **询问用户**：是否需要手动指定或跳过该参数

**提示格式示例：**
```
⚠️ 警告：在treg文件中未找到与 "HP_VBG" 匹配的参数！

treg文件中可用的参数名列表：
- bandgap
- iztc_res
- bg_res_div
- osc_4p5m
- ibus_sns_ea_os
- ibus_sns_gain
- ibus_loop_os
- ...

请确认DFT参数名是否正确，或手动指定对应的treg参数名。
```

### 16.6 treg参数动态查找规则

**核心规则：不硬编码参数列表，而是动态从treg文件中查找！**

treg（Trim Register）文件是Trim参数的权威来源，所有可用的Trim参数都定义在该文件中。不需要在规则文件中硬编码参数列表，而是应该：

1. **动态解析treg文件**：读取项目目录下的`*.treg`文件（如NU1201.treg）
2. **提取参数名**：从treg文件中提取所有`[trim_xxx]`段的参数名
3. **匹配查找**：按照16.5节的匹配规则（精确匹配→模糊匹配→用户提示）查找对应的参数

**treg文件结构示例：**
```
[trim_bandgap]
Target=1.200000
Trim_type=SIGNED
Table=0x00000000
...

[trim_iztc_res]
Target=0.000001
Trim_type=UNSIGNED
Table=0x00000000
...
```

**提取规则：** 从`[trim_xxx]`格式的段落名中提取参数名（去掉`trim_`前缀），例如：
- `[trim_bandgap]` → 参数名：`bandgap`
- `[trim_iztc_res]` → 参数名：`iztc_res`
- `[trim_buck_hsfet_gain]` → 参数名：`buck_hsfet_gain`

**优势：**
- 当treg文件更新（新增或删除参数）时，无需修改规则文件
- 适用于不同型号的芯片（不同的treg文件）
- 避免硬编码导致的维护问题

### 16.7 DFT到treg映射表（参考）

**注意：以下映射表仅作为参考示例，实际应按照16.5节的匹配规则动态查找！**

| DFT参数名 | treg参数名 | 匹配方式 |
|-----------|-----------|---------|
| HP_VBG | bandgap | 子串匹配（BG） |
| IZTC_1UA | iztc_res | 子串匹配（IZTC） |
| CV_BUF_TRIM | mnt_vbat_cv_buf | 子串匹配（CV_BUF） |
| BUCK_HS_CS_GAIN | buck_hsfet_gain | 子串匹配（BUCK_HS） |
| BUCK_HS_CS_OFFSET | buck_hsfet_os | 子串匹配（BUCK_HS） |
| BOOST_HS_CS_GAIN | boost_hsfet_gain | 子串匹配（BOOST_HS） |
| BOOST_LS_CS_GAIN | boost_lsfet_gain | 子串匹配（BOOST_LS） |

**映射逻辑：**
1. 首先尝试精确匹配（DFT参数名 = treg参数名）
2. 失败后尝试子串匹配（忽略大小写，查找DFT参数名中的关键字）
3. 子串匹配关键字示例：BG→bandgap, IZTC→iztc_res, BUCK→buck_, BOOST→boost_, GAIN→_gain, OFFSET→_os