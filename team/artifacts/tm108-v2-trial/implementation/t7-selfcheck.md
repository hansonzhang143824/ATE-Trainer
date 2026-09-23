# t7 self-check — TM108 implementation (ate-implementer)

- task: `t7` · run: `tm108-v2-impl` · role: **ate-implementer**
- date: 2026-09-17 · target root: `D:/PROJECT6-DALI/ForCodexDebug`
- status: **implementation done and self-checked — NOT reviewed, NOT compiled** (see §6)
- **revised by `t11` — comment/documentation only.** `t11` closed review findings `RF-02`, `RF-03` and
  `RF-04` (all `low`, owner `ate-implementer`). This file's navigational numbers were **corrected in
  place** to the measured values and the hash binding was re-published. See `t11-selfcheck.md` §4 for
  the number-reconciliation table (including the captain's criterion `E17`) and §3 for the exact code
  edits in `test.cpp`. `RF-01` (blocker, owner `test-method-expert`) was **not touched**, so the compile
  gate `t9` remains held.
- **Line convention (declared) — display lines.** Every `:NNNN` reference in this file is a 1-based
  **display line**: decode the file, split on `LF`, drop the trailing empty element. `test.cpp` contains
  **3 bare-LF terminators**, so a split on CRLF instead of LF yields numbers exactly one LOWER for every
  line after `1393`. That undeclared off-by-one is what review finding `RF-04` measured; every number
  below has been recomputed under the LF convention with python byte mode.

> **Reader discipline (HARD).** `test.cpp` / `sub.cpp` / `StdAfx.h` under the target are DLP
> transparent-encrypted. Every read, write and hash of them in this task used **python byte mode only**
> (`open(p,'rb')` / `open(p,'wb')`), with `C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`.
> No `Get-Content`, no `Select-String`, no `Get-FileHash` and no .NET file API was applied to them.
> **Every hash below is labelled `plaintext` and names its reader. No ciphertext digest is recorded.**
>
> **Trap encountered and confirmed.** A pwsh `Get-Content`/`Set-Content` text pipeline applied to a
> *workspace helper file* (not a target file) returned the `TSZ#` ciphertext header and destroyed that
> helper. That is the failure mode the contract warns about, observed first-hand. After that point all
> helper files were written and edited only through the python/agent file tools. No target file was ever
> touched by a pwsh text pipeline.

## 1. Inputs — hashes re-verified, not trusted

All hashes computed by python byte mode (**reader: python `open(p,'rb')`; kind: plaintext**).

| # | Path | sha256 (plaintext, re-verified) | Matches t7 contract |
|---|---|---|---|
| I1 | `.../strategy/tm108-resource-config-contract.md` | `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4` | ✅ |
| I2 | `.../strategy/tm108-resource-config-contract.json` | `FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9` | ✅ |
| I3 | `.../method/tm108-test-method-contract.md` | `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7` | ✅ |
| I4 | `.../method/tm108-test-method-contract.json` | `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21` | ✅ |
| I5 | `.../method/bst-sw-phase-check.md` | `FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54` | ✅ |
| I6 | `.../captain-precheck/oi-t4-01-status-addendum.md` | `626BB270BF2B803AA1E5EE1318F9DFFC36D6C12254FFA5F745133A32EA12B9BF` | ✅ |
| I7 | `.../captain-precheck/protocol-runtime-memory.md` | `28B9E154648F75B60349A9F16286D695D1C3F8E3BEE02B8DE82DEBF74837D993` | re-hash as required |
| I8a | `team/TEAM_ARCHITECTURE_V2.md` | `E03F6CF04190F7923C575F1A5D987350E7B29D478A8C84F4346BCCE91BC75551` | re-hash as required |
| I8b | `team/ROLE_ROUTING.md` | `3D1526E969F2017A76D69E40376AE394E20D822E3230667C8E91283767890961` | re-hash as required |
| I9 | `team/schemas/implementation-manifest.schema.json` | `2F5AF49431A4D958131629A47F5228DC59DCC904CFEE81691FB9BD8A4D650F6D` | re-hash as required |
| — | `.../implementation/t7-task-contract.md` | `13A155431803BFF23759476366D6F01C031E738F6E1B2DA70691CFB9A16CCC9B` | hashed for the record |

`targetRoot` is pinned by I9 (`const = D:/PROJECT6-DALI/ForCodexDebug`) and the manifest reproduces it.

## 2. Target state before the change (plaintext, python byte mode)

| File | plaintext sha256 | size | BOM | CRLF | bare LF | TM108 |
|---|---|---|---|---|---|---|
| `source/test.cpp` | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | 469714 | yes | 9350 | 3 | comment `:2149`, symbol **`:2155`** (corrected in `t11` from `:2154`) |
| `source/sub.cpp` | `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470` | 121909 | yes | 3335 | — | **0 occurrences of `TM108`** |

Both reproduce the t7 contract §2 table exactly. `sub.cpp` therefore was **not** required by I3
(no Trim framework → no `measure_xxx` binding; I3 §11 hands the implementer `test.cpp`) and was left
unmodified; a backup of it was still taken (see §4) so that its byte-identity is provable.

## 3. What was changed, and the exact commands run

Single command that produced the change (dry-run first, then with `--write`):

```
python "team/artifacts/tm108-v2-trial/implementation/_t7_edit_test.py"            # dry run -> _t7_candidate.cpp
python "team/artifacts/tm108-v2-trial/implementation/_t7_edit_test.py" --write    # in-place write of source/test.cpp
```

The generator only ever inserts/replaces **comment** lines inside the TM108 banner and the body of
`TM108_HSKP_VAC1_PRST`; it asserts (a) the verified line offsets of 25 anchor lines around the function
before doing anything, (b) that the region contains exactly one `DUT_API int TM108_HSKP_VAC1_PRST(...)`
symbol, and (c) that the whole-file sequence of non-comment lines is unchanged.

**Change class: traceability and premise hygiene in comments only.** Zero executable statements were
added, removed or re-valued (evidence in §5).

| # | Location (pre-change file → delivered file, display lines) | Change | Reason / planRef |
|---|---|---|---|
| 1 | banner `:2150` → `:2150` | "digital check carried by the DFT as V(DTEST0)" instead of asserting the pin | I3 §0/§11: `DTEST0` is never equated with `nQON`; I6 OI-T4-01 unresolved |
| 2 | banner `:2152` → `:2152` | removed `measure V(DTEST0)=nQON toggle (r 4.059 f 3.738)`: the alias and the two measured numbers have **no** basis in I1–I4 | t7 §4 (the `DTEST0 == nQON` assumption "embedded in the function's comment" must be corrected); I3 §4 (no offline threshold numbers exist) |
| 3 | inserted after `:2153` → `:2154-2191` | CONFORMANCE block: per-value contract references, plus an explicit NOT-ASSERTED list (`OI-T4-01/OI-T5-01`, `RT-2/OI-T5-02`, `RT-4/OI-T4-09`, `F1–F6/OI-T4-1x/16`), and the `RT-1` line recording that it is **refuted** (see §7.1) | I3 §6 (raw context must be visible), I3 §9/§10/§11 |
| 4 | Connect block `:2167-2170` → `:2205-2216` | closure set `{13,65}` named, default-conducting `K8/K18/K19/K64` recorded, `K21_VAC_Cap` isolation recorded, `K17_BUSL_VAC` required-closed-with-no-assigned-actuation recorded | I2 §6 G1/G3 + §6.1; I3 §3 P1 (`:199`) |
| 5 | Power On `:2174-2175` → `:2221-2225` | VBAT 3 V labelled as the DFT-intent value with `F4/OI-T4-12` recorded as open (4.2 V never averaged) | I3 §3 P2 |
| 6 | Register Config `:2179` → `:2230-2236` | `entertestmode` + the single field directive recorded as **applied** values, with the CSV counterpart (`EN_DTEST0/DTEST0_MUX = 1/23`) recorded as **not applied**; no de-activation write | I2 §7; I3 §3 P3; `OI-T5-05/RT-3` |
| 7 | Measure comment `:2185-2186` → `:2240-2249` | `Step 4` heading + P4/P5/P6 phase markers + `sweepGeometry` (200 = sample count, 20 µs ⇒ 4 ms, one source/range/level across both segments, no relay action at the turn-around). **`t11`: the `Step 4` heading at `:2240` and its 3-line wording note at `:2241-2243` were restored here — see §3.2** | I3 §3 P4/P5/P6, §4, §6; `F5/OI-T4-13`; review finding `RF-03` |
| 8 | Polarity comment `:2189` → `:2253-2256` | the misleading "nQON falls through 1.65 V (inverted)" replaced by: the recorded `triggerModeRise` is `TRIG_FALLING` = the slope of the observed node, **premise pending `OI-T4-01`** | I3 §4 (segment rise trig), I3 §6 `triggerModeRise` |
| 9 | Polarity comment `:2193` → `:2260-2263` | mirrored statement for `TRIG_RISING`, same capture level on purpose | I3 §4 (segment fall), §6 `captureLevel` |
| 10 | Hys comment `:2202` → `:2272-2274` | R-HYS wording (x1e3 applied at the assignment only, never to the Rise/Fall identity) + per-site rule | I3 §4 calculation, §6 `R-HYS` |
| 11 | Power Off `:2208` → `:2280-2284` + inserted `:2289-2295` | P7/P8 markers; hold-range-then-zero ordering; K13 still closed in P7 as the sanctioned discharge path; RELAY_OFF with the unified range pairs; the closure-release statement. **`t11`: the `:2291-2295` lines now state the framework's per-item reset as an ASSUMPTION (not verified, `compile-diagnostician` named) — see §3.1** | I3 §5 actions 1–6; `R-POFF`; review finding `RF-02` |
| 12 | LogData `:2217` → `:2300-2306` | logPlan scope: calculated quantities only, no substituted value; the remaining raw-context quantities are carried by the trace comments; `failureContext` is the station log's record | I3 §6 |
| 13 | inserted → `:2186-2189` (the `RT-1` entry; no pre-change counterpart) | the `RT-1` line corrected: `RT-1` **refuted** by re-checking R1 (keep-open list excludes `13`/`65`; every R1 mention of K13 requires closure) — see §7.1 | captain `rt-1-record-correction.md`; I2 §6.1 + `resourceSummary` |

**Every line reference in this table was re-derived in `t11` from a `difflib.SequenceMatcher` opcode map
of the pre-change file against the delivered file, and each one was then checked by printing the target
line's actual content.** The t7 figures were uniformly one line low (the CRLF/LF off-by-one described in
the header) and one of them (`:2185-2187`, now `:2186-2189`) was two lines low because it addressed a
block entry point rather than the entry's first line.

