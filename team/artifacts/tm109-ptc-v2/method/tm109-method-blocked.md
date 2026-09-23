# TM109 METHOD stage — BLOCKED, routed finding to test-strategy-architect

- **Stage:** METHOD (role: test-method-expert), task `TM109-METHOD-PTC-V2`
- **Status:** BLOCKED (no method contract written on purpose)
- **Terminal report:** `BLOCKED: TM109; evidence: team/artifacts/tm109-ptc-v2/method/tm109-method-blocked.json; question: see below`
- **Machine-readable twin:** `method/tm109-method-blocked.json`
- **Signed input used:** `strategy/tm109-resource-config-contract.json` sha256 `7b91ac7ad86e8c0aa63d69d9e4a70c9819b49579617b4c3c1726869cbdbc1a44` (recomputed = the hash recorded in `strategy/deliverable-ready.json`; the contract was read, not modified)

## 1. What is blocking

The signed observation endpoint for EP-3 is the DUT pin **INT** (`PA0_PC3_ACM`, S5 ch15, pull-up `K103_PA0_PU` + `K128_FOVI7_PU_PS`).
The toggle that TM109 must capture is **V(DTEST0)** — the DFT `Check` field, the DFT meta note `check int pin toggle`, and the resolved register delta (0x56=0x15 = DMUX_EN, 0x57=0x08 = DMUX_SEL 21 = `a2d_vac2_prst`, `_dump_DTESTMAP.txt` line 23) all describe the same signal: the `a2d_vac2_prst` status routed onto the **DTEST0** output.

Five current-project sources agree that **DTEST0 is a pad function of nQON**, and the netlist shows **INT_PA0 and nQON are two different DUT Kelvin contacts with two different pull-ups**. A capture on the signed INT_PA0 node would therefore probe a node the mux registers do not drive — no toggle, no Rise/Fall/Hys. Trigger polarity, sampling or limits cannot repair a wrong observation node.

This is exactly the trigger the signed contract wrote into itself (`conflicts.CF-4`, lines 754-755):

> "If the test-method or review stage obtains current-project evidence that the DTEST0 output is physically presented on the nQON pin, the monitor route and its pull-up must be switched together by returning a routed finding to test-strategy-architect; the register delta and the monitor intent are unaffected."

Changing a source table, channel, route or relay/pull-up set is outside this role's boundary (test-method-expert.md line 3/10, strategy handoff `returnRule`), so the decision is returned instead of silently taken.

## 2. Evidence

