# -*- coding: utf-8 -*-
"""t1 收尾补丁 4：应用 captain/user 在 t1 修订之后下达的三项裁定 + DD-01 结案 + FS-01 重述。

裁定（迟于 t1 修订，属滞后而非错误）：
  R-01 BD-01 限值：用户裁定 = OVERVIEW（TM600 11 mΩ / TM601 7.5 mΩ）；DFT.csv 10/8 mohm 保留为已登记冲突。
  R-02 BD-03 寄存器：captain 裁定 .sv 映射权威（0x10=0x43, 0x59=0x20, 0x61=0x4B, TM600 0x5A=0x02 / TM601 0x5A=0x01）。
  R-03 BD-02 强制/感知对：TM600 force=pmid2sw 且 sense=PMID-SW；TM601 force=sw2pgnd 且 sense=SW-PGND。
  R-04 DD-01：captain 裁定 iset[] 第三槽为 ramp 时间（本任务已独立复核：125 处 iset[] 全部 4 字段，第三槽仅时间形态）。
本补丁保持一切"逐字保留"字段不变（values/units/locators 原样），只增加 resolution/wording。
"""
import os, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

d = json.loads(rt(ART))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# ================================================================ R-01 / PA-01,PA-02（限值裁定）
d['limitConflictPairs']['status'] = 'resolved-by-user-ruling (values retained verbatim in both slots)'
d['pendingUserAdjudication'] = [
  {'id': 'PA-01', 'topic': 'TM600 HS_RDSON limit', 'status': 'resolved-by-user-ruling',
   'optionA': {'value': 11, 'unit': 'mΩ', 'provenance': 'project/DALI/Dali_testmode.xlsx sheet=OVERVIEW!row 132'},
   'optionB': {'value': 10, 'unit': 'mohm', 'provenance': 'project/DALI/input/DFT.csv record index 18 (0-based) = csvRecord 19'},
   'ruledValue': 'OVERVIEW 11 mΩ', 'alternativeRetained': 'DFT.csv 10 mohm / ',
   'rule': 'implementation and spec must use 11 mΩ; the DFT.csv 10 mohm value stays registered in this artifact as a retained alternative, never as the limit'},
  {'id': 'PA-02', 'topic': 'TM601 LS_RDSON limit', 'status': 'resolved-by-user-ruling',
   'optionA': {'value': 7.5, 'unit': 'mΩ', 'provenance': 'project/DALI/Dali_testmode.xlsx sheet=OVERVIEW!row 133'},
   'optionB': {'value': 8, 'unit': 'mohm', 'provenance': 'project/DALI/input/DFT.csv record index 19 (0-based) = csvRecord 20'},
   'ruledValue': 'OVERVIEW 7.5 mΩ', 'alternativeRetained': 'DFT.csv 8 mohm',
   'rule': 'implementation and spec must use 7.5 mΩ; the DFT.csv 8 mohm value stays registered as a retained alternative'},
]
d['limitConflictPairs']['supersedesStatus'] = 'pending-user-adjudication (this is the post-ruling state)'

# ================================================================ R-02 / BD-03（寄存器裁定）
for c in d['conflicts']:
    if c['id'] == 'C-03':
        c['resolution'] = {
          'ruledBy': 'captain', 'ruledAt': now,
          'decision': 'the per-TM reg_config .sv mapping is authoritative',
          'authoritative': {'path': 'project/DALI/reg_config/tm600.sv + tm601.sv',
                            'writes': '0x10=0x43; 0x59=0x20; 0x61=0x4B; TM600 0x5A=0x02 (D2A_BUBO_TM_HSON=1); TM601 0x5A=0x01 (D2A_BUBO_TM_LSON=1)'},
          'superseded': {'path': 'project/DALI/input/DFT.csv records 18/19',
                         'writes': '0x58/0x59/0x61 older map — retained verbatim in this artifact as the superseded alternative'},
          'corroboration': c.get('independentCorroboration', {}).get('strength', ''),
        }
        c['status'] = 'resolved-by-ruling (alternative retained verbatim)'

