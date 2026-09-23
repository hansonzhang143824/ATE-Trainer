# Library-Functions 索引

> STS8300 测试工程库函数统一目录（原 `库函数\`，2026-08-29 改名 + 按类重排）。
> 每类一个文件夹，与工程 include 路径对应；本文件是唯一索引入口。

## 类目录总览

| 文件夹 | 文件 | 用途 | 备注 |
|--------|------|------|------|
| `BoardCheck/` | BoardCheck.h/.cpp | 板卡检查 | |
| `Coutlier/` | Coutlier.h/.cpp | 离群值剔除/统计 | |
| `FMEA/` | FMEA.h/.cpp | 失效模式与影响分析 | |
| `inireader/` | inireader.h/.cpp | ini 格式 setup 文件解析 | `.ini`→`.treg` 扩展名变更（语法不变） |
| `spec/` | spec.h/.cpp | SPEC 限值参数对象 | SITE_NUM 定义已注释（避免与 treg.h 重定义） |
| `tempchar/` | tempchar.h/.cpp | 温度特性 | |
| `treg/` | treg.h/.cpp | Trim Register（TRIM/SEL/ASSY/ASSY_GRP/TRIM_GRP） | 知识库：`.claude/knowledge/standards/treg.md` + `.claude/knowledge/sources/treg/`；**SITE_NUM 唯一定义在此（`treg.h:49 #define SITE_NUM 12`）** |
| `Test_Method/` | Test_Method.h/.cpp | 通用测试方法（77 个 BOOL 函数，含 64 ramp 捕获重载） | 见下方「ramp 捕获库」 |
| `shared_functions/` | README.md + registry/ | 自进化沉淀共享函数库 + 注册表/changelog | /evolve 三 Agent 产出落点 |
| `sub_func/` | sub_func.h/.cpp | 项目子函数 | |
| `_inbox/` | （投递口） | 新版库文件投递口，ingest.py 自动归位 | 见下方「更新流程」 |

## ramp 捕获库（Test_Method）

- 现底座已含完整 **64 函数 = 4 类型（rampv_capv/rampv_capi/rampi_capv/rampi_capi）× 4 ramp 源 × 4 cap 源**，每类型 16 个**同名重载**（靠参数类型区分，无后缀命名），.h 声明与 .cpp 实现一一对应（各 16）。
- 另有遗留函数：**2× rampv_capv(..., delay_2p)** + **rampi_fv_capv**（声明+实现齐全，老 TM 代码在用）。
- 更新方式：**整文件粘贴**（走 `_inbox\` + `ingest.py` 覆盖）；粘贴即完整库，无需再生成。
- 用法知识：memory `test-method-ramp-library`（step=采样点数、interval≥10、TRIG_RISING/FALLING、result=触发点 ramp 电压）。

## SITE_NUM 规则（2026-08-29 拍板；08-30 迁移完成，fast_rebuild 实测 PASS）

- **SITE_NUM 唯一定义 = 工程 `StdAfx.h` L23**（`#define SITE_NUM 12`，在 include spec.h 之前）。2026-08-30 从 treg.h:49 迁移至此：treg.h 是跨项目库、SITE_NUM 是项目配置，库头文件不硬编码。
- 库头文件**禁定义**：`treg.h:49` 与 `spec.h:62` 的 SITE_NUM 行均为注释态，**勿解注**（否则与 StdAfx.h 重定义）。
- 包含顺序约束：treg.h 与 StdAfx.h 循环包含（treg.h L28→stdafx.h，靠 pragma once 终止），改 StdAfx.h 头部时定义必须保持在 include spec.h 之前。
- codegen 入口解析时，材料中出现 `STS_SITE_NUM` 一律改写为 `SITE_NUM`。

## 更新流程（_inbox 自动归位）

1. 把新版库文件丢进 `_inbox\`。
2. 运行：`python -X utf8 ingest.py`（先 `--dry-run` 预览）。
3. 机制：按文件名主干匹配类文件夹（含别名表 test_method→Test_Method 等）；同名旧文件先备份到 `_archive\inbox_backup\<时间戳>\` 再覆盖；识别不了的留在 `_inbox\` 并列出，找 Claude 判断。

## 读写注意

- 库文件磁盘上是 **DLP 透明加密（TSZ# 头）**：python 读写（`open(...,'rb'/'wb')`）透明解/加密得明文；grep/head/g++ 等非授权进程读到密文（TSZ#）。读写/验证一律走 python 字节模式，禁文本模式。
- 改动库文件后必须实际验证（编译或计数核查），不允许"推断通过"。
