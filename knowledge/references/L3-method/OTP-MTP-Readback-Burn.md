# OTP/MTP Readback & Burn — 典型测试方法

> 权威来源：用户 2026-09-07 口述确认（三次解释合并）。本文是 L3 方法层权威记录，索引见 `../param_type_index.md` / `../func_type_index.md` #3/#4。

## 一、这个测试项目是来做什么的

读取 OTP / MTP 中存好的烧录数据。
- **OTP**（One Time Program）：一次性烧录，不可擦除
- **MTP**（Multiple Program）：可反复擦写

读取数据的三个用途：
1. **判状态**：芯片是否被 Trim 过 → 确定每个工位 FRESH / BURNNED
2. **取码**：每个 trim 参数（如 VBG）和 option（selection）参数烧录的 code
3. **附带（可选）**：非 trim 区烧录值，如 Gain/Offset 校准系数

## 二、PRE Read（烧录前读）

**工作流**：
```
① 通过通信协议（I2C 或其他）读取 MTP/OTP 的值 → 存入变量
② 变量值 → trim_reg 成员变量 read_back 对应位置（位置在 .treg 里定义）—— set_read_back(value, site)
③ comp_read(0) 比较确认 FRESH 芯片（全零=未烧）→ 全局 BURN_FLAG[site]
④ get_read_back 把所有 Trim + option 全部打印（datalog）
   可选：非 trim 区的烧录值（Gain/Offset 校准值、SN、lot/wafer）
```

## 三、BURN（烧录）

**烧三类数据**：
| 类 | 内容 | 必须 |
|----|------|------|
| 1 | Trim 找到的 BestCode | ✅ |
| 2 | Option bit | ✅ |
| 3 | 其他需存在数据：Gain/Offset 校准系数、随机码（SN）、年月日等各类信息 | 可选 |

**执行过程**：
```
① 把 trim_reg 中 working 槽的值存入变量
② 芯片上电，配置寄存器
③ 通过通信协议烧录变量值到 NVM
④ 下电
⑤ copy_work_to_prog：把 working 值传给 programmed 槽
```

**FRESH/BURNNED 闸门（核心）**：过程中必须知道芯片是否 FRESH——
**BURNNED 的芯片禁止重新烧录**。
- 实现 = 数据写 + 密钥写；密钥逐工位选择：**FRESH → 真密钥（真触发 fuse 编程），BURNNED → 假密钥（写了无效）**
- **该闸门是 OTP/MTP 家族通用机制**：OTP FT 复流与 MTP FT 复烧都用逐工位真假密钥；仅当流程整体保证全新（如 MTP 的 CP）时才由流程闸门替代（2026-09-07 用户确认）
- 具体密钥寄存器/键值/假键值/目标地址全部是项目协议，查项目资料，不进框架模板

**MTP 额外做 CRC**：MTP 内存大，额外做 CRC 校验保证烧录正确（烧前对全部烧录数据算 CRC 随数据写入，读后重算比对）。OTP 一般没有。

## 四、POST Read（烧录后读）

- 烧录后再读一遍；读的内容一般**等于或大于** PRE read；传值方式与 PRE 相同
- **核心 = log 所有数据，保证烧录的读出来一致**
- OTP：比较 read_back vs programmed —— `comp_prog_to_read(site)`
- MTP：除 comp_prog_to_read 外**还比较 CRC 值**，确保读写一致

## 五、treg 四值槽状态机（三件套在其中的角色）

```
start（.treg 定义默认）
   │ Trim 测试步骤求 BestCode
   ▼
working ◄── copy_read_to_work（PRE 发现 BURNNED：装载芯片实况，保 SN/已烧码）
   │ BURN：烧录
   ▼
programmed ◄── copy_read_to_prog（QA/QUAL/TempChar 复流：把芯片实况登记为应烧值）
   ▲
   │ comp_prog_to_read（POST 验证：read_back == programmed？）
read_back ◄── set_read_back（PRE/POST/READBACK：从芯片读回的实况）
```

- Trim 项操作 working 槽；Burn 项操作 programmed 槽；Readback 项操作 read_back 槽
- `copy_work_to_prog`（burn 后登记应烧值）与 `copy_read_to_prog`（复流登记实况）方向相同来源不同

## 六、相关 treg API（`Library-Functions/treg/treg.h` 实测）

| API | 作用 |
|-----|------|
| `set_read_back(value, site=MS_ALL)` | 读回值写进 read_back 槽 |
| `get_read_back(site)` | 取 read_back 槽值 → datalog |
| `comp_read(INT64 value, site)` | read_back 与给定值逐位比较（PRE 判 fresh 用 comp_read(0)） |
| `comp_prog_to_read(site)` | read_back vs programmed（POST 验证） |
| `comp_read_to_start / comp_read_to_work` | read_back vs start / working |
| `copy_read_to_work / copy_read_to_prog` | read_back → working / programmed |
| `copy_work_to_prog` | working → programmed（BURN 后登记） |

## 七、OTP vs MTP 实现差异（详见 L4 案例 md）

| 维度 | OTP | MTP |
|------|-----|-----|
| 读通路 | 直读寄存器窗口 | 控制器配置写 + 数据端口顺序读 |
| 写通路 | 逐寄存器写 + 触发键 | 写端口逐字 + 写使能键 |
| CRC | 无 | 有（烧前算+读后验） |
| fresh 判定 | PRE 必须 comp_read(0) | QC/CP 流可跳过（wafer 信息已在） |
| FT 复烧/复流 | 逐工位真假密钥 | **同样逐工位真假密钥**（仅 CP 等全新流程由流程闸门替代，2026-09-07 用户确认） |
| 第三类数据 | SN、版本（少量） | 校准系数、lot/wafer/XY（信息页） |

## 七A、枚举与全局定义出处（2026-09-07 用户确认）

- `TRIM_FLOW`（FT/CP/QA/QUAL/TempChar/HTOL_Burn 等流程枚举）、`FRESH/BURNNED`（烧录状态）、`TTR_MODE` 等——**定义在各测试程序工程的全局宏定义与变量定义中**（如工程 `StdAfx.h` / 全局头文件）
- 工程源文件为 **DLP 加密（TSZ# 头）+ GBK 编码**：DSH read 工具因非 UTF-8 拒读、Bash/grep 见密文、pwsh 无 DLP 授权——具体数值需用户贴出或经工程侧确认
- 生成代码时**语义引用（TRIM_FLOW == FT 等），数值不写死在框架模板里**，以各项目全局定义为准

## 八、代码框架模板要点（生成代码时）

1. 三件套五段式：AFX 参数块 → 变量声明 → 供电+通信读/写段 → set_read_back/comp 段 → get_read_back+SetTestResult 段
2. 节点双轨：`trim_reg.trim("treg名")`（trim 码）/ `trim_reg.sel("opt名")`（option 位）；assy("寄存器组节点") 管整字
3. 验证结果必须参数化出结果（Burn_Check_Pass / Burn_Done / CRC_CODE_CHECK_L/HByte）
4. 无模拟量测量、无限值判断——出值全是代码快照
5. BURN_FLAG 是跨项全局状态；PRE 是它的唯一生产者
