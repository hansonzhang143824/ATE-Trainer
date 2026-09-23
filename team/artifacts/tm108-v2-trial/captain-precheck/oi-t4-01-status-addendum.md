# Captain addendum — OI-T4-01 status correction (TM108 trial)

Authority: user ruling §7 of `protocol-runtime-memory.md:94-99`, which states that OI-T4-01
(`DTEST0` unproven, zero hits in the schematic three-artifact set) and DFT conflicts F1-F6
"remain unresolved and may not be resolved by any agent".

## 1. Reported contradiction

`test-strategy-architect` (protocol compliance report, TM108) reports that artifact
`team/artifacts/tm108-v2-trial/dft/dtest0-oi-t4-01-resolution.md` labels OI-T4-01 as
`部分关闭` ("partially closed") at its ruling sections (`:14-68`, especially `:25-49`) and in its
open-items row (`:171`). That label is a status change to a user-frozen item.

## 2. Captain ruling (record correction, not artifact edit)

OI-T4-01 remains **UNRESOLVED** by ruling. No agent may close, partially close, or relabel it.
The t6 artifact's substantive evidence stands as evidence; its status label does not carry authority.

The member artifact is deliberately left byte-unchanged: silently rewriting another role's signed
artifact would itself be a violation. This addendum is the authoritative status record.

## 3. Preserved evidence (FACT, not a closure)

- `project/DALI/_archive/_dump_TestIO.txt:2` — `nQON | DTEST0 | SCAN_OUT` (archived snapshot, 2026-08-06, sha 7fd842e6…).
- `project/DALI/_archive/_dump_DTESTMAP.txt:24,25` — index 22 = `a2d_vac1_prst`, index 23 = `a2d_vbat_uv_ok` (sha 9edd814e…).
- `project/DALI/meta/manifest.json:60,:63` — declares the current workbook's `TestIO` (7 rows) and `DTESTMAP` (75 rows);
  row counts agree with the archived snapshots.
- `project/DALI/input/PINLIST.txt:1-39` — `DTEST0` absent as a pad (`:10` = `INT`).

## 4. What this evidence does and does not establish

Establishes (relation level, from an archived carrier):
the DFT check pin `DTEST0` maps to DUT terminal `nQON` in the workbook's own pin-map sheets.

Does NOT establish:
- that the mapping is carried by the current three-artifact set (it is not);
- the current-workbook cell contents for `TestIO` / `DTESTMAP` (registered as OI-T6-02);
- the mux field value (`DMUX_SEL` 22 vs 23, OI-T4-10) or its bit definition;
- the 1.65 V trigger level (OI-T6-03, no DFT basis).

Therefore no downstream stage may consume the observation allocation on this basis alone.

## 5. Open items after this addendum

- OI-T4-01: UNRESOLVED (user-frozen).
- OI-T6-02: current-workbook `TestIO`/`DTESTMAP` carrier absent — closure requires a plain-text dump of those two sheets (needs xlsx-sheet reading capability the run does not have).
- OI-T6-03: 1.65 V trigger level has no DFT evidence.
- OI-T4-10/11/13/14 and F1-F6: unresolved, both sides retained, no averaging, no side selection.
- OI-T4-16: recorded, not delegated; no Setup change authorized.

## 6. Pending user rulings

B-1 (TestIO/DTESTMAP carrier + whether the archived mapping may be used as evidence),
B-2 (1.65 V source), B-3 (mux 22 vs 23), B-4 (implementation/build target under the
`D:/PROJECT6-DALI/devel` write denial), and the F1-F6 set.

## 7. t5 disposition (captain, per §7)

`t5` remains permitted to finish only its already-claimed atomic output and must not send
`deliverable_ready` downstream. Its §3 trigger was never issued and will not be issued while
the suspension and the unresolved conflicts persist.
