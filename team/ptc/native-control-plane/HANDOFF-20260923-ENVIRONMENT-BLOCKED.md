# Native PTC control-plane handoff — environment blocked

Checkpoint: 2026-09-23, Asia/Shanghai. This is **not completion** and **not the quota threshold being reached**.

## User authority and quota

- Replace the abandoned 4090 console with DSH-native training/release controls on 3080; no bridge or legacy migration.
- Training: isolated single-agent and whole-flow trials, editable drafts, diagnoses and regression evidence. Release: immutable complete bundle of agents and orchestration, runtime may pause/communicate but not change logic.
- User authorized parallel development using CodeM (xhigh), Claude Code/OpenCode and native helpers. External read-only review of training-dispatch.js/training-execution.js was explicitly approved and completed earlier.
- Latest clarification: **40% remaining = 60% consumed** triggers handoff and pause until the user resumes. Do not use the superseded 40%-consumed threshold. Latest sample before writing this checkpoint: 44% consumed / 56% remaining. See QUOTA-CONTROL.md.
- Development is presently blocked by an independently reproduced local runtime/filesystem problem. Do not spend the remaining quota repeatedly running hung tests, pretend tests passed, or disable safety checks to deploy.

## Working directory and deployment

- Workspace: `D:\Newtest\DSH\ATE-Coding-Flow` (not a Git checkout).
- Plugin source: `plugins/dsh-ptc-control-plane`.
- Installed junction: `C:\Users\nvt10241\.dsh\profiles\web\node_modules\dsh-ptc-control-plane` points to this plugin.
- Last successful sanctioned DSH restart evidence: `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20260922-234207` (gates A/B/C passed, runtime started at approximately 23:43).
- The running server has NOT been restarted after this checkpoint's new pipeline manager, guard, HTTP routes or DFT budget/watchdog changes. Source-on-disk is newer than loaded server modules.
- Client build printed `built lib\client.js (37387 bytes)` during this turn, but its process did not promptly complete; do not call this a successful full deployment. Static serving may expose newer client bytes before a server restart, while the old server does not expose pipelineStages/new routes.
- ONLY restart via:

```powershell
& 'C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1' -PluginDir 'D:\Newtest\DSH\ATE-Coding-Flow\plugins\dsh-ptc-control-plane'
```

Do not kill/relaunch DSH ad hoc. Restore the test/runtime environment first. The sanctioned tool must pass its tests before stopping the existing server.

## Actual browser acceptance and DFT diagnosis

- IAB tab 7, URL `http://127.0.0.1:3080/`, retained for handoff. Existing conversation: 生成TM109代码并执行DFT expert.
- Actual UI-run `training-20260922t153154z-fa40e64f`: typed TM109, clicked creation, real expert dispatched; clicked stop, status became blocked; child result settled and both handles disposed. See UI-ACCEPTANCE-20260922-CP008.md. This proves dispatch/stop, not semantic correctness.
- Actual draft-editor UI save changed only `team/expert-profiles/ptc-dft-expert/instructions.md`, not versions. SHA before `fb0190a4f01d531c81213df5393d3a365e771237794dbf00569c336af968ba5c`; after `7046fba48d7a51023764e7c85caa5583a4bdf820d1df07229f4d7c10cd063eee`; history `530fb54f-9ead-4ce2-a45c-6b14d6e60d37`.
- Subsequent actual UI-run `training-20260922t154456z-898b29e5` ended **blocked** at `2026-09-22T15:50:03.993Z`: `training execution exceeded 300000 ms`. Last browser observation still showed blocked, no active stop button.
- Diagnosis in DFT-TIMEOUT-154456-REVIEW.md: child `dfbf854e-46f4-4503-bef4-4855e2455f6a`, model `zai-coding-cn/glm-5.3-flash`, inherited adapter `maxTokens=131072`. One model request/step, **zero tools**, approximately 294.632 seconds of reasoning. Preflight/materials 7.319 seconds; actual dispatch tens of milliseconds. Cancellation settled the child within 58 ms, disposal about 63 ms. This is not slow hashing or repeated tool refusal.
- New source-only fixes are NOT live-verified: DFT parent/child local `agentOptions.maxTokens=4096`; after binding a child, a 60-second no-permitted-material-tool-start watchdog; approved read/write/pwsh starts reset it, run_code alone does not; five-minute total dispatch deadline retained. No global model/provider settings changed. DFT guard now allows reading its frozen instructions.
- Source-view script described below addresses the missing XLSX-readable raw evidence, but is **not wired into execution yet**. Do not claim the timeout root cause is fully fixed simply because a watchdog was added.

## Code delivered before environment blockage

