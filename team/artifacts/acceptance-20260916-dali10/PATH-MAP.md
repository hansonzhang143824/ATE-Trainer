# Run path map (who carries which task's artifact)

**PATH BASE (added after test-strategy-architect's verification): every path below is relative to the REPOSITORY ROOT `D:/Newtest/DSH/ATE-Coding-Plat`. A path that lives inside the run directory therefore starts with `team/artifacts/acceptance-20260916-dali10/`; `scripts/...` is at the repository root, NOT inside the run directory.`

Written by `setup-architect` because this run produced several false MISSING cases from name/path ambiguity (basename-only searches, and one base-directory mismatch). **Rule: cite by full path + recomputed sha256 at citation time; never cite a remembered hash; state the base of any path list.**

| task / role | artifact (relative to the repository root) |
|---|---|
| `t34` (acceptance report; verdict `blocked`) | `team/artifacts/acceptance-20260916-dali10/acceptance-report.json` — **there is NO file named `t34*`; `t34` is a task label.** Its entries live in that JSON's `limitations[]`. Pointer files: `t34-carrier-pointer.json`, `t34-CARRIER-PATH.md` |
| `t35` | `team/artifacts/acceptance-20260916-dali10/t35-contract-reconciliation.md` |
| `t41` | `team/artifacts/acceptance-20260916-dali10/t41-tm601-bst-path-determination.md` |
| `t49` / `t53` (contract work) | `team/artifacts/acceptance-20260916-dali10/setup-contract-build.py` (generator) |
| contract | `team/artifacts/acceptance-20260916-dali10/setup-contract.json` (+ `setup-contract-pin.json`) |
| plan side | `team/artifacts/acceptance-20260916-dali10/test-plan.json` (owner: test-strategy-architect) + `team/artifacts/acceptance-20260916-dali10/implementation-input-pin.json` (owner: setup-architect) |
| payload (canonical, writes stopped) | `team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp` |
| anchors | `team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-anchors.json` (owner: setup-architect) / `team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json` (owner: compile-diagnostician) |
| snapshot ledgers | `team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-freeze-snapshots.json` (owner: setup-architect, append-only) / `team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.snapshots.jsonl` (owner: compile-diagnostician) |
| peer ledger metadata | `team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.snapshots.meta.json` (CORRECTED: an earlier revision of this table said `t28-anchors.snapshots.json`, which does not exist) |
| gate script / baseline | `scripts/verify_bst_sw_sequence.py` (**repository root**) / `scripts/gate_baseline.json` (28 B, untouched) |

**Gate-read field** (the only contract field the bst-sw gate consumes):
`team/artifacts/acceptance-20260916-dali10/setup-contract.json` → `aliasResolution[bst2sw].resolution.closedRelayNumbers` = `[48, 60, 61, 76]`,
which yields the TM600 expectation `[48, 60, 61, 76, 83]`.

**Frozen vs live (as declared by the owning side):** FROZEN = `setup-contract.json`, `setup-contract-build.py`, `setup-contract-pin.json`, and the canonical payload. Everything else (reports, `t35`, `t41`, pins, anchors, ledgers, the plan) is a **live file** — cite with a timestamp, never with a bare hash.
