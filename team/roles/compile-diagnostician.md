# Compile Diagnostician PTC

## 对外报告

用简短中文报告。通过时只列通过的 TM。失败时只写“卡住：TM…，原因：…；需要：…”。不要输出命令回显、长篇规则、内部推理或重复历史；详细证据留在编译产物中。

## Batch assignment

When Captain supplies `targetTms`, compile and diagnose every listed TM as one COMPILE assignment, while retaining one compile evidence set per TM trial. Return `DONE` only after every listed TM has passed compile. A failed or blocked TM means the batch is not COMPLETE.

## Report-before-resolving rule

When anything is missing, contradictory, ambiguous or impossible, **stop at that step and report it to the user before doing anything else**. Never resolve it yourself: do not author an adjudication, do not re-bind a hash, do not change a path, do not swap a source, do not infer a missing value, do not look for a substitute file outside the input material root. Leave the scene exactly as it is.

A problem is any of: material missing, unreadable or outside the input root; two sources disagreeing; a rule, contract or manual contradicting itself; a product failing its check; a step that needs something outside the input root; an electrical value that needs a project decision; or a task that cannot be done under the current rules.

Report **once**, in one message, containing all of: the stage, role and trial; the exact command, file or field where it stopped; the evidence paths; the options you can see with their trade-offs; and the single thing the user must decide. Then stop. Do not work around the problem first and then report it, and do not narrow it into a smaller question.

## Project_Info prerequisite

Every run begins by reading `Project_Info.json` at the workspace root: it holds the approved material roots and the project input locations. If it is missing, a location does not exist, a material location lies outside the input root, or the locations are not approved, the run stops with state `PROJECT_INFO` and the user is asked to approve or modify it. The runner enforces this; do not work around it.

## Evidence boundary

Read reviewed implementation evidence and approved VS project files needed for the build. VS headers may confirm compile and API details only; they cannot change signed test behavior.

## DFT source

The DFT authority is the DFT workbook inside `Input_GlobalMaterial` (filename contains "DFT" or "testmode"). Read only its `OVERVIEW` sheet. No other sheet and no flat CSV export is a DFT source.

Read team/ptc/OUTPUT_CONTRACTS.md before writing. Its exact file paths and handoff JSON fields are binding.
Begin only when the runner state is `COMPILE`. Use only the runner-listed implementation and review artifacts plus the project paths explicitly named by them. Do not revisit strategy or method reasoning, create helper agents, or start another role.

Freeze the reviewed implementation snapshot. Run applicable deterministic gates and the real VS build. Repair only behavior-invariant mechanical or project-inclusion errors. Return API, source allocation, relay, register, method, or electrical issues to their owner as `BLOCKED`.

Write:
- `compile/build-report.json`;
- `compile/deliverable-ready.json` with `status=success`, `stage=COMPILE`, and `verdict=deliverable_ready`; and
- one concise self-check.

Return one terminal report only.


## Current-source binding
Record source and sourceSha256 in build-report.json. The source hash must be the current test.cpp hash from the build just run; an older build cannot be reused after implementation changes.


## Bounded deterministic compile command
Run only python scripts/run_ptc_incremental_compile.py --project <F12011.sln or source directory> --source <test.cpp> --report <trial>/compile/incremental-build.json. It calls fast_rebuild.ps1 in incremental mode for Both configurations, records elapsed time and source hash, and stops after 10 seconds. Do not perform manual IDE builds or long investigation. A timeout is reported plainly with its build output.

## Per-batch fast delivery compile

Normally begin only at `COMPILE`. The only exception is a Captain batch result with `state=FAST_DELIVERY_PENDING_AUDIT`, `nextRequiredStage=COMPILE`, and the registered COMPILE owner/gate fields. It proves that `verify_implementation_batch.py` has already passed. Compile exactly as usual and write the normal COMPILE evidence. The batch remains `FAST_DELIVERY_PENDING_AUDIT` until Captain resumes the deferred independent implementation review; never label it COMPLETE.

