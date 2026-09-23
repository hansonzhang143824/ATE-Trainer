# -*- coding: utf-8 -*-
"""t1 收尾补丁：按 captain 追加的取证要求修订已完成的 dft-ir.json。

追加要求（captain 2026-09-16 补充，t1 已 completed）：
  1. TM600/TM601 限值冲突成对并列（OVERVIEW vs DFT.csv）+ 显式冲突条目 + openQuestion，禁止折中/静默对齐/只留一个。
  2. source 引用带 python 明文 sha256 与字节数（DFT.csv 明文锚点 16862 B / B92D203F…，xlsx 12210607 B / D9D721A3…）。
  3. TM600/TM601 皆 MV&MI → force 通路 + 同时 Kelvin 差分读取。
  4. 符号名已裁定 TM600_HS_RDSON / TM601_LS_RDSON（依据 scripts/gen_testitems_meta.py 命名硬规则）。
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

CSV_P = os.path.join(ROOT, 'project/DALI/input/DFT.csv')
XLSX_P = os.path.join(ROOT, 'project/DALI/Dali_testmode.xlsx')
CSV_SHA_U = sh(CSV_P).upper()
XLSX_SHA_U = sh(XLSX_P).upper()
CSV_SIZE = os.path.getsize(CSV_P)
XLSX_SIZE = os.path.getsize(XLSX_P)

d = json.loads(rt(ART))

# ---------------------------------------------------------------- 1) 限值冲突成对并列
PAIRS = {
 'TM600': {
   'overview': {'source': 'project/DALI/Dali_testmode.xlsx (sheet OVERVIEW)',
                'item': 'TM600', 'level': 'BUBO', 'name': 'HS_RDSON',
                'expectValue': 11, 'unit': 'mΩ', 'test': 'direct', 'special': 'Y\n2 FLOAT',
                'locator': 'sheet=OVERVIEW!row 132 (Item=TM600)'},
   'dftCsv': {'source': 'project/DALI/input/DFT.csv',
              'recordIndex0Based': 18, 'recordIndex1Based': 19, 'csvRecord': 19,
              'item': 'TM600', 'functionName': 'RDSON_TEST', 'shortName': 'HS_RDSON',
              'expectValue': 10, 'unit': 'mohm', 'check': 'PMID-SW',
              'dynamic': 'iset[pmid2sw,1,1e-3,0]', 'type': 'MV&MI',
              'locator': 'DFT.csv record index 18 (0-based) = csvRecord 19 (1-based); Item=TM600'},
   'delta': 'TM600 11 mΩ (OVERVIEW) vs 10 mohm (DFT.csv) — 1 mΩ / 9.1% difference on a milliohm limit',
 },
 'TM601': {
   'overview': {'source': 'project/DALI/Dali_testmode.xlsx (sheet OVERVIEW)',
                'item': 'TM601', 'level': 'BUBO', 'name': 'LS_RDSON',
                'expectValue': 7.5, 'unit': 'mΩ', 'test': 'direct', 'special': None,
                'locator': 'sheet=OVERVIEW!row 133 (Item=TM601)'},
   'dftCsv': {'source': 'project/DALI/input/DFT.csv',
              'recordIndex0Based': 19, 'recordIndex1Based': 20, 'csvRecord': 20,
              'item': 'TM601', 'functionName': None, 'shortName': 'LS_RDSON',
              'expectValue': 8, 'unit': 'mohm', 'check': 'PGND-SW',
              'dynamic': 'iset[sw2pgnd,1,1e-6,0]', 'type': 'MV&MI',
              'locator': 'DFT.csv record index 19 (0-based) = csvRecord 20 (1-based); Item=TM601'},
   'delta': 'TM601 7.5 mΩ (OVERVIEW) vs 8 mohm (DFT.csv) — 0.5 mΩ / 6.7% difference',
 },
}
d['limitConflictPairs'] = {
  'policy': 'NO-FOLD: both values are recorded verbatim with their own locator; no averaging, no silent alignment to meta, neither value may be dropped. The choice is pending explicit user adjudication.',
  'status': 'pending-user-adjudication',
  'pairs': PAIRS,
}
d['pendingUserAdjudication'] = [
  {'id': 'PA-01', 'topic': 'TM600 HS_RDSON limit',
   'optionA': '11 mΩ (project/DALI/Dali_testmode.xlsx sheet OVERVIEW!row 132, Unit=mΩ, Special="Y\n2 FLOAT")',
   'optionB': '10 mohm (project/DALI/input/DFT.csv record index 18 / csvRecord 19, Unit=mohm)',
   'status': 'open', 'note': '用户裁定尚未下达；禁止折中或只保留一个'},
  {'id': 'PA-02', 'topic': 'TM601 LS_RDSON limit',
   'optionA': '7.5 mΩ (project/DALI/Dali_testmode.xlsx sheet OVERVIEW!row 133, Unit=mΩ, Special 空)',
   'optionB': '8 mohm (project/DALI/input/DFT.csv record index 19 / csvRecord 20, Unit=mohm)',
   'status': 'open', 'note': '用户裁定尚未下达；禁止折中或只保留一个'},
]

# ---------------------------------------------------------------- 2) DFT.csv 冲突条目补 0-based 索引
csv_note = ('DFT.csv record index 18/19 (0-based) = csvRecord 19/20 (1-based); '
            'plaintext anchor: %d bytes, sha256 %s (python byte-mode read; PowerShell sees a TSZ# ciphertext head)'
            % (CSV_SIZE, CSV_SHA_U))
for c in d['conflicts']:
    if c['id'] == 'C-01':
        c['recordIndexNote'] = csv_note
        for s in c['sources']:
            if 'DFT.csv' in s.get('source', ''):
                s['recordIndex'] = '0-based 18 (TM600) / 19 (TM601) = 1-based 19 / 20'
                s['plaintextSha256'] = CSV_SHA_U
                s['plaintextSize'] = CSV_SIZE
    if c['id'] == 'C-05':
        c['recordIndexNote'] = 'same 0-based indices 18/19 for the DFT_restored.csv comparison'

# ---------------------------------------------------------------- 3) source 明文锚点
d['source']['plaintextAnchors'] = [
  {'path': 'project/DALI/Dali_testmode.xlsx', 'sha256': XLSX_SHA_U, 'sizeBytes': XLSX_SIZE,
   'role': 'OVERVIEW sheet = DFT intent source of record (sheet 3 of 22)',
   'note': 'python byte-mode read; on-disk head PK\\x03\\x04 (zip/OOXML container)'},
  {'path': 'project/DALI/input/DFT.csv', 'sha256': CSV_SHA_U, 'sizeBytes': CSV_SIZE,
   'role': 'secondary intent source (row-per-TM variant)',
   'note': 'python byte-mode read yields plaintext starting with the header "Item,Function Name,..." while PowerShell/grep see a TSZ# ciphertext head — this sha256 is the plaintext anchor, NOT a ciphertext hash'},
  {'path': 'project/DALI/input/DFT_restored.csv', 'sha256': sh(os.path.join(ROOT, 'project/DALI/input/DFT_restored.csv')).upper(),
   'sizeBytes': os.path.getsize(os.path.join(ROOT, 'project/DALI/input/DFT_restored.csv')),
   'role': 'recovered copy of DFT.csv; differs in the TM600/TM601 rows', 'note': 'plaintext anchor'},
  {'path': 'project/DALI/reg_config/tm600.sv', 'sha256': sh(os.path.join(ROOT, 'project/DALI/reg_config/tm600.sv')).upper(),
   'sizeBytes': os.path.getsize(os.path.join(ROOT, 'project/DALI/reg_config/tm600.sv')),
   'role': 'TM600 register evidence (1495 B)', 'note': 'python plaintext anchor'},
  {'path': 'project/DALI/reg_config/tm601.sv', 'sha256': sh(os.path.join(ROOT, 'project/DALI/reg_config/tm601.sv')).upper(),
   'sizeBytes': os.path.getsize(os.path.join(ROOT, 'project/DALI/reg_config/tm601.sv')),
   'role': 'TM601 register evidence (1378 B)', 'note': 'python plaintext anchor'},
  {'path': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', 'sha256': sh(r'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').upper(),
   'sizeBytes': os.path.getsize(r'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'),
   'role': 'current implementation in the only writable tree', 'note': 'python plaintext anchor'},
]
d['source']['hashConvention'] = ('all sha256 values in this artifact were computed over the bytes read through the '
                                 'python (DLP-authorized) channel, i.e. the PLAINTEXT anchor; uppercase for the '
                                 'plaintextAnchors block, lowercase elsewhere. The grep tool may also show plaintext '
                                 'in this session but is not used as a hash anchor.')

# ---------------------------------------------------------------- 4) 符号名裁定
d['captainRulings'] = [
  {'id': 'CR-01', 'topic': 'TM600/TM601 symbol names',
   'ruling': {'TM600': 'TM600_HS_RDSON', 'TM601': 'TM601_LS_RDSON'},
   'basis': 'naming hard rule in scripts/gen_testitems_meta.py line 91: '
            "DUT_API int ((?:TM\\d+(?:_\\d+)?_\\w+|Trim_\\w+))\\(short funcindex — i.e. TM<item>_<SHORTNAME>; "
            'TM600 ShortName=HS_RDSON and TM601 ShortName=LS_RDSON, so the symbols are TM600_HS_RDSON / TM601_LS_RDSON',
   'supersedes': 'acceptance-plan.json symbolHint RDSON_TEST_HS / RDSON_TEST_LS (placeholders)',
   'status': 'applied',
   'appliedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds')},
]
for it in d['items']:
    if it['tm'] == 'TM600':
        it['symbol'] = 'TM600_HS_RDSON'
        it['symbolRuling'] = 'CR-01 (captain): TM<item>_<SHORTNAME> per scripts/gen_testitems_meta.py:91'
        it['symbolHintFromPlan'] = 'RDSON_TEST_HS (acceptance-plan.json placeholder, superseded by CR-01)'
    if it['tm'] == 'TM601':
        it['symbol'] = 'TM601_LS_RDSON'
        it['symbolRuling'] = 'CR-01 (captain): TM<item>_<SHORTNAME> per scripts/gen_testitems_meta.py:91'
        it['symbolHintFromPlan'] = 'RDSON_TEST_LS (acceptance-plan.json placeholder, superseded by CR-01)'

# ---------------------------------------------------------------- 5) MV&MI force + Kelvin
for it in d['items']:
    if it['tm'] in ('TM600', 'TM601'):
        it['mvMiRequirement'] = {
          'type': 'MV&MI',
          'source': 'project/DALI/input/DFT.csv record index %s (0-based), Type=MV&MI' % ('18' if it['tm'] == 'TM600' else '19'),
          'requirement': 'a force path (current forced through the DUT pin pair) is mandatory AND the differential voltage '
                         'must be read simultaneously on the same pair with a separate Kelvin sense (force/sense separation); '
                         'RON = V_measured / I_measured x 1e3 mΩ — the programmed current must never be substituted for the '
                         'measured one (R-VIR).',
          'forcePath': it['channels'][0],
          'sensePath': it['channels'][1],
          'notes': [
            'The DFT does not state whether force and sense share physical pins; with only one floating resource available, '
            'the verification must confirm Kelvin separation or explicitly declare the shared-pin limitation.',
            'Because the force and sense pins differ between sources (BD-02), the final force/sense assignment is a t3/t4 decision.',
          ],
        }

# ---------------------------------------------------------------- 6) openQuestions 补充
d['openQuestions'] = [q for q in d['openQuestions'] if not q.startswith('PA-')]
d['openQuestions'].insert(0, 'PA-01 (pending user adjudication): TM600 11 mΩ (OVERVIEW!row 132) vs 10 mohm (DFT.csv record index 18) — both recorded verbatim, no fold.')
d['openQuestions'].insert(1, 'PA-02 (pending user adjudication): TM601 7.5 mΩ (OVERVIEW!row 133) vs 8 mohm (DFT.csv record index 19) — both recorded verbatim, no fold.')
d['openQuestions'].insert(2, 'CR-01 resolved the TM600/TM601 symbol names (TM600_HS_RDSON / TM601_LS_RDSON); the acceptance-plan placeholder hints RDSON_TEST_HS/LS are superseded.')

# ---------------------------------------------------------------- 7) 修订记录
d['revisions'] = d.get('revisions', [])
d['revisions'].append({
  'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
  'by': 'dft-expert (t1 close-out, captain follow-up requirements)',
  'changes': [
    'added limitConflictPairs + pendingUserAdjudication (PA-01/PA-02): TM600 11 mΩ vs 10 mohm, TM601 7.5 mΩ vs 8 mohm recorded as paired verbatim evidence',
    'added source.plaintextAnchors with python plaintext sha256 + byte counts (DFT.csv 16862 B / %s; xlsx %d B / %s)' % (CSV_SHA_U, XLSX_SIZE, XLSX_SHA_U),
    'added source.hashConvention (plaintext anchoring; grep output is not a hash anchor)',
    'added captainRulings CR-01 and renamed the symbols to TM600_HS_RDSON / TM601_LS_RDSON',
    'added items[TM600/TM601].mvMiRequirement (force path + simultaneous Kelvin differential read; RON from measured V/I)',
    'annotated conflict C-01/C-05 with the 0-based record indices 18/19 (1-based 19/20) and the DFT.csv plaintext anchor',
  ],
})

# ---------------------------------------------------------------- 8) verification 覆盖清单
d['verification']['plaintextAnchorDftCsv'] = {'sizeBytes': CSV_SIZE, 'sha256': CSV_SHA_U}
d['verification']['symbolNames'] = {'TM600': 'TM600_HS_RDSON', 'TM601': 'TM601_LS_RDSON', 'ruling': 'CR-01'}
d['verification']['limitConflictPairCount'] = 2

with open(ART, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print('patched', ART, os.path.getsize(ART), 'bytes')
print('sha256', sh(ART))
print('symbols:', [(i['tm'], i['symbol']) for i in d['items'] if i['tm'] in ('TM600', 'TM601')])
print('pendingUserAdjudication:', [p['id'] for p in d['pendingUserAdjudication']])
