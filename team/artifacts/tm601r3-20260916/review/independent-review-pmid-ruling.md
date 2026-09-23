# Independent adversarial review — "Ruling A1: TM600 (HS_RDSON) PMID = 5 V"

- Reviewer role: independent adversarial reviewer (read-only). Exactly one file was written: this report.
- Workspace: `D:\Newtest\DSH\ATE-Coding-Plat`; deployed tree read-only at `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` (never modified). `D:/PROJECT6-DALI/devel` was not touched.
- Method: python byte-mode reads (openpyxl for the workbook; `open(path,'rb')` for text) because PowerShell `Get-Content`/`Get-FileHash` may return DLP/TSZ ciphertext inside the run directory (contract `integrityNotes`).
- Evidence tags used throughout: **FACT** (verbatim source I read, with file:line), **INFERENCE** (my reasoning over facts), **UNKNOWN** (not resolvable with the evidence available here).

---

## 1. VERDICT

**DISAGREE — with Ruling A1 as written. Do not implement it in its current form.**

- I disagree with (i) the stated rationale, which is a non-sequitur, and (ii) the scope of the ruling, which changes one field of a four-field coupled divergence and, if applied literally, is the *most dangerous* of the available actions.
- I do **not** claim PMID = 15 V is correct. The evidence I found actually points the other way for the operating point (see §6, the pro-5 V findings). The ruling is unsound as *reasoning and as an implementation instruction*, not necessarily wrong in *direction*.
- If the four conditions in §8 were met, my verdict would become **AGREE-WITH-CONDITIONS**. Until then it is **DISAGREE**.

---

## 2. What the conflicting sources actually say (FACT)

### 2.1 The workbook (claimed sole authority)
`project/DALI/Dali_testmode.xlsx`, sheet `OVERVIEW`, row 1 = header (`A1=Item … L1=Code1 … O1=Power … Q1=Check … AH1=de test`).
Row 132 = TM600 (FACT, read with openpyxl):

| Cell | Value |
|---|---|
| E132 / F132 | `11` / `mΩ` |
| K132 | `Rds,on=(PMID-SW)/ISW` |
| L132 (`Code1`) | `vset[vbat,3.5,100e-6,0]` / `vset[pmid,5,100e-6,0]` / `vset[bst_sw,5,1e-3,0]` / `vset[vdrv,5,100e-6,0]` |
| N132 (`Code3`) | `delay[1e-3]` / **`iset[sw,1,1e-3,0]`** / `delay[2e-3]` / `finish[]` |
| O132 (`Power`) | `VBAT` / `BST-SW` |
| Q132 (`Check`) | `PMID-SW` / `floating source：V(BST_SW)` |
| AH132 (`de test`) | `I=0.2A` / `pmid-sw=46mV` |

Row 133 = TM601: L133 = `vset[vbat,3.5,…]`, `vset[vdrv,5,…]`, `vset[vbus,5,…]`, `vset[bst,5,100e-6,0]`; E133 = `7.5 mΩ`; N133 = `iset[pmid_sw,1,1e-3,0]` (FACT).

Plaintext sha256 of the workbook = `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564`, 12,210,680 bytes, mtime 2026-09-16 21:46:39 (FACT, python).

### 2.2 The other DFT — `project/DALI/input/DFT.csv` (record for TM600, csv-parsed)
`Item=TM600, Function Name=RDSON_TEST, ShortName=HS_RDSON, ExpectValue=10, Unit=mohm, Hardware_initial = "vset[vbat,4.2,100e-6,0]\nvset[pmid,15,100e-6,0]\nvset[bst2sw,5,1e-3,0]\nvset[vdrv,5,100e-6,0]", Dynamic = "iset[pmid2sw,1,1e-3,0]", Check = "PMID-SW", Type = "MV&MI"` (FACT). TM601: `vset[pmid,9,…]`, `ExpectValue=8 mΩ`, `Dynamic=iset[sw2pgnd,1,1e-6,0]`, `Check=PGND-SW` (FACT).
sha256 = `b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4` — **equal to the sha the frozen contract recorded as an input**, so DFT.csv did not change during the run (FACT: contract `integrityNotes.frozenAuthorities`).

