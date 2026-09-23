# Implementer reconnaissance — acceptance-20260916-dali10 (t5 pre-work)

Author: ate-implementer. Status: **read-only reconnaissance only**. No file under
`D:/PROJECT6-DALI/ForCodexDebug` was created, modified or deleted; no build was run.
t5 remains **blocked by t4** (`test-plan.json` absent). This note exists so implementation
can start the moment t4 lands, and so downstream gate task t8 can plan for a scoping risk
(§5) that the DFT intent alone does not reveal.

## 1. Toolchain facts (verified, not assumed)

| Fact | Evidence |
| --- | --- |
| `ForCodexDebug/source/test.cpp` and `devel/source/test.cpp` are **byte-identical** (sha256 `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`, 434629 B) | python `sha256` of both paths |
| `test.cpp` is **DLP-transparent-encrypted**; only whitelisted processes see plaintext. PowerShell `Get-Content` with cp936 yields 2198 garbage lines; `python` `open('rb')` yields **8878 lines**, `\xef\xbb\xbf` BOM present, 8874 CRLF | raw byte comparison of both readers |
| Canonical reader/writer = python byte mode, UTF-8 BOM + CRLF preserved; never text mode (corrupts CRLF to `\r\r\n`) | `scripts/gen_path_defines.py`, `scripts/gen_relay_role_defines.py` `read_enc`/`write_enc`; `scripts/verify_single_fn.py` check 4 `crlf_clean` |
| python present at `C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`, reads DLP plaintext | verified live |
| Test Item meta registry `project/DALI/meta/dali_tm_meta.json` holds **99** functions; `test.cpp` has **116** `DUT_API` functions | json load + regex count |

## 2. TM600 / TM601 baseline confirmation

Neither symbol exists in `test.cpp`: zero matches for `TM600`, `TM601`, `RDSON`, `RDS`
anywhere in the 8878-line plaintext. `DUT_API` list ends at `TM1205_TRX_BST_UV_GD`
(line 8766); the highest numeric TMs present are `TM1004`–`TM1100` then `TM1205`.
This confirms `acceptance-plan.json` `baseline: "missing-from-debug-test.cpp"` for both.

## 3. Authoritative DFT intent (source for the t4 plan)

`project/DALI/input/DFT.csv` rows 18/19, decoded via python (utf-8-sig):

**TM600 `RDSON_TEST` / `HS_RDSON`, expect 10 mohm, type `MV&MI`, Check `PMID-SW`**

- Hardware_initial: `vset[vbat,4.2,100e-6,0] vset[pmid,15,100e-6,0] vset[bst2sw,5,1e-3,0] vset[vdrv,5,100e-6,0]`
- Software_initial: `entertestmode(); 0x58=0x00; 0x10=0x43; 0x59=0x01; 0x61=0x0B;`
  fields `[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]`
- Dynamic: `iset[pmid2sw,1,1e-3,0]` → force 1 A through PMID→SW (high-side pass element ON)

**TM601 `LS_RDSON`, expect 8 mohm, type `MV&MI`, Check `PGND-SW`**

- Hardware_initial: `vset[vbat,4.2,100e-6,0] vset[pmid,9,100e-6,0] vset[vdrv,5,100e-6,0]`
- Software_initial: `entertestmode(); 0x10=0x43; 0x58=0x20; 0x59=0x02; 0x61=0x0B;`
  fields `[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]`
- Dynamic: `iset[sw2pgnd,1,1e-6,0]` → force current through SW→PGND (low-side ON)

Both are `MV&MI`: the result is RDSON = measured differential V / forced I, so each needs a
force path **and** a simultaneous Kelvin differential voltage read.

## 4. Closest golden cases located (candidate reuse set for t4 to select from)

