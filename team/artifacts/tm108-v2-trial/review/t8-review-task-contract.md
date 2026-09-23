# t8 task contract — TM108 independent rule review (rule-reviewer)

**Task id:** `t8`
**Role:** `rule-reviewer`
**Run:** `tm108-v2-impl`
**Depends on:** `t7` (ate-implementer) reaching `DONE`.
**Status:** prepared while `t7` runs; dispatch only after `t7` reports `DONE`.

## 1. Trigger and authority

- Under `ROLE_ROUTING.md` the automatic trigger for `rule-reviewer` is an `ate-implementer`
  `deliverable_ready`. That notification is expected from `t7`; if `t7` reports `DONE` without it,
  this user-triggered contract is the substitute (`ROLE_ROUTING.md:39`).
- User ruling (current) > signed resource/config contract (I1/I2) > signed method contract (I3/I4) >
  active standards > golden > experience. The **implemented function is not an authority**
  (`tm108-test-method-contract.md:664`).

## 2. Reviewed inputs

| # | Path | Note |
|---|---|---|
| R1 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` | sha256 `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4` |
| R2 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.json` | sha256 `FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9` |
| R3 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.md` | sha256 `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7` |
| R4 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.json` | sha256 `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21` |
| R5 | `team/artifacts/tm108-v2-trial/method/bst-sw-phase-check.md` | sha256 `FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54` |
| R6 | `team/artifacts/tm108-v2-trial/implementation/implementation-manifest.json` | `t7` output, `runId="tm108-v2-impl"` |
| R7 | `team/artifacts/tm108-v2-trial/implementation/t7-selfcheck.md` | `t7` output |
| R8 | `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` | the changed artifact (and `sub.cpp` only if `t7` touched it) |
| R9 | the `t7` backup file recorded in the manifest `backups[]` | the pre-change snapshot |

Role contract: `team/TEAM_ARCHITECTURE_V2.md`, section `规则审查专家：职业定义草案 V1`
(approximately lines 397-512). Read it before starting.

## 3. Independence rules (hard)

- **Read-only.** The reviewer has no write authority over any reviewed artifact. Do not edit
  `test.cpp`, `sub.cpp`, the manifest or the contracts. Suggested patches belong in the findings
  file, never applied.
- Work on a **copy**: copy the reviewed `test.cpp` (and `sub.cpp` if `t7` touched it) into
  `team/artifacts/tm108-v2-trial/review/copy/` and inspect that copy. Take a plaintext hash snapshot
  of every reviewed target file **before and after** the review and state that they are identical.
  Never write into the target directory.
- DLP trap: read/hash the target C++ files with **python byte mode only**
  (`C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`). pwsh
  `Get-Content`/`Select-String`/`Get-FileHash` and any .NET file API see ciphertext (`TSZ#…`) and
  will produce false absence claims and false "modified" digests. Label every hash `plaintext`.
  Precedent: `team/artifacts/acceptance-20260916-dali10/implementer-recon.md:9-17, :324-350`.
- The reviewer must not resolve, close or relabel any open item, and must not select a side in any
  conflict.

## 4. Required review content

Review the implementation against **R1-R5 only**. At minimum:

1. **Contract conformance** — every source table, channel, path, relay number, functional relay,
   isolation condition, register value, ramp, delay, sample count, range and limit in the changed
   code is traceable to an R1-R5 section or key. Flag any number that appears only in the code.
2. **Phase order** — the implemented sequence matches R3 `methodPhases[]` (9 phases) including the
   power-down steps and the safe end state.
3. **The two known divergences are addressed** — (a) the `DTEST0 == nQON` assumption in the
   function's comment; (b) the `K13` (`K13_VBAT_Cap`) state per R3 `RT-1` (closed at P1, released at
   P8).
   **Corrected instruction for (b):** the captain has refuted `RT-1`'s premise —
   `captain-precheck/rt-1-record-correction.md`. R1 requires `K13_VBAT_Cap` closed (md `:221`, `:245`,
   `:313`; json `relayGroups[G3].functionalRelays`) and R1's keep-open list **does not contain 13**
   (md `:248`; json `resourceSummary.keepOpenRelayNumbers` — both the same 16 numbers), so R1 and R3
   **agree** and there is no inconsistency to surface. Verify the implemented K13 state against R1
   and R3 directly, and do **not** fail the implementation for omitting a non-existent
   inconsistency. If you find byte-level R1 text listing `13` as keep-open, say so with the exact
   line — that would withdraw the correction.
