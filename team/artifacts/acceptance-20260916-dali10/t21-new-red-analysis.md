# t21 (revision 2) — F1–F7 closing status and gate evidence

Author: ate-implementer (content). Executor for the target-tree write: **Captain / write-capable party**.
Run: `acceptance-20260916-dali10`. Target state (unchanged by me): `test.cpp` = 462848 B /
`3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479` (the t20 write).

Final payload: `implementation-payload-TM600-TM601.cpp` =
**31133 B / `620d99eaa87b6971cddb16a2dbb1f4af4c950f9fc0b0edcf9b266eb824b53ebf`**
(supersedes `7902f5d9…`; BOM + CRLF, 0 lone LF).

---

## F1 — the `cbit` NEW-RED was a harness false positive (corrected finding)

I had attributed `cbit` to a pre-existing header-vs-bench-baseline inconsistency. **The correction
supersedes that attribution**: the user's evidence shows `run_gates.ps1` reads
`scripts/gate_baseline.json` with `Get-Content -Raw -Encoding UTF8`, which under this run's DLP/TSZ
protection returns the **8192 B ciphertext** (first characters `%TSD-Header-###%`) instead of the 28 B
BOM-prefixed JSON `{"cbit": true}`. `ConvertFrom-Json` then throws, `$baseline` comes back empty, and
**every red gate is classified NEW-RED**. So the reported "2 NEW-RED" was inflated by a broken baseline
read, and the K168/K169/K170 set was never evidence about my change — my own reproduction did show the
error set is invariant under the payload edit, but the *classification* was the harness's fault.

**Required fix (NOT mine to make — it is `scripts/`, outside my scope):** repair the baseline read in
`run_gates.ps1` so it parses the file through the **python-authorised reader** and passes the result back,
and **never** edit `gate_baseline.json` to mask it. Flagged for the owner.

## F2 — TM601 stabiliser caps: CLOSED (was a real defect)

The FR-001 reverse rule (`verify_relay_trace.py:317-328`) requires each cap family of a statically
powered PIN to be closed unless that PIN is the measured current path or a ramp source.
`TM601_LS_RDSON` declared SW and VBUS powered and closed none of them. Closed now, each name verified
against the live header:

| Cap relay | Value | Locator |
| --- | --- | --- |
| `K44_Cap_SW2_BST2` | 44 | `StdAfx.h:205` |
| `K45_Cap_SW1_BST1` | 45 | `StdAfx.h:206` |
| `K57_CAP_BST_SW` | 57 | `StdAfx.h:220` |
| `K5_VBUS_Cap` | 5 | `StdAfx.h:161` |

`TM600_HS_RDSON` already carried `K57_CAP_BST_SW`; it needs none of the other three because its meta
does not declare the BST-SW rail as a statically powered PIN.

## F3 — bare `126`: CLOSED (was a real defect)

`StdAfx.h:299 #define K126_V1P5_CAP 126` (aliased at `:656 K_V1P5_VDRV_Cap`). The relay is **not**
fictional, but the gate matches **named** tokens against the defines table, so a bare number can never
match and was reported as `虚构继电器名 126 (无 #define)` — an **error**, which is what made the gate
exit non-zero. Both functions now use `K126_V1P5_CAP`, matching the sibling cap names in the same lists.
Bare `126` tokens in executable code: **0**.

## F4 — voltage ranges: CLOSED, applied exactly as specified

