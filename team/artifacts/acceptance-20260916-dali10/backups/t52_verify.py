import sys,io,os,json,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read()
print('=== CANONICAL VERIFICATION (read-only; no writes this turn) ===')
print('  payload: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  captain canon: 41,797 B / 6034af710a348e578099886737cc7cc086c8297808189cfa283ad8ce4ec7c4fa @20:48:18')
print('  MATCH:', hashlib.sha256(r).hexdigest()=='6034af710a348e578099886737cc7cc086c8297808189cfa283ad8ce4ec7c4fa')
u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
L=u.split('\n')
t6=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')][0]
t7=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')][0]
seg=code.split('\n')[t6:t7]
print()
print('=== the captain\'s own assertions re-checked ===')
print('  TM600 SetOn calls: %d'%sum(1 for l in seg if 'cbite.SetOn(' in l))
for l in seg:
    if 'cbite.SetOn(' in l:
        items=[x.strip() for x in l.split('SetOn(')[1].rstrip(');').split(',')]
        print('    L%d: %d items -> %s'%(L.index([x for x in L if l in x][0])+1,len(items),[i for i in items if i][:12]))
print('  executable K46: %d'%sum(l.count('K46') for l in code.split('\n')))
print('  --check-extra annotation: %d'%u.count('--check-extra'))
print('  executable K48/K76/K109/K110: %d/%d/%d/%d'%(sum(l.count('K48_ACM5_AMP_REF') for l in code.split('\n')),sum(l.count('K76_ACM_BST') for l in code.split('\n')),sum(l.count('K109_BUSL1_PB0') for l in code.split('\n')),sum(l.count('K110_ACM18_BST') for l in code.split('\n'))))
print('  executable SW12 in TM600: %d'%sum(l.count('SW12_U1REF_BST_ACM') for l in code.split('\n')[t6:t7]))
print('  executable SW12 in TM601: %d'%sum(l.count('SW12_U1REF_BST_ACM') for l in code.split('\n')[t7:]))
print()
m=os.path.join(d,'implementation-manifest.json'); rm=open(m,'rb').read(); M=json.loads(rm.decode('utf-8-sig'))
print('=== my manifest state ===')
print('  %d B / %s'%(len(rm),hashlib.sha256(rm).hexdigest()))
vc=M['handoffCitationRisk']['landingGate']['verifiedCounts']
print('  verifiedCounts.payloadSha256 matches canonical:', vc.get('payloadSha256')=='6034af710a348e578099886737cc7cc086c8297808189cfa283ad8ce4ec7c4fa')
print('  GATE CLOSED:', 'GATE CLOSED' in M['handoffCitationRisk']['landingGate']['status'])