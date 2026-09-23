# 芯片测试项目清单（test-item catalog）— L2 层骨架

> 来源：用户 2026-09-02 提供（19 大类）。
> 归属：4 层框架的 **L2「芯片测试项目基础知识」层**。
> 用途：作为芯片测试项目的**目录**——每一项后续填充"该测试项目 → 测什么/怎么测/观测脚/派生知识"，并与 L3（ATE 方法）/ L4（黄金案例）挂钩。
> 状态：**项目清单（骨架）**，逐项知识待填充/用户校验。

## 1. 基本功能参数测试（Basic function）

- a) 频率测试 Frequency
- b) 时间参数测试 Time
- c) DC 电压 DC voltage
- d) DC 电流 DC current

## 2. 一般电压阈值测试（Voltage threshold）

> ✅ **通用 ATE 方法**：见 `ATE-primer.md`（阈值电压类：Pin+PRST/UVLO/OVP/LOW → Rising/Falling/Hys）。观测脚=DTEST0(nQON)。

- a) PRST 电压阈值（Power-on reset）✅ 代表项目 `VAC1_PRST`
- b) OVP 过压保护（Over-voltage，见 L2-test-items `06-ovp.md`）✅ 代表项目 `VBAT_OVP`
- c) UVP 欠压保护（Under-voltage，见 `04-uvlo.md`）✅ 代表项目 `VBUS_UVLO`
- d) OCP 过流保护（Over-current，见 `05-ocp.md`，电压阈值类/电流触发）
- e) RECHG 电压保护（重新充电阈值）✅ 代表项目 `VBAT_RECHG`（⚠️ Hys 不×1e3，见 ATE-primer）

## 3. 一般电流阈值测试（Current threshold）

- a) TRIKEL 电压阈值保护（Trickle 阈值）✅ 代表项目 `VBAT_TRICKLE`（见 ATE-primer VTRICKLE 节）
- b) 内置/外置 Current sense 功能介绍
- c) PEAK current 峰值电流
- d) Trickle 电流测试
- e) Iterm 电流测试
- f) ZCD 测试（零电流检测，见金案例 HS_ZCD/LS_ZCD）

## 4. Current Sense 测试（电流检测，见 `07-current-sense.md`）

- a) Current Sense Gain（增益）
- b) Current Sense Offset（偏移）

## 5. IR_COMP 测试（电流环补偿）

## 6. 电压精度测试（Voltage accuracy）

## 7. 电流精度测试（Current accuracy）

## 8. 上管电阻测试（HS RON，见L1-chip 03-mosfet-drive + 01-bootstrap）

## 9. 下管电阻测试（LS RON，见L1-chip 03-mosfet-drive）

## 10. ADC 电压测试

## 11. ADC 电流测试

## 12. ADC 电压校准测试

## 13. ADC 电流校准测试

## 14. Burn（烧录/老化？—— 按项目解析，可能指 Trim/OTP 烧录）

## 15. OS（Open/Short 开短路，见 references 相关）

## 16. P2P（Pin-to-Pin 漏电/互短，见 path-principles ②'）

## 17. ABS（绝对最大额定？/ 或 ABS 保护）

## 18. READ_PRE（读取前状态/预读）

## 19. READ_POST（读取后状态/回读）

---

## 与既有知识的映射

- ✅ **已有 ATE 方法（L3，见 `ATE-primer.md`）**：PRST/UVLO/OVP/LOW 阈值电压类（统一 Rising/Falling/Hys）+ VTRICKLE/RECHG
- ✅ 已挂 L3→L2：`VAC1_PRST` / `VBUS_UVLO` / `VBAT_OVP` / `VBAT_LOW` / `VBAT_TRICKLE` / `VBAT_RECHG`
- ✅ 已有成熟知识：UVLO(04) / OCP(05) / OVP(06) / Current Sense(07) / nFAULT(08) / 自举+RON(01/03) / VREF(10) / 差分对处理(diff-pair-spec)
- ⏳ 待补：电压/电流精度、ADC 电压/电流、校准、OS/P2P/ABS、Burn、READ_PRE/POST、IR_COMP、ZCD、PEAK/Iterm 等
- **L4 黄金案例缺口**：见下表

> ⏳ 本文件为**骨架记录**，逐项知识待填充（用户校验 + 补 L3 方法 + 挂 L4 案例）。
