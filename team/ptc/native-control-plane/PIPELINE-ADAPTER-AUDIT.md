# 完整训练流水线真实适配器调查

日期：2026-09-22。调查范围：只读代码、配置、工程与依赖；未启动专家、未编译、未执行硬件、未改生产脚本或正式项目。本文区分已经存在的实现与下一步必须实现的适配器。

## 结论

角色映射有确定证据，完整阶段引擎已经具备可注入接口；但现有生产 gate 不能只替换 `--trial-dir` 就直接用于训练。INPUT_SYNC、METHOD REVIEW 仍使用生产全局目录，STRATEGY 仍读取根 `Project_Info.json` 指向的正式 VS 头文件，寄存器提取脚本固定读取生产 `reg_config`。COMPILE 包装脚本有额外副作用：会保存正在运行的 VS 中所有文档，并可能修改项目 toolset。

因此应先补一套显式 run context 的训练命令适配器、完整材料/工程快照以及按训练回执识别的工具守卫，再连接真实 DSH 子会话。现在把注入回调的测试通过解释为“完整真实专家流水线已打通”是不准确的。

## 1. Registry owner 到 profile 的确定映射

权威阶段与 owner 来自 `team/ptc/ptc_stage_registry.json`。profile 命名转换的既有证据是 `scripts/validate_expert_roster.py:26` 的 `OWNER_PROFILE`，同时由各草稿 `profile.yaml` 的 `ownerRole` 交叉确认。

| Registry 阶段 / source role | Registry owner / source role | 现有 profileId | 关键证据 |
|---|---|---|---|
| INPUT_SYNC 内 DFT | dft-expert | ptc-dft-expert | `validate_expert_roster.py:28` |
| INPUT_SYNC 内原理图 | schematic-expert | ptc-schematic-expert | `validate_expert_roster.py:29` |
| STRATEGY | test-strategy-architect | strategy-expert | `validate_expert_roster.py:30`；`team/expert-profiles/strategy-expert/profile.yaml:7` |
| METHOD | test-method-expert | method-expert | `validate_expert_roster.py:31`；`team/expert-profiles/method-expert/profile.yaml:7` |
| RULE_REVIEW_METHOD | rule-reviewer | rule-reviewer | `validate_expert_roster.py:32` |
| IMPLEMENTATION | ate-implementer | ate-implementer | `validate_expert_roster.py:33`；对应 `profile.yaml:7` |
| RULE_REVIEW_IMPLEMENTATION | rule-reviewer | rule-reviewer | profile.yaml 注释明确此 profile 拥有两种 review 阶段，回执记录实际阶段 |
| COMPILE | compile-diagnostician | compile-diagnostician | `validate_expert_roster.py:34`；对应 `profile.yaml:7` |

INPUT_SYNC 的 registry owner 是 Captain，不能把两位解析专家误当成两个新阶段。`validate_expert_roster.py:10` 明确了此区别；`prepare_input_sync_v2.py:58` 的 `roleGates` 同时记录两种 source role。DFT-only 应由明确 scope 缩小 source-role 集合并停在 INPUT_SYNC，不能根据 UI 标签猜测。

现有 `plugins/dsh-ptc-material-boundary/lib/dispatch-profile.js:94` 的 `resolvePublishedProfile` 读取 `publishedVersion`，不是训练草稿装载器。真实训练不能直接调用它并声称用了草稿；应复用其回执/身份验证思路，为训练材料快照生成独立草稿身份。

## 2. 每个 gate 的路径和副作用

