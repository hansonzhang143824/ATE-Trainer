# t29 — TM600 BST excitation path: K109/K110 closure (contract conformance, high)

Author: ate-implementer (content) · Independent review: rule-reviewer · Executor: Captain (REPLACE semantics).
Payload after this repair: `implementation-payload-TM600-TM601.cpp` =
**36381 B / `73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e`** (BOM + CRLF, 0 lone LF).
Previous version (missing K109/K110): 35014 B / `444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c` — kept as history.

## 1. The defect

TM600's SetOn set closed only `K83 + K60,K61` (+ cap gates). Ruling (ii) puts the BST−SW 5 V rail on the
**ground-referenced** `SW12_U1REF_BST_ACM` (ACM200), but the route from that source to BST was never
closed. `K110_ACM18_BST` is a **double-throw** relay, and its name does not by itself route anything:

| Locator | Route |
| --- | --- |
| `SCH-Connect-Map.txt:724` | `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` ← **un-actuated** |
| `SCH-Connect-Map.txt:725` | `S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S` ← **un-actuated** |
| `SCH-Connect-Map.txt:43` | `S1_FPVIe_FL0 -> K89(NC) -> K145(ON) -> K146(ON) -> K109(ON) -> K110(ON) -> BST_F` |
| `SCH-Connect-Map.txt:109` | `S1_FPVIe_FL0 -> … -> K109(ON) -> K110(NC) -> PB0_F` (the other throw) |
| `SCH-Connect-Map.txt:42` | `CH0 Low -> BST [Kelvin] 需闭合: K109,K110,K138,K139,K145,K146` |

So with `K110` open the ACM18 source lands on the **PB0 PWM pin**, not on BST: ruling (ii)'s
"ground-referenced drive of BST−SW" was electrically unrealised. "The fixture may hard-wire it" is **not**
an admissible omission — the contract and the connect map both require the closure; if a hard wire exists,
the contract must be changed first by its owner (separate task).

## 2. Per-item conformance table (contract rev 24 = 328805 B / `fd00a508…`)

| Authority | Requires | Payload now | Locator |
| --- | --- | --- | --- |
| `tmDeltas.TM600.pinRouteTable.BST["列2 … CH0 Low"].needsClosed` | `[109,110,138,139,145,146]` | **109, 110 closed**; 138/139/145/146 belong to the FPVIe CH0-Low variant of this route, not to the ACM200 drive used here — see §4 (contract inconsistency flagged) | contract path above; connect map `:42` |
| `aliasResolution[3]` (`bst2sw`) `resolution.relayChain` + `closedRelayNumbers` | `[110, 61]` — chain `K110_ACM18_BST` "SetOn (ACM200 S5_FH18 -> BST)" and `K61_ACM8_SW` "SetOn (ACM200 S5_FH8 -> SW)" | **110 closed** (61 already was) | contract `aliasResolution[3].resolution` |
| `tmDeltas.TM600.relaySet` | contains `110` (also `109`) | present | contract `tmDeltas.TM600.relaySet` |
| `aliasFlatTable[3].relayPath` | `K110_ACM18_BST -> K61_ACM8_SW` | matches | contract `aliasFlatTable[3]` |
| Connect map route requirement | `K109,K110` on the CH0-Low→BST route | both closed | `SCH-Connect-Map.txt:42,:43` |
| `K109` role | `K109_BUSL1_PB0` selects the branch (`K109(ON)` in the BST path, `K109(ON)` + `K110(NC)` for PB0) | closed | `:43`, `:109`; `StdAfx.h:278` |

Resulting TM600 SetOn:
`K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1`

> **Locator substitution, flagged not hidden.** The task and review addendum cite contract `L145` and `L1897`.
> Those are line numbers in the reviewer's contract excerpt; the artefact this payload actually references is the
> JSON `setup-contract.json`, where I verified the same authorities **by path and value** —
> `tmDeltas.TM600.pinRouteTable./BST/…CH0 Low.needsClosed = [109,110,138,139,145,146]`,
> `/BST/…CH1 Low.needsClosed = [109,110]`, `aliasFlatTable[3].relayPath = "K110_ACM18_BST -> K61_ACM8_SW"`,
> and `aliasResolution[3].resolution.relayChain` naming `K110_ACM18_BST` "SetOn (ACM200 S5_FH18 -> BST)".
> I did **not** assert `L145`/`L1897` as verified because I could not confirm those line numbers in my copy —
> the semantic authorities are identical, the citation form is not.

## 2b. PER-FUNCTION JUSTIFICATION (captain-mandated: no silent single-place edit)

### TM600 — closes K109 **and** K110

