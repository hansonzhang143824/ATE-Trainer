# 测试函数框架模板

## 普通测试函数
```cpp
DUT_API int TMxxx_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *Param1 = StsGetParam(funcindex, "Param1");
    // CParam *ParamN = StsGetParam(funcindex, "ParamN");  // 如有更多参数
    //}}AFX_STS_PARAM_PROTOTYPES

    double param1[SITE_NUM] = { 0 };
    // double paramN[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 ======
    <%RELAY_CODE%>

    // ====== Step 2: 上电 ======
    <%POWER_ON_CODE%>

    // ====== Step 3: 寄存器配置 ======
    entertestmode();  // 重新上电后先进入测试模式（写密钥解锁测试寄存器），再写寄存器
    <%REGISTER_CODE%>

    // ====== Step 4: 测量 ======
    <%MEASURE_CODE%>

    // ====== Step 5: 下电 ======
    <%POWER_OFF_CODE%>

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        Param1->SetTestResult(site, 0, param1[site]);
        // ParamN->SetTestResult(site, 0, paramN[site]);
    }
    return 0;
}
```

## Toggle/AWG 测试函数

> **参数命名**: AWG/Toggle 两段式 ramp(升+降) → 参数固定 3 个：`<%PARAM_BASE%>_Rise` / `_Fall` / `_Hys`（**基名 = DFT 参数名**，如 `VBAT_UV_Rise`；**非字面 `Param_` 前缀**），**Hys = Rise − Fall**。禁止只生成单个参数。

```cpp
DUT_API int TMxxx_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *<%PARAM_BASE%>_Rise = StsGetParam(funcindex, "<%PARAM_BASE%>_Rise");
    CParam *<%PARAM_BASE%>_Fall = StsGetParam(funcindex, "<%PARAM_BASE%>_Fall");
    CParam *<%PARAM_BASE%>_Hys = StsGetParam(funcindex, "<%PARAM_BASE%>_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: 继电器闭合 ======
    cbite.SetOn(K43_SDA_INT, K58_INT_PU, -1);  // Toggle强制
    delay_ms(3);
    <%MORE_RELAY%>

    // ====== Step 2: 上电 ======
    <%POWER_ON_CODE%>

    // ====== Step 3: 寄存器配置 ======
    entertestmode();  // 重新上电后先进入测试模式（写密钥解锁测试寄存器），再写寄存器
    <%REGISTER_CODE%>

    // ====== Step 4: 测量 (AWG) ======
    <%AWG_CODE%>

    // ====== Step 5: 下电 ======
    <%POWER_OFF_CODE%>

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site) {
        <%PARAM_BASE%>_Rise->SetTestResult(site, 0, rise_result[site]);
        <%PARAM_BASE%>_Fall->SetTestResult(site, 0, fall_result[site]);
        <%PARAM_BASE%>_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
```

## Trim 测试函数
```cpp
DUT_API int TMxxx_Trim_XXX(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *PARAM_step0 = StsGetParam(funcindex, "PARAM_step0");
    // ... step1~stepN (根据 treg 位数决定) ...
    CParam *PARAM_pre_value = StsGetParam(funcindex, "PARAM_pre_value");
    CParam *PARAM_pre_bit = StsGetParam(funcindex, "PARAM_pre_bit");
    CParam *PARAM_post_bit = StsGetParam(funcindex, "PARAM_post_bit");
    CParam *PARAM_updated = StsGetParam(funcindex, "PARAM_updated");
    CParam *PARAM_guessed = StsGetParam(funcindex, "PARAM_guessed");
    CParam *PARAM_target = StsGetParam(funcindex, "PARAM_target");
    CParam *PARAM_post_value = StsGetParam(funcindex, "PARAM_post_value");
    CParam *PARAM_post_rt = StsGetParam(funcindex, "PARAM_post_rt");
    //}}AFX_STS_PARAM_PROTOTYPES

    TRIM_NODE &<TREG_NAME_UPPER> = trim_reg.trim("<TREG_NAME>");  // 变量名 = trim 参数名大写 (global 规则)

    // ====== Step 1: 继电器闭合 ======
    <%RELAY_CODE%>

    // ====== Step 2: 上电 ======
    <%POWER_ON_CODE%>

    // ====== Step 3: 寄存器配置 ======
    entertestmode();  // 重新上电后先进入测试模式（写密钥解锁测试寄存器），再写寄存器
    <%REGISTER_CODE%>

    // 大电流初始化（如有 ≥1A 电流）
    <%FPVI_INIT%>

    // ====== Step 4: Trim execute ======
    <TREG_NAME_UPPER>.execute(measure_<FUNC_NAME>, spec, funcindex, funclabel, 1, 0, 0, 0);

    // 大电流关闭（如有）
    <%FPVI_OFF%>

    // ====== Step 5: 下电 ======
    <%POWER_OFF_CODE%>

    return 0;
}
```

