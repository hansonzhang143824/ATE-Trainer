# 会话 #29 — 背景：Nuvolta STS8300 ATE 离线代码生成体系。codex 迁移产出了「V2 硬件解析」——把原理图输入源从 EDIF 网表换成 CSV，通过桥

- 文件：`agent-a509ec6146664b766.jsonl`（项目 subagents）
- 时间：2026-08-23T15:14:52.304Z → 2026-08-23T15:16:03.006Z，大小 0.2 MB
- 用户消息 1 条 / 助手文本 2 段 / 工具调用标记 4 行

---

## 对话正文（工具输出已剥离）

### 2026-08-23 15:14:52 [user]

背景：Nuvolta STS8300 ATE 离线代码生成体系。codex 迁移产出了「V2 硬件解析」——把原理图输入源从 EDIF 网表换成 CSV，通过桥接器复用 legacy 六门控引擎。V2 脚本在 `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\` 目录。但 V2 的 skill 文档（SKILL.md/PATH_CONTRACT.md/VALIDATION_RULES.md/RELAY_CONTROL_RULES.md/AI_CONTEXT.md）全是空壳（2~4行），我需要精确了解脚本内容，以便设计"补齐 V2 文档"要写什么。

请精确读取以下脚本（用 Read），返回**精确的技术细节**（列名、函数名、规则条款、硬编码常量）：

1. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\csv_schematic_adapter_v2.py`（约656行）
   - 返回：REQUIRED_COLUMNS 25 列的确切列名清单、build_graph 构建的图结构（节点/边类型）、write_synthetic_edif 生成的合成网表格式、如何处理 Altium 符号 PinNumber 与封装脚号互换、如何忽略匿名 PORT、如何规范化网络命名。

2. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\csv_pathproof_v2.py`（约349行）
   - 返回：PathProof BFS 算法要点、硬编码的源表名（ACM200/FXVIe_PLUS/FPVIe/QTMU/QVM 等）、G6K 继电器 pin 转换规则、Kelvin Force/Sense 角色匹配规则、DUT PIN 到达即停止的规则、F/S 交叉路径拒绝规则。

3. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\adapt_tm607_for_v2_hardware.py`
   - 返回：TM607 极性适配的具体逻辑（FPVI High→PGND、FPVI Low→SW1、电流取负等）。

4. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\prepare_v2_compile_sandbox.py`
   - 返回：隔离编译沙箱的机制（如何复制、写到哪里、如何保证不污染正式工程）。

请分节返回，附文件路径和关键行号。这些细节将直接用于编写 V2 的 skill 文档正文（替换现在的空壳），准确性优先。

### 2026-08-23 15:14:53 [assistant]

I'll read all four scripts in parallel to extract the precise technical details.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-23 15:16:03 [assistant]

以下为四个脚本的精确技术细节（均已全文读取，行号对应实际代码）。所有路径为绝对路径。

---

## 1. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\csv_schematic_adapter_v2.py`（656 行）

### REQUIRED_COLUMNS（L25–32），恰好 25 列
顺序如下：

1. `SheetPath`
2. `RecordType`
3. `RecordKey`
4. `NetName`
5. `MemberType`
6. `MemberName`
7. `Designator`
8. `ComponentUniqueID`
9. `MemberUniqueID`
10. `ComponentKind`
11. `LibraryReference`
12. `PartID`
13. `PinNumber`
14. `PinName`
15. `Electrical`
16. `Relation`
17. `EndpointStatus`
18. `ObservedNetCount`
19. `ObservedNets`
20. `EffectiveShortNetCount`
21. `EffectiveShortNets`
22. `DanglingEndpointCount`
23. `DanglingNets`
24. `Status`
25. `RawID`

校验：`load_csv`（L64–145）读取头部，`missing` 缺列直接报错；`extra` 列保留但不使用（计入 warnings）。`RecordType` 仅接受 `{"NET_MEMBER", "NET_TIE_ENDPOINT", "NET_TIE_GROUP"}`（L139–144），其余报错。还检测加密容器：文件头 `%TSD-Header-###%` 或 `TSZ#` 报错（L65–70）。

