# Session handoff

This document is a bounded continuation record. Read it before acting in the new thread.

## Metadata

```json
{
  "handoff_id": "20260928-agent-trainer-repair",
  "created_at_utc": "2026-09-28T05:56:28Z",
  "source_thread_id": "01a0e332-3e07-7cb3-b22b-1920e83a8ab2",
  "compression_count": 0,
  "compression_threshold": 2,
  "workspace": "D:/Newtest/DSH/ATE-Coding-Flow",
  "branch": "current working tree; preserve unrelated user changes",
  "source_model": "gpt-5-current-thread",
  "source_reasoning": "unknown",
  "objective": "Repair the DSH Agent Trainer into an empty-project, user-configurable framework. Users must create Agents and workflows themselves; the same workflow must support SMOKE_ONLY and BUSINESS_ONLY adapters; schematic must complete before DFT in the real business path; publish must freeze a self-contained immutable bundle; engineering mode must be read-only; run details must expose inputs/outputs and Skill/script usage. Use the user-created schematic expert, DFT expert, and Offline-Coding-Flow for final UI and lifecycle acceptance.",
  "user_constraints": [
    "The formal project starts with no default Agents and no default workflows.",
    "Synthetic Role 1~7 and Synthetic Producer -> Consumer are isolated validation fixtures, not product defaults.",
    "SMOKE_ONLY remains available for framework acceptance and must never be presented as real DFT execution.",
    "BUSINESS_ONLY must use the real Agent rules, Skills, scripts, inputs, outputs, and gates.",
    "The real two-step business order is schematic expert -> DFT expert; do not claim concurrent execution satisfies it.",
    "Publish freezes Agent memory, instructions, Skills, scripts, contracts, workflow, and SHA-256 dependencies.",
    "Engineering mode can only run an activated frozen version and cannot modify it.",
    "The white Agent Trainer surface is the target UI; preserve the user's existing files and unrelated changes.",
    "Every material change must have a Git checkpoint/commit; do not stage unrelated dirty files.",
    "The attached prototype must be reviewed by the user before production buttons are wired.",
    "Active SMOKE_ONLY is the AGENTS.md eight-expert framework contract: registry order, fresh no-tool/no-private-material children, exact arithmetic prompt, reviewer twice, evolution auxiliary task, answer=3, and businessGatePassed=false.",
    "BUSINESS_ONLY is training evidence under Training_Materials/runs and is not release-eligible until a separate business training and release decision.",
    "The continuation thread must use gpt-6-astra with ultra reasoning, falling back to xhigh only if ultra is rejected."
  ],
  "completed": [
    "Read and reconciled the 20260927 drawing-flow handoff, current AGENTS.md, current Git state, current 3080 state, and the Offline-Coding-Flow status-panel handoff.",
    "Created docs/prototypes/agent-trainer-repair-prototype.html, an interactive V1-style white three-column Trainer prototype with empty-project explanation, two user-created Agents, schematic -> DFT workflow, dynamic Agent/workflow creation and ordering, SMOKE_ONLY/BUSINESS_ONLY contracts, run tabs, and publish/engineering states.",
    "Created docs/维修计划-动态AgentTrainer-20260928.md with phased implementation, parallel tracks, AGENTS-aligned smoke/business boundaries, Git rules, and acceptance criteria.",
    "Created docs/agent-trainer-repair-plan-20260928.md as an ASCII-stable pointer to the UTF-8 Chinese plan.",
    "Confirmed current implementation gaps: fixed smoke role allowlists, separate business path rather than one workflow mode switch, missing generic trainer service/bundle, project state currently unbound, and business pipeline source steps currently concurrent.",
    "Confirmed the latest 20260928 TM109 business run contains schematic and DFT artifacts and semantic review evidence, but it is not proof of final UI, publish, or engineering read-only acceptance.",
    "No production execution code was changed in this review turn; the target prototype is the review gate.",
    "Computer Use verified the local prototype: SMOKE_ONLY/BUSINESS_ONLY highlighter and contract switch, schematic-before-DFT business order, run-record input/output and Skill+script tabs, Agent filtering, empty-project creation, dynamic workflow step insertion, SMOKE freeze/publish/engineering read-only, and BUSINESS_ONLY release blocking."
  ],
  "decisions": [
    "Do not delete historical smoke/business artifacts; isolate them from the formal project registry.",
    "Do not reuse ARITHMETIC_PROFILES as the product Agent registry.",
    "Use one workflow revision with an explicit executionMode and adapter, not duplicated smoke/business workflows.",
    "Use static JSON Pointer bindings and persist actual payload plus source artifact hashes.",
    "Business INPUT_SYNC must await schematic output and gates before starting DFT.",
    "Do not begin production wiring until the user approves the prototype interaction.",
    "Keep framework-smoke (eight experts) visibly distinct from the two-agent workflow-business graph in UI, run metadata, and release eligibility.",
    "Parallel work is allowed only along the file boundaries in the repair plan; the primary thread owns contracts, merge, restart, and final Computer Use acceptance."
  ],
  "changed_files": [
    "docs/prototypes/agent-trainer-repair-prototype.html — review-only interactive target prototype",
    "docs/维修计划-动态AgentTrainer-20260928.md — repair plan and acceptance contract",
    "docs/agent-trainer-repair-plan-20260928.md — ASCII-stable plan pointer",
    "docs/session-handoffs/20260928-agent-trainer-repair.md — encrypted handoff",
    "docs/session-handoffs/20260928-agent-trainer-repair.md.sha256 — handoff digest"
  ],
  "validation": [
    "Read-only audit of current source and state: current GET /api/ptc-control/state reports identity=unbound and project=null.",
    "Read-only audit of Training_Materials/runs/training-20260928t022905z-9ab45836 shows schematic and DFT input-sync artifacts, receipts, and semantic review files.",
    "Read-only audit of docs/session-handoffs/20260927-offline-coding-status-panel.md confirms the prior layout patch passed 11 targeted tests and Gate A/B/C, but no fresh end-to-end run followed it.",
    "Prototype file was written as a standalone local HTML; JavaScript syntax, duplicate-id, required-interaction-string, and V1-layout checks passed. A temporary localhost preview was used for Computer Use verification; the file is ready to open in Codex for user review."
  ],
  "open_risks": [
    "The active runtime bundle and backend are mismatched after rollback; white Trainer routes may still return not found until the project/trainer service is wired.",
    "DLP-protected files must be read and hashed through their plaintext view where required.",
    "The worktree contains many unrelated modified and untracked user files; do not clean or stage them.",
    "The user has not yet approved the prototype; no production implementation may be inferred from prototype clicks."
  ],
  "next_action": "Present docs/prototypes/agent-trainer-repair-prototype.html to the user for P0 approval. The prototype is the V1 white Trainer/Agent/workflow layout with dynamic empty-project creation, both execution modes, run detail tabs, freeze, and engineering read-only. Until approval, do not modify production execution code. After approval, create a Git checkpoint and start P1 with the empty project registry and trainer/backend binding.",
  "resume_prompt": "Read AGENTS.md, docs/agent-trainer-repair-plan-20260928.md, then read the UTF-8 plan at docs/维修计划-动态AgentTrainer-20260928.md, and verify the adjacent SHA-256 digest for this handoff before acting. Open docs/prototypes/agent-trainer-repair-prototype.html in Codex and report whether the user-facing interaction matches the requested empty-project V1 Trainer (left Trainer/Agent/workflow navigation), dynamic workflow, framework-smoke versus two-agent business scope, dual mode, publish freeze, engineering read-only, and run detail tabs. Wait for explicit prototype approval before changing production code. After approval, use the four parallel tracks in the plan and checkpoint each merge in Git. Use gpt-6-astra ultra (xhigh only if ultra is rejected)."
}
```