| Golden | Lines | Why it matters to TM600/TM601 |
| --- | --- | --- |
| `TM640_BOOST_HS_OCP` | 7503–7590 | Same BUBO/PMID→SW loop, `D2A_BUBO_TM_HSON`, `0x61=0x4B`, relay set `K_FPVIH_TO_PMID_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K65_nQON_PU`. Closest match to TM600 force path. |
| `TM641_BST_UV` | 7606–7717 | BST-SW differential maintenance, documents that `K48/K76` are shared between `SW12_U1REF_BST_ACM` and the FPVI High-to-BST route → one source must stay `RELAY_OFF`. Directly constrains TM600 (`bst2sw=5V` on the BST/SW pair). |
| `TM1205_TRX_BST_UV_GD` | 8766–8877 | Newest implementation; canonical 6-step skeleton, FPVI0 floating differential pair `High→SW (K46/K49) / Low→BST (K41/K43)`, `FPVIe_10V/100MA`, serial re-route via second `cbite.SetOn`. |
| `TM702_IBUS_SNS_GAIN_TRIM` / `TM703` | 8128–8356 | `FPVI0.Set(FI, ±1.0/3.0, FPVIe_1V, FPVIe_2A, …)` force-current probe, `mohm` arithmetic target 198, VCS = `V(VDM)-V(AMUX)` differential-sense idiom. Closest match to the `MV&MI` RDSON math. |

Confirmed canonical 6-step skeleton (identical across TM640/TM641/TM1205):
`AFX_STS_PARAM_PROTOTYPES` `StsGetParam` block → `SITE_NUM` result arrays → Step 1 `cbite.SetOn(...)` + `delay_ms(3)` → Step 2 power-on with explicit compliance/limit per source → Step 3 `entertestmode()` + `I2CWriteSameData(DEV_ADDR, reg, val)` with per-write `delay_us/ms` → Step 4 measure → Step 5 reverse-order power-down with `RELAY_OFF` → Step 6 `FOR_EACH_VALID_SITE(site)` `SetTestResult`.

Naming precedent: `acceptance-plan.json` `symbolHint` (`RDSON_TEST_HS` / `RDSON_TEST_LS`)
differs from every other TM whose symbol is `TMxxx_<SHORTNAME>`. **t4 must fix the exact
symbol names** — this is a real decision, not a detail.

## 5. Scoping risk for downstream gates (t8) — found during reconnaissance

`project/DALI/meta/dali_tm_meta.json` is the Test Item meta registry consumed by
`scripts/check_testitems_meta.py` (with `--require-all`, `--require-scope`) and
`scripts/verify_relay_trace.py --meta`. It currently contains **99** functions and
**has no TM600/TM601 entry**. Its declared source is the OVERVIEW/DFT intent table and it is
(re)generated by `scripts/gen_testitems_meta.py`.

Consequence: emitting the two `DUT_API` functions alone may satisfy compilation while leaving
the meta-coverage gate incomplete. I have **not** yet verified which of these is true:

1. `gen_testitems_meta.py` regenerates TM600/TM601 from `DFT.csv` (rows 18/19 exist) and the
   gate then passes after a regeneration step; or
2. the meta registry is a hand-maintained source, in which case a data change outside
   `test.cpp` is required and the run must decide whether that path is in scope.

UNKNOWN, to be resolved before t8 runs. `devel` is read-only, so any regeneration must target
the debug copy only.

## 6. Ready state

Blocked on t4 for: exact symbol names, per-TM parameter names/types, selected golden case per
TM, force/measure source assignment, and settle/compliance values. Everything else needed to
write the two functions is captured above.

---

# ADDENDUM (after Captain's adjudication A–E)

## 7. RESOLVED from Captain: decisions A, B, C, E

- **A (symbols)** — Captain ruled the hard rule is `scripts/gen_testitems_meta.py:91`
  `re.match(r'DUT_API int ((?:TM\d+(?:_\d+)?_\w+|Trim_\w+))\(short funcindex', line)`, so both
  functions must be `DUT_API int TM600_*(short funcindex, LPCTSTR funclabel)`. I verified that
  regex and the wiring at lines 94–97 and 359–360 (`name = fns[item]`, `row = ov.get('TM'+item)`).
  **t4's signed value is the single authority.**
- **B (meta coverage)** — In t5 inScope; `gen_testitems_meta.py` derives names from test.cpp and
  intent from OVERVIEW, so regenerating after the functions land is expected to satisfy
  `check_testitems_meta.py --require-all`. Run the generator **with python only** (TSZ-authorized).
