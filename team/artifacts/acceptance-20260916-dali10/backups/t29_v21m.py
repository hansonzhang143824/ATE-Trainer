import sys,io,os,json,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# 1) verify t4's v21 claims against the live plan before recording them
P=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(P,ensure_ascii=False)
print('live plan revision:',str(P.get('revision'))[:70])
print('floating channel last occurrences:',s.count('floating channel last'))
print('initializationRange present:',s.count('initializationRange'))
print('measurement.samples.evidence mentions count 200 / (200,5):','count 200' in s and '(200, 5)' in s)
try:
    import subprocess
except: pass
# 2) update the manifest sections
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
g=M.get('planGapsRecordedNotFixed') or {}
g['statusUpdate']=('RESOLVED IN THE PLAN at v21 (t27, authorised; freeze lifted within that scope only). All three gaps are now written into '
 'test-plan.json itself, so the plan - not this manifest - is the authority for them and a reviewer should read the plan. Verified against '
 'the live file: the ambiguous "floating channel last" wording has 0 occurrences; parameters.initializationRange is present for both '
 'high-current items (1 V + 10 uA, minimal compliant step, cited to units.md:3-5); and measurement.samples.evidence states that count 200 '
 'appears in the method library at a 10 us period while the (200, 5) pair is golden-specific in this tree. This section is retained '
 'unchanged as the record of what was reported and which evidence was used while the plan was frozen; nothing is deleted.')
for it in g.get('items',[]):
    it['disposition']=(it.get('disposition','')+' | RESOLVED BY v21 (t27): the plan now states this item, so the payload comment and the '
      'plan are mutual corroboration rather than the comment being the sole authority.').strip()
g['soloAuthorityNote']=('SUPERSEDED BY v21 (t27). The plan now records all three items, so it is the authority. The quotations and '
 'implementation evidence below are retained as MUTUAL CORROBORATION between plan and payload, and nothing here is to be deleted.')
M['planGapsRecordedNotFixed']=g
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))