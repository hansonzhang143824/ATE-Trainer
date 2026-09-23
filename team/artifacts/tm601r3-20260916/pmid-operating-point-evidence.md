# PMID 口径证据（A 项）— 已部署实现反证「15 V 台阶在 PMID=5 V 下成立」

> 时间：2026-09-16 23:5x +0800 ｜ 性质：**只读代码证据 + 推断**。归口：本文件给 `t2/t7/t8` 用，**不是电气签核**。
> 证据源：`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`（部署态，只读）= 469,714 B / Python 明文 `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`。
> 方法：python 按 `DUT_API int <Name>(short funcindex` 定界切函数体后打印 `.Set(`/`iset`/`SetOn` 行（本次**未**用「最近前置 DUT_API」错法；定界方式见 t45 的方法论教训）。

## 1. FACT：部署态 `TM600_HS_RDSON`（L9057-L9216）的实际激励

| 行 | 内容（逐字） | 含义 |
| --- | --- | --- |
| 9081 | `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1)` | 闭集 **7 个**：**无 K46/K48/K76/K109/K110**（与门禁实跑「缺失=[48,76]」一致） |
| 9086 | 注释：`ATE excitation per the plan (DFT/OVERVIEW, BD-08): PMID 15 V, VBAT 4.2 V, VDRV 5 V.` | 部署态按 **PMID=15 V / VBAT=4.2 V** 实现 |
| 9097-9115 | `SW12_U1REF_BST_ACM.Set(FV, 0→5→10→15→20, ACM200_10V/20V/40V, ACM200_100MA, RELAY_ON)` 与 `PMID_HG2_FXVI.Set(FV, 0→5→10→15, FXVIe_PLUS_10V/20V/30V, …)` **交替** | **BST−SW 台阶**：每一步 `BST = PMID + 5`，BST 始终领先 PMID 5 V |
| 9100 | 注释 `// step 1: PMID 0 V, BST-SW 5 V` | **step1 的 BST 设置就是 `Set(FV,5,ACM200_10V,…)`** |
| 9104 | 注释 `// step 2: PMID 5 V, BST-SW 5 V` | **step2 的 BST 设置是 `Set(FV,10,ACM200_20V,…)`**（因 PMID 已达 5 V） |
| 9114 | 注释 `// step 4: PMID 15 V, BST-SW 5 V (FET on -> SW follows PMID)` | 部署态的最终操作点 = **PMID 15 V / BST 20 V / BST−SW 5 V** |
| 9174-9186 | 反向台阶 `15→10→5→0` 与 `10→5→0` 交替 | 与上电对称；**与 `voltage-inference.md:159-160` 的下电台阶一致** |

**⇒ 部署态 TM600 的 15 V 台阶是「每一步都维持 BST−SW=5 V」的条件序列**，不是「BST 固定在 20 V」。这与 `voltage-inference.md`（L142 PMID=15、L154-160 台阶表）完全吻合，说明该文档描述的是**部署态那条 15 V 台阶**。

## 2. FACT：部署态 `TM640_BOOST_HS_OCP`（L7503-L7605）——同族 5 V 操作点的既有先例

| 行 | 内容 |
| --- | --- |
| 7492 | `// DFT: vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5] vset[vdm,1]` |
| 7512-7513 | `// 电流通路: PMID→FPVI0 High (K83)…; BST 供电 SW12_U1REF_BST_ACM (K48+K76)`；`cbite.SetOn(…, K48_ACM5_AMP_REF, K76_ACM_BST, …)` |
| 7517 | `// DFT: vbat=3.5V pmid=5V bst_sw=5V vdrv=5V vdm=1V` |
| 7518/7520 | `FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10A, RELAY_ON)`；`VBAT_PD3_FXVI.Set(FV, 3.5, …)` |
| 7521 | `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, RELAY_ON); // PMID=SW=0V, BST-SW=5V` |
| 7524 | `PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, …, RELAY_ON); // PMID=5V, SW 跟随到 5V` |
| 7526 | `SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, RELAY_ON); // SW=5V, BST-SW=5V` |
| 7566-7570 | 下电：`Set(FV,5,ACM200_10V)` 与 `PMID→0` 交替，`// BST-SW: 5V→0V` |

