import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
g=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_relay_trace.py'
t=open(g,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== VERBATIM: the FR-001 reverse rule and its exemption clause (lines 305-330) ===')
for i in range(304,330): print('%4d| %s'%(i+1,t[i].rstrip()))
print()
print('=== how mi_pins is derived (does the force loop count as measured-current path?) ===')
for i,l in enumerate(t):
    if 'mi_current_pins' in l or 'mi_pins' in l:
        print('%4d: %s'%(i+1,l.rstrip()[:130]))