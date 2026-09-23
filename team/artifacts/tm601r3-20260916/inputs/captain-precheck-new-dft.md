# Captain 预检：新版 TM601/TM600 DFT 现盘核对（只读）

> 状态：**Captain 自查记录，不是任务交付件**。`t1`（dft-expert）必须自己重提取并自行取证；本文件仅用于给用户裁定提供决策输入，以及给新 DAG 一个可对照的现盘基线。
> 生成时间：2026-09-16 22:1x +0800。所有哈希由同一 Python 进程 `open(path,'rb').read()` 现算。

## 1. 输入现盘

| 文件 | size | Python 明文 SHA-256 | mtime |
| --- | --- | --- | --- |
| `project/DALI/Dali_testmode.xlsx`（**唯一权威**） | 12,210,680 | `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` | 2026-09-16 21:46:39 |
| `project/DALI/input/DFT.csv` | 16,862 | `b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4` | 2026-07-18 16:12:54 |
| `project/DALI/input/DFT_restored.csv` | 16,824 | `0e0c31106586eacc0ef919b2c5a42d78c036e714d905ec9a7121dbffadcd8bc2` | 2026-07-16 18:04:36 |

旧版 `dft-ir.json` 记录的 xlsx 证据哈希为 `d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e` ⇒ **现盘已不是被提取过的那一版**，21:46 之后所有依赖旧读数的结论都必须重算。

## 2. 新版 OVERVIEW 逐字段（sheet=OVERVIEW，header 在 row 1）

### row 132 — TM600（**未变**）

| 列 | 值 |
| --- | --- |
| Item / Level / Name | TM600 / BUBO / HS_RDSON |
| ExpectValue / Unit / Test | 11 / mΩ / direct |
| Special | `Y\n2 FLOAT` |
| Notes | `Rds,on=(PMID-SW)/ISW` |
| Code1 | `vset[vbat,3.5,100e-6,0]` / **`vset[pmid,5,100e-6,0]`（PMID=5 V）** / **`vset[bst_sw,5,1e-3,0]`（BST−SW=5 V）** / `vset[vdrv,5,100e-6,0]` |
| Code2 | `en_tm[]` / `field[(WAKE_UP,1)]` / `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]` |
| Code3 | `delay[1e-3]` / `iset[sw,1,1e-3,0]` / `delay[2e-3]` / `finish[]` |
| Power | `VBAT` / `BST-SW` |
| Dynamic | `ISW` |
| Check | `PMID-SW` / `floating source：V(BST_SW)` |
| de test | `I=0.2A` / `pmid-sw=46mV`（**AMS 域校验值，非限值**） |

### row 133 — TM601（**已修改**）

| 列 | 值 |
| --- | --- |
| Item / Level / Name | TM601 / BUBO / LS_RDSON |
| ExpectValue / Unit / Test | 7.5 / mΩ / direct |
| Special | 空（无 `2 FLOAT`，与 TM600 不同） |
| Notes | `Rds,on=(SW-PGND)/IPMID2SW` |
| Code1 | `vset[vbat,3.5,100e-6,0]` / `vset[vdrv,5,100e-6,0]` / `vset[vbus,5,100e-6,0]` / **`vset[bst,5,100e-6,0]`（BST=5 V —— 关键改动）** |
| Code2 | `en_tm[]` / `field[(WAKE_UP,1)]` / `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]` |
| Code3 | `delay[5e-3]` / **`iset[pmid_sw,1,1e-3,0]`** / `delay[2e-3]` / `finish[]` |
| Power | `VBAT` |
| Dynamic | `SW` / `ISW` |
| Check | `SW-PGND` / `floating source：I(PMID_SW)` |
| de test | `I=1A` / `SW-PGND=0.3`（**AMS 域校验值，非限值**） |

## 3. 与旧 IR 的差异（FACT）

| 字段 | 旧 `dft-ir.json`（TM601） | 新版工作簿（TM601） | 判定 |
| --- | --- | --- | --- |
| BST 轨激励 | 条目内**只有** vbat/vdrv/vbus，**没有任何 BST/bst_sw 激励** | 有 `vset[bst,5,100e-6,0]` | **NEW / 决定性变更**；旧条目缺 BST 登记，正是本轮回炉的根因 |
| 激励源命名 | `iset[pmid_sw,1,1e-3]`（与新版一致） | `iset[pmid_sw,1,1e-3,0]` | SAME |
| Check / Dynamic | SW-PGND / I(PMID_SW) | SW-PGND / I(PMID_SW) | SAME |
| ExpectValue | 7.5 mΩ | 7.5 mΩ | SAME |
| 是否含 "无 BST" 字样 | 条目内**未出现**「无 BST」结论；该推断出现在项目文档、计划与 payload 层 | — | 旧推断**不在 DFT 内**，属下游产物外推 |

