import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
c=os.path.join(d,'setup-contract.json'); r=open(c,'rb').read()
print('live setup-contract.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
J=json.loads(r.decode('utf-8-sig'))
tm=J['tmDeltas']['TM600']
print()
print('=== tmDeltas.TM600.relaySet ===', json.dumps(tm.get('relaySet'),ensure_ascii=False)[:300])
# aliasResolution for TM600
ar=J.get('aliasResolution')
if isinstance(ar,list):
    for e in ar:
        s=json.dumps(e,ensure_ascii=False)
        if 'TM600' in s and 'closedRelayNumbers' in s:
            print('=== aliasResolution entry ===', s[:400]); break
elif isinstance(ar,dict):
    print('aliasResolution keys:',list(ar)[:8])
# pinRouteTable BST route
prt=J.get('pinRouteTable')
def find_needs(o,path=''):
    out=[]
    if isinstance(o,dict):
        if 'needsClosed' in o: out.append((path,o.get('needsClosed'),o.get('pin') or o.get('node')))
        for k,v in o.items(): out+=find_needs(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): out+=find_needs(v,path+'[%d]'%i)
    return out
hits=[x for x in find_needs(prt) if 'BST' in str(x).upper()]
print()
print('=== pinRouteTable entries mentioning BST ===')
for p,n,pin in hits[:10]: print('  %-46s needsClosed=%s pin=%s'%(p,n,pin))