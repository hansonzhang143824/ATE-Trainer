import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('=== contract now (t4 measured rev 39 / 377,694 B / 18587b83... @22:10:11) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
for e in J.get('aliasResolution') or []:
    if e.get('alias')=='bst2sw':
        res=e['resolution']
        print('  bst2sw closedRelayNumbers =',res.get('closedRelayNumbers'))
        print('  bst2sw superseded         =',res.get('closedRelayNumbersSuperseded'))
print()
n=os.path.join(d,'review-handoff-note-plan-side.md'); nr=open(n,'rb').read(); t=nr.decode('utf-8-sig')
print('=== t4 note (they say 46,261 B / 6da0109a... @22:18:42) ===')
print('  %d B / %s @%s'%(len(nr),hashlib.sha256(nr).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  stale-directive strings, re-counted:')
for pat in ['RETAIN `K109`/`K110` this round','retain `K109`/`K110` this round','`--check-extra` not to be enabled','keep `--check-extra` disabled','REPLACED by an outright REMOVAL','has since been']:
    print('    %-42s %d'%(pat,t.count(pat)))