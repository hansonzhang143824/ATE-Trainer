import sys,io,re,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h'
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
print('=== definitions of K131-K135 (the ch1 BST/SW path) ===')
for i,l in enumerate(t.split('\n')):
    if re.match(r'\s*#define\s+K13[0-5]_',l): print('  ',l.strip()[:110])
print()
print('=== do live TMs drive BST-SW with FPVI1 anywhere? ===')
src=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
s=open(src,'rb').read().decode('utf-8-sig',errors='replace')
print('  FPVI1 occurrences in test.cpp:',s.count('FPVI1'))
for i,l in enumerate(s.split('\n')):
    if 'FPVI1' in l: print('   %d: %s'%(i+1,l.strip()[:110]))