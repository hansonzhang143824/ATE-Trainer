# TM109 Resource and Configuration Contract

- Revision: 2
- Role: test-strategy-architect
- Verdict: `deliverable_ready`
- JSON SHA-256: `a22502ece50f321312a466b77cfef5a40efe8f9a41995f7ee8af3b44048107e2`

## Classification

| Field | Value |
| --- | --- |
| projectType | normal (一般测试项目) |
| parameterType | UVLO family, specific parameter PRST |
| functionArchitecture | single TM109 item function; one stimulus endpoint (VAC2) plus one check endpoint (INT) plus one initial-condition rail (VBAT) |

## Source allocation and routes

| Endpoint | Source table | Channel | Route | Actuated relays |
| --- | --- | --- | --- | --- |
| VBAT | FXVIe_PLUS S3 ch5 | S3_FXVIe_PLUS_FH5 (force), S3_FXVIe_PLUS_SH5 (sense) | S3_FXVIe_PLUS_FH5 -> K8_PD3_S1(un-actuated) -> VBAT_F_S1; S3_FXVIe_PLUS_SH5 -> K8_PD3_S1(un-actuated) -> VBAT_S_S1 | none |
| VAC2 | ACM200 S5 ch0 | S5_ACM200_FH0 (force), S5_ACM200_SH0 (sense) | S5_ACM200_FH0 -> K19_VAC2_S1(actuated) -> K70_VAC_F_S1(actuated) -> VAC2_F_S1; S5_ACM200_SH0 -> K19_VAC2_S1(actuated) -> VAC2_S_S1 | K19, K70 |
| INT | ACM200 S5 ch15 | S5_ACM200_FH15 (force), S5_ACM200_SH15 (sense) | S5_ACM200_FH15 -> K102_PC3_S1 (un-actuated/default conducting) -> INT_F_S1; S5_ACM200_SH15 -> K102_PC3_S1 (un-actuated/default conducting) -> INT_S_S1 | none |

## Relay groups

### RG-1: EP-VBAT

