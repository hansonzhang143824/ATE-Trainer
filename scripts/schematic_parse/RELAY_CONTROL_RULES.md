# Relay Control Rules（继电器控制规则）

继电器通过 `cbite.SetOn(N)` 切换；本文件固化 V2 解析里继电器拓扑的机械/电气状态规则。

## G6K 双刀继电器转换表（csv_pathproof_v2.transitions）

G6K（`K\d+_` 且非 SW_SPST）有两组常闭/常开触点：

| 状态 | 触点转换 |
|------|----------|
| NC（常闭，未上电） | `2↔3`、`7↔6` |
| ON（上电闭合） | `3↔4`、`6↔5` |

`transitions(inst, pin)` 对当前引脚返回可达引脚 + 状态（NC/ON）。

## MOS / SPST（非 G6K 继电器）

单刀：`1↔2`，仅 ON 态（`pin==1→(2,ON)`，`pin==2→(1,ON)`）。

## infer_cell 分类（csv_schematic_adapter_v2）

- `K\d+_` 设计器：引脚集合超出 `{1,2}` **或** 引脚名集合超出 `{COMMON, NO}` → `G6K`；否则 `SW_SPST`。
- 非继电器：`CAP/C`→Cap、`R`→Res2、`D`→D_Schottky、`TP`→TEST_POINT_SMALL、其他→`CSV_<前缀>`。

## bus 域（csv_pathproof_v2.bus_domain）

- HIGH：net 含 `FH_BUS` / `SH_BUS` / `FH_PC` / `SH_PC`
- LOW：net 含 `FL_BUS` / `SL_BUS` / `FL_PC` / `SL_PC`
- 其他：`""`（无域）

非 scarce 源不穿 bus 域网；跨 HIGH/LOW 域拒绝；ON 态进入某域后须保持同域。
scarce 源（`FPVIe`/`QTMU`/`QVM`/`CH0`）豁免 bus 域剪枝。

## 与 CBIT 一致性

每条通路的 `required_on`（需闭合继电器号）必须能在 CBIT 表找到；缺失 → `MISSING_CBIT` 拒绝。
实际生成测试代码时，闭合顺序与 CBIT 定义的继电器号一一对应（见 `gen_cbit_defines.py` V8 继电器状态校验）。
