# TM600/TM601 measurement step — captain-authored call form (verbatim)

> **Status: supplementary handoff, NOT part of `test-plan.json`.**
> The t4 contract requires `test-plan.json` to contain **no concrete test API names and no C++ code**
> (acceptance criterion + role boundary "不发明测试 API 名"). The captain's final batch (item 8)
> specifies the exact call form for the measurement step, so it is recorded **here verbatim** for
> t5 while `test-plan.json` carries the same step as role/argument semantics
> (`items[TM600].measurement.activationSemantics`, mirrored on TM601).

Source: captain ruling, "t4 定稿追加（最后一批，第 8 项）", reproduced with ONE later amendment (see below).

```cpp
FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
FPVI0.SetClamp(50, 50);          // provisional engineering default；每次 FV/FI 切换后必须重发
delay_ms(1);                     // AMENDED: was delay_ms(2) - see the pulse arithmetic below
FPVI0.MeasureVI(200, 5, FPVIe_MV_X10);
R[mΩ] = FPVI0.GetMeasResult(site, MVRET) / FPVI0.GetMeasResult(site, MIRET) * 1e3;
FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
```

### Amendment 1 — settle reduced from 2 ms to 1 ms (pulse arithmetic), captain-decided

The verbatim form above was `delay_ms(2)`, which does not satisfy the user's **2 ms hard cap** on the
forced-current window: measurement is synchronous in `MEAS_NORMAL` and the sample period is in µs
(`knowledge/sources/fpvie.md:174-209`), so `MeasureVI(200, 5)` **adds** 200 × 5 µs = **1 ms** to the
force duration, i.e. `delay_ms(2)` + 1 ms capture ≈ **3 ms**. The captain therefore ruled the settle to
**1 ms**, giving `settle 1 ms + acquisition 1 ms = 2 ms ≤ 2 ms HARD CAP`.

- This is a **deliberate, cited deviation from the archived golden** (the golden's `delay_us(2000)` +
  the same capture has an effective ~3 ms pulse). It must **not** be judged as an unsupported deviation.
- `pulseCap = 2 ms (HARD CAP)` is retained; its **metric** is the *whole forced-current duration*
  (settle + acquisition).
- Implemented and verified in `test-plan.json`: `items[TM600|TM601].measurement.pulseCap.metric`,
  the `settle` parameter (value 1 ms), and both the item `sequence` step and the activation step
  ("Wait 1 ms … the capture … completes inside the same window, so settle + acquisition = 2 ms").

## Binding annotations carried from the ruling

1. **Do not introduce**, in plan or implementation: `FPVIe_RELAY_SENSE_ON`, `FPVIe_CONTACTMODE`,
   `FPVIe_HIGH_MV`, `FPVIe_LOW_MV`. All four have **zero hits in all project source**; this run is
   code + compilation only and cannot produce board evidence of their necessity. They become
   **bench verification item U9** (documented fallback if board work shows the sense path inactive
   under `FPVIe_RELAY_ON`). The only remaining first-use surface of form (a) is `FPVIe_MV_X10`.
   **Stronger, verified reason (ledger, 18:0x):** `FPVIe_HIGH_MV`/`FPVIe_LOW_MV` are **unreachable** —
   the driver's `enum MeasRet` (`ATDriverPackGlobal.h`) carries only `{MEASTYPERET, MVRET, MIRET}`,
   and **no public method accepts** `FPVIe_RET_RESULT` (`FPVIe.h:60-66`). So the differential voltage
   is read through the channel's generic voltage return (`MVRET`), and **U9 is narrowed to one dimension**:
   whether `FPVIe_RELAY_ON` alone activates the sense path, versus `FPVIe_RELAY_SENSE_ON` as the fallback.
2. **First-use annotations** (so t6/t8 do not flag them as defects):
   - `FPVIe_MV_X10` = **first use, intentional deviation**; argument = "10 mV-class differential on the 1 V range";
     explicitly **reject** `FPVIe_100MV` (a failing device saturates under the ±0.5 V clamp first).
   - `GetMeasResult(site, MVRET)` on the floating channel = **golden-supported, first use in project source**
     (cite `knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp:91`; project source 0 hits).
   - The gain argument itself has method-library precedent but is used there **only at X1**
     (`Library-Functions/Test_Method/Test_Method.cpp`, 36 call sites with `FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG`).
