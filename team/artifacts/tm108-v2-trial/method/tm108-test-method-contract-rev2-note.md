# TM108 test-method contract — Rev 2 revision note (task `t10`, run `tm108-v2-impl`)

- **Role:** `test-method-expert` (owner of the R3 contract artifact)
- **Driver:** `RF-01` — `blocker`, category `contract-vs-capability`, owner `test-method-expert`, from the independent rule review `t8`
  (`review/t8-review-findings.md` / `.json`), plus the related inference `RR-02` under the same rule.
- **Disposition taken:** **(b)** — the raw-context/context rows of `logPlan` are **explicitly downgraded to source-comment documentation**
  (stating plainly that they are **not** station-log records), and a **failure-path rule that does not depend on any API this project does not have**
  is added for the no-trigger / boundary-trigger / negative-Hys cases.
- **Machine-readable twin:** `tm108-test-method-contract.json` (revised in the same revision).
- **Scope of this task:** this artifact pair only. **No C++ file was written or modified**, and `D:\PROJECT6-DALI` was **not accessed at all**.
  No electrical value, relay, register, range, limit or tolerance was introduced.

---

## 1. Hash ledger — baseline (rev 1) and revised (rev 2)

Every value is a **plaintext sha256 computed in python byte mode** (`open(p,'rb')`), the convention this run uses for hash anchors.

| Artifact | Rev 1 = the exact bytes the `t8` review was performed against | Rev 2 = this revision |
|---|---|---|
| `method/tm108-test-method-contract.md` | `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7` — 90822 B | `F87EE0CA396D23D8C3F19886EEF6F70264DB7F29BAFF69445B66FAB8A9B0A332` — 113157 B |
| `method/tm108-test-method-contract.json` | `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21` — 102544 B | `5990ACC1EFB6B1AB42BFC8C2DD22B24BF52254293620E8FDA35599D06138C313` — 126324 B |
| `method/bst-sw-phase-check.md` (unchanged by this task) | `FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54` — 9860 B | same (`FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54`) — untouched, byte-identical |

The Rev 1 hashes reproduce the review's own snapshot (`review/t8-review-findings.json` → `reviewedInputs[R3].sha256_plaintext`,
`reviewedInputs[R4].sha256_plaintext`), so the baseline in this note is the reviewed byte image and not a re-derived one.
This note is the record of both hash sets because a file cannot contain its own sha256.

**Inputs consumed by this revision (plaintext sha256, for the audit trail)**

