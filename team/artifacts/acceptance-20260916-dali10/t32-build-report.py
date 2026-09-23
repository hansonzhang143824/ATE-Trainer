# -*- coding: utf-8 -*-
"""t32: build the independent verification report (verification-report.json)."""
import os, sys, json, re, hashlib, datetime

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RD = os.path.join(ROOT, 'team', 'artifacts', RUN)
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"
DEVEL = r"D:/PROJECT6-DALI/devel"
OUT = os.path.join(RD, 'verification-report.json')

def sha(p):
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

def entry(rel):
    p = os.path.join(RD, rel)
    return {'path': 'team/artifacts/%s/%s' % (RUN, rel), 'sizeBytes': os.path.getsize(p), 'sha256': sha(p)}

def strip_comments(src):
    out = []; i, n = 0, len(src); in_line = in_block = in_str = None
    while i < n:
        c = src[i]; nxt = src[i + 1] if i + 1 < n else ''
        if in_line:
            if c == '\n': in_line = False; out.append(c)
            i += 1; continue
        if in_block:
            if c == '*' and nxt == '/': in_block = False; i += 2; continue
            if c == '\n': out.append(c)
            i += 1; continue
        if in_str:
            out.append(c)
            if c == '\\': out.append(nxt); i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c == '/' and nxt == '/': in_line = True; i += 2; continue
        if c == '/' and nxt == '*': in_block = True; i += 2; continue
        if c in ('"', "'"): in_str = c; out.append(c); i += 1; continue
        out.append(c); i += 1
    return ''.join(out)

def func_block(text, name):
    m = re.search(r'DUT_API\s+int\s+' + re.escape(name) + r'\s*\(', text)
    if not m: return None, None, None
    brace = text.find('{', m.end()); depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == '{': depth += 1
        elif text[pos] == '}':
            depth -= 1
            if depth == 0:
                return text[m.start():pos + 1], text.count('\n', 0, m.start()) + 1, text.count('\n', 0, pos) + 1
    return text[m.start():], text.count('\n', 0, m.start()) + 1, None

# ---------------------------------------------------------------- recomputation
tgt = os.path.join(TARGET, 'source', 'test.cpp')
txt = rt(tgt); st = strip_comments(txt)
deployed = {'path': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', 'sizeBytes': os.path.getsize(tgt), 'sha256': sha(tgt),
            'lines': txt.count('\n') + 1, 'bom': txt.startswith('\ufeff')}
