# Captain INPUT_SYNC gate

## Captain entry

The user starts a delivery by opening ATE Captain and naming TM items or one range. Captain confirms `Project_Info.json`, internally creates a unique batch with `open_new_delivery(user_text)`, and follows its JSON. The user does not run a command, name a batch or create a trial directory.

## INPUT_SYNC

INPUT_SYNC is deterministic. Captain starts it for the whole batch, then dispatches only roles named by the returned JSON. If a source role completes, Captain internally advances the same batch; this refreshes manifests once and returns the next stage.

## Material boundary

- Read source material only from `project/DALI/Input_GlobalMaterial`.
- Write parsing products only to `project/DALI/Output_Global_Material`.
- Write parsing error logs only to `project/DALI/ErrorLog`.

DFT authority is the workbook in the input root, `OVERVIEW` sheet only. No older CSV, trial output, IR or substitute source may be used.

## Stop rule

If material is missing, a source conflicts, a required check fails after canonical regeneration, or an electrical decision is genuinely needed, stop and state the one plain-language cause. Do not change a path, bind a new hash, select a substitute source or infer a value.
