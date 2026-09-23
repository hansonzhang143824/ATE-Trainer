# TM109 direct-trial — captain dispatch ledger

Updated by the Captain only. One row per dispatch; terminal status is append-only.

## Coordination facts (verified by the Captain)

- Input freeze: `input-manifest.json` hashes are authoritative. Do NOT re-hash ATE inputs with `pwsh` `Get-FileHash`/`certutil` — that sandbox layer reads a shadowed `TSZ#` view and produces false mismatches. Use Python `hashlib`. See `captain-ruling-001-input-hash.md`.

## Dispatches

| Task | Role | Subagent | Status | Output | Frozen source hash |
|---|---|---|---|---|---|
| TM109-DFT | dft-expert | c1382f61-8bc6-43ac-bbd6-6379bd9fde9b | DONE (round-1 BLOCKED was a false negative) | `dft/dft-meta.json` (18571 B, sha `885d546e…37e22`, top-level `sourceSha256` ✅ gate-ready) | `b92d203f…0fd4` ✅ confirmed |
| TM109-SCHEMATIC | schematic-expert | 99ed514f-dfc7-4b24-a021-6bbbbfafd4b0 | DONE (round-1 BLOCKED was a false negative), then **gate-conformance fix dispatched** | `schematic/schematic-connect-map.json` (600613 B, sha `a63d78ec…cb9c0`) | `35fdd158…7ff5` ✅ confirmed |

### Gate result after both DONE (deterministic, exit 0)

`python scripts/prepare_input_sync.py --tm TM109 --trial-dir team/artifacts/tm109-direct-trial`
→ `NEEDS-DERIVED-ARTIFACTS`, `DISPATCH=schematic-expert`.

Cause: the gate's readiness predicate is `obj.get('sourceSha256') == source_hash` evaluated on the **top level** of the derived output. `dft-meta.json` carries a top-level `sourceSha256` → `ready`. `schematic-connect-map.json` carries it only at `derivation.sourceSha256` → `stale`. A conformance fix (add the top-level field, change nothing else) was dispatched to the schematic owner; the gate must be re-run after that DONE and must come back `ready` before the strategy architect starts.

### Canonical digest tool (authority)

Per `team/DIRECT_DISPATCH_STATE_MACHINE.md:46`, DLP transparent-protected ATE files must be hashed with `python scripts/hash_ate_plaintext.py`; Windows readers (`Get-FileHash`, `certutil`, `ReadAllBytes`, `Get-Content -AsByteStream`) are forbidden for these gates. Captain reproduced both input digests with that mandated hasher — they equal the declared freeze hashes.

## Stage record

| Stage | State | Evidence |
|---|---|---|
| INPUT_SYNC | **COMPLETE** | `input-manifest.json` `READY`, `DISPATCH=` (empty), exit 0, both entries `ready` |
| Schematic conformance fix | DONE | output sha `a63d78ec…cb9c0` → `b495135b…b40199`, additive single top-level key, proved by byte-exact reconstruction |
| DFT derivation | DONE | `dft-meta.json` sha `885d546e…37e22`, `verdict: generated`, `sourceSha256` = declared |
| test-strategy-architect | **BLOCKED — not dispatched** | `dft-meta.json` `handoff.blockingItems = ["TM109-OI-1"]`; start matrix needs two `deliverable_ready` events, DFT's was withheld |

## Blocking decision (single, carried to the user)

`TM109-OI-1` — the TM109 DFT row is internally inconsistent and `DFT.csv` contains no cross-reference table to settle it:

- `ShortName` (lines 30–34) = `VAC2_PRST`
- `Dynamic` (lines 31–34) = `vset[vac3,3.8,100e-6,1]` / `…vac3,4.4,1e-3…` / `…vac3,4.1,100e-6…` / `…vac3,3.5,1e-3…`
- whole-file token search: `vac2` occurs in **no** record; `vac3` occurs in TM109, TM110, TM624
- TM109's `Dynamic` block is character-identical to TM110's (`VAC3_PRST`, 0x95, MUX 21); TM109's register byte is 0x96 / MUX 22; TM108 `VAC1_PRST` → `vac1`, 0x97, MUX 23

No role in this runtime may choose between these facts. Resolver: user/spec owner.

## Ruling 002 — TM109-OI-1 ruled by the user

User ruling: **`vac2` is authoritative** (option: the `ShortName` stands; the Dynamic block was a copy-paste from TM110). The user applied the correction to the canonical source themselves.

