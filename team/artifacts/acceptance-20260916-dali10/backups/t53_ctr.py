import sys,io,os,json,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json')
r=open(p,'rb').read()
print('=== CONTRACT on disk now ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
print()
print('=== their claim: ch5 data ADDED but the wrong field NOT removed ===')
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        res=e.get('resolution') or {}
        print('  aliasResolution[%d] bst2sw:'%i)
        print('     closedRelayNumbers =',res.get('closedRelayNumbers'),'  <- gate feeds on THIS')
        print('     relayChain         =',json.dumps(res.get('relayChain'),ensure_ascii=False)[:150])
        print('     keys present       =',list(res.keys()))
print()
print('=== does channelsInScope.BST still carry the old ch18 value? ===')
s=json.dumps(J,ensure_ascii=False)
for pat in ['S5_ACM200_FH18/SH18 (K110_BST)','acm200_ch5','BST_routes','S5_ACM200_FH5']:
    print('  %-32s occurrences: %d'%(pat,s.count(pat)))
# locate channelsInScope
def find(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='channelsInScope' and isinstance(v,dict):
                print('  channelsInScope at %s: BST=%s'%(path,str(v.get('BST'))[:80]))
                if 'BST_routes' in v: print('      BST_routes=%s'%json.dumps(v.get('BST_routes'),ensure_ascii=False)[:120])
            find(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): find(v,path+'[%d]'%i)
find(J)