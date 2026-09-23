# 会话 #31 — I'm working in the Nuvolta STS8300 ATE offline coding project at D:\\Newtest\\CLAU

- 文件：`agent-a0c94c95e413d92dd.jsonl`（项目 subagents）
- 时间：2026-08-26T04:43:10.948Z → 2026-08-26T04:47:26.880Z，大小 0.8 MB
- 用户消息 1 条 / 助手文本 22 段 / 工具调用标记 43 行

---

## 对话正文（工具输出已剥离）

### 2026-08-26 04:43:10 [user]

I'm working in the Nuvolta STS8300 ATE offline coding project at D:\Newtest\CLAUDE_PROCESS. I need to understand the full workflow for writing a batch of test-item functions (TM614, TM615, TM616) so I can plan the implementation.

Please read and report on the mechanics of the codegen pipeline and the most recent, similar batch. Focus on:

1. `.claude/skills/nuvolta-codegen.md` — the master skill. Read the ENTIRE "写TM测试代码" flow: dual-path entry (A: has resource allocation table → dual-parse--A; B: no → sch-parse), cbit common pre-step (gen_cbit_defines.py --cbit [--stat] [--verify]), test-type identification, test-flow 6-step, relay checklist, anti-short rules, floating source rules, measurement rules, power-on/power-off scripting (gen_power_sequence.py), register config iron law, range selection, high-current, trim, toggle, function framework, common errors. Summarize the concrete commands and the order.

2. How the last completed batch was written. Read daylog/2026-08-10.md and any daylog entries about TM403-425 (15 functions: 8 Toggle + 4 FB + 3 Trim) and TM216-402 (9 functions). Identify ONE representative example TM function in test.cpp (the VS project test source) that is a good template. Report: the function signature, the AFX comment block, how cbit.SetOn(relay) is done, how power_on/power_off scripts are called, register i2c writes, measurement, SetTestResult/LogData. Give me the exact file path of test.cpp and a representative function body.

3. The meta gate: gen_testitems_meta.py + check_testitems_meta.py --require-all and --require-scope. How to run them and what they check.

4. Which scripts must be run after writing (gen_testitems_meta.py, check_testitems_meta.py --require-all/--require-scope, verify_relay_trace.py, verify_awg_params.py, gen_cbit_defines.py --verify, fast_rebuild.ps1) and in what order to gate completion.

Do NOT modify any files. Report concisely with exact file paths, commands, and concrete details. Prefer quoting the actual skill flow and the structural skeleton of a real TM function.

### 2026-08-26 04:43:12 [assistant]

I'll start by exploring the project structure and reading the key files in parallel.
- [tool] Bash
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:43:18 [assistant]

Let me read the master skill and daylog files in parallel.
- [tool] Read
- [tool] Read

### 2026-08-26 04:43:21 [assistant]

Now let me find the test.cpp file and read the other daylogs for context.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:43:30 [assistant]

Let me locate the verify scripts and read the meta gate scripts.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:43:36 [assistant]

Let me read the meta gate scripts and key verification scripts.
- [tool] Read
- [tool] Read

### 2026-08-26 04:43:38 [assistant]

Now let me examine project_config.json, fast_rebuild.ps1, and the verification scripts' interfaces.
- [tool] Read
- [tool] Read
- [tool] Bash

### 2026-08-26 04:43:42 [assistant]

The real VS project source is at D:/PROJECT6-DALI/devel/source per project_config.json. Let me verify.
- [tool] Bash

### 2026-08-26 04:43:49 [assistant]

The real source tree may be at D:/PROJECT6-DALI. Let me inspect it.
- [tool] Bash

### 2026-08-26 04:43:58 [assistant]

The real test.cpp is DLP-encrypted (binary). Let me find a readable copy — check the backup and other test.cpp variants.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:44:09 [assistant]

The readable copy is at D:\Newtest\CODEX\_PROCESS\test.cpp. Let me inspect it and find the TM403-425 batch functions.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:44:18 [assistant]

