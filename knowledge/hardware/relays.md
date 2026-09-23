# 继电器硬件规格

## 机械继电器 G6K-2G-Y (DPDT, 磁保持)

8 脚物理封装（6信号脚 pin2-7 + 2线圈脚 pin1/pin8），双刀双掷(DPDT)。
两个独立线圈（set/reset 脉冲控制，**不需持续供电**）。
A/B 极 **同步切换**，不可独立控制。

```
         Coil1            Coil2
       ┌──1──8──┐      ┌──────────┐
       │         │      │          │
  NO   2         4  NC  NO    7         5  NC
       │  COM1   │      │  COM2    │
       └────3────┘      └─────6────┘
```

| Pin | 名称 | 默认(无电) | 通电(set) |
|:---:|------|:---------:|:---------:|
| 1 | CP | 线圈+ | — |
| 2 | NO | **↔ COM1(3)** | 断开 |
| 3 | COM1 | ↔ NO(2) | ↔ NC(4) |
| 4 | NC | 断开 | **↔ COM1(3)** |
| 5 | NC | 断开 | **↔ COM2(6)** |
| 6 | COM2 | ↔ NO(7) | ↔ NC(5) |
| 7 | NO | **↔ COM2(6)** | 断开 |
| 8 | CN | 线圈- | — |

**记忆口诀: 默认 2-3 通、6-7 通；通电 3-4 通、6-5 通。**

> ⚠️ 磁保持继电器：标注 NO 的脚在**默认无电时闭合**，NC 脚在通电后才闭合。与普通弹簧继电器直觉相反！

## MOS 光耦继电器 (TLP3412 / TLP4320 / G3VM)

**所有光耦 SPST 继电器行为一致：默认断开，通电闭合。**

- TLP3412: 4 pin, Load 端 pin3-pin4
- TLP4320: 4 pin, Load 端 pin3-pin4
- G3VM: 4/6 pin 各种封装，原理相同

| Pin | 名称 | 默认 | 通电 |
|:---:|------|:---:|:---:|
| 1 | CTRL+ (Anode) | — | LED+ |
| 2 | CTRL- (Cathode) | — | LED- |
| 3 | LOAD1 | **断开** | ↔ LOAD2(4) |
| 4 | LOAD2 | **断开** | ↔ LOAD1(3) |

> ⚠️ 网表中看到的 SPST 继电器（如 K59_PGND_FOS, K63_KLV_FOS 等 FOS/SNS 型）都是光耦继电器，**必须 cbite.SetOn 才会导通**。

## CBIT 表分类体系（权威来源）

**CBIT 表的分组标题决定继电器的物理类型和站点分布，不可从编号范围推断。**

| CBIT 分组 | 物理类型 | 默认状态 | 站点分布 | 实例名后缀 |
|-----------|------|:---:|------|------|
| **光耦** | SW_SPST (TLP3412/G3VM) | 断开 | 每 Site 独立 | `_S1` ~ `_S8` |
| **机械独享** | G6K-2G-Y | NC | 每 Site 独立 | `_S1` ~ `_S8` |
| **机械共享** | G6K-2G-Y | NC | 2 Site 共享一个继电器 | `_S1S2`, `_S3S4`, `_S5S6`, `_S7S8` |

> **铁律：继电器类型以 CBIT 表分组标题为准，不以 K 编号范围推断。** 不同项目（NU6810 vs DALI）分组完全不同。

## 按功能分类

### 设计原因（为什么这样分类）

功能分类的本质是**继电器在复用结构中的位置**，不是编号：

| 类型 | 位置 | 解决什么问题 | 复用方式 |
|------|------|-------------|---------|
| **Share** | PIN 端 | 其他源表（ACM/ACM200/FXVIe/DCM）通道不够每个 PIN 一个 | **分时复用**：1 通道→继电器→多 PIN，切换哪个 PIN 接入，测试串行执行 |
| **BUS** | 源表端 | 稀缺源表（FPVIe/QVM/QTMU）通道极少，n 个 PIN 点对点共享 1 通道需 n-1 个机械/2n 个光耦继电器，不可扩展 | **BUS 广播**：稀缺源表分出 Force-Sense 总线，各 PIN 独立接入，可同时或选择性接入 |
| **Connect** | — | 通道与 PIN 一一对应 | 无复用 |

- **BUS + Share 组合 = 两级复用**：源表通道经 BUS 继电器接入 FPVI_BUS 后，该源表连接的所有 PIN 可再经 Share 继电器分时复用 BUS。
- **BUS 线 Kelvin 黄金准则**：FPVIe BUS 4 线（FH+SH+FL+SL）、QVM BUS 2 线（SH+SL）必须是 Kelvin 结构（F/S 分开，G6K 两 pole 分别走）；QTMU BUS 仅 1 线（FH，FL 接机台地），不分 Kelvin。

