# PTC DFT Expert — CHANGELOG

## draft (unpublished)

- Initial master assets: metadata, instructions, output contract, the TM106 golden
  case and the case index.
- Declared executionClass `input-dft`; the class name is read from the plugin's
  `expert-policy-registry.js` at evaluation time, so this profile cannot drift
  away from the enforced policy without the evaluation failing.
- TM106 asserts the structural contract, the canonical input identity and the
  read-source boundary only. Its expected DFT semantic values are marked
  `PENDING_DOMAIN_INPUT` and no evaluation may claim to have checked them.

## training round 1 (draft)

- Rule change: the TM106 case now declares an executable `verification` block
  (`python scripts/validate_dft_outputs.py --tm TM106`, exit 0, `"status": "ready"`)
  and the draft evaluation runs it. The instructions state the re-binding rule that
  the first-batch loop exposed: a review still pointing at pre-refresh hashes makes
  the whole artifact set stale.

## real business round 2026-09-27

- Added the BUSINESS_ONLY DFT contract for schematic-first `INPUT_SYNC` handoff.
- Required the actual DFT expert semantic review and `modelDispatched: true` for business completion.
- Recorded revision id `dft-business-input-sync-20260927`; smoke/framework behavior remains unchanged.

## runtime verification round 2026-09-28

- Advanced the active BUSINESS_ONLY revision to `dft-business-input-sync-20260928`.
- A fresh business run must bind the current-day profile snapshot and dispatch the DFT semantic reviewer; 2026-09-27 runs remain historical evidence only.
- Added run-local intent adjudication to the semantic-review packet. Resolved
  project conflicts, including TM109's VAC1 copy-paste note versus the VAC2
  generated recipe, are reviewed against the accepted baseline and remain
  visible as non-blocking diagnostics; unresolved or contradicted decisions
  still block the run.