Let me search for readable copies of the DALI test.cpp containing the TM403-425 batch, and inspect the archived batch generator.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:44:24 [assistant]

Let me read the archived batch generator for TM403-425, which contains the templates and generated function structure.
- [tool] Read

### 2026-08-26 04:44:30 [assistant]

This is the definitive batch generator. Now let me read the verification script interfaces and the remaining daylogs to understand the meta gate and the most recent batches.
- [tool] Bash
- [tool] Read

### 2026-08-26 04:44:37 [assistant]

Let me fix the script extraction and read the remaining daylogs.
- [tool] Bash

### 2026-08-26 04:44:41 [assistant]

The docstrings are GBK-encoded. Let me re-extract with the correct encoding.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:44:58 [assistant]

The scripts are UTF-8; the console mangled the display. Let me read the argparse/usage sections directly with the Read tool.
- [tool] Bash
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-26 04:45:10 [assistant]

Let me read proj_config.py for derived paths, generate representative function bodies from the archived generator, and check the remaining daylogs.
- [tool] Read
- [tool] Bash

### 2026-08-26 04:45:19 [assistant]

Let me generate the Trim function body, check the OVERVIEW sheet for TM614-616, and read the remaining daylogs.
- [tool] Bash
- [tool] Bash

### 2026-08-26 04:45:37 [assistant]

Let me read the remaining daylogs (2026-08-24 and 2026-08-09) for the most recent pipeline state and the material gate context.
- [tool] Read
- [tool] Read

### 2026-08-26 04:45:51 [assistant]

Let me read gen_cbit_defines.py to confirm its --verify invocation, and sample the meta JSON.
- [tool] Read
- [tool] Bash

### 2026-08-26 04:45:59 [assistant]

Let me verify the references/materials layout for the material gate and check the framework doc for the toggle/trim templates.
- [tool] Bash
- [tool] Bash
- [tool] Read

### 2026-08-26 04:47:26 [assistant]

I now have a complete picture of the pipeline. Here is my report.

---

# Nuvolta STS8300 codegen pipeline — mechanics and the last similar batch

## 0. Key file paths

| Asset | Path |
|---|---|
| Master skill | `D:\Newtest\CLAUDE_PROCESS\.claude\skills\nuvolta-codegen.md` |
| Sch-parse skill | `D:\Newtest\CLAUDE_PROCESS\.claude\skills\sch-parse.md` |
| Last-batch daylog | `D:\Newtest\CLAUDE_PROCESS\daylog\2026-08-10.md` (also `2026-08-09.md`, `2026-08-16.md`, `2026-08-24.md`) |
| Real VS test source | `D:\PROJECT6-DALI\devel\source\test.cpp` (DLP-encrypted — see note) |
| VS source dir | `D:\PROJECT6-DALI\devel\source` (test.cpp / sub.cpp / StdAfx.h / Pin_Channel_define.h) |
| Project config | `D:\Newtest\CLAUDE_PROCESS\project_config.json` (sole input manifest) |
| OVERVIEW (DFT) | `D:\Newtest\CLAUDE_PROCESS\Project\DALI\Dali_testmode.xlsx` |
| SCH-Connect-Map | `D:\Newtest\CLAUDE_PROCESS\Project\DALI\SCH-Connect-Map.txt` |
| COMPONENT-STATISTIC | `D:\Newtest\CLAUDE_PROCESS\Project\DALI\COMPONENT-STATISTIC.txt` |
| CBIT table | `D:\Newtest\CLAUDE_PROCESS\Project\DALI\CBIT表-DALI.xlsx` |
| Meta output | `D:\Newtest\CLAUDE_PROCESS\Project\DALI\meta\dali_tm_meta.json` (currently 81 functions; TM614-616 not yet present) |
| Archived batch generator | `D:\Newtest\CLAUDE_PROCESS\_archive\gen_insert_tm403_425.py` |
| Golden material index | `D:\Newtest\CLAUDE_PROCESS\.claude\references\param_type_index.md` |
| Pipeline scripts | `D:\Newtest\CLAUDE_PROCESS\{gen_testitems_meta.py, check_testitems_meta.py, verify_relay_trace.py, verify_awg_params.py, verify_single_fn.py, verify_material_receipt.py, gen_cbit_defines.py, gen_paths.py, gen_path_defines.py, gen_power_sequence.py, fast_rebuild.ps1}` |

