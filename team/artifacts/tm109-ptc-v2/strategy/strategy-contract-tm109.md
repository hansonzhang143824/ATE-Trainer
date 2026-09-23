# TM109 strategy contract - VAC2_PRST (resource and configuration contract)

> Role: test-strategy-architect | Stage: STRATEGY | Project: DALI | TM: TM109
> Generated: 2026-09-18 01:14:16 +08:00
> Machine-readable primary artifact: `strategy-contract-tm109.json` (same directory)
> Binding: `team/artifacts/tm109-ptc-v2/input-manifest.json` -> canonicalInputs.intentResolution (status `resolved`) governs every TM109 DFT conflict. No DFT conflict was resolved by this role's own reasoning.

## 1. Item frame

| Field | Value | Evidence |
|---|---|---|
| Item / ShortName | TM109 / VAC2_PRST | DFT.csv:30 |
| Project type | general test item (Toggle / threshold AWG) | DFT Type = "Toggle, MV"; test-types.md #7 |
| Parameter type | UVLO family - PRST (power-on reset threshold) | test-types.md #4; OVERVIEW:148 |
| Function architecture | single-pin threshold toggle: one swept voltage channel on VAC2, comparator output muxed to DTEST0, captured as a logic toggle on an open-drain pad | OVERVIEW:149-150; DTESTMAP:23 |
| Static supply | VBAT = 3.0 V | binding (intentResolution) |
| Swept pin | VAC2 | binding; DFT.csv:31-34 |
| Register writes | 0x56 = 0x15 (DMUX_EN=1, DMUX_SEL=21 -> a2d_vac2_prst), 0x57 = 0x08, entertestmode() | binding; reg_config/tm109.sv:12-15 |
| Monitor intent | DTEST0 / nQON logic toggle | binding monitorIntent; TestIO:2 |

## 2. Endpoints, sources and routes (all four routes are accepted project path proofs)

| PIN | Role | Source table / object | Channel | Route (force / sense) | Relays to energize |
|---|---|---|---|---|---|
| VBAT | static supply, Kelvin F/S | FXVIe_PLUS / `VBAT_PD3_FXVI` | ch5: S3_FXVIe_PLUS_FH5 / SH5 | FH5 -> K8_PD3 (NC) -> VBAT_F ; SH5 -> K8_PD3 (NC) -> VBAT_S | none |
| VAC2 | swept stimulus, Kelvin F/S | ACM200 / `VAC123_AMUX_ACM` | ch0: S5_ACM200_FH0 / SH0 | VAC_FORCE_S1 -> K18_VAC3 (NC) -> K19_VAC2 (ON) -> VAC2_F ; VAC_SENSE_S1 -> K18 (NC) -> K19 (ON) -> VAC2_S | `K19_ACM0_VAC2` |
| nQON (DTEST0 pad) | monitor, open-drain capture | ACM200 / `NQON_HG1_ACM` | ch9: S5_ACM200_FH9 / SH9 | FH9 -> K64_ACM9_HG1 (NC) -> nQON_F ; SH9 -> K64 (NC) -> nQON_S | none (+ functional `K65_nQON_PU`) |
| INT_PA0 | monitor, alternative reading of the DFT Check literal | ACM200 / `PA0_PC3_ACM` | ch15: FH15 / SH15 | FH15 -> K102_ACM15_PC3 (NC) -> INT_F ; SH15 -> K102 (NC) -> INT_S | none |

Routing rationale: no differential pair and no high current, so relay-design-flow step 3 takes the non-scarce branch (ACM200 / FXVIe). Every selected route is the shortest available for its pin and needs at most one SetOn relay. The anti-short rule selects the channel that reaches only the target pin, which is why VAC2 uses VAC123_AMUX_ACM (channel 0) and not a floating-source bus entry.

## 3. Relay group G1 (single group, no time division)

**SetOn closure (exclusive - every relay not listed stays de-energized):**

```
K13_VBAT_Cap   (13)  functional: VBAT regulation capacitor, default-closed for a powered PIN
K19_ACM0_VAC2  (19)  path: ACM200 channel 0 -> VAC2 share relay, the only VAC2 selector
K65_nQON_PU    (65)  functional: nQON/DTEST0 open-drain pull-up, mandatory to read a high level
```

