# Captain notes for `t7` (TM108 implementation) — pre-rulings, no new electrical facts

Written 2026-09-17 while `t7` runs. These notes resolve **ambiguity about which artifact owns a
question**; they introduce no new electrical value and no relay/mux/register/limit decision.

## 1. `RT-4` (missing tolerance) is spec-side, not code-side

- R3's own `limits` section (`tm108-test-method-contract.md:476-482`) states: *"This contract
  therefore states which threshold text is authoritative and that the tolerance does not exist; the
  pass/fail application (including how a missing tolerance is handled) is a spec-side decision,
  returned as RT-4 rather than invented here."*
- The DFT fact layer independently confirms no tolerance column exists
  (`dft-fact-audit.md:215` — "no numeric tolerance is stated in any DFT source").
- Consequence for `t7`: a `BLOCKED: t7` raised solely because *no tolerance is available* is
  answered by the contract itself. The implementer must implement the measurement, the calculation
  and the reporting exactly as R3 states, carry `RT-4` as an unresolved open item, and must **not**
  write any tolerance, guard band or pass/fail numeric.
- If, and only if, the implementer finds that the changed code *itself* must contain a limit
  comparison to satisfy R3, it must report that with the exact R3 reference — in which case this
  note is wrong and is withdrawn with that evidence.
- Status of this note: captain **reading of the signed contract**, not a new ruling and not a
  resolution of `RT-4` (which stays open and user-owned).

**UPGRADE (2026-09-17 21:2x) — the pre-change code confirms the reading, so this is now FACT.**
The independent pre-change image (`captain-precheck/tm108-block-before.txt`, function
`test.cpp:2155-2225`) shows the function's Step 6 is pure reporting:

```c
FOR_EACH_VALID_SITE(site)
{
    VAC1_PRST_Rise->SetTestResult(site, 0, rise_result[site]);
    VAC1_PRST_Fall->SetTestResult(site, 0, fall_result[site]);
    VAC1_PRST_Hys->SetTestResult(site, 0, hys[site]);
}
```

(`test.cpp:2218-2223`.) There is **no limit, tolerance, guard band or pass/fail literal** anywhere in
the function — limits are applied on the spec side. So `RT-4` is not a code artifact for `t7`. A
`BLOCKED: t7` on "no tolerance available" is therefore answered: implement the measurement and the
reporting, carry `RT-4`, add no tolerance.

## 2. `RT-1` (`K13`) — REWRITTEN: there is no inconsistency; `RT-1` is refuted

**This section replaces an earlier version of itself.** The earlier text repeated R3's `RT-1` claim
that R1 lists `13` in its keep-open set while also requiring it closed, and told `t7` to surface that
inconsistency. That claim is **false**, verified against R1 directly — see
`captain-precheck/rt-1-record-correction.md`.

Facts: R1 requires `K13_VBAT_Cap` closed (md `:221`, `:245` `动作（必须闭） = 13, 65`, `:313`;
json `relayGroups[G3].functionalRelays`), and R1's keep-open list **excludes 13** (md `:248` and json
`resourceSummary.keepOpenRelayNumbers` — the same 16 numbers, `13` and `65` not among them; R1's md
is 441 lines, so R3's cited `contract md :574` is out of range). Every R1 mention of K13 requires
closure. **R1 and R3 agree.**

Instruction to `t7`, unchanged in effect: implement `K13_VBAT_Cap` closed for the active phases and
released in the method's power-down, as the pre-change code already does at `test.cpp:2171`
(`cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`). Report no inconsistency, because none exists. Do not
send anything back to `test-strategy-architect` for `RT-1`.

## 3. `OI-T4-01` / `OI-T5-01` — observation endpoint

Carry, do not resolve, do not relabel. The code must not assert `DTEST0 == nQON`
(`oi-t4-01-status-addendum.md:35-41`; `tm108-test-method-contract.md:281, :664`). `DMUX_SEL=22` is
the signed contract's value and may be implemented as the contract's value; the contested `23` is
recorded only.

## 4. Next stage is prepared

`team/artifacts/tm108-v2-trial/review/t8-review-task-contract.md` is ready for immediate dispatch the
moment `t7` reports `DONE`. It is read-only, works on a copy, and requires plaintext before/after
hash snapshots.
