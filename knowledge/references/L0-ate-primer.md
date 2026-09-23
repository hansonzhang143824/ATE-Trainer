# ATE 通识必读（ATE 测试方法总纲）— L0 层

> **地位：L0 必读层（框架最顶层）**。每次读 ATE 测试方法（L1/L2/L3）前，**先读本文件**。
> 来源：用户 2026-09-02 定义。是理解所有测试方法里"观测脚"代称的**总纲领**。

## 本项目映射（本工程实际 Pin，2026-09-02 用户确认）

> ⚠️ **ATEST/DTEST 是代称**，具体 Pin 每项目不同；以下是**本项目**实例。

| 代称 | 本项目实际 Pin | 测什么 | 备注 |
|---|---|---|---|
| **ATEST0** | **VDM**（模拟观测脚） | 模拟电压/电流 | 高阻读电压（如 VREF、阈值）；VDM_SDA_ACM / AMUX_FOVI 类 |
| **DTEST0** | **nQON**（数字观测脚） | 数字：toggle / 时间 / 翻转 | 开漏 pad，需上拉 `K65_nQON_PU` |

> 补充：AMUX 模拟观测经 `AMUX_FOVI`（pin-resource-map）；ATEST0→VDM 为模拟观测、DTEST0→nQON 为数字观测。

## 两个核心代称（贯穿所有测试）

### 1. ATEST / AMUX —— 模拟观测（Analog muxout to Pin）

- **ATEST / AMUX 是代称**，专指 **Analog muxout to Pin**
- **具体是哪个 Pin，每个项目不同** → 须按项目解析（不能照搬其他项目的 ATEST/AMUX）
- 这些 Pin 上一般测**模拟电压或电流**（如 VREF、检测电压、阈值比较）

### 2. DTEST / DMUX —— 数字观测（Digital muxout to Pin）

- **DTEST / DMUX 是代称**，专指 **Digital muxout to Pin**
- **具体是哪个 Pin，每个项目不同** → 须按项目解析
- 这些 Pin 上一般测**数字信号**，比如**频率、时间、toggle**（翻转）

## 关键纪律

1. **代称非固定 PIN**：ATEST/AMUX、DTEST/DMUX 是"角色名"，不是某个具体引脚——**不同项目对应不同物理 PIN**（如 nFAULT 也是功能代称，见 L2 `08-nfault.md`）
2. **逻辑类型决定观测脚**：
   - 测**模拟量**（电压/电流）→ ATEST/AMUX（如 VREF、阈值电压）
   - 测**数字量**（频率/时间/toggle）→ DTEST/DMUX（如 BST_UV 翻转、ZCD toggle）
3. **先查本文件通识，再读具体方法**——否则把"某项目的 ATEST=PinX"误套到别的项目，观测脚就错了

## 与其他层的关系

- 本文件是**最高统摄**：定义"观测脚"这个贯穿概念
- L1/L2 具体模块用到的观测脚（nFAULT、DTEST0、DMUX 等）都是这两个代称的**实例**
- L3 ATE 方法设计"怎么观测"时，先确认本文件的代称 → 再按项目解析成具体 PIN
