# 原理图解析（Netlist → 元件清单 + 连接图）

> **权威规范:** 本文档正文（源出 `原理图解析基本规则.txt`，正文已并入本文件）
> **Skill:** `skills/sch-parse.md` | **Agent:** `agents/cbit-parse-agent.md`
> **相关:** `knowledge/hardware/relays.md`（继电器规格）、`knowledge/hardware/bus-topology.md`（BUS拓扑）、`knowledge/hardware/closed-loop-model.md`（闭环模型）

---

## 一、作用与输入输出

| 项 | 内容 |
|----|------|
| **作用** | 解析原理图 Netlist（.NET），提取 DUT PIN、继电器、其他器件、源表 POGO，并生成连接图 |
| **输入** | 原理图 Net 文件 |
| **输出①** | `Component-Statistic` — 全元件分类清单（PIN/源表/继电器/元器件/net 五段） |
| **输出②** | `SCH-Connect-Map.txt` — 源表→PIN/BUS 连接图（11 列，见 §五） |

**门控铁律：** 六个任务严格串行，每个任务的检查 Step 全部判定正常后，才允许进入下一任务。任何一步报错 → 停止，向用户报告，不继续。

---

## 二、六任务工作流

### 任务一：解析所有 DUT PIN

```
Step1: 遍历所有 port，direction=OUTPUT 的 port 名 = DUT PIN 名
Step2: 忽略尾缀 _Sx（工位信息）
Step3: 统计分类：同时含 _F 和 _S 变体 → Kelvin PIN；不含 _F/_S → Non-Kelvin PIN
Step4: 输出 Component-Statistic，格式：PIN(type)，type=Kelvin|Non-Kelvin
       ⚠️ 禁止写成 PIN_F(kelvin) / PIN_S(kelvin) —— F/S 是同一 PIN 的两个端口，不是两个 PIN
Step5: 【门控】PIN 成对检查：
       只有 _F 无 _S → 报错 "Kelvin PIN 缺少Sense PIN"
       只有 _S 无 _F → 报错 "Kelvin PIN 缺少Force PIN"
       成对或纯 PIN → 正常，进入任务二
Step6: 【门控】孤立PORT检查 + TP短接确认（异常必须反馈，禁止静默跳过）：
       DUT port 无同名 net 时，按顺序：
       a. 【TP短接先问】存在 TP_<PIN> 测试点且其连接某 net
          → 一般 PIN 与 TP 短接（TP 是 PIN 的测试点/probe 点），但**必须向用户询问确认**
          → 用户确认短接 → 建立关系：PIN → TP 所在 net
          → 用户否认短接 → 继续 b/c
       b. 继电器 instance 名含 PIN → 映射到信号 net
       c. 全部失败 → 该 port 在网表中孤立（仅端口声明，不属于任何 net，如 DALI 的 PWM2）
          → 必须向用户反馈异常，原理图确认：
             i.  短接到其他 PIN 的 net（netlist 无记录，如 PWM1↔PB0）→ 登记短接表
             ii. 设计意图 NC（悬空未用）→ 用户确认后放行
       → 未确认前不得继续，禁止当成"不存在"静默跳过
       → 短接关系登记机制（PIN_SHORT_MAP 主体从 net 文件来，非固定表）：
          i. 主体从 net 文件**自动推导**：同一信号 net 的多个 PIN → 自动合并为短接节点（net_pinname/disp，无需登记）
          ii. netlist 无记录的例外（用户确认）登记在每项目配置文件 `sch_confirmed.json`
              （user_shorts = PIN↔PIN 短接，tp_confirmed = 已确认 TP↔PIN 短接），**不放解析脚本**
```

### 任务二：解析所有源表

