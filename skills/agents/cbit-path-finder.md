---
name: cbit-path-finder
description: CBIT Phase2 — 从Netlist追踪所有DUT_PIN到稀缺源表的通路（已脚本化→gen_paths.py，规格文档）
model: sonnet
tools: Read, Grep, Glob, Bash
---

# CBIT Path Finder — Phase 2

> **已脚本化 (2026-08-09)** → **`D:\Newtest\CLAUDE_PROCESS\gen_paths.py`**（架构原则: 推理→agent, 固定→脚本）。
> 本文件降级为**规格文档**，保留规则溯源（下方四步流程 + 铁律即脚本 RULE_COVERAGE P-P1~P-P11 的来源）。
> **脚本用法**:
> ```
> python gen_paths.py --netlist Project/DALI/CSV_CONNECTIVITY.NET --cbit Project/DALI/CBIT表-DALI.xlsx [--json] [--max-depth 6]
> python gen_paths.py --audit-rules      # RULE_COVERAGE 机器自检 (P-P1~P-P11)
> ```
> **脚本已实现**: BFS 通路追踪 (trace_single, 含稀缺源表识别/非稀缺源禁借道BUS/FPVIe域约束/跨域BUS短接约束)、G6K/MOS/MOS2 脚位通断 (rtrans)、源端短接继电器排除 (K86/K130, AGND/GND例外)、FPVIe 通道分组 (FH+SH/FL+SL)、F/S 合并分类 (Kelvin/PC短接/单线)、CBIT 表 Excel 动态读 relay 类型 (80 G6K 与旧硬编码全对齐)。
> **验证状态**: --audit-rules 11 规则 PASSED；实测 146 条 FPVIe 配对通路 + 360 条 path_list JSON；relay 类型 80=80 与旧硬编码一致；max_depth/TP_*排除参数化。
> **边界 (2026-08-09 用户确认)**: 本脚本是**通路追踪工具**（BFS→path_list），覆盖 FPVIe/ACM200/FOVIe，**不生成 SCH-Connect-Map.txt**。完整 SCH-Connect-Map（10 列、多源、最短路径+F/S 同时连通）难度大、推理密集 → 归 **sch-parse agent（任务六）**，不脚本化。cbit-agent Phase 2 优先参考 sch-parse 产出的 SCH-Connect-Map，缺失时才用本脚本兜底。

## 输入

来自 Phase 1:
- `port_list`: 所有 port + direction
- `net_map`: {net_name: [(instance, pin), ...]}
- `instance_map`: {name: {type, pins[]}}
- `cbit_map`: CBIT 映射

## 定义

**稀缺源表:** FPVIe, QTMU, QVM

**路径:** 从 DUT_PIN 出发，经过 Net → 继电器引脚 → Net → ... → 稀缺源表端口，全程电气联通。

## 四步执行流程

### Step 1: 列出所有 DUT_PIN

```
DUT_PIN_list = {name | port.direction == OUTPUT}
排除非信号端口 (如 TP_*, TEST_*, Net*)
```

### Step 2: 追踪 DUT_PIN → 稀缺源表通路

**BFS 深度限制:** 从 DUT_PIN 出发到 BUS 网络，最多穿越 **4 个不同继电器**（max_depth=4），防止无限搜索。

**短路 PIN 检测（Step 2.1 增强）:**

