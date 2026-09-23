# ATE direct-dispatch corrective record — 2026-09-17

This record closes the workflow defects observed during the TM108 trial. TM108 remains frozen; this record does not authorize a new source write.

| Defect observed | Permanent correction | Enforced / verified by |
|---|---|---|
| F1: a Goal recheck became 28 execution rounds | ATE workspace rejects `create_goal` and goal `resume`; the direct state machine advances only from a completed specialist result or a new user instruction. | DSH plugin guard unit tests; plugin regression suite 106/106; plugin restart gates A/B/C. |
| F2: an unverified input claim entered t7 and caused a rewrite | `PREFLIGHT → IMPLEMENT` requires `verify_t7_preflight.py` to hash the method/source inputs and show a declared primitive for every requirement. A blocked requirement prevents production source write. | synthetic supported result exit 0; synthetic missing primitive result exit 2. |
| F3: a check claimed more than its inspected scope | Each review claim must list every searched file, query, candidate count and evidence. | `verify_review_evidence_scope.py`. |
| F4: zero candidates returned a hollow `OK` | A presence/capability check with candidateCount=0 and status=pass is rejected. | synthetic valid evidence exit 0; synthetic hollow capability pass exit 2. |
| F5: legacy AgentTeams staged/approved workflow was invoked | ATE workspace rejects every `agent_teams_*` call in the DSH tool guard. Other workspaces are unaffected. | direct guard unit tests; plugin regression suite 106/106. |
| RF-05: review read one revision while later implementation work modified live source | Reviewer must create a byte-exact review copy from the implementation manifest, then verify source/copy/hash immediately before verdict. A changed live source blocks verdict and requires a new snapshot after consolidated remediation. | synthetic snapshot create + verify exit 0; source mutation exit 2. |
| F6: signed method demanded a log plan with no reachable API | This is an upstream contract capability block, not a code-review retry. It is caught in PREFLIGHT and routes one precise contract question. | T7 capability requirement result exit 2. |

## Fixed execution limits

- Only input acquisition may run two roles in parallel. All downstream stages have one active owner.
- Exactly one independent review, one consolidated remediation, one re-review, then compile. A re-review failure reports the blocker; it does not create another graph.
- Reviewer has read-only copied inputs and no child task authority.
- New scripts are limited to the three transition gates above. They are not a per-review script collection.

## Authorities

- Sequencing: `team/ptc/ptc_stage_registry.json`
- Implementer preflight: `team/roles/ate-implementer-t7-preflight.md`
- Review snapshot/evidence gate: `team/roles/rule-reviewer-snapshot-gate.md`
- DSH runtime block: `D:\Newtest\DSH\Plugin-Think\packages\dsh-commander-workbench\lib\ate-direct-dispatch-guard.js`