```
Step1: 遍历所有 port，direction=INOUT 的 port 名 = 源表名
Step2: 类型判断（严格按 a~h 顺序，先匹配先生效）：
   a. 含 "ACM200" → ACM200
   b. 含 "ACM" 且不含 "200" → ACM
   c. 含 "FXVIe_PLUS" → FXVIe_PLUS
   d. 含 "FXVIe" 且不含 "PLUS" → FXVIe
   e. 含 "FPVIe" → FPVIe
   f. 含 "QVM" → QVM
   g. 含 "QTMU" → QTMU
   h. 含 "S24_Px" 或 "S9_Px" → DCM
Step3: 输出 Component-Statistic：按源表类型分组，列举同类型全部通道名
Step4: 【门控】通道成对检查：
   a. FPVIe/ACM/ACM200/FXVIe/FXVIe_PLUS：FH↔SH、FL↔SL 必须同时存在，
      缺失 → 报错（指明缺 FH/SH/FL/SL 哪个）；多通道源的 FL/SL 可能为分组端口
      （如 FL(0-3)/FL(4-7)），按组覆盖全部通道检查
   b. QVM：QVMH↔QVML 或 CHn+↔CHn- 必须同时存在，缺失 → 报错
Step5: 任务二b: 读取 Pin_Channel_define.h 建立源表名映射（STS PinPlanner 生成，与原理图同目录）
   - `extern <类型> <源表名>;` → 每个源表名的权威类型（如 `extern ACM200 ACDRV123_VCC_ACM;`）
   - `#define _PIN_CHANNEL_DEFINE_<源表名>_ "<Sx_y,...>"` → 该源表名的多工位通道串
     （所有工位对应通道共享同一名字，可同时操作）
   - netlist 源表端口（`S5_ACM200_FH1`）推导通道键（`S5_1`）→ 映射语义源表名
     （`ACDRV123_VCC_ACM`）+ 权威类型（ACM200）
   - 输出 Component-Statistic "任务二b: 源表名映射"段
   - 【门控】类型交叉验证：netlist 端口名类型与 .h 声明不一致时报错（已知别名除外），以 .h 为准

> **源表类型权威**：最终类型以 Pin_Channel_define.h 声明为准，netlist 端口名可能与实际类型不一致——
> DALI 的 S3 槽为 **FXVIe_PLUS**（旧网表误标 "FOVIe"，2026-08-05 22:11 起 netlist 直接标 `S3_FXVIe_PLUS_*`）；
> netlist 短名 "QVM"/"QTMU" 即官方 "QVMe"/"QTMUe"（'e'增强系列）。列7 FXVIe_PLUS 覆盖 S3 槽（旧命名 FOVIe 亦归类 FXVIe_PLUS）。
```

### 任务三：解析所有继电器

```
Step1: 遍历所有 Instance，名字匹配 K<数字>_ 的为继电器
Step2: 类型判断：含 "SW_SPST" → 光耦继电器；其余 → 机械继电器（常见 G6K_2G_Y_DC12_3part）
Step3a: 机械继电器 A/B part 识别：
        PortRef &2/&3/&4 之一 → A part；PortRef &6/&5/&7 之一 → B part
        同时有 A 和 B part → 一个机械继电器；只有 A 或只有 B 也正常
Step3b: 功能分类（按 §三《继电器功能分类》）：BUS 型 / Share 型 / Connect 型
Step3c: 输出 Component-Statistic：按类型分组列举全部继电器名
Step4: 【门控】浮空检查（浮空 = 该脚无任何连接点）：
       机械继电器 A part 或 B part 的 3 个脚中 ≥2 个浮空 → 报错
       光耦继电器任一脚浮空 → 报错
```

### 任务四：解析所有元器件（排除源表、PIN、继电器）

```
Step1: 按元器件类型分组列出，输出 Component-Statistic
Step2: 【门控】连接性检查：所有元器件无浮空，否则报错
```

### 任务五：解析所有 net

```
Step1: net 分类：FPVI 相关 BUS net / QVM 相关 BUS net / QTMU 相关 BUS net / 其他 net
       输出 Component-Statistic
