# 资源分配表 — Sheet20 NU6801 Site1

> 来源：`Sheet20_NU6801_SITE1.NET` | 工位后缀 `_S1` 已移除  
> **更正：FPVI_FL_BUS 与 S30_FOVIe_FH2 通过 K31_BUS_PMID 的 A 模块 3-4 脚连接。**

---

## 源表资源分配

| 源表名称（命名规则） | 对应 Pin | 源表类型 | 通道 | 选择器链 | 直连Pin |
|------|----------|:---:|------|------|:---:|
| ACDRV123_ACM | ACDRV1, ACDRV2, ACDRV3 | ACM200 | S22 | K22→K23 | — |
| VAC123_ACM | VAC1, VAC2, VAC3 | ACM200 | →跨页 | K35→K36 | — |
| KLV12_ACM | KLV1, KLV2 | ACM200 | →跨页 | K20 | — |
| VBAT_ACM | VBAT | ACM200 | →跨页 | — | ✓ |
| VBUS_ACM | VBUS | ACM200 | →跨页 | — | ✓ |
| VDRV_ACM | VDRV | ACM200 | →跨页 | — | ✓ |
| VCC_ACM | VCC | ACM200 | →跨页 | — | ✓ |
| VBATD_ACM | VBATD | ACM200 | →跨页 | — | ✓ |
| PMID_ACM | PMID | ACM200 | →跨页 | — | ✓ |
| BST_SW_ACM | BST, SW | ACM200 | →跨页 | — | — |
| NTC_FOVI | NTC | FOVIe | S30_CH3 | — | ✓ |
| AMUX_NTC_FOVI | AMUX, NTC | FOVIe | →跨页 | — | — |
| PGND_ACM | PGND | ACM200 | →跨页 | — | — |
| FPVI | (大电流注入) | FPVIe | — | — | — |
| SDA_INT_ACM | SDA, INT | ACM200 | →跨页 | — | — |
| SCL_ACM | SCL | ACM200 | →跨页 | — | ✓ |

> `→跨页` = 具体 ACM200 通道号在仪器接口图（如 `P123_S27ACM_S28ACM.SchDoc`）

---

## 每个 Pin 链路详表

### ACDRV1/2/3 — 共享 S22_ACM200

| Pin | BUS Relay | 选择器状态 | Cap1 | Cap2 | Kelvin | P2P | 上拉 |
|-----|-----------|----------|:---:|:---:|:---:|:---:|:---:|
| ACDRV1 | K21_BUS_ACDRV | K22=NC, K23=NC | — | — | R_ACDRV1_K | K47 | — |
| ACDRV2 | K21_BUS_ACDRV | K22=NC, K23=ON | — | — | R_ACDRVw_K | K48 | — |
| ACDRV3 | K21_BUS_ACDRV | K22=ON, K23=NC | — | — | R_ACDRV3_K | K49 | — |

```
S22_ACM200_FH/SH → K21(C1,NC) →[通电]→ K21(O1)→K22.COM1 → K23.COM1 → PIN
                                              K21(O2)→K22.COM2 → K23.COM2 → PIN_S
```

### VAC1/2/3 — 共享 ACM200

| Pin | BUS Relay | 选择器状态 | Cap1 | Cap2 | Kelvin | P2P |
|-----|-----------|----------|:---:|:---:|:---:|:---:|
| VAC1 | K34_BUS_VAC | K35=NC, K36=NC | Cap1_VAC1 | K37(共享) | — | K50 |
| VAC2 | K34_BUS_VAC | K35=NC, K36=ON | Cap1_VAC2 | K37(共享) | — | K51 |
| VAC3 | K34_BUS_VAC | K35=ON, K36=NC | Cap1_VAC3 | K37(共享) | — | K52 |

### KLV1/2 — 共享 ACM200

| Pin | BUS Relay | 选择器状态 | Cap1 | Cap2 | Kelvin | P2P |
|-----|-----------|----------|:---:|:---:|:---:|:---:|
| KLV1 | K19_BUS_KLV | K20=NC | — | — | R_SW_K1 | K39 |
| KLV2 | K19_BUS_KLV | K20=ON | — | — | R_SW_K2 | K40 |

### 直连 Pin

| Pin | BUS Relay | Cap1 | Cap2_Relay | Kelvin | P2P | 上拉 |
|-----|-----------|------|-----------|--------|:---:|:---:|
| VBAT | K29_BUS_VBAT | Cap1_VBAT | K30_VBAT_Cap | R_VBAT_K | — | — |
| VBUS | K15_BUS_VBUS | Cap1_VBUS | K16_VBUS_Cap | R_VBUS_K | — | — |
| VDRV | K26_BUS_VDRV | Cap1_VDRV | K28_VDRV_Cap | R_VDRV_K | — | — |
| VCC | — | Cap1_VCC | K25_VCC_Cap | R_VCC_K | — | — |
| VBATD | — | Cap1_VBATD | K66_VBATD_Cap | R_VBTAD_K | — | — |
| PMID | K31_BUS_PMID | Cap1_PMID | K32_PMID_Cap | R_PMID_K | — | — |
| BST | K38_BUS_BST | — | K18_BST_SW_Cap | R_BST_K | — | — |
| SW | K17_BUS_SW | — | K18_BST_SW_Cap | R_SW_K | — | — |
| NTC | K41_BUS_NTC | — | — | R_NTC_K | — | K56 |
| AMUX | K40_BUS_AMUX | — | — | R_AMUX_K | — | — |
| PGND | K42_BUS_PGND | — | — | R_PGND_K | — | — |
| INT | — | — | — | R_INT_K | K46 | K58 |
| SDA | — | — | — | R_SDA_K | — | K57 |
| SCL | — | — | — | — | — | K53 |

---

## FPVI 总线继电器

| BUS | 连接的继电器 COM 端 |
|-----|------|
| FPVI_FH_BUS | K15(3), K17(3), K19(3), K21(3), K26(3), K40(3), K41(3), K42(3) |
| FPVI_SH_BUS | K15(6), K17(6), K19(6), K21(6), K26(6), K40(6), K41(6), K42(6) |
| FPVI_FL_BUS | K29(3), K34(3), K38(3), K31(3) |
| FPVI_SL_BUS | K29(6), K31(6), K34(6), K38(6) |

---

## GND 短接

| 连接 | 器件 |
|------|------|
| AGND ↔ DGND | R_DGND2AGND |
| AGND ↔ JGND | R_JGND2AGND |
| AGND ↔ AGND_F_S1 | R_GND_S1 |
