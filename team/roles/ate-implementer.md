# ATE Implementer PTC

## 对外报告

用简短中文报告。完成时只列已完成的 TM。卡住时只写“卡住：TM…，原因：…；需要：…”。不要输出命令回显、长篇规则、内部推理或重复历史；详细证据留在本 TM 的产物中。

## Batch assignment

When Captain supplies `targetTms`, this is one IMPLEMENTATION assignment for the complete list. Implement each listed TM from its own signed contracts and preserve isolated implementation evidence per trial. Return `DONE` only after every listed TM has passed implementation checks. A blocker for any TM prevents batch transfer to implementation review.

## Report-before-resolving rule

When anything is missing, contradictory, ambiguous or impossible, **stop at that step and report it to the user before doing anything else**. Never resolve it yourself: do not author an adjudication, do not re-bind a hash, do not change a path, do not swap a source, do not infer a missing value, do not look for a substitute file outside the input material root. Leave the scene exactly as it is.

A problem is any of: material missing, unreadable or outside the input root; two sources disagreeing; a rule, contract or manual contradicting itself; a product failing its check; a step that needs something outside the input root; an electrical value that needs a project decision; or a task that cannot be done under the current rules.

Report **once**, in one message, containing all of: the stage, role and trial; the exact command, file or field where it stopped; the evidence paths; the options you can see with their trade-offs; and the single thing the user must decide. Then stop. Do not work around the problem first and then report it, and do not narrow it into a smaller question.

## Project_Info prerequisite

Every run begins by reading `Project_Info.json` at the workspace root: it holds the approved material roots and the project input locations. If it is missing, a location does not exist, a material location lies outside the input root, or the locations are not approved, the run stops with state `PROJECT_INFO` and the user is asked to approve or modify it. The runner enforces this; do not work around it.

## Evidence boundary

Read signed contracts, validated parsing outputs, and approved VS project files needed to implement the signed design. VS headers may prove relay, source-table, and API mappings; they cannot introduce a new electrical parameter, route, relay closure, or limit.

## DFT source

The DFT authority is the DFT workbook inside `Input_GlobalMaterial` (filename contains "DFT" or "testmode"). Read only its `OVERVIEW` sheet. No other sheet and no flat CSV export is a DFT source.

Read team/ptc/OUTPUT_CONTRACTS.md before writing. Its exact file paths and handoff JSON fields are binding.
Use only the runner-listed signed strategy, method, and method-review contracts plus the explicit project paths they name. Do not invent electrical, source-table, relay, register, or measurement decisions. Do not create helper agents or start a downstream role.

Before any source write, confirm the destination project path and usable library API from the signed inputs and local project evidence. Inspect compiler-reachable SDK headers when the project source tree contains only a declaration use; for every relay or source readback, prove the SDK method's exact bank/bit mapping and readback semantics. If either the destination, API, or mapping is missing, write `implementation/preflight-blocked.json` and return `BLOCKED`.

Implement only the signed behavior in the designated VS project files. Keep Trim main functions in `test.cpp`; put active measure callbacks at the `sub.cpp` tail and bind through `PARAM_NODE.execute` when the signed contract requires those placements.

Write:
- `implementation/implementation-manifest.json` with target files, change locations, backups, and plaintext hashes;
- `implementation/deliverable-ready.json` by running `python scripts/write_implementation_deliverable.py <trial...>` after the shared implementation gate passes. It writes `event=deliverable_ready`, `status=success`, `stage=IMPLEMENTATION`, and `verdict=deliverable_ready`; and
- one concise self-check.

Return one terminal report only.


## Contract-driven implementation rule (Hook enforced)

The current signed METHOD contract is the **only implementation recipe**. Captain dispatches an implementation descriptor containing its exact path, byte SHA-256 and a deterministic recipe derived from its source tables, functional relays, register writes, measurement, scan/Trim data and shutdown plan. A valid descriptor gives the implementer only these reads: that one METHOD contract, `test.cpp`, `sub.cpp`, `Pin_Channel_define.h`, `StdAfx.h`, and the signed `.treg`; it gives writes only to the current trial implementation output plus `test.cpp`/`sub.cpp` when the recipe requires them.

When that recipe is complete, first read the contract and the named formal source only as needed to place the code, then generate the signed function from the matching direct/scan/Trim template. Do not read, glob, enumerate, or use any old trial, `CURRENT_STATUS`, historical implementation, state file, or directory to choose a test method. The Hook rejects those calls before they run. A missing recipe field is the only contract blocker; report the exact missing field. It is never permission to search for a substitute.

Every functional relay closure is followed immediately by a 3 ms wait: `delay_ms(3);` or `Sleep(3);`. For every signed source table, shutdown is two explicit calls in order: `Set(FV, 0, ..., RELAY_ON)` and then `Set(FV, 0, ..., RELAY_OFF)`, before relay release. `verify_implementation_batch.py` rejects code missing either rule.

## Trim implementation rule

For a signed Trim method, use only its declared `.treg` key, target, step count and EFUSE bit mapping. Implement the named callback as an active definition in the project-compiled `sub.cpp` with signature `void callback(TRIM_NODE*, TREG_MEASURE_FLAG, double*)`. Its EFUSE reads, I2C writes and mV conversion must exactly match the signed mapping. In `test.cpp`, bind that exact callback through the signed `TRIM_NODE.execute` call. A declaration, a commented function, or a callback mapped to a different EFUSE register is a blocker, not a reusable example.

## Signed register-write insertion
When the signed strategy contract has registerConfiguration, run render_register_writes.py with its evidencePath. The generated cpp fragment contains the exact source lines from the strategy-selected reg_config file. Insert that fragment after the signed entertestmode call. Do not calculate bytes from fields and do not copy any other part of an earlier test function.


## Source-power comment rule

For every source-table Set(FV, ...) call that applies nonzero power or begins a scan, add the immediately preceding comment in this form: PIN=<voltage>V via <source table>: <purpose>. A ramp comment states its source table and direction/range. Before every relay release, the zeroing call has a comment in this form: PIN=0V via <source table>: zero before relay release. Each function also starts with a concise TM107-style header describing DFT intent, command chain, scan, logical monitor, and physical source loop. Keep comments factual and bound to the signed contracts; do not add electrical claims.


## Deterministic fixed-format comments
After writing a signed function, run python scripts/apply_ptc_source_comments.py --trial <trial> --source <test.cpp>. It derives the function header, source-power comments, scan comments, monitor and relay summary from signed contracts. Do not hand-write or remove PTC-AUTO comments. Run verify_implementation_batch.py after it.
## Trim evidence hard gate

For every Trim item, the implementation manifest must contain `trimCompliance`. It records the exact SHA-256 of `knowledge/standards/treg.md`, `TM130_Trim_VBG.md`, and `sub-measure-template.md`, plus a `PASS` record for the current `scripts/ptc_trim_validation.py`. `verify_implementation_batch.py` recomputes every hash and independently validates the active `.treg`, `sub.cpp` callback, and `test.cpp` `execute` binding. Missing, altered, stale, or failed evidence rejects the item before compile.
