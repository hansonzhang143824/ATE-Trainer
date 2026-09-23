# TM403-425 设计文档（15 项，2026-08-10）

## 总览

15 项 isCodeGen='Y'：8 Toggle + 4 FB + 3 Trim。跳过 TM414/415/416（isCodeGen 空）、TM404/405/407/417/423（无 OVERVIEW 行）。

源表：VBAT_PD3_FXVI(FXVIe_PLUS)、VBUS_DRVH1_ACM(ACM200)、VAC123_AMUX_ACM(ACM200)、VDM_SDA_ACM(ACM200)、NQON_HG1_ACM(ACM200)。

## Toggle 8 项（VBAT/VBUS ramp + NQON 观测 DTEST0）

统一 TRIG 模式（参考 TM111/TM112/TM400 已验证）：**rising ramp→TRIG_FALLING, falling ramp→TRIG_RISING**（nQON 经 1.65V 阈值）。

| TM | 名称 | DMUX_SEL | 额外寄存器 | 供电源 | ramp 源 | ramp 双向 | VBUS/VBAT 量程 | 期望 r/f |
|----|------|----------|-----------|--------|---------|-----------|---------------|----------|
| 403 | VBUS_REVI_VTH | 30 (0x1E) | — | VBAT=4V | VBUS 3.7→4.5→3.7 | 双向 | ACM200_10V | -0.016/-0.138 |
| 406 | VBAT_LOW_VTH | 26 (0x1A) | 0x09=0x0A | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 2.686/2.491 |
| 408 | VBAT_OVP | 28 (0x1C) | — | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 4.231/4.158 |
| 409 | VBUS_HT_4P8V | 31 (0x1F) | 0x09=0x0A | VBAT=4V | VBUS 4→7→4 | 双向 | ACM200_40V | 4.661/4.562 |
| 410 | VTRIKLE_VTH1 | 29 (0x1D) | 0x0A=0x09 | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 2.687/2.393 |
| 411 | VTRIKLE_VTH2 | 29 (0x1D) | — | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 2.983/2.690 |
| 412 | VRE_CHG_VTH1 | 27 (0x1B) | — | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 3.979/4.030 |
| 413 | VRE_CHG_VTH2 | 27 (0x1B) | 0x0A=0x69 | VAC1=5V | VBAT 0→5→0 | 双向 | FXVIe_PLUS_10V | 3.882/3.929 |

- VBUS ramp 类（403/409）：Step1 闭 K13_VBAT_Cap + K65_nQON_PU，VBUS 不闭 K5（E012 ramp 源例外）
- VBAT ramp 类（406/408/410-413）：Step1 闭 K21_VAC_Cap + K65_nQON_PU，VBAT 不闭 K13（E012 ramp 源例外）
- Step3 均含 0x10=0x43, 0x57=0x08 + 0x56=DMUX_SEL
- Step5 三步下电含 ramp 源 + 供电源 + NQON

## FB 4 项（ATEST0 MV via VDM，V(ATEST0)=通道 voutp）

| TM | 名称 | 0x11 | 被测通道 | 电压 | VAC/VBUS 量程 | 通路继电器 |
|----|------|------|---------|------|-------------|-----------|
| 418 | VAC1_FB | 0x11 | VAC1 | 5V | ACM200_10V | 无（NC 直连）|
| 419 | VAC2_FB | 0x12 | VAC2 | 10V | ACM200_40V | K19_ACM0_VAC2 |
| 420 | VAC3_FB | 0x13 | VAC3 | 15V | ACM200_40V | K18_ACM0_VAC3 |
| 421 | VBUS_FB | 0x14 | VBUS | 4→10V | ACM200_40V | 无（NC 直连）|

- Step1: K13_VBAT_Cap + K21_VAC_Cap（VBUS 用 K5_VBUS_Cap）+ 通路继电器
- Step2: VBAT=4V (FXVIe_PLUS_10V/100MA) + VAC/VBUS FV
- Step3: 0x10=0x43, 0x11=<sel>, 0x57=0x02(EN_ATEST0), 0x5E=0x1F(ATEST0_MUX=31=channel voutp)
- Step4: VDM_SDA_ACM.Set(FI,0,10V,10UA) → MeasureVI(50,5) → MVRET
- 期望: VAC1/10, VAC2/10, VAC3/10, VBUS/10

## Trim 3 项（execute + measure，VDM MV）

| TM | 名称 | trim key | step 数 | EFUSE | 寄存器 (ATEST) | VBAT | target |
|----|------|----------|---------|-------|---------------|------|--------|
| 422 | VBAT_FB | mnt_vbat_rsns_loop | step0~15 | F7 | 0x57=0x02, 0x5E=0x17(FB_VBAT) | 4→5V | 0 (偏差) |
| 424 | VREF_TRIM | mnt_dac_buf_os | step0~31 | F7+F8 | 0x57=0x02, 0x5E=0x13(VREF_1P68V) | 4.4V | 1680 mV |
| 425 | VREF_1P2V_BUF | mnt_v1p2_buf | step0~15 | F6+F7 | 0x57=0x04(EN_ATEST1), 0x58=0x02(ATEST1_MUX=2) | 4.4V | 1200 mV |

- Step1: K13_VBAT_Cap（VDM K59 NC 直连）
- Step3: 0x10=0x43 + ATEST 寄存器
- Step4: VDM.Set(FI,0,10V,10UA) 高阻 → `<KEY>.execute(<measure_fn>, spec, funcindex, funclabel, 1, 0, 0, 0)`
- TRIM_NODE 变量名 = trim 参数名大写（E028）：MNT_VBAT_RSNS_LOOP / MNT_DAC_BUF_OS / MNT_V1P2_BUF
- measure 返回：422 = (V(FB)-2.0)×1e3 mV 偏差；424 = V×1e3 mV；425 = V×1e3 mV

## sub.cpp 新增 measure 函数（DALI 风格，参照 measure_bandgap）

- measure_mnt_vbat_rsns_loop: 写 0xF7 → VDM MeasureVI(50,5) → (MVRET - 2.0)*1e3
- measure_mnt_dac_buf_os: 写 0xF7 + 0xF8 → VDM MeasureVI → MVRET*1e3
- measure_mnt_v1p2_buf: 写 0xF6 + 0xF7 → VDM MeasureVI → MVRET*1e3

插入点：test.cpp 末尾（TM402 后，5810 行后）；sub.cpp measure_osc_64k 后（3100 行后）。
DLP：test.cpp UTF-8-BOM+CRLF 字节写；sub.cpp GBK 字节写。
