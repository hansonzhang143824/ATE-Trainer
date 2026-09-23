# TM109 Test Method Contract

- Revision: 1
- Role: test-method-expert
- Task: TM109-METHOD-R1
- Verdict: `deliverable_ready`
- Signed input: `team/artifacts/tm109-direct-trial/strategy/tm109-resource-config-contract.json`
  - sha256 `a22502ece50f321312a466b77cfef5a40efe8f9a41995f7ee8af3b44048107e2` (verified with `python scripts/hash_ate_plaintext.py`)

## Item

| Field | Value |
| --- | --- |
| projectId / tm | DALI / TM109 |
| parameter base | VAC2_PRST (DFT ShortName) |
| parameters | VAC2_PRST_Rise (V), VAC2_PRST_Fall (V), VAC2_PRST_Hys (mV) |
| projectType | normal (一般测试项目) — from the signed strategy contract |
| parameterType | UVLO family, PRST — from the signed strategy contract |
| DFT intent | Hardware_initial vset[vbat,4.2,...]; Dynamic vset[vac2, 3.8 / 4.4 / 4.1 / 3.5]; Check INT; Software_initial entertestmode + I2CWriteSameData(DEV_ADDR,0x55,0x96); ExpectValue "rising vth 4.15V, hys 0.35V" |
| stimulus form | two-segment threshold sweep: up 3.80 -> 4.40 V (TRIG_RISING), down 4.40 -> 3.50 V (TRIG_FALLING); the four DFT levels are visited in DFT order and no voltage outside their span is applied |

The four DFT levels are used as the envelope and level order; the continuous sweeps between them are a method decision (the discrete form only brackets the thresholds and cannot produce Rise/Fall/Hys). It remains the documented fallback if a ruling forbids the ramp form.

## Resource boundary (strategy-owned, copied verbatim — not changed here)

| Endpoint | Source | Ports | Closure | Relay group |
| --- | --- | --- | --- | --- |
| VBAT | FXVIe_PLUS S3 ch5 | FH5 force + SH5 sense | {} (K8_PD3 un-actuated) | RG-1 |
| VAC2 | ACM200 S5 ch0 | FH0 force + SH0 sense | {K19_VAC2, K70_VAC_F} | RG-2 |
| INT | ACM200 S5 ch15 | FH15 force + SH15 sense | {} (K102_PC3 un-actuated) | RG-3 |

Register delta (verbatim): `entertestmode()` then `I2CWriteSameData(DEV_ADDR, 0x55, 0x96)`.

## Phases

| Phase | Name | Key content |
| --- | --- | --- |
| MP-1 | pre-state verification | all sources off/0 V, no relay actuated, read-back gate |
| MP-2 | equipotential route closure | close {K19,K70} while every source is at 0 V; K18/K20/K68 stay open; settle >= 3 ms |
| MP-3 | VBAT initial condition | FXVIe_PLUS ch5 FV 4.2 V with Kelvin sense; settle >= 3 ms |
| MP-4 | unlock + register activation | entertestmode then 0x55 = 0x96 with VAC2 still below 4.15 V; monitor armed; settle >= 1 ms |
| MP-5 | VAC2 preset 3.80 V | DFT step 1; capture the pre-sweep observation state |
| MP-6 | rising sweep 3.80 -> 4.40 V | 10 mV step, <= 1 V/ms, >= 10 us per step, TRIG_RISING, latch VAC2_PRST_Rise |
| MP-7 | falling sweep 4.40 -> 3.50 V | same step, TRIG_FALLING, latch VAC2_PRST_Fall |
| MP-8 | calculation and judgement | Hys = (Rise - Fall) * 1e3 mV; per-site publication |
| MP-9 | ordered power-down | VAC2 -> 0, VBAT -> 0, >= 200 us, then open {K19,K70}; no register writes |
| MP-10 | exception cleanup | unconditional same order plus failure context, item left failed |

Every phase carries prerequisite, relayGroup, resourceState, registerActivation, actualNodeVoltages, differentialChecks, bstSwCheck, setpoint, ramp, delay, sample, exitCondition, onFailure and evidence.

## BST-SW constraint

The rule `0 V <= BST_actual - SW_actual <= 5 V` is evaluated in every phase and returns NOT_APPLICABLE for this item, because no endpoint, allocation, relay group or register field of the signed contract addresses BST or SW, and the project gate `scripts/verify_bst_sw_sequence.py` only targets functions containing a `rampi_capv` current ramp (empty PASS otherwise). If a ruling binds the DTEST0_MUX = 22 pad to a BST or SW node, the check becomes applicable and every phase must be re-proved with both node potentials derived from the actual route and drive state.

## Limits

| Parameter | Nominal | Source | Judgement |
| --- | --- | --- | --- |
| VAC2_PRST_Rise | 4.15 V | DFT ExpectValue text (FACT) | PENDING_LIMIT_RULING — no tolerance is stated (TM109-OI-2) |
| VAC2_PRST_Fall | 3.80 V | DERIVED = Rise - Hys (the DFT states no falling value) | LOG_ONLY_PENDING_RULING |
| VAC2_PRST_Hys | 350 mV | DFT ExpectValue text (FACT) | PENDING_LIMIT_RULING |

Capture uncertainty is +/- 10 mV per threshold (one sweep step) and up to +/- 20 mV on the derived hysteresis. No tolerance is invented.

## Golden applicability

`partial`. `L4-Golden-code/UVLO.cpp` is the same parameter family (it even declares VAC2_PRST parameters) and supplies the method skeleton: ordered power-up, rail pre-set below the swept level, unlock then register write, one up-sweep plus one down-sweep with a latched capture, Hys = (Rise - Fall) * 1e3 mV, and levels to 0 V before the relays open. The DFT operation point, resources, observation instrument, sweep parameters, register set and limits all differ and are rewritten from the signed contract. `toggle-template.cpp` is the same source snapshot and `OVP.cpp` is family corroboration only.

## Routed findings (recorded, not repaired — the signed strategy is not edited)

| Id | Severity | Issue | Owner |
| --- | --- | --- | --- |
| RF-01 | high | VBAT Cap2 / 稳压 role relay identity is absent from the signed boundary although FR-001 closes the capacitor of a powered PIN by default | test-strategy-architect (schematic-expert closes it) |
| RF-02 | high | the Toggle observation closure for INT is empty: the framework needs an observation plus pull-up relay pair, the pad structure is unknown, and no pull-up identity exists in the frozen table | test-strategy-architect (schematic-expert closes it) |
| RF-03 | medium | the DTEST0_MUX = 22 observation pad is not bound to a DUT pin by any frozen deliverable | user ruling / strategy owner |
| RF-04 | low | strategy open item OI-S-03's description is stale versus revision 2 (documentation only) | test-strategy-architect |

## Conflicts

- CF-M1: the trigger-edge convention for a threshold ramp differs between two active standards. Adopted: TRIG_RISING on the ascending sweep and TRIG_FALLING on the descending sweep, per the user-confirmed rule and the executable family Golden; the parameter naming (Rise from the ascending sweep, Hys = Rise - Fall) is identical in both sources.
- CF-M2: no new conflict with the signed strategy contract; its conflicts C-01 to C-07 and open items are carried forward unchanged.

## Environment note (hashing)

For the DLP-protected artifacts, PowerShell's native hashing path (`Get-FileHash`, .NET SHA256, `certutil`) returns a different digest of the same byte length than the plaintext readers. All hashes in this deliverable use `python scripts/hash_ate_plaintext.py` / `Path.read_bytes()`, which is the project's documented plaintext reader and which reproduces the hash the strategy role signed.
