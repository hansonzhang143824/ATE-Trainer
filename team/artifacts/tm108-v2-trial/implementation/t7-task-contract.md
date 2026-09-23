# t7 task contract — TM108 implementation (ate-implementer)

**Task id:** `t7`
**Role:** `ate-implementer`
**Run:** `tm108-v2-impl`
**Trigger basis:** direct user instruction ("写TM108的code"). Per `team/ROLE_ROUTING.md:39` and
`protocol-runtime-memory.md:8-11`, a user trigger has the highest authority and overrides the
automatic trigger path. No `deliverable_ready` handoff was issued by `test-method-expert`
(suspended per `protocol-runtime-memory.md:94-104`); this contract is the user-triggered substitute
for that notification and is the record of it.

## 1. Signed upstream inputs (hashes must be re-verified by the implementer, not trusted)

| # | Path | sha256 (verified 2026-09-17 by the captain) | Role |
|---|---|---|---|
| I1 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` | `6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4` | signed resource/config boundary (t4) |
| I2 | `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.json` | `FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9` | machine-readable boundary |
| I3 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.md` | `8EB56D24678406219FE83C3D9E7F09D7D3EC5C39A7A52403F72464802FCA1FA7` | signed test method contract (t5) |
| I4 | `team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.json` | `F947E6C626D32A01FB159C57C32A8F9CC0E9CEFF60B45EA445610123CC3C0E21` | machine-readable method |
| I5 | `team/artifacts/tm108-v2-trial/method/bst-sw-phase-check.md` | `FA41E471AE549AB0AFFCF629FC1D691703281A08498CFE10C26D926C4D115E54` | per-phase BST/SW evaluation |
| I6 | `team/artifacts/tm108-v2-trial/captain-precheck/oi-t4-01-status-addendum.md` | `626BB270BF2B803AA1E5EE1318F9DFFC36D6C12254FFA5F745133A32EA12B9BF` | authoritative OI-T4-01 status |
| I7 | `team/artifacts/tm108-v2-trial/captain-precheck/protocol-runtime-memory.md` | re-hash | runtime protocol + suspension ruling |
| I8 | `team/TEAM_ARCHITECTURE_V2.md` (implementer charter, lines 294-395) + `team/ROLE_ROUTING.md` | re-hash | role contract |
| I9 | `team/schemas/implementation-manifest.schema.json` | re-hash | manifest schema (`targetRoot` const = `D:/PROJECT6-DALI/ForCodexDebug`) |

Chain check (captain, FACT): I1/I2 hashes reproduce the values recorded in I3's Hash Ledger (E1/E2),
so the strategy→method chain is intact and I1/I2 are current.

## 2. Target state (FACT — python plaintext read, 2026-09-17)

Target root is pinned by I9 to `D:/PROJECT6-DALI/ForCodexDebug`.

| File | Plaintext sha256 | Size | Lines | TM108 |
|---|---|---|---|---|
| `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | 469714 B | 9354 (BOM, 9350 CRLF) | comment `:2150`, symbol `:2155` |
| `D:\PROJECT6-DALI\ForCodexDebug\source\sub.cpp` | `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470` | 121909 B | 3336 | 0 hits |

`TM108` is **already implemented**: `DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)`
at `test.cpp:2155`. The task is therefore to bring that function into conformance with I1-I4
(ROLE_ROUTING V2 / I3 §11). `sub.cpp` has no TM108 content; touch it only if the contract requires it,
and if so say why.

## 3. Reader/writer discipline (HARD — DLP trap)

`test.cpp` / `sub.cpp` / `StdAfx.h` under the target are **DLP-transparent-encrypted**. Only
whitelisted processes see plaintext.

- ✅ Read/write/hash these files with **python byte mode only** (`open(p,'rb')` / `open(p,'wb')`),
  preserving UTF-8 BOM + CRLF. Python is at
  `C:\Users\nvt10241\AppData\Local\Programs\Python\Python312\python.exe`.
- ❌ Never use pwsh `Get-Content` / `Select-String` / `Get-FileHash` or any .NET file API on them.
  pwsh sees ciphertext (header `TSZ#…`), reports 0 hits for text that exists, and produces a
  ciphertext digest that falsely looks like "file modified".
