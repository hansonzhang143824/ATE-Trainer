import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== A) reconcile the t40 evidence document value ===')
for n in ['t40-tm601-bst-evidence.md','t29-k110-evidence.md','APPLY-TM600-TM601.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-36s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('     t4 measured t40 = 11,691 / de6bb17f...  -> that is post-section-0 (correct)')
print('     my 8,229 / cb322c7e was the PRE-section-0 value (superseded by my own later edit)')
print()
print('=== B) per-function relay counts, BOTH text and executable ===')
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n')
s6=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')][0]
s7=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')][0]
e7=next((i for i in range(s7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
for nm,a,b in (('TM600',s6,s7),('TM601',s7,e7)):
    txt=L[a:b]; exe=[re.sub(r'//.*$','',x) for x in txt]
    print('  %s L%d-%d:'%(nm,a+1,b))
    for k in ['K109_BUSL1_PB0','K110_ACM18_BST','SW12_U1REF_BST_ACM']:
        print('     %-20s text=%d  executable=%d'%(k,sum(x.count(k) for x in txt),sum(x.count(k) for x in exe)))
print()
print('     t4 reported TM600 K109=2 K110=2 -> all-text; executable is 1 each (the SetOn list)')
print('     the 2nd occurrence sits in the per-function justification COMMENT')