## Objective

Repair the DSH Agent Trainer into an empty-project, user-configurable framework. Users must create Agents and workflows themselves; the same workflow must support SMOKE_ONLY and BUSINESS_ONLY adapters; schematic must complete before DFT in the real business path; publish must freeze a self-contained immutable bundle; engineering mode must be read-only; run details must expose inputs/outputs and Skill/script usage. Use the user-created schematic expert, DFT expert, and Offline-Coding-Flow for final UI and lifecycle acceptance.

## User constraints

- The formal project starts with no default Agents and no default workflows.
- Synthetic Role 1~7 and Synthetic Producer -> Consumer are isolated validation fixtures, not product defaults.
- SMOKE_ONLY remains available for framework acceptance and must never be presented as real DFT execution.
- BUSINESS_ONLY must use the real Agent rules, Skills, scripts, inputs, outputs, and gates.
- The real two-step business order is schematic expert -> DFT expert; do not claim concurrent execution satisfies it.
- Publish freezes Agent memory, instructions, Skills, scripts, contracts, workflow, and SHA-256 dependencies.
- Engineering mode can only run an activated frozen version and cannot modify it.
- The white Agent Trainer surface is the target UI; preserve the user's existing files and unrelated changes.
- Every material change must have a Git checkpoint/commit; do not stage unrelated dirty files.
- The attached prototype must be reviewed by the user before production buttons are wired.
- Active SMOKE_ONLY is the AGENTS.md eight-expert framework contract: registry order, fresh no-tool/no-private-material children, exact arithmetic prompt, reviewer twice, evolution auxiliary task, answer=3, and businessGatePassed=false.
- BUSINESS_ONLY is training evidence under Training_Materials/runs and is not release-eligible until a separate business training and release decision.
- The continuation thread must use gpt-6-astra with ultra reasoning, falling back to xhigh only if ultra is rejected.

## Completed

