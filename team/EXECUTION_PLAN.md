# V2 Execution Plan

1. User selects a TM trial scope.
2. Captain creates run-id and freezes DFT, schematic, Setup and rule hashes.
3. Follow the eight-role delivery DAG in team/ptc/ptc_stage_registry.json.
4. Keep outputs in the new run-id. Do not treat retired context as current fact.
5. Run evolution-expert only after explicit user request and only over closed runs.
