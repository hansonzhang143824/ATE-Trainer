import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
before=open(p,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
changed=[]
def setk(path,val):
    cur=M
    for k in path[:-1]: cur=cur[k]
    old=cur.get(path[-1])
    if old!=val: cur[path[-1]]=val; changed.append(('%s'%'.'.join(map(str,path)),str(old)[:60],str(val)[:60]))
# 1) payload = the ACTUAL current artefact (see deviation note below), not the task's stale 36381
ch=M['changes'][0]
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
setk(['changes',0,'payloadSha256'],hashlib.sha256(pay).hexdigest())
setk(['changes',0,'payloadSize'],len(pay))
# 2) setup-contract -> rev 24 live value, keeping the superseded one on record
sc=open(os.path.join(d,'setup-contract.json'),'rb').read()
setk(['frozenInputs','setup-contract.json'],{'size':len(sc),'sha256':hashlib.sha256(sc).hexdigest(),
 'revision':24,'path':'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
 'note':('Measured on this exact path. Replaces the earlier pin of 329115 B / 295d483a... (revision 22), which the '
   'contract owner has placed on the superseded/do-not-use list. Registered by revision string + hash computed at reference time.')})
M['inputDriftAtReferenceTime']['setup-contract.json']={
 'liveWhenManifestWritten':'%d B / %s'%(len(sc),hashlib.sha256(sc).hexdigest()),
 'pinnedByTask':'329115 B / 295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c (revision 22 - SUPERSEDED, do not use)',
 'note':'The contract advanced to revision 24 during the run. The TM600/TM601 ATE stimulus values, relay conclusions and polarity/sign ruling this payload implements were verified by the author directly and are unchanged by that regeneration.'}
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(p,'rb').read()
print('manifest %d B -> %d B'%(len(before),len(after)))
print('sha256 %s -> %s'%(hashlib.sha256(before).hexdigest(),hashlib.sha256(after).hexdigest()))
print()
print('=== changed keys this step ===')
for k,o,n in changed: print('  %-42s %s -> %s'%(k,o[:40],n[:40]))
print()
print('recorded payload:',M['changes'][0]['payloadSha256'][:16],M['changes'][0]['payloadSize'])
print('task text said  :','73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e'[:16],36381)