对每个 DUT_PIN:
```
2.1 找到 DUT_PIN 连接的 Net (三步查找):

   Step A: 直接同名匹配
     if DUT_PIN 名称直接在 nets 中存在:
       sn = DUT_PIN 名称  (如 PA0_F_S1 就是 net 名)
       → port_sn[base] = sn

   Step B: 反向 relay 匹配（短路/无直接 net 场景）
     if DUT_PIN 没有同名 net (如 PA0 只有 PORT 定义):
       遍历所有 net，搜索 relay instance 名中包含 DUT_PIN 名称的连接:
         例: K101_BUS_PA0_S1 中包含 "PA0"
         → 该 relay 所在 net = PA0 的信号 net
         → port_sn[base] = 关联最多的 net
     
     适用场景:
     - PA0 端口只有 port 定义，没有直接叫 PA0 的 net
     - net 中的所有连接指向 INT (短路在一起)
     - PA0 和 INT 是同一电气节点 → 用同一个信号 net 追踪

   Step C: 都找不到 → 该 DUT_PIN 无通路，跳过追踪

2.2 从 Net 出发，BFS/DFS 遍历:
    - Net → 连接的 relay 引脚
    - relay 引脚 → 同一 relay 的其他引脚 (根据 relay 类型判断通断)
    - 其他引脚 → 连接的 Net
    - 继续直到到达 稀缺源表端口 或 遍历完所有可达节点
2.3 对于机械 G6K 继电器:

    **G6K-2G-Y 脚位:**
    - 8脚物理封装（6信号脚 pin2-7 + 2线圈脚 pin1/pin8）
    - 两组触点**同步切换**，不可独立控制
    - 默认 NC (无电): pin3↔pin2, pin6↔pin7 (两组同时)
    - SetOn NO (通电): pin3↔pin4, pin6↔pin5 (两组同时)

    **功能分类（必须根据继电器用途选择正确的追踪方式）:**

    | 功能类型 | 典型编号 | 默认 NC 通路含义 | SetOn NO 通路含义 | 追踪策略 |
    |:---:|---|---|---|---|
    | **BUS** | K15,K17,K19,K21,K26,K29,K31,K33,K34,K38,K40,K41,K42 | 3↔2/6↔7: Pin 断开 BUS | 3↔4/6↔5: Pin 连通 BUS (Force/Sense) | **只追踪 SetOn NO 路径** |
    | **Share** | K20,K22,K23,K35,K36 | 3↔2/6↔7: 通默认通道 | 3↔4/6↔5: 通备用通道 | **两条都追踪**，标注目标通道 |
    | **Cap** | K16,K18,K25,K28,K30,K32,K37,K66 | 3↔2/6↔7: Cap 断开 | 3↔4/6↔5: Cap 接入 | **只追踪 SetOn NO 路径** |
    | **FPVIe矩阵** | K8~K13 | 3↔2/6↔7: FPVI→FPVI_BUS 直通 | 3↔4/6↔5: 备用路径 | **保持默认 NC，不追踪 NO** |
    | **通用** | 其余 G6K | 取决于设计 | 取决于设计 | 两条都追踪 |

    > netlist 中的连接是**物理焊接**，不是状态说明。必须结合功能分类才能判断通路是否实际生效。

2.4 对于 SPST (MOS TLP3412) 继电器:
    - 默认: pin1-pin2 **断开** (MOS 关断)
    - SetOn: pin1-pin2 **闭合** (MOS 导通)
    - 所有 MOS P2P 继电器 (K46~K59, K68) 默认断开，需 SetOn 才通

2.5 对于 FPVIe 矩阵继电器 (K8~K13):
    - 这是特殊的机械 G6K，默认 NC 已连通 FPVI→FPVI_BUS
    - 追踪时标注 state="KeepDefault"
    - **不放入** via_relays 的 SetOn 列表（不需要 cbite.SetOn）
```

### Step 3: 路径去重与分类

对每条找到的路径:
```
3.1 提取路径上的继电器列表 (需要 SetOn 的继电器)
3.2 判断路径连到稀缺源表的哪一端:
    - FH_BUS / SH_BUS → High 侧
    - FL_BUS / SL_BUS → Low 侧
3.3 去重: 相同 relay 集合 = 同一条路径
```

### Step 3.5: Force/Sense 合并分类（新增）

**铁律：追踪时保留完整 DUT pin 名（含 `_F_Sx`/`_S_Sx` 后缀），合并阶段才按后缀交叉配对。**