> **DLP note:** both `D:\PROJECT6-DALI\devel\source\test.cpp` and `D:\Newtest\CLAUDE_PROCESS\test.cpp` are DLP-transparent-encrypted (start with `TSZ#`). All scripts read them via a `read_enc()` fallback (`utf-8-sig→utf-8→gbk→latin-1`). You must write these DLP files in **byte mode** `open(path,'wb')` (BOM+CRLF preserved); a text-mode write corrupts CRLF into `\r\r\n` (see 2026-08-10 "教训" entry). The exact function bodies that went into test.cpp are reconstructable from the archived generator (`_archive/gen_insert_tm403_425.py`), which is what I used below.

---

## 1. The master skill — `nuvolta-codegen.md`, full "写TM测试代码" flow

The skill is an entry gate with a **dual-path architecture** + a **cbit common pre-step** + a **shared generation loop** + a **double check close-out**.

### Entry / Step 0 — path split
- **Flow A** (has `资源分配表.csv`): `dual-parse --A` → full `TestItemMeta` (incl. `resourcesInvolved`, `voltageInference`). No sch-parse.
- **Flow B** (no resource table, only `.net`): `sch-parse` → `COMPONENT-STATISTIC` + `SCH-Connect-Map`; `Pin_Channel_define.h` for source-name mapping; `dual-parse --B` (DFT-only) → partial TestItemMeta (`resourcesInvolved` empty; relay-agent fills from SCH-Connect-Map).
- Current DALI project runs **Flow B** (config `project_config.json` has no resource-table in `inputs`, only in `optional_inputs`).

### Step 2 — cbit common pre-step (every entry)
- **If no relay definition file** (`relay.h` / StdAfx.h defines): create it.
  - A path: only P1 single-point + P4 check (relay.h single-point only).
  - B path: full four stages (singlepoint → path-finder → path-namer → check) incl. path relays.
- **If a definition file exists**: check-only, no update (unless user asks).
- Concrete commands:
  - **P1 (A+B):** `python gen_cbit_defines.py --cbit <CBIT表.xlsx> --stat <COMPONENT-STATISTIC.txt>` → single-point `#define` block + V1~V8 report (**OVERALL PASS required before use**).
  - **P2 (B only):** prefer SCH-Connect-Map; fallback `python gen_paths.py --netlist <CSV_CONNECTIVITY.NET> --cbit <CBIT表.xlsx> --json`.
  - **P3 (B only):** `python gen_path_defines.py` → path defines appended to StdAfx.h 2.x section; verify with `--verify` / `--check-relay` / `--audit-rules`.
  - **P4 (A+B):** `python gen_cbit_defines.py --cbit <CBIT表.xlsx> --stat <COMPONENT-STATISTIC.txt> --verify <relay.h/StdAfx.h> [--map <SCH-Connect-Map.txt>]` (B adds `--map` to run V2/V7).

### Steps 3–4 — shared generation loop (per test item, A/B share one pipeline)
0. **Material gate (pre-generation, 2026-08-23):** classify param type per `param_type_index.md` → load `chip/` + `method/` + **all** `code/` gold materials → write receipt → `python verify_material_receipt.py --receipt <receipt> --tm <TM>` → **FAIL blocks relay-agent** (TM607-609 root cause: Current Threshold / ZCD must declare both `code/HS_ZCD.cpp` + `code/LS_ZCD.cpp`, only one → FAIL).
1. **relay-agent** → `cbite.SetOn(...)` (A: resource table / B: SCH-Connect-Map).
2. Generate **pin-map JSON** (`{pinMap: {PIN: {object,type}}, currentLimit, rampProfile, mvNoFipins}`).
3. **`python gen_power_sequence.py --meta <meta.json> --pin-map <map.json>`** → one call outputs three `###SECTION:...###` blocks:
   - `###SECTION:POWER_ON###` → Step 2
   - `###SECTION:POWER_STATE###` → PowerState JSON (for the power-off section)
   - `###SECTION:POWER_OFF###` → Step 5
