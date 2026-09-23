# Validation Rules（校验规则）

由 `scripts/csv_schematic_adapter_v2.py`（CSV 侧）与 `sch_parse.py`（六门控侧）共同执行。

## 1. 25 列契约（REQUIRED_COLUMNS）

CSV 表头必须含以下 25 列（缺一 → 报错，多余列 → 警告保留不用）：

```
SheetPath, RecordType, RecordKey, NetName, MemberType, MemberName, Designator,
ComponentUniqueID, MemberUniqueID, ComponentKind, LibraryReference, PartID,
PinNumber, PinName, Electrical, Relation, EndpointStatus, ObservedNetCount,
ObservedNets, EffectiveShortNetCount, EffectiveShortNets, DanglingEndpointCount,
DanglingNets, Status, RawID
```

`RecordType` 仅允许 `NET_MEMBER` / `NET_TIE_ENDPOINT` / `NET_TIE_GROUP`（其他 → 报错）。

## 2. DLP 加密拒收

`load_csv` 读前 16 字节，若以 `%TSD-Header-###%` 或 `TSZ#` 开头 → 报错：
「密文容器不是可解析 CSV，需导出/复制为明文 .txt 或明文 .csv」。即 CSV 必须以**解密后**内容喂入。

## 3. Compact 布局归一化

Dali-SCH 的 compact 布局（PIN 行 `Electrical` 为空、`PinNumber/PinName` 移入 PartID 后列）会被
`normalized` 回 25 列标准位置；PinNumber/PinName 可互换（谁数字谁当物理引脚号）。PORT/NET_LABEL/POWER_PORT
也有对应 compact 归一。

## 4. 图构建规则（build_graph）

- **PIN 行**：`Designator` = 器件，`PinNumber`（或符号化时 `PinName`）数字 = 物理引脚。
- **PORT 行**：`Electrical==OUTPUT` → DUT 端口；`I/O` 且为 Kelvin 风格非 slot（`^.+_[FS]_S\d+$` 且不以 `S\d+_` 开头）→ 更正为 OUTPUT；否则 → INOUT 源端口。**匿名 PORT 忽略**（记入 `ignored_ports`，不静默）。
- **方向冲突**：同 PORT 两种 Electrical 风格，保守取 OUTPUT（源不可凭空造出）。
- **`S3_FOVIe_*` → `S3_FXVIe_PLUS_*`** 语义别名归一。
- **NET_TIE_GROUP**：`Status==OK` 且 `EffectiveShortNets` 数 == `EffectiveShortNetCount`，把组内各 net 的器件连接取并集（零欧关系，不造继电器）。
- **singleton_relay_net 删除**：只连单只继电器悬空引脚的冗余网（G3 已查浮空，此处防 G5 重复计为硬失败）。
- **intentional_open_net 删除**：`TP_*` 或含 `NC` 的显式开网（设计意图）。
- **infer_cell**：`K\d+_` → 引脚超出 {1,2} 或引脚名超出 {COMMON,NO} 判 `G6K`，否则 `SW_SPST`；`CAP/C`→Cap、`R`→Res2、`D`→D_Schottky、`TP`→TEST_POINT_SMALL。
- **PIN 短接自动登记（TP 合成）**：PORT-only DUT 端口（`Electrical==OUTPUT` 但无自身 PIN 行）只要与另一个 DUT 端口共 net（同一电气节点 = 短路），就合成 `TP_<PORT>` 测试点（`TEST_POINT_SMALL`，pin 1）挂到该 net。真实 Altium EDIF 正是用 `TP_<PORT>` 标记「端口接线点」；CSV 导出若漏了该测试点，此规则兜底，使短接端口成为 net 成员（sch_parse 经 Step B1 `TP_<PORT>` 映射 + `tp_confirmed` 确认），而非孤立 PORT。已存在同名 `TP_` 时不重复合成；合成结果记入 manifest `synthesized_tps`。

## 5. 六门控（sch_parse.py）

G1c（孤立 PORT）、G1d（TP 短接确认）、G2（功能分类）、G3（浮空引脚/物理规则）、G4（器件参数）、G5（net 完整性）。
任一 FAIL → `PARSER_FAIL`。

## 6. 下游 CBIT 校验（gen_cbit_defines V1–V8）

V1 无重复 / V2 通路完整性 / V3 命名 / V4 量程 / V5 覆盖 / V6 F-S 配对 / V7 FPVI 命名 / V8 继电器状态。
