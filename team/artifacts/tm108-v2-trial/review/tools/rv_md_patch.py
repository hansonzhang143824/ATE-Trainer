# -*- coding: utf-8 -*-
import os, hashlib, sys

P = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.md'
t = open(P, 'rb').read().decode('utf-8')

def insert_after_line_containing(text, needle, payload):
    i = text.index(needle)
    j = text.index('\n', i)
    return text[:j + 1] + payload + text[j + 1:]

def insert_before(text, needle, payload):
    i = text.index(needle)
    return text[:i] + payload + text[i:]

def insert_after_paragraph_containing(text, needle, payload):
    i = text.index(needle)
    j = text.index('\n', i)
    return text[:j + 1] + payload + text[j + 1:]

# ---- M1: new reviewed inputs in the hash table
t = insert_after_line_containing(t, 'fa41e471ae549ab0affcf629fc1d691703281a08498cfe10c26d926c4d115e54',
"""| `source/BoardCheck.h` — widened C11 scope | `ad562c1c14929bbf71f5549269ce6c44c16352eb4d4299a130952f714d5d83ea` | 32536 | – | – | – | ✅ |
| `source/treg.h` — widened C11 scope | `e10c2ac7e2b53b043467ed1579e76de9c41bde2b6e7d5b787a3e0d8ccc262bbc` | 51157 | – | – | – | ✅ |
| `source/src/treg.h` — duplicate-copy check | `ae0d6d6221f8fdb5409e98956218211740170ad6bbfa70ef016d0efbf61450ff` | 47730 | – | – | – | ✅ |
""")

# ---- M6: scope-correction note in the verdict section
t = insert_after_paragraph_containing(t, 'does not hand off downstream',
"""
> **Scope correction applied (captain input during t8).** The t8 contract restricted the `C11` verification to "no other logging primitive exists **in `test.cpp`**"; the captain withdrew that restriction as its own error, because "absent from `test.cpp`" is not "absent from the project". `C11` and `RF-01` were therefore re-based on a project-level probe of every named candidate (`BoardCheck.h`'s `CBC_log`, `treg.h`'s `TREG_LOG::log_data`, `treg.h`'s `TREG_ERROR::treg_error_log`, and the `log_data_t`/`test_t` typedefs). **Every candidate was ruled out**, so the ruling and the terminal verdict are **unchanged** — see the C11 addendum in §3.
""")