## 模板占位符说明
| 占位符 | 来源 | 说明 |
|--------|------|------|
| `<%RELAY_CODE%>` | 继电器Agent | cbite.SetOn(...) |
| `<%POWER_ON_CODE%>` | 上电Agent | .Set(FV/FI, ...) |
| `<%REGISTER_CODE%>` | DFT Software_initial | 原样复制；**只要配寄存器，之前一律先 `entertestmode()`** —— 不设条件、**不看 DFT 有无 `en_tm[]`**（2026-09-13 用户拍板；模板已含） |
| `<%MEASURE_CODE%>` | 测量Agent | MeasureVI / rampv_capv / execute |
| `<%POWER_OFF_CODE%>` | 下电Agent | 反转序列 |
| `<%FPVI_INIT%>` | FPVI知识库 | 大电流三段式初始化 |
| `<%FPVI_OFF%>` | FPVI知识库 | 大电流三段式关闭 |
| `<%AWG_CODE%>` | 测量Agent | rampv_capv / rampi_capv |
| `<%TREG_NAME%>` | treg文件 | trim_reg.trim()参数名 |

## 注释强制规则

**生成的每一段代码必须有注释**，注释密度不低于参考代码（`references/tm600-normal-highcurrent.cpp`）：

| 代码段 | 最少注释要求 |
|--------|------------|
| Step 1: Connect | 每个 relay 组的连接目标（如 `PMID -> FPVIe FH`） |
| Step 2: Power On | 每个源表电压/电流值 + 源表类型 + 上电顺序原因 |
| Step 3: Register | 每个 I2C 寄存器的 field 含义（从 DFT `//field[...]` 复制） |
| Step 4: Measure | 测量公式、量程选择原因、电流路径说明 |
| Step 5: Power Off | 下电顺序原因（如 `BST先降到与SW齐平再同步归零`） |
| Step 6: Check | 变量名与 DFT 参数名的对应 |

**反例**：生成无注释的裸代码，用户无法理解每行的硬件意图。

## Trim 判定铁律（2026-08-10 用户纠偏）

**DFT `Trim='Y'` → 无条件走 trim 框架**（`trim_reg.trim("key")` + `TRIM_NODE &<KEY_UPPER>`（变量名=trim 参数名大写，如 "osc_64k"→`OSC_64K`，禁止 `PARAM_NODE` 通用名）+ `<VAR>.execute(measure_xxx, spec, funcindex, funclabel, 1, 0, 0, 0)` + step0~N 参数 + 8 后缀 + sub.cpp 尾部 ACTIVE measure 函数）。**执行中发现材料缺失或错误（treg 无对应段、measure 函数注释、寄存器字段矛盾）→ 向用户报告错误**（列出具体不匹配点），**禁止静默降级**为"暂测默认值/普通测试直接测量"。**反例教训 (TM300/301)**: treg 只有 `[osc_4p5m]` 段、sub.cpp 前段 measure_osc_4p5m 被注释 → 误降级直接测频，错；TM301 走 `"osc_4p5m"`（16step），TM300 报告 treg 缺 `[osc_64k]` + 0xF2 写入与 TRIM_REG 矛盾。sub.cpp 正确模式 = 尾部（line 2924+）追加 ACTIVE 实现，参照 measure_bandgap/bg_res_div/iztc_res。treg 权威源 = `NU1201.treg`。