Previously integrated core: run identity/path guards, DFT run-local materials and command guard, lifecycle cancellation, draft history/API/editor, release integrity/schema, frozen publisher core, pure pipeline engine. Last complete historical main-suite result was 132/132 before the newest additions; do not reuse that as today's full-suite result.

New bounded helper deliveries, with their dedicated tests completed before the environment failure:

| Module | Verified dedicated result | Meaning / limits |
|---|---|---|
| pipeline-materials.js | 4/4 | Approved configuration provenance, all stage drafts, SCH/CBIT/register/knowledge copies, immutable vs-baseline and mutable vs-project; no actual compile |
| pipeline-dispatch.js | 10/10 | Frozen stage/owner/profile/TM/child bindings, wx initial receipt reservation, cancellation/recovery, read-only schematic INPUT_SYNC exception |
| training_schematic.py | 10/10 earlier helper run | Calls original generator/validator through private runtime mappings, preserves protected legacy scripts |
| training_stage_gate.py | 9/9 | INPUT_SYNC through implementation-review adapters, register preparation, real original checks with controlled mapping; much of fixture coverage injects callbacks, not live project proof |
| training-compile.js | 10/10 earlier helper run | Private vcxproj, fixed v120 MSBuild, bounded tree cancellation, fresh DLL hashes; no real compile |
| host-command.js | 12/12 | Fake-spawn lifecycle/output caps/timeout/late termination tests; no actual process kill in those tests |
| client/state.js + lib/control-state.js | 10/10 + 3/3 | Registry-driven stage selector, pipeline API shapes, progress, pause/resume/stop and interrupted warning |

Root integration after these deliveries (still awaiting complete execution validation):

- New `lib/pipeline-execution.js`: background preparation, separate pipeline manager, run identity/lock, pause/resume/stop, source DFT+SCH adapters, stage-dispatch adapters, fixed Python gates, isolated compile and evidence recovery. Dependency-injection hooks are code-only, not HTTP inputs.
- `lib/index.js`: two new POST routes `/api/ptc-control/training-pipelines/execute` and `/control`; strict allowed JSON fields; combines DFT and generic pipeline guards before tools; closes old generic stage receipts at startup; shutdown cancels managers.
- `pipeline-guard.js`: startup reconciliation revokes and closes prior stage receipts; scoped generic stage tools and profile/registry hashes. No free-form shell for generic children.
- `pipeline-dispatch.js`: supplies host-computed shaFacts in prompt (added after its earlier 10/10 run).
- `training-execution.js`: exports `runDftGate` and `finalProductHashes` for host adapters.
- `training-dispatch.js` and its tests: 4096-token local budget and no-tool-progress watchdog as above. New cases not executed successfully after local environment failure.
- `pipeline-execution.test.mjs`: 12 fixture/DI tests written, NOT completed. Two test attempts hung before first result. Static review findings were patched: stage owner/gate, schematic report identity/7 output paths, source recovery, compile artifact run scope/size, source/project hash recheck, prepared identity and resumed background tracking. Re-run all cases after recovery; do not assume green.
- `all.test.mjs` now registers pipeline-materials/guard/dispatch/execution, schematic roots, training compile/stage gate and host-command suites. The source-view test is not registered yet.
- Native pipeline UI source now has ordered registry-derived start/end stages, TM list, explicit experimental pipeline creation, per-stage progress/gate result, pause/resume/stop. It is not a live full-flow acceptance.

### Source-view adapter not yet integrated

New files: `scripts/training_dft_source_view.py`, `test/training-dft-source-view.test.mjs`.

```text
python -X utf8 scripts/training_dft_source_view.py --run-id <id> --tm TM109 [--tm TM110]
```

- Fixed output `Training_Materials/runs/<id>/input/dft-source-view.json`.
- Checks training run/material manifest v2/workbook plaintext SHA-256. Selects only canonical OVERVIEW A-column exact unique TM rows; raw coordinates/value/dataType/formula, first-row headers, neighboring rows and full related merged ranges. No reusing generated DFT meta as purported independent source.
- Limits ZIP/dimensions/time and 128 KiB; ambiguity/overflow blocks, never silent truncation. Creates exclusively or reuses identical bytes, never overwrites different evidence.
- Success stdout `{status:'SOURCE_VIEW',runId,path,sha256,sourceSha256,testItems,reused,bytes}`; failure exit 2/BLOCKED. Not a semantic PASS.
- Both script syntax and 4 fixture tests remain UNEXECUTED due Python startup hang. Need review, run, then integrate host preparation and read-only guard access, bind host source/view digests, add producer to frozen policy list, register tests, update fixtures. Do not append to an existing material manifest without maintaining its fingerprint contract.

## Environment blocker — do not misdiagnose as agent logic

From roughly midnight, isolated Node filesystem operations stopped completing:

