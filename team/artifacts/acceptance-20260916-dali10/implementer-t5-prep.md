# t5 implementation-prep — TM600/TM601 skeleton + 8-item review stance

Author: ate-implementer. Run: `acceptance-20260916-dali10`.
Status: **preparation only — NOT written to source.** Nothing under `D:/PROJECT6-DALI/ForCodexDebug`
has been created, modified or deleted; no build was run. Per the Captain's 14:20+ instruction, this
captures the skeleton and review stance that t5 will execute once the user-adjudicated items land.

Inputs consumed: `dft-ir.json` (CR-01, PA-01/PA-02, BD-01..07), Captain rulings BD-02/BD-03 closed,
`implementer-recon.md` (Addenda 1-4). All hashes below are **python plaintext sha256**, and every
existence statement names its tool and scope (Addendum 4 rule).

---

## 1. Captain rulings now FIXED — no further t4 guessing on these

| # | Item | Ruling |
| --- | --- | --- |
| BD-03 | Register map | `.sv` mapping wins: `0x10=0x43`, `0x59=0x20`, `0x61=0x4B`, plus **TM600 `0x5A=0x02` (HS)** / **TM601 `0x5A=0x01` (LS)**. If t4's plan disagrees, this ruling governs and I report the divergence. |
| BD-02 | Force/sense topology | **TM600:** force `pmid2sw` (PMID↔SW), sense `PMID-SW`. **TM601:** force `sw2pgnd` (SW↔PGND), sense `SW-PGND`. `tm601.sv`'s `isrcPMID_SW` stimulus is **not adopted** (PMID↔SW cannot drive 1 A through the LS FET, and it contradicts its own SW-PGND check node). Scope: `.sv` is authoritative **only** for register mapping; topology and stimulus values follow DFT intent. |
| iset | Field semantics | `iset[<pin pair>, <current A>, <ramp time s>, <flag>]` — third field is **ramp time**, not current. TM601 `iset[sw2pgnd,1,1e-6,0]` = **1 A + 1 µs ramp**; TM600 `iset[pmid2sw,1,1e-3,0]` = **1 A + 1 ms ramp**. **Ramp difference must be recorded**: TM601 1 µs / TM600 1 ms. |
| BD-05 | Clamp | `SetClamp` is available. `SetClamp(50,50)` on a 1 V range = 0.5 V ≈ 500 mΩ ceiling — far above 11 mΩ, so it will not trigger in normal operation and is a **protection** (open-circuit / mis-wiring), NOT a test limit. Test limits come from BD-01. The numeric source for BD-05 is still with the user. |

### 1.1 Independent verification of the iset ruling (my #3 flag is RETRACTED)

I had flagged `iset[sw2pgnd,1,1e-6,0]` as a probable unit defect (1 µA → 8 nV). That was wrong;
I retract it. I verified the field semantics across the whole file: 36 `iset[...]` occurrences
(34 four-field, 2 five-field). **Field 3 takes only time-shaped values** — `1e-3` ×26, `1e-6` ×3,
`0` ×5; **field 2 takes only current-shaped values** — `-0.4 … 4` (0.01, 0.02, 0.03, 0.1, 0.5, 0.9,
1, 2, 3, 3.2, 4, and negatives). No field-2 value is a time and no field-3 value is a plausible
current, so `1e-6` is unambiguously the ramp slot. `reg_config/tm600.sv:38-42` is decisive and
self-labelling: `` `NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3); `` // `pin SW current set to 1A`.

Two exceptions, both benign and outside my scope: TM627/TM628 use a 5-field variant
(`iset[pmid2sw,-0,9,0,0]`) where field 3 is `9`; they do not affect the TM600/TM601 rows.

### 1.2 Independent verification of the BD-03 ruling

Confirmed by enumerating every `0x5A` write in the live `test.cpp` (python): `TM607_BUCK_LS_ZCD`
(7018) writes `0x5A=0x01` "D2A_BUBO_TM_LSON=1"; `TM608_BOOST_HS_ZCD` (7109), `TM609_BOOST_HS_NEG`
(7202) and `TM640_BOOST_HS_OCP` (7534) all write `0x5A=0x02` "D2A_BUBO_TM_HSON=1". Shipped
generation is LS=`0x01` / HS=`0x02` in `0x5A`, matching the `.sv` files — four independent TMs.

---

## 2. TM600/TM601 implementation skeleton (prepared, not written)

Design shape follows the project's canonical 6-step skeleton and the live `MV&MI` milliohm
precedent verified in `sub.cpp` (3258-3287, 3320-3331) and `TM702_1` (`test.cpp`:8070/8080).

```
DUT_API int TM600_HS_RDSON(short funcindex, LPCTSTR funclabel)      // name per CR-01
DUT_API int TM601_LS_RDSON(short funcindex, LPCTSTR funclabel)
```

| Step | TM600_HS_RDSON | TM601_LS_RDSON |
| --- | --- | --- |
| 0 Param | `//{{AFX_STS_PARAM_PROTOTYPES` + `StsGetParam(funcindex, "HS_RDSON")` + `//}}`; `double hs_rdson[SITE_NUM] = { 0 };` | same with `"LS_RDSON"` / `ls_rdson` |
| 1 Connect | `cbite.SetOn(K_FPVIH_TO_PMID_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW, -1)` then `delay_ms(3)` — **relay set must be re-confirmed by t3 setup contract** | `cbite.SetOn(<SW↔PGND pair incl. K36_ACM3_PGND_WL>, K13_VBAT_Cap, -1)` — **pair pending t2/t3** |
| 2 Power-on | VBAT, VDRV, PMID, BST-SW per setup contract; staged, explicit compliance per source | VBAT, VDRV, VBUS/PGND per setup contract |
| 3 Registers | `entertestmode(); 0x10=0x43; 0x59=0x20; 0x5A=0x02; 0x61=0x4B;` + `delay` 1e-3 | `entertestmode(); 0x10=0x43; 0x59=0x20; 0x5A=0x01; 0x61=0x4B;` + `delay` 5e-3 |
| 4 Measure | `FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, <RELAY MODE: PENDING>)`; ramp **1 ms**; `delay_ms(2)`; read sense pair + force; `SetClamp(50,50)` as protection; short pulse then `Set(FI, 0, …)` | same with ramp **1 µs**; range `FPVIe_2A` |
| 5 Power-off | reverse-order staged ramp-down, all sources `RELAY_OFF`, `FPVI0` last | same |
| 6 LogData | `FOR_EACH_VALID_SITE(site) HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);` | `… LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);` |

