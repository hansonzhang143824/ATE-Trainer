# DFT v7 runtime acceptance — 2026-09-22

Published version: v7; previous v6 retained unchanged.
Manifest digest: 71b3f07886dde4d731e47ed29679a0f979b92c24267f27a7d23225dc5e558d91.

## Implemented behavior

- Published dispatcher invokes the existing read-only DFT_OUTPUT gate before
  spawning a model. The gate computes the canonical plaintext SHA-256, checks
  source coverage, schema, unresolved intent, and both semantic-review bindings.
- All requested TMs ready: return UNCHANGED; no model child; no DFT artifact,
  verification-file or error-log writes. Host batch bookkeeping is still saved.
- Missing/stale products: start the published expert with exact command recipes.
  Invalid gate response, execution failure or 30-second gate timeout fails closed.
- Model DFT jobs receive an eight-minute abort timer. The installed DSH driver
  connects that signal to child.cancel(). Timed-out results are blocked and do
  not qualify as successful source handoffs.
- DFT-only input is saved in executionScope and filters dispatches. The scoped
  continuation exits before preparing or entering later stages.
- v7 resolves the old delivery-address-book and verification-file conflicts.

## Evidence

- Direct production-path acceptance: batch dali-20260922-192826-tm109,
  1077 ms, v7, UNCHANGED, spawnCount=0, advanced=false. All three DFT byte
  digests and modification times equal their before-test values.
  Report: team/artifacts/dali-20260922-192826-tm109/fastpath-acceptance.json.
- Live 3080 acceptance after service restart: session
  session-5b6ed0cc-ca08-481b-a8cc-a6d57a507ba7, batch
  dali-20260922-193103-tm109. Receipt pins v7, childSessionId=null,
  executionMode=UNCHANGED. source-terminal.json reports done and advanced=false.
  Captain responded with UNCHANGED in one turn without tool calls.
- Plugin regression: 116 passed, 1 skipped (file symlink privilege unavailable),
  0 failures. Includes accelerated deadline cancellation, no late cancellation
  after success, malformed gate failures, no-model reuse and scoped completion.
- Python scope tests: 14 passed. Chinese/full-width/English DFT-only requests
  produce only the DFT role; continuation cannot prepare or advance downstream.
- Publisher's draft evaluation, boundary regression and existing case gate passed.

The live service was restarted only after session.list reported zero running
sessions. New process: 8480; HTTP 3080 verified online. Existing sessions persist.
Runtime logs: team/artifacts/dft-v7-runtime/server.stdout.log and server.stderr.log.

## Reproduce

Open a new ATE Captain conversation and send:

    TM109，只执行DFT expert，检查已有产物，完成后停止。

Expected with unchanged inputs/products: UNCHANGED, no specialist child, no
artifact rewrites, no schematic dispatch, no downstream stage.

The real-material test deliberately exercised reuse only. Regeneration was not
forced on the already valid TM109 set. The eight-minute cancellation was tested
with a shortened timer and a hung provider; no eight-minute live model was run.
