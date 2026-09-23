# t23 amendment — sign, fail-closed, range: evidence pack

Author: ate-implementer (content) · Executor: Captain (write-capable). `sourceTaskId=t23`.
Payload after this amendment: `implementation-payload-TM600-TM601.cpp` =
**34788 B / `f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509`** (BOM + CRLF, 0 lone LF).

## Locator verification requested by the user (both verified, with one path correction)

| Claim | Verified? | Exact finding |
| --- | --- | --- |
| `source/Test_Method.h:32` defines `ERROR_RES 9999` | **Yes, path corrected** | The live file is **`Library-Functions/Test_Method/Test_Method.h:32`** — `#define ERROR_RES 9999` (revision note at `:18` "Reset ERROR_RES to 9999"). A copy also exists in the VS debug tree at `ForCodexDebug/source/Test_Method.h:32`, and `ERROR_RES` is **already used by the target**: `test.cpp:7059` (`if (ls_zcd[site] != ERROR_RES)`) and `test.cpp:8090`. So it is reachable in the debug build without adding any include. |
| precedent `debug/source/test.cpp:8087-8090` | **Yes, line-exact** | In this workspace the file is `D:/Newtest/DSH/ATE-Coding-Plat/source/test.cpp` (the project's own copy; `debug/source/test.cpp` resolves to the same content). Lines 8087-8090 read `if (im3[site] - im1[site] > 1e-6) gain[site] = (vcs3[site] - vcs1[site]) / (im3[site] - im1[site]) * 1e3;  // mohm  else  gain[site] = ERROR_RES;`. The **same two lines appear in the target at 8087-8090**, so the precedent is live code, not just a library convention. |

## Requirement 1 + 2 — positive magnitude, same-sign criterion, polarity as failure

Both functions now read **both** results signed and then require the same sign:

```c
if (i_meas[site] > 0.1 && v_meas[site] * i_meas[site] > 0.0)
    hs_rdson[site] = fabs(v_meas[site]) / fabs(i_meas[site]) * 1e3;   // positive magnitude, mohm
else
    hs_rdson[site] = ERROR_RES;   // absent current, or MVRET/MIRET sign mismatch
```

- **No code path can emit a negative resistance**: the value reported on the success path is an
  absolute value divided by an absolute value, and the failure path reports `ERROR_RES`.
- **The negative-as-"expected magnitude" framing is gone.** It was wrong on two counts — it inverted the
  reported sign, and it excused a polarity fault. TM600 is documented as +1 A → both readings positive;
  TM601's derived −1 A means both readings negative, so **the ratio is still positive** and a positive
  `MVRET` with a negative `MIRET` is now the **polarity/fixture failure**.
- Sign judgement uses the product test `v*i > 0` rather than `v/i > 0`, which is exactly equivalent for
  the same-sign case and does not itself divide.

## Requirement 3 — fail-CLOSED, no self-invented zero

`|I| ≤ 0.1 A` and the sign-mismatch case both now report **`ERROR_RES` (9999)**, matching
`test.cpp:8087-8090`. Nothing in the payload reports `0.0` on a failure path; the previous
`(i_meas > 0.1) ? … : 0.0` silently presented an open circuit as a sub-milliohm pass and has been removed
along with its two orphaned copies. On requirement 2's "走失败码上报": both the zero-current and the
polarity fault are reported through `ERROR_RES`. If the reviewer wants a **distinct** code for polarity
(so the two faults are distinguishable in the log), say so — the project idiom offers one code, and
inventing a second would be the kind of "自创" value the instruction forbids, so I did not.

## Requirement 4 — cleanup is never skipped (path enumeration)

Enumerated over executable code: **2 `return` statements in total** (`return 0;`), and **zero**
`goto` / `break` / `continue` / `throw`. Both returns are the final statement of their function, after
the whole teardown:

```
TM600: ... FPVI1 RELAY_OFF (ch1 first) -> FPVI0 RELAY_OFF (measurement channel LAST, R-POFF-04) -> LogData -> return 0;
TM601: ... SW12/U1REF RELAY_OFF -> FPVI0 RELAY_OFF (LAST)                                            -> LogData -> return 0;
```

The measurement block itself contains **no early return** — a failed site writes `ERROR_RES` into the
result array and falls through, so the power-off, relay-default and R-POFF ordering still run for every
site. Failure therefore cannot leave the DUT energised.

## Requirement 6 — complete `Set(FV, v, range)` pairing table (range ≥ 2× v; 0 V exempt)

| Instrument | v | range | Check |
| --- | --- | --- | --- |
| `VBAT_PD3_FXVI` | 4.2 V | `FXVIe_PLUS_10V` | 10 ≥ 8.4 OK |
| `V1P5_U34PS_FXVI` | 5 V | `FXVIe_PLUS_10V` | 10 ≥ 10 OK (minimum compliant step) |
| `SW12_U1REF_BST_ACM` | 5 V | `ACM200_10V` | 10 ≥ 10 OK |
| `SW12_U1REF_BST_ACM` | 10 V | `ACM200_20V` | 20 ≥ 20 OK |
| **`PMID_HG2_FXVI`** | **10 V** | **`FXVIe_PLUS_20V`** | **20 ≥ 20 OK — was `FXVIe_PLUS_10V` = 1×, the violation you found (both the rising L227 and falling L286 steps)** |
| `SW12_U1REF_BST_ACM` | 15 V | `ACM200_40V` | 40 ≥ 30 OK |
| `PMID_HG2_FXVI` | 15 V | `FXVIe_PLUS_30V` | 30 ≥ 30 OK |
| `SW12_U1REF_BST_ACM` | 20 V | `ACM200_40V` | 40 ≥ 40 OK |
| `PMID_HG2_FXVI` | 9 V | `FXVIe_PLUS_20V` | 20 ≥ 18 OK |
| all `v = 0` initialisations and teardown | 0 V | smallest step | not constrained |

**Violations: 0.** The falling staircase reuses each value's own range, so no step keeps a higher step's
range in either direction.

## Requirement 7 — invariants preserved (verified after every edit)

`delay_ms(1)` ×6 · `delay_ms(2)` ×0 · `SetClamp(50, 50)` ×2 · `MeasureVI(200, 5, FPVIe_MV_X10)` ×2 ·
ramp family 0 · bare `126` 0 · `K126_V1P5_CAP` in place · `ERROR_RES` ×2 · BOM present, CRLF, **0 lone LF**.

## Requirement 8 — gates re-run (workspace sandbox; target tree untouched)

| Gate | Result |
| --- | --- |
| `verify_relay_trace.py --meta` | **RELAY TRACE PASSED** — and now only **three** warnings: the two pre-existing `TM643` ones plus **one** for `TM601_LS_RDSON` (VBUS/K5). The **SW-family warnings are gone** because `RELAY TRACE` counts `FR-001 反向` only for genuinely required caps (3, down from 5) |
| `verify_awg_params.py` | **AWG PARAMS PASSED**, `FAIL=0 WARN=0` over 42 AWG functions |
| `verify_bst_sw_sequence.py` | **BST-SW SEQUENCE PASSED**, `targets=4 FAIL=0` |

Sandbox copy for this run: 468124 B / `ee99431ef3621fa00dd6163e889c710bc1e9cdd0677a075651a5ebf74dac4c53`.

## Two additional defects I found while making these fixes (reported, not hidden)

1. **The `-1 A`-in-TM600 comment was worse than a stray phrase**: the block was also **missing its
   indentation on the first line**, so the previous edit had left a malformed comment. Rewritten as a
   TM600-only statement; the TM601 sign discussion now exists only inside TM601.
2. **The negative-list bullet in the header was dangling** — `"...must NOT appear in the"` was followed by
   an orphaned fragment `"and the two PC-route relays) do NOT appear in either function's relay set."`
   left over from an earlier rewording. Repaired into a complete statement.

Both were silent text corruption from scripted edits. They were caught by reading the file back, and they
are the reason I re-derived every invariant above rather than trusting the earlier measurements.

## Scope discipline

`TM643` untouched (recorded baseline deviation). `devel` never written. Target tree remains byte-identical
to the t20 after-state: `test.cpp` = 462848 B / `3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479`.
F2 (the four caps) remains subject to t22's ruling; K57 is the only closure still in question.