# ================================================================ R-03 / BD-02 + FS-01 重述 + forceAndSense 非破坏性更正
for it in d['items']:
    if it['tm'] == 'TM600':
        it['forceAndSense']['force'].update({
          'pins': ['PMID', 'SW'], 'ruledPair': 'pmid2sw',
          'ruledBy': 'captain (R-03)', 'authoritativePair': 'pmid2sw',
          'note': 'ruled pair pmid2sw; the reg_config/tm600.sv instrument node is SW (iset[sw,1,1e-3,0]) and DFT.csv names the same loop pmid2sw. '
                  'Instrument-side pin notation vs loop-end notation — see instrumentPin.',
          'instrumentPin': {'node': 'SW', 'evidence': 'reg_config/tm600.sv:38-42 (`NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3); // iset[sw,1,1e-3,0] // pin SW current set to 1A)'},
          'rulingStatus': 'resolved',
        })
        it['forceAndSense']['sense'].update({'ruledPair': 'PMID-SW', 'ruledBy': 'captain (R-03)', 'rulingStatus': 'resolved'})
        it['forceAndSense']['rulingApplied'] = 'R-03: TM600 force pmid2sw / sense PMID-SW — force and sense are the same physical pair (Kelvin separation still to be confirmed by t2)'
    if it['tm'] == 'TM601':
        it['forceAndSense']['force'] = {
          'pins': ['SW', 'PGND'], 'ruledPair': 'sw2pgnd',
          'polarity': 'force the 1 A loop PGND -> floating source -> SW -> LS FET -> PGND (low-side conduction path)',
          'source': 'DFT.csv record index 19: iset[sw2pgnd,1,1e-6,0] (magnitude 1 A, ramp 1 µs per ruling R-04)',
          'authoritativePair': 'sw2pgnd',
          'instrumentPin': {'node': 'PMID_SW', 'evidence': 'reg_config/tm601.sv iset[pmid_sw,1,1e-3,0] — instrument-side pin notation only; it is NOT a statement that current is pushed from PMID'},
          'consistentWithCheckNode': True,
          'checkNode': 'PGND-SW (DFT.csv Check) / SW-PGND (OVERVIEW Notes Rds,on=(SW-PGND)/IPMID2SW)',
          'ruledBy': 'captain (R-03)', 'rulingStatus': 'resolved',
          'priorReading': 'the earlier revision of this artifact recorded the .sv PMID↔SW pair as the force path and flagged it as inconsistent with the SW-PGND check node; that reading is WITHDRAWN by ruling R-03 (the force path is sw2pgnd, PMID is only a powered rail)',
        }
        it['forceAndSense']['sense'].update({'ruledPair': 'SW-PGND', 'ruledBy': 'captain (R-03)', 'rulingStatus': 'resolved'})
        it['forceAndSense']['selfConsistency'] = ('RESOLVED by ruling R-03: the force pair (sw2pgnd) and the sense pair (SW-PGND) are the same physical '
                                                  'low-side conduction path, so the sensed drop IS the LS RDSON drop. The earlier "INCONSISTENT" verdict '
                                                  'was based on reading the .sv instrument pin name isrcPMID_SW as the physical force pair; that reading is withdrawn.')
        it['forceAndSense']['rulingApplied'] = 'R-03: TM601 force sw2pgnd / sense SW-PGND (adopt DFT.csv, NOT the .sv PMID↔SW pair)'
        # 非破坏性更正：保留旧表述在 priorReading，主字段改为裁定结果
        it['channels'][0] = {'role': 'floating force (high current)', 'pins': ['SW', 'PGND'],
                             'sense': 'force the 1 A low-side loop (ruled pair sw2pgnd); instrument node is isrcPMID_SW per reg_config/tm601.sv',
                             'ruledPair': 'sw2pgnd'}
        it['mvMiRequirement']['forcePath'] = it['channels'][0]
        it['mvMiRequirement']['sensePath'] = it['channels'][1]
        it['mvMiRequirement']['notes'] = [
          'R-03 ruled the force/sense pairs: TM601 force sw2pgnd, sense SW-PGND (same physical path -> Kelvin separation is the same question as TM600).',
          'FS-01 remains open ONLY as a t2 schematic-wiring question; the implementation answer is ruled and does not block t5.',
        ]

# ================================================================ FS-01 重述（保留但明确不阻塞）
d['openQuestions'] = [q for q in d['openQuestions'] if not q.startswith(('FS-01', 'DD-01', 'PA-01', 'PA-02'))]
d['openQuestions'].insert(0, 'PA-01 (RESOLVED by user ruling R-01): the limit is OVERVIEW 11 mΩ (sheet=OVERVIEW!row 132); '
                             'DFT.csv 10 mohm (record index 18 / csvRecord 19) is retained verbatim in limitConflictPairs as the '
                             'registered alternative and must not be used as the limit.')
d['openQuestions'].insert(1, 'PA-02 (RESOLVED by user ruling R-01): the limit is OVERVIEW 7.5 mΩ (sheet=OVERVIEW!row 133); '
                             'DFT.csv 8 mohm (record index 19 / csvRecord 20) is retained verbatim as the registered alternative.')
