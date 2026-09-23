# ATE Team Routing V2

Default context is TEAM_ARCHITECTURE_V2.md, the current role charter, current project facts, active rules, and signed upstream contracts. retired-context/2026-09-17-v1 is audit-only and must not be default input.

1 dft-expert owns scoped meta, YAML, manifest and DFT intent.
2 schematic-expert owns SCH-Connect-Map, Components-Statistic, schematic-ir and physical-path facts.
3 setup-architect owns frozen project resource and safety baseline only.
4 test-strategy-architect owns type, named sources, routes, relay groups and register configuration.
5 test-method-expert owns evidenced phases, actual-node state, measurement, power-down and log.
6 ate-implementer owns correctly placed VS code and implementation-manifest.
7 rule-reviewer owns independent review findings and owner routing.
8 compile-diagnostician owns gates, real build and build-report.
9 evolution-expert owns closed-run knowledge proposals only; it is user-triggered and excluded from the normal TM DAG.

DFT and schematic work may run in parallel. Frozen Setup is baseline. Strategy contract precedes method contract; both precede implementation; review precedes compilation. Resource, route, relay and register issues return to strategy. Stage, actual-node, measurement, power-down and log issues return to test method. API, library, code and VS placement issues return to implementation.

## Dispatch and Trigger Rule

A TM workflow is an event-driven, role-bound sequence. A task may be assigned only to its named owner. An idle member must never claim, start, or receive a task owned by another role.

When a role completes its signed artifact, it emits only a `deliverable_ready` event containing the artifact paths, verdict, unresolved items, and the permitted next role. The next role starts in exactly one of two ways:

1. **Direct event trigger:** the completing role sends `deliverable_ready` to the named next role; that role validates it and immediately claims only its own pre-authorized task.
2. **User trigger:** the task remains uncreated or `awaiting_user_trigger` until the user explicitly starts that stage.

No task may be pre-created as runnable for a later stage. A blocking finding stops the sequence and is reported to the user; no agent may create an automatic resolution task, select a conflict value, or bypass it by dispatching implementation, review, or compilation. `evolution-expert` is excluded from all normal TM events and can be dispatched only by an explicit user trigger.

## Direct Handoff Protocol

The completing role owns the normal handoff. After it passes its own required acceptance checks, it must send the named next role one `deliverable_ready` notification. The notification contains: task ID, artifact paths and hashes, verdict, unresolved or blocking items, the exact permitted next action, and the completion gate that was satisfied.

The named next role must act immediately when it receives a valid `deliverable_ready` notification: claim only its own pre-authorized task, mark it in progress, read the declared artifacts, and perform only its chartered work. It must reject a notification when the sender, task owner, required artifacts, hashes, gate, or assigned next role do not match.

The captain does not relay ordinary handoffs. The captain observes the event trail, resolves a rejected handoff or blocking finding, and may create a user-triggered stage. A blocking verdict notifies the designated resolver instead of the normal next role; no downstream role starts until the resolver completes a replacement `deliverable_ready` handoff.


## TM Trigger Matrix

User trigger has highest authority. A user-triggered role first validates its declared inputs, then immediately performs only its chartered work.

| Receiving role | Required valid notification(s) for automatic start |
|---|---|
| test-strategy-architect | Both `dft-expert` and `schematic-expert` `deliverable_ready` notifications for the same TM |
| test-method-expert | `test-strategy-architect` `deliverable_ready` |
| ate-implementer | `test-method-expert` `deliverable_ready` |
| rule-reviewer | `ate-implementer` `deliverable_ready` |
| compile-diagnostician | `rule-reviewer` pass `deliverable_ready` |

The strategy architect records one upstream notification as waiting only. It starts only after the matching second notification arrives. All other normal roles start immediately after their sole required valid notification arrives.

## User Error Escalation

Any missing, unreadable, hash-mismatched, conflicting, unsafe, out-of-charter, failed-review, or failed-build input is a blocking error. The discovering role must notify the user directly with: TM and stage, problem, impact, evidence paths plus line/key, eliminated alternatives, and the precise ruling required. It must not notify the normal next role with `deliverable_ready`, start an automatic repair task, choose between conflicting facts, or continue downstream until the user rules.
