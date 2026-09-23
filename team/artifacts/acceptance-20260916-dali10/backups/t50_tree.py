import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
tp=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
r=open(tp,'rb').read()
print('=== FACT: the TARGET TREE right now ===')
print('  %d B / %s  @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(tp).st_mtime))))
print('  my recorded pre-existing value was 469,714 B / 15c7d2b8... (t23)')
t=r.decode('utf-8-sig'); L=t.split('\n')
print()
print('=== FACT: does the deployed TM600 now close K48/K76? ===')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
for i in range(t6,t7):
    if 'cbite.SetOn(' in L[i]: print('  L%-5d %s'%(i+1,L[i].strip()[:175]))
print('  TM600 body: K109=%d K110=%d K48=%d K76=%d'%(
 sum(L[i].count('K109') for i in range(t6,t7)),sum(L[i].count('K110') for i in range(t6,t7)),
 sum(L[i].count('K48') for i in range(t6,t7)),sum(L[i].count('K76') for i in range(t6,t7))))
print()
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
import json
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('=== FACT: contract on disk ===')
print('  revision:',J.get('revision'))
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        print('  aliasResolution[%d].closedRelayNumbers=%s'%(i,e['resolution'].get('closedRelayNumbers')))
        print('  usedByTm=%s'%json.dumps(e.get('usedByTm'),ensure_ascii=False))