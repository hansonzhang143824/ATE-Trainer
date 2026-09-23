# UVLO 欠压锁定阈值（chip Block）

> 具体参数类型族 **UVLO**，含 UVLO / OVP / PRST / VBAT_LOW / RECHG。四件套：`L1-chip/UVLO`(是什么) + `L3-method/UVLO`(怎么测) + `L4-Golden-code/UVLO`(长啥样) + `L5-debug/UVLO`(怎么排查，按需)。

## 是什么

芯片为保证输入电压过低时切断电源轨道、保护电路，设计了 **UVLO（Under-Voltage Lock-Out，欠压锁定）**。它本质是一个**阈值电压**：

- 电压从高于 UV 上限下降 → 达到**上阈值**，芯片**无反应**
- 继续下降到**下阈值以下** → 芯片**触发 UV 保护**（切断电源轨道）
- 此时增加供电电压超过**下阈值** → 芯片**不恢复**
- 继续增加到超过**上阈值** → 芯片**才恢复**

上下阈值之差 = **迟滞 HYS**，用于防止电压在阈值点附近波动导致芯片反复触发/恢复 UV。

## 指示 PIN

UV 触发/恢复时，内部状态机读取该信号，mux 到一个指示 PIN 上：

- 有的叫 **POWER GOOD（PG）**，有的就是 **DTEST PIN**
- 结构：**Open-Drain**（需接上拉，见 FR-002）或 **Push-Pull**（不用）
- power 状态变动 → 指示 PIN 上要么高电平、要么低电平

## 同类阈值（原理同 UVLO）

- **OVP** 过压保护：原理与 UVLO 相同
- **PRST** present 电压阈值：等效于 UVLO
- **VBAT_LOW**：同样的阈值保护
- **RECHG**：同样属阈值保护类
