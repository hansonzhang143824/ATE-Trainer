import json,hashlib,os
R=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
j=os.path.join(R,'t8-review-findings.json'); m=os.path.join(R,'t8-review-findings.md')
d=json.loads(open(j,'rb').read().decode('utf-8'))
print('JSON OK  sha256=%s bytes=%d' % (hashlib.sha256(open(j,'rb').read()).hexdigest(), os.path.getsize(j)))
print('  reviewStatus=%s  findings=%d  blocking=%s  inputs=%d  risks=%d' % (
  d['reviewStatus'], len(d['findings']),
  [f['id'] for f in d['findings'] if f.get('blocking')], len(d['reviewedInputs']), len(d['residualRisks'])))
print('  RF-01 owner=%s severity=%s' % ([f['responsibleOwner'] for f in d['findings'] if f['id']=='RF-01'][0],
                                        [f['severity'] for f in d['findings'] if f['id']=='RF-01'][0]))
t=open(m,'rb').read().decode('utf-8')
print('MD   sha256=%s bytes=%d lines=%d' % (hashlib.sha256(open(m,'rb').read()).hexdigest(), os.path.getsize(m), t.count(chr(10))+1))
i_c11=t.index('### C11 '); i_add=t.index('#### C11 addendum'); i_c12=t.index('### C12 ')
print('  C11 heading at %d < addendum at %d < C12 heading at %d  -> ordering OK: %s' % (i_c11,i_add,i_c12, i_c11<i_add<i_c12))
print('  scope-correction note before the summary table:', t.index('Scope correction applied') < t.index('## 1. Independence'))
print()
print('=== FINAL read-only snapshot (plaintext, python byte mode) ===')
for p in [r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp',
          r'D:\PROJECT6-DALI\ForCodexDebug\source\sub.cpp',
          r'D:\PROJECT6-DALI\ForCodexDebug\source\BoardCheck.h',
          r'D:\PROJECT6-DALI\ForCodexDebug\source\treg.h',
          r'D:\PROJECT6-DALI\ForCodexDebug\source\src\treg.h',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\implementation-manifest.json',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md']:
    b=open(p,'rb').read()
    print('  %-46s %8d %s' % (os.path.basename(p), len(b), hashlib.sha256(b).hexdigest()[:32]))