### Dali-SCH compact 布局归一化（L88–129）
CSV 可能是 Altium 的紧凑导出（固定前 9 列 + 尾部若干列），脚本按 `MemberType` 归一化：
- **PIN 行**（L91–114）：`values[4].strip().upper() == "PIN"` 且 `values[14]` 空、`values[12]` 为 `PASSIVE/INPUT/OUTPUT/I/O/POWER`。固定列 `[0:9]`，`PartID=values[9]`；PinNumber/PinName 按是否数字判断顺序（L102–112）：`values[10]` 是数字 → `PinNumber=values[10]`, `PinName=values[11]`；否则反过来；两个都不是数字 → 报错。`Electrical=values[12]`, `RawID=values[13]`。
- **PORT / NET_LABEL / POWER_PORT 行**（L115–126）：固定列 `[0:6]`，`Electrical=values[6]`；PORT 行额外 `Status=values[7]`, `RawID=values[8]`，其余 `RawID=values[7]`。

### build_graph 图结构（L148–329）
返回 dict，键为（L311–329）：`nets`（net→`[(inst, pin)]`）、`ports`（name→方向）、`port_nets`、`net_ports`、`net_labels`、`instances`、`inst_pins`、`relay_count`、`source_port_rows`、`dut_port_rows`、`ignored_ports`、`port_direction_conflicts`、`net_tie_groups`、`semantic_port_aliases`、`electrical_role_corrections`、`singleton_relay_nets`、`intentional_open_nets`。

- **节点**：网络（net）、端口（PORT）、实例（inst）、网标（NET_LABEL/POWER_PORT）。
- **边**：net→(inst,pin) 连接；port→net 映射；net→端口有序列表（`net_ports_ordered`）。

### Altium 符号 PinNumber 与封装脚号互换（L192–206）
```
try: pin = int(PinNumber)
except ValueError:
    display_pin = PinName
    if display_pin.isdigit(): pin = int(display_pin)
    else: raise ValueError(...)
```
注释（L195–198）：IC 符号上 Altium 可能把符号化设计脚（GND/VOUT/RS+）放进 `PinNumber`、把物理封装脚号放进 `PinName`；继电器行 `PinNumber` 保持数字，所以**优先取数字字段**，保证确定性、保住拓扑。

### 匿名 PORT 忽略（L213–221）
`PORT` 行 `MemberName` 为空 → 计入 `ignored_ports` 并 `continue`。注释：Altium 在 N00028 上发出两个相连的无名端口，无寻址语义端点、无元件脚；legacy EDIF 用 UNDEFINED 表示并忽略。

### PORT 角色判定（L226–244）
- `Electrical == "OUTPUT"` → 方向 `OUTPUT`，`dut_rows += 1`。
- `Electrical == "I/O"` → 若 `re.match(r"^.+_[FS]_S\d+$", name)` **且不**以 `^S\d+_` 开头（即非 slot 源的 Kelvin 式 DUT 端）→ 归一化为 `OUTPUT`（`electrical_role_corrections`，`dut_rows += 1`）；否则 → `INOUT`（`source_rows += 1`）。slot 源总是以 `S<slot>_` 开头。
- 其余 Electrical（INPUT 等）→ `ignored_ports` 忽略。
- 方向冲突（L245–261）：同名 PORT 两次方向不同时，保守取 `resolved = "OUTPUT" if "OUTPUT" in (old, direction) else old`，记入 `port_direction_conflicts`。

### 语义别名（L222–225）
`name.startswith("S3_FOVIe_")` → `name.replace("S3_FOVIe_", "S3_FXVIe_PLUS_", 1)`，记入 `semantic_port_aliases`。

### NET_TIE_GROUP（L166–179, L273–281）
组行校验 `Status == "OK"` 且 `EffectiveShortNetCount` 与 `EffectiveShortNets.split("|")` 长度一致；合并逻辑：把组内每个 net 的连接取并集，回写组内所有 net（零欧姆等效，不造继电器）。

### 单点冗余网删除（L287–299）
对每个无端口端口覆盖、且连接数恰为 1 的 net：
- 实例匹配 `^K\d+_`（继电器）→ 移入 `singleton_relay_nets`，`del nets[name]`（注释：G3 已检查物理浮空脚规则，允许 G6K 一个浮空触点；删掉冗余表示以免 G5 再计为硬失败）。
- 实例以 `TP_` 开头或 net 名含 `NC`（`re.search(r"(^|_)NC($|_)", name, re.I)`）→ 移入 `intentional_open_nets`，删除。
- 末尾若 `not ports` 或 `not nets` → 报错（L301–304）。