- **C (hash iron rule)** — **Correction to my §1 table**: hashes for every DLP file in this run
  MUST be produced by python and labelled `plaintext`. PowerShell `Get-FileHash`/`.NET` read
  ciphertext on the same byte length and give a *different* digest, which would falsely report a
  file as modified. My earlier `sha256 5c9cb3f9…` was produced with python, so it is the valid
  plaintext digest; any future before/after comparison must use the same method.
- **E (fact re-verification)** — Captain independently reproduced my test.cpp byte-identity and
  DFT.csv facts; all TRUE. Golden path corrected to `knowledge/references/L4-Golden-code/`.

## 8. NEW BLOCKING EVIDENCE — the golden TM600/TM601 sources are a different API generation

Found `knowledge/references/L4-Golden-code/Rdson.cpp` (139 lines, `TM600_RDSON_TEST`) and
`tm600-normal-highcurrent.cpp` (same content), documented as "TM600 唯一正确版". They are **not
paste-ready for this tree**: the names they are built on do not exist in the current source.

Verified by direct lookup in the live debug copy (python plaintext read of `StdAfx.h` + `test.cpp`):

| Golden uses | Present in current tree? | Current equivalent |
| --- | --- | --- |
| `K31_VBUSL_PMID` (FPVI High→PMID) | **No** (0 hits) | `K_FPVIH_TO_PMID_A` / `K83_BUSH0_PMID` |
| `K17_BUSH_SW` (FPVI Low→SW) | **No** | `K60_BUSL0_VCP` + `K61_ACM8_SW` |
| `K30_VBAT_Cap`, `K28_VDRV_Cap`, `K32_PMID_Cap` | **No** | `K13_VBAT_Cap`, `K57_CAP_BST_SW` |
| `K18_BST_SW_Cap` | **No** | no exact match (re-check) |
| `BTST_ACM`, `PMID_FOVI`, `VBAT_ACM`, `VDRV_AMP_ACM` | **No** | `SW12_U1REF_BST_ACM`, `PMID_HG2_FXVI`, `VBAT_PD3_FXVI`, `V1P5_U34PS_FXVI` |
| `FOVIe_40V/100MA/RELAY_ON/10V/10MA`, `FPVI_RELAY_ON/OFF` | **No** (0 hits) | `FXVIe_PLUS_*`, `FPVIe_*` |
| `FPVI.SetClamp(50, 50)` | **No** — `SetClamp` absent from test.cpp *and* StdAfx.h | none found; compliance is expressed through the range/enum argument of `.Set(...)`. **UNRESOLVED how the 0.5 V compliance is commanded in this generation** |
| `FPVI.MeasureVI(200, 5)`, `GetMeasResult(site, MVRET/MIRET)`, `MVRET`, `MIRET` | **Yes** — `MeasureVI(50,5)` used at 55 call sites | usable as-is |

All five archived drafts under `_archive/` (`TM600_output.cpp`, `TM600_fixed.cpp`,
`TM600_HS_RDSON.cpp`, `TM600_TM601_combined.cpp`, `TM601_LS_RDSON.cpp`) carry the same legacy
set (`SetClamp`, `K31_VBUSL_PMID`, `K17_BUSH_SW`, `PMID_FOVI`, `BTST_ACM`, `FOVIe_*`,
`FPVI_RELAY_ON`). **No archived or golden TM600/TM601 file can be copied and compiled.** A port is
required, and the port is where implementation risk actually lives.

Practical consequence: the reuse set must be re-based on current-generation goldens — `TM640`
(PMID↔SW force loop, `K83`/`K60`+`K61`), `TM641` (BST-SW differential, K48/K76 sharing),
`TM702_1` (force-current then `MeasureVI(50,5)` + `GetMeasResult` mV/mA arithmetic — the closest
match to `MV&MI` RDSON), `TM1205` (newest skeleton) — rather than on the RDSON golden files.

## 9. Open questions for t4 / Captain (not decidable by the implementer)

