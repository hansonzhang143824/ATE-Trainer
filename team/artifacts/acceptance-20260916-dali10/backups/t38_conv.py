import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n')
s6=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')][0]
s7=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')][0]
e7=next((i for i in range(s7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
def acm(a,b):
    # EXACT convention: executable lines only (strip inline comments), substring SW12_U1REF_BST_ACM.Set
    exe=[re.sub(r'//.*$','',x) for x in L[a:b]]
    return sum(1 for x in exe if 'SW12_U1REF_BST_ACM.Set' in x)
print('=== EXACT counting convention, both functions ===')
print('  TM600 (L%d-%d) ACM Sets = %d'%(s6+1,s7,acm(s6,s7)))
print('  TM601 (L%d-%d) ACM Sets = %d'%(s7+1,e7,acm(s7,e7)))
print()
print('  convention = count of executable lines (comments stripped, inline too)')
print('               containing the substring "SW12_U1REF_BST_ACM.Set"')
print('               within the function body delimited by the DUT_API int <name>(... line')
print()
print('=== t4 also asked about PER-FUNCTION JUSTIFICATION text vs executable ===')
print('  all-text = %d ; executable = %d  (correctly 1/0: it is a comment marker)'%(u.count('PER-FUNCTION JUSTIFICATION'),sum(re.sub(r'//.*$','',x).count('PER-FUNCTION JUSTIFICATION') for x in L)))
print()
print('=== current file values (for their freeze decision) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-38s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))