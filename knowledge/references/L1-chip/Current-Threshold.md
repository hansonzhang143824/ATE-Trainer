# Current Threshold 电流阈值（chip Block）

> 具体参数类型族 **Current Threshold**，含 ZCD / IPeak。四件套：`L1-chip/Current-Threshold`(是什么) + `L3-method/Current-Threshold`(怎么测) + `L4-Golden-code/Current-Threshold`(长啥样) + `L5-debug/Current-Threshold`(怎么排查，按需)。

## ZCD（Zero Cross Detection 过零电流检测）

ZCD 测的是一个**电流阈值**，为提高电源芯片效率、防止反向续流导致的效率下降：

- 电流逐步降低到接近 0mA → 触发阈值保护 → 重新开启功率管、输入能量
- 芯片实际是采集 **ZCD 电流 × Rdson → Vcs（currentsense 电压）**
- 比较 Vcs 与内部 **Vref_zcd**：一旦 Vcs 超过 Vref_zcd → 指示 PIN 翻转

## 常见做法（按拓扑）

- **BUCK 模式**：做在 SW 和 PGND 的功率 MOSFET 上，检查 SW–PGND 之间的电流阈值
- **BOOST 模式**：常用 PMID 与 SW 间的电流阈值检测

## 关键特性

- **ZCD 没有迟滞，只有一个阈值点**（区别于 UVLO 有上下阈值 + HYS）

## 外挂电阻等效（无功率 MOSFET 的芯片）

特殊芯片无功率 MOSFET 时，外挂电阻在 SW–PGND 或 SW–PMID 之间，在电阻上 ramp 电流，芯片感受到差分电压 —— 与存在 MOSFET 时 ramp 电流经过 MOSFET 等效。

> PMID 只是一个例子，实际可能用别的 PIN。
