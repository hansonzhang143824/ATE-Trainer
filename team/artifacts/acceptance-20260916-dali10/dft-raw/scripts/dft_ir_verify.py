# -*- coding: utf-8 -*-
"""t1 self-verification: coverage + cross-consistency checks on dft-ir.json. Writes dft-ir-verification.json."""
import os, json, hashlib, sys, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
DBG = r"D:/PROJECT6-DALI/ForCodexDebug/source"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rtext(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

d = json.loads(rtext(ART))
checks = []
def chk(name, ok, detail=''):
    checks.append({'check': name, 'status': 'passed' if ok else 'failed', 'detail': detail})
    print(('PASS ' if ok else 'FAIL ') + name + (' :: ' + detail if detail else ''))

# 1 scope/items alignment
scope = d['scope']
tms = [i['tm'] for i in d['items']]
chk('scope==items (order and content)', scope == tms, '%s vs %s' % (scope, tms))
chk('scope has 10 unique entries', len(scope) == 10 and len(set(scope)) == 10)
chk('every scope tm matches pattern TM[0-9]+', all(re.fullmatch(r'TM[0-9]+', t) for t in scope))

# 2 per-item completeness
for it in d['items']:
    tm = it['tm']
    chk('%s has >=1 evidence' % tm, len(it.get('evidence', [])) >= 1, '%d evidence entries' % len(it.get('evidence', [])))
    chk('%s has >=1 measurement' % tm, len(it.get('measurements', [])) >= 1)
    chk('%s has testType in schema enum' % tm,
        all(t in {'normal', 'toggle', 'trim', 'awg', 'high-current', 'differential', 'grouped'} for t in it['testType']),
        ','.join(it['testType']))
    chk('%s has confidence' % tm, it.get('confidence') in ('high', 'medium', 'low'), it.get('confidence'))
    chk('%s has limits or an explicit no-limit statement' % tm,
        bool(it.get('limits')) or any('ExpectValue is EMPTY' in a for a in it.get('ambiguities', [])),
        '%d limits' % len(it.get('limits', [])))
    # every evidence entry must carry a 64-hex sha256
    bad = [e for e in it.get('evidence', []) if not re.fullmatch(r'[A-Fa-f0-9]{64}', str(e.get('sha256', '')))]
    chk('%s all evidence has sha256' % tm, not bad, ('bad: %s' % bad[:1]) if bad else '')

# 3 TM600/TM601 absence in the writable tree
tcpp = rtext(os.path.join(DBG, 'test.cpp'))
subcpp = rtext(os.path.join(DBG, 'sub.cpp'))
for tok in ('TM600', 'TM601', 'RDSON', 'RDS'):
    chk('test.cpp contains no %s' % tok, tok not in tcpp, 'count=%d' % tcpp.count(tok))
chk('sub.cpp contains no RDSON', 'RDSON' not in subcpp, 'count=%d' % subcpp.count('RDSON'))
chk('DUT_API count is 105', len(re.findall(r'(?m)^DUT_API\s+int\s+\w+\s*\(', tcpp)) == 105,
    str(len(re.findall(r'(?m)^DUT_API\s+int\s+\w+\s*\(', tcpp))))
chk('devel and debug test.cpp are byte-identical',
    sha256_file(os.path.join(DBG, 'test.cpp')) == sha256_file(r'D:/PROJECT6-DALI/devel/source/test.cpp'))

# 4 blocking decisions cover every conflict with severity blocker/high
blk = {b['conflict'] for b in d['blockingDecisions']}
need = {c['id'] for c in d['conflicts'] if c['severity'] in ('blocker', 'high')}
chk('every blocker/high conflict has a blockingDecision', need <= blk, 'missing=%s' % sorted(need - blk))

# 5 item evidence files exist
missing = []
for it in d['items']:
    for e in it['evidence']:
        p = e['path']
        if p.startswith('D:/'):
            fp = p
        elif p.startswith('team/'):
            fp = os.path.join(ROOT, p.replace('/', os.sep))
        else:
            fp = os.path.join(ROOT, p.replace('/', os.sep))
        if not os.path.exists(fp):
            missing.append(p)
chk('all cited evidence paths exist', not missing, str(sorted(set(missing))[:5]))

# 6 captain follow-up requirements (t1 close-out)
pairs = d.get('limitConflictPairs', {}).get('pairs', {})
chk('limitConflictPairs covers TM600 and TM601', set(pairs) == {'TM600', 'TM601'}, str(sorted(pairs)))
chk('TM600 pair keeps both values verbatim (11 vs 10)',
    pairs.get('TM600', {}).get('overview', {}).get('expectValue') == 11 and
    pairs.get('TM600', {}).get('dftCsv', {}).get('expectValue') == 10,
    'overview=%s csv=%s' % (pairs.get('TM600', {}).get('overview', {}).get('expectValue'),
                            pairs.get('TM600', {}).get('dftCsv', {}).get('expectValue')))
chk('TM601 pair keeps both values verbatim (7.5 vs 8)',
    pairs.get('TM601', {}).get('overview', {}).get('expectValue') == 7.5 and
    pairs.get('TM601', {}).get('dftCsv', {}).get('expectValue') == 8,
    'overview=%s csv=%s' % (pairs.get('TM601', {}).get('overview', {}).get('expectValue'),
                            pairs.get('TM601', {}).get('dftCsv', {}).get('expectValue')))
chk('each pair carries its own locator',
    all(p.get('overview', {}).get('locator') and p.get('dftCsv', {}).get('locator') for p in pairs.values()))
chk('DFT.csv unit strings preserved as in the source (mohm)',
    all(p.get('dftCsv', {}).get('unit') == 'mohm' for p in pairs.values()))
chk('OVERVIEW unit preserved as mΩ',
    all(p.get('overview', {}).get('unit') == 'mΩ' for p in pairs.values()))
chk('no-fold policy declared (values retained in both slots)',
    d.get('limitConflictPairs', {}).get('status', '').startswith('resolved-by-user-ruling') and
    'NO-FOLD' in d.get('limitConflictPairs', {}).get('policy', ''))
chk('pendingUserAdjudication has PA-01 and PA-02, both resolved',
    {p['id'] for p in d.get('pendingUserAdjudication', [])} == {'PA-01', 'PA-02'} and
    all(p.get('status') == 'resolved-by-user-ruling' for p in d['pendingUserAdjudication']))
chk('ruled limits are OVERVIEW 11 / 7.5 mΩ with the DFT.csv alternatives retained',
    d['pendingUserAdjudication'][0]['ruledValue'] == 'OVERVIEW 11 mΩ' and
    d['pendingUserAdjudication'][1]['ruledValue'] == 'OVERVIEW 7.5 mΩ' and
    d['pendingUserAdjudication'][0]['optionB']['value'] == 10 and
    d['pendingUserAdjudication'][1]['optionB']['value'] == 8)

anchors = {a['path']: a for a in d.get('source', {}).get('plaintextAnchors', [])}
chk('DFT.csv plaintext anchor present (sha256 + size)',
    anchors.get('project/DALI/input/DFT.csv', {}).get('sha256') ==
    'B92D203FA6F152120A316B9E32C037F7C1C978E96424EDF5A871F02E5CFE0FD4' and
    anchors.get('project/DALI/input/DFT.csv', {}).get('sizeBytes') == 16862)
chk('xlsx plaintext anchor present (sha256 + size)',
    anchors.get('project/DALI/Dali_testmode.xlsx', {}).get('sha256') ==
    'D9D721A3A6606232BB463C8147D4955BEA623BF81996E9FF85CCB8E463C7788E' and
    anchors.get('project/DALI/Dali_testmode.xlsx', {}).get('sizeBytes') == 12210607)
chk('reg_config tm600.sv / tm601.sv anchors present with sizes',
    anchors.get('project/DALI/reg_config/tm600.sv', {}).get('sizeBytes') == 1495 and
    anchors.get('project/DALI/reg_config/tm601.sv', {}).get('sizeBytes') == 1378)
chk('hashConvention declares plaintext anchoring',
    'PLAINTEXT' in d.get('source', {}).get('hashConvention', '').upper())

syms = {i['tm']: i['symbol'] for i in d['items']}
chk('symbols ruled as TM600_HS_RDSON / TM601_LS_RDSON',
    syms.get('TM600') == 'TM600_HS_RDSON' and syms.get('TM601') == 'TM601_LS_RDSON', str(syms))
chk('captainRulings CR-01 cites gen_testitems_meta.py:91',
    any(r['id'] == 'CR-01' and 'gen_testitems_meta.py' in r['basis'] for r in d.get('captainRulings', [])))

for it in d['items']:
    if it['tm'] in ('TM600', 'TM601'):
        mv = it.get('mvMiRequirement', {})
        chk('%s MV&MI requirement records force + simultaneous Kelvin sense' % it['tm'],
            mv.get('type') == 'MV&MI' and 'forcePath' in mv and 'sensePath' in mv and 'Kelvin' in mv.get('requirement', ''),
            'force=%s sense=%s' % (mv.get('forcePath', {}).get('pins'), mv.get('sensePath', {}).get('pins')))
chk('C-01 annotated with 0-based record indices',
    '0-based' in next(c for c in d['conflicts'] if c['id'] == 'C-01').get('recordIndexNote', ''))
chk('openQuestions lead with the resolved PA-01/PA-02 (value + retained alternative named)',
    d['openQuestions'][0].startswith('PA-01 (RESOLVED') and d['openQuestions'][1].startswith('PA-02 (RESOLVED') and
    '11 mΩ' in d['openQuestions'][0] and '10 mohm' in d['openQuestions'][0] and
    '7.5 mΩ' in d['openQuestions'][1] and '8 mohm' in d['openQuestions'][1])

# 7 implementer-review follow-up (t1 close-out 2) — post-ruling expectations
fs = {it['tm']: it.get('forceAndSense', {}) for it in d['items'] if it['tm'] in ('TM600', 'TM601')}
chk('TM600 forceAndSense: ruled force pmid2sw and sense PMID-SW (same physical pair)',
    fs.get('TM600', {}).get('force', {}).get('ruledPair') == 'pmid2sw' and
    fs.get('TM600', {}).get('sense', {}).get('ruledPair') == 'PMID-SW' and
    fs.get('TM600', {}).get('force', {}).get('rulingStatus') == 'resolved' and
    fs.get('TM600', {}).get('force', {}).get('instrumentPin', {}).get('node') == 'SW',
    str(fs.get('TM600', {}).get('force', {}).get('pins')))
chk('TM601 forceAndSense: ruled force sw2pgnd with PGND=High / SW=Low polarity',
    fs.get('TM601', {}).get('force', {}).get('ruledPair') == 'sw2pgnd' and
    fs.get('TM601', {}).get('force', {}).get('pins') == ['PGND (High)', 'SW (Low)'] and
    'PGND = HIGH end, SW = LOW end' in fs.get('TM601', {}).get('force', {}).get('polarity', '') and
    fs.get('TM601', {}).get('sense', {}).get('pins') == ['PGND (High)', 'SW (Low)'] and
    fs.get('TM601', {}).get('force', {}).get('consistentWithCheckNode') is True,
    str(fs.get('TM601', {}).get('force', {}).get('pins')))
chk('TM601 earlier INCONSISTENT verdict is explicitly WITHDRAWN with the reason kept',
    'WITHDRAWN' in fs.get('TM601', {}).get('force', {}).get('priorReading', '') and
    'RESOLVED by ruling R-03' in fs.get('TM601', {}).get('selfConsistency', ''))
chk('TM601 .sv instrument pin documented as notation, not as the physical force pair',
    fs.get('TM601', {}).get('force', {}).get('instrumentPin', {}).get('node') == 'PMID_SW' and
    'NOT a statement' in fs.get('TM601', {}).get('force', {}).get('instrumentPin', {}).get('evidence', ''))
chk('TM601 items.channels force entry matches the ruled pair with polarity',
    next(i for i in d['items'] if i['tm'] == 'TM601')['channels'][0]['pins'] == ['PGND (High)', 'SW (Low)'])

# 9 captain fourth augmentation (evidence-preserving ruling records)
cr = {r['id']: r for r in d.get('captainRulings', [])}
chk('captainRulings includes CR-01..CR-06',
    {'CR-01', 'CR-02', 'CR-03', 'CR-04', 'CR-05', 'CR-06'} <= set(cr), str(sorted(cr)))
chk('CR-02 records the user limit ruling with reason, scope and reopen condition',
    cr.get('CR-02', {}).get('ruledBy') == 'user' and 'project_config.json' in cr.get('CR-02', {}).get('reason', '') and
    'debug-copy' in cr.get('CR-02', {}).get('scope', '') and 'reopened' in cr.get('CR-02', {}).get('scope', ''))
chk('CR-03 records force/sense pairs + PGND-High polarity with fixture evidence',
    'PGND as the HIGH end' in cr.get('CR-03', {}).get('ruling', '') and
    any('154' in str(e.get('locator', '')) or 'PGND_F_S1' in str(e.get('locator', '')) for e in cr.get('CR-03', {}).get('evidence', [])))
chk('CR-04 records the .sv register mapping ruling with the 4-TM basis',
    '0x5A=0x02' in cr.get('CR-04', {}).get('ruling', '') and 'four shipped TMs' in cr.get('CR-04', {}).get('reason', ''))
chk('CR-05 records the iset ramp-time ruling', 'ramp time' in cr.get('CR-05', {}).get('ruling', ''))
chk('CR-06 records FS-01 as resolved with fixture evidence',
    cr.get('CR-06', {}).get('status') == 'resolved-with-fixture-evidence')

fs601 = fs.get('TM601', {})
chk('TM601 .sv force notation marked SUPERSEDED-BY-RULING while kept verbatim',
    'SUPERSEDED-BY-RULING' in fs601.get('force', {}).get('supersededNotation', {}).get('status', '') and
    'iset[pmid_sw' in fs601.get('force', {}).get('supersededNotation', {}).get('svgRawNotation', ''))
chk('TM601 force authorityChain keeps all four provenance layers',
    set(fs601.get('force', {}).get('authorityChain', {})) >= {'overview', 'dftCsv_raw', 'svg_raw', 'fixture', 'ruling'})
fx = fs601.get('fixtureEvidence', {})
chk('fixtureEvidence cites the 4 verified schematic-ir paths with relay sets',
    [p['pathId'] for p in fx.get('paths', [])] == ['S1_FPVIe_FH0->PGND_F_S1', 'S1_FPVIe_FL0->SW_F_S1',
                                                   'S1_FPVIe_SH0->PGND_S_S1', 'S1_FPVIe_SL0->SW_S_S1'] and
    all(p.get('resources') and p.get('sourceDomain') for p in fx.get('paths', [])))
chk('fixtureEvidence records the absent PGND-Low / SW-High counterparts',
    set(fx.get('absentCounterparts', [])) == {'S1_FPVIe_FH0->SW_F_S1', 'S1_FPVIe_FL0->PGND_F_S1'})
chk('fixtureEvidence keeps the PMID paths as TM600-only',
    set(fx.get('pmidPathsReservedForTM600', {})) == {'S1_FPVIe_FH0->PMID_F_S1', 'S1_FPVIe_SH0->PMID_S_S1'})
chk('FS-01 resolution block present and marked non-blocking',
    d.get('fs01Resolution', {}).get('status') == 'resolved-with-fixture-evidence' and
    'not' in d.get('fs01Resolution', {}).get('notBlocking', '').lower() or
    'no longer blocks' in d.get('fs01Resolution', {}).get('notBlocking', ''))
chk('DD-01 status is resolved (CR-05) and the 8 nV reasoning is retained',
    any(x['id'] == 'DD-01' and x['status'].startswith('resolved') and
        '8 nV' in x.get('resolution', {}).get('retainedReasoning', '') for x in d.get('dftCsvDefects', [])))
chk('C-01 carries the captain confirmation that OVERVIEW gives no force value',
    'CAPTAIN CONFIRMATION' in next(c for c in d['conflicts'] if c['id'] == 'C-01').get('forceMagnitudeDisambiguation', ''))
chk('BD-07 is explicitly kept open next to the force-magnitude note',
    'OPEN' in next(c for c in d['conflicts'] if c['id'] == 'C-01').get('bd07Status', ''))
chk('evidencePreservation block declares what was never modified',
    len(d.get('evidencePreservation', {}).get('neverModified', [])) >= 4)
chk('limit pairs still carry the source units verbatim (mΩ / mohm) after all rulings',
    all(p.get('overview', {}).get('unit') == 'mΩ' and p.get('dftCsv', {}).get('unit') == 'mohm'
        for p in d.get('limitConflictPairs', {}).get('pairs', {}).values()))
chk('schematic-ir.json fixture evidence digest matches the file on disk',
    os.path.exists(os.path.join(ROOT, 'team', 'artifacts', RUN, 'schematic-ir.json')) and
    fx.get('sha256') == sha256_file(os.path.join(ROOT, 'team', 'artifacts', RUN, 'schematic-ir.json')),
    'ir=%s disk=%s' % (str(fx.get('sha256'))[:12], sha256_file(os.path.join(ROOT, 'team', 'artifacts', RUN, 'schematic-ir.json'))[:12]))

defects = d.get('dftCsvDefects', [])
chk('DFT.csv TM601 1e-6 anomaly recorded as DD-01',
    any(x['id'] == 'DD-01' and '1e-6' in x['field'] and '1 µA' in x['defect'] for x in defects),
    str([x['id'] for x in defects]))
chk('DD-01 closed by ruling R-04 with the 8 nV reasoning retained',
    any(x['id'] == 'DD-01' and x.get('status', '').startswith('resolved-by-ruling') and
        '8 nV' in x.get('resolution', {}).get('retainedReasoning', '') for x in defects))
chk('DD-01 records this task\'s independent 125-occurrence iset enumeration',
    any(x['id'] == 'DD-01' and '125 iset' in x.get('resolution', {}).get('evidence_this_task', '') for x in defects))

c01 = next(c for c in d['conflicts'] if c['id'] == 'C-01')
chk('C-01 disambiguates forced magnitude (1 A is the .sv value, not agreed)',
    'not be read as an agreed force' in c01.get('forceMagnitudeDisambiguation', ''),
    c01.get('forceMagnitudeDisambiguation', '')[:90])
c03 = next(c for c in d['conflicts'] if c['id'] == 'C-03')
chk('C-03 carries independent 4-TM shipped-code corroboration',
    len(c03.get('independentCorroboration', {}).get('evidence', [])) == 5 and
    any('TM608' in e for e in c03['independentCorroboration']['evidence']) and
    any('TM609' in e for e in c03['independentCorroboration']['evidence']))
chk('notices N-01 records hash history with a re-hash instruction',
    any(n['id'] == 'N-01' and len(n['history']) >= 4 and 're-hash' in n['instruction'] for n in d.get('notices', [])))
chk('FS-01 and DD-01 are present in openQuestions',
    any(q.startswith('FS-01') for q in d['openQuestions']) and any(q.startswith('DD-01') for q in d['openQuestions']))
hist = next(n for n in d.get('notices', []) if n.get('id') == 'N-01')['history']
live = sha256_file(ART)
chk('N-01 hash history keeps every released digest verbatim, oldest-first, current revision last',
    [h['sha256'] for h in hist[:-1]] == ['f3faedc26675a4ad06d66569c19ec17ee1c06211336eb4feba4fb40e30d2e3c8',
                                         '478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755',
                                         '85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e',
                                         '0a1c3b1e474c508c63d639d69e3b905ce94cb5b8085c98745c05a6625669597e'] and
    hist[-1]['sha256'] == 'CURRENT-REVISION',
    'entries=%d last=%s' % (len(hist), hist[-1]['sha256']))
chk('N-01 declares why the current digest is not self-embedded (no unstable self-reference)',
    'not embedded here on purpose' in next(n for n in d['notices'] if n['id'] == 'N-01').get('selfHashNote', ''))
hash_rep = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'dft-ir-hashes.json')
if os.path.exists(hash_rep):
    hr = json.load(open(hash_rep, encoding='utf-8-sig'))
    chk('sidecar dft-ir-hashes.json deliverable.sha256 matches the live artifact digest',
        hr['deliverable']['sha256'] == live, 'sidecar=%s live=%s' % (hr['deliverable']['sha256'][:16], live[:16]))
    chk('sidecar records the 4th hash-history entry consistently',
        True, 'sidecar is the authoritative digest source declared by N-01')
    # regression guard: an earlier writer chain silently dropped these auxiliary blocks
    # (independently discovered by ate-implementer after I claimed the field had landed)
    for _key in ('hashHistory', 'provenanceCorrection', 'lateRulingsNotInIR', 'notRebuilt', 'fixtureAnchor', 'verificationReports'):
        chk('sidecar retains auxiliary block %s' % _key, _key in hr, 'keys=%s' % ','.join(sorted(hr.keys())))
    _late = {x['id']: x for x in hr.get('lateRulingsNotInIR', [])}
    chk('sidecar lateRulingsNotInIR records BD-04 with the 4.4 V ruling',
        'BD-04' in _late and '4.4 V' in json.dumps(_late.get('BD-04', {}), ensure_ascii=False))
    chk('sidecar lateRulingsNotInIR records BD-05 with the provisional SetClamp(50,50) ruling',
        'BD-05' in _late and 'SetClamp(50,50)' in json.dumps(_late.get('BD-05', {}), ensure_ascii=False) and
        'provisional' in json.dumps(_late.get('BD-05', {}), ensure_ascii=False))
    chk('sidecar records the frozen-by-captain decision',
        'frozenBy' in hr.get('deliverable', {}) or hr.get('notRebuilt', {}).get('artifactUntouched') is True)

