import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
cands=[r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt',
       r'D:\PROJECT6-DALI\ForCodexDebug\project\DALI\SCH-Connect-Map.txt',
       r'D:\PROJECT6-DALI\ForCodexDebug\SCH-Connect-Map.txt']
for c in cands:
    print(('EXISTS ' if os.path.exists(c) else 'absent '),c)
p=cands[0]
if os.path.exists(p):
    L=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
    print()
    print('=== L670-675 of the workspace connect map ===')
    for i in range(669,675):
        if i<len(L): print('  L%d| %s'%(i+1,L[i].rstrip()[:150]))
    print()
    print('=== any FH5 / K48 / K76 lines (the pin-5 path) ===')
    for i,l in enumerate(L):
        if ('FH5' in l or 'K48' in l or 'K76' in l) and i<1200:
            print('  L%d| %s'%(i+1,l.strip()[:150]))