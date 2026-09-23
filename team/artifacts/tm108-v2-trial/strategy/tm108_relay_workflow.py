# -*- coding: utf-8 -*-
"""TM108 (VAC1_PRST) mandatory eight-step relay workflow evidence generator (t4).

Owner: test-strategy-architect · run: tm108-v2-trial
Read-only with respect to every project path. The ONLY writes are the evidence
files inside this task's in-scope directory
(team/artifacts/tm108-v2-trial/strategy/).

Closure sets are derived from the per-path PROOF records
(`project/DALI/path_proofs.json.txt` -> `accepted_path_proofs[].required_on`
plus the full `path[]` relay chain), transcribed for the TM108 terminals by the
schematic expert into `team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.json`.

They are deliberately NOT derived from:
  * `schematic-ir.json pins[].requiredRelays` (documented as an INTERSECTION of
    all proofs for that pin, therefore incomplete - see schematic-fact-audit
    section 3.2), or
  * `schematic-ir.json relays[].state` (a single-valued default/comparison state
    that cannot express whether a relay must be actuated on a given path - see
    schematic-fact-audit I-1 / C-1).

Usage:
    python tm108_relay_workflow.py            # print the workflow
    python tm108_relay_workflow.py --write    # also write step-01..step-08 .txt
"""
import io
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                       # team/artifacts/tm108-v2-trial
PROOFS = RUN / 'schematic' / 'tm108-paths-proofs.json'
MAP = pathlib.Path('project/DALI/SCH-Connect-Map.txt')
CS = pathlib.Path('project/DALI/Component-Statistic.txt')
IR = pathlib.Path('project/DALI/schematic-ir.json')

TM = 'TM108'

# ---------------------------------------------------------------- DFT intent
# endpoint -> (role, DFT basis, source-of-intent citation)
DFT_ENDPOINTS = {
    'VBAT': 'power / static supply rail -> DFT Power column "VBAT"',
    'VAC1': 'dynamic / scanned input -> DFT Dynamic column "VAC1"',
    'DTEST0': 'check / observation -> DFT Check column "V(DTEST0)"',
    'AGND': 'reference return (board-level; not a DFT column)',
    'KLV1': 'NOT required by this TM (no DFT column, no ramp, no measurement)',
    'KLV2': 'NOT required by this TM (no DFT column, no ramp, no measurement)',
}

# proof terminal -> endpoint it serves in this TM
TERMINAL_ENDPOINT = [
    ('VAC1_F_S1', 'VAC1 force side'),
    ('VAC1_S_S1', 'VAC1 sense side'),
    ('VBAT_F_S1', 'VBAT force side'),
    ('VBAT_S_S1', 'VBAT sense side'),
    ('nQON_F_S1', 'observation candidate (nQON, force side)'),
    ('nQON_S_S1', 'observation candidate (nQON, sense side)'),
    ('AGND_F_S1', 'reference, force side'),
    ('AGND_S_S1', 'reference, sense side'),
]