### infer_cell（L47–61）
- `^K\d+_` 开头：若 `pins - {1,2}` 或 `pin_names - {"COMMON","NO"}` 非空 → `"G6K"`；否则 → `"SW_SPST"`。
- 其余前缀映射：`CAP/C→Cap`, `R→Res2`, `D→D_Schottky`, `TP→TEST_POINT_SMALL`, 其它 → `f"CSV_{prefix}"`。

### write_synthetic_edif 合成网表格式（L338–402）
EDIF 输出骨架：
```
(edif CSV_V2
  (library CSV_V2_LIB
    (cell Sheet1_SchDoc
      (interface
        (port <name> (direction <OUTPUT|INOUT>))     # 每个端口，按名字排序
        ...
      )
    )
  (Instance <inst> (viewRef NetlistView (cellRef <cell>)))
  (Net <canonical>
      (PortRef &<pin> (InstanceRef <inst>))
      ...
  )
)
```
- **安全符号** `safe_symbol`（L332–335）：匹配 `[A-Za-z_][A-Za-z0-9_]*` 原样用；否则 `{prefix}_{index}`。非法符号用 `(rename sym "原名")` 形式（L350–352, L387–388）。
- **规范网络命名**（L363–383）：优先 `net_labels`（`canonical = net if net in labels else labels[0]`）；否则取 `net_ports` 第一候选；再否则用物理 net 名。若规范名已被占用且不等于物理名 → 回退物理名，记 `canonical_name_collisions`。
- 返回统计：`physical_nets`, `renamed_nets`, `terminals`（恒 0）, `canonical_net_names`, `canonical_name_collisions`。
- 合成网表写到 `workspace/Project/DALI/CSV_CONNECTIVITY_V2.NET`（L510），放在 `sch_confirmed.json` 旁以复用同一套人工审过的 per-project exceptions（L508–510）。

### main 流程（L480–652）
- 默认输入 `package_dir/Dali-SCH.csv`；默认 out-dir `workspace/Project/DALI/hardware_parse_v2`；默认 legacy map `Project/DALI/SCH-Connect-Map.txt`。
- V2 配置：深拷贝 base `project_config.json`，`revision` 追加 `-csv-v2-validation`，`inputs.schematic` 指向合成网表，`intermediates.component_statistic`/`sch_connect_map` 指向 out-dir 下 `.v2.txt`。**因工作区会自动加密新建 .json 文件，配置写成文本后缀** `project_config.v2.json.txt`（L520–523）。
- `absolutize_config_paths`（L446–477）：把 `inputs`/`optional_inputs`/`intermediates`/`outputs` 中的文档化路径字段（如 `dft, schematic, cbit, vs_project, channelmap, vs_src_dir, treg, resource_definitions, relay_definitions`、`sch_connect_map, component_statistic, relay_h, paths_txt, singlepoint_bench, waivers`、`meta, build_manifest, path_proofs` 等）相对路径解析为绝对路径，因为 V2 配置位于 `Project/DALI` 之下而生产配置在 workspace 根。
- 运行 legacy 引擎：`subprocess.run([sys.executable, legacy_parser, "--config", config_path], cwd=workspace)`（L589–593），输出写到 `strict_gate_run.v2.txt`。
- manifest 写到 `validation_manifest.v2.json.txt`（L586）。
- **迁移比对** `compare_migration`（L426–443）：从 `## 列` 分隔的路径记录中抽 `"Relay-"`、`"←"`、`CH\d+ (?:High|Low)` 行（`path_records`，L410–423），与 legacy map 做 Counter 差集。
- **状态机**（L632–646）：`PASS`（parser 通过 + migration PASS）、`PARSER_PASS_REVISION_DELTA_APPROVED`（凭 `approved_revision_delta.v2.json.txt`，字段 `approved==True`、`v2_input_sha256`、`old_sch_connect_map_sha256` 三者校验，L619–630）、`PARSER_PASS_COMPARISON_FAIL`（exit 2）、`PARSER_FAIL`。

---

## 2. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\csv_pathproof_v2.py`（349 行）

