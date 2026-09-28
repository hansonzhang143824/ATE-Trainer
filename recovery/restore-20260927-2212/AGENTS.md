# ATE PTC Direct Runtime — active smoke scope

`team/ptc/ptc_stage_registry.json` remains the authority for stage order and
owner. The former DFT and schematic execution flows, rules, gates, and checks
are preserved under
`team/ptc/native-control-plane/archive/DFT-SCHEMATIC-LEGACY-20260923/`.
They are historical references and are not part of the active DSH-native
`SMOKE_ONLY` training or published replay.

## Eight-expert smoke contract

1. DFT, schematic, strategy, method, reviewer, implementer, compile, and
   evolution experts all receive exactly: `1+2等于几，把答案写在JSON里`.
2. Each expert is trained independently in a new run with a fresh DSH model
   child. The child has no tools and receives no private project material or
   archived expert instructions. It must return JSON with numeric `answer: 3`.
3. The whole-chain training run dispatches fresh children in registry stage
   order. DFT and schematic occupy the two `INPUT_SYNC` slots; the reviewer
   is dispatched at both review stages. Evolution is a final auxiliary smoke
   task, not an invented registry stage. Captain/host independently checks
   each new child result and stops on a missing, malformed, or non-3 answer.
4. Do not call the former DFT gate, schematic parser, Component-Statistic
   producer, SCH-Connect-Map generator, business gates, or compile in this
   smoke path. No previous specialist output can substitute for a fresh
   arithmetic response.
5. Freeze the eight trained profile snapshots and the completed orchestration
   evidence to `publish/versions/<releaseId>/`. Published mode uses the
   pinned snapshot and writes a new run under `publish/runs/<runId>/`, again
   dispatching fresh arithmetic children for every slot.
6. Every smoke result says `SMOKE_ONLY` and `businessGatePassed: false`. A
   passing arithmetic chain proves model invocation, stage handoff, and
   release replay only. It never certifies semiconductor work.

## Hash and write boundaries

- Use SHA-256 lowercase 64-character hexadecimal digests only. Generated
  evidence is hashed over exact on-disk bytes. Protected canonical material,
  if used in a future explicitly restored business path, is hashed only with
  Python's plaintext view via `scripts/hash_ate_plaintext.py`.
- Training writes stay under `Training_Materials/runs/<runId>/`; published
  smoke writes stay under `publish/runs/<runId>/`. Historical business outputs
  and the legacy archive are not overwritten by smoke runs.
- Do not reactivate the archived DFT/schematic workflow or business gates
  without a separate explicit request, training, and release decision.

## Authorized Agent Trainer framework scope (2026-09-24)

FRAMEWORK_TRAINING and FRAMEWORK_REPLAY use synthetic project candidates, explicit immutable bundles, selected instructions/Skills/contracts, and registered synthetic tools. They are separate from the unchanged SMOKE_ONLY arithmetic path. Do not import archived business profiles or private inputs. Every framework result retains businessGatePassed: false. Candidate writes belong under Training_Materials/framework/projects; training runs under Training_Materials/runs; releases/replays under publish. A alone controls 3080; B/C/D follow the parallel plan file ownership.
