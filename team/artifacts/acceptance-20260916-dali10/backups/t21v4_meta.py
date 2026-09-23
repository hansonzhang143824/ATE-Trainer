import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
M=json.loads(open(os.path.join(base,'project','DALI','meta','dali_tm_meta.json'),'rb').read().decode('utf-8-sig'))
for e in M['functions']:
    if e.get('functionName')=='TM601_LS_RDSON':
        print('=== TM601_LS_RDSON meta (verbatim) ===')
        for k in ('functionName','testType','dftItem','params','hardwareInit','capAuthority'):
            print('%s: %s'%(k,json.dumps(e.get(k),ensure_ascii=False)[:600]))
print()
# how does gen_testitems_meta map a param to mi_pins?
g=os.path.join(base,'scripts','gen_testitems_meta.py')
t=open(g,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== gen_testitems_meta.py: capAuthority / powered_pins / mi_pins construction ===')
for i,l in enumerate(t):
    if any(k in l for k in ['capAuthority','powered_pins','mi_pins','ramp_pins','testpad','checkPin','check']):
        print('%4d: %s'%(i+1,l.rstrip()[:140]))