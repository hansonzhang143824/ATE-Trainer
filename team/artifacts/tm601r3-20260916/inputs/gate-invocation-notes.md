## 2026-09-16 22:5x +0800 门禁调用方式核实（t11 起点）+ 一处新缺口登记

来源：Captain 只读核实 `scripts/run_gates.ps1`（`bst-sw` 门 = `args=@('scripts\verify_bst_sw_sequence.py')`，见 `run_gates.ps1:82`）与 `scripts/verify_bst_sw_sequence.py` 头部（560 行）。

### A1. `bst-sw` 门的行为（FACT，逐字引自脚本 docstring L5-L14）

| 现象 | 原文/依据 |
| --- | --- |
| **目标函数不硬编码，由 meta 拓扑指纹派生** | `verify_bst_sw_sequence.py:5-7`：`HS (BOOST, PMID-SW): powered_pins 含 BST-SW/BST_SW → BST 5V→10V 台阶`；`LS (BUCK, SW-PGND): powered_pins 含 IPMID2SW/PMID-SW → BST=5V (禁 10V)` |
| 电流量程判据 | `:8` `max |iset| ≥ 1A → FPVIe_10A, 否则 FPVIe_2A` |
| 寄存器判据 | `:9` `LS → I2C 0x01, HS → I2C 0x02` |
| **非 ZCD 项目可能「空 PASS」** | `:14` 「meta 无 BST-SW 目标 → 空 PASS (不误伤非 ZCD 项目)」 |
| 契约常量 | `:34-35` `BST_SRC = "SW12_U1REF_BST_ACM"`、`BST_CAP_RELAY = "K57_CAP_BST_SW"` |
| 入口参数 | `:13` 用法 `python verify_bst_sw_sequence.py [--src <test.cpp>] [--config <json>] [--list]`；判定「任一 FAIL → exit 1」 |
| 日志与范围 | `run_gates.ps1:22-25` 参数 `-Only` / `-LogDir` / `-BuildPath`；`:37` 未给 `-LogDir` 时落 `%TEMP%\dsh_gates_<ts>`；`:82` `bst-sw` 常规门不含 `--src` |

**可执行后果（INFERENCE，供 t11/t6 使用）**：常规 `run_gates.ps1` 对 `bst-sw` **不传 `--src`**，故它校的是**meta 派生目标 + 现网用例**，而不是候选 payload；且 meta 无 BST-SW 目标时会**空 PASS**。⇒ 若要证明候选 payload 满足闭集，必须另用 `--src <candidate>`，并按 t54 已登记的缺口（`main()` 在 `targets` 为空时提前 `return`，静默跳过契约闭集断言）**同时**核对「非空 targets」，否则会把空 PASS 当成绿。

### A1.1 新缺口（本轮实测，需 t6/t7/t11 处置）

- 脚本把 TM601 这类 LS 项归入 `BST=5V (禁 10V)` 分支的**入口条件**是 `powered_pins 含 IPMID2SW/PMID-SW`（`:7`）。
- 但**新版 DFT 明确给出 TM601 的 BST=5 V**（`OVERVIEW!L133` 第 4 行 `vset[bst,5,100e-6,0]`），而 TM601 的 `Power`(`O133`) 只有 `VBAT`、`Check`(`Q133`) 只有 `SW-PGND` + `I(PMID_SW)`。
- ⇒ **门禁分支是靠 meta 指纹间接推断的，而非 DFT 显式声明**；若 meta 指纹未能命中（别名/大小写/拓扑变化），TM601 的 BST 约束会**落进空 PASS 而不报警**（这正是「门禁盲区」在本轮的第二个实例）。
- **处置归口**：由 `t1`（把 `vset[bst,…]` 写进 DFT IR 并使 meta 派生可命中）、`t7`（在计划内写明 TM601 的 BST 目标与寄存器依据）、`t11`（用 `--src` + 非空 targets 双向确认，禁止以空 PASS 记为绿）分别落实。**本轮不修改任何门禁脚本**（`run_gates.ps1` / `verify_bst_sw_sequence.py` 均未改，字节不动）。

### A2. 边界

`devel` 零写入；目标树未落盘（469,714 B / `15c7d2b8…`）；未运行门禁（避免产出与最终树不对应的证据）；无机台/电性验证。