RON arithmetic (R-VIR: measured only, never the programmed value):
```
mohm = fabs( MVRET_senseHigh - MVRET_senseLow ) / fabs( MIRET ) * 1e3
```
Differential sense will use **two single-ended `MeasureVI(50,5)` reads + subtraction** — the
precedent-backed form (`sub.cpp`, `TM702_1`); `FXVIe_PLUSDiffMeasure` exists but has **zero** project
usages. Flagged to t4/test-strategy so the plan states which form it intends.

> **SUPERSEDED by §6 below.** The Captain ruled the two-single-ended-subtraction form **NOT
> adoptable**: it measures VDM−AMUX, which is not the node pair the DFT `Check` column requires.
> The correct form is a single floating source whose FORCE pair *is* the SENSE pair, read back with
> `MVRET`/`MIRET`. §2's arithmetic line above is also superseded by the exact R-VIR formula in §6.3.

Still needed before writing: `HS_RDSON`/`LS_RDSON` parameter types; the exact relay sets from the t3
setup contract; the force-source instance; and the settle/pulse widths.

---

## 3. The other eight TMs — review stance

Scope for t5 is "review existing implementation, change only where evidence supports it". Current
finding: **no source change is justified for any of the eight yet**, and two of them are blocked on
user adjudication rather than on code.

All eight verified live: tool = **python**, scope = `ForCodexDebug/source/test.cpp` (plaintext, 8878
lines). Declarations matched with `DUT_API int <name>\(short funcindex`; TM600/TM601 re-checked in the
same read and are still 0 occurrences.

| TM | Symbol @ declaration line | Stance |
| --- | --- | --- |
| TM000 | `TM000_IQ_STANDBY` @1358 | No change. `dft-ir` openQuestion notes no `reg_config/tm000.sv` exists, so the APORT/VAC_PLUG enable bit map used by the implementation is an **inference** — record as READ-BACKED, do not "fix" it by guessing. |
| TM001 | `TM001_IIN_SUSPEND` @1432 | No change. No `reg_config/tm001.sv` and no DFT.csv row; `AC1_GATE_ON` is an explicit TODO in the source. Out of t5's authority to invent. |
| TM102 | `TM102_HSKP_LP_ATEST0` @1730 | No change. `acceptance-plan` symbolHint vs OVERVIEW Name (`LP_VBG_BF`) disagree — a naming/IR issue, not a code defect. |
| TM103 | `TM103_HSKP_LP_HR_0P5U` @1802 | No change. Three register/observation stories (OVERVIEW+sv vs DFT.csv AMUX row vs implementation) — needs a C-01-class ruling before touching code. |
| TM108 | `TM108_HSKP_VAC1_PRST` @2155 | **Blocked (BD-04)**: rising threshold 4.4 V (OVERVIEW) vs 4.15 V (DFT.csv); also C-04 DMUX_SEL 22 vs 23. No change without the ruling. |
| TM109 | `TM109_HSKP_VAC2_PRST` @2233 | **Blocked (BD-04)**; plus the DFT.csv row ramps VAC3 instead of VAC2 (suspected copy/paste). |
| TM135 | `Trim_BG_RES_DIV` @3930 | No change. Trim step count (8) traces to a source comment, not a DFT source; TReg/EFUSE definition out of boundary. |
| TM1205 | `TM1205_TRX_BST_UV_GD` @8766 | **Blocked (BD-06)**: no ExpectValue/tolerance in any DFT source, so it cannot be judged pass/fail. Code itself needs no change. |

Net: t5's *only* intended source edits remain the two new functions; the eight are review-only
pending their rulings.

---

## 4. Evidence protocol that t5's manifest will attest

1. Every hash: **python plaintext sha256**, labelled `plaintext`. Never `Get-FileHash` (ciphertext
   hash, same byte length, falsely reports modification).
2. Every existence/absence claim: tool named (`python` / grep tool) **and** limiting scope
   (e.g. "absent from TM-level `test.cpp`" ≠ "absent library-wide").
3. No existence/absence assertion about `test.cpp` / `sub.cpp` / `StdAfx.h` from pwsh
   `Select-String` / `Get-Content` — reproduced blindness: pwsh 0 hits vs python 1 hit;
   pwsh 3316 lines vs python 8878 lines.
4. Before-hash → recoverable backup → write via python byte mode (UTF-8 BOM + CRLF preserved) →
   immediate re-read/re-hash. Never text mode (corrupts CRLF to `\r\r\n`).
5. Backups via python read/write, **not** PowerShell `Copy-Item` (produces empty copies for DLP files).

---

## 5. Remaining blockers (all user-adjudicated, none mine to decide)

- **BD-01 / PA-01 / PA-02** — TM600 11 mΩ (OVERVIEW!row132) vs 10 mohm (DFT.csv rec19); TM601
  7.5 mΩ (OVERVIEW!row133) vs 8 mohm (DFT.csv rec20). I will put **both values verbatim** in the
  manifest, never a fold or an average.
- **BD-05 numeric source** — the compliance value has no source; `SetClamp(50,50)`@1 V = 0.5 V is a
  candidate protection setting only.
- **BD-07** — TM600 OVERVIEW `Special='Y / 2 FLOAT'`: two floating nodes or a 2 A floating force?
- **BD-04 / BD-06** — affect TM108/109 and TM1205 respectively.
- **BD-02 secondary** — the exact relay sets still need the t3 setup contract (topology is ruled; the
  physical relay/pin realization is not yet assigned).

---

## 6. LOCKED implementation constraints (Captain rulings, each independently verified by me)

Scope note: BD-02 is **closed** by these rulings — three independent sources agree (DFT.csv rows are
internally self-consistent: force pair == sense pair; `rules-registry.md:44` R-BST-SW; Captain ruling).

### 6.1 Forbidden: no ramp family — verified against the gate script

`scripts/verify_bst_sw_sequence.py:78-114` `derive_targets()` collects a function as a gate target if
its block contains `rampi_capv(`:
```
if not name or not re.search(r'\brampi_capv\s*\(', block):  continue
```
and marks topology from the FPVIe high-side relay in `cbite.SetOn(...)` (`K_FPVIH_TO_PGND` → LS,
`K_FPVIH_TO_PMID` → HS), skipping with a WARN if it cannot decide. The script's own docstring says
the target set drifts with meta and "每加一个 TM 就可能多几条假 FAIL". VERIFIED verbatim.

Therefore TM600/TM601 must **not** use `rampi_capv`/`rampv_capv` (they are MV&MI static-force, not a
current-threshold ramp family). Using the ramp family would very likely add a NEW-RED on the `bst-sw`
baseline gate and break acceptance criterion 5.

### 6.2 Ranges — verified against `knowledge/standards/units.md:3-5`

