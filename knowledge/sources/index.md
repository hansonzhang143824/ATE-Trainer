# STS8300 源表 + 系统函数速查表

> 唯一索引：写测试代码需要哪个源表/系统函数 API，先查本表定位到 `sources/` 对应文件。
> 正文（全章 API：函数签名 / 参数 / 量程表 / 精度 / 示例）在各自 `.md`；本表只做定位，不重复正文。
> 迁移自 auto-memory `STS8300-*.md`（2026-08-16，去 frontmatter，来源注记保留在各文件头部）。

## 源表（Source Meters）

| 源表 | 文件 | 全称 | 一句话功能 | 适用场景 |
|------|------|------|-----------|---------|
| ACM200 | `acm200.md` | Analog Channel Module 200 | 精密源测量单元（**浮动源**，硬件手册 p84「二十四通道浮动电压电流源模块」；Low 端经继电器短接 AGND，不闭合仍浮动） | **核心源表**，通用 FV/FI + MeasureVI |
| FOVIe | `fovie.md` | Four-Quadrant VI Source | 四象限电压电流源表 | 标准源表；物理上 `FOVIe = FXVIe_PLUS` |
| FPVIe | `fpvie.md` | Four-Quadrant Power VI | 大电流四象限功率源表，**浮动源** | **≥200mA 大电流**（RDSON 等）、浮动源 |
| FXVIe | `fxvie.md` | Flexible VI | 灵活扩展源表（Gang/TMU/差分测量） | 灵活多通道 / 差分 / 触发 |
| HVIe | `hvie.md` | High Voltage Source Meter | 高压源表（≤3000V） | 高压测试 |
| HPVIe | `hpvie.md` | High Power VI | 大功率源表 | 大功率驱动 |
| QVMe | `qvme.md` | Quick V/I Meter | 快速电压电流表 + FFT 分析 | 高速采样 / FFT |
| ACM | `acm.md` | AC Source Meter | 交流源表 | 交流激励 |

## 系统函数（System Functions）

| 文件 | 内容 |
|------|------|
| `system-functions.md` | 框架函数 / 全局函数 / 测试参数函数 / 进阶函数（Chapter 1） |
| `cbite-qtmue.md` | CBITE 继电器控制 + QTMUE 时间测量（Chapter 2） |

## 其它

| 文件 | 内容 |
|------|------|
| `accotest-api.md` | Accotest 通用 API 参考（原 sources 已有，非本次迁移） |
| `hardware-specs.md` | **STS8300 硬件规格速查**（硬件手册 Rev2.13）：22 模块通道数/量程/浮动/精度表 |
| `treg/` | **TREG 官方解释文档**（机台手册同级）：`TREG_presentation.pdf`（36页基础教程）+ `TREG_execute()_&_trim_groups.pdf`（32页 execute/trim groups 进阶）；索引与语法速查 → `treg/treg-docs-index.md`；setup 文件已由 `.ini` 改为 `.treg` 扩展名 |
| `raw/` | **机台手册原始 PDF + 抽取文本**：`STS8300 编程手册-2.1.15.pdf`（API/量程，无精度）、`STS8300 硬件手册_Rev2.13.pdf`（板卡规格，含精度表）、`AccoTEST 自动化接口编程手册_Rev 1.0.0.pdf`、`accotest_manual.txt`、`hw_specs_extract.txt`（硬件手册 22 模块抽取）、`tmp_*.txt`（各源表抽取）。抽取文本仅供 python 读取（DLP）；正文在 `hardware-specs.md` + 各源表 `.md` |

## 关键区分（写代码前必看）

- **浮动源（2026-08-30 权威规则）**：所有模拟源（ACM/ACM200/FOVIe/FXVIe/FXVIe_PLUS/FPVIe/QVM）本质**浮动**；DCM/QTMU 非浮动。ACM200 等 Low 端常经继电器短接 AGND，**不闭合仍浮动**；FPVIe 走 FPVI_BUS（需按「浮动源规则」闭合 BUS 继电器）。判断看 Low 端链路是否有需闭合的继电器。详见 `knowledge/hardware/` 的 bus-topology 与 `hardware-specs.md`。
- **硬件规格**：各源表通道数/量程/浮动/精度速查 → `hardware-specs.md`（硬件手册 Rev2.13，含精度表；编程手册只有量程）。
- **FOVIe = FXVIe_PLUS**：同一物理卡两个名，类型以 `Pin_Channel_define.h` 为准。详见 memory `nuvolta-source-name-mapping`。
- **量程选择**：量程 ≥ 2×设定值，选最接近一档（每文件内有量程表）。
