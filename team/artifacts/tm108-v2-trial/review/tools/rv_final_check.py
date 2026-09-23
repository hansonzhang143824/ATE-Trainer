import json,hashlib,os,time
R=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
j=os.path.join(R,'t8-review-findings.json'); m=os.path.join(R,'t8-review-findings.md')
d=json.loads(open(j,'rb').read().decode('utf-8'))
req=['runId','reviewedInputs','applicableRules','phaseTrace','findings','gateResults','waivedFindings','reviewStatus','residualRisks']
print('JSON OK  missing=%s  status=%s' % ([k for k in req if k not in d], d['reviewStatus']))
print('  outputs: json %d B / md %d B' % (os.path.getsize(j), os.path.getsize(m)))
for f in d['findings']:
    print('   %-6s %-8s %-22s blocking=%s' % (f['id'], f['severity'], f['responsibleOwner'], f.get('blocking')))
print('  gates: FAIL=%d PASS=%d NOTVERIFIED=%d' % (
  sum(1 for g in d['gateResults'] if g['status']=='FAIL'),
  sum(1 for g in d['gateResults'] if g['status']=='PASS'),
  sum(1 for g in d['gateResults'] if g['status'].startswith('NOT'))))
print()
print('=== state of the drifted artifacts at THIS instant ===')
for p in [r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\implementation-manifest.json',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md',
          os.path.join(R,'copy','test.cpp'), os.path.join(R,'copy','test.cpp.r2-live')]:
    b=open(p,'rb').read()
    print('  %-34s %8d %s  mtime=%s' % (os.path.basename(p), len(b), hashlib.sha256(b).hexdigest()[:20],
          time.strftime('%H:%M:%S', time.localtime(os.stat(p).st_mtime))))
