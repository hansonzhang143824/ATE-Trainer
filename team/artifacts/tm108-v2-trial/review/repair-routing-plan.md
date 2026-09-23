# Repair routing plan — `t8` findings for `tm108-v2-impl`

Pre-written so that a non-`pass` verdict can be routed **in the same round it arrives**, without
lowering the bar and without drafting under time pressure. Routing follows the reviewer charter's
finding table (`team/TEAM_ARCHITECTURE_V2.md`, `规则审查专家` §5) and the captain's rulings on record.

## 1. Rule that governs every repair

A repair **changes the artifact**, therefore it invalidates the review that produced the finding. Any
repair must:

1. be performed by the finding's `responsibleOwner` — never by the reviewer and never by the captain;
2. be recorded with new plaintext hashes (code + manifest, re-bound: `changes[0].afterSha256` must equal
   the new live hash, and the pre-change image never changes);
3. preserve every invariant the captain already proved — comments-vs-code scope, the TM108-only
   footprint, BOM/CRLF, `DUT_API` 107, signature text, the closure set `{13,65}`, `K21` unclosed, no
   invented tolerance, no CSV-layer alternative in code;
4. be followed by a **re-review on the new revision** (a fresh `rule-reviewer` task bound to the new
   hash). The old verdict does not carry over.

## 2. Likely findings and their owners

| If the reviewer finds… | Owner | Repair condition | Notes |
|---|---|---|---|
| A contract-conformance gap in the code (relay, register, range, phase order, reporting) | `ate-implementer` | bring the named code site into line with the cited R1/R3 section; no other change | the implementer must not re-decide any electrical fact; if the contract itself is the problem, see the rows below |
| `C11` — R3's `logPlan` raw context cannot be emitted with any reachable primitive | `test-method-expert` | state whether each of `CBC_log::log` / `CBC_log::test_log` (`BoardCheck.h:759-760`), `log_data` (`treg.h:195`), `treg_error_log` (`treg.h:176`) is reachable from a TM function; either re-issue the `logPlan` within the real capability or accept the trace-comment form explicitly | **contract-vs-capability**: do not let this be patched as a code defect if the primitive genuinely does not exist |
| `C11` — a usable primitive **does** exist and the implementer missed it | `ate-implementer` | emit the named `logPlan` quantities through that primitive, per site, with the contract's fields | code finding; cite the primitive's declaration line |
| `C12` — `K17_BUSL_VAC` must be actuated by TM108 | `ate-implementer` (form) with `test-strategy-architect` (if the contract must assign the form) | either add the actuation call the reviewer accepts, or obtain a written contract statement that inheritance is the sanctioned form | R1 md `:245-246` separates 「动作（必须闭）= 13, 65」 from 「须处于闭合态 = 17」; `OI-T4-04` is the open item that owns the form |
| A number, relay, register, ramp, range or limit that is not traceable to R1-R3 | `ate-implementer` if it is in the code; otherwise `test-strategy-architect` / `test-method-expert` if the contract is the source | per the routing table | the captain's gate already found no untraceable numeric, so this is unlikely |
| An open item treated as settled (`OI-T4-01`, `OI-T5-01/02`, `RT-2`, `RT-4`, F1-F6) | whichever artifact asserts it | restore the carried/unresolved wording; `OI-T4-01` especially: no agent may close or relabel it (`captain-precheck/oi-t4-01-status-addendum.md`) | a finding here is a **record** defect, not an electrical one |
| `RT-1` asserted as an open contract inconsistency | nobody — the premise is refuted | delete/re-word the assertion; the requested "authoritative statement" already exists in R1 | already handled in the delivered manifest; any recurrence is a regression |
| Scope: any change outside TM108 | `ate-implementer` | revert the out-of-scope hunk | the captain's scope proof would catch it |
| Manifest no longer hash-bound to the code | `ate-implementer` | rewrite `changes[0].afterSha256` (and hashes) to the live file | the deliverable is the bound pair |

## 3. What must NOT happen

- No repair may be performed by the reviewer, the captain, or a downstream role (`t9` compile) as a
  way to make a finding disappear.
- No finding may be closed by editing the reviewer's findings files.
- No electrical value may be introduced to satisfy a finding: if a value is missing, the item is
  returned to its contract owner and stays carried, exactly as `RT-2`/`RT-4` do.
- The `pass` bar stays as stated in `captain-precheck/commander-signoff-tm108.md` §4; it is not
  adjusted to fit the effort already spent.

## 4. Dispatch templates (fill on arrival)

**To `ate-implementer` (code finding):** task id `t10`, role `ate-implementer`, inputs = the reviewer's
findings file + the finding ids being repaired + the named contract sections, output = the same
`test.cpp` / manifest paths with new hashes, plus the invariant list from §1.3. Report
`DONE: t10; outputs: <paths>` or `BLOCKED: t10; evidence: <paths>; question: <one question>`.

**To `test-method-expert` / `test-strategy-architect` (contract finding):** task id `t10`, role as
routed, inputs = the findings file + the specific contract return item, output = a corrected contract
artifact **or** a written statement of the sanctioned alternative; **the signed contract's current
hash is the baseline and the change must be recorded as a new revision**, after which `t7`'s
deliverable must be re-checked against it.