Rule: "选最接近设定值 2 倍的那一档量程" → 1 A → **`FPVIe_2A`** (not `FPVIe_1A`). Voltage range
**`FPVIe_1V`**, not `FPVIe_100MV` (a failing part at 1 A × 1 Ω = 1 V would hit the range ceiling).
`FPVIe_IRNG` = `10A, 2A, 1A, 100MA, 10MA, 1MA, 100UA, 10UA` (`FPVIe.h:17`).
Resolution gain per `FPVIe.h:104-112`, enums `:37-51`: `FPVIe_MV_GAIN` = `X1, X2, X5, X10`.
⚠ **First-of-its-kind deviation to record:** all **56** `MeasureVI` call sites in `test.cpp` use the
bare `(50, 5)` form and there are **0** occurrences of `FPVIe_MV_X10`/`FPVIe_MI_X10` in `test.cpp` or
`StdAfx.h`. So using `MeasureVI(50, 5, FPVIe_MV_X10)` introduces project-first precedent. It is a real
resolution improvement for a 10 mV-class signal inside a 1 V range, so I will implement it as ruled,
but the review/gate should expect it as a deviation rather than flag it as an unauthorized departure.

### 6.3 R-VIR iron law — verified at `rules-registry.md:40`, `units.md:64-66`, E027

```
rdson[site] = FPVI0.GetMeasResult(site, MVRET) / FPVI0.GetMeasResult(site, MIRET) * 1e3;  // ohm -> mohm
```
Both operands MUST come from the **same source after the same `MeasureVI`**. Never substitute the
programmed 1 A. Enforcement is check-agent **E027**, whose failure conditions are explicit: "R 赋值出现
`/1e-5` 等理论电流/电压字面量 → FAIL; R 公式只读 MVRET 未读 MIRET → FAIL". So the formula must read
`MIRET` (it does) and carry no numeric current literal. Note `units.md:9-12` also fixes the output
unit: at >100 mA the result unit is mΩ via `V/A × 1000` — matches the DFT `Unit=mohm`.

### 6.4 Force shape — single FPVIe floating source, force pair == sense pair

Per R-BST-SW (`rules-registry.md:44`): "HS=BOOST(PMID-SW) / LS=BUCK(SW-PGND)，均电流>200mA 用 FPVIe 浮动源".
One `FPVI0` serves both roles; `MVRET` reads the differential directly. Not adopting
`FXVIe_PLUS_DIFF_*` (0 project uses, and the FXVIe family caps at 1 A) and not adopting the
two-single-ended subtraction (measures VDM−AMUX, not the DFT `Check` pair).

> ⚠ **THE SENSE HALF IS NOW RESOLVED — see §7.4.** The Captain ruled (user authority) that the
> **same FPVI floating source carries both force and sense**, with `R = MVRET / MIRET × 1e3` (R-VIR);
> the two-single-ended-subtraction form is **not adopted**. The force shape and geometry below stand.

| | TM600_HS_RDSON | TM601_LS_RDSON |
| --- | --- | --- |
| Force & sense pair | **PMID↔SW** | **SW↔PGND** |
| DFT Check | `PMID-SW` | `PGND-SW` |
| Force | 1 A | 1 A |
| Ramp | **1 ms** (`iset[pmid2sw,1,1e-3,0]`) | **1 µs** (`iset[sw2pgnd,1,1e-6,0]`) |
| Range | `FPVIe_1V` / `FPVIe_2A` | `FPVIe_1V` / `FPVIe_2A` |
| Registers | `0x10=0x43; 0x59=0x20; 0x5A=0x02; 0x61=0x4B` | `0x10=0x43; 0x59=0x20; 0x5A=0x01; 0x61=0x4B` |
| **Orientation (t2)** | ch0 **high→PMID** (K83), **low→SW** (K60,K61) | ch0 **INVERTED: high→PGND** (K154,K155), **low→SW** (K60,K61) |

Ramp values come **only** from DFT (`tm601.sv`'s 1e-3 is NOT copied — that file is the older
generation and was ruled not adopted for topology/stimulus).

> **Orientation correction (my prep doc previously omitted this).** For TM601 the loop runs
> PGND → (high) floating source (low) → SW → LS FET → PGND, i.e. **PGND is the HIGH terminal** because
> it hangs off `FPVIe0_FH_BUS_S1` while SW hangs off `FPVIe0_FL_BUS_S1`. With current flowing
> PGND→SW the LS FET drop is measured as V(SW)−V(PGND), matching `Check=PGND-SW`. **This also
> reconciles FS-01/§6.11**: the DFT naming (`iset[sw2pgnd]`, `Check=PGND-SW`) and the schematic
> orientation agree, and "1 A through the LS FET" is the same loop — no contradiction remains.

### 6.5 Power-up / power-down discipline (R-PON / R-POFF)

- Power-up: large-current three-stage `FV=0 → FI=0 → Clamp → FI`; floating-source staging ≤5 V steps.
- Power-down: zero → `delay_ms(1)` → `RELAY_OFF`; **`FPVI0` goes `RELAY_OFF` last**; large current
  `FI=0 → FV=0 → OFF`; `RELAY_OFF` uses the unified range — FPVI **1V/10MA**, not the 10 A range.
- `SetClamp(50,50)` is recorded as **protection** (guards open-circuit/mis-wiring), NOT a test limit;
  its numeric basis is still BD-05 / user-adjudicated.

### 6.6 verify commands t5 will run (and record in the manifest)

- `python scripts/validate_team_artifact.py implementation-manifest <this run>/implementation-manifest.json`
- `python scripts/check_testitems_meta.py --require-all --require-scope`
- `python scripts/verify_relay_trace.py --meta` (must show **no NEW-RED**; especially `bst-sw`)
- `python scripts/verify_single_fn.py` per function (includes the `crlf_clean` check)
- `python scripts/gen_testitems_meta.py` regeneration, python-only
- Release build via the project's DLP-authorized toolchain, reported separately from electrical
  validation (acceptance criterion 6)

### 6.7 Acceptance limits — BD-01 CLOSED by user adjudication

**Ruling: use OVERVIEW — TM600 = 11 mΩ, TM601 = 7.5 mΩ** (unit mΩ). The DFT.csv values (10 / 8 mohm)
are retained **as a registered conflict, verbatim** — no fold, no average, no deletion.

The manifest will cite **both** sides side by side and state the resolution explicitly:

- TM600: `OVERVIEW!row 132` = 11 mΩ **← acceptance limit** ｜ `DFT.csv index 18 (csvRecord 19)` = 10 mohm **registered conflict, retained**
- TM601: `OVERVIEW!row 133` = 7.5 mΩ **← acceptance limit** ｜ `DFT.csv index 19 (csvRecord 20)` = 8 mohm **registered conflict, retained**

I will not write a single bare value without that provenance.

### 6.8 BD-05 / BD-07 handling per ruling