| # | Source (locator) | Fact |
|---|---|---|
| E1 | `project/DALI/_archive/_dump_TestIO.txt` line 2 (sheet date `update 2026/02/27`) | `nQON  DTEST0  SCAN_OUT` — the project's own test-IO table puts the DTEST0 function on the nQON pad |
| E2 | `project/DALI/_archive/_dump_DTESTMAP.txt` line 1 + line 23 | `Reg_DTEST0_general` mux, `21 a2d_vac2_prst` — the signed `DMUX_SEL=21` writes a2d_vac2_prst onto the DTEST0 mux |
| E3 | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` TM109 block 2317-2393 (closure 2339, capture 2358-2364; header note 2320) | current project regression code for **this item** observes `V(DTEST0)=nQON toggle` on `NQON_HG1_ACM` with `K65_nQON_PU`; `PA0_PC3_ACM`/`K103`/`K128` are not used (sibling TM108, lines 2257-2266, identical) |
| E4 | `knowledge/hardware/relays.md` lines 142, 150 | PU (open-drain) rule; DALI instance `K65_nQON_PU` (nQON/DTEST0 上拉) is closed by the functions that observe DTEST0 — **explicitly including the TM105~113 threshold family** |
| E5 | `knowledge/references/L0-ate-primer.md` line 13 | project pad mapping (user-confirmed): `DTEST0 -> nQON`, open-drain, needs `K65_nQON_PU` |
| E6 | `project/DALI/SCH-Connect-Map.txt` 798-800, 891, 702-704, 885, 927-929 | nQON reached from `S5_ACM200_FH9/SH9` via K64 NC (zero actuations), fixed-5V pull-up `R_nQON_PU_S1` via K65; INT_PA0 reached from `S5_ACM200_FH15/SH15` via K102 NC with the PA0 source-meter pull-up K103+K128 |
| E7 | `project/DALI/Component-Statistic.txt` line 61 | DUT Kelvin pins include `INT`, `PA0` **and** `nQON` as separate contacts |
| E8 | signed strategy contract RA-3, setOnClosure, RG-3 (isolation bullet line 627), CF-4, OI-1 | the contract itself keeps `K65_nQON_PU` un-actuated ("not a target pin of this item") and holds the nQON route as the fully specified alternative |

## 3. Minimal change requested from test-strategy-architect

1. `EP-3`: pin `INT` -> `nQON`; role/requirement text unchanged (monitor of the logic toggle).
2. `RA-3`: `PA0_PC3_ACM` -> `NQON_HG1_ACM` (ACM200, SITE_1 port S5, channel 9, ports `S5_ACM200_FH9` / `S5_ACM200_SH9`); route actuations stay **zero** (K64 NC conducts; closing K64 would select HG1_F/HG1_S, SCH-Connect-Map 699-701).
3. `RA-3.functionalActuations`: `K103_PA0_PU` + `K128_FOVI7_PU_PS` -> `K65_nQON_PU` (S34_CBIT65, ON, fixed-5V `R_nQON_PU_S1`).
4. `setOnClosure`: `[13,19,103,128]` -> `[13,19,65]`; RG-3 relays `{65}`; single-SetOn-call rule unchanged.
5. Isolation list: K65 out of the keep-open set; K103/K128 into it (K101/K102 stay).
6. `OI-2` (pull-up source drive level) becomes moot — the nQON pull-up is a fixed 5 V rail, not an FXVIe_PLUS PU-PS tap.
7. `CF-4` status -> resolved on the nQON side, with the DFT `Check` field `INT` recorded as the conflicting field.

**Not affected:** register delta `0x56=0x15`, `0x57=0x08` after `entertestmode()` (the mux target is precisely what nQON carries); VBAT 3.0 V static supply (RA-1/RG-1); VAC2 swept rail (RA-2/RG-2, K19 ON, K18/K20/K21 un-actuated, AGND_F return); exclusive SetOn semantics.

## 4. Method-owned items deliberately left open

Capture level, per-segment trigger edge, sweep windows/sample count/interval, pass/fail limits (the DFT publishes `rising vth 4.15V, hys 0.35V` with **no tolerance** — none is invented), Log fields, and the three-step power-down plan. Every one of them depends on which physical node is observed and which pull-up feeds it, so none is fixed before the route is signed. No value in this report may be implemented. BST/SW is not applicable to TM109 (the DFT row declares neither node).

## 5. Self-verification run (deterministic)

| Gate | Command (cwd `D:/Newtest/DSH/ATE-Coding-Plat`) | Result |
|---|---|---|
| ABI checker named by `team/ptc/OUTPUT_CONTRACTS.md` | `python scripts/validate_ptc_output_contracts.py` | exit 0, prints `PASS` |
| Stage gate | `python scripts/ate_ptc_runner.py --tm TM109 --trial-dir team/artifacts/tm109-ptc-v2 --command next` | exit 0, `state=METHOD, dispatch=test-method-expert` — the stage is still correctly open, no false handoff exists |
| Input integrity | `Get-FileHash -Algorithm SHA256 .../strategy/tm109-resource-config-contract.json` | `7b91ac7a...c1a44` = hash recorded in `strategy/deliverable-ready.json` |

## 6. The one question

> Will you re-sign **EP-3/RA-3** (and the SetOn closure) onto the DTEST0 pad route that your own **CF-4** already specifies — `NQON_HG1_ACM` channel 9 (`S5_ACM200_FH9/SH9`), `K64` un-actuated, `K65_nQON_PU` closed, closure `{13,19,65}` — given that the DTEST0 output driven by the binding register delta (`0x56=0x15`, `0x57=0x08` / `DMUX_SEL=21` = `a2d_vac2_prst`) is presented on the nQON pad, not on the INT/PA0 node, so the signed INT allocation cannot capture the toggle?
