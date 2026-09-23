# PTC Execution Authority

ATE Captain is the only user entry for DALI PTC delivery. The user opens a Captain conversation and names TM items or one range. Captain internally uses `scripts/captain_delivery_entry.py`, the stage registry, and `scripts/ate_ptc_batch_runner.py`; it does not ask the user to provide a batch id or run commands.

`team/ptc/ptc_stage_registry.json` is the sole stage, owner, gate and test-family authority. Legacy Skills, agent maps and state machines cannot dispatch an agent or override a registered gate.

The stage chain is:

`INPUT_SYNC -> STRATEGY -> METHOD -> RULE_REVIEW_METHOD -> IMPLEMENTATION -> RULE_REVIEW_IMPLEMENTATION -> COMPILE -> COMPLETE`

Each new Captain batch defaults to fast delivery only after all TMs reach implementation review. It remains batch-scoped, retains input boundary enforcement, hash binding, minimum implementation verification and compile, and records `FAST_DELIVERY_PENDING_AUDIT`. Captain never resumes strict audit automatically; it does so only after a later explicit user instruction. No role gains global permissions.