- **BD-05 (clamp numeric source):** remains an **open item**, recorded as such. `SetClamp(50,50)` is
  written as **protection only** (open-circuit / mis-wiring guard), never as a test limit. No
  invented number.
- **BD-07 (`Y / 2 FLOAT`):** implemented under the **"two floating nodes"** assumption and **labelled
  as an assumption** in the manifest, per ruling.
- **BD-04 / BD-06:** outside TM600/TM601 scope; carried per t4's annotation.

### 6.9 Remaining gate before any source write

The t3 setup contract must supply the alias-resolution table (including K numbers) for the two force
pairs. **No source write until it lands** — this is the only remaining blocker on Step 1.

### 6.9.1 t2 schematic sensing evidence — the single-source form is now physically CONFIRMED

Independently verified by me: `schematic-ir.json` = 450689 B, python plaintext sha256
`ed77ccae15f458535015994d9dbbc6cd4c95c34b0bc283fae9cab32bcd06e41d` (matches the handoff, which also
notes an earlier `3ed7a4d7…` revision was superseded). `schematic-ir-sensing.json` = 39593 B,
sha256 `dc52dca4a5077e2cbb18aed3f7b85a02df3b04df577a5472086ccfab32c9b69c`.

`unreachableNodes = []` — no node in scope is unreachable, so no blocking decision on reachability.

`requiredPairAssertions` — **all three found = true**, asserted against the proof data rather than
hand-typed:
- FPVIe ch0 high `PMID` / low `SW` → **TM600** `unionRelays [60, 61, 83]`, `fourWireProper: true`,
  `touchesPcNets: false`
- FPVIe ch0 high `PGND` / low `SW` → **TM601** `unionRelays [60, 61, 154, 155]`, `fourWireProper: true`
- FPVIe ch1 high `BST` / low `SW` → TM600 bootstrap loop

`hasForceAndSenseOnBothEnds: true` on both item pairs. **This is the decisive answer to my §7
question**: the FPVIe's force AND sense conductors both land on the two DUT pins, so the floating
source's own `MVRET` really is a genuine 4-wire Kelvin differential. The Captain's single-source form
is therefore physically sound, not merely mandated — my escalation is closed with evidence.

### 6.9.2 Schematic constraints t5 must honour (from t2, not my inference)

| # | Constraint | Why |
| --- | --- | --- |
| SD-1 | TM600 and TM601 **shall not share a function/site**: both need FPVIe **ch0**, and TM600 also needs ch1 for BST↔SW (only 2 channels per site) | resource arbitration — our two functions are separate already |
| SD-2 | Keep the force↔sense bridges **OPEN** — `K88_FPVI0_Sense_FLOAT` (88, current StdAfx.h name; t2 cites the schematic naming `K86_KELVIN0_F/S`) and its FPVI1 twin `K132_FPVI1_Sense_FLOAT` (132); likewise the local-sense shortcuts `K87`/`K89` (FPVI1 `K131`/`K133`) | they merge force and sense on their row and are required only by QTMU (27) / QVM (14) proofs — **never** by an FPVIe proof; closing them degrades 4-wire to 2-wire and invalidates the mΩ result |
| SD-3 | Keep `K93_AGND2PGND` **OPEN** during TM601 | it ties AGND_F to PGND_F/PGND_S, which would short the differential reference and route the 1 A return through the K93 contact |
| SD-4 | Fix loop orientation explicitly (PMID↔SW = ch0 high→low; SW↔PGND = ch0 **low→high**) | PGND is the HIGH terminal; see the orientation row in §6.4 |
| SD-5 | **Never** route the Kelvin measurement through the FPVIe0 PC-net relays `K90_FPVI0_PC_Force` / `K91_FPVI0_PC_Sense` | those nets are board-shorted F↔S and carry R1_CS 100 mΩ / R2_CS 5 mΩ — the same order as the DUT — so they would corrupt a 10 mΩ measurement. Use the BUS route instead: K83 / K60+K61 / K154+K155 (§6.9.4) |
| — | Open `K141`/`K142` (the FPVIe0↔FPVIe1 BUS bridges) | otherwise TM600's two floating loops collapse into one node |
| — | BST must lead PMID/SW by ≥5 V while the FET is on; `D_BST_SW_S1` clamps BST−SW as secondary protection | E006 ramp rule; the 220 nF bootstrap cap has **no** ground bleed, so bootstrap discharge must be source-driven |

### 6.9.3 STIMULUS CORRECTION — I had the `.sv` values, the DFT ATE values are different

My §3/§6.4 stimulus figures came from `reg_config/*.sv` (simulation values). DFT.csv carries the **DFT
ATE values**, and they differ. Re-verified this turn: `DFT.csv` = 16862 B, python plaintext sha256
`b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4`.

| | DFT.csv (ATE, **use this**) | `.sv` (simulation) |
| --- | --- | --- |
| TM600 | `vset[vbat,4.2,100e-6,0] vset[pmid,15,100e-6,0] vset[bst2sw,5,1e-3,0] vset[vdrv,5,100e-6,0]` | vbat 3.5, pmid 5, bst_sw 5, vdrv 5 |
| TM601 | `vset[vbat,4.2,100e-6,0] vset[pmid,9,100e-6,0] vset[vdrv,5,100e-6,0]` | vbat 3.5, vdrv 5, vbus 5 |

test-strategy-architect independently reported the DFT.csv values (TM600 `vbat 4.2 / pmid 15 / bst2sw 5 /
vdrv 5`; TM601 `vbat 4.2 / pmid 9 / vdrv 5`) and **he is right**; my `.sv` numbers were the wrong
source. Note TM601's DFT row powers **PMID 9 V**, while its `.sv` powers **VBUS 5 V** instead — a
further divergence on top of C-03/C-05. Cross-checked against the acceptance plan's own
"Hardware_initial" wording, which is DFT-layer.

### 6.9.4 RELAY PATH EVIDENCE — the exact K numbers for the two force pairs

From the live `StdAfx.h` (python), the simple `_A` macros give the minimal force+sense path to each pin:

| Macro | Definition | Line |
| --- | --- | --- |
| `K_FPVIH_TO_PMID_A` | `83` — `K83_BUSH0_PMID` | 421 |
| `K_FPVIL_TO_SW_A` | `60,61` — `K60_BUSL0_VCP + K61_ACM8_SW` | 490 |
| `K_FPVIH_TO_PGND_A` | `154,155` — `K154_BUSH0_AMUX + K155_FOVI3_PGND` | 417 |
| `K_FPVIH_TO_BST_A` | `46,48,76` — `K46_BUS0_FH_SW1 + K48_ACM5_AMP_REF + K76_ACM_BST` | 377 |
| `K_FPVIL_TO_BST1_A` | `41` — `K41_BUS0_FL_BST` | — |

