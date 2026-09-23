# LS_ZCD 要点总结（Current Threshold · BUCK 下管 ZCD）

> 源文件：`L4-Golden-code/LS_ZCD.cpp`（53 行）｜索引登记：Current Threshold / ZCD，LS_ZCD（BUCK，被测两端 SW−PGND）

## 1. 参数类型
- **Current Threshold（ZCD 过零电流阈值）**，BUCK 拓扑**下管（LS）**侧；一般测试项目（阈值 AWG）。
- 单阈值、**无迟滞、无 Hys**；与 HS_ZCD 同族，互为"同一角色在不同拓扑的落点"对照。

## 2. 角色抽象（精髓）
- **被测 MOSFET 两端 = SW ↔ PGND**（下管）：电流 >200mA → FPVI 短接两端：K33_BUSL_PGND（低边）+ K17_BUSH_SW（高边），注释 SW-FPVI-PGND connect。
- **台阶配对结构 = BST − SW**：约束与 HS 相同（BST≥SW 且 BST−SW≤5V）；本 BUCK 案例台阶量程小：VBAT=VDRV=PMID=BST=5V 一次到位，无 10V 抬升段。
- **翻转观测脚 = SDA_INT（INT）**：K43_INT_ACM + K58_INT_PU 上拉，与 HS 相同。
- **映射原则同 HS**：按角色映射（如 SW1↔PGND、BST2−CFH2），不抄继电器号。

## 3. 关键结构/特殊点
- 下管导通寄存器：0x61=0x0D（D2A_BUBO_TM_LSON=1）→ SW=PGND（HS 用 0x0B 导通上管）。
- 上电更简单：VBAT=V_TYP、PMID_FOVI=5V（FOVIe_20V）、BST=5V、VDRV=5V 平上，无 PMID 0→5 台阶段。
- 代码末尾有一段"先重新上电（35-40 行）再统一下电"的写法，疑似模板残留/保护性复位；要点是以最后统一 RELAY_OFF 收尾为准。
- 与 HS_ZCD 的差异只在：被测两端继电器（K33 vs K36）、导通寄存器（0x0D vs 0x0B）、台阶幅度；其余角色完全同构 → 读一份即可迁移。

## 4. 上电/下电时序
- SetOn：K30_VBAT_Cap, K32_PMID_Cap, K33_BUSL_PGND, K17_BUSH_SW, K28_VDRV_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap。
- 上电：VBAT/PMID/BST/VDRV 依次上到 5V 量级 → SDA_INT 设 FI=0 → entertestmode + I2C 导通下管 → 电流 ramp。
- 下电：FPVI FI→FV 0 →（35-40 行重复上电段）→ VBAT/PMID/BST/VDRV/SDA 归 0 → 统一 RELAY_OFF。

## 5. 测量与判定
- `rampi_capv(FPVI, FPVIe_1V, FPVIe_1A, SDA_INT_ACM, ACM200_10V, ACM200_100UA, 0.25, -0.5, 200, 20, 2.5, TRIG_RISING, ls_zcd)`：与 HS 完全同参，抓 SDA_INT 翻转。
- 翻转点电流 = ZCD 阈值；`LS_ZCD->SetTestResult` 按 site 存；判定在 spec 层。

## 6. 一句话适用场景
BUCK 下管 SW−PGND 的 ZCD/电流阈值测试；与 HS_ZCD 合并为"同角色两拓扑落点"的黄金对照（BOOST 看 PMID−SW，BUCK 看 SW−PGND）。
