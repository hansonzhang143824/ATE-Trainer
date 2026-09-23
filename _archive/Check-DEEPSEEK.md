# 项目规则与错误跟踪

## 第一优先级：核心原则

> **重要**：以下原则为最高优先级，任何其他规则都不能违反这些原则。执行任何测试代码前，必须首先检查这些原则是否满足。

| 序号 | 原则 | 优先级 | 描述 |
|------|------|--------|------|
| P001 | DFT至上原则 | **最高** | 测试条件必须严格满足DFT要求，不得自行创造；仅浮动源配置存在推理空间（有大电流意味着两个引脚电压基本相同） |
| P002 | 继电器配置原则 | **最高** | 继电器必须根据DFT和资源分配表确定，不得虚构不存在的继电器；继电器配置不得有冲突，必须符合规则 |
| P003 | 规则匹配原则 | **最高** | 根据测试参数特点选择对应的规则执行，如Trim测试用Trim规则，AWG测试用AWG规则 |
| P004 | 疑问处理原则 | **最高** | 对于不清楚或矛盾的问题，直接向用户提问，不得凭空捏造答案 |
| P005 | 规则更新原则 | **最高** | 错误理解后必须更新规则；规则描述应使用类型化语言，而非具体引脚名称；具体引脚可作为参考案例 |

### 核心原则执行流程
1. **DFT验证**：执行任何测试前，首先验证所有测试条件是否符合DFT要求
2. **资源验证**：验证所有继电器配置是否来自资源分配表，无虚构或冲突
3. **规则匹配**：根据测试类型选择对应的规则集
4. **疑问确认**：对于任何不确定的问题，立即向用户提问
5. **规则更新**：发现错误后，立即更新规则文件，确保不再重复

## 错误跟踪日志

| 日期 | 错误编号 | TM项 | 错误描述 | 正确模式 | 状态 |
|------|----------|------|----------|----------|------|
| 2026-07-04 | E001 | TM125/TM130 | Trim参数只定义了单个参数指针，缺少step0~stepN和固定后缀参数 | 根据treg位数定义所有step参数 + 8个固定后缀参数 | ✅已修复 |
| 2026-07-04 | E002 | TM125/TM130 | Trim测试直接调用MeasureVI() | Trim测试必须使用TRIM_NODE.execute()模式 | ✅已修复 |
| 2026-07-04 | E003 | TM109/TM110 | VAC2/VAC3测试缺少继电器连接 | VAC2需要K36_VAC_SHARE2，VAC3需要K35_VAC_SHARE | ✅已修复 |
| 2026-07-04 | E005 | TM105/TM106/TM108/TM109/TM110 | AW测试只定义了单个参数 | AW测试固定包含3个参数：Parm_Rise、Parm_Fall、Parm_Hys，必须全部定义 | ✅已修复 |
| 2026-07-04 | E006 | TM600/TM601/TM606/TM607/TM608/TM609/TM623/TM624/TM625/TM626 | 虚构源表名称（SW_PMID_FPVI、PMID_SW_FPVI、SW_PGND_FPVI、BST_FPVI） | 资源分配表中只有FPVI和FPVI_PC两个FPVI资源，必须使用FPVI | ✅已修复 |
| 2026-07-04 | E007 | TM600/TM608/TM609/TM623/TM625 | 浮动电压源未使用台阶式上下电 | 浮动电压源必须台阶式上电/下电，每步间隔200us | ✅已修复 |
| 2026-07-04 | E008 | TM600 | 继电器配置错误：同时闭合两个共享引脚的浮动源BUS继电器导致短接 | 当两个浮动源共享同一引脚时，优先保证电流浮动源，放弃电压浮动源的BUS继电器 | ✅已修复 |
| 2026-07-04 | E009 | TM600 | 下电时未设置FPVI=FV=0强制等电位 | 上电和下电都必须先设置FPVI=FV=0，确保相关引脚等电位 | ✅已修复 |
| 2026-07-04 | E010 | TM600 | 上电/下电顺序错误，导致压差超限 | 浮动电压源必须始终满足0 ≤ 高位引脚 - 低位引脚 ≤ 5V；上电时高位先上升，低位跟随；下电时低位先下降，高位跟随 | ✅已修复 |
| 2026-07-04 | E011 | TM607/TM608/TM609/TM623/TM625 | 继电器配置错误：使用错误继电器导致冲突 | 使用正确的继电器配置，避免BST和PMID通过SW短接 | ✅已修复 |
| 2026-07-04 | E012 | TM607/TM608/TM609/TM623/TM625 | 上电/下电未设置FPVI=FV=0强制等电位 | 上电和下电都必须先设置FPVI=FV=0，确保相关引脚等电位 | ✅已修复 |
| 2026-07-04 | E013 | TM607/TM608/TM609/TM623/TM625 | 浮动电压源电压顺序错误，未遵循台阶式上下电规则 | 浮动电压源始终满足压差约束；上电时高位先上升，低位跟随；下电时低位先下降，高位跟随；每次电压变化后等待200us | ✅已修复 |
| 2026-07-04 | E014 | TM608 | 浮动电压源电压计算错误：BST设置为10V，实际应为14V | 根据DFT配置计算电压：BST = SW + 5V = 9V + 5V = 14V | ✅已修复 |
| 2026-07-04 | E015 | TM609/TM623/TM625 | PMID电压设置错误：PMID设置为9V，DFT要求为5V | 严格按照DFT中PMID的设定值，不得自行修改 | ✅已修复 |
| 2026-07-04 | E016 | TM607 | 浮动电压源压差超限：BST设置为10V，SW=0V，压差10V>5V | BST最高设置为5V（SW=0V时，BST-SW≤5V） | ✅已修复 |
| 2026-07-04 | E017 | TM608 | 台阶上下电不完整：上电缺少中间台阶，下电缺少FPVI逐步降压 | 上电和下电都必须确保每步压差≤5V，使用FPVI的FV模式逐步调整电压 | ✅已修复 |

