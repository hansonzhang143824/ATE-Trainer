import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
g=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_relay_trace.py'
t=open(g,'rb').read().decode('utf-8-sig',errors='replace')
for i,l in enumerate(t.split('\n')):
    if any(k in l for k in ['config','cfg','project_config','vs_src_dir','sys.argv','def load','import ']):
        print('%4d: %s'%(i+1,l.rstrip()[:140]))