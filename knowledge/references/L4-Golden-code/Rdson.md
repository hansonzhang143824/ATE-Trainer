# Rdson 要点总结（RDSON · 台阶上电 + FPVI 大电流）

> 源文件：`L4-Golden-code/Rdson.cpp`（TM600_RDSON_TEST，139 行）｜索引登记：RDSON 官方案例；**与 `L4-Golden-code/tm600-normal-highcurrent.cpp` 同源同内容**（同一快照，登记角色不同）

## 1. 参数类型
- **RDSON（毫欧级导通电阻）**，一般测试项目 + 大电流；RON = VON/ION。
- 关联规则：R-VIR（V_meas/I_meas 双实测）、R-PON/R-POFF、FPVIe；易受接触电阻/自热/时序干扰（见 L1-chip/RDSON.md、L3-method/RDSON.md 的 15 步流程）。

## 2. 角色抽象（精髓）
- **被测 MOSFET 两端 = PMID ↔ SW（HS FET）**：K31_VBUSL_PMID（高边）+ K17_BUSH_SW（低边）→ FPVI 大电流闭环：FPVI→K31→PMID→FET→SW→K17→FPVI。
- **台阶配对结构 = BST − SW**：BTST_ACM 独立供 BST、SW_ACM 独立供 SW=0V → **不经过 FPVI_BUS（K38 不闭）**，压差恒 5V；K18_BST_SW_Cap = BST−SW P2P 电容稳定压差。
- 仅供电角色：K30_VBAT_Cap、K28_VDRV_Cap（Cap2 供电）；K32_PMID_Cap = FPVI 浮动 MI 的 Cap（电流走 FPVI_BUS，Cap 不干扰测量）。
- 下一项目：被测管两端、台阶对、供电轨全按角色映射（如 SW1↔VBUS、BST2−CFH2）。

## 3. 关键结构/特殊点
- **BUS 优先级仲裁**：FPVI 只有一个 → 大电流 iset[PMID2SW,1A] 必须用 FPVI（占 K31+K17）；BST−SW 仅需小电流 → 双独立源（BTST_ACM/SW_ACM）供电。
- 上电 = **4 级台阶 ramp**：BST 始终领先 PMID 5V 同步抬（0/0→5/0→10/5→15/10→20/15），每级 delay 200us；FET 导通前 SW=0 独立供电，导通后 SW 跟随 PMID。
- 测量三段式：FPVI FV=0 → FI=0 → **SetClamp(50,50) = 0.5V compliance（最大可测 500mΩ）** → FI=1A → delay 2ms → MeasureVI → **立即 FI=0 关断**（短脉冲防自热）。
- 毫欧级低阻的 Kelvin/Sense 分离思想见 L3-method/RDSON.md；本案例 RON 由 FPVI 本体 V/I 双实测（呼应 R-VIR，禁用设定电流值）。

## 4. 上电/下电时序
- SetOn：K31_VBUSL_PMID, K17_BUSH_SW, K18_BST_SW_Cap, K32_PMID_Cap, K30_VBAT_Cap, K28_VDRV_Cap。
- 上电：FPVI=0V 初始化 → VBAT=4.2/VDRV=5 → SW=0 → PMID/BST 0 → 台阶 4 级至 BST20/PMID15 → I2C 导通 HS FET（0x59 HSON、0x61 0x0B；导通瞬间 SW 0→15V，BST−SW=5V ✓）。
- 下电（**FET 不关**，保持导通让 SW 跟随 PMID 同步降，保证 BST−SW≥0）：BST15/PMID10 → BST10/PMID5 → BST5/PMID0（VBAT 归 0）→ VDRV 0、BST 0、SW 0 → 统一 RELAY_OFF（FPVI 最后断）。

## 5. 测量与判定
- `FPVI.MeasureVI(200, 5)` 后取 `MVRET/MIRET`：`hs_rdson = MVRET / MIRET * 1e3`（mohm）。
- 按 site SetTestResult；spec 上下限判定在外层。

## 6. 一句话适用场景
任意"台阶上电 + FPVI 大电流 + BST−SW 压差约束"的 RDSON 测试（HS/LS 管、内部功率管）；也是大电流浮动源案例的母版。