### 2.3 `knowledge/hardware/voltage-inference.md`
`18: PMID_FOVI.Set(FV, 15) → PMID = 15V`; `121: 示例: VBAT=4.2, VDRV=5, SW=0, PMID=15, BST=20`; `127-128: PMID=15 (A) → SW跳变=15 … BST=20 (A) → BST-SW=20-15=5V ✓`; `142-143: DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5] / iset[pmid2sw,1A]`; `151-160` the phase table (FACT, read lines 1-178).

**FACT (important):** lines 142-143 of that document are a *verbatim transcription of DFT.csv's TM600 record* (`vbat 4.2 / pmid 15 / bst2sw 5 / vdrv 5 / iset[pmid2sw,1A]`), not an independent authority. **INFERENCE:** therefore `voltage-inference.md` is downstream of DFT.csv; relabelling the markdown as "historical" does **not** retire the 15 V reading, because the 15 V reading still lives in `DFT.csv`, a run input that the frozen contract itself cites as authority (see §2.4).

### 2.4 What the frozen contract cites
`team/artifacts/tm601r3-20260916/snapshot/setup_contract.json` (FACT, read with python):
- `:1429` bst2sw firstSource = `"project/DALI/input/DFT.csv line 92: vset[bst2sw,5,1e-3,0]"` with sha `b92d203f…`;
- `:963` pmid2sw firstSource = `"DFT.csv line 97: iset[pmid2sw,1,1e-3,0] -> PMID-SW, Check=MV&MI"`;
- `:1422` bst2sw `usedByTm = ["TM600 (BST must lead PMID)"]`;
- `:1435-1439` `forceInstrument = SW12_U1REF_BST_ACM` (ground-referenced ACM200, S5_5) and `"SW12_U1REF_BST_ACM is ground-referenced, so the BST-SW differential is set by the ACM output level"`;
- `:1443-1463` bst2sw relayChain SetOn = **K48, K76** (ACM200 S5_FH5 → BST) + **K60, K61** (SW end) — i.e. closed-relay set `[48,60,61,76]`;
- `:1515-1520` evidence for that: `SCH-Connect-Map.txt:672 (BST [Kelvin] needs-closed K48,K76)`, `:673/674`, `IR required_on=[48,76]`, and `test.cpp:7000/7087/7170/7513 (deployed SetOn closes K48 + K76)`;
- `:1436` `bstRuling_ii`: the FPVIe1 CH1 differential BST–SW form is rejected as "intended but currently unrealisable";
- `:1047`: `"FPVIe1 is the only remaining channel and is allocated to BST<->SW 5V for the same TM600 item"`.
**INFERENCE:** the contract's own sense-path authority for TM600 is DFT.csv-derived, and it explicitly fixes the BST–SW implementation as *ground-referenced ACM absolute* output.

### 2.5 Schematic — what the ACM pin physically reaches
`project/DALI/SCH-Connect-Map.txt` (FACT):
- `:672-674` `BST [Kelvin] 需闭合: K48,K76` / `F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F` / `S: S5_ACM200_SH5 -> … -> BST_S`;
- `:165-167` `CH0 High -> PMID 需闭合: K83`; `:174-176` `CH0 Low -> SW 需闭合: K60,K61`;
- `:904` `SW 稳压 Cap_SW_BST_S1 C=220nF 需闭合: K57`;
- `:39-41` FPVIe0 CH0 High → BST needs `K46,K48,K76`;
- `:461-462` `BST ← S10_CH0_A 通路 需闭合: K141,K46,K48,K76`.
`SW12_U1REF_BST_ACM` is the ACM200 channel at `S5_5` (FACT: `backup\D__test_method__dali_strays\COMPONENT-STATISTIC.txt:113 "S11_5 -> SW12_U1REF_BST_ACM (ACM200)"`; the macro expands to `'S5_5,S6_5,S11_5,…'`, contract `:1435`).

