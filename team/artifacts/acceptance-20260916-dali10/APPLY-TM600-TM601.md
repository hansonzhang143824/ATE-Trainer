# How to apply the TM600/TM601 implementation — updated for the t23 payload

Author: **ate-implementer (content author)**. Executor: **the write-capable party (Captain)** — the
report and the manifest must state *"content author = ate-implementer, executor = write-capable party"*.
Run: `acceptance-20260916-dali10`. Supersedes the earlier revision of this file.

**Status: NOT APPLIED.** `D:/PROJECT6-DALI/ForCodexDebug` is outside the implementer's session workspace,
the sandbox denies the write (five probe denials), and approvals are disabled, so no source change has
been made by the author. Everything below is verified and ready for a process that can write.

## Inputs — recompute at cite time (python plaintext, byte hash)

| File | Size | sha256 |
| --- | --- | --- |
| `implementation-payload-TM600-TM601.cpp` | **38147 B** | **`272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0`** |
| `backups/test.cpp.before_TM600_TM601.bak` | 434629 B | `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` |

Payload form: **UTF-8 BOM + CRLF, 0 lone LF**. The old `…pulse2ms-variant.cpp` **no longer exists** — the
`delay_ms(1)` settle is in the delivered payload, so there is a single delivery path by design.

## Frozen upstream inputs (recompute; do not carry these forward blindly)

| Input | Frozen value |
| --- | --- |
| `setup-contract.json` | revision 22 / 329115 B / `295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c` |
| `test-plan.json` | v20 / 166099 B / `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016` |
| excerpt (binding call form) | 8423 B / `9554d4d6f4fe878d05ba65fe5a79628192445f46ff74793e22d146f0e9ef89c8` |

## Why python, and never an editor or Copy-Item

`test.cpp` is a DLP `TSZ#` container. Python is DLP-whitelisted and reads/writes plaintext; PowerShell
`Get-Content`/`Copy-Item` see ciphertext and produce empty or garbage copies, and an editor in text mode
turns CRLF into `\r\r\n`. Every hash in this document is **python plaintext**; `Get-FileHash` is invalid
for these artifacts and must never be compared against them.

> ## ⚠ THE TREE HAS ALREADY BEEN WRITTEN — COMPARE BEFORE WRITING
> A write has already occurred: `test.cpp` = **469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**
> (mtime 2026-09-16 18:53:33), and it landed the **earlier t23** revision: `TM600_HS_RDSON` at L9057 with its SetOn
> at **L9081** closing 60/61/83 and **neither K109 nor K110**, `TM601_LS_RDSON` at L9217 with its SetOn at L9255.
> So the tree contains this feature area but **carries the t29 defect** (the BST excitation path is unclosed).
> **Executor: first recompute the hash of `source/test.cpp`.** If it is `15c7d2b8…`, the region must be **REPLACED**
> with the current payload (`272667f3…`) — do not append a second copy. If it already contains `K109_BUSL1_PB0`
> and `K110_ACM18_BST`, the repair is already in place and only verification is owed. Any other hash: stop and
> re-derive, because the tree has moved again.

## Target state at preparation time

```
path   D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp
size   462848 bytes
sha   3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479
```