Step2: 【门控】连接性检查：所有 net 无浮空，否则报错
```

### 任务六：生成 SCH-Connect-Map.txt

按 §五 的 11 列结构输出。每列的通路必须满足 §四《通路有效性》。

---

## 三、继电器功能分类（《继电器功能分类》）

> 分类的本质是**继电器在复用结构中的位置**，不是编号。设计原因见 §六。

### Share 继电器（PIN 端分时复用）

从源表（ACM/ACM200/FXVIe/FXVIe_PLUS/DCM）出发到 DUT PIN 经过的继电器（含默认连通和上电连通的），同时满足：

| 条件 | 内容 |
|------|------|
| Share 条件1 | 通过默认或导通可以实现源表→PIN 的连通 |
| Share 条件2 | **同一个源表通道同时连接到超过 1 个 PIN** |

### Connect 继电器（独享通道）

同样从源表→PIN 经过的继电器，满足：

| 条件 | 内容 |
|------|------|
| Connect 条件1 | 通过默认或导通可以实现源表→PIN 的连通 |
| Connect 条件2 | **同一个源表通道只对应 1 个 PIN** |

### BUS 继电器（源表端接入稀缺源表 BUS）

从稀缺源表（FPVIe/QTMU/QVM）出发到 BUS 节点经过的继电器，满足：

| 条件 | 内容 |
|------|------|
| BUS 条件1 | BUS 节点必须是节点，且数量超过 1 个 |
| BUS 条件2 | 含 "BUS" 字符的节点：必须是 Force/Sense 分开的 **Kelvin 结构**，且 FH+SH 成组、FL+SL 成组 |
| BUS 条件3 | 不含 "BUS" 字符的节点：必须能在节点处短接 Force/Sense（更常见是节点后短接），且 FH+SH 成组、FL+SL 成组；**一旦检测到，向用户确认** |

### Cap 继电器（电容耦合，名称含 CAP）

名称含 "CAP"/"Cap" 的继电器通过**电容耦合**连接两个 DUT 节点（如 BST↔SW），不是直接电气通路，**不参与 BUS/Share 通路追踪**，功能分类为 Cap。

⚠️ 误判场景：Cap 继电器连接含 `_PC_` 等类 BUS net 时（如 K57_CAP_BST_SW 连接 FPVIe1_FH_PC_S1），L3 拓扑会误判为 BUS。此时**以用户确认为准**，经 `sch_confirmed.json` 的 `relay_class` 覆盖为 Cap，禁止按名称猜测。

---

## 四、通路有效性（《通路有效性》）

> 从源表的 **Force 端和 Sense 端同时出发**到目的位置，沿途经历的继电器（含默认连通和上电连通的）算一条通路。

| 规则 | 内容 |
|------|------|
| 最短路径原则 | 同一对起终点有多条通路时，取经过继电器最少的一条 |
| 双线铁律 | **Force 和 Sense 务必同时连通**，只通一条不算通路 |
| **F/S 状态一致性铁律** | 同一继电器出现在 F 路径和 S 路径中，其 state 必须一致（同 ON 或同 NC）。G6K 等双稳态继电器通电/保持二选一，若 F 走 ON 而 S 走 NC（或反之），物理上 F/S 无法同时连通 → 该通路标 **[F/S冲突]**，非有效通路。实现：`sch_parse.py` 的 `fs_conflict()`（K83/K52 均由网表双状态触发发现） |
| **反短接铁律** | **源表→目标 PIN 的通路禁止经过/连接其他 DUT PIN**（非目标 PIN 禁止被施加状态）。例：给 A PIN 施加信号，通路中间不得顺带连到 B PIN。例外：浮动源（FPVIe）等电位/电流闭环连接的两个 PIN 都算被测目标 |
| **Rule A 固定电压节点铁律** | **源表→PIN 通路禁止穿越任何固定电压节点**。固定电压节点 = 地（机台地 AGND/DGND/JGND + 芯片地脚 AGND_F/AGND_S，0V）∪ 固定电源轨（S34_J+5V，5V；通用含 12V）。**核心判据**：固定节点电压硬件钉死、源表改不了，通路一旦经过，源表（可程控）会与固定电压**相互对拉、无法独立控制通路电压** → 非法。固定节点作**终点**合法（源表 FL 返回线接 AGND_F 地脚、地脚短路等），作**中间节点**非法。实现：`sch_parse.py` trace() + `csv_pathproof_v2.py` fixed_voltage_nets 剪枝。**软规则**：通路穿越其他源表 → 只加 `⚠经过源表` 警告不剪（源表可编程，非固定电压） |
| 汇合位置 | Kelvin = F/S 到芯片 PAD 才汇合；Non-Kelvin = F/S 在 copper/继电器处已短接（详见 `closed-loop-model.md`） |

---

## 五、SCH-Connect-Map.txt 结构（11 列）

| 列 | 内容 | 继电器类型 |
|:---:|------|:---:|
| 1 | FPVIe → FPVIe 的 BUS 节点（必须 FH+SH 组合或 FL+SL 组合）需闭合的继电器 | BUS |
| 2 | FPVIe → PIN 需闭合的继电器 | BUS |
| 3 | QTMUe → PIN 需闭合的继电器 | BUS |
| 4 | QVMe → PIN 需闭合的继电器 | BUS |
| 5 | ACM → PIN 需闭合的继电器 | Share |
| 6 | ACM200 → PIN 需闭合的继电器 | Share |
| 7 | FXVIe_PLUS → PIN 需闭合的继电器 | Share |
| 8 | QTMUe → PIN 需闭合的继电器 | Share |
| 9 | QVMe → PIN 需闭合的继电器 | Share |
| 10 | DCM → PIN 需闭合的继电器 | Share |
| 11 | 通路分类（P2P-到地 / P2P-互短 / 上拉-固定5V / 上拉-源表 / 下拉 / 稳压 / net短接） | — |

- 每列按《通路有效性》输出（最短路径 + F/S 同时连通）
- 某列全部继电器都不满足时，该列也要输出（标注无通路），不允许静默省略
- **通路终点显示 F/S 端口**：标题行显示合并节点名（`ACDRV1`、`PA6_PWM2`），路径行终点去工位尾缀保留 F/S 侧（Force 路径 → `ACDRV1_F`，Sense 路径 → `ACDRV1_S`）；F 与 S 两条路径终点不得都只显示节点名

### 列11 通路分类（六类，按连接分类）

| 分类 | 结构 | 判据 | 需闭合继电器 |
|------|------|------|------|
| P2P-到地 | PIN ↔ 地脚(AGND_F) | 继电器端点一侧=DUT PIN、另一侧=地脚；ON≤2 | 该继电器 |
| P2P-互短 | PIN ↔ PIN（不同 base） | 继电器端点两侧=两个不同 DUT PIN；ON≤2 | 该继电器 |
| 上拉-固定5V | PIN + 电阻 + 继电器 + S34_J+5V | 电阻一端 PIN、另一端经继电器到固定5V轨；**不看电阻值** | 路径继电器 |
| 上拉-源表 | PIN + 电阻 + 继电器 + 源表端口 | 同上，另一端经继电器到源表（可输出 range 内任意电压） | 路径继电器 |
| 下拉 | PIN + 电阻 + 继电器 + 地 | 同上，另一端到地（AGND_F 地脚/机台地） | 路径继电器 |
| 稳压 | PIN + 电容(≥100nF) + Cap继电器 | **按电容值≥100nF 判（不看名字）**，值权威 CSV ComponentValue（adapter 嵌入合成 EDIF） | 名含 Cap/CAP 的继电器 |
| net短接 | 两 net 同电气节点（直接导线） | CSV `ELECTRICAL_SHORT_GROUP`(DIRECT_NET_ALIAS) / `NET_TIE_GROUP`(EffectiveShortNets)；**只记录不合并** | — |

> **排除判据**：Kelvin 电阻（两端 net 直接 F↔S 同 base，如 R_PD2_S1/R_PD3_S1/R_PD5_S1）不进上拉/下拉。
> **上拉两子类必须分开标**：固定 5V 轨（只能 5V）≠ 源表（可输出 range 内任意电压，不限 5V）。
> **net短接语义**（用户确认 2026-08-25）：短接组内两 net 是同一电气节点，**不合并**（各自处理）；
> 但通路分析须注意「一旦经过此节点即已短接」这一事实——即使后面通路又分开 force/sense，也不再是 Kelvin 四线走线
> （如 FPVIe0_FL_PC_S1 ↔ FPVIe0_SL_PC_S1、FPVIe0_FH_PC_S1 ↔ FPVIe0_SH_PC_S1 的 F/S 已被直接导线短接）。
> 完整判定优先级（ELECTRICAL_SHORT_GROUP → NetTie → 多 NET_LABEL → 0Ω → Jumper → Relay/MOS）见 `schematic_parse/NET_SHORT_RULES.md`。

---

## 六、设计原理：为什么要分时复用、为什么要 BUS

> 本节是功能分类的"为什么"——理解设计动机才能在没有编号表的新板卡上正确分类。

### 6.1 稀缺源表 vs 其他源表

| | 稀缺源表 | 其他源表 |
|---|---------|---------|
| 类型 | FPVIe, QVM, QTMU | ACM, ACM200, FXVIe, FXVIe_PLUS, DCM |
| 通道数 | 极少（FPVIe 一板仅 2 通道） | 多（ACM200 每槽 24ch） |
| 矛盾 | 通道远少于 PIN 数 | 通道可能不够分给每个 PIN |

### 6.2 Share 继电器 = PIN 端分时复用

**问题：** 其他源表通道不够每个 PIN 一个通道。
**方案：** 一个源表通道 → 继电器 → 多个 PIN，继电器在 **PIN 端**，切换哪个 PIN 接入仪器。测试串行执行，不同时间测不同 PIN —— 这就是"分时复用"。

```
                ┌─ K_SHARE(NC默认) ── PinA  (默认通道)
