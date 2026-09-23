# t38 addendum — ACM200 pin identity: the `[48,76]` exposure (read-only preparation)

Status: **PREPARATION ONLY.** Payload and contract were **not** modified for this document; the payload remains
frozen at `39,457 B / 2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`. Prepared because the
captain's landing gate is now **t40 (rule-reviewer) + t42 (schematic-expert, ACM200 pin attribution)**, and t42's
outcome can change *which relays must be closed*. This document makes either branch immediately executable and
states the new evidence without prejudging t42.

## 0. THE DECISIVE DOCUMENTARY LINE (verified first-hand at `project/DALI/SCH-Connect-Map.txt`)

```
L672|   BST  [Kelvin]  需闭合: K48,K76
L673|     F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F
L674|     S: S5_ACM200_SH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_S
```
This is the **netlist stating the ACM200 path to BST in full**: the source is **pin 5** (`S5_ACM200_FH5`), and the
required closures are **K48 and K76** with **no K109/K110 anywhere in the path**. Note the path *starts* at the
ACM200 pin, so this row is about the excitation reaching BST — as distinct from `L42`/`L268`, whose paths start at
**`S1_FPVIe_FH0`** (a measurement pin), which is why those rows list `K109/K110`.
Two further corroborations from the same file: `L39` `CH0 High -> BST 需闭合: K46,K48,K76` (the FPVIe CH0-High
route to the same node goes through `K46 -> K48 -> K76`, over the same two relays), and `L461`/`L536` where other
sources (`S10_CH0_A`, `S8_QVM_CH0+`) reach BST through the identical `K46 -> K48 -> K76` chain. **`K48/K76` are the
relays that carry anything to BST in this fixture**; `K109/K110` belong to the FPVIe-channel rows.

**Also worth noting for t42:** `L775`/`L778` show the *same* pin 5 continuing `-> K48(Relay-NC) -> K49 -> SW1_F/SW2_F`,
i.e. `K48` is a two-destination relay (BST when ON with `K76`, SW1/SW2 when NC). That is the same double-throw
mechanism established for `K110`, and it means **`K48` being un-actuated silently routes pin 5 to SW1/SW2** rather
than to BST — the identical dangling-drive pattern, one relay family over.

## 1. The contradiction, stated exactly

The contract contains a **contradiction about which ACM200 pin** feeds `SW12_U1REF_BST_ACM`, and the two candidate
answers need different relays:

| Evidence | Says | Required to reach BST |
| --- | --- | --- |
| `tmDeltas.TM600.pinRouteTable /BST/列6: ACM200 → PIN (Share继电器)` (line 672) | the **ACM200-side** route | **`[48, 76]`** — **no 110** |
| `pinRouteTable /BST/列2: FPVIe → PIN (BUS继电器) \| CH0 Low` (line 42) | the **FPVIe-side** route | `[109, 110, 138, 139, 145, 146]` |
| `pinRouteTable /BST/列2: … \| CH1 Low` (line 268) | the **FPVIe-side** route | `[109, 110]` |
| Channel macro `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_` (`Pin_Channel_define.h:20`, referenced `StdAfx.h:69`) | the instrument's own pin | **`S5_5, S6_5, …`** → **pin 5** |

**Both routes cannot be the one in force**, and the two sides need disjoint relay sets. Pin 5 is the ACM200 *source* (pin 5, per `SCH-Connect-Map.txt:672-674`)
pin; the FPVIe CH0/CH1 rows are about the *measurement* channel, so the `[109,110]` figures may be describing the
kelvin pair rather than the ACM source's own path — which is precisely what t42 must settle.

## 2. NEW EVIDENCE (not previously in the record): the deployed tree already implements the pin-5 path

The incumbent code closes **`K48_ACM5_AMP_REF` + `K76_ACM_BST`** for this very instrument, at **four** sites
(`test.cpp` L7000, L7087, L7170, L7513), and states the mechanism in its own comment:

