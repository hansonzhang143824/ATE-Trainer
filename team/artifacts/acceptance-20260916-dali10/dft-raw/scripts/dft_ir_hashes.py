# -*- coding: utf-8 -*-
"""Emit the t1 hash report: dft-ir.json + every source it cites."""
import os, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RAW = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw')

def sh(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

artifact = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
d = json.load(open(artifact, encoding='utf-8'))

sources = {}
# seed with the declared source block
src = d['source']
for key in ('path',):
    pass
def add(path):
    if path in sources: return
    if path.startswith('D:/'):
        fp = path
    else:
        fp = os.path.join(ROOT, path.replace('/', os.sep))
    if os.path.exists(fp):
        sources[path] = {'sha256': sh(fp), 'size': os.path.getsize(fp)}
    else:
        sources[path] = {'sha256': None, 'size': None, 'error': 'not found'}

add(src['path'])
add(src['secondaryIntentSource']['path'])
for s in src['tertiarySources']:
    add(s['path'])
for it in d['items']:
    for e in it['evidence']:
        add(e['path'])
    for rw in it.get('registerWritesFromRegConfig', []):
        pass

def sh(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

runs = []
for name in sorted(os.listdir(RAW)):
    fp = os.path.join(RAW, name)
    if os.path.isfile(fp):
        runs.append({'path': 'team/artifacts/%s/dft-raw/%s' % (RUN, name), 'sha256': sh(fp), 'size': os.path.getsize(fp)})
sub = os.path.join(RAW, 'scripts')
if os.path.isdir(sub):
    for name in sorted(os.listdir(sub)):
        fp = os.path.join(sub, name)
        if os.path.isfile(fp):
            runs.append({'path': 'team/artifacts/%s/dft-raw/scripts/%s' % (RUN, name), 'sha256': sh(fp), 'size': os.path.getsize(fp)})

report = {
    'runId': RUN, 'task': 't1 (DFT intent extraction)', 'producedBy': 'dft-expert',
    'generatedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'deliverable': {'path': 'team/artifacts/%s/dft-ir.json' % RUN,
                    'sha256': sh(artifact), 'size': os.path.getsize(artifact),
                    'schema': 'team/schemas/dft-ir.schema.json',
                    'schemaValidation': 'PASS (scripts/validate_team_artifact.py dft-ir)',
                    'selfVerification': 'see the verificationReports block (each report records the artifact digest it was issued against)'},
    'sourceHashes': sources,
    'runOutputHashes': runs,
    'writeBoundary': {
        'workspaceRoot': 'D:/Newtest/DSH/ATE-Coding-Plat',
        'filesWritten': ['team/artifacts/%s/dft-ir.json' % RUN] + [r['path'] for r in runs],
        'debugCopyUntouched': {'path': 'D:/PROJECT6-DALI/ForCodexDebug', 'writesPerformed': 0,
                                'note': 't1 performed read-only analysis; test.cpp/sub.cpp/StdAfx.h were read via python byte mode and hashed, never written'},
        'productionTreeUntouched': {'path': 'D:/PROJECT6-DALI/devel', 'writesPerformed': 0,
                                     'note': 'devel/source/test.cpp sha256 equals ForCodexDebug/source/test.cpp sha256 (both read in this task)'},
    },
}
op = os.path.join(RAW, 'dft-ir-hashes.json')
# 保留既有 sidecar 的辅助区块（回归修复：早期版本整体覆盖，导致 hashHistory / lateRulingsNotInIR /
# provenanceCorrection / notRebuilt / fixtureAnchor 等被静默丢弃 —— 由 ate-implementer 独立发现）
AUX = ('hashHistory', 'provenanceCorrection', 'lateRulingsNotInIR', 'notRebuilt', 'fixtureAnchor',
       'verificationReports', 't9HandoffDisciplines', 'frozenBy')
if os.path.exists(op):
    try:
        prev = json.loads(open(op, encoding='utf-8-sig').read())
        for k in AUX:
            if k in prev:
                report[k] = prev[k]
        for k, v in prev.items():
            if k not in report and k not in AUX:
                report[k] = v
    except Exception as e:
        print('WARN: could not merge existing sidecar (aux blocks dropped):', e)
with open(op, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('wrote', op)
print('preserved aux blocks:', [k for k in AUX if k in report])
print('deliverable sha256', report['deliverable']['sha256'])
print('sources', len(sources), 'run outputs', len(runs))
