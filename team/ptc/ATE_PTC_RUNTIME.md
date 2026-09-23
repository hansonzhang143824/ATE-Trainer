# ATE PTC Runtime

## Purpose

PTC advances a complete user-requested TM batch one stage at a time. Specialists see only their signed inputs for all TMs assigned to their stage.

## Captain algorithm

1. The user starts by opening **ATE Captain** and naming TM items or one range in natural language. Captain confirms `Project_Info.json` if necessary and calls internal `open_new_delivery(user_text)`. Users do not run commands or choose a batch id.
2. The entry creates a unique frozen batch, binds the approved project JSON hash, runs INPUT_SYNC for the whole scope, and returns its JSON handoff. A range includes existing DFT items only. An explicitly named missing TM is reported simply.
3. Captain dispatches only the returned role(s). Each role receives every TM that needs its current stage.
4. On each terminal report, Captain calls internal `advance_batch(batchId)`. It refreshes INPUT_SYNC manifests after source specialists finish and returns the next whole-batch handoff.
5. New Captain batches default to fast delivery after all TMs pass implementation and reach independent implementation review. INPUT_SYNC, strategy, method, method review, input boundary, hashes, the minimum implementation check and compile remain mandatory. The batch state becomes `FAST_DELIVERY_PENDING_AUDIT`.
6. Captain does not automatically resume independent audit. It can resume only on a later explicit user request for that batch.
7. On any real problem, state the short cause, evidence path on request, and stop at that gate.

## Boundaries

Only DFT and schematic parsing roles read raw source material. They read only `project/DALI/Input_GlobalMaterial`; their products go only to `project/DALI/Output_Global_Material` and logs to `project/DALI/ErrorLog`.

Strategy, method, review, implementation and compile roles may read signed contracts, validated parsing outputs and approved VS project resource evidence. VS headers never override DFT limits or schematic facts.

## Stage chain

`INPUT_SYNC -> STRATEGY -> METHOD -> RULE_REVIEW_METHOD -> IMPLEMENTATION -> RULE_REVIEW_IMPLEMENTATION -> COMPILE -> COMPLETE`

For a multi-TM request, all selected TMs pass each stage before transfer to the next. Shared parsing products may be reused; every TM retains separate later-stage evidence.

## Plain-language reports

Say only what completed or what is blocked and needed next. Do not show command lines, internal stage mechanics, long tool output or repeated history unless the user asks for it.