d['openQuestions'].insert(2, 'FS-01 (kept, narrowed — t2 wiring question, NOT a t5 blocker): is the LS floating source physically wired across SW↔PGND '
                             '(the ruled pair per R-03, and the only self-consistent reading) or across PMID↔SW (the reg_config/tm601.sv instrument pin name '
                             'isrcPMID_SW, which is instrument-side notation)? Working/implementation answer = sw2pgnd (R-03); t2 should confirm the physical '
                             'relay path and whether force and sense share pins (Kelvin separation) for both TM600 and TM601.')

# ================================================================ R-04 / DD-01 结案
for x in d.get('dftCsvDefects', []):
    if x['id'] == 'DD-01':
        x['status'] = 'resolved-by-ruling (R-04): the third iset[] field is the ramp time'
        x['resolution'] = {
          'ruledBy': 'captain', 'ruledAt': now,
          'decision': 'the third iset[] field is the ramp/settle time, so iset[sw2pgnd,1,1e-6,0] = 1 A with a 1 µs ramp',
          'evidence_captain': 'reg_config/tm600.sv:38-42 is self-labelling: `NVT_STIM.isrcSW.ramp_isrc_val(1, 1e-3);` // "pin SW current set to 1A" // iset[sw,1,1e-3,0]',
          'evidence_this_task': ('independent enumeration over project/DALI/reg_config/*.sv: 125 iset[...] occurrences, ALL 4-field; '
                                 'field 3 takes only time-shaped values (1e-3 x53, 1e-6 x48, 100e-6 x12, 2e-3 x6, 10e-3 x5, 1e-5 x1) and '
                                 'field 2 only current-shaped values; no 5-field row found in this workspace'),
          'retainedReasoning': 'read literally as a current, 1e-6 A would be 1 µA giving 8 nV across 8 mΩ — below ATE resolution, which is why the ramp-time reading is the only coherent one',
          'residualOddity': 'ate-implementer reports TM627/TM628 use a 5-field variant iset[pmid2sw,-0,9,0,0]; outside TM600/TM601 scope, not re-verified here',
        }
d['openQuestions'].insert(3, 'DD-01 closed by ruling R-04 (third iset field = ramp time): TM601 = 1 A + 1 µs ramp, TM600 = 1 A + 1 ms ramp. '
                             'The DFT.csv phrasing remains confusing and should be fixed at source eventually, but it no longer blocks anything.')

# ================================================================ R-05 BD-07（实现按"两个浮动节点"读法，标注为假设）
d['conflicts'][-1] if False else None

# ================================================================ blockingDecisions 收口
RESOLVED = {
 'BD-01': {'ruledBy': 'user', 'decision': 'OVERVIEW 11 mΩ (TM600) / 7.5 mΩ (TM601) is the limit; DFT.csv 10/8 mohm retained as a registered alternative',
           'affects': 'spec limits for TM600_HS_RDSON / TM601_LS_RDSON'},
 'BD-02': {'ruledBy': 'captain', 'decision': 'TM600 force pmid2sw / sense PMID-SW; TM601 force sw2pgnd / sense SW-PGND (FS-01 narrowed to a t2 wiring question)',
           'affects': 'relay/path selection and the sensed differential pair'},
 'BD-03': {'ruledBy': 'captain', 'decision': 'reg_config/tm600.sv + tm601.sv authoritative (0x10=0x43, 0x59=0x20, 0x61=0x4B, TM600 0x5A=0x02 / TM601 0x5A=0x01); DFT.csv 0x58/0x59/0x61 superseded',
           'affects': 'which FET is forced on'},
}
for b in d['blockingDecisions']:
    if b['id'] in RESOLVED:
        b['status'] = 'closed'
        b['resolution'] = RESOLVED[b['id']]
        b['resolutionRuledAt'] = now
    else:
        b.setdefault('status', 'open')

