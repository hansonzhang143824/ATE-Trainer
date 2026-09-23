import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
g=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_relay_trace.py'
t=open(g,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== cap_pin() and fam_intersect() definitions ===')
for i,l in enumerate(t):
    if 'def cap_pin' in l or 'def fam_intersect' in l:
        for j in range(i,min(i+16,len(t))): print('%4d: %s'%(j+1,t[j].rstrip()[:130]))
        print()