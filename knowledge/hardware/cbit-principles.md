# CBIT 通用原理

> **权威规范:** 本文档正文（源出 `继电器识别规范.txt`，正文已并入本文件 + `relays.md`）
> **Agent:** `agents/cbit-agent.md`（四模式 CBIT 管理）
> **项目映射:** `knowledge/hardware/cbit-mapping.md`（NU1201 等具体项目）

---

## 一、CBIT 常量体系

### Slot 与位号映射

| CBIT 通道 | 程序常量 | 范围 |
|-----------|---------|------|
| `S34_CBITn` | `n` | 0 ~ 127 |
| `S36_CBITn` | `n + 128` | 128 ~ 255 |
| **总计** | **0 ~ 255** | 256 个 |

### StdAfx.h 识别规则

所有 `#define` 中数值在 0~255 之间的常量即为继电器定义。例：
```cpp
#define K_PGND2AGND  0,1    // CBIT 0,1 → S34_CBIT0 + S34_CBIT1
#define K_VBAT_Cap    2      // CBIT 2   → S34_CBIT2
```

---

## 二、CBIT 表与原理图对应

| 源 | 格式 | 示例 |
|----|------|------|
| **CBIT 表** | `K<编号>` | `K1`, `K11_F`, `K93_GAIN1_SEL` |
| **Netlist** | `K<编号>_<功能>_<站点>` | `K1_PGND2AGND_S1`, `K2_VBAT_Cap_G1` |
| **StdAfx.h** | `K_<功能>` | `K_PGND2AGND`, `K_VBAT_Cap` |

**K 编号匹配规则:** CBIT 表第一列 `Kx` 与原理图中 `Kx_xxx` 等价，`Kx_` 前缀相同即为同一继电器。

---

## 三、多站点与 CBIT 位号

CBIT 表后面各列如果包含多个 CBIT 通道，说明多个工位需要同时操作：
- K1 用到 `S34_CBIT0` + `S34_CBIT1` → 两个继电器
- 定义：`#define K1 0,1`

---

## 四、通路继电器命名与执行流程

FPVI、QTMU、QVM 以下简称 **稀缺源表**。

### 三种通路类型

| 类型 | 源 | 目的地 | 格式 | 检查 |
|------|-----|--------|------|------|
| 类型1 | 稀缺源表 | 公共节点(>3器件) | `K_<源>_TO_<Net>` | Net满足公共节点定义 |
| 类型2 | 稀缺源表 | DUT Pin | `K_<源>_TO_<PIN>` | port=OUTPUT |
| 类型3 | 其他模拟源 | DUT Pin | `K_<PIN>_<源>` | — |

### 类型1/2 执行流程（4步）

1. **Step 1:** 从 Netlist port 找所有 OUTPUT 端口 → DUT_PIN 列表
2. **Step 2:** 对每个 DUT_PIN，追踪到稀缺源表的通路。每条不同路径 = 一个通路继电器
3. **Step 3:** 无通路 → 不定义
4. **Step 4:** 同样方式遍历 Net → 稀缺源表

### 多路径命名优先级

同一 DUT_PIN 到同一稀缺源表有多条路径时：

| 优先级 | 区分依据 | 命名格式 | 示例 |
|:---:|------|------|------|
| 1 | High/Low 端不同 | `K_<源>H_TO_xxx` / `K_<源>L_TO_xxx` | `K_FPVIH_TO_SW2` / `K_FPVIL_TO_SW2` |
| 2 | 经过其他源表不同 | `K_<源>_TO_xxx_<途经源>` | `K_FPVI_TO_SW2_ACM` / `K_FPVI_TO_SW2_FOVI` |
| 3 | 完全相同 | `K_<源>_TO_xxx_A/B/C` | `K_FPVI_TO_SW2_A` |

### 功能后缀

| 后缀 | 含义 |
|------|------|
| `_F` / `_S` | G6K 双线圈 Coil1/Coil2（不表示 Force/Sense 功能） |
| `_FS` | 同一 G6K 的 F+S 双线圈合并（单字母后缀） |
| `_FOS_SNS` | 同一 G6K 的 FORCE+SENSE 双线圈合并（全词后缀） |
| `_TO_` | 起点→终点的完整路径 |
| `_PU` | Pull-Up 上拉 |
| `_Cap` | 电容连接 |

### FOS_SNS 合并规则

当两个继电器的 DUT Pin 名称使用全词 `FORCE`/`SENSE` 后缀且共享同一 CBIT 通道时，合并为 `_FOS_SNS`：

```
K_FPVIH_TO_KLV_FORCE_S1 + K_FPVIH_TO_KLV_SENSE_S1  (共享 CBIT 35)
  → K_FPVIH_TO_KLV_FOS_SNS  // FORCE + SENSE → FOS_SNS
```

判断条件：
1. 两个路径共享完全相同的 via_relays CBIT 集合
2. DUT Pin 名称去除站点后缀后，一个以 `_FORCE` 结尾，另一个以 `_SENSE` 结尾
3. 合并后的基础名 = 去除 `_FORCE_*`/`_SENSE_*` 的公共前缀 + `_FOS_SNS`

