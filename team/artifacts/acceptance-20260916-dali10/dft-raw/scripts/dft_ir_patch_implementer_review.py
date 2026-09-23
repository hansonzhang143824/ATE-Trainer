# -*- coding: utf-8 -*-
"""t1 收尾补丁 2：按 ate-implementer 的独立复核意见修订 dft-ir.json。

背景：ate-implementer 独立枚举了 live test.cpp 中所有 0x5A 写入并确认 C-03 方向；同时指出
本 IR 的 items.TM601.channels 存在 force/sense 自相矛盾（必须显式登记），以及 DFT.csv 的
iset[sw2pgnd,1,1e-6,0] 单位/时长可疑、C-01 文字可能被误读为双方都是 1 A。
"""
import os, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')

def sh(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

d = json.loads(rt(ART))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# ================================================================ A) force/sense 显式分离（修正 TM601 自相矛盾）
FORCE_SENSE = {
 'TM600': {
   'force': {'pins': ['PMID', 'SW'], 'polarity': 'PMID = High, SW = Low',
             'source': 'reg_config/tm600.sv iset[sw,1,1e-3,0] (HS FET forced on: current enters PMID, exits SW, returns through the floating source)',
             'csvAlternative': 'DFT.csv record index 18: iset[pmid2sw,1,1e-3,0] — same pair, the rail is named by its two ends',
             'consistentWithCheckNode': True,
             'checkNode': 'PMID-SW (DFT.csv Check, OVERVIEW Notes Rds,on=(PMID-SW)/ISW)'},
   'sense': {'pins': ['PMID', 'SW'], 'polarity': 'differential',
             'source': 'DFT.csv Check=PMID-SW (MV&MI: differential voltage read while the force current flows)',
             'decomposition': 'RON_HS = V(PMID-SW) / I(PMID→SW) x 1e3 mΩ'},
   'selfConsistency': 'CONSISTENT: the forced loop PMID→SW is exactly the pair whose drop is sensed, so the sensed drop is the HS FET drop.',
 },
 'TM601': {
   'force': {'pins': ['PMID', 'SW'], 'polarity': 'PMID = High, SW = (Low)',
             'source': 'reg_config/tm601.sv iset[pmid_sw,1,1e-3,0]',
             'csvAlternative': 'DFT.csv record index 19: iset[sw2pgnd,1,1e-6,0] — a DIFFERENT pair (SW→PGND)',
             'consistentWithCheckNode': False,
             'checkNode': 'PGND-SW (DFT.csv Check) / SW-PGND (OVERVIEW Notes Rds,on=(SW-PGND)/IPMID2SW)'},
   'sense': {'pins': ['SW', 'PGND'], 'polarity': 'differential',
             'source': 'DFT.csv Check=PGND-SW and OVERVIEW Notes Rds,on=(SW-PGND)/IPMID2SW (MV&MI)',
             'decomposition': 'RON_LS = V(SW-PGND) / I(SW→PGND) x 1e3 mΩ'},
   'selfConsistency': 'INCONSISTENT — this is the deliberate finding: reg_config/tm601.sv forces current into the PMID↔SW pair, '
                      'which cannot drive 1 A through the low-side FET (SW↔PGND), so the SW-PGND sense would not measure an LS '
                      'RDSON drop. The DFT.csv row (iset[sw2pgnd] with Check=PGND-SW) is the electrically self-consistent pairing. '
                      'Both are recorded verbatim; t2 (schematic) must confirm which physical pair is wired for the LS force before '
                      't3/t4 fix the plan. DO NOT silently adopt the .sv pair for TM601.',
 },
}
for it in d['items']:
    if it['tm'] == 'TM600':
        it['forceAndSense'] = FORCE_SENSE['TM600']
    if it['tm'] == 'TM601':
        it['forceAndSense'] = FORCE_SENSE['TM601']

# ================================================================ B) DFT.csv TM601 定时/单位可疑
d['dftCsvDefects'] = [{
  'id': 'DD-01',
  'path': 'project/DALI/input/DFT.csv', 'recordIndex0Based': 19, 'csvRecord': 20, 'item': 'TM601',
  'field': 'Dynamic = iset[sw2pgnd,1,1e-6,0]',
  'defect': 'the third argument of iset[] is the ramp/settle time in seconds in every other row of this file '
            '(e.g. iset[pmid2sw,1,1e-3,0], iset[sw,-2,1e-3,0], iset[sw,2,1e-3,0]). Read literally as a current, 1e-6 A '
            'would be 1 µA, giving 8 mΩ x 1 µA = 8 nV across the LS FET — far below any ATE measurement resolution and '
            'electrically useless for the test.',
  'interpretation': 'most likely a 1 µs ramp time (typo/unit slip), i.e. the force magnitude is 1 A as elsewhere; '
                    'alternatively the whole row is a copy defect. Both readings are recorded; neither is adopted silently.',
  'impact': 'if 1e-6 were a force current the TM601 test could not produce a measurable result; the forced magnitude '
            'must be confirmed (see BD-02/BD-05) before implementation.',
  'status': 'open — needs DFT-owner confirmation',
}]

# ================================================================ C) C-01 force 幅度表述消歧 + 独立复核证据
for c in d['conflicts']:
    if c['id'] == 'C-01':
        c['forceMagnitudeDisambiguation'] = (
          'The two sources do NOT agree on the forced magnitude either: OVERVIEW (rows 132/133) states no force at all; '
          'reg_config/tm600.sv and tm601.sv force 1 A (iset[sw,1,1e-3] / iset[pmid_sw,1,1e-3]); DFT.csv record 18 forces 1 A '
          '(iset[pmid2sw,1,1e-3]) but DFT.csv record 19 literally writes 1e-6 (see dftCsvDefects DD-01) and its TM600 static '
          'operating point implies 4 A. "1 A" is therefore the .sv value for BOTH parts and must not be read as an agreed force.')
        c['scopeStatement'] = ('This conflict covers: (a) the limit value (OVERVIEW 11/7.5 mΩ vs DFT.csv 10/8 mohm); '
                               '(b) the force and Kelvin-sense pin pairs; (c) the forced magnitude; (d) the compliance limit '
                               '(never stated by any source).')
    if c['id'] == 'C-03':
        c['independentCorroboration'] = {
          'by': 'ate-implementer (independent enumeration of live test.cpp)',
          'finding': '0x5A is the FET-select register and the shipped generation is LS=0x01 / HS=0x02',
          'evidence': [
            'TM607_BUCK_LS_ZCD  test.cpp:7018  0x5A=0x01  // D2A_BUBO_TM_LSON=1',
            'TM608_BOOST_HS_ZCD test.cpp:7109  0x5A=0x02  // D2A_BUBO_TM_HSON=1',
            'TM609_BOOST_HS_NEG test.cpp:7202  0x5A=0x02  // D2A_BUBO_TM_HSON=1',
            'TM640_BOOST_HS_OCP test.cpp:7534  0x5A=0x02  // + LOW_ILIMT_OFF=1',
            'TM640_BOOST_HS_OCP test.cpp:7541  0x5A=0x06  // + BOOST_OCP_EN=1',
          ],
          'strength': 'four shipped TMs (not just TM640/TM607 as this IR originally cited); HS=0x02 also holds in TM608 and TM609',
          'effect': 'C-03/BD-03 now rests on shipped-code evidence in addition to reg_config/tm600.sv+tm601.sv; the DFT.csv 0x58/0x59/0x61 rows are the older map',
        }

# ================================================================ D) hash 再公告（下游必须重新取哈希）
if 'notices' not in d: d['notices'] = []
d['notices'] = [n for n in d['notices'] if n.get('id') != 'N-01']
d['notices'].append({
  'id': 'N-01', 'topic': 'artifact hash changed after the first handoff — re-hash, do not trust quoted digests',
  'history': [
    {'sha256': 'f3faedc26675a4ad06d66569c19ec17ee1c06211336eb4feba4fb40e30d2e3c8', 'sizeBytes': 88109, 'note': 'first build (t1 handoff)'},
    {'sha256': '478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755', 'sizeBytes': 88101, 'note': 'TM1205 md hash corrected'},
    {'sha256': '85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e', 'sizeBytes': 99058, 'note': 'captain follow-up (PA-01/PA-02, plaintext anchors, CR-01 symbols, MV&MI)'},
    {'sha256': 'CURRENT-REVISION', 'sizeBytes': None, 'note': 'this revision: force/sense split (FS-01), DD-01, C-03 corroboration, notices N-01'},
  ],
  'instruction': 'always re-hash the file before citing it; team/artifacts/%s/dft-raw/dft-ir-hashes.json holds the authoritative digest' % RUN,
  'selfHashNote': ('the digest of THIS revision is not embedded here on purpose: embedding it would change the bytes it '
                   'describes (unstable self-reference). The authoritative digest is '
                   'team/artifacts/%s/dft-raw/dft-ir-hashes.json -> deliverable.sha256; the dft_ir_verify.py check compares '
                   'that sidecar against the live file.' % RUN),
})

# ================================================================ E) openQuestions 增补
d['openQuestions'] = [q for q in d['openQuestions'] if not q.startswith(('DD-01', 'FS-'))]
d['openQuestions'].insert(2, 'FS-01 (deliberate finding): reg_config/tm601.sv forces PMID↔SW while the LS RDSON check node is SW-PGND — the .sv force path is inconsistent with its own check node; the DFT.csv pairing (iset[sw2pgnd] + Check=PGND-SW) is the self-consistent one. t2 must confirm the physical LS force pair.')
d['openQuestions'].insert(3, 'DD-01 (source defect): DFT.csv TM601 writes iset[sw2pgnd,1,1e-6,0]; read literally that is 1 µA (8 nV across 8 mΩ), while every other row uses the third slot as a ramp time — likely a 1 µs/1 ms typo. Needs DFT-owner confirmation.')

# ================================================================ F) revisions + verification
d['revisions'].append({
  'at': now, 'by': 'dft-expert (t1 close-out 2, responding to ate-implementer independent review)',
  'changes': [
    'added items[TM600/TM601].forceAndSense (force pair vs Kelvin sense pair stated separately) and flagged the TM601 .sv force path as INCONSISTENT with its own SW-PGND check node (FS-01) — this corrects a real self-contradiction in the previous revision where channels[0]=PMID-SW and channels[1]=SW-PGND were both implied to be the measurement',
    'added dftCsvDefects DD-01 (DFT.csv TM601 iset[sw2pgnd,1,1e-6,0] unit/ramp anomaly)',
    'annotated C-01 with forceMagnitudeDisambiguation (the sources disagree on the forced magnitude too; 1 A is the .sv value for both parts, the CSV TM601 literal is 1e-6) and scopeStatement',
    'annotated C-03 with independentCorroboration from ate-implementer (four shipped TMs: TM607 0x5A=0x01 LS, TM608/TM609/TM640 0x5A=0x02 HS)',
    'added notices N-01 (artifact hash history; downstream must re-hash)',
  ],
})
d['verification']['forceSenseSplit'] = {'TM600': 'consistent (PMID-SW force, PMID-SW sense)',
                                        'TM601': 'INCONSISTENT across sources (PMID-SW force vs SW-PGND sense) — FS-01',
                                        'dftCsvDefectCount': 1}

with open(ART, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print('patched', ART, os.path.getsize(ART), 'bytes')
print('new sha256', sh(ART))
