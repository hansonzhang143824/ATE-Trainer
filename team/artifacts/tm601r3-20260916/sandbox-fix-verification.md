# 沙箱实证：TM600 的 K48/K76 闭集修法使门禁契约断言由红转绿（R10）

> 时间：2026-09-17 01:2x +0800 ｜ **只改动沙箱副本**，目标树与 `devel` 未被触碰（见 §3 前后哈希）。
> 可复现脚本：`sandbox_fix_test.py`（本目录）；结果：`sandbox/fix-test-result.json` = 1,986 B / `5e633bf5…2b3cb33`。

## 1. 方法

1. 把部署态 `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` **逐字节复制**到 `sandbox/test.cpp.copy`（469,714 B / `15c7d2b8…36c01a`）。
2. 在该副本内做**唯一一处**编辑（锚点出现次数实测 = 1，脚本内 `assert n == 1`）：
   ```
   旧: cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap,
                   K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);
   新: cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap,
                   K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP,
                   K48_ACM5_AMP_REF, K76_ACM_BST, -1);
   ```
   产出 `sandbox/test.cpp.k48k76` = **469,745 B / `fab6262b32013154ad84dbf381b62936706c7c6804dd11fd5bedf8c9b5d703dd`**（比原件 +31 B）。
3. 对两份副本各自运行门禁的契约断言通道：
   `python scripts\verify_bst_sw_sequence.py --src <副本> --contract team\artifacts\tm601r3-20260916\snapshot\setup_contract.json`

## 2. 结果（逐字）

| 用例 | `[t30]` TM600 | `[t30]` TM601 | `[scan]` | exit |
| --- | --- | --- | --- | --- |
| **A 未编辑副本** | 必需 `[48,60,61,76,83]`，**缺失 `[48,76]`** | 必需 `[60,61,154,155]`，缺失 `[]` | `targets=4 FAIL=2` → `*** FAIL (BST-SW GOLDEN SEQUENCE) ***` | **1** |
| **B 仅加 K48+K76** | 必需 `[48,60,61,76,83]`，**缺失 `[]`** | 必需 `[60,61,154,155]`，缺失 `[]` | `targets=4 FAIL=0` → `BST-SW SEQUENCE PASSED` | **0** |

## 3. 边界与前后哈希（证明未动目标）

| 对象 | 测试前 | 测试后 |
| --- | --- | --- |
| `ForCodexDebug/source/test.cpp` | `15c7d2b8…36c01a` | **`15c7d2b8…36c01a`（未变）** |
| `devel/source/test.cpp` | `5c9cb3f9…ac3317` | **`5c9cb3f9…ac3317`（未变）** |

## 4. 结论（含两条必须写进报告的限制）

1. **修法可证**：在 TM600 那一次 `SetOn` 内补 `K48_ACM5_AMP_REF + K76_ACM_BST`，即可让该门的契约闭集断言由红转绿（**exit 1 → 0**）。这是**沙箱内实证**，不是预测。
2. **该门只校验闭集，不校验阶梯**：用例 A/B 的 `targets=4 / FAIL` 只随**继电器集合**变化；把 BST 源设成 5 V、10 V 还是 20 V，本门**都不会报红**。⇒ **门禁绿 ≠ 操作点正确**（V 值/阶梯正确性必须由 `t7` 计划 + `t8` 独立审查 + 台架签核保证）。
3. **仍未证实**：`K48/K76` 的**实际物理贯通**（继电器动作/端子连续性）——门禁只做文本集合比对；以及 BST 供给的**电缆/端子实际拓扑**。
4. **适用范围**：本用例只覆盖 TM600 的闭集；TM601 需按其自身契约登记（其闭集当前无 BST 腿，故本门对 TM601 的 BST 供给**仍无约束**，须经 `t6` 修订后才有效）。
5. **不可外推**：本结果**不**证明 5 V 或 10 V 操作点正确，也不证明 BST−SW 在硬件上达标；它只证明「补这两条腿可以满足现行契约断言」。

## 5. 边界

未改目标树 / `devel` / 门禁脚本 / 契约 / 计划；沙箱副本仅存在于本 run 目录；**无机台/电性验证**。
