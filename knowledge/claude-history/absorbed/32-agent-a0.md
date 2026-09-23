# 吸收记录 #32 — TM614/615/616 测试项定义探索（subagent 只读）

- 源文件：`sessions/32-agent-a0.md`（175 行，全文）← `~/.claude/projects/subagents/agent-a03a48eaf273d2122.jsonl`
- 时间：2026-08-26 04:43 → 04:50（0.9MB）；用户 1 条 / 助手 1 段 / 工具 69 次
- 主题：探索 TM614/615/616 是什么测试（物理/电气/项目结构类型/路径 A/B/参考材料）

## 测试项定义（OVERVIEW 权威，Dali_testmode.xlsx rows 145-147 + _dump_OVERVIEW.txt:1158-1188）

三项均：Level=BUBO、Test=direct、Purpose=SCM、isCodeGen=Y、AMS Validation=Done。meta json 目前只到 TM607/608/609，**TM614-616 未写**（PROGRESS/daylog 无记录）。

1. **TM614 `VC_CLAMP_LOW`**：VC（误差放大器 COMP 节点）低侧钳位电压。VBAT=5V+PMID=5V，BUBO 测试模式（VBUS_LOOP_DISABLE=1/IBUS_SET=127/DIS_NTC_DETECTION_ANALOG=1/BUBO_SHORT_RCOMP=1）等 10ms 后测 COMP pin 直流电压。Expect 1.3V（AMS 实测 1.044V 已知偏差）。Power=VBAT、Check=V(COMP)（纯 FV-MV）→ **一般测试项目 normal 框架**。寄存器（tm614.sv）：entertestmode+0x10=0x43/0x0E=0x7F/0x59=0x20/0x61=0x5B/0x70=0x02，delay 10ms。COMP 经 ACM200 `COMP_VCN_ACM`(S5_11) 测，Kelvin 需 K157（SCH-Connect-Map:57-59,687-689）。
2. **TM615 `PSM_THREHOLD`**：芯片进/出 PSM（脉冲跳频）的 VC 阈值。VBAT=3.5V+PMID=5V，EA_VC 经 ATEST1 mux(5) 引到 AMUX 测试垫，**ramp AMUX 1.3→1.5→1.3V** 捕比较器翻转。双阈值 Expect 1.4/1.35V（AMS 实测 r1.341/f1.392）。Check=V(DTEST0)、Dynamic=ATEST1(AMUX)、HELPER="Ramp NTC, check INT toggle"；DMUX_SEL=37=a2d_bubo_dtest。→ is_toggle() 返回 True（Check 含 V(DTEST0)）→ **toggle 框架 3 参数 PSM_THREHOLD_Rise/_Fall/_Hys**。
3. **TM616 `VC_OFFSET`**：VC offset = NTC/VC 电压使 ATEST0 电流（PWM_V2I，ATEST0_MUX=2）变号。VBAT=3.5V+PMID=5V+VDM=2V，ramp AMUX 1.3→1.5→1.3，测 AMUX 电压于 ATEST0 电流翻转点。Expect 1.4V（实测 1.41）。Check=I(ATEST0)（MI）、Dynamic=ATEST1(AMUX) → **一般测试项目 normal**；note 电流过小测试不保证（可靠性 caveat）。

## 路径 A/B 与参考材料

- 资源分配表.csv 存在（40 行 25 pin）但**稀疏（无 COMP/VDM/DTEST0/ATEST0）**；project_config _说明 明确"resource_table 仅 A 路径用，当前走 B 路径"→ **实际 B 路径**，继电器用 SCH-Connect-Map.txt（963 行 11 列）。
- OVERVIEW TM6xx 全貌：600-609 Y 已登记（meta 只有 607/608/609 写入），610-613 应力 isCodeGen 空，614-616 目标，617-626 缺，627/628 Y（Indirect trickle），631-647 部分在 reg_config。
- 参考层无 VC_CLAMP/PSM_THREHOLD/VC_OFFSET 条目（新材料族，材料门需声明）；最接近参考：TM615→code/toggle-template.cpp+UVLO.cpp+OVP.cpp+HS_ZCD/LS_ZCD（BUBO DTEST0/INT toggle）；TM614→tm600-normal-highcurrent.cpp；TM616→sub-measure-template/TM623_sub_measure + chip/CurrentSense.md。BUBO mux：DMUX_SEL=37=a2d_bubo_dtest、ATEST1_MUX=5=EA_VC、ATEST0_MUX=2=PWM_V2I。

## 涉及文件

- 只读 xlsx/OVERVIEW dump/reg_config tm614-616.sv/meta json/SCH-Connect-Map/资源分配表/project_config/Pin_Channel_define.h。零修改。

## 交叉引用

- #33 同批并行钉死观察源（TM615 observe=NQON？TM616 I(ATEST0) 在哪测）；#31 提供 pipeline 与模板；TM614-616 与 #15 TM403-425（同 BUBO 族阈值 toggle）同族。

## 未决问题

- TM614-616 生成是否发生（#34 会话及后续）。
