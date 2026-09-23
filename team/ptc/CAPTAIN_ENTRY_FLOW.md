# Captain entry and source expert flow

## What the user does

The user clicks **ATE Captain**, opens a new conversation, and says which tests to deliver. Examples:

- `做 TM102、TM105 和 TM425`
- `做 TM106 到 TM110`

The user does not create a trial directory, choose a batch id, run Python, or manually advance a stage.

## What Captain does

1. Classify the request. Expert-agent optimization edits the relevant role and gate; ordinary conversation does not start a delivery.
2. For a delivery, confirm the current project with `Project_Info.json`. If confirmation is missing or paths changed, show the project confirmation window. Do not use another path.
3. Call the internal `open_new_delivery(user_text)` entry in `scripts/captain_delivery_entry.py`.
4. It parses the TM list or range, creates a unique batch id, binds the project JSON hash, runs INPUT_SYNC for the complete selection, and returns one JSON handoff.
5. Dispatch only the returned role(s), with the returned complete TM list. After each terminal role report, call internal `advance_batch(batchId)` and follow its next handoff.
6. A range skips TM numbers that do not exist in DFT. A TM the user explicitly named but that does not exist is reported simply: `你点名的 TMxxx 在 DFT 中没有。`
7. If a gate is blocked, explain the exact one cause in short Chinese and stop at that gate.

## INPUT_SYNC

INPUT_SYNC is deterministic. Captain invokes it internally for every TM in the new batch, then follows the returned `dispatches` list. DFT and schematic specialists receive only their listed TM set. Their products are checked or regenerated only from `project/DALI/Input_GlobalMaterial`.

## Batch fast delivery

Every new Captain batch records fast delivery as its delivery default. It does **not** skip INPUT_SYNC, strategy, method, method review, implementation, input-boundary enforcement, hash binding, minimum implementation verification, or compile.

When every TM reaches `RULE_REVIEW_IMPLEMENTATION`, Captain internally enables the batch exception and proceeds to compile. The result is `FAST_DELIVERY_PENDING_AUDIT`, never `COMPLETE`.

Independent implementation audit is never automatically resumed. Captain calls the resume operation only after the user explicitly asks to restore strict audit for that batch.

## Source experts

- The DFT expert reads source facts only from the canonical workbook `OVERVIEW` in `Input_GlobalMaterial`. The Hook also permits it to read back its own assigned TM DFT output folder solely for the mandatory self-check; all other output folders remain denied.
- The schematic expert reads only canonical schematic material from `Input_GlobalMaterial`. TXT remains the human product; JSON is the lossless AI product.
## PTC activation boundary

The Captain entry Hook runs only when the top-level session has `agentPreset=ate-ptc` and its `cwd` is exactly the DSH workspace root. A normal coding session is never PTC, including when its first message mentions a TM number.

## Semiconductor preprocessing (workflow part 1)

Before any write-function / invoke-command / run-test action, and whenever a session starts or Captain is invoked, Captain runs preprocessing.

### Project basics (always output and maintain)

1. Input location — local directory holding the project input documents (default `project/DALI/Input_GlobalMaterial`).
2. Document list — all documents the project uses (at least the three input classes).
3. Output location — directory where test results and artifacts are written.
4. VS project location — path of the associated Visual Studio project.

### Confirmation rules

- Already confirmed in this session → reuse silently, never re-ask.
- First message in a new session → load the last cached configuration from `team/ptc/.captain-project-cache.json` (seeded from the approved `Project_Info.json`) and show it for confirmation.
- User says it is wrong → allow correction and overwrite the cache.
- User explicitly asks for a reset → re-run full identification from scratch.

### Document identification

Read every candidate document under the input location, then classify each one:

| Class | Strong signals |
| --- | --- |
| Schematic | CSV with `PORT`, `pin`, `Capo`, `KELVIN`; electrical-connectivity content |
| DFT | Excel/CSV with test-item names, test conditions, expected values, register configuration; `VSET` power-on commands — the strongest DFT signal |
| CBIT table | Board names like `S30_ACM200_FH`; Cbit numbers; filename contains `Cbit`. Strong exclusion: schematic and DFT documents contain no Cbit information |

Deterministic keyword rules decide first; only conflicting or weak signals go to model reasoning inside the Captain session. Output a per-document verdict (schematic / DFT / CBIT table / unknown), present it plus the four project facts to the user for confirmation, then pass the confirmed document-type mapping to the INPUT_SYNC specialists (dft-expert, schematic-expert) as the pre-judgment for their parsing.
