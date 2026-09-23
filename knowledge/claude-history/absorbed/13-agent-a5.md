# 吸收记录 #13 — 继电器脚本调研（gen_cbit_defines.py / gen_paths.py）

- 源文件：`sessions/13-agent-a5.md` ← `~/.claude/projects/subagents/agent-a59caf3cca737c6c1.jsonl`
- 时间：2026-08-10 11:55→11:58（0.5MB）；subagent 只读调研
- 主题：gen_cbit_defines.py（658 行）与 gen_paths.py（832 行）的能力边界

## gen_cbit_defines.py

- **单点 #define 生成**：读 CBIT 表 Excel（col0 原位号、col10 CBIT 通道；S34_CBITn→n、S36_CBITn→n+128），`merge_names()` 合并（KELVIN F/S→`_FS`、单字母 F/S 去后缀、FORCE/SENSE→`_FOS_SNS`、BUS 方向合并、同 K 号后缀拼接），输出 `relay.h` 单点段（1.1 MOS SPST / 1.2 G6K Dedicated / 1.3 G6K Shared），全打 stdout。`phase2_singlepoint_output.txt`（161 条）为逐字节对拍基准。
- **V1~V8 校验**：`load_existing_defines` 正则 `^\s*#define\s+(K\d+[A-Za-z0-9_]*)\s+(\d+)`（**只吃单个整数 value**，多值别名 `46,49` 不解析）。`verify_defines` **按 CBIT 值做主键**比较：目标有脚本无→ERROR；同值异名（物理名 vs 规范化名）→WARN（`--warn-as-error` 才 FAIL）——这就是 StdAfx.h `K3_BUSL0_VBUS` vs 规范 `K3_BUSL_VBUS` 差异的处理方式。
- **不生成通路继电器 2.x 别名**（check_v7 仅防御占位）；2.x 由旧 `DALI\gen_final.py`/`gen_v8.py` 生成。

## gen_paths.py

- `--json` 输出 path_list：`[{dut_pin, source, side(FPVIe 有), via_relays:[{name,cbit,type(G6K/SPST),state(SetOn/KeepDefault),annotation}], intermediate_source}]`——**永远走 stdout，不落盘**（无 --json-output）。
- CLI：`--netlist --cbit --output --json --max-depth(默认6) --audit-rules`。
- **源表覆盖**：FPVIe/ACM200/FOVIe ✓；**QTMU/QVM 未覆盖**（netlist 有 S8_QVM/QTMU 继电器但主流程只用 ACM/FOVI 关键字过滤，QVM→AMPOUT、QTMU→nQON 通路只以手写别名存在于 relay.h 2.3 段）。
- RULE_COVERAGE 11 条（P-P1~P-P11）自检。
- 仓库无已保存的 path_list JSON/txt；`DALI\paths.txt` 常量未接为默认。

## 交叉引用

- 命名体系：relay.h 规范化名 vs StdAfx.h 物理名（详见 #14）；gen_paths 的 path_list 是 relay.h 2.x 通路的"原料"；`verify_relay_trace.py` 另用物理名核对 SetOn（#11）。