# source-port -> project-side object, all verified against the source-definition
# headers (Pin_Channel_define.h / StdAfx-style extern list) and Component-Statistic.
DEF_SOURCES = [
    ('S5_ACM200_FH0', 'ACM200', 'VAC123_AMUX_ACM',
     '_PIN_CHANNEL_DEFINE_VAC123_AMUX_ACM_ = "S5_0,..."', 'Pin_Channel_define.h:15', 'extern ACM200 VAC123_AMUX_ACM;', 'Pin_Channel_define.h:96', 'Component-Statistic.txt:382'),
    ('S5_ACM200_SH0', 'ACM200', 'VAC123_AMUX_ACM',
     '_PIN_CHANNEL_DEFINE_VAC123_AMUX_ACM_ = "S5_0,..."', 'Pin_Channel_define.h:15', 'extern ACM200 VAC123_AMUX_ACM;', 'Pin_Channel_define.h:96', 'Component-Statistic.txt:408'),
    ('S5_ACM200_FH9', 'ACM200', 'NQON_HG1_ACM',
     '_PIN_CHANNEL_DEFINE_NQON_HG1_ACM_ = "S5_9,..."', 'Pin_Channel_define.h:24', 'extern ACM200 NQON_HG1_ACM;', 'Pin_Channel_define.h:105', 'Component-Statistic.txt:405'),
    ('S5_ACM200_SH9', 'ACM200', 'NQON_HG1_ACM',
     '_PIN_CHANNEL_DEFINE_NQON_HG1_ACM_ = "S5_9,..."', 'Pin_Channel_define.h:24', 'extern ACM200 NQON_HG1_ACM;', 'Pin_Channel_define.h:105', 'Component-Statistic.txt:431'),
    ('S3_FXVIe_PLUS_FH5', 'FXVIe_PLUS', 'VBAT_PD3_FXVI',
     '_PIN_CHANNEL_DEFINE_VBAT_PD3_FXVI_ = "S3_5,..."', 'Pin_Channel_define.h:12', 'extern FXVIe_PLUS VBAT_PD3_FXVI;', 'Pin_Channel_define.h:93', 'Component-Statistic.txt:308'),
    ('S3_FXVIe_PLUS_SH5', 'FXVIe_PLUS', 'VBAT_PD3_FXVI',
     '_PIN_CHANNEL_DEFINE_VBAT_PD3_FXVI_ = "S3_5,..."', 'Pin_Channel_define.h:12', 'extern FXVIe_PLUS VBAT_PD3_FXVI;', 'Pin_Channel_define.h:93', 'Component-Statistic.txt:833-834'),
    ('S1_FPVIe_FH0', 'FPVIe', 'FPVI0',
     '_PIN_CHANNEL_DEFINE_FPVI0_ = "S1_0,..."', 'Pin_Channel_define.h:39', 'extern FPVIe FPVI0;', 'Pin_Channel_define.h:120', 'Component-Statistic.txt:378'),
    ('S1_FPVIe_SH0', 'FPVIe', 'FPVI0',
     '_PIN_CHANNEL_DEFINE_FPVI0_ = "S1_0,..."', 'Pin_Channel_define.h:39', 'extern FPVIe FPVI0;', 'Pin_Channel_define.h:120', 'Component-Statistic.txt:380'),
    ('S1_FPVIe_FL0', 'FPVIe', 'FPVI0',
     '_PIN_CHANNEL_DEFINE_FPVI0_ = "S1_0,..."', 'Pin_Channel_define.h:39', 'extern FPVIe FPVI0;', 'Pin_Channel_define.h:120', 'Component-Statistic.txt:378-381'),
    ('S1_FPVIe_SL0', 'FPVIe', 'FPVI0',
     '_PIN_CHANNEL_DEFINE_FPVI0_ = "S1_0,..."', 'Pin_Channel_define.h:39', 'extern FPVIe FPVI0;', 'Pin_Channel_define.h:120', 'Component-Statistic.txt:378-381'),
    ('S1_FPVIe_FL1', 'FPVIe', 'FPVI1',
     '_PIN_CHANNEL_DEFINE_FPVI1_ = "S1_1,..."', 'Pin_Channel_define.h:40', 'extern FPVIe FPVI1;', 'Pin_Channel_define.h:121', 'Component-Statistic.txt:379'),
    ('S1_FPVIe_SL1', 'FPVIe', 'FPVI1',
     '_PIN_CHANNEL_DEFINE_FPVI1_ = "S1_1,..."', 'Pin_Channel_define.h:40', 'extern FPVIe FPVI1;', 'Pin_Channel_define.h:121', 'Component-Statistic.txt:379'),
    ('S8_QVM_CH0+', 'QVMe', 'QVM_S1',
     '_PIN_CHANNEL_DEFINE_QVM_S1_ = "S8_0"', 'Pin_Channel_define.h:41', 'extern QVMe QVM_S1;', 'Pin_Channel_define.h:122', 'Component-Statistic.txt:436'),
    ('S8_QVM_CH0-', 'QVMe', 'QVM_S1',
     '_PIN_CHANNEL_DEFINE_QVM_S1_ = "S8_0"', 'Pin_Channel_define.h:41', 'extern QVMe QVM_S1;', 'Pin_Channel_define.h:122', 'Component-Statistic.txt:437'),
    ('S10_CH0_A', 'QTMUe', 'QTMU_S1',
     '_PIN_CHANNEL_DEFINE_QTMU_S1_ = "S10_0"', 'Pin_Channel_define.h:49', 'extern QTMUe QTMU_S1;', 'Pin_Channel_define.h:130', 'Component-Statistic.txt:376'),
    ('S10_CH0_B', 'QTMUe', 'QTMU_S1',
     '_PIN_CHANNEL_DEFINE_QTMU_S1_ = "S10_0"', 'Pin_Channel_define.h:49', 'extern QTMUe QTMU_S1;', 'Pin_Channel_define.h:130', 'Component-Statistic.txt:377'),
    ('S24_P0', 'DCM', 'S24_P0 (DCM port)',
     'Component-Statistic.txt:69 lists S24_P0 among the DCM (15) ports', 'Component-Statistic.txt:69',
     'no extern object found in Pin_Channel_define.h', 'Pin_Channel_define.h:1-144', 'proof path=[] - see OI-9'),
]