| 阶段 / 权威 gate | 当前路径行为 | 写入 / 风险 | 最小训练适配要求 |
|---|---|---|---|
| INPUT_SYNC：`prepare_input_sync_v2.py` | 仅接受 `--tm --trial-dir`；第 29–30 行再执行 legacy；第 38–47 行使用全局 DFT/SCH validator 与生产材料路径 | 第 65 行写指定 trial manifest，但 manifest 内容仍绑定生产输入/输出；只改变 trial 不等于训练隔离 | 输入、派生产物、ErrorLog、特殊映射、意图记录都来自 run context；禁止使用全局默认路径；执行所有 source gates 后生成 run-local manifest |
| STRATEGY：`validate_strategy_contract.py` | 合同/handoff/manifest 路径可传；第 193 行从 manifest 读取 output root；第 224–226 行却固定读取仓库根 `Project_Info.json`，进而查正式 VS header | 本体只读；第 143–145 行把寄存器路径接在仓库 ROOT；路径来自合同但没有训练目录归属检查 | 显式传入 run-local project info 或 source header；约束 register source/evidence 与 manifest 输入输出在 run 内；知识规则可读固定快照 |
| METHOD：`validate_method_contract.py` | 参数为合同路径和 `--strategy-sha`；调用 `ptc_contract_schema.validate_method_contract`；该核心做结构/语义检查 | 本体无生产目录写入，最接近可直接复用；它不独立验证所有文件路径/实际外部 source | 宿主验证传入合同路径、真实 strategy digest 和 run-local signedInputs；在原 gate 外增加路径/签名校验，不能用模型给的 hash |
| RULE_REVIEW_METHOD：`review_method_batch.py` | 第 10–11 行固定 `OUT=ROOT/project/DALI/Output_Global_Material`；第 28–30 行读取正式 schematic；第 34 行寄存器路径基于 ROOT | `--write-pass` 才写每个 trial 的三份 review/handoff/self-check；没有这个参数仅校验 | output root、source root、知识快照显式参数化；trial 必须 run-local；一次校验通过后宿主写审核产物，避免又跑一次完整门禁造成重复工作 |
| IMPLEMENTATION / RULE_REVIEW_IMPLEMENTATION：`verify_implementation_batch.py` | trials 显式传入；第 229 行直接信任 implementation manifest 的 `changes[].path`；trim 引用由 `ptc_trim_validation` 继续读取绝对 sourcePath | 本体只读；不保证 source 属于训练副本。`changes=[]` 时当前循环可输出 `PASS` 且 `checks=[]`，宿主不能把空检查当有效实现证据 | 先确保每个 TM 有非空 changes/symbols，所有 afterSha/source/trim source 均绑定 run-local VS 副本；然后执行权威 gate 并保留每 TM 实际检查 |
| COMPILE：`run_ptc_incremental_compile.py` | 接受 `--project --source --report --timeout-seconds --config`；默认 Both、10 秒 | 第 11 行调用 `fast_rebuild.ps1`，其 DTE SaveAll 与 toolset 自动修改有额外副作用；超时只终止 Python 直接子进程，不能从本实现证明 MSBuild/CL 后代全部结束 | 训练专用编译入口，禁用 DTE/IDE 保存、禁用自动改正式工程；显式项目、输出、临时目录；持有可终止整个子进程树的生命周期；每命令最多 30 秒 |

补充依赖：

- `scripts/dft_source.py:21` 固定 ROOT/project/DALI 的 input/output/error；`discover_workbook`/`discover_schematic` 还导入 `project_info` 读取正式声明。`prepare_input_sync.py:13` 继承这些全局量，`INTENT_RESOLUTIONS` 固定正式 `project/DALI/meta/intent-resolutions.json`。
- `scripts/validate_schematic_outputs.py:8` 在 import 时计算 INPUT/OUT；CLI 只有 `--source --confirmed`，没有 output root 或 cbit 路径。传两个训练输入仍会校验正式输出和正式 CBIT。须先补显式 path context。
- `scripts/extract_register_config.py:16` 固定 `ROOT/project/DALI/reg_config/<tm>.sv`；TM109 的 `project/DALI/reg_config/tm109.sv` 实际存在。应快照后传路径，保留原 source locator 与 copied-to locator，不能让模型任选替代文件。
- `scripts/write_implementation_deliverable.py:77` 又起一次 `verify_implementation_batch.py`，当前 `subprocess.run` 未设 timeout；训练适配器需要相同 30 秒预算与可取消进程树。
- `scripts/ptc_trim_validation.py:188` 直接读签名 `.treg` 与 `sub.cpp`；第 169 行检查相邻/上一级 `.vcxproj` 是否纳入 sub.cpp。训练必须保留工程相对布局并重绑路径后重新签名。
- 两个 batch reviewer 按 trial 目录末级名字推导 TM。因此建议试验路径为 `<run>/trials/tm109`、`<run>/trials/tm110`，不把 run 根直接当 TM trial，也不能把所有 TM 的 `deliverable-ready.json` 写到同一个平铺 stage 目录。

## 3. 当前确认的输入、配置和项目

`Project_Info.json` 经 Python 明文视图读取的实际值：

- 正式输入：`project/DALI/Input_GlobalMaterial`。
- 正式输出：`project/DALI/Output_Global_Material`。
- 正式错误日志：`project/DALI/ErrorLog`。
- 正式项目 source：`D:/PROJECT6-DALI/ForCodexDebug/source`。
- DFT：`Dali_testmode.xlsx`；SCH：`Dali-SCH.csv`；CBIT：`CBIT表-DALI.xlsx`。

