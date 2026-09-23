import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\knowledge\sources\cbite-qtmue.md'
print('exists:',os.path.exists(p))
if os.path.exists(p):
    L=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
    print('=== L80-100 (the cited exclusivity block) ===')
    for i in range(79,min(100,len(L))): print('  L%d| %s'%(i+1,L[i].rstrip()[:150]))
print()
print('=== verify K46 / K49 / K110 pin-level claims from the netlist ===')
sch=open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt','rb').read().decode('utf-8-sig',errors='replace').split('\n')
for pat in ['K46','K48','K49','K41','K43']:
    hits=[(i+1,l.strip()) for i,l in enumerate(sch) if pat+'(' in l and ('FH5' in l or 'FL' in l)]
    print('  %s in ch5/FPVIe rows: %d'%(pat,len(hits)))
    for ln,l in hits[:4]: print('      L%d| %s'%(ln,l[:120]))