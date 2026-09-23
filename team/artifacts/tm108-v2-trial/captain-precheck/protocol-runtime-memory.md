# Team runtime protocol — mandatory, effective immediately

Authority: user ruling (highest priority), adopting the already-recorded sections
`Dispatch and Trigger Rule`, `Direct Handoff Protocol`, `TM Trigger Matrix`, `User Error Escalation`
from `team/TEAM_ARCHITECTURE_V2.md` (lines 778-814) and `team/ROLE_ROUTING.md` (lines 17-53).
This file is the team's operational memory for that ruling. It binds every member and the captain.

## 1. User trigger has highest authority

A user-triggered role first validates its declared inputs, then performs only its chartered work.
The user's explicit instruction overrides the automatic trigger path in every case.

## 2. Direct Handoff Protocol (normal path)

The completing role owns the normal handoff, not the captain. After passing its own required
acceptance checks it sends the named next role exactly one `deliverable_ready` notification containing:

- TM, task ID
- artifact paths and hashes
- verdict
- unresolved or blocking items
- the completion gate that was satisfied
- the exact permitted next action

The receiving role must validate sender, task owner, required artifacts, hashes, gate and assigned
next role, then immediately claim only its own pre-authorized task, mark it in progress, read the
declared artifacts, and perform only its chartered work. It must reject the notification when any of
those do not match.

The captain does not relay ordinary handoffs. The captain observes the event trail, resolves a
rejected handoff or blocking finding, and may create a user-triggered stage.

## 3. TM Trigger Matrix (automatic start conditions)

| Receiving role | Required valid notification(s) for automatic start |
|---|---|
| test-strategy-architect | Both `dft-expert` and `schematic-expert` `deliverable_ready` for the same TM |
| test-method-expert | `test-strategy-architect` `deliverable_ready` |
| ate-implementer | `test-method-expert` `deliverable_ready` |
| rule-reviewer | `ate-implementer` `deliverable_ready` |
| compile-diagnostician | `rule-reviewer` pass `deliverable_ready` |

test-strategy-architect records the first upstream notification as waiting only and starts only when
the matching second notification arrives. All other normal roles start immediately after their sole
required valid notification.

## 4. Role binding and dispatch rule

A task may be assigned only to its named owner. An idle member must never claim, start, or receive a
task owned by another role. No task may be pre-created as runnable for a later stage.
`evolution-expert` is excluded from all normal TM events and can be dispatched only by explicit user trigger.

## 5. User Error Escalation (blocking path)

Any missing, unreadable, hash-mismatched, conflicting, unsafe, out-of-charter, failed-review or
failed-build input is a blocking error. The discovering role must notify the user directly with:

1. TM and stage
2. the problem
3. the impact
4. evidence paths plus line or key
5. eliminated alternatives
6. the precise ruling required

It must NOT notify the normal next role with `deliverable_ready`, start an automatic repair task,
choose between conflicting facts, or continue downstream until the user rules.

## 6. Per-role application

- **dft-expert** — Owns DFT intent facts. On completion of a TM's DFT artifact sends `deliverable_ready`
  to test-strategy-architect only. Stage-2 input is one of the two required notifications. Never claims
  strategy, method, implementation, review or compile tasks. Blocking error → escalate to user.
- **schematic-expert** — Owns physical connection facts. On completion sends `deliverable_ready` to
  test-strategy-architect only. Stage-2 input is the other required notification. Never selects routes.
  Blocking error → escalate to user.
- **setup-architect** — Owns the frozen resource and safety baseline. Sends `deliverable_ready` only for
  user-triggered Setup reconciliation; Setup is otherwise read-only. Never produces per-TM decisions.
- **test-strategy-architect** — Starts only after both DFT and schematic `deliverable_ready` for the same
  TM. Sends `deliverable_ready` to test-method-expert on completion. Records the first upstream
  notification as waiting only. Blocking error → escalate to user, never pick a conflict value.
- **test-method-expert** — Starts on test-strategy-architect `deliverable_ready`. Sends
  `deliverable_ready` to ate-implementer on completion. Works only inside the signed resource boundary.
  Blocking error → escalate to user.
- **ate-implementer** — Starts on test-method-expert `deliverable_ready`. Sends `deliverable_ready` to
  rule-reviewer on completion. Never invents electrical or method decisions.
- **rule-reviewer** — Starts on ate-implementer `deliverable_ready`. On pass sends `deliverable_ready` to
  compile-diagnostician. On a blocking verdict it notifies the designated resolver and the user instead of
  the normal next role; no downstream role starts.
- **compile-diagnostician** — Starts only on a rule-reviewer **pass** `deliverable_ready`. Emits
  build-report. Repairs only behaviour-invariant mechanical errors; everything else returns to its owner.
- **evolution-expert** — Excluded from all normal TM events. No task, no notification, no message.
  Works only after an explicit user trigger, on closed-run evidence only.

## 7. TM108 suspension (user ruling, effective immediately)

All further TM108 dispatch and all automatic repair is suspended.

- `t5` (test-method-expert) and `t6` (dft-expert) may complete only the atomic audit/contract output they
  have already claimed, then stop. No `deliverable_ready` handoff downstream.
- If either surfaces a blocking item, it escalates directly to the user per section 5.
- The captain creates no remediation task and starts no downstream role.
- OI-T4-01 (`DTEST0` unproven, zero hits in the schematic three-artifact set) and DFT conflicts
  F1-F6 remain unresolved and may not be resolved by any agent.
- Implementation, review and compile stages remain unstarted and uncreated.
