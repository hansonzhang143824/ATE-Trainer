# ATE PTC Direct Runtime

`team/ptc/ptc_stage_registry.json` is the only authority for PTC stage, owner, gate and test family. Legacy Skills and state machines are reference material only.

## Global hash contract

1. Every PTC agent and deterministic gate uses SHA-256 only. A digest is always
   the lowercase 64-character hexadecimal representation; no other hash
   algorithm or casing is accepted.
2. Canonical input materials protected by DLP are hashed through Python's
   plaintext view with `scripts/hash_ate_plaintext.py`. Never use
   `Get-FileHash`, `certutil`, PowerShell byte readers, Node byte readers, or a
   model-computed value for those inputs because they may see the protected
   wrapper rather than the plaintext material.
3. Generated artifacts are hashed over their exact on-disk bytes, with no text
   decoding, newline normalization, JSON canonicalization, or reserialization.
   The deterministic producer or gate owns this calculation and must print or
   record the digest. Agents copy that value; they do not choose a hashing
   implementation.
4. A semantic review binds only the final artifacts it reviewed. The review
   file never hashes itself. Any later artifact write invalidates the binding
   and requires regeneration of the digest and review before the gate runs.
5. Hash provenance is fail-closed: if the approved deterministic command did
   not produce the digest, report the item as blocked. Do not improvise another
   command, algorithm, byte view, or manually transcribed digest.

## DFT overwrite regression

1. A request for a TM uses the shared delivery directory
   `project/DALI/Output_Global_Material/dft/<TM>/` and is explicitly an
   overwrite regression, not an isolated output copy.
2. Compute the current canonical DFT workbook plaintext SHA-256, then run the
   DFT output gate before any write. If all three products exist, the gate is
   `ready`, its canonical input digest equals the current workbook digest, and
   the semantic-review artifact hashes match the current bytes, report
   `UNCHANGED` and write nothing.
3. If any product is absent, generate the complete three-product set. If any
   source digest, artifact digest, source coverage, condition field, or review
   binding differs, regenerate and overwrite the complete set, bind the new
   hashes, and rerun the gate. Never patch or preserve only part of a stale set.
4. A successful terminal `DONE` report must include `mode=CREATED`,
   `mode=UNCHANGED`, or `mode=OVERWRITTEN`, plus the canonical source digest and
   final gate result. These are modes inside the existing DONE ABI, not new
   terminal report types.
5. The published dispatcher runs the read-only DFT gate before starting a model.
   A ready set returns `UNCHANGED` without a child model. Batch receipts and the
   host's source-terminal record are bookkeeping; the three DFT artifacts are
   untouched. No specialist verification file or error log is written on reuse.

## PTC execution time limits

1. A deterministic command has a 30-second budget. On timeout, cancel it and
   report the exact command and evidence; do not silently wait indefinitely.
2. The same error may be retried once only, and only after changing the stated
   cause. A repeated identical failure is immediately `BLOCKED`.
3. A specialist must not spend more than 60 consecutive seconds reasoning
   without a tool call or a terminal report. At that point it reports the
   current step and concrete blocker instead of continuing to speculate.
4. DFT delivery targets five minutes and has an eight-minute hard stop. At the
   hard stop the specialist emits `BLOCKED` with the last completed command and
   does no more work. Captain does not auto-retry or advance the batch.
5. The dispatcher enforces the eight-minute deadline with a retained abort
   controller connected to the DSH child lifecycle. Prompt instructions alone
   are not the deadline enforcement mechanism.

## Captain entry

1. Classify the request with `team/ptc/CAPTAIN_ENTRY_FLOW.md`. Ordinary conversation is answered directly; expert optimization changes the named role and its checks. A project-delivery request starts a new delivery.
2. Semiconductor preprocessing runs before any write-function / invoke-command / run-test action, and whenever a session starts or Captain is invoked. Captain outputs and maintains four project facts: input location, document list (the three input classes), output location, and the VS project location. Confirmation rules: already confirmed in this session → reuse silently; new session → show the last cached configuration (`team/ptc/.captain-project-cache.json`, seeded from the approved `Project_Info.json`) for confirmation; user says it is wrong → correct it and overwrite the cache; user explicitly asks for a reset → re-run full identification.
3. Document identification: read every candidate document under the input location and classify each as one of schematic / DFT / CBIT table / unknown. Schematic: CSV with PORT, pin, Capo, KELVIN keywords and electrical-connectivity content. DFT: Excel/CSV with test-item names, test conditions, expected values, register configuration, and VSET power-on commands (strongest DFT signal). CBIT table: board names like S30_ACM200_FH, Cbit numbers, or a filename containing Cbit (strong exclusion: schematic and DFT documents contain no Cbit information). Deterministic rules decide first; only conflicting or weak signals go to model reasoning inside the session. Present the classification plus the four project facts to the user for confirmation, then pass the confirmed document-type mapping to the INPUT_SYNC specialists as the pre-judgment for their parsing.
4. In a new ATE Captain conversation, the user only names test items or a range, for example “TM102、TM105” or “TM106 到 TM110”. Captain confirms the current `Project_Info.json` when needed, then internally calls `scripts/captain_delivery_entry.py`. The user never supplies a batch id or runs a Python command.
5. Captain reads only that entry’s JSON. It automatically creates a unique batch, binds the approved project configuration, runs INPUT_SYNC, and returns the one role or source-role list to dispatch. A range includes only DFT items that exist; an explicitly named missing TM is reported in one short sentence.
6. After a role’s terminal report, Captain internally calls `advance_batch(batchId)`. It refreshes INPUT_SYNC manifests when source roles finish, then returns the next whole-batch stage. Every dispatch carries all TMs waiting at that stage.
7. The normal Captain batch uses fast delivery after every TM reaches `RULE_REVIEW_IMPLEMENTATION`. It still enforces the input boundary, hash binding, minimum implementation verification and compile. It becomes `FAST_DELIVERY_PENDING_AUDIT`; it is not COMPLETE. Captain never resumes the independent audit on its own. Resume only when the user later asks for it explicitly.
8. On a real block, report the one short cause and stop. Do not alter paths, source hashes, electrical values or sources to work around it.
9. An explicit "只执行 DFT expert" request records `executionScope` in the batch:
   only `dft-expert` is dispatched and `stopAfter=INPUT_SYNC`. Do not call
   `advance_batch` after its terminal result. The entry also rejects downstream
   continuation for that scoped batch. Use a new request/batch for more stages.

## Boundaries

- Parsing roles read only `project/DALI/Input_GlobalMaterial` and write only `project/DALI/Output_Global_Material` or `project/DALI/ErrorLog`.
- Strategy, method, review, implementation and compile roles read their signed contracts, validated parsing products and the approved VS project.
- The stage chain remains `INPUT_SYNC -> STRATEGY -> METHOD -> RULE_REVIEW_METHOD -> IMPLEMENTATION -> RULE_REVIEW_IMPLEMENTATION -> COMPILE -> COMPLETE`.