> 完整设计原理与判定条件见 `knowledge/hardware/schematic-parsing.md` §三、§六。

### 动态分类（三层判断，权威方法）

**编号硬编码不可移植** —— 下面的编号表只是当前板卡实例。换板卡必须按三层法重新分类：

| 层 | 依据 | 判断 |
|:---:|------|------|
| 1 | CBIT 表名称初判 | SHARE/SHARE2 → Share；BUSH/BUSL/VBUSL → BUS 候选；CAP → Cap 候选 |
| 2 | SCH-Connect-Map 交叉验证（定案） | "Connect Relay to Resource" 段 → Share；"Relay to FPVI_BUS" 段 → BUS；矛盾 → 人工确认 |
| 3 | Netlist 拓扑验证（兜底） | BUS：G6K 两 pole 指向同一 BUS 线（F/S 分开走）；Share：两 pole 指向不同 PIN |

⚠️ 不是所有含 "BUS" 名字的继电器都是 BUS 继电器，必须过第 2/3 层验证。

### 功能分类总表（机械 G6K 继电器）— ⚠️ 当前板卡实例（NU1201），不可移植

| 功能类型 | 典型继电器编号 | 默认 NC 行为 | SetOn NO 行为 | 何时需要 SetOn |
|:---:|---|---|---|---|
| **BUS 继电器** | K15,K17,K19,K21,K26,K29,K31,K33,K34,K38,K40,K41,K42 | pin3↔2/pin6↔7: Pin↛BUS | pin3↔4/pin6↔5: Pin↔BUS | 任何需要接 BUS 的测试 |
| **Share 继电器** | K20,K22,K23,K35,K36 | pin3↔2/pin6↔7: 通默认通道 | pin3↔4/pin6↔5: 通备用通道 | 仅当目标=备用通道 |
| **Cap 继电器** | K16,K18,K25,K28,K30,K32,K37,K66 | pin3↔2/pin6↔7: Cap 断开 | pin3↔4/pin6↔5: Cap 接入 | 任何需要 Cap 的测试 |
| **FPVIe 矩阵** | K8~K13 | pin3↔2/pin6↔7: FPVI→FPVI_BUS 直通 | pin3↔4/pin6↔5: 备用路径 | **不需要**（默认 NC 已满足） |
| **P2P 继电器** (MOS) | K46~K59, K68 | **断开** (MOS 关断) | **闭合** (MOS 导通) | 任何需要 Pin 间短接时 |

### 命名模式（非功能分类，仅命名规律）

| 类型 | 命名模式 | 作用 |
|------|------------|------|
| **BUS 继电器** | `BUSL_xxx` / `BUSH_xxx` / `BUS_FL_SL_xxx` | Pin 接入 FPVI 总线 |
| **Cap 继电器** | `xxx_Cap` / `CAP_xxx` | 电容接入 |
| **P2P 继电器** | `xxx_P2P` | Pin 间短接 |
| **Share 继电器** | `xxx_SHARE` | 通道切换 |
| **Kelvin 继电器** | `KELVINx_F/S` / `KLVINx` | Kelvin 4线测量路径 |
| **Force/Sense** | `xxx_F` / `xxx_S` | G6K 线圈编号（非功能描述） |

## 功能应用规则 (Cap/PU/P2P — 从功能角度判定闭合)

**与闭环规则是两层,不可互相替代:**
- **闭环规则**(relay-agent Step 8):回答"通不通"——源表→目标 PIN 是否有可达通路,闭合集 ⊆ 可达集
- **功能应用规则**:回答"该不该闭"——Cap/PU/P2P 附件继电器从**被测试项的功能需求**出发,确定是否要接入

附件继电器(Cap/PU/P2P)常不在 SCH-Connect-Map 的"源表→PIN 通路段"中(它们在 PIN 端附加),所以闭环可达性检查**覆盖不到它们**,必须靠功能规则单独判定。由 `verify_relay_trace.py` B/D 检查强制执行。

### Cap 稳压电容继电器 (`Kxx_<PIN>_Cap`)

**原理**: 该继电器接入的是 PIN 上的**稳压电容(容值 >200nF)**,用于稳定电压——上电时把纹波滤掉,让电压平稳。

**总原则 (FR-001)**: PIN **加电就需要其 Cap** — **默认闭**。仅两种情况**按 PIN** 移除该 PIN 的 Cap:
1. 该 PIN **被测电流** (MIRET, 或 ramp?_capi 电流捕获) — 电容会吃掉/缓冲电流, 掩盖真实 Iq
2. 该 PIN 是 **ramp/扫描电压源** — 电容拖慢/扭曲 ramp

