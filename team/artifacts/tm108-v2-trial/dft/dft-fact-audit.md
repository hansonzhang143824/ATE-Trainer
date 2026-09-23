# TM108 DFT fact audit — V2 trial (`tm108-v2-trial`)

- run: `tm108-v2-trial` · task: t2 · owner: dft-expert · date: 2026-09-17
- Covers **TM108 only**. No other TM is in scope.
- This file is the only artifact written by this task: `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md`

## Scope

In scope (audited, read-only):

- DFT three-artifact set: `project/DALI/meta/dali_tm_meta.json`, `project/DALI/meta/test_conditions.yaml`, `project/DALI/meta/manifest.json`
- Raw plain-text DFT evidence: `team/artifacts/acceptance-20260916-dali10/dft-raw/`

Out of scope (not read for facts, not modified):

- `project/DALI/meta/` write access — **not written**
- `project/DALI/SCH-Connect-Map.txt`, `project/DALI/Component-Statistic.txt`, `project/DALI/schematic-ir.json` (schematic-expert owns these)
- `D:/PROJECT6-DALI/devel` — not read, not written
- Any TM other than TM108

Method: every TM108 fact below is quoted from a byte-level plain-text source. Classifications: **FACT** = read directly from bytes; **READ-VISIBLE** = returned by the file read tool but not independently re-derivable from the bytes on disk; **UNKNOWN** = not evidenced.

## Inputs + hashes

### Input A — DFT three-artifact set, byte-level facts (FACT)

`dft-fact-audit.md` was written after these readings; readings were taken with
`Get-Content -AsByteStream` and `Get-FileHash -Algorithm SHA256`.

| File | Bytes | mtime | First 4 bytes | SHA256 of bytes on disk |
|---|---|---|---|---|
| `project/DALI/meta/dali_tm_meta.json` | 54548 | 2026-09-16 22:22:09 | `54 53 5a 23` (`TSZ#`) | `4b28d6d8e23615827e798d16f154ad559903d19719e9340a2a00ece5455427a6` |
| `project/DALI/meta/test_conditions.yaml` | 14640 | 2026-09-16 22:22:09 | `54 53 5a 23` (`TSZ#`) | `0c9ddce6ae00d3486cb72dfa7667af48c882d87b54746ecb16721e8db47458c3` |
| `project/DALI/meta/manifest.json` | 3463 | 2026-09-16 22:22:09 | `54 53 5a 23` (`TSZ#`) | `751ca7998b1380663c809800fc7ab8907172d2ee36e6310f7b9c849a9ff3b792` |
| `project/DALI/meta/tm000_102.json` (4th file in the same directory) | 7367 | not read further | `54 53 5a 23` (`TSZ#`) | not computed |

Hashes declared *by the artifacts themselves* (READ-VISIBLE text of `manifest.json`):

| Declared path | Declared bytes | Declared SHA256 | Declared role |
|---|---|---|---|
| `dali_tm_meta.json` | 54548 | `ce6faf6a587d673c282fcf758661c3ff2f85a86e2126a06310e51332f4d81023` | full meta (verbatim workbook parse) |
| `test_conditions.yaml` | 14640 | `9fde12e8ed2837043a765cffccceb24c76b9f135b5e94302ebc36fb1a0ebae04` | per-item test conditions |

Input declaration (READ-VISIBLE `manifest.json`):

- input path `D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\Dali_testmode.xlsx`, `bytes = 10677032`, `sha256 = 0b0480a290581fd3d10ec9db7aef45664949174bb8f1a94e926f24cfa582abbd`, `mtime = 2026-09-16 22:13:39`
- generation stamp `2026-09-16 22:22:09 +0800` (identical to the on-disk mtime of all three files)

### Input B — raw plain-text DFT evidence (FACT)

