# Hash audit — acceptance-20260916-dali10

Author: ate-implementer. Purpose: this run has repeatedly circulated **stale hashes**, because
artifacts were regenerated while messages were in flight. This file records a single python
plaintext measurement of every contested artifact, taken in one pass, with the quoted value beside it.
**Recompute before citing.** Nothing here should be hand-copied onward.

> ## ⚠ STANDING WARNING — several artifacts are regenerated repeatedly in this run
> `schematic-ir.json` has been rebuilt **at least twice inside this run**: dft-expert read
> 453464 B / `9f5643d1…` when building its "v6" at ~14:10, and the live file is now
> **457531 B / `9f4a7707…f639`, mtime 14:17:50** — the intermediate revision no longer exists.
> Likewise `test-plan.json` has passed v1→v10 and `setup-contract.json` has been rebuilt repeatedly in
> the same window. **Every row below, including ones I measured, is only valid at its measurement
> instant.**

## ADDENDUM 2 — a fourth drift case, worse than the previous three (reported by dft-expert, verified by me)

The first three cases were stale hashes **inside messages**. dft-expert reported, and I verified, a case
where a **frozen artifact's body embeds an anchor to a revision that no longer exists**:
`dft-ir.json`'s `fixtureEvidence.sha256` pointed at a `schematic-ir.json` revision
(453464 B / `9f5643d1…`) that t2 has since rebuilt (live 457531 B / `9f4a7707…f639`, mtime 14:17:50).
That is why `dft-raw/dft-ir-hashes.json` records self-verification as **135/136 with one deliberate
FAIL** — the failing check is the fixture-anchor equality, left failing **on purpose** as an honest
drift signal rather than edited to pass. I confirmed the sidecar text myself ("135/136 checks passed,
issuedAt 14:29:55, artifactSha256 d8f900a4…") and that it carries a `fixtureAnchor` block with
`drift: true`, `liveAtReanchor` and `absentCounterpartsStillAbsent`. dft-expert also re-verified the
four fixture paths against the live file and found the polarity/FS-01 conclusions unchanged, so this is
a provenance defect, not a technical regression.
**Downstream action:** t7/t9 must re-run `dft-raw/scripts/dft_ir_reanchor_fixture.py` before asserting
on fixture provenance, cite its `liveAtReanchor.sha256` rather than any in-body frozen value, and state
the drift explicitly. (Script present, 5403 B.)

⚠ One claim I could **not** verify: dft-expert states it wrote the BD-05 provisional-ruling text into
the sidecar under `lateRulingsNotInIR`. That key appeared **only in the generator**
`dft-raw/scripts/dft_ir_freeze_notice.py` at the time I checked; the emitted sidecar
(`dft-raw/dft-ir-hashes.json`, then 16356 B / `446096f12f4a3745…`) carried the keys runId, task,
producedBy, generatedAt, deliverable, sourceHashes, runOutputHashes, writeBoundary,
verificationReports, fixtureAnchor — with no `lateRulingsNotInIR`, no `BD-05` and no `SetClamp`. I
reported it rather than assuming completion.

## ADDENDUM 3 — that gap is now DIAGNOSED, FIXED and VERIFIED (dft-expert's root cause)

dft-expert traced it and owned the error: the sidecar has **two writers**, and the main-chain writer
`dft_ir_hashes.py` **rebuilt the report dict from scratch**, so every later run of the main generator
**overwrote** the auxiliary blocks that `dft_ir_freeze_notice.py` / `dft_ir_reanchor_fixture.py` had
added. The sequence that produced my reading was: generate (v6) → hashes.py overwrites with base keys →
freeze_notice adds `hashHistory`/`lateRulingsNotInIR` → reanchor read-modify-writes and preserves them →
**another generate lets hashes.py overwrite again**. So the field was written and then destroyed, not
never written. In their words, they made the very mistake they had been warning others about: trusting a
writer's stdout instead of re-reading the file.

**Fix verified by me on the live file** — `dft-raw/dft-ir-hashes.json` now has **14 top-level keys** and
**all six auxiliary blocks present**: `hashHistory` (6 entries) · `provenanceCorrection` ·
`lateRulingsNotInIR` · `notRebuilt` · `fixtureAnchor` · `verificationReports`. `lateRulingsNotInIR`
now carries BD-04 ("TM108/TM109 rising threshold = OVERVIEW 4.4 V; DFT.csv 4.15 V retained verbatim as
a registered conflict") among its entries. `dft-ir.json` itself is **unchanged** at 130724 B /
`d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b`. `dft_ir_hashes.py` was changed to
read-merge-write, its stale `selfVerification: "72/72"` line removed, and `dft_ir_verify.py` gained a
regression guard asserting the six blocks and the BD-04/BD-05 contents.

*Measurement note — CORRECTED:* dft-expert's `20483 B / 4ebc1089…` is **an author's instantaneous value
read from a writer's stdout, now VOID** — not a second version that existed. Both of us re-read the file
and get **19733 B / `9ed89c1134f494ae59f0877b125effd302d21f34aa572d3249865ccd0607af6b` (mtime 15:00:46)**,
which is the only current value for this file. Do not cite the 20483 B figure anywhere.
dft-expert also notes, as a *possible and unproven* explanation for the 750 B delta, that
`runOutputHashes` grows as files are added under `dft-raw/` (25→31→33 entries), so two generations of the
same logical content differ slightly; recorded as a candidate explanation, not a conclusion.
**Caveat withdrawn:** because `dft-ir.json` is unchanged and the sidecar again anchors it
(`deliverable.sha256` == the live dft-ir hash, verified True in the same instant), the sidecar is now
consistent with its artefact and the "partially written" caveat I placed on it earlier is removed.

*Schema inconsistency for t9:* the sidecar's `deliverable.size` field is named `size`, while the build
script uses `sizeBytes` — two names for one quantity inside one artefact. **Match artefacts by `sha256`,
not by a size field name**, when reconciling.

## FOUR DISCIPLINES THIS ACCIDENT PRODUCED (adopt for the rest of the run)

1. When several writers share one sidecar, **no writer may build it from scratch** — each must
   read-modify-write and preserve unknown keys.
2. "The field is on disk" may **only** be asserted by **re-reading the file**; **another party's** stdout is not
   evidence. (This is the same class as the implementer's rule about never asserting source content from
   shell text search.)
3. After changing any writer, run an **idempotence check**: invoke the other writers afterwards and
   re-read, proving the block survives a later writer — not merely that one run produced it.
4. **Never cite your own previously printed number.** Re-read the file immediately before quoting it —
   rule 2 covers "do not trust another party's stdout", this one covers "do not trust your own stdout".
   dft-expert added this after catching themselves quoting a value they had read from a writer's output
   rather than from the file (the 20483 B figure above), which is exactly the failure rule 2 describes.

Measurement method: python `open(path,'rb')` → `hashlib.sha256` (the DLP-whitelisted path). PowerShell
`Get-FileHash` reads ciphertext for these files and is not valid.

Measured at 14:28 (approx), same pass:

| Artifact | Live size | Live sha256 (python plaintext) | Quoted value in circulation | Match |
| --- | --- | --- | --- | --- |
| `dft-ir.json` | 130724 B | `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b` | 116140 B / `82398d2f…` (dft-expert msg) | **NO** |
| `schematic-ir-sensing.json` | 47446 B | `43ad8c84ed21290efbb8a955568cab382fdaa5a766405e44bd2f337633a818f8` | 47156 B / `ad9859e9 (SUPERSEDED — this figure was already historical when first quoted; see the standing warning at the top of this file)…` (captain ×2) | **NO** |
| `test-plan.json` | 128624 B | `738998ca98414f32…` (recompute) | 121694 B / `2e93a46c…` (t10 task output) | **NO** |
| `schematic-ir.json` | 457531 B | `9f4a7707fb0a1b31f4f884dcac617c5273506de6c2a088a3b9c3f1b20683f639` | — | — |
| `setup-contract.json` | 262032 B | `7e6ca7f5baa1eecbb4c159406bae570855805ec899e02c22b73af19be691a569` | — | — |

## The one authoritative cross-check
`dft-raw/dft-ir-hashes.json` (13041 B, sha256 `0b9d29faa77e24a21f01c3be40b9bc800c621db94988ef600e3a3da3886fb91d`)
is the sidecar dft-expert built for exactly this problem, and it **agrees with my live measurement**:

```
"deliverable": {
  "path": "team/artifacts/acceptance-20260916-dali10/dft-ir.json",
  "sha256": "d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b",
  "size": 130724
}
```

So for `dft-ir.json` my value is the correct one and the quoted `82398d2f…` / 116140 B is stale — the
file was revised again after that message was written. The same mechanism explains the sensing and
plan mismatches; note `test-plan.json` has already advanced past t10's `v3` to **`v4`** (mtime
14:25:51), i.e. t11 landed during this audit.

## Recommendation

Adopt one rule for the rest of the run: **no hash is quoted from memory or from a message.** Before
citing, recompute with python and, where a sidecar exists (`dft-raw/dft-ir-hashes.json`), cross-check
against it. The line count is a stable cheap check too — `test.cpp` plaintext is 8878 lines.

## Why this matters downstream

t6 (review), t8 (gates/build) and t9 (integration, which performs the isolation audit) all assert on
artifact identity. Three artifacts currently have quoted digests that do not match disk, so any
review that trusts a quoted hash would be validating a revision that no longer exists.
