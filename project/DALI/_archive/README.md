# _archive — Project/DALI 收敛（2026-08-25）

> 本目录收纳 Project/DALI 根目录的历史杂项，移出后不参与生产管线。如需恢复，从这里移回即可。

## 内容分类

| 类别 | 数量 | 说明 |
|------|------|------|
| `_dump_*` 调试转储 | 14 | Excel 各 sheet 的调试 dump（2026-08-06 前后），已被生产脚本取代 |
| `.bak_*` 备份 | 9 | 历史备份（unify_k7 / unify_busl / pathrule 等节点） |
| 一次性生成脚本 | 10 | append_tm105/108、gen_final/gen_paths/gen_v8/phase2_singlepoint（DALI 内旧副本，权威版在 workspace 根）、debug_trace、replace_ramp_library、_verify_vbat_path、_tm607_608_609_new.cpp |
| 早期中间产物 | 3 | phase1_nets.txt / phase1_parsed_data.txt / phase2_singlepoint_output.txt |
| 设计文档 | 1 | design_tm403-425.md（TM403-425 已完成，留档） |

## 保留（未移入）

生产管线仍在用：`Dali-SCH.csv`(原理图 CSV)、`CBIT表-DALI.xlsx`(CBIT 表)、`Dali_testmode.xlsx`(DFT)、`DALI_Net.NET`(电容值源)、`sch_confirmed.json`(用户确认例外)、`sch_parse.py`(解析引擎)、`SCH-Connect-Map.txt`/`COMPONENT-STATISTIC.txt`(产物)、`CSV_CONNECTIVITY.NET`/`path_proofs.json.txt`/`PATHPROOF-VALIDATION.txt`/`validation_manifest.json.txt`/`strict_gate_run.log`(管线中间产物)、`通路规则实现方案.md`(已批准方案)。
