// =====================================================================
// t5 implementation payload — TM600_HS_RDSON / TM601_LS_RDSON
// run: acceptance-20260916-dali10 | author: ate-implementer
//
// STATUS: NOT APPLIED. The sandbox denies writes to D:/PROJECT6-DALI/ForCodexDebug
// (outside the session workspace) and the escalation request was rejected by the user,
// so this payload could not be inserted into source/test.cpp.
//
// HOW TO APPLY (python byte mode is mandatory — test.cpp is a DLP TSZ container and
// text-mode writes corrupt CRLF to \r\r\n):
//   before-sha256 = 5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317
//   before-size   = 434629 bytes, 8878 lines, UTF-8 BOM + 8874 CRLF
//   append the two functions below at end-of-file, preserving BOM + CRLF, then re-read
//   and re-hash. A byte-identical backup already exists at
//   team/artifacts/acceptance-20260916-dali10/backups/test.cpp.before_TM600_TM601.bak
//
// IDENTIFIERS: all verified against the live tree by python read (DLP-whitelisted).
//   FPVI0/FPVI1 (Pin_Channel_define.h:120-121), FPVIe_RELAY_ON/OFF, FPVIe_1V/2A/10A/10MA,
//   FPVIe_MV_X10, K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K154_BUSH0_AMUX,
//   K155_FOVI3_PGND, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP,
//   VBAT_PD3_FXVI, PMID_HG2_FXVI, SW12_U1REF_BST_ACM, V1P5_U34PS_FXVI, FXVIe_PLUS_*.
//   `FPVIE_RELAY_ON` (capital E) does NOT exist — capital-E references fail to compile.
//
// DElIBERATE FIRST USES (flag for t6, do not treat as unauthorised):
//   - FPVI0.GetMeasResult(site, MVRET) as the measurement — "golden-supported, project-first":
//     no live occurrence in test.cpp/sub.cpp/Test_Method.cpp, but the archived TM600 golden
//     does exactly this at tm600-normal-highcurrent.cpp:91 (== Rdson.cpp, byte-identical).
//   - MeasureVI(..., FPVIe_MV_X10) — the *gain argument* has method-library precedent only as
//     the explicit FPVIe_MV_X1 default (Test_Method.cpp, 36x); X10 itself is a first use.
//   - SetClamp(50,50) — unused anywhere in the live tree.
//
// CAPTAIN RULING — MINIMAL FIRST-USE SURFACE (this run): the payload must NOT use
//   FPVIe_RELAY_SENSE_ON, FPVIe_CONTACTMODE, FPVIe_HIGH_MV or FPVIe_LOW_MV. All four have
//   ZERO hits in project source, and this run performs code + compilation only with no
//   instrument authorisation, so their necessity cannot be decided by hardware evidence.
//   Verified absent from this payload. They are recorded instead as a bench verification
//   item (U series): if on-instrument work shows the sense return is not active under
//   FPVIe_RELAY_ON, then SENSE_ON + CONTACTMODE (with HIGH_MV/LOW_MV) is the documented
//   fallback — NOT the implementation for this run. Net first-use surface = 1 item (MV_X10).
//   Rationale for keeping the MV_X10 gain: a 10 mV-class signal in a 1 V range needs it, and
//   FPVIe_100MV is explicitly rejected (a failing part would saturate under the 0.5 V clamp).
//
// FORBIDDEN, must not appear: test_method.rampi_capv / rampv_capv (they would enrol these
//   functions as BST-SW gate targets -> new red), and the PC route K90/K91 + K82_R_CS.
//
// PROVISIONAL / NOT FOR HARDWARE: the clamp value is a provisional engineering default
//   (non-datasheet, not a pass/fail criterion, not authorised for instrument execution).
//
// CAPTAIN RULING (b) APPLIED - settle reduced to 1 ms.
//   The user states the 1 A pulse limit as a HARD CAP on the whole force duration; the golden form
//   (delay_us(2000) then MeasureVI) is itself ~3 ms, so the precedent form and the explicit cap
//   conflict. Ruling: the explicit cap governs, precedent supplies structure only. Reduction is the
//   safe direction (shorter stress); exceeding the cap is the dangerous one.
//   Result: settle 1 ms + acquisition 200 x 5 us = 1 ms => total 2 ms <= 2 ms HARD CAP.
//   This is an INTENTIONAL DEVIATION from the golden 2 ms settle and is annotated as such in code.
//   Superseded artefact: implementation-payload-TM600-TM601.pulse2ms-variant.cpp (removed - the
//   delivered payload now IS the pulse-compliant form, so a second copy would only risk divergence).
// ============================ FINAL USER RULING (binding) ============================
// Scope: this deliverable is the DEBG copy's code generation and compilation closure only.
//   No real instrument execution is authorised. The production tree is not modified.
// Pulse: the 1 A pulse must be short; the sequence is force -> complete the measurement ->
//   de-assert immediately, and no long 1 A hold is permitted.
//   Pulse-width budget for this payload -- THEORETICAL, NOT MEASURED (captain ruling (b) applied):
//     settle   delay_ms(1)                    = 1.000 ms
//     MeasureVI(200, 5) acquisition           = 200 x 5 us = 1.000 ms   (MEAS_NORMAL
//                                               completes inside the call, so it adds time)
//     -> nominal total                        = 2.000 ms, i.e. EXACTLY the 2 ms HARD CAP
//   F6 -- MARGIN IS ZERO ON PAPER. These are nominal SDK/spec figures and they EXCLUDE the
//   driver, call and relay latency that a real instrument adds, so the true pulse is >= 2.000 ms
//   and cannot be shown to satisfy the cap by calculation alone. This payload must therefore NOT
//   be described as "pulse-compliant, measured": compliance is a BRING-UP VERIFICATION ITEM --
//   scope the actual force-ON to force-OFF interval on hardware and confirm <= 2 ms before any
//   claim. Recorded with U11 as a bring-up limitation, not as a verified result.
//   The cap is stated as a HARD CAP bounding the WHOLE force duration (settle + acquisition), whose
//   purpose is to limit DUT/relay thermal and stress. Exceeding it is the dangerous direction, so the
//   settle was reduced from the golden's 2 ms - a DELIBERATE DEVIATION, annotated as such in code.
//   (Superseded reading: with the golden 2 ms settle the same arithmetic gave ~3 ms, which is why the
//   request for a ruling was raised. The explicit cap governs; precedent supplies structure only.)
//
// F7 -- ARTEFACT LANDING (must be stated in the manifest and the report):
//   dali_tm_meta.json and test_conditions.yaml are generated into the DSH WORKSPACE at
//   project/DALI/meta/, NOT into the VS debug tree. They are workspace-side build/report
//   artefacts consumed by the gates and the manifest; they are not part of the VS project and
//   are not compiled. The only VS-tree change from this task is source/test.cpp.
//
// MANIFEST BOUNDARY SENTENCE - reproduce VERBATIM in implementation-manifest.json:
//   "本次交付＝debug 代码生成与编译闭环；不授权真实上机；clamp/脉冲参数与感测端子激活方式均为
//    provisional / bench-signoff-required；编译与门禁通过不等于电性/硬件正确。"
//
// PLAN v5 CONFORMANCE (relay-wiring safety revision) - verified against test-plan.json v5:
//   * Minimal endpoint form only. The SetOn lists below use the plain endpoint macros
//     (K83_BUSH0_PMID / K60_BUSL0_VCP / K61_ACM8_SW / K154_BUSH0_AMUX / K155_FOVI3_PGND) and the
//     cap gates. NO composite K_FPVI*_TO_* macro is used.
//   * NEGATIVE LIST (verifiable form): relays 87, 88, 89, 90, 91 must NOT appear in the
//     required-on (SetOn) set of either function. They are normally-conducting contacts (one
//     sense-float hook, two local-sense short hooks and two PC-route hooks), so the operative rule
//     is about the required-on set rather than about forcing a relay open. Verified absent.
//   * v5 polarity correction: remote four-wire sensing stays ACTIVE only while the sense-float and
//     local-sense relays remain OPEN. This payload simply never closes them, which is the correct
//     realisation of that prerequisite - the requirement is an open relay, not a closed one.
//   * v5 relay-name authority: names are taken from the live StdAfx.h, not the schematic IR's
//     descriptive 'KELVIN0'-style aliases (which have zero occurrences in the live tree).
//   * v5 gate-red criterion: these functions INTRODUCE no ramp-capture library calls, and any gate
//     verdict must be judged as a delta against the baseline (KNOWN-RED vs NEW-RED), never on
//     absolute token presence.
//
// ==================== CAPTAIN RULING: K87/K88/K89 STATE (closes recon section 6.15) ==========
// K87 / K88 / K89 must be left at their DEFAULT state: no SetOn, and no explicit OFF.
// Evidence chain:
//   1. SCH-Connect-Map.txt legend L4 (Relay-ON = 需SetOn闭合, Relay-NC = 默认导通) and L9-12:
//      S1_FPVIe_FH0 -> K87(NC) -> FPVIe0_FH_BUS_S1, S1_FPVIe_SH0 -> K88(NC) -> FPVIe0_SH_BUS_S1,
//      S1_FPVIe_FL0 -> K89(NC) -> FPVIe0_FL_BUS_S1, group header "需闭合: 无(默认导通)".
//   2. StdAfx.h:251-253 names describe the side that gets EXCITED: SetOn on K87/K89 shorts
//      FH<->SL / FL<->SH and would degrade the four-wire measurement to two-wire; K88 switches
//      the sense to float/local. Closing them is therefore the failure mode, not the setup.
//   3. Relay state authority is the connect-map legend plus each line's 需闭合 list; relay state
//      must never be inferred backwards from a name.
// Consequence: the ONLY relays that must be closed on these paths are K83 (TM600 High->PMID) and
// K60,K61 (Low->SW); for TM601 they are K154,K155 plus K60,K61. The payload reflects this.
// t2's mitigation phrase "use the FPVIe BUS Kelvin route (K87/K88/K89)" means the route PASSES
// THROUGH those relays in their default state - it does NOT mean actuate them.
// K141/K142 stay OPEN; K86/K130 stay OPEN; K93 stays OPEN during TM601.
//
// DO NOT REVIVE THIS STALE READING: t2's hazard `limit-inconsistency` still describes the third
//   `iset` field as a "1 mA / 1 uA compliance" figure. That is superseded - the third field is the
//   RAMP TIME (TM600 1 ms, TM601 1 us). Do not carry that reading into code or review.
//
// BD-05 CITATION STRENGTHENED: the clamp re-issue requirement is not merely a Captain ruling, it is
//   stated in the manual - `knowledge/sources/fpvie.md:141-168`: "Switching between FV/FI modes
//   clears clamp settings back to 102%; within the same mode, clamp settings persist", and the
//   manual's own example re-issues SetClamp after a mode switch. Cite that source in the manifest.
//
// CLAMP-TRIGGER SEMANTICS (read this the BD-05 way: protection, never a limit):
//   the golden's own comment says 50% x 1 V = 0.5 V compliance -> "max measurable RDSON = 500 mohm".
//   Therefore at >= 500 mohm the source is clamped and the reading is NO LONGER a valid RDSON.
//   => clamp engagement is a FAILURE SIGNATURE, not a measurement result, and must never be logged
//      or evaluated as a pass/fail limit. For TM600/TM601 the expected drop is ~11 mV / 7.5 mV at
//      1 A, three orders below the 0.5 V clamp, so engagement means an open circuit or mis-wiring.
//
// MEASUREMENT-SAMPLE PROVENANCE (state it this way, it is not golden-exclusive):
//   (200, 5) is the golden's value. More averaging than any TM-level code uses - every one of the
//   56 MeasureVI calls in test.cpp is (50,5) with no (200,...) at all - but (200,10) does appear in
//   sub.cpp (x4) and BoardCheck.cpp, so the count itself is not unique to the golden. The choice is
//   correctness-neutral: it affects only noise and test time.
//
// BST-SW RAIL: ALTERNATIVE NOT ADOPTED (record, do not implement the golden's arrangement).
//   The golden builds BST-SW from two independent ground-referenced sources (BTST_ACM + SW_ACM) and
//   thereby frees an FPVIe channel. That is NOT adopted for this run, on fixture evidence rather
//   than preference: ACM200 reaches SW only and cannot reach BST, and FXVIe_PLUS reaches PMID/PGND
//   only with its low side returning to AGND_F, so it cannot form a floating pair. The golden's
//   sources are also the previous generation - live `BTST_ACM` and `PMID_FOVI` have 0 hits - so
//   adopting it would first require re-deriving live sources, with no evidence that a non-FPVIe
//   source pair able to carry BST-SW exists on this fixture.
//   PRECONDITION TO ADOPT: fixture evidence proving a reachable, float-capable non-FPVIe source
//   pair for BST-SW. (Counter-evidence to date: ACM200 does not reach BST.)
//
// TWO-PROVENANCE CORROBORATION (for the evidence chain): the archived revision pairs 11 / 7.5 mohm
//   with pmid 5 V, while DFT.csv pairs 10 / 8 mohm with pmid 15 / 9 V. That independently supports
//   the ruling that two sources coexist, with OVERVIEW governing the acceptance limits.
//
// LIMITATIONS to carry into the manifest (per the final ruling):
//   U1  relay contact current rating for the 1 A loops has no datasheet evidence
//   U2  10 kOhm series rows in the Kelvin sense path vs the FPVIe sense input spec
//   U3  FPVIe0 FL0 and FPVIe1 FL1 both land on the switched node (plausible, unproven)
//   U4  S10_CH0_A / S10_CH0_B source type is inferred, unconfirmed
//   U5  whether the default route to the high-side node must be opened while FPVIe owns it
//   U6  no sanctioned discharge role in the current relay definitions (cap gate + 1 kOhm bleed assumed)
//   U7  slot retained
//   U8  no formal rejection test for the cross path linking the high and low buses
//   U9  whether plain FPVIe_RELAY_ON suffices to activate the sense path, or whether the
//       dedicated sense-activation setting is required -> bench verification item; the
//       dedicated setting + contact mode is the documented fallback and is NOT used here
//   BD-06 TM1205 has no numeric limit in any DFT source; structural closure only
//   BD-07 TM600 'Y / 2 FLOAT' implemented as two floating nodes - a REOPENABLE assumption
// Also: BD-01 limits are 11 / 7.5 mohm (OVERVIEW, user-ruled) with DFT.csv 10 / 8 mohm retained
//   verbatim as a registered conflict - never rewritten, averaged or deleted.
// =====================================================================================
// =====================================================================
DUT_API int TM600_HS_RDSON(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *HS_RDSON = StsGetParam(funcindex, "HS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double hs_rdson[SITE_NUM] = { 0 };
    double v_meas[SITE_NUM] = { 0 };
    double i_meas[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // floating force/Kelvin pair (K83 PMID high, K60+K61 SW low) + VBAT/PMID/BST-SW caps.
    // K86/K87/K88/K89 are the channel's own force<->sense routing relays and appear in no
    // "needsClosed" set, so they are deliberately absent from this SetOn list.
    // K141/K142 (QTMU bridges) and K90/K91 (PC route) must stay open - not actuated here.
    // EXPLICIT NEGATIVE LIST (verifiable form): relays 87, 88, 89, 90, 91 must NOT appear in the
    // required-on (SetOn) set of these functions. Device-level evidence (t3): they are
    // normally-conducting contacts - one sense-float hook, two local-sense short hooks and two
    // PC-route hooks - so no action is needed for the route to pass through them, and actuating them
    // is what would break the measurement.
    // NOT A CONFLICT: the schematic IR lists only the relays that REQUIRE action, while the connect
    // map separately prints the default-conducting contacts; both are correct and they describe
    // different sets. The operative rule is about the required-on set, not about "keeping a relay
    // open".
    // [SUPERSEDED BY t50 - retained as history, NOT the operative rule] // t29 FIX - BST EXCITATION PATH (contract conformance, high severity).
    // The BST-SW rail is driven by the ground-referenced ACM200 SW12_U1REF_BST_ACM per ruling (ii).
    // K110_ACM18_BST is a DOUBLE-THROW relay and its name alone does NOT route the source to BST:
    //   S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F   (SCH-Connect-Map.txt:724)
    //   S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S   (:725)
    // i.e. un-actuated it steers the ACM18 source to the PB0 PWM pin. Only when K110 is closed does
    // the source continue to BST:
    //   ... K109(Relay-ON) -> K110(Relay-ON) -> BST_F   (:43)
    //   ... K109(Relay-ON) -> K110(Relay-NC) -> PB0_F   (:109)
    // while K109_BUSL1_PB0 selects the branch. Route requirement: CH0 Low -> BST needsClosed
    // K109,K110,... (:42; contract pinRouteTable BST/CH0 Low = [109,110,138,139,145,146]).
    // Without K110 the ACM source reaches PB0, not BST, so ruling (ii)'s "ground-referenced drive of
    // BST-SW" would not hold electrically. "The fixture may hard-wire it" is NOT an acceptable
    // omission: both the contract and the connect map require the closure.
    // Negative list: K109/K110 are NOT part of the forbidden 87/88/89/90/91 class, and the
    // unrealisable ch1 composite (K_FPVIH_TO_BST_B = 131,132,134,135) is NOT used here.
    // t50: SetOn is EXCLUSIVE - it closes ONLY the relays listed here and releases every other relay
    // (knowledge/sources/cbite-qtmue.md:80-81 "All unspecified pins are set OFF"; :92-93 the trap: two
    // separate SetOn calls release the first one's closures; the DALI precedent is TM109/110, merged into a
    // single call at :96). Therefore THIS single call IS the item's complete explicit closed set, and any
    // relay the item needs must appear here - omitting one is not "leaving it alone", it forces it OFF.
    // The defect corrected here was exactly that: the BST source leg (K48_ACM5_AMP_REF + K76_ACM_BST) was
    // absent, so ch5 could only reach PB0/SW1/SW2 (SCH-Connect-Map.txt:775/:778) and never BST (:673).
    // K46 is deliberately NOT added: it sits on the FPVIe0 high-side BUS path (the TM641/TM643 shape), not
    // on the ACM200 ch5 source path. K49 and K110 need no explicit handling - after K48 energises, its
    // COM moves to the NC contact that feeds K76, and the default throw feeding K49 is opened; K110 is
    // released by exclusivity anyway (it is still listed below because this revision retains the pair).
    // [SUPERSEDED BY t50 FINAL RULING BELOW - retained as history, NOT the operative rule] // t43 RULING (rule-reviewer, review/t43-...md, 7,439 B / d4c3835437a41c9f1bee7b15c2d381da69c99ceacd0503f5f6dbb0f1023e90a7):
    // which ACM200 channel feeds BST - ch5 (K48+K76) or ch18 (K110 as the contract relayChain spells
    // out, "S5_FH18") - is UNKNOWN(c) and needs the contract owner or bench evidence. The SAFE minimal
    // fix, which this payload implements, is the UNION: close the ch5 BST branch (K48_ACM5_AMP_REF +
    // K76_ACM_BST) IN ADDITION TO the contract-literal branch (K109/K110/K61). Neither branch alone is
    // safe: omitting K48/K76 leaves BST unreachable if ch5 is right, and DELETING K110 breaks the chain
    // if ch18 is right. The union is safe under both readings because the two branches arrive on the same
    // BST net (K76.S1.5 and K110.S1.5 both sit on BST_F_S1).
    // OPERATIONAL FACT (as instructed for t50; no mnemonic cited - knowledge/hardware/relays.md L31 is
    // referenced 0 times here):
    //   UN-ENERGISED: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F/SW1_S
    //                 (or K49(Relay-ON) -> SW2_F/SW2_S)   [SCH-Connect-Map.txt:775/:778]
    //   K48 ENERGISED: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F/BST_S
    //                 [SCH-Connect-Map.txt:673/:674]
    // i.e. K48 is a steering relay for the ch5 source: un-actuated the source lands on the SW1/SW2
    // phase nodes, actuated it is diverted to BST while the default SW1 path is broken.
    // t50 FINAL RULING (supersedes the union approach recorded above): the instrument is driven on
    // CH5 of the ACM200, so this revision closes the **ch5 single route only** - K48_ACM5_AMP_REF +
    // K76_ACM_BST. The earlier union (which also closed K109/K110) is NO LONGER applied: K109_BUSL1_PB0
    // and K110_ACM18_BST have been REMOVED from this call.
    // EVIDENCE ORDER FOR THE REMOVAL (strongest first):
    //   1. PRODUCTION BEHAVIOUR (binding) - every deployed implementation that drives
    //      SW12_U1REF_BST_ACM closes K48+K76; across the whole production tree K110_ACM18_BST and
    //      K109_BUSL1_PB0 occur 0 times, so no shipped item closes them.
    //   2. t42 independent review PASS (ACM200 pin attribution).
    //   3. CONTRACT OWNER WITHDRAWAL - the owner agreed to the removal, and the contract owner's
    //      earlier objection only existed because rev 25 was additive-only; rev 25 is now a
    //      NARROWING revision, which removes that objection.
    // K109/K110 belong to the CH18 route (S1_FPVIe_FL* -> K109 -> K110 -> BST per
    // SCH-Connect-Map.txt:43/:269; the contract's relayChain labels them "S5_FH18"), NOT to ch5.
    // Their disposition is now RULED: removed from this item.
    // NO --check-extra DISABLE is needed any more: with a single ch5 route there is no deliberate
    // over-closure, so that limitation recorded earlier in this comment is withdrawn.
    // SW side unchanged (K60 + K61); K46 is still NOT added (it is the FPVIe0 high-side BUS pin).
    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);
    delay_ms(3);  // NOT in the pulse window: power-up relay settle after Step 1, before any force
                  // is applied. The 2 ms HARD CAP is judged between force and de-assert only.

    // ====== Step 2: Power On (BST staircase, BST always leads PMID by 5 V) ======
    // ATE excitation per the plan (DFT/OVERVIEW, BD-08): PMID 15 V, VBAT 4.2 V, VDRV 5 V.
    // The register-config simulation levels (3.5 / 5 V) are reference only, never excitation.
    // Range rule (units.md:3-5): range >= 2x the set value, nearest-to-2x smallest step.
    // A 0 V / 0 A initialization has no 2x requirement, so the MINIMAL compliant step is used
    // (FPVIe_10UA), which is also the unified off-range current side required by R-POFF-06.
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10UA, FPVIe_RELAY_ON);
    delay_us(200);
    VBAT_PD3_FXVI.Set(FV, 4.2, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    // step 1: PMID 0 V, BST-SW 5 V
    SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    // step 2: PMID 5 V, BST-SW 5 V
    SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 10, FXVIe_PLUS_20V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    // step 3: PMID 10 V, BST-SW 5 V
    SW12_U1REF_BST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_30V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    // step 4: PMID 15 V, BST-SW 5 V (FET on -> SW follows PMID)
    SW12_U1REF_BST_ACM.Set(FV, 20, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config (reg_config/tm600.sv; BD-03) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
    I2CWriteSameData(DEV_ADDR, 0x5A, 0x02);  // D2A_BUBO_TM_HSON=1 (HS FET forced on)
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // D2A_BUBO_EN_FORCE_ON=1
    delay_ms(1);

    // ====== Step 4: Measure (three-stage high-current init, then a short 1 A pulse) ======
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    // BD-05 (user-adjudicated, CLOSED): provisional engineering default, non-datasheet,
    // NOT a pass/fail criterion, not authorised for hardware execution. 50% x 1 V = 0.5 V.
    // Re-issued after every force/measure mode switch (the switch clears it back to 102%).
    // STRICTER THAN THE GOLDEN PRECEDENT: the archived golden sets the clamp only once;
    // the re-issue is a manual requirement (knowledge/sources/fpvie.md:141-168), not a deviation.
    FPVI0.SetClamp(50, 50);
    // Sign derivation (captain ruling, contract signConventionFinding step3): step1 alias direction
    // pmid2sw = PMID->SW; step2 instrument terminals = HIGH->PMID (K83), LOW->SW (K60,K61);
    // step3 assumed convention positive FI drives current OUT of the HIGH terminal => +1 A gives
    // the DFT literal PMID->SW. The convention itself is U11 bring-up verification, not an
    // established fact (no header or manual in this workspace states it).
    FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);   // +1 A (DFT literal), ramp 1 ms
    delay_ms(1);  // 1 ms + 1 ms = 2 ms <= 2 ms HARD CAP (user ruling)
                  // settlement 1 ms + acquisition 200 x 5 us = 1 ms => the WHOLE 1 A force duration
                  // (settle + acquisition) is within the user-stated HARD CAP, whose purpose is to limit
                  // DUT/relay thermal and stress. deliberate deviation: golden used delay_us(2000) and the
                  // golden form is itself ~3 ms; an explicit hard cap governs over a precedent form.
    FPVI0.MeasureVI(200, 5, FPVIe_MV_X10);                   // 200 samples (golden value)
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);    // remove the pulse immediately
    FOR_EACH_VALID_SITE(site)
    {
                // F5 SIGN PREMISE (this function only): the force is the DFT literal +1 A with the high terminal
        // on PMID, so a correct measurement has BOTH MVRET and MIRET positive; the ratio is positive and
        // is reported as a positive magnitude in milliohm. The mirrored force direction used by the
        // companion low-side item is described in that function alone, not here.
        // F5 DIVISION GUARD: dividing by a measured current of ~0 would yield inf/NaN and a bogus
        // RDSON. The idiom follows existing project code (test.cpp:8087-8090) but uses a physically
        // meaningful floor, not an epsilon: 0.1 A = 10% of the 1 A nominal force, a PROVISIONAL
        // engineering default (bench-signoff-required). The failure path below reports ERROR_RES, NOT a
        // zero or small value, so an absent-force or wrong-polarity condition fails closed.
        v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED
        i_meas[site] = FPVI0.GetMeasResult(site, MIRET);     // measured loop current, SIGNED (sign kept for the check)
        // R-VIR, POSITIVE MAGNITUDE. Same sign is normal (|MVRET|/|MIRET|); OPPOSITE sign means the
        // polarity or the fixture is wrong and is a FAILURE, never expressed as a negative resistance.
        // Fail-CLOSED: below the 0.1 A floor, or on a sign mismatch, the item reports ERROR_RES (9999,
        // Test_Method.h:32) exactly as the project precedent does (test.cpp:8087-8090: else
        // gain[site] = ERROR_RES) instead of a small resistance that could read as a pass.
        if (i_meas[site] > 0.1 && v_meas[site] * i_meas[site] > 0.0)
            hs_rdson[site] = fabs(v_meas[site]) / fabs(i_meas[site]) * 1e3;  // mohm, positive magnitude
        else
            hs_rdson[site] = ERROR_RES;  // ERROR_RES = 9999; no current (|I| <= 0.1 A), or an MVRET/MIRET
                                     // sign mismatch, i.e. reverse polarity or a fixture fault
    }

    // ====== Step 5: Power Off (FET kept on, BST and PMID ramp down together) ======
    SW12_U1REF_BST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 10, FXVIe_PLUS_20V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // unified RELAY_OFF ranges (FPVIe 1V/10MA, NOT the 10 A range); floating channel last
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    FPVI1.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);  // channel 1 (BST-SW loop) releases first
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);  // measurement channel releases LAST (R-POFF-04)

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        HS_RDSON->SetTestResult(site, 0, hs_rdson[site]);
    }
    return 0;
}

