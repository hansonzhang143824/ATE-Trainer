# 吸收记录 #33 — TM615/616 观察源钉死调查（subagent 只读，结论性证据）

- 源文件：`sessions/33-agent-ae.md`（288 行，全文）← `~/.claude/projects/subagents/agent-ae4848cfb9fb6ef04.jsonl`
- 时间：2026-08-26 04:56 → 05:07（0.5MB）；用户 1 条 / 助手 29 段 / 工具 47 次
- 主题：为 TM614/615/616 写码钉死观察源/测量对象（问题 A：TM615 observe 源；问题 B：TM616 I(ATEST0) 测量对象与库函数）

## ⭐ 问题 A 结论：TM615 PSM_THREHOLD 观察源 = **NQON_HG1_ACM**（不是 AMUX_PGND_FXVI）

证据链：①`_dump_TestIO.txt` 焊盘→信号映射（物理铁证）：nQON→DTEST0（+SCAN_OUT）、VDM→ATEST0（SCAN_EN）、AMUX(PD6)→ATEST1 → V(DTEST0) 翻转物理发生在 nQON pad；②同族校准：TM403/406/412 DFT observe 列写 VBUS/VBAT 但全部实现为观察 NQON_HG1_ACM（test.cpp:5840-5851 注释"nQON high-Z reads DTEST0 logic level"；TM412:6330-6341），OVERVIEW note 都是"check INT toggle"；③TM615 自己 note="Ramp NTC, **check INT toggle**"（_dump_OVERVIEW.txt:1165-1173）→ INT=nQON。ATEST1(AMUX) 是 swept 节点标注（被 ramp 的激励），非测量脚。**照抄 TM403 但 ramp 源换 AMUX**：
```cpp
test_method.rampv_capv(AMUX_PGND_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_10MA,
                       NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                       1.3, 1.5, 200, 20, 1.65, TRIG_FALLING, vth_r);  // + 下行 1.5→1.3 TRIG_RISING
hys[site] = (vth_r[site] - vth_f[site]) * 1e3;  // R-HYS
```

## ⭐ 问题 B 结论：TM616 VC_OFFSET

1. **I(ATEST0) 测在 `VDM_SDA_ACM`**（TestIO：VDM→ATEST0）；先例 TM103（test.cpp:1829-1836）"VDM 为 ATEST 的模拟 PIN: 直接测电流"：`VDM_SDA_ACM.Set(FV,1,...,RELAY_ON); MeasureVI(50,5); GetMeasResult(site,MIRET)*1e6`。
2. **库函数 = `rampv_capi`**（ramp 电压+捕获电流，Test_Method.h:73 FXVIe_PLUS ramp+cap 重载；实现 Test_Method.cpp:1242：cap_res 保持 cap_fv_value + SetMeasITrig，result = ramp_res 电压在 cap 电流穿 trig 时刻）。可直接照抄调用行（以 TM113 test.cpp:2580-2587 为模板）：
```cpp
test_method.rampv_capi(AMUX_PGND_FXVI, FXVIe_PLUS_10V, FXVIe_PLUS_10MA,
                       VDM_SDA_ACM, ACM200_10V, ACM200_10UA,
                       2.0,            // cap_fv_value = VDM 固定 2V (vset[vdm,2])
                       1.3, 1.5, 200, 20,   // start, stop, step, interval
                       0.0001,         // trig_level 小正电流 (电流过小 caveat)
                       TRIG_RISING, vc_offset);
```
不是 AMUX 单点 MeasureVI(FI)/MIRET——这是找"电流突变对应电压"的跨越检测，必须 ramp+trigger-capture。

## 补充：继电器 K 名清单（StdAfx.h 宏 + SCH-Connect-Map）

| DUT 引脚 | 源表对象 | K | 宏 | 状态 |
|---|---|---|---|---|
| VBAT | VBAT_PD3_FXVI(S3_5) | K8 | K8_FOVI5_PD3(:163) | 默认 NC 无需 SetOn |
| PMID | PMID_HG2_FXVI(S3_1) | K84 | K84_FOVI1_HG2(:246) | 默认 NC；稳压 cap K85_CAP_PMID(:247)；FPVI 通路 K83_BUSH0_PMID |
| AMUX | AMUX_PGND_FXVI(S3_3) | K155 | K155_FOVI3_PGND(:329) | 默认 NC；BUS 通路 K154_BUSH0_AMUX |
| COMP | COMP_VCN_ACM(S5_11) | K157 | K157_ACM11_COMP(:332) | **Relay-ON 需 SetOn** |
| nQON | NQON_HG1_ACM(S5_9) | K64+K65 | K64_ACM9_HG1(:227)/K65_nQON_PU(:228) | K64 默认 NC；K65 上拉需 SetOn |

## 涉及文件

- 只读：test.cpp（TM403:5806-5866/TM412:6320-6350/TM113:2548-2614/TM103:1815-1852）、库函数/test_method/Test_Method.h(.cpp)、Pin_Channel_define.h、StdAfx.h、_dump_OVERVIEW.txt、_dump_TestIO.txt、SCH-Connect-Map.txt、reg_config tm615/616.sv。零修改。

## 交叉引用

- #32 提供 DFT 全貌（本会话钉死实现细节）；观察源结论与 #15 TM403-425 实现一致（nQON 捕 DTEST0）；rampv_capi 语义与 #15 ramp 库文档一致。
- 关键领域知识沉淀：**TestIO 焊盘映射（nQON→DTEST0、VDM→ATEST0、AMUX→ATEST1）是 BUBO 阈值测试观察脚判定的物理权威**——后续写码直接引用。

## 未决问题

- TM614-616 最终实现是否按此落笔（#34 会话查证）。
