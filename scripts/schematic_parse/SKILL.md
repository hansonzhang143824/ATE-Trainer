# ATE Hardware Parser Skill

把 Altium 原理图 CSV（`Dali-SCH.csv`）转成 ATE 通道映射（Source → Relay 网络 → DUT PIN），
产出通路定义（StdAfx.h 2.x 段）与 CBIT 单点/校验定义。CSV 解析是**唯一生产管线**。

## 权威输入

- `Project/DALI/Dali-SCH.csv`（项目 config `inputs.csv_schematic`）：Altium unified circuit connectivity CSV v3，**唯一权威源**。
- 电容/电阻值已并入 `Dali-SCH.csv` 的 `ComponentValue` 列，adapter 嵌入合成 EDIF `(Property Value ...)` 供 `sch_parse.py` 稳压分类读取（**无需独立 .NET**）。

## 入口

```
python schematic_parse/scripts/run_hardware_parse.py                       # 校验 + 生成通路/CBIT 定义（--no-write，不写 StdAfx.h）
python schematic_parse/scripts/run_hardware_parse.py --publish-definitions # 校验 + 真正发布 StdAfx.h 2.x 段（先备份）
```

## 四脚本流水线

| 顺序 | 脚本 | 输入 → 输出 |
|------|------|-------------|
| 1 | `scripts/csv_schematic_adapter_v2.py` | CSV → 合成 EDIF `CSV_CONNECTIVITY.NET` → `sch_parse.py` 六门控 → `Output_Global_Material/schematic/SCH-Connect-Map.txt` + `Component-Statistic.txt` + `validation_manifest.json.txt` |
| 2 | `scripts/csv_pathproof_v2.py` | CSV + CBIT → 原生 BFS PathProof → `path_proofs.json.txt` + `PATHPROOF-VALIDATION.txt` |
| 3 | `gen_path_defines.py --config project_config.json --map <SCH-Connect-Map.txt> [--no-write]` | 通路定义 2.x 段 |
| 4 | `gen_cbit_defines.py --config project_config.json --stat <Component-Statistic.txt> --map <SCH-Connect-Map.txt>` | CBIT 单点 + V1–V8 校验 |
| 5 | `gen_relay_role_defines.py --map <SCH-Connect-Map.txt> [--no-write]` | 列11 角色继电器定义 → StdAfx.h RELAY_ROLE 段（稳压/P2P/短路/上拉/下拉） |

产物统一落 `Project/DALI/`；脚本 1/2 复用本目录 `scripts/` 下的
`sch_parse.py`（六门控引擎），脚本 3/4/5 复用 workspace 根目录的
`gen_path_defines.py` / `gen_cbit_defines.py` / `gen_relay_role_defines.py`（不重造引擎）。

## 状态机（脚本 1 的退出码与 manifest.status）

| status | 含义 | 退出码 |
|--------|------|--------|
| `PASS` | 六门控 PASS（列11 通路分类 + Rule A/B 已应用） | 0 |
| `PARSER_FAIL` | 六门控失败 | parser 退出码 |

## 注意

- CSV 是 **DLP 透明加密**文件，只能用 Python（白名单进程）读写；`load_csv` 会拒收
  `%TSD-Header-###%` / `TSZ#` 密文容器。
- `--publish-definitions` 前脚本自动备份 `StdAfx.h` 到 `Backup/`（`relay_definitions` 指向它）。
- **多源同 PIN 通路命名铁律（2026-08-26 用户拍板）**：多个源/多个 FPVIe 通道连到同一 PIN → 命名尾缀加 `_A/_B/_C` 区分（如 `K_FPVIH_TO_ACDRV1_A/B`）。**这是正常命名，不算 warning/歧义，全部发布**（`gen_path_defines.py` 已按 (source, side, pin) 分组自动加尾缀）。只有 ⚠非有效（F/S 未同时闭合）通路不发布，脚本 parse 阶段已自动跳过。`--verify`/`--check-relay` 与发布同预期。
- **列11 角色继电器命名铁律（2026-08-26 用户拍板）**：`gen_relay_role_defines.py` 从列11 自动生成角色名 #define，值=需闭合继电器 CBIT（逗号分隔）：
  - 稳压：`K_<Pin>_Cap`（单端去耦）/ `K_<Pin1>_<Pin2>_Cap`（两脚电容，组件名 `Cap_<P1>_<P2>` 如自举 SW↔BST）；「需闭合:无」无继电器 → 跳过。
  - P2P-到地：`K_<Pin>_P2P`；上拉：`K_<Pin>_PU`；下拉：`K_<Pin>_PD`。
  - **短路判据**：闭合**一个**继电器（单 CBIT ≤1）即短接**两个 DUT 节点** → 短路继电器 → `K_<PinA>_<PinB>_ST`（如 `K_KLV1_KLV2_ST`）。源/地 Kelvin F/S（K86/K130/K92）不算。注：K25（VCC↔ACDRV1/2/3 公共轨，需经 K22/23/24 才够到 ACDRV 引脚，图论推不出）曾被并入短路，**2026-08-26 用户放弃并入** → 不定义，短路仅列11 P2P-互短 直接型。
- **net 短接判定**：CSV 的 `ELECTRICAL_SHORT_GROUP` / `NET_TIE_GROUP` 记录 → adapter 提取为
  短接组 → 合成 EDIF `(comment "CSV_NET_SHORT:...")` → `sch_parse.py` 列11 输出「net短接」分类
  （直接导线/NetTie 同电气节点）。只记录短接事实、**不合并 net**（下游通路分析需知道「经过此节点
  即已短接、F/S 分叉也不再是 Kelvin 四线」）。完整判据见 `NET_SHORT_RULES.md`。
