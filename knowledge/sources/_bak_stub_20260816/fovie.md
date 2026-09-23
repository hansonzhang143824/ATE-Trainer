# FOVIe 源表参考

## 概述
FOVIe — 四象限源测量单元，非浮空源（Low端默认接AGND）。

## Set 函数签名
```cpp
<ResourceName>.Set(mode, value, vRange, iRange, RELAY);
```

## 模式
| 模式 | 含义 | 使用场景 |
|------|------|----------|
| `FV` | Force Voltage | vset 指令 |
| `FI` | Force Current | iset 指令 / MV测量时设FI=0 |

## RELAY 控制
| 值 | 含义 |
|----|------|
| `FOVIe_RELAY_ON` | 源表输出导通 |
| `FOVIe_RELAY_OFF` | 源表输出断开 |

## 量程表

### 电压量程
| 设定值范围 | 选用量程 |
|-----------|---------|
| V ≤ 0.5V | `FOVIe_1V` |
| V ≤ 1V | `FOVIe_2V` |
| V ≤ 2.5V | `FOVIe_5V` |
| V ≤ 5V | `FOVIe_10V` |
| V ≤ 10V | `FOVIe_20V` |
| V ≤ 20V | `FOVIe_40V` |

### 电流量程
| 设定值范围 | 选用量程 |
|-----------|---------|
| I ≤ 5μA | `FOVIe_10UA` |
| I ≤ 50μA | `FOVIe_100UA` |
| I ≤ 500μA | `FOVIe_1MA` |
| I ≤ 5mA | `FOVIe_10MA` |
| I ≤ 50mA | `FOVIe_100MA` |
| I ≤ 500mA | `FOVIe_1A` |

## 量程选择规则
**量程 ≥ 2 × 设定值**，选最接近的一档。

## MeasureVI / GetMeasResult
同 ACM200，支持 MIRET/MVRET。

## 所在槽位
S3, S4, S13, S14, S19, S20, S29, S30 — 每槽 8 通道 (FH/SH 0~7)
