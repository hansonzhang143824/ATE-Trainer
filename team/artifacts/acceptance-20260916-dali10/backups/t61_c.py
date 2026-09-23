import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('=== contract now (they cite rev 36 / 376,308 B / d9ecffb0... @21:49:39) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        res=e['resolution']
        print('  bst2sw:')
        print('     closedRelayNumbers          =',res.get('closedRelayNumbers'))
        print('     closedRelayNumbersSuperseded=',res.get('closedRelayNumbersSuperseded'))
        print('     usedByTm                    =',json.dumps(e.get('usedByTm'),ensure_ascii=False))