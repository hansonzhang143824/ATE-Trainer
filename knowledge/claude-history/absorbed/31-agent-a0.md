# 吸收记录 #31 — codegen pipeline 机制与最近批次复盘报告（TM614-616 实施规划前置，subagent 只读）

- 源文件：`sessions/31-agent-a0.md`（387 行，全文）← `~/.claude/projects/subagents/agent-a0c94c95e413d92dd.jsonl`
- 时间：2026-08-26 04:43 → 04:47（0.8MB）；用户 1 条 / 助手 22 段 / 工具 43 次
- 主题：为规划 TM614/615/616 批次实施，完整报告 codegen pipeline 机制（master skill 流程/最近批次写法/meta 门/收尾脚本顺序）

## 报告要点（结构化）

1. **master skill 流程**（nuvola-codegen.md）：双路径入口（A=有资源分配表→dual-parse--A；B=无→sch-parse→COMPONENT-STATISTIC+SCH-Connect-Map→Pin_Channel_define→dual-parse--B）；cbit 公共前置（P1 gen_cbit_defines --cbit --stat / P2 gen_paths --json / P3 gen_path_defines / P4 --verify；B 路径完整四阶段）；共享生成循环（relay-agent→pin-map JSON→gen_power_sequence.py 一次输出 POWER_ON/POWER_STATE/POWER_OFF 三 SECTION→entertestmode+Software_initial 模板→measure-agent→LogData→单函数冒烟 verify_single_fn.py 7 项）；收尾双查（check-agent + cbit --verify + verify_awg_params + meta 门）。
2. **规则摘要**：反短接 P006/H009、闭环、BUS 决策表、Cap2 FR-001 按 PIN 豁免（函数级 MI 豁免是反模式=10 函数漏检教训）、entertestmode 铁律 R034、Toggle 3 参数+Hys=rise-fall+反向 TRIG、单位换算（换算在 GetMeasResult 处不在 SetTestResult）、R-PON-09 两段式按 PIN 类型、≥200mA→FPVIe、Trim 铁律（TRIM_NODE=key 大写+execute+sub.cpp measure）、MR-000 一 TM 一函数、B-001 批量纪律（冒烟先行/长度降序/自检）。
3. **最近批次**：TM216-402（9 函数）与 TM403-425（15 函数：8 Toggle+4 FB+3 Trim）2026-08-10 完成，生成器 `_archive/gen_insert_tm403_425.py`；**完整 Toggle 模板 = TM403 函数体**（六步法逐段注释、K13_VBAT_Cap+K65_nQON_PU、rampv_capv 双扫 3.7→4.5→3.7 TRIG_FALLING/RISING、Hys×1e3、三步下电、SetTestResult）；FB/MV 模板 TM418；Trim 模板 TM424（TRIM_NODE &MNT_DAC_BUF_OS + execute + sub.cpp measure_mnt_dac_buf_os 写 EFUSE F7/F8）。
4. **meta 门**：gen_testitems_meta.py（纯 DFT 派生 OVERVIEW→capAuthority 四集；读 test.cpp 函数名单 regex `DUT_API int (TM\d+(?:_\d+)?_\w+|Trim_\w+)`）→ check_testitems_meta.py --require-all（正向：test.cpp 每函数必有 meta）/ --require-scope <范围>（反向：OVERVIEW isCodeGen=Y 必须已写入）。
5. **收尾顺序**：生成期每函数 verify_material_receipt.py + verify_single_fn.py；批次后 gen_testitems_meta.py → check_testitems_meta.py --require-all --require-scope → verify_relay_trace.py --meta --warn-as-error → gen_cbit_defines.py --verify → verify_awg_params.py → fast_rebuild.ps1（Release 0 errors/0 warnings）。
6. ⭐ **材料门已落地**（2026-08-23 吸收自 codex）：生成前按 param_type_index 判参数类型→读 chip/method/全部 code/ 黄金材料→写 receipt→`verify_material_receipt.py --receipt --tm`（FAIL 阻止 relay-agent；TM607-609 根因：Current Threshold/ZCD 必须同时声明 code/HS_ZCD.cpp+code/LS_ZCD.cpp）。TM614-616 的 OVERVIEW isCodeGen=Y 已就绪（TM614 VC_CLAMP_LOW Check=V(COMP)、TM615 PSM_THREHOLD Check=V(DTEST0)、TM616 VC_OFFSET Check=I(ATEST0)），meta 尚无 → 需重生成。
7. DLP 读写纪律 + B-001 建议（先插 1 代表函数冒烟全绿再批量）。

## 涉及文件

- 只读 master skill、daylog 2026-08-09/10/16/24、_archive/gen_insert_tm403_425.py（模板权威源）、verify 脚本接口、project_config.json、meta json（81 函数无 TM614-616）。

## 交叉引用

- 材料门/verify_material_receipt.py/verify_bst_sw_sequence.py 证实 #30 评估的吸收落地；#32/#33 同批（08-26 04:43 并行）分别探 TM614-616 测试定义与观察源；模板函数体（TM403/TM418/TM424）即 #15 产物。
- "TM607-609 根因：必须同时读 HS_ZCD+LS_ZCD" 与 #30 材料门描述一致。

## 未决问题

- TM614-616 实际生成是否发生、材料门 receipt 是否声明（#34 及后续会话查证）。