**Read this carefully — the target is NOT at the pre-change baseline any more.** An earlier revision
(434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`) was already appended to
the tree by the t20 write, and that deployed revision carries the *old* TM601 relay list (bare `126`, and
none of the stabiliser caps). t22 documented this as `T22-05 TRUE_RED_CURRENT_STATE`: the gates evaluated
that 18:23:31 revision, not this payload. So the executor must **replace** the TM600/TM601 region, not
append a second copy.

## Apply procedure

1. Read `src/test.cpp` as bytes and record its sha256. If it is `3dbceb49…` (462848 B), proceed with the
   **replace** path below; if it is `5c9cb3f9…` (434629 B), the t20 write never landed and you may use the
   simpler **append** path. Any other value: stop and re-derive — the tree moved.
2. Verify the backup at `backups/test.cpp.before_TM600_TM601.bak` is byte-identical to the **pre-change**
   baseline (`5c9cb3f9…`). That backup is the recoverable copy for either path.
3. **Replace path**: locate `DUT_API int TM600_HS_RDSON` and the end of `DUT_API int TM601_LS_RDSON` in the
   deployed file, excise that whole region (including its leading banner comment), and insert the payload
   body — everything from its own `DUT_API int TM600_HS_RDSON` to the end of file — with line endings
   normalised: `body.replace('\r\n','\n').replace('\r','\n').replace('\n','\r\n')`. The payload header
   comment block above the functions is documentation and may be omitted for a clean diff.
4. Re-encode as UTF-8 **with BOM**, write in **binary** mode, then re-read and verify:
   - starts with `EF BB BF`, 0 lone LF;
   - `DUT_API int TM600_HS_RDSON(short funcindex` and `DUT_API int TM601_LS_RDSON(short funcindex` each
     appear exactly once;
   - code-level invariants (comments stripped) hold: `delay_ms(1)` ×6, `delay_ms(2)` ×0,
     `SetClamp(50, 50)` ×2, `MeasureVI(200, 5, FPVIe_MV_X10)` ×2, `rampi_capv`/`rampv_capv` ×0,
     bare `126` tokens ×0, `K126_V1P5_CAP` ×2, `ERROR_RES` ×2;
   - record the **after-sha256** as the manifest's `afterSha256`.
5. Regenerate meta/conditions **with python only** — and note the landing point: these are written into
   the **DSH workspace** (`project/DALI/meta/`), *not* into the VS debug tree:
   `python scripts/gen_testitems_meta.py` then `python scripts/gen_test_conditions.py`.
6. Run the gates and report the **delta** against the baseline (KNOWN-RED vs NEW-RED) with exit code, log
   path and log hash per gate. Expect `relay-trace` warnings on `TM601_LS_RDSON` (VBUS/K5) and on the
   pre-existing `TM643`; **warnings do not fail the gate** — only the `虚构继电器名` **errors** did, and
   those are fixed by `K126_V1P5_CAP`. Do **not** close relays to silence the warnings.
7. Produce `implementation-manifest.json`: per changed file, backup path, before/after python-plaintext
   sha256, re-read verification; the frozen-input hashes; the signed authorship line; and `limitations`
   (U1–U11, BD-06, BD-07, the TM601 named exception, the `ERROR_RES` fail-closed semantics, the
   zero-margin pulse budget, and the recorded `TM643` baseline deviation).
8. Release build, reported separately from any electrical claim: **a compile closed loop is not electrical
   sign-off**, and no instrument/hardware validation is authorised for this delivery.

## Guardrails for the executor

- Write **only** `D:/PROJECT6-DALI/ForCodexDebug`; `D:/PROJECT6-DALI/devel` is read-only — never write it.
- Do not touch `TM643_VBAT_LOOP_INDICTOR`; its two warnings are a registered baseline deviation.
- Do not edit `scripts/gate_baseline.json` to mask anything; the baseline-read defect belongs to the
  harness owner.
- Keep the two `DUT_API` function bodies **verbatim** — they are the content that t24 will review.


---

## READER RULE — which relay set is the current target (added, append-only)

**Cite these values, not any shorthand.**

- **Authoritative closed set = `[48,60,61,76]`** — BST side `[48,76]` in the ACM200 family, SW side `[60,61]` in the FPVIe[L] family (**it includes `K60`**).
- **Gate expectation = `{48,60,61,76,83}`** (the union of the two aliases the gate reads: `pmid2sw {83,60,61}` and `bst2sw {48,60,61,76}`).
- **Historical shorthands are not targets.** `[48,61,76]` is the **old incomplete shorthand** — it omits the SW side's `K60`. `[110,61]` is the earlier cross-family pair, incomplete under either reading.

**Why this matters:** a stale wording that carries an in-band label is a *record* and may be kept; a stale wording **without** one reads as a *live target*. The criterion is the annotation, not the mere presence of the old string.

**Why a reader rule is needed at all:** the gate performs a **subset** check, so it cannot see either a **missing member** of the expectation set or **extra closures**. Defects of that class cannot be caught at the gate layer and must be caught in writing or review — which is what this rule does.

**Citation discipline:** cite this document and the plan/contract **by path and owner, and recompute at use time**. Do not treat any size or hash printed in it as current — a pinned measurement of a moving artefact becomes a new source of drift.

**Source:** shared practice across the review, plan and implementation sides, not attributable to a single author. **Payload note:** the frozen payload closes the ch5 set and contains no `K109`/`K110`.

**[SUPERSEDED, retained as history]** The payload-hash row earlier in this document predates the `t38` revision and is **not** current. The landing owner must refresh it at landing. This is recorded rather than deleted, so the trail shows it was once wrong and was flagged.
