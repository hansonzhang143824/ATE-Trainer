import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== all RELAY_OFF lines (code) ===')
for i,l in enumerate(code):
    if 'RELAY_OFF' in l: print('   ',l.strip()[:105])
print()
print('count of "FPVIe_10MA, FPVIe_RELAY_OFF":',u.count('FPVIe_10MA, FPVIe_RELAY_OFF'))
print('count of FPVI0 ... RELAY_OFF :',sum(1 for l in code if 'FPVI0.Set' in l and 'RELAY_OFF' in l))
print('count of FPVI1 ... RELAY_OFF :',sum(1 for l in code if 'FPVI1.Set' in l and 'RELAY_OFF' in l))
print()
print('=== ordering: within each function, is FPVI0 the LAST RELAY_OFF? ===')
cur=None; seq={}
for l in code:
    if 'DUT_API int' in l: cur=l.split('int ')[1].split('(')[0]; seq[cur]=[]
    if cur and 'RELAY_OFF' in l:
        inst=l.split('.Set')[0].strip(); seq[cur].append(inst)
for k,v in seq.items(): print('  %-22s order=%s  FPVI0 last=%s'%(k,v,v[-1].startswith('FPVI0')))
print()
print('payload',len(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()),'B',hashlib.sha256(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()).hexdigest())