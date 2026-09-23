import sys,io,os,hashlib,time,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('=== contract now (captain cites 355,658 B / 4a45f734... / rev 29) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        res=e['resolution']
        print('  closedRelayNumbers   =',res.get('closedRelayNumbers'))
        print('  relayChain (now ch5?) =',json.dumps(res.get('relayChain'),ensure_ascii=False)[:190])
        print('  relayChainSuperseded present:', 'relayChainSuperseded' in res)
pi=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
pr=open(pi,'rb').read()
print()
print('=== payload (must stay frozen) ===')
print('  %d B / %s'%(len(pr),hashlib.sha256(pr).hexdigest()))
print('  frozen 66abc088... -> MATCH:',hashlib.sha256(pr).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')