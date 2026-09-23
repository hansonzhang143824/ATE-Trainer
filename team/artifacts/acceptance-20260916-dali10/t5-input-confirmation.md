# t5 INPUT CONFIRMATION — consistency gate (awaiting final snapshot hashes)

Author: ate-implementer. Run: `acceptance-20260916-dali10`.

**STATE: HOLD.** Per the user's consistency gate I will not write anything under
`D:/PROJECT6-DALI/ForCodexDebug` — no source edit, no backup, no temp file, no meta regeneration —
until the Captain sends (a) the **final snapshot hashes** of `test-plan.json` and
`setup-contract.json` (python plaintext) and (b) the **key-decision summary**. Then I fill the two
HASH cells below and only then begin writing source, so t6/t9 can do a clean consistency check.

Verified this turn: `test.cpp` = `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`
(still the run baseline). `devel` untouched. I have never written to the target.

## A. Confirmation table (HASH cells deliberately blank)

> **Revision churn, verified from the kept copies** (`test-plan.v1..v8.json` are preserved alongside
> the live file): v1 98641 B → v2 113773 B → v3 121694 B → v4 128624 B → v5 131707 B → v6 134802 B →
> v7 136263 B → v8 137290 B → live **v9 142445 B / `19ff5e842d45168aae68b24b3eb2a0d41deaff72d9f28e4080577ab7a2a14842`**
> ("evidence-accuracy corrections from independent review"). t4 asked me to register **v4** as the
> baseline, but five revisions have landed since; registering v4 would pin a digest that is no longer
> the artifact anyone would read. **Therefore the version recorded below will be the one the Captain's
> release message pins, with earlier revisions listed as history** — not a version chosen by t4 or by
> me. Substantively the content has not regressed: v9 still carries `pulseCap` 2 ms, the
> stricter-than-golden clamp annotation, 17 limitations incl. U10, and `revisionHistory`.

| # | Content key | Locator | Value asserted | HASH (computed at reference time) |
| --- | --- | --- | --- | --- |
| 1 | implementation basis — per-item test plan | `team/artifacts/acceptance-20260916-dali10/test-plan.json` → `items[TM600]`, `items[TM601]` | symbols `TM600_HS_RDSON` / `TM601_LS_RDSON`; force loop PMID↔SW (TM600) and SW↔PGND with **PGND high** (TM601); 1.0 A; ramp 1 ms / 1 µs; **settle 1 ms**; samples 200 @ interval 5; clamp 50/50 re-issued per mode switch; relayUnion [60,61,83] and [60,61,154,155] | **v20 · 166099 B · `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016`** |
| 2 | implementation basis — relay/setup contract | `team/artifacts/acceptance-20260916-dali10/setup-contract.json` → `tmDeltas.TM600`, `tmDeltas.TM601` | relay sets, pin routes, register delta, force/sense topology, cleanup; BST−SW on the ground-referenced `SW12_U1REF_BST_ACM` (ruling (ii)) | **revision 22 · 329115 B · `295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c`** |
| 3 | verbatim call form | `team/artifacts/acceptance-20260916-dali10/test-plan-tm600-tm601-measurement-excerpt.md` → code block | `Set(FI,±1.0,FPVIe_1V,FPVIe_2A,FPVIe_RELAY_ON)` → `SetClamp(50,50)` → **`delay_ms(1)`** → `MeasureVI(200,5,FPVIe_MV_X10)` → `MVRET/MIRET*1e3` → immediate `Set(FI,0,…)` | **8423 B · `9554d4d6f4fe878d05ba65fe5a79628192445f46ff74793e22d146f0e9ef89c8`** |
| 4 | DFT intent incl. limits + iset semantics | `team/artifacts/acceptance-20260916-dali10/dft-ir.json` → items TM600/TM601, `limitConflictPairs` | 11 / 7.5 mΩ ruled; 10 / 8 mohm retained verbatim; third `iset` field = ramp time (1 ms / 1 µs); third-field literal "1 µA" reading superseded | **130724 B · `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b`** |
| 5 | schematic sensing evidence | `team/artifacts/acceptance-20260916-dali10/schematic-ir-sensing.json` → `dfdPairVerdicts`, `requiredPairAssertions` | FPVIe ch0 is the only instrument with force+sense on both ends of both Check pairs; four other instruments rejected | **47446 B · `43ad8c84ed21290efbb8a955568cab382fdaa5a766405e44bd2f337633a818f8`** |
| 6 | golden reference for the measurement idiom | `knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp` → line 91 | `GetMeasResult(site, MVRET) / GetMeasResult(site, MIRET) * 1e3` (golden-supported, project-first) | `8cdb0be1…` (verify at cite time) |
| 7 | clamp re-issue authority | `knowledge/sources/fpvie.md` → L141-168 | "Switching between FV/FI modes clears clamp settings back to 102%" + manual re-issues after a switch | verify at cite time |
| 8 | relay-name authority | `D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h` → L251-253 (ch0), L305-307 (ch1), L377/417/421/490 (path macros) | minimal `_A` macros: 83 / 60,61 / 154,155 / 46,48,76 — **none** contains 87-91 or 131-135 | verify at cite time |
| 9 | relay-state actuation authority | `project/DALI/SCH-Connect-Map.txt` → L4 legend, L9-12, per-line 需闭合 | K83 + K60,K61 (TM600); K154,K155 + K60,K61 (TM601); K87/K88/K89 default (not SetOn) | verify at cite time |

