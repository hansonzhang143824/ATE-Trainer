# 模块 10：基准电压 VREF（Reference / Bandgap）

> 初稿（待用户校验）：领域知识整理 + 本工程 VREF 相关测试（TM130、TM424/425）。
> ⏳ **待用户修改校验**。

## 1. 功能

**VREF / Bandgap（带隙基准）**：芯片内部的**参考电压源**（如 1.2V、1.65V），是所有比较器/ADC/阈值的**基准**。
是芯片的"标尺"——OVP/UVLO/OCP 等阈值都是与 VREF 比较得出的。
> 检测类测试（电压/电流阈值）的准确度依赖 VREF 稳。有的测试项**先测 VREF** 再测阈值。

## 2. 硬件结构

- **带隙基准电路**：产生温度稳定的 VREF（如 bandgap → 1.2V，再分压出 1.65V 等）
- **VREF 引脚/内部**：VREF 引到观测点（如 ATEST0/AMUX），或内部使用
- **缓存/分压**：VREF 经缓冲/分压后供比较器

## 3. ATE 测试方法（通用）

- **直接测 VREF**：通过观测脚（ATEST0/AMUX/VDM——功能代称，按项目解析）读 VREF 电压值
- **VREF 精度/温度**：评估 VREF 是否在设计范围内（常温+高温）
- **阈值依赖**：OVP/UVLO 阈值 = f(VREF, 分压比) → VREF 偏则阈值偏
- **本工程**：`TM1100_DEMO_VREF_1P65`（读 1.65V 基准）、`TM130_VCC_VBAT_HT`（VREF 相关）、`TM424_VREF_TRIM`/`TM425_VREF_1P2V_BUF`

## 4. 派生知识（可推导的测试要求）

| 想问/要测 | 推导 |
|---|---|
| **阈值准不准** | 先确认 VREF 稳（带隙/factor）→ VREF 偏则阈值偏 |
| **测阈值前** | 若比较器用 VREF → 考虑先测/确认 VREF |
| **VREF 值怎么读** | ATEST0/AMUX/VDM 观测脚（功能代称），高阻读电压（FI=0 量程） |
| **与 Trim 关系** | VREF 可 Trim（TM424 类）→ 需在 Trim 后测 |

## 5. 易错点

- ❌ 阈值测偏却怪比较器——先排查 VREF 是否稳（VREF 偏导致阈值整体平移）
- ❌ 读 VREF 用错量程/引脚（观测脚是功能代称，按项目解析）
- ✅ VREF 是基准，影响整片阈值类测试——设计阈值测试前先确认 VREF

## 6. 实例引用

- TM1100_DEMO_VREF_1P65（1.65V 基准 demo）
- TM424_VREF_TRIM / TM425_VREF_1P2V_BUF（VREF trim / 1.2V 缓冲）
- TM130 等 VREF 相关；golden UVLO.cpp / OVP.cpp 阈值均依赖 VREF
