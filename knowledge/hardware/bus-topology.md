# 闭环回路模型 + 硬件连接拓扑

---

## 一、POGO 概念

机台安装板卡后，所有板卡通道引出到 **POGO 点位**。如 `S28_ACM200_FH2` 就是一个 POGO 点。

**闭环判定:** POGO 点的 High 端和 Low 端都能连接到芯片 Pin（或与 Pin 短接的线路），中间无断路（需要的继电器必须闭合），即形成闭环。

```
S28_ACM200_FH2 → VBUS   (High端到达Pin)
S28_ACM200_FL(0~11) → AGND_F → AGND  (Low端到达地)
⇒ 闭环 ✓
```

**AGND / DGND / JGND 短接关系（设计规范，100%强制）:**
```
AGND_F_Sx ←→ AGND ←→ DGND ←→ JGND
```
- AGND_F（芯片 Force 地）与机台 AGND 短接
- DGND（DCM/QTMU Low 端）与 AGND 强制短接
- JGND（CBIT/电源 Low 端）与 DGND/AGND 强制短接
- 三地等电位，99% 原理图都是三者短路关系

---

## 二、源表闭环分类

### 2.1 模拟源（非浮动接法）— ACM200 / ACM / FOVIe / FXVIe / FXVIe_PLUS

```
FH/SH → [继电器(如有)] → [电阻(如有)] → 芯片 Pin
                                        ↓ (电流流过 DUT)
SL/FL → [继电器(如有)] → [电阻(如有)] → AGND_F → AGND
```

| 要点 | 说明 |
|------|------|
| High 端 | FH/SH 通过继电器/电阻到达芯片 Pin |
| Low 端 | SL/FL 接 AGND_F，AGND_F 与 AGND 短接 |
| 电流路径 | 源表 High → Pin → DUT → AGND → 源表 Low |
| DUT 含义 | Pin 本就是 DUT 的引脚，电流从 High 流入经 DUT 从 Low 流回 |

**所有模拟源本质都是浮动的**，只是实际使用中通常将 Low 端接 AGND_F。

### 2.2 模拟源（浮动接法）— FPVI

```
FH/SH → [BUS 继电器] → PinA → DUT → PinB → [BUS 继电器] → FL/SL
```

- 一块板卡仅 2 通道，电流能力强（10A）
- Low 端**不强制接 AGND**，偶尔通过继电器接地/接 BUS/接其他位置
- 两端都需要 BUS 继电器 → 形成浮动闭环

### 2.3 数字源 — DCM / CBIT / 电源 / QTMU

**共同特性：**

| 特性 | 说明 |
|------|------|
| **不分 Kelvin** | 从 POGO 出来就是 Non-Kelvin 结构（FH/SH 已短接） |
| **Low 端统一** | 全部短接 **DGND**，DGND 通过 POGO 输出 |
| **闭环简化** | 只需 High 端到达 Pin/节点 → 即形成闭环（Low 端自动经 DGND 回流） |

**各数字源详情：**

| 数字源 | High 端 POGO | Low 端 |
|--------|-------------|--------|
| DCM | S24_P0~P63, S9_P0~P63 | DGND |
| QTMU | QTMU_A/B High 端 | DGND |
| CBIT | S34_CBIT0~127, S36_CBIT0~127 | JGND（但 JGND↔DGND） |
| 电源 | S36_±15V/±12V/+5V, S34_±15V/±12V/+5V | JGND（但 JGND↔DGND） |

```
数字源闭环:
High 端(POGO) → [继电器] → Pin/节点
Low 端 = DGND (已固定)
⇒ High 端到达 = 闭环 ✓
```

### 2.4 浮动电压表 — QVMe

```
只有 Sense 线: SH/SL，无 Force 线
SH → PinA / 节点
SL → PinB / 节点
```

- 闭环原则与模拟源一致（条件① SH-SL 连通 + 条件② 回路）
- 区别：QVMe 不输出电流，仅测量电压

