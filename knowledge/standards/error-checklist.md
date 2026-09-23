# 错误检查清单（速查）

> 统一错误码体系 (P/E/R/H 四层)，完整定义见 `agents/check-agent.md`（60+ 项 P/E/R/H 检查）。
> 使用方：check-agent（Step 5 收尾双查）、verify_awg_params.py / verify_relay_trace.py / check_testitems_meta.py 门禁。
> 关联：`toggle-awg-rules.md`（H010）、`register-config.md`（H011）、`relay-checklist.md`（H009/P006/R004）。

| 层 | 含义 | 示例 |
|----|------|------|
| **P** (Principles) | 核心原则 | DFT至上、继电器来源、规则匹配、**反短接(P006)** |
| **E** (Errors) | 硬错误 | Trim参数、AFX注释、电压计算、台阶缺失 |
| **R** (Rules) | 规则检查 | 量程≥2×、FV/FI模式、Cap2规则、Mon_src |
| **H** (Hard) | 硬约束 | AWG用rampv_capv、Trim在sub.cpp、合并规则 |

## 常用错误码明细

| 码 | 规则 | 说明 |
|----|------|------|
| **H009** | **反短接**: 通路经过非目标PIN / Share两侧同时闭合 | 非目标PIN禁驱动，除非浮动源连接两PIN（check-agent P006） |
| **H010** | **AWG/Toggle参数**: 两段式ramp必须3参数 `<基名>_Rise/_Fall/_Hys` (基名=DFT参数名, 如VBAT_UV_Rise) | Hys=Rise−Fall，禁止单参数（check-agent E005 + verify_awg_params.py） |
| **H011** | **配寄存器前进测试模式**: 只要有重新上电，配置寄存器之前必须先 `entertestmode()` | 上电后未调用 entertestmode() 直接 I2CWriteSameData → FAIL（check-agent R034） |
| **E025** | **LogData 单位** | SetTestResult 单位必须与 spec/DFT 预期一致（有 DFT 判 FAIL，无 DFT 判 WARN），见 `units.md` §LogData |
| **E026** | **Ramp Hys 单位** | Hys 电压→mV / 电流→mA（×1e3），见 `units.md` §Ramp Hys 单位 |
| **E027** | **电阻=实测V/实测I** | 禁止用设定值代入，见 `units.md` §电阻 |
| **R034** | **entertestmode 顺序** | 上电后、配寄存器前必须有 entertestmode()，见 `register-config.md` |
| **E011** | **无继电器 SetOn(-1)** | 无继电器需闭合时显式 `cbite.SetOn(-1)`，见 `relay-checklist.md` 11步清单 |
