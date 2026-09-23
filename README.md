# ATE-Coding-Platform

DeepSeek Harness (dsh) 主导的 **ATE 测试代码自动生成平台** 工作区。
（2026-09-02 起，替代原 Claude Code 工作区 `D:\Newtest\CLAUDE_PROCESS`）

## 目录结构

| 目录 | 用途 |
|------|------|
| `project/` | 项目输入数据（DALI 原理图、SCH-Connect-Map、测试项 xlsx、硬件手册等） |
| `knowledge/` | 规则 / 知识库（standards、sources、experience、references）+ claude-history 46 会话吸收成果 |
| `scripts/` | 工具脚本（meta 生成、relay 检查、通路解析等） |
| `skills/` | agent 定义（18）+ dsh 技能（skill）定义 |
| `docs/` | 文档（工作流/架构/评审/迁移报告） |
| `Library-Functions/` | C++ 库函数（跨项目共享资产，10 类 + _inbox 自动归位） |
| `_archive/` `backup/` | 历史归档 / 备份 |
| `assets/` | 图标等资源 |

> **当前隔离验收环境的代码落点 = `D:\PROJECT6-DALI\ForCodexDebug\source\`**（fast_rebuild 对象；原生产工程 `D:\PROJECT6-DALI\devel` 保持只读）。
> **黄金案例（写码参照） = `knowledge\references\code\`**（入口见 `knowledge\references\param_type_index.md` 同名联动索引）。
> 源码无损存档：`D:\Newtest\CLAUDE_PROCESS`（永久保留，只 copy 未删）。

## 启动方式

- 桌面快捷方式 **DeepSeek Harness.lnk**（工作目录已指向本目录）
- AgentTeams 启动：`cd D:\Newtest\DSH\ATE-Coding-Plat` 后运行 `powershell -ExecutionPolicy Bypass -File .\team\start-ate-dsh.ps1`
- 普通模式：`cd D:\Newtest\DSH\ATE-Coding-Plat && dsh web`
- 团队使用说明与验收范围见 `team\README.md`。
- Web UI：`http://127.0.0.1:3080`

## 迁移规划（从 CLAUDE_PROCESS）

已执行（2026-09-02，全程只 copy 未删，源目录原样保留）：

1. [x] 项目输入数据 → `project/`（DALI 原始数据、SCH-Connect-Map，372 文件验证一致）
2. [x] 规则/知识 → `knowledge/`（standards 17、sources、experience、references 23）
3. [x] 工具脚本 → `scripts/`（gen_*.py、check_*.py + schematic_parse 流水线，路径适配完成）
4. [x] 技能/代理 → `skills/`（agents 18 + nuvolta-codegen.md/sch-parse.md + AGENT_MAP）
5. [ ] 原 CLAUDE_PROCESS 移除 —— **按用户铁律取消：永久保留**（只 copy 不删）