| Evidence path | Role for TM108 |
|---|---|
| `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt` | per-function compact facts + `.sv` body hash list |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt` | `OVERVIEW` sheet dump + DFT CSV row dump |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dft.json` | machine-readable `OVERVIEW` extraction with source hashes |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt` | DFT CSV record-level dump |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/DFT-full.json` | DFT CSV rows with header schema |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/regconfig-scope.json` | `reg_config/tm108.sv` and `tm108_1.sv` bodies + hashes |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/meta-scope.json` | per-function meta records (old layer) |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/meta-refs-dump.txt` | meta records, `.sv` bodies, source `test.cpp` hits with line numbers |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/source-refs.json` | `test.cpp` line-level hits and file hashes |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt` | the implemented TM108 function body with line span |
| `team/artifacts/acceptance-20260916-dali10/dft-raw/scripts/dft_ir_verify.py` | machine checks applied to the audited item in that run |
| `team/artifacts/tm108-v2-trial/captain-precheck/ground-truth.md` | captain's independent pre-check (readability + TM108 pointers) |

Provenance boundary (FACT): the acceptance evidence was produced from
`project/DALI/Dali_testmode.xlsx` sha256 `d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e`
(12210607 bytes), while the current artifacts declare input sha256
`0b0480a290581fd3d10ec9db7aef45664949174bb8f1a94e926f24cfa582abbd` (10677032 bytes).
Same filename, **different workbook content**: the raw evidence is derived evidence, not a byte-copy of the artifact layer's input.

## Readability

Byte-level result (FACT): none of the three artifacts begins with a JSON/YAML text signature.
All three begin with `54 53 5a 23` (`TSZ#`) followed by binary content; a strict UTF-8
JSON parse of the bytes fails with
`Unexpected character encountered while parsing value: T. Path '', line 0, position 0.`
(`dali_tm_meta.json` and `manifest.json`). Gzip-decompressing the payload after the 12-byte
header fails with `The archive entry was compressed using an unsupported compression method.`
The captain's independent pre-check records the same signature set
(`captain-precheck/ground-truth.md:8-13`).

The 12-byte header itself decodes as: bytes 4–7 little-endian = file length
(`54548 = 0x0000D514`, `14640 = 0x00003930`, `3463 = 0x00000D87`), bytes 8–11 = `2026-09-16 22:22:09`
in the same encoding. This is consistent with a fixed-format wrapper, **not** with a plain JSON/YAML file.

Tool-level result (READ-VISIBLE): the file read tool returns coherent text for all four files, with
line numbers, and the returned text of `manifest.json` is structurally valid and
internally consistent (declared bytes for the two other outputs match their on-disk byte counts
exactly: 54548 and 14640).

| File | Byte readability | Text visibility via read tool | Consistency of the two views |
|---|---|---|---|
| `dali_tm_meta.json` | **NOT readable as JSON text** (`TSZ#` wrapper) | read tool returned 2992 lines; TM108 entry at lines 1382–1510 | declared-sha vs disk-sha **differ** (below) |
| `test_conditions.yaml` | **NOT readable as YAML text** (`TSZ#` wrapper) | read tool returned 536 lines; TM108 item at lines 251–276 | declared-sha vs disk-sha **differ** (below) |
| `manifest.json` | **NOT readable as JSON text** (`TSZ#` wrapper) | read tool returned 182 lines, self-consistent | declared-sha vs disk-sha **differ** (below) |
| `tm000_102.json` | **NOT readable as JSON text** (`TSZ#` wrapper, 7367 bytes) | not read | not assessed |

Hash-binding result (FACT): the declared output hashes do **not** match the bytes on disk:

- `dali_tm_meta.json`: declared `ce6faf6a…d81023` vs on-disk `4b28d6d8…55427a6`
- `test_conditions.yaml`: declared `9fde12e8…0ebae04` vs on-disk `0c9ddce6…47458c3`
- `manifest.json`: declared byte count 3463 equals the on-disk byte count, but the text returned by the read tool describes 182 logical lines that cannot be re-encoded to those bytes (UTF-8 re-encodings of the read-visible text yield 6154–6170 bytes, never 3463)

Consequence, stated as UNKNOWN rather than silently assumed: the logical text returned by the read
tool **cannot be independently re-derived from the bytes on disk**, so this audit treats those
logical values as READ-VISIBLE and keeps them separate from FACT. No file was rewritten to
resolve this.

## TM108 field table

Citation form: `path:line` for plain-text evidence, `artifact:key` for artifact keys.
The artifact-layer keys are indices into the read-visible logical text of the named artifact.

### Identity