4. Template fill → `entertestmode();` + DFT `Software_initial` copied verbatim.
5. **measure-agent** → measure code (MI/MV/Toggle/Trim/AMUX-NTC).
6. Template fill → LogData (`SetTestResult`).
7. **Single-fn smoke (B-001, mandatory):** `python verify_single_fn.py --src <test.cpp> --fn <当前TM>` (7 checks: placeholder residue / semicolon-before-comment / brace balance / CRLF clean / `<%X%>` template residue / lifecycle six-stage behavior / register-unlock order). **FAIL → stay on current TM; only PASS → next.**
8. Last item? no → loop; yes → Step 5.

### Step 5 — close-out double-check
- **check-agent** (60+ checks, P/E/R/H layers).
- `python gen_cbit_defines.py --verify <relay.h/StdAfx.h>` → V1~V8.
- `python verify_awg_params.py --src test.cpp` → Toggle/AWG 3-param gate (E005, "必跑").
- **Meta full-coverage gate (mandatory per batch, 2026-08-10):** "写完代码 → `python check_testitems_meta.py --require-all --require-scope <本批范围>` → 再 `verify_relay_trace.py --meta <新meta> --warn-as-error`".
- FAIL → fix → re-check → PASS.

### Concrete rules carried by the flow
- **反短接铁律 (P006/H009):** source→target path must not pass through/connect other DUT pins. Share 2-in-1 relays (e.g. PB5/VAC Force/Sense) close only the target side, never both. Prefer SCH-Connect-Map paths that reach only the target pin (e.g. VAC1 uses `VAC123_AMUX_ACM`, not a path that short-crosses PB5). Exception: floating-source isopotential/current-loop two pins are both targets.
- **Closed loop:** non-floating source (ACM/ACM200/FXVIe_PLUS): `Source High ─[Connect Relay]─ Pin ─ DUT ─ AGND ─ Source Low`. Floating source (FPVI): `Source High ─[BUS Relay]─ PinA ─ DUT ─ PinB ─[BUS Relay]─ Source Low`.
- **BUS decision table:** `iset[AxB,I]` → BUS required; `vset[AxB,V]` → practice always uses BUS; `vset[A,V]`/`iset[A,I]` → no BUS.
- **Cap2 (FR-001):** Cap default closed for any pin that is powered. Remove **per PIN** only when ① that pin's current is measured (MIRET / capi current capture), or ② that pin is a ramp/scan source. **No function-level MI exemption** ("function has MIRET → whole function no Cap" is an anti-pattern that caused 10-function leakage). Reverse check E: PIN statically FV-supplied but its Cap not closed → WARN (per-PIN exemptions only; testpad bias AMUX/VDM/NTC excluded). DALI Cap family: `K13_VBAT_Cap` / `K21_VAC_Cap` / `K0_VCC_Cap` / `K5_VBUS_Cap`.
- **Register config iron law (R034/H011):** any re-power → must call `entertestmode()` before `I2CWriteSameData` (key-protected test registers).
- **Toggle/AWG:** two-stage ramp → exactly 3 params `<DFT参数基名>_Rise/_Fall/_Hys` (base = DFT param name, not literal `Param_` prefix), `Hys = Rise − Fall`; rising ramp → `TRIG_FALLING`, falling → `TRIG_RISING`; gate `verify_awg_params.py` (E005/H010).
- **Units (R-LOG / R-HYS / R-VIR):** MIRET A→uA `*1e6` / mA `*1e3`; MVRET V→mV `*1e3`; conversion at the `GetMeasResult` assignment (with comment), not at SetTestResult. Ramp Hys: voltage→mV, current→mA. Resistance = `MVRET/MIRET` (both measured, same MeasureVI), never theoretical set value.
- **Power-on two-stage (R-PON-09):** FV with measurement current <100uA: power pins → 100MA two-stage (`Set(FV,v,...,100MA,RELAY_ON)` → `delay_us(500)` → measurement small range); ATEST analog pins (VDM/NTC/AMON) → direct small range; digital pins (GPx/KLV/SNSP/SNSN) → 10MA two-stage. Scripted in `gen_power_sequence.py` (`pin_category()` + `gen_two_stage_power_on()`).
- **High current:** ≥200mA → FPVIe; BST ramps ahead of PMID (≈5V). Range ≥ 2× rule (e.g. 7V target > 10V档 table_max 5.0 → `ACM200_40V`).
- **Trim iron law (2026-08-10):** DFT `Trim='Y'` → unconditional trim framework: `TRIM_NODE &<KEY_UPPER> = trim_reg.trim("<key>")` (var = key upper, e.g. `osc_64k`→`OSC_64K`, never generic `PARAM_NODE`) + `<VAR>.execute(measure_xxx, spec, funcindex, funclabel, 1, 0, 0, 0)` + step0~N params + 8 fixed suffixes + sub.cpp tail ACTIVE measure function. Missing/erroneous material → **report to user**, never silently downgrade to default/plain measure (TM300/301 lesson).
- **Comment density:** every generated block carries hardware-intent comments (Step 1 relay targets, Step 2 source values/types/order, Step 3 field meanings from DFT `//field[...]`, Step 4 formula/range/current path, Step 5 power-down order reason, Step 6 var↔DFT param mapping).
- **Merge iron law MR-000:** each DFT item = one independent function, no merging.
- **Batch discipline B-001 (TM403-425 lesson):** ① smoke one representative function first (compile + `check_testitems_meta --require-all` + `verify_relay_trace --meta --warn-as-error` all green) then batch; ② replace placeholders **sorted by length descending** (`sorted(mapping, key=len, reverse=True)`) and assert no `__X__` residue (prefix collisions `__CONNECT_COMMENTS__`⊃`__CONNECT__`, `__RAMP_RANGE_COMMENT__`⊃`__RAMP_RANGE__`, `__RETCOMMENT__`⊃`__RET__`); ③ post-gen self-check: semicolon before trailing comment, brace balance, CRLF byte-clean (DLP `open('wb')`, never text mode).