### 硬编码源表名（L44–53 `source_meta`）
源类型 token（顺序即优先级）：`"ACM200", "FXVIe_PLUS", "FXVIe", "FPVIe", "QTMU", "QVM"`。
正则补充：`^S(?:24|9)_P\d+$` → `"DCM"`；`^S10_CH\d+_[AB]$` → `"QTMU"`。
侧/通道解析：`_(FH|SH|FL|SL)(\d+)`（`FH/FL→F`、`SH/SL→S`）；`CH(\d+)([+-])$`（`+→F`、`-→S`）；`_P(\d+)$`（`channel, role="F"`）。`domain`：`FH/SH/+ → HIGH`，`FL/SL/- → LOW`。
`pair_key = f"{family}:{channel}:{pair_domain}"`，`pair_domain` 对 `QVM` 强制为空串（L79）。`family` 取 `S\d+_.+?` 前缀（去掉 FH/SH 尾标）。

### pin_role（L33–41）
- `^(.+?)_(?:FORCE|SENSE)_S\d+$` → `(base, "F"/"S")`
- `^(.+?)_([FS])_S\d+$` → `(base, F|S)`
- `^(.+?)_S\d+$` → `(base, "")`
- 其余 → `(port, "")`

### NativeGraph 结构（L90–195）
- `relays` = 实例名可匹配 `K(\d+)_`（`relay_number`，L28–30）；`g6k` = cell 为 `"G6K"`；`mos` = `relays - g6k`。
- `ipn`：反向 pin-net 表 `inst[pin] → [nets]`。
- `dut_by_net`：net → OUTPUT 端口名列表。

### G6K 继电器 pin 转换规则（L111–119 `transitions`）
- **G6K NC 路径**：`{2:(3,), 3:(2,), 7:(6,), 6:(7,)}`
- **G6K ON 路径**：`{3:(4,), 4:(3,), 6:(5,), 5:(6,)}`
- 即 NC 状态连通 (2↔3)、(7↔6)；ON 状态连通 (3↔4)、(6↔5)。
- 非 G6K（MOS/SPST）：`pin==1 → yield (2,"ON")`；`pin==2 → yield (1,"ON")`。

### BFS 算法要点（L133–195 `trace`）
- `max_depth` 默认 `6`。起点 = `port_nets.get(source)`，队列元素 `(net, path, used_numbers(frozenset), active_bus_domain)`。
- 优先序 `best[key]`：`key = (len(used_numbers), 路径中 ON 状态数)`，字典序更小者胜（L144）。
- **DUT PIN 到达即停止**（L141–157）：当前 net 命中 `dut_by_net`（有 OUTPUT 端口）→ 对每个 dut 记录 proof 并 `continue`（不扩展）。注释明确 `# PATH_CONTRACT: DUT PIN is a terminal; never expand beyond it.`
- 剪枝：`len(used_numbers) >= max_depth` 跳过；非继电器实例跳过；已用过继电器号跳过；`next_net == net` 跳过。
- **Bus 域规则**：`bus_domain`（L121–127）——net 含 `FH_BUS/SH_BUS/FH_PC/SH_PC` → `HIGH`；含 `FL_BUS/SL_BUS/FL_PC/SL_PC` → `LOW`。若非 scarce 源且 next_net 属 bus 域 → 跳过；next_domain 与源 meta.domain 冲突 → 跳过；ON 转移进入新 bus 域与 `active_bus_domain` 冲突 → 跳过，进入则更新 `next_active`。
- `scarce`（L129–131）：源含 `"FPVIe", "QTMU", "QVM", "CH0"` 之一即为 scarce（scarce 源豁免 bus 域剪枝）。

### Kelvin Force/Sense 角色匹配（L219–280 `validate_and_pair`）
- 对每条 proof：`dut_base, dut_role = pin_role(dut_pin)`；`source_role = source_meta.role`。
- `role_match = not dut_role or not source_role or dut_role == source_role`（L234）——任一角色为空即放行；否则 F≠S → `reject_reason="KELVIN_ROLE_CROSS"` 进 rejected。
- `cbit_complete`：`required_on` 中每个继电器号在 CBIT 表中缺失 → `reject_reason="MISSING_CBIT"` + hard issue。
- **F/S 配对**（L248–280）：仅源类型 `{"FPVIe","ACM200","FXVIe_PLUS","FXVIe","QVM"}` 且 role ∈ {F,S}；按 `(pair_key, dut_base)` 分组，F、S 各取最短路径（`min(..., key=lambda p: (len(p["path"]), len(p["required_on"])))`）；计算 F/S 中继电器的 ON/OFF 状态集合交集冲突数 `conflicts`；`status = "PASS" if not conflicts else "FAIL"`。

