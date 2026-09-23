# TM600/TM601 的 BST 供给资源事实与「5 V 工况」实现形状

> 时间：2026-09-17 00:0x +0800 ｜ 只读代码事实 + 推断。归口：`t2`（物理/资源）、`t6`（契约）、`t7`（操作点）、`t8`（独立审查）。

## 0. 自我更正（第 5 次）

我在本轮中间步骤曾据一次**被截断的输出**推测「部署态 TM600 体内不含 `PMID_HG2_FXVI.Set(...)`，该源只被声明未使用」。**已撤回**：全文件普查 `PMID_HG2_FXVI` = 59 处、其中 `.Set(`/测量 51 处，**TM600 体内确有多处**（`test.cpp:9102 / 9107 / 9112` 上电，`9176 / 9180 / 9184` 下电，`9193` 释放）。截断来自我自己的 `Select-Object -First` 限制，不是事实。

## 1. FACT：部署态 TM600 的继电器栅格（`test.cpp:9081`）

```
cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap,
            K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1)
```
| 目的 | 闭集 | 备注 |
| --- | --- | --- |
| FPVI0 → PMID（高） | `K83` | |
| FPVI0 → SW（低） | `K60, K61` | 与 TM601 共用同一对低端腿 |
| **ACM200 ch5 → BST** | **缺 `K48, K76`** | 唯一缺口；未闭时 K48 释放 ⇒ 改道 K49 ⇒ SW1/SW2 |
| 稳压电容 | `K13, K85, K57, K126` | `K57_CAP_BST_SW` 即 BST−SW 对电容 |
| **其余 BST 来路** | 不闭 `K46` | `K46` 属 MOS P2P（默认断开）⇒ 来路②④⑤ 物理断开 |

## 2. FACT：`SW12_U1REF_BST_ACM`（ACM200 ch5）被谁用、怎么用

- 全文件 45 处提及；**驱动性 `.Set` 出现在**：`TM607`(`:7008`)、`TM608`(`:7096/:7100`)、`TM609`(`:7179/:7184`)、`TM640`(`:7521/:7526`)、`TM600`(`:9097-9115`)、`TM601`(`:9269`)，以及若干函数仅做 `Set(FV,0,…,RELAY_ON)` 的**收尾归零**（`:848/:945/:992/:1051`）。
- **TM641/TM643 的既有做法（先例）**：`test.cpp:7598 / 7621 / 7714` 注释逐字写
  > `⚠ K48/K76 同时把 ACM200_FH5(SW12_U1REF_BST_ACM) 输出端接 BST → 该源全程 RELAY_OFF 不驱动`
  即：**当某函数让 BST 由别的来路（FPVIe/QVM 低端，经 `K109/K110`）驱动时，必须把 ch5 源显式 RELAY_OFF**，因为 `K48/K76` 一旦闭合就把 ch5 输出接上 BST。这既是「多源互斥」的既有实现，也是「显式 RELAY_OFF 配对」的先例。

## 3. FACT：`PB0_BST_ACM`（ACM200 **ch18**）的用途是 **PB0/PWM1 引脚测量**，不是 BST 供电

`:5003 / 5022 / 5026 / 5041 / 5045`（TM214_PWM1_Vth）、`:5185-5199`（TM216_PWM1_Current，含 `MeasureVI(50,5)` + `GetMeasResult(MIRET)`），且 `:4994 / 5160` 注释 `PWM1 -> PB0_BST_ACM: default NC`。
⇒ ch18 到 BST 的 `K110` 腿（`SCH:678-680` 族）**在本板是实现路由，但该仪器的实际用途是 PWM1 采集**；把它当 BST 供电源需另证（`t2`）。

## 4. INFERENCE：新版 TM600「5 V 工况」的实现形状已由 TM640 给出（强）

`TM640`（部署态）与新 TM600 的 DFT 轨值**逐字相同**（`vbat=3.5 / pmid=5 / bst_sw=5 / vdrv=5`），其实现是：

| 步骤 | 调用（`test.cpp`） |
| --- | --- |
| 固定 PMID=SW=0 | `:7518` `FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10A, RELAY_ON)` |
| VBAT | `:7520` `VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, 100MA, ON)` |
| **BST=5（SW=0）** | `:7521` `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ON)` |
| PMID=5（SW 跟随） | `:7524` `PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, 100MA, ON)` |
| **BST=10（SW=5 ⇒ BST−SW=5）** | `:7526` `SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ON)` |
| 闭集 | `:7513` 含 `K_FPVIH_TO_PMID_A, K60, K61, K13, K57, **K48, K76**, K65, …` |

⇒ **TM600 在 5 V 工况下的正确形状 = 「FET 导通前先 BST=5，PMID 抬到 5 后 BST=10」两步**（或等价的两段），且**必须闭 `K48/K76`**。这与新版 DFT 把 `PMID` 与 `BST_SW` 都写成 5 V 一致（`BST_SW`=差分目标，实现在 BST 单端值上）。
⇒ **反证 A2**：若沿用部署态 TM600 的 15 V 台阶（`PMID 5→10→15`、`BST 10→15→20`），在 PMID 只到 5 V 的操作点上会停在 `BST=10`，或若照抄到 20 V 则 **BST−SW=15 V**，与 R-BST-SW（`0 ≤ BST−SW ≤ 5 V`，见门禁 `:545` 输出 `[contract] BST>=SW and 0<=BST-SW<=5V`）直接冲突。

## 5. 对 TM601 的落点（FACT + INFERENCE）

- 部署态 TM601 `:9269` 已经 `Set(FV, 5, ACM200_10V, ACM200_100MA, RELAY_ON)` ⇒ **BST=5 V 的既有写法存在**。
  该函数**唯一的 `cbite.SetOn` 在 `:9255`**（实测逐字）：
  ```
  cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW,
              K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1)
  ```
  ⇒ **该 SetOn 不含 `K48/K76`**（也不含 `K46/K49/K109/K110`）。结合 `:9246` 既有注释（`SW1 needs K46 / SW2 needs K46+K49, DIFFERENT NODES from SW`），**部署态 ch5 被设到 5 V 但没有闭合到 BST 的通路** ⇒ **BST=5 V 实际到不了 BST 节点**。这正是用户指出「TM601 缺 BST 通路」的代码级证据。
  ⚠ 中间更正：我一度把这条写成「未闭 K48/K76 ⇒ 源被设置却无通路」，随后因门禁**只检查契约登记的腿**而自我怀疑并撤回过一次；现以 `:9255` 逐字实测**恢复该结论**（方法：按 `DUT_API int <Name>(short funcindex` 定界取函数体，仅打印含 `SetOn`/`K48|K76|K49|K46|K109|K110` 的行）。
- ⇒ **TM601 的 BST=5 V 若要真正送达 BST 节点**，`t6` 必须给它登记包含 `K48/K76` 的闭集（与 TM600 的修法同族），并**同时**处置 `K60/K61` 与 SW 回路的共享（TM601 的激励回路本就用 `K60/K61`）。
- ⇒ **UNKNOWN（交 `t2`）**：TM601 是否**必须**有 BST 供给（LS 导通不需要 BST，但 DFT 明确写了 `vset[bst,5,…]`）；以及 BST 供给与 SW—PGND 1 A 回路共用 `K60/K61` 时是否有互斥/耦合后果。

## 6. 边界

只读 `test.cpp`（469,714 B / `15c7d2b8…`）；未修改任何文件；未落盘 payload；`devel` 零写入；**无机台/电性验证**；本文件不含电气签核。
