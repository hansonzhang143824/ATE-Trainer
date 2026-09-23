import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
M=json.loads(open(os.path.join(base,'project','DALI','meta','dali_tm_meta.json'),'rb').read().decode('utf-8-sig'))
F=M['functions']
print('functions type:',type(F).__name__, (len(F) if hasattr(F,'__len__') else ''))
for key in ('TM601_LS_RDSON','TM600_HS_RDSON'):
    e = F.get(key) if isinstance(F,dict) else None
    if e is None and isinstance(F,list):
        e=next((x for x in F if x.get('name')==key),None)
    print('===',key,'===')
    if e is None: print('  not found; sample keys:',list(F)[:5] if isinstance(F,dict) else 'n/a'); continue
    ca=e.get('capAuthority') or {}
    print('  verdict:',e.get('verdict'),'| capAuthority keys:',list(ca))
    for f in ('powered_pins','mi_pins','ramp_pins','testpad_pins'):
        print('   %-14s %s'%(f,ca.get(f)))
    print('  full entry head:',json.dumps(e,ensure_ascii=False)[:400])