### 2.6 Register-config stimulus deck
`project/DALI/reg_config/tm600.sv:6-25` (FACT): `vsrcVBAT.ramp_vsrc_val(3.5, 100e-6)` with comment `// vset[vbat,3.5,100e-6,0]`; `vsrcPMID.ramp_vsrc_val(5, 100e-6)` with `// vset[pmid,5,100e-6,0]`; `vsrcBST_SW.ramp_vsrc_val(5, 1e-3)` with `// vset[bst_sw,5,1e-3,0]`; `vsrcVDRV…(5, 100e-6)` with `// vset[vdrv,5,100e-6,0]`. **FACT:** the deck mirrors the workbook's L132 numbers exactly, including `bst_sw` naming. This is *not* an independent third witness; it is the same numbers expressed in an AMS deck.

### 2.7 Provenance of the "modified workbook" premise (new evidence, contradicts the premise)
`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dft.json` (generated 2026-09-16 13:43:58, i.e. **before** the workbook's 21:46:39 mtime) records the workbook sha as `d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e`, **different** from the current `f4bbb856…` (FACT) — so the workbook *was* modified at ~21:46.
The same JSON shows that at 13:43 TM600 already had `ExpectValue=11`, `Unit=mΩ`, `Code1` with `vset[pmid,5,…]` + `vset[bst_sw,5,1e-3,0]`, and `de test = "I=0.2A\npmid-sw=46mV"` (FACT). TM601's 13:43 `Code1` had only `vbat 3.5 / vdrv 5 / vbus 5` — **no `vset[bst,…]`**, whereas the current L133 has `vset[bst,5,100e-6,0]` (FACT).
**INFERENCE:** the 21:46 edit did **not** introduce PMID = 5 V for TM600 (it was already there); the visible delta is at least TM601's added `vset[bst,5,…]`. So "the user modified the workbook, therefore the user newly ruled PMID = 5 V" is **not supported by the available evidence**.

---

## 3. Attack question (a) — does `Rds,on=(PMID-SW)/ISW` still hold, and is 5 V vs 15 V discriminated?

- Expected sense voltage, 11 mΩ at 1 A = **11 mV** (FACT/arithmetic). Workbook's own datum: 46 mV at 0.2 A = **230 mΩ** (arithmetic over FACT AH132) — i.e. ≈21× the E132 = 11 mΩ limit, whereas 11 mΩ at 0.2 A would be 2.2 mV. **INFERENCE:** the workbook's only measured datum is internally inconsistent with its own limit by ~21×; whichever reading is authoritative, the workbook is not self-verifying on this point, and the ruling cites only the self-consistency of the *differential* rail.
- FPVIe sense chain (FACT, `knowledge/sources/raw/hw_specs_extract.txt`): `X10 amplifier`, `±1V: resolution 0.003mV, accuracy ±(0.175mV + 0.050% Rdg)` (`:1355-1357`); `±100mV: 0.305µV, ±(0.125mV + 0.400% Rdg)` (`:1358-1360`); `FPVIe_100MV can only be used for measurement, NOT for output` (`knowledge/sources/fpvie.md:59-60`). At 11 mV on ±1 V/X10 → ±0.18 mV ⇒ **±1.6 %** of reading; the deployed payload already asks for this gain (`FPVIe_MV_X10`, test.cpp:9146).
- BST rail source accuracy (FACT, ACM200 table `hw_specs_extract.txt:1044-1060`): `±10V: 0.381mV, ±(1.5mV + 0.025% Rdg)`; `±20V: 0.762mV, ±(3mV + 0.025%)`; `±40V: 1.524mV, ±(6mV + 0.025%)`.
  - 5 V world: PMID 5 V on FXVIe_PLUS `±10V` (`±(2mV+0.025%)`, `:450-452`) + BST_abs 10 V on ACM `±10V` → BST−SW ≈ 5 V ± ~4 mV.
  - 15 V world: PMID 15 V on `±30V` (`±(6mV+0.025%)`, `:444-446`) + BST_abs 20 V on ACM `±40V` → BST−SW ≈ 5 V ± ~21 mV.
- **Answer:** the equation holds in both worlds, and **resolution does not discriminate them**. The FPVIe measures the drop *differentially across its own force terminals*, so the absolute PMID value cancels; 11 mV is resolvable with X10 in either case. Question (a) therefore provides **no support** for the ruling's rationale, and it also removes one of the possible arguments against it — i.e. it is simply not a discriminator. **UNKNOWN:** whether "Rdg" in the FPVIe accuracy tables is the reading or the range; if it were the range, X10/±1 V would be ±0.5 mV ⇒ ±4.5 % on 11 mV, which would matter for any Rds,on measurement here (both readings equally).

## 4. Attack question (b) — does `vset[pmid,…]` force, or program a comparison target?

- **FACT:** `knowledge/standards/units.md:70-73` — `| DFT指令 | 模式 | | vset[...] | FV | Force Voltage | | iset[...] | FI | Force Current |`; `:74` `测量MV但无FI配置 → FI=0`.
- **FACT:** there is no `vset`/`iset` runtime API anywhere in the VS tree. In the whole `source/` directory only `test.cpp` contains the tokens (298 hits), and **all 235 lines that contain `vset[`/`iset[` are comments** (`// vset[vbat,4.4,100e-6,0] → VBAT=4.4V FV`, test.cpp:1375); count of bare `vset(`/`iset(` calls = 0. The translation is hand-written.
- **FACT:** the deployed translation of `vset[pmid,15]` is a real force: `PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_30V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON)` (test.cpp:9112); FV/FI modes and clamp semantics are documented in `knowledge/sources/fpvie.md:55-56, 141-168`.
- **Answer:** `vset[…]` commands a **low-impedance FV force** (with a programmable compliance clamp), not a comparison/target. No comparison-target mechanism exists in this codebase. **UNKNOWN:** the DFT tool's own specification of `vset[pin,val,ramp,0]` and of the `floating source:` annotation is **not present in this workspace**, so the FV mapping rests on the project standard plus hand translation, not on a primary tool manual.
- **Collateral finding (does not discriminate the ruling but must be resolved):** under the DFT.csv topology the FPVIe forces 1 A across PMID↔SW while a *second* source also drives PMID at FV with only a `FXVIe_PLUS_100MA` current range (test.cpp:9112 vs 9140). **UNKNOWN:** whether FV+FI on one node can coexist during the 1 A pulse, or whether the 100 mA range clamps. The deployed TM640 does the same (`:7524` PMID 5 V/100 mA, `:7550` FPVI0 FI), so it may be intentional, but no manual or bench evidence in the workspace settles it.

## 5. Attack question (c) — what node does `SW12_U1REF_BST_ACM` actually tie to?

- **FACT:** `SCH-Connect-Map.txt:672-674` — the ACM200 channel at `S5_ACM200_FH5/SH5` (= `SW12_U1REF_BST_ACM`, `S5_5`) reaches **BST_F / BST_S** only via `K48(Relay-ON) -> K76(Relay-ON)`. It is therefore a **ground-referenced BST** output; it does **not** tie to SW.
- **FACT:** the contract agrees (`:1435`, `:1439`, `:1443-1463`) and names the relay set `[48,60,61,76]`.
- **INFERENCE (decisive for the ruling's wording):** with a ground-referenced BST source, "BST−SW = 5 V" requires **BST_abs = SW + 5 V**, i.e. **10 V** when PMID = SW = 5 V (11 mV below it, to be exact). Setting the ACM to `5` while PMID = 5 V yields BST−SW = **0 V**.
- **FACT — the deployed sibling proves the convention:** `TM640_BOOST_HS_OCP` closes `K48_ACM5_AMP_REF + K76_ACM_BST` (test.cpp:7513), drives `SW12_U1REF_BST_ACM.Set(FV, 5, …)` with PMID/SW = 0 (`:7521`, comment `PMID=SW=0V, BST-SW=5V`), then `Set(FV, 10, …)` after `PMID_HG2_FXVI.Set(FV, 5, …)` (`:7524-7526`, comment `SW=5V, BST-SW=5V`), and on power-down `Set(FV, 5)` is annotated `BST-SW: 5V→0V` (`:7566`). That is absolute-voltage semantics, confirmed by the power-down annotation.
- **FACT — the deployed TM600 does not close the BST leg:** its SetOn is `K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` (test.cpp:9081) — **no K48, no K76**, although the same file's TM640/TM609/TM608 HS functions do close them (`:7513`, `:7169`) and `:7000/7087/7170`. Its own header asserts the opposite of the connect map: `"ACM200 reaches SW only and cannot reach BST"` (test.cpp:9027-9028).
- **INFERENCE:** the 20 V BST staircase (test.cpp:9097-9115) is at best **unproven to reach the BST pin**, while the contract requires K48+K76 for exactly this alias. If K48/K76 really must be closed (map says `需闭合`), then in the current code BST−SW ≈ 0/−Vf, the HS FET is not enhanced, and *the entire PMID debate is moot until that is fixed*.
- **Answer to (c):** yes, the ACM channel can establish BST−SW = 5 V, but **only as an absolute level = PMID + 5 V (10 V for the 5 V world)**, and only when K48+K76 are closed. The claim in the recommendation that "BST_SW = 5 V" is therefore safe only if read as a *differential*; read as an absolute ACM setpoint it is wrong and would break the test. **UNKNOWN:** the default (un-actuated) state of K48 and K76 — no relay-default authority for those two relays was found in what I read; the map's `需闭合`/`Relay-ON` notation implies they are normally open to BST, and the sibling code closes them, but I could not read a definitive default-state table entry.

## 6. Attack question (d) — deployed precedent for a high-side BST test with PMID ≠ 15 V

**Yes — PMID = 5 V is the deployed norm for this BUBO high-side family; the deployed TM600's 15 V is the outlier.** (All FACT, test.cpp, names + line numbers.)

| Function | PMID | BST source value | K48/K76 | Evidence |
|---|---|---|---|---|
| `TM640_BOOST_HS_OCP` (:7503) | **5 V** (`PMID_HG2_FXVI.Set(FV, 5, …)`, comment `PMID=5V, SW 跟随到 5V`) | `SW12_U1REF_BST_ACM` **10 V** (=SW+5) | **closed** (7513) | 7513, 7517 (`DFT: vbat=3.5V pmid=5V bst_sw=5V vdrv=5V`), 7521-7526, 7566 |
| `TM609_BOOST_HS_NEG` (:7160) | `FPVI0 FV=0 … // PMID=SW=5V` | `SW12_U1REF_BST_ACM (K48+K76)` | closed | 7169, 7174, 7216 |
| `TM608_BOOST_HS_ZCD` (:7073) | `FPVI0 FV=0 … // PMID=SW=5V` | family pattern | (7000/7087 cite K48+K76) | 7091, 7130 |
| `TM643_VBAT_LOOP_INDICTOR` (:7717) | comment `vbat=5V pmid=5V bst_sw=5V(差分) vdrv=5V` | floating differential (`BST_SW 浮动差分源`) | — | 7731, 7738 |
| `TM600_HS_RDSON` (:9057) | **15 V** | ACM **20 V** | **not closed** | 9081, 9086-9087, 9097-9115 |

Limits worth stating precisely: these precedents establish the **5 V operating point** (and its correct absolute-BST translation) for BUBO high-side items, but **none of them is an Rds,on measurement with a 1 A force**. There is **no deployed precedent for a 1 A high-side RDSON at PMID = 5 V** (UNKNOWN/absence of evidence, not evidence of absence).
The other side of the record is the archived golden, which is a 15 V/20 V arrangement: `knowledge/references/L4-Golden-code/Rdson.cpp:58-67` (`BST=20V … PMID=15V (BST-PMID=5V ✓)`, `FET导通后SW→PMID≈15V, BST-SW=20-15=5V ✓`) with `FPVI.Set(FI, 1, …)` and `delay_us(2000)` at `:85-87`. **INFERENCE:** the 15 V reading is not merely a documentation artifact; it is also the archived golden's operating point, which is presumably why the implementer chose it.

## 7. Attack question (e) — what concretely breaks, in each direction

Ordered by severity; each item states its evidence class.

1. **Literal/partial application of the ruling (HIGH, damage-class).** Change only `vset[pmid]` to 5 V and leave the synchronized BST staircase (`SW12_U1REF_BST_ACM` 0→5→10→15→**20** V, test.cpp:9104-9115; PMID steps 0→5→10→15, `:9102-9112`). Then at the last step BST_abs = 20 V with SW ≈ 5 V ⇒ **BST−SW ≈ 15 V**. The project's own BST–SW guidance puts the differential absolute maximum in the ~5 V–6 V class (`docs/BST-SW通用知识介绍.txt`: "绝对最大值 … 例如不超过5.5V"; workbook `ABS` rows M44/M50 use `BST1-SW1=6V` as the applied condition) — FACT for the quoted text, INFERENCE for the DUT's exact limit: **the DUT datasheet is not in the workspace**, so the exact abs-max is UNKNOWN, but 15 V is ~3× the 5 V operating differential and in the over-drive direction. Effects: gate over-stress; HS FET over-enhanced → Rds,on reads **low (optimistic pass)**.
2. **Naive absolute reading of "BST = 5 V" (HIGH, false-fail-class).** Set the ground-referenced ACM to 5 V while PMID = SW = 5 V ⇒ BST−SW = 0 V (−Vf). HS FET off ⇒ the 1 A force is pushed through body diode/parasitics; the sensed |V(PMID−SW)| rises far beyond the deployed `SetClamp(50,50)` = 50 % × 1 V = **0.5 V** compliance. The payload itself documents this: `max measurable RDSON = 500 mohm`, clamp engagement "is a FAILURE SIGNATURE, not a measurement result" (test.cpp:9011-9016), and the division guard reports `ERROR_RES` (9999) when the current collapses (test.cpp:9154-9169). Result: 100 % of sites false-fail; the bootstrap-leading invariant (contract: BST must lead PMID / BST−SW ≥ −Vf) is violated.
3. **Limit-comparison incoherence (MEDIUM–HIGH, correctness-class).** The 11 mΩ limit and PMID 5 V come from the *same workbook row*; DFT.csv pairs **10 mΩ with 15 V** (FACT: DFT.csv TM600 `ExpectValue=10`; and the deployed header states it explicitly: *"the archived revision pairs 11/7.5 mohm with pmid 5 V, while DFT.csv pairs 10/8 mohm with pmid 15/9 V"*, test.cpp:9035-9037). The deployed code therefore cross-pairs (workbook limit + DFT.csv excitation) — and the ruling fixes only half of that pair. Note the workbook's own limit is *not* corroborated by its own datum (46 mV @ 0.2 A ⇒ 230 mΩ, §3). No pass/fail conclusion can be trusted while the limit's qualifying operating point is unknown.
4. **Sense-amplifier range (LOW — not a discriminator).** 11 mV with X10/±1 V: ±0.18 mV ⇒ ±1.6 %; ±0.031 mV resolution-equivalent is far below the signal. The differential measurement cancels PMID's absolute value. Nothing breaks here in either world (FACT-based, §3).
5. **DUT not enhanced / mode not representative (MEDIUM, condition-class).** The AMS-validated condition for TM600 is vbat 3.5 / pmid 5 (`reg_config/tm600.sv`), and workbook `State AMS Validation = Done` (FACT). Running at PMID 15 / VBAT 4.2 (the status quo) exercises a condition that no AMS/bench evidence in the workspace covers for this item; conversely, if 15 V were the bench-qualified condition, a 5 V run is equally unqualified. Which direction is *wrong* is **UNKNOWN** without DUT/bench data.
6. **Damage risk if the truth were 5 V and 15 V is kept (LOW).** Workbook `ABS` bounds: `M29 'PMID=22V'`, `M30 '…BST=28V…'` ⇒ 15 V/20 V is inside the absolute-max envelope (FACT). So the status quo is the *harsher but envelope-compliant* direction; the 5 V direction is physically gentler but is the one that can collapse BST−SW if implemented partially. **5 V is not automatically the "safe" choice.**
7. **Unresolved in both worlds (MEDIUM).** The FXVIe FV source on PMID with a 100 mA range in parallel with the FPVIe's 1 A force (test.cpp:9112 vs 9140) — see §10 U-E.

## 8. Strongest counter-argument, and what would settle it

**Strongest counter-argument (as found):** *Ruling A1 rests on a non-sequitur and on an incomplete authority base, and it is not isolatable.*

- The rationale ("`Check = 'PMID-SW' + floating source: V(BST_SW)` is self-consistent with BST−SW = 5 V") is satisfied by **both** worlds (15/20 and 5/10 give the same differential); it therefore contains **zero** information about PMID's absolute value. (FACT + arithmetic, §3.)
- "Label lines 18/142-143/151-160 as historical" does not retire the 15 V reading: those lines transcribe **DFT.csv**, and DFT.csv is a frozen run input whose sha the contract pins as the authority for `bst2sw` (line 92) and `pmid2sw` (line 97) — the very aliases that define TM600's relay topology. (FACT: voltage-inference.md:142-143 vs DFT.csv record; contract:1429-1430, :963.)
- The workbook and DFT.csv differ in **four coupled fields** for TM600: PMID (5/15), VBAT (3.5/4.2), the current-command form (`iset[sw,1,1e-3,0]` vs `iset[pmid2sw,1,1e-3,0]`, i.e. single-ended sink at SW vs the floating loop the contract resolved to FPVIe0 FHSH0/FLSL0), and the limit (11/10 mΩ). Adopting PMID alone yields a configuration that appears in **no** source document; adopting the workbook record faithfully changes the measurement topology and therefore invalidates the contract's `pmid2sw` alias resolution and part of the relay plan.
- The premise that the modification carried the PMID=5 V intent is false on the evidence I have: a 13:43:58 dump (pre-21:46 edit) already shows `vset[pmid,5]` and `ExpectValue=11`; the visible 21:46 delta is TM601's added `vset[bst,5,…]`.
- And a harder, independent problem sits underneath the whole ruling: the deployed TM600 does not close the relays the contract requires to put the ACM output on BST (`K48`, `K76`), while its own comment asserts the opposite of the connect map.

**What would settle it definitively:**
1. Relay/bench continuity check (no DUT): with the TM600 SetOn list as deployed (test.cpp:9081), measure BST at the DUT pin while `SW12_U1REF_BST_ACM` is at 5/10/20 V. If BST does not move, the current item is invalid regardless of PMID, and the ruling is repairing the wrong thing.
2. The DFT tool's own definition of `vset[pin,val,ramp,0]` and of the `floating source:` annotation (or a written statement from the DFT author / user): is `vset[pmid,5]` **ATE excitation** or **AMS-only stimulus**? This single document decides the case.
3. The DFT author's intent for the conflicting fields: a diff/annotation of `TM600` between DFT.csv and the workbook, in particular whether `iset[sw,1]` (workbook) supersedes `iset[pmid2sw,1]` (DFT.csv), and whether the 11 mΩ limit was qualified at 5 V or 15 V.
4. A bench comparison: run a real part at (vbat 3.5, pmid 5, bst_sw 5) and at (vbat 4.2, pmid 15, bst_sw 5), each with BST−SW = 5 V, and compare measured Rds,on against 11 mΩ and against AMS. This is the only evidence that decides which operating point the limit belongs to.
5. DUT datasheet condition for HS Rds,on (V(PMID)/V(BST−SW)/temperature) — not in the workspace (`docs/Rdson.docx` is ATE methodology only; no voltages, FACT).

## 9. Required conditions (if the orchestrator nevertheless proceeds)

Any implementation of PMID = 5 V must, in my assessment, carry these four conditions, or it is not the ruling that is being implemented:

1. **Write it as a differential.** "BST−SW = 5 V; with the ground-referenced ACM form (contract `bstRuling_ii`) the ACM setpoint must be **BST_abs = PMID + 5 V = 10 V**, not 5 V." Add the staircase in lockstep: PMID 0→5 V with ACM 5→10 V (mirroring test.cpp:7518-7526, TM640) — never ACM above PMID+5 V.
2. **Fix the BST leg before/with the voltage change:** close `K48_ACM5_AMP_REF` + `K76_ACM_BST` exactly as the contract requires for this alias (`[48,60,61,76]`) and as the sibling functions do, and delete the false claim at test.cpp:9027-9028.
3. **Settle the limit's provenance in the same ruling:** state explicitly which source the 11 mΩ limit is qualified against, and what happens to `iset[pmid2sw]` vs `iset[sw]`; do not change PMID while leaving the cross-pairing unstated.
4. **Re-verify, not re-assert:** re-check all four coupled fields against a single declared authority, record the DFT.csv-vs-workbook conflict as still open, and re-run the compile/gate closure on the changed function; a bench item for BST−SW and for the 5 V operating point must be registered as bring-up verification (not claimed as verified).

## 10. UNKNOWN list (things that block implementation)

- **U-A** Whether `vset[pmid,5]` in TM600 denotes ATE excitation or AMS/simulation stimulus. No DFT-tool `vset` specification exists in the workspace; only `units.md:70-73` (vset = FV) plus hand translation.
- **U-B** Default state of `K48`/`K76` and whether the deployed TM600's ACM output reaches BST at all. Contract says SetOn `[48,76]`; deployed code omits them; no relay-default authority table for those two relays was found in what I read.
- **U-C** The DUT's HS Rds,on dependence on the PMID working point (no datasheet in-repo; `docs/Rdson.docx` is methodology only).
- **U-D** The complete delta of the 21:46 workbook edit. I could only compare the 10 in-scope rows (TM600/TM601 among them) via the 13:43 `overview-dft.json`; a sheet-wide diff (or the workbook's revision history) is needed to state what the edit changed.
- **U-E** Whether an FV source on PMID (FXVIe_PLUS, 100 mA range) and an FI force of 1 A (FPVIe0) can coexist on one node during the pulse. No manual statement or bench evidence available.
- **U-F** The DUT's exact BST–SW absolute maximum (the workspace has only generic guidance, `docs/BST-SW通用知识介绍.txt`: "例如不超过5.5V"), which is why failure mode §7.1 is a damage *risk* rather than a quantified violation.

## 11. Checks performed / not performed (honesty statement)

Performed (all read-only): workbook row-by-row read (openpyxl, byte mode), DFT.csv csv-parse + sha, DFT_restored diff, reg_config/tm600.sv + tm601.sv, voltage-inference.md (all 178 lines, incl. lines 1-200 required), setup_contract.json (aliases, bst2sw ruling, relay chains, integrity notes; 371,739 bytes read by python), SCH-Connect-Map.txt targeted ranges (:15-400, :640-800) and target greps, deployed `test.cpp` (TM600_HS_RDSON 9057-9204 fully; TM640/TM609/TM608/TM641/TM643 regions; all `BST|PMID|RDSON` and all `FPVI0|FPVI1` hits; 235 vset/iset comment lines), `source/` tree sweep for a runtime `vset` API, hw_specs_extract.txt FPVIe/ACM200/FXVIe_PLUS tables, fpvie.md/acm200.md greps, units.md, golden `Rdson.cpp` (139 lines), `docs/Rdson.docx` text extraction, `docs/BST-SW通用知识介绍.txt`.
Not performed / impossible here: **no hardware or bench measurement** (no instrument access); **no DFT-tool manual available**; I did not read `D:/PROJECT6-DALI/devel` (instructed read-only, and not needed); I did not modify any file other than this report. `voltage-inference.md` lines 18/142-143/151-160 were read first-hand, and DFT.csv/TM600 rows were re-parsed with the `csv` module rather than trusted from the brief.

---

### One-line summary
The 15 V reading is not merely a stale markdown example but the operating point of `DFT.csv` (a hash-pinned run input that the frozen contract cites for TM600's sense-path aliases) and of the archived golden; the proffered self-consistency argument does not discriminate 5 V from 15 V; the workbook's 5 V/11 mΩ pair is *also* consistent with the deployed BUBO convention (TM640 uses PMID 5 V with ACM BST = 10 V absolute, K48+K76 closed) — but the deployed TM600 does not close K48/K76, so the ruling must not be applied as a one-field edit.
