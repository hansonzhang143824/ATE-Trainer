# Path Contract（通路契约）

合法通路：`Source → Relay 网络 → DUT PIN`。由 `scripts/csv_pathproof_v2.py` 的 BFS 强制执行，
四条契约硬编码进 `path_proofs.json.txt` 的 `contracts` 段。

## 契约 1：DUT PIN 是终点（dut_pin_is_terminal）

`trace()` 一旦到达 DUT 端口（`ports` 中 direction==OUTPUT 的网）即产出 proof 并 `continue`，
**绝不越过 DUT PIN 继续扩展**。防止把 DUT 内部当成通路继续穿。

## 契约 2：Kelvin F/S 不交叉（kelvin_force_sense_no_cross）

Force 源只能到 Force PIN、Sense 源只能到 Sense PIN。`validate_and_pair` 用 `pin_role`
与 `source_meta.role` 比对：`role_match = not dut_role or not source_role or dut_role == source_role`，
不匹配 → `KELVIN_ROLE_CROSS` 拒绝。

## 契约 3：共享继电器状态一致（shared_relay_state_must_match）

同一 DUT 的 Force/Sense 两条 proof，若共享继电器号码但状态（ON/NC）不同 → 冲突 → pair FAIL。
见 `validate_and_pair` 的 `f_state`/`s_state` 交集比对。

## 契约 4：CBIT 可追溯（cbit_traceability_required）

proof 里每个 `required_on`（需闭合的继电器号）都必须在 CBIT 表（`CBIT表-DALI.xlsx`）有记录；
缺失 → `MISSING_CBIT` 拒绝 + hard_issue。`load_cbit` 复用 `gen_cbit_defines.read_excel_cbit`。

## BFS 剪枝规则（trace）

- `max_depth = 6`：同一条通路最多经过 6 个不同继电器（`used_numbers` 去重）。
- **bus 域剪枝**：`bus_domain(net)` 判定 HIGH（`FH_BUS/SH_BUS/FH_PC/SH_PC`）或 LOW
  （`FL_BUS/SL_BUS/FL_PC/SL_PC`）。非 scarce 源跳过 bus 域网；跨域（HIGH↔LOW）拒绝。
- **scarce 源豁免**：`FPVIe`/`QTMU`/`QVM`/`CH0` 源跳过 bus 域剪枝（稀缺源必须能到 bus）。
- **活跃 bus 域一致**：ON 态进入 bus 域后，后续必须同域。
- **Rule A 固定电压节点剪枝**：`next_net ∈ fixed_voltage_nets 且 next_net ∉ dut_by_net` → `continue`。
  固定电压节点 = 地（`AGND/DGND/JGND/AGND_*`，0V）∪ 固定电源轨（`J+5V/J+12V`，5V/12V）。
  作**中间节点**非法（源表与之对拉、无法独立控制通路电压）；作**终点**（DUT 地脚）由 terminal-stop 覆盖。
- **软规则（不剪）**：通路穿越其他**源表**端口只加 `⚠经过源表` 警告（源表可编程，非固定电压，
  属「另一条源表通路」而非「固定节点对拉」）。
- `source_meta` 解析源类型（ACM200/FXVIe_PLUS/FXVIe/FPVIe/QTMU/QVM/DCM）、F/S 角色、
  HIGH/LOW 域、pair_key（`family:channel:domain`）。
