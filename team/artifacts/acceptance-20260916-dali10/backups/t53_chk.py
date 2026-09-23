import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig')
print('=== CURRENT payload on disk (captain quoted 42,998 / c03632d9 @20:59:12) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  captain quotes c03632d9... -> my later authorised write (comment work) superseded it')
print()
# their expected set vs what the payload closes
L=u.split('\r\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
line=next(L[i] for i in range(t6,t7) if 'cbite.SetOn(' in L[i])
items=[x.strip() for x in line.split('SetOn(')[1].rstrip(');').split(',')]
relays=[x for x in items if x and x!='-1']
print('=== SET ARITHMETIC the captain asks me to confirm ===')
print('  payload closes (%d): %s'%(len(relays),relays))
expected_names=['K48_ACM5_AMP_REF','K60_BUSL0_VCP','K61_ACM8_SW','K76_ACM_BST','K83_BUSH0_PMID']
print('  expected set {48,60,61,76,83} = %s'%expected_names)
missing=[e for e in expected_names if e not in relays]
print('  payload CLOSES every expected item:', len(missing)==0, ('missing=%s'%missing) if missing else '(superset confirmed)')
print('  extra closures beyond expectation: %s'%[x for x in relays if x not in expected_names])
print()
print('  => under the t53-narrowed contract (BST [48,76] + SW [60,61] + PMID 83) the gate should be GREEN.')