These match t2's `unionRelays` exactly ([60,61,83] for PMID↔SW; [60,61,154,155] for SW↔PGND), which is
a good independent cross-check. **So Step 1 can be written as `cbite.SetOn(K_FPVIH_TO_PMID_A,
K_FPVIL_TO_SW_A, ...)`-style or with the raw numbers — but note the `_A` macros expand to those
numbers, so either form closes exactly the right relays.**

**Why the simple `_A` form is the correct one for a Kelvin measurement:** the local-sense shortcuts are
`K87_FPVI0_FH_SL_SHORT` (87) and `K89_FPVI0_FL_SH_SHORT` (89), and the sense-isolate relay is
`K88_FPVI0_Sense_FLOAT` (88) (`StdAfx.h:251-253`; FPVI1 mirror at `:305-307`). None of them appears in
the `_A` macros. By contrast the **composite** macros do include them — e.g. `K_FPVIH_TO_VAC1 = 70,87,88,90,91`
(`:429`) and `K_FPVIL_TO_KLV1 = 73,88,89,90,91` (`:459`) — along with the PC-net relays `K90_FPVI0_PC_Force`
and `K91_FPVI0_PC_Sense`. **Those composites must not be used for TM600/TM601**: closing 87/89 or 88
would bridge force↔sense (local sensing) and collapse the 4-wire Kelvin measurement, and 90/91 route
through the board-shorted PC nets (SD-5). Same relay numbers as t2's SD-2, under the current
StdAfx.h names (t2 cites the schematic's `K86_KELVIN0_*` naming, `StdAfx.h` uses `K88_FPVI0_Sense_FLOAT`
— 0 hits for the former, so take the names from `StdAfx.h`).

### 6.9.5 Acceptance-limit ruling scope (verbatim requirement for the manifest)
Per the user's adjudication, the manifest must record **both** provenances *and* this scope:
**this ruling applies only to the present debug-copy acceptance run; if a newer version or an
approval record is found, the decision must be reopened.** The DFT.csv 10 / 8 mohm values are
retained unmodified in the IR and the final report — no rewrite, no average, no deletion.

### 6.10 Provenance correction: "1 A" is NOT an OVERVIEW figure (my own oversight)

I had been repeating "force = 1 A" for both parts as though it were agreed across sources. Caught by
dft-expert's `forceMagnitudeDisambiguation`, and it is right:

| Source | TM600 force | TM601 force |
| --- | --- | --- |
| OVERVIEW rows 132/133 | **not stated at all** | **not stated at all** |
| `reg_config/tm600.sv` / `tm601.sv` | 1 A (`iset[sw,1,1e-3]`) | 1 A (`iset[pmid_sw,1,1e-3]`) |
| DFT.csv rec 18/19 | 1 A (`iset[pmid2sw,1,1e-3]`) | 1 A (third slot is the 1 µs ramp slot) |
| TM600 CSV static operating point | implies **4 A** | — |

So 1 A is well-corroborated by the `.sv` files + DFT.csv rec 18 + the Captain's iset ruling, but it is
**not** an OVERVIEW-stated value and must never be cited as "both sources agree". This also keeps
**BD-07** genuinely open (`Y / 2 FLOAT`: two floating nodes vs a 2 A floating force?) — I implement
the ruled "two floating nodes" reading and label it an assumption.

### 6.11 IR divergence on TM601's force field (logged, not silently reconciled)

dft-expert's third IR revision (107133 B, live python plaintext sha256
`0a1c3b1e474c508c63d639d69e3b905ce94cb5b8085c98745c05a6625669597e`, re-hashed by me and matching)
still lists BD-01/02/03 as `open` (lag behind rulings) and sets
`items.TM601.forceAndSense.force.pins = [PMID, SW]` with `consistentWithCheckNode: false` — which
contradicts the Captain's ruling `force = sw2pgnd` for TM601.

I did not edit the IR and did not silently follow the ruling while the artifact says otherwise; I
raised it with both dft-expert and the Captain. My reading, offered for their judgement: the two are
reconcilable if `tm601.sv`'s `isrcPMID_SW` is the **instrument-side pin notation** for the same
SW↔PGND loop (PGND → floating source → SW → LS FET → PGND) with PMID merely a powered rail — which is
consistent with DFT.csv pairing `iset[sw2pgnd]` with `Check=PGND-SW`. If instead the schematic really
wires the LS floating source across PMID↔SW, then the DFT row's check node is wrong, which is a larger
problem. Either way only t2 settles it, and it does **not** block t5: I implement `sw2pgnd` per the
explicit ruling while recording that the ruling rests on the first reading.

---

### 6.12 BD-05 CLOSED (user ruling) — clamp as a provisional protection default

**Ruling:** adopt the golden's `SetClamp(50, 50)`, and **re-issue it after every FV/FI mode switch**.

**Independently verified** at `knowledge/sources/fpvie.md:141-168` — the manual text is explicit:
"Clamp settings are mode-dependent. Switching between FV/FI modes clears clamp settings back to
**102%**. Within the same mode, clamp settings persist." and the worked example re-issues
`SetClamp(25, 25); // re-set after mode switch`. So re-issuing is mandatory, not optional. Also
verified: `percent_PFS`/`percent_NFS` are **percent of full scale**, valid range 10-102%.

Compliance arithmetic: 1 A force on `FPVIe_1V` / `FPVIe_2A` → clamp 50% × 1 V = **±0.5 V**. Expected
drops are ~11 mV (TM600) / 7.5 mV (TM601) at 1 A, so the clamp sits **three orders above** the signal
and can only trip on an open circuit or gross mis-wiring. It is **protection, not a limit**.

Manifest must label it **provisional engineering default** — not a datasheet value, not a pass/fail
criterion — and state: **not valid for hardware/instrument execution, and the production tree must not
be modified.**

### 6.13 Limitations to carry in the manifest and the final report (U1 / U2)

- **U1** — the relay contact **1 A rating has no datasheet evidence**; hardware sign-off is required
  before any on-instrument execution.
- **U2** — the Kelvin sense rows carry **10 kΩ series parts** (`R_PMID_KLV_S1`, `R_SW1_KLV_S1`). That is
  benign only if the FPVIe sense input is genuinely high-impedance; t2's `force-sense` hazard asks for a
  contact check (`FPVIe_HIGH_SIDE`/`FPVIe_LOW_SIDE`) to confirm the sense series resistance is inside
  the FPVIe sense-input spec.

### 6.14 ΔV form FINALLY SETTLED — branch (a); branch (b) recorded as non-deliverable this run