SDK ranges re-verified by reading the headers directly (`C:\AccoTEST\AccoTEST System\INCLude\`):
`FXVIe.h` → `3p6V/10V/20V/30V/40V`; `ACM200.h` → `3p6V/10V/20V/40V`; `FPVIe.h` →
`1V/2V/5V/10V/20V/40V/100V`. Corrections applied:

| Setting | Before | After | Reason |
| --- | --- | --- | --- |
| `PMID_HG2_FXVI` 15 V setpoint | `FXVIe_PLUS_10V` | **`FXVIe_PLUS_30V`** | 15 V was **over-range** on the 10 V step |
| `PMID_HG2_FXVI` 9 V setpoint (TM601) | `FXVIe_PLUS_10V` | **`FXVIe_PLUS_20V`** | 10 V fails the ≥ 2× rule for 9 V |
| `SW12_U1REF_BST_ACM` 10 V step (up **and** down staircase) | `ACM200_10V` | **`ACM200_20V`** | ladder consistency; 15/20 V already used `ACM200_40V` |

**Kept at 10 V per the spec's own instruction** — and this is the interval-closure conclusion, not a
sweep: for the **4.2 V and 5 V** setpoints the 20 V step is *not* the smallest compliant range. The rule
is `range ≥ 2 × setpoint`, so 5 V needs range ≥ 10 V and the **minimum** compliant range is exactly
`10V`; `[10,20)` is the valid interval. Moving to 20 V would enlarge the interval but no longer be the
minimum step. The same interval logic makes 9 V → 20 V correct (9 V needs ≥ 18 V, so 10 V is *invalid* and
20 V is both the minimum and the only choice up to 40 V). Zero setpoints carry no ≥ 2× requirement and
keep the smallest step.

**Low-fall steps and the off state re-checked as instructed**: the staircase now goes
`0/5/10/15/20` on ACM with `ACM200_10V → 10V → 20V → 40V → 40V`, and the falling steps reuse the same
per-value range as the rising ones (10 V → 20 V on both directions, 5 V → 10 V), so no step retains a
higher step's range in either direction. Off/teardown retains the unified `1V/10MA` (FPVIe) and
`10V/10MA` (FXVIe/ACM) as the contract's R-POFF-06 requires.

## F5 — TM601 sign and division guard: CLOSED

Both functions now read `MVRET` **signed** and fold only `MIRET`:

```c
hs_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;
```

- **Sign premise written in code**: TM601 forces the derived −1 A (PGND on the HIGH terminal), so the
  expected differential is **negative**, the expected magnitude is negative, and a **positive** reading is
  the polarity/fixture diagnostic. TM600 is the mirror case.
- **Division protection**: the guard follows existing project idiom (`test.cpp:7884`,
  `if (iforce[site] > 1e-6) acc = … / iforce`) but uses a **physically meaningful floor** rather than an
  epsilon — 0.1 A = 10 % of the 1 A nominal force — and is labelled **provisional / bench-signoff-required**.
  Below the floor the item reports 0 mΩ, so an absent-force fault is visible as a zero-current condition
  instead of a silent `inf`/`NaN`. Unguarded divides remaining in code: **0**.

## F6 — pulse margin: wording corrected, compliance is now a bring-up item

The header now states the budget is **THEORETICAL, NOT MEASURED**, that the nominal total is
**exactly** the 2 ms HARD CAP, and explicitly that *"F6 — MARGIN IS ZERO ON PAPER … the true pulse is
>= 2.000 ms and cannot be shown to satisfy the cap by calculation alone."* The payload must not be
described as "pulse-compliant, measured"; compliance is a **bring-up verification item** (scope the real
force-ON → force-OFF interval on hardware) recorded with U11. The three delays outside the window
(`delay_ms(3)` ×2, `delay_ms(5)`) remain annotated as pre-pulse power-up/register intervals.

## F7 — artefact landing: recorded

Header now states `dali_tm_meta.json` and `test_conditions.yaml` are generated into the **DSH workspace**
at `project/DALI/meta/`, **not** into the VS debug tree; they are workspace-side build/report artefacts
consumed by the gates and the manifest, not compiled, and the only VS-tree change from this task is
`source/test.cpp`.

## Gate evidence — run against the project's own gates on a workspace sandbox

Because the gates take their source from `project_config.json`, I rebuilt a sandbox copy of the target
with the **final payload body substituted for the t20-era functions** and ran the project's gates directly
against it (nothing under `ForCodexDebug` or `devel` was written):

| Gate | Result |
| --- | --- |
| `verify_relay_trace.py --meta` | **RELAY TRACE PASSED** — 99 functions, FR-001 reverse 2, only the two pre-existing `TM643_VBAT_LOOP_INDICTOR` warnings; **all four TM601 findings and both `虚构继电器名 126` errors gone** |
| `verify_awg_params.py` | **AWG PARAMS PASSED** — `FAIL=0 WARN=0` across 42 AWG functions, i.e. the F4 range changes introduce no range violation |
| `verify_bst_sw_sequence.py` | **BST-SW SEQUENCE PASSED** — `targets=4 FAIL=0`, BST ≥ SW and 0 ≤ BST−SW ≤ 5 V hold |

Sandbox copy hash for that run: 464659 B / `7d97590d048cd347ffa9505b75b470f22136e3458f0b9b17fbf96afab3acdfda`.

## Residual, and what is still owed

- **`TM643_VBAT_LOOP_INDICTOR` (2 warnings) — pre-existing, NOT mine.** It exists in
  `backups/test.cpp.before_TM600_TM601.bak`, its body is untouched, and the gate against the pre-change
  copy emits byte-identical warnings. Out of scope; needs a decision (documented deviation vs. its own
  repair task).
- **F1's `run_gates.ps1` baseline fix is owed by the harness owner** — it is in `scripts/`, outside my
  in-scope paths, and must not be masked by editing `gate_baseline.json`.
- **The delta re-run, the Release build and the final `implementation-manifest.json`** require the write
  to have landed and the workspace to be the target tree, which this session cannot do; `afterSha256`
  therefore stays `pending-write`. Nothing here claims those steps passed.