现有训练源目录 `Training_Materials/Input_GlobalMaterial` 已包含三类材料、`sch_confirmed.json` 和 `DALI-special-information.json`。当前 `training-materials.js:130` 只快照 DFT 所需工作簿/特殊说明/解析规则及单个 DFT profile，尚未准备完整流水线材料、寄存器文件或工程。

完整训练准备阶段至少还需：SCH、确认映射、CBIT；每 TM 的已批准 `.sv`；用于 manifest 的意图记录（可空但需记录缺失，不能偷读正式 mutable 文件）；所有参与草稿 profile、合同、案例、规则和脚本身份；VS 源码与 `.spec/.treg`。输入复制必须走受保护材料的 Python 明文视图，按批准命令记录复制前后 SHA-256；生成产物按其实际落盘字节计算 SHA-256。

生成训练 `Project_Info` 应记录 `mode=training`、原批准配置来源与 digest、训练副本映射，不能伪造一次新的用户审批，也不能覆盖根正式配置。若现有 gate 只识别正式 schema，需增加训练上下文验证分支，不能靠改 `approvedBy` 绕过。

## 4. 可编译训练副本究竟复制什么

本机实际工程：`D:/PROJECT6-DALI/ForCodexDebug/source/F12011.sln`，其中第 6 行指向同目录 `F12011.vcxproj`。工程为 VS2013 / v120、Debug|Win32 与 Release|Win32、DynamicLibrary。

建议副本结构：

```text
Training_Materials/runs/<runId>/vs-project/
├─ NU1201.spec
├─ NU1201.treg
└─ source/
   ├─ F12011.sln
   ├─ F12011.vcxproj
   ├─ 所有工程参与的 .cpp/.h
   └─ src/                  # 至少 visa.h、visatype.h、visa.lib；建议完整私有副本
```

明确的项目依赖证据：

- `.vcxproj:145` 起列出 ClCompile：BoardCheck、Coutlier、diags、FMEA、inireader、F12011、Shmoo、spec、StdAfx、sub、tempchar、test、Test_Method、treg（以 XML 实际列表为准，复制器不要手工硬编码文件数）。`StdAfx.cpp` 创建 PCH，其余使用 stdafx.h。
- `.vcxproj:180`、`:181` 引用父目录 `NU1201.spec`、`NU1201.treg`，两文件实际存在，不能只拷 source 子目录后遗漏它们。
- `tempchar.h:24` 使用 `#pragma comment(lib, "src/visa.lib")`，并包含 `src/visa.h`；三份 VISA 文件都存在于 source/src。
- `.vcxproj:46`、`:51` 的 OutDir 为父目录；`:86`、`:132` 的 Link OutputFile 明确是 `..\F12011.dll`。单设 MSBuild `/p:OutDir=` 不足以证明最终 DLL 路径被覆盖，需校验/覆盖 Link OutputFile 等全部实际输出。
- `.vcxproj:47`、`:52` 的中间目录是 source/debug、source/Release；PCH/OBJ/PDB/ImportLibrary 也有显式 `$(Configuration)` 相对路径。训练副本的父目录和全部输出须处于 run 根，禁止使用指向生产的 junction、symlink、hardlink。
- 旧 source/debug、source/Release 下有已有 OBJ/PCH/tlog；为证明训练确实编译当前源码，第一轮不应直接把旧成功二进制当验证证据。若复用 build cache，必须另有工具链/完整输入/命令 binding。
- 需要复制 `.sln/.vcxproj` 与其参与源码、头文件、资源、`.spec/.treg` 和本地 VISA 依赖；不需把历史 `.bak`、旧 DLL/PDB/ILK、生产运行 `.pgs/.LDF` 全部复制进训练执行目录。

本机只读确认存在的外部构建依赖：

- `C:/Program Files (x86)/MSBuild/12.0/Bin/MSBuild.exe`。
- `C:/AccoTEST/AccoTEST System/INCLUDE`。
- `C:/AccoTEST/AccoTEST System/lIB/UserRes.lib` 和 `UserType.lib`。
- Windows/VC 系统库：项目显式 odbc32/odbccp32，源码 pragma 的 User32/Gdi32；由本机 VS/Windows SDK 提供。
- 用户 props：`C:/Users/nvt10241/AppData/Local/Microsoft/MSBuild/v4.0/Microsoft.Cpp.Win32.user.props` 当前为空的 Property/Item 分组，无额外目标；仍应在编译身份里记录其内容，因为项目 import 了它。

