# 吸收记录 #5 — S3 更名重生成 + 反短接铁律 + Toggle 3 参数规则 + 上下文管理规则

- 源文件：`sessions/05-a5e7eabc.md` ← `~/.claude/projects/C--Users-nvt10241/a5e7eabc-c3bb-47b8-b6ff-82d028f96600.jsonl`
- 时间：2026-08-05 14:06 → 08-06 02:22（2.1MB）；用户 8 条 / 助手 92 段 / 工具 187 次
- 主题：**S3 端口更名（FOVIe→FXVIe_PLUS）重生成 + AI.cpp VAC 家族修正 + 两条规则固化（反短接铁律、Toggle 3 参数）+ 上下文管理约定**

## 阶段一：S3 端口更名重生成

- 新网表（22:11）把 S3 端口从 `S3_FOVIe_*` 全部改为 `S3_FXVIe_PLUS_*`（与 Pin_Channel_define.h 权威类型一致），无 FOVIe 残留。
- **坑**：`sch_parse.py` 硬编码旧前缀 → G2 误报 FAIL、列7 丢通路 → 改为 `S3_FXVIe_PLUS_`（classify_source 保留 FOVIe 兼容分支）。
- 规则文档 4 处"netlist 标 FOVIe"过时表述同步（原理图解析基本规则.txt / schematic-parsing.md / sch-parse.md / nuvolta-codegen.md）。
- 统计零回归：182 继电器 / 276 元器件 / 306 net；CBIT↔网表 182=182（"同号不同名"仅为 CBIT 基础名 vs 网表 `_S1` 工位尾缀）。

## 阶段二：AI.cpp 重写 + VAC 通路错误修正（重要）

- 源表名清单（Pin_Channel_define.h 提取，7 个）：VBAT_PD3_FXVI(FXVIe_PLUS/S3_5)、VDM_SDA_ACM(ACM200/S5_7)、NQON_HG1_ACM(S5_9)、VBUS_DRVH1_ACM(S5_10)、PB5_PC4_ACM(S5_14)、ACDRV123_VCC_ACM(S5_1)、SCL_VACWL_ACM(S5_2 备用)。
- **用户质疑 K69_PB5_F → 挖出 AI.cpp 真实错误**：地图里 VAC1/2/3 由 `VAC123_AMUX_ACM`（S5_0）经 K18/K19/K20 选择树驱动（默认导通免 SetOn），AI.cpp 却用了 `PB5_PC4_ACM`（S5_14，K100 直连是给 PB5/PC4 的）+ 同时闭合 K69(→PB5_FORCE) 与 K70(→VAC_FORCE)——**会把 PB5 和 VAC1 两个 PIN 短接**，违反 Share"二选一"。
- **修正**：TM105/108/109/110/111/112 源表 → `VAC123_AMUX_ACM`，移除 K69/K70/K77/K78 SetOn（保留 VAC2→K19、VAC3→K18、Cap2 K13/K21、K65_nQON_PU）。

## ⭐ 反短接铁律（用户立规，全链固化）

> 测试时，源表→目标 PIN 的通路**禁止经过/连接其他 DUT PIN**（非目标 PIN 禁驱动）。例外：浮动源（FPVIe）等电位/电流闭环连接的两个 PIN 都算被测。

落地位置：schematic-parsing.md §四（铁律）+ §七（错误表）、check-agent.md **P006**（检查 FAIL）、relay-agent.md **Step 11**（生成时查通道）、nuvolta-codegen.md 核心规则 + 错误清单 **H009**、memory `nuvolta-anti-short-rule.md`。
（背景：会话 #2 曾误判"VAC123_AMUX S5_0 悬空"——本会话以网表级溯源纠正，证明**必须以 SCH-Connect-Map/网表为准，不轻信语义名与首轮推断**。）

## ⭐ Toggle 3 参数规则（用户立规）

> 有 ramp（AWG）的测试项目，DFT 有两段（升+降）→ 参数为 `Param_Rise / Param_Fall / Param_Hys`，**Hys = Rise − Fall**，禁止单参数。

- AI.cpp 8 个 Toggle 函数（TM105-112）改为 3 参数（8×hys 计算 + 8×_Rise/_Fall/_Hys 输出，48 处改动）。
- 落地：dual-parse-agent.md Step 3 + 铁律、measure-agent.md、check-agent.md **E005**、framework.md、nuvolta-codegen.md **H010**、memory `nuvolta-toggle-rules.md`。
- TM113 同为两段式，待算法定稿后展开（当前：VCC ramp 单点测 I(VBAT)，真折返需扫 VCC 采样找峰值）。

## ⭐ 上下文管理约定（用户立规，长期工作方式）

> 上下文快满时：**大体积产出（尤其代码）保存到本地文件，对话里只留简短摘要**（改动文件/函数、应用规则、验证结果、待办）。

- 固化：memory `nuvolta-context-management.md`；MEMORY.md 写TM触发链。
- **代码模板变更**：`ToggleTest tt` → 全局一次 `Test_Method test_method;//cannot delete`（函数内不再声明；16 处 `test_method.rampv_capv(`）。
- TM113 用户指出应改用 **`rampv_capi`**（ramp 电压、捕获电流）做折返检测，参考 rampv_capv；本会话结束前被用户打断（DEEPSEEK.md 有 ramp 函数族权威文档待查）。

## 其他

- VS Code `code` 命令失效（bin\code.cmd 指向已删哈希目录 `1b6a188127`，实际 `df53daabb1`）→ 用 `Code.exe` 直接打开（遗留问题，可修）。
- 验证方法参考：check-agent 四层（P/E/R/H）+ 门控体系。

## 交叉引用

- VAC 通路错误链条：#2 首轮推断（K69 必需）→ #5 网表溯源推翻（S5_0 才是 VAC 通道）→ 反短接铁律诞生。与后续 gen 脚本的"最短通路/反短接"逻辑直接相关。
- 与「工作流全景.md」Step4（relay-agent）、Step7（measure）对应。

## 未决问题

- TM113 折返算法 + `rampv_capi` 签名确认（DEEPSEEK.md 权威文档）。
- K13_VBAT_Cap 分类、DTEST0 触发电平 1.65V、field[] 寄存器地址（同前，长期）。
