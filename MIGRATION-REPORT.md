# CLAUDE_PROCESS → ATE-Coding-Platform 迁移报告

- 迁移日期：2026-09-02
- 源：`D:\Newtest\CLAUDE_PROCESS`（734 文件 / 93.3 MB，**原样保留零改动**，全程只 COPY）
- 目标：`D:\Newtest\DSH\ATE-Coding-Platform`
- 铁律：只 copy 不删除不移动；源目录内容一份不少

## 迁移映射与验证结果

| 类别 | 源 → 目标 | 文件数 | 验证 |
|---|---|---|---|
| ① 项目输入 | `Project\` → `project\`（DALI 全树含 input 22/meta 17/reg_config 275 + Boston） | 372 | ✅ 372/372 数量+大小一致 |
| ② 规则/知识 | `.claude\knowledge\` → `knowledge\`（experience 5/hardware 10/sources 31/standards 17/panorama.md） | 64 | ✅ 0 失配 |
| ② 知识-引用 | `.claude\references\` → `knowledge\references\`（param_type_index、黄金 code/、chip/method/debug/circuit） | 23 | ✅ |
| ② 知识-板卡 | `源表单板使用\` → `knowledge\sources\raw\源表单板使用\`（7 单板手册 PDF） | 7 | ✅ 7/7 |
| ③ 工具脚本 | 根级 35 py + 2 ps1 + 13 bat → `scripts\` | 50 | ✅ 0 失配 |
| ③ 配置 | 根级 `project_config.json` → `scripts\`（与 proj_config.py 成对） | 1 | ✅ |
| ③ 解析流水线 | `schematic_parse\` 整树 → `scripts\schematic_parse\`（scripts 5 + config 2 + 8 规则 md + _archive 10） | 25 | ✅ 25/25 |
| ④ 技能/代理 | `.claude\agents\`(18) → `skills\agents\`；`.claude\skills\`(2) → `skills\`；AGENT_MAP.md → `skills\` | 21 | ✅ 18+2+1 |
| ⑤ 库函数 | `Library-Functions\` 整树 → 顶层 `Library-Functions\`（10 类 + INDEX.md + ingest.py；2026-09-02 从 code\ 移正） | 23 | ✅ 23/23 |
| ⑤ 代码副本 | 根级 test.cpp/sub.cpp/Rdson.cpp/UVLO.cpp → `code\` | 4 | ✅ |
| ⑤ 工作流文档 | 根级 md/shtml/html/docx/pdf/jpg → `docs\`（工作流全景、ATE 架构、评审、讨论、PROGRESS、TREG PDF×2 等） | 22 | ✅ 0 失配 |
| ⑤ 历史日志 | `daylog\`(6) → `docs\daylog\` | 6 | ✅ |
| ⑤ 历史备份 | `_archive\` → `_archive\`；`backup\` → `backup\` | 57+25 | ✅ |
| 测试夹具 | `_awg_verify\` → `_awg_verify\`；`_test\` → `_test\` | 1+6 | ✅ |

**合计迁入：约 686 文件；全量数量+大小比对 0 失配。**

## 跳过项（源目录保留原样，未迁入）

- `__pycache__\`（运行缓存）、`History\`（空目录）、`1.txt`、`manal-op`、`recorded.json`、debug.log（运行残留，可再生/无知识价值）
- 注：`1.txt`/`manal-op`/`recorded.json` 若确需可随时补 copy

## 目标工作区现状

```
ATE-Coding-Platform/
├── project/          ← DALI 输入+解析产物（Dali-SCH.csv / SCH-Connect-Map.txt / Dali_testmode.xlsx / reg_config…）
├── knowledge/        ← claude-history（46 会话吸收成果）+ experience/hardware/sources/standards/references
├── scripts/          ← gen_*.py check_*.py verify_*.py + proj_config 对 + schematic_parse 全树 + 2 提取脚本
├── skills/           ← agents(18) + nuvolta-codegen.md + sch-parse.md + AGENT_MAP.md
├── Library-Functions/ ← C++ 库函数（跨项目共享，10 类 + INDEX.md + ingest.py）
├── docs/             ← 工作流/架构/评审文档 + daylog + 迁移报告
├── assets/           ← dsh-whale.ico 等
├── _archive/  backup/  _awg_verify/  _test/
└── README.md
```

## 后续注意（迁移后接续 #46 未决项）

1. **脚本路径假设**：gen_*.py/check_*.py 原在 CLAUDE_PROCESS 根运行、按相对路径引用 `Project\DALI\` 与 `.claude\`——迁入 `scripts\` 后相对路径结构改变，首次运行需按新布局核对 project_config.json 的路径值（如 inputs.csv_schematic、relay_definitions 指向）。
2. **DLP 加密**：复制保持密文原样；新工作区文件同样受 DLP 透明加密，读写仍需 PowerShell/python 白名单通道（同 CLAUDE_PROCESS 纪律）。
3. **真实编译工程** `D:\PROJECT6-DALI\devel\source\` 未迁移（在 CLAUDE_PROCESS 之外，本就不属此迁移范围）；code\ 内 test.cpp 等是工作副本。
4. 源 CLAUDE_PROCESS 依用户铁律**永久保留**，未做任何清理。
