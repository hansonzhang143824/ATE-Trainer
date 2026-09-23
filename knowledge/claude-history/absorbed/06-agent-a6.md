# 吸收记录 #6 — 上下电确定性规则提取（R-PON/R-POFF/R-FLT/R-RNG/R-SRC/R-ST 全表）

- 源文件：`sessions/06-agent-a6.md` ← `~/.claude/projects/subagents/agent-a600621296415fbd4.jsonl`
- 时间：2026-08-09 10:34→10:35（0.2MB）；subagent 只读调研（为 gen_power_sequence.py 脚本化做准备）
- 主题：把 power-on/off agent 的确定性规则全量提取为**决策表**，供脚本化

## 规则体系（编号即权威引用，后续脚本直接对应）

**上电 R-PON**：①指令→模式（vset→FV / iset→FI / MV 无 FI→FI=0+10UA）②浮动源识别（pin 含"2"即跨 Pin）③量程 ≥2× 设定值、≤90% ④普通上电模板 `Set(FV,v,vRange,iRange,RELAY_ON)` ⑤浮动电压源三阶段（PinB 基准→FPVI FV=0 等电位→PinA 台阶升，每步 ≤5V+delay_us(200)）⑥vset[A2B]+FET 导通台阶 ramp（E006 防反偏，A 领先 C 恰 V）⑦大电流三段式（FV=0→FI=0→SetClamp(25,25)→FI=target，稳定 delay_us(2000)，测完立即 FI=0）⑧PowerState JSON 4 字段：sources[]/floatingPairs[]/upSequence[]/finalVoltages{}。

**下电 R-POFF**：①类型判定（floatingPairs 非空+vset→浮动 / FI≥1A→大电流 / 其他→普通）②普通三步（全部 FV=0 保持量程 RELAY_ON → delay_ms(1) → 统一 10V/10MA RELAY_OFF）③RELAY_OFF 统一量程表 ④浮动下电（反转 upSequence：PinA 先降→PinB→其他→PinA 归零，≤5V+delay_us(200)，**FPVI 永远最后 RELAY_OFF**）⑤大电流下电 FI=0→FV=0→OFF ⑥铁律：下电起点=PowerState 最终态、测量后归零用 FV=0。

**浮动源 R-FLT**：FPVIe 唯一浮动（QVMe 自身闭环）；等电位 `FPVI.Set(FV,0,FPVIe_1V,FPVIe_10A,RELAY_ON)`；FPVI_BUS 决策表（iset[AxB] 必须 / vset[AxB] 实践全用 / 单 Pin 不闭）；Cap2 三档（FPVI 浮动 MI→ON / 源表直接 MI→OFF / MV→ON）；E010 Sense 通路继电器必须闭（需原理图追踪）。

**量程 R-RNG / 查表 R-SRC**：ACM200 V:3p6V(≤1.8)/10V(≤5)/40V(≤20)，I:1UA(≤500nA)~200MA(≤100mA)；FOVIe(=FXVIe_PLUS) V:1V~40V，I:10UA~1A；FPVIe V:100MV~100V，I:10UA~10A。电阻单位 >100mA→mΩ / ≤100mA→Ω；程序电压=V、电流=A。

**继电器 R-REL / 台阶 R-ST**：Pin→Resource 查表（权威=资源分配表.csv）；继电器热切（先等压再切换）；FPVIe FH/SH、FL/SL 禁交叉；每步 ≤5V + delay_us(200)、继电器后 delay_ms(3)、大电流稳定 ≥1-5ms。

## ⚠ 脚本化前必须拍板的冲突清单

1. **FPVI RELAY_OFF 电流量程**：`FPVIe_10MA`（统一小挡）vs `FPVIe_10A`（大电流复用）→ 后续 #8 以 test.cpp:1042 实锤 **10MA** ✓
2. 大电流阈值双层：≥200mA 强制 FPVIe；≥1A 触发三段式+BUS
3. 普通下电第 1 步量程 = 上电量程（大挡）
4. FPVI 等电位/初始化 iRange 10A vs 2A 版本差异
5. 浮动下电 FPVI 位置（最后单独 OFF）

## 可脚本化 vs 需 agent

- **100% 脚本化**：量程查表、模式映射、浮动源识别、下电三步、浮动上下电台阶、大电流三段式、PowerState JSON、Pin→Resource、BUS/Cap 判定（15 项）
- **必须 agent/人工**：fetPairs（FET 对，用户提供）、E010 Sense 通路继电器（原理图）、闭环/短路意图、电压推断 C/D 类型

## 交叉引用

- 本会话是 #7（脚本模式调研）、#8（gen_power_sequence.py 设计）的前置；规则编号 R-PON/R-POFF 等在 #8 的 RULE_COVERAGE 中被引用。
- 源文件位置：`.claude/agents/power-on-agent.md`、`power-off-agent.md`、memory 的 nuvolta-{power-rules,range-rules,floating-source,high-current}.md、knowledge/sources/{acm200,fovie,fpvie}.md、knowledge/standards/units.md、knowledge/hardware/{relays,bus-topology,test-strategy,voltage-inference}.md
