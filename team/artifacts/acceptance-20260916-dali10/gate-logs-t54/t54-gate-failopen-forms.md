# 门禁 fail-open 形态登记（本 run 累计三类）

- 触发：schematic-expert 归纳三类"门禁形态风险"，主题统一为**要 fail-closed**；本记录逐条复核并存档。
- 适用范围：本 run（`acceptance-20260916-dali10`）的门禁链；**均为静态/行为层面的门禁语义问题**，与电性无关。

## 形态 1｜展开器静默截断（工具≠语义）

| 项 | 内容 |
| --- | --- |
| 位置 | `scripts/verify_relay_trace.py` L39-44 `parse_defines()`：`#define\s+(K\d*_\w+)\s+(\d+)` **只捕获一段数字** |
| 量级 | StdAfx.h **多值宏 209 个，209/209 全部被截为首值**（单值宏 282 个） |
| 例 | `K_FPVIH_TO_BST_A` parsed=46 / true=`[46,48,76]`；`K_FPVIL_TO_BST_B` parsed=109 / true=`[109,110]` |
| **是否影响本 run 判据** | **部分/欠严（under-strict）**：`cap_defs` 只收录 Cap 家族（多值宏 = 0）⇒ **Cap 别名↔规范名映射这条路不受影响**（我原判这条成立）；但 `n = defines[r]` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** 被**当数字使用**，而 `r` 来自 `parse_setons()`（**原样取 SetOn 实参、不做宏展开**）⇒ 当 SetOn 写**多值宏名**时**只校验其首值那一个继电器**（例 `K_FPVIH_TO_PGND_A=154,155` ⇒ 只校验 154；`K_FPVIH_TO_BST_A=46,48,76` ⇒ 只校验 46）。⇒ 故它**不是假通过**，但**不能作为"多值宏逐条校验"的证据**。 原判词（保留留痕）：「**否** —— 调用点仅 `verify_relay_trace.py`（L294 载入）；其判据真正消费的 `cap_defs` **只收录 Cap 家族**（实测 19 个，**多值宏 = 0**），L316 的 `defines[name] in canon_by_ch` 比较由单值 Cap 宏提供；L376 的 `n` 之后未再参与数值比较 ⇒ **`relay-trace` 的 PASS 不是被截断值造成的假通过** |
| 护栏 | **先测展开器、再信展开**；判"某宏闭了哪些 K"一律以 `StdAfx.h` 原文逐字展开 |
| 留证 | `gate-logs-t54/t54_truncation_blast.py` / `t54-truncation-blast.log`、`t54_relaytrace_settled.py` / `t54-relaytrace-settled.log` |

## 形态 2｜子集判定（多余闭合不可见）

| 项 | 内容 |
| --- | --- |
| 位置 | `verify_bst_sw_sequence.py` `check_contract_closures()`：`missing = sorted(set(exp) - data['nums'])` |
| 语义 | **只判"期望 ⊆ 实际"**；额外闭合仅在 `--check-extra` 下才报（L458-465，`allowed = exp ∪ budget`） |
| 后果 | **"GREEN" ≠ "闭合集被约束"**：本批方案 B（仅闭 ACM200 族 `{48,76}` + SW `{60,61}`）由**工程判断与契约一致性**保证，**门禁不具备反证能力** |
| 护栏 | 若要使 B 受门禁保护，须**另立明确决定**启用 `--check-extra` 并定义 budget 池（Captain 已令写入 `build-report.attributionLimitations`） |
| 留证 | `build-report.json` → `attributionLimitations[0]` |

## 形态 3｜空目标集 fail-open（契约断言被静默跳过）★ B-7

| 项 | 内容 |
| --- | --- |
| 位置 | `verify_bst_sw_sequence.py` **L490** `targets = derive_targets(...)`；**L497-499** `if not targets: print("[scan] … 空 PASS"); return 0` |
| 关键 | **早退发生在任何判定之前**；而契约闭合断言在 **L502/L515** 才执行 ⇒ 空集时**整段被跳过** |
| 且 `targets` ≠ 判定范围 | `check_contract_closures(..., scope=)` 的 `scope` 来自 **`resolve_scope()`（L409-413）⇒ `DEFAULT_TM_SCOPE`（L259）**，**不来自 `targets`** |
| 触发条件 | `--src` 指向**不含 `rampi_capv(` 家族**的源（`derive_targets` L96-114 按函数体内是否含 `rampi_capv(` 筛选）—— 例如**只含 TM600/TM601 的副本**，正是本 run TM600/TM601 专用夹具的形态 |
| 行为实测 | `--src <候选payload>` ⇒ `[scan] … 非 ZCD/OCP 家族, 空 PASS` / **exit 0**；**加 `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON` 后仍"空 PASS" / exit 0** ⇒ **`--tm-scope` 救不了**（早退在断言之前） |
| 自相矛盾 | 同文件 **L506-507** 自述原则："*契约是高电流路线闭合集合的权威，**缺失必须红而不是静默跳过***" ⇒ 该原则**只落实在"契约读不到"**这条路径；"目标集为空"仍静默 PASS ⇒ **同一条原则只落实一半（fail-open）** |
| 对本 run 的含义 | **任何 `targets=0` 的门禁 PASS 都不能作为 `t54` 判据的证据**（它没检查任何东西）；"未落盘 ⇒ 无法用被审脚本判候选 payload"即由本形态直接造成 |
| 护栏（两选一） | **(a)【schematic-expert 主张，我赞成】把 `if not targets` 改为 FAIL**（或至少要求"契约断言已执行"）——与其 L506-507 的既定原则一致、改动最小；**(b)** 保留现行行为但**要求日志出现 `targets=N (N>0)`**，并在验收记录中写明 N>0 |
| 归属 | **本批不授权改 `scripts/`**（Captain 裁定）⇒ 属**独立 owner 决定**；修改时**不得动 `gate_baseline.json`**（28 B / `021015da…02cb1d`） |
| 留证 | `gate-logs-t54/t54_verify_failopen.py` / `t54-failopen-verify.log`、`gate-logs-t33/t54-execution-constraint.md`、`build-report.capabilityLimitations[0]`（id=**B-7**） |

## 三条共性

三者都是**"检查没执行/覆盖不足"却返回成功**的形态（fail-open）：
1. **工具≠语义**（展开器截断）——用错工具；
2. **判据不对称**（子集判定）——只查缺、不查多；
3. **作用域早退**（空 targets）——什么都没查就 PASS。
⇒ **共同护栏方向：要 fail-closed** —— ① 先测展开器再信展开；② 需约束闭合集须显式 `--check-extra` + budget；③ 空 `targets` 应 FAIL 或强制记录 N>0。

## 边界

静态连通性/门禁语义层面；**非电性结论**；**无机台实测**；**门禁 PASS ≠ 电性签核**。