| Authority | Requires | Locator |
| --- | --- | --- |
| `tmDeltas.TM600.pinRouteTable./BST/…CH0 Low` | `[109,110,138,139,145,146]` | contract rev 24 |
| `tmDeltas.TM600.pinRouteTable./BST/…CH1 Low` | `[109,110]` | contract rev 24 |
| `tmDeltas.TM600.relaySet` | contains **109** and **110** | contract rev 24 |
| `aliasResolution[3]` (bst2sw) `relayChain` | `K110_ACM18_BST` "SetOn (ACM200 S5_FH18 -> BST)" | contract rev 24 |
| `aliasFlatTable[3].relayPath` | `K110_ACM18_BST -> K61_ACM8_SW` | contract rev 24 |
| Connect map CH0 route | `CH0 Low -> BST 需闭合: K109,K110,K138,K139,K145,K146` | `SCH-Connect-Map.txt:42`; path at `:43` |
| Connect map CH1 route | `CH1 Low -> BST 需闭合: K109,K110` | `:268`; path at `:269`/`:270` |

### TM601 — does **NOT** close K109/K110, and this is a finding from the contract, not an omission

| Authority | Finding | Locator |
| --- | --- | --- |
| `tmDeltas.TM601.pinRouteTable` | node set is SW, PGND, PMID, VBUS, VBAT, VDRV, V1P5, AGND — **there is no BST node at all**, so the item declares no BST route and no BST `needsClosed` | contract rev 24 |
| `tmDeltas.TM601.relaySet` | `[3,7,60,61,83,86,130,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,154,155]` — **contains neither 109 nor 110**, whereas TM600's set contains both | contract rev 24 |
| `tmDeltas.TM601.ateStimulus` | `{vbat 4.2 V, pmid 9 V, vdrv 5 V}` only; **no bst2sw stimulus**, and `bst2sw` occurs **0** times in the whole TM601 delta | contract rev 24 |
| `tmDeltas.TM601` text | its single "BST" string is the register field `D2A_BUBO_TM_LSON`, **not a powered rail** | contract rev 24 |
| Connect map | the BST routes (`:42`/`:43`, `:268`/`:269`) are channel routes; this item drives SW (`:174`) and PGND (`:156`) and reaches no BST pin | `SCH-Connect-Map.txt` |

**Why the distinction is physical, not pedantic:** the ACM200 bootstrap source only reaches BST when K110 is closed — `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` (`:724`), `SH18 -> K110(NC) -> PB0_S` (`:725`), versus the BST path `K109(ON) -> K110(ON) -> BST_F` (`:43`). TM601 never drives that rail, so actuating K109/K110 there would be an unmotivated relay closure — exactly what the minimal-endpoint rule forbids — rather than a repair.

### Minimal-endpoint discipline (verified item by item)

(a) **Only contract-authorised relays added.** No relay outside TM600's `relaySet` and the BST `needsClosed` sets was introduced: the closure is exactly `K109_BUSL1_PB0` + `K110_ACM18_BST` on the TM600 list, both of which are in `tmDeltas.TM600.relaySet` and in the route table.
(b) **No negative-list relay touched.** Executable-code check: `K87`/`K88`/`K89`/`K131`/`K132`/`K133` appear **nowhere** in either SetOn list (those are the Relay-NC default-conducting parts and must stay un-actuated).
(c) **No composite macro.** `K_FPVIH_TO_BST_B` and `K_FPVIL_TO_SW_B` occur **0** times in executable code, consistent with ruling (ii) recording that route as unrealisable.

## 3. Negative-list and composite-macro checks

- `K109`/`K110` are **not** in the forbidden 87/88/89/90/91 class (defines: `StdAfx.h:278 K109_BUSL1_PB0 109`,
  `:279 K110_ACM18_BST 110`), so closing them conflicts with no negative-list rule.
- The unrealisable ch1 composite is **not** used: `K_FPVIH_TO_BST_B` count in executable code = **0**.

## 4. ⚠ THREE CONTRACT INCONSISTENCIES FOUND WHILE DOING THIS (not mine to fix)

Flagged rather than silently resolved, per this run's discipline. The contract owner should reconcile:

