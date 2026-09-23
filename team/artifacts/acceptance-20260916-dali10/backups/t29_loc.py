import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(J,ensure_ascii=False)
print('=== search for closedRelayNumbers / needsClosed / BST routes ===')
def walk(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in ('closedRelayNumbers',):
                print('  %s = %s'%(path+'/'+k,json.dumps(v,ensure_ascii=False)[:120]))
            if k=='needsClosed' and any(x in json.dumps(v) for x in ('109','110')):
                print('  %s = %s   (parent keys: %s)'%(path+'/'+k,json.dumps(v,ensure_ascii=False)[:80],path[-90:]))
            if k=='relayPath' and '110' in json.dumps(v):
                print('  %s = %s'%(path+'/'+k,json.dumps(v,ensure_ascii=False)[:130]))
            walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
walk(J)
print()
print('=== tmDeltas.TM600: which keys exist and what mentions 109/110 ===')
tm=J['tmDeltas']['TM600']
for k,v in tm.items():
    j=json.dumps(v,ensure_ascii=False)
    if '109' in j or '110' in j: print('  %s: %s'%(k,j[:400]))