# The eight steps of knowledge/references/L3-method/relay-design-flow.md
STEPS = ['STEP1 FIND-PIN', 'STEP2 FIND-PATH', 'STEP3 SOURCE-SPLIT',
         'STEP4 SHORTEST-PATH', 'STEP5 LOCAL-CONFLICT', 'STEP6 GLOBAL-CONFLICT',
         'STEP7 CLOSURE-GROUPING', 'STEP8 CLOSURE-SET OUTPUT']


def load_proofs():
    return json.loads(PROOFS.read_text(encoding='utf-8'))


def dtest0_scan():
    """Independent re-measurement: DTEST0 token hits in the schematic set."""
    out = []
    for p in (MAP, CS, IR):
        if p.exists():
            txt = io.open(p, encoding='utf-8', errors='replace').read()
            n = txt.count('DTEST')
            out.append('%s hits(DTEST)=%d' % (p.as_posix(), n))
        else:
            out.append('%s MISSING' % p.as_posix())
    return out


def main():
    d = load_proofs()
    pr = d['proofs']
    lines = []
    w = lines.append

    w('TM108 mandatory eight-step relay workflow - evidence output')
    w('owner=test-strategy-architect run=tm108-v2-trial')
    w('flow source: knowledge/references/L3-method/relay-design-flow.md:39-75 (steps 1-8)')
    w('closure-set source: proof required_on + full proof relay chain (NOT pins[].requiredRelays, NOT relays[].state)')
    w('proof file: %s' % PROOFS.as_posix())
    w('proof source: project/DALI/path_proofs.json.txt (engine=%s status=%s)'
      % (d.get('engine', 'n/a'), d.get('status')))
    w('counts: %s' % json.dumps(d['counts']))
    w('')

    # ---- STEP 1
    w('===== %s =====' % STEPS[0])
    w('DFT intent endpoints for TM108:')
    for k in ('VBAT', 'VAC1', 'DTEST0'):
        w('  %-6s %s' % (k, DFT_ENDPOINTS[k]))
    w('board reference endpoints considered:')
    for k in ('AGND', 'KLV1', 'KLV2'):
        w('  %-6s %s' % (k, DFT_ENDPOINTS[k]))
    w("basis: DFT Power='VBAT' / Dynamic='VAC1' / Check='V(DTEST0)' at project/DALI/meta/dali_tm_meta.json:1400-1402")
    w('basis: DFT raw row team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dump.txt:159-161')
    w('basis: DFT conditions project/DALI/meta/test_conditions.yaml:255/259/260/267')
    w('')
    w('proof-backed terminals carrying those endpoints:')
    for t, ep in TERMINAL_ENDPOINT:
        w('  %-10s -> %-40s accepted proofs=%d' % (t, ep, len(pr.get(t, []))))
    w('')

    # ---- STEP 2
    w('===== %s =====' % STEPS[1])
    w('candidate source ports per terminal, with the FULL proof relay chain')
    w('(state=NC means the contact is default-conducting and is NOT in required_on):')
    w('')
    for t, _ep in TERMINAL_ENDPOINT:
        w('-- %s' % t)
        for p in pr.get(t, []):
            sm = p.get('source_meta') or {}
            chain = ' -> '.join('%s#%s(%s)' % (s['relay'], s['relay_number'], s['state'])
                                for s in (p.get('path') or [])) or '<EMPTY path: 0 relay steps>'
            w('   %-22s type=%-10s role=%-2s side=%-3s req=%s' %
              (p['source_port'], sm.get('type', ''), sm.get('role') or '-',
               sm.get('side') or '-', p.get('required_on')))
            w('       net=%s terminal_stop=%s' % (p.get('dut_net'), p.get('terminal_stop')))
            w('       %s' % chain)
        for r in d.get('rejected', {}).get(t, []):
            w('   REJECTED %-22s net=%-26s %s' % (r['source_port'], r['dut_net'], r['reason']))
        w('')

    # ---- STEP 3
    w('===== %s =====' % STEPS[2])
    w('branch rule (relay-design-flow.md:43-48 / path-principles.md:6): differential pin pair or')
    w('heavy current -> scarce source (FPVIe/QVMe); otherwise the non-scarce families (ACM/FXVIe...).')
    w('TM108 condition = voltage threshold toggle, no differential pair, no heavy current:')
    w('  DFT Check is a single-ended digital observation V(DTEST0), not a two-pin differential')
    w('  (project/DALI/meta/dali_tm_meta.json:1402); no iset[] current force appears in TM108')
    w('  (project/DALI/meta/dali_tm_meta.json:1494 currentStimuli=[]).')
    w('=> take the non-scarce branch (K): ACM200 / FXVIe_PLUS. FPVIe/QVMe remain second-choice and')
    w('   the FPVIe capacity is preserved for the differential / high-current items as required by')
    w('   the frozen baseline.')
    w('')

    # ---- STEP 4 (shortest path)
    w('===== %s =====' % STEPS[3])
    w('shortest path is ranked by the UNION SIZE of relays that must be actuated (required_on),')
    w('which is the set the closure set is actuated from (setup-contract relayStatePolicy,')
    w('locator team/artifacts/acceptance-20260916-dali10/setup-contract.json:3899-3902).')
    w('')
    for t, _ep in TERMINAL_ENDPOINT:
        ps = pr.get(t, [])
        ranked = sorted(ps, key=lambda p: (len(p.get('required_on') or []), len(p.get('path') or [])))
        w('-- %s' % t)
        for rank, p in enumerate(ranked, 1):
            req = p.get('required_on') or []
            w('   rank%d union=%d  %-24s req_on=%-16s path_steps=%d' %
              (rank, len(req), p['source_port'], str(req), len(p.get('path') or [])))
        w('')

    # ---- STEP 5 (local conflict)
    w('===== %s =====' % STEPS[4])
    local = [
        ('LC-1 VAC1 f/s pairing', 'VAC1_F and VAC1_S share ONE branch: the FPVIe CH0 Low pair '
         '(K17 -> K18(NC) -> K19(NC)) lands FL0 on VAC1_F and SL0 on VAC1_S '
         '(SCH-Connect-Map.txt:193-194). Closing K17 therefore reaches BOTH sides with one '
         'actuation and no extra union: no conflict.'),
        ('LC-2 VAC1 CH0 High vs CH0 Low branch', 'the CH0 High branch needs K70/K87/K90 '
         '(SCH-Connect-Map.txt:190) while the Low branch needs only K17 (SCH-Connect-Map.txt:193); '
         'they join at VAC_FORCE_S1 (proof from_net/to_net in tm108-paths-proofs.txt). '
         'Selecting the Low branch avoids K70/K87/K90/K82 entirely: the High branch is DROPPED, '
         'it is not merged.'),
        ('LC-3 VBAT vs PD3 share', 'K8_PD3_S1 is the VBAT<->PD3 two-way selector: VBAT needs '
         'K8 default-conducting (SCH-Connect-Map.txt:832-834) while PD3 needs K8(Relay-ON) '
         '(SCH-Connect-Map.txt:814-816). TM108 uses VBAT only, so K8 stays at its un-actuated '
         'state; PD3 is not used by this TM.'),
        ('LC-4 nQON vs HG1 share', 'K64_HG1_S1 pin7 = nQON net, pin2 = '
         'NetK62_BUS_FH_QON_S1_2 (tm108-paths-proofs.txt nQON_F_S1 chains). nQON needs K64 '
         'un-actuated (SCH-Connect-Map.txt:242-244) while HG1 needs K64(Relay-ON) '
         '(SCH-Connect-Map.txt:469-470). TM108 observes nQON, so K64 must stay un-actuated.'),
        ('LC-5 observation both sides', 'the DFT check is ONE single-ended pin. Reading nQON_F and '
         'nQON_S at the same time is not permitted as a measurement, but the F-side chain '
         '(K62) and the S-side chain (K62_BUS_SH_QON) are two different relays on the same node '
         'group; only the side the resolved observation endpoint needs may be actuated. This is '
         'carried as an open item (OI-T4-02) until the DTEST0<->nQON relation is proven.'),
        ('LC-6 time-division candidate', 'VAC1 (ramp) and VBAT (static) are DIFFERENT nets with '
         'disjoint relay chains in the selected allocation, so no time-division is needed: '
         'one closure set covers the whole item.'),
    ]
    for k, v in local:
        w('-- %s' % k)
        w('   %s' % v)
    w('degrade chain used: none (no shortest path was in conflict, so no second-shortest, no')
    w('differential-drop and no 定点补证-on-conflict branch was triggered) - relay-design-flow.md:54-61.')
    w('')

    # ---- STEP 6 (global conflict)
    w('===== %s =====' % STEPS[5])
    glob = [
        ('GC-1 BUS sharing on K17', 'K17_BUSL_VAC_S1 is a [BUS] relay shared by VAC1/VAC2/VAC3, '
         'AMUX and VAC_WL (Component-Statistic.txt:441; SCH-Connect-Map.txt:192/198/204/36). '
         'Closing it excludes those other functions at the same time; TM108 needs exactly one '
         'VAC branch, so K18/K19 stay un-actuated and no other VACn branch can be reached.'),
        ('GC-2 BUS sharing on K62', 'K62_BUS_FH_QON_S1 / K62_BUS_SH_QON_S1 are [BUS] relays shared '
         'with HG1 (Component-Statistic.txt:441/457; SCH-Connect-Map.txt:469-470). K64 selects '
         'between nQON and HG1, so the exclusion is discharged by LC-4.'),
        ('GC-3 QTMU bridge must stay open', 'K141_QTMU_BUSA_S1S2 / K142_QTMU_BUSB_S1S2 bridge the '
         'FPVIe0 and FPVIe1 BUS wires; the frozen baseline requires them OPEN whenever an FPVIe '
         'channel owns a pin (setup-contract.json:8158 safetyInvariants). The selected allocation '
         'uses neither, so the requirement is met and the QTMU alternates for VAC1/VBAT/nQON '
         'remain unacceptable for this item.'),
        ('GC-4 cap gates', 'K21_VAC_Cap must stay OPEN while VAC1 is the scanned input '
         '(SCH-Connect-Map.txt:913; setup-contract.json:3953-3958 globalInitialization order 4) and '
         'K13_VBAT_Cap is required for the VBAT static supply (SCH-Connect-Map.txt:914; '
         'knowledge/standards/relay-checklist.md:27-40). No conflict: they are different pins.'),
        ('GC-5 anti-short / P2P', 'K14_VAC1_P2P (SCH-Connect-Map.txt:877), K38_KLV1_2_short '
         '(SCH-Connect-Map.txt:882), K39/K40 (SCH-Connect-Map.txt:872-873) and K92_AGND_F2S '
         '(Component-Statistic.txt:453) must stay at their un-actuated default '
         '(setup-contract.json:3920-3937 globalInitialization order 2). TM108 closes none of them.'),
        ('GC-6 non-target pins fed back', 'no terminal_stop violation: every accepted proof used '
         'here reports terminal_stop=true and role_match=true (tm108-paths-proofs.txt per-proof '
         'validation blocks). The rejected proofs for these terminals are role mismatches only '
         '(Force port terminating on a Sense terminal), not topology gaps '
         '(schematic-fact-audit.md section 3.3 item 5).'),
        ('GC-7 site-joint relays', 'K13 and K21 are _S1S2 joint relays '
         '(setup-contract.json:8167 safetyInvariants), so re-configuring them disturbs the other '
         'site: recorded as a scheduling constraint, not a resource conflict.'),
        ('GC-8 resource budget', 'the FPVIe family has exactly 2 channels per site and the mOhm items '
         'consume both (setup-contract.json:8165 safetyInvariants). The selected allocation uses ZERO '
         'FPVIe channels, so TM108 does not compete with them for FPVIe.'),
    ]
    for k, v in glob:
        w('-- %s' % k)
        w('   %s' % v)
    w('=> no global conflict remained after local handling; the flow therefore reaches step 7')
    w('   without an M-branch (second-shortest for non-composite relays).')
    w('')

    # ---- STEP 7 (closure grouping)
    w('===== %s =====' % STEPS[6])
    w('groups are split by CONFLICT, not by stage bookkeeping. After step 5/6 the selected')
    w('allocation has no relay whose required state differs between the rising and the falling')
    w('sweep, so the item needs exactly ONE closure set. The stage split that DOES exist is the')
    w('static-supply group versus the scanned-input group, recorded as two groups so the method')
    w('owner can order them:')
    w('')
    w('group G1 (static supply + observation path, valid before and during both sweeps):')
    w('  actuate      : K13_VBAT_Cap (VBAT cap gate), K65_nQON_PU (nQON 5V pull-up)')
    w('  keep-open    : K21_VAC_Cap (VAC1 is the scanned input), K8_PD3 (VBAT side),')
    w('                 K64_HG1 (nQON side), K141/K142 (QTMU bridge), K14/K15/K16 (P2P)')
    w('  evidence     : SCH-Connect-Map.txt:891 (K65), :914 (K13), :913 (K21), :832-834 (K8)')
    w('')
    w('group G2 (VAC1 scanned input, VAC1=0-10V ramp, both directions):')
    w('  actuate      : K18_VAC3/K19_VAC2 are NOT actuated (default-conducting, 0 union)')
    w('  keep-open    : K70_VAC_F, K87_KELVIN0, K90_PC0_Force, K82_R_CS (the CH0 High branch),')
    w('                 K17 as the shared BUS entry point must be in the selected state')
    w('  evidence     : tm108-paths-proofs.txt S5_ACM200_FH0/SH0 chains (req=[]),')
    w('                 SCH-Connect-Map.txt:192-194, SCH-Connect-Map.txt:190')
    w('')
    w('group G3 (optional alternate, only if the ACM200 VAC123_AMUX_ACM channel is occupied):')
    w('  actuate      : K17 (VAC1), K13, K65')
    w('  keep-open    : K18/K19/K21/K70/K87/K90/K82/K141/K142/K86/K130')
    w('  evidence     : tm108-paths-proofs.txt S1_FPVIe_FL0 (req=[17]) + S1_FPVIe_SL0 (req=[17])')
    w('')

    # ---- STEP 8
    w('===== %s =====' % STEPS[7])
    w('final closure-set output belongs to the contract (tm108-resource-config-contract.md/.json,')
    w('relayGroups[]). The actuation call form (cbite.SetOn(...) with -1 terminator and the')
    w('full-set semantics) is implementation-side; this step records only the set and the')
    w('keep-open set, plus the divergence rule that the gate must be re-issued per group')
    w('(relay-design-flow.md:115 - merging two groups into one SetOn parallels them).')
    w('')
    w('DTEST0 independent re-scan (this run):')
    for l in dtest0_scan():
        w('  %s' % l)

    text = '\n'.join(lines) + '\n'
    print(text)
    if '--write' in sys.argv:
        slugs = ['find_pin', 'find_path', 'source_split', 'shortest_path',
                 'local_conflict', 'global_conflict', 'closure_grouping', 'closure_set']
        for i, slug in enumerate(slugs, 1):
            tag = '===== %s =====' % STEPS[i - 1]
            if tag in text:
                body = text.split(tag, 1)[1]
            else:
                body = text
            nxt = STEPS[i] if i < len(STEPS) else None
            if nxt and ('===== %s =====' % nxt) in body:
                body = body.split('===== %s =====' % nxt, 1)[0]
            head = ('TM108 relay workflow %s (step %d/8) - owner=test-strategy-architect '
                    'run=tm108-v2-trial\nflow: knowledge/references/L3-method/relay-design-flow.md:39-75\n'
                    'closure-set source: proof required_on + full proof relay chain\n\n' % (STEPS[i - 1], i))
            (HERE / ('step-%02d-%s.txt' % (i, slug))).write_text(head + body.lstrip('\n'), encoding='utf-8')
        (HERE / 'tm108-relay-workflow.txt').write_text(text, encoding='utf-8')
        print('WROTE 9 files into %s' % HERE.as_posix())


if __name__ == '__main__':
    main()