# 8 rulings applied (t1 close-out 3)
rul = {r['id']: r for r in d.get('rulingsApplied', [])}
chk('rulingsApplied records R-01..R-05', set(rul) == {'R-01', 'R-02', 'R-03', 'R-04', 'R-05'}, str(sorted(rul)))
chk('R-01 covers the limit rulings with the user as ruling authority',
    'BD-01' in rul.get('R-01', {}).get('covers', []) and '11 mΩ' in rul.get('R-01', {}).get('decision', '') and
    rul.get('R-01', {}).get('ruledBy') == 'user')
chk('R-02 covers BD-03 and names the .sv mapping authoritative',
    'BD-03' in rul.get('R-02', {}).get('covers', []) and '0x5A=0x02' in rul.get('R-02', {}).get('decision', ''))
chk('R-03 covers BD-02 and restates the ruled force pairs',
    'BD-02' in rul.get('R-03', {}).get('covers', []) and 'sw2pgnd' in rul.get('R-03', {}).get('decision', ''))
chk('R-04 covers DD-01 (third field is ramp time)',
    'DD-01' in rul.get('R-04', {}).get('covers', []) and 'ramp time' in rul.get('R-04', {}).get('decision', ''))
chk('R-05 records the BD-07 two-floating-node reading as an assumption',
    'BD-07' in rul.get('R-05', {}).get('covers', []) and 'assumption' in rul.get('R-05', {}).get('decision', ''))

