# -*- coding: utf-8 -*-
"""t1 收尾补丁 5（Captain 第四次增补要求）：BD-01/02/03 + DD-01 + FS-01 的"裁定与消解"记录。

原则：**证据保全式增补** —— 不改写/不删除任何原始记号（DFT.csv / .sv / OVERVIEW 的原始值、单位、locator 全部原样保留），
只在原记录旁新增 ruling/resolution 说明与 Captain 裁定引用。
"""
import os, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
SCH = os.path.join(ROOT, 'team', 'artifacts', RUN, 'schematic-ir.json')

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

def sh(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

d = json.loads(rt(ART))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
SCH_SHA = sh(SCH)
sch = json.loads(rt(SCH))
sch_paths = {p['id']: p for p in sch['paths']}
FIXTURE = [
  ('S1_FPVIe_FH0->PGND_F_S1', 'F (force)', 'HIGH', ['154', '155']),
  ('S1_FPVIe_FL0->SW_F_S1',   'F (force)', 'LOW',  ['60', '61']),
  ('S1_FPVIe_SH0->PGND_S_S1', 'S (sense)', 'HIGH', ['154', '155']),
  ('S1_FPVIe_SL0->SW_S_S1',   'S (sense)', 'LOW',  ['60', '61']),
]
fixture_evidence = []
for pid, role, dom, relays in FIXTURE:
    x = sch_paths.get(pid, {})
    fixture_evidence.append({
      'pathId': pid, 'role': role, 'sourceDomain': dom, 'components': x.get('from'),
      'dutPin': x.get('to'), 'resources': x.get('resources', relays),
      'confidence': x.get('confidence'), 'verifiedBy': 'dft-expert (looked up directly in schematic-ir.json paths[])',
    })
absent_counterparts = [pid for pid in ('S1_FPVIe_FH0->SW_F_S1', 'S1_FPVIe_FL0->PGND_F_S1') if pid not in sch_paths]
pmid_counterpart = {pid: {'from': sch_paths[pid]['from'], 'to': sch_paths[pid]['to'], 'resources': sch_paths[pid]['resources']}
                    for pid in ('S1_FPVIe_FH0->PMID_F_S1', 'S1_FPVIe_SH0->PMID_S_S1') if pid in sch_paths}

# ================================================================ 1) Captain 裁定增补（BD-01/02/03 + DD-01 + FS-01）
d.setdefault('captainRulings', [])
def upsert_ruling(entry):
    for i, r in enumerate(d['captainRulings']):
        if r['id'] == entry['id']:
            d['captainRulings'][i] = entry
            return
    d['captainRulings'].append(entry)

upsert_ruling({
  'id': 'CR-02', 'covers': ['BD-01', 'PA-01', 'PA-02', 'C-01 (limit half)'], 'ruledBy': 'user',
  'topic': 'TM600/TM601 RDSON limits for this acceptance run',
  'ruling': ('this acceptance run uses the OVERVIEW limits: TM600 HS_RDSON = 11 mΩ, TM601 LS_RDSON = 7.5 mΩ '
             '(project/DALI/Dali_testmode.xlsx, sheet=OVERVIEW!rows 132-133). The DFT.csv values (TM600 10 mohm, '
             'TM601 8 mohm) are retained as a REGISTERED CONFLICT — rewriting, averaging or deleting them is forbidden.'),
  'reason': 'project_config.json declares inputs.dft = project/DALI/Dali_testmode.xlsx, i.e. OVERVIEW is the DFT authority input',
  'scope': 'applies ONLY to this debug-copy acceptance run (D:/PROJECT6-DALI/ForCodexDebug); if a newer DFT version is discovered, this ruling must be reopened',
  'status': 'applied', 'ruledAt': now,
  'evidence': [{'path': 'project/DALI/Dali_testmode.xlsx', 'locator': 'sheet=OVERVIEW!row 132 (TM600 ExpectValue=11, Unit=mΩ) / row 133 (TM601 ExpectValue=7.5, Unit=mΩ)'},
               {'path': 'project_config.json', 'locator': 'inputs.dft'},
               {'path': 'project/DALI/input/DFT.csv', 'locator': 'record index 18 (0-based) = csvRecord 19 ExpectValue=10+mohm; record index 19 = csvRecord 20 ExpectValue=8+mohm (retained, not adopted)'}],
})

upsert_ruling({
  'id': 'CR-03', 'covers': ['BD-02', 'C-01 (pin half)', 'FS-01'], 'ruledBy': 'captain',
  'topic': 'TM600/TM601 force and Kelvin-sense pairs',
  'ruling': ('TM600 force/sense = PMID↔SW. TM601 force/sense = SW↔PGND with **PGND as the HIGH end and SW as the LOW end**. '
             'The .sv notations isrcPMID_SW / iset[pmid_sw] are NOT adopted for TM601.'),
  'reason': 'confirmed by fixture evidence in the schematic IR (t2): the FPVIe force channel reaches PGND_F_S1 through relays 154/155 (role F, HIGH domain) '
            'and SW_F_S1 through relays 60/61 (role F, LOW domain); the sense channel mirrors it (PGND_S_S1 154/155 HIGH, SW_S_S1 60/61 LOW). '
            'PMID↔SW is TM600\'s pairing (S1_FPVIe_FH0->PMID_F_S1, relay 83).',
  'status': 'applied', 'ruledAt': now,
  'evidence': [{'path': 'team/artifacts/%s/schematic-ir.json' % RUN, 'sha256': SCH_SHA,
                'locator': 'paths[] ids S1_FPVIe_FH0->PGND_F_S1, S1_FPVIe_FL0->SW_F_S1, S1_FPVIe_SH0->PGND_S_S1, S1_FPVIe_SL0->SW_S_S1'}],
})

upsert_ruling({
  'id': 'CR-04', 'covers': ['BD-03', 'C-03'], 'ruledBy': 'captain',
  'topic': 'TM600/TM601 register map',
  'ruling': ('per-TM reg_config .sv mapping is adopted: TM600 0x59=0x20, 0x5A=0x02, 0x61=0x4B; TM601 0x59=0x20, 0x5A=0x01, 0x61=0x4B '
             '(both also write 0x10=0x43).'),
  'reason': 'the 0x5A bit pattern across four shipped TMs (TM607 0x5A=0x01 for the low-side FET, TM608/TM609/TM640 0x5A=0x02 for the high-side FET) '
            'plus the LS/HS bit-inversion fix recorded in docs/PROGRESS.md',
  'status': 'applied', 'ruledAt': now,
  'evidence': [{'path': 'project/DALI/reg_config/tm600.sv', 'locator': '0x59=0x20 / 0x5A=0x02 / 0x61=0x4B'},
               {'path': 'project/DALI/reg_config/tm601.sv', 'locator': '0x59=0x20 / 0x5A=0x01 / 0x61=0x4B'},
               {'path': 'docs/PROGRESS.md', 'locator': 'LS/HS register bit inversion fix history'},
               {'path': 'project/DALI/input/DFT.csv', 'locator': 'records 18/19 register rows — retained verbatim as the superseded alternative'}],
})

upsert_ruling({
  'id': 'CR-05', 'covers': ['DD-01'], 'ruledBy': 'captain',
  'topic': 'DFT.csv TM601 iset[sw2pgnd,1,1e-6,0] — unit/field semantics',
  'ruling': 'the third iset[] field is the ramp time, so TM601 = 1 A with a 1 µs ramp (NOT 1 µA).',
  'reason': 'reg_config/tm600.sv:38-42 is self-labelling in three mutually consistent lines; across the file the 2nd field takes only current-shaped '
            'values and the 3rd field only time-shaped values',
  'status': 'applied (DD-01 resolved)', 'ruledAt': now,
  'evidence': [{'path': 'project/DALI/reg_config/tm600.sv', 'locator': 'lines 38-42 (`NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3);` // "pin SW current set to 1A" // iset[sw,1,1e-3,0])'},
               {'path': 'project/DALI/reg_config/*.sv', 'locator': 'this task independently enumerated 125 iset[...] occurrences: all 4-field; 3rd slot values are time-shaped only (1e-3, 1e-6, 100e-6, 2e-3, 10e-3, 1e-5)'}],
})

upsert_ruling({
  'id': 'CR-06', 'covers': ['FS-01'], 'ruledBy': 'captain',
  'topic': 'TM601 physical loop — FS-01 resolution',
  'ruling': 'the TM601 loop is SW↔PGND with PGND on the HIGH end; tm601.sv\'s isrcPMID_SW is NOT the wiring of that loop (PMID↔SW belongs to TM600).',
  'reason': 'Captain validated FS-01 directly against the schematic IR paths[] (see CR-03 evidence); this task re-verified the same four path ids and their relay sets',
  'status': 'resolved-with-fixture-evidence', 'ruledAt': now,
  'evidence': [{'path': 'team/artifacts/%s/schematic-ir.json' % RUN, 'sha256': SCH_SHA, 'locator': 'paths[] (182 paths)'}],
})

upsert_ruling({
  'id': 'CR-01', 'covers': ['symbol naming'], 'ruledBy': 'captain',
  'topic': 'TM600/TM601 symbol names',
  'ruling': {'TM600': 'TM600_HS_RDSON', 'TM601': 'TM601_LS_RDSON'},
  'reason': 'naming hard rule in scripts/gen_testitems_meta.py:91 — DUT_API int TM<item>_<SHORTNAME>(short funcindex',
  'status': 'applied',
  'basis': 'naming hard rule in scripts/gen_testitems_meta.py line 91: '
           "DUT_API int ((?:TM\\d+(?:_\\d+)?_\\w+|Trim_\\w+))\\(short funcindex — i.e. TM<item>_<SHORTNAME>; "
           'TM600 ShortName=HS_RDSON and TM601 ShortName=LS_RDSON, so the symbols are TM600_HS_RDSON / TM601_LS_RDSON',
  'supersedes': 'acceptance-plan.json symbolHint RDSON_TEST_HS / RDSON_TEST_LS (placeholders)',
  'appliedAt': now,
})

# ================================================================ 1b) N-01 哈希历史追加本版
notices = d.setdefault('notices', [])
n01 = next((n for n in notices if n.get('id') == 'N-01'), None)
if n01 is not None:
    n01['history'] = [h for h in n01['history'] if h['sha256'] != 'CURRENT-REVISION']
    n01['history'].append({'sha256': 'CURRENT-REVISION', 'sizeBytes': None,
                           'note': 'captain fourth augmentation (CR-02..CR-06 ruling records, TM601 polarity + fixture evidence, FS-01 resolved)'})
    n01['history'][-1]['sha256'] = 'CURRENT-REVISION'
    n01['history'][-1]['sizeBytes'] = None

# ================================================================ 2) items.TM601 force 字段：标注"已被裁定取代"，保留 .sv 原始记号
for it in d['items']:
    if it['tm'] != 'TM601':
        continue
    f = it['forceAndSense']['force']
    f['supersededNotation'] = {
      'svgRawNotation': 'reg_config/tm601.sv iset[pmid_sw,1,1e-3,0] (instrument-side pin name isrcPMID_SW)',
      'status': 'SUPERSEDED-BY-RULING — do not wire TM601 from the .sv notation',
      'replacedBy': 'sw2pgnd (force) / SW-PGND (sense), with PGND = HIGH end and SW = LOW end (captain ruling CR-03)',
      'preservedForAudit': 'the original .sv token is kept verbatim in this field and in instrumentPin; it is evidence of what the .sv file says, not of the wiring',
      'reason': 'the fixture routes the FPVIe force channel to PGND (relays 154/155, HIGH) and SW (relays 60/61, LOW); no FPVIe path to PGND-as-LOW or SW-as-HIGH exists',
    }
    f['polarity'] = 'PGND = HIGH end, SW = LOW end (captain ruling CR-03; the earlier "PMID = High, SW = Low" wording was TM600-only and is explicitly NOT valid for TM601)'
    f['pins'] = ['PGND (High)', 'SW (Low)']
    f['correctionNotice'] = ('the previous revision of this artifact stated force pins [SW, PGND] without the polarity assignment; CR-03 fixes the polarity as '
                             'PGND=High / SW=Low. The DFT.csv token iset[sw2pgnd] is preserved unchanged in authorityChain.')
    f['authorityChain'] = {
      'overview': 'rows 132/133 state the check nodes (TM600 PMID-SW, TM601 SW-PGND) but no force value',
      'dftCsv_raw': 'DFT.csv record index 19: iset[sw2pgnd,1,1e-6,0] (kept verbatim; 3rd field = ramp time per CR-05)',
      'svg_raw': 'reg_config/tm601.sv: iset[pmid_sw,1,1e-3,0] (kept verbatim; superseded for wiring per CR-03)',
      'fixture': 'schematic-ir.json paths[]: F S1_FPVIe_FH0->PGND_F_S1 [154,155] HIGH; F S1_FPVIe_FL0->SW_F_S1 [60,61] LOW',
      'ruling': 'CR-03 (captain, fixture-confirmed)',
    }
    it['forceAndSense']['sense'].update({
      'pins': ['PGND (High)', 'SW (Low)'],
      'ruledPair': 'SW-PGND', 'ruledBy': 'captain CR-03', 'rulingStatus': 'resolved-with-fixture-evidence',
      'polarityNote': 'sense channel mirrors the force channel: S1_FPVIe_SH0->PGND_S_S1 [154,155] HIGH, S1_FPVIe_SL0->SW_S_S1 [60,61] LOW',
    })
    it['forceAndSense']['fixtureEvidence'] = {
      'source': 'team/artifacts/%s/schematic-ir.json' % RUN, 'sha256': SCH_SHA, 'generatedBy': sch.get('generatedBy'),
      'paths': fixture_evidence,
      'absentCounterparts': absent_counterparts,
      'absentMeaning': 'no FPVIe path exists with PGND as the LOW end or SW as the HIGH end — the polarity is not symmetric in the fixture',
      'pmidPathsReservedForTM600': pmid_counterpart,
      'verification': 'dft-expert looked up each cited path id in schematic-ir.json and confirmed from/to, sourceRole, sourceDomain, resources and confidence',
    }
    it['forceAndSense']['polarityConclusion'] = 'TM601 force = PGND(High)↔SW(Low); TM601 sense = PGND(High)↔SW(Low); PMID↔SW is TM600\'s pair (F S1_FPVIe_FH0->PMID_F_S1, relay 83)'
    it['channels'][0] = {'role': 'floating force (high current, low-side loop)', 'pins': ['PGND (High)', 'SW (Low)'],
                         'sense': 'force the 1 A loop through PGND(High) -> floating source -> SW(Low) -> LS FET', 'ruledPair': 'sw2pgnd'}
    it['channels'][1] = {'role': 'differential Kelvin sense', 'pins': ['PGND (High)', 'SW (Low)'],
                         'sense': 'MV of the same physical pair (fixture sense channel at relays 154/155 HIGH and 60/61 LOW)'}
    it['mvMiRequirement']['forcePath'] = it['channels'][0]
    it['mvMiRequirement']['sensePath'] = it['channels'][1]
    it['mvMiRequirement']['notes'] = [
      'CR-03 ruled the pairs AND the polarity: PGND = High, SW = Low for both force and sense.',
      'The earlier "PMID = High / SW = Low" phrasing was TM600-only and does not hold for TM601 (it is preserved in force.priorReading).',
      'Kelvin separation: the fixture provides distinct F and S channels on both ends (154/155 vs 60/61), so favour four-wire measurement; t3 must still confirm the relay aliases.',
    ]

# TM600 极性确认（保持原样，仅补裁定引用）
for it in d['items']:
    if it['tm'] == 'TM600':
        it['forceAndSense']['force']['polarityConfirmed'] = 'PMID = High, SW = Low (CR-03 confirms PMID↔SW for TM600); fixture path S1_FPVIe_FH0->PMID_F_S1 uses relay 83'
        it['forceAndSense']['force']['rulingRef'] = 'CR-03'

# ================================================================ 3) forceMagnitudeDisambiguation + Captain 确认
for c in d['conflicts']:
    if c['id'] == 'C-01':
        c['forceMagnitudeDisambiguation'] += (
          ' | CAPTAIN CONFIRMATION (CR-03/CR-05): OVERVIEW rows 132/133 give NO force value; the 1 A figure comes from '
          'reg_config/tm600.sv + reg_config/tm601.sv and from DFT.csv record 18, and the iset field semantics were ruled by the captain '
          '(record 19 is likewise 1 A with a 1 µs ramp). "1 A" must therefore never be cited as an OVERVIEW number.')
        c['bd07Status'] = 'BD-07 (TM600 OVERVIEW Special="Y / 2 FLOAT") remains OPEN — the two-floating-node reading is an implementation assumption, not a source fact'

# ================================================================ 4) FS-01 消解
d['openQuestions'] = [q for q in d['openQuestions'] if not q.startswith('FS-01')]
d['openQuestions'].insert(2, 'FS-01 (RESOLVED with fixture evidence — no longer a t2 question and NOT a t5 blocker; captain CR-06 + this task\'s re-verification): '
                             'the TM601 physical loop is SW↔PGND with PGND on the HIGH end — schematic-ir.json has FPVIe force/sense paths to PGND (relays 154/155, HIGH '
                             'domain) and SW (relays 60/61, LOW domain), while PMID↔SW is TM600\'s pair (relay 83). tm601.sv\'s isrcPMID_SW is NOT the wiring of this loop '
                             'and is retained only as raw .sv evidence. Consequence recorded in items.TM601: the dft-ir wording "PMID(High)/SW(Low)" does NOT hold for '
                             'TM601. Residual: t3 must still map the pgnd2sw/sw2pgnd bus aliases to concrete relay groups.')
d['fs01Resolution'] = {
  'status': 'resolved-with-fixture-evidence', 'ruledBy': 'captain (CR-06)',
  'fixtureProof': {'file': 'team/artifacts/%s/schematic-ir.json' % RUN, 'sha256': SCH_SHA,
                   'paths': [f['pathId'] for f in fixture_evidence]},
  'conclusion': 'TM601 force/sense = SW↔PGND (PGND High, SW Low); PMID↔SW belongs to TM600',
  'notBlocking': 'no longer blocks t5; the only residual is the t3 alias→relay mapping',
}

# ================================================================ 5) DD-01 → resolved（保留 8 nV 论证）
for x in d.get('dftCsvDefects', []):
    if x['id'] == 'DD-01':
        x['status'] = ('resolved-by-ruling (R-04 / CR-05): the third iset[] field is the ramp time; '
                       'TM601 = 1 A + 1 µs ramp (the earlier "open — needs DFT-owner confirmation" state is superseded)')
        x.setdefault('resolution', {})['statusTransition'] = 'was: "open — needs DFT-owner confirmation" → now: resolved by R-04/CR-05'

# ================================================================ 6) blockingDecisions 与摘要保持与裁定一致
for b in d['blockingDecisions']:
    b.setdefault('rulingRef', None)
    if b['id'] in ('BD-01', 'BD-02', 'BD-03'):
        b['status'] = 'closed'
        b['resolution'] = b.get('resolution', {})
        b['resolution']['rulingRef'] = {'BD-01': 'CR-02', 'BD-02': 'CR-03', 'BD-03': 'CR-04'}[b['id']]
    else:
        b['status'] = 'open'
d['blockingDecisionsSummary']['closed'] = ['BD-01', 'BD-02', 'BD-03']
d['blockingDecisionsSummary']['open'] = ['BD-05', 'BD-06', 'BD-07']
d['blockingDecisionsSummary']['openNotes']['BD-07'] = ('TM600 OVERVIEW Special="Y / 2 FLOAT" — the two-floating-node reading is an implementation '
                                                       'assumption (R-05/implementer), NOT a source fact; stays OPEN')

# ================================================================ 7) 证据保全声明 + revisions
d['evidencePreservation'] = {
  'policy': 'EVIDENCE-PRESERVING AUGMENTATION: this revision only ADDS ruling/resolution records beside the original evidence.',
  'neverModified': [
    'limitConflictPairs[TM600/TM601].{overview,dftCsv} values, units (mΩ / mohm), locators — byte-identical to the sources',
    'all DFT.csv tokens quoted in this artifact (iset[sw2pgnd,1,1e-6,0], iset[pmid2sw,1,1e-3,0], register rows)',
    'all reg_config/*.sv tokens quoted in this artifact, including the superseded iset[pmid_sw,...]',
    'all OVERVIEW cell-level locators',
    'conflicts[].sources — each conflict keeps every source it ever cited',
  ],
  'supersededButPreserved': ['items.TM601.forceAndSense.force svgRawNotation', 'items.TM601.forceAndSense.force priorReading',
                             'conflicts[C-01/C-03/C-05] alternative values'],
}
d['revisions'].append({
  'at': now, 'by': 'dft-expert (t1 close-out 4, captain fourth augmentation request)',
  'changes': [
    'captainRulings += CR-02 (BD-01 user limit ruling, with the debug-copy-only scope and the reopen condition), CR-03 (BD-02 force/sense + polarity, fixture-confirmed), CR-04 (BD-03 register map), CR-05 (DD-01 iset field semantics), CR-06 (FS-01 resolution)',
    'items.TM601.forceAndSense.force: marked SUPERSEDED-BY-RULING for the .sv notation (raw token preserved), polarity fixed to PGND=High / SW=Low, authorityChain and fixtureEvidence added',
    'items.TM601.forceAndSense.fixtureEvidence: four schematic-ir paths re-verified by this task (from/to, role, domain, relays, confidence), plus the absent PGND-as-Low / SW-as-High counterparts and the PMID paths reserved for TM600',
    'FS-01 → resolved-with-fixture-evidence (fs01Resolution block added); openQuestion restated as resolved with the t3 alias residual only',
    'DD-01 status → resolved (CR-05); the 8 nV reasoning kept as the retainedReasoning',
    'C-01.forceMagnitudeDisambiguation += captain confirmation that OVERVIEW gives no force value; BD-07 explicitly kept open',
    'evidencePreservation block added (declares what was never modified)',
  ],
})
d['verification']['captainRulings'] = [r['id'] for r in d['captainRulings']]
d['verification']['fs01'] = 'resolved-with-fixture-evidence'

with open(ART, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
b = open(ART, 'rb').read()
print('patched', ART, len(b), 'bytes')
print('new sha256', hashlib.sha256(b).hexdigest())
print('captainRulings:', [r['id'] for r in d['captainRulings']])
print('TM601 force pins:', d['items'][8]['forceAndSense']['force']['pins'])