- Purpose: hold the VBAT rail from FXVIe_PLUS ch5
- Path relays: []
- Isolation: K8_PD3_S1 must remain un-actuated on this route (it selects the PD3/VBAT pair on the FXVIe_PLUS ch5 leg); K7_BUSH_VBAT_S1, K143_DCM_BUS0_H_S1, K144_DCM_BUS1_H_S1, K130_KELVIN1_F_S1, K136_QVMH_BUS0_S1, K131_KELVIN1_S1S2, K132_KELVIN1_S1, K141_QTMU_BUSA_S1S2 are not part of the selected closure set; they belong to the FPVIe/QVM/QTMU/DCM BUS candidate routes to the same pin (recorded in the same pin record's relayChainUnion)

### RG-2: EP-VAC2

- Purpose: connect ACM200 ch0 to VAC2 (force leg to VAC2_F, sense leg to VAC2_S)
- Path relays: [{"relay": "K19_VAC2", "number": 19, "instance": "K19_VAC2_S1", "state": "actuated", "recordedToken": "ON", "usedBy": ["force leg", "sense leg"]}, {"relay": "K70_VAC_F", "number": 70, "instance": "K70_VAC_F_S1", "state": "actuated", "recordedToken": "ON", "usedBy": ["force leg"]}]
- Isolation: Share/select siblings on the same ACM200 ch0 force group must stay un-actuated: K18_VAC3_S1 (VAC3 side), K20_AMUX_S1 (AMUX side), K68_VCP_F_S1 (VCP side); the group's resource list [18,19,20,68,70] spans five different DUT pins, so actuating more than the target side would land the same instrument on a non-target pin; K82_R_CS_S1S2, K87_KELVIN0_S1S2, K89_KELVIN0_S1S2, K90_PC0_Force_S1, K133_KELVIN1_S1S2, K142_QTMU_BUSB_S1S2, K145_DCM_BUS0_L_S1, K146_DCM_BUS1_L_S1, K138_QVML_BUS0_S1, K139_QVML_BUS1_S1, K17_BUSL_VAC_S1 are not required by the selected route

### RG-3: EP-INT

- Purpose: connect ACM200 ch15 to the INT check endpoint; test-method-expert selects monitor/measurement configuration
- Path relays: []
- Isolation: if the ACM200 ch15 candidate is used: K102_PC3_S1 must remain un-actuated, because the INT_F_S1 record's own chain token for it is NC while PC3_F_S1 is a separate candidate sink of the same source port (INFERENCE, direction not re-proved here — OI-S-03); K101_BUS_FH_PA0_S1, K130_KELVIN1_F_S1, K136_QVMH_BUS0_S1, K137_QVMH_BUS1_S1, K143_DCM_BUS0_H_S1, K144_DCM_BUS1_H_S1, K131_KELVIN1_S1S2, K132_KELVIN1_S1, K141_QTMU_BUSA_S1S2 are not required by the candidate routes with zero actuations

## Register delta

| Order | Call | Details |
| --- | --- | --- |
| 1 | entertestmode | argsRaw=[]; scope=per-TM item; type=unlock-call (no register value asserted here) |
| 2 | I2CWriteSameData | deviceAddrSymbol=DEV_ADDR; reg=0x55; data=0x96; dftFieldCommentVerbatim=field[(EN_DTEST0,1),(DTEST0_MUX,22)]; fields=[{'field': 'EN_DTEST0', 'annotationValueVerbatim': '1', 'class': 'DFT annotation, not an independently derived bit field'}, {'field': 'DTEST0_MUX', 'annotationValueVerbatim': '22', 'class': 'DFT annotation, not an independently derived bit field'}]; scope=per-TM item delta (this contract asserts no global Setup register state); fieldExpansion=UNRESOLVED — dft-meta.json tms.TM109.dftRegisterConfig.note states DFT.csv supplies no register map and that field names, widths and values are neither re-derived nor expanded; this contract keeps that position (OI-S-06 companion) |
| rule | rule | rule=register writes require the test-mode unlock sequence first; ruleSource=knowledge/standards/register-config.md:12-22; appliesTo=the delta above; boundaryNote=the placement/ordering of this configuration inside the item flow is a test-method-stage decision and is not decided here; global Setup register state belongs to the setup-architect baseline (knowledge/standards/register-config.md:40 boundary rule) |

## Handoff to test method

- VBAT: FXVIe_PLUS S3 ch5 (FH5 force + SH5 sense) with the closure set empty; K8_PD3 un-actuated
- VAC2: ACM200 S5 ch0 (FH0 force + SH0 sense) with the closure set {K19_VAC2, K70_VAC_F}; the ACM200 ch0 group's other select relays (K18/K20/K68) must stay un-actuated
- INT: ACM200 S5 ch15 (FH15 force + SH15 sense), closure set empty; K102_PC3 remains un-actuated. Observation mode, sampling and limits are test-method decisions.

## Open items (non-blocking unless stated)

- `TM109-OI-2`: TM109 states its expectation only as descriptive text. DFT.csv provides no numeric minimum, maximum, or pass-fail bound.
- `TM109-OI-3`: TM109's row states no ramp rate, delay, settle time, or sampling window for the four Dynamic steps.
- `TM109-OI-4`: The 'Function Name' cell is empty for TM109, so no function name is available from the DFT source.
- `TM109-OI-5`: The ExpectValue text names only a rising threshold plus hysteresis, while the Dynamic stimulus also contains falling steps. DFT.csv states no falling-threshold value.
- `OI-S-01`: The frozen deliverables publish per-pin aggregated actuation sets (resources) and per-pin relayChainUnion only. The authoritative per-path required_on list is not among this trial's deliverables, so every per-source activation count in this contract is a derived estimate rather than a published per-path fact.
- `OI-S-02`: No Cap2 relay for VBAT or VAC2 and no pull-up relay for the check endpoint can be identified from the frozen DALI relay table; the knowledge layer names such relays but those names/numbers are not present in the frozen table (conflict C-04).
- `OI-S-03`: The check endpoint INT has two candidate routes with zero required actuations (ACM200 ch15 force/sense ports and S24_P14), so relay count does not order them, and choosing the observing instrument is not this stage's decision. The endpoint's source table, slot and channel are therefore recorded UNRESOLVED with the full candidate set.
- `OI-S-04`: The type of S10_CH0_A / S10_CH0_B is inferred from a slot name and needs confirmation (conflict C-03).
- `OI-S-05`: S24_P14 is recorded with type DCM, channel 14 and role F but with empty role/domain strings; its capability and intended use are not asserted by the frozen deliverables.
- `OI-S-06`: DFT.csv labels no vset/iset argument position; the third and fourth arguments (100e-6 / 1e-3 and the trailing 1) and the Hardware_initial arguments (100e-6, 0) are recorded positionally and verbatim only. No voltage/current/range/limit meaning is assigned by this contract, so capability checks (current magnitude, range) cannot be completed from this source.
- `OI-S-07`: Chain-context relay state tokens (ON vs NC) versus actuation semantics are not defined inside the frozen deliverables; this contract reads NC as the un-actuated/default-conducting contact because that is how the same record uses the token for a zero-actuation route, and marks the reading as INFERENCE (conflict C-01).
- `OI-S-08`: The DFT check token "INT" and the configured DTEST0 mux annotation coexist without any frozen deliverable binding the two (conflict C-06). No observation-semantics interpretation is made by this contract.
- `OI-S-09`: The frozen relay table contains 101 entries and every entry carries a dutPins list; the deliverables do not state whether this set is the complete relay population of the board, so the absence of a Cap/pull-up entry (C-04) cannot be converted into a claim about the hardware.

## Evidence

- `project/DALI/input/DFT.csv` — data record 9 of 35; physical lines 30-34; columns Item / Function Name / ShortName / ExpectValue / Unit / Trim / Record / Hardware_initial / Software_initial / Dynamic / Check / Type; columns in scope: Hardware_initial, Software_initial, Dynamic, Check, Type, ShortName, ExpectValue
- `project/DALI/schematic-ir.json` — canonical connectivity source referenced by the frozen schematic deliverables
- `team/artifacts/tm109-direct-trial/input-manifest.json` — canonicalInputs.dft.status = ready, canonicalInputs.schematic.status = ready, missingOrStaleOutputs = []
- `team/artifacts/tm109-direct-trial/dft/dft-meta.json` — tms.TM109.identity / rawIntent.rawRow / pinConditions (hardwareInitial, dynamic, checkEndpoint, argSemantics) / limits / dftRegisterConfig / explicitRelations / openItems / handoff / sourceLocations.tm109RecordSpan
- `team/artifacts/tm109-direct-trial/dft/dft-conditions.yaml` — rawIntent.rawRow + derivedTokens.vsetPins
- `team/artifacts/tm109-direct-trial/schematic/SCH-Connect-Map.json` — tmScope / candidatePaths.pinCentric (PIN_VBAT_F_S1, PIN_VBAT_S_S1, PIN_VAC2_F_S1, PIN_VAC2_S_S1, PIN_INT_F_S1, PIN_INT_S_S1) / candidatePaths.sourceCentric (SRC_S3_FXVIe_PLUS_FH5/SH5, SRC_S5_ACM200_FH0/SH0/FH15/SH15, SRC_S10_CH0_A/B, SRC_S1_FPVIe_FH0/SH0/FL0/SL0, SRC_S8_QVM_CH0+/-, SRC_S24_P14) / relayChainIndex / consistencyNotes / outOfScopeFlagsForDownstream / counts
- `team/artifacts/tm109-direct-trial/schematic/schematic-ir.json` — paths[] records for VBAT_F_S1 / VBAT_S_S1 / VAC2_F_S1 / VAC2_S_S1 / INT_F_S1 / INT_S_S1; relays[] (101 entries); pins[]; nets[] (NetCap1_VBAT_S1_1, NetCap1_VAC2_S1_1, NetK19_VAC2_S1_5, NetK102_PC3_S1_7, NetK102_PC3_S1_2); pinsPerTm
- `team/artifacts/tm109-direct-trial/schematic/Components-Statistic.json` — declared counts (key level only)
- `knowledge/references/L3-method/relay-design-flow.md` — lines 36-75 (eight-step main flow) and 78-88 (execution key points)
- `knowledge/references/L3-method/path-principles.md` — line 6 (precision gate), line 8 (shortest path), line 11 (measured VBAT ranking), line 19-24 (relay sharing/conflict degradation), line 28 (single-ended-to-ground excludes FPVIe), lines 32-37 (capability whitelist)
- `knowledge/standards/relay-checklist.md` — lines 6-13 (closed-loop rule for non-floating vs floating sources), lines 19-24 (BUS relay decision table), lines 27-41 (Cap2 rule and DALI Cap family), lines 44-50 (anti-short rule, Share relays), lines 52-69 (path classification)
- `knowledge/standards/test-types.md` — line 36 (UVLO family incl. PRST), line 60 (general test item class), lines 76-86 (threshold tests are AWG; method choice is not made here)
- `knowledge/references/L3-method/voltage-threshold-ate.md` — lines 11-22 (PRST naming and representative project), line 32 (observation and edge convention — referenced only, not decided here)
- `knowledge/references/L1-chip/UVLO.md` — lines 7-22 (threshold + hysteresis concept; indicator pin of the family)
- `knowledge/standards/register-config.md` — lines 12-22 (test-mode unlock before register writes), line 40 (global Setup vs per-TM delta boundary)
- `knowledge/hardware/pin-resource-map.md` — lines 5-19 (pin to resource quick table), lines 32-45 (relay quick table)
- `knowledge/hardware/pin-resource-map.md` — INT / SDA -> SDA_INT_ACM -> ACM200; relay notes K43_SDA_INT and K58_INT_PU