---

## 2. Last completed batch — TM403-425 and TM216-402 (daylog/2026-08-10)

Both batches were completed 2026-08-10 and are documented in `daylog\2026-08-10.md`:
- **TM216-402 (9 fns):** TM216/217 PWM Current (MI), TM220/222 DMA/DMO R (R-VIR), TM300/301 OSC Trim (trim framework), TM400/401/402 VBUS OVP VTH (Toggle).
- **TM403-425 (15 fns):** 8 Toggle + 4 FB + 3 Trim, generated by `_archive\gen_insert_tm403_425.py` (4 templates TOGGLE/FB/TRIM/MEASURE + data dicts + `fill()` length-descending replacement), appended to test.cpp after TM402. Verification was all green: cbit V1~V8 PASS, `verify_relay_trace --meta --warn-as-error` PASS, `gen_dali_meta --require-all --require-scope 403-425` → 78/78 + 15/15 PASS, `fast_rebuild.ps1` → Release 0 errors/0 warnings.

### test.cpp location + how power_on/power_off scripts are called
- **Real file:** `D:\PROJECT6-DALI\devel\source\test.cpp` (DLP-encrypted). The function bodies were generated from the archived generator's templates; that generator is the faithful source for the skeleton below.
- **Power on/off:** in the current pipeline these are **not** function calls — `gen_power_sequence.py` emits the Step 2 `Set(FV,...)` block and Step 5 three-step power-down `Set(FV,0,...,RELAY_ON)`→`delay_ms(1)`→`Set(FV,0,...,RELAY_OFF)` block from the pin-map/meta. In the archived batch generator, the same Step2/Step5 statements were authored in the per-function data dicts (`supply_set` / `poff1` / `poff2`). The target output is identical.

