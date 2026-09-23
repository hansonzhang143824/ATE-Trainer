# tm600-normal-highcurrent 要点总结（Normal + 大电流 + 浮动源 黄金案例）

> 源文件：`L4-Golden-code/tm600-normal-highcurrent.cpp`（TM600_RDSON_TEST，139 行）｜索引登记：**TM600 黄金案例（唯一正确版，已确认）**；**与 `L4-Golden-code/Rdson.cpp` 同源同内容**（同一快照，Rdson.cpp 为同函数按参数命名快照）

## 1. 参数类型
- **RDSON 大电流测试**（Normal 流程 + FPVI 浮动源 + BST 台阶上电），一般测试项目。
- 工程定位：TM600 **唯一正确版**（过程稿 TM600_*.cpp 与 TM601_LS_RDSON.cpp 已移 `_archive/` 隔离）；本文件是"最复杂案例"的官方定型，Rdson.md 为其参数命名快照的要点 —— 两 md 可互参。

## 2. 角色抽象（精髓）
- **被测 MOSFET 两端 = PMID ↔ SW（HS FET）**：K31_VBUSL_PMID + K17_BUSH_SW 占 FPVI_BUS 形成大电流闭环（FPVI→PMID→FET→SW→FPVI）。
- **台阶配对结构 = BST − SW**：BTST_ACM/SW_ACM 双独立源供电（K38 不闭），K18_BST_SW_Cap 稳压差，差值恒 5V。
- 供电角色：K30_VBAT_Cap/K28_VDRV_Cap（仅供电）、K32_PMID_Cap（FPVI 浮动 MI 的 Cap，不干扰电流路径）。
- **角色复用要点**：这套三元组（被测管两端 / BST−SW 台阶对 / 供电轨）在 RDSON、ZCD（HS_ZCD/LS_ZCD）、Trim（TM623 HS Gain）间通用 —— 本案例是它们共用的"工程母版"。

## 3. 关键结构/特殊点
- **资源仲裁整链范式**：FPVI 唯一 → 大电流 iset[PMID2SW,1A] 优先级最高占 FPVI_BUS；BST−SW 只需小电流 → 降级给双独立源。"何时必须浮动源、何时普通源即可"以此为准判定。
- 上电 = 4 级台阶 ramp（BST 领先 PMID 5V：0/0→5/0→10/5→15/10→20/15，每级 delay 200us）；I2C 导通 HS FET 后 SW 跟随 PMID。
- 下电 **FET 不关**：保持导通、SW 跟随 PMID 台阶同步降（BST15/PMID10→…→BST5/PMID0→全 0），保证 BST−SW≥0 不反偏。
- 测量：FV0 → FI0 → **SetClamp(50,50)（0.5V compliance → 最大可测 500mΩ）** → FI=1A → delay 2ms → MeasureVI → **立即 FI=0 关断**（短脉冲防自热）。

## 4. 上电/下电时序
- SetOn：K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap。
- 上电/下电台阶与 Rdson.cpp 逐行一致（详见 Rdson.md 第 4 节），不再重复。

## 5. 测量与判定
- `FPVI.MeasureVI(200, 5)` → `hs_rdson = MVRET / MIRET * 1e3`（mohm，双实测呼应 R-VIR）。
- 按 site SetTestResult（HS_RDSON）；spec 判定在外层。

## 6. 一句话适用场景
"Normal + 大电流 + 浮动源"组合的 RDSON/功率管测试**统一母版**：写 TM600 类工程代码前先对齐本案例的资源仲裁、台阶上电/下电纪律与短脉冲防自热。