1. **Compliance**: the RDSON method (`L5-debug/RDSON.md`) requires the PMU not to enter Clamp and
   the golden sets a 0.5 V compliance for a 500 mΩ ceiling. With `SetClamp` gone, what is the
   sanctioned way to bound the force voltage in this generation? Without it the 1 A force on a
   10 mΩ DUT is fine, but the measurement ceiling is unbounded.
2. **Measurement topology conflict**: `DFT.csv` for TM600/TM601 says `iset[pmid2sw,1,1e-3,0]` /
   `iset[sw2pgnd,1,1e-6,0]` with `Check = PMID-SW` / `PGND-SW` (force current, differential
   Kelvin sense). The golden instead computes RDSON from the FPVI's **own** `MVRET/MIRET`. These
   are different topologies; t4 must pick one and say so.
3. **Limit conflict (Captain item D)** — OVERVIEW 11/7.5 mΩ vs DFT.csv 10/8 mohm. Not to be
   silently resolved or averaged. If t4 still marks it blocking, t5 stops and reports.
4. **Naming note for t4**: every existing symbol is `TM<Item>_<ShortName>` (`TM607_BUCK_LS_ZCD`,
   `TM614_VC_CLAMP_LOW`). Applying that to Item 600/601 and ShortName HS_RDSON/LS_RDSON gives
   `TM600_HS_RDSON` / `TM601_LS_RDSON`, matching the Captain's recommendation. The archived cohort
   instead used `..._TEST` suffixes (`TM600_RDSON_TEST`, `TM600_HS_RDSON_TEST`,
   `TM601_LS_RDSON_TEST`); both forms satisfy the generator regex, so only the signed t4 value
   decides.

---

# ADDENDUM 2 — corrections to §8 and the resolved API facts

## 10. RETRACTION — my §8 "SetClamp absent / no clamp API" claim was WRONG

I limited the search to project source (`test.cpp`, `StdAfx.h`, `sub.cpp`, `Test_Method.*`) and
wrote the conclusion as if it applied to the library. It does not. The tester SDK is at
`C:\AccoTEST\AccoTEST System\INCLude` (from `F12011.vcxproj` `AdditionalIncludeDirectories`), and
`SetClamp` is a real instrument method:

- `FPVIe.h:101` — `int SetClamp(double percent_PFS, double percent_NFS);` (also `Set` :86, `MeasureVI` :104, `GetMeasResult` :114)
- `FXVIe.h:117` and `:458` — `SetClamp` for `FXVIe` and `FXVIe_PLUS`
- `ACM200.h`, `FOVIe.h` — `SetClamp` present
- `SetClamp` is simply **unused by this project's own code** (0 hits in test.cpp / sub.cpp / Test_Method.cpp), but it is fully callable.

So the golden's `FPVI.SetClamp(50, 50)` is **valid in this generation** and is on the direct
golden path. Do not design around a missing clamp API. (Note: it is still the project's choice
whether to adopt it, or to express compliance through the range enum as the Captain described —
but that is now a style decision, not a capability limit.)

## 11. Range enums live in the SDK, not the project — correct current inventory

`FXVIe_PLUS`, `FPVIe`, `ACM200`, `FOVIe` are SDK **types**; their range enums are declared in the
SDK headers, which is why a project-source-only search finds zero `#define`s.

`FPVIe.h` (`FPVIe_IRNG` :17) = `10A, 2A, 1A, 100MA, 10MA, 1MA, 100UA, 10UA`
`FPVIe.h` (`FPVIe_VRNG` :6) = `100V, 40V, 20V, 10V, 5V, 2V, 1V, 100MV`
`FXVIe.h` (`FXVIe_PLUS_IRNG` :348) = `1A, 100MA, 10MA, 1MA, 100UA, 10UA, 1UA`
`FXVIe.h` (`FXVIe_PLUS_VRNG` :339) = `40V, 30V, 20V, 10V, 3p6V`