### Representative template — Toggle (most complete; 8 of 15 in the batch)
This is the exact body that the archived generator inserted for TM403 (toggle 3-param AWG pattern):

```cpp
// =====================================================================
// TM403: VBUS_REVI_VTH — VBUS-VBAT 反向比较阈值 (Toggle, VBUS ramp)
// DFT: vset[vbat,4,100e-6,0] -> en_tm[] -> field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] -> 0x10=0x43, 0x56=0x1E, 0x57=0x08 -> VBUS 3.7->4.5->3.7 ramp, 捕 DTEST0 翻转
// 期望: falling -0.120V / rising 0V (r -0.016 / f -0.138)
// Loop: VBAT_PD3_FXVI + VBUS_DRVH1_ACM + NQON_HG1_ACM
// =====================================================================
DUT_API int TM403_VBUS_REVI_VTH(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_REVI_VTH_Rise = StsGetParam(funcindex, "VBUS_REVI_VTH_Rise");
    CParam *VBUS_REVI_VTH_Fall = StsGetParam(funcindex, "VBUS_REVI_VTH_Fall");
    CParam *VBUS_REVI_VTH_Hys = StsGetParam(funcindex, "VBUS_REVI_VTH_Hys");
    //}}AFX_STS_PARAM_PROTOTYPES

    double rise_result[SITE_NUM] = { 0 };
    double fall_result[SITE_NUM] = { 0 };
    double hys[SITE_NUM] = { 0 };

    // ====== Step 1: Connect (继电器闭合) ======
    // VBAT -> VBAT_PD3_FXVI: K8 default NC
    // VBUS -> VBUS_DRVH1_ACM: default NC (VBUS 为被测 ramp 源, 不闭 K5_VBUS_Cap)
    // nQON -> NQON_HG1_ACM:  K64 direct + K65_nQON_PU pull-up
    // K13_VBAT_Cap: VBAT 静态供电稳定 (FR-001: 供电→闭)
    cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1);
    delay_ms(3);

    // ====== Step 2: Power On (上电) ======
    // vset[vbat,4,100e-6,0] -> VBAT=4V FV
    VBAT_PD3_FXVI.Set(FV, 4, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);

    // ====== Step 3: Register Config (寄存器配置) ======
    // field[(WAKE_UP,1),(DMUX_EN,1),(DMUX_SEL,30)] -> 0x10=0x43, 0x56=0x1E, 0x57=0x08
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
    I2CWriteSameData(DEV_ADDR, 0x56, 0x1E);
    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);
    delay_ms(2);

    // ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======
    // nQON high-Z reads DTEST0 logic level; VBUS 3.7->4.5->3.7 ramp
    // VBUS 量程: 4.5V×2=9 <= 10V 档 table_max 5.0 -> ACM200_10V (R-RNG)
    double vth_r[SITE_NUM] = { 0 };
    double vth_f[SITE_NUM] = { 0 };
    // rising ramp: nQON falls through 1.65V (inverted) -> capture rise threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           3.7, 4.5, 200, 20, 1.65, TRIG_FALLING, vth_r);
    // falling ramp: nQON rises through 1.65V (inverted) -> capture fall threshold
    test_method.rampv_capv(VBUS_DRVH1_ACM, ACM200_10V, ACM200_100MA,
                           NQON_HG1_ACM, ACM200_10V, ACM200_10UA,
                           4.5, 3.7, 200, 20, 1.65, TRIG_RISING, vth_f);
    FOR_EACH_VALID_SITE(site)
    {
        rise_result[site] = vth_r[site];
        fall_result[site] = vth_f[site];
    }
    // Hys = Rise - Fall (Toggle 两段式, 3参数)
    FOR_EACH_VALID_SITE(site)
    {
        hys[site] = (rise_result[site] - fall_result[site]) * 1e3;  // V -> mV (R-HYS: Hys 电压→mV)
    }

    // ====== Step 5: Power Off (三步下电) ======
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
    delay_ms(1);
    VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    // ====== Step 6: LogData (测试结果) ======
    FOR_EACH_VALID_SITE(site)
    {
        VBUS_REVI_VTH_Rise->SetTestResult(site, 0, rise_result[site]);
        VBUS_REVI_VTH_Fall->SetTestResult(site, 0, fall_result[site]);
        VBUS_REVI_VTH_Hys->SetTestResult(site, 0, hys[site]);
    }
    return 0;
}
```