---

## 三、闭环判定与验证

> 完整理论见 `knowledge/hardware/closed-loop-model.md`

### 闭环 = 两个条件缺一不可

| 条件 | 检查内容 | 违反后果 |
|------|---------|---------|
| ① Force-Sense 连接 | FH/SH 必须连通，FL/SL 必须连通（通过继电器/电阻/PAD） | Sense 浮空，电压测量无效 |
| ② High-Low 回路 | FH/FL 电流必须能流通（通过 DUT/节点/AGND） | 电流断路，无法 force |

### 判定条件

**闭环成立:** 条件① + 条件② 同时满足。

```
条件②检查:
High 端: POGO点 → [继电器(需闭合)] → [电阻] → Pin → 到达!
Low 端:  POGO点 → [继电器(需闭合)] → [电阻] → AGND/Pin/短路线 → 到达!

条件①检查:
Force High 和 Sense High 是否在目标点连通? (Kelvin=PAD汇合 / Non-Kelvin=板上短接)
Force Low 和 Sense Low 是否在目标点连通?

两个条件都满足 → 闭环 ✓
任一条不满足   → 开环 ✗
```

### 验证方法

闭环是否正确，无法仅靠软件自动判定。需要人工验证：

> **每次检查源表 POGO 信号是否到达了与芯片 Pin 短接的线路上。**

实际操作中参考：
- SCH-Connect-Map：Pin → Resource → 继电器映射
- Netlist (`.NET`)：继电器引脚 → 网络 → 器件的物理连接
- 原理图 (A0 Agent)：追踪 POGO → 继电器 → Pin 的完整路径

> POGO 点位详情见 `knowledge/hardware/pogo.md`

---

## 四、BUS 继电器的两个用途

### 用途 1: 接入 FPVI 源表

BUS 继电器一端接 Pin，另一端接 FPVI_BUS。闭合后 Pin 的控制权从默认源表**转移给 FPVI**。

```
PMID_FOVI (默认) ──Default── PMID Pin
                              │
K31_BUS_PMID 闭合 → PMID Pin ──→ FPVI_BUS → FPVI
```

大电流场景（`iset[AxB]≥1A`）只有 FPVI 量程够，必须用 BUS。

### 用途 2: 多节点通过 BUS 短接

多个 BUS 继电器同时闭合 = 多个 Pin 接到同一条 BUS = **这几个 Pin 被短接在一起**。

```
应用场景: PinA 需要 10V, PinB 也需要 10V
  → 只操作 PinA 的源表输出 10V
  → 闭合 PinA 的 BUS 继电器 + PinB 的 BUS 继电器
  → PinB 不操作自己的源表 → 通过 BUS 从 PinA "借"到 10V
```

**风险:** 短接关系必须是 DFT 明确要求的。DFT 未要求短接 = 禁止。
```
K31(PMID) + K17(SW) + K33(PGND) 都闭合
  → PMID=SW=PGND 三端短接
  → DFT 从未要求 PMID↔PGND 短接 → 禁止!
```

---

## 五、BUS 继电器决策表

| DFT指令 | 是否需要BUS | 原因 |
|---------|:---:|------|
| `iset[AxB,I]` | ✅ 必须 | FPVI 大电流，经 PinA→DUT→PinB 闭环 |
| `vset[AxB,V]` | ✅ 实践全用 | 单源保证 PinA-PinB 精度 |
| `vset[A,V]` / `iset[A,I]` | ❌ | 单 Pin，源表 High 端直连(Default) |

### FPVI BUS 优先级

FPVI 仅 2 通道。多浮动对冲突时：

| 优先级 | 场景 | 原因 |
|:---:|------|------|
| **最高** | `iset[AxB]` 大电流 (≥1A) | 只有 FPVI 量程够 |
| **低** | `vset[AxB]` 电压差 | 两个独立源表各自供电可替代 |

