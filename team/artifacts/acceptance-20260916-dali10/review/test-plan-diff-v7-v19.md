v7(136263/e1dd24de) -> v19(164399/d2aef4ad5f3e)
added=28 removed=2 changed=49

== REMOVED (v7 had, v19 lacks) ==
  - items/TM600/measurement/samples/note = adopted from the archived TM600 golden; the live precedent uses 50 samples - difference recorded; the capture must complete inside the 2 ms pulse cap
  - items/TM601/measurement/samples/note = adopted from the archived TM600 golden; the live precedent uses 50 samples - difference recorded; the capture must complete inside the 2 ms pulse cap
== ADDED ==
  + items/TM000/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM001/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM102/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM103/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM108/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM109/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM1205/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM135/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM600/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM600/measurement/activationSemantics/clampAnnotation/ceiling = with 0.5 V of compliance at 1 A, a device at roughly 500 mOhm or above clamps the current source, so the reading stops being a measurement of the device and becomes a clamp condition; that condition i
  + items/TM600/measurement/activationSemantics/pulseCap/metric = the WHOLE forced-current duration, i.e. settle time plus acquisition time (1 ms settle + 200 samples x 5 us = 1 ms acquisition = 2 ms total)
  + items/TM600/measurement/pulseCap/metric = the WHOLE forced-current duration, i.e. settle time plus acquisition time (1 ms settle + 200 samples x 5 us = 1 ms acquisition = 2 ms total)
  + items/TM600/measurement/samples/alternative = the 50/5 pair would preserve TM-level consistency and is equally defensible; the choice is recorded here so it is explicit rather than silent
  + items/TM600/measurement/samples/evidence = the archived golden uses this pair; within the TM-level test source every one of the measurement calls uses the 50/5 pair and none uses 200; the shared trim-measurement source and the board-check sour
  + items/TM600/measurement/samples/rationale = taken from the golden for its heavier averaging on a 10 mV-class signal; 200 samples at the 5-unit period is about 1 ms of capture, comfortably inside the 2 ms pulse cap
  + items/TM600/measurement/samples/summary = golden value; heavier averaging than any TM-level code; correctness-neutral, affecting only noise and test time
  + items/TM600/unresolved/3 = DV-01 driver-level evidence for the sense-bus routing.
  + items/TM601/cleanup/2 = Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
  + items/TM601/measurement/activationSemantics/clampAnnotation/ceiling = with 0.5 V of compliance at 1 A, a device at roughly 500 mOhm or above clamps the current source, so the reading stops being a measurement of the device and becomes a clamp condition; that condition i
  + items/TM601/measurement/activationSemantics/pulseCap/metric = the WHOLE forced-current duration, i.e. settle time plus acquisition time (1 ms settle + 200 samples x 5 us = 1 ms acquisition = 2 ms total)
  + items/TM601/measurement/pulseCap/metric = the WHOLE forced-current duration, i.e. settle time plus acquisition time (1 ms settle + 200 samples x 5 us = 1 ms acquisition = 2 ms total)
  + items/TM601/measurement/samples/alternative = the 50/5 pair would preserve TM-level consistency and is equally defensible; the choice is recorded here so it is explicit rather than silent
  + items/TM601/measurement/samples/evidence = the archived golden uses this pair; within the TM-level test source every one of the measurement calls uses the 50/5 pair and none uses 200; the shared trim-measurement source and the board-check sour
  + items/TM601/measurement/samples/rationale = taken from the golden for its heavier averaging on a 10 mV-class signal; 200 samples at the 5-unit period is about 1 ms of capture, comfortably inside the 2 ms pulse cap
  + items/TM601/measurement/samples/summary = golden value; heavier averaging than any TM-level code; correctness-neutral, affecting only noise and test time
  + items/TM601/parameters/5/note = 1 ms settle + 200 samples x 5 us acquisition = 1 ms, so the whole forced-current window is 2 ms and meets the user's 2 ms HARD CAP (deliberate deviation from the golden's 2 ms settle)
  + limitations/17 = BD-06 - TM1205 has no numeric limit in any DFT source, so that item closes structurally only and is never reported as a passed/failed electrical result.
  + limitations/18 = BD-07 - the high-side item's 'Y / 2 FLOAT' special flag is interpreted as two floating nodes (recorded as a REOPENABLE assumption, not a measured fact).
