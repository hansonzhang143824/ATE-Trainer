# 迁移后衔接核查报告 — 脚本在新工作区的可运行性断点（已按方案 A 修复）

- 核查日期：2026-09-02（核查 + 修复同日完成）
- 范围：`scripts\` 全部 50+2 脚本 + `scripts\schematic_parse\` 流水线
- **修复状态：✅ 方案 A 已执行完毕，全部断点已适配并逐项验证通过**（下述断点清单即修复清单）

## 核心机制（先理解这个再看断点）

`proj_config.py` 的路径基准规则：
- `cfg['_root']` = **project_config.json 所在目录**（`root = os.path.dirname(config_path)`）
- config 内所有**相对路径**（`Project/DALI/...`）都以 `_root` 为基准解析
- 原 CLAUDE_PROCESS 布局：`project_config.json` 在 **workspace 根**（与 gen_*.py 同级）→ `_root` = CLAUDE_PROCESS 根 → `Project/DALI` 等相对路径正确
- 迁移后：config 被复制到 `scripts\` → `_root` = `ATE-Coding-Platform\scripts` → 相对路径全部错位

同时脚本对 workspace 布局有一批**隐式假设**（自身位置上溯 N 级找根、`_root` 下找 `.claude\` 等），迁移后层级变化导致假设失效。

## 断点清单

| # | 脚本 | 位置/行为 | 期望（原布局） | 实际（新布局） | 断 |
|---|---|---|---|---|---|
| 1 | **全部 20+ 个 import proj_config 的脚本** | config 相对路径以 `_root` 为基准 | `_root`=CLAUDE_PROCESS 根 | `_root`=`scripts\` | ✗ |
| 2 | `gen_source_path.py` L121 | `MAP_PATH = Path(__file__).parent / 'Project'/'DALI'/...` | `CLAUDE_PROCESS\Project\DALI` | `scripts\Project\DALI`（实际在 `project\DALI`） | ✗ |
| 3 | `schematic_parse\scripts\sch_parse.py` L12 | `_WS_ROOT` 上溯两级 | `<ws>\schematic_parse\scripts` → `<ws>` | `scripts\schematic_parse\scripts` → `scripts\`（proj_config 恰好在此可导入，但 config 基准=scripts\） | △ |
| 4 | `schematic_parse\scripts\csv_schematic_adapter_v2.py` L514-521 | `workspace = package_dir.parent`；默认 `workspace/'Project'/'DALI'` | `<ws>` | `scripts\schematic_parse`（又偏一层） | ✗ |
| 5 | `schematic_parse\scripts\csv_pathproof_v2.py` L292-298 | `workspace = package.parent`，默认 `workspace/'Project'/'DALI'` | `<ws>` | `scripts\schematic_parse` | ✗ |
| 6 | `schematic_parse\scripts\run_hardware_parse.py` L28-35 | `workspace = parents[2]`；`package = ws/'schematic_parse'`；`config = ws/'project_config.json'`；`out_dir = ws/'Project'/'DALI'` | `<ws>` 及根下各项 | `workspace`=`scripts\`（package/config 碰巧在 scripts\ 能找到，out_dir 断） | △ |
| 7 | `verify_material_receipt.py` L142 | `refs_root = cfg['_root']/'.claude'/'references'` | CLAUDE_PROCESS 根下 .claude | `scripts\.claude\references`（实际在 `knowledge\references`） | ✗ |
| 8 | `verify_merge_rules.py` L12-14 | `PROJ = _root`；`RULES = PROJ/'.claude'/'knowledge'/'standards'/...`；`LOG = PROJ/'merge_log.md'` | 根下 .claude + 根下 merge_log | `scripts\.claude\...`（实际 `knowledge\standards`）；merge_log.md 未迁 | ✗ |
| 9 | `verify_library_status.py` L70-71 | `root = _root`；`root/'Library-Functions'/'sub_func'` | 根下 Library-Functions | `scripts\Library-Functions`（实际 `code\Library-Functions`） | ✗ |
| 10 | `verify_i2c_sv.py` L5-6 / `verify_tm206_425.py` L5 | 硬编码 `D:\Newtest\CLAUDE_PROCESS\Project\DALI\AI.cpp` + reg_config | 指向旧 CLAUDE_PROCESS | CLAUDE_PROCESS 仍在 → 文件可寻，但 AI.cpp 已弃用（吸收记录已知待办） | △ |
| 11 | `schematic_parse\_archive\*.py`（3 个） | `parents[2]` + `Project/DALI/hardware_parse_v2` | 历史一次性脚本 | 全断（但属 _archive 历史，可不修） | ○ |

## 修复动作记录（2026-09-02，方案 A）

| # | 文件 | 修复 |
|---|---|---|
| 1 | `project_config.json` | 从 `scripts\` 移回 **workspace 根** `ATE-Coding-Platform\`（config 相对路径基准 = config 所在目录，必须与脚本的"根"同层）；相对路径 `Project/DALI` 统一改为小写 `project/DALI`（与磁盘实际目录一致） |
| 2 | `scripts\proj_config.py` | `_DEFAULT_CONFIG` 增加上溯查找：自身目录无 config 则逐级向上找 `project_config.json`（覆盖"脚本在 scripts\、config 在根"的新布局） |
| 3 | `scripts\verify_material_receipt.py` L142 | `cfg['_root']/'.claude'/'references'` → `cfg['_root']/'knowledge'/'references'` |
| 4 | `scripts\verify_merge_rules.py` L13 | `.claude/knowledge/standards/merge_rules.md` → `knowledge/standards/merge_rules.md` |
| 5 | `scripts\verify_library_status.py` L71 | `Library-Functions/sub_func/...` → `code/Library-Functions/sub_func/...`（2026-09-02 随 Library-Functions 归位顶层，改回 `root/Library-Functions/sub_func/...`，与源一致） |
| 6 | `scripts\gen_source_path.py` L121+ | MAP_PATH 改为经 `proj_config` 读 `intermediates.sch_connect_map`（不再 `__file__` 相对） |
| 7 | `scripts\schematic_parse\scripts\csv_schematic_adapter_v2.py` | workspace 推导改 `_workspace_root()`（上溯找 config 所在目录 = workspace 根） |
| 8 | `scripts\schematic_parse\scripts\csv_pathproof_v2.py` | 同上 + `load_cbit` sys.path 双候选（根 + `workspace/scripts`，因 gen_cbit_defines.py 现位于 scripts\） |
| 9 | `scripts\schematic_parse\scripts\run_hardware_parse.py` | `package` = `parents[1]`（scripts\schematic_parse）、`scripts_root` = package.parent、`workspace` = 上溯 config 根；gen_path_defines/gen_cbit_defines 改走 scripts_root |

## 修复验证结果（全部通过）

- `proj_config.load()`：`_root` = `D:\Newtest\DSH\ATE-Coding-Platform` ✓；全部 9 个 config 键（dft/csv_schematic/cbit/channelmap/relay_definitions/treg/map/meta/test.cpp）exists=True ✓
- 13 个 import proj_config 的脚本（check_*/gen_*/verify_*）import 冒烟全 OK ✓
- `verify_material_receipt.py --audit-rules`：与源 CLAUDE_PROCESS 行为**逐字一致**（同报 PSM_THREHOLD/VC_CLAMP_LOW/VC_OFFSET 漏检 = 迁移前既有业务待办，非迁移引入）✓
- `verify_merge_rules.py`：PASS（与源一致 MR-000）✓
- `verify_library_status.py`：PASS（36 文件扫描）✓
- `gen_source_path.py --demo`：12 demo 全链路输出正常 ✓
- schematic_parse 三脚本 import OK + `_workspace_root()` 正确解析 ✓
- 真实工程依赖链（`D:\PROJECT6-DALI\devel\source\test.cpp / StdAfx.h / NU1201.treg`）经绝对路径全部命中 ✓

## 仍有效的部分（无需处理）

- `project_config.json` 中**绝对路径**：`D:/PROJECT6-DALI/devel/source/...`（channelmap/relay_definitions/vs_src_dir/treg）→ 真实编译工程未迁移、仍在原处 → **全部有效** ✓
- `scripts\` 内脚本相互 import proj_config：proj_config.py 与被导入脚本**同目录** → 导入本身成功 ✓
- Windows 大小写不敏感：config 写 `Project/DALI`、实际目录 `project\DALI` → 文件系统层可互通，大小写不是问题

## 遗留注意（修复后仍存在，非迁移引入）

1. `verify_i2c_sv.py` / `verify_tm206_425.py` 硬编码 `D:\Newtest\CLAUDE_PROCESS\Project\DALI\AI.cpp` + reg_config——AI.cpp 已弃用（吸收记录 #42 已知待办），指向旧 CLAUDE_PROCESS（源仍在故可寻，但脚本本身待迁移到 test.cpp 或归档）
2. `schematic_parse\_archive\*.py`（3 个历史一次性脚本）parents 推导未修——属 _archive 历史，不再使用
3. `verify_material_receipt.py --audit-rules` 报 PSM_THREHOLD/VC_CLAMP_LOW/VC_OFFSET 参数类型漏检 = 迁移前既有业务待办（与源 CLAUDE_PROCESS 行为一致），需在源/新工作区同步补 requirements
4. 真实编译工程 `D:\PROJECT6-DALI\devel\source\` 未迁移（在 CLAUDE_PROCESS 之外）；新工作区脚本经绝对路径直读该工程（需该工程保持可用）
5. 源 CLAUDE_PROCESS 依用户铁律永久保留（只 copy 未删），新旧两套脚本并存——改脚本时注意两边同步

## 结论

✅ 迁移后衔接适配（方案 A）已完成并验证：config 归位根 + proj_config 上溯查找 + 6 处路径引用修正 + schematic_parse 三脚本 workspace 推导重写。**新工作区 `scripts\` 下的工具链现在可按原用法直接运行**（读新 `project\` 输入、新 `knowledge\` 规则库，直连 `D:\PROJECT6-DALI` 真实工程）。
