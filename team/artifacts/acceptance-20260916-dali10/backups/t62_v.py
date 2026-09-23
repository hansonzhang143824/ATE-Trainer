import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) their note hash (they say 37,652 B / 09e310ef... @22:03:05) ===')
p=os.path.join(d,'review-handoff-note-plan-side.md')
if os.path.exists(p):
    r=open(p,'rb').read()
    print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print('=== 2) their table says K48_ACM5_AMP_REF+K76_ACM_BST "各 2" for TM607/608/609/640; I measured 1 each ===')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    dd=0; st=False
    for i in range(o,len(L)):
        s=re.sub(r'//.*$','',L[i]); dd+=s.count('{')-s.count('}')
        if '{' in s: st=True
        if st and dd==0: return o,i
for n in ['TM607_BUCK_LS_ZCD','TM640_BOOST_HS_OCP']:
    o,j=body(n); st=[re.sub(r'//.*$','',x) for x in L[o:j+1]]
    lines48=[o+1+k for k,x in enumerate(st) if 'K48' in x]
    lines76=[o+1+k for k,x in enumerate(st) if 'K76' in x]
    print('  %-24s K48: %d line(s) at %s | K76: %d line(s) at %s'%(n,len(lines48),lines48,len(lines76),lines76))
    for ln in lines48: print('      L%d: %s'%(ln,L[ln-1].strip()[:120]))
print()
print('  => token count vs line count: same lines may mention more than once.')