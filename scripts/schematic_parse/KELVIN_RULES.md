# Kelvin Rules（开尔文四线规则）

Force 与 Sense 分离：`Source_F → PIN_F`、`Source_S → PIN_S`，**禁止交叉**。

## 角色识别

- `pin_role(port)` 解析 `_FORCE_/SENSE_` 或 `_F_/_S_` 后缀 → F/S。
- `source_meta(port)` 从 `_(FH|SH|FL|SL)\d+`（FH/SH=Force、FL/SL=Sense）或 `CH\d+[+-]`（+=F、-=S）判定源角色与 HIGH/LOW 域。

## 交叉判定（validate_and_pair）

`role_match = not dut_role or not source_role or dut_role == source_role`。
F 源到 S PIN 或 S 源到 F PIN → `role_match=False` → `KELVIN_ROLE_CROSS` 拒绝。

## Kelvin 配对（validate_and_pair 分组）

- 仅对 kelvin 源类型配对：`FPVIe`/`ACM200`/`FXVIe_PLUS`/`FXVIe`/`QVM`。
- 分组键 `(source_meta.pair_key, dut_base)`，其中 pair_key = `family:channel:domain`。
- 同一组须同时有 F 与 S proof，取各自最短路径（`len(path), len(required_on)`）为代表。
- **共享继电器状态冲突**：F/S 两条 proof 交集继电器号状态不一致 → pair `FAIL` + hard_issue。

## 输出

`kelvin_pairs`（F/S 配对结果）+ `kelvin_pair_failures`（FAIL 数）写入 `path_proofs.json.txt`；
`kelvin_pair_failures=0` 才 PASS。
