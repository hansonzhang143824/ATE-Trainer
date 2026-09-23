# t8 — TM108 independent rule review

- **Task:** `t8` · **Role:** `rule-reviewer` · **Run:** `tm108-v2-impl`
- **Reviewed deliverable:** `t7` (`ate-implementer`) — TM108 implementation in `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp`
- **Reviewer:** `rule-reviewer` (did not produce and must not modify anything reviewed)
- **Date:** 2026-09-17T21:33:06+08:00
- **Machine-readable twin:** `t8-review-findings.json`

## Verdict

> ### `needs-revision`

The **executable content** of the deliverable is verified faithful to the signed contracts on every point this review could test. The verdict is **not** `pass` on one blocking count: **R3 §6 `logPlan` requires 10 log records and the implementation emits 3**, with the remaining 7 present only as comments — and I independently confirmed that this file exposes no logging primitive other than `CParam::SetTestResult`, so the requirement as written cannot be met in code. That is a **contract-vs-capability** finding owned by `test-method-expert`, not a code defect (per the t8 contract's own instruction for `C11`).

Per `ROLE_ROUTING.md:47`, the compile stage (`t9`) may not start until a `rule-reviewer` `pass` exists, so **`t9` is held** and this review **does not hand off downstream**.

> **Scope correction applied (captain input during t8).** The t8 contract restricted the `C11` verification to "no other logging primitive exists **in `test.cpp`**"; the captain withdrew that restriction as its own error, because "absent from `test.cpp`" is not "absent from the project". `C11` and `RF-01` were therefore re-based on a project-level probe of every named candidate (`BoardCheck.h`'s `CBC_log`, `treg.h`'s `TREG_LOG::log_data`, `treg.h`'s `TREG_ERROR::treg_error_log`, and the `log_data_t`/`test_t` typedefs). **Every candidate was ruled out**, so the ruling and the terminal verdict are **unchanged** — see the C11 addendum in §3.

| | |
|---|---|
| Blocking findings | **1** (`RF-01`, owner `test-method-expert`) |
| Non-blocking findings | 3 (`RF-02`, `RF-03`, `RF-04`, all owner `ate-implementer`) |
| Waived findings | 3 (`WF-01`, `WF-02`, `WF-03`) |
| Gates passed | 9 · failed 1 · not verified / out of scope 2 |
| Residual risks | 11 |

---


> ### ⚠ REVISION DRIFT — the reviewed pair no longer exists on disk
>
> This review examined **`test.cpp` `b79b911a…d5a` (477123 B) + `implementation-manifest.json` `a4f5286d…556` (25688 B)**, preserved for audit at `review/copy/test.cpp`.
> **While the review was running — not by me; I wrote only under `review/` — `test.cpp` was replaced and the manifest was rewritten twice.**
>
> | | as reviewed | currently on disk (last read) |
> |---|---|---|
> | `test.cpp` | `b79b911a…d5a`, 477123 B, mtime 21:29:56 | **`456fba2c…eaa`, 477760 B, mtime 21:39:39** |
> | manifest | `a4f5286d…556`, 25688 B | **`58c54c48…78e`, 41935 B, mtime 21:41:13** |
> | `t7-selfcheck.md` | `a13ef000...`, 18594 B | **`160803f22435...`, 30825 B, mtime 21:42:27** |
>
> The manifest was observed at **three** sizes/hashes inside this window (`a4f5286d…` → `26171fca…` → `58c54c48…`). The newer pair is internally consistent, but it is **not** the pair this review examined, so **my hash binding no longer describes the state on disk** and this review cannot serve as the gate for the current revision. See **`RF-05`**, gate **`G-13`**, risk **`RR-14`**, and the `revisionDrift` block in the JSON. The self-check artifact was rewritten as well, from 18594 B to 30825 B.
>
> Re-checked against the newer revision where I could: **`RF-02` and `RF-03` are repaired** there; **`RF-01` is not** (and cannot be — it is a contract-vs-capability finding); `RF-04` **not verified**. The terminal verdict is unchanged.

## 1. Independence, read-only discipline and hash snapshot

**Read-only.** I never wrote to `D:\PROJECT6-DALI\ForCodexDebug` or to `D:\PROJECT6-DALI\devel`. The reviewed file was copied byte-for-byte into `review/copy/test.cpp` (python byte mode) and all inspection was done on that copy plus the pre-change backup. Every write of this task went under `team/artifacts/tm108-v2-trial/review/` only.

**DLP discipline.** All reads and hashes of `test.cpp` used python byte mode only (`open(p,'rb')`) with `C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`. I used no pwsh `Get-Content` / `Set-Content` / `Select-String` / `Get-FileHash` and no .NET file API on any DLP-transparent-encrypted file. Every hash below is labelled **plaintext**.

**Files are unchanged by this review.** I took a plaintext snapshot before the review and again after it. **Every value is identical**, so no reviewed artifact was touched:

| File | plaintext sha256 | bytes | BOM | CRLF | bare LF | unchanged |
|---|---|---|---|---|---|---|
| `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` | `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a` | 477123 | yes | 9434 | 3 | ✅ |
| `review/copy/test.cpp` (my copy) | `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a` | 477123 | yes | 9434 | 3 | ✅ byte-identical to the live file |
| `implementation/backup/tm108-v2-impl__test.cpp.before` | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | 469714 | yes | 9350 | 3 | ✅ |
| `implementation/implementation-manifest.json` | `a4f5286da293f0e564849e37afce263e7bce38d08753503189a25e1bcbeba556` | 25688 | – | – | – | ✅ |
| `implementation/t7-selfcheck.md` | `a13ef000e6305b20e2316262aeece15403afff16ba58a3b08ce2c49f98dac2db` | 18594 | – | – | – | ✅ |
| `strategy/tm108-resource-config-contract.md` | `6f6057721062e97ebda53531383aff22a91bd0aa8141aadc6bafc5ef448fe6e4` | 42261 | – | – | – | ✅ |
| `strategy/tm108-resource-config-contract.json` | `fba489b5d8ca06a12d74c187edbbfe1e2f3fc2d564b27dc6ab8b092f8bd3e4b9` | 66422 | – | – | – | ✅ |
| `method/tm108-test-method-contract.md` | `8eb56d24678406219fe83c3d9e7f09d7d3ec5c39a7a52403f72464802fca1fa7` | 90822 | – | – | – | ✅ |
| `method/tm108-test-method-contract.json` | `f947e6c626d32a01fb159c57c32a8f9cc0e9ceff60b45ea445610123cc3c0e21` | 102544 | – | – | – | ✅ |
| `method/bst-sw-phase-check.md` | `fa41e471ae549ab0affcf629fc1d691703281a08498cfe10c26d926c4d115e54` | 9860 | – | – | – | ✅ |
| `source/BoardCheck.h` — widened C11 scope | `ad562c1c14929bbf71f5549269ce6c44c16352eb4d4299a130952f714d5d83ea` | 32536 | – | – | – | ✅ |
| `source/treg.h` — widened C11 scope | `e10c2ac7e2b53b043467ed1579e76de9c41bde2b6e7d5b787a3e0d8ccc262bbc` | 51157 | – | – | – | ✅ |
| `source/src/treg.h` — duplicate-copy check | `ae0d6d6221f8fdb5409e98956218211740170ad6bbfa70ef016d0efbf61450ff` | 47730 | – | – | – | ✅ |

**Signed contracts re-hashed by me, not trusted.** R1–R5 all reproduce the hashes stated in the t8 contract. In particular R1 is **441 lines** long — which matters for C10.

**Open items — nothing resolved, closed or relabelled.** `OI-T4-01`, `OI-T4-04`, `OI-T5-01`, `OI-T5-02`, `OI-T5-03`, `OI-T5-05`, `RT-1`, `RT-2`, `RT-3`, `RT-4`, `RT-5`, `F1`–`F6` and `OI-T4-10/11/12/13/14/16` are all left exactly as open as I found them. I selected no side in any conflict.

**No build, no gate script, no hardware claim.** Compilation belongs to `compile-diagnostician`.

---

## 2. What the change is — independently reconstructed

Anchors: the **live file** TM108 span is **2193–2309** (signature at 2193, closing brace at 2309); the **pre-change backup** TM108 span is **2155–2225**. Both reproduce the captain's figures.

| Property | My measurement | Captain's claim | Agrees |
|---|---|---|---|
| Added lines | 97 | 97 | ✅ |
| Removed lines | 13 | 13 | ✅ |
| Non-comment changed lines | **0** | 0 | ✅ |
| Non-comment line sequence | **identical** (5628 items each) | byte-identical | ✅ |
| Comment-stripped, whitespace-normalised text | **byte-identical**, both `0341d69a9b23ffb62bff99e0c777392a609bef1a2316ce66664e460714cb739f` (236169 chars) | – | stronger than claimed |
| Changed range | backup `2150..2217`, live `2150..2301` | inside the TM108 span | ✅ |
| Diff hunks | **3** at `unified_diff n=3` (`@@ -2147,10 +2147,48 @@`, `@@ -2165,32 +2203,60 @@`, `@@ -2199,22 +2265,40 @@`) / **13** raw change blocks | 3 hunks | ✅ same measurement, two conventions |

The **comment-only** claim is confirmed twice over: no added or removed line is an executable statement or a blank line's code neighbour, and the two files are identical once comments and whitespace are removed. It is therefore **impossible** for any executable value to have changed — I also confirmed the values positively, below.

**Backup authenticity (decisive).** The captain's independently captured pre-change block `captain-precheck/tm108-block-before.txt` (sha256 `19fe6b5c7770e8f0f9882a040d6354d29db07f7684e8cb9fabbf10abc4194416`, 81 lines) matches the t7 backup at **lines 2147..2227 exactly, line for line**. The pre-change image is a genuine capture, not a reconstruction.

**Hash binding.** `implementation-manifest.json` `changes[0].afterSha256` `= b79b911a…d5a` `=` the plaintext sha256 **I computed on the live file**. The manifest is **not stale**; the deliverable is reviewable as one hash-bound artifact.

---

## 3. Check items C1–C12 — every item answered

### C1 — is the `DTEST0 == nQON` assertion gone? — **SATISFIED**

Gone, not merely softened. The pre-change banner asserted it twice (backup `:2150` "digital V(DTEST0)", `:2152` "measure V(DTEST0)=nQON toggle (r 4.059 f 3.738)" — note those two numbers have no basis in R1–R4), and the inline comments at backup `:2189`, `:2193` asserted the inverted alias again. The live banner instead says "capture the digital toggle on the observation candidate" (`test.cpp:2152`) and **explicitly disclaims the equality**:

> `test.cpp:2182-2184` — "the DFT check pin V(DTEST0) is **NOT equated** with the nQON candidate – the observation allocation RA-5 is marked CANDIDATE ONLY"

The capture is labelled `PENDING-OI-T4-01` at `test.cpp:2245` and the polarity premise is `PENDING` at `test.cpp:2250`. This is exactly the "re-worded as pending OI-T4-01" outcome, and it matches R1 §4.1 ("本契约**不假设** `DTEST0 == nQON`").

### C2 — closure set still `{13, 65}`, nothing added or removed? — **SATISFIED**

`test.cpp:2218` `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` is a non-comment line, and the non-comment sequence is byte-identical (G-04), so it *cannot* have been altered. No relay was added to or removed from the `SetOn`. `K21_VAC_Cap` is **not** in it. Matches R1 G3 (`:224` closure `{13, 65}`), R1 `:245` (must-actuate = 13, 65), R1 `:225` (frozen-baseline cross-check names this exact call form) and R2 line 493 (`relayGroups[G3].closureSetActuatedThisStage = [13, 65]`).

### C3 — the `K21_VAC_Cap` scanned-input exception preserved? — **SATISFIED**

Pre-change backup `:2169` "do NOT close K21_VAC_Cap" → live `test.cpp:2211` "VAC1 is the scanned input, so **K21_VAC_Cap must stay un-actuated** – no cap across the node", and the banner lists `K21_VAC_Cap` **first** in the isolation set at `test.cpp:2167`. Matches R1 `:200`, `:248` and R1's own confirmation at `:225`. The cap-gate asymmetry (close K13, never K21) required by R1/R3 is preserved.

### C4 — the power-down ranges — **SUPERSEDED BY §4c; CONFORMS, NO FINDING**

I verified the two sub-steps separately against R3 instead of against the pre-change limits, as instructed.

- **Sub-step 1** (`test.cpp:2281-2283`): all three channels zeroed while **holding** their working range with the relay still ON — `VAC123_AMUX_ACM` at `ACM200_20V/ACM200_100MA` (the **exact P4 pair**), `VBAT_PD3_FXVI` at `FXVIe_PLUS_10V/FXVIe_PLUS_100MA`, `NQON_HG1_ACM` at `ACM200_10V/ACM200_10UA`. This is precisely R3 P7's "FV=0, range/limit held as in P4, relay still ON" (`md :384`) and R3 §5 actions 1–3.
- **Sub-step 2** (`test.cpp:2290-2292`): the unified `RELAY_OFF` pairs `ACM200_10V/10MA` and `FXVIe_PLUS_10V/10MA` — exactly R3 §5 action 5 (`md :506`).

So the pre-change suspicion does **not** survive the fuller read, as the captain already ruled, and the `10MA` in sub-step 2 is **not** a deviation from anything R3 says: R3 prescribes no range for that sub-step beyond the unified `RELAY_OFF` table, and the code matches that table. `delay_ms(1)` sits between the sub-steps as R3 §5 action 4 requires. **No code finding and no contract-wording gap is raised here.**

### C5 — is the 1.65 V level presented with its provenance? — **SATISFIED**

Not a DFT fact anywhere. The banner attributes it to the method contract and labels the geometry a method-side position with the governing conflict open:

> `test.cpp:2172-2174` — "capture level **1.65 V** … (**method** sec.4 "segment rise"/"segment fall"; the geometry is a **method-side position**, F5 open)"

and the sweep geometry is separately attributed at `test.cpp:2241` ("recorded because F5/OI-T4-13 is open"). The inline comment at `test.cpp:2213` grounds the level physically ("the pull-up is what makes a 1.65 V capture level a mid-scale logic threshold"), matching R3 `md :210`/`:311` and R1 `:121`.

*Residual note, not a finding:* the token `OI-T5-03` — the open item under which R3 `md :621` registers exactly these method-side positions — appears neither in the code banner nor in the manifest `openItems[]` (see RR-06). R3's own handoff list (`md :658`) does not require the implementation to carry it, so I do not score it.

### C6 — was any tolerance, guard band or limit literal added? — **SATISFIED**

No. Step 6 reporting is three calls of the form `SetTestResult(site, 0, value)` at `test.cpp:2304-2306` with **no limit argument, no tolerance expression and no pass/fail branch**. My independent numeric inventory of the entire body `2193-2309` finds only these literals: `0, 1, 3, 20, 0.0, 1e3, 200, 1.65, 10.0` — every one an argument of a pre-existing call, none a limit or tolerance. The banner states at `test.cpp:2190`: "RT-4/OI-T4-09 no tolerance is published … none is invented", and `RT-4` is carried in manifest `openItems`. This confirms `RT-4` is a spec-side matter, not a code artifact.

### C7 — the project-wide absence of any release call — **WAIVED, NOT SCORED** (assertion defect raised separately as RF-02)

I measured the pattern myself rather than accepting it: **104** `cbite.SetOn` occurrences and **zero** occurrences of `SetOff` / `RelayOff` / `Reset` / `.Off(` / `DelayOff` / `SetOffAll` in **both** the pre-change and the post-change file. No item in this file releases a closure explicitly, so TM108's lack of a release call is the **project convention**, not a deviation — per the check item it is **not scored against `t7`** (waived as `WF-01`). The framework behaviour that R3 P8 action 6 depends on was **not verified in this session** and is not the implementer's to invent; it is recorded as an unverified gate (`G-09`) and residual risk `RR-01` in the test framework / `compile-diagnostician` territory.

What I *do* score separately is that the code states that unverified framework behaviour **as an established fact** (`test.cpp:2178-2179`, `:2287-2289`) — a wording defect, `RF-02`. This does not contradict the waiver: `RF-02` scores the assertion, not the omission.

### C8 — verified conformances, no regression — **ALL REPRODUCED**

| Item | Live location | Contract |
|---|---|---|
| `entertestmode()` | `test.cpp:2235` | R1 §7 / R3 P3 step 1 |
| `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)` = `DMUX_SEL=22` | `test.cpp:2237` | R1 §7 |
| `I2CWriteSameData(DEV_ADDR, 0x57, 0x08)` = `DMUX_EN=1` | `test.cpp:2238` | R1 §7 |
| `VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON)` | `test.cpp:2227` | R3 P2 / RA-3 |
| `rampv_capv` rise: `ACM200_20V/100MA` source, `ACM200_10V/10UA` observe, `0.0→10.0`, `200`, `20`, `1.65`, `TRIG_FALLING` | `test.cpp:2253-2255` | R3 §4 segment rise |
| `rampv_capv` fall: mirrored, `10.0→0.0`, `TRIG_RISING` | `test.cpp:2260-2262` | R3 §4 segment fall |
| `hys[site] = (rise - fall) * 1e3` | `test.cpp:2273` | R-HYS (mV) |
| CSV-layer alternative `0x55=0x97` / `DTEST0_MUX=23` **absent** | – | R1 §7 (registered conflict, not adopted) |

Because the non-comment sequence is byte-identical before/after (G-04), **none of these can have regressed** — and I confirmed each value positively rather than inferring it from the absence of a diff. The only comment-side change here replaces the misleading "nQON falls through 1.65 V (inverted)" wording with an explicit PENDING statement: an improvement, not a regression.

### C9 — sibling-TM usage is not authority — **SATISFIED**

I treated codebase-wide usage and the knowledge base as non-evidence throughout. The `DTEST0 = nQON` alias does appear across sibling items (e.g. `test.cpp:1951-1961`, `:2110-2120`, `:2351-2358`, `:7741-7744`), and `TM109`/`TM110` are structurally the same test as the untouched TM108 baseline — a **convenience-copy risk, not corroboration**. Nothing in TM108's own region asserts the alias, and **no change outside TM108 was made or requested**: the changed range is backup `2150..2217` / live `2150..2301`, entirely inside TM108's banner and body, with zero non-comment lines changed.

### C10 — the refuted `DEV-1` claim — **SATISFIED ON THE REVISION REVIEWED; the claim has been withdrawn**

I judged the revision actually before me, checking C10's three sub-problems:

- **(a) substantive claim** — no longer made. `deviations[DEV-1].subject` now reads *"RT-1 claim about K13 – **WITHDRAWN** by this role after independent re-check"*, and the body states the contradiction *"does NOT survive re-checking"* and *"R1 and I3 AGREE and there was never a contradiction to resolve"*.
- **(b) false framing in the subject line** — gone. It is no longer described as a `REPORTED CONTRACT INCONSISTENCY`; manifest `openItems` `RT-1` reads *"REFUTED – NOT carried as an engineering item, and no R1 contradiction is claimed"*.
- **(c) mis-routing to `test-strategy-architect`** — gone. `DEV-1.ownerOfResolution` now reads *"none required (captain already refuted RT-1…)"*.

The **code banner** was corrected the same way: `test.cpp:2186-2189` reads *"RT-1 REFUTED by independent re-check of the signed strategy contract … the earlier RT-1 claim is withdrawn, not carried"*. So **no artifact of this delivery asserts an R1 contradiction**, and `DEV-1` does not stand as a valid deviation.

I verified the premise myself rather than trusting the cancellation:

| Check | Result |
|---|---|
| R1 `md :248` keep-open list | exactly **16** relays: `14,15,16,21,38,39,40,70,82,86,87,90,92,130,141,142` — **no 13, no 65** |
| R2 line 574 `keepOpenRelayNumbers` | the **identical 16-number** list — confirms (c) the `:574` citation is a JSON line, not an md line |
| R2 line 493 `relayGroups[G3].closureSetActuatedThisStage` | `[13, 65]` |
| R1 `:245` | places `13, 65` under **动作（必须闭）** = must actuate |
| R1 length | **441 lines** → the cited `contract md :574` is out of range |

**Timing:** the correction post-dates the first manifest revision and is present in the revision under review — the revision that matters.

The stale citation survives **only inside R3 §10** (the upstream signed contract). I record that as `WF-02` / `RR-10` rather than resolving it: my charter forbids me from resolving, closing or relabelling `RT-1`, and the t8 contract forbids failing the implementation for a non-existent inconsistency.

### C11 — the `logPlan` raw-context question — **NOT SATISFIED; RULED AS A CONTRACT-VS-CAPABILITY FINDING → `test-method-expert`** (blocking, `RF-01`)

**My position: "it is in the comments" does NOT satisfy R3 §6 `logPlan` as a record.** I state that as a verdict rather than deferring it.

Why the requirement is for *emitted records*: R3 §6 (`md :530-551`) is a table of **logicalIds** in a section named `logPlan`, with a `kind` column distinguishing `calculated` / `raw context` / `context`. Its own notes justify each raw-context row by what a reader **of the log** must see — *"without it a reviewer cannot tell which premise was in force"* (`triggerModeRise/Fall`), *"a log that hides the geometry makes the conflict unresolvable after the fact"* (`sweepGeometry`), *"the applied values must be **logged**, not the contested ones"* (`registerActivationTrace`) — and R3 `md :486` requires a no-trigger segment to **record** the failure context including *"the actual start/stop/step/interval values **used**"* rather than write a substituted number. A static comment cannot carry "the values actually used": it is text that would not follow the code if the code changed.

**What the code does:** emits **3 of 10** rows (`test.cpp:2304-2306`) and concedes the rest at `test.cpp:2296-2299` ("The remaining logPlan context quantities … are carried by the trace comments in this function"). `relayActuationTrace` occurs **once in the entire 9437-line file**, at `test.cpp:2207`; `registerActivationTrace` **once**, at `test.cpp:2231`. Both are comments.

**I verified the capability claim independently** (this is the branch C11 told me to check, because a missed primitive would make it a code finding against `ate-implementer`). Using a string-literal-aware comment stripper over the whole file and inventorying every callable in **real code**:

- the **only** log-writing call anywhere in `test.cpp` is **`SetTestResult`** (187 code call sites);
- `GetMeasResult` (64 sites) is a measurement readback, not a log write; `STSSetInitSelectDialog` (2) is a UI dialog;
- **`LogData` occurs 91 times and is *always* a `// ====== Step 6: LogData ======` comment header, never a call**;
- `printf`/`cout` appear only in the hotkey/UI code at `test.cpp:390` and `:564-569`;
- **no** function defined in `test.cpp` takes a string/format for logging;
- independently, the active standard **R-LOG itself defines the log rule in terms of `SetTestResult`** (`rules-registry.md:37`) and names no other primitive.

**Conclusion:** no existing primitive was missed → this is **not** a code finding against `ate-implementer`. It is a **contract-vs-capability** finding, and the need returns to **`test-method-expert`**.

**Related second gap under the same rule.** R3 §4 (`md :486`) and §6 (`md :544`) require that a segment with no trigger, a boundary trigger or a negative Hys **record failure context instead of writing a substituted number**. The code has **no no-trigger detection at all**: `vth_r`/`vth_f` are initialised to 0 (`test.cpp:2247-2248`), copied at `:2265-2266` and logged unconditionally at `:2304-2306`. If a segment produces no trigger, **0 is logged as `VAC1_PRST_Rise`/`_Fall`** — the opposite of R3 `:544` and of the code's own comment at `test.cpp:2299` ("No placeholder number is ever logged in place of a missing capture"). I mark this an **INFERENCE, not a measured fact**: `functions-registry.md:43` documents only the `rampv_capv` signature and "result = the voltage at the trigger point", with no no-trigger signal and no documented return value, so the primitive's real behaviour is **UNKNOWN** to me. It is recorded as `RR-02`, not asserted.


#### C11 addendum — captain scope correction (widened project-level verification); ruling UNCHANGED

The captain withdrew the t8 contract's own restriction of this check to "no other logging primitive exists **in `test.cpp`**", on the principle that **"absent from `test.cpp`" is not "absent from the project"**. My first pass committed exactly that narrow-scope error; that narrower basis is **superseded**, and the finding is re-based on the probe below. Every candidate was examined in python byte mode with mechanism-level evidence, not by name inspection.

**(i) `BoardCheck.h:214 class CBC_log` — `log()` at `:759`, `test_log()` at `:760`, instance `CBC_log bc_log;` at `:778`. NOT USABLE.**

- `BoardCheck.h` is **not in the transitive include closure** of `test.cpp`. The closure I computed over local headers is `Coutlier.h`, `FMEA.h`, `LogDataStruct.h`, `Pin_Channel_define.h`, `StdAfx.h`, `Test_Method.h`, `mylib.h`, `spec.h`, `src/visa.h`, `src/visatype.h`, `stdafx.h`, `sub.cpp`, `sub.h`, `tempchar.h`, `test.cpp`, `treg.h` — **`BoardCheck.h` is absent**, so the type is not even declared for a TM translation unit.
- `log`/`test_log` (`:759-760`) are public *members of `BoardCheck`* (nearest specifier `public:` at `:346`, next `private:` at `:767`), but the **only instance** `CBC_log bc_log;` (`:778`) is in `BoardCheck`'s **private** section.
- `CBC_log`, `bc_log` and `test_log` have **zero users outside `BoardCheck.h`/`BoardCheck.cpp`** across all 36 source files scanned.
- The only instantiations are a **local** `BoardCheck bc;` at `source/diags.cpp:80` and inside `run_diags()` (`source/diags.cpp:188`), which `test.cpp:797` calls **once from the startup path** behind `if (DO_BoardCheck)` — never from a TM.
- The qualified name **`CBC_log::` occurs 0 times anywhere in the tree** — `log()`/`test_log()` are declared but **never defined and never called**.
- `BoardCheck` is a dialog-based board-check utility (`BoardCheckGroup`, `DialogTemplate`, listbox, buttons, `SetConsoleTextSize`). `BoardCheck.cpp` writes **nothing** to the station datalog — **0** `SetTestResult`, **0** `msLogData`, **0** `SetTestNumber`; only `GetMeasResult` (151), i.e. it **reads** results and CSV. Its "Save datalog" comments are its own board-check CSV.

**(ii) `treg.h:195 TREG_LOG::log_data` — the important negative result. NOT REACHABLE.**

- Declared under **`private:`** (`treg.h:194`) in `class TREG_LOG`, whose friends are only `TREG`, `TRIM_NODE` and `TRIM_GRP_NODE` (`:187-189`). A TM function is none of those.
- Its implementation (`treg.cpp:285-348`) **is a genuine datalog write path with exactly the shape R3 §6 needs** — it carries a `testname` string plus limits and unit: `log_data_func(site, testname, lolim, hilim, value, unit, no_scaling)`, else `test_func(testnum, value, site, 0)`, else `msLogData(...)`.
- But **every piece of the plumbing is private static**: `TREG_LOG::datalog_func` (`treg.cpp:275`), registered by the private `register_dlog_func` (`treg.h:197`); the `log_data_func`/`test_func` helpers are private to the `TREG_ETS364` path.
- The **only public route into it** is a `TRIM`/`TRIM_GRP` node's `execute(..., int log_level = TREG_LOG_STD, ...)` (`treg.h:559`, `:565`, `:742`) — i.e. the **Trim framework**, which R1 §1 declares TM108 does **not** trigger (`trim = null`; "Trim 判定 否（不触发 Trim 框架）"). There is no public `TREG` wrapper: the only `log` members on the `TREG` side are the private `log_data`, the `TREG_LOGLEVEL` enum, and the `log_level` default parameters.
- This holds for **both** `treg.h` copies in the tree.

**(iii) `treg.h:176 TREG_ERROR::treg_error_log` — public static, therefore technically callable, but NOT a `logPlan` vehicle.**

- Its definition (`treg.cpp:227-251`) is a **debug console error channel**: it increments `error_count`, and on the first call does `FreeConsole(); AllocConsole(); SetConsoleTitleA("AccoTEST Debug Window"); freopen("conout$", "w+t", stdout);` then `printf_s(" %d. ", error_count); printf_s(buffer);`.
- **All 47** of its uses in `treg.cpp` are **error paths** ("TREG: No TRIM parameter defined.", "post_value define is wrong in PGS…"); **none** is a data record.
- Its sibling `TREG_ERROR::error` (`treg.cpp:256-267`) routes to `error_func` → `etsfatalerror()` (ETS364) or `MessageBox()` — a **fatal error**, categorically not a log.
- `TREG_ERROR` is used **0 times** in `test.cpp` and `sub.cpp`.
- It cannot produce R3 §6's unit/precision/per-site datalog records, and routing data through it would misuse a fatal-error console channel.

**(iv) `treg.h:108` / `:110` `log_data_t` / `test_t`** — **callback typedefs** under `#ifdef TREG_ETS364`, not callable primitives; the callback is invoked only from the private `TREG_LOG::log_data`. Not a vehicle.

**Also checked and negative.** `Test_Method.h` (the object owning `rampv_capv`) has **zero** log-related members; `sub.h` has none; `LogDataStruct.h` defines `CAccoCsvData`, a **CSV datalog reader** (`load_data` into `test_vec`/`lolim_map`/`hilim_map`/`unit_map`/`val_map`), not a writer; `mylib.h` has no logger. No other candidate API name exists in the tree: `WriteLog`, `AddLog`, `LogMessage`, `PrintLog`, `SetLog`, `LogString` = **0 hits**; `msLogData` only in `treg.cpp`; `DataLog` once in `BoardCheck.cpp`.

**Positive corroboration that `SetTestResult` *is* this project's datalog primitive.** The framework's own logdata helper `source/src/treg.cpp:62 stslogdata()` writes through `CParam::SetTestResult`; the active standard **R-LOG defines the log rule in terms of `SetTestResult`** (`rules-registry.md:37`); and `LogData` in `test.cpp` is 91 raw tokens with **0** occurrences as a call — exactly the step label the captain said it was. I did not mistake it for an API.

**Ruling: UNCHANGED.** No candidate is usable, so `DEV-3` remains a **contract-vs-capability** finding owned by **`test-method-expert`** — **not** a code finding against `ate-implementer`. The widened evidence *sharpens* it: a real datalog primitive does exist in the framework, but it is deliberately **fenced to the Trim framework**, which this item by R1's own classification does not use.

**Verified vs inferred vs unknown — stated explicitly.**

- **Verified by measurement:** R1–R5 hashes; the live/backup/manifest hash binding; the backup against the captain's independent pre-change block; the comment-only nature three ways; the TM108 spans; the `test.cpp` include closure; the access specifiers and friend lists in `BoardCheck.h` and both `treg.h` copies; the absence of any `CBC_log::` definition tree-wide; the definition of `treg_error_log`; and the counts recorded below.
- **Inferred (flagged):** that a no-trigger segment logs the `0` initialiser (`RR-02`) — because `rampv_capv`'s no-trigger behaviour is undocumented.
- **Unknown (flagged, not assumed):** **`CParam`'s full public surface** (`RR-12`), the framework's per-item relay reset (`RR-01`), and which `treg` copy is in the build (`RR-13`).

**Honest limit of this conclusion — a residual UNKNOWN (`RR-12`).** `CParam` is the only framework object a TM holds (`StsGetParam` returns `CParam*`), and **no `class CParam` declaration exists anywhere under `D:\PROJECT6-DALI\ForCodexDebug`** — the token appears there only as a *use* (`test.cpp` 668, `source/src/treg.cpp` 2, `Shmoo.h` 1, `Test_Method.cpp` 1). It is declared in an **external SDK header not present in this checkout**, so its full public API **cannot be enumerated from this tree**. The observed surface used in `test.cpp` is `SetTestResult` (188), `GetMaxLimit` (3), `getNextParam` (4), `get_param_name_in_spec` (4). If that SDK header exposes a text/logging method reachable from a TM, **`RF-01` must be re-opened as a code finding against `ate-implementer`**. I cannot rule that out here, and I do not claim to.

**Count discrepancy, recorded for reconciliation.** The captain's figures "`SetTestResult` (200 uses) and `GetMeasResult` (422)" do not reproduce against any file set I measured. My measurement of `test.cpp`: `SetTestResult` **188** call sites (188 raw tokens); `GetMeasResult` **65** raw, **64** comment-stripped. Tree totals over the 36 source files: `SetTestResult` **244**; `GetMeasResult` **574** (`sub.cpp` 204, `Test_Method.cpp` 153, `BoardCheck.cpp` 151, `test.cpp` 65, `tempchar.cpp` 1). This does not affect the C11 conclusion, which rests on access specifiers, include closure and method definitions rather than on counts.

### C12 — the `K17` closed-state requirement — **I ACCEPT THE "NO CALL" READING**

**Which reading I accept and why:** I accept that this is a **valid exercise of the delegated decision**, and that **R1's requirement is satisfied by inheritance**. I do not accept it merely because the contract delegates it — four independently checked reasons:

1. **R1's own partition does not class relay 17 as an action of this item.** R1 §6.1 separates `动作（必须闭）` = `13, 65` from `须处于闭合态` = `17`, and annotates 17 as *"the VAC low-domain BUS entry (same source as the VAC branch, **非本项新增动作** — not a new action of this item)"*. R1 G1's closure set is explicitly `[]` (*"仅需 K17 在闭合态"*). R1 therefore requires the **state**, not an actuation.
2. **The machine-readable boundary places relay 17's actuation in the group this item does not use.** R2 line 520: `relayGroups[G4].closureSetActuatedThisStage = [17]` — and G4 is the **alternate** allocation that R1 says must **not** be enabled together with G1–G3. R2 lines 453/467/493 show the applied groups G1/G2/G3 with closure sets `[]`, `[]`, `[13,65]`.
3. **R3 explicitly withholds the call form.** R3 P1 (`md :199`): *"K17 is required to be in the closed state … WITHOUT this method claiming how it got there – OI-T4-04 is still open, so no actuation call for K17 is written by this contract (**ate-implementer decides the call form** under OI-T4-04)"*. R3 P8 (`md :428`) confirms the outcome: K17 *"is left as the VAC branch entry state requires; releasing it would re-open the branch and is therefore NOT part of this method"*.
4. **The measured evidence is decisive, and I reproduced it.** `K17_BUSL_VAC` occurs **0 times** in the entire pre-change `test.cpp` and exactly **3** times post-change, all 3 inside TM108's own trace comments (`test.cpp:2162`, `:2208`, `:2214`). No TM in the file actuates relay 17, so the closed state is an **inherited test-program precondition**, and writing a `SetOn` would have invented an actuation decision that neither contract makes — and that R1's partition explicitly declines to call an action.

The disposition is recorded openly rather than silently: manifest `deviations[DEV-2]`, manifest `openItems` `OI-T4-04`, and the code comment at `test.cpp:2214-2216`. **`OI-T4-04` remains open; I neither close nor relabel it.**

---

## 4. Conformance summary

| Area | Verdict | Basis |
|---|---|---|
| Source tables / channels / paths | **conforms** | RA-1/RA-2 `VAC123_AMUX_ACM S5_0`, RA-3/RA-4 `VBAT_PD3_FXVI S3_5`, RA-5 `NQON_HG1_ACM S5_9` (CANDIDATE ONLY) — each used exactly as allocated |
| Relay groups / closure set / isolation | **conforms** | closure `{13,65}`; K21 and the whole isolation set un-actuated; K8/K18/K19/K64 default-conducting; K17 state-only |
| Register delta | **conforms** | `entertestmode` + `(DMUX_EN=1, DMUX_SEL=22)`; no de-activation write; CSV alternative registered as not applied |
| Phase order P0–P8 (9 phases) | **conforms** | verified phase by phase — see the `phaseTrace` array in the JSON |
| Power-down (P7 → P8) | **partially conforms** | action 5 conforms exactly; action 6 (explicit release) has no call → **waived** `WF-01`, unverified gate `G-09` |
| Measurement plan (ranges, ramp, samples, capture, triggers, calculation, units) | **conforms** | C8, all reproduced |
| Limits / tolerance | **conforms** | no limit or tolerance invented; `RT-4` carried |
| BST/SW constraint | **conforms** | 0 driving actions; the 9/9 unproven conclusion carried, as R5 `:59-:60` requires |
| `logPlan` | **FAILS** | 3 of 10 rows emitted; 7 comment-only → `RF-01` |
| Signature / scope / file integrity / hash binding | **conforms** | G-01, G-02, G-03, G-05, G-06, G-07 |

---

## 5. Findings

### RF-01 · **blocker** · `test-method-expert` — the `logPlan` record is not implemented (contract-vs-capability)

| | |
|---|---|
| **TM** | TM108 |
| **Category** | measurement/log method — contract-vs-capability |
| **Violated rule** | R3 §6 `logPlan` (`md :530-551`; raw-context rows `:539-:545`) and §4 failure context (`md :486`), with §6's prohibition at `md :544` |
| **Owner** | `test-method-expert` |
| **Blocking** | **yes** |

**Evidence** — in the TM108 body the only logging call is `CParam::SetTestResult` at `test.cpp:2304-2306` (3 of 10 `logPlan` rows). All 7 raw-context/context rows exist **only as comment text**: `relayActuationTrace` (1 occurrence in the whole file, `test.cpp:2207`), `registerActivationTrace` (1 occurrence, `test.cpp:2231`), `sweepGeometry` (`:2241`), `triggerModeRise/Fall` (`:2251`, `:2256`), `captureLevel` (`:2257`), `failureContext` / `bstSwStatus` (`:2297-2299`). The code concedes it (`test.cpp:2296-2299`). **Independent capability check** (see C11): the only log-writing primitive anywhere in `test.cpp` is `SetTestResult`; `LogData`'s 91 hits are all comment headers; **R-LOG itself names only `SetTestResult`**. The related failure-path gap is described in C11 and carried as `RR-02` (inference only).

**Repair condition** — R3 §6 must be re-issued so it is executable inside the signed boundary: **either** (a) each raw-context/context logicalId names the concrete reachable mechanism and the exact field mapping that carries it as a **record**, **or** (b) R3 explicitly **downgrades** those rows to source-comment documentation, states that as the method's own position, and adds a failure-path rule for a no-trigger / boundary-trigger / negative-Hys segment that does not depend on an API this project does not have. Until (a) or (b) is signed, the implementation cannot be shown to conform to R3 §6.

**Routing note** — this is explicitly **not** returned to `ate-implementer`: the missing capability is a property of the platform and the signed boundary, not a defect the implementer could fix without inventing an API. **No executable line of `test.cpp` needs to change to close `RF-01`.**


**Widened-scope addendum (captain correction).** This finding's evidence was originally scoped to `test.cpp`, and that scope was withdrawn by the captain as too narrow. It has been re-based on a project-level probe: `BoardCheck.h`'s `CBC_log` (not in the `test.cpp` include closure; its only instance private at `:778`; the qualified name `CBC_log::` used 0 times tree-wide), `treg.h`'s `TREG_LOG::log_data` (a real datalog writer, but private with only `TREG`/`TRIM_NODE`/`TRIM_GRP_NODE` as friends, and reachable only through a Trim node's `execute()` — while R1 §1 declares TM108 `trim = null`), and `treg.h`'s `TREG_ERROR::treg_error_log` (public static, but a debug-console **error/fatal** channel, not a datalog record). **None is usable**, so the owner, severity and blocking status are unchanged. Mechanism-level proof and the one residual UNKNOWN (`RR-12`) are in the C11 addendum in §3.

### RF-02 · low · `ate-implementer` — an unverified framework behaviour asserted as fact

**Evidence** — `test.cpp:2178-2179` ("the closure set is released implicitly with the `cbite` scope; no relay of this item is left actuated…") and `test.cpp:2287-2289` ("…the `cbite` scope ends with the function, so no relay of this item outlives it"). The review record classifies this framework behaviour as **UNKNOWN** (t8 contract §4c, `C7`). Every *other* unproven premise in this delivery is correctly labelled PENDING or carried as an open item — this is the only place where an unevidenced premise is stated in the indicative mood.

**Violated rule** — charter §2 (evidence precedence) and §4's library-function rule (implicit side effects must trace to a registered source).

**Repair condition** — reword `test.cpp:2178-2179` and `:2287-2289` so the implicit release is presented as an assumption about the `cbite` scope still to be confirmed against the framework (naming `compile-diagnostician` as the confirming party), and make the safe-end-state sentence conditional on that confirmation. **Do not add any release call** and do not delete the P8 discussion — wording only, inside comments.

### RF-03 · low · `ate-implementer` — TM108 lost its `Step 4` heading

**Evidence** — the edit replaced `// ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======` (backup `:2185`) with `// P4 rising sweep -> P5 turn-around -> P6 falling sweep (method sec.3 P4/P5/P6)` (`test.cpp:2240`). TM108's step sequence is now Step 1 (`:2205`), 2 (`:2221`), 3 (`:2230`), **5** (`:2276`), 6 (`:2294`) — **no Step 4 anywhere** in the span. The neighbouring TMs keep the complete set (`TM107` at `:2108`, `TM109` at `:2347`). The self-check records the removal as deliberate (`t7-selfcheck.md:83-84`). Effect: TM108 alone has a numbering gap in the file's own structural convention, and the banner's P4/P5/P6 markers have no numbered anchor.

**Repair condition** — restore a `Step 4` heading for the P4/P5/P6 region (the contract phase markers may stay on the same or following lines) so the sequence is 1..6 like every sibling item. Comment-only.

### RF-04 · low · `ate-implementer` — evidence numbers in the implementation artifacts that do not reproduce

**Evidence** — four numbers a reviewer would navigate by do not land where they say:

| # | Claim | My measurement |
|---|---|---|
| 1 | `t7-selfcheck.md:131` — signature at `test.cpp:2191` | **2193** |
| 2 | `t7-selfcheck.md:129` / manifest `changes[0].changeKind` — "5625 non-comment lines" | **5628** before, **5628** after |
| 3 | `t7-selfcheck.md:132` — "95 TM symbols" | **98** (`DUT_API\s+int\s+TM\d+`) |
| 4 | manifest `sourceLocationBefore=2154` / `After=2192`; `t7-selfcheck.md:130` "lines 2149–2216" | **2155 / 2193 / 2150–2217** (a consistent off-by-one convention, undeclared and applied inconsistently — #1 is off by two) |

**No material claim is affected:** I independently reproduced the hash binding, the comment-only nature, the scope confinement and the 97-added/13-removed counts. The counts that matter are right; the counts that are wrong are the ones used for navigation.

**Repair condition** — correct those numbers (or state the line-numbering convention once in the manifest `readerDiscipline` block and apply it consistently across both artifacts) so a reviewer following the manifest arrives at the intended line.

---


## 5a. Revision drift — `RF-05`, `G-13`, `RR-14`

**What happened.** The deliverable is defined by the t8 contract §4.7 as the *hash-bound pair* (code + manifest). That pair moved under this review:

| | revision as reviewed | revision on disk at my last read |
|---|---|---|
| `test.cpp` | `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a`, 477123 B, CRLF 9434, bare LF 3, mtime `21:29:56` | `456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa`, 477760 B, CRLF 9440, bare LF 3, mtime `21:39:39` |
| `implementation-manifest.json` | `a4f5286da293f0e564849e37afce263e7bce38d08753503189a25e1bcbeba556`, 25688 B | `58c54c48d1d72177551b32463ea62133a105fad4883f838a15e669d42638778e`, 41935 B, mtime `21:41:13` |
| manifest observed during the window | — | `a4f5286d…` → `26171fca…` (36494 B) → `58c54c48…` (41935 B) |

Both revisions are preserved for audit: `review/copy/test.cpp` (as reviewed) and `review/copy/test.cpp.r2-live` (as newly observed). I wrote to neither target file; every write of this task went under `team/artifacts/tm108-v2-trial/review/`.

**Consequence.** A reviewer cannot pass a gate on an artifact that is being rewritten underneath it, and the newest manifest may itself have been superseded after my last read (`RR-14`). The newer pair *is* internally consistent — its `changes[0].afterSha256` equals the newer live file — but it is not the pair I examined.

**What I re-verified against the newer revision.**

| Finding | Status in the newer revision |
|---|---|
| `RF-02` | **REPAIRED.** The new revision marks the framework behaviour as assumed — `ASSUMED, NOT verified (compile-diagnostician's item)` (1×) and `That behaviour is ASSUMED here and NOT verified` (1×) — and **both** old assertive strings are gone (`released implicitly with the cbite scope` 0×, `the cbite scope ends with the function` 0×). Conforms to the repair condition: wording only, no release call added. |
| `RF-03` | **REPAIRED.** `Step 4: Measure (library AWG ramp, capture on the observation candidate)` is present exactly once inside TM108, with a note recording why the sibling wording was deliberately not reused. The item's step scheme is 1..6 again (94 `Step 4: Measure` headings across the file). |
| `RF-04` | **NOT VERIFIED.** It concerns numbers in `t7-selfcheck.md` and `implementation-manifest.json`, and both have been rewritten to states this review has not read. Re-check in the next pass. |
| `RF-01` | **NOT RESOLVED**, and unresolvable by a code edit by design. Re-verified on the newer revision: `SetTestResult` is still the only log-writing call anywhere in the file (188 raw / **187 in code**), `LogData` still 91 raw / **0 in code**, the TM108 span still holds exactly **3** `SetTestResult` sites, and the logPlan-deferring comment is intact (`carried by the trace comments in this function` 1×, `failureContext` 1×, `bstSwStatus` 1×, `sweepGeometry` 2×). |
| comment-only discipline | **PRESERVED** on the newer revision: non-comment line sequence still identical to the pre-change backup (5628 items each), BOM present, bare LF still 3. |

**Required action.** Freeze a single revision, land every remaining repair, and re-run `t8` against that frozen pair — with no writes to `test.cpp` or the manifest while the re-review is in flight. This review's evidence is anchored to `b79b911a…` and cannot be carried over automatically.

**Finding `RF-05` (high, blocking, owner: captain for the artifact freeze, with `ate-implementer` as the writer of both files).** Violated rule: `ROLE_ROUTING.md:32-34` (a role must validate a handoff against the declared artifacts and hashes, and a blocking verdict stops the sequence) together with t8 contract §4.7, which makes the deliverable the hash-bound pair and treats a manifest naming a different revision as blocking. Repair condition as stated in the paragraph above.

## 6. Waived findings

| id | Subject | Why waived |
|---|---|---|
| `WF-01` | No explicit release call for `{13,65}` anywhere in the project (`C7`) | Project-wide pattern: **104** `cbite.SetOn` and **0** release/reset calls in both files. R3 §5 action 6 is realised by the framework's per-item relay reset or the item boundary. The framework behaviour was not verified and is not the implementer's to invent. Carried as `G-09` / `RR-01`. |
| `WF-02` | R3 §10 `RT-1` still states a K13 divergence and cites `md :248, :574` (`C10`) | The premise is refuted and I verified it (R1 `:248`, R2 `:574`, R2 `:493`, R1 `:245`; R1 is 441 lines so `:574` is out of range). The text lives in the **upstream** contract, not the deliverable; the t8 contract forbids failing the implementation for it; and my charter forbids me from resolving or relabelling `RT-1`. Carried as `RR-10`. |
| `WF-03` | No tolerance, guard band or pass/fail criterion exists (`C6` / `RT-4`) | A spec-side gap no code change can close; the t8 contract forbids inventing one. Confirmed absent (numeric inventory of the body; `SetTestResult(site, 0, value)` with no limit argument). `RT-4` remains carried. |

---

## 7. Gate results

| id | Gate | Status | Evidence |
|---|---|---|---|
| `G-01` | Manifest hash binding | **PASS** | live file sha256 = `changes[0].afterSha256` = my own plaintext hash. Manifest not stale. |
| `G-02` | Backup byte-identity | **PASS** | `15c7d2b8…c01a`, 469714 B, BOM, CRLF 9350, bare LF 3 — matches manifest exactly. |
| `G-03` | Backup is the genuine pre-change image | **PASS** | captain's independent block (`19fe6b5c…4416`) matches backup lines **2147..2227 exactly**. |
| `G-04` | Executable content unchanged | **PASS** | non-comment sequence identical (5628 each); comment-stripped normalised text byte-identical (`0341d69a…739f`); 0 non-comment changed lines. |
| `G-05` | BOM / CRLF / bare-LF integrity | **PASS** | BOM present both sides; CRLF 9350→9434 (Δ +84 = net line change); bare LF 3 both sides. |
| `G-06` | Scope confinement | **PASS** | 3 hunks @3 / 13 raw blocks; changed range entirely inside the TM108 banner+body; TM107 and TM109 untouched. |
| `G-07` | Signature unchanged & unique | **PASS** | present exactly once at `:2193`, byte-identical to backup `:2155`; it is a non-comment line. |
| `G-08` | No BST/SW action added, 9/9 carried | **PASS** | only relay call is `:2218`; no `K47/K48/K57/K61/K76/K109/K110/K141/K142/K86/K130` in the body; no numeric relay literal; 9/9 stated at `:2185`. |
| `G-12` | Open items carried, not settled in code | **PASS** | `OI-T4-01`/`OI-T5-01` PENDING at `:2182-2184`, `:2245`, `:2250`; `RT-2`/`OI-T5-02` `:2185`; `RT-4`/`OI-T4-09` `:2190`; F1–F6 `:2191`; `OI-T4-04` `:2214`; `OI-T5-05`/`RT-3` `:2170`. |
| `G-13` | Reviewed revision == revision currently on disk | **FAIL** | Live file is `456fba2c…eaa` (477760 B) and manifest `58c54c48…78e` (41935 B); this review examined `b79b911a…d5a` (477123 B) and `a4f5286d…556` (25688 B). The reviewed pair no longer exists on disk. See `RF-05`, `RR-14`. |
| `G-11` | R3 §6 `logPlan` completeness | **FAIL** | 3 of 10 rows emitted → `RF-01`. Re-run at the widened project scope ordered by the captain: `BoardCheck.h`'s `CBC_log`, `treg.h`'s `TREG_LOG::log_data` and `treg.h`'s `TREG_ERROR::treg_error_log` were each examined and none is a usable vehicle (see the C11 addendum in §3). The gate stays **FAIL**. |
| `G-09` | P8 explicit release of the closure set (framework per-item relay reset) | **NOT VERIFIED — OUT OF SCOPE** | needs the test framework / `compile-diagnostician`; this role may not run a gate script. Routed as `RR-01`. |
| `G-10` | Compilation / build / link | **NOT VERIFIED — OUT OF SCOPE** | forbidden to this role; belongs to `compile-diagnostician`. No compilation or hardware claim is made. |

---

## 8. Residual risks

| id | Sev | Risk |
|---|---|---|
| `RR-01` | high | The framework's per-item relay reset is **UNKNOWN**. R3 §5 action 6 has no call; the code asserts the release happens with the `cbite` scope. If the framework does not reset per item, the VBAT cap gate stays closed across items. Verify via the framework / `compile-diagnostician`. |
| `RR-02` | high | **Inference:** a no-trigger segment appears to be logged as `0` (initialisers at `:2247-2248` flow to `SetTestResult` at `:2304-2306` with no guard and no failure-context record), contradicting R3 `md :486`/`:544`. `rampv_capv`'s failure semantics are undocumented (`functions-registry.md:43`), so this needs the primitive's contract or a bench observation. |
| `RR-03` | high | `OI-T4-01` / `OI-T5-01`: the observation endpoint identity is unresolved, so the trigger polarity, the validity of the 1.65 V capture level and the sufficiency of `DMUX_SEL=22` are all unproven. The code correctly never equates `DTEST0` with `nQON`, but the item's measurement premise remains unverified. |
| `RR-04` | high | `OI-T5-02` / `RT-2`: the BST/SW differential constraint is unproven in **9/9** phases. R5 itself warns its conclusion is "unproven", **not** "no risk". |
| `RR-05` | medium | Every applied number is one side of an unresolved DFT conflict: VBAT 3 V vs 4.2 V (F4), `DMUX_SEL` 22 vs 23 (F2), sweep geometry (F5), rising limit 4.4 V vs 4.15 V (F1), `V(DTEST0)` vs `Check=INT` (F3), DFT timing (F6). All carried on both sides with no averaging, as required, but the item is unvalidatable as an engineering result until they are ruled. |
| `RR-06` | medium | `OI-T5-03` (R3 `md :621`), under which the method-side numeric positions are registered, appears nowhere in the code banner or the manifest `openItems[]`. The code *does* state the provenance as method-side, so `C5` passes; recorded so the manager can decide whether the artifacts should carry the token. |
| `RR-07` | medium | `RT-3` / `OI-T5-05`: the register delta has no de-activation field, so the mux activation is never un-written. Correctly not invented; still unclosed. |
| `RR-08` | low | `RT-4` / `OI-T4-09`: no tolerance exists, so no pass/fail can be adjudicated (`WF-03`). |
| `RR-09` | low | `OI-T4-03` / `RT-5`: serial use of the shared `ACM200` object is assumed, never confirmed by a concurrency table. |
| `RR-10` | low | R3 §10 `RT-1` still carries the refuted K13 divergence and the `:574` citation. The deliverable no longer asserts it; the stale text survives only in the signed upstream contract. Not resolved, closed or relabelled by this review. |
| `RR-11` | low | The manifest/self-check line convention is off by one and applied inconsistently (`RF-04`), so navigating by those numbers lands one line early. Hash-bound facts are unaffected. |
| `RR-14` | **high** | The reviewed pair is no longer on disk and the newest manifest was **still changing** when this review ended (three distinct sizes/hashes in one window). Both revisions are preserved (`review/copy/test.cpp`, `review/copy/test.cpp.r2-live`) but neither may be assumed current. Any consumer must **re-hash `test.cpp` and the manifest before acting**, and must not treat the `RF-02`/`RF-03` repairs I observed as verified for whatever revision is current at read time. Owner: captain (freeze) + `ate-implementer`. |
| `RR-12` | medium | **UNKNOWN, stated not assumed:** `CParam`'s full public surface cannot be enumerated from this checkout. It is the only framework object a TM receives (`StsGetParam`), yet no `class CParam` declaration exists anywhere under the target root — only *uses* of it. If the external SDK header declares a text/logging method reachable from a TM, `RF-01` must be re-opened as a **code** finding against `ate-implementer`. Closing action: locate and read that header. |
| `RR-13` | low | The tree carries two **non-identical** copies of `treg.h` (`source/treg.h` `e10c2ac7…`, 51157 B vs `source/src/treg.h` `ae0d6d62…`, 47730 B) and of `treg.cpp` (`ae86d1a1…` vs `1cefbf11…`). Both `treg.h` copies declare `log_data` under `private:`, so the C11 ruling is copy-independent. No `.sln`/`.vcxproj` was opened (out of scope), so which copy is in the build is UNKNOWN. Owner: `compile-diagnostician`. |

---

## 9. Routing and next action

**No downstream handoff. `t9` / compile is held** (`ROLE_ROUTING.md:47` requires a `rule-reviewer` `pass` before `compile-diagnostician` may start).

| Returned to | Finding | Kind |
|---|---|---|
| `test-method-expert` | `RF-01` | Contract repair — re-issue R3 §6 `logPlan` and its failure-path rule |
| `ate-implementer` | `RF-02` | Comment wording only |
| `ate-implementer` | `RF-03` | Comment only (restore the `Step 4` heading) |
| `ate-implementer` | `RF-04` | Documentation only (correct numbers in `t7-selfcheck.md` and `implementation-manifest.json`) |

Carried, not returned: `OI-T4-01`, `OI-T5-01`, `OI-T5-02`/`RT-2`, `OI-T5-03`, `OI-T5-05`/`RT-3`, `RT-4`/`OI-T4-09`, `F1`–`F6`/`OI-T4-10..16` — all left exactly as open as I found them; `RR-01` (framework relay reset) → `compile-diagnostician` / test framework; `RR-10` (stale `RT-1` text inside R3) → whoever re-issues R3.

### What `t7` got right — stated explicitly, because the verdict is not a rejection

The comment-only discipline is real and independently confirmed three ways: the non-comment line sequence is **identical**, the comment-stripped normalised text is **byte-identical**, and the changed range is confined to the TM108 banner and body. The hash binding holds, the backup is provably the genuine pre-change image, the signature and file integrity are untouched, every R1 resource/relay/register value is used exactly as allocated, the full R3 P0–P8 phase order and power-down sequence are implemented faithfully including the two sub-steps of the power-down (`C4`), and the item added **no** BST/SW action, **no** relay outside `{13,65}`, **no** tolerance and **no** invented number. The two open judgments the captain flagged (`C11`, `C12`) are answered above — one against the delivery as a contract gap, one in the implementer's favour.

---

*Evidence artifacts of this review (all under `team/artifacts/tm108-v2-trial/review/`): `copy/test.cpp` (byte-identical copy), `tools/rv_*.py` (reproducible analysis), `tools/out/full_diff.txt`, `tools/out/after_span.txt`, `tools/out/before_span.txt`, `tools/out/scan.txt`, `tools/out/logging.txt`, `tools/out/diff_summary.json`.*
