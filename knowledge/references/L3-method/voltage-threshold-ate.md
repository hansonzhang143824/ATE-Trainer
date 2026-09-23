# 阈值电压测试 ATE 通用方法（voltage-threshold-ate）

- 来源：用户提供（阈值电压类 + VTRICKLE/RECHG）。
- **L3 通用方法**：应用于电压阈值测试项（Pin+PRST/UVLO/OVP/LOW + VBAT+TRICKLE/RECHG）。
- 前置：观测脚代称见 `ATE-primer.md`（DTEST0→nQON）。

---

# 方法 A：阈值电压类通用（Pin+PRST/UVLO/OVP/LOW）

> 应用于 `Pin+PRST/UVLO/OVP/LOW` 结构。代表项目：VAC1_PRST、VBUS_UVLO、VBAT_OVP、VBAT_LOW。

## 命名规则

| 后缀 | 含义 | 代表项目 |
|---|---|---|
| **PRST** | Power-on Reset | VAC1_PRST |
| **UVLO** | 欠压锁定 | VBUS_UVLO |
| **OVP** | 过压保护 | VBAT_OVP |
| **LOW** | 低压（低阈） | VBAT_LOW |

命名：`Pin + 后缀 + _Rising/_Falling/_Hys`。

## ATE 测试方法（统一，测 DTEST 翻转）

1. **Rising 阈值**：Pin 从**低到高** Ramp → 观测 **DTEST toggle**，电压**从高到低跳变** → **Trigger Falling edge**
   - 定义：`Pin_UVLO/PRST/OVP/LOW_Rising`
2. **Falling 阈值**：Pin 从**高到低** Ramp → 观测 **DTEST toggle**，电压**从低到高跳变** → **Trigger Rising edge**
   - 定义：`Pin_UVLO/PRST/OVP/LOW_Falling`
3. **迟滞**：`Pin_XXX_Hys = (Rising − Falling) × 1e3`（mV，**乘 1000**）

**实测逻辑**：观测脚 = DTEST0(nQON)；Rising/Falling 命名以**触发边沿**为准（升扫 TRIG_FALLING 捕 rise / 降扫 TRIG_RISING 捕 fall），与 diff-pair-spec 的"观测脚与 ramp 反向"一致。

**涉及文件**：L4 黄金案例 `references/L4-Golden-code/UVLO.cpp`（PRST 阈值）、`OVP.cpp`（VBAT OVP）、`toggle-template.cpp`；参数 `_Rising/_Falling/_Hys`（E005 门禁）。

---

# 方法 B：VTRICKLE / RECHG（VBAT+TRICKLE/RECHG）

> `VBAT + TRICKLE/RECHG` 结构。代表项目：VBAT_TRICKLE、VBAT_RECHG。

| 后缀 | 含义 | 代表项目 |
|---|---|---|
| **TRICKLE** | 涓流充电电压阈值 | VBAT_TRICKLE |
| **RECHG** | 重新充电阈值（比 VBAT 高多少 mV 触发重充） | VBAT_RECHG |

## ATE 测试方法

1. **Rising**：VBAT 从**低到高** Ramp → DTEST 高→低 → TRIG Falling edge → `VBAT_TRICKLE/RECHG_Rising`
2. **Falling**：VBAT 从**高到低** Ramp → DTEST 低→高 → TRIG Rising edge → `VBAT_TRICKLE/RECHG_Falling`
3. **迟滞**（⚠️ TRICKLE 与 RECHG 公式不同）：

   **TRICKLE**（同一般阈值）：`VBAT_TRICKLE_Hys = (Rising − Falling) × 1e3`（mV）

   **RECHG**（**不 ×1e3**）：
   ```
   VBAT_RECHG     = (VBAT_RECHG − VBAT) × 1e3    // 相对 VBAT 的 mV 偏移
   VBAT_RECHG_Hys = Rising − Falling              // 不×1e3：Rising/Falling已换算为mV, 相减即mV
   ```

## 关键差异（RECHG 特殊）

- RECHG 阈值本身是**相对 VBAT 的 mV 偏移**（`×1e3` 已含）
- RECHG_Hys **不 ×1e3**：Rising/Falling 已换算为 mV 规格，相减即 mV
- 与一般阈值（Rising/Falling 是绝对电压 V，相减 ×1e3 才得 mV）**不同**