> **UNKNOWN（不作断言）**：无法从现盘判定「旧版工作簿本身是否已含 `vset[bst,…]` 而仅被旧提取漏记」——旧版 xlsx 字节已不可得。两种情形对本轮的处置相同：**以新版为唯一权威重建**。

## 4. 两处待裁定/待核实的实质差异（FACT 并列，不取一）

### D1 — TM600 的 PMID：5 V vs 旧黄金/规则 15 V

- 新版工作簿：`vset[pmid,5,100e-6,0]`（row 132 Code1），并配 `vset[bst_sw,5,…]`。
- `knowledge/hardware/voltage-inference.md`：`L18 PMID_FOVI.Set(FV, 15) → PMID = 15V`；`L142 DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]`；`L151-160` 的 TM600 台阶表以 PMID=15 V / BST=20 V 推演。
- 两处**不能同时成立**为同一操作点。旧管线已把「5 V vs 15 V」记为待对账项（`ROLE_ROUTING.md §4` 冲突隔离）。
- **需裁定**：哪一侧是本轮操作点；另一侧保留为历史/参考并标注适用域与重开条件。

### D2 — TM601 的 BST=5 V 语义

- 新版工作簿只给 `vset[bst,5,100e-6,0]`，**没有** `bst_sw`（差分）行；而 Notes 要求 `Rds,on=(SW-PGND)/IPMID2SW`，即 SW 是激励回路的一个节点。
- 若 BST 是**相对 GND 的单端轨**：LS 导通时 SW-PGND=0.3 V（AMS 域值）⇒ BST−SW ≈ 4.7 V，且 BST−SW 会随 SW 变动。
- 若 BST 实际是**相对 SW 的 5 V 轨**（即 BST−SW=5 V，TM600 的写法）：需在物理上由 `vset[bst,…]` 之外的方式建立。
- **需核实**：由 schematic/Setup 给物理事实、test-strategy-architect 给操作点；**实现者不得猜**。
- 另注：新版 row 133 的 `Power=VBAT`（不含 SW/BST），而 Code1 给了 vbus 与 bst 两条轨 —— 该内部表述差异由 `t1` 逐条登记。

### D3 — TM601 的源命名三方并存（待 t1 归口，不阻断）

| 来源 | 激励写法 |
| --- | --- |
| 新版工作簿 row 133 | `iset[pmid_sw,1,1e-3,0]` |
| `reg_config/tm601.sv` | `iset[pmid_sw,1,1e-3]` |
| `input/DFT.csv` record 20 | `iset[sw2pgnd,1,1e-6,0]`（另 ExpectValue=8 mΩ、vset[vbat,4.2]） |
| 旧契约 `aliasResolution.sw2pgnd` | 通道 CH0 Low→SW `[60,61]`、High→PGND `[154,155]` |

## 5. 旧契约里与 TM601 相关的现盘登记（供 t6 对照）

- `tmDeltas.TM601`：`scopePins=[SW,PGND,PMID,VBUS,VBAT,VDRV,V1P5,AGND]`、`relaySet=[3,7,60,61,83,86,130,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,154,155]`、`aliasesUsed=[sw2pgnd]` —— **不含 K110**，且**未登记 BST 供电源**。
- `tmDeltas.TM600`：`scopePins` 含 `BST`、`aliasesUsed=[pmid2sw, bst2sw]`、`relaySet` 含 `46,48,76,109,110,131–135,154,155` 等 —— 含 ch5 与 K110 两侧资源（多源混登记，正是 B4/多源互斥要重做的事）。
- 契约现盘 `revision=37`（核对时由 376,308 B / `d9ecffb0…` 漂移到 377,128 B）⇒ **旧目录不可作输入**，新 DAG 一律走 `snapshot/` 冻结副本。

## 6. 边界

`D:/PROJECT6-DALI/devel` 零写入；目标树未落盘（`15c7d2b8…/469714 B`）；**未做任何机台/电性验证**；本文件不构成电气裁定。