- `dft/source-correction-vac2.json`: `beforeSha256` `b92d203f…0fd4` → `afterSha256` `ce69dce829a1473f1c7fd2ec7d55014b9e2fcf85262301169c654100b5461541`, byte length unchanged at 16862, `changedTokens` = `vac3`→`vac2` ×4, scope "TM109 Dynamic field only", backup retained at `dft/backup/DFT.csv.before-vac2-ruling`.
- Gate re-run: `input-manifest.json` → `needs-derived-artifacts`, `dispatchableRoles = ["dft-expert"]`; `schematic` now `ready`, `dft` `stale` against the new hash.
- Dispatched: **TM109-DFT-R2**, role `dft-expert` only. Outputs `dft/dft-meta.json` + `dft/dft-conditions.yaml`, both bound to top-level `sourceSha256` = `ce69dce8…1541`, using the mandated `scripts/hash_ate_plaintext.py`.
- The previous `dft-meta.json` (bound to `b92d203f…0fd4`) is superseded, not deleted.
- **TM109-DFT-R2 (subagent `9842cea0-c6ac-4bf6-a2e0-feb26cdebd56`) was stopped before finishing and its closing report is empty.** Verified after the stop: `dft-meta.json` unchanged (18571 B, sha `885d546e…37e22`, top-level `sourceSha256` still `b92d203f…0fd4`), `dft-conditions.yaml` absent, `source-correction-vac2.json` and `dft-error-log.json` untouched. Zero bytes written by the run; no partial or corrupt artifact. Stopping cause not stated by the runtime and not attributable by the Captain. **User ruling: the stop was deliberate — HOLD.** No re-dispatch of TM109-DFT-R2 (or any TM109 role) until the user says otherwise. Do not treat this as an idle/obsolete task that may be resumed automatically.

## TM109-SCHEMATIC-R3 (subagent `b9d26b6d-19d7-4616-b880-7d9c3b6eb656`)

Dispatched as the single role named by manifest v2 (`dispatchableRoles = ["schematic-expert"]`) to deliver the three required files under `schematic/`. **Stopped before finishing; closing report empty.** Verified after the stop with Python:

- `schematic/SCH-Connect-Map.json` — ABSENT
- `schematic/Components-Statistic.json` — ABSENT
- `schematic/schematic-ir.json` — ABSENT
- `schematic/schematic-connect-map.json` and `schematic/error-log-tm109-schematic.json` — unchanged (evidence only)
- `input-manifest.json` — unchanged: `status = needs-derived-artifacts`, `schematic = stale`, `dft = ready`, `dispatchableRoles = ["schematic-expert"]`

Zero bytes written by the run; no partial or corrupt artifact; nothing to clean up. This is the second consecutive stop with an empty closing report (see the R2 note above). Per the user's R2 ruling, a stop of an authorized task is treated as deliberate and the Captain does not auto-restart it. **State: HELD at the schematic stage.** Unblocking requires exactly one `schematic-expert` delivery of the three named files, each with top-level `sourceSha256` = `35fdd158…7ff5`.

## TM109-STRATEGY-R1 (subagent `535a5bff-db53-4f9b-bc57-774e8aa5e559`)

Dispatched on the user's explicit continuation trigger as the single role authorized, after manifest v2 reached `status = ready` with `dispatchableRoles = []`, `dft = ready` (`ce69dce8…1541`) and `schematic = ready` (`35fdd158…7ff5`, all three required files reported present by the gate). Task: the project strategy artifact only, under `strategy/`.

**Stopped before finishing; closing report empty.** Verified after the stop with Python:

- `team/artifacts/tm109-direct-trial/strategy/` — directory ABSENT, zero bytes written (no partial artifact, nothing to clean up)
- `input-manifest.json` — unchanged: `status = ready`, `dispatchableRoles = []`, both inputs `ready`
- No subagent running; all five children idle

This is the third consecutive stop of an authorized task with an empty closing report. Per the user's standing R2 ruling, a stop is treated as deliberate and the Captain does not auto-restart. **State: HELD at the strategy stage.** Upstream is complete and hash-bound; the only missing item is the single strategy artifact. Downstream (`test-method-expert`) remains gated and must not be started before it.

### Correction — the strategy artifact did land

The "directory ABSENT / zero bytes written" finding above was true at the moment it was taken (immediately after the first stop notice). A later re-check, triggered by a duplicate stop notice for the same subagent id, found that a run **did** write the artifact afterwards. Corrected facts (Python-verified):

