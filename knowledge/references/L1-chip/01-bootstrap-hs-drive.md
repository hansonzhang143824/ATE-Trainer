# 模块 01：自举 & BST−SW（Bootstrap / HS 驱动）

> 用于：BST_UV（自举欠压锁定）测试、高侧 RON 测试、任何涉及 BST−SW 压差的测试项。
> 关联：`diff-pair-spec.md`（差分电压对 ATE 通用处理）、`relay-design-flow.md`。

## 1. 功能

**自举（bootstrap）** 用于驱动**高侧（High-Side）N 沟道 MOSFET/GaN**。
高侧开关完全导通需：`VGS = V(HS栅极) − V(源极SW) ≥ 5V~10V`。
当高侧导通时 SW 接近输入电压（12/24V），芯片内部逻辑电压（5V）不足以提供栅极驱动 → 需要自举电容把 BST 抬升到 V_SW + 5V。

**BST_UV（自举欠压锁定）** = 保护功能，监控 BST−SW 压差，低于阈值触发。

## 2. 硬件结构（引脚/外部元件）

- **BST / SW 引脚**：为驱动高侧开关设计的一对引脚
- **自举电容**：BST−SW 间连接，0.01~0.1µF，低 ESR（`K_xx_Cap` 类继电器）
- **充电**：低侧开关导通时 SW≈0V，内部二极管用 VCC 给电容充到 ~5V
- **抬升**：高侧需导通时低侧关断、SW 上升，BST 被自举到 V_SW+5V（电容两端电压不能突变）
- **芯片关注**：ΔV = **V(BST) − V(SW)**，非对地绝对电压

## 3. ATE 测试方法（施加/扫描/观测）

参见 `diff-pair-spec.md` 完整版，要点：
- **施加方案**：
  - 方案一（浮动源）：FPVI 跨 BST/SW 两端，ΔV=V_FPVI（两端绝对电压自由或一端被钳位）
  - 方案二（单端）：钳 SW=0V（开下管/强制低），扫 BST，ΔV=V_BST
- **选源**：差分/大电流 → 优先 FPVI/QVM（浮动差分源）；否则非稀缺源表
- **观测脚**：nFAULT 是功能代称，实际 = DTEST0 / DMUX / 各项目不同 PIN（须按项目解析）
- **扫描**：下扫捕触发（欠压）/ 上扫捕恢复（迟滞）；观测脚与 ramp 反向（升扫 TRIG_FALLING→rise / 降扫 TRIG_RISING→fall）
- **工程**：Kelvin 四线、扫描斜率适中、温度补偿、故障位回读

## 4. 派生知识（可推导的测试要求）

| 想知道/要测 | 从本模块推导 |
|---|---|
| **测高侧 RON** | 必须先让 HS 管**完全导通** → **必须 BST−SW ≥5V**（VGS 充足）→ 设计时保持 BST−SW 恒 5V，BST = SW+5V |
| **测 BST_UV** | 让 HS **关断/触发欠压** → 扫描 BST−SW **低于阈值**（如 2.5V）→ 捕获保护触发点 |
| **为什么 SW 会跟随 PMID** | HS 导通后 SW 是输出节点，VGS 足够时 SW→PMID |
| **BST 为什么比 SW 高** | 自举抬升，BST = SW + 电容电压（~5V），非固定对地 |

## 5. 易错点

- ❌ 把 BST/SW 当对地绝对电压测——**测的是压差 ΔV**
- ❌ 测 RON 时让 BST−SW 太低（<阈值）→ 管子没导通 → RON 测的是体二极管/关断态，结果错误
- ❌ 测 BST_UV 时让 BST−SW 一直 >阈值 → 永不到阈值，测不到触发点
- ✅ 区分两个场景：**RON 要导通（BST−SW≥5V）** vs **BST_UV 要触发（扫到 <阈值）**——方向相反

## 6. 实例引用

- **TM1205（BST_UV）**：BST1−SW1/BST2−SW2 差分对，FPVI0 浮动差分扫描（详见 diff-pair-spec 第五节）
- **RDSON 黄金案例**：BST−SW 恒 5V 台阶（BTST_ACM + SW_ACM 独立供电），PMID 用 FOVIe 台阶，FPVI 大电流