源表通道 ── COM ┤
                └─ K_SHARE(NO通电) ── PinB  (备用通道)
```

### 6.3 BUS 继电器 = 源表端接入稀缺源表总线

**问题：** 稀缺源表通道更少。若 n 个 PIN 共享 1 个 FPVI 通道用点对点接法，机械继电器需要 n-1 个、光耦需要 2n 个 —— 不可扩展。
**方案：** **BUS 广播**——FPVI 分出 Force-Sense 总线（FPVI_BUS），各 PIN/源表通过各自的 BUS 继电器接入总线。继电器在 **源表端**，切换该通道是否接入 BUS。

两个好处：
1. 各源表/PIN **独立接入** BUS，可同时接入也可选择性接入；
2. 接入端在源表处 → 该源表连接的所有 PIN 都可以通过 Share 继电器**二级分时复用** FPVI BUS（BUS + Share 组合 = 两级复用）。

### 6.4 三种稀缺源表的 BUS 线结构（黄金准则）

| 稀缺源表 | BUS 线 | Kelvin? | G6K 两 pole 走法 |
|---------|-------|:---:|------|
| FPVIe | FH+SH+FL+SL（4线） | ✅ | 两 pole 分别走 Force 和 Sense |
| QVM | SH+SL（2线） | ✅ | 两 pole 分别走 SH 和 SL |
| QTMU | FH（1线） | ❌ | 只走 FH（FL 已接机台地，不分 Kelvin） |

**黄金准则：FPVIe/QVM 的 BUS 线输出必须是 Kelvin 结构（Force 和 Sense 分开）；QTMU 不分 Kelvin。**

### 6.5 动态分类（三层判断，替代硬编码编号）

> 硬编码编号表（如"K15,K17... 是 BUS"）只是**某一块板卡的实例**，换板卡即失效。分类必须按功能位置动态判断。

| 层 | 依据 | 判断 |
|:---:|------|------|
| 1 | CBIT 表名称初判 | 含 SHARE/SHARE2 → Share；含 BUSH/BUSL/VBUSL → BUS 候选；含 CAP → Cap 候选；其余 → 通用 |
| 2 | SCH-Connect-Map 交叉验证（定案） | 出现在 "Connect Relay to Resource" 段 → Share；出现在 "Relay to FPVI_BUS" 段 → BUS；两段矛盾 → 标记人工确认 |
| 3 | Netlist 拓扑验证（兜底） | BUS：G6K 两 pole 指向**同一目标**（BUS 线），F/S 分开走；Share：G6K 两 pole 指向**不同目标**（不同 PIN） |

⚠️ **不是所有名字含 BUS 的继电器都是 BUS 继电器** —— 必须过第 2/3 层验证。

### 6.6 同名 Net 必须合并（分时复用的副产物）

同一 PIN 允许两个源表通道连接（避免特殊情况的分时复用冲突），导致同名 Net 出现多条记录。**同名 Net 物理上是同一电气节点，解析时必须合并所有 Joined 成员**，否则通路追踪会漏连接。

```
合并前:  AMON_S_S1 → [(K39,&6)]        AMON_S_S1 → [(R_AMON,&1),(TP_AMON,&1)]
合并后:  AMON_S_S1 → [(K39,&6),(R_AMON,&1),(TP_AMON,&1)]
```

---

## 七、常见错误

| 错误 | 正确 |
|------|------|
| 把 `PIN_F` 和 `PIN_S` 当两个独立 PIN 输出 | 同一 Kelvin PIN 的两个端口，输出 `PIN(Kelvin)` |
| ACM 先匹配导致 ACM200 被误判为 ACM | 类型判断严格按 a~h 顺序，ACM200 优先 |
| 用编号范围硬编码功能分类 | 用 §6.5 三层动态分类 |
| 通路只追 Force 没追 Sense | F/S 务必同时连通（§四） |
| 同名 Net 不合并直接建 net_map | 解析阶段先合并（§6.6） |
| 任务报错后继续下一任务 | 门控：报错即停，报告用户 |
| 孤立PORT（无同名net、无TP、无继电器名映射）静默跳过 | 异常必须向用户反馈，原理图确认短接/NC后才继续（任务一 Step6c） |
| 有 `TP_<PIN>` 测试点就静默假设 PIN↔TP 短接 | 必须先向用户询问确认，确认后才建立关系（任务一 Step6a） |
| Cap 继电器连接 `_PC_` 类 BUS net 被拓扑误判为 BUS | 以用户确认的 `relay_class` 覆盖为准（如 K57_CAP_BST_SW = Cap，登记在 sch_confirmed.json） |
| 按 netlist 端口名判定源表类型，忽略 Pin_Channel_define.h | 以 .h 声明为权威类型（如 netlist 标 FOVIe 的 S3 实为 FXVIe_PLUS；QVM/QTMU = QVMe/QTMUe） |
| 通路经过非目标 PIN 仍当作有效通路（如闭合 Share 两侧继电器把两 PIN 短接） | 反短接铁律: 非目标 PIN 禁驱动，除非浮动源连接两 PIN；生成测试通路前核对中间节点不包含其他 DUT PIN |
| **串/并联误判**: 两个 relay 的 COM 同接一条 BUS，就当成串联 | COM2 共享 ≠ 串联；O2→COM2 才是串联。查 O2：不同 relay 的 O2 去不同地方 = 并联 |
| **多余 relay**: 信号根本不会经过某个 relay，却说需要操作它 | 走线不到的地方，那个 relay 不参与；核对整条链路上 relay 是否实际在路径上 |
| **遗漏直接路径**: relay 旁有直接铜皮（NC 直通），却以为必须经过 relay | 查 pin 两侧：有 NC 直通路径吗？有则不需闭合该 relay |

> 以上三条为继电器拓扑追踪专属错误，源自旧 A0-原理图Agent（已迁移）。通路追踪时同样适用于 gen_paths.py 结果的人工核对。
