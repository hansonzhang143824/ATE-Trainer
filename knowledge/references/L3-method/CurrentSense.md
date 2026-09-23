# Current Sense 测试方法（method）

> 四件套：`L1-chip/CurrentSense`(是什么) + `L3-method/CurrentSense`(怎么测) + `L4-Golden-code/CurrentSense`(长啥样) + `L5-debug/CurrentSense`(怎么排查，按需)。

## Trim 顺序（铁律）

**先 Trim Offset，再 Trim Gain**。若先 Trim Gain，Gain 值一般不在小电流/0 电流 Trim，Offset 中的 Gain error 会带来影响。

| 参数 | Trim 条件 | 理由 |
|---|---|---|
| Offset (Vos) | **0 电流** Trim（除非 DE 的 DFT 明确要求特定电流） | 排除 Gain error 影响 |
| Gain | **大电流** Trim + **两点做差法** | 保证 Gain 可靠性，排除固定 offset |

## 测量电路设计关注点

- Current Sense 电压**驱动能力弱** → 测量源需**足够大的输出阻抗**（硬件设计时向 DE 咨询驱动能力，同时确认 Reference 驱动能力）
- 电流 **force 点位**和 **Sense 点位**选取重要，走线满足**均流**要求
- 多球（多 die）保留**单球测试 + 多球测试**选项，应对均流和潜在应力问题
- 外置 Sense 电阻：沿用 **4 线 Kelvin** 设计思路

## 差分电压测量方法

- 用源表产生独立 current sense 电压：在**固定小电阻上产生大电流** → 得到相对准确的差分电压，接入芯片 **Force 端**
- 差分电压测量用**运算放大器**执行，经继电器接入芯片 **Sense 端**，保证运放测量的电压与芯片感受的电压一致

**差分运放选型注意**：开环增益 Gain、失调电压 Vos、共模输入电压差和绝对电压、瞬时响应速度、是否支持双向检测。推荐 **MAX49925、OPA189**。

## 开环 vs 闭环测试

### 闭环测试
- reference 设 1A，内阻 5mohm → 环路建立时 IBUS_SNSP − IBUS_SNSN 电压差 = 5mV
- 测 IBUS_SNSP − IBUS_SNSN 电压差，与 5mV 比较 → 得到环路精度

### 开环测试（无闭环设计，或闭环有环路稳定性问题时用）
- 手动 ramp IBUS_SNSP − IBUS_SNSN 电压差，观察 **Comp 点翻转**
- 有些芯片 Vcomp 可 mux 到 indicator 上测试（翻转驱动电流强）；无法 mux 则经 AMUX 观察 Vcomp 翻转 —— **类似 AWG 测试**，获取 IBUS_SNSP − IBUS_SNSN 电压差

## 总结（关键）

- 无论哪种方式，**关键测量都必须在芯片 Sense 端测差分电压**
- 保证 AWG 检测准确：AWG Ramp 的同时**实时采集差分电压** → 选高速响应差分运放是关键