### Representative template — FB / MV (simplest; relevant to a `V(COMP)` MV item like TM614)
The FB template (`_archive\gen_insert_tm403_425.py` `FB_TPL` + TM418 data) — signature `DUT_API int TM418_VAC1_FB(short funcindex, LPCTSTR funclabel)`, AFX block `CParam *VAC1_FB = StsGetParam(funcindex, "VAC1_FB");`, Step1 `cbite.SetOn(K13_VBAT_Cap, K21_VAC_Cap, -1); delay_ms(3);`, Step2 two `Set(FV,...)` statements, Step3 `entertestmode();` then `I2CWriteSameData(DEV_ADDR,0x10,0x43); 0x11=0x11; 0x57=0x02; 0x5E=0x1F;`, Step4 measure `VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON); delay_ms(1); VDM_SDA_ACM.MeasureVI(50, 5); FOR_EACH_VALID_SITE(site){ vac1_fb[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET); }`, Step5 three-step power-off, Step6 `VAC1_FB->SetTestResult(site, 0, vac1_fb[site]);`.

### Trim pattern (3 of 15 in the batch)
`DUT_API int TM424_VREF_TRIM(...)` — AFX block has `step0..step31` + 8 suffixes (`pre_value/pre_bit/post_bit/updated/guessed/target/post_value/post_rt`), then `TRIM_NODE &MNT_DAC_BUF_OS = trim_reg.trim("mnt_dac_buf_os");`, Step1 `cbite.SetOn(K13_VBAT_Cap, -1);`, Step2 VBAT 4.4V FV, Step3 `entertestmode();` + reg writes, Step4 `VDM_SDA_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);` then `MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, 0);`. The measure function lives at the tail of `sub.cpp` (write EFUSE F7/F8 via `dcm.I2CWriteData(DEV_ADDR,0xF7,1,working_value)` → `VDM_SDA_ACM.MeasureVI(50,5)` → `GetMeasResult(MVRET)*1e3` mV).

---

## 3. The meta gate — `gen_testitems_meta.py` + `check_testitems_meta.py`

### Generator: `D:\Newtest\CLAUDE_PROCESS\gen_testitems_meta.py`
- Pure DFT-derived: reads `OVERVIEW` (Dali_testmode.xlsx), the test.cpp **function name list** (regex `DUT_API int (TM\d+(?:_\d+)?_\w+|Trim_\w+)`), and StdAfx.h Cap `#define Kxx_<PIN>_Cap` → writes `Project\DALI\meta\dali_tm_meta.json`.
- Derives the **capAuthority 4 sets** per function (what check E consumes):
  - `powered_pins` = vset ∪ Power column ∪ bare Dynamic pins (iset loads like VCC/VMCU are measurement targets, not supply rails)
  - `mi_pins` = Check/Dynamic `I(pin)` → per-PIN Cap exemption
  - `ramp_pins` = vset same-pin ≥2 values **only for toggle tests** (shipmode power-down sequence not counted) → Cap exemption
  - `testpad_pins` = AMUX/VDM/ATEST/DTEST0/NTC → no Cap check
- Run: `python gen_testitems_meta.py` (defaults from `project_config.json`; optional `--dump` preview / `--audit` 4-set table). **Run this after writing the test.cpp functions** so new functions get records.

