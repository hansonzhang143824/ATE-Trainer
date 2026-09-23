import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
g=os.path.join(base,'scripts','check_cbit_defines.py')
if not os.path.exists(g):
    import glob; c=glob.glob(os.path.join(base,'scripts','*cbit*')); print('candidates:',[os.path.basename(x) for x in c]); g=c[0] if c else None
if g:
    t=open(g,'rb').read().decode('utf-8-sig',errors='replace'); print('using',os.path.basename(g))
    for i,l in enumerate(t.split('\n')):
        if any(k in l for k in ['目标有脚本无','脚本有目标无','baseline','基准','exit','FAIL','count']):
            print('  %4d: %s'%(i+1,l.rstrip()[:140]))
print()
print('=== cbit log tail (the actual verdict lines) ===')
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-logs-t20','cbit.log')
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
print('\n'.join(t.split('\n')[-40:]))