# Changelog — rule-reviewer

## v1 (draft) — 2026-09-20
- Initial draft created from `team/roles/rule-reviewer.md` per the second-batch
  migration plan.
- Covers BOTH review stages (RULE_REVIEW_METHOD and RULE_REVIEW_IMPLEMENTATION);
  profile.yaml declares the METHOD review as primary stage.
- Golden case TM106 established (symbolic `<run>` paths; semantic truth deferred
  to domain input, only the mechanical review gate is asserted).
- Readable roots: the run's strategy / method / implementation outputs (the
  contracts and evidence under review). Writable: the run's own `review/`
  directory only — the reviewed contract is never modified.
