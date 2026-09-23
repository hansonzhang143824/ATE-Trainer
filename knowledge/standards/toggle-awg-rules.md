# Toggle/AWG 规则（两段式 ramp）

> 使用方：measure-agent（Toggle/AWG 测量）、Step1 gen_test_conditions.py（testType 覆盖判定）、verify_awg_params.py（门禁）。
> 关联：`framework.md`（Toggle 框架）、`units.md`（R-HYS 单位）、`error-checklist.md`（H010）、`naming.md`（3 参数命名）。

## 测量方法判定：AWG 是增项（R-AWG，2026-08-27 用户拍板）

**AWG（ramp + toggle capture）是相对四种基本 IV 测量（FV-MV / FI-MV / FV-MI / FI-MI）的增项，不是替代**。判定先问「有没有 AWG」：
- **无 AWG**（DFT 无 ramp / 无 Toggle）→ 按四种基本 IV 之一写（`MeasureVI` / Set + Measure），**禁止按 AWG 写**（禁 test_method）
- **有 AWG** → 按 AWG 写（`test_method` `rampv_capv`/`rampi_capv`）；AWG 可与基本 IV **同时存在**（同测例既有静态 IV 测量又有 ramp 捕获，YAML 的 `measure` 与 `observe` 可共存），也**可只有 AWG**（TM616：ramp AMUX → capture I(ATEST0)，observei 即测量，无独立 measure）

## Toggle/AWG 参数规则（两段式 ramp）

AWG/Toggle 两段式 ramp（升+降）测试 → 参数固定 **3 个**：`<DFT参数基名>_Rise` / `<DFT参数基名>_Fall` / `<DFT参数基名>_Hys`（如 `VBAT_UV_Rise`；基名=DFT 参数名，**非字面 `Param_` 前缀**），**Hys = Rise − Fall**。禁止只生成单个参数；LogData 三个参数分别 SetTestResult。检查项: check-agent **E005** / **H010**；门禁 `verify_awg_params.py`。

**段数从 ramp 曲线推导（升+降=2 段→3 参数），不看 DFT 期待值个数**：DFT 期待值列只有一个值、但 ramp 曲线是两段（如 1.3→1.5→1.3），仍是 Toggle 3 参数（佐证 TM616 VC_OFFSET 期待单值 "1.4"，但 3 参数；TM615 PSM_THREHOLD 同理）。无 ramp 的静态测试（如 TM614 V(COMP)）才是单参数。

### 段数 = ramp **调用数**（2026-09-13 用户拍板，门禁按此判定）

| ramp 调用数 | 语义 | 参数契约 |
|---|---|---|
| **≥2** | 两段式（升+降）→ 有「触发阈值」+「释放阈值」 | 必须 `<基名>_Rise/_Fall/_Hys` 三件套（Hys=Rise−Fall） |
| **=1** | 单向单段 = **单阈值设计**（ZCD / OCP / 负向限流）→ 不存在「释放阈值」 | **不适用** 3 参数规则，单参数即正解（如 `LS_ZCD` / `HS_ZCD` / `HS_NEG` / `BOOST_HS_OCP`） |
| **=0** | 无 AWG | 不进本门禁（按四种基本 IV 写） |

判「调用数」必须用**调用模式** `rampv_capv`/`rampi_capv` **紧跟 `(`**，不可用裸字符串（裸字符串会把注释里的提及也算作调用）。

## Toggle trigger 规则（2026-09-18 用户全局裁决）

**升扫（输入从低到高）→ TRIG_FALLING；降扫（输入从高到低）→ TRIG_RISING。** 所有方法均按此触发边沿执行；与此相反的旧方法描述和黄金案例只作历史参考，不作为触发极性的依据。Rise/Fall 参数名仍按输入扫描方向命名。

## Toggle 强制继电器

Toggle 观测需双继电器闭合（如 K43_SDA_INT + K58_INT_PU），见 `relay-checklist.md` 角色继电器段。

## 工具

`verify_awg_params.py`（`--src test.cpp [--strict-params]`）→ Toggle 3 参数门禁（E005，收尾必跑）。

**2026-09-13 修两处缺陷后，历史「豁免白名单」已作废**（原记 TM607/608/609/640/425 待长期豁免）：
1. **规则适用条件过宽** → 改为按「ramp 调用数」判定（见上表）：TM607/608/609/640 是**单向单段单阈值**（DFT 只有 1 个 `iset` 设点、代码只有 1 次 ramp 调用），3 参数规则本就不适用 → 真豁免，无需白名单。
2. **切块错归属** → 原 `re.split('吃到下一个 DUT_API 之前')` 把**下一个函数的头注释**吞进本函数块（test.cpp 98/99 函数带前置注释块 → 99/99 块都有此泄漏，实测最大 1552 字节）；TM425_VREF_1P2V_BUF 实为 **Trim** 测试，只因下一条测试(TM607-609)的批注释里写了 `rampi_capv` 就被误报。已改为**取函数体（花括号配平）**，并把 `Trim_` 命名纳入切块（原只认 `TM\d+_`，3 个 Trim 函数会被并进上一个 TM 块）。

