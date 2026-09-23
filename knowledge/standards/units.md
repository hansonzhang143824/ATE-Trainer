# 单位和量程规则

## 量程选择：≥ 2× 设定值

**选最接近设定值 2 倍的那一档量程。**

## 电阻单位判断

| 测量电流 | 输出单位 | 公式 |
|---------|:---:|------|
| > 100mA | mΩ | V/A × 1000 |
| ≤ 100mA | Ω | V/A × 1 |

## 电压单位
- 程序中的电压值单位: **V**
- 电流值单位: **A**

## LogData 单位 = spec 预期单位 (铁律)

**SetTestResult 的第三个参数 (结果值) 单位必须与 spec/DFT 预期单位一致**（DFT `Unit` 列权威），不能按源表原始 A/V 直接 log。

| 源表原始 | spec 预期 | 换算 |
|---------|----------|------|
| `MIRET` (A) | uA | `× 1e6` |
| `MIRET` (A) | mA | `× 1e3` |
| `MIRET` (A) | nA | `× 1e9` |
| `MVRET` (V) | mV | `× 1e3` |
| `MVRET` (V) | V | 不换算 |

```cpp
// 例: DFT Unit=uA → 乘 1e6
param[site] = <ResourceName>.GetMeasResult(site, MIRET) * 1e6;  // A -> uA
...
Param->SetTestResult(site, 0, param[site]);
```

- 换算加在 GetMeasResult 赋值处（带 `// A -> uA` 注释），不是 SetTestResult 处
- 判断依据: DFT `Unit` 列 / spec 预期值单位。无 DFT 时看参数命名约定 (µA 级 IQ 测试默认 uA)
- 反例 (错误): Iq 测试 spec 预期 uA 却 `SetTestResult(site, 0, raw_A)` → 数据差 1e6 倍, 全判 FAIL

## Ramp Hys 单位规则 (R-HYS)

**含 ramp 的 rise/fall/hys 测试 (Toggle/AWG 两段式), Hys 单位固定:**

| Hys 物理量 | 源表原始 | 预期单位 | 换算 |
|-----------|---------|---------|------|
| 电压 | `rampv_capv` 结果 (V) | mV | `× 1e3` |
| 电流 | `rampi_capv` 结果 (A) | mA | `× 1e3` |

```cpp
// 例: 电压 Hys (rampv_capv → V)
hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS)
// 例: 电流 Hys (rampi_capv → A)
hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // A -> mA (R-HYS)
...
Hys->SetTestResult(site, 0, hys[site]);
```

- 原理: Rise/Fall 是触发点 ramp 电压/电流（V/A），Hys=Rise−Fall 是差值（数值小），spec 预期用小单位 mV/mA，不是源表原始 V/A
- 换算加在 `hys[site] = rise - fall` 赋值处（带注释），不是 SetTestResult 处
- 佐证: DFT `IBUS_TERM_200mA_Hys` ExpectValue=200 **Unit=mA**
- 反例 (错误): Hys 直接 `SetTestResult(site, 0, rise-fall)` 原始 V → 数据差 1e3 倍, 全判 FAIL

## 电阻 = 实测 V / 实测 I 铁律 (R-VIR)

**电阻计算必须用实测电压和实测电流** — `R[site] = 源表.GetMeasResult(site, MVRET) / 源表.GetMeasResult(site, MIRET)`（同一源表同一次 MeasureVI 后读取）。禁止用理论设定电流（如 `Set(FI, 1e-5, ...)` 的设定值 `1e-5`）或设定电压代入。FI 灌电流测 V 时须同时读 MVRET + MIRET 再相除（R = V实测 / I实测）。强制层: check-agent **E027**。

## FV/FI 模式判断

| DFT指令 | 模式 | 说明 |
|---------|:---:|------|
| `vset[...]` | FV | Force Voltage |
| `iset[...]` | FI | Force Current |
| 测量MV但无FI配置 | FI=0 | 电流量程选最小档(10UA) |

## LogData 格式
```cpp
FOR_EACH_VALID_SITE(site) {
    Param->SetTestResult(site, 0, result[site]);
}
```
- 第一个参数: site
- 第二个参数: 0（默认）
- 第三个参数: 结果数组

## cbite.SetOn 格式
```cpp
cbite.SetOn(Kxx, Kyy, -1);  // -1 结尾
delay_ms(3);                // 紧跟 3ms 延迟
```
无继电器时:
```cpp
cbite.SetOn(-1);
delay_ms(3);
```

## 台阶式上下电
- 每步 |ΔV| ≤ 5V
- 每步后 delay_us(200)
- 上电: PinB 基准先设 → FPVI FV=0 等电位 → PinA 升至最终值
- 下电: PinA 先降到与 PinB 齐平 → PinB 归零 → 其他源 → PinA 归零
