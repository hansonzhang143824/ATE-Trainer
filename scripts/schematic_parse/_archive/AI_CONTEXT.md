# ATE Background（AI 上下文）

ATE 通路有效性 ≠ 普通 PCB 连通性。核心概念：**Source（源表）、Kelvin Force/Sense（四线）、Relay（继电器切换）、CBIT（通道位映射）**。

## 硬件连接确认

根据 DFT + 原理图（CSV）确认硬件连接：哪个源表、闭合哪些继电器、用什么量程、到哪个 DUT PIN。
连接通过 `cbite.SetOn(N)` 切换实现。

## 数据流

```
Dali-SCH.csv（唯一权威源）
  → csv_schematic_adapter_v2.py（CSV → 合成 EDIF → 六门控）→ SCH-Connect-Map.txt + COMPONENT-STATISTIC.txt
  → csv_pathproof_v2.py（原生 BFS PathProof，4 契约）→ path_proofs.json.txt
  → gen_path_defines.py（通路定义 2.x 段）+ gen_cbit_defines.py（CBIT 单点 + V1–V8）
```

## 边界

- **CSV 为唯一权威源**；`DALI_Net.NET` 提供器件值（稳压电容分类）。
- **资源/继电器定义由外部团队提供**（`Pin_Channel_define.h` / `StdAfx.h`），本流程只读取 + 闭环验证，不生产。
- 所有权：`resource_and_relay_definition = external_team`；`definition_validation = offline_coding_pipeline`。
- DLP 透明加密：CSV / .NET / .cpp / .h 文件只能用 Python 字节模式读写；哈希用解密后内容（`.upper()`）。
