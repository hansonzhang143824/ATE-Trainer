# t25 复核回复与自我更正（rule-reviewer 意见的回应）

- 日期：2026-09-16
- 上游意见：`team/artifacts/acceptance-20260916-dali10/review/t25-independent-opinion.md`
  （rule-reviewer，只读；结论 F1/F2/R1/R2/F3 全 ACCEPT，无 reject，附 3 条非阻塞 finding）
- 本文件性质：**对已终态 t25 的补充记录**（t25 已提交 failed，attempt 不可再更新；
  本文件与 `t25-closure-report.md` 的附录等价）
- 复核证据：`t25-reviewer-response-evidence.json`、`t25-capdefs-and-branch.json`

---

## 1. ✅ 接受 rule-reviewer 的 F-1 更正 —— **我原表述错误，现撤回**

**我原表述（错误）**："`K_SW_BST_Cap`(token `SW_BST`) 在修复后不再被 `SW` 触发闭合要求"。

**独立复算（我自己的运行，未复用其脚本）**：

```
fam_intersect({'SW'}, 'SW_BST')  = ['SW']    ← 规则真实调用形态 ⇒ 仍命中
fam_intersect({'SW_BST'}, 'SW')  = ['SW_BST']
```

判据：`'SW_BST'.startswith('SW')` 之后是 `'_'`（非字母数字）= **合法 token 边界** ⇒ 命中。
真实数据复算（`t25-capdefs-and-branch.json`）：

| cap token | cap_defs 归一化目标 | `fam_intersect(powered, token)` | 修复前会产生告警 | 修复后会产生告警 |
| --- | --- | --- | --- | --- |
| `SW_BST` | `K57_CAP_BST_SW` | `['SW']` | **是** | **是** |
| `SW1_BST1` | `K45_Cap_SW1_BST1` | `[]` | 是 | 否（假阳性已消） |
| `SW2_BST2` | `K44_Cap_SW2_BST2` | `[]` | 是 | 否（假阳性已消） |
| `VBUS` | `K5_VBUS_Cap` | `['VBUS']` | 是 | 是（F3，需 meta 侧修） |

⇒ **rule-reviewer 的更正成立**；我关于 `SW_BST` 的表述是错的，**撤回**。
（结论层无影响：`SW_BST` 与 `BST_SW` 归一化到同一继电器，门禁上表现为同一条
`TM601_LS_RDSON: 静态供电 SW 但未闭稳压电容 K57_CAP_BST_SW` 告警，修复前后都在。）

**我 F2 修复的准确收敛表述（供后续引用）**：
> 全树 A/B 中，F2 只消除 **2 条**告警（`K44_Cap_SW2_BST2`、`K45_Cap_SW1_BST1`）；
> `SW_BST` 的匹配**未被改动**（它是合法 token 边界命中），也没有从任何输出中消失。

## 2. ✅ 接受 R2 结论：同一物理继电器（我已独立复算）

| token | `#define` | 通道号 | 归一化目标 |
| --- | --- | --- | --- |
| `SW_BST` | `K_SW_BST_Cap` | 57 | **`K57_CAP_BST_SW`** |
| `BST_SW` | `K57_CAP_BST_SW` | 57 | **`K57_CAP_BST_SW`** |

`canon_by_ch[57] = K57_CAP_BST_SW`（`verify_relay_trace.py:274-286`）⇒ 两 token 指向同一继电器
⇒ 我原登记为 UNKNOWN 的 `R2-01` **降级为已解决（非缺陷）**。同时确认 reviewer 的补充：
`K21_VAC_Cap`(21) 与 `K_VAC1_Cap`(21) 亦归一化到同一继电器 ⇒ **R1 的 VAC 折叠在"同一继电器"
意义上正确**，故我的修法无需为 VAC 家族回退（`t25-variant-matrix.json` 亦证明修复前后
VAC 告警均为 0，该折叠是 latent 的）。

## 3. ✅ 接受 F-2（fail-open）—— 已定级为非阻塞，交给 t26/后续任务收口

reviewer 指出的真问题：`run_gates.ps1` 的 `if (-not $stdafx) { ...cbit 门将跳过 }` 属 **fail-open**
（门**消失**而不是变红），"门静默消失"会换形态复发。我同意该定级与方向。

**我的补充证据（为何 F1 修完后该路径已不再是主要风险，但仍应修）**：修复前它**已经真实触发过**
（基线加载失败 + cbit 门缺席 = 11 门），修复后 `cbit` 能被正确分类。但**同类风险仍在**：
`scripts/` 下其它门禁（`path-def`、`bst-sw` 等）仍以 pwsh 读受保护源/配置，
若哪天再出现"读不到"，仍会静默跳过而非变红。
**建议**（留给后续任务，不在 t25 inScope）：在 run_gates 里把"门被跳过"计入 `NEW-RED` 分类器，
或直接改为显式失败；并给其余脚本做一次同样的"授权读者"审计。

## 4. ⚠️ 接受 F-3（与 t26 并发）—— **并据此撤回我向 Captain 提的 (A) 建议**