### CBIT（L198–216）
`load_cbit` 从 workspace 导入 `gen_cbit_defines`，`read_excel_cbit(str(path))` 读 `CBIT表-DALI.xlsx`，按 `K(\d+)` 分组，值用 `cbit_val(raw)`；同号不同值 → issue。

### 契约（payload，L307–312）
`dut_pin_is_terminal: True`、`kelvin_force_sense_no_cross: True`、`shared_relay_state_must_match: True`、`cbit_traceability_required: True`。

### 输出
- `path_proofs.v2.json.txt`（L329）与 `PATHPROOF-VALIDATION.v2.txt`（L331），默认 out-dir `Project/DALI/hardware_parse_v2`；`status` 无 issue 即 `PASS`。

---

## 3. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\adapt_tm607_for_v2_hardware.py`（115 行）

### 作用域保护（L26–44）
- 非生产（默认）：`test_cpp = v2_dir / "vs_compile_sandbox" / "devel" / "source" / "test.cpp"`，并用 `test_cpp.relative_to(v2_dir)` 强制必须位于 V2 目录下。
- 生产：`test_cpp = Path(config["inputs"]["vs_src_dir"]) / "test.cpp"`，且**必须**同时传 `--production --intentional-hardware-revision`，否则报错退出（L31–32）。
- 读写用 `gen_path_defines.read_enc / write_enc`（保留原编码）。

### 幂等检测（L46–52）
已适配当且仅当同时满足：文本**不含** `"K_FPVIL_TO_PGND"`、含 `"K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A"`、含 `"ls_zcd[site] = -ls_zcd[site];"`。

### 替换规则（L54–91，`replace_once` 要求唯一匹配，否则报错）
1. **极性注释**：旧 `// 电流环: FPVI0 High→SW1 → DUT(LSFET) → PGND → FPVI0 Low` → 新 `// 新版硬件极性: FPVI0 High→PGND → DUT(LSFET) → SW1 → FPVI0 Low` + `// 芯片定义电流 SW→PGND = -FPVI0 电流，因此源表反向 ramp，结果再取负`。
2. **High 侧通路注释**：`SW1 → FPVI0 High: K_FPVIH_TO_SW1_A = K136,K137,K143,K144,K46` → `PGND → FPVI0 High: K_FPVIH_TO_PGND_A = K136,K137,K143,K144,K154,K155`（注意新加 K154,K155，去掉 K46）。
3. **Low 侧通路注释**：`PGND → FPVI0 Low : K_FPVIL_TO_PGND = K138,K140,K51,K53,K93` → `SW1 → FPVI0 Low : K_FPVIL_TO_SW1_A = K47`。
4. **CBIT 通路切换**：`cbite.SetOn(K_FPVIH_TO_SW1_A, K_FPVIL_TO_PGND, K13_VBAT_Cap, K65_nQON_PU, -1);` → `cbite.SetOn(K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);`（High 改接 PGND，Low 改接 SW1）。
5. **ramp 方向注释**：旧 `FPVI0 ramp 电流 -0.2A -> +0.2A; nQON(ACM200 10UA 高阻) 捕 DTEST0 翻转点` → 新 `FPVI0 源表电流 +0.2A -> -0.2A，对应芯片 SW->PGND 电流 -0.2A -> +0.2A`。
6. **翻转点注释**：旧 `翻转点电流 = ZCD 阈值 (期望 0.1A); trig_level=1.65V = nQON 逻辑中点` → 新 `翻转点源表电流取负后为 ZCD 阈值 (期望 +0.1A); trig 保持已确认的 RISING`。
7. **参数行电流取负**：`-0.2, 0.2, 200, 20, 1.65, TRIG_RISING, ls_zcd);` → `0.2, -0.2, 200, 20, 1.65, TRIG_RISING, ls_zcd);`（电流起点/终点对调，200/20/1.65/TRIG_RISING 不变）。
8. **结果取负**：`LS_ZCD->SetTestResult(site, 0, ls_zcd[site]);` → 先注释 `恢复为 DFT 定义的 SW->PGND 正方向；错误哨兵值保持不变`，再 `if (ls_zcd[site] != ERROR_RES) ls_zcd[site] = -ls_zcd[site];` 然后才 SetTestResult。

### 收尾（L95–110）
- 替换后若文本仍含 `"K_FPVIL_TO_PGND"` → `raise RuntimeError("stale invalid V2 alias remains in test.cpp")`。
- 生产模式先备份 `test_cpp.parent/Backup/test.cpp.before_hardware_parse_v2_{YYYYmmdd_HHMMSS}.bak`（`shutil.copy2`）。

