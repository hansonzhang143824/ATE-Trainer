# ATE Lazy Agent Team Runtime

## Purpose

Keep the nine ATE professions and their versioned skills available across projects without paying to start nine model sessions. The Commander is the only coordinator.

## Runtime contract

1. Creating or approving a team creates a roster only. Every member remains `unspawned`.
2. A member is materialized only when the Commander creates an explicitly assigned, dependency-ready task for that role.
3. Each member receives its role charter, one short task notice, and paths to required project artifacts. It reads only the files needed for that task.
4. On success, the member writes artifacts and a terminal task report. It does not wake or brief the next role.
5. On failure, it writes one error log and marks the task failed. No downstream work starts.
6. The Commander reads terminal reports, creates the next task after validation, and on any failure or problem stops immediately and reports it to the user. It never works around the problem and never resolves a conflict on its own.

## Required terminal report

```yaml
status: success | reuse | failed
stage: dft | schematic | strategy | method | implementation | review | build
projectId: <project>
tm: <TM>
outputs:
  - path: <project-relative path>
    sha256: <hash>
verdict: <short result>
error_log: <path> # required only for failed
```

## Initial TM dispatch

For a user command that names a project and TM, the Commander creates only two tasks:

- `dft-expert`: G0 comparison; reuse or regenerate the narrowed DFT scope.
- `schematic-expert`: G1 comparison; reuse or regenerate the narrowed schematic scope and PathProof.

No other role is materialized until the Commander verifies the required terminal reports.
