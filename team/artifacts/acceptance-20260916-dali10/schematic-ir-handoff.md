# schematic-ir handoff (independent re-parse, run acceptance-20260916-dali10)

Owner: schematic-expert (this session, independent round).
Inputs pinned: `project/DALI/Dali-SCH.csv` = 307157 B / `04b540f83fa00268cb45d118e9229474cc393a87c8af5caf27a2a8ac8188120a`

## Pipeline (executed this round, isolated out-dir)
- adapter exit=0
- pathproof exit=0

## Counts (fresh)
```
{"sources": 112, "raw_best_paths": 1004, "accepted_path_proofs": 669, "rejected_paths": 335, "kelvin_pairs": 219, "kelvin_pair_failures": 0}
```

## Coverage
- distinct DUT pins with accepted proofs: 135
- distinct sources: 97
- distinct relays used on accepted paths: 101
- nets derived: 123 | IR paths: 232

## Checks
- [PASS] pathproof_status — status=PASS
- [PASS] pathproof_issues_empty — issues=0
- [PASS] parser_gate_pass — parser_gate_status=PASS status=PASS
- [PASS] contracts_all_true — {"dut_pin_is_terminal": true, "kelvin_force_sense_no_cross": true, "shared_relay_state_must_match": true, "cbit_traceability_required": true}
- [PASS] kelvin_pair_failures_zero — failures=0 pairs=219
- [PASS] cited_hashes_stable — mismatched=none
- [PASS] cbit_traceability — unmapped=0 []
- [PASS] counts_consistency — accepted=669 rejected=335 pairs=219
- [PASS] accepted_have_terminal_stop — proofs_without_terminal_stop=0
- [PASS] determinism_vs_canonical — CSV_CONNECTIVITY.NET=True; SCH-Connect-Map.txt=True; Component-Statistic.txt=True

## Open / unspecified
- No relay contact current rating is published in this workspace for the 1A loops (realisable 1A depends on unpinned relay/hardware data).
- Sense-path series resistance (10kohm Kelvin rows) versus the FPVIe sense input impedance is not documented here.
- Whether FPVIe0 low and FPVIe1 low may both sit on the same SW node is not provable from the netlist alone.
- Source type of S10_CH0_A/B is inferred from the slot name and still needs user confirmation.
- K84_HG2 default-conducting FXVIe_PLUS route to PMID: whether it must be opened when FPVIe owns PMID is not stated.
- No discharge role is published by the current StdAfx.h; the realisable mechanism is Cap relay plus 1kohm bleed.
- Committed intermediates carry stale absolute paths / a different recorded CSV sha; provenance regeneration is still open.
- K90_PC0_Force NC cross-path: a formal cross-path exclusion proof for standard FPVIe routing is still open.
- The sanctioned compliance/range triple for the 1A force is not specified in the parsed inputs.
- Loop orientation (which terminal is HIGH) is a strategy decision, not derivable from the netlist.
- OPPORTUNITY: many more accepted paths exist than the scope pins; no pin selection was performed here.
- OPPORTUNITY: rejected paths were not re-classified by reason beyond the engine's own labels.
- OPPORTUNITY: cross-site (_S1S2) relay arbitration for simultaneous multi-site execution was not modelled.
- UNKNOWN(UNSPECIFIED): the exact 1004-raw-to-669-accepted acceptance semantics beyond the four contracts.

## CodexDebug / devel
- Not modified by this round (only read for channel/relay definitions).
