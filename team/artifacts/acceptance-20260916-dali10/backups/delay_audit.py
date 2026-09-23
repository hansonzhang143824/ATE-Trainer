import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    u=open(os.path.join(d,n),'rb').read().decode('utf-8-sig')
    print('####',n)
    for i,l in enumerate(u.split('\n')):
        if 'delay_ms(' in l and not l.strip().startswith('//'):
            print('   %4d: %s'%(i+1,l.strip()[:100]))