- **L6997:** `//   BST  ← SW12_U1REF_BST_ACM: K48_ACM5_AMP_REF + K76_ACM_BST (FH5→BST)`
- **L7000:** `cbite.SetOn(K_FPVIH_TO_PGND_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K85_CAP_PMID, K65_nQON_PU, -1);`
- Defines: `StdAfx.h` → `K48_ACM5_AMP_REF = 48`, `K76_ACM_BST = 76`.
- And `K46_BUS0_FH_SW1 = 46` — note the **`FH_SW1`** suffix, i.e. pin 46 is the **SW1** pin, a *different* node
  from the one this measurement uses (consistent with the SW / SW1 / SW2 distinction already recorded).

**The `FH5` in that comment matches the macro's pin 5.** So there is a strong prior that the in-force path is the
**FH5 → `[48,76]`** one, and that the `[109,110]` figures belong to the FPVIe-kelvin framing instead.

## 3. The exposure this creates — it affects TM600 as much as TM601

Measured against my payload's SetOn lists (`K83, K60, K61, K109, K110, K13, K85, K57, K126` for TM600):
**`K48` closed: no. `K76` closed: no. `K46` closed: no.**

| Relay | Route that requires it | In `TM600.relaySet`? | In `TM601.relaySet`? | Closed by my payload? |
| --- | --- | --- | --- | --- |
| `48` (`K48_ACM5_AMP_REF`) | ACM200-side BST route (col 6, L672) | **yes** | no | **no** |
| `76` (`K76_ACM_BST`) | ACM200-side BST route (col 6, L672) | **yes** | no | **no** |
| `46` | `CH0 High -> BST` (L39) — ruling (ii) classed it unrealisable | yes | no | no |
| `109`/`110` | FPVIe-side CH0 Low (L42) / CH1 Low (L268) | yes | no | **yes** |

**Consequence, stated as a conditional and not as a conclusion:** if the in-force baseline is the **pin-5 (FH5)** path,
then **TM600's 5 V does not reach BST either** — because TM600 closes `109/110` (the FPVIe-side requirement) but not
`48/76` (the ACM200-side requirement that its own `relaySet` authorises). That would make `[48,76]` the missing
closure, and my t29 `K109/K110` work would have satisfied the wrong route. Under the same reading, TM601 could not
be fixed at all without a contract change, since neither `48/76` nor `109/110` is in its `relaySet`.
If instead the baseline is pin 18, the current payload is right for TM600 and the contract's ACM200 row is a
**missing-entry** defect for rev 25. **t42 decides; I am not choosing.**

## 4. Why `[48,76]` is separable from the TM601 issue you have frozen

The frozen item is about **excitation that has no landing** (a relay-closure/authority question). Closing `48/76`
is a **relay closure** for a route the contract already declares and for which TM600 already has authority — it is
not an excitation change. So the pin-5 branch could be executed **without** unfreezing the TM601 decision, if the
captain prefers to split them. Flagged as an option; the captain's call.

## 5. What I will do on each outcome (ready, no further analysis needed)

- **t42 says pin 5 / `[48,76]`** → for **TM600** add `K48_ACM5_AMP_REF` + `K76_ACM_BST` to the SetOn (locators:
  contract `pinRouteTable /BST/列6` line 672; deployed `test.cpp:6997` mechanism comment; `SCH` `S5_ACM200_FH5 -> K48 -> K76 -> BST_F` at `:673` as cited by the captain), keep `109/110` only if the FPVIe kelvin pair is also
  required by a route in force, then re-run the three gates. **TM601** needs the contract question answered
  separately (it has no authority for any of these relays).
- **t42 says pin 18** → current payload stands for TM600; the contract's ACM200-side row is a rev-25 missing-entry
  item; TM601 remains as my t38 proposal.
- **Either way** I will re-run relay-trace / bst-sw / awg on a sandbox copy and report exit codes and the full
  warning list, and I will not land anything.

## 6. Discipline

No payload, contract, plan, script or target-tree write was made for this document. All figures are read from the
artefacts at the paths stated. The `[48,76]` reading is **contract-and-source evidence, not bench measurement** —
whether the ACM200 source actually lands on BST through those two relays remains **UNKNOWN** until t42 says which
pin the instrument drives. **A compile closed loop is not electrical sign-off.**
