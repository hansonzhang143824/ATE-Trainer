import sys,io,os,json,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('=== CONTRACT now ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
print('  expert quotes: 354,675 B / 504d21df3594e6f2... / rev 29')
print()
print('=== the decision field + the still-wrong record fields ===')
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        res=e['resolution']
        print('  closedRelayNumbers    =',res.get('closedRelayNumbers'),' <- decision field (gate reads THIS)')
        print('  relayChain            =',json.dumps(res.get('relayChain'),ensure_ascii=False)[:170])
        print('  supersededRelaySet    =',res.get('supersededRelaySet'))
        print('  closedRelayNumbersByRoute present:', 'closedRelayNumbersByRoute' in res)
print('  channelsInScope.BST   =',json.dumps(J['resources'][2].get('channelsInScope',{}).get('BST'),ensure_ascii=False)[:80])
n=J.get('_t30ExpectationNote') or {}
print('  _t30ExpectationNote   =',json.dumps(n,ensure_ascii=False)[:300])