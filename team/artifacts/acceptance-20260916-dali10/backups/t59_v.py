import sys,io,os,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) my landingGate: they think it says "BLOCKED pending t43" ===')
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
g=M['handoffCitationRisk']['landingGate']
print('  status :',g['status'])
print('  gates  :',g['gates'][:150])
print('  history:',g['gateHistoryNote'][:140])
print()
print('=== 2) the intersection vs removal: what does the FROZEN payload actually contain? ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); import re
code=re.sub(r'//.*$','',r.decode('utf-8-sig'),flags=re.M)
print('  payload %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  executable K48=%d K76=%d | K109=%d K110=%d | K46=%d'%(
 code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST'),code.count('K46')))
print('  => the union is NOT present: K109/K110 are ABSENT. The intersection directive was replaced by removal.')
print()
print('=== 3) --check-extra polarity in the payload ===')
u=r.decode('utf-8-sig')
for i,l in enumerate(u.split('\r\n')):
    if 'check-extra' in l: print('  L%d: %s'%(i+1,l.strip()[:130]))
print()
print('=== 4) contract revision now ===')
C=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('  revision:',C.get('revision'),'| closedRelayNumbers:',
      [e['resolution'].get('closedRelayNumbers') for e in C['aliasResolution'] if e.get('alias')=='bst2sw'])