# UVLO 测试方法（method）

> 阈值测试 = AWG（ramp 电压 → monitor 翻转）。四件套：`L1-chip/UVLO`(是什么) + `L3-method/UVLO`(怎么测) + `L4-Golden-code/UVLO`(长啥样) + `L5-debug/UVLO`(怎么排查，按需)。

## 典型测试方法

1. 供电 PIN 上 **ramp 电压从低到高**，观测 monitor PIN 的翻转 → 翻转点 = **上阈值**
2. 供电 PIN 上 **ramp 电压从高到低**，观测 monitor PIN 的翻转 → 翻转点 = **下阈值**
3. 上下阈值之差 = **迟滞 HYS**，一般用 **mV** 表示（R-HYS：Hys 电压量 → mV）

## 框架归属

- 项目结构类型 → **一般测试项目**（AWG 翻转）
- 测量方法 → **`test_method` 成员函数**（`rampv_capv`）取代 `measureVI`
- 参数命名 → `ShortName_Rise` / `_Fall` / `_Hys`（Hys = Rise − Fall）

## 指示 PIN 结构注意

- Open-Drain → 需接上拉（FR-002 PU 开漏上拉）
- Push-Pull → 不用