== CHANGED ==
  ~ BD/BD-04/status
      v7 : closed-for-this-run (user-confirmed: the captain's analogous ruling was formally adopted by the user)
      v19: closed-for-this-run
  ~ BD/BD-06/status
      v7 : closed-by-user-adjudication (structural closure only)
      v19: closed-by-user-adjudication (structural closure only, no numeric criteria)
  ~ items/TM000/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM001/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM102/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM103/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM108/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM108/unresolved/0
      v7 : BD-04: rising threshold 4.4 V (OVERVIEW) vs 4.15 V (DFT.csv) - open.
      v19: BD-04 is CLOSED for this run (see blockingDecisions[BD-04]): the OVERVIEW rising threshold 4.4 V governs, and the DFT.csv value 4.15 V is retained verbatim as a registered conflict.
  ~ items/TM109/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM109/unresolved/0
      v7 : BD-04 open (4.4 vs 4.15 V).
      v19: BD-04 is CLOSED for this run (see blockingDecisions[BD-04]); the DFT.csv row for this item is retained as a self-contradictory registered conflict (value 4.15 V plus the wrong ramp pin and a copied monitor select).
  ~ items/TM1205/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM135/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM600/assumptions/0
      v7 : Resource arbitration: the contract's arrangement uses both floating channels (one for the 1 A loop, one for the 5 V bootstrap rail); the archived golden instead builds the bootstrap rail from two independent ground-referenced sources and needs only one floatin
      v19: Resource arbitration — DECIDED: the bootstrap-to-switched loop is driven from the floating channel 1 (high terminal to the bootstrap node, low terminal to the switched node). This is the baseline and it means the high-side item consumes both floating channels 
  ~ items/TM600/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM600/measurement/activationSemantics/orderedSteps/2
      v7 : 3. Wait 2 ms for settling - this IS the pulse cap, so it may not be extended.
      v19: 3. Wait 1 ms for settling; the capture (200 samples x 5 us = 1 ms) then completes inside the same window, so settle + acquisition = 2 ms and meets the 2 ms HARD CAP. The shorter settle is a DELIBERATE DEVIATION from the archived golden's 2 ms, which would put 
  ~ items/TM600/measurement/activationSemantics/pulseCap/consequence
      v7 : the settle time may not exceed 2 ms, and the sample capture must finish before the current is removed
      v19: settle plus acquisition may not exceed 2 ms in total, and the sample capture must finish before the current is removed
  ~ items/TM600/measurement/activationSemantics/pulseCap/precedent/locator
      v7 : the golden waits 2 ms after the 1 A step and immediately returns the current to zero
      v19: the golden waits 2 ms after the 1 A step and immediately returns the current to zero, so the golden's own effective pulse is about 3 ms - the user's cap governs and the shorter settle is a deliberate, cited trade-off
  ~ items/TM600/measurement/decisionPoint/primary/annotation
      v7 : first use in the live tree; intentional deviation from the live single-ended precedent - flagged for review
      v19: ARCHIVED NATIVE IMPLEMENTATION of this exact item - the archived high-side golden computes the resistance from the floating channel's own measured voltage and current, so this is the older design's own choice rather than a novelty; it is also the ONLY ASSEMBLA
  ~ items/TM600/measurement/pulseCap/consequence
      v7 : the settle time may not exceed 2 ms, and the sample capture must finish before the current is removed
      v19: settle plus acquisition may not exceed 2 ms in total, and the sample capture must finish before the current is removed
  ~ items/TM600/measurement/pulseCap/precedent/locator
      v7 : the golden waits 2 ms after the 1 A step and immediately returns the current to zero
      v19: the golden waits 2 ms after the 1 A step and immediately returns the current to zero, so the golden's own effective pulse is about 3 ms - the user's cap governs and the shorter settle is a deliberate, cited trade-off
  ~ items/TM600/parameters/5/source
      v7 : the archived golden's 2 ms settle after the 1 A step
      v19: 1 ms settle so that settle + acquisition meets the user's 2 ms HARD CAP on the whole forced-current window (DELIBERATE DEVIATION from the archived golden's 2 ms settle, whose own effective pulse is about 3 ms; the hard cap governs)
  ~ items/TM600/parameters/5/value
      v7 : 2
      v19: 1
  ~ items/TM600/sequence/6
      v7 : Wait 2 ms for settling.
      v19: Wait 1 ms for settling; the capture (200 samples x 5 us = 1 ms) completes inside the same window, so settle + acquisition = 2 ms and meets the 2 ms hard cap on the whole forced-current window (deliberate deviation from the archived golden's 2 ms settle, whose 
  ~ items/TM600/unresolved/0
      v7 : BD-05 clamp numeric value (mechanism fixed, value provisional).
      v19: BD-05 is CLOSED by user adjudication: the clamp is a provisional engineering default requiring bench sign-off and is protection only - it must never be used as a limit.
  ~ items/TM600/unresolved/2
      v7 : DV-01 driver-level evidence for the sense-bus routing.
      v19: U9 whether the plain output-relay-on setting activates the sense path; U10 two-wire sense-meter channel concurrency with the floating channel on the same nodes.
  ~ items/TM601/cleanup/1
      v7 : Restore every TM-specific relay and register to the contract's post-function state so the next TM starts from the documented baseline.
      v19: The unified relay-off range follows the contract / captain ruling (the 1 V range with the 10 mA current range), not the archived golden's wider 10 V / 10 mA pair.
  ~ items/TM601/measurement/activationSemantics/orderedSteps/2
      v7 : 3. Wait 2 ms for settling - this IS the pulse cap, so it may not be extended.
      v19: 3. Wait 1 ms for settling; the capture (200 samples x 5 us = 1 ms) then completes inside the same window, so settle + acquisition = 2 ms and meets the 2 ms HARD CAP. The shorter settle is a DELIBERATE DEVIATION from the archived golden's 2 ms, which would put 
  ~ items/TM601/measurement/activationSemantics/pulseCap/consequence
      v7 : the settle time may not exceed 2 ms, and the sample capture must finish before the current is removed
      v19: settle plus acquisition may not exceed 2 ms in total, and the sample capture must finish before the current is removed
  ~ items/TM601/measurement/activationSemantics/pulseCap/precedent/locator
      v7 : the golden waits 2 ms after the 1 A step and immediately returns the current to zero
      v19: the golden waits 2 ms after the 1 A step and immediately returns the current to zero, so the golden's own effective pulse is about 3 ms - the user's cap governs and the shorter settle is a deliberate, cited trade-off
  ~ items/TM601/measurement/pulseCap/consequence
      v7 : the settle time may not exceed 2 ms, and the sample capture must finish before the current is removed
      v19: settle plus acquisition may not exceed 2 ms in total, and the sample capture must finish before the current is removed
  ~ items/TM601/measurement/pulseCap/precedent/locator
      v7 : the golden waits 2 ms after the 1 A step and immediately returns the current to zero
      v19: the golden waits 2 ms after the 1 A step and immediately returns the current to zero, so the golden's own effective pulse is about 3 ms - the user's cap governs and the shorter settle is a deliberate, cited trade-off
  ~ items/TM601/parameters/5/value
      v7 : 2
      v19: 1
  ~ items/TM601/sequence/6
      v7 : Wait 2 ms.
      v19: Wait 1 ms for settling; the capture (200 samples x 5 us = 1 ms) completes inside the same window, so settle + acquisition = 2 ms and meets the 2 ms hard cap on the whole forced-current window (deliberate deviation from the archived golden's 2 ms settle).
  ~ limitations/1
      v7 : U1 (relay contact rating at 1 A) and U2 (10 kOhm series rows in the Kelvin sense path) are open hardware questions; no on-tester authorisation is implied by this plan.
      v19: U1 (relay contact rating at 1 A) and U2 are open hardware questions; no on-tester authorisation is implied by this plan.
  ~ limitations/10
      v7 : U6 - no sanctioned discharge role exists in the current relay definitions; the contract assumes cap-gate open plus a 1 kOhm bleed (about 4.7 ms time constant on a 4.7 uF rail).
      v19: U5 - whether the default route to the high-side node must be opened while the floating channel owns that node is unresolved.
  ~ limitations/11
      v7 : U7 - (not raised by the contract; slot retained).
      v19: U6 - no sanctioned discharge role exists in the current relay definitions; the contract assumes cap-gate open plus a 1 kOhm bleed (about 4.7 ms time constant on a 4.7 uF rail).
  ~ limitations/12
      v7 : U8 - no formal rejection test exists for the cross path that cross-links the high and low buses.
      v19: U7 - (not raised by the contract; slot retained).
  ~ limitations/13
      v7 : U9 - whether the plain output-relay-on setting is sufficient to activate the sense path, or whether the dedicated sense-activation relay setting is required. The latter has zero occurrences in the project source and this run cannot produce board evidence, so i
      v19: U8 - no formal rejection test exists for the cross path that cross-links the high and low buses.
  ~ limitations/14
      v7 : U10 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented; must be settled by the relay-trace gate / independent review, and is NOT assumed here.
      v19: U9 - whether the plain output-relay-on setting is sufficient to activate the sense path, or whether the dedicated sense-activation relay setting is required. The latter has zero occurrences in the project source and this run cannot produce board evidence, so i
  ~ limitations/15
      v7 : BD-06 - TM1205 has no numeric limit in any DFT source, so that item closes structurally only and is never reported as a passed/failed electrical result.
      v19: U10 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented; must be settled by the relay-trace gate / independent review, and is NOT assumed here.
  ~ limitations/16
      v7 : BD-07 - the high-side item's 'Y / 2 FLOAT' special flag is interpreted as two floating nodes (recorded as a REOPENABLE assumption, not a measured fact).
      v19: U11 - SIGN-CONVENTION: FPVIe ch0 terminals are fixed by the netlist (PGND only on the HIGH side, SW only on the LOW side); the iset sign semantics must be derived as alias direction -> instrument terminal -> command sign; implement the DFT literal direction an
  ~ limitations/2
      v7 : TM1205 closes structurally only (BD-06).
      v19: U2 with its numeric criterion - the Kelvin row feeding the high-side sense path carries a series resistor of about 10 kOhm; if the sense amplifier input sits after it, the 1% error budget requires an input bias current no greater than about 11 nA for the 11 mO
  ~ limitations/3
      v7 : The clamp value is a provisional engineering default and is protection only (BD-05).
      v19: TM1205 closes structurally only (BD-06).
  ~ limitations/4
      v7 : The source defect recorded for TM109's DFT.csv row (copied monitor select, third pin in the ramp) is carried, not corrected.
      v19: The clamp value is a provisional engineering default (provisional / bench-signoff-required) and is protection only - never a pass/fail criterion (BD-05).
  ~ limitations/5
      v7 : Coverage of TM001/TM102/TM135/TM1205 in DFT.csv is absent; the authoritative DFT input is the workbook (contract openItem DFT-COVERAGE).
      v19: The source defect recorded for TM109's DFT.csv row (copied monitor select, third pin in the ramp) is carried, not corrected.
  ~ limitations/6
      v7 : Build/compile success is not electrical validation; this plan asserts nothing about measured silicon behaviour.
      v19: Coverage of TM001/TM102/TM135/TM1205 in DFT.csv is absent; the authoritative DFT input is the workbook (contract openItem DFT-COVERAGE).
  ~ limitations/7
      v7 : U3 - the two floating channels' low terminals both land on the switched node; plausible but unproven from the netlist.
      v19: Build/compile success is not electrical validation; this plan asserts nothing about measured silicon behaviour.
  ~ limitations/8
      v7 : U4 - the source type of the two named channel identifiers is inferred, not confirmed.
      v19: U3 - the two floating channels' low terminals both land on the switched node; plausible but unproven from the netlist.
  ~ limitations/9
      v7 : U5 - whether the default route to the high-side node must be opened while the floating channel owns that node is unresolved.
      v19: U4 - the source type of the two named channel identifiers is inferred, not confirmed.