```
3.5.1 提取 DUT pin 的 F/S 后缀:
      - VBUS_F_S1 → base="VBUS", suffix="F"
      - VBUS_S_S1 → base="VBUS", suffix="S"
      - nRST_S1   → base="nRST",  suffix="" (无F/S区分)

3.5.2 按 (base, suffix) 分组，交叉配对:
      
      配对优先级:
      Pass 1 — [Kelvin]: Force终点_F + Sense终点_S
        FL→VBUS_F + SL→VBUS_S → Kelvin (4线, 在DUT端汇合)
        FH→VBUS_F + SH→VBUS_S → Kelvin
        
      Pass 2 — [PC短接]: Force终点_F + Sense终点_F
        FL→VBUS_F + SL→VBUS_F → PC短接 (F/S在PC总线处已短接, 2线测量)
        FH→VBUS_F + SH→VBUS_F → PC短接
        
      Pass 3 — [单线]: 无配对对手的路径

3.5.3 配对算法:
      - 每条Force路径优先匹配重叠继电器最多的Sense路径
      - 同位置同继电器同状态 → 显示一次
      - 同位置不同继电器 → 逗号并列 (Force在前, Sense在后)
```

### Step 4: 遍历 Net → 稀缺源表

对 Netlist 中的公共节点 Net:
```
4.1 筛选: Net 连接 >3 个不同 relay/元件
4.2 追踪 Net → 稀缺源表的通路 (同 Step 2 方法)
```

## 输出格式

```
path_list:
  - {dut_pin: "SW2", source: "FPVIe", side: "High",
     via_relays: [{name: "K46_BUS_FH_SW1", cbit: 46, type: "SPST", state: "SetOn",
                   annotation: "[通电→闭合]"},
                  {name: "K49_ACM_SW2", cbit: 49, type: "G6K", state: "SetOn",
                   annotation: "[通电→NO, 3→4, 6→5]"}],
     intermediate_source: "ACM200"}
  - {dut_pin: "KLV1", source: "FPVIe", side: "High",
     via_relays: [{name: "K35_BUSH_KLV", cbit: 35, type: "G6K", state: "SetOn",
                   annotation: "[通电→NO, 3→4, 6→5]"}],
     intermediate_source: null}
  - {dut_pin: "FPVI_BUS", source: "FPVIe", side: "High",
     via_relays: [{name: "K9_FPVI_MATRIX", cbit: 9, type: "G6K", state: "KeepDefault",
                   annotation: "[默认NC, 保持]"}],
     intermediate_source: null}
  ...
```

**state 取值:**
| state | 含义 | 是否需 cbite.SetOn |
|-------|------|:---:|
| `"SetOn"` | 继电器需通电切换 | ✅ 是 |
| `"KeepDefault"` | 保持默认 NC 即可 | ❌ 否 |

**annotation 格式规范:**
| 继电器类型 | 格式 | 示例 |
|-----------|------|------|
| 机械 G6K SetOn | `[通电→NO, 3→4, 6→5]` | BUS/Cap 继电器 |
| 机械 G6K KeepDefault | `[默认NC, 保持]` | FPVIe矩阵 |
| 机械 Share SetOn | `[通电→NO, 切至<目标>]` | 通道切换 |
| MOS SPST SetOn | `[通电→闭合]` | P2P 继电器 |

## 铁律

- 只追踪电气联通路径
- 不跳继电器 (G6K 两个线圈独立评估)
- 不确定的路径 → 标记并继续
- **FPVIe 域约束**: FH 必须配对 SH，FL 必须配对 SL，禁止交叉。从 FH/SH 源追踪时禁止进入 FL_BUS/SL_BUS/FL_PC/SL_PC 网域；从 FL/SL 源追踪时禁止进入 FH_BUS/SH_BUS/FH_PC/SH_PC 网域。
- **2脚MOS (MOS2)**: max(pins)==2 的 K 器件 → pin1↔pin2 为开关触点，COIL 为空，SetOn 导通。控制端走 CBIT 通道，不在信号网表中。
- **源端短接继电器排除**: 两端网表都是 INOUT 源端口的 2 脚继电器不出现在路径中（如 K86/K130: FH↔SH 短接），除非涉及 AGND/GND。
- **Force/Sense 合并**: DUT PIN 路径目标始终使用合并名（去掉 _F/_S 后缀），不显示 (F)/(S) 标注。FH 和 SH 到同一 DUT PIN 的路径终点名相同。