---

## 4. `D:\Newtest\CODEX\_PROCESS\ATE_Hardware_Parse_Skill_V2_Test_Package\scripts\prepare_v2_compile_sandbox.py`（136 行）

### 复制过滤（L18–33）
- `IGNORED_DIRS = {"Backup", "debug", "Debug", "Release", ".vs", "ipch"}`
- `IGNORED_SUFFIXES = {".obj", ".pdb", ".ilk", ".pch", ".tlog"}`
- `copy_filter` 返回排除集，供 `shutil.copytree` 的 `ignore=` 用。

### 沙箱位置约束（L36–40, L61）
`require_child(sandbox, v2_dir)`：`sandbox.relative_to(v2_dir)` 必须成功，否则 `ValueError("sandbox must remain below ...")`。v2_dir = `workspace/Project/DALI/hardware_parse_v2`。

### 复制机制（L64–104）
- 只读源：`config["inputs"]["vs_src_dir"]`、`config["inputs"]["vs_project"]`、`config["inputs"]["treg"]`（均 `.resolve()`，且逐一 `exists()` 校验）。
- `shutil.copytree(source_dir, sandbox/devel/source, dirs_exist_ok=True, copy_function=copy2, ignore=copy_filter)`。
- `treg` 单独 `copy2` 到 `sandbox/devel/<treg文件名>`。
- **沙箱配置**：深拷贝 config，`revision += "-compile-sandbox"`，重写 `inputs`：
  - `vs_project` → `sandbox_source / source_project.name`
  - `channelmap` → `sandbox_source / Path(channelmap).name`
  - `vs_src_dir` → `sandbox_source`
  - `treg` → `sandbox_treg`
  - `resource_definitions` / `relay_definitions` → `sandbox_source / <原名>`（**仅取其 basename 挂到沙箱源码目录**）
- 写出 `v2_dir / "project_config.v2.compile.json.txt"`。

### 防污染保证（L106–132）
- 不修改生产 VS 树、不写生产 `project_config.json`；生产 VS 仅作为只读输入。
- manifest（`compile_sandbox_manifest.v2.json.txt`）记录 `mode: "isolated_compile_validation"`、`production_vs_modified: False`，以及 **baseline_hashes**：生产/沙箱 `StdAfx.h`、`test.cpp` 各自 sha256（可对比证明生产未被改动）。
- 沙箱内的 `test.cpp`/`StdAfx.h` 是独立副本，`adapt_tm607_for_v2_hardware.py` 的默认非生产分支只改这个副本。

---

### 关键行号速查
| 内容 | 文件:行号 |
|---|---|
| 25 列 REQUIRED_COLUMNS | csv_schematic_adapter_v2.py:25–32 |
| Dali-SCH compact 归一化 | :88–129 |
| PinNumber/PinName 互换 | :192–206 |
| 匿名 PORT 忽略 | :213–221 |
| I/O→OUTPUT 修正、方向冲突 | :226–261 |
| S3_FOVIe_→S3_FXVIe_PLUS_ | :222–225 |
| NET_TIE_GROUP 合并 | :273–281 |
| singleton relay / open net 删除 | :287–299 |
| infer_cell 类别 | :47–61 |
| EDIF 骨架/规范命名 | :338–402 |
| 合成网表路径 | :510 |
| 配置绝对化路径字段集 | :455–466 |
| legacy 引擎调用 | :589–593 |
| 迁移比对 | :426–443 |
| 状态机 | :632–646 |
| 源表名 token | csv_pathproof_v2.py:44–53 |
| pin_role | :33–41 |
| G6K 转换表 | :111–119 |
| BFS/终端停止/域剪枝 | :133–195 |
| 角色匹配/交叉拒绝 | :219–280 |
| CBIT 冲突 | :198–216 |
| 替换规则（TM607） | adapt_tm607_for_v2_hardware.py:54–91 |
| 幂等检测 | :46–52 |
| 沙箱复制过滤 | prepare_v2_compile_sandbox.py:18–33, 73–99 |
| baseline 哈希 | :110–123 |

以上可直接作为 V2 skill 文档正文的技术素材。需要我针对某一段再展开（例如 `source_meta` 的全部正则分支、或 migration comparison 的抽样上限等）可以继续。