The Captain withdrew the last named (b) candidates on t2's evidence, which I verified in
`schematic-ir.json` `hazards`:
- `measurement-validity` (QTMU): "QTMU low side is DGND … invalid for a mOhm-level force/sense
  measurement", `requiredMitigation`: "**For TM600/TM601 use only FPVIe Kelvin routes; do not measure
  RDSON on the QTMU defaults.**" So `S10_CH0_A` is out.
- `shared-resource`: `K141`/`K142` bridge `FPVIe0↔FPVIe1` BUS wires, and the QTMU default routes for
  PMID/SW require exactly those relays — which would merge TM600's two floating loops.
- QVM forms no proper pair (`nonKelvinInstruments`: mixed F/S, invalid for the mΩ Kelvin sense);
  ACM200 cannot reach PMID.
- PC route excluded: `kelvin-integrity` records `FPVIe0_FH_PC ↔ SH_PC` and `FL_PC ↔ SL_PC` as
  **board-shorted DIRECT_WIRE**, plus `R1_CS 100 mΩ±1%` / `R2_CS 5 mΩ±1%`.

So: **ΔV = branch (a), FPVIe's own Kelvin route** — `S1_FPVIe_SH0→PMID_S_S1` [83],
`S1_FPVIe_SL0→SW_S_S1` [60,61], `S1_FPVIe_SH0→PGND_S_S1` [154,155]. Branch (b) is recorded as
"**not deliverable in this run unless t3 finds an instrument table with genuine independent Kelvin
split lines**".

Target skeleton (mode slot still PENDING):

```cpp
FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, <RELAY MODE: PENDING before t3>);
FPVI0.SetClamp(50, 50);          // re-issue after EVERY FV/FI mode switch (fpvie.md:161)
delay_ms(2);
FPVI0.MeasureVI(50, 5, FPVIe_MV_X10);
rdson[site] = FPVI0.GetMeasResult(site, MVRET) / FPVI0.GetMeasResult(site, MIRET) * 1e3;  // mohm
```

Driver layer still PENDING: whether `FPVIe_RELAY_SENSE_ON` (or another setting) is what connects the
internal sense amplifier to `SH_BUS`/`SL_BUS`.

### 6.15 NEW OPEN ITEM — t2's relay recipe vs the live relay names

t2's `measurement-validity` / `kelvin-integrity` `requiredMitigation` says to measure "through the
FPVIe BUS Kelvin route (**K87/K88/K89** for channel 0)". I checked those names in the live
`StdAfx.h:251-253`:

| Relay | Live name | What the name states |
| --- | --- | --- |
| 87 | `K87_FPVI0_FH_SL_SHORT` | FH↔SL **short** (local sense) |
| 88 | `K88_FPVI0_Sense_FLOAT` | sense **float** / isolation |
| 89 | `K89_FPVI0_FL_SH_SHORT` | FL↔SH **short** (local sense) |

Closing 87 or 89 as named would **short force to sense** and destroy the Kelvin measurement — the
opposite of t2's intent. Two unverified readings:
1. the relays are **bipolar** (switch sense between remote-pin and local-short), so the names describe
   the local-short position and t2's "use K87/K88/K89" means the *other* throw; or
2. t2's recipe follows the **schematic revision** whose names are `K86_KELVIN0_*` (0 hits in the live
   `StdAfx.h`), i.e. a revision mismatch.

This is precisely the "driver layer" the Captain left PENDING, so it does not block the skeleton — but
t3 must resolve it, because the two readings imply **opposite relay states**, and a wrong choice yields
either a 2-wire measurement or no remote sense at all. I am not guessing it.

Related: t2's `limit-inconsistency` hazard still describes the third `iset` field as "a 1mA compliance
figure" / "1uA". That is superseded — the field is the **ramp time** (1 ms / 1 µs), settled by the
Captain. Flagged so the hazard text is not read as current.

## 7. RESOLVED — sense instrument: one FPVI floating source, `R = MVRET / MIRET × 1e3`

Raised by test-strategy-architect, verified by me, escalated to the Captain, **ruled and closed**.
The force shape and the geometry are settled, and so is the sense instrument. §7.0-§7.3 record the
investigation and remain as provenance; §7.4 is the binding outcome.

### 7.0 A correction to my own §21 search (retracted)

My §21 concluded "sub.cpp contains zero PMID↔SW spellings". The architect showed my search was
under-specified and he is right. I had searched five spellings (`PMID2SW`/`pmid2sw`/`PMID_SW`/
`pmid_sw`/`PMID-SW`) and missed the **arrow** form. python re-run:

| spelling | sub.cpp | test.cpp |
| --- | --- | --- |
| `PMID--->SW` | **32** | 0 |
| `PMID-->SW` | 2 | 0 |
| `PMID2SW` / `pmid2sw` / `PMID_SW` / `pmid_sw` / `PMID-SW` | 0 each | 0 each |

The 32 arrow hits are commented dead code in the legacy form, e.g.
`//\t\tFPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW` at 1128/1143/1304/1477/1649.
So the operative conclusion stands — the **live** force-shape precedent is `sub.cpp:3258`, not 1128 —
but my phrasing was wrong: "0 hits for these five spellings" is not "the concept is absent". This is
the same discipline failure as the pwsh trap (§19): an absence claim must be scoped to its tool
**and** its search pattern, and I stated it as concept-scoped.

### 7.1 Verified evidence for the architect's position
- `FPVI0.MeasureVI(50, 5)` **is** called in live code (test.cpp:7873/7972/8067/8077) — so calling it
  is precedented.
- But python search for `FPVI\w*\.GetMeasResult\([^)]*MVRET` returns **ZERO** hits in `test.cpp` and
  `sub.cpp`. Every `FPVI0.GetMeasResult` in test.cpp is `MIRET` (7877, 7976, 8071, 8081).
- At all four sites the measured voltage comes from **separate** ACM instruments
  (`VDM_SDA_ACM`, `VAC123_AMUX_ACM`) via two single-ended `MVRET` reads plus subtraction.
- Conclusion now supported by evidence: taking the floating FPVIe's **own `MVRET`** as the
  measurement has **no project precedent**.

### 7.2 Why precedent alone does not settle it (my assessment)

"Never used" is an absence of precedent, not a prohibition, and the Captain's ruling that one
floating source carries both force and sense is a positive architectural statement. Metrologically the
floating source's own differential sense is *better* for a 10 mΩ target than subtracting two
ground-referenced single-ended reads: two instruments bring uncorrelated offset/gain errors, plus
common-mode error on what is effectively a floating pair, and a difference of two large numbers.
That is the reason a floating source exists. So overturning the ruling needs a metrological reason,
not just a precedent count.

### 7.3 The fact that actually resolves it — and that neither of us can read