- Read and reconciled the 20260927 drawing-flow handoff, current AGENTS.md, current Git state, current 3080 state, and the Offline-Coding-Flow status-panel handoff.
- Created docs/prototypes/agent-trainer-repair-prototype.html, an interactive V1-style white three-column Trainer prototype with empty-project explanation, two user-created Agents, schematic -> DFT workflow, dynamic Agent/workflow creation and ordering, SMOKE_ONLY/BUSINESS_ONLY contracts, run tabs, and publish/engineering states.
- Created docs/维修计划-动态AgentTrainer-20260928.md with phased implementation, parallel tracks, AGENTS-aligned smoke/business boundaries, Git rules, and acceptance criteria.
- Created docs/agent-trainer-repair-plan-20260928.md as an ASCII-stable pointer to the UTF-8 Chinese plan.
- Confirmed current implementation gaps: fixed smoke role allowlists, separate business path rather than one workflow mode switch, missing generic trainer service/bundle, project state currently unbound, and business pipeline source steps currently concurrent.
- Confirmed the latest 20260928 TM109 business run contains schematic and DFT artifacts and semantic review evidence, but it is not proof of final UI, publish, or engineering read-only acceptance.
- No production execution code was changed in this review turn; the target prototype is the review gate.
- Computer Use verified the local prototype: SMOKE_ONLY/BUSINESS_ONLY highlighter and contract switch, schematic-before-DFT business order, run-record input/output and Skill+script tabs, Agent filtering, empty-project creation, dynamic workflow step insertion, SMOKE freeze/publish/engineering read-only, and BUSINESS_ONLY release blocking.

## Decisions to preserve

- Do not delete historical smoke/business artifacts; isolate them from the formal project registry.
- Do not reuse ARITHMETIC_PROFILES as the product Agent registry.
- Use one workflow revision with an explicit executionMode and adapter, not duplicated smoke/business workflows.
- Use static JSON Pointer bindings and persist actual payload plus source artifact hashes.
- Business INPUT_SYNC must await schematic output and gates before starting DFT.
- Do not begin production wiring until the user approves the prototype interaction.
- Keep framework-smoke (eight experts) visibly distinct from the two-agent workflow-business graph in UI, run metadata, and release eligibility.
- Parallel work is allowed only along the file boundaries in the repair plan; the primary thread owns contracts, merge, restart, and final Computer Use acceptance.

## Changed files

- docs/prototypes/agent-trainer-repair-prototype.html — review-only interactive target prototype
- docs/维修计划-动态AgentTrainer-20260928.md — repair plan and acceptance contract
- docs/agent-trainer-repair-plan-20260928.md — ASCII-stable plan pointer
- docs/session-handoffs/20260928-agent-trainer-repair.md — encrypted handoff
- docs/session-handoffs/20260928-agent-trainer-repair.md.sha256 — handoff digest

## Validation

- Read-only audit of current source and state: current GET /api/ptc-control/state reports identity=unbound and project=null.
- Read-only audit of Training_Materials/runs/training-20260928t022905z-9ab45836 shows schematic and DFT input-sync artifacts, receipts, and semantic review files.
- Read-only audit of docs/session-handoffs/20260927-offline-coding-status-panel.md confirms the prior layout patch passed 11 targeted tests and Gate A/B/C, but no fresh end-to-end run followed it.
- Prototype file was written as a standalone local HTML; JavaScript syntax, duplicate-id, required-interaction-string, and V1-layout checks passed. A temporary localhost preview was used for Computer Use verification; the file is ready to open in Codex for user review.

## Open risks and unknowns

- The active runtime bundle and backend are mismatched after rollback; white Trainer routes may still return not found until the project/trainer service is wired.
- DLP-protected files must be read and hashed through their plaintext view where required.
- The worktree contains many unrelated modified and untracked user files; do not clean or stage them.
- The user has not yet approved the prototype; no production implementation may be inferred from prototype clicks.

## First action in the new thread

Present docs/prototypes/agent-trainer-repair-prototype.html to the user for P0 approval. The prototype is the V1 white Trainer/Agent/workflow layout with dynamic empty-project creation, both execution modes, run detail tabs, freeze, and engineering read-only. Until approval, do not modify production execution code. After approval, create a Git checkpoint and start P1 with the empty project registry and trainer/backend binding.

## Resume prompt

Read AGENTS.md, docs/agent-trainer-repair-plan-20260928.md, then read the UTF-8 plan at docs/维修计划-动态AgentTrainer-20260928.md, and verify the adjacent SHA-256 digest for this handoff before acting. Open docs/prototypes/agent-trainer-repair-prototype.html in Codex and report whether the user-facing interaction matches the requested empty-project V1 Trainer (left Trainer/Agent/workflow navigation), dynamic workflow, framework-smoke versus two-agent business scope, dual mode, publish freeze, engineering read-only, and run detail tabs. Wait for explicit prototype approval before changing production code. After approval, use the four parallel tracks in the plan and checkpoint each merge in Git. Use gpt-6-astra ultra (xhigh only if ultra is rejected).