# ---- M2: C11 addendum, inserted immediately before the C12 heading
C11_ADDENDUM = """
#### C11 addendum — captain scope correction (widened project-level verification); ruling UNCHANGED

The captain withdrew the t8 contract's own restriction of this check to "no other logging primitive exists **in `test.cpp`**", on the principle that **"absent from `test.cpp`" is not "absent from the project"**. My first pass committed exactly that narrow-scope error; that narrower basis is **superseded**, and the finding is re-based on the probe below. Every candidate was examined in python byte mode with mechanism-level evidence, not by name inspection.

**(i) `BoardCheck.h:214 class CBC_log` — `log()` at `:759`, `test_log()` at `:760`, instance `CBC_log bc_log;` at `:778`. NOT USABLE.**

- `BoardCheck.h` is **not in the transitive include closure** of `test.cpp`. The closure I computed over local headers is `Coutlier.h`, `FMEA.h`, `LogDataStruct.h`, `Pin_Channel_define.h`, `StdAfx.h`, `Test_Method.h`, `mylib.h`, `spec.h`, `src/visa.h`, `src/visatype.h`, `stdafx.h`, `sub.cpp`, `sub.h`, `tempchar.h`, `test.cpp`, `treg.h` — **`BoardCheck.h` is absent**, so the type is not even declared for a TM translation unit.
- `log`/`test_log` (`:759-760`) are public *members of `BoardCheck`* (nearest specifier `public:` at `:346`, next `private:` at `:767`), but the **only instance** `CBC_log bc_log;` (`:778`) is in `BoardCheck`'s **private** section.
- `CBC_log`, `bc_log` and `test_log` have **zero users outside `BoardCheck.h`/`BoardCheck.cpp`** across all 36 source files scanned.
- The only instantiations are a **local** `BoardCheck bc;` at `source/diags.cpp:80` and inside `run_diags()` (`source/diags.cpp:188`), which `test.cpp:797` calls **once from the startup path** behind `if (DO_BoardCheck)` — never from a TM.
- The qualified name **`CBC_log::` occurs 0 times anywhere in the tree** — `log()`/`test_log()` are declared but **never defined and never called**.
- `BoardCheck` is a dialog-based board-check utility (`BoardCheckGroup`, `DialogTemplate`, listbox, buttons, `SetConsoleTextSize`). `BoardCheck.cpp` writes **nothing** to the station datalog — **0** `SetTestResult`, **0** `msLogData`, **0** `SetTestNumber`; only `GetMeasResult` (151), i.e. it **reads** results and CSV. Its "Save datalog" comments are its own board-check CSV.

**(ii) `treg.h:195 TREG_LOG::log_data` — the important negative result. NOT REACHABLE.**

- Declared under **`private:`** (`treg.h:194`) in `class TREG_LOG`, whose friends are only `TREG`, `TRIM_NODE` and `TRIM_GRP_NODE` (`:187-189`). A TM function is none of those.
- Its implementation (`treg.cpp:285-348`) **is a genuine datalog write path with exactly the shape R3 §6 needs** — it carries a `testname` string plus limits and unit: `log_data_func(site, testname, lolim, hilim, value, unit, no_scaling)`, else `test_func(testnum, value, site, 0)`, else `msLogData(...)`.
- But **every piece of the plumbing is private static**: `TREG_LOG::datalog_func` (`treg.cpp:275`), registered by the private `register_dlog_func` (`treg.h:197`); the `log_data_func`/`test_func` helpers are private to the `TREG_ETS364` path.
- The **only public route into it** is a `TRIM`/`TRIM_GRP` node's `execute(..., int log_level = TREG_LOG_STD, ...)` (`treg.h:559`, `:565`, `:742`) — i.e. the **Trim framework**, which R1 §1 declares TM108 does **not** trigger (`trim = null`; "Trim 判定 否（不触发 Trim 框架）"). There is no public `TREG` wrapper: the only `log` members on the `TREG` side are the private `log_data`, the `TREG_LOGLEVEL` enum, and the `log_level` default parameters.
- This holds for **both** `treg.h` copies in the tree.

**(iii) `treg.h:176 TREG_ERROR::treg_error_log` — public static, therefore technically callable, but NOT a `logPlan` vehicle.**

- Its definition (`treg.cpp:227-251`) is a **debug console error channel**: it increments `error_count`, and on the first call does `FreeConsole(); AllocConsole(); SetConsoleTitleA("AccoTEST Debug Window"); freopen("conout$", "w+t", stdout);` then `printf_s(" %d. ", error_count); printf_s(buffer);`.
- **All 47** of its uses in `treg.cpp` are **error paths** ("TREG: No TRIM parameter defined.", "post_value define is wrong in PGS…"); **none** is a data record.
- Its sibling `TREG_ERROR::error` (`treg.cpp:256-267`) routes to `error_func` → `etsfatalerror()` (ETS364) or `MessageBox()` — a **fatal error**, categorically not a log.
- `TREG_ERROR` is used **0 times** in `test.cpp` and `sub.cpp`.
- It cannot produce R3 §6's unit/precision/per-site datalog records, and routing data through it would misuse a fatal-error console channel.

**(iv) `treg.h:108` / `:110` `log_data_t` / `test_t`** — **callback typedefs** under `#ifdef TREG_ETS364`, not callable primitives; the callback is invoked only from the private `TREG_LOG::log_data`. Not a vehicle.

**Also checked and negative.** `Test_Method.h` (the object owning `rampv_capv`) has **zero** log-related members; `sub.h` has none; `LogDataStruct.h` defines `CAccoCsvData`, a **CSV datalog reader** (`load_data` into `test_vec`/`lolim_map`/`hilim_map`/`unit_map`/`val_map`), not a writer; `mylib.h` has no logger. No other candidate API name exists in the tree: `WriteLog`, `AddLog`, `LogMessage`, `PrintLog`, `SetLog`, `LogString` = **0 hits**; `msLogData` only in `treg.cpp`; `DataLog` once in `BoardCheck.cpp`.

**Positive corroboration that `SetTestResult` *is* this project's datalog primitive.** The framework's own logdata helper `source/src/treg.cpp:62 stslogdata()` writes through `CParam::SetTestResult`; the active standard **R-LOG defines the log rule in terms of `SetTestResult`** (`rules-registry.md:37`); and `LogData` in `test.cpp` is 91 raw tokens with **0** occurrences as a call — exactly the step label the captain said it was. I did not mistake it for an API.

**Ruling: UNCHANGED.** No candidate is usable, so `DEV-3` remains a **contract-vs-capability** finding owned by **`test-method-expert`** — **not** a code finding against `ate-implementer`. The widened evidence *sharpens* it: a real datalog primitive does exist in the framework, but it is deliberately **fenced to the Trim framework**, which this item by R1's own classification does not use.

**Verified vs inferred vs unknown — stated explicitly.**

- **Verified by measurement:** R1–R5 hashes; the live/backup/manifest hash binding; the backup against the captain's independent pre-change block; the comment-only nature three ways; the TM108 spans; the `test.cpp` include closure; the access specifiers and friend lists in `BoardCheck.h` and both `treg.h` copies; the absence of any `CBC_log::` definition tree-wide; the definition of `treg_error_log`; and the counts recorded below.
- **Inferred (flagged):** that a no-trigger segment logs the `0` initialiser (`RR-02`) — because `rampv_capv`'s no-trigger behaviour is undocumented.
- **Unknown (flagged, not assumed):** **`CParam`'s full public surface** (`RR-12`), the framework's per-item relay reset (`RR-01`), and which `treg` copy is in the build (`RR-13`).

**Honest limit of this conclusion — a residual UNKNOWN (`RR-12`).** `CParam` is the only framework object a TM holds (`StsGetParam` returns `CParam*`), and **no `class CParam` declaration exists anywhere under `D:\\PROJECT6-DALI\\ForCodexDebug`** — the token appears there only as a *use* (`test.cpp` 668, `source/src/treg.cpp` 2, `Shmoo.h` 1, `Test_Method.cpp` 1). It is declared in an **external SDK header not present in this checkout**, so its full public API **cannot be enumerated from this tree**. The observed surface used in `test.cpp` is `SetTestResult` (188), `GetMaxLimit` (3), `getNextParam` (4), `get_param_name_in_spec` (4). If that SDK header exposes a text/logging method reachable from a TM, **`RF-01` must be re-opened as a code finding against `ate-implementer`**. I cannot rule that out here, and I do not claim to.

**Count discrepancy, recorded for reconciliation.** The captain's figures "`SetTestResult` (200 uses) and `GetMeasResult` (422)" do not reproduce against any file set I measured. My measurement of `test.cpp`: `SetTestResult` **188** call sites (188 raw tokens); `GetMeasResult` **65** raw, **64** comment-stripped. Tree totals over the 36 source files: `SetTestResult` **244**; `GetMeasResult` **574** (`sub.cpp` 204, `Test_Method.cpp` 153, `BoardCheck.cpp` 151, `test.cpp` 65, `tempchar.cpp` 1). This does not affect the C11 conclusion, which rests on access specifiers, include closure and method definitions rather than on counts.

"""
t = insert_before(t, '### C12 — the `K17` closed-state requirement', C11_ADDENDUM)