Neither position establishes **which instrument measures the DFT `Check` pair**:
1. Does the FPVIe's voltage sense physically land on the Kelvin pair (FH/SH vs FL/SL), or only at its
   own output? If it lands on the Kelvin pair, its `MVRET` is a true four-wire differential.
2. Which voltmeter is on PMID and which on SW — candidates raised by the architect were
   `PMID_HG2_FXVI`, `SW1_SW2_FXVI`, or an ACM reached through a relay.

This is the `DFT 路径别名 → 仪器/继电器` mapping. I supported the architect's request to put it in t3's
inScope, and I will register it as a blocking decision rather than invent instrument names (the role
boundary forbids inventing API names).

**Important nuance:** the two forms are not necessarily mutually exclusive. R-BST-SW
(`rules-registry.md:44`) speaks to the **force** source and the BST-SW staircase; it does not
explicitly say which instrument senses 10 mV. So the force pair can remain PMID↔SW per the ruling
while the sense is taken by dedicated voltmeters. Under that reading the architect's form and the
Captain's ruling coexist, and only the sensing instrument is at issue.

### 7.4 RESOLVED then RE-OPENED — the Captain reversed on the sense form, and t2's evidence contradicts the reversal

**Captain ruling 1 (earlier):** the same FPVI floating source carries force AND sense; `R = MVRET / MIRET × 1e3`.
**Captain ruling 2 (later, reversing the sense half):** the FPVIe's own `MVRET` must **not** be the
measurement; sense must be **two single-ended `MVRET` reads on the DFT `Check` pair**, subtracted.
Rationale given: "1 A × 10 mΩ ≈ 10 mV, and a source-end two-wire self-read would include relay/lead
resistance, so an independent Kelvin sense point on the DUT pins is required".

I verified the captain's code citation exactly (test.cpp:8065-8071: `VDM_SDA_ACM` + `VAC123_AMUX_ACM`
+ `FPVI0`, then `MVRET_A − MVRET_B` and `FPVI0.GetMeasResult(site, MIRET)`), and confirmed the
capability claims (`GetMeasResult` defaults to `MVRET` at `FPVIe.h:114-117`; `FPVIe_MV_GAIN` at
`:37-51`). The self-correction about "capability exists ≠ used correctly" was right.

**But the stated metrological rationale does not apply to this instrument.** `bus-topology.md:104`
requires `FH/SH` and `FL/SL` connected through the PAD, and t2's `singleEndedEvidence` gives FPVIe
`sense` terminals `S1_FPVIe_SH0 → PMID_S_S1 (req [83])` and `S1_FPVIe_SL0 → SW_S_S1 (req [60,61])`
— sense conductors run in parallel to the DUT pins, so relay/lead resistance sits in the **force**
branch, not the sense branch. Two-wire degradation happens only through the K86/K130 force↔sense
bridges (SD-2), and identically for ACM200 (`FH8/SH8 … req [61]`, `twoWireBridged: []`).

**The decisive problem is reachability**, from t2's `schematic-ir-sensing.json` (asserted against the
fresh PathProof, not hand-typed):

| Instrument | Reaches | Verdict |
| --- | --- | --- |
| ACM200 | **SW only** (req K61); cannot reach PMID or PGND at all; ±200 mA | usable for SW single-ended ≤200 mA; **invalid** for the 1 A force |
| FXVIe_PLUS | **PMID and PGND only**, never SW; low side returns to AGND_F | **invalid** for a PMID-SW or SW-PGND differential pair |
| QTMUe | single line, low on DGND, non-Kelvin | **invalid** for mΩ differential RDSON |
| QVMe | floating, two sense leads, but CH0+ lands on a **force** net → mixed F/S | limited-accuracy independent differential; **invalid** for the mΩ Kelvin sense |
| **FPVIe** | true force **and** sense on both ends of both pairs | `fourWireProper: true`, `hasForceAndSenseOnBothEnds: true`, `touchesPcNets: false` |

So **no pair of non-FPVIe instruments can supply single-ended `MVRET` on both nodes of either Check
pair**: TM600 would need two different instruments and ACM200 cannot reach PMID; TM601 has no
reachable Kelvin instrument on SW other than FPVIe. The precedent the captain cited (VDM − AMUX)
works precisely because *both* those nodes are reachable by ACM-class instruments; the Check pairs
here are not.

Escalated to the Captain with three options: (a) revert to the FPVIe floating 4-wire pair and drop the
non-applicable relay/lead rationale; (b) have t3 name concrete ground-referenced instruments on each
Check node, else register it as a blocking decision; (c) dedicate FPVIe ch1 as a separate floating
voltmeter — but SD-1 says both channels are committed.

**Status: sense form resolved by the Captain's criterion to branch (a); activation syntax still
pending t3.** The force shape, ramps, registers, ranges and arithmetic stand under either reading.

> ### ⚠ §9 supersedes every hash quoted earlier in this document. Re-measure before citing.

---

## 9. CURRENT-DISK HASHES (re-measured by python; superseded all earlier values here)

The Captain flagged twice that hand-copied hashes in this document were stale — the artifacts were
regenerated underneath me by t1/t2/t3/t4. Per the run's own rule ("re-hash, never trust a quoted
digest") the authoritative values at the time of writing are:

| Artifact | Size | python plaintext sha256 | mtime |
| --- | --- | --- | --- |
| `schematic-ir-sensing.json` | 47446 B | `43ad8c84ed21290efbb8a955568cab382fdaa5a766405e44bd2f337633a818f8` | 14:07:07 |
| `schematic-ir.json` | 457531 B | `9f4a7707fb0a1b31f4f884dcac617c5273506de6c2a088a3b9c3f1b20683f639` | 14:17:50 |
| `setup-contract.json` | 262032 B | `7e6ca7f5baa1eecbb4c159406bae570855805ec899e02c22b73af19be691a569` | 14:23:52 |
| `test-plan.json` | 121694 B | `2e93a46c54c79b9028940840f6cf162d15304f89df3c3e88dd5fdea5f5061eda` | 14:20:55 |
| `dft-ir.json` | 130724 B | `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b` | — |

**Unresolved discrepancy, stated rather than smoothed over:** the Captain twice reported the sensing
artifact as **47156 B / `ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140`**. I
re-measured the file that exists and it is **47446 B / `43ad8c84…`** (mtime 14:07:07). The byte sizes
differ by 290, so this is not a hash-method artefact — one of the two measurements is of a different
file or revision. I am reporting my measurement with its path and size rather than adopting the
other value; a third party should re-hash the same path to settle it. Note `test-plan.json` has since
moved to `v3 (t10)` and `t11`/`t12` are still pending, so these values will move again.

