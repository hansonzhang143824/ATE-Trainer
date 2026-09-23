# CHANGELOG — compile-diagnostician

## draft v1 (2026-09-20)

- Initial master profile from `team/roles/compile-diagnostician.md` (third batch).
- Boundary: read reviewed implementation evidence and the approved VS project
  files needed for the build; write only the trial compile directory and the
  diagnostician error log.
- Bounded command: only `python scripts/run_ptc_incremental_compile.py
  --project ... --source ... --report ...` (incremental, Both configurations,
  10-second cap). No manual IDE builds.
- Current-source binding: build-report sourceSha256 must come from the build
  just run; stale builds cannot be reused after implementation changes.
- FAST_DELIVERY_PENDING_AUDIT: compile may begin on that batch state but the
  batch stays PENDING_AUDIT until the deferred implementation review; never
  labelled COMPLETE.
- Golden case TM106 grounded in the real regression compile evidence.