## Trim测试规则

### 参数定义规则
- 根据treg文件确定参数位数：step数 = 2^位数
- 在AFX块中定义所有step参数：step0 ~ stepN（N = 2^n - 1）
- 在AFX块中定义所有固定后缀参数：_pre_value, _pre_bit, _post_bit, _updated, _guessed, _target, _post_value, _post_rt

### 测量模式规则
- Trim测试必须使用 `TRIM_NODE.execute(measure_xxx, spec, funcindex, funclabel, 1, 0, 0, 0)`
- 绝对不能直接调用 `MeasureVI()` 在test.cpp中

### 文件分工规则
- 测量函数 `measure_xxx` 必须放在sub.cpp中
- 测试入口函数 `TMxxx_Trim_xxx` 必须放在test.cpp中

## AWG/Toggle测试规则

### 类型识别规则
- DFT.csv中Type列包含"Toggle" → 确定为AWG测试
- AWG测试必须定义3个参数：Rise、Fall、Hys

### 参数定义规则
- 参数1：`ShortName_Rise` → 上升沿阈值
- 参数2：`ShortName_Fall` → 下降沿阈值
- 参数3：`ShortName_Hys` → 迟滞（自动计算：Rise - Fall）
- 所有参数必须在AFX块中定义

### 测量模式规则
- 使用 `test_method.rampv_capv()` 或 `test_method.rampi_capv()`
- 上升沿测量：ramp从低到高，TRIG_FALLING触发，结果存入Rise数组
- 下降沿测量：ramp从高到低，TRIG_RISING触发，结果存入Fall数组
- Hys = Rise - Fall，自动计算并设置结果

## 通用测试规则

### 参数定义规则
- 所有CParam定义必须放在 `//{{AFX_STS_PARAM_PROTOTYPES` 和 `//}}AFX_STS_PARAM_PROTOTYPES` 之间

### 芯片测试模式规则
- 芯片上电后需先调用 `entertestmode()` 进入测试模式
- 测试模式在不下电情况下保持有效，无需重复调用

### 代码注释规则
- **DFT配置注释**：每个测试函数开头必须注释DFT配置信息，包括电压源、电流源、测量方式等
- **继电器配置注释**：每个继电器必须注释其作用和对应的引脚
- **电源阶段注释**：每个电源上电/下电阶段必须注明该阶段各引脚的电压值
- **浮动源电压标注**：涉及浮动源（`vset[PinA2PinB,...]`或`iset[PinA2PinB,...]`）的测试代码，必须在注释中标注浮动源两端Pin的实时电压（格式：PinA=XXV, PinB=XXV）
- **台阶式上下电注释**：台阶式上下电的每个台阶都需标注该台阶各引脚的电压值
- **大电流加载注释**：大电流加载时必须标注电流路径方向（格式：PinA → DUT内部 → PinB）
- **量程选择注释**：非零力设置需注释量程选择依据（量程≥设定值×2）

