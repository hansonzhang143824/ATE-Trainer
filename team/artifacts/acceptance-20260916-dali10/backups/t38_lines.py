import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('=== the lines they cite for the leg closure ===')
for ln in (7513,7623,7734,7500):
    print('  L%d| %s'%(ln,L[ln-1].strip()[:150]))
print()
print('=== what is at L7623 / L7734 in MY read? (owners) ===')
for ln in (7623,7734):
    o=next((k for k in reversed(range(ln)) if L[k].startswith('DUT_API int ')),None)
    print('  L%d owner by nearest-preceding DUT_API: %s (L%d)'%(ln,L[o].split('(')[0].replace('DUT_API int ','') if o else '?',o+1 if o else 0))
print()
print('=== do those functions close the leg via the COMPOSITE macro? ===')
for f in ['TM641_BST_UV','TM643_VBAT_LOOP_INDICTOR']:
    tot=0
    for i,l in enumerate(L):
        if l.startswith('DUT_API int '+f+'('):
            depth=0; started=False
            for k in range(i,len(L)):
                s=re.sub(r'//.*$','',L[k]); depth+=s.count('{')-s.count('}') 
                if '{' in s: started=True
                if started and depth==0: break
            blk=L[i:k+1]
            for x in blk:
                if 'K_FPVIH_TO_BST_A' in x and 'SetOn' in x: print('  %s L%d: %s'%(f,k+1 if False else L.index(x)+1,x.strip()[:140]))
            # count composite
            comp=sum(1 for x in blk if 'K_FPVIH_TO_BST_A' in x)
            print('  %-28s composite K_FPVIH_TO_BST_A occurrences in body: %d'%(f,comp)); break