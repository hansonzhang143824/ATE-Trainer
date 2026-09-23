# ATE Direct Dispatch State Machine

This document is the executable operating contract for ATE delivery. One task run has exactly one state. A transition requires the named artifact; text intent, a chat reply, or a staged plan is never sufficient.

| State | Required evidence before entry | Only allowed action | Exit evidence | Next state |
|---|---|---|---|---|
| INPUT_SYNC | User task + CURRENT_STATUS.md | Reuse matching DFT/schematic outputs or dispatch only stale input owner(s) | input manifest with hashes | PREFLIGHT |
| PREFLIGHT | Signed strategy + method contracts + target capability scan | Validate every requested measurement, log, relay, register and code side effect has a reachable implementation primitive | `preflight-capability.json` | IMPLEMENT or BLOCKED |
| IMPLEMENT | PREFLIGHT pass | One implementer task writes code and one manifest | implementation manifest + byte-safe before/after hashes | REVIEW |
| REVIEW | Frozen implementation hash | One independent rule-reviewer reads a copy and writes one findings file | `review-findings.json` | COMPILE, REMEDIATION, or BLOCKED |
| REMEDIATION | REVIEW findings | One implementer task fixes every approved finding in one change set | remediation manifest + new frozen hash | REREVIEW |
| REREVIEW | Frozen remediation hash | One independent re-review | re-review verdict | COMPILE or BLOCKED |
| COMPILE | REVIEW/REREVIEW pass | One compile-diagnostician run | build log + diagnostic report | COMPLETE or BLOCKED |
| BLOCKED | Exact evidence path + one unresolved decision | Stop dispatching; report one concrete user question | user ruling or updated signed contract | INPUT_SYNC or PREFLIGHT |
| COMPLETE | Compile pass + independent review pass | Publish terminal report | terminal report | COMPLETE |

## Hard limits

1. No `agent_teams_*` call is permitted.
2. At most two simultaneous specialists, and only for independent input acquisition. Review and remediation never overlap.
3. A reviewer creates no child tasks and exits after its single findings artifact.
4. One review may produce one remediation task. One remediation may produce one re-review. A failed re-review becomes BLOCKED; it never expands into another autonomous graph.
5. A goal loop is forbidden unless the user explicitly asks for automatic continuation. When authorized, it may perform one state recheck only; it cannot generate a new task.
6. Before IMPLEMENT, a capability preflight must reject a contract claim that has no reachable code primitive. This would have caught TM108 RF-01 before `test.cpp` was changed.
7. Any source write requires a byte-safe before hash, an after hash, and a restore pointer before the next state can start.
## Required executable gates

The following commands are transition gates, not suggestions:

- `PREFLIGHT → IMPLEMENT`: `python scripts/verify_t7_preflight.py <trial>/implementation/preflight-capability.json` must return `PASS` (exit 0). A `BLOCKED` result prevents any write to a production source file. The preflight must enumerate every signed method requirement, including logging, and prove each required symbol exists in the declared source/header scope.
- `IMPLEMENT → REVIEW`: implementation manifest records byte-safe before/after hashes for every changed source.
- `REVIEW entry`: `python scripts/verify_review_snapshot.py create --implementation-manifest <manifest> --copy-dir <trial>/review/copy --snapshot <trial>/review/immutable-review-snapshot.json` must return `PASS`. Reviewers inspect only those copies.
- `REVIEW verdict`: `python scripts/verify_review_snapshot.py verify --snapshot <trial>/review/immutable-review-snapshot.json` must return `PASS` immediately before the verdict is written. A changed live source is revision drift and blocks the verdict.
- `REVIEW verdict`: `python scripts/verify_review_evidence_scope.py --evidence <trial>/review/review-evidence-scope.json` must return `PASS`. No capability/presence assertion may pass from a zero-candidate search.

Each gate command, exit code, and artifact hash goes into the single stage report. A failed gate ends that stage with `BLOCKED`; Captain does not create a helper task, retry loop, or source write.



The incident-to-control mapping is recorded in `team/PROCESS-CORRECTIONS-2026-09-17.md`. New ATE runs must use it with this state machine; it does not reopen frozen trials.

## INPUT_SYNC implementation rule

INPUT_SYNC is a deterministic script stage, not an investigative Captain turn. Run only `python scripts/prepare_input_sync.py --tm <TM> --trial-dir <trial>`, then read its `input-manifest.json` and follow `status`/`dispatchableRoles`. During this state the Captain may not read previous trials, inspect source details, interpret a DFT row, or run arbitrary probes. A missing/failed source or output results in `BLOCKED` with the manifest path.

All DFT/schematic/source hash values for DLP transparent-protected files must come from `python scripts/hash_ate_plaintext.py`. Windows byte readers (`Get-FileHash`, certutil, ReadAllBytes, Get-Content -AsByteStream) are forbidden for these gates because they can hash a TSZ wrapper instead of plaintext.

DFT completion requires `dft-meta.json` + `dft-conditions.yaml`; schematic completion requires `SCH-Connect-Map.txt` + `Component-Statistic.txt` + `SCH-Connect-Map.json` + `Components-Statistic.json` + `schematic-receipt.json`, all under the trial directory and bound to the canonical plaintext hash. Strategy may not start until these five files are present and input-manifest records them.