// =====================================================================
// TM601: LS_RDSON -- low-side power-FET RDSON (MV&MI, 1 A floating force)
// DFT OVERVIEW: Rds,on=(SW-PGND)/IPMID2SW ; DFT.csv rec 20: iset[sw2pgnd,1,1e-6,0]
//   acceptance limit 7.5 mohm (OVERVIEW row 133, user-adjudicated BD-01);
//   DFT.csv 8 mohm retained verbatim as a registered conflict (no fold/average)
// Loop: FPVIe0 CH0, INVERTED orientation - high -> PGND (K154,K155), low -> SW (K60,K61),
//   because PGND hangs off FPVIe0_FH_BUS_S1 and SW off FPVIe0_FL_BUS_S1. Current flows
//   PGND -> source -> SW -> LS FET -> PGND, so the sensed drop is the LS FET drop.
// K93_AGND2PGND must stay OPEN or PGND is tied to AGND_F (SD-3).
// Register side bit differs from TM600: 0x5A=0x01 (LSON), not 0x02 - the opposite FET.
// =====================================================================
DUT_API int TM601_LS_RDSON(short funcindex, LPCTSTR funclabel)
{
    //{{AFX_STS_PARAM_PROTOTYPES
    CParam *LS_RDSON = StsGetParam(funcindex, "LS_RDSON");
    //}}AFX_STS_PARAM_PROTOTYPES

    double ls_rdson[SITE_NUM] = { 0 };
    double v_meas[SITE_NUM] = { 0 };
    double i_meas[SITE_NUM] = { 0 };

    // ====== Step 1: Connect ======
    // floating force/Kelvin pair SW<->PGND (PGND high via K154+K155, SW low via K60+K61)
    // plus the VBAT/PMID caps. K93_AGND2PGND deliberately not actuated (must stay open, SD-3).
    // FR-001 REVERSE - CLOSURES LIMITED TO THE RAIL THIS FUNCTION ACTUALLY POWERS.
    // This item powers SW (low side) and PGND (high side), both on FPVIe0 CH0:
    //   CH0 Low  -> SW   [Kelvin] needsClosed: K60,K61   (SCH-Connect-Map.txt:174)
    //   CH0 High -> PGND [Kelvin] needsClosed: K154,K155 (SCH-Connect-Map.txt:156)
    // K57 IS closed on purpose: K57_CAP_BST_SW (:220) sits on SW via Cap_SW_BST_S1 220nF
    //   ("SW 稳压 needsClosed: K57", :904), and SW is the node the 1 A measurement current
    //   actually traverses (the force returns through the low terminal), so FR-001's reverse
    //   requirement is supported by the wiring here.
    // K5_VBUS_Cap IS NOT CLOSED - the earlier rationale was wrong and is withdrawn. This function
    //   does not power VBUS: the low-side group reaches SW through K60,K61 and VCP through K60,
    //   whereas VBUS is reached only via CH0 Low -> VBUS needsClosed: K3 (:213) or the CH1 route
    //   K138,K139,K145,K146,K3 (:421). The VBUS token is present in this item's meta powered_pins,
    //   but meta presence is not proof that THIS function drives the rail, and no K3 closure exists
    //   here. Closing K5 would switch in a 4.7uF branch on the vendor's VBUS bulk cap for a rail
    //   that is not energised on the tester side - (V-B) an exception, not a silencer.
    // K44_Cap_SW2_BST2 (:205) and K45_Cap_SW1_BST1 (:206) ARE NOT CLOSED - SW1 and SW2 are
    //   DIFFERENT NODES from SW: SW1 needs K46 (:177), SW2 needs K46+K49 (:183), and this function
    //   routes to neither. They are flagged only because the gate folds the family by PREFIX
    //   (cap_pin("K45_Cap_SW1_BST1") -> SW1_BST1, then fam_intersect matches the powered pin "SW"
    //   because "SW1_BST1".startswith("SW")) - a name-prefix collision across distinct rails.
    //   Closing K44/K45 would energise rails this item does not use.
    // SETTLING IS NOT ANALYSED, and this is NOT an assertion of inertness: K57 is a pin-to-cap
    //   branch (220nF) that changes the RC settling of the very rail being measured. With F6 giving
    //   ZERO on-paper margin inside the 2 ms force window, the effect on settling is a BRING-UP
    //   VERIFICATION ITEM (with U11), to be measured on hardware - not argued away here.
    // t29 PER-FUNCTION JUSTIFICATION - WHY THIS ITEM DOES NOT CLOSE K109/K110 (explicit, not omitted).
    // Contract authority, both checked in setup-contract.json (rev 24):
    //   * pinRouteTable: this item's table has nodes SW, PGND, PMID, VBUS, VBAT, VDRV, V1P5, AGND and NO "BST"
    //     node at all - so it declares no BST route and no BST needsClosed. Contrast TM600, whose table does
    //     carry /BST/... with needsClosed [109,110,...] (CH0 Low) and [109,110] (CH1 Low).
    //   * tmDeltas.TM601.relaySet does NOT contain 109 or 110 (it is [3,7,60,61,83,86,130,132,133,134,135,...]),
    //     whereas tmDeltas.TM600.relaySet contains both.
    //   * Stimulus: this item's ateStimulus is {vbat 4.2 V, pmid 9 V, vdrv 5 V} only; there is no bst2sw
    //     stimulus and bst2sw occurs 0 times in its whole delta. Its single textual "BST" is the register
    //     field D2A_BUBO_TM_LSON, not a powered rail.
    // Physical consequence (the reason the distinction is real and not pedantic): the ACM200 bootstrap source
    // is only steered to BST when K110 is closed - S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F
    // (SCH-Connect-Map.txt:724) and SH18 -> K110(NC) -> PB0_S (:725), while the BST path requires
    // K109(ON) -> K110(ON) -> BST_F (:43, and :268/:269 for CH1). t38 REMOVED the ACM excitation that
    // used to be switched on in this function: it was a DANGLING drive - the source was commanded to 5 V
    // but, with K110 un-actuated, it landed on PB0 and never reached BST. Removing it is the correct
    // remedy rather than closing K109/K110, because this item has NO BST requirement in any source:
    //   * DFT.csv - its row (L98) declares no bst2sw stimulus (the TM600 row declares none either);
    //   * setup-contract - TM601.pinRouteTable has NO BST node, TM601.relaySet contains neither 109 nor 110,
    //     and aliasResolution[3] (bst2sw) lists usedByTm = TM600 and TM1205 only;
    //   * netlist (SCH-Connect-Map.txt) - the only paths to BST need K109(ON)+K110(ON) (:42/:43), which no
    //     authority assigns to this item.
    // Closing K109/K110 here would therefore be an unmotivated relay actuation on a rail the item does not use.
    // Relay-contact nuance (knowledge/hardware/relays.md L3-31): K110 is a G6K-2G-Y DPDT LATCHING relay whose
    // pins 2 and 7 are marked NO yet CONDUCT when unpowered ("默认 2-3 通、6-7 通"; the file warns this is the
    // opposite of a spring relay). So the connect-map notation "K110(Relay-NC)" denotes the UN-ACTUATED path,
    // i.e. K110(Relay-NC) -> PB0 is the state with K110 NOT set. Actuating K110 (SetOn) switches COM1 to pin 4
    // and COM2 to pin 5, which is the leg that continues to BST_F. Hence: not actuated -> PB0, actuated -> BST.
    // SW side is complete as required: CH0 Low -> SW needsClosed K60,K61 (:174) and both are closed, and the
    // SW stabiliser K57_CAP_BST_SW (Cap_SW_BST_S1, :904) remains closed.
    // Minimal-endpoint discipline: no relay outside this item's contract authority is closed, the negative-list
    // relays (87/88/89/131/132/133, Relay-NC default-conducting) are NOT actuated, and the composite macros
    // K_FPVIH_TO_BST_B / K_FPVIL_TO_SW_B are NOT used (ruling (ii) records that route as unrealisable).
    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);
    delay_ms(3);  // NOT in the pulse window: power-up relay settle after Step 1, before any force
                  // is applied. The 2 ms HARD CAP is judged between force and de-assert only.

    // ====== Step 2: Power On ======
    // ATE excitation per the plan (DFT/OVERVIEW, BD-08): VBAT 4.2 V, PMID 9 V, VDRV 5 V.
    // Range rule (units.md:3-5): range >= 2x the set value, nearest-to-2x smallest step.
    // A 0 V / 0 A initialization has no 2x requirement, so the MINIMAL compliant step is used
    // (FPVIe_10UA), which is also the unified off-range current side required by R-POFF-06.
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10UA, FPVIe_RELAY_ON);
    delay_us(200);
    VBAT_PD3_FXVI.Set(FV, 4.2, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);
    delay_us(200);
    PMID_HG2_FXVI.Set(FV, 9, FXVIe_PLUS_20V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_us(200);

    // ====== Step 3: Register Config (reg_config/tm601.sv; BD-03) ======
    entertestmode();
    I2CWriteSameData(DEV_ADDR, 0x10, 0x43);  // WAKE_UP=1
    I2CWriteSameData(DEV_ADDR, 0x59, 0x20);  // D2A_BUBO_TM_DIS_CLK=1
    I2CWriteSameData(DEV_ADDR, 0x5A, 0x01);  // D2A_BUBO_TM_LSON=1 (LS FET forced on)
    I2CWriteSameData(DEV_ADDR, 0x61, 0x4B);  // D2A_BUBO_EN_FORCE_ON=1
    delay_ms(5);  // NOT in the pulse window: register/sequence interval BEFORE the force is
                  // applied (DFT row context). The 2 ms HARD CAP is judged between the force
                  // statement and the de-assert only (1 ms settle + 1 ms acquisition = 2 ms).

    // ====== Step 4: Measure (three-stage init, then a short 1 A pulse) ======
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    // BD-05 (user-adjudicated, CLOSED): provisional engineering default, non-datasheet,
    // NOT a pass/fail criterion, not authorised for hardware execution. 50% x 1 V = 0.5 V.
    // Re-issued after every force/measure mode switch (the switch clears it back to 102%).
    // STRICTER THAN THE GOLDEN PRECEDENT: the archived golden sets the clamp only once;
    // the re-issue is a manual requirement (knowledge/sources/fpvie.md:141-168), not a deviation.
    FPVI0.SetClamp(50, 50);
    // Sign derivation (captain ruling, contract signConventionFinding step3): step1 alias direction
    // sw2pgnd = SW->PGND; step2 instrument terminals = HIGH->PGND (K154,K155), LOW->SW (K60,K61);
    // step3 with PGND on the HIGH terminal the commanded sign is the OPPOSITE of the DFT literal,
    // so -1 A (DERIVED, not +1 A). MIRET is read through fabs(), so the magnitude is unaffected.
    // U11 bring-up check: confirm the conducting device is the one BD-03 enables (0x5A=0x01 LS),
    // that |MVRET|/|MIRET| lands near 7.5 mohm (not a ~0.6-0.7 V body-diode drop), and that
    // |MIRET| matches the programmed value; if the driven device is wrong, flip the sign FOR THIS
    // ITEM ONLY with hardware evidence (never a-priori).
    FPVI0.Set(FI, -1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);  // -1 A (derived), ramp 1 us
    delay_ms(1);  // 1 ms + 1 ms = 2 ms <= 2 ms HARD CAP (user ruling)
                  // settlement 1 ms + acquisition 200 x 5 us = 1 ms => the WHOLE 1 A force duration
                  // (settle + acquisition) is within the user-stated HARD CAP, whose purpose is to limit
                  // DUT/relay thermal and stress. deliberate deviation: golden used delay_us(2000) and the
                  // golden form is itself ~3 ms; an explicit hard cap governs over a precedent form.
    FPVI0.MeasureVI(200, 5, FPVIe_MV_X10);                   // 200 samples (golden value)
    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);    // remove the pulse immediately
    FOR_EACH_VALID_SITE(site)
    {
        // F5 SIGN PREMISE: MVRET stays SIGNED (only MIRET is folded). TM601 forces the DERIVED -1 A
        // because PGND sits on the HIGH terminal, so the expected differential is negative and the
        // magnitude is expected negative; a POSITIVE reading is the polarity/fixture diagnostic.
        // F5 DIVISION GUARD: same 0.1 A floor as TM600 (10% of nominal 1 A, PROVISIONAL and
        // bench-signoff-required). Below the floor the item reports 0 mohm so an absent-force fault
        // reads as zero current rather than an inf/NaN RDSON.
        v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED
        i_meas[site] = FPVI0.GetMeasResult(site, MIRET);     // measured loop current, SIGNED (sign kept for the check)
        // R-VIR, POSITIVE MAGNITUDE. This item forces the DERIVED -1 A (PGND is on the HIGH terminal),
        // so a correct result has BOTH MVRET and MIRET negative; the ratio is then positive and is
        // reported as a magnitude. A positive MVRET with a negative MIRET is the polarity/fixture fault
        // and is reported through the failure path below, never as a negative resistance.
        // Fail-CLOSED: below the 0.1 A floor, or on a sign mismatch, report ERROR_RES (9999,
        // Test_Method.h:32) per the project precedent (test.cpp:8087-8090) rather than a low value.
        if (i_meas[site] > 0.1 && v_meas[site] * i_meas[site] > 0.0)
            ls_rdson[site] = fabs(v_meas[site]) / fabs(i_meas[site]) * 1e3;  // mohm, positive magnitude
        else
            ls_rdson[site] = ERROR_RES;  // ERROR_RES = 9999; no current (|I| <= 0.1 A), or an MVRET/MIRET
                                     // sign mismatch, i.e. reverse polarity or a fixture fault
    }

    // ====== Step 5: Power Off (no bootstrap ramp: the LS FET has no bootstrap) ======
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
    delay_ms(1);
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
    delay_ms(1);
    // unified RELAY_OFF ranges (FPVIe 1V/10MA, NOT the 10 A range); floating channel last
    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);

    // ====== Step 6: LogData ======
    FOR_EACH_VALID_SITE(site)
    {
        LS_RDSON->SetTestResult(site, 0, ls_rdson[site]);
    }
    return 0;
}