> 冲突时大电流优先占 BUS，电压差让路用独立源表。

### BUS 短接风险

FPVI_BUS 连接的所有 Pin 通过 BUS 互通。**必须验证 DFT 是否明确要求这些 Pin 短接。**

```
K31(PMID→BUS) + K17(SW→BUS) + K33(PGND→BUS) = PMID-SW-PGND 三端短接
DFT 从未要求 PMID↔PGND 短接 → 禁止!
```

### 继电器热切规则

**重配 cbite.SetOn 前，被断开 Pin 和被闭合 Pin 电压必须相等。**

```
切换 K31→K33: PMID=15V vs PGND=0V → 热切拉弧 ✗
防热切: PMID→0V → 切换 → PMID 恢复 ✓
```

---

## 六、FPVI_BUS 拓扑

```
FPVI_High ──→ [K8~K13 FPVIe 矩阵] ──→ FPVI_FH_BUS / FPVI_SH_BUS
                                              │
                ┌─────────────────────────────┼─────────────────────────────┐
                │                             │                             │
          K31_BUS_PMID                   K15_BUS_SW                   K17_BUS_BST
          (通电→PMID接入)               (通电→SW接入)               (通电→BST接入)
                │                             │                             │
              PMID                           SW                           BST
```

---

## 七、Cap2 电容规则（默认闭 + 按 PIN 例外）

**总原则 (FR-001, 2026-08-10 重构): PIN 加电→闭其 Cap。仅两种情况按 PIN 移除: ①该 PIN 被测电流 (流经其 Cap) ②该 PIN 是 ramp/扫描源。禁止按函数 MI 豁免 (曾致 10 函数漏闭)。**

| 该 PIN 的情况 | 测量路径 | Cap2 |
|------|---------|:---:|
| FPVI浮动源 iset[AxB] MI | 电流走FPVI_BUS (不经过该 PIN Cap) | ✅ ON |
| 源表直接测该 PIN 电流 | 电流走源表本身, 流经该 PIN | ❌ OFF |
| 该 PIN 是 ramp/扫描源 | — | ❌ OFF |
| MV / 仅供电 | 电压测量或非测量 | ✅ ON |

**判断逻辑:**
1. 该 PIN 被测电流? → 电流走 FPVI_BUS → ON；电流走源表本身 (流经该 PIN) → OFF
2. 该 PIN 是 ramp/扫描源? → OFF
3. 其余 (供电 / MV / 仅供电) → ON

---

## 八、合并规则

### 基本铁律

**闭环回路不同 = 绝不合并。** Pin完全相同 + 继电器完全相同 = 才能合并。

### HS/LS 禁止合并

同一 Function 内含 HS FET 对 + LS FET 对 → **禁止合并，拆分独立函数。**

| 原因 | 说明 |
|------|------|
| BUS 不同 | HS: K31+K17, LS: K17+K33 |
| FET 互斥 | HS: 0x59=0x01, LS: 0x59=0x02 |
| 热切风险 | 切换需先归零再切继电器 |
| 电压冲突 | HS: PMID=15V, LS: PMID=9V |

---

## 九、E006 反偏防护 (PMID-FET-SW 耦合)

### 问题

HS FET 导通后 SW=PMID。若 BST < PMID → BST-SW < 0 → bootstrap 电容反偏 → 烧片。

### 约束

- 上电: BST 领先 PMID ≥ 5V 同步台阶 ramp
- 下电: BST 领先 PMID ≥ 5V 同步台阶下降（保持 FET 导通）
- 关 FET 下电 → SW 浮空 → BST-SW 不可控 → **错误**

### 快速检查

`vset[bst2sw]` + `iset[pmid2sw]` 同时存在:
- [ ] BST/PMID 同步台阶 ramp?
- [ ] 上电 BST 始终领先 PMID ≥ 5V?
- [ ] 下电保持 FET 导通?
