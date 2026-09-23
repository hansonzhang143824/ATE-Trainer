# HS_ZCD 要点总结（Current Threshold · BOOST 上管 ZCD）

> 源文件：`L4-Golden-code/HS_ZCD.cpp`（61 行）｜索引登记：Current Threshold / ZCD，HS_ZCD（BOOST，被测两端 PMID−SW）

## 1. 参数类型
- **Current Threshold（ZCD 过零电流阈值）**，BOOST 拓扑**上管（HS）**侧；一般测试项目（阈值 AWG：电流 ramp → 观测脚翻转）。
- 单阈值、**无迟滞、无 Hys**（区别于 UVLO 族要测上下阈值 + HYS）。

## 2. 角色抽象（精髓）
PIN/继电器是"角色实例"而非名称。本案例角色清单：
- **被测 MOSFET 两端 = PMID ↔ SW**：被测对象是上管，两端分别连 PMID 与 SW；电流 >200mA → 用 **FPVI 把两端短接**成一条电流路径（K36_BUSL_PMID 高边 + K17_BUSH_SW 低边，注释 SW-FPVI-PMID connect）。
- **台阶配对结构 = BST − SW**：压差全程必须 BST≥SW 且 BST−SW≤5V；自举电容 Cap_SW_BST（K57）是配对结构一部分 → BOOST 测试闭 K57、**不闭** SW1/BST1 对的 K45。
- **翻转观测脚 = SDA_INT（INT）**：K43_INT_ACM 接 ACM、K58_INT_PU 上拉。
- **下一项目映射**：按角色映射到新 PIN，如 SW1↔VBUS、BST2−CFH2；从本项目权威源按角色解析，不照抄继电器号。

## 3. 关键结构/特殊点
- **浮动源仲裁**：电流 >200mA 必须用 FPVIe 浮动源；浮动源只有一个 → 优先级：被测大电流用 FPVI，**BST−SW 台阶改由 BTST_ACM 独立源供电**（满足台阶上电原则）。
- 测量本质 = **电流阈值**：rampi_capv 在 FPVI 上 ramp 电流、抓其他 PIN（SDA_INT）翻转，翻转点对应的电流值即 ZCD 值。
- 上管导通靠寄存器：0x61=0x0B（D2A_BUBO_TM_HSON=1）→ PMID 与 SW short。

## 4. 上电/下电时序
- SetOn 一组：K30_VBAT_Cap, K32_PMID_Cap, K36_BUSL_PMID, K17_BUSH_SW, K28_VDRV_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap。
- 上电：FPVI=FV 0V（先令 PMID=SW=0 等电位启动）→ VBAT=V_TYP、BST=5V、VDRV=5V → PMID_FOVI=5V → BST=10V（成对抬升，全程 BST−SW=5V）。
- 下电：FPVI 回 FV0 锁等电位 → BST=5V → PMID=0V → BST=0V → VBAT/VDRV/SDA_INT 归 0 → 各源统一 RELAY_OFF。

## 5. 测量与判定
- `rampi_capv(FPVI, FPVIe_1V, FPVIe_1A, SDA_INT_ACM, ACM200_10V, ACM200_100UA, 0.25, -0.5, 200, 20, 2.5, TRIG_RISING, hs_zcd)`：电流 ramp（升方向 → TRIG_RISING）抓翻转。
- 结果按 site 存 `HS_ZCD->SetTestResult`；规格上下限判定在参数/spec 层完成（本函数只产出测量值）。

## 6. 一句话适用场景
BOOST/升降压芯片 HS 侧 ZCD（及同族电流阈值）测试：把"被测 MOSFET 两端 + BST−SW 台阶对 + INT 观测脚"按角色映射即可直接套用。
