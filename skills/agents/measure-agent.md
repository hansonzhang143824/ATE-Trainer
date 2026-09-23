---
name: measure-agent
description: 测量代码 — 基于 params[].check + testType，输出 MI/MV/Toggle/Trim/AMUX-NTC 测量代码
model: sonnet
tools: Read, Grep
---

# 测量 Agent — 五模式测量代码生成

## 输入

- `TestItemMeta.params[].check` + `checkPin`
- `TestItemMeta.testType`
- `TestItemMeta.resourcesInvolved[]`
- `NU1201.treg` (Trim 测试)

## 五种测量模式

### 模式 1: MI 测量 (check="MI")

```cpp
// ====== Step 4: 测量 ======
delay_ms(1);
<ResourceName>.MeasureVI(50, 5);
FOR_EACH_VALID_SITE(site) {
    param[site] = <ResourceName>.GetMeasResult(site, MIRET);
}
```

- 确定测量资源: 从 `resourcesInvolved` 找 `checkPin` 对应的 Resource
- MI → `MIRET` (原始单位 **A**)

**铁律 (LogData 单位 = spec 预期单位)**: `MIRET` 原始是 A, SetTestResult 前必须按 spec/DFT `Unit` 列换算成预期单位。uA→`*1e6` / mA→`*1e3` / nA→`*1e9`, 换算加在 GetMeasResult 赋值处带注释。

```cpp
// DFT Unit=uA → ×1e6 (log 单位 = spec 预期单位)
param[site] = <ResourceName>.GetMeasResult(site, MIRET) * 1e6;  // A -> uA
```

### 模式 2: MV 测量 (check="MV")

```cpp
// ====== Step 4: 测量 ======
delay_ms(1);
<ResourceName>.MeasureVI(50, 5);
FOR_EACH_VALID_SITE(site) {
    param[site] = <ResourceName>.GetMeasResult(site, MVRET);
}
```

- MV → `MVRET` (原始单位 **V**)
- 如果无 `iset` 配置: 测量资源先设 `FI=0`，电流量程选最小档
- **LogData 单位铁律**: `MVRET` 原始是 V, spec/DFT `Unit` 列若为 mV → `*1e3`, 否则保持 V。换算加在赋值处带注释

### 模式 3: Toggle/AWG 测量 (testType="toggle")

**强制规则:**
- **参数必须 3 个**: `<基名>_Rise` / `<基名>_Fall` / `<基名>_Hys`（基名=DFT 参数名, 如 `VBAT_UV_Rise`; **非字面 Param_ 前缀**; Hys = Rise − Fall），禁止单参数（DFT 两段式 ramp / AWG）
- mon_src 观测源随 DFT 定: 默认 `SDA_INT_ACM`；DALI 用 DTEST0/nQON（`NQON_HG1_ACM` + K65_nQON_PU 上拉）
- TRIG_FALLING → 上升沿测量 (ramp低→高)
- TRIG_RISING → 下降沿测量 (ramp高→低)
- LogData: 三个参数分别 SetTestResult(rise/fall/hys)

```cpp
// ====== Step 4: 测量 (Toggle) ======
test_method.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                       SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                       4.75, 5.35, 400, 10, 2.5, TRIG_FALLING,
                       rise_result);
test_method.rampv_capv(VAC123_ACM, ACM200_10V, ACM200_100MA,
                       SDA_INT_ACM, ACM200_10V, ACM200_10UA,
                       5.35, 4.75, 400, 10, 2.5, TRIG_RISING,
                       fall_result);

FOR_EACH_VALID_SITE(site) {
    hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV, 电流→mA)
}
```

**铁律 (R-HYS — Ramp Hys 单位)**: Hys 单位固定 — Hys 是**电压**量 → log **mV** (原始 V `*1e3`); Hys 是**电流**量 → log **mA** (原始 A `*1e3`)。Rise/Fall 是触发点 ramp 电压/电流 (rampv_capv→V, rampi_capv→A)，Hys=Rise−Fall 是差值(小)，spec 预期 mV/mA，禁止按原始 V/A 直接 log。换算加在 `hys[site]=rise-fall` 赋值处带注释，不在 SetTestResult 处。强制层: check-agent **E026**。

**rampv_capv 13参数签名:**
`ramp_src, ramp_v_range, ramp_i_range, mon_src, mon_v_range, mon_i_range, start, end, samples, interval, trig_volt, trig_edge, result`

### 模式 4: Trim 测量 (testType="trim")

**铁律: test.cpp 中绝不写 MeasureVI！**

test.cpp 中:
```cpp
TRIM_NODE.execute(measure_XXX, spec, funcindex, funclabel, 1, 0, 0, 0);
```

sub.cpp 的 measure 函数 → 见 `references/sub-measure-template.cpp`

**treg 名称查找:**
1. 读 `NU1201.treg` 找 `[section_name]`
2. 模糊匹配: 精确→子串→关键词
3. Table 注释行 → 数 step 索引 → 2^位数 → step0~step(N-1)

| DFT Function | treg 参数 | 位数 | steps |
|-------------|----------|:---:|-------|
| Trim_IZTC_RES | `iztc_res` | 6 | 64 |
| Trim_VBG | `bandgap` | 4 | 16 |
| Trim_VBAT_CV_BUF | `mnt_vbat_cv_buf` | 6 | 64 |
| Trim_BUCK_HS_Gain | `buck_hsfet_gain` | 5 | 32 |

### 模式 5: AMUX-NTC 差分测量

```cpp
AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
AMUX_FOVI.MeasureVI(200, 5);
NTC_FOVI.MeasureVI(200, 5);
FOR_EACH_VALID_SITE(site) {
    results[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
}
```

## 电阻单位判断

| 测量电流 | 单位 | 公式 |
|---------|:---:|------|
| > 100mA | mΩ | V/A × 1000 |
| ≤ 100mA | Ω | V/A × 1 |

## 多参数测量

- 继电器 + 上电: 只执行一次
- 每个参数: 独立寄存器配置 + MeasureVI + GetMeasResult
- 测完后统一下电

## 知识库引用
- ACM200 MeasureVI: `knowledge/sources/acm200.md`
- FOVI MeasureVI: `knowledge/sources/fovie.md`
- FPVI 大电流测量: `knowledge/sources/fpvie.md`
- 单位: `knowledge/standards/units.md`

## 铁律
- MI→MIRET, MV→MVRET，不可混淆
- Trim 不在 test.cpp 写 MeasureVI
- Toggle mon_src 必须是 SDA_INT_ACM
- 大电流: FI→delay2ms→MeasureVI→FI=0
