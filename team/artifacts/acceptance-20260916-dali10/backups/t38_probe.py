import sys,io,os,re,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig'); L=u.split('\n')
print('payload %d B / %s'%(os.path.getsize(p),hashlib.sha256(open(p,'rb').read()).hexdigest()))
s=[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]
print('TM601 function starts at payload L%d'%(s+1))
print()
print('=== TM601: every executable SW12_U1REF_BST_ACM / Set command ===')
for i in range(s,len(L)):
    l=L[i]
    if l.strip().startswith('//'): continue
    if 'SW12_U1REF_BST_ACM' in l or 'cbite.SetOn' in l:
        print('  L%-4d %s'%(i+1,l.strip()[:150]))
print()
print('=== TM601 vs TM600: do the ACM drives differ? ===')
t6=[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]
for label,start in (('TM600',t6),('TM601',s)):
    acm=[l.strip()[:110] for l in L[start:start+400] if 'SW12_U1REF_BST_ACM.Set' in l]
    print('  %s ACM Sets (%d):'%(label,len(acm)))
    for a in acm[:8]: print('      ',a)