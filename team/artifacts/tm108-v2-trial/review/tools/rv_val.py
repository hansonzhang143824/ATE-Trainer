import json, hashlib, os
p = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json'
raw = open(p,'rb').read()
d = json.loads(raw.decode('utf-8'))
req = ['runId','reviewedInputs','applicableRules','phaseTrace','findings','gateResults','waivedFindings','reviewStatus','residualRisks']
print('JSON parses OK. bytes=%d sha256=%s' % (len(raw), hashlib.sha256(raw).hexdigest()))
print('missing charter fields:', [k for k in req if k not in d])
print('runId =', d['runId'], '| reviewStatus =', d['reviewStatus'])
print('reviewedInputs =', len(d['reviewedInputs']), 'applicableRules =', len(d['applicableRules']),
      'phaseTrace =', len(d['phaseTrace']), 'findings =', len(d['findings']),
      'gateResults =', len(d['gateResults']), 'waivedFindings =', len(d['waivedFindings']),
      'residualRisks =', len(d['residualRisks']))
freq = ['id','severity','TM','category','evidence','violatedRule','responsibleOwner','repairCondition']
for f in d['findings']:
    miss = [k for k in freq if k not in f]
    print('  finding %-6s severity=%-8s owner=%-22s missingFields=%s' % (f['id'], f['severity'], f['responsibleOwner'], miss))
gr = {}
for g in d['gateResults']:
    gr[g['status']] = gr.get(g['status'],0)+1
print('  gateResults statuses:', gr)
print('  checkItemsAnswered keys:', sorted(d['checkItemsAnswered'].keys()))
print('  all inputs have plaintext hash + stability flag:',
      all('sha256_plaintext' in i and i.get('hashStableAcrossReview') is True for i in d['reviewedInputs']))
