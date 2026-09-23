# RUN-LEDGER — `tm108-v2-impl` (TM108 code delivery)

Recovery anchor. Read this first after any session restart, compaction, or interruption; then read
`team/CURRENT_STATUS.md`. Rules in force: `AGENTS.md` (workspace) + `~/.dsh/AGENTS.md` (global).

- Run: `tm108-v2-impl` · TM: **TM108** (`VAC1_PRST`, symbol `TM108_HSKP_VAC1_PRST`)
- Upstream run whose signed artifacts are reused: `tm108-v2-trial`
- Trigger: direct user instruction "写TM108的code" (2026-09-17 21:20 +08:00). Per `team/ROLE_ROUTING.md:39`
  and `captain-precheck/protocol-runtime-memory.md:8-11`, a user trigger has the highest authority and
  overrides the automatic trigger path. The §7 TM108 suspension (`protocol-runtime-memory.md:94-104`)
  is superseded **for the implementation and review stages only** by that instruction; its open-item
  freezes (`OI-T4-01`, F1-F6) remain in force.
- Dispatch mode: direct DSH `subagent` only. No `agent_teams_*` tool is used in this workspace
  (`AGENTS.md` rules 1-2).

## 1. Upstream artifacts (reused, freshness verified)

| Task | Owner | Artifact | sha256 (captain-verified 2026-09-17 21:2x) |
|---|---|---|---|
| t2 | dft-expert | `dft/dft-fact-audit.md` | re-hash on use |
| t3 | schematic-expert | `schematic/schematic-fact-audit.md` (+ extraction scripts in `schematic/`) | re-hash on use |
| t4 | test-strategy-architect | `strategy/tm108-resource-config-contract.md` | `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4` |
| t4 | test-strategy-architect | `strategy/tm108-resource-config-contract.json` | `FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9` |
| t5 | test-method-expert | `method/tm108-test-method-contract.md` | `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7` |
| t5 | test-method-expert | `method/tm108-test-method-contract.json` | `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21` |
| t5 | test-method-expert | `method/bst-sw-phase-check.md` | `FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54` |
| t6 | dft-expert | `dft/dtest0-oi-t4-01-resolution.md` | status overridden by `captain-precheck/oi-t4-01-status-addendum.md` |
| — | captain | `captain-precheck/ground-truth.md`, `protocol-runtime-memory.md`, `oi-t4-01-status-addendum.md` | addendum `626BB270BF2B803AA1E5EE1318F9DFFC36D6C12254FFA5F745133A32EA12B9BF` |

**Chain check (FACT):** the t4 hashes reproduce exactly the values recorded inside t5's own Hash
Ledger (`tm108-test-method-contract.md` E1/E2), so the strategy→method chain is intact and t4/t5 are
current. No `deliverable_ready` was issued by t5 (suspension); the `t7` task contract is the recorded
substitute for that notification.

## 2. This run's tasks

| id | Role | Status | Artifact / contract | Notes |
|---|---|---|---|---|
| t7 | ate-implementer | **dispatched, running** (subagent `1f95a49e`), started 21:20 | contract `implementation/t7-task-contract.md` | bring the existing `TM108_HSKP_VAC1_PRST` (`test.cpp:2155-2225`) into conformance with t4/t5 |
| t8 | rule-reviewer | **prepared, not dispatched** | contract `review/t8-review-task-contract.md` | dispatch only after t7 reports `DONE`; read-only, copy-based, plaintext before/after hashes |
| t9 | compile-diagnostician | not in this run's objective | — | needs a t8 `pass` `deliverable_ready`; not started |

## 3. Pre-change baseline (captain-frozen, independent of t7's manifest)

`captain-precheck/t7-pre-change-baseline.json`, produced by `captain-precheck/record-t7-baseline.py`
with the python plaintext reader, **before any write**:

| File | sha256_plaintext | bytes |
|---|---|---|
| `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | 469714 |
| `D:\PROJECT6-DALI\ForCodexDebug\source\sub.cpp` | `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470` | 121909 |
| `D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h` | `ba8ab3de1b0c35cb7e9a477bd0b385f80671dc51011a08c9a5220518aab6aee6` | 56968 |

`test.cpp`: 9354 lines, 9350 CRLF, UTF-8 BOM, 107 `DUT_API int`. `TM108_HSKP_VAC1_PRST` block =
lines **2155-2225** (71 lines), comment `:2150`. `sub.cpp` has zero TM108 content.

Use this to check t7's claimed `beforeSha256` and diff scope instead of trusting the manifest.

## 4. Reader discipline (hard)

`test.cpp` / `sub.cpp` / `StdAfx.h` under the target are DLP-transparent-encrypted. Python byte mode
only (`C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`), UTF-8 BOM + CRLF
preserved. pwsh `Get-Content` / `Select-String` / `Get-FileHash` and any .NET file API read
**ciphertext** (header `TSZ#…`), report false zeros, and produce false "modified" digests. Every
hash recorded anywhere in this run must be labelled `plaintext` and name its reader.

## 5. Carried open items (must remain unresolved)

`OI-T4-01` (user-frozen, not closable by any agent — `captain-precheck/oi-t4-01-status-addendum.md`),
`OI-T5-01`, `OI-T5-02`/`RT-2`, `RT-1`, `RT-4`, F1-F6, `OI-T4-10/11/12/13/14/16`, `OI-T6-02`,
`OI-T6-03`. Pending user rulings: **B-1** (TestIO/DTESTMAP carrier), **B-2** (1.65 V source),
**B-3** (mux 22 vs 23), plus the F1-F6 set. `B-4` (write authorization to the pinned target) is
**cleared**: the session file policy is `danger-full-access` and a plain write to
`D:\PROJECT6-DALI\ForCodexDebug` succeeded on 2026-09-17.