| 该 PIN 的情况 | 该 PIN 的 Cap |
|------|:---:|
| 测该 PIN 电压 / 供电 (MV / 供电) | ✅ 闭合 |
| 测该 PIN 电流 (MI, MIRET / capi 捕获) | ❌ 移除 |
| 该 PIN 是 ramp/扫描源 | ❌ 移除 |

> ⚠ **禁止按函数豁免** ("函数里有 MI → 整函数不闭"): 只有被测电流**流经**的 PIN 才移除其 Cap, 其它纯供电 PIN 仍必闭。2026-08-10 该反模式曾致 10 函数漏闭。

**DALI 实例**: `K13_VBAT_Cap`(VBAT)、`K21_VAC_Cap`(VAC)、`K0_VCC_Cap`(VCC)、`K5_VBUS_Cap`(VBUS)。Iq 测试(TM000/001/001_2/001_3)测 I(VBAT) 电流流经 → 严禁闭合 `K13_VBAT_Cap`; 测 I(VDM)/I(VMCU)/I(VCC) 等其它 PIN 电流时 VBAT 纯供电 → 仍必闭。

> **2026-08-10 修复（两轮）**: ① 25 函数补 `K13_VBAT_Cap`(TM105~110/114~116/121/122~124/137/138/200~203/210~215), 3 函数补 `K21_VAC_Cap`(TM114/115/128); ② 修"函数级 MI 豁免"反模式: 10 函数补 `K13_VBAT_Cap`(TM103/104/117/118/125/126/132/134/204/207) + 4 函数补 `K5_VBUS_Cap`(TM114/124/127/128, VBUS_DRVH1_ACM 提取修复后暴露)。反向检查 E 已脚本化强制 (按 PIN 豁免)。

### PU 开漏上拉继电器 (`Kxx_*_PU`)

**原理**: 上拉电阻为 **Open Drain(开漏)输出** 准备——DUT 的 DTEST0/nQON 等开漏 pad 自身只能拉低,必须外接上拉才能读出高电平。**只有观测开漏输出时才需要上拉**。

**判定**:
- 观测开漏输出 (Toggle 的 ramp 监视源 / DTEST0 直读 / QTMU 测频) → **必须闭合**
- 不观测开漏输出 → 闭合冗余, 确认是否必要

**最常见场景**: **Toggle 测试**(有 `_Rise/_Fall/_Hys` 3 参数)→ 几乎必定观测开漏 → 必需上拉。

**DALI 实例**: `K65_nQON_PU`(nQON/DTEST0 上拉)。观测 DTEST0 的函数(TM105~113 阈值、TM121/127~130 Toggle、TM137/138 TSD/TDIE、TM200~215 阈值/SNK/PWM、TM300/301 OSC 测频、TM400~413 监测)全部闭合;不观测的(如 TM113 测 I(VBAT))不闭。

### P2P PIN 到地短路继电器 (`Kxx_*_P2P`)

**原理**: P2P 继电器把 **PIN 短接到地**(MOS 光耦, 默认断开, 通电闭合), 用于需要 PIN 对地短路测量的场景。

**判定**: 仅当测试项**需要 PIN 到地短路**时才接入, 否则禁止闭合。

> 当前 DALI 无 P2P 继电器, 该规则为占位。与某些项目里"Pin 间短接"的 P2P 定义不同, 以本项目网表为准。

### 校验实现

`verify_relay_trace.py`:
- **检查 B(正向)**: 闭合了 PU 但函数未观测开漏 → WARN; 测该 PIN 电流却闭合其 Cap → FAIL
- **检查 D(反向)**: 观测开漏但未闭合任何 PU → WARN(开漏无上拉读不到电平)
- **检查 E(FR-001 反向, 2026-08-10)**: 某 PIN 被 FV 静态供电(非 MI/非 ramp 扫描源/非下电段)却未闭其 Cap → WARN
  - 判定: 上电+测量段的 `.Set(FV, ...)` 提取供电 PIN (对象名取末 token, 排除 `VCC_VMCU_FXVI` 类"名字含它但驱动别的 PIN"的误判) → 前缀匹配 Cap 家族(VBAT/VAC/VCC/VBUS)
  - 排除: 测电流(MIRET / `ramp?_capi` 电流捕获第4参) / `ramp?_cap?` 扫描源(首参) / 下电段归零(截断 Step 5)

> 判定只看**去注释后的代码**(源表对象 `NQON_HG1_ACM`/`QTMU_GP`/`SDA_INT` 的出现), 注释里的方案说明/下个函数预告不会误报。