# ---- M3: RF-01 addendum after its routing note
t = insert_after_paragraph_containing(t, '**No executable line of `test.cpp` needs to change to close `RF-01`.**',
"""

**Widened-scope addendum (captain correction).** This finding's evidence was originally scoped to `test.cpp`, and that scope was withdrawn by the captain as too narrow. It has been re-based on a project-level probe: `BoardCheck.h`'s `CBC_log` (not in the `test.cpp` include closure; its only instance private at `:778`; the qualified name `CBC_log::` used 0 times tree-wide), `treg.h`'s `TREG_LOG::log_data` (a real datalog writer, but private with only `TREG`/`TRIM_NODE`/`TRIM_GRP_NODE` as friends, and reachable only through a Trim node's `execute()` — while R1 §1 declares TM108 `trim = null`), and `treg.h`'s `TREG_ERROR::treg_error_log` (public static, but a debug-console **error/fatal** channel, not a datalog record). **None is usable**, so the owner, severity and blocking status are unchanged. Mechanism-level proof and the one residual UNKNOWN (`RR-12`) are in the C11 addendum in §3.
""")

# ---- M4: two new residual risk rows
t = insert_after_line_containing(t, '| `RR-11` | low |',
"""| `RR-12` | medium | **UNKNOWN, stated not assumed:** `CParam`'s full public surface cannot be enumerated from this checkout. It is the only framework object a TM receives (`StsGetParam`), yet no `class CParam` declaration exists anywhere under the target root — only *uses* of it. If the external SDK header declares a text/logging method reachable from a TM, `RF-01` must be re-opened as a **code** finding against `ate-implementer`. Closing action: locate and read that header. |
| `RR-13` | low | The tree carries two **non-identical** copies of `treg.h` (`source/treg.h` `e10c2ac7…`, 51157 B vs `source/src/treg.h` `ae0d6d62…`, 47730 B) and of `treg.cpp` (`ae86d1a1…` vs `1cefbf11…`). Both `treg.h` copies declare `log_data` under `private:`, so the C11 ruling is copy-independent. No `.sln`/`.vcxproj` was opened (out of scope), so which copy is in the build is UNKNOWN. Owner: `compile-diagnostician`. |
""")

# ---- M5: G-11 row
old_g11 = '| `G-11` | R3 §6 `logPlan` completeness | **FAIL** | 3 of 10 rows emitted → `RF-01`. |'
new_g11 = '| `G-11` | R3 §6 `logPlan` completeness | **FAIL** | 3 of 10 rows emitted → `RF-01`. Re-run at the widened project scope ordered by the captain: `BoardCheck.h`\'s `CBC_log`, `treg.h`\'s `TREG_LOG::log_data` and `treg.h`\'s `TREG_ERROR::treg_error_log` were each examined and none is a usable vehicle (see the C11 addendum in §3). The gate stays **FAIL**. |'
assert t.count(old_g11) == 1, t.count(old_g11)
t = t.replace(old_g11, new_g11, 1)

with open(P, 'wb') as f:
    f.write(t.encode('utf-8'))
print('MD written. bytes=%d sha256=%s' % (os.path.getsize(P), hashlib.sha256(open(P, 'rb').read()).hexdigest()))
for probe in ('C11 addendum', 'RR-12', 'RR-13', 'Scope correction applied', 'Widened-scope addendum', 'ad562c1c14929bbf71f5549269ce6c44c16352eb4d4299a130952f714d5d83ea'):
    print('  contains %-22s %d' % (probe[:22], t.count(probe)))