> 此规则源自 `继电器识别规范.txt` 第107行：
> "如果是FROCE、SENSE，就加尾缀FOS_SNS"

与单字母 `_F/_S` 的区别：
- 单字母: `KLV_F_S1` + `KLV_S_S1` → `KLV`（去掉后缀）
- 全词: `KLV_FORCE_S1` + `KLV_SENSE_S1` → `KLV_FOS_SNS`（保留标记）

### 站点后缀（定义时扣除）

| 后缀 | 含义 | StdAfx.h 处理 |
|------|------|-------------|
| `_Sx` | 单工位独占 | **扣除**（如 `_S1` → 删除） |
| `_Sx_Sy` / `_SxSy` | 机械共享 | **扣除** |
| `_G1` | 全局共享 | 可保留可省略 |

### Kelvin vs Non-Kelvin Pin 识别

DUT Pin 端口名中的 `_F`/`_S` 后缀用于区分 **Kelvin** 和 **Non-Kelvin** 引脚：

| Pin 类型 | 端口名模式 | 示例 | 特征 |
|:---:|------|------|------|
| **Non-Kelvin** | `PIN_F_Sx` + `PIN_S_Sx` 成对 | `PB5_F_S1` + `PB5_S_S1` | Force 和 Sense 分开走线，共享 CBIT，需合并 |
| **Non-Kelvin (全词)** | `PIN_FORCE_Sx` + `PIN_SENSE_Sx` 成对 | `KLV_FORCE_S1` + `KLV_SENSE_S1` | 同上，仅后缀命名风格不同 |
| **Digital / 单信号** | `PIN_Sx`（无 F/S） | `nRST_S1` | 无 Force/Sense 区分，`_S1` 仅为工位号 |

**norm() 剥离顺序：**

```
nRST_S1
  → strip _FORCE_S\d+  (miss)
  → strip _SENSE_S\d+  (miss)
  → strip _[FS]_S\d+   (miss, 无F/S前缀)
  → strip _S\d+        (match!) → nRST  ✓

PB5_F_S1
  → strip _FORCE_S\d+  (miss)
  → strip _SENSE_S\d+  (miss)
  → strip _[FS]_S\d+   (match!) → PB5  ✓
```

> **铁律：`_Sx` 永远是站点后缀，最终一定会被剥离。** 无论前面有没有 F/S/FORCE/SENSE。

---

## 五、通路继电器判定（三类必须定义）

### 类别 A: DUT PIN ↔ 源表 POGO
**必须定义。** 涉及的源表：ACM200, ACM, FOVIe, FXVIe, FXVIe_PLUS, FPVIe, QTMU, QVM

### 类别 B: FPVIe/QTMU/QVMe ↔ 公共节点
**必须定义。** 公共节点判定条件：**单个节点同时被超过 3 个不同的继电器或元器件短接。**

> 不是所有 BUSH/BUSL 另一端都是公共节点，必须逐个验证。

### 类别 C: DUT PIN ↔ 电容/电阻
**必须定义。** 如 VCC→Cap2_VCC，继电器名改为 `K_VCC_Cap`。

---

## 六、继电器通路原则

### 原则 1: 连通性
起点到终点信号路径必须联通。方式：线短接、继电器、POGO-net。

### 原则 2: Kelvin 双线
Force 和 Sense 都需要满足原则 1。

### 原则 3: 反命名推断（禁止）
`_F`/`_S` 只表示 G6K 线圈编号，**不表示该继电器是 Force/Sense 切换器**。必须从原理图追踪实际连接节点。

### 短路合并
Force 和 Sense 如已短接（线/继电器/<100Ω电阻），可合并评估。

---

## 七、路径分解方法

```
Step 1: 确认起始点 — K_ 后第一部分
Step 2: 确认终点   — K_ 后第二部分
Step 3: 利用通路原则，找出路径上经过的所有继电器
```

示例：
| 继电器名 | 起点 | 终点 |
|---------|------|------|
| `K_FPVI_TO_IBATP` | FPVI POGO | IBATP Pin |
| `K_IBATP_ACM` | IBATP Pin | ACM200 POGO |
| `K_VBAT_Cap` | VBAT 节点 | VBAT 连接的 Cap |
| `K_BST_SW_Cap` | BST 节点 | SW 节点（两者间的 Cap） |

---

## 八、组合定义规则

1. **合并:** `#define K1 0,1` + `#define K2 2,3` → `#define KMEGER 0,1,2,3`
2. **可读命名:** `K_KLV1_ACM` = K12_KLV1_F + K12_KLV1_S（闭合后 KLV1→ACM200）
3. **GRP 总线:** `KGRP_FPVI_TO_HG2` 含 FPVI→FPVI_BUS→HG2 全部继电器
4. **上拉类:** `K_SDA_PU` = SDA 上拉；`K40_NTC_BUF` = NTC→Buffer
