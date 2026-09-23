# Parallel review and integration, 2026-09-22

The user authorized independent parallel tasks and Claude Code/OpenCode as alternatives to CodeM. CodeM was run at xhigh. Codex retained exclusive write ownership of the implementation files.

## Actual CLI results

- CodeM: initial sandbox invocation failed to create its configuration lock. An approved retry succeeded. The xhigh read-only review completed with exit 0. No CodeM source changes were requested.
- Claude Code: initial read-only review failed with ConnectionRefused and the first external retry was rejected pending specific source-egress approval. The user subsequently explicitly approved sending training-dispatch.js and training-execution.js to the configured service for read-only review. Both approved reviews then completed with exit 0 (terminal sessions 27559 and 7286). The second retry cleared invalid process-local proxy settings only for that invocation. Configured model: deepseek-v4-pro[1M], service host api.deepseek.com; Claude Code CLI does not imply Anthropic inference. Findings: distinguish cancellation request from actual termination, retain raw settlement evidence, bound and record resource disposal, and cover startup in the deadline.
- OpenCode: command help is available. No model task dispatched, and it was not used to bypass the Claude source-transmission rejection.

## Findings confirmed by Codex

1. Separate training run IDs still write the same Training_Materials/Output_Global_Material/dft/TM109 files. The run-local execution lock does not provide cross-run product isolation. A passing serial UI run does not prove concurrent isolation.
2. Verification files are admitted by the dft- basename prefix, without binding each file to its run and TM.
3. A provisional dispatch receipt with childSessionId null is accepted by the guard if its label matches. This weakens the intended one-child binding.
4. runWriteDecision uses lexical path containment. A filesystem link can invalidate this coarse helper's assumptions. This helper is not currently the material guard, whose realpath checks provide a different layer.
5. The timeout promise previously awaited child and parent disposal. A hanging disposal could prevent terminal state settlement. Explicit stop only signalled abort and relied on the provider to settle.

CodeM also raised filesystem check/use races. Do not treat its claim that a permitted training child can create symlinks as established: the allowed commands and write tools do not themselves demonstrate that capability. Further validation belongs with the per-run boundary work.

## Integrated changes

- Cancellation and timeout settle without awaiting unbounded disposal.
- A closed signed receipt revokes subsequent tool calls.
- Timeout/abort skips certification of potentially partial outputs and writes blocked state promptly.
- The task prompt asks for an independent semantic review and allows PASS only when supported, rather than requiring a PASS result in advance.
- Tests exercise hanging disposal, a provider ignoring abort, and no re-gate after cancellation. The 60-test suite and official restart gates A/B/C pass.
- After restart, Codex selected ptc-dft-expert and clicked the single-agent training button in the 3080 UI. Run training-20260922t145626z-9eea57cb visibly completed UNCHANGED with no model dispatch. This validates the normal reuse path, not a live model timeout.

## Remaining scope

- CP-008: per-run input/product snapshots and run-bound verification; preserve fast unchanged reuse through explicit validated cache semantics.
- Bind a child before any material tool access; reject stale provisional receipts.
- Include parent creation/provider startup in the deadline.
- Cancellation requests do not prove an already-running tool process has exited. Do not claim otherwise.
- Follow-up implementation now includes run-local frozen materials, strict child binding and lifecycle tracking; integration and browser acceptance are still in progress, so the historical 60-test result above is not certification of these newer changes.
- Full pipeline training, immutable release publication and release-bound delivery remain part of the overall plan; they are not certified by this review.
