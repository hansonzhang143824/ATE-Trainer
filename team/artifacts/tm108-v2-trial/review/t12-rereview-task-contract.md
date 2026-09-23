# t12 task contract — TM108 re-review after the `needs-revision` repairs (`rule-reviewer`)

**Task id:** `t12`
**Role:** `rule-reviewer`
**Run:** `tm108-v2-impl`
**Depends on:** `t10` (`test-method-expert`, R3 §6 `logPlan` re-issue) **and** `t11`
(`ate-implementer`, `RF-02`/`RF-03`/`RF-04` comment fixes) both reaching `DONE`.
**Status:** prepared in advance; dispatch only when both repairs have landed.

A repair changed the artifacts, so the `t8` verdict **does not carry over**. This is a new, independent
review bound to the **new** hashes. The `pass` bar is unchanged
(`captain-precheck/commander-signoff-tm108.md` §4) and is not adjusted for effort already spent.

## 1. What must be re-established, not assumed

| # | Item | How |
|---|---|---|
| R1 | The new `test.cpp` hash and the new manifest hash, and that `changes[0].afterSha256` equals the live file | your own python plaintext reader |
| R2 | The pre-change image is **still** `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` (469714 B) — the audit anchor must not have been rewritten | hash the backup; if it changed, that is a blocker in itself |
| R3 | The new R3 (`tm108-test-method-contract.md` / `.json`) hashes, and what changed inside §6 `logPlan` versus the old revision (`8EB56D24…` md / `F947E6C6…` json) | diff the two revisions; the change must be confined to the `logPlan`/failure-path area plus an openItem disposition |
| R4 | The change to `test.cpp` is **still comments-only**: every added/removed line is a comment or blank, and the non-comment line sequence is byte-identical | classify every added and removed line yourself |
| R5 | Every hunk lies inside the TM108 region; `DUT_API int` count unchanged (107); signature present exactly once; BOM + CRLF preserved; no other TM moved | your own diff |
| R6 | All five upstream contracts still hashes-match their recorded values (`6F605772…` R1 md, `FBA489B5…` R1 json, `FA41E471…` bst-sw-phase-check, `626BB270…` oi-t4-01 addendum, and R3's new value) | re-hash |
| R7 | No new electrical value, relay, register, ramp, range, limit, tolerance or `TRIG_*`/`1.65`/`200`/`20` parameter appeared; closure set still `{13,65}`; `K21_VAC_Cap` still unclosed; no `cbite` release call added; no BST/SW action added (0 tokens) | body inventory |

## 2. The four findings — each must be verified closed, with evidence

| Finding | Sev | What "closed" means |
|---|---|---|
| `RF-01` R3 §6 `logPlan` demanded 10 records, only 3 emitted | blocker | Either **(a)** every raw-context row now names a concrete, **reachable** mechanism with its field mapping — in which case the implementation must actually use it and you must verify the call sites exist in real code — or **(b)** the rows are explicitly downgraded to comment documentation, with a failure-path rule that does not depend on a non-existent API. Confirm the chosen disposition is stated in the artifact and recorded as an openItem disposition. Also confirm the `RR-02` no-trigger/initialiser contradiction is addressed. **Verify the capability claim yourself before accepting it** — if a reachable logging mechanism exists, `(a)` is compulsory and the code is incomplete. |
| `RF-02` framework relay release asserted as fact | low | the text now states the behaviour as **assumed, not verified**, names the verification owner, and **no release call was added** |
| `RF-03` TM108 lost its `Step 4` heading | low | the numbering matches the sibling TMs' scheme, or the deviation is explicit in a comment. Verify against `TM107` and `TM109`, not against the finding's prose |
| `RF-04` four navigational numbers did not reproduce | low | every number now reproduces under your own python plaintext read (signature line, changed-range claim, TM-symbol count, non-comment line count, and the manifest's `sourceLocationBefore`/`sourceLocationAfter`) |

A finding whose repair you cannot verify with evidence is **not closed**. If any repair is absent or
partial, the verdict is `needs-revision` again with a fresh finding.

## 3. Independence rules (unchanged from `t8`)

- **Read-only.** Never write to `D:\PROJECT6-DALI` (nor to `devel`, which stays frozen). Copy what you
  review into `team\artifacts\tm108-v2-trial\review\copy2\` and inspect the copy. Snapshot plaintext
  hashes before and after and state that they are unchanged by your review.
- **DLP:** python byte mode only for `test.cpp` / `sub.cpp` / `StdAfx.h`
  (`C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`). pwsh
  `Get-Content`/`Set-Content`/`Select-String`/`Get-FileHash` and any .NET file API read ciphertext
  (`TSZ#…`), report false zeros, and can destroy the file. Label every hash `plaintext` and name the
  reader.
- Review against the contracts only; the implementation is not an authority.
- Resolve, close or relabel **no** open item (`OI-T4-01`, `OI-T4-04`, `OI-T5-01/02/03/05`, `RT-1`..`RT-5`,
  F1-F6, `OI-T4-10`..`16`); take no side in any conflict.
- No build, no gate script, no hardware claim; `RF-01`'s capability question is about **reachability in
  source**, not about running anything.
- Do not modify the implementation or the contracts; suggested fixes belong in your findings.

## 4. Required outputs

1. `team\artifacts\tm108-v2-trial\review\t12-review-findings.md`
2. `team\artifacts\tm108-v2-trial\review\t12-review-findings.json` — charter fields: `runId`,
   `reviewedInputs[]` (old **and** new hashes), `applicableRules[]`, `phaseTrace[]`, `findings[]`,
   `gateResults[]`, `waivedFindings[]`, `reviewStatus`, `residualRisks[]`, plus a
   `closureVerification[]` block giving, per finding `RF-01`..`RF-04`, the evidence that it is closed
   (or the reason it is not).
3. A one-line verdict: `pass` / `needs-revision` / `reject`.

`pass` is the **only** verdict that lets `t9` (compile) be considered, and only after the commander's
final sign-off re-runs the acceptance gate on the revision you name.

## 5. Reporting

- `DONE: t12; outputs: <paths>; verdict: <pass|needs-revision|reject>`
- `BLOCKED: t12; evidence: <paths>; question: <one precise question>`
