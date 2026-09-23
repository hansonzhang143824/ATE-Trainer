# T1 — New-DFT input diff for TM600 / TM601 (independent verifier report)

Run: `tm601r3-20260916` · Task: t1-input-diff-new-dft
Mode: **read-only**. Exactly one file written: this report.
Date of measurement: session of 2026-09-16 (workbook mtime 2026-09-16 21:46:39).

---

## 0. Provenance and method (read this before using any number below)

All workbook reads used `openpyxl.load_workbook(..., data_only=True, read_only=True)` via Python byte-mode
access, and a second `data_only=False` pass to prove there are **no formula cells** in rows 132/133
(every non-empty cell reports `data_type` `s` = inline/shared string, or `n` = number for `E132`/`E133`).
A binary `.xlsx` is **not** a TSZ/DLP text artefact, so no plaintext-shim risk applies; the DLP filter does
however change the size reported through different access paths (see below).

| Artefact | Path | Measurement | SHA-256 (Python `read_bytes`) |
|---|---|---|---|
| **CURRENT workbook** | `project/DALI/Dali_testmode.xlsx` | `len(read_bytes())` = **12,210,680** bytes; `Get-Item .Length` = 12,218,368 bytes (DLP/TSZ container vs plaintext delta = 7,688 B); mtime `2026/9/16 21:46:39` | **`f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564`** |
| OLD workbook revision | same path, superseded content | sha recorded by the previous extraction (not read as a file — no copy exists on disk) | `d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e` |
| **Witness for the OLD revision's OVERVIEW text** | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dft.json` | `overview.sha256` = `d9d721a3…c7788e`; `overview.sheet` = `OVERVIEW`; `overview.file` = `project/DALI/Dali_testmode.xlsx`; `sourceRowCount` = 250; `generatedBy` = `scripts/_dft_extract.py`; `runId` = `acceptance-20260916-dali10`; **14 in-scope rows** | (JSON not hashed here) |
| Old revision human-readable dump | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt` | 12,402 B, mtime 2026-09-16 13:43:58; TM600 at line 234, TM601 at line 258 | (not hashed) |
| OLD DFT IR | `team/artifacts/acceptance-20260916-dali10/dft-ir.json` | `generatedAt` = `2026-09-16T14:15:18+08:00`; `source.sha256` = `d9d721a3…c7788e` | (not hashed) |
| `reg_config/tm600.sv` | `project/DALI/reg_config/tm600.sv` | 1,495 B | `290574bcd198cb5e85429f8ae37f91ce97da31713cfc7075b9d07e57014bada0` |
| `reg_config/tm601.sv` | `project/DALI/reg_config/tm601.sv` | 1,378 B | `d250b43cdaba3513b031f6dfc5ffc4743f5c6058787709f7286122152948fade` |
| `project/DALI/input/DFT.csv` | — | 16,862 B | `b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4` |
| `project/DALI/input/DFT_restored.csv` | — | 16,824 B | `0e0c31106586eacc0ef919b2c5a42d78c036e714d905ec9a7121dbffadcd8bc2` |

**Both `reg_config/*.sv` hashes are byte-identical to the hashes the old IR recorded**
(`dft-ir.json` → `items[7].evidence[3].sha256` and `items[8].evidence[3].sha256`), and both CSV hashes match
`dft-ir.json` → `source.secondaryIntentSource.sha256` / `source.tertiarySources[0].sha256`.
⇒ **The `.sv` files and both CSVs are UNCHANGED. Only the workbook changed.**

`dft-raw/dft-ir-hashes.json` is itself DLP/TSZ-protected (it renders as ciphertext under both PowerShell and
Python text reads), so it was **not** used as evidence; `overview-dft.json` (plaintext) was used instead.

---

## 1. Verbatim current-workbook rows (every non-empty cell, column name included)

Header is `OVERVIEW` row 1. Column letters are given so every locator is unambiguous.

### 1.1 `OVERVIEW!row 132` — Item = TM600

| Col | Column name (row 1, verbatim) | Value (verbatim; `\n` = real newline inside the cell) |
|---|---|---|
| A | `Item` | `TM600` |
| B | `Level` | `BUBO` |
| C | `Name` | `HS_RDSON` |
| D | `Description` | `high side powerfet rdson` |
| E | `ExpectValue` | `11` (numeric) |
| F | `Unit` | `mΩ` |
| G | `Test` | `direct` |
| H | `Special` | `Y\n2 FLOAT` |
| I | `Purpose` | `SCM` |
| K | `Notes` | `Rds,on=(PMID-SW)/ISW` |
| L | `Code1` | `vset[vbat,3.5,100e-6,0]\nvset[pmid,5,100e-6,0]\nvset[bst_sw,5,1e-3,0]\nvset[vdrv,5,100e-6,0]` |
| M | `Code2` | `en_tm[]\nfield[(WAKE_UP,1)]\nfield[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]` |
| N | `Code3` | `delay[1e-3]\niset[sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]` |
| O | `Power` | `VBAT\nBST-SW` |
| P | `Dynamic` | `ISW` |
| Q | `Check` | `PMID-SW\nfloating source：V(BST_SW)` |
| R | `isCodeGen` | `Y` |
| U | `State \nAMS\nValidation` | `Done` |
| AH | `de test` | `I=0.2A\npmid-sw=46mV` |
| AJ | `is test` | `checked` |

Empty in row 132: `J` (Trim), `S` (`isRun`), `T` (Assign), `V` (`State\nBench Validation`),
`W` (`is CP test?`), `X` (`CP comment`), `Y` (`State\nATE Validation`), `Z` (`HELPER`), cols 27–33, `AI` (`aetest`).

### 1.2 `OVERVIEW!row 133` — Item = TM601

| Col | Column name (row 1, verbatim) | Value (verbatim; `\n` = real newline inside the cell) |
|---|---|---|
| A | `Item` | `TM601` |
| B | `Level` | `BUBO` |
| C | `Name` | `LS_RDSON` |
| D | `Description` | `low side powerfet  rdson` (note: **two** spaces before `rdson`) |
| E | `ExpectValue` | `7.5` (numeric) |
| F | `Unit` | `mΩ` |
| G | `Test` | `direct` |
| **H** | `Special` | **EMPTY — no cell value at all** |
| I | `Purpose` | `SCM` |
| K | `Notes` | `Rds,on=(SW-PGND)/IPMID2SW` |
| **L** | `Code1` | `vset[vbat,3.5,100e-6,0]\nvset[vdrv,5,100e-6,0]\nvset[vbus,5,100e-6,0]\nvset[bst,5,100e-6,0]` |
| M | `Code2` | `en_tm[]\nfield[(WAKE_UP,1)]\nfield[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]` |
| N | `Code3` | `delay[5e-3]\niset[pmid_sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]` |
| O | `Power` | `VBAT` |
| P | `Dynamic` | `SW\nISW` |
| Q | `Check` | `SW-PGND\nfloating source：I(PMID_SW)` |
| R | `isCodeGen` | `Y` |
| U | `State \nAMS\nValidation` | `Done` |
| AH | `de test` | `I=1A\nSW-PGND=0.3` |
| AJ | `is test` | `checked` |

Empty in row 133: `H` (Special), `J`, `S`, `T`, `V`, `W`, `X`, `Y`, `Z`, cols 27–33, `AI`.

Literal per-line readings of cell `L133` (the changed cell):
```
line 1: vset[vbat,3.5,100e-6,0]
line 2: vset[vdrv,5,100e-6,0]
line 3: vset[vbus,5,100e-6,0]
line 4: vset[bst,5,100e-6,0]
```
Literal per-line readings of cell `N133`: `delay[5e-3]` / `iset[pmid_sw,1,1e-3,0]` / `delay[2e-3]` / `finish[]`.

---

## 2. Other sheets mentioning TM600 / TM601

**Method.** Every sheet was iterated cell-by-cell (all 22 sheets: `Progress`, `action`, `OVERVIEW`,
`codeExplain`, `InitialDFT_Check`, `SpeicalSetup`, `Package`, `ABS`, `Pin2Pin`, `TestIO`, `TESTREG`,
`SETTING_MAP`, `DTESTMAP`, `ATESTMAP`, `TRIM_REG`, `TRIMTABLE_AMUX`, `TRIMTABLE_MNT`, `TRIMTABLE_BG`,
`TRIMTABLE_CLK`, `TRIMTABLE_BUBO`, `TRIMTABLR_QDT`, `TRIMTABLE_IBUS`) with a case-insensitive regex
`TM\s*_?60[01]|PMID_SW|PMI2SW|pmid2sw|sw2pgnd|TM600|TM601`.

**Result — FACT:** the only cells in the entire workbook matching `TM600`/`TM601` are `OVERVIEW!A132` and
`OVERVIEW!A133`. **Zero hits** in `Progress`, `InitialDFT_Check`, `SpeicalSetup`, `TESTREG`,
`SETTING_MAP`, `DTESTMAP`, `ATESTMAP`, `TRIMTABLE_BUBO` or any other sheet.

The same sweep shows exactly where the TM601 instrument tokens live in the workbook (all in the TM601 row),
and two **unrelated** rows for context:
- `OVERVIEW!K133`, `OVERVIEW!N133`, `OVERVIEW!Q133` — the only TM601 token cells (see §1.2).
- `OVERVIEW!L137`, `P137`, `Q137` — TM603: `…iset[pmid_sw,4,1e-3,0]…`, `Dynamic=IPMID2SW`,
  `Check=DTEST\nIPMID2SW\nfloating source：I(PMID_SW)`. (Same instrument naming convention, different item.)
- `OVERVIEW!L140`, `Q140`, `N141`, `Q141` — `vset[…]\nvset[bst_sw,5,1e-3,0]\niset[pmid_sw,-0.2,1e-3,0]`, `Check=V(DTEST0)\nfloating source：I(PMID_SW)` (a `bst_sw` pair token exists elsewhere in the workbook, but **not** in the TM600/TM601 rows).
- `OVERVIEW!Q149` — `V(DTEST0)\nfloating source：V(BST_SW)、I(PMID_SW)` (the only other `V(BST_SW)` compliance monitor).
- **`sw2pgnd` appears ZERO times in the entire workbook.**

---

## 3. `project/DALI/reg_config/tm600.sv` — full body verbatim (1,495 B)

```
/////////////////////// Auto-generated AMS Test Code ////////////
/////////////////////// Test: HS_RDSON ////////////
// Test Item: TM600, generate time: 2026-05-15 16:48:30 //
//////////////////generated by Tom/////////////////////////////

`NVT_STIM.en_vsrc_vbat = 1;
`NVT_STIM.vsrcVBAT.ramp_vsrc_val(3.5, 100e-6);
#1000;
// pin VBAT set to 3.5V
//		vset[vbat,3.5,100e-6,0]
`NVT_STIM.en_vsrc_pmid = 1;
`NVT_STIM.vsrcPMID.ramp_vsrc_val(5, 100e-6);
#1000;
// pin PMID set to 5V
//		vset[pmid,5,100e-6,0]
`NVT_STIM.en_vsrc_bst_sw = 1;
`NVT_STIM.vsrcBST_SW.ramp_vsrc_val(5, 1e-3);
#1000;
// pin BST_SW set to 5V
//		vset[bst_sw,5,1e-3,0]
`NVT_STIM.en_vsrc_vdrv = 1;
`NVT_STIM.vsrcVDRV.ramp_vsrc_val(5, 100e-6);
#1000;
// pin VDRV set to 5V
//		vset[vdrv,5,100e-6,0]

entertestmode();
//		en_tm[]
I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
//		field[(WAKE_UP,1)]
I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // Write reg 0x59 = 32
I2CWriteSameData(DEV_ADDR, 0x5A, 0x02);  // Write reg 0x5A = 2
I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // Write reg 0x61 = 75
//		field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]

#1000000;  // delay 1e-3s
//		delay[1e-3]
`NVT_STIM.en_isrc_sw = 1;
`NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3);
#1000;
// pin SW current set to 1A
//		iset[sw,1,1e-3,0]
#2000000;  // delay 2e-3s
//		delay[2e-3]
$finish;
//		finish[]

/////////////////////// End of Auto-generated Code ////////////
```

> Note: the file as read contains **no space** in the banner lines
> (`// Test Item: TM600, generate time: 2026-05-15 16:48:30 //`); the header
> comments are reproduced exactly as bytes on disk. `generate time` is 2026-05-15 and is **older** than the
> workbook's other content — the `.sv` is unchanged since the old revision and was not regenerated.

## 3.1 `project/DALI/reg_config/tm601.sv` — full body verbatim (1,378 B)

```
/////////////////////// Auto-generated AMS Test Code ////////////
/////////////////////// Test: LS_RDSON ////////////
// Test Item: TM601, generate time: 2026-05-15 16:48:30 //
//////////////////generated by Tom/////////////////////////////

`NVT_STIM.en_vsrc_vbat = 1;
`NVT_STIM.vsrcVBAT.ramp_vsrc_val(3.5, 100e-6);
#1000;
// pin VBAT set to 3.5V
//		vset[vbat,3.5,100e-6,0]
`NVT_STIM.en_vsrc_vdrv = 1;
`NVT_STIM.vsrcVDRV.ramp_vsrc_val(5, 100e-6);
#1000;
// pin VDRV set to 5V
//		vset[vdrv,5,100e-6,0]
`NVT_STIM.en_vsrc_vbus = 1;
`NVT_STIM.vsrcVBUS.ramp_vsrc_val(5, 100e-6);
#1000;
// pin VBUS set to 5V
//		vset[vbus,5,100e-6,0]

entertestmode();
//		en_tm[]
I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // Write reg 0x10 = 67
//		field[(WAKE_UP,1)]
I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // Write reg 0x59 = 32
I2CWriteSameData(DEV_ADDR, 0x5A, 0x01);  // Write reg 0x5A = 1
I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // Write reg 0x61 = 75
//		field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]

#5000000;  // delay 5e-3s
//		delay[5e-3]
`NVT_STIM.en_isrc_pmid_sw = 1;
`NVT_STIM.isrcPMID_SW.ramp_isrc_val(1, 1e-3);
#1000;
// pin PMID_SW current set to 1A
//		iset[pmid_sw,1,1e-3,0]
#2000000;  // delay 2e-3s
//		delay[2e-3]
$finish;
//		finish[]

/////////////////////// End of Auto-generated Code ////////////
```

**FACT (decisive for 5b):** `tm601.sv` contains **no `bst` token of any kind** — no `en_vsrc_bst`,
no `vsrcBST`, no `vset[bst…]`, no `vset[bst_sw…]`. Its only rails are VBAT, VDRV, VBUS.

---

## 4. Field-by-field diff

### 4A. What actually changed in the workbook (old revision → current revision)

The old revision's OVERVIEW text is witnessable from `dft-raw/overview-dft.json`
(which self-records `overview.sha256 = d9d721a3…c7788e`). Comparing it against the current workbook:

| Row | Item | Differing cells | Old revision (d9d721a3) | Current revision (f4bbb856) | Verdict |
|---|---|---|---|---|---|
| 132 | TM600 | — | — | — | **IDENTICAL — all 39 captured fields equal** |
| 133 | TM601 | **`L133` (`Code1`)** | `vset[vbat,3.5,100e-6,0]\nvset[vdrv,5,100e-6,0]\nvset[vbus,5,100e-6,0]` (3 lines) | `…\nvset[bst,5,100e-6,0]` (**4 lines**) | **CHANGED (line 4 added)** |

**Scope caveat (FACT):** the old extract covers only **14 of the 250 data rows**
(rows 2, 3, 4, 5, 6, 9, 10, 15, 16, 17, 45, 132, 133, 241), so the claim above is precise for
**TM600/TM601 only**, and additionally shows two unrelated trailing-whitespace changes in rows it does cover
(`F6`/`Code1` TM001_3 gained a trailing `\n`; `D10`/`Description` TM103 gained a trailing space).
Cells outside those 14 rows were **not** comparable → the rest of the workbook's diff status is **UNKNOWN**.

### 4B. Current workbook vs old `dft-ir.json` items (the requested diff)

Legend: **SAME** · **CHANGED (old → new)** · **NEW in workbook** (workbook has it, IR does not) ·
**REMOVED from workbook** (IR has it, workbook does not) · **IR-ONLY/derived** (IR content neither stated
nor contradicted by the workbook).

#### TM600 (`dft-ir.json` → `items[7]`, symbol `TM600_HS_RDSON`)

| Field | Old IR value | Current workbook | Verdict |
|---|---|---|---|
| Item / Level / Name | `TM600` / `BUBO` / `HS_RDSON` | `A132`/`B132`/`C132` identical | **SAME** |
| Description | "high side powerfet rdson — Rds,on=(PMID-SW)/ISW with a floating high-current force and a differential Kelvin sense across PMID-SW" | `high side powerfet rdson` | **SAME raw token**; IR text is an elaboration, not verbatim |
| ExpectValue | `11` (`limits[0]`) | `11` (`E132`) | **SAME** |
| Unit | `mΩ` | `mΩ` (`F132`) | **SAME** |
| Test | `direct` (in `evidence[0]`) | `direct` (`G132`) | **SAME** |
| Special | `Y / 2 FLOAT`; `bd07Status` = "BD-07 … remains **OPEN** — the two-floating-node reading is an implementation assumption, not a source fact" | `Y\n2 FLOAT` (`H132`) | **SAME string**; semantics still **UNKNOWN/OPEN** |
| Purpose = `SCM` | not recorded anywhere in `items[7]` | `SCM` (`I132`) | **NEW in workbook vs IR** |
| Notes | `Rds,on=(PMID-SW)/ISW` (`evidence[0]`) | identical (`K132`) | **SAME** |
| `Code1` rails — vbat | `vbat = 3.5 V, ramp 100e-6` (`stimuli[0]`, note cites **reg_config/tm600.sv**) | `vset[vbat,3.5,100e-6,0]` (`L132` line 1) | **SAME value**; provenance now OVERVIEW-rank-1 |
| `Code1` rails — pmid | `pmid = 5.0 V, ramp 100e-6` (`stimuli[1]`) | `vset[pmid,5,100e-6,0]` (line 2) | **SAME** |
| `Code1` rails — bst_sw | `bst_sw = 5.0 V, ramp 1e-3` (`stimuli[2]`, "the BST-SW differential rail is held at 5 V") | `vset[bst_sw,5,1e-3,0]` (line 3) | **SAME** |
| `Code1` rails — vdrv | `vdrv = 5.0 V, ramp 100e-6` (`stimuli[3]`) | `vset[vdrv,5,100e-6,0]` (line 4) | **SAME** |
| `Code2` en_tm + fields | kinds `en_tm` and `field`; `WAKE_UP`, `D2A_BUBO_EN_FORCE_ON`, `D2A_BUBO_TM_DIS_CLK`, `D2A_BUBO_TM_HSON` (`stimuli[4],[5]`) | `M132` identical token-for-token | **SAME** |
| `Code3` delay → iset → delay → finish | `delay 1e-3`; `iset[sw,1,1e-3,0]`; `delay 2e-3` (`stimuli[6],[7],[9]`) | `N132` = `delay[1e-3]\niset[sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]` | **SAME values** — but note the IR's own claim below is *false* |
| IR claim: "OVERVIEW … no force at all" | `conflicts[0].forceMagnitudeDisambiguation`: "OVERVIEW (rows 132/133) **states no force at all**"; `items[8].authorityChain.overview`: "rows 132/133 state the check nodes … **but no force value**" | `N132` (and `N133`) state the force explicitly | **CONTRADICTED — the IR claim is wrong for BOTH workbook revisions.** The force line was present in the old revision too (`overview-dft.json` row 132 `Code3`). This is an **old-IR under-extraction defect**, not a workbook change. |
| `Power` | `channels[2]` supply `VBAT`, `BST-SW`, `VDRV`; `channels[3]` bootstrap `BST`/`SW` | `VBAT\nBST-SW` (`O132`) | **SAME pair present**; IR additionally lists **VDRV** (from `.sv`) and a `BST`/`SW` bootstrap channel that the `Power` cell does not name |
| `Dynamic` | `measurements[1]` MI on `SW` (A) | `ISW` (`P132`) | **SAME** |
| `Check` | `measurements[0]` MV `PMID-SW`; `measurements[2]` MV `BST_SW` = "floating-source compliance monitor **named by OVERVIEW Check**" | `PMID-SW\nfloating source：V(BST_SW)` (`Q132`) | **SAME** |
| `isCodeGen` = `Y` | not recorded | `Y` (`R132`) | **NEW in workbook vs IR** |
| `State AMS Validation` = `Done` | not recorded | `Done` (`U132`) | **NEW in workbook vs IR** |
| `de test` = `I=0.2A\npmid-sw=46mV` | not recorded | `AH132` identical | **NEW in workbook vs IR** |
| `is test` = `checked` | not recorded | `AJ132` | **NEW in workbook vs IR** |
| Register writes | `registerWritesFromOverview` = `[]`; `registerWritesFromRegConfig` = `0x10=0x43`, `0x59=0x20`, `0x5A=0x02`, `0x61=0x4B` | `M132` gives field **names** only, no addresses | **SAME** (no conflict; workbook states no address) |
| `testType` [normal, high-current, differential]; `mvMiRequirement`; `sequence`; `highCurrentPlan`; `compliance` = UNKNOWN | IR-derived from `.sv` + DFT.csv | not stated by the workbook | **IR-ONLY/derived**; `compliance` still **UNKNOWN** |
| `limits[1]` DFT.csv `ExpectValue=10` ("mohm") | IR alternative | workbook `11` | **CHANGED/unresolved**: 11 (wb) vs 10 (DFT.csv rec. 18, re-read this task: `ExpectValue='10'`, `Unit='mohm'`) — conflict **unchanged**, not resolved here |
| Force/sense pair | `forceAndSense.force.authoritativePair` = `pmid2sw`; `sense.ruledPair` = `PMID-SW` (captain R-03/CR-03) | `K132` `(PMID-SW)/ISW`, `P132` `ISW`, `Q132` `PMID-SW`, `N132` `iset[sw,…]` | **SAME / consistent** (workbook names the loop by its two ends and the instrument pin as `sw`) |

#### TM601 (`dft-ir.json` → `items[8]`, symbol `TM601_LS_RDSON`)

| Field | Old IR value | Current workbook | Verdict |
|---|---|---|---|
| Item / Level / Name | `TM601` / `BUBO` / `LS_RDSON` | `A133`/`B133`/`C133` identical | **SAME** |
| Description | "low side powerfet rdson — Rds,on=(SW-PGND)/IPMID2SW with a floating force and differential Kelvin sense across the low-side FET" | `low side powerfet  rdson` (double space) | **SAME raw token**; IR text is an elaboration |
| ExpectValue | `7.5` (`limits[0]`) | `7.5` (`E133`) | **SAME** |
| Unit | `mΩ` | `mΩ` (`F133`) | **SAME** |
| Test | `direct` | `direct` (`G133`) | **SAME** |
| Special | `limits[0]` says "**no Special flag**" | `H133` **empty** | **SAME** |
| Purpose = `SCM` | not recorded | `SCM` (`I133`) | **NEW in workbook vs IR** |
| Notes | `Rds,on=(SW-PGND)/IPMID2SW` (`evidence[0]`) | identical (`K133`) | **SAME** |
| `Code1` rails — vbat | `vbat = 3.5 V, ramp 100e-6` (`stimuli[0]`) | `vset[vbat,3.5,100e-6,0]` (`L133` line 1) | **SAME** |
| `Code1` rails — vdrv | `vdrv = 5.0 V, ramp 100e-6` (`stimuli[1]`) | `vset[vdrv,5,100e-6,0]` (line 2) | **SAME** |
| `Code1` rails — vbus | `vbus = 5.0 V, ramp 100e-6` (`stimuli[2]`) | `vset[vbus,5,100e-6,0]` (line 3) | **SAME** |
| **`Code1` rails — bst** | **ABSENT** — `items[8].channels` lists only force, sense, and supply `[VBAT, VDRV, VBUS]`; `stimuli` has no `bst`; `reg_config/tm601.sv` has no `bst` | **`vset[bst,5,100e-6,0]` (line 4)** | **NEW in workbook** — new vs old revision, vs old IR, **and vs `tm601.sv`** |
| `Code2` en_tm + fields | `WAKE_UP`, `D2A_BUBO_EN_FORCE_ON`, `D2A_BUBO_TM_DIS_CLK`, `D2A_BUBO_TM_LSON` | `M133` identical token-for-token | **SAME** |
| `Code3` delay → iset → delay → finish | `delay 5e-3`; `iset[pmid_sw,1,1e-3,0]`; `delay 2e-3` — with `stimuli[5].note` "delay 5e-3 before the current is applied (longer than TM600's 1 ms)" | `N133` = `delay[5e-3]\niset[pmid_sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]` | **SAME values** (IR cited only `reg_config/tm601.sv`; the workbook now carries the identical text) |
| IR claim: "OVERVIEW … no force at all" | as above | `N133` states `iset[pmid_sw,1,1e-3,0]` | **CONTRADICTED** (present in old revision too — see §4A). Old-IR extraction defect. |
| `Power` | `channels[2]` supply `VBAT`, `VDRV`, `VBUS` | `VBAT` (`O133`) | **SAME subset**; IR additionally lists `VDRV`/`VBUS` (from `.sv`). Neither names `BST`/`BST-SW` — **so the new `vset[bst,…]` is not mirrored in `Power`.** |
| `Dynamic` | `measurements[1]` **MI pin `PMID_SW`** (A) | `SW\nISW` (`P133`) | **CHANGED (IR: `PMID_SW` → workbook: `SW`, `ISW`)** — same physical loop, different pin naming; unresolved |
| `Check` | `forceAndSense.force.checkNode` = "`PGND-SW` (DFT.csv Check) / `SW-PGND` (OVERVIEW Notes …)"; `sense.source` = "DFT.csv `Check=PGND-SW` and OVERVIEW Notes …" | `SW-PGND\nfloating source：I(PMID_SW)` (`Q133`) | **CHANGED (IR recorded DFT.csv's reversed `PGND-SW` as *the* Check → workbook Check cell reads `SW-PGND`)**; the floating-source token `I(PMID_SW)` matches the IR's `instrumentPin.node = PMID_SW` |
| Force pair + polarity | `forceAndSense.force.authoritativePair` = **`sw2pgnd`**, polarity **"PGND = HIGH end, SW = LOW end"**, source "DFT.csv record index 19: `iset[sw2pgnd,1,1e-6,0]`"; `rulingApplied` = "R-03: TM601 force sw2pgnd / sense SW-PGND (**adopt DFT.csv, NOT the .sv PMID↔SW pair**)"; `supersededNotation.status` = "**SUPERSEDED-BY-RULING — do not wire TM601 from the .sv notation**" | Workbook says `SW-PGND` (Check) + `IPMID2SW` (Notes) + `pmid_sw` (Code3 iset) and states **no polarity and no force-pair token**; **`sw2pgnd` appears zero times in the workbook** | **CHANGED / MATERIAL** — the workbook's own Check cell re-asserts exactly the `.sv` notation `I(PMID_SW)` that the IR's CR-03 declared superseded. The IR's ruled pair is **not** in the new DFT, and the new DFT's token is **not** in the IR's ruled pair. Unresolved — see §5a and §8. |
| `isCodeGen` = `Y` | not recorded | `Y` (`R133`) | **NEW in workbook vs IR** |
| `State AMS Validation` = `Done` | not recorded | `Done` (`U133`) | **NEW in workbook vs IR** |
| `de test` = `I=1A\nSW-PGND=0.3` | not recorded | `AH133` identical | **NEW in workbook vs IR** |
| `is test` = `checked` | not recorded | `AJ133` | **NEW in workbook vs IR** |
| Register writes | `registerWritesFromOverview` = `[]`; `registerWritesFromRegConfig` = `0x10=0x43`, `0x59=0x20`, `0x5A=0x01`, `0x61=0x4B` | `M133` field names only | **SAME** (no conflict) |
| `limits[1]` DFT.csv `ExpectValue=8` ("mohm") | IR alternative | workbook `7.5` | **CHANGED/unresolved**: 7.5 (wb) vs 8 (DFT.csv rec. 19, re-read: `ExpectValue='8'`) — conflict unchanged |
| `testType`, `mvMiRequirement`, `sequence`, `highCurrentPlan`, `compliance` = UNKNOWN, `ambiguities[0..3]` | IR-derived | not stated by the workbook | **IR-ONLY/derived**; `ambiguities[0]` (three-way force-pin disagreement), `[2]` (no LS golden), `[3]` (compliance) **all still open** |

### 4C. Third source, re-read in this task (not part of §4A but load-bearing for §5a)

`project/DALI/input/DFT.csv` (sha `b92d203f…0fd4`) and `DFT_restored.csv` (sha `0e0c3110…8bc2`), records 18/19
(1-based) — queried with `csv.reader`, not by text grep:

| | TM600 (rec. 18) | TM601 (rec. 19) |
|---|---|---|
| `ExpectValue` / `Unit` | `10` / `mohm` (restored: `mΩ`) | `8` / `mohm` (restored: `mΩ`) |
| `Hardware_initial` | `vset[vbat,4.2,100e-6,0]\nvset[pmid,15,100e-6,0]\nvset[bst2sw,5,1e-3,0]\nvset[vdrv,5,100e-6,0]` | `vset[vbat,4.2,100e-6,0]\nvset[pmid,9,100e-6,0]\nvset[vdrv,5,100e-6,0]` |
| `Dynamic` | `iset[pmid2sw,1,1e-3,0]` | `iset[sw2pgnd,1,1e-6,0]` |
| `Check` | `PMID-SW` | `PGND-SW` |
| `Type` | `MV&MI` | `MV&MI` |

Both CSVs are byte-identical to the hashes the old IR recorded ⇒ **unchanged**.
Note the CSVs' TM601 rails are `vbat=4.2, pmid=9, vdrv=5` — a **third, mutually inconsistent** rail set.

---

## 5. Explicit answers to 5a–5e (verbatim locators)

### 5a. TM601 force/sense loop, Check expression, instrument family name

- **Check expression (verbatim, `OVERVIEW!Q133`):** `SW-PGND\nfloating source：I(PMID_SW)`
  — i.e. the sensed differential is **`SW-PGND`**, and the "floating source" annotation is a **current**
  (`I(…)`) on node **`PMID_SW`** (full-width colon `：` in the source).
- **Force line (verbatim, `OVERVIEW!N133`, `Code3`):** `iset[pmid_sw,1,1e-3,0]`
  ⇒ **the token that appears is `pmid_sw`** (lowercase, underscore), matching `reg_config/tm601.sv`:
  `` `NVT_STIM.en_isrc_pmid_sw = 1; `` / `` `NVT_STIM.isrcPMID_SW.ramp_isrc_val(1, 1e-3); ``
  and the `.sv` comment `//		iset[pmid_sw,1,1e-3,0]`.
- **`iset[sw2pgnd,…]` does NOT appear in the workbook at all** (zero hits workbook-wide).
  It exists only in `project/DALI/input/DFT.csv` record 19 → `Dynamic = 'iset[sw2pgnd,1,1e-6,0]'`
  (and identically in `DFT_restored.csv`), i.e. in the old IR's `items[8].forceAndSense.force.source`.
- **`iset[pmid2sw,…]` does NOT appear in the TM601 row.** It appears only in `DFT.csv` record 18 (TM600).
  The workbook's TM601 Notes label the current `IPMID2SW` (`OVERVIEW!K133`).
- **Instrument family name — FACT (negative):** neither `OVERVIEW!row 133` nor `reg_config/tm601.sv` names any
  instrument family. **No `FPVI`, `FPVIe`, `FOVIe`, `FXVIe`, `ACM`, `QTMV`, `HPVIe` token appears** in either.
  The only instrument-identity strings present are the generic conventions
  `floating source：I(PMID_SW)` (`Q133`) and `IPMID2SW` (`K133`), plus the `.sv` handle `isrcPMID_SW`.
  ⇒ **"FPVI-style" is an INFERENCE from `knowledge/` + fixture evidence, never a DFT-stated fact.**
  What the workbook *does* state that bears on instrument choice: a **current-source (I) floating** measurement
  (`Q133`) and the pair name `SW-PGND` (`Q133`) with `IPMID2SW` (`K133`).

### 5b. BST (bootstrap) rail for TM601

- **YES — and it is the single change in this workbook revision.**
  Verbatim line, `OVERVIEW!L133` (`Code1`) **line 4**:
  ```
  vset[bst,5,100e-6,0]
  ```
  Value **5 V**, ramp **100e-6 s**, ignore field **0**, pin token **`bst`** (single pin, not `bst_sw`).
- **NOT PRESENT in the old revision** (`overview-dft.json` row 133 `Code1` has only 3 lines), it is absent from
  `reg_config/tm601.sv` (no `bst` token anywhere in that file), and it is absent from the old IR.
- **BST-SW differential for TM601: NOT specified.** Contrast with TM600, which has all three of:
  `OVERVIEW!L132` line 3 `vset[bst_sw,5,1e-3,0]` (pair token + **1e-3** ramp), `OVERVIEW!O132` `Power` =
  `VBAT\nBST-SW`, and `OVERVIEW!Q132` `Check` = `PMID-SW\nfloating source：V(BST_SW)`
  (a **V**oltage compliance monitor on `BST_SW`).
  For TM601: `Power` (`O133`) = `VBAT` only; `Check` (`Q133`) monitors **`I(PMID_SW)`**, not `V(BST_SW)`;
  and the string `bst_sw`/`BST-SW` appears **nowhere** in row 133.
  ⇒ TM601 has an **absolute BST rail but no BST-SW differential pair and no BST-SW compliance monitor**.
  Whether `vset[bst,…]` means absolute-vs-ground or differential-vs-SW is **UNKNOWN** (see §7/§8).

### 5c. TM601 values for vbat / vdrv / vbus, ExpectValue, Unit, Test, Special, Notes

| Asked | Verbatim | Locator |
|---|---|---|
| vbat | `vset[vbat,3.5,100e-6,0]` → **3.5 V**, ramp `100e-6`, ignore `0` | `OVERVIEW!L133` line 1 |
| vdrv | `vset[vdrv,5,100e-6,0]` → **5 V** | `OVERVIEW!L133` line 2 |
| vbus | `vset[vbus,5,100e-6,0]` → **5 V** | `OVERVIEW!L133` line 3 |
| (bst, for completeness) | `vset[bst,5,100e-6,0]` → **5 V** | `OVERVIEW!L133` line 4 |
| ExpectValue | `7.5` (numeric cell) | `OVERVIEW!E133` |
| Unit | `mΩ` | `OVERVIEW!F133` |
| Test | `direct` | `OVERVIEW!G133` |
| **Special** | **cell is EMPTY — no value** | `OVERVIEW!H133` |
| Notes | `Rds,on=(SW-PGND)/IPMID2SW` | `OVERVIEW!K133` |

Also, verbatim and relevant: `OVERVIEW!O133` = `VBAT`; `OVERVIEW!P133` = `SW\nISW`;
`OVERVIEW!N133` = `delay[5e-3]\niset[pmid_sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]`;
`OVERVIEW!M133` = `en_tm[]\nfield[(WAKE_UP,1)]\nfield[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]`.
**No `vset[pmid,…]` exists for TM601** (TM600 has one; TM601 does not) even though its Notes reference `IPMID2SW`.

### 5d. TM600 values: PMID, BST_SW, ExpectValue, Special, Dynamic/iset, Check

| Asked | Verbatim | Locator |
|---|---|---|
| PMID | `vset[pmid,5,100e-6,0]` → **5 V** (line 2 of 4) | `OVERVIEW!L132` |
| BST_SW | `vset[bst_sw,5,1e-3,0]` → **5 V**, ramp **`1e-3`** (line 3 of 4) | `OVERVIEW!L132` |
| (other rails, completeness) | `vset[vbat,3.5,100e-6,0]` (line 1) and `vset[vdrv,5,100e-6,0]` (line 4) | `OVERVIEW!L132` |
| ExpectValue | `11` | `OVERVIEW!E132` |
| Special | `Y\n2 FLOAT` | `OVERVIEW!H132` |
| Dynamic | `ISW` | `OVERVIEW!P132` |
| Dynamic/iset line | `delay[1e-3]\niset[sw,1,1e-3,0]\ndelay[2e-3]\nfinish[]` → force **`iset[sw,1,1e-3,0]`** | `OVERVIEW!N132` |
| Check | `PMID-SW\nfloating source：V(BST_SW)` | `OVERVIEW!Q132` |
| Power | `VBAT\nBST-SW` | `OVERVIEW!O132` |
| Unit / Test / Purpose / Notes | `mΩ` / `direct` / `SCM` / `Rds,on=(PMID-SW)/ISW` | `F132` / `G132` / `I132` / `K132` |

### 5e. Numeric validation/measured columns — verbatim, with column names, and limit-vs-measured status

| Verbatim value | Column name (row 1) | Locator |
|---|---|---|
| `I=0.2A\npmid-sw=46mV` | `de test` (col 34) | `OVERVIEW!AH132` (TM600) |
| `I=1A\nSW-PGND=0.3` | `de test` (col 34) | `OVERVIEW!AH133` (TM601) |
| `checked` | `is test` (col 36) | `OVERVIEW!AJ132`, `OVERVIEW!AJ133` |

- **`I=1A` / `SW-PGND=0.3` (`AH133`) — read verbatim; the `0.3` carries NO unit.**
- **`I=0.2A` / `pmid-sw=46mV` (`AH132`) — `46mV` has an explicit unit.**
- **Limit vs measured — FACT:** the spec limit for these items is the separate column pair
  `ExpectValue` + `Unit` (`E`/`F` = `11 mΩ` TM600, `7.5 mΩ` TM601). The `de test` column is a **different
  column** whose header is literally `de test` (DE = design-engineering debug), and `is test` = `checked` is a
  status flag. So these are **not** the acceptance limits.
- **INFERENCE (explicitly labelled, not fact):** the `de test` strings are most plausibly single-point
  DE/debug `I`-and-`V` observations. They cannot be RDSON *limits* and are arithmetically inconsistent with a
  pass at the stated limits (46 mV / 0.2 A = 230 mΩ vs 11 mΩ; 0.3 at 1 A = 300 mΩ if volts vs 7.5 mΩ).
- **UNKNOWN:** whether `SW-PGND=0.3` is volts, a code, or an out-of-range reading; whether `I=…` is *set* or
  *measured*; and which bench/probe produced either row. **Neither `de test` cell is recorded anywhere in the
  old IR** → both are NEW relative to it.

---

## 6. What the project's own reference docs state (for the later conflict ruling — NOT resolved here)

Exhaustive searches run over `knowledge/` for `TM600|TM601|HS_RDSON|LS_RDSON` and for
`sw2pgnd|SW2PGND|BST2SW|bst2sw|pmid2sw|PMID2SW|PGND-SW|SW-PGND`.

### 6.1 `knowledge/hardware/voltage-inference.md` — **TM600 only; NO TM601 section exists**

| Locator | Verbatim quote |
|---|---|
| `138` | `## TM600 应用示例` |
| `142` | `DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]` |
| `143` | `      iset[pmid2sw,1A] (dynamic)` |
| `144` | `FET对(C1): PMID ↔ SW, 导通条件 0x59=0x01` |
| `146` | `BST-SW: 无BUS → 类型A独立: BTST_ACM=20V, SW_ACM=0V` |
| `155`–`157` | `| 台阶3 | 10V | 0V | 15V | 15V | A: BTST=15, SW=0 |` … `| 台阶4 | 15V | 0V | 20V | 20V | A: BTST=20, SW=0 |` … `| **FET导通** | 15V | **15V** | 20V | **5V** ✓ | C: PMID=SW |` |
| `70` | `| C1 | PMID ↔ SW | 上管 (HS) | 0x59=0x01 (HSON=1) | PMID = SW |` |
| `72` | `| C3 | SW ↔ PGND | 下管 (LS) | — | SW = PGND |` |
| `80` | `| **下管 (Low-Side)** | SW-PGND, LG-PGND | S=GND |` |
| `98` | `iset[PMID2SW, 1A] → PMID ≈ SW (压差 = I × RDSON, 通常 < 100mV)` |
| `171`–`173` | `{ "id": "C1", "pair": ["PMID", "SW"],   "type": "HS", "condition": "0x59_bit0=1" }` / `{ "id": "C2", "pair": ["VBUS", "PMID"], "type": "HS", "condition": "0x59_bit1=1" }` / `{ "id": "C3", "pair": ["SW", "PGND"],   "type": "LS", "condition": "0x59_bit2=1" }` |

⇒ **`voltage-inference.md` states TM600 rails `vbat=4.2 V, pmid=15 V, bst2sw=5 V, vdrv=5 V`, dynamic
`iset[pmid2sw,1A]`, BST=20 V working point, `BST-SW=5 V`.** It states **nothing whatsoever about TM601** —
no TM601 rails, no TM601 polarity, no TM601 BST value.

### 6.2 Other `knowledge/` files that state TM600 rails/values

| Locator | Verbatim quote |
|---|---|
| `knowledge/references/L4-Golden-code/Rdson.md:17` | `- 上电 = **4 级台阶 ramp**：BST 始终领先 PMID 5V 同步抬（0/0→5/0→10/5→15/10→20/15），每级 delay 200us；FET 导通前 SW=0 独立供电，导通后 SW 跟随 PMID。` |
| `knowledge/references/L4-Golden-code/Rdson.md:18` | `- 测量三段式：FPVI FV=0 → FI=0 → **SetClamp(50,50) = 0.5V compliance（最大可测 500mΩ）** → FI=1A → delay 2ms → MeasureVI → **立即 FI=0 关断**（短脉冲防自热）。` |
| `knowledge/references/L4-Golden-code/Rdson.md:23` | `- 上电：FPVI=0V 初始化 → VBAT=4.2/VDRV=5 → SW=0 → PMID/BST 0 → 台阶 4 级至 BST20/PMID15 → I2C 导通 HS FET（0x59 HSON、0x61 0x0B；导通瞬间 SW 0→15V，BST−SW=5V ✓）。` |
| `knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:17` | `- 上电 = 4 级台阶 ramp（BST 领先 PMID 5V：0/0→5/0→10/5→15/10→20/15，每级 delay 200us）；I2C 导通 HS FET 后 SW 跟随 PMID。` |
| `knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:19` | `- 测量：FV0 → FI0 → **SetClamp(50,50)（0.5V compliance → 最大可测 500mΩ）** → FI=1A → delay 2ms → MeasureVI → **立即 FI=0 关断**（短脉冲防自热）。` |
| `knowledge/references/L4-Golden-code/Rdson.md:16` | `- **BUS 优先级仲裁**：FPVI 只有一个 → 大电流 iset[PMID2SW,1A] 必须用 FPVI（占 K31+K17）；BST−SW 仅需小电流 → 双独立源（BTST_ACM/SW_ACM）供电。` |
| `knowledge/hardware/bus-topology.md:278` | `` `vset[bst2sw]` + `iset[pmid2sw]` 同时存在: `` |
| `knowledge/hardware/bus-topology.md:260` | `| 电压冲突 | HS: PMID=15V, LS: PMID=9V |` (HS/LS merge prohibition table) |
| `knowledge/standards/rules-registry.md:44` (rule `R-BST-SW`) | `**BST-SW 台阶黄金约束 (Current Threshold/ZCD)**: BST≥SW、0≤BST-SW≤5V、目标 BST-SW=5V。HS=BOOST(PMID-SW) / LS=BUCK(SW-PGND)，均电流>200mA 用 FPVIe 浮动源 + BST 台阶上电; **LS 拓扑 SW=PGND=0 用 BST=5V(禁 10V)**、HS 用 BST=5V→10V 台阶; K57_CAP_BST_SW（BUBO BST−SW 对电容；SCH L904 …） 差分电容继电器必闭` — **stated applicability class = `Current Threshold/ZCD 类 (TM607-609)`** |
| `knowledge/claude-history/sessions/06-agent-a6.md:154` | ``典型：TM600 `vset[bst2sw,5]` + `iset[pmid2sw,1A]` + HS FET(`0x59=0x01`) → BST 领先 PMID 5V ramp。`` |

**TM601 in `knowledge/` — one hit only, and it is not a rail statement:**
`knowledge/references/param_type_index.md:55` → `> 过程稿 `TM600_*.cpp`（4 文件）+ `TM601_LS_RDSON.cpp` 已移至
`_archive/` 隔离，**非黄金案例**；…`

### 6.3 Recorded conflict (both sides, unresolved)

| Item | New DFT (`Dali_testmode.xlsx`, `f4bbb856`) | `knowledge/hardware/voltage-inference.md` / goldens |
|---|---|---|
| TM600 vbat | `3.5` (`L132`) | `4.2` (line 142) |
| TM600 pmid | `5` (`L132`) | `15` (line 142) |
| TM600 bst token | `vset[bst_sw,5,1e-3,0]` (`L132`) — pair, 5 V, 1 ms ramp | `vset[bst2sw,5]` (line 142) with working point BST=20 V / BST−SW=5 V (lines 146, 155-157) |
| TM600 iset token | `iset[sw,1,1e-3,0]` (`N132`) | `iset[pmid2sw,1A]` (line 143) |
| TM600 compliance | not stated anywhere in the workbook | `SetClamp(50,50)` = 0.5 V (Rdson.md:18, tm600-normal-highcurrent.md:19) |
| TM601 | `vbat=3.5, vdrv=5, vbus=5, bst=5`; `SW-PGND` / `I(PMID_SW)` / `IPMID2SW`; no BST-SW | **not stated at all** — `voltage-inference.md` has no TM601 example |
| Contract between them | `DFT.csv`/`DFT_restored.csv` third variant: TM600 `vbat=4.2, pmid=15, bst2sw=5`; TM601 `vbat=4.2, pmid=9, vdrv=5` (`iset[sw2pgnd,1,1e-6,0]`) | — |

---

## 7. FACT / INFERENCE / UNKNOWN

### FACT (read verbatim this task)

1. The current workbook is `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564`, 12,210,680 bytes by
   Python `read_bytes` (12,218,368 by `Get-Item`), mtime `2026/9/16 21:46:39`.
2. `OVERVIEW!row 132` (TM600) and `OVERVIEW!row 133` (TM601) contain exactly the cells quoted in §1;
   no merged ranges intersect rows 132–133; no formula cells exist in either row.
3. The **only** workbook change for TM600/TM601 between revisions is the appended 4th line
   `vset[bst,5,100e-6,0]` in `OVERVIEW!L133`. TM600 row 132 is identical in all 39 captured fields.
4. The witness for the old revision (`dft-raw/overview-dft.json`) self-recorded
   `overview.sha256 = d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e`.
5. `reg_config/tm600.sv` and `reg_config/tm601.sv` are byte-identical to the hashes the old IR recorded
   ⇒ unchanged; neither was regenerated (both carry `generate time: 2026-05-15 16:48:30`).
   `DFT.csv` and `DFT_restored.csv` likewise hash-match the old IR ⇒ unchanged.
6. `tm601.sv` contains no `bst` token; `tm600.sv` contains `vset[bst_sw,5,1e-3,0]`.
7. `TM600`/`TM601` appear in `OVERVIEW!A132` and `OVERVIEW!A133` only — no other sheet mentions them.
8. `sw2pgnd` appears **zero** times in the workbook. `iset[pmid_sw,1,1e-3,0]` appears in
   `OVERVIEW!N133` and `OVERVIEW!N137` (TM603 only).
9. No instrument-family token (FPVI/FPVIe/FOVIe/FXVIe/ACM/…) appears in `OVERVIEW!row 133` or `tm601.sv`.
10. The old IR asserts twice that `OVERVIEW` rows 132/133 state "no force value"/"no force at all";
    `overview-dft.json` shows both rows carried `Code3` iset lines in the **old** revision too
    ⇒ that assertion is **false for both revisions** (an old-IR extraction defect, not a DFT change).
11. The `de test` column (`AH132`/`AH133`) holds `I=0.2A\npmid-sw=46mV` and `I=1A\nSW-PGND=0.3`;
    the spec-limit columns are `ExpectValue`+`Unit` (`E`/`F`).

### INFERENCE (mine, not read anywhere)

- I1. `vset[bst,5,100e-6,0]` reads as an **absolute** BST rail of 5 V because the token has one pin
  (`bst`), whereas TM600's `bst_sw` names a pair; consistent with the LS topology `SW=PGND=0` in which the
  project's own rule `R-BST-SW` says "LS … 用 BST=5V(禁 10V)".
- I2. The BST line was added because `tm601.sv` (which never set BST) was judged incomplete for an LS RDSON
  measurement — but nothing in the workbook or `.sv` states a reason.
- I3. The `de test` values are DE/debug single-point observations, not acceptance limits — from column naming
  plus arithmetic inconsistency with `ExpectValue`.
- I4. `I(PMID_SW)` in `Q133` is instrument-pin notation for the same 1 A loop that `iset[pmid_sw,…]` drives;
  the workbook is naming the force instrument's node, not asserting a physical PMID→SW current direction.
- I5. "FPVI-style floating source" for TM601 is defensible only from `knowledge/` goldens and the fixture IR,
  **not** from the DFT.

### UNKNOWN (not established — do not assert)

- U1. Whether `vset[bst,…]` means BST-to-ground or BST-to-SW. **The cell does not say.**
- U2. Whether TM601's physically forced pair is `SW-PGND` (workbook Check) or `sw2pgnd` (DFT.csv/old-IR
  ruling CR-03), and the **polarity**. The workbook states no polarity. Cannot be settled from DFT text.
- U3. Whether TM601 requires a BST-SW **differential** and/or a `V(BST_SW)` compliance monitor (TM600 has
  both; TM601 has neither).
- U4. Units and meaning of `SW-PGND=0.3`; whether `I=…` is set or measured.
- U5. The force compliance/clamp for the 1 A force — stated nowhere in the workbook, `.sv`, or CSVs
  (old IR `highCurrentPlan.compliance` was already UNKNOWN; still UNKNOWN).
- U6. Semantics of TM600 `Special` = `Y\n2 FLOAT` (old IR `BD-07` remains OPEN); unchanged by this revision.
- U7. Whether the workbook changed **outside** the 14 rows the old extract covered. Only those 14 rows were
  comparable; the rest is UNKNOWN (three differing cells were found among the 14: `L133` TM601,
  `F6`/TM001_3 trailing `\n`, `D10`/TM103 trailing space).
- U8. Whether `ExpectValue` 11/7.5 (workbook) or 10/8 (DFT.csv) governs — conflict unchanged.
- U9. Whether TM603's `iset[pmid_sw,…]` (`N137`) and TM601's are meant to be the same convention or a copy
  artefact.
- U10. Whether the old IR must be corrected for its "no force in OVERVIEW" claims before downstream
  consumers rely on `items[7]`/`items[8]`.

---

## 8. Open items requiring another owner's ruling

| # | Question | Owner | Why it blocks |
|---|---|---|---|
| R1 | TM601 force pair + polarity: `SW-PGND` per the new DFT `Check`, or `sw2pgnd` per DFT.csv / old-IR CR-03 (`PGND = HIGH`)? And is `I(PMID_SW)` a wiring statement or instrument-pin notation? | captain / DFT owner + schematic owner | Determines relay wiring for the LS loop; the workbook's Check cell re-asserts the notation the old ruling declared superseded, with no polarity anywhere |
| R2 | Does `vset[bst,5,100e-6,0]` supersede or supplement the (absent) BST-SW handling for TM601, and is an absolute 5 V BST rail correct for LS RDSON? | DFT owner (+ knowledge owner for `R-BST-SW` scope) | A downstream implementer must know whether to drive BST absolutely or as a `bst_sw` differential, and at which ramp (100 µs here vs 1 ms for TM600) |
| R3 | Is a `V(BST_SW)` BST-SW compliance monitor required for TM601 as it is for TM600? | DFT owner | TM600 monitors it in `Check`; TM601 monitors only `I(PMID_SW)` — could be an omission or intentional |
| R4 | Force compliance/clamp for the TM601 1 A force (and for TM600) | DFT/spec owner | Still UNKNOWN in every source; needed to bound the measurable RON range |
| R5 | Ruling on `de test` column: are `I=1A` / `SW-PGND=0.3` / `I=0.2A` / `pmid-sw=46mV` measured results, and what are their units? | DFT/DE owner | Column carries no unit for TM601 and is not in the old IR |
| R6 | Which rail set governs TM600/TM601: workbook (`3.5/5` and `3.5/5/5/5`), `knowledge/voltage-inference.md` (`4.2/15`), or `DFT.csv` (`4.2/15` and `4.2/9`)? | captain / DFT owner | Three mutually inconsistent rail sets across three sources; recorded, deliberately **not** resolved here |
| R7 | Must the old `dft-ir.json` `items[7]`/`items[8]` be corrected or regenerated against `f4bbb856`? | captain | The old IR under-extracted OVERVIEW `Code1..Code3`/`Power`/`Dynamic` and made a false "no force value" claim; downstream consumers may rely on it |
| R8 | Is the TM601 `Special` cell being empty intentional (old IR already recorded "no Special flag")? | DFT owner | Confirmed empty in both revisions; only the intent is unclear |

---

## 9. Reproducibility notes

- Every workbook read: `python` + `openpyxl`, `data_only=True, read_only=True` (values) and a
  `data_only=False` pass (cell `data_type`, merged ranges). No PowerShell text command was used on any
  TSZ/DLP-protected artefact; `dft-raw/dft-ir-hashes.json` was identified as protected and skipped.
- CSVs were parsed with Python's `csv.reader` over `read_bytes()` (embedded newlines inside quoted cells
  make line-based text tooling unsafe).
- `reg_config/*.sv` read as bytes with Python, hashed with `hashlib.sha256(b)`.
- No file other than this report was created or modified. The report's own byte size and SHA-256 are printed
  by the agent that wrote it (see the task's completion message).