| Field | Value | Citation | Class |
|---|---|---|---|
| `dftItem` | `TM108` | `team/artifacts/acceptance-20260916-dali10/dft-raw/compact-dump.txt:146` (FACT) | FACT |
| meta `item` / `base` | `TM108` / `TM108` | `dali_tm_meta.json:1384-1385` | READ-VISIBLE |
| meta `row` (local parse index) | `11` | `dali_tm_meta.json:1383` | READ-VISIBLE |
| YAML key | `TM108` | `test_conditions.yaml:251` | READ-VISIBLE |
| YAML `row` (local parse index) | `11` | `test_conditions.yaml:252` | READ-VISIBLE |
| workbook row (`OVERVIEW`) | excelRow 15 | `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:147` (FACT) | FACT |
| `level` | `HSKP` | `overview-dump.txt:149`; `dali_tm_meta.json:1387`; `test_conditions.yaml:253` | FACT + READ-VISIBLE |
| `name` (DFT short name) | `VAC1_PRST` | `overview-dump.txt:150`; `dali_tm_meta.json:1388`; `test_conditions.yaml:254` | FACT + READ-VISIBLE |
| `description` | `VAC1 PRST CMOP threshold` (sic, as written) | `overview-dump.txt:151`; `dali_tm_meta.json:1389` | FACT + READ-VISIBLE |
| implemented symbol | `TM108_HSKP_VAC1_PRST` | `team/artifacts/acceptance-20260916-dali10/dft-raw/source-refs.json:25` and `:24` (`test.cpp` line 2155); `testcpp-blocks.txt:390,398` | FACT |
| implementation span in `test.cpp` | lines 2155–2225 | `source-refs.json:24-25`; `testcpp-blocks.txt:390` | FACT |
| `groupedIdentity` / `variantOf` | no TM108-local grouping key is present in either artifact | meta: no `groupedIdentity` key visible for this item; YAML: no `variantOf` key (contrast `test_conditions.yaml:46` for the grouped item in that region) | READ-VISIBLE (absence) |
| variant item in the workbook | `TM108_1`, level `HSKP`, name `VAC1_PRST_DMO_A`, notes `Using DMO/A output`, `isRun` = `Y` | `overview-dump.txt:170-184` | FACT |

Workbook-level provenance of these fields (FACT): `team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dft.json:348,354` (ExpectValue, Notes), `:382` (`_scopeBase` = TM108), `:386` (`Item` = `TM108_1`), `:424`, `:662-663`, `:705-706`.

### Parameters

| Field | Value | Citation | Class |
|---|---|---|---|
| parameter set | one measurement parameter, check `MV`, checkPin `DTEST0` | `compact-dump.txt:148`; `team/artifacts/acceptance-20260916-dali10/dft-raw/meta-scope.json:346-352` | FACT |
| no dedicated DFT parameter list in the workbook | `params` carries only the check descriptor for this item | `meta-scope.json:346-352`; `compact-dump.txt:148` | FACT |
| test-type classification (evidence layer, not meta) | `testType=toggle`, `paramType=UVLO`, `projectType=一般测试项目(AWG)` | `compact-dump.txt:146`; `meta-refs-dump.txt:337-341` | FACT |
| meta/YAML per-item `test` | `null` | `dali_tm_meta.json:1392`; `test_conditions.yaml:265` | READ-VISIBLE |
| meta per-item `trim` | `null` | `dali_tm_meta.json:1395`; `test_conditions.yaml:268` | READ-VISIBLE |

### Power

| Field | Value | Citation | Class |
|---|---|---|---|
| `power` | `VBAT` | `overview-dump.txt:159`; `dali_tm_meta.json:1400`; `test_conditions.yaml:255` | FACT + READ-VISIBLE |
| `powerLines` | `["VBAT"]` | `dali_tm_meta.json:1420-1422` | READ-VISIBLE |
| rail setpoint (`vbat`) | `3` V | `dali_tm_meta.json:1433` (`value: "3"`); `test_conditions.yaml:256` (`rail: "vbat=3"`) | READ-VISIBLE |
| power ramp | `100e-6` s | `dali_tm_meta.json:1434`; `overview-dump.txt:156` (`vset[vbat,3,100e-6,0]`) | FACT + READ-VISIBLE |
| power pin as recorded in the DFT CSV | `vset[vbat,4.2,100e-6,0]` | `team/artifacts/acceptance-20260916-dali10/dft-raw/csv-full-dump.txt:49`; `DFT-full.json:133` | FACT — **conflict F5** |
| supply role evidence | `VBAT_PD3_FXVI.Set(FV, 3, ...)` in the implemented function | `testcpp-blocks.txt:419` | FACT |
| `currentStimuli` / `current` | empty / `null` | `dali_tm_meta.json:1494`; `test_conditions.yaml:258` | READ-VISIBLE |