4. **Open items carried, not decided** — `OI-T4-01`, `OI-T5-01`, `OI-T5-02`/`RT-2`, `RT-1`, `RT-4`,
   F1-F6, `OI-T4-10/11/12/13/14/16` appear as unresolved in the manifest/self-check and are not used
   as settled facts in the code.
5. **No BST/SW driving action was added** (R3 states the constraint is unproven in all 9 phases).
6. **Signature and scope** — `DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)`
   unchanged; no TM other than TM108 touched; no unrelated hunks.
7. **File integrity and hash binding** — UTF-8 BOM present, CRLF count preserved, before/after
   plaintext hashes match the manifest, backup is byte-identical to the recorded pre-change hash.
   **The manifest's `changes[].afterSha256` must equal the plaintext hash of the exact file you
   inspected.** A stale manifest is a **blocking** finding, not a formality: the deliverable is the
   hash-bound pair (code + manifest), and a manifest that names a different revision than the file on
   disk cannot be reviewed as one artifact. Verify the binding yourself with the python plaintext
   reader; do not accept the manifest's own statement.
8. **Geometry check** — where R3 states a measurement/integration concern (for example the 1 A
   `iset` per `RT-4`'s neighbourhood, the 1.65 V capture level registered as `OI-T5-03`), verify the
   code states the contract's provenance rather than asserting it as a DFT fact.

### 4b. Captain-flagged check items (from the independent pre-change image)

These come from the captain's own read of the **pre-change** function, before `t7` edited anything.
Pre-change image: `team/artifacts/tm108-v2-trial/captain-precheck/tm108-block-before.txt`
(function `test.cpp:2155-2225`, extracted `:2147-2227`, block sha256 `19fe6b5c7770e8f0…`); machine
record `.../captain-precheck/tm108-divergence-sites-before.json`. They are **checks, not verdicts** —
verify each against R1-R5 and against the *current* file, and judge the latest implementation only.

| # | Pre-change site | Why it is flagged | What to determine |
|---|---|---|---|
| C1 | `:2152` — comment `measure V(DTEST0)=nQON toggle` | asserts the `DTEST0 == nQON` identity that R3 forbids adopting | is the assertion gone or explicitly re-worded as pending `OI-T4-01`? |
| C2 | `:2171` — `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` | the closure set {13, 65} matches R1/R3; verify it was not changed and that `K21_VAC_Cap` stays open (pre-change comment `:2169` states the scanned-input exception) | closure set still {13,65}? any relay added to or removed from the `SetOn`? |
| C3 | `:2169` — comment "VAC1 is scanned input, do NOT close K21_VAC_Cap" | matches the R3 cap-gate asymmetry | preserved? |
| C4 | `:2213-2215` — power-down zeroing `VAC123_AMUX_ACM.Set(FV,0,ACM200_10V,ACM200_10MA,ACM200_RELAY_OFF)`, `VBAT_PD3_FXVI.Set(FV,0,FXVIe_PLUS_10V,FXVIe_PLUS_10MA,FXVIe_PLUS_RELAY_OFF)`, `NQON_HG1_ACM.Set(FV,0,ACM200_10V,ACM200_10MA,ACM200_RELAY_OFF)` | R3 P4 states `ACM200_100MA` / `FXVIe_PLUS_100MA` and observation `ACM200_10UA`, while R3 P7 states "range/limit held as in P4"; the pre-change teardown used **different** limits (10MA) and collapses P7/P8 | does the current code match R3's per-phase values for every phase, and for the power-down steps in particular? if it deviates, is that a code finding (→ `ate-implementer`) or a contract wording gap (→ `test-method-expert`)? |
| C5 | `:2189, :2193` — hard-coded `1.65V` capture level | registered as `OI-T5-03` (method-side provenance, not a DFT fact) | does the code (or its comment) present the level with its provenance instead of as a DFT fact? |
| C6 | `:2163-2165, :2220-2222` — `SetTestResult(site, 0, …)` only | confirms the pass/fail application is spec-side, so `RT-4` (missing tolerance) is not a code artifact | confirm no tolerance, guard band or limit literal was **added** by `t7`, and that `RT-4` remains carried |

### 4c. Captain refinements after reading the rest of the pre-change function (round 6)

**`C4` in the table above is SUPERSEDED** — the suspicion does not survive the fuller read. Read
together, the pre-change power-down is:

- `:2209-2211` — sub-step 1: `FV=0` with `RELAY_ON`, at exactly the P4 range/limit pairs
  (`ACM200_20V/ACM200_100MA`, `FXVIe_PLUS_10V/FXVIe_PLUS_100MA`, `ACM200_10V/ACM200_10UA`). This
  **matches R3 P7** ("FV=0, range/limit held as in P4, relay still ON").
- `:2213-2215` — sub-step 2: `FV=0` with `RELAY_OFF`, at `…_10MA`. R3 states **no** range/limit for
  this sub-step, so the `10MA` difference is not a deviation from anything R3 says.

So: verify the current code keeps sub-step 1 at the P4 pairs, and treat sub-step 2's ranges as
unconstrained by R3 unless R3 does state them. Do not raise a finding on the `10MA` alone.

**`C7` (new) — the signed closure set is never explicitly released in code, project-wide.**
Measured in the pre-change `test.cpp`: **103** occurrences of `cbite.SetOn` and **zero** occurrences
of any `cbite` release/reset call (`SetOff` / `RelayOff` / `Reset` / `Off`). The TM108 function
actuates its closure at `:2171` and has no release call. This is the **whole codebase's** pattern, so
an explicit release is not the project convention and its absence in TM108 must **not** be scored as
an implementation deviation. R3's P8 "release of the signed closure set and the safe end state" is
therefore satisfied either by the framework's per-item relay reset or by the item boundary — the
framework behaviour itself was **not verified in this session (UNKNOWN)** and is not the
implementer's to invent. If the reviewer wants to establish it, the evidence is the test framework /
`compile-diagnostician` territory, not a code finding against `t7`.

**`C9` (new) — the `DTEST0 == nQON` alias is asserted by other TMs; that is not authority.**
A hash-anchored scan of the applied `test.cpp` (`sha256_pl 8498c304…`) finds the equality asserted in
**7 functions outside TM108's scope**: `TM104_HSKP_LP_PTAT_0P5U`, `TM105_HSKP_VSPRE_MAX_CMP`,
`TM106_HSKP_VBUS_PRST`, `TM109_HSKP_VAC2_PRST`, `TM110_HSKP_VAC3_PRST`, `TM111_HSKP_VBAT_UV`,
`TM425_VREF_1P2V_BUF`; the knowledge base carries the alias too. **TM108's own region asserts it
nowhere.** Consequence for the review: codebase-wide usage and the knowledge base must **not** be
treated as evidence that the relation is established, and no change outside TM108 may be requested.
Note also that the sibling items `TM109` (VAC2) and `TM110` (VAC3) are structurally the same test at
the same capture values — close to the untouched TM108 baseline, so treat them as a **convenience
copy risk**, not as corroboration.

**`C10` (new) — the manifest's `deviations[DEV-1]` repeats a refuted claim.**
`implementation-manifest.json` `deviations[DEV-1]` records `RT-1` as a "REPORTED CONTRACT
INCONSISTENCY" and cites "contract md :248, :574", and the code banner at `test.cpp:2186-2187` says
the same. The captain refuted this premise (`captain-precheck/rt-1-record-correction.md`): I1 md
`:248` and I1 json `resourceSummary.keepOpenRelayNumbers` are the same 16 numbers and do **not**
contain 13; I1 requires K13 closed; and I1 md is 441 lines so `:574` is out of range. Determine
whether the owner's correction landed **before or after** the manifest was written, and require the
claim to be removed or re-worded so that no artifact asserts an R1 contradiction that does not
exist. Do not let `DEV-1` stand as a valid deviation.

**Round-11 verbatim quote, so the reviewer does not have to hunt for it.** At the 21:28:38 revision
of `implementation-manifest.json`, `deviations[DEV-1]` still reads (unchanged from the first
revision, even though the *code* banner was corrected at 21:28):

> `"subject": "K13 in the keep-open set of the signed strategy contract (RT-1)"`,
> `"handling": "carried as a REPORTED CONTRACT INCONSISTENCY, not resolved. The strategy contract's G3 states the closure set {13,65} (contract md :224) while resourceSummary.keepOpenRelayNumbers also lists 13 (contract md :248, :574). … RT-1's owner (test-strategy-architect) must issue one authoritative statement."`,
> `"ownerOfResolution": "test-strategy-architect"`

Three separate problems, judge each: (a) the substantive claim is refuted; (b) the **subject line
alone** is a false framing; (c) it routes work to `test-strategy-architect` for a statement that
already exists in R1. Check the revision you actually review — the owner was still running when this
note was written, so the text may have been corrected by then.

**`C11` (new) — `DEV-3`: the method contract's `logPlan` raw context is only in comments.**
The manifest's `deviations[DEV-3]` states that R3 §5 `logPlan` asks for `registerActivationTrace`,
`relayActuationTrace`, `triggerModeRise/Fall`, `captureLevel` and `sweepGeometry` as raw context
(R3 `:541` is the `sweepGeometry` row; `:486` requires the failure context to be recorded rather than
substituted), that the working tree exposes **no** in-TM text-logging primitive other than
`CParam::SetTestResult`, and that the implementer therefore put those quantities in trace comments and
added no invented log call. This is the **most substantive open judgment in the deliverable**. Rule on
it explicitly, and say which way:
- If R3's `logPlan` is genuinely unimplementable with the primitives this tree exposes, that is a
  **contract-vs-capability** finding and belongs to `test-method-expert` (return the need), not a code
  defect to patch silently.
- Independently verify the "no logging primitive exists" claim, and **widen the scope beyond
  `test.cpp`** — the implementer's evidence was scoped to that one file, and "absent from `test.cpp`"
  is not "absent from the project". The captain's own probe of the project source already found
  candidate primitives **outside** `test.cpp` that must be ruled on explicitly:
  - `BoardCheck.h:214 class CBC_log` with `:759 BOOL log(DWORD tnum, const char* component, double* result, double lolim, double hilim, const char* unit);`
    and `:760 BOOL test_log(DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);`
    — a per-item logger that takes a **component string** plus limits and a unit;
  - `treg.h:195 static void log_data(unsigned tnum, unsigned index, double value, int site, bool use_mslogdata, bool allow_mslogdata, …)`
    and `treg.h:176 static int treg_error_log(const char *format, …)` — a printf-style logger;
  - `treg.h:108 typedef void(*log_data_t)(…)` and `:110 typedef void(*test_t)(int tnum, double res, int site, int alarm_log);`
    show the framework has a logging callback concept.
  Decide for each whether it is actually reachable from a TM function and whether R3's `logPlan`
  quantities could be emitted through it. Only if **none** is usable is `DEV-3` a contract-vs-capability
  finding against `test-method-expert`; if one is usable, this is a code finding against
  `ate-implementer` instead. State which, and say what you verified (a scoped claim is not a proof).
Do not accept "it is in the comments" as satisfying a `logPlan` record without saying so as a verdict.

**`C12` (new) — `DEV-2`: K17 closed-state requirement with no actuation call.**
R3 `:199` requires `K17` to be in the closed state and explicitly delegates the **call form** to
`ate-implementer` under `OI-T4-04` ("…no actuation call for K17 is written by this contract
(ate-implementer decides the call form under OI-T4-04)"). The implementer decided the form is "no
call", on the measured evidence that `K17_BUSL_VAC` occurs **0 times** anywhere in the pre-change
`test.cpp` (so no TM actuates relay 17 and the state is inherited). Decide whether that is a valid
exercise of the delegated decision or an unexercised delegation, and whether R1's requirement is
satisfied by inheritance. Do not let the item pass merely because "the contract delegates it" —
state which of the two readings you accept and why.

**Round-17 evidence the captain measured independently (use it; do not re-derive from scratch).**
From the pre-image backup and the live file (python byte mode):

| Fact | Value |
|---|---|
| `K17` occurrences in the **pre-change** file | **0** (the token appears nowhere, in any function) |
| `K17` occurrences after the change | 3 — all inside comments the implementer added (`:2162`, `:2208`, `:2214`) |
| TM108 closure call (pre-change, unchanged) | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)` |
| TM109 (VAC2) closure call | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K19_ACM0_VAC2, -1)` |
| TM110 (VAC3) closure call | `cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K18_ACM0_VAC3, -1)` |

Two consequences to weigh, and they pull in opposite directions — say which you accept:
1. **Supporting "no call"**: no function in the file actuates K17, so the VAC-branch entry state is
   inherited rather than an item action, and `K17` was invisible to the previous TM108 code too.
2. **Against it**: the two sibling VAC items in the same family **do** add their VAC-branch entry
   relay (`K18` / `K19`) to their own `SetOn`, so an unchanged-TM108 that omits the analogous call is
   not obviously the family convention. R1 md `:245-246` separates "动作（必须闭）= 13, 65" from
   "须处于闭合态 = 17", and R3 `:199` delegates the call form to `ate-implementer` under `OI-T4-04` —
   so *someone* was supposed to decide the form, and "no call" is a decision that must be defended on
   the evidence above rather than assumed.
Note this is also why `C9` calls the siblings a **copy risk**: TM109/TM110 are close to the untouched
TM108 baseline, so neither copying them nor ignoring them is automatically right.

**`C8` (new) — verified conformances, for the reviewer's checklist.** (Heading restored after an
accidental overwrite; body re-based on the **applied** file, `sha256_pl 8498c304…`.) The item
matches R1/R3 on: register staircase (`entertestmode()`, `I2CWriteSameData(DEV_ADDR,0x56,0x16)` =
R1 `DMUX_SEL=22`, `I2CWriteSameData(DEV_ADDR,0x57,0x08)` = R1 `DMUX_EN=1`); power-on VBAT
`FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, RELAY_ON`; the measurement call pair (2 ×
`test_method.rampv_capv` — 20 V/100 mA source, 10 V/10 µA observation, `0.0→10.0` then `10.0→0.0`,
200 samples at **20 µs** per sample per method contract `:455`/`:465`, capture 1.65 V, `TRIG_FALLING`
then `TRIG_RISING`); hysteresis units (`(rise - fall) * 1e3` → mV). R1 explicitly registers the
unused CSV-layer alternative (`0x55=0x97`, `EN_DTEST0/DTEST0_MUX=23`) as a **registered conflict**, so
its absence from the executed code is correct. Verify `t7` did not regress any of these.