**Material constraint (corrects the Captain's assumption):** there is **no `FXVIe_PLUS_10A` and no
`FXVIe_10A`**. `FXVIe_PLUS` tops out at **1 A**, exactly at the required force with zero margin,
and `FXVIe` at 1 A. Only `FPVIe` reaches 10 A / 2 A. Therefore the 1 A force for TM600/TM601
(`iset[pmid2sw,1,...]`) can only be carried by an `FPVIe` (e.g. `FPVI0`), as the golden itself
does — not by an `FXVIe_PLUS`. The Captain's warning against copying `FXVIe_PLUS_10MA` stands and
is stronger than stated: the correct family is `FPVIe` with `FPVIe_IRNG` ≥ `FPVIe_2A`/`FPVIe_1A`.

## 12. Differential Kelvin sense for the DFT topology (Captain ruling #2) IS available

`UserRes.h:361` `int USERRES_API FXVIe_PLUSDiffMeasure(FXVIe_PLUS* baseFXVIe_PLUS,
FXVIe_PLUS* measFXVIe_PLUS, UINT sampleTimes, double samplePeriod, FXVIe_PLUS_DIFF_VRNG vRange);`
with `FXVIe_PLUSDiffGetMeasResult` (:367) and `FXVIe_PLUS_DIFF_VRNG` = `DIFF_10V, DIFF_3p6V`
(`FXVIe.h:423`). Also `FXVIeDiffMeasure` / `FXVIeDiffGetMeasResult` (:353) exist for `FXVIe`.

Caveat: **0 usages of any Diff* API in the project's own source** (nothing in test.cpp, sub.cpp,
Test_Method.*). Current TMs implement differential sense instead as two single-ended reads and a
subtraction — `vcs = VDM_SDA_ACM.GetMeasResult(site,MVRET) - VAC123_AMUX_ACM.GetMeasResult(site,MVRET)`
(TM702_1, test.cpp:8070/8080). Both are viable for `Check = PMID-SW` / `PGND-SW`; the subtraction
form has precedent and the Diff* form is unused. t4 should pick one; I will not pick silently.

## 13. Accepted refinement from the Captain (precision on §8 wording)

`FOVIe_*` and `VBAT_ACM` are **not** absent library-wide — they live in the **method-library
layer**. Per-file counts I reproduced independently: `FOVIe_` → sub.cpp 21, Test_Method.cpp 187,
Test_Method.h 75; `VBAT_ACM` → sub.cpp 5; `SetClamp` → 0 in all project files; `BTST_ACM` /
`PMID_FOVI` / `K31_VBUSL_PMID` / `FPVI_RELAY_ON` → 0 in all project files. So §8's operative
conclusion (the goldens cannot be pasted into TM-level `test.cpp`) holds, but the phrase "does not
exist in the library" must not be used — it would wrongly suggest those library helpers are
unavailable.

## 14. Net effect on t5 planning

- Risk is still concentrated in the port (§8), because every golden/archive draft references
  TM-level names that are absent from `test.cpp`/`StdAfx.h`.
- But the port is **mechanically feasible on current-generation API**: `FPVIe` 2 A range + `Set`,
  `SetClamp`, `MeasureVI(50,5)`, `GetMeasResult(site, MVRET/MIRET)`, and optionally
  `FXVIe_PLUSDiffMeasure` are all available.
- Still open and NOT to be decided by me: t4's signed symbol names; Captain item D limits; and the
  single-ended-subtraction vs Diff* choice for the Kelvin sense.
- Resolution limit remains a real engineering concern: 1 A × 10 mΩ ≈ 10 mV inside a 1 V `FPVIe_VRNG`
  step. The golden's mitigation was `SetClamp` + short 2 ms pulse; t4 should state the intended
  measurement range and pulse width.

---

# ADDENDUM 3 — t1 dft-ir.json consumed; my §3 register block is SUPERSEDED

dft-expert (t1) delivered `team/artifacts/acceptance-20260916-dali10/dft-ir.json` and warned that
my §3 register values came from `DFT.csv`. **That warning is correct, and it invalidates §3's
register block.** I verified the claim independently against the shipped code rather than accepting it.

## 15. §3 RETRACTION — the DFT.csv register map is the older map