## 继电器配置规则

### 核心原则
- 继电器配置取决于源表绑定关系，需从资源分配表.csv中查找
- 步骤：根据DFT.csv中的Hardware_initial确定使用的引脚 → 在资源分配表.csv中查找对应的"Connect Relay to Resource"列 → 非"Default"的继电器必须闭合

### 冲突处理规则
- **浮动源冲突规则**：当两个浮动源共享同一引脚时，会导致第三个引脚被短接，因此必须放弃一个浮动源的BUS继电器；优先保证电流浮动源（iset），放弃电压浮动源（vset）的BUS继电器
- **单Pin配置规则**：单Pin电压配置（`vset[PinName,...]`）不闭合BUS继电器，闭合电容继电器

### 操作规则
- 如果没有继电器需要闭合，必须使用 `cbite.SetOn(-1);`
- 所有继电器必须在cbite.SetOn()中列出

## 浮动源规则

### 定义识别
- **浮动电压源**：`vset[PinA2PinB,电压,电流,0]` - 定义PinA和PinB之间的电压差
- **浮动电流源**：`iset[PinA2PinB,电流,电压,0]` - 定义PinA和PinB之间的电流

### 电压计算规则
- **核心公式**：PinA电压 = PinB电压 + 设定电压差
- **大电流推理规则**：当存在大电流浮动源（iset[PinA2PinB,电流,...]）时，说明PinA和PinB之间有大电流流动，推断PinA和PinB电压基本相同

### 压差约束规则
- **全局约束**：0 ≤ PinA电压 - PinB电压 ≤ 5V（适用于所有浮动电压源）
- **单Pin配置例外**：`vset[PinName,...]`单Pin配置不受此约束，因其不涉及两个引脚的压差

### 台阶式上下电规则
- **触发条件**：只要DFT中出现`vset[PinA2PinB,a,...]`配置且`a<6V`，整个程序中PinA和PinB的上电都必须使用台阶上下电规则
- **上电顺序**：高位引脚（PinA）先上升到目标电压或以上，低位引脚（PinB）再跟随上升
- **下电顺序**：低位引脚（PinB）先下降，高位引脚（PinA）再跟随下降
- **每步延迟**：每次电压变化后必须等待200us，确保电压稳定
- **FPVI辅助规则**：上电和下电都必须先设置FPVI=FV=0，强制相关引脚等电位；下电时使用FPVI的FV模式逐步降低电压，避免压差突然变大

### 短路避免规则
- **端点数量规则**：每个浮动源只能连接2个端点，1端或3端及以上都不行
- **共享引脚规则**：当两个浮动源共享同一引脚时，必须放弃一个浮动源的BUS继电器；优先保证电流浮动源（iset），放弃电压浮动源（vset）的BUS继电器

### 电压标注规则
- **标注范围**：所有涉及浮动源（`vset[PinA2PinB,...]`或`iset[PinA2PinB,...]`）的测试代码，必须在注释中标注浮动源两端Pin的实时电压
- **标注格式**：使用统一格式标注两端Pin的电压值（格式：PinA=XXV, PinB=XXV）
- **上电阶段标注**：每个上电阶段必须标注该阶段浮动源两端Pin的电压值，包括初始等电位阶段（FV=0）和目标电压阶段
- **下电阶段标注**：每个下电阶段必须标注该阶段浮动源两端Pin的电压值，包括切换回FV=0等电位阶段
- **台阶式上下电标注**：台阶式上下电的每个台阶都需标注该台阶浮动源两端Pin的电压值
- **大电流加载标注**：大电流加载时必须标注电流路径方向（格式：PinA → DUT内部 → PinB），并标注加载时两端Pin的电压值
- **标注示例**：
  ```
  // 浮动源 iset[sw2pgnd,3] 上电阶段
  // 阶段1: PMID=0V, SW=0V (FPVI强制等电位), PGND=0V
  // 阶段2: PMID=5V, SW=0V, PGND=0V
  // 大电流加载: SW≈5V, PGND=0V (电流路径: SW → DUT内部 → PGND)
  ```

## 电源配置规则