**Substantive consequence of the revision:** t10 published plan `v3`, and my payload was built from
the t4 revision. I re-checked the current v3 values for both items and they match the payload
exactly — force loop PMID→SW (TM600) / SW↔PGND with PGND high (TM601), 1.0 A, ramp 1 ms / 1 µs,
settle 2 ms, 200 samples at interval 5, clamp 50/50 re-issued after every mode switch, DV-01 ruled
to the primary (branch (a)) form. So the payload remains valid against v3.

### 7.5 FINAL CRITERION APPLIED — branch (a): FPVIe's own 4-wire Kelvin differential

The Captain ruled the ΔV form is decided by **path-table evidence**, with three branches. I applied
the criterion and it fires **(a)**.

#### 7.5.1 Corrections to the Captain's fact list (python, all project source)

- `FPVIe_RELAY_SENSE_ON`, `FPVIe_HIGH_SIDE`, `FPVIe_LOW_SIDE`, `FPVIe_CONTACTMODE`, `FPVIe_HIGH_MV`,
  `FPVIe_LOW_MV` → **0 hits in every project source file**. Captain's claim confirmed.
- **`FPVIe_MV` → NOT 0:** test.cpp 0, sub.cpp 0, `StdAfx.h` 0, `BoardCheck.*` 0, but
  **`Test_Method.cpp` = 36**, all of the form
  `MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG)` (288, 559, 704, …, 3584) on
  `ramp_res`/`cap_res`, which are FPVIe objects (`:275` `ramp_res.Set(FI, start_point, …)`).
  Two consequences: (i) the **gain argument has method-library precedent, but only passing the X1
  default explicitly** — so `FPVIe_MV_X10` remains a genuine first use; (ii) it does **not** rescue
  "the FPVI's voltage is measured", because in that same block the voltage read is
  `cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT)` (`:300`) — the FPVIe is the ramper, the ACM is
  the voltmeter, exactly as the architect argued.
- SDK enums verified verbatim: `FPVIe_OUT_RELAY{HOLD, ON, OFF, SENSE_ON}`,
  `FPVIe_CONTACTMODE{HIGH_SIDE, LOW_SIDE, ALL_SIDE}`,
  `FPVIe_RET_RESULT{MV, MI, HIGH_MV, LOW_MV}`, plus `FPVIe_CLAMP_ALARM`.

#### 7.5.2 Why branch (a) fires

The criterion: "if the path table proves FPVIe's sense terminals actually reach the two pins of the
Check pair → use the FPVIe's own 4-wire Kelvin differential". Evidence (t2, asserted against the
fresh PathProof):
- PMID: `S1_FPVIe_SH0 → PMID_S_S1`, requiredOn **[83]**; SW: `S1_FPVIe_SL0 → SW_S_S1`, requiredOn **[60,61]**
- `requiredPairAssertions` all three `found: true`; for both items `hasForceAndSenseOnBothEnds: true`,
  `fourWireProper: true`, `touchesPcNets: false`
- `bus-topology.md:104` independently requires FH/SH and FL/SL connected through the PAD
- the only thing bridging force↔sense (K86/K130) is exactly what SD-2 keeps **OPEN**

Branch (b) cannot fire on these nodes: t2 shows ACM200 reaches SW only and never PMID/PGND, and
FXVIe_PLUS reaches PMID/PGND but never SW and cannot float. Branch (c) does not apply.

#### 7.5.3 Residual limit on my own evidence — not papered over

The path proofs establish the sense conductors are **physically connected** to the pins in the relay
matrix. They do **not** establish the correct **instrument-level relay mode** for exposing those
terminals — i.e. whether `FPVIe_RELAY_ON` suffices or `FPVIe_RELAY_SENSE_ON` (and which
`FPVIe_CONTACTMODE`) is required for the sense return to be active. That is an instrument-configuration
fact and is exactly what was requested from t3. So the (a)-vs-(b) decision needs no further input, but
the **activation syntax** does — I will not lock it before t3 (or the Captain) confirms.

#### 7.5.4 If branch (a) is implemented, these are project-first uses to flag as argued deviations

- `FPVIe_RELAY_SENSE_ON` and/or `FPVIe_HIGH_MV`/`FPVIe_LOW_MV` — 0 precedent in project source
- `FPVIe_MV_X10` gain — the gain argument has precedent only as the explicit X1 default
Each will be recorded in the manifest as a deliberate, evidence-argued departure, not an unauthorized one.

#### 7.5.5 Naming correctness for the record

The ruling's item 1 wrote `FPVIe.Set(FI, 1.0, …)`. `FPVIe` is a **class**, so that is not valid C++;
the objects are the globals `FPVI0`/`FPVI1` (`extern FPVIe FPVI0;` — `Pin_Channel_define.h:120`).

Correct object name: `FPVI0`. Correct enum spelling: **`FPVIe_RELAY_ON`** — the ruling's
`FPVIE_RELAY_ON` (capital E) does not exist. The Captain has since confirmed this typo and confirmed
that `FPVIe_RELAY_ON` is authoritative.

**But the relay MODE is NOT locked** (Captain's explicit instruction). The output-relay argument is a
**PENDING slot**: `FPVIe_RELAY_ON` (local/instrument-end sense) vs `FPVIe_RELAY_SENSE_ON` (remote
sense). Which one is correct depends on the instrument-level activation fact that is still open, and
this section asserts only the *identifier* (`FPVI0`) and the *enum spelling*, not the mode:

```cpp
FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, <RELAY MODE: PENDING>);   // RELAY_ON vs RELAY_SENSE_ON — OPEN
```

**Reason it matters:** if the mode is effectively local/instrument-end sensing, `MVRET` would include
lead + relay drop — tens of percent error against an 11 / 7.5 mΩ target. So the mode must not be
defaulted to `FPVIe_RELAY_ON` "because every live precedent uses it"; the precedents (sub.cpp:3258,
test.cpp:7869) are all non-mΩ items where that error is irrelevant.

**Specific warning about the relay set — the sense path must NOT include these:**
`K88_FPVI0_Sense_FLOAT` (88) is the sense **float/isolation** relay, and `K90_FPVI0_PC_Force` /
`K91_FPVI0_PC_Sense` (90/91) are the **PC-net** relays, which are **board-shorted F↔S** and carry the
100 mΩ / 5 mΩ shunts (t2's SD-5). None of them is part of the Kelvin route; a plan that closes them to
"get remote sensing" would short force to sense and route the measurement through the shunts. The
correct route is the `_A` minimal form (§6.9.4): 83 / 60+61 / 154+155.

Also accepted: `FPVIe_MV_X10` is now an **explicitly-argued deviation**, not a mandate — valid only if
the sense instrument is FPVIe-class; if an ACM-class instrument senses instead, I pick its range by
the same ≥2× rule and record the reasoning.
