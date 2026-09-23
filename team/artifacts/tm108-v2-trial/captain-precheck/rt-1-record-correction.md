# Captain record correction — `RT-1` (TM108) is a FALSE finding, refuted by R1 itself

Authority: captain, under `ROLE_ROUTING.md` (the captain resolves a blocking finding and does not
relay ordinary handoffs) and following the precedent set by
`captain-precheck/oi-t4-01-status-addendum.md` §2: **a record correction, not an artifact edit.**
`method/tm108-test-method-contract.md` (R3) is deliberately left byte-unchanged
(sha256 `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7`); the member artifact's
evidence stands, but this claim in it does not.

## 1. The claim under review

R3's return item `RT-1` (`tm108-test-method-contract.md:637`) asserts, in its own words:

> "The signed contract's relayGroups[G3] states that K13_VBAT_Cap must be closed (backed by
> relay-checklist.md :27-37 for a powered rail) while the same contract's resourceSummary
> .keepOpenRelayNumbers also lists 13 in the keep-open set (contract md :248, :574; contract json
> resourceSummary)."

Its stated repair condition is "one authoritative statement of K13's state in the signed contract
(or removal from the keep-open set)".

## 2. Independent check of R1 (captain, 2026-09-17 21:2x)

R1 = `strategy/tm108-resource-config-contract.md`
(sha256 `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4`) and
`strategy/tm108-resource-config-contract.json`
(sha256 `FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9`), both re-read directly.

| Check | Result | Evidence |
|---|---|---|
| Does R1 require `K13_VBAT_Cap` closed? | **YES** | md `:245` `动作（必须闭） = 13, 65`; md `:221` G3 功能继电器 `K13_VBAT_Cap`; md `:313` "`K13_VBAT_Cap` 必须闭合"; json `relayGroups[G3].functionalRelays` = `K13_VBAT_Cap` (number 13, "VBAT stabiliser cap gate for a powered rail") |
| Does R1's keep-open list contain `13`? | **NO** | md `:248` `必须保持未动（隔离/互斥） = 14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142`; json `resourceSummary.keepOpenRelayNumbers` = exactly the same 16 numbers; `13 in list → False`, `65 in list → False` |
| Is `13` mentioned anywhere in R1 as non-actuated / keep-open? | **NO** | every R1 mention of K13 is md `:23, :119, :221, :235, :313, :321, :380` — all require closure or depend on it |
| Is the cited `contract md :574` in range? | **NO** | R1 md is **441 lines**; `:574` cannot be a reference into R1 |
| Do R1's md and json agree with each other? | **YES** | identical 16-number list in both |

## 3. Ruling

- **`RT-1` is refuted.** R1 is internally consistent about `K13`: G3 requires it closed, and the
  keep-open list excludes it. There was never a contradiction to resolve, and the claimed "13 in the
  keep-open set" is not present in any R1 form.
- **The requested repair already exists.** `RT-1`'s own repair condition — "one authoritative
  statement of K13's state in the signed contract" — is satisfied by R1 md `:221` + `:245` + `:248`
  read together, confirmed by R1 json `relayGroups[G3]` + `resourceSummary`. **No artifact needs to
  change and no owner needs to act.**
- **Authoritative K13 state for TM108:** *closed* for the item's active phases (R1 md `:245`,
  `:313`), *released* in the method's power-down P8 per R3. The pre-change code already does exactly
  this (`test.cpp:2171` — `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`).
- `RT-1` is retained on the record as a **false positive**, not as an open engineering item. It must
  not be used to withhold a review verdict or to send work back to `test-strategy-architect`.
- **Withdrawn by the captain:** my earlier framing in `implementation/captain-notes-t7.md` §2 and in
  `implementation/t7-task-contract.md` §5 (`RT-1` row) that R1 contains a K13 inconsistency which the
  implementer must surface. The instruction to *implement K13 per R3* stands unchanged and is
  independent of this error, because R3 and R1 agree on the state.

## 4. Consequential corrections

- `implementation/captain-notes-t7.md` §2 — reframed.
- `review/t8-review-task-contract.md` §4.3 — the reviewer is now told to verify whether `RT-1`'s
  premise is supported by R1, with this addendum as the captain's evidence, and **not** to fail an
  implementation for omitting a non-existent inconsistency.
- `RUN-LEDGER.md` — round-5 entry records this.

## 5. Limits of this correction

- This correction decides **no electrical value**. It only establishes what R1 does and does not say.
- It does not close `OI-T4-01` or F1-F6 (both remain user-frozen), and it does not touch `RT-2`,
  `RT-4`, `OI-T5-01/02`.
- If `test-strategy-architect` or `test-method-expert` can show a byte-level R1 passage that lists
  `13` as keep-open, this ruling is withdrawn with that evidence. None exists at the two cited
  locations.
