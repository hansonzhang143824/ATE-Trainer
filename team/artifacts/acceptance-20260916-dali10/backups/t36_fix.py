import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
# replace the two truncated hashes with the real measured values
fix={}
for a in M['gateAndGenerationEvidence']['artefacts']:
    q=os.path.join(r'D:\Newtest\DSH\ATE-Coding-Plat',a['path'].replace('/',os.sep))
    if os.path.exists(q):
        rr=open(q,'rb').read(); real=hashlib.sha256(rr).hexdigest()
        if a['sha256']!=real: fix[a['path']]=(a['sha256'],real); a['sha256']=real; a['size']=len(rr)
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('corrected truncated hashes:',fix if fix else 'none')
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))
M2=json.loads(r.decode('utf-8'))
print()
print('=== final alignment check ===')
print('  status                 :',str(M2['status'])[:80])
print('  payload                :',M2['changes'][0]['payloadSize'],M2['changes'][0]['payloadSha256'][:16])
print('  after                  :',M2['changes'][0]['afterSize'],M2['changes'][0]['afterSha256'][:16],'| pending flag:',M2['changes'][0]['afterSha256IsPending'])
print('  test-plan (v21)        :',M2['frozenInputs']['test-plan.json']['revision'][:20],M2['frozenInputs']['test-plan.json']['sha256'][:16])
print('  setup-contract rev     :',M2['frozenInputs']['setup-contract.json']['revision'],M2['frozenInputs']['setup-contract.json']['sha256'][:16])
print('  planGap dispositions   :',[i['disposition'][:34] for i in M2['planGapsRecordedNotFixed']['items']])
print('  soloAuthorityNote      :',M2['planGapsRecordedNotFixed']['soloAuthorityNote'][:60])
print('  t24 / t29              :',M2['reviewStatus']['t24']['status'][:40],'/',M2['reviewStatus']['t29']['status'][:30])
print('  buildReport            :',M2['buildReport']['status'])
print('  t28 evidence artefacts :',len(M2['gateAndGenerationEvidence']['artefacts']))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('  target unchanged by me :',hashlib.sha256(s).hexdigest()=='15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a')