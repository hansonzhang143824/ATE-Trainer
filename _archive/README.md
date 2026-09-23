# _archive — 归档清单（2026-08-16 收敛整理）

> 本目录存放「已迁移 / 被取代」的旧权威散件，**移动而非删除**（可逆）。
> 依据：`现状盘点报告.md` §C 散件清单（删前已改 knowledge/ 内引用）。

## 归档文件与去向

| 归档文件 | 迁移去向 | 状态 |
|---------|---------|------|
| `源表规则.txt` | `knowledge/hardware/closed-loop-model.md` | 正文已整合 |
| `继电器识别规范.txt` | `relays.md` + `cbit-principles.md` + `schematic-parsing.md` | 正文已整合 |
| `原理图解析基本规则.txt` | `knowledge/hardware/schematic-parsing.md` | 正文已整合 |
| `常用测试要求和硬件选型-实践.txt` | `knowledge/hardware/test-strategy.md` | 正文已整合 |
| `规则文件DEEPSEEK.md` | `knowledge/standards/rules-registry.md`（权威） | 历史主权威，正文已迁 |
| `project_rules.md` | 旧 E001~E017，与 `common-errors` 新 E001~E012/E028/E029 冲突 | 冲突源，已归档 |
| `Check-DEEPSEEK.md` | `project_rules.md` 的重复副本 | 已归档 |
| `使用说明.md` | 被 `auto-memory/nuvolta-working-dir.md` 取代 | 已归档 |
| `启动.txt` | 被 `auto-memory/nuvolta-working-dir.md` 取代 | 已归档 |
| `try_resource.md` | `knowledge/hardware/pin-resource-map.md` | 正文已整合 |

## 错误编号冲突（已解）

`project_rules.md` / `Check-DEEPSEEK.md` 的旧 E001~E017 与 `nuvolta-common-errors.md` 的新 E001~E012/E028/E029 冲突（E008 两套含义不同）。
**裁决**：新 `common-errors` 为权威，旧文件归档。任何引用旧 E 编号的文档以新编号为准。

## 根目录杂项归档（2026-08-16 第二批）

> 根目录散件 / 历史 / 备份收敛，**移动而非删除**（可逆）。

| 归档文件 | 性质 | 状态 |
|---------|------|------|
| `manual-op` | manal-op 旧版（无脚本引用，replay 用 manal-op） | 废弃 |
| `test1.cpp` | NU6801 PMIC 测试程序（非本芯片 DALI/NU1201） | 参考代码 |
| `EditScript1.pas` / `ExportCurrentSheet.pas` / `ExportFullNetlist.pas` | Altium Designer 网表导出脚本 | 历史脚本 |
| `Offline Coding.docx` / `Offline  Coding 全景工作流.txt` | 离线编码文档 | 历史文档 |
| `stdafx_pre_k7rename_backup.h` / `stdafx_pre_path_backup.h` | StdAfx.h 改名前备份 | 备份 |
| `PROGRESS.md.bak_unify_k7_20260816` | K7 统一前备份 | 备份 |
| `debug.log` | 空日志（0 字节） | 空文件 |
| `_add_measure_osc.py` / `_fix_tm300_301.py` / `_rename_trim_node.py` / `_sync_tm300_301_gen.py` / `_append_sub_measures.cpp` / `_tm_batch_a~d.cpp`（9 个） | 一次性临时脚本 / 历史批次生成 | 临时脚本 |
| `OVP.cpp` | `references/code/OVP.cpp`（案例已归档，根目录原件移除） | 案例重复件 |

## 历史一次性脚本归档（2026-08-16 第三批）

> 根目录灰色地带脚本收敛，**移动而非删除**（可逆）。保留 `input_guard.py`（deploy-agent 键鼠屏蔽组件，被 auto_sts8300.py 引用）。

| 归档文件 | 性质 | 状态 |
|---------|------|------|
| `patch.py` | auto_sts8300.py 提速打补丁（一次性） | 历史一次性 |
| `extract_stdafx_from_transcript.py` | 从旧 transcript 提取 StdAfx.h（一次性恢复） | 历史一次性 |
| `restore_stdafx.py` | recover_stdafx.h.txt → StdAfx.h 字节写回（一次性恢复） | 历史一次性 |
| `gen_tm206_425.py` | TM206-425 批量生成器（历史） | 历史一次性 |
| `gen_insert_tm403_425.py` | TM403-425 批量插入生成器（历史；skill 引用已改 `_archive/` 路径） | 历史一次性 |
| `gen_tm216_402.cpp` | TM216-402 生成输出快照（历史） | 历史一次性 |

## 还原方法

若某处因归档报错：从本目录把文件 `Move-Item` 回根目录即可（字节未改）。