1. **`Narrowly vs route** — `aliasResolution[3].resolution.closedRelayNumbers` = `[110, 61]` while the route
   that actually reaches BST on CH0 Low requires `[109,110,138,139,145,146]` (`pinRouteTable`, `:42`).
   `K109` is absent from the narrow set although it is in `tmDeltas.TM600.relaySet`. I closed both K109 and
   K110 to satisfy the route table and the connect map.
2. **Terminal assignment vs route table** — the `bst2sw` resolution declares `terminalAssignment.high = BST`
   / `nodeOnHighTerminal = BST`, which is the **FPVIe CH1** framing (`CH1 High -> BST needsClosed [109,110]`,
   `:268`, and `pinRouteTable` CH1 High = `[131,132,134,135]`). But ruling (ii) puts the drive on the
   ground-referenced **ACM200 `SW12_U1REF_BST_ACM`**, and `SW12_U1REF_BST_ACM.Set(FV, …)` is an FV command
   on that instrument, not an FPVIe terminal pair. The ACM path's manual locator is `SCH-Connect-Map.txt:501`
   (`PGND ← S10_CH0_A 需闭合: K141,K154,K155` — a QTMU route) which is not the path in use, so **which
   terminal arrangement the ACM drive uses is not established by the contract text**; the closure set I
   applied (K109/K110 = the BST branch selectors) is the one the route table and connect map require
   regardless. What I **did** resolve: which relays to close (the route table plus the connect map agree on
   K109/K110). What remains **open and is not mine to settle**: which terminal carries BST under the ACM
   drive, which the contract text does not establish — it must be reconciled by the contract owner so a
   later reader does not infer from `terminalAssignment` that an FPVIe channel pair is in play.
3. **`CH0 High -> BST` route exists but is unusable without also closing `[46,48,76]`** (`:39`), which is the
   composite associated with the unrealisable ch1 class; the payload does not use it.

## 5. Invariants (comments stripped) — all unchanged

`delay_ms(1)` ×6 · `delay_ms(2)` ×0 · `SetClamp(50, 50)` ×2 · `MeasureVI(200, 5, FPVIe_MV_X10)` ×2 ·
bare `126` ×0 · `K126_V1P5_CAP` ×2 · `ERROR_RES` ×2 · `K5_VBUS_Cap`/`K44_Cap_SW2_BST2`/`K45_Cap_SW1_BST1` ×0 ·
`K57_CAP_BST_SW` ×2 · `rampi_capv`+`rampv_capv` ×0 · `K109_BUSL1_PB0` ×1 · `K110_ACM18_BST` ×1 ·
BOM present, CRLF, **0 lone LF**.

## 6. Gate evidence (workspace sandbox rebuilt from the target with this payload substituted in)

| Gate | Result |
| --- | --- |
| `verify_relay_trace.py --meta` | **PASSED** — `FR-001 反向` = **2**, and only the **two pre-existing `TM643`** warnings remain. The previous revision showed **3** (an extra TM601 VBUS/K5 warning); adding K109/K110 **removed** it, i.e. this change is net-negative for warnings as well as closing the defect |
| `verify_bst_sw_sequence.py` | **PASSED** — `targets=4 FAIL=0`, `BST>=SW and 0<=BST-SW<=5V` |
| `verify_awg_params.py` | **PASSED** — `FAIL=0 WARN=0` over 42 AWG functions |

Sandbox copy: 471004 B / `f8ec66d2a46b7a4d2ed9f2bb3d15260ef4f578383ccefdb457fbc69ca0e1ccf7`.
**New red: 0.** Range table unchanged: `PMID_HG2` 10 V steps remain `FXVIe_PLUS_20V`; violations = 0.

## 6b. Payload revision history (kept as history, never deleted)

| revision | size | sha256 | note |
| --- | --- | --- | --- |
| **t29 (current)** | 36381 B | `73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e` | TM600 closes K109/K110 — the BST excitation path |
| t23 (deployed) | 35014 B | `444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c` | K126 fix + ERROR_RES fail-closed + positive-magnitude sign + ranges; TM600 SetOn lacked K109/K110 |
| t21 rev3 | 32969 B | `7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b` | K5/K44/K45 removed per the t22 ruling |
| t21 rev2 | 34788 B | `f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509` | sign / ERROR_RES / range corrections |
| t21 rev1 | 28726 B | `c8bf3b3e693673bb92c04fc7c34d8529a1c2a02c785fbaa507f2387956fcd86e` | stabiliser caps added (later reverted by t22) |
| t20 | 28222 B | `7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122` | payload as delivered at t20 |

The predecessor contents are recoverable from this run's revision trail and are recorded here rather than in a
separate directory, because this task's in-scope paths are the payload and this document only.

## 8. Deployed-tree state at the time of this repair (measured, not relayed)

`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` = **469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**, mtime **2026-09-16 18:53:33**.

Measured facts (my own read, cross-checked because a relayed description differed):

- `DUT_API int TM600_HS_RDSON` occurs **1** time, at **L9057**; `DUT_API int TM601_LS_RDSON` occurs **1** time,
  at **L9217**. (A relayed reading claimed 2 occurrences each; that is not what the file contains.)
- **L9081** `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1)`
  closes 60, 61, 83 — the PMID side — and **neither K109 nor K110**.
- **L9255** closes `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` — 154, 155, 60, 61.
- `K109_BUSL1_PB0` = **0** and `K110_ACM18_BST` = **0** occurrences: the deployed build predates this repair.

**Conclusion:** the write HAS happened (executor = the captain under the agreed split), and it landed the
**t23** revision — the `K126_V1P5_CAP` rename and the `ERROR_RES` fail-closed guard are present. It therefore
**carries the t29 defect** (BST excitation path unclosed), and `afterSha256` for THIS repair must not be filled
with `15c7d2b8…`: that hash belongs to the superseded revision, and recording it as the after-state of the
K109/K110 payload would assert a landing that has not happened.

## 7. Scope, authorship, open items

Only `implementation-payload-TM600-TM601.cpp` and this document were written. `devel`, the target tree,
`project/DALI/meta`, `scripts/`, the contract, the plan and `implementation-manifest.json` were **not**
touched. Independent review is owed by rule-reviewer (the author must not self-approve); landing is the
captain's, with **REPLACE** semantics on the TM600/TM601 region. **A compile closed loop is not electrical
sign-off**, and no instrument/hardware validation is authorised for this delivery.
