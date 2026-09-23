# Output Rules（输出规则）

所有产物落 `Project/DALI/`，用 `.txt` 后缀（保持明文，规避 DLP 对 `.json` 的透明加密）。

## SCH-Channel-Map（SCH-Connect-Map.txt）

每条通路记录须含：Source、PIN、Force/Sense Path、Relay（继电器号 + NC/ON 态）、CBIT（必需闭合）、
Validation、列11 通路分类（P2P-到地 / P2P-互短 / 上拉 / 下拉 / 稳压）。
由六门控引擎产出（脚本 1 喂合成 EDIF）。

## Component-Statistic（Component-Statistic.txt）

器件统计（源端口 / DUT 端口 / 继电器 / net 数等），供 CBIT 校验对拍。

## PathProof（path_proofs.json.txt + PATHPROOF-VALIDATION.txt）

原生 BFS 校验结果：`contracts`（4 契约）、`counts`（sources / accepted / rejected / kelvin_pairs / failures）、
`issues`、`status`（无 issue → PASS）。

## Validation Manifest（validation_manifest.json.txt）

脚本 1 的总清单：input sha256、graph 统计、artifacts（各产物路径 + sha256）、
`parser_gate_status`、`status`。

## 通路定义（StdAfx.h 2.x 段，--publish-definitions 时写）

`gen_path_defines.py` 产出的 `#define Kxx_... <number>` 通路定义；`--no-write` 仅输出不落盘，
`--publish-definitions` 先备份 `StdAfx.h` 再写。

## 命名与优先级

- 合成 EDIF 网名：每个物理 CSV net 只发一次；DUT(OUTPUT) 名优先于源(I/O) 名；已有原始名优先于两者。
- `S3_FOVIe_*` 归一为 `S3_FXVIe_PLUS_*`。


PTC published location: `project/DALI/Output_Global_Material/schematic/`. The complete TXT files are authoritative; `schematic-receipt.json` is hash metadata only.
