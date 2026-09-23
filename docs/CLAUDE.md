# Nuvolta STS8300 测试代码生成项目

> 为 Nuvolta **NU1201** 芯片生成 STS8300 测试平台代码（offline coding，机台外写码）。
> 本文件是**入口 + 指针**；架构权威见 `.claude/AGENT_MAP.md`，全景 14 步见 `.claude/knowledge/panorama.md`。

## 目录布局

| 位置 | 内容 |
|------|------|
| `D:\Newtest\CLAUDE_PROCESS` | 工作根目录（不访问外部文件） |
| `Project\DALI\` | 项目输入（`Dali_testmode.xlsx` / `.treg` / `SCH-Connect-Map.txt` / `Component-Statistic.txt` / `meta\` / `reg_config\`） |
| `D:\PROJECT6-DALI\devel\source\` | VS 工程源（`test.cpp` / `sub.cpp` / `StdAfx.h`，**DLP 透明加密**） |
| `Library-Functions\` | `test_method`（ramp 捕获库）· `shared_functions`（跨项目子函数）· `treg`（trim 库）· `sub_func` |

## 可用技能

- `/nuvolta-codegen` — 主 Skill，编排代码生成流水线
- `/sch-parse` — 原理图解析（SCH-Connect-Map + Component-Statistic）

## 代码生成流水线（主 Skill 编排，CBIT-Definition）

```
入口: 解析指令 → 本批 TM 范围
  sch-parse → Pin_Channel_define → dft-parse（仅 DFT）
       ▼
  CBIT-Definition: 有继电器定义文件? 否→四阶段创建 / 是→仅 check
       ▼
  共用循环（每测试项）: 框架 → relay → 上电 → 寄存器 → measure → 下电 → LogData
       ▼
  收尾双查: check-agent + cbit-check
```

## 脚本（推理→agent，固定→脚本）

- **cbit**：`gen_cbit_defines.py`（P1 单点 + P4 校验）· `gen_paths.py`（P2 通路）· `gen_path_defines.py`（P3 通路定义）
- **上下电**：`gen_power_sequence.py`
- **meta**：`gen_testitems_meta.py`（生成）+ `check_testitems_meta.py`（校验）
- **校验**：`verify_relay_trace.py` · `verify_awg_params.py` · `verify_single_fn.py` · `verify_merge_rules.py`
- **构建**：`fast_rebuild.ps1`（快速验证）· `compile.ps1`（完整编译 + Debug）

## 三注册表（唯一权威索引）

| 类型 | 位置 |
|------|------|
| 规则 | `.claude/knowledge/standards/rules-registry.md` |
| 材料 | `.claude/references/param_type_index.md` |
| 函数 | `.claude/knowledge/standards/functions-registry.md` |

## 关键约束

- 所有 `.cpp` / `.h` / `.NET` 读写**必须走 Python**（DLP 透明加密，字节模式，禁文本模式）
- 编译 / Debug 走 `compile-agent` / `compile.ps1`；快速验证走 `fast_rebuild.ps1`
- 项目所有输入都在对应文件夹；Library-Functions只在 `Library-Functions\`
- **网页输出统一 SHTML 格式（R-SHTML）**（`.claude/knowledge/standards/shtml-output-rule.md`）：`.shtml` 扩展名 + 标准 HTML5 + UTF-8 无 BOM 纯文本 + CSS 全内联零外部资源；改网页文件用 PowerShell UTF8Encoding 无 BOM 全量重写

## 旁路工作流（用户触发，不进 pipeline）

- compile-agent / deploy-agent / testplan-agent
- 自进化：`/evolve rules|exp|fn`（rules / experience / sub-function 三 agent，共享 daylog）

## 文档地图

- Agent 全景：`.claude/AGENT_MAP.md`
- 全景 14 步：`.claude/knowledge/panorama.md`
- 检验两层：`.claude/knowledge/standards/verification.md`
- 进度：`PROGRESS.md` · `daylog/`
