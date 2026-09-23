# backups/ — scratch and snapshot material (read me before running anything here)

## The rule

**Any script in this directory with a hardcoded hash assertion was written to verify a state at the moment it
ran. Those assertions are NOT current.** The clearest example: several scripts assert or print `MATCH` for
`6034af71...` (the t50 UNION revision, 41,797 B), which was written to the canonical payload path at 20:48:18
and superseded at 20:59:12. Running such a script today will report a mismatch — **that mismatch is expected
and is not a defect in the payload.**

They are kept because they are the *receipts* that each revision existed and was verified when written
(rule-reviewer used them that way for the union revision, whose bytes are no longer recoverable). Read them
as a log, not as tests.

## For current verification, use the live gates instead

    python scripts/verify_relay_trace.py --meta --src <sandbox test.cpp> --defines <sandbox StdAfx.h>
    python scripts/verify_bst_sw_sequence.py --src <sandbox test.cpp>
    python scripts/verify_awg_params.py --src <sandbox test.cpp>

State as of this note: canonical payload `implementation-payload-TM600-TM601.cpp` =
43806 B / `66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4` (frozen; no writes since 21:09:24). Contract cited by the value the gate consumes
(`aliasResolution[3].closedRelayNumbers`), not by revision number.

## Ownership note

These scripts were contributed by more than one member during the run. Nothing here was moved, renamed or
edited when this README was added — it is purely an annotation, so no member's scratch state was disturbed.

Written by ate-implementer.