## B. Key decisions the payload already implements (to be cross-checked against the Captain's summary)

| Decision | Implemented as |
| --- | --- |
| BD-01 limits | 11 / 7.5 mΩ cited as the acceptance limits, DFT.csv 10 / 8 mohm retained verbatim as a registered conflict; scope + reopen condition recorded in the payload header |
| BD-05 clamp | `SetClamp(50,50)` = ±0.5 V on the 1 V range, re-issued after every FV/FI switch, labelled provisional / bench-signoff-required / protection-only; **stricter than the golden** noted |
| Pulse | `delay_ms(1)` settle → `MeasureVI(200,5)` → immediate `Set(FI,0)`; nothing in between. **This is the delivered form** (captain ruling (b)); the earlier `delay_ms(2)` reading and its ~3 ms whole-pulse arithmetic are superseded, and the `pulse2ms-variant.cpp` file they were staged in **no longer exists** — deleted on the captain's instruction so there is a single delivery path, `implementation-payload-TM600-TM601.cpp` |
| Pulse budget | Nominal 1 ms settle + 1 ms acquisition = **exactly** the 2 ms HARD CAP, i.e. **zero on-paper margin**; it excludes driver/call/relay latency, so the payload must not be described as pulse-compliant measured — compliance is a bring-up item with U11 |
| ΔV = (a) | floating source's own 4-wire Kelvin pair; `R = measured MVRET / measured MIRET × 1e3`; PC route excluded |
| Relay rules | K87/K88/K89 left at default (never SetOn); K141/K142 open; K86/K130 open; K93 open during TM601 |
| Register map | per-TM `.sv`: `0x10=0x43`, `0x59=0x20`, `0x61=0x4B`, `0x5A=0x02` (HS) / `0x01` (LS) |
| Excitation | ATE values only — TM600 vbat 4.2 / pmid 15 / bst2sw 5 / vdrv 5; TM601 vbat 4.2 / pmid 9 / vdrv 5 — **not** the `.sv` 3.5 / 5 V |
| Ramp family | no `rampi_capv` / `rampv_capv` introduced (delta-only criterion) |
| First-use surface | exactly one item: `FPVIe_MV_X10`; `RELAY_SENSE_ON` / `CONTACTMODE` / `HIGH_MV` / `LOW_MV` absent from code (latter two also unreachable) → U9 |

## C. Manifest draft (fields present, hash-bearing values to be filled after release)

