# 步骤 14 检验（Verification）

> 三层检验：**输入同步门**（生成之前，判要不要重生成）+ **单项目冒烟自检**（一个函数生成后秒级自检）+ **跨项目统一门禁**（整批生成后脚本化校验 + 编译）。
> 关联：`rules-registry.md` B-001（批量生成纪律）、`framework.md`（6 步结构）、各 verify 脚本。

---

## 第零层：输入同步门（生成之前 · 2026-09-13 新增）

> 先于一切「是否要重生成」判定。管**输入侧派生文件是否与源同版本**（内容哈希，不看 mtime）。

- 落点：`check_input_sync.py`（退出码 0 = 全 MATCH = **无需修改**；1 = 有落后项）
- 两条版本链：

| 组 | 链 | 版本记录落点 |
|---|---|---|
| DFT | `Dali_testmode.xlsx` → `dali_tm_meta.json` → `test_conditions.yaml` | meta `_syncStamp.dftSha256` / yaml `_sync.metaSha256` |
| SCH | `Dali-SCH.csv` → `SCH-Connect-Map.txt` + `Component-Statistic.txt` | `validation_manifest.json.txt` 的 `input.sha256` + `artifacts.*_sha256` |

- **IN SYNC → 什么都不用改**（跳过 Step0/SCH 重生成，直接进 CBIT-Definition 与生成循环）。
- **OUT OF SYNC → 只重生成落后那一组**；DFT 组顺序不可反（先 meta 后 YAML，YAML 的 stamp 引用 meta 哈希），复跑本门至 IN SYNC。
- 与 Step2 的 dll mtime 门分工：本门 = 输入侧**版本一致**；dll mtime 门 = 产物侧**新鲜度**（编译发布时效）。两者独立，本门在前。

## 第一层：单项目冒烟自检

> 一个函数生成后立即自检，秒级、无需编译。对应 B-001「先单函数冒烟」的前置工具。

- 落点：`verify_single_fn.py`（骨架已建，检查项已定，待实现）

检查项（**已确认 5 项**）：

| # | 检查项 | 说明 | 来源 |
|---|---|---|---|
| 1 | 占位符残留 | `__X__` 无残留（替换后断言，有→FAIL） | B-001 |
| 2 | 分号在注释前 | `* 1e3;  // comment`（防 C2143） | B-001 |
| 3 | 花括号配平 | `{}` 数量匹配 | B-001 |
| 4 | CRLF 字节干净 | DLP 字节模式无 `\r\r\n` | B-001 |
| 5 | 6 步结构完整 | Step1~6 占位符全部替换 | framework.md |

> 踢出：占位符降序替换 = 生成期纪律（留 B-001，非事后检查）；参数完整性 = 跨数据比对（归第二层门禁 `check_testitems_meta.py`）。

## 第二层：跨项目统一门禁

> 整批生成后统一跑，脚本化校验 + 编译。

| 脚本 | 校验内容 |
|---|---|
| `check_testitems_meta.py --require-all` | meta 全覆盖门（正向） |
| `check_testitems_meta.py --require-scope <批次>` | 反向覆盖门（含参数完整性） |
| `verify_relay_trace.py --meta` | 反向检查 E（Cap 供电判定） |
| `verify_awg_params.py` | AWG/Toggle 参数 E005 |
| `gen_cbit_defines.py --verify <StdAfx.h> [--map <Map>]` | CBIT 定义校验（⚠ 两个参数都必填，裸写=argparse exit 2 而非校验失败） |
| `gen_path_defines.py --verify` | 通路定义校验 |
| `fast_rebuild.ps1` | 编译（0 errors / 0 warnings） |

## 与 B-001 的关系

> **已确认**：`verify_single_fn.py` = 把 B-001「生成后自检」（分号/括号/CRLF/占位符残留）脚本化，充当「先单函数冒烟」的秒级前置工具。
> 流程：**冒烟脚本（每 TM，秒级不编译）→ 编译（按批次规模，见 `context-management.md §2.2`：≤5 个写完编一次 / >5 个每 5 个编一次 + 末尾一次）→ 归位后再编译一次（查组装）→ 跨项目门禁 → 批量放量**。

---

## 待确认

- [x] 冒烟自检 5 项（A 组）已定；降序替换（B 组）留 B-001；参数完整性（C 组）归门禁
- [x] B-001 强制层更新为 `verify_single_fn.py`
- [ ] `verify_single_fn.py` 实现（5 项检查逻辑 + 入参/判定）