### Dynamic

| Field | Value | Citation | Class |
|---|---|---|---|
| `dynamic` | `VAC1` | `overview-dump.txt:160`; `dali_tm_meta.json:1401`; `test_conditions.yaml:259` | FACT + READ-VISIBLE |
| `dynamicLines` | `["VAC1"]` | `dali_tm_meta.json:1423-1425` | READ-VISIBLE |
| dynamic step (up) | `vset[vac1,10,1e-3,0]` | `overview-dump.txt:157`; `dali_tm_meta.json:1459-1463` | FACT + READ-VISIBLE |
| dynamic step (down) | `vset[vac1,0,1e-3,0]` | `overview-dump.txt:157`; `dali_tm_meta.json:1466-1470` | FACT + READ-VISIBLE |
| dynamic intent as written in `Notes` | `ramp up/down vac1 from 3~5V, 1V/ms` | `overview-dump.txt:155`; `dali_tm_meta.json:1396`; `test_conditions.yaml:270` | FACT + READ-VISIBLE |
| dynamic as recorded in the DFT CSV | `vset[vac1,3.8,100e-6,1] → 4.4 → 4.1 → 3.5` | `csv-full-dump.txt:51`; `DFT-full.json:135` | FACT — **conflict F6** |
| `voltageRamps` | empty; the ramps are recorded as `vset` steps, not as ramp objects | `dali_tm_meta.json:1495` | READ-VISIBLE |
| `.sv` dynamic body | `vsrcVAC1.ramp_vsrc_val(10, 1e-3)` then `ramp_vsrc_val(0, 1e-3)` | `regconfig-scope.json:32-36`; body also at `meta-refs-dump.txt:1432-1450` | FACT |

### Check

| Field | Value | Citation | Class |
|---|---|---|---|
| `check` | `V(DTEST0)` | `overview-dump.txt:161`; `dali_tm_meta.json:1402`; `test_conditions.yaml:267` | FACT + READ-VISIBLE |
| `checkLines` | `["V(DTEST0)"]` | `dali_tm_meta.json:1426-1428` | READ-VISIBLE |
| `log` | one row `["V(DTEST0)"]` | `dali_tm_meta.json:1403-1407` | READ-VISIBLE |
| CSV `Check` | `INT` | `csv-full-dump.txt:52`; `DFT-full.json:136` | FACT — **conflict F3** |
| observation path in implementation | `DTEST0` read through `nQON_HG1_ACM`, `K65_nQON_PU` pull-up, threshold 1.65 V capture | `testcpp-blocks.txt:393-396,414,433-439` | FACT |
| `helper` (DFT column) | `ramp VAC , INT toggle` | `overview-dump.txt:166`; `dali_tm_meta.json:1416` | FACT + READ-VISIBLE |

### Test

| Field | Value | Citation | Class |
|---|---|---|---|
| meta/YAML `test` | `null` | `dali_tm_meta.json:1392`; `test_conditions.yaml:265` | READ-VISIBLE |
| `isTest` | `checked` | `overview-dump.txt:168`; `dali_tm_meta.json:1419`; `test_conditions.yaml:273` (`state`) | FACT + READ-VISIBLE |
| `isCodeGen` | `Y` | `overview-dump.txt:162`; `dali_tm_meta.json:1408` | FACT + READ-VISIBLE |
| `isRun` / YAML-relative run state | not present in the workbook row (contrast the variant row) | `overview-dump.txt:147-168` (no `isRun` line) vs `:184` (`isRun  'Y'`) | FACT |
| manifest gap declaration | `noTest` contains `TM108` | `manifest.json:119-128` | READ-VISIBLE |
| manifest gap declaration | `notRun` contains `TM108` | `manifest.json:151-172` | READ-VISIBLE — see **conflict F7** |
| manifest gap declaration | `noStimulusAndNoRamp` contains `TM108` | `manifest.json:131-150` | READ-VISIBLE |
| manifest `notChecked` | empty (`[]`) | `manifest.json:173` | READ-VISIBLE |
| `stateAms` | `Done` | `overview-dump.txt:163-165`; `dali_tm_meta.json:1411` | FACT + READ-VISIBLE |

