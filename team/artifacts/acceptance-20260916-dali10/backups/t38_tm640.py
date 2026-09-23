import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('=== TM640 body bounds: mine L7503-7589 vs expert L7503-7590 ===')
for ln in (7502,7503,7512,7513,7589,7590,7591):
    s=re.sub(r'//.*$','',L[ln-1])
    print('  L%-5d %-8s %s'%(ln,'COMMENT' if not s.strip() else 'CODE',L[ln-1].strip()[:120]))
print()
print('=== does my body range include L7512? ===')
o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM640_BOOST_HS_OCP('))
depth=0; started=False
for i in range(o,len(L)):
    s=re.sub(r'//.*$','',L[i]); depth+=s.count('{')-s.count('}')
    if '{' in s: started=True
    if started and depth==0: end=i; break
print('  my brace-depth end = L%d ; the closing brace line'%(end+1))
print('  L7512 inside my range?', 7512-1>=o and 7512-1<=end)
print()
print('=== mentions counted over my range vs theirs ===')
mine=[i+1 for i in range(o,end+1) if 'SW12_U1REF_BST_ACM' in L[i]]
print('  my mentions (L%d-%d): %d -> %s'%(o+1,end+1,len(mine),mine))
print('  if the range were L7503-7590 (one more line): %d'%len([i+1 for i in range(7502,7590) if 'SW12_U1REF_BST_ACM' in L[i]]))
print('  L7590 content: %s'%L[7589].strip()[:100])