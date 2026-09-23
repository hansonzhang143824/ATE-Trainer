# Action Items（待办裁定/待改机制）

## Action-01 · [30] gate 放行机制（记录于 2026-09-22，提出人：张帅）

- **现状（已落地）**：`scripts/validate_dft_outputs.py` 的 validate() 已加组合判定——`parseStatus=pendingUser` 或 `openItems` 非空 ⇒ 不得判 ready。放行规则 = openItems 清空 + parseStatus 回到 ok/selfResolved。
- **后期将改**：放行机制将改为 intent-resolutions 覆盖放行（`project/DALI/meta/intent-resolutions.json` 中对应项有 resolution 即放行），替代现在的"清单清空"规则。
- **改动时同步**：修改 `scripts/validate_dft_outputs.py` 的两条 Action-01 判定 + 更新本条状态为已完成。
- **来源**：Trainer 增补卡 [30]，张帅 2026-09-22 裁定"当前先按简化版做，后期我会改"。
