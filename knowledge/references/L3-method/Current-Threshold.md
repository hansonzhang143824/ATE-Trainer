# Current Threshold 测试方法（method）

> 阈值测试 = AWG（ramp 电流 → monitor 翻转）。四件套：`L1-chip/Current-Threshold`(是什么) + `L3-method/Current-Threshold`(怎么测) + `L4-Golden-code/Current-Threshold`(长啥样) + `L5-debug/Current-Threshold`(怎么排查，按需)。

## 典型测试方法（ZCD）

1. 在 **PGND–SW** 或 **PMID–SW** 之间 **ramp 电流**
2. 观测指示 PIN 的 toggle 信号翻转
3. 翻转点对应阈值电流 = **ZCD 电流**

## 关键注意

- **ZCD 无迟滞**，只有一个阈值点（不像 UVLO 要测上下两个阈值 + HYS）

## 框架归属

- 项目结构类型 → **一般测试项目**（AWG 翻转）
- 测量方法 → **`test_method` 成员函数**（`rampi_capv`，电流 ramp）取代 `measureVI`