### Checker: `D:\Newtest\CLAUDE_PROCESS\check_testitems_meta.py`
- Read-only verifier; any FAIL → exit 1; prints `CHECK-TESTITEMS-META PASSED` when green. Depends on the meta JSON already existing (gen first, check second).
- `--require-all` (**forward gate**): every test.cpp function must have a meta record; missing → ERROR (fix by adding the OVERVIEW row, then re-run gen); coverage = test.cpp function count, `<100%` → FAIL.
- `--require-scope <范围>` (**reverse gate**, blocks the "recorded in OVERVIEW but never written to test.cpp" hole that hit TM403-425): every OVERVIEW `isCodeGen='Y'` item in scope must have a `DUT_API` function in test.cpp; missing → FAIL listing TM number + Name. `parse_scope()` supports comma lists and `a-b` ranges, auto-strips `TM` prefix.
- Run: `python check_testitems_meta.py --require-all --require-scope 614-616`

For TM614/615/616, the OVERVIEW already has `isCodeGen='Y'` for all three (TM614 VC_CLAMP_LOW Check=V(COMP), TM615 PSM_THREHOLD Check=V(DTEST0), TM616 VC_OFFSET Check=I(ATEST0)), so the reverse gate will be satisfiable once the three functions exist in test.cpp.

---

## 4. Scripts to run after writing — order to gate completion

Pipeline **inputs** (all defaults resolve from `project_config.json`): dft xlsx = `Project\DALI\Dali_testmode.xlsx`, vs_src_dir = `D:\PROJECT6-DALI\devel\source`, meta = `Project\DALI\meta\dali_tm_meta.json`, cbit = `Project\DALI\CBIT表-DALI.xlsx`, sch_connect_map = `Project\DALI\SCH-Connect-Map.txt`.

**During generation (per function):**
1. Before generating each function: material gate — `python verify_material_receipt.py --receipt <receipt.json> --tm <TMxxx>` (FAIL blocks generation).
2. Immediately after assembling each function: `python verify_single_fn.py --src D:\PROJECT6-DALI\devel\source\test.cpp --fn TMxxx` — **must PASS before moving to the next function** (B-001).

**After the whole batch is written (final gate sequence):**
1. `python gen_testitems_meta.py` — regenerate meta JSON so the new functions get records (gen before check).
2. `python check_testitems_meta.py --require-all --require-scope 614-616` — meta forward + reverse coverage gate.
3. `python verify_relay_trace.py --meta Project\DALI\meta\dali_tm_meta.json --warn-as-error` — relay structural rule (Step 1 must have `cbite.SetOn(...)`/`SetOn(-1)`), name authenticity vs StdAfx.h defines + SCH-Connect-Map, functional rules (Cap/PU/P2P), FR-001 reverse Cap check (meta-authoritative).
4. `python gen_cbit_defines.py --cbit Project\DALI\CBIT表-DALI.xlsx --stat Project\DALI\COMPONENT-STATISTIC.txt --verify D:\PROJECT6-DALI\devel\source\StdAfx.h` — V1~V8 relay-definition check (daylog ran it as `gen_cbit_defines.py --verify StdAfx.h`).
5. `python verify_awg_params.py --src D:\PROJECT6-DALI\devel\source\test.cpp` — Toggle/AWG 3-param gate (E005; skill marks it "必跑" for the batch).
6. `.\fast_rebuild.ps1 D:\PROJECT6-DALI\devel\source` (or add `-Incremental` for a faster incremental Build) — **Release 0 errors / 0 warnings** is the final compile gate.

The skill's stated order for the close-out is explicit: "写完代码 → `python check_testitems_meta.py --require-all --require-scope <本批范围>` → 再 `verify_relay_trace.py --meta <新meta> --warn-as-error`". The 2026-08-10 TM403-425 validation ran the same set in the order: cbit `--verify` → `verify_relay_trace --meta --warn-as-error` → meta `--require-all --require-scope` → `fast_rebuild.ps1`, all green.

**B-001 recommendation for a new batch (TM614-616):** insert **one** representative function first, run smoke + `check_testitems_meta --require-all` + `verify_relay_trace --meta --warn-as-error` + a quick build until green, then generate the remaining two. After each DLP file edit, keep CRLF clean (`\r\n`, byte mode, no `\r\r`) and assert no `__X__` placeholder residue.
