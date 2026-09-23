import sys,io,os,re,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
g=os.path.join(base,'scripts','verify_relay_trace.py')
t=open(g,'rb').read().decode('utf-8-sig',errors='replace')
print('=== verify_relay_trace.py : fabricated-name check + static-power rules ===')
for i,l in enumerate(t.split('\n')):
    if any(k in l for k in ['虚构','无 #define','staticPower','static_power','FR-001','defines','relay_defs','NaN']):
        print('  %4d: %s'%(i+1,l.rstrip()[:140]))