- `runId`: `acceptance-20260916-dali10`
- `targetRoot`: `D:/PROJECT6-DALI/ForCodexDebug`
- `scope`: the ten TMs; **source edits intended for TM600/TM601 only**; the other eight reviewed with no
  change justified except a possible TM108/TM109 threshold edit (BD-04) which requires reporting first
- `backups`: `team/artifacts/acceptance-20260916-dali10/backups/test.cpp.before_TM600_TM601.bak`,
  sha256 `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` (python plaintext, verified
  byte-identical before any write attempt)
- `changes`: one entry planned — `source/test.cpp`; `symbols` `["TM600_HS_RDSON","TM601_LS_RDSON"]`;
  `beforeSha256` = the baseline above; `afterSha256` = _(pending the write)_; `planRefs` per table A
- `selfChecks`: `python scripts/gen_testitems_meta.py`; `python scripts/check_testitems_meta.py
  --require-all --require-scope`; `python scripts/verify_relay_trace.py --meta`;
  `python scripts/verify_single_fn.py`; `python scripts/validate_team_artifact.py implementation-manifest`;
  gate run via the `scripts/run_gates.ps1` pwsh wrapper, reported as a **delta** (KNOWN-RED vs NEW-RED
  with exit code, log path, log hash). Exit codes to be recorded when they can actually run.
- `limitations`: U1, U2, U3–U8, U9, BD-06, BD-07, plus the boundary sentence (debug code + compilation
  only; clamp/pulse and sense-activation provisional and bench-signoff-required; compile ≠ electrical
  correctness) and the BD-04 note for TM108/TM109.

## C2. Rulings applied to the payload since §B was written

| Ruling | Effect on the payload | Verified |
| --- | --- | --- |
| BD-05 pulse **(b)**: settle reduced to 1 ms so settle + acquisition = 2 ms ≤ 2 ms HARD CAP | `delay_ms(1)` settle in both functions; `delay_ms(2)` = **0**; arithmetic + "deliberate deviation from the golden 2 ms" annotated in code | yes |
| L177 range finding: 0 V / 0 A init must use the minimal compliant step | both power-on inits now `FPVIe_1V, FPVIe_10UA`; `FPVIe_10A` = **0** | yes |
| Teardown order (R-POFF-04): the measurement channel must release last | TM600 order rebuilt so **FPVI0 is last**, FPVI1 first; TM601 FPVI0 last | yes |
| **BST−SW arbitration, ruling (A)** — baseline is the ground-referenced ACM, FPVIe1-CH1 recorded as `intended-but-unrealisable` | **no payload change needed**: the rail is driven by `SW12_U1REF_BST_ACM` ×13, `FPVI1` appears only in the teardown `RELAY_OFF`, and K131/K132/K134/K135 appear nowhere in code. The plan text is being corrected in t17 | yes |
| **Sign convention (contract `signConventionFinding`, closed by ruling; U11)** | TM600 `+1.0 A` (DFT literal, PMID on the HIGH terminal); **TM601 `-1.0 A` (derived, NOT the DFT literal, because PGND sits on the HIGH terminal)**; three-step chain + U11 criteria annotated in code; `MIRET` read through `fabs()` | yes |

**Payload as of this revision** (python plaintext, BOM + CRLF, 0 lone LF):
`implementation-payload-TM600-TM601.cpp` = **27228 B / `889c8e77668c86350227035afcb436792358feb424ba1d9e62c2b5da356b207e`**.
The duplicate `…pulse2ms-variant.cpp` has been **deleted** on the Captain's instruction, so there is a
single delivery path. Superseded values for the record: `26011 B / bf7e58da…` (before the sign change)
and `23323 B / 82c5b5fb…` (before the range fix and teardown fix).

## D. Write-gate status
Two independent reasons no write has occurred: (1) this consistency gate, and (2) the sandbox denies
writes to the target from this session (read works; the single escalation was rejected by the user and
was not retried). When the gate lifts, the write still needs target access **or** an external operator
running `APPLY-TM600-TM601.md`.