3. **Everything else has precedent**: `FPVIe_RELAY_ON` (289 project hits); `FPVI0`/`FPVI1` are global
   objects (`extern FPVIe FPVI0;` — `Pin_Channel_define.h:120-121`), so **`FPVIe.Set(...)` must not be written**;
   `MeasureVI`; `GetMeasResult(site, MIRET)`.

## Relay-wiring rules for these two functions (revision v5, verified against the live header)

- Use **only the minimal endpoint path macros**. The composite macros additionally carry the sense-float,
  both local-sense cross-short and both PC-route relays; closing them collapses the four-wire measurement
  into a local two-wire one.
- **Negative list (checkable form): relays 87, 88, 89, 90, 91 must not appear in the REQUIRED-ON set**
  of these two functions. The minimal endpoint macros that reach the required pins contain none of them
  (high side→target and low side→switched node).
- **Mechanism (corrected after the schematic owner's device-level evidence):** those relays are the sense
  network's **default-conducting (normally-closed) contacts** — the sense-float contact and both local
  two-wire cross-short hooks — plus the two shunt(PC)-route relays. They appear *in the chain* on the
  connect map but not in its "needs closed" set, which is why the connectivity IR lists only the relays
  requiring action. So the operative rule is about the **required-on set**, not about "keeping a relay
  open": an earlier wording that said "these relays must stay OPEN" mis-modelled a normally-closed
  contact and has been withdrawn.
- **Apparent conflict that is not a conflict:** generating the relay set from the connectivity IR's
  action list is correct, and a gate checking the connect map's per-line "needs closed" list is equally
  correct. Neither may be cited as contradicting the other.
- **Relay names come from the live relay-definition header.** The schematic IR's Kelvin-prefixed relay
  names have **zero occurrences** in the live tree and are descriptive aliases, not code names
  (`KELVIN0` = 0 hits, verified with the plaintext-capable search tool).
- On the historical library revision comment (`Test_Method.h:21`, the only `RELAY_SENSE` occurrence in the
  tree): recorded as **context only**. It is a different instrument family's cap call changed to fix an
  alarm issue, i.e. **weak evidence about intent**, and must not be cited as the reason for choosing a
  sense mode.
4. **Boundary sentence for this run** (also written into `test-plan.json.limitations` / `boundaryStatement`):
   *"本次交付＝代码与编译闭环；感测端子激活方式与 clamp 数值均为 provisional/工程默认，须上机验证。"*
5. Limitations to carry (current plan numbering): **U1** (relay 1 A contact rating / hardware sign-off),
   **U2** (the high-side Kelvin row's ~10 kΩ series resistor with its bias-current criterion: ≤ ~11 nA for
   the 11 mΩ item, ≤ ~7.5 nA for the 7.5 mΩ item), **U3–U9** (shared low terminal, inferred channel
   identifiers, the default route question, no sanctioned discharge role, retained slot, no rejection test,
   whether plain relay-on activations suffice for the sense path), **U10** (the two-wire sense meter
   channel's concurrent use while the floating channel forces the same nodes) and **U11** (SIGN-CONVENTION
   — implement the DFT literal direction, never invert silently, with the three bring-up criteria).
   BD-06 and BD-07 are also carried in `limitations`.

## Consistency with the plan

| Aspect | Where |
| --- | --- |
| Ordered step semantics (force/clamp/settle/capture/divide/teardown) | `test-plan.json` → `items[TM600|TM601].measurement.activationSemantics.orderedSteps` |
| Sense-source rule + U9 exclusion | `…measurement.activationSemantics.senseActivation` |
| Gain first-use + rejected 100 mV range | `…measurement.gainFirstUse` |
| Sample count 200 / interval 5 (+ live-precedent 50 difference) | `…measurement.samples` |
| Relay unions (TM600 60,61,83; TM601 60,61,154,155) | `items[TM600|TM601].relayUnion` |
| Four-instrument rejection of form (b) | `blockingDecisions[DV-01].fourInstrumentRejection` |
| Activation-surface rule | `blockingDecisions[DV-01].activationSurface` |

No API name or code fragment appears anywhere in `test-plan.json`; this file is the only place the
verbatim call form is stored.