# ================================================================ rulingsApplied（新增区块）
d['rulingsApplied'] = [
  {'id': 'R-01', 'covers': ['BD-01', 'PA-01', 'PA-02', 'C-01(limit half)'], 'ruledBy': 'user',
   'decision': 'limits = OVERVIEW: TM600 11 mΩ, TM601 7.5 mΩ; DFT.csv 10/8 mohm retained verbatim as a registered alternative',
   'effect': 'spec/implementation use 11 / 7.5 mΩ; both provenances must still be cited side by side'},
  {'id': 'R-02', 'covers': ['BD-03', 'C-03'], 'ruledBy': 'captain',
   'decision': 'per-TM reg_config .sv register mapping is authoritative (TM600 0x5A=0x02 HS, TM601 0x5A=0x01 LS); DFT.csv register rows superseded',
   'effect': 'implementation uses the .sv writes; DFT.csv writes remain in the artifact as the superseded alternative'},
  {'id': 'R-03', 'covers': ['BD-02', 'C-01(pin half)', 'FS-01(implementation half)'], 'ruledBy': 'captain',
   'decision': 'TM600 force pmid2sw / sense PMID-SW; TM601 force sw2pgnd / sense SW-PGND (adopt DFT.csv, not the .sv PMID↔SW pair)',
   'effect': 'FS-01 no longer asserts a contradiction; it is narrowed to a t2 physical-wiring/Kelvin question and does not block t5'},
  {'id': 'R-04', 'covers': ['DD-01'], 'ruledBy': 'captain',
   'decision': 'the third iset[] field is the ramp time; TM601 = 1 A + 1 µs ramp, TM600 = 1 A + 1 ms ramp',
   'effect': 'DD-01 closed; the 8 nV argument retained as the reason the ramp reading is the only coherent one'},
  {'id': 'R-05', 'covers': ['BD-07'], 'ruledBy': 'implementer (working assumption, upstream)',
   'decision': 'TM600 OVERVIEW Special="Y / 2 FLOAT" is read as two floating nodes — this is an assumption, not a source fact',
   'effect': 'labelled an assumption, not a source fact; BD-07 stays open in this artifact until a source confirms it'},
]
d['blockingDecisionsSummary'] = {
  'closed': ['BD-01', 'BD-02', 'BD-03'],
  'open': ['BD-05', 'BD-06', 'BD-07'],
  'openNotes': {
    'BD-05': 'TM600/TM601 force compliance/clamp still stated by no source (golden case uses 50% x 1 V = 0.5 V)',
    'BD-06': 'TM1205 has no ExpectValue/tolerance in any DFT source',
    'BD-07': 'Y / 2 FLOAT semantics — implementation proceeds on the ruled two-floating-node reading, still an assumption',
  },
}

# ================================================================ N-01 哈希历史刷新（本版为已发布修订）
notices = d.setdefault('notices', [])
n01 = next((n for n in notices if n.get('id') == 'N-01'), None)
if n01 is None:
    n01 = {'id': 'N-01', 'topic': 'artifact hash changed after the first handoff — re-hash, do not trust quoted digests', 'history': []}
    notices.append(n01)
# 重建为确定性的"已发布修订"序列（幂等：每次生成都得到同一数组）
n01['history'] = [
    {'sha256': 'f3faedc26675a4ad06d66569c19ec17ee1c06211336eb4feba4fb40e30d2e3c8', 'sizeBytes': 88109,
     'note': 'first build (t1 handoff)'},
    {'sha256': '478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755', 'sizeBytes': 88101,
     'note': 'TM1205 md hash corrected'},
    {'sha256': '85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e', 'sizeBytes': 99058,
     'note': 'captain follow-up (PA-01/PA-02, plaintext anchors, CR-01 symbols, MV&MI)'},
    {'sha256': '0a1c3b1e474c508c63d639d69e3b905ce94cb5b8085c98745c05a6625669597e', 'sizeBytes': 107133,
     'note': 'implementer-review response (forceAndSense split, DD-01, C-03 corroboration)'},
    {'sha256': 'CURRENT-REVISION', 'sizeBytes': None,
     'note': 'post-ruling revision (R-01..R-05 applied: BD-01/02/03 closed, DD-01 closed, FS-01 narrowed)'},
]

# ================================================================ revisions + verification
d['revisions'].append({
  'at': now, 'by': 'dft-expert (t1 close-out 3, applying post-revision rulings R-01..R-05)',
  'changes': [
    'PA-01/PA-02: limit conflicts now resolved-by-user-ruling (OVERVIEW 11 / 7.5 mΩ ruled; DFT.csv 10 / 8 mohm retained verbatim)',
    'C-03/BD-03: resolution recorded — .sv mapping authoritative, DFT.csv register rows superseded (retained)',
    'C-01/BD-02 + items[TM601].forceAndSense: force pair corrected to the ruled sw2pgnd; the earlier "INCONSISTENT" verdict WITHDRAWN (it came from reading the .sv instrument pin name isrcPMID_SW as the physical force pair); priorReading kept for audit',
    'FS-01 narrowed and restated: now a t2 physical-wiring/Kelvin question, explicitly NOT a t5 blocker',
    'DD-01 closed by ruling R-04 (third iset field = ramp time); 8 nV reasoning retained',
    'added rulingsApplied (R-01..R-05) and blockingDecisionsSummary (closed BD-01/02/03, open BD-05/06/07)',
  ],
})
d['verification']['rulingsApplied'] = ['R-01', 'R-02', 'R-03', 'R-04', 'R-05']
d['verification']['openBlockerIds'] = ['BD-05', 'BD-06', 'BD-07']

with open(ART, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
import hashlib
b = open(ART, 'rb').read()
print('patched', ART, len(b), 'bytes')
print('new sha256', hashlib.sha256(b).hexdigest())