- Every existence/absence claim and every hash must be labelled `plaintext` and name its reader.
- Evidence precedent: `team/artifacts/acceptance-20260916-dali10/implementer-recon.md:9-17, :324-350`.

## 4. Authority order

1. User ruling (current).
2. I1/I2 (signed resource/config contract) and I3/I4 (signed test method contract).
3. Existing code is a **downstream consumer**, never an authority. Two known divergences that the
   implementation must correct, per I3's evidence row for the implemented function:
   - the `DTEST0 == nQON` assumption embedded in the function's comment — I3 does **not** adopt it;
   - the K13 (`K13_VBAT_Cap`) relay state — I3 governs (closes at P1, releases at P8; see I3 `RT-1`),
     **and I1 agrees**: I1 requires K13 closed and does **not** list it as keep-open. The alleged I1
     inconsistency in the original `RT-1` text is refuted — see
     `captain-precheck/rt-1-record-correction.md`. State the K13 disposition without claiming an I1
     contradiction.
4. Any conflict discovered between code and contract is **returned**, never silently merged.

## 5. Must-not-resolve (carry as openItems only)

| id | Subject | Handling |
|---|---|---|
| `OI-T4-01` | `DTEST0` observation endpoint identity / carrier | user-frozen; no agent may close or relabel it (I6) |
| `OI-T5-01` | observation endpoint identity, trigger polarity, capture-level validity, `DMUX_SEL=22` sufficiency | carry |
| `OI-T5-02` / `RT-2` | BST/SW constraint unproven in all 9 phases; K57 cap-gate state | carry; add **no** BST/SW driving action |
| `RT-1` | K13 explicit-state statement in the signed contract | **AMENDED 2026-09-17**: implement per I3 (close at P1 / release at P8) — this coincides with I1, so there is **nothing to report and no inconsistency exists**. R3's `RT-1` premise was refuted by the captain against I1 directly; see `team/artifacts/tm108-v2-trial/captain-precheck/rt-1-record-correction.md`. Do **not** write or state that I1's `resourceSummary.keepOpenRelayNumbers` contains relay 13 — it does not (I1 md `:248` and I1 json agree, 16 numbers). |
| `RT-4` | missing tolerance | do **not** invent a tolerance; carry |
| F1-F6, `OI-T4-10/11/12/13/14/16` | DFT conflicts | carry; do not pick a side, do not average |

Do not add, remove or re-value any source table, channel, path, relay set, functional relay,
isolation condition, register value, ramp, delay, sample count, range or limit beyond what I1-I4
state. Numbers that exist only in the current code are **not** authorised by this contract.

## 6. Required outputs

1. `D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp` modified **in place**, minimal diff, TM108 scope
   only (plus `sub.cpp` only if I3 requires it).
2. A byte-exact backup of the pre-change `test.cpp` (and `sub.cpp` if touched) with its plaintext
   sha256, recorded in the manifest `backups[]`.
3. `team/artifacts/tm108-v2-trial/implementation/implementation-manifest.json` conforming to I9:
   `runId="tm108-v2-impl"`, `targetRoot="D:/PROJECT6-DALI/ForCodexDebug"`, `scope`, `backups[]`,
   `changes[]` (path / symbols / beforeSha256 / afterSha256 / planRefs — `planRefs` must cite the
   I1-I4 section or key for every change), `selfChecks[]`.
4. A short `team/artifacts/tm108-v2-trial/implementation/t7-selfcheck.md` listing the exact commands
   run, with the reader used per check, and the carried open items.

## 7. Self-check minimum

- plaintext sha256 before/after for every touched file; BOM present and CRLF count preserved.
- The `DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)` signature unchanged
  (the meta generator regex requires it).
- Every numeric/relay/register literal in the changed code traceable to an I1-I4 reference.
- No TM108 text added or removed in any other function; no other TM touched.
- Explicitly state what was **not** verified (no build was run by this role; compilation belongs to
  `compile-diagnostician`).

## 8. Reporting

Exactly one structured message:

- `DONE: t7; outputs: <paths>`
- `BLOCKED: t7; evidence: <paths>; question: <one precise question>`
