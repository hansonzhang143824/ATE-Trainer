# PTC Schematic Expert — CHANGELOG

## draft (unpublished)

- Initial master assets: metadata, instructions, output contract, the TM106
  golden case and the case index.
- Declared executionClass `input-schematic`. Its runtime label is TM-less
  (`PTC schematic expert`) because one schematic product serves the whole batch;
  the label shape is read from the plugin's `expert-policy-registry.js` at
  dispatch time, so it cannot drift away from the boundary recogniser.
- The case asserts the canonical input identity, the required output set, and an
  explicit `forbiddenInputs` entry for `project/DALI/schematic-ir.json`. Its
  expected schematic semantics are marked `PENDING_DOMAIN_INPUT`.

## training round 1 (draft)

- Rule change: the TM106 case now declares an executable `verification` block
  (`python scripts/validate_schematic_outputs.py`, exit 0, `"status": "ready"`)
  and the draft evaluation runs it. The instructions state that every sha256 in the
  receipt must be re-bound whenever a TXT/JSON pair changes.