## 5. Explicitly out of scope

- No compilation, no gate script execution, no build report — that is `compile-diagnostician`.
- No hardware claim, no deployment.
- No electrical or method decision: any such issue is a finding routed to its owner.
- Judging whether `DMUX_SEL=22` (vs 23), the 1.65 V level, the `DTEST0` identity or the F1-F6 values
  are *correct*. Only whether the code implements what the contracts signed.

## 6. Required outputs

1. `team/artifacts/tm108-v2-trial/review/t8-review-findings.md` — human-readable report.
2. `team/artifacts/tm108-v2-trial/review/t8-review-findings.json` — machine-readable, with the
   charter's fields: `runId`, `reviewedInputs[]` (with plaintext hashes), `applicableRules[]`,
   `phaseTrace[]`, `findings[]` (`id` / `severity` / `TM` / `category` / `evidence` /
   `violatedRule` / `responsibleOwner` / `repairCondition`), `gateResults[]`, `waivedFindings[]`,
   `reviewStatus`, `residualRisks[]`.
3. A one-line verdict.

## 7. Finding routing (charter §5)

DFT intent → `dft-expert`; schematic/path/relay facts → `schematic-expert`; global resource or Setup
boundary → `setup-architect`; source/relay-group/register-value → `test-strategy-architect`; phase /
differential state / measurement / log method → `test-method-expert`; API / range / code placement /
fidelity → `ate-implementer`; build/environment → `compile-diagnostician`.

## 8. Verdict rule

- `pass` — implemented faithfully; no blocking finding. Only then may the next stage (`t9`, compile)
  be considered.
- `needs-revision` or `reject` — must list findings with `responsibleOwner` and `repairCondition`,
  and must **not** hand off downstream. Return to the owner of the contract or the implementation as
  the routing table dictates.

## 9. Reporting

Exactly one structured message:

- `DONE: t8; outputs: <paths>; verdict: <pass|needs-revision|reject>`
- `BLOCKED: t8; evidence: <paths>; question: <one precise question>`