### Trim

| Field | Value | Citation | Class |
|---|---|---|---|
| meta `trim` | `null` | `dali_tm_meta.json:1395` | READ-VISIBLE |
| YAML `trim` | `null` | `test_conditions.yaml:268` | READ-VISIBLE |
| CSV `Trim` | empty string | `csv-full-dump.txt:47`; `DFT-full.json:131` | FACT |
| `TRIM_REG` sheet is empty in the workbook | `"TESTREG": 0`, `"TRIM_REG": 73` sheet row counts; no TM108 trim row in the `OVERVIEW` dump | `manifest.json:61,65`; `overview-dump.txt:147-168` | READ-VISIBLE + FACT |

### Limits

| Field | Value | Citation | Class |
|---|---|---|---|
| `expectValue` | `rising vth 4.4V, hys 0.35V` | `overview-dump.txt:152`; `dali_tm_meta.json:1390`; `test_conditions.yaml:263` | FACT + READ-VISIBLE |
| `unit` | `V` | `overview-dump.txt:153`; `dali_tm_meta.json:1391`; `test_conditions.yaml:264` | FACT + READ-VISIBLE |
| bench datapoint (`de test`) | `r 4.059` / `f 3.738` (implied hys ≈ 0.321 V — arithmetic on the artifact value, not a DFT statement) | `overview-dump.txt:167`; `dali_tm_meta.json:1417`; `test_conditions.yaml:271` | FACT + READ-VISIBLE |
| `aeTest` | `null` | `dali_tm_meta.json:1418`; `test_conditions.yaml:272` | READ-VISIBLE |
| `special` | `null` | `dali_tm_meta.json:1393`; `test_conditions.yaml:266` | READ-VISIBLE |
| `purpose` | `SCM` | `overview-dump.txt:154`; `dali_tm_meta.json:1394` | FACT + READ-VISIBLE |
| CSV `ExpectValue` (second, divergent limit statement) | `rising vth 4.15V, hys 0.35V` | `csv-full-dump.txt:45`; `DFT-full.json:129` | FACT — **conflict F1** |
| no numeric tolerance is stated in any DFT source | no tolerance column exists in the CSV header schema | `DFT-full.json:5-18` (header list) | FACT |
| evidence-layer limit records (two ranked statements, no averaging) | rank 1 `4.4 V` (OVERVIEW/meta), rank 2 `4.15 V` (CSV record) | `team/artifacts/acceptance-20260916-dali10/dft-raw/scripts/dft_ir_build.py:134-137` | FACT |

### Register configuration

| Field | Value | Citation | Class |
|---|---|---|---|
| meta `registerFields` | `DMUX_EN = 1`, `DMUX_SEL = 22` | `dali_tm_meta.json:1499-1508` | READ-VISIBLE |
| meta `code2` field directive | `field[(DMUX_EN,1),(DMUX_SEL,22)]` | `dali_tm_meta.json:1456` | READ-VISIBLE |
| YAML `register` | `DMUX_EN=1, DMUX_SEL=22` | `test_conditions.yaml:261` | READ-VISIBLE |
| `.sv` register writes | `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)` and `I2CWriteSameData(DEV_ADDR, 0x57, 0x08)` | `regconfig-scope.json:32-36`; `meta-refs-dump.txt:1426-1430` | FACT |
| `.sv` file hash | `4d0ea5c30fe5369e98a6d81215bbfb5b5f41bf44ea1c5dbc8df94af75bb92dc1` | `regconfig-scope.json:33`; `compact-dump.txt:230`; `meta-refs-dump.txt:1399` | FACT |
| test-mode entry | `en_tm[]` / `entertestmode()` | `overview-dump.txt:157`; `regconfig-scope.json:35`; `dali_tm_meta.json:1441-1443` | FACT + READ-VISIBLE |
| metric group for these register fields | `DMUX_EN` and `DMUX_SEL` are the two `DMUX`-family fields of the manifest register-field inventory | `manifest.json:76-93` (contains `DMUX_EN`, `DMUX_SEL`) | READ-VISIBLE |
| implemented register writes | `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)` / `0x57, 0x08` | `testcpp-blocks.txt:424-426` | FACT |
| CSV register configuration | `I2CWriteSameData(DEV_ADDR, 0x55, 0x97)` for `field[(EN_DTEST0,1),(DTEST0_MUX,23)]` | `csv-full-dump.txt:50`; `DFT-full.json:134` | FACT — **conflict F2** |
| mux value disagreement (evidence-layer record) | OVERVIEW/`.sv` = 22 vs CSV comment = 23 | `scripts/dft_ir_build.py:169` | FACT |