### 3.1 `t11` revision — the `RF-02` rewording (comments only)

The framework behaviour that power-down action 6 depends on — an item's relays being reset when its
`cbite` scope ends with the function — was classified **UNKNOWN** by the `t8` review (`C7`, waived
`WF-01`, residual risk `RR-01`). Two comments nevertheless stated it in the indicative mood. They were
reworded so that the release is an **assumption**, marked **not verified in this run**, with
`compile-diagnostician` named as the confirming party, and with the safe-end-state sentence made
conditional on that confirmation:

- `test.cpp:2178-2179` (banner `safety end` row) — now "…no relay of this item is left actuated and no
  source energised **ONLY IF** the `cbite` scope resets the closure — **ASSUMED, NOT verified
  (compile-diagnostician's item)**." The rewording deliberately kept the original **two-line** count so
  that the signature line would not move.
- `test.cpp:2291-2295` (P8 discussion) — now conditions the whole description on the unconfirmed reset
  and keeps the full P8 description ("every source off, no rail charged, every keep-open relay still
  un-actuated and nothing written to the DUT, but the release of the closure is itself unconfirmed…").

**No release call was added and no API call of any kind was added, removed or re-valued.** `SetOff`,
`RelayOff`, `.Off(`, `DelayOff`, `SetOffAll` and `Release` all still occur **0** times as calls in the
delivered file (the single `Release` text hit is the pre-existing file-header line 56), the item's only
relay call is still `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`, and the executable content of the file
is byte-identical to the pre-change backup. This is the **assertion** that `RF-02` scores; it is separate
from the **absence** of the release call, which was waived as `WF-01`, and the reworded text does not
contradict that waiver.

### 3.2 `t11` revision — the `RF-03` Step 4 heading (comments only)

`t7` replaced the pre-change heading
`// ====== Step 4: Measure (library AWG ramp, trigger-capture DTEST0 toggle) ======` (pre-change
`:2185`) with the `P4/P5/P6` phase marker and left **no** `Step 4` heading behind, so the delivered span
read `Step 1, 2, 3, 5, 6` while `TM107` (`:2108`) and `TM109` (`:2353`) kept `1..6`.

**What `t11` actually found when it re-measured:** one defect — a **missing heading between `Step 3`
(`:2230`) and the P4 marker**. There is **no out-of-order step heading**: the only other `Step 4` token
inside the span is the power-down sub-step reference `// Step 4-6: release the three channels…`
(`:2289`), which is not a heading, and that fully explains the captain's quick-scan token list
`Step 1,2,3,5,1,4,6`.

**Choice made, and why:** the heading is **restored** in the sibling form rather than left as a declared
deviation, because the `Step n` scheme is the file's own navigational convention for every one of its
~110 TMs and a lone gap defeats a reader walking an item by step number. The restored text is

`// ====== Step 4: Measure (library AWG ramp, capture on the observation candidate) ======`

at `test.cpp:2240`, followed by the existing `P4/P5/P6` marker line. **The wording deliberately differs
from the sibling text**, which reads `trigger-capture DTEST0 toggle`: re-using it verbatim would
re-introduce exactly the `V(DTEST0) == nQON` assertion that this change removed and that review item
`C1` verified as gone. That deviation is stated **explicitly in the code** in a 3-line note at
`:2241-2243` rather than left silent — the alternative `t11` was authorised to choose. TM108's sequence
now reads `Step 1 :2205, Step 2 :2221, Step 3 :2230, Step 4 :2240, Step 5 :2280, Step 6 :2300`.

The three stale relay comments that the old `Step 4/5/6` labels duplicated were removed in the same edit
so that no contradictory comment remains next to the new one. The `Step 5` and `Step 6` labels were
carried over onto the new headings, but the `Step 4` label was replaced by the `P4/P5/P6` phase marker
and **no `Step 4` heading was left behind** — the sequence read `1,2,3,5,6`. That was review finding
`RF-03` (low, owner `ate-implementer`), and it is **corrected in `t11`**: see §3.2 above.

### 3.3 `t7` mid-task evidence that changed a stated conclusion (withdrawn claim)

While `t7` was running, the captain published `captain-precheck/rt-1-record-correction.md` (and reframed
`implementation/captain-notes-t7.md` §2), which **refutes `RT-1`**. I re-verified the premise myself
before acting on it (python byte mode, plaintext reads of R1):

| Check | Result |
|---|---|
| `resourceSummary.keepOpenRelayNumbers` contains `13`? | **False** (16 numbers: 14,15,16,21,38,39,40,70,82,86,87,90,92,130,141,142) |
| `... contains 65`? | **False** |
| `relayGroups[G3].closureSetActuatedThisStage` | `[13, 65]` |
| R1 md length vs the cited `contract md :574` | 442 lines printed by `str.split('\n')` (441 real lines + trailing newline) → `:574` is **out of range** |

**Withdrawn:** the statement in change #3's first draft and in my first `MANIFEST` draft that the signed
strategy contract contains a K13 keep-open contradiction. **Corrected conclusion:** R1 and I3 **agree** —
`K13_VBAT_Cap` is closed from P1 through P7 and released at P8, which is exactly what the code does. The
code banner now records `RT-1` as refuted, not as carried. Evidence: `rt-1-record-correction.md` §2–§3.

## 4. Outputs, hashes, backup

**`source/test.cpp` after the change** (python byte mode, **plaintext** reader):

- sha256 `456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa` · size 477760 · lines 9443 ·
  BOM yes · CRLF 9440 · bare LF 3 (**unchanged**) — **the delivered state, `t11` revision**
- superseded revisions, kept for audit and **not** the delivered state:
  - `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a` · 477123 B · 9437 lines · CRLF 9434 —
    the `t7`-delivered state, the one reviewed by `rule-reviewer` as `t8` (byte-identical to
    `review/copy/test.cpp`)
  - `8498c304ba4752ffcc44c646bdff9649006bb0a858b25db099368bdfa4ae9871` · 477016 B — the first `t7` edit
    pass, before the `RT-1` banner correction (`DEV-5`)

**Backup of the pre-change file — byte-exact** (required by t7 §6.2), written with `open(p,'wb')`:

- `team/artifacts/tm108-v2-trial/implementation/backup/tm108-v2-impl__test.cpp.before`
  sha256 (**plaintext**) `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`, 469714 B, BOM yes, CRLF 9350
- `team/artifacts/tm108-v2-trial/implementation/backup/tm108-v2-impl__sub.cpp.before`
  sha256 (**plaintext**) `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470`, byte-identical to the live `sub.cpp`

**Recorded outputs:** `implementation-manifest.json` (schema I9), this file, and — for the `t11`
revision layer — `t11-selfcheck.md` plus the `_t11_*.py` evidence scripts listed in §8.

## 5. Self-check results (each with its reader)

| # | Check | Command (reader) | Result |
|---|---|---|---|
| 1 | pre-change hash / size / BOM / CRLF reproduce t7 §2 | python byte mode | ✅ 469714 B, 9350 CRLF, `15c7d2b8…c01a` |
| 2 | `sub.cpp` hash + `TM108` occurrence count | python byte mode | ✅ `e86d49be…1470`, 0 occurrences → not required by I3 |
| 3 | all I1–I9 hashes | python byte mode | ✅ all match (table §1) |
| 4 | post-change hash / size / BOM / CRLF preserved | python byte mode | ✅ 477760 B, 9443 lines, CRLF 9440, bare LF 3, BOM present, `456fba2c…6eaa` (`t11` revision) |
| 5 | **no executable statement changed anywhere in the file** | python non-comment-line extraction + sequence compare | ✅ **5628** non-comment lines before and after (corrected in `t11` from `5625` — `RF-04` item 2), sequences byte-identical |
| 6 | change confined to TM108 | python prefix/suffix byte compare + `difflib` opcodes | ✅ prefix byte-identical, suffix identical; every opcode inside display lines **2150–2307** of the delivered file (pre-change file **2150–2217**) — banner + `TM108_HSKP_VAC1_PRST` only (corrected in `t11` from `2149–2216` — `RF-04` item 4) |
| 7 | signature unchanged (meta-generator regex requirement) | python exact-line match | ✅ `DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)` present exactly once (`test.cpp:2193`; corrected in `t11` from `2191` — `RF-04` item 1). Unmoved by `t11`: no comment line was inserted above it |
| 8 | no other TM touched | python `DUT_API int TM\w+\(` inventory | ✅ **98** TM symbols in the file (corrected in `t11` from `95` — `RF-04` item 3; 107 `DUT_API int ` declarations exist in total, which is the figure captain criterion `E17` also measured); only TM108 lies inside the changed range |
| 9 | every relay / register / numeric literal in the changed code traceable | python body inventory | ✅ body calls: `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`; `VBAT_PD3_FXVI.Set(FV,3,FXVIe_PLUS_10V,FXVIe_PLUS_100MA,RELAY_ON)`; `delay_ms(3)`; `entertestmode()`; `I2CWriteSameData(DEV_ADDR,0x56,0x16)`; `I2CWriteSameData(DEV_ADDR,0x57,0x08)`; two `rampv_capv(...)`; the three RELAY_OFF pairs; Hys `*1e3` — each mapped in the manifest `changes[].apiMappings` / `planRefs` |
| 10 | **no numeric relay literal invented** | python body scan | ✅ the only relay call uses the pinned `StdAfx.h` macros; no bare relay number appears in the body |
| 11 | no BST/SW driving action added | python body scan for `BST`/`SW` + `SetOn`/`.Set(` | ✅ 0 actions (`OI-T5-02`/`RT-2` carried) |
| 12 | no `K57` / `K48` / `K61` / `K76` / `K109` / `K110` / `K141` / `K142` / `K86` / `K130` token introduced | python body scan | ✅ 0 occurrences; only `K13/K65` (closure), `K21` (isolation) and `K17` (contract state) are named |
| 13 | relay-macro names exist in the live header | python byte mode on `source/StdAfx.h` | ✅ `K13_VBAT_Cap`(13), `K65_nQON_PU`(65), `K21_VAC_Cap`(21), `K17_BUSL_VAC`(17) all `#define`d; NOTE `K64_HG1` is **not** a live macro (live name `K64_ACM9_HG1`) so the code correctly never actuates it |
| 14 | range/trigger/current-limit symbols used by the unchanged calls exist | python byte mode on `source/BoardCheck.h` | ✅ `ACM200_20V`, `ACM200_10V`, `ACM200_10MA`, `ACM200_100MA`, `ACM200_10UA`, `FXVIe_PLUS_10V`, `FXVIe_PLUS_100MA`, `FXVIe_PLUS_10MA`, `ACM200_RELAY_ON/OFF` all resolvable |
| 15 | `D:/PROJECT6-DALI/devel` untouched | file-level audit of this session | ✅ never read, never written |

### `t11` revision self-checks (each with its reader)

| # | Check | Reader | Result |
|---|---|---|---|
| 16 | comments-only property survives the `t11` edit | python byte mode + comment stripper, delivered **vs** pre-change backup **and vs** the `t7` revision | ✅ non-comment sequence byte-identical in both comparisons (**5628** items each); comment-stripped whitespace-normalised text byte-identical, sha256 `0341d69a…739f`, 236169 chars |
| 17 | no executable statement changed by `t11` | python `difflib.SequenceMatcher` opcode map of the delivered file against the `t7` revision | ✅ 3 changed blocks — 2 comment-line replacements (2→2 and 3→5) and 1 pure comment insertion (0→4); `added 11 / removed 5` of which all 16 lines are `//` comment lines; **0** non-comment lines touched |
| 18 | signature present exactly once, count unmoved | python exact-line match | ✅ `test.cpp:2193`, 1 occurrence, unchanged; `TM108_HSKP_VAC1_PRST` total occurrences still 1 |
| 19 | `DUT_API int` count unchanged | python regex count | ✅ 98 `DUT_API int TM<n>` / 98 `DUT_API int TM\w+(` / 107 `DUT_API int` — identical before and after `t11`, and identical to the pre-change backup |
| 20 | BOM / CRLF preserved | python byte mode | ✅ BOM present; CRLF 9434 (`t7`) → **9440** (`t11`), exactly `+6` for the 6 added comment lines; bare LF still **3** and still on the same 3 display lines |
| 21 | all hunks confined to TM108 | python prefix/suffix byte compare + opcode map | ✅ changed range `t7`-revision `2178..2289` → delivered `2178..2295`, entirely inside the TM108 banner/body; lines 1..2148 (TM107 and everything before it) byte-identical; everything after the TM108 closing brace (`:2315`, i.e. TM109's banner at `:2318`) byte-identical |
| 22 | no release call and no API call added by `t11` | python text scan | ✅ `SetOff` / `RelayOff` / `.Off(` / `DelayOff` / `SetOffAll` / `Release` still 0 occurrences as calls (the single `Release` hit is the pre-existing file-header line 56); the item's only relay call is still `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` at `:2218` |
| 23 | frozen parameters untouched | python verbatim-occurrence count inside the TM108 body | ✅ each occurs exactly once and verbatim: `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)`, `delay_ms(3)`, `VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON)`, `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)`, `I2CWriteSameData(DEV_ADDR, 0x57, 0x08)`, `0.0, 10.0, 200, 20, 1.65, TRIG_FALLING, vth_r`, `10.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f`, `hys[site] = (rise_result[site] - fall_result[site]) * 1e3` |
| 24 | pre-change audit anchor untouched | python byte-mode sha256 | ✅ `15c7d2b8…c01a`, 469714 B, BOM, CRLF 9350, bare LF 3 — byte-unchanged; the backup was opened read-only and never written by `t11` |
| 25 | hash binding restored | python byte-mode sha256 of the live file vs manifest `changes[0].afterSha256` | ✅ live = `456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa` = manifest value; the `t7` hash is retained as `intermediateStateSha256_2` |
| 26 | manifest still valid against schema `I9` | python `json.load` + required-key check | ✅ parses; `runId`, `targetRoot` (const match), `scope`, `backups`, `changes`, `selfChecks` all present; 13 self-check entries |

### Values deliberately left exactly as they were (no re-authorisation, no re-valuation)

`cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` · `delay_ms(3)` · `VBAT_PD3_FXVI.Set(FV,3,…100MA,RELAY_ON)` ·
`delay_ms(1)` · `entertestmode()` · `0x56=0x16` / `0x57=0x08` · two `rampv_capv` calls with
`ACM200_20V/ACM200_100MA` + `ACM200_10V/ACM200_10UA`, `0.0→10.0` / `10.0→0.0`, `200`, `20`, `1.65`,
`TRIG_FALLING` / `TRIG_RISING` · the three zero-and-hold calls · the three `RELAY_OFF` pairs ·
`(Rise-Fall)*1e3`. Each is traceable to I1–I4 (see the manifest) and **none** was changed.

## 6. What was NOT verified (explicit)

- **No build, no compile, no link, no preprocessor run** — out of this role's charter; the compile gate
  belongs to `compile-diagnostician`. The `exitCode 0` entries in the manifest `selfChecks[]` describe
  the python checks, **not** a build.
- **No independent review and no acceptance verdict** — `rule-reviewer` owns that; this role did not
  adjudicate its own output.
- **No hardware execution, no bench measurement, no station-log inspection** — the logPlan trace items
  are documented and traceable in the code, but whether the station log actually emits them was not
  tested (see deviation DEV-3 in the manifest).
- **Meta-generator compatibility** was checked only as an exact text match of the signature, not by
  running the generator.
- **The `I2CWriteSameData(DEV_ADDR, 0x56, 0x16)` / `0x57, 0x08` register write semantics** were verified
  only against the contract's provenance (`strategy §7` ← `reg_config/tm108.sv`); no datasheet or device
  model was read by this role.

### Added by the `t11` revision

- **No re-review of the revised revision.** `t11` closed `RF-02`, `RF-03` and `RF-04` by its own
  measurement; it did **not** adjudicate them. `rule-reviewer` owns the verdict, and `RF-01`
  (blocker, owner `test-method-expert`) is untouched, so the compile gate `t9` stays held.
- **The framework's per-item relay reset is still UNVERIFIED.** `t11` only reworded the two comments
  that asserted it; the behaviour itself was not confirmed and cannot be confirmed from this role. It
  remains residual risk `RR-01` / gate `G-09`, owned by `compile-diagnostician` / the test framework.
- **The `t7`-revision hash was not re-derived from a copy.** The `t7` state is recorded from this
  role's own earlier measurement and independently corroborated by `review/copy/test.cpp`
  (sha256 `b79b911a…d5a`, byte-identical); it was not re-read from any archive.
- **The step headings were checked as text only** — no codebase structure or documentation generator was
  run to confirm that the `Step n` convention is machine-consumed anywhere.

## 7. Carried open items — none resolved, none relabelled, no side chosen

| id | Subject | Handling in this task |
|---|---|---|
| `OI-T4-01` | `DTEST0` observation endpoint identity / carrier | **UNRESOLVED (user-frozen, I6).** Not closed, not partially closed, not relabelled, not sided. The completed code contains **no** statement equating `DTEST0` with `nQON`; the alias sentence was *removed* from the banner. |
| `OI-T5-01` | observation endpoint identity, trigger polarity, capture-level validity, `DMUX_SEL=22` sufficiency | carried; every dependent premise is labelled PENDING in the code. `DMUX_SEL=22` is implemented **as the signed contract's value** (captain-notes-t7 §3), with the contested `23` recorded as not applied. |
| `OI-T5-02` / `RT-2` | BST/SW constraint unproven in all 9 phases; K57 cap-gate state | carried; **no** BST/SW driving action and no `K57` token was added |
| `RT-1` | K13 explicit-state statement in the signed contract | **REFUTED — not carried as an open item** (§3.3). R1's keep-open list excludes `13`/`65` and every R1 mention of K13 requires closure, so R1 and I3 agree. K13 is implemented per I3 (closed at P1 … released at P8); the closure set `{13,65}` already stood in the code and was not altered. Nothing is returned to `test-strategy-architect`. |
| `RT-4` / `OI-T4-09` | missing tolerance for "rising vth 4.4 V, hys 0.35 V" | carried; **no** tolerance, limit or pass/fail criterion invented, and the function needs none (its Step 6 is pure reporting — captain-notes-t7 §1) |
| `F1`–`F6`, `OI-T4-10/11/12/13/14/16` | DFT conflicts | carried on both sides, no averaging, no selection; where a conflict governs an applied number (F2/F4/F5) the code records the applied value and the open conflict |
| `OI-T4-04` | K17 actuation form | carried; no actuation call written (manifest DEV-2) |
| `OI-T5-05` / `RT-3` | no register de-activation exists | carried; nothing is un-written at the end of the item |
| `OI-T4-03` / `RT-5` | site concurrency of the shared ACM200 object | carried; serial use assumed and documented, no scheduling rule added |

**No source table, channel, path, relay, functional relay, isolation condition, register value, ramp,
delay, sample count, range or limit was added, removed or re-valued.** The only contract-visible
divergence found (K13's double listing) is reported as `RT-1` and left open.

## 8. Declared out-of-whitelist artifacts

`t7` authorises writing `test.cpp` (and `sub.cpp` if required), `implementation-manifest.json` and
`t7-selfcheck.md`. Two further things were necessarily written:

1. `implementation/backup/tm108-v2-impl__test.cpp.before` and `...__sub.cpp.before` — the byte-exact
   pre-change backup **required by t7 §6.2**. It is kept **outside** the VS tree on purpose: a `.cpp`
   copy inside `source/` would be picked up by the build/meta tooling.

The temporary `_t7_*.py` helper generators used to inspect, edit and verify the target were **deleted**
again before that task ended, so that the only durable writes of `t7` are the four authorised paths plus
the two backups above. Every command they ran, its reader, and its observed result are recorded verbatim
in §3 and §5, and the pre/post digests plus the byte-exact backup let `rule-reviewer` reconstruct and
re-check the whole delta independently (diff the backup against the live file).

`t11` keeps its helper scripts **deliberately**, so that every number it corrected can be re-derived by
a reviewer without re-writing any tooling — they are declared here because they are durable writes
outside the two-artifact whitelist, and they live beside this file in the implementation artifact
directory:

| Path | Purpose |
|---|---|
| `_t11_analyze.py` | byte-level properties, LF-vs-CRLF line convention, bare-LF line positions, signature line, non-comment and TM-symbol counts, TM108 step headings |
| `_t11_diff.py` | `SequenceMatcher` opcode map, changed range, added/removed counts, unified hunks, comment-stripped normalised equality |
| `_t11_edit_test.py` | the `t11` edit itself, guarded by 30+ assertions on the pre-state; dry-run by default, `--write` to apply |
| `_t11_verify.py` | the full post-write verification: comments-only property vs backup **and** vs the `t7` revision, symbol counts, scope confinement, absence of any release call, frozen-parameter inventory |

Nothing else was created or modified. `D:/PROJECT6-DALI/devel` was not accessed.
