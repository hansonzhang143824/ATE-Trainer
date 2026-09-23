# CHANGELOG — ate-implementer

## draft v1 (2026-09-20)

- Initial master profile from `team/roles/ate-implementer.md` (third batch).
- Boundary: read the signed method contract, strategy evidence, TRIM standards,
  golden reference code and approved target sources; write only the trial
  implementation directory, the implementer error log and the approved target
  source files being implemented.
- Gate: `scripts/verify_implementation_batch.py` driven by each signed method
  contract; deliverable written via `scripts/write_implementation_deliverable.py`.
- Golden case TM106 grounded in the real dali-20260919-145154 implementation
  (implementation-manifest + deliverable-ready).
