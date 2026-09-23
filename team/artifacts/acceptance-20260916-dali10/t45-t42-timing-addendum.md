# t46 — t42 timing addendum: expected relay sets per TM under the corrected contract

**Author:** schematic-expert · **Kind:** work (t46, t42 supplementary) · **Attempt:** 1
**Purpose:** record the three per-TM expectation statements so no consumer plans on "t29 lands ⇒ `bst-sw`
turns green". **The t42 verdict is unchanged** (`SW12_U1REF_BST_ACM` = ACM200 channel 5 ⇒ BST needs
`[48,76]`). This file does not modify `t42-acm200-pin-attribution.md` (`8883daad…`),
`t44-t42-addendum.md` (`30aa1be6…`) or `t45-l672-section-evidence.md` (`4d894034…`).

---

## 1. Statement 1 — TM600 still misses `[48,76]`; t29's `K109/K110` does not turn `bst-sw` green

Measured (deployed `ForCodexDebug/source/test.cpp`, body `TM600_HS_RDSON` = **L9057–9204**):

```
SetOn L9081 = K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap,
              K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP          -> {13,57,60,61,83,85,126}
body hits: K46 = 0, K48 = 0, K49 = 0, K76 = 0, K109 = 0, K110 = 0
```

Expectation for TM600 (union over the contract's declarations, see §4):

| contract revision | expected set | source of each element | deployed satisfies? |
|---|---|---|---|
| rev 24 (on disk) | `{60,61,83,110}` | `pmid2sw=[83,60,61]` (via `aliasesUsed`) ∪ `bst2sw=[110,61]` (via `usedByTm`) | **no — missing `110`** (today's red) |
| rev 25 (corrected) | `{48,60,61,76,83}` | `pmid2sw=[83,60,61]` ∪ `bst2sw(BST end)=[48,76]`, SW end `[61]` already covered | **no — missing `48,76`** |

⇒ **Both before and after the contract fix, `bst-sw` reports red for TM600 — the cause simply moves from
"missing K110" to "missing 48,76".** t29's `K109/K110` repair is therefore **not sufficient** to turn the
assertion green, and t33/t34 must not sequence on that premise.

**Why K109/K110 cannot substitute:** `K109/K110` is the **FPVIe[L] / QVM[L]** leg to BST
(`StdAfx.h:452 K_FPVIL_TO_BST_B = 109,110` with the comment `FPVIe[L] -> BST`; `:451`; `:557 K_BST_QVML`;
`SCH-Connect-Map.txt:42/43` from `S1_FPVIe_FL0`; `:268/269` from `S1_FPVIe_FL1`; `:538/539` from
`S8_QVM_CH0-`). The **ACM200** route is `K_BST_ACM = 48,76` (`StdAfx.h:620`, comment `ACM200[] -> BST`), and
the ACM200 column's own group header is `SCH-Connect-Map.txt:672 BST [Kelvin] 需闭合: K48,K76` with source
`S5_ACM200_FH5` (pin 5). Deployed TM600 **drives** that instrument (10 `.Set` calls, 9 `RELAY_ON` + 1
`RELAY_OFF`, non-zero FV ×7, staircase `0→5→10→15→20→15→10→5→0`, top range `ACM200_40V`) while closing none of
its routing relays; since BST has no default route (`:672` lists required closures, whereas `:675 BST1` reads
`无(默认导通)`), and `K48` at default sends ch5 to `SW1` (`:774/:775`), the drive lands on **SW1** and the BST
rail is left undriven. Closing `K48/K76` **reroutes** ch5 off SW1/SW2 rather than adding a branch
(`:673` / `:775` / `:778` — one physical line, three states, one destination).

---

## 2. Statement 2 — TM601 is **not** bound by the `bst2sw` expectation (applying it is a false red)

Contract facts (rev 24, verified): `aliasResolution[1] sw2pgnd` has `usedByTm = ['TM601']` and
`closedRelayNumbers = [154,155,60,61]`; `tmDeltas.TM601.aliasesUsed = ['sw2pgnd']`;
`aliasResolution[3] bst2sw` has `usedByTm = ['TM600 (BST must lead PMID)', 'TM1205 (BST1-SW1 / BST2-SW2 ramps)']`
— **TM601 is absent**.

Measured: deployed `TM601_LS_RDSON` (L9217–9353) closes `{13,57,60,61,85,126,154,155}` (SetOn `L9255`),
which **satisfies** `sw2pgnd = {154,155,60,61}` ⇒ **TM601 is green** under the current contract, and remains
green when only `bst2sw` is corrected, because TM601 never participates in that alias.

**The trap:** listing TM601 as "expected `[48,61,76]`, missing `[48,76]`" applies TM600's alias to TM601 and
produces a **false red**. Acting on it would push an implementer to add `48/76` to TM601 — the opposite of
**t38**, which removed TM601's `SW12_U1REF_BST_ACM` drive precisely because *TM601 has no BST requirement*.
Grep-verifiable corroboration: deployed TM601's body contains **0** hits for `K46/K48/K49/K76/K109/K110`.

> Note (informational, not a defect claim): the deployed TM601 body still contains 3 `.Set` calls of that
> instrument (one non-zero, `L9269`), i.e. t38's removal exists in the payload (`2d0984d9…`) but not in the
> deployed tree (`15c7d2b8…`). That is the same "payload not landed" state t33 already blocks on; it does not
> change TM601's expectation, which is `sw2pgnd` only.

---

## 3. Statement 3 — TM1205's expectation must come from the `bst1_sw1` / `bst2_sw2` variant rows

Contract facts: `aliasResolution[3] bst2sw`'s **nodes are `BST ↔ SW`**, yet its `usedByTm` entry claims
`TM1205 (BST1-SW1 / BST2-SW2 ramps)` — and **BST1/BST2 are different DUT pins from BST**. TM1205 has
`aliasesUsed = []`, so under the union rule it picks up `bst2sw = [110,61]` **via `usedByTm`** only.

Measured (deployed): `TM1205_TRX_BST_UV_GD` (L8766) closes the **variant** routes —
`L8791 K_FPVIH_TO_SW1_A + K_FPVIL_TO_BST1_A` (= `K46` + `K41`) and
`L8835 K_FPVIH_TO_SW2_A + K_FPVIL_TO_BST2_A` (= `K46,K49` + `K41,K43`),
matching `aliasFlatTable[14] bst1_sw1 kNumbers=[46,41]` and `[15] bst2_sw2 kNumbers=[46,49,41,43]`
(both `variantOf = bst2sw`, `usedByTm = null`).

⇒ With `bst2sw = [110,61]` applied to TM1205 the assertion reports a **second false red** (TM1205 never uses
K110/K61 for this). Its expectation should be taken from the two variant rows
(`[46,41]` and `[46,49,41,43]`), which the deployed code **does** satisfy.

---

## 4. The assertion's union design is correct and necessary — keep it

`scripts/verify_bst_sw_sequence.py` computes the expectation as the **union** of three sources
(`L243–246`): `aliasResolution[*].closedRelayNumbers` for aliases whose `usedByTm` contains the TM as an
independent token ∪ `tmDeltas.<TM>.aliasesUsed` ∪ `--tm-alias <TM>=<a>`.

This is **required**, not incidental: `tmDeltas.TM600.aliasesUsed = ['pmid2sw']` **omits** `bst2sw`, so an
assertion indexed by `aliasesUsed` alone would skip TM600's BST leg entirely — the exact blind spot this
assertion was built to close. Unioning `usedByTm` is what catches it. **No change to the script's indexing is
warranted**; the two false-reds in §2/§3 come from the *contract's* data, not from the script's design.

The script is also **contract-driven** — it contains no hard-coded K numbers for this leg, so a contract
rev 25 automatically updates the expectations. That is the intended behaviour and the reason to fix the
contract rather than the script.

---

## 5. Disposition summary (what to act on, in one table)

| TM | expectation now (rev 24) | expectation after contract rev 25 | deployed set | today | after rev 25 | action |
|---|---|---|---|---|---|---|
| TM600 | `{60,61,83,110}` | `{48,60,61,76,83}` | `{13,57,60,61,83,85,126}` | red (missing 110) | **red (missing 48,76)** | needs a real repair closing `[48,76]` — not K109/K110 |
| TM601 | `{154,155,60,61}` | unchanged | `{13,57,60,61,85,126,154,155}` | **green** | **green** | none — do not add `48/76` |
| TM1205 | `{110,61}` (mis-applied) | should be `[46,41]` + `[46,49,41,43]` from the variants | `{13,65,46,41,49,43}` | red (false) | **green** if the variants are used | contract must bind TM1205 to the variant rows |

---

## 6. Boundary

Only this file was written for t46. **No writes** to `t42`/`t44`/`t45` artefacts, the contract
(`fd00a508…`, rev 24), the test plan, the payload (`2d0984d9…`), gate scripts, `devel`, or the target tree.
Temporary scripts removed.

All statements rest on **static connectivity + header/netlist/in-service-function-body evidence**. This is
**not** machine-measured and **not** an electrical conclusion; a green gate or a closed compile is not
electrical sign-off. Open for the contract owner / bench: whether TM600/TM601 must be ACM-driven at all,
whether `PB0_BST_ACM` (ch18) + `[110]` is permitted, and the electrical consequence of the SW1 landing.

**Reproduce:**

```bash
python -c "import json;c=json.load(open('team/artifacts/acceptance-20260916-dali10/setup-contract.json',encoding='utf-8-sig'));print(c['revision']);[print(e['alias'],e.get('usedByTm'),e['resolution']['closedRelayNumbers'],[x['relay'] for x in e['resolution'].get('relayChain',[])]) for e in c['aliasResolution'] if e.get('alias') in ('pmid2sw','sw2pgnd','bst2sw')];print([ (e['alias'],e.get('kNumbers')) for e in c['aliasFlatTable'] if e.get('alias') in ('bst1_sw1','bst2_sw2')]);print({t:c['tmDeltas'][t].get('aliasesUsed') for t in ('TM600','TM601','TM1205')})"
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();[print(i,ls[i-1].strip()[:170]) for i in (8791,8835,9081,9255)]"
python -c "l=open('project/DALI/SCH-Connect-Map.txt',encoding='utf-8',errors='replace').read().splitlines();[print(i,l[i-1].strip()) for i in (672,673,675,774,775,777,778)]"
```