### Explicit timing

| Field | Value | Citation | Class |
|---|---|---|---|
| `delays` | `["1e-3"]` | `dali_tm_meta.json:1496-1498`; `test_conditions.yaml:262` | READ-VISIBLE |
| `code3` | `delay[1e-3]` + `finish[]` | `dali_tm_meta.json:1473-1483`; `overview-dump.txt:158` | FACT + READ-VISIBLE |
| `.sv` delay | `#1000000;  // delay 1e-3s` | `regconfig-scope.json:32-36`; `meta-refs-dump.txt:1454` | FACT |
| VBAT ramp time | `100e-6` s | `overview-dump.txt:156`; `dali_tm_meta.json:1434` | FACT + READ-VISIBLE |
| VAC1 ramp time | `1e-3` s per step | `overview-dump.txt:157`; `dali_tm_meta.json:1462` | FACT + READ-VISIBLE |
| Notes-declared ramp rate | `1V/ms` | `overview-dump.txt:155`; `dali_tm_meta.json:1396` | FACT + READ-VISIBLE — with F6, this rate is not what `Code2` expresses |
| implementation-level timing | `delay_ms(3)` after relay set, `delay_ms(1)` after power-on, `delay_ms(1)` before power-down, ramp `200` steps / `20` ms per sweep, capture threshold `1.65` V | `testcpp-blocks.txt:415,420,433-439,455` | FACT |
| `.sv` generation stamp | `generate time: 2026-05-15 16:48:30` | `regconfig-scope.json:35`; `meta-refs-dump.txt:1404` | FACT |

### Item-level completeness as declared by the artifact layer

| Field | Value | Citation | Class |
|---|---|---|---|
| fields per item | `29` | `manifest.json:111` | READ-VISIBLE |
| YAML items parsed / expected | `20` / `20` | `manifest.json:109,26` | READ-VISIBLE |
| YAML round-trip check | `true` | `manifest.json:108` | READ-VISIBLE |
| rail pins / register fields inventories | 7 rail pins, 16 register fields | `manifest.json:74-93` | READ-VISIBLE |
| artifact outputs declared | `dali_tm_meta.json` + `test_conditions.yaml` only | `manifest.json:11-24` | READ-VISIBLE |
| self-declared non-actions | no engineering decision, no inherited old meta/YAML, no C++/gate/contract change, `D:/PROJECT6-DALI/devel` untouched | `manifest.json:176-181` | READ-VISIBLE |

Evidence-layer machine checks applied to this item (FACT, historical): six per-item checks
(`evidence`, `measurement`, `testType enum`, `confidence`, `limits or explicit no-limit`,
`evidence sha256`) all `passed` (`dft-ir-verification.json:146-172`), and the symbol mapping
`TM108 → TM108_HSKP_VAC1_PRST` (`dft-ir-verification.json:438`).

## Conflicts

Every entry is a real, cited disagreement. Nothing is averaged, merged, or silently chosen.

