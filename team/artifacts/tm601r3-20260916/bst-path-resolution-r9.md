# 四方矛盾消解 + 两项决定性事实（R9）

> 时间：2026-09-17 01:0x +0800 ｜ 只读实测（`test.cpp` 部署态 `15c7d2b8…`）+ 引用复核。归口：`t2`（物理）、`t6`（契约）、`t8`（独立审查）；最终裁定权在用户。

## 1. 决定性事实 A：本板「闭 K48/K76 且驱动 ch5」的函数普查（我实测，逐函数定界）

| function | from | to | 闭 K48 | 闭 K76 | 驱动 ch5（`Set(FV,>0)`） |
| --- | --- | --- | --- | --- | --- |
| `TM607_BUCK_LS_ZCD` | 6985 | 7072 | **True** | **True** | **True** |
| `TM608_BOOST_HS_ZCD` | 7073 | 7159 | **True** | **True** | **True** |
| `TM609_BOOST_HS_NEG` | 7160 | 7249 | **True** | **True** | **True** |
| `TM640_BOOST_HS_OCP` | 7503 | 7605 | **True** | **True** | **True** |
| `TM600_HS_RDSON` | 9057 | 9216 | **False** | **False** | True |
| `TM601_LS_RDSON` | 9217 | 9353 | **False** | **False** | True |

⇒ **本板既有 4 个已实现函数都「闭 K48+K76 并驱动 ch5」，其中 3 个（TM608/609/640）是 HS 高边项**，与 TM600 同类。**不存在「本板 ACM200 到不了 BST」的证据；相反，有 4 份行为证据表明可达。**

## 2. 决定性事实 B：那条「ACM200 到不了 BST」的注释，其上下文是**黄金案例的另一种安排**

`test.cpp:9024-9033` 逐字（节选）：
```
// BST-SW RAIL: ALTERNATIVE NOT ADOPTED (record, do not implement the golden's arrangement).
//   The golden builds BST-SW from two independent ground-referenced sources (BTST_ACM + SW_ACM) and
//   thereby frees an FPVIe channel. That is NOT adopted for this run, on fixture evidence rather
//   than preference: ACM200 reaches SW only and cannot reach BST, and FXVIe_PLUS reaches PMID/PGND
//   only with its low side returning to AGND_F, so it cannot form a floating pair. ...
//   PRECONDITION TO ADOPT: fixture evidence proving a reachable, float-capable non-FPVIe source
//   pair for BST-SW. (Counter-evidence to date: ACM200 does not reach BST.)
```

**消解（INFERENCE，证据强）**：
- 该段讨论的是**黄金案例那套「用两个独立地参考源 BTST_ACM + SW_ACM 拼 BST−SW 以省下一个 FPVIe 通道」**的安排；作者要论证的是「**它无法构成一对**」。
- 括号里的「`ACM200 reaches SW only and cannot reach BST`」**是黄金安排下的事实陈述**：在黄金拓扑里 ACM200 被用来驱动 **SW**，而 BST 由 `BTST_ACM` 驱动 ⇒ 「ACM200 到不了 BST」说的是**在那套两源拓扑里它不在 BST 上**，**不是**「本板硬件上 ACM200 的 ch5 接不到 BST」。
- 与 §1 的 4 份行为证据、`SCH-Connect-Map.txt:672-674`（`S5_ACM200_FH5 → K48 → K76 → BST_F`）、以及 `relays.md` 的 Share 语义完全一致。
- ⇒ **该注释是「对黄金安排被否」的局部论证，被字面扩张后与硬件事实冲突**；不应作为「ch5 不可达 BST」的证据。**该句并不与端子图矛盾——是我的引用方式越出了它的上下文**（对我 R8 回执里把它读作「注释与端子图直接矛盾」的更正）。

## 3. 决定性事实 C：部署态自己写明「11/7.5 mΩ 与 PMID=5 V 配对」

`test.cpp:9035-9037` 逐字：
```
// TWO-PROVENANCE CORROBORATION (for the evidence chain): the archived revision pairs 11 / 7.5 mohm
//   with pmid 5 V, while DFT.csv pairs 10 / 8 mohm with pmid 15 / 9 V. That independently supports
//   the ruling that two sources coexist, with OVERVIEW governing the acceptance limits.
```
⇒ 部署态实现者**已经认定**：**`OVERVIEW` 的 11/7.5 mΩ 与 `PMID=5 V` 属于同一套来源**，`DFT.csv` 的 10/8 mΩ 与 15/9 V 属另一套。这正是**修改后工作簿的取值**（11/7.5 mΩ + `vset[pmid,5]`）。
⇒ **对我 R8 回执中「四字段耦合、不能只挑 PMID」的更正**：耦合确实存在，但**工作簿那一套（5 V + 11/7.5）是自洽的一套**，`DFT.csv` 那一套（15/9 V + 10/8）是另一套；**不是同一个工况的四个零散冲突字段**。据此，A 项的问题变成「**选哪一套来源**」，而部署态与门禁都站在工作簿这一套（门禁期望集 `[48,60,61,76,83]` 正是 `pmid2sw`+`bst2sw` 两支的并集，对应 PMID=5 V 工况）。

## 4. 由此得到的可执行结论（不改任何文件，仅登记）

1. **TM600 的正确修法**：在 `:9081` 那一次 `SetOn` 内**补 `K48_ACM5_AMP_REF` + `K76_ACM_BST`**（同一次调用、完整集合），使 `{K48, K60, K61, K76, K83}` 同时成立 ⇒ 这正是 `TM640:7513` 的形状，也正好补齐门禁的 `missing=[48,76]`。
2. **TM601 的修法**：其 `:9255` SetOn 目前 `{K154,K155,K60,K61,K13,K85,K57,K126}`，而 `:9269` 已在驱动 ch5=5 V ⇒ **要给 TM601 登记 BST 腿（K48/K76）**，否则 5 V 永远到不了 BST（这正是用户指出的缺口，**现在两侧证据一致**）。
3. **BST 单端值**：TM600（SW 跟随到 5 V）需 `BST_abs = 10 V` 才有 `BST−SW = 5 V`（TM640 形状，`:7521→:7526`）；TM601（SW≈0）单值 `BST = 5 V` 即得 `BST−SW ≈ 4.99 V`。
4. **多源互斥**：`TM641/643` 的既有做法（`:7598/:7621/:7714` 注释「K48/K76 把 ch5 输出接 BST ⇒ 该源全程 RELAY_OFF 不驱动」）证明**必须显式释放**——因为 ch5 一旦经 K48/K76 接上 BST，其它函数的闭集若也含 K48/K76 就会把 ch5 一并接上。

## 5. 仍未证实（不得写成已证）

- `K48/K76` 的**实际物理贯通**（继电器动作/端子连续性）——需台架或端子测量，本环境不可做。
- `vset` 的权威语义（工作区无 DFT 工具手册）；`FV+FI` 在 PMID 上能否共存。
- 部署态 TM600 的 20 V 台阶**是否真的到达过 BST**（现证据只说明它**没闭合 K48/K76**，未闭合即按默认投改道 ⇒ 大概率未到达，但**属 INFERENCE**）。
- 第二个独立复核 `e1aec5f2-…` 尚未回收；本文件结论**未经其复核**。

## 6. 边界

只读；未改任何脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；**无机台/电性验证**。
