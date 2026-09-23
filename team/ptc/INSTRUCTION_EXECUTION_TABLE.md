# Captain execution table

| Step | Captain internal action | Result |
|---|---|---|
| 1 | Read the user’s TM list or range in a new ATE Captain conversation. | A range skips numbers absent from DFT; an explicitly named absent TM gets one short error. |
| 2 | Confirm `Project_Info.json` and call `open_new_delivery(user_text)`. | A unique batch is created, bound to the current project, and INPUT_SYNC runs. |
| 3 | Read only its JSON handoff. | Dispatch the listed source roles or one stage role for all listed TMs. |
| 4 | After each terminal role report, call `advance_batch(batchId)`. | Captain receives the next stage for the complete batch. |
| 5 | When every TM reaches implementation review, enable the batch’s default fast delivery internally. | Input boundary, hashes, minimum implementation verification and compile still run; state is `FAST_DELIVERY_PENDING_AUDIT`. |
| 6 | Only after a later explicit user request, resume the independent implementation audit. | Resume begins at the skipped review without rerunning completed stages. |
| 7 | At a real block, report the short cause and stop. | Never alter source, path, hash or electrical values as a workaround. |

## Boundaries

- DFT and schematic source reads: `project/DALI/Input_GlobalMaterial` only.
- Parsing products: `project/DALI/Output_Global_Material` only.
- Parsing error logs: `project/DALI/ErrorLog` only.
- Later roles use signed contracts, validated parsing products and approved VS project evidence.
