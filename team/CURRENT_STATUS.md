# Current PTC status

## Schematic source stage

- Approved source materials: `Dali-SCH.csv` and `sch_confirmed.json` in `Input_GlobalMaterial`.
- TXT products are for human review: `SCH-Connect-Map.txt`, `Component-Statistic.txt`.
- JSON products are for AI and scripts: `SCH-Connect-Map.json`, `Components-Statistic.json`.
- Each JSON contains every TXT byte, the full TXT text, section records, indexes, and the TXT SHA-256. `schematic-receipt.json` binds all four products to both approved input hashes.
- Run `python scripts/validate_schematic_outputs.py` before accepting schematic output.

## Current Captain batch

- Batch: `dali-20260922-184558-tm109` — user request「帮我写TM109的code,只执行DFT expert」. Scope TM109 only, **frozen at INPUT_SYNC (DFT parsing)** by the user's instruction: do not advance to STRATEGY or later stages.
- Entry record: `team/artifacts/ptc-batches/dali-20260922-184558-tm109.json`. Trial dir: `team/artifacts/dali-20260922-184558-tm109/tm109`.
- Stage: **INPUT_SYNC**. The framework auto-dispatched both source roles for TM109: dft-expert (profile v6, child `c5b3ab78-3a43-4fca-82bd-584889a21c9d`) and schematic-expert (v2, child `6aeee494-3100-4762-9e68-3308fb7cbfad`), both dispatched 2026-09-22 18:45:58 local.
- TM109 DFT products: `project/DALI/Output_Global_Material/dft/TM109/{dft-meta.json,dft-conditions.yaml,dft-semantic-review.json}` — `python scripts/validate_dft_outputs.py --tm TM109` reports `DFT_OUTPUT status=ready` with no stale output (checked 2026-09-22 18:47 local). Expected specialist outcome for this batch: `mode=UNCHANGED`.
- Operator note: one manual `captain_delivery_entry.py --request` call also created the empty duplicate batch `dali-20260922-184700-tm109`; it was removed so exactly one TM109 batch is active.
- Previous batch history (kept below): `dali-20260919-135213-tm103-tm106-tm108-tm109-tm425` — user request `TM103/106/108/109/425`, fast delivery is the default for this batch.
- Entry record: `team/artifacts/ptc-batches/dali-20260919-135213-tm103-tm106-tm108-tm109-tm425-captain-entry.json`.
- Stage: **INPUT_SYNC**. Dispatched role: **dft-expert** for TM103, TM106, TM108, TM109 — attempt 1 `890b653c-0dd1-48f0-8cb4-45866043193c` returned BLOCKED (boundary defect below); attempt 2 (retry) `cd6592c4-f674-405b-a633-c34ebf7e29d6`.
- Boundary defect found and fixed (Captain, verified): the dft-expert boundary allows exactly one dft-meta generator, `scripts/refresh_dft_meta_from_source.py` with a required `--ruling <trial>/input-manifest.json`, but that script had no `--ruling` argument, so argparse exited 1 and no meta could be produced inside the role boundary. `--ruling` is now implemented: it must be a trial `input-manifest.json` under `team/artifacts` whose `canonicalInputs.dft.sha256` equals `--expected-sha`, and it is recorded in the meta as provenance. The generator now also prints `metaSha256`, `rawIntent` and `testCondition`; `render_dft_conditions_yaml.py` now prints `outputSha256`, so the role can bind the semantic review without read access to its own output directory. The boundary file itself was not modified, so no plugin reload was needed.
- Tests: `scripts/test_refresh_dft_meta_from_source.py` (3 tests, OK). Verdict on the retry dispatch is pending.
- Waiting at IMPLEMENTATION: TM425, trial `team/artifacts/tm425-ptc`, owner `ate-implementer` (its implementation artifact is missing or its signed hash/function no longer matches).
- Entry parser fix: `scripts/captain_delivery_entry.py` now also parses the `TM103/106/108/109/425` shorthand and TM mentions written directly against Chinese text; before the fix the first Captain entry returned BLOCKED for this request.
