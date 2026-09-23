import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
M=json.loads(open(os.path.join(base,'project','DALI','meta','dali_tm_meta.json'),'rb').read().decode('utf-8-sig'))
F=M['functions']
print('first entry keys:',list(F[0]))
print('first entry:',json.dumps(F[0],ensure_ascii=False)[:500])
print()
key=[k for k in F[0] if 'name' in k.lower() or 'fn' in k.lower()][:4]
print('name-ish keys:',key)
for e in F:
    for k in key:
        if e.get(k) in ('TM601_LS_RDSON','TM600_HS_RDSON'):
            print('===',e.get(k),'===')
            ca=e.get('capAuthority') or {}
            print(' capAuthority keys:',list(ca))
            for f in ('powered_pins','mi_pins','ramp_pins','testpad_pins'):
                print('   %-14s %s'%(f,ca.get(f)))