## BUS 继电器闭合规则

FPVI 浮动源或 Kelvin 测试时闭合，普通测试不闭合。详见 `knowledge/hardware/bus-topology.md`。

## FPVIe 域约束（铁律）

**FH 必须配对 SH，FL 必须配对 SL，禁止交叉。**

| 源通道 | 允许进入的 BUS 网域 | 禁止进入的 BUS 网域 |
|--------|:---:|:---:|
| FH / SH (高侧) | FH_BUS, SH_BUS, FH_PC, SH_PC | FL_BUS, SL_BUS, FL_PC, SL_PC |
| FL / SL (低侧) | FL_BUS, SL_BUS, FL_PC, SL_PC | FH_BUS, SH_BUS, FH_PC, SH_PC |

K90 (PC0_Force) 是 G6K 继电器，其 NC 路径（pin2↔3, pin7↔6）将高侧和低侧总线交叉连接。这个交叉路径仅用于 Kelvin 4 线 PC 通道测量，**不用于标准 FPVIe DUT pin 路由**。路径追踪时必须拒绝 FH→SL_BUS 或 FL→SH_BUS 的交叉路径。

## 双线圈继电器命名（_F + _S 共享 CBIT）

同一机械 G6K 的 F/S 双线圈共享一个 CBIT 通道，定义时合并：

### 合并规则

| 情况 | 后缀格式 | 示例 |
|------|:---:|------|
| KELVIN 单字母 F/S | `_FS` | `K86_KELVIN0_FS` (K86_KELVIN0_F + K86_KELVIN0_S) |
| 非KELVIN 单字母 F/S | 去掉后缀 | `K22_ACDRV1` (K22_ACDRV1_F + K22_ACDRV1_S) |
| FORCE/SENSE 全词 | `_FOS_SNS` | `K_FPVIH_TO_KLV_FOS_SNS` (FORCE_S1 + SENSE_S1) |
| 其他共享 CBIT | `name1_name2` | `K_PB0_PB1_OSC` (K147_PB0_OSC + K147_PB1_OSC) |

```c
#define K_KELVIN1_FS    130   // K130: KELVIN1_F + KELVIN1_S 双线圈
#define K_FPVIH_TO_KLV_FOS_SNS  35  // K35: FORCE + SENSE (FOS_SNS合并)
```

光耦 F/S 独立继电器即使共享 CBIT 也用 `_FS` 合并（不可独立控制）。

> **FORCE/SENSE 全词合并源自 `继电器识别规范.txt` 第107行规则（正文已并入 `cbit-principles.md`）。**
> 在 DALI 等项目中，DUT Pin 名称可能使用全词 `KLV_FORCE_S1`/`KLV_SENSE_S1` 而非单字母 `KLV_F_S1`/`KLV_S_S1`。

## GRP 宏生成方法论

**三步法，不可跳步：**

```
Step 1: 确认信号起终点（如 FPVI → PC）
Step 2: 确认路径上的所有继电器（如 FH: K87+K90, SH: K88+K91）
Step 3: 查出每个继电器的 CBIT 通道 → 组合成 GRP 宏
```

示例：
```c
// FPVI → PC, Kelvin 4线
#define KGRP_FPVI_FH_PC  87,90   // High Force: KELVIN0_SH + PC0_Force
#define KGRP_FPVI_SH_PC  88,91   // Sense High:  KELVIN0_S  + PC0_Sense
#define KGRP_FPVI_FL_PC  89,90   // Low Force:   KELVIN0_SH2 + PC0_Force
#define KGRP_FPVI_SL_PC  88,91   // Low Sense:   KELVIN0_S  + PC0_Sense
```

## Site 识别

- `_Sx` — 单 Site 独立继电器
- `_SxSx` — 机械共享，一个继电器服务 2 个 Site
- `_G1` — 全局共享继电器
- 程序中引用时去掉 Site 后缀

## CBIT 定义管理

继电器在 StdAfx.h 中的 #define 定义由 **cbit-agent** 专门管理，四模式覆盖审查/创建/验证：

| 模式 | 功能 |
|------|------|
| cbit-review-exist | 检查已有 CBIT 定义是否正确 |
| cbit-ctreate-step | 有 CBIT 表时生成 #define |
| cbit-ctreate-auto | 无 CBIT 表时从 Netlist 生成 |
| cbit-check | 组合验证（位号不重复/通路完整/命名一致） |

> 详细规则见 `knowledge/hardware/cbit-principles.md`，agent 定义见 `agents/cbit-agent.md`（权威规范正文已并入 cbit-principles.md）。