- `strategy/tm109-resource-config-contract.json` — 54581 B, sha256 `9669bc01c49d7aeb11bca9085ae4ce0f1a611f21e287cf788c0bb379e39a8efd`, valid JSON, ends with closing braces (not truncated), `taskId = TM109-STRATEGY-R1`, `verdict = generated`.
- Bound inputs match the manifest exactly: DFT.csv `ce69dce8…1541`, schematic-ir.json `35fdd158…7ff5`; also binds the five upstream deliverables and the manifest by hash.
- Selection recorded: VAC2 stimulus via ACM200 S5 ch0 (FH0 force + SH0 sense) with closure `{K19_VAC2, K70_VAC_F}`; VBAT via FXVIe_PLUS S3 ch5; relays actuated by this contract = `[19, 70]`. INT endpoint recorded with candidate tables only — no observing instrument fixed.
- `handoff.nextRole = test-method-expert`, `handoff.blockingItems = []` (empty), `gateSatisfied` recorded ⇒ the `deliverable_ready` handoff to `test-method-expert` (ROLE_ROUTING.md:44) is satisfied by the artifact itself.
- Registered and carried, not resolved: 7 conflicts (`C-01`…`C-07`, one `high`: `C-04` knowledge-layer relay names absent from the frozen DALI relay table) and 13 open items (`TM109-OI-2…5`, `OI-S-01…09`), all listed as non-blocking, with an explicit `returnRule` back to this role if the method needs a resource, relay state or register configuration the contract does not contain.

**Corrected state: strategy stage COMPLETE. `test-method-expert` is now the only eligible downstream role.** It has not been dispatched — the Captain holds for an explicit user trigger.

Sequence note: `test-strategy-architect` starts only after `dft-expert`'s post-ruling `deliverable_ready` for TM109.

## Round-1 false-negative evidence (retained, not deleted)

- `schematic/error-log-tm109-schematic.json`
- `dft/dft-error-log.json`

## Captain verification of TM109-SCHEMATIC (independent of the role's self-check)

- `derivation.sourceSha256` = `derivation.sourceSha256Declared` = declared freeze hash = `true`
- `parserGateStatus` = `PASS`; `validationStatus` = `PASS`
- Artifact is valid JSON; top-level structure present (`nets`, `dutPins`, `candidatePaths`, `connectivityContracts`, `counts`, `hazards`, `openQuestions`).

## Open items (not dispatched — no additional specialists created)

1. **Strategy architect (test-strategy-architect)**: NOT dispatched — its documented start gate is unmet. Both derived outputs are gate-`ready` and the manifest is `READY`, but the start matrix requires `dft-expert` **and** `schematic-expert` `deliverable_ready` events for the same TM (`TEAM_ARCHITECTURE_V2.md:804`, `ROLE_ROUTING.md:43`). `dft-expert` deliberately withheld its `deliverable_ready`: its artifact records `handoff.nextRole = test-strategy-architect` with `handoff.blockingItems = ["TM109-OI-1"]` and the note that the Commander must obtain a ruling before a route is committed. The Captain does not fabricate the missing handoff. Runtime state is **BLOCKED** pending one user ruling (`ROLE_ROUTING.md:53`, `TEAM_ARCHITECTURE_V2.md:814`: a conflicting input is a blocking error, the runtime must not choose between conflicting facts and must not continue downstream until the user rules).
2. **TM109-OI-1 (registered by dft-expert, severity: blocking-for-downstream, NOT resolved by the Captain)**: the single TM109 row has `ShortName` = `VAC2_PRST` while its `Dynamic` block drives pin `vac3`; token search finds `vac2` in no record and `vac3` in TM109/TM110/TM624, and TM109's Dynamic block is character-identical to TM110's. `DFT.csv` contains no pin cross-reference table. The strategy architect must not commit a route or endpoint until this is ruled on. Registered in `dft/dft-meta.json` (OI-1…OI-5, where OI-2…OI-5 are non-blocking).
2. **Formal project delivery reports** (`project/DALI/SCH-Connect-Map.txt`, `Component-Statistic.txt` per the IR `deliveryContract.reportOrder`): NOT written by this trial; the dispatch named one output path only. Separate decision, not a gap in TM109-SCHEMATIC.
3. `perTmPinBinding` = UNKNOWN(UNSPECIFIED) for TM109 in the frozen IR — the schematic artifact is TM-agnostic hardware fact; it binds no pin/path to TM109. The DFT side and the strategy architect must not assume otherwise.
