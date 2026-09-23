# t38 — parameterised batch plan for the t43 decision (A: instrument pin, B: TM600 K109/K110)

Status: **plan only — nothing executed.** Payload frozen at `39,457 B / 2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`; target tree
unchanged (`469,714 B / 15c7d2b8…`); contract, plan, scripts untouched. Written so that whichever way **t43**
rules, execution is a single mechanical batch with no further analysis.

## 0. The two pending variables (neither is hard-coded here)

- **A — instrument pin**: does `SW12_U1REF_BST_ACM` drive **ch5** or **ch18**?
- **B — TM600 `K109/K110` disposition**: **retain** (marked per-contract-conservative) or **remove / mark "not closed by this item"**.

`A` sets *which route must be closed*; `B` sets *whether the FPVIe-side pair stays*. Per captain's instruction I
**choose neither**, and I record below that the four combinations are **not** independent — `B` has a safety
condition that depends on `A` (§3).

## 1. Evidence anchors used by every branch

| Anchor | Value |
| --- | --- |
| ch5 route to BST | `SCH-Connect-Map.txt:672-674` → `BST [Kelvin] 需闭合: K48,K76`; `S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F` |
| ch18 route to BST | `SCH-Connect-Map.txt:42` → `CH0 Low -> BST 需闭合: K109,K110,K138,K139,K145,K146`; `:43` → `… K109(ON) -> K110(ON) -> BST_F` |
| SW route (unchanged in every branch) | `:174` → `CH0 Low -> SW 需闭合: K60,K61` (both already closed) |
| Relay authority, TM600 | `relaySet` contains **48, 76, 109, 110** — all four are within TM600's authority |
| Relay authority, TM601 | `relaySet` contains **none** of 48, 76, 109, 110 |
| channel macro | `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_` = `S5_5, S6_5, …` (pin **5**) |
| in-service precedent | deployed tree closes `K48_ACM5_AMP_REF + K76_ACM_BST` at L7000/L7087/L7170/L7513; comment `L6997 … (FH5→BST)` |
| further pin-5 evidence | `StdAfx.h`: `K48_ACM5_AMP_REF = 48`, `K76_ACM_BST = 76`, **`K_BST_ACM = 48,76`** |

## 2. The four-combination matrix

| # | A (pin) | B (K109/K110) | Required-to-BST set | TM600 SetOn action | TM601 SetOn action |
| --- | --- | --- | --- | --- | --- |
| **1** | ch5 | **retain** | `[48,76]` (+`[61]` for SW) | **ADD `K48_ACM5_AMP_REF` + `K76_ACM_BST`**; keep `K109/K110` with a comment marking them retained-because-the-contract-lists-them | no change (still 0 ACM calls) |
| **2** | ch5 | **remove** | `[48,76]` (+`[61]`) | **ADD `48/76` AND REMOVE `K109/K110`** → net SetOn = `K83, K60, K61, K48, K76, K13, K85, K57, K126` | no change |
| **3** | ch18 | **retain** | `[110,61]` as today | **no change** to the required set; keep `K109/K110`; note in comment that `48/76` are the ch5 route (not in force) | no change |
| **4** | ch18 | **remove** | `[110,61]` — **but see §3 hazard** | cannot simply remove: removing `K109/K110` while the instrument still drives 5 V **destroys the only path to BST** ⇒ this combination forces **either** a payload change to also stop driving the ACM source, **or** a contract statement that the ACM route is not required | no change |

**Common to all four:** the three gates re-run on a sandbox copy; independent review; captain's REPLACE. No branch
touches TM601's SetOn, because TM601 owns **none** of the four relays under either reading — so the t38 removal
conclusion is invariant across this matrix.

## 3. The one dependency that must not be lost: `B=remove` is not safe under every `A`

This is the point that makes the two variables **coupled**, and it is worth stating because it is the same failure
mode as t38 itself:

- **Under `A = ch18`** (today's payload), `K109/K110` **are** the path to BST. Removing them while the payload still
  executes `SW12_U1REF_BST_ACM.Set(FV, 5, …)` on TM600 would re-create **exactly the defect t38 removed from TM601**:
  an excitation with no landing. So combination 4 is **not** a simple "delete two relays" batch — it must be paired
  with either stopping the ACM drive or a contract statement of non-requirement.
- **Under `A = ch5`** (combination 2), removing `K109/K110` is safe *from that standpoint*, because `48/76` carry the
  source; the remaining question is only the coupling below.

## 4. On the coupling argument (why my earlier "keep conservatively" was weakly reasoned)

`schematic-expert` (the t42 author) argues against retaining, on grounds of **substantive coupling, not harmless
redundancy**: closing `K109` joins pins 3/6 = `FPVIe1_FL_BUS_S1` / `FPVIe1_SL_BUS_S1`, which puts the **FPVIe1
low-domain bus onto the BST node**; and energising `K110` connects the **ch18 source pin** to BST, so if that source
is undriven the BST node acquires an **undeclared / floating source**.

**I accept that this weakens my earlier framing.** I had suggested keeping `K109/K110` as "conservative" under the
pin-5 reading. That reasoning assumed an un-closed relay is electrically *neutral*, i.e. that extra closures are
merely redundant — but with a double-throw latching part (see `t40` §3b) **both** contacts are live paths, so an
"extra" closure can change the circuit rather than sit inert. "Conservative" is therefore the wrong word for
**adding an unrequired closure to a node under measurement**; the conservative act is to close exactly what the
in-force route requires. That is precisely the ruling the captain has sent to **t43**, and I am not pre-empting it.

## 5. What I need from the t43 batch (nothing else)

1. **A** decided (ch5 or ch18), with the authority that decides it.
2. **B** decided, and — if `B = remove` while `A = ch18` — the accompanying instruction from §3 (stop the drive, or
   declare non-requirement).
3. Confirmation of whether **rev 25** splits the pin-5 and pin-18 ACM200 rows (the captain's plan has rev 25 landing
   **before** the payload change, which I endorse: the payload cannot be compliant against an authority that does not
   express the requirement).

On receipt I execute: apply the row above → re-run `relay-trace` / `bst-sw` / `awg` on a sandbox copy → report exit
codes and the full warning list (the two `TM643_VBAT_LOOP_INDICTOR` warnings should remain, new red = 0) → hand to
independent review → captain REPLACE. **I will not choose between A and B, and I will not pre-place either into the
payload.**

## 6. Discipline

All of the above is **documentary and in-service-code evidence — not an electrical conclusion**. No bench measurement
exists for any branch; whether the ACM200 source actually lands on BST remains **UNKNOWN** until the pin is settled by
authority and, ultimately, by hardware. **A compiled closed loop is not electrical sign-off.**
