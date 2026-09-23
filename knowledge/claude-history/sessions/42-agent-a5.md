# 会话 #42 — 在工作区 `D:\\Newtest\\CLAUDE_PROCESS` 下盘点全部脚本，用于写一份"ATE Offline Coding 工作流架构"文档（需要列出每

- 文件：`agent-a5d7ebe517ed12cef.jsonl`（项目 subagents）
- 时间：2026-08-26T13:15:43.858Z → 2026-08-26T13:17:12.309Z，大小 0.4 MB
- 用户消息 1 条 / 助手文本 12 段 / 工具调用标记 70 行

---

## 对话正文（工具输出已剥离）

### 2026-08-26 13:15:43 [user]

在工作区 `D:\Newtest\CLAUDE_PROCESS` 下盘点全部脚本，用于写一份"ATE Offline Coding 工作流架构"文档（需要列出每阶段调用的脚本）。

请做：
1. 用 Glob 搜索以下位置的 `.py` 和 `.ps1` 文件：
   - `D:\Newtest\CLAUDE_PROCESS\*.py` 和 `*.ps1`（根目录，排除 `_archive\`、`_bak*`、`_stub*`）
   - `D:\Newtest\CLAUDE_PROCESS\schematic_parse\**\*.py`（含 scripts 子目录）
   - `D:\Newtest\CLAUDE_PROCESS\Project\DALI\*.py`
   - 其他散落在 `库函数\` 下与工具链相关的 .py
2. 对每个脚本，读文件开头（docstring / 前 40 行 / argparse 部分）提取：**文件名、一句话用途、关键输入参数/文件、关键输出文件、属于哪个工作流环节（codegen 门禁 / 上电下电 / cbit / 通路 / 原理图解析 / 编译部署 / 自进化审计 / meta 校验）**。可从脚本名和 argparse 推断，不必逐行读全文。
3. 特别标注：
   - 哪些是**门禁类**（PASS/FAIL 校验，如 verify_*、check_*）
   - 哪些是**生成类**（gen_*，写代码/定义/文档）
   - 哪些是**流程编排类**（如 run_hardware_parse.py、compile.ps1、fast_rebuild.ps1、auto_sts8300.py）
   - 是否提到 `gen_knowledge_audit.py`（标记为待建）或任何标注"待建/⏳"的脚本
4. 读 `schematic_parse\scripts\` 目录（如果存在）下的脚本。

输出为结构化清单，按工作流环节分组，中文回答。每个脚本一行要点即可，重点是"输入→输出"和"归属环节"。

### 2026-08-26 13:15:45 [assistant]

我先并行搜索各目录下的脚本文件。
- [tool] Glob
- [tool] Glob
- [tool] Glob
- [tool] Glob
- [tool] Glob

### 2026-08-26 13:15:49 [assistant]

Project\DALI 根目录无 .py（都在 meta/ 子目录）。我再看一下目录结构和 `库函数\` 下的更多内容。
- [tool] Bash
- [tool] Bash
- [tool] Glob

### 2026-08-26 13:15:56 [assistant]

现在批量读取各脚本头部。先读根目录的生成/校验/门禁类脚本。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:15:59 [assistant]

继续读 verify_* 门禁脚本和 schematic_parse 脚本。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:03 [assistant]

读 schematic_parse\scripts、DALI\meta 及 .ps1 脚本。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:07 [assistant]

读 .ps1 脚本和 STS8300/UI 自动化脚本，同时检索 gen_knowledge_audit 及待建标记。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:11 [assistant]

检索 gen_knowledge_audit、待建标记，并快速读 STS8300/UI 辅助脚本。
- [tool] Grep
- [tool] Grep
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:15 [assistant]

读剩余的 spy/记录脚本，以及工作流全景文档以对齐环节定义。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:19 [assistant]

最后确认一下 schematic_parse 目录结构、daylog/_test/backup 中是否有散落脚本，以及 _archive 里是否有被引用为活跃的脚本。
- [tool] Bash
- [tool] Grep

### 2026-08-26 13:16:24 [assistant]

快速看 run_hardware_parse.py 的编排后半段和 _archive 中脚本头部，确保归类和输入输出完整。
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 13:16:28 [assistant]

最后读 project_config.json 确认各脚本引用的输入输出路径。
- [tool] Read

### 2026-08-26 13:17:12 [assistant]

盘点完成。以下是 `D:\Newtest\CLAUDE_PROCESS` 下脚本的结构化清单，按工作流环节分组。

---

# ATE Offline Coding 工作流脚本盘点

> 全局说明：`project_config.json` 是唯一输入入口（脚本默认读它，`--config` 可覆盖）；`proj_config.py` 是所有脚本共用的配置读取器。DLP 加密文件（test.cpp/StdAfx.h/Excel）均用字节模式读写。主 pipeline 原则为「推理→agent，固定→脚本」。

## 0. 公共基础

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `proj_config.py` | 配置库 | `project_config.json` 统一读取器，派生 vs_src_dir 下 test.cpp/sub.cpp/StdAfx.h 绝对路径 | 读 `project_config.json` → 各脚本的 cfg 字典 |
| `project_config.json` | 配置 | 唯一输入清单（inputs/intermediates/outputs），换项目只改它 | — |

---

## 1. 原理图解析（sch-parse 环节）

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `schematic_parse\scripts\csv_schematic_adapter_v2.py` | 生成 | **唯一生产管线**：读 Altium CSV 校验 schema → 物化合成 EDIF | `Dali-SCH.csv` → `CSV_CONNECTIVITY.NET`（合成 EDIF） |
| `schematic_parse\scripts\sch_parse.py` | 生成+门禁 | 原理图解析六任务门控流程；任一任务 FAIL 即停，不生成 map（`--force` 继续） | `CSV_CONNECTIVITY.NET` + `sch_confirmed.json`(用户确认短接) → `COMPONENT-STATISTIC.txt` + `SCH-Connect-Map.txt` |
| `schematic_parse\scripts\csv_pathproof_v2.py` | 门禁 | 原生 CSV 图 PathProof 校验器（哈希冻结，防原理图漂移） | `CSV_CONNECTIVITY.NET` → `path_proofs.json.txt` |
| `schematic_parse\scripts\run_hardware_parse.py` | 流程编排 | **ATe hardware parse action**：串行调用 adapter→pathproof→gen_path_defines→gen_cbit_defines（`--publish-definitions` 发布 StdAfx.h） | 上述各脚本链式执行 → 输出全部 canonical 产物 |

---

## 2. meta 校验（DFT 意图层 / TestItemMeta）

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `gen_testitems_meta.py` | 生成 | TestItemMeta 生成器（纯 DFT 派生，不碰原理图），产出 capAuthority 四权威集 | OVERVIEW xlsx + test.cpp + StdAfx.h → `meta\dali_tm_meta.json` |
| `check_testitems_meta.py` | 门禁 | meta 覆盖完整性收尾门：`--require-all`(正向) / `--require-scope`(反向)，任一 FAIL exit 1 | meta json + test.cpp + OVERVIEW → PASS/FAIL |
| `Project\DALI\meta\append_tm.py` | 生成 | 将 gen_tm000_102.cpp 的 7 个 TM 函数追加到 DALI test.cpp（保 UTF-8 BOM+CRLF，幂等） | `meta\gen_tm000_102.cpp` → `D:\PROJECT6-DALI\devel\source\test.cpp` |
| `Project\DALI\meta\check_tm.py` | 门禁 | TM000~102 codegen 标识符检查：生成代码所有大写标识符须在 DALI 工程已定义（编译通过前置） | `gen_tm000_102.cpp` vs `D:\PROJECT6-DALI\devel\source\*.h/*.cpp` → PASS/FAIL |
| `Project\DALI\meta\find_fpvi.py` / `find_fpvi2.py` / `find_fpvi3.py` | 工具/调查 | 搜/提取 `fpvi_gp_valid` 在 DALI / 工厂 / SDK 的声明与定义体 | 源码目录 → 命中位置打印 |

---

## 3. cbit 环节

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `gen_cbit_defines.py` | 生成+门禁 | CBIT 单点继电器 #define 生成器 + V1~V8 校验器；`--verify` 对拍基准文件 | `CBIT表-DALI.xlsx` + `COMPONENT-STATISTIC.txt` + `SCH-Connect-Map.txt` → relay.h 单点 #define 块 + 校验报告 |

---

## 4. 通路环节（path / relay）

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `gen_paths.py` | 生成 | 源表→DUT Pin 通路生成器（path-finder 脚本化，BFS 追踪 + 稀缺源识别）；`--json` 输出结构化 path_list | Netlist(.NET/合成 EDIF) + CBIT 表 xlsx → 通路文档 + path_list |
| `gen_path_defines.py` | 生成 | 从 SCH-Connect-Map 解析 SetOn 通路 → 生成 2.x 通路段追加到 StdAfx.h；`--no-write/--verify/--check-relay` | `SCH-Connect-Map.txt` → StdAfx.h 2.x 通路段 |
| `gen_relay_role_defines.py` | 生成 | 列11 角色继电器定义生成器（稳压/P2P/短路/上拉/下拉）→ 幂等插入 StdAfx.h RELAY_ROLE 段 | `SCH-Connect-Map.txt` 列11 → StdAfx.h 角色 #define |
| `verify_relay_trace.py` | 门禁 | 继电器轨迹核对（闭环/功能/结构三层），Step1 必须有 SetOn；E 权威源 = meta capAuthority | test.cpp + StdAfx.h + SCH-Connect-Map + meta → PASS/FAIL |

---

## 5. 上电/下电环节

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `gen_power_sequence.py` | 生成 | 上电/下电代码生成器（R-PON/R-POFF 固定模板规则落地）；stdout 三段式 section 供主 Skill 拼装 | TestItemMeta json + pin-map + `Pin_Channel_define.h` → POWER_ON / POWER_STATE / POWER_OFF 代码段；`--verify` 对拍基准 cpp |

---

## 6. codegen 门禁（收尾双查 + 各 verify）

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `verify_single_fn.py` | 门禁 | 单函数冒烟自检（步骤14第一层，秒级免编译）：7 项检查（占位符/花括号/CRLF/Step1-6/lifecycle/reg unlock） | test.cpp + `--fn` → PASS/FAIL |
| `verify_awg_params.py` | 门禁 | AWG/Toggle 参数检查：ramp 必须 3 参数 `<基名>_Rise/_Fall/_Hys`，`--strict-params` 加查数值 | test.cpp → PASS/FAIL（WARN 不阻断） |
| `verify_bst_sw_sequence.py` | 门禁 | BST-SW 台阶黄金约束门（R-BST-SW）：目标函数由 meta capAuthority 拓扑指纹派生，验 HS/LS 台阶 + 量程 + 寄存器 | meta + test.cpp → PASS/FAIL |
| `verify_i2c_sv.py` | 门禁 | AI.cpp 新批次 I2CWriteSameData 与 `reg_config\tm*.sv` verbatim 一致性 | AI.cpp vs reg_config/*.sv → PASS/FAIL |
| `verify_tm206_425.py` | 门禁 | AI.cpp TM206~425 批次验证（花括号平衡 / AFX 参数对 / 函数数） | AI.cpp → PASS/FAIL |
| `verify_material_receipt.py` | 门禁 | **材料声明门（生成前拦截）**：按 param_type_index 校验 receipt 声明的 chip/method/code 材料覆盖参数类型 | `material_receipts.json`(--receipt) + param_type_index → PASS/FAIL |
| `verify_merge_rules.py` | 门禁 | 合并纪律检查：merge_log.md 与 merge_rules.md 一致性（M001~M004） | merge_log.md + merge_rules.md → PASS/FAIL |
| `verify_library_status.py` | 门禁 | 阻止含 TODO/恒成功桩的共享库进正式 VS 工程：生产工程引用 + 桩方法联动判 FAIL | `库函数\sub_func` + vs_src_dir → PASS/FAIL |

> 注：`verify_i2c_sv.py` / `verify_tm206_425.py` 均指向 `AI.cpp`，但文档标注 AI.cpp 已弃用，主路径改走 `test.cpp`（见 verify_relay_trace/verify_single_fn）。

---

## 7. 编译/部署环节（compile / deploy）

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| `compile.ps1` | 流程编排 | 完整 VS 编译部署：找 sln→toolset 检查(v→v120)→MSBuild Rebuild→COM Debugger.Go()→等 testui.exe 启动 | 工程路径 → Release/Debug DLL + 运行 Debugger |
| `fast_rebuild.ps1` | 流程编排 | 快速命令行构建（替代慢 IDE Rebuild）：先 COM SaveAll 保存 VS 文档→MSBuild Build/Rebuild | 工程路径/-Config/-Platform/-Incremental → 编译结果 |
| `Project\DALI\meta\dte_rebuild.ps1` | 流程编排 | COM 触发已运行 VS IDE Rebuild Solution + 轮询 F12011.dll 重建（最长300s） | 已运行 VS → DLL 重建确认 |
| `Project\DALI\meta\dte_buildcheck.ps1` | 诊断 | 综合验证 VS 构建状态：DLL 时间戳 / devenv 进程 / 输出窗口面板 | — |
| `Project\DALI\meta\dte_read_buildlog.ps1` | 诊断 | 只读 VS 输出窗口 Build 面板日志（尾部4000字符） | — |
| `auto_sts8300.py` | 流程编排 | **STS8300 Deploy Agent 全自动**：Launch→Login→VC Project→VS→Build→F5，状态检测 0-4 跳过已完成步 | PGS_PATH/PGS_NAME → 打开 STS8300 + VS + 运行 |
| `start_sts8300.py` / `run_sts8300.py` | 流程编排 | 启动 STS8300 软件 / 启动+载入工程+打开 VS Project | — |
| `diag_sts8300.py` | 诊断 | 检查 control.exe 进程 + pywinauto 窗口结构 | — |
| `click_vcproject.py` | 工具 | 点击 STS8300 Control 界面「VC Project」按钮 | — |
| `spy_control.py` / `spy_login.py` / `spy_vcproject.py` / `spy_click.py` / `spy_popup.py` / `spy_vs_status.py` | 侦查/调试 | 侦查 STS8300/VS 登录框/打开对话框/控件树/弹窗/VS 状态栏窗口结构（人工 UI 自动化开发用） | — |
| `record_actions.py` / `replay_actions.py` | 工具 | 录制鼠标键盘操作到 json / 按 json 回放（F8 录制，ESC 退出） | 操作 → `recorded.json` / 回放 |
| `input_guard.py` | 工具/库 | 自动化期间低级钩子屏蔽用户键鼠（ESC 中止），被 auto_sts8300.py 依赖 | — |

---

## 8. 自进化 / 知识审计环节

| 脚本 | 类型 | 一句话用途 | 输入 → 输出 |
|---|---|---|---|
| **`gen_knowledge_audit.py`** | **待建 ⏳** | **知识完整性审计脚本**（ID 连续/无重复、active 有强制层、反向引用可查、来源清单对照）。**当前无实体文件**，仅出现在文档中（`工作流全景.md` / `工作流Action清单.html` / `ATE_Offline_Actions_*.html` / `CODEX迁移评审*.md`），执行顺序第 5 步，P2 优先级 | 三注册表(rules-registry/param_type_index/functions-registry) + references → 审计报告 |
| `库函数\test_method\gen_ramp64.py` | 生成 | 生成 Test_Method 库 64 个 ramp-capture 函数（4类型×4 ramp×4 cap），DLP 字节模式写回 | `Test_Method.h/.cpp` → 拼接生成新函数体写回 |

---

## 9. 归档区（`_archive`，非活跃，供参考）

- **根目录 `_archive\`**：`patch.py`（UI 脚本补丁）、`_add_measure_osc.py`、`_sync_tm300_301_gen.py`、`_rename_trim_node.py`、`_fix_tm300_301.py`、`gen_insert_tm403_425.py`、`gen_tm206_425.py`、`extract_stdafx_from_transcript.py`、`restore_stdafx.py`
- **`Project\DALI\_archive\`**：`append_tm105_107.py`、`append_tm108_112.py`、`replace_ramp_library.py`、`debug_trace.py`、`gen_paths.py`、`gen_final.py`、`gen_v8.py`、`phase2_singlepoint.py`、`_verify_vbat_path.py`（多为旧版生成器快照，含 `.bak_*`）
- **`schematic_parse\_archive\`**：`adapt_tm607_609_bst_sw.py`、`adapt_tm607_for_v2_hardware.py`、`prepare_v2_compile_sandbox.py`

另外根目录还有一批 `.bat` 启动器（`auto_sts8300.bat`、`run_sts8300.bat`、`run_spy*.bat`、`spy_*.bat`、`run_record/run_replay/replay_manal.bat`、`find_python.bat`），只做 Python 调用入口，不属 pipeline 核心。

---

## 关键标注汇总

- **门禁类（PASS/FAIL 校验）**：`check_testitems_meta.py`、`verify_relay_trace.py`、`verify_single_fn.py`、`verify_awg_params.py`、`verify_bst_sw_sequence.py`、`verify_i2c_sv.py`、`verify_tm206_425.py`、`verify_material_receipt.py`、`verify_merge_rules.py`、`verify_library_status.py`、`csv_pathproof_v2.py`、`sch_parse.py`（门控）、`gen_cbit_defines.py --verify`、`meta\check_tm.py`
- **生成类（gen_*，写代码/定义/文档）**：`gen_testitems_meta.py`、`gen_power_sequence.py`、`gen_cbit_defines.py`、`gen_paths.py`、`gen_path_defines.py`、`gen_relay_role_defines.py`、`csv_schematic_adapter_v2.py`、`meta\append_tm.py`、`库函数\test_method\gen_ramp64.py`
- **流程编排类**：`schematic_parse\scripts\run_hardware_parse.py`、`compile.ps1`、`fast_rebuild.ps1`、`meta\dte_rebuild.ps1`、`auto_sts8300.py`、`start_sts8300.py`、`run_sts8300.py`
- **待建标记**：`gen_knowledge_audit.py` 在全部相关文档中被标注「⏳ 待建」（A09，P2，执行顺序第 5 步），**无实体文件**。脚本内未发现其它「待建/⏳」标注。

### 环节→脚本调用链速览（供架构图用）

```
原理图解析: csv_schematic_adapter_v2 → sch_parse → csv_pathproof_v2
           └─ run_hardware_parse.py 串行编排上面 + gen_path_defines + gen_cbit_defines
meta:      gen_testitems_meta → check_testitems_meta (+ meta\check_tm 前置)
cbit:      gen_cbit_defines (P1 #define + P4 V1~V8)
通路:      gen_paths → gen_path_defines → gen_relay_role_defines → verify_relay_trace
上电下电:  gen_power_sequence (Step5/Step8)
codegen门禁: verify_material_receipt(前置) → verify_single_fn → verify_awg_params
            → verify_bst_sw_sequence → verify_relay_trace → check_testitems_meta
编译部署:  fast_rebuild.ps1 / compile.ps1 / dte_rebuild.ps1 / auto_sts8300.py
知识审计:  gen_knowledge_audit.py (⏳ 待建)
```

所有脚本均位于 `D:\Newtest\CLAUDE_PROCESS\` 下（绝对路径如上表各 `file_path`）。