**实测（只读 `.agent-teams/ate-dali-acceptance/team.json`）**：`t26` 处于 **in_progress**、owner 为
**setup-architect**，其 `inScope` **已包含** `project/DALI/meta/dali_tm_meta.json`，且其验收条目
与我 §F3 提案**同源同向**（TM601 `powered_pins` 不得含 `VBUS`、对齐冻结 ATE、修正 `mi_pins`、
SW/SW1/SW2 分节点、重跑门禁给完整警告清单与 exit、明确 K57 结论）。

⇒ **我撤回给 Captain 的 (A) 建议（"把 t25 inScope 扩到该 meta 并让我落地"）**，
改为推荐 **(B)：不扩 t25 权限，由 t26 单一 owner 落地 meta**；理由：
1. **写冲突**：同一文件同一字段，两个 owner 并发写会互相覆盖，且结论会不一致；
2. **无必要**：t26 已覆盖我提案的全部内容（TM600+TM601+mi_pins+分节点），我落地只会重复；
3. **可验证性**：t26 的 verify 命令与我完全一致
   （`pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t26`），
   而**脚本侧 F1/F2 已经落地并生效** ⇒ t26 的基线加载与 SW1/SW2 判定会直接受益。

**给 t26 的两条实测预警（我已复算，避免它走弯路）**：
1. **t26 声明"`fam_intersect` 前缀碰撞是缺陷"这条已由 t25 在脚本侧修复**（对称 token 边界，
   已过独立复核 ACCEPT）⇒ t26 **不需要**、也**不应**再通过改 meta 去规避 SW1/SW2：
   修复后 SW1/SW2 已不再被 `SW` 命中（`fam_intersect` 实测 = `[]`），meta 侧无需特殊处理。
2. **K57 的预期结论存在一个易混点**：一旦 t26 按真实测量 pin 把 `SW` 写入 `mi_pins`，
   `verify_relay_trace.py:325-326` 的**按 PIN 豁免**会触发，于是 **K57 不再被规则要求闭合**。
   这与 t22 的实现侧裁定（"BST_SW 确实被静态供电 ⇒ 该闭 K57"）**并不冲突，但语义不同**：
   - 规则层（FR-001 模型）：修复后 **不要求** K57；
   - 工程层（t22/payload）：BST−SW 轨真被 `bst_sw 5.0` 供电 ⇒ **建议仍闭**。
   ⇒ t26 的验收条目要求"明确 K57 是否仍应闭合"，请**按两层分别表述**，
   不要写成"K57 是假阳性/应删除"，也不要因为规则豁免就断言"可以不闭"。
3. **门禁预期基线（t26 落地后，脚本侧已含 F1+F2）**：`VBUS` 从 TM601 `powered_pins` 移除 ⇒
   `relay-trace` 消失 1 条（该假阳性）；若 `mi_pins=['SW']` 生效 ⇒ 再消失 1 条（K57 豁免）；
   最终 `relay-trace` 预期剩 **3 条**（TM643 ×2 存量 + TM601 K5_VBUS_Cap 若未移除）；
   另 **2 条裸 `126` 虚构继电器名错误仍在**（属 payload 未落地，见 t23），
   故 `relay-trace` 的 **exit 仍为 1** —— 这不是 t26 的缺陷，须在报告中归因清楚。

## 5. 门禁现状与归属（与 reviewer 一致，复述以备引用）

12 门 = 10 GREEN + `cbit` KNOWN-RED + `relay-trace` NEW-RED；`exit=1`。
`relay-trace` 的 FAIL 直接原因是 **2 条裸 `126` 虚构继电器名 ERROR**（部署态 `test.cpp`
sha256 `3dbceb49…` 的 SetOn 仍含裸 `126`；t23 已改为 `K126_V1P5_CAP` 但**未落盘**）
⇒ 与 F1/F2 无关，归因正确。**t25 未新增任何红。**

## 6. 教学点（写入失败经验，避免复发）

1. **不要用 pwsh 判断受保护源的内容或存在性**：本工作区 pwsh 能看到密文与**另一套元数据**
   （`gate_baseline.json` pwsh 8192 B vs 明文 28 B）⇒「0 命中/尺寸不同」都不能作为结论。
2. **"只改读取方式"的修复也要自证边界**：我把 `$root` 从 `$MyInvocation` 改成 `$PSScriptRoot`
   时引入了新缺陷，只有**以副本运行**才暴露 ⇒ 修 harness 时必须至少用一次"异地位运行"。
3. **对家族/token 匹配，先问"方向"**：`fam_intersect(powered, ptok)` 的命中可能来自
   `ptok` 是 powered 的**前缀**（SW → SW1_BST1）或 powered 是 `ptok` 的**前缀**（VAC1 → VAC），
   两者的正确修法相同（对称 token 边界），但**影响面完全不同**，必须分别用 A/B 全树对照量化。
4. **别把"我没改"当作"我知道它是什么"**：R2 我原登记为 UNKNOWN 的两个 token，
   经 `cap_defs` 归一化后是同一继电器 —— 归一化层是这类误判的高发区。
