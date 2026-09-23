# 会话 #6 — 你在探索 D:\\Newtest\\CLAUDE_PROCESS 项目，目标是收集 **上电(power-on) 和 下电(power-off) 的全部确定性规则*

- 文件：`agent-a600621296415fbd4.jsonl`（项目 subagents）
- 时间：2026-08-09T10:34:01.498Z → 2026-08-09T10:35:35.571Z，大小 0.2 MB
- 用户消息 1 条 / 助手文本 6 段 / 工具调用标记 22 行

---

## 对话正文（工具输出已剥离）

### 2026-08-09 10:34:01 [user]

你在探索 D:\Newtest\CLAUDE_PROCESS 项目，目标是收集 **上电(power-on) 和 下电(power-off) 的全部确定性规则**，为把它们从 agent 转成 python 脚本做准备（脚本必须覆盖 agent follow 的所有规则）。

请读取以下文件并提取所有**可脚本化的确定性规则**（决策表/铁律/固定模板），分类整理：

1. `D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-off-agent.md` — 下电规则全文（三步下电、RELAY_OFF 统一量程等）
2. `D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-on-agent.md` — 上电规则（我已读过，重点确认浮动源三阶段、大电流、量程选择的细节）
3. `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-power-rules.md` — 上下电规则记忆
4. `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-range-rules.md` — 量程选择规则（量程≥2×设定值决策表）
5. `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-floating-source.md` — 浮动源规则（iset/vset指令解析、FPVI_BUS继电器）
6. `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-high-current.md` — 大电流测试规则（≥200mA用FPVIe）
7. `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\hardware\pin-resource-map.md` — Pin→Resource 映射（如果存在）
8. 搜索 `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\sources\` 下的量程表文件（acm200.md, fovie.md, fpvie.md 等），提取每种源表的量程选择规则和 Set() 签名格式

输出要求（用中文）：
- **每条规则编号**（R-PON-01, R-POFF-01 等），注明来源文件
- 规则内容 = 条件 + 动作（决策表形式，方便写脚本 if/else 或查表）
- 特别注意：PowerState JSON 的字段结构、浮动源三阶段序列、大电流 SetClamp 用法、下电三步的先后顺序与量程规格
- 最后给出"哪些规则是纯确定性可脚本化的，哪些仍需 agent 推理（如依赖原理图语义）"的判断

不要修改任何文件，只读取和汇报。

### 2026-08-09 10:34:04 [assistant]

我将并行读取所有指定的文件，并搜索量程表文件。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Glob
- [tool] Glob

### 2026-08-09 10:34:09 [assistant]

继续读取量程表文件和 Pin 映射文件。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:34:14 [assistant]

补充读取被 agent 引用的"台阶规则"标准文件和继电器文件，以完整覆盖规则。
- [tool] Glob
- [tool] Glob

### 2026-08-09 10:34:16 [assistant]

读取台阶规则标准、继电器文件和测试策略，以完整覆盖被引用的规则。
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:34:21 [assistant]

补充读取 bus-topology.md（FPVI_BUS 继电器闭合规则）和 voltage-inference.md，确认是否含确定性上电规则。
- [tool] Read
- [tool] Read

### 2026-08-09 10:35:35 [assistant]

已完成全部指定文件的读取（外加 agent 引用的 `units.md`、`relays.md`、`bus-topology.md`、`test-strategy.md`、`voltage-inference.md` 作为交叉验证）。以下是完整规则汇总。

---

# 上电/下电确定性规则提取报告

## 0. 规则编号与来源对照

| 前缀 | 主题 | 主要来源 |
|---|---|---|
| R-PON- | 上电 | `power-on-agent.md` + `nuvolta-floating-source.md` + `nuvolta-high-current.md` |
| R-POFF- | 下电 | `power-off-agent.md` + `nuvolta-power-rules.md` |
| R-FLT- | 浮动源判定 | `nuvolta-floating-source.md` |
| R-RNG- | 量程选择 | `nuvolta-range-rules.md` + `units.md` + 源表文件 |
| R-SRC- | 源表量程查表 | `sources/acm200.md`、`fovie.md`、`fpvie.md` |
| R-REL- | 继电器/BUS | `pin-resource-map.md` + `bus-topology.md` + `relays.md` |
| R-ST- | 台阶/时序 | `units.md` + `voltage-inference.md` |

---

## 一、上电规则（Power-On）

### R-PON-01 指令 → 模式映射
来源：`power-on-agent.md` Step 2、`units.md`、`nuvolta-power-rules.md`
| 条件 | 动作 |
|---|---|
| `vset[...]` | mode = `FV` |
| `iset[...]` | mode = `FI` |
| 测量 MV 且无 FI 配置 | `FI=0`，电流量程选最小档 `10UA` |
| 模式参数 `1e-3`（仅 Toggle 用 ramp；MI/MV/Trim 用静态 FI/FV） | 不自动等于 AWG-ramp |

### R-PON-02 浮动源识别（决定性，`[]` 内含 `2`）
来源：`nuvolta-floating-source.md`
| 指令 | 判定 | 动作 |
|---|---|---|
| `iset[PinA2PinB, I]` | 浮动电流源 | 用 FPVI，闭合 FPVI_BUS 继电器 |
| `vset[PinA2PinB, V]` | 浮动电压源 | 台阶式上电/下电 |
| `iset[PinName, I]` | 非浮动 | 不用 FPVI |
| `vset[PinName, V]` | 非浮动 | 普通上电 |

### R-PON-03 量程选择（≥2×设定值）
来源：`nuvolta-range-rules.md`、`units.md`、各源表文件
- 规则：**量程 ≥ 2×设定值**，选最接近的最小档（推荐 force 占量程 ~50%）
- force/测量值 **不得超过量程 90%**，除非已到该源表最大量程
- 大电流（≥1A）量程持续时间尽量短：`FV=0` 阶段用小量程，FI force 前再切大量程
- 详细查表见第五节 R-SRC-01~03。

### R-PON-04 普通上电（无浮动源）
来源：`power-on-agent.md` 4a、`nuvolta-power-rules.md`
- 逐条 hardwareInit 生成：
```cpp
<Resource>.Set(FV, value, vRange, iRange, <TYPE>_RELAY_ON);
```
- 多 Pin 上电：每个 Pin 独立执行。

### R-PON-05 浮动电压源上电三阶段（E006 防反偏核心）
来源：`power-on-agent.md` 4b、`nuvolta-floating-source.md`、`units.md`
| 阶段 | 动作 | 量程/等待 |
|---|---|---|
| 1 | PinB 先设基准电压 | 例 `SW_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, RELAY_ON)` |
| 2 | FPVI `FV=0` 强制等电位（PinA=PinB） | `FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON)` + `delay_us(200)` |
| 3 | PinA 升至最终值（PinA−PinB ≤ 5V） | 例 `BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, RELAY_ON)` + `delay_us(200)` |

铁律：每步 `|PinA-PinB| ≤ 5V`，每步后 `delay_us(200)`，FPVI FV=0 等电位**不可省略**。

### R-PON-06 vset[A2B]+FET 导通台阶 ramp（防反偏 E006 子集）
来源：`nuvolta-floating-source.md`
场景：`vset[A2B,V]` 的 B 端与 `iset` 共享，寄存器操作使 B 端跳变（FET 导通 B≈C）。
| 步骤 | 动作 |
|---|---|
| 1 | `FPVI.Set(FV, 0, FPVIe_1V, ...)` 稳住 B 端 = 0V |
| 2 | A 与 C 同步台阶 ramp，**A 始终领先 C 恰好 V**（台阶 0~n 直至 C 到目标） |
| 3 | 寄存器配置（FET 导通）→ B→C_final |
| 4 | 导通瞬间 A−B = V ✓ |

反例（会烧）：PMID=15V、BST=5V → 导通后 BST−SW=−10V ❌。
典型：TM600 `vset[bst2sw,5]` + `iset[pmid2sw,1A]` + HS FET(`0x59=0x01`) → BST 领先 PMID 5V ramp。

### R-PON-07 大电流上电（阈值见 R-RNG-04）
来源：`power-on-agent.md` 4c、`nuvolta-high-current.md`、`fpvie.md`
初始化三段式（顺序**不可颠倒**）：
```cpp
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 1. FV=0
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 2. FI=0
FPVI.SetClamp(25, 25);                                  // 3. SetClamp(FI模式切换后)
```
测量流程（measure 内）：
```cpp
FPVI.Set(FI, target, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
delay_us(2000);                              // 稳定 ≥1~5ms，推荐2ms
源表.MeasureVI(200, 5);
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 立即关断，再读数据
```
注意：`SetClamp(25, 25)` = 电压钳位 25V、电流钳位 25A，仅 FPVI 有。

### R-PON-08 PowerState JSON 结构（字段必须全含）
来源：`power-on-agent.md` Step 5
```json
{
  "sources": [
    { "name": "VBAT_ACM", "mode": "FV", "finalValue": 4.2, "vRange": "ACM200_10V", "iRange": "ACM200_100MA" }
  ],
  "floatingPairs": [],
  "upSequence": [
    { "step": 1, "source": "VBAT_ACM", "mode": "FV", "value": 4.2, "note": "VBAT上电", "delay": 0 }
  ],
  "finalVoltages": { "VBAT": 4.2 }
}
```
4 个必备字段：`sources[]`、`floatingPairs[]`、`upSequence[]`、`finalVoltages{}`。
- `floatingPairs[]` 非空 + `type="vset"` → 下电类型判定为"浮动电压源下电"（R-POFF-02）
- `finalVoltages` 是 Pin 名（如 `VBAT`），非 Resource 名。

---

## 二、下电规则（Power-Off）

### R-POFF-01 下电类型判定（下电 Agent Step 1）
来源：`power-off-agent.md`
| 条件 | 下电类型 |
|---|---|
| `floatingPairs` 非空 + `type="vset"` | 浮动电压源下电 |
| FI ≥ 1A | 大电流下电 |
| 其他 | 普通下电 |

### R-POFF-02 普通下电（三步走，不可跳步）
来源：`power-off-agent.md` Step 2a、`nuvolta-power-rules.md`
| 步骤 | 动作 |
|---|---|
| 1 | 对每个源 `.Set(FV, 0, 原vRange, 原iRange, RELAY_ON)`（保持上电量程/大挡） |
| 2 | `delay_ms(1)` |
| 3 | `.Set(FV, 0, 10V档, 10MA档, RELAY_OFF)`（统一小挡） |

铁律：每源表下电都必须三步：FV=0(大挡) → delay → 小挡 RELAY_OFF。跳步 → 电压 spike 损坏芯片/源表。

### R-POFF-03 RELAY_OFF 统一量程
来源：`nuvolta-power-rules.md`、`power-off-agent.md`、`nuvolta-high-current.md` #14
| 源表 | RELAY_OFF 电压量程 | RELAY_OFF 电流量程 |
|---|---|---|
| ACM200 | `ACM200_10V` | `ACM200_10MA` |
| FOVIe | `FOVIe_10V` | `FOVIe_10MA` |
| FPVI | `FPVIe_1V` | **不一致：`FPVIe_10MA` vs `FPVIe_10A`（见第九节）** |

### R-POFF-04 浮动电压源下电（反转 upSequence，台阶式）
来源：`power-off-agent.md` Step 2b、`nuvolta-power-rules.md`、`units.md`
| 步骤 | 动作 | 等待 |
|---|---|---|
| 1 | PinA 降到与 PinB 齐平（压差→0） | `delay_us(200)` |
| 2 | PinB 归零（或下一步目标） | `delay_us(200)` |
| 3 | 其他源归零 | `delay_us(200)` |
| 4 | PinA 归零 | — |
| 5 | `delay_ms(1)` → 所有源 RELAY_OFF（统一 10V/10MA） | — |
| 6 | **FPVI 最后 RELAY_OFF** | — |

核心约束：**反转 upSequence**；PinA 先降 → PinB 再降 → 其他 → PinA 归零；每步 `|PinA-PinB| ≤ 5V` + `delay_us(200)`。
（power-off-agent 示例中 PinA=BTST 用 `ACM200_40V` 保持原量程归零，其余源用 `ACM200_10V`。）

### R-POFF-05 大电流下电
来源：`power-off-agent.md` Step 2c、`fpvie.md`
```cpp
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 1. FI=0
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);  // 2. FV=0
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_OFF); // 3. RELAY_OFF
```

### R-POFF-06 下电铁律汇总
来源：`power-off-agent.md`、`nuvolta-high-current.md` #14、`fpvie.md`
1. **必须从 PowerState 读取最终状态**（下电起点 = 上电终点），不得凭空编造。
2. 浮动下电顺序：PinA 先降 → PinB → 其他 → PinA 归零。
3. 每步 |PinA−PinB| ≤ 5V + delay_us(200)。
4. **FPVI 永远是最后一个 RELAY_OFF 的源**。
5. 大电流下电：FI=0 → FV=0 → OFF。
6. 测量后归零用 **FV=0**（比 FI=0 更安全，主动钳位差分电压为 0），数据在 FI=0 后读取。

---

## 三、浮动源规则（Power-Float）

### R-FLT-01 浮动源定义表
来源：`nuvolta-floating-source.md`
| 源表 | Low 端 | 浮动？ |
|---|---|---|
| FPVIe | 不强制接 AGND，可接任意 Pin/节点 | ✅ |
| ACM200 / FOVIe / ACM / FXVIe 等 | FL→AGND_F, SL→AGND_S | ❌ |
| QVMe | 自身闭环 | ✅ |

### R-FLT-02 FPVI 等电位规则
来源：`fpvie.md`、`power-on-agent.md`
- 浮动电压源上下电必须：`FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON)`
- 作用：强制 PinA=PinB，为台阶式上下电建立基础。
- FPVI 永远是最后一个 RELAY_OFF。

### R-FLT-03 FPVI_BUS 继电器闭合（BUS 决策表）
来源：`bus-topology.md` §五
| DFT 指令 | 需要 BUS？ | 原因 |
|---|---|---|
| `iset[AxB,I]` | ✅ 必须 | FPVI 大电流，经 PinA→DUT→PinB 闭环 |
| `vset[AxB,V]` | ✅ 实践全用 | 单源保证 PinA−PinB 精度 |
| `vset[A]` / `iset[A]` | ❌ | 单 Pin，源表 High 端直连(Default) |

BUS 优先级：`iset[AxB] ≥1A` 最高，`vset[AxB]` 电压差低（可用两个独立源替代）。

### R-FLT-04 Cap 继电器闭合（Cap2 三档规则）
来源：`bus-topology.md` §七、`relays.md`
| 场景 | 测量路径 | Cap2 |
|---|---|---|
| FPVI 浮动源 iset[AxB] MI | 电流走 FPVI_BUS | ✅ ON |
| 源表直接 MI | 电流走源表本身 | ❌ OFF |
| MV / 仅供电 | 电压测量或非测量 | ✅ ON |

（例：`iset[pmid2sw,1A]` → PMID_Cap 可加；`VBAT_ACM 直接 MI 测 IQ` → VBAT_Cap 不应加。）

### R-FLT-05 E010 浮动源 Sense 通路强制规则
来源：`nuvolta-high-current.md` #15、`test-strategy.md` §二、`relays.md`
- 浮动源 force 电流/差分电压时，**SH/SL 到测量点的 Sense 通路所有继电器必须闭合**。
- 不闭合 → FPVI 退化为 2-wire（短接 FH/SH、FL/SL），精度从 0.1mV 级退化到 mV 级。
- 各 HIB 继电器名不同，**需从原理图追踪**（判定见第九节"需推理"）。

---

## 四、量程选择决策表

### R-RNG-01 快速决策表（memory 版）
来源：`nuvolta-range-rules.md`
| 设定值 | 2 倍 | 选量程 | 备注 |
|---|---|---|---|
| FI=0（测电压） | — | 10UA | 最小档，提高精度 |
| FI=10μA | 20μA | 100UA | — |
| FI=1mA | 2mA | 10MA | — |
| FI=30mA | 60mA | 100MA | — |
| FI=0.5A | 1A | FPVIe_1A | — |
| FI=1A | 2A | FPVIe_2A | — |
| FI=3A | 6A | FPVIe_10A | — |
| FV=5V | 10V | 10V | 等于 10V |
| FV=9V | 18V | 20V 或 40V | 大于 18V 的最小档 |
| FV=0（测电流） | — | 10V | 正常量程 |

### R-RNG-02 电阻单位选择
来源：`nuvolta-range-rules.md`、`units.md`
| 测量电流 | 输出单位 | 公式 |
|---|---|---|
| >100mA | mΩ | V/I×1000 |
| ≤100mA | Ω | V/I×1 |

单位：程序中电压值 = **V**，电流值 = **A**。

### R-RNG-03 大电流阈值（注意歧义）
| 来源 | 阈值 |
|---|---|
| `nuvolta-high-current.md` | ≥200mA = 大电流，**必须用 FPVIe** |
| `power-on-agent.md` Step 1 / 4c | iset[AxB] **≥ 1A** 才走"大电流上电"模板 |
| `bus-topology.md` | `iset[AxB] ≥1A` 用 BUS |

脚本应统一为：`I ≥ 200mA` 强制 FPVIe；`I ≥ 1A` 触发"大电流三段式 + BUS"。两个阈值都要有，只是触发点不同。

---

## 五、源表量程查表（Set 签名 + 量程表）

**Set 函数签名（统一，三种源表相同）：**
```cpp
<ResourceName>.Set(mode, value, vRange, iRange, RELAY);
```
RELAY 常量：`ACM200_RELAY_ON/OFF`、`FOVIe_RELAY_ON/OFF`、`FPVI_RELAY_ON/OFF`。
MeasureVI：`<Resource>.MeasureVI(sampleCount, discardCount)`；GetMeasResult：`<Resource>.GetMeasResult(site, MIRET|MVRET)`。

### R-SRC-01 ACM200 量程表（`acm200.md`）
| 电压设定值 | 电压量程 | 电流设定值 | 电流量程 |
|---|---|---|---|
| V ≤ 1.8V | `ACM200_3p6V` | I ≤ 500nA | `ACM200_1UA` |
| V ≤ 5V | `ACM200_10V` | I ≤ 5μA | `ACM200_10UA` |
| V ≤ 20V | `ACM200_40V` | I ≤ 50μA | `ACM200_100UA` |
| | | I ≤ 500μA | `ACM200_1MA` |
| | | I ≤ 5mA | `ACM200_10MA` |
| | | I ≤ 50mA | `ACM200_100MA` |
| | | I ≤ 100mA | `ACM200_200MA` |

槽位：S5,S6,S11,S12,S21,S22,S27,S28（每槽 24 通道 FH/SH 0~23）。

### R-SRC-02 FOVIe 量程表（`fovie.md`）
| 电压设定值 | 电压量程 | 电流设定值 | 电流量程 |
|---|---|---|---|
| V ≤ 0.5V | `FOVIe_1V` | I ≤ 5μA | `FOVIe_10UA` |
| V ≤ 1V | `FOVIe_2V` | I ≤ 50μA | `FOVIe_100UA` |
| V ≤ 2.5V | `FOVIe_5V` | I ≤ 500μA | `FOVIe_1MA` |
| V ≤ 5V | `FOVIe_10V` | I ≤ 5mA | `FOVIe_10MA` |
| V ≤ 10V | `FOVIe_20V` | I ≤ 50mA | `FOVIe_100MA` |
| V ≤ 20V | `FOVIe_40V` | I ≤ 500mA | `FOVIe_1A` |

槽位：S3,S4,S13,S14,S19,S20,S29,S30（每槽 8 通道）。

### R-SRC-03 FPVIe 量程表（`fpvie.md`）
| 电压设定值 | 电压量程 | 电流设定值 | 电流量程 |
|---|---|---|---|
| V ≤ 50mV | `FPVIe_100MV` | I ≤ 5μA | `FPVIe_10UA` |
| V ≤ 0.5V | `FPVIe_1V` | I ≤ 50μA | `FPVIe_100UA` |
| V ≤ 1V | `FPVIe_2V` | I ≤ 500μA | `FPVIe_1MA` |
| V ≤ 2.5V | `FPVIe_5V` | I ≤ 5mA | `FPVIe_10MA` |
| V ≤ 5V | `FPVIe_10V` | I ≤ 50mA | `FPVIe_100MA` |
| V ≤ 10V | `FPVIe_20V` | I ≤ 500mA | `FPVIe_1A` |
| V ≤ 20V | `FPVIe_40V` | I ≤ 1A | `FPVIe_2A` |
| V ≤ 50V | `FPVIe_100V` | I ≤ 5A | `FPVIe_10A` |

FPVI 特殊：`FPVI.SetClamp(vClamp, iClamp)`；唯一浮动源；只做跨 Pin 浮动操作。

> 备注：`nuvolta-range-rules.md` 里的简表（ACM200 电压 40/10/3.6V，FOVI 电流到 1A 等）与源表详表口径基本一致，**脚本应以 sources/*.md 详表为准**（更全、更精确的边界值）。

---

## 六、Pin → Resource 映射（决定性查表）

### R-REL-01 Pin→Resource 映射（`pin-resource-map.md`）
| Pin | Resource Name | Type |
|---|---|---|
| VBAT | VBAT_ACM | ACM200 |
| PMID | PMID_FOVI | FOVI |
| SW | SW_ACM | ACM200 |
| BST | BTST_ACM | ACM200 |
| VDRV | VDRV_AMP_ACM | ACM200 |
| VBUS | VBUS_FOVI | FOVI |
| VAC1/VAC2/VAC3 | VAC123_ACM | ACM200 |
| AMUX | AMUX_FOVI | FOVI |
| NTC | NTC_FOVI | FOVI |
| INT/SDA | SDA_INT_ACM | ACM200 |
| FPVI_BUS | FPVI | FPVI |

- 权威来源：`资源分配表.csv`（速查表可能过时）。
- 资源命名规则：`PIN1_PIN2_..._PINn_<源表类型>`，直连放最前，relay 越多越靠后。

### R-REL-02 常用继电器速查（`pin-resource-map.md`）
K30_VBAT_Cap（VBAT Cap2）、K31_BUS_PMID_S1（PMID→FPVI_BUS）、K15_BUS_SW_S1（SW→FPVI_BUS）、K17_BUS_BST_S1（BST→FPVI_BUS）、K32_PMID_Cap、K28_VDRV_Cap、K43_SDA_INT、K58_INT_PU、K35/K36_VAC_SHARE 等。

### R-REL-03 继电器热切规则
来源：`bus-topology.md` §五
- **重配 cbite.SetOn 前，被断开 Pin 与被闭合 Pin 电压必须相等。**
- 切换 K31→K33：PMID=15V vs PGND=0V → 热切拉弧 ✗；先 PMID→0V → 切换 → 恢复 ✓。
- `cbite.SetOn(Kxx, Kyy, -1)` 后紧跟 `delay_ms(3)`；无继电器 `cbite.SetOn(-1)`。

### R-REL-04 FPVIe 域约束（铁律）
来源：`relays.md`
- FH 必须配对 SH，FL 必须配对 SL，**禁止交叉**（FH 不能进 FL_BUS/SL_BUS 域，反之亦然）。
- K90 交叉路径仅用于 Kelvin 4 线 PC 通道，**不用于标准 FPVIe DUT pin 路由**。

---

## 七、台阶/时序规则（R-ST）

来源：`units.md`、`voltage-inference.md`
| 规则 | 值 |
|---|---|
| 每步最大电压步进 | `|ΔV| ≤ 5V` |
| 每步后等待 | `delay_us(200)` |
| 下电三步间等待 | `delay_ms(1)` |
| 大电流稳定时间 | ≥1~5ms（推荐 2ms，`delay_us(2000)`） |
| 继电器动作后 | `delay_ms(3)` |

---

## 八、可脚本化 vs 仍需 agent 推理的判断

### ✅ 纯确定性可脚本化（直接转 if/else 或查表）
1. **指令→模式**（vset→FV / iset→FI / MV→FI=0+10UA）— R-PON-01
2. **浮动源识别**（`[]` 含 `2`）— R-PON-02
3. **量程选择查表**（按源表类型 + 设定值查五节详表，含 ≥2× 校验与 90% 上限校验）— R-RNG-01/03, R-SRC-01~03
4. **普通上电代码生成**（`Set(FV, v, vRng, iRng, RELAY_ON)` 模板）— R-PON-04
5. **浮动源三阶段序列**（PinB 基准 → FPVI FV=0 → PinA 升目标，每步 200μs）— R-PON-05
6. **下电类型判定**（floatingPairs 非空+vset / FI≥1A / 其他）— R-POFF-01
7. **普通下电三步**（归零保持量程 → delay 1ms → 统一 10V/10MA RELAY_OFF）— R-POFF-02/03
8. **浮动下电序列**（PinA 齐平 → PinB → 其他 → PinA → 统一 OFF → FPVI 最后 OFF）— R-POFF-04
9. **大电流初始化/测量/关断三段式**（FV=0→FI=0→SetClamp；FI=0→FV=0→OFF）— R-PON-07, R-POFF-05
10. **PowerState JSON 生成/消费**（4 字段结构）— R-PON-08
11. **Pin→Resource 查表**（从 CSV 读入）— R-REL-01
12. **BUS 继电器判定**（iset[AxB] 必须 / vset[AxB] 全用 / 单 Pin 不闭）— R-FLT-03
13. **Cap 继电器判定**（FPVI 浮动 MI→ON / 源表直接 MI→OFF / MV→ON）— R-FLT-04
14. **量程切换时序**（FV=0 用小电流量程，FI force 前再切大量程）
15. **电阻单位选择**（>100mA→mΩ / ≤100mA→Ω）

### ⚠️ 仍需 agent 推理（依赖原理图/DFT 语义，脚本只能做"提示/校验"）
1. **FET 对定义**：`voltage-inference.md` 明确"FET 对由用户提供，Agent 不可自行推断"。类型 C（导通后 Pin 相等）、E006 同步 ramp 的 C 端目标值、下电时保持 FET 导通等，依赖用户输入的 `fetPairs` 配置 + 寄存器语义。→ **需输入数据，非纯规则**。
2. **E010 Sense 通路继电器**：SH/SL 到测量点路径上的继电器（如 NU6810 的 K43+K46），必须从原理图/Netlist 追踪路径，继电器名随 HIB 板卡变化，**不可硬编码**。→ 需原理图语义。
3. **闭环判定**：条件①Force-Sense 连通 + 条件②High-Low 回路，需沿 POGO→继电器→Pin 逐段验证，`bus-topology.md` 明言"无法仅靠软件自动判定"。→ 需人工/原理图。
4. **BUS 短接是否 DFT 明确要求**：多 Pin 同闭 BUS = 短接，需验证 DFT 意图，否则禁止（PMID-SW-PGND 三端短接反例）。→ 需 DFT 语义。
5. **电压推断**（类型 A/B/C/D 叠加）：B 型依赖闭环完整，C 型依赖用户 FET 配置，D 型依赖 RDSON 近似。上下电台阶的**具体中间电压值**需要先跑电压推断器才能生成 upSequence/downSequence。→ 建议做成独立推理模块，但输入（fetPairs）来自用户。
6. **继电器热切时序**：切换前保证两端等压，需要"先归零→切换→恢复"的编排，与测试项上下文有关。→ 半可脚本化。
7. **Cap/PU/P2P 附件继电器是否闭合**：`relays.md` 明确功能规则与闭环规则是两层，需从"被测试项功能需求"判断（如开漏观测才需要上拉）。→ 需测试项语义。

---

## 九、⚠️ 必须注意的歧义/冲突清单（写脚本前需拍板）

| # | 冲突点 | 文件 A | 文件 B | 建议 |
|---|---|---|---|---|
| 1 | **FPVI OFF 电流量程** | `nuvolta-power-rules.md` / `nuvolta-high-current.md`#14：`FPVIe_10MA` | `power-off-agent.md` Step2c / `fpvie.md` 关闭段：`FPVIe_10A` | 大概率 `10MA` 是"统一小挡"正确值，`10A` 是大电流下电复用量程。需确认硬件。 |
| 2 | **大电流阈值** | `nuvolta-high-current.md`：≥200mA 必须 FPVIe | `power-on-agent.md`：iset[AxB]≥1A 才走大电流模板 | 脚本应分两层：≥200mA 决定用 FPVIe；≥1A 决定用 10A 量程 + BUS。 |
| 3 | **普通下电第 1 步量程** | `power-off-agent.md`："保持原量程" | `nuvolta-power-rules.md`："大电流挡" | 语义一致（上电量程即大挡）。 |
| 4 | **FPVI 等电位/初始化电流量程** | `power-on-agent.md` 4b：`FPVIe_10A` | `nuvolta-floating-source.md` 示例：`FPVIe_2A` | 大电流初始化 fpvie.md 用 10A；浮动电压源等电位用 2A 或 10A 均出现。建议统一模板参数。 |
| 5 | **浮动下电中 FPVI 位置** | `power-off-agent.md` Step2b：FPVI 在最后单独 OFF（`FPVIe_1V, FPVIe_10A`） | 统一量程表建议 `FPVIe_1V, FPVIe_10MA` | 同 #1。 |

---

## 十、结论

**可 100% 脚本化**：量程查表、模式映射、浮动源识别、下电三步、浮动上下电台阶序列、大电流三段式、PowerState JSON 生成、Pin→Resource 映射、BUS/Cap 继电器判定。这些全部是查表 + 固定模板 + 固定时序，可直接转 Python。

**必须保留 agent/人工环节**：(1) 从用户获取 `fetPairs`（FET 对）配置；(2) 依赖原理图/Netlist 的 Sense 通路继电器确认（E010）；(3) 闭环/短路意图判定；(4) 电压推断的 C/D 类型叠加。建议脚本把这些做成**输入接口**（读配置 + 校验输出），而非内嵌规则。

**最需要先行确认的单一事项**：FPVI RELAY_OFF 的电流量程到底是 `FPVIe_10MA` 还是 `FPVIe_10A`（九节 #1），它决定下电统一量程表的正确性。

相关文件绝对路径汇总：
- `D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-off-agent.md`
- `D:\Newtest\CLAUDE_PROCESS\.claude\agents\power-on-agent.md`
- `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-power-rules.md`
- `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-range-rules.md`
- `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-floating-source.md`
- `C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\memory\nuvolta-high-current.md`
- `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\hardware\pin-resource-map.md`
- `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\sources\{acm200,fovie,fpvie,hvie,qvme,accotest-api}.md`
- `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\standards\units.md`
- `D:\Newtest\CLAUDE_PROCESS\.claude\knowledge\hardware\{relays,bus-topology,test-strategy,voltage-inference}.md`
