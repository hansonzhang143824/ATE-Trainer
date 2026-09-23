# t13 任务契约（预置稿 · 待 t11/t12 completed 后正式创建）

> 状态：**草稿**。按用户纪律 3，本任务在 **t11 与 t12 均标为 completed 之后**才创建；
> `sourceTaskId = t5`（**不覆盖**已 failed 的 t5）。本文件只是把创建时不需再想的内容预先落盘。

## 目的

在 `D:/PROJECT6-DALI/ForCodexDebug` 落盘 TM600_HS_RDSON / TM601_LS_RDSON，`D:/PROJECT6-DALI/devel` **只读且严禁改动**。

## 创建前置条件（缺一不可）

1. `t11` = completed（`test-plan.json` 含 U11 与 settle 1 ms；`validate_team_artifact.py test-plan` exit 0）。
2. `t12` = completed（`setup-contract.json` 含 U10/U11、QVM 措辞降级为 `candidate, disputed with t2`、BST 资源更正为 `SW12_U1REF_BST_ACM`；`validate_team_artifact.py setup-contract` exit 0）。
3. 契约**冻结**（产物内含单调 `revision` + `generatedAt`）。

## 输入固定（**python 明文 SHA-256**，不得用 `Get-FileHash`）

- `team/artifacts/acceptance-20260916-dali10/test-plan.json`（pin：内容键 + locator + **revision 字符串** + 该时刻现算哈希）
- `team/artifacts/acceptance-20260916-dali10/setup-contract.json`（同上）
- `test-plan-tm600-tm601-measurement-excerpt.md`（逐字调用形式）
- `dft-ir.json`（限值与 `iset` 语义）、`schematic-ir-sensing.json`（`dfdPairVerdicts` / `requiredPairAssertions`）
- 目标基线：`source/test.cpp` = `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`（434629 B，8878 行）

## 必做步骤

1. **权限自检**：对目标目录做 1 字节写探针（写完即删）。**若被拒 → 立即停手，回报"payload 就绪、权限未生效"；不得把权限失败写成实现失败或完成。**
2. **写前备份**：备份 `test.cpp` 到 run 目录并校验与实盘逐字节相同。
3. **复核 payload**：以 `implementation-payload-TM600-TM601.pulse2ms-variant.cpp`（`delay_ms(1)`，裁定 (b)）为准；核对 BOM + CRLF（无孤立 LF）。
4. **写入**：**python 字节模式**追加（文本模式会把 CRLF 变 `\r\r\n`；PowerShell 复制会得到空/DLP 密文文件）。
5. **写后回读**：python 明文回读并比对哈希、行数、BOM/CRLF；记录 before/after。
6. **同步元数据**：`gen_testitems_meta.py` + `gen_test_conditions.py`，使 `check_testitems_meta.py --require-all` 通过（**不改门禁脚本**）。
7. **跑 gates**：以**相对基线的新增量**判定（KNOWN-RED 与 NEW-RED 分开；退出码 + 日志路径 + 日志哈希）。
8. **产出 `implementation-manifest.json`**（schema **PASS**）：含备份路径、前后明文哈希、复读校验、limitations（U1/U2/U3–U8/U9/U10/U11/BD-06/BD-07 + 边界句）。

## 解锁

t13 **completed** 后才解锁 **t6**（独立规则审查）与 **t7**（TM600/TM601 能力核验）。

## 边界（纪律 5）

- **不授权真实机台 / 硬件电性验证**；SIGN-CONVENTION（U11）**只作 bring-up limitation**。
- **编译闭环 ≠ 电性签核**；报告须把"编译成功"与"电性验证"**分开陈述**。
- 只改 `ForCodexDebug`；`devel`、`scripts/`、`team/`、`project/DALI/input/` 一律不动。