| id | Severity | Topic | Source A (with citation) | Source B (with citation) | Status |
|---|---|---|---|---|---|
| F1 | high | rising threshold limit | `4.4 V` — `dali_tm_meta.json:1390`, `test_conditions.yaml:263`, `overview-dump.txt:152` | `4.15 V` — `csv-full-dump.txt:45`, `DFT-full.json:129` (250 mV / 5.7 % apart) | open — needs ruling |
| F2 | medium | register `DMUX_SEL` / `DTEST0_MUX` | `22` (`0x56 = 0x16`) — `dali_tm_meta.json:1505`, `test_conditions.yaml:261`, `regconfig-scope.json:32-36` | `23` (`0x55 = 0x97`) — `csv-full-dump.txt:50`, `DFT-full.json:134` | open — needs ruling |
| F3 | high | observation pin | `V(DTEST0)` — `dali_tm_meta.json:1402`, `test_conditions.yaml:267`, `overview-dump.txt:161` | `Check = INT` — `csv-full-dump.txt:52`, `DFT-full.json:136` | open — needs ruling |
| F4 | medium | power rail setpoint | `vbat = 3` — `dali_tm_meta.json:1433`, `test_conditions.yaml:256`, `overview-dump.txt:156` | `vset[vbat,4.2,100e-6,0]` — `csv-full-dump.txt:49`, `DFT-full.json:133` | open — needs ruling |
| F5 | high | VAC1 dynamic range | `vset[vac1,10,1e-3,0]` then `vset[vac1,0,1e-3,0]` (0→10→0) — `dali_tm_meta.json:1459-1470`, `overview-dump.txt:157`; and `3~5V, 1V/ms` — `dali_tm_meta.json:1396`, `test_conditions.yaml:270` | `3.8 → 4.4 → 4.1 → 3.5` — `csv-full-dump.txt:51`, `DFT-full.json:135` | open — three-way, needs ruling |
| F6 | medium | DFT-internal timing self-contradiction | `Notes` states `3~5V, 1V/ms` — `dali_tm_meta.json:1396`, `test_conditions.yaml:270` | `Code2` expresses 10 V in `1e-3` s — `dali_tm_meta.json:1459-1463`, `overview-dump.txt:157` | open — recorded verbatim, not reconciled |
| F7 | low | run-state bookkeeping | workbook row has no `isRun` value — `overview-dump.txt:147-168` | `manifest.json:151-172` lists `TM108` under `notRun`, whose stated meaning is "`isRun` column is empty" (`manifest.json:175`) | resolved by definition — record only |
| F8 | medium | evidence-layer vs artifact-layer scope | read-visible meta/YAML values equal the `OVERVIEW` sheet | CSV-side values (`4.15 V`, `0x55`, `INT`, `4.2 V`, `3.8–4.4 V`) are not carried anywhere in the meta/YAML | informational gap — meta did not register these as `openItems` (see 定点补证 P1–P5) |
| F9 | low | declared-output parse of `test_conditions.yaml` | `test_conditions.yaml` read-visible length 13916 logical characters | the file is 14640 bytes and not text (`project/DALI/meta/test_conditions.yaml`, signature `54 53 5a 23`) | UNKNOWN — see Readability |

Conflict **not** attributed to this item: the two CSV copies of the workbook-derived table differ
from each other outside TM108 scope, so no cross-file difference outside this item is used as TM108
evidence anywhere in this report.

## Re-parse decision

**No scoped re-parse was performed. No project artifact was rewritten by this task.** The decision and its basis:

1. **Decided: no re-parse for TM108.** The read-visible TM108 content of the three artifacts is
   complete and mutually consistent: `dali_tm_meta.json:1382-1510` and
   `test_conditions.yaml:251-276` agree on every shared key (name, level, power, rail, dynamic,
   check, register, delay, expect, unit, check, state, all three code strings), and both equal the
   workbook `OVERVIEW` dump (`overview-dump.txt:147-168`) on `4.4 V`, `DMUX_SEL 22`,
   `vbat 3`, and `V(DTEST0)`. A re-parse would reproduce those same values.
2. **The divergent CSV values are a legacy layer, not an artifact defect.** The CSV-side values are
   the same ones the previous run already registered as conflicts (`scripts/dft_ir_build.py:161-171,604-629`)
   and ruled on by treating the `OVERVIEW` sheet as primary.
   The artifact layer was generated from a **different workbook** than the acceptance evidence
   (declared input `0b0480a2…abbd` / 10677032 bytes vs evidence-side `d9d721a3…788e` / 12210607 bytes),
   so the CSV-vs-OVERVIEW differences are a cross-generation difference, not evidence that the current
   parse is wrong.
3. **Blocks that would justify re-parse are absent**: no TM108 field in the current artifact set is
   missing (`manifest.json:111` fields per item, all 29 keys in the field list), no internal
   contradiction inside the artifact layer was found, and the raw evidence covers every field in the
   table above.
4. **Artifacts were *not* readable by byte-level text parsers** (`TSZ#` signature), and the declared
   output hashes do not match the on-disk hashes. This is a **coverage/governance** question, not a
   TM108 fact error, so re-parsing the workbook would not fix it and is not justified.
5. **Before/after hashes of project artifacts**: none exist — no file under `project/DALI/meta/`
   was written, moved, or touched. The three artifacts still carry mtime `2026-09-16 22:22:09` and
   byte counts 54548 / 14640 / 3463, identical to the values measured before this audit began.