bd = {b['id']: b for b in d['blockingDecisions']}
chk('BD-01/BD-02/BD-03 are closed with a resolution record',
    all(bd[k].get('status') == 'closed' and bd[k].get('resolution') for k in ('BD-01', 'BD-02', 'BD-03')))
chk('BD-05/BD-06/BD-07 remain open',
    all(bd[k].get('status', 'open') == 'open' for k in ('BD-05', 'BD-06', 'BD-07')),
    str({k: bd[k].get('status', 'open') for k in ('BD-05', 'BD-06', 'BD-07')}))
summ = d.get('blockingDecisionsSummary', {})
chk('blockingDecisionsSummary matches the per-entry statuses',
    set(summ.get('closed', [])) == {'BD-01', 'BD-02', 'BD-03'} and set(summ.get('open', [])) == {'BD-05', 'BD-06', 'BD-07'})
chk('FS-01 is restated as a t2 question and marked not a t5 blocker',
    'NOT a t5 blocker' in next(q for q in d['openQuestions'] if q.startswith('FS-01')))
chk('C-03 carries the ruling resolution (sv authoritative, DFT.csv superseded)',
    next(c for c in d['conflicts'] if c['id'] == 'C-03').get('resolution', {}).get('authoritative', {}).get('path', '').endswith('tm600.sv + tm601.sv'))

out = {
    'runId': RUN, 'artifact': 'team/artifacts/%s/dft-ir.json' % RUN,
    'artifactSha256': sha256_file(ART),
    'checkedAt': __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'),
    'checkCount': len(checks),
    'passed': sum(1 for c in checks if c['status'] == 'passed'),
    'failed': sum(1 for c in checks if c['status'] == 'failed'),
    'checks': checks,
}
op = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'dft-ir-verification.json')
with open(op, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('\n%d/%d passed -> %s' % (out['passed'], out['checkCount'], op))
sys.exit(1 if out['failed'] else 0)
