# -*- coding: utf-8 -*-
"""t32 probe 3: evidence for the eight review disciplines."""
import os, sys, json, re, hashlib, subprocess, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RD = os.path.join(ROOT, 'team', 'artifacts', RUN)
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"

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

def run(args):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return p.returncode, ((p.stdout or '') + (p.stderr or '')).strip()

ev = {}

# D1 DFT intent traceability
dft = json.loads(rt(os.path.join(RD, 'dft-ir.json')))
syms = {i['tm']: i['symbol'] for i in dft['items'] if i['tm'] in ('TM600', 'TM601')}
ev['D1'] = {'artifact': 'team/artifacts/%s/dft-ir.json' % RUN, 'sha256': sha(os.path.join(RD, 'dft-ir.json')),
            'symbols': syms,
            'dftCsvRecords': {'TM600': 'index 18 (0-based) / csvRecord 19', 'TM601': 'index 19 (0-based) / csvRecord 20'},
            'overviewRows': {'TM600': 'sheet=OVERVIEW!row 132', 'TM601': 'sheet=OVERVIEW!row 133'},
            'limits': {i['tm']: i['limits'] for i in dft['items'] if i['tm'] in ('TM600', 'TM601')}}

# D2 contract as single global source
sc = os.path.join(RD, 'setup-contract.json')
tp = os.path.join(RD, 'test-plan.json')
ev['D2'] = {'contract': {'path': 'team/artifacts/%s/setup-contract.json' % RUN, 'size': os.path.getsize(sc), 'sha256': sha(sc)},
            'plan': {'path': 'team/artifacts/%s/test-plan.json' % RUN, 'size': os.path.getsize(tp), 'sha256': sha(tp)},
            'reviewCitation': {'file': 'team/artifacts/%s/review/t24-implementation-review.md' % RUN,
                               'sha256': sha(os.path.join(RD, 'review', 't24-implementation-review.md')),
                               'citesContractRev': 'rev 24 / 328805 B'}}

# D3 no self-approval
t24 = rt(os.path.join(RD, 'review', 't24-implementation-review.md'))
t25 = rt(os.path.join(RD, 'review', 't25-independent-opinion.md'))
ev['D3'] = {'reviewer': 'rule-reviewer',
            't24': {'path': 'team/artifacts/%s/review/t24-implementation-review.md' % RUN,
                    'sha256': sha(os.path.join(RD, 'review', 't24-implementation-review.md')),
                    'mentionsAuthorSeparation': bool(re.search(r'author|self|independent', t24, re.I)),
                    'verdictLines': [l.strip() for l in t24.splitlines() if re.search(r'verdict|PASS|FAIL|needs_revision', l)][:6]},
            't25': {'path': 'team/artifacts/%s/review/t25-independent-opinion.md' % RUN,
                    'sha256': sha(os.path.join(RD, 'review', 't25-independent-opinion.md'))},
            'implementerRole': 'ate-implementer (payload author)',
            'verifierRole': 'dft-expert (this task, t32)',
            'finding': 'reviewability: rule-reviewer wrote the review; the payload author is ate-implementer; this task is executed by dft-expert — three distinct identities'}

# D4 backups + before/after hashes
bak = os.path.join(RD, 'backups', 'test.cpp.before_TM600_TM601.bak')
ev['D4'] = {'backup': {'path': 'team/artifacts/%s/backups/test.cpp.before_TM600_TM601.bak' % RUN,
                       'size': os.path.getsize(bak), 'sha256': sha(bak)},
            'deployed': {'path': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
                         'size': os.path.getsize(os.path.join(TARGET, 'source', 'test.cpp')),
                         'sha256': sha(os.path.join(TARGET, 'source', 'test.cpp'))},
            'applyRecord': {'path': 'team/artifacts/%s/t20-apply-verification.json' % RUN,
                            'sha256': sha(os.path.join(RD, 't20-apply-verification.json')),
                            'content': json.loads(rt(os.path.join(RD, 't20-apply-verification.json')))},
            'manifest': {'path': 'team/artifacts/%s/implementation-manifest.json' % RUN,
                         'sha256': sha(os.path.join(RD, 'implementation-manifest.json'))}}

# D5 only allowed tree modified
ev['D5'] = {'targetRoot': 'D:/PROJECT6-DALI/ForCodexDebug', 'productionRoot': 'D:/PROJECT6-DALI/devel',
            'hashes': {}}
for rel in (('source', 'test.cpp'), ('source', 'StdAfx.h'), ('source', 'sub.cpp'), ('source', 'Pin_Channel_define.h')):
    a = os.path.join(TARGET, *rel); b = os.path.join('D:/PROJECT6-DALI/devel', *rel)
    ev['D5']['hashes']['/'.join(rel)] = {'target': sha(a), 'devel': sha(b), 'identical': sha(a) == sha(b)}

# D6 gate delta attribution
gl = os.path.join(RD, 'gate-logs-t25-verify')
ev['D6'] = {'gateLogs': [], 't25Final': None}
if os.path.isdir(gl):
    for n in sorted(os.listdir(gl)):
        p = os.path.join(gl, n)
        if os.path.isfile(p):
            ev['D6']['gateLogs'].append({'name': n, 'size': os.path.getsize(p), 'sha256': sha(p)})
tf = os.path.join(gl, 't25-final-verification.md')
if os.path.exists(tf):
    tt = rt(tf)
    ev['D6']['t25Final'] = {'sha256': sha(tf),
                            'summaryLines': [l.strip() for l in tt.splitlines() if re.search(r'FULL_EXIT|GREEN|KNOWN-RED|NEW-RED|verdict|verdicts', l, re.I)][:12]}
ag = os.path.join(RD, 't21-new-red-analysis.md')
if os.path.exists(ag):
    ev['D6']['newRedAnalysis'] = {'path': 'team/artifacts/%s/t21-new-red-analysis.md' % RUN, 'sha256': sha(ag)}

# D7 compile vs electrical separation
build_logs = []
for d in ('build-verified', 'gate-logs-t25', 'gate-logs-t25-verify', 'gate-logs-t28'):
    p = os.path.join(RD, d)
    if os.path.isdir(p):
        for n in sorted(os.listdir(p)):
            fp = os.path.join(p, n)
            if os.path.isfile(fp):
                build_logs.append({'path': 'team/artifacts/%s/%s/%s' % (RUN, d, n), 'size': os.path.getsize(fp)})
ev['D7'] = {'buildEvidence': build_logs[:20],
            'separationStatement': 'build/compile evidence only; no instrument or hardware run by this task or by the implementation tasks',
            'noHardwareRun': 'no SMU/instrument access was used; the run has no electrical data'}

# D8 all evidence under artifacts/<run-id>/
top = sorted(os.listdir(RD))
ev['D8'] = {'runDir': 'team/artifacts/%s' % RUN, 'fileCount': sum(1 for n in top if os.path.isfile(os.path.join(RD, n))),
            'sampleEvidenceFiles': [n for n in top if re.match(r'(t2[0-9]|t29|APPLY|HASH|RUN-LEDGER|review)', n)][:12],
            'writesOutsideRunDirByThisTask': 'none'}

out = os.path.join(RD, 't32-discipline-evidence.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(ev, f, ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: (list(v.keys()) if isinstance(v, dict) else v) for k, v in ev.items()}, ensure_ascii=False, indent=1)[:1800])
print('\nwrote', out, os.path.getsize(out))