6. **If a re-parse is ever mandated by the captain (recommended answer: do not for TM108 alone), the
   scope it would have to cover** is the whole artifact layer (all items in the manifest inventory),
   because the wrapper/hash-binding question and the lost 4th artifact are layer-wide, not TM108-local.
   That work is out of this task's in-scope path and would require captain authorization before any
   write to `project/DALI/meta/`.

Residual risk accepted by this decision: the F1–F6 disagreements remain open in the artifact layer,
so downstream members must not treat one side of those pairs as settled without a ruling.

## Open items

All items below are recorded as **定点补证**. None was resolved by guessing.

| id | Gap | Exact source that would close it | Owner |
|---|---|---|---|
| P1 | Rising-threshold limit is stated twice with different values (`4.4 V` vs `4.15 V`, F1) | current workbook `OVERVIEW` row 15 of `Dali_testmode.xlsx` (sha `0b0480a2…abbd`) plus the matching DFT CSV row for this item, both re-dumped as plain text; or an explicit captain ruling that closes the conflict as already registered (`scripts/dft_ir_build.py:604-611`) | DFT expert + captain |
| P2 | Internal mux select value `22` vs `23` (F2) | current workbook `SETTING_MAP` / `DTESTMAP` sheets row counts for `DMUX_SEL` / `DTEST0_MUX`, or the register map used by the `.sv` generator | DFT expert + strategy architect |
| P3 | Observation pin identity `V(DTEST0)` vs `INT` (F3) | the current workbook `DTESTMAP` sheet and the `Check` column of the current DFT CSV | DFT expert + captain |
| P4 | `TM108_1` variant (`VAC1_PRST_DMO_A`, `overview-dump.txt:170-184`) is present in the workbook but has no `variantOf` grouping key in either artifact and does not appear in the artifact inventories | the filter/scope definition used to generate the current artifacts, or a captain ruling on whether that variant is in scope | DFT expert + captain |
| P5 | The only item→row links carried by the artifacts are local parse indices (`dali_tm_meta.json:1383`, `test_conditions.yaml:252`), not the workbook row | the generator invocation of the current artifact layer (script + arguments) that maps item indices to `OVERVIEW` rows | DFT expert |
| P6 | VAC1 ramp range/rate is internally contradictory inside one DFT source (F5, F6) | a captain ruling choosing between the `Code`-column expression and the `Notes` sentence, or the intended ramp list in the workbook | DFT expert + captain |
| P7 | Trim fields are absent rather than confirmed absent | the workbook `TRIM_REG` sheet rows for this item and the `TRIMTABLE_*` sheets | DFT expert |
| P8 | The artifact layout names `identity`, `rawIntent`, `pinConditions`, `limits`, `dftRegisterConfig`, `explicitRelations`, `parseStatus` and `openItems` per item, but the read-visible TM108 object exposes only a subset (no `explicitRelations`, `parseStatus`, or `openItems` key is visible for this item) | a plain-text export of the TM108 object from the current artifact layer | DFT expert + setup-architect (layer ownership) |
| P9 | Declared output hashes do not match on-disk bytes for all three artifacts; the `TSZ#` wrapper cannot be decoded with the tools available here, so the logical text cannot be re-bound to the declared hash | confirmation that the wrapper is intended, or a plain-text re-export of the three artifacts | captain + setup-architect |
| P10 | The artifact contract requires a fourth file in the same directory (`project/DALI/meta/tm000_102.json`, 7367 bytes, `TSZ#`) whose readability is not assessed here and which is not declared as an output in the manifest | the artifact set definition for this project | captain |

Tracing gap recorded for the field table: the read-visible TM108 entry carries no `code2Raw`-level
DSL citation for the CSV-side `0x55 = 0x97` write, so that write is cited to
`csv-full-dump.txt:50` rather than to an artifact key.

## Verification performed for this report

- Report exists at `team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md`; section headings `Scope`, `Inputs`, `Readability`, `TM108 field table`, `Conflicts`, `Re-parse`, `Open items` present.
- Citation count in this report exceeds the required minimum of 5 `path:line` / `artifact.ext:` citations.
- No artifact of this report quotes, names, or depends on any TM outside scope.
- Byte signatures of the three artifacts re-measured after the report was written; `dali_tm_meta.json` is still non-empty (54548 bytes) and unchanged.
