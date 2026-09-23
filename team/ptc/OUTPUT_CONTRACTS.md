# PTC Gate Output Contracts

This is the shared deterministic output ABI for the PTC runner. A role must use the exact pathname and JSON fields listed for its active stage. A terminal DONE is valid only after these files exist and pass the listed structure.

## STRATEGY / test-strategy-architect

For TM <tm> write:
- strategy/<tm-lower>-resource-config-contract.json
- strategy/deliverable-ready.json
- strategy/self-check.json

The strategy contract requires verdict = deliverable_ready; one resourceAllocation row per endpoint, i.e. exactly the set canonicalInputs.dft.declaredPins (the pins the DFT row declares) union {the contract's own pinResolution.physicalDutPin}; each row has selectionState = SELECTED and a nonempty sourceTable; resourceSummary.sourceTablesUnresolved = false. Validate with `python scripts/validate_strategy_contract.py <contract> <handoff> --expected-monitor <monitorDutPin> --manifest <trial>/input-manifest.json`.

Each `resourceAllocation` must also carry an `evidenceChain` with locators for the DFT endpoint, source-table definition, schematic route, relay definition, and register configuration. If its source port is not present in its selected path, `interconnectLocator` is mandatory and must identify the document that proves the connection.

strategy/deliverable-ready.json requires event = deliverable_ready, status = success, stage = STRATEGY, verdict = deliverable_ready, sha256 equal to the byte SHA-256 of the strategy contract, and nextRole = test-method-expert. A routed correction must add the finding id to top-level resolvedFindings and must be validated with --expected-monitor using that same input decision.


### Logical signal / physical pin binding

Before a strategy resource allocation is valid, every DFT monitor/check label must be bound to exactly one physical DUT pin listed by the trial Components-Statistic output. pinResolution records logicalSignal, physicalDutPin, resolutionState, componentsStatisticLocator, and mappingEvidence; monitorDutPin equals that physicalDutPin. A DFT label absent from the DUT-pin list is a logical signal, not permission to select a similarly named route. No unique mapping means BLOCKED with one user question before source or relay allocation.

## METHOD / test-method-expert

For TM <tm> write:
- method/<tm-lower>-test-method-contract.json
- method/deliverable-ready.json
- method/self-check.json

The handoff requires event = deliverable_ready, status = success, stage = METHOD, and verdict = deliverable_ready.

For a scanning method, `measurementPlan.scanRangeResolution` is required. It records the `ExpectValue` prediction when present, the `vset` candidate, the explicit Notes candidate when present, the selected range, and the deterministic selection reason from the Method Expert scan-range rule. It must not introduce numeric acceptance limits or tolerance.

## RULE_REVIEW_METHOD / rule-reviewer

Write:
- review/method-contract-review.json
- review/method-contract-review-deliverable-ready.json
- review/method-contract-review-self-check.json

The handoff requires event = deliverable_ready, status = success, stage = RULE_REVIEW_METHOD, and verdict = deliverable_ready.

## IMPLEMENTATION / ate-implementer

The signed METHOD contract is the executable source for this stage. Before implementation dispatch, Hook derives and hashes an `implementationRecipe` from it: source tables, functional relays, a mandatory 3 ms relay-settle, ordered register writes, measurement/scan/Trim recipe and zero-before-off shutdown. The descriptor contains the exact METHOD contract path, its byte SHA-256 and that recipe. A descriptor with a stale hash, altered recipe or missing mandatory field is rejected before an implementer can read or write. It is not valid to recover a missing field from an older trial or status file.

Write:
- implementation/implementation-manifest.json
- implementation/deliverable-ready.json
- implementation/self-check.json

The handoff requires event = deliverable_ready, status = success, stage = IMPLEMENTATION, and verdict = deliverable_ready. Generate it only with `python scripts/write_implementation_deliverable.py <trial...>` after `verify_implementation_batch.py` passes; it binds the implementation manifest hash, current source hash, and signed method input.

## RULE_REVIEW_IMPLEMENTATION / rule-reviewer

Write:
- review/implementation-review.json
- review/implementation-review-deliverable-ready.json
- review/implementation-review-self-check.json

The handoff requires event = deliverable_ready, status = success, stage = RULE_REVIEW_IMPLEMENTATION, and verdict = deliverable_ready.

## COMPILE / compile-diagnostician

Write:
- compile/build-report.json
- compile/deliverable-ready.json
- compile/self-check.json

The handoff requires event = deliverable_ready, status = success, stage = COMPILE, and verdict = deliverable_ready.

The eight-step `relayDesignWorkflow` is an optional audit trace of route selection, not a per-step acceptance gate. Final relay acceptance checks source-to-PIN connectivity, validated Force and Sense paths, no simultaneous ON/OFF requirement for the same CBIT across Force and Sense, no simultaneous use of the same end of one source-table channel by two different PINs, and inclusion of applicable functional relays. Keep source-hash, manifest, and artifact-integrity validation.

The top-level `classification` is mandatory before resource allocation. It contains `projectType` and `parameterType`; each has `value`, a `flowLocator` into `knowledge/standards/test-types.md`, an `indexLocator` into its matching index (`func_type_index.md` or `param_type_index.md`), and an `evidenceLocator` into the signed DFT/schematic facts.

Every selected resource must contain `physicalProofs[]` drawn from formal `Path-Proofs.json`. Each entry states the exact source port, DUT Force/Sense terminal, required-on relay numbers, and locator. The strategy gate compares each entry and its union against the canonical accepted proof.


### Register configuration contract
A strategy contract for a TM with Code2 field declarations requires top-level registerConfiguration. It records evidencePath, evidenceSha256, sourcePath, and orderedWrites from strategy/register-config-evidence.json. The evidence must prove matching TM header and matching DFT Code2 fields. Implementation uses render_register_writes.py to copy only orderedWrites.sourceText verbatim.

Method contracts require signedInputs.strategyContractSha256. Method reviews require signedInputs.methodContractSha256. The runner treats a missing or mismatched hash as stale and returns to that stage.
\nMethod completeness is checked by validate_method_contract.py: current strategy hash, resourceBoundary, methodPhases, measurementPlan with scanRangeResolution, and powerDownPlan are mandatory.\n
Implementation reviews require signedInputs.implementationManifestSha256. The runner treats a missing or mismatched hash as stale and returns to implementation review.

Compile reports require source and sourceSha256 matching the current test.cpp. The runner treats an older build record as stale.


### DFT interpretation handoff

The DFT output pair is the signed test-condition contract. It preserves raw OVERVIEW fields and records interpreted static supply, dynamic sweep, test-mode/register-field intent, logical monitor, result types, timing, and source contradictions. Strategy consumes this interpretation and does not redefine test-condition meaning; it only selects physical resources and verified implementation mappings.


DFT testCondition requires isTrim, staticPower, hasRamp, ramps, dynamicPins, highCurrent, differentialVoltage, involvedPins, measurement, registerFieldIntent, referenceValue, and notes. Use NOT_DECLARED where the OVERVIEW row does not declare a feature; do not invent it.


DFT output exposes projectId, TM number, parameter name, level, description, purpose, unit, remarks, and expected value both as readable testCondition fields and in full rawIntent.

DFT semantic-review gate: after deterministic extraction, dft-semantic-review.json is mandatory. It must have verdict PASS, bind the canonical workbook plaintext hash from scripts/hash_ate_plaintext.py, declare that source inside Input_GlobalMaterial, and bind the byte hashes of the current dft-meta.json and dft-conditions.yaml. The Hook permits a DFT expert to read those products only inside its exact assigned TM output folders for this self-check; it does not permit reading another TM, a trial folder, old parsing products, or engineering files. Without this review the DFT gate is stale.

METHOD review batch gate: `scripts/review_method_batch.py` is the deterministic acceptance pass. It is contract-driven: methodFamily=direct_measurement requires the signed direct-measurement result and shutdown requirements; methodFamily=scan requires only its signed sweeps, scan results, and shutdown requirements. No gate may impose another TM's voltage range, trigger pair, or result count. An LLM reviews only the script's FAIL report. `--write-pass` writes handoffs only with already-recorded user authorization to advance. A trim METHOD contract must additionally declare the active .treg path/hash/key, target mV, step count, and EFUSE register-bit mapping; it must declare the compiled sub.cpp callback and mV result unit. The Trim gate verifies these facts against the active .treg and callback before accepting the method.

## Per-batch fast delivery (Captain default)

Every batch created through a new ATE Captain delivery conversation records fast delivery as its default delivery policy. Captain can activate it only when every selected TM has reached `RULE_REVIEW_IMPLEMENTATION`; it cannot skip INPUT_SYNC, strategy, method, method review or implementation.

The activation is internal to Captain. It preserves input-boundary Hook enforcement, signed input and source hashes, the current implementation manifest, minimum implementation checks and real compile. It records `FAST_DELIVERY_PENDING_AUDIT`, gate configuration hashes and the skipped implementation-review stage in that batch’s record. It never grants a global role or tool permission.

Captain never resumes strict audit automatically. Only a later explicit user request may authorize Captain to resume the pending independent review for that exact batch. Resume validates the recorded gate configuration and begins at the deferred review without repeating completed stages.


Captain internal resume operation is `--resume-audit --batch <id>`. It is not a user command and Captain invokes it only after the user explicitly requests strict audit restoration.
## Trim evidence hard gate

For every Trim item, the implementation manifest must contain `trimCompliance`. It records the exact SHA-256 of `knowledge/standards/treg.md`, `TM130_Trim_VBG.md`, and `sub-measure-template.md`, plus a `PASS` record for the current `scripts/ptc_trim_validation.py`. `verify_implementation_batch.py` recomputes every hash and independently validates the active `.treg`, `sub.cpp` callback, and `test.cpp` `execute` binding. Missing, altered, stale, or failed evidence rejects the item before compile.
