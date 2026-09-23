import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n')
s6=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')][0]
s7=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')][0]
e7=next((i for i in range(s7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
def strip(x): return re.sub(r'//.*$','',x)
print('=== TWO DIFFERENT DEFINITIONS, same numbers (a coincidence worth flagging) ===')
for nm,a,b in (('TM600',s6,s7),('TM601',s7,e7)):
    blk=L[a:b]
    stripblk=[strip(x) for x in blk]
    d_mentions=sum(x.count('SW12_U1REF_BST_ACM') for x in stripblk)      # t4's definition
    d_sets=sum(1 for x in stripblk if 'SW12_U1REF_BST_ACM.Set' in x)      # my definition
    unstripped=sum(x.count('SW12_U1REF_BST_ACM') for x in blk)
    print('  %s: t4-def (mentions in stripped code) = %d | my-def (.Set lines in stripped code) = %d | unstripped mentions = %d'%(nm,d_mentions,d_sets,unstripped))
print()
print('  => both definitions yield 10/0 HERE, but they are not the same measure:')
print('     a comment mentioning the instrument, or a non-.Set reference, would move the counts apart.')
print()
print('=== manifest current value (t4 says 48,277) ===')
p=os.path.join(d,'implementation-manifest.json'); r=open(p,'rb').read()
print('  now: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))