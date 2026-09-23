import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt'
L=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== cited locators (verify myself) ===')
for n in (42,43,109,110,724,725,174,177):
    if n<=len(L): print('%5d| %s'%(n,L[n-1].strip()[:150]))
print()
print('=== every line mentioning K109 or K110 ===')
for i,l in enumerate(L):
    if re.search(r'\bK109\b|\bK110\b',l): print('%5d| %s'%(i+1,l.strip()[:150]))
print()
print('=== definitions of K109/K110 in StdAfx.h ===')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
for i,l in enumerate(h.split('\n')):
    if re.search(r'#define\s+\S*(109|110)\b',l): print('  %4d| %s'%(i+1,l.strip()[:120]))