项目 LibraryDirectories 中还重复声明 `D:/SoftwareInstall/AccoTEST System/INCLude`，此路径本机不存在；同时有已存在的 C:/AccoTEST 路径。尚未实际编译，不能据此断言一定成功或失败。训练预检应展示实际使用的 SDK/库路径，不自动修改生产工程。

## 5. 最小安全适配器设计

1. **冻结 run 材料与草稿。** 创建独立 run identity；取 approved 配置的只读来源；用宿主复制材料、规则、profiles、registry 和 VS 项目到 run。建立完整 path manifest、源码映射和 digest。禁止使用 UI 全局模式影响已创建 run。
2. **生成每 TM trial 地址。** `<run>/trials/<tm-lower>` 内保留现有 contract ABI 所需 strategy/method/review/implementation/compile 子目录；共享解析产品在 `<run>/input-sync`。所有 handoff/manifest 明确引用本 run。登记 `vsProjectRoot`、`programSourceRoot`、registerRoot、knowledgeRoot、projectInfoPath，不能只给泛化 runRoot。
3. **角色解析器。** 先取 frozen registry stage owner，再用上表经 profile `ownerRole` 交叉确认的映射。SOURCE stage 使用已确认输入分类得到的角色集合；DFT-only 明确 scope。读冻结草稿 instructions，生成含 owner/profile/stage/TMs/runId/digests 的 host receipt。
4. **DSH dispatch adapter。** 可复用原生 parent + `agentPresets.mount(...,'ate-ptc')` + `subagents.start` 的生命周期装配，训练 persona 必须带 run-local 地址簿。返回全部 role 的真实 terminal；不以“已派发”充当 DONE。将子 session 与稳定 dispatchId 持久绑定，提供 recoverStage，从回执恢复未知在途任务，禁止重复派发。
5. **run-aware gate adapter。** 每个注册 gate 有唯一确定命令模板和参数 schema。给旧 gate 增加明确 context 参数或新训练包装器调用原校验函数，所有路径通过宿主 resolve/containment 检查后再执行。不能仅修改 cwd，因为多数脚本 ROOT 来自 `__file__`。不能把未过 gate 的专家完成报告映射为 gate PASS。
6. **训练工具守卫。** 为每个角色按回执绑定只读材料、自己的 TM trial 输出、获准 VS 副本文件；拒绝正式 project、实际 ForCodexDebug、versions、active-release 等写入。Shell 白名单检查完整 argv，禁止任意 Python/PowerShell 注入。校验器会读取合同里内嵌路径，所以宿主也要验证所有 signedInputs/change/source/evidence 字段的归属。
7. **编译宿主服务。** 编译器由宿主固定启动；不调用会 DTE SaveAll 的旧 fast_rebuild 路径。读取/检查复制的工程 imports、custom tasks、pre/post-build events；本次观察的项目无自定义 build event，但实际激活前仍应对快照复核。只构建，不加载 DLL、不运行测试仪、不执行硬件函数。取消/超时必须杀子进程树并留最后命令证据。
8. **真实证据收集。** 记录每个 TM 每阶段真实 gate 命令、exitCode、stdout/stderr、耗时、输入/输出摘要、profile/candidate digest。完整 pipeline-regression 证据要求 registry 所有阶段按序完成；范围训练、DFT-only、blocked、timeout 或空 implementation checks 均不得生成“完整流程通过”。

可以先在 TM109 范围打通 INPUT_SYNC→STRATEGY→METHOD→RULE_REVIEW_METHOD 的训练副本路径，再接 IMPLEMENTATION→独立 REVIEW→COMPILE；UI 必须明确尚未接通的阶段。完整发布仍由真实端到端 regression 通过作为前置条件。

## 6. 已知阻碍与工程边界

- **已证实必须改造：** INPUT_SYNC/SCH/METHOD REVIEW 固定生产路径；STRATEGY 固定正式 Project_Info；寄存器固定生产来源；编译入口 DTE SaveAll；副本工程全依赖准备；draft persona 与训练回执/guard 对齐。
- **尚未验证：** 独立干净 VS 副本 Debug/Release 实际编译时长与成功性；所有 source角色完整回执与 gate 串联；取消是否终止 MSBuild/CL 后代；完整 TM109 实施能否满足现行策略/方法合同。不能给这些事项写 PASS。
- **设计上需要固定：** 多 TM trial ABI 和共享解析产品映射；训练 Project_Info 的来源与身份 schema；发布 candidateDigest 绑定到此次真正参与训练的所有 profiles/编排/合同/规则；SDK只读依赖如何绑定版本。
- **本次输出：** 只有本文。未执行生产入口 `advance_batch`、未改写旧 gate、未编译、未修改正式 VS 文件。
