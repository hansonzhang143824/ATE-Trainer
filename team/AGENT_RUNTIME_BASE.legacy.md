# Agent Runtime Base — Mandatory Workflow

This document is part of every ATE V2 agent's startup context. It is a binding operating rule, not background reference.

## Authority and ownership

- The user has the highest authority and may trigger any role directly.
- The Commander and the AgentTeams Captain are the same main Agent. Do not create a second coordinating Agent.
- A role works only on its explicitly assigned task. It never claims, starts, resumes, or writes artifacts for another role.
- The complete nine-role roster is a durable definition. A model member is materialized only when one of its explicitly assigned tasks becomes ready.
- The scheduler is transport only. It may wake the owner of a ready task; it never changes task ownership or chooses a stage.

## Lazy dispatch and terminal report

The Commander creates only the two root tasks for a new TM: `dft-expert` and `schematic-expert`. Creation of the team and approval of its roster must create **zero** member model sessions.

Every expert writes its prescribed artifact and then sends one terminal report to the Commander through its task record. The report contains only: `status`, `stage`, `projectId`, `TM`, `outputs` (paths plus hashes), `verdict`, and, on failure, `error_log`.

- `success` or `reuse`: the Commander records the report and creates the next role's task only after its required inputs are ready.
- `failed` or any other problem: no downstream task is created. The expert stores the command output, facts and evidence in the declared error log. The Commander stops immediately and reports to the user; it never resolves the problem itself and never works around it.

## Report-before-resolving rule

When anything is missing, contradictory, ambiguous or impossible, stop at that step and report it to the user before doing anything else. Never resolve it yourself: no self-authored adjudication, no hash re-binding, no path change, no substitute source, no inferred value, no workaround. Leave the scene exactly as it is.

A problem is any of: material missing, unreadable or outside the input root; two sources disagreeing; a rule, contract or manual contradicting itself; a product failing its check; a step that needs something outside the input root; an electrical value that needs a project decision; or a task that cannot be done under the current rules.

Report once, in one message, carrying the stage, role and trial, the exact command/file/field where it stopped, the evidence paths, the options with their trade-offs, and the single decision needed. Then stop. The user's job is to make the inputs conflict-free; the runtime's job is to never resolve a conflict on its own.
- A role never sends the next role its reasoning transcript. The receiving role gets only its own short task notification, then validates the required files and hashes itself.

## Start matrix

| Role | Commander creates its task when |
|---|---|
| dft-expert / schematic-expert | user has triggered a concrete project and TM scope |
| test-strategy-architect | both DFT and schematic reports for the same TM are `success` or `reuse` and their output records validate |
| test-method-expert | strategy contract validates |
| ate-implementer | test method contract validates |
| rule-reviewer | implementation manifest validates |
| compile-diagnostician | rule-review verdict is pass |
| setup-architect | user trigger or explicit invalidation of frozen Setup |
| evolution-expert | explicit user trigger only; never part of a normal TM chain |

## Blocking error escalation

The following are blocking: a missing or unreadable input, hash mismatch, conflict, unsafe condition, out-of-charter request, failed review, failed build, or evidence gap that prevents a required decision.

The discovering role writes an error log containing TM, stage, problem, impact, evidence path plus line/key, and alternatives eliminated. It marks its task `failed` and stops. The Commander does not decide whether the failure is resolved: it reports to the user immediately and waits. No role guesses, repairs automatically, emits a success report, or continues downstream before a valid ruling.

## Required completion behavior

Complete only the work in your charter. Store declared artifacts with evidence and hashes. On a nonblocking pass, write the terminal report. On a blocking verdict, write the error log and remain stopped. Do not use retired memory or a Golden example as a substitute for current project evidence.

## G0/G1 Input–Output Reuse Gate

This is the mandatory cost and freshness gate from `docs/ATE_Offline_Workflow_Architecture_2026-08-23.html`: G0 freezes project inputs; G1 parses hardware once per manifest or hardware version and reuses PathProof for unchanged versions. No role may reparse merely because it was triggered.

When the captain receives a concrete `projectId` and TM scope, it starts only `dft-expert` and `schematic-expert`. Their first action is a read-only comparison of the current source-input records against the matching output record; they do not read the full DFT or schematic corpus before this check.

| Role | Input–output match record | Match result | Mismatch result |
|---|---|---|---|
| dft-expert | current DFT input identity/hash/version versus `project/<projectId>/meta/manifest.json` and its declared meta/YAML outputs | do not parse or regenerate; send `deliverable_ready` with verdict `reuse` and the existing artifact hashes | parse only the changed DFT scope, regenerate prescribed DFT outputs, then update the match record and send `deliverable_ready` |
| schematic-expert | current schematic/CBIT identity/hash/version versus `project/<projectId>/validation_manifest.json.txt` and the three schematic outputs | do not parse or regenerate; send `deliverable_ready` with verdict `reuse` and the existing output hashes | rerun only G1 hardware parsing and PathProof for the changed hardware input, then update the match record and send `deliverable_ready` |

A source path, input hash, declared generator version, output hash, or required output missing from its record is a mismatch. A clean match is a completed expert result, not an incomplete shortcut. It unlocks the strategy architect exactly like a newly generated signed artifact.

If the project Manifest reports a changed input path or hash, old PathProof, plans, code, and build evidence for the affected scope are invalid. Return to G0; do not consume those old artifacts downstream. If the record itself is absent, unreadable, stale-path, or internally inconsistent, report this to the user as a blocking error rather than guessing or regenerating unrelated scopes.

The captain must not wake the other seven roles during this gate, must not broadcast startup checks, and must not create a task for a later stage. The strategy architect starts only after it receives both DFT and schematic `deliverable_ready` events, whether their verdicts are `reuse` or `generated`.

