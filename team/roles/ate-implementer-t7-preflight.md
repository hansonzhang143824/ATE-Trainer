# t7 implementation preflight override

Before any source write, create preflight-capability.json and run:

    python scripts/verify_t7_preflight.py <preflight-capability.json>

The artifact must hash the signed method contract and every target source. Map each requested code side effect to actual symbols in frozen target sources or compiler-reachable SDK headers.

- A header outside the project source tree may be listed in apiSources only when the VS project supplies compilerIncludeEvidence for that header's include directory. Path, plaintext SHA-256, role, and compiler evidence are mandatory.
- An SDK declaration proves only that the method exists. A relay or source readback marked supported must set requiresSemanticMapping: true and include semanticMapping with API symbol, relay bank/bit mapping, source readback method, and concrete evidence for all three.
- If the SDK declaration exists but its mapping or source readback semantics are absent, leave the requirement blocked. Do not infer a mapping from a relay number or method name.
- Exit 0: all requirements are supported; t7 may write source once.
- Exit 2: an unsupported requirement; t7 returns BLOCKED and does not write source.
- Exit 1: malformed or stale evidence; repair evidence only.

A task book assertion is not proof. contractEvidence must cite the signed method contract; any claim absent from that contract is excluded from source edits and reported as an input defect.