**Isolation / mutual exclusion requirements (must remain de-energized):**

| Relay | Reason |
|---|---|
| K18_ACM0_VAC3, K20_ACM0_AMUX | same VAC share tree; energizing either would move the channel to VAC3 / AMUX |
| K21_VAC_Cap | VAC regulation capacitor on the swept VAC node - ramp-source Cap exemption |
| K8_FOVI5_PD3 | its NC contact routes FXVIe ch5 to VBAT; energizing it would route the supply to PD3 |
| K64_ACM9_HG1 | its NC contact routes ACM200 ch9 to nQON; energizing it would route the monitor to HG1 |
| K17_BUSL_VAC, K70_R5M_VAC_F | FPVIe low/high bus entries to the VAC node; must stay open to keep the scarce floating bus off the swept pin |
| K14/K15/K16 (VAC1/VAC2/VAC3 P2P) | P2P-to-AGND shorts are not needed and K15 would ground the swept pin |
| K66_TMU_nQON, K62_BUS0_FH_QON | alternative nQON entries, not used |
| K102_ACM15_PC3 | relevant only if the INT alternative monitor channel is selected instead |

Global conflict check: three independent resources (FXVIe_PLUS ch5, ACM200 ch0, ACM200 ch9), no shared relay, no shared bus, no non-target DUT pin driven. Time-division is not required.

## 4. Register delta

| Address | Value | Fields | Source | Scope |
|---|---|---|---|---|
| 0x56 | 0x15 | DMUX_EN=1, DMUX_SEL=21 (a2d_vac2_prst -> DTEST0) | binding; reg_config/tm109.sv:14; DTESTMAP:23 | TM109 |
| 0x57 | 0x08 | field name not documented (open item TM109-OI-1) | binding; reg_config/tm109.sv:15; append_tm108_112.py:144 | TM109 |
| mode entry | entertestmode() | - | DFT.csv:30; reg_config/tm109.sv:12 | TM109 |
| 0x55 | 0x96 | EN_DTEST0=1, DTEST0_MUX=22 | DFT-source evidence, **recorded not used** - superseded by the binding (TM109-C2) | evidence only |

## 5. Conflicts

| ID | Kind | Status | Handling |
|---|---|---|---|
| TM109-C1 | DFT stimulus pin (vac3 vs VAC2) | resolved_by_binding | swept pin = VAC2; the copied VAC3 field is evidence only |
| TM109-C2 | register map (0x55=0x96 vs 0x56=0x15 / 0x57=0x08) | resolved_by_binding | only the binding's writes are in the contract |
| TM109-C3 | VBAT value (DFT 4.2 V vs project 3.0 V) | resolved_by_binding | VBAT = 3.0 V |
| TM109-C4 | expected limit (4.15 V vs 4.4 V) | open - not this role's domain | recorded for the method expert / user |
| TM109-C5 | monitor pin literal (INT vs DTEST0/nQON) | open - non-blocking | primary nQON, alternative INT/PA0; relay closure identical |

## 6. Open items

- **TM109-OI-1** (low): field name/meaning of 0x57 = 0x08 is undocumented; the value itself is authoritative.
- **TM109-OI-2** (medium): monitor pad literal INT vs nQON (see TM109-C5).
- **TM109-OI-3** (high): rising-threshold limit conflict 4.15 V (DFT) vs 4.4 V (OVERVIEW); hysteresis 0.35 V agrees.
- **TM109-OI-4** (low): cross-site (_S1S2) relay arbitration is not modelled in the source IR; K19/K65 are declared on the site-1 instances.
- **TM109-OI-5** (low): unpublished relay contact current rating and sense-path series resistance; neither binds a voltage-only threshold test.

## 7. Handoff

Next role: **test-method-expert**. The resource allocation, the single relay group G1 with its exclusive SetOn closure, the isolation requirements and the register delta above are fixed. Phases, ramp timing, trigger edge, sampling, calculation, limits, power-down and Log are the method expert's to design inside these boundaries; any need outside them returns to test-strategy-architect rather than being substituted.