### 量程选择规则
- 对于非零力设置（FV/FI/FPVI/FOVI/ACM200），量程必须大于等于设定值的2倍
- FPVI量程选择：0.5A选1A，1A选2A，2A以上选10A
- 高电流测试电压量程使用FPVIe_1V（大电流测试不需要大电压）

### 继电器状态规则
- RELAY_ON状态保持原始量程
- RELAY_OFF状态统一使用10V/10MA

### 大电流测试流程
- FPVI.Set(FV, 0) → FPVI.Set(FI, 0) → 配置寄存器 → 芯片管子打开 → 设置电流测量 → 测量完毕 → FPVI.Set(FI, 0) → FPVI.Set(FV, 0) → 台阶式下电
- 高电流加载需要1ms~5ms（推荐2ms）稳定延迟后再测量

## 硬约束规则

- AWG testing must use `test_method.rampv_capv()` library function; original STSAWG method is removed
- Trim measurement functions must be placed in sub.cpp, test functions in test.cpp
- Trim function naming format: `measure_` + parameter name
- For treg file parsing: Determine number of working_values based on `[_EFUSE_REG_Fx]` encapsulation; `_F0/_F1/_F2` suffixes in encapsulation names correspond to I2C addresses `0xF0/0xF1/0xF2`
- Power-down range rules: RELAY_ON state maintains original range; RELAY_OFF state uniformly uses 10V/10MA
- treg parameter lookup process: exact match first, then fuzzy match (substring, keyword, case-insensitive), finally prompt user if not found
- AMUX-NTC measurement requires FI mode (FI=0) with 10UA current range; FV mode is forbidden for voltage measurement
- Measurement mode distinction: FV (Force Voltage) for current measurement, FI (Force Current) for voltage measurement
- Current ≥1A is defined as high current and must use FPVI; FPVI range must be greater than current value
- FPVI_BUS is a common bus; closing multiple relays causes corresponding pins to short
- Only pins involved in iset commands need to close corresponding FPVI_BUS relays; AMUX and NTC FPVI_BUS relays (K40, K41) must not be closed
- High current loading sequence: Set FV=0 → switch to FI=0 → set clamp after FI mode → load current → measure → immediately set current to 0
- FPVI zero current setting must be placed between measurement and data processing
- If no relays need to be closed, must use `cbite.SetOn(-1);` instead of omitting
- Toggle signal observation source must be SDA_INT_ACM; NTC_FOVI or AMUX_FOVI are forbidden
- Current ramp testing must use `test_method.rampi_capv()` library function
- Relay configuration must include all required voltage source capacitor relays, FPVI_BUS relays for floating sources, P2P relays between BST and SW, and pull-up resistors for INT pins in toggle tests
- Only actually needed source tables should be used in test code
- 所有测试函数的参数定义必须放在 `//{{AFX_STS_PARAM_PROTOTYPES` 和 `//}}AFX_STS_PARAM_PROTOTYPES` 之间
- 程序中所有源表（FPVI、ACM200、FOVI）返回的电压单位都是 V（伏特），电流单位都是 A（安培）
- 电阻单位选择规则：测量电流>100mA时输出mΩ（计算公式V/A×1000），≤100mA时输出Ω（计算公式V/A×1）
- 模式参数是否需要实现为ramp取决于测试类型：Toggle测试使用rampi_capv/rampv_capv，MI/MV/MV&MI（如RDSON）和Trim测试使用静态FI/FV设置
- 测试项目合并规则：仅当两个参数在同一Function Name中时合并测试项目，其他情况不合并
- 单Pin电压设置（`vset[Pin,电压]`）不需要FPVI_BUS继电器；仅浮动源配置（`vset[PinA2PinB,电压]`和`iset[PinA2PinB,电流]`）需要对应的FPVI_BUS继电器
- 当DFT缺少浮动电压源配置时，BST电压必须等于SW电压，VDRV电压必须等于LG电压，防止压差过大

## 错误模式分类

| 错误模式 | 描述 | 典型错误编号 |
|----------|------|--------------|
| EM001 | 参数定义错误 | E001, E005 |
| EM002 | 测量模式错误 | E002 |
| EM003 | 源表名称错误 | E006 |
| EM004 | 继电器配置错误 | E003, E008, E011 |
| EM005 | 浮动源电压计算错误 | E014, E015, E016 |
| EM006 | 浮动源上下电顺序错误 | E007, E009, E010, E012, E013, E017 |
| EM007 | 量程选择错误 | - |
| EM008 | 大电流测试流程错误 | - |
