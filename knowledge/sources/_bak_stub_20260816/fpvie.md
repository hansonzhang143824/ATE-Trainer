# FPVIe 源表参考

## 概述
FPVIe — 大电流四象限源测量单元，**浮空源**（High/Low 端均不默认接AGND）。
只有浮空跨Pin操作（iset/vset[AxB]）时才需要 FPVI 参与。

## Set 函数签名
```cpp
FPVI.Set(mode, value, vRange, iRange, RELAY);
```

## 模式
| 模式 | 含义 | 使用场景 |
|------|------|----------|
| `FV` | Force Voltage | 浮动电压源(vset[AxB])、等电位(FV=0) |
| `FI` | Force Current | 浮动电流源(iset[AxB])、大电流测试(≥1A) |

## RELAY 控制
| 值 | 含义 |
|----|------|
| `FPVI_RELAY_ON` | 源表输出导通 |
| `FPVI_RELAY_OFF` | 源表输出断开 |

## 量程表

### 电压量程
| 设定值范围 | 选用量程 |
|-----------|---------|
| V ≤ 50mV | `FPVIe_100MV` |
| V ≤ 0.5V | `FPVIe_1V` |
| V ≤ 1V | `FPVIe_2V` |
| V ≤ 2.5V | `FPVIe_5V` |
| V ≤ 5V | `FPVIe_10V` |
| V ≤ 10V | `FPVIe_20V` |
| V ≤ 20V | `FPVIe_40V` |
| V ≤ 50V | `FPVIe_100V` |

### 电流量程
| 设定值范围 | 选用量程 |
|-----------|---------|
| I ≤ 5μA | `FPVIe_10UA` |
| I ≤ 50μA | `FPVIe_100UA` |
| I ≤ 500μA | `FPVIe_1MA` |
| I ≤ 5mA | `FPVIe_10MA` |
| I ≤ 50mA | `FPVIe_100MA` |
| I ≤ 500mA | `FPVIe_1A` |
| I ≤ 1A | `FPVIe_2A` |
| I ≤ 5A | `FPVIe_10A` |

## FPVI 特殊操作

### SetClamp
```cpp
FPVI.SetClamp(vClamp, iClamp);  // 电压钳位, 电流钳位
```

### 大电流测试三段式（≥1A）

**初始化（execute前）：**
```cpp
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 1. FV=0
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 2. FI=0
FPVI.SetClamp(25, 25);                                  // 3. Clamp
```

**测量中（sub.cpp measure函数内）：**
```cpp
FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 加载电流
delay_us(2000);                                         // 稳定2ms
// ... MeasureVI ...
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 立即关断
```

**关闭（execute后）：**
```cpp
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 1. FI=0
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);   // 2. FV=0
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_OFF);  // 3. OFF
```

## FPVI 等电位规则
- 浮动电压源上下电必须: `FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON)`
- 作用: 强制 PinA = PinB，为台阶式上下电建立基础
- 永远是最后一个 RELAY_OFF 的源