b600, s600, e600 = func_block(txt, 'TM600_HS_RDSON')
b601, s601, e601 = func_block(txt, 'TM601_LS_RDSON')
seton600 = [[t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1'] for so in re.findall(r'cbite\.SetOn\((.*?)\)\s*;', b600 or '', re.DOTALL)]
seton601 = [[t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1'] for so in re.findall(r'cbite\.SetOn\((.*?)\)\s*;', b601 or '', re.DOTALL)]
INV = [('delay_ms(1)', r'delay_ms\(1\)', 6), ('delay_ms(2)', r'delay_ms\(2\)', 0),
       ('SetClamp(50,50)', r'SetClamp\(\s*50\s*,\s*50\s*\)', 2),
       ('MeasureVI(200,5,FPVIe_MV_X10)', r'MeasureVI\(\s*200\s*,\s*5\s*,\s*FPVIe_MV_X10\s*\)', 2),
       ('bare 126', r'(?<![0-9A-Za-z_])126(?![0-9A-Za-z_])', 0), ('K126_V1P5_CAP', r'K126_V1P5_CAP', 2),
       ('ERROR_RES', r'ERROR_RES', 2)]
inv_scope = {}
for label, pat, expected in INV:
    b600c = len(re.findall(pat, strip_comments(b600 or '')))
    b601c = len(re.findall(pat, strip_comments(b601 or '')))
    inv_scope[label] = {'expectedInTwoFunctions': expected, 'TM600': b600c, 'TM601': b601c, 'sum': b600c + b601c,
                        'match': (b600c + b601c) == expected}
inv_whole = {label: len(re.findall(pat, st)) for label, pat, _ in INV}

payload_p = os.path.join(RD, 'implementation-payload-TM600-TM601.cpp')
ptxt = strip_comments(rt(payload_p))
payload = {'path': 'team/artifacts/%s/implementation-payload-TM600-TM601.cpp' % RUN,
           'sizeBytes': os.path.getsize(payload_p), 'sha256': sha(payload_p),
           'invariants': {label: len(re.findall(pat, ptxt)) for label, pat, _ in INV},
           'K109_BUSL1_PB0': len(re.findall(r'K109_BUSL1_PB0', ptxt)), 'K110_ACM18_BST': len(re.findall(r'K110_ACM18_BST', ptxt)),
           'setOn600': [[t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1']
                        for so in re.findall(r'cbite\.SetOn\((.*?)\)\s*;', func_block(rt(payload_p), 'TM600_HS_RDSON')[0] or '', re.DOTALL)]}

bak = os.path.join(RD, 'backups', 'test.cpp.before_TM600_TM601.bak')
btxt = rt(bak)
baseline = {'path': 'team/artifacts/%s/backups/test.cpp.before_TM600_TM601.bak' % RUN, 'sizeBytes': os.path.getsize(bak),
            'sha256': sha(bak), 'hits': {t: btxt.count(t) for t in ('TM600', 'TM601', 'RDSON')},
            'functionsPresent': {n: bool(re.search(r'DUT_API\s+int\s+' + n + r'\s*\(', btxt)) for n in ('TM600_HS_RDSON', 'TM601_LS_RDSON')}}

goldp = os.path.join(ROOT, 'knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp')
gtxt = rt(goldp)
probes = [l.strip() for l in gtxt.splitlines() if l.strip().startswith(('FPVI.Set(', 'FPVI.MeasureVI(', 'VBAT_ACM.Set', 'BTST_ACM.Set', 'PMID_FOVI.Set'))]
golden = {'path': 'knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp', 'sizeBytes': os.path.getsize(goldp),
          'sha256': sha(goldp), 'probedDistinctiveLines': len(probes),
          'hitsInPayload': [q for q in probes if q in rt(payload_p)],
          'hitsInDeployed': [q for q in probes if q in txt],
          'verdict': 'no copied golden bytes: 0/%d distinctive golden statements appear in either candidate' % len(probes)}

devel = {}
for rel in (('source', 'test.cpp'), ('source', 'StdAfx.h'), ('source', 'sub.cpp'), ('source', 'Pin_Channel_define.h')):
    a = os.path.join(TARGET, *rel); b = os.path.join(DEVEL, *rel)
    devel['/'.join(rel)] = {'target': sha(a), 'devel': sha(b), 'identical': sha(a) == sha(b),
                            'targetSize': os.path.getsize(a), 'develSize': os.path.getsize(b)}

# contract requirement for TM600 BST closure
cs = os.path.join(RD, 'setup-contract.json')
c = json.loads(rt(cs))
cstext = json.dumps(c, ensure_ascii=False)


def deepfind(node, key):
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key: hits.append(v)
            hits += deepfind(v, key)
    elif isinstance(node, list):
        for v in node: hits += deepfind(v, key)
    return hits

needs = deepfind(c, 'needsClosed')
bst_needs = []
for n in needs:
    s = json.dumps(n, ensure_ascii=False)
    if '109' in s or '110' in s or '138' in s or '139' in s:
        bst_needs.append(n)
bst_compare = []
required = ['K109_BUSL1_PB0', 'K110_ACM18_BST']
for r in required:
    num = re.match(r'K(\d+)', r).group(1)
    where = 'contract.needsClosed entries containing %s' % num
    if r in (b600 or ''):
        state = 'CLOSED in deployed TM600 SetOn'
    elif r in (ptxt):
        state = 'present in payload, ABSENT from deployed test.cpp'
    else:
        state = 'absent everywhere'
    bst_compare.append({'required': r, 'requirementLocator': where, 'deployedState': state,
                        'deployedCount': (b600 or '').count(r), 'payloadCount': len(re.findall(r, ptxt))})

# ---------------------------------------------------------------- findings
findings = [
 {'id': 'T32-F1', 'severity': 'blocker', 'category': 'bst-closure / deployed-revision',
  'problem': ('contract-required BST excitation relays K109_BUSL1_PB0 and K110_ACM18_BST are ABSENT from the deployed TM600_HS_RDSON '
              'SetOn set in D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp (%d B / %s). The t29 repair exists only in '
              'implementation-payload-TM600-TM601.cpp (%d B / %s), which contains both. The deployed set is the pre-t29 one.'
              % (deployed['sizeBytes'], deployed['sha256'][:16], payload['sizeBytes'], payload['sha256'][:16])),
  'file': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', 'line': 9057,
  'requiredFix': ('land the payload containing K109/K110 into the target tree (REPLACE semantics on the TM600/TM601 region), then '
                  're-run the gates against the landed revision and re-run this verification. Until then the BST-SW 5 V excitation '
                  'route required by the contract is not closed in executable code.'),
  'evidence': {'deployedSetOn': seton600[0] if seton600 else None,
               'payloadSetOn': payload['setOn600'][0] if payload['setOn600'] else None,
               'deployedK109count': (b600 or '').count('K109'), 'deployedK110count': (b600 or '').count('K110')}},
 {'id': 'T32-F2', 'severity': 'high', 'category': 'reviewed-object identity',
  'problem': ('the independent review t24 (verdict=pass) was performed on payload 444810dd… (35014 B), and the object it verified is '
              'not the object that is deployed today (15c7d2b8…): the reviewed payload contained bare relay token 126 while the deployed '
              'file uses K126_V1P5_CAP, and the reviewed SetOn lists lack K60_BUSL0_VCP / K85_CAP_PMID that the deployed file has. '
              'Neither the reviewed payload hash nor the deployed hash appears in the review text.'),
  'file': 'team/artifacts/%s/review/t24-implementation-review.md' % RUN,
  'requiredFix': 'record which revision each review verdict applies to (payload sha256 in the review header) and re-review after the landing; a verdict that predates the deployed bytes cannot be counted as review of the deployment.',
  'evidence': {'reviewCitedHashes': ['444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c', 'dce54185d89382bfdd1a58196eb7b410ca88646aa82d38a3dd9820d3f868e18f'],
               'deployedHash': deployed['sha256'], 'payloadHash': payload['sha256']}},
 {'id': 'T32-F3', 'severity': 'high', 'category': 'gate evidence attribution',
  'problem': ('the GREEN gate evidence circulated for this run (gate-logs-t25-verify, gate-logs-t28 — both "no new red") does not belong to the '
              'deployed revision. Those logs report relay-trace "功能规则 182 处, FR-001 反向 2 处" with zero TM601 warnings, whereas the deployed '
              'revision produces "179 处 / 反向 4 处" plus two TM601_FR-001 warnings plus two "虚构继电器名 126" FAILs (see gate-logs-t25/relay-trace.log). '
              'The 179/4 run is the one whose inputs match the deployed tree state.'),
  'file': 'team/artifacts/%s/gate-logs-t25-verify/relay-trace.log' % RUN,
  'requiredFix': 'after the landing, re-run scripts/run_gates.ps1 against the target tree and record the revision hash inside the log directory; do not carry forward gate logs from a different revision.',
  'evidence': {'deployedStateLog': 'team/artifacts/%s/gate-logs-t25/relay-trace.log (179 / 4 / NEW-RED)' % RUN,
               'carriedForwardLogs': ['gate-logs-t25-verify/relay-trace.log (182 / 2 / PASSED, 18:58:58)',
                                      'gate-logs-t28/relay-trace.log (182 / 2 / PASSED, 19:22:25)'],
               'targetMtime': '2026-09-16T18:53:33'}},
 {'id': 'T32-F4', 'severity': 'medium', 'category': 'schema gap (verification unreachable)',
  'problem': ('the contract\'s verify command `python scripts/validate_team_artifact.py verification-report <artifact>` cannot pass: '
              'team/schemas/verification-report.schema.json does not exist (the validator resolves schemas as '
              'team/schemas/<name>.schema.json). Exit code observed: 1, FileNotFoundError. The verification kind therefore has no schema in this run.'),
  'file': 'scripts/validate_team_artifact.py', 'line': 101,
  'requiredFix': ('the schema owner must add team/schemas/verification-report.schema.json (out of t32\'s in-scope paths, which are limited to '
                  'verification-report.json). This report is emitted in a schema-shaped layout so it can be re-validated unchanged once the schema exists.'),
  'evidence': {'schemaDir': sorted(os.listdir(os.path.join(ROOT, 'team', 'schemas'))),
               'command': 'python scripts/validate_team_artifact.py verification-report team/artifacts/%s/verification-report.json' % RUN,
               'observed': 'FileNotFoundError: .../team/schemas/verification-report.schema.json'}},
 {'id': 'T32-F5', 'severity': 'low', 'category': 'reviewable-invariant scoping',
  'problem': ('the invariant counts in the acceptance criteria (delay_ms(1)x6, SetClamp(50,50)x2, MeasureVI(200,5,FPVIe_MV_X10)x2, bare 126=0, '
              'K126_V1P5_CAP=2, ERROR_RES=2) hold exactly for the payload / the two TM600+TM601 function bodies, not for whole-file test.cpp '
              '(whole file: delay_ms(1)=292, ERROR_RES=4, K57_CAP_BST_SW=6, K45_Cap_SW1_BST1=1, K5_VBUS_Cap=9). A whole-file recomputation '
              'would read as a mismatch.'),
  'file': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
  'requiredFix': 'state the scope (payload file, or the two function bodies) whenever these invariants are quoted.',
  'evidence': {'scoped': inv_scope, 'wholeFile': inv_whole}},
]

acceptance = [
 {'criterion': '真实新增能力取证：TM600/TM601 为真实新增（改动前基线命中=0）且非黄金副本',
  'status': 'passed',
  'evidence': ('baseline team/artifacts/%s/backups/test.cpp.before_TM600_TM601.bak = 434629 B / %s；TM600=%d TM601=%d RDSON=%d；两函数均不存在。'
               '黄金 knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp = 6106 B / %s；其 %d 条特征语句在 payload 中命中 %d 条、在部署文件中命中 %d 条。'
               '部署文件现算 %d B / %s，含 TM600_HS_RDSON(L9057-9204) 与 TM601_LS_RDSON(L9217-9353)。')
              % (RUN, baseline['sha256'], baseline['hits']['TM600'], baseline['hits']['TM601'], baseline['hits']['RDSON'],
                 golden['sha256'], golden['probedDistinctiveLines'], len(golden['hitsInPayload']), len(golden['hitsInDeployed']),
                 deployed['sizeBytes'], deployed['sha256'])},
 {'criterion': '八项审查纪律逐条核验（命令 + exit code + locator）',
  'status': 'passed',
  'evidence': '见 eightDisciplineAudit；逐条给出命令、exit code 与产物 locator。'},
 {'criterion': '独立复算落盘结果（哈希 / 出现次数 / 去注释不变量）',
  'status': 'passed',
  'evidence': ('python 明文现算 deployed=%d B/%s；TM600 出现 %d 次、TM601 %d 次（去注释后各 %d 次，均为函数名/参数名声明）；'
               '去注释不变量按"两函数体"口径逐条相符：%s。整个文件口径的对照值见 findings T32-F5。')
              % (deployed['sizeBytes'], deployed['sha256'], txt.count('TM600'), txt.count('TM601'), st.count('TM600'),
                 json.dumps({k: v['sum'] for k, v in inv_scope.items()}, ensure_ascii=False))},
 {'criterion': 'BST 闭合集合符合性（t29 后）：TM600 SetOn 是否含 K109/K110 + 对照表',
  'status': 'failed',
  'evidence': ('部署 TM600 SetOn = %s —— **不含 K109/K110**（各 0 次）；payload 同函数 SetOn = %s —— 两者均在。'
               '见 findings T32-F1 与 bstClosureComparison。'
               % (json.dumps(seton600[0] if seton600 else None, ensure_ascii=False),
                  json.dumps(payload['setOn600'][0] if payload['setOn600'] else None, ensure_ascii=False)))},
 {'criterion': 'devel 零写入（devel 与目标树同哈希证据）',
  'status': 'passed',
  'evidence': ('StdAfx.h 与 sub.cpp（以及 Pin_Channel_define.h）在 devel 与目标树**逐字节相同**：%s。'
               'test.cpp 不同属预期且由基线锚定：devel=%s（=改前基线 5c9cb3f9…），target=%s；本任务未对 devel 做任何写操作。')
              % (json.dumps({k: v['identical'] for k, v in devel.items() if k != 'source/test.cpp'}, ensure_ascii=False),
                 devel['source/test.cpp']['devel'], devel['source/test.cpp']['target'])},
 {'criterion': '产出 verification-report.json 并通过 validate_team_artifact.py（exit 0）',
  'status': 'failed',
  'evidence': ('报告已产出（本文件）。但契约要求的 verify 命令无法 exit 0：team/schemas/verification-report.schema.json **不存在**，'
               'validator 以 FileNotFoundError/exit 1 结束（实测）。见 findings T32-F4。')},
]

report = {
 'schema': 'verification-report (team/schemas/verification-report.schema.json — MISSING in this run; see T32-F4)',
 'runId': RUN, 'task': 't32', 'producedBy': 'dft-expert',
 'generatedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
 'subject': {'claim': 'TM600_HS_RDSON / TM601_LS_RDSON are real new capabilities, landed and gate-verified',
             'deployedArtifact': deployed, 'payloadArtifact': payload},
 'verdict': 'fail',
 'verdictReason': ('Two of six acceptance criteria fail. (1) T32-F1: the contract-required BST excitation relays K109/K110 are absent from the '
                   'deployed TM600 SetOn — the t29 repair is in the payload only. (2) The contract verify command cannot exit 0 because '
                   'team/schemas/verification-report.schema.json does not exist (T32-F4). Additionally the GREEN gate logs in circulation '
                   'and the t24 review verdict do not belong to the deployed revision (T32-F2/T32-F3).'),
 'newCapabilityProof': {'baseline': baseline, 'goldenNotCopied': golden,
                        'deployedFunctions': {'TM600_HS_RDSON': {'lines': [s600, e600], 'chars': len(b600 or '')},
                                              'TM601_LS_RDSON': {'lines': [s601, e601], 'chars': len(b601 or '')}}},
 'independentRecomputation': {'deployed': deployed, 'tokenCounts': {'TM600_raw': txt.count('TM600'), 'TM601_raw': txt.count('TM601'),
                              'TM600_commentsStripped': st.count('TM600'), 'TM601_commentsStripped': st.count('TM601'),
                              'TM600_HS_RDSON_stripped': st.count('TM600_HS_RDSON'), 'TM601_LS_RDSON_stripped': st.count('TM601_LS_RDSON')},
                              'invariantsScopedToTwoFunctions': inv_scope, 'invariantsWholeFile': inv_whole,
                              'payloadInvariants': payload['invariants']},
 'bstClosureComparison': {'contractPath': 'team/artifacts/%s/setup-contract.json' % RUN, 'contractSha256': sha(cs),
                          'contractSizeBytes': os.path.getsize(cs),
                          'contractNeedsClosedEntriesMentioning109_110': bst_needs[:4],
                          'requiredVsDeployed': bst_compare,
                          'deployedSetOnTM600': seton600[0] if seton600 else None,
                          'payloadSetOnTM600': payload['setOn600'][0] if payload['setOn600'] else None,
                          'deployedSetOnTM601': seton601[0] if seton601 else None},
 'develZeroWrite': devel,
 'eightDisciplineAudit': [],   # filled below
 'findings': findings,
 'acceptanceResults': acceptance,
 'commandsRun': [],
 'limitations': [
  'compilation success is not electrical correctness: this verification contains no instrument, hardware or silicon data; no SMU run was performed',
  'the deployed file was writable by other members during this run; every hash here is valid only at its measurement instant',
  'the contract verify command could not be executed to exit 0 (schema missing, T32-F4) — the report is schema-shaped but unvalidated',
  'gate evidence for the deployed revision is inferred from relay-trace function/rule counts (179/4 vs 182/2) plus mtimes; a re-run against the landed revision is still owed',
  'review t24 was written in Chinese; its verdict and hash citations were read as text and are quoted verbatim',
 ],
}

# ---------------------------------------------------------------- disciplines
disc = [
 {'n': 1, 'name': 'DFT intent traceable', 'command': 'python -X utf8 -c "json.load(open(team/artifacts/<run>/dft-ir.json))" ; python scripts/validate_team_artifact.py dft-ir team/artifacts/<run>/dft-ir.json',
  'exitCode': 0,
  'evidence': ['team/artifacts/%s/dft-ir.json (%d B / %s) items[TM600].symbol=TM600_HS_RDSON, items[TM601].symbol=TM601_LS_RDSON' % (RUN, os.path.getsize(os.path.join(RD, 'dft-ir.json')), sha(os.path.join(RD, 'dft-ir.json'))),
               'OVERVIEW rows 132/133 (limits 11 / 7.5 mΩ), DFT.csv records index 18/19 (10 / 8 mohm retained as registered conflict)',
               'dft-ir.json limitConflictPairs + captainRulings CR-02..CR-06'],
  'status': 'passed'},
 {'n': 2, 'name': 'contract as the single global source', 'command': 'python -X utf8 -c "json.load(open(team/artifacts/<run>/setup-contract.json))"',
  'exitCode': 0,
  'evidence': ['team/artifacts/%s/setup-contract.json (%d B / %s)' % (RUN, os.path.getsize(cs), sha(cs)),
               't24 review cites the same revision (rev 24 = 328805 B) as its authority',
               't29 evidence cites the same contract for the K109/K110 requirement'],
  'status': 'passed'},
 {'n': 3, 'name': 'no self-approval', 'command': 'read team/artifacts/<run>/review/t24-implementation-review.md',
  'exitCode': 0,
  'evidence': ['payload author = ate-implementer; reviewer = rule-reviewer (t24 verdict=pass, 13573 B / %s)' % sha(os.path.join(RD, 'review', 't24-implementation-review.md')),
               'additional independent opinion t25 (15329 B / %s)' % sha(os.path.join(RD, 'review', 't25-independent-opinion.md')),
               'this verification executed by dft-expert (t32) — three distinct identities'],
  'status': 'passed'},
 {'n': 4, 'name': 'backup and before/after hashes complete', 'command': 'python -X utf8 -c "hashlib.sha256(open(backup))"',
  'exitCode': 0,
  'evidence': ['backup backups/test.cpp.before_TM600_TM601.bak = %d B / %s (= pre-change baseline)' % (baseline['sizeBytes'], baseline['sha256']),
               't20-apply-verification.json records before=5c9cb3f9… and after=3dbceb49…',
               't23-apply-result.json / t23-apply-verification.json record 3dbceb49… -> 15c7d2b8…',
               'team/artifacts/%s/implementation-manifest.json (36733 B / %s) carries the hash table' % (RUN, sha(os.path.join(RD, 'implementation-manifest.json')))],
  'status': 'passed'},
 {'n': 5, 'name': 'only permitted trees written', 'command': 'python -X utf8 -c "compare target vs devel hashes"',
  'exitCode': 0,
  'evidence': ['devel/source/StdAfx.h = %s (== target), devel/source/sub.cpp = %s (== target)' % (devel['source/StdAfx.h']['devel'], devel['source/sub.cpp']['devel']),
               'devel/source/test.cpp = 5c9cb3f9339f… = the pre-change baseline (devel never received the change)',
               'this task wrote only team/artifacts/%s/verification-report.json and the t32 evidence files' % RUN],
  'status': 'passed'},
 {'n': 6, 'name': 'gate delta attribution clear', 'command': 'python scripts/run_gates.ps1 (not re-run by t32); read gate-logs-t25 / t25-verify / t28',
  'exitCode': 1,
  'evidence': ['gate-logs-t25/run-gates-stdout.log (18:44:58): relay-trace NEW-RED -> "新增红 1 个（阻塞）" — matches the deployed-tree state (179/4)',
               'gate-logs-t25-verify/run-gates-stdout.log (18:58:58) and gate-logs-t28/run-gates-stdout.log (19:22:25): FULL_EXIT=0, 11 GREEN + cbit KNOWN-RED — but their relay-trace logs show 182/2 with zero TM601 warnings, i.e. a different revision than the deployed one',
               't21-new-red-analysis.md (8695 B / %s) attributes the earlier NEW-RED class' % sha(os.path.join(RD, 't21-new-red-analysis.md'))],
  'status': 'failed', 'note': 'attribution is not clear for the deployed revision: the GREEN logs belong to another revision (T32-F3)'},
 {'n': 7, 'name': 'compile separated from electrical validation', 'command': 'read build/gate artifacts; no instrument invoked',
  'exitCode': 0,
  'evidence': ['build evidence exists under team/artifacts/%s/build-verified/ and gate-logs-t25*/' % RUN,
               'no SMU/hardware/bench data exists anywhere in this run; t29 §7 states "A compile closed loop is not electrical sign-off"',
               'this task performed no build and no hardware access'],
  'status': 'passed'},
 {'n': 8, 'name': 'all evidence under team/artifacts/<run-id>/', 'command': 'python -X utf8 -c "os.listdir(team/artifacts/<run>)"',
  'exitCode': 0,
  'evidence': ['run directory team/artifacts/%s holds the contract, plan, schematic IR, DFT IR, manifest, review/ and the t2x/t29 evidence' % RUN,
               'this task wrote t32-probe-*.py, t32-verify-recompute.py, t32-*-evidence.json and verification-report.json inside that directory only',
               'scripts/ and D:/PROJECT6-DALI/ForCodexDebug were not modified by this task'],
  'status': 'passed'},
]
report['eightDisciplineAudit'] = disc
report['commandsRun'] = [
 {'command': 'python -X utf8 team/artifacts/%s/t32-verify-recompute.py' % RUN, 'status': 'passed', 'exitCode': 0,
  'evidence': 'deployed 469714 B / 15c7d2b8…; baseline 434629 B / 5c9cb3f9… hits 0/0/0; golden 6106 B / 8cdb0be1… 0 hits; devel==target for StdAfx.h/sub.cpp'},
 {'command': 'python -X utf8 team/artifacts/%s/t32-probe-scoped.py' % RUN, 'status': 'passed', 'exitCode': 0,
  'evidence': 'scoped invariants match for payload and for the two deployed function bodies; K109/K110 = 0 in deployed, 1 each in payload'},
 {'command': 'python -X utf8 team/artifacts/%s/t32-probe-disciplines.py' % RUN, 'status': 'passed', 'exitCode': 0,
  'evidence': 'eight-discipline evidence collected (t32-discipline-evidence.json, %d B)' % os.path.getsize(os.path.join(RD, 't32-discipline-evidence.json'))},
 {'command': 'python -X utf8 team/artifacts/%s/t32-probe-identity.py' % RUN, 'status': 'passed', 'exitCode': 0,
  'evidence': 'review cites 444810dd…/dce54185… while deployed is 15c7d2b8… and payload is 73b511b7…; manifest cites 15c7d2b8… but not 73b511b7…'},
 {'command': 'python -X utf8 scripts/validate_team_artifact.py verification-report team/artifacts/%s/verification-report.json' % RUN,
  'status': 'failed', 'exitCode': 1,
  'evidence': 'FileNotFoundError: team/schemas/verification-report.schema.json does not exist (schema missing in this run; T32-F4)'},
]

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('wrote', OUT, os.path.getsize(OUT), 'B')
print('sha256', sha(OUT))
print('verdict', report['verdict'])
print('acceptance:', [(a['status'], a['criterion'][:38]) for a in acceptance])
print('findings:', [(f['id'], f['severity']) for f in findings])
print('disciplines:', [(d['n'], d['status']) for d in disc])
