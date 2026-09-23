# Pin→源表→继电器 映射

## Pin→Resource 映射

| Pin | Resource Name | Type | 槽位 |
|-----|--------------|------|------|
| VBAT | VBAT_ACM | ACM200 | — |
| PMID | PMID_FOVI | FOVI | — |
| SW | SW_ACM | ACM200 | — |
| BST | BTST_ACM | ACM200 | — |
| VDRV | VDRV_AMP_ACM | ACM200 | — |
| VBUS | VBUS_FOVI | FOVI | — |
| VAC1 / VAC2 / VAC3 | VAC123_ACM | ACM200 | — |
| AMUX | AMUX_FOVI | FOVI | — |
| NTC | NTC_FOVI | FOVI | — |
| INT / SDA | SDA_INT_ACM | ACM200 | — |
| FPVI_BUS | FPVI | FPVI | — |

> **权威来源**: `SCH-Connect-Map.txt` / `Pin_Channel_define.h`。本表为常用速查，最终以 map/define 为准。

## 资源命名规则

格式: `PIN1_PIN2_..._PINn_<源表类型>`

| 优先级 | 条件 | 示例 |
|:---:|------|------|
| 1（最前） | 直连（无 relay 切换） | `VBAT_ACM` |
| 2 | 切换 1 个 relay | `ACDRV1_ACM` |
| 3+ | 切换 2+ relay | 依次后移 |
| 光耦 | 随机排序 | — |

## 常见继电器速查

| 继电器 | 功能 | 何时闭合 |
|--------|------|----------|
| K30_VBAT_Cap | VBAT Cap2 电容 | VBAT参与时 |
| K28_VDRV_Cap | VDRV Cap2 电容 | VDRV参与时 |
| K31_BUS_PMID_S1 | PMID→FPVI_BUS | PMID跨Pin操作 |
| K32_PMID_Cap | PMID Cap2 | FPVI浮动MI时 |
| K15_BUS_SW_S1 | SW→FPVI_BUS | SW跨Pin操作 |
| K17_BUS_BST_S1 | BST→FPVI_BUS | BST跨Pin操作 |
| K43_SDA_INT | INT上拉 | Toggle测试 |
| K58_INT_PU | INT信号 | Toggle测试 |
| K35_VAC_SHARE | VAC3切换 | VAC3参与时 |
| K36_VAC_SHARE2 | VAC2切换 | VAC2参与时 |

> **完整映射**: 见 `SCH-Connect-Map.txt`