**⇒ 本板既有「PMID=5 V + BST−SW=5 V」的已部署先例就是 TM640**：`vbat=3.5/pmid=5/bst_sw=5/vdrv=5`，BST 用 **ACM200 10 V 档 100 MA**、两步（`Set(FV,5)` 当 SW=0，`Set(FV,10)` 当 SW=5）。这与**新版 TM600 DFT 的 `vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5]` 逐字相同**。

## 3. FACT：部署态 `TM601_LS_RDSON`（L9217-L9353）的 BST 设置

| 行 | 内容 |
| --- | --- |
| 9269 | `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON)` ← **部署态 TM601 已经在驱动 BST 到 5 V** |
| 9277-9279 | `0x59=0x20`（DIS_CLK）、`0x5A=0x01`（**TM_LSON=1**）、`0x61=0x4B`（EN_FORCE_ON） |
| 9338/9344 | 下电 `Set(FV,0,ACM200_10V,ACM200_100MA,RELAY_ON)` → `Set(FV,0,ACM200_10V,ACM200_10MA,RELAY_OFF)` |

**⇒ 重要更正（第 4 次，对旧 run 的叙事）**：旧 run 反复陈述的「TM601 无 BST / 已移除 ACM 激励」**与部署态代码不符**——部署态 TM601 **在 `:9269` 明确 `Set(FV,5,…)` 驱动 BST=5 V**；只是它的 `SetOn` 未闭 `K48/K76`（故不构成高影响改动）。

## 4. 据此对裁 A 的判定（INFERENCE，标注证据强度）

**结论：A2（改用 15 V）在算术上自我矛盾；A1（PMID=5 V）与已部署先例一致。** 依据：

1. **若 PMID=5 V 而沿用部署态 TM600 的台阶**（`PMID 5→10→15` 与 `BST 10→15→20`），则 BST 会到 **20 V**，而 `BST−SW` 在该台阶的注释语义下**每一步都应是 5 V**——台阶本身按其自身注释就无法维持在 PMID=5 V 的操作点（step4 需要 PMID=15 V）。
2. **部署态 TM600 的 `Set(FV,5,ACM200_10V)`** 恰好就是新版 DFT 单值 `vset[bst_sw,5]` 的直接实现；**部署态 TM640** 则给出了「PMID=5 V 固定 + BST−SW=5 V」的**两步**完整既有先例，且其 DFT 行与新版 TM600 的 DFT 轨值**逐字相同**。
3 **旧黄金/`voltage-inference.md` 的 PMID=15 V 台阶 = 部署态 TM600 的那条台阶**，即它是**已被实现的历史操作点**，不是与新版 DFT 并列的候选；两者关系是「同一支路的两种工况」，不是「同一工况的两个值」。

**⇒ 建议裁定（供用户确认）**：以新版 DFT 的 `PMID=5 V` + `BST−SW=5 V` 为本次操作点；`voltage-inference.md` 的 15 V 台阶标注为**已部署的另一种工况（PMID=15 V 台阶）**并保留；**不得**把 5 V 的 DFT 与 15 V 的台阶拼在一起（会产生 20 V BST 台阶）。

**证据强度**：`TM640` 先例 = 已部署代码 + 同构 DFT 行（强）；`TM600` 部署态 step1 的 5 V 设置 = 已部署代码（强）；「串台阶会产生 20 V」= 由台阶注释推得（中，属 INFERENCE，未实测电压）。

**仍待独立复核**：子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5` 仍在运行；其上文只给了 A1 的原始理由（「与唯一权威一致 + Check 自洽」），**未包含本文件第 1/2 节的代码级反证**。⇒ 本结论标为**强证据但未经独立复核**，最终由 `t8` 独立审查 + 用户裁定收口。

## 5. 边界

只读 `test.cpp`，未改任何文件；未落盘 payload；`devel` 零写入；目标树哈希未变（`15c7d2b8…`）；**无机台/电性验证**；未主张任何电压在硬件上正确。
