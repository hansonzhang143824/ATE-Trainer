import sys,io,os,re,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mine=['t5-input-confirmation.md','implementation-manifest.json','APPLY-TM600-TM601.md','t21-new-red-analysis.md','t21-tm601-fr001-exception.md','t23-amendment-evidence.md','HASH-AUDIT.md','implementation-payload-TM600-TM601.cpp','implementer-t5-prep.md']
print('=== audit MY artefacts for references to the deleted variant or stale values ===')
for n in mine:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('  %-46s (absent)'%n); continue
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    hits=[]
    for pat in ['pulse2ms-variant','pulse2ms','3e439b17','2b48bc0e','8d9c1d84','342651a7','5911 B','ad9859e9','161516','0578bd5e']:
        if pat in t: hits.append(pat)
    print('  %-46s %s'%(n, hits if hits else 'clean'))
print()
print('=== t13-task-contract.md (not mine) ===')
p=os.path.join(d,'t13-task-contract.md')
if os.path.exists(p):
    L=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
    for i,l in enumerate(L):
        if 'variant' in l.lower() or 'pulse2ms' in l: print('  %4d| %s'%(i+1,l.strip()[:130]))
else: print('  absent')