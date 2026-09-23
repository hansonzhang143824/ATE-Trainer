# 继电器规则清单（relay-agent 查 SCH-Connect-Map 据此判定连接类型）

> 使用方：relay-agent（Step 1~9 继电器闭合）、verify_relay_trace.py（功能规则溯源）、check-agent（P006/R004/FR-001）。
> 关联：`hardware/schematic-parsing.md`（列11 通路分类生成）、`hardware/bus-topology.md`（BUS 拓扑）、`hardware/relays.md`（继电器规格）、`path-principles.md`（找通路）。

## 闭环回路

```
非浮空源 (ACM, ACM200, FXVIe_PLUS):   # S3 槽为 FXVIe_PLUS(2026-08-05 起 netlist 直接标, 旧网表标 FOVIe)
  Source High ──[Connect Relay]── Pin ── DUT ── AGND ── Source Low
浮空源 (FPVI):
  Source High ──[BUS Relay]── PinA ── DUT ── PinB ──[BUS Relay]── Source Low
```

> 详细: `knowledge/hardware/bus-topology.md`

## BUS 继电器决策表

| DFT指令 | BUS | 原因 |
|---------|:---:|------|
| `iset[AxB,I]` | ✅ 必须 | 电流须闭环 |
| `vset[AxB,V]` | ✅ 实践全用 | 保证精度 |
| `vset[A,V]` / `iset[A,I]` | ❌ | 单Pin不需要 |

## Cap2 规则（默认闭 + 按 PIN 例外）

**总原则 (FR-001, 2026-08-10 重构)**: PIN **加电就需要其 Cap 稳压电容** `Kxx_<PIN>_Cap` — **默认闭**。仅两种情况**按 PIN** 移除该 PIN 的 Cap:
1. 该 PIN **被测电流** — 被测电流流经该 PIN, Cap 会吃掉/掩盖真实 Iq
2. 该 PIN 是 **ramp/扫描电压源** — Cap 拖慢/扭曲 ramp

| 该 PIN 的情况 | 该 PIN 的 Cap |
|------|:---:|
| 该 PIN 被测电流 (MIRET / ramp?_capi 电流捕获) | ❌ 移除 |
| 该 PIN 是 ramp/扫描源 (ramp?_cap? 首参 / 循环扫描) | ❌ 移除 |
| 其余 — 该 PIN 供电 / 该 PIN 测电压(MV) / FPVI浮动源 iset[AxB]+MI | ✅ 闭合 |

> ⚠ **禁止"函数里有 MI → 整函数不闭 Cap"** 的按函数豁免 (曾致 10 函数漏闭, 2026-08-10)。豁免必须逐 PIN: 只有被测电流**流经**的 PIN 才移除, 其它纯供电 PIN 仍必闭。
> 例: TM103 测 I(VDM) → VDM 无 Cap, 但 VBAT 纯供电 → 仍必闭 K13_VBAT_Cap。

**DALI Cap 家族**: K13_VBAT_Cap(VBAT) / K21_VAC_Cap(VAC) / K0_VCC_Cap(VCC) / K5_VBUS_Cap(VBUS)。

**反向检查 (FR-001 反向, 检查 E)**: PIN 被 FV 静态供电却未闭其 Cap → WARN (供电→闭)。豁免按 PIN: 仅该 PIN 自身被测电流 / 该 PIN 是 ramp 源 / 该源作 capi 电流捕获 / 下电段(FV=0 归零)。测试垫偏置 (AMUX/VDM/NTC, 对象名与闭合 Share 继电器都含测试垫 token) 非供电轨不查 Cap。由 verify_relay_trace.py 检查 E 强制。

## 反短接铁律（非目标 PIN 禁驱动）

测试时，源表→目标 PIN 的通路**禁止经过/连接其他 DUT PIN**——给 A PIN 施加信号，通路不得顺带连到 B PIN。
- **Share 二选一继电器**（如 PB5/VAC Force/Sense 组）只能闭合目标侧，禁止两侧同闭（短接两 PIN）
- 源表通道选型：优先用 SCH-Connect-Map 中**只到目标 PIN** 的通路（如 VAC1 用 `VAC123_AMUX_ACM`，不用经 Share 短接 PB5 的路径）
- 例外: 浮动源（FPVIe）等电位/电流闭环连接的两个 PIN 都算被测目标
- 检查项: check-agent **P006**；详见 `knowledge/hardware/schematic-parsing.md` §四 反短接铁律

## SCH-Connect-Map 列11 通路分类（六类，2026-08-25）

`SCH-Connect-Map.txt` 除「需闭合继电器」外新增**列11 通路分类**，每 PIN 标一类：

| 分类 | 判据 | 对 codegen 的含义 |
|------|------|------|
| **P2P-到地** | PIN ↔ AGND，ON ≤ 2 | 短路测试：目标 PIN 直通地脚，源表可经该通路测 PIN 对地 |
| **P2P-互短** | PIN ↔ PIN（两不同 base），ON ≤ 2 | **反短接铁律**数据源：非目标 PIN 禁驱动（P006/H009） |
| **上拉-固定5V** | PIN→电阻→继电器→`S34_J+5V`（只能 5V） | 开漏观测必闭该 PU 继电器，上拉电压固定 5V |
| **上拉-源表** | PIN→电阻→继电器→源表端口（range 内任意电压） | 上拉电压可程控（FV 设 range 内任意值，不限 5V） |
| **下拉** | PIN→电阻→继电器→地（AGND_F/AGND_S 等） | 该 PIN 有下拉电阻，默认态被拉地 |
| **稳压** | PIN→电容（**≥100nF**，按值判非名）→继电器 | Cap2 规则数据源：该 PIN 供电需闭其 Cap 稳压电容 |
| **net短接** | 两 net 同电气节点（CSV ELECTRICAL_SHORT_GROUP / NET_TIE_GROUP） | **只记录不合并**；F/S 短接组（如 FL↔SL）已板上短接 → 通路分叉 F/S 也不再是 Kelvin 四线 |

- **上拉/下拉按连接判，不看电阻值**；Kelvin 电阻（只连 Force↔Sense，不穿越继电器）**不进列11**（上拉/下拉的排除判据）。
- **net短接语义（用户确认 2026-08-25）**：短接组只记录事实、**不合并 net**（各自处理）；但通路分析须注意「一旦经过此节点即已短接，即使后面又分叉 force/sense 也不再是 Kelvin 四线走线」。判定优先级见 `schematic_parse/NET_SHORT_RULES.md`。
- **Rule A**（硬）：源表→PIN 通路禁穿越固定电压节点（地 0V ∪ 固定轨 5V/12V），终点合法/中间非法。**Rule B**（硬）：禁穿越其他 PIN（terminal-stop）。软规则：穿越其他源表仅 ⚠ 警告。
- 权威来源：`.csv`（Dali-SCH.csv）唯一权威（连接 + ComponentValue 电容/电阻值，2026-08-25 起无需独立 .NET）。详见 `Project/DALI/通路规则实现方案.md`。

## 11步继电器检查清单

relay-agent 闭合顺序（13 步详见 `agents/relay-agent.md`）：**先通路继电器 → 再角色继电器 → 一起 `cbite.SetOn()` 封装**。
- 第 11 步：无继电器需闭合时**显式 `cbite.SetOn(-1)`**（R004/E011）
- 第 5 步 Cap2：默认闭 + 按 PIN 例外（见上）