I wrote in §3: TM600 `0x58=0x00; 0x10=0x43; 0x59=0x01; 0x61=0x0B` and TM601 `0x10=0x43; 0x58=0x20;
0x59=0x02; 0x61=0x0B`, taken verbatim from DFT.csv rows 18/19. Those values must NOT be implemented.
They are superseded by `reg_config/tm600.sv` / `tm601.sv` (the compiled AMS sequences for exactly
these two test items), which give `0x10=0x43; 0x59=0x20; 0x5A=0x02|0x01; 0x61=0x4B`.

**Independent confirmation from shipped code (not from dft-expert's IR).** I enumerated every
`0x5A` write in the live `test.cpp` and grouped it by owning function:

| Function | write | shipped comment |
| --- | --- | --- |
| `TM607_BUCK_LS_ZCD` (7018) | `0x5A=0x01` | `D2A_BUBO_TM_LSON=1 (下管 LS FET 导通)` |
| `TM608_BOOST_HS_ZCD` (7109) | `0x5A=0x02` | `D2A_BUBO_TM_HSON=1 (上管 HS FET 导通)` |
| `TM609_BOOST_HS_NEG` (7202) | `0x5A=0x02` | `D2A_BUBO_TM_HSON=1` |
| `TM640_BOOST_HS_OCP` (7534) | `0x5A=0x02` | `D2A_BUBO_TM_HSON=1, ...LOW_ILIMT_OFF=1` |
| `TM640_BOOST_HS_OCP` (7541) | `0x5A=0x06` | adds `D2A_BUBO_TM_BOOST_OCP_EN=1` |

So in the shipped generation **LS = `0x01`, HS = `0x02` in register 0x5A**, and `0x5A` is the register
that carries the HSON/LSON bit — exactly the `.sv` direction. DFT.csv puts the FET-select bits in
`0x59`/`0x58` and inverts the semantic (its TM601 row writes HSON for the low-side test). The
canonical BUBO cluster in shipped code is `0x59=0x20` + `0x61=0x4B` + `0x5A=0x01|0x02`, which is what
`tm600.sv`/`tm601.sv` emit. Confirmed consequence: TM600 must write `0x5A=0x02` (HS) and TM601
`0x5A=0x01` (LS); writing the DFT.csv pair would enable the **opposite** FET.

Caveat I am NOT able to resolve: whether DFT.csv is simply stale, or is describing a different
silicon revision. That is conflict C-03 / BD-03 and belongs to t4.

## 16. Additional verified deltas between DFT.csv and the .sv files (feeding C-01/C-03/C-05)

| Item | `.sv` (per-TM compiled sequence) | `DFT.csv` | Note |
| --- | --- | --- | --- |
| TM600 supplies | vbat 3.5, pmid 5, bst_sw 5, vdrv 5 | vbat 4.2, pmid 15, bst2sw 5, vdrv 5 | all four differ |
| TM601 supplies | vbat 3.5, vdrv 5, vbus 5 | vbat 4.2, pmid 9, vdrv 5 | `.sv` powers VBUS, CSV powers PMID |
| TM600 force | `iset[sw,1,1e-3]` | `iset[pmid2sw,1,1e-3]` | same 1 A, different node names |
| TM601 force | `iset[pmid_sw,1,1e-3]` | `iset[sw2pgnd,1,1e-6]` | 1 A vs 1 µA **and** different node |
| TM600 delay | 1e-3 then 2e-3 | (none) | |
| TM601 delay | 5e-3 then 2e-3 | (none) | |

**Engineering red flag worth escalating, not silently resolving:** the DFT.csv TM601 force is
`iset[sw2pgnd,1,1e-6,0]`. Read literally, `1e-6` is 1 µA, which is physically useless for an 8 mΩ
measurement (8 mΩ × 1 µA = 8 nV, far below any ATE resolution). Either it is a typo for a 1 µs ramp
time (the field is the ramp-time slot in every other row: `iset[sw,-2,1e-3,0]`, `iset[pmid,1/3]`,
`iset[sw,2,1e-3,0]`), or it is a 1 µA force. The `.sv` says 1 A. This should be resolved with the
same ruling as C-01/C-03 rather than guessed.

Separately, TM601's `.sv` forces between **PMID and SW** while its quoted check is **SW-PGND**. Those
cannot both be the measurement: forcing current into PMID↔SW does not push 1 A through the low-side
FET (SW↔PGND). dft-expert's item also flags this for t2. It is my single biggest correctness risk for
TM601 and I will not code around it — it needs the t2/t3 answer to BD-02.

## 17. dft-ir.json integrity note (hash mismatch — for the ledger)

The t1 handoff quoted `sha256 478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755`.
The file on disk does **not** match: live python plaintext sha256 is
`85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e` (99058 B, mtime 2026-09-16
13:52:00, created 13:48:01). `revisions[0]` explains it: dft-expert revised the artifact at
13:52:00 "t1 close-out, captain follow-up requirements" (added `limitConflictPairs`,
`pendingUserAdjudication` PA-01/PA-02, plaintext anchors, `captainRulings` CR-01, `mvMiRequirement`).
So the quoted digest is stale, not the file corrupt — every substantive claim in the handoff checks
out against the current revision. Downstream consumers should re-hash rather than trust the quoted value.

## 18. Inputs now pinned for t5

- **Symbols (resolved, CR-01 applied in dft-ir.json):** `TM600_HS_RDSON`, `TM601_LS_RDSON`.
- **Limits:** cite `dft-ir.json` `limitConflictPairs` / PA-01 / PA-02 — both values verbatim, no fold.
  TM600 11 mΩ (OVERVIEW!row 132) vs 10 mohm (DFT.csv rec 19); TM601 7.5 mΩ (OVERVIEW!row 133) vs
  8 mohm (DFT.csv rec 20). I will put the **pair** in the manifest, not a single number.
- **Register map:** `.sv` is the working default per dft-expert guidance, pending BD-03.
- **Still BLOCKING for me:** BD-01 (limits), BD-02 (force/sense pins — specifically the TM601
  PMID-SW vs SW-PGND contradiction), BD-03 (register map confirmation), BD-05 (1 A compliance/clamp).
  BD-05 now has a concrete candidate: the golden's `SetClamp(50,50)` on a 1 V range = 0.5 V,
  and `SetClamp` is confirmed available (§10).
- **Meta registry:** TM600/TM601 absent from `dali_tm_meta.json` — matches dft-expert's independent
  check; regeneration question recorded in `dft-ir.json` openQuestions.

---

# ADDENDUM 4 — evidence-method discipline (adopted) + force/measure precedent verified

Captain relayed a取证方法纪律 discovered by test-strategy-architect. I reproduced every claim
myself and adopt the rules for the whole of t5.

## 19. Reproduced: PowerShell is blind to the protected source

Same file (`ForCodexDebug/source/test.cpp`), same strings, two readers:

| Probe | pwsh | python plaintext |
| --- | --- | --- |
| `TM607_BUCK_LS_ZCD` | `Select-String` → **0** | `str.count` → **1** |
| `DUT_API int TM607` | `Select-String` → **0** | `str.count` → **1** |
| line count | `Get-Content` → **3316** | `split('\n')` → **8878** |
| file size | 434629 B | 434629 B |

CONFIRMED. My own first attempt at this file (§1) hit exactly this trap and I flagged it then; this
makes it a hard rule rather than a personal workaround.

**Rules I will follow for all of t5, and that my manifest will attest:**
1. ❌ No existence/absence assertion about `test.cpp` / `sub.cpp` / `StdAfx.h` may rest on pwsh
   `Select-String` / `Get-Content` — a pwsh 0-hit does **not** prove absence.
2. ✅ Existence and content assertions: use the **grep tool** or **python** (DLP-whitelisted).
3. ✅ Hash anchors: **python plaintext sha256 only**, each labelled `plaintext`. `Get-FileHash` is a
   ciphertext hash on the same byte length and will falsely report "file modified".
4. ⚠️ Every existence/absence statement must name its **limiting scope and tool** (e.g. "absent from
   TM-level `test.cpp` by python read" ≠ "absent library-wide").
5. Gates/compilation are unaffected: `run_gates.ps1` is a pwsh wrapper around python, and `cl.exe`
   is DLP-authorized (the baseline could not be 0-error otherwise).

Per-item tool attribution now required in the manifest; §8's `0 hits` claims were all python-based
and remain valid, and §13 already carries the scope caveat this rule demands.

## 20. Verified: the range enums and the 1 A selection

Captain's cited enums confirmed present in project headers: `BoardCheck.h` contains `FOVIe_1A`,
`FXVIe_PLUS_1A`, `FPVIe_1A`, `FPVIe_10A` (1 each); `BoardCheck.cpp` references `FPVIe_1A` 14×.
Ground truth from the SDK declarations (`C:\AccoTEST\AccoTEST System\INCLude`) — these are the
authoritative enum bodies, not usage counts:

- `FOVIe.h` `FOVIe_IRNG` = `1A, 100MA, 10MA, 1MA, 100UA, 10UA` (max 1 A)
- `FXVIe.h` `FXVIe_PLUS_IRNG` = `1A, 100MA, 10MA, 1MA, 100UA, 10UA, 1UA` (max 1 A)
- `FPVIe.h` `FPVIe_IRNG` = `10A, 2A, 1A, 100MA, 10MA, 1MA, 100UA, 10UA` (max 10 A)

So `FPVIe_1A` does satisfy ≥1 A, and my earlier point (§11) stands unchanged: `FXVIe_PLUS` tops out
at exactly 1 A with zero margin, so the 1 A force is safest on an `FPVIe`
(`FPVIe_2A`/`FPVIe_10A`) as the live precedent below actually does.

## 21. Verified: `sub.cpp` force-current precedents are mostly commented

`sub.cpp` (3336 plaintext lines) holds **105** `Set(FI, ...)` lines — **91 commented out, 14 live**.
Live ones are all in the trim-measure helpers, e.g. `FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A,
FPVIe_RELAY_ON)` (3258) and `3.0 / FPVIe_10A` (3270), and `2.0 / FPVIe_10A` (3320). Also:
**zero occurrences of `PMID2SW` / `pmid2sw` / `PMID_SW` / `pmid_sw` / `PMID-SW` in `sub.cpp`**
by python under those five spellings — so these precedents are generic force-current shapes, NOT a
TM600/TM601 PMID↔SW path I can lean on. Captain's warning not to code from them before t4 is well
founded.

## 22. What the live precedent is actually good for (the `MV&MI` RDSON shape)

The live `sub.cpp` pattern and TM702_1 agree on one idiom, and it is the right one for a milliohm
measurement:

```
FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);   // force
delay_ms(2);                                              // settle
VDM_SDA_ACM.MeasureVI(50, 5);                             // sense A
VAC123_AMUX_ACM.MeasureVI(50, 5);                         // sense B
FPVI0.MeasureVI(50, 5);                                   // actual force
Vsense = GetMeasResult(site, MVRET)_A - GetMeasResult(site, MVRET)_B;   // differential
Imeas  = fabs(GetMeasResult(site, MIRET));                              // measured, not set
results = fabs(Vsense2 - Vsense1) / fabs(Imeas2 - Imeas1) * 1e3;        // mohm
```

Three things this settles for t5:
- Differential sense is done as **two single-ended reads + subtraction**, which has project
  precedent (`sub.cpp` 3265/3277, TM702_1 test.cpp:8070/8080). The `FXVIe_PLUSDiffMeasure` API
  (§12) exists but has zero precedent. This is the precedent-backed option for the captain's #2
  topology ruling, and it is what I will propose to t4 rather than decide alone.
- RON is computed from **measured** V and I (`MIRET`), never from the programmed value — this is the
  project's R-VIR rule and it agrees with `L5-debug/RDSON.md` item 2.
- Zeros are driven to `0` via a `.Set(FI, 0, ...)` teardown, matching Step 5 discipline.

Note the precedent pair used for the differential sense is `VDM`−`AMUX`, not the DFT's `PMID-SW` /
`PGND-SW` pair. Transferring the idiom therefore still depends on the t2/t3 answer to BD-02 — the
shape is reusable, the node pair is not yet authoritative.
