# 命名规则

## 函数命名
```
TMxxx_XXX               — 普通测试 / Toggle测试
TMxxx_Trim_XXX          — Trim测试
```

## 参数命名
- CParam 对象: `Param_XXX`（大驼峰）
- 数组: `param[SITE_NUM]`（小写）
- AWG/Toggle 两段式 ramp 固定 3 参数: `<基名>_Rise`, `<基名>_Fall`, `<基名>_Hys`（基名=DFT 参数名, 如 `VBAT_UV_Rise`; 非字面 Param_ 前缀; Hys = Rise − Fall）
- Trim 固定 9 后缀: `PARAM_step0~stepN`, `PARAM_pre_value`, `PARAM_pre_bit`, `PARAM_post_bit`, `PARAM_updated`, `PARAM_guessed`, `PARAM_target`, `PARAM_post_value`, `PARAM_post_rt`

## 源表命名（程序中的变量名）
来自 SCH-Connect-Map / Pin_Channel_define.h，不可虚构。

格式: `PIN1_PIN2_..._PINn_<源表类型>`
- 直连 Pin 在前，需 relay 切换的 Pin 在后
- 例: `VBAT_ACM`, `SDA_INT_ACM`, `VAC123_ACM`

## 继电器命名（程序中的名称）
原理图名称去掉 `_S1`/`_S2` 后缀:
- `K31_BUS_PMID_S1` → `K31_BUS_PMID`
- `K32_PMID_Cap_G2` → `K32_PMID_Cap`

**Cap 继电器特别注意:** Cap2 定义格式为 `电容值, 继电器名, 电阻值`，继电器只取中间字段。
- `Cap_4.7uF, K32_PMID_Cap, R_1K` → 继电器名 = `K32_PMID_Cap`
- ❌ 错误: `K32_PMID_Cap_R_1K` (把电阻值拼进继电器名)
- ✅ 正确: `K32_PMID_Cap`

## treg 参数命名
`trim_reg.trim("NAME")` 中的 NAME 必须匹配 `NU1201.treg` 中的 `[section_name]`
