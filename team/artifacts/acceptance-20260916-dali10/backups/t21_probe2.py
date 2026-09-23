import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
print('=== defines for the four caps + K126 ===')
for n in ['K44','K45','K57','K5_','K126','K13','K85']:
    hits=[(i+1,l.strip()) for i,l in enumerate(h.split('\n')) if re.match(r'\s*#define\s+'+n,l)]
    for ln,l in hits[:2]: print('  %-6s StdAfx.h:%d  %s'%(n,ln,l[:110]))
print()
t=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
s=t.find('DUT_API int TM600_HS_RDSON'); e=t.find('DUT_API int',s+10)
b600=t[s:e if e>0 else len(t)]
print('=== TM600 block: which caps does it close? ===')
for l in b600.split('\n'):
    if 'SetOn(' in l or 'Off(' in l: print('  ',l.strip()[:130])
print()
print('=== how do OTHER live functions close K44/K45/K5/K57? (sample) ===')
import re as R
cnt=0
for m in R.finditer(r'cbite\.SetOn\(([^)]*)\)',t):
    args=m.group(1)
    if any(x in args for x in ('K44','K45','K5_VBUS','K57')):
        cnt+=1
        if cnt<=6: print('  ',args[:135])
print('  total SetOn lines mentioning those caps:',cnt)