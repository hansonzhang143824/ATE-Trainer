# TM109 implementation - role self-check (ate-implementer)

- taskId: TM109-IMPLEMENTATION
- tm: TM109 / projectId: DALI / stage: IMPLEMENTATION
- verdict: **BLOCKED** (no source written)
- generatedAt: 2026-09-18 00:32:38 +08:00

## What was verified before any source write

| # | Check | Command / reader | Result |
|---|-------|------------------|--------|
| SC-01 | signed method contract hash | `python -c hashlib.sha256(Path.read_bytes())` | d9d7e10f9dc96730695a97a7e2b59b235987b3745689a3eaccc738a893000459 - matches method/deliverable-ready.json |
| SC-02 | signed strategy contract hash | same | a22502ece50f321312a466b77cfef5a40efe8f9a41995f7ee8af3b44048107e2 - matches strategy/deliverable-ready.json |
| SC-03 | method rule-review artifact hash | same | deb628ef4532d29fe06a8431994c8b9a122233e4b8cce9cd0b5a0e2b8c07795f - matches review/method-contract-review-deliverable-ready.json |
| SC-04 | destination project path confirmed | project_config.json `inputs.vs_src_dir`; schematic-ir.json absolute source paths | D:/PROJECT6-DALI/ForCodexDebug/source; item symbol TM109_HSKP_VAC2_PRST present at test.cpp:2323 |
| SC-05 | target source revision | python byte mode | test.cpp 477760 B, sha256 456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa, BOM, 9440 CRLF - identical to the revision the tm108-v2 trial recorded as delivered; no drift |
| SC-06 | usable library API confirmed | grep over the declared *.cpp/*.h scope | VBAT_PD3_FXVI = S3_5 (FXVIe_PLUS S3 ch5), VAC123_AMUX_ACM = S5_0 (ACM200 S5 ch0), PA0_PC3_ACM = S5_15 (ACM200 S5 ch15), K19_ACM0_VAC2 = 19, K70_R5M_VAC_F = 70, entertestmode / I2CWriteSameData / DEV_ADDR, rampv_capv 9th parameter = voltage step, SetOn(-1) = safe empty closure set |
| SC-07 | t7 preflight gate | `python scripts/verify_t7_preflight.py implementation/preflight-capability.json` | **exit 2** - "BLOCKED: 8 requirements; method hash and target hashes verified"; 7 supported, 1 blocked (REQ-08-phase-exit-state-readback) |
| SC-08 | write capability of the designated code scope | .NET write-open of test.cpp; Set-Content into the target dir; harness write tool; controls in workspace and %TEMP% | target file DENIED, new file in target dir DENIED, harness write tool DENIED (`[sandbox: file access denied under workspace-write mode]`), workspace OK, %TEMP% OK; target file ReadOnly attribute = False |
| SC-09 | no relay / register / limit / timing value invented | comparison of the signed boundary against the frozen macro names | no relay selected, no closure amended, no register value changed, no limit or timing substituted |
| SC-10 | write confinement | file-tool and shell history | no file was created, edited or deleted outside team/artifacts/tm109-direct-trial/implementation/; the two write-probe files created inside the session workspace / %TEMP% were removed in the same command |
| SC-11 | downstream roles | - | none started; no helper agent, no AgentTeams, no Goal round, no polling, no retry |

## Why the stage is BLOCKED

**B-1 (hard, session capability).** The designated VS project source is
`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`. This session's file policy is
workspace-write for `D:\Newtest\DSH\ATE-Coding-Plat` only. An existing-file write-open is
denied, creating any new file in that directory is denied, and the harness write tool returns
`[sandbox: file access denied under workspace-write mode]`; approval escalation is disabled for
this session and a delegated subagent cannot widen its own scope. The same operations succeed in
the session workspace and in %TEMP%, so the denial is the sandbox boundary rather than a file
attribute or a project ACL. No byte of the VS project was changed.

**B-2 (signed-scope defect, blocks a faithful write even with write permission).** The signed method
contract requires the item to read back actuation/source state at MP-1 (`.sample`), MP-2 and MP-9
(`.exitCondition`, `orderedActions[5]`) and in `logPlan.rawValues`. No read-back primitive is
reachable in the declared target-source scope: 0 hits for `cbite.GetState`, `cbite.GetOn`,
`cbite.IsOn`, `cbite.GetRelay`, `RelayState`, `RelayStatus`, `GetRelayState`, `ReadRelay`
over every `*.cpp` and `*.h` under `D:/PROJECT6-DALI/ForCodexDebug/source`; the only `cbite`
member reachable there is `SetOn`. This is reported as *not reachable in the declared scope*, not
as a claim about the library, because the `CBITe` class body is outside that scope. Owner:
test-method-expert (method contract), closing source test-strategy-architect or a user ruling.

## Carried conditions (not resolved here)

- RV-03 / MF-04: no numeric tolerance exists for VAC2_PRST_Rise or VAC2_PRST_Hys; the item may
  publish unjudged values with an explicit PENDING_LIMIT_RULING marker only.
- RV-04 / MF-01 / MF-02: the signed RG-1 and RG-3 closures are empty, so the FR-001 VBAT Cap2
  closure is omitted and the INT observation is unproven. Both stay with test-strategy-architect.
  (Observation only, not acted on: `StdAfx.h` carries `#define K13_VBAT_Cap 13` with the comment
  `Cap2_VBAT_S1`, i.e. the VBAT Cap2 identity exists in the project relay-definition source. This
  role did not select it and does not amend the signed closure set.)

## Evidence

- `team/artifacts/tm109-direct-trial/implementation/preflight-capability.json` (sha256 54cead15239f24b3e6866bad32e8e777ed82dc247a0f6383db68acf4031377d7)
- `team/artifacts/tm109-direct-trial/implementation/preflight-blocked.json` (sha256 2d28b44d77451f5b155de19f3f6c0c1484b5bcaba1309dfbff216d57778ac6df)
- `team/artifacts/tm109-direct-trial/implementation/deliverable-ready.json` (status blocked)

## Not tested / residual risk

- nothing was compiled, linked or executed; the compile stage has no artifact to act on
- the preflight symbol scan is scoped to the declared target sources; it does not prove anything
  about the tester SDK headers that are not part of that scope
- the frozen source revision was read but not written, so its hash still equals the pre-task value
