# 吸收记录 #29 — codex V2 硬件解析脚本技术提取（subagent 只读，供补 V2 skill 文档）

- 源文件：`sessions/29-agent-a5.md`（292 行，全文）← `~/.claude/projects/subagents/agent-a509ec6146664b766.jsonl`
- 时间：2026-08-23 15:14 → 15:16（0.2MB）；用户 1 条 / 助手 2 段 / 工具 4 次
- 主题：精确提取 `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\` 四个脚本的技术细节（V2 skill 文档全是 2~4 行空壳，需据此补正文）

## 四个脚本的精确技术要点

1. **csv_schematic_adapter_v2.py（656 行）**：
   - REQUIRED_COLUMNS 恰好 25 列（SheetPath/RecordType/RecordKey/NetName/MemberType/MemberName/Designator/ComponentUniqueID/MemberUniqueID/ComponentKind/LibraryReference/PartID/PinNumber/PinName/Electrical/Relation/EndpointStatus/ObservedNetCount/ObservedNets/EffectiveShortNetCount/EffectiveShortNets/DanglingEndpointCount/DanglingNets/Status/RawID）；RecordType 仅 NET_MEMBER/NET_TIE_ENDPOINT/NET_TIE_GROUP；检测 %TSD-Header-###%/TSZ# 加密容器报错。
   - Dali-SCH compact 归一化（PIN 行按 PinNumber/PinName 数字判断顺序）；**PinNumber/PinName 互换处理**（IC 符号可能把符号脚放 PinNumber，取数字字段保拓扑）；匿名 PORT 忽略；PORT 角色：Electrical=OUTPUT→DUT；I/O 且匹配 `^.+_[FS]_S\d+$` 非 Sx_ 前缀→归一 OUTPUT（Kelvin 式 DUT 端），否则 INOUT=源表（slot 源总以 S<slot>_ 开头）；`S3_FOVIe_`→`S3_FXVIe_PLUS_` 语义别名。
   - infer_cell：^K\d+_ 且脚数/脚名超出 {1,2}/{COMMON,NO} → G6K 否则 SW_SPST；CAP→Cap/R→Res2/D→D_Schottky/TP→TEST_POINT_SMALL。
   - NET_TIE_GROUP 并集合并（零欧姆等效不造继电器）；singleton relay net/intentional open net（TP_/NC）删除。
   - write_synthetic_edif 合成网表 → `Project/DALI/CSV_CONNECTIVITY_V2.NET`（放 sch_confirmed.json 旁复用人工审过的 per-project exceptions）；规范网络命名优先 net_labels；配置写成 `project_config.v2.json.txt` 文本后缀（防自动加密）；absolutize_config_paths 文档化路径字段集；legacy 引擎 subprocess 调用；compare_migration 抽 `Relay-`/`←`/`CH\d+ High|Low` 行与 legacy map Counter 差集；状态机 PASS / PARSER_PASS_REVISION_DELTA_APPROVED（approved_revision_delta.v2.json.txt 三字段）/ PARSER_PASS_COMPARISON_FAIL(exit 2) / PARSER_FAIL。
2. **csv_pathproof_v2.py（349 行）**：硬编码源表 token（顺序即优先级）ACM200/FXVIe_PLUS/FXVIe/FPVIe/QTMU/QVM + `^S(?:24|9)_P\d+$`→DCM + `^S10_CH\d+_[AB]$`→QTMU；FH/FL→F、SH/SL→S、`CH(\d+)([+-])`→F/S、`_P(\d+)$`→F；FH/SH/+→HIGH、FL/SL/-→LOW；QVM pair_domain 强制空。G6K 转换：NC {2:(3,),3:(2,),7:(6,),6:(7,)}、ON {3:(4,),4:(3,),6:(5,),5:(6,)}；MOS 1↔2。BFS max_depth 6、**DUT PIN 到达即停止**（PATH_CONTRACT terminal）、bus 域剪枝（FH_BUS/SH_BUS/FH_PC/SH_PC→HIGH）、scarce 源（FPVIe/QTMU/QVM/CH0）豁免；Kelvin F/S 角色匹配（任一空即放行，F≠S → KELVIN_ROLE_CROSS 拒绝）；F/S 配对取最短、共享继电器状态冲突→FAIL；CBIT 缺失→MISSING_CBIT。契约：dut_pin_is_terminal/kelvin_force_sense_no_cross/shared_relay_state_must_match/cbit_traceability_required 全 True。输出 path_proofs.v2.json.txt + PATHPROOF-VALIDATION.v2.txt。
3. **adapt_tm607_for_v2_hardware.py（115 行）**：作用域保护（非生产默认改 v2_dir/vs_compile_sandbox 副本，relative_to 强制；生产必须 --production --intentional-hardware-revision）；幂等检测三条件；8 条 replace_once 规则把 TM607 从"旧硬件极性"（FPVI0 High→SW1、Low→PGND）改为 **V2 新极性（FPVI0 High→PGND、Low→SW1，K_FPVIH_TO_PGND_A=K136,K137,K143,K144,K154,K155 / K_FPVIL_TO_SW1_A=K47）**，ramp 电流 0.2→-0.2 对调、结果取负（`if (ls_zcd[site] != ERROR_RES) ls_zcd[site] = -ls_zcd[site];`）；残留 K_FPVIL_TO_PGND → RuntimeError；生产先备份 Backup/test.cpp.before_hardware_parse_v2_*.bak。
4. **prepare_v2_compile_sandbox.py（136 行）**：复制过滤（IGNORED_DIRS Backup/debug/Debug/Release/.vs/ipch；IGNORED_SUFFIXES .obj/.pdb/.ilk/.pch/.tlog）；沙箱必须位于 v2_dir 下；copytree vs_src_dir/vs_project + treg copy2；沙箱 config 重写 vs_project/channelmap/vs_src_dir/treg/resource_definitions/relay_definitions → `project_config.v2.compile.json.txt`；**防污染**：不写生产 VS 树/生产 config；manifest 记录 mode=isolated_compile_validation + production_vs_modified:False + baseline_hashes（生产/沙箱 StdAfx.h、test.cpp 各自 sha256 可对比证明生产未被改动）。

## 关键结论

- V2 = **CSV→合成 EDIF→复用 legacy 六门控引擎**的桥接方案，配合 PathProof 原生证明 + 沙箱隔离编译 + 迁移比对状态机——技术细节完备可直接写 V2 skill 文档正文。
- TM607 极性适配揭示了 **V2 硬件拓扑与 legacy 相反**（High/Low 对调）——硬件版本差异的具象案例。

## 涉及文件

- 只读 CODEX 四个脚本（D:\Newtest\CODEX\_PROCESS\...\scripts\）。零修改。

## 交叉引用

- 与 #20 CSV 复刻评估（同 25 列 unified CSV）互为印证：CSV 方案实际已在 CODEX 侧落地为 V2 引擎；#30 报告 skill 2.0 引用 `run_hardware_parse.py --engine v2`；TM607 极性适配呼应 #20 TM607-609 写码（legacy 极性）。

## 未决问题

- V2 skill 文档是否被补齐、V2 是否替换 legacy 为生产默认（CODEX _PROCESS 与 CLAUDE_PROCESS 两工作区的关系待 #34 厘清）。
