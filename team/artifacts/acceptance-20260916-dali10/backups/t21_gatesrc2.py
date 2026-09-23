import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
g=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_relay_trace.py'
t=open(g,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== lines 265-335 (cap family + static power rule) ===')
for i in range(264,335):
    if i<len(t): print('%4d: %s'%(i+1,t[i].rstrip()[:150]))