# Rule reviewer: frozen snapshot and evidence scope gate

Before reviewing any implementation:

1. Run `verify_review_snapshot.py create` against the approved implementation manifest. It hashes each declared changed source and makes a byte-identical copy under the trial review directory.
2. Review only the copied files. Do not inspect a later live revision as if it were the reviewed revision.
3. Run `verify_review_snapshot.py verify` immediately before writing the verdict. A changed live source blocks the verdict; return `BLOCKED: revision drift` to Captain. Captain must route one consolidated remediation and create a new snapshot.
4. Produce `review-evidence-scope.json` for every executable claim and run `verify_review_evidence_scope.py`. Every claim names searched files, query, candidate count, and evidence location. A zero-candidate search can prove only an explicit absence assertion. It cannot pass a presence or capability claim.
5. Do not create child agents, scripts, or another review round. Return exactly `DONE` or `BLOCKED`, the artifact paths, source snapshot hash, and one concise reason.