- Node `C:\Program Files\nodejs\node.exe`, v24.18.0, libuv 1.52.1.
- Root instrumented plugin test: mkdir/write/open/read/close completed; last marker was `BEFORE renameSync` replacing a **new isolated temporary fixture** draft. No AFTER marker.
- Helper reproduced rename hang in three separate new temp directories: target absent, target existing, and same-extension a.tmp to b.tmp. This does not require production files or competing access to the same target.
- Another test hung in recursive temp cleanup; removing only the nonessential after-test cleanup allowed its state assertions to finish. This does not justify weakening business atomic writes.
- Python `-c "print('runtime-ok')"` and separate PowerShell/Python comparisons also timed out before an operation marker. Therefore we cannot claim their rename operation failed, only startup/front-end execution stalled.
- No Handle/Process Monitor found on PATH; read-only filter listing denied. No evidence establishes a specific security product, Windows driver or libuv bug. No security setting was disabled and no protected script was moved to strip encryption.
- Last combined-suite attempt (session 90425) passed many earlier tests and stopped after the fifth schematic test, with a Python --help child. NOT a passing full suite.
- Root plugin reruns 46958/97695 and instrumented 56078 stopped at draft rename. Pipeline test sessions 5228/30458 also did not complete. Client build session 51942 printed its output size but did not promptly finish.
- Exact command/PID-checked termination was requested for owned test/diagnostic children only. Examples: node 15236/42688/42308/45212; Python 44436/46564; taskkill reported success, but some process objects remained visible or no final close event arrived. Earlier 38808/16448 had similar behavior. PID numbers are historical and MUST be re-resolved before any future action; never kill a reused PID based on this document alone.
- No current native helper is running model calls or continuing code changes after handoff. Some terminated/hung OS test processes may remain awaiting system cleanup; do not claim all process trees are confirmed gone.
- Existing DSH web process was left running. No new release activated, no real VS build, no production source modification, no 4090 mutation.

## Resume order

1. Resolve the local runtime/filesystem stall with the user/system administrator. Save other work before any reboot; do NOT automatically reboot the machine or disable security software. Read-only diagnostics exhausted so far are above.
2. Prove a single fresh isolated Node rename and Python print can terminate, with bounded processes; do not immediately re-run multiple full suites.
3. Check current quota; obey the 60%-used/40%-remaining handoff stop. Re-inventory owned lingering test processes by current command lines, not historical PIDs.
4. Review and execute pipeline-execution and new watchdog tests. Verify actual schematic validator JSON shape; root now requires seven exact output paths and canonicalInput.path. Check source/project build report binding against real compiler schema. Harden remaining recovery/manifest/runtime policy boundaries before enabling production.
5. Review/test/integrate raw DFT source view. It must be host-generated, independently hash-bound and read-only to the child. Revalidate all frozen-policy/cache fixtures when adding its producer policy.
6. Run complete `node test/all.test.mjs` with appropriate local permissions (fake/isolated fixtures; no real experts). Build client. Only after this succeeds use the sanctioned DSH restart script, whose own gates must pass.
7. Computer Use acceptance: real clicks/type TM109 for a new DFT run, observe useful first tool within 60 seconds, real semantic review and final gate, then repeat to prove UNCHANGED with matching input/draft/policy/product provenance. Do not manufacture ready results or reuse stale artifacts as fresh review.
8. Real pipeline UI acceptance source-only first, then ordered extended stages; verify per-run isolation, pause/resume/stop, failure stops downstream, and no delivery writes. A compile adapter module is not proof the approved VS environment can build the isolated project.
9. Finish remaining product scope: non-DFT single-agent execution, orchestration draft editing/training evidence, whole-bundle publish UI and trustworthy evidence collection, immutable release/runtime enforcement and communication/pause controls. Publisher core existing tests are not a released production workflow.

## Safety / context references

- Design: `team/ptc/DSH-NATIVE-PTC-CONTROL-PLANE-PLAN.md`.
- Workboard and audits: WORKBOARD.md, PIPELINE-ADAPTER-AUDIT.md, SNAPSHOT-INTEGRATION-REVIEW.md, PARALLEL-REVIEW-20260922.md.
- Sole stage authority: `team/ptc/ptc_stage_registry.json`.
- Approved VS original: `D:/PROJECT6-DALI/ForCodexDebug/source`; only read for snapshot. Never use legacy fast_rebuild/DTE SaveAll for training.
- Some old .py/.json are DLP-wrapped to PowerShell/Node. Authorized Python reads expose their plaintext. Preserve protection; use separate training adapters instead of deleting/recreating old files to strip wrappers.
- Account reset credits: none observed. Do not purchase/redeem or create a recurring workaround.