| Input | sha256 | Used for |
|---|---|---|
| `review/t8-review-findings.md` | `4700223A2A257D144B355A3FD2E8BD60B7186C6C44B996BBD7FAD67A0BF47A25` | `RF-01`, `RR-02` (md) |
| `review/t8-review-findings.json` | `CC3664921CF70F74B696EC13D17157E1321401EEC1D450702841FF67A266E649` | `RF-01`, `RR-02`, the reviewer's hash snapshot |
| `review/tools/out/logging.txt` | `F50719EBB45771A74EAD9F704D819A7810B44B1A7E89A3888B58966520CE616E` | callable inventory / `SetTestResult` count / no string-taking definition |
| `review/tools/out/reach.txt` | `A63F092DBB343DEBB2E8059CA40C61ADFFB501731CCA710C088F5C3D88B46755` | include-closure + declaration reachability |
| `review/tools/out/errlog.txt` | `63EEAAF3ED98992BEF36D161DD8D800ADE63A4F17D9A2A300FCE9863B3C5D989` | `TREG_ERROR` / `TREG_LOG` implementations |
| `review/tools/out/cparam.txt` | `05115FF9B68C344D1029DF0E8A8BA0B94645698AF92E1EE653AF8E9FE9E08F19` | `SetTestResult` call form via `StsGetParam` |
| `review/copy/test.cpp` | `B79B911A65A33ABD62697F8576BD04B5022194751C9BFC5B174ECDAB96D05D5A` (477123 B) | the reviewed code revision (read-only; byte-identical to the live file per the review's G-01/G-02) |
| `Library-Functions/treg/treg.h` | `E10C2AC7E2B53B043467ED1579E76DE9C41BDE2B6E7D5B787A3E0D8CCC262BBC` | byte-identical to the project's `source/treg.h` (reproduces `reach.txt`) |
| `Library-Functions/treg/treg.cpp` | `AE86D1A1CDBD3EE1BAED85D3435A46CB19D5803AE97C0FAF0373E1CA91512489` | byte-identical to the project's `source/treg.cpp`; `treg_error_log` console implementation, `msLogData` under `#ifdef TREG_ETS364` |
| `Library-Functions/BoardCheck/BoardCheck.h` | `AD562C1C14929BBF71F5549269CE6C44C16352EB4D4299A130952F714D5D83EA` | byte-identical to the project's `source/BoardCheck.h`; `CBC_log` declarations |
| `knowledge/standards/rules-registry.md` | `9BA6E2524BFF615A89D10162476DFD724748D263A712B7040C78DC91DAFE92D1` | `R-LOG` at `:37` (the standard itself names only `SetTestResult`) |
| `knowledge/standards/functions-registry.md` | `4EAC1DE1C65CFB72E28703A4798877AF9812A90D80681E80F2A2E0FE29EFFF7E` | `:43` `rampv_capv` — no failure/no-trigger signal registered (`RR-02`) |
| `strategy/tm108-resource-config-contract.md` | `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4` | unchanged signed boundary (re-verified) |

---

## 2. What the review found, and what this revision does about it

`RF-01`'s repair condition offers two routes. This revision takes **(b)** and says why **(a)** is not available inside the signed boundary.

**Why not (a).** Option (a) would require every raw-context row to name a concrete, reachable mechanism plus its field mapping.
The only station-log write path reachable from a TM function is `CParam::SetTestResult(<site>, <limit>, <value>)`, and it can only be called
on a parameter object obtained through `StsGetParam(funcindex, "<name>")` — i.e. on a **DFT parameter**. This item has exactly three DFT
parameters (`VAC1_PRST_Rise`, `VAC1_PRST_Fall`, `VAC1_PRST_Hys`). Emitting the other seven quantities as records would therefore first
require **new DFT parameters**: a DFT/strategy-side change that is outside this contract's boundary and that the method owner may not invent.
It is registered as the new open item `OI-T5-06` and the new return item `RT-6` instead.

**What (b) changes.** `logPlan` is split into two explicit classes, and the split is stated as the method's own position:

1. **`logPlan.recordedItems` / §6.1 — three calculated quantities = station-log records**, with the mechanism and its field mapping given
   (argument 1 = site, argument 2 = limit, *not used* by this item because no tolerance exists (`RT-4`), argument 3 = value).
2. **`logPlan.documentationOnlyItems` / §6.2 — seven raw-context/context rows = source-comment documentation**,
   with the plain statement that **they are not station-log records and are not emitted by any call**.
3. **`logPlan.capabilityAudit` / §6.3** — the candidate-by-candidate audit that forces the split, including the include-closure and
   declaration evidence, so that the disposition is auditable rather than asserted.
4. **`measurementPlan.failurePathRule` / §4 — the failure-path rule**: no-trigger, boundary-trigger and negative-Hys, decided per site,
   with no substituted number published, using only the two carriers this project really has (source-comment documentation, and the
   **absence** of the affected parameter's result). It names **no** detection primitive, because `rampv_capv`'s failure semantics are
   unregistered (`functions-registry.md:43`); that gap is the new open item `OI-T5-07`.

---

## 3. Capability evidence — verified before relying on it

The task required this be checked rather than taken on faith. This task re-ran the checks on workspace copies whose **byte identity with the
project source is itself hash-verified** (`Library-Functions/treg/*` and `Library-Functions/BoardCheck/BoardCheck.h` reproduce the hashes the
review computed on `D:\PROJECT6-DALI\ForCodexDebug\source\*`), so no claim here depends on reading the DLI-protected tree.

| Candidate | In `test.cpp`'s closure? | Callable from a TM? | Verdict |
|---|---|---|---|
| `CParam::SetTestResult(site, limit, value)` on a `StsGetParam(funcindex,"<名>")` object | yes (used 187 times in code) | yes | **the only station-log write path**, and it is bound to DFT parameter names → carries only the three recorded rows |
| `TREG_ERROR::treg_error_log(const char*, ...)` (`treg.h:176`, `public static`) | **yes** (`StdAfx.h:27` → `treg.h`) | **yes** | **reachable but not a log**: it `FreeConsole()`/`AllocConsole()`/`SetConsoleTitleA("AccoTEST Debug Window")`/`freopen("conout$","w+t",stdout)` and `printf_s`-es an `" ERROR  Information List"` banner (`treg.cpp:227-251`). A debug-console error sink: no site dimension, not the station data log → **not adopted** |
| `TREG_LOG::log_data(...)` (`treg.h:195`) | yes | **no** — declared in a `private:` section (`friend TREG` / `TRIM_NODE` / `TRIM_GRP_NODE` only) | not reachable |
| `CBC_log::log` / `CBC_log::test_log` (`BoardCheck.h:759-760`) | **no** — `BoardCheck.h` is not in the closure; no user outside `BoardCheck.*` | n/a | not reachable |
| `msLogData(...)` + `SetTestNumber(...)` (`treg.cpp:348`, inside `#ifdef TREG_ETS364`) | declaration is in the tester-framework headers, **not present in this workspace** | **UNKNOWN** | **not adopted**: reachability and semantics cannot be established, and calling it would violate the reviewer charter's library-function rule (a call must trace to a registered declaration, implementation and semantics) — the same rule under which `RF-02` scores an unevidenced implicit side effect. Registered as `OI-T5-06` / `RT-6` |
| `LogData` (91 hits in `test.cpp`) | n/a | n/a | comment headers only, never calls |
| `printf` / `cout` | n/a | yes | hotkey/UI code only |
| `stslogdata(...)` (duplicate `source/src/treg.cpp`) | not declared in any header seen here | n/a | not adopted; and it adds no capability — its own body still writes through `StsGetParam(funcindex,"Func_Label")->SetTestResult(...)` |

**One refinement of the review's wording, reported rather than buried.** The review concluded that "this file exposes no logging primitive other
than `SetTestResult`". That is **substantively correct and the disposition is unchanged**, but the precise statement is that
`TREG_ERROR::treg_error_log` **is** reachable and callable from `test.cpp`; it is simply **not a station-log mechanism** (debug console).
So the accurate formulation is "no reachable mechanism can carry the seven rows **as records**", not "no reachable text-log API exists".
This refinement is recorded in `logPlan.capabilityAudit` and in the review's own ledger row as a self-correction, and it does **not** move the
finding from contract repair to code repair.

---

## 4. `RR-02` (no-trigger logged as `0`) — how it is handled

`RR-02` is an **INFERENCE**, not a measured fact: `rampv_capv`'s failure semantics are undocumented (`functions-registry.md:43` documents only
"result = the voltage at the trigger point"). This revision therefore:

- states the **obligation** in `failurePathRule` case `no-trigger` — no initialised or defaulted number may be published in place of a missing
  capture, and `Hys` must not be computed from a segment without a capture;
- does **not** name a detection primitive, does **not** assert that the current implementation violates the rule, and does **not** invent a
  return-value convention;
- carries the undetectable part as the new open item **`OI-T5-07`**, whose closing evidence is the primitive's registered declaration and body
  (or a bench observation of a no-trigger segment);
- records that until `OI-T5-07` closes, a no-capture segment must be treated as an **unclosed failure path**, not as a conformant one — and
  that if the primitive turns out to report no trigger, the consequence is a code item for `ate-implementer` at that point, not now.

The Rev 1 wording at `md :486` and `:544` is therefore superseded by this rule; both of its substantive parts (the three triggering cases and
the prohibition on a substituted number) are preserved.

---

## 5. Discipline the review required of any repair

| Requirement | Status |
|---|---|
| Performed by the finding's `responsibleOwner`, not by the reviewer or the captain | ✅ `test-method-expert` |
| Recorded with new plaintext hashes; the pre-change image never changes | ✅ §1 above; `bst-sw-phase-check.md` is byte-identical (untouched) |
| Every open item left open: `OI-T4-01`, `OI-T5-01/02/03/05`, `RT-1`..`RT-5`, `F1`–`F6` | ✅ none resolved, none relabelled, no side chosen; `OI-T5-06` / `OI-T5-07` / `RT-6` are **additions** |
| No electrical value, relay, register, range, limit or tolerance introduced | ✅ the revision adds no such fact; the new rule judges only against values the item itself writes and reads |
| Reviewer's findings files not edited | ✅ untouched |
| Implementation not edited; `D:\PROJECT6-DALI` not touched | ✅ no C++ file was written or modified; the code revision was inspected only through the review's byte-identical copy |
| The disposition recorded as audit-able in the contract's own open/return sections | ✅ `OI-T5-06` / `OI-T5-07` in `openItems[]`, `RT-6` in `returns[]`, `§0b` revision ledger, `§6.1`–`§6.4`, `§11` reviewer criterion |

## 6. Known limitations carried with this revision

1. **The generator is stale.** `_build_method_contract.py` produced Rev 1 and lives inside this workspace's `TSZ#` transparent-encryption
   container, so it was **not** modified by this task; Rev 2 was applied to the published plaintext artifacts (the outputs of
   `_finalize_method_contract.mjs`). Rev 2 is therefore not reproducible from that generator as it stands — recorded here and in the contract's
   `evidence[]` (E25) so no later re-issue silently assumes otherwise.
2. **This revision does not close `RF-01` by itself.** Per the repair routing plan §1.4, a repair invalidates the review that produced the
   finding, so a **fresh `rule-reviewer` pass bound to the Rev 2 hashes** is required. The criterion that review should apply is stated in
   `§11` of the contract and in `logPlan.reviewerCriterionRev2`.
3. **`RF-02`, `RF-03`, `RF-04`** (all owner `ate-implementer`, all comment/documentation-only) are outside this task's ownership and are
   untouched by it.
