# 吸收记录 #7 — 脚本模式 + TestItemMeta JSON schema + 电源代码样例调研

- 源文件：`sessions/07-agent-ae.md` ← `~/.claude/projects/subagents/agent-ae56468dece4444b1.jsonl`
- 时间：2026-08-09 10:34→10:36（0.4MB）；subagent 只读调研
- 主题：为"上电/下电代码生成脚本"摸清现有写法模式、TestItemMeta 数据结构、真实电源代码

## 现有脚本写法模式

- **gen_tm206_425.py（54KB，生成器范式）**：`AI = 目标路径` + `blocks=[]` + 模板字符串（`@TM@`/`@PNAME@`/`@SRCSET@` 等占位符）+ 构建器函数 `.replace()` + 读全文件**末尾追加**。模板 6 段：Step1 Connect(cbite.SetOn)→Step2 Power On→Step3 Register(entertestmode)→Step4 Measure→Step5 Power Off(三步下电)→Step6 LogData。注释用 `// vset[vbat,4,100e-6,0] → VBAT=4V` 反推 DFT 指令。
- **verify_relay_trace.py（7KB，verify 范式）**：`read_enc()`（utf-8-sig→utf-8→gbk→latin-1 回退，**DLP 加密环境必须复用**）；`parse_defines`（`#define\s+(K\d+_\w+)\s+(\d+)`）；`cbite.SetOn\(([^)]*)\)` 正则；按 `DUT_API int (TM\d+_\w+)` 切函数；errors/warns 累积 + `sys.exit(1)` FAIL / `PASSED` exit 0；`--warn-as-error`（sys.argv 非 argparse）。
- **verify_merge_rules.py（5KB）**：`main()` + `sys.stdout.reconfigure(encoding='utf-8')`；`[前缀]` 汇总行。

## TestItemMeta JSON schema（dual-parse-agent.md:34-57 定义）

```json
{ "functionName","testType","params":[{shortName,check,checkPin,trim}],
  "hardwareInit":[{cmd:"vset|iset", pin:小写, value, time:"100e-6", ignore:0}],
  "softwareInit","dynamic","pinsInvolved","resourcesInvolved",
  "floatingPairs":[{type:"vset|iset", pinA, pinB, deltaV, fullNotation}],
  "activeFetPairs":[{id,pair,type,condition}],
  "voltageInference":{preFetOn,postFetOn} }
```
- pin 含 `"2"` = 跨 Pin 浮动源；跨 Pin 时 resourcesInvolved 必须追加 `"FPVI"`（铁律）
- 消费方：power-on-agent 输出上电代码块 + PowerState JSON（4 字段）；power-off-agent 消费 PowerState

## 真实电源代码（对拍基准）

- 普通：`VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON); delay_ms(1);` 下电三步。
- 多源：VBUS+VBAT+VAC123 各 Set，下电先全部 FV=0 保持量程 RELAY_ON → delay_ms(1) → 统一 10V/10MA RELAY_OFF。
- FPVI 浮动大电流（test.cpp TM600）：FV=0→FI=0→SetClamp(25,25)→FI=1A→delay_us(2000)→MeasureVI(200,5)→FI=0；下电台阶反转、FPVI 最后 OFF（`FPVIe_10MA`）。
- **源表对象名两套**：AI.cpp 现行（`VBAT_PD3_FXVI`/`VAC123_AMUX_ACM`/`VCC_VMCU_FXVI`/`VBUS_DRVH1_ACM`/`AMUX_PGND_FXVI`/`NQON_HG1_ACM`/`QTMU_GP`/`FPVI`）vs test.cpp 旧名（`VBAT_ACM`/`PMID_FOVI`/`BTST_ACM`…）——**以 AI.cpp extern 为准**。

## 资源分配表.csv 格式（10 列）

`Unnamed:0, Pin Name, Resource Name, Connect Relay to Resource, Relay to FPVI_BUS, P2P Relay, Type, Cap1, Cap2, PULL_UP RESISTOR, Prority`
- 行例：`15,VBAT,VBAT_ACM,Default,K29_BUSL_VBAT,,ACM200,"10nF, DC","Cap_4.7uF, K30_VBAT_Cap, R_1K",,1`
- 每 Pin 可多行；FPVI 特殊行（`FPVI_BUS,FPVI,Default,Default,,,FPVI`）+ FPVI_PC Kelvin（K9-K13）；DFT.csv 是原始表（Hardware_initial 列即 `vset[...]` 多行）。

## 交叉引用

- 输入给 #8（gen_power_sequence.py 架构设计）；`#define Kxx` 在 AI.cpp 顶部（13 处，与 relay.h 不一致，verify 以 AI.cpp 为准）；Cap 断开规则 FR-001（见 #9）。
