import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('=== 1) the add-only note the expert found ===')
def walk(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and ('add-only' in v or 'add only' in v.lower()):
                print('  %s/%s = %s'%(path,k,v[:220]))
            walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
walk(J)
print()
print('=== 2) does closedRelayNumbersByRoute exist? (affects whether option 乙 is even open) ===')
s=json.dumps(J,ensure_ascii=False)
for k in ['closedRelayNumbersByRoute','closedRelayNumbers','BST_routes','supersededRelaySet']:
    print('  %-26s %d'%(k,s.count(k)))
print()
print('=== 3) WHICH SCRIPTS consume closedRelayNumbers? (the fix target list) ===')
base=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts'
for f in sorted(os.listdir(base)):
    if not f.endswith('.py'): continue
    t=open(os.path.join(base,f),encoding='utf-8-sig',errors='replace').read().split('\n')
    hits=[(i+1,l.strip()) for i,l in enumerate(t) if 'closedRelayNumbers' in l]
    if hits:
        print('  %-32s %d refs'%(f,len(hits)))
        for ln,l in hits[:4]: print('      L%-4d %s'%(ln,l[:120]))