Captain ownership pre-rulings (no new electrical values): `implementation/captain-notes-t7.md`
(§1 `RT-4` is spec-side, not code-side; §2 `RT-1` — the method contract governs the code, the
contract's internal conflict stays open).

## 6. Round log

| # | When | Action | Evidence |
|---|---|---|---|
| 1 | 2026-09-17 21:2x | reused t4/t5 after hash check; dispatched t7; wrote `t7-task-contract.md`; cleared B-4 by measurement; corrected the DLP/ciphertext misreading | `CURRENT_STATUS.md` dispatch log; probe results |
| 2 | 21:2x | froze `t7-pre-change-baseline.json`; confirmed t7 had not yet written (`test.cpp` hash unchanged) | baseline json + hash re-read |
| 3 | 21:2x | verified role-charter line spans used by the task contracts (实现专家 294-396, 规则审查专家 397-513); wrote this ledger | `grep '^# ' team/TEAM_ARCHITECTURE_V2.md` |
| 4 | 21:21-21:22 | extracted the TM108 **pre-change image** and divergence sites; **corrected a false negative in my own extraction** (see below); confirmed `RT-4` is not a code artifact | `captain-precheck/tm108-block-before.txt`, `.../tm108-divergence-sites-before.json` |

### Round-4 self-correction (recorded, not hidden)

The first run of `captain-precheck/extract-tm108-before.py` used `\bK13\b` and `\bK\d+\b`. Those
patterns are **wrong for this codebase** — the relay object is spelled `K13_VBAT_Cap` and `_` is a
word character, so `\bK13\b` never matches. That produced the false result `K13_lines=[]` and
"relay lines [2168, 2170]". The corrected patterns give K13 lines `[2168, 2171]` and relay lines
`[2168, 2169, 2170, 2171]`. Withdrawn: the earlier two-element relay-line list. Corrected claim:
the function's only actuated closure is `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` at `:2171`,
i.e. the signed closure set {13, 65}.

### Round-4 independent findings about the pre-change function (facts)

- `:2152` comment asserts `V(DTEST0)=nQON` — divergence 1 is present as the method contract states.
- `:2171` `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` — closure set matches the contract {13, 65}.
- Step 6 (`:2218-2223`) is `SetTestResult` reporting only → `RT-4` is spec-side (see
  `implementation/captain-notes-t7.md` §1 upgrade).
- Power-down (`:2213-2215`) uses `ACM200_10MA` / `FXVIe_PLUS_10MA` while R3 P4 states `ACM200_100MA`
  / `FXVIe_PLUS_100MA` and P7 says "range/limit held as in P4" — recorded as **check item C4** in the
  t8 contract, not adjudicated here.

| 5 | 21:22-21:2x | **refuted R3's `RT-1` against R1 directly** and recorded the correction; rewrote `captain-notes-t7.md` §2; corrected `t8-review-task-contract.md` §4.3 | `captain-precheck/rt-1-record-correction.md` |
| 6 | 21:23-21:2x | read the rest of the pre-change function; verified register staircase / power-on / measurement / hysteresis / P7 power-down against R1-R3 (all conformant); **withdrew round-4 check item C4**; found C7 (103 `cbite.SetOn`, 0 release, project-wide) | `review/t8-review-task-contract.md` §4c; round-6 findings below |
| 7 | 21:24-21:25 | wrote and smoke-tested the post-change verification gate; fixed 3 bugs in it found by the smoke test | `captain-precheck/verify-t7-change.py` |
| 8 | 21:25 | previewed the implementer's in-progress candidate (`_t7_candidate.cpp`) against the live target; found one false claim inherited from the original task contract; amended the `t7` contract and sent the owner a precise correction | `captain-precheck/rt-1-record-correction.md`; round-8 findings below |
| 9 | 21:26-21:27 | **the change was applied** (sha256_pl `8498c304…`, 477016 B, 9437 lines, target == candidate); ran the captain gate and produced an **independent scope proof**; read the manifest | `captain-precheck/t7-post-change-verification.json`; round-9 findings below |
| 10 | 21:28 | owner applied the `RT-1` correction (`_t7_fix_rt1.py`); re-ran the gate on the new revision — still conformant, scope proof still holds — and found the **manifest is now hash-stale** | `captain-precheck/t7-post-change-verification.json`; round-10 findings below |
| 11 | 21:28 | **hash binding closed** (`manifest changes[0].afterSha256` now equals the live file); verified `DEV-1` in the manifest is **still uncorrected** while the code banner is corrected | round-11 findings below |
| 12 | 21:29 | **`DEV-1` corrected** by the owner (subject now "WITHDRAWN … after independent re-check", with the refutation reproduced from its own byte-mode reads); final gate re-run clean; read `DEV-2/3/4` and turned the two substantive ones into `t8` check items `C11`/`C12` | round-12 findings below |
| 13 | 21:29-21:30 | `t7` reported **`DONE`**; the captain independently reproduced its two headline claims (comments-only; 3 in-scope hunks) and **dispatched `t8`** to `rule-reviewer` | round-13 findings below |

### Round-13 findings — `t7` DONE, claims independently reproduced, `t8` dispatched

`DONE: t7` received with outputs: `test.cpp`, `implementation-manifest.json`, `t7-selfcheck.md` and the
two backups. Captain-side reproduction of its own claims, from a python plaintext read of the backup
and the live file:

| Implementer claim | Captain's independent check | Result |
|---|---|---|
| "comments-only; zero executable statements touched" | classified all 97 added and 13 removed lines: **every one is a comment or blank**; non-comment lines 5691 → 5691 with the sequence **byte-identical** | **CONFIRMED** |
| "every diff opcode inside the TM108 region" | full-file diff has exactly 3 hunks, all inside the TM108 span (`2123-2311`) | **CONFIRMED** |
| "manifest bound to the live file" | `changes[0].afterSha256` == live `b79b911a…`; `intermediateStateSha256` + `DEV-5` also recorded | **CONFIRMED** |
| "RT-1 withdrawn" | `DEV-1` subject now "RT-1 claim about K13 - WITHDRAWN by this role after independent re-check", `ownerOfResolution: none required`; deviations are `DEV-1..DEV-5` | **CONFIRMED** |
| backup is the true pre-image | backup hashes to the captain's own recorded `15c7d2b8…` | **CONFIRMED** |

Note: the implementer counted 5625 non-comment lines and the captain's stricter heuristic counts 5691;
the two differ only in how trailing/inline comments are treated. The load-bearing result — the
non-comment sequence is **identical** before and after — holds under both, so the comments-only claim
is sound.

**Dispatched:** `t8` to `rule-reviewer` (background subagent), contract
`review/t8-review-task-contract.md`, requiring a terminal verdict (`pass` / `needs-revision` /
`reject`), read-only operation on a copy, python-byte-mode reads only, and an explicit position on
every check item `C1`-`C12`.

### Round-14 status — sign-off criteria frozen, reviewer verified to be on the right revision

- `t7` has **settled** (subagent state `ready`; it will not act again unless messaged). Its closing
  message confirms the `RT-1` correction is in all three places (code banner, manifest `DEV-1`,
  manifest `openItems` row now `REFUTED - NOT carried as an engineering item`), that `test.cpp` was
  byte-identical before and after the captain's correction message, and that no electrical value,
  relay, register, ramp, range, limit or tolerance was touched.
- Captain wrote `captain-precheck/commander-signoff-tm108.md`: acceptance criteria and their evidence
  (E1-E11 PASS, E12 = the `t8` verdict, PENDING), the closure conditions, and an explicit list of what
  the sign-off does **not** cover (no build/compile — that is `t9`, outside this objective; no gate
  script; no hardware; all contested electrical facts stay user-owned).
- Manifest schema conformance verified by the captain against
  `team/schemas/implementation-manifest.schema.json`: all `required` keys present, `targetRoot` const
  matches, `scope` non-empty, 2 backups + 1 change + 10 self-checks well-formed, `statusLabel` and
  `verificationNotPerformed` honest.
- `t8` is progressing against the contract: it created `review/tools/rv_hash.py`, `rv_copy.py`,
  `review/copy/test.cpp` (477123 B) and before/after span extracts. **The captain verified the copy
  hashes to the reviewed revision** (`b79b911a…`), so the review is judging the delivered artifact and
  not a stale copy, and the live target is unchanged at the same hash (the reviewer has not written to
  it, as required).

### Round-15 note — the reviewer's independent diff agrees with the captain's on every material quantity

The reviewer produced its own diff (`review/tools/out/diff_summary.json`, `full_diff.txt`) from its own
copy. Cross-checked against the captain's independent computation:

| Quantity | Captain | Reviewer | Agree |
|---|---|---|---|
| added / removed lines | 97 / 13 | 97 / 13 | yes |
| comments-only change | yes (classified every line) | `commentOnly: true` | yes |
| non-comment content | sequence byte-identical | `nonCommentIdentical: true`, `strippedIdentical: true` | yes |
| location | 3 unified hunks, all inside span `2123-2311` | 13 changed opcodes, all within before `2149-2217` / after `2149-2301` | yes (same change, finer granularity: `get_opcodes()` vs `unified_diff(n=3)`) |

The three comment-stripping heuristics in play (implementer 5625, reviewer 5628, captain 5691) differ
only in how they treat inline/trailing comments, and all three agree on the load-bearing property —
the non-comment content is unchanged. Two independent parties now agree on the shape of the change;
the outstanding question is only the reviewer's fidelity verdict.

### Round-16 finding — `C11`'s evidence scope was too narrow, and the captain widened it

Probing the project source (python byte mode) for logging primitives showed that `DEV-3`'s claim
("no text-logging primitive other than `CParam::SetTestResult`") is **scoped to `test.cpp`**, which is
not the same as "absent from the project". Found outside `test.cpp`:

| Candidate | Location | What it is |
|---|---|---|
| `CBC_log::log` / `CBC_log::test_log` | `BoardCheck.h:214`, `:759`, `:760` | per-item logger taking a `component` **string** plus `lolim`/`hilim`/`unit` |
| `log_data` | `treg.h:195` | static, per-site value logger |
| `treg_error_log` | `treg.h:176` | static, printf-style logger |
| `log_data_t` / `test_t` | `treg.h:108`, `:110` | framework logging-callback typedefs |

Also confirmed: in `test.cpp` the token `LogData` is a **step label**, not an API; `SetComment` /
`AddComment` / `WriteLog` / `LogWrite` / `PushLog` / `Log(` occur **0** times; `SetTestResult` (200)
and `GetMeasResult` (422) are the only result primitives in use.

Actions: the `t8` contract's `C11` was rewritten to require the wider scope with these four candidates
named and a per-candidate reachability ruling; and the reviewer was sent the same evidence directly,
with the instruction to amend `C11` in its findings if it had already finalised, and to change its
verdict if that is what the evidence requires. The consequences are explicit: if none of the
primitives is reachable from a TM, `DEV-3` is a contract-vs-capability finding for
`test-method-expert`; if one is reachable, it becomes a code finding against `ate-implementer`.

### Round-17 finding — `C12` (`K17`) evidence, which pulls both ways

Measured by the captain (python byte mode) on the pre-image backup and the live file:

| Fact | Value |
|---|---|
| `K17` occurrences in the **pre-change** file | **0** — the token appears in no function at all |
| `K17` occurrences after the change | 3, all inside the implementer's added comments (`:2162`, `:2208`, `:2214`) |
| TM108 closure call | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` (pre-change and unchanged) |
| TM109 (VAC2) closure call | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K19_ACM0_VAC2, -1)` |
| TM110 (VAC3) closure call | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K18_ACM0_VAC3, -1)` |

The evidence supports and opposes the implementer's "no call" decision at the same time: nothing in
the file actuates K17 (so the state is inherited), **but** both sibling VAC items add their own
VAC-branch entry relay (`K18`/`K19`) to their closure call, so TM108 omitting the analogous call is
not obviously the family convention. R1 md `:245-246` separates `动作（必须闭） = 13, 65` from
`须处于闭合态 = 17`, and R3 `:199` delegates the call form to `ate-implementer` under `OI-T4-04` —
so the form was a decision someone had to make and defend. Sent to the reviewer with both readings and
an instruction to pick one explicitly; `t8` §4b `C12` carries the same table. Also reinforced for
`C9`: the siblings are a **copy risk**, not corroboration, in either direction.

### Round-19 verification — two more sign-off criteria closed by the captain

- **No BST/SW driving action** (R3 states the differential constraint is unproven in all 9 phases, so
  any BST/SW action would be a serious finding). Token scan of the TM108 body (`2193-2309`):
  `K57` `K48` `K61` `K76` `K109` `K110` `K141` `K142` `K86` `K130` `BST` `SW_` `PMID` — **0 each**.
  File-wide, `K57` (11), `K48` (16), `K76` (16) all occur **outside** TM108; `K110` occurs 0 times in
  the whole file. Added to the sign-off record as **E13**.
- **`C5` capture-level provenance**: `test.cpp:2213` grounds the 1.65 V level as a *mid-scale logic
  threshold of the 5 V pull-up* (the method contract's own rationale) rather than a DFT fact, and
  `:2245` / `:2257` mark the premise **PENDING OI-T4-01**. Added as **E14**.
- `t8` was mid-composition (no new artifacts since its `logging.txt`), `t7` remains settled (`ready`),
  and the target is still `b79b911a…`.

### Round-20 verification — upstream chain confirmed intact (sign-off criterion E15)

Re-hashed all six signed upstream artifacts against the values frozen before dispatch. **All six
reproduce exactly**, so no contract drifted while the implementation or the review was running and
`t8` is judging against the same revisions the captain verified:

`6F605772…` (R1 md) · `FBA489B5…` (R1 json) · `8EB56D24…` (R3 md) · `F947E6C6…` (R3 json) ·
`FA41E471…` (`bst-sw-phase-check.md`) · `626BB270…` (`oi-t4-01-status-addendum.md`).

The manifest's `signedContracts[]` declares the same six with `verifiedByImplementer: true` and
`reader: python byte mode`. The captain's own ruling record `rt-1-record-correction.md` hashes
`B9C1377B980EE53A197B6C8D574453A2` — recorded now so any later edit to it is detectable.

Sign-off evidence stands at **E1-E11 + E13 + E14 + E15 = PASS**, with only **E12** (the `t8` verdict)
pending. `t8` is running (`rv_xcheck.py` at 21:32:32); the target is unchanged at `b79b911a…`.

### Round-22 verification — generator discoverability closed (sign-off criterion E16)

`t7` explicitly declared one thing unverified: "the meta-generator regex compatibility of the signature
was checked only as a text match, not by running the generator". Closed by the captain:

- The generator's **actual** regex was read from the source, not from a quote:
  `scripts/gen_testitems_meta.py:91` —
  `re.match(r'DUT_API int ((?:TM\d+(?:_\d+)?_\w+|Trim_\w+))\(short funcindex', line)`, with `:94`
  deriving the item id via `re.match(r'TM(\d+(?:_\d+)?)_', name)`.
- Applying it to the pre-image backup and to the live file gives **101** generator-visible names in
  each, **including `TM108_HSKP_VAC1_PRST`**, with **no duplicates**, and identical before/after — so
  the change does not affect the meta-coverage path at all.
- Noted for completeness: the generator sees 101 of the file's 107 `DUT_API int` declarations; the
  remaining 6 do not match its name pattern. That is pre-existing and unrelated to this change.
- The generator itself was deliberately **not run** — that rewrites `project/DALI/meta/*`, a data
  change outside this objective and not authorised here.

`test/CURRENT_STATUS.md` was refreshed this round with the active-work-stream block (stage table,
recovery pointers, delivered hashes, and the list of still user-owned open items), so a restart lands
on the correct state instead of the round-5 snapshot.

### Round-23 verification — `t7-selfcheck.md` claim audit (sign-off criterion E17)

The self-check document was the one required output the captain had only confirmed to *exist*. Audited
its verifiable claims against the delivered revision (`captain-precheck/check-selfcheck-claims.py`).
Most reproduce exactly (post-change hash/size/BOM/CRLF, backup hashes, `sub.cpp` hash and 0 TM108
occurrences, comments-only change, 0 BST/SW tokens, relay-macro existence incl. the `K64_HG1` vs
`K64_ACM9_HG1` catch). **Two low-severity inaccuracies and one count mismatch:**

| Claim in the self-check | Measured | Effect |
|---|---|---|
| check 7: signature at `test.cpp:2191` | **2193** (present exactly once) | none — existence and uniqueness both hold |
| check 6: every opcode inside "display lines 2149-2216" | before side `2150-2217`, **after side `2150-2301`** | none — the conclusion ("confined to TM108") is correct; the stated range is wrong/stale |
| check 8: "95 TM symbols" | its own regex gives **98**; 107 `DUT_API int ` declarations exist | none — cosmetic |

Recorded as **E17** in the sign-off rather than silently accepted, and routed to `ate-implementer` as
documentation-only (no code change) if the verdict is otherwise `pass`. The reviewer's own numbers are
unaffected: it independently measured 97 added / 13 removed and 13 changed opcodes, matching the
captain.

`t8` remains running; the target is unchanged at `b79b911a…`.

### Round-24 — `t8` verdict received: `needs-revision` (1 blocker + 3 low); repairs dispatched

`case verdict` recorded in `captain-precheck/commander-signoff-tm108.md` (E12 row + "Verdict outcome"
section). Load-bearing claims reproduced by the captain: live `test.cpp` `b79b911a…`; manifest
`a4f5286d…`; TM108 body `2193-2309` holding exactly **3** `SetTestResult`; R3 §6 `logPlan` carrying
**10** logical ids. The blocker is a genuine contract-vs-capability gap and no executable line needs to
change.

Dispatched: `t10` → `test-method-expert` (re-issue R3 §6 `logPlan`, disposition **(a)** name a reachable
mechanism with field mapping, or **(b)** downgrade to comment documentation plus a failure-path rule
that does not depend on a non-existent API; also fold in `RR-02`); `t11` → `ate-implementer`
(`RF-02`/`RF-03`/`RF-04`, comment/documentation only, re-bind the manifest hash). Both are background
subagents; they write disjoint artifacts (`R3` vs `test.cpp`).

Consequence to remember: a change to **either** artifact invalidates the `t8` review, so a **re-review
on the new revision** is mandatory before `t9`/compile can be considered — the `pass` bar set in
`commander-signoff-tm108.md` §4 is not adjusted.

### Post-mortem — where the elapsed time actually went (recorded so it is not repeated)

1. **Pacing, the largest factor, and entirely self-inflicted.** 23 automatic goal rounds fired at
   15-30 s intervals while the implementer and reviewer needed multi-minute turns. Each round was
   treated as needing a fresh deliverable, producing ~10 marginal artifacts (extra notes, an unused
   `t7-block-diff` scaffolding, repeated round summaries). The correct behaviour was to dispatch and
   wait for the completion notice. No technical work was blocked by this; it consumed attention and
   context.
2. **A false premise I propagated without checking (real rework).** `RT-1` in the signed method
   contract claimed R1 contradicted itself on `K13`. I repeated it into the `t7` task contract
   ("report the contract inconsistency") instead of verifying it; the implementer dutifully wrote it
   into the code banner and the manifest. I then refuted it against R1 directly, wrote
   `rt-1-record-correction.md`, amended two contracts, sent a correction, and the implementer redid the
   manifest. Cost: roughly three extra turns plus a second revision of `test.cpp`.
3. **A too-narrow check item I wrote (`C11`).** Its wording scoped the logging-primitive verification
   to `test.cpp`, which is exactly the scope-discipline error this team had already banned. I had to
   widen it mid-review and message the reviewer.
4. **Self-inflicted document defects in my own artifacts:** the accidental deletion of the `C8` heading
   in the `t8` contract (needed a repair + a re-based body), and three bugs in my own verification gate
   that only the smoke test caught — a missing `newline=''` (a false 166-line diff on an unchanged
   file), a C1 window that silently examined zero lines and returned a vacuous `OK`, and a wrong
   before-image filename.
5. **One protocol slip:** I mistakenly called the forbidden `agent_teams_status` tool. It errored and
   changed nothing, and it is recorded in round 8.
6. **The substantive defect is not mine and not the implementer's:** R3's `logPlan` (written in the
   earlier `tm108-v2-trial`) specified 10 log records for a codebase whose only reachable in-TM log
   write is `SetTestResult`. This is precisely what the blocker `RF-01` is, and it was latent upstream
   from the start.
7. **Legitimate cost:** ~14 minutes of wall clock for an implement-then-independently-review cycle
   across 10 evidence scripts, with 17 sign-off criteria independently reproduced. That part did not
   need to be shorter.

### Round-25 note — `t8` is producing FURTHER evidence after its `needs-revision` verdict

The reviewer reported `needs-revision` at ~21:34, but its subagent is still running and, from ~21:34:50
onward, has been executing exactly the two scope-widening corrections the captain queued: it produced
`rv_val.py`, `rv_extern.py`/`extern_c11.txt`, `rv_extern2.py`/`extern_c11b.txt`, `rv_extern3.py`/
`extern_c11c.txt` (76 KB), `rv_errlog.py`/`errlog.txt`, `rv_cparam.py`/`cparam.txt` (21:37:18) and
`rv_reach.py` (21:37:39). Its current line of enquiry is the right one for the blocker: it is searching
the whole `ForCodexDebug` tree for a `CParam` **declaration** and reading the `SetTestResult` call
contexts — i.e. asking whether `CParam` exposes any record/log member beyond `SetTestResult`, which is
precisely what decides whether `RF-01` is contract-side (as routed to `t10`) or code-side.

Record discipline: **`t8` may therefore emit an amended `C11` finding and, if so, an amended verdict.**
Until it settles, the `needs-revision` verdict recorded in `commander-signoff-tm108.md` (E12) binds the
routing, and any amendment is to be folded in as a *superseding* revision of `t8-review-findings.*`
with both revisions' hashes recorded — not silently overwritten. `t10` was dispatched with an explicit
instruction to verify the capability claim independently and to report instead of re-issuing the
contract if it finds a reachable mechanism, so the two tasks do not depend on each other's answer.

Round 25 produced no new artifact beyond this note, by design (see post-mortem cause 1).

### Round-26 — the widened `C11` check resolves the logging question, and it rejects the captain's own candidates

`t8`'s post-verdict enquiry (`tools/rv_reach.py` → `reach.txt`, `rv_final.py` → `final_reach.txt`,
`rv_blk.py`) answered the question that decides `RF-01`'s disposition, using the right method — an
**include-closure** analysis rather than a name search:

| Candidate the captain raised | Verdict from the reviewer's analysis |
|---|---|
| `BoardCheck.h:214 CBC_log` with `:759 log(...)` / `:760 test_log(...)` | **NOT REACHABLE** — the transitive local-header closure of `test.cpp` has 16 entries and **`BoardCheck.h` is not one of them**; `CBC_log` / `bc_log` / `test_log` have **no user outside `BoardCheck.*`**; `BoardCheck` appears in `test.cpp` only as the `DO_BoardCheck` operator-mode flag, not as a type use |
| `treg.h:195 log_data(...)` | **NOT REACHABLE** — `treg.h` *is* in the closure, but the declaration sits in a `TREG_LOG` segment under `private:` |
| `treg.h:176 treg_error_log(...)` | under investigation in `t8`'s final pass; no evidence yet that it writes station-log records for raw context |
| `LogData` (91 hits in `test.cpp`) | confirmed again to be `// ====== Step 6: LogData ======` comment headers, never calls |
| `LogDataStruct.h` (in the closure, 601 lines) | listed and read; no log-writing API found |

Also observed, and worth keeping: there are **two non-identical copies** of `treg.h` / `treg.cpp`
(`source/` vs `source/src/`, 51157 vs 47730 B) — a latent trap for any name-based search, which is
another reason the include-closure method was the right one.

**Self-correction recorded:** the captain's round-16 probe found those candidate primitives by *name*
and used them to widen `C11` and to push a queued message at the reviewer. The reviewer tested them
properly and showed that none is reachable from a TM function. So the widening was worth doing — it
was tested rather than assumed — but its outcome is that **my candidates do not overturn the
implementer's claim**; the correct classification of `RF-01` remains contract-vs-capability, and `t10`'s
routing stands. This is the second time a captain hypothesis was falsified by evidence rather than
defended; both are on the record.

### Round-12 findings — the deliverable is code-complete and internally consistent

- `DEV-1` is now corrected in the manifest (21:28:56): subject *"RT-1 claim about K13 — WITHDRAWN by
  this role after independent re-check"*, `ownerOfResolution: none required`, and the `handling` text
  reproduces the refutation **from the owner's own python byte-mode reads** of I1/I2 (the same
  16-number keep-open list, `relayGroups[G3].closureSetActuatedThisStage = [13,65]`, R1 md `:245`,
  and `:574` out of range). The remaining occurrences of `keepOpenRelayNumbers` / `:574` in the
  manifest are inside that corrective text, i.e. quoted in order to refute them.
- Hash binding still holds: `changes[0].afterSha256 = b79b911a…` == live file.
- Final gate on this revision: every invariant passes; **C1** and **C6** pass; scope proof passes
  (3 hunks, all inside the TM108 span `2123-2311`).
- Two substantive self-declared deviations were read in full and converted into review checks rather
  than being accepted or rejected here: `DEV-3` (R3 `logPlan` raw context carried as comments, on the
  claim that no in-TM text-logging primitive exists) → `C11`; `DEV-2` (`K17_BUSL_VAC` required closed
  with no actuation call, on the measured evidence that relay 17 is actuated by no TM in the tree) →
  `C12`. `DEV-4` is administrative (helper scripts/backup location) and needs no review action.
- Owner was still running at the close of this round; no `DONE` has been received yet.

### Round-11 findings — hash binding resolved, `DEV-1` still open on the manifest side

- **Closed (round-10 watch item):** `implementation-manifest.json` (21:28:38, 23376 B) now carries
  `changes[0].afterSha256 = b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a`, which
  **equals the live file hash** — the deliverable is hash-bound again. `t7-selfcheck.md` was rewritten
  in the same pass (18594 B, 21:28:33).
- **Still open:** `deviations[DEV-1]` in that same manifest still asserts the refuted claim verbatim
  ("…resourceSummary.keepOpenRelayNumbers also lists 13 (contract md :248, :574)") with
  `ownerOfResolution: test-strategy-architect`; the string `REFUTED` appears nowhere in the manifest
  while the code banner at `test.cpp:2186` **does** say `REFUTED`. So code and manifest currently
  disagree about the same finding. The owner was still running; `t8` §4b `C10` now carries the
  verbatim quote and splits it into three separately-judged problems (false claim, false subject
  framing, unnecessary routing).

### Round-10 findings — the `RT-1` correction landed in the code; the manifest is now stale

`t7` processed the captain's round-8 correction (its own scripts `_t7_fix_rt1.py` at 21:28:00 and
`_t7_verify2.py` at 21:28:08). Live state now:

- `test.cpp` **sha256_pl `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a`**,
  477123 B, 9438 lines; TM108 symbol span `2193-2309` (shifted by the one added line).
- The refuted banner line now reads `//   RT-1       REFUTED by independent re-check of the signed
  strategy contract: keepOpenRelayNumbers …`.
- Gate re-run on this revision: BOM preserved; CRLF delta +84 (= the 84 added lines); signature
  unchanged; `DUT_API` 107 → 107; closure set {13,65} present; K21 not closed; no `cbite` release
  added; CSV-layer alternative still absent; measurement pair and register writes present; **C1 PASS**
  (only the "NOT equated with the nQON candidate" statement, explicit pending marker); **C6 PASS**
  (no numeric tolerance).
- **Independent scope proof re-confirmed** on the new revision: the backup still hashes to the
  captain's pre-image (`backup_matches_recorded_preimage: true`) and the full-file diff is exactly
  **3 hunks**, all inside the TM108 span (`2147/2165/2199` → `2147-2194 / 2203-2262 / 2265-2304`,
  span `2123-2311`).

**Watch item (verified, currently failing):** `implementation-manifest.json` is **hash-stale** — its
`changes[0].afterSha256` is `8498c304…` (the 21:27:14 revision) while the live file is `b79b911a…`.
The manifest predates the `RT-1` fix. The deliverable is the hash-bound pair, so this must be closed
before review. `t8` §4.7 was strengthened: the reviewer must verify the binding against the live file
and treat a stale manifest as a **blocking** finding. Owner was still running when this round closed.

### Round-9 findings — the change is applied, independently verified, scope-proven

`t7` applied `test.cpp` at ~21:26:20. Live state: **sha256_pl `8498c304ba4752ffcc44c646bdff9649006bb0a858b25db099368bdfa4ae9871`**,
477016 B, 9437 lines, byte-identical to `_t7_candidate.cpp`.

Captain gate (`verify-t7-change.py`), all values from a hash-anchored python plaintext read:

| Check | Result |
|---|---|
| BOM preserved / CRLF delta / signature / `DUT_API` count | BOM true; CRLF +83 (== the 83 added lines); signature unchanged; 107 → 107 |
| closure set {13,65} present, K21 not closed, no `cbite` release added | all pass; the only `cbite.SetOn` in the body is `:2217` `K13_VBAT_Cap, K65_nQON_PU` (the other match is a comment) |
| CSV-layer alternative not written | pass (`0x55`/`0x97` absent from the code) |
| measurement pair + register writes survive | pass (2 × `rampv_capv`, `TRIG_FALLING`/`TRIG_RISING`, `0x56,0x16`, `0x57,0x08`, `entertestmode()`) |
| **C1** (`DTEST0 == nQON` assertion) | **PASS** — window 2150-2308 contains only "the DFT check pin V(DTEST0) is NOT equated with the nQON candidate"; explicit pending marker present |
| **C6** (no invented tolerance) | **PASS** — no numeric tolerance; the only occurrence of the word is the carrying statement `no tolerance is published … none is invented` |
| **Independent scope proof** | **PASS** — `backup_matches_recorded_preimage: true` (the backup hashes to the captain's own pre-image `15c7d2b8…`), and the full-file diff is exactly **3 hunks**, all inside the TM108 span: before `2147/2165/2199` → after `2147-2193 / 2202-2261 / 2264-2303`, span `2122-2310` |

Manifest read (`implementation/implementation-manifest.json`, 23097 B): `runId=tm108-v2-impl`,
`targetRoot=D:/PROJECT6-DALI/ForCodexDebug`, both backups recorded with plaintext hashes that match
the captain's baseline, `changes[0]` carries `beforeSha256 15c7d2b8…` / `afterSha256 8498c304…`
(both independently reproduced by the captain), `sub.cpp` recorded as unmodified with its 0-hit
evidence, no Trim framework, 10 self-checks, and `openItems[]` carrying `OI-T4-01`, `OI-T5-01`,
`OI-T5-02`, F1-F6 and the rest without closing or siding on any of them. `t7-selfcheck.md` exists.

**Still open at the end of this round:** the manifest's `deviations[DEV-1]` and the code banner at
`test.cpp:2186-2187` still assert the refuted `RT-1` claim ("…also lists 13 (contract md :248, :574)").
This is the defect the round-8 correction message addresses; the owner was still running when this
round closed. `DEV-1` must not survive review as a "reported contract inconsistency", and `t8` §4b
now carries an explicit check for it.

### Round-9 self-correction (gate defect)

The gate's C1 window was `start-8` lines, chosen for the *pre-change* function. The conformant
revision adds a ~44-line banner above the symbol, so the window contained **no** candidate line at
all and the C1 check returned `c1_candidate_lines: []` with a vacuous `OK`. Fixed: the window now
runs from the TM108 banner line to the function end (`c1_window_lines: [2150, 2308]`), and the old
`tolerance_literal_present` word check was replaced by `numeric_tolerance_introduced` plus a
`tolerance_word_lines` list, because the word legitimately appears in the carrying statement.

### Round-8 findings — candidate preview, one defect, and a contract amendment

`t7` is building the change in the workspace before touching the target (`_t7_apply.py` → `_t7_candidate.cpp`
477764 B → `_t7_show_candidate.py` → `_t7_edit_test.py`), and the target is still byte-unchanged at
sha256_pl `15c7d2b8…`. Diffing candidate vs live target (13 changed opcodes, all inside the TM108
span) showed:

- **C1 is satisfied.** The forbidden `measure V(DTEST0)=nQON toggle` line is replaced by
  "capture the digital toggle on the observation candidate", and a `NOT ASSERTED HERE` block states
  that `DTEST0` is **not** equated with `nQON` and that `RA-5` is `CANDIDATE ONLY`.
- **C7 is handled correctly.** The candidate states the closure set is released implicitly with the
  `cbite` scope, and adds no `cbite` release call — consistent with the project-wide 103:0 pattern.
- **Verified-correct citations** (spot-checked against the contracts, so the reviewer can trust the
  ids): `RT-3` (`tm108-test-method-contract.md:639`), `OI-T5-05` (`:623`), `OI-T4-04`
  (`tm108-resource-config-contract.md:377`), `RT-4` (`:640`), `RT-5` (`:641`), and the sweep geometry
  "200 samples x 20 us" (method contract `:455`, `:465` — "interval 20 us per sample => 4 ms").
- **One defect found: the candidate repeated the refuted `RT-1` claim** — "the signed strategy
  contract lists relay 13 both in the G3 closure set (sec.6) and in resourceSummary
  .keepOpenRelayNumbers (sec.6.1)". The section reference is valid (§6.1 exists at R1 md `:241`) but
  the list it points to does not contain 13. Root cause is **the captain's own task contract**: the
  original `t7-task-contract.md` §5 told the implementer to "report the contract inconsistency", and
  round 5 corrected only `captain-notes-t7.md` and the `t8` contract, not the `t7` contract the
  implementer was working from.
  - Fix applied in round 8: `implementation/t7-task-contract.md` §4.3 and §5 `RT-1` row amended with
    the refutation and a pointer to `captain-precheck/rt-1-record-correction.md`; the owner was sent a
    precise correction via `send_message` covering the code comment and the manifest, with an explicit
    "change nothing else" instruction.

### Round-8 protocol slip (self-reported)

I mistakenly called the `agent_teams_status` tool, which this workspace forbids for ATE delivery
(`AGENTS.md` rule 1). It returned `invalid AgentTeams state in team "ate-coding-core-v2"` and changed
nothing. No `agent_teams_*` tool will be used again for this work; the dispatch path stays direct
DSH `subagent`.

### Round-5 finding — `RT-1` is a false positive (withdraws an earlier captain claim)

R3's `RT-1` (`tm108-test-method-contract.md:637`) asserts that R1 requires `K13_VBAT_Cap` closed while
also listing `13` in `resourceSummary.keepOpenRelayNumbers`. Independent check of R1:

- R1 **does** require K13 closed — md `:221` (G3 functional relay), `:245` (`动作（必须闭） = 13, 65`),
  `:313`; json `relayGroups[G3].functionalRelays` = `K13_VBAT_Cap` / number 13.
- R1's keep-open list **does not contain 13** — md `:248` and json `resourceSummary
  .keepOpenRelayNumbers` are the same 16 numbers `[14,15,16,21,38,39,40,70,82,86,87,90,92,130,141,142]`;
  `13 in list → False`, `65 in list → False`.
- R3's cited `contract md :574` is **out of range**: R1 md is 441 lines.
- R1 md and json agree with each other; every R1 mention of K13 requires closure.

Therefore R1 and R3 **agree** on K13 and there was no inconsistency. `RT-1`'s requested repair ("one
authoritative statement of K13's state") already exists in R1. `RT-1` is retained as a **false
positive**, not as open engineering work. Withdrawn: the earlier captain framing (in
`implementation/captain-notes-t7.md` §2 and `implementation/t7-task-contract.md` §5) that R1
contains a K13 inconsistency the implementer must surface. The instruction to implement K13 per R3
stands, because it coincides with R1 and with the pre-change code at `:2171`.

### Round-6 findings — the pre-change function is already largely conformant (facts)

Read the rest of the pre-change function (my earlier flags were based on a partial read). All of the
following were verified line by line against R1 json `registerDelta` and R3 §3 P2/P4/P5/P7:

| Element | Pre-change code | Contract | Verdict |
|---|---|---|---|
| testmode unlock | `:2180` `entertestmode()` | R1 `registerDelta` entertestmode entry | conformant |
| `DMUX_SEL=22` | `:2182` `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)` | R1 `DMUX_SEL` entry names exactly this write | conformant |
| `DMUX_EN=1` | `:2183` `I2CWriteSameData(DEV_ADDR, 0x57, 0x08)` | R1 `DMUX_EN` entry names exactly this write | conformant |
| VBAT power-on | `:2176` `FV,3,FXVIe_PLUS_10V,FXVIe_PLUS_100MA,RELAY_ON` | R1/R3 P2 setpoint 3 V + the same range/limit pair | conformant |
| measurement pair | `:2190-2196` 20 V/100 mA source, 10 V/10 µA observation, `0.0→10.0` then `10.0→0.0`, 200 steps, 20 ms, capture 1.65 V, `TRIG_FALLING`/`TRIG_RISING` | R3 P4/P5 verbatim | conformant |
| hysteresis | `:2205` `(rise - fall) * 1e3` mV | R3 `Hys = Rise - Fall`, mV after R-HYS | conformant |
| power-down sub-step 1 | `:2209-2211` `FV=0`, `RELAY_ON`, P4 pairs | R3 P7 "range/limit held as in P4, relay still ON" | conformant |
| power-down sub-step 2 | `:2213-2215` `FV=0`, `RELAY_OFF`, `…_10MA` | R3 states no range/limit here | not a deviation |
| CSV-layer alternative | absent from code | R1 registers `0x55=0x97` / `EN_DTEST0,DTEST0_MUX=23` as a **registered conflict** | correct to omit |

**Withdrawn (round-4 check item C4):** my suspicion that the power-down range/limit pair deviates
from R3. The `10MA` values sit in the `RELAY_OFF` sub-step, where R3 constrains nothing; the
`RELAY_ON` sub-step uses exactly the P4 pairs. Corrected in `review/t8-review-task-contract.md` §4c.

**New fact (check item C7):** `test.cpp` contains **103** `cbite.SetOn` calls and **zero** `cbite`
release/reset calls — project-wide, not just for TM108. So the absence of an explicit closure-set
release in the TM108 function is the codebase convention, and must not be scored as a deviation from
R3's P8. The framework's per-item relay reset is **UNKNOWN** (not verified this session).

## 7. Next pointer

Wait for t7's completion notice (notify-driven; never in-turn blocking).
- `DONE: t7` → verify claimed `beforeSha256`/scope against §3, then dispatch t8 with
  `review/t8-review-task-contract.md`.
- `BLOCKED: t7` → answer from `captain-notes-t7.md` if it is an ownership question; escalate to the
  user with one precise question + evidence path only if it is a genuine electrical ruling.
