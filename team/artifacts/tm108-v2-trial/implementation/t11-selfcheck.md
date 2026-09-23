# t11 self-check — TM108 review findings RF-02 / RF-03 / RF-04 closed by `ate-implementer`

- task: `t11` · run: `tm108-v2-impl` · role: **ate-implementer**
- date: 2026-09-17 · target root: `D:/PROJECT6-DALI/ForCodexDebug`
- supersedes, for the numbers it corrects, the corresponding rows of `t7-selfcheck.md` (which was
  **corrected in place** by this task, not superseded as a document)
- scope: comment/documentation only. **No executable statement of `test.cpp` changed.**
- status: **revised and self-checked — NOT re-reviewed, NOT compiled** (§8)
- companion: `implementation-manifest.json` (hash-bound twin; `changes[0].afterSha256` = the delivered hash)

> **Reader discipline (HARD).** `test.cpp` / `sub.cpp` / `StdAfx.h` under the target are DLP
> transparent-encrypted. Every read, write and hash of them in this task used **python byte mode only**
> (`open(p,'rb')` / `open(p,'wb')`), with
> `C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`.
> No `Get-Content`, no `Select-String`, no `Get-FileHash`, no `.NET` file API and no pwsh text pipeline
> was applied to any target file. **Every hash below is labelled `plaintext` and names its reader.**
>
> **Line convention (declared — this is the `RF-04` root cause).** Every `:NNNN` reference below is a
> 1-based **display line**: decode the file, split on `LF`, drop the trailing empty element. The file
> carries **3 bare-LF terminators** (display lines **1393**, **4639**, **4698** in the delivered
> revision; **1393**, **4555**, **4614** pre-change), so splitting on CRLF instead of LF yields numbers
> exactly **one lower** for every line after `1393`. The `t7` artifacts used the CRLF split without
> saying so, which is what made their navigational numbers not reproduce. All numbers below are
> recomputed under the LF convention by the scripts listed in §7.

---

## 1. Inputs read

| Task input | Path | Reader |
|---|---|---|
| `RF-02`/`RF-03`/`RF-04` (all owner `ate-implementer`) + waived `WF-01` | `review/t8-review-findings.md`, `review/t8-review-findings.json` | agent file read |
| the documents `RF-04`'s numbers live in | `implementation/implementation-manifest.json`, `implementation/t7-selfcheck.md` | agent file read |
| role charter | `team/TEAM_ARCHITECTURE_V2.md` §`实现专家：职业定义草案 V2` (lines 294–396) | agent file read |
| captain criterion `E17` (same inaccuracies) | `captain-precheck/commander-signoff-tm108.md:52` | agent file read |
| the changed artifact | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | **python byte mode** |
| the audit anchor | `implementation/backup/tm108-v2-impl__test.cpp.before` | **python byte mode** (read-only) |
| the `t7`-reviewed revision (corroboration) | `review/copy/test.cpp` | **python byte mode** |

`t8`'s verdict on the revision this task revised was **`needs-revision`**: one **blocker** (`RF-01`,
owner `test-method-expert`) and three **low** findings (`RF-02`, `RF-03`, `RF-04`, all owner
`ate-implementer`). Only the three low findings were in scope here.

---

## 2. The delivered state (python byte mode; kind: plaintext)

| Revision | sha256 (plaintext) | bytes | lines | BOM | CRLF | bare LF |
|---|---|---|---|---|---|---|
| **delivered (`t11`)** | `456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa` | **477760** | **9443** | yes | **9440** | 3 |
| `t7`-delivered (reviewed by `t8`) | `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a` | 477123 | 9437 | yes | 9434 | 3 |
| first `t7` pass (`DEV-5` intermediate) | `8498c304ba4752ffcc44c646bdff9649006bb0a858b25db099368bdfa4ae9871` | 477016 | — | yes | — | — |
| pre-change backup (**audit anchor**) | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | 469714 | 9353 | yes | 9350 | 3 |

- the **audit anchor is byte-unchanged**: `15c7d2b8…c01a` / 469714 B / BOM / CRLF 9350 / bare LF 3, opened
  read-only and never written by `t11`;
