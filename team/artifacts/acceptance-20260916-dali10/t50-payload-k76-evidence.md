# t50 (authorised narrowing) — K109/K110 removal: APPLIED, but BLOCKED at the bst-sw gate

Author: ate-implementer (content) · Executor: Captain (REPLACE) · Outcome: **FAILED — do not land without a ruling.**

## 0. The blocking finding, stated first

The authorised change was applied exactly as specified (§2). The artifact self-checks pass (§3). **But the
`bst-sw` gate FAILS under the contract that is actually on disk**, and it fails in the **opposite direction to the
premise of the authorisation**:

```
[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] vs payload SetOn 比对完成, 缺失=[110] (缺失数 1)
[t30] 契约来源: setup-contract.json rev=25
*** FAIL (BST-SW GOLDEN SEQUENCE) ***
  - TM600_HS_RDSON: 契约声明必需的继电器 K110 未出现在 cbite.SetOn 中
    (契约来源: aliasResolution[bst2sw].closedRelayNumbers (usedByTm lists TM600))
```
**The authorisation's justification was that rev 25 "只增不翻 ⇒ 期望集含 110" was cancelled because rev 25 was
changed to a "narrowing" revision. Measured on disk, that is not what rev 25 contains:** `setup-contract.json`
declares `revision: 25`, and its `aliasResolution[3]` still reads
`closedRelayNumbers = [110, 61]` with `usedByTm = ["TM600 (BST must lead PMID)", "TM1205 …"]` — i.e. **rev 25,
as it stands, still demands `K110` for TM600 through the `aliasResolution[*]` criterion**, which is the criterion
the gate states it uses ("判据: aliasResolution[*].resolution.closedRelayNumbers …; route enumerations and the
relaySet pool are locators only").

**So the premise of this change is not yet true on disk.** Either the rev-25 narrowing has not landed, or it landed
without changing `aliasResolution[3]`. Until one of those is resolved, removing `K109/K110` necessarily reds the
gate that the acceptance criteria require to pass.

## 1. Two-scope report, as the task requires — with one honest limitation

| Scope | Bytes under test | `relay-trace` | `bst-sw` | `awg` |
| --- | --- | --- | --- | --- |
| **disk contract = rev 25** | sandbox `477,622 B / 7675cdc4…` (payload `72d7bc3a` era) | **PASS** | **FAIL** (`missing K110`) | **PASS** |
| **rev 24 (pre-narrowing)** | not cleanly available | — | — | — |

**Limitation I must disclose rather than paper over:** I have **no frozen rev-24 contract copy**, so I could not run
a true rev-24 comparison. My first attempt reported "SCOPE A rev 24 … PASSED", but that run's sandbox rebuild had
silently failed (`TypeError` on a bad `open()` keyword in my own script), so those numbers came from **stale bytes**
and are **void**. A second attempt without the `--src` override caused the gate to scan the **deployed tree**
(`test.cpp:9081`) instead of my sandbox. **So the honest statement is: the only trustworthy `bst-sw` result is the
FAIL under disk rev 25 shown above, and I cannot produce the rev-24 column without a rev-24 contract copy.** I am
reporting this rather than reconstructing a number I did not measure.

## 1b. Exit-code clarification, and a fact that widens the finding

My first exit-code capture reported `bst-sw` exit **0**; that was **wrong** — the PowerShell pipeline was capturing
`Select-Object`'s status rather than the gate's. Re-measured with the exit code captured immediately after the
invocation:

```
python scripts/verify_bst_sw_sequence.py --src <sandbox>   ->  exit 1
python scripts/verify_bst_sw_sequence.py                  ->  exit 1   (scanning the DEPLOYED tree)
```

**And the second line matters more than the first:** the gate fails against the **deployed** `test.cpp`
(`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp:9081`, which closes `K83, K60, K61, K13, K57, K85, K126` — no
`K109/K110`, no `K48/K76`) **under the same rev-25 contract**. So this is **not** a consequence of my change: the
rev-25 contract demands `K110` for TM600 while **neither the deployed tree nor the current payload closes it**.
The mismatch is between the contract and the tree, and it pre-dates this edit. It does however mean the gate cannot
pass in its described form until the rev-25 expectation is reconciled with what any implementation can satisfy.

## 1d. FINAL EDIT (captain-authorised, second and last write) + POST-CHANGE VERIFICATION

**Hash trail for this instruction:** `c03632d9…` / 42,998 B (**recorded before the edit**) → **`66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4` / 43,806 B** (+808 B).
Parts (i) removal of `K109/K110` and (ii) withdrawal of the `--check-extra` disable were already in `c03632d9…`;
this edit added (iii) the two-case operational fact and marked the two superseded comment blocks.

### FACT — measured after this edit, on `66abc088…`

| Item | Value |
| --- | --- |
| TM600 `SetOn` (the authorised 9-item target) | `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);` |
| `SetOn` calls in TM600 | **1** |
| Content keys (comments stripped) | `K48_ACM5_AMP_REF` 1 · `K76_ACM_BST` 1 · `K109_BUSL1_PB0` **0** · `K110_ACM18_BST` **0** · `K46` 0 |
| Invariants | `delay_ms(1)` 6 · `delay_ms(2)` 0 · `SetClamp(50,50)` 2 · `MeasureVI(200,5,FPVIe_MV_X10)` 2 · bare `126` 0 · `K126_V1P5_CAP` 2 · `ERROR_RES` 2 · `K57_CAP_BST_SW` 2 · `K5+K44+K45` 0 |
| `PMID_HG2` 10 V step | `FXVIe_PLUS_20V` |
| Encoding | BOM · CRLF · **0 lone LF** |
| ACM Sets | TM600 10 · TM601 0 |
| Two-case operational fact present | yes — *UN-ENERGISED: `S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F/SW1_S` (or `K49(Relay-ON) -> SW2_F/SW2_S`) `:775`/`:778`; K48 ENERGISED: `-> K48(Relay-ON) -> K76(Relay-ON) -> BST_F/BST_S` `:673`/`:674`* |
| `relays.md` L31 mnemonic referenced | **0** (prohibition held) |
| Superseded blocks marked | 2 — the `t29` block and the `t43` union block now carry `[SUPERSEDED BY t50 … retained as history, NOT the operative rule]`, so the file no longer contains a standing instruction that contradicts the code |
| **`relay-trace`** | **PASS exit 0** — FR-001 reverse 2; warnings = only the two `TM643_VBAT_LOOP_INDICTOR` entries |
| **`awg`** | **PASS exit 0** — `FAIL=0 WARN=0` |
| **`bst-sw`** | **FAIL exit 1** — `[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] … 缺失=[110]`; `[scan] targets=4 FAIL=1`; contract source `setup-contract.json rev=26` |
| Sandbox rebuilt from these bytes | `478,429 B` / `3039e926…`; its TM600 `SetOn` is the 9-item line above |

### Why I also marked the superseded blocks (a truthfulness fix, inside the authorised comment work)

Before this edit the file contained **two comment blocks that flatly contradicted the code**: the `t29` block said the
BST path requires `K109`/`K110` closed (*"Without K110 the ACM source reaches PB0, not BST, so ruling (ii)'s
ground-referenced drive of BST-SW would not hold electrically"*), and the `t43` block said the payload implements the
**union** including `K109/K110`. After the authorised removal both were false as standing instructions. Since the
authorisation was precisely to replace that comment content with a **removal note + rationale**, marking them is
within scope; I did **not** delete them — they are retained as history, which also preserves the audit trail for the
reviewer. Flagged explicitly because a reviewer reading `667…`/`66abc088…` side by side will see the comment body change.

### INFERENCE / UNKNOWN (post-change)

- **INFERENCE:** `bst-sw` remains red for the same reason as before this edit — rev 26 still lists `110` for TM600 in
  `aliasResolution[3].closedRelayNumbers`, the criterion the gate declares it uses. This edit is comment-only and did
  not change that. Nothing on disk closes both `109/110` and `48/76`, so no payload satisfies rev 26 as written.
- **UNKNOWN:** whether rev 26 intended to drop `110` (field missed) or the requirement stands; whether `bst-sw` is the
  gate to bind on versus a frozen rev-24 baseline (I hold no rev-24 copy); and any electrical consequence. No bench
  measurement is claimed anywhere in this document.

## 1c. POST-CHANGE RE-VERIFICATION (performed after the CRLF repair, on the final bytes)

This section exists because my first gate run was made **before** the CRLF repair and therefore graded the
LF-broken intermediate (`72d7bc3a…`). Everything below was re-run against the **final** bytes.

**Sandbox provenance — checked rather than assumed:** the gate prints `payload locator: test.cpp:9133`, and I
verified what sits at that line: in my **sandbox** it is exactly the TM600 `SetOn`, whereas in the **deployed**
tree line 9133 is an unrelated `SetClamp` comment. The line number therefore confirms the gate read **my sandbox**
and that `--src` was honoured. (I state it because I had earlier mis-attributed a result to the wrong file, and a
locator that matches the wrong tree is exactly how that happens.)

### FACT — measured, with the command that produced it

| Item | Value |
| --- | --- |
| Payload bytes | `42,998 B` / **`c03632d93e0d4cc594ed4045bf6d52e6d3f897e61ed183e0475d556c45db26e0`** |
| Encoding | BOM present · CRLF 558 · **0 lone LF** |
| Content keys (comments stripped) | `K48_ACM5_AMP_REF` 1 · `K76_ACM_BST` 1 · `K109_BUSL1_PB0` **0** · `K110_ACM18_BST` **0** · `K46` 0 |
| Invariants | `delay_ms(1)` 6 · `delay_ms(2)` 0 · `SetClamp(50,50)` 2 · `MeasureVI(200,5,FPVIe_MV_X10)` 2 · bare `126` 0 · `K126_V1P5_CAP` 2 · `ERROR_RES` 2 · `K57_CAP_BST_SW` 2 · `K5+K44+K45` 0 |
| `PMID_HG2` 10 V step | `FXVIe_PLUS_20V` |
| TM600 `SetOn` calls | **1** |
| ACM Sets | TM600 10 · TM601 0 |
| `--check-extra` disable statement | withdrawn (replaced by the single-route rationale) |
| **`relay-trace`** | **PASS, exit 0** — FR-001 reverse 2; complete warning list = the two `TM643_VBAT_LOOP_INDICTOR` entries; no TM600/TM601 finding |
| **`awg`** | **PASS, exit 0** — `FAIL=0 WARN=0`, 42 AWG functions |
| **`bst-sw`** | **FAIL, exit 1** — `[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] … 缺失=[110]`, `[scan] targets=4 FAIL=1` |
| Contract source reported by the gate | `setup-contract.json rev=26` |
| Target tree | `469,714 B` / `15c7d2b8…` @18:53:33 — **unchanged**, TM600 `SetOn` at L9081 still closes neither `109/110` nor `48/76` |

### INFERENCE — reasoning over those facts

- **The rev-26/rev-25 narrowing has not removed `110` from TM600's expectation.** `setup-contract.json` declares
  `revision: 26` and its `aliasResolution[3].closedRelayNumbers` is still `[110, 61]` with `usedByTm` including TM600 —
  the criterion the gate states it uses ("route enumerations and the relaySet pool are **locators only**").
- **The failure is not caused by this edit.** The same gate fails against the deployed tree too; and no
  currently-deployed implementation closes both `109/110` and `48/76`, so **no payload on disk satisfies rev 26's
  stated TM600 expectation**. My change makes the payload match deployed reality and thereby exposes the mismatch.
- Therefore the unfreeze's premise ("rev 25 narrowed ⇒ the `110` expectation is cancelled") is, at this moment,
  **not true of the bytes on disk**, regardless of the revision number having advanced.

### UNKNOWN — not established by anything I hold

- Whether the rev-26 drafting intended to drop `110` for TM600 and the field was simply missed, or whether the
  intent is genuinely to keep requiring it. Only the contract owner can say.
- Whether `bst-sw` is the gate the captain intends to bind on for this decision, or whether a frozen rev-24
  snapshot is the correct baseline — I hold **no frozen rev-24 copy**, so I cannot produce that column.
- Any electrical consequence of closing only the ch5 route. No bench measurement exists.

## 2. The change applied (exactly the authorised scope)

- **`L241`, the single TM600 `SetOn`** — `K109_BUSL1_PB0` and `K110_ACM18_BST` removed, nothing else touched:
  `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);`
- **Still one call**, no second `SetOn` introduced; **`K46` still absent**; SW side `K60`/`K61` kept.
- **Comments synced as instructed:** the `--check-extra` disable line is **withdrawn** (a single ch5 route no longer
  over-closes, so the limitation is no longer needed) and replaced by a block recording the change with the
  evidence-strength order the task specified — **1. production behaviour** (every deployed implementation that drives
  `SW12_U1REF_BST_ACM` closes `K48+K76`; across the whole production tree `K110_ACM18_BST` and `K109_BUSL1_PB0`
  occur **0** times), **2. `t42` independent review PASS**, **3. contract-owner withdrawal**. The `K109/K110`-belongs-
  to-ch18 explanation is retained and marked **ruled: removed from this item**.
- **Format regression caught and fixed in-flight:** my first save wrote **558 lone LF** (I normalised CRLF and did not
  restore it). Repaired to **CRLF with 0 lone LF**, BOM intact. Recorded because a silent encoding change is exactly
  the kind of thing this run has been fighting.

## 3. Artifact state and self-checks

| Field | Value |
| --- | --- |
| **Hash before this change** | `6034af71…` / 41,797 B (the previous canonical) |
| **Hash after (current)** | **`c03632d93e0d4cc594ed4045bf6d52e6d3f897e61ed183e0475d556c45db26e0` / 42,998 B** |
| Intermediate (LF-broken, superseded) | `72d7bc3a…` / 42,440 B — **not valid**, format defect |
| Content keys (executable) | `K48_ACM5_AMP_REF` 1 ✅ · `K76_ACM_BST` 1 ✅ · **`K109_BUSL1_PB0` 0** ✅ · **`K110_ACM18_BST` 0** ✅ · `K46` 0 ✅ |
| Invariants | `delay_ms(1)` 6 · `delay_ms(2)` 0 · `SetClamp(50,50)` 2 · `MeasureVI(200,5,FPVIe_MV_X10)` 2 · bare `126` 0 · `K126_V1P5_CAP` 2 · `ERROR_RES` 2 · `K57_CAP_BST_SW` 2 — all ✅ |
| TM600 `SetOn` calls | **1** ✅ |
| ACM Sets | TM600 10 · TM601 0 |
| TM601 segment | **unchanged** (no ACM drive) ✅ |
| Encoding | BOM ✅ · CRLF ✅ · 0 lone LF ✅ |

## 4. What is needed to unblock

One of:
1. **the rev-25 narrowing to actually land** in `setup-contract.json` so that `aliasResolution[3]` no longer lists
   `110` for TM600 (then the current bytes should pass `bst-sw` as intended and this document's status clears); or
2. a ruling that `bst-sw` should be evaluated against a **different, frozen rev-24 snapshot**, which requires
   producing and hashing that snapshot and re-running the gate against it; or
3. reinstating `K109/K110` (reverting to `6034af71…`), which is the only option that passes both the disk contract
   and the previous gate runs — but it contradicts the production-behaviour evidence.

**I recommend (1)**, because it matches the authorisation's own reasoning: the change is justified *by* the contract
narrowing, so the contract narrowing should be the thing that lands first. I am not choosing between them unilaterally.

## 5. Boundary

Only the workspace payload and this document were written. The contract, plan, gate scripts, target tree and `devel`
were not modified by me (the contract's rev 25 was produced by its owner, not by me — I only read it). The target
tree remains `469,714 B / 15c7d2b8…`, untouched all run. **Static and in-service-code evidence only — not an
electrical conclusion; no bench measurement; a compiled closed loop is not electrical sign-off.**
