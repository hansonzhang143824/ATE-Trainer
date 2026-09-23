import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
t6=J['tmDeltas']['TM601']
print('=== TM601 pinRouteTable: every route and its needsClosed (does any need 109/110?) ===')
def walk(o,path=''):
    if isinstance(o,dict):
        if 'needsClosed' in o: print('  %-58s %s'%(path[-58:],o['needsClosed']))
        for k,v in o.items(): walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
walk(t6.get('pinRouteTable') or {})
print()
print('=== TM600 pinRouteTable routes needing 109/110 ===')
t6d=J['tmDeltas']['TM600']
def walk2(o,path=''):
    if isinstance(o,dict):
        if 'needsClosed' in o and (109 in o['needsClosed'] or 110 in o['needsClosed']):
            print('  %-58s %s'%(path[-58:],o['needsClosed']))
        for k,v in o.items(): walk2(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk2(v,path+'[%d]'%i)
walk2(t6d.get('pinRouteTable') or {})
print()
print('=== minimal-endpoint discipline: my payload SetOn vs contract authority ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
for l in code:
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:210])
print()
print('  TM600 relaySet has 109:',109 in t6d.get('relaySet',[]),' 110:',110 in t6d.get('relaySet',[]))
print('  TM601 relaySet has 109:',109 in t6.get('relaySet',[]),' 110:',110 in t6.get('relaySet',[]))
print()
print('=== negative-list relays must stay un-SetOn: are any 87/88/89/131/132/133 in either SetOn? ===')
s=' '.join(code)
for r in ['K87','K88','K89','K131','K132','K133']:
    print('  %-6s in executable SetOn text: %s'%(r, r in s))