- the `t7` state above is byte-identical to `review/copy/test.cpp`, so the state `t8` reviewed is
  preserved for audit even though it is no longer the delivered file;
- `t11` adds exactly **+6 lines** and **+637 bytes**; CRLF `9434 → 9440` is exactly `+6`, and bare LF
  stays **3** on the same three display lines.

---

## 3. The three fixes

### 3.1 `RF-02` — an unverified framework behaviour asserted as fact (wording only)

**Reviewer's requirement.** *"Reword `test.cpp:2178-2179` and `:2287-2289` so the implicit release is
presented as an assumption about the `cbite` scope that still has to be confirmed against the framework
(naming the framework or `compile-diagnostician` as the confirming party), and so that the safe-end-state
sentence reads as conditional on that confirmation. **Do NOT add any release call** and do NOT remove the
P8 discussion — the fix is one of wording only, inside comments."*

| # | Location (delivered) | Before (t7) | After (t11) |
|---|---|---|---|
| 1 | `:2178-2179` — banner `safety end` row | "…the closure set is released implicitly with the `cbite` scope; no relay of this item is left actuated and no source is left energised" | "…no relay of this item is left actuated and no source energised **ONLY IF** the `cbite` scope resets the closure — **ASSUMED, NOT verified (`compile-diagnostician`'s item)**." |
| 2 | `:2291-2295` — P8 discussion (was `:2287-2289`, 3 lines) | "{13,65} need no explicit release call: the `cbite` scope ends with the function, so no relay of this item outlives it. P8 therefore ends with every source off…" | "{13,65} need no explicit release call **IF** the framework resets the relays of an item when its `cbite` scope ends with the function. **That behaviour is ASSUMED here and NOT verified in this run — confirming it is `compile-diagnostician`'s item.** P8 therefore ends with every source off, no rail charged, every keep-open relay still un-actuated and nothing written to the DUT, **but the release of the closure is itself unconfirmed until that reset is confirmed**." |

Design choices, stated so the next reviewer can check them:

- **The banner rewrite was deliberately kept to its original two lines** so that the **signature line
  would not move**. Check 7 of `t7-selfcheck.md` points at the signature, and keeping `:2193` stable
  means the `RF-04` item 1 correction is a pure number fix with no knock-on. The P8 rewrite genuinely
  needed two extra lines; those shift only lines **below** the signature.
- **No release call, and no API call of any kind, was added.** Measured on the delivered file:
  `SetOff` / `RelayOff` / `.Off(` / `DelayOff` / `SetOffAll` / `Release` all occur **0** times as calls
  (the single `Release` text hit is the pre-existing file-header line 56), and the item's only relay call
  is still `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` at `:2218`.
- **The P8 discussion was not removed** — it is now longer, and every clause it carried is still there.
- **`WF-01` is not contradicted.** `WF-01` waived the *absence* of the release call (the project-wide
  pattern: 104 `cbite.SetOn` text occurrences and 0 release calls). `RF-02` scores the *assertion* about
  why the absence is safe. The delivered text now states that assertion as an assumption, which is
  strictly consistent with the waiver.
- A measurement worth recording, because it corrects a detail in the review: the review's `WF-01` says
  "104 `cbite.SetOn` in **both** files". Measured: **104** in the delivered file but **103** in the
  pre-change backup — the one extra occurrence is a **comment** mention added by `t7` at `:2162`
  (`//   relays     : P1 closure set {13,65} (cbite.SetOn, …)`). The code-side count is 103 in both,
  which the byte-identical non-comment sequence proves. **Nothing turns on this** — the "0 release
  calls" conclusion is unaffected — and it is recorded only so the count is not re-litigated.

### 3.2 `RF-03` — TM108 lost its `Step 4` heading (comment only)

**What I actually found, having re-measured before editing** (the task told me to verify rather than
assume, because the captain's quick scan had reported the tokens `Step 1,2,3,5,1,4,6`):

- the defect is **one missing heading**, not an out-of-order label. The delivered sequence was
  `Step 1 :2205`, `Step 2 :2221`, `Step 3 :2230`, **nothing**, `Step 5 :2276`, `Step 6 :2294`;
- the pre-change heading `// ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======`
  (pre-change `:2185`) had been replaced by the `P4/P5/P6` marker line, leaving no `Step 4` at all;
- the other `Step 4` token the quick scan found is `// Step 4-6: release the three channels…` — a
  **power-down sub-step reference**, not a heading. With that accounted for, the token list
  `1,2,3,5,1,4,6` is fully explained and there is **no ordering fault** anywhere in the span.

**Choice made: restore the heading, in the sibling form but not the sibling wording.** The `Step n`
scheme is the file's own navigational convention for every one of its ~110 TMs, so leaving one item with
a gap defeats a reader walking an item by step number; `t11` was authorised to choose between restoring
it and declaring the deviation, and it does **both**:

```
:2240     // ====== Step 4: Measure (library AWG ramp, capture on the observation candidate) ======
:2241     // Heading note: the sibling items' Step 4 line reads "trigger-capture DTEST0 toggle". That
:2242     // wording is deliberately NOT reused here, because TM108 does not equate V(DTEST0) with the
:2243     // observation candidate (OI-T4-01 open, RA-5 CANDIDATE ONLY). The step scheme stays 1..6.
```

The existing `// P4 rising sweep -> P5 turn-around -> P6 falling sweep (method sec.3 P4/P5/P6)` marker
line stays immediately after the note (now at `:2244`).

**Why the wording differs from the siblings, and why that is the safer text:** the sibling line reads
`trigger-capture DTEST0 toggle`. Re-using it verbatim would re-introduce precisely the
`V(DTEST0) == nQON` assertion that the `t7` change removed and that review item `C1` verified as gone
("the DFT check pin `V(DTEST0)` is **NOT equated** with the `nQON` candidate"). Copying the convention
must not resurrect a retracted claim, so the heading names the observation candidate instead and the
reason for the deviation is recorded **in the code** rather than left silent.

Delivered sequence: `Step 1 :2205`, `Step 2 :2221`, `Step 3 :2230`, **`Step 4 :2240`**, `Step 5 :2280`,
`Step 6 :2300`.

### 3.3 `RF-04` — evidenced numbers that did not reproduce (documentation only)

**Reviewer's requirement.** *"Correct the four numbers in `t7-selfcheck.md:129, :130, :131, :132` and the
two `sourceLocation` values in `implementation-manifest.json` `targetSymbols[0]` (or state explicitly
which line-numbering convention is in use and apply it consistently across both artifacts), so that a
reviewer following the manifest arrives at the intended line and can reproduce the stated counts."*

Both branches were taken: every number was **recomputed from scratch with python byte mode** (the
reviewer's and the captain's values were treated as claims to check, not as results to copy), **and** the
convention is now declared once in `manifest.readerDiscipline.lineNumbering` and at the head of
`t7-selfcheck.md`. See §4 for the reconciliation table.

---

## 4. Number reconciliation — `RF-04` and captain criterion `E17`

Every value below was recomputed by `_t11_analyze.py` / `_t11_diff.py` / `_t11_verify.py` (python byte
mode, LF convention). `t7`'s value, `t8`'s measured value and my own measured value are shown separately;
where they differ the reason is given.

| # | Claim in the `t7` artifacts | `t8` measured | **My measurement (delivered)** | Verdict |
|---|---|---|---|---|
| 1 | `t7-selfcheck.md` check 7: signature at `test.cpp:2191` | 2193 | **2193** | `t7` was **2 low**. Corrected to 2193 in both `t7-selfcheck.md` and manifest `selfChecks` |
| 2 | `t7-selfcheck.md` check 5 + manifest `changeKind`: "5625 non-comment lines" | 5628 before / 5628 after | **5628 before / 5628 after** | `t7` was 3 low. Corrected in both |
| 3 | `t7-selfcheck.md` check 8: "95 TM symbols in the file" | 98 (`DUT_API\s+int\s+TM\d+`) | **98** (`DUT_API\s+int\s+TM\d+` = 98; `DUT_API\s+int\s+TM\w+\s*\(` = 98; `DUT_API\s+int\s+\w+` = **107**) | `t7` was 3 low. Corrected to 98; the 107 total is also recorded, matching `E17` |
| 4a | manifest `targetSymbols[0].sourceLocationBefore` = `2154` | 2155 | **2155** | `t7` was 1 low. Corrected |
| 4b | manifest `targetSymbols[0].sourceLocationAfter` = `2192` | 2193 | **2193** | `t7` was 1 low. Corrected |
| 4c | `t7-selfcheck.md` check 6 + manifest `changedLineRangeBefore`: "2149–2216" | after-side 2150–2301, before-side 2150–2217 | **before-side 2150–2217; delivered (after `t11`) 2150–2307** | `t7` was 1 low on both ends. Corrected; the delivered end moved from 2301 to **2307** because `t11` itself adds 6 comment lines |
| 4d | manifest `enclosingBlock`: banner `2148..2152`, body `2154..2224` | banner 2149..2154 / body 2155..2225 (pre-change) | **pre-change: banner 2149–2154, body 2155–2225; delivered: banner 2149–2192, body 2193–2315** | `t7` was 1 low throughout. Corrected |
| 5 | manifest `changeKind` "comments only" (the material claim) | reproduced | **reproduced** — see §5 | `t7`'s conclusion was **right** |
| 6 | added / removed line counts (97 / 13 per the review) | 97 / 13 | **103 / 13** cumulative against the backup (97/13 for the `t7` step alone) | not stated numerically in `t7`'s artifacts; now recorded explicitly in the manifest |

Additional navigational references that `RF-04` did not name but which were measurably off in the same
way — **all re-derived in `t11` from a `SequenceMatcher` opcode map and each one verified by printing
the target line's content** (`_t11_analyze.py` companion dump):

| `t7-selfcheck.md` §3 row | `t7` reference | **Corrected reference (pre-change → delivered)** |
|---|---|---|
| 1 | banner `:2149` → `:2149` | `:2150` → `:2150` |
| 2 | banner `:2151` → `:2151` | `:2152` → `:2152` |
| 3 | banner `:2153..` inserted | inserted after `:2153` → `:2154-2191` |
| 4 | Connect block `:2167-2169` → `:2204-2215` | `:2167-2170` → `:2205-2216` |
| 5 | Power On `:2174` → `:2221-2225` | `:2174-2175` → `:2221-2225` (after-side was already right) |
| 6 | Register Config `:2178` → `:2229-2236` | `:2179` → `:2230-2236` |
| 7 | Measure comment `:2184-2185` → `:2239-2244` | `:2185-2186` → `:2240-2249` |
| 8 | Polarity comment `:2188` → `:2248-2251` | `:2189` → `:2253-2256` |
| 9 | Polarity comment `:2192` → `:2255-2258` | `:2193` → `:2260-2263` |
| 10 | Hys comment `:2201` → `:2267-2269` | `:2202` → `:2272-2274` |
| 11 | Power Off `:2207` → `:2275-2279` + inserted `:2284-2288` | `:2208` → `:2280-2284` + inserted `:2289-2295` |
| 12 | LogData `:2216` → `:2293-2299` | `:2217` → `:2300-2306` |
| 13 | banner `:2185-2187` → `:2185-2188` | inserted → `:2186-2189` (the `RT-1` entry had no pre-change counterpart; the `t7` reference pointed at the entry's neighbouring line) |
| §2 table | pre-change `symbol :2154` | `:2155` |

**Reconciliation with `E17`.** The captain's criterion `E17` recorded the same four inaccuracies and
routed them to `ate-implementer` as documentation-only "if the verdict is otherwise `pass`". Its numbers
(signature 2193; after-side range 2150–2301 with before-side 2150–2217; 98 `DUT_API int TM\w+(` vs the
quoted 95; 107 `DUT_API int ` in total) **all reproduce exactly** under the declared LF convention, and
its one "2 LOW-SEVERITY INACCURACIES" reading is confirmed — with the qualification that the non-comment
count `5625 → 5628` is a third inaccuracy of the same class. The single value by which my measurement
differs from `E17` is the **after-side changed range**, and the difference is **not a disagreement**:
`E17` measured the `t7` revision (2150–**2301**), whereas the delivered `t11` revision ends at **2307**
because `t11` adds 6 comment lines of its own. Both values are now recorded in the manifest.

---

## 5. Self-check — property-by-property, reader named

| # | Property | Reader | Result |
|---|---|---|---|
| 1 | **comments-only preserved** — non-comment line sequence byte-identical before/after | python byte mode + comment stripper, delivered **vs** pre-change backup, and delivered **vs** the `t7` revision (`review/copy/test.cpp`) | ✅ **5628** non-comment lines in all three states, sequence equal in both comparisons |
| 2 | stronger form: whole-comment-stripped, whitespace-normalised text | python string-literal-aware comment stripper | ✅ byte-identical, both `0341d69a9b23ffb62bff99e0c777392a609bef1a2316ce66664e460714cb739f`, 236169 chars — the same digest `t8` measured |
| 3 | **no executable statement changed by `t11`** | python `SequenceMatcher` opcode map, delivered vs `t7` revision | ✅ **3** changed blocks: 2 comment-line replacements (2→2 and 3→5) and 1 pure comment insertion (0→4); 16 lines involved, **all** `//` comments; **0** non-comment lines touched |
| 4 | signature present exactly once, unmoved | python exact-line match (byte mode) | ✅ `test.cpp:2193`, exactly 1 occurrence, byte-identical to the pre-change `:2155` line |
| 5 | `DUT_API int` count unchanged | python regex count (byte mode) | ✅ 98 / 98 / 107 — identical before and after `t11` and identical to the backup |
| 6 | BOM / CRLF preserved | python byte mode byte inspection | ✅ BOM present; CRLF `9434 → 9440` = exactly `+6`; bare LF **3** on the same three display lines; no bare-LF set changed |
| 7 | all hunks confined to TM108 | python prefix/suffix byte equality + opcode map | ✅ changed range `t7`-rev `2178..2289` → delivered `2178..2295`; prefix lines 1–2148 (TM107's `Step 4` at `:2108` and everything before) byte-identical; suffix after the TM108 closing brace (`:2315`; TM109 banner at `:2318`, its `Step 4` at `:2353`) byte-identical |
| 8 | hash binding restored | python byte-mode sha256 of the live file vs manifest `changes[0].afterSha256` | ✅ live = `456fba2c…6eaa` = manifest value; the `t7` hash retained as `intermediateStateSha256_2`, the first `t7` pass as `intermediateStateSha256` |
| 9 | manifest still valid | python `json.load` + required keys + `targetRoot` const | ✅ parses; all six required keys present; `targetRoot` matches the schema const; 13 self-check entries; 7 deviations; 15 open items |
| 10 | **no release call and no API call added** | python text scan (byte mode) | ✅ `SetOff` / `RelayOff` / `.Off(` / `DelayOff` / `SetOffAll` / `Release` = **0** as calls; the item's only relay call is still `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` at `:2218` |
| 11 | **no electrical value touched** | python verbatim-occurrence count inside the TM108 body | ✅ each occurs exactly once and verbatim: `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`; `delay_ms(3)`; `VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON)`; `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)`; `I2CWriteSameData(DEV_ADDR, 0x57, 0x08)`; `0.0, 10.0, 200, 20, 1.65, TRIG_FALLING, vth_r`; `10.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f`; `hys[site] = (rise_result[site] - fall_result[site]) * 1e3` |
| 12 | TM108 step sequence is `1..6` | python regex over the delivered span | ✅ `2205 / 2221 / 2230 / 2240 / 2280 / 2300` |
| 13 | pre-change audit anchor untouched | python byte-mode sha256 (read-only) | ✅ `15c7d2b8…c01a`, 469714 B, BOM, CRLF 9350, bare LF 3 |
| 14 | `D:/PROJECT6-DALI/devel` untouched | session file audit | ✅ never read, never written |
| 15 | write-readback integrity | python byte mode, post-write re-read compared to the validated in-memory image | ✅ byte-for-byte equal |

---

## 6. Files written by `t11`

| Path | Kind |
|---|---|
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | the target — **comments only**, 3 comment blocks, +6 lines |
| `implementation/implementation-manifest.json` | documentation: corrected numbers, declared line convention, revision trail, 4 new `selfChecks`, `DEV-6`/`DEV-7`, `reviewFindingsAddressedByT11[]`, re-published hash binding |
| `implementation/t7-selfcheck.md` | documentation: corrected in place (checks 5–8, §2, §3 table + `§3.1`/`§3.2`, §4, §6, §8) + a `t11` self-check table. **I chose to correct `t7-selfcheck.md` in place rather than supersede it**, because the point of `RF-04` is that *the document a reviewer navigates by* must land on the right line; leaving the wrong numbers in the document a reviewer opens would have re-created the finding. This file (`t11-selfcheck.md`) records the revision layer so the correction is auditable. |
| `implementation/_t11_analyze.py`, `_t11_diff.py`, `_t11_edit_test.py`, `_t11_verify.py` | helper scripts, **kept deliberately** so every corrected number can be re-derived |

**Not written / not touched:** `implementation/backup/*` (audit anchor, byte-unchanged), `review/**`,
`strategy/**`, `method/**`, `sub.cpp`, any other TM in `test.cpp`, anything under `D:/PROJECT6-DALI/devel`.
`test.cpp` was opened for write exactly once, by `_t11_edit_test.py --write`.

---

## 7. Re-deriving every number from scratch

```
PY="C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe"
IMP="team/artifacts/tm108-v2-trial/implementation"
& $PY "$IMP/_t11_analyze.py"     # properties, line convention, signature, counts, step headings
& $PY "$IMP/_t11_diff.py"        # opcode map, changed range, hunks, comment-stripped equality
& $PY "$IMP/_t11_edit_test.py"   # dry run: re-validates the pre-state guards and prints the new state
& $PY "$IMP/_t11_verify.py"      # full post-write verification against backup and the t7 revision
```

`_t11_edit_test.py` is **self-guarding**: it refuses to edit unless the live file still hashes to the
`t7` revision `b79b911a…d5a` at 477123 B / 9437 lines / CRLF 9434 / bare LF 3, and unless each target
line still contains the exact text it is about to replace. Running it now (without `--write`) reports a
sha256 mismatch and aborts — that is the intended behaviour for a revision that has already been applied.

---

## 8. What was NOT verified (explicit)

- **No build, no compile, no link, no preprocessor run.** Out of this role's charter; that gate belongs
  to `compile-diagnostician`. No `exitCode 0` recorded anywhere in this task refers to a build.
- **No independent review and no verdict.** `t11` closed `RF-02`, `RF-03` and `RF-04` by its own
  measurement and does **not** adjudicate them. `rule-reviewer` owns the verdict on this revision.
- **No hardware execution, no bench measurement, no station-log inspection.** Whether the station log
  actually emits the `logPlan` trace quantities was not tested by this role.
- **`RF-01` was not addressed and remains the single blocking finding.** It is a
  contract-vs-capability finding owned by `test-method-expert` (working in parallel under `t10`); the
  `t8` routing note states that "no executable line of `test.cpp` needs to change to close `RF-01`", and
  `t11` added no logging call, no API call and no placeholder value. **The compile gate `t9` therefore
  stays held** until `rule-reviewer` puts a `pass` on the record.
- **The framework's per-item relay reset is still UNVERIFIED.** `t11` reworded the two comments that
  asserted it; it did not confirm the behaviour, and cannot from this role. Residual risk `RR-01` /
  gate `G-09`, owned by `compile-diagnostician` / the test framework. `WF-01` is untouched.
- **The `t7`-revision hash was not re-read from an archive.** It is recorded from this role's own earlier
  measurement and corroborated by `review/copy/test.cpp`; no other copy was located or inspected.
- **The `Step n` convention was checked as text only** — no codebase structure or documentation
  generator was run to confirm that any tooling consumes it.
- **No open item was closed, relabelled or sided.** `OI-T4-01`, `OI-T5-01`, `OI-T5-02`/`RT-2`,
  `OI-T5-03`, `OI-T5-05`/`RT-3`, `RT-1`, `RT-4`/`OI-T4-09`, `F1`–`F6`/`OI-T4-10..16`, `OI-T4-04`,
  `OI-T4-16` all remain